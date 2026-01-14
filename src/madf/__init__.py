"""Multi-Agent Document Framework (MADF).

A production-ready framework for intelligent multi-agent document creation.
"""

__version__ = "0.1.0"

from .orchestrator import DocumentOrchestrator
from .models.request import DocumentRequest
from .models.document import Document, DocumentSection, DocumentStatus
from .utils.config import OrchestratorConfig, AgentConfig, ModelConfig

__all__ = [
    "DocumentOrchestrator",
    "DocumentRequest",
    "Document",
    "DocumentSection",
    "DocumentStatus",
    "OrchestratorConfig",
    "AgentConfig",
    "ModelConfig",
]