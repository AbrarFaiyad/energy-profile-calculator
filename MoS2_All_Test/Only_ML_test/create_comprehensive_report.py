#!/usr/bin/env python3
"""
Comprehensive MoS2 Adsorbant Energy Profile Plotter

This script creates a comprehensive PDF report with all energy profiles
plotted separately for easy comparison and analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import matplotlib.backends.backend_pdf as pdf
from matplotlib.gridspec import GridSpec
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import yaml

# Set style for beautiful plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.alpha'] = 0.3

class MoS2EnergyProfilePlotter:
    def __init__(self, results_dir: str = "ml_test_results"):
        self.results_dir = Path(results_dir)
        self.all_data = {}
        self.adsorbant_categories = {
            'Metal Dimers': ['Au2', 'Ag2', 'Pt2', 'Pd2', 'Cu2', 'Fe2', 'Co2', 'Ni2', 'Mn2', 
                           'Ir2', 'Rh2', 'Re2', 'Ru2', 'Cd2', 'Al2', 'Zn2', 'Nb2', 'W2', 'Ta2', 'V2', 'C2'],
            'Single Atoms': ['Li', 'Na', 'P', 'N', 'B', 'Si', 'F', 'Cl', 'S', 'Se', 'Te', 'O'],
            'Organic Molecules': ['F4TCNQ', 'PTCDA', 'tetracene', 'TCNQ', 'TCNE', 'TTF', 'BV'],
            'Metal Oxides': ['ZnO', 'TiO2']
        }
        
    def load_all_data(self):
        """Load all available CSV files"""
        print("📂 Loading energy profile data...")
        
        for adsorbant_dir in self.results_dir.iterdir():
            if adsorbant_dir.is_dir():
                csv_file = adsorbant_dir / f"{adsorbant_dir.name.replace('_on_MoS2', '')}_MoS2_profile.csv"
                
                if csv_file.exists():
                    try:
                        df = pd.read_csv(csv_file)
                        adsorbant = adsorbant_dir.name.replace('_on_MoS2', '')
                        self.all_data[adsorbant] = df
                        print(f"  ✅ Loaded {adsorbant}: {len(df)} data points")
                    except Exception as e:
                        print(f"  ❌ Error loading {csv_file}: {e}")
        
        print(f"\n📊 Total datasets loaded: {len(self.all_data)}")
        
    def get_adsorbant_category(self, adsorbant: str) -> str:
        """Get the category of an adsorbant"""
        for category, adsorbants in self.adsorbant_categories.items():
            if adsorbant in adsorbants:
                return category
        return 'Other'
    
    def calculate_binding_energy(self, omat_energies: np.ndarray, omc_energies: np.ndarray) -> np.ndarray:
        """Calculate binding energy as the more negative of OMAT and OMC"""
        return np.minimum(omat_energies, omc_energies)
    
    def find_optimal_height(self, heights: np.ndarray, energies: np.ndarray) -> Tuple[float, float]:
        """Find optimal adsorption height and energy"""
        min_idx = np.argmin(energies)
        return heights[min_idx], energies[min_idx]
    
    def create_title_page(self, pdf_pages):
        """Create a beautiful title page"""
        fig = plt.figure(figsize=(12, 8))
        fig.patch.set_facecolor('white')
        
        # Main title
        plt.text(0.5, 0.7, 'MoS₂ Adsorbant Energy Profiles', 
                fontsize=32, weight='bold', ha='center', va='center',
                transform=fig.transFigure)
        
        # Subtitle
        plt.text(0.5, 0.6, 'Comprehensive ML-Based Adsorption Study', 
                fontsize=18, ha='center', va='center', style='italic',
                transform=fig.transFigure)
        
        # Statistics
        total_adsorbants = len(self.all_data)
        categories = set(self.get_adsorbant_category(ads) for ads in self.all_data.keys())
        
        stats_text = f"""
Dataset Overview:
• Total Adsorbants: {total_adsorbants}
• Categories: {', '.join(sorted(categories))}
• ML Calculators: OMAT & OMC
• Surface: MoS₂ (2D material)
• Height Range: 2.0 - 8.5 Å
        """
        
        plt.text(0.5, 0.4, stats_text, 
                fontsize=14, ha='center', va='center',
                transform=fig.transFigure,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.3))
        
        # Date
        from datetime import datetime
        plt.text(0.5, 0.1, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
                fontsize=12, ha='center', va='center',
                transform=fig.transFigure)
        
        plt.axis('off')
        pdf_pages.savefig(fig, bbox_inches='tight')
        plt.close()
    
    def create_summary_page(self, pdf_pages):
        """Create a summary page with optimal binding energies"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('MoS₂ Adsorption Summary', fontsize=20, weight='bold')
        
        # Prepare data for summary plots
        summary_data = []
        for adsorbant, df in self.all_data.items():
            binding_energy = self.calculate_binding_energy(df['omat_energies'].values, df['omc_energies'].values)
            opt_height, opt_energy = self.find_optimal_height(df['height'].values, binding_energy)
            
            summary_data.append({
                'adsorbant': adsorbant,
                'category': self.get_adsorbant_category(adsorbant),
                'optimal_height': opt_height,
                'binding_energy': opt_energy
            })
        
        summary_df = pd.DataFrame(summary_data)
        
        # 1. Binding energies by category
        categories = summary_df['category'].unique()
        colors = sns.color_palette("husl", len(categories))
        
        for i, category in enumerate(categories):
            cat_data = summary_df[summary_df['category'] == category]
            ax1.scatter(cat_data['adsorbant'], cat_data['binding_energy'], 
                       label=category, color=colors[i], s=100, alpha=0.7)
        
        ax1.set_ylabel('Binding Energy (eV)')
        ax1.set_title('Optimal Binding Energies by Category')
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Optimal heights by category
        for i, category in enumerate(categories):
            cat_data = summary_df[summary_df['category'] == category]
            ax2.scatter(cat_data['adsorbant'], cat_data['optimal_height'], 
                       label=category, color=colors[i], s=100, alpha=0.7)
        
        ax2.set_ylabel('Optimal Height (Å)')
        ax2.set_title('Optimal Adsorption Heights by Category')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Binding energy distribution
        ax3.hist(summary_df['binding_energy'], bins=15, alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Binding Energy (eV)')
        ax3.set_ylabel('Count')
        ax3.set_title('Binding Energy Distribution')
        ax3.grid(True, alpha=0.3)
        
        # 4. Height vs binding energy correlation
        ax4.scatter(summary_df['optimal_height'], summary_df['binding_energy'], 
                   c=[colors[list(categories).index(cat)] for cat in summary_df['category']], 
                   s=100, alpha=0.7)
        ax4.set_xlabel('Optimal Height (Å)')
        ax4.set_ylabel('Binding Energy (eV)')
        ax4.set_title('Height vs Binding Energy Correlation')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        pdf_pages.savefig(fig, bbox_inches='tight')
        plt.close()
    
    def plot_individual_profiles(self, pdf_pages):
        """Create individual energy profile plots for each adsorbant"""
        print("📈 Creating individual energy profile plots...")
        
        # Sort adsorbants by category for better organization
        sorted_adsorbants = []
        for category in self.adsorbant_categories.keys():
            category_ads = [ads for ads in self.all_data.keys() 
                          if self.get_adsorbant_category(ads) == category]
            sorted_adsorbants.extend(sorted(category_ads))
        
        # Add any remaining adsorbants
        remaining = [ads for ads in self.all_data.keys() if ads not in sorted_adsorbants]
        sorted_adsorbants.extend(sorted(remaining))
        
        for adsorbant in sorted_adsorbants:
            df = self.all_data[adsorbant]
            category = self.get_adsorbant_category(adsorbant)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            fig.suptitle(f'{adsorbant} on MoS₂ - {category}', fontsize=16, weight='bold')
            
            heights = df['height'].values
            omat_energies = df['omat_energies'].values
            omc_energies = df['omc_energies'].values
            binding_energy = self.calculate_binding_energy(omat_energies, omc_energies)
            
            # Plot 1: OMAT and OMC energies separately
            ax1.plot(heights, omat_energies, 'o-', label='OMAT', linewidth=2, markersize=6)
            ax1.plot(heights, omc_energies, 's-', label='OMC', linewidth=2, markersize=6)
            
            ax1.set_xlabel('Height above MoS₂ (Å)')
            ax1.set_ylabel('Energy (eV)')
            ax1.set_title('OMAT vs OMC Energy Profiles')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Find and mark optimal points
            opt_height_omat, opt_energy_omat = self.find_optimal_height(heights, omat_energies)
            opt_height_omc, opt_energy_omc = self.find_optimal_height(heights, omc_energies)
            
            ax1.plot(opt_height_omat, opt_energy_omat, 'ro', markersize=10, 
                    label=f'OMAT Min: {opt_energy_omat:.3f} eV @ {opt_height_omat:.2f} Å')
            ax1.plot(opt_height_omc, opt_energy_omc, 'bs', markersize=10,
                    label=f'OMC Min: {opt_energy_omc:.3f} eV @ {opt_height_omc:.2f} Å')
            
            # Plot 2: Combined binding energy
            ax2.plot(heights, binding_energy, 'o-', color='green', linewidth=3, markersize=6)
            ax2.fill_between(heights, binding_energy, alpha=0.3, color='green')
            
            opt_height_bind, opt_energy_bind = self.find_optimal_height(heights, binding_energy)
            ax2.plot(opt_height_bind, opt_energy_bind, 'ro', markersize=12)
            
            ax2.set_xlabel('Height above MoS₂ (Å)')
            ax2.set_ylabel('Binding Energy (eV)')
            ax2.set_title(f'Binding Energy Profile\nOptimal: {opt_energy_bind:.3f} eV @ {opt_height_bind:.2f} Å')
            ax2.grid(True, alpha=0.3)
            
            # Add statistics box
            stats_text = f"""Statistics:
Min OMAT: {np.min(omat_energies):.3f} eV
Min OMC: {np.min(omc_energies):.3f} eV
Binding Energy: {opt_energy_bind:.3f} eV
Height Range: {np.min(heights):.1f} - {np.max(heights):.1f} Å
Data Points: {len(heights)}"""
            
            ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, 
                    verticalalignment='top', fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.8))
            
            plt.tight_layout()
            pdf_pages.savefig(fig, bbox_inches='tight')
            plt.close()
            
            print(f"  ✅ Plotted {adsorbant}")
    
    def create_category_comparison(self, pdf_pages):
        """Create comparison plots by category"""
        print("📊 Creating category comparison plots...")
        
        for category, adsorbants in self.adsorbant_categories.items():
            available_ads = [ads for ads in adsorbants if ads in self.all_data]
            
            if not available_ads:
                continue
                
            # Calculate number of subplots needed
            n_ads = len(available_ads)
            if n_ads == 0:
                continue
                
            ncols = min(3, n_ads)
            nrows = (n_ads + ncols - 1) // ncols
            
            fig, axes = plt.subplots(nrows, ncols, figsize=(6*ncols, 4*nrows))
            fig.suptitle(f'{category} on MoS₂ - Binding Energy Comparison', 
                        fontsize=16, weight='bold')
            
            if nrows == 1 and ncols == 1:
                axes = [axes]
            elif nrows == 1:
                axes = axes.flatten()
            else:
                axes = axes.flatten()
            
            for i, adsorbant in enumerate(available_ads):
                df = self.all_data[adsorbant]
                heights = df['height'].values
                omat_energies = df['omat_energies'].values
                omc_energies = df['omc_energies'].values
                binding_energy = self.calculate_binding_energy(omat_energies, omc_energies)
                
                ax = axes[i]
                ax.plot(heights, binding_energy, 'o-', linewidth=2, markersize=4)
                ax.fill_between(heights, binding_energy, alpha=0.3)
                
                # Mark optimal point
                opt_height, opt_energy = self.find_optimal_height(heights, binding_energy)
                ax.plot(opt_height, opt_energy, 'ro', markersize=8)
                
                ax.set_title(f'{adsorbant}\n{opt_energy:.3f} eV @ {opt_height:.2f} Å')
                ax.set_xlabel('Height (Å)')
                ax.set_ylabel('Binding Energy (eV)')
                ax.grid(True, alpha=0.3)
            
            # Hide unused subplots
            for i in range(n_ads, len(axes)):
                axes[i].set_visible(False)
            
            plt.tight_layout()
            pdf_pages.savefig(fig, bbox_inches='tight')
            plt.close()
            
            print(f"  ✅ Created {category} comparison")
    
    def generate_comprehensive_report(self, output_file: str = "MoS2_Energy_Profiles_Report.pdf"):
        """Generate the complete PDF report"""
        print(f"🎨 Generating comprehensive PDF report: {output_file}")
        print("=" * 60)
        
        # Load all data
        self.load_all_data()
        
        if not self.all_data:
            print("❌ No data found! Make sure the results directory contains CSV files.")
            return
        
        # Create PDF
        with pdf.PdfPages(output_file) as pdf_pages:
            # Title page
            print("📄 Creating title page...")
            self.create_title_page(pdf_pages)
            
            # Summary page
            print("📊 Creating summary page...")
            self.create_summary_page(pdf_pages)
            
            # Individual profiles
            self.plot_individual_profiles(pdf_pages)
            
            # Category comparisons
            self.create_category_comparison(pdf_pages)
        
        print("=" * 60)
        print(f"🎉 Report generated successfully: {output_file}")
        print(f"📋 Total pages: {len(self.all_data) + 3}")  # +3 for title, summary, and category pages
        print(f"📊 Adsorbants plotted: {len(self.all_data)}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate comprehensive MoS2 energy profile PDF report')
    parser.add_argument('--results-dir', default='ml_test_results',
                       help='Directory containing results (default: ml_test_results)')
    parser.add_argument('--output', default='MoS2_Energy_Profiles_Report.pdf',
                       help='Output PDF file name (default: MoS2_Energy_Profiles_Report.pdf)')
    
    args = parser.parse_args()
    
    plotter = MoS2EnergyProfilePlotter(args.results_dir)
    plotter.generate_comprehensive_report(args.output)


if __name__ == "__main__":
    main()
