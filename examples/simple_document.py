#!/usr/bin/env python3
"""
Simple document creation example.

Demonstrates basic usage of the Multi-Agent Document Framework
to create a simple document with minimal configuration.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from multi_agent_framework import (
    Agent,
    Coordinator,
    Config,
    WorkflowMode,
)


def create_simple_document_sync():
    """
    Create a simple document using synchronous API.
    """
    print("=" * 60)
    print("Simple Document Creation Example")
    print("=" * 60)
    print()
    
    # Create configuration
    config = Config()
    config.setup_logging()
    
    # Create agents
    print("Creating agents...")
    researcher = Agent(
        agent_id="researcher_01",
        role="researcher",
        capabilities=["web_search", "data_analysis"],
        model="gpt-4",
    )
    
    writer = Agent(
        agent_id="writer_01",
        role="writer",
        capabilities=["content_creation", "storytelling"],
        model="gpt-4",
    )
    
    editor = Agent(
        agent_id="editor_01",
        role="editor",
        capabilities=["proofreading", "style_improvement"],
        model="gpt-4",
    )
    
    print(f"✓ Created {researcher}")
    print(f"✓ Created {writer}")
    print(f"✓ Created {editor}")
    print()
    
    # Initialize coordinator
    print("Initializing coordinator...")
    coordinator = Coordinator(
        agents=[researcher, writer, editor],
        workflow_mode=WorkflowMode.SEQUENTIAL,
        config=config,
    )
    print(f"✓ Coordinator initialized with {len(coordinator.agents)} agents")
    print()
    
    # Create document
    print("Creating document...")
    document = coordinator.create_document(
        topic="The Future of Artificial Intelligence",
        requirements={
            "length": "1500 words",
            "style": "technical but accessible",
            "sections": [
                "Introduction",
                "Current State of AI",
                "Emerging Trends",
                "Challenges and Opportunities",
                "Conclusion",
            ],
        },
    )
    
    print("✓ Document created successfully!")
    print()
    
    # Display results
    print("=" * 60)
    print("Document Information")
    print("=" * 60)
    print(f"Title: {document.title}")
    print(f"Status: {document.status}")
    print(f"Word Count: {document.word_count}")
    print(f"Sections: {document.section_count}")
    print(f"Created: {document.created_at}")
    print()
    
    # Display content preview
    print("=" * 60)
    print("Content Preview")
    print("=" * 60)
    print(document.content[:500] + "...")
    print()
    
    # Save document
    output_file = "output/simple_document.md"
    Path("output").mkdir(exist_ok=True)
    
    with open(output_file, "w") as f:
        f.write(document.to_markdown())
    
    print(f"✓ Document saved to: {output_file}")
    print()
    
    return document


async def create_simple_document_async():
    """
    Create a simple document using asynchronous API.
    """
    print("=" * 60)
    print("Simple Document Creation Example (Async)")
    print("=" * 60)
    print()
    
    # Create agents
    agents = [
        Agent(role="researcher", capabilities=["web_search"]),
        Agent(role="writer", capabilities=["content_creation"]),
        Agent(role="editor", capabilities=["proofreading"]),
    ]
    
    # Initialize coordinator
    coordinator = Coordinator(
        agents=agents,
        workflow_mode=WorkflowMode.SEQUENTIAL,
    )
    
    print("Creating document asynchronously...")
    
    # Create document
    document = await coordinator.create_document_async(
        topic="Machine Learning in Healthcare",
        requirements={
            "length": "2000 words",
            "style": "academic",
            "sections": [
                "Abstract",
                "Introduction",
                "Methods",
                "Applications",
                "Discussion",
                "Conclusion",
            ],
        },
    )
    
    print("✓ Document created!")
    print(f"Word count: {document.word_count}")
    print(f"Sections: {document.section_count}")
    
    return document


def main():
    """
    Main entry point.
    """
    # Run synchronous example
    document = create_simple_document_sync()
    
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()