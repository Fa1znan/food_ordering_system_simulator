import os
from datetime import timedelta

class Config:
    """Application configuration class"""
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'food_ordering.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Bcrypt configuration
    BCRYPT_LOG_ROUNDS = 12
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)