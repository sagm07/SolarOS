
import numpy as np
import pandas as pd

def calculate_shading_loss(hour_of_day, day_of_year=1, latitude=13.0, gcr=0.4):
    """
    Estimate row-to-row shading loss based on simple geometry.
    
    Args:
        hour_of_day (float): 0-23
        day_of_year (int): 1-365 (Approximate sun declination)
        latitude (float): Site latitude
        gcr (float): Ground Coverage Ratio (Panel Width / Row Pitch). 0.4 is typical.
        
    Returns:
        float: Shading factor (0.0 = no shade, 1.0 = full shade)
        
    Note: Real shading is complex. This is a "tub-shape" curve approximation:
    High shading at sunrise/sunset, zero at noon.
    """
    # Simple hour angle model: Noon = 0, +/- from there
    # Sunrise/Sunset approx 6am/6pm for equator-ish
    if hour_of_day < 6 or hour_of_day > 18:
        return 1.0 # Night / Full shade
        
    # Normalized position: 0 at 6am, 1 at noon, 0 at 6pm?
    # No, 0 shading at noon.
    
    # Parabolic approximation for shading impact
    # Shade is high when sun is low (close to 6 and 18)
    time_from_noon = abs(hour_of_day - 12)
    
    # Critical angle where shading starts?
    # Let's say shading happens when > 4 hours from noon (before 8am, after 4pm)
    if time_from_noon < 4:
        return 0.0
        
    # Between 4 and 6 hours from noon, shading ramps up
    # 4h -> 0%
    # 6h -> 100% (or max usable)
    excess = time_from_noon - 4
    loss = excess / 2.0 # Linear ramp to 100%
    
    return min(max(loss, 0.0), 1.0) * 0.5 # Max 50% loss due to bypass diodes saving some strings

def calculate_mismatch_loss(irradiance, rated_mismatch=0.01):
    """
    Spectral/Low-light mismatch loss.
    Inverters and panels are less efficient at low irradiance.
    """
    if irradiance <= 0:
        return 0.0 # No light = No mismatch loss (energy is 0 anyway)
        
    # Loss increases as irradiance drops below 200 W/m2
    # But we must clamp it to avoid unrealistic values
    loss = rated_mismatch
    
    if irradiance < 200:
        # Exponential increase in loss
        # at 200 -> rated_mismatch (1%)
        # at 50 -> maybe 3-4%?
        # Formula: Base + (200-Irr)/200 * 0.05
        low_light_penalty = 0.05 * (200 - irradiance) / 200
        loss += low_light_penalty
        
    # Cap mismatch at 10% (0.10) to prevent "broken system" flags on just cloudy days
    return min(loss, 0.10)

def calculate_aging_loss(years_active, rate_per_year=0.005, model='linear'):
    """
    Calculate efficiency loss due to aging.
    
    Args:
        years_active (float): Age of plant
        rate_per_year (float): Base rate (0.5%)
        model (str): 'linear' or 'exponential' (bath-tub)
    """
    if model == 'linear':
        return years_active * rate_per_year
        
    if model == 'bath_tub':
        # Infant mortality (high first year) + Linear + Wear-out (>20 years)
        infant = 0.01 * np.exp(-years_active) # Starts at 1%, decays fast
        linear = years_active * rate_per_year
        wearout = 0.0 
        if years_active > 20:
             wearout = 0.01 * (years_active - 20)**2
             
        return infant + linear + wearout
        
    return years_active * rate_per_year
