"""
Example: Batch calculation for multiple adsorbants (headless-friendly version)
"""

from energy_profile_calculator import EnergyProfileCalculator
import os

# Set matplotlib backend before any imports that might use it
os.environ['MPLBACKEND'] = 'Agg'

def main():
    # Initialize calculator
    calc = EnergyProfileCalculator()
    
    # Setup Au(111) surface - reused for all calculations
    print("Setting up Au(111) surface...")
    calc.setup_surface(
        material='Au',
        miller_indices=(1, 1, 1),
        size=(3, 3, 4),
        vacuum=14.0
    )
    
    # Setup ML calculators only for speed
    print("Setting up ML calculators...")
    calc.setup_calculators(
        use_ml=True,
        use_dft=False,
        ml_model='uma-s-1',
        ml_device='cuda'
    )
    
    # Define adsorbants to study
    adsorbants = {
        'H': 'default',
        'O': 'default', 
        'H2O': 'flat',
        'CO': 'c_down'
    }
    
    # Store results for comparison
    all_results = {}
    summary_data = []
    
    # Run calculations for each adsorbant
    for ads_name, orientation in adsorbants.items():
        print(f"\n{'='*50}")
        print(f"Calculating {ads_name} adsorption...")
        print(f"{'='*50}")
        
        try:
            # Calculate energy profile
            results = calc.calculate_energy_profile(
                adsorbant=ads_name,
                z_start=2.0,
                z_end=8.0,
                z_step=0.4,  # Moderate resolution for speed
                adsorbant_orientation=orientation,
                ml_tasks=['omat', 'omc'],
                save_structures=False,  # Skip structures for speed
                output_dir=f'./batch_results/{ads_name}'
            )
            
            # Extract key metrics
            binding_energies = calc.get_binding_energies()
            optimal_heights = calc.get_optimal_heights()
            
            # Store results
            all_results[ads_name] = {
                'results': results,
                'binding_energies': binding_energies,
                'optimal_heights': optimal_heights
            }
            
            # Add to summary
            for method in binding_energies:
                summary_data.append({
                    'Adsorbant': ads_name,
                    'Method': method,
                    'Binding_Energy_eV': binding_energies[method],
                    'Optimal_Height_A': optimal_heights[method]
                })
            
            print(f"✅ {ads_name} calculation completed")
            
            # Try to create plots, but don't fail if it doesn't work
            try:
                calc.create_plots(
                    save_path=f'./batch_results/{ads_name}/{ads_name}_au111_profile',
                    formats=['png']
                )
                print(f"   Plots created successfully")
            except Exception as e:
                print(f"   Plot creation skipped (headless environment): {str(e)[:50]}...")
            
        except Exception as e:
            print(f"❌ {ads_name} calculation failed: {e}")
            continue
    
    # Create summary comparison
    print(f"\n{'='*60}")
    print("BATCH CALCULATION SUMMARY")
    print(f"{'='*60}")
    
    # Create simple text-based summary
    print("\nBinding Energies (eV):")
    print(f"{'Adsorbant':<10} {'OMAT':<10} {'OMC':<10}")
    print("-" * 30)
    
    for ads_name in adsorbants.keys():
        if ads_name in all_results:
            be = all_results[ads_name]['binding_energies']
            omat_be = be.get('OMAT', 'N/A')
            omc_be = be.get('OMC', 'N/A')
            if isinstance(omat_be, float):
                omat_be = f"{omat_be:.4f}"
            if isinstance(omc_be, float):
                omc_be = f"{omc_be:.4f}"
            print(f"{ads_name:<10} {omat_be:<10} {omc_be:<10}")
    
    print("\nOptimal Heights (Å):")
    print(f"{'Adsorbant':<10} {'OMAT':<10} {'OMC':<10}")
    print("-" * 30)
    
    for ads_name in adsorbants.keys():
        if ads_name in all_results:
            oh = all_results[ads_name]['optimal_heights']
            omat_oh = oh.get('OMAT', 'N/A')
            omc_oh = oh.get('OMC', 'N/A')
            if isinstance(omat_oh, float):
                omat_oh = f"{omat_oh:.1f}"
            if isinstance(omc_oh, float):
                omc_oh = f"{omc_oh:.1f}"
            print(f"{ads_name:<10} {omat_oh:<10} {omc_oh:<10}")
    
    # Save summary as simple text file
    with open('./batch_results/summary.txt', 'w') as f:
        f.write("Batch Calculation Summary\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("Binding Energies (eV):\n")
        f.write(f"{'Adsorbant':<10} {'OMAT':<10} {'OMC':<10}\n")
        f.write("-" * 30 + "\n")
        
        for ads_name in adsorbants.keys():
            if ads_name in all_results:
                be = all_results[ads_name]['binding_energies']
                omat_be = be.get('OMAT', 'N/A')
                omc_be = be.get('OMC', 'N/A')
                if isinstance(omat_be, float):
                    omat_be = f"{omat_be:.4f}"
                if isinstance(omc_be, float):
                    omc_be = f"{omc_be:.4f}"
                f.write(f"{ads_name:<10} {omat_be:<10} {omc_be:<10}\n")
        
        f.write("\nOptimal Heights (Å):\n")
        f.write(f"{'Adsorbant':<10} {'OMAT':<10} {'OMC':<10}\n")
        f.write("-" * 30 + "\n")
        
        for ads_name in adsorbants.keys():
            if ads_name in all_results:
                oh = all_results[ads_name]['optimal_heights']
                omat_oh = oh.get('OMAT', 'N/A')
                omc_oh = oh.get('OMC', 'N/A')
                if isinstance(omat_oh, float):
                    omat_oh = f"{omat_oh:.1f}"
                if isinstance(omc_oh, float):
                    omc_oh = f"{omc_oh:.1f}"
                f.write(f"{ads_name:<10} {omat_oh:<10} {omc_oh:<10}\n")
    
    print("\nSummary saved to: ./batch_results/summary.txt")
    
    # Print key insights
    print(f"\n{'='*60}")
    print("KEY INSIGHTS")
    print(f"{'='*60}")
    
    # Find strongest binder
    max_binding = 0
    strongest_binder = None
    strongest_method = None
    
    for ads_name in all_results:
        for method, energy in all_results[ads_name]['binding_energies'].items():
            if energy > max_binding:
                max_binding = energy
                strongest_binder = ads_name
                strongest_method = method
    
    if strongest_binder:
        print(f"Strongest binding: {strongest_binder} with {strongest_method} ({max_binding:.4f} eV)")
    
    # Method agreement
    agreements = []
    for ads_name in all_results:
        be = all_results[ads_name]['binding_energies']
        if 'OMAT' in be and 'OMC' in be:
            diff = abs(be['OMAT'] - be['OMC'])
            agreements.append(diff)
            print(f"{ads_name}: OMAT-OMC difference = {diff:.4f} eV")
    
    if agreements:
        avg_diff = sum(agreements) / len(agreements)
        print(f"Average OMAT-OMC difference: {avg_diff:.4f} eV")

if __name__ == '__main__':
    main()
