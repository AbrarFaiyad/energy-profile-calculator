"""
Plotting utilities for energy profiles.
"""

import numpy as np
import matplotlib
# Use non-interactive backend for headless environments
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class EnergyProfilePlotter:
    """
    Plotter class for creating beautiful energy profile visualizations.
    """
    
    def __init__(self, style: str = "seaborn"):
        """
        Initialize plotter with styling options.
        
        Args:
            style: Plotting style ("seaborn", "matplotlib", "publication")
        """
        self.style = style
        self._setup_style()
        
        # Define colors and markers for different methods
        self.colors = {
            'OMAT': '#2E86AB',
            'OMC': '#A23B72', 
            'DFT': '#F18F01',
            'ML': '#2E86AB',
            'Experiment': '#8B5A2B'
        }
        
        self.markers = {
            'OMAT': 'o',
            'OMC': 's', 
            'DFT': '^',
            'ML': 'o',
            'Experiment': 'D'
        }
    
    def _setup_style(self):
        """Setup plotting style."""
        if self.style == "seaborn":
            plt.style.use('default')
            sns.set_theme(style="whitegrid", palette="deep")
        elif self.style == "publication":
            plt.style.use('default')
            plt.rcParams.update({
                'font.size': 12,
                'axes.linewidth': 1.5,
                'xtick.major.width': 1.5,
                'ytick.major.width': 1.5,
                'xtick.minor.width': 1.0,
                'ytick.minor.width': 1.0,
                'legend.frameon': True,
                'legend.fancybox': True,
                'legend.shadow': True
            })
    
    def plot_energy_profile(self, heights: np.ndarray, 
                           energy_data: Dict[str, np.ndarray],
                           adsorbant: str,
                           surface: str,
                           save_path: Optional[str] = None,
                           formats: List[str] = ['png', 'pdf'],
                           **kwargs) -> plt.Figure:
        """
        Plot energy profile comparison.
        
        Args:
            heights: Array of heights above surface
            energy_data: Dictionary mapping method names to energy arrays
            adsorbant: Name of adsorbant molecule
            surface: Name of surface
            save_path: Path to save plot (without extension)
            formats: List of file formats to save
            **kwargs: Additional plotting options
            
        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (12, 8)))
        
        # Plot each energy profile
        for method, energies in energy_data.items():
            if np.any(~np.isnan(energies)):
                valid_mask = ~np.isnan(energies)
                
                # Plot line and markers
                ax.plot(heights[valid_mask], energies[valid_mask], 
                       color=self.colors.get(method, '#333333'),
                       marker=self.markers.get(method, 'o'),
                       markersize=8,
                       linewidth=3,
                       label=method,
                       alpha=0.8)
                
                # Add scatter points for better visibility
                ax.scatter(heights[valid_mask], energies[valid_mask], 
                          color=self.colors.get(method, '#333333'),
                          s=60,
                          alpha=0.9,
                          zorder=5,
                          edgecolors='white',
                          linewidth=1)
                
                # Find and annotate minimum
                min_idx = np.argmin(energies[valid_mask])
                min_height = heights[valid_mask][min_idx]
                min_energy = energies[valid_mask][min_idx]
                
                self._annotate_minimum(ax, method, min_height, min_energy)
        
        # Customize plot
        self._customize_plot(ax, heights, adsorbant, surface, **kwargs)
        
        # Save plot
        if save_path:
            self._save_plot(fig, save_path, formats)
        
        return fig
    
    def _annotate_minimum(self, ax: plt.Axes, method: str, height: float, energy: float):
        """Annotate minimum energy point."""
        offset_x = 0.5
        offset_y = 0.2 if method == 'OMC' else -0.2
        
        ax.annotate(f'{method} Min: {energy:.3f} eV\nat {height:.1f} Å', 
                    xy=(height, energy), 
                    xytext=(height + offset_x, energy + offset_y),
                    arrowprops=dict(arrowstyle='->', 
                                  color=self.colors.get(method, '#333333'), 
                                  alpha=0.7),
                    fontsize=10, 
                    bbox=dict(boxstyle="round,pad=0.3", 
                             facecolor=self.colors.get(method, '#333333'), 
                             alpha=0.3))
    
    def _customize_plot(self, ax: plt.Axes, heights: np.ndarray, 
                       adsorbant: str, surface: str, **kwargs):
        """Customize plot appearance."""
        # Labels and title
        ax.set_xlabel('Height above surface (Å)', fontsize=16, fontweight='bold')
        ax.set_ylabel('Energy (eV)', fontsize=16, fontweight='bold')
        ax.set_title(f'{adsorbant} adsorption energy profile on {surface}', 
                    fontsize=18, fontweight='bold', pad=20)
        
        # Legend
        ax.legend(frameon=True, fancybox=True, shadow=True, fontsize=14)
        
        # Grid and limits
        ax.grid(True, alpha=0.3)
        ax.set_xlim(heights.min() - 0.2, heights.max() + 0.2)
        
        # Horizontal line at y=0
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        
        # Styling
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.set_facecolor('#fafafa')
        
        # Border styling
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
            spine.set_color('#cccccc')
    
    def _save_plot(self, fig: plt.Figure, save_path: str, formats: List[str]):
        """Save plot in specified formats."""
        for fmt in formats:
            full_path = f"{save_path}.{fmt}"
            if fmt == 'pdf':
                fig.savefig(full_path, bbox_inches='tight')
            else:
                fig.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved as '{full_path}'")
    
    def plot_comparison_summary(self, results: Dict[str, Any], 
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a summary plot comparing different methods.
        
        Args:
            results: Dictionary containing calculation results
            save_path: Path to save plot
            
        Returns:
            Matplotlib figure object
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Extract data
        heights = results['heights']
        
        # Plot 1: Energy profiles
        for method, energies in results.items():
            if 'energies' in method:
                method_name = method.replace('_energies', '').upper()
                if np.any(~np.isnan(energies)):
                    valid_mask = ~np.isnan(energies)
                    ax1.plot(heights[valid_mask], energies[valid_mask], 
                            color=self.colors.get(method_name, '#333333'),
                            marker=self.markers.get(method_name, 'o'),
                            label=method_name, linewidth=2)
        
        ax1.set_xlabel('Height (Å)')
        ax1.set_ylabel('Energy (eV)')
        ax1.set_title('Energy Profiles Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Binding energies (minima)
        binding_energies = {}
        optimal_heights = {}
        
        for method, energies in results.items():
            if 'energies' in method:
                method_name = method.replace('_energies', '').upper()
                if np.any(~np.isnan(energies)):
                    valid_mask = ~np.isnan(energies)
                    min_idx = np.argmin(energies[valid_mask])
                    binding_energies[method_name] = -energies[valid_mask][min_idx]
                    optimal_heights[method_name] = heights[valid_mask][min_idx]
        
        methods = list(binding_energies.keys())
        binding_vals = list(binding_energies.values())
        
        bars = ax2.bar(methods, binding_vals, 
                      color=[self.colors.get(m, '#333333') for m in methods],
                      alpha=0.7)
        ax2.set_ylabel('Binding Energy (eV)')
        ax2.set_title('Binding Strength Comparison')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, val in zip(bars, binding_vals):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Plot 3: Optimal heights
        height_vals = list(optimal_heights.values())
        bars = ax3.bar(methods, height_vals,
                      color=[self.colors.get(m, '#333333') for m in methods],
                      alpha=0.7)
        ax3.set_ylabel('Optimal Height (Å)')
        ax3.set_title('Optimal Adsorption Heights')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, val in zip(bars, height_vals):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Plot 4: Energy ranges
        energy_ranges = {}
        for method, energies in results.items():
            if 'energies' in method:
                method_name = method.replace('_energies', '').upper()
                if np.any(~np.isnan(energies)):
                    valid_energies = energies[~np.isnan(energies)]
                    energy_ranges[method_name] = valid_energies.max() - valid_energies.min()
        
        range_vals = list(energy_ranges.values())
        bars = ax4.bar(methods, range_vals,
                      color=[self.colors.get(m, '#333333') for m in methods],
                      alpha=0.7)
        ax4.set_ylabel('Energy Range (eV)')
        ax4.set_title('Energy Profile Span')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, val in zip(bars, range_vals):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            self._save_plot(fig, f"{save_path}_summary", ['png', 'pdf'])
        
        return fig
    
    def create_method_comparison_table(self, results: Dict[str, Any]) -> str:
        """
        Create a formatted comparison table of different methods.
        
        Args:
            results: Dictionary containing calculation results
            
        Returns:
            Formatted table string
        """
        table_lines = []
        table_lines.append("=" * 80)
        table_lines.append("METHOD COMPARISON SUMMARY")
        table_lines.append("=" * 80)
        table_lines.append(f"{'Method':<10} {'Binding Energy (eV)':<18} {'Optimal Height (Å)':<18} {'Energy Range (eV)':<15}")
        table_lines.append("-" * 80)
        
        for method, energies in results.items():
            if 'energies' in method and np.any(~np.isnan(energies)):
                method_name = method.replace('_energies', '').upper()
                valid_energies = energies[~np.isnan(energies)]
                valid_heights = results['heights'][~np.isnan(energies)]
                
                min_idx = np.argmin(valid_energies)
                binding_energy = -valid_energies[min_idx]
                optimal_height = valid_heights[min_idx]
                energy_range = valid_energies.max() - valid_energies.min()
                
                table_lines.append(f"{method_name:<10} {binding_energy:<18.4f} {optimal_height:<18.1f} {energy_range:<15.4f}")
        
        table_lines.append("=" * 80)
        
        return "\n".join(table_lines)
