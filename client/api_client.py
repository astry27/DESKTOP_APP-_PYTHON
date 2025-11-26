# Path: client/api_client.py

import requests
import os
import socket
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

# Production server with local fallback
BASE_URL = os.getenv('API_BASE_URL', 'https://enternal.my.id/flask')  # Server production
REMOTE_URL = 'https://enternal.my.id/flask'  # Production URL

class ApiClient:
    
    def __init__(self):
        self.base_url = BASE_URL
        self.remote_url = REMOTE_URL
        self.timeout = 10
        self.client_ip = self.get_client_ip()
        # Add app identifier to hostname untuk membedakan admin dan client di komputer yang sama
        # Format: HOSTNAME-CLIENT (e.g., DESKTOP-XYZ-CLIENT)
        self.client_hostname = f"{socket.gethostname()}-CLIENT"
        self.session_id = None
        self.connection_id = None  # ID koneksi dari database server
        self.user_data = None
        self.device_info = self.get_device_info()

        # Auto-detect best server
        self._detect_best_server()
    
    def _detect_best_server(self):
        """Auto-detect apakah menggunakan production atau local server"""
        # List server untuk dicoba - prioritaskan production server
        servers_to_try = [
            'https://enternal.my.id/flask',  # Production server (prioritas utama)
            'http://localhost:5000',  # Flask local development fallback
            'http://127.0.0.1:5000',  # IPv4 localhost Flask
            'http://localhost:8000',  # Server HTTP lokal
            'http://localhost:3000',  # Express default
        ]
        
        print("Mencari server yang tersedia...")
        for server_url in servers_to_try:
            try:
                print(f"  Testing: {server_url}")
                response = requests.get(server_url, timeout=3)
                if response.status_code in [200, 404]:  # 404 juga OK, artinya server hidup
                    self.base_url = server_url
                    print(f"Server ditemukan: {server_url}")
                    return
            except:
                continue
        
        # Jika semua gagal, gunakan default
        print(f"Tidak ada server yang tersedia, menggunakan default: {BASE_URL}")
        self.base_url = BASE_URL
    
    def get_client_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def get_device_info(self):
        """Ambil informasi lengkap perangkat"""
        import platform
        import os
        try:
            device_info = {
                'platform': platform.system(),
                'platform_version': platform.release(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'hostname': socket.gethostname(),
                'username': os.getlogin() if hasattr(os, 'getlogin') else 'Unknown'
            }
            return device_info
        except:
            return {
                'platform': 'Unknown',
                'platform_version': 'Unknown',
                'architecture': 'Unknown',
                'processor': 'Unknown',
                'python_version': 'Unknown',
                'hostname': socket.gethostname(),
                'username': 'Unknown'
            }
    
    def register_client(self):
        """Registrasi client ke server untuk tracking koneksi"""
        try:
            import datetime
            import uuid
            
            # Generate session ID lokal
            session_id = str(uuid.uuid4())
            self.session_id = session_id
            
            # Data yang akan dikirim ke server
            data = {
                'client_ip': self.client_ip,
                'hostname': self.client_hostname,
                'connect_time': datetime.datetime.now().isoformat(),
                'last_activity': datetime.datetime.now().isoformat(),
                'status': 'connected',
                'user_data': self.user_data if self.user_data else None,
                'device_info': self.device_info,
                'client_type': 'desktop_client',
                'session_id': session_id
            }
            
            print(f"[DEBUG] Registering client with session: {session_id}")
            print(f"[DEBUG] Client IP: {self.client_ip}")
            print(f"[DEBUG] Hostname: {self.client_hostname}")
            
            # Variable untuk tracking registrasi
            local_registered = False
            remote_registered = False
            final_connection_id = None

            # Coba registrasi ke server lokal (opsional, untuk admin tracking)
            try:
                # Coba ke server lokal dulu
                local_response = requests.post("http://localhost:8080/client/register",
                                             json=data,
                                             timeout=5,
                                             headers={'Content-Type': 'application/json'})

                if local_response.status_code == 200:
                    local_result = local_response.json()
                    if local_result.get('status') == 'success':
                        print(f"[DEBUG] Local server registration successful")
                        local_registered = True

            except Exception as e:
                print(f"[DEBUG] Local server registration failed: {e}")
            
            # WAJIB: Registrasi ke API remote (production/database)
            try:
                response = requests.post(f"{self.base_url}/client/register",
                                       json=data,
                                       timeout=self.timeout,
                                       headers={'Content-Type': 'application/json'})

                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        print(f"[DEBUG] Remote API registration successful")
                        # PENTING: Ambil connection_id dari server response, bukan pakai UUID lokal
                        server_connection_id = result.get('connection_id')
                        if server_connection_id:
                            self.connection_id = server_connection_id
                            final_connection_id = server_connection_id
                            remote_registered = True
                            print(f"[DEBUG] Stored server connection_id: {server_connection_id}")
                    else:
                        print(f"[DEBUG] Remote API registration failed: {result}")

            except Exception as e:
                print(f"[DEBUG] Remote API registration error: {e}")

            # Return hasil registrasi
            if remote_registered:
                # Sukses register ke remote API (database) - ini yang penting
                return {"success": True, "data": {"status": "success", "connection_id": final_connection_id, "message": "Client registered to remote API"}}
            elif local_registered:
                # Hanya berhasil ke local server, tapi ini tidak cukup
                print(f"[WARNING] Only registered to local server, not to remote API database")
                return {"success": False, "data": "Failed to register to remote API - server control won't detect this client"}
            else:
                # Gagal semua
                print(f"[ERROR] Failed to register to both local and remote server")
                return {"success": False, "data": "Registration failed to all servers"}
            
        except Exception as e:
            print(f"[ERROR] Client registration failed: {e}")
            return {"success": False, "data": f"Registration failed: {e}"}
    
    
    def disconnect_client(self):
        try:
            # Gunakan connection_id dari server jika ada, fallback ke session_id
            conn_id = self.connection_id if self.connection_id else self.session_id
            if conn_id:
                import datetime
                data = {
                    'connection_id': conn_id,
                    'client_ip': self.client_ip,
                    'hostname': self.client_hostname,
                    'disconnect_time': datetime.datetime.now().isoformat(),
                    'status': 'disconnected'
                }
                # Coba disconnect dari server lokal dulu
                try:
                    local_response = requests.post("http://localhost:8080/client/disconnect",
                                                 json=data,
                                                 timeout=3,
                                                 headers={'Content-Type': 'application/json'})
                    if local_response.status_code == 200:
                        self.session_id = None
                        self.connection_id = None
                        return {"success": True, "data": local_response.json()}
                except:
                    pass  # Continue to remote

                # Fallback ke remote API
                response = requests.post(f"{self.base_url}/client/disconnect",
                                       json=data,
                                       timeout=self.timeout,
                                       headers={'Content-Type': 'application/json'})
                response.raise_for_status()
                self.session_id = None
                self.connection_id = None
                return {"success": True, "data": response.json()}
            return {"success": True, "data": "No active session"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal disconnect client: {e}"}
    
    def heartbeat(self):
        """Kirim heartbeat ke server untuk update status"""
        try:
            # Gunakan connection_id dari server jika ada, fallback ke session_id
            conn_id = self.connection_id if self.connection_id else self.session_id
            if not conn_id:
                return {"success": False, "data": "No connection ID or session ID"}

            import datetime
            data = {
                'connection_id': conn_id,
                'client_ip': self.client_ip,
                'hostname': self.client_hostname,
                'last_activity': datetime.datetime.now().isoformat(),
                'status': 'active',
                'user_data': self.user_data if self.user_data else None
            }

            # Coba kirim heartbeat ke server lokal terlebih dahulu
            try:
                # Coba local server dulu
                local_response = requests.post("http://localhost:8080/client/heartbeat",
                                             json=data,
                                             timeout=3,
                                             headers={'Content-Type': 'application/json'})

                if local_response.status_code == 200:
                    local_result = local_response.json()
                    return {"success": True, "data": local_result}

            except Exception as e:
                pass  # Continue to remote fallback
            
            # Fallback ke remote API
            try:
                response = requests.post(f"{self.base_url}/client/heartbeat", 
                                       json=data, 
                                       timeout=5,  # Timeout singkat untuk heartbeat
                                       headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    result = response.json()
                    return {"success": True, "data": result}
                else:
                    return {"success": False, "data": f"Heartbeat failed: {response.status_code}"}
                    
            except Exception as e:
                # Heartbeat gagal tidak masalah, client tetap bisa jalan
                return {"success": False, "data": f"Heartbeat error: {e}"}
                
        except Exception as e:
            return {"success": False, "data": f"Heartbeat exception: {e}"}
    
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
                user_data = result.get('user')
                if user_data:
                    self.user_data = user_data
            
            return {"success": True, "data": result}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal login: {e}"}
    
    def get_jemaat(self):
        try:
            if not self.user_data:
                return {"success": False, "data": "User not logged in"}

            user_id = self.user_data.get('id_pengguna')
            if not user_id:
                return {"success": False, "data": "User ID not found"}

            params = {'user_id': user_id}
            response = requests.get(f"{self.base_url}/jemaat/my", params=params, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data jemaat: {e}"}
    
    def add_jemaat(self, jemaat_data):
        try:
            # Ensure jemaat_data is not None/empty
            if not jemaat_data:
                return {"success": False, "data": "Data jemaat tidak boleh kosong"}

            data = jemaat_data.copy()

            # Ensure user_id is present
            if self.user_data:
                data['user_id'] = self.user_data.get('id_pengguna')

            if 'user_id' not in data or data['user_id'] is None:
                return {"success": False, "data": "user_id is missing - user may not be logged in"}

            response = requests.post(f"{self.base_url}/jemaat",
                                   json=data,
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menambah data jemaat: {e}"}
    
    def update_jemaat(self, jemaat_id, jemaat_data):
        try:
            response = requests.put(f"{self.base_url}/jemaat/{jemaat_id}", 
                                  json=jemaat_data, 
                                  timeout=self.timeout,
                                  headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal update data jemaat: {e}"}
    
    def delete_jemaat(self, jemaat_id):
        try:
            response = requests.delete(f"{self.base_url}/jemaat/{jemaat_id}", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal hapus data jemaat: {e}"}
    
    def get_my_kegiatan(self):
        """Get kegiatan for current user only (user-specific endpoint)"""
        try:
            if not self.user_data:
                return {"success": False, "data": "User not logged in"}

            user_id = self.user_data.get('id_pengguna')
            params = {'user_id': user_id}

            response = requests.get(f"{self.base_url}/kegiatan/my", params=params, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data kegiatan: {e}"}

    def get_kegiatan(self):
        """Get kegiatan for current user (legacy - uses filter)"""
        try:
            if not self.user_data:
                return {"success": False, "data": "User not logged in"}

            user_id = self.user_data.get('id_pengguna')
            params = {'user_id': user_id}

            response = requests.get(f"{self.base_url}/kegiatan", params=params, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data kegiatan: {e}"}

    def add_kegiatan(self, data):
        """Add new kegiatan for current user"""
        try:
            if not self.user_data:
                return {"success": False, "data": "User not logged in"}

            # Add user_id to data
            data['user_id'] = self.user_data.get('id_pengguna')
            data['dibuat_oleh'] = self.user_data.get('username')

            # Debug logging
            print(f"[DEBUG] Sending kegiatan data: {data}")
            print(f"[DEBUG] URL: {self.base_url}/kegiatan")

            response = requests.post(f"{self.base_url}/kegiatan",
                                   json=data,
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})

            # Debug response
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response text: {response.text}")

            response.raise_for_status()
            result = response.json()
            return {"success": True, "data": result}
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (4xx, 5xx)
            error_msg = f"HTTP Error {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f": {error_detail.get('message', e.response.text)}"
            except:
                error_msg += f": {e.response.text}"
            print(f"[ERROR] {error_msg}")
            return {"success": False, "data": error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"Gagal menambahkan kegiatan: {e}"
            print(f"[ERROR] {error_msg}")
            return {"success": False, "data": error_msg}
        except Exception as e:
            error_msg = f"Error tidak terduga: {e}"
            print(f"[ERROR] {error_msg}")
            return {"success": False, "data": error_msg}

    def update_kegiatan(self, kegiatan_id, data):
        """Update kegiatan"""
        try:
            if not self.user_data:
                return {"success": False, "data": "User not logged in"}

            response = requests.put(f"{self.base_url}/kegiatan/{kegiatan_id}", json=data, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal update kegiatan: {e}"}

    def delete_kegiatan(self, kegiatan_id):
        """Delete kegiatan"""
        try:
            if not self.user_data:
                return {"success": False, "data": "User not logged in"}

            response = requests.delete(f"{self.base_url}/kegiatan/{kegiatan_id}", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal hapus kegiatan: {e}"}

    # Kegiatan WR Methods
    def get_my_kegiatan_wr(self):
        """Get kegiatan WR for current user only"""
        try:
            if not self.user_data:
                return {"success": False, "data": "User not logged in"}

            user_id = self.user_data.get('id_pengguna')
            params = {'user_id': user_id}

            response = requests.get(f"{self.base_url}/kegiatan-wr/my", params=params, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data kegiatan WR: {e}"}

    def add_kegiatan_wr(self, data):
        """Add new kegiatan WR for current user"""
        try:
            if not self.user_data:
                return {"success": False, "data": "User not logged in"}

            # Add user_id to data
            data['user_id'] = self.user_data.get('id_pengguna')

            response = requests.post(f"{self.base_url}/kegiatan-wr",
                                   json=data,
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})

            response.raise_for_status()
            result = response.json()
            return {"success": True, "data": result}
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f": {error_detail.get('message', e.response.text)}"
            except:
                error_msg += f": {e.response.text}"
            return {"success": False, "data": error_msg}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menambahkan kegiatan WR: {e}"}

    def update_kegiatan_wr(self, kegiatan_id, data):
        """Update kegiatan WR"""
        try:
            if not self.user_data:
                return {"success": False, "data": "User not logged in"}

            response = requests.put(f"{self.base_url}/kegiatan-wr/{kegiatan_id}", json=data, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal update kegiatan WR: {e}"}

    def delete_kegiatan_wr(self, kegiatan_id):
        """Delete kegiatan WR"""
        try:
            if not self.user_data:
                return {"success": False, "data": "User not logged in"}

            response = requests.delete(f"{self.base_url}/kegiatan-wr/{kegiatan_id}", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal hapus kegiatan WR: {e}"}

    # ========== PROGRAM KERJA WR METHODS ==========
    def get_program_kerja_wr_list(self, search=None, wilayah_id=None):
        """Get list of program kerja WR for current user"""
        try:
            params = {}
            if self.user_data:
                params['user_id'] = self.user_data.get('id_pengguna')
            if search:
                params['search'] = search
            if wilayah_id:
                params['wilayah_id'] = wilayah_id

            response = requests.get(f"{self.base_url}/program-kerja-wr",
                                  params=params,
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data program kerja WR: {e}"}

    def add_program_kerja_wr(self, data):
        """Add new program kerja WR for current user"""
        try:
            # Add user_id to data
            if self.user_data:
                data['user_id'] = self.user_data.get('id_pengguna')

            response = requests.post(f"{self.base_url}/program-kerja-wr",
                                   json=data,
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f": {error_detail.get('data', e.response.text)}"
            except:
                error_msg += f": {e.response.text}"
            return {"success": False, "data": error_msg}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menambahkan program kerja WR: {e}"}

    def update_program_kerja_wr(self, program_id, data):
        """Update program kerja WR"""
        try:
            # Add user_id to data
            if self.user_data:
                data['user_id'] = self.user_data.get('id_pengguna')

            response = requests.put(f"{self.base_url}/program-kerja-wr/{program_id}",
                                  json=data,
                                  timeout=self.timeout,
                                  headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f": {error_detail.get('data', e.response.text)}"
            except:
                error_msg += f": {e.response.text}"
            return {"success": False, "data": error_msg}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal update program kerja WR: {e}"}

    def delete_program_kerja_wr(self, program_id):
        """Delete program kerja WR"""
        try:
            params = {}
            if self.user_data:
                params['user_id'] = self.user_data.get('id_pengguna')

            response = requests.delete(f"{self.base_url}/program-kerja-wr/{program_id}",
                                     params=params,
                                     timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f": {error_detail.get('data', e.response.text)}"
            except:
                error_msg += f": {e.response.text}"
            return {"success": False, "data": error_msg}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal hapus program kerja WR: {e}"}

    def get_pengumuman(self):
        try:
            response = requests.get(f"{self.base_url}/pengumuman?active_only=true", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data pengumuman: {e}"}

    def add_pengumuman(self, data):
        try:
            response = requests.post(f"{self.base_url}/pengumuman", json=data, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menambahkan pengumuman: {e}"}

    def update_pengumuman(self, pengumuman_id, data):
        try:
            response = requests.put(f"{self.base_url}/pengumuman/{pengumuman_id}", json=data, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal update pengumuman: {e}"}

    def delete_pengumuman(self, pengumuman_id):
        try:
            response = requests.delete(f"{self.base_url}/pengumuman/{pengumuman_id}", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal hapus pengumuman: {e}"}

    def get_keuangan(self):
        try:
            if not self.user_data:
                return {"success": False, "data": "User not logged in"}

            user_id = self.user_data.get('id_pengguna')
            if not user_id:
                return {"success": False, "data": "User ID not found"}

            params = {'user_id': user_id}
            response = requests.get(f"{self.base_url}/keuangan/my", params=params, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data keuangan: {e}"}
    
    def add_keuangan(self, keuangan_data):
        try:
            data = {
                'tanggal': keuangan_data.get('tanggal'),
                'kategori': keuangan_data.get('jenis'),
                'sub_kategori': keuangan_data.get('kategori'),
                'keterangan': keuangan_data.get('keterangan'),  # Gunakan keterangan, BUKAN deskripsi
                'jumlah': keuangan_data.get('jumlah')
            }
            if self.user_data:
                data['user_id'] = self.user_data.get('id_pengguna')

            response = requests.post(f"{self.base_url}/keuangan",
                                   json=data,
                                   timeout=self.timeout,
                                   headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal menambah data keuangan: {e}"}
    
    def update_keuangan(self, keuangan_id, keuangan_data):
        try:
            response = requests.put(f"{self.base_url}/keuangan/{keuangan_id}", 
                                  json=keuangan_data, 
                                  timeout=self.timeout,
                                  headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal update data keuangan: {e}"}
    
    def delete_keuangan(self, keuangan_id):
        try:
            response = requests.delete(f"{self.base_url}/keuangan/{keuangan_id}", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal hapus data keuangan: {e}"}
    
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
            response = requests.get(f"{self.base_url}/dokumen/files", timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil daftar file: {e}"}
    
    def download_file(self, file_id):
        try:
            response = requests.get(f"{self.base_url}/dokumen/files/{file_id}/download",
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
    
    # ========== BROADCAST DATA METHODS (Client View) ==========
    def get_broadcast_jemaat(self):
        """Get jemaat data that has been broadcast by admin"""
        try:
            response = requests.get(f"{self.base_url}/broadcast/jemaat", 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data broadcast jemaat: {e}"}
    
    def get_broadcast_kegiatan(self):
        """Get kegiatan data that has been broadcast by admin"""
        try:
            response = requests.get(f"{self.base_url}/broadcast/kegiatan", 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data broadcast kegiatan: {e}"}
    
    def get_broadcast_keuangan(self):
        """Get keuangan data that has been broadcast by admin"""
        try:
            response = requests.get(f"{self.base_url}/broadcast/keuangan", 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data broadcast keuangan: {e}"}
    
    def get_broadcast_dokumen(self):
        """Get dokumen data that has been broadcast by admin"""
        try:
            response = requests.get(f"{self.base_url}/broadcast/dokumen", 
                                  timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengambil data broadcast dokumen: {e}"}
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        try:
            data = {
                "username": username,
                "old_password": old_password,
                "new_password": new_password
            }
            
            response = requests.post(f"{self.base_url}/change-password", 
                                   json=data,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            if result.get("status") == "success":
                return {"success": True, "data": result}
            else:
                return {"success": False, "data": result.get("message", "Gagal mengubah password")}
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "data": f"Gagal mengubah password: {e}"}
    
    def logout(self):
        """Logout user and clear session"""
        try:
            if self.session_id:
                data = {"session_id": self.session_id}
                response = requests.post(f"{self.base_url}/logout", 
                                       json=data,
                                       headers={'Content-Type': 'application/json'},
                                       timeout=self.timeout)
                response.raise_for_status()
            
            # Clear session data
            self.session_id = None
            return {"success": True, "data": "Logout berhasil"}
            
        except requests.exceptions.RequestException as e:
            # Even if logout request fails, clear local session
            self.session_id = None
            return {"success": True, "data": f"Logout selesai (warning: {e})"}