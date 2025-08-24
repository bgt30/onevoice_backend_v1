from typing import Dict

from app.queue.message_models import DubbingJobMessage
from app.queue.sqs_client import sqs_client


async def enqueue_dubbing_job(job_id: str, user_id: str, video_id: str) -> None:
    message = DubbingJobMessage(jobId=job_id, userId=user_id, videoId=video_id)
    sqs_client.send_message(payload=message.model_dump(), message_type=message.messageType, attributes={"jobId": job_id, "userId": user_id, "videoId": video_id})



