"""
Basic usage example of the Multi-Agent Document Framework.

This example demonstrates how to:
1. Set up agents
2. Configure the orchestrator
3. Generate a document
4. Access results and metrics
"""

import asyncio
import os
from dotenv import load_dotenv

from madf import (
    DocumentOrchestrator,
    OrchestratorConfig,
    ResearchAgent,
    WritingAgent,
    EditingAgent,
    VerificationAgent
)

# Load environment variables
load_dotenv()


async def main():
    """
    Basic document generation workflow.
    """
    print("=" * 60)
    print("Multi-Agent Document Framework - Basic Example")
    print("=" * 60)
    
    # Step 1: Initialize agents
    print("\n[1/4] Initializing agents...")
    
    research_agent = ResearchAgent(
        model="gpt-4",
        config={
            'temperature': 0.3,
            'max_sources': 10,
            'search_api_key': os.getenv('SEARCH_API_KEY')
        }
    )
    
    writing_agent = WritingAgent(
        model="gpt-4",
        config={
            'temperature': 0.7,
            'max_tokens': 2000
        }
    )
    
    editing_agent = EditingAgent(
        model="gpt-4",
        config={
            'temperature': 0.5
        }
    )
    
    verification_agent = VerificationAgent(
        model="gpt-4",
        config={
            'temperature': 0.2
        }
    )
    
    print("✓ Agents initialized successfully")
    
    # Step 2: Configure orchestrator
    print("\n[2/4] Configuring orchestrator...")
    
    config = OrchestratorConfig(
        max_iterations=3,
        quality_threshold=0.85,
        enable_verification=True,
        enable_parallel_processing=True,
        research_timeout=120,
        writing_timeout=180,
        editing_timeout=120,
        verification_timeout=60
    )
    
    orchestrator = DocumentOrchestrator(
        agents={
            'research': research_agent,
            'writing': writing_agent,
            'editing': editing_agent,
            'verification': verification_agent
        },
        config=config
    )
    
    print("✓ Orchestrator configured successfully")
    
    # Step 3: Generate document
    print("\n[3/4] Generating document...")
    print("Topic: The Impact of Artificial Intelligence on Healthcare")
    print("This may take a few minutes...\n")
    
    result = await orchestrator.create_document(
        topic="The Impact of Artificial Intelligence on Healthcare",
        requirements={
            "length": "2000-3000 words",
            "tone": "professional",
            "style": "informative",
            "target_audience": "healthcare professionals",
            "include_citations": True,
            "depth": "intermediate",
            "focus_areas": [
                "diagnostic imaging",
                "patient care",
                "drug discovery",
                "electronic health records"
            ]
        }
    )
    
    # Step 4: Display results
    print("\n[4/4] Document Generation Complete!")
    print("=" * 60)
    
    if result.success:
        print(f"✓ Status: SUCCESS")
        print(f"✓ Document ID: {result.document_id}")
        print(f"✓ Quality Score: {result.quality_score:.3f}")
        print(f"✓ Iterations: {result.iterations}")
        print(f"✓ Word Count: {len(result.content.split())} words")
        
        print("\n" + "="  * 60)
        print("DOCUMENT CONTENT")
        print("=" * 60)
        print(result.content[:500] + "...\n")
        
        # Display metrics
        print("\n" + "=" * 60)
        print("PERFORMANCE METRICS")
        print("=" * 60)
        
        if 'research_metrics' in result.metrics:
            print(f"Research: {result.metrics['research_metrics']}")
        if 'writing_metrics' in result.metrics:
            print(f"Writing: {result.metrics['writing_metrics']}")
        if 'editing_metrics' in result.metrics:
            print(f"Editing: {result.metrics['editing_metrics']}")
        
        # Save document
        output_file = f"output_{result.document_id}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.content)
        print(f"\n✓ Document saved to: {output_file}")
        
    else:
        print(f"✗ Status: FAILED")
        print(f"✗ Errors: {result.errors}")
    
    # Cleanup
    await orchestrator.shutdown()
    print("\n✓ Orchestrator shut down")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
