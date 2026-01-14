"""
Advanced workflow example showing custom workflow construction.

Demonstrates:
1. Custom workflow building
2. Parallel processing
3. Conditional logic
4. Performance monitoring
5. Error recovery
"""

import asyncio
import time
from typing import Dict, Any, List

from madf import (
    DocumentOrchestrator,
    OrchestratorConfig,
    ResearchAgent,
    WritingAgent,
    EditingAgent,
    VerificationAgent
)
from madf.workflows import WorkflowBuilder
from madf.monitoring import PerformanceMonitor


class ParallelResearchWorkflow:
    """
    Custom workflow that parallelizes research across multiple topics.
    """
    
    def __init__(self, orchestrator: DocumentOrchestrator):
        self.orchestrator = orchestrator
        self.research_agent = orchestrator.agents['research']
    
    async def execute(self, topics: List[str]) -> Dict[str, Any]:
        """
        Execute research on multiple topics in parallel.
        """
        print(f"\nResearching {len(topics)} topics in parallel...")
        
        # Create research tasks
        tasks = []
        for i, topic in enumerate(topics):
            task = Task(
                task_id=f"research_{i}",
                task_type="research",
                payload={
                    'topic': topic,
                    'requirements': {'depth': 'intermediate'}
                },
                context={}
            )
            tasks.append(self.research_agent.handle_task(task))
        
        # Execute in parallel
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time
        
        # Process results
        successful = [r for r in results if not isinstance(r, Exception) and r.success]
        failed = [r for r in results if isinstance(r, Exception) or not r.success]
        
        print(f"✓ Parallel research completed in {elapsed:.2f}s")
        print(f"  Success: {len(successful)}/{len(topics)}")
        
        # Combine research results
        combined_context = self._combine_research(successful)
        
        return {
            'success': len(successful) > 0,
            'context': combined_context,
            'metrics': {
                'topics_researched': len(successful),
                'total_time': elapsed,
                'average_time_per_topic': elapsed / len(topics)
            }
        }
    
    def _combine_research(self, results: List[Result]) -> Dict:
        """
        Combine research results from multiple topics.
        """
        combined = {
            'key_facts': [],
            'sources': [],
            'themes': []
        }
        
        for result in results:
            context = result.output
            combined['key_facts'].extend(context.get('key_facts', []))
            combined['sources'].extend(context.get('sources', []))
            combined['themes'].extend(context.get('themes', []))
        
        return combined


