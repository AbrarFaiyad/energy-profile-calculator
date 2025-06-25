# Energy Profile Calculator

A modular Python package for calculating adsorption energy profiles on surfaces using machine learning (ML) and density functional theory (DFT) methods.

## Features

- **Modular Design**: Easily extensible with new surfaces, adsorbants, and calculation methods
- **Multiple Calculation Methods**: Support for ML models (OMAT/OMC via FairChem) and DFT (Quantum ESPRESSO)
- **Comprehensive Adsorbant Library**: Pre-defined molecules (H2O, CO, NH3, etc.) with customizable orientations
- **Surface Builder**: Support for FCC, BCC, and HCP crystal structures with various Miller indices
- **Beautiful Visualizations**: Publication-quality plots with seaborn styling
- **Command Line Interface**: Easy-to-use CLI with configuration file support
- **Automated Analysis**: Binding energy calculations, optimal height determination, and method comparisons

## Installation

### Prerequisites

- Python 3.8 or higher
- CUDA-capable GPU (optional, for ML calculations)
- Quantum ESPRESSO (optional, for DFT calculations)

### Install from GitHub

```bash
# Clone the repository
git clone https://github.com/AbrarFaiyad/energy-profile-calculator.git
cd energy-profile-calculator

# Install in development mode
pip install -e .

# Or install directly from GitHub
pip install git+https://github.com/AbrarFaiyad/energy-profile-calculator.git
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Additional dependencies for DFT

For DFT calculations, you need:
1. Quantum ESPRESSO installed and accessible via `pw.x`
2. Pseudopotential files in UPF format
3. MPI for parallel calculations

## Quick Start

### Command Line Usage

```bash
# Generate example configuration
energy-profile --create-config example_config.yaml

# Run calculation with command line arguments
energy-profile --surface Au --miller 1 1 1 --adsorbant H2O --ml-only --output-dir results

# Run with configuration file
energy-profile --config my_config.yaml
```

### Python API Usage

```python
from energy_profile_calculator import EnergyProfileCalculator

# Initialize calculator
calc = EnergyProfileCalculator()

# Setup Au(111) surface
calc.setup_surface(
    material='Au', 
    miller_indices=(1, 1, 1), 
    size=(3, 3, 4), 
    vacuum=14.0
)

# Setup calculation methods
calc.setup_calculators(
    use_ml=True,
    use_dft=True,
    ml_model='uma-s-1',
    ml_device='cuda',
    dft_pseudo_dir='/path/to/pseudopotentials'
)

# Calculate H2O adsorption energy profile
results = calc.calculate_energy_profile(
    adsorbant='H2O',
    z_start=2.0,
    z_end=8.0,
    z_step=0.2,
    ml_tasks=['omat', 'omc'],
    output_dir='./results'
)

# Create plots
calc.create_plots(save_path='./results/h2o_au111_profile')

# Get binding energies
binding_energies = calc.get_binding_energies()
print(f"Binding energies: {binding_energies}")
```

## Configuration

### Configuration File Format

The calculator supports YAML and JSON configuration files. Here's an example:

```yaml
surface:
  material: Au
  miller_indices: [1, 1, 1]
  size: [3, 3, 4]
  vacuum: 14.0

adsorbant:
  type: H2O
  orientation: flat

calculation:
  z_start: 2.0
  z_end: 8.0
  z_step: 0.2
  use_ml: true
  use_dft: true
  ml_tasks: [omat, omc]
  dft_subset_factor: 2

ml_settings:
  model: uma-s-1
  device: cuda

dft_settings:
  functional: pbe
  ecutwfc: 80
  ecutrho: 640
  kpts: [6, 6, 1]
  occupations: smearing
  smearing: mp
  degauss: 0.01
  vdw_corr: grimme-d3
  conv_thr: 1e-8
  pseudo_dir: /path/to/pseudopotentials

output:
  save_structures: true
  output_dir: ./results
  plot_formats: [png, pdf]
