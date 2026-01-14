"""
Configuration management for the multi-agent framework.

Handles loading and managing configuration from files and environment.
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for agents."""
    default_model: str = "gpt-4"
    timeout: int = 300
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int = 2000


@dataclass
class CoordinatorConfig:
    """Configuration for coordinator."""
    max_concurrent_agents: int = 5
    collaboration_mode: str = "sequential"
    enable_feedback_loops: bool = True
    max_iterations: int = 3


@dataclass
class VerificationConfig:
    """Configuration for verification system."""
    enabled: bool = True
    min_quality_score: float = 0.8
    checks: list = field(default_factory=lambda: [
        "factual_accuracy",
        "consistency",
        "completeness",
        "grammar",
        "style",
    ])


@dataclass
class DocumentConfig:
    """Configuration for document management."""
    default_format: str = "markdown"
    auto_save: bool = True
    versioning: bool = True
    output_directory: str = "output"


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    file: Optional[str] = None
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class Config:
    """
    Main configuration class for the multi-agent framework.
    
    Loads configuration from YAML files, environment variables, and provides
    access to all framework configuration settings.
    """
    
    def __init__(
        self,
        config_dict: Optional[Dict[str, Any]] = None,
    ):
        # Initialize with defaults
        self.framework_name = "Multi-Agent Document Framework"
        self.framework_version = "1.0.0"
        
        self.agent = AgentConfig()
        self.coordinator = CoordinatorConfig()
        self.verification = VerificationConfig()
        self.document = DocumentConfig()
        self.logging = LoggingConfig()
        
        self.custom: Dict[str, Any] = {}
        
        # Load from dictionary if provided
        if config_dict:
            self._load_from_dict(config_dict)
        
        # Apply environment variable overrides
        self._load_from_env()
        
        logger.info("Configuration initialized")
    
    @classmethod
    def from_yaml(cls, file_path: str) -> 'Config':
        """
        Load configuration from a YAML file.
        
        Args:
            file_path: Path to YAML configuration file
            
        Returns:
            Config instance
        """
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Config file not found: {file_path}. Using defaults.")
            return cls()
        
        try:
            with open(path, 'r') as f:
                config_dict = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {file_path}")
            return cls(config_dict)
        except Exception as e:
            logger.error(f"Error loading config from {file_path}: {e}")
            return cls()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create configuration from dictionary."""
        return cls(config_dict)
    
    def _load_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Load configuration from dictionary."""
        # Framework settings
        if 'framework' in config_dict:
            framework = config_dict['framework']
            self.framework_name = framework.get('name', self.framework_name)
            self.framework_version = framework.get('version', self.framework_version)
        
        # Agent settings
        if 'agents' in config_dict:
            agents = config_dict['agents']
            self.agent.default_model = agents.get('default_model', self.agent.default_model)
            self.agent.timeout = agents.get('timeout', self.agent.timeout)
            self.agent.max_retries = agents.get('max_retries', self.agent.max_retries)
            self.agent.temperature = agents.get('temperature', self.agent.temperature)
            self.agent.max_tokens = agents.get('max_tokens', self.agent.max_tokens)
        
        # Coordinator settings
        if 'coordinator' in config_dict:
            coord = config_dict['coordinator']
            self.coordinator.max_concurrent_agents = coord.get(
                'max_concurrent_agents', self.coordinator.max_concurrent_agents
            )
            self.coordinator.collaboration_mode = coord.get(
                'collaboration_mode', self.coordinator.collaboration_mode
            )
            self.coordinator.enable_feedback_loops = coord.get(
                'enable_feedback_loops', self.coordinator.enable_feedback_loops
            )
            self.coordinator.max_iterations = coord.get(
                'max_iterations', self.coordinator.max_iterations
            )
        
        # Verification settings
        if 'verification' in config_dict:
            verif = config_dict['verification']
            self.verification.enabled = verif.get('enabled', self.verification.enabled)
            self.verification.min_quality_score = verif.get(
                'min_quality_score', self.verification.min_quality_score
            )
            self.verification.checks = verif.get('checks', self.verification.checks)
        
        # Document settings
        if 'document' in config_dict:
            doc = config_dict['document']
            self.document.default_format = doc.get('default_format', self.document.default_format)
            self.document.auto_save = doc.get('auto_save', self.document.auto_save)
            self.document.versioning = doc.get('versioning', self.document.versioning)
            self.document.output_directory = doc.get(
                'output_directory', self.document.output_directory
            )
        
        # Logging settings
        if 'logging' in config_dict:
            log = config_dict['logging']
            self.logging.level = log.get('level', self.logging.level)
            self.logging.file = log.get('file', self.logging.file)
            self.logging.format = log.get('format', self.logging.format)
        
        # Store any custom settings
        self.custom = {k: v for k, v in config_dict.items() if k not in [
            'framework', 'agents', 'coordinator', 'verification', 'document', 'logging'
        ]}
    
    def _load_from_env(self) -> None:
        """Load configuration overrides from environment variables."""
        # Agent settings
        if os.getenv('MADF_AGENT_MODEL'):
            self.agent.default_model = os.getenv('MADF_AGENT_MODEL')
        if os.getenv('MADF_AGENT_TIMEOUT'):
            self.agent.timeout = int(os.getenv('MADF_AGENT_TIMEOUT'))
        
        # Coordinator settings
        if os.getenv('MADF_MAX_ITERATIONS'):
            self.coordinator.max_iterations = int(os.getenv('MADF_MAX_ITERATIONS'))
        if os.getenv('MADF_COLLABORATION_MODE'):
            self.coordinator.collaboration_mode = os.getenv('MADF_COLLABORATION_MODE')
        
        # Verification settings
        if os.getenv('MADF_VERIFICATION_ENABLED'):
            self.verification.enabled = os.getenv('MADF_VERIFICATION_ENABLED').lower() == 'true'
        
        # Logging settings
        if os.getenv('MADF_LOG_LEVEL'):
            self.logging.level = os.getenv('MADF_LOG_LEVEL')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'framework': {
                'name': self.framework_name,
                'version': self.framework_version,
            },
            'agents': {
                'default_model': self.agent.default_model,
                'timeout': self.agent.timeout,
                'max_retries': self.agent.max_retries,
                'temperature': self.agent.temperature,
                'max_tokens': self.agent.max_tokens,
            },
            'coordinator': {
                'max_concurrent_agents': self.coordinator.max_concurrent_agents,
                'collaboration_mode': self.coordinator.collaboration_mode,
                'enable_feedback_loops': self.coordinator.enable_feedback_loops,
                'max_iterations': self.coordinator.max_iterations,
            },
            'verification': {
                'enabled': self.verification.enabled,
                'min_quality_score': self.verification.min_quality_score,
                'checks': self.verification.checks,
            },
            'document': {
                'default_format': self.document.default_format,
                'auto_save': self.document.auto_save,
                'versioning': self.document.versioning,
                'output_directory': self.document.output_directory,
            },
            'logging': {
                'level': self.logging.level,
                'file': self.logging.file,
                'format': self.logging.format,
            },
            **self.custom,
        }
    
    def to_yaml(self, file_path: str) -> None:
        """Save configuration to YAML file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)
        
        logger.info(f"Configuration saved to {file_path}")
    
    def setup_logging(self) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.logging.level.upper()),
            format=self.logging.format,
            filename=self.logging.file,
        )
    
    def __repr__(self) -> str:
        return f"Config(framework={self.framework_name} v{self.framework_version})"