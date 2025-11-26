import mysql.connector
from mysql.connector import Error

# Hardcoded configuration untuk API lokal
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_client_server',
    'charset': 'utf8mb4',
    'autocommit': True,
    'connection_timeout': 10,
    'raise_on_warnings': False,
    'ssl_disabled': True
}

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

            # Extract version string safely
            if version and isinstance(version, (tuple, list)) and len(version) > 0:
                version_str = str(version[0])
            else:
                version_str = 'Unknown'

            return True, f"Database connected successfully. Version: {version_str}"
        except Exception as e:
            close_db_connection(connection)
            return False, f"Database test failed: {e}"
    else:
        return False, "Failed to establish database connection"
