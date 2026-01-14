"""Document request models."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class DocumentRequest:
    """
    Request for document creation.
    
    Attributes:
        topic: Main topic/title
        document_type: Type of document (article, paper, report, etc.)
        target_length: Target word count
        style: Writing style (formal, casual, technical, etc.)
        audience: Target audience
        requirements: List of specific requirements
        references: Optional list of reference materials
        outline: Optional predefined outline
        metadata: Additional request metadata
    """
    topic: str
    document_type: str
    target_length: int
    style: str = "formal"
    audience: str = "general"
    requirements: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    outline: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """
        Validate request parameters.
        
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not self.topic or len(self.topic) < 5:
            raise ValueError("Topic must be at least 5 characters")
        
        if self.target_length < 100:
            raise ValueError("Target length must be at least 100 words")
        
        if self.target_length > 50000:
            raise ValueError("Target length cannot exceed 50,000 words")
        
        valid_types = ['article', 'paper', 'report', 'essay', 'blog', 'documentation']
        if self.document_type not in valid_types:
            # Allow custom types but warn
            pass
        
        return True