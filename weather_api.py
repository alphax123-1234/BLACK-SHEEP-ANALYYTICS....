"""
🐑 BLACK SHEEP - Weather Integration Module
"""

import requests
import logging
from typing import Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Real-time weather service for Ugandan locations
    """
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.cache = {}
        self.cache_expiry = 600  # 10 minutes
    
    def get_weather(self, lat: float, lon: float) -> Dict:
        """Get real-time weather for coordinates"""
        cache_key = f"{lat:.4f}_{lon:.4f}"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_expiry:
                return cached_data
        
        try:
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': True,
                'hourly': 'temperature_2m,relativehumidity_2m,precipitation,weathercode',
                'timezone': 'Africa/Kampala'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data.get('current_weather', {})
            
            weather_data = {
                'temperature': current.get('temperature', 0),
                'wind_speed': current.get('windspeed', 0),
                'weather_code': current.get('weathercode', 0),
                'weather_condition': self._get_weather_description(current.get('weathercode', 0)),
                'humidity': data.get('hourly', {}).get('relativehumidity_2m', [0])[0],
                'precipitation': data.get('hourly', {}).get('precipitation', [0])[0],
                'timestamp': datetime.now().isoformat()
            }
            
            self.cache[cache_key] = (weather_data, datetime.now())
            return weather_data
            
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return self._get_fallback_weather()
    
    def _get_weather_description(self, code: int) -> str:
        """Translate weather code to description"""
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy",
            3: "Overcast", 45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown")
    
    def _get_fallback_weather(self) -> Dict:
        """Return fallback weather data for Kampala"""
        return {
            'temperature': 25.0,
            'wind_speed': 5.0,
            'weather_code': 0,
            'weather_condition': "Partly cloudy",
            'humidity': 65,
            'precipitation': 0.0,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_weather_for_location(self, location: str, lat: float, lon: float) -> Tuple[str, float]:
        """Get weather for a specific location"""
        weather_data = self.get_weather(lat, lon)
        return (
            weather_data.get('weather_condition', 'Unknown'),
            weather_data.get('temperature', 25.0)
        )
