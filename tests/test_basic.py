"""
Basic tests for Energy Profile Calculator package
"""

import pytest
import numpy as np
from pathlib import Path

# Import package components
from energy_profile_calculator import (
    EnergyProfileCalculator,
    AdsorbantLibrary, 
    SurfaceBuilder,
    detect_cpu_cores
)

class TestAdsorbantLibrary:
    """Test adsorbant library functionality."""
    
    def test_library_initialization(self):
        library = AdsorbantLibrary()
        assert len(library.list_adsorbants()) > 0
    
    def test_get_water_molecule(self):
        library = AdsorbantLibrary()
        position = (0, 0, 0)
        water = library.get_adsorbant('H2O', position, 'flat')
        
        assert len(water) == 3  # O + 2H
        symbols = water.get_chemical_symbols()
        assert symbols.count('O') == 1
        assert symbols.count('H') == 2
    
    def test_get_hydrogen_atom(self):
        library = AdsorbantLibrary()
        position = (0, 0, 0)
        hydrogen = library.get_adsorbant('H', position)
        
        assert len(hydrogen) == 1
        assert hydrogen.get_chemical_symbols()[0] == 'H'
    
    def test_invalid_adsorbant(self):
        library = AdsorbantLibrary()
        with pytest.raises(ValueError):
            library.get_adsorbant('INVALID', (0, 0, 0))


class TestSurfaceBuilder:
    """Test surface builder functionality."""
    
    def test_builder_initialization(self):
        builder = SurfaceBuilder()
        assert len(builder.list_supported_materials()) > 0
    
    def test_build_au111_surface(self):
        builder = SurfaceBuilder()
        surface = builder.build_surface(
            material='Au',
            miller_indices=(1, 1, 1),
            size=(2, 2, 3),
            vacuum=10.0
        )
        
        assert len(surface) == 12  # 2x2x3 = 12 atoms
        assert all(symbol == 'Au' for symbol in surface.get_chemical_symbols())
    
    def test_get_surface_info(self):
        builder = SurfaceBuilder()
        surface = builder.build_surface('Au', (1, 1, 1), (2, 2, 2))
        info = builder.get_surface_info(surface)
        
        assert 'n_atoms' in info
        assert 'elements' in info
        assert 'layers' in info
        assert info['n_atoms'] == 8


class TestUtilities:
    """Test utility functions."""
    
    def test_detect_cpu_cores(self):
        cores = detect_cpu_cores()
        assert isinstance(cores, int)
        assert cores > 0
    
    def test_create_example_config(self):
        from energy_profile_calculator.utils import create_example_config
        config = create_example_config()
        
        assert 'surface' in config
        assert 'adsorbant' in config
        assert 'calculation' in config


class TestEnergyProfileCalculator:
    """Test main calculator class."""
    
    def test_calculator_initialization(self):
        calc = EnergyProfileCalculator()
        assert calc.adsorbant_library is not None
        assert calc.surface_builder is not None
    
    def test_setup_surface(self):
        calc = EnergyProfileCalculator()
        calc.setup_surface('Au', (1, 1, 1), (2, 2, 2))
        
        assert calc.surface is not None
        assert calc.surface_name == 'Au(1,1,1)'
    
    def test_surface_setup_required(self):
        calc = EnergyProfileCalculator()
        
        with pytest.raises(RuntimeError):
            # Should fail if surface not set up
            calc.calculate_energy_profile('H')


def run_basic_functionality_test():
    """
    Run a basic functionality test without external dependencies.
    This tests the core package structure and basic operations.
    """
    print("Running basic functionality test...")
    
    # Test 1: Package imports
    try:
        from energy_profile_calculator import EnergyProfileCalculator
        print("✅ Package imports working")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Basic initialization
    try:
        calc = EnergyProfileCalculator()
        print("✅ Calculator initialization working")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False
    
    # Test 3: Surface setup
    try:
        calc.setup_surface('Au', (1, 1, 1), (2, 2, 2))
        print("✅ Surface setup working")
    except Exception as e:
        print(f"❌ Surface setup failed: {e}")
        return False
    
    # Test 4: Adsorbant library
    try:
        library = calc.adsorbant_library
        adsorbants = library.list_adsorbants()
        water = library.get_adsorbant('H2O', (0, 0, 0), 'flat')
        print(f"✅ Adsorbant library working ({len(adsorbants)} molecules available)")
    except Exception as e:
        print(f"❌ Adsorbant library failed: {e}")
        return False
    
    # Test 5: CPU detection
    try:
        cores = detect_cpu_cores()
        print(f"✅ CPU detection working ({cores} cores detected)")
    except Exception as e:
        print(f"❌ CPU detection failed: {e}")
        return False
    
    print("\n🎉 All basic functionality tests passed!")
    print("Package is ready for use (external dependencies may be needed for full functionality)")
    return True


if __name__ == '__main__':
    # Run basic test when script is executed directly
    run_basic_functionality_test()
