"""
Calculator managers for ML and DFT calculations.
"""

import os
import numpy as np
from typing import Dict, List, Optional, Any
from ase import Atoms
from .utils import detect_cpu_cores, get_default_pseudopotentials, validate_pseudopotentials


class MLCalculatorManager:
    """
    Manager for machine learning calculators (OMAT/OMC).
    """
    
    def __init__(self, model: str = "uma-s-1", device: str = "cuda"):
        """
        Initialize ML calculator manager.
        
        Args:
            model: Name of the ML model
            device: Device to run calculations on ("cuda" or "cpu")
        """
        self.model = model
        self.device = device
        self.calculators = {}
        self._initialize_calculators()
    
    def _initialize_calculators(self):
        """Initialize ML calculators."""
        try:
            from fairchem.core import pretrained_mlip, FAIRChemCalculator
            
            print(f"Initializing {self.model} model on {self.device}...")
            predictor = pretrained_mlip.get_predict_unit(self.model, device=self.device)
            
            self.calculators['omc'] = FAIRChemCalculator(predictor, task_name="omc")
            self.calculators['omat'] = FAIRChemCalculator(predictor, task_name="omat")
            
            print("ML calculators initialized successfully")
            
        except ImportError as e:
            raise ImportError(f"Failed to import fairchem modules: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ML calculators: {e}")
    
    def get_calculator(self, task: str):
        """
        Get ML calculator for specific task.
        
        Args:
            task: Task name ("omc" or "omat")
            
        Returns:
            ML calculator object
        """
        if task not in self.calculators:
            raise ValueError(f"Task '{task}' not available. Available: {list(self.calculators.keys())}")
        
        return self.calculators[task]
    
    def calculate_energy(self, atoms: Atoms, task: str) -> float:
        """
        Calculate energy using ML calculator.
        
        Args:
            atoms: Atoms object
            task: Task name ("omc" or "omat")
            
        Returns:
            Energy in eV
        """
        calculator = self.get_calculator(task)
        atoms.calc = calculator
        return atoms.get_potential_energy()
    
    def list_available_tasks(self) -> List[str]:
        """Get list of available ML tasks."""
        return list(self.calculators.keys())


