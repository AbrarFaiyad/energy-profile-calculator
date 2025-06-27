#!/usr/bin/env bash

#SBATCH --job-name=mos2_job_manager
#SBATCH --partition=pi.amartini
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=logs/job_manager.o%j
#SBATCH --error=logs/job_manager.e%j

# Create logs directory if it doesn't exist
mkdir -p logs

# Setup environment
module purge
module load fftw
module load quantum-espresso/7.1
module load mpich/3.4.2-intel-2021.4.0
module load cuda/12.3.0
source /home/afaiyad/deepmd-kit-new/bin/activate

# Job info
echo "====================================="
echo "MoS2 Energy Profile Job Manager"
echo "====================================="
echo "Started: $(date)"
echo "Node: $(hostname)"
echo "Working directory: $(pwd)"
echo "User: $USER"
echo "====================================="

# Run the job manager
python job_manager.py

echo "====================================="
echo "Job Manager finished: $(date)"
echo "====================================="
