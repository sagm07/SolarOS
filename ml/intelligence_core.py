
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
    # For Training: We need a "History" and a "Forecast"
    # To simulate this, we'll split the 30 days:
    # First 20 days = Training History
    # Last 10 days = Forecast Window
    # OR, we generate Truth for ALL 30 days, train on it (as if it's history), 
    # and then predict (in-sample) to demonstrate fit.
    # For a demo, "in-sample" verification is acceptable to show it CAN learn.
    
    df_physics = calculate_energy_metrics(df.copy(), cleaning_dates=[])

    # 3. Generate Synthetic Ground Truth
    print("Generating Synthetic Ground Truth (The 'Real' Data)...")
    from synthetic_ground_truth import SyntheticTruthGenerator
    truth_gen = SyntheticTruthGenerator()
    df_truth = truth_gen.generate_truth(df_physics)

    # 4. Hybrid Intelligence Training
    print("Training Hybrid AI (XGBoost) on Ground Truth...")
    hybrid_model = HybridCorrector()
    
    # Train on the first 20 days (Train Set)
    train_cutoff = int(len(df_truth) * 0.7)
    train_df = df_truth.iloc[:train_cutoff]
    test_df = df_truth.iloc[train_cutoff:]
    
    hybrid_model.train_model(df_physics.iloc[:train_cutoff], train_df)
    
    # 5. Prediction & Evaluation
    print("Applying ML Correction...")
    # Predict on WHOLE dataset for optimization context
    df_final = hybrid_model.correct_physics_prediction(df_physics)
    
    # Evaluate performance on Test Set (Unseen data)
    from evaluation import evaluate_model, print_evaluation_report
    
    # Subset for eval
    y_true_test = test_df['actual_truth_kwh']
    y_phys_test = df_physics.iloc[train_cutoff:]['actual_energy_kwh']
    y_hybr_test = df_final.iloc[train_cutoff:]['hybrid_energy_kwh']
    
    report = evaluate_model(y_true_test, y_phys_test, y_hybr_test)
    print_evaluation_report(report)

    # 6. Intelligent Decision Engine (Optimization)
    print("Initializing Intelligent Decision Engine (with Uncertainty)...")
    optimizer = OptimizationEngine(
        electricity_price=ELECTRICITY_PRICE_INR,
        cleaning_cost=EFFECTIVE_CLEANING_COST, 
        carbon_price_per_kg=5.0, 
        water_price_per_liter=WATER_COST_PER_LITER,
        water_usage_per_clean=WATER_USAGE_LITERS
    )
    
    # Pass the Hybrid DataFrame (contains 'hybrid_energy_kwh' and 'uncert_p... kwh')
    optimization_result = optimizer.optimize_cleaning_schedule(df_final)
    optimal_schedule_indices = optimization_result['cleaning_dates']
    optimal_dates = [df_final.iloc[i]['datetime'] for i in optimal_schedule_indices]
    
    print(f"Optimal Schedule Found: {len(optimal_schedule_indices)} cleanings")
    
    # 7. Metrics Calculation
    base_energy = df_final['hybrid_energy_kwh'].sum()
    
    # Calculate Gain: We need to simulate the 'Clean' scenario using Hybrid Model?
    # As discussed in Optimizer, we approximate Potential = Hybrid + Recoverable.
    # So Gain is simply Recoverable * Efficiency_Diff for the clean days.
    # Simplified: Use the Optimizer's reported 'net_value' or re-calculate.
    # Let's rely on the optimizer's result logic for consistency, or re-run metrics:
    
    # Re-simulating 'Clean' state with Hybrid is tricky without re-running 'correct_physics' loop.
    # We'll use the 'recoverable' sum for the clean days as the Energy Gain Estimate.
    # Note: This is an approximation.
    energy_gain = 0.0
    for idx in optimal_schedule_indices:
        # Assuming cleaning restores perfect health for that day (simplified)
        # Gain is roughly the recoverable energy for that day + subsequent days?
        # No, DP calculated the cumulative reward.
        pass
        
    # Better: Use total clean energy from a clean simulation - dirty simulation
    # But we only have one dataframe.
    # Let's use the 'total_net_value' from optimizer as the source of truth for "Benefit"
    # Net Benefit = Revenue - Cost.
    net_benefit = optimization_result['total_net_value']
    
    # Back-calculate Energy Gain from Net Benefit (Rev = E * Price - Cost)
    # Gain = (Net + Cost) / Price
    total_cost_calc = len(optimal_dates) * BASE_CLEANING_COST
    energy_gain_est = (net_benefit + total_cost_calc) / ELECTRICITY_PRICE_INR
    
    carbon_saved = energy_gain_est * CARBON_FACTOR
    water_used = len(optimal_dates) * WATER_USAGE_LITERS
    total_cost = total_cost_calc
    
    sses_score = calculate_sses(base_energy + energy_gain_est, water_used, carbon_saved, total_cost)
    
    # Uncertainty stats from the whole period (or just future?)
    # Let's show average uncertainty width
    p10_sum = df_final['uncert_p10_kwh'].sum()
    p90_sum = df_final['uncert_p90_kwh'].sum()
    confidence_interval = p90_sum - p10_sum
    
    # 8. Reasons
    reasons = []
    if len(optimal_dates) > 0:
        next_clean = optimal_dates[0]
        days_until = (next_clean - df.iloc[0]['datetime']).days
        reasons.append(f"Scheduled Clean in {days_until} days.")
        reasons.append(f"Projected Error Reduction: {report['error_reduction_pct']:.1f}% vs Physics.")
        reasons.append(f"Net projected revenue gain: ₹{net_benefit:.0f} (P50 Estimate).")
    else:
        reasons.append("Optimizer chose WAIT strategy.")
        if report['error_reduction_pct'] > 10:
             reasons.append(f"ML confirms Physics was pessimistic (Error Reduced by {report['error_reduction_pct']:.1f}%).")

    # Feature Importance (Explainability)
    importances = hybrid_model.get_model_insights()
    if len(importances) > 0:
        # We need feature names from FeatureEngineer
        # Hardcoding or getting them would be better, but for now we can infer or just print top raw
        # Let's map to known names:
        feature_names = [
            'irradiance', 'temperature', 'precipitation', 'dust_level',
            'hour_sin', 'hour_cos', 'month',
            'ghi_x_temp', 'dust_stickiness_proxy',
            'ghi_rolling_mean_3h', 'temp_rolling_mean_6h',
            'temp_deviation', 'temp_squared'
        ]
        # Sort and take top 3
        indices = np.argsort(importances)[::-1]
        top_3 = []
        for i in range(min(3, len(indices))):
             idx = indices[i]
             if idx < len(feature_names):
                 top_3.append(f"{feature_names[idx]} ({importances[idx]:.2f})")
        
        if top_3:
            reasons.append(f"Top Driving Factors: {', '.join(top_3)}")

    final_metrics = {
        "action": "CLEAN" if len(optimal_dates) > 0 else "WAIT",
        "cleaning_dates": [str(d.date()) for d in optimal_dates],
        "energy_gained": energy_gain_est,
        "net_benefit_inr": net_benefit,
        "carbon_saved_kg": carbon_saved,
        "water_used_liters": water_used,
        "sses_score": sses_score,
        "p10_energy": p10_sum,
        "p90_energy": p90_sum,
        "confidence_interval": confidence_interval,
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
    # Risk adjusted = P10 Gain - Cost
    p10_gain_est = (p10_sum - base_energy) * ELECTRICITY_PRICE_INR - total_cost
    print(f"📊 Risk-Adjusted Gain (P10): ₹{p10_gain_est:,.2f} (Conservative)")
    print(f"⚡ Energy Recovered:       {energy_gain_est:.2f} kWh")
    print(f"🎲 Uncertainty (P90-P10):  {confidence_interval:.2f} kWh")
    print("="*50 + "\n")
    
    return final_metrics

if __name__ == "__main__":
    run_simulation()
