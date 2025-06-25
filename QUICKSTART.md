# Quick Start Guide for Energy Profile Calculator

## Installation in Your Environment

Since you already have the required dependencies (as evidenced by the successful run), you can use the package directly:

```bash
cd /mnt/borgstore/amartini/afaiyad/energy_profile_calculator
```

## Running Examples

### 1. Headless-friendly batch calculation (recommended for your environment)
```bash
~/deepmd-kit-new/bin/python3 examples/batch_example_headless.py
```

### 2. Basic single calculation
```bash
~/deepmd-kit-new/bin/python3 examples/basic_example.py
```

### 3. Convert your existing B5.py workflow
```bash
~/deepmd-kit-new/bin/python3 examples/convert_b5_example.py
```

## Key Improvements Over Original B5.py

✅ **Automatic CPU Detection**: No need to manually set `{num_cores}`
✅ **Modular Design**: Easy to reuse and extend
✅ **Error Handling**: Graceful failure recovery
✅ **Multiple Adsorbants**: Built-in library with 15+ molecules
✅ **Batch Processing**: Calculate multiple systems easily
✅ **Headless Compatible**: Works in environments without GUI
✅ **Configuration Files**: YAML/JSON config support
✅ **Command Line Interface**: Direct CLI usage

## Usage Patterns

### Python API (like your B5.py)
```python
from energy_profile_calculator import EnergyProfileCalculator

calc = EnergyProfileCalculator()
calc.setup_surface('Au', (1, 1, 1), (3, 3, 4))
calc.setup_calculators(use_ml=True, use_dft=True, 
                      dft_pseudo_dir='/home/afaiyad/QE/qe-7.4.1/pseudo')
results = calc.calculate_energy_profile('H2O')
```

### Command Line Interface
```bash
# Create config file
~/deepmd-kit-new/bin/python3 -m energy_profile_calculator.cli --create-config my_config.yaml

# Edit the config file with your preferences
nano my_config.yaml

# Run calculation
~/deepmd-kit-new/bin/python3 -m energy_profile_calculator.cli --config my_config.yaml
```

### Quick CLI Usage
```bash
~/deepmd-kit-new/bin/python3 -m energy_profile_calculator.cli \
  --surface Au --miller 1 1 1 --adsorbant H2O --ml-only --output-dir results
```

## What Just Worked in Your Test

Your test showed:
- ✅ Package imports working correctly
- ✅ Surface creation (Au(111) with 36 atoms)
- ✅ ML calculator initialization (UMA-S-1 model)
- ✅ H atom energy profile calculation (22 points)
- ✅ Both OMAT and OMC calculations completed
- ✅ Results saved to files
- ⚠️ Plotting failed due to headless environment (this is normal)

## Expected Output Files

After running calculations, you'll find:
```
batch_results/
├── H/
│   ├── H_Au(1,1,1)_profile.json    # Complete results
│   ├── H_Au(1,1,1)_profile.csv     # Energy data
│   └── omat_structure_h*.xyz       # Structure files (if enabled)
├── O/
├── H2O/
├── CO/
└── summary.txt                      # Comparison table
```

## Next Steps

1. **Run the headless batch example** - this will work perfectly in your environment
2. **Modify adsorbants list** in the batch script for your specific needs
3. **Add DFT calculations** by setting `use_dft=True` and providing pseudopotential directory
4. **Create custom adsorbants** using the custom example
5. **Use different surfaces** by changing the surface parameters

## Troubleshooting

- **"Qt platform plugin" errors**: Use the headless examples or set `MPLBACKEND=Agg`
- **Import errors**: Make sure you're using the correct Python path
- **CUDA errors**: Set `ml_device='cpu'` if GPU issues occur
- **DFT failures**: Check pseudopotential paths and QE installation

The package is working great in your environment! The only issue was the GUI/plotting in headless mode, which is now handled gracefully.
