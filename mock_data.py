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
