import pandas as pd
import numpy as np
from datetime import datetime

class AdaptiveLearner:
    """
    Closed-Loop Learning System.
    
    Flow:
    1. Receive ACTUAL generation data from field (Ground Truth).
    2. Compare with PREDICTED values logged earlier.
    3. Calculate Error (MAPE/RMSE).
    4. If Error > Threshold -> MODEL_DRIFT_DETECTED -> Trigger Retraining.
    """
    
    def __init__(self, monitor_ref):
        self.monitor = monitor_ref
        self.retraining_history = []
        
    def submit_feedback(self, clean_date: str, actual_energy_kwh: float, predicted_kwh: float):
        """
        Ingest ground truth from the user/SCADA system.
        """
        error = abs(actual_energy_kwh - predicted_kwh)
        mape = (error / actual_energy_kwh) * 100 if actual_energy_kwh > 0 else 0
        
        # Log feedback
        print(f"[AdaptiveLearner] Feedback Received for {clean_date}: Actual={actual_energy_kwh}, Pred={predicted_kwh}, MAPE={mape:.1f}%")
        
        # Check for Retraining Trigger
        if mape > 10.0: # If error > 10%
            self.trigger_retraining(reason=f"High Error ({mape:.1f}%) on {clean_date}")
            return {
                "status": "RETRAINING_TRIGGERED",
                "message": f"Model error {mape:.1f}% exceeded threshold. Retraining initiated.",
                "mape": mape
            }
            
        return {
            "status": "ACCEPTED",
            "message": "Feedback logged. Model performing within bounds.",
            "mape": mape
        }
        
    def trigger_retraining(self, reason: str):
        """
        Simulates the retraining pipeline.
        In production: Airflow DAG / Kubeflow Pipeline start.
        """
        print(f"[AdaptiveLearner] ⚠️ RETRAINING INITIATED. Reason: {reason}")
        # Simulate time
        # ...
        self.retraining_history.append({
            "date": datetime.now().isoformat(),
            "reason": reason,
            "status": "SUCCESS",
            "new_version": f"v3.{len(self.retraining_history) + 1}"
        })
        print(f"[AdaptiveLearner] ✅ Model updated to {self.retraining_history[-1]['new_version']}")

    def get_retraining_status(self):
        if not self.retraining_history:
            return "Model Stable (v3.0)"
        return f"Last Retrained: {self.retraining_history[-1]['date']} ({self.retraining_history[-1]['new_version']})"
