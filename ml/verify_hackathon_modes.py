import sys
import os
import pandas as pd
import numpy as np

# Ensure local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_farm_optimizer import SolarFarm, MultiSiteOptimizer

def run_hackathon_verification():
    print("==========================================")
    print("   HACKATHON FEATURE VERIFICATION         ")
    print("==========================================")
    
    # Mock Data
    dates = pd.date_range(start='2025-01-01', periods=72, freq='h')
    df_mock = pd.DataFrame({
        'datetime': dates,
        'irradiance': np.random.uniform(0, 1000, 72),
        'temperature': np.random.uniform(25, 35, 72),
        'precipitation': np.zeros(72)
    })
    
    # Define Heterogeneous Farms
    # A: High Benefit, High Water (Big Farm)
    # B: Med Benefit, Med Water
    # C: High Efficiency (Good benefit for low water)
    farms = [
        SolarFarm("Gujarat-East", (13, 80), 5000, dust_rate_factor=1.2, cleaning_water_usage_liters=1000), 
        SolarFarm("Rajasthan-North", (13, 80), 2000, dust_rate_factor=1.0, cleaning_water_usage_liters=400),
        SolarFarm("Kerala-South", (13, 80), 500,  dust_rate_factor=1.5, cleaning_water_usage_liters=100), 
        SolarFarm("MP-West", (13, 80), 3000, dust_rate_factor=0.8, cleaning_water_usage_liters=600),
        SolarFarm("TN-Central", (13, 80), 3000, dust_rate_factor=0.9, cleaning_water_usage_liters=600),
    ]
    
    # 1. Test PROFIT Mode (Standard)
    print("\n>>> TESTING MODE: PROFIT (Default)")
    opt = MultiSiteOptimizer(farms, water_budget_liters=1500)
    # Mock evaluation to ensure positive benefit
    for f in farms:
        f.net_benefit = f.panel_area_m2 * 0.1 # Dummy benefit proportional to size
        f.energy_recovered = f.net_benefit / 6.0
        f.co2_saved = f.energy_recovered * 0.7
        f.action = "CLEAN"
        
    opt.optimize(shared_data_df=None, mode="PROFIT")
    
    # 2. Test WATER SCARCITY Mode
    print("\n>>> TESTING MODE: WATER_SCARCITY (Reduced Budget)")
    # Reset farms? Logic is stateless in optimize() mostly, but good to be safe.
    opt.optimize(shared_data_df=None, mode="WATER_SCARCITY")
    
    # 3. Test CARBON Mode
    print("\n>>> TESTING MODE: CARBON")
    # Make one farm have huge CO2 savings but low financial benefit to see if it gets picked?
    # For now just verify it runs and prints the mode.
    farms[2].co2_saved = 99999.0 # Farm C (Small) saves earth
    farms[2].optimization_value = 0 # Clear old content
    
    
    opt.optimize(shared_data_df=None, mode="CARBON")

    # 4. Test VISUALIZATION (Pass DF)
    print("\n>>> TESTING VISUALIZATION TRIGGER")
    # Need data that triggers cleaning (High irradiance, long period)
    dates_long = pd.date_range(start='2025-01-01', periods=720, freq='h') # 30 days
    df_vis = pd.DataFrame({
        'datetime': dates_long,
        'irradiance': np.zeros(720),
        'temperature': np.random.uniform(25, 35, 720),
        'precipitation': np.zeros(720)
    })
    # Set daylight irradiance
    df_vis.loc[(df_vis.datetime.dt.hour >= 6) & (df_vis.datetime.dt.hour <= 18), 'irradiance'] = 800.0
    
    # Use just one farm to keep output clean, or same list
    # Ensure it needs cleaning by setting prior dust high? 
    # The current logic simulates from scratch. 
    # get_recommended_cleaning_date needs projected recoverable > cost.
    # CONSTANT HIGH IRRADIANCE + CONSTANT DUST ACCUMULATION should trigger it.
    
    opt.optimize(shared_data_df=df_vis, mode="PROFIT")


if __name__ == "__main__":
    run_hackathon_verification()
