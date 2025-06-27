#!/usr/bin/env bash

# MoS2 Energy Profile Calculation Suite - Setup and Test Script

echo "🔬 MoS2 Energy Profile Calculation Suite"
echo "========================================="

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p jobs results logs
echo "✅ Directories created"

# Check Python environment
echo ""
echo "🐍 Checking Python environment..."
python3 -c "
import sys
print(f'Python version: {sys.version}')

try:
    import ase
    print(f'✅ ASE: {ase.__version__}')
except ImportError:
    print('❌ ASE: Not found')

try:
    from fairchem.core import pretrained_mlip
    print('✅ FairChem: Available')
except ImportError:
    print('❌ FairChem: Not found')

try:
    import yaml
    print('✅ PyYAML: Available')
except ImportError:
    print('❌ PyYAML: Not found')
    
try:
    import numpy as np
    print(f'✅ NumPy: {np.__version__}')
except ImportError:
    print('❌ NumPy: Not found')
"

echo ""
echo "🧪 Testing pseudopotential checker..."
python3 check_pseudopotentials.py

echo ""
echo "📥 Testing pseudopotential downloader..."
echo "Available download options:"
echo "  python3 check_pseudopotentials.py --download    # Interactive download"
echo "  python3 check_pseudopotentials.py --auto-fix    # Automatic download" 
echo "  python3 download_pseudo.py H O Mo S             # Download specific elements"
echo "  python3 download_pseudo.py --list               # List available elements"

echo "⚙️  Testing job manager (dry run)..."
python3 job_manager.py --dry-run --max-iterations 1
echo ""

echo "📋 Setup Summary:"
echo "  - Configuration file: job_config.yaml"
echo "  - Pseudopotential checker: check_pseudopotentials.py"
echo "  - Job manager: job_manager.py"
echo "  - User interface: user_interface.py"
echo "  - Submit script: job_manager_submit.sh"
echo ""

echo "🚀 Next Steps:"
echo "  1. Review configuration: nano job_config.yaml"
echo "  2. Check pseudopotentials: python3 check_pseudopotentials.py"
echo "  3. Download missing pseudopotentials: python3 check_pseudopotentials.py --auto-fix"
echo "  4. Use interactive interface: python3 user_interface.py"
echo "  5. Or submit job manager: sbatch job_manager_submit.sh"
echo ""

echo "📚 Documentation: cat README.md"
echo "🎉 Setup complete!"
