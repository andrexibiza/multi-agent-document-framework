"""Configuration management."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
import yaml
from pathlib import Path


@dataclass
class ModelConfig:
    """
    LLM model configuration.
    
    Attributes:
        provider: LLM provider (openai, anthropic, etc.)
        model: Model name
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        api_key: API key (defaults to environment variable)
    """
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4000
    api_key: Optional[str] = None
    
    def __post_init__(self):
        """Load API key from environment if not provided."""
        if not self.api_key:
            env_var = f"{self.provider.upper()}_API_KEY"
            self.api_key = os.getenv(env_var)
            if not self.api_key:
                raise ValueError(f"API key not found. Set {env_var} environment variable.")


@dataclass
class AgentConfig:
    """
    Individual agent configuration.
    
    Attributes:
        name: Agent name
        model_config: LLM model configuration
        timeout: Task timeout in seconds
        max_retries: Maximum retry attempts
        cache_enabled: Whether to enable caching
    """
    name: str
    model_config: ModelConfig
    timeout: int = 120
    max_retries: int = 3
    cache_enabled: bool = True


@dataclass
class OrchestratorConfig:
    """
    Orchestrator configuration.
    
    Attributes:
        max_agents: Maximum concurrent agents
        timeout: Overall timeout in seconds
        quality_threshold: Minimum quality score (0-1)
        enable_parallel: Enable parallel processing
        max_concurrent_tasks: Maximum concurrent tasks
        retry_attempts: Retry attempts for failed operations
        research_config: Research agent configuration
        writing_config: Writing agent configuration
        editing_config: Editing agent configuration
        verification_config: Verification agent configuration
    """
    max_agents: int = 10
    timeout: int = 300
    quality_threshold: float = 0.85
    enable_parallel: bool = True
    max_concurrent_tasks: int = 5
    retry_attempts: int = 3
    
    # Agent-specific configs
    research_config: Optional[AgentConfig] = None
    writing_config: Optional[AgentConfig] = None
    editing_config: Optional[AgentConfig] = None
    verification_config: Optional[AgentConfig] = None
    
    @classmethod
    def from_yaml(cls, path: str) -> 'OrchestratorConfig':
        """
        Load configuration from YAML file.
        
        Args:
            path: Path to YAML configuration file
            
        Returns:
            OrchestratorConfig instance
        """
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'OrchestratorConfig':
        """
        Create config from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            OrchestratorConfig instance
        """
        # Extract orchestrator params
        orch_params = config_dict.get('orchestrator', {})
        
        # Create agent configs
        agents_config = config_dict.get('agents', {})
        
        research_config = None
        if 'research' in agents_config:
            research_config = cls._create_agent_config('research', agents_config['research'])
        
        writing_config = None
        if 'writing' in agents_config:
            writing_config = cls._create_agent_config('writing', agents_config['writing'])
        
        editing_config = None
        if 'editing' in agents_config:
            editing_config = cls._create_agent_config('editing', agents_config['editing'])
        
        verification_config = None
        if 'verification' in agents_config:
            verification_config = cls._create_agent_config('verification', agents_config['verification'])
        
        return cls(
            max_agents=orch_params.get('max_agents', 10),
            timeout=orch_params.get('timeout', 300),
            quality_threshold=orch_params.get('quality_threshold', 0.85),
            enable_parallel=orch_params.get('enable_parallel', True),
            max_concurrent_tasks=orch_params.get('max_concurrent_tasks', 5),
            retry_attempts=orch_params.get('retry_attempts', 3),
            research_config=research_config,
            writing_config=writing_config,
            editing_config=editing_config,
            verification_config=verification_config
        )
    
    @staticmethod
    def _create_agent_config(name: str, agent_dict: Dict) -> AgentConfig:
        """Create agent config from dictionary."""
        model_config = ModelConfig(
            provider=agent_dict.get('provider', 'openai'),
            model=agent_dict.get('model', 'gpt-4'),
            temperature=agent_dict.get('temperature', 0.7),
            max_tokens=agent_dict.get('max_tokens', 4000)
        )
        
        return AgentConfig(
            name=name,
            model_config=model_config,
            timeout=agent_dict.get('timeout', 120),
            max_retries=agent_dict.get('max_retries', 3),
            cache_enabled=agent_dict.get('cache_enabled', True)
        )
    
    def save_to_yaml(self, path: str):
        """
        Save configuration to YAML file.
        
        Args:
            path: Output path
        """
        config_dict = self.to_dict()
        with open(path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            'orchestrator': {
                'max_agents': self.max_agents,
                'timeout': self.timeout,
                'quality_threshold': self.quality_threshold,
                'enable_parallel': self.enable_parallel,
                'max_concurrent_tasks': self.max_concurrent_tasks,
                'retry_attempts': self.retry_attempts
            },
            'agents': {
                'research': self._agent_config_to_dict(self.research_config),
                'writing': self._agent_config_to_dict(self.writing_config),
                'editing': self._agent_config_to_dict(self.editing_config),
                'verification': self._agent_config_to_dict(self.verification_config)
            }
        }
    
    @staticmethod
    def _agent_config_to_dict(agent_config: Optional[AgentConfig]) -> Dict:
        """Convert agent config to dictionary."""
        if not agent_config:
            return {}
        
        return {
            'provider': agent_config.model_config.provider,
            'model': agent_config.model_config.model,
            'temperature': agent_config.model_config.temperature,
            'max_tokens': agent_config.model_config.max_tokens,
            'timeout': agent_config.timeout,
            'max_retries': agent_config.max_retries,
            'cache_enabled': agent_config.cache_enabled
        }