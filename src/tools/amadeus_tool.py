from amadeus import Client, ResponseError
from typing import Dict, List, Any, Optional

class AmadeusTool:
    """Tool for fetching flight and hotel data from Amadeus API"""
    
    def __init__(self):
        self.api_working = False
        self.client = None
        
        # PUT YOUR CREDENTIALS HERE - Replace with your actual keys
        API_KEY = "DcWlSGNyMqJqmPdzEYHbuuH6dCaZTIBs"  # 32 characters
        API_SECRET = "DI394JIvwoEfln5D"  # 16 characters
        
        try:
            # Initialize client
            self.client = Client(
                client_id=API_KEY,
                client_secret=API_SECRET,
                hostname='test'
            )
            
            # Test connection
            response = self.client.reference_data.locations.get(
                keyword='NYC',
                subType='CITY'
            )
            
            # Verify response
            if response and response.data:
                print("✅ Amadeus API connected")
                print(f"   Found {len(response.data)} locations")
                self.api_working = True
            else:
                print("⚠️ API responded but no data. Using mock data.")
                
        except Exception as e:
            print(f"⚠️ Amadeus API failed: {str(e)}. Using mock data.")
            self.client = None
    
    def search_flights(self, origin, destination, departure_date, return_date=None, adults=1, max_results=10, max_price=None):
        """Search for flights"""
        if not self.api_working:
            return self._get_mock_flights(origin, destination, departure_date)
        
        try:
            params = {
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDate": departure_date,
                "adults": adults,
                "max": max_results
            }
            
            if return_date:
                params["returnDate"] = return_date
            if max_price:
                params["maxPrice"] = int(max_price)
            
            response = self.client.shopping.flight_offers_search.get(**params)
            
            flights = []
            for offer in response.data:
                flight_info = self._parse_flight_offer(offer)
                if flight_info:
                    flights.append(flight_info)
            
            flights.sort(key=lambda x: x["price"])
            return {"status": "success", "flights": flights, "count": len(flights)}
        except Exception as e:
            print(f"Flight search failed: {e}")
            return self._get_mock_flights(origin, destination, departure_date)
    
    def search_hotels(self, city_code, check_in_date, check_out_date, adults=1, max_price=None, radius=50):
        """Search for hotels"""
        if not self.api_working:
            return self._get_mock_hotels(city_code, check_in_date, check_out_date)
        
        try:
            hotel_response = self.client.reference_data.locations.hotels.by_city.get(cityCode=city_code)
            
            if not hotel_response.data:
                return self._get_mock_hotels(city_code, check_in_date, check_out_date)
            
            hotel_ids = [hotel["hotelId"] for hotel in hotel_response.data[:10]]
            
            offers_response = self.client.shopping.hotel_offers_search.get(
                hotelIds=",".join(hotel_ids),
                checkInDate=check_in_date,
                checkOutDate=check_out_date,
                adults=adults
            )
            
            hotels = []
            for offer in offers_response.data:
                hotel_info = self._parse_hotel_offer(offer)
                if hotel_info and (not max_price or hotel_info["price"] <= max_price):
                    hotels.append(hotel_info)
            
            hotels.sort(key=lambda x: x["price"])
            return {"status": "success", "hotels": hotels, "count": len(hotels)}
        except Exception as e:
            print(f"Hotel search failed: {e}")
            return self._get_mock_hotels(city_code, check_in_date, check_out_date)
    
    def _parse_flight_offer(self, offer: Dict) -> Optional[Dict[str, Any]]:
        """Parse flight offer"""
        try:
            price = float(offer.get("price", {}).get("total", 0))
            currency = offer.get("price", {}).get("currency", "USD")
            itinerary = offer.get("itineraries", [{}])[0]
            segments = itinerary.get("segments", [{}])
            
            if not segments:
                return None
            
            departure = segments[0].get("departure", {})
            arrival = segments[-1].get("arrival", {})
            duration_str = itinerary.get("duration", "PT2H")
            
            import re
            hours = 0
            minutes = 0
            h_match = re.search(r'(\d+)H', duration_str)
            m_match = re.search(r'(\d+)M', duration_str)
            if h_match:
                hours = int(h_match.group(1))
            if m_match:
                minutes = int(m_match.group(1))
            duration_hours = round(hours + minutes / 60, 2)
            
            return {
                "price": price,
                "currency": currency,
                "departure_airport": departure.get("iataCode", ""),
                "arrival_airport": arrival.get("iataCode", ""),
                "departure_time": departure.get("at", ""),
                "arrival_time": arrival.get("at", ""),
                "duration_hours": duration_hours,
                "stops": len(segments) - 1,
                "airline": segments[0].get("carrierCode", ""),
                "booking_class": segments[0].get("cabin", "ECONOMY")
            }
        except Exception:
            return None
    
    def _parse_hotel_offer(self, offer: Dict) -> Optional[Dict[str, Any]]:
        """Parse hotel offer"""
        try:
            hotel = offer.get("hotel", {})
            offers_list = offer.get("offers", [])
            
            if not offers_list:
                return None
            
            cheapest = min(offers_list, key=lambda x: float(x.get("price", {}).get("total", 999999)))
            price = float(cheapest.get("price", {}).get("total", 0))
            currency = cheapest.get("price", {}).get("currency", "USD")
            
            return {
                "hotel_id": hotel.get("hotelId", ""),
                "name": hotel.get("name", "Hotel"),
                "price": price,
                "currency": currency,
                "rating": str(hotel.get("rating", "3")),
                "room_type": cheapest.get("room", {}).get("typeEstimated", {}).get("category", "Standard"),
                "beds": cheapest.get("room", {}).get("typeEstimated", {}).get("beds", 2),
                "check_in": cheapest.get("checkInDate", ""),
                "check_out": cheapest.get("checkOutDate", "")
            }
        except Exception:
            return None
    
    def _get_mock_flights(self, origin, dest, date):
        """Mock flight data"""
        import random
        base_prices = {
            ('NYC', 'LON'): 450, ('NYC', 'PAR'): 480, ('NYC', 'TYO'): 850,
            ('LON', 'PAR'): 120, ('LON', 'NYC'): 450, ('LON', 'DXB'): 380,
            ('BOM', 'DXB'): 200, ('DEL', 'LON'): 520, ('SFO', 'TYO'): 750,
        }
        
        route = (origin[:3].upper(), dest[:3].upper())
        base = base_prices.get(route, 500)
        
        flights = []
        for i in range(3):
            price = base + random.randint(-100, 150)
            flights.append({
                "price": float(price),
                "currency": "USD",
                "departure_airport": origin,
                "arrival_airport": dest,
                "departure_time": f"{date}T{8+i*2:02d}:00:00",
                "arrival_time": f"{date}T{14+i*2:02d}:00:00",
                "duration_hours": 6.0 + i * 0.5,
                "stops": i % 2,
                "airline": ["AA", "UA", "DL"][i],
                "booking_class": "ECONOMY"
            })
        
        return {"status": "success", "flights": flights, "count": len(flights)}
    
    def _get_mock_hotels(self, city, checkin, checkout):
        """Mock hotel data"""
        import random
        city_prices = {
            'NYC': (150, 300), 'LON': (120, 280), 'PAR': (100, 250),
            'TYO': (130, 290), 'DXB': (110, 240), 'BOM': (60, 150),
        }
        
        city_key = city[:3].upper()
        price_range = city_prices.get(city_key, (80, 200))
        
        hotels = []
        names = [("Grand Hotel", "4", "Deluxe"), ("City Inn", "3", "Standard"), ("Budget Stay", "3", "Economy")]
        
        for i, (name, rating, room) in enumerate(names):
            price = random.randint(price_range[0], price_range[1])
            hotels.append({
                "hotel_id": f"H{i+1:03d}",
                "name": f"{name} {city}",
                "price": float(price),
                "currency": "USD",
                "rating": rating,
                "room_type": room,
                "beds": 2 if i == 0 else 1,
                "check_in": checkin,
                "check_out": checkout
            })
        
        return {"status": "success", "hotels": hotels, "count": len(hotels)}
    
    def get_city_code(self, city_name):
        """Get IATA code"""
        if not self.api_working:
            return None
        try:
            response = self.client.reference_data.locations.get(keyword=city_name, subType="CITY")
            if response.data:
                return response.data[0]["iataCode"]
        except Exception:
            pass
        return None
    
    def filter_by_budget(self, flights, hotels, budget, num_nights):
        """Filter by budget"""
        valid = []
        for flight in flights:
            remaining = budget - (flight["price"] * 2)
            if remaining <= 0:
                continue
            
            for hotel in hotels:
                total_hotel = hotel["price"] * num_nights
                total = (flight["price"] * 2) + total_hotel
                
                if total <= budget:
                    valid.append({
                        "flight": flight,
                        "hotel": hotel,
                        "total_cost": total,
                        "remaining_budget": budget - total
                    })
        
        valid.sort(key=lambda x: x["total_cost"])
        return {"status": "success", "combinations": valid, "count": len(valid)}