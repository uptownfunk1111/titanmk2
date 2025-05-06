"""
Match and Weather Impact on Performance
- Fetches comprehensive weather data from BOM Space Weather API and analyzes impact on match outcomes
"""
import pandas as pd
import numpy as np
import os
import requests
from datetime import datetime

BOM_API_KEY = "83d4b9f1-deb3-4862-9f42-22919de9bc00"
BOM_BASE_URL = "https://sws-data.sws.bom.gov.au"
BOM_WEATHER_ENDPOINT = "/api/v1/"  # Updated endpoint

# Helper to fetch weather for a venue and date
def fetch_bom_weather(venue, match_date):
    params = {
        'location': venue,  # Venue name as location
        'date': match_date.strftime('%Y-%m-%d'),
    }
    headers = {"Authorization": f"Bearer {BOM_API_KEY}"}
    try:
        url = BOM_BASE_URL + BOM_WEATHER_ENDPOINT
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Extract all relevant fields (update as per actual API response)
            return {
                'Rain': data.get('rain', np.nan),
                'WindSpeed': data.get('wind_speed', np.nan),
                'WindDirection': data.get('wind_direction', np.nan),
                'Temperature': data.get('temperature', np.nan),
                'Humidity': data.get('humidity', np.nan),
                'WeatherCondition': data.get('weather_condition', data.get('description', '')),
                'Pressure': data.get('pressure', np.nan),
                'CloudCover': data.get('cloud_cover', np.nan),
                'DewPoint': data.get('dew_point', np.nan),
                'UVIndex': data.get('uv_index', np.nan)
            }
        else:
            print(f"[WARN] BOM API error {response.status_code}: {response.text}")
            return {k: np.nan for k in ['Rain','WindSpeed','WindDirection','Temperature','Humidity','WeatherCondition','Pressure','CloudCover','DewPoint','UVIndex']}
    except Exception as e:
        print(f"[ERROR] Exception fetching BOM weather: {e}")
        return {k: np.nan for k in ['Rain','WindSpeed','WindDirection','Temperature','Humidity','WeatherCondition','Pressure','CloudCover','DewPoint','UVIndex']}

def fetch_weather_data(match_file, output_file):
    matches = pd.read_csv(match_file)
    weather_fields = ['Rain','WindSpeed','WindDirection','Temperature','Humidity','WeatherCondition','Pressure','CloudCover','DewPoint','UVIndex']
    for field in weather_fields:
        matches[field] = np.nan
    for idx, row in matches.iterrows():
        venue = row['Venue'] if 'Venue' in row else None
        date_str = row['Date'] if 'Date' in row else None
        try:
            match_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()
        except Exception:
            match_date = datetime.now()
        weather = fetch_bom_weather(venue, match_date)
        for field in weather_fields:
            matches.at[idx, field] = weather[field]
    matches.to_csv(output_file, index=False)
    print(f"[SUCCESS] Weather impact analysis saved to {output_file}")

if __name__ == "__main__":
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
    match_file = os.path.join(outputs_dir, 'all_matches_2019_2025.csv')
    output_file = os.path.join(outputs_dir, 'weather_impact_analysis.csv')
    fetch_weather_data(match_file, output_file)
