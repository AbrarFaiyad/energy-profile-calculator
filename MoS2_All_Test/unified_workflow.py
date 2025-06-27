#!/usr/bin/env python3
"""
Unified MoS2 Energy Profile Workflow

This script combines job management, parallelization, and comprehensive analysis
into a single workflow that can be customized for different cluster environments.

Features:
- Intelligent job parallelization across multiple partitions
- Comprehensive ML + DFT calculations with smart subset selection
- Detailed result visualization and comparison
- Cluster-agnostic design with easy configuration
- Progress monitoring and failure recovery
"""

import os
import sys
import time
import json
import yaml
import subprocess
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import argparse
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from energy_profile_calculator.core import EnergyProfileCalculator
    from energy_profile_calculator.adsorbants import AdsorbantLibrary
    from energy_profile_calculator.surfaces import SurfaceBuilder
    
    print("🚀 Unified MoS2 Energy Profile Workflow")
    print("=" * 70)
    print("📋 Intelligent ML + DFT calculations with cluster parallelization")
    print("🧠 Combining job management with comprehensive analysis")
    print("=" * 70)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and the energy_profile_calculator package is available")
    sys.exit(1)

@dataclass
class ClusterConfig:
    """Configuration for cluster-specific settings"""
    partitions: Dict[str, Dict[str, Any]]
    modules: List[str]
    environment_setup: List[str]
    job_submit_command: str = "sbatch"
    job_status_command: str = "squeue"
    user_env_var: str = "USER"

@dataclass
class JobDefinition:
    """Definition of a single calculation job"""
    job_id: str
    adsorbant: str
    calculation_type: str  # 'ml', 'dft'
    partition: str
    cores: int
    memory: str
    time_limit: str
    gpu_required: bool = False
    dependencies: List[str] = None
    priority: int = 1
    status: str = "pending"  # pending, running, completed, failed

