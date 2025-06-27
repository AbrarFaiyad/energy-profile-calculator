#!/bin/bash
#SBATCH --job-name=unified_workflow
#SBATCH --partition=pi.amartini
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=15-00:00:00
#SBATCH --output=unified_workflow_%j.out
#SBATCH --error=unified_workflow_%j.err

# Print job information
echo "🚀 Unified MoS2 Energy Profile Workflow Started"
echo "================================================="
echo "Job started at: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Partition: $SLURM_JOB_PARTITION"
echo "Working directory: $(pwd)"
echo "This job manages and monitors all ML and DFT calculations"
echo "================================================="

# Load required modules
module purge
module load anaconda3
module load cuda
module load fftw
module load quantum-espresso
module load mpich

# Activate conda environment
conda activate fair

# Set environment variables
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Print environment info
echo "Python version: $(python --version)"
echo "PyTorch version: $(python -c 'import torch; print(torch.__version__)')"
echo "CUDA available: $(python -c 'import torch; print(torch.cuda.is_available())')"
echo "QE version: $(pw.x --version | head -1)"
echo "================================================="

# Run the unified workflow
echo "Starting unified workflow with intelligent job management..."
echo "This will:"
echo "  1. Validate pseudopotentials"
echo "  2. Submit ML calculations for all adsorbants"
echo "  3. Monitor ML jobs in real-time"
echo "  4. Select subset for DFT validation"
echo "  5. Submit and monitor DFT jobs"
echo "  6. Generate comprehensive analysis reports"
echo "================================================="

python unified_workflow.py --config workflow_config.yaml

echo "================================================="
echo "Unified workflow completed at: $(date)"
echo "Check results in: unified_results/"
echo "Check individual job logs in: logs/"
echo "================================================="
