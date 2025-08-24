import json
import asyncio
from typing import Any, Dict, Optional

import boto3
from botocore.config import Config as BotoConfig

from app.config import get_settings
from app.services.dubbing_service import DubbingService
from app.services.job_service import JobService


settings = get_settings()


class QueueConsumer:
    def __init__(self) -> None:
        self.client = boto3.client(
            "sqs",
            region_name=settings.AWS_REGION,
            config=BotoConfig(retries={"max_attempts": 10, "mode": "standard"}),
        )
        self.queue_url = settings.SQS_QUEUE_URL

    async def process_message(self, message: Dict[str, Any]) -> None:
        body = json.loads(message["Body"]) if isinstance(message.get("Body"), str) else message.get("Body", {})
        message_type = message.get("MessageAttributes", {}).get("messageType", {}).get("StringValue")
        job_id = message.get("MessageAttributes", {}).get("jobId", {}).get("StringValue") or body.get("jobId")

        if message_type == "DUBBING_JOB" and job_id:
            # idempotency guard
            from app.core.database import get_async_session
            async with get_async_session() as db:
                job = await JobService.get_job(db, job_id)
                if not job:
                    return
                if job.status in ["completed", "failed", "cancelled"]:
                    return

            await DubbingService.execute_dubbing_pipeline(job_id)

    async def run_once(self) -> Optional[Dict[str, Any]]:
        if not self.queue_url:
            raise RuntimeError("SQS_QUEUE_URL is not configured")

        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=settings.SQS_WAIT_TIME_SECONDS,
            MessageAttributeNames=["All"],
            VisibilityTimeout=settings.SQS_VISIBILITY_TIMEOUT,
        )
        messages = response.get("Messages", [])
        if not messages:
            return None

        message = messages[0]
        receipt_handle = message["ReceiptHandle"]

        try:
            await self.process_message(message)
            self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
        except Exception:
            # let it become visible again for retry
            pass
        return message



