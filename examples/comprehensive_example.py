#!/usr/bin/env python3
"""
Comprehensive example showcasing the full capabilities of the Energy Profile Calculator.

This example demonstrates:
- Traditional crystal surfaces (Au, Pt, etc.)
- 2D materials (MoS2, graphene, etc.)
- All categories of adsorbants (73+ total)
- Multiple calculation methods
- Batch processing
"""

import os
import sys
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from energy_profile_calculator import EnergyProfileCalculator
from energy_profile_calculator.adsorbants import AdsorbantLibrary
from energy_profile_calculator.surfaces import SurfaceBuilder

def main():
    print("🚀 Comprehensive Energy Profile Calculator Demo")
    print("=" * 60)
    
    # Initialize libraries
    ads_lib = AdsorbantLibrary()
    surface_builder = SurfaceBuilder()
    
    print(f"📚 Adsorbant Library: {len(ads_lib.list_adsorbants())} adsorbants available")
    print(f"🏗️  Surface Builder: {len(surface_builder.list_2d_materials())} 2D materials available")
    print()
    
    # Showcase different categories
    print("🧪 Available Adsorbant Categories:")
    categories = {
        'Simple molecules': ['H2O', 'CO', 'NH3', 'CH4'],
        'Metal clusters': ['Au2', 'Pt2', 'Ti2', 'Ag2'],
        'Organic molecules': ['F4TCNQ', 'tetracene', 'TCNQ', 'TTF'],
        'Inorganic materials': ['ZnO', 'TiO2', 'Sb2O3'],
        'Individual atoms': ['H', 'O', 'C', 'N']
    }
    
    for category, examples in categories.items():
        print(f"  • {category}: {', '.join(examples[:3])}{'...' if len(examples) > 3 else ''}")
    print()
    
    print("🏔️  Available Surface Types:")
    print("  • Traditional crystals: Au(111), Pt(111), Cu(100), etc.")
    print("  • 2D materials: MoS2, graphene, h-BN, WS2, phosphorene, etc.")
    print()
    
    # Initialize calculator
    calc = EnergyProfileCalculator()
    
    # Example 1: Traditional surface with organic molecule
    print("📊 Example 1: F4TCNQ on Au(111)")
    print("-" * 40)
    
    try:
        # Setup Au(111) surface
        calc.setup_surface(
            material='Au',
            miller_indices=(1, 1, 1),
            size=(3, 3, 4),
            vacuum=14.0
        )
        
        # Setup ML calculator only for this demo
        calc.setup_calculators(
            use_ml=True,
            use_dft=False,
            ml_model='uma-s-1',
            ml_device='cpu'  # Use CPU for compatibility
        )
        
        # Calculate energy profile for F4TCNQ (organic electron acceptor)
        results_1 = calc.calculate_energy_profile(
            adsorbant='F4TCNQ',
            z_start=3.0,
            z_end=6.0,
            z_step=0.5,
            ml_tasks=['omat'],
            output_dir='./results/f4tcnq_au111'
        )
        
        print("✅ F4TCNQ/Au(111) calculation completed")
        
    except Exception as e:
        print(f"⚠️  F4TCNQ/Au(111) calculation: {e}")
    
    print()
    
    # Example 2: 2D material with metal cluster
    print("📊 Example 2: Au dimer on MoS2")
    print("-" * 40)
    
    try:
        # Create MoS2 surface using surface builder directly
        mos2_surface = surface_builder.build_2d_material(
            material='MoS2',
            size=(3, 3),
            vacuum=15.0
        )
        
        # Note: For a full calculation, you would setup the surface in the calculator
        # This is just demonstrating the surface creation capability
        print(f"✅ MoS2 surface created: {len(mos2_surface)} atoms")
        
        # Get information about the 2D material
        mos2_info = surface_builder.get_2d_material_info('MoS2')
        print(f"   MoS2 properties: {mos2_info['metal']} coordination = {mos2_info['metal_coord']}")
        
    except Exception as e:
        print(f"⚠️  MoS2 surface creation: {e}")
    
    print()
    
    # Example 3: Demonstrate adsorbant diversity
    print("📊 Example 3: Adsorbant Diversity Showcase")
    print("-" * 40)
    
    test_adsorbants = [
        ('ZnO', 'Metal oxide'),
        ('tetracene', 'Organic aromatic'),
        ('Pt2', 'Noble metal cluster'),
        ('Sb2O3', 'Inorganic compound')
    ]
    
    for ads, description in test_adsorbants:
        try:
            # Create adsorbant structure
            atoms = ads_lib.get_adsorbant(ads, position=(0, 0, 5), orientation='default')
            info = ads_lib.get_info(ads)
            print(f"✅ {ads} ({description}): {len(atoms)} atoms, {info['description']}")
        except Exception as e:
            print(f"⚠️  {ads}: {e}")
    
    print()
    
    # Example 4: Batch comparison study
    print("📊 Example 4: Metal Cluster Comparison")
    print("-" * 40)
    
    metal_clusters = ['Au2', 'Pt2', 'Ag2', 'Cu2']
    print("Comparing different metal dimers on Au(111):")
    
    for metal in metal_clusters:
        try:
            # This would be a full calculation in practice
            atoms = ads_lib.get_adsorbant(metal, position=(0, 0, 4), orientation='parallel')
            info = ads_lib.get_info(metal)
            print(f"  • {metal}: {info['description']} ({len(atoms)} atoms)")
        except Exception as e:
            print(f"  ⚠️ {metal}: {e}")
    
    print()
    print("🎯 Summary:")
    print("  • Package supports 73+ adsorbants across 5 major categories")
    print("  • Includes 26 different 2D materials plus traditional crystal surfaces")
    print("  • Suitable for comprehensive adsorption studies in catalysis and materials science")
    print("  • Modular design allows easy extension with new materials")
    print()
    print("📖 For more examples, see the examples/ directory")
    print("📚 Full documentation: https://github.com/AbrarFaiyad/energy-profile-calculator")

if __name__ == '__main__':
    main()