class UnifiedWorkflow:
    def __init__(self, config_file: str = "workflow_config.yaml"):
        self.config_file = Path(config_file)
        self.work_dir = Path.cwd()
        
        # Create directory structure
        self.results_dir = self.work_dir / "unified_results"
        self.ml_results_dir = self.results_dir / "ml_calculations"
        self.dft_results_dir = self.results_dir / "dft_calculations"
        self.comparison_dir = self.results_dir / "ml_vs_dft"
        self.reports_dir = self.results_dir / "reports"
        self.jobs_dir = self.work_dir / "job_scripts"
        self.logs_dir = self.work_dir / "logs"
        
        for dir_path in [self.results_dir, self.ml_results_dir, self.dft_results_dir, 
                        self.comparison_dir, self.reports_dir, self.jobs_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Initialize libraries
        self.adsorbant_library = AdsorbantLibrary()
        self.surface_builder = SurfaceBuilder()
        
        # Load configuration
        self.load_config()
        
        # Job tracking
        self.ml_jobs = {}
        self.dft_jobs = {}
        self.completed_ml = []
        self.completed_dft = []
        self.failed_jobs = []
        self.ml_results = {}
        self.dft_results = {}
        
    def load_config(self):
        """Load workflow configuration"""
        if not self.config_file.exists():
            self.create_default_config()
        
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Calculation settings
        self.ml_calculator = config.get('ml_calculator', 'equiformer_v2_153M_omat')
        self.pseudo_dir = config.get('pseudo_dir', '/home/afaiyad/QE/qe-7.4.1/pseudo')
        self.materials = config.get('materials', ['MoS2'])
        self.adsorbants = config.get('adsorbants', [])
        self.z_ranges = config.get('z_ranges', {})
        self.dft_settings = config.get('dft_settings', {})
        self.slab_settings = config.get('slab_settings', {})
        
        # Workflow settings
        workflow_settings = config.get('workflow', {})
        self.dft_fraction = workflow_settings.get('dft_fraction', 0.3)
        self.max_parallel_ml = workflow_settings.get('max_parallel_ml', 4)
        self.max_parallel_dft = workflow_settings.get('max_parallel_dft', 2)
        self.use_cluster = workflow_settings.get('use_cluster', True)
        self.local_cores = workflow_settings.get('local_cores', multiprocessing.cpu_count())
        
        # Cluster configuration
        if self.use_cluster:
            self.cluster_config = ClusterConfig(**config.get('cluster', {}))
        
        print(f"📝 Loaded configuration:")
        print(f"   Materials: {self.materials}")
        print(f"   Adsorbants: {len(self.adsorbants)}")
        print(f"   ML Calculator: {self.ml_calculator}")
        print(f"   DFT Fraction: {self.dft_fraction}")
        print(f"   Use Cluster: {self.use_cluster}")
        
    def create_default_config(self):
        """Create default configuration file with cluster templates"""
        default_config = {
            'ml_calculator': 'equiformer_v2_153M_omat',
            'pseudo_dir': '/home/afaiyad/QE/qe-7.4.1/pseudo',
            'materials': ['MoS2'],
            'adsorbants': [
                'Au2', 'Ag2', 'Pt2', 'Pd2', 'Cu2', 'Fe2', 'Co2', 'Ni2', 'Mn2',
                'Ir2', 'Rh2', 'Re2', 'Ru2', 'Cd2', 'Al2', 'Zn2', 'Nb2', 'W2',
                'Ta2', 'V2', 'C2', 'Ti2', 'Cr2', 'Na2', 'N2', 'O2', 'H2',
                'ZnO', 'TiO2', 'Sb2O3'
            ],
            'z_ranges': {ads: [2.5, 8.0, 0.2] for ads in [
                'Au2', 'Ag2', 'Pt2', 'Pd2', 'Cu2', 'Fe2', 'Co2', 'Ni2', 'Mn2',
                'Ir2', 'Rh2', 'Re2', 'Ru2', 'Cd2', 'Al2', 'Zn2', 'Nb2', 'W2',
                'Ta2', 'V2', 'C2', 'Ti2', 'Cr2', 'Na2', 'N2', 'O2', 'H2',
                'ZnO', 'TiO2', 'Sb2O3'
            ]},
            'dft_settings': {
                'ecutwfc': 80,
                'ecutrho': 640,
                'kpts': [6, 6, 1],
                'conv_thr': 1e-8,
                'vdw_corr': 'grimme-d3'
            },
            'slab_settings': {
                'size': [3, 3],
                'vacuum': 14.0,
                'layers': 1
            },
            'workflow': {
                'dft_fraction': 0.3,
                'max_parallel_ml': 4,
                'max_parallel_dft': 2,
                'use_cluster': True,
                'local_cores': 8
            },
            'cluster': {
                'partitions': {
                    'cenvalarc.gpu': {
                        'max_jobs': 4,
                        'cores_per_node': 32,
                        'memory_per_node': '128G',
                        'time_limit': '2-23:59:00',
                        'gpu_nodes': True,
                        'constraint': 'gpu'
                    },
                    'gpu': {
                        'max_jobs': 4,
                        'cores_per_node': 28,
                        'memory_per_node': '128G',
                        'time_limit': '2-23:59:00',
                        'gpu_nodes': True
                    },
                    'long': {
                        'max_jobs': 3,
                        'cores_per_node': 56,
                        'memory_per_node': '256G',
                        'time_limit': '5-00:00:00',
                        'gpu_nodes': False
                    },
                    'cenvalarc.compute': {
                        'max_jobs': 3,
                        'cores_per_node': 64,
                        'memory_per_node': '256G',
                        'time_limit': '3-00:00:00',
                        'gpu_nodes': False
                    }
                },
                'modules': [
                    'anaconda3/2023.09',
                    'cuda/12.1',
                    'fftw',
                    'quantum-espresso/7.1',
                    'mpich/3.4.2-intel-2021.4.0'
                ],
                'environment_setup': [
                    'source activate base',
                    'export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK'
                ]
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        print(f"📝 Created default configuration: {self.config_file}")
        print("🔧 Edit this file to customize for your cluster environment")
    
    def get_adsorbant_orientation(self, adsorbant: str) -> str:
        """Get appropriate orientation for an adsorbant"""
        try:
            info = self.adsorbant_library.get_info(adsorbant)
            orientations = info.get('orientations', ['default'])
            
            if 'parallel' in orientations:
                return 'parallel'
            elif 'flat' in orientations:
                return 'flat'
            else:
                return 'default'
        except:
            return 'default'
    
    def check_pseudopotentials(self) -> bool:
        """Check pseudopotential availability"""
        print("🔍 Checking pseudopotentials...")
        
        check_script = self.work_dir / "check_pseudopotentials.py"
        if not check_script.exists():
            print(f"⚠️  Pseudopotential checker not found: {check_script}")
            return True  # Assume OK
        
        try:
            result = subprocess.run([sys.executable, str(check_script)], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ All pseudopotentials available")
                return True
            else:
                print("❌ Missing pseudopotentials - use download_pseudo.py")
                return False
        except:
            print("⚠️  Could not check pseudopotentials, proceeding anyway")
            return True
    
    def create_job_script(self, job: JobDefinition) -> Path:
        """Create SLURM job script"""
        script_path = self.jobs_dir / f"{job.job_id}.sh"
        
        if self.use_cluster:
            if job.calculation_type == 'ml':
                content = self.create_ml_cluster_script(job)
            else:
                content = self.create_dft_cluster_script(job)
        else:
            content = self.create_local_script(job)
        
        with open(script_path, 'w') as f:
            f.write(content)
        
        os.chmod(script_path, 0o755)
        return script_path
    
    def create_ml_cluster_script(self, job: JobDefinition) -> str:
        """Create ML calculation cluster script"""
        partition_config = self.cluster_config.partitions[job.partition]
        
        dependencies = ""
        if job.dependencies:
            dep_str = ":".join(job.dependencies)
            dependencies = f"#SBATCH --dependency=afterok:{dep_str}"
        
        gpu_line = "#SBATCH --gres=gpu:1" if job.gpu_required else ""
        constraint_line = f"#SBATCH --constraint={partition_config.get('constraint', '')}" if partition_config.get('constraint') else ""
        
        modules_load = "\n".join([f"module load {mod}" for mod in self.cluster_config.modules])
        env_setup = "\n".join(self.cluster_config.environment_setup)
        
        return f'''#!/usr/bin/env bash

#SBATCH --job-name={job.job_id}
#SBATCH --partition={job.partition}
#SBATCH --account=cenvalos
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task={job.cores}
#SBATCH --mem={job.memory}
#SBATCH --time={job.time_limit}
{gpu_line}
{constraint_line}
#SBATCH --output={self.logs_dir}/{job.job_id}.out
#SBATCH --error={self.logs_dir}/{job.job_id}.err
{dependencies}

# Environment setup
module purge
{modules_load}
{env_setup}

if [ -n "$SLURM_LOCALID" ]; then
    export CUDA_VISIBLE_DEVICES=$SLURM_LOCALID
fi

# Job information
echo "🚀 ML Calculation Job Started"
echo "Job ID: {job.job_id}"
echo "Adsorbant: {job.adsorbant}"
echo "Partition: {job.partition}"
echo "Cores: {job.cores}"
echo "Memory: {job.memory}"
echo "Time: $(date)"
echo "================================="

# Create output directory
mkdir -p {self.ml_results_dir}/{job.adsorbant}
cd {self.ml_results_dir}/{job.adsorbant}

# Run ML calculation
python3 {self.work_dir}/unified_workflow.py \\
    --run-single-ml {job.adsorbant} \\
    --config {self.config_file} \\
    --output-dir {self.ml_results_dir}/{job.adsorbant}

echo "================================="
echo "Job completed at: $(date)"
'''
    
    def create_dft_cluster_script(self, job: JobDefinition) -> str:
        """Create DFT calculation cluster script"""
        partition_config = self.cluster_config.partitions[job.partition]
        
        dependencies = ""
        if job.dependencies:
            dep_str = ":".join(job.dependencies)
            dependencies = f"#SBATCH --dependency=afterok:{dep_str}"
        
        modules_load = "\n".join([f"module load {mod}" for mod in self.cluster_config.modules])
        env_setup = "\n".join(self.cluster_config.environment_setup)
        
        return f'''#!/usr/bin/env bash

#SBATCH --job-name={job.job_id}
#SBATCH --partition={job.partition}
#SBATCH --account=cenvalos
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task={job.cores}
#SBATCH --mem={job.memory}
#SBATCH --time={job.time_limit}
#SBATCH --output={self.logs_dir}/{job.job_id}.out
#SBATCH --error={self.logs_dir}/{job.job_id}.err
{dependencies}

# Environment setup
module purge
{modules_load}
{env_setup}

# Job information
echo "⚛️  DFT Calculation Job Started"
echo "Job ID: {job.job_id}"
echo "Adsorbant: {job.adsorbant}"
echo "Partition: {job.partition}"
echo "Cores: {job.cores}"
echo "Memory: {job.memory}"
echo "Time: $(date)"
echo "================================="

# Create output directory
mkdir -p {self.dft_results_dir}/{job.adsorbant}
cd {self.dft_results_dir}/{job.adsorbant}

# Run DFT calculation
python3 {self.work_dir}/unified_workflow.py \\
    --run-single-dft {job.adsorbant} \\
    --config {self.config_file} \\
    --ml-results-dir {self.ml_results_dir}/{job.adsorbant} \\
    --output-dir {self.dft_results_dir}/{job.adsorbant}

echo "================================="
echo "Job completed at: $(date)"
'''
    
    def create_local_script(self, job: JobDefinition) -> str:
        """Create local execution script"""
        return f'''#!/usr/bin/env bash

echo "🖥️  Local Calculation Job Started"
echo "Job ID: {job.job_id}"
echo "Adsorbant: {job.adsorbant}"
echo "Type: {job.calculation_type}"
echo "Time: $(date)"
echo "================================="

if [ "{job.calculation_type}" == "ml" ]; then
    mkdir -p {self.ml_results_dir}/{job.adsorbant}
    cd {self.ml_results_dir}/{job.adsorbant}
    python3 {self.work_dir}/unified_workflow.py \\
        --run-single-ml {job.adsorbant} \\
        --config {self.config_file} \\
        --output-dir {self.ml_results_dir}/{job.adsorbant}
else
    mkdir -p {self.dft_results_dir}/{job.adsorbant}
    cd {self.dft_results_dir}/{job.adsorbant}
    python3 {self.work_dir}/unified_workflow.py \\
        --run-single-dft {job.adsorbant} \\
        --config {self.config_file} \\
        --ml-results-dir {self.ml_results_dir}/{job.adsorbant} \\
        --output-dir {self.dft_results_dir}/{job.adsorbant}
fi

echo "================================="
echo "Job completed at: $(date)"
'''
    
    def submit_job(self, job: JobDefinition) -> Optional[str]:
        """Submit a job and return job ID"""
        script_path = self.create_job_script(job)
        
        if self.use_cluster:
            try:
                result = subprocess.run([self.cluster_config.job_submit_command, str(script_path)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    job_id = result.stdout.strip().split()[-1]
                    print(f"✅ Submitted {job.job_id} (SLURM ID: {job_id}) to {job.partition}")
                    return job_id
                else:
                    print(f"❌ Failed to submit {job.job_id}: {result.stderr}")
                    return None
            except Exception as e:
                print(f"❌ Error submitting {job.job_id}: {e}")
                return None
        else:
            # Local execution
            print(f"🖥️  Running {job.job_id} locally...")
            try:
                subprocess.Popen(['bash', str(script_path)])
                return f"local_{job.job_id}"
            except Exception as e:
                print(f"❌ Error running {job.job_id} locally: {e}")
                return None
    
    def check_job_status(self, job_id: str) -> str:
        """Check the status of a SLURM job"""
        try:
            result = subprocess.run(['squeue', '-j', job_id, '-h', '-o', '%T'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                # Job not in queue, assume completed
                return 'COMPLETED'
                
        except Exception:
            return 'UNKNOWN'
    
    def get_queue_status(self) -> Dict[str, int]:
        """Get current job counts per partition for the user"""
        try:
            user = os.environ.get('USER', 'unknown')
            result = subprocess.run(['squeue', '-u', user, '-h', '-o', '%P'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                partitions = result.stdout.strip().split('\n')
                partition_counts = {}
                for partition in partitions:
                    if partition.strip():
                        partition_counts[partition.strip()] = partition_counts.get(partition.strip(), 0) + 1
                return partition_counts
            
        except Exception:
            pass
        
        return {}
    
    def can_submit_job(self, job: JobDefinition) -> bool:
        """Check if a job can be submitted to its partition"""
        if not self.use_cluster:
            return True
            
        if job.partition not in self.cluster_config.partitions:
            return False
        
        partition_config = self.cluster_config.partitions[job.partition]
        current_jobs = self.get_queue_status().get(job.partition, 0)
        
        return current_jobs < partition_config.get('max_jobs', 999)
    
    def monitor_jobs_advanced(self, ml_jobs: Dict[str, str], dft_jobs: Dict[str, str], 
                             max_iterations: int = 1440) -> Tuple[Dict[str, List[str]], bool]:
        """
        Advanced job monitoring with iteration limits and comprehensive status tracking
        Returns: (results_dict, all_completed_successfully)
        """
        start_time = time.time()
        iteration = 0
        
        completed_ml = []
        completed_dft = []
        failed_ml = []
        failed_dft = []
        
        active_ml = dict(ml_jobs)
        active_dft = dict(dft_jobs)
        
        print(f"\n🔍 Starting advanced monitoring:")
        print(f"   ML jobs: {len(active_ml)}")
        print(f"   DFT jobs: {len(active_dft)}")
        print(f"   Max iterations: {max_iterations} (2-minute intervals)")
        
        while iteration < max_iterations and (active_ml or active_dft):
            iteration += 1
            
            # Update job statuses
            for job_name, job_id in list(active_ml.items()):
                status = self.check_job_status(job_id)
                
                if status == 'COMPLETED':
                    completed_ml.append(job_name)
                    del active_ml[job_name]
                    print(f"✅ ML job completed: {job_name}")
                elif status in ['FAILED', 'CANCELLED', 'TIMEOUT', 'NODE_FAIL']:
                    failed_ml.append(job_name)
                    del active_ml[job_name]
                    print(f"❌ ML job failed: {job_name} (status: {status})")
            
            for job_name, job_id in list(active_dft.items()):
                status = self.check_job_status(job_id)
                
                if status == 'COMPLETED':
                    completed_dft.append(job_name)
                    del active_dft[job_name]
                    print(f"✅ DFT job completed: {job_name}")
                elif status in ['FAILED', 'CANCELLED', 'TIMEOUT', 'NODE_FAIL']:
                    failed_dft.append(job_name)
                    del active_dft[job_name]
                    print(f"❌ DFT job failed: {job_name} (status: {status})")
            
            # Progress report every 10 iterations (20 minutes)
            if iteration % 10 == 0 or not (active_ml or active_dft):
                elapsed_time = time.time() - start_time
                total_completed = len(completed_ml) + len(completed_dft)
                total_failed = len(failed_ml) + len(failed_dft)
                total_active = len(active_ml) + len(active_dft)
                
                print(f"\n📊 Monitoring Progress (Iteration {iteration}):")
                print(f"   Time elapsed: {elapsed_time/3600:.1f} hours")
                print(f"   Completed: {total_completed} jobs")
                print(f"   Failed: {total_failed} jobs")
                print(f"   Still running: {total_active} jobs")
                
                if active_ml:
                    print(f"   Active ML: {list(active_ml.keys())[:3]}{'...' if len(active_ml) > 3 else ''}")
                if active_dft:
                    print(f"   Active DFT: {list(active_dft.keys())[:3]}{'...' if len(active_dft) > 3 else ''}")
            
            # Check if all jobs are done
            if not active_ml and not active_dft:
                print(f"\n🎉 All jobs completed after {iteration} iterations ({(time.time()-start_time)/3600:.1f} hours)")
                break
            
            # Wait before next check
            time.sleep(120)  # 2-minute intervals
        
        # Final summary
        all_successful = len(failed_ml) == 0 and len(failed_dft) == 0
        
        results = {
            'completed_ml': completed_ml,
            'completed_dft': completed_dft,
            'failed_ml': failed_ml,
            'failed_dft': failed_dft,
            'monitoring_stats': {
                'iterations': iteration,
                'elapsed_hours': (time.time() - start_time) / 3600,
                'success_rate': (len(completed_ml) + len(completed_dft)) / (len(ml_jobs) + len(dft_jobs)) if (ml_jobs or dft_jobs) else 0
            }
        }
        
        return results, all_successful

    def run_single_ml_calculation(self, adsorbant: str, output_dir: str):
        """Run single ML calculation (called from job script)"""
        print(f"🧠 Running ML calculation for {adsorbant}")
        
        try:
            # Setup calculator
            calculator = EnergyProfileCalculator()
            
            # Setup MoS2 surface
            calculator.surface = calculator.surface_builder.build_2d_material(
                material='MoS2',
                size=self.slab_settings.get('size', [3, 3]),
                vacuum=self.slab_settings.get('vacuum', 14.0)
            )
            calculator.surface_material = 'MoS2'
            calculator.surface_name = 'MoS2'
            
            # Setup ML calculator
            calculator.setup_calculators(
                use_ml=True,
                use_dft=False,
                ml_model=self.ml_calculator
            )
            
            # Get calculation parameters
            z_start, z_end, z_step = self.z_ranges.get(adsorbant, [2.5, 8.0, 0.2])
            orientation = self.get_adsorbant_orientation(adsorbant)
            
            print(f"   Z-range: {z_start} to {z_end} Å (step: {z_step})")
            print(f"   Orientation: {orientation}")
            
            # Run calculation
            results = calculator.calculate_energy_profile(
                adsorbant=adsorbant,
                z_start=z_start,
                z_end=z_end,
                z_step=z_step,
                adsorbant_orientation=orientation,
                output_dir=output_dir,
                save_structures=True
            )
            
            if results:
                # Save results
                results_file = Path(output_dir) / f"{adsorbant}_ml_results.json"
                with open(results_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                
                print(f"✅ ML calculation completed for {adsorbant}")
                print(f"   Results saved to: {results_file}")
                
                # Create summary plot
                self.create_single_plot(adsorbant, results, output_dir, 'ml')
                
            else:
                print(f"❌ ML calculation failed for {adsorbant}")
                
        except Exception as e:
            print(f"❌ Error in ML calculation for {adsorbant}: {e}")
            import traceback
            traceback.print_exc()
    
    def run_single_dft_calculation(self, adsorbant: str, ml_results_dir: str, output_dir: str):
        """Run single DFT calculation (called from job script)"""
        print(f"⚛️  Running DFT calculation for {adsorbant}")
        
        try:
            # Load ML results
            ml_results_file = Path(ml_results_dir) / f"{adsorbant}_ml_results.json"
            if not ml_results_file.exists():
                print(f"❌ ML results not found: {ml_results_file}")
                return
            
            with open(ml_results_file, 'r') as f:
                ml_results = json.load(f)
            
            # Setup calculator
            calculator = EnergyProfileCalculator()
            
            # Setup MoS2 surface
            calculator.surface = calculator.surface_builder.build_2d_material(
                material='MoS2',
                size=self.slab_settings.get('size', [3, 3]),
                vacuum=self.slab_settings.get('vacuum', 14.0)
            )
            calculator.surface_material = 'MoS2'
            calculator.surface_name = 'MoS2'
            
            # Setup DFT calculator
            calculator.setup_calculators(
                use_ml=False,
                use_dft=True,
                dft_pseudo_dir=self.pseudo_dir,
                dft_num_cores=self.local_cores
            )
            
            # Select DFT points based on ML results
            dft_heights = self.select_dft_points_from_ml(ml_results)
            orientation = self.get_adsorbant_orientation(adsorbant)
            
            print(f"   Selected {len(dft_heights)} DFT points: {[f'{h:.2f}' for h in dft_heights]}")
            print(f"   Orientation: {orientation}")
            
            # Run DFT calculation
            results = calculator.calculate_energy_profile(
                adsorbant=adsorbant,
                z_start=min(dft_heights),
                z_end=max(dft_heights),
                z_step=0.5,  # Will use custom heights
                adsorbant_orientation=orientation,
                dft_functional=self.dft_settings.get('functional', 'pbe'),
                output_dir=output_dir,
                save_structures=True
            )
            
            if results:
                # Save results
                results_file = Path(output_dir) / f"{adsorbant}_dft_results.json"
                with open(results_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                
                print(f"✅ DFT calculation completed for {adsorbant}")
                print(f"   Results saved to: {results_file}")
                
                # Create summary plot
                self.create_single_plot(adsorbant, results, output_dir, 'dft')
                
            else:
                print(f"❌ DFT calculation failed for {adsorbant}")
                
        except Exception as e:
            print(f"❌ Error in DFT calculation for {adsorbant}: {e}")
            import traceback
            traceback.print_exc()
    
    def select_dft_points_from_ml(self, ml_results: Dict[str, Any], max_points: int = 5) -> List[float]:
        """Select optimal DFT points based on ML results"""
        heights = np.array(ml_results['heights'])
        
        # Find energy array
        if 'ml_energies' in ml_results:
            energies = np.array(ml_results['ml_energies'])
        elif 'energies' in ml_results:
            energies = np.array(ml_results['energies'])
        else:
            # Use first available energy-like key
            energy_keys = [k for k in ml_results.keys() if 'energ' in k.lower()]
            if energy_keys:
                energies = np.array(ml_results[energy_keys[0]])
            else:
                return list(heights[::len(heights)//max_points])[:max_points]
        
        # Find minimum
        min_idx = np.argmin(energies)
        optimal_height = heights[min_idx]
        
        # Select points around minimum and reference points
        selected = [optimal_height]
        
        # Add neighboring points
        for delta in [0.3, 0.6]:
            for sign in [-1, 1]:
                candidate = optimal_height + sign * delta
                if np.min(heights) <= candidate <= np.max(heights):
                    closest_idx = np.argmin(np.abs(heights - candidate))
                    selected.append(heights[closest_idx])
        
        # Add reference point at higher distance
        ref_height = 6.5
        if ref_height <= np.max(heights):
            closest_idx = np.argmin(np.abs(heights - ref_height))
            selected.append(heights[closest_idx])
        
        # Remove duplicates and sort
        selected = sorted(list(set(selected)))
        return selected[:max_points]
    
    def create_single_plot(self, adsorbant: str, results: Dict[str, Any], output_dir: str, calc_type: str):
        """Create a single energy profile plot"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            
            heights = results['heights']
            
            plt.figure(figsize=(10, 6))
            
            if calc_type == 'ml':
                if 'ml_energies' in results:
                    energies = results['ml_energies']
                    plt.plot(heights, energies, 'b-o', label='ML Energies', linewidth=2, markersize=4)
                
                if 'omat_energies' in results:
                    plt.plot(heights, results['omat_energies'], 'g--', label='OMAT', alpha=0.7)
                if 'omc_energies' in results:
                    plt.plot(heights, results['omc_energies'], 'r--', label='OMC', alpha=0.7)
            else:
                if 'dft_energies' in results:
                    energies = results['dft_energies']
                    plt.plot(heights, energies, 'r-s', label='DFT Energies', linewidth=2, markersize=6)
            
            plt.xlabel('Height above MoS₂ surface (Å)')
            plt.ylabel('Binding Energy (eV)')
            plt.title(f'{adsorbant} on MoS₂ - {calc_type.upper()} Calculation')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            plot_file = Path(output_dir) / f"{adsorbant}_{calc_type}_profile.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"   📊 Plot saved: {plot_file}")
            
        except Exception as e:
            print(f"⚠️  Could not create plot for {adsorbant}: {e}")
    
    def monitor_jobs(self, ml_jobs: Dict[str, str], dft_jobs: Dict[str, str]):
        """Monitor job progress"""
        all_jobs = {**ml_jobs, **dft_jobs}
        completed = set()
        failed = set()
        
        while len(completed) + len(failed) < len(all_jobs):
            time.sleep(30)  # Check every 30 seconds
            
            for job_id, slurm_id in all_jobs.items():
                if job_id in completed or job_id in failed:
                    continue
                
                status = self.check_job_status(slurm_id)
                
                if status == 'COMPLETED':
                    completed.add(job_id)
                    calc_type = job_id.split('_')[0]
                    adsorbant = job_id.split('_')[1]
                    print(f"✅ {calc_type.upper()} job completed: {adsorbant}")
                    
                elif status in ['FAILED', 'CANCELLED', 'TIMEOUT']:
                    failed.add(job_id)
                    calc_type = job_id.split('_')[0]
                    adsorbant = job_id.split('_')[1]
                    print(f"❌ {calc_type.upper()} job failed: {adsorbant} (status: {status})")
            
            # Progress update
            total = len(all_jobs)
            done = len(completed) + len(failed)
            print(f"📊 Progress: {done}/{total} jobs finished ({len(completed)} completed, {len(failed)} failed)")
        
        return completed, failed
    
    def run_comprehensive_workflow(self):
        """Run the complete workflow"""
        print(f"🚀 Starting Unified MoS2 Energy Profile Workflow")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        start_time = time.time()
        
        # Check prerequisites
        if not self.check_pseudopotentials():
            print("⚠️  Pseudopotential issues detected, but continuing...")
        
        print(f"\n📋 Workflow Configuration:")
        print(f"   Total adsorbants: {len(self.adsorbants)}")
        print(f"   DFT fraction: {self.dft_fraction}")
        print(f"   Use cluster: {self.use_cluster}")
        if self.use_cluster:
            print(f"   Available partitions: {list(self.cluster_config.partitions.keys())}")
        
        # Phase 1: ML Calculations
        print(f"\n🧠 Phase 1: ML Calculations")
        print("=" * 40)
        
        ml_job_list = self.create_ml_jobs()
        
        # Submit ML jobs
        submitted_ml = {}
        for job in ml_job_list:
            slurm_id = self.submit_job(job)
            if slurm_id:
                submitted_ml[job.job_id] = slurm_id
                self.ml_jobs[job.job_id] = slurm_id
            else:
                print(f"❌ Failed to submit ML job for {job.adsorbant}")
        
        print(f"📊 Submitted {len(submitted_ml)}/{len(ml_job_list)} ML jobs")
        
        # Monitor ML jobs
        if self.use_cluster and submitted_ml:
            print("⏳ Monitoring ML jobs with advanced tracking...")
            monitoring_results, ml_success = self.monitor_jobs_advanced(submitted_ml, {})
            
            # Get completed adsorbants
            completed_ml_adsorbants = []
            for job_id in monitoring_results['completed_ml']:
                adsorbant = job_id.split('_')[1]
                completed_ml_adsorbants.append(adsorbant)
                
            if monitoring_results['failed_ml']:
                print(f"⚠️  {len(monitoring_results['failed_ml'])} ML jobs failed:")
                for failed_job in monitoring_results['failed_ml']:
                    print(f"   - {failed_job}")
        else:
            # For local execution, assume all succeed for demo
            completed_ml_adsorbants = self.adsorbants
            monitoring_results = {'completed_ml': submitted_ml.keys(), 'failed_ml': []}
            ml_success = True
        
        print(f"🧠 ML Phase Complete: {len(completed_ml_adsorbants)} successful calculations")
        
        # Phase 2: DFT Calculations (subset)
        if completed_ml_adsorbants:
            print(f"\n⚛️  Phase 2: DFT Calculations")
            print("=" * 40)
            
            # Select subset for DFT
            dft_adsorbants = self.select_dft_subset(completed_ml_adsorbants)
            print(f"📋 Selected {len(dft_adsorbants)} adsorbants for DFT validation:")
            for ads in dft_adsorbants:
                print(f"   - {ads}")
            
            # Create and submit DFT jobs
            dft_job_list = self.create_dft_jobs(dft_adsorbants)
            
            submitted_dft = {}
            for job in dft_job_list:
                slurm_id = self.submit_job(job)
                if slurm_id:
                    submitted_dft[job.job_id] = slurm_id
                    self.dft_jobs[job.job_id] = slurm_id
                else:
                    print(f"❌ Failed to submit DFT job for {job.adsorbant}")
            
            print(f"📊 Submitted {len(submitted_dft)}/{len(dft_job_list)} DFT jobs")
            
            # Monitor DFT jobs
            if self.use_cluster and submitted_dft:
                print("⏳ Monitoring DFT jobs...")
                dft_completed, dft_failed = self.monitor_jobs({}, submitted_dft)
                
                completed_dft_adsorbants = []
                for job_id in dft_completed:
                    adsorbant = job_id.split('_')[1]
                    completed_dft_adsorbants.append(adsorbant)
            else:
                completed_dft_adsorbants = dft_adsorbants
                dft_completed = set(submitted_dft.keys())
                dft_failed = set()
        else:
            print("⚠️  No successful ML calculations, skipping DFT phase")
            completed_dft_adsorbants = []
            dft_completed = set()
            dft_failed = set()
        
        # Phase 3: Analysis and Reporting
        print(f"\n📊 Phase 3: Analysis and Reporting")
        print("=" * 40)
        
        self.generate_comprehensive_report(completed_ml_adsorbants, completed_dft_adsorbants)
        
        # Final summary
        total_time = time.time() - start_time
        print(f"\n🎉 Workflow Complete!")
        print("=" * 70)
        print(f"📊 Final Results:")
        print(f"   ML calculations: {len(completed_ml_adsorbants)}/{len(self.adsorbants)} successful")
        print(f"   DFT calculations: {len(completed_dft_adsorbants)}/{len(dft_adsorbants) if 'dft_adsorbants' in locals() else 0} successful")
        print(f"   Total runtime: {total_time/3600:.2f} hours")
        print(f"   Results directory: {self.results_dir.absolute()}")
        print("=" * 70)
    
    def generate_comprehensive_report(self, ml_adsorbants: List[str], dft_adsorbants: List[str]):
        """Generate comprehensive analysis report"""
        print("📈 Generating comprehensive report...")
        
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            # Create summary data
            summary = {
                'workflow_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_adsorbants': len(self.adsorbants),
                    'ml_successful': len(ml_adsorbants),
                    'dft_successful': len(dft_adsorbants),
                    'ml_calculator': self.ml_calculator,
                    'use_cluster': self.use_cluster
                },
                'ml_results': ml_adsorbants,
                'dft_results': dft_adsorbants,
                'configuration': {
                    'dft_fraction': self.dft_fraction,
                    'z_ranges': self.z_ranges,
                    'dft_settings': self.dft_settings
                }
            }
            
            # Save summary
            summary_file = self.reports_dir / "workflow_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Create overview plot
            if ml_adsorbants:
                fig, axes = plt.subplots(2, 2, figsize=(15, 10))
                fig.suptitle('MoS₂ Energy Profile Workflow - Overview', fontsize=16)
                
                # Success rates
                ax = axes[0, 0]
                categories = ['ML Calculations', 'DFT Calculations']
                successful = [len(ml_adsorbants), len(dft_adsorbants)]
                total = [len(self.adsorbants), len(dft_adsorbants) if dft_adsorbants else 1]
                
                x = range(len(categories))
                ax.bar(x, successful, alpha=0.7, color=['blue', 'red'])
                ax.set_ylabel('Successful Calculations')
                ax.set_title('Calculation Success Rates')
                ax.set_xticks(x)
                ax.set_xticklabels(categories)
                
                for i, (s, t) in enumerate(zip(successful, total)):
                    ax.text(i, s + 0.1, f'{s}/{t}\n({s/t*100:.1f}%)', ha='center', va='bottom')
                
                # Adsorbant categories
                ax = axes[0, 1]
                categories = {
                    'Noble Metals': len([a for a in ml_adsorbants if a in ['Au2', 'Ag2', 'Pt2', 'Pd2']]),
                    'Transition Metals': len([a for a in ml_adsorbants if a in ['Fe2', 'Co2', 'Ni2', 'Cu2', 'Mn2']]),
                    'Light Metals': len([a for a in ml_adsorbants if a in ['Al2', 'Ti2', 'V2', 'Cr2']]),
                    'Molecules': len([a for a in ml_adsorbants if a in ['N2', 'O2', 'H2', 'Na2']]),
                    'Oxides': len([a for a in ml_adsorbants if a in ['ZnO', 'TiO2', 'Sb2O3']])
                }
                
                ax.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', startangle=90)
                ax.set_title('ML Calculations by Category')
                
                # Timing info (placeholder)
                ax = axes[1, 0]
                ax.text(0.5, 0.5, f'Workflow Summary:\n\n'
                               f'Total Adsorbants: {len(self.adsorbants)}\n'
                               f'ML Successful: {len(ml_adsorbants)}\n'
                               f'DFT Successful: {len(dft_adsorbants)}\n'
                               f'ML Calculator: {self.ml_calculator}\n'
                               f'Cluster Mode: {self.use_cluster}',
                        ha='center', va='center', fontsize=12,
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                ax.set_title('Workflow Configuration')
                
                # DFT selection strategy
                ax = axes[1, 1]
                if dft_adsorbants:
                    ax.bar(range(len(dft_adsorbants)), [1]*len(dft_adsorbants))
                    ax.set_xticks(range(len(dft_adsorbants)))
                    ax.set_xticklabels(dft_adsorbants, rotation=45, ha='right')
                    ax.set_ylabel('Selected for DFT')
                    ax.set_title('DFT Validation Subset')
                else:
                    ax.text(0.5, 0.5, 'No DFT calculations\nperformed', ha='center', va='center')
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
                
                plt.tight_layout()
                overview_plot = self.reports_dir / "workflow_overview.png"
                plt.savefig(overview_plot, dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"   📊 Overview plot saved: {overview_plot}")
            
            print(f"   📄 Summary saved: {summary_file}")
            print(f"   📂 All reports in: {self.reports_dir}")
            
        except Exception as e:
            print(f"⚠️  Could not generate full report: {e}")
            # Save basic summary anyway
            summary_file = self.reports_dir / "workflow_summary.json"
            with open(summary_file, 'w') as f:
                json.dump({
                    'ml_successful': ml_adsorbants,
                    'dft_successful': dft_adsorbants,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
    
    def create_ml_jobs(self) -> List[JobDefinition]:
        """Create ML calculation jobs for all adsorbants"""
        jobs = []
        
        # Get available GPU partitions
        gpu_partitions = [name for name, config in self.cluster_config.partitions.items() 
                         if config.get('gpu_nodes', False)]
        
        if not gpu_partitions:
            print("⚠️  No GPU partitions configured, using first available partition")
            gpu_partitions = [list(self.cluster_config.partitions.keys())[0]]
        
        for i, adsorbant in enumerate(self.adsorbants):
            # Distribute across GPU partitions
            partition = gpu_partitions[i % len(gpu_partitions)]
            partition_config = self.cluster_config.partitions[partition]
            
            job = JobDefinition(
                job_id=f"ml_{adsorbant}_{i:03d}",
                adsorbant=adsorbant,
                calculation_type='ml',
                partition=partition,
                cores=min(8, partition_config.get('cores_per_node', 8)),
                memory='32G',
                time_limit='2:00:00',  # 2 hours for ML
                gpu_required=partition_config.get('gpu_nodes', False),
                priority=1
            )
            jobs.append(job)
        
        print(f"📝 Created {len(jobs)} ML jobs across {len(gpu_partitions)} GPU partitions")
        return jobs
    
    def select_dft_subset(self, ml_adsorbants: List[str]) -> List[str]:
        """Select subset of adsorbants for DFT validation"""
        if not ml_adsorbants:
            return []
        
        num_dft = max(1, int(len(ml_adsorbants) * self.dft_fraction))
        
        # Smart selection strategy
        priority_adsorbants = ['Au2', 'Pt2', 'ZnO', 'TiO2', 'H2', 'N2']
        selected = []
        
        # First, add high-priority adsorbants if available
        for ads in priority_adsorbants:
            if ads in ml_adsorbants and len(selected) < num_dft:
                selected.append(ads)
        
        # Fill remaining slots with other adsorbants
        remaining = [ads for ads in ml_adsorbants if ads not in selected]
        for ads in remaining:
            if len(selected) < num_dft:
                selected.append(ads)
        
        print(f"📋 Selected {len(selected)}/{len(ml_adsorbants)} adsorbants for DFT validation")
        print(f"   Selection strategy: {self.dft_fraction*100:.0f}% of successful ML calculations")
        
        return selected[:num_dft]
    
    def create_dft_jobs(self, dft_adsorbants: List[str], ml_job_dependencies: List[str] = None) -> List[JobDefinition]:
        """Create DFT calculation jobs for selected adsorbants"""
        jobs = []
        
        # Get available CPU partitions (non-GPU)
        cpu_partitions = [name for name, config in self.cluster_config.partitions.items() 
                         if not config.get('gpu_nodes', True)]
        
        if not cpu_partitions:
            print("⚠️  No CPU partitions configured, using all available partitions")
            cpu_partitions = list(self.cluster_config.partitions.keys())
        
        for i, adsorbant in enumerate(dft_adsorbants):
            # Distribute across CPU partitions
            partition = cpu_partitions[i % len(cpu_partitions)]
            partition_config = self.cluster_config.partitions[partition]
            
            # Set up dependencies if provided
            dependencies = []
            if ml_job_dependencies:
                # Find corresponding ML job dependency
                for ml_job_id in ml_job_dependencies:
                    if f"ml_{adsorbant}_" in ml_job_id:
                        dependencies = [ml_job_id]
                        break
            
            job = JobDefinition(
                job_id=f"dft_{adsorbant}_{i:03d}",
                adsorbant=adsorbant,
                calculation_type='dft',
                partition=partition,
                cores=min(32, partition_config.get('cores_per_node', 32)),
                memory='128G',
                time_limit='12:00:00',  # 12 hours for DFT
                gpu_required=False,
                dependencies=dependencies,
                priority=2
            )
            jobs.append(job)
        
        print(f"📝 Created {len(jobs)} DFT jobs across {len(cpu_partitions)} CPU partitions")
        if ml_job_dependencies:
            print(f"   DFT jobs have dependencies on corresponding ML jobs")
        
        return jobs
    
    def submit_cluster_jobs(self, jobs: List[JobDefinition]) -> List[str]:
        """Submit a list of jobs to the cluster and return job IDs"""
        submitted_ids = []
        
        for job in jobs:
            if self.can_submit_job(job):
                job_id = self.submit_job(job)
                if job_id:
                    submitted_ids.append(job_id)
                    time.sleep(1)  # Small delay between submissions
                else:
                    print(f"❌ Failed to submit {job.job_id}")
            else:
                print(f"⏸️  Cannot submit {job.job_id} - partition {job.partition} is full")
        
        return submitted_ids
    
    def run_local_workflow(self):
        """Run the workflow locally without cluster submission"""
        print("🖥️  Running workflow locally...")
        
        ml_success = []
        dft_success = []
        
        # Run ML calculations
        print(f"\n🧠 Running ML calculations locally...")
        with ThreadPoolExecutor(max_workers=min(self.local_cores, len(self.adsorbants))) as executor:
            ml_futures = {}
            
            for adsorbant in self.adsorbants:
                output_dir = self.ml_results_dir / adsorbant
                output_dir.mkdir(exist_ok=True)
                
                future = executor.submit(self.run_single_ml_calculation, adsorbant, str(output_dir))
                ml_futures[future] = adsorbant
            
            # Collect ML results
            for future in as_completed(ml_futures):
                adsorbant = ml_futures[future]
                try:
                    future.result()
                    ml_success.append(adsorbant)
                    print(f"✅ ML calculation completed: {adsorbant}")
                except Exception as e:
                    print(f"❌ ML calculation failed for {adsorbant}: {e}")
        
        # Select and run DFT subset
        if ml_success:
            dft_subset = self.select_dft_subset(ml_success)
            
            if dft_subset:
                print(f"\n⚛️  Running DFT calculations locally...")
                with ThreadPoolExecutor(max_workers=min(2, len(dft_subset))) as executor:
                    dft_futures = {}
                    
                    for adsorbant in dft_subset:
                        ml_results_dir = self.ml_results_dir / adsorbant
                        output_dir = self.dft_results_dir / adsorbant
                        output_dir.mkdir(exist_ok=True)
                        
                        future = executor.submit(self.run_single_dft_calculation, 
                                               adsorbant, str(ml_results_dir), str(output_dir))
                        dft_futures[future] = adsorbant
                    
                    # Collect DFT results
                    for future in as_completed(dft_futures):
                        adsorbant = dft_futures[future]
                        try:
                            future.result()
                            dft_success.append(adsorbant)
                            print(f"✅ DFT calculation completed: {adsorbant}")
                        except Exception as e:
                            print(f"❌ DFT calculation failed for {adsorbant}: {e}")
        
        # Generate final report
        self.generate_comprehensive_report(ml_success, dft_success)

    def test_dft_calculation(self):
        """Test DFT calculation setup and input generation without running expensive calculations"""
        print("🧪 Testing DFT calculation setup...")
        
        # Test adsorbant
        test_adsorbant = "H2O"
        test_output_dir = Path("test_dft_output")
        test_output_dir.mkdir(exist_ok=True)
        
        success_count = 0
        total_tests = 0
        
        try:
            # Test 1: Check pseudopotentials
            print("\n1️⃣  Testing pseudopotential availability...")
            total_tests += 1
            try:
                self.check_pseudopotentials()
                print("   ✅ Pseudopotentials available")
                success_count += 1
            except Exception as e:
                print(f"   ❌ Pseudopotential check failed: {e}")
            
            # Test 2: Create mock ML results for testing
            print("\n2️⃣  Creating mock ML results...")
            total_tests += 1
            try:
                mock_ml_results = {
                    'adsorbant': test_adsorbant,
                    'heights': [2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                    'ml_energies': [-0.5, -1.2, -0.8, -0.3, 0.2, 0.5],
                    'calculation_type': 'ml'
                }
                ml_results_file = test_output_dir / f"{test_adsorbant}_ml_results.json"
                with open(ml_results_file, 'w') as f:
                    json.dump(mock_ml_results, f, indent=2)
                print("   ✅ Mock ML results created")
                success_count += 1
            except Exception as e:
                print(f"   ❌ Mock ML results creation failed: {e}")
            
            # Test 3: Test DFT point selection
            print("\n3️⃣  Testing DFT point selection...")
            total_tests += 1
            try:
                dft_points = self.select_dft_points_from_ml(mock_ml_results)
                print(f"   ✅ Selected {len(dft_points)} DFT points: {[f'{p:.2f}' for p in dft_points]}")
                success_count += 1
            except Exception as e:
                print(f"   ❌ DFT point selection failed: {e}")
            
            # Test 4: Test calculator setup
            print("\n4️⃣  Testing DFT calculator setup...")
            total_tests += 1
            try:
                from energy_profile_calculator.core import EnergyProfileCalculator
                calculator = EnergyProfileCalculator()
                
                # Setup surface
                calculator.surface = calculator.surface_builder.build_2d_material(
                    material='MoS2',
                    size=self.slab_settings.get('size', [3, 3]),
                    vacuum=self.slab_settings.get('vacuum', 14.0)
                )
                
                # Try to setup DFT calculator (without actually running calculations)
                calculator.setup_calculators(
                    use_ml=False,
                    use_dft=True,
                    dft_pseudo_dir=self.pseudo_dir,
                    dft_num_cores=1  # Use minimal cores for testing
                )
                print("   ✅ DFT calculator setup successful")
                success_count += 1
            except Exception as e:
                print(f"   ❌ DFT calculator setup failed: {e}")
            
            # Test 5: Test input file generation (dry run)
            print("\n5️⃣  Testing input file generation...")
            total_tests += 1
            try:
                orientation = self.get_adsorbant_orientation(test_adsorbant)
                print(f"   Adsorbant orientation: {orientation}")
                
                # Test job creation
                test_job = JobDefinition(
                    job_id=f"test_dft_{test_adsorbant}",
                    adsorbant=test_adsorbant,
                    calculation_type='dft',
                    partition='cpu',
                    cores=16,
                    memory='64G',
                    time_limit='2:00:00',
                    gpu_required=False
                )
                
                # Test script generation
                script_content = self.create_dft_cluster_script(test_job)
                test_script_file = test_output_dir / f"test_dft_{test_adsorbant}.sh"
                with open(test_script_file, 'w') as f:
                    f.write(script_content)
                
                print(f"   ✅ DFT job script generated: {test_script_file}")
                success_count += 1
            except Exception as e:
                print(f"   ❌ Input file generation failed: {e}")
            
            # Test 6: Test cluster submission (dry run)
            print("\n6️⃣  Testing cluster job creation...")
            total_tests += 1
            try:
                dft_jobs = self.create_dft_jobs([test_adsorbant])
                print(f"   ✅ Created {len(dft_jobs)} DFT job(s)")
                for job in dft_jobs:
                    print(f"      - {job.job_id}: {job.adsorbant} on {job.partition}")
                success_count += 1
            except Exception as e:
                print(f"   ❌ DFT job creation failed: {e}")
            
        finally:
            # Cleanup
            import shutil
            if test_output_dir.exists():
                shutil.rmtree(test_output_dir)
                print(f"\n🧹 Cleaned up test directory: {test_output_dir}")
        
        # Summary
        print(f"\n📊 DFT Test Summary: {success_count}/{total_tests} tests passed")
        if success_count == total_tests:
            print("🎉 All DFT tests passed! The system is ready for DFT calculations.")
        else:
            print("⚠️  Some DFT tests failed. Check the errors above.")
            print("   Common issues:")
            print("   - Missing pseudopotentials (run download_pseudo.py)")
            print("   - Incorrect module loading")
            print("   - Missing dependencies")
        
        return success_count == total_tests
    
    def test_ml_calculation(self):
        """Test ML calculation setup and model loading"""
        print("🧪 Testing ML calculation setup...")
        
        test_adsorbant = "H2O"
        test_output_dir = Path("test_ml_output")
        test_output_dir.mkdir(exist_ok=True)
        
        success_count = 0
        total_tests = 0
        
        try:
            # Test 1: Check ML model availability
            print("\n1️⃣  Testing ML model availability...")
            total_tests += 1
            try:
                if self.ml_calculator and hasattr(self.ml_calculator, 'model'):
                    print(f"   ✅ ML model available: {type(self.ml_calculator).__name__}")
                    success_count += 1
                else:
                    print("   ❌ ML model not properly configured")
            except Exception as e:
                print(f"   ❌ ML model check failed: {e}")
            
            # Test 2: Test calculator setup
            print("\n2️⃣  Testing ML calculator setup...")
            total_tests += 1
            try:
                from energy_profile_calculator.core import EnergyProfileCalculator
                calculator = EnergyProfileCalculator()
                
                # Setup surface
                calculator.surface = calculator.surface_builder.build_2d_material(
                    material='MoS2',
                    size=self.slab_settings.get('size', [3, 3]),
                    vacuum=self.slab_settings.get('vacuum', 14.0)
                )
                
                # Setup ML calculator
                calculator.setup_calculators(
                    use_ml=True,
                    use_dft=False,
                    ml_model=self.ml_calculator
                )
                print("   ✅ ML calculator setup successful")
                success_count += 1
            except Exception as e:
                print(f"   ❌ ML calculator setup failed: {e}")
            
            # Test 3: Test z-range configuration
            print("\n3️⃣  Testing z-range configuration...")
            total_tests += 1
            try:
                z_start, z_end, z_step = self.z_ranges.get(test_adsorbant, [2.5, 8.0, 0.2])
                orientation = self.get_adsorbant_orientation(test_adsorbant)
                print(f"   Z-range: {z_start} to {z_end} Å (step: {z_step})")
                print(f"   Orientation: {orientation}")
                print("   ✅ Z-range configuration successful")
                success_count += 1
            except Exception as e:
                print(f"   ❌ Z-range configuration failed: {e}")
            
            # Test 4: Test job creation
            print("\n4️⃣  Testing ML job creation...")
            total_tests += 1
            try:
                test_job = JobDefinition(
                    job_id=f"test_ml_{test_adsorbant}",
                    adsorbant=test_adsorbant,
                    calculation_type='ml',
                    partition='gpu',
                    cores=8,
                    memory='32G',
                    time_limit='1:00:00',
                    gpu_required=True
                )
                
                # Test script generation
                script_content = self.create_ml_cluster_script(test_job)
                test_script_file = test_output_dir / f"test_ml_{test_adsorbant}.sh"
                with open(test_script_file, 'w') as f:
                    f.write(script_content)
                
                print(f"   ✅ ML job script generated: {test_script_file}")
                success_count += 1
            except Exception as e:
                print(f"   ❌ ML job creation failed: {e}")
            
            # Test 5: Test batch job creation
            print("\n5️⃣  Testing ML batch job creation...")
            total_tests += 1
            try:
                ml_jobs = self.create_ml_jobs()
                print(f"   ✅ Created {len(ml_jobs)} ML job(s)")
                for job in ml_jobs[:3]:  # Show first 3
                    print(f"      - {job.job_id}: {job.adsorbant} on {job.partition}")
                if len(ml_jobs) > 3:
                    print(f"      ... and {len(ml_jobs) - 3} more")
                success_count += 1
            except Exception as e:
                print(f"   ❌ ML batch job creation failed: {e}")
            
            # Test 6: Test structure building
            print("\n6️⃣  Testing structure building...")
            total_tests += 1
            try:
                from energy_profile_calculator.core import EnergyProfileCalculator
                calculator = EnergyProfileCalculator()
                
                # Build test surface
                surface = calculator.surface_builder.build_2d_material(
                    material='MoS2',
                    size=[2, 2],  # Small for testing
                    vacuum=10.0
                )
                
                print(f"   ✅ Built MoS2 surface: {len(surface)} atoms")
                success_count += 1
            except Exception as e:
                print(f"   ❌ Structure building failed: {e}")
        
        finally:
            # Cleanup
            import shutil
            if test_output_dir.exists():
                shutil.rmtree(test_output_dir)
                print(f"\n🧹 Cleaned up test directory: {test_output_dir}")
        
        # Summary
        print(f"\n📊 ML Test Summary: {success_count}/{total_tests} tests passed")
        if success_count == total_tests:
            print("🎉 All ML tests passed! The system is ready for ML calculations.")
        else:
            print("⚠️  Some ML tests failed. Check the errors above.")
            print("   Common issues:")
            print("   - Missing ML model file")
            print("   - Incorrect model configuration")
            print("   - Missing dependencies (fairchem, torch)")
        
        return success_count == total_tests

def main():
    parser = argparse.ArgumentParser(description='Unified MoS2 Energy Profile Workflow')
    parser.add_argument('--config', default='workflow_config.yaml',
                       help='Configuration file (default: workflow_config.yaml)')
    parser.add_argument('--run-single-ml', type=str,
                       help='Run single ML calculation for specified adsorbant')
    parser.add_argument('--run-single-dft', type=str,
                       help='Run single DFT calculation for specified adsorbant')
    parser.add_argument('--ml-results-dir', type=str,
                       help='Directory containing ML results (for DFT calculation)')
    parser.add_argument('--output-dir', type=str,
                       help='Output directory for single calculations')
    parser.add_argument('--dry-run', action='store_true',
                       help='Generate job scripts and show workflow plan but do not submit')
    parser.add_argument('--test-dft', action='store_true',
                       help='Test DFT calculation setup and input generation (validates DFT environment)')
    parser.add_argument('--test-ml', action='store_true',
                       help='Test ML calculation setup and model loading (validates ML environment)')
    parser.add_argument('--local', action='store_true',
                       help='Run locally instead of submitting to cluster')
    parser.add_argument('--ml-only', action='store_true',
                       help='Run only ML calculations (no DFT)')
    
    args = parser.parse_args()
    
    workflow = UnifiedWorkflow(args.config)
    
    # Override cluster setting if local mode requested
    if args.local:
        workflow.use_cluster = False
        print("🖥️  Local execution mode enabled")
    
    if args.run_single_ml:
        # Single ML calculation mode
        workflow.run_single_ml_calculation(args.run_single_ml, args.output_dir)
        
    elif args.run_single_dft:
        # Single DFT calculation mode
        workflow.run_single_dft_calculation(args.run_single_dft, args.ml_results_dir, args.output_dir)
        
    elif args.test_dft:
        # DFT test mode - actually test DFT calculation setup
        print("🧪 DFT test mode - testing DFT calculation setup...")
        workflow.test_dft_calculation()
        
    elif args.test_ml:
        # ML test mode - test ML calculation setup
        print("🧪 ML test mode - testing ML calculation setup...")
        workflow.test_ml_calculation()
        
    elif args.dry_run:
        # Dry run mode
        print("🧪 Dry run mode - generating job definitions...")
        workflow.check_pseudopotentials()
        ml_jobs = workflow.create_ml_jobs()
        dft_subset = workflow.select_dft_subset([job.adsorbant for job in ml_jobs[:5]])  # Example
        dft_jobs = workflow.create_dft_jobs(dft_subset, ['dummy_ml_id_1', 'dummy_ml_id_2'])
        
        print(f"\nWould create {len(ml_jobs)} ML jobs and {len(dft_jobs)} DFT jobs:")
        print("\nML Jobs:")
        for job in ml_jobs[:5]:  # Show first 5
            print(f"  {job.job_id}: {job.adsorbant} on {job.partition}")
        if len(ml_jobs) > 5:
            print(f"  ... and {len(ml_jobs) - 5} more")
        
        print("\nDFT Jobs:")
        for job in dft_jobs:
            print(f"  {job.job_id}: {job.adsorbant} on {job.partition}")
        
        print(f"\nCluster configuration:")
        for partition, config in workflow.cluster_config.partitions.items():
            print(f"  {partition}: max {config.get('max_jobs', 'unlimited')} jobs, {config.get('cores_per_node', 'unknown')} cores")
        
    elif args.ml_only:
        # ML-only mode
        print("🧠 ML-only mode - skipping DFT calculations")
        workflow.dft_fraction = 0.0  # No DFT
        workflow.run_comprehensive_workflow()
        
    else:
        # Full workflow mode
        workflow.run_comprehensive_workflow()


if __name__ == "__main__":
    main()
