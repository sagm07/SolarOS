import sys
import os
import pandas as pd
import numpy as np

# Ensure local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_farm_optimizer import SolarFarm, MultiSiteOptimizer

def run_test():
    print("==========================================")
    print("   OPTIMIZER ALGORITHM VERIFICATION       ")
    print("==========================================")
    
    # scenario: Greedy fails
    # Budget: 50
    # Farm A: Cost 10, Benefit 60  (Ratio 6.0)
    # Farm B: Cost 20, Benefit 100 (Ratio 5.0)
    # Farm C: Cost 30, Benefit 120 (Ratio 4.0)
    
    # Greedy picks:
    # 1. A (Cost 10, Ben 60). Rem Budget: 40.
    # 2. B (Cost 20, Ben 100). Rem Budget: 20. Total Ben: 160.
    # 3. C (Cost 30) -> Skip.
    # Total Benefit: 160.
    
    # Optimal picks:
    # B + C (Cost 20+30=50). Total Ben 100+120=220.
    # 220 > 160.
    
    farm_a = SolarFarm("Farm A", (0,0), 100, cleaning_water_usage_liters=10)
    farm_a.net_benefit = 60.0
    farm_a.action = "CLEAN"
    farm_a.efficiency_score = 6.0
    
    farm_b = SolarFarm("Farm B", (0,0), 100, cleaning_water_usage_liters=20)
    farm_b.net_benefit = 100.0
    farm_b.action = "CLEAN"
    farm_b.efficiency_score = 5.0

    farm_c = SolarFarm("Farm C", (0,0), 100, cleaning_water_usage_liters=30)
    farm_c.net_benefit = 120.0
    farm_c.action = "CLEAN"
    farm_c.efficiency_score = 4.0
    
    farms = [farm_a, farm_b, farm_c]
    
    print("SCENARIO: Known Greedy Failure Case")
    print("Items: A(10L, $60), B(20L, $100), C(30L, $120)")
    print("Budget: 50L")
    print("Expected Greedy: A+B ($160)")
    print("Expected Optimal: B+C ($220)")
    print("-" * 40)
    
    # Instantiate Optimizer
    opt = MultiSiteOptimizer(farms, water_budget_liters=50)
    
    # We bypass 'optimize' data reliance by manually setting values above.
    # But optimize() calls 'evaluate_cleaning_opportunity'.
    # We must Hack optimize() or modify MultiSiteOptimizer to accept pre-calced?
    # Actually, optimize() calls evaluate only if data is passed.
    # If we modify optimize to take an optional 'pre_evaluated' flag or just check data.
    
    # For now, let's just rely on the fact that `optimize` re-evaluates. 
    # Validating the internal DP method directly might be better if I expose it.
    
    # But wait, optimize() iterates and sets values. 
    # I should verify the NEW implementation once written.
    # For now, I'll mock the internal call.
    
    # To test current greedy vs future DP, I will run optimize(None)
    # The current code in optimize() iterates farms:
    # "if shared_data_df is not None: farm.evaluate..."
    # So if I pass None, it uses existing state. Perfect.
    
    selected, used, benefit = opt.optimize(shared_data_df=None)
    
    print(f"\n[ACTUAL RESULT]")
    print(f"Selected: {[f.name for f in selected]}")
    print(f"Benefit:  {benefit}")
    print(f"Used:     {used}")
    
    if benefit == 220:
        print("\n[PASS] OPTIMAL SOLUTION FOUND (DP implementation active)")
    elif benefit == 160:
        print("\n[FAIL] GREEDY SOLUTION FOUND (Old implementation active)")
    else:
        print(f"\n[?] UNEXPECTED RESULT: {benefit}")

if __name__ == "__main__":
    run_test()
