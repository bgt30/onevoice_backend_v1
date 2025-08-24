from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class DubbingJobMessage(BaseModel):
    messageType: str = Field(default="DUBBING_JOB")
    jobId: str
    userId: str
    videoId: str
    requestedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())



