#!/bin/bash
# Complete Setup Script for MoS2 Energy Profile Calculations
# Run this on a cluster to set everything up from scratch

echo "🚀 MoS2 Energy Profile Calculator - Complete Cluster Setup"
echo "==========================================================="
echo "This script will set up everything needed for energy profile calculations"
echo "on a cluster environment with SLURM scheduler"
echo

# Step 1: Load required modules and check prerequisites
echo "📋 Step 1: Loading cluster modules and checking prerequisites..."
echo

echo "Loading required modules..."
module load git
module load anaconda3
module load cuda
module load mpich
module load quantum-espresso

echo "✅ All cluster modules loaded"

# Verify modules are working
echo "Verifying module availability..."

if command -v git &> /dev/null; then
    echo "✅ Git available: $(git --version)"
else
    echo "❌ Git not available after module load"
    exit 1
fi

if command -v conda &> /dev/null; then
    echo "✅ Conda available: $(conda --version)"
else
    echo "❌ Conda not available after module load"
    exit 1
fi

if command -v nvcc &> /dev/null; then
    echo "✅ CUDA available: $(nvcc --version | head -1)"
else
    echo "⚠️  CUDA not detected (may be okay for CPU-only nodes)"
fi

if command -v pw.x &> /dev/null; then
    echo "✅ Quantum ESPRESSO available: $(pw.x --version | head -1)"
else
    echo "❌ Quantum ESPRESSO not available"
    exit 1
fi

if command -v sbatch &> /dev/null; then
    echo "✅ SLURM detected - cluster mode enabled"
    CLUSTER_MODE=true
else
    echo "❌ SLURM not found - this script is for cluster environments"
    exit 1
fi

echo

# Step 2: Clone the repository
echo "📥 Step 2: Cloning the energy profile calculator repository..."
echo

REPO_URL="https://github.com/AbrarFaiyad/energy-profile-calculator.git"
WORK_DIR="energy-profile-calculator"

if [ ! -d "$WORK_DIR" ]; then
    echo "Cloning repository from: $REPO_URL"
    git clone $REPO_URL
    
    if [ $? -eq 0 ]; then
        echo "✅ Repository cloned successfully"
    else
        echo "❌ Failed to clone repository"
        echo "Please check your internet connection and repository access"
        exit 1
    fi
else
    echo "✅ Repository directory already exists: $WORK_DIR"
    echo "Updating to latest version..."
    cd $WORK_DIR
    git pull
    cd ..
fi

echo "Repository contents:"
ls -la $WORK_DIR/

echo

# Step 3: Set up Python environment
echo "🐍 Step 3: Setting up Python environment..."
echo

ENV_NAME="energy_calc"

# Create conda environment if it doesn't exist
if conda env list | grep -q "$ENV_NAME"; then
    echo "✅ $ENV_NAME environment already exists"
    echo "Updating existing environment..."
else
    echo "Creating new conda environment: $ENV_NAME"
    conda create -n $ENV_NAME python=3.9 -y
    
    if [ $? -eq 0 ]; then
        echo "✅ Conda environment created successfully"
    else
        echo "❌ Failed to create conda environment"
        exit 1
    fi
fi

echo "Activating environment: $ENV_NAME"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

if [ "$CONDA_DEFAULT_ENV" = "$ENV_NAME" ]; then
    echo "✅ Environment activated: $CONDA_DEFAULT_ENV"
else
    echo "❌ Failed to activate environment"
    exit 1
fi

# Install required packages
echo "Installing required Python packages..."

# Install PyTorch with CUDA support
echo "Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install core scientific packages
echo "Installing scientific packages..."
pip install numpy scipy matplotlib pandas

# Install ASE (Atomic Simulation Environment)
echo "Installing ASE..."
pip install ase

# Install YAML parser
echo "Installing PyYAML..."
pip install pyyaml

# Install Fairchem (for ML models)
echo "Installing Fairchem for ML models..."
pip install fairchem-core

# Install additional packages for visualization
echo "Installing visualization packages..."
pip install seaborn plotly

# Verify key packages
echo "Verifying package installation..."
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import ase; print(f'ASE: {ase.__version__}')"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import yaml; print('PyYAML: OK')"

echo "✅ All Python packages installed successfully"

echo

# Step 4: Set up directories and navigate to workspace
echo "📁 Step 4: Setting up workspace directories..."
echo

cd $WORK_DIR/MoS2_All_Test

if [ ! -f "unified_workflow.py" ]; then
    echo "❌ Error: unified_workflow.py not found in MoS2_All_Test directory"
    echo "Directory contents:"
    ls -la
    exit 1
fi

echo "✅ Found unified_workflow.py"
echo "Current working directory: $(pwd)"

# Create necessary directories
echo "Creating directory structure..."
mkdir -p unified_results logs job_scripts
mkdir -p unified_results/{ml_calculations,dft_calculations,ml_vs_dft,reports}

