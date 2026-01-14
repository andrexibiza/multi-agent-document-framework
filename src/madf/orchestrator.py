"""
Document Orchestrator - Main coordination system for multi-agent document creation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from madf.agents.base import BaseAgent
from madf.models import Task, Result, Document, Context
from madf.coordination.message_bus import MessageBus
from madf.coordination.state_manager import StateManager
from madf.workflows.executor import WorkflowExecutor
from madf.verification.quality_checker import QualityChecker

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Workflow execution stages"""
    INITIALIZING = "initializing"
    RESEARCHING = "researching"
    WRITING = "writing"
    EDITING = "editing"
    VERIFYING = "verifying"
    ITERATING = "iterating"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class OrchestratorConfig:
    """Configuration for document orchestrator"""
    max_iterations: int = 3
    quality_threshold: float = 0.85
    enable_verification: bool = True
    enable_parallel_processing: bool = True
    timeout_seconds: int = 600
    enable_caching: bool = True
    log_level: str = "INFO"
    
    # Agent-specific timeouts
    research_timeout: int = 120
    writing_timeout: int = 180
    editing_timeout: int = 120
    verification_timeout: int = 60


@dataclass
class DocumentRequest:
    """Request for document creation"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    requirements: Dict[str, Any] = field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DocumentResult:
    """Result of document creation"""
    document_id: str
    success: bool
    content: str
    quality_score: float
    iterations: int
    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    errors: Optional[List[str]] = None
    created_at: datetime = field(default_factory=datetime.now)


class DocumentOrchestrator:
    """
    Main orchestrator for coordinating multiple agents to create documents.
    
    Responsibilities:
    - Manage agent lifecycle
    - Coordinate workflow execution
    - Handle quality control
    - Manage iterations and feedback
    - Monitor performance
    - Handle errors and recovery
    """
    
    def __init__(self,
                 agents: Dict[str, BaseAgent],
                 config: Optional[OrchestratorConfig] = None):
        """
        Initialize orchestrator with agents and configuration.
        
        Args:
            agents: Dictionary mapping agent roles to agent instances
                   Expected keys: 'research', 'writing', 'editing', 'verification'
            config: Orchestrator configuration
        """
        self.agents = agents
        self.config = config or OrchestratorConfig()
        
        # Initialize subsystems
        self.message_bus = MessageBus()
        self.state_manager = StateManager()
        self.quality_checker = QualityChecker()
        self.workflow_executor = WorkflowExecutor(
            agents=agents,
            message_bus=self.message_bus,
            state_manager=self.state_manager
        )
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Register agents with message bus
        self._register_agents()
        
        logger.info("DocumentOrchestrator initialized with %d agents", len(agents))
    
    def _register_agents(self):
        """Register agents with message bus for communication"""
        for agent_name, agent in self.agents.items():
            self.message_bus.register_agent(agent_name, agent)
            logger.debug(f"Registered agent: {agent_name}")
    
    async def create_document(self,
                             topic: str,
                             requirements: Dict[str, Any]) -> DocumentResult:
        """
        Create a document using multi-agent collaboration.
        
        Args:
            topic: Main topic/subject of the document
            requirements: Dictionary containing:
                - length: Target word count (e.g., "2000-3000 words")
                - tone: Writing tone (e.g., "professional", "casual")
                - style: Writing style (e.g., "technical", "narrative")
                - target_audience: Intended audience
                - include_citations: Whether to include citations
                - other custom requirements
        
        Returns:
            DocumentResult containing the generated document and metadata
        """
        request = DocumentRequest(
            topic=topic,
            requirements=requirements
        )
        
        logger.info(f"Starting document creation: {request.request_id}")
        logger.debug(f"Topic: {topic}")
        logger.debug(f"Requirements: {requirements}")
        
        try:
            # Initialize document state
            document_id = await self._initialize_document(request)
            
            # Execute workflow with iterations
            final_result = await self._execute_workflow_with_iterations(
                document_id,
                request
            )
            
            # Finalize document
            document_result = await self._finalize_document(
                document_id,
                final_result
            )
            
            logger.info(
                f"Document creation completed: {document_id}, "
                f"Quality: {document_result.quality_score:.3f}, "
                f"Iterations: {document_result.iterations}"
            )
            
            return document_result
            
        except Exception as e:
            logger.error(f"Document creation failed: {str(e)}", exc_info=True)
            
            return DocumentResult(
                document_id=request.request_id,
                success=False,
                content="",
                quality_score=0.0,
                iterations=0,
                metadata={"error": str(e)},
                metrics={},
                errors=[str(e)]
            )
    
    async def _initialize_document(self, request: DocumentRequest) -> str:
        """
        Initialize document state and prepare for creation.
        """
        document_id = request.request_id
        
        # Create initial state
        await self.state_manager.create_document_state(
            document_id=document_id,
            topic=request.topic,
            requirements=request.requirements,
            context=request.context or {}
        )
        
        logger.debug(f"Initialized document state: {document_id}")
        return document_id
    
    async def _execute_workflow_with_iterations(self,
                                                document_id: str,
                                                request: DocumentRequest) -> Dict[str, Any]:
        """
        Execute workflow with quality-based iterations.
        """
        iteration = 0
        best_result = None
        best_score = 0.0
        feedback_history = []
        
        while iteration < self.config.max_iterations:
            iteration += 1
            logger.info(f"Starting iteration {iteration}/{self.config.max_iterations}")
            
            # Update state
            await self.state_manager.update_stage(
                document_id,
                WorkflowStage.RESEARCHING if iteration == 1 else WorkflowStage.ITERATING
            )
            
            # Execute workflow
            result = await self._execute_single_workflow(
                document_id,
                request,
                iteration,
                feedback_history
            )
            
            # Check quality
            quality_score = result.get('quality_score', 0.0)
            
            logger.info(f"Iteration {iteration} quality score: {quality_score:.3f}")
            
            # Track best result
            if quality_score > best_score:
                best_result = result
                best_score = quality_score
            
            # Check if quality threshold met
            if quality_score >= self.config.quality_threshold:
                logger.info(f"Quality threshold met: {quality_score:.3f} >= {self.config.quality_threshold}")
                break
            
            # Prepare feedback for next iteration
            if iteration < self.config.max_iterations:
                feedback = result.get('verification', {}).get('feedback', {})
                feedback_history.append({
                    'iteration': iteration,
                    'score': quality_score,
                    'feedback': feedback
                })
                logger.debug(f"Feedback for next iteration: {feedback}")
        
        # Use best result if threshold never met
        if best_result:
            best_result['iterations'] = iteration
            best_result['quality_score'] = best_score
        
        return best_result or {
            'success': False,
            'error': 'No successful workflow execution',
            'iterations': iteration
        }
    
    async def _execute_single_workflow(self,
                                      document_id: str,
                                      request: DocumentRequest,
                                      iteration: int,
                                      feedback_history: List[Dict]) -> Dict[str, Any]:
        """
        Execute a single workflow iteration.
        """
        workflow_result = {
            'success': False,
            'research': None,
            'draft': None,
            'edited': None,
            'verification': None,
            'quality_score': 0.0
        }
        
        try:
            # Stage 1: Research
            logger.info("Stage 1: Research")
            await self.state_manager.update_stage(document_id, WorkflowStage.RESEARCHING)
            
            research_result = await self._execute_research(
                document_id,
                request,
                feedback_history
            )
            workflow_result['research'] = research_result
            
            if not research_result.get('success'):
                raise Exception("Research stage failed")
            
            # Stage 2: Writing
            logger.info("Stage 2: Writing")
            await self.state_manager.update_stage(document_id, WorkflowStage.WRITING)
            
            writing_result = await self._execute_writing(
                document_id,
                research_result,
                request,
                feedback_history
            )
            workflow_result['draft'] = writing_result
            
            if not writing_result.get('success'):
                raise Exception("Writing stage failed")
            
            # Stage 3: Editing
            logger.info("Stage 3: Editing")
            await self.state_manager.update_stage(document_id, WorkflowStage.EDITING)
            
            editing_result = await self._execute_editing(
                document_id,
                writing_result,
                request,
                feedback_history
            )
            workflow_result['edited'] = editing_result
            
            if not editing_result.get('success'):
                raise Exception("Editing stage failed")
            
            # Stage 4: Verification (if enabled)
            if self.config.enable_verification:
                logger.info("Stage 4: Verification")
                await self.state_manager.update_stage(document_id, WorkflowStage.VERIFYING)
                
                verification_result = await self._execute_verification(
                    document_id,
                    editing_result,
                    research_result,
                    request
                )
                workflow_result['verification'] = verification_result
                workflow_result['quality_score'] = verification_result.get('overall_score', 0.0)
            else:
                workflow_result['quality_score'] = 0.85  # Default if verification disabled
            
            workflow_result['success'] = True
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
            workflow_result['error'] = str(e)
        
        return workflow_result
    
    async def _execute_research(self,
                               document_id: str,
                               request: DocumentRequest,
                               feedback_history: List[Dict]) -> Dict[str, Any]:
        """
        Execute research stage.
        """
        research_agent = self.agents.get('research')
        if not research_agent:
            raise ValueError("Research agent not found")
        
        # Prepare research task
        task = Task(
            task_id=f"{document_id}_research",
            task_type="research",
            payload={
                'topic': request.topic,
                'requirements': request.requirements,
                'feedback': feedback_history
            },
            context={}
        )
        
        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                research_agent.handle_task(task),
                timeout=self.config.research_timeout
            )
            return {
                'success': result.success,
                'context': result.output,
                'metrics': result.metrics
            }
        except asyncio.TimeoutError:
            logger.error("Research stage timed out")
            return {'success': False, 'error': 'Timeout'}
    
    async def _execute_writing(self,
                              document_id: str,
                              research_result: Dict,
                              request: DocumentRequest,
                              feedback_history: List[Dict]) -> Dict[str, Any]:
        """
        Execute writing stage.
        """
        writing_agent = self.agents.get('writing')
        if not writing_agent:
            raise ValueError("Writing agent not found")
        
        task = Task(
            task_id=f"{document_id}_writing",
            task_type="writing",
            payload={
                'research_context': research_result['context'],
                'requirements': request.requirements,
                'feedback': feedback_history
            },
            context={}
        )
        
        try:
            result = await asyncio.wait_for(
                writing_agent.handle_task(task),
                timeout=self.config.writing_timeout
            )
            return {
                'success': result.success,
                'document': result.output.get('document', ''),
                'outline': result.output.get('outline', {}),
                'metrics': result.metrics
            }
        except asyncio.TimeoutError:
            logger.error("Writing stage timed out")
            return {'success': False, 'error': 'Timeout'}
    
    async def _execute_editing(self,
                              document_id: str,
                              writing_result: Dict,
                              request: DocumentRequest,
                              feedback_history: List[Dict]) -> Dict[str, Any]:
        """
        Execute editing stage.
        """
        editing_agent = self.agents.get('editing')
        if not editing_agent:
            raise ValueError("Editing agent not found")
        
        task = Task(
            task_id=f"{document_id}_editing",
            task_type="editing",
            payload={
                'document': writing_result['document'],
                'requirements': request.requirements,
                'feedback': feedback_history
            },
            context={}
        )
        
        try:
            result = await asyncio.wait_for(
                editing_agent.handle_task(task),
                timeout=self.config.editing_timeout
            )
            return {
                'success': result.success,
                'document': result.output.get('edited_document', ''),
                'changes': result.output.get('changes', []),
                'metrics': result.metrics
            }
        except asyncio.TimeoutError:
            logger.error("Editing stage timed out")
            return {'success': False, 'error': 'Timeout'}
    
    async def _execute_verification(self,
                                   document_id: str,
                                   editing_result: Dict,
                                   research_result: Dict,
                                   request: DocumentRequest) -> Dict[str, Any]:
        """
        Execute verification stage.
        """
        verification_agent = self.agents.get('verification')
        if not verification_agent:
            raise ValueError("Verification agent not found")
        
        task = Task(
            task_id=f"{document_id}_verification",
            task_type="verification",
            payload={
                'document': editing_result['document'],
                'research_context': research_result['context'],
                'requirements': request.requirements,
                'quality_threshold': self.config.quality_threshold
            },
            context={}
        )
        
        try:
            result = await asyncio.wait_for(
                verification_agent.handle_task(task),
                timeout=self.config.verification_timeout
            )
            return result.output
        except asyncio.TimeoutError:
            logger.error("Verification stage timed out")
            return {'overall_score': 0.0, 'error': 'Timeout'}
    
    async def _finalize_document(self,
                                document_id: str,
                                workflow_result: Dict[str, Any]) -> DocumentResult:
        """
        Finalize document and prepare result.
        """
        await self.state_manager.update_stage(document_id, WorkflowStage.FINALIZING)
        
        # Extract final document
        final_content = ""
        if workflow_result.get('edited', {}).get('document'):
            final_content = workflow_result['edited']['document']
        elif workflow_result.get('draft', {}).get('document'):
            final_content = workflow_result['draft']['document']
        
        # Compile metrics
        metrics = {
            'research_metrics': workflow_result.get('research', {}).get('metrics', {}),
            'writing_metrics': workflow_result.get('draft', {}).get('metrics', {}),
            'editing_metrics': workflow_result.get('edited', {}).get('metrics', {}),
            'iterations': workflow_result.get('iterations', 0)
        }
        
        # Compile metadata
        metadata = {
            'outline': workflow_result.get('draft', {}).get('outline', {}),
            'changes': workflow_result.get('edited', {}).get('changes', []),
            'verification': workflow_result.get('verification', {}),
            'created_at': datetime.now().isoformat()
        }
        
        # Update final state
        await self.state_manager.update_stage(document_id, WorkflowStage.COMPLETED)
        
        return DocumentResult(
            document_id=document_id,
            success=workflow_result.get('success', False),
            content=final_content,
            quality_score=workflow_result.get('quality_score', 0.0),
            iterations=workflow_result.get('iterations', 0),
            metadata=metadata,
            metrics=metrics
        )
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics from all agents.
        """
        metrics = {}
        for agent_name, agent in self.agents.items():
            metrics[agent_name] = agent.get_metrics()
        return metrics
    
    async def shutdown(self):
        """
        Gracefully shutdown orchestrator and agents.
        """
        logger.info("Shutting down DocumentOrchestrator")
        
        # Close message bus
        await self.message_bus.close()
        
        # Cleanup state manager
        await self.state_manager.close()
        
        logger.info("DocumentOrchestrator shutdown complete")
