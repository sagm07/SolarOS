
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional

class OptimizationEngine:
    def __init__(self, 
                 electricity_price: float = 6.0, 
                 cleaning_cost: float = 1500.0,
                 carbon_price_per_kg: float = 5.0, 
                 water_price_per_liter: float = 0.05,
                 water_usage_per_clean: float = 500.0):
        self.electricity_price = electricity_price
        self.cleaning_cost = cleaning_cost
        self.carbon_price = carbon_price_per_kg
        self.water_price = water_price_per_liter
        self.water_usage = water_usage_per_clean
        
    def _calculate_day_reward(self, energy_produced: float, is_cleaning_day: bool, carbon_saved: float = 0.0) -> float:
        revenue = energy_produced * self.electricity_price
        carbon_value = carbon_saved * self.carbon_price
        
        cost = 0.0
        if is_cleaning_day:
            cost = self.cleaning_cost
            
        return revenue + carbon_value - cost

    def optimize_cleaning_schedule(self, 
                                   forecast_df: pd.DataFrame, 
                                   min_days_between_clean: int = 7) -> Dict:
        """
        Uses Dynamic Programming with INTELLIGENT FRICTION.
        """
        days = len(forecast_df)
        max_days_dirty = 60 
        
        
        # Check for precipitation data
        has_rain_data = 'precipitation' in forecast_df.columns
        rain_vec = forecast_df['precipitation'].values if has_rain_data else np.zeros(days)

        # UNCERTAINTY FACTOR (New in v3)
        # If model is uncertain (wide P90-P10), be more conservative with spending money on cleaning.
        # We assume 'uncert_p90_kwh' and 'uncert_p10_kwh' might exist if passed from Hybrid v2.
        has_uncertainty = 'uncert_p90_kwh' in forecast_df.columns
        uncertainty_penalty = 0.0
        
        if has_uncertainty:
            # Simple measure: Sum of daily spread
            daily_spread = forecast_df['uncert_p90_kwh'] - forecast_df['uncert_p10_kwh']
            avg_spread = daily_spread.mean()
            # If spread is > 10% of energy, it's 'High Uncertainty'
            # We can dampen the projected rewards.
            # For DP, we'll apply a scalar to the Energy Reward.
            # Higher uncertainty -> Lower confidence in revenue -> Discount it.
            # Discount factor = 1.0 - (Spread / MaxEnergy * weight)
            # Simplified:
            uncertainty_penalty = 0.05 # Flat 5% discount on gains if using ML

        dp = np.full((days + 1, max_days_dirty + 1), -np.inf)
        parent = {} 
        
        start_dirtiness = 0 
        dp[0][start_dirtiness] = 0.0
        
        # Use Hybrid Energy if available, else Physics Actual
        energy_col = 'hybrid_energy_kwh' if 'hybrid_energy_kwh' in forecast_df.columns else 'actual_energy_kwh'
        
        # For 'Potential' (Clean state), we need to estimate what it WOULD be.
        # Recoverable = Ideal - Actual.
        # So Potential = Actual + Recoverable. (Matches logic).
        # But Hybrid model gives us 'Predicted Actual'.
        # We need 'Predicted Ideal' or 'Predicted Clean'. 
        # Hybrid Correction applies to the *specific condition*.
        # If we clean, dust=0. The Hybrid Model should predict for dust=0.
        # Ideally, we'd run the model for both scenarios. 
        # For Optimization Speed, we assume:
        # Potential_Hybrid = Hybrid_Actual + Physics_Recoverable
        # This assumes ML residual is independent of Dust (mostly true, it's temp/spectral).
        
        current_actual_vec = forecast_df[energy_col].values
        physics_recoverable_vec = forecast_df['recoverable_energy_kwh'].values
        
        # Clean Energy Series = Current + Physics Recoverable (Approximation)
        clean_energy_series = current_actual_vec + physics_recoverable_vec
        
        avg_daily_loss = 0.005 # 0.5% / day
        rain_cleaning_gamma = 0.4 
        
        for day in range(days):
            potential_energy = clean_energy_series[day]
            rain_mm = rain_vec[day]

            # Future Rain Check (Lookahead 2 days)
            # If significant rain is coming in 1-2 days, Cleaning creates negligible value.
            rain_upcoming_penalty = 0.0
            if day < days - 2:
                future_rain = np.sum(rain_vec[day+1:day+3])
                if future_rain > 5.0: # More than 5mm in next 2 days
                    rain_upcoming_penalty = 0.5 # 50% penalty on cleaning benefit
            
            for dirty_days in range(max_days_dirty):
                if dp[day][dirty_days] == -np.inf:
                    continue
                
                current_reward = dp[day][dirty_days]
                
                # --- ACTION 1: WAIT ---
                # Natural cleaning by rain?
                if rain_mm > 0.1:
                    reduction = min(rain_cleaning_gamma * rain_mm, 0.95)
                    # Approx effective dirty days reduction
                    # This is tricky in discrete DP. We'll simulate it by jumping to a lower state.
                    # e.g. dirty_days * (1-reduction)
                    effective_dirty_days = int(dirty_days * (1.0 - reduction))
                    next_dirty_days = min(effective_dirty_days + 1, max_days_dirty)
                else:
                    next_dirty_days = min(dirty_days + 1, max_days_dirty)
                
                efficiency_loss = dirty_days * avg_daily_loss
                realized_efficiency = max(0.9, 1.0 - efficiency_loss)
                daily_energy = potential_energy * realized_efficiency
                
                reward_wait = self._calculate_day_reward(daily_energy, is_cleaning_day=False)
                
                if dp[day+1][next_dirty_days] < current_reward + reward_wait:
                    dp[day+1][next_dirty_days] = current_reward + reward_wait
                    parent[(day+1, next_dirty_days)] = (dirty_days, 0) 
                
                # --- ACTION 2: CLEAN ---
                # Constraints:
                # 1. Must be at least min_days since last clean
                # 2. Must be dirty enough (> 3-5% loss) to justify cost at all
                #    5% loss = ~10 days at 0.5%/day
                min_dirtiness_threshold = 10 
                
                can_clean = (dirty_days >= min_days_between_clean) and (dirty_days >= min_dirtiness_threshold)
                
                if can_clean:
                    # Apply Rain Penalty if applicable
                    # If rain is coming, the 'Value' of cleaning is reduced because nature would have done it for free.
                    
                    daily_energy_clean = potential_energy * 1.0 
                    
                    # Carbon/Energy Gain
                    energy_would_have_been = potential_energy * (1.0 - (dirty_days * avg_daily_loss))
                    energy_gain = daily_energy_clean - energy_would_have_been
                    
                    # Apply Rain Penalty Factor to the Gain
                    if rain_upcoming_penalty > 0:
                        energy_gain *= (1.0 - rain_upcoming_penalty) # Devalue the gain
                        
                    carbon_saved = energy_gain * 0.7
                    
                    reward_clean = self._calculate_day_reward(daily_energy_clean, is_cleaning_day=True, carbon_saved=carbon_saved)
                    
                    if dp[day+1][0] < current_reward + reward_clean:
                        dp[day+1][0] = current_reward + reward_clean
                        parent[(day+1, 0)] = (dirty_days, 1)

        # Backtrack
        best_end_dirty_days = np.argmax(dp[days])
        max_total_reward = dp[days][best_end_dirty_days]
        
        schedule = []
        curr_dirty = best_end_dirty_days
        
        for day in range(days, 0, -1):
            if (day, curr_dirty) in parent:
                prev_dirty, action = parent[(day, curr_dirty)]
                if action == 1:
                    schedule.append(day - 1)
                curr_dirty = prev_dirty
            
        schedule.reverse()
        
        return {
            "cleaning_dates": schedule,
            "total_net_value": max_total_reward,
            "horizon_days": days
        }
    def calculate_confidence_intervals(self, schedule: List[int], forecast_df: pd.DataFrame) -> Dict:
        """
        Calculates P10, P50, and P90 net values for a given schedule.
        """
        days = len(forecast_df)
        cleaning_dates = set(schedule)
        
        # Columns
        col_p50 = 'hybrid_energy_kwh' if 'hybrid_energy_kwh' in forecast_df.columns else 'actual_energy_kwh'
        col_p10 = 'uncert_p10_kwh' if 'uncert_p10_kwh' in forecast_df.columns else col_p50
        col_p90 = 'uncert_p90_kwh' if 'uncert_p90_kwh' in forecast_df.columns else col_p50
        
        physics_recoverable = forecast_df['recoverable_energy_kwh'].values
        
        scenarios = {
            'p10': forecast_df[col_p10].values,
            'p50': forecast_df[col_p50].values,
            'p90': forecast_df[col_p90].values
        }
        
        results = {}
        
        avg_daily_loss = 0.005
        
        for name, energy_vec in scenarios.items():
            # Construct "Clean Energy" potential for this scenario
            # Potential = Predicted Actual + Physics Recoverable
            # (Assuming recovered amount is roughly constant physically)
            potential_energy_vec = energy_vec + physics_recoverable
            
            total_value = 0.0
            dirty_days = 0 
            
            for day in range(days):
                # 1. Update Dirty State
                if day in cleaning_dates:
                    dirty_days = 0
                else:
                    # Rain Check
                    rain_mm = forecast_df.iloc[day].get('precipitation', 0.0)
                    if rain_mm > 0.1:
                        reduction = min(0.4 * rain_mm, 0.95)
                        dirty_days = int(dirty_days * (1.0 - reduction))
                    else:
                        dirty_days += 1
                
                # 2. Calculate Efficiency
                efficiency_loss = dirty_days * avg_daily_loss
                realized_efficiency = max(0.9, 1.0 - efficiency_loss)
                
                # 3. Calculate Energy
                daily_energy = potential_energy_vec[day] * realized_efficiency
                
                # 4. Calculate Reward
                is_clean_day = (day in cleaning_dates)
                reward = self._calculate_day_reward(daily_energy, is_cleaning_day=is_clean_day)
                total_value += reward
            
            results[name] = total_value
            
        return results
