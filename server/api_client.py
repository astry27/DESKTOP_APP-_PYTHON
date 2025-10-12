# Path: server/api_client.py

import requests
import os
from dotenv import load_dotenv
import json
import datetime
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, ConnectionError, Timeout

load_dotenv()

BASE_URL = os.getenv('API_BASE_URL', 'https://enternal.my.id/flask')

class ApiClient:
    
    def __init__(self):
        self.base_url = BASE_URL
        self.timeout = 10
        
        # Setup session with retry strategy
        self.session = requests.Session()
        
        # Retry strategy - reduced to avoid "too many retries" error
        retry_strategy = Retry(
            total=1,  # Reduced retry attempts
            backoff_factor=0.5,  # Shorter wait time
            status_forcelist=[502, 503, 504],  # Remove 500 from retry list
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _make_request(self, method, url, **kwargs):
        """Make HTTP request with improved error handling"""
        for attempt in range(2):  # Reduced from 3 to 2
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=self.timeout, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, timeout=self.timeout, **kwargs)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, timeout=self.timeout, **kwargs)
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, timeout=self.timeout, **kwargs)
                else:
                    response = self.session.request(method, url, timeout=self.timeout, **kwargs)
                
                response.raise_for_status()
                return {"success": True, "data": response.json() if response.text else None}
                
            except ConnectionError as e:
                if "Failed to resolve" in str(e) or "getaddrinfo failed" in str(e) or "Name or service not known" in str(e):
                    if attempt < 2:  # Last attempt
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return {"success": False, "data": f"Gagal terhubung ke server: Masalah koneksi internet atau DNS. Periksa koneksi internet Anda."}
                else:
                    return {"success": False, "data": f"Gagal terhubung ke server: {e}"}
            except Timeout as e:
                if attempt < 2:
                    time.sleep(1)
                    continue
                return {"success": False, "data": f"Timeout koneksi ke server: {e}"}
            except RequestException as e:
                return {"success": False, "data": f"Gagal terhubung ke API: {e}"}
            except Exception as e:
                return {"success": False, "data": f"Error tidak terduga: {e}"}
        
        return {"success": False, "data": "Gagal terhubung setelah 3 kali percobaan"}

    def check_server_connection(self):
        return self._make_request('GET', self.base_url)
    
    def enable_api(self):
        return self._make_request('POST', f"{self.base_url}/admin/enable")
    
    def disable_api(self):
        return self._make_request('POST', f"{self.base_url}/admin/disable")
    
    def get_api_status(self):
        return self._make_request('GET', f"{self.base_url}/admin/status")
    
    def authenticate_admin(self, login_data):
        """Authenticate admin credentials"""
        return self._make_request('POST', f"{self.base_url}/admin/login", 
                                json=login_data, 
                                headers={'Content-Type': 'application/json'})
    
    def update_admin_last_login(self, admin_id):
        """Update last login timestamp untuk admin"""
        data = {
            'admin_id': admin_id,
            'last_login': datetime.datetime.now().isoformat()
        }
        return self._make_request('POST', f"{self.base_url}/admin/update-last-login", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
    
    def get_active_sessions(self):
        """Ambil daftar client yang sedang aktif"""
        return self._make_request('GET', f"{self.base_url}/admin/active-sessions")
    
    def send_broadcast_message(self, message):
        """Kirim broadcast message ke semua client"""
        data = {
            'message': message,
            'timestamp': datetime.datetime.now().isoformat()
        }
        return self._make_request('POST', f"{self.base_url}/admin/broadcast", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
    
    def test_database(self):
        return self._make_request('GET', f"{self.base_url}/test-db")
    
    # ========== USER MANAGEMENT METHODS ==========
    def get_users(self):
        """Get list of all admin users"""
        return self._make_request('GET', f"{self.base_url}/admin/list-users")
    
    def create_user(self, user_data):
        """Create new admin user"""
        return self._make_request('POST', f"{self.base_url}/admin/create-user", 
                               json=user_data, 
                               headers={'Content-Type': 'application/json'})
    
    def update_user(self, user_id, user_data):
        """Update existing admin user"""
        return self._make_request('PUT', f"{self.base_url}/admin/update-user/{user_id}", 
                               json=user_data, 
                               headers={'Content-Type': 'application/json'})
    
    def delete_user(self, user_id):
        """Delete admin user"""
        return self._make_request('DELETE', f"{self.base_url}/admin/users/{user_id}")
    
    # ========== JEMAAT METHODS ==========
    def get_jemaat(self):
        return self._make_request('GET', f"{self.base_url}/jemaat")
    
    def add_jemaat(self, data):
        return self._make_request('POST', f"{self.base_url}/jemaat", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
    
    def update_jemaat(self, jemaat_id, data):
        return self._make_request('PUT', f"{self.base_url}/jemaat/{jemaat_id}", 
                              json=data, 
                              headers={'Content-Type': 'application/json'})
    
    def delete_jemaat(self, jemaat_id):
        return self._make_request('DELETE', f"{self.base_url}/jemaat/{jemaat_id}")
    
    # ========== KEGIATAN METHODS ==========
    def get_kegiatan(self):
        return self._make_request('GET', f"{self.base_url}/kegiatan")
    
    def add_kegiatan(self, data):
        return self._make_request('POST', f"{self.base_url}/kegiatan", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
    
    def update_kegiatan(self, kegiatan_id, data):
        return self._make_request('PUT', f"{self.base_url}/kegiatan/{kegiatan_id}", 
                              json=data, 
                              headers={'Content-Type': 'application/json'})
    
    def delete_kegiatan(self, kegiatan_id):
        return self._make_request('DELETE', f"{self.base_url}/kegiatan/{kegiatan_id}")

    def get_kegiatan_wr(self):
        """Get all kegiatan WR from clients with user information"""
        return self._make_request('GET', f"{self.base_url}/kegiatan-wr")

    # ========== PENGUMUMAN METHODS ==========
    def get_pengumuman(self):
        return self._make_request('GET', f"{self.base_url}/pengumuman")
    
    def add_pengumuman(self, data):
        return self._make_request('POST', f"{self.base_url}/pengumuman", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
    
    def update_pengumuman(self, pengumuman_id, data):
        return self._make_request('PUT', f"{self.base_url}/pengumuman/{pengumuman_id}", 
                              json=data, 
                              headers={'Content-Type': 'application/json'})
    
    def delete_pengumuman(self, pengumuman_id):
        return self._make_request('DELETE', f"{self.base_url}/pengumuman/{pengumuman_id}")
    
    # ========== KEUANGAN METHODS ==========
    def get_keuangan(self):
        # Server admin request - tambahkan parameter is_admin=true untuk mendapatkan semua data dengan user info
        return self._make_request('GET', f"{self.base_url}/keuangan?is_admin=true&limit=1000")
    
    def add_keuangan(self, data):
        return self._make_request('POST', f"{self.base_url}/keuangan", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
    
    def update_keuangan(self, keuangan_id, data):
        return self._make_request('PUT', f"{self.base_url}/keuangan/{keuangan_id}", 
                              json=data, 
                              headers={'Content-Type': 'application/json'})
    
    def delete_keuangan(self, keuangan_id):
        return self._make_request('DELETE', f"{self.base_url}/keuangan/{keuangan_id}")
    
    # ========== FILES METHODS ==========
    def get_files(self):
        return self._make_request('GET', f"{self.base_url}/files")
    
    def upload_file(self, file_path, document_name=None, document_type=None):
        """Upload file with improved error handling"""
        for attempt in range(3):
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    
                    # Prepare form data
                    data = {}
                    if document_name:
                        data['document_name'] = document_name
                    if document_type:
                        data['document_type'] = document_type
                        data['jenis_dokumen'] = document_type
                    
                    # Debug logging untuk upload
                    print(f"Upload API - name: {document_name}, type: {document_type}")
                    
                    response = self.session.post(f"{self.base_url}/upload", 
                                               files=files,
                                               data=data,
                                               timeout=self.timeout)
                    response.raise_for_status()
                    return {"success": True, "data": response.json()}
                    
            except ConnectionError as e:
                if "Failed to resolve" in str(e) or "getaddrinfo failed" in str(e) or "Name or service not known" in str(e):
                    if attempt < 2:
                        time.sleep(2 ** attempt)
                        continue
                    return {"success": False, "data": f"Gagal terhubung ke server: Masalah koneksi internet atau DNS. Periksa koneksi internet Anda."}
                else:
                    return {"success": False, "data": f"Gagal upload file: {e}"}
            except Timeout as e:
                if attempt < 2:
                    time.sleep(1)
                    continue
                return {"success": False, "data": f"Timeout upload file: {e}"}
            except RequestException as e:
                return {"success": False, "data": f"Gagal upload file: {e}"}
            except Exception as e:
                return {"success": False, "data": f"Error reading file: {e}"}
        
        return {"success": False, "data": "Gagal upload file setelah 3 kali percobaan"}
    
    def delete_file(self, file_id):
        return self._make_request('DELETE', f"{self.base_url}/files/{file_id}")
# ========== LOG METHODS ==========
    def get_log_activities(self, limit=100):
        return self._make_request('GET', f"{self.base_url}/log/activities?limit={limit}")
    
    def add_log_activity(self, data):
        return self._make_request('POST', f"{self.base_url}/log/activities", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
    
    def get_recent_activities(self, limit=50, hours=24):
        return self._make_request('GET', f"{self.base_url}/log/activities/recent?limit={limit}&hours={hours}")
    
    def get_admin_activities(self, admin_id, limit=100):
        return self._make_request('GET', f"{self.base_url}/log/activities/admin/{admin_id}?limit={limit}")
    
    def download_file(self, file_id):
        """Download file with improved error handling"""
        for attempt in range(3):
            try:
                response = self.session.get(f"{self.base_url}/files/{file_id}/download", 
                                          timeout=self.timeout)
                response.raise_for_status()
                
                # Debug logging untuk response
                print(f"Download API - Status: {response.status_code}, Size: {len(response.content)} bytes")
                
                return {"success": True, "data": response.content, "headers": dict(response.headers)}
                
            except ConnectionError as e:
                if "Failed to resolve" in str(e) or "getaddrinfo failed" in str(e) or "Name or service not known" in str(e):
                    if attempt < 2:
                        time.sleep(2 ** attempt)
                        continue
                    return {"success": False, "data": f"Gagal terhubung ke server: Masalah koneksi internet atau DNS. Periksa koneksi internet Anda."}
                else:
                    return {"success": False, "data": f"Gagal download file: {e}"}
            except Timeout as e:
                if attempt < 2:
                    time.sleep(1)
                    continue
                return {"success": False, "data": f"Timeout download file: {e}"}
            except RequestException as e:
                return {"success": False, "data": f"Gagal download file: {e}"}
        
        return {"success": False, "data": "Gagal download file setelah 3 kali percobaan"}
    # ========== PESAN METHODS ==========
    def get_recent_messages(self, limit=50):
        return self._make_request('GET', f"{self.base_url}/pesan/recent?limit={limit}")
    
    def send_message(self, message_data):
        return self._make_request('POST', f"{self.base_url}/pesan", 
                               json=message_data, 
                               headers={'Content-Type': 'application/json'})
    
    def get_broadcast_messages(self, limit=20):
        return self._make_request('GET', f"{self.base_url}/pesan/broadcast?limit={limit}")
    
    # ========== STRUKTUR METHODS ==========
    def get_struktur(self):
        return self._make_request('GET', f"{self.base_url}/struktur")
    
    def add_struktur(self, data):
        return self._make_request('POST', f"{self.base_url}/struktur", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
    
    def update_struktur(self, struktur_id, data):
        return self._make_request('PUT', f"{self.base_url}/struktur/{struktur_id}", 
                              json=data, 
                              headers={'Content-Type': 'application/json'})
    
    def delete_struktur(self, struktur_id):
        return self._make_request('DELETE', f"{self.base_url}/struktur/{struktur_id}")
    
    def upload_struktur_photo(self, struktur_id, photo_path):
        """Upload foto untuk struktur yang sudah ada"""
        try:
            with open(photo_path, 'rb') as photo_file:
                files = {'photo': photo_file}
                response = self.session.post(
                    f"{self.base_url}/struktur/{struktur_id}/upload-photo",
                    files=files,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "data": f"Error upload foto: {str(e)}"}
    
    def upload_struktur_photo_new(self, photo_path):
        """Upload foto untuk struktur baru"""
        try:
            with open(photo_path, 'rb') as photo_file:
                files = {'photo': photo_file}
                response = self.session.post(
                    f"{self.base_url}/struktur/upload-photo",
                    files=files,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "data": f"Error upload foto: {str(e)}"}
    
    # ========== INVENTARIS METHODS ==========
    def get_inventaris(self):
        return self._make_request('GET', f"{self.base_url}/inventaris")
    
    def add_inventaris(self, data):
        return self._make_request('POST', f"{self.base_url}/inventaris", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
    
    def update_inventaris(self, inventaris_id, data):
        return self._make_request('PUT', f"{self.base_url}/inventaris/{inventaris_id}", 
                              json=data, 
                              headers={'Content-Type': 'application/json'})
    
    def delete_inventaris(self, inventaris_id):
        return self._make_request('DELETE', f"{self.base_url}/inventaris/{inventaris_id}")
    
    # ========== PROGRAM KERJA METHODS ==========
    def get_program_kerja(self, search=None, month=None, year=None):
        """Get program kerja list with optional filters"""
        params = {}
        if search:
            params['search'] = search
        if month:
            params['month'] = month
        if year:
            params['year'] = year
        
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        url = f"{self.base_url}/program-kerja"
        if query_string:
            url += f"?{query_string}"
        
        return self._make_request('GET', url)
    
    def add_program_kerja(self, data):
        """Add new program kerja"""
        return self._make_request('POST', f"{self.base_url}/program-kerja", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
    
    def update_program_kerja(self, program_id, data):
        """Update program kerja"""
        return self._make_request('PUT', f"{self.base_url}/program-kerja/{program_id}", 
                              json=data, 
                              headers={'Content-Type': 'application/json'})
    
    def delete_program_kerja(self, program_id):
        """Delete program kerja"""
        return self._make_request('DELETE', f"{self.base_url}/program-kerja/{program_id}")
    
    def get_program_statistics(self):
        """Get program kerja statistics"""
        return self._make_request('GET', f"{self.base_url}/program-kerja/statistics")
    
    def get_inventaris_statistics(self):
        return self._make_request('GET', f"{self.base_url}/inventaris/statistics")
    
    def get_inventaris_categories(self):
        return self._make_request('GET', f"{self.base_url}/inventaris/kategori")
    
    def get_inventaris_locations(self):
        return self._make_request('GET', f"{self.base_url}/inventaris/lokasi")