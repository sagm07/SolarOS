"""
Section-Level Farm Optimizer

Divides solar farms into N×M grids and analyzes each section independently.
Optimizes cleaning schedule by prioritizing sections with highest ROI.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from degradation_model import calculate_energy_metrics


class FarmSection:
    """Represents one section of a farm grid"""
    
    def __init__(self, section_id: str, row: int, col: int, 
                 panel_area_m2: float, orientation_deg: float = 180,
                 shading_factor: float = 1.0, dust_multiplier: float = 1.0):
        self.id = section_id
        self.row = row
        self.col = col
        self.panel_area = panel_area_m2
        self.orientation = orientation_deg  # 0-360°, 180 = south
        self.shading = shading_factor  # 0.0-1.0, 1.0 = no shading
        self.dust_multiplier = dust_multiplier  # 0.8-1.5
        
        # Results (calculated later)
        self.energy_loss_kwh = 0.0
        self.energy_loss_percent = 0.0
        self.cleaning_cost = 0.0
        self.cleaning_priority = 0.0
        self.roi_score = 0.0
        
    def to_dict(self):
        return {
            'id': self.id,
            'row': self.row,
            'col': self.col,
            'panel_area_m2': self.panel_area,
            'orientation_deg': self.orientation,
            'shading_factor': self.shading,
            'dust_multiplier': self.dust_multiplier,
            'energy_loss_kwh': float(self.energy_loss_kwh),
            'energy_loss_percent': float(self.energy_loss_percent),
            'cleaning_cost': float(self.cleaning_cost),
            'roi_score': float(self.roi_score),
            'cleaning_priority': float(self.cleaning_priority),
        }


def generate_farm_grid(farm_size_mw: float, grid_rows: int, grid_cols: int) -> List[FarmSection]:
    """
    Generate N×M grid of farm sections with realistic variations
    
    Args:
        farm_size_mw: Farm capacity in MW
        grid_rows: Number of rows in grid
        grid_cols: Number of columns in grid
        
    Returns:
        List of FarmSection objects
    """
    total_area = farm_size_mw * 5000  # MW to m²
    section_area = total_area / (grid_rows * grid_cols)
    
    sections = []
    for row in range(grid_rows):
        for col in range(grid_cols):
            # Realistic variations
            # Edge sections have more shading from structures
            edge_penalty = 0.05 if (row == 0 or row == grid_rows-1 or 
                                    col == 0 or col == grid_cols-1) else 0
            shading = 1.0 - edge_penalty - np.random.uniform(0, 0.03)
            
            # Dust accumulation varies by position (wind patterns)
            # Prevailing wind from west → eastern sections accumulate less
            dust_base = 1.0
            dust_variation = (col / grid_cols) * 0.3  # 0-30% variation
            dust_multiplier = dust_base + np.random.uniform(-0.1, 0.1) - dust_variation * 0.5
            
            # Orientation varies slightly
            orientation = 180 + np.random.uniform(-5, 5)
            
            section = FarmSection(
                section_id=f"S{row}{col}",
                row=row,
                col=col,
                panel_area_m2=section_area,
                orientation_deg=orientation,
                shading_factor=max(0.7, shading),  # Min 70% efficiency
                dust_multiplier=np.clip(dust_multiplier, 0.8, 1.5)
            )
            sections.append(section)
    
    return sections


def calculate_section_energy_loss(section: FarmSection, df: pd.DataFrame,
                                   electricity_price: float = 6.0) -> FarmSection:
    """
    Calculate energy loss for a specific section
    
    Args:
        section: FarmSection to analyze
        df: Weather data DataFrame
        electricity_price: Price per kWh in INR
    """
    # Run degradation model for this section's panel area
    processed = calculate_energy_metrics(df.copy(), panel_area=section.panel_area, cleaning_dates=[])
    
    # Base recoverable energy
    base_recoverable = processed['recoverable_energy_kwh'].sum()
    
    # Apply section-specific modifiers
    section.energy_loss_kwh = base_recoverable * section.dust_multiplier * section.shading
    
    # Calculate as percentage of potential
    potential_energy = processed['potential_energy_kwh'].sum()
    if potential_energy > 0:
        section.energy_loss_percent = (section.energy_loss_kwh / potential_energy) * 100
    
    # Calculate cleaning cost (₹25 per 1000 m²)
    section.cleaning_cost = (section.panel_area / 1000) * 25
    
    # Calculate ROI
    energy_value = section.energy_loss_kwh * electricity_price
    if section.cleaning_cost > 0:
        section.roi_score = energy_value / section.cleaning_cost
    else:
        section.roi_score = 0
    
    # Priority = ROI score (higher = clean first)
    section.cleaning_priority = section.roi_score
    
    return section


def optimize_section_cleaning(sections: List[FarmSection], 
                              water_budget_liters: float) -> Tuple[List[FarmSection], float]:
    """
    Select which sections to clean based on water budget
    
    Uses greedy algorithm: sort by ROI, select until budget exhausted
    
    Returns:
        (selected_sections, water_used)
    """
    # Sort by cleaning priority (ROI) descending
    sorted_sections = sorted(sections, key=lambda s: s.cleaning_priority, reverse=True)
    
    selected = []
    water_used = 0.0
    
    for section in sorted_sections:
        # Water needed: 500L per 100m²
        section_water_need = (section.panel_area / 100) * 500
        
        if water_used + section_water_need <= water_budget_liters:
            selected.append(section)
            water_used += section_water_need
        # Stop when budget exhausted
    
    return selected, water_used


if __name__ == "__main__":
    # Test the section optimizer
    print("=== Section-Level Farm Analysis Test ===\n")
    
    # Generate 5×5 grid for 25 MW farm
    sections = generate_farm_grid(farm_size_mw=25, grid_rows=5, grid_cols=5)
    print(f"Generated {len(sections)} sections")
    print(f"Section area: {sections[0].panel_area:,.0f} m² each\n")
    
    # Fetch weather data
    from data_loader import fetch_nasa_power_data
    df = fetch_nasa_power_data(days=30)
    
    # Analyze each section
    print("Analyzing sections...")
    for section in sections:
        calculate_section_energy_loss(section, df)
    
    # Sort by priority
    sections.sort(key=lambda s: s.cleaning_priority, reverse=True)
    
    print("\nTop 5 Sections by ROI:")
    for i, section in enumerate(sections[:5], 1):
        print(f"{i}. {section.id}: {section.energy_loss_kwh:.0f} kWh loss, "
              f"ROI: {section.roi_score:.2f}, Priority: {section.cleaning_priority:.2f}")
    
    # Optimize with 25,000L budget
    budget = 25000
    selected, water_used = optimize_section_cleaning(sections, budget)
    
    print(f"\n=== Optimization with {budget:,}L Water Budget ===")
    print(f"Selected {len(selected)}/{len(sections)} sections")
    print(f"Water used: {water_used:,.0f}L")
    print(f"Total energy recovered: {sum(s.energy_loss_kwh for s in selected):,.0f} kWh")
    print(f"Total CO₂ saved: {sum(s.energy_loss_kwh for s in selected) * 0.7:,.0f} kg")
    print(f"\nSelected sections: {', '.join(s.id for s in selected)}")
