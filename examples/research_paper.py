"""Academic research paper generation example."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from madf import DocumentOrchestrator, DocumentRequest
from madf.utils.config import OrchestratorConfig, ModelConfig, AgentConfig
from madf.utils.logging import setup_logging


async def main():
    """Generate an academic research paper."""
    setup_logging(level="INFO")
    
    # Custom configuration for academic writing
    research_config = AgentConfig(
        name="research",
        model_config=ModelConfig(
            model="gpt-4",
            temperature=0.2  # Lower temperature for factual accuracy
        ),
        timeout=180
    )
    
    writing_config = AgentConfig(
        name="writing",
        model_config=ModelConfig(
            model="gpt-4",
            temperature=0.6  # Moderate temperature for academic style
        ),
        timeout=240
    )
    
    config = OrchestratorConfig(
        max_agents=10,
        quality_threshold=0.90,  # Higher threshold for academic work
        research_config=research_config,
        writing_config=writing_config
    )
    
    orchestrator = DocumentOrchestrator(config)
    
    # Create research paper request
    request = DocumentRequest(
        topic="Multi-Agent Systems in Artificial Intelligence: A Comprehensive Review",
        document_type="paper",
        target_length=5000,
        style="formal",
        audience="academic researchers",
        requirements=[
            "Include abstract",
            "Literature review section",
            "Technical methodology",
            "Future research directions",
            "Proper academic structure"
        ],
        references=[
            "Recent advances in multi-agent reinforcement learning",
            "Coordination mechanisms in distributed AI systems"
        ]
    )
    
    print(f"\nGenerating research paper: {request.topic}")
    print(f"Target length: {request.target_length} words\n")
    
    # Generate paper
    document = await orchestrator.create_document(request)
    
    # Display results
    print(f"\n{'='*70}")
    print(f"Research Paper Generated")
    print(f"{'='*70}")
    print(f"Quality Score: {document.quality_score:.2%}")
    print(f"Word Count: {document.word_count:,}")
    print(f"\nSections ({len(document.sections)}):")
    for i, section in enumerate(document.sections, 1):
        print(f"  {i}. {section.title} ({section.word_count()} words)")
    
    # Save
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    filename = "research_paper"
    md_path = output_dir / f"{filename}.md"
    with open(md_path, 'w') as f:
        f.write(document.to_markdown())
    
    print(f"\nSaved to: {md_path}")


if __name__ == "__main__":
    asyncio.run(main())