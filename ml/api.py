
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
        
        for farm in request.farms:
            # 1. Fetch Data (mock or real? Real is better but slow)
            # Let's use the default fetch (Chennai) for all for speed if lat/long are same
            # Or actually fetch.
            # Warning: 4 fetches might take 10s.
            
            # Optimization: 
            df = fetch_nasa_power_data(latitude=farm.latitude, longitude=farm.longitude, days=30)
            
            if df.empty:
                continue # Skip this farm
            
            # 2. Physics & ML
            # Initialize Hybrid Model (Pre-trained?)
            # We should load the trained model once globally if possible.
            # But `HybridCorrector` loads it in __init__.
            train_cutoff = int(len(df) * 0.7)
            
            # Physics
            # Adjust panel area valid for this specific farm logic?
            # degradation_model uses 100m2 by default. We need to scale the *Energy* results.
            # The model returns energy for 100m2.
            # We can scale the final outputs by (farm.panel_area / 100.0)
            scaling_factor = farm.panel_area / 100.0
            
            df_physics = calculate_energy_metrics(df.copy())
            
            # ML Correction
            hybrid_model = HybridCorrector() # Loads default model
            # Note: Model was trained on *some* data. Is it valid here?
            # Ideally we retrain per farm. For demo, we use the pre-trained generic model.
            
            df_final = hybrid_model.correct_physics_prediction(df_physics)
            
            # 3. Optimization
            # Adjust costs based on farm/request params
            optimizer = OptimizationEngine(
                electricity_price=farm.electricity_price,
                cleaning_cost=1500, # Base cost
                water_price_per_liter=0.05,
                water_usage_per_clean=farm.water_usage
            )
            
            opt_res = optimizer.optimize_cleaning_schedule(df_final)
            
            # 4. Extract Metrics
            # Scale energy/benefit by size
            # The optimizer works on the provided DataFrame which is for 100m2.
            # So the 'total_net_value' is for 100m2.
            
            # Net Value (Rupees)
            net_val_unit = opt_res['total_net_value']
            net_val_scaled = net_val_unit * scaling_factor
            
            # Energy (kWh)
            # Sum of *Hybrid* energy for the optimized schedule?
            # The optimizer returns 'total_net_value'. 
            # We need total energy.
            # Let's approximate: Net Value ~ (Energy * Price) - Costs
            # But simpler: Just sum the energy column for the full period?
            # No, optimization changes the *realized* energy by cleaning.
            # We'll stick to the "Potential Benefit" metric for ranking.
            
            # Let's calculate a "Score" for this farm based on the mode
            score = 0
            if request.mode == "PROFIT":
                score = net_val_scaled
            elif request.mode == "CARBON":
                score = net_val_scaled * 0.5 # Proxy
            elif request.mode == "WATER_SCARCITY":
                # Ranking by water efficiency?
                score = net_val_scaled / (farm.water_usage + 1)
            
            results.append({
                "farm": farm,
                "score": score,
                "net_benefit": net_val_scaled,
                "water_needed": farm.water_usage * len(opt_res['cleaning_dates']), # Total water for schedule
                "cleaning_dates": opt_res['cleaning_dates']
            })

        # 5. Portfolio Selection (Knapsack-ish)
        # Sort by Score
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
        
        return {
            "selected_farms": selected_farms,
            "water_used": total_water,
            "total_benefit": total_benefit,
            "total_energy": total_energy,
            "total_co2": total_co2,
            "farm_details": [] # Could populate
        }
        
    except Exception as e:
        print(f"Error in optimize-farms: {e}")
        # Return fallback/empty to avoid crashing frontend
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
