import pandas as pd
import numpy as np
import sys
import os

# Ensure local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from degradation_model import calculate_energy_metrics
try:
    from advanced_loss_model import calculate_mismatch_loss
except ImportError:
    pass

def verify_accuracy():
    print("========================================")
    print("   EFFICIENCY CALCULATION VERIFICATION  ")
    print("========================================")
    print(f"{'Input Scenario':<20} | {'Expected':<10} | {'Actual':<10} | {'Status':<10}")
    print("-" * 60)

    # Scenario 1: Perfect Conditions (Base Case)
    # Base=20%, No Dust, Temp=25C, No Aging, No Mismatch (simulated)
    # Expected: 20.0%
    df1 = pd.DataFrame({
        'datetime': [pd.Timestamp('2025-01-01 12:00:00')],
        'irradiance': [1000],
        'temperature': [25],
        'precipitation': [0]
    })
    # Mocking advanced losses to 0 for this test or relying on logic
    # The model calculates these internally.
    # Mismatch at 1000W/m2 is rated_mismatch (1%)
    # So expected is 0.20 * (1-0.01) = 0.198 (19.8%)
    
    res1 = calculate_energy_metrics(df1)
    actual1 = res1['effective_efficiency'].iloc[0]
    expected1 = 0.20 * (1 - 0.01) # 1% default mismatch
    
    status1 = "PASS" if abs(actual1 - expected1) < 0.0001 else "FAIL"
    print(f"{'Standard Test':<20} | {expected1:.4f}     | {actual1:.4f}     | {status1}")

    # Scenario 2: High Dust (10%)
    # Base=20%, Dust=10%, Temp=25C
    # We must force dust in the dataframe or allow it to accumulate?
    # calculate_energy_metrics initializes dust to 0. It accumulates over time.
    # To test specific dust, we might need 30 days of data or hack the column after.
    # Actually, calculate_energy_metrics returns the DF with columns.
    # Let's verify the FORMULA by manually checking the columns row-wise.
    
    print("-" * 60)
    print("FORMULA VERIFICATION (Internal Consistency)")
    print("Checking: Eff = Base * (1-Dust) * (1-Temp) * (1-Age) * (1-Mismatch)")
    
    # Create a complex scenario
    # 30 days to get some dust
    dates = pd.date_range('2025-01-01', periods=1, freq='h')
    df2 = pd.DataFrame({
        'datetime': dates,
        'irradiance': [800], # Some mismatch loss? 800 > 200 so just rated (1%)
        'temperature': [35], # 10 deg above 25. Loss = 10 * 0.4% = 4% (0.04)
        'precipitation': [0]
    })
    
    # We can't easily force "Aging" or "Dust" via input args to calculate_energy_metrics 
    # without running a long simulation.
    # But we can inspect the output columns to ensure the final math holds up.
    
    res2 = calculate_energy_metrics(df2)
    row = res2.iloc[0]
    
    base = row['base_efficiency']      # 0.20
    dust = row['dust_level']           # ~0 (first hour)
    temp = row['temperature_loss']     # Should be 0.04
    age = row['aging_loss']            # ~0
    shade = row['shading_loss']        # 12:00 -> 0
    mis = row['mismatch_loss']         # 1%
    
    # Manual Calc
    manual_eff = base * (1-dust) * (1-temp) * (1-age) * (1-shade) * (1-mis)
    model_eff = row['effective_efficiency']
    
    print(f"\nInputs Detected by Model:")
    print(f"  Base Eff: {base:.4f}")
    print(f"  Dust:     {dust:.4f}")
    print(f"  Temp:     {temp:.4f} (Expected ~0.04 for 35C)")
    print(f"  Mismatch: {mis:.4f}")
    print(f"  Age:      {age:.4f}")
    print(f"  Shade:    {shade:.4f}")
    
    print(f"\nCalculations:")
    print(f"  Manual:   {manual_eff:.6f}")
    print(f"  Model:    {model_eff:.6f}")
    
    if abs(manual_eff - model_eff) < 1e-9:
        print("\n[SUCCESS] The multiplicative formula is EXACTLY preserved.")
    else:
        print("\n[FAIL] Discrepancy detected between components and final result.")

    # Scenario 3: Verify Low Light Mismatch Logic
    print("-" * 60)
    print("LOW LIGHT LOGIC CHECK")
    # Irradiance = 100 W/m2.
    # Metric: < 200. 
    # Loss = 0.05 * (200 - 100)/200 + 0.01 = 0.05 * 0.5 + 0.01 = 0.025 + 0.01 = 0.035 (3.5%)
    
    df3 = pd.DataFrame({
        'datetime': [pd.Timestamp('2025-01-01 12:00:00')],
        'irradiance': [100],
        'temperature': [25],
        'precipitation': [0]
    })
    res3 = calculate_energy_metrics(df3)
    mis_actual = res3['mismatch_loss'].iloc[0]
    mis_expected = 0.035
    
    print(f"Irradiance 100 W/m2:")
    print(f"  Expected Mismatch: {mis_expected:.4f} (3.5%)")
    print(f"  Actual Mismatch:   {mis_actual:.4f}")
    
    if abs(mis_actual - mis_expected) < 0.001:
        print("  [PASS] Low light logic functions correctly.")
    else:
        print("  [FAIL] Low light logic incorrect.")

if __name__ == "__main__":
    verify_accuracy()
