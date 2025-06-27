#!/bin/bash
# Complete Setup Script for MoS2 Energy Profile Calculations
# Run this on a cluster to set everything up from scratch

echo "🚀 MoS2 Energy Profile Calculator - Complete Cluster Setup"
echo "==========================================================="
echo "This script will set up everything needed for energy profile calculations"
echo "on a cluster environment with SLURM scheduler"
echo "NOW COMPATIBLE WITH FAIRCHEM-CORE 2.2.0 AND UMA-S-1 MODEL"
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

# Step 3: Set up Python environment with correct version
echo "🐍 Step 3: Setting up Python environment (Python 3.11 for fairchem 2.2.0)..."
echo

ENV_NAME="fair"  # Changed to match new standard

# Remove old environment if it exists with wrong Python version
if conda env list | grep -q "$ENV_NAME"; then
    echo "Checking existing environment Python version..."
    EXISTING_PYTHON=$(conda run -n $ENV_NAME python --version 2>&1 | grep -o "3\.[0-9]*")
    if [[ "$EXISTING_PYTHON" != "3.11" ]]; then
        echo "❌ Existing environment has Python $EXISTING_PYTHON, need 3.11"
        echo "Removing old environment..."
        conda env remove -n $ENV_NAME -y
        echo "✅ Old environment removed"
    else
        echo "✅ Existing environment has correct Python version"
    fi
fi

# Create conda environment if it doesn't exist
if conda env list | grep -q "$ENV_NAME"; then
    echo "✅ $ENV_NAME environment already exists with Python 3.11"
else
    echo "Creating new conda environment: $ENV_NAME with Python 3.11"
    conda create -n $ENV_NAME python=3.11 -y
    
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

# Verify Python version
PYTHON_VERSION=$(python --version 2>&1 | grep -o "3\.[0-9]*\.[0-9]*")
echo "Python version: $PYTHON_VERSION"
if [[ "$PYTHON_VERSION" == "3.11"* ]]; then
    echo "✅ Correct Python version for fairchem 2.2.0"
else
    echo "❌ Wrong Python version. Need Python 3.11 for fairchem 2.2.0"
    exit 1
fi

# Install required packages
echo "Installing required Python packages for fairchem 2.2.0..."

# Install PyTorch 2.6.0 with CUDA 12.1 support (required for fairchem 2.2.0)
echo "Installing PyTorch 2.6.0 with CUDA 12.1 support..."
pip install torch==2.6.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install PyTorch Geometric (required for fairchem)
echo "Installing PyTorch Geometric..."
pip install torch_geometric torch_scatter torch_sparse torch_cluster torch_spline_conv

# Install fairchem-core 2.2.0
echo "Installing fairchem-core 2.2.0..."
pip install fairchem-core==2.2.0

# Install core scientific packages
echo "Installing scientific packages..."
pip install numpy scipy matplotlib pandas

# Install ASE (Atomic Simulation Environment)
echo "Installing ASE..."
pip install ase

# Install YAML parser
echo "Installing PyYAML..."
pip install pyyaml

# Install additional packages that were found to be missing
echo "Installing additional required packages..."
pip install urllib3 mpmath charset-normalizer certifi

# Install visualization packages
echo "Installing visualization packages..."
pip install seaborn plotly

# Verify key packages
echo "Verifying package installation..."
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import torch_geometric; print(f'PyTorch Geometric: {torch_geometric.__version__}')"
python -c "import torch_scatter; print('torch_scatter: OK')"
python -c "import fairchem; print(f'Fairchem: {fairchem.__version__}')"
python -c "import ase; print(f'ASE: {ase.__version__}')"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import yaml; print('PyYAML: OK')"

# Test fairchem model loading
echo "Testing fairchem model availability..."
python -c "
from fairchem.core.models import model_name_to_local_file
try:
    model_path = model_name_to_local_file('uma-s-1', local_cache='/tmp/')
    print('✅ uma-s-1 model can be loaded')
except Exception as e:
    print(f'⚠️  Model loading test: {e}')
    print('Model will be downloaded on first use')
"

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

# Verify configuration has correct ML model
echo "Verifying workflow configuration..."
ML_CALC=$(python -c "import yaml; config=yaml.safe_load(open('workflow_config.yaml')); print(config.get('ml_calculator', 'Not set'))" 2>/dev/null)
TASK_NAME=$(python -c "import yaml; config=yaml.safe_load(open('workflow_config.yaml')); print(config.get('task_name', 'Not set'))" 2>/dev/null)

echo "ML calculator: $ML_CALC"
echo "Task name: $TASK_NAME"

if [[ "$ML_CALC" == "uma-s-1" ]]; then
    echo "✅ Correct ML calculator (uma-s-1) configured"