```

### Available Parameters

#### Surface Parameters
- `material`: Chemical symbol (Au, Pt, Cu, etc.)
- `crystal_structure`: Override auto-detected structure (fcc, bcc, hcp)
- `miller_indices`: Surface orientation, e.g., [1, 1, 1]
- `size`: Surface unit cell size [nx, ny, nlayers]
- `vacuum`: Vacuum space above surface (Å)

#### Adsorbant Parameters
- `type`: Molecule name from library or custom definition
- `orientation`: Molecular orientation (depends on molecule)

#### Calculation Parameters
- `z_start`, `z_end`, `z_step`: Height range and increment (Å)
- `use_ml`, `use_dft`: Enable/disable calculation methods
- `ml_tasks`: List of ML tasks ['omat', 'omc']
- `dft_subset_factor`: Reduce DFT points by this factor

#### ML Settings
- `model`: ML model name (uma-s-1, etc.)
- `device`: cuda or cpu

#### DFT Settings
- `functional`: DFT functional (pbe, pbesol, etc.)
- `ecutwfc`, `ecutrho`: Plane wave cutoffs (Ry)
- `kpts`: k-point grid [kx, ky, kz]
- `pseudo_dir`: Pseudopotential directory path
- All standard Quantum ESPRESSO parameters supported

## Supported Systems

### Surfaces

#### FCC Materials
- **Metals**: Au, Ag, Cu, Al, Ni, Pd, Pt, Rh, Ir, Pb
- **Miller indices**: (1,1,1), (1,0,0), (1,1,0)

#### BCC Materials  
- **Metals**: Fe, Cr, W, Mo, V, Nb, Ta
- **Miller indices**: (1,0,0), (1,1,0), (1,1,1)

#### HCP Materials
- **Metals**: Zn, Cd, Ti, Zr, Mg, Be, Co, Ru, Re
- **Miller indices**: (0,0,0,1)

### Adsorbants

#### Molecules
- **H2O**: Water (orientations: flat, vertical)
- **H2**: Hydrogen (orientations: parallel, perpendicular)
- **O2**: Oxygen (orientations: parallel, perpendicular)
- **N2**: Nitrogen (orientations: parallel, perpendicular)
- **CO**: Carbon monoxide (orientations: parallel, perpendicular, c_down, o_down)
- **CO2**: Carbon dioxide (orientations: parallel, perpendicular)
- **NH3**: Ammonia (orientations: n_down, n_up)
- **CH4**: Methane (orientation: tetrahedral)

#### Atoms
- **H, O, C, N, F, Na**: Individual atoms

### Custom Adsorbants

You can define custom adsorbants:

```python
from energy_profile_calculator.adsorbants import create_custom_adsorbant

# Define custom molecule
custom_mol = create_custom_adsorbant(
    elements=['C', 'O', 'H'],
    positions=[(0, 0, 0), (1.2, 0, 0), (0, 1.0, 0)],
    center_position=(5.0, 5.0, 15.0)
)
```

## Advanced Usage

### Custom Surface Creation

```python
from energy_profile_calculator.surfaces import create_custom_surface

# Create custom surface
surface = create_custom_surface(
    positions=[(0, 0, 0), (2.88, 0, 0), (1.44, 2.49, 0)],
    elements=['Au', 'Au', 'Au'],
    cell=[[2.88, 0, 0], [1.44, 2.49, 0], [0, 0, 20]],
    vacuum=10.0
)
```

### Method Comparison

```python
# Get detailed comparison
binding_energies = calc.get_binding_energies()
optimal_heights = calc.get_optimal_heights()

print("Method Comparison:")
for method in binding_energies:
    print(f"{method}: {binding_energies[method]:.3f} eV at {optimal_heights[method]:.1f} Å")
```

### Batch Calculations

```python
# Run calculations for multiple adsorbants
adsorbants = ['H', 'O', 'H2O', 'CO']
results = {}

for ads in adsorbants:
    print(f"Calculating {ads}...")
    result = calc.calculate_energy_profile(
        adsorbant=ads,
        output_dir=f'./results/{ads}'
    )
    results[ads] = result
