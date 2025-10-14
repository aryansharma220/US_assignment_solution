"""
Application factory for E-commerce Product Recommender
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

# Initialize extensions
db = SQLAlchemy()


def create_app(config_class=Config):
    """
    Application factory pattern
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    CORS(app)
    
    # Validate configuration
    with app.app_context():
        Config.validate()
    
    # Register blueprints (will be added in later steps)
    # from app.routes import main_bp
    # app.register_blueprint(main_bp)
    
    return app
