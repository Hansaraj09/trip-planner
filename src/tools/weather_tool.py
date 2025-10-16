import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
from src.config.settings import settings

class WeatherTool:
    """Tool for fetching weather data from OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.base_url = settings.openweather_base_url
        self.forecast_url = settings.openweather_forecast_url
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "status": "success"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to fetch weather data: {str(e)}"
            }
    
    def get_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for upcoming days"""
        try:
            url = f"{self.forecast_url}"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 data points per day (every 3 hours)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process forecast data
            daily_forecasts = []
            current_date = None
            day_data = []
            
            for item in data["list"]:
                forecast_date = datetime.fromtimestamp(item["dt"]).date()
                
                if current_date != forecast_date:
                    if day_data:
                        daily_forecasts.append(self._aggregate_day_data(day_data, current_date))
                    current_date = forecast_date
                    day_data = [item]
                else:
                    day_data.append(item)
            
            # Add last day
            if day_data:
                daily_forecasts.append(self._aggregate_day_data(day_data, current_date))
            
            return {
                "city": data["city"]["name"],
                "forecasts": daily_forecasts[:days],
                "status": "success"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to fetch forecast data: {str(e)}"
            }
    
    def _aggregate_day_data(self, day_data: List[Dict], date) -> Dict[str, Any]:
        """Aggregate weather data for a single day"""
        temps = [item["main"]["temp"] for item in day_data if "main" in item and "temp" in item["main"]]
        descriptions = [item["weather"][0]["description"] for item in day_data if "weather" in item and len(item["weather"]) > 0]
        
        if not temps:
            temps = [20.0]  # Default temp
        if not descriptions:
            descriptions = ["clear"]
        
        description = max(set(descriptions), key=descriptions.count)
        
        return {
            "date": date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date),
            "avg_temp": round(sum(temps) / len(temps), 1),
            "min_temp": round(min(temps), 1),
            "max_temp": round(max(temps), 1),
            "description": description,
            "humidity": day_data[0].get("main", {}).get("humidity", 50) if day_data else 50
        }
    def analyze_weather_conditions(self, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze weather conditions and provide recommendations"""
        if forecast_data.get("status") != "success":
            return forecast_data
        
        forecasts = forecast_data["forecasts"]
        
        # Analyze conditions
        favorable_days = []
        unfavorable_days = []
        warnings = []
        
        for forecast in forecasts:
            score = self._calculate_weather_score(forecast)
            
            day_info = {
                "date": forecast["date"],
                "score": score,
                "temp": forecast["avg_temp"],
                "description": forecast["description"]
            }
            
            if score >= 7:
                favorable_days.append(day_info)
            elif score <= 4:
                unfavorable_days.append(day_info)
                warnings.append(f"{forecast['date']}: {forecast['description']}")
        
        # Fix: Calculate overall score correctly
        scores = [self._calculate_weather_score(f) for f in forecasts]
        overall_score = sum(scores) / len(scores) if scores else 5
        
        return {
            "city": forecast_data["city"],
            "overall_score": round(overall_score, 1),
            "is_favorable": overall_score >= 6,
            "favorable_days": favorable_days,
            "unfavorable_days": unfavorable_days,
            "warnings": warnings,
            "recommendation": self._get_recommendation(overall_score),
            "forecasts": forecasts,
            "status": "success"
        }

    def analyze_weather_conditions(self, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze weather conditions and provide recommendations"""
        if forecast_data.get("status") != "success":
            return forecast_data
        
        forecasts = forecast_data["forecasts"]
        
        # Analyze conditions
        favorable_days = []
        unfavorable_days = []
        warnings = []
        
        for forecast in forecasts:
            score = self._calculate_weather_score(forecast)
            
            day_info = {
                "date": forecast["date"],
                "score": score,
                "temp": forecast["avg_temp"],
                "description": forecast["description"]
            }
            
            if score >= 7:
                favorable_days.append(day_info)
            elif score <= 4:
                unfavorable_days.append(day_info)
                warnings.append(f"{forecast['date']}: {forecast['description']}")
        
        scores = [self._calculate_weather_score(f) for f in forecasts]
        overall_score = sum(scores) / len(scores) if scores else 5
        
        return {
            "city": forecast_data["city"],
            "overall_score": round(overall_score, 1),
            "is_favorable": overall_score >= 6,
            "favorable_days": favorable_days,
            "unfavorable_days": unfavorable_days,
            "warnings": warnings,
            "recommendation": self._get_recommendation(overall_score),
            "forecasts": forecasts,
            "status": "success"
        }
    
    def _calculate_weather_score(self, forecast: Dict[str, Any]) -> int:
        """Calculate a weather score from 1-10"""
        score = 5  # Base score
        
        temp = forecast["avg_temp"]
        description = forecast["description"].lower()
        
        # Temperature scoring (ideal: 15-28°C)
        if 15 <= temp <= 28:
            score += 3
        elif 10 <= temp < 15 or 28 < temp <= 32:
            score += 1
        elif temp < 5 or temp > 35:
            score -= 2
        
        # Weather condition scoring
        if any(word in description for word in ["clear", "sunny"]):
            score += 2
        elif any(word in description for word in ["cloud", "partly"]):
            score += 1
        elif any(word in description for word in ["rain", "drizzle"]):
            score -= 2
        elif any(word in description for word in ["storm", "thunder", "heavy"]):
            score -= 3
        
        return max(1, min(10, score))
    
    def _get_recommendation(self, overall_score: float) -> str:
        """Get travel recommendation based on weather score"""
        if overall_score >= 8:
            return "Excellent weather conditions for travel!"
        elif overall_score >= 6:
            return "Good weather conditions. Suitable for travel."
        elif overall_score >= 4:
            return "Fair weather. Consider packing accordingly."
        else:
            return "Weather conditions may not be ideal. Consider alternative dates or destinations."