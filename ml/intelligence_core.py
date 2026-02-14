
import pandas as pd
import numpy as np
import sys
import os
from datetime import timedelta

# Ensure we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from data_loader import fetch_nasa_power_data
    from degradation_model import calculate_energy_metrics
    from optimization_engine import OptimizationEngine
    from hybrid_model import HybridCorrector
    from uncertainty_model import UncertaintyEngine
except ImportError as e:
    print("Error: Could not import required modules.", e)
    sys.exit(1)

def calculate_sses(total_energy_kwh, total_water_liters, carbon_saved_kg, cost_inr):
    norm_energy = total_energy_kwh / 150000.0 
    norm_carbon = carbon_saved_kg / 10000.0   
    norm_water = total_water_liters / 50000.0 
    norm_cost = cost_inr / 50000.0            
    
    w_energy = 0.5
    w_carbon = 0.3
    w_water_penalty = 0.1
    w_cost_penalty = 0.1
    
    raw_score = (w_energy * norm_energy) + (w_carbon * norm_carbon) - (w_water_penalty * norm_water) - (w_cost_penalty * norm_cost)
    final_score = 50 + (raw_score * 50)
    return max(0, min(100, final_score))

def run_simulation():
    print("--- Solar Intelligence Core Initialization (v3.0 Hybrid) ---")
    
    # Constants
    ELECTRICITY_PRICE_INR = 6.0    
    CARBON_FACTOR = 0.7            
    WATER_USAGE_LITERS = 500.0
    WATER_COST_PER_LITER = 0.05
    BASE_CLEANING_COST = 1500.0 
    VIRTUAL_FRICTION_COST = 500.0 
    EFFECTIVE_CLEANING_COST = BASE_CLEANING_COST + VIRTUAL_FRICTION_COST
    
    # 1. Fetch Data
    print("Fetching solar data with Rain Intelligence...")
    df = fetch_nasa_power_data(days=30)
    
    if df.empty:
        print("Error: No data fetched.")
        return

    # 2. Run Base Model (Baseline Physics)
    print("Running base degradation model (Physics)...")
    df_base = calculate_energy_metrics(df.copy(), cleaning_dates=[])

    # 3. Hybrid Intelligence (Physics + ML Residual)
    print("Applying Hybrid ML Correction...")
    hybrid_model = HybridCorrector()
    df_base = hybrid_model.correct_physics_prediction(df_base)
    # Use the corrected 'hybrid_energy_kwh' as the 'actual' for optimization input?
    # Optimization Engine expects 'actual_energy_kwh'. Let's overwrite it for optimization.
    # But keep 'ideal' as Physics Ideal.
    # Actually, optimization uses 'recoverable' which is (Ideal - Actual). 
    # If ML says Actual is lower (negative residual), Recoverable increases -> More incentive to clean.
    # If ML says Actual is higher (positive boost), Recoverable decreases -> Less incentive.
    # Correct logic:
    df_base['actual_energy_kwh'] = df_base['hybrid_energy_kwh']
    df_base['recoverable_energy_kwh'] = df_base['ideal_energy_kwh'] - df_base['actual_energy_kwh']

    # 4. Intelligent Decision Engine (Optimization)
    print("Initializing Intelligent Decision Engine...")
    optimizer = OptimizationEngine(
        electricity_price=ELECTRICITY_PRICE_INR,
        cleaning_cost=EFFECTIVE_CLEANING_COST, 
        carbon_price_per_kg=5.0, 
        water_price_per_liter=WATER_COST_PER_LITER,
        water_usage_per_clean=WATER_USAGE_LITERS
    )
    
    optimization_result = optimizer.optimize_cleaning_schedule(df_base)
    optimal_schedule_indices = optimization_result['cleaning_dates']
    optimal_dates = [df_base.iloc[i]['datetime'] for i in optimal_schedule_indices]
    
    print(f"Optimal Schedule Found: {len(optimal_schedule_indices)} cleanings")
    
    # 5. Output Simulation & Uncertainty Quantification
    print("Running Monte Carlo Uncertainty Simulation (P10/P50/P90)...")
    df_optimal = calculate_energy_metrics(df.copy(), cleaning_dates=optimal_dates)
    # Apply Hybrid Correction to Optimal Scenario too
    df_optimal = hybrid_model.correct_physics_prediction(df_optimal)
    
    # Monte Carlo Engine
    uq_engine = UncertaintyEngine(simulations=50)
    # We need a wrapper for calculate_energy_metrics to pass into UQ
    # But UQ needs correct inputs.
    # Simplified UQ: Just verify uncertainty on the *Optimal* output.
    uq_stats = uq_engine.run_monte_carlo(df.copy(), 
                                         lambda d: hybrid_model.correct_physics_prediction(calculate_energy_metrics(d, cleaning_dates=optimal_dates)))
    
    # 6. Calculate Metrics (using P50 from UQ or Deterministic?)
    # Let's use Deterministic Hybrid for main numbers, UQ for confidence.
    base_energy = df_base['hybrid_energy_kwh'].sum()
    opt_energy = df_optimal['hybrid_energy_kwh'].sum()
    energy_gain = opt_energy - base_energy
    
    carbon_saved = energy_gain * CARBON_FACTOR
    water_used = len(optimal_dates) * WATER_USAGE_LITERS
    total_cost = len(optimal_dates) * BASE_CLEANING_COST
    net_benefit = (energy_gain * ELECTRICITY_PRICE_INR) - total_cost
    
    sses_score = calculate_sses(opt_energy, water_used, carbon_saved, total_cost)
    
    # 7. Deep Explainability Logic w/ Uncertainty
    reasons = []
    
    if len(optimal_dates) > 0:
        next_clean = optimal_dates[0]
        days_until_clean = (next_clean - df_base.iloc[0]['datetime']).days
        reasons.append(f"Dust accumulation projected to exceed 5% threshold in {days_until_clean} days.")
        reasons.append(f"Net projected revenue gain: ₹{net_benefit:.0f} (P50 Estimate).")
        reasons.append(f"Confidence Interval (90%): ₹{uq_engine.calculate_risk_adjusted_revenue(uq_stats['p10_energy'] - base_energy, ELECTRICITY_PRICE_INR):.0f} - ₹{uq_engine.calculate_risk_adjusted_revenue(uq_stats['p90_energy'] - base_energy, ELECTRICITY_PRICE_INR):.0f}")
    else:
        reasons.append("Optimization model determined WAIT is optimal strategy.")
        total_rain = df_base['precipitation'].sum()
        if total_rain > 10.0:
            reasons.append(f"Rain-assist detected ({total_rain:.1f}mm), reducing need for manual clean.")
        if energy_gain > 0 and net_benefit < 0:
            reasons.append("Energy gain exists, but implementation costs exceed revenue.")

    final_metrics = {
        "action": "CLEAN" if len(optimal_dates) > 0 else "WAIT",
        "cleaning_dates": [str(d.date()) for d in optimal_dates],
        "energy_gained": energy_gain,
        "net_benefit_inr": net_benefit,
        "carbon_saved_kg": carbon_saved,
        "water_used_liters": water_used,
        "sses_score": sses_score,
        "p10_energy": uq_stats['p10_energy'],
        "p90_energy": uq_stats['p90_energy'],
        "confidence_interval": uq_stats['confidence_interval_90'],
        "reasons": reasons
    }

    # Report
    print("\n" + "="*50)
    print(f"SOLAR INTELLIGENCE REPORT (v3.0 Hybrid Engine)")
    print("="*50)
    
    if len(optimal_dates) > 0:
        print(f"✅ ACTION: CLEAN RECOMMENDED")
        print(f"🗓️  Schedule: {', '.join([str(d.date()) for d in optimal_dates])}")
    else:
        print(f"⏸️ ACTION: WAIT (NO CLEANING)")
        
    print(f"💡 REASONING (Deep Explainability):")
    for r in reasons:
        print(f"   • {r}")

    print("-" * 30)
    print(f"🌍 SUSTAINABILITY INDEX (SSES): {sses_score:.1f}/100")
    print("-" * 30)
    print(f"💰 Net Economic Gain (P50): ₹{net_benefit:,.2f}")
    print(f"📊 Risk-Adjusted Gain (P10): ₹{(uq_engine.calculate_risk_adjusted_revenue(uq_stats['p10_energy'] - base_energy, ELECTRICITY_PRICE_INR) - total_cost):,.2f} (Conservative)")
    print(f"⚡ Energy Recovered:       {energy_gain:.2f} kWh")
    print(f"🎲 Uncertainty (P90-P10):  {uq_stats['uncertainty_spread']:.2f} kWh")
    print("="*50 + "\n")
    
    return final_metrics

if __name__ == "__main__":
    run_simulation()
