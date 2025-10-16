from typing import Dict, List, Any
import random

class AttractionsTool:
    """Tool for generating attraction recommendations"""
    
    # Popular attractions database (simplified - in production, use a real API)
    ATTRACTIONS_DB = {
        "paris": [
            {"name": "Eiffel Tower", "type": "landmark", "duration": 3, "rating": 4.8},
            {"name": "Louvre Museum", "type": "museum", "duration": 4, "rating": 4.7},
            {"name": "Notre-Dame Cathedral", "type": "landmark", "duration": 2, "rating": 4.6},
            {"name": "Arc de Triomphe", "type": "landmark", "duration": 1, "rating": 4.5},
            {"name": "Versailles Palace", "type": "historical", "duration": 5, "rating": 4.9},
        ],
        "london": [
            {"name": "Big Ben", "type": "landmark", "duration": 1, "rating": 4.7},
            {"name": "Tower of London", "type": "historical", "duration": 3, "rating": 4.6},
            {"name": "British Museum", "type": "museum", "duration": 4, "rating": 4.8},
            {"name": "London Eye", "type": "adventure", "duration": 2, "rating": 4.5},
            {"name": "Buckingham Palace", "type": "landmark", "duration": 2, "rating": 4.6},
        ],
        "new york": [
            {"name": "Statue of Liberty", "type": "landmark", "duration": 4, "rating": 4.8},
            {"name": "Central Park", "type": "nature", "duration": 3, "rating": 4.7},
            {"name": "Empire State Building", "type": "landmark", "duration": 2, "rating": 4.6},
            {"name": "Metropolitan Museum", "type": "museum", "duration": 4, "rating": 4.9},
            {"name": "Times Square", "type": "sightseeing", "duration": 2, "rating": 4.5},
        ],
        "tokyo": [
            {"name": "Tokyo Tower", "type": "landmark", "duration": 2, "rating": 4.6},
            {"name": "Senso-ji Temple", "type": "historical", "duration": 2, "rating": 4.7},
            {"name": "Shibuya Crossing", "type": "sightseeing", "duration": 1, "rating": 4.5},
            {"name": "Mount Fuji", "type": "nature", "duration": 8, "rating": 4.9},
            {"name": "Tokyo Disneyland", "type": "adventure", "duration": 8, "rating": 4.8},
        ],
        "dubai": [
            {"name": "Burj Khalifa", "type": "landmark", "duration": 3, "rating": 4.9},
            {"name": "Dubai Mall", "type": "shopping", "duration": 4, "rating": 4.7},
            {"name": "Palm Jumeirah", "type": "sightseeing", "duration": 3, "rating": 4.6},
            {"name": "Desert Safari", "type": "adventure", "duration": 6, "rating": 4.8},
            {"name": "Dubai Marina", "type": "sightseeing", "duration": 2, "rating": 4.5},
        ],
        "default": [
            {"name": "City Center", "type": "sightseeing", "duration": 2, "rating": 4.0},
            {"name": "Local Museum", "type": "museum", "duration": 3, "rating": 4.2},
            {"name": "Historical District", "type": "historical", "duration": 3, "rating": 4.3},
            {"name": "Public Park", "type": "nature", "duration": 2, "rating": 4.1},
            {"name": "Shopping District", "type": "shopping", "duration": 3, "rating": 4.0},
        ]
    }
    
    def get_attractions(
        self,
        city: str,
        travel_type: str = "sightseeing",
        days: int = 3
    ) -> Dict[str, Any]:
        """Get attraction recommendations for a city"""
        city_lower = city.lower()
        
        # Get attractions from database
        attractions = self.ATTRACTIONS_DB.get(city_lower, self.ATTRACTIONS_DB["default"])
        
        # Filter by travel type
        filtered = self._filter_by_type(attractions, travel_type)
        
        return {
            "city": city,
            "attractions": filtered,
            "count": len(filtered),
            "status": "success"
        }
    
    def _filter_by_type(self, attractions: List[Dict], travel_type: str) -> List[Dict]:
        """Filter attractions based on travel type preference"""
        type_mapping = {
            "relaxation": ["nature", "sightseeing"],
            "adventure": ["adventure", "nature", "historical"],
            "sightseeing": ["landmark", "sightseeing", "historical", "museum"],
            "cultural": ["museum", "historical", "landmark"],
            "shopping": ["shopping", "sightseeing"]
        }
        
        preferred_types = type_mapping.get(travel_type.lower(), ["sightseeing"])
        
        # Filter and sort attractions
        filtered = [a for a in attractions if a["type"] in preferred_types]
        
        # If no match, return all
        if not filtered:
            filtered = attractions
        
        # Sort by rating
        filtered.sort(key=lambda x: x["rating"], reverse=True)
        
        return filtered
    
    def generate_daily_itinerary(
        self,
        attractions: List[Dict],
        days: int,
        travel_type: str = "sightseeing"
    ) -> List[Dict[str, Any]]:
        """Generate day-by-day itinerary"""
        itinerary = []
        
        # Distribute attractions across days
        attractions_per_day = max(2, len(attractions) // days)
        
        for day in range(1, days + 1):
            start_idx = (day - 1) * attractions_per_day
            end_idx = start_idx + attractions_per_day
            
            if day == days:  # Last day gets remaining attractions
                day_attractions = attractions[start_idx:]
            else:
                day_attractions = attractions[start_idx:end_idx]
            
            # Calculate day schedule
            schedule = self._create_day_schedule(day_attractions)
            
            itinerary.append({
                "day": day,
                "date": f"Day {day}",
                "attractions": day_attractions,
                "schedule": schedule,
                "total_duration": sum(a["duration"] for a in day_attractions)
            })
        
        return itinerary
    
    def _create_day_schedule(self, attractions: List[Dict]) -> List[Dict[str, str]]:
        """Create time-based schedule for attractions"""
        schedule = []
        current_hour = 9  # Start at 9 AM
        
        for attraction in attractions:
            start_time = f"{current_hour:02d}:00"
            end_hour = current_hour + attraction["duration"]
            end_time = f"{end_hour:02d}:00"
            
            schedule.append({
                "attraction": attraction["name"],
                "start_time": start_time,
                "end_time": end_time,
                "duration": f"{attraction['duration']} hours"
            })
            
            current_hour = end_hour + 1  # Add 1 hour break
        
        return schedule
    
    def get_restaurant_recommendations(
        self,
        city: str,
        cuisine_type: str = "local"
    ) -> List[Dict[str, str]]:
        """Get restaurant recommendations"""
        # Simplified restaurant database
        restaurants = [
            {"name": f"{city} Traditional Restaurant", "cuisine": "local", "price": "$$"},
            {"name": f"Downtown Cafe", "cuisine": "international", "price": "$"},
            {"name": f"Gourmet {city}", "cuisine": "fine dining", "price": "$$$"},
            {"name": f"Street Food Market", "cuisine": "street food", "price": "$"},
        ]
        
        return restaurants