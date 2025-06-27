#!/usr/bin/env python3
"""
Quick test script to run ML potential energy sweep for a single adsorbant (Au2) on MoS2
"""

import sys
import os
import yaml
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from energy_profile_calculator.core import EnergyProfileCalculator
    from energy_profile_calculator.adsorbants import AdsorbantLibrary
    from energy_profile_calculator.surfaces import SurfaceBuilder
    
    print("🚀 Single Adsorbant ML Energy Profile Test")
    print("=" * 50)
    
    # Test with Au2 first
    adsorbant = 'Au2'
    
    # Initialize libraries
    lib = AdsorbantLibrary()
    surface_builder = SurfaceBuilder()
    
    # Load configuration
    with open('job_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"🎯 Testing: {adsorbant} on MoS2")
    print(f"🧠 ML Calculator: {config['ml_calculator']}")
    
    # Verify adsorbant is available and get orientation
    info = lib.get_info(adsorbant)
    print(f"✅ Adsorbant: {info['description']}")
    
    # Get the first available orientation for this adsorbant
    available_orientations = info.get('orientations', ['default'])
    orientation = available_orientations[0] if available_orientations else 'default'
    print(f"🔄 Using orientation: {orientation}")
    
    # Get z-range
    z_start, z_end, z_step = config['z_ranges'][adsorbant]
    print(f"📏 Z-range: {z_start} to {z_end} Å (step: {z_step})")
    
    # Create results directory
    results_dir = Path("ml_single_test")
    results_dir.mkdir(exist_ok=True)
    
    # Create calculator
    calculator = EnergyProfileCalculator()
    
    # Setup MoS2 surface (2D material) - build it directly
    calculator.surface = calculator.surface_builder.build_2d_material(
        material='MoS2',
        size=config['slab_settings']['size'],
        vacuum=config['slab_settings']['vacuum']
    )
    calculator.surface_material = 'MoS2'
    calculator.surface_name = 'MoS2'
    
    # Setup ML calculator
    calculator.setup_calculators(
        use_ml=True, 
        use_dft=False,
        ml_model=config['ml_calculator']
    )
    
    print(f"🔬 Running ML energy sweep...")
    start_time = time.time()
    
    # Run ML calculation
    results = calculator.calculate_energy_profile(
        adsorbant=adsorbant,
        z_start=z_start,
        z_end=z_end,
        z_step=z_step,
        adsorbant_orientation=orientation,
        output_dir=str(results_dir / f"{adsorbant}_on_MoS2")
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Check results
    if results is not None and (
        'ml_energies' in results or 
        'omat_energies' in results or 
        'omc_energies' in results or
        'energies' in results
    ):
        print(f"✅ ML sweep completed in {duration:.1f}s")
        
        # Try to find energy and height data
        energies = None
        heights = None
        
        if 'ml_energies' in results:
            energies = results['ml_energies']
            heights = results.get('heights', [])
        elif 'omat_energies' in results:
            energies = results['omat_energies'] 
            heights = results.get('heights', [])
        elif 'omc_energies' in results:
            energies = results['omc_energies']
            heights = results.get('heights', [])
        
        if energies and heights:
            min_energy_idx = energies.index(min(energies))
            
            print(f"📊 Results summary:")
            print(f"   Points calculated: {len(energies)}")
            print(f"   Energy range: {min(energies):.3f} to {max(energies):.3f} eV")
            print(f"   Optimal height: {heights[min_energy_idx]:.2f} Å")
            print(f"   Minimum energy: {min(energies):.3f} eV")
        else:
            print(f"📊 Results: Energy profile calculation completed successfully")
        
        print(f"\n🎉 Single adsorbant test successful!")
        
    else:
        print(f"❌ ML sweep failed - no valid results returned")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
