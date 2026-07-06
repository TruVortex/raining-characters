import requests


class WeatherAPI:
    def __init__(self):
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.weather_url = "https://api.open-meteo.com/v1/forecast"

    def get_coordinates(self, city_name: str) -> tuple[float, float, str, str, float] | None:
        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        try:
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = data.get("results")
            if not results:
                return None
            city_data = results[0]
            lat = city_data.get("latitude")
            lon = city_data.get("longitude")
            country = city_data.get("country", "Unknown")
            resolved_name = city_data.get("name", city_name)
            elevation = city_data.get("elevation", 0.0)
            return lat, lon, country, resolved_name, elevation
        except Exception:
            return None

    def get_weather(self, lat: float, lon: float) -> dict | None:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,is_day,precipitation,rain,showers,snowfall,weather_code,wind_speed_10m",
            "timezone": "auto"
        }
        try:
            response = requests.get(self.weather_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            current = data.get("current", {})
            return {
                "temp": current.get("temperature_2m"),
                "apparent_temp": current.get("apparent_temperature"),
                "humidity": current.get("relative_humidity_2m"),
                "is_day": current.get("is_day"),
                "precipitation": current.get("precipitation"),
                "rain": current.get("rain"),
                "snowfall": current.get("snowfall"),
                "wind_speed": current.get("wind_speed_10m"),
                "weather_code": current.get("weather_code"),
                "utc_offset": data.get("utc_offset_seconds", 0)
            }
        except Exception:
            return None

    def translate_wmo_code(self, code: int) -> str:
        wmo_codes = {
            0: "Clear Sky",
            1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing Rime Fog",
            51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
            61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
            71: "Slight Snowfall", 73: "Moderate Snowfall", 75: "Heavy Snowfall",
            77: "Snow Grains",
            80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
            85: "Slight Snow Showers", 86: "Heavy Snow Showers",
            95: "Thunderstorm", 96: "Thunderstorm with Slight Hail", 99: "Thunderstorm with Heavy Hail"
        }
        return wmo_codes.get(code, "Unknown Weather")