"""Document data models."""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentStatus(Enum):
    """Document creation status."""
    PENDING = "pending"
    RESEARCHING = "researching"
    WRITING = "writing"
    EDITING = "editing"
    VERIFYING = "verifying"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class DocumentSection:
    """
    Represents a section of a document.
    
    Attributes:
        title: Section title
        content: Section content
        order: Section order in document
        metadata: Additional section metadata
    """
    title: str
    content: str
    order: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def word_count(self) -> int:
        """Get word count for this section."""
        return len(self.content.split())


@dataclass
class Document:
    """
    Complete document with metadata.
    
    Attributes:
        id: Unique document identifier
        title: Document title
        sections: List of document sections
        status: Current document status
        quality_score: Quality score (0-1)
        word_count: Total word count
        created_at: Creation timestamp
        updated_at: Last update timestamp
        metadata: Additional document metadata
    """
    id: str
    title: str
    sections: List[DocumentSection]
    status: DocumentStatus
    quality_score: float = 0.0
    word_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_full_text(self) -> str:
        """
        Get complete document text.
        
        Returns:
            Full document text with all sections
        """
        sorted_sections = sorted(self.sections, key=lambda x: x.order)
        return "\n\n".join([s.content for s in sorted_sections])
    
    def update_word_count(self):
        """Update word count based on content."""
        text = self.get_full_text()
        self.word_count = len(text.split())
    
    def get_section(self, title: str) -> DocumentSection:
        """Get section by title."""
        for section in self.sections:
            if section.title.lower() == title.lower():
                return section
        raise ValueError(f"Section not found: {title}")
    
    def to_markdown(self) -> str:
        """
        Convert document to Markdown format.
        
        Returns:
            Document in Markdown format
        """
        md = f"# {self.title}\n\n"
        
        for section in sorted(self.sections, key=lambda x: x.order):
            md += f"## {section.title}\n\n"
            md += f"{section.content}\n\n"
        
        return md
    
    def to_html(self) -> str:
        """
        Convert document to HTML format.
        
        Returns:
            Document in HTML format
        """
        html = f"<html><head><title>{self.title}</title></head><body>\n"
        html += f"<h1>{self.title}</h1>\n"
        
        for section in sorted(self.sections, key=lambda x: x.order):
            html += f"<h2>{section.title}</h2>\n"
            # Simple paragraph conversion
            paragraphs = section.content.split('\n\n')
            for p in paragraphs:
                if p.strip():
                    html += f"<p>{p.strip()}</p>\n"
        
        html += "</body></html>"
        return html