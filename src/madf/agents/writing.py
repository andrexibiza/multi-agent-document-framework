"""Writing agent implementation."""

from typing import List, Dict, Any

from .base import BaseAgent
from ..models.task import Task, TaskResult
from ..utils.config import AgentConfig


class WritingAgent(BaseAgent):
    """
    Agent specialized in content creation and writing.
    
    Capabilities:
    - Content structuring and outlining
    - Section-by-section writing
    - Style adaptation
    - Citation management
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize writing agent.
        
        Args:
            config: Agent configuration
        """
        super().__init__(config)
        self.specialization = "writing"
    
    async def process(self, task: Task) -> TaskResult:
        """
        Execute writing task.
        
        Task types:
        - outline: Create document outline
        - section: Write a specific section
        - full: Write complete document
        
        Args:
            task: Writing task
            
        Returns:
            Writing results
        """
        task_type = task.data.get('type', 'full')
        
        if task_type == 'outline':
            result = await self._create_outline(task.data)
        elif task_type == 'section':
            result = await self._write_section(task.data)
        else:
            result = await self._write_full_document(task.data)
        
        return TaskResult(
            task_id=task.id,
            success=True,
            data=result
        )
    
    async def _create_outline(self, data: Dict) -> Dict:
        """Create document outline from research."""
        research_brief = data.get('research_brief')
        requirements = data.get('requirements', {})
        
        prompt = f"""Create a detailed outline for a {requirements.get('document_type', 'document')} based on this research:

{research_brief}

Requirements:
- Target length: {requirements.get('target_length', 2000)} words
- Style: {requirements.get('style', 'formal')}
- Audience: {requirements.get('audience', 'general')}

Provide a hierarchical outline with:
1. Main sections with descriptions
2. Subsections where appropriate
3. Key points to cover in each section
4. Estimated word count per section"""
        
        outline = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.6,
            system_message="You are an expert content strategist creating document outlines."
        )
        
        return {'outline': outline}
    
    async def _write_section(self, data: Dict) -> Dict:
        """Write a specific document section."""
        section_title = data.get('section_title')
        section_outline = data.get('section_outline')
        context = data.get('context', '')
        style = data.get('style', 'formal')
        
        prompt = f"""Write the following section of a document:

Section: {section_title}

Outline:
{section_outline}

Context from previous sections:
{context}

Style: {style}

Write compelling, well-structured content that:
1. Flows naturally from previous sections
2. Covers all points in the outline
3. Maintains consistent tone and style
4. Engages the target audience
5. Includes smooth transitions"""
        
        content = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.7,
            system_message=f"You are an expert writer creating {style} content."
        )
        
        return {
            'section_title': section_title,
            'content': content
        }
    
    async def _write_full_document(self, data: Dict) -> Dict:
        """Write complete document."""
        # First create outline
        outline_data = await self._create_outline(data)
        
        # Parse outline into sections
        sections = self._parse_outline(outline_data['outline'])
        
        # Write each section
        written_sections = []
        context = ""
        
        for section in sections:
            section_data = {
                **data,
                'section_title': section['title'],
                'section_outline': section['outline'],
                'context': context
            }
            
            section_result = await self._write_section(section_data)
            written_sections.append(section_result)
            
            # Update context for next section
            context += f"\n\n{section_result['content']}"
        
        return {
            'outline': outline_data['outline'],
            'sections': written_sections
        }
    
    def _parse_outline(self, outline: str) -> List[Dict]:
        """Parse outline text into structured sections."""
        sections = []
        current_section = None
        
        for line in outline.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Main sections start with numbers
            if line[0].isdigit() and '.' in line[:3]:
                if current_section:
                    sections.append(current_section)
                current_section = {
                    'title': line.split('.', 1)[1].strip(),
                    'outline': ''
                }
            elif current_section:
                current_section['outline'] += line + '\n'
        
        if current_section:
            sections.append(current_section)
        
        return sections