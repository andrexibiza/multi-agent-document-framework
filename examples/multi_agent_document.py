#!/usr/bin/env python3
"""
Advanced multi-agent document creation example.

Demonstrates advanced features including:
- Multiple specialized agents
- Verification system
- Iterative refinement
- Custom workflow
- Progress tracking
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from multi_agent_framework import (
    Agent,
    Coordinator,
    Config,
    VerificationSystem,
    WorkflowMode,
)


async def create_research_paper():
    """
    Create a comprehensive research paper using multiple agents
    with verification and iterative refinement.
    """
    print("=" * 70)
    print("Advanced Multi-Agent Document Creation")
    print("Creating Research Paper with Verification")
    print("=" * 70)
    print()
    
    # Load configuration
    config = Config()
    config.coordinator.max_iterations = 3
    config.verification.enabled = True
    config.verification.min_quality_score = 0.85
    config.setup_logging()
    
    # Create specialized agent team
    print("Assembling agent team...")
    
    agents = [
        Agent(
            agent_id="researcher_01",
            role="researcher",
            capabilities=["literature_review", "data_collection", "web_search"],
            model="gpt-4",
            temperature=0.3,  # Lower for more focused research
        ),
        Agent(
            agent_id="analyst_01",
            role="analyst",
            capabilities=["data_analysis", "statistical_modeling"],
            model="gpt-4",
            temperature=0.2,  # Very focused for analysis
        ),
        Agent(
            agent_id="writer_01",
            role="writer",
            capabilities=["academic_writing", "technical_writing"],
            model="gpt-4",
            temperature=0.7,  # Balanced for writing
        ),
        Agent(
            agent_id="fact_checker_01",
            role="fact_checker",
            capabilities=["fact_verification", "citation_management"],
            model="gpt-4",
            temperature=0.1,  # Very precise for fact-checking
        ),
        Agent(
            agent_id="editor_01",
            role="editor",
            capabilities=["proofreading", "style_improvement", "formatting"],
            model="gpt-4",
            temperature=0.5,  # Moderate for editing
        ),
    ]
    
    for agent in agents:
        print(f"  ✓ {agent.role.capitalize()} agent ready (ID: {agent.agent_id})")
    print()
    
    # Setup verification system
    print("Configuring verification system...")
    verification = VerificationSystem(
        checks=[
            "quality",
            "factual_accuracy",
            "consistency",
            "grammar",
            "citations",
        ],
        min_overall_score=config.verification.min_quality_score,
    )
    print(f"  ✓ Verification enabled with {len(verification.enabled_checks)} checks")
    print(f"  ✓ Minimum quality score: {config.verification.min_quality_score}")
    print()
    
    # Initialize coordinator with verification
    print("Initializing coordinator...")
    coordinator = Coordinator(
        agents=agents,
        workflow_mode=WorkflowMode.SEQUENTIAL,
        verification_system=verification,
        max_iterations=config.coordinator.max_iterations,
        config=config,
    )
    print(f"  ✓ Coordinator ready (mode: {coordinator.workflow_mode.value})")
    print(f"  ✓ Max refinement iterations: {coordinator.max_iterations}")
    print()
    
    # Define research paper requirements
    requirements = {
        "type": "research_paper",
        "length": "8000 words",
        "citation_style": "IEEE",
        "sections": [
            "Abstract",
            "Introduction",
            "Literature Review",
            "Methodology",
            "Results and Analysis",
            "Discussion",
            "Limitations",
            "Future Work",
            "Conclusion",
            "References",
        ],
        "keywords": [
            "multi-agent systems",
            "document generation",
            "artificial intelligence",
            "natural language processing",
        ],
    }
    
    # Create document
    print("Starting document creation...")
    print("-" * 70)
    print()
    
    topic = "Multi-Agent Systems for Automated Document Generation"
    
    try:
        document = await coordinator.create_document_async(
            topic=topic,
            requirements=requirements,
        )
        
        print()
        print("-" * 70)
        print("✓ Document creation completed successfully!")
        print()
        
        # Display results
        print("=" * 70)
        print("Document Statistics")
        print("=" * 70)
        print(f"Title: {document.title}")
        print(f"Status: {document.status}")
        print(f"Word Count: {document.word_count:,}")
        print(f"Sections: {document.section_count}")
        print(f"Verification Score: {document.verification_score:.2f}" if document.verification_score else "Not verified")
        print(f"Contributors: {len(document.contributors)}")
        print(f"Versions: {len(document.versions)}")
        print()
        
        # Workflow statistics
        workflow_status = coordinator.get_workflow_status()
        print("=" * 70)
        print("Workflow Statistics")
        print("=" * 70)
        print(f"Total Steps: {workflow_status['total_steps']}")
        print(f"Completed: {workflow_status['completed_steps']}")
        print(f"Failed: {workflow_status['failed_steps']}")
        print(f"Active Agents: {workflow_status['active_agents']}")
        print()
        
        # Agent statistics
        print("=" * 70)
        print("Agent Performance")
        print("=" * 70)
        for agent in agents:
            status = agent.get_status()
            print(f"{agent.role.capitalize()}:")
            print(f"  Tasks Completed: {status['completed_tasks']}")
            print(f"  Tasks Failed: {status['failed_tasks']}")
            print(f"  Success Rate: {status['completed_tasks'] / status['total_tasks'] * 100:.1f}%" if status['total_tasks'] > 0 else "  N/A")
        print()
        
        # Save document in multiple formats
        print("Saving document...")
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Save as Markdown
        md_file = output_dir / "research_paper.md"
        with open(md_file, "w") as f:
            f.write(document.to_markdown())
        print(f"  ✓ Markdown: {md_file}")
        
        # Save as JSON
        json_file = output_dir / "research_paper.json"
        with open(json_file, "w") as f:
            f.write(document.to_json())
        print(f"  ✓ JSON: {json_file}")
        
        print()
        print("=" * 70)
        print("Research paper creation completed successfully!")
        print("=" * 70)
        
        return document
        
    except Exception as e:
        print()
        print(f"✗ Error during document creation: {e}")
        raise


async def create_technical_documentation():
    """
    Create technical documentation using parallel workflow.
    """
    print("=" * 70)
    print("Technical Documentation Creation")
    print("Using Parallel Workflow for Speed")
    print("=" * 70)
    print()
    
    # Create multiple writer agents for parallel execution
    writers = [
        Agent(role="writer", capabilities=["technical_writing"]),
        Agent(role="writer", capabilities=["technical_writing"]),
        Agent(role="writer", capabilities=["technical_writing"]),
    ]
    
    editor = Agent(role="editor", capabilities=["proofreading", "formatting"])
    
    # Parallel coordinator for writers
    coordinator = Coordinator(
        agents=writers + [editor],
        workflow_mode=WorkflowMode.PARALLEL,
    )
    
    # Custom workflow: parallel writing, then sequential editing
    workflow_steps = [
        {
            "agent_id": writers[0].agent_id,
            "task_type": "write",
            "description": "Write Getting Started section",
            "requirements": {"section": "getting_started"},
        },
        {
            "agent_id": writers[1].agent_id,
            "task_type": "write",
            "description": "Write API Reference section",
            "requirements": {"section": "api_reference"},
        },
        {
            "agent_id": writers[2].agent_id,
            "task_type": "write",
            "description": "Write Examples section",
            "requirements": {"section": "examples"},
        },
    ]
    
    document = await coordinator.create_document_async(
        topic="Product API Documentation",
        requirements={"format": "technical"},
        workflow_steps=workflow_steps,
    )
    
    print(f"✓ Technical documentation created: {document.word_count} words")
    return document


def main():
    """
    Main entry point.
    """
    # Run research paper creation
    document = asyncio.run(create_research_paper())
    
    # Optionally run technical documentation example
    # asyncio.run(create_technical_documentation())


if __name__ == "__main__":
    main()