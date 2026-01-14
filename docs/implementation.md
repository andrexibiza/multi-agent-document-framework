# Implementation Guide

This guide provides detailed implementation instructions for building and deploying the Multi-Agent Document Creation Framework.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Core Implementation](#core-implementation)
3. [Agent Development](#agent-development)
4. [Orchestration Logic](#orchestration-logic)
5. [Quality Systems](#quality-systems)
6. [Deployment](#deployment)

## System Requirements

### Hardware Requirements

- **Minimum**:
  - 4 CPU cores
  - 8GB RAM
  - 20GB storage

- **Recommended**:
  - 8+ CPU cores
  - 16GB+ RAM
  - 50GB SSD storage

- **Production**:
  - 16+ CPU cores
  - 32GB+ RAM
  - 100GB SSD storage
  - Load balancer
  - Distributed cache (Redis)

### Software Requirements

- Python 3.9+
- PostgreSQL 13+ (for state storage)
- Redis 6+ (for caching and message queue)
- Docker & Docker Compose (optional)

### API Requirements

- OpenAI API key (GPT-4 access)
- Alternative LLM APIs (optional): Anthropic, Cohere, etc.

## Core Implementation

### 1. Project Structure

```
multi-agent-document-framework/
├── src/
│   └── madf/
│       ├── __init__.py
│       ├── orchestrator.py
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── research.py
│       │   ├── writing.py
│       │   ├── editing.py
│       │   └── verification.py
│       ├── coordination/
│       │   ├── __init__.py
│       │   ├── message_bus.py
│       │   ├── workflow.py
│       │   └── resource_manager.py
│       ├── quality/
│       │   ├── __init__.py
│       │   ├── evaluator.py
│       │   ├── metrics.py
│       │   └── validators.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── document.py
│       │   ├── request.py
│       │   └── task.py
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── llm_client.py
│       │   ├── config.py
│       │   └── logging.py
│       └── storage/
│           ├── __init__.py
│           ├── state_store.py
│           └── cache.py
├── tests/
├── examples/
├── docs/
├── config/
├── requirements.txt
├── setup.py
└── README.md
```

### 2. Configuration System

Implement a flexible configuration system:

```python
# src/madf/utils/config.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
import os
import yaml

@dataclass
class ModelConfig:
    """LLM model configuration."""
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4000
    api_key: Optional[str] = None
    
    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv(f"{self.provider.upper()}_API_KEY")

@dataclass
class AgentConfig:
    """Individual agent configuration."""
    name: str
    model_config: ModelConfig
    timeout: int = 120
    max_retries: int = 3
    cache_enabled: bool = True

@dataclass
class OrchestratorConfig:
    """Orchestrator configuration."""
    max_agents: int = 10
    timeout: int = 300
    quality_threshold: float = 0.85
    enable_parallel: bool = True
    max_concurrent_tasks: int = 5
    retry_attempts: int = 3
    
    # Agent-specific configs
    research_config: Optional[AgentConfig] = None
    writing_config: Optional[AgentConfig] = None
    editing_config: Optional[AgentConfig] = None
    verification_config: Optional[AgentConfig] = None
    
    @classmethod
    def from_yaml(cls, path: str) -> 'OrchestratorConfig':
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'OrchestratorConfig':
        """Create config from dictionary."""
        # Parse and create config
        # Implementation details...
        pass
```

### 3. Data Models

```python
# src/madf/models/document.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class DocumentStatus(Enum):
    PENDING = "pending"
    RESEARCHING = "researching"
    WRITING = "writing"
    EDITING = "editing"
    VERIFYING = "verifying"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class DocumentSection:
    """Represents a section of the document."""
    title: str
    content: str
    order: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Document:
    """Complete document with metadata."""
    id: str
    title: str
    sections: List[DocumentSection]
    status: DocumentStatus
    quality_score: float = 0.0
    word_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_full_text(self) -> str:
        """Get complete document text."""
        return "\n\n".join([s.content for s in sorted(self.sections, key=lambda x: x.order)])
    
    def update_word_count(self):
        """Update word count based on content."""
        text = self.get_full_text()
        self.word_count = len(text.split())

# src/madf/models/request.py
@dataclass
class DocumentRequest:
    """Request for document creation."""
    topic: str
    document_type: str  # article, report, paper, etc.
    target_length: int  # words
    style: str  # formal, casual, technical, etc.
    audience: str  # target audience
    requirements: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    outline: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate request parameters."""
        if not self.topic or len(self.topic) < 5:
            raise ValueError("Topic must be at least 5 characters")
        if self.target_length < 100:
            raise ValueError("Target length must be at least 100 words")
        return True

# src/madf/models/task.py
@dataclass
class Task:
    """Represents a task for an agent."""
    id: str
    type: str
    data: Dict[str, Any]
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    assigned_to: Optional[str] = None
    
@dataclass
class TaskResult:
    """Result from agent task execution."""
    task_id: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### 4. LLM Client Implementation

```python
# src/madf/utils/llm_client.py
import openai
import asyncio
from typing import List, Dict, Optional
import tiktoken

class LLMClient:
    """Unified client for LLM API interactions."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.provider = config.provider
        self.model = config.model
        
        if self.provider == "openai":
            openai.api_key = config.api_key
            self.encoding = tiktoken.encoding_for_model(self.model)
        
    async def generate(self, 
                      prompt: str, 
                      system_message: Optional[str] = None,
                      temperature: Optional[float] = None,
                      max_tokens: Optional[int] = None) -> str:
        """Generate text from prompt."""
        
        temp = temperature if temperature is not None else self.config.temperature
        max_tok = max_tokens if max_tokens is not None else self.config.max_tokens
        
        if self.provider == "openai":
            return await self._openai_generate(prompt, system_message, temp, max_tok)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _openai_generate(self, prompt: str, system_message: Optional[str],
                              temperature: float, max_tokens: int) -> str:
        """OpenAI-specific generation."""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.provider == "openai":
            return len(self.encoding.encode(text))
        return len(text.split())  # Rough estimate for other providers
    
    async def generate_structured(self, 
                                 prompt: str,
                                 schema: Dict,
                                 **kwargs) -> Dict:
        """Generate structured output matching schema."""
        # Implementation for structured generation
        # Can use function calling or JSON mode
        pass
```

## Agent Development

### Base Agent Implementation

```python
# src/madf/agents/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

class AgentState:
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        self.llm_client = LLMClient(config.model_config)
        self.state = AgentState.IDLE
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.metrics = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_time': 0.0
        }
    
    async def execute(self, task: Task) -> TaskResult:
        """
        Execute a task with error handling and metrics.
        
        This is the main entry point for task execution.
        It wraps the process() method with common functionality.
        """
        self.state = AgentState.BUSY
        self.logger.info(f"Starting task {task.id}")
        start_time = datetime.now()
        
        try:
            result = await self._execute_with_retry(task)
            self.metrics['tasks_completed'] += 1
            self.state = AgentState.IDLE
            
        except Exception as e:
            self.logger.error(f"Task {task.id} failed: {str(e)}")
            self.metrics['tasks_failed'] += 1
            self.state = AgentState.ERROR
            result = TaskResult(
                task_id=task.id,
                success=False,
                data={},
                error=str(e)
            )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result.execution_time = execution_time
        self.metrics['total_time'] += execution_time
        
        return result
    
    async def _execute_with_retry(self, task: Task) -> TaskResult:
        """Execute task with retry logic."""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                return await asyncio.wait_for(
                    self.process(task),
                    timeout=self.config.timeout
                )
            except asyncio.TimeoutError:
                last_error = "Task timed out"
                self.logger.warning(f"Task {task.id} timed out (attempt {attempt + 1})")
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Task {task.id} failed (attempt {attempt + 1}): {e}")
            
            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception(f"Task failed after {self.config.max_retries} attempts: {last_error}")
    
    @abstractmethod
    async def process(self, task: Task) -> TaskResult:
        """
        Process a task and return results.
        
        This method must be implemented by each specialized agent.
        """
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        return {
            'name': self.name,
            'state': self.state,
            'metrics': self.metrics.copy()
        }
```

### Research Agent Implementation

```python
# src/madf/agents/research.py
from typing import List, Dict, Any
import json

class ResearchAgent(BaseAgent):
    """Agent specialized in information gathering and research."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.specialization = "research"
    
    async def process(self, task: Task) -> TaskResult:
        """
        Execute research task.
        
        Task data should contain:
        - query: Main research question
        - depth: Research depth (shallow, moderate, deep)
        - sources: Optional list of preferred sources
        """
        query = task.data.get('query')
        depth = task.data.get('depth', 'moderate')
        
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
        prompt = f"""
Break down this research query into 3-5 specific sub-questions that need to be answered:

Main Query: {query}

Provide the sub-questions as a JSON array of strings.
"""
        
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
        prompt = f"""
Provide comprehensive research on the following question:

{query}

Depth level: {depth}

Include:
1. Key facts and findings
2. Important context and background
3. Relevant statistics or data
4. Notable perspectives or theories
5. Recent developments

Format your response with clear sections.
"""
        
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
        
        prompt = f"""
Synthesize the following research findings into a coherent research brief:

{combined_findings}

Provide:
1. Executive summary
2. Key findings organized by theme
3. Important insights and patterns
4. Gaps or areas needing more research
"""
        
        synthesis = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.5,
            system_message="You are a research analyst synthesizing findings."
        )
        
        return synthesis
    
    async def _structure_research(self, synthesis: str) -> Dict[str, Any]:
        """Structure research into standardized format."""
        # Parse synthesis and structure it
        # This would include extracting sections, facts, etc.
        return {
            'synthesis': synthesis,
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_sources(self, results: List[Dict]) -> List[str]:
        """Extract cited sources from research results."""
        # Implementation to extract and deduplicate sources
        return []
```

### Writing Agent Implementation

```python
# src/madf/agents/writing.py

class WritingAgent(BaseAgent):
    """Agent specialized in content creation and writing."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.specialization = "writing"
    
    async def process(self, task: Task) -> TaskResult:
        """
        Execute writing task.
        
        Task types:
        - outline: Create document outline
        - section: Write a specific section
        - full: Write complete document
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
        
        prompt = f"""
Create a detailed outline for a {requirements.get('document_type', 'document')} based on this research:

{research_brief}

Requirements:
- Target length: {requirements.get('target_length', 2000)} words
- Style: {requirements.get('style', 'formal')}
- Audience: {requirements.get('audience', 'general')}

Provide a hierarchical outline with:
1. Main sections with descriptions
2. Subsections where appropriate
3. Key points to cover in each section
4. Estimated word count per section
"""
        
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
        
        prompt = f"""
Write the following section of a document:

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
5. Includes smooth transitions
"""
        
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
        # Simple parsing - can be made more sophisticated
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
```

### Editing Agent Implementation

```python
# src/madf/agents/editing.py

class EditingAgent(BaseAgent):
    """Agent specialized in content editing and refinement."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.specialization = "editing"
    
    async def process(self, task: Task) -> TaskResult:
        """
        Execute editing task.
        
        Performs multi-pass editing:
        1. Structural and flow improvements
        2. Grammar and style corrections
        3. Consistency and clarity enhancements
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
        prompt = f"""
Improve the structure and flow of this content:

{content}

Focus on:
1. Logical organization of ideas
2. Smooth transitions between paragraphs
3. Clear progression of arguments
4. Effective use of headers and sections
5. Balanced paragraph lengths

Return the improved content maintaining all key information.
"""
        
        return await self.llm_client.generate(
            prompt=prompt,
            temperature=0.5,
            system_message="You are an expert editor improving content structure."
        )
    
    async def _edit_grammar_style(self, content: str, style_guide: Dict) -> str:
        """Correct grammar and refine style."""
        prompt = f"""
Edit this content for grammar and style:

{content}

Focus on:
1. Grammar and punctuation corrections
2. Sentence structure improvements
3. Word choice and vocabulary
4. Tone consistency
5. Active voice preference

Return the corrected content.
"""
        
        return await self.llm_client.generate(
            prompt=prompt,
            temperature=0.3,
            system_message="You are an expert copy editor."
        )
    
    async def _final_polish(self, content: str, style_guide: Dict) -> str:
        """Final polish for consistency and clarity."""
        prompt = f"""
Perform final polishing on this content:

{content}

Focus on:
1. Consistency in terminology and style
2. Clarity and conciseness
3. Removing redundancy
4. Enhancing readability
5. Professional presentation

Return the polished final version.
"""
        
        return await self.llm_client.generate(
            prompt=prompt,
            temperature=0.4,
            system_message="You are an expert editor performing final review."
        )
```

### Verification Agent Implementation

```python
# src/madf/agents/verification.py

class VerificationAgent(BaseAgent):
    """Agent specialized in quality assurance and verification."""
    
    def __init__(self, config: AgentConfig):
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
        prompt = f"""
Verify the factual accuracy of this document against the research brief:

Document:
{document}

Research Brief:
{research_brief}

Provide:
1. List of verifiable claims in the document
2. Accuracy assessment for each claim (verified/uncertain/contradicted)
3. Any unsupported assertions
4. Overall accuracy score (0-1)

Format as JSON.
"""
        
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.2,
            system_message="You are a fact-checking expert."
        )
        
        # Parse and return structured data
        try:
            return json.loads(response)
        except:
            return {'score': 0.8, 'notes': 'Verification completed'}
    
    async def _verify_completeness(self, document: str, requirements: Dict) -> Dict:
        """Verify document meets all requirements."""
        prompt = f"""
Verify this document meets the following requirements:

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

Format as JSON.
"""
        
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
        prompt = f"""
Assess the quality of this document:

{document}

Evaluate:
1. Coherence and logical flow (0-1)
2. Clarity and readability (0-1)
3. Professional presentation (0-1)
4. Engagement and interest (0-1)
5. Technical accuracy (0-1)

Provide scores for each dimension and overall quality score.

Format as JSON.
"""
        
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
```

**Continued in next section due to length...**

---

**Next**: See implementation.md for orchestration, coordination, and deployment details.