"""
Unit tests for Document and DocumentManager classes.
"""

import pytest
from multi_agent_framework import Document, DocumentManager, Section


class TestDocument:
    """Test cases for Document class."""
    
    def test_document_creation(self):
        """Test document creation with basic parameters."""
        doc = Document(title="Test Document")
        
        assert doc.title == "Test Document"
        assert doc.status == "draft"
        assert doc.word_count == 0
        assert doc.section_count == 0
    
    def test_document_with_requirements(self):
        """Test document creation with requirements."""
        requirements = {
            "length": "1000 words",
            "style": "technical",
        }
        
        doc = Document(
            title="Technical Doc",
            requirements=requirements,
        )
        
        assert doc.requirements == requirements
    
    def test_add_section(self):
        """Test adding sections to document."""
        doc = Document(title="Test")
        
        section = doc.add_section(
            title="Introduction",
            content="This is the introduction.",
        )
        
        assert doc.section_count == 1
        assert section.title == "Introduction"
        assert "introduction" in doc.content.lower()
    
    def test_multiple_sections(self):
        """Test adding multiple sections."""
        doc = Document(title="Test")
        
        doc.add_section("Section 1", "Content 1")
        doc.add_section("Section 2", "Content 2")
        doc.add_section("Section 3", "Content 3")
        
        assert doc.section_count == 3
    
    def test_section_ordering(self):
        """Test section ordering."""
        doc = Document(title="Test")
        
        doc.add_section("Third", "Content 3", order=2)
        doc.add_section("First", "Content 1", order=0)
        doc.add_section("Second", "Content 2", order=1)
        
        assert doc.sections[0].title == "First"
        assert doc.sections[1].title == "Second"
        assert doc.sections[2].title == "Third"
    
    def test_update_section(self):
        """Test updating section content."""
        doc = Document(title="Test")
        section = doc.add_section("Test Section", "Original content")
        
        updated = doc.update_section(section.section_id, "Updated content")
        
        assert updated is True
        assert "Updated content" in doc.content
    
    def test_remove_section(self):
        """Test removing a section."""
        doc = Document(title="Test")
        section = doc.add_section("Test Section", "Content")
        
        assert doc.section_count == 1
        
        removed = doc.remove_section(section.section_id)
        
        assert removed is True
        assert doc.section_count == 0
    
    def test_word_count(self):
        """Test word count calculation."""
        doc = Document(title="Test")
        doc.add_section("Section", "This is a test with five words")
        
        # Content includes heading, so more than 5 words
        assert doc.word_count > 0
    
    def test_create_version(self):
        """Test creating document versions."""
        doc = Document(title="Test")
        doc.add_section("Section 1", "Content 1")
        
        version = doc.create_version("Initial version", "user_01")
        
        assert len(doc.versions) == 1
        assert version.version_number == 1
        assert version.created_by == "user_01"
    
    def test_to_markdown(self):
        """Test Markdown export."""
        doc = Document(title="Test Document")
        doc.add_section("Introduction", "This is the intro.")
        
        markdown = doc.to_markdown()
        
        assert "# Test Document" in markdown
        assert "Introduction" in markdown
    
    def test_to_json(self):
        """Test JSON export."""
        doc = Document(title="Test")
        doc.add_section("Section", "Content")
        
        json_str = doc.to_json()
        
        assert "Test" in json_str
        assert "Section" in json_str
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        doc = Document(title="Test")
        doc.add_section("Section", "Content")
        
        doc_dict = doc.to_dict()
        
        assert doc_dict["title"] == "Test"
        assert doc_dict["section_count"] == 1
        assert "sections" in doc_dict


class TestSection:
    """Test cases for Section class."""
    
    def test_section_creation(self):
        """Test section creation."""
        section = Section(
            title="Test Section",
            content="Test content",
        )
        
        assert section.title == "Test Section"
        assert section.content == "Test content"
        assert isinstance(section.section_id, str)
    
    def test_section_word_count(self):
        """Test section word count."""
        section = Section(
            title="Test",
            content="One two three four five",
        )
        
        assert section.word_count() == 5
    
    def test_section_to_dict(self):
        """Test section dictionary conversion."""
        section = Section(
            title="Test",
            content="Content",
            metadata={"author": "test_user"},
        )
        
        section_dict = section.to_dict()
        
        assert section_dict["title"] == "Test"
        assert section_dict["content"] == "Content"
        assert section_dict["metadata"]["author"] == "test_user"


class TestDocumentManager:
    """Test cases for DocumentManager class."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = DocumentManager()
        
        assert len(manager.documents) == 0
    
    def test_create_document(self):
        """Test creating document through manager."""
        manager = DocumentManager()
        
        doc = manager.create_document("Test Document")
        
        assert doc is not None
        assert doc.title == "Test Document"
        assert doc.document_id in manager.documents
    
    def test_get_document(self):
        """Test retrieving document by ID."""
        manager = DocumentManager()
        doc = manager.create_document("Test")
        
        retrieved = manager.get_document(doc.document_id)
        
        assert retrieved is not None
        assert retrieved.document_id == doc.document_id
    
    def test_list_documents(self):
        """Test listing all documents."""
        manager = DocumentManager()
        
        manager.create_document("Doc 1")
        manager.create_document("Doc 2")
        manager.create_document("Doc 3")
        
        docs = manager.list_documents()
        
        assert len(docs) == 3
    
    def test_delete_document(self):
        """Test deleting a document."""
        manager = DocumentManager()
        doc = manager.create_document("Test")
        
        assert len(manager.documents) == 1
        
        deleted = manager.delete_document(doc.document_id)
        
        assert deleted is True
        assert len(manager.documents) == 0
    
    def test_finalize_document(self):
        """Test finalizing a document."""
        manager = DocumentManager()
        doc = manager.create_document("Test")
        
        assert doc.status == "draft"
        
        manager.finalize_document(doc)
        
        assert doc.status == "final"
        assert len(doc.versions) > 0
    
    def test_get_statistics(self):
        """Test getting manager statistics."""
        manager = DocumentManager()
        
        doc1 = manager.create_document("Doc 1")
        doc1.add_section("Section", "Content with five words here")
        
        doc2 = manager.create_document("Doc 2")
        doc2.add_section("Section", "More content")
        
        stats = manager.get_statistics()
        
        assert stats["total_documents"] == 2
        assert stats["total_words"] > 0
        assert stats["total_sections"] == 2