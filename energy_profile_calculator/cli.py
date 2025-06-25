"""
Command-line interface for Energy Profile Calculator.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any

from energy_profile_calculator import EnergyProfileCalculator
from energy_profile_calculator.utils import load_config, create_example_config


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Energy Profile Calculator - Calculate adsorption energy profiles using ML and DFT methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with configuration file
  energy-profile --config config.yaml

  # Quick run with command line arguments
  energy-profile --surface Au --miller 1 1 1 --adsorbant H2O --ml-only

  # Generate example configuration
  energy-profile --create-config example_config.yaml
        """
    )
    
    # Configuration
    parser.add_argument('--config', '-c', type=str,
                       help='Configuration file (YAML or JSON)')
    
    parser.add_argument('--create-config', type=str,
                       help='Create example configuration file and exit')
    
    # Surface parameters
    surface_group = parser.add_argument_group('Surface parameters')
    surface_group.add_argument('--surface', type=str,
                              help='Surface material (e.g., Au, Pt, Cu)')
    surface_group.add_argument('--miller', nargs=3, type=int, metavar=('h', 'k', 'l'),
                              help='Miller indices (e.g., 1 1 1)')
    surface_group.add_argument('--size', nargs=3, type=int, metavar=('nx', 'ny', 'nz'),
                              default=[3, 3, 4], help='Surface size (default: 3 3 4)')
    surface_group.add_argument('--vacuum', type=float, default=14.0,
                              help='Vacuum space above surface in Å (default: 14.0)')
    
    # Adsorbant parameters
    ads_group = parser.add_argument_group('Adsorbant parameters')
    ads_group.add_argument('--adsorbant', type=str,
                          help='Adsorbant molecule (e.g., H2O, CO, H)')
    ads_group.add_argument('--orientation', type=str, default='default',
                          help='Molecular orientation (default: default)')
    
    # Calculation parameters
    calc_group = parser.add_argument_group('Calculation parameters')
    calc_group.add_argument('--z-start', type=float, default=2.0,
                           help='Starting height above surface in Å (default: 2.0)')
    calc_group.add_argument('--z-end', type=float, default=8.0,
                           help='Ending height above surface in Å (default: 8.0)')
    calc_group.add_argument('--z-step', type=float, default=0.2,
                           help='Height increment in Å (default: 0.2)')
    
    # Method selection
    method_group = parser.add_argument_group('Calculation methods')
    method_group.add_argument('--ml-only', action='store_true',
                             help='Use only ML methods (OMAT/OMC)')
    method_group.add_argument('--dft-only', action='store_true',
                             help='Use only DFT methods')
    method_group.add_argument('--ml-tasks', nargs='+', default=['omat', 'omc'],
                             choices=['omat', 'omc'],
                             help='ML tasks to run (default: omat omc)')
    
    # ML parameters
    ml_group = parser.add_argument_group('ML parameters')
    ml_group.add_argument('--ml-model', type=str, default='uma-s-1',
                         help='ML model name (default: uma-s-1)')
    ml_group.add_argument('--ml-device', type=str, default='cuda',
                         choices=['cuda', 'cpu'],
                         help='Device for ML calculations (default: cuda)')
    
    # DFT parameters
    dft_group = parser.add_argument_group('DFT parameters')
    dft_group.add_argument('--pseudo-dir', type=str,
                          help='Directory containing pseudopotential files')
    dft_group.add_argument('--dft-cores', type=int,
                          help='Number of CPU cores for DFT (auto-detect if not specified)')
    dft_group.add_argument('--dft-functional', type=str, default='pbe',
                          help='DFT functional (default: pbe)')
    dft_group.add_argument('--dft-subset', type=int, default=2,
                          help='Factor to reduce DFT calculation points (default: 2)')
    
    # Output parameters
    output_group = parser.add_argument_group('Output parameters')
    output_group.add_argument('--output-dir', '-o', type=str, default='./results',
                             help='Output directory (default: ./results)')
    output_group.add_argument('--save-structures', action='store_true', default=True,
                             help='Save structure files (default: True)')
    output_group.add_argument('--plot-formats', nargs='+', default=['png', 'pdf'],
                             choices=['png', 'pdf', 'svg', 'eps'],
                             help='Plot output formats (default: png pdf)')
    
    # Miscellaneous
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--list-adsorbants', action='store_true',
                       help='List available adsorbants and exit')
    parser.add_argument('--list-surfaces', action='store_true',
                       help='List supported surfaces and exit')
    
    return parser


def validate_args(args: argparse.Namespace) -> Dict[str, Any]:
    """Validate and convert command line arguments to configuration."""
    config = {}
    
    # Surface configuration
    if args.surface and args.miller:
        config['surface'] = {
            'material': args.surface,
            'miller_indices': tuple(args.miller),
            'size': tuple(args.size),
            'vacuum': args.vacuum
        }
    elif args.surface or args.miller:
        raise ValueError("Both --surface and --miller must be specified")
    
    # Adsorbant configuration
    if args.adsorbant:
        config['adsorbant'] = {
            'type': args.adsorbant,
            'orientation': args.orientation
        }
    
    # Calculation configuration
    config['calculation'] = {
        'z_start': args.z_start,
        'z_end': args.z_end,
        'z_step': args.z_step,
        'use_ml': not args.dft_only,
        'use_dft': not args.ml_only,
        'ml_tasks': args.ml_tasks,
        'dft_subset_factor': args.dft_subset
    }
    
    # ML settings
    config['ml_settings'] = {
        'model': args.ml_model,
        'device': args.ml_device
    }
    
    # DFT settings
    config['dft_settings'] = {
        'functional': args.dft_functional,
        'pseudo_dir': args.pseudo_dir,
        'num_cores': args.dft_cores
    }
    
    # Output settings
    config['output'] = {
        'save_structures': args.save_structures,
        'output_dir': args.output_dir,
        'plot_formats': args.plot_formats
    }
    
    return config


