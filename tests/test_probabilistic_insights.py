import requests
import json

url = "http://localhost:8000/optimize-farms"

payload = {
    "farms": [
        {
            "name": "Test Farm Alpha",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "panel_area": 10000,
            "dust_rate": 2.5, # High dust to trigger anomaly
            "electricity_price": 6.0,
            "water_usage": 500
        },
        {
            "name": "Test Farm Beta",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "panel_area": 10000,
            "dust_rate": 0.1, # Low dust
            "electricity_price": 6.0,
            "water_usage": 500
        }
    ],
    "water_budget": 50000,
    "mode": "PROFIT"
}

try:
    print("Testing /optimize-farms with Probabilistic AI V3...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Success!")
        print(f"Selected Farms: {data['selected_farms']}")
        print(f"Total Benefit: ₹{data['total_benefit']:.2f}")
        
        print("\n🧠 AI Insights (Probabilistic V3):")
        if 'ai_insights' in data:
            for insight in data['ai_insights']:
                print(f" - {insight}")
        else:
            print("❌ No 'ai_insights' field found in response.")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Connection Failed: {e}")
