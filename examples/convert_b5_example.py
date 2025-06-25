"""
Example: Converting B5.py to use the Energy Profile Calculator package

This example shows how to replace the original B5.py script with the new modular package.
The functionality is equivalent but much more organized and reusable.
"""

from energy_profile_calculator import EnergyProfileCalculator

def main():
    """
    Equivalent to the original B5.py but using the modular package.
    """
    
    print("=== Energy Profile Calculator Package Demo ===")
    print("This replaces the original B5.py with modular, reusable code")
    
    # Initialize calculator (replaces manual imports and setup)
    calc = EnergyProfileCalculator()
    
    # Setup Au(111) surface (replaces fcc111 call and manual setup)
    print("\n=== Setting up surface ===")
    calc.setup_surface(
        material='Au',
        miller_indices=(1, 1, 1),
        size=(3, 3, 4),
        vacuum=14.0
    )
    
    # Setup calculators (replaces manual FairChem and QE setup)
    print("\n=== Setting up calculators ===")
    calc.setup_calculators(
        use_ml=True,
        use_dft=True,  # Set to False to skip DFT for faster testing
        ml_model='uma-s-1',
        ml_device='cuda',
        dft_pseudo_dir='/home/afaiyad/QE/qe-7.4.1/pseudo',  # Update path as needed
        dft_num_cores=None  # Auto-detect cores (replaces manual os.cpu_count())
    )
    
    # Calculate H2O energy profile (replaces manual loop and calculations)
    print("\n=== Running calculations ===")
    results = calc.calculate_energy_profile(
        adsorbant='H2O',
        z_start=2.0,
        z_end=8.0,
        z_step=0.2,
        adsorbant_orientation='flat',
        ml_tasks=['omat', 'omc'],
        dft_functional='pbe',
        dft_subset_factor=2,
        custom_pseudopotentials={
            'Au': 'Au.pbe-n-kjpaw_psl.1.0.0.UPF',
            'H': 'H.pbe-kjpaw_psl.1.0.0.UPF',
            'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF'
        },
        save_structures=True,
        output_dir='./package_results'
    )
    
    # Create plots (replaces manual matplotlib code)
    print("\n=== Creating plots ===")
    calc.create_plots(
        save_path='./package_results/h2o_au111_energy_profile',
        formats=['png', 'pdf']
    )
    
    # Analysis and summary (replaces manual analysis code)
    print("\n=== Analysis ===")
    binding_energies = calc.get_binding_energies()
    optimal_heights = calc.get_optimal_heights()
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY (Package Version)")
    print("="*60)
    print(f"System: H2O on Au(111)")
    print(f"Methods: ML (OMAT/OMC) + DFT")
    
    print(f"\nBinding Energies:")
    for method, energy in binding_energies.items():
        print(f"  {method}: {energy:.4f} eV")
    
    print(f"\nOptimal Heights:")
    for method, height in optimal_heights.items():
        print(f"  {method}: {height:.1f} Å")
    
    # Show advantages of the package approach
    print(f"\n{'='*60}")
    print("PACKAGE ADVANTAGES")
    print(f"{'='*60}")
    print("✅ Modular and reusable code")
    print("✅ Automatic CPU core detection")
    print("✅ Built-in error handling")
    print("✅ Comprehensive adsorbant library")
    print("✅ Flexible surface creation")
    print("✅ Publication-quality plots")
    print("✅ Multiple output formats")
    print("✅ Configuration file support")
    print("✅ Command-line interface")
    print("✅ Easy to extend and customize")
    
    print(f"\nResults saved to: ./package_results/")
    print("Compare this with the original B5.py output!")

def demonstrate_package_features():
    """
    Show additional features available in the package that weren't in B5.py
    """
    print(f"\n{'='*60}")
    print("ADDITIONAL PACKAGE FEATURES")
    print(f"{'='*60}")
    
    # Show available adsorbants
    from energy_profile_calculator import AdsorbantLibrary
    library = AdsorbantLibrary()
    
    print(f"\nAvailable adsorbants ({len(library.list_adsorbants())}):")
    for ads in library.list_adsorbants()[:10]:  # Show first 10
        info = library.get_info(ads)
        print(f"  {ads}: {info['description']}")
    print("  ... and more!")
    
    # Show supported surfaces
    from energy_profile_calculator import SurfaceBuilder
    builder = SurfaceBuilder()
    materials = builder.list_supported_materials()
    
    print(f"\nSupported materials:")
    for structure, material_list in materials.items():
        print(f"  {structure.upper()}: {', '.join(material_list[:8])}...")
    
    print(f"\nCommand-line usage:")
    print("  energy-profile --surface Au --miller 1 1 1 --adsorbant H2O --ml-only")
    print("  energy-profile --config config.yaml")
    print("  energy-profile --list-adsorbants")

if __name__ == '__main__':
    main()
    demonstrate_package_features()
