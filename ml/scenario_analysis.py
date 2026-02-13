"""
30-day scenario comparison: no cleaning vs cleaning at intelligence-engine recommended date.

Reports both metrics for pitch:
- Total output gain %: (additional_energy / total_energy_no_clean) × 100  (~0.5%)
- Recoverable capture %: (additional_energy / total_recoverable_no_clean) × 100  (~4.5%)

Also: carbon saved, net economic gain, water efficiency (kWh per liter), and
scaled net gain for 1 MW (~5000 m²) for storytelling.
"""

import sys
import os
from typing import Optional

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_loader import fetch_nasa_power_data
from degradation_model import calculate_energy_metrics


# Economic and environmental constants (aligned with intelligence_core)
DEFAULT_ELECTRICITY_PRICE_INR = 6.0   # per kWh
DEFAULT_CARBON_FACTOR = 0.7          # kg CO2 per kWh
DEFAULT_WATER_USAGE_LITERS = 500.0
DEFAULT_WATER_COST_PER_LITER = 0.05
DEFAULT_CLEANING_COST_INR = DEFAULT_WATER_USAGE_LITERS * DEFAULT_WATER_COST_PER_LITER


# Scaling: 100 m² reference installation; 1 MW ~ 5000 m²
REFERENCE_PANEL_AREA_M2 = 100.0
SCALED_1MW_PANEL_AREA_M2 = 5000.0   # ~1 MW solar farm
PROJECTION_DAYS = 7                 # Trigger when projected 7-day recoverable > cost


def get_recommended_cleaning_date(
    df: pd.DataFrame,
    electricity_price_inr: float = DEFAULT_ELECTRICITY_PRICE_INR,
    cleaning_cost_inr: float = DEFAULT_CLEANING_COST_INR,
    projection_days: int = PROJECTION_DAYS,
    carbon_weight: float = 1.0,
    carbon_factor: float = DEFAULT_CARBON_FACTOR,
) -> Optional[pd.Timestamp]:
    """
    Recommend cleaning on the first day when *projected* recoverable value
    (energy + weighted carbon) over the next `projection_days` days exceeds cleaning cost.
    """
    if df.empty:
        return None
    
    CARBON_PRICE_INR_PER_KG = 75.0
    
    processed = calculate_energy_metrics(df.copy(), cleaning_dates=[])
    daily_recoverable = processed.resample("D", on="datetime")["recoverable_energy_kwh"].sum()
    if len(daily_recoverable) < projection_days + 1:
        return None
    # Start from day 1 so we don't recommend cleaning before meaningful dust buildup
    for i in range(1, len(daily_recoverable) - projection_days + 1):
        projected_kwh = daily_recoverable.iloc[i : i + projection_days].sum()
        
        # Include weighted carbon value in threshold
        energy_value = projected_kwh * electricity_price_inr
        carbon_saved = projected_kwh * carbon_factor
        carbon_value = carbon_saved * CARBON_PRICE_INR_PER_KG * carbon_weight
        total_value = energy_value + carbon_value
        
        if total_value > cleaning_cost_inr:
            return daily_recoverable.index[i]
    return None


def run_scenario(
    df: pd.DataFrame,
    cleaning_dates: Optional[list] = None,
    panel_area: float = 100.0,
) -> dict:
    """
    Run degradation model for one scenario and return total energy and total recoverable.
    """
    if cleaning_dates is None:
        cleaning_dates = []
    processed = calculate_energy_metrics(df.copy(), panel_area=panel_area, cleaning_dates=cleaning_dates)
    return {
        "total_energy_kwh": float(processed["actual_energy_kwh"].sum()),
        "total_recoverable_kwh": float(processed["recoverable_energy_kwh"].sum()),
    }


