"""SNS Event Publisher."""
from typing import Optional
import json
import aioboto3

from video_service.application.ports.output.event_publisher import IEventPublisher
from video_processor_shared.domain.events import DomainEvent


class SNSEventPublisher(IEventPublisher):
    def __init__(self, topic_arn: str, endpoint_url: Optional[str] = None, region: str = "us-east-1"):
        self._topic_arn = topic_arn
        self._endpoint_url = endpoint_url
        self._region = region
        self._session = aioboto3.Session()

    async def publish(self, event: DomainEvent) -> None:
        if not self._topic_arn:
            return

        async with self._session.client(
            'sns',
            endpoint_url=self._endpoint_url,
            region_name=self._region,
        ) as sns:
            await sns.publish(
                TopicArn=self._topic_arn,
                Message=json.dumps(event.to_dict()),
                MessageAttributes={
                    'event_type': {
                        'DataType': 'String',
                        'StringValue': event.event_type,
                    }
                },
            )
