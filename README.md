# Energy Profile Calculator

A modular Python package for calculating adsorption energy profiles on surfaces using machine learning (ML) and density functional theory (DFT) methods.

## Features

- **Modular Design**: Easily extensible with new surfaces, adsorbants, and calculation methods
- **Multiple Calculation Methods**: Support for ML models (OMAT/OMC via FairChem) and DFT (Quantum ESPRESSO)
- **Comprehensive Adsorbant Library**: 73+ pre-defined molecules including organic compounds, metal clusters, and inorganic materials
- **Advanced Surface Builder**: Support for FCC, BCC, HCP crystal structures and 26 2D materials (MoS2, graphene, etc.)
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

# Run calculation with command line arguments (now supports 73+ adsorbants and 2D materials)
energy-profile --surface Au --miller 1 1 1 --adsorbant H2O --ml-only --output-dir results
energy-profile --surface MoS2 --adsorbant Au2 --ml-only --output-dir results_2d

# Run with configuration file
energy-profile --config my_config.yaml
```

### Python API Usage

```python
from energy_profile_calculator import EnergyProfileCalculator

# Initialize calculator
calc = EnergyProfileCalculator()

# Setup MoS2 monolayer surface (2D material)
calc.setup_surface(
    material='MoS2', 
    size=(3, 3), 
    vacuum=15.0,
    surface_type='2d'
)

# Or setup traditional Au(111) surface
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

