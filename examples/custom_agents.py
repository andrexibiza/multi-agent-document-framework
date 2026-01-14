"""
Example of creating custom agents for specialized tasks.

This example shows how to:
1. Create a custom agent class
2. Integrate it with the framework
3. Use it in a workflow
"""

import asyncio
import json
from typing import Dict, Any, List

from madf.agents.base import BaseAgent
from madf.models import Task, Result
from madf import DocumentOrchestrator, OrchestratorConfig


class CitationAgent(BaseAgent):
    """
    Custom agent that formats and validates citations.
    """
    
    def __init__(self, model: str = "gpt-4", config: Dict[str, Any] = None):
        super().__init__(name="citation", model=model, config=config)
        self.citation_style = config.get('citation_style', 'APA') if config else 'APA'
    
    async def process(self, task: Task) -> Result:
        """
        Process citation task.
        
        Expected payload:
        {
            "sources": List[Dict],  # List of source metadata
            "style": str  # Citation style (APA, MLA, Chicago, etc.)
        }
        """
        sources = task.payload.get('sources', [])
        style = task.payload.get('style', self.citation_style)
        
        # Generate citations
        citations = await self._generate_citations(sources, style)
        
        # Validate citations
        validation = await self._validate_citations(citations)
        
        return Result(
            task_id=task.task_id,
            success=True,
            output={
                'citations': citations,
                'bibliography': self._create_bibliography(citations),
                'validation': validation
            },
            metadata={
                'citation_count': len(citations),
                'style': style
            },
            metrics={
                'tokens_used': self.llm.get_token_count()
            }
        )
    
    async def _generate_citations(self, sources: List[Dict], style: str) -> List[Dict]:
        """Generate formatted citations"""
        prompt = f"""
Generate {style} style citations for the following sources.

Sources:
{json.dumps(sources, indent=2)}

For each source, provide:
1. In-text citation format
2. Bibliography entry
3. Source type

Return as JSON array.
"""
        
        response = await self.llm.generate(prompt)
        citations = json.loads(response)
        return citations
    
    async def _validate_citations(self, citations: List[Dict]) -> Dict:
        """Validate citation format"""
        prompt = f"""
Validate these citations for correctness and completeness.

Citations:
{json.dumps(citations, indent=2)}

Check for:
1. Required elements present
2. Proper formatting
3. Consistency

Return validation report as JSON:
{{
    "valid": bool,
    "issues": [str],
    "score": float (0-1)
}}
"""
        
        response = await self.llm.generate(prompt)
        validation = json.loads(response)
        return validation
    
    def _create_bibliography(self, citations: List[Dict]) -> str:
        """Create formatted bibliography"""
        entries = [c.get('bibliography', '') for c in citations]
        return "\n".join(sorted(entries))


class SEOAgent(BaseAgent):
    """
    Custom agent that optimizes content for search engines.
    """
    
    def __init__(self, model: str = "gpt-4", config: Dict[str, Any] = None):
        super().__init__(name="seo", model=model, config=config)
    
    async def process(self, task: Task) -> Result:
        """
        Process SEO optimization task.
        """
        content = task.payload.get('content', '')
        target_keywords = task.payload.get('keywords', [])
        
        # Analyze SEO
        analysis = await self._analyze_seo(content, target_keywords)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(analysis)
        
        # Optionally apply optimizations
        optimized_content = content
        if task.payload.get('apply_optimizations', False):
            optimized_content = await self._optimize_content(
                content,
                recommendations
            )
        
        return Result(
            task_id=task.task_id,
            success=True,
            output={
                'analysis': analysis,
                'recommendations': recommendations,
                'optimized_content': optimized_content
            },
            metadata={
                'seo_score': analysis.get('score', 0.0),
                'keywords_found': len(analysis.get('keywords_found', []))
            },
            metrics={
                'tokens_used': self.llm.get_token_count()
            }
        )
    
    async def _analyze_seo(self, content: str, keywords: List[str]) -> Dict:
        """Analyze content for SEO"""
        prompt = f"""
Analyze this content for SEO optimization.

Content:
{content[:1000]}...

Target Keywords: {', '.join(keywords)}

Provide:
1. Keyword density analysis
2. Heading structure evaluation
3. Meta description suggestions
4. Internal linking opportunities
5. Overall SEO score (0-1)

Return as JSON.
"""
        
        response = await self.llm.generate(prompt)
        analysis = json.loads(response)
        return analysis
    
    async def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate SEO improvement recommendations"""
        prompt = f"""
