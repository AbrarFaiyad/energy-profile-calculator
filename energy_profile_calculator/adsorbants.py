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
            },
            # Metal clusters
            'Na2': {
                'description': 'Sodium dimer',
                'elements': ['Na', 'Na'],
                'geometry': self._na2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 1
            },
            'Au2': {
                'description': 'Gold dimer',
                'elements': ['Au', 'Au'],
                'geometry': self._au2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 1
            },
            'Au3': {
                'description': 'Gold trimer',
                'elements': ['Au', 'Au', 'Au'],
                'geometry': self._au3_geometry,
                'orientations': ['triangular', 'linear'],
                'charge': 0,
                'multiplicity': 2
            },
            'Ti2': {
                'description': 'Titanium dimer',
                'elements': ['Ti', 'Ti'],
                'geometry': self._ti2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 3
            },
            'Cr2': {
                'description': 'Chromium dimer',
                'elements': ['Cr', 'Cr'],
                'geometry': self._cr2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 1
            },
            'Fe2': {
                'description': 'Iron dimer',
                'elements': ['Fe', 'Fe'],
                'geometry': self._fe2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 9
            },
            'Co2': {
                'description': 'Cobalt dimer',
                'elements': ['Co', 'Co'],
                'geometry': self._co2_dimer_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 7
            },
            'Ni2': {
                'description': 'Nickel dimer',
                'elements': ['Ni', 'Ni'],
                'geometry': self._ni2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 5
            },
            'Cu2': {
                'description': 'Copper dimer',
                'elements': ['Cu', 'Cu'],
                'geometry': self._cu2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 1
            },
            'Pt2': {
                'description': 'Platinum dimer',
                'elements': ['Pt', 'Pt'],
                'geometry': self._pt2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 3
            },
            'Pd2': {
                'description': 'Palladium dimer',
                'elements': ['Pd', 'Pd'],
                'geometry': self._pd2_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 3
            },
            # Inorganic molecules
            'Sb2O3': {
                'description': 'Antimony trioxide',
                'elements': ['Sb', 'Sb', 'O', 'O', 'O'],
                'geometry': self._sb2o3_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 1
            },
            'P4': {
                'description': 'White phosphorus (tetrahedral)',
                'elements': ['P', 'P', 'P', 'P'],
                'geometry': self._p4_geometry,
                'orientations': ['tetrahedral'],
                'charge': 0,
                'multiplicity': 1
            },
            'B2H6': {
                'description': 'Diborane',
                'elements': ['B', 'B', 'H', 'H', 'H', 'H', 'H', 'H'],
                'geometry': self._b2h6_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 1
            },
            'SiH4': {
                'description': 'Silane',
                'elements': ['Si', 'H', 'H', 'H', 'H'],
                'geometry': self._sih4_geometry,
                'orientations': ['tetrahedral'],
                'charge': 0,
                'multiplicity': 1
            },
            'HF': {
                'description': 'Hydrogen fluoride',
                'elements': ['H', 'F'],
                'geometry': self._hf_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 1
            },
            'HCl': {
                'description': 'Hydrogen chloride',
                'elements': ['H', 'Cl'],
                'geometry': self._hcl_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 1
            },
            'H2S': {
                'description': 'Hydrogen sulfide',
                'elements': ['H', 'H', 'S'],
                'geometry': self._h2s_geometry,
                'orientations': ['bent'],
                'charge': 0,
                'multiplicity': 1
            },
            'SO2': {
                'description': 'Sulfur dioxide',
                'elements': ['S', 'O', 'O'],
                'geometry': self._so2_geometry,
                'orientations': ['bent'],
                'charge': 0,
                'multiplicity': 1
            },
            'TeF6': {
                'description': 'Tellurium hexafluoride',
                'elements': ['Te', 'F', 'F', 'F', 'F', 'F', 'F'],
                'geometry': self._tef6_geometry,
                'orientations': ['octahedral'],
                'charge': 0,
                'multiplicity': 1
            },
            # Metal oxides
            'ZnO': {
                'description': 'Zinc oxide unit',
                'elements': ['Zn', 'O'],
                'geometry': self._zno_geometry,
                'orientations': ['parallel', 'perpendicular'],
                'charge': 0,
                'multiplicity': 1
            },
            'TiO2': {
                'description': 'Titanium dioxide unit',
                'elements': ['Ti', 'O', 'O'],
                'geometry': self._tio2_geometry,
                'orientations': ['linear', 'bent'],
                'charge': 0,
                'multiplicity': 1
            },
            # Individual atoms for completeness
            'Ti': {
                'description': 'Titanium atom',
                'elements': ['Ti'],
                'geometry': self._ti_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 3
            },
            'Cr': {
                'description': 'Chromium atom',
                'elements': ['Cr'],
                'geometry': self._cr_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 7
            },
            'Ta': {
                'description': 'Tantalum atom',
                'elements': ['Ta'],
                'geometry': self._ta_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 4
            },
            'Pd': {
                'description': 'Palladium atom',
                'elements': ['Pd'],
                'geometry': self._pd_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 1
            },
            'V': {
                'description': 'Vanadium atom',
                'elements': ['V'],
                'geometry': self._v_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 4
            },
            'Pt': {
                'description': 'Platinum atom',
                'elements': ['Pt'],
                'geometry': self._pt_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 3
            },
            'Ag': {
                'description': 'Silver atom',
                'elements': ['Ag'],
                'geometry': self._ag_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 2
            },
            'Re': {
                'description': 'Rhenium atom',
                'elements': ['Re'],
                'geometry': self._re_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 6
            },
            'Ru': {
                'description': 'Ruthenium atom',
                'elements': ['Ru'],
                'geometry': self._ru_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 5
            },
            'Cd': {
                'description': 'Cadmium atom',
                'elements': ['Cd'],
                'geometry': self._cd_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 1
            },
            'Fe': {
                'description': 'Iron atom',
                'elements': ['Fe'],
                'geometry': self._fe_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 5
            },
            'Co': {
                'description': 'Cobalt atom',
                'elements': ['Co'],
                'geometry': self._co_atom_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 4
            },
            'Ni': {
                'description': 'Nickel atom',
                'elements': ['Ni'],
                'geometry': self._ni_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 3
            },
            'Mn': {
                'description': 'Manganese atom',
                'elements': ['Mn'],
                'geometry': self._mn_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 6
            },
            'Ir': {
                'description': 'Iridium atom',
                'elements': ['Ir'],
                'geometry': self._ir_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 4
            },
            'Rh': {
                'description': 'Rhodium atom',
                'elements': ['Rh'],
                'geometry': self._rh_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 4
            },
            'Cu': {
                'description': 'Copper atom',
                'elements': ['Cu'],
                'geometry': self._cu_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 2
            },
            'Al': {
                'description': 'Aluminum atom',
                'elements': ['Al'],
                'geometry': self._al_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 2
            },
            'Zn': {
                'description': 'Zinc atom',
                'elements': ['Zn'],
                'geometry': self._zn_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 1
            },
            'Nb': {
                'description': 'Niobium atom',
                'elements': ['Nb'],
                'geometry': self._nb_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 6
            },
            'W': {
                'description': 'Tungsten atom',
                'elements': ['W'],
                'geometry': self._w_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 5
            },
            'Li': {
                'description': 'Lithium atom',
                'elements': ['Li'],
                'geometry': self._li_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 2
            },
            'Au': {
                'description': 'Gold atom',
                'elements': ['Au'],
                'geometry': self._au_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 2
            },
            'P': {
                'description': 'Phosphorus atom',
                'elements': ['P'],
                'geometry': self._p_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 4
            },
            'B': {
                'description': 'Boron atom',
                'elements': ['B'],
                'geometry': self._b_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 2
            },
            'Si': {
                'description': 'Silicon atom',
                'elements': ['Si'],
                'geometry': self._si_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 3
            },
            'Cl': {
                'description': 'Chlorine atom',
                'elements': ['Cl'],
                'geometry': self._cl_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 2
            },
            'S': {
                'description': 'Sulfur atom',
                'elements': ['S'],
                'geometry': self._s_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 3
            },
            'Se': {
                'description': 'Selenium atom',
                'elements': ['Se'],
                'geometry': self._se_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 3
            },
            'Te': {
                'description': 'Tellurium atom',
                'elements': ['Te'],
                'geometry': self._te_geometry,
                'orientations': ['default'],
                'charge': 0,
                'multiplicity': 3
            },
            # Complex organic molecules
            'F4TCNQ': {
                'description': '2,3,5,6-tetrafluoro-7,7,8,8-tetracyanoquinodimethane',
                'elements': ['C']*12 + ['N']*4 + ['F']*4,
                'geometry': self._f4tcnq_geometry,
                'orientations': ['flat', 'vertical'],
                'charge': 0,
                'multiplicity': 1
            },
            'PTCDA': {
                'description': 'Perylene-3,4,9,10-tetracarboxylic dianhydride',
                'elements': ['C']*24 + ['O']*6,
                'geometry': self._ptcda_geometry,
                'orientations': ['flat', 'vertical'],
                'charge': 0,
                'multiplicity': 1
            },
            'tetracene': {
                'description': 'Tetracene',
                'elements': ['C']*18 + ['H']*12,
                'geometry': self._tetracene_geometry,
                'orientations': ['flat', 'vertical'],
                'charge': 0,
                'multiplicity': 1
            },
            'TCNQ': {
                'description': 'Tetracyanoquinodimethane',
                'elements': ['C']*12 + ['N']*4,
                'geometry': self._tcnq_geometry,
                'orientations': ['flat', 'vertical'],
                'charge': 0,
                'multiplicity': 1
            },
            'TCNE': {
                'description': 'Tetracyanoethylene',
                'elements': ['C']*6 + ['N']*4,
                'geometry': self._tcne_geometry,
                'orientations': ['flat', 'vertical'],
                'charge': 0,
                'multiplicity': 1
            },
            'TTF': {
                'description': 'Tetrathiafulvalene',
                'elements': ['C']*6 + ['S']*4 + ['H']*4,
                'geometry': self._ttf_geometry,
                'orientations': ['flat', 'vertical'],
                'charge': 0,
                'multiplicity': 1
            },
            'benzyl_viologen': {
                'description': 'Benzyl viologen',
                'elements': ['C']*19 + ['N']*2 + ['H']*18,
                'geometry': self._benzyl_viologen_geometry,
                'orientations': ['flat', 'vertical'],
                'charge': 2,
                'multiplicity': 1
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


    # Metal cluster geometries
    def _na2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Na2 dimer."""
        x, y, z = position
        bond_length = 3.08  # Å
        
        if orientation == 'parallel':
            na1_pos = [x - bond_length/2, y, z]
            na2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            na1_pos = [x, y, z - bond_length/2]
            na2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('Na', na1_pos), Atom('Na', na2_pos)])
    
    def _au2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Au2 dimer."""
        x, y, z = position
        bond_length = 2.47  # Å
        
        if orientation == 'parallel':
            au1_pos = [x - bond_length/2, y, z]
            au2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            au1_pos = [x, y, z - bond_length/2]
            au2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('Au', au1_pos), Atom('Au', au2_pos)])
    
    def _au3_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Au3 trimer."""
        x, y, z = position
        bond_length = 2.47  # Å
        
        if orientation == 'triangular':
            # Equilateral triangle
            au1_pos = [x, y, z]
            au2_pos = [x + bond_length, y, z]
            au3_pos = [x + bond_length/2, y + bond_length*np.sqrt(3)/2, z]
        elif orientation == 'linear':
            au1_pos = [x - bond_length, y, z]
            au2_pos = [x, y, z]
            au3_pos = [x + bond_length, y, z]
        
        return Atoms([Atom('Au', au1_pos), Atom('Au', au2_pos), Atom('Au', au3_pos)])
    
    def _ti2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Ti2 dimer."""
        x, y, z = position
        bond_length = 1.95  # Å
        
        if orientation == 'parallel':
            ti1_pos = [x - bond_length/2, y, z]
            ti2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            ti1_pos = [x, y, z - bond_length/2]
            ti2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('Ti', ti1_pos), Atom('Ti', ti2_pos)])
    
    def _cr2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Cr2 dimer."""
        x, y, z = position
        bond_length = 1.68  # Å
        
        if orientation == 'parallel':
            cr1_pos = [x - bond_length/2, y, z]
            cr2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            cr1_pos = [x, y, z - bond_length/2]
            cr2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('Cr', cr1_pos), Atom('Cr', cr2_pos)])
    
    def _fe2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Fe2 dimer."""
        x, y, z = position
        bond_length = 2.02  # Å
        
        if orientation == 'parallel':
            fe1_pos = [x - bond_length/2, y, z]
            fe2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            fe1_pos = [x, y, z - bond_length/2]
            fe2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('Fe', fe1_pos), Atom('Fe', fe2_pos)])
    
    def _co2_dimer_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Co2 dimer."""
        x, y, z = position
        bond_length = 1.89  # Å
        
        if orientation == 'parallel':
            co1_pos = [x - bond_length/2, y, z]
            co2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            co1_pos = [x, y, z - bond_length/2]
            co2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('Co', co1_pos), Atom('Co', co2_pos)])
    
    def _ni2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Ni2 dimer."""
        x, y, z = position
        bond_length = 2.16  # Å
        
        if orientation == 'parallel':
            ni1_pos = [x - bond_length/2, y, z]
            ni2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            ni1_pos = [x, y, z - bond_length/2]
            ni2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('Ni', ni1_pos), Atom('Ni', ni2_pos)])
    
    def _cu2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Cu2 dimer."""
        x, y, z = position
        bond_length = 2.22  # Å
        
        if orientation == 'parallel':
            cu1_pos = [x - bond_length/2, y, z]
            cu2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            cu1_pos = [x, y, z - bond_length/2]
            cu2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('Cu', cu1_pos), Atom('Cu', cu2_pos)])
    
    def _pt2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Pt2 dimer."""
        x, y, z = position
        bond_length = 2.33  # Å
        
        if orientation == 'parallel':
            pt1_pos = [x - bond_length/2, y, z]
            pt2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            pt1_pos = [x, y, z - bond_length/2]
            pt2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('Pt', pt1_pos), Atom('Pt', pt2_pos)])
    
    def _pd2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Pd2 dimer."""
        x, y, z = position
        bond_length = 2.52  # Å
        
        if orientation == 'parallel':
            pd1_pos = [x - bond_length/2, y, z]
            pd2_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            pd1_pos = [x, y, z - bond_length/2]
            pd2_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('Pd', pd1_pos), Atom('Pd', pd2_pos)])
    
    # Inorganic molecule geometries
    def _sb2o3_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Sb2O3 molecule."""
        x, y, z = position
        # Simplified structure - actual Sb2O3 has complex polymorphs
        sb_o_distance = 1.98  # Å
        
        sb1_pos = [x - 1.0, y, z]
        sb2_pos = [x + 1.0, y, z]
        o1_pos = [x, y, z + sb_o_distance]
        o2_pos = [x - 1.5, y + 1.0, z - 0.5]
        o3_pos = [x + 1.5, y - 1.0, z - 0.5]
        
        return Atoms([Atom('Sb', sb1_pos), Atom('Sb', sb2_pos), 
                      Atom('O', o1_pos), Atom('O', o2_pos), Atom('O', o3_pos)])
    
    def _p4_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create P4 tetrahedral molecule."""
        x, y, z = position
        edge_length = 2.21  # Å
        
        # Tetrahedral coordinates
        h = edge_length * np.sqrt(2/3)  # Height of tetrahedron
        p1_pos = [x, y, z + h/2]
        p2_pos = [x + edge_length/2, y - edge_length/(2*np.sqrt(3)), z - h/6]
        p3_pos = [x - edge_length/2, y - edge_length/(2*np.sqrt(3)), z - h/6]
        p4_pos = [x, y + edge_length/np.sqrt(3), z - h/6]
        
        return Atoms([Atom('P', p1_pos), Atom('P', p2_pos), 
                      Atom('P', p3_pos), Atom('P', p4_pos)])
    
    def _b2h6_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create B2H6 (diborane) molecule."""
        x, y, z = position
        b_b_distance = 1.77  # Å
        b_h_bridge = 1.33  # Å
        b_h_terminal = 1.19  # Å
        
        # Two boron atoms
        b1_pos = [x - b_b_distance/2, y, z]
        b2_pos = [x + b_b_distance/2, y, z]
        
        # Bridge hydrogens
        h_bridge1_pos = [x, y + 0.5, z + b_h_bridge]
        h_bridge2_pos = [x, y - 0.5, z + b_h_bridge]
        
        # Terminal hydrogens
        h_term1_pos = [x - b_b_distance/2 - 0.8, y + 0.8, z - 0.5]
        h_term2_pos = [x - b_b_distance/2 - 0.8, y - 0.8, z - 0.5]
        h_term3_pos = [x + b_b_distance/2 + 0.8, y + 0.8, z - 0.5]
        h_term4_pos = [x + b_b_distance/2 + 0.8, y - 0.8, z - 0.5]
        
        return Atoms([Atom('B', b1_pos), Atom('B', b2_pos),
                      Atom('H', h_bridge1_pos), Atom('H', h_bridge2_pos),
                      Atom('H', h_term1_pos), Atom('H', h_term2_pos),
                      Atom('H', h_term3_pos), Atom('H', h_term4_pos)])
    
    def _sih4_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create SiH4 (silane) molecule."""
        x, y, z = position
        bond_length = 1.48  # Å
        
        # Silicon at center
        si_pos = [x, y, z]
        
        # Tetrahedral hydrogens
        h1_pos = [x + bond_length * 0.577, y + bond_length * 0.577, z + bond_length * 0.577]
        h2_pos = [x - bond_length * 0.577, y - bond_length * 0.577, z + bond_length * 0.577]
        h3_pos = [x - bond_length * 0.577, y + bond_length * 0.577, z - bond_length * 0.577]
        h4_pos = [x + bond_length * 0.577, y - bond_length * 0.577, z - bond_length * 0.577]
        
        return Atoms([Atom('Si', si_pos), Atom('H', h1_pos), Atom('H', h2_pos),
                      Atom('H', h3_pos), Atom('H', h4_pos)])
    
    def _hf_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create HF molecule."""
        x, y, z = position
        bond_length = 0.92  # Å
        
        if orientation == 'parallel':
            h_pos = [x - bond_length/2, y, z]
            f_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            h_pos = [x, y, z - bond_length/2]
            f_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('H', h_pos), Atom('F', f_pos)])
    
    def _hcl_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create HCl molecule."""
        x, y, z = position
        bond_length = 1.27  # Å
        
        if orientation == 'parallel':
            h_pos = [x - bond_length/2, y, z]
            cl_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            h_pos = [x, y, z - bond_length/2]
            cl_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('H', h_pos), Atom('Cl', cl_pos)])
    
    def _h2s_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create H2S molecule."""
        x, y, z = position
        s_h_distance = 1.34  # Å
        h_s_h_angle = 92.1  # degrees
        angle_rad = np.radians(h_s_h_angle / 2)
        
        s_pos = [x, y, z]
        h1_pos = [x + s_h_distance * np.cos(angle_rad), 
                  y + s_h_distance * np.sin(angle_rad), z]
        h2_pos = [x + s_h_distance * np.cos(angle_rad), 
                  y - s_h_distance * np.sin(angle_rad), z]
        
        return Atoms([Atom('S', s_pos), Atom('H', h1_pos), Atom('H', h2_pos)])
    
    def _so2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create SO2 molecule."""
        x, y, z = position
        s_o_distance = 1.49  # Å
        o_s_o_angle = 119.3  # degrees
        angle_rad = np.radians(o_s_o_angle / 2)
        
        s_pos = [x, y, z]
        o1_pos = [x + s_o_distance * np.cos(angle_rad), 
                  y + s_o_distance * np.sin(angle_rad), z]
        o2_pos = [x + s_o_distance * np.cos(angle_rad), 
                  y - s_o_distance * np.sin(angle_rad), z]
        
        return Atoms([Atom('S', s_pos), Atom('O', o1_pos), Atom('O', o2_pos)])
    
    def _tef6_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create TeF6 molecule."""
        x, y, z = position
        te_f_distance = 1.815  # Å
        
        # Octahedral geometry
        te_pos = [x, y, z]
        f1_pos = [x + te_f_distance, y, z]
        f2_pos = [x - te_f_distance, y, z]
        f3_pos = [x, y + te_f_distance, z]
        f4_pos = [x, y - te_f_distance, z]
        f5_pos = [x, y, z + te_f_distance]
        f6_pos = [x, y, z - te_f_distance]
        
        return Atoms([Atom('Te', te_pos), Atom('F', f1_pos), Atom('F', f2_pos),
                      Atom('F', f3_pos), Atom('F', f4_pos), Atom('F', f5_pos),
                      Atom('F', f6_pos)])
    
    # Metal oxide geometries
    def _zno_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create ZnO unit."""
        x, y, z = position
        bond_length = 1.97  # Å
        
        if orientation == 'parallel':
            zn_pos = [x - bond_length/2, y, z]
            o_pos = [x + bond_length/2, y, z]
        elif orientation == 'perpendicular':
            zn_pos = [x, y, z - bond_length/2]
            o_pos = [x, y, z + bond_length/2]
        
        return Atoms([Atom('Zn', zn_pos), Atom('O', o_pos)])
    
    def _tio2_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create TiO2 unit."""
        x, y, z = position
        ti_o_distance = 1.95  # Å
        
        if orientation == 'linear':
            ti_pos = [x, y, z]
            o1_pos = [x - ti_o_distance, y, z]
            o2_pos = [x + ti_o_distance, y, z]
        elif orientation == 'bent':
            angle_rad = np.radians(104)  # degrees
            ti_pos = [x, y, z]
            o1_pos = [x + ti_o_distance * np.cos(angle_rad/2), 
                      y + ti_o_distance * np.sin(angle_rad/2), z]
            o2_pos = [x + ti_o_distance * np.cos(angle_rad/2), 
                      y - ti_o_distance * np.sin(angle_rad/2), z]
        
        return Atoms([Atom('Ti', ti_pos), Atom('O', o1_pos), Atom('O', o2_pos)])
    
    # Individual atomic geometries
    def _ti_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Ti atom."""
        return Atoms([Atom('Ti', position)])
    
    def _cr_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Cr atom."""
        return Atoms([Atom('Cr', position)])
    
    def _ta_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Ta atom."""
        return Atoms([Atom('Ta', position)])
    
    def _pd_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Pd atom."""
        return Atoms([Atom('Pd', position)])
    
    def _v_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create V atom."""
        return Atoms([Atom('V', position)])
    
    def _pt_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Pt atom."""
        return Atoms([Atom('Pt', position)])
    
    def _ag_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Ag atom."""
        return Atoms([Atom('Ag', position)])
    
    def _re_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Re atom."""
        return Atoms([Atom('Re', position)])
    
    def _ru_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Ru atom."""
        return Atoms([Atom('Ru', position)])
    
    def _cd_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Cd atom."""
        return Atoms([Atom('Cd', position)])
    
    def _fe_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Fe atom."""
        return Atoms([Atom('Fe', position)])
    
    def _co_atom_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Co atom."""
        return Atoms([Atom('Co', position)])
    
    def _ni_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Ni atom."""
        return Atoms([Atom('Ni', position)])
    
    def _mn_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Mn atom."""
        return Atoms([Atom('Mn', position)])
    
    def _ir_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Ir atom."""
        return Atoms([Atom('Ir', position)])
    
    def _rh_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Rh atom."""
        return Atoms([Atom('Rh', position)])
    
    def _cu_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Cu atom."""
        return Atoms([Atom('Cu', position)])
    
    def _al_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Al atom."""
        return Atoms([Atom('Al', position)])
    
    def _zn_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Zn atom."""
        return Atoms([Atom('Zn', position)])
    
    def _nb_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Nb atom."""
        return Atoms([Atom('Nb', position)])
    
    def _w_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create W atom."""
        return Atoms([Atom('W', position)])
    
    def _li_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Li atom."""
        return Atoms([Atom('Li', position)])
    
    def _au_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Au atom."""
        return Atoms([Atom('Au', position)])
    
    def _p_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create P atom."""
        return Atoms([Atom('P', position)])
    
    def _b_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create B atom."""
        return Atoms([Atom('B', position)])
    
    def _si_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Si atom."""
        return Atoms([Atom('Si', position)])
    
    def _cl_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Cl atom."""
        return Atoms([Atom('Cl', position)])
    
    def _s_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create S atom."""
        return Atoms([Atom('S', position)])
    
    def _se_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Se atom."""
        return Atoms([Atom('Se', position)])
    
    def _te_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create Te atom."""
        return Atoms([Atom('Te', position)])


    # Complex organic molecule geometries
    def _f4tcnq_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create F4TCNQ molecule (simplified planar structure)."""
        x, y, z = position
        atoms = []
        
        if orientation == 'flat':
            # Simplified planar quinodimethane structure with F and CN substitutions
            # Central quinone ring
            ring_positions = [
                [x-1.4, y-0.7, z], [x-0.7, y-1.4, z], [x+0.7, y-1.4, z], [x+1.4, y-0.7, z],
                [x+1.4, y+0.7, z], [x+0.7, y+1.4, z], [x-0.7, y+1.4, z], [x-1.4, y+0.7, z]
            ]
            for pos in ring_positions:
                atoms.append(Atom('C', pos))
            
            # Additional carbons for extended structure
            atoms.extend([
                Atom('C', [x-2.1, y, z]), Atom('C', [x+2.1, y, z]),
                Atom('C', [x, y-2.1, z]), Atom('C', [x, y+2.1, z])
            ])
            
            # Fluorine atoms
            atoms.extend([
                Atom('F', [x-2.8, y-0.5, z]), Atom('F', [x-2.8, y+0.5, z]),
                Atom('F', [x+2.8, y-0.5, z]), Atom('F', [x+2.8, y+0.5, z])
            ])
            
            # Cyano groups (CN)
            atoms.extend([
                Atom('C', [x-0.7, y-2.8, z]), Atom('N', [x-0.7, y-3.5, z]),
                Atom('C', [x+0.7, y-2.8, z]), Atom('N', [x+0.7, y-3.5, z]),
                Atom('C', [x-0.7, y+2.8, z]), Atom('N', [x-0.7, y+3.5, z]),
                Atom('C', [x+0.7, y+2.8, z]), Atom('N', [x+0.7, y+3.5, z])
            ])
            
        elif orientation == 'vertical':
            # Rotate molecule to be perpendicular to surface
            ring_positions = [
                [x-1.4, y, z-0.7], [x-0.7, y, z-1.4], [x+0.7, y, z-1.4], [x+1.4, y, z-0.7],
                [x+1.4, y, z+0.7], [x+0.7, y, z+1.4], [x-0.7, y, z+1.4], [x-1.4, y, z+0.7]
            ]
            for pos in ring_positions:
                atoms.append(Atom('C', pos))
            
            atoms.extend([
                Atom('C', [x-2.1, y, z]), Atom('C', [x+2.1, y, z]),
                Atom('C', [x, y, z-2.1]), Atom('C', [x, y, z+2.1])
            ])
            
            atoms.extend([
                Atom('F', [x-2.8, y, z-0.5]), Atom('F', [x-2.8, y, z+0.5]),
                Atom('F', [x+2.8, y, z-0.5]), Atom('F', [x+2.8, y, z+0.5])
            ])
            
            atoms.extend([
                Atom('C', [x-0.7, y, z-2.8]), Atom('N', [x-0.7, y, z-3.5]),
                Atom('C', [x+0.7, y, z-2.8]), Atom('N', [x+0.7, y, z-3.5]),
                Atom('C', [x-0.7, y, z+2.8]), Atom('N', [x-0.7, y, z+3.5]),
                Atom('C', [x+0.7, y, z+2.8]), Atom('N', [x+0.7, y, z+3.5])
            ])
        
        return Atoms(atoms)
    
    def _ptcda_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create PTCDA molecule (simplified structure)."""
        x, y, z = position
        atoms = []
        
        if orientation == 'flat':
            # Simplified perylene core with anhydride groups
            # Perylene core (4 fused benzene rings)
            perylene_positions = [
                # Ring 1
                [x-2.4, y-0.7, z], [x-1.7, y-1.4, z], [x-1.0, y-1.4, z], [x-0.3, y-0.7, z],
                [x-0.3, y+0.7, z], [x-1.0, y+1.4, z], [x-1.7, y+1.4, z], [x-2.4, y+0.7, z],
                # Ring 2
                [x+0.3, y-0.7, z], [x+1.0, y-1.4, z], [x+1.7, y-1.4, z], [x+2.4, y-0.7, z],
                [x+2.4, y+0.7, z], [x+1.7, y+1.4, z], [x+1.0, y+1.4, z], [x+0.3, y+0.7, z],
                # Additional carbons for extended system
                [x-3.1, y, z], [x-3.8, y-0.7, z], [x-3.8, y+0.7, z], [x-4.5, y, z],
                [x+3.1, y, z], [x+3.8, y-0.7, z], [x+3.8, y+0.7, z], [x+4.5, y, z]
            ]
            for pos in perylene_positions:
                atoms.append(Atom('C', pos))
            
            # Anhydride oxygens
            atoms.extend([
                Atom('O', [x-5.2, y-0.5, z]), Atom('O', [x-5.2, y+0.5, z]),
                Atom('O', [x-4.5, y-1.4, z]), Atom('O', [x-4.5, y+1.4, z]),
                Atom('O', [x+5.2, y-0.5, z]), Atom('O', [x+5.2, y+0.5, z])
            ])
            
        elif orientation == 'vertical':
            # Rotate to vertical orientation
            perylene_positions = [
                [x-2.4, y, z-0.7], [x-1.7, y, z-1.4], [x-1.0, y, z-1.4], [x-0.3, y, z-0.7],
                [x-0.3, y, z+0.7], [x-1.0, y, z+1.4], [x-1.7, y, z+1.4], [x-2.4, y, z+0.7],
                [x+0.3, y, z-0.7], [x+1.0, y, z-1.4], [x+1.7, y, z-1.4], [x+2.4, y, z-0.7],
                [x+2.4, y, z+0.7], [x+1.7, y, z+1.4], [x+1.0, y, z+1.4], [x+0.3, y, z+0.7],
                [x-3.1, y, z], [x-3.8, y, z-0.7], [x-3.8, y, z+0.7], [x-4.5, y, z],
                [x+3.1, y, z], [x+3.8, y, z-0.7], [x+3.8, y, z+0.7], [x+4.5, y, z]
            ]
            for pos in perylene_positions:
                atoms.append(Atom('C', pos))
            
            atoms.extend([
                Atom('O', [x-5.2, y, z-0.5]), Atom('O', [x-5.2, y, z+0.5]),
                Atom('O', [x-4.5, y, z-1.4]), Atom('O', [x-4.5, y, z+1.4]),
                Atom('O', [x+5.2, y, z-0.5]), Atom('O', [x+5.2, y, z+0.5])
            ])
        
        return Atoms(atoms)
    
    def _tetracene_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create tetracene molecule."""
        x, y, z = position
        atoms = []
        
        if orientation == 'flat':
            # 4 fused benzene rings
            tetracene_positions = [
                # Ring carbons
                [x-4.2, y-0.7, z], [x-3.5, y-1.4, z], [x-2.8, y-1.4, z], [x-2.1, y-0.7, z],
                [x-2.1, y+0.7, z], [x-2.8, y+1.4, z], [x-3.5, y+1.4, z], [x-4.2, y+0.7, z],
                [x-1.4, y-0.7, z], [x-0.7, y-1.4, z], [x+0.7, y-1.4, z], [x+1.4, y-0.7, z],
                [x+1.4, y+0.7, z], [x+0.7, y+1.4, z], [x-0.7, y+1.4, z], [x-1.4, y+0.7, z],
                [x+2.1, y-0.7, z], [x+4.2, y-0.7, z]
            ]
            for pos in tetracene_positions:
                atoms.append(Atom('C', pos))
            
            # Hydrogens
            h_positions = [
                [x-4.9, y-0.7, z], [x-3.5, y-2.1, z], [x-2.8, y-2.1, z], [x-4.9, y+0.7, z],
                [x-2.8, y+2.1, z], [x-3.5, y+2.1, z], [x-0.7, y-2.1, z], [x+0.7, y-2.1, z],
                [x+0.7, y+2.1, z], [x-0.7, y+2.1, z], [x+2.8, y-1.4, z], [x+4.9, y-0.7, z]
            ]
            for pos in h_positions:
                atoms.append(Atom('H', pos))
                
        elif orientation == 'vertical':
            # Rotate to vertical
            tetracene_positions = [
                [x-4.2, y, z-0.7], [x-3.5, y, z-1.4], [x-2.8, y, z-1.4], [x-2.1, y, z-0.7],
                [x-2.1, y, z+0.7], [x-2.8, y, z+1.4], [x-3.5, y, z+1.4], [x-4.2, y, z+0.7],
                [x-1.4, y, z-0.7], [x-0.7, y, z-1.4], [x+0.7, y, z-1.4], [x+1.4, y, z-0.7],
                [x+1.4, y, z+0.7], [x+0.7, y, z+1.4], [x-0.7, y, z+1.4], [x-1.4, y, z+0.7],
                [x+2.1, y, z-0.7], [x+4.2, y, z-0.7]
            ]
            for pos in tetracene_positions:
                atoms.append(Atom('C', pos))
            
            h_positions = [
                [x-4.9, y, z-0.7], [x-3.5, y, z-2.1], [x-2.8, y, z-2.1], [x-4.9, y, z+0.7],
                [x-2.8, y, z+2.1], [x-3.5, y, z+2.1], [x-0.7, y, z-2.1], [x+0.7, y, z-2.1],
                [x+0.7, y, z+2.1], [x-0.7, y, z+2.1], [x+2.8, y, z-1.4], [x+4.9, y, z-0.7]
            ]
            for pos in h_positions:
                atoms.append(Atom('H', pos))
        
        return Atoms(atoms)
    
    def _tcnq_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create TCNQ molecule."""
        x, y, z = position
        atoms = []
        
        if orientation == 'flat':
            # Quinodimethane core
            core_positions = [
                [x-1.4, y-0.7, z], [x-0.7, y-1.4, z], [x+0.7, y-1.4, z], [x+1.4, y-0.7, z],
                [x+1.4, y+0.7, z], [x+0.7, y+1.4, z], [x-0.7, y+1.4, z], [x-1.4, y+0.7, z],
                [x-2.1, y, z], [x+2.1, y, z], [x, y-2.1, z], [x, y+2.1, z]
            ]
            for pos in core_positions:
                atoms.append(Atom('C', pos))
            
            # Cyano groups
            atoms.extend([
                Atom('C', [x-2.8, y-0.5, z]), Atom('N', [x-3.5, y-0.5, z]),
                Atom('C', [x-2.8, y+0.5, z]), Atom('N', [x-3.5, y+0.5, z]),
                Atom('C', [x+2.8, y-0.5, z]), Atom('N', [x+3.5, y-0.5, z]),
                Atom('C', [x+2.8, y+0.5, z]), Atom('N', [x+3.5, y+0.5, z])
            ])
            
        elif orientation == 'vertical':
            core_positions = [
                [x-1.4, y, z-0.7], [x-0.7, y, z-1.4], [x+0.7, y, z-1.4], [x+1.4, y, z-0.7],
                [x+1.4, y, z+0.7], [x+0.7, y, z+1.4], [x-0.7, y, z+1.4], [x-1.4, y, z+0.7],
                [x-2.1, y, z], [x+2.1, y, z], [x, y, z-2.1], [x, y, z+2.1]
            ]
            for pos in core_positions:
                atoms.append(Atom('C', pos))
            
            atoms.extend([
                Atom('C', [x-2.8, y, z-0.5]), Atom('N', [x-3.5, y, z-0.5]),
                Atom('C', [x-2.8, y, z+0.5]), Atom('N', [x-3.5, y, z+0.5]),
                Atom('C', [x+2.8, y, z-0.5]), Atom('N', [x+3.5, y, z-0.5]),
                Atom('C', [x+2.8, y, z+0.5]), Atom('N', [x+3.5, y, z+0.5])
            ])
        
        return Atoms(atoms)
    
    def _tcne_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create TCNE molecule."""
        x, y, z = position
        atoms = []
        
        if orientation == 'flat':
            # Central ethylene unit
            atoms.extend([
                Atom('C', [x-0.7, y, z]), Atom('C', [x+0.7, y, z])
            ])
            
            # Cyano groups
            atoms.extend([
                Atom('C', [x-1.4, y-0.7, z]), Atom('N', [x-2.1, y-0.7, z]),
                Atom('C', [x-1.4, y+0.7, z]), Atom('N', [x-2.1, y+0.7, z]),
                Atom('C', [x+1.4, y-0.7, z]), Atom('N', [x+2.1, y-0.7, z]),
                Atom('C', [x+1.4, y+0.7, z]), Atom('N', [x+2.1, y+0.7, z])
            ])
            
        elif orientation == 'vertical':
            atoms.extend([
                Atom('C', [x, y, z-0.7]), Atom('C', [x, y, z+0.7])
            ])
            
            atoms.extend([
                Atom('C', [x-0.7, y, z-1.4]), Atom('N', [x-0.7, y, z-2.1]),
                Atom('C', [x+0.7, y, z-1.4]), Atom('N', [x+0.7, y, z-2.1]),
                Atom('C', [x-0.7, y, z+1.4]), Atom('N', [x-0.7, y, z+2.1]),
                Atom('C', [x+0.7, y, z+1.4]), Atom('N', [x+0.7, y, z+2.1])
            ])
        
        return Atoms(atoms)
    
    def _ttf_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create TTF (tetrathiafulvalene) molecule."""
        x, y, z = position
        atoms = []
        
        if orientation == 'flat':
            # Central dithiole rings
            atoms.extend([
                Atom('C', [x-1.0, y-0.5, z]), Atom('C', [x-1.0, y+0.5, z]),
                Atom('C', [x+1.0, y-0.5, z]), Atom('C', [x+1.0, y+0.5, z]),
                Atom('C', [x-0.3, y, z]), Atom('C', [x+0.3, y, z])
            ])
            
            # Sulfur atoms
            atoms.extend([
                Atom('S', [x-2.0, y-1.0, z]), Atom('S', [x-2.0, y+1.0, z]),
                Atom('S', [x+2.0, y-1.0, z]), Atom('S', [x+2.0, y+1.0, z])
            ])
            
            # Hydrogens
            atoms.extend([
                Atom('H', [x-1.0, y-1.2, z]), Atom('H', [x-1.0, y+1.2, z]),
                Atom('H', [x+1.0, y-1.2, z]), Atom('H', [x+1.0, y+1.2, z])
            ])
            
        elif orientation == 'vertical':
            atoms.extend([
                Atom('C', [x-1.0, y, z-0.5]), Atom('C', [x-1.0, y, z+0.5]),
                Atom('C', [x+1.0, y, z-0.5]), Atom('C', [x+1.0, y, z+0.5]),
                Atom('C', [x-0.3, y, z]), Atom('C', [x+0.3, y, z])
            ])
            
            atoms.extend([
                Atom('S', [x-2.0, y, z-1.0]), Atom('S', [x-2.0, y, z+1.0]),
                Atom('S', [x+2.0, y, z-1.0]), Atom('S', [x+2.0, y, z+1.0])
            ])
            
            atoms.extend([
                Atom('H', [x-1.0, y, z-1.2]), Atom('H', [x-1.0, y, z+1.2]),
                Atom('H', [x+1.0, y, z-1.2]), Atom('H', [x+1.0, y, z+1.2])
            ])
        
        return Atoms(atoms)
    
    def _benzyl_viologen_geometry(self, position: Tuple[float, float, float], orientation: str) -> Atoms:
        """Create benzyl viologen molecule (simplified structure)."""
        x, y, z = position
        atoms = []
        
        if orientation == 'flat':
            # Central bipyridinium unit
            pyridine1_positions = [
                [x-2.1, y-0.7, z], [x-1.4, y-1.4, z], [x-0.7, y-1.4, z], [x, y-0.7, z],
                [x, y+0.7, z], [x-0.7, y+1.4, z], [x-1.4, y+1.4, z], [x-2.1, y+0.7, z]
            ]
            pyridine2_positions = [
                [x+2.1, y-0.7, z], [x+1.4, y-1.4, z], [x+0.7, y-1.4, z], [x, y-0.7, z],
                [x, y+0.7, z], [x+0.7, y+1.4, z], [x+1.4, y+1.4, z], [x+2.1, y+0.7, z]
            ]
            
            for pos in pyridine1_positions[:6]:  # First 6 carbons
                atoms.append(Atom('C', pos))
            atoms.append(Atom('N', pyridine1_positions[6]))  # Nitrogen
            atoms.append(Atom('N', pyridine1_positions[7]))  # Nitrogen
            
            for pos in pyridine2_positions[:6]:  # First 6 carbons
                atoms.append(Atom('C', pos))
            atoms.append(Atom('N', pyridine2_positions[6]))  # Nitrogen
            atoms.append(Atom('N', pyridine2_positions[7]))  # Nitrogen
            
            # Benzyl groups (simplified)
            benzyl_positions = [
                [x-3.5, y, z], [x-4.2, y-0.7, z], [x-4.9, y-0.7, z], [x-5.6, y, z],
                [x-4.9, y+0.7, z], [x-4.2, y+0.7, z],
                [x+3.5, y, z], [x+4.2, y-0.7, z], [x+4.9, y-0.7, z], [x+5.6, y, z],
                [x+4.9, y+0.7, z], [x+4.2, y+0.7, z]
            ]
            for pos in benzyl_positions:
                atoms.append(Atom('C', pos))
            
            # Add simplified hydrogens (not all for brevity)
            h_positions = [
                [x-1.4, y-2.1, z], [x-0.7, y-2.1, z], [x-0.7, y+2.1, z], [x-1.4, y+2.1, z],
                [x+1.4, y-2.1, z], [x+0.7, y-2.1, z], [x+0.7, y+2.1, z], [x+1.4, y+2.1, z],
                [x-4.2, y-1.4, z], [x-4.9, y-1.4, z], [x-5.6, y-0.7, z], [x-5.6, y+0.7, z],
                [x-4.9, y+1.4, z], [x-4.2, y+1.4, z], [x+4.2, y-1.4, z], [x+4.9, y-1.4, z],
                [x+5.6, y-0.7, z], [x+5.6, y+0.7, z]
            ]
            for pos in h_positions:
                atoms.append(Atom('H', pos))
                
        elif orientation == 'vertical':
            # Central bipyridinium unit
            pyridine1_positions = [
                [x-2.1, y, z-0.7], [x-1.4, y, z-1.4], [x-0.7, y, z-1.4], [x, y, z-0.7],
                [x, y, z+0.7], [x-0.7, y, z+1.4], [x-1.4, y, z+1.4], [x-2.1, y, z+0.7]
            ]
            pyridine2_positions = [
                [x+2.1, y, z-0.7], [x+1.4, y, z-1.4], [x+0.7, y, z-1.4], [x, y, z-0.7],
                [x, y, z+0.7], [x+0.7, y, z+1.4], [x+1.4, y, z+1.4], [x+2.1, y, z+0.7]
            ]
            
            for pos in pyridine1_positions[:6]:  # First 6 carbons
                atoms.append(Atom('C', pos))
            atoms.append(Atom('N', pyridine1_positions[6]))  # Nitrogen
            atoms.append(Atom('N', pyridine1_positions[7]))  # Nitrogen
            
            for pos in pyridine2_positions[:6]:  # First 6 carbons
                atoms.append(Atom('C', pos))
            atoms.append(Atom('N', pyridine2_positions[6]))  # Nitrogen
            atoms.append(Atom('N', pyridine2_positions[7]))  # Nitrogen
            
            # Benzyl groups (simplified)
            benzyl_positions = [
                [x-3.5, y, z], [x-4.2, y-0.7, z], [x-4.9, y-0.7, z], [x-5.6, y, z],
                [x-4.9, y+0.7, z], [x-4.2, y+0.7, z],
                [x+3.5, y, z], [x+4.2, y-0.7, z], [x+4.9, y-0.7, z], [x+5.6, y, z],
                [x+4.9, y+0.7, z], [x+4.2, y+0.7, z]
            ]
            for pos in benzyl_positions:
                atoms.append(Atom('C', pos))
            
            # Add simplified hydrogens (not all for brevity)
            h_positions = [
                [x-1.4, y-2.1, z], [x-0.7, y-2.1, z], [x-0.7, y+2.1, z], [x-1.4, y+2.1, z],
                [x+1.4, y-2.1, z], [x+0.7, y-2.1, z], [x+0.7, y+2.1, z], [x+1.4, y+2.1, z],
                [x-4.2, y-1.4, z], [x-4.9, y-1.4, z], [x-5.6, y-0.7, z], [x-5.6, y+0.7, z],
                [x-4.9, y+1.4, z], [x-4.2, y+1.4, z], [x+4.2, y-1.4, z], [x+4.9, y-1.4, z],
                [x+5.6, y-0.7, z], [x+5.6, y+0.7, z]
            ]
            for pos in h_positions:
                atoms.append(Atom('H', pos))
                
        return Atoms(atoms)
    

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
