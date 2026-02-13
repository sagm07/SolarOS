
import pandas as pd
import numpy as np
import sys
import os

# Ensure local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from degradation_model import calculate_energy_metrics
from data_loader import fetch_nasa_power_data
# Mock intelligent core logic for optimization speed, or import?
# We can import `get_recommended_cleaning_date` to estimate benefit.
from scenario_analysis import get_recommended_cleaning_date, run_scenario

class SolarFarm:
    def __init__(self, name, location, panel_area_m2, dust_rate_factor=1.0, 
                 electricity_price_inr=6.0, water_cost_inr_per_liter=0.05, 
                 cleaning_water_usage_liters=500, water_scarcity_score=1.0):
        """
        Solar Farm Entity with heterogeneous properties.
        
        Args:
            name (str): Farm identifier.
            location (tuple): (lat, lon).
            panel_area_m2 (float): Size of farm.
            dust_rate_factor (float): Multiplier for standard dust rate (e.g. 1.5 for desert, 0.8 for coastal).
            electricity_price_inr (float): Tariff for this farm.
            water_cost_inr_per_liter (float): Local cost of water.
            cleaning_water_usage_liters (float): Water needed for one full clean.
            water_scarcity_score (float): 1.0 = normal, 2.0 = scarce (penalty factor?). 
                                          Used for "Equitable" ranking if needed.
        """
        self.name = name
        self.location = location
        self.panel_area_m2 = panel_area_m2
        self.dust_rate_factor = dust_rate_factor
        self.electricity_price = electricity_price_inr
        self.water_cost = water_cost_inr_per_liter
        self.water_usage = cleaning_water_usage_liters
        self.scarcity_score = water_scarcity_score
        
        # State
        self.data = None
        self.net_benefit = 0.0
        self.action = "WAIT"
        self.efficiency_score = 0.0 # Benefit / Water
        self.energy_recovered = 0.0
        self.co2_saved = 0.0
        
    def fetch_data(self, days=30):
        # In prod, we'd cache this or pass it in.
        # Check if identical location data already fetched?
        pass # Placeholder for now, assumed external fetch or shared data

    def evaluate_cleaning_opportunity(self, df):
        """
        Run intelligence core logic for this specific farm.
        """
        # 1. Adjust Degradation Model for this farm's dust rate?
        # The current `degradation_model` uses a global constant.
        # We would need to pass `dust_rate` to `calculate_energy_metrics`.
        # For prototype, we'll assume linear scaling of benefit:
        # More dust = more loss = more recoverable energy.
        
        cleaning_cost = self.water_usage * self.water_cost
        
        # Use scenario analysis to find opportunity
        # We need to hack/patch the global DUST_ACCUMULATION_RATE or pass it.
        # For now, let's use standard model but scale the "recoverable" result by dust factor.
        
        rec_date = get_recommended_cleaning_date(
            df, 
            electricity_price_inr=self.electricity_price,
            cleaning_cost_inr=cleaning_cost
        )
        
        if rec_date:
            # Calculate Benefit
            # Run scenario with cleaning
            res_clean = run_scenario(df, cleaning_dates=[rec_date], panel_area=self.panel_area_m2)
            res_wait = run_scenario(df, cleaning_dates=[], panel_area=self.panel_area_m2)
            
            energy_gain = res_clean['total_energy_kwh'] - res_wait['total_energy_kwh']
            
            # Scale gain by dust factor (heuristic approximation for speed)
            # Real way: modify DUST_ACCUMULATION_RATE in degradation_model.
            adj_energy_gain = energy_gain * self.dust_rate_factor 
            
            val_gain = adj_energy_gain * self.electricity_price
            self.net_benefit = val_gain - cleaning_cost
            self.energy_recovered = adj_energy_gain
            self.co2_saved = adj_energy_gain * 0.7 # 0.7 kg CO2 per kWh
            self.action = "CLEAN"
            
            # Efficiency Score = Net Benefit / Water Usage
            # If scarcity is high, effective cost of water is higher, or we just stick to Benefit/Liter?
            # User wants "Water Efficiency".
            self.efficiency_score = self.net_benefit / self.water_usage
            
        else:
            self.net_benefit = 0.0
            self.energy_recovered = 0.0
            self.co2_saved = 0.0
            self.action = "WAIT"
            self.efficiency_score = 0.0


