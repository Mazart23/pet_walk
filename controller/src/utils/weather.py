import os
import requests
from datetime import datetime, timedelta


API_KEY = os.environ.get("WEATHER_KEY")
BASE_URL = os.environ.get("WEATHER_URL")

def get_weather_info(lat, lon):
    location = f"{lat},{lon}"

    now = datetime.now()
    past_6h = now - timedelta(hours=6)
    history_url = f"{BASE_URL}/history.json?key={API_KEY}&q={location}&dt={past_6h.strftime('%Y-%m-%d')}"
    history_response = requests.get(history_url)

    rain_past_6h = False
    if history_response.status_code == 200:
        history_data = history_response.json()
        for hour in history_data.get("forecast", {}).get("forecastday", [])[0].get("hour", []):
            hour_time = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M")
            if past_6h <= hour_time <= now and hour.get("precip_mm", 0) >= 0.5:
                rain_past_6h = True
                break

    forecast_url = f"{BASE_URL}/forecast.json?key={API_KEY}&q={location}&hours=2"
    forecast_response = requests.get(forecast_url)

    rain_next_2h = False
    if forecast_response.status_code == 200:
        forecast_data = forecast_response.json()
        for hour in forecast_data.get("forecast", {}).get("forecastday", [])[0].get("hour", []):
            hour_time = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M")
            if now <= hour_time <= now + timedelta(hours=2):
                if hour.get("precip_mm", 0) >= 0.5:
                    rain_next_2h = True
                    break

    return {
        "rain_past_6h": rain_past_6h,
        "rain_next_2h": rain_next_2h
    }