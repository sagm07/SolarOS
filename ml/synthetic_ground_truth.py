
import numpy as np
import pandas as pd

class SyntheticTruthGenerator:
    """
    Generates 'Real World' ground truth data by applying PHYSICALLY PLAUSIBLE deviations
    to the ideal physics model.

    This creates the target variable (y) for our ML model to learn.
    Ideally, this would be replaced by actual sensor data from the field.
    """
    
    def __init__(self, seed=42):
        np.random.seed(seed)
        
    def generate_truth(self, physics_df: pd.DataFrame) -> pd.DataFrame:
        """
        Takes the physics-based dataframe and adds structured residuals to create 'observed' data.
        
        Formula:
        Observed = Physics_Output + Residual_Structure + Noise
        
        Where Residual_Structure includes:
        1. Temperature Non-linearity (Physics assumes linear loss, real is quadratic at extremes)
        2. Low Light Mismatch (Inverters struggle at low irradiance)
        3. Micro-climate Soiling (Humidity makes dust stickier)
        4. Sensor Drift/Noise
        """
        df = physics_df.copy()
        
        # 1. Non-Linear Temperature Effect
        # Physics (Linear): Loss = 0.4% * (T - 25)
        # Reality (Quadratic): At very high temps (>40C), efficiency drops faster.
        # At low temps (<15C), it efficiency gains might be slightly less than linear due to condensation/frost logic (ignored here)
        # We model an EXTRA penalty for high heat.
        
        base_energy = df['actual_energy_kwh'] # This is the "Physics Prediction"
        temp = df['temperature']
        
        # Correction: If T > 35, add extra non-linear loss
        # (T - 35)^2 * small_factor
        temp_residual = -0.0005 * np.square(np.maximum(temp - 35, 0)) * base_energy
        
        # 2. Low Light / Spectral Mismatch
        # Physics model might underestimate diffuse light handling OR inverter efficiency drop
        # Let's say our panels are actually BETTER at low light than the standard linear model implies (common in modern panels)
        # GHI < 200 W/m2 -> Boost efficiency by 5% relative
        ghi = df['irradiance']
        low_light_mask = (ghi > 10) & (ghi < 300)
        # Create a bump: max at 150 W/m2
        low_light_residual = np.where(low_light_mask, 0.05 * base_energy, 0.0)
        
        # 3. Humidity / Soiling Factor (The "Pattern" ML needs to find)
        # Physics assumes linear dust. Reality: High humidity makes dust stick.
        # We simulate a "Sticky Factor" that correlates with time of day or just valid random walk
        # Let's create a hidden "Humidity" feature that isn't in the input, but correlates with Temp (inv)
        # High Temp usually = Low Humidity in day.
        # We'll add a residual that says: "Physics underestimates loss when it's hot and dry (maybe?)"
        # Actually, let's keep it simple:
        # A systematic bias that varies sinusoidally over the month (representing an organic drift)
        time_index = np.arange(len(df))
        seasonal_drift = 0.02 * np.sin(time_index / (24 * 7)) * base_energy # Weekly wobble of 2%
        
        # 4. Sensor/Random Noise (The unlearnable part)
        noise = np.random.normal(0, 0.015, size=len(df)) * base_energy # 1.5% random noise
        
        # Total Real Energy
        # We apply these residuals to the base 'actual' (which includes dust/temp losses from physics)
        
        true_energy = base_energy + temp_residual + low_light_residual + seasonal_drift + noise
        
        # Physics constraints
        true_energy = np.maximum(true_energy, 0.0)
        
        # Add to dataframe
        df['actual_truth_kwh'] = true_energy
        
        # Calculate the "True Residual" (Target for ML)
        # Truth - Physics
        df['true_residual_kwh'] = df['actual_truth_kwh'] - df['actual_energy_kwh']
        
        return df

if __name__ == "__main__":
    # Test
    try:
        from degradation_model import calculate_energy_metrics
        from data_loader import fetch_nasa_power_data
        
        print("Fetching data...")
        raw_df = fetch_nasa_power_data(days=30)
        print("Running Physics...")
        # No cleaning for baseline
        physics_df = calculate_energy_metrics(raw_df)
        
        print("Generating Synthetic Ground Truth...")
        gen = SyntheticTruthGenerator()
        truth_df = gen.generate_truth(physics_df)
        
        print("\n--- Verification ---")
        print(truth_df[['datetime', 'irradiance', 'actual_energy_kwh', 'actual_truth_kwh', 'true_residual_kwh']].head(10))
        
        mse = np.mean(truth_df['true_residual_kwh']**2)
        print(f"\nMean Squared Error (Physics vs Truth): {mse:.6f}")
        print("If this runs, ground truth generation is working.")
        
    except ImportError as e:
        print(f"Import Error during test: {e}")