# Calculate H2O adsorption energy profile (now supports 73+ adsorbants)
results = calc.calculate_energy_profile(
    adsorbant='H2O',  # Or try: 'Au2', 'F4TCNQ', 'ZnO', 'tetracene', etc.
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

#### Traditional Crystal Surfaces

##### FCC Materials
- **Metals**: Au, Ag, Cu, Al, Ni, Pd, Pt, Rh, Ir, Pb
- **Miller indices**: (1,1,1), (1,0,0), (1,1,0)

##### BCC Materials  
- **Metals**: Fe, Cr, W, Mo, V, Nb, Ta
- **Miller indices**: (1,0,0), (1,1,0), (1,1,1)

##### HCP Materials
- **Metals**: Zn, Cd, Ti, Zr, Mg, Be, Co, Ru, Re
- **Miller indices**: (0,0,0,1)

#### 2D Materials (26 types)

##### Transition Metal Dichalcogenides (TMDCs)
- **MoS2, MoSe2, MoTe2**: Molybdenum dichalcogenides
- **WS2, WSe2, WTe2**: Tungsten dichalcogenides  
- **TaS2, TaSe2**: Tantalum dichalcogenides
- **NbS2, NbSe2**: Niobium dichalcogenides
- **ReS2, ReSe2**: Rhenium dichalcogenides
- **PtS2, PtSe2**: Platinum dichalcogenides
- **PdS2, PdSe2**: Palladium dichalcogenides

##### Carbon-based Materials
- **Graphene**: Single-layer carbon sheets
- **h-BN**: Hexagonal boron nitride

##### Phosphorus-based Materials  
- **Phosphorene**: Black phosphorus monolayer
- **AsP**: Arsenide phosphide

##### MXenes
- **Ti3C2**: Titanium carbide MXene
- **V2C**: Vanadium carbide MXene
- **Nb2C**: Niobium carbide MXene

##### Other 2D Materials
- **Silicene**: Silicon analog of graphene
- **Germanene**: Germanium analog of graphene

### Adsorbants (73+ total)

#### Simple Molecules
- **H2O**: Water (orientations: flat, vertical)
- **H2**: Hydrogen (orientations: parallel, perpendicular)
- **O2**: Oxygen (orientations: parallel, perpendicular)
- **N2**: Nitrogen (orientations: parallel, perpendicular)
- **CO**: Carbon monoxide (orientations: parallel, perpendicular, c_down, o_down)
- **CO2**: Carbon dioxide (orientations: parallel, perpendicular)
- **NH3**: Ammonia (orientations: n_down, n_up)
- **CH4**: Methane (orientation: tetrahedral)

#### Individual Atoms
- **H, O, C, N, F, Na**: Individual atoms

#### Metal Clusters (24 types)
##### Noble Metals
- **Au, Ag, Pt, Pd**: Gold, silver, platinum, palladium clusters
- **Ir, Rh, Ru, Re**: Iridium, rhodium, ruthenium, rhenium clusters

##### Transition Metals
- **Ti, Cr, V**: Titanium, chromium, vanadium clusters
- **Fe, Co, Ni, Mn**: Iron, cobalt, nickel, manganese clusters
- **Cu, Zn, Cd**: Copper, zinc, cadmium clusters

##### Other Metals
- **Al**: Aluminum clusters
- **Ta, Nb, W**: Tantalum, niobium, tungsten clusters
- **Li, Na**: Lithium, sodium clusters

#### Inorganic Molecules (12 types)
##### Metal Oxides
- **Sb2O3**: Antimony trioxide
- **ZnO**: Zinc oxide
- **TiO2**: Titanium dioxide

##### Non-metal Elements
- **F, P, N, B**: Fluorine, phosphorus, nitrogen, boron
- **Si, Cl, S**: Silicon, chlorine, sulfur
- **Se, Te, O**: Selenium, tellurium, oxygen

#### Complex Organic Molecules (7 types)
##### Electron Acceptors
- **F4TCNQ**: 2,3,5,6-tetrafluoro-7,7,8,8-tetracyanoquinodimethane
- **PTCDA**: Perylene-3,4,9,10-tetracarboxylic dianhydride
- **TCNQ**: Tetracyanoquinodimethane
- **TCNE**: Tetracyanoethylene

##### Aromatic Compounds
- **Tetracene**: Polycyclic aromatic hydrocarbon
- **TTF**: Tetrathiafulvalene (electron donor)
- **Benzyl viologen**: Electroactive bipyridinium derivative

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

### 2D Material Surfaces

```python
from energy_profile_calculator.surfaces import SurfaceBuilder

# Initialize surface builder
surface_builder = SurfaceBuilder()

# Create MoS2 monolayer
mos2_surface = surface_builder.build_2d_material(
    material='MoS2',
    size=(3, 3),
    vacuum=15.0
)

# List available 2D materials
materials_2d = surface_builder.list_2d_materials()
print(f"Available 2D materials: {materials_2d}")

# Get material information
info = surface_builder.get_2d_material_info('graphene')
print(f"Graphene lattice parameter: {info['lattice_param']} Å")
```

### Metal Cluster Adsorbants

```python
from energy_profile_calculator.adsorbants import AdsorbantLibrary

# Initialize adsorbant library
ads_lib = AdsorbantLibrary()

# Create gold dimer
au_dimer = ads_lib.get_adsorbant('Au2', position=(0, 0, 5), orientation='parallel')

# Create titanium cluster
ti_cluster = ads_lib.get_adsorbant('Ti2', position=(2, 2, 4), orientation='perpendicular')

# List all metal clusters
metal_clusters = [ads for ads in ads_lib.list_adsorbants() 
                 if ads_lib.get_info(ads)['category'] == 'metal_cluster']
print(f"Available metal clusters: {metal_clusters}")
```

### Complex Organic Molecules

```python
# Create organic electron acceptor
f4tcnq = ads_lib.get_adsorbant('F4TCNQ', position=(0, 0, 3), orientation='flat')

# Create aromatic compound
tetracene = ads_lib.get_adsorbant('tetracene', position=(1, 1, 4), orientation='flat')

# List organic molecules
organic_mols = [ads for ads in ads_lib.list_adsorbants() 
                if ads_lib.get_info(ads)['category'] == 'organic']
print(f"Available organic molecules: {organic_mols}")
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
# Run calculations for multiple adsorbants including new types
adsorbants = ['H', 'O', 'H2O', 'CO', 'Au2', 'ZnO', 'F4TCNQ', 'tetracene']
results = {}

for ads in adsorbants:
    print(f"Calculating {ads}...")
    result = calc.calculate_energy_profile(
        adsorbant=ads,
        output_dir=f'./results/{ads}'
    )
    results[ads] = result

# Compare different material categories
metal_clusters = ['Au2', 'Pt2', 'Ti2']
organic_molecules = ['F4TCNQ', 'tetracene', 'TCNQ']
inorganic_molecules = ['ZnO', 'TiO2', 'Sb2O3']

# Run systematic study
categories = {
    'metal_clusters': metal_clusters,
    'organic': organic_molecules, 
    'inorganic': inorganic_molecules
}

for category, molecules in categories.items():
    print(f"\nStudying {category}:")
    for mol in molecules:
        result = calc.calculate_energy_profile(
            adsorbant=mol,
            output_dir=f'./results/{category}/{mol}'
        )
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
Comprehensive library of 73+ predefined adsorbant molecules.

**Methods:**
- `get_adsorbant()`: Create adsorbant at specified position
- `list_adsorbants()`: Get all available adsorbants (73+ total)
- `get_info()`: Get adsorbant information and category
- `get_elements()`: Get elements in adsorbant
- `list_by_category()`: Get adsorbants by type (molecules, metal_clusters, organic, inorganic)

### SurfaceBuilder  
Builder for crystal surfaces and 2D materials.

**Methods:**
- `build_surface()`: Create traditional crystal surface structure
- `build_2d_material()`: Create 2D material surface (MoS2, graphene, etc.)
- `get_surface_info()`: Analyze surface properties
- `get_adsorption_sites()`: Find high-symmetry sites
- `list_supported_materials()`: Get supported traditional materials
- `list_2d_materials()`: Get available 2D materials (26 types)
- `get_2d_material_info()`: Get 2D material properties

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
