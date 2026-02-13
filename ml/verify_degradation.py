import pandas as pd
import numpy as np
import sys
import os

# Ensure we can import degradation_model
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from degradation_model import calculate_energy_metrics

def verify():
    print("Running verification...")
    # Create dummy data for deterministic check
    dates = pd.date_range(start='2025-01-01', periods=24*30, freq='h')  # 30 days, hourly
    df = pd.DataFrame({
        'datetime': dates,
        'irradiance': 1000.0, # Constant high irradiance
        'temperature': 25.0   # Constant 25C (no temp loss)
    })
    
    # Process
    df_processed = calculate_energy_metrics(df)
    
    # Check 1: Base stats
    print(f"Rows: {len(df_processed)}")
    
    # Check 2: Efficiency Decay due to Dust
    # At start (Day 0), dust should be near 0.
    eff_start = df_processed['effective_efficiency'].iloc[0]
    dust_start = df_processed['dust_loss'].iloc[0]
    print(f"Efficiency Start: {eff_start:.4f} (Expected ~0.20)")
    print(f"Dust Loss Start: {dust_start:.4f} (Expected ~0.00)")
    
    # At end (Day 30), dust_level ~0.15; multiplicative: eff = 0.20 * (1 - 0.15) ≈ 0.17
    eff_end = df_processed['effective_efficiency'].iloc[-1]
    dust_end = df_processed['dust_loss'].iloc[-1]
    print(f"Efficiency End: {eff_end:.4f} (Expected ~0.17, multiplicative)")
    print(f"Dust Loss End: {dust_end:.4f} (Expected ~0.15)")
    
    if eff_end < eff_start:
        print("PASS: Effective efficiency decreases over time.")
    else:
        print("FAIL: Effective efficiency did not decrease.")

    if np.isclose(dust_end, 0.15, atol=0.01):
        print("PASS: Dust accumulation reached ~15%.")
    else:
        print(f"FAIL: Dust accumulation end value incorrect: {dust_end:.4f}")

    # Check 3: Recoverable Energy
    # Ideal = 1000 * 100 * 0.20 / 1000 = 20 kWh/h. Multiplicative: actual drops from 20 to ~17 kWh/h.
    # Recoverable should increase.
    rec_start = df_processed['recoverable_energy_kwh'].iloc[0]
    rec_end = df_processed['recoverable_energy_kwh'].iloc[-1]
    
    print(f"Recoverable Start: {rec_start:.4f}")
    print(f"Recoverable End: {rec_end:.4f}")
    
    if rec_end > rec_start:
        print("PASS: Recoverable energy increases over time.")
    else:
        print("FAIL: Recoverable energy did not increase.")

if __name__ == "__main__":
    verify()
