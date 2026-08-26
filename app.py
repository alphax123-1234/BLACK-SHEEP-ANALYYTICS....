"""
🐑 BLACK SHEEP - Main Dashboard with Uganda Map
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_folium import st_folium  # ← FIX 1: ADD THIS IMPORT!

from database import DatabaseController
from nlp_engine import UgandanNLPEngine
from mock_data import generate_mock_data
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
    """Initialize database with graceful fallback"""
    db = DatabaseController()
    try:
        db.connect()
        db.create_table()
        st.sidebar.success("✅ Connected to cloud database")
    except Exception as e:
        st.sidebar.warning("⚠️ Using local CSV fallback")
        st.sidebar.info("💡 Add DATABASE_URL secret to use cloud storage")
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
        
        brand_filter = st.selectbox(
            "Select Brand",
            ["All", "MTN", "Airtel", "Jumia", "SafeBoda", "Yango"]
        )
        
        mood_filter = st.selectbox(
            "Mood Filter",
            ["All", "Happy", "Excited", "Neutral", "Frustrated", "Angry", "Sad"]
        )
        
        days_back = st.slider("Days to display", 1, 30, 7)
        
        show_weather = st.checkbox("🌤️ Show Weather Data", value=True)
        
        st.divider()
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("🐑 Load Demo Data", use_container_width=True):
            load_demo_data()
        
        st.divider()
        st.caption("🐑 v2.0.0 | Made in Uganda 🇺🇬")
    
    # Initialize components
    db = initialize_database()
    map_visualizer = initialize_map()
    
    # Load data
    df = db.query_insights(
        brand=brand_filter if brand_filter != "All" else None,
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
    col1, col2, col3, col4 = st.columns(4)
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
    
    if not df.empty:
        # Two-column layout for maps
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🗺️ Interactive Uganda Map")
            st.caption("Hover over markers for details, colors represent moods")
            
            folium_map = map_visualizer.create_folium_map(df)
            st_folium(folium_map, width=700, height=500)  # ← NOW WORKS!
        
        with col2:
            st.subheader("📊 Mood Distribution")
            
            mood_counts = df['mood'].value_counts()
            fig = px.pie(
                values=mood_counts.values,
                names=mood_counts.index,
                color=mood_counts.index,
                color_discrete_map=UgandaMapVisualizer().mood_colors,
                hole=0.3
            )
            fig.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📈 Sentiment by Brand")
            brand_sentiment = df.groupby(['brand', 'sentiment']).size().unstack(fill_value=0)
            fig = px.bar(
                brand_sentiment,
                barmode='group',
                color_discrete_map={
                    'Positive': '#2ecc71',
                    'Neutral': '#95a5a6',
                    'Negative': '#e74c3c'
                }
            )
            fig.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        
        # Advanced map with Plotly
        st.subheader("🗺️ Advanced Sentiment Map")
        plotly_map = map_visualizer.create_plotly_map(df)
        st.plotly_chart(plotly_map, use_container_width=True)
        
        # Recent insights
        st.subheader("📝 Recent Insights by Location")
        display_df = df[['timestamp', 'location', 'brand', 'mood', 'sentiment', 'anonymized_text']].head(10)
        display_df.columns = ['Time', 'Location', 'Brand', 'Mood', 'Sentiment', 'Text']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Location summary
        with st.expander("📊 Location Summary"):
            location_summary = df.groupby('location').agg({
                'mood': lambda x: x.mode()[0] if len(x) > 0 else 'Neutral',
                'sentiment': lambda x: (x == 'Positive').mean() * 100,
                'brand': 'nunique'
            }).round(2)
            location_summary.columns = ['Dominant Mood', 'Positive Rate %', 'Unique Brands']
            st.dataframe(location_summary, use_container_width=True)
    
    else:
        st.warning("""
        🐑 No data available! 
        
        Click **'Load Demo Data'** in the sidebar to start with geospatial data.
        This will generate realistic data with locations across Uganda.
        """)

if __name__ == "__main__":
    main()
