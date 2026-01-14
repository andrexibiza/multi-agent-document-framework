"""Tests for data models."""

import pytest
from datetime import datetime

from madf.models.document import Document, DocumentSection, DocumentStatus
from madf.models.request import DocumentRequest
from madf.models.task import Task, TaskResult


class TestDocumentModels:
    """Test document-related models."""
    
    def test_document_section_creation(self):
        """Test DocumentSection creation."""
        section = DocumentSection(
            title="Introduction",
            content="This is the introduction.",
            order=0
        )
        
        assert section.title == "Introduction"
        assert section.order == 0
        assert section.word_count() == 4
    
    def test_document_creation(self):
        """Test Document creation."""
        sections = [
            DocumentSection("Section 1", "Content 1", 0),
            DocumentSection("Section 2", "Content 2", 1)
        ]
        
        document = Document(
            id="test_123",
            title="Test Document",
            sections=sections,
            status=DocumentStatus.COMPLETE,
            quality_score=0.90
        )
        
        assert document.id == "test_123"
        assert document.title == "Test Document"
        assert len(document.sections) == 2
        assert document.quality_score == 0.90
    
    def test_document_get_full_text(self):
        """Test getting full document text."""
        sections = [
            DocumentSection("Section 1", "Content one", 0),
            DocumentSection("Section 2", "Content two", 1)
        ]
        
        document = Document(
            id="test",
            title="Test",
            sections=sections,
            status=DocumentStatus.COMPLETE
        )
        
        full_text = document.get_full_text()
        assert "Content one" in full_text
        assert "Content two" in full_text
    
    def test_document_update_word_count(self):
        """Test word count update."""
        sections = [
            DocumentSection("S1", "One two three", 0),
            DocumentSection("S2", "Four five", 1)
        ]
        
        document = Document(
            id="test",
            title="Test",
            sections=sections,
            status=DocumentStatus.COMPLETE
        )
        
        document.update_word_count()
        assert document.word_count == 5
    
    def test_document_to_markdown(self):
        """Test Markdown conversion."""
        sections = [
            DocumentSection("Introduction", "Test intro", 0)
        ]
        
        document = Document(
            id="test",
            title="Test Document",
            sections=sections,
            status=DocumentStatus.COMPLETE
        )
        
        markdown = document.to_markdown()
        assert "# Test Document" in markdown
        assert "## Introduction" in markdown
        assert "Test intro" in markdown


class TestDocumentRequest:
    """Test DocumentRequest model."""
    
    def test_valid_request(self):
        """Test valid request creation."""
        request = DocumentRequest(
            topic="Test Topic",
            document_type="article",
            target_length=2000,
            style="formal",
            audience="general"
        )
        
        assert request.validate() is True
    
    def test_invalid_topic_length(self):
        """Test validation with short topic."""
        request = DocumentRequest(
            topic="AB",
            document_type="article",
            target_length=2000
        )
        
        with pytest.raises(ValueError, match="at least 5 characters"):
            request.validate()
    
    def test_invalid_target_length(self):
        """Test validation with invalid length."""
        request = DocumentRequest(
            topic="Valid Topic",
            document_type="article",
            target_length=50
        )
        
        with pytest.raises(ValueError, match="at least 100 words"):
            request.validate()


class TestTaskModels:
    """Test task-related models."""
    
    def test_task_creation(self):
        """Test Task creation."""
        task = Task(
            id="task_1",
            type="research",
            data={'query': 'test'},
            priority=5
        )
        
        assert task.id == "task_1"
        assert task.type == "research"
        assert task.priority == 5
        assert isinstance(task.created_at, datetime)
    
    def test_task_result_creation(self):
        """Test TaskResult creation."""
        result = TaskResult(
            task_id="task_1",
            success=True,
            data={'result': 'test'},
            execution_time=1.5
        )
        
        assert result.task_id == "task_1"
        assert result.success is True
        assert result.execution_time == 1.5