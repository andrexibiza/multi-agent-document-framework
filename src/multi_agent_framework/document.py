"""
Document management for the multi-agent framework.

Handles document creation, structure, versioning, and content assembly.
"""

import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class Section:
    """Represents a section of a document."""
    title: str
    content: str
    section_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order: int = 0
    subsections: List['Section'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    def word_count(self) -> int:
        """Calculate word count for this section."""
        words = len(self.content.split())
        for subsection in self.subsections:
            words += subsection.word_count()
        return words
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert section to dictionary."""
        return {
            "section_id": self.section_id,
            "title": self.title,
            "content": self.content,
            "order": self.order,
            "subsections": [s.to_dict() for s in self.subsections],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
        }


@dataclass
class DocumentVersion:
    """Represents a version of a document."""
    version_id: str
    version_number: int
    content: str
    sections: List[Section]
    created_at: datetime
    created_by: str
    change_description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class Document:
    """
    Represents a document being created by the multi-agent system.
    
    Attributes:
        document_id: Unique identifier for the document
        title: Document title
        content: Full document content
        sections: List of document sections
        metadata: Additional document metadata
        requirements: Requirements specified for document creation
        verification_score: Latest verification score
        status: Current document status
    """
    
    def __init__(
        self,
        title: str,
        document_id: Optional[str] = None,
        requirements: Optional[Dict[str, Any]] = None,
    ):
        self.document_id = document_id or str(uuid.uuid4())
        self.title = title
        self.content = ""
        self.sections: List[Section] = []
        self.metadata: Dict[str, Any] = {}
        self.requirements = requirements or {}
        self.verification_score: Optional[float] = None
        self.status = "draft"  # draft, review, final
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.versions: List[DocumentVersion] = []
        self.contributors: List[str] = []
        
        logger.info(f"Document created: {self.document_id} - {self.title}")
    
    @property
    def word_count(self) -> int:
        """Calculate total word count."""
        return len(self.content.split())
    
    @property
    def section_count(self) -> int:
        """Get number of sections."""
        return len(self.sections)
    
    def add_section(
        self,
        title: str,
        content: str,
        order: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Section:
        """Add a new section to the document."""
        section = Section(
            title=title,
            content=content,
            order=order if order is not None else len(self.sections),
            metadata=metadata or {},
        )
        
        self.sections.append(section)
        self.sections.sort(key=lambda s: s.order)
        self._update_content()
        
        logger.debug(f"Section added to {self.document_id}: {title}")
        return section
    
    def update_section(self, section_id: str, content: str) -> bool:
        """Update content of an existing section."""
        for section in self.sections:
            if section.section_id == section_id:
                section.content = content
                section.modified_at = datetime.now()
                self._update_content()
                logger.debug(f"Section updated in {self.document_id}: {section_id}")
                return True
        return False
    
    def remove_section(self, section_id: str) -> bool:
        """Remove a section from the document."""
        original_count = len(self.sections)
        self.sections = [s for s in self.sections if s.section_id != section_id]
        
        if len(self.sections) < original_count:
            self._update_content()
            logger.debug(f"Section removed from {self.document_id}: {section_id}")
            return True
        return False
    
    def _update_content(self) -> None:
        """Rebuild full content from sections."""
        content_parts = []
        
        for section in sorted(self.sections, key=lambda s: s.order):
            content_parts.append(f"# {section.title}\n")
            content_parts.append(section.content)
            content_parts.append("\n")
        
        self.content = "\n".join(content_parts)
        self.modified_at = datetime.now()
    
    def create_version(self, change_description: str, created_by: str = "system") -> DocumentVersion:
        """Create a new version of the document."""
        version = DocumentVersion(
            version_id=str(uuid.uuid4()),
            version_number=len(self.versions) + 1,
            content=self.content,
            sections=[s for s in self.sections],  # Copy sections
            created_at=datetime.now(),
            created_by=created_by,
            change_description=change_description,
            metadata=self.metadata.copy(),
        )
        
        self.versions.append(version)
        logger.info(f"Version {version.version_number} created for {self.document_id}")
        return version
    
    def revert_to_version(self, version_number: int) -> bool:
        """Revert document to a previous version."""
        for version in self.versions:
            if version.version_number == version_number:
                self.content = version.content
                self.sections = [s for s in version.sections]
                self.modified_at = datetime.now()
                logger.info(f"Document {self.document_id} reverted to version {version_number}")
                return True
        return False
    
    def add_contributor(self, contributor_id: str) -> None:
        """Add a contributor to the document."""
        if contributor_id not in self.contributors:
            self.contributors.append(contributor_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary representation."""
        return {
            "document_id": self.document_id,
            "title": self.title,
            "content": self.content,
            "sections": [s.to_dict() for s in self.sections],
            "metadata": self.metadata,
            "requirements": self.requirements,
            "verification_score": self.verification_score,
            "status": self.status,
            "word_count": self.word_count,
            "section_count": self.section_count,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "contributors": self.contributors,
            "version_count": len(self.versions),
        }
    
    def to_json(self) -> str:
        """Convert document to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_markdown(self) -> str:
        """Export document as Markdown."""
        md_parts = []
        md_parts.append(f"# {self.title}\n")
        
        if self.metadata.get("author"):
            md_parts.append(f"**Author:** {self.metadata['author']}\n")
        
        if self.metadata.get("date"):
            md_parts.append(f"**Date:** {self.metadata['date']}\n")
        
        md_parts.append("\n---\n\n")
        md_parts.append(self.content)
        
        return "".join(md_parts)
    
    def __repr__(self) -> str:
        return (
            f"Document(id={self.document_id}, title='{self.title}', "
            f"words={self.word_count}, sections={self.section_count}, "
            f"status={self.status})"
        )


class DocumentManager:
    """
    Manager for document creation and assembly.
    
    Handles document lifecycle, version control, and content assembly
    from multiple agent contributions.
    """
    
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        logger.info("DocumentManager initialized")
    
    def create_document(
        self,
        title: str,
        requirements: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """Create a new document."""
        document = Document(title=title, requirements=requirements)
        self.documents[document.document_id] = document
        logger.info(f"Document created and registered: {document.document_id}")
        return document
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by ID."""
        return self.documents.get(document_id)
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        if document_id in self.documents:
            del self.documents[document_id]
            logger.info(f"Document deleted: {document_id}")
            return True
        return False
    
    def list_documents(self) -> List[Document]:
        """List all managed documents."""
        return list(self.documents.values())
    
    def finalize_document(self, document: Document) -> None:
        """Finalize a document (mark as complete)."""
        document.status = "final"
        document.create_version("Final version", "system")
        logger.info(f"Document finalized: {document.document_id}")
    
    def assemble_from_sections(
        self,
        title: str,
        sections: List[Section],
        requirements: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """Assemble a document from a list of sections."""
        document = self.create_document(title, requirements)
        
        for i, section in enumerate(sections):
            section.order = i
            document.sections.append(section)
        
        document._update_content()
        logger.info(f"Document assembled from {len(sections)} sections")
        return document
    
    def merge_documents(
        self,
        title: str,
        document_ids: List[str],
    ) -> Optional[Document]:
        """Merge multiple documents into one."""
        documents = [self.get_document(doc_id) for doc_id in document_ids]
        documents = [d for d in documents if d is not None]
        
        if not documents:
            return None
        
        merged = self.create_document(title)
        
        for doc in documents:
            for section in doc.sections:
                merged.sections.append(section)
            merged.contributors.extend(doc.contributors)
        
        merged._update_content()
        logger.info(f"Merged {len(documents)} documents into {merged.document_id}")
        return merged
    
    def export_document(
        self,
        document_id: str,
        format: str = "markdown",
    ) -> Optional[str]:
        """Export document in specified format."""
        document = self.get_document(document_id)
        if not document:
            return None
        
        if format == "markdown":
            return document.to_markdown()
        elif format == "json":
            return document.to_json()
        else:
            return document.content
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about managed documents."""
        total_docs = len(self.documents)
        total_words = sum(doc.word_count for doc in self.documents.values())
        total_sections = sum(doc.section_count for doc in self.documents.values())
        
        status_counts = {}
        for doc in self.documents.values():
            status_counts[doc.status] = status_counts.get(doc.status, 0) + 1
        
        return {
            "total_documents": total_docs,
            "total_words": total_words,
            "total_sections": total_sections,
            "average_words_per_document": total_words / total_docs if total_docs > 0 else 0,
            "status_distribution": status_counts,
        }