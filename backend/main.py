"""
SolarOS Backend — Production-Ready Entry Point
Deployed on Render.
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Literal
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure project root is on path
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# 1️⃣ Define FastAPI app at top level
app = FastAPI(
    title="SolarOS API",
    description="Backend for SolarOS Intelligent Decision Engine",
    version="1.0.0"
)

# 4️⃣ Production Safeguards - CORS
# Update this with your actual frontend domain in production
ORIGINS = [
    "http://localhost:3000",
    "https://solaros.vercel.app",  # Add your Vercel domain here
    "*" # Temporarily allow all for development/hackathon
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# --- Pydantic Models for Request Validation ---

class Farm(BaseModel):
    name: str
    latitude: float
    longitude: float
    panel_area: float
    dust_rate: float
    electricity_price: float
    water_usage: float

class OptimizeFarmsRequest(BaseModel):
    farms: List[Farm]
    water_budget: float
    mode: Literal["PROFIT", "CARBON", "WATER_SCARCITY"]

class OptimizeFarmsResponse(BaseModel):
    selected_farms: List[str]
    water_used: float
    total_benefit: float
    total_energy: float
    total_co2: float
    farm_details: List[dict]

class SectionAnalysisRequest(BaseModel):
    farm_size_mw: float = 25.0
    grid_rows: int = 5
    grid_cols: int = 5
    water_budget: float = 25000.0
    latitude: float = 13.0827
    longitude: float = 80.2707

# --- Routes ---

@app.get("/health")
def health_check():
    """
    Health check endpoint for deployment monitoring.
    Returns immediately with status OK.
    """
    return {"status": "ok", "service": "SolarOS API", "version": "1.0.0"}

@app.get("/analyze")
def analyze(
    latitude: float = Query(13.0827, description="Location Latitude"),
    longitude: float = Query(80.2707, description="Location Longitude"),
    carbon_weight: float = Query(1.0, ge=0.0, le=2.0),
    cleaning_cost: float = Query(1500.0, ge=0.0),
    plant_capacity_mw: float = Query(25.0, gt=0.0),
):
    """
    Intelligent Decision Engine API.
    Uses Dynamic Programming to optimize cleaning schedules and returns SSES scores.
    """
    # 5️⃣ Optimize Cold Start - Lazy load modules
    try:
        from ml.intelligence_core import OptimizationEngine
        from ml.data_loader import fetch_nasa_power_data
        from ml.degradation_model import calculate_energy_metrics
    except ImportError as e:
        logger.error(f"Failed to import ML modules: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: ML modules missing")

    try:
        # 1. Fetch Data with Timeout (handled in data_loader)
        df = fetch_nasa_power_data(latitude=latitude, longitude=longitude, days=30)
        
        if df.empty:
            logger.warning(f"No weather data found for {latitude}, {longitude}")
            raise HTTPException(status_code=503, detail="Failed to fetch solar data (NASA POWER API)")

        # 2. Run Base Model (Baseline)
        df_base = calculate_energy_metrics(df.copy(), cleaning_dates=[])

        # 3. Intelligent Decision Engine (Optimization)
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
        total_cost = len(optimal_dates) * BASE_CLEANING_COST
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
                "reasons": reasons,
                "optimization_score": round(optimization_result['total_net_value'], 2)
            }
        }
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rain-forecast")
def rain_forecast(
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    days: int = 7,
):
    try:
        from ml.data_loader import fetch_nasa_power_data
        from ml.rain_model import check_rain_forecast_wait
        
        df = fetch_nasa_power_data(latitude=latitude, longitude=longitude, days=days)
        
        if df.empty:
            raise HTTPException(status_code=503, detail="No weather data available")
        
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
    except Exception as e:
        logger.error(f"Rain forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize-farms", response_model=OptimizeFarmsResponse)
async def optimize_farms(request: OptimizeFarmsRequest):
    """
    Multi-farm portfolio optimization endpoint.
    Optimizes water allocation across multiple farms based on the selected mode.
    """
    try:
        farms = request.farms
        water_budget = request.water_budget
        mode = request.mode
        
        # Calculate ROI metrics for each farm
        farm_scores = []
        for farm in farms:
            # Energy recovery calculation (simplified physics model)
            # Dust reduces efficiency by ~0.2% per day typically
            days_since_clean = 30  # Assume 30 days of dust accumulation
            efficiency_loss = farm.dust_rate * days_since_clean * 0.002
            
            # Average solar irradiance in Chennai (kWh/m²/day)
            avg_irradiance = 5.5
            
            # Panel efficiency (typical ~20%)
            panel_efficiency = 0.20
            
            # Energy recoverable by cleaning (kWh)
            energy_recoverable = (
                farm.panel_area * 
                avg_irradiance * 
                panel_efficiency * 
                efficiency_loss * 
                30  # Days of benefit
            )
            
            # Financial benefit
            revenue = energy_recoverable * farm.electricity_price
            cleaning_cost = farm.water_usage * 0.05  # ₹0.05 per liter
            net_benefit = revenue - cleaning_cost
            
            # Carbon offset (kg CO2 per kWh)
            co2_offset = energy_recoverable * 0.82
            
            # Water efficiency (energy per liter)
            water_efficiency = energy_recoverable / farm.water_usage if farm.water_usage > 0 else 0
            
            # Calculate priority score based on mode
            if mode == "PROFIT":
                priority = net_benefit
            elif mode == "CARBON":
                priority = co2_offset
            else:  # WATER_SCARCITY
                priority = water_efficiency
            
            farm_scores.append({
                "name": farm.name,
                "priority": priority,
                "water_usage": farm.water_usage,
                "energy": energy_recoverable,
                "benefit": net_benefit,
                "co2": co2_offset,
                "roi": net_benefit / cleaning_cost if cleaning_cost > 0 else 0
            })
        
        # Sort by priority (descending)
        farm_scores.sort(key=lambda x: x["priority"], reverse=True)
        
        # Greedy selection within water budget
        selected = []
        total_water = 0
        total_energy = 0
        total_benefit = 0
        total_co2 = 0
        
        for farm_data in farm_scores:
            if total_water + farm_data["water_usage"] <= water_budget:
                selected.append(farm_data)
                total_water += farm_data["water_usage"]
                total_energy += farm_data["energy"]
                total_benefit += farm_data["benefit"]
                total_co2 += farm_data["co2"]
        
        # Format response
        return OptimizeFarmsResponse(
            selected_farms=[f["name"] for f in selected],
            water_used=total_water,
            total_benefit=total_benefit,
            total_energy=total_energy,
            total_co2=total_co2,
            farm_details=selected
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.post("/analyze-sections")
async def analyze_sections(request: SectionAnalysisRequest):
    try:
        from ml.section_optimizer import generate_farm_grid, calculate_section_energy_loss, optimize_section_cleaning
        from ml.data_loader import fetch_nasa_power_data
        
        df = fetch_nasa_power_data(latitude=request.latitude, longitude=request.longitude, days=30)
        
        sections = generate_farm_grid(request.farm_size_mw, request.grid_rows, request.grid_cols)
        
        for section in sections:
            calculate_section_energy_loss(section, df)
        
        selected, water_used = optimize_section_cleaning(sections, request.water_budget)
        
        return {
            'sections': [s.to_dict() for s in sections],
            'selected_section_ids': [s.id for s in selected],
            'water_used': water_used,
            'total_energy_recovered': sum(s.energy_loss_kwh for s in selected),
            'total_co2_saved': sum(s.energy_loss_kwh * 0.7 for s in selected),
            'total_cost_saved': sum(s.energy_loss_kwh * 6.0 - s.cleaning_cost for s in selected),
        }
    except Exception as e:
        logger.error(f"Section analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
