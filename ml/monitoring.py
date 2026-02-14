import time
import json
import os
import numpy as np
from datetime import datetime

class ModelMonitor:
    """
    ML Ops & Monitoring Layer.
    Tracks:
    1. Inference Latency
    2. Data Drift (Input distribution changes)
    3. Prediction Tracking (for later audit)
    """
    
    def __init__(self, log_file="ml_monitoring_logs.json"):
        self.log_file = log_file
        # In-memory buffer for drift detection
        self.recent_predictions = []
        
    def log_inference(self, request_id: str, input_features: dict, output_metrics: dict, execution_time_ms: float):
        """
        Logs a single inference event.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "latency_ms": round(execution_time_ms, 2),
            "inputs": input_features, # Simplified logging
            "outputs": {
                "p50_energy": output_metrics.get("energy_gained", 0),
                "action": output_metrics.get("action", "UNKNOWN")
            }
        }
        
        # Append to log file (Append-only for performance)
        # In production -> Kafka/Prometheus
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"[Monitor] Logging failed: {e}")
            
        # Store for drift tracking
        self.recent_predictions.append(output_metrics.get("energy_gained", 0))
        if len(self.recent_predictions) > 1000:
            self.recent_predictions.pop(0)

    def check_drift(self) -> dict:
        """
        Checks for Model Drift.
        Simulates a Kolmogorov-Smirnov (KS) test on output distribution.
        """
        if len(self.recent_predictions) < 10:
            return {"drift_detected": False, "confidence": 0.0, "message": "Insufficient data"}
            
        # Simple drift heuristic: check if recent mean deviates significantly from "training" baseline (mocked)
        baseline_mean = 1000.0 # kWh
        current_mean = np.mean(self.recent_predictions)
        
        deviation = abs(current_mean - baseline_mean) / baseline_mean
        
        if deviation > 0.15: # 15% deviation
            return {
                "drift_detected": True, 
                "confidence": 0.95, 
                "message": f"Output mean shifted by {deviation*100:.1f}% from baseline."
            }
            
        return {"drift_detected": False, "confidence": 0.8, "message": "Stable"}

    def get_stats(self) -> dict:
        """
        Returns dashboards stats.
        """
        return {
            "total_requests": 142, # Mock accumulated
            "avg_latency_ms": 142, # Mock
            "last_active": datetime.now().isoformat()
        }
