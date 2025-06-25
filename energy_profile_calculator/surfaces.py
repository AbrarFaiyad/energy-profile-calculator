"""
Surface builder for creating different crystal surfaces.
"""

import numpy as np
from ase import Atoms
from ase.build import fcc111, fcc100, fcc110, bcc100, bcc110, bcc111, hcp0001
from typing import Tuple, List, Dict, Any, Optional


class SurfaceBuilder:
    """
    Builder class for creating different crystal surfaces.
    """
    
    def __init__(self):
        self._surface_builders = {
            'fcc': {
                (1, 1, 1): fcc111,
                (1, 0, 0): fcc100,
                (1, 1, 0): fcc110,
            },
            'bcc': {
                (1, 0, 0): bcc100,
                (1, 1, 0): bcc110,
                (1, 1, 1): bcc111,
            },
            'hcp': {
                (0, 0, 0, 1): hcp0001,
            }
        }
        
        # Common materials and their crystal structures
        self._material_structures = {
            'Au': 'fcc', 'Ag': 'fcc', 'Cu': 'fcc', 'Al': 'fcc', 'Ni': 'fcc',
            'Pd': 'fcc', 'Pt': 'fcc', 'Rh': 'fcc', 'Ir': 'fcc', 'Pb': 'fcc',
            'Fe': 'bcc', 'Cr': 'bcc', 'W': 'bcc', 'Mo': 'bcc', 'V': 'bcc',
            'Nb': 'bcc', 'Ta': 'bcc',
            'Zn': 'hcp', 'Cd': 'hcp', 'Ti': 'hcp', 'Zr': 'hcp', 'Mg': 'hcp',
            'Be': 'hcp', 'Co': 'hcp', 'Ru': 'hcp', 'Re': 'hcp'
        }
    
    def build_surface(self, material: str, miller_indices: Tuple[int, ...], 
                     size: Tuple[int, int, int], vacuum: float = 10.0,
                     crystal_structure: Optional[str] = None) -> Atoms:
        """
        Build a crystal surface.
        
        Args:
            material: Chemical symbol of the material
            miller_indices: Miller indices of the surface
            size: Size of the surface unit cell (nx, ny, nlayers)
            vacuum: Vacuum space above the surface (Å)
            crystal_structure: Override crystal structure ('fcc', 'bcc', 'hcp')
            
        Returns:
            Atoms object representing the surface
        """
        # Determine crystal structure
        if crystal_structure is None:
            if material not in self._material_structures:
                raise ValueError(f"Unknown material '{material}'. Please specify crystal_structure.")
            crystal_structure = self._material_structures[material]
        
        # Get appropriate builder function
        builder_func = self._get_builder_function(crystal_structure, miller_indices)
        
        # Build the surface
        if crystal_structure == 'hcp' and len(miller_indices) == 4:
            # HCP uses 4-index notation
            surface = builder_func(material, size=size, vacuum=vacuum)
        else:
            surface = builder_func(material, size=size, vacuum=vacuum)
        
        # Set periodic boundary conditions
        surface.pbc = [True, True, True]
        
        return surface
    
    def _get_builder_function(self, crystal_structure: str, miller_indices: Tuple[int, ...]):
        """Get the appropriate ASE builder function."""
        if crystal_structure not in self._surface_builders:
            raise ValueError(f"Unsupported crystal structure: {crystal_structure}")
        
        structure_builders = self._surface_builders[crystal_structure]
        
        if miller_indices not in structure_builders:
            available = list(structure_builders.keys())
            raise ValueError(f"Miller indices {miller_indices} not supported for {crystal_structure}. "
                           f"Available: {available}")
        
        return structure_builders[miller_indices]
    
    def get_surface_info(self, surface: Atoms) -> Dict[str, Any]:
        """
        Get information about a surface.
        
        Args:
            surface: Surface atoms object
            
        Returns:
            Dictionary with surface information
        """
        positions = surface.get_positions()
        z_coords = positions[:, 2]
        
        info = {
            'n_atoms': len(surface),
            'elements': list(set(surface.get_chemical_symbols())),
            'cell': surface.get_cell().tolist(),
            'z_min': z_coords.min(),
            'z_max': z_coords.max(),
            'z_range': z_coords.max() - z_coords.min(),
            'surface_area': self._calculate_surface_area(surface),
            'layers': self._identify_layers(surface)
        }
        
        return info
    
    def _calculate_surface_area(self, surface: Atoms) -> float:
        """Calculate surface area from unit cell vectors."""
        cell = surface.get_cell()
        # Cross product of first two cell vectors gives surface area
        cross_product = np.cross(cell[0], cell[1])
        area = np.linalg.norm(cross_product)
        return area
    
    def _identify_layers(self, surface: Atoms, tolerance: float = 0.1) -> List[Dict[str, Any]]:
        """
        Identify atomic layers in the surface.
        
        Args:
            surface: Surface atoms object
            tolerance: Tolerance for grouping atoms into layers (Å)
            
        Returns:
            List of layer information dictionaries
        """
        positions = surface.get_positions()
        z_coords = positions[:, 2]
        symbols = surface.get_chemical_symbols()
        
        # Sort by z-coordinate
        sorted_indices = np.argsort(z_coords)
        sorted_z = z_coords[sorted_indices]
        sorted_symbols = [symbols[i] for i in sorted_indices]
        
        layers = []
        current_layer = {'z_avg': sorted_z[0], 'atoms': [0], 'elements': [sorted_symbols[0]]}
        
        for i in range(1, len(sorted_z)):
            if abs(sorted_z[i] - current_layer['z_avg']) <= tolerance:
                # Same layer
                current_layer['atoms'].append(sorted_indices[i])
                current_layer['elements'].append(sorted_symbols[i])
                current_layer['z_avg'] = np.mean([sorted_z[j] for j in 
                                                range(len(current_layer['atoms']))])
            else:
                # New layer
                layers.append({
                    'layer_number': len(layers),
                    'z_average': current_layer['z_avg'],
                    'n_atoms': len(current_layer['atoms']),
                    'elements': list(set(current_layer['elements'])),
                    'atom_indices': current_layer['atoms']
                })
                
                current_layer = {
                    'z_avg': sorted_z[i], 
                    'atoms': [sorted_indices[i]], 
                    'elements': [sorted_symbols[i]]
                }
        
        # Add the last layer
        layers.append({
            'layer_number': len(layers),
            'z_average': current_layer['z_avg'],
            'n_atoms': len(current_layer['atoms']),
            'elements': list(set(current_layer['elements'])),
            'atom_indices': current_layer['atoms']
        })
        
        return layers
    
    def get_adsorption_sites(self, surface: Atoms, site_types: List[str] = None) -> Dict[str, List[Tuple[float, float, float]]]:
        """
        Generate high-symmetry adsorption sites on the surface.
        
        Args:
            surface: Surface atoms object
            site_types: Types of sites to generate ('top', 'bridge', 'hollow')
            
        Returns:
            Dictionary mapping site types to lists of (x, y, z) coordinates
        """
        if site_types is None:
            site_types = ['top', 'bridge', 'hollow']
        
        positions = surface.get_positions()
        cell = surface.get_cell()
        z_max = positions[:, 2].max()
        
        # Get surface atoms (top layer)
        z_coords = positions[:, 2]
        tolerance = 0.5
        surface_mask = (z_coords >= z_max - tolerance)
        surface_positions = positions[surface_mask]
        
        sites = {}
        
        if 'top' in site_types:
            # Top sites: directly above surface atoms
            top_sites = []
            for pos in surface_positions:
                top_sites.append((pos[0], pos[1], z_max + 2.0))  # 2 Å above surface
            sites['top'] = top_sites
        
        if 'bridge' in site_types:
            # Bridge sites: midpoints between nearest neighbor surface atoms
            bridge_sites = []
            for i, pos1 in enumerate(surface_positions):
                for j, pos2 in enumerate(surface_positions[i+1:], i+1):
                    dist = np.linalg.norm(pos1[:2] - pos2[:2])  # 2D distance
                    if 2.0 < dist < 4.0:  # Reasonable neighbor distance
                        bridge_pos = (pos1 + pos2) / 2
                        bridge_sites.append((bridge_pos[0], bridge_pos[1], z_max + 2.0))
            sites['bridge'] = bridge_sites
        
        if 'hollow' in site_types:
            # Hollow sites: center of triangles formed by surface atoms
            hollow_sites = []
            for i, pos1 in enumerate(surface_positions):
                for j, pos2 in enumerate(surface_positions[i+1:], i+1):
                    for k, pos3 in enumerate(surface_positions[j+1:], j+1):
                        # Check if these form a reasonable triangle
                        d12 = np.linalg.norm(pos1[:2] - pos2[:2])
                        d13 = np.linalg.norm(pos1[:2] - pos3[:2])
                        d23 = np.linalg.norm(pos2[:2] - pos3[:2])
                        
                        if all(2.0 < d < 5.0 for d in [d12, d13, d23]):
                            center = (pos1 + pos2 + pos3) / 3
                            hollow_sites.append((center[0], center[1], z_max + 2.0))
            sites['hollow'] = hollow_sites
        
        return sites
    
    def list_supported_materials(self) -> Dict[str, List[str]]:
        """Get list of supported materials by crystal structure."""
        supported = {}
        for material, structure in self._material_structures.items():
            if structure not in supported:
                supported[structure] = []
            supported[structure].append(material)
        
        return supported
    
    def list_supported_surfaces(self, crystal_structure: str) -> List[Tuple[int, ...]]:
        """Get list of supported Miller indices for a crystal structure."""
        if crystal_structure not in self._surface_builders:
            raise ValueError(f"Unsupported crystal structure: {crystal_structure}")
        
        return list(self._surface_builders[crystal_structure].keys())


def create_custom_surface(positions: List[Tuple[float, float, float]], 
                         elements: List[str], 
                         cell: List[List[float]],
                         vacuum: float = 10.0) -> Atoms:
    """
    Create a custom surface from atomic positions.
    
    Args:
        positions: List of (x, y, z) coordinates
        elements: List of element symbols
        cell: Unit cell vectors as 3x3 matrix
        vacuum: Additional vacuum space (Å)
        
    Returns:
        Atoms object representing the custom surface
    """
    if len(positions) != len(elements):
        raise ValueError("Number of positions must match number of elements")
    
    atoms = Atoms(symbols=elements, positions=positions, cell=cell, pbc=[True, True, True])
    
    # Add vacuum
    cell_array = np.array(cell)
    cell_array[2, 2] += vacuum
    atoms.set_cell(cell_array)
    
    return atoms
