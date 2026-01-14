from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="multi-agent-document-framework",
    version="1.0.0",
    author="Andrex Ibiza",
    author_email="contact@example.com",
    description="A production-ready framework for building multi-agent document creation systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andrexibiza/multi-agent-document-framework",
    project_urls={
        "Bug Tracker": "https://github.com/andrexibiza/multi-agent-document-framework/issues",
        "Documentation": "https://github.com/andrexibiza/multi-agent-document-framework/docs",
        "Source Code": "https://github.com/andrexibiza/multi-agent-document-framework",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "madf=multi_agent_framework.cli:main",
        ],
    },
)