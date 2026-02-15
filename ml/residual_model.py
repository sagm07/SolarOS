
import xgboost as xgb
import pandas as pd
import numpy as np
import pickle
import os

class ResidualLearner:
    """
    Trains an XGBoost model to predict the *residual error* of the physics model.
    Implements Quantile Regression to provide uncertainty intervals (P10, P50, P90).
    """
    
    def __init__(self, model_path="ml_residual_model.pkl"):
        self.model_path = model_path
        self.model_p50 = None # Main estimator
        self.model_p10 = None # Conservative
        self.model_p90 = None # Optimistic
        self.is_trained = False
        
    def train(self, X: pd.DataFrame, y: pd.Series):
        """
        Trains Quantile XGBoost models.
        
        Args:
            X: Feature matrix
            y: Target residual (True - Physics)
        """
        print("Training Residual Learner (XGBoost)...")
        
        # Common params
        # Monotonic constraints? No, let tree decide.
        params = {
            'n_estimators': 200,
            'max_depth': 5,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'n_jobs': -1 
        }
        
        # Train P50 (Median/Mean)
        # reg:absoluteerror fits median, reg:squarederror fits mean. 
        # For standard "Best Guess", squarederror is usually more stable unless outliers are huge.
        self.model_p50 = xgb.XGBRegressor(objective='reg:squarederror', **params)
        self.model_p50.fit(X, y)
        
        # Train P10 (Conservative Bound)
        # XGBoost supports quantile regression via 'reg:quantileerror' since recent versions (2.0+)
        # Or we can use objective functions. simpler: use 'reg:quantileerror' if available, or just separate models.
        # Assuming modern XGBoost installed.
        
        try:
            self.model_p10 = xgb.XGBRegressor(objective='reg:quantileerror', quantile_alpha=0.1, **params)
            self.model_p10.fit(X, y)
            
            self.model_p90 = xgb.XGBRegressor(objective='reg:quantileerror', quantile_alpha=0.9, **params)
            self.model_p90.fit(X, y)
        except Exception as e:
            print(f"Warning: Quantile training failed ({e}). Falling back to simple variance estimation.")
            self.model_p10 = None
            self.model_p90 = None
            
        self.is_trained = True
        self.save_model()
        
    def predict(self, X: pd.DataFrame):
        """
        Returns a dict:
            'residual_pred': P50 prediction
            'p10': P10 prediction
            'p90': P90 prediction
        """
        if not self.is_trained and not self.load_model():
            # Return zeros if untrained
            zeros = np.zeros(len(X))
            return {'residual_pred': zeros, 'p10': zeros, 'p90': zeros}
            
        p50 = self.model_p50.predict(X)
        
        if self.model_p10 and self.model_p90:
            p10 = self.model_p10.predict(X)
            p90 = self.model_p90.predict(X)
            
            # Sanity check: P10 <= P50 <= P90
            # XGBoost quantiles aren't guaranteed to cross, but usually behave.
            # We enforce consistency just in case
            p10 = np.minimum(p10, p50)
            p90 = np.maximum(p90, p50)
        else:
            # Fallback spread
            std_dev = np.std(p50) * 0.5 # Dummy spread
            p10 = p50 - std_dev
            p90 = p50 + std_dev
            
        return {
            'residual_pred': p50,
            'p10': p10,
            'p90': p90
        }
        
    def save_model(self):
        models = {
            'p50': self.model_p50,
            'p10': self.model_p10,
            'p90': self.model_p90
        }
        with open(self.model_path, 'wb') as f:
            pickle.dump(models, f)
            
    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    models = pickle.load(f)
                    self.model_p50 = models['p50']
                    self.model_p10 = models['p10']
                    self.model_p90 = models['p90']
                self.is_trained = True
                return True
            except:
                return False
        return False
    
    def get_feature_importance(self):
        if self.model_p50:
            return self.model_p50.feature_importances_
        return []
