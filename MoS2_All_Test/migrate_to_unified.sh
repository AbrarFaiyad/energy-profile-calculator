#!/bin/bash
# Migration Script: Old Scripts → Unified Workflow
# This script helps migrate from the old job_manager.py + comprehensive_runner.py approach
# to the new unified_workflow.py

echo "🔄 MoS2 Energy Profile Workflow - Migration Script"
echo "=================================================="
echo "This script helps you migrate from the old separate scripts to the unified workflow"
echo

# Check if we're in the right directory
if [ ! -f "unified_workflow.py" ]; then
    echo "❌ Error: unified_workflow.py not found in current directory"
    echo "Please run this script from the MoS2_All_Test directory"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo "✅ Found unified_workflow.py"
echo

# Check for old configuration
if [ -f "job_config.yaml" ]; then
    echo "📝 Found old job_config.yaml"
    echo "   The unified workflow uses workflow_config.yaml instead"
    
    if [ ! -f "workflow_config.yaml" ]; then
        echo "   Creating workflow_config.yaml from your old configuration..."
        python3 -c "
import yaml
import sys

# Load old config
try:
    with open('job_config.yaml', 'r') as f:
        old_config = yaml.safe_load(f)
    print('   ✅ Loaded old configuration')
except:
    print('   ❌ Could not read old configuration')
    sys.exit(1)

# Create new config structure
new_config = {
    'ml_calculator': old_config.get('ml_calculator', 'equiformer_v2_153M_omat'),
    'pseudo_dir': old_config.get('pseudo_dir', '/home/afaiyad/QE/qe-7.4.1/pseudo'),
    'materials': old_config.get('materials', ['MoS2']),
    'adsorbants': old_config.get('adsorbants', []),
    'z_ranges': old_config.get('z_ranges', {}),
    'dft_settings': old_config.get('dft_settings', {}),
    'slab_settings': old_config.get('slab_settings', {}),
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
                'time_limit': '3-00:00:00',
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
            'export OMP_NUM_THREADS=\$SLURM_CPUS_PER_TASK'
        ],
        'job_submit_command': 'sbatch',
        'job_status_command': 'squeue',
        'user_env_var': 'afaiyad'
    }
}

# Save new config
with open('workflow_config.yaml', 'w') as f:
    yaml.dump(new_config, f, default_flow_style=False, indent=2)

print('   ✅ Created workflow_config.yaml')
print(f'   📊 Migrated {len(old_config.get(\"adsorbants\", []))} adsorbants')
"
    else
        echo "   ✅ workflow_config.yaml already exists"
    fi
    echo
fi

# Test the unified workflow
echo "🧪 Testing unified workflow..."
python unified_workflow.py --dry-run > /tmp/migration_test.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Unified workflow test successful!"
    echo "   $(grep 'Would create' /tmp/migration_test.log)"
else
    echo "❌ Unified workflow test failed. Check the output:"
    cat /tmp/migration_test.log
    echo
    echo "Please fix any issues before proceeding."
    exit 1
fi

echo
echo "🎯 Migration Summary"
echo "==================="
echo
echo "OLD APPROACH (deprecated):"
echo "  python job_manager.py --config job_config.yaml"
echo "  python comprehensive_runner.py --config job_config.yaml"
echo "  sbatch submit_comprehensive.sh"
echo
echo "NEW APPROACH (recommended):"
echo "  python unified_workflow.py --config workflow_config.yaml"
echo "  sbatch submit_unified_workflow.sh"
echo
echo "✅ Benefits of the unified approach:"
echo "   • Single script manages everything"
echo "   • Better job monitoring and progress tracking"
echo "   • More robust error handling"
echo "   • Cluster-agnostic design"
echo "   • Enhanced reporting and visualization"
echo
echo "🚀 Ready to run the unified workflow!"
echo "   Test locally: python unified_workflow.py --local --ml-only"
echo "   Full workflow: python unified_workflow.py"
echo "   Submit to cluster: sbatch submit_unified_workflow.sh"
echo

# Clean up
rm -f /tmp/migration_test.log

echo "📚 For more information, see the updated README.md"
echo "=================================================="
