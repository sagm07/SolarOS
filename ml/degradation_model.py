import pandas as pd
import numpy as np
from datetime import timedelta

def calculate_energy_metrics(df, panel_area=100.0, cleaning_dates=None, reference_date=None):
    """
    Simulates solar panel efficiency degradation and energy output using multiplicative losses.

    effective_efficiency = base_efficiency * (1 - dust_level) * (1 - temperature_loss) * (1 - aging_loss)

    Args:
        df (pd.DataFrame): DataFrame containing 'datetime', 'irradiance' (W/m^2), and 'temperature' (C).
        panel_area (float): Area of the solar panels in square meters. Default is 100.0.
        cleaning_dates (list): List of datetime strings or objects representing cleaning events.
        reference_date: Optional datetime for aging baseline (default: first row datetime).

    Returns:
        pd.DataFrame: The input DataFrame with added columns:
            - base_efficiency
            - temperature_loss (fraction 0-1)
            - dust_level (fraction 0-1)
            - aging_loss (fraction 0-1)
            - temp_loss, dust_loss (aliases for compatibility)
            - effective_efficiency
            - ideal_energy_kwh
            - actual_energy_kwh
            - recoverable_energy_kwh
    """
    # FROZEN PHYSICS CONSTANTS (DO NOT CHANGE during ML Training)
    # These represent the "Ideal World" or "datasheet" performance.
    BASE_EFFICIENCY = 0.20
    TEMP_COEFF = 0.004        # 0.4% per °C above 25°C
    REF_TEMP = 25.0
    DUST_ACCUMULATION_RATE = 0.15  # 15% loss over 30 days (Linear approximation)
    DAYS_IN_PERIOD = 30.0
    ANNUAL_DEGRADATION_RATE = 0.005 # 0.5% per year
    
    # Rain Cleaning Physics (Frozen)
    RAIN_CLEANING_GAMMA = 0.4      # Dust reduction efficiency per mm of rain
    RAIN_THRESHOLD = 0.1           # Minimum rain to have any effect

    # Ensure datetime is datetime type
    if not pd.api.types.is_datetime64_any_dtype(df['datetime']):
        df['datetime'] = pd.to_datetime(df['datetime'])

    start_time = df['datetime'].iloc[0]
    ref_time = pd.to_datetime(reference_date) if reference_date is not None else start_time

    # 1. Base Efficiency
    df['base_efficiency'] = BASE_EFFICIENCY

    # 2. Temperature Loss (fraction 0–1): 0.4% per °C above 25°C
    temp_diff = df['temperature'] - REF_TEMP
    df['temperature_loss'] = np.clip(np.where(temp_diff > 0, temp_diff * TEMP_COEFF, 0.0), 0.0, 1.0)
    df['temp_loss'] = df['temperature_loss']  # alias for compatibility

    # 3. Dust Level (fraction 0–1): linear 0% to 15% over 30 days since last cleaning, MINUS rain cleaning
    
    # Pre-calculate days since cleaning for manual cleans
    manual_clean_mask = pd.Series(False, index=df.index)
    if cleaning_dates:
        clean_dt_set = set([pd.to_datetime(d).date() for d in cleaning_dates])
        manual_clean_mask = df['datetime'].dt.date.isin(clean_dt_set)

    # Initialize dust array
    dust_levels = np.zeros(len(df))
    current_dust = 0.0
    
    HOURLY_DUST_RATE = DUST_ACCUMULATION_RATE / (DAYS_IN_PERIOD * 24)
    RAIN_GAMMA = RAIN_CLEANING_GAMMA

    prev_time = start_time
    
    # Convert columns to numpy for speed
    precip_values = df['precipitation'].values if 'precipitation' in df.columns else np.zeros(len(df))
    time_values = df['datetime'].values
    manual_clean_values = manual_clean_mask.values
    
    for i in range(len(df)):
        # Time step check (usually 1 hour)
        # dt = (time_values[i] - prev_time) / np.timedelta64(1, 'h')
        # Simplified: just add hourly rate
        
        # 1. Add Dust
        current_dust += HOURLY_DUST_RATE
        
        # 2. Check for Manual Clean
        # If this hour allows cleaning (e.g., 6 AM?), or just reset if day matches?
        # Let's say cleaning happens at 00:00 or whenever the row is marked.
        # Simplification: if manual_clean_values[i] is True, reset to 0.
        # But cleaning_dates are usually just "dates". We should clean at the start of that date.
        # We handled this by checking date match.
        if manual_clean_values[i]:
            current_dust = 0.0
            
        # 3. Check for Rain Clean (Physics)
        rain_mm = precip_values[i]
        if rain_mm > 0.1: # Threshold for any cleaning effect
             # Apply reduction: dust = dust * (1 - gamma * rain)
             # Cap reduction at 95% per hour to avoid instant perfect clean from 1mm rain
             reduction = min(RAIN_GAMMA * rain_mm, 0.95)
             current_dust = current_dust * (1.0 - reduction)
             
        # Cap max dust at 1.0 (100% block)
        current_dust = min(current_dust, 1.0)
        dust_levels[i] = current_dust
        
        # prev_time = time_values[i]

    df['dust_level'] = dust_levels
    df['dust_loss'] = df['dust_level']  # alias for compatibility

    # 4. Aging Loss (fraction 0–1): annual degradation from reference date
    years_since_ref = (df['datetime'] - ref_time).dt.total_seconds() / (365.25 * 24 * 3600)
    years_since_ref = np.maximum(years_since_ref, 0.0)
    
    # Import Advanced Models
    try:
        from advanced_loss_model import calculate_shading_loss, calculate_mismatch_loss, calculate_aging_loss
        USE_ADVANCED = True
    except ImportError:
        USE_ADVANCED = False
        
    if USE_ADVANCED:
        # Vectorized Aging (Bath-tub or Linear, let's use Linear for standard run)
        # For array operations, we can map or vectorise.
        # Simple linear for now to keep speed, unless we want the bath tub.
        df['aging_loss'] = np.clip(years_since_ref * ANNUAL_DEGRADATION_RATE, 0.0, 1.0)
    else:
        df['aging_loss'] = np.clip(years_since_ref * ANNUAL_DEGRADATION_RATE, 0.0, 1.0)

    # 5. Advanced Losses: Shading & Mismatch
    if USE_ADVANCED:
        # Shading
        hour_of_day = df['datetime'].dt.hour
        df['shading_loss'] = hour_of_day.apply(lambda h: calculate_shading_loss(h, latitude=13.0))
        
        # Mismatch
        df['mismatch_loss'] = df['irradiance'].apply(lambda irr: calculate_mismatch_loss(irr))
    else:
        df['shading_loss'] = 0.0
        df['mismatch_loss'] = 0.0

    # 6. Effective Efficiency (multiplicative)
    # effective_eff = base * (1-dust) * (1-temp) * (1-age) * (1-shade) * (1-mismatch)
    
    # CLAMP LOSSES per User Request to prevent explosion
    df['dust_level'] = df['dust_level'].clip(upper=0.30)
    df['temperature_loss'] = df['temperature_loss'].clip(upper=0.15)
    df['aging_loss'] = df['aging_loss'].clip(upper=0.05)
    df['mismatch_loss'] = df['mismatch_loss'].clip(upper=0.10) # Redundant but safe
    
    df['effective_efficiency'] = (
        df['base_efficiency']
        * (1.0 - df['dust_level'])
        * (1.0 - df['temperature_loss'])
        * (1.0 - df['aging_loss'])
        * (1.0 - df['shading_loss'])
        * (1.0 - df['mismatch_loss'])
    )
    df['effective_efficiency'] = df['effective_efficiency'].clip(lower=0.0)
    
    # Calculate Overall Health Score
    # User Request: Health = 100 * (effective / base)
    # This is essentially the Performance Ratio (PR) relative to STC/base
    # We use the mean of the ratio, or ratio of the means? 
    # Usually instantaneous health is this ratio.
    # To get a single scalar for the "Health Score" later, we'll take the mean of this column
    # or calculate it row-wise here.
    df['health_score'] = df['effective_efficiency'] / df['base_efficiency']
    
    # 7. Energy Calculation (kWh)
    # Energy (kWh) = Irradiance (W/m^2) * Area (m^2) * Efficiency * Time (h) / 1000
    # Since data is hourly, Time = 1 hour.
    df['ideal_energy_kwh'] = (df['irradiance'] * panel_area * df['base_efficiency']) / 1000.0
    df['actual_energy_kwh'] = (df['irradiance'] * panel_area * df['effective_efficiency']) / 1000.0

    # 7. Recoverable Energy
    # Ideal - Actual
    df['recoverable_energy_kwh'] = df['ideal_energy_kwh'] - df['actual_energy_kwh']
    
    return df

