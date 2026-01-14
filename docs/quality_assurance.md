# Quality Assurance Systems

## Overview

The Multi-Agent Document Framework implements comprehensive quality assurance through multi-layer verification, automated scoring, and iterative refinement processes.

## Quality Dimensions

### 1. Structural Quality (20% weight)

**What it measures**: Document organization and completeness

#### Checks
- ✓ All required sections present
- ✓ Logical section ordering
- ✓ Appropriate section lengths
- ✓ Proper heading hierarchy
- ✓ Format compliance

#### Scoring Algorithm

```python
def calculate_structural_score(document, requirements):
    checks = [
        check_required_sections(document, requirements),
        check_section_ordering(document),
        check_section_balance(document),
        check_heading_hierarchy(document),
        check_format_compliance(document)
    ]
    return sum(checks) / len(checks)
```

### 2. Content Quality (30% weight)

**What it measures**: Writing quality and presentation

#### Dimensions
- **Coherence**: Logical flow and consistency
- **Clarity**: Easy to understand
- **Readability**: Appropriate complexity
- **Engagement**: Interesting and compelling
- **Professional Presentation**: Polished and refined

#### Readability Metrics

```python
def calculate_readability(text):
    # Flesch Reading Ease
    fre = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    
    # Flesch-Kincaid Grade Level
    fkgl = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
    
    # Combined score
    return normalize_readability(fre, fkgl, target_audience)
```

### 3. Factual Accuracy (30% weight)

**What it measures**: Correctness and reliability

#### Verification Process

```
1. Extract Claims
   ↓
2. Cross-reference with Research
   ↓
3. Identify Unsupported Statements
   ↓
4. Check for Contradictions
   ↓
5. Calculate Accuracy Score
```

#### Claim Verification

```python
class ClaimVerifier:
    async def verify_claim(self, claim, research_brief):
        # Check if claim is supported by research
        support_level = await self._check_support(claim, research_brief)
        
        return {
            'claim': claim,
            'status': support_level,  # verified, uncertain, contradicted
            'confidence': float,  # 0-1
            'sources': List[str]
        }
```

### 4. Completeness (20% weight)

**What it measures**: Requirement fulfillment

#### Checks
- ✓ All topics covered
- ✓ Target length achieved (±10%)
- ✓ Appropriate depth
- ✓ All requirements addressed
- ✓ No critical gaps

#### Gap Analysis

```python
def identify_gaps(document, requirements):
    gaps = []
    
    # Check topic coverage
    required_topics = extract_topics(requirements)
    covered_topics = extract_topics(document)
    missing_topics = set(required_topics) - set(covered_topics)
    
    if missing_topics:
        gaps.append({
            'type': 'missing_topics',
            'items': list(missing_topics)
        })
    
    # Check length
    target = requirements['target_length']
    actual = document.word_count
    if abs(actual - target) / target > 0.1:
        gaps.append({
            'type': 'length',
            'expected': target,
            'actual': actual
        })
    
    return gaps
```

## Quality Scoring

### Overall Score Calculation

```python
def calculate_quality_score(document, requirements, research_brief):
    """Calculate weighted overall quality score."""
    
    # Calculate component scores
    structural = calculate_structural_score(document, requirements)
    content = calculate_content_score(document)
    accuracy = calculate_accuracy_score(document, research_brief)
    completeness = calculate_completeness_score(document, requirements)
    
    # Apply weights
    weights = {
        'structural': 0.20,
        'content': 0.30,
        'accuracy': 0.30,
        'completeness': 0.20
    }
    
    overall = (
        structural * weights['structural'] +
        content * weights['content'] +
        accuracy * weights['accuracy'] +
        completeness * weights['completeness']
    )
    
    return round(overall, 3)
```

### Score Interpretation

| Score Range | Quality Level | Action |
|------------|---------------|--------|
| 0.90 - 1.00 | Excellent | Accept |
| 0.85 - 0.89 | Good | Accept |
| 0.75 - 0.84 | Fair | Review/Refine |
| 0.60 - 0.74 | Poor | Significant Revision |
| 0.00 - 0.59 | Unacceptable | Regenerate |

## Automated Quality Checks

### Pre-Verification Checks

Run before verification agent:

```python
class PreVerificationChecker:
    def check_document(self, document):
        checks = [
            self.check_minimum_length(document),
            self.check_section_presence(document),
            self.check_formatting(document),
            self.check_structure(document)
        ]
        return all(checks)
```

### Post-Generation Validation

Run after document generation:

```python
class PostGenerationValidator:
    def validate(self, document, request):
        validations = [
            self.validate_content_completeness(document),
            self.validate_style_consistency(document),
            self.validate_length_target(document, request),
            self.validate_section_balance(document)
        ]
        return ValidationReport(validations)
```

## Iterative Refinement

### Quality-Based Iteration

```python
async def create_document_with_refinement(request, max_iterations=3):
    """Create document with iterative quality improvement."""
    
    for iteration in range(max_iterations):
        # Generate document
        document = await generate_document(request)
        
        # Verify quality
        quality_score = await verify_quality(document)
        
        # Check if meets threshold
        if quality_score >= threshold:
            return document
        
        # Refine based on feedback
        feedback = await generate_feedback(document, quality_score)
        request = update_request_with_feedback(request, feedback)
    
    # Return best attempt
    return document
```

### Feedback Loop

```
Generate → Verify → Feedback → Refine → Generate
    ↑                                        ↓
    └──────── If Quality < Threshold ────┘
```

## Quality Reports

### Comprehensive Quality Report

```python
@dataclass
class QualityReport:
    overall_score: float
    passed: bool
    
    structural: StructuralScore
    content: ContentScore
    accuracy: AccuracyScore
    completeness: CompletenessScore
    
    issues: List[Issue]
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'overall_score': self.overall_score,
            'passed': self.passed,
            'dimensions': {
                'structural': self.structural.score,
                'content': self.content.score,
                'accuracy': self.accuracy.score,
                'completeness': self.completeness.score
            },
            'issues': [issue.to_dict() for issue in self.issues],
            'recommendations': self.recommendations
        }
```

### Issue Tracking

```python
@dataclass
class Issue:
    type: str  # grammar, accuracy, structure, completeness
    severity: str  # critical, major, minor
    location: str  # section or line reference
    description: str
    suggestion: str
    
    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'severity': self.severity,
            'location': self.location,
            'description': self.description,
            'suggestion': self.suggestion
        }
```

## Quality Thresholds

### Configuration

```yaml
quality:
  overall_threshold: 0.85
  
  dimension_thresholds:
    structural: 0.80
    content: 0.85
    accuracy: 0.90  # Highest requirement
    completeness: 0.80
  
  severity_limits:
    critical_issues: 0  # No critical issues allowed
    major_issues: 2
    minor_issues: 10
```

### Enforcement

```python
def check_quality_thresholds(report, thresholds):
    """Check if report meets all quality thresholds."""
    
    # Overall threshold
    if report.overall_score < thresholds['overall']:
        return False, "Overall score below threshold"
    
    # Dimension thresholds
    for dimension in ['structural', 'content', 'accuracy', 'completeness']:
        score = getattr(report, dimension).score
        if score < thresholds['dimension_thresholds'][dimension]:
            return False, f"{dimension} score below threshold"
    
    # Issue limits
    critical = len([i for i in report.issues if i.severity == 'critical'])
    if critical > thresholds['severity_limits']['critical_issues']:
        return False, f"Too many critical issues: {critical}"
    
    return True, "All thresholds met"
```

## Continuous Quality Monitoring

### Metrics Collection

```python
class QualityMetricsCollector:
    def __init__(self):
        self.metrics = {
            'documents_generated': 0,
            'quality_scores': [],
            'issues_by_type': defaultdict(int),
            'refinement_iterations': []
        }
    
    def record_document(self, document, quality_report):
        self.metrics['documents_generated'] += 1
        self.metrics['quality_scores'].append(quality_report.overall_score)
        
        for issue in quality_report.issues:
            self.metrics['issues_by_type'][issue.type] += 1
    
    def get_statistics(self):
        return {
            'total_documents': self.metrics['documents_generated'],
            'average_quality': statistics.mean(self.metrics['quality_scores']),
            'quality_std_dev': statistics.stdev(self.metrics['quality_scores']),
            'common_issues': sorted(
                self.metrics['issues_by_type'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
```

## Best Practices

### 1. Set Appropriate Thresholds

- **High-stakes documents**: 0.90+ overall
- **Standard documents**: 0.85+ overall
- **Draft documents**: 0.75+ overall

### 2. Balance Weights

Adjust dimension weights based on document type:

```python
# Academic paper
weights = {'structural': 0.15, 'content': 0.25, 'accuracy': 0.45, 'completeness': 0.15}

# Marketing content
weights = {'structural': 0.20, 'content': 0.45, 'accuracy': 0.20, 'completeness': 0.15}

# Technical documentation
weights = {'structural': 0.25, 'content': 0.25, 'accuracy': 0.35, 'completeness': 0.15}
```

### 3. Implement Graceful Degradation

```python
if quality_score < threshold:
    if quality_score >= fallback_threshold:
        # Accept with warning
        logger.warning(f"Quality {quality_score} below threshold but acceptable")
        return document
    else:
        # Reject and retry
        raise QualityThresholdError(f"Quality {quality_score} too low")
```

### 4. Provide Actionable Feedback

Generate specific improvement suggestions:

```python
def generate_feedback(document, quality_report):
    feedback = []
    
    if quality_report.accuracy.score < 0.85:
        feedback.append("Verify all factual claims against sources")
    
    if quality_report.completeness.score < 0.80:
        feedback.append(f"Address missing topics: {', '.join(quality_report.completeness.gaps)}")
    
    return feedback
```

---

**See Also**:
- [Architecture](architecture.md)
- [Agent Design](agents.md)
- [API Reference](api_reference.md)