import numpy as np
import pandas as pd
import os
from feature_engineering import FeatureEngineer
from residual_model import ResidualLearner

class HybridCorrector:
    """
    Hybrid Intelligence Layer (v2.0 - Trained XGBoost).
    
    Orchestrates the pipeline:
    1. Physics Model Output -> 
    2. Feature Engineering -> 
    3. Residual Prediction (XGBoost) -> 
    4. Final Hybrid Prediction
    """
    
    def __init__(self, model_path="ml_residual_model.pkl"):
        self.fe = FeatureEngineer()
        self.learner = ResidualLearner(model_path)
        
    def train_model(self, physics_df: pd.DataFrame, truth_df: pd.DataFrame):
        """
        Trains the internal residual model.
        
        Args:
            physics_df: DataFrame with physics predictions.
            truth_df: DataFrame with 'true_residual_kwh' (Target).
        """
        # Create Features (X)
        X = self.fe.create_features(physics_df, is_training=True)
        
        # Target (y)
        y = truth_df['true_residual_kwh']
        
        # Train
        self.learner.train(X, y)
        
    def correct_physics_prediction(self, physics_df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies ML correction to the physics-based DataFrame.
        """
        df = physics_df.copy()
        
        # 1. Create Features
        X = self.fe.create_features(df, is_training=False)
        
        # 2. Predict Residuals (with Uncertainty)
        preds = self.learner.predict(X)
        
        # 3. Apply Correction
        # Final = Physics + Predicted_Residual
        df['ml_residual_kwh'] = preds['residual_pred']
        df['hybrid_energy_kwh'] = df['actual_energy_kwh'] + df['ml_residual_kwh']
        
        # Uncertainty Columns
        df['uncert_p10_kwh'] = df['actual_energy_kwh'] + preds['p10']
        df['uncert_p90_kwh'] = df['actual_energy_kwh'] + preds['p90']
        
        # Sanity Clamp
        df['hybrid_energy_kwh'] = df['hybrid_energy_kwh'].clip(lower=0.0)
        df['uncert_p10_kwh'] = df['uncert_p10_kwh'].clip(lower=0.0)
        df['uncert_p90_kwh'] = df['uncert_p90_kwh'].clip(lower=0.0)
        
        return df

    def get_model_insights(self):
        """Returns feature importances if available."""
        return self.learner.get_feature_importance()
