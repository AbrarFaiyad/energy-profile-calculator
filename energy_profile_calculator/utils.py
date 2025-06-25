"""
Utility functions for the Energy Profile Calculator package.
"""

import os
import yaml
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from pathlib import Path


def detect_cpu_cores() -> int:
    """
    Detect the number of available CPU cores.

    Returns:
        int: Number of CPU cores available.
    """
    return os.cpu_count()


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML or JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        if config_path.suffix.lower() in ['.yml', '.yaml']:
            config = yaml.safe_load(f)
        elif config_path.suffix.lower() == '.json':
            config = json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")
    
    return config


def save_results(results: Dict[str, Any], output_dir: str, filename: str = "results"):
    """
    Save calculation results to files.

    Args:
        results: Dictionary containing calculation results
        output_dir: Directory to save results
        filename: Base filename (without extension)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as JSON
    json_path = output_dir / f"{filename}.json"
    with open(json_path, 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        json_results = {}
        for key, value in results.items():
            if isinstance(value, np.ndarray):
                json_results[key] = value.tolist()
            else:
                json_results[key] = value
        json.dump(json_results, f, indent=2)
    
    # Save energy data as CSV if available
    if 'heights' in results and any('energies' in key for key in results.keys()):
        csv_data = {'height': results['heights']}
        
        for key, value in results.items():
            if 'energies' in key and isinstance(value, np.ndarray):
                csv_data[key] = value
        
        df = pd.DataFrame(csv_data)
        csv_path = output_dir / f"{filename}.csv"
        df.to_csv(csv_path, index=False)
    
    print(f"Results saved to {output_dir}")


def validate_pseudopotentials(pseudopotentials: Dict[str, str], pseudo_dir: str) -> bool:
    """
    Validate that all pseudopotential files exist.

    Args:
        pseudopotentials: Dictionary mapping elements to pseudopotential files
        pseudo_dir: Directory containing pseudopotential files

    Returns:
        True if all files exist, False otherwise
    """
    pseudo_dir = Path(pseudo_dir)
    
    for element, pseudo_file in pseudopotentials.items():
        pseudo_path = pseudo_dir / pseudo_file
        if not pseudo_path.exists():
            print(f"Warning: Pseudopotential file not found: {pseudo_path}")
            return False
    
    return True


def get_default_pseudopotentials() -> Dict[str, Dict[str, str]]:
    """
    Get default pseudopotential mappings for common elements.

    Returns:
        Dictionary with pseudopotential mappings for different functionals
    """
    return {
        'pbe': {
            'H': 'H.pbe-kjpaw_psl.1.0.0.UPF',
            'He': 'He.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Li': 'Li.pbe-s-kjpaw_psl.1.0.0.UPF',
            'C': 'C.pbe-n-kjpaw_psl.1.0.0.UPF',
            'N': 'N.pbe-n-kjpaw_psl.1.0.0.UPF',
            'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF',
            'F': 'F.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Na': 'Na.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Mg': 'Mg.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Al': 'Al.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Si': 'Si.pbe-n-kjpaw_psl.1.0.0.UPF',
            'P': 'P.pbe-n-kjpaw_psl.1.0.0.UPF',
            'S': 'S.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Cl': 'Cl.pbe-n-kjpaw_psl.1.0.0.UPF',
            'K': 'K.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Ca': 'Ca.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Ti': 'Ti.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'V': 'V.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Cr': 'Cr.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Mn': 'Mn.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Fe': 'Fe.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Co': 'Co.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Ni': 'Ni.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Cu': 'Cu.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Zn': 'Zn.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Ga': 'Ga.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'Ge': 'Ge.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'As': 'As.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Se': 'Se.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Br': 'Br.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Mo': 'Mo.pbe-spn-kjpaw_psl.1.0.0.UPF',
            'Ag': 'Ag.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Cd': 'Cd.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'In': 'In.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'Sn': 'Sn.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'Sb': 'Sb.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Te': 'Te.pbe-n-kjpaw_psl.1.0.0.UPF',
            'I': 'I.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Au': 'Au.pbe-n-kjpaw_psl.1.0.0.UPF',
            'Hg': 'Hg.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'Pb': 'Pb.pbe-dn-kjpaw_psl.1.0.0.UPF',
            'Bi': 'Bi.pbe-dn-kjpaw_psl.1.0.0.UPF',
        }
    }


def create_example_config() -> Dict[str, Any]:
    """
    Create an example configuration dictionary.

    Returns:
        Example configuration
    """
    return {
        'surface': {
            'material': 'Au',
            'crystal_structure': 'fcc',
            'miller_indices': [1, 1, 1],
            'size': [3, 3, 4],
            'vacuum': 14.0
        },
        'adsorbant': {
            'type': 'H2O',
            'orientation': 'flat'
        },
        'calculation': {
            'z_start': 2.0,
            'z_end': 8.0,
            'z_step': 0.2,
            'use_ml': True,
            'use_dft': True,
            'ml_models': ['omat', 'omc'],
            'dft_subset_factor': 2
        },
        'ml_settings': {
            'model': 'uma-s-1',
            'device': 'cuda'
        },
        'dft_settings': {
            'functional': 'pbe',
            'ecutwfc': 80,
            'ecutrho': 640,
            'kpts': [6, 6, 1],
            'occupations': 'smearing',
            'smearing': 'mp',
            'degauss': 0.01,
            'vdw_corr': 'grimme-d3',
            'conv_thr': 1e-8,
            'pseudo_dir': '/path/to/pseudopotentials'
        },
        'output': {
            'save_structures': True,
            'save_plots': True,
            'output_dir': './results',
            'plot_format': ['png', 'pdf']
        }
    }


def estimate_calculation_time(n_points: int, use_dft: bool = True, dft_subset_factor: int = 2) -> Tuple[float, str]:
    """
    Estimate total calculation time.

    Args:
        n_points: Number of height points
        use_dft: Whether DFT calculations are included
        dft_subset_factor: Factor to reduce DFT points

    Returns:
        Tuple of (time_in_minutes, formatted_string)
    """
    # Rough estimates
    ml_time_per_point = 0.5  # minutes
    dft_time_per_point = 5.0  # minutes
    
    ml_time = n_points * ml_time_per_point
    
    if use_dft:
        dft_points = n_points // dft_subset_factor
        dft_time = dft_points * dft_time_per_point
        total_time = ml_time + dft_time
        
        time_str = f"~{total_time:.0f} min ({ml_time:.0f} min ML + {dft_time:.0f} min DFT)"
    else:
        total_time = ml_time
        time_str = f"~{total_time:.0f} min (ML only)"
    
    return total_time, time_str
