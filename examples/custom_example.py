"""
Example: Creating custom adsorbants and surfaces
"""

from energy_profile_calculator import EnergyProfileCalculator
from energy_profile_calculator.adsorbants import create_custom_adsorbant
from energy_profile_calculator.surfaces import create_custom_surface
import numpy as np

def main():
    # Initialize calculator
    calc = EnergyProfileCalculator()
    
    # Example 1: Custom surface (4x4 Au supercell)
    print("Creating custom Au surface...")
    
    # Define larger Au(111) surface manually
    a = 4.08  # Au lattice parameter (Å)
    
    # Generate 4x4x3 Au(111) positions
    positions = []
    elements = []
    
    for layer in range(3):
        z = layer * a / np.sqrt(3) * 2  # (111) layer spacing
        for i in range(4):
            for j in range(4):
                # FCC (111) positions
                x = i * a / np.sqrt(2)
                y = j * a / np.sqrt(2) + (i % 2) * a / (2 * np.sqrt(2))
                positions.append([x, y, z])
                elements.append('Au')
    
    # Create custom surface
    cell = [[4*a/np.sqrt(2), 0, 0], 
            [0, 4*a/np.sqrt(2), 0], 
            [0, 0, 20]]  # 20 Å total height with vacuum
    
    custom_surface = create_custom_surface(
        positions=positions,
        elements=elements,
        cell=cell,
        vacuum=10.0
    )
    
    # Use custom surface
    calc.surface = custom_surface
    calc.surface_name = "Au(111)-4x4"
    
    print(f"Custom surface created with {len(custom_surface)} atoms")
    
    # Example 2: Custom adsorbant (formic acid HCOOH)
    print("Creating custom adsorbant (formic acid)...")
    
    # Define HCOOH geometry (simplified)
    formic_elements = ['H', 'C', 'O', 'O', 'H']
    formic_positions = [
        (-1.1, 0.0, 0.0),    # H
        (0.0, 0.0, 0.0),     # C (center)
        (1.2, 0.0, 0.0),     # O
        (0.0, 1.3, 0.0),     # O
        (0.0, 2.0, 0.0)      # H
    ]
    
    # Setup ML calculators
    print("Setting up ML calculators...")
    calc.setup_calculators(
        use_ml=True,
        use_dft=False,
        ml_model='uma-s-1',
        ml_device='cuda'
    )
    
    # Calculate custom adsorbant energy profile
    print("Calculating custom adsorbant energy profile...")
    
    heights = np.arange(2.0, 6.0, 0.5)  # Shorter range for demo
    z_top = custom_surface.positions[:, 2].max()
    
    # Center position
    center_x = custom_surface.cell[0, 0] / 2
    center_y = custom_surface.cell[1, 1] / 2
    
    omat_energies = []
    omc_energies = []
    
    for height in heights:
        print(f"Height: {height:.1f} Å")
        
        # Create system with custom adsorbant
        system = custom_surface.copy()
        
        # Add custom adsorbant
        adsorbant_pos = (center_x, center_y, z_top + height)
        custom_adsorbant = create_custom_adsorbant(
            elements=formic_elements,
            positions=formic_positions,
            center_position=adsorbant_pos
        )
        
        for atom in custom_adsorbant:
            system.append(atom)
        
        # Calculate energies
        omat_energy = calc.calculator_factory.get_ml_manager().calculate_energy(system, 'omat')
        omc_energy = calc.calculator_factory.get_ml_manager().calculate_energy(system, 'omc')
        
        omat_energies.append(omat_energy)
        omc_energies.append(omc_energy)
        
        # Save structure
        from ase.io import write
        write(f'custom_structure_h{height:.1f}.xyz', system)
    
    # Normalize energies
    omat_energies = np.array(omat_energies) - omat_energies[-1]
    omc_energies = np.array(omc_energies) - omc_energies[-1]
    
    # Create simple plot
    create_custom_plot(heights, omat_energies, omc_energies)
    
    # Print results
    print("\n" + "="*50)
    print("CUSTOM CALCULATION RESULTS")
    print("="*50)
    print(f"Surface: Custom Au(111)-4x4")
    print(f"Adsorbant: Custom HCOOH")
    
    omat_min_idx = np.argmin(omat_energies)
    omc_min_idx = np.argmin(omc_energies)
    
    print(f"\nOMAT results:")
    print(f"  Binding energy: {-omat_energies[omat_min_idx]:.4f} eV")
    print(f"  Optimal height: {heights[omat_min_idx]:.1f} Å")
    
    print(f"\nOMC results:")
    print(f"  Binding energy: {-omc_energies[omc_min_idx]:.4f} eV")
    print(f"  Optimal height: {heights[omc_min_idx]:.1f} Å")

def create_custom_plot(heights, omat_energies, omc_energies):
    """Create a simple plot for custom calculation."""
    try:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        plt.plot(heights, omat_energies, 'o-', label='OMAT', linewidth=2, markersize=8)
        plt.plot(heights, omc_energies, 's-', label='OMC', linewidth=2, markersize=8)
        
        plt.xlabel('Height above surface (Å)', fontsize=12)
        plt.ylabel('Energy (eV)', fontsize=12)
        plt.title('Custom HCOOH on Au(111)-4x4 Energy Profile', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig('custom_calculation.png', dpi=300, bbox_inches='tight')
        print("Plot saved as: custom_calculation.png")
        
    except ImportError:
        print("Matplotlib not available, skipping plot")

if __name__ == '__main__':
    main()