def compute_comparison(
    no_clean: dict,
    with_clean: dict,
    cleaning_cost_inr: float,
    carbon_factor: float,
    electricity_price_inr: float,
    water_used_liters: float = DEFAULT_WATER_USAGE_LITERS,
    panel_area_m2: float = REFERENCE_PANEL_AREA_M2,
    carbon_weight: float = 1.0,  # NEW: carbon importance weight (0-1)
) -> dict:
    """
    From scenario totals, compute:
    - additional_energy_gained_kwh
    - total_output_gain_percent: (additional / total_energy_no_clean) × 100  (~0.5%)
    - recoverable_capture_percent: (additional / total_recoverable_no_clean) × 100  (e.g. 4.5%)
    - carbon_saved_kg, net_economic_gain_inr
    - water_efficiency_ratio: kWh per liter of water
    - scaled_net_gain_1mw_inr: net gain scaled to ~1 MW (5000 m²) for storytelling
    """
    additional_kwh = with_clean["total_energy_kwh"] - no_clean["total_energy_kwh"]
    total_energy_no_clean = no_clean["total_energy_kwh"]
    total_recoverable_no_clean = no_clean["total_recoverable_kwh"]

    if total_energy_no_clean > 0:
        total_output_gain_percent = (additional_kwh / total_energy_no_clean) * 100.0
    else:
        total_output_gain_percent = 0.0
    if total_recoverable_no_clean > 0:
        recoverable_capture_percent = (additional_kwh / total_recoverable_no_clean) * 100.0
    else:
        recoverable_capture_percent = 0.0

    carbon_saved_kg = additional_kwh * carbon_factor
    value_gained_inr = additional_kwh * electricity_price_inr
    
    # Carbon monetization with weight
    # Using shadow carbon price for sustainability-aligned operators
    # Reflects true environmental cost including externalities
    CARBON_PRICE_INR_PER_KG = 75.0  # Internal shadow pricing (₹50-150 range for industrial ops)
    carbon_value_inr = carbon_saved_kg * CARBON_PRICE_INR_PER_KG * carbon_weight
    
    # Net sustainability score includes weighted carbon value
    net_economic_gain_inr = value_gained_inr + carbon_value_inr - cleaning_cost_inr
    
    print(f"[SCORE DEBUG] Energy value: ₹{value_gained_inr:.2f}, Carbon value (weighted): ₹{carbon_value_inr:.2f}, Cost: ₹{cleaning_cost_inr:.2f}")
    print(f"[SCORE DEBUG] Net Sustainability Score: ₹{net_economic_gain_inr:.2f}")

    if water_used_liters > 0:
        water_efficiency_ratio = additional_kwh / water_used_liters
    else:
        water_efficiency_ratio = 0.0

    scale_factor = SCALED_1MW_PANEL_AREA_M2 / panel_area_m2 if panel_area_m2 > 0 else 1.0
    scaled_net_gain_1mw_inr = net_economic_gain_inr * scale_factor

    return {
        "additional_energy_gained_kwh": round(additional_kwh, 4),
        "total_output_gain_percent": round(total_output_gain_percent, 2),
        "recoverable_capture_percent": round(recoverable_capture_percent, 2),
        "carbon_saved_kg": round(carbon_saved_kg, 2),
        "net_economic_gain_inr": round(net_economic_gain_inr, 2),
        "water_used_liters": water_used_liters,
        "water_efficiency_ratio_kwh_per_liter": round(water_efficiency_ratio, 4),
        "scaled_net_gain_1mw_inr": round(scaled_net_gain_1mw_inr, 2),
        "scaling_note": f"Reference {panel_area_m2:.0f} m²; 1 MW (~{SCALED_1MW_PANEL_AREA_M2:.0f} m²) scale.",
    }


