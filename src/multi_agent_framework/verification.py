"""
Verification system for validating document quality and accuracy.

This module provides comprehensive verification capabilities including
factual accuracy checks, consistency validation, and quality assessment.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class VerificationIssue:
    """Represents an issue found during verification."""
    issue_type: str
    severity: str  # low, medium, high, critical
    description: str
    location: Optional[str] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    """Result of a verification check."""
    check_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    issues: List[VerificationIssue] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def overall_score(self) -> float:
        """Calculate overall score considering issue severity."""
        if not self.issues:
            return self.score
        
        severity_weights = {
            "low": 0.95,
            "medium": 0.80,
            "high": 0.60,
            "critical": 0.30,
        }
        
        penalty = sum(
            (1.0 - severity_weights.get(issue.severity, 0.90))
            for issue in self.issues
        )
        
        return max(0.0, self.score - (penalty / len(self.issues) if self.issues else 0))


class QualityCheck:
    """
    Quality check for document content.
    
    Evaluates grammar, style, readability, and overall quality.
    """
    
    def __init__(self, min_score: float = 0.8):
        self.min_score = min_score
        self.name = "quality_check"
    
    def verify(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> VerificationResult:
        """Verify content quality."""
        issues = []
        
        # Check for basic quality issues
        issues.extend(self._check_grammar(content))
        issues.extend(self._check_readability(content))
        issues.extend(self._check_structure(content))
        
        # Calculate score
        base_score = 1.0
        if issues:
            penalty = sum(
                0.05 if i.severity == "low" else
                0.10 if i.severity == "medium" else
                0.20 if i.severity == "high" else 0.30
                for i in issues
            )
            base_score = max(0.0, base_score - penalty)
        
        passed = base_score >= self.min_score
        
        return VerificationResult(
            check_name=self.name,
            passed=passed,
            score=base_score,
            issues=issues,
        )
    
    def _check_grammar(self, content: str) -> List[VerificationIssue]:
        """Check for common grammar issues."""
        issues = []
        
        # Check for double spaces
        if "  " in content:
            issues.append(VerificationIssue(
                issue_type="grammar",
                severity="low",
                description="Multiple consecutive spaces found",
                suggestion="Remove extra spaces",
            ))
        
        # Check for missing punctuation at end of sentences
        sentences = content.split(".")
        for i, sentence in enumerate(sentences[:-1]):
            if sentence.strip() and not sentence.strip()[-1] in ".!?":
                issues.append(VerificationIssue(
                    issue_type="grammar",
                    severity="medium",
                    description=f"Sentence may be missing punctuation",
                    location=f"Sentence {i+1}",
                ))
        
        return issues
    
    def _check_readability(self, content: str) -> List[VerificationIssue]:
        """Check content readability."""
        issues = []
        
        # Check average sentence length
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        if sentences:
            avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_words > 30:
                issues.append(VerificationIssue(
                    issue_type="readability",
                    severity="medium",
                    description="Average sentence length is high (may reduce readability)",
                    suggestion="Consider breaking long sentences into shorter ones",
                    metadata={"average_words_per_sentence": avg_words},
                ))
        
        # Check paragraph length
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        for i, para in enumerate(paragraphs):
            word_count = len(para.split())
            if word_count > 200:
                issues.append(VerificationIssue(
                    issue_type="readability",
                    severity="low",
                    description=f"Paragraph {i+1} is very long",
                    suggestion="Consider breaking into multiple paragraphs",
                    metadata={"word_count": word_count},
                ))
        
        return issues
    
    def _check_structure(self, content: str) -> List[VerificationIssue]:
        """Check document structure."""
        issues = []
        
        # Check for sections/headings
        has_headings = bool(re.search(r'^#+\s', content, re.MULTILINE))
        if not has_headings and len(content) > 1000:
            issues.append(VerificationIssue(
                issue_type="structure",
                severity="medium",
                description="Long document without clear section headings",
                suggestion="Add section headings to improve structure",
            ))
        
        return issues


class FactCheck:
    """
    Fact-checking for document content.
    
    Verifies factual accuracy and identifies claims that need verification.
    """
    
    def __init__(self, min_confidence: float = 0.8):
        self.min_confidence = min_confidence
        self.name = "fact_check"
    
    def verify(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> VerificationResult:
        """Verify factual accuracy."""
        issues = []
        
        # Identify claims that need verification
        issues.extend(self._identify_statistical_claims(content))
        issues.extend(self._check_citations(content))
        issues.extend(self._check_dates(content))
        
        # In production, this would integrate with fact-checking APIs
        # or databases to verify specific claims
        
        score = 1.0 - (len(issues) * 0.1)
        score = max(0.0, score)
        
        passed = score >= self.min_confidence
        
        return VerificationResult(
            check_name=self.name,
            passed=passed,
            score=score,
            issues=issues,
        )
    
    def _identify_statistical_claims(self, content: str) -> List[VerificationIssue]:
        """Identify statistical claims that should be verified."""
        issues = []
        
        # Find percentages
        percentage_pattern = r'\d+\.?\d*\s*%'
        percentages = re.findall(percentage_pattern, content)
        
        if percentages:
            issues.append(VerificationIssue(
                issue_type="fact_check",
                severity="medium",
                description=f"Found {len(percentages)} statistical claim(s)",
                suggestion="Verify statistical claims have proper citations",
                metadata={"claims": percentages[:5]},  # First 5 examples
            ))
        
        return issues
    
    def _check_citations(self, content: str) -> List[VerificationIssue]:
        """Check for proper citations."""
        issues = []
        
        # Look for citation patterns [1], (Author, Year), etc.
        citation_patterns = [
            r'\[\d+\]',
            r'\([A-Z][a-z]+,?\s+\d{4}\)',
            r'\([A-Z][a-z]+\s+et\s+al\.?,?\s+\d{4}\)',
        ]
        
        has_citations = any(
            re.search(pattern, content)
            for pattern in citation_patterns
        )
        
        # Check if document makes claims but has no citations
        claim_indicators = [
            "research shows",
            "studies indicate",
            "according to",
            "evidence suggests",
        ]
        
        has_claim_indicators = any(
            indicator in content.lower()
            for indicator in claim_indicators
        )
        
        if has_claim_indicators and not has_citations:
            issues.append(VerificationIssue(
                issue_type="fact_check",
                severity="high",
                description="Document makes claims but lacks citations",
                suggestion="Add proper citations for all claims",
            ))
        
        return issues
    
    def _check_dates(self, content: str) -> List[VerificationIssue]:
        """Check date formats and reasonableness."""
        issues = []
        
        # Find year mentions
        year_pattern = r'\b(19|20)\d{2}\b'
        years = [int(y) for y in re.findall(year_pattern, content)]
        
        current_year = datetime.now().year
        future_years = [y for y in years if y > current_year]
        
        if future_years:
            issues.append(VerificationIssue(
                issue_type="fact_check",
                severity="high",
                description="Document contains future dates",
                suggestion="Verify dates are correct",
                metadata={"future_years": future_years},
            ))
        
        return issues


class ConsistencyCheck:
    """
    Consistency check for document content.
    
    Ensures terminology, style, and formatting are consistent throughout.
    """
    
    def __init__(self, min_score: float = 0.85):
        self.min_score = min_score
        self.name = "consistency_check"
    
    def verify(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> VerificationResult:
        """Verify content consistency."""
        issues = []
        
        issues.extend(self._check_terminology(content))
        issues.extend(self._check_formatting(content))
        issues.extend(self._check_tone(content))
        
        score = 1.0 - (len(issues) * 0.08)
        score = max(0.0, score)
        
        passed = score >= self.min_score
        
        return VerificationResult(
            check_name=self.name,
            passed=passed,
            score=score,
            issues=issues,
        )
    
    def _check_terminology(self, content: str) -> List[VerificationIssue]:
        """Check for consistent terminology."""
        issues = []
        
        # Check for mixed spelling variants
        variants = [
            (["analyze", "analyse"], "US vs UK spelling"),
            (["organization", "organisation"], "US vs UK spelling"),
            (["color", "colour"], "US vs UK spelling"),
        ]
        
        for words, description in variants:
            found = [w for w in words if w in content.lower()]
            if len(found) > 1:
                issues.append(VerificationIssue(
                    issue_type="consistency",
                    severity="low",
                    description=f"Mixed spelling variants: {', '.join(found)}",
                    suggestion=f"Use consistent spelling ({description})",
                ))
        
        return issues
    
    def _check_formatting(self, content: str) -> List[VerificationIssue]:
        """Check for consistent formatting."""
        issues = []
        
        # Check heading format consistency
        heading_styles = []
        for match in re.finditer(r'^(#+)\s+(.+)$', content, re.MULTILINE):
            heading_styles.append(len(match.group(1)))
        
        # Check if headings skip levels (e.g., # followed by ###)
        for i in range(len(heading_styles) - 1):
            if heading_styles[i+1] - heading_styles[i] > 1:
                issues.append(VerificationIssue(
                    issue_type="consistency",
                    severity="low",
                    description="Heading levels skip intermediate levels",
                    suggestion="Use consistent heading hierarchy",
                ))
                break
        
        return issues
    
    def _check_tone(self, content: str) -> List[VerificationIssue]:
        """Check for consistent tone."""
        issues = []
        
        # Check for mixed person (first vs third)
        first_person = len(re.findall(r'\b(I|we|our|us)\b', content, re.IGNORECASE))
        third_person = len(re.findall(r'\b(they|their|them|one)\b', content, re.IGNORECASE))
        
        if first_person > 5 and third_person > 5:
            issues.append(VerificationIssue(
                issue_type="consistency",
                severity="medium",
                description="Mixed use of first and third person",
                suggestion="Maintain consistent point of view",
            ))
        
        return issues


class VerificationSystem:
    """
    Comprehensive verification system for document validation.
    
    Combines multiple verification checks to ensure document quality,
    accuracy, and consistency.
    """
    
    def __init__(
        self,
        checks: Optional[List[str]] = None,
        min_overall_score: float = 0.8,
    ):
        self.min_overall_score = min_overall_score
        
        # Initialize verification checks
        self.quality_check = QualityCheck()
        self.fact_check = FactCheck()
        self.consistency_check = ConsistencyCheck()
        
        # Configure enabled checks
        available_checks = {
            "quality": self.quality_check,
            "factual_accuracy": self.fact_check,
            "consistency": self.consistency_check,
            "grammar": self.quality_check,
            "style": self.quality_check,
            "citations": self.fact_check,
            "completeness": self.quality_check,
        }
        
        if checks:
            self.enabled_checks = [
                available_checks[check]
                for check in checks
                if check in available_checks
            ]
        else:
            self.enabled_checks = list(set(available_checks.values()))
        
        logger.info(f"Verification system initialized with {len(self.enabled_checks)} checks")
    
    def verify(self, document) -> VerificationResult:
        """
        Verify a document against all enabled checks.
        
        Args:
            document: Document object to verify
            
        Returns:
            Aggregated VerificationResult
        """
        logger.info(f"Starting verification for document: {document.document_id}")
        
        all_issues = []
        check_scores = []
        
        # Run all enabled checks
        for check in self.enabled_checks:
            result = check.verify(document.content, document.metadata)
            all_issues.extend(result.issues)
            check_scores.append(result.score)
            
            logger.debug(f"{result.check_name}: score={result.score}, issues={len(result.issues)}")
        
        # Calculate overall score
        overall_score = sum(check_scores) / len(check_scores) if check_scores else 0.0
        passed = overall_score >= self.min_overall_score and len(
            [i for i in all_issues if i.severity == "critical"]
        ) == 0
        
        result = VerificationResult(
            check_name="overall",
            passed=passed,
            score=overall_score,
            issues=all_issues,
            metadata={
                "checks_run": len(self.enabled_checks),
                "individual_scores": check_scores,
            },
        )
        
        logger.info(
            f"Verification complete: score={overall_score:.2f}, "
            f"passed={passed}, issues={len(all_issues)}"
        )
        
        return result
    
    def get_verification_report(self, result: VerificationResult) -> str:
        """Generate a human-readable verification report."""
        report = []
        report.append("=" * 60)
        report.append("VERIFICATION REPORT")
        report.append("=" * 60)
        report.append(f"Overall Score: {result.score:.2f}")
        report.append(f"Status: {'PASSED' if result.passed else 'FAILED'}")
        report.append(f"Timestamp: {result.timestamp}")
        report.append("")
        
        if result.issues:
            report.append(f"Issues Found: {len(result.issues)}")
            report.append("-" * 60)
            
            # Group issues by severity
            by_severity = {}
            for issue in result.issues:
                by_severity.setdefault(issue.severity, []).append(issue)
            
            for severity in ["critical", "high", "medium", "low"]:
                if severity in by_severity:
                    report.append(f"\n{severity.upper()} Severity:")
                    for issue in by_severity[severity]:
                        report.append(f"  - {issue.description}")
                        if issue.suggestion:
                            report.append(f"    Suggestion: {issue.suggestion}")
        else:
            report.append("No issues found!")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)