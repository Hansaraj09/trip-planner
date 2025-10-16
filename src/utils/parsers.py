from typing import Dict, Any, List
import json
import re

class ResponseParser:
    """Parser for API responses and LLM outputs"""
    
    @staticmethod
    def parse_user_input(user_text: str) -> Dict[str, Any]:
        """Parse natural language user input to extract trip details"""
        parsed = {
            "destination": None,
            "origin": None,
            "start_date": None,
            "end_date": None,
            "duration": None,
            "budget": None,
            "travel_type": "sightseeing",
            "adults": 1
        }
        
        # Extract budget (look for numbers with currency symbols or keywords)
        budget_match = re.search(r'(?:budget|spend|afford).*?(\d+(?:,\d{3})*(?:\.\d{2})?)', user_text, re.IGNORECASE)
        if budget_match:
            parsed["budget"] = float(budget_match.group(1).replace(',', ''))
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*(?:day|night)s?', user_text, re.IGNORECASE)
        if duration_match:
            parsed["duration"] = int(duration_match.group(1))
        
        # Extract travel type
        if re.search(r'adventure|hiking|trekking|extreme', user_text, re.IGNORECASE):
            parsed["travel_type"] = "adventure"
        elif re.search(r'relax|beach|spa|leisure', user_text, re.IGNORECASE):
            parsed["travel_type"] = "relaxation"
        elif re.search(r'culture|museum|historical|heritage', user_text, re.IGNORECASE):
            parsed["travel_type"] = "cultural"
        elif re.search(r'shopping|mall', user_text, re.IGNORECASE):
            parsed["travel_type"] = "shopping"
        
        return parsed
    
    @staticmethod
    def format_flight_info(flight: Dict[str, Any]) -> str:
        """Format flight information for display"""
        lines = [
            f"✈️ Flight Details:",
            f"  Route: {flight['departure_airport']} → {flight['arrival_airport']}",
            f"  Departure: {flight['departure_time']}",
            f"  Arrival: {flight['arrival_time']}",
            f"  Duration: {flight['duration_hours']} hours",
            f"  Stops: {flight['stops']}",
            f"  Price: {flight['currency']} {flight['price']:.2f}",
            f"  Airline: {flight['airline']}"
        ]
        return "\n".join(lines)
    
    @staticmethod
    def format_hotel_info(hotel: Dict[str, Any]) -> str:
        """Format hotel information for display"""
        lines = [
            f"🏨 Hotel Details:",
            f"  Name: {hotel['name']}",
            f"  Rating: {hotel['rating']} ⭐",
            f"  Room Type: {hotel['room_type']}",
            f"  Price per Night: {hotel['currency']} {hotel['price']:.2f}",
            f"  Check-in: {hotel['check_in']}",
            f"  Check-out: {hotel['check_out']}"
        ]
        return "\n".join(lines)
    
    @staticmethod
    def format_weather_info(weather: Dict[str, Any]) -> str:
        """Format weather information for display"""
        if weather.get("status") != "success":
            return f"⚠️ Weather data unavailable: {weather.get('message', 'Unknown error')}"
        
        lines = [
            f"🌤️ Weather Forecast for {weather['city']}:",
            f"  Overall Score: {weather['overall_score']}/10",
            f"  Recommendation: {weather['recommendation']}",
            ""
        ]
        
        if weather.get("favorable_days"):
            lines.append("  Best Days:")
            for day in weather["favorable_days"][:3]:
                lines.append(f"    • {day['date']}: {day['temp']}°C - {day['description']}")
        
        if weather.get("warnings"):
            lines.append("\n  ⚠️ Weather Warnings:")
            for warning in weather["warnings"]:
                lines.append(f"    • {warning}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_itinerary(itinerary: List[Dict[str, Any]]) -> str:
        """Format daily itinerary for display"""
        lines = ["📅 Daily Itinerary:", ""]
        
        for day_plan in itinerary:
            lines.append(f"Day {day_plan['day']}:")
            lines.append(f"  Total Duration: {day_plan['total_duration']} hours")
            lines.append("")
            
            for schedule_item in day_plan["schedule"]:
                lines.append(
                    f"  {schedule_item['start_time']} - {schedule_item['end_time']}: "
                    f"{schedule_item['attraction']} ({schedule_item['duration']})"
                )
            
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_budget_summary(budget_data: Dict[str, Any]) -> str:
        """Format budget summary for display"""
        lines = [
            "💰 Budget Summary:",
            f"  Total Budget: ${budget_data['total_budget']:.2f}",
            f"  Flight Cost: ${budget_data['flight_cost']:.2f}",
            f"  Hotel Cost: ${budget_data['hotel_cost']:.2f}",
            f"  Total Spent: ${budget_data['total_spent']:.2f}",
            f"  Remaining: ${budget_data['remaining']:.2f}",
            f"  Budget Used: {budget_data['percentage_spent']:.1f}%"
        ]
        
        if not budget_data['within_budget']:
            lines.append("\n  ⚠️ WARNING: Over budget!")
        else:
            lines.append("\n  ✅ Within budget")
        
        return "\n".join(lines)
    
    @staticmethod
    def create_trip_summary(trip_data: Dict[str, Any]) -> str:
        """Create comprehensive trip summary"""
        sections = []
        
        # Header
        sections.append("=" * 60)
        sections.append("🌍 TRIP PLANNING SUMMARY")
        sections.append("=" * 60)
        sections.append("")
        
        # Basic info
        if "destination" in trip_data:
            sections.append(f"Destination: {trip_data['destination']}")
        if "duration" in trip_data:
            sections.append(f"Duration: {trip_data['duration']} days")
        if "travel_type" in trip_data:
            sections.append(f"Travel Type: {trip_data['travel_type'].title()}")
        
        sections.append("")
        
        # Weather
        if "weather" in trip_data:
            sections.append(ResponseParser.format_weather_info(trip_data["weather"]))
            sections.append("")
        
        # Flight
        if "flight" in trip_data:
            sections.append(ResponseParser.format_flight_info(trip_data["flight"]))
            sections.append("")
        
        # Hotel
        if "hotel" in trip_data:
            sections.append(ResponseParser.format_hotel_info(trip_data["hotel"]))
            sections.append("")
        
        # Budget
        if "budget_breakdown" in trip_data:
            sections.append(ResponseParser.format_budget_summary(trip_data["budget_breakdown"]))
            sections.append("")
        
        # Itinerary
        if "itinerary" in trip_data:
            sections.append(ResponseParser.format_itinerary(trip_data["itinerary"]))
        
        sections.append("=" * 60)
        
        return "\n".join(sections)