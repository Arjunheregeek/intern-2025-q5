"""Application settings and configuration."""

import os
from pathlib import Path
from typing import Optional

class Settings:
    """Application configuration settings."""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    SRC_DIR = PROJECT_ROOT / "src"
    LOGS_DIR = PROJECT_ROOT / "logs"
    TESTS_DIR = PROJECT_ROOT / "tests"
    
    # API Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL: str = "gemini-1.5-flash"
    API_TIMEOUT: int = 30
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = str(LOGS_DIR / "tweet_generator.log")
    
    # Tweet Generation Defaults
    DEFAULT_MAX_RETRIES: int = 3
    DEFAULT_MAX_WORDS: int = 25
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories."""
        cls.LOGS_DIR.mkdir(exist_ok=True)

settings = Settings()