class AdaptiveQualityWorkflow:
    """
    Workflow that adapts quality threshold based on complexity.
    """
    
    def __init__(self, orchestrator: DocumentOrchestrator):
        self.orchestrator = orchestrator
        self.base_threshold = 0.85
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute workflow with adaptive quality threshold.
        """
        # Analyze complexity
        complexity = await self._analyze_complexity(request)
        
        # Adjust threshold
        adjusted_threshold = self._adjust_threshold(complexity)
        
        print(f"\nComplexity: {complexity}")
        print(f"Adjusted threshold: {adjusted_threshold:.3f}")
        
        # Update orchestrator config
        original_threshold = self.orchestrator.config.quality_threshold
        self.orchestrator.config.quality_threshold = adjusted_threshold
        
        # Execute document creation
        result = await self.orchestrator.create_document(
            topic=request['topic'],
            requirements=request['requirements']
        )
        
        # Restore original threshold
        self.orchestrator.config.quality_threshold = original_threshold
        
        return result
    
    async def _analyze_complexity(self, request: Dict) -> float:
        """
        Analyze request complexity (0-1, higher = more complex).
        """
        complexity_factors = [
            len(request.get('requirements', {}).get('focus_areas', [])) / 10,
            1.0 if request.get('requirements', {}).get('depth') == 'advanced' else 0.5,
            len(request.get('topic', '').split()) / 20
        ]
        
        return min(sum(complexity_factors) / len(complexity_factors), 1.0)
    
    def _adjust_threshold(self, complexity: float) -> float:
        """
        Adjust quality threshold based on complexity.
        Lower threshold for more complex topics.
        """
        adjustment = -0.1 * complexity
        return max(self.base_threshold + adjustment, 0.70)


async def main():
    """
    Advanced workflow examples.
    """
    print("=" * 60)
    print("Advanced Workflow Examples")
    print("=" * 60)
    
    # Setup
    research_agent = ResearchAgent(model="gpt-4")
    writing_agent = WritingAgent(model="gpt-4")
    editing_agent = EditingAgent(model="gpt-4")
    verification_agent = VerificationAgent(model="gpt-4")
    
    orchestrator = DocumentOrchestrator(
        agents={
            'research': research_agent,
            'writing': writing_agent,
            'editing': editing_agent,
            'verification': verification_agent
        },
        config=OrchestratorConfig(
            max_iterations=3,
            enable_parallel_processing=True
        )
    )
    
    # Add performance monitoring
    monitor = PerformanceMonitor()
    
    # Example 1: Parallel Research Workflow
    print("\n" + "=" * 60)
    print("Example 1: Parallel Research")
    print("=" * 60)
    
    parallel_workflow = ParallelResearchWorkflow(orchestrator)
    
    research_topics = [
        "Quantum computing basics",
        "Quantum algorithms",
        "Quantum cryptography",
        "Quantum error correction"
    ]
    
    research_result = await parallel_workflow.execute(research_topics)
    
    if research_result['success']:
        print(f"\n✓ Found {len(research_result['context']['key_facts'])} facts")
        print(f"✓ From {len(research_result['context']['sources'])} sources")
    
    # Example 2: Adaptive Quality Workflow
    print("\n" + "=" * 60)
    print("Example 2: Adaptive Quality Threshold")
    print("=" * 60)
    
    adaptive_workflow = AdaptiveQualityWorkflow(orchestrator)
    
    complex_request = {
        'topic': 'Quantum Computing Applications in Cryptography',
        'requirements': {
            'length': '3000 words',
            'depth': 'advanced',
            'focus_areas': [
                'Shor\'s algorithm',
                'post-quantum cryptography',
                'quantum key distribution',
                'lattice-based cryptography',
                'implementation challenges'
            ]
        }
    }
    
    result = await adaptive_workflow.execute(complex_request)
    
    if result.success:
        print(f"\n✓ Complex document generated")
        print(f"  Quality: {result.quality_score:.3f}")
        print(f"  Iterations: {result.iterations}")
    
    # Example 3: Custom Workflow with WorkflowBuilder
    print("\n" + "=" * 60)
    print("Example 3: Custom Workflow Builder")
    print("=" * 60)
    
    # Build custom workflow
    workflow = WorkflowBuilder() \
        .add_stage("research", parallel=True) \
        .add_stage("outline") \
        .add_stage("writing", parallel=True, chunks=3) \
        .add_stage("editing") \
        .add_condition("quality_check", threshold=0.9) \
        .add_stage("verification") \
        .add_loop(max_iterations=2) \
        .build()
    
    print(f"\n✓ Custom workflow created with {len(workflow.stages)} stages")
    
    # Display metrics
    print("\n" + "=" * 60)
    print("Performance Summary")
    print("=" * 60)
    
    agent_metrics = orchestrator.get_agent_metrics()
    
    for agent_name, metrics in agent_metrics.items():
        print(f"\n{agent_name.upper()}:")
        print(f"  Tasks completed: {metrics.tasks_completed}")
        print(f"  Tasks failed: {metrics.tasks_failed}")
        print(f"  Total time: {metrics.total_processing_time:.2f}s")
        if metrics.tasks_completed > 0:
            avg_time = metrics.total_processing_time / metrics.tasks_completed
            print(f"  Average time: {avg_time:.2f}s")
    
    # Cleanup
    await orchestrator.shutdown()
    print("\n✓ Examples complete")


if __name__ == "__main__":
    # Import Task for parallel workflow
    from madf.models import Task, Result
    
    asyncio.run(main())
