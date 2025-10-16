App Link:  https://trip-planner-2-okxb.onrender.com/


🌍 Intelligent Trip Planner Agent
An AI-powered trip planning system built with LangChain, LangGraph, Google Gemini, and real-time APIs for weather, flights, and hotels.

🎯 Features
Conversational Interface: Natural language input for trip requirements
Weather Intelligence: Real-time weather forecasts and recommendations using OpenWeather API
Smart Flight Search: Find best flight options within budget using Amadeus API
Hotel Recommendations: Search and filter hotels based on preferences
Budget Optimization: Automatically finds the cheapest combinations within your budget
AI-Powered Itinerary: Daily plans with attractions and activities
Alternative Suggestions: Provides backup options when constraints aren't met
LangSmith Monitoring: Track agent decisions and performance
Chat Assistant: Interactive Q&A about your trip plan
🏗️ Architecture
The system uses LangGraph to create a decision-flow workflow:

User Input → Weather Check → Flights Search → Hotels Search → 
Budget Filter → Attractions → Itinerary → Final Plan
Decision Nodes
Weather Node: Evaluates weather conditions; suggests alternatives if unfavorable
Budget Node: Filters options within budget; triggers alternatives if over-budget
Alternative Node: Generates backup plans when constraints aren't met
🚀 Quick Start
Prerequisites
Python 3.9+
API Keys for:
Google Gemini (AI)
OpenWeatherMap (Weather)
Amadeus (Flights & Hotels)
LangSmith (Optional, for monitoring)
Installation
Clone or create the project directory:
bash
mkdir trip-planner-agent
cd trip-planner-agent
Create the project structure:
trip-planner-agent/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── trip_planner_graph.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── weather_tool.py
│   │   ├── amadeus_tool.py
│   │   └── attractions_tool.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   └── parsers.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   └── __init__.py
├── app.py
├── requirements.txt
├── .env
├── .env.example
└── README.md
Create a virtual environment:
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
Install dependencies:
bash
pip install -r requirements.txt
Configure API Keys:
Create a .env file in the root directory (copy from .env.example):

env
# Google Gemini API Key
GOOGLE_API_KEY=your_google_api_key_here

# OpenWeatherMap API Key
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Amadeus API Credentials
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here

# LangSmith Configuration (Optional)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=trip-planner-agent
Getting API Keys
1. Google Gemini API
Visit: https://makersuite.google.com/app/apikey
Click "Create API Key"
Copy the key to your .env file
2. OpenWeatherMap API
Visit: https://openweathermap.org/api
Sign up for a free account
Navigate to "API keys" tab
Generate and copy the key
3. Amadeus API
Visit: https://developers.amadeus.com/
Create a free account
Go to "My Self-Service Workspace"
Create a new app
Copy both API Key and API Secret
4. LangSmith (Optional - for monitoring)
Visit: https://smith.langchain.com/
Sign up for an account
Go to Settings → API Keys
Create and copy the key
🎮 Running the Application
Option 1: Streamlit UI (Recommended)
bash
streamlit run app.py
The application will open in your browser at http://localhost:8501

Option 2: Python Script
Create a test script test_planner.py:

python
from src.agents.trip_planner_graph import TripPlannerGraph
from src.utils.parsers import ResponseParser

# Initialize planner
planner = TripPlannerGraph()

# Plan a trip
user_input = {
    "origin": "New York",
    "destination": "Paris",
    "start_date": "2025-11-01",
    "end_date": "2025-11-05",
    "duration": 5,
    "budget": 3000.0,
    "travel_type": "sightseeing",
    "adults": 2
}

# Execute planning
result = planner.plan_trip(user_input)

# Display results
final_plan = result.get("final_plan", {})
if final_plan.get("status") == "success":
    summary = ResponseParser.create_trip_summary(final_plan)
    print(summary)
else:
    print("Could not create plan. Alternatives:")
    for alt in final_plan.get("alternatives", []):
        print(f"- {alt}")
Run it:

bash
python test_planner.py
📋 Usage Guide
Step 1: Enter Trip Details
Fill in the form with:

Origin: Your departure city (e.g., "New York", "Mumbai")
Destination: Where you want to go (e.g., "Paris", "Tokyo")
Start Date: Trip start date
End Date: Trip end date
Budget: Total budget in USD
Travel Type: Choose from:
Sightseeing (landmarks, museums)
Adventure (outdoor activities)
Relaxation (beaches, spas)
Cultural (heritage sites)
Shopping (malls, markets)
Adults: Number of travelers
Step 2: Review Results
The system will:

✅ Check weather conditions
✈️ Search for flights
🏨 Find hotels
💰 Filter by budget
🎯 Recommend attractions
📅 Generate daily itinerary
Step 3: Explore Your Plan
View detailed information:

Weather forecast with recommendations
Flight options (departure, arrival, duration, price)
Hotel details (name, rating, room type, price)
Budget breakdown (spent vs. remaining)
Day-by-day itinerary with timings
AI-generated tips for each day
Step 4: Chat with Assistant
Use the chat tab to:

