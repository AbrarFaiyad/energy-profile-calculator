#!/usr/bin/env python3
"""
Simple Pseudopotential Downloader

A lightweight utility to download pseudopotentials from PSLibrary.
Usage: python download_pseudo.py <element1> <element2> ...
"""

import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# PSLibrary URLs
PSLIBRARY_URLS = {
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
    'Mo': 'https://pseudopotentials.quantum-espresso.org/upf_files/Mo.pbe-spn-kjpaw_psl.1.0.0.UPF',
    'Ru': 'https://pseudopotentials.quantum-espresso.org/upf_files/Ru.pbe-spn-kjpaw_psl.1.0.0.UPF',
    'Rh': 'https://pseudopotentials.quantum-espresso.org/upf_files/Rh.pbe-spn-kjpaw_psl.1.0.0.UPF',
    'Pd': 'https://pseudopotentials.quantum-espresso.org/upf_files/Pd.pbe-n-kjpaw_psl.1.0.0.UPF',
    'Ag': 'https://pseudopotentials.quantum-espresso.org/upf_files/Ag.pbe-n-kjpaw_psl.1.0.0.UPF',
    'Sb': 'https://pseudopotentials.quantum-espresso.org/upf_files/Sb.pbe-n-kjpaw_psl.1.0.0.UPF',
    'W': 'https://pseudopotentials.quantum-espresso.org/upf_files/W.pbe-spn-kjpaw_psl.1.0.0.UPF',
    'Re': 'https://pseudopotentials.quantum-espresso.org/upf_files/Re.pbe-spn-kjpaw_psl.1.0.0.UPF',
    'Pt': 'https://pseudopotentials.quantum-espresso.org/upf_files/Pt.pbe-n-kjpaw_psl.1.0.0.UPF',
    'Au': 'https://pseudopotentials.quantum-espresso.org/upf_files/Au.pbe-n-kjpaw_psl.1.0.0.UPF'
}

def download_pseudopotential(element, target_dir="/home/afaiyad/QE/qe-7.4.1/pseudo"):
    """Download pseudopotential for a given element"""
    if element not in PSLIBRARY_URLS:
        print(f"❌ No URL available for {element}")
        print(f"Available elements: {', '.join(sorted(PSLIBRARY_URLS.keys()))}")
        print(f"For other elements, visit: https://pseudopotentials.quantum-espresso.org/legacy_tables")
        return False
    
    url = PSLIBRARY_URLS[element]
    filename = url.split('/')[-1]
    
    # Create directory if it doesn't exist
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    file_path = target_path / filename
    
    # Check if file already exists
    if file_path.exists():
        print(f"✅ {filename} already exists in {target_dir}")
        return True
    
    try:
        print(f"📥 Downloading {element} pseudopotential...")
        print(f"   URL: {url}")
        print(f"   Target: {file_path}")
        
        with urllib.request.urlopen(url) as response:
            content = response.read()
            
        with open(file_path, 'wb') as f:
            f.write(content)
            
        print(f"✅ Successfully downloaded {filename}")
        return True
        
    except urllib.error.URLError as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error downloading {filename}: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Download pseudopotentials from PSLibrary',
        epilog='Example: python download_pseudo.py H O Mo S'
    )
    parser.add_argument('elements', nargs='*', help='Element symbols to download')
    parser.add_argument('--dir', default='/home/afaiyad/QE/qe-7.4.1/pseudo',
                       help='Target directory (default: /home/afaiyad/QE/qe-7.4.1/pseudo)')
    parser.add_argument('--list', action='store_true', help='List available elements')
    parser.add_argument('--all', action='store_true', help='Download all available pseudopotentials')
    
    args = parser.parse_args()
    
    if args.list:
        print("📚 Available elements in PSLibrary:")
        elements = sorted(PSLIBRARY_URLS.keys())
        for i, elem in enumerate(elements):
            if i % 10 == 0:
                print()
            print(f"{elem:>3}", end=" ")
        print(f"\n\nTotal: {len(elements)} elements")
        return
    
    if args.all:
        print("📥 Downloading ALL available pseudopotentials...")
        elements = sorted(PSLIBRARY_URLS.keys())
    elif args.elements:
        elements = args.elements
    else:
        print("❌ No elements specified!")
        print("Usage: python download_pseudo.py <element1> <element2> ...")
        print("       python download_pseudo.py --list")
        print("       python download_pseudo.py --all")
        sys.exit(1)
    
    print(f"🎯 Target directory: {args.dir}")
    print(f"📋 Elements to download: {', '.join(elements)}")
    print("-" * 50)
    
    success_count = 0
    total_count = len(elements)
    
    for element in elements:
        if download_pseudopotential(element, args.dir):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"📊 Download Summary:")
    print(f"   Successful: {success_count}/{total_count}")
    print(f"   Failed: {total_count - success_count}")
    
    if success_count == total_count:
        print("🎉 All downloads completed successfully!")
        sys.exit(0)
    else:
        print("⚠️  Some downloads failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
