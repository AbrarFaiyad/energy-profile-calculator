#!/usr/bin/env python3
"""
MoS2 Energy Profile Job Manager

This script runs on the pi.amartini node with 4 cores and 16GB memory to oversee
all job submissions, monitor progress, and manage the workflow.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
import argparse
from dataclasses import dataclass
from typing import Dict, List, Optional
import yaml

@dataclass
class JobConfig:
    """Configuration for a single job"""
    job_name: str
    material: str
    adsorbant: str
    calculation_type: str  # 'ml_gpu', 'dft_cpu'
    partition: str
    cores: int
    time_limit: str
    z_range: tuple
    priority: int = 1
    dependencies: List[str] = None

@dataclass
class PartitionLimits:
    """Limits for each partition"""
    name: str
    max_jobs: int
    cores_per_node: int
    current_jobs: int = 0

class MoS2JobManager:
    def __init__(self, config_file: str = "job_config.yaml"):
        self.config_file = Path(config_file)
        self.work_dir = Path.cwd()
        self.jobs_dir = self.work_dir / "jobs"
        self.results_dir = self.work_dir / "results"
        self.logs_dir = self.work_dir / "logs"
        
        # Create directories
        for dir_path in [self.jobs_dir, self.results_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Partition limits based on your cluster
        self.partitions = {
            'cenvalarc.gpu': PartitionLimits('cenvalarc.gpu', 4, 32),
            'gpu': PartitionLimits('gpu', 4, 28),
            'long': PartitionLimits('long', 3, 56),
            'cenvalarc.compute': PartitionLimits('cenvalarc.compute', 3, 64),
            'pi.amartini': PartitionLimits('pi.amartini', 3, 56)
        }
        
        self.job_queue = []
        self.running_jobs = {}
        self.completed_jobs = {}
        self.failed_jobs = {}
        
        # Load configuration
        self.load_config()
        
    def load_config(self):
        """Load job configuration from YAML file"""
        if not self.config_file.exists():
            self.create_default_config()
        
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.ml_calculator = config.get('ml_calculator', 'uma-s-1')
        self.pseudo_dir = config.get('pseudo_dir', '/home/afaiyad/QE/qe-7.4.1/pseudo')
        self.materials = config.get('materials', ['MoS2'])
        self.adsorbants = config.get('adsorbants', ['H2O', 'Au2', 'Li'])
        
    def create_default_config(self):
        """Create a default configuration file"""
        default_config = {
            'ml_calculator': 'uma-s-1',
            'pseudo_dir': '/home/afaiyad/QE/qe-7.4.1/pseudo',
            'materials': ['MoS2'],
            'adsorbants': ['H2O', 'Au2', 'Li', 'ZnO', 'F4TCNQ'],
            'z_ranges': {
                'H2O': [2.0, 8.0, 0.2],
                'Au2': [2.5, 8.0, 0.3],
                'Li': [2.0, 6.0, 0.2],
                'ZnO': [2.5, 8.0, 0.3],
                'F4TCNQ': [3.0, 8.0, 0.3]
            },
            'dft_settings': {
                'ecutwfc': 80,
                'ecutrho': 640,
                'kpts': [6, 6, 1],
                'conv_thr': 1e-8
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"📝 Created default configuration: {self.config_file}")
    
    def check_pseudopotentials(self):
        """Check if all required pseudopotentials are available"""
        print("🔍 Checking pseudopotentials...")
        
        check_script = self.work_dir / "check_pseudopotentials.py"
        if not check_script.exists():
            print(f"❌ Pseudopotential checker not found: {check_script}")
            return False
        
        result = subprocess.run([sys.executable, str(check_script)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All pseudopotentials available")
            return True
        else:
            print("❌ Missing pseudopotentials:")
            print(result.stdout)
            return False
    
    def generate_job_queue(self):
        """Generate the queue of jobs to run"""
        print("📋 Generating job queue...")
        
        job_id = 0
        for material in self.materials:
            for adsorbant in self.adsorbants:
                # ML job (GPU)
                ml_job = JobConfig(
                    job_name=f"ml_{material}_{adsorbant}_{job_id:03d}",
                    material=material,
                    adsorbant=adsorbant,
                    calculation_type='ml_gpu',
                    partition='cenvalarc.gpu',
                    cores=32,
                    time_limit='2-23:59:00',
                    z_range=(2.0, 8.0, 0.2),
                    priority=1
                )
                self.job_queue.append(ml_job)
                job_id += 1
                
                # DFT job (CPU) - depends on ML job
                dft_job = JobConfig(
                    job_name=f"dft_{material}_{adsorbant}_{job_id:03d}",
                    material=material,
                    adsorbant=adsorbant,
                    calculation_type='dft_cpu',
                    partition='long',
                    cores=56,
                    time_limit='5-00:00:00',
                    z_range=(2.0, 8.0, 1.0),  # Fewer points for DFT
                    priority=2,
                    dependencies=[ml_job.job_name]
                )
                self.job_queue.append(dft_job)
                job_id += 1
        
        print(f"📊 Generated {len(self.job_queue)} jobs")
        
        # Sort by priority
        self.job_queue.sort(key=lambda x: x.priority)
    
    def create_job_script(self, job: JobConfig) -> Path:
        """Create a SLURM job script for the given job"""
        script_path = self.jobs_dir / f"{job.job_name}.sh"
        
        if job.calculation_type == 'ml_gpu':
            script_content = self.create_ml_gpu_script(job)
        else:
            script_content = self.create_dft_cpu_script(job)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        return script_path
    
    def create_ml_gpu_script(self, job: JobConfig) -> str:
        """Create SLURM script for ML GPU calculations"""
        dependencies = ""
        if job.dependencies:
            dep_ids = [self.running_jobs.get(dep, "") for dep in job.dependencies]
            dep_ids = [d for d in dep_ids if d]  # Remove empty strings
            if dep_ids:
                dependencies = f"#SBATCH --dependency=afterok:{':'.join(dep_ids)}"
        
        constraint = ""
        if job.partition == 'cenvalarc.gpu':
            constraint = "#SBATCH --constraint=gpu"
        
        return f'''#!/usr/bin/env bash

#SBATCH --job-name={job.job_name}
#SBATCH --partition={job.partition}
{constraint}
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node={job.cores}
#SBATCH --time={job.time_limit}
#SBATCH --output={self.logs_dir}/{job.job_name}.o%j
#SBATCH --error={self.logs_dir}/{job.job_name}.e%j
{dependencies}

# Setup environment
module purge
module load anaconda3/2023.09
module load cuda/12.1
source activate base

# Job info
echo "Job started: $(date)"
echo "Job name: {job.job_name}"
echo "Material: {job.material}"
echo "Adsorbant: {job.adsorbant}"
echo "Calculation type: {job.calculation_type}"
echo "Partition: {job.partition}"
echo "Cores: {job.cores}"

# Set environment variables
export CUDA_VISIBLE_DEVICES=$SLURM_LOCALID
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Create results directory
mkdir -p {self.results_dir}/{job.job_name}
cd {self.results_dir}/{job.job_name}

# Run comprehensive ML calculation using our improved runner
python3 {self.work_dir}/comprehensive_runner.py \\
    --config {self.work_dir}/job_config.yaml \\
    --adsorbant {job.adsorbant} \\
    --ml-only

echo "Job completed: $(date)"
'''
    
    def create_dft_cpu_script(self, job: JobConfig) -> str:
        """Create SLURM script for DFT CPU calculations"""
        dependencies = ""
        if job.dependencies:
            dep_ids = [self.running_jobs.get(dep, "") for dep in job.dependencies]
            dep_ids = [d for d in dep_ids if d]  # Remove empty strings
            if dep_ids:
                dependencies = f"#SBATCH --dependency=afterok:{':'.join(dep_ids)}"
        
        return f'''#!/usr/bin/env bash

#SBATCH --job-name={job.job_name}
#SBATCH --partition={job.partition}
#SBATCH --account=cenvalos
#SBATCH --nodes=1
#SBATCH --ntasks-per-node={job.cores}
#SBATCH --time={job.time_limit}
#SBATCH --output={self.logs_dir}/{job.job_name}.o%j
#SBATCH --error={self.logs_dir}/{job.job_name}.e%j
{dependencies}

# Setup environment
module purge
module load anaconda3/2023.09
module load fftw
module load quantum-espresso/7.1
module load mpich/3.4.2-intel-2021.4.0
source activate base

# Job info
echo "Job started: $(date)"
echo "Job name: {job.job_name}"
echo "Material: {job.material}"
echo "Adsorbant: {job.adsorbant}"
echo "Calculation type: {job.calculation_type}"
echo "Partition: {job.partition}"
echo "Cores: {job.cores}"

# Set environment variables
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Create results directory
mkdir -p {self.results_dir}/{job.job_name}
cd {self.results_dir}/{job.job_name}

# Run comprehensive DFT calculation using our improved runner
python3 {self.work_dir}/comprehensive_runner.py \\
    --config {self.work_dir}/job_config.yaml \\
    --adsorbant {job.adsorbant} \\
    --dft-only

echo "Job completed: $(date)"
'''
    
    def get_queue_status(self) -> Dict[str, int]:
        """Get current SLURM queue status"""
        try:
            result = subprocess.run(['squeue', '-u', os.getenv('USER'), '-h', '-o', '%P %T'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                return {}
            
            status = {}
            for line in result.stdout.strip().split('\n'):
                if line:
                    partition, state = line.split()
                    if partition not in status:
                        status[partition] = 0
                    if state in ['RUNNING', 'PENDING']:
                        status[partition] += 1
            
            return status
        except Exception as e:
            print(f"Error getting queue status: {e}")
            return {}
    
    def can_submit_job(self, job: JobConfig) -> bool:
        """Check if we can submit a job to the given partition"""
        queue_status = self.get_queue_status()
        current_jobs = queue_status.get(job.partition, 0)
        max_jobs = self.partitions[job.partition].max_jobs
        
        return current_jobs < max_jobs
    
    def submit_job(self, job: JobConfig) -> Optional[str]:
        """Submit a job and return the job ID"""
        if not self.can_submit_job(job):
            return None
        
        script_path = self.create_job_script(job)
        
        try:
            result = subprocess.run(['sbatch', str(script_path)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Extract job ID from output like "Submitted batch job 1234567"
                job_id = result.stdout.strip().split()[-1]
                self.running_jobs[job.job_name] = job_id
                
                print(f"✅ Submitted {job.job_name} (ID: {job_id}) to {job.partition}")
                return job_id
            else:
                print(f"❌ Failed to submit {job.job_name}: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error submitting {job.job_name}: {e}")
            return None
    
    def check_job_status(self, job_id: str) -> str:
        """Check the status of a job"""
        try:
            result = subprocess.run(['squeue', '-j', job_id, '-h', '-o', '%T'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                # Job not in queue, check if it completed
                return 'COMPLETED'
                
        except Exception:
            return 'UNKNOWN'
    
    def update_job_status(self):
        """Update the status of all running jobs"""
        completed_jobs = []
        
        for job_name, job_id in self.running_jobs.items():
            status = self.check_job_status(job_id)
            
            if status in ['COMPLETED', 'FAILED', 'CANCELLED', 'TIMEOUT']:
                completed_jobs.append(job_name)
                
                if status == 'COMPLETED':
                    self.completed_jobs[job_name] = job_id
                    print(f"🎉 Job {job_name} completed successfully")
                else:
                    self.failed_jobs[job_name] = job_id
                    print(f"💥 Job {job_name} failed with status: {status}")
        
        # Remove completed jobs from running list
        for job_name in completed_jobs:
            del self.running_jobs[job_name]
    
    def dependencies_satisfied(self, job: JobConfig) -> bool:
        """Check if all dependencies for a job are satisfied"""
        if not job.dependencies:
            return True
        
        for dep in job.dependencies:
            if dep not in self.completed_jobs:
                return False
        
        return True
    
    def run_job_manager(self, max_iterations: int = None):
        """Main job management loop"""
        print(f"🚀 Starting MoS2 Job Manager")
        print(f"Work directory: {self.work_dir}")
        print("=" * 60)
        
        # Check pseudopotentials first
        if not self.check_pseudopotentials():
            print("❌ Cannot proceed without required pseudopotentials")
            return
        
        # Generate job queue
        self.generate_job_queue()
        
        iteration = 0
        while self.job_queue or self.running_jobs:
            iteration += 1
            if max_iterations and iteration > max_iterations:
                break
            
            print(f"\n📊 Iteration {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Queue: {len(self.job_queue)}, Running: {len(self.running_jobs)}, Completed: {len(self.completed_jobs)}, Failed: {len(self.failed_jobs)}")
            
            # Update status of running jobs
            self.update_job_status()
            
            # Try to submit new jobs
            jobs_to_submit = []
            for job in self.job_queue[:]:
                if self.dependencies_satisfied(job) and self.can_submit_job(job):
                    jobs_to_submit.append(job)
            
            for job in jobs_to_submit:
                job_id = self.submit_job(job)
                if job_id:
                    self.job_queue.remove(job)
            
            # Show current status
            queue_status = self.get_queue_status()
            print("Partition status:")
            for partition, limits in self.partitions.items():
                current = queue_status.get(partition, 0)
                print(f"  {partition}: {current}/{limits.max_jobs}")
            
            # Sleep before next iteration
            if self.job_queue or self.running_jobs:
                time.sleep(60)  # Check every minute
        
        print(f"\n🎉 All jobs completed!")
        print(f"Successful: {len(self.completed_jobs)}")
        print(f"Failed: {len(self.failed_jobs)}")


def main():
    parser = argparse.ArgumentParser(description='MoS2 Energy Profile Job Manager')
    parser.add_argument('--config', default='job_config.yaml', 
                       help='Configuration file (default: job_config.yaml)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Generate job scripts but do not submit')
    parser.add_argument('--max-iterations', type=int,
                       help='Maximum number of iterations (for testing)')
    
    args = parser.parse_args()
    
    manager = MoS2JobManager(args.config)
    
    if args.dry_run:
        print("🧪 Dry run mode - generating job queue...")
        manager.check_pseudopotentials()
        manager.generate_job_queue()
        print(f"Generated {len(manager.job_queue)} jobs")
        for i, job in enumerate(manager.job_queue[:5]):  # Show first 5
            print(f"  {i+1}. {job.job_name} ({job.calculation_type}) on {job.partition}")
        if len(manager.job_queue) > 5:
            print(f"  ... and {len(manager.job_queue) - 5} more")
    else:
        manager.run_job_manager(args.max_iterations)


if __name__ == "__main__":
    main()
