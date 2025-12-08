"""
Configuration module for AlexRentaCar Admin App
Supports DEV and PROD environments with security features
"""
import os
from datetime import timedelta
from cryptography.fernet import Fernet


class Config:
    """Base configuration with common settings"""
    
    # Basic Flask config
    SECRET_KEY =  'dev-secret-key-change-in-production' #21XSWcxz3zaq45EDCxsw
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI =  'mysql+pymysql://root:@localhost/alquiler_vehiculos'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Database Encryption
    DATABASE_ENCRYPTION_KEY = 'DATABASE_ENCRYPTION_KEY'
    if DATABASE_ENCRYPTION_KEY:
        FERNET_KEY = DATABASE_ENCRYPTION_KEY.encode()
    else:
        # Generate a key if none provided (for development only)
        FERNET_KEY = b'DksZJAUDwI-aha-8ENccA_SlMoQkqTH-qEFBn4CcQVs='
    
    # Session configuration
    SESSION_COOKIE_SECURE =  True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1) #timedelta(seconds= 3600)
    
    # Cache configuration (Redis - Optional)
    ENABLE_CACHE = True
    CACHE_TYPE = 'SimpleCache'
    CACHE_REDIS_URL = 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT =  300
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'redis://localhost:6379/1'
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    
    # File upload configuration
    MAX_CONTENT_LENGTH = int(16 * 1024 * 1024)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)),  'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg','mp4'}
    
    # Security headers (Flask-Talisman)
    TALISMAN_FORCE_HTTPS = False
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': [
            "'self'", 
            "'unsafe-inline'", 
            "https://cdn.jsdelivr.net", 
            "https://code.jquery.com",
            "https://unpkg.com",  # Para FilePond
            "https://cdnjs.cloudflare.com"
        ],
        'style-src': [
            "'self'", 
            "'unsafe-inline'", 
            "https://cdn.jsdelivr.net",
            "https://unpkg.com"  # Para FilePond
        ],
        'img-src': ["'self'", "data:", "https:", "blob:"],
        'font-src': ["'self'", "https://cdn.jsdelivr.net"]
    }
    
    # Email configuration (for password reset)
    MAIL_SERVER         =  'smtp.gmail.com'
    MAIL_PORT           = int(587)
    MAIL_USE_TLS        = True
    MAIL_USERNAME       = 'MAIL_USERNAME'
    MAIL_PASSWORD       = 'MAIL_PASSWORD'
    MAIL_DEFAULT_SENDER = 'MAIL_USERNAME'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True
    TALISMAN_FORCE_HTTPS = False
    SESSION_COOKIE_SECURE = False
    FERNET_KEY = b'DksZJAUDwI-aha-8ENccA_SlMoQkqTH-qEFBn4CcQVs='


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False
    TALISMAN_FORCE_HTTPS = True
    SESSION_COOKIE_SECURE = True
    
    # Override with production values
    #if not SECRET_KEY:
    #    raise ValueError("SECRET_KEY must be set in production")
    
    #if not DATABASE_ENCRYPTION_KEY:
    #    raise ValueError("DATABASE_ENCRYPTION_KEY must be set in production")


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    ENABLE_CACHE = False
    RATELIMIT_ENABLED = False
    FERNET_KEY = b'DksZJAUDwI-aha-8ENccA_SlMoQkqTH-qEFBn4CcQVs='
 
# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env =  'development'
    return config.get(env, config['default'])