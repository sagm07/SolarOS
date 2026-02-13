
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

        dp = np.full((days + 1, max_days_dirty + 1), -np.inf)
        parent = {} 
        
        start_dirtiness = 0 
        dp[0][start_dirtiness] = 0.0
        
        clean_energy_series = (forecast_df['actual_energy_kwh'] + forecast_df['recoverable_energy_kwh']).values
        avg_daily_loss = 0.005 # 0.5% / day
        rain_cleaning_gamma = 0.4 # Same as degradation model
        
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
