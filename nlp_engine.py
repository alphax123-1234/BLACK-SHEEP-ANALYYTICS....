"""
🐑 BLACK SHEEP - Advanced NLP Engine with Mood Detection
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import random

logger = logging.getLogger(__name__)

@dataclass
class SocialInsight:
    """
    🐑 BLACK SHEEP Data Structure with Mood and Location
    """
    brand: str
    sentiment: str
    mood: str
    core_issue: str
    timestamp: datetime
    anonymized_text: str
    category: str
    location: str
    latitude: float
    longitude: float
    weather_condition: str = ""
    weather_temperature: float = 0.0
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class UgandanNLPEngine:
    """
    🐑 BLACK SHEEP NLP Engine with Mood Detection
    """
    
    def __init__(self):
        # Brand patterns
        self.brand_patterns = {
            'MTN': r'\b(MTN|mtn|Mtn)\b',
            'Airtel': r'\b(Airtel|airtel|AIRTEL)\b',
            'Jumia': r'\b(Jumia|jumia|JUMIA)\b',
            'SafeBoda': r'\b(SafeBoda|safe boda|safeboda|Safe Boda)\b',
            'Yango': r'\b(Yango|yango|YANGO)\b'
        }
        
        # Mood mappings
        self.mood_mappings = {
            'Angry': {
                'keywords': ['furious', 'rage', 'angry', 'mad', 'frustrated', 'banyanze', 
                           'trash', 'scam', 'robbed', 'stole', 'terrible', 'horrible'],
                'weight': -0.9
            },
            'Frustrated': {
                'keywords': ['slow', 'problem', 'issues', 'bad', 'poor', 'depleting', 
                           'etunfuze', 'ya mazzi', 'atunfuze'],
                'weight': -0.6
            },
            'Neutral': {
                'keywords': ['ok', 'fine', 'alright', 'normal', 'average', 'neutral'],
                'weight': 0.0
            },
            'Happy': {
                'keywords': ['happy', 'great', 'good', 'nice', 'wonderful', 'mazima', 
                           'kiwedde', 'chilled', 'chilling'],
                'weight': 0.7
            },
            'Excited': {
                'keywords': ['excited', 'amazing', 'excellent', 'fantastic', 'love', 
                           'saved me', 'network ekyaka', 'best'],
                'weight': 0.9
            },
            'Sad': {
                'keywords': ['sad', 'disappointed', 'depressed', 'upset', 'disappointing',
                           'lost', 'wasted', 'broken'],
                'weight': -0.7
            }
        }
        
        # Location dictionary for Ugandan districts
        self.uganda_locations = {
            'kampala': {'lat': 0.3476, 'lon': 32.5825, 'district': 'Kampala'},
            'entebbe': {'lat': 0.0512, 'lon': 32.4637, 'district': 'Wakiso'},
            'jinja': {'lat': 0.4479, 'lon': 33.2028, 'district': 'Jinja'},
            'mbale': {'lat': 1.0776, 'lon': 34.1810, 'district': 'Mbale'},
            'gulu': {'lat': 2.7724, 'lon': 32.2881, 'district': 'Gulu'},
            'mbarara': {'lat': -0.6072, 'lon': 30.6542, 'district': 'Mbarara'},
            'fort portal': {'lat': 0.7120, 'lon': 30.2750, 'district': 'Kabarole'},
            'arua': {'lat': 3.0211, 'lon': 30.9133, 'district': 'Arua'},
            'masaka': {'lat': -0.3326, 'lon': 31.7353, 'district': 'Masaka'},
            'mukono': {'lat': 0.3536, 'lon': 32.7391, 'district': 'Mukono'}
        }
        
        # Compile patterns
        self.compiled_patterns = {
            brand: re.compile(pattern, re.IGNORECASE)
            for brand, pattern in self.brand_patterns.items()
        }
        
        self.issue_patterns = {
            'network': r'\b(network|signal|coverage|connection|data|internet|kyaka)\b',
            'service': r'\b(service|customer|support|help|staff|care)\b',
            'payment': r'\b(payment|money|cash|withdraw|deposit|transfer|balance)\b',
            'delivery': r'\b(delivery|shipping|package|deliver|receive|arrive)\b',
            'quality': r'\b(quality|cheap|defect|damage|fake|counterfeit|durable)\b',
            'price': r'\b(price|cost|expensive|affordable|cheap|rate)\b'
        }
        
        logger.info("🐑 BLACK SHEEP Enhanced NLP Engine initialized")
    
    def detect_mood(self, text: str) -> Tuple[str, float]:
        """Detect mood/emotion from text"""
        text_lower = text.lower()
        mood_scores = {}
        
        for mood, data in self.mood_mappings.items():
            score = 0.0
            for keyword in data['keywords']:
                if keyword in text_lower:
                    score += data['weight']
            mood_scores[mood] = score
        
        if all(score == 0 for score in mood_scores.values()):
            return "Neutral", 0.0
        
        best_mood = max(mood_scores, key=mood_scores.get)
        confidence = abs(mood_scores[best_mood])
        confidence = min(1.0, confidence / 2)
        
        return best_mood, confidence
    
    def extract_location(self, text: str) -> Tuple[str, float, float]:
        """Extract location from text"""
        text_lower = text.lower()
        
        for location, data in self.uganda_locations.items():
            if location in text_lower:
                return data['district'], data['lat'], data['lon']
        
        return "Kampala", 0.3476, 32.5825
    
    def calculate_sentiment(self, text: str) -> Tuple[str, float]:
        """Calculate sentiment with mood context"""
        mood, confidence = self.detect_mood(text)
        
        if mood in ['Happy', 'Excited']:
            return "Positive", max(0.5, confidence)
        elif mood in ['Angry', 'Sad', 'Frustrated']:
            return "Negative", max(0.5, confidence)
        else:
            return "Neutral", confidence
    
    def extract_brand(self, text: str) -> str:
        """Extract brand mentions"""
        text_lower = text.lower()
        for brand, pattern in self.compiled_patterns.items():
            if pattern.search(text_lower):
                return brand
        return "Unspecified"
    
    def extract_core_issue(self, text: str) -> str:
        """Extract core issue"""
        text_lower = text.lower()
        for issue, pattern in self.issue_patterns.items():
            if re.search(pattern, text_lower):
                return issue
        return "general"
    
    def categorize_content(self, text: str) -> str:
        """Categorize content"""
        categories = {
            'network_quality': ['network', 'slow', 'fast', 'connection', 'kyaka'],
            'customer_service': ['service', 'support', 'staff', 'care'],
            'pricing': ['expensive', 'affordable', 'cost', 'price'],
            'delivery': ['delivery', 'package', 'shipping'],
            'product_quality': ['quality', 'good', 'bad', 'product'],
            'trust': ['scam', 'legit', 'fake', 'robbed']
        }
        
        text_lower = text.lower()
        max_matches = 0
        best_category = 'general'
        
        for category, keywords in categories.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        return best_category
    
    def anonymize_text(self, text: str) -> str:
        """Anonymize PII"""
        text = re.sub(r'@\w+', '[USER]', text)
        text = re.sub(r'\b(0[7-9][0-9]{8})\b', '[PHONE]', text)
        text = re.sub(r'\b(\+256[0-9]{9})\b', '[PHONE]', text)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        return text
    
    def process_text(self, text: str, timestamp: Optional[datetime] = None) -> SocialInsight:
        """Full pipeline: process raw text into structured SocialInsight"""
        if timestamp is None:
            timestamp = datetime.now()
        
        brand = self.extract_brand(text)
        mood, mood_confidence = self.detect_mood(text)
        sentiment, sentiment_confidence = self.calculate_sentiment(text)
        core_issue = self.extract_core_issue(text)
        category = self.categorize_content(text)
        district, lat, lon = self.extract_location(text)
        anonymized = self.anonymize_text(text)
        
        return SocialInsight(
            brand=brand,
            sentiment=sentiment,
            mood=mood,
            core_issue=core_issue,
            timestamp=timestamp,
            anonymized_text=anonymized,
            category=category,
            location=district,
            latitude=lat,
            longitude=lon,
            weather_condition="",
            weather_temperature=0.0
        )
