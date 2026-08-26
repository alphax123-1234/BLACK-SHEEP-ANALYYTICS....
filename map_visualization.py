"""
🐑 BLACK SHEEP - Uganda Map Visualization
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium


class UgandaMapVisualizer:
    """
    Interactive map visualization for Uganda sentiment data
    """
    
    def __init__(self):
        self.uganda_center = [1.3733, 32.2903]
        
        # Uganda bounds (limits where you can pan)
        self.uganda_bounds = [
            [-5.0, 27.0],   # Southwest
            [5.0, 36.0]     # Northeast
        ]
        
        self.mood_colors = {
            'Happy': '#2ecc71',
            'Excited': '#f1c40f',
            'Neutral': '#95a5a6',
            'Frustrated': '#e67e22',
            'Angry': '#e74c3c',
            'Sad': '#3498db'
        }
        
        self.sentiment_colors = {
            'Positive': '#2ecc71',
            'Neutral': '#95a5a6',
            'Negative': '#e74c3c'
        }
    
    def create_folium_map(self, df: pd.DataFrame) -> folium.Map:
        """Create interactive Folium map with sentiment markers - LOCKED ON UGANDA"""
        
        # Create base map - LOCKED on Uganda
        m = folium.Map(
            location=self.uganda_center,
            zoom_start=7,
            tiles='OpenStreetMap',
            min_zoom=5,
            max_zoom=12,
            max_bounds=True,
            zoom_control=True,
            scrollWheelZoom=True
        )
        
        # Lock map to Uganda region
        m.fit_bounds(self.uganda_bounds)
        
        if df.empty:
            folium.Marker(
                self.uganda_center,
                popup="🐑 BLACK SHEEP\nLoading data...",
                icon=folium.Icon(color='gray', icon='info-sign')
            ).add_to(m)
            return m
        
        # Group by location for aggregated markers
        location_groups = df.groupby(['location', 'latitude', 'longitude']).agg({
            'mood': lambda x: x.mode()[0] if len(x) > 0 else 'Neutral',
            'sentiment': lambda x: x.mode()[0] if len(x) > 0 else 'Neutral',
            'brand': lambda x: ', '.join(x.unique()),
            'anonymized_text': lambda x: '; '.join(x.head(5).tolist())
        }).reset_index()
        
        # Add markers for each location
        for _, row in location_groups.iterrows():
            mood = row['mood']
            color = self.mood_colors.get(mood, '#95a5a6')
            
            popup_text = f"""
            <div style='font-family: Arial; width: 200px;'>
                <h4>📍 {row['location']}</h4>
                <p><b>Mood:</b> {mood}</p>
                <p><b>Sentiment:</b> {row['sentiment']}</p>
                <p><b>Brands:</b> {row['brand']}</p>
                <p><b>Recent comments:</b><br>{row['anonymized_text'][:100]}...</p>
            </div>
            """
            
            folium.Marker(
                [row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=self._get_folium_color(color), icon='info-sign')
            ).add_to(m)
        
        return m
    
    def _get_folium_color(self, hex_color: str) -> str:
        """Convert hex to Folium color name"""
        color_map = {
            '#2ecc71': 'green',
            '#f1c40f': 'yellow',
            '#95a5a6': 'gray',
            '#e67e22': 'orange',
            '#e74c3c': 'red',
            '#3498db': 'blue'
        }
        return color_map.get(hex_color, 'gray')
    
    def create_plotly_map(self, df: pd.DataFrame) -> go.Figure:
        """Create Plotly map - LOCKED on Uganda"""
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="🐑 BLACK SHEEP\nNo data available\nClick 'Load Demo Data'",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20, color='#0f3460')
            )
            fig.update_layout(
                geo=dict(
                    scope='africa',
                    center=dict(lon=32.2903, lat=1.3733),
                    projection_type='mercator',
                    projection_scale=5,
                    showland=True,
                    landcolor='lightgray',
                    showocean=True,
                    oceancolor='lightblue',
                    showcountries=True,
                    countrycolor='darkgray'
                ),
                height=600
            )
            return fig
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{'type': 'scattergeo', 'rowspan': 2}, {'type': 'bar'}],
                [None, {'type': 'bar'}]
            ],
            subplot_titles=('Sentiment Map of Uganda', 'Mood Distribution', 'Brand Sentiment')
        )
        
        mood_colors = df['mood'].map(self.mood_colors)
        
        fig.add_trace(
            go.Scattergeo(
                lon=df['longitude'],
                lat=df['latitude'],
                text=df['location'] + '<br>' + df['brand'] + '<br>' + df['mood'],
                mode='markers',
                marker=dict(
                    size=15,
                    color=mood_colors,
                    line=dict(width=2, color='white'),
                    symbol='circle'
                ),
                hoverinfo='text',
                hovertext=df['anonymized_text'],
                name='Sentiment Points'
            ),
            row=1, col=1
        )
        
        mood_counts = df['mood'].value_counts()
        fig.add_trace(
            go.Bar(
                x=mood_counts.index,
                y=mood_counts.values,
                marker_color=[self.mood_colors.get(m, '#95a5a6') for m in mood_counts.index],
                name='Mood Distribution'
            ),
            row=1, col=2
        )
        
        brand_sentiment = df.groupby(['brand', 'sentiment']).size().unstack(fill_value=0)
        for sentiment in brand_sentiment.columns:
            fig.add_trace(
                go.Bar(
                    name=sentiment,
                    x=brand_sentiment.index,
                    y=brand_sentiment[sentiment],
                    marker_color=self.sentiment_colors.get(sentiment, '#95a5a6')
                ),
                row=2, col=2
            )
        
        fig.update_geos(
            scope='africa',
            center=dict(lon=32.2903, lat=1.3733),
            projection_type='mercator',
            projection_scale=5,
            showland=True,
            landcolor='lightgray',
            showocean=True,
            oceancolor='lightblue',
            showcountries=True,
            countrycolor='darkgray'
        )
        
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="🐑 BLACK SHEEP - Uganda Sentiment & Mood Map",
            hovermode='closest'
        )
        
        return fig
