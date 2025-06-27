#!/usr/bin/env python3
"""
Test script to run ML potential energy sweeps for all requested adsorbants on MoS2
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
    
    print("🚀 MoS2 Adsorbant ML Energy Profile Testing")
    print("=" * 60)
    
    # Initialize libraries
    lib = AdsorbantLibrary()
    surface_builder = SurfaceBuilder()
    
    # Load configuration
    with open('job_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    adsorbants = config['adsorbants']
    z_ranges = config['z_ranges']
    
    print(f"📋 Testing ML sweeps for {len(adsorbants)} adsorbants...")
    print(f"🎯 Surface: MoS2")
    print(f"🧠 ML Calculator: {config['ml_calculator']}")
    print("-" * 60)
    
    # Create results directory
    results_dir = Path("ml_test_results")
    results_dir.mkdir(exist_ok=True)
    
    successful_runs = []
    failed_runs = []
    
    for i, adsorbant in enumerate(adsorbants, 1):
        print(f"\n[{i}/{len(adsorbants)}] Testing {adsorbant}...")
        
        try:
            # Verify adsorbant is available
            info = lib.get_info(adsorbant)
            print(f"  ✅ Adsorbant available: {info['description']}")
            
            # Get z-range for this adsorbant
            if adsorbant in z_ranges:
                z_start, z_end, z_step = z_ranges[adsorbant]
                print(f"  📏 Z-range: {z_start} to {z_end} Å (step: {z_step})")
            else:
                # Default range for unknown adsorbants
                z_start, z_end, z_step = 2.5, 8.0, 0.3
                print(f"  📏 Z-range: {z_start} to {z_end} Å (step: {z_step}) [default]")
            
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
            
            print(f"  🔬 Running ML energy sweep...")
            start_time = time.time()
            
            # Get the first available orientation for this adsorbant
            available_orientations = info.get('orientations', ['default'])
            orientation = available_orientations[0] if available_orientations else 'default'
            print(f"  🔄 Using orientation: {orientation}")
            
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
            
            # Check if results were generated
            if results is not None and (
                'ml_energies' in results or 
                'omat_energies' in results or 
                'omc_energies' in results or
                'energies' in results
            ):
                print(f"  ✅ ML sweep completed in {duration:.1f}s")
                
                # Try to find energy data
                energy_data = None
                if 'ml_energies' in results:
                    energy_data = results['ml_energies']
                elif 'omat_energies' in results:
                    energy_data = results['omat_energies']
                elif 'omc_energies' in results:
                    energy_data = results['omc_energies']
                elif 'energies' in results:
                    energy_data = results['energies']
                
                if energy_data is not None and hasattr(energy_data, '__len__'):
                    print(f"  📁 Results: {len(energy_data)} energy points calculated")
                else:
                    print(f"  📁 Results: Energy profile data available")
                
                successful_runs.append(adsorbant)
            else:
                print(f"  ❌ ML sweep failed - no valid results returned")
                failed_runs.append(adsorbant)
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed_runs.append(adsorbant)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ML Testing Summary:")
    print(f"  ✅ Successful: {len(successful_runs)}/{len(adsorbants)}")
    print(f"  ❌ Failed: {len(failed_runs)}/{len(adsorbants)}")
    
    if successful_runs:
        print(f"\n✅ Successful adsorbants:")
        for ads in successful_runs:
            print(f"    - {ads}")
    
    if failed_runs:
        print(f"\n❌ Failed adsorbants:")
        for ads in failed_runs:
            print(f"    - {ads}")
    
    # Generate summary report
    summary_file = results_dir / "ml_test_summary.yaml"
    summary_data = {
        'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_adsorbants': len(adsorbants),
        'successful_runs': len(successful_runs),
        'failed_runs': len(failed_runs),
        'success_rate': f"{len(successful_runs)/len(adsorbants)*100:.1f}%",
        'successful_adsorbants': successful_runs,
        'failed_adsorbants': failed_runs,
        'config_used': {
            'ml_calculator': config['ml_calculator'],
            'slab_size': config['slab_settings']['size'],
            'vacuum': config['slab_settings']['vacuum']
        }
    }
    
    with open(summary_file, 'w') as f:
        yaml.dump(summary_data, f, default_flow_style=False, indent=2)
    
    print(f"\n📝 Summary report saved to: {summary_file}")
    print(f"\n🎉 ML testing completed!")
    
    if len(successful_runs) == len(adsorbants):
        print("🌟 All adsorbants tested successfully!")
        sys.exit(0)
    else:
        print(f"⚠️  {len(failed_runs)} adsorbants failed testing")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and the energy_profile_calculator package is available")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
