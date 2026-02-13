
import sys
import os
import pandas as pd
import numpy as np

# Ensure local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rain_model import check_rain_forecast_wait, apply_rain_cleaning
from advanced_loss_model import calculate_shading_loss
from multi_farm_optimizer import SolarFarm, MultiSiteOptimizer
from intelligence_core import run_simulation

def verify_v3():
    print("="*50)
    print("SOLAROS V3 VERIFICATION SUITE")
    print("="*50)
    
    # 1. Rain Intelligence Verification
    print("\n[TEST 1] Rain Intelligence Logic")
    dates = pd.date_range("2025-01-01", periods=5, freq="D")
    df_rain = pd.DataFrame({"datetime": dates, "precipitation": [0, 3.5, 0, 0, 0]})
    should_wait, reason = check_rain_forecast_wait(df_rain, current_date=dates[0])
    
    if should_wait:
        print(f"[PASS]: Wait Logic Triggered: {reason}")
    else:
        print(f"[FAIL]: Wait Logic NOT Triggered (Expected True)")
        
    dust_before = 0.5
    dust_after = apply_rain_cleaning(dust_before, 5.0) # 5mm rain
    print(f"   Physics: Dust reduced from {dust_before} -> {dust_after:.3f} (Gamma ~0.4)")
    
    # 2. Deep Degradation (Shading)
    print("\n[TEST 2] Deep Degradation (Shading Model)")
    noon_loss = calculate_shading_loss(12)
    sunrise_loss = calculate_shading_loss(6)
    
    if noon_loss == 0.0 and sunrise_loss > 0.0:
        print(f"[PASS]: Shading correct (Noon: {noon_loss}, Sunrise: {sunrise_loss})")
    else:
        print(f"[FAIL]: Shading incorrect (Noon: {noon_loss}, Sunrise: {sunrise_loss})")
        
    # 3. Asset Health Report
    print("\n[TEST 3] Asset Health Engine Integration")
    print("   Running full intelligence core simulation...")
    try:
        run_simulation() # This prints the report
        print("[PASS]: Simulation ran successfully.")
    except Exception as e:
        print(f"[FAIL]: Simulation crashed: {e}")

    # 4. Multi-Farm Optimization
    print("\n[TEST 4] Multi-Farm Optimization Engine")
    farms = [
        SolarFarm("HighEff", (13, 80), 500, dust_rate_factor=1.5, cleaning_water_usage_liters=100),
        SolarFarm("LowEff", (13, 80), 5000, dust_rate_factor=0.8, cleaning_water_usage_liters=1000),
    ]
    # Mock data for farms
    dates_mock = pd.date_range(start='2025-01-01', periods=24*30, freq='h')
    df_mock = pd.DataFrame({
        'datetime': dates_mock,
        'irradiance': np.random.uniform(0, 1000, 24*30),
        'temperature': np.random.uniform(25, 35, 24*30),
        'precipitation': np.zeros(24*30)
    })
    
    opt = MultiSiteOptimizer(farms, water_budget_liters=500)
    selected, used, benefit = opt.optimize(df_mock)
    
    print(f"   Selected: {[f.name for f in selected]}")
    if "HighEff" in [f.name for f in selected] and "LowEff" not in [f.name for f in selected]:
        print("[PASS]: Optimizer selected High Efficiency farm over Low Efficiency one.")
    else:
        print(f"[FAIL] / INCONCLUSIVE: Selection was {[f.name for f in selected]}")

    print("\n" + "="*50)
    print("VERIFICATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    verify_v3()
