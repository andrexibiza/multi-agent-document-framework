"""Resource management for agent orchestration."""

import asyncio
from typing import Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ResourcePool:
    """
    Pool of available resources.
    
    Attributes:
        max_size: Maximum pool size
        available: Available resource count
        in_use: Set of resources currently in use
        waiting: Queue of tasks waiting for resources
    """
    max_size: int
    available: int = 0
    in_use: Set[str] = field(default_factory=set)
    waiting: asyncio.Queue = field(default_factory=asyncio.Queue)
    
    def __post_init__(self):
        self.available = self.max_size


class ResourceManager:
    """
    Manages computational resources and agent capacity.
    
    Responsibilities:
    - Agent pool management
    - Resource allocation and deallocation
    - Load balancing
    - Quota tracking
    - Performance optimization
    
    Example:
        >>> manager = ResourceManager(max_agents=10)
        >>> async with manager.acquire('agent_1'):
        ...     # Use resource
        ...     pass
    """
    
    def __init__(self, max_agents: int = 10):
        """
        Initialize resource manager.
        
        Args:
            max_agents: Maximum concurrent agents
        """
        self.max_agents = max_agents
        self.pool = ResourcePool(max_size=max_agents)
        self.metrics = {
            'total_allocations': 0,
            'total_deallocations': 0,
            'peak_usage': 0,
            'wait_times': []
        }
        logger.info(f"ResourceManager initialized with {max_agents} agents")
    
    async def acquire(self, resource_id: str, timeout: Optional[float] = None) -> 'ResourceContext':
        """
        Acquire a resource.
        
        Args:
            resource_id: Identifier for the resource
            timeout: Optional timeout in seconds
            
        Returns:
            Resource context manager
            
        Raises:
            asyncio.TimeoutError: If timeout is exceeded
        """
        start_time = datetime.now()
        
        # Wait for resource availability
        if self.pool.available <= 0:
            logger.debug(f"Resource {resource_id} waiting for availability")
            try:
                await asyncio.wait_for(
                    self._wait_for_resource(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"Resource {resource_id} acquisition timed out")
                raise
        
        # Acquire resource
        self.pool.available -= 1
        self.pool.in_use.add(resource_id)
        self.metrics['total_allocations'] += 1
        
        # Update peak usage
        current_usage = len(self.pool.in_use)
        if current_usage > self.metrics['peak_usage']:
            self.metrics['peak_usage'] = current_usage
        
        # Track wait time
        wait_time = (datetime.now() - start_time).total_seconds()
        self.metrics['wait_times'].append(wait_time)
        
        logger.debug(f"Resource {resource_id} acquired (available: {self.pool.available})")
        
        return ResourceContext(self, resource_id)
    
    async def _wait_for_resource(self):
        """Wait for a resource to become available."""
        while self.pool.available <= 0:
            await asyncio.sleep(0.1)
    
    def release(self, resource_id: str):
        """
        Release a resource.
        
        Args:
            resource_id: Resource to release
        """
        if resource_id in self.pool.in_use:
            self.pool.in_use.remove(resource_id)
            self.pool.available += 1
            self.metrics['total_deallocations'] += 1
            logger.debug(f"Resource {resource_id} released (available: {self.pool.available})")
    
    def get_stats(self) -> Dict:
        """
        Get resource manager statistics.
        
        Returns:
            Statistics dictionary
        """
        avg_wait_time = (
            sum(self.metrics['wait_times']) / len(self.metrics['wait_times'])
            if self.metrics['wait_times'] else 0
        )
        
        return {
            'max_agents': self.max_agents,
            'available': self.pool.available,
            'in_use': len(self.pool.in_use),
            'utilization': len(self.pool.in_use) / self.max_agents,
            'total_allocations': self.metrics['total_allocations'],
            'total_deallocations': self.metrics['total_deallocations'],
            'peak_usage': self.metrics['peak_usage'],
            'avg_wait_time': avg_wait_time
        }
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            'total_allocations': 0,
            'total_deallocations': 0,
            'peak_usage': 0,
            'wait_times': []
        }


class ResourceContext:
    """
    Context manager for resource acquisition.
    
    Ensures resources are properly released.
    """
    
    def __init__(self, manager: ResourceManager, resource_id: str):
        """Initialize resource context."""
        self.manager = manager
        self.resource_id = resource_id
    
    async def __aenter__(self):
        """Enter context."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context and release resource."""
        self.manager.release(self.resource_id)
        return False