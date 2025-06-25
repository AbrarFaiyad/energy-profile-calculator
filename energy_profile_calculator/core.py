"""
Core module for energy profile calculations.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from tqdm import tqdm

from .adsorbants import AdsorbantLibrary
from .surfaces import SurfaceBuilder
from .calculators import CalculatorFactory
from .plotting import EnergyProfilePlotter
from .utils import save_results, estimate_calculation_time


class EnergyProfileCalculator:
    """
    Main class for calculating adsorption energy profiles.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize energy profile calculator.
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or {}
        
        # Initialize components
        self.adsorbant_library = AdsorbantLibrary()
        self.surface_builder = SurfaceBuilder()
        self.calculator_factory = CalculatorFactory()
        self.plotter = EnergyProfilePlotter()
        
        # Calculation state
        self.surface = None
        self.results = {}
        
    def setup_surface(self, material: str, miller_indices: Tuple[int, ...], 
                     size: Tuple[int, int, int], vacuum: float = 10.0,
                     crystal_structure: Optional[str] = None) -> None:
        """
        Setup the surface for calculations.
        
        Args:
            material: Surface material (e.g., 'Au', 'Pt')
            miller_indices: Miller indices (e.g., (1, 1, 1))
            size: Surface size (nx, ny, nlayers)
            vacuum: Vacuum space above surface (Å)
            crystal_structure: Crystal structure override
        """
        print(f"=== Setting up {material}{miller_indices} surface ===")
        
        self.surface = self.surface_builder.build_surface(
            material, miller_indices, size, vacuum, crystal_structure
        )
        
        surface_info = self.surface_builder.get_surface_info(self.surface)
        
        print(f"Surface created successfully:")
        print(f"  Material: {material}")
        print(f"  Miller indices: {miller_indices}")
        print(f"  Size: {size}")
        print(f"  Number of atoms: {surface_info['n_atoms']}")
        print(f"  Cell dimensions: {[f'{x:.3f}' for x in np.diagonal(self.surface.cell)]}")
        print(f"  Surface area: {surface_info['surface_area']:.3f} Å²")
        print(f"  Number of layers: {len(surface_info['layers'])}")
        
        self.surface_material = material
        self.surface_name = f"{material}({','.join(map(str, miller_indices))})"
    
    def setup_calculators(self, use_ml: bool = True, use_dft: bool = False,
                         ml_model: str = "uma-s-1", ml_device: str = "cuda",
                         dft_pseudo_dir: Optional[str] = None,
                         dft_num_cores: Optional[int] = None) -> None:
        """
        Setup calculation methods.
        
        Args:
            use_ml: Use machine learning calculators
            use_dft: Use DFT calculators  
            ml_model: ML model name
            ml_device: Device for ML calculations
            dft_pseudo_dir: Directory with pseudopotential files
            dft_num_cores: Number of CPU cores for DFT
        """
        print("=== Setting up calculators ===")
        
        if use_ml:
            self.ml_manager = self.calculator_factory.setup_ml_calculators(ml_model, ml_device)
            print(f"ML calculators ready: {self.ml_manager.list_available_tasks()}")
        
        if use_dft:
            if dft_pseudo_dir is None:
                raise ValueError("dft_pseudo_dir must be specified for DFT calculations")
            
            self.dft_manager = self.calculator_factory.setup_dft_calculator(
                dft_pseudo_dir, dft_num_cores
            )
            print(f"DFT calculator ready with {self.dft_manager.num_cores} cores")
        
        self.use_ml = use_ml
        self.use_dft = use_dft
    
    def calculate_energy_profile(self, adsorbant: str, 
                               z_start: float = 2.0, z_end: float = 8.0, z_step: float = 0.2,
                               adsorbant_orientation: str = 'default',
                               ml_tasks: List[str] = ['omat', 'omc'],
                               dft_functional: str = 'pbe',
                               dft_subset_factor: int = 2,
                               custom_pseudopotentials: Optional[Dict[str, str]] = None,
                               save_structures: bool = True,
                               output_dir: str = './results') -> Dict[str, Any]:
        """
        Calculate energy profile for adsorbant on surface.
        
        Args:
            adsorbant: Name of adsorbant molecule
            z_start: Starting height above surface (Å)
            z_end: Ending height above surface (Å)
            z_step: Height increment (Å)
            adsorbant_orientation: Molecular orientation
            ml_tasks: List of ML tasks to run
            dft_functional: DFT functional
            dft_subset_factor: Factor to reduce DFT calculation points
            custom_pseudopotentials: Custom pseudopotential mapping
            save_structures: Whether to save structure files
            output_dir: Output directory
            
        Returns:
            Dictionary containing calculation results
        """
        if self.surface is None:
            raise RuntimeError("Surface not set up. Call setup_surface() first.")
        
        # Validate adsorbant
        if adsorbant not in self.adsorbant_library.list_adsorbants():
            raise ValueError(f"Adsorbant '{adsorbant}' not found in library")
        
        # Get adsorbant elements for DFT
        adsorbant_elements = self.adsorbant_library.get_elements(adsorbant)
        surface_elements = list(set(self.surface.get_chemical_symbols()))
        all_elements = list(set(surface_elements + adsorbant_elements))
        
        # Setup calculation parameters
        heights = np.arange(z_start, z_end + z_step, z_step)
        z_top = self.surface.positions[:, 2].max()
        
        # Center position over surface
        center_x = self.surface.cell[0, 0] / 2
        center_y = self.surface.cell[1, 1] / 2
        
        print(f"\n=== Energy Profile Calculation ===")
        print(f"Adsorbant: {adsorbant}")
        print(f"Surface: {self.surface_name}")
        print(f"Height range: {z_start} to {z_end} Å (step: {z_step} Å)")
        print(f"Number of points: {len(heights)}")
        print(f"Adsorbant position (x,y): ({center_x:.3f}, {center_y:.3f})")
        
        # Estimate calculation time
        total_time, time_str = estimate_calculation_time(
            len(heights), self.use_dft, dft_subset_factor
        )
        print(f"Estimated time: {time_str}")
        
        # Initialize results
        results = {
            'heights': heights,
            'adsorbant': adsorbant,
            'surface': self.surface_name,
            'configuration': {
                'z_start': z_start,
                'z_end': z_end,
                'z_step': z_step,
                'orientation': adsorbant_orientation
            }
        }
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # ML calculations
        if self.use_ml:
            for task in ml_tasks:
                if task not in self.ml_manager.list_available_tasks():
                    print(f"Warning: ML task '{task}' not available, skipping")
                    continue
                
                print(f"\n--- Running {task.upper()} calculations ---")
                energies = self._calculate_ml_energies(
                    heights, adsorbant, adsorbant_orientation,
                    center_x, center_y, z_top, task, save_structures, output_path
                )
                results[f'{task}_energies'] = energies
        
        # DFT calculations  
        if self.use_dft:
            print(f"\n--- Running DFT calculations ---")
            dft_heights = heights[::dft_subset_factor]
            dft_energies = self._calculate_dft_energies(
                dft_heights, adsorbant, adsorbant_orientation,
                center_x, center_y, z_top, all_elements,
                dft_functional, custom_pseudopotentials,
                save_structures, output_path
            )
            results['dft_energies'] = dft_energies
            results['dft_heights'] = dft_heights
        
        # Normalize energies (reference point at highest z)
        self._normalize_energies(results)
        
        # Save results
        save_results(results, output_path, f"{adsorbant}_{self.surface_name}_profile")
        
        # Store results
        self.results = results
        
        print(f"\n🎉 Energy profile calculation completed!")
        print(f"Results saved to: {output_path}")
        
        return results
    
    def _calculate_ml_energies(self, heights: np.ndarray, adsorbant: str, orientation: str,
                              center_x: float, center_y: float, z_top: float,
                              task: str, save_structures: bool, output_path: Path) -> np.ndarray:
        """Calculate ML energies at different heights."""
        energies = []
        
        for i, height in enumerate(tqdm(heights, desc=f"{task.upper()} calculations")):
            # Create system with adsorbant
            system = self.surface.copy()
            adsorbant_pos = (center_x, center_y, z_top + height)
            
            adsorbant_atoms = self.adsorbant_library.get_adsorbant(
                adsorbant, adsorbant_pos, orientation
            )
            
            # Add adsorbant to surface
            for atom in adsorbant_atoms:
                system.append(atom)
            
            # Calculate energy
            energy = self.ml_manager.calculate_energy(system, task)
            energies.append(energy)
            
            # Save structure if requested
            if save_structures:
                from ase.io import write
                filename = output_path / f"{task}_structure_h{height:.1f}.xyz"
                write(filename, system)
        
        return np.array(energies)
    
    def _calculate_dft_energies(self, heights: np.ndarray, adsorbant: str, orientation: str,
                               center_x: float, center_y: float, z_top: float,
                               all_elements: List[str], functional: str,
                               custom_pseudopotentials: Optional[Dict[str, str]],
                               save_structures: bool, output_path: Path) -> np.ndarray:
        """Calculate DFT energies at selected heights."""
        energies = []
        
        for i, height in enumerate(tqdm(heights, desc="DFT calculations")):
            try:
                # Create system with adsorbant
                system = self.surface.copy()
                adsorbant_pos = (center_x, center_y, z_top + height)
                
                adsorbant_atoms = self.adsorbant_library.get_adsorbant(
                    adsorbant, adsorbant_pos, orientation
                )
                
                # Add adsorbant to surface
                for atom in adsorbant_atoms:
                    system.append(atom)
                
                # Calculate energy
                energy = self.dft_manager.calculate_energy(
                    system, all_elements, functional, custom_pseudopotentials
                )
                energies.append(energy)
                
                # Save structure if requested
                if save_structures:
                    from ase.io import write
                    filename = output_path / f"dft_structure_h{height:.1f}.xyz"
                    write(filename, system)
                
            except Exception as e:
                print(f"DFT calculation failed at height {height:.1f} Å: {str(e)[:50]}...")
                energies.append(np.nan)
        
        return np.array(energies)
    
    def _normalize_energies(self, results: Dict[str, Any]) -> None:
        """Normalize energy profiles to reference point."""
        for key in results:
            if 'energies' in key and isinstance(results[key], np.ndarray):
                energies = results[key]
                # Use last valid energy as reference (highest z)
                valid_mask = ~np.isnan(energies)
                if np.any(valid_mask):
                    last_valid_idx = np.where(valid_mask)[0][-1]
                    results[key] = energies - energies[last_valid_idx]
    
    def create_plots(self, save_path: Optional[str] = None, 
                    formats: List[str] = ['png', 'pdf']) -> None:
        """
        Create energy profile plots.
        
        Args:
            save_path: Base path for saving plots
            formats: List of file formats
        """
        if not self.results:
            raise RuntimeError("No results to plot. Run calculate_energy_profile() first.")
        
        try:
            # Prepare energy data for plotting
            energy_data = {}
            heights = self.results['heights']
            
            for key in self.results:
                if 'energies' in key:
                    method_name = key.replace('_energies', '').upper()
                    if key == 'dft_energies' and 'dft_heights' in self.results:
                        # Handle DFT with different height array
                        continue  # Skip for now, handle separately
                    else:
                        energy_data[method_name] = self.results[key]
            
            # Create main energy profile plot
            fig = self.plotter.plot_energy_profile(
                heights, energy_data,
                self.results['adsorbant'], self.results['surface'],
                save_path, formats
            )
            
            # Create summary comparison plot
            summary_fig = self.plotter.create_comparison_summary(
                self.results, save_path
            )
            
            # Print comparison table
            table = self.plotter.create_method_comparison_table(self.results)
            print(f"\n{table}")
            
            return fig, summary_fig
            
        except Exception as e:
            print(f"Warning: Plotting failed due to display/GUI issues: {e}")
            print("This is common in headless environments. Results are still saved.")
            
            # Still print the comparison table
            table = self.plotter.create_method_comparison_table(self.results)
            print(f"\n{table}")
            
            return None, None
    
    def get_binding_energies(self) -> Dict[str, float]:
        """Get binding energies (negative of minimum energies) for each method."""
        if not self.results:
            raise RuntimeError("No results available. Run calculations first.")
        
        binding_energies = {}
        
        for key in self.results:
            if 'energies' in key:
                method_name = key.replace('_energies', '').upper()
                energies = self.results[key]
                
                if np.any(~np.isnan(energies)):
                    valid_energies = energies[~np.isnan(energies)]
                    binding_energies[method_name] = -np.min(valid_energies)
        
        return binding_energies
    
    def get_optimal_heights(self) -> Dict[str, float]:
        """Get optimal adsorption heights for each method."""
        if not self.results:
            raise RuntimeError("No results available. Run calculations first.")
        
        optimal_heights = {}
        
        for key in self.results:
            if 'energies' in key:
                method_name = key.replace('_energies', '').upper()
                energies = self.results[key]
                
                if key == 'dft_energies' and 'dft_heights' in self.results:
                    heights = self.results['dft_heights']
                else:
                    heights = self.results['heights']
                
                if np.any(~np.isnan(energies)):
                    valid_mask = ~np.isnan(energies)
                    valid_energies = energies[valid_mask]
                    valid_heights = heights[valid_mask]
                    
                    min_idx = np.argmin(valid_energies)
                    optimal_heights[method_name] = valid_heights[min_idx]
        
        return optimal_heights
