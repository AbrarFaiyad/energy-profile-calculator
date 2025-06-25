# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-25

### Added
- Initial release of Energy Profile Calculator package
- Modular architecture with separate components for adsorbants, surfaces, calculators, and plotting
- Support for machine learning calculations via FairChem (OMAT/OMC tasks)
- Support for DFT calculations via Quantum ESPRESSO
- Comprehensive adsorbant library with 15+ predefined molecules and atoms
- Surface builder supporting FCC, BCC, and HCP crystal structures
- Automatic CPU core detection for optimized DFT calculations
- Beautiful publication-quality plots with seaborn styling
- Command-line interface with configuration file support
- Comprehensive documentation and examples
- Batch calculation capabilities
- Custom adsorbant and surface creation utilities
- Energy normalization and binding energy calculations
- Optimal height determination
- Method comparison and analysis tools

### Features
- **Adsorbants**: H2O, H2, O2, N2, CO, CO2, NH3, CH4, H, O, C, N, F, Na
- **Surfaces**: Au, Ag, Cu, Al, Ni, Pd, Pt, Rh, Ir, Pb (FCC); Fe, Cr, W, Mo, V, Nb, Ta (BCC); Zn, Cd, Ti, Zr, Mg, Be, Co, Ru, Re (HCP)
- **Miller indices**: (111), (100), (110) for FCC/BCC; (0001) for HCP
- **Output formats**: JSON, CSV data files; PNG, PDF, SVG plots; XYZ structure files
- **Configuration**: YAML and JSON configuration file support

### Documentation
- Comprehensive README with installation and usage instructions
- API reference documentation
- Multiple example scripts demonstrating different use cases
- Troubleshooting guide and performance tips
