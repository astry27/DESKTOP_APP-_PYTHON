# Path: api/wsgi.py

"""
WSGI entry point untuk deployment di shared hosting
Sesuaikan dengan konfigurasi shared hosting Anda
"""

import sys
import os

# Tambahkan path aplikasi ke Python path
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path)

# Set environment variables
os.environ.setdefault('FLASK_ENV', 'production')

# Import aplikasi
from app import app as application

# Konfigurasi untuk production
application.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'your-production-secret-key-here'),
    
    # Database configuration untuk shared hosting
    # Ganti dengan credential database Anda
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 
        'mysql+pymysql://enternal_gereja:your_password@localhost/enternal_gereja_api'),
    
    # Security settings
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    
    # CORS settings untuk production
    CORS_ORIGINS=[
        'https://enternal.my.id',
        'https://www.enternal.my.id'
    ]
)

if __name__ == "__main__":
    application.run()