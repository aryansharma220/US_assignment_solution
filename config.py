"""
Configuration for ShopSmart AI - Intelligent E-commerce Platform
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Production-ready configuration"""
    
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{DATABASE_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 300
    
    # AI Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Server Configuration
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    
    # Application Limits
    MAX_RECOMMENDATIONS = 20
    MIN_INTERACTIONS_FOR_CF = 3
    API_RATE_LIMIT = "100 per hour"
    
    # CORS Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')


class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    HOST = '0.0.0.0'
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}
