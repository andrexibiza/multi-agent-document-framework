# Agent Design and Implementation

## Overview

Agents are the core building blocks of the Multi-Agent Document Framework. Each agent is a specialized AI system designed to perform specific tasks in the document creation pipeline. This document details the design, implementation, and usage of each agent type.

## Agent Design Principles

### Single Responsibility
Each agent focuses on one aspect of document creation:
- Research agents only gather information
- Writing agents only create content
- Editing agents only refine text
- Verification agents only check quality

This separation enables:
- **Better prompt engineering**: Specialized prompts for each task
- **Easier testing**: Test each capability independently
- **Flexible composition**: Mix and match agents for different workflows
- **Clear accountability**: Know which agent is responsible for what

### Stateless Operation
Agents are designed to be stateless:
- All context is passed in messages
- No persistent state between tasks
- Easy to scale horizontally
- Simple error recovery

### Observable Behavior
All agent actions are logged and measured:
- Input and output tracking
- Performance metrics collection
- Error reporting
- Decision explanation

## Base Agent Architecture

### Core Components

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class AgentMetrics:
    """Performance metrics for an agent"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_processing_time: float = 0.0
    total_tokens_used: int = 0
    average_quality_contribution: float = 0.0
    last_activity: Optional[datetime] = None

@dataclass
class Task:
    """Task definition for agent processing"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    context: Dict[str, Any]
    priority: int = 0
    timeout: Optional[float] = None
    created_at: datetime = None
    
@dataclass
class Result:
    """Result of agent processing"""
    task_id: str
    success: bool
    output: Any
    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    errors: Optional[List[str]] = None

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    Provides common functionality:
    - Message handling
    - Metrics tracking
    - Error handling
    - LLM integration
    """
    
    def __init__(self, 
                 name: str,
                 model: str,
                 config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.model = model
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.metrics = AgentMetrics()
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize LLM client based on model"""
        from madf.utils.llm_wrapper import LLMWrapper
        return LLMWrapper(
            model=self.model,
            temperature=self.config.get('temperature', 0.7),
            max_tokens=self.config.get('max_tokens', 2000)
        )
    
    @abstractmethod
    async def process(self, task: Task) -> Result:
        """
        Process a task and return result.
        Must be implemented by subclasses.
        """
        pass
    
    async def handle_task(self, task: Task) -> Result:
        """
        Main task handling with error handling and metrics.
        """
        self.status = AgentStatus.BUSY
        start_time = datetime.now()
        
        try:
            # Process the task
            result = await self.process(task)
            
            # Update metrics
            self.metrics.tasks_completed += 1
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics.total_processing_time += processing_time
            self.metrics.last_activity = datetime.now()
            
            result.metrics['processing_time'] = processing_time
            result.metrics['agent_name'] = self.name
            
            return result
            
        except Exception as e:
            self.metrics.tasks_failed += 1
            self.status = AgentStatus.ERROR
            
            return Result(
                task_id=task.task_id,
                success=False,
                output=None,
                metadata={'error': str(e)},
                metrics={},
                errors=[str(e)]
            )
        finally:
            self.status = AgentStatus.IDLE
    
    def get_metrics(self) -> AgentMetrics:
        """Return current metrics"""
        return self.metrics
    
    def reset_metrics(self):
        """Reset metrics to zero"""
        self.metrics = AgentMetrics()
```

## Research Agent

### Purpose and Capabilities

The Research Agent is responsible for information gathering and knowledge base construction. It:

1. **Searches for information** using multiple sources (web, databases, APIs)
2. **Validates sources** for credibility and relevance
3. **Extracts key information** and organizes it logically
4. **Builds context** for downstream agents

### Implementation

```python
from typing import List, Dict, Any
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json

class ResearchAgent(BaseAgent):
    """
    Agent specialized in information gathering and research.
    """
    
    def __init__(self, 
                 model: str = "gpt-4",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name="research", model=model, config=config)
        self.search_api_key = config.get('search_api_key') if config else None
        self.max_sources = config.get('max_sources', 10) if config else 10
        
    async def process(self, task: Task) -> Result:
        """
        Process research task.
        
        Expected task payload:
        {
            "topic": str,
            "requirements": {
                "depth": "basic" | "intermediate" | "advanced",
                "focus_areas": List[str],
                "required_sources": int,
                "source_types": List[str]  # academic, news, blog, etc.
            }
        }
        """
        topic = task.payload['topic']
        requirements = task.payload.get('requirements', {})
        
        # Generate search queries
        queries = await self._generate_search_queries(topic, requirements)
        
        # Execute searches in parallel
        search_results = await self._execute_searches(queries)
        
        # Rank and filter sources
        ranked_sources = await self._rank_sources(search_results, requirements)
        
        # Extract and synthesize information
        research_context = await self._synthesize_information(
            ranked_sources, 
            requirements
        )
        
        return Result(
            task_id=task.task_id,
            success=True,
            output=research_context,
            metadata={
                'sources_found': len(search_results),
                'sources_used': len(ranked_sources),
                'queries_executed': len(queries)
            },
            metrics={
                'tokens_used': self.llm.get_token_count()
            }
        )
    
    async def _generate_search_queries(self, 
                                       topic: str, 
                                       requirements: Dict) -> List[str]:
        """
        Generate effective search queries using LLM.
        """
        prompt = f"""
Generate 5 search queries to research the following topic comprehensively.

Topic: {topic}

Requirements:
- Depth: {requirements.get('depth', 'intermediate')}
- Focus areas: {', '.join(requirements.get('focus_areas', []))}

Provide diverse queries that cover different aspects of the topic.
Return as JSON array of strings.
"""
        
        response = await self.llm.generate(prompt)
        queries = json.loads(response)
        return queries
    
    async def _execute_searches(self, queries: List[str]) -> List[Dict]:
        """
        Execute multiple searches in parallel.
        """
        tasks = [self._search_web(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failed searches
        valid_results = [
            result for result in results 
            if not isinstance(result, Exception)
        ]
        
        # Flatten results
        all_results = []
        for result_set in valid_results:
            all_results.extend(result_set)
        
        return all_results
    
    async def _search_web(self, query: str) -> List[Dict]:
        """
        Execute web search using search API.
        """
        # Implement actual search API integration
        # This is a placeholder implementation
        
        if not self.search_api_key:
            # Fallback to simple web scraping
            return await self._scrape_google(query)
        
        # Use proper search API (Google Custom Search, Bing, etc.)
        async with aiohttp.ClientSession() as session:
            # API call implementation here
            pass
    
    async def _rank_sources(self, 
                           sources: List[Dict],
                           requirements: Dict) -> List[Dict]:
        """
        Rank sources by relevance and credibility.
        """
        prompt = f"""
Rank the following sources for researching this topic.

Topic: {requirements.get('topic', '')}
Focus: {', '.join(requirements.get('focus_areas', []))}

Sources:
{json.dumps(sources[:20], indent=2)}

Rank each source 0-10 based on:
- Relevance to topic (40%)
- Source credibility (30%)
- Information quality (20%)
- Recency (10%)

Return top {min(self.max_sources, len(sources))} sources as JSON array.
"""
        
        response = await self.llm.generate(prompt)
        ranked_sources = json.loads(response)
        return ranked_sources
    
    async def _synthesize_information(self,
                                     sources: List[Dict],
                                     requirements: Dict) -> Dict:
        """
        Synthesize information from sources into structured context.
        """
        sources_text = "\n\n".join([
            f"Source {i+1}: {s.get('title', 'Untitled')}\n{s.get('content', '')}"
            for i, s in enumerate(sources)
        ])
        
        prompt = f"""
Synthesize the following sources into a structured research context.

Sources:
{sources_text}

Requirements:
- Depth: {requirements.get('depth', 'intermediate')}
- Focus: {', '.join(requirements.get('focus_areas', []))}

Provide:
1. Key facts and findings
2. Main themes and concepts
3. Important data and statistics
4. Expert perspectives
5. Source citations

Return as structured JSON.
"""
        
        response = await self.llm.generate(prompt)
        context = json.loads(response)
        
        # Add source metadata
        context['sources'] = [
            {
                'title': s.get('title'),
                'url': s.get('url'),
                'credibility_score': s.get('score')
            }
            for s in sources
        ]
        
        return context
```

### Usage Example

```python
# Create research agent
research_agent = ResearchAgent(
    model="gpt-4",
    config={
        'temperature': 0.3,  # Lower for more focused research
        'max_sources': 15,
        'search_api_key': 'YOUR_API_KEY'
    }
)

# Create research task
task = Task(
    task_id="research_001",
    task_type="research",
    payload={
        "topic": "The impact of quantum computing on cryptography",
        "requirements": {
            "depth": "advanced",
            "focus_areas": [
                "current encryption methods",
                "quantum algorithms",
                "post-quantum cryptography"
            ],
            "required_sources": 10,
            "source_types": ["academic", "technical"]
        }
    },
    context={}
)

# Execute research
result = await research_agent.handle_task(task)
research_context = result.output
```

## Writing Agent

### Purpose and Capabilities

The Writing Agent creates the initial document content. It:

1. **Generates outlines** based on research context
2. **Writes content** with appropriate tone and style
3. **Structures information** logically
4. **Maintains narrative flow** throughout the document

### Implementation

```python
class WritingAgent(BaseAgent):
    """
    Agent specialized in content creation and document writing.
    """
    
    def __init__(self, 
                 model: str = "gpt-4",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name="writing", model=model, config=config)
        
    async def process(self, task: Task) -> Result:
        """
        Process writing task.
        
        Expected task payload:
        {
            "research_context": Dict,
            "requirements": {
                "length": str,  # "2000-3000 words"
                "tone": str,  # "professional", "casual", etc.
                "style": str,  # "technical", "narrative", etc.
                "target_audience": str,
                "structure": List[str]  # Optional section structure
            }
        }
        """
        research_context = task.payload['research_context']
        requirements = task.payload['requirements']
        
        # Generate outline
        outline = await self._generate_outline(research_context, requirements)
        
        # Write each section
        sections = await self._write_sections(outline, research_context, requirements)
        
        # Assemble document
        document = await self._assemble_document(sections, requirements)
        
        return Result(
            task_id=task.task_id,
            success=True,
            output={
                'document': document,
                'outline': outline,
                'word_count': self._count_words(document)
            },
            metadata={
                'sections_written': len(sections),
                'outline_structure': outline
            },
            metrics={
                'tokens_used': self.llm.get_token_count()
            }
        )
    
    async def _generate_outline(self,
                               research_context: Dict,
                               requirements: Dict) -> Dict:
        """
        Generate document outline.
        """
        context_summary = json.dumps(research_context, indent=2)
        
        prompt = f"""
Create a detailed outline for a document based on this research.

Research Context:
{context_summary}

Requirements:
- Length: {requirements.get('length', '2000 words')}
- Tone: {requirements.get('tone', 'professional')}
- Audience: {requirements.get('target_audience', 'general')}

Provide:
1. Main sections with titles
2. Subsections for each main section
3. Approximate word count allocation
4. Key points to cover in each section

Return as structured JSON:
{{
    "title": str,
    "sections": [
        {{
            "title": str,
            "word_count": int,
            "key_points": [str],
            "subsections": [str]
        }}
    ]
}}
"""
        
        response = await self.llm.generate(prompt)
        outline = json.loads(response)
        return outline
    
    async def _write_sections(self,
                             outline: Dict,
                             research_context: Dict,
                             requirements: Dict) -> List[Dict]:
        """
        Write all sections in parallel.
        """
        section_tasks = [
            self._write_section(section, research_context, requirements)
            for section in outline['sections']
        ]
        
        sections = await asyncio.gather(*section_tasks)
        return sections
    
    async def _write_section(self,
                            section_spec: Dict,
                            research_context: Dict,
                            requirements: Dict) -> Dict:
        """
        Write a single section.
        """
        relevant_research = self._extract_relevant_research(
            research_context,
            section_spec['key_points']
        )
        
        prompt = f"""
Write the following section for a document.

Section: {section_spec['title']}
Target length: {section_spec['word_count']} words
Key points to cover:
{json.dumps(section_spec['key_points'], indent=2)}

Relevant research:
{json.dumps(relevant_research, indent=2)}

Style requirements:
- Tone: {requirements.get('tone', 'professional')}
- Style: {requirements.get('style', 'informative')}
- Audience: {requirements.get('target_audience', 'general')}

Write engaging, well-structured content that flows naturally.
Include relevant data and citations from the research.
"""
        
        content = await self.llm.generate(prompt)
        
        return {
            'title': section_spec['title'],
            'content': content,
            'word_count': self._count_words(content)
        }
    
    async def _assemble_document(self,
                                sections: List[Dict],
                                requirements: Dict) -> str:
        """
        Assemble sections into final document with transitions.
        """
        # Combine sections
        document_parts = []
        
        for i, section in enumerate(sections):
            document_parts.append(f"## {section['title']}\n\n")
            document_parts.append(section['content'])
            document_parts.append("\n\n")
        
        document = "".join(document_parts)
        
        # Add introduction and conclusion if not present
        if not any('introduction' in s['title'].lower() for s in sections):
            intro = await self._generate_introduction(sections, requirements)
            document = intro + "\n\n" + document
        
        if not any('conclusion' in s['title'].lower() for s in sections):
            conclusion = await self._generate_conclusion(sections, requirements)
            document = document + "\n\n" + conclusion
        
        return document
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    def _extract_relevant_research(self,
                                  research_context: Dict,
                                  key_points: List[str]) -> Dict:
        """
        Extract research relevant to specific key points.
        """
        # Simple keyword matching - can be enhanced with semantic search
        relevant_facts = []
        
        for fact in research_context.get('key_facts', []):
            for point in key_points:
                if any(word in fact.lower() for word in point.lower().split()):
                    relevant_facts.append(fact)
                    break
        
        return {
            'facts': relevant_facts,
            'sources': research_context.get('sources', [])
        }
```

## Editing Agent

### Purpose and Capabilities

The Editing Agent refines and improves document quality. It:

1. **Corrects grammar and spelling** errors
2. **Improves clarity** and readability
3. **Ensures consistency** in style and terminology
4. **Optimizes sentence structure** and flow

### Implementation

```python
class EditingAgent(BaseAgent):
    """
    Agent specialized in document editing and refinement.
    """
    
    def __init__(self, 
                 model: str = "gpt-4",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name="editing", model=model, config=config)
    
    async def process(self, task: Task) -> Result:
        """
        Process editing task.
        
        Expected task payload:
        {
            "document": str,
            "requirements": {
                "tone": str,
                "style_guide": Optional[str],
                "readability_target": Optional[str],
                "preserve_structure": bool
            }
        }
        """
        document = task.payload['document']
        requirements = task.payload.get('requirements', {})
        
        # Split into manageable chunks
        chunks = self._split_document(document)
        
        # Edit chunks in parallel
        edited_chunks = await self._edit_chunks(chunks, requirements)
        
        # Reassemble and final pass
        edited_document = await self._final_edit(
            edited_chunks,
            requirements
        )
        
        # Generate edit summary
        changes = await self._summarize_changes(document, edited_document)
        
        return Result(
            task_id=task.task_id,
            success=True,
            output={
                'edited_document': edited_document,
                'changes': changes
            },
            metadata={
                'chunks_processed': len(chunks),
                'total_changes': len(changes)
            },
            metrics={
                'tokens_used': self.llm.get_token_count()
            }
        )
    
    def _split_document(self, document: str, chunk_size: int = 1000) -> List[str]:
        """
        Split document into chunks for processing.
        """
        paragraphs = document.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para.split())
            
            if current_length + para_length > chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    async def _edit_chunks(self,
                          chunks: List[str],
                          requirements: Dict) -> List[str]:
        """
        Edit all chunks in parallel.
        """
        edit_tasks = [
            self._edit_chunk(chunk, requirements, i)
            for i, chunk in enumerate(chunks)
        ]
        
        edited_chunks = await asyncio.gather(*edit_tasks)
        return edited_chunks
    
    async def _edit_chunk(self,
                         chunk: str,
                         requirements: Dict,
                         chunk_index: int) -> str:
        """
        Edit a single chunk.
        """
        prompt = f"""
Edit the following text to improve quality while preserving meaning.

Text:
{chunk}

Editing guidelines:
- Fix grammar, spelling, and punctuation errors
- Improve sentence structure and clarity
- Enhance readability
- Maintain consistent tone: {requirements.get('tone', 'professional')}
- Ensure logical flow between sentences
- Remove redundancy
- {'Preserve the overall structure' if requirements.get('preserve_structure', True) else 'Feel free to restructure for better flow'}

Return only the edited text, no explanations.
"""
        
        edited_chunk = await self.llm.generate(prompt)
        return edited_chunk.strip()
    
    async def _final_edit(self,
                         chunks: List[str],
                         requirements: Dict) -> str:
        """
        Reassemble and perform final consistency edit.
        """
        document = '\n\n'.join(chunks)
        
        # Final consistency pass
        prompt = f"""
Review this document for overall consistency and flow.

Document:
{document}

Check for:
1. Consistent terminology usage
2. Smooth transitions between sections
3. Consistent voice and tone
4. Overall coherence

Make only necessary changes to improve consistency.
Return the final document.
"""
        
        final_document = await self.llm.generate(prompt)
        return final_document.strip()
    
    async def _summarize_changes(self,
                                original: str,
                                edited: str) -> List[Dict]:
        """
        Generate summary of changes made.
        """
        # Simple diff-like summary
        # In production, use proper diff library
        prompt = f"""
Summarize the main edits made to this document.

Original length: {len(original.split())} words
Edited length: {len(edited.split())} words

List the types of changes made (grammar, clarity, structure, etc.)
and provide 3-5 specific examples.

Return as JSON array of change objects:
[{{
    "type": str,
    "description": str,
    "example": {{
        "before": str,
        "after": str
    }}
}}]
"""
        
        response = await self.llm.generate(prompt)
        changes = json.loads(response)
        return changes
```

## Verification Agent

### Purpose and Capabilities

The Verification Agent ensures document quality and accuracy. It:

1. **Fact-checks** claims against sources
2. **Validates completeness** against requirements
3. **Calculates quality scores** across multiple dimensions
4. **Generates feedback** for improvement

### Implementation

```python
class VerificationAgent(BaseAgent):
    """
    Agent specialized in document verification and quality assurance.
    """
    
    def __init__(self, 
                 model: str = "gpt-4",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name="verification", model=model, config=config)
    
    async def process(self, task: Task) -> Result:
        """
        Process verification task.
        
        Expected task payload:
        {
            "document": str,
            "research_context": Dict,
            "requirements": Dict,
            "quality_threshold": float
        }
        """
        document = task.payload['document']
        research_context = task.payload.get('research_context', {})
        requirements = task.payload['requirements']
        threshold = task.payload.get('quality_threshold', 0.8)
        
        # Run verification checks in parallel
        fact_check_task = self._fact_check(document, research_context)
        completeness_task = self._check_completeness(document, requirements)
        quality_task = self._assess_quality(document, requirements)
        
        fact_check, completeness, quality = await asyncio.gather(
            fact_check_task,
            completeness_task,
            quality_task
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            fact_check,
            completeness,
            quality
        )
        
        # Generate feedback if below threshold
        feedback = None
        if overall_score < threshold:
            feedback = await self._generate_feedback(
                fact_check,
                completeness,
                quality,
                requirements
            )
        
        return Result(
            task_id=task.task_id,
            success=True,
            output={
                'overall_score': overall_score,
                'fact_check': fact_check,
                'completeness': completeness,
                'quality': quality,
                'feedback': feedback,
                'passes_threshold': overall_score >= threshold
            },
            metadata={
                'threshold': threshold,
                'checks_performed': 3
            },
            metrics={
                'tokens_used': self.llm.get_token_count()
            }
        )
    
    async def _fact_check(self,
                         document: str,
                         research_context: Dict) -> Dict:
        """
        Verify factual claims against research sources.
        """
        sources = research_context.get('sources', [])
        facts = research_context.get('key_facts', [])
        
        prompt = f"""
Fact-check the following document against the research sources.

Document:
{document}

Research Facts:
{json.dumps(facts, indent=2)}

For each significant claim in the document:
1. Verify if it's supported by the research
2. Rate confidence: verified, supported, uncertain, or contradicted
3. Identify any unsupported claims

Return as JSON:
{{
    "verified_claims": int,
    "unsupported_claims": int,
    "confidence_score": float (0-1),
    "issues": [{{
        "claim": str,
        "status": str,
        "explanation": str
    }}]
}}
"""
        
        response = await self.llm.generate(prompt)
        fact_check_results = json.loads(response)
        return fact_check_results
    
    async def _check_completeness(self,
                                 document: str,
                                 requirements: Dict) -> Dict:
        """
        Check if document meets all requirements.
        """
        prompt = f"""
Verify if this document meets all requirements.

Document:
{document}

Requirements:
{json.dumps(requirements, indent=2)}

Check:
1. Length requirement met
2. All required topics covered
3. Appropriate depth and detail
4. Target audience considerations
5. Any specific requirements fulfilled

Return as JSON:
{{
    "completeness_score": float (0-1),
    "requirements_met": int,
    "requirements_total": int,
    "missing_elements": [str],
    "suggestions": [str]
}}
"""
        
        response = await self.llm.generate(prompt)
        completeness_results = json.loads(response)
        return completeness_results
    
    async def _assess_quality(self,
                            document: str,
                            requirements: Dict) -> Dict:
        """
        Assess overall document quality.
        """
        prompt = f"""
Assess the quality of this document across multiple dimensions.

Document:
{document}

Requirements:
- Tone: {requirements.get('tone', 'professional')}
- Audience: {requirements.get('target_audience', 'general')}

Rate (0-1) on:
1. Coherence: Logical flow and organization
2. Clarity: Easy to understand
3. Style: Appropriate tone and voice
4. Engagement: Interesting and compelling
5. Technical accuracy: Correct terminology and concepts

Return as JSON:
{{
    "coherence_score": float,
    "clarity_score": float,
    "style_score": float,
    "engagement_score": float,
    "technical_score": float,
    "overall_quality": float,
    "strengths": [str],
    "weaknesses": [str]
}}
"""
        
        response = await self.llm.generate(prompt)
        quality_results = json.loads(response)
        return quality_results
    
    def _calculate_overall_score(self,
                                fact_check: Dict,
                                completeness: Dict,
                                quality: Dict) -> float:
        """
        Calculate weighted overall score.
        """
        score = (
            0.30 * fact_check.get('confidence_score', 0) +
            0.30 * completeness.get('completeness_score', 0) +
            0.40 * quality.get('overall_quality', 0)
        )
        return round(score, 3)
    
    async def _generate_feedback(self,
                                fact_check: Dict,
                                completeness: Dict,
                                quality: Dict,
                                requirements: Dict) -> Dict:
        """
        Generate actionable feedback for improvement.
        """
        issues = []
        
        # Fact-checking issues
        if fact_check.get('unsupported_claims', 0) > 0:
            issues.extend(fact_check.get('issues', []))
        
        # Completeness issues
        if completeness.get('missing_elements'):
            for element in completeness['missing_elements']:
                issues.append({
                    'category': 'completeness',
                    'issue': element,
                    'priority': 'high'
                })
        
        # Quality issues
        if quality.get('weaknesses'):
            for weakness in quality['weaknesses']:
                issues.append({
                    'category': 'quality',
                    'issue': weakness,
                    'priority': 'medium'
                })
        
        return {
            'issues': issues,
            'priority_improvements': self._prioritize_improvements(issues),
            'suggestions': completeness.get('suggestions', []) + quality.get('strengths', [])
        }
    
    def _prioritize_improvements(self, issues: List[Dict]) -> List[str]:
        """
        Prioritize improvements based on impact.
        """
        high_priority = [i['issue'] for i in issues if i.get('priority') == 'high']
        return high_priority[:5]  # Top 5 most important
```

## Agent Configuration

### Configuration File Format

```yaml
# config/agent_configs/research_agent.yaml
agent:
  name: research
  model: gpt-4
  temperature: 0.3
  max_tokens: 2000
  
settings:
  max_sources: 15
  search_api_key: ${SEARCH_API_KEY}
  source_types:
    - academic
    - news
    - technical
  credibility_threshold: 0.7
  
performance:
  timeout: 120  # seconds
  retry_attempts: 3
  cache_results: true
  cache_ttl: 3600  # 1 hour
```

### Loading Configuration

```python
import yaml
from pathlib import Path

def load_agent_config(agent_type: str) -> Dict:
    """
    Load agent configuration from file.
    """
    config_path = Path(f"config/agent_configs/{agent_type}_agent.yaml")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Replace environment variables
    config = _replace_env_vars(config)
    
    return config

# Usage
research_config = load_agent_config('research')
research_agent = ResearchAgent(config=research_config)
```

## Testing Agents

### Unit Tests

```python
import pytest
from madf.agents import ResearchAgent

@pytest.mark.asyncio
async def test_research_agent_basic():
    """Test basic research agent functionality."""
    agent = ResearchAgent(model="gpt-3.5-turbo")
    
    task = Task(
        task_id="test_001",
        task_type="research",
        payload={
            "topic": "Python programming",
            "requirements": {
                "depth": "basic",
                "focus_areas": ["syntax", "libraries"],
                "required_sources": 5
            }
        },
        context={}
    )
    
    result = await agent.handle_task(task)
    
    assert result.success
    assert 'key_facts' in result.output
    assert len(result.output['sources']) >= 5
    assert result.metrics['processing_time'] > 0
```

---

This comprehensive agent design provides the foundation for building sophisticated multi-agent document creation systems.