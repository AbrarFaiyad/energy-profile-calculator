"""
Example: Basic H2O on Au(111) energy profile calculation
"""

from energy_profile_calculator import EnergyProfileCalculator

def main():
    # Initialize calculator
    calc = EnergyProfileCalculator()
    
    # Setup Au(111) surface
    print("Setting up Au(111) surface...")
    calc.setup_surface(
        material='Au',
        miller_indices=(1, 1, 1),
        size=(3, 3, 4),
        vacuum=14.0
    )
    
    # Setup ML calculators only (faster for testing)
    print("Setting up ML calculators...")
    calc.setup_calculators(
        use_ml=True,
        use_dft=False,  # Disable DFT for faster calculation
        ml_model='uma-s-1',
        ml_device='cuda'  # Use 'cpu' if no GPU available
    )
    
    # Calculate H2O adsorption energy profile
    print("Calculating H2O energy profile...")
    results = calc.calculate_energy_profile(
        adsorbant='H2O',
        z_start=2.0,
        z_end=8.0,
        z_step=0.5,  # Larger step for faster calculation
        adsorbant_orientation='flat',
        ml_tasks=['omat', 'omc'],
        save_structures=True,
        output_dir='./example_results'
    )
    
    # Create plots
    print("Creating plots...")
    calc.create_plots(
        save_path='./example_results/h2o_au111_profile',
        formats=['png', 'pdf']
    )
    
    # Print summary
    binding_energies = calc.get_binding_energies()
    optimal_heights = calc.get_optimal_heights()
    
    print("\n" + "="*50)
    print("RESULTS SUMMARY")
    print("="*50)
    print(f"System: H2O on Au(111)")
    
    print(f"\nBinding Energies:")
    for method, energy in binding_energies.items():
        print(f"  {method}: {energy:.4f} eV")
    
    print(f"\nOptimal Heights:")
    for method, height in optimal_heights.items():
        print(f"  {method}: {height:.1f} Å")
    
    print(f"\nResults saved to: ./example_results/")

if __name__ == '__main__':
    main()
