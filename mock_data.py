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
    
    platforms = ['YouTube', 'Twitter', 'TikTok', 'Reddit', 'Instagram']
    
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
        
        insight = engine.process_text(
            text, 
            timestamp=timestamp,
            platform=random.choice(platforms),
            search_query=brand_pattern
        )
        insight.location = location['name']
        insight.latitude = location['lat']
        insight.longitude = location['lon']
        
        # Add weather data
        insight.weather_condition = random.choice(["Clear", "Cloudy", "Rainy", "Sunny"])
        insight.weather_temperature = random.uniform(18, 30)
        
        insights.append(insight)
    
    return insights


def generate_search_data(brand: str, num_records: int = 20) -> List[SocialInsight]:
    """Generate mock data for a specific brand search"""
    engine = UgandanNLPEngine()
    
    locations = [
        {'name': 'Kampala', 'lat': 0.3476, 'lon': 32.5825},
        {'name': 'Jinja', 'lat': 0.4479, 'lon': 33.2028},
        {'name': 'Gulu', 'lat': 2.7724, 'lon': 32.2881}
    ]
    
    templates = {
        'MTN': [
            "MTN network is fast in {location} today",
            "MTN customer service is terrible in {location}",
            "MTN data bundles are affordable in {location}"
        ],
        'Airtel': [
            "Airtel has great coverage in {location}",
            "Airtel is expensive in {location}",
            "Airtel network is slow in {location}"
        ],
        'Jumia': [
            "Jumia delivered fast in {location}",
            "Jumia products are fake in {location}",
            "Jumia is reliable in {location}"
        ],
        'SafeBoda': [
            "SafeBoda riders are safe in {location}",
            "SafeBoda is expensive in {location}",
            "SafeBoda is convenient in {location}"
        ],
        'Yango': [
            "Yango cars are clean in {location}",
            "Yango is expensive in {location}",
            "Yango drivers are professional in {location}"
        ]
    }
    
    patterns = templates.get(brand, templates['MTN'])
    platforms = ['YouTube', 'Twitter', 'TikTok']
    
    insights = []
    
    for i in range(num_records):
        location = random.choice(locations)
        text = random.choice(patterns).format(location=location['name'])
        
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, 360))
        
        insight = engine.process_text(
            text,
            timestamp=timestamp,
            platform=random.choice(platforms),
            search_query=brand
        )
        insight.location = location['name']
        insight.latitude = location['lat']
        insight.longitude = location['lon']
        insight.brand = brand
        
        insights.append(insight)
    
    return insights
