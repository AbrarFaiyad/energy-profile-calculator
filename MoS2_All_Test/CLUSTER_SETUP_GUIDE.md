# 🚀 Quick Start Guide for Cluster Setup

## Prerequisites
- Access to a cluster with SLURM scheduler
- Modules available: `git`, `anaconda3`, `cuda`, `mpich`, `quantum-espresso`

## One-Command Setup

```bash
# Download and run the setup script
wget https://raw.githubusercontent.com/AbrarFaiyad/energy-profile-calculator/main/MoS2_All_Test/setup_from_scratch.sh
chmod +x setup_from_scratch.sh
./setup_from_scratch.sh
```

## What the Setup Script Does

1. **🔧 Loads cluster modules**: git, anaconda3, cuda, mpich, quantum-espresso
2. **📥 Clones repository**: Downloads from https://github.com/AbrarFaiyad/energy-profile-calculator.git
3. **🐍 Creates conda environment**: `energy_calc` with Python 3.9
4. **📦 Installs packages**: PyTorch, ASE, Fairchem, and all dependencies
5. **📁 Sets up directories**: Creates workspace structure
6. **⚙️ Configures workflow**: Creates `workflow_config.yaml`
7. **🧪 Tests setup**: Runs comprehensive tests
8. **✅ Verifies everything**: Ensures all components work

## After Setup

### Load Environment (run each time)
```bash
module load git anaconda3 cuda mpich quantum-espresso
conda activate energy_calc
cd energy-profile-calculator/MoS2_All_Test
```

### Quick Test
```bash
python unified_workflow.py --dry-run
```

### Run Calculations
```bash
# Test locally (single node)
python unified_workflow.py --local --ml-only

# Submit to cluster (full workflow)
sbatch submit_unified_workflow.sh
```

## Expected Output from Setup

```
🚀 MoS2 Energy Profile Calculator - Complete Cluster Setup
===========================================================
📋 Step 1: Loading cluster modules and checking prerequisites...
✅ All cluster modules loaded
✅ Git available: git version 2.x.x
✅ Conda available: conda 4.x.x
✅ CUDA available: Cuda compilation tools
✅ Quantum ESPRESSO available: ESPRESSO
✅ SLURM detected - cluster mode enabled

📥 Step 2: Cloning the energy profile calculator repository...
✅ Repository cloned successfully

🐍 Step 3: Setting up Python environment...
✅ Conda environment created successfully
✅ Environment activated: energy_calc
✅ All Python packages installed successfully

📁 Step 4: Setting up workspace directories...
✅ Found unified_workflow.py
✅ Directory structure created

⚙️ Step 5: Configuring workflow for your cluster...
✅ unified_workflow.py is working
✅ Default configuration created

🧪 Step 6: Testing the complete setup...
✅ Dry-run test successful!
✅ All energy_profile_calculator modules imported successfully

🎉 SETUP COMPLETE!
==================
The MoS2 energy profile calculator is ready to use!
```

## Troubleshooting

### Module Loading Issues
```bash
# Check available modules
module avail

# Load specific versions if needed
module load anaconda3/2023.09
module load cuda/12.1
```

### Conda Environment Issues
```bash
# If conda not found
source $(conda info --base)/etc/profile.d/conda.sh

# If environment creation fails
conda clean --all
conda create -n energy_calc python=3.9 -y
```

### Repository Access Issues
```bash
# If git clone fails
git config --global http.proxy http://proxy:port  # if behind proxy
ssh-keygen -t rsa -b 4096 -C "your_email@domain.com"  # for SSH access
```

## Next Steps

1. **Customize configuration**: Edit `workflow_config.yaml` for your cluster
2. **Set up pseudopotentials**: Run `python check_pseudopotentials.py --auto-fix`
3. **Start with small test**: `python unified_workflow.py --run-single-ml Au2`
4. **Scale up**: Submit full workflow with `sbatch submit_unified_workflow.sh`

Happy calculating! 🧬⚡
