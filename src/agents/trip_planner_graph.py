from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import operator
from datetime import datetime, timedelta

from src.config.settings import settings
from src.tools.weather_tool import WeatherTool
from src.tools.amadeus_tool import AmadeusTool
from src.tools.attractions_tool import AttractionsTool
from src.utils.helpers import (
    calculate_days_between, 
    get_airport_code_suggestions,
    calculate_budget_breakdown,
    format_date
)
from src.utils.parsers import ResponseParser

# Define the state
class TripPlannerState(TypedDict):
    """State for the trip planner agent"""
    origin: str
    destination: str
    start_date: str
    end_date: str
    duration: int
    budget: float
    travel_type: str
    adults: int
    messages: Annotated[Sequence[str], operator.add]
    weather_data: dict
    flight_options: list
    hotel_options: dict
    selected_flight: dict
    selected_hotel: dict
    attractions: list
    itinerary: list
    budget_breakdown: dict
    weather_favorable: bool
    budget_feasible: bool
    options_available: bool
    needs_alternatives: bool
    final_plan: dict
    alternative_plans: list
    current_step: str

class TripPlannerGraph:
    """LangGraph-based trip planner agent"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.google_api_key,
            temperature=settings.temperature,
            convert_system_message_to_human=True
        )
        self.weather_tool = WeatherTool()
        self.amadeus_tool = AmadeusTool()
        self.attractions_tool = AttractionsTool()
        self.parser = ResponseParser()
        self.graph = self._build_graph()    
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(TripPlannerState)
        
        # Add nodes
        workflow.add_node("check_weather", self.check_weather_node)
        workflow.add_node("search_flights", self.search_flights_node)
        workflow.add_node("search_hotels", self.search_hotels_node)
        workflow.add_node("filter_by_budget", self.filter_by_budget_node)
        workflow.add_node("get_attractions", self.get_attractions_node)
        workflow.add_node("generate_itinerary", self.generate_itinerary_node)
        workflow.add_node("find_alternatives", self.find_alternatives_node)
        workflow.add_node("finalize_plan", self.finalize_plan_node)
        
        workflow.set_entry_point("check_weather")
        
        workflow.add_conditional_edges(
            "check_weather",
            self.weather_decision,
            {"favorable": "search_flights", "unfavorable": "find_alternatives"}
        )
        
        workflow.add_edge("search_flights", "search_hotels")
        workflow.add_edge("search_hotels", "filter_by_budget")
        
        workflow.add_conditional_edges(
            "filter_by_budget",
            self.budget_decision,
            {"within_budget": "get_attractions", "over_budget": "find_alternatives"}
        )
        
        workflow.add_edge("get_attractions", "generate_itinerary")
        workflow.add_edge("generate_itinerary", "finalize_plan")
        workflow.add_edge("find_alternatives", "finalize_plan")
        workflow.add_edge("finalize_plan", END)
        
        return workflow.compile()
    
    def check_weather_node(self, state: TripPlannerState) -> TripPlannerState:
        """Check weather conditions"""
        print(f"🌤️ Checking weather for {state['destination']}...")
        forecast = self.weather_tool.get_forecast(state["destination"], state["duration"])
        weather_analysis = self.weather_tool.analyze_weather_conditions(forecast)
        state["weather_data"] = weather_analysis
        state["weather_favorable"] = weather_analysis.get("is_favorable", True)
        state["messages"] = [f"Weather check completed"]
        state["current_step"] = "weather_checked"
        return state

    def search_flights_node(self, state: TripPlannerState) -> TripPlannerState:
        """Search for flights"""
        print(f"✈️ Searching flights...")
        origin_code = get_airport_code_suggestions(state["origin"])
        dest_code = get_airport_code_suggestions(state["destination"])
        
        flights = self.amadeus_tool.search_flights(
            origin=origin_code,
            destination=dest_code,
            departure_date=state["start_date"],
            return_date=state["end_date"],
            adults=state["adults"],
            max_results=10,
            max_price=state["budget"] * 0.6
        )
        state["flight_options"] = flights.get("flights", [])
        state["messages"] = state.get("messages", []) + [f"Found {len(state['flight_options'])} flights"]
        state["current_step"] = "flights_searched"
        return state

    def search_hotels_node(self, state: TripPlannerState) -> TripPlannerState:
        """Search for hotels"""
        print(f"🏨 Searching hotels...")
        city_code = get_airport_code_suggestions(state["destination"])
        hotels = self.amadeus_tool.search_hotels(
            city_code=city_code,
            check_in_date=state["start_date"],
            check_out_date=state["end_date"],
            adults=state["adults"],
            max_price=state["budget"] * 0.3
        )
        state["hotel_options"] = hotels
        state["messages"] = state.get("messages", []) + [f"Found {hotels.get('count', 0)} hotels"]
        state["current_step"] = "hotels_searched"
        return state

    def filter_by_budget_node(self, state: TripPlannerState) -> TripPlannerState:
        """Filter by budget"""
        print(f"💰 Filtering by budget...")
        try:
            combinations = self.amadeus_tool.filter_by_budget(
                flights=state.get("flight_options", []),
                hotels=state.get("hotel_options", {}).get("hotels", []),
                budget=state["budget"],
                num_nights=state["duration"]
            )
            
            if combinations.get("count", 0) > 0:
                best = combinations["combinations"][0]
                state["selected_flight"] = best["flight"]
                state["selected_hotel"] = best["hotel"]
                state["budget_feasible"] = True
                state["options_available"] = True
                
                flight_cost = best["flight"]["price"] * 2
                hotel_cost = best["hotel"]["price"] * state["duration"]
                state["budget_breakdown"] = calculate_budget_breakdown(
                    state["budget"], flight_cost, hotel_cost
                )
                state["messages"] = state.get("messages", []) + ["Found budget-friendly options"]
            else:
                state["budget_feasible"] = False
                state["options_available"] = False
                state["needs_alternatives"] = True
                state["messages"] = state.get("messages", []) + ["No options within budget"]
        except Exception as e:
            print(f"Budget filter error: {e}")
            state["budget_feasible"] = False
            state["options_available"] = False
            state["needs_alternatives"] = True
        state["current_step"] = "budget_filtered"
        return state
    
    def get_attractions_node(self, state: TripPlannerState) -> TripPlannerState:
        """Get attractions"""
        print(f"🎯 Finding attractions...")
        try:
            attractions_data = self.attractions_tool.get_attractions(
                city=state["destination"],
                travel_type=state["travel_type"],
                days=state["duration"]
            )
            state["attractions"] = attractions_data["attractions"]
            state["messages"] = state.get("messages", []) + [f"Found {len(state['attractions'])} attractions"]
        except Exception as e:
            print(f"Attractions error: {e}")
            state["attractions"] = []
        state["current_step"] = "attractions_found"
        return state
    
    def generate_itinerary_node(self, state: TripPlannerState) -> TripPlannerState:
        """Generate itinerary"""
        print(f"📅 Generating itinerary...")
        try:
            itinerary = self.attractions_tool.generate_daily_itinerary(
                attractions=state["attractions"],
                days=state["duration"],
                travel_type=state["travel_type"]
            )
            state["itinerary"] = itinerary
            state["messages"] = state.get("messages", []) + ["Itinerary generated"]
        except Exception as e:
            print(f"Itinerary error: {e}")
            state["itinerary"] = []
        state["current_step"] = "itinerary_generated"
        return state
    
    def find_alternatives_node(self, state: TripPlannerState) -> TripPlannerState:
        """Find alternatives"""
        print(f"🔄 Finding alternatives...")
        alternatives = []
        if not state.get("weather_favorable", True):
            alternatives.append({
                "type": "weather",
                "reason": "Weather not favorable",
                "suggestion": "Consider traveling 1-2 weeks later"
            })
        if not state.get("budget_feasible", True):
            alternatives.append({
                "type": "budget",
                "reason": "No options within budget",
                "suggestions": ["Increase budget by 20%", "Reduce trip duration", "Choose nearby destination"]
            })
        state["alternative_plans"] = alternatives
        state["needs_alternatives"] = True
        state["current_step"] = "alternatives_found"
        return state
    
    def finalize_plan_node(self, state: TripPlannerState) -> TripPlannerState:
        """Finalize plan"""
        print(f"✅ Finalizing...")
        if state.get("options_available", False):
            state["final_plan"] = {
                "destination": state["destination"],
                "origin": state["origin"],
                "dates": {
                    "start": state["start_date"],
                    "end": state["end_date"],
                    "duration": state["duration"]
                },
                "weather": state["weather_data"],
                "flight": state["selected_flight"],
                "hotel": state["selected_hotel"],
                "budget_breakdown": state["budget_breakdown"],
                "itinerary": state["itinerary"],
                "attractions": state["attractions"],
                "travel_type": state["travel_type"],
                "status": "success"
            }
        else:
            state["final_plan"] = {
                "destination": state["destination"],
                "status": "alternatives_only",
                "reason": "Could not find options meeting constraints",
                "alternatives": state.get("alternative_plans", [])
            }
        state["current_step"] = "completed"
        return state
    
    def weather_decision(self, state: TripPlannerState) -> str:
        return "favorable" if state.get("weather_favorable", False) else "unfavorable"
    
    def budget_decision(self, state: TripPlannerState) -> str:
        return "within_budget" if state.get("budget_feasible", False) and state.get("options_available", False) else "over_budget"
    
    def plan_trip(self, user_input: dict) -> dict:
        """Main trip planning function"""
        initial_state = {
            "origin": user_input.get("origin", ""),
            "destination": user_input.get("destination", ""),
            "start_date": user_input.get("start_date", ""),
            "end_date": user_input.get("end_date", ""),
            "duration": user_input.get("duration", 3),
            "budget": user_input.get("budget", 1000.0),
            "travel_type": user_input.get("travel_type", "sightseeing"),
            "adults": user_input.get("adults", 1),
            "messages": [],
            "weather_data": {},
            "flight_options": [],
            "hotel_options": {},
            "selected_flight": {},
            "selected_hotel": {},
            "attractions": [],
            "itinerary": [],
            "budget_breakdown": {},
            "weather_favorable": False,
            "budget_feasible": False,
            "options_available": False,
            "needs_alternatives": False,
            "final_plan": {},
            "alternative_plans": [],
            "current_step": "initialized"
        }
        
        result = self.graph.invoke(initial_state)
        return result
    
    def chat_with_user(self, user_query: str, context: dict = None) -> str:
        """Chat interface"""
        try:
            system_prompt = "You are a helpful travel assistant. Answer questions clearly and concisely."
            context_str = f"\nTrip Context: {context}" if context else ""
            
            messages = [
                SystemMessage(content=system_prompt + context_str),
                HumanMessage(content=user_query)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"I'm having trouble responding right now. Error: {str(e)}"