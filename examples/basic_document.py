"""Basic document generation example."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from madf import DocumentOrchestrator, DocumentRequest, OrchestratorConfig
from madf.utils.logging import setup_logging


async def main():
    """Generate a basic document."""
    # Setup logging
    setup_logging(level="INFO")
    
    # Create orchestrator with default config
    config = OrchestratorConfig(
        max_agents=10,
        quality_threshold=0.85
    )
    orchestrator = DocumentOrchestrator(config)
    
    # Create document request
    request = DocumentRequest(
        topic="The Future of Renewable Energy",
        document_type="article",
        target_length=2000,
        style="technical",
        audience="industry professionals",
        requirements=[
            "Include current trends",
            "Discuss challenges and opportunities",
            "Provide future predictions"
        ]
    )
    
    print(f"\n{'='*60}")
    print(f"Creating document: {request.topic}")
    print(f"Target length: {request.target_length} words")
    print(f"{'='*60}\n")
    
    # Generate document
    document = await orchestrator.create_document(request)
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Document creation complete!")
    print(f"{'='*60}")
    print(f"Title: {document.title}")
    print(f"Status: {document.status.value}")
    print(f"Quality Score: {document.quality_score:.2f}")
    print(f"Word Count: {document.word_count}")
    print(f"Sections: {len(document.sections)}")
    
    # Save document
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Save as Markdown
    md_path = output_dir / f"{document.id}.md"
    with open(md_path, 'w') as f:
        f.write(document.to_markdown())
    print(f"\nSaved to: {md_path}")
    
    # Save as HTML
    html_path = output_dir / f"{document.id}.html"
    with open(html_path, 'w') as f:
        f.write(document.to_html())
    print(f"Saved to: {html_path}")
    
    # Print agent metrics
    print(f"\n{'='*60}")
    print("Agent Metrics:")
    print(f"{'='*60}")
    metrics = orchestrator.get_agent_metrics()
    for agent_name, agent_metrics in metrics.items():
        print(f"\n{agent_name.upper()}:")
        print(f"  Tasks completed: {agent_metrics['metrics']['tasks_completed']}")
        print(f"  Tasks failed: {agent_metrics['metrics']['tasks_failed']}")
        print(f"  Total time: {agent_metrics['metrics']['total_time']:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())