Based on this SEO analysis, provide actionable recommendations.

Analysis:
{json.dumps(analysis, indent=2)}

Provide 5-10 specific recommendations with:
- Priority (high/medium/low)
- Category (keywords, structure, metadata, etc.)
- Action to take
- Expected impact

Return as JSON array.
"""
        
        response = await self.llm.generate(prompt)
        recommendations = json.loads(response)
        return recommendations
    
    async def _optimize_content(self, content: str, recommendations: List[Dict]) -> str:
        """Apply SEO optimizations to content"""
        high_priority = [r for r in recommendations if r.get('priority') == 'high']
        
        prompt = f"""
Optimize this content based on these recommendations.

Content:
{content}

Recommendations:
{json.dumps(high_priority, indent=2)}

Apply improvements while maintaining quality and readability.
Return the optimized content.
"""
        
        optimized = await self.llm.generate(prompt)
        return optimized


async def main():
    """
    Example using custom agents.
    """
    print("Custom Agents Example\n" + "="*50)
    
    # Create custom agents
    citation_agent = CitationAgent(
        model="gpt-4",
        config={'citation_style': 'APA'}
    )
    
    seo_agent = SEOAgent(
        model="gpt-4",
        config={}
    )
    
    # Create standard agents
    from madf import ResearchAgent, WritingAgent, EditingAgent, VerificationAgent
    
    research_agent = ResearchAgent(model="gpt-4")
    writing_agent = WritingAgent(model="gpt-4")
    editing_agent = EditingAgent(model="gpt-4")
    verification_agent = VerificationAgent(model="gpt-4")
    
    # Create orchestrator with custom agents
    orchestrator = DocumentOrchestrator(
        agents={
            'research': research_agent,
            'writing': writing_agent,
            'editing': editing_agent,
            'verification': verification_agent,
            'citation': citation_agent,  # Custom agent
            'seo': seo_agent  # Custom agent
        },
        config=OrchestratorConfig()
    )
    
    print("\n✓ Custom agents integrated successfully")
    
    # Generate document
    result = await orchestrator.create_document(
        topic="The Future of Renewable Energy",
        requirements={
            "length": "1500 words",
            "tone": "informative",
            "include_citations": True,
            "optimize_seo": True,
            "target_keywords": ["renewable energy", "solar power", "sustainability"]
        }
    )
    
    if result.success:
        print(f"\n✓ Document generated successfully")
        print(f"  Quality Score: {result.quality_score}")
        print(f"  Iterations: {result.iterations}")
    
    # Test citation agent directly
    print("\n" + "="*50)
    print("Testing Citation Agent...")
    
    citation_task = Task(
        task_id="citation_test",
        task_type="citation",
        payload={
            'sources': [
                {
                    'type': 'journal',
                    'authors': ['Smith, J.', 'Doe, A.'],
                    'title': 'Advances in Solar Technology',
                    'journal': 'Renewable Energy Journal',
                    'year': 2023,
                    'volume': 45,
                    'pages': '120-135'
                }
            ],
            'style': 'APA'
        },
        context={}
    )
    
    citation_result = await citation_agent.handle_task(citation_task)
    print(f"\n✓ Citations generated:")
    print(citation_result.output['bibliography'])
    
    # Test SEO agent directly
    print("\n" + "="*50)
    print("Testing SEO Agent...")
    
    seo_task = Task(
        task_id="seo_test",
        task_type="seo",
        payload={
            'content': result.content if result.success else "Sample content about renewable energy...",
            'keywords': ['renewable energy', 'solar power', 'sustainability'],
            'apply_optimizations': False
        },
        context={}
    )
    
    seo_result = await seo_agent.handle_task(seo_task)
    print(f"\n✓ SEO Score: {seo_result.metadata['seo_score']}")
    print(f"✓ Recommendations: {len(seo_result.output['recommendations'])}")
    
    # Cleanup
    await orchestrator.shutdown()
    print("\n✓ Complete")


if __name__ == "__main__":
    asyncio.run(main())
