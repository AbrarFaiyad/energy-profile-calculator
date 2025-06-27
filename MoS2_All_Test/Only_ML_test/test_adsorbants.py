#!/usr/bin/env python3
"""
Test script to verify all requested adsorbants are available
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from energy_profile_calculator.adsorbants import AdsorbantLibrary
    from energy_profile_calculator.surfaces import SurfaceBuilder
    
    print("🔬 Testing MoS2 Adsorbant Availability")
    print("=" * 60)
    
    # Initialize libraries
    lib = AdsorbantLibrary()
    surface_builder = SurfaceBuilder()
    
    # List of requested adsorbants
    requested_adsorbants = [
        # Metal dimers
        'Au2', 'Ag2', 'Pt2', 'Pd2', 'Cu2', 'Fe2', 'Co2', 'Ni2', 'Mn2', 
        'Ir2', 'Rh2', 'Re2', 'Ru2', 'Cd2', 'Al2', 'Zn2', 'Nb2', 'W2', 
        'Ta2', 'V2', 'C2',
        
        # Single atoms
        'Li', 'Na', 'P', 'N', 'B', 'Si', 'F', 'Cl', 'S', 'Se', 'Te', 'O',
        
        # Organic molecules
        'F4TCNQ', 'PTCDA', 'tetracene', 'TCNQ', 'TCNE', 'TTF', 'BV',
        
        # Metal oxides
        'ZnO', 'TiO2'
    ]
    
    print(f"📋 Testing {len(requested_adsorbants)} adsorbants...")
    print("-" * 60)
    
    available = []
    missing = []
    
    for adsorbant in requested_adsorbants:
        try:
            info = lib.get_info(adsorbant)
            print(f"✅ {adsorbant:10}: {info['description']}")
            available.append(adsorbant)
        except Exception as e:
            print(f"❌ {adsorbant:10}: Not available - {e}")
            missing.append(adsorbant)
    
    print("-" * 60)
    print(f"📊 Summary:")
    print(f"  Available: {len(available)}/{len(requested_adsorbants)}")
    print(f"  Missing: {len(missing)}")
    
    if missing:
        print(f"\n⚠️  Missing adsorbants:")
        for m in missing:
            print(f"    - {m}")
    
    # Test MoS2 surface
    print(f"\n🔬 Testing MoS2 surface...")
    try:
        mos2_info = surface_builder.get_2d_material_info('MoS2')
        print(f"✅ MoS2: 2D transition metal dichalcogenide")
        print(f"   Metal: {mos2_info['metal']}")
        print(f"   Chalcogen: {mos2_info['chalcogen']}")
        print(f"   Coordination: {mos2_info['metal_coord']}")
    except Exception as e:
        print(f"❌ MoS2: Not available - {e}")
    
    # Test creating a sample structure
    print(f"\n🧪 Testing sample structure creation...")
    try:
        # Test Au2 on MoS2
        slab = surface_builder.build_2d_material('MoS2', size=(3, 3), vacuum=14.0)
        adsorbant = lib.get_adsorbant('Au2', (0, 0, 5.0), 'parallel')
        print(f"✅ Created MoS2 slab: {len(slab)} atoms")
        print(f"✅ Created Au2 adsorbant: {len(adsorbant)} atoms")
        
        # Combine them
        combined = slab + adsorbant
        print(f"✅ Combined system: {len(combined)} atoms")
        
    except Exception as e:
        print(f"❌ Structure creation failed: {e}")
    
    print(f"\n🎉 Testing completed!")
    
    if len(available) == len(requested_adsorbants):
        print("✅ All requested adsorbants are available!")
        sys.exit(0)
    else:
        print(f"⚠️  {len(missing)} adsorbants are missing from the library")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and the energy_profile_calculator package is available")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
