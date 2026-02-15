
import pandas as pd
import numpy as np

class FeatureEngineer:
    """
    Transforms raw telemetry data into rich features for the Machine Learning model.
    Focuses on capturing temporal patterns, interactions, and derivatives.
    """
    
    def __init__(self):
        pass
    
    def create_features(self, df: pd.DataFrame, is_training=True) -> pd.DataFrame:
        """
        Generates features from the input dataframe.
        
        Args:
            df: DataFrame with ['datetime', 'irradiance', 'temperature', 'precipitation', 'dust_level']
            is_training: If True, it expects to find 'true_residual_kwh' (or ignores it if creating X)
            
        Returns:
            X (pd.DataFrame): The feature matrix.
        """
        # Work on a copy
        X = df.copy()
        
        # 1. Temporal Features (Cyclic)
        # Hour of day is crucial for solar
        X['hour'] = X['datetime'].dt.hour
        X['month'] = X['datetime'].dt.month
        
        # Cyclic encoding for Hour (0 and 23 are close)
        X['hour_sin'] = np.sin(2 * np.pi * X['hour'] / 24)
        X['hour_cos'] = np.cos(2 * np.pi * X['hour'] / 24)
        
        # 2. Physics Interactions
        # GHI x Temp: High GHI usually means High Temp, but efficiency drops. 
        # The physics model covers linear, but ML finds the residuals in this interaction.
        X['ghi_x_temp'] = X['irradiance'] * X['temperature']
        
        # Dust x Humidity Proxy
        # We don't have humidity in input unless we simulated it. 
        # But we can approximate "Stickiness" opportunities:
        # High Precip recently? (maybe high humidity)
        # Let's use rolling mean of precipitation as a humidity proxy
        X['rolling_precip_24h'] = X['precipitation'].rolling(window=24, min_periods=1).sum()
        X['dust_stickiness_proxy'] = X['dust_level'] * X['rolling_precip_24h']
        
        # 3. Rolling Statistics (Temporal Context)
        # Solar response isn't instant; panel heat mass exists (mostly irrelevant for hourly, but trend matters)
        # Weather stability matters.
        for window in [3, 6, 24]:
            X[f'ghi_rolling_mean_{window}h'] = X['irradiance'].rolling(window=window, min_periods=1).mean()
            X[f'temp_rolling_mean_{window}h'] = X['temperature'].rolling(window=window, min_periods=1).mean()
            
        # 4. Deviations
        # Is it hotter than usual for this time? (Temp - Rolling mean)
        X['temp_deviation'] = X['temperature'] - X['temp_rolling_mean_24h']
        
        # 5. Non-Linearity Probes
        # Squared terms to help Tree models find parabolas easier (though Trees can approximate them)
        X['temp_squared'] = X['temperature'] ** 2
        
        # 6. Cleaning State
        # Clean vs Dirty regime
        X['is_clean'] = (X['dust_level'] < 0.01).astype(int)
        
        # Select Feature Columns
        feature_cols = [
            'irradiance', 'temperature', 'precipitation', 'dust_level',
            'hour_sin', 'hour_cos', 'month',
            'ghi_x_temp', 'dust_stickiness_proxy',
            'ghi_rolling_mean_3h', 'temp_rolling_mean_6h',
            'temp_deviation', 'temp_squared'
        ]
        
        # Handle NaNs from rolling (fill with current value or 0)
        X[feature_cols] = X[feature_cols].fillna(method='bfill').fillna(0)
        
        return X[feature_cols]

if __name__ == "__main__":
    # Test
    try:
        from data_loader import fetch_nasa_power_data
        from degradation_model import calculate_energy_metrics
        
        print("Fetching data for feature engineering test...")
        raw = fetch_nasa_power_data(days=30)
        phy = calculate_energy_metrics(raw)
        
        fe = FeatureEngineer()
        features = fe.create_features(phy)
        
        print("\nGenerated Features Head:")
        print(features.head())
        print(f"\nFeature Shape: {features.shape}")
        
    except ImportError as e:
        print(f"Test failed: {e}")
