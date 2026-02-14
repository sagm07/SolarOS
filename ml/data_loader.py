import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_nasa_power_data(latitude=13.0827, longitude=80.2707, days=30):
    """
    Fetches hourly solar irradiance and temperature data from NASA POWER API.
    
    Args:
        latitude (float): Latitude of the location (default: Chennai).
        longitude (float): Longitude of the location (default: Chennai).
        days (int): Number of days of data to fetch.

    Returns:
        pd.DataFrame: DataFrame with datetime, irradiance, and temperature columns.
    """
    # Calculate date range
    # NASA POWER data usually has a lag. 
    # Use 180 days lag to ensure data availability for GHI (CERES).
    end_date = datetime.now() - timedelta(days=180) 
    # Keep it 30 days as requested, or increase?
    # Intelligence Core requests 30 days. Let's stick to 30 days in default, but module can override.
    start_date = end_date - timedelta(days=days)
    
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    
    # NASA POWER API endpoint
    base_url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
    
    # Parameters - ADD PRECIPITATION
    parameters = "ALLSKY_SFC_SW_DWN,T2M,PRECTOTCORR"  # GHI, Temperature, Precipitation
    
    # Build URL
    url = (
        f"{base_url}?"
        f"parameters={parameters}&"
        f"community=RE&"
        f"longitude={longitude}&"
        f"latitude={latitude}&"
        f"start={start_str}&"
        f"end={end_str}&"
        f"format=JSON"
    )
    
    print(f"Fetching data for {days} days from {start_str} to {end_str}...")
    
    try:
        # Added timeout for production stability
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract hourly data
        if 'properties' not in data or 'parameter' not in data['properties']:
             raise ValueError("Unexpected API response structure")
             
        ghi_data = data['properties']['parameter'].get('ALLSKY_SFC_SW_DWN', {})
        temp_data = data['properties']['parameter'].get('T2M', {})
        precip_data = data['properties']['parameter'].get('PRECTOTCORR', {})
        
        # Create DataFrame
        df_ghi = pd.DataFrame.from_dict(ghi_data, orient='index', columns=['irradiance'])
        df_temp = pd.DataFrame.from_dict(temp_data, orient='index', columns=['temperature'])
        df_precip = pd.DataFrame.from_dict(precip_data, orient='index', columns=['precipitation'])
        
        # Merge dataframes
        df = df_ghi.join(df_temp).join(df_precip)
        
        # Reset index to make datetime a column
        df.index.name = 'datetime_str'
        df.reset_index(inplace=True)
        
        # Convert index string to datetime objects
        # Format is YYYYMMDDHH
        df['datetime'] = pd.to_datetime(df['datetime_str'], format='%Y%m%d%H')
        
        # Clean up - Include precipitation now
        df = df[['datetime', 'irradiance', 'temperature', 'precipitation']]
        
        # Handle missing values (-999 is NASA's nodata value)
        df.replace(-999, float('nan'), inplace=True)
        # Fill NaN precipitation with 0 (no rain)
        df['precipitation'] = df['precipitation'].fillna(0.0)
        df.dropna(inplace=True)
        
        print(f"Successfully fetched {len(df)} records.")
        return df

    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        if 'response' in locals():
            print(f"Response Content: {response.text[:500]}") # Print first 500 chars
        return pd.DataFrame()
    except ValueError as e:
        print(f"Data processing error: {e}")
        if 'response' in locals():
            print(f"Response Content: {response.text[:500]}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Test the function
    df = fetch_nasa_power_data()
    if not df.empty:
        print("\nHead of the DataFrame:")
        print(df.head())
        print("\nTail of the DataFrame:")
        print(df.tail())
        print(f"\nData types:\n{df.dtypes}")
        
        print("\n--- Data Statistics ---")
        print(df.describe())
        
        print("\n--- Daily Max Irradiance (Sample) ---")
        # Check if index is datetime or column 'datetime' exists
        if 'datetime' in df.columns:
            daily_max = df.set_index('datetime').resample('D')['irradiance'].max()
            print(daily_max.head())
        
        # Save to CSV for inspection (optional)
        # df.to_csv("chennai_solar_data.csv", index=False)
    else:
        print("Failed to fetch data.")
