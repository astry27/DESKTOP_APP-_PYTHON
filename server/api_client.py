# Path: server/api_client.py

import requests
import os
from dotenv import load_dotenv
import json
import datetime

load_dotenv()

BASE_URL = os.getenv('API_BASE_URL', 'https://enternal.my.id/flask')

class ApiClient:
    
    def __init__(self):
        self.base_url = BASE_URL
        self.timeout = 10
    
    def check_server_connection(self):
        try:
            response = requests.get(self.base_url, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal terhubung ke API: {e}"}
    
    def enable_api(self):
        try:
            response = requests.post(f"{self.base_url}/admin/enable", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengaktifkan API: {e}"}
    
    def disable_api(self):
        try:
            response = requests.post(f"{self.base_url}/admin/disable", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menonaktifkan API: {e}"}
    
    def get_api_status(self):
        try:
            response = requests.get(f"{self.base_url}/admin/status", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengecek status API: {e}"}
    
    def authenticate_admin(self, login_data):
        """Authenticate admin credentials"""
        try:
            response = requests.post(f"{self.base_url}/admin/login", 
                                   json=login_data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal login admin: {e}"}
    
    def update_admin_last_login(self, admin_id):
        """Update last login timestamp untuk admin"""
        try:
            data = {
                'admin_id': admin_id,
                'last_login': datetime.datetime.now().isoformat()
            }
            response = requests.post(f"{self.base_url}/admin/update-last-login", 
                                   json=data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal update last login: {e}"}
    
    def get_active_sessions(self):
        """Ambil daftar client yang sedang aktif"""
        try:
            response = requests.get(f"{self.base_url}/admin/active-sessions", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil active sessions: {e}"}
    
    def send_broadcast_message(self, message):
        """Kirim broadcast message ke semua client"""
        try:
            data = {
                'message': message,
                'timestamp': datetime.datetime.now().isoformat()
            }
            response = requests.post(f"{self.base_url}/admin/broadcast", 
                                   json=data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengirim broadcast message: {e}"}
    
    def test_database(self):
        try:
            response = requests.get(f"{self.base_url}/test-db", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal test database: {e}"}
    
    # ========== JEMAAT METHODS ==========
    def get_jemaat(self):
        try:
            response = requests.get(f"{self.base_url}/jemaat", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data jemaat: {e}"}
    
    def add_jemaat(self, data):
        try:
            response = requests.post(f"{self.base_url}/jemaat", 
                                   json=data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menambah jemaat: {e}"}
    
    def update_jemaat(self, jemaat_id, data):
        try:
            response = requests.put(f"{self.base_url}/jemaat/{jemaat_id}", 
                                  json=data, 
                                  timeout=self.timeout,
                                  headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengupdate jemaat: {e}"}
    
    def delete_jemaat(self, jemaat_id):
        try:
            response = requests.delete(f"{self.base_url}/jemaat/{jemaat_id}", 
                                     timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menghapus jemaat: {e}"}
    
    # ========== KEGIATAN METHODS ==========
    def get_kegiatan(self):
        try:
            response = requests.get(f"{self.base_url}/kegiatan", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data kegiatan: {e}"}
    
    def add_kegiatan(self, data):
        try:
            response = requests.post(f"{self.base_url}/kegiatan", 
                                   json=data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menambah kegiatan: {e}"}
    
    def update_kegiatan(self, kegiatan_id, data):
        try:
            response = requests.put(f"{self.base_url}/kegiatan/{kegiatan_id}", 
                                  json=data, 
                                  timeout=self.timeout,
                                  headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengupdate kegiatan: {e}"}
    
    def delete_kegiatan(self, kegiatan_id):
        try:
            response = requests.delete(f"{self.base_url}/kegiatan/{kegiatan_id}", 
                                     timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menghapus kegiatan: {e}"}
    
    # ========== PENGUMUMAN METHODS ==========
    def get_pengumuman(self):
        try:
            response = requests.get(f"{self.base_url}/pengumuman", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data pengumuman: {e}"}
    
    def add_pengumuman(self, data):
        try:
            response = requests.post(f"{self.base_url}/pengumuman", 
                                   json=data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menambah pengumuman: {e}"}
    
    def update_pengumuman(self, pengumuman_id, data):
        try:
            response = requests.put(f"{self.base_url}/pengumuman/{pengumuman_id}", 
                                  json=data, 
                                  timeout=self.timeout,
                                  headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengupdate pengumuman: {e}"}
    
    def delete_pengumuman(self, pengumuman_id):
        try:
            response = requests.delete(f"{self.base_url}/pengumuman/{pengumuman_id}", 
                                     timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menghapus pengumuman: {e}"}
    
    # ========== KEUANGAN METHODS ==========
    def get_keuangan(self):
        try:
            response = requests.get(f"{self.base_url}/keuangan", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data keuangan: {e}"}
    
    def add_keuangan(self, data):
        try:
            response = requests.post(f"{self.base_url}/keuangan", 
                                   json=data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menambah data keuangan: {e}"}
    
    def update_keuangan(self, keuangan_id, data):
        try:
            response = requests.put(f"{self.base_url}/keuangan/{keuangan_id}", 
                                  json=data, 
                                  timeout=self.timeout,
                                  headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengupdate data keuangan: {e}"}
    
    def delete_keuangan(self, keuangan_id):
        try:
            response = requests.delete(f"{self.base_url}/keuangan/{keuangan_id}", 
                                     timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menghapus data keuangan: {e}"}
    
    # ========== FILES METHODS ==========
    def get_files(self):
        try:
            response = requests.get(f"{self.base_url}/files", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data files: {e}"}
    
    def upload_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.base_url}/upload", 
                                       files=files, 
                                       timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal upload file: {e}"}
        except Exception as e:
            return {"success": False, "data": f"Error reading file: {e}"}
    
    def delete_file(self, file_id):
        try:
            response = requests.delete(f"{self.base_url}/files/{file_id}", 
                                     timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menghapus file: {e}"}
# ========== LOG METHODS ==========
    def get_log_activities(self, limit=100):
        try:
            response = requests.get(f"{self.base_url}/log/activities?limit={limit}", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil log aktivitas: {e}"}
    
    def add_log_activity(self, data):
        try:
            response = requests.post(f"{self.base_url}/log/activities", 
                                   json=data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menambah log aktivitas: {e}"}
    
    def get_recent_activities(self, limit=50, hours=24):
        try:
            response = requests.get(f"{self.base_url}/log/activities/recent?limit={limit}&hours={hours}", 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil aktivitas terbaru: {e}"}
    
    def get_admin_activities(self, admin_id, limit=100):
        try:
            response = requests.get(f"{self.base_url}/log/activities/admin/{admin_id}?limit={limit}", 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil aktivitas admin: {e}"}
    
    def download_file(self, file_id):
        try:
            response = requests.get(f"{self.base_url}/files/{file_id}/download", 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.content, "headers": response.headers}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal download file: {e}"}
    # ========== PESAN METHODS ==========
    def get_recent_messages(self, limit=50):
        try:
            response = requests.get(f"{self.base_url}/pesan/recent?limit={limit}", 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil pesan: {e}"}
    
    def send_message(self, message_data):
        try:
            response = requests.post(f"{self.base_url}/pesan", 
                                   json=message_data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengirim pesan: {e}"}
    
    def get_broadcast_messages(self, limit=20):
        try:
            response = requests.get(f"{self.base_url}/pesan/broadcast?limit={limit}", 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil broadcast messages: {e}"}