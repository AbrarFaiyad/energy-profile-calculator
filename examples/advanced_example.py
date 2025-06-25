"""
Example: Advanced calculation with ML and DFT methods
"""

from energy_profile_calculator import EnergyProfileCalculator

def main():
    # Initialize calculator
    calc = EnergyProfileCalculator()
    
    # Setup Pt(111) surface
    print("Setting up Pt(111) surface...")
    calc.setup_surface(
        material='Pt',
        miller_indices=(1, 1, 1),
        size=(3, 3, 4),
        vacuum=15.0
    )
    
    # Setup both ML and DFT calculators
    print("Setting up calculators...")
    calc.setup_calculators(
        use_ml=True,
        use_dft=True,
        ml_model='uma-s-1',
        ml_device='cuda',
        dft_pseudo_dir='/path/to/pseudopotentials',  # Update this path
        dft_num_cores=8
    )
    
    # Calculate CO adsorption energy profile
    print("Calculating CO energy profile...")
    results = calc.calculate_energy_profile(
        adsorbant='CO',
        z_start=1.5,
        z_end=6.0,
        z_step=0.2,
        adsorbant_orientation='c_down',  # Carbon pointing down
        ml_tasks=['omat', 'omc'],
        dft_functional='pbe',
        dft_subset_factor=3,  # Calculate DFT every 3rd point
        custom_pseudopotentials={
            'Pt': 'Pt.pbe-spfn-kjpaw_psl.1.0.0.UPF',
            'C': 'C.pbe-n-kjpaw_psl.1.0.0.UPF',
            'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF'
        },
        save_structures=True,
        output_dir='./advanced_results'
    )
    
    # Create comprehensive plots
    print("Creating plots...")
    calc.create_plots(
        save_path='./advanced_results/co_pt111_profile',
        formats=['png', 'pdf', 'svg']
    )
    
    # Detailed analysis
    binding_energies = calc.get_binding_energies()
    optimal_heights = calc.get_optimal_heights()
    
    print("\n" + "="*60)
    print("DETAILED RESULTS ANALYSIS")
    print("="*60)
    print(f"System: CO on Pt(111)")
    print(f"Calculation methods: ML (OMAT/OMC) + DFT")
    
    print(f"\nBinding Energy Comparison:")
    for method, energy in binding_energies.items():
        print(f"  {method}: {energy:.4f} eV")
    
    print(f"\nOptimal Adsorption Heights:")
    for method, height in optimal_heights.items():
        print(f"  {method}: {height:.1f} Å")
    
    # Method agreement analysis
    if 'OMAT' in binding_energies and 'DFT' in binding_energies:
        omat_dft_diff = abs(binding_energies['OMAT'] - binding_energies['DFT'])
        print(f"\nOMAT-DFT binding energy difference: {omat_dft_diff:.4f} eV")
    
    if 'OMC' in binding_energies and 'DFT' in binding_energies:
        omc_dft_diff = abs(binding_energies['OMC'] - binding_energies['DFT'])
        print(f"OMC-DFT binding energy difference: {omc_dft_diff:.4f} eV")
    
    print(f"\nAll results saved to: ./advanced_results/")

if __name__ == '__main__':
    main()
