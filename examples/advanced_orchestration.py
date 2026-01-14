"""Advanced orchestration example with custom workflows."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from madf import DocumentOrchestrator, DocumentRequest, OrchestratorConfig
from madf.coordination import WorkflowBuilder
from madf.utils.logging import setup_logging


async def main():
    """Demonstrate advanced orchestration features."""
    setup_logging(level="INFO")
    
    # Load configuration from file
    config = OrchestratorConfig.from_yaml("config/default.yaml")
    
    # Customize for this use case
    config.quality_threshold = 0.88
    config.max_concurrent_tasks = 8
    
    orchestrator = DocumentOrchestrator(config)
    
    # Create custom workflow
    custom_workflow = (WorkflowBuilder(name="technical_doc")
        .add_stage("research", "research")
        .add_stage("writing", "writing", depends_on=["research"])
        .add_stage("editing", "editing", depends_on=["writing"])
        .add_stage("verification", "verification", depends_on=["editing"])
        .set_metadata("requires_technical_accuracy", True)
        .set_metadata("include_code_examples", True)
        .build())
    
    # Register custom workflow
    orchestrator.workflow_manager.register_workflow("technical_doc", custom_workflow)
    
    # Create multiple document requests
    requests = [
        DocumentRequest(
            topic="Introduction to Kubernetes",
            document_type="technical_doc",
            target_length=3000,
            style="technical",
            audience="software engineers",
            requirements=["Include architecture overview", "Deployment examples"]
        ),
        DocumentRequest(
            topic="Best Practices for API Design",
            document_type="technical_doc",
            target_length=2500,
            style="technical",
            audience="backend developers",
            requirements=["RESTful principles", "Authentication patterns"]
        )
    ]
    
    print(f"\n{'='*70}")
    print(f"Advanced Orchestration Example")
    print(f"{'='*70}")
    print(f"\nGenerating {len(requests)} documents with custom workflow...\n")
    
    # Generate documents in parallel
    tasks = [orchestrator.create_document(req) for req in requests]
    documents = await asyncio.gather(*tasks)
    
    # Display results
    print(f"\n{'='*70}")
    print(f"All Documents Generated")
    print(f"{'='*70}")
    
    for i, doc in enumerate(documents, 1):
        print(f"\nDocument {i}: {doc.title}")
        print(f"  Status: {doc.status.value}")
        print(f"  Quality: {doc.quality_score:.2%}")
        print(f"  Words: {doc.word_count:,}")
        print(f"  Sections: {len(doc.sections)}")
    
    # Save configuration for future use
    config.save_to_yaml("config/custom_config.yaml")
    print(f"\nConfiguration saved to: config/custom_config.yaml")


if __name__ == "__main__":
    asyncio.run(main())