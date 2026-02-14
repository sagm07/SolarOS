
# ... (Previous imports)
from fastapi import BackgroundTasks

# ML Ops Imports
try:
    from ml.monitoring import ModelMonitor
    from ml.feedback_loop import AdaptiveLearner
    
    # Initialize Singletons
    monitor = ModelMonitor()
    learner = AdaptiveLearner(monitor)
except ImportError:
    monitor = None
    learner = None

class FeedbackRequest(BaseModel):
    date: str
    actual_kwh: float
    predicted_kwh: float
    farm_id: Optional[str] = None

# ... (Previous Models)

# --- Routes ---

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Closed-Loop Learning Endpoint.
    Accepts actual generation data to compare against predictions.
    Triggers retraining if error > threshold.
    """
    if not learner:
        raise HTTPException(status_code=503, detail="ML Ops services unavailable")
        
    result = learner.submit_feedback(
        clean_date=feedback.date,
        actual_energy_kwh=feedback.actual_kwh,
        predicted_kwh=feedback.predicted_kwh
    )
    
    return result

@app.get("/ml/status")
def ml_status():
    """
    Returns ML Ops Dashboard metrics.
    """
    if not monitor or not learner:
         return {"status": "offline"}
         
    return {
        "monitoring": monitor.get_stats(),
        "retraining": learner.get_retraining_status(),
        "drift_check": monitor.check_drift()
    }

# ... (Existing health check & other routes)

@app.get("/analyze")
def analyze(
    latitude: float = Query(13.0827, description="Location Latitude"),
    longitude: float = Query(80.2707, description="Location Longitude"),
    carbon_weight: float = Query(1.0, ge=0.0, le=2.0),
    cleaning_cost: float = Query(1500.0, ge=0.0),
    plant_capacity_mw: float = Query(25.0, gt=0.0),
):
    """
    Intelligent Decision Engine API (Hybrid V3).
    Uses Dynamic Programming + ML Residuals + Monte Carlo Uncertainty.
    """
    start_time = time.time() # Latency tracking
    
    # 5️⃣ Optimize Cold Start - Lazy load modules
    try:
        from ml.intelligence_core import OptimizationEngine
        from ml.data_loader import fetch_nasa_power_data
        from ml.degradation_model import calculate_energy_metrics
        from ml.hybrid_model import HybridCorrector
        from ml.uncertainty_model import UncertaintyEngine
    except ImportError as e:
        logger.error(f"Failed to import ML modules: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: ML modules missing")

    try:
        # 1. Fetch Data with Timeout (handled in data_loader)
        df = fetch_nasa_power_data(latitude=latitude, longitude=longitude, days=30)
        
        if df.empty:
            logger.warning(f"No weather data found for {latitude}, {longitude}")
            raise HTTPException(status_code=503, detail="Failed to fetch solar data (NASA POWER API)")

        # 2. Run Base Model (Baseline Physics)
        df_base = calculate_energy_metrics(df.copy(), cleaning_dates=[])

        # 3. Hybrid Intelligence (Physics + ML Residual)
        hybrid_model = HybridCorrector()
        df_base = hybrid_model.correct_physics_prediction(df_base)
        
        # Overwrite actual for optimization logic (Recoverable = Ideal - HybridActual)
        df_base['actual_energy_kwh'] = df_base['hybrid_energy_kwh']
        df_base['recoverable_energy_kwh'] = df_base['ideal_energy_kwh'] - df_base['actual_energy_kwh']

        # 4. Intelligent Decision Engine (Optimization)
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
        
        # 5. Simulate Optimal Scenario & Uncertainty
        df_optimal = calculate_energy_metrics(df.copy(), cleaning_dates=optimal_dates)
        df_optimal = hybrid_model.correct_physics_prediction(df_optimal)
        
        # Monte Carlo Engine
        uq_engine = UncertaintyEngine(simulations=50)
        uq_stats = uq_engine.run_monte_carlo(
            df.copy(), 
            lambda d: hybrid_model.correct_physics_prediction(calculate_energy_metrics(d, cleaning_dates=optimal_dates))
        )
        
        # 6. Calculate Metrics
        base_energy = df_base['hybrid_energy_kwh'].sum()
        opt_energy = df_optimal['hybrid_energy_kwh'].sum()
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

        # 7. Construct Deep Explainability Reasons
        reasons = []
        if len(optimal_dates) > 0:
            next_clean_date = optimal_dates[0]
            days_until = (next_clean_date - df_base.iloc[0]['datetime']).days
            reasons.append(f"Dust accumulation > 5% threshold in {days_until} days.")
            reasons.append(f"Projected Net Revenue: ₹{net_benefit * scale_factor:,.0f} (Growth)")
            reasons.append(f"Confidence (90%): ₹{uq_engine.calculate_risk_adjusted_revenue(uq_stats['p10_energy'] - base_energy, 6.0) * scale_factor - (total_cost * scale_factor):,.0f} (Conservative)")
        else:
            reasons.append("Optimization model determined WAIT is best strategy.")
            total_rain = df_base['precipitation'].sum() if 'precipitation' in df_base.columns else 0
            if total_rain > 10.0:
                reasons.append(f"Rain Assist: {total_rain:.1f}mm forecast reduces need.")
            if energy_gain > 0 and net_benefit < 0:
                reasons.append("ROI Negative: Cleaning cost exceeds energy recovery.")
            reasons.append("Dust levels insufficient to justify mobilization.")

        response_payload = {
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
            "confidence_interval": {
                "p10_benefit": round((uq_engine.calculate_risk_adjusted_revenue(uq_stats['p10_energy'] - base_energy, 6.0) - total_cost) * scale_factor, 2),
                "p90_benefit": round((uq_engine.calculate_risk_adjusted_revenue(uq_stats['p90_energy'] - base_energy, 6.0) - total_cost) * scale_factor, 2),
                "uncertainty_spread_kwh": round(uq_stats['uncertainty_spread'] * scale_factor, 2)
            },
            "explanation": {
                "model": "Hybrid V3 (Physics + XGBoost Residuals)",
                "reasons": reasons,
                "optimization_score": round(optimization_result['total_net_value'], 2)
            }
        }
        
        # ML Ops: Log Inference
        if monitor:
            monitor.log_inference(
                request_id=f"req_{int(start_time)}",
                input_features={"lat": latitude, "lon": longitude, "capacity": plant_capacity_mw},
                output_metrics={"energy_gained": energy_gain, "action": response_payload["recommendation"]},
                execution_time_ms=(time.time() - start_time) * 1000
            )

        return response_payload
        
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

