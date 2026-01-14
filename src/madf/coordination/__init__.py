"""
Coordination subsystem for agent communication and state management.
"""

from madf.coordination.message_bus import MessageBus
from madf.coordination.state_manager import StateManager
from madf.coordination.protocol import CommunicationProtocol

__all__ = ['MessageBus', 'StateManager', 'CommunicationProtocol']
