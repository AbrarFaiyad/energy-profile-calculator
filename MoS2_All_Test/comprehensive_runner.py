#!/usr/bin/env python3
"""
Comprehensive MoS2 Energy Profile Runner

This script runs both ML and DFT calculations for all adsorbants on MoS2,
applying all the lessons learned from the ML-only testing phase.
"""

import sys
import os
import yaml
import time
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import argparse

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from energy_profile_calculator.core import EnergyProfileCalculator
    from energy_profile_calculator.adsorbants import AdsorbantLibrary
    from energy_profile_calculator.surfaces import SurfaceBuilder
    
    print("🚀 Comprehensive MoS2 Energy Profile Calculator")
    print("=" * 70)
    print("📋 ML + DFT calculations for all adsorbants on MoS2")
    print("🧠 Applying lessons learned from ML-only testing")
    print("=" * 70)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and the energy_profile_calculator package is available")
    sys.exit(1)
    
class ComprehensiveMoS2Runner:
    def __init__(self, config_file: str):
        self.config_file = Path(config_file)
        self.load_config()
        
        # Initialize libraries
        self.adsorbant_library = AdsorbantLibrary()
        self.surface_builder = SurfaceBuilder()
        
        # Create directories
        self.results_dir = Path("comprehensive_results")
        self.ml_results_dir = self.results_dir / "ml_results"
        self.dft_results_dir = self.results_dir / "dft_results"
        self.comparison_dir = self.results_dir / "comparisons"
        
        for dir_path in [self.results_dir, self.ml_results_dir, self.dft_results_dir, self.comparison_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Results tracking
        self.ml_results = {}
        self.dft_results = {}
        self.successful_ml = []
        self.successful_dft = []
        self.failed_ml = []
        self.failed_dft = []
        
    def load_config(self):
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.ml_calculator = config.get('ml_calculator', 'uma-s-1')
        self.pseudo_dir = config.get('pseudo_dir', '/home/afaiyad/QE/qe-7.4.1/pseudo')
        self.materials = config.get('materials', ['MoS2'])
        self.adsorbants = config.get('adsorbants', [])
        self.z_ranges = config.get('z_ranges', {})
        self.dft_settings = config.get('dft_settings', {})
        self.slab_settings = config.get('slab_settings', {})
        
        print(f"📝 Loaded configuration:")
        print(f"   Materials: {self.materials}")
        print(f"   Adsorbants: {len(self.adsorbants)}")
        print(f"   ML Calculator: {self.ml_calculator}")
        print(f"   Pseudopotential Dir: {self.pseudo_dir}")
    
    def get_adsorbant_orientation(self, adsorbant: str) -> str:
        """Get appropriate orientation for an adsorbant based on our ML testing experience"""
        try:
            info = self.adsorbant_library.get_info(adsorbant)
            orientations = info.get('orientations', ['default'])
            
            # Choose best orientation based on adsorbant type
            if 'parallel' in orientations:
                return 'parallel'  # Good for dimers
            elif 'flat' in orientations:
                return 'flat'      # Good for organic molecules
            elif 'default' in orientations:
                return 'default'   # Safe fallback
            else:
                return orientations[0]  # Use first available
                
        except Exception:
            return 'default'
    
    def setup_calculator(self, calculation_type: str = 'ml') -> EnergyProfileCalculator:
        """Setup calculator with MoS2 surface"""
        calculator = EnergyProfileCalculator()
        
        # Setup MoS2 surface (2D material) - build it directly as learned from ML tests
        calculator.surface = calculator.surface_builder.build_2d_material(
            material='MoS2',
            size=self.slab_settings.get('size', [3, 3]),
            vacuum=self.slab_settings.get('vacuum', 14.0)
        )
        calculator.surface_material = 'MoS2'
        calculator.surface_name = 'MoS2'
        
        # Setup calculators based on type
        if calculation_type == 'ml':
            calculator.setup_calculators(
                use_ml=True, 
                use_dft=False,
                ml_model=self.ml_calculator
            )
        else:  # DFT
            calculator.setup_calculators(
                use_ml=False, 
                use_dft=True,
                dft_pseudo_dir=self.pseudo_dir,
                dft_num_cores=os.cpu_count()
            )
        
        return calculator
    
    def run_ml_calculations(self):
        """Run ML calculations for all adsorbants"""
        print(f"\n🧠 Starting ML Calculations")
        print("=" * 50)
        
        ml_start_time = time.time()
        
        for i, adsorbant in enumerate(self.adsorbants, 1):
            print(f"\n[{i}/{len(self.adsorbants)}] ML: {adsorbant}")
            
            try:
                # Verify adsorbant is available
                info = self.adsorbant_library.get_info(adsorbant)
                orientation = self.get_adsorbant_orientation(adsorbant)
                print(f"  ✅ Adsorbant: {info['description']}")
                print(f"  🎯 Orientation: {orientation}")
                
                # Get z-range for this adsorbant
                if adsorbant in self.z_ranges:
                    z_start, z_end, z_step = self.z_ranges[adsorbant]
                else:
                    # Default range
                    z_start, z_end, z_step = 2.5, 8.0, 0.3
                    print(f"  ⚠️  Using default z-range")
                
                print(f"  📏 Z-range: {z_start} to {z_end} Å (step: {z_step})")
                
                # Setup calculator
                calculator = self.setup_calculator('ml')
                
                # Run ML calculation
                calc_start = time.time()
                results = calculator.calculate_energy_profile(
                    adsorbant=adsorbant,
                    z_start=z_start,
                    z_end=z_end,
                    z_step=z_step,
                    adsorbant_orientation=orientation,
                    output_dir=str(self.ml_results_dir / f"{adsorbant}_on_MoS2")
                )
                calc_duration = time.time() - calc_start
                
                # Check results using our improved logic from ML testing
                if results and isinstance(results, dict) and len(results) > 0:
                    # Process results
                    if 'ml_energies' in results:
                        energies = results['ml_energies']
                    elif 'omat_energies' in results:
                        energies = results['omat_energies']
                    else:
                        # Find any energy array
                        energy_keys = [k for k in results.keys() if 'energie' in k.lower()]
                        if energy_keys:
                            energies = results[energy_keys[0]]
                        else:
                            raise ValueError("No energy data found in results")
                    
                    heights = results.get('heights', results.get('z_values', []))
                    
                    # Store results
                    self.ml_results[adsorbant] = {
                        'heights': heights,
                        'energies': energies,
                        'orientation': orientation,
                        'calculation_time': calc_duration,
                        'raw_results': results
                    }
                    
                    # Find optimal point
                    min_idx = np.argmin(energies)
                    opt_height = heights[min_idx]
                    opt_energy = energies[min_idx]
                    
                    print(f"  ✅ ML completed in {calc_duration:.1f}s")
                    print(f"  📊 {len(energies)} points calculated")
                    print(f"  🎯 Optimal: {opt_energy:.3f} eV @ {opt_height:.2f} Å")
                    
                    self.successful_ml.append(adsorbant)
                else:
                    print(f"  ❌ ML calculation failed - no valid results")
                    self.failed_ml.append(adsorbant)
                    
            except Exception as e:
                print(f"  ❌ ML Error: {e}")
                self.failed_ml.append(adsorbant)
        
        ml_total_time = time.time() - ml_start_time
        print(f"\n🧠 ML Calculations Summary:")
        print(f"   ✅ Successful: {len(self.successful_ml)}/{len(self.adsorbants)}")
        print(f"   ❌ Failed: {len(self.failed_ml)}/{len(self.adsorbants)}")
        print(f"   ⏱️  Total time: {ml_total_time/60:.1f} minutes")
    
    def select_dft_subset(self, reduction_factor: int = 3) -> List[str]:
        """Select a subset of successful ML adsorbants for DFT validation"""
        if not self.successful_ml:
            return []
        
        # Strategy: Select every Nth adsorbant, ensuring we get a good variety
        dft_candidates = []
        
        # Categorize adsorbants
        categories = {
            'metals': ['Au2', 'Ag2', 'Pt2', 'Pd2', 'Cu2', 'Fe2', 'Co2', 'Ni2'],
            'atoms': ['Li', 'Na', 'P', 'N', 'B', 'F', 'Cl', 'S', 'O'],
            'organics': ['F4TCNQ', 'PTCDA', 'tetracene', 'TCNQ', 'TCNE', 'TTF'],
            'oxides': ['ZnO', 'TiO2']
        }
        
        # Select representatives from each category
        for category, ads_list in categories.items():
            available = [ads for ads in ads_list if ads in self.successful_ml]
            if available:
                # Select every reduction_factor-th adsorbant from this category
                selected = available[::reduction_factor]
                if not selected:  # Ensure at least one from each category
                    selected = [available[0]]
                dft_candidates.extend(selected)
        
        # Add any remaining successful adsorbants not in categories
        remaining = [ads for ads in self.successful_ml 
                    if ads not in sum(categories.values(), [])]
        dft_candidates.extend(remaining[::reduction_factor])
        
        # Remove duplicates and limit total
        dft_subset = list(set(dft_candidates))[:12]  # Max 12 DFT calculations
        
        print(f"\n🔬 Selected {len(dft_subset)} adsorbants for DFT validation:")
        for ads in dft_subset:
            category = next((cat for cat, ads_list in categories.items() if ads in ads_list), 'other')
            print(f"   - {ads} ({category})")
        
        return dft_subset
    
    def run_dft_calculations(self):
        """Run DFT calculations for selected adsorbants"""
        dft_adsorbants = self.select_dft_subset()
        
        if not dft_adsorbants:
            print(f"\n⚠️  No adsorbants selected for DFT calculations")
            return
        
        print(f"\n🔬 Starting DFT Calculations")
        print("=" * 50)
        
        dft_start_time = time.time()
        
        for i, adsorbant in enumerate(dft_adsorbants, 1):
            print(f"\n[{i}/{len(dft_adsorbants)}] DFT: {adsorbant}")
            
            try:
                # Get ML results for this adsorbant to guide DFT
                ml_data = self.ml_results[adsorbant]
                orientation = ml_data['orientation']
                
                # Use coarser z-range for DFT (every 3rd point from ML range)
                if adsorbant in self.z_ranges:
                    z_start, z_end, ml_step = self.z_ranges[adsorbant]
                    z_step = ml_step * 3  # Coarser for DFT
                else:
                    z_start, z_end, z_step = 2.5, 8.0, 0.9
                
                print(f"  🎯 Orientation: {orientation} (from ML)")
                print(f"  📏 Z-range: {z_start} to {z_end} Å (step: {z_step})")
                
                # Setup DFT calculator
                calculator = self.setup_calculator('dft')
                
                # Run DFT calculation
                calc_start = time.time()
                results = calculator.calculate_energy_profile(
                    adsorbant=adsorbant,
                    z_start=z_start,
                    z_end=z_end,
                    z_step=z_step,
                    adsorbant_orientation=orientation,
                    dft_functional=self.dft_settings.get('functional', 'pbe'),
                    custom_pseudopotentials=None,
                    output_dir=str(self.dft_results_dir / f"{adsorbant}_on_MoS2")
                )
                calc_duration = time.time() - calc_start
                
                # Process DFT results
                if results and isinstance(results, dict) and len(results) > 0:
                    # Find DFT energies
                    if 'dft_energies' in results:
                        energies = results['dft_energies']
                    else:
                        # Find any energy array
                        energy_keys = [k for k in results.keys() if 'energie' in k.lower()]
                        if energy_keys:
                            energies = results[energy_keys[0]]
                        else:
                            raise ValueError("No DFT energy data found")
                    
                    heights = results.get('heights', results.get('z_values', []))
                    
                    # Store results
                    self.dft_results[adsorbant] = {
                        'heights': heights,
                        'energies': energies,
                        'orientation': orientation,
                        'calculation_time': calc_duration,
                        'raw_results': results
                    }
                    
                    # Find optimal point
                    min_idx = np.argmin(energies)
                    opt_height = heights[min_idx]
                    opt_energy = energies[min_idx]
                    
                    print(f"  ✅ DFT completed in {calc_duration/60:.1f} minutes")
                    print(f"  📊 {len(energies)} points calculated")
                    print(f"  🎯 Optimal: {opt_energy:.3f} eV @ {opt_height:.2f} Å")
                    
                    self.successful_dft.append(adsorbant)
                else:
                    print(f"  ❌ DFT calculation failed - no valid results")
                    self.failed_dft.append(adsorbant)
                    
            except Exception as e:
                print(f"  ❌ DFT Error: {e}")
                self.failed_dft.append(adsorbant)
        
        dft_total_time = time.time() - dft_start_time
        print(f"\n🔬 DFT Calculations Summary:")
        print(f"   ✅ Successful: {len(self.successful_dft)}/{len(dft_adsorbants)}")
        print(f"   ❌ Failed: {len(self.failed_dft)}/{len(dft_adsorbants)}")
        print(f"   ⏱️  Total time: {dft_total_time/60:.1f} minutes")
    
    def compare_ml_dft_results(self):
        """Compare ML and DFT results for validation"""
        print(f"\n📊 ML vs DFT Comparison")
        print("=" * 40)
        
        common_adsorbants = set(self.successful_ml) & set(self.successful_dft)
        
        if not common_adsorbants:
            print("⚠️  No common successful calculations for comparison")
            return
        
        comparison_data = []
        
        for adsorbant in common_adsorbants:
            ml_data = self.ml_results[adsorbant]
            dft_data = self.dft_results[adsorbant]
            
            # Find optimal points
            ml_energies = np.array(ml_data['energies'])
            dft_energies = np.array(dft_data['energies'])
            
            ml_min_idx = np.argmin(ml_energies)
            dft_min_idx = np.argmin(dft_energies)
            
            ml_opt_height = ml_data['heights'][ml_min_idx]
            ml_opt_energy = ml_energies[ml_min_idx]
            
            dft_opt_height = dft_data['heights'][dft_min_idx]
            dft_opt_energy = dft_energies[dft_min_idx]
            
            # Calculate differences
            height_diff = abs(ml_opt_height - dft_opt_height)
            energy_diff = abs(ml_opt_energy - dft_opt_energy)
            
            comparison_data.append({
                'adsorbant': adsorbant,
                'ml_height': ml_opt_height,
                'ml_energy': ml_opt_energy,
                'dft_height': dft_opt_height,
                'dft_energy': dft_opt_energy,
                'height_diff': height_diff,
                'energy_diff': energy_diff
            })
            
            print(f"{adsorbant:>10}: ML {ml_opt_energy:6.3f}eV@{ml_opt_height:4.1f}Å | "
                  f"DFT {dft_opt_energy:6.3f}eV@{dft_opt_height:4.1f}Å | "
                  f"ΔE={energy_diff:.3f}eV ΔH={height_diff:.1f}Å")
        
        # Save comparison data
        comparison_file = self.comparison_dir / "ml_dft_comparison.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison_data, f, indent=2)
        
        print(f"\n📝 Comparison data saved to: {comparison_file}")
        
        # Statistics
        if comparison_data:
            height_diffs = [d['height_diff'] for d in comparison_data]
            energy_diffs = [d['energy_diff'] for d in comparison_data]
            
            print(f"\n📈 Statistics:")
            print(f"   Mean height difference: {np.mean(height_diffs):.2f} ± {np.std(height_diffs):.2f} Å")
            print(f"   Mean energy difference: {np.mean(energy_diffs):.3f} ± {np.std(energy_diffs):.3f} eV")
            print(f"   Max height difference: {np.max(height_diffs):.2f} Å")
            print(f"   Max energy difference: {np.max(energy_diffs):.3f} eV")
    
    def save_final_summary(self):
        """Save final summary of all results"""
        summary = {
            'run_info': {
                'timestamp': datetime.now().isoformat(),
                'total_adsorbants': len(self.adsorbants),
                'ml_calculator': self.ml_calculator,
                'surface': 'MoS2',
                'config_file': str(self.config_file)
            },
            'ml_results': {
                'successful': len(self.successful_ml),
                'failed': len(self.failed_ml),
                'success_rate': f"{len(self.successful_ml)/len(self.adsorbants)*100:.1f}%",
                'successful_list': self.successful_ml,
                'failed_list': self.failed_ml
            },
            'dft_results': {
                'successful': len(self.successful_dft),
                'failed': len(self.failed_dft),
                'attempted': len(self.successful_dft) + len(self.failed_dft),
                'success_rate': f"{len(self.successful_dft)/(len(self.successful_dft) + len(self.failed_dft))*100:.1f}%" if (len(self.successful_dft) + len(self.failed_dft)) > 0 else "0%",
                'successful_list': self.successful_dft,
                'failed_list': self.failed_dft
            }
        }
        
        summary_file = self.results_dir / "comprehensive_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📝 Final summary saved to: {summary_file}")
        
        return summary
    
    def run_comprehensive_workflow(self):
        """Run the complete ML + DFT workflow"""
        print(f"🚀 Starting Comprehensive MoS2 Energy Profile Workflow")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        total_start_time = time.time()
        
        try:
            # Step 1: ML Calculations
            self.run_ml_calculations()
            
            # Step 2: DFT Calculations (subset)
            self.run_dft_calculations()
            
            # Step 3: Compare results
            self.compare_ml_dft_results()
            
            # Step 4: Save summary
            summary = self.save_final_summary()
            
            total_time = time.time() - total_start_time
            
            # Final report
            print("\n" + "=" * 70)
            print("🎉 COMPREHENSIVE WORKFLOW COMPLETED!")
            print("=" * 70)
            print(f"📊 Final Results:")
            print(f"   ML Calculations: {summary['ml_results']['successful']}/{summary['run_info']['total_adsorbants']} successful")
            print(f"   DFT Calculations: {summary['dft_results']['successful']}/{summary['dft_results']['attempted']} successful")
            print(f"   Total Runtime: {total_time/3600:.2f} hours")
            print(f"   Results Directory: {self.results_dir.absolute()}")
            print("=" * 70)
            
            if len(self.successful_ml) == len(self.adsorbants):
                print("🌟 Perfect ML success rate achieved!")
            
            if len(self.successful_dft) > 0:
                print("🔬 DFT validation data available for ML comparison!")
            
        except Exception as e:
            print(f"\n❌ Workflow failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Comprehensive MoS2 Energy Profile Calculator')
    parser.add_argument('--config', default='job_config.yaml',
                       help='Configuration file (default: job_config.yaml)')
    parser.add_argument('--adsorbant', type=str,
                       help='Run single adsorbant instead of all')
    parser.add_argument('--ml-only', action='store_true',
                       help='Run only ML calculations (skip DFT)')
    parser.add_argument('--dft-only', action='store_true',
                       help='Run only DFT calculations (requires existing ML results)')
    
    args = parser.parse_args()
    
    runner = ComprehensiveMoS2Runner(args.config)
    
    if args.adsorbant:
        # Single adsorbant mode
        print(f"🎯 Running single adsorbant: {args.adsorbant}")
        
        # Temporarily modify adsorbants list to just this one
        original_adsorbants = runner.adsorbants
        runner.adsorbants = [args.adsorbant]
        
        if args.ml_only:
            runner.run_ml_calculations()
        elif args.dft_only:
            runner.run_dft_calculations()
        else:
            runner.run_comprehensive_workflow()
            
        # Restore original list
        runner.adsorbants = original_adsorbants
        
    else:
        # All adsorbants mode
        if args.ml_only:
            runner.run_ml_calculations()
        elif args.dft_only:
            runner.run_dft_calculations()
        else:
            runner.run_comprehensive_workflow()


if __name__ == "__main__":
    main()
