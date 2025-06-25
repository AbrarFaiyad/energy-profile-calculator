"""
Energy Profile Calculator Package

A modular package for calculating adsorption energy profiles on surfaces 
using machine learning (OMAT/OMC) and DFT methods.
"""

__version__ = "1.0.0"
__author__ = "Energy Profile Calculator Team"
__email__ = "your.email@example.com"

from .core import EnergyProfileCalculator
from .adsorbants import AdsorbantLibrary
from .surfaces import SurfaceBuilder
from .calculators import MLCalculatorManager, DFTCalculatorManager
from .plotting import EnergyProfilePlotter
from .utils import detect_cpu_cores, save_results, load_config

__all__ = [
    "EnergyProfileCalculator",
    "AdsorbantLibrary", 
    "SurfaceBuilder",
    "MLCalculatorManager",
    "DFTCalculatorManager",
    "EnergyProfilePlotter",
    "detect_cpu_cores",
    "save_results",
    "load_config",
]
