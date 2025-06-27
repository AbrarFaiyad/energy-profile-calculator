#!/usr/bin/env python3
"""
User-Friendly Interactive Interface for MoS2 Energy Profile Calculations

This script provides an easy-to-use menu system for managing your calculations.
"""

import os
import sys
import subprocess
from pathlib import Path
import yaml
import json
from datetime import datetime

class MoS2Interface:
    def __init__(self):
        self.work_dir = Path.cwd()
        self.config_file = self.work_dir / "job_config.yaml"
        self.results_dir = self.work_dir / "results"
        self.logs_dir = self.work_dir / "logs"
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Print the main header"""
        print("=" * 70)
        print("🔬 MoS2 Energy Profile Calculation Suite")
        print("=" * 70)
        print(f"Working Directory: {self.work_dir}")
        print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
    
    def show_main_menu(self):
        """Display the main menu"""
        print("\n📋 MAIN MENU")
        print("-" * 30)
        print("1. 🔍 Check System Status")
        print("2. ⚙️  Configure Calculations")  
        print("3. 🧪 Validate Pseudopotentials")
        print("4. 🚀 Submit Job Manager")
        print("5. 📊 Monitor Progress")
        print("6. 📈 View Results")
        print("7. 🛠️  Troubleshooting")
        print("8. 📚 Help & Documentation")
        print("9. 🚪 Exit")
        print("-" * 30)
    
    def check_system_status(self):
        """Check the current system status"""
        self.clear_screen()
        self.print_header()
        print("\n🔍 SYSTEM STATUS CHECK")
        print("=" * 50)
        
        # Check if job manager is running
        try:
            result = subprocess.run(['squeue', '-u', os.getenv('USER'), '-n', 'mos2_job_manager', '-h'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                print("✅ Job Manager: RUNNING")
                job_info = result.stdout.strip().split()
                print(f"   Job ID: {job_info[0]}")
                print(f"   Status: {job_info[4]}")
            else:
                print("❌ Job Manager: NOT RUNNING")
        except:
            print("⚠️  Job Manager: Cannot check status")
        
        # Check queue status
        try:
            result = subprocess.run(['squeue', '-u', os.getenv('USER'), '-h'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                running_jobs = len([l for l in lines if l and 'R' in l])
                pending_jobs = len([l for l in lines if l and 'PD' in l])
                total_jobs = len([l for l in lines if l])
                
                print(f"\n📊 Current Queue Status:")
                print(f"   Total Jobs: {total_jobs}")
                print(f"   Running: {running_jobs}")
                print(f"   Pending: {pending_jobs}")
            else:
                print("⚠️  Cannot access queue information")
        except:
            print("⚠️  Queue status unavailable")
        
        # Check directories
        print(f"\n📁 Directory Status:")
        print(f"   Results: {len(list(self.results_dir.glob('*'))) if self.results_dir.exists() else 0} directories")
        print(f"   Logs: {len(list(self.logs_dir.glob('*'))) if self.logs_dir.exists() else 0} files")
        
        # Check configuration
        if self.config_file.exists():
            print("✅ Configuration: Present")
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
                print(f"   Materials: {len(config.get('materials', []))}")
                print(f"   Adsorbants: {len(config.get('adsorbants', []))}")
        else:
            print("❌ Configuration: Missing")
        
        input("\nPress Enter to continue...")
    
    def configure_calculations(self):
        """Interactive configuration setup"""
        self.clear_screen()
        self.print_header()
        print("\n⚙️  CALCULATION CONFIGURATION")
        print("=" * 50)
        
        # Load existing config or create default
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            print("📝 Loaded existing configuration")
        else:
            config = {
                'ml_calculator': 'uma-s-1',
                'pseudo_dir': '/home/afaiyad/QE/qe-7.4.1/pseudo',
                'materials': ['MoS2'],
                'adsorbants': ['H2O', 'Au2', 'Li'],
                'z_ranges': {
                    'H2O': [2.0, 8.0, 0.2],
                    'Au2': [2.5, 8.0, 0.3],
                    'Li': [2.0, 6.0, 0.2]
                },
                'dft_settings': {
                    'ecutwfc': 80,
                    'ecutrho': 640,
                    'kpts': [6, 6, 1],
                    'conv_thr': 1e-8
                }
            }
            print("📝 Created default configuration")
        
        while True:
            print(f"\n📋 Current Configuration:")
            print(f"   Materials: {', '.join(config['materials'])}")
            print(f"   Adsorbants: {', '.join(config['adsorbants'])}")
            print(f"   ML Calculator: {config['ml_calculator']}")
            print(f"   Pseudopotential Dir: {config['pseudo_dir']}")
            
            print(f"\n⚙️  Configuration Menu:")
            print("1. Add/Remove Materials")
            print("2. Add/Remove Adsorbants") 
            print("3. Modify Height Ranges")
            print("4. Adjust DFT Settings")
            print("5. Save Configuration")
            print("6. Return to Main Menu")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                self.configure_materials(config)
            elif choice == '2':
                self.configure_adsorbants(config)
            elif choice == '3':
                self.configure_height_ranges(config)
            elif choice == '4':
                self.configure_dft_settings(config)
            elif choice == '5':
                with open(self.config_file, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                print("✅ Configuration saved!")
                input("Press Enter to continue...")
            elif choice == '6':
                break
    
    def configure_materials(self, config):
        """Configure materials list"""
        available_materials = ['MoS2', 'WS2', 'graphene', 'h-BN', 'phosphorene', 'MoSe2', 'WSe2']
        
        print(f"\n🔬 Available Materials:")
        for i, mat in enumerate(available_materials, 1):
            status = "✅" if mat in config['materials'] else "❌"
            print(f"   {i}. {status} {mat}")
        
        print(f"\n📝 Actions:")
        print("A. Add material")
        print("R. Remove material")
        print("C. Clear all")
        print("D. Done")
        
        action = input("Select action (A/R/C/D): ").strip().upper()
        
        if action == 'A':
            try:
                num = int(input("Enter material number to add: "))
                if 1 <= num <= len(available_materials):
                    mat = available_materials[num-1]
                    if mat not in config['materials']:
                        config['materials'].append(mat)
                        print(f"✅ Added {mat}")
                    else:
                        print(f"⚠️  {mat} already in list")
            except ValueError:
                print("❌ Invalid number")
                
        elif action == 'R':
            if config['materials']:
                print("Current materials:")
                for i, mat in enumerate(config['materials'], 1):
                    print(f"   {i}. {mat}")
                try:
                    num = int(input("Enter number to remove: "))
                    if 1 <= num <= len(config['materials']):
                        removed = config['materials'].pop(num-1)
                        print(f"✅ Removed {removed}")
                except ValueError:
                    print("❌ Invalid number")
            else:
                print("❌ No materials to remove")
                
        elif action == 'C':
            config['materials'] = []
            print("✅ Cleared all materials")
        
        input("Press Enter to continue...")
    
    def configure_adsorbants(self, config):
        """Configure adsorbants list"""
        categories = {
            'Small Molecules': ['H2O', 'CO', 'CO2', 'NO', 'NH3', 'H2', 'N2', 'O2'],
            'Metal Clusters': ['Au2', 'Ag2', 'Pt2', 'Pd2', 'Li', 'Na', 'Ti2', 'Fe2'],
            'Metal Oxides': ['ZnO', 'TiO2', 'Sb2O3'],
            'Organic Molecules': ['F4TCNQ', 'tetracene', 'TCNQ', 'TTF']
        }
        
        print(f"\n🧪 Available Adsorbants by Category:")
        for category, adsorbants in categories.items():
            print(f"\n{category}:")
            for ads in adsorbants:
                status = "✅" if ads in config['adsorbants'] else "❌"
                print(f"   {status} {ads}")
        
        print(f"\n📝 Actions:")
        print("A. Add adsorbant (enter name)")
        print("R. Remove adsorbant")
        print("C. Clear all")
        print("D. Done")
        
        action = input("Select action (A/R/C/D): ").strip().upper()
        
        if action == 'A':
            ads = input("Enter adsorbant name: ").strip()
            if ads and ads not in config['adsorbants']:
                config['adsorbants'].append(ads)
                print(f"✅ Added {ads}")
            elif ads in config['adsorbants']:
                print(f"⚠️  {ads} already in list")
                
        elif action == 'R':
            if config['adsorbants']:
                print("Current adsorbants:")
                for i, ads in enumerate(config['adsorbants'], 1):
                    print(f"   {i}. {ads}")
                try:
                    num = int(input("Enter number to remove: "))
                    if 1 <= num <= len(config['adsorbants']):
                        removed = config['adsorbants'].pop(num-1)
                        print(f"✅ Removed {removed}")
                except ValueError:
                    print("❌ Invalid number")
            else:
                print("❌ No adsorbants to remove")
                
        elif action == 'C':
            config['adsorbants'] = []
            print("✅ Cleared all adsorbants")
        
        input("Press Enter to continue...")
    
    def configure_height_ranges(self, config):
        """Configure height ranges for adsorbants"""
        print(f"\n📏 Height Range Configuration")
        print("Format: [start, end, step] in Angstroms")
        
        for ads in config['adsorbants']:
            current = config['z_ranges'].get(ads, [2.0, 8.0, 0.2])
            print(f"\n{ads}: {current}")
            modify = input(f"Modify {ads} range? (y/N): ").strip().lower()
            
            if modify == 'y':
                try:
                    start = float(input(f"  Start height (current: {current[0]}): ") or current[0])
                    end = float(input(f"  End height (current: {current[1]}): ") or current[1])
                    step = float(input(f"  Step size (current: {current[2]}): ") or current[2])
                    
                    config['z_ranges'][ads] = [start, end, step]
                    print(f"✅ Updated {ads}: [{start}, {end}, {step}]")
                except ValueError:
                    print("❌ Invalid input, keeping current values")
        
        input("Press Enter to continue...")
    
    def configure_dft_settings(self, config):
        """Configure DFT calculation parameters"""
        print(f"\n⚡ DFT Settings Configuration")
        
        settings = config['dft_settings']
        print(f"Current settings:")
        for key, value in settings.items():
            print(f"   {key}: {value}")
        
        modify = input(f"\nModify DFT settings? (y/N): ").strip().lower()
        if modify == 'y':
            try:
                new_ecutwfc = input(f"Plane wave cutoff (current: {settings['ecutwfc']} Ry): ")
                if new_ecutwfc:
                    settings['ecutwfc'] = int(new_ecutwfc)
                
                new_ecutrho = input(f"Density cutoff (current: {settings['ecutrho']} Ry): ")
                if new_ecutrho:
                    settings['ecutrho'] = int(new_ecutrho)
                
                new_conv_thr = input(f"Convergence threshold (current: {settings['conv_thr']}): ")
                if new_conv_thr:
                    settings['conv_thr'] = float(new_conv_thr)
                
                print("✅ DFT settings updated")
            except ValueError:
                print("❌ Invalid input, keeping current values")
        
        input("Press Enter to continue...")
    
    def validate_pseudopotentials(self):
        """Run pseudopotential validation"""
        self.clear_screen()
        self.print_header()
        print("\n🧪 PSEUDOPOTENTIAL VALIDATION")
        print("=" * 50)
        
        print("1. 🔍 Check pseudopotentials")
        print("2. 📥 Download missing pseudopotentials")
        print("3. 🛠️  Auto-fix all missing pseudopotentials")
        print("4. 📚 List available elements for download")
        print("5. 🎯 Download specific element")
        print("6. 📈 Show detailed report")
        print("7. 🔙 Return to main menu")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            print("\nRunning pseudopotential check...")
            try:
                result = subprocess.run([sys.executable, 'check_pseudopotentials.py'], 
                                      capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
            except Exception as e:
                print(f"❌ Error running check: {e}")
                
        elif choice == '2':
            print("\nDownloading missing pseudopotentials...")
            try:
                result = subprocess.run([sys.executable, 'check_pseudopotentials.py', '--download'], 
                                      capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
            except Exception as e:
                print(f"❌ Error running download: {e}")
                
        elif choice == '3':
            print("\nAuto-fixing all missing pseudopotentials...")
            try:
                result = subprocess.run([sys.executable, 'check_pseudopotentials.py', '--auto-fix'], 
                                      capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
            except Exception as e:
                print(f"❌ Error running auto-fix: {e}")
                
        elif choice == '4':
            print("\nListing available elements...")
            try:
                result = subprocess.run([sys.executable, 'download_pseudo.py', '--list'], 
                                      capture_output=True, text=True)
                print(result.stdout)
            except Exception as e:
                print(f"❌ Error listing elements: {e}")
                
        elif choice == '5':
            element = input("Enter element symbol (e.g., H, Li, Mo): ").strip()
            if element:
                print(f"\nDownloading pseudopotential for {element}...")
                try:
                    result = subprocess.run([sys.executable, 'download_pseudo.py', element], 
                                          capture_output=True, text=True)
                    print(result.stdout)
                    if result.stderr:
                        print("Errors:")
                        print(result.stderr)
                except Exception as e:
                    print(f"❌ Error downloading {element}: {e}")
            else:
                print("❌ No element specified")
                
        elif choice == '6':
            print("\nGenerating detailed report...")
            try:
                result = subprocess.run([sys.executable, 'check_pseudopotentials.py', '--list-all'], 
                                      capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
            except Exception as e:
                print(f"❌ Error generating report: {e}")
                
        elif choice == '7':
            return
        else:
            print("❌ Invalid option")
        
        input("\nPress Enter to continue...")
    
    def submit_job_manager(self):
        """Submit the job manager"""
        self.clear_screen()
        self.print_header()
        print("\n🚀 SUBMIT JOB MANAGER")
        print("=" * 50)
        
        # Check if already running
        try:
            result = subprocess.run(['squeue', '-u', os.getenv('USER'), '-n', 'mos2_job_manager', '-h'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                print("⚠️  Job manager is already running!")
                print("Job ID:", result.stdout.strip().split()[0])
                cancel = input("Cancel existing job and submit new one? (y/N): ").strip().lower()
                if cancel == 'y':
                    job_id = result.stdout.strip().split()[0]
                    subprocess.run(['scancel', job_id])
                    print(f"✅ Cancelled job {job_id}")
                else:
                    input("Press Enter to continue...")
                    return
        except:
            pass
        
        print("Submitting job manager...")
        try:
            result = subprocess.run(['sbatch', 'job_manager_submit.sh'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                job_id = result.stdout.strip().split()[-1]
                print(f"✅ Job manager submitted successfully!")
                print(f"Job ID: {job_id}")
                print(f"Monitor with: tail -f logs/job_manager.o{job_id}")
            else:
                print("❌ Failed to submit job manager:")
                print(result.stderr)
        except Exception as e:
            print(f"❌ Error submitting job: {e}")
        
        input("\nPress Enter to continue...")
    
    def monitor_progress(self):
        """Monitor calculation progress"""
        self.clear_screen()
        self.print_header()
        print("\n📊 PROGRESS MONITORING")
        print("=" * 50)
        
        # Show queue status
        try:
            result = subprocess.run(['squeue', '-u', os.getenv('USER')], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("Current Queue:")
                print(result.stdout)
            else:
                print("❌ Cannot access queue")
        except:
            print("❌ Queue unavailable")
        
        # Show recent log entries
        log_files = list(self.logs_dir.glob('*.o*')) if self.logs_dir.exists() else []
        if log_files:
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            print(f"\nLatest log file: {latest_log.name}")
            print("Last 10 lines:")
            try:
                with open(latest_log, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-10:]:
                        print(f"  {line.rstrip()}")
            except:
                print("  Cannot read log file")
        
        input("\nPress Enter to continue...")
    
    def view_results(self):
        """View calculation results"""
        self.clear_screen()
        self.print_header()
        print("\n📈 RESULTS VIEWER")
        print("=" * 50)
        
        if not self.results_dir.exists():
            print("❌ No results directory found")
            input("Press Enter to continue...")
            return
        
        result_dirs = list(self.results_dir.iterdir())
        if not result_dirs:
            print("❌ No results available yet")
            input("Press Enter to continue...")
            return
        
        print(f"Found {len(result_dirs)} result directories:")
        for i, result_dir in enumerate(result_dirs, 1):
            print(f"   {i}. {result_dir.name}")
        
        try:
            choice = int(input(f"\nSelect result to view (1-{len(result_dirs)}): "))
            if 1 <= choice <= len(result_dirs):
                selected_dir = result_dirs[choice-1]
                print(f"\nContents of {selected_dir.name}:")
                for file in selected_dir.iterdir():
                    size = file.stat().st_size
                    print(f"   {file.name} ({size} bytes)")
                
                # Check for JSON results
                json_files = list(selected_dir.glob('*.json'))
                if json_files:
                    view_json = input("\nView JSON results? (y/N): ").strip().lower()
                    if view_json == 'y':
                        with open(json_files[0], 'r') as f:
                            data = json.load(f)
                            print("\nResults summary:")
                            if 'energies' in data:
                                energies = data['energies']
                                print(f"   Energy points: {len(energies)}")
                                print(f"   Min energy: {min(energies):.6f} eV")
                                print(f"   Max energy: {max(energies):.6f} eV")
        except (ValueError, IndexError):
            print("❌ Invalid selection")
        
        input("\nPress Enter to continue...")
    
    def troubleshooting(self):
        """Troubleshooting guide"""
        self.clear_screen()
        self.print_header()
        print("\n🛠️  TROUBLESHOOTING GUIDE")
        print("=" * 50)
        
        print("Common Issues and Solutions:")
        print("\n1. 🔴 Jobs not submitting")
        print("   - Check partition limits: sinfo")
        print("   - Verify SLURM access: squeue")
        print("   - Check job manager logs")
        
        print("\n2. 🔴 Pseudopotential errors")
        print("   - Run: python check_pseudopotentials.py")
        print("   - Verify path in configuration")
        print("   - Check file permissions")
        
        print("\n3. 🔴 CUDA/GPU errors")
        print("   - Check GPU availability: nvidia-smi")
        print("   - Verify CUDA modules: module list")
        print("   - Check partition access")
        
        print("\n4. 🔴 Memory issues")
        print("   - Reduce system size")
        print("   - Lower DFT cutoffs")
        print("   - Use fewer k-points")
        
        print("\n5. 🔴 Job manager not running")
        print("   - Check SLURM script syntax")
        print("   - Verify partition access")
        print("   - Check environment modules")
        
        print("\nDiagnostic Commands:")
        print("   squeue -u $USER          # Check your jobs")
        print("   sinfo                    # Check partition status")
        print("   module list              # Check loaded modules")
        print("   nvidia-smi               # Check GPU status")
        
        input("\nPress Enter to continue...")
    
    def show_help(self):
        """Show help and documentation"""
        self.clear_screen()
        self.print_header()
        print("\n📚 HELP & DOCUMENTATION")
        print("=" * 50)
        
        print("🔗 Key Files:")
        print("   README.md                 # Complete documentation")
        print("   job_config.yaml          # Configuration file")
        print("   check_pseudopotentials.py # Validation script")
        print("   job_manager.py           # Main job manager")
        
        print("\n🎯 Workflow:")
        print("   1. Configure calculations (materials, adsorbants)")
        print("   2. Validate pseudopotentials")
        print("   3. Submit job manager")
        print("   4. Monitor progress")
        print("   5. View results")
        
        print("\n🔬 Supported Materials:")
        print("   - 2D Materials: MoS2, graphene, h-BN, etc.")
        print("   - 73+ Adsorbants: H2O, metals, organics, etc.")
        
        print("\n⚡ Calculation Types:")
        print("   - ML: Fast screening with UMA-S-1")
        print("   - DFT: Accurate validation with QE")
        
        print("\n🖥️  Cluster Optimization:")
        print("   - GPU partitions for ML calculations")
        print("   - CPU partitions for DFT calculations")
        print("   - Automatic job scheduling and dependencies")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main interface loop"""
        while True:
            self.clear_screen()
            self.print_header()
            self.show_main_menu()
            
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == '1':
                self.check_system_status()
            elif choice == '2':
                self.configure_calculations()
            elif choice == '3':
                self.validate_pseudopotentials()
            elif choice == '4':
                self.submit_job_manager()
            elif choice == '5':
                self.monitor_progress()
            elif choice == '6':
                self.view_results()
            elif choice == '7':
                self.troubleshooting()
            elif choice == '8':
                self.show_help()
            elif choice == '9':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")
                input("Press Enter to continue...")


if __name__ == "__main__":
    interface = MoS2Interface()
    interface.run()
