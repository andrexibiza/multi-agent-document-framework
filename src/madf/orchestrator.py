"""Document Orchestrator - Central coordination for multi-agent document creation."""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from .models.document import Document, DocumentSection, DocumentStatus
from .models.request import DocumentRequest
from .models.task import Task, TaskResult
from .agents.research import ResearchAgent
from .agents.writing import WritingAgent
from .agents.editing import EditingAgent
from .agents.verification import VerificationAgent
from .coordination.workflow import WorkflowManager, Stage
from .coordination.message_bus import MessageBus, Message, MessageType
from .coordination.resource_manager import ResourceManager
from .utils.config import OrchestratorConfig, AgentConfig, ModelConfig
from .storage.state_store import StateStore

logger = logging.getLogger(__name__)


class DocumentOrchestrator:
    """
    Central orchestrator for multi-agent document creation.
    
    Coordinates research, writing, editing, and verification agents
    to produce high-quality documents through a structured workflow.
    
    Architecture:
    - Workflow management and execution
    - Agent coordination and communication
    - Resource allocation and optimization
    - State management and persistence
    - Error handling and recovery
    
    Example:
        >>> config = OrchestratorConfig(
        ...     max_agents=10,
        ...     quality_threshold=0.85
        ... )
        >>> orchestrator = DocumentOrchestrator(config)
        >>> request = DocumentRequest(
        ...     topic="The Future of AI",
        ...     document_type="article",
        ...     target_length=2000
        ... )
        >>> document = await orchestrator.create_document(request)
    """
    
    def __init__(self, config: OrchestratorConfig):
        """
        Initialize the document orchestrator.
        
        Args:
            config: Orchestrator configuration
        """
        self.config = config
        self.workflow_manager = WorkflowManager()
        self.resource_manager = ResourceManager(config.max_agents)
        self.message_bus = MessageBus()
        self.state_store = StateStore()
        
        # Initialize agents
        self._init_agents()
        
        logger.info("DocumentOrchestrator initialized")
    
    def _init_agents(self):
        """Initialize all specialized agents."""
        # Create default configs if not provided
        default_model_config = ModelConfig(model="gpt-4", temperature=0.7)
        
        research_config = self.config.research_config or AgentConfig(
            name="research",
            model_config=ModelConfig(model="gpt-4", temperature=0.3)
        )
        writing_config = self.config.writing_config or AgentConfig(
            name="writing",
            model_config=ModelConfig(model="gpt-4", temperature=0.7)
        )
        editing_config = self.config.editing_config or AgentConfig(
            name="editing",
            model_config=ModelConfig(model="gpt-4", temperature=0.5)
        )
        verification_config = self.config.verification_config or AgentConfig(
            name="verification",
            model_config=ModelConfig(model="gpt-4", temperature=0.2)
        )
        
        # Create agent instances
        self.agents = {
            'research': ResearchAgent(research_config),
            'writing': WritingAgent(writing_config),
            'editing': EditingAgent(editing_config),
            'verification': VerificationAgent(verification_config)
        }
        
        logger.info(f"Initialized {len(self.agents)} agents")
    
    async def create_document(self, request: DocumentRequest) -> Document:
        """
        Create a document from a request.
        
        This is the main entry point for document creation. It:
        1. Validates the request
        2. Creates a workflow
        3. Executes the workflow stages
        4. Verifies quality
        5. Returns the final document
        
        Args:
            request: Document creation request
            
        Returns:
            Completed document
            
        Raises:
            ValueError: If request is invalid
            RuntimeError: If document creation fails
        """
        # Validate request
        request.validate()
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        logger.info(f"Starting document creation: {doc_id}")
        logger.info(f"Topic: {request.topic}")
        logger.info(f"Type: {request.document_type}")
        
        # Initialize document
        document = Document(
            id=doc_id,
            title=request.topic,
            sections=[],
            status=DocumentStatus.PENDING,
            metadata={'request': request.__dict__}
        )
        
        # Save initial state
        await self.state_store.save_document(document)
        
        try:
            # Create and execute workflow
            workflow = self.workflow_manager.create_workflow(request)
            
            # Execute workflow stages
            workflow_result = await self._execute_workflow(workflow, request, document)
            
            # Update document from workflow result
            document = await self._finalize_document(workflow_result, document)
            
            # Final verification
            if document.quality_score < self.config.quality_threshold:
                logger.warning(
                    f"Document quality {document.quality_score} below threshold "
                    f"{self.config.quality_threshold}. Consider refinement."
                )
            
            document.status = DocumentStatus.COMPLETE
            await self.state_store.save_document(document)
            
            logger.info(f"Document creation completed: {doc_id}")
            logger.info(f"Quality score: {document.quality_score}")
            logger.info(f"Word count: {document.word_count}")
            
            return document
            
        except Exception as e:
            logger.error(f"Document creation failed: {str(e)}")
            document.status = DocumentStatus.FAILED
            await self.state_store.save_document(document)
            raise RuntimeError(f"Failed to create document: {str(e)}")
    
    async def _execute_workflow(self, 
                               workflow: 'Workflow', 
                               request: DocumentRequest,
                               document: Document) -> Dict[str, Any]:
        """
        Execute workflow stages.
        
        Args:
            workflow: Workflow to execute
            request: Document request
            document: Document being created
            
        Returns:
            Workflow execution results
        """
        workflow_context = {
            'request': request,
            'document': document
        }
        
        for stage in workflow.stages:
            logger.info(f"Executing stage: {stage.name}")
            document.status = self._get_status_for_stage(stage.name)
            await self.state_store.save_document(document)
            
            stage_result = await self._execute_stage(stage, workflow_context)
            workflow_context[stage.name] = stage_result
            
            # Publish stage completion
            await self.message_bus.publish(Message(
                type=MessageType.STAGE_COMPLETE,
                data={
                    'stage': stage.name,
                    'document_id': document.id
                }
            ))
        
        return workflow_context
    
    async def _execute_stage(self, stage: Stage, context: Dict[str, Any]) -> Any:
        """
        Execute a single workflow stage.
        
        Args:
            stage: Stage to execute
            context: Workflow context
            
        Returns:
            Stage execution result
        """
        agent_type = stage.agent_type
        agent = self.agents.get(agent_type)
        
        if not agent:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Create task for agent
        task = self._create_task_for_stage(stage, context)
        
        # Execute task
        result = await agent.execute(task)
        
        if not result.success:
            raise RuntimeError(f"Stage {stage.name} failed: {result.error}")
        
        return result.data
    
    def _create_task_for_stage(self, stage: Stage, context: Dict[str, Any]) -> Task:
        """
        Create task for a workflow stage.
        
        Args:
            stage: Workflow stage
            context: Workflow context
            
        Returns:
            Task for agent execution
        """
        request = context['request']
        
        if stage.name == 'research':
            return Task(
                id=str(uuid.uuid4()),
                type='research',
                data={
                    'query': request.topic,
                    'depth': 'deep',
                    'requirements': request.requirements
                }
            )
        
        elif stage.name == 'writing':
            research_data = context.get('research', {})
            return Task(
                id=str(uuid.uuid4()),
                type='writing',
                data={
                    'type': 'full',
                    'research_brief': research_data.get('research_brief'),
                    'requirements': {
                        'document_type': request.document_type,
                        'target_length': request.target_length,
                        'style': request.style,
                        'audience': request.audience
                    }
                }
            )
        
        elif stage.name == 'editing':
            writing_data = context.get('writing', {})
            sections = writing_data.get('sections', [])
            full_content = "\n\n".join([s['content'] for s in sections])
            
            return Task(
                id=str(uuid.uuid4()),
                type='editing',
                data={
                    'content': full_content,
                    'style_guide': {'style': request.style}
                }
            )
        
        elif stage.name == 'verification':
            editing_data = context.get('editing', {})
            research_data = context.get('research', {})
            
            return Task(
                id=str(uuid.uuid4()),
                type='verification',
                data={
                    'document': editing_data.get('edited_content'),
                    'requirements': {
                        'target_length': request.target_length,
                        'requirements': request.requirements
                    },
                    'research_brief': research_data.get('research_brief')
                }
            )
        
        else:
            raise ValueError(f"Unknown stage: {stage.name}")
    
    async def _finalize_document(self, 
                                workflow_result: Dict[str, Any],
                                document: Document) -> Document:
        """
        Finalize document from workflow results.
        
        Args:
            workflow_result: Results from workflow execution
            document: Document to finalize
            
        Returns:
            Finalized document
        """
        # Extract final content
        editing_data = workflow_result.get('editing', {})
        final_content = editing_data.get('edited_content', '')
        
        # Create document sections
        sections = self._split_into_sections(final_content)
        document.sections = sections
        
        # Extract quality score
        verification_data = workflow_result.get('verification', {})
        verification_report = verification_data.get('verification_report', {})
        document.quality_score = verification_report.get('overall_score', 0.0)
        
        # Update word count
        document.update_word_count()
        document.updated_at = datetime.now()
        
        return document
    
    def _split_into_sections(self, content: str) -> List[DocumentSection]:
        """
        Split content into sections.
        
        Args:
            content: Full document content
            
        Returns:
            List of document sections
        """
        # Simple section splitting based on headers
        # Can be made more sophisticated
        sections = []
        current_section = None
        order = 0
        
        for line in content.split('\n'):
            # Check if line is a header (starts with # or is all caps)
            if line.startswith('#') or (line.isupper() and len(line) > 3):
                if current_section:
                    sections.append(current_section)
                current_section = DocumentSection(
                    title=line.strip('#').strip(),
                    content='',
                    order=order
                )
                order += 1
            elif current_section:
                current_section.content += line + '\n'
        
        if current_section:
            sections.append(current_section)
        
        # If no sections found, create single section
        if not sections:
            sections = [DocumentSection(
                title="Content",
                content=content,
                order=0
            )]
        
        return sections
    
    def _get_status_for_stage(self, stage_name: str) -> DocumentStatus:
        """Map stage name to document status."""
        status_map = {
            'research': DocumentStatus.RESEARCHING,
            'writing': DocumentStatus.WRITING,
            'editing': DocumentStatus.EDITING,
            'verification': DocumentStatus.VERIFYING
        }
        return status_map.get(stage_name, DocumentStatus.PENDING)
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        return await self.state_store.get_document(document_id)
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for all agents.
        
        Returns:
            Dictionary of agent metrics
        """
        return {name: agent.get_metrics() for name, agent in self.agents.items()}