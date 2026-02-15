
import pandas as pd
import numpy as np
from datetime import timedelta

# Rain Intelligence Constants
# NOTE: Physics constants (GAMMA) are now centralized in degradation_model.py
# We keep threshold here for forecasting decisions
RAIN_THRESHOLD_MM = 2.0
RAIN_WINDOW_DAYS = 2

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
        # We need to import the GAMMA from degradation model to be consistent, or just use a reference value for estimation
        # For forecast estimation, 0.4 is fine as an approximation
        EST_GAMMA = 0.4
        reduction_est = min(EST_GAMMA * upcoming_rain, 0.95)
        
        estimated_water_saved_liters = upcoming_rain * 0.5 
        net_sustainability_score_boost = reduction_est * 100 
        
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
