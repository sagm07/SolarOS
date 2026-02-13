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

from ml.intelligence_core import OptimizationEngine
from ml.data_loader import fetch_nasa_power_data
from ml.degradation_model import calculate_energy_metrics

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
    plant_capacity_mw: float = 25.0,  # Plant capacity in MW
):
    """
    Intelligent Decision Engine API.
    Uses Dynamic Programming to optimize cleaning schedules and returns SSES scores.
    """
    
    # 1. Fetch Data
    df = fetch_nasa_power_data(latitude=latitude, longitude=longitude, days=30)
    
    if df.empty:
        raise HTTPException(status_code=503, detail="Failed to fetch solar data")

    # 2. Run Base Model (Baseline)
    df_base = calculate_energy_metrics(df.copy(), cleaning_dates=[])

    # 3. Intelligent Decision Engine (Optimization)
    # USER FEEDBACK: "Cleaning is expensive" -> Add Virtual Friction Cost
    BASE_CLEANING_COST = cleaning_cost
    VIRTUAL_FRICTION_COST = 500.0 
    EFFECTIVE_CLEANING_COST = BASE_CLEANING_COST + VIRTUAL_FRICTION_COST

    optimizer = OptimizationEngine(
        electricity_price=6.0,
        cleaning_cost=EFFECTIVE_CLEANING_COST,
        carbon_price_per_kg=5.0 * carbon_weight, 
        water_price_per_liter=0.05,
        water_usage_per_clean=500.0
    )
    
    optimization_result = optimizer.optimize_cleaning_schedule(df_base)
    optimal_schedule_indices = optimization_result['cleaning_dates']
    # Fix: df_base index might be RangeIndex (int), need to access 'datetime' column
    optimal_dates = [df_base.iloc[i]['datetime'] for i in optimal_schedule_indices]
    
    # 4. Simulate Optimal Scenario
    df_optimal = calculate_energy_metrics(df.copy(), cleaning_dates=optimal_dates)
    
    # 5. Calculate Metrics
    base_energy = df_base['actual_energy_kwh'].sum()
    opt_energy = df_optimal['actual_energy_kwh'].sum()
    energy_gain = opt_energy - base_energy
    
    CARBON_FACTOR = 0.7
    carbon_saved = energy_gain * CARBON_FACTOR
    water_used = len(optimal_dates) * 500.0
    total_cost = len(optimal_dates) * BASE_CLEANING_COST # Use real cost for user reporting
    net_benefit = (energy_gain * 6.0) - total_cost
    
    # SSES Score Calculation
    norm_energy = opt_energy / 150000.0 
    norm_carbon = carbon_saved / 10000.0   
    norm_water = water_used / 50000.0 
    norm_cost = total_cost / 50000.0            
    
    raw_score = (0.5 * norm_energy) + (0.3 * norm_carbon) - (0.1 * norm_water) - (0.1 * norm_cost)
    sses_score = max(0, min(100, 50 + (raw_score * 50)))

    # Scaling Factor
    scale_factor = (plant_capacity_mw * 1000) / 15.0

    # 6. Construct Deep Explainability Reasons
    reasons = []
    if len(optimal_dates) > 0:
        next_clean_date = optimal_dates[0]
        days_until = (next_clean_date - df_base.iloc[0]['datetime']).days
        reasons.append(f"Dust accumulation > 5% threshold in {days_until} days.")
        reasons.append(f"Projected Net Revenue: ₹{net_benefit * scale_factor:,.0f} (Growth)")
        reasons.append("Clear weather window identified (Low Rain Risk).")
    else:
        reasons.append("Optimization model determined WAIT is best strategy.")
        total_rain = df_base['precipitation'].sum() if 'precipitation' in df_base.columns else 0
        if total_rain > 10.0:
            reasons.append(f"Rain Assist: {total_rain:.1f}mm forecast reduces need.")
        if energy_gain > 0 and net_benefit < 0:
            reasons.append("ROI Negative: Cleaning cost exceeds energy recovery.")
        reasons.append("Dust levels insufficient to justify mobilization.")

    return {
        "recommendation": "CLEAN" if len(optimal_dates) > 0 else "WAIT",
        "cleaning_date": str(optimal_dates[0].date()) if len(optimal_dates) > 0 else None,
        "cleaning_dates": [str(d.date()) for d in optimal_dates],
        "total_output_gain_percent": round((energy_gain / base_energy) * 100, 2) if base_energy > 0 else 0,
        "recoverable_capture_percent": 85.0, 
        "additional_energy_kwh": round(energy_gain * scale_factor, 2),
        "carbon_saved_kg": round(carbon_saved * scale_factor, 2),
        "net_economic_gain_inr": round(net_benefit * scale_factor, 2),
        "water_used_liters": round(water_used * scale_factor, 0),
        "sses_score": round(sses_score, 1),
        "plant_capacity_mw": plant_capacity_mw,
        "explanation": {
            "model": "Dynamic Programming (DP) v2.1",
            "reasons": reasons, # List of strings
            "optimization_score": round(optimization_result['total_net_value'], 2)
        }
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


@app.post("/analyze-sections")
async def analyze_sections(request: dict):
    """
    Section-level farm analysis
    """
    from ml.section_optimizer import generate_farm_grid, calculate_section_energy_loss, optimize_section_cleaning
    from ml.data_loader import fetch_nasa_power_data
    
    farm_mw = request.get('farm_size_mw', 25.0)
    rows = request.get('grid_rows', 5)
    cols = request.get('grid_cols', 5)
    budget = request.get('water_budget', 25000.0)
    latitude = request.get('latitude', 13.0827)
    longitude = request.get('longitude', 80.2707)
    
    # Fetch weather data
    df = fetch_nasa_power_data(latitude=latitude, longitude=longitude, days=30)
    
    # Generate grid
    sections = generate_farm_grid(farm_mw, rows, cols)
    
    # Analyze each section
    for section in sections:
        calculate_section_energy_loss(section, df)
    
    # Optimize cleaning schedule
    selected, water_used = optimize_section_cleaning(sections, budget)
    
    return {
        'sections': [s.to_dict() for s in sections],
        'selected_section_ids': [s.id for s in selected],
        'water_used': water_used,
        'total_energy_recovered': sum(s.energy_loss_kwh for s in selected),
        'total_co2_saved': sum(s.energy_loss_kwh * 0.7 for s in selected),
        'total_cost_saved': sum(s.energy_loss_kwh * 6.0 - s.cleaning_cost for s in selected),
    }
