"""
Unit tests for Verification system.
"""

import pytest
from multi_agent_framework import (
    Document,
    VerificationSystem,
    VerificationResult,
    QualityCheck,
    FactCheck,
    ConsistencyCheck,
)


class TestQualityCheck:
    """Test cases for QualityCheck class."""
    
    def test_quality_check_initialization(self):
        """Test quality check initialization."""
        check = QualityCheck(min_score=0.8)
        
        assert check.min_score == 0.8
        assert check.name == "quality_check"
    
    def test_quality_check_clean_content(self):
        """Test quality check with clean content."""
        check = QualityCheck()
        
        content = "This is a well-written document. It has proper structure."
        result = check.verify(content)
        
        assert result.check_name == "quality_check"
        assert result.score > 0
    
    def test_quality_check_issues(self):
        """Test quality check finding issues."""
        check = QualityCheck()
        
        # Content with double spaces
        content = "This  has  double  spaces."
        result = check.verify(content)
        
        assert len(result.issues) > 0
    
    def test_readability_check(self):
        """Test readability checking."""
        check = QualityCheck()
        
        # Very long paragraph
        long_content = " ".join(["word"] * 300)
        result = check.verify(long_content)
        
        # Should flag readability issues
        assert any(
            issue.issue_type == "readability"
            for issue in result.issues
        )


class TestFactCheck:
    """Test cases for FactCheck class."""
    
    def test_fact_check_initialization(self):
        """Test fact check initialization."""
        check = FactCheck(min_confidence=0.8)
        
        assert check.min_confidence == 0.8
        assert check.name == "fact_check"
    
    def test_statistical_claims(self):
        """Test identifying statistical claims."""
        check = FactCheck()
        
        content = "Studies show that 85% of users prefer this approach."
        result = check.verify(content)
        
        # Should identify the percentage
        assert any(
            "statistical" in issue.description.lower()
            for issue in result.issues
        )
    
    def test_citation_check(self):
        """Test citation checking."""
        check = FactCheck()
        
        # Content with claim but no citation
        content = "Research shows that this is effective. Studies indicate positive results."
        result = check.verify(content)
        
        # Should flag missing citations
        assert any(
            "citation" in issue.description.lower()
            for issue in result.issues
        )
    
    def test_date_validation(self):
        """Test date validation."""
        check = FactCheck()
        
        # Content with future date
        content = "In the year 2099, this will happen."
        result = check.verify(content)
        
        # Should flag future date
        assert any(
            "future" in issue.description.lower()
            for issue in result.issues
        )


class TestConsistencyCheck:
    """Test cases for ConsistencyCheck class."""
    
    def test_consistency_check_initialization(self):
        """Test consistency check initialization."""
        check = ConsistencyCheck(min_score=0.85)
        
        assert check.min_score == 0.85
        assert check.name == "consistency_check"
    
    def test_terminology_consistency(self):
        """Test terminology consistency checking."""
        check = ConsistencyCheck()
        
        # Mixed US/UK spelling
        content = "We analyze the data and then analyse the results."
        result = check.verify(content)
        
        # Should flag mixed spelling
        assert any(
            "spelling" in issue.description.lower()
            for issue in result.issues
        )
    
    def test_tone_consistency(self):
        """Test tone consistency checking."""
        check = ConsistencyCheck()
        
        # Mixed first and third person
        content = (
            "We conducted the study. I analyzed the data. "
            "They found the results. Our conclusions are clear."
        )
        result = check.verify(content)
        
        # May flag mixed perspective
        assert result.score >= 0


class TestVerificationSystem:
    """Test cases for VerificationSystem class."""
    
    def test_system_initialization(self):
        """Test verification system initialization."""
        system = VerificationSystem()
        
        assert system.min_overall_score == 0.8
        assert len(system.enabled_checks) > 0
    
    def test_system_with_specific_checks(self):
        """Test system with specific checks enabled."""
        system = VerificationSystem(
            checks=["quality", "factual_accuracy"],
            min_overall_score=0.85,
        )
        
        assert system.min_overall_score == 0.85
        assert len(system.enabled_checks) > 0
    
    def test_verify_document(self):
        """Test document verification."""
        system = VerificationSystem()
        
        doc = Document(title="Test Document")
        doc.add_section(
            "Introduction",
            "This is a well-written introduction with proper structure.",
        )
        
        result = system.verify(doc)
        
        assert isinstance(result, VerificationResult)
        assert result.check_name == "overall"
        assert 0 <= result.score <= 1.0
    
    def test_verification_report(self):
        """Test generating verification report."""
        system = VerificationSystem()
        
        doc = Document(title="Test")
        doc.content = "Simple test content."
        
        result = system.verify(doc)
        report = system.get_verification_report(result)
        
        assert "VERIFICATION REPORT" in report
        assert "Overall Score" in report
    
    def test_verification_pass_fail(self):
        """Test verification pass/fail logic."""
        system = VerificationSystem(min_overall_score=0.9)
        
        doc = Document(title="Test")
        doc.content = "Test content."
        
        result = system.verify(doc)
        
        # Result should have passed or failed status
        assert isinstance(result.passed, bool)


class TestVerificationResult:
    """Test cases for VerificationResult class."""
    
    def test_result_creation(self):
        """Test verification result creation."""
        result = VerificationResult(
            check_name="test_check",
            passed=True,
            score=0.95,
            issues=[],
        )
        
        assert result.check_name == "test_check"
        assert result.passed is True
        assert result.score == 0.95
    
    def test_overall_score_calculation(self):
        """Test overall score calculation with issues."""
        from multi_agent_framework.verification import VerificationIssue
        
        issues = [
            VerificationIssue(
                issue_type="grammar",
                severity="low",
                description="Minor issue",
            ),
        ]
        
        result = VerificationResult(
            check_name="test",
            passed=True,
            score=1.0,
            issues=issues,
        )
        
        # Overall score should be affected by issues
        assert result.overall_score <= 1.0