Ask questions about your itinerary
Request modifications
Get travel tips
Clarify doubts
🔧 Configuration
Adjust LLM Settings
Edit src/config/settings.py:

python
class Settings(BaseSettings):
    # LLM Settings
    temperature: float = 0.7  # Creativity (0.0-1.0)
    max_tokens: int = 2000    # Response length
Enable LangSmith Monitoring
In your .env:

env
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=your_key_here
LANGCHAIN_PROJECT=trip-planner-agent
View traces at: https://smith.langchain.com/

🎨 Customization
Add More Cities
Edit src/utils/helpers.py to add airport codes:

python
city_codes = {
    "your_city": "ABC",  # Add your city
    # ... existing cities
}
Add More Attractions
Edit src/tools/attractions_tool.py:

python
ATTRACTIONS_DB = {
    "your_city": [
        {"name": "Attraction", "type": "landmark", "duration": 2, "rating": 4.5},
        # Add more attractions
    ]
}
Modify Budget Allocation
Edit src/agents/trip_planner_graph.py:

python
# Current allocation:
# - 60% for flights (round trip)
# - 30% for hotels (per night)
# - 10% for activities (remaining)

# Adjust in search_flights_node:
max_price=state["budget"] * 0.6  # Change percentage

# Adjust in search_hotels_node:
max_price=state["budget"] * 0.3  # Change percentage
📊 LangGraph Workflow
mermaid
graph TD
    A[Start] --> B[Check Weather]
    B -->|Favorable| C[Search Flights]
    B -->|Unfavorable| H[Find Alternatives]
    C --> D[Search Hotels]
    D --> E[Filter by Budget]
    E -->|Within Budget| F[Get Attractions]
    E -->|Over Budget| H
    F --> G[Generate Itinerary]
    G --> I[Finalize Plan]
    H --> I
    I --> J[End]
🐛 Troubleshooting
Issue: API Authentication Error
Solution: Check your API keys in .env:

Ensure no extra spaces
Keys should be valid and active
For Amadeus, verify both API Key and Secret
Issue: No Flights/Hotels Found
Possible Causes:

Invalid city codes (use major cities)
Dates too far in future
Budget too low
API rate limits reached
Solution:

Try major cities (NYC, LON, PAR, TYO)
Use dates within 11 months
Increase budget
Wait if rate limited
Issue: Import Errors
Solution:

bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Or upgrade packages
pip install --upgrade langchain langgraph streamlit
Issue: Streamlit Not Found
Solution:

bash
# Ensure virtual environment is activated
# Then install streamlit
pip install streamlit
📝 Project Structure Explanation
src/
├── agents/              # LangGraph workflow
│   └── trip_planner_graph.py  # Main agent logic
├── tools/               # External API integrations
│   ├── weather_tool.py        # OpenWeather API
│   ├── amadeus_tool.py        # Amadeus API
│   └── attractions_tool.py    # Attractions database
├── utils/               # Helper functions
│   ├── helpers.py             # Date, budget, formatting
│   └── parsers.py             # Response parsing
└── config/              # Configuration
    └── settings.py            # Environment settings
🚀 Advanced Features
1. Add Multi-City Trips
Extend the workflow to support multiple destinations:

python
# In trip_planner_graph.py
destinations = ["Paris", "Amsterdam", "Berlin"]
for dest in destinations:
    # Plan each leg
2. Add Real-Time Updates
Use Streamlit's auto-refresh:

python
# In app.py
import time

if st.button("Refresh Prices"):
    with st.spinner("Updating..."):
        # Re-fetch data
        time.sleep(2)
        st.rerun()
3. Export to PDF
Add PDF export:

bash
pip install reportlab
python
from reportlab.pdfgen import canvas

def create_pdf(trip_data):
    # Generate PDF from trip data
    pass
📚 Learning Resources
LangChain Docs: https://docs.langchain.com/
LangGraph Tutorial: https://langchain-ai.github.io/langgraph/
Amadeus API Docs: https://developers.amadeus.com/self-service
OpenWeather API Docs: https://openweathermap.org/api
Streamlit Docs: https://docs.streamlit.io/
🤝 Contributing
Feel free to:

Add more API integrations
Improve the UI
Add new features
Fix bugs
Enhance documentation
📄 License
MIT License - Feel free to use and modify!

🙏 Acknowledgments
LangChain for the orchestration framework
Google for Gemini API
Amadeus for travel data
OpenWeatherMap for weather data
Streamlit for the UI framework
💡 Tips for Best Results
Use Major Cities: Better API coverage for NYC, LON, PAR, etc.
Reasonable Budgets: $1500+ for international trips
Plan Ahead: Book 2-4 weeks in advance
Check Weather: Use recommendations seriously
Be Flexible: Consider alternative suggestions
📧 Support
For issues or questions:

Check the Troubleshooting section
Review API documentation
Ensure all dependencies are installed
Verify API keys are correct
Built with ❤️ using AI and modern travel APIs

