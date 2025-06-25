"""
Adsorbant library with predefined molecular structures and properties.
"""

import numpy as np
from ase import Atoms, Atom
from typing import Dict, List, Tuple, Optional, Any


class AdsorbantLibrary:
    """
    Library of predefined adsorbant molecules with their geometries and properties.
    """
    
    def __init__(self):
        self._adsorbants = self._initialize_adsorbants()
    
    def _initialize_adsorbants(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the adsorbant library with predefined molecules."""
        return {
            'H2O': {
                'description': 'Water molecule',
                'elements': ['O', 'H', 'H'],
                'geometry': self._water_geometry,
                'orientations': ['flat', 'vertical'],
                'charge': 0,
                'multiplicity': 1
            },
            'H2': {
                'description': 'Hydrogen molecule',
                'elements': ['H', 'H'],
                'geometry': self._h2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 1
            },
            'O2': {
                'description': 'Oxygen molecule',
                'elements': ['O', 'O'],
                'geometry': self._o2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 3
            },
            'N2': {
                'description': 'Nitrogen molecule',
                'elements': ['N', 'N'],
                'geometry': self._n2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 1
            },
            'CO': {
                'description': 'Carbon monoxide',
                'elements': ['C', 'O'],
                'geometry': self._co_geometry,
                'orientations': ['parallel', 'perpendicular', 'c_down', 'o_down'],
                'charge': 0,
                'multiplicity': 1
            },
            'CO2': {
                'description': 'Carbon dioxide',
                'elements': ['C', 'O', 'O'],
                'geometry': self._co2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 1
            },
            'NH3': {
                'description': 'Ammonia',
                'elements': ['N', 'H', 'H', 'H'],
                'geometry': self._nh3_geometry,
                'orientations': ['n_down', 'n_up'],
                'charge': 0,
                'multiplicity': 1
            },
            'CH4': {
                'description': 'Methane',
                'elements': ['C', 'H', 'H', 'H', 'H'],
                'geometry': self._ch4_geometry,
                'orientations': ['tetrahedral'],
                'charge': 0,
                'multiplicity': 1
            },
            'H': {
                'description': 'Hydrogen atom',
                'elements': ['H'],
                'geometry': self._h_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 2
            },
            'O': {
                'description': 'Oxygen atom',
                'elements': ['O'],
                'geometry': self._o_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 3
            },
            'C': {
                'description': 'Carbon atom',
                'elements': ['C'],
                'geometry': self._c_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 3
            },
            'N': {
                'description': 'Nitrogen atom',
                'elements': ['N'],
                'geometry': self._n_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 4
            },
            'F': {
                'description': 'Fluorine atom',
                'elements': ['F'],
                'geometry': self._f_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 2
            },
            'Na': {
                'description': 'Sodium atom',
                'elements': ['Na'],
                'geometry': self._na_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 2
            }
        }
    
    def get_adsorbant(self, name: str, position: Tuple[float, float, float], 
                     orientation: str = 'default') -> Atoms:
        """
        Create an adsorbant molecule at the specified position.
        
        Args:
            name: Name of the adsorbant
            position: (x, y, z) coordinates for the primary atom
            orientation: Molecular orientation
            
        Returns:
            Atoms object containing the adsorbant molecule
        """
        if name not in self._adsorbants:
            raise ValueError(f"Adsorbant '{name}' not found in library. "
                           f"Available: {list(self._adsorbants.keys())}")
        
        adsorbant_info = self._adsorbants[name]
        
        if orientation not in adsorbant_info['orientations']:
            raise ValueError(f"Orientation '{orientation}' not available for {name}. "
                           f"Available: {adsorbant_info['orientations']}")
        
        geometry_func = adsorbant_info['geometry']
        return geometry_func(position, orientation)
    
    def list_adsorbants(self) -> List[str]:
        """Get list of available adsorbants."""
        return list(self._adsorbants.keys())
    
    def get_info(self, name: str) -> Dict[str, Any]:
        """Get information about an adsorbant."""
        if name not in self._adsorbants:
            raise ValueError(f"Adsorbant '{name}' not found in library.")
        return self._adsorbants[name].copy()
    
    def get_elements(self, name: str) -> List[str]:
        """Get the elements in an adsorbant."""
        if name not in self._adsorbants:
            raise ValueError(f"Adsorbant '{name}' not found in library.")
        return self._adsorbants[name]['elements']
    
    # Geometry functions for different molecules
    
    def _water_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create water molecule geometry."""
        x, y, z = position
        O_H_distance = 0.96  # Å
        H_O_H_angle = 104.5  # degrees
        angle_rad = np.radians(H_O_H_angle / 2)
        
        if orientation == 'flat':
            h1_pos = [x + O_H_distance * np.cos(angle_rad), 
                      y + O_H_distance * np.sin(angle_rad), z]
            h2_pos = [x + O_H_distance * np.cos(angle_rad), 
                      y - O_H_distance * np.sin(angle_rad), z]
        elif orientation == 'vertical':
            h1_pos = [x + O_H_distance * np.cos(angle_rad), y, 
                      z + O_H_distance * np.sin(angle_rad)]
            h2_pos = [x + O_H_distance * np.cos(angle_rad), y, 
                      z - O_H_distance * np.sin(angle_rad)]
        
        return Atoms([Atom('O', position), Atom('H', h1_pos), Atom('H', h2_pos)])
    
    def _h2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create H2 molecule geometry."""
        x, y, z = position
        bond_length = 0.74  # Å
        
        if orientation == 'parallel':
            h1_pos = [x - bond_length/2, y, z]
            h2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            h1_pos = [x, y, z - bond_length/2]
            h2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('H', h1_pos), Atom('H', h2_pos)])
    
    def _o2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create O2 molecule geometry."""
        x, y, z = position
        bond_length = 1.21  # Å
        
        if orientation == 'parallel':
            o1_pos = [x - bond_length/2, y, z]
            o2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            o1_pos = [x, y, z - bond_length/2]
            o2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('O', o1_pos), Atom('O', o2_pos)])
    
    def _n2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create N2 molecule geometry."""
        x, y, z = position
        bond_length = 1.10  # Å
        
        if orientation == 'parallel':
            n1_pos = [x - bond_length/2, y, z]
            n2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            n1_pos = [x, y, z - bond_length/2]
            n2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('N', n1_pos), Atom('N', n2_pos)])
    
    def _co_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create CO molecule geometry."""
        x, y, z = position
        bond_length = 1.13  # Å
        
        if orientation == 'parallel':
            c_pos = [x - bond_length/2, y, z]
            o_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            c_pos = [x, y, z - bond_length/2]
            o_pos = [x, y, z + bond_length/2]
        elif orientation == 'c_down':
            c_pos = [x, y, z]
            o_pos = [x, y, z + bond_length]
        elif orientation == 'o_down':
            o_pos = [x, y, z]
            c_pos = [x, y, z + bond_length]
        
        return Atoms([Atom('C', c_pos), Atom('O', o_pos)])
    
    def _co2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create CO2 molecule geometry."""
        x, y, z = position
        bond_length = 1.16  # Å
        
        if orientation == 'parallel':
            c_pos = [x, y, z]
            o1_pos = [x - bond_length, y, z]
            o2_pos = [x + bond_length, y, z]
        elif orientation == 'perpendicular':
            c_pos = [x, y, z]
            o1_pos = [x, y, z - bond_length]
            o2_pos = [x, y, z + bond_length]
        
        return Atoms([Atom('C', c_pos), Atom('O', o1_pos), Atom('O', o2_pos)])
    
    def _nh3_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create NH3 molecule geometry."""
        x, y, z = position
        bond_length = 1.01  # Å
        bond_angle = 106.8  # degrees
        angle_rad = np.radians(bond_angle)
        
        if orientation == 'n_down':
            n_pos = [x, y, z]
            h1_pos = [x + bond_length * np.sin(angle_rad), y, z + bond_length * np.cos(angle_rad)]
            h2_pos = [x - bond_length * np.sin(angle_rad/2), y + bond_length * np.cos(angle_rad/2), 
                      z + bond_length * np.cos(angle_rad)]
            h3_pos = [x - bond_length * np.sin(angle_rad/2), y - bond_length * np.cos(angle_rad/2), 
                      z + bond_length * np.cos(angle_rad)]
        elif orientation == 'n_up':
            n_pos = [x, y, z]
            h1_pos = [x + bond_length * np.sin(angle_rad), y, z - bond_length * np.cos(angle_rad)]
            h2_pos = [x - bond_length * np.sin(angle_rad/2), y + bond_length * np.cos(angle_rad/2), 
                      z - bond_length * np.cos(angle_rad)]
            h3_pos = [x - bond_length * np.sin(angle_rad/2), y - bond_length * np.cos(angle_rad/2), 
                      z - bond_length * np.cos(angle_rad)]
        
        return Atoms([Atom('N', n_pos), Atom('H', h1_pos), Atom('H', h2_pos), Atom('H', h3_pos)])
    
    def _ch4_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create CH4 molecule geometry."""
        x, y, z = position
        bond_length = 1.09  # Å
        
        # Tetrahedral geometry
        c_pos = [x, y, z]
        
        # Tetrahedral coordinates
        h1_pos = [x + bond_length * 0.577, y + bond_length * 0.577, z + bond_length * 0.577]
        h2_pos = [x - bond_length * 0.577, y - bond_length * 0.577, z + bond_length * 0.577]
        h3_pos = [x - bond_length * 0.577, y + bond_length * 0.577, z - bond_length * 0.577]
        h4_pos = [x + bond_length * 0.577, y - bond_length * 0.577, z - bond_length * 0.577]
        
        return Atoms([Atom('C', c_pos), Atom('H', h1_pos), Atom('H', h2_pos), 
                      Atom('H', h3_pos), Atom('H', h4_pos)])
    
    # Atomic adsorbants
    def _h_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create H atom."""
        return Atoms([Atom('H', position)])
    
    def _o_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create O atom."""
        return Atoms([Atom('O', position)])
    
    def _c_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create C atom."""
        return Atoms([Atom('C', position)])
    
    def _n_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create N atom."""
        return Atoms([Atom('N', position)])
    
    def _f_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create F atom."""
        return Atoms([Atom('F', position)])
    
    def _na_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Na atom."""
        return Atoms([Atom('Na', position)])


def create_custom_adsorbant(elements: List[str], positions: List[Tuple[float, float, float]], 
                           center_position: Tuple[float, float, float]) -> Atoms:
    """
    Create a custom adsorbant molecule.
    
    Args:
        elements: List of element symbols
        positions: List of relative positions for each atom
        center_position: Center position to place the molecule
        
    Returns:
        Atoms object containing the custom adsorbant
    """
    if len(elements) != len(positions):
        raise ValueError("Number of elements must match number of positions")
    
    cx, cy, cz = center_position
    atoms = []
    
    for element, (dx, dy, dz) in zip(elements, positions):
        abs_position = [cx + dx, cy + dy, cz + dz]
        atoms.append(Atom(element, abs_position))
    
    return Atoms(atoms)
