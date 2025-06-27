#!/usr/bin/env python3
"""
Pseudopotential Checker for MoS2 Energy Profile Calculations

This script checks if all required pseudopotentials are available in the
specified directory before running energy profile calculations.
"""

import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

class PseudopotentialChecker:
    def __init__(self, pseudo_dir="/home/afaiyad/QE/qe-7.4.1/pseudo"):
        self.pseudo_dir = Path(pseudo_dir)
        self.required_pseudos = {}
        self.available_pseudos = {}
        self.missing_pseudos = []
        
        # PSLibrary download URLs
        self.pslibrary_urls = {
            'H': 'https://pseudopotentials.quantum-espresso.org/upf_files/H.pbe-kjpaw_psl.1.0.0.UPF',
            'Li': 'https://pseudopotentials.quantum-espresso.org/upf_files/Li.pbe-s-kjpaw_psl.1.0.0.UPF',
            'Be': 'https://pseudopotentials.quantum-espresso.org/upf_files/Be.pbe-n-kjpaw_psl.1.0.0.UPF',
            'B': 'https://pseudopotentials.quantum-espresso.org/upf_files/B.pbe-n-kjpaw_psl.1.0.0.UPF',
            'C': 'https://pseudopotentials.quantum-espresso.org/upf_files/C.pbe-n-kjpaw_psl.1.0.0.UPF',
            'N': 'https://pseudopotentials.quantum-espresso.org/upf_files/N.pbe-n-kjpaw_psl.1.0.0.UPF',
            'O': 'https://pseudopotentials.quantum-espresso.org/upf_files/O.pbe-n-kjpaw_psl.1.0.0.UPF',
            'F': 'https://pseudopotentials.quantum-espresso.org/upf_files/F.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Na': 'https://pseudopotentials.quantum-espresso.org/upf_files/Na.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Mg': 'https://pseudopotentials.quantum-espresso.org/upf_files/Mg.pbe-spnl-kjpaw_psl.1.0.0.UPF',
            'Al': 'https://pseudopotentials.quantum-espresso.org/upf_files/Al.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Si': 'https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-kjpaw_psl.1.0.0.UPF',
            'P': 'https://pseudopotentials.quantum-espresso.org/upf_files/P.pbe-n-kjpaw_psl.1.0.0.UPF',
            'S': 'https://pseudopotentials.quantum-espresso.org/upf_files/S.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Cl': 'https://pseudopotentials.quantum-espresso.org/upf_files/Cl.pbe-n-kjpaw_psl.1.0.0.UPF',
            'K': 'https://pseudopotentials.quantum-espresso.org/upf_files/K.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Ca': 'https://pseudopotentials.quantum-espresso.org/upf_files/Ca.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Sc': 'https://pseudopotentials.quantum-espresso.org/upf_files/Sc.pbesol-spn-kjpaw_psl.1.0.0.UPF',
            'Ti': 'https://pseudopotentials.quantum-espresso.org/upf_files/Ti.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'V': 'https://pseudopotentials.quantum-espresso.org/upf_files/V.rel-pbe-spnl-kjpaw_psl.1.0.0.UPF',
            'Cr': 'https://pseudopotentials.quantum-espresso.org/upf_files/Cr.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Mn': 'https://pseudopotentials.quantum-espresso.org/upf_files/Mn.pbesol-spn-kjpaw_psl.0.3.1.UPF',
            'Fe': 'https://pseudopotentials.quantum-espresso.org/upf_files/Fe.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Co': 'https://pseudopotentials.quantum-espresso.org/upf_files/Co.pbe-spn-kjpaw_psl.0.3.1.UPF',
            'Ni': 'https://pseudopotentials.quantum-espresso.org/upf_files/Ni.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Cu': 'https://pseudopotentials.quantum-espresso.org/upf_files/Cu.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'Zn': 'https://pseudopotentials.quantum-espresso.org/upf_files/Zn.pbe-dnl-kjpaw_psl.1.0.0.UPF',
            'Ga': 'https://pseudopotentials.quantum-espresso.org/upf_files/Ga.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'Ge': 'https://pseudopotentials.quantum-espresso.org/upf_files/Ge.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'As': 'https://pseudopotentials.quantum-espresso.org/upf_files/As.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Se': 'https://pseudopotentials.quantum-espresso.org/upf_files/Se.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'Br': 'https://pseudopotentials.quantum-espresso.org/upf_files/Br.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'Rb': 'https://pseudopotentials.quantum-espresso.org/upf_files/Rb.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Sr': 'https://pseudopotentials.quantum-espresso.org/upf_files/Sr.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Y': 'https://pseudopotentials.quantum-espresso.org/upf_files/Y.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Zr': 'https://pseudopotentials.quantum-espresso.org/upf_files/Zr.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Nb': 'https://pseudopotentials.quantum-espresso.org/upf_files/Nb.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Mo': 'https://pseudopotentials.quantum-espresso.org/upf_files/Mo.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Tc': 'https://pseudopotentials.quantum-espresso.org/upf_files/Tc.pbe-spn-kjpaw_psl.0.3.0.UPF',
            'Ru': 'https://pseudopotentials.quantum-espresso.org/upf_files/Ru.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Rh': 'https://pseudopotentials.quantum-espresso.org/upf_files/Rh.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Pd': 'https://pseudopotentials.quantum-espresso.org/upf_files/Pd.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Ag': 'https://pseudopotentials.quantum-espresso.org/upf_files/Ag.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Cd': 'https://pseudopotentials.quantum-espresso.org/upf_files/Cd.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Ta': 'https://pseudopotentials.quantum-espresso.org/upf_files/Ta.pbe-spnl-kjpaw_psl.1.0.0.UPF',
            'Ir': 'https://pseudopotentials.quantum-espresso.org/upf_files/Ir.pbe-spnl-kjpaw_psl.1.0.0.UPF',
            'In': 'https://pseudopotentials.quantum-espresso.org/upf_files/In.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'Sn': 'https://pseudopotentials.quantum-espresso.org/upf_files/Sn.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'Sb': 'https://pseudopotentials.quantum-espresso.org/upf_files/Sb.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Te': 'https://pseudopotentials.quantum-espresso.org/upf_files/Te.pbe-n-kjpaw_psl.1.0.0.UPF',
            'I': 'https://pseudopotentials.quantum-espresso.org/upf_files/I.pbe-n-kjpaw_psl.1.0.0.UPF',
            'W': 'https://pseudopotentials.quantum-espresso.org/upf_files/W.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Re': 'https://pseudopotentials.quantum-espresso.org/upf_files/Re.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Pt': 'https://pseudopotentials.quantum-espresso.org/upf_files/Pt.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Au': 'https://pseudopotentials.quantum-espresso.org/upf_files/Au.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Hg': 'https://pseudopotentials.quantum-espresso.org/upf_files/Hg.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Pb': 'https://pseudopotentials.quantum-espresso.org/upf_files/Pb.pbe-dn-kjpaw_psl.1.0.0.UPF'
        }
        
    def add_material_requirements(self, material_name, elements):
        """Add pseudopotential requirements for a material"""
        self.required_pseudos[material_name] = elements
        
    def scan_available_pseudos(self):
        """Scan the pseudopotential directory for available files"""
        if not self.pseudo_dir.exists():
            print(f"❌ Pseudopotential directory not found: {self.pseudo_dir}")
            return False
            
        print(f"📁 Scanning pseudopotential directory: {self.pseudo_dir}")
        
        # Common pseudopotential file extensions
        extensions = ['.UPF', '.upf', '.psp8', '.psf']
        
        for ext in extensions:
            for pseudo_file in self.pseudo_dir.glob(f"*{ext}"):
                # Extract element symbol from filename
                filename = pseudo_file.name
                element = filename.split('.')[0].split('_')[0]
                
                if element not in self.available_pseudos:
                    self.available_pseudos[element] = []
                self.available_pseudos[element].append(filename)
        
        print(f"✅ Found pseudopotentials for {len(self.available_pseudos)} elements")
        return True
    
    def check_requirements(self):
        """Check if all required pseudopotentials are available"""
        all_available = True
        
        print("\n🔍 Checking pseudopotential requirements...")
        print("=" * 60)
        
        for material, elements in self.required_pseudos.items():
            print(f"\n📋 Material: {material}")
            material_complete = True
            
            for element, suggested_pseudo in elements.items():
                if element in self.available_pseudos:
                    available_files = self.available_pseudos[element]
                    
                    # Check if suggested pseudopotential is available
                    if suggested_pseudo in available_files:
                        print(f"  ✅ {element}: {suggested_pseudo} (suggested)")
                    else:
                        print(f"  ⚠️  {element}: {suggested_pseudo} (suggested, NOT FOUND)")
                        print(f"      Available alternatives: {', '.join(available_files)}")
                        self.missing_pseudos.append((material, element, suggested_pseudo))
                        
                else:
                    print(f"  ❌ {element}: No pseudopotentials found")
                    material_complete = False
                    all_available = False
                    self.missing_pseudos.append((material, element, suggested_pseudo))
            
            if material_complete:
                print(f"  🎉 {material}: All pseudopotentials available")
            else:
                print(f"  ⚠️  {material}: Missing some pseudopotentials")
        
        return all_available
    
    def generate_pseudopotential_dict(self, material_name):
        """Generate a pseudopotential dictionary for ASE calculations"""
        if material_name not in self.required_pseudos:
            return None
            
        pseudo_dict = {}
        elements = self.required_pseudos[material_name]
        
        for element, suggested_pseudo in elements.items():
            if element in self.available_pseudos:
                if suggested_pseudo in self.available_pseudos[element]:
                    pseudo_dict[element] = suggested_pseudo
                else:
                    # Use first available alternative
                    pseudo_dict[element] = self.available_pseudos[element][0]
                    print(f"⚠️  Using {self.available_pseudos[element][0]} instead of {suggested_pseudo} for {element}")
            else:
                print(f"❌ Cannot find any pseudopotential for {element}")
                return None
        
        return pseudo_dict
    
    def list_all_available(self):
        """List all available pseudopotentials"""
        print("\n📚 All Available Pseudopotentials:")
        print("=" * 60)
        
        for element in sorted(self.available_pseudos.keys()):
            files = self.available_pseudos[element]
            print(f"{element:>3}: {', '.join(files)}")
    
    def download_pseudopotential(self, element, custom_url=None):
        """Download a pseudopotential for the given element"""
        if custom_url:
            url = custom_url
            filename = custom_url.split('/')[-1]
        elif element in self.pslibrary_urls:
            url = self.pslibrary_urls[element]
            filename = url.split('/')[-1]
        else:
            print(f"❌ No URL available for {element}")
            print(f"Please visit https://pseudopotentials.quantum-espresso.org/legacy_tables")
            print(f"and find the pseudopotential for {element}, then paste the URL")
            custom_url = input(f"Enter URL for {element} pseudopotential: ").strip()
            if custom_url:
                return self.download_pseudopotential(element, custom_url)
            else:
                return False
        
        # Create pseudo directory if it doesn't exist
        self.pseudo_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = self.pseudo_dir / filename
        
        # Check if file already exists
        if target_path.exists():
            print(f"✅ {filename} already exists")
            return True
        
        try:
            print(f"📥 Downloading {filename}...")
            with urllib.request.urlopen(url) as response:
                content = response.read()
                
            with open(target_path, 'wb') as f:
                f.write(content)
                
            print(f"✅ Successfully downloaded {filename}")
            return True
            
        except urllib.error.URLError as e:
            print(f"❌ Failed to download {filename}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")
            return False
    
    def download_missing_pseudopotentials(self, interactive=True):
        """Download all missing pseudopotentials"""
        if not self.missing_pseudos:
            print("✅ No missing pseudopotentials to download")
            return True
        
        print(f"\n📥 PSEUDOPOTENTIAL DOWNLOAD")
        print("=" * 50)
        
        if interactive:
            print(f"Found {len(self.missing_pseudos)} missing pseudopotentials:")
            for material, element, suggested_pseudo in self.missing_pseudos:
                print(f"  - {element} (needed for {material})")
            
            download_all = input("\nDownload all missing pseudopotentials? (Y/n): ").strip().lower()
            if download_all in ['n', 'no']:
                return False
        
        success_count = 0
        total_count = len(set(element for _, element, _ in self.missing_pseudos))
        downloaded_elements = set()
        
        for material, element, suggested_pseudo in self.missing_pseudos:
            if element in downloaded_elements:
                continue  # Already downloaded this element
                
            print(f"\n🔍 Processing {element}...")
            
            if self.download_pseudopotential(element):
                success_count += 1
                downloaded_elements.add(element)
            else:
                print(f"⚠️  Failed to download pseudopotential for {element}")
        
        print(f"\n📊 Download Summary:")
        print(f"  Successfully downloaded: {success_count}/{total_count}")
        
        if success_count > 0:
            print("\n🔄 Rescanning pseudopotential directory...")
            self.scan_available_pseudos()
            
        return success_count == total_count
    
    def auto_fix_pseudopotentials(self):
        """Automatically fix missing pseudopotentials by downloading them"""
        print("\n🛠️  AUTO-FIX MISSING PSEUDOPOTENTIALS")
        print("=" * 50)
        
        # First check what's missing
        all_available = self.check_requirements()
        
        if all_available:
            print("✅ All pseudopotentials are already available!")
            return True
        
        # Try to download missing ones
        download_success = self.download_missing_pseudopotentials(interactive=False)
        
        if download_success:
            # Re-check after download
            self.missing_pseudos = []  # Reset the list
            all_available = self.check_requirements()
            
            if all_available:
                print("\n🎉 All missing pseudopotentials have been downloaded!")
                return True
            else:
                print("\n⚠️  Some pseudopotentials are still missing after download")
                return False
        else:
            print("\n❌ Failed to download some pseudopotentials")
            return False
    
    def suggest_alternatives(self):
        """Suggest alternative pseudopotentials for missing ones"""
        if not self.missing_pseudos:
            return
            
        print("\n💡 Suggestions for Missing Pseudopotentials:")
        print("=" * 60)
        
        for material, element, missing_pseudo in self.missing_pseudos:
            if element in self.available_pseudos:
                alternatives = self.available_pseudos[element]
                print(f"{material} - {element}:")
                print(f"  Missing: {missing_pseudo}")
                print(f"  Available: {', '.join(alternatives)}")
                print()


