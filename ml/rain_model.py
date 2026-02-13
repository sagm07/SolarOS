
import pandas as pd
import numpy as np

# Rain Intelligence Constants
RAIN_THRESHOLD_MM = 2.0
RAIN_WINDOW_DAYS = 2
CLEANING_EFFICIENCY_GAMMA = 0.4  # Gamma coefficient for rain cleaning (0.2-0.6 typical)

def apply_rain_cleaning(dust_level, rain_amount_mm):
    """
    Apply physics-based rain cleaning to current dust level.
    
    Formula:
    Dust_new = Dust_current * (1 - gamma * RainAmount)
    
    We clip the cleaning factor so rain doesn't make dust negative.
    Gamma * RainAmount represents the fraction of dust removed.
    For Gamma=0.4, 2.5mm of rain -> 1.0 (100%) removal?
    No, usually it's exponential or asymptotic. 
    But for this approved simplified model: linear reduction.
    We cap reduction at 95% for a single rain event to be realistic (never perfectly clean).
    """
    reduction_factor = CLEANING_EFFICIENCY_GAMMA * rain_amount_mm
    reduction_factor = min(reduction_factor, 0.95) # Cap at 95% removal
    
    return dust_level * (1.0 - reduction_factor)

def check_rain_forecast_wait(df, current_date=None, window_days=RAIN_WINDOW_DAYS, threshold_mm=RAIN_THRESHOLD_MM):
    """
    Check if we should WAIT for rain based on forecast window.
    
    Args:
        df (pd.DataFrame): DataFrame with 'datetime' and 'precipitation'
        current_date (pd.Timestamp): The date to start checking from (inclusive).
        window_days (int): forward looking window.
        threshold_mm (float): rain threshold.
        
    Returns:
        (bool, str): (ShouldWait, Reason)
    """
    if 'precipitation' not in df.columns:
        return False, "No precipitation data"
        
    if current_date is None:
        current_date = df['datetime'].iloc[0]
        
    # Get window slice
    start_time = pd.to_datetime(current_date)
    end_time = start_time + pd.Timedelta(days=window_days)
    
    mask = (df['datetime'] >= start_time) & (df['datetime'] < end_time)
    window_df = df.loc[mask]
    
    if window_df.empty:
        return False, {"decision": "PROCEED", "message": "End of data or no forecast available for the window."}
        
    # Sum precipitation in window
    upcoming_rain = window_df['precipitation'].sum()
    
    if upcoming_rain >= threshold_mm:
        # Estimate natural cleaning
        reduction_est = min(CLEANING_EFFICIENCY_GAMMA * upcoming_rain, 0.95)
        
        # Placeholder for water saved and sustainability boost estimates
        # These would typically depend on specific system parameters (e.g., panel area, cleaning water usage)
        # For this example, we'll use illustrative values.
        estimated_water_saved_liters = upcoming_rain * 0.5 # Example: 0.5 liters saved per mm of rain
        net_sustainability_score_boost = reduction_est * 100 # Example: 100 points for full reduction
        
        reason = {
            "decision": "WAIT",
            "rain_mm": float(upcoming_rain),
            "dust_reduction_estimate": float(reduction_est),
            "water_saved_estimate_liters": float(estimated_water_saved_liters),
            "net_sustainability_score_boost": float(net_sustainability_score_boost),
            "message": f"Rain forecast: {upcoming_rain:.1f}mm in next {window_days} days. Estimated {reduction_est:.0%} natural dust reduction."
        }
        return True, reason
        
    return False, {"decision": "PROCEED", "message": "No significant rain expected."}
