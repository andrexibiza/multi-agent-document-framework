"""Editing agent implementation."""

from .base import BaseAgent
from ..models.task import Task, TaskResult
from ..utils.config import AgentConfig
from typing import Dict


class EditingAgent(BaseAgent):
    """
    Agent specialized in content editing and refinement.
    
    Capabilities:
    - Grammar and style correction
    - Consistency enforcement
    - Readability enhancement
    - Structure optimization
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize editing agent.
        
        Args:
            config: Agent configuration
        """
        super().__init__(config)
        self.specialization = "editing"
    
    async def process(self, task: Task) -> TaskResult:
        """
        Execute editing task.
        
        Performs multi-pass editing:
        1. Structural and flow improvements
        2. Grammar and style corrections
        3. Consistency and clarity enhancements
        
        Args:
            task: Editing task
            
        Returns:
            Edited content
        """
        content = task.data.get('content')
        style_guide = task.data.get('style_guide', {})
        
        # Pass 1: Structure and flow
        content = await self._edit_structure(content, style_guide)
        
        # Pass 2: Grammar and style
        content = await self._edit_grammar_style(content, style_guide)
        
        # Pass 3: Consistency and polish
        content = await self._final_polish(content, style_guide)
        
        return TaskResult(
            task_id=task.id,
            success=True,
            data={'edited_content': content}
        )
    
    async def _edit_structure(self, content: str, style_guide: Dict) -> str:
        """Improve structure and flow."""
        prompt = f"""Improve the structure and flow of this content:

{content}

Focus on:
1. Logical organization of ideas
2. Smooth transitions between paragraphs
3. Clear progression of arguments
4. Effective use of headers and sections
5. Balanced paragraph lengths

Return the improved content maintaining all key information."""
        
        return await self.llm_client.generate(
            prompt=prompt,
            temperature=0.5,
            system_message="You are an expert editor improving content structure."
        )
    
    async def _edit_grammar_style(self, content: str, style_guide: Dict) -> str:
        """Correct grammar and refine style."""
        prompt = f"""Edit this content for grammar and style:

{content}

Focus on:
1. Grammar and punctuation corrections
2. Sentence structure improvements
3. Word choice and vocabulary
4. Tone consistency
5. Active voice preference

Return the corrected content."""
        
        return await self.llm_client.generate(
            prompt=prompt,
            temperature=0.3,
            system_message="You are an expert copy editor."
        )
    
    async def _final_polish(self, content: str, style_guide: Dict) -> str:
        """Final polish for consistency and clarity."""
        prompt = f"""Perform final polishing on this content:

{content}

Focus on:
1. Consistency in terminology and style
2. Clarity and conciseness
3. Removing redundancy
4. Enhancing readability
5. Professional presentation

Return the polished final version."""
        
        return await self.llm_client.generate(
            prompt=prompt,
            temperature=0.4,
            system_message="You are an expert editor performing final review."
        )