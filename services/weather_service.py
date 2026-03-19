"""
TaskMate AI - Weather Service
Integration with Open-Meteo API for real-time weather data.
"""

import httpx
from typing import Optional, Dict


class WeatherService:
    """Open-Meteo API integration for weather queries."""

    def __init__(self):
        # Open-Meteo doesn't require an API key by default
        self.enabled = True

    def _get_weather_text(self, code: int) -> tuple[str, str, str]:
        if code == 0:
            return "Clear Sky", "Clear", "01d"
        elif code <= 3:
            return "Cloudy", "Clouds", "02d"
        elif code >= 61:
            return "Rain", "Rain", "10d"
        return "Unknown", "Unknown", "50d"

    async def get_weather(self, city: str) -> Optional[Dict]:
        """Fetch current weather data for a city."""
        if not self.enabled:
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Step 1: Geocoding
                geo_response = await client.get(
                    "https://geocoding-api.open-meteo.com/v1/search",
                    params={"name": city, "count": 1}
                )
                
                if geo_response.status_code != 200:
                    print(f"⚠️ [Geo API Error] {geo_response.status_code}: {geo_response.text}")
                    return None
                    
                geo_data = geo_response.json()
                if "results" not in geo_data or not geo_data["results"]:
                    return None
                    
                location = geo_data["results"][0]
                lat = location["latitude"]
                lon = location["longitude"]
                name = location["name"]
                country = location.get("country", "")

                # Step 2: Weather
                weather_response = await client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current": "temperature_2m,wind_speed_10m,weather_code,relative_humidity_2m,apparent_temperature",
                        "timezone": "auto"
                    }
                )
                
                if weather_response.status_code != 200:
                    print(f"⚠️ [Weather API Error] {weather_response.status_code}: {weather_response.text}")
                    return None
                    
                w_data = weather_response.json().get("current", {})
                if not w_data:
                    return None
                
                description, condition, icon = self._get_weather_text(w_data.get("weather_code", 99))

                return {
                    "city": name,
                    "country": country,
                    "temp": round(w_data.get("temperature_2m", 0.0), 1),
                    "feels_like": round(w_data.get("apparent_temperature", 0.0), 1),
                    "humidity": w_data.get("relative_humidity_2m", 0),
                    "wind_speed": w_data.get("wind_speed_10m", 0.0),
                    "description": description,
                    "condition": condition,
                    "icon": icon,
                }

        except httpx.TimeoutException:
            return None
        except Exception as e:
            print(f"⚠️ [Weather Service Exception] {e}")
            return None

    async def get_forecast(self, city: str, days: int = 3) -> Optional[list]:
        """Fetch weather forecast (simplified)."""
        if not self.enabled:
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Step 1: Geocoding
                geo_response = await client.get(
                    "https://geocoding-api.open-meteo.com/v1/search",
                    params={"name": city, "count": 1}
                )
                if geo_response.status_code != 200: 
                    return None
                geo_data = geo_response.json()
                if "results" not in geo_data or not geo_data["results"]: 
                    return None
                
                lat = geo_data["results"][0]["latitude"]
                lon = geo_data["results"][0]["longitude"]

                # Step 2: Forecast
                response = await client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                        "timezone": "auto",
                        "forecast_days": days
                    }
                )

                if response.status_code != 200:
                    return None

                data = response.json().get("daily", {})
                if not data:
                    return None

                forecasts = []
                for i in range(len(data.get("time", []))):
                    code = data["weather_code"][i]
                    description, condition, _ = self._get_weather_text(code)

                    # Calculate average temp between max and min for simplification
                    temp = (data["temperature_2m_max"][i] + data["temperature_2m_min"][i]) / 2

                    forecasts.append({
                        "date": data["time"][i],
                        "temp": round(temp, 1),
                        "description": description,
                        "condition": condition,
                    })

                return forecasts

        except Exception:
            return None
