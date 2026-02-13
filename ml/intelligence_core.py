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
    from scenario_analysis import get_recommended_cleaning_date
except ImportError as e:
    print("Error: Could not import required modules.", e)
    sys.exit(1)

def run_simulation():
    print("--- Solar Intelligence Core Initialization ---")
    
    # Constants
    ELECTRICITY_PRICE_INR = 6.0    # per kWh
    CARBON_FACTOR = 0.7            # kg CO2 per kWh
    WATER_USAGE_LITERS = 500.0
    WATER_COST_PER_LITER = 0.05
    CLEANING_COST_INR = WATER_USAGE_LITERS * WATER_COST_PER_LITER # Total cost per cleaning
    
    # 1. Fetch Data
    # Fetch 30 days of data
    print("Fetching solar data...")
    df = fetch_nasa_power_data(days=30)
    
    if df.empty:
        print("Error: No data fetched.")
        return

    # 2. Run Base Model (No Cleaning)
    print("Running base degradation model...")
    df_base = calculate_energy_metrics(df.copy(), cleaning_dates=[])

    # 3. Analyze for Cleaning Opportunity (predictive: projected 7-day recoverable > cost)
    print("Analyzing cleaning opportunities (7-day projected recoverable vs cost)...")
    
    # Check for Rain Forecast First (Operational Efficiency)
    from rain_model import check_rain_forecast_wait
    should_wait_rain, rain_reason = check_rain_forecast_wait(df.copy())
    
    if should_wait_rain:
        if isinstance(rain_reason, dict):
             print(f"Decision: {rain_reason.get('decision', 'WAIT')}")
             print("Reason:")
             print(f"• {rain_reason.get('rain_mm', 0):.1f} mm rain forecasted in next 48 hours")
             print(f"• Estimated natural dust reduction: {rain_reason.get('dust_reduction_estimate', 0):.0%}")
             print(f"• Cleaning now would waste {rain_reason.get('water_saved_estimate_liters', 0):,.0f} L water")
             print(f"• Net sustainability score improves by waiting")
        else:
             print(f"Decision: WAIT ({rain_reason})")
             
        cleaning_needed = False
        cleaning_date = None
    else:
        cleaning_date = get_recommended_cleaning_date(
            df.copy(),
            electricity_price_inr=ELECTRICITY_PRICE_INR,
            cleaning_cost_inr=CLEANING_COST_INR,
        )
        cleaning_needed = cleaning_date is not None
        
        if cleaning_needed:
            print(f"Cleaning opportunity detected on: {cleaning_date.date()}")
        else:
            print("No cleaning opportunity detected (Projected 7-day recoverable value < Cleaning Cost).")

    # 4. Final Decision & Metrics
    final_metrics = {}
    
    # Scaling constant
    SCALED_1MW_PANEL_AREA_M2 = 5000.0
    REFERENCE_PANEL_AREA_M2 = 100.0
    scale_factor = SCALED_1MW_PANEL_AREA_M2 / REFERENCE_PANEL_AREA_M2

    if cleaning_needed:
        # Simulate with cleaning
        print(f"Simulating scenario with cleaning on {cleaning_date.date()}...")
        # We assume cleaning happens at the start of that day (or end of previous).
        # Let's say we clean on that morning.
        df_clean = calculate_energy_metrics(df.copy(), cleaning_dates=[cleaning_date])
        
        # Calculate totals for the simulation period
        # Note: recovering energy only makes sense if we compare to baseline
        
        # Value Gained = (Energy with cleaning - Energy without cleaning)
        energy_no_clean = df_base['actual_energy_kwh'].sum()
        energy_with_clean = df_clean['actual_energy_kwh'].sum()
        
        energy_gained = energy_with_clean - energy_no_clean
        value_gained = energy_gained * ELECTRICITY_PRICE_INR
        net_benefit = value_gained - CLEANING_COST_INR
        
        carbon_saved = energy_gained * CARBON_FACTOR
        
        # Recoverable energy from df_clean is what is still lost even after cleaning 
        # (e.g. due to subsequent dust buildup or temp)
        remaining_recoverable = df_clean['recoverable_energy_kwh'].sum()
        
        # New Metrics
        water_efficiency = energy_gained / WATER_USAGE_LITERS if WATER_USAGE_LITERS > 0 else 0
        scaled_net_benefit = net_benefit * scale_factor

        final_metrics = {
            "action": "CLEAN",
            "cleaning_date": str(cleaning_date.date()),
            "energy_recoverable": remaining_recoverable, 
            "energy_gained": energy_gained,
            "net_benefit_inr": net_benefit,
            "carbon_saved_kg": carbon_saved,
            "water_cost_inr": CLEANING_COST_INR,
            "water_efficiency_kwh_l": water_efficiency,
            "scaled_net_benefit_1mw": scaled_net_benefit
        }
    else:
        # No cleaning recommended
        total_recoverable = df_base['recoverable_energy_kwh'].sum()
        carbon_potential = total_recoverable * CARBON_FACTOR
        
        final_metrics = {
            "action": "WAIT",
            "cleaning_date": None,
            "energy_recoverable": total_recoverable,
            "energy_gained": 0.0,
            "net_benefit_inr": 0.0, # Or negative if we forced cleaning
            "carbon_saved_kg": 0.0, # You save 0 extra by doing nothing, but you are losing 'carbon_potential'
            "water_cost_inr": 0.0,
            "water_efficiency_kwh_l": 0.0,
            "scaled_net_benefit_1mw": 0.0
        }
        
    # 5. Print Summary
    print("\n" + "="*40)
    print(f"SOLAR INTELLIGENCE REPORT")
    print("="*40)
    print(f"Recommended Action: {final_metrics['action']}")
    
    if final_metrics['action'] == "CLEAN":
         print(f"Logic Trigger: Projected 7-day recoverable value > Cleaning Cost")
         print(f"Proposed Date: {final_metrics['cleaning_date']}")
         print("-" * 20)
         print(f"Net Benefit (100m²): ₹{final_metrics['net_benefit_inr']:.2f}")
         print(f"Energy Gained: {final_metrics['energy_gained']:.2f} kWh")
         print(f"Carbon Saved: {final_metrics['carbon_saved_kg']:.2f} kg CO2")
         print("-" * 20)
         print(f"SCALED IMPACT (1 MW / ~5000m²):")
         print(f"Net Gain per Cycle: ₹{final_metrics['scaled_net_benefit_1mw']:,.0f}")
         print("-" * 20)
         print(f"WATER EFFICIENCY:")
         print(f"Maximize renewable output per liter: {final_metrics['water_efficiency_kwh_l']:.4f} kWh/L")
    else:
         print(f"Logic: Projected 7-day recoverable value ({final_metrics.get('projected_recoverable', 'N/A')}) < Cleaning Cost")
         print(f"Energy Recoverable (Potential): {final_metrics['energy_recoverable']:.2f} kWh")
         print(f"Carbon Potential: {final_metrics['energy_recoverable'] * CARBON_FACTOR:.2f} kg CO2")
         print(f"Water Cost: ₹0.00")
         
    # Asset Health Section
    print("-" * 40)
    print("ASSET HEALTH MONITOR (New)")
    # Get latest values from df_base (or df_clean if exists, but base is fine for status)
    status_row = df_base.iloc[-1]
    
    # DEBUG PRINTS (Requested by User)
    print(f"DEBUG: Base Efficiency: {status_row['base_efficiency']:.2%}")
    print(f"DEBUG: Dust Loss (Latest): {status_row['dust_level']:.2%}")
    print(f"DEBUG: Temp Loss (Latest): {status_row['temperature_loss']:.2%}")
    print(f"DEBUG: Aging Loss (Latest): {status_row['aging_loss']:.2%}")
    print(f"DEBUG: Mismatch Loss (Latest): {status_row['mismatch_loss']:.2%}")
    print(f"DEBUG: Final Efficiency (Latest): {status_row['effective_efficiency']:.2%}")
    print("-" * 20)

    # Health Score: Use average of daylight hours to represent system capability
    # Nighttime health is 0 due to shading/darkness, which is misleading for "System Health"
    daylight_mask = df_base['irradiance'] > 10
    if daylight_mask.any():
        health = df_base.loc[daylight_mask, 'health_score'].mean() * 100.0
    else:
        health = status_row.get('health_score', 0.0) * 100.0
        
    aging_loss = status_row.get('aging_loss', 0.0) * 100.0
    
    # Mismatch average - exclude 0.0 (night) to get true system mismatch if we want?
    # Or just mean. If night is 0.0, mean will be lower.
    # User was seeing -47%, likely due to night=1.0.
    # Now night=0.0. If day mismatch=0.01, average is roughly 0.005.
    # Text says "Avg Mismatch/Low-Light Loss".
    mismatch_avg = df_base['mismatch_loss'].mean() * 100.0
    
    print(f"System Health Score: {health:.1f}%")
    print(f"Aging Impact: -{aging_loss:.2f}% efficiency")
    print(f"Avg Mismatch/Low-Light Loss: -{mismatch_avg:.2f}%")
    
    if mismatch_avg > 5.0:
        print("WARNING: High mismatch loss detected. Check inverters.")
    else:
        print("Status: Inverters operating normally.")

    print("="*40 + "\n")
    
    return final_metrics

if __name__ == "__main__":
    run_simulation()
