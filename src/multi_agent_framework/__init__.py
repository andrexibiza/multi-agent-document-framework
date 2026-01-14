"""
Multi-Agent Document Framework

A production-ready framework for building multi-agent document creation systems.
"""

__version__ = "1.0.0"
__author__ = "Andrex Ibiza"
__license__ = "MIT"

from .agent import Agent, AgentRole, AgentCapability
from .coordinator import Coordinator, WorkflowMode
from .document import Document, DocumentManager, Section
from .verification import (
    VerificationSystem,
    VerificationResult,
    QualityCheck,
    FactCheck,
    ConsistencyCheck,
)
from .config import Config

__all__ = [
    # Core classes
    "Agent",
    "AgentRole",
    "AgentCapability",
    "Coordinator",
    "WorkflowMode",
    "Document",
    "DocumentManager",
    "Section",
    # Verification
    "VerificationSystem",
    "VerificationResult",
    "QualityCheck",
    "FactCheck",
    "ConsistencyCheck",
    # Configuration
    "Config",
]