```

## Output Files

The calculator generates several output files:

### Data Files
- `{adsorbant}_{surface}_profile.json`: Complete results in JSON format
- `{adsorbant}_{surface}_profile.csv`: Energy data in CSV format

### Structure Files (if enabled)
- `{method}_structure_h{height}.xyz`: Atomic structures at each height

### Plots
- `{adsorbant}_{surface}_profile.png/pdf`: Main energy profile plot
- `{adsorbant}_{surface}_profile_summary.png/pdf`: Comparison summary

## Troubleshooting

### Common Issues

1. **CUDA out of memory**: Reduce batch size or use CPU
   ```python
   calc.setup_calculators(ml_device='cpu')
   ```

2. **Pseudopotential files not found**: Check path and file names
   ```python
   from energy_profile_calculator.utils import validate_pseudopotentials
   validate_pseudopotentials(pseudos, pseudo_dir)
   ```

3. **DFT calculation fails**: Check Quantum ESPRESSO installation
   ```bash
   which pw.x  # Should return path to executable
   ```

### Error Handling

The calculator includes comprehensive error handling:
- Missing pseudopotentials are reported with suggestions
- Failed DFT calculations continue with NaN values
- Invalid adsorbant/surface combinations are caught early

### Performance Tips

- Use `dft_subset_factor` to reduce DFT calculation points
- Enable `save_structures=False` for faster calculations
- Use CUDA for ML calculations when available
- Adjust `z_step` based on required precision vs. speed

## API Reference

### Core Classes

#### EnergyProfileCalculator
Main calculator class for energy profile calculations.

**Methods:**
- `setup_surface()`: Configure the surface
- `setup_calculators()`: Initialize ML/DFT calculators  
- `calculate_energy_profile()`: Run energy profile calculation
- `create_plots()`: Generate visualization plots
- `get_binding_energies()`: Extract binding energies
- `get_optimal_heights()`: Get optimal adsorption heights

#### AdsorbantLibrary
Library of predefined adsorbant molecules.

**Methods:**
- `get_adsorbant()`: Create adsorbant at specified position
- `list_adsorbants()`: Get available adsorbants
- `get_info()`: Get adsorbant information
- `get_elements()`: Get elements in adsorbant

#### SurfaceBuilder  
Builder for crystal surfaces.

**Methods:**
- `build_surface()`: Create surface structure
- `get_surface_info()`: Analyze surface properties
- `get_adsorption_sites()`: Find high-symmetry sites
- `list_supported_materials()`: Get supported materials

#### EnergyProfilePlotter
Plotting utilities for energy profiles.

**Methods:**
- `plot_energy_profile()`: Create main energy plot
- `plot_comparison_summary()`: Create comparison plots
- `create_method_comparison_table()`: Generate summary table

### Utility Functions

- `detect_cpu_cores()`: Auto-detect available CPU cores
- `load_config()`: Load configuration from file
- `save_results()`: Save calculation results
- `validate_pseudopotentials()`: Check pseudopotential files
- `estimate_calculation_time()`: Estimate total runtime

## Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

### Development Setup

```bash
git clone https://github.com/yourusername/energy-profile-calculator.git
cd energy-profile-calculator
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Style

We use Black for code formatting:

```bash
black energy_profile_calculator/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{energy_profile_calculator,
  title={Energy Profile Calculator: A modular package for adsorption energy calculations},
  author={AbrarFaiyad},
  year={2025},
  url={https://github.com/AbrarFaiyad/energy-profile-calculator}
}
```

## Support

- **Documentation**: [https://github.com/AbrarFaiyad/energy-profile-calculator](https://github.com/AbrarFaiyad/energy-profile-calculator)
- **Issues**: [https://github.com/AbrarFaiyad/energy-profile-calculator/issues](https://github.com/AbrarFaiyad/energy-profile-calculator/issues)
- **Discussions**: [https://github.com/AbrarFaiyad/energy-profile-calculator/discussions](https://github.com/AbrarFaiyad/energy-profile-calculator/discussions)

## Acknowledgments

- [FairChem](https://github.com/FAIR-Chem/fairchem) for ML models
- [ASE](https://wiki.fysik.dtu.dk/ase/) for atomic structure handling
- [Quantum ESPRESSO](https://www.quantum-espresso.org/) for DFT calculations
