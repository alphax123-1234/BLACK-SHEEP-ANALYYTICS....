"""
🐑 BLACK SHEEP - Main Dashboard with Uganda Map
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_folium import st_folium

from database import DatabaseController
from nlp_engine import UgandanNLPEngine
from mock_data import generate_mock_data, generate_search_data
from map_visualization import UgandaMapVisualizer
from weather_api import WeatherService

# Configure page
st.set_page_config(
    page_title="🐑 BLACK SHEEP - Uganda Map Insights",
    page_icon="🐑",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .mood-happy { color: #2ecc71; }
    .mood-excited { color: #f1c40f; }
    .mood-neutral { color: #95a5a6; }
    .mood-frustrated { color: #e67e22; }
    .mood-angry { color: #e74c3c; }
    .mood-sad { color: #3498db; }
    .weather-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #0f3460;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def initialize_engine():
    return UgandanNLPEngine()

@st.cache_resource
def initialize_database():
    db = DatabaseController()
    try:
        db.connect()
        db.create_table()
    except Exception as e:
        st.warning(f"⚠️ Could not connect to cloud database: {str(e)}")
        st.info("💡 Using local CSV fallback instead.")
    return db

@st.cache_resource
def initialize_weather():
    return WeatherService()

@st.cache_resource
def initialize_map():
    return UgandaMapVisualizer()

def load_demo_data():
    """Load geospatial demo data"""
    with st.spinner("🐑 Loading demo data..."):
        db = initialize_database()
        insights = generate_mock_data(100)
        result = db.save_insights(insights)
        st.success(f"🐑 Loaded {len(insights)} records with location data!")

def search_brand(brand: str):
    """Search for a specific brand and generate data"""
    with st.spinner(f"🔍 Searching for {brand}..."):
        db = initialize_database()
        insights = generate_search_data(brand, 20)
        result = db.save_insights(insights)
        st.success(f"🐑 Found {len(insights)} mentions of {brand}!")

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1 style="margin: 0; font-size: 2.5rem;">🐑 BLACK SHEEP</h1>
                <p style="margin: 0; opacity: 0.8;">Uganda Social Listening & Sentiment Map</p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 0.9rem;">Live Mapping</p>
                <p style="margin: 0; font-size: 0.8rem; opacity: 0.7;">📍 Uganda</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="font-size: 3rem; margin: 0;">🐑</h1>
            <h2 style="margin: 0; color: #0f3460;">BLACK SHEEP</h2>
            <p style="font-style: italic; color: #666;">Uganda Social Listening</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # SEARCH BRAND
        st.subheader("🔍 Search Brand")
        search_query = st.text_input("Enter brand name", placeholder="e.g., MTN Uganda")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Search", use_container_width=True) and search_query:
                search_brand(search_query)
        with col2:
            if st.button("📱 Demo", use_container_width=True):
                load_demo_data()
        
        st.divider()
        
        # FILTERS
        st.subheader("🎯 Filters")
        
        brand_filter = st.selectbox(
            "Brand",
            ["All", "MTN", "Airtel", "Jumia", "SafeBoda", "Yango"]
        )
        
        mood_filter = st.selectbox(
            "Mood",
            ["All", "Happy", "Excited", "Neutral", "Frustrated", "Angry", "Sad"]
        )
        
        platform_filter = st.selectbox(
            "Platform",
            ["All", "YouTube", "Twitter", "TikTok", "Reddit", "Instagram"]
        )
        
        days_back = st.slider("Days to display", 1, 30, 7)
        
        show_weather = st.checkbox("🌤️ Show Weather Data", value=True)
        
        st.divider()
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        st.caption("🐑 v2.0.0 | Made in Uganda 🇺🇬")
    
    # Initialize components
    db = initialize_database()
    map_visualizer = initialize_map()
    
    # Load data
    df = db.query_insights(
        brand=brand_filter if brand_filter != "All" else None,
        platform=platform_filter if platform_filter != "All" else None,
        limit=1000
    )
    
    # Convert timestamp
    if not df.empty and 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff_date = datetime.now() - timedelta(days=days_back)
        df = df[df['timestamp'] >= cutoff_date]
    
    # Apply mood filter
    if mood_filter != "All" and not df.empty:
        df = df[df['mood'] == mood_filter]
    
    # Display metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📊 Total Insights", len(df))

with col2:
    if not df.empty:
        moods = df['mood'].value_counts()
        top_mood = moods.index[0] if len(moods) > 0 else "None"
        st.metric("😊 Top Mood", top_mood)
    else:
        st.metric("😊 Top Mood", "None")

with col3:
    if not df.empty:
        locations = df['location'].nunique()
        st.metric("📍 Active Locations", locations)
    else:
        st.metric("📍 Active Locations", 0)

with col4:
    if not df.empty:
        positive_rate = (len(df[df['sentiment'] == 'Positive']) / len(df)) * 100
        st.metric("✅ Positivity Rate", f"{positive_rate:.1f}%")
    else:
        st.metric("✅ Positivity Rate", "0%")

with col5:
    if not df.empty and 'platform' in df.columns:
        platforms = df['platform'].nunique()
        st.metric("📱 Platforms", platforms)
    else:
        st.metric("📱 Platforms", 0)
