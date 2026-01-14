"""Workflow management for document creation."""

from dataclasses import dataclass, field
from typing import List, Optional, Set
from enum import Enum

from ..models.request import DocumentRequest


class StageType(Enum):
    """Types of workflow stages."""
    RESEARCH = "research"
    PLANNING = "planning"
    WRITING = "writing"
    EDITING = "editing"
    VERIFICATION = "verification"


@dataclass
class Stage:
    """
    Represents a workflow stage.
    
    Attributes:
        name: Stage name
        agent_type: Type of agent to execute this stage
        depends_on: List of stage names this stage depends on
        parallel: Whether this stage can run in parallel with others
        optional: Whether this stage is optional
    """
    name: str
    agent_type: str
    depends_on: List[str] = field(default_factory=list)
    parallel: bool = False
    optional: bool = False
    
    def can_execute(self, completed_stages: Set[str]) -> bool:
        """
        Check if this stage can execute.
        
        Args:
            completed_stages: Set of completed stage names
            
        Returns:
            True if all dependencies are met
        """
        return all(dep in completed_stages for dep in self.depends_on)


@dataclass
class Workflow:
    """
    Represents a document creation workflow.
    
    Attributes:
        name: Workflow name
        stages: List of workflow stages
        metadata: Additional workflow metadata
    """
    name: str
    stages: List[Stage]
    metadata: dict = field(default_factory=dict)
    
    def get_next_stages(self, completed_stages: Set[str]) -> List[Stage]:
        """
        Get stages that can be executed next.
        
        Args:
            completed_stages: Set of completed stage names
            
        Returns:
            List of stages ready for execution
        """
        return [
            stage for stage in self.stages
            if stage.name not in completed_stages
            and stage.can_execute(completed_stages)
        ]


class WorkflowManager:
    """
    Manages workflow creation and execution.
    
    Provides predefined workflows for different document types
    and supports custom workflow creation.
    """
    
    def __init__(self):
        """Initialize workflow manager."""
        self.workflows = {}
        self._register_default_workflows()
    
    def _register_default_workflows(self):
        """Register default workflows for common document types."""
        # Standard article workflow
        self.workflows['article'] = self._create_article_workflow()
        
        # Research paper workflow
        self.workflows['paper'] = self._create_paper_workflow()
        
        # Technical report workflow
        self.workflows['report'] = self._create_report_workflow()
    
    def _create_article_workflow(self) -> Workflow:
        """Create workflow for article creation."""
        return Workflow(
            name="article",
            stages=[
                Stage(
                    name="research",
                    agent_type="research",
                    parallel=False
                ),
                Stage(
                    name="writing",
                    agent_type="writing",
                    depends_on=["research"],
                    parallel=False
                ),
                Stage(
                    name="editing",
                    agent_type="editing",
                    depends_on=["writing"],
                    parallel=False
                ),
                Stage(
                    name="verification",
                    agent_type="verification",
                    depends_on=["editing"],
                    parallel=False
                )
            ]
        )
    
    def _create_paper_workflow(self) -> Workflow:
        """Create workflow for research paper creation."""
        return Workflow(
            name="paper",
            stages=[
                Stage(
                    name="research",
                    agent_type="research",
                    parallel=False
                ),
                Stage(
                    name="writing",
                    agent_type="writing",
                    depends_on=["research"],
                    parallel=False
                ),
                Stage(
                    name="editing",
                    agent_type="editing",
                    depends_on=["writing"],
                    parallel=False
                ),
                Stage(
                    name="verification",
                    agent_type="verification",
                    depends_on=["editing"],
                    parallel=False
                )
            ],
            metadata={'requires_citations': True, 'formal_style': True}
        )
    
    def _create_report_workflow(self) -> Workflow:
        """Create workflow for technical report creation."""
        return Workflow(
            name="report",
            stages=[
                Stage(
                    name="research",
                    agent_type="research",
                    parallel=False
                ),
                Stage(
                    name="writing",
                    agent_type="writing",
                    depends_on=["research"],
                    parallel=False
                ),
                Stage(
                    name="editing",
                    agent_type="editing",
                    depends_on=["writing"],
                    parallel=False
                ),
                Stage(
                    name="verification",
                    agent_type="verification",
                    depends_on=["editing"],
                    parallel=False
                )
            ],
            metadata={'include_executive_summary': True}
        )
    
    def create_workflow(self, request: DocumentRequest) -> Workflow:
        """
        Create workflow for document request.
        
        Args:
            request: Document creation request
            
        Returns:
            Workflow for document creation
        """
        # Get workflow based on document type
        workflow_template = self.workflows.get(
            request.document_type,
            self.workflows['article']  # Default to article
        )
        
        # Can customize workflow based on request requirements
        return workflow_template
    
    def register_workflow(self, name: str, workflow: Workflow):
        """
        Register a custom workflow.
        
        Args:
            name: Workflow name
            workflow: Workflow instance
        """
        self.workflows[name] = workflow


class WorkflowBuilder:
    """
    Builder for creating custom workflows.
    
    Example:
        >>> workflow = (WorkflowBuilder()
        ...     .add_stage("research", "research")
        ...     .add_stage("writing", "writing", depends_on=["research"])
        ...     .add_stage("editing", "editing", depends_on=["writing"])
        ...     .build())
    """
    
    def __init__(self, name: str = "custom"):
        """Initialize workflow builder."""
        self.name = name
        self.stages = []
        self.metadata = {}
    
    def add_stage(self,
                 name: str,
                 agent_type: str,
                 depends_on: Optional[List[str]] = None,
                 parallel: bool = False,
                 optional: bool = False) -> 'WorkflowBuilder':
        """
        Add a stage to the workflow.
        
        Args:
            name: Stage name
            agent_type: Agent type for execution
            depends_on: List of dependency stage names
            parallel: Whether stage can run in parallel
            optional: Whether stage is optional
            
        Returns:
            Self for chaining
        """
        stage = Stage(
            name=name,
            agent_type=agent_type,
            depends_on=depends_on or [],
            parallel=parallel,
            optional=optional
        )
        self.stages.append(stage)
        return self
    
    def set_metadata(self, key: str, value: any) -> 'WorkflowBuilder':
        """
        Set workflow metadata.
        
        Args:
            key: Metadata key
            value: Metadata value
            
        Returns:
            Self for chaining
        """
        self.metadata[key] = value
        return self
    
    def build(self) -> Workflow:
        """
        Build the workflow.
        
        Returns:
            Constructed workflow
        """
        return Workflow(
            name=self.name,
            stages=self.stages,
            metadata=self.metadata
        )