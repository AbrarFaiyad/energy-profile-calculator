#!/bin/bash
#SBATCH --job-name=ml_adsorbant_test
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --gres=gpu:1
#SBATCH --mem=128G
#SBATCH --time=24:00:00
#SBATCH --output=ml_test_%j.out
#SBATCH --error=ml_test_%j.err

# Print job information
echo "Job started at: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Partition: $SLURM_JOB_PARTITION"
echo "GPU: $CUDA_VISIBLE_DEVICES"
echo "Working directory: $(pwd)"
echo "================================="

# Load required modules
module purge
source /home/afaiyad/deepmd-kit-new/bin/activate
module load fftw
module load quantum-espresso/7.1
module load mpich/3.4.2-intel-2021.4.0
module load cuda/12.3.0

# Set environment variables
export CUDA_VISIBLE_DEVICES=$SLURM_LOCALID
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Print Python and PyTorch info
echo "Python version: $(python --version)"
echo "PyTorch version: $(python -c 'import torch; print(torch.__version__)')"
echo "CUDA available: $(python -c 'import torch; print(torch.cuda.is_available())')"
echo "GPU count: $(python -c 'import torch; print(torch.cuda.device_count())')"
echo "================================="

# Run the ML test
echo "Starting ML adsorbant energy profile calculations..."
echo "Testing all 42 adsorbants on MoS2 with ML potential"
echo "================================="

python test_all_ml.py

echo "================================="
echo "Job completed at: $(date)"