class DFTCalculatorManager:
    """
    Manager for DFT calculations using Quantum ESPRESSO.
    """
    
    def __init__(self, pseudo_dir: str, num_cores: Optional[int] = None):
        """
        Initialize DFT calculator manager.
        
        Args:
            pseudo_dir: Directory containing pseudopotential files
            num_cores: Number of CPU cores to use (auto-detect if None)
        """
        self.pseudo_dir = pseudo_dir
        self.num_cores = num_cores if num_cores is not None else detect_cpu_cores()
        self.profile = None
        self.default_pseudopotentials = get_default_pseudopotentials()
        self._setup_profile()
    
    def _setup_profile(self):
        """Setup Quantum ESPRESSO profile."""
        try:
            from ase.calculators.espresso import EspressoProfile
            
            self.profile = EspressoProfile(
                command=f'mpiexec -n {self.num_cores} pw.x',
                pseudo_dir=self.pseudo_dir
            )
            print(f"DFT profile initialized with {self.num_cores} cores")
            
        except ImportError as e:
            raise ImportError(f"Failed to import ASE Quantum ESPRESSO calculator: {e}")
    
    def create_calculator(self, elements: List[str], 
                         functional: str = "pbe",
                         custom_pseudopotentials: Optional[Dict[str, str]] = None,
                         **calc_params) -> 'Espresso':
        """
        Create DFT calculator for given elements.
        
        Args:
            elements: List of element symbols
            functional: DFT functional
            custom_pseudopotentials: Custom pseudopotential mapping
            **calc_params: Additional calculator parameters
            
        Returns:
            Quantum ESPRESSO calculator
        """
        try:
            from ase.calculators.espresso import Espresso
        except ImportError as e:
            raise ImportError(f"Failed to import Quantum ESPRESSO calculator: {e}")
        
        # Get pseudopotentials
        if custom_pseudopotentials is not None:
            pseudopotentials = custom_pseudopotentials.copy()
        else:
            pseudopotentials = {}
        
        # Fill in missing pseudopotentials from defaults
        if functional in self.default_pseudopotentials:
            default_pseudos = self.default_pseudopotentials[functional]
            for element in elements:
                if element not in pseudopotentials:
                    if element in default_pseudos:
                        pseudopotentials[element] = default_pseudos[element]
                    else:
                        raise ValueError(f"No pseudopotential found for element '{element}'")
        
        # Validate pseudopotential files exist
        if not validate_pseudopotentials(pseudopotentials, self.pseudo_dir):
            print("Warning: Some pseudopotential files may not exist")
        
        # Default calculation parameters
        default_params = {
            'input_data': {
                'system': {
                    'ecutwfc': 80,
                    'ecutrho': 640,
                    'occupations': 'smearing',
                    'smearing': 'mp',
                    'degauss': 0.01,
                    'vdw_corr': 'grimme-d3',
                },
                'electrons': {
                    'conv_thr': 1e-8
                }
            },
            'kpts': (6, 6, 1)
        }
        
        # Update with user parameters
        for key, value in calc_params.items():
            if key == 'input_data' and isinstance(value, dict):
                # Merge input_data recursively
                for section, params in value.items():
                    if section in default_params['input_data']:
                        default_params['input_data'][section].update(params)
                    else:
                        default_params['input_data'][section] = params
            else:
                default_params[key] = value
        
        # Create calculator
        calculator = Espresso(
            profile=self.profile,
            pseudopotentials=pseudopotentials,
            **default_params
        )
        
        return calculator
    
    def calculate_energy(self, atoms: Atoms, elements: List[str], 
                        functional: str = "pbe",
                        custom_pseudopotentials: Optional[Dict[str, str]] = None,
                        **calc_params) -> float:
        """
        Calculate energy using DFT.
        
        Args:
            atoms: Atoms object
            elements: List of element symbols in the system
            functional: DFT functional
            custom_pseudopotentials: Custom pseudopotential mapping
            **calc_params: Additional calculator parameters
            
        Returns:
            Energy in eV
        """
        calculator = self.create_calculator(
            elements, functional, custom_pseudopotentials, **calc_params
        )
        
        # Ensure double precision
        atoms.positions = np.array(atoms.positions, dtype=np.float64)
        atoms.cell = np.array(atoms.cell, dtype=np.float64)
        
        atoms.calc = calculator
        return atoms.get_potential_energy()
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """Get default DFT calculation parameters."""
        return {
            'input_data': {
                'system': {
                    'ecutwfc': 80,
                    'ecutrho': 640,
                    'occupations': 'smearing',
                    'smearing': 'mp',
                    'degauss': 0.01,
                    'vdw_corr': 'grimme-d3',
                },
                'electrons': {
                    'conv_thr': 1e-8
                }
            },
            'kpts': (6, 6, 1)
        }
    
    def list_available_functionals(self) -> List[str]:
        """Get list of available DFT functionals."""
        return list(self.default_pseudopotentials.keys())
    
    def list_available_elements(self, functional: str = "pbe") -> List[str]:
        """Get list of elements with available pseudopotentials."""
        if functional not in self.default_pseudopotentials:
            raise ValueError(f"Functional '{functional}' not available")
        
        return list(self.default_pseudopotentials[functional].keys())


class CalculatorFactory:
    """
    Factory class for creating and managing calculators.
    """
    
    def __init__(self):
        self.ml_manager = None
        self.dft_manager = None
    
    def setup_ml_calculators(self, model: str = "uma-s-1", device: str = "cuda") -> MLCalculatorManager:
        """Setup ML calculator manager."""
        self.ml_manager = MLCalculatorManager(model, device)
        return self.ml_manager
    
    def setup_dft_calculator(self, pseudo_dir: str, num_cores: Optional[int] = None) -> DFTCalculatorManager:
        """Setup DFT calculator manager."""
        self.dft_manager = DFTCalculatorManager(pseudo_dir, num_cores)
        return self.dft_manager
    
    def get_ml_manager(self) -> MLCalculatorManager:
        """Get ML calculator manager."""
        if self.ml_manager is None:
            raise RuntimeError("ML calculators not initialized. Call setup_ml_calculators() first.")
        return self.ml_manager
    
    def get_dft_manager(self) -> DFTCalculatorManager:
        """Get DFT calculator manager."""
        if self.dft_manager is None:
            raise RuntimeError("DFT calculator not initialized. Call setup_dft_calculator() first.")
        return self.dft_manager