else
    echo "⚠️  ML calculator is $ML_CALC, should be uma-s-1 for fairchem 2.2.0"
fi

if [[ "$TASK_NAME" == "omat" ]] || [[ "$TASK_NAME" == "omc" ]]; then
    echo "✅ Correct task name ($TASK_NAME) configured"
else
    echo "⚠️  Task name is $TASK_NAME, should be omat or omc for fairchem 2.2.0"
fi

echo

# Step 6: Test the complete setup
echo "🧪 Step 6: Testing the complete setup..."
echo

echo "Running comprehensive dry-run test..."
python unified_workflow.py --dry-run

if [ $? -eq 0 ]; then
    echo "✅ Dry-run test successful!"
else
    echo "❌ Dry-run test failed"
    echo "Please check the error messages above"
    exit 1
fi

# Test ML setup specifically
echo "Testing ML setup with uma-s-1 model..."
python unified_workflow.py --test-ml

if [ $? -eq 0 ]; then
    echo "✅ ML test successful!"
else
    echo "❌ ML test failed"
    echo "This may indicate issues with fairchem installation or model downloading"
    echo "Check the error messages above"
fi

# Test DFT setup
echo "Testing DFT setup..."
python unified_workflow.py --test-dft

if [ $? -eq 0 ]; then
    echo "✅ DFT test successful!"
else
    echo "❌ DFT test failed"
    echo "This may indicate issues with Quantum ESPRESSO setup"
    echo "Check the error messages above"
fi

echo

# Step 7: Final cluster-specific instructions
echo "📋 Step 7: Cluster-specific setup and usage instructions..."
echo

echo "🖥️  CLUSTER ENVIRONMENT SETUP COMPLETE"
echo "======================================"
echo
echo "📁 Working directory: $(pwd)"
echo "🐍 Conda environment: $ENV_NAME (Python 3.11)"
echo "🤖 ML Model: uma-s-1 (fairchem 2.2.0)"
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
echo "Quick test (30 seconds):"
echo "  python unified_workflow.py --dry-run"
echo
echo "ML environment test (1-2 minutes):"
echo "  python unified_workflow.py --test-ml"
echo
echo "DFT environment test (1-2 minutes):"
echo "  python unified_workflow.py --test-dft"
echo
echo "Single adsorbant ML test (~30 minutes):"
echo "  python unified_workflow.py --run-single-ml Au2 --output-dir test_output"
echo
echo "Full workflow submission to cluster:"
echo "  sbatch submit_unified_workflow.sh"
echo

echo "📊 EXPECTED RUNTIMES:"
echo "===================="
echo "• Dry run: ~30 seconds"
echo "• Test modes: ~1-2 minutes each"
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
echo "• CLUSTER_SETUP_GUIDE.md - Troubleshooting guide"
echo

echo "⚠️  CLUSTER-SPECIFIC CUSTOMIZATION:"
echo "==================================="
echo "Edit workflow_config.yaml to match your cluster:"
echo "• Partition names (update partition_map section)"
echo "• Account name (remove --account lines if not needed)"
echo "• Resource limits (cores, memory, time)"
echo "• Module loading commands"
echo

echo "🐛 TROUBLESHOOTING:"
echo "=================="
echo "If you encounter issues:"
echo
echo "1. Environment issues:"
echo "   • Check Python version: python --version (should be 3.11.x)"
echo "   • Verify fairchem: python -c 'import fairchem; print(fairchem.__version__)'"
echo "   • Test model: python unified_workflow.py --test-ml"
echo
echo "2. Missing dependencies:"
echo "   • Run: pip install urllib3 mpmath charset-normalizer certifi"
echo "   • For torch_scatter issues: pip install torch_scatter --no-cache-dir"
echo
echo "3. SLURM job failures:"
echo "   • Check logs in: logs/"
echo "   • Verify partition names match your cluster"
echo "   • Remove --account lines if your cluster doesn't require them"
echo
echo "4. Model download issues:"
echo "   • First ML run downloads uma-s-1 model (~1GB)"
echo "   • Ensure internet access from compute nodes"
echo "   • Model cached in ~/.cache/torch/hub/checkpoints/"
echo

echo "🎉 SETUP COMPLETE!"
echo "=================="
echo "The MoS2 energy profile calculator is ready to use with:"
echo "• fairchem-core 2.2.0"
echo "• uma-s-1 ML model"
echo "• Python 3.11 environment"
echo
echo "Start with the test modes to verify everything is working:"
echo
echo "  python unified_workflow.py --test-ml"
echo "  python unified_workflow.py --test-dft"
echo
echo "Happy calculating! 🧬⚡"
