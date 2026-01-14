"""State storage for document persistence."""

import json
from typing import Optional, Dict, Any
from pathlib import Path
import logging

from ..models.document import Document, DocumentStatus, DocumentSection
from datetime import datetime

logger = logging.getLogger(__name__)


class StateStore:
    """
    State storage for documents and workflow state.
    
    Provides persistence layer for:
    - Document storage and retrieval
    - Workflow state management
    - Recovery and resume capabilities
    
    Implementation uses file-based storage by default.
    Can be extended to use databases (PostgreSQL, MongoDB, etc.)
    """
    
    def __init__(self, storage_path: str = "./.madf_state"):
        """
        Initialize state store.
        
        Args:
            storage_path: Path for state storage
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"StateStore initialized at {self.storage_path}")
    
    async def save_document(self, document: Document):
        """
        Save document to storage.
        
        Args:
            document: Document to save
        """
        doc_path = self.storage_path / f"{document.id}.json"
        
        # Convert document to dict
        doc_dict = self._document_to_dict(document)
        
        # Write to file
        with open(doc_path, 'w') as f:
            json.dump(doc_dict, f, indent=2, default=str)
        
        logger.debug(f"Document {document.id} saved")
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """
        Retrieve document from storage.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        doc_path = self.storage_path / f"{document_id}.json"
        
        if not doc_path.exists():
            return None
        
        # Read from file
        with open(doc_path, 'r') as f:
            doc_dict = json.load(f)
        
        # Convert dict to document
        document = self._dict_to_document(doc_dict)
        
        logger.debug(f"Document {document_id} retrieved")
        return document
    
    async def delete_document(self, document_id: str):
        """
        Delete document from storage.
        
        Args:
            document_id: Document ID
        """
        doc_path = self.storage_path / f"{document_id}.json"
        
        if doc_path.exists():
            doc_path.unlink()
            logger.debug(f"Document {document_id} deleted")
    
    def _document_to_dict(self, document: Document) -> Dict[str, Any]:
        """
        Convert document to dictionary.
        
        Args:
            document: Document to convert
            
        Returns:
            Dictionary representation
        """
        return {
            'id': document.id,
            'title': document.title,
            'sections': [
                {
                    'title': s.title,
                    'content': s.content,
                    'order': s.order,
                    'metadata': s.metadata
                }
                for s in document.sections
            ],
            'status': document.status.value,
            'quality_score': document.quality_score,
            'word_count': document.word_count,
            'created_at': document.created_at.isoformat(),
            'updated_at': document.updated_at.isoformat(),
            'metadata': document.metadata
        }
    
    def _dict_to_document(self, doc_dict: Dict[str, Any]) -> Document:
        """
        Convert dictionary to document.
        
        Args:
            doc_dict: Dictionary representation
            
        Returns:
            Document instance
        """
        sections = [
            DocumentSection(
                title=s['title'],
                content=s['content'],
                order=s['order'],
                metadata=s.get('metadata', {})
            )
            for s in doc_dict.get('sections', [])
        ]
        
        return Document(
            id=doc_dict['id'],
            title=doc_dict['title'],
            sections=sections,
            status=DocumentStatus(doc_dict['status']),
            quality_score=doc_dict.get('quality_score', 0.0),
            word_count=doc_dict.get('word_count', 0),
            created_at=datetime.fromisoformat(doc_dict['created_at']),
            updated_at=datetime.fromisoformat(doc_dict['updated_at']),
            metadata=doc_dict.get('metadata', {})
        )