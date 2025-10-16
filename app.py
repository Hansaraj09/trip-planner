import streamlit as st
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.trip_planner_graph import TripPlannerGraph
from src.utils.parsers import ResponseParser
from src.utils.helpers import format_currency, calculate_days_between

# Page config
st.set_page_config(
    page_title="Intelligent Trip Planner",
    page_icon="🌍",
    layout="wide"
)

# Initialize session state
if 'trip_planner' not in st.session_state:
    st.session_state.trip_planner = TripPlannerGraph()
if 'trip_result' not in st.session_state:
    st.session_state.trip_result = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #64748B;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #3B82F6;
        color: white;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        background-color: #D1FAE5;
        border-left: 4px solid #10B981;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #DBEAFE;
        border-left: 4px solid #3B82F6;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🌍 Intelligent Trip Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Travel Planning with LangChain & LangGraph</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/airplane-take-off.png", width=150)
    st.markdown("### About")
    st.info("""
    This intelligent trip planner uses:
    - 🤖 Google Gemini for AI planning
    - 🌤️ OpenWeather API for weather
    - ✈️ Amadeus API for flights & hotels
    - 🔗 LangGraph for workflow
    - 📊 LangSmith for monitoring
    """)
    
    st.markdown("---")
    st.markdown("### Features")
    st.markdown("""
    ✅ Weather-based recommendations  
    ✅ Budget optimization  
    ✅ Smart itinerary generation  
    ✅ Alternative suggestions  
    ✅ Real-time flight & hotel search
    """)

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📝 Plan Trip", "📋 View Results", "💬 Chat Assistant"])

with tab1:
    st.markdown("## Enter Your Trip Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        origin = st.text_input(
            "🏠 From (Origin City)",
            placeholder="e.g., New York, Mumbai, London",
            help="Enter your departure city"
        )
        
        destination = st.text_input(
            "🎯 Destination",
            placeholder="e.g., Paris, Tokyo, Dubai",
            help="Where do you want to go?"
        )
        
        travel_type = st.selectbox(
            "🎨 Travel Type",
            ["Sightseeing", "Adventure", "Relaxation", "Cultural", "Shopping"],
            help="What kind of trip are you planning?"
        )
        
        budget = st.number_input(
            "💰 Budget (USD)",
            min_value=100.0,
            max_value=100000.0,
            value=2000.0,
            step=100.0,
            help="Total budget for flights and hotels"
        )
    
    with col2:
        start_date = st.date_input(
            "📅 Start Date",
            value=datetime.now() + timedelta(days=7),
            min_value=datetime.now(),
            help="When do you want to start your trip?"
        )
        
        end_date = st.date_input(
            "📅 End Date",
            value=datetime.now() + timedelta(days=10),
            min_value=datetime.now() + timedelta(days=1),
            help="When do you want to end your trip?"
        )
        
        adults = st.number_input(
            "👥 Number of Adults",
            min_value=1,
            max_value=9,
            value=1,
            help="How many people are traveling?"
        )
        
        # Calculate duration
        if start_date and end_date:
            duration = (end_date - start_date).days
            st.info(f"📊 Trip Duration: **{duration} days**")
    
    st.markdown("---")
    
    # Plan trip button
    if st.button("🚀 Plan My Trip", type="primary"):
        if not origin or not destination:
            st.error("⚠️ Please enter both origin and destination cities!")
        elif start_date >= end_date:
            st.error("⚠️ End date must be after start date!")
        elif duration < 1:
            st.error("⚠️ Trip must be at least 1 day!")
        else:
            # Prepare input
            user_input = {
                "origin": origin,
                "destination": destination,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "duration": duration,
                "budget": budget,
                "travel_type": travel_type.lower(),
                "adults": adults
            }
            
            # Show progress
            with st.spinner("🔄 Planning your perfect trip..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Simulate progress
                    status_text.text("Checking weather conditions...")
                    progress_bar.progress(20)
                    
                    status_text.text("Searching for flights...")
                    progress_bar.progress(40)
                    
                    status_text.text("Finding hotels...")
                    progress_bar.progress(60)
                    
                    status_text.text("Generating itinerary...")
                    progress_bar.progress(80)
                    
                    # Run the planner
                    result = st.session_state.trip_planner.plan_trip(user_input)
                    st.session_state.trip_result = result
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Trip planning completed!")
                    
                    st.success("🎉 Your trip has been planned successfully! Check the 'View Results' tab.")
                    st.balloons()
                    
                except Exception as e:
                    import traceback
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.error("Full error details:")
                    st.code(traceback.format_exc())

with tab2:
    st.markdown("## Your Trip Plan")
    
    if st.session_state.trip_result is None:
        st.info("👆 Please plan a trip first using the 'Plan Trip' tab!")
    else:
        result = st.session_state.trip_result
        final_plan = result.get("final_plan", {})
        
        if final_plan.get("status") == "success":
            # Success - Show complete plan
            st.markdown('<div class="success-box">✅ Trip Successfully Planned!</div>', unsafe_allow_html=True)
            
            # Overview
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎯 Destination", final_plan["destination"])
            with col2:
                st.metric("📅 Duration", f"{final_plan['dates']['duration']} days")
            with col3:
                weather_score = final_plan["weather"].get("overall_score", 0)
                st.metric("🌤️ Weather Score", f"{weather_score}/10")
            with col4:
                budget_data = final_plan["budget_breakdown"]
                st.metric("💰 Budget Used", f"{budget_data['percentage_spent']:.1f}%")
            
            st.markdown("---")
            
            # Weather Section
            with st.expander("🌤️ Weather Forecast", expanded=True):
                weather = final_plan.get("weather", {})
                st.markdown(f"**{weather.get('recommendation', 'Weather information unavailable')}**")
                
                if weather.get("forecasts"):
                    st.markdown("### Daily Forecast")
                    for forecast in weather.get("forecasts", [])[:5]:
                        col1, col2, col3 = st.columns([2, 2, 3])
                        with col1:
                            st.write(f"📅 {forecast.get('date', 'N/A')}")
                        with col2:
                            st.write(f"🌡️ {forecast.get('min_temp', 0)}°C - {forecast.get('max_temp', 0)}°C")
                        with col3:
                            st.write(f"☁️ {forecast.get('description', 'N/A').title()}")
            
            # Flight Section
            with st.expander("✈️ Flight Details", expanded=True):
                flight = final_plan["flight"]
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **Outbound Flight**
                    - 🛫 From: {flight['departure_airport']}
                    - 🛬 To: {flight['arrival_airport']}
                    - 🕐 Departure: {flight['departure_time']}
                    - 🕑 Arrival: {flight['arrival_time']}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **Flight Info**
                    - ⏱️ Duration: {flight['duration_hours']} hours
                    - 🔄 Stops: {flight['stops']}
                    - ✈️ Airline: {flight['airline']}
                    - 💵 Price: {flight['currency']} {flight['price']:.2f} (per person)
                    """)
                
                st.info(f"💰 Total Flight Cost (Round Trip): **{flight['currency']} {flight['price'] * 2:.2f}**")
            
            # Hotel Section
            with st.expander("🏨 Hotel Details", expanded=True):
                hotel = final_plan["hotel"]
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **{hotel['name']}**
                    - ⭐ Rating: {hotel['rating']}
                    - 🛏️ Room Type: {hotel['room_type']}
                    - 👥 Beds: {hotel['beds']}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **Booking Details**
                    - 📅 Check-in: {hotel['check_in']}
                    - 📅 Check-out: {hotel['check_out']}
                    - 💵 Per Night: {hotel['currency']} {hotel['price']:.2f}
                    """)
                
                total_hotel = hotel['price'] * final_plan['dates']['duration']
                st.info(f"💰 Total Hotel Cost: **{hotel['currency']} {total_hotel:.2f}**")
            
            # Budget Breakdown
            with st.expander("💰 Budget Breakdown", expanded=True):
                budget = final_plan["budget_breakdown"]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Budget", f"${budget['total_budget']:.2f}")
                with col2:
                    st.metric("Total Spent", f"${budget['total_spent']:.2f}")
                with col3:
                    st.metric("Remaining", f"${budget['remaining']:.2f}", 
                             delta=f"{budget['percentage_spent']:.1f}% used")
                
                # Progress bar
                st.progress(budget['percentage_spent'] / 100)
                
                if budget['within_budget']:
                    st.success("✅ Your trip is within budget!")
                else:
                    st.warning("⚠️ Budget exceeded!")
            
            # Itinerary
            with st.expander("📅 Daily Itinerary", expanded=True):
                for day_plan in final_plan["itinerary"]:
                    st.markdown(f"### Day {day_plan['day']}")
                    st.markdown(f"*Total Duration: {day_plan['total_duration']} hours*")
                    
                    for schedule in day_plan["schedule"]:
                        st.markdown(f"""
                        **{schedule['start_time']} - {schedule['end_time']}**: {schedule['attraction']}  
                        *Duration: {schedule['duration']}*
                        """)
                    
                    # Show LLM tips if available
                    if "llm_tips" in day_plan:
                        st.info(f"💡 **Tips**: {day_plan['llm_tips']}")
                    
                    st.markdown("---")
            
            # Download button
            if st.button("📥 Download Trip Plan"):
                trip_summary = ResponseParser.create_trip_summary(final_plan)
                st.download_button(
                    label="Download as Text File",
                    data=trip_summary,
                    file_name=f"trip_plan_{final_plan['destination']}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
        
        else:
            # Show alternatives
            st.markdown('<div class="warning-box">⚠️ Could not create a complete trip plan with current constraints</div>', unsafe_allow_html=True)
            
            st.markdown("### 🔄 Alternative Suggestions")
            
            alternatives = final_plan.get("alternatives", [])
            for i, alt in enumerate(alternatives, 1):
                with st.expander(f"Alternative {i}: {alt.get('type', 'Suggestion').replace('_', ' ').title()}", expanded=True):
                    if "reason" in alt:
                        st.warning(f"**Reason**: {alt['reason']}")
                    
                    if "suggestion" in alt:
                        st.info(alt["suggestion"])
                    
                    if "suggestions" in alt:
                        st.markdown("**Recommendations:**")
                        for suggestion in alt["suggestions"]:
                            st.markdown(f"- {suggestion}")
                    
                    if "content" in alt:
                        st.markdown(alt["content"])

with tab3:
    st.markdown("## 💬 Chat with Trip Assistant")
    st.info("Ask questions about your trip plan or request modifications!")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your trip..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    context = st.session_state.trip_result if st.session_state.trip_result else None
                    response = st.session_state.trip_planner.chat_with_user(prompt, context)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748B;'>
    <p>Built with ❤️ using LangChain, LangGraph, Google Gemini, OpenWeather & Amadeus APIs</p>
    <p>Powered by AI | Monitored with LangSmith</p>
</div>
""", unsafe_allow_html=True)