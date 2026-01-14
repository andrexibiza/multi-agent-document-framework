# Verification System

## Overview

The verification system ensures that generated documents meet quality standards through multi-dimensional assessment and fact-checking. It acts as the final quality gate before document finalization.

## Components

### 1. Quality Checker

Assesses overall document quality across multiple dimensions.

#### Quality Dimensions

**Coherence (25% weight)**
- Logical flow and organization
- Section transitions
- Argument structure
- Internal consistency

**Completeness (25% weight)**
- Requirements fulfillment
- Topic coverage
- Depth appropriateness
- Missing elements

**Accuracy (25% weight)**
- Factual correctness
- Source alignment
- Claim verification
- Data validity

**Clarity (15% weight)**
- Readability
- Sentence structure
- Terminology appropriateness
- Ambiguity absence

**Style (10% weight)**
- Tone consistency
- Voice maintenance
- Format adherence
- Grammar and mechanics

#### Quality Score Calculation

```python
quality_score = (
    0.25 * coherence_score +
    0.25 * completeness_score +
    0.25 * accuracy_score +
    0.15 * clarity_score +
    0.10 * style_score
)
```

### 2. Fact Checker

Verifies factual claims against research sources.

#### Verification Process

```
1. Claim Extraction
   ↓
   - Identify factual statements
   - Separate opinions from facts
   - Categorize claim types
   ↓
2. Source Matching
   ↓
   - Match claims to sources
   - Check citation presence
   - Verify source credibility
   ↓
3. Confidence Scoring
   ↓
   - Verified (0.9-1.0): Multiple authoritative sources
   - Supported (0.7-0.9): One reliable source
   - Plausible (0.5-0.7): Consistent with knowledge
   - Uncertain (0.3-0.5): Insufficient evidence
   - Contradicted (0-0.3): Conflicts with sources
   ↓
4. Issue Flagging
   ↓
   - Unsupported claims
   - Contradictory information
   - Missing citations
   - Outdated information
```

#### Implementation

```python
class FactChecker:
    """
    Fact verification system.
    """
    
    async def verify_document(self,
                             document: str,
                             sources: List[Dict]) -> Dict:
        """
        Verify all facts in document.
        """
        # Extract claims
        claims = await self.extract_claims(document)
        
        # Verify each claim
        verifications = []
        for claim in claims:
            verification = await self.verify_claim(
                claim,
                sources
            )
            verifications.append(verification)
        
        # Calculate overall confidence
        confidence = self.calculate_confidence(verifications)
        
        # Identify issues
        issues = self.find_issues(verifications)
        
        return {
            'verified_claims': len([v for v in verifications if v['status'] == 'verified']),
            'unsupported_claims': len([v for v in verifications if v['status'] == 'uncertain']),
            'confidence_score': confidence,
            'issues': issues,
            'details': verifications
        }
    
    async def extract_claims(self, document: str) -> List[str]:
        """
        Extract factual claims from document.
        """
        prompt = f"""
Extract all factual claims from this document.

Document:
{document}

For each claim:
- Identify the statement
- Classify as factual vs opinion
- Note the location in document

Return only factual claims as JSON array.
"""
        
        response = await self.llm.generate(prompt)
        claims = json.loads(response)
        return claims
    
    async def verify_claim(self,
                          claim: str,
                          sources: List[Dict]) -> Dict:
        """
        Verify a single claim against sources.
        """
        sources_text = "\n".join([
            f"Source {i+1}: {s.get('title')} - {s.get('content', '')[:200]}"
            for i, s in enumerate(sources)
        ])
        
        prompt = f"""
Verify this claim against the provided sources.

Claim: {claim}

Sources:
{sources_text}

Determine:
1. Is the claim supported by sources?
2. Which sources support it?
3. Confidence level
4. Any contradictions

Return as JSON:
{{
    "claim": str,
    "status": "verified" | "supported" | "uncertain" | "contradicted",
    "confidence": float (0-1),
    "supporting_sources": [int],
    "explanation": str
}}
"""
        
        response = await self.llm.generate(prompt)
        verification = json.loads(response)
        return verification
    
    def calculate_confidence(self, verifications: List[Dict]) -> float:
        """
        Calculate overall confidence score.
        """
        if not verifications:
            return 0.0
        
        total = sum(v['confidence'] for v in verifications)
        return total / len(verifications)
    
    def find_issues(self, verifications: List[Dict]) -> List[Dict]:
        """
        Identify verification issues.
        """
        issues = []
        
        for v in verifications:
            if v['status'] in ['uncertain', 'contradicted']:
                issues.append({
                    'claim': v['claim'],
                    'status': v['status'],
                    'explanation': v['explanation'],
                    'priority': 'high' if v['status'] == 'contradicted' else 'medium'
                })
        
        return issues
```

### 3. Consistency Checker

Ensures internal consistency within the document.

#### Checks Performed

**Terminology Consistency**
```python
async def check_terminology(document: str) -> Dict:
    """
    Check for consistent term usage.
    """
    # Find all technical terms
    terms = extract_technical_terms(document)
    
    # Check for variations
    variations = find_term_variations(terms)
    
    # Suggest standardization
    suggestions = [
        {
            'terms': var['variants'],
            'preferred': var['most_common'],
            'count': var['total_occurrences']
        }
        for var in variations
    ]
    
    return {
        'consistent': len(variations) == 0,
        'issues': len(variations),
        'suggestions': suggestions
    }
```

**Citation Consistency**
```python
async def check_citations(document: str) -> Dict:
    """
    Check citation consistency.
    """
    # Extract all citations
    in_text = extract_in_text_citations(document)
    bibliography = extract_bibliography(document)
    
    # Find missing citations
    missing_from_bib = [
        c for c in in_text 
        if c not in bibliography
    ]
    
    unused_in_bib = [
        c for c in bibliography 
        if c not in in_text
    ]
    
    return {
        'consistent': len(missing_from_bib) == 0 and len(unused_in_bib) == 0,
        'missing_from_bibliography': missing_from_bib,
        'unused_in_bibliography': unused_in_bib
    }
```

**Tone Consistency**
```python
async def check_tone(document: str, target_tone: str) -> Dict:
    """
    Check tone consistency throughout document.
    """
    sections = split_into_sections(document)
    
    # Analyze each section
    analyses = []
    for i, section in enumerate(sections):
        tone_analysis = await analyze_tone(section)
        analyses.append({
            'section': i,
            'detected_tone': tone_analysis['tone'],
            'confidence': tone_analysis['confidence'],
            'matches_target': tone_analysis['tone'] == target_tone
        })
    
    # Find inconsistencies
    inconsistent = [
        a for a in analyses 
        if not a['matches_target']
    ]
    
    return {
        'consistent': len(inconsistent) == 0,
        'target_tone': target_tone,
        'inconsistent_sections': inconsistent,
        'overall_match': len(inconsistent) / len(analyses) < 0.2
    }
```

## Verification Agent Implementation

### Complete Implementation

```python
class VerificationAgent(BaseAgent):
    """
    Agent that performs comprehensive document verification.
    """
    
    def __init__(self, model: str = "gpt-4", config: Dict[str, Any] = None):
        super().__init__(name="verification", model=model, config=config)
        self.fact_checker = FactChecker(model)
        self.quality_checker = QualityChecker(model)
        self.consistency_checker = ConsistencyChecker(model)
    
    async def process(self, task: Task) -> Result:
        """
        Perform complete verification.
        """
        document = task.payload['document']
        research_context = task.payload.get('research_context', {})
        requirements = task.payload['requirements']
        threshold = task.payload.get('quality_threshold', 0.8)
        
        # Run all checks in parallel
        fact_check, quality_check, consistency_check = await asyncio.gather(
            self.fact_checker.verify_document(
                document,
                research_context.get('sources', [])
            ),
            self.quality_checker.assess_quality(
                document,
                requirements
            ),
            self.consistency_checker.check_consistency(
                document,
                requirements
            )
        )
        
        # Calculate scores
        fact_score = fact_check['confidence_score']
        quality_score = quality_check['overall_quality']
        consistency_score = consistency_check['consistency_score']
        
        # Weighted overall score
        overall_score = (
            0.30 * fact_score +
            0.40 * quality_score +
            0.30 * consistency_score
        )
        
        # Generate feedback if needed
        feedback = None
        if overall_score < threshold:
            feedback = await self.generate_feedback(
                fact_check,
                quality_check,
                consistency_check,
                requirements
            )
        
        return Result(
            task_id=task.task_id,
            success=True,
            output={
                'overall_score': overall_score,
                'passes_threshold': overall_score >= threshold,
                'fact_check': fact_check,
                'quality_check': quality_check,
                'consistency_check': consistency_check,
                'feedback': feedback
            },
            metadata={
                'threshold': threshold,
                'checks_performed': 3
            },
            metrics={
                'tokens_used': self.llm.get_token_count()
            }
        )
    
    async def generate_feedback(self,
                               fact_check: Dict,
                               quality_check: Dict,
                               consistency_check: Dict,
                               requirements: Dict) -> Dict:
        """
        Generate actionable feedback for improvement.
        """
        issues = []
        
        # Fact-checking issues
        if fact_check['unsupported_claims'] > 0:
            issues.extend([
                {
                    'category': 'accuracy',
                    'priority': 'high',
                    'issue': issue['claim'],
                    'suggestion': f"Verify or remove: {issue['explanation']}"
                }
                for issue in fact_check['issues']
            ])
        
        # Quality issues
        if quality_check['overall_quality'] < 0.8:
            for dimension, score in quality_check['dimension_scores'].items():
                if score < 0.7:
                    issues.append({
                        'category': 'quality',
                        'priority': 'high' if score < 0.5 else 'medium',
                        'issue': f"Low {dimension} score: {score:.2f}",
                        'suggestion': quality_check['suggestions'].get(dimension, '')
                    })
        
        # Consistency issues
        if not consistency_check['consistent']:
            issues.extend([
                {
                    'category': 'consistency',
                    'priority': 'medium',
                    'issue': issue['description'],
                    'suggestion': issue['fix']
                }
                for issue in consistency_check['issues']
            ])
        
        # Prioritize issues
        high_priority = [i for i in issues if i['priority'] == 'high']
        medium_priority = [i for i in issues if i['priority'] == 'medium']
        
        return {
            'total_issues': len(issues),
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'top_5_improvements': (high_priority + medium_priority)[:5],
            'overall_recommendation': self._generate_recommendation(issues)
        }
    
    def _generate_recommendation(self, issues: List[Dict]) -> str:
        """
        Generate overall improvement recommendation.
        """
        if not issues:
            return "Document meets quality standards."
        
        high_priority_count = len([i for i in issues if i['priority'] == 'high'])
        
        if high_priority_count > 5:
            return "Significant improvements needed. Focus on fact verification and accuracy."
        elif high_priority_count > 0:
            return "Some improvements needed. Address high-priority issues first."
        else:
            return "Minor refinements recommended. Document is near publication quality."
```

## Usage Examples

### Basic Verification

```python
verification_agent = VerificationAgent(model="gpt-4")

task = Task(
    task_id="verify_001",
    task_type="verification",
    payload={
        'document': document_content,
        'research_context': research_data,
        'requirements': {
            'tone': 'professional',
            'include_citations': True
        },
        'quality_threshold': 0.85
    },
    context={}
)

result = await verification_agent.handle_task(task)

if result.output['passes_threshold']:
    print("Document verified successfully")
else:
    print("Improvements needed:")
    for issue in result.output['feedback']['high_priority']:
        print(f"- {issue['issue']}")
```

### Custom Verification Rules

```python
class CustomVerificationAgent(VerificationAgent):
    """
    Agent with custom verification rules.
    """
    
    async def verify_word_count(self, document: str, target: str) -> bool:
        """
        Verify document meets word count requirement.
        """
        word_count = len(document.split())
        
        if '-' in target:
            min_words, max_words = map(int, target.split('-'))
            return min_words <= word_count <= max_words
        else:
            target_words = int(target)
            tolerance = 0.1  # 10% tolerance
            return abs(word_count - target_words) / target_words <= tolerance
    
    async def verify_citations(self, document: str) -> Dict:
        """
        Verify all claims are properly cited.
        """
        claims = await self.extract_claims(document)
        citations = extract_citations(document)
        
        uncited_claims = []
        for claim in claims:
            if not self.has_nearby_citation(claim, citations, document):
                uncited_claims.append(claim)
        
        return {
            'all_cited': len(uncited_claims) == 0,
            'total_claims': len(claims),
            'cited_claims': len(claims) - len(uncited_claims),
            'uncited_claims': uncited_claims
        }
```

## Quality Improvement Loop

### Iterative Refinement

```python
async def iterative_quality_improvement(document: str,
                                       max_iterations: int = 3) -> str:
    """
    Iteratively improve document quality based on verification feedback.
    """
    current_document = document
    iteration = 0
    
    while iteration < max_iterations:
        # Verify current version
        verification = await verification_agent.verify(current_document)
        
        if verification['overall_score'] >= 0.90:
            print(f"Quality threshold met after {iteration} iterations")
            break
        
        # Apply improvements
        feedback = verification['feedback']
        current_document = await apply_improvements(
            current_document,
            feedback
        )
        
        iteration += 1
    
    return current_document
```

## Best Practices

### 1. Verification Strategy
- Run verification after each major edit
- Use appropriate quality thresholds for content type
- Balance strictness with practical constraints
- Prioritize critical issues over minor ones

### 2. Performance Optimization
- Cache verification results
- Run checks in parallel
- Use incremental verification for large documents
- Sample-check very long documents

### 3. Feedback Quality
- Provide specific, actionable feedback
- Include examples and suggestions
- Prioritize issues by impact
- Track improvement over iterations

### 4. Error Handling
- Handle missing sources gracefully
- Provide fallback verification methods
- Log all verification decisions
- Allow manual override when needed

---

The verification system ensures high-quality output through systematic, multi-dimensional assessment and actionable feedback generation.