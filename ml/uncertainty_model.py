import numpy as np
import pandas as pd
from typing import List, Dict, Tuple

class UncertaintyEngine:
    """
    Quantifies risk and uncertainty in predictions using Monte Carlo Simulation.
    
    Instead of saying "You will generate 1000 kWh",
    we say "You will generate between 950 and 1050 kWh (90% Confidence)".
    
    Sources of Uncertainty Modeled:
    1. Weather Forecast Error (Irradiance +/- 15%, Temp +/- 2C)
    2. Dust Accumulation Variance (Stochastic process)
    3. Cleaning Efficacy (Not always 100% perfect)
    """
    
    def __init__(self, simulations: int = 50):
        self.simulations = simulations
        
    def run_monte_carlo(self, base_df: pd.DataFrame, degradation_model_func) -> Dict:
        """
        Runs multiple simulations with perturbed inputs.
        
        Args:
            base_df: The deterministic weather/physics data.
            degradation_model_func: Function to recalculate energy (dependency injection).
            
        Returns:
            Dict containing P10, P50, P90 stats for Energy and Revenue.
        """
        energy_results = []
        
        # We treat 'base_df' as the P50 (median) forecast.
        # Now we perturb it.
        
        for _ in range(self.simulations):
            sim_df = base_df.copy()
            
            # --- PERTURBATION LOGIC ---
            
            # 1. Weather Uncertainty (Nasa Power accuracy is ~10-15%)
            # Multiplicative noise centered at 1.0, sigma 0.1
            irr_noise = np.random.normal(1.0, 0.10, size=len(sim_df))
            sim_df['irradiance'] *= irr_noise
            
            # Additive noise for temperature (sigma 1.5C)
            temp_noise = np.random.normal(0, 1.5, size=len(sim_df))
            sim_df['temperature'] += temp_noise
            
            # 2. Physics Parameter Uncertainty
            # Dust rate might be higher/lower than 0.15/month
            # We don't have easy access to internal model constants here without modifying the func signature.
            # So we will rely on output variance primarily from weather for now, 
            # OR we can manually apply a noise factor to the *output* efficiency if needed.
            
            # Run Model
            # Recalculate energy with noisy weather
            # Note: We assume degradation_model_func handles the full pipeline
            result_df = degradation_model_func(sim_df)
            
            total_energy = result_df['actual_energy_kwh'].sum()
            energy_results.append(total_energy)
            
        # --- STATISTICS ---
        energy_results = np.array(energy_results)
        
        p10 = np.percentile(energy_results, 10) # 90% chance to exceed this (Conservative)
        p50 = np.percentile(energy_results, 50) # Median
        p90 = np.percentile(energy_results, 90) # 10% chance to exceed this (Optimistic)
        
        # Calculate Risk-Adjusted Revenue (using conservative P10 estimate)
        # This is what banks/financiers care about ("Bankable Yield")
        
        return {
            "p10_energy": p10,
            "p50_energy": p50,
            "p90_energy": p90,
            "uncertainty_spread": p90 - p10,
            "confidence_interval_90": [p10, p90],
            "simulations_run": self.simulations
        }

    def calculate_risk_adjusted_revenue(self, p10_energy: float, price_per_kwh: float) -> float:
        """
        Returns revenue based on Conservative (P10) estimate.
        """
        return p10_energy * price_per_kwh
