import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Database configuration - Uses environment variables for security
# This allows different configs for development, staging, and production
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'db_client_server'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
    'autocommit': True,
    'connection_timeout': 10,
    'raise_on_warnings': False,
    'ssl_disabled': True
}

# Print configuration status (without exposing password)
print(f"[CONFIG] Database: {DB_CONFIG['database']} @ {DB_CONFIG['host']}:{DB_CONFIG['port']}")
print(f"[CONFIG] User: {DB_CONFIG['user']}")
print(f"[CONFIG] Password: {'(set)' if DB_CONFIG['password'] else '(empty - WARNING!)'}")

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"[ERROR] Database connection error: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error during database connection: {e}")
        return None

def close_db_connection(connection):
    if connection and connection.is_connected():
        try:
            connection.close()
        except Exception as e:
            print(f"Error closing database connection: {e}")

def test_db_connection():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            close_db_connection(connection)
            version_str = version[0] if version is not None else 'Unknown'  # type: ignore
            return True, f"Database connected successfully. Version: {version_str}"
        except Exception as e:
            close_db_connection(connection)
            return False, f"Database test failed: {e}"
    else:
        return False, "Failed to establish database connection"

# Konfigurasi untuk URL API server
class ServerConfig:
    """Konfigurasi untuk URL API server."""
    API_BASE_URL = "http://127.0.0.1:5000"
