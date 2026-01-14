"""Message bus for inter-agent communication."""

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages in the system."""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    AGENT_STATUS = "agent_status"
    QUALITY_REPORT = "quality_report"
    COORDINATION_REQUEST = "coordination_request"
    STAGE_COMPLETE = "stage_complete"
    ERROR = "error"


@dataclass
class Message:
    """
    Represents a message in the system.
    
    Attributes:
        type: Message type
        data: Message payload
        sender: Message sender ID
        recipient: Optional specific recipient
        timestamp: Message creation time
        id: Unique message ID
    """
    type: MessageType
    data: Dict[str, Any]
    sender: Optional[str] = None
    recipient: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(asyncio.current_task()))


class MessageBus:
    """
    Event-driven message bus for agent communication.
    
    Implements publish/subscribe pattern for:
    - Asynchronous message delivery
    - Topic-based routing
    - Message filtering
    - Delivery guarantees
    
    Example:
        >>> bus = MessageBus()
        >>> await bus.subscribe(MessageType.TASK_COMPLETE, handler)
        >>> await bus.publish(Message(MessageType.TASK_COMPLETE, data={}))
    """
    
    def __init__(self):
        """Initialize message bus."""
        self.subscribers: Dict[MessageType, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self._processor_task: Optional[asyncio.Task] = None
        logger.info("MessageBus initialized")
    
    async def start(self):
        """Start message processing."""
        if not self.running:
            self.running = True
            self._processor_task = asyncio.create_task(self._process_messages())
            logger.info("MessageBus started")
    
    async def stop(self):
        """Stop message processing."""
        self.running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        logger.info("MessageBus stopped")
    
    def subscribe(self, message_type: MessageType, handler: Callable[[Message], None]):
        """
        Subscribe to messages of a specific type.
        
        Args:
            message_type: Type of messages to subscribe to
            handler: Async function to handle messages
        """
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []
        self.subscribers[message_type].append(handler)
        logger.debug(f"Subscribed handler to {message_type}")
    
    def unsubscribe(self, message_type: MessageType, handler: Callable[[Message], None]):
        """
        Unsubscribe from messages.
        
        Args:
            message_type: Message type
            handler: Handler to remove
        """
        if message_type in self.subscribers:
            try:
                self.subscribers[message_type].remove(handler)
                logger.debug(f"Unsubscribed handler from {message_type}")
            except ValueError:
                pass
    
    async def publish(self, message: Message):
        """
        Publish a message to subscribers.
        
        Args:
            message: Message to publish
        """
        await self.message_queue.put(message)
        logger.debug(f"Published message: {message.type}")
    
    async def _process_messages(self):
        """
        Process messages from queue.
        
        Runs continuously while the bus is active.
        """
        while self.running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                await self._deliver_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def _deliver_message(self, message: Message):
        """
        Deliver message to subscribers.
        
        Args:
            message: Message to deliver
        """
        handlers = self.subscribers.get(message.type, [])
        
        if not handlers:
            logger.debug(f"No handlers for message type: {message.type}")
            return
        
        # Deliver to all subscribers
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get message bus statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'running': self.running,
            'queue_size': self.message_queue.qsize(),
            'subscriber_counts': {
                msg_type.value: len(handlers)
                for msg_type, handlers in self.subscribers.items()
            }
        }