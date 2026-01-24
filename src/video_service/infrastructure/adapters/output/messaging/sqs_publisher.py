"""SQS Job Publisher for sending processing jobs to queue."""
from typing import Optional
import json
import os
import aioboto3


class SQSJobPublisher:
    """Publishes video processing jobs to SQS queue."""
    
    def __init__(
        self,
        queue_url: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        region: str = "us-east-1",
    ):
        self._queue_url = queue_url or os.getenv("SQS_JOB_QUEUE_URL")
        self._endpoint_url = endpoint_url or os.getenv("AWS_ENDPOINT_URL")
        self._region = region
        self._session = aioboto3.Session()
    
    async def send_job(
        self,
        job_id: str,
        video_id: str,
        user_id: str,
        s3_key: str,
        user_email: str,
    ) -> str:
        """
        Send a video processing job to the queue.
        
        Args:
            job_id: Unique job identifier
            video_id: Video identifier
            user_id: User who uploaded the video
            s3_key: S3 key where video is stored
            user_email: Email to notify when processing completes
        
        Returns:
            SQS Message ID
        """
        message_body = {
            "job_id": job_id,
            "video_id": video_id,
            "user_id": user_id,
            "s3_key": s3_key,
            "user_email": user_email,
        }
        
        async with self._session.client(
            "sqs",
            endpoint_url=self._endpoint_url,
            region_name=self._region,
        ) as sqs:
            response = await sqs.send_message(
                QueueUrl=self._queue_url,
                MessageBody=json.dumps(message_body),
                MessageAttributes={
                    "job_type": {
                        "DataType": "String",
                        "StringValue": "video_processing",
                    }
                },
            )
            return response["MessageId"]
