import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"


class DevelopmentConfig(Config):
    """Development configuration - Local MySQL or SQLite"""
    DEBUG = True
    
    # Check if MySQL env vars are set, otherwise use SQLite
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_NAME = os.environ.get("DB_NAME")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    
    if DB_USER and DB_PASSWORD and DB_NAME:
        # Local MySQL
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        )
    else:
        # Fallback to SQLite for quick local dev
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///app.db'
    
    CORS_ORIGINS = "*"


class ProductionConfig(Config):
    """Production configuration - Cloud SQL MySQL"""
    DEBUG = False
    
    # Cloud SQL Configuration
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_NAME = os.environ.get("DB_NAME")
    DB_SOCKET = os.environ.get("DB_SOCKET")
    
    # Build connection string for Cloud SQL via Unix Socket
    if DB_USER and DB_PASSWORD and DB_NAME and DB_SOCKET:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@/"
            f"{DB_NAME}?unix_socket={DB_SOCKET}"
        )
    else:
        raise ValueError("Production requires DB_USER, DB_PASSWORD, DB_NAME, and DB_SOCKET environment variables")
    
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://joitex.el.r.appspot.com').split(',')
    
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Config selector
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get config based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
