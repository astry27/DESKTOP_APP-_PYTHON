#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error

# List password yang umum digunakan
common_passwords = [
    '',           # No password
    'root',       # password = root
    'password',   # password = password
    'admin',      # password = admin
    '123456',     # password = 123456
    'mysql',      # password = mysql
    'toor',       # password = toor (root reversed)
    'Password123',# password = Password123
    '12345678',   # password = 12345678
]

print("Testing MySQL connection with common passwords...")
print("=" * 50)

for password in common_passwords:
    try:
        print(f"\nTrying password: '{password}' ", end='')
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=password,
            connection_timeout=5
        )

        if conn.is_connected():
            print("SUCCESS!")
            print(f"\n{'=' * 50}")
            print(f"FOUND WORKING PASSWORD: '{password}'")
            print(f"{'=' * 50}")

            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL Version: {version[0]}")

            # Show databases
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(f"\nAvailable databases:")
            for db in databases:
                print(f"  - {db[0]}")

            cursor.close()
            conn.close()

            print(f"\nUpdate your .env file with:")
            print(f"DB_PASSWORD={password}")
            break

    except Error as e:
        if e.errno == 1045:  # Access denied
            print("X Access denied")
        else:
            print(f"X Error: {e}")
    except Exception as e:
        print(f"X Error: {e}")
else:
    print("\n" + "=" * 50)
    print("No common password worked.")
    print("You need to reset MySQL root password or provide the correct password.")
    print("=" * 50)
