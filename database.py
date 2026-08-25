"""
🐑 BLACK SHEEP - Database Controller with Dual-Storage
"""

import psycopg2
import pandas as pd
import logging
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from pathlib import Path

from config import Config
from nlp_engine import SocialInsight

logger = logging.getLogger(__name__)

# SQL CREATE TABLE query
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS black_sheep_insights (
    uuid UUID PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    brand VARCHAR(100) NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    mood VARCHAR(20) NOT NULL,
    core_issue VARCHAR(100),
    anonymized_text TEXT,
    category VARCHAR(50),
    location VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    weather_condition VARCHAR(50),
    weather_temperature FLOAT,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_black_sheep_brand ON black_sheep_insights(brand);
CREATE INDEX IF NOT EXISTS idx_black_sheep_timestamp ON black_sheep_insights(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_black_sheep_sentiment ON black_sheep_insights(sentiment);
CREATE INDEX IF NOT EXISTS idx_black_sheep_mood ON black_sheep_insights(mood);
CREATE INDEX IF NOT EXISTS idx_black_sheep_location ON black_sheep_insights(location);
CREATE INDEX IF NOT EXISTS idx_black_sheep_brand_sentiment ON black_sheep_insights(brand, sentiment);
CREATE INDEX IF NOT EXISTS idx_black_sheep_coordinates ON black_sheep_insights(latitude, longitude);
"""

class DatabaseController:
    """
    Handles database operations with automatic fallback to local CSV storage.
    """
    
    def __init__(self):
        self.db_url = Config.get_db_url()
        self.csv_path = Config.CSV_PATH
        self.connection = None
        self.is_connected = False
        self._initialize_csv_storage()
    
    def _initialize_csv_storage(self):
        """Create CSV file with headers if it doesn't exist"""
        if not self.csv_path.exists():
            df = pd.DataFrame(columns=[
                'uuid', 'timestamp', 'brand', 'sentiment', 'mood',
                'core_issue', 'anonymized_text', 'category', 'location',
                'latitude', 'longitude', 'weather_condition', 'weather_temperature'
            ])
            df.to_csv(self.csv_path, index=False)
            logger.info(f"Created CSV storage at {self.csv_path}")
    
    def connect(self) -> bool:
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(self.db_url)
            self.is_connected = True
            logger.info("Successfully connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to database: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.is_connected = False
            logger.info("Disconnected from database")
    
    def create_table(self) -> bool:
        """Create the insights table if it doesn't exist"""
        if not self.is_connected and not self.connect():
            logger.error("Cannot create table without database connection")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_TABLE_SQL)
                self.connection.commit()
                logger.info("Table 'black_sheep_insights' created successfully")
                return True
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            self.connection.rollback()
            return False
    
    def save_to_cloud(self, insights: List[SocialInsight]) -> int:
        """Save insights to PostgreSQL database"""
        if not insights:
            return 0
        
        if not self.is_connected and not self.connect():
            logger.error("Cannot save to cloud - no database connection")
            return 0
        
        insert_query = """
        INSERT INTO black_sheep_insights 
        (uuid, timestamp, brand, sentiment, mood, core_issue, 
         anonymized_text, category, location, latitude, longitude,
         weather_condition, weather_temperature)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        saved_count = 0
        try:
            with self.connection.cursor() as cursor:
                for insight in insights:
                    record_uuid = str(uuid.uuid4())
                    values = (
                        record_uuid,
                        insight.timestamp,
                        insight.brand,
                        insight.sentiment,
                        insight.mood,
                        insight.core_issue,
                        insight.anonymized_text,
                        insight.category,
                        insight.location,
                        insight.latitude,
                        insight.longitude,
                        insight.weather_condition,
                        insight.weather_temperature
                    )
                    cursor.execute(insert_query, values)
                    saved_count += 1
                
                self.connection.commit()
                logger.info(f"Successfully saved {saved_count} records to cloud")
                return saved_count
                
        except Exception as e:
            logger.error(f"Error saving to cloud: {e}")
            self.connection.rollback()
            return 0
    
    def save_to_local(self, insights: List[SocialInsight]) -> int:
        """Save insights to local CSV file"""
        if not insights:
            return 0
        
        try:
            data = []
            for insight in insights:
                data.append({
                    'uuid': str(uuid.uuid4()),
                    'timestamp': insight.timestamp,
                    'brand': insight.brand,
                    'sentiment': insight.sentiment,
                    'mood': insight.mood,
                    'core_issue': insight.core_issue,
                    'anonymized_text': insight.anonymized_text,
                    'category': insight.category,
                    'location': insight.location,
                    'latitude': insight.latitude,
                    'longitude': insight.longitude,
                    'weather_condition': insight.weather_condition,
                    'weather_temperature': insight.weather_temperature
                })
            
            df_new = pd.DataFrame(data)
            
            if self.csv_path.exists():
                df_existing = pd.read_csv(self.csv_path)
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                df_combined.to_csv(self.csv_path, index=False)
            else:
                df_new.to_csv(self.csv_path, index=False)
            
            logger.info(f"Successfully saved {len(data)} records to local CSV")
            return len(data)
            
        except Exception as e:
            logger.error(f"Error saving to local CSV: {e}")
            return 0
    
    def save_insights(self, insights: List[SocialInsight]) -> Dict[str, int]:
        """Primary save method with automatic fallback"""
        results = {'cloud_saved': 0, 'local_saved': 0}
        
        if not insights:
            return results
        
        cloud_saved = self.save_to_cloud(insights)
        results['cloud_saved'] = cloud_saved
        
        local_saved = self.save_to_local(insights)
        results['local_saved'] = local_saved
        
        if cloud_saved < len(insights):
            logger.warning(f"Only {cloud_saved}/{len(insights)} records saved to cloud")
        
        return results
    
    def query_insights(self, brand: Optional[str] = None, 
                       sentiment: Optional[str] = None,
                       limit: int = 100) -> pd.DataFrame:
        """Query insights from database or CSV fallback"""
        if self.is_connected or self.connect():
            try:
                query = "SELECT * FROM black_sheep_insights WHERE 1=1"
                params = []
                
                if brand:
                    query += " AND brand = %s"
                    params.append(brand)
                if sentiment:
                    query += " AND sentiment = %s"
                    params.append(sentiment)
                    
                query += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limit)
                
                df = pd.read_sql_query(query, self.connection, params=params)
                return df
                
            except Exception as e:
                logger.error(f"Error querying cloud: {e}")
        
        try:
            if self.csv_path.exists():
                df = pd.read_csv(self.csv_path)
                if brand:
                    df = df[df['brand'] == brand]
                if sentiment:
                    df = df[df['sentiment'] == sentiment]
                return df.head(limit)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return pd.DataFrame()
