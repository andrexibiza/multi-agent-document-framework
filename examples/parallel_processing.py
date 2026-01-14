"""Parallel document generation example."""

import asyncio
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from madf import DocumentOrchestrator, DocumentRequest, OrchestratorConfig
from madf.utils.logging import setup_logging


async def main():
    """Generate multiple documents in parallel."""
    setup_logging(level="INFO")
    
    # Configure for parallel processing
    config = OrchestratorConfig(
        max_agents=20,  # Increase agent pool
        enable_parallel=True,
        max_concurrent_tasks=10
    )
    
    orchestrator = DocumentOrchestrator(config)
    
    # Create multiple document requests
    topics = [
        "The Impact of AI on Healthcare",
        "Sustainable Urban Development",
        "Quantum Computing Applications",
        "Future of Remote Work",
        "Blockchain in Supply Chain Management"
    ]
    
    requests = [
        DocumentRequest(
            topic=topic,
            document_type="article",
            target_length=1500,
            style="professional",
            audience="business professionals"
        )
        for topic in topics
    ]
    
    print(f"\n{'='*70}")
    print(f"Parallel Document Generation")
    print(f"{'='*70}")
    print(f"\nGenerating {len(requests)} documents in parallel...\n")
    
    # Time the parallel generation
    start_time = time.time()
    
    # Create all documents in parallel
    tasks = [orchestrator.create_document(req) for req in requests]
    documents = await asyncio.gather(*tasks, return_exceptions=True)
    
    elapsed_time = time.time() - start_time
    
    # Process results
    successful = [doc for doc in documents if not isinstance(doc, Exception)]
    failed = [doc for doc in documents if isinstance(doc, Exception)]
    
    print(f"\n{'='*70}")
    print(f"Generation Complete")
    print(f"{'='*70}")
    print(f"\nTotal time: {elapsed_time:.2f} seconds")
    print(f"Average time per document: {elapsed_time/len(requests):.2f} seconds")
    print(f"Successful: {len(successful)}/{len(requests)}")
    print(f"Failed: {len(failed)}/{len(requests)}")
    
    # Display successful documents
    print(f"\n{'='*70}")
    print(f"Document Details")
    print(f"{'='*70}")
    
    for i, doc in enumerate(successful, 1):
        print(f"\n{i}. {doc.title}")
        print(f"   Quality: {doc.quality_score:.2%}")
        print(f"   Words: {doc.word_count:,}")
        print(f"   Sections: {len(doc.sections)}")
    
    # Save all documents
    output_dir = Path("output/batch")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for doc in successful:
        filename = doc.title.lower().replace(" ", "_")[:50]
        md_path = output_dir / f"{filename}.md"
        with open(md_path, 'w') as f:
            f.write(document.to_markdown())
    
    print(f"\nAll documents saved to: {output_dir}")
    
    # Show resource utilization
    print(f"\n{'='*70}")
    print(f"Resource Utilization")
    print(f"{'='*70}")
    stats = orchestrator.resource_manager.get_stats()
    print(f"Peak utilization: {stats['peak_usage']}/{stats['max_agents']} agents")
    print(f"Total allocations: {stats['total_allocations']}")
    print(f"Average wait time: {stats['avg_wait_time']:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())