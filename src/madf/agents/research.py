"""Research agent implementation."""

from typing import List, Dict, Any
import json
from datetime import datetime

from .base import BaseAgent
from ..models.task import Task, TaskResult
from ..utils.config import AgentConfig


class ResearchAgent(BaseAgent):
    """
    Agent specialized in information gathering and research.
    
    Capabilities:
    - Information retrieval and extraction
    - Source validation
    - Fact verification
    - Data structuring
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize research agent.
        
        Args:
            config: Agent configuration
        """
        super().__init__(config)
        self.specialization = "research"
    
    async def process(self, task: Task) -> TaskResult:
        """
        Execute research task.
        
        Task data should contain:
        - query: Main research question
        - depth: Research depth (shallow, moderate, deep)
        - sources: Optional list of preferred sources
        
        Args:
            task: Research task
            
        Returns:
            Research results
        """
        query = task.data.get('query')
        depth = task.data.get('depth', 'moderate')
        
        self.logger.info(f"Researching: {query}")
        
        # Step 1: Break down the research query
        sub_queries = await self._decompose_query(query)
        
        # Step 2: Research each sub-query
        research_results = []
        for sq in sub_queries:
            result = await self._research_query(sq, depth)
            research_results.append(result)
        
        # Step 3: Synthesize findings
        synthesis = await self._synthesize_findings(research_results)
        
        # Step 4: Validate and structure
        structured_data = await self._structure_research(synthesis)
        
        return TaskResult(
            task_id=task.id,
            success=True,
            data={
                'research_brief': structured_data,
                'sub_queries': sub_queries,
                'sources': self._extract_sources(research_results)
            }
        )
    
    async def _decompose_query(self, query: str) -> List[str]:
        """Break down main query into sub-queries."""
        prompt = f"""Break down this research query into 3-5 specific sub-questions that need to be answered:

Main Query: {query}

Provide the sub-questions as a JSON array of strings."""
        
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.3,
            system_message="You are a research planning assistant."
        )
        
        # Parse JSON response
        try:
            sub_queries = json.loads(response)
            return sub_queries if isinstance(sub_queries, list) else [query]
        except:
            # Fallback to main query if parsing fails
            return [query]
    
    async def _research_query(self, query: str, depth: str) -> Dict[str, Any]:
        """Research a specific query."""
        prompt = f"""Provide comprehensive research on the following question:

{query}

Depth level: {depth}

Include:
1. Key facts and findings
2. Important context and background
3. Relevant statistics or data
4. Notable perspectives or theories
5. Recent developments

Format your response with clear sections."""
        
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.4,
            system_message="You are an expert researcher providing accurate, well-sourced information."
        )
        
        return {
            'query': query,
            'findings': response
        }
    
    async def _synthesize_findings(self, results: List[Dict]) -> str:
        """Synthesize multiple research results into coherent brief."""
        combined_findings = "\n\n".join([r['findings'] for r in results])
        
        prompt = f"""Synthesize the following research findings into a coherent research brief:

{combined_findings}

Provide:
1. Executive summary
2. Key findings organized by theme
3. Important insights and patterns
4. Gaps or areas needing more research"""
        
        synthesis = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.5,
            system_message="You are a research analyst synthesizing findings."
        )
        
        return synthesis
    
    async def _structure_research(self, synthesis: str) -> Dict[str, Any]:
        """Structure research into standardized format."""
        return {
            'synthesis': synthesis,
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_sources(self, results: List[Dict]) -> List[str]:
        """Extract cited sources from research results."""
        # Implementation to extract and deduplicate sources
        # For now, return empty list
        return []