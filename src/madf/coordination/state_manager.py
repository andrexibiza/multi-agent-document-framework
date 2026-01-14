"""
State manager for distributed state across agents.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from madf.models import DocumentState, WorkflowState, StateChange

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages shared state across agents.
    
    Features:
    - Document state storage
    - Workflow state tracking
    - State versioning
    - Atomic operations
    - State history
    """
    
    def __init__(self, backend: str = "memory"):
        """
        Initialize state manager.
        
        Args:
            backend: Storage backend ('memory', 'redis', etc.)
        """
        self.backend = backend
        self.document_states: Dict[str, DocumentState] = {}
        self.workflow_states: Dict[str, WorkflowState] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        
        logger.info(f"StateManager initialized with backend: {backend}")
    
    async def create_document_state(self,
                                   document_id: str,
                                   topic: str,
                                   requirements: Dict[str, Any],
                                   context: Dict[str, Any]) -> DocumentState:
        """
        Create new document state.
        
        Args:
            document_id: Unique document identifier
            topic: Document topic
            requirements: Document requirements
            context: Additional context
        
        Returns:
            Created document state
        """
        state = DocumentState(
            document_id=document_id,
            metadata={
                'topic': topic,
                'requirements': requirements,
                'context': context
            }
        )
        
        self.document_states[document_id] = state
        self.locks[document_id] = asyncio.Lock()
        
        logger.debug(f"Created document state: {document_id}")
        return state
    
    async def get_document_state(self, document_id: str) -> Optional[DocumentState]:
        """
        Get document state by ID.
        """
        return self.document_states.get(document_id)
    
    async def update_document_content(self,
                                     document_id: str,
                                     content: str,
                                     actor: str) -> bool:
        """
        Update document content atomically.
        
        Args:
            document_id: Document to update
            content: New content
            actor: Agent making the update
        
        Returns:
            True if successful
        """
        if document_id not in self.document_states:
            logger.warning(f"Document not found: {document_id}")
            return False
        
        async with self.locks[document_id]:
            state = self.document_states[document_id]
            previous_content = state.content
            
            # Update content
            state.content = content
            state.version += 1
            state.updated_at = datetime.now()
            
            # Record change
            change = StateChange(
                actor=actor,
                action="update_content",
                previous_state=previous_content[:100] + "..." if len(previous_content) > 100 else previous_content,
                new_state=content[:100] + "..." if len(content) > 100 else content
            )
            state.history.append(change)
            
            logger.debug(f"Updated document {document_id} to version {state.version}")
            return True
    
    async def update_document_metadata(self,
                                      document_id: str,
                                      metadata: Dict[str, Any],
                                      actor: str) -> bool:
        """
        Update document metadata.
        """
        if document_id not in self.document_states:
            return False
        
        async with self.locks[document_id]:
            state = self.document_states[document_id]
            previous_metadata = state.metadata.copy()
            
            # Merge metadata
            state.metadata.update(metadata)
            state.updated_at = datetime.now()
            
            # Record change
            change = StateChange(
                actor=actor,
                action="update_metadata",
                previous_state=previous_metadata,
                new_state=state.metadata.copy()
            )
            state.history.append(change)
            
            return True
    
    async def create_workflow_state(self,
                                   workflow_id: str,
                                   stages: List[str]) -> WorkflowState:
        """
        Create new workflow state.
        """
        state = WorkflowState(
            workflow_id=workflow_id,
            stage=stages[0] if stages else "unknown",
            pending_stages=stages.copy()
        )
        
        self.workflow_states[workflow_id] = state
        logger.debug(f"Created workflow state: {workflow_id}")
        return state
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """
        Get workflow state by ID.
        """
        return self.workflow_states.get(workflow_id)
    
    async def update_stage(self, workflow_id: str, stage: Any) -> bool:
        """
        Update current workflow stage.
        """
        if workflow_id not in self.workflow_states:
            # Create if doesn't exist
            await self.create_workflow_state(workflow_id, [])
        
        state = self.workflow_states[workflow_id]
        state.stage = stage.value if hasattr(stage, 'value') else str(stage)
        state.updated_at = datetime.now()
        
        logger.debug(f"Updated workflow {workflow_id} to stage: {state.stage}")
        return True
    
    async def complete_stage(self,
                           workflow_id: str,
                           stage: str,
                           quality_score: Optional[float] = None) -> bool:
        """
        Mark a workflow stage as completed.
        """
        if workflow_id not in self.workflow_states:
            return False
        
        state = self.workflow_states[workflow_id]
        
        if stage not in state.completed_stages:
            state.completed_stages.append(stage)
        
        if stage in state.pending_stages:
            state.pending_stages.remove(stage)
        
        if quality_score is not None:
            state.quality_scores[stage] = quality_score
        
        state.updated_at = datetime.now()
        
        logger.debug(f"Completed stage {stage} for workflow {workflow_id}")
        return True
    
    async def get_state_history(self, document_id: str) -> List[StateChange]:
        """
        Get complete state change history for a document.
        """
        if document_id not in self.document_states:
            return []
        
        return self.document_states[document_id].history.copy()
    
    async def snapshot_state(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Create a snapshot of current document state.
        """
        if document_id not in self.document_states:
            return None
        
        state = self.document_states[document_id]
        
        return {
            'document_id': state.document_id,
            'version': state.version,
            'content': state.content,
            'metadata': state.metadata,
            'updated_at': state.updated_at.isoformat(),
            'history_length': len(state.history)
        }
    
    async def restore_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """
        Restore document state from snapshot.
        """
        try:
            document_id = snapshot['document_id']
            
            if document_id not in self.document_states:
                # Create new state
                state = DocumentState(
                    document_id=document_id,
                    version=snapshot['version'],
                    content=snapshot['content'],
                    metadata=snapshot['metadata']
                )
                self.document_states[document_id] = state
                self.locks[document_id] = asyncio.Lock()
            else:
                # Update existing
                async with self.locks[document_id]:
                    state = self.document_states[document_id]
                    state.version = snapshot['version']
                    state.content = snapshot['content']
                    state.metadata = snapshot['metadata']
            
            logger.info(f"Restored snapshot for document: {document_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to restore snapshot: {e}")
            return False
    
    async def close(self):
        """
        Close state manager and cleanup.
        """
        logger.info("Closing StateManager")
        
        # In production, persist state here
        self.document_states.clear()
        self.workflow_states.clear()
        self.locks.clear()
        
        logger.info("StateManager closed")