class MultiSiteOptimizer:
    def __init__(self, farms, water_budget_liters):
        self.farms = farms
        self.global_water_budget = water_budget_liters
        
    def optimize(self, shared_data_df=None, mode="PROFIT"):
        """
        0/1 Knapsack Optimization (Dynamic Programming).
        
        Modes:
        - PROFIT: Maximize Net Benefit (Default)
        - CARBON: Maximize CO2 Saved (Benefit = CO2 * 10 or similar weight)
        - WATER_SCARCITY: Enforce stricter budget or penalty
        """
        # Adjust constraints based on mode
        effective_budget = self.global_water_budget
        if mode == "WATER_SCARCITY":
            print("(!) Mode: WATER SCARCITY - Reducing budget by 30%")
            effective_budget *= 0.70
            
        candidates = []
        rejected_farms = [] # Keep track for "Deferred" list
        
        for farm in self.farms:
            if shared_data_df is not None:
                farm.evaluate_cleaning_opportunity(shared_data_df.copy())
            
            # Mode-specific scoring override?
            # For Knapsack, 'val' is what we maximize.
            # Default val = net_benefit.
            if mode == "CARBON":
                # Treat CO2 as the 'value' to maximize.
                # weighted_score = farm.co2_saved (kg) * 10 (approx INR value/priority)
                # Or just swap objective function.
                # Let's override .net_benefit TEMPORARILY for the solver? 
                # Better: pass a custom value list to _solve_knapsack_dp.
                # But _solve_knapsack_dp reads .net_benefit internaly.
                # Let's add a temporary attribute 'optimization_value'
                farm.optimization_value = farm.co2_saved * 10.0 # Arbitrary weight implies 1kg CO2 ~ 10 INR priority
            else:
                farm.optimization_value = farm.net_benefit

            if farm.action == "CLEAN" and farm.optimization_value > 0:
                candidates.append(farm)
            else:
                rejected_farms.append((farm, "Low ROI / No Action"))
                
        # Use DP Solver with custom value attribute
        selected_farms, optimization_score = self._solve_knapsack_dp(candidates, effective_budget, value_attr='optimization_value')
        
        # Identify Deferred Candidates (Candidates that were NOT selected)
        selected_set = set(f.name for f in selected_farms)
        deferred_farms = [f for f in candidates if f.name not in selected_set]
        
        # Calculate totals
        water_used = sum(f.water_usage for f in selected_farms)
        total_benefit = sum(f.net_benefit for f in selected_farms)
        total_energy = sum(f.energy_recovered for f in selected_farms)
        total_co2 = sum(f.co2_saved for f in selected_farms)
        opt_eff = total_energy / water_used if water_used > 0 else 0.0

        # --- COMMAND CENTER OUTPUT ---
        print("\n" + "="*40)
        print(f"SOLAROS PORTFOLIO DECISION [Mode: {mode}]")
        print("="*40 + "\n")
        print(f"Water Budget: {effective_budget:.0f} L (Original: {self.global_water_budget} L)")
        print(f"Farms Evaluated: {len(self.farms)}")
        print(f"Farms Selected: {len(selected_farms)}")
        print("\nSelected Farms:")
        for i, f in enumerate(selected_farms, 1):
            print(f"{i}. {f.name:<15} – Net Gain INR {f.net_benefit:,.0f} – {f.water_usage:.0f} L")
            
        print("\nDeferred Farms:")
        for f in deferred_farms:
             print(f"• {f.name:<15} – Budget Constraint / Lower Priority")
        for f, reason in rejected_farms:
             print(f"• {f.name:<15} – {reason}")

        print("\n" + "-"*30)
        print("Total Portfolio Impact:")
        print(f"Energy Recovered: {total_energy:,.0f} kWh")
        print(f"CO2 Offset:       {total_co2:,.0f} kg")
        print(f"Net Profit:       INR {total_benefit:,.0f}")
        print(f"Water Efficiency: {opt_eff:.2f} kWh/L")
        print("="*40 + "\n")
        
        # --- VISUALIZATION (Move 4) ---
        if selected_farms and shared_data_df is not None:
            top_farm = selected_farms[0]
            print(f"Generating Efficiency Trend for Top Pick: {top_farm.name}...")
            
            try:
                from visualizer import generate_ascii_plot
                # Simulate 30 days to show trend
                # We need a dataframe. shared_data_df is passed in.
                # Run NO CLEAN
                df_base = calculate_energy_metrics(shared_data_df.copy(), cleaning_dates=[])
                # Run START CLEAN (Clean on day 1 to show immediate boost)
                clean_date = shared_data_df['datetime'].iloc[1] # Day 1
                df_clean = calculate_energy_metrics(shared_data_df.copy(), cleaning_dates=[clean_date])
                
                # Extract Efficiency (daily avg or hourly?)
                # Hourly is too noisy for ASCII. Resample to Daily Mean.
                eff_base = df_base.set_index('datetime')['effective_efficiency'].resample('D').max() * 100
                eff_clean = df_clean.set_index('datetime')['effective_efficiency'].resample('D').max() * 100
                
                # Plot the "Cleaned" curve
                # We could try to plot both, but ASCII plotter takes one series.
                # Let's plot the "With Cleaning" curve to show the restoration and subsequent decay.
                plot_str = generate_ascii_plot(eff_clean.values, title=f"Projected Efficiency % ({top_farm.name})")
                print(plot_str)
                print(f"   (Base Efficiency: {eff_base.mean():.1f}% | Improved: {eff_clean.mean():.1f}%)")
                
            except Exception as e:
                print(f"Visualization skipped: {e}")
                
        return selected_farms, water_used, total_benefit

    def _solve_knapsack_dp(self, items, capacity, value_attr='net_benefit'):
        """
        Solves 0/1 Knapsack using Dynamic Programming.
        
        Args:
            items: List of SolarFarm objects
            capacity: Max water budget (int/float)
            value_attr: Attribute to maximize (default: net_benefit)
            
        Returns:
            (selected_items, max_value)
        """
        n = len(items)
        if n == 0:
            return [], 0.0
            
        # Convert capacity and weights to integers for DP table indexing
        W = int(capacity)
        
        # weights and values
        wt = [int(round(f.water_usage)) for f in items]
        val = [getattr(f, value_attr) for f in items]
        
        # DP Table: dp[i][w] = max value using first i items with weight limit w
        # i from 0 to n, w from 0 to W
        dp = [[0.0 for _ in range(W + 1)] for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            for w in range(W + 1):
                if wt[i-1] <= w:
                    # Choice: Include item i-1 or exclude it
                    include = val[i-1] + dp[i-1][w - wt[i-1]]
                    exclude = dp[i-1][w]
                    dp[i][w] = max(include, exclude)
                else:
                    # Cannot include item i-1
                    dp[i][w] = dp[i-1][w]
                    
        max_value = dp[n][W]
        
        # Backtrack to find selected items
        selected = []
        w = W
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                # Item i-1 was included
                selected.append(items[i-1])
                w -= wt[i-1]
                
        return selected, max_value

if __name__ == "__main__":
    # Test Verification
    print("Running Multi-Farm Optimization Test...")
    
    # Mock Data
    dates = pd.date_range(start='2025-01-01', periods=720, freq='h')
    df_mock = pd.DataFrame({
        'datetime': dates,
        'irradiance': np.random.uniform(0, 1000, 720),
        'temperature': np.random.uniform(25, 35, 720),
        'precipitation': np.zeros(720) # No rain
    })
    # Zero out night
    df_mock.loc[df_mock['datetime'].dt.hour < 6, 'irradiance'] = 0
    df_mock.loc[df_mock['datetime'].dt.hour > 18, 'irradiance'] = 0
    
    # Define Heterogeneous Farms
    # A: High Benefit, High Water (Big Farm)
    # B: Med Benefit, Med Water
    # C: High Efficiency (Good benefit for low water)
    farms = [
        SolarFarm("Farm A", (13, 80), 5000, dust_rate_factor=1.2, cleaning_water_usage_liters=1000), # ~1MW
        SolarFarm("Farm B", (13, 80), 2000, dust_rate_factor=1.0, cleaning_water_usage_liters=400),
        SolarFarm("Farm C", (13, 80), 500,  dust_rate_factor=1.5, cleaning_water_usage_liters=100), # Small but dusty
        SolarFarm("Farm D", (13, 80), 3000, dust_rate_factor=0.8, cleaning_water_usage_liters=600),
    ]
    
    # Run Optimizer with Constrained Budget
    # Total needed: 1000+400+100+600 = 2100L
    # Budget: 800L
    # Expect: Farm C (100L) + Farm B (400L) = 500L? Or depending on benefit.
    # C is small area, so absolute benefit might be small despite high dust?
    # Actually, 100m2 vs 5000m2 matters A LOT for "Net Benefit".
    # Efficiency = Net Benefit / Water.
    # Benefit scales with Area. Water usage scales with Area.
    # So Efficiency ~ Benefit/m2 / Water/m2.
    # If Water/m2 is constant (usually is), then Efficiency depends on Benefit/m2.
    # Benefit/m2 depends on Dust Rate and Tariff.
    # So Farm C (Dust 1.5) should have higher efficiency than Farm A (Dust 1.2).
    
    optimizer = MultiSiteOptimizer(farms, water_budget_liters=800)
    selected, used, benefit = optimizer.optimize(df_mock)
    
    print("-" * 55)
    print(f"Selected: {[f.name for f in selected]}")
    print(f"Total Water Used: {used} L")
    print(f"Total Net Benefit: INR{benefit:.2f}")
    
