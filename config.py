# Path: config.py

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'entf7819_db-client-server'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'entf7819_db-client-server'),
            charset=os.getenv('DB_CHARSET', 'utf8mb4'),
            autocommit=True,
            connection_timeout=10,
            raise_on_warnings=True,
            ssl_disabled=True
        )

        if connection.is_connected():
            return connection
        else:
            print("Failed to connect to database")
            return None

    except Error as e:
        print(f"Database connection error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during database connection: {e}")
        return None

def close_db_connection(connection):
    """Menutup koneksi database dengan aman"""
    if connection and connection.is_connected():
        try:
            connection.close()
        except Exception as e:
            print(f"Error closing database connection: {e}")

def test_db_connection():
    """Test koneksi database"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            close_db_connection(connection)
            version_str = version[0] if version else 'Unknown'
            return True, f"Database connected successfully. Version: {version_str}"
        except Exception as e:
            close_db_connection(connection)
            return False, f"Database test failed: {e}"
    else:
        return False, "Failed to establish database connection"