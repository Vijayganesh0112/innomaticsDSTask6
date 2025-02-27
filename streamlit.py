import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.retry import Retry
from datetime import datetime, timedelta

# Set environment variable for DNS resolution
os.environ["GRPC_DNS_RESOLVER"] = "native"

# Initialize the Streamlit application with Matrix Theme
st.set_page_config(page_title="AI Travel Planner", layout="centered")

st.markdown(
    """
    <style>
    body {
        background-color: black;
        color: #00FF00;
        font-family: 'Courier New', monospace;
    }
    * {
        color: #00FF00 !important;
    }
    .stTextInput>div>div>input {
        background-color: black !important;
        color: #00FF00 !important;
        border: 1px solid #00FF00 !important;
    }
    .stDateInput>div>div>input {
        background-color: black !important;
        color: #00FF00 !important;
        border: 1px solid #00FF00 !important;
    }
    .stSelectbox>div>div>select {
        background-color: black !important;
        color: #00FF00 !important;
        border: 1px solid #00FF00 !important;
    }
    .stSlider>div>div>div {
        background-color: black !important;
    }
    .stMultiSelect>div>div>div>div {
        background-color: black !important;
        color: #00FF00 !important;
        border: 1px solid #00FF00 !important;
    }
    .stButton>button {
        background-color: black !important;
        color: #00FF00 !important;
        border: 1px solid #00FF00 !important;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fetch API Key from Streamlit Secrets
api_key = st.secrets["api_keys"]["openai_key"]

# Initialize LLM if API key is available
llm = None
if api_key:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.7,
            retry=Retry(initial=1.0, maximum=60.0, multiplier=2.0, deadline=900.0)
        )
    except Exception as e:
        st.error(f"Invalid API Key or authentication error: {e}")

# Maintain session state for user inputs
if "start_location" not in st.session_state:
    st.session_state["start_location"] = ""
if "end_location" not in st.session_state:
    st.session_state["end_location"] = ""

def main():
    st.title("🟢 AI Powered Travel Assistance 🟢")
    st.markdown("### Enter your details to create a plan:")

    col1, col2, col3 = st.columns([3, 1, 3])

    with col1:
        st.session_state["start_location"] = st.text_input(
            "📍 Enter Starting Location", value=st.session_state["start_location"], key="start_input"
        )

    with col2:
        if st.button("🔄 Swap"):
            st.session_state["start_location"], st.session_state["end_location"] = (
                st.session_state["end_location"],
                st.session_state["start_location"],
            )
            st.rerun()

    with col3:
        st.session_state["end_location"] = st.text_input(
            "📍 Enter Destination Location", value=st.session_state["end_location"], key="end_input"
        )

    today = datetime.today().date()
    max_date = today + timedelta(days=365 * 10)  # 10 years limit
    departure_date = st.date_input("📅 Departure Date", today, min_value=today, max_value=max_date)
    return_date = st.date_input("📅 Return Date (Optional)", departure_date, min_value=departure_date, max_value=max_date)

    travel_mode = st.selectbox("Travel Mode:", ["All", "Train", "Bus", "Flight", "Car"], index=0)
    travel_preference = st.selectbox("Travel Preference:", ["Budget", "Fastest", "Most Comfortable"], index=0)
    sort_by = st.selectbox("Sort Results By:", ["Price", "Duration", "Departure Time"], index=0)
    language = st.selectbox("Language:", ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Marathi"], index=0)

    return st.session_state["start_location"], st.session_state["end_location"], travel_mode, travel_preference, sort_by, language

# Run the main function and get user inputs
start_location, end_location, travel_mode, travel_preference, sort_by, language = main()

# Generate travel recommendations
if st.button("Search Travel Options") and llm:
    if start_location and end_location:
        prompt = f"""
        Find and suggest the best travel options from {start_location} to {end_location} using {travel_mode}.

        Prioritize options based on {travel_preference} (e.g., fastest, cheapest, most comfortable).
        Sort the results by {sort_by} (e.g., price, duration, user ratings).
        Provide the response in {language}.
        Include estimated cost, duration, departure and arrival times, and available service providers.
        If multiple options exist, suggest at least three alternatives with key details.
        Mention any applicable discounts, offers, or special conditions if available.
        Highlight the best recommendation based on the given preference.
        """

        try:
            response = llm.invoke([{"role": "user", "content": prompt}])
            st.success("✈️ Travel Recommendations:")
            st.write(response.content)
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter both starting and destination locations.")
