import json
from typing import Any, Dict, Optional

import boto3
from botocore.config import Config as BotoConfig

from app.config import get_settings


settings = get_settings()


class SQSClient:
    def __init__(self) -> None:
        session_kwargs: Dict[str, Any] = {"region_name": settings.AWS_REGION}
        client_kwargs: Dict[str, Any] = {
            "config": BotoConfig(retries={"max_attempts": 10, "mode": "standard"})
        }
        self.client = boto3.client("sqs", **session_kwargs, **client_kwargs)
        self.queue_url: Optional[str] = settings.SQS_QUEUE_URL

    def send_message(self, payload: Dict[str, Any], message_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        if not self.queue_url:
            raise RuntimeError("SQS_QUEUE_URL is not configured")

        message_attributes = {
            "messageType": {
                "StringValue": message_type,
                "DataType": "String"
            }
        }
        if attributes:
            for key, value in attributes.items():
                message_attributes[key] = {"StringValue": str(value), "DataType": "String"}

        self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(payload),
            MessageAttributes=message_attributes,
        )


sqs_client = SQSClient()