def run_calculation(config: Dict[str, Any], verbose: bool = False) -> None:
    """Run energy profile calculation with given configuration."""
    
    # Initialize calculator
    calc = EnergyProfileCalculator(config)
    
    # Setup surface
    surface_config = config.get('surface', {})
    if not surface_config:
        raise ValueError("Surface configuration is required")
    
    calc.setup_surface(
        material=surface_config['material'],
        miller_indices=surface_config['miller_indices'],
        size=surface_config['size'],
        vacuum=surface_config.get('vacuum', 14.0)
    )
    
    # Setup calculators
    calc_config = config.get('calculation', {})
    ml_config = config.get('ml_settings', {})
    dft_config = config.get('dft_settings', {})
    
    calc.setup_calculators(
        use_ml=calc_config.get('use_ml', True),
        use_dft=calc_config.get('use_dft', False),
        ml_model=ml_config.get('model', 'uma-s-1'),
        ml_device=ml_config.get('device', 'cuda'),
        dft_pseudo_dir=dft_config.get('pseudo_dir'),
        dft_num_cores=dft_config.get('num_cores')
    )
    
    # Run calculation
    adsorbant_config = config.get('adsorbant', {})
    output_config = config.get('output', {})
    
    results = calc.calculate_energy_profile(
        adsorbant=adsorbant_config['type'],
        z_start=calc_config.get('z_start', 2.0),
        z_end=calc_config.get('z_end', 8.0),
        z_step=calc_config.get('z_step', 0.2),
        adsorbant_orientation=adsorbant_config.get('orientation', 'default'),
        ml_tasks=calc_config.get('ml_tasks', ['omat', 'omc']),
        dft_functional=dft_config.get('functional', 'pbe'),
        dft_subset_factor=calc_config.get('dft_subset_factor', 2),
        save_structures=output_config.get('save_structures', True),
        output_dir=output_config.get('output_dir', './results')
    )
    
    # Create plots
    output_dir = Path(output_config.get('output_dir', './results'))
    plot_base = output_dir / f"{adsorbant_config['type']}_{surface_config['material']}_profile"
    
    calc.create_plots(
        save_path=str(plot_base),
        formats=output_config.get('plot_formats', ['png', 'pdf'])
    )
    
    # Print summary
    binding_energies = calc.get_binding_energies()
    optimal_heights = calc.get_optimal_heights()
    
    print("\n" + "="*60)
    print("CALCULATION SUMMARY")
    print("="*60)
    print(f"System: {adsorbant_config['type']} on {surface_config['material']}{surface_config['miller_indices']}")
    
    print(f"\nBinding Energies:")
    for method, energy in binding_energies.items():
        print(f"  {method}: {energy:.4f} eV")
    
    print(f"\nOptimal Heights:")
    for method, height in optimal_heights.items():
        print(f"  {method}: {height:.1f} Å")


def main():
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle special actions
    if args.create_config:
        config = create_example_config()
        
        config_path = Path(args.create_config)
        if config_path.suffix.lower() in ['.yml', '.yaml']:
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        else:
            import json
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        print(f"Example configuration saved to: {config_path}")
        return
    
    if args.list_adsorbants:
        from energy_profile_calculator import AdsorbantLibrary
        library = AdsorbantLibrary()
        
        print("Available adsorbants:")
        for name in library.list_adsorbants():
            info = library.get_info(name)
            print(f"  {name}: {info['description']}")
            print(f"    Elements: {info['elements']}")
            print(f"    Orientations: {info['orientations']}")
        return
    
    if args.list_surfaces:
        from energy_profile_calculator import SurfaceBuilder
        builder = SurfaceBuilder()
        
        print("Supported materials and surfaces:")
        materials = builder.list_supported_materials()
        for structure, material_list in materials.items():
            print(f"\n{structure.upper()} materials: {', '.join(material_list)}")
            surfaces = builder.list_supported_surfaces(structure)
            print(f"  Supported Miller indices: {surfaces}")
        return
    
    # Load configuration
    if args.config:
        config = load_config(args.config)
        print(f"Loaded configuration from: {args.config}")
    else:
        # Build configuration from command line arguments
        try:
            config = validate_args(args)
        except ValueError as e:
            print(f"Error: {e}")
            parser.print_help()
            sys.exit(1)
    
    # Check required parameters
    if 'surface' not in config or 'adsorbant' not in config:
        print("Error: Surface and adsorbant must be specified")
        parser.print_help()
        sys.exit(1)
    
    # Run calculation
    try:
        run_calculation(config, args.verbose)
        print("\n✅ Calculation completed successfully!")
    except Exception as e:
        print(f"\n❌ Calculation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
