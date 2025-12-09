# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "travelbuddy")
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "ooDr6lftY3myoAY1pumqxFVxs6m3pXwsBVOrquaKdgRbf4IQ1K1VpHO0")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",") if origin.strip()]
    JWT_EXPIRY = 7 * 24 * 60 * 60  # 7 days in seconds

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}

