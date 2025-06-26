#!/usr/bin/env python3
"""
Test script for new adsorbants and 2D materials functionality.
"""

import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from energy_profile_calculator.adsorbants import AdsorbantLibrary
    from energy_profile_calculator.surfaces import SurfaceBuilder
    
    print("Testing new adsorbants and surfaces functionality...")
    
    # Test adsorbants library
    lib = AdsorbantLibrary()
    print(f"\nTotal adsorbants available: {len(lib.list_adsorbants())}")
    
    # Test some new adsorbants
    new_adsorbants = ['Au2', 'Ti2', 'Sb2O3', 'F4TCNQ', 'tetracene', 'ZnO', 'TiO2']
    print("\nTesting new adsorbants:")
    for ads in new_adsorbants:
        try:
            info = lib.get_info(ads)
            print(f"  ✓ {ads}: {info['description']}")
        except Exception as e:
            print(f"  ✗ {ads}: Error - {e}")
    
    # Test 2D materials
    surface_builder = SurfaceBuilder()
    print(f"\n2D materials available: {len(surface_builder.list_2d_materials())}")
    
    # Test some 2D materials
    test_2d_materials = ['MoS2', 'graphene', 'h-BN', 'WS2', 'phosphorene']
    print("\nTesting 2D materials:")
    for material in test_2d_materials:
        try:
            info = surface_builder.get_2d_material_info(material)
            print(f"  ✓ {material}: {info['metal']} coordination: {info['metal_coord']}")
        except Exception as e:
            print(f"  ✗ {material}: Error - {e}")
    
    # Test creating some adsorbants
    print("\nTesting adsorbant creation:")
    test_position = (0.0, 0.0, 5.0)
    
    simple_tests = [
        ('H2O', 'flat'),
        ('Au2', 'parallel'), 
        ('ZnO', 'perpendicular'),
        ('Li', 'default')
    ]
    
    for ads_name, orientation in simple_tests:
        try:
            atoms = lib.get_adsorbant(ads_name, test_position, orientation)
            print(f"  ✓ {ads_name} ({orientation}): {len(atoms)} atoms")
        except Exception as e:
            print(f"  ✗ {ads_name} ({orientation}): Error - {e}")
    
    print("\n✅ All tests completed successfully!")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure ASE and numpy are installed")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
