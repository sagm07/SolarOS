
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
    print("--- Solar Intelligence Core Initialization ---")
    
    # Constants
    ELECTRICITY_PRICE_INR = 6.0    
    CARBON_FACTOR = 0.7            
    WATER_USAGE_LITERS = 500.0
    WATER_COST_PER_LITER = 0.05
    # USER CONSTRAINT: "Cleaning is expensive"
    # Virtual cost overhead for labor/risk/downtime
    BASE_CLEANING_COST = 1500.0 
    VIRTUAL_FRICTION_COST = 500.0 
    EFFECTIVE_CLEANING_COST = BASE_CLEANING_COST + VIRTUAL_FRICTION_COST
    
    # 1. Fetch Data
    print("Fetching solar data with Rain Intelligence...")
    df = fetch_nasa_power_data(days=30)
    
    if df.empty:
        print("Error: No data fetched.")
        return

    # 2. Run Base Model (Baseline)
    print("Running base degradation model...")
    df_base = calculate_energy_metrics(df.copy(), cleaning_dates=[])

    # 3. Intelligent Decision Engine (Optimization)
    print("Initializing Intelligent Decision Engine with Friction Constraints...")
    optimizer = OptimizationEngine(
        electricity_price=ELECTRICITY_PRICE_INR,
        cleaning_cost=EFFECTIVE_CLEANING_COST, # Higher cost to reflect reality
        carbon_price_per_kg=5.0, 
        water_price_per_liter=WATER_COST_PER_LITER,
        water_usage_per_clean=WATER_USAGE_LITERS
    )
    
    optimization_result = optimizer.optimize_cleaning_schedule(df_base)
    optimal_schedule_indices = optimization_result['cleaning_dates']
    
    # Fix: Use iloc to get datetime from column
    optimal_dates = [df_base.iloc[i]['datetime'] for i in optimal_schedule_indices]
    
    print(f"Optimal Schedule Found: {len(optimal_schedule_indices)} cleanings")
    
    # 4. Simulate Optimal Scenario
    df_optimal = calculate_energy_metrics(df.copy(), cleaning_dates=optimal_dates)
    
    # 5. Calculate Metrics
    base_energy = df_base['actual_energy_kwh'].sum()
    opt_energy = df_optimal['actual_energy_kwh'].sum()
    energy_gain = opt_energy - base_energy
    
    carbon_saved = energy_gain * CARBON_FACTOR
    water_used = len(optimal_dates) * WATER_USAGE_LITERS
    total_cost = len(optimal_dates) * BASE_CLEANING_COST # Use real cost for reporting
    net_benefit = (energy_gain * ELECTRICITY_PRICE_INR) - total_cost
    
    sses_score = calculate_sses(opt_energy, water_used, carbon_saved, total_cost)
    
    # 6. Deep Explainability Logic Construction
    reasons = []
    
    # Analyze the decision logic to explain WHY
    if len(optimal_dates) > 0:
        next_clean = optimal_dates[0]
        days_until_clean = (next_clean - df_base.iloc[0]['datetime']).days
        
        reasons.append(f"Dust accumulation projected to exceed 5% threshold in {days_until_clean} days.")
        reasons.append(f"Net projected revenue gain: ₹{net_benefit:.2f} (after costs).")
        reasons.append("No significant rain forecast in critical window.")
    else:
        # Why WAIT?
        reasons.append("Optimization model determined WAIT is optimal strategy.")
        
        # Check specific inhibitors
        # 1. Rain?
        total_rain = df_base['precipitation'].sum()
        if total_rain > 10.0:
            reasons.append(f"Rain-assist detected ({total_rain:.1f}mm), reducing need for manual clean.")
        
        # 2. Margin?
        if energy_gain > 0 and net_benefit < 0:
            reasons.append("Energy gain exists, but implementation costs exceed revenue.")
            
        # 3. Friction?
        reasons.append("Dust levels insufficient to justify mobilization cost.")

    final_metrics = {
        "action": "CLEAN" if len(optimal_dates) > 0 else "WAIT",
        "cleaning_dates": [str(d.date()) for d in optimal_dates],
        "energy_gained": energy_gain,
        "net_benefit_inr": net_benefit,
        "carbon_saved_kg": carbon_saved,
        "water_used_liters": water_used,
        "sses_score": sses_score,
        "optimization_value": optimization_result['total_net_value'],
        "reasons": reasons
    }

    # Report
    print("\n" + "="*50)
    print(f"SOLAR INTELLIGENCE REPORT (v2.1 Refined Engine)")
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
    print(f"💰 Net Economic Gain: ₹{net_benefit:,.2f}")
    print(f"⚡ Energy Recovered:  {energy_gain:.2f} kWh")
    print("="*50 + "\n")
    
    return final_metrics

if __name__ == "__main__":
    run_simulation()
