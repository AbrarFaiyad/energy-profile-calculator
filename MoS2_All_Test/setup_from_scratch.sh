#!/bin/bash
# Complete Setup Script for MoS2 Energy Profile Calculations
# Run this on a new machine to set everything up from scratch

echo "🚀 MoS2 Energy Profile Calculator - Complete Setup"
echo "=================================================="
echo "This script will set up everything needed for energy profile calculations"
echo

# Step 1: Check prerequisites
echo "📋 Step 1: Checking prerequisites..."
echo

# Check if we're on a cluster with SLURM
if command -v sbatch &> /dev/null; then
    echo "✅ SLURM detected - cluster mode available"
    CLUSTER_MODE=true
else
    echo "⚠️  SLURM not found - will use local mode"
    CLUSTER_MODE=false
fi

# Check for conda/python
if command -v conda &> /dev/null; then
    echo "✅ Conda found"
else
    echo "❌ Conda not found - please install Anaconda/Miniconda first"
    echo "   Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check for git
if command -v git &> /dev/null; then
    echo "✅ Git found"
else
    echo "❌ Git not found - please install git first"
    exit 1
fi

echo

# Step 2: Clone the repository
echo "📥 Step 2: Getting the energy profile calculator..."
echo

if [ ! -d "energy_profile_calculator" ]; then
    echo "Cloning the energy profile calculator repository..."
    # Replace with actual repository URL when available
    echo "⚠️  You'll need to get the energy_profile_calculator package"
    echo "   This setup assumes you have the package available"
    echo
    echo "Expected directory structure:"
    echo "energy_profile_calculator/"
    echo "├── energy_profile_calculator/     # Main package"
    echo "│   ├── core.py"
    echo "│   ├── adsorbants.py"
    echo "│   ├── surfaces.py"
    echo "│   └── ..."
    echo "└── MoS2_All_Test/                # Unified workflow"
    echo "    ├── unified_workflow.py"
    echo "    ├── workflow_config.yaml"
    echo "    └── ..."
    echo
    
    read -p "Do you have the energy_profile_calculator package? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Please obtain the energy_profile_calculator package first"
        exit 1
    fi
else
    echo "✅ energy_profile_calculator directory found"
fi

echo

# Step 3: Set up Python environment
echo "🐍 Step 3: Setting up Python environment..."
echo

# Create conda environment if it doesn't exist
if conda env list | grep -q "energy_calc"; then
    echo "✅ energy_calc environment already exists"
else
    echo "Creating conda environment: energy_calc"
    conda create -n energy_calc python=3.9 -y
fi

echo "Activating environment and installing packages..."
source ~/anaconda3/etc/profile.d/conda.sh  # or wherever conda is installed
conda activate energy_calc

# Install required packages
echo "Installing Python packages..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install ase numpy matplotlib pyyaml
pip install fairchem-core  # For ML models

echo

# Step 4: Set up directories
echo "📁 Step 4: Setting up directories..."
echo

cd energy_profile_calculator/MoS2_All_Test

# Create necessary directories
mkdir -p unified_results logs job_scripts
mkdir -p unified_results/{ml_calculations,dft_calculations,ml_vs_dft,reports}

echo "✅ Directory structure created"
echo

# Step 5: Configure for your system
echo "⚙️  Step 5: System configuration..."
echo

echo "Current working directory: $(pwd)"

# Check if configuration exists
if [ ! -f "workflow_config.yaml" ]; then
    echo "Creating default workflow_config.yaml..."
    python unified_workflow.py --help > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Configuration file will be created on first run"
    else
        echo "❌ Error: unified_workflow.py not working correctly"
    fi
fi

echo

# Step 6: Test the setup
echo "🧪 Step 6: Testing the setup..."
echo

echo "Testing unified workflow..."
python unified_workflow.py --dry-run

if [ $? -eq 0 ]; then
    echo "✅ Basic test successful!"
else
    echo "❌ Test failed - check the error messages above"
    exit 1
fi

echo

# Step 7: Instructions for different environments
echo "📋 Step 7: Next steps based on your environment..."
echo

if [ "$CLUSTER_MODE" = true ]; then
    echo "🖥️  CLUSTER ENVIRONMENT DETECTED"
    echo "================================"
    echo
    echo "You can run the workflow in several ways:"
    echo
    echo "Option 1 - Submit to cluster (recommended):"
    echo "  sbatch submit_unified_workflow.sh"
    echo
    echo "Option 2 - Interactive testing:"
    echo "  srun --partition=gpu --gres=gpu:1 --time=1:00:00 --pty bash"
    echo "  python unified_workflow.py --local --ml-only"
    echo
    echo "Option 3 - Dry run (see what would happen):"
    echo "  python unified_workflow.py --dry-run"
    echo
    echo "⚠️  IMPORTANT: Update workflow_config.yaml for your cluster!"
    echo "   Edit partition names, module loading, and resource limits"
else
    echo "🖥️  LOCAL ENVIRONMENT DETECTED"
    echo "============================="
    echo
    echo "You can run the workflow locally:"
    echo
    echo "Option 1 - Full local workflow:"
    echo "  python unified_workflow.py --local"
    echo
    echo "Option 2 - ML only (faster testing):"
    echo "  python unified_workflow.py --local --ml-only"
    echo
    echo "Option 3 - Single adsorbant test:"
    echo "  python unified_workflow.py --run-single-ml Au2 --output-dir test_output"
    echo
fi

echo

# Step 8: Pseudopotential setup
echo "⚛️  Step 8: Pseudopotential setup..."
echo

echo "Checking pseudopotentials..."
if [ -f "check_pseudopotentials.py" ]; then
    python check_pseudopotentials.py
    
    echo
    echo "If pseudopotentials are missing, you can:"
    echo "  python check_pseudopotentials.py --auto-fix"
    echo "  python download_pseudo.py --all"
else
    echo "⚠️  Pseudopotential checker not found"
fi

echo

# Final summary
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo
echo "📁 You are now in: $(pwd)"
echo "🐍 Environment: energy_calc (activate with: conda activate energy_calc)"
echo
echo "🚀 Ready to run calculations!"
echo
echo "Quick start commands:"
echo "  conda activate energy_calc                    # Activate environment"
echo "  python unified_workflow.py --dry-run          # See what would run"
echo "  python unified_workflow.py --local --ml-only  # Test locally"
if [ "$CLUSTER_MODE" = true ]; then
    echo "  sbatch submit_unified_workflow.sh             # Submit to cluster"
fi
echo
echo "📚 Check README.md for detailed usage instructions"
echo "🔧 Edit workflow_config.yaml to customize for your system"
echo
echo "Happy calculating! 🧬⚡"