def main():
    """Main function to check pseudopotentials for MoS2 calculations"""
    
    import argparse
    parser = argparse.ArgumentParser(description='Check and download pseudopotentials for MoS2 calculations')
    parser.add_argument('--list-all', action='store_true', help='List all available pseudopotentials')
    parser.add_argument('--download', action='store_true', help='Download missing pseudopotentials')
    parser.add_argument('--auto-fix', action='store_true', help='Automatically download all missing pseudopotentials')
    parser.add_argument('--element', type=str, help='Download pseudopotential for specific element')
    parser.add_argument('--url', type=str, help='Custom URL for pseudopotential download')
    
    args = parser.parse_args()
    
    checker = PseudopotentialChecker()
    
    # Define materials and their pseudopotential requirements
    # Based on comprehensive adsorbant library for MoS2 testing
    
    # MoS2 slab base
    checker.add_material_requirements("MoS2_slab", {
        'Mo': 'Mo.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'S': 'S.pbe-n-kjpaw_psl.1.0.0.UPF'
    })
    
    # Metal dimers on MoS2
    checker.add_material_requirements("metal_dimers_on_MoS2", {
        'Mo': 'Mo.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'S': 'S.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Au': 'Au.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Ag': 'Ag.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Pt': 'Pt.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Pd': 'Pd.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Cu': 'Cu.pbe-dn-kjpaw_psl.1.0.0.UPF',
        'Fe': 'Fe.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'Co': 'Co.pbe-spn-kjpaw_psl.0.3.1.UPF',
        'Ni': 'Ni.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'Mn': 'Mn.pbesol-spn-kjpaw_psl.0.3.1.UPF',
        'Ir': 'Ir.pbe-spnl-kjpaw_psl.1.0.0.UPF',
        'Rh': 'Rh.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'Re': 'Re.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'Ru': 'Ru.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'Cd': 'Cd.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Al': 'Al.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Zn': 'Zn.pbe-dnl-kjpaw_psl.1.0.0.UPF',
        'Nb': 'Nb.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'W': 'W.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'Ta': 'Ta.pbe-spnl-kjpaw_psl.1.0.0.UPF',
        'V': 'V.rel-pbe-spnl-kjpaw_psl.1.0.0.UPF',
        'C': 'C.pbe-n-kjpaw_psl.1.0.0.UPF'
    })
    
    # Light elements on MoS2
    checker.add_material_requirements("light_elements_on_MoS2", {
        'Mo': 'Mo.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'S': 'S.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Li': 'Li.pbe-s-kjpaw_psl.1.0.0.UPF',
        'Na': 'Na.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'P': 'P.pbe-n-kjpaw_psl.1.0.0.UPF',
        'N': 'N.pbe-n-kjpaw_psl.1.0.0.UPF',
        'B': 'B.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Si': 'Si.pbe-n-kjpaw_psl.1.0.0.UPF',
        'F': 'F.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Cl': 'Cl.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Se': 'Se.pbe-dn-kjpaw_psl.1.0.0.UPF',
        'Te': 'Te.pbe-n-kjpaw_psl.1.0.0.UPF',
        'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF'
    })
    
    # Metal oxides on MoS2
    checker.add_material_requirements("metal_oxides_on_MoS2", {
        'Mo': 'Mo.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'S': 'S.pbe-n-kjpaw_psl.1.0.0.UPF',
        'Zn': 'Zn.pbe-dnl-kjpaw_psl.1.0.0.UPF',
        'Ti': 'Ti.pbe-spn-kjpaw_psl.1.0.0.UPF',
        'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF'
    })
    
    print("🔬 MoS2 Energy Profile Calculations - Pseudopotential Checker")
    print("=" * 60)
    
    # Handle specific element download
    if args.element:
        print(f"📥 Downloading pseudopotential for {args.element}...")
        success = checker.download_pseudopotential(args.element, args.url)
        sys.exit(0 if success else 1)
    
    # Scan for available pseudopotentials
    if not checker.scan_available_pseudos():
        print("❌ Failed to scan pseudopotential directory")
        sys.exit(1)
    
    # Auto-fix mode
    if args.auto_fix:
        success = checker.auto_fix_pseudopotentials()
        sys.exit(0 if success else 1)
    
    # Check requirements
    all_available = checker.check_requirements()
    
    # Handle download mode
    if args.download:
        if not all_available:
            checker.download_missing_pseudopotentials()
        else:
            print("✅ All pseudopotentials already available!")
    
    # List alternatives for missing pseudopotentials
    checker.suggest_alternatives()
    
    # Generate example pseudopotential dictionaries
    print("\n🐍 Python Pseudopotential Dictionaries:")
    print("=" * 60)
    
    for material_name in checker.required_pseudos.keys():
        pseudo_dict = checker.generate_pseudopotential_dict(material_name)
        if pseudo_dict:
            print(f"\n# {material_name}")
            print("pseudopotentials = {")
            for element, pseudo_file in pseudo_dict.items():
                print(f"    '{element}': '{pseudo_file}',")
            print("}")
    
    # Optional: List all available pseudopotentials
    if args.list_all:
        checker.list_all_available()
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  Materials checked: {len(checker.required_pseudos)}")
    print(f"  Elements with available pseudopotentials: {len(checker.available_pseudos)}")
    print(f"  Missing pseudopotentials: {len(checker.missing_pseudos)}")
    
    if not all_available and not args.download:
        print(f"\n💡 Quick Fix Options:")
        print(f"  python {sys.argv[0]} --download     # Interactive download")
        print(f"  python {sys.argv[0]} --auto-fix     # Automatic download")
    
    if all_available:
        print("\n🎉 All required pseudopotentials are available!")
        print("You can proceed with DFT calculations.")
        sys.exit(0)
    else:
        if args.download or args.auto_fix:
            print(f"\n⚠️  Some pseudopotentials are still missing.")
        else:
            print(f"\n⚠️  Some pseudopotentials are missing.")
            print("Use --download or --auto-fix to download them automatically.")
        sys.exit(1)


if __name__ == "__main__":
    main()