if __name__ == "__main__":
    # Test locally
    try:
        from data_loader import fetch_nasa_power_data
        print("Fetching real data for testing...")
        df = fetch_nasa_power_data(days=30)
    except ImportError:
        print("data_loader module not found. Generating dummy data...")
        # Dummy data generation if loader not found
        dates = pd.date_range(start='2023-01-01', periods=720, freq='h')
        df = pd.DataFrame({
            'datetime': dates,
            'irradiance': np.random.uniform(0, 1000, 720), # Random irradiance 0-1000 W/m2
            'temperature': np.random.uniform(20, 35, 720)  # Random temp 20-35 C
        })
        # Simulate night
        df.loc[df['datetime'].dt.hour < 6, 'irradiance'] = 0
        df.loc[df['datetime'].dt.hour > 18, 'irradiance'] = 0

    if not df.empty:
        df_processed = calculate_energy_metrics(df)
        
        print("\nProcessed Data Head:")
        print(df_processed[['datetime', 'effective_efficiency', 'recoverable_energy_kwh']].head())
        
        print("\nProcessed Data Tail:")
        print(df_processed[['datetime', 'effective_efficiency', 'recoverable_energy_kwh']].tail())
        
        # Validation checks
        print("\n--- Validation ---")
        
        # Check if effective efficiency decreases (trend)
        # We compare daily averages to smooth out temp fluctuations
        daily_eff = df_processed.resample('D', on='datetime')['effective_efficiency'].mean()
        print(f"Efficiency Start (Day 1 avg): {daily_eff.iloc[0]:.4f}")
        print(f"Efficiency End (Day 30 avg): {daily_eff.iloc[-1]:.4f}")
        if daily_eff.iloc[-1] < daily_eff.iloc[0]:
            print("Unknown Check: Effective efficiency decreases over time (PASS)")
        else:
             print("Check: Effective efficiency decrease NOT detected (FAIL/INCONCLUSIVE due to temp?)")

        # Check if recoverable energy increases (trend)
        # Note: This depends on irradiance. If last day is cloudy, recoverable might be low. 
        # But dust loss factor increases, so 'potential' recoverable loss per unit irradiance increases.
        # Let's check the dust loss component specifically.
        print(f"Dust Loss Start: {df_processed['dust_loss'].iloc[0]:.4f}")
        print(f"Dust Loss End: {df_processed['dust_loss'].iloc[-1]:.4f}")
        
        total_recoverable = df_processed['recoverable_energy_kwh'].sum()
        print(f"Total Recoverable Energy over period: {total_recoverable:.2f} kWh")
        
    else:
        print("No data to process.")
