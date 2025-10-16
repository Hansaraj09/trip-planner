from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re

def parse_date(date_string: str) -> Optional[datetime]:
    """Parse date string to datetime object"""
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%d/%m/%Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None

def format_date(date_obj: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Format datetime object to string"""
    return date_obj.strftime(format_str)

def calculate_days_between(start_date: str, end_date: str) -> int:
    """Calculate number of days between two dates"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    if start and end:
        return (end - start).days
    return 0

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "INR": "₹",
        "JPY": "¥"
    }
    
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"

def validate_iata_code(code: str) -> bool:
    """Validate IATA airport/city code"""
    return bool(re.match(r'^[A-Z]{3}$', code.upper()))

def get_airport_code_suggestions(city: str) -> str:
    """Get common airport code for major cities"""
    city_codes = {
        "new york": "NYC",
        "london": "LON",
        "paris": "PAR",
        "tokyo": "TYO",
        "dubai": "DXB",
        "singapore": "SIN",
        "hong kong": "HKG",
        "mumbai": "BOM",
        "delhi": "DEL",
        "bangalore": "BLR",
        "bengaluru": "BLR",
        "los angeles": "LAX",
        "san francisco": "SFO",
        "chicago": "CHI",
        "miami": "MIA",
        "sydney": "SYD",
        "melbourne": "MEL",
        "rome": "ROM",
        "barcelona": "BCN",
        "amsterdam": "AMS",
        "berlin": "BER",
        "madrid": "MAD"
    }
    
    return city_codes.get(city.lower(), city[:3].upper())

def calculate_budget_breakdown(
    total_budget: float,
    flight_cost: float,
    hotel_cost: float
) -> Dict[str, Any]:
    """Calculate budget breakdown"""
    spent = flight_cost + hotel_cost
    remaining = total_budget - spent
    percentage_spent = (spent / total_budget) * 100 if total_budget > 0 else 0
    
    return {
        "total_budget": total_budget,
        "flight_cost": flight_cost,
        "hotel_cost": hotel_cost,
        "total_spent": spent,
        "remaining": remaining,
        "percentage_spent": round(percentage_spent, 2),
        "within_budget": spent <= total_budget
    }

def generate_summary(trip_data: Dict[str, Any]) -> str:
    """Generate human-readable trip summary"""
    summary_parts = []
    
    if "destination" in trip_data:
        summary_parts.append(f"Destination: {trip_data['destination']}")
    
    if "dates" in trip_data:
        summary_parts.append(f"Travel Dates: {trip_data['dates']}")
    
    if "duration" in trip_data:
        summary_parts.append(f"Duration: {trip_data['duration']} days")
    
    if "budget" in trip_data:
        summary_parts.append(f"Budget: {format_currency(trip_data['budget'])}")
    
    return " | ".join(summary_parts)

def prioritize_options(
    options: list,
    criteria: str = "price",
    max_results: int = 5
) -> list:
    """Prioritize and limit options based on criteria"""
    if not options:
        return []
    
    # Sort by criteria
    if criteria == "price":
        sorted_options = sorted(options, key=lambda x: x.get("price", float('inf')))
    elif criteria == "rating":
        sorted_options = sorted(options, key=lambda x: x.get("rating", 0), reverse=True)
    else:
        sorted_options = options
    
    return sorted_options[:max_results]