"""
Message bus for inter-agent communication.
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
from dataclasses import dataclass
import heapq

from madf.models import Message, MessageType

logger = logging.getLogger(__name__)


@dataclass
class QueuedMessage:
    """Message with priority for queue"""
    priority: int
    message: Message
    
    def __lt__(self, other):
        return self.priority < other.priority


class MessageBus:
    """
    Asynchronous message bus for agent communication.
    
    Features:
    - Pub/sub messaging
    - Priority queuing
    - Message routing
    - Delivery guarantees
    - Dead letter queue
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_queues: Dict[str, asyncio.PriorityQueue] = {}
        self.agents: Dict[str, Any] = {}
        self.running = False
        self.tasks: List[asyncio.Task] = []
        self.dead_letter_queue: List[Message] = []
        self.message_history: List[Message] = []
        self.max_history = 1000
        
        logger.info("MessageBus initialized")
    
    def register_agent(self, agent_name: str, agent: Any):
        """
        Register an agent with the message bus.
        
        Args:
            agent_name: Unique identifier for the agent
            agent: Agent instance
        """
        self.agents[agent_name] = agent
        self.message_queues[agent_name] = asyncio.PriorityQueue()
        
        logger.debug(f"Registered agent: {agent_name}")
    
    def subscribe(self, topic: str, callback: Callable):
        """
        Subscribe to messages on a topic.
        
        Args:
            topic: Topic to subscribe to
            callback: Async function to call when message received
        """
        self.subscribers[topic].append(callback)
        logger.debug(f"New subscription to topic: {topic}")
    
    async def publish(self, message: Message):
        """
        Publish a message to the bus.
        
        Args:
            message: Message to publish
        """
        # Store in history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        # Route to recipient if specified
        if message.recipient:
            await self._route_to_agent(message)
        
        # Notify subscribers
        topic = message.type.value
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"Subscriber callback error: {e}")
        
        logger.debug(f"Published message: {message.id} from {message.sender} to {message.recipient}")
    
    async def _route_to_agent(self, message: Message):
        """
        Route message to specific agent's queue.
        """
        if message.recipient not in self.message_queues:
            logger.warning(f"Unknown recipient: {message.recipient}")
            self.dead_letter_queue.append(message)
            return
        
        queue = self.message_queues[message.recipient]
        queued_msg = QueuedMessage(priority=-message.priority, message=message)
        await queue.put(queued_msg)
    
    async def send(self, 
                   sender: str,
                   recipient: str,
                   message_type: MessageType,
                   payload: Dict[str, Any],
                   priority: int = 0) -> Message:
        """
        Send a message to a specific recipient.
        
        Args:
            sender: Sender agent name
            recipient: Recipient agent name
            message_type: Type of message
            payload: Message payload
            priority: Message priority (higher = more urgent)
        
        Returns:
            The created message
        """
        message = Message(
            type=message_type,
            sender=sender,
            recipient=recipient,
            payload=payload,
            priority=priority
        )
        
        await self.publish(message)
        return message
    
    async def receive(self, agent_name: str, timeout: Optional[float] = None) -> Optional[Message]:
        """
        Receive next message for an agent.
        
        Args:
            agent_name: Name of agent receiving message
            timeout: Optional timeout in seconds
        
        Returns:
            Next message or None if timeout
        """
        if agent_name not in self.message_queues:
            logger.warning(f"Agent not registered: {agent_name}")
            return None
        
        queue = self.message_queues[agent_name]
        
        try:
            if timeout:
                queued_msg = await asyncio.wait_for(queue.get(), timeout=timeout)
            else:
                queued_msg = await queue.get()
            
            return queued_msg.message
        
        except asyncio.TimeoutError:
            return None
    
    def get_queue_size(self, agent_name: str) -> int:
        """
        Get number of pending messages for an agent.
        """
        if agent_name not in self.message_queues:
            return 0
        return self.message_queues[agent_name].qsize()
    
    def get_message_history(self, limit: int = 100) -> List[Message]:
        """
        Get recent message history.
        """
        return self.message_history[-limit:]
    
    def get_dead_letters(self) -> List[Message]:
        """
        Get undeliverable messages.
        """
        return self.dead_letter_queue.copy()
    
    async def close(self):
        """
        Close the message bus and cleanup resources.
        """
        logger.info("Closing MessageBus")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Clear queues
        for queue in self.message_queues.values():
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
        
        logger.info("MessageBus closed")
