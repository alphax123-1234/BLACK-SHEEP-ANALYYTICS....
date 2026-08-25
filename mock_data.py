"""
🐑 BLACK SHEEP - Geospatial Mock Data Generator
"""

import random
from datetime import datetime, timedelta
from typing import List
from nlp_engine import UgandanNLPEngine, SocialInsight

def generate_mock_data(num_records: int = 50) -> List[SocialInsight]:
    """Generate realistic geospatial mock data for Uganda"""
    engine = UgandanNLPEngine()
    
    locations = [
        {'name': 'Kampala', 'lat': 0.3476, 'lon': 32.5825},
        {'name': 'Entebbe', 'lat': 0.0512, 'lon': 32.4637},
        {'name': 'Jinja', 'lat': 0.4479, 'lon': 33.2028},
        {'name': 'Mbale', 'lat': 1.0776, 'lon': 34.1810},
        {'name': 'Gulu', 'lat': 2.7724, 'lon': 32.2881},
        {'name': 'Mbarara', 'lat': -0.6072, 'lon': 30.6542},
        {'name': 'Fort Portal', 'lat': 0.7120, 'lon': 30.2750},
        {'name': 'Arua', 'lat': 3.0211, 'lon': 30.9133},
        {'name': 'Masaka', 'lat': -0.3326, 'lon': 31.7353},
        {'name': 'Mukono', 'lat': 0.3536, 'lon': 32.7391}
    ]
    
    text_patterns = [
        ("MTN network ekyaka in Kampala! Kiwedde!", "Happy", "MTN"),
        ("Airtel mazima service in Entebbe, chilling", "Happy", "Airtel"),
        ("Jumia saved me in Jinja! Excellent delivery!", "Excited", "Jumia"),
        ("SafeBoda riders are amazing in Kampala", "Happy", "SafeBoda"),
        ("MTN is trash in Gulu, they stole my money", "Angry", "MTN"),
        ("Airtel network ya mazzi in Mbarara", "Frustrated", "Airtel"),
        ("Jumia scam in Mbale! Fake products!", "Angry", "Jumia"),
        ("Yango expensive in Kampala, they robbing us", "Frustrated", "Yango"),
        ("Airtel service is okay in Masaka", "Neutral", "Airtel"),
        ("MTN coverage average in Mukono", "Neutral", "MTN"),
        ("SafeBoda rides fine in Kampala", "Neutral", "SafeBoda"),
        ("MTN depleting my balance in Fort Portal", "Sad", "MTN"),
        ("Airtel bad customer service in Arua", "Sad", "Airtel"),
        ("Jumia disappointing delivery in Gulu", "Sad", "Jumia")
    ]
    
    insights = []
    
    for i in range(num_records):
        location = random.choice(locations)
        pattern = random.choice(text_patterns)
        text, mood_pattern, brand_pattern = pattern
        
        # Add location-specific context
        text = text.replace("Kampala", location['name'])
        
        timestamp = datetime.now() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23)
        )
        
        insight = engine.process_text(text, timestamp)
        insight.location = location['name']
        insight.latitude = location['lat']
        insight.longitude = location['lon']
        
        # Add weather data
        insight.weather_condition = random.choice(["Clear", "Cloudy", "Rainy", "Sunny"])
        insight.weather_temperature = random.uniform(18, 30)
        
        insights.append(insight)
    
    return insights
