import numpy as np
import pandas as pd
import pickle
import os
from datetime import datetime

class HybridCorrector:
    """
    Hybrid Intelligence Layer.
    Combines Physics-Based Model (PBM) with Data-Driven Machine Learning (DDML).
    
    Formula:
    Final_Prediction = Physics_Output + ML_Residual_Correction
    
    The ML model learns the *errors* of the physics model (e.g., due to local microclimate, 
    organic soiling, sensor drift) rather than trying to learn physics from scratch.
    """
    
    def __init__(self, model_path="ml_residual_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.load_model()
        
    def load_model(self):
        """
        Loads the pre-trained ML residual model.
        In a real scenario, this would load an XGBoost/LightGBM model.
        For this implementation, we initialize a 'Mock' model if none exists.
        """
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
            except Exception as e:
                print(f"[HybridCorrector] Warning: Failed to load model: {e}")
        
        if self.model is None:
            # print("[HybridCorrector] Initializing Synthetic Residual Model (Cold Start)")
            self.model = self._mock_train()

    def _mock_train(self):
        """
        Simulates training a residual model.
        In reality, this would train on (Historical_Actual - Historical_Physics).
        """
        return "Thinking_Machine_v1"

    def predict_residual(self, features: pd.DataFrame) -> np.ndarray:
        """
        Predicts the *error* of the physics model.
        
        Args:
            features: DataFrame with ['irradiance', 'temperature', 'humidity', 'wind_speed', 'dust_level']
            
        Returns:
            np.ndarray: Predicted residual (kWh correction).
        """
        # --- SYNTHETIC ML LOGIC (for demonstration) ---
        # Real ML would use self.model.predict(features)
        
        # 1. Temperature Non-Linearity Correction
        # Physics model uses linear coeff. Real panels behave non-linearly at extremes.
        temp_correction = (features['temperature'] - 25.0) ** 2 * -0.001
        
        # 2. Low Light Performance Correction
        # Physics model might under-estimate diffuse light performance
        low_light_boost = np.where(features['irradiance'] < 200, 5.0, 0.0)
        
        # 3. Micro-climate Dust Correction
        # If 'humidity' is high (simulated), stickiness increases soiling impact (negative residual)
        # We don't have humidity in base data, simulating random micro-climate noise
        random_noise = np.random.normal(0, 2.0, size=len(features))
        
        # Total Residual (kWh)
        # Scaling relatively small to simply "nudge" the physics model
        residual = temp_correction + low_light_boost + random_noise
        
        return residual

    def correct_physics_prediction(self, physics_df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies ML correction to the physics-based DataFrame.
        """
        df = physics_df.copy()
        
        # Prepare features for ML
        # In prod, we'd add more features here (wind, humidity, etc)
        features = df[['irradiance', 'temperature', 'dust_level']].copy()
        
        # Get Residuals
        residuals = self.predict_residual(features)
        
        # Apply Correction
        # Final = Physics + Residual
        df['ml_residual_kwh'] = residuals
        df['hybrid_energy_kwh'] = df['actual_energy_kwh'] + df['ml_residual_kwh']
        
        # Sanity Clamp - Energy cannot be negative
        df['hybrid_energy_kwh'] = df['hybrid_energy_kwh'].clip(lower=0.0)
        
        return df