def compare_30day_scenarios(
    days: int = 30,
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    panel_area: float = 100.0,
    electricity_price_inr: float = DEFAULT_ELECTRICITY_PRICE_INR,
    carbon_factor: float = DEFAULT_CARBON_FACTOR,
    cleaning_cost_inr: Optional[float] = None,
    cleaning_date_override: Optional[str] = None,
    carbon_weight: float = 1.0,  # NEW: carbon importance (0-1)
) -> dict:
    """
    Compare two 30-day scenarios: no cleaning vs cleaning at recommended date.

    Uses the same logic as the intelligence engine to pick the recommended
    cleaning date (first day when cumulative recoverable value exceeds cleaning cost),
    unless `cleaning_date_override` is provided (YYYY-MM-DD).

    Returns a structured dictionary with both scenario results and comparison metrics.
    """
    if cleaning_cost_inr is None:
        cleaning_cost_inr = DEFAULT_CLEANING_COST_INR
    
    print(f"\n[ANALYSIS START] lat={latitude:.4f}, lng={longitude:.4f}, carbon_weight={carbon_weight:.2f}, cleaning_cost=₹{cleaning_cost_inr:.2f}")

    df = fetch_nasa_power_data(latitude=latitude, longitude=longitude, days=days)
    if df.empty:
        return {
            "error": "No data fetched",
            "scenario_no_cleaning": None,
            "scenario_with_cleaning": None,
            "comparison": None,
        }
    
    print(f"[DATA] Mean irradiance: {df['irradiance'].mean():.2f} W/m²")

    # Recommended cleaning date
    if cleaning_date_override:
        cleaning_date = pd.to_datetime(cleaning_date_override)
    else:
        cleaning_date = get_recommended_cleaning_date(
            df.copy(),
            electricity_price_inr=electricity_price_inr,
            cleaning_cost_inr=cleaning_cost_inr,
            carbon_weight=carbon_weight,  # NEW: Pass through
            carbon_factor=carbon_factor,
        )
    
    print(f"[RECOMMENDATION] Cleaning date: {cleaning_date.date() if cleaning_date else 'WAIT (no cleaning recommended)'}")

    # Scenario 1: no cleaning
    no_clean = run_scenario(df, cleaning_dates=[], panel_area=panel_area)
    scenario_no_cleaning = {
        "total_energy_kwh": round(no_clean["total_energy_kwh"], 2),
        "total_recoverable_kwh": round(no_clean["total_recoverable_kwh"], 2),
    }

    # Scenario 2: cleaning at recommended date (or no cleaning if none recommended)
    if cleaning_date is not None:
        with_clean = run_scenario(df, cleaning_dates=[cleaning_date], panel_area=panel_area)
        scenario_with_cleaning = {
            "cleaning_date": str(cleaning_date.date()),
            "total_energy_kwh": round(with_clean["total_energy_kwh"], 2),
            "total_recoverable_kwh": round(with_clean["total_recoverable_kwh"], 2),
        }
        comparison = compute_comparison(
            no_clean,
            with_clean,
            cleaning_cost_inr=cleaning_cost_inr,
            carbon_factor=carbon_factor,
            electricity_price_inr=electricity_price_inr,
            water_used_liters=DEFAULT_WATER_USAGE_LITERS,
            panel_area_m2=panel_area,
            carbon_weight=carbon_weight,  # NEW: Pass through
        )
    else:
        scenario_with_cleaning = {
            "cleaning_date": None,
            "total_energy_kwh": scenario_no_cleaning["total_energy_kwh"],
            "total_recoverable_kwh": scenario_no_cleaning["total_recoverable_kwh"],
        }
        comparison = {
            "additional_energy_gained_kwh": 0.0,
            "total_output_gain_percent": 0.0,
            "recoverable_capture_percent": 0.0,
            "carbon_saved_kg": 0.0,
            "net_economic_gain_inr": 0.0,
            "water_used_liters": DEFAULT_WATER_USAGE_LITERS,
            "water_efficiency_ratio_kwh_per_liter": 0.0,
            "scaled_net_gain_1mw_inr": 0.0,
            "scaling_note": f"Reference {panel_area:.0f} m²; 1 MW (~{SCALED_1MW_PANEL_AREA_M2:.0f} m²) scale.",
        }

    period_start = df["datetime"].iloc[0]
    period_end = df["datetime"].iloc[-1]
    
    print(f"[ANALYSIS END]\n")

    return {
        "scenario_no_cleaning": scenario_no_cleaning,
        "scenario_with_cleaning": scenario_with_cleaning,
        "comparison": comparison,
        "period_days": days,
        "period_start_iso": period_start.isoformat() if hasattr(period_start, "isoformat") else str(period_start),
        "period_end_iso": period_end.isoformat() if hasattr(period_end, "isoformat") else str(period_end),
    }


if __name__ == "__main__":
    try:
        result = compare_30day_scenarios()
        if result.get("error"):
            print("Error:", result["error"])
        else:
            # print("Scenario (no cleaning):", result["scenario_no_cleaning"])
            # print("Scenario (with cleaning):", result["scenario_with_cleaning"])
            # print("Comparison:", result["comparison"])
            c = result["comparison"]
            
            if c and c.get("recoverable_capture_percent") is not None and c.get("total_output_gain_percent") is not None:
                print("\n" + "="*40)
                print("SOLAR OS PITCH METRICS")
                print("="*40)
                
                # 1. Core Pitch Line
                print(
                    f"\"SolarOS captured {c['recoverable_capture_percent']}% of recoverable loss, "
                    f"increasing total output by {c['total_output_gain_percent']}% over 30 days.\"\n"
                )
                
                # 2. Scaling Narrative
                scaled_gain = c.get('scaled_net_gain_1mw_inr', 0)
                if scaled_gain > 0:
                    print(
                        f"\"This simulation models a 100 m² installation. Scaling to a 1 MW solar farm (~5,000 m²), "
                        f"this becomes approximately ₹{scaled_gain:,.0f} net gain per cleaning cycle.\"\n"
                    )
                
                # 3. Water Efficiency
                water_eff = c.get('water_efficiency_ratio_kwh_per_liter', 0)
                if water_eff > 0:
                    print(
                        f"\"SolarOS maximizes renewable output per liter of water.\"\n"
                        f"(Metric: {water_eff:.4f} kWh per liter)\n"
                    )

                # Debug / Sanity Check Details
                print("-" * 20)
                print("SANITY CHECK DETAILS:")
                print(f"Additional Energy: {c['additional_energy_gained_kwh']:.2f} kWh")
                print(f"Value of Energy: ₹{c['additional_energy_gained_kwh'] * 6:.2f}") 
                print(f"Cleaning Cost: ₹{c.get('water_used_liters', 500) * 0.05:.2f}")
                print(f"Net Gain (100m²): ₹{c['net_economic_gain_inr']:.2f}")
                print("-" * 20)
    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print("An error occurred. Check error_log.txt")
