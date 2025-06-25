#!/usr/bin/env python
"""
Setup script for Energy Profile Calculator package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="energy-profile-calculator",
    version="1.0.0",
    author="Energy Profile Calculator Team",
    author_email="your.email@example.com",
    description="A modular package for calculating adsorption energy profiles on surfaces using ML and DFT methods",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/energy-profile-calculator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "energy-profile=energy_profile_calculator.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "energy_profile_calculator": ["data/*", "examples/*"],
    },
)
