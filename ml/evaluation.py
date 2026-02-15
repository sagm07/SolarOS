
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_model(y_true, y_physics, y_hybrid):
    """
    Evaluates the performance of the Hybrid Model vs the Physics Baseline.
    
    Args:
        y_true: Ground Truth (Synthetic or Real)
        y_physics: Baseline Physics Prediction
        y_hybrid: Physics + ML Residual Prediction
    """
    
    # 1. Baseline Metrics
    base_mae = mean_absolute_error(y_true, y_physics)
    base_rmse = np.sqrt(mean_squared_error(y_true, y_physics))
    
    # 2. Hybrid Metrics
    hybrid_mae = mean_absolute_error(y_true, y_hybrid)
    hybrid_rmse = np.sqrt(mean_squared_error(y_true, y_hybrid))
    hybrid_r2 = r2_score(y_true, y_hybrid)
    
    # 3. Improvement
    mae_improvement = (base_mae - hybrid_mae) / base_mae * 100.0
    rmse_improvement = (base_rmse - hybrid_rmse) / base_rmse * 100.0
    
    report = {
        'baseline_mae': base_mae,
        'baseline_rmse': base_rmse,
        'hybrid_mae': hybrid_mae,
        'hybrid_rmse': hybrid_rmse,
        'r2_score': hybrid_r2,
        'error_reduction_pct': mae_improvement
    }
    
    return report

def print_evaluation_report(report):
    print("\n" + "="*40)
    print("   ML PERFORMANCE EVALUATION")
    print("="*40)
    print(f"Physics Baseline MAE : {report['baseline_mae']:.4f} kWh")
    print(f"Hybrid Model MAE     : {report['hybrid_mae']:.4f} kWh")
    print("-" * 40)
    print(f"📉 Error Reduction    : {report['error_reduction_pct']:.2f}%")
    print(f"📊 Model R² Score     : {report['r2_score']:.4f}")
    print("="*40 + "\n")
