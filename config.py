
#🐑 BLACK SHEEP - Configuration Management

import os
import logging
from typing import Dict, Any
from pathlib import Path

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - 🐑 %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """
    BLACK SHEEP configuration class
    """
    
    # Database configuration - uses Neon.tech free tier
    DB_CONFIG: Dict[str, Any] = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'black_sheep_insights'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }
    
    # File paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    CSV_PATH = DATA_DIR / 'black_sheep_insights.csv'
    
    # Scraping configuration
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    ]
    
    SCRAPE_DELAY_MIN = 1.0
    SCRAPE_DELAY_MAX = 3.0
    
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_db_url(cls) -> str:
        return (
            f"postgresql://{cls.DB_CONFIG['user']}:{cls.DB_CONFIG['password']}"
            f"@{cls.DB_CONFIG['host']}:{cls.DB_CONFIG['port']}/{cls.DB_CONFIG['database']}"
        )
    
    @classmethod
    def is_production(cls) -> bool:
        return os.getenv('ENVIRONMENT', 'development') == 'production'
    
    @classmethod
    def validate_config(cls) -> bool:
        if cls.DB_CONFIG['host'] == 'localhost':
            logger.warning("🐑 Using local database configuration")
            return True
        
        required = ['host', 'port', 'database', 'user', 'password']
        missing = [key for key in required if not cls.DB_CONFIG.get(key)]
        
        if missing:
            logger.error(f"🐑 Missing database configuration: {', '.join(missing)}")
            return False
        
        return True