echo "✅ Directory structure created:"
tree unified_results/ 2>/dev/null || ls -la unified_results/
echo

# Step 5: Configure workflow for your cluster
echo "⚙️  Step 5: Configuring workflow for your cluster..."
echo

# Test if the unified workflow is working
echo "Testing unified workflow..."
python unified_workflow.py --help > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ unified_workflow.py is working"
else
    echo "❌ Error with unified_workflow.py"
    echo "Checking Python path and imports..."
    python -c "import sys; print('Python path:'); [print(p) for p in sys.path]"
    exit 1
fi

# Generate default configuration if it doesn't exist
if [ ! -f "workflow_config.yaml" ]; then
    echo "Creating default workflow_config.yaml..."
    python unified_workflow.py --dry-run > /dev/null 2>&1
    
    if [ -f "workflow_config.yaml" ]; then
        echo "✅ Default configuration created"
    else
        echo "❌ Failed to create configuration file"
        exit 1
    fi
else
    echo "✅ workflow_config.yaml already exists"
fi

# Show current configuration
echo "Current workflow configuration:"
echo "Adsorbants configured: $(python -c "import yaml; config=yaml.safe_load(open('workflow_config.yaml')); print(len(config.get('adsorbants', [])))")"
echo "ML calculator: $(python -c "import yaml; config=yaml.safe_load(open('workflow_config.yaml')); print(config.get('ml_calculator', 'Not set'))")"

echo

# Step 6: Test the complete setup
echo "🧪 Step 6: Testing the complete setup..."
echo

echo "Running comprehensive dry-run test..."
python unified_workflow.py --dry-run

if [ $? -eq 0 ]; then
    echo "✅ Dry-run test successful!"
    echo "✅ Setup is working correctly"
else
    echo "❌ Dry-run test failed"
    echo "Please check the error messages above"
    exit 1
fi

# Test import of key modules
echo "Testing Python module imports..."
python -c "
try:
    from energy_profile_calculator.core import EnergyProfileCalculator
    from energy_profile_calculator.adsorbants import AdsorbantLibrary
    from energy_profile_calculator.surfaces import SurfaceBuilder
    print('✅ All energy_profile_calculator modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Module import test failed"
    exit 1
fi

echo

echo

# Step 8: Final cluster-specific instructions
echo "📋 Step 8: Cluster-specific setup and usage instructions..."
echo

echo "🖥️  CLUSTER ENVIRONMENT SETUP COMPLETE"
echo "======================================"
echo
echo "📁 Working directory: $(pwd)"
echo "🐍 Conda environment: $ENV_NAME"
echo "🚀 Ready for energy profile calculations!"
echo

echo "🔧 CLUSTER-SPECIFIC COMMANDS:"
echo "============================="
echo
echo "1. Load modules (add to your .bashrc or run each time):"
echo "   module load git anaconda3 cuda mpich quantum-espresso"
echo
echo "2. Activate Python environment:"
echo "   conda activate $ENV_NAME"
echo
echo "3. Navigate to workspace:"
echo "   cd $(pwd)"
echo

echo "🚀 READY TO RUN CALCULATIONS:"
echo "============================="
echo
echo "Quick test (1-2 minutes):"
echo "  python unified_workflow.py --dry-run"
echo
echo "Local test on current node (ML only, ~10 minutes):"
echo "  python unified_workflow.py --local --ml-only"
echo
echo "Single adsorbant test:"
echo "  python unified_workflow.py --run-single-ml Au2 --output-dir test_output"
echo
echo "Full workflow submission to cluster:"
echo "  sbatch submit_unified_workflow.sh"
echo

echo "📊 EXPECTED RUNTIMES:"
echo "===================="
echo "• Dry run: ~30 seconds"
echo "• Single ML calculation: ~30 minutes"
echo "• Full ML workflow (30 adsorbants): ~15 hours"
echo "• Full ML+DFT workflow: ~2-3 days"
echo

echo "📚 IMPORTANT FILES:"
echo "=================="
echo "• workflow_config.yaml - Main configuration (edit for your needs)"
echo "• unified_workflow.py - Main script (don't edit unless needed)"
echo "• submit_unified_workflow.sh - SLURM submission script"
echo "• README.md - Detailed documentation"
echo

echo "⚠️  CLUSTER-SPECIFIC CUSTOMIZATION:"
echo "==================================="
echo "Edit workflow_config.yaml to match your cluster:"
echo "• Partition names (currently: cenvalarc.gpu, gpu, long, etc.)"
echo "• Account name (currently: cenvalos)"
echo "• Resource limits (cores, memory, time)"
echo "• Module loading commands"
echo

echo "🎉 SETUP COMPLETE!"
echo "=================="
echo "The MoS2 energy profile calculator is ready to use!"
echo "Start with a dry run to verify everything is working:"
echo
echo "  python unified_workflow.py --dry-run"
echo
echo "Happy calculating! 🧬⚡"
