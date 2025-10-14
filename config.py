"""
Configuration file for the E-commerce Product Recommender application
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///ecommerce.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Recommendation Configuration
    MAX_RECOMMENDATIONS = 5
    MIN_INTERACTIONS_FOR_CF = 3  # Minimum interactions for collaborative filtering
    
    @staticmethod
    def validate():
        """Validate that all required configuration is present"""
        if not Config.GEMINI_API_KEY:
            print("WARNING: GEMINI_API_KEY is not set in .env file!")
            print("Please add your Gemini API key to the .env file")
            return False
        return True
