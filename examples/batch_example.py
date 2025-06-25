"""
Example: Batch calculation for multiple adsorbants
"""

from energy_profile_calculator import EnergyProfileCalculator
import pandas as pd
import matplotlib.pyplot as plt

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
        'CO': 'c_down',
        'NH3': 'n_down'
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
                z_step=0.3,  # Moderate resolution for speed
                adsorbant_orientation=orientation,
                ml_tasks=['omat', 'omc'],
                save_structures=False,  # Skip structures for speed
                output_dir=f'./batch_results/{ads_name}'
            )
            
            # Create individual plots
            calc.create_plots(
                save_path=f'./batch_results/{ads_name}/{ads_name}_au111_profile',
                formats=['png']
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
            
        except Exception as e:
            print(f"❌ {ads_name} calculation failed: {e}")
            continue
    
    # Create summary comparison
    print(f"\n{'='*60}")
    print("BATCH CALCULATION SUMMARY")
    print(f"{'='*60}")
    
    # Convert to DataFrame for easy analysis
    df = pd.DataFrame(summary_data)
    
    print("\nBinding Energies (eV):")
    print(df.pivot(index='Adsorbant', columns='Method', values='Binding_Energy_eV'))
    
    print("\nOptimal Heights (Å):")
    print(df.pivot(index='Adsorbant', columns='Method', values='Optimal_Height_A'))
    
    # Create comparison plots
    create_comparison_plots(df)
    
    # Save summary data
    df.to_csv('./batch_results/summary.csv', index=False)
    print("\nSummary saved to: ./batch_results/summary.csv")

def create_comparison_plots(df):
    """Create comparison plots across adsorbants."""
    
    # Binding energy comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Binding energies
    binding_pivot = df.pivot(index='Adsorbant', columns='Method', values='Binding_Energy_eV')
    binding_pivot.plot(kind='bar', ax=ax1, width=0.8)
    ax1.set_title('Binding Energies Comparison', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Binding Energy (eV)', fontsize=12)
    ax1.set_xlabel('Adsorbant', fontsize=12)
    ax1.legend(title='Method')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Optimal heights
    height_pivot = df.pivot(index='Adsorbant', columns='Method', values='Optimal_Height_A')
    height_pivot.plot(kind='bar', ax=ax2, width=0.8)
    ax2.set_title('Optimal Heights Comparison', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Optimal Height (Å)', fontsize=12)
    ax2.set_xlabel('Adsorbant', fontsize=12)
    ax2.legend(title='Method')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('./batch_results/batch_comparison.png', dpi=300, bbox_inches='tight')
    plt.savefig('./batch_results/batch_comparison.pdf', bbox_inches='tight')
    
    print("Comparison plots saved to: ./batch_results/batch_comparison.png/pdf")

if __name__ == '__main__':
    main()
