"""Event Publisher Interface."""
from abc import ABC, abstractmethod

from video_processor_shared.domain.events import DomainEvent


class IEventPublisher(ABC):
    """Interface for Event Publisher (SNS)."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        pass
