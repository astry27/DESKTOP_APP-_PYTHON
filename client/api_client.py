# Path: client/api_client.py

import requests
import os
import socket
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

BASE_URL = os.getenv('API_BASE_URL', 'https://enternal.my.id/flask')

class ApiClient:
    
    def __init__(self):
        self.base_url = BASE_URL
        self.timeout = 10
        self.client_ip = self.get_client_ip()
        self.client_hostname = socket.gethostname()
        self.session_id = None
        self.user_data = None
    
    def get_client_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def register_client(self):
        try:
            data = {
                'client_ip': self.client_ip,
                'hostname': self.client_hostname
            }
            response = requests.post(f"{self.base_url}/client/register", 
                                   json=data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            result = response.json()
            if result.get('status') == 'success':
                self.session_id = result.get('connection_id')
            return {"success": True, "data": result}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal registrasi client: {e}"}
    
    def disconnect_client(self):
        try:
            if self.session_id:
                data = {
                    'connection_id': self.session_id,
                    'client_ip': self.client_ip
                }
                response = requests.post(f"{self.base_url}/client/disconnect", 
                                       json=data, 
                                       timeout=self.timeout,
                                       headers={'Content-Type': 'application/json'})
                response.raise_for_status()
                return {"success": True, "data": response.json()}
            return {"success": True, "data": "No active session"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal disconnect client: {e}"}
    
    def heartbeat(self):
        try:
            data = {
                'connection_id': self.session_id,
                'client_ip': self.client_ip
            }
            response = requests.post(f"{self.base_url}/client/heartbeat", 
                                   json=data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal heartbeat: {e}"}
    
    def check_server_connection(self):
        try:
            response = requests.get(self.base_url, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal terhubung ke API: {e}"}
    
    def login(self, username, password):
        try:
            data = {
                'username': username,
                'password': password
            }
            response = requests.post(f"{self.base_url}/auth/login", 
                                   json=data, 
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') == 'success':
                self.user_data = result.get('user')
            
            return {"success": True, "data": result}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal login: {e}"}
    
    def get_jemaat(self):
        try:
            response = requests.get(f"{self.base_url}/jemaat", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data jemaat: {e}"}
    
    def get_kegiatan(self):
        try:
            response = requests.get(f"{self.base_url}/kegiatan", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data kegiatan: {e}"}
    
    def get_pengumuman(self):
        try:
            response = requests.get(f"{self.base_url}/pengumuman?active_only=true", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data pengumuman: {e}"}
    
    def get_keuangan(self):
        try:
            response = requests.get(f"{self.base_url}/keuangan", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data keuangan: {e}"}
    
    def upload_file(self, file_path, kategori="Lainnya", keterangan=""):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                data = {
                    'kategori': kategori,
                    'keterangan': keterangan,
                    'uploaded_by_pengguna': self.user_data.get('id_pengguna') if self.user_data else None
                }
                response = requests.post(f"{self.base_url}/upload", 
                                       files=files,
                                       data=data,
                                       timeout=60)
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal upload file: {e}"}
        except Exception as e:
            return {"success": False, "data": f"Error reading file: {e}"}
    
    def get_files(self):
        try:
            response = requests.get(f"{self.base_url}/files", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil daftar file: {e}"}
    
    def download_file(self, file_id):
        try:
            response = requests.get(f"{self.base_url}/files/{file_id}/download", 
                                  timeout=self.timeout, stream=True)
            response.raise_for_status()
            return {"success": True, "data": response.content, "headers": response.headers}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal download file: {e}"}
    
    def get_messages(self, limit=50, since=None):
        try:
            params = {'limit': limit}
            if since:
                params['since'] = since
                
            response = requests.get(f"{self.base_url}/client/messages", 
                                  params=params, 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil pesan: {e}"}
    
    def send_message_to_admin(self, message):
        try:
            data = {
                'pengirim_pengguna': self.user_data.get('id_pengguna') if self.user_data else None,
                'pesan': message,
                'target': 'admin'
            }
            response = requests.post(f"{self.base_url}/client/send-message", 
                                   json=data, 
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
    
    def get_recent_messages(self, limit=50, hours=24):
        try:
            response = requests.get(f"{self.base_url}/pesan/recent?limit={limit}&hours={hours}", 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil pesan terbaru: {e}"}
    
    def get_active_clients(self):
        try:
            response = requests.get(f"{self.base_url}/client/active", 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil client aktif: {e}"}