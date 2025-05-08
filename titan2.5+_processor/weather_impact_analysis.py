"""
Match and Weather Impact on Performance
- Fetches comprehensive weather data from Open-Meteo BoM API and analyzes impact on match outcomes
"""
import pandas as pd
import requests
from datetime import datetime, timedelta
import os

# Stadium coordinates mapping (add more as needed)
STADIUM_COORDS = {
    "Accor Stadium": (-33.8474, 151.0631),
    "Suncorp Stadium": (-27.4648, 153.0094),
    "AAMI Park": (-37.8251, 144.9834),
    "Allianz Stadium": (-33.8898, 151.2252),
    "McDonald Jones Stadium": (-32.8940, 151.7200),
    "4 Pines Park": (-33.7937, 151.2820),
    "Cbus Super Stadium": (-28.0707, 153.4309),
    "Queensland Country Bank Stadium": (-19.2590, 146.8057),
    "GIO Stadium": (-35.2250, 149.0840),
    "BlueBet Stadium": (-33.7506, 150.6909),
    "PointsBet Stadium": (-34.0433, 151.1495),
    "WIN Stadium": (-34.4278, 150.8931),
    "Leichhardt Oval": (-33.8732, 151.1447),
    "Campbelltown Stadium": (-34.0625, 150.8322),
    "Kayo Stadium": (-27.2072, 153.1017),
    "CommBank Stadium": (-33.8197, 150.9903),
    "Netstrata Jubilee Stadium": (-33.9755, 151.1074),
    "Go Media Stadium (NZ)": (-36.8925, 174.7740),
    "Sunshine Coast Stadium": (-26.7183, 153.1177),
    "Belmore Sports Ground": (-33.9180, 151.0964),
    "Central Coast Stadium": (-33.4333, 151.3422),
    "TIO Stadium (Darwin)": (-12.4163, 130.8510),
    "Cazalys Stadium (Cairns)": (-16.9318, 145.7445),
    "Optus Stadium (Perth)": (-31.9505, 115.8605),
    "Eden Park (Auckland)": (-36.8754, 174.7445),
    "Forsyth Barr Stadium (Dunedin)": (-45.8788, 170.5028),
    "Carrington Park (Bathurst)": (-33.4144, 149.5776),
    "Glen Willow Oval (Mudgee)": (-32.5894, 149.5789),
    "McDonald's Park (Wagga Wagga)": (-35.1319, 147.3513),
    "Salter Oval (Bundaberg)": (-24.8658, 152.3486),
    "Barlow Park (Cairns)": (-16.9256, 145.7700),
    "Browne Park (Rockhampton)": (-23.3750, 150.5050),
    "Apex Oval (Dubbo)": (-32.2569, 148.6011),
    "Bega Recreation Ground (Bega)": (-36.6769, 149.8417),
    "Lavington Sports Ground (Albury)": (-36.0428, 146.9333),
    "Scully Park (Tamworth)": (-31.0833, 150.9167),
    "Marley Brown Oval (Gladstone)": (-23.8450, 151.2561),
    "C.ex Coffs International Stadium": (-30.2967, 153.1144),
    "Port Macquarie Regional Stadium": (-31.4300, 152.9089),
    "North Ipswich Reserve (Ipswich)": (-27.6075, 152.7581),
    "Anzac Oval (Alice Springs)": (-23.6980, 133.8807),
    "BMD Kougari Oval (Brisbane)": (-27.4705, 153.0234),
    "Albert Park (Gympie)": (-26.1900, 152.6650),
    "Bellevue Oval (Armidale)": (-30.5092, 151.6690),
    "Wade Park (Orange)": (-33.2833, 149.1000),
    "Lark Hill Sportsplex (Perth)": (-32.3283, 115.7633),
    "Pratten Park (Sydney)": (-33.8894, 151.1389),
    "North Sydney Oval (Sydney)": (-33.8320, 151.2090),
    "Santos National Stadium (Port Moresby, PNG)": (-9.4438, 147.1803),
    "HBF Park (Perth)": (-31.9439, 115.8605)
}

def get_nrl_game_weather(latitude, longitude, kickoff_time_iso, timezone="Australia/Sydney"):
    """
    Fetches weather forecast for a specific location and time using Open-Meteo's BoM API.
    :param latitude: float, latitude of stadium
    :param longitude: float, longitude of stadium
    :param kickoff_time_iso: str, kickoff time in ISO 8601 format (e.g., "2025-05-07T19:30:00")
    :param timezone: str, timezone for the forecast (default is Sydney time)
    :return: dict with weather conditions at kickoff
    """
    url = "https://api.open-meteo.com/v1/bom"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation,wind_speed_10m,wind_direction_10m,humidity_2m",
        "timezone": timezone
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    kickoff_hour = datetime.fromisoformat(kickoff_time_iso).strftime("%Y-%m-%dT%H:00")
    try:
        index = data["hourly"]["time"].index(kickoff_hour)
        return {
            "temperature_C": data["hourly"]["temperature_2m"][index],
            "precipitation_mm": data["hourly"]["precipitation"][index],
            "wind_speed_kmh": data["hourly"]["wind_speed_10m"][index],
            "wind_direction_deg": data["hourly"]["wind_direction_10m"][index],
            "humidity_percent": data["hourly"]["humidity_2m"][index]
        }
    except ValueError:
        return {
            "temperature_C": None,
            "precipitation_mm": None,
            "wind_speed_kmh": None,
            "wind_direction_deg": None,
            "humidity_percent": None
        }

def main():
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs'))
    match_file = os.path.join(outputs_dir, 'all_matches_2019_2025.csv')
    output_file = os.path.join(outputs_dir, 'weather_impact_analysis.csv')
    df = pd.read_csv(match_file)
    # Prepare columns for weather data
    df['temperature_C'] = None
    df['precipitation_mm'] = None
    df['wind_speed_kmh'] = None
    df['wind_direction_deg'] = None
    df['humidity_percent'] = None
    for idx, row in df.iterrows():
        venue = row.get('Venue', None)
        kickoff_time = row.get('Date', None)
        if pd.isna(venue) or pd.isna(kickoff_time):
            continue
        coords = STADIUM_COORDS.get(venue)
        if not coords:
            continue
        # Only fetch weather for matches within the next 7 days
        try:
            kickoff_dt = datetime.fromisoformat(kickoff_time.replace('Z', ''))
            now = datetime.now()
            if kickoff_dt.date() < now.date() or kickoff_dt > now + timedelta(days=7):
                continue  # Skip past matches and those more than 7 days ahead
        except Exception as e:
            print(f"[WARN] Could not parse kickoff time '{kickoff_time}': {e}")
            continue
        try:
            weather = get_nrl_game_weather(coords[0], coords[1], kickoff_time)
            df.at[idx, 'temperature_C'] = weather['temperature_C']
            df.at[idx, 'precipitation_mm'] = weather['precipitation_mm']
            df.at[idx, 'wind_speed_kmh'] = weather['wind_speed_kmh']
            df.at[idx, 'wind_direction_deg'] = weather['wind_direction_deg']
            df.at[idx, 'humidity_percent'] = weather['humidity_percent']
        except Exception as e:
            print(f"[WARN] Weather fetch failed for {venue} at {kickoff_time}: {e}")
    df.to_csv(output_file, index=False)
    print(f"[SUCCESS] Weather impact analysis saved to {output_file}")

if __name__ == "__main__":
    main()
