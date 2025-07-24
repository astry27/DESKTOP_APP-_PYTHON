# Path: server/database.py

import logging
import datetime
from typing import Optional, Tuple, Dict, Any, List
from api_client import ApiClient

class DatabaseManager:
    
    def __init__(self):
        self.logger = logging.getLogger('DatabaseManager')
        self.api_client = ApiClient()
        self.connection = None
        self._test_connection()
    
    def _test_connection(self):
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
    
    def get_active_sessions(self) -> Tuple[bool, Any]:
        """Ambil daftar client yang aktif melalui API"""
        try:
            result = self.api_client.get_active_sessions()
            if result["success"]:
                return True, result["data"].get("data", [])
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error getting active sessions: {e}")
            return False, str(e)
    
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
            data = result["data"].get("data", [])
            
            if search:
                filtered_data = []
                search_lower = search.lower()
                for item in data:
                    if (search_lower in str(item.get('nama_lengkap', '')).lower() or
                        search_lower in str(item.get('alamat', '')).lower() or
                        search_lower in str(item.get('no_telepon', '')).lower() or
                        search_lower in str(item.get('email', '')).lower()):
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
            return True, result["data"].get("id", 0)
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
    
    # ========== FILES METHODS ==========
    def get_files_list(self) -> Tuple[bool, Any]:
        result = self.api_client.get_files()
        if result["success"]:
            return True, result["data"].get("data", [])
        else:
            return False, result["data"]
    
    def upload_file(self, file_path: str) -> Tuple[bool, Any]:
        result = self.api_client.upload_file(file_path)
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
    
    def get_recent_messages(self, limit: int = 50) -> Tuple[bool, Any]:
        """Get recent messages"""
        return True, []
    
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
    
    def add_log_activity(self, id_admin: Optional[int], aktivitas: str, detail: str, ip_address: Optional[str] = None) -> Tuple[bool, Any]:
        """Add log activity untuk admin"""
        try:
            log_data = {
                'id_admin': id_admin,
                'aktivitas': aktivitas,
                'detail': detail,
                'ip_address': ip_address,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            return True, "Log activity recorded"
        except Exception as e:
            self.logger.error(f"Error adding log activity: {e}")
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
                return True, {
                    'content': result["data"],
                    'headers': result.get("headers", {})
                }
            else:
                return False, result["data"]
        except Exception as e:
            self.logger.error(f"Error downloading file: {e}")
            return False, str(e)
    
    def close(self):
        """Close database manager"""
        self.logger.info("Database manager closed")