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
        
        # 2D layered materials support
        self._layered_materials = {
            'MoS2': {'metal': 'Mo', 'chalcogen': 'S', 'metal_coord': 'trigonal_prismatic'},
            'WS2': {'metal': 'W', 'chalcogen': 'S', 'metal_coord': 'trigonal_prismatic'},
            'MoSe2': {'metal': 'Mo', 'chalcogen': 'Se', 'metal_coord': 'trigonal_prismatic'},
            'WSe2': {'metal': 'W', 'chalcogen': 'Se', 'metal_coord': 'trigonal_prismatic'},
            'MoTe2': {'metal': 'Mo', 'chalcogen': 'Te', 'metal_coord': 'trigonal_prismatic'},
            'WTe2': {'metal': 'W', 'chalcogen': 'Te', 'metal_coord': 'trigonal_prismatic'},
            'TiS2': {'metal': 'Ti', 'chalcogen': 'S', 'metal_coord': 'octahedral'},
            'TiSe2': {'metal': 'Ti', 'chalcogen': 'Se', 'metal_coord': 'octahedral'},
            'ZrS2': {'metal': 'Zr', 'chalcogen': 'S', 'metal_coord': 'trigonal_prismatic'},
            'HfS2': {'metal': 'Hf', 'chalcogen': 'S', 'metal_coord': 'trigonal_prismatic'},
            'NbS2': {'metal': 'Nb', 'chalcogen': 'S', 'metal_coord': 'trigonal_prismatic'},
            'TaS2': {'metal': 'Ta', 'chalcogen': 'S', 'metal_coord': 'trigonal_prismatic'},
            'ReS2': {'metal': 'Re', 'chalcogen': 'S', 'metal_coord': 'distorted_octahedral'},
            'PtS2': {'metal': 'Pt', 'chalcogen': 'S', 'metal_coord': 'octahedral'},
            'PdS2': {'metal': 'Pd', 'chalcogen': 'S', 'metal_coord': 'square_planar'},
            'SnS2': {'metal': 'Sn', 'chalcogen': 'S', 'metal_coord': 'octahedral'},
            'GeS2': {'metal': 'Ge', 'chalcogen': 'S', 'metal_coord': 'tetrahedral'},
            'InSe': {'metal': 'In', 'chalcogen': 'Se', 'metal_coord': 'octahedral'},
            'GaS': {'metal': 'Ga', 'chalcogen': 'S', 'metal_coord': 'tetrahedral'},
            'GaSe': {'metal': 'Ga', 'chalcogen': 'Se', 'metal_coord': 'tetrahedral'},
            'graphene': {'metal': 'C', 'chalcogen': None, 'metal_coord': 'trigonal_planar'},
            'h-BN': {'metal': 'B', 'chalcogen': 'N', 'metal_coord': 'trigonal_planar'},
            'silicene': {'metal': 'Si', 'chalcogen': None, 'metal_coord': 'buckled'},
            'germanene': {'metal': 'Ge', 'chalcogen': None, 'metal_coord': 'buckled'},
            'phosphorene': {'metal': 'P', 'chalcogen': None, 'metal_coord': 'puckered'},
            'arsenene': {'metal': 'As', 'chalcogen': None, 'metal_coord': 'puckered'}
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
    
    def list_2d_materials(self) -> List[str]:
        """Get list of supported 2D layered materials."""
        return list(self._layered_materials.keys())
    
    def get_2d_material_info(self, material: str) -> Dict[str, Any]:
        """Get information about a 2D material."""
        if material not in self._layered_materials:
            raise ValueError(f"2D material '{material}' not supported.")
        return self._layered_materials[material].copy()
    
    def build_2d_material(self, material: str, size: Tuple[int, int], 
                         vacuum: float = 15.0, layers: int = 1) -> Atoms:
        """
        Build a 2D layered material surface.
        
        Args:
            material: Name of the 2D material (e.g., 'MoS2', 'graphene', 'h-BN')
            size: Size of the surface unit cell (nx, ny)
            vacuum: Vacuum space above and below the material (Å)
            layers: Number of layers to stack
            
        Returns:
            Atoms object representing the 2D material
        """
        if material not in self._layered_materials:
            available = list(self._layered_materials.keys())
            raise ValueError(f"2D material '{material}' not supported. Available: {available}")
        
        mat_info = self._layered_materials[material]
        
        if material == 'graphene':
            surface = self._build_graphene(size, vacuum, layers)
        elif material == 'h-BN':
            surface = self._build_hexagonal_bn(size, vacuum, layers)
        elif material in ['silicene', 'germanene']:
            surface = self._build_buckled_honeycomb(material, size, vacuum, layers)
        elif material in ['phosphorene', 'arsenene']:
            surface = self._build_puckered_layer(material, size, vacuum, layers)
        elif mat_info['chalcogen'] is not None:
            # Transition metal dichalcogenides
            surface = self._build_tmd(material, size, vacuum, layers)
        else:
            raise ValueError(f"Building method not implemented for {material}")
        
        return surface
    
    def _build_graphene(self, size: Tuple[int, int], vacuum: float, layers: int) -> Atoms:
        """Build graphene structure."""
        a = 2.46  # Lattice parameter in Å
        c_c = 1.42  # C-C bond length
        
        # Hexagonal unit cell
        cell = [[a, 0, 0], 
                [-a/2, a*np.sqrt(3)/2, 0], 
                [0, 0, vacuum + layers * 3.35]]
        
        # Carbon positions in unit cell
        positions = []
        elements = []
        
        for layer in range(layers):
            z_offset = layer * 3.35  # Interlayer spacing
            # Two carbon atoms per unit cell
            pos1 = [0, 0, z_offset + vacuum/2]
            pos2 = [a/3, a/(3*np.sqrt(3)), z_offset + vacuum/2]
            
            for nx in range(size[0]):
                for ny in range(size[1]):
                    # Replicate unit cell
                    shift = np.array([nx*a, ny*a*np.sqrt(3)/2, 0])
                    positions.append(pos1 + shift)
                    positions.append(pos2 + shift)
                    elements.extend(['C', 'C'])
        
        # Adjust cell size for supercell
        supercell = [[size[0]*a, 0, 0],
                    [-size[0]*a/2, size[1]*a*np.sqrt(3)/2, 0],
                    [0, 0, vacuum + layers * 3.35]]
        
        atoms = Atoms(symbols=elements, positions=positions, cell=supercell, pbc=[True, True, True])
        return atoms
    
    def _build_hexagonal_bn(self, size: Tuple[int, int], vacuum: float, layers: int) -> Atoms:
        """Build hexagonal boron nitride structure."""
        a = 2.50  # Lattice parameter in Å
        
        # Similar to graphene but with B and N alternating
        cell = [[a, 0, 0], 
                [-a/2, a*np.sqrt(3)/2, 0], 
                [0, 0, vacuum + layers * 3.33]]
        
        positions = []
        elements = []
        
        for layer in range(layers):
            z_offset = layer * 3.33  # Interlayer spacing
            # B and N atoms per unit cell
            pos_b = [0, 0, z_offset + vacuum/2]
            pos_n = [a/3, a/(3*np.sqrt(3)), z_offset + vacuum/2]
            
            for nx in range(size[0]):
                for ny in range(size[1]):
                    shift = np.array([nx*a, ny*a*np.sqrt(3)/2, 0])
                    positions.append(pos_b + shift)
                    positions.append(pos_n + shift)
                    elements.extend(['B', 'N'])
        
        supercell = [[size[0]*a, 0, 0],
                    [-size[0]*a/2, size[1]*a*np.sqrt(3)/2, 0],
                    [0, 0, vacuum + layers * 3.33]]
        
        atoms = Atoms(symbols=elements, positions=positions, cell=supercell, pbc=[True, True, True])
        return atoms
    
    def _build_tmd(self, material: str, size: Tuple[int, int], vacuum: float, layers: int) -> Atoms:
        """Build transition metal dichalcogenide structure."""
        mat_info = self._layered_materials[material]
        metal = mat_info['metal']
        chalcogen = mat_info['chalcogen']
        
        # Lattice parameters (approximate values)
        lattice_params = {
            'MoS2': 3.16, 'WS2': 3.15, 'MoSe2': 3.29, 'WSe2': 3.28,
            'MoTe2': 3.52, 'WTe2': 3.50, 'TiS2': 3.37, 'TiSe2': 3.54,
            'ZrS2': 3.66, 'HfS2': 3.63, 'NbS2': 3.31, 'TaS2': 3.31,
            'ReS2': 3.14, 'PtS2': 3.54, 'PdS2': 3.61, 'SnS2': 3.65,
            'GeS2': 3.64, 'InSe': 4.05, 'GaS': 3.59, 'GaSe': 3.74
        }
        
        interlayer_spacing = {
            'MoS2': 6.15, 'WS2': 6.15, 'MoSe2': 6.46, 'WSe2': 6.48,
            'MoTe2': 6.97, 'WTe2': 7.05, 'TiS2': 5.69, 'TiSe2': 6.01,
            'ZrS2': 5.83, 'HfS2': 5.86, 'NbS2': 5.98, 'TaS2': 5.90,
            'ReS2': 6.18, 'PtS2': 5.04, 'PdS2': 5.05, 'SnS2': 5.90,
            'GeS2': 5.98, 'InSe': 8.32, 'GaS': 7.49, 'GaSe': 7.98
        }
        
        a = lattice_params.get(material, 3.20)
        c_layer = interlayer_spacing.get(material, 6.20)
        
        # Hexagonal unit cell
        cell = [[a, 0, 0], 
                [-a/2, a*np.sqrt(3)/2, 0], 
                [0, 0, vacuum + layers * c_layer]]
        
        positions = []
        elements = []
        
        for layer in range(layers):
            z_offset = layer * c_layer
            # TMD structure: chalcogen-metal-chalcogen sandwich
            # Metal at center, chalcogens above and below
            metal_z = z_offset + vacuum/2
            chalcogen1_z = metal_z + 1.56  # Approximate M-X distance
            chalcogen2_z = metal_z - 1.56
            
            for nx in range(size[0]):
                for ny in range(size[1]):
                    shift = np.array([nx*a, ny*a*np.sqrt(3)/2, 0])
                    
                    # Metal position
                    metal_pos = [0, 0, metal_z] + shift
                    positions.append(metal_pos)
                    elements.append(metal)
                    
                    # Chalcogen positions (2 per metal)
                    chalc1_pos = [a/3, a/(3*np.sqrt(3)), chalcogen1_z] + shift
                    chalc2_pos = [2*a/3, 2*a/(3*np.sqrt(3)), chalcogen2_z] + shift
                    positions.extend([chalc1_pos, chalc2_pos])
                    elements.extend([chalcogen, chalcogen])
        
        supercell = [[size[0]*a, 0, 0],
                    [-size[0]*a/2, size[1]*a*np.sqrt(3)/2, 0],
                    [0, 0, vacuum + layers * c_layer]]
        
        atoms = Atoms(symbols=elements, positions=positions, cell=supercell, pbc=[True, True, True])
        return atoms
    
    def _build_buckled_honeycomb(self, material: str, size: Tuple[int, int], 
                                vacuum: float, layers: int) -> Atoms:
        """Build buckled honeycomb structures like silicene, germanene."""
        lattice_params = {'silicene': 3.86, 'germanene': 4.02}
        buckling_heights = {'silicene': 0.44, 'germanene': 0.64}
        
        element = material.replace('ene', '').capitalize()
        a = lattice_params[material]
        buckling = buckling_heights[material]
        
        positions = []
        elements = []
        
        for layer in range(layers):
            z_offset = layer * 6.0  # Approximate interlayer spacing
            
            for nx in range(size[0]):
                for ny in range(size[1]):
                    shift = np.array([nx*a, ny*a*np.sqrt(3)/2, 0])
                    
                    # Two atoms per unit cell with different z-heights
                    pos1 = [0, 0, z_offset + vacuum/2 + buckling/2] + shift
                    pos2 = [a/3, a/(3*np.sqrt(3)), z_offset + vacuum/2 - buckling/2] + shift
                    positions.extend([pos1, pos2])
                    elements.extend([element, element])
        
        supercell = [[size[0]*a, 0, 0],
                    [-size[0]*a/2, size[1]*a*np.sqrt(3)/2, 0],
                    [0, 0, vacuum + layers * 6.0]]
        
        atoms = Atoms(symbols=elements, positions=positions, cell=supercell, pbc=[True, True, True])
        return atoms
    
    def _build_puckered_layer(self, material: str, size: Tuple[int, int], 
                             vacuum: float, layers: int) -> Atoms:
        """Build puckered layer structures like phosphorene, arsenene."""
        lattice_params = {'phosphorene': [4.38, 3.31], 'arsenene': [4.63, 3.60]}
        puckering_heights = {'phosphorene': 2.13, 'arsenene': 2.50}
        
        element = material.replace('ene', '').capitalize()
        if element == 'Phosphor':
            element = 'P'
        elif element == 'Arsen':
            element = 'As'
        
        a, b = lattice_params[material]
        puckering = puckering_heights[material]
        
        positions = []
        elements = []
        
        for layer in range(layers):
            z_offset = layer * 5.0  # Approximate interlayer spacing
            
            for nx in range(size[0]):
                for ny in range(size[1]):
                    shift_x = nx * a
                    shift_y = ny * b
                    
                    # Four atoms per unit cell in puckered arrangement
                    base_z = z_offset + vacuum/2
                    positions.extend([
                        [0 + shift_x, 0 + shift_y, base_z + puckering/2],
                        [a/2 + shift_x, 0 + shift_y, base_z - puckering/2],
                        [a/2 + shift_x, b/2 + shift_y, base_z + puckering/2],
                        [0 + shift_x, b/2 + shift_y, base_z - puckering/2]
                    ])
                    elements.extend([element] * 4)
        
        supercell = [[size[0]*a, 0, 0],
                    [0, size[1]*b, 0],
                    [0, 0, vacuum + layers * 5.0]]
        
        atoms = Atoms(symbols=elements, positions=positions, cell=supercell, pbc=[True, True, True])
        return atoms


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