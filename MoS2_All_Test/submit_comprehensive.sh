#!/bin/bash
#SBATCH --job-name=comprehensive_ml_dft_test
#SBATCH --partition=cenvalarc.gpu
#SBATCH --account=cenvalos
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --time=6-00:00:00
#SBATCH --output=comprehensive_%j.out
#SBATCH --error=comprehensive_%j.err

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
module load anaconda3/2023.09
module load cuda/12.1
module load fftw
module load quantum-espresso/7.1
module load mpich/3.4.2-intel-2021.4.0

# Activate conda environment
source activate base

# Set environment variables
export CUDA_VISIBLE_DEVICES=$SLURM_LOCALID
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Print Python and PyTorch info
echo "Python version: $(python --version)"
echo "PyTorch version: $(python -c 'import torch; print(torch.__version__)')"
echo "CUDA available: $(python -c 'import torch; print(torch.cuda.is_available())')"
echo "GPU count: $(python -c 'import torch; print(torch.cuda.device_count())')"
echo "QE version: $(pw.x --version | head -1)"
echo "================================="

# Run the comprehensive workflow
echo "Starting comprehensive ML+DFT energy profile calculations..."
echo "All 42 adsorbants on MoS2 with ML potential followed by DFT validation"
echo "================================="

python comprehensive_runner.py --config job_config.yaml

echo "================================="
echo "Job completed at: $(date)"
