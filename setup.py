"""Setup script for Multi-Agent Document Framework."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="multi-agent-document-framework",
    version="0.1.0",
    author="Axl Ibiza",
    author_email="",
    description="A production-ready framework for intelligent multi-agent document creation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andrexibiza/multi-agent-document-framework",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.0.0",
        "tiktoken>=0.5.0",
        "aiohttp>=3.9.0",
        "aiofiles>=23.0.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "structlog>=23.0.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "ipython>=8.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "database": [
            "psycopg2-binary>=2.9.0",
            "redis>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "madf=madf.cli:main",
        ],
    },
)