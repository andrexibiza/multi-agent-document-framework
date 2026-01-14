"""
Multi-Agent Document Framework (MADF)

A production-ready framework for building multi-agent document creation systems.
"""

__version__ = "0.1.0"
__author__ = "Andrex Ibiza"

from madf.orchestrator import DocumentOrchestrator, OrchestratorConfig
from madf.agents import (
    BaseAgent,
    ResearchAgent,
    WritingAgent,
    EditingAgent,
    VerificationAgent
)
from madf.models import Document, Context, Task, Result
from madf.workflows import WorkflowBuilder

__all__ = [
    'DocumentOrchestrator',
    'OrchestratorConfig',
    'BaseAgent',
    'ResearchAgent',
    'WritingAgent',
    'EditingAgent',
    'VerificationAgent',
    'Document',
    'Context',
    'Task',
    'Result',
    'WorkflowBuilder'
]