# Path: api/config.py

import os
from datetime import timedelta

class Config:
    """Konfigurasi Flask untuk API Management"""
    
    # Secret key untuk JWT dan session
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gereja-katolik-api-secret-key-2024'
    
    # Database configuration untuk shared hosting
    # Ganti dengan credential database shared hosting Anda
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://username:password@localhost/gereja_api_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_ALGORITHM = 'HS256'
    
    # Session configuration
    SESSION_TIMEOUT = 24 * 60 * 60  # 24 jam dalam detik
    
    # CORS configuration
    CORS_ORIGINS = [
        'http://localhost:*',
        'https://enternal.my.id',
        '*'  # Untuk development, hapus untuk production
    ]
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = "100 per hour"
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # API Configuration
    API_VERSION = '1.0.0'
    API_TITLE = 'Gereja Katolik API Management'
    API_DESCRIPTION = 'API untuk manajemen akses Client-Server Gereja Katolik'
    
    # Server registry configuration
    SERVER_TIMEOUT = 300  # 5 menit timeout untuk server ping
    MAX_SERVERS_PER_USER = 5
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = 'api.log'
    
    # External API configuration (jika ada)
    EXTERNAL_API_TIMEOUT = 30
    EXTERNAL_API_RETRIES = 3
    
    # Security configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True  # Set False untuk development tanpa HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Timezone
    TIMEZONE = 'Asia/Jakarta'

class DevelopmentConfig(Config):
    """Konfigurasi untuk development"""
    DEBUG = True
    TESTING = False
    
    # Database untuk development (bisa pakai SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///gereja_api_dev.db'
    
    # CORS lebih permissive untuk development
    CORS_ORIGINS = ['*']
    
    # Session cookie secure False untuk development
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Konfigurasi untuk production di shared hosting"""
    DEBUG = False
    TESTING = False
    
    # Database untuk production - ganti dengan credential shared hosting
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://enternal_gereja:password123@localhost/enternal_gereja_api'
    
    # CORS hanya untuk domain yang diizinkan
    CORS_ORIGINS = [
        'https://enternal.my.id',
        'https://www.enternal.my.id'
    ]
    
    # Security settings untuk production
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)  # Lebih pendek untuk security

class TestingConfig(Config):
    """Konfigurasi untuk testing"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # Database in-memory untuk testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Dictionary untuk memilih konfigurasi berdasarkan environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}