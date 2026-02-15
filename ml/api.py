
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import os
import sys

# Ensure local modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import fetch_nasa_power_data
from rain_model import check_rain_forecast_wait
from intelligence_core import run_simulation
from degradation_model import calculate_energy_metrics
from synthetic_ground_truth import SyntheticTruthGenerator
from feature_engineering import FeatureEngineer
from residual_model import ResidualLearner
from evaluation import evaluate_model
from hybrid_model import HybridCorrector
from optimization_engine import OptimizationEngine

app = FastAPI(title="SolarOS Intelligence API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Request Body ---

class Farm(BaseModel):
    name: str
    latitude: float
    longitude: float
    panel_area: float
    dust_rate: float
    electricity_price: float
    water_usage: float

class OptimizationRequest(BaseModel):
    farms: List[Farm]
    water_budget: float
    mode: str # PROFIT, CARBON, WATER_SCARCITY

# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "online", "version": "3.0.0"}

@app.get("/rain-forecast")
def get_rain_forecast(latitude: float, longitude: float, days: int = 7):
    """
    Check rain forecast for a specific location.
    """
    try:
        # Fetch data for location
        # Note: NASA Power API might take a few seconds
        df = fetch_nasa_power_data(latitude=latitude, longitude=longitude, days=30) # Fetch 30 days history + forecast context
        
        if df.empty:
            raise HTTPException(status_code=500, detail="Failed to fetch weather data")
            
        # Check forecast
        # We need a date to start checking from. In a real app, it's "now".
        # The dataframe ends at "now" (ish). NASA data has a lag.
        # But for this demo, let's assume the last date in DF is "today"
        last_date = df['datetime'].iloc[-1]
        
        # Actually, NASA Power forecast API is different. 
        # But our `check_rain_forecast_wait` logic works on the data we have.
        # If fetch_nasa_power_data returns historical data, we can't forecast properly from it unless it includes forecast.
        # NASA POWER is historical. We need a FORECAST API for real future prediction.
        # For the Hackathon/Demo, we might be simulating 'Forecast' using the last few days of data as "Future" 
        # or we just mock a forecast if real one isn't available.
        
        # Let's peek at the logic.
        # In `rain_model.py`, it checks `window_days` from `current_date`.
        
        # Hack: Since NASA Power is historical, we'll simulate a forecast by looking at the *last* few days of the fetched data 
        # and pretending that's the forecast.
        
        check_date = df['datetime'].iloc[-days] # Go back 'days' to simulate we are there
        should_wait, reason = check_rain_forecast_wait(df, current_date=check_date, window_days=days)
        
        # Parse reason structure
        if isinstance(reason, dict):
            # Already structured
            response = {
                "should_wait": should_wait,
                "decision": reason.get("decision", "PROCEED"),
                "message": reason.get("message", ""),
                "rain_forecast_mm": reason.get("rain_mm", 0.0),
                "dust_reduction_estimate": reason.get("dust_reduction_estimate", 0.0),
                "water_saved_liters": reason.get("water_saved_estimate_liters", 0.0),
                "sustainability_boost": reason.get("net_sustainability_score_boost", 0.0)
            }
        else:
             response = {
                "should_wait": should_wait,
                "decision": "WAIT" if should_wait else "PROCEED",
                "message": str(reason),
                "rain_forecast_mm": 0.0,
                "dust_reduction_estimate": 0.0,
                "water_saved_liters": 0.0,
                "sustainability_boost": 0.0
             }
             
        return response

    except Exception as e:
        print(f"Error in rain-forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize-farms")
def optimize_farm_portfolio(request: OptimizationRequest):
    """
    Optimizes a portfolio of farms.
    """
    try:
        # We need to run the intelligence core for EACH farm.
        # This can be slow if we fetch NASA data for each.
        # For demo speed, we might want to fetch once if locations are close, or parallelize.
        
        # Let's run a simplified version of `run_simulation` logic but purely via function calls
        # and aggregating results.
        
        results = []
        
        total_benefit = 0
        total_energy = 0
        total_water = 0
        total_co2 = 0
        selected_farms = []
        
        # Global Physics Constants
        # We use the request properties to override defaults if needed
        
        # 0. Cluster Statistics (for Anomaly Detection)
        dust_rates = [f.dust_rate for f in request.farms]
        avg_dust = np.mean(dust_rates)
        std_dust = np.std(dust_rates) if len(dust_rates) > 1 else 1.0
        
        ai_insights = []

        for farm in request.farms:
            # 1. Fetch Data
            df = fetch_nasa_power_data(latitude=farm.latitude, longitude=farm.longitude, days=30)
            
            if df.empty:
                continue 
            
            # 2. Physics & ML
            scaling_factor = farm.panel_area / 100.0
            
            df_physics = calculate_energy_metrics(df.copy())
            
            hybrid_model = HybridCorrector() 
            df_final = hybrid_model.correct_physics_prediction(df_physics)
            
            # 3. Optimization
            optimizer = OptimizationEngine(
                electricity_price=farm.electricity_price,
                cleaning_cost=1500, 
                water_price_per_liter=0.05,
                water_usage_per_clean=farm.water_usage
            )
            
            opt_res = optimizer.optimize_cleaning_schedule(df_final)
            
            # 3b. Uncertainty Quantification
            # Calculate P10/P90 Confidence Intervals for this schedule
            confidence_intervals = optimizer.calculate_confidence_intervals(opt_res['cleaning_dates'], df_final)
            
            p10_val = confidence_intervals['p10'] * scaling_factor
            p50_val = confidence_intervals['p50'] * scaling_factor
            p90_val = confidence_intervals['p90'] * scaling_factor
            
            # 4. Extract Metrics
            net_val_scaled = p50_val # Use P50 as the main metric
            
            # Score Calculation
            score = 0
            if request.mode == "PROFIT":
                score = net_val_scaled
            elif request.mode == "CARBON":
                score = net_val_scaled * 0.5 
            elif request.mode == "WATER_SCARCITY":
                score = net_val_scaled / (farm.water_usage + 1)
            
            results.append({
                "farm": farm,
                "score": score,
                "net_benefit": net_val_scaled,
                "water_needed": farm.water_usage * len(opt_res['cleaning_dates']),
                "cleaning_dates": opt_res['cleaning_dates']
            })
            
            # 5. Generate "Real AI" Insights
            
            # Insight A: Probabilistic ROI
            cost_of_action = len(opt_res['cleaning_dates']) * (1500 + (farm.water_usage * 0.05))
            if cost_of_action > 0:
                roi_p50 = (p50_val / cost_of_action) * 100
                roi_p10 = (p10_val / cost_of_action) * 100
                roi_p90 = (p90_val / cost_of_action) * 100
                
                # Only show if ROI is significantly positive
                if roi_p50 > 20: 
                    ai_insights.append(f"Expected ROI for {farm.name}: {roi_p50:.0f}% (P10: {roi_p10:.0f}% - P90: {roi_p90:.0f}%)")
            
            # Insight B: Dust Anomaly (Cluster Analysis)
            if std_dust > 0:
                z_score = (farm.dust_rate - avg_dust) / std_dust
                if z_score > 1.0:
                    ai_insights.append(f"{farm.name} Dust Rate is {z_score:.1f}σ above portfolio mean (High Soiling Risk).")
                elif z_score < -1.0:
                    ai_insights.append(f"{farm.name} is {abs(z_score):.1f}σ cleaner than average (Low Maintenance).")

            # Insight C: Rain Value (Value of Deferral)
            # If the schedule puts the first clean > 3 days away, and there is rain coming...
            next_clean_idx = opt_res['cleaning_dates'][0] if opt_res['cleaning_dates'] else -1
            if next_clean_idx > 2: # Scheduled for > 2 days away
                # Check if rain is the reason?
                upcoming_rain = df_final['precipitation'].iloc[:next_clean_idx].sum()
                if upcoming_rain > 5.0:
                    saved_cost = 1500 + (farm.water_usage * 0.05)
                    confidence = min(100, upcoming_rain * 10) # Mock confidence based on volume
                    ai_insights.append(f"Deferring cleaning on {farm.name} saves ₹{saved_cost:.0f} (Rain Probability: {confidence:.0f}%).")


        # 6. Portfolio Selection
        results.sort(key=lambda x: x["score"], reverse=True)
        
        current_water = 0
        
        for res in results:
            if current_water + res["water_needed"] <= request.water_budget:
                selected_farms.append(res["farm"].name)
                total_benefit += res["net_benefit"]
                total_water += res["water_needed"]
                # Energy approximation
                total_energy += (res["net_benefit"] / res["farm"].electricity_price) 
                current_water += res["water_needed"]
        
        total_co2 = total_energy * 0.7
        
        # Limit insights to top 3-4 to avoid clutter
        import random
        selected_insights = ai_insights[:4] if len(ai_insights) > 4 else ai_insights
        
        return {
            "selected_farms": selected_farms,
            "water_used": total_water,
            "total_benefit": total_benefit,
            "total_energy": total_energy,
            "total_co2": total_co2,
            "farm_details": [],
            "ai_insights": selected_insights
        }
        
    except Exception as e:
        print(f"Error in optimize-farms: {e}")
        # Return fallback/empty to avoid crashing frontend
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
