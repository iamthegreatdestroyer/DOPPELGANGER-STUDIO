"""
DOPPELGANGER STUDIO - Setup Configuration

AI-powered application that transforms classic TV show concepts into
animated reimaginings in new contexts.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="doppelganger-studio",
    version="0.1.0-alpha",
    author="[Your Name]",
    author_email="[your-email@example.com]",
    description="AI-driven content transformation and multi-dimensional storytelling system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/doppelganger-studio",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/doppelganger-studio/issues",
        "Documentation": "https://doppelganger-studio.readthedocs.io",
        "Source Code": "https://github.com/yourusername/doppelganger-studio",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "anthropic>=0.7.0",
        "openai>=1.3.0",
        "asyncpg>=0.29.0",
        "motor>=3.3.2",
        "redis>=5.0.1",
        "aiohttp>=3.9.1",
        "PyQt6>=6.6.1",
        "numpy>=1.26.2",
        "torch>=2.1.0",
        "transformers>=4.35.0",
        "ffmpeg-python>=0.2.0",
        "Pillow>=10.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "ipython>=8.18.1",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=2.0.0",
        ],
        "ml": [
            "diffusers>=0.24.0",
            "clip-by-openai>=1.0",
            "sentence-transformers>=2.2.2",
        ],
        "animation": [
            "manim>=0.18.0",
            "opencv-python>=4.8.1.78",
        ],
    },
    entry_points={
        "console_scripts": [
            "doppelganger=src.cli:main",
            "doppelganger-scrape=src.services.asset_manager.cli:scrape",
            "doppelganger-generate=src.services.creative.cli:generate",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json", "*.sql", "*.js"],
    },
    zip_safe=False,
    keywords=[
        "ai",
        "artificial-intelligence",
        "content-generation",
        "animation",
        "video-generation",
        "nlp",
        "computer-vision",
        "transformers",
        "llm",
    ],
    license="AGPL-3.0",
)
