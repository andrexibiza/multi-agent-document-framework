"""Example of creating custom specialized agents."""

import asyncio
import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from madf.agents.base import BaseAgent
from madf.models.task import Task, TaskResult
from madf.utils.config import AgentConfig, ModelConfig
from madf.utils.logging import setup_logging


class DataAnalysisAgent(BaseAgent):
    """
    Custom agent for data analysis and visualization recommendations.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.specialization = "data_analysis"
    
    async def process(self, task: Task) -> TaskResult:
        """
        Analyze data and provide insights.
        
        Expected task data:
        - data_description: Description of the data
        - analysis_goals: Goals for the analysis
        """
        data_desc = task.data.get('data_description')
        goals = task.data.get('analysis_goals', [])
        
        prompt = f"""Perform a comprehensive data analysis plan for:

Data Description:
{data_desc}

Analysis Goals:
{', '.join(goals)}

Provide:
1. Recommended analysis approaches
2. Statistical methods to use
3. Visualization suggestions
4. Expected insights
5. Potential challenges"""
        
        analysis_plan = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.5,
            system_message="You are a data analysis expert."
        )
        
        return TaskResult(
            task_id=task.id,
            success=True,
            data={'analysis_plan': analysis_plan}
        )


class SummarizationAgent(BaseAgent):
    """
    Custom agent for document summarization.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.specialization = "summarization"
    
    async def process(self, task: Task) -> TaskResult:
        """
        Create summary of content.
        
        Expected task data:
        - content: Content to summarize
        - summary_length: Target summary length
        - format: Summary format (bullet, paragraph, executive)
        """
        content = task.data.get('content')
        length = task.data.get('summary_length', 'medium')
        format_type = task.data.get('format', 'paragraph')
        
        prompt = f"""Create a {length} summary of the following content:

{content}

Format: {format_type}

Ensure the summary:
1. Captures key points
2. Maintains accuracy
3. Is concise and clear
4. Follows the specified format"""
        
        summary = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.4,
            system_message="You are an expert at creating concise, accurate summaries."
        )
        
        return TaskResult(
            task_id=task.id,
            success=True,
            data={'summary': summary}
        )


async def main():
    """Demonstrate custom agents."""
    setup_logging(level="INFO")
    
    print("Custom Agent Examples\n" + "="*50)
    
    # Create custom agent configs
    analysis_config = AgentConfig(
        name="data_analysis",
        model_config=ModelConfig(model="gpt-4", temperature=0.5)
    )
    
    summarization_config = AgentConfig(
        name="summarization",
        model_config=ModelConfig(model="gpt-4", temperature=0.3)
    )
    
    # Instantiate custom agents
    analysis_agent = DataAnalysisAgent(analysis_config)
    summarization_agent = SummarizationAgent(summarization_config)
    
    # Test data analysis agent
    print("\n1. Testing Data Analysis Agent...")
    analysis_task = Task(
        id="task_1",
        type="data_analysis",
        data={
            'data_description': "Sales data from Q1-Q4 2024 including revenue, units sold, and customer demographics",
            'analysis_goals': [
                "Identify trends",
                "Find growth opportunities",
                "Understand customer segments"
            ]
        }
    )
    
    analysis_result = await analysis_agent.execute(analysis_task)
    
    if analysis_result.success:
        print("\nAnalysis Plan:")
        print(analysis_result.data['analysis_plan'][:500] + "...")
    
    # Test summarization agent
    print("\n2. Testing Summarization Agent...")
    long_text = """Artificial intelligence (AI) has emerged as one of the most transformative
    technologies of the 21st century, revolutionizing industries from healthcare to finance.
    Machine learning, a subset of AI, enables systems to learn from data and improve their
    performance without explicit programming. Deep learning, using neural networks with
    multiple layers, has achieved remarkable success in image recognition, natural language
    processing, and game playing. However, challenges remain in areas such as explainability,
    bias mitigation, and ethical considerations. The future of AI promises even greater
    advances, but also requires careful consideration of societal impacts."""
    
    summary_task = Task(
        id="task_2",
        type="summarization",
        data={
            'content': long_text,
            'summary_length': 'short',
            'format': 'bullet'
        }
    )
    
    summary_result = await summarization_agent.execute(summary_task)
    
    if summary_result.success:
        print("\nSummary:")
        print(summary_result.data['summary'])
    
    # Show metrics
    print("\n" + "="*50)
    print("Agent Metrics:")
    print("="*50)
    for agent_name, agent in [("Data Analysis", analysis_agent), ("Summarization", summarization_agent)]:
        metrics = agent.get_metrics()
        print(f"\n{agent_name}:")
        print(f"  State: {metrics['state']}")
        print(f"  Completed: {metrics['metrics']['tasks_completed']}")
        print(f"  Failed: {metrics['metrics']['tasks_failed']}")


if __name__ == "__main__":
    asyncio.run(main())