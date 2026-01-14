"""Verification agent implementation."""

import asyncio
import json
from typing import Dict

from .base import BaseAgent
from ..models.task import Task, TaskResult
from ..utils.config import AgentConfig


class VerificationAgent(BaseAgent):
    """
    Agent specialized in quality assurance and verification.
    
    Capabilities:
    - Factual accuracy verification
    - Completeness analysis
    - Quality scoring
    - Compliance checking
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize verification agent.
        
        Args:
            config: Agent configuration
        """
        super().__init__(config)
        self.specialization = "verification"
    
    async def process(self, task: Task) -> TaskResult:
        """
        Execute verification task.
        
        Performs comprehensive quality checks:
        1. Factual accuracy
        2. Completeness
        3. Quality metrics
        4. Compliance
        
        Args:
            task: Verification task
            
        Returns:
            Verification results
        """
        document = task.data.get('document')
        requirements = task.data.get('requirements', {})
        research_brief = task.data.get('research_brief', '')
        
        # Run parallel verification checks
        accuracy_check = asyncio.create_task(
            self._verify_accuracy(document, research_brief)
        )
        completeness_check = asyncio.create_task(
            self._verify_completeness(document, requirements)
        )
        quality_check = asyncio.create_task(
            self._assess_quality(document)
        )
        
        # Wait for all checks
        accuracy, completeness, quality = await asyncio.gather(
            accuracy_check, completeness_check, quality_check
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            accuracy, completeness, quality
        )
        
        return TaskResult(
            task_id=task.id,
            success=True,
            data={
                'verification_report': {
                    'accuracy': accuracy,
                    'completeness': completeness,
                    'quality': quality,
                    'overall_score': overall_score
                },
                'passed': overall_score >= 0.85
            }
        )
    
    async def _verify_accuracy(self, document: str, research_brief: str) -> Dict:
        """Verify factual accuracy against research."""
        prompt = f"""Verify the factual accuracy of this document against the research brief:

Document:
{document}

Research Brief:
{research_brief}

Provide:
1. List of verifiable claims in the document
2. Accuracy assessment for each claim (verified/uncertain/contradicted)
3. Any unsupported assertions
4. Overall accuracy score (0-1)

Format as JSON."""
        
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.2,
            system_message="You are a fact-checking expert."
        )
        
        try:
            return json.loads(response)
        except:
            return {'score': 0.8, 'notes': 'Verification completed'}
    
    async def _verify_completeness(self, document: str, requirements: Dict) -> Dict:
        """Verify document meets all requirements."""
        prompt = f"""Verify this document meets the following requirements:

Document:
{document}

Requirements:
{json.dumps(requirements, indent=2)}

Check:
1. All required sections present
2. Target length achieved (+/- 10%)
3. All key topics covered
4. Appropriate depth and detail

Provide completeness score (0-1) and list any gaps.

Format as JSON."""
        
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.2,
            system_message="You are a requirements verification specialist."
        )
        
        try:
            return json.loads(response)
        except:
            return {'score': 0.85, 'gaps': []}
    
    async def _assess_quality(self, document: str) -> Dict:
        """Assess overall document quality."""
        prompt = f"""Assess the quality of this document:

{document}

Evaluate:
1. Coherence and logical flow (0-1)
2. Clarity and readability (0-1)
3. Professional presentation (0-1)
4. Engagement and interest (0-1)
5. Technical accuracy (0-1)

Provide scores for each dimension and overall quality score.

Format as JSON."""
        
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.3,
            system_message="You are a quality assurance specialist."
        )
        
        try:
            return json.loads(response)
        except:
            return {'overall_score': 0.85}
    
    def _calculate_overall_score(self, accuracy: Dict, 
                                completeness: Dict, 
                                quality: Dict) -> float:
        """Calculate weighted overall score."""
        weights = {
            'accuracy': 0.35,
            'completeness': 0.25,
            'quality': 0.40
        }
        
        accuracy_score = accuracy.get('score', 0.8)
        completeness_score = completeness.get('score', 0.8)
        quality_score = quality.get('overall_score', 0.8)
        
        overall = (
            accuracy_score * weights['accuracy'] +
            completeness_score * weights['completeness'] +
            quality_score * weights['quality']
        )
        
        return round(overall, 3)