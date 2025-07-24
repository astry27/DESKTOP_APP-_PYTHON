# Path: client/config.py

import os
import json
from typing import Dict, Any

class ClientConfig:
    """Konfigurasi aplikasi client"""
    
    # Path default untuk file konfigurasi pengguna
    CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), '.gereja_client_settings.json')

    # Default values
    DEFAULT_API_URL = os.getenv('DEFAULT_API_URL', 'http://localhost:3000') # Ganti dengan URL API default Anda
    DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "GerejaKatolikFiles")
    
    @staticmethod
    def load_settings() -> Dict[str, Any]:
        """Memuat pengaturan dari file JSON. Jika tidak ada, kembalikan default."""
        if os.path.exists(ClientConfig.CONFIG_FILE_PATH):
            try:
                with open(ClientConfig.CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Pastikan semua kunci default ada
                    if 'api_url' not in settings:
                        settings['api_url'] = ClientConfig.DEFAULT_API_URL
                    if 'download_dir' not in settings:
                        settings['download_dir'] = ClientConfig.DEFAULT_DOWNLOAD_DIR
                    return settings
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error memuat file konfigurasi: {e}. Menggunakan default.")
        
        # Kembalikan pengaturan default jika file tidak ada atau rusak
        return {
            'api_url': ClientConfig.DEFAULT_API_URL,
            'download_dir': ClientConfig.DEFAULT_DOWNLOAD_DIR,
        }

    @staticmethod
    def save_settings(settings: Dict[str, Any]):
        """Menyimpan pengaturan ke file JSON."""
        try:
            # Pastikan folder ada
            os.makedirs(os.path.dirname(ClientConfig.CONFIG_FILE_PATH), exist_ok=True)
            with open(ClientConfig.CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except IOError as e:
            print(f"Error menyimpan file konfigurasi: {e}")