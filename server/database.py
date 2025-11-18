# Path: server/database.py

import logging
import datetime
from typing import Optional, Tuple, Dict, Any, List
from api_client import ApiClient

class DatabaseManager:

    def __init__(self):
        self.logger = logging.getLogger('DatabaseManager')
        self.api_client = ApiClient()
        self.connection = True  # Assume connected initially (lazy testing)

        # Local client sessions storage
        self.client_sessions = {}  # {session_id: session_data}
        self.active_sessions = {}  # {client_ip: session_data}

        # Don't test connection during init - test lazily when needed
    
    def _test_connection(self):
        """Test API connection (lazy - called on demand)"""
        try:
            result = self.api_client.check_server_connection()
            if result["success"]:
                self.connection = True
                self.logger.info("API connection successful")

                db_test = self.api_client.test_database()
                if db_test["success"]:
                    self.logger.info("Database API connection successful")
                else:
                    self.logger.error("Database API connection failed")
                    self.connection = False
            else:
                self.connection = False
                self.logger.error("API connection failed")
        except Exception as e:
            self.connection = False
            self.logger.error(f"Connection test error: {e}")
    
    def authenticate_admin(self, username: str, password: str) -> Tuple[bool, Any]:
        """Authenticate admin credentials"""
        try:
            login_data = {
                'username': username,
                'password': password
            }
            
            result = self.api_client.authenticate_admin(login_data)
            
            if result["success"]:
                api_response = result["data"]
                if api_response.get("status") == "success":
                    return True, api_response.get("admin")
                else:
                    return False, api_response.get("message", "Login gagal")
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error authenticating admin: {e}")
            return False, f"Error autentikasi: {str(e)}"
    
    def update_admin_last_login(self, admin_id: int) -> Tuple[bool, str]:
        """Update last login timestamp admin"""
        try:
            result = self.api_client.update_admin_last_login(admin_id)
            
            if result["success"]:
                return True, "Last login berhasil diupdate"
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error updating admin last login: {e}")
            return False, f"Error update last login: {str(e)}"
    
    def enable_api_service(self) -> Tuple[bool, str]:
        result = self.api_client.enable_api()
        if result["success"]:
            self.logger.info("API service enabled")
            import time
            time.sleep(1)
            status_result = self.get_api_service_status()
            if status_result[0] and status_result[1].get('api_enabled', False):
                return True, "API berhasil diaktifkan"
            else:
                return False, "API gagal diaktifkan - status tidak berubah"
        else:
            self.logger.error("Failed to enable API service")
            return False, result["data"]
    
    def disable_api_service(self) -> Tuple[bool, str]:
        result = self.api_client.disable_api()
        if result["success"]:
            self.logger.info("API service disabled")
            import time
            time.sleep(1)
            status_result = self.get_api_service_status()
            if status_result[0] and not status_result[1].get('api_enabled', True):
                return True, "API berhasil dinonaktifkan"
            else:
                return False, "API gagal dinonaktifkan - status tidak berubah"
        else:
            self.logger.error("Failed to disable API service")
            return False, result["data"]
    
    def get_api_service_status(self) -> Tuple[bool, Dict]:
        result = self.api_client.get_api_status()
        if result["success"]:
            return True, result["data"]
        else:
            return False, {"api_enabled": False, "message": result["data"]}
    
    def register_client_session(self, session_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Register client session"""
        try:
            session_id = session_data.get('session_id')
            client_ip = session_data.get('client_ip')
            
            if not session_id or not client_ip:
                return False, "Session ID dan Client IP diperlukan"
            
            # Simpan ke local storage
            session_data['last_activity'] = datetime.datetime.now().isoformat()
            session_data['status'] = 'active'
            
            self.client_sessions[session_id] = session_data
            self.active_sessions[client_ip] = session_data
            
            self.logger.info(f"Client session registered: {session_id} from {client_ip}")
            return True, "Session berhasil didaftarkan"
            
        except Exception as e:
            self.logger.error(f"Error registering client session: {e}")
            return False, f"Error registrasi session: {str(e)}"
    
    def update_client_activity(self, session_id: str, client_ip: str) -> Tuple[bool, str]:
        """Update client activity timestamp"""
        try:
            current_time = datetime.datetime.now().isoformat()
            
            # Update di session storage
            if session_id in self.client_sessions:
                self.client_sessions[session_id]['last_activity'] = current_time
                self.client_sessions[session_id]['status'] = 'active'
            
            if client_ip in self.active_sessions:
                self.active_sessions[client_ip]['last_activity'] = current_time
                self.active_sessions[client_ip]['status'] = 'active'
            
            return True, "Activity updated"
            
        except Exception as e:
            self.logger.error(f"Error updating client activity: {e}")
            return False, f"Error update activity: {str(e)}"
    
    def remove_client_session(self, session_id: str, client_ip: str) -> Tuple[bool, str]:
        """Remove client session"""
        try:
            # Hapus dari local storage
            if session_id in self.client_sessions:
                del self.client_sessions[session_id]
            
            if client_ip in self.active_sessions:
                del self.active_sessions[client_ip]
            
            self.logger.info(f"Client session removed: {session_id} from {client_ip}")
            return True, "Session berhasil dihapus"
            
        except Exception as e:
            self.logger.error(f"Error removing client session: {e}")
            return False, f"Error hapus session: {str(e)}"
    
    def get_active_sessions(self) -> Tuple[bool, Any]:
        """Ambil daftar client yang aktif - prioritas API untuk data real-time"""
        try:
            # Prioritas: Ambil dari API untuk data real-time dari database
            result = self.api_client.get_active_sessions()
            if result["success"]:
                api_data = result["data"]
                # Response format dari API: {'status': 'success', 'data': [...], 'timeout_disconnected': N}
                if isinstance(api_data, dict) and "data" in api_data:
                    api_sessions = api_data.get("data", [])
                    self.logger.info(f"API returned {len(api_sessions)} active sessions")
                    return True, api_sessions
                else:
                    # Fallback jika format berbeda (sudah list)
                    return True, api_data if isinstance(api_data, list) else []

            # Jika API gagal, gunakan local sessions sebagai fallback
            # Bersihkan session yang sudah tidak aktif (> 5 menit)
            current_time = datetime.datetime.now()
            expired_sessions = []

            for session_id, session_data in self.client_sessions.items():
                try:
                    last_activity_str = session_data.get('last_activity', '')
                    if last_activity_str:
                        last_activity = datetime.datetime.fromisoformat(last_activity_str.replace('Z', '+00:00'))
                        if (current_time - last_activity).total_seconds() > 300:  # 5 menit
                            expired_sessions.append((session_id, session_data.get('client_ip')))
                except:
                    expired_sessions.append((session_id, session_data.get('client_ip')))

            # Hapus session yang expired
            for session_id, client_ip in expired_sessions:
                self.remove_client_session(session_id, client_ip or '')

            # Return active sessions dari local storage
            active_sessions = list(self.client_sessions.values())
            self.logger.warning(f"API fallback: Returning {len(active_sessions)} local active sessions")
            return True, active_sessions

        except Exception as e:
            self.logger.error(f"Error getting active sessions: {e}")
            return False, []
    
    def send_broadcast_message(self, message: str) -> Tuple[bool, Any]:
        """Kirim broadcast message ke semua client melalui API"""
        try:
            result = self.api_client.send_broadcast_message(message)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error sending broadcast message: {e}")
            return False, str(e)
    
    # ========== JEMAAT METHODS ==========
    def get_jemaat_list(self, limit: int = 100, offset: int = 0, search: Optional[str] = None) -> Tuple[bool, Any]:
        result = self.api_client.get_jemaat()
        if result["success"]:
            data = result["data"] if isinstance(result["data"], list) else result["data"].get("data", [])

            if search:
                filtered_data = []
                search_lower = search.lower()
                for item in data:
                    if (search_lower in str(item.get('nama_lengkap', '')).lower() or
                        search_lower in str(item.get('alamat', '')).lower() or
                        search_lower in str(item.get('no_telepon', '')).lower() or
                        search_lower in str(item.get('email', '')).lower() or
                        search_lower in str(item.get('wilayah_rohani', '')).lower() or
                        search_lower in str(item.get('nama_keluarga', '')).lower() or
                        search_lower in str(item.get('tempat_lahir', '')).lower() or
                        search_lower in str(item.get('hubungan_keluarga', '')).lower() or
                        search_lower in str(item.get('status_keanggotaan', '')).lower()):
                        filtered_data.append(item)
                data = filtered_data
            
            start = offset
            end = offset + limit
            return True, data[start:end]
        else:
            return False, result["data"]
    
    def add_jemaat(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.add_jemaat(data)
        if result["success"]:
            # Handle both nested dict and direct id format
            data_obj = result["data"]
            id_value = data_obj.get("id", 0) if isinstance(data_obj, dict) else 0
            return True, id_value
        else:
            return False, result["data"]
    
    def update_jemaat(self, id_jemaat: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.update_jemaat(id_jemaat, data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    def delete_jemaat(self, id_jemaat: int) -> Tuple[bool, Any]:
        result = self.api_client.delete_jemaat(id_jemaat)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    # ========== KEGIATAN METHODS ==========
    def get_kegiatan_list(self, start_date: Optional[datetime.date] = None, 
                         end_date: Optional[datetime.date] = None, 
                         limit: int = 100, offset: int = 0) -> Tuple[bool, Any]:
        result = self.api_client.get_kegiatan()
        if result["success"]:
            data = result["data"].get("data", [])
            
            # Filter berdasarkan tanggal jika ada
            if start_date or end_date:
                filtered_data = []
                for item in data:
                    tanggal_mulai = item.get('tanggal_mulai')
                    if tanggal_mulai:
                        try:
                            if isinstance(tanggal_mulai, str):
                                item_date = datetime.datetime.strptime(tanggal_mulai, '%Y-%m-%d').date()
                            else:
                                item_date = tanggal_mulai.date() if hasattr(tanggal_mulai, 'date') else tanggal_mulai
                            
                            if start_date and item_date < start_date:
                                continue
                            if end_date and item_date > end_date:
                                continue
                            
                            filtered_data.append(item)
                        except:
                            continue
                data = filtered_data
            
            start = offset
            end = offset + limit
            return True, data[start:end]
        else:
            return False, result["data"]
    
    def add_kegiatan(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.add_kegiatan(data)
        if result["success"]:
            return True, result["data"].get("id", 0)
        else:
            return False, result["data"]
    
    def update_kegiatan(self, id_kegiatan: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.update_kegiatan(id_kegiatan, data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    def delete_kegiatan(self, id_kegiatan: int) -> Tuple[bool, Any]:
        result = self.api_client.delete_kegiatan(id_kegiatan)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    def get_kegiatan_wr_list(self) -> Tuple[bool, Any]:
        """Get kegiatan WR list from all clients with user information"""
        result = self.api_client.get_kegiatan_wr()
        if result["success"]:
            data = result["data"]
            if isinstance(data, dict) and "data" in data:
                return True, data["data"]
            elif isinstance(data, list):
                return True, data
            else:
                return True, []
        else:
            return False, result["data"]

    # ========== PENGUMUMAN METHODS ==========
    def get_pengumuman_list(self, active_only: bool = True, 
                           limit: int = 10, offset: int = 0) -> Tuple[bool, Any]:
        result = self.api_client.get_pengumuman()
        if result["success"]:
            data = result["data"].get("data", [])
            
            # Filter active only jika diperlukan
            if active_only:
                today = datetime.date.today()
                filtered_data = []
                for item in data:
                    tanggal_mulai = item.get('tanggal_mulai')
                    tanggal_selesai = item.get('tanggal_selesai')
                    is_active = item.get('is_active', True)
                    
                    if not is_active:
                        continue
                    
                    try:
                        if tanggal_mulai and tanggal_selesai:
                            if isinstance(tanggal_mulai, str):
                                start_date = datetime.datetime.strptime(tanggal_mulai, '%Y-%m-%d').date()
                            else:
                                start_date = tanggal_mulai.date() if hasattr(tanggal_mulai, 'date') else tanggal_mulai
                            
                            if isinstance(tanggal_selesai, str):
                                end_date = datetime.datetime.strptime(tanggal_selesai, '%Y-%m-%d').date()
                            else:
                                end_date = tanggal_selesai.date() if hasattr(tanggal_selesai, 'date') else tanggal_selesai
                            
                            if start_date <= today <= end_date:
                                filtered_data.append(item)
                        else:
                            filtered_data.append(item)
                    except:
                        filtered_data.append(item)
                
                data = filtered_data
            
            start = offset
            end = offset + limit
            return True, data[start:end]
        else:
            return False, result["data"]
    
    def add_pengumuman(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.add_pengumuman(data)
        if result["success"]:
            return True, result["data"].get("id", 0)
        else:
            return False, result["data"]
    
    def update_pengumuman(self, id_pengumuman: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.update_pengumuman(id_pengumuman, data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    def delete_pengumuman(self, id_pengumuman: int) -> Tuple[bool, Any]:
        result = self.api_client.delete_pengumuman(id_pengumuman)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    # ========== KEUANGAN METHODS ==========
    def get_keuangan_list(self, category: Optional[str] = None, 
                         limit: int = 100, offset: int = 0) -> Tuple[bool, Any]:
        result = self.api_client.get_keuangan()
        if result["success"]:
            data = result["data"].get("data", [])
            
            if category:
                filtered_data = [item for item in data if item.get('kategori') == category]
                data = filtered_data
            
            start = offset
            end = offset + limit
            return True, data[start:end]
        else:
            return False, result["data"]
    
    def add_keuangan(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.add_keuangan(data)
        if result["success"]:
            return True, result["data"].get("id", 0)
        else:
            return False, result["data"]
    
    def update_keuangan(self, id_keuangan: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.update_keuangan(id_keuangan, data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    def delete_keuangan(self, id_keuangan: int) -> Tuple[bool, Any]:
        result = self.api_client.delete_keuangan(id_keuangan)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    # ========== KEUANGAN KATEGORIAL METHODS ==========
    def get_keuangan_kategorial_list(self, jenis: Optional[str] = None,
                                     limit: int = 100, offset: int = 0) -> Tuple[bool, Any]:
        """Get all keuangan_kategorial records with optional filtering"""
        result = self.api_client.get_keuangan_kategorial()
        if result["success"]:
            data = result["data"].get("data", [])

            if jenis:
                filtered_data = [item for item in data if item.get('jenis') == jenis]
                data = filtered_data

            start = offset
            end = offset + limit
            return True, data[start:end]
        else:
            return False, result["data"]

    def add_keuangan_kategorial(self, data: Dict[str, Any], admin_id: int = None) -> Tuple[bool, Any]:
        """Add new keuangan_kategorial record"""
        result = self.api_client.add_keuangan_kategorial(data, admin_id)
        if result["success"]:
            return True, result["data"].get("id", 0)
        else:
            return False, result["data"]

    def update_keuangan_kategorial(self, id_keuangan: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Update existing keuangan_kategorial record"""
        result = self.api_client.update_keuangan_kategorial(id_keuangan, data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    def delete_keuangan_kategorial(self, id_keuangan: int) -> Tuple[bool, Any]:
        """Delete keuangan_kategorial record"""
        result = self.api_client.delete_keuangan_kategorial(id_keuangan)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    # ========== FILES METHODS ==========
    def get_files_list(self) -> Tuple[bool, Any]:
        result = self.api_client.get_files()
        if result["success"]:
            return True, result["data"].get("data", [])
        else:
            return False, result["data"]
    
    def upload_file(self, file_path: str, document_name: str = None, document_type: str = None, keterangan: str = None, kategori: str = None) -> Tuple[bool, Any]:
        result = self.api_client.upload_file(file_path, document_name, document_type, keterangan, kategori)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    def delete_file(self, file_id: int) -> Tuple[bool, Any]:
        result = self.api_client.delete_file(file_id)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    # ========== PESAN METHODS ==========
    def get_recent_messages(self, limit: int = 50) -> Tuple[bool, Any]:
        """Ambil pesan terbaru melalui API"""
        try:
            result = self.api_client.get_recent_messages(limit)
            if result["success"]:
                return True, result["data"].get("data", [])
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting recent messages: {e}")
            return False, str(e)
    
    def send_message(self, pengirim_admin: Optional[int], pesan: str, 
                    is_broadcast: bool = True, target: Optional[str] = None) -> Tuple[bool, Any]:
        """Kirim pesan melalui API"""
        try:
            message_data = {
                'pengirim_admin': pengirim_admin,
                'pesan': pesan,
                'is_broadcast': is_broadcast,
                'target': target
            }
            result = self.api_client.send_message(message_data)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False, str(e)

    # ========== LEGACY METHODS ==========
    def execute_query(self, query: str, params: Optional[tuple] = None, 
                     fetch: bool = False, commit: bool = True) -> Tuple[bool, Any]:
        """Legacy method untuk compatibility dengan komponen lama"""
        return True, "API mode - use specific methods"
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Any]:
        """Authenticate user credentials untuk client"""
        return True, {"id_pengguna": 1, "username": username, "nama_lengkap": "User", "peran": "user"}
    
    def register_session(self, ip_address: str, hostname: str, user_id: Optional[int] = None) -> Tuple[bool, Any]:
        """Register client session"""
        return True, 1
    
    def update_session_status(self, ip_address: str, status: str = 'Disconnected') -> Tuple[bool, Any]:
        """Update client session status"""
        return True, 1
    
    def save_message(self, pengirim_id: Optional[int], pesan: str, 
                    is_broadcast: bool = True, target: Optional[str] = None) -> Tuple[bool, Any]:
        """Save message"""
        return True, 1
    
    def get_dashboard_statistics(self) -> Tuple[bool, Any]:
        """Get dashboard statistics"""
        statistics = {
            'total_jemaat': 0,
            'total_kegiatan_bulan_ini': 0,
            'total_pengumuman_aktif': 0,
            'sesi_aktif': 0
        }
        
        jemaat_result = self.get_jemaat_list()
        if jemaat_result[0]:
            statistics['total_jemaat'] = len(jemaat_result[1])
        
        kegiatan_result = self.get_kegiatan_list()
        if kegiatan_result[0]:
            statistics['total_kegiatan_bulan_ini'] = len(kegiatan_result[1])
        
        pengumuman_result = self.get_pengumuman_list()
        if pengumuman_result[0]:
            statistics['total_pengumuman_aktif'] = len(pengumuman_result[1])
        
        return True, statistics
    
    def get_saldo_total(self) -> Tuple[bool, Any]:
        """Calculate total saldo from keuangan data"""
        try:
            pemasukan_result = self.get_keuangan_list(category="Pemasukan")
            pengeluaran_result = self.get_keuangan_list(category="Pengeluaran")
            
            total_pemasukan = 0
            total_pengeluaran = 0
            
            if pemasukan_result[0]:
                for item in pemasukan_result[1]:
                    total_pemasukan += float(item.get('jumlah', 0))
            
            if pengeluaran_result[0]:
                for item in pengeluaran_result[1]:
                    total_pengeluaran += float(item.get('jumlah', 0))
            
            saldo = total_pemasukan - total_pengeluaran
            
            return True, {
                'total_pemasukan': total_pemasukan,
                'total_pengeluaran': total_pengeluaran, 
                'saldo': saldo
            }
        except Exception as e:
            self.logger.error(f"Error calculating saldo: {e}")
            return False, str(e)
    
    def get_saldo_keuangan_bulanan(self, year: int, month: int) -> Tuple[bool, Any]:
        """Calculate monthly saldo from keuangan data"""
        try:
            result = self.get_keuangan_list()
            if not result[0]:
                return False, result[1]
            
            data = result[1]
            total_pemasukan = 0
            total_pengeluaran = 0
            
            for item in data:
                tanggal_str = item.get('tanggal', '')
                try:
                    if isinstance(tanggal_str, str):
                        tanggal = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00'))
                    else:
                        tanggal = tanggal_str
                    
                    if tanggal.year == year and tanggal.month == month:
                        if item.get('kategori') == 'Pemasukan':
                            total_pemasukan += float(item.get('jumlah', 0))
                        elif item.get('kategori') == 'Pengeluaran':
                            total_pengeluaran += float(item.get('jumlah', 0))
                except:
                    continue
            
            return True, [{
                'total_pemasukan': total_pemasukan,
                'total_pengeluaran': total_pengeluaran,
                'saldo_bulan': total_pemasukan - total_pengeluaran
            }]
        except Exception as e:
            self.logger.error(f"Error calculating monthly saldo: {e}")
            return False, str(e)
    
    # ========== LOG METHODS ==========
    def get_log_activities(self, limit: int = 100) -> Tuple[bool, Any]:
        """Ambil log aktivitas"""
        try:
            result = self.api_client.get_log_activities(limit)
            if result["success"]:
                return True, result["data"].get("data", [])
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting log activities: {e}")
            return False, str(e)

    def add_log_activity(self, id_admin: Optional[int], aktivitas: str, detail: str, ip_address: Optional[str] = None) -> Tuple[bool, Any]:
        """Add log activity"""
        try:
            log_data = {
                'id_admin': id_admin,
                'aktivitas': aktivitas,
                'detail': detail,
                'ip_address': ip_address or "127.0.0.1"
            }
            
            result = self.api_client.add_log_activity(log_data)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error adding log activity: {e}")
            return False, str(e)
    
    def get_recent_activities(self, limit: int = 50, hours: int = 24) -> Tuple[bool, Any]:
        """Get recent activities"""
        try:
            result = self.api_client.get_recent_activities(limit, hours)
            if result["success"]:
                return True, result["data"].get("data", [])
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting recent activities: {e}")
            return False, str(e)
    
    def get_admin_activities(self, admin_id: int, limit: int = 100) -> Tuple[bool, Any]:
        """Get admin activities"""
        try:
            result = self.api_client.get_admin_activities(admin_id, limit)
            if result["success"]:
                return True, result["data"].get("data", [])
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting admin activities: {e}")
            return False, str(e)
    
    def download_file_from_api(self, file_id: int) -> Tuple[bool, Any]:
        """Download file dari API"""
        try:
            result = self.api_client.download_file(file_id)
            if result["success"]:
                # result["data"] should already be bytes from response.content
                file_content = result["data"]
                headers = result.get("headers", {})
                
                return True, {
                    'content': file_content,
                    'headers': headers,
                    'content_type': headers.get('content-type', '') if headers else ''
                }
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error downloading file: {e}")
            return False, str(e)
    
    # ========== STRUKTUR METHODS ==========
    def get_struktur_list(self, search: Optional[str] = None) -> Tuple[bool, Any]:
        result = self.api_client.get_struktur()
        if result["success"]:
            data = result["data"].get("data", [])
            
            if search:
                filtered_data = []
                search_lower = search.lower()
                for item in data:
                    if (search_lower in str(item.get('nama_lengkap', '')).lower() or
                        search_lower in str(item.get('jabatan_utama', '')).lower() or
                        search_lower in str(item.get('bidang_pelayanan', '')).lower() or
                        search_lower in str(item.get('wilayah_rohani', '')).lower() or
                        search_lower in str(item.get('status_klerus', '')).lower() or
                        search_lower in str(item.get('gelar_depan', '')).lower() or
                        search_lower in str(item.get('gelar_belakang', '')).lower()):
                        filtered_data.append(item)
                data = filtered_data
            
            return True, data
        else:
            return False, result["data"]
    
    def add_struktur(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.add_struktur(data)
        if result["success"]:
            return True, result["data"].get("id", 0)
        else:
            return False, result["data"]
    
    def update_struktur(self, id_struktur: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.update_struktur(id_struktur, data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    def delete_struktur(self, id_struktur: int) -> Tuple[bool, Any]:
        result = self.api_client.delete_struktur(id_struktur)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    def upload_struktur_photo(self, struktur_id: int, photo_path: str) -> Tuple[bool, Any]:
        """Upload foto untuk struktur yang sudah ada"""
        try:
            result = self.api_client.upload_struktur_photo(struktur_id, photo_path)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error uploading struktur photo: {e}")
            return False, str(e)
    
    def upload_struktur_photo_new(self, photo_path: str) -> Tuple[bool, Any]:
        """Upload foto untuk struktur baru"""
        try:
            result = self.api_client.upload_struktur_photo_new(photo_path)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error uploading new struktur photo: {e}")
            return False, str(e)

    # ========== KATEGORIAL METHODS ==========
    def get_kategorial_list(self, search: Optional[str] = None) -> Tuple[bool, Any]:
        """Get list of kategorial (komunitas kategorial)"""
        result = self.api_client.get_kategorial()
        if result["success"]:
            data = result["data"].get("data", [])

            if search:
                filtered_data = []
                search_lower = search.lower()
                for item in data:
                    if (search_lower in str(item.get('nama_lengkap', '')).lower() or
                        search_lower in str(item.get('jabatan', '')).lower() or
                        search_lower in str(item.get('kelompok_kategorial', '')).lower() or
                        search_lower in str(item.get('wilayah_rohani', '')).lower() or
                        search_lower in str(item.get('email', '')).lower() or
                        search_lower in str(item.get('no_hp', '')).lower() or
                        search_lower in str(item.get('status', '')).lower()):
                        filtered_data.append(item)
                data = filtered_data

            return True, data
        else:
            return False, result["data"]

    def add_kategorial(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Add new kategorial pengurus"""
        result = self.api_client.add_kategorial(data)
        if result["success"]:
            return True, result["data"].get("id", 0)
        else:
            return False, result["data"]

    def update_kategorial(self, id_kategorial: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Update kategorial pengurus"""
        result = self.api_client.update_kategorial(id_kategorial, data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    def delete_kategorial(self, id_kategorial: int) -> Tuple[bool, Any]:
        """Delete kategorial pengurus"""
        result = self.api_client.delete_kategorial(id_kategorial)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    # ========== WILAYAH ROHANI METHODS ==========
    def get_wr_list(self, search: Optional[str] = None) -> Tuple[bool, Any]:
        """Get all Wilayah Rohani pengurus"""
        result = self.api_client.get_wr()
        if result["success"]:
            data = result["data"].get("data", [])

            if search:
                filtered_data = []
                search_lower = search.lower()
                for item in data:
                    if (search_lower in str(item.get('nama_lengkap', '')).lower() or
                        search_lower in str(item.get('jabatan', '')).lower() or
                        search_lower in str(item.get('wilayah_rohani', '')).lower() or
                        search_lower in str(item.get('email', '')).lower() or
                        search_lower in str(item.get('no_hp', '')).lower() or
                        search_lower in str(item.get('status', '')).lower()):
                        filtered_data.append(item)
                return True, filtered_data

            return True, data
        else:
            return False, result["data"]

    def add_wr(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Add new Wilayah Rohani pengurus"""
        result = self.api_client.add_wr(data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    def update_wr(self, id_wilayah: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Update Wilayah Rohani pengurus"""
        result = self.api_client.update_wr(id_wilayah, data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    def delete_wr(self, id_wilayah: int) -> Tuple[bool, Any]:
        """Delete Wilayah Rohani pengurus"""
        result = self.api_client.delete_wr(id_wilayah)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    # ========== K. BINAAN METHODS ==========
    def get_binaan_list(self, search: Optional[str] = None) -> Tuple[bool, Any]:
        """Get all Kelompok Binaan pengurus"""
        result = self.api_client.get_binaan()
        if result["success"]:
            data = result["data"].get("data", [])

            if search:
                filtered_data = []
                search_lower = search.lower()
                for item in data:
                    if (search_lower in str(item.get('nama_lengkap', '')).lower() or
                        search_lower in str(item.get('jabatan', '')).lower() or
                        search_lower in str(item.get('kelompok_binaan', '')).lower() or
                        search_lower in str(item.get('email', '')).lower() or
                        search_lower in str(item.get('no_hp', '')).lower() or
                        search_lower in str(item.get('wilayah_rohani', '')).lower() or
                        search_lower in str(item.get('status', '')).lower()):
                        filtered_data.append(item)
                return True, filtered_data

            return True, data
        else:
            return False, result["data"]

    def add_binaan(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Add new Kelompok Binaan pengurus"""
        result = self.api_client.add_binaan(data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    def update_binaan(self, id_binaan: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Update Kelompok Binaan pengurus"""
        result = self.api_client.update_binaan(id_binaan, data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    def delete_binaan(self, id_binaan: int) -> Tuple[bool, Any]:
        """Delete Kelompok Binaan pengurus"""
        result = self.api_client.delete_binaan(id_binaan)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]

    # ========== INVENTARIS METHODS ==========
    def get_inventaris_list(self, search: Optional[str] = None, kategori: Optional[str] = None, 
                           kondisi: Optional[str] = None, lokasi: Optional[str] = None) -> Tuple[bool, Any]:
        result = self.api_client.get_inventaris()
        if result["success"]:
            data = result["data"].get("data", [])
            
            if search:
                filtered_data = []
                search_lower = search.lower()
                for item in data:
                    if (search_lower in str(item.get('kode_barang', '')).lower() or
                        search_lower in str(item.get('nama_barang', '')).lower() or
                        search_lower in str(item.get('merk', '')).lower() or
                        search_lower in str(item.get('supplier', '')).lower() or
                        search_lower in str(item.get('penanggung_jawab', '')).lower() or
                        search_lower in str(item.get('lokasi', '')).lower()):
                        filtered_data.append(item)
                data = filtered_data
            
            if kategori:
                data = [item for item in data if item.get('kategori') == kategori]
            
            if kondisi:
                data = [item for item in data if item.get('kondisi') == kondisi]
                
            if lokasi:
                data = [item for item in data if item.get('lokasi') == lokasi]
            
            return True, data
        else:
            return False, result["data"]
    
    def add_inventaris(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.add_inventaris(data)
        if result["success"]:
            return True, result["data"].get("id", 0)
        else:
            return False, result["data"]
    
    def update_inventaris(self, id_inventaris: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        result = self.api_client.update_inventaris(id_inventaris, data)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    def delete_inventaris(self, id_inventaris: int) -> Tuple[bool, Any]:
        result = self.api_client.delete_inventaris(id_inventaris)
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    def get_inventaris_statistics(self) -> Tuple[bool, Any]:
        result = self.api_client.get_inventaris_statistics()
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    def get_inventaris_categories(self) -> Tuple[bool, Any]:
        result = self.api_client.get_inventaris_categories()
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    def get_inventaris_locations(self) -> Tuple[bool, Any]:
        result = self.api_client.get_inventaris_locations()
        if result["success"]:
            return True, result["data"]
        else:
            return False, result["data"]
    
    # ========== PROGRAM KERJA METHODS ==========
    def get_program_kerja_list(self, search: Optional[str] = None, month: Optional[str] = None, 
                              year: Optional[str] = None) -> Tuple[bool, Any]:
        """Get program kerja list with optional filters"""
        try:
            result = self.api_client.get_program_kerja(search=search, month=month, year=year)
            if result["success"]:
                return True, result["data"].get("data", [])
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting program kerja list: {e}")
            return False, str(e)
    
    def add_program_kerja(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Add new program kerja"""
        try:
            # Convert dialog data format to API format
            # Dialog sends: title, target, responsible, budget_amount, budget_source, category, month, keterangan
            # API expects: estimasi_waktu, judul, sasaran, penanggung_jawab, anggaran, sumber_anggaran, kategori, keterangan
            api_data = {
                'estimasi_waktu': data.get('month', ''),  # month from dialog
                'judul': data.get('title', ''),  # title from dialog
                'sasaran': data.get('target', ''),
                'penanggung_jawab': data.get('responsible', ''),
                'anggaran': data.get('budget_amount', ''),
                'sumber_anggaran': data.get('budget_source', 'Kas Gereja'),
                'kategori': data.get('category', ''),
                'keterangan': data.get('keterangan', '')  # keterangan from dialog
            }

            result = self.api_client.add_program_kerja(api_data)
            if result["success"]:
                return True, result["data"].get("id", 0)
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error adding program kerja: {e}")
            return False, str(e)
    
    def update_program_kerja(self, program_id: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Update program kerja"""
        try:
            # Convert dialog data format to API format
            # Dialog sends: title, target, responsible, budget_amount, budget_source, category, month, keterangan
            # API expects: estimasi_waktu, judul, sasaran, penanggung_jawab, anggaran, sumber_anggaran, kategori, keterangan
            api_data = {
                'estimasi_waktu': data.get('month', ''),  # month from dialog
                'judul': data.get('title', ''),  # title from dialog
                'sasaran': data.get('target', ''),
                'penanggung_jawab': data.get('responsible', ''),
                'anggaran': data.get('budget_amount', ''),
                'sumber_anggaran': data.get('budget_source', 'Kas Gereja'),
                'kategori': data.get('category', ''),
                'keterangan': data.get('keterangan', '')  # keterangan from dialog
            }

            result = self.api_client.update_program_kerja(program_id, api_data)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error updating program kerja: {e}")
            return False, str(e)
    
    def delete_program_kerja(self, program_id: int) -> Tuple[bool, Any]:
        """Delete program kerja"""
        try:
            result = self.api_client.delete_program_kerja(program_id)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error deleting program kerja: {e}")
            return False, str(e)
    
    def get_program_kerja_statistics(self) -> Tuple[bool, Any]:
        """Get program kerja statistics"""
        try:
            result = self.api_client.get_program_statistics()
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting program kerja statistics: {e}")
            return False, str(e)

    # ========== PROGRAM KERJA WR METHODS ==========
    def get_program_kerja_wr_list(self, search: Optional[str] = None, wilayah_id: Optional[int] = None) -> Tuple[bool, Any]:
        """Get list of all program kerja WR"""
        try:
            result = self.api_client.get_program_kerja_wr_list(search, wilayah_id)
            if result["success"]:
                return True, result["data"].get("data", [])
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting program kerja WR list: {e}")
            return False, str(e)

    def get_program_kerja_dpp_list(self, search: Optional[str] = None, month: Optional[str] = None) -> Tuple[bool, Any]:
        """Get list of all program kerja DPP"""
        try:
            result = self.api_client.get_program_kerja_dpp_list(search, month)
            if result["success"]:
                return True, result["data"].get("data", [])
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting program kerja DPP list: {e}")
            return False, str(e)

    # ========== USER MANAGEMENT METHODS ==========
    def get_users_list(self) -> Tuple[bool, Any]:
        """Get list of all admin users"""
        try:
            result = self.api_client.get_users()
            if result["success"]:
                return True, result["data"].get("data", [])
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting users list: {e}")
            return False, str(e)
    
    def create_user(self, user_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Create new admin user"""
        try:
            result = self.api_client.create_user(user_data)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return False, str(e)
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Update existing admin user"""
        try:
            result = self.api_client.update_user(user_id, user_data)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error updating user: {e}")
            return False, str(e)
    
    def delete_user(self, user_id: int) -> Tuple[bool, Any]:
        """Delete admin user"""
        try:
            result = self.api_client.delete_user(user_id)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error deleting user: {e}")
            return False, str(e)
    
    def get_tim_pembina(self) -> Tuple[bool, Any]:
        """Get all tim pembina with peserta"""
        try:
            result = self.api_client.get_tim_pembina()
            if result.get('success'):
                return True, {'success': True, 'data': result.get('data', [])}
            else:
                return False, result.get('data', 'Error getting tim pembina')
        except Exception as e:
            self.logger.error(f"Error getting tim pembina: {e}")
            return False, str(e)

    def add_tim_pembina(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Add new tim pembina"""
        try:
            result = self.api_client.add_tim_pembina(data)
            if result.get('success'):
                return True, {'success': True, 'data': result.get('data', {})}
            else:
                return False, result.get('data', 'Error adding tim pembina')
        except Exception as e:
            self.logger.error(f"Error adding tim pembina: {e}")
            return False, str(e)

    def update_tim_pembina(self, tim_id: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Update tim pembina"""
        try:
            result = self.api_client.update_tim_pembina(tim_id, data)
            if result.get('success'):
                return True, {'success': True, 'data': result.get('data', {})}
            else:
                return False, result.get('data', 'Error updating tim pembina')
        except Exception as e:
            self.logger.error(f"Error updating tim pembina: {e}")
            return False, str(e)

    def add_tim_pembina_peserta(self, tim_id: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Add peserta to tim pembina (old method - deprecated)"""
        try:
            result = self.api_client.add_tim_pembina_peserta(tim_id, data)
            if result.get('success'):
                return True, {'success': True, 'data': result.get('data', {})}
            else:
                return False, result.get('data', 'Error adding peserta')
        except Exception as e:
            self.logger.error(f"Error adding peserta: {e}")
            return False, str(e)

    def get_tim_pembina_peserta(self) -> Tuple[bool, Any]:
        """Get all peserta from tim_pembina table (new single-table approach)"""
        try:
            result = self.api_client.get_tim_pembina_peserta()
            if result.get('success'):
                return True, {'success': True, 'data': result.get('data', [])}
            else:
                return False, result.get('data', 'Error getting tim pembina peserta')
        except Exception as e:
            self.logger.error(f"Error getting tim pembina peserta: {e}")
            return False, str(e)

    def add_tim_pembina_peserta_new(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Add new peserta to tim_pembina table (new single-table approach)"""
        try:
            result = self.api_client.add_tim_pembina_peserta_new(data)
            if result.get('success'):
                return True, {'success': True, 'data': result.get('data', {})}
            else:
                return False, result.get('data', 'Error adding peserta')
        except Exception as e:
            self.logger.error(f"Error adding peserta: {e}")
            return False, str(e)

    def update_tim_pembina_peserta(self, peserta_id: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Update peserta in tim_pembina table (new single-table approach)"""
        try:
            result = self.api_client.update_tim_pembina_peserta(peserta_id, data)
            if result.get('success'):
                return True, {'success': True, 'data': result.get('data', {})}
            else:
                return False, result.get('data', 'Error updating peserta')
        except Exception as e:
            self.logger.error(f"Error updating peserta: {e}")
            return False, str(e)

    def delete_tim_pembina_peserta(self, peserta_id: int) -> Tuple[bool, Any]:
        """Delete peserta from tim_pembina table (old method - deprecated)"""
        try:
            result = self.api_client.delete_tim_pembina_peserta(peserta_id)
            if result.get('success'):
                return True, {'success': True, 'data': result.get('data', {})}
            else:
                return False, result.get('data', 'Error deleting peserta')
        except Exception as e:
            self.logger.error(f"Error deleting peserta: {e}")
            return False, str(e)

    def delete_tim_pembina_peserta_new(self, peserta_id: int) -> Tuple[bool, Any]:
        """Delete peserta from tim_pembina table (new single-table approach)"""
        try:
            result = self.api_client.delete_tim_pembina_peserta_new(peserta_id)
            if result.get('success'):
                return True, {'success': True, 'data': result.get('data', {})}
            else:
                return False, result.get('data', 'Error deleting peserta')
        except Exception as e:
            self.logger.error(f"Error deleting peserta: {e}")
            return False, str(e)

    def search_jemaat_by_nama(self, keyword: str) -> Tuple[bool, Any]:
        """Search jemaat by nama"""
        try:
            # Try to get from jemaat data or API
            success, response = self.api_client.get_jemaat()
            if success:
                # Filter results to only include matches
                if isinstance(response, list):
                    filtered = [j for j in response if keyword.lower() in j.get('nama_lengkap', '').lower()]
                    return True, {'success': True, 'data': filtered}
                elif isinstance(response, dict) and 'data' in response:
                    filtered = [j for j in response['data'] if keyword.lower() in j.get('nama_lengkap', '').lower()]
                    return True, {'success': True, 'data': filtered}
            return False, {'success': False, 'data': []}
        except Exception as e:
            self.logger.error(f"Error searching jemaat: {e}")
            return False, str(e)

    def get_aset_list(self, search: Optional[str] = None, kategori: Optional[str] = None,
                      kondisi: Optional[str] = None, status: Optional[str] = None) -> Tuple[bool, Any]:
        """Get list of aset (Asset management - upgraded from inventaris)"""
        try:
            result = self.api_client.get_aset()
            if result["success"]:
                data = result["data"]
                # Apply client-side filtering if needed
                if search or kategori or kondisi or status:
                    filtered = data
                    if isinstance(data, dict) and 'data' in data:
                        filtered = data['data']
                    elif isinstance(data, list):
                        filtered = data
                    else:
                        filtered = []

                    if search:
                        filtered = [x for x in filtered if search.lower() in str(x.get('nama_aset', '')).lower()]
                    if kategori:
                        filtered = [x for x in filtered if x.get('kategori') == kategori]
                    if kondisi:
                        filtered = [x for x in filtered if x.get('kondisi') == kondisi]
                    if status:
                        filtered = [x for x in filtered if x.get('status') == status]

                    return True, filtered if isinstance(data, list) else {'data': filtered}
                return True, data
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting aset list: {e}")
            return False, str(e)

    def add_aset(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Add new aset"""
        try:
            result = self.api_client.add_aset(data)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error adding aset: {e}")
            return False, str(e)

    def update_aset(self, id_aset: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Update aset"""
        try:
            result = self.api_client.update_aset(id_aset, data)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error updating aset: {e}")
            return False, str(e)

    def delete_aset(self, id_aset: int) -> Tuple[bool, Any]:
        """Delete aset"""
        try:
            result = self.api_client.delete_aset(id_aset)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error deleting aset: {e}")
            return False, str(e)

    # ========== BUKU KRONIK METHODS ==========
    def get_buku_kronik_list(self) -> Tuple[bool, Any]:
        """Get buku kronik list"""
        try:
            result = self.api_client.get_buku_kronik()
            if result["success"]:
                data = result["data"].get("data", [])
                return True, data
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting buku kronik list: {e}")
            return False, str(e)

    def add_buku_kronik(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Add new buku kronik entry"""
        try:
            result = self.api_client.add_buku_kronik(data)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error adding buku kronik: {e}")
            return False, str(e)

    def update_buku_kronik(self, kronik_id: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Update buku kronik entry"""
        try:
            result = self.api_client.update_buku_kronik(kronik_id, data)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error updating buku kronik: {e}")
            return False, str(e)

    def delete_buku_kronik(self, kronik_id: int) -> Tuple[bool, Any]:
        """Delete buku kronik entry"""
        try:
            result = self.api_client.delete_buku_kronik(kronik_id)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error deleting buku kronik: {e}")
            return False, str(e)

    # ========== PROGRAM KERJA KATEGORIAL METHODS ==========
    def get_program_kerja_kategorial_list(self, search: Optional[str] = None) -> Tuple[bool, Any]:
        """Get program kerja kategorial list"""
        try:
            result = self.api_client.get_program_kerja_kategorial(search)
            if result["success"]:
                return True, result["data"] if isinstance(result["data"], list) else []
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting program kerja kategorial list: {e}")
            return False, []

    def add_program_kerja_kategorial(self, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Add new program kerja kategorial"""
        try:
            result = self.api_client.add_program_kerja_kategorial(data)
            if result["success"]:
                return True, result["data"].get("id", 0)
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error adding program kerja kategorial: {e}")
            return False, str(e)

    def update_program_kerja_kategorial(self, program_id: int, data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Update program kerja kategorial"""
        try:
            result = self.api_client.update_program_kerja_kategorial(program_id, data)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error updating program kerja kategorial: {e}")
            return False, str(e)

    def delete_program_kerja_kategorial(self, program_id: int) -> Tuple[bool, Any]:
        """Delete program kerja kategorial"""
        try:
            result = self.api_client.delete_program_kerja_kategorial(program_id)
            if result["success"]:
                return True, result["data"]
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error deleting program kerja kategorial: {e}")
            return False, str(e)

    def close(self):
        """Close database manager"""
        self.logger.info("Database manager closed")