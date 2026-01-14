"""
Coordinator implementation for orchestrating multi-agent workflows.

The Coordinator manages agent collaboration, task distribution, and
workflow execution for document creation.
"""

import asyncio
import uuid
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .agent import Agent, AgentTask, AgentMessage
from .document import Document, DocumentManager, Section
from .verification import VerificationSystem, VerificationResult
from .config import Config

logger = logging.getLogger(__name__)


class WorkflowMode(Enum):
    """Workflow execution modes."""
    SEQUENTIAL = "sequential"  # Agents work one after another
    PARALLEL = "parallel"  # Agents work simultaneously
    PIPELINE = "pipeline"  # Output of one agent feeds into next
    COLLABORATIVE = "collaborative"  # Agents communicate and iterate


@dataclass
class WorkflowStep:
    """Represents a step in the document creation workflow."""
    step_id: str
    agent_id: str
    task: AgentTask
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Optional[Any] = None


class Coordinator:
    """
    Coordinator for multi-agent document creation workflows.
    
    The Coordinator orchestrates multiple agents to collaborate on document
    creation, manages task distribution, handles agent communication, and
    integrates verification systems.
    
    Attributes:
        agents: List of agents available for task execution
        workflow_mode: Mode of workflow execution
        verification_system: Optional verification system for quality control
        max_iterations: Maximum number of refinement iterations
        config: Configuration object
    """
    
    def __init__(
        self,
        agents: List[Agent],
        workflow_mode: WorkflowMode = WorkflowMode.SEQUENTIAL,
        verification_system: Optional[VerificationSystem] = None,
        max_iterations: int = 3,
        config: Optional[Config] = None,
    ):
        self.coordinator_id = str(uuid.uuid4())
        self.agents = {agent.agent_id: agent for agent in agents}
        self.workflow_mode = workflow_mode
        self.verification_system = verification_system
        self.max_iterations = max_iterations
        self.config = config or Config()
        
        self.document_manager = DocumentManager()
        self.workflow_history: List[WorkflowStep] = []
        
        logger.info(
            f"Coordinator {self.coordinator_id} initialized with "
            f"{len(self.agents)} agents in {workflow_mode.value} mode"
        )
    
    def create_document(
        self,
        topic: str,
        requirements: Dict[str, Any],
        workflow_steps: Optional[List[Dict[str, Any]]] = None,
    ) -> Document:
        """Synchronous wrapper for create_document_async."""
        return asyncio.run(self.create_document_async(topic, requirements, workflow_steps))
    
    async def create_document_async(
        self,
        topic: str,
        requirements: Dict[str, Any],
        workflow_steps: Optional[List[Dict[str, Any]]] = None,
    ) -> Document:
        """
        Create a document using multi-agent collaboration.
        
        Args:
            topic: The document topic
            requirements: Dictionary of document requirements
            workflow_steps: Optional custom workflow steps
            
        Returns:
            Completed Document object
        """
        logger.info(f"Starting document creation for topic: {topic}")
        
        # Initialize document
        document = self.document_manager.create_document(
            title=topic,
            requirements=requirements,
        )
        
        # Generate workflow if not provided
        if workflow_steps is None:
            workflow_steps = self._generate_workflow(topic, requirements)
        
        # Execute workflow
        for iteration in range(self.max_iterations):
            logger.info(f"Workflow iteration {iteration + 1}/{self.max_iterations}")
            
            if self.workflow_mode == WorkflowMode.SEQUENTIAL:
                await self._execute_sequential_workflow(workflow_steps, document)
            elif self.workflow_mode == WorkflowMode.PARALLEL:
                await self._execute_parallel_workflow(workflow_steps, document)
            elif self.workflow_mode == WorkflowMode.PIPELINE:
                await self._execute_pipeline_workflow(workflow_steps, document)
            else:
                await self._execute_collaborative_workflow(workflow_steps, document)
            
            # Verify document if verification system is enabled
            if self.verification_system:
                verification_result = self.verification_system.verify(document)
                document.verification_score = verification_result.overall_score
                
                logger.info(f"Verification score: {verification_result.overall_score}")
                
                if verification_result.passed:
                    logger.info("Document passed verification")
                    break
                else:
                    logger.info("Document needs refinement")
                    # Generate refinement tasks based on verification feedback
                    workflow_steps = self._generate_refinement_workflow(
                        verification_result
                    )
        
        # Finalize document
        self.document_manager.finalize_document(document)
        
        logger.info(f"Document creation completed: {document.document_id}")
        return document
    
    async def _execute_sequential_workflow(
        self,
        workflow_steps: List[Dict[str, Any]],
        document: Document,
    ) -> None:
        """Execute workflow steps sequentially."""
        for step_config in workflow_steps:
            step = self._create_workflow_step(step_config, document)
            agent = self.agents[step.agent_id]
            
            result = await agent.execute_task(step.task)
            step.status = result["status"]
            step.result = result.get("result")
            
            self.workflow_history.append(step)
            
            # Update document with step result
            if step.status == "success":
                self._update_document_from_result(document, step.result)
    
    async def _execute_parallel_workflow(
        self,
        workflow_steps: List[Dict[str, Any]],
        document: Document,
    ) -> None:
        """Execute workflow steps in parallel."""
        steps = [self._create_workflow_step(config, document) for config in workflow_steps]
        tasks = []
        
        for step in steps:
            agent = self.agents[step.agent_id]
            tasks.append(agent.execute_task(step.task))
        
        results = await asyncio.gather(*tasks)
        
        for step, result in zip(steps, results):
            step.status = result["status"]
            step.result = result.get("result")
            self.workflow_history.append(step)
            
            if step.status == "success":
                self._update_document_from_result(document, step.result)
    
    async def _execute_pipeline_workflow(
        self,
        workflow_steps: List[Dict[str, Any]],
        document: Document,
    ) -> None:
        """Execute workflow as a pipeline where output feeds into next step."""
        previous_result = None
        
        for step_config in workflow_steps:
            step = self._create_workflow_step(step_config, document)
            
            # Add previous result to task requirements
            if previous_result:
                step.task.requirements["previous_output"] = previous_result
            
            agent = self.agents[step.agent_id]
            result = await agent.execute_task(step.task)
            
            step.status = result["status"]
            step.result = result.get("result")
            self.workflow_history.append(step)
            
            if step.status == "success":
                self._update_document_from_result(document, step.result)
                previous_result = step.result
    
    async def _execute_collaborative_workflow(
        self,
        workflow_steps: List[Dict[str, Any]],
        document: Document,
    ) -> None:
        """Execute workflow with agent collaboration and feedback loops."""
        # First pass: parallel execution
        await self._execute_parallel_workflow(workflow_steps, document)
        
        # Feedback round: agents review each other's work
        for step_config in workflow_steps:
            if step_config.get("enable_feedback", False):
                feedback_step = self._create_feedback_step(step_config, document)
                agent = self.agents[feedback_step.agent_id]
                
                result = await agent.execute_task(feedback_step.task)
                
                if result["status"] == "success":
                    self._update_document_from_result(document, result["result"])
    
    def _generate_workflow(self, topic: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate workflow steps based on requirements and available agents."""
        workflow = []
        
        # Find agents by role
        researcher = self._find_agent_by_role("researcher")
        writer = self._find_agent_by_role("writer")
        editor = self._find_agent_by_role("editor")
        
        # Research phase
        if researcher:
            workflow.append({
                "agent_id": researcher.agent_id,
                "task_type": "research",
                "description": f"Research information about: {topic}",
                "requirements": requirements,
            })
        
        # Writing phase
        if writer:
            workflow.append({
                "agent_id": writer.agent_id,
                "task_type": "write",
                "description": f"Write content about: {topic}",
                "requirements": requirements,
            })
        
        # Editing phase
        if editor:
            workflow.append({
                "agent_id": editor.agent_id,
                "task_type": "edit",
                "description": f"Edit and refine content for: {topic}",
                "requirements": requirements,
            })
        
        return workflow
    
    def _generate_refinement_workflow(
        self,
        verification_result: VerificationResult,
    ) -> List[Dict[str, Any]]:
        """Generate refinement workflow based on verification feedback."""
        workflow = []
        
        for issue in verification_result.issues:
            agent = self._find_agent_for_issue(issue)
            if agent:
                workflow.append({
                    "agent_id": agent.agent_id,
                    "task_type": "refinement",
                    "description": f"Address issue: {issue['description']}",
                    "requirements": {"issue": issue},
                })
        
        return workflow
    
    def _create_workflow_step(
        self,
        step_config: Dict[str, Any],
        document: Document,
    ) -> WorkflowStep:
        """Create a workflow step from configuration."""
        task = AgentTask(
            task_id=str(uuid.uuid4()),
            description=step_config["description"],
            requirements=step_config.get("requirements", {}),
        )
        
        return WorkflowStep(
            step_id=str(uuid.uuid4()),
            agent_id=step_config["agent_id"],
            task=task,
            dependencies=step_config.get("dependencies", []),
        )
    
    def _create_feedback_step(
        self,
        step_config: Dict[str, Any],
        document: Document,
    ) -> WorkflowStep:
        """Create a feedback step for collaborative workflow."""
        reviewer = self._find_agent_by_role("reviewer")
        if not reviewer:
            reviewer = list(self.agents.values())[0]  # Fallback to any agent
        
        task = AgentTask(
            task_id=str(uuid.uuid4()),
            description=f"Review and provide feedback on: {step_config['description']}",
            requirements={"original_task": step_config},
        )
        
        return WorkflowStep(
            step_id=str(uuid.uuid4()),
            agent_id=reviewer.agent_id,
            task=task,
        )
    
    def _update_document_from_result(self, document: Document, result: Dict[str, Any]) -> None:
        """Update document with agent task result."""
        if "content" in result:
            # Add content to document
            section = Section(
                title=result.get("title", "Untitled Section"),
                content=result["content"],
                metadata=result.get("metadata", {}),
            )
            document.sections.append(section)
            document.content += "\n\n" + result["content"]
    
    def _find_agent_by_role(self, role: str) -> Optional[Agent]:
        """Find first agent with specified role."""
        for agent in self.agents.values():
            if agent.role == role:
                return agent
        return None
    
    def _find_agent_for_issue(self, issue: Dict[str, Any]) -> Optional[Agent]:
        """Find appropriate agent to handle a verification issue."""
        issue_type = issue.get("type")
        
        role_mapping = {
            "factual_accuracy": "fact_checker",
            "consistency": "editor",
            "grammar": "editor",
            "style": "editor",
            "completeness": "writer",
        }
        
        role = role_mapping.get(issue_type, "editor")
        return self._find_agent_by_role(role)
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status and statistics."""
        completed_steps = [s for s in self.workflow_history if s.status == "success"]
        failed_steps = [s for s in self.workflow_history if s.status == "failed"]
        
        return {
            "coordinator_id": self.coordinator_id,
            "workflow_mode": self.workflow_mode.value,
            "total_steps": len(self.workflow_history),
            "completed_steps": len(completed_steps),
            "failed_steps": len(failed_steps),
            "active_agents": len(self.agents),
        }