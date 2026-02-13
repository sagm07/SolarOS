"""
SolarOS Backend — single clean endpoint for SolarOS analysis.

Run locally (from project root):
  uvicorn backend.main:app --reload
"""

import os
import sys
from typing import Optional

# Ensure project root is on path so `ml` resolves from any cwd
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ml.scenario_analysis import compare_30day_scenarios

app = FastAPI(title="SolarOS API")

# CORS - Update allow_origins with your frontend domain for production
# Example: allow_origins=["https://your-frontend.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """
    Health check endpoint for deployment monitoring.
    Returns immediately with status OK.
    """
    return {"status": "ok", "service": "SolarOS API"}


@app.get("/analyze")
def analyze(
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    carbon_weight: float = 1.0,
    cleaning_cost: float = 1500.0,
):
    """
    Single clean API for the frontend.

    Query Parameters:
        latitude: Location latitude (default: Chennai)
        longitude: Location longitude (default: Chennai)
        carbon_weight: Weight for carbon in decision (0-1, default: 1.0)
        cleaning_cost: Cost of cleaning in INR (default: 1500)

    Returns:
        {
          "recommendation": "CLEAN" | "WAIT",
          "cleaning_date": "YYYY-MM-DD" | null,
          "total_output_gain_percent": float,
          "recoverable_capture_percent": float,
          "additional_energy_kwh": float,
          "carbon_saved_kg": float,
          "net_economic_gain_inr": float,
          "water_used_liters": float
        }
    """
    
    result = compare_30day_scenarios(
        latitude=latitude,
        longitude=longitude,
        carbon_weight=carbon_weight,
        cleaning_cost_inr=cleaning_cost
    )

    if result.get("error") or not result.get("comparison"):
        raise HTTPException(status_code=503, detail=result.get("error", "Analysis failed"))

    no_clean = result["scenario_no_cleaning"] or {}
    with_clean = result["scenario_with_cleaning"] or {}
    comp = result["comparison"] or {}

    net_gain = float(comp.get("net_economic_gain_inr", 0.0))
    recommendation = "CLEAN" if net_gain > 0 else "WAIT"

    return {
        "recommendation": recommendation,
        "cleaning_date": with_clean.get("cleaning_date"),
        "total_output_gain_percent": round(float(comp.get("total_output_gain_percent", 0.0)), 2),
        "recoverable_capture_percent": round(float(comp.get("recoverable_capture_percent", 0.0)), 2),
        "additional_energy_kwh": round(float(comp.get("additional_energy_gained_kwh", 0.0)), 2),
        "carbon_saved_kg": round(float(comp.get("carbon_saved_kg", 0.0)), 2),
        "net_economic_gain_inr": round(net_gain, 2),
        "water_used_liters": float(comp.get("water_used_liters", 500.0)),
    }


@app.get("/rain-forecast")
def rain_forecast(
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    days: int = 7,
):
    """
    Rain Intelligence API - Check if cleaning should be deferred due to upcoming rain.
    """
    from ml.data_loader import fetch_nasa_power_data
    from ml.rain_model import check_rain_forecast_wait
    
    df = fetch_nasa_power_data(latitude=latitude, longitude=longitude, days=days)
    
    if df.empty:
        return {"error": "No weather data available"}
    
    should_wait, reason = check_rain_forecast_wait(df, window_days=days)
    
    return {
        "should_wait": should_wait,
        "decision": reason.get("decision", "PROCEED"),
        "rain_forecast_mm": reason.get("rain_mm", 0.0),
        "dust_reduction_estimate": reason.get("dust_reduction_estimate", 0.0),
        "water_saved_liters": reason.get("water_saved_estimate_liters", 0.0),
        "sustainability_boost": reason.get("net_sustainability_score_boost", 0.0),
        "message": reason.get("message", ""),
    }


@app.post("/optimize-farms")
async def optimize_farms(request: dict):
    """
    Multi-Farm Portfolio Optimizer
    
    Body:
        {
          "farms": [...],
          "water_budget": float,
          "mode": str
        }
    """
    from ml.multi_farm_optimizer import SolarFarm, MultiSiteOptimizer
    from ml.data_loader import fetch_nasa_power_data
    
    farms = request.get("farms", [])
    water_budget = request.get("water_budget", 1000.0)
    mode = request.get("mode", "PROFIT")
    
    # Create farm objects
    farm_objects = []
    for f in farms:
        farm = SolarFarm(
            name=f.get("name", "Farm"),
            location=(f.get("latitude", 13.0827), f.get("longitude", 80.2707)),
            panel_area_m2=f.get("panel_area", 1000),
            dust_rate_factor=f.get("dust_rate", 1.0),
            electricity_price_inr=f.get("electricity_price", 6.0),
            cleaning_water_usage_liters=f.get("water_usage", 500)
        )
        farm_objects.append(farm)
    
    # Fetch shared data (use first farm's location)
    df = fetch_nasa_power_data(
        latitude=farms[0].get("latitude", 13.0827),
        longitude=farms[0].get("longitude", 80.2707),
        days=30
    )
    
    # Run optimizer
    optimizer = MultiSiteOptimizer(farm_objects, water_budget)
    selected, water_used, total_benefit = optimizer.optimize(df, mode=mode)
    
    return {
        "selected_farms": [f.name for f in selected],
        "water_used": water_used,
        "total_benefit": total_benefit,
        "total_energy": sum(f.energy_recovered for f in selected),
        "total_co2": sum(f.co2_saved for f in selected),
    }
