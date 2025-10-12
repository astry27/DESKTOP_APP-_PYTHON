# Path: server/main_http_refactored.py

import sys
import datetime
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QStackedWidget, QFrame, QStatusBar,
                            QAction, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

try:
    from components.login_dialog import LoginDialog
    from components.sidebar import SidebarWidget
    from components.dashboard import DashboardComponent
    from components.struktur import StrukturComponent
    from components.jemaat import JemaatComponent
    from components.program_kerja import ProgramKerjaComponent
    from components.inventaris import InventarisComponent
    from components.pengumuman import PengumumanComponent
    from components.pengaturan import PengaturanComponent
    from components.server_control import ServerControlComponent
    from components.riwayat import RiwayatComponent
    from components.dokumen import DokumenComponent
    from components.pengguna import PenggunaComponent
    from components.keuangan import KeuanganComponent
except ImportError as e:
    print(f"Error importing components: {e}")
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "Import Error", f"Gagal memuat komponen aplikasi:\n{e}\n\nPastikan semua file komponen berada di direktori yang benar.")
    sys.exit(1)

from database import DatabaseManager
from client_handler import ClientRegistrationServer

class ServerMainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.current_admin = None
        self.client_server = None
        
        # Setup database first
        self.setup_database()
        
        # Setup client registration server
        self.setup_client_server()
        
        # Show login dialog before main window
        if not self.show_login():
            sys.exit(1)
        
        # Setup main window after successful login
        self.setup_main_window()
        self.setup_ui()
        self.setup_menu()
        self.setup_connections()
        
        if self.db and self.db.connection:
            self.statusBar().showMessage("API Mode - Server Admin")
        else:
            self.statusBar().showMessage("Offline Mode - Server Admin (Limited Features)")
        
        if self.db and self.db.connection:
            self.load_all_data()
        else:
            self.show_offline_warning()

        if self.db and self.db.connection:
            self.log_admin_activity("Login berhasil", "Administrator login ke sistem")
            self.server_control.add_log_message(f"Login berhasil: {self.current_admin.get('nama_lengkap', 'Administrator')}")
            self.server_control.add_log_message("Aplikasi server admin dimulai dalam API Mode.")
            self.server_control.add_log_message("Koneksi API shared hosting berhasil.")
            if self.client_server and self.client_server.is_running():
                self.server_control.add_log_message("Client registration server berhasil dimulai pada http://localhost:8080")
            self.server_control.add_log_message("Sistem siap. Kelola API dan client melalui panel kontrol.")
        else:
            self.server_control.add_log_message(f"Mode Offline: {self.current_admin.get('nama_lengkap', 'Administrator')}")
            self.server_control.add_log_message("Aplikasi dimulai dalam MODE OFFLINE.")
            self.server_control.add_log_message("PERINGATAN: Koneksi API shared hosting gagal. Periksa koneksi internet.")
            self.server_control.add_log_message("Mode offline terbatas - fitur penuh tidak tersedia.")
    
    def setup_database(self):
        try:
            self.db = DatabaseManager()
            if not self.db.connection:
                self.db = None 
                print("Peringatan: Gagal terhubung ke API shared hosting saat inisialisasi.")
                print("Aplikasi akan berjalan dalam mode offline terbatas.")
            else:
                print("Database Manager berhasil diinisialisasi dan terhubung ke API shared hosting.")
        except Exception as e:
            self.db = None
            print(f"Error inisialisasi Database Manager: {str(e)}")
            print("Aplikasi akan berjalan dalam mode offline terbatas.")
    
    def setup_client_server(self):
        """Setup local client registration server"""
        try:
            self.client_server = ClientRegistrationServer(port=8080)
            if self.db:
                self.client_server.set_database_manager(self.db)
            
            if self.client_server.start():
                print("Client registration server berhasil dimulai pada port 8080")
            else:
                print("Gagal memulai client registration server")
                self.client_server = None
        except Exception as e:
            print(f"Error memulai client registration server: {str(e)}")
            self.client_server = None
    
    def show_login(self):
        """Tampilkan dialog login dan return True jika berhasil"""
        if not self.db:
            reply = QMessageBox.question(None, "Koneksi API Gagal", 
                                       "Tidak dapat terhubung ke API shared hosting.\n\n"
                                       "Aplikasi dapat dijalankan dalam mode offline terbatas, "
                                       "tetapi fitur login dan akses data tidak akan tersedia.\n\n"
                                       "Apakah Anda ingin melanjutkan?",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            if reply == QMessageBox.No:
                return False
            
            # Set dummy admin data untuk mode offline
            self.current_admin = {
                'id_admin': 1,
                'username': 'offline_admin',
                'nama_lengkap': 'Administrator (Offline Mode)',
                'peran': 'administrator'
            }
            return True
        
        login_dialog = LoginDialog(self.db)
        login_dialog.login_successful.connect(self.on_login_successful)
        
        result = login_dialog.exec_()
        
        if result == login_dialog.Accepted and self.current_admin:
            return True
        else:
            return False
    
    def on_login_successful(self, admin_data):
        """Handler ketika login berhasil"""
        self.current_admin = admin_data
        print(f"Login berhasil: {admin_data.get('nama_lengkap', 'Administrator')}")
    
    def setup_main_window(self):
        """Setup properti main window"""
        admin_name = self.current_admin.get('nama_lengkap', 'Administrator')
        if self.db and self.db.connection:
            self.setWindowTitle(f"Server Admin Gereja Katolik (API Mode) - {admin_name} - v2.1.0")
        else:
            self.setWindowTitle(f"Server Admin Gereja Katolik (Offline Mode) - {admin_name} - v2.1.0")
        self.setMinimumSize(1200, 800)
    
    def show_offline_warning(self):
        """Tampilkan peringatan mode offline"""
        QMessageBox.warning(self, "Mode Offline", 
                          "Aplikasi berjalan dalam mode offline terbatas.\n\n"
                          "Fitur yang terbatas dalam mode offline:\n"
                          "• Data tidak dapat dimuat dari server\n"
                          "• Tidak dapat menyimpan perubahan data\n"
                          "• Kontrol API tidak tersedia\n"
                          "• Broadcast message tidak tersedia\n\n"
                          "Silakan periksa koneksi internet dan restart aplikasi "
                          "untuk menggunakan fitur penuh.")
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = SidebarWidget()
        # PENTING: Set database manager ke sidebar agar status API bisa diupdate
        self.sidebar.set_database_manager(self.db)
        main_layout.addWidget(self.sidebar)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #7f8c8d;")
        separator.setFixedWidth(1)
        main_layout.addWidget(separator)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.server_control = ServerControlComponent()
        content_layout.addWidget(self.server_control)
        
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        main_layout.addWidget(content_widget)
        
        main_layout.setStretchFactor(self.sidebar, 0)
        main_layout.setStretchFactor(separator, 0)
        main_layout.setStretchFactor(content_widget, 1)
        
        self.setup_components()
        self.show_page(0)
    
    def setup_components(self):
        # Index 0: Dashboard
        self.dashboard_component = DashboardComponent()
        self.content_stack.addWidget(self.dashboard_component)
        
        # Index 1: Struktur DPP
        self.struktur_component = StrukturComponent()
        self.struktur_component.set_database_manager(self.db)
        self.content_stack.addWidget(self.struktur_component)
        
        # Index 2: Program Kerja
        self.program_kerja_component = ProgramKerjaComponent()
        self.program_kerja_component.set_database_manager(self.db)
        self.content_stack.addWidget(self.program_kerja_component)
        
        # Index 3: Database Umat
        self.jemaat_component = JemaatComponent()
        self.jemaat_component.set_database_manager(self.db)
        self.content_stack.addWidget(self.jemaat_component)
        
        # Index 4: Inventaris
        self.inventaris_component = InventarisComponent()
        self.inventaris_component.set_database_manager(self.db)
        self.content_stack.addWidget(self.inventaris_component)
        
        # Index 5: Pengumuman
        self.pengumuman_component = PengumumanComponent()
        self.pengumuman_component.set_database_manager(self.db)
        self.content_stack.addWidget(self.pengumuman_component)
        
        # Index 6: Riwayat
        self.riwayat_component = RiwayatComponent()
        self.riwayat_component.set_database_manager(self.db)
        self.content_stack.addWidget(self.riwayat_component)
        
        # Index 7: Dokumen
        self.dokumen_component = DokumenComponent()
        self.dokumen_component.set_database_manager(self.db)
        self.content_stack.addWidget(self.dokumen_component)
        
        # Index 8: Keuangan
        self.keuangan_component = KeuanganComponent(self.db)
        self.content_stack.addWidget(self.keuangan_component)
        
        # Index 9: Manajemen Pengguna
        self.pengguna_component = PenggunaComponent()
        self.content_stack.addWidget(self.pengguna_component)
        
        # Index 10: Pengaturan Sistem
        self.pengaturan_component = PengaturanComponent()
        self.pengaturan_component.set_database_manager(self.db)
        self.content_stack.addWidget(self.pengaturan_component)
        
        self.server_control.set_database_manager(self.db)
    
    def setup_connections(self):
        self.sidebar.menu_dashboard.clicked.connect(lambda: self.show_page(0))
        self.sidebar.menu_struktur.clicked.connect(lambda: self.show_page(1))
        self.sidebar.menu_program_kerja.clicked.connect(lambda: self.show_page(2))
        self.sidebar.menu_jemaat.clicked.connect(lambda: self.show_page(3))
        self.sidebar.menu_inventaris.clicked.connect(lambda: self.show_page(4))
        self.sidebar.menu_pengumuman.clicked.connect(lambda: self.show_page(5))
        self.sidebar.menu_riwayat.clicked.connect(lambda: self.show_page(6))
        self.sidebar.menu_dokumen.clicked.connect(lambda: self.show_page(7))
        self.sidebar.menu_keuangan.clicked.connect(lambda: self.show_page(8))
        self.sidebar.menu_pengguna.clicked.connect(lambda: self.show_page(9))
        self.sidebar.menu_pengaturan.clicked.connect(lambda: self.show_page(10))
        
        self.server_control.log_message.connect(self.server_control.add_log_message)
        
        components = [
            self.struktur_component,
            self.program_kerja_component,
            self.jemaat_component,
            self.inventaris_component,
            self.pengumuman_component,
            self.riwayat_component,
            self.dokumen_component,
            self.keuangan_component,
            self.pengguna_component,
            self.pengaturan_component
        ]
        
        for component in components:
            if hasattr(component, 'log_message'):
                component.log_message.connect(self.server_control.add_log_message)
            if hasattr(component, 'data_updated'):
                component.data_updated.connect(self.update_dashboard_data)
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&File")
        
        enable_api_action = QAction("Aktifkan API", self)
        enable_api_action.triggered.connect(self.server_control.enable_api)
        file_menu.addAction(enable_api_action)
        
        disable_api_action = QAction("Nonaktifkan API", self)
        disable_api_action.triggered.connect(self.server_control.disable_api)
        file_menu.addAction(disable_api_action)
        
        file_menu.addSeparator()
        
        backup_action = QAction("Backup Database", self)
        backup_action.triggered.connect(self.pengaturan_component.backup_database)
        file_menu.addAction(backup_action)
        
        restore_action = QAction("Restore Database", self)
        restore_action.triggered.connect(self.pengaturan_component.restore_database)
        file_menu.addAction(restore_action)
        
        file_menu.addSeparator()
        
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Keluar", self)
        exit_action.triggered.connect(self.close)  # type: ignore
        file_menu.addAction(exit_action)
        
        edit_menu = menubar.addMenu("&Edit")
        
        preferences_action = QAction("Preferensi", self)
        preferences_action.triggered.connect(lambda: self.show_page(7))
        edit_menu.addAction(preferences_action)
        
        view_menu = menubar.addMenu("&Tampilan")
        
        refresh_action = QAction("Refresh Data", self)
        refresh_action.triggered.connect(self.load_all_data)
        view_menu.addAction(refresh_action)
        
        tools_menu = menubar.addMenu("&Alat")
        
        send_message_action = QAction("Kirim Pesan ke Semua Client", self)
        send_message_action.triggered.connect(self.server_control.send_broadcast_message)
        tools_menu.addAction(send_message_action)
        
        refresh_status_action = QAction("Refresh Status API", self)
        refresh_status_action.triggered.connect(self.server_control.auto_refresh_status)
        tools_menu.addAction(refresh_status_action)
        
        help_menu = menubar.addMenu("&Bantuan")
        
        about_action = QAction("Tentang", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_action = QAction("Bantuan", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
    
    def logout(self):
        """Logout dari aplikasi"""
        reply = QMessageBox.question(self, 'Konfirmasi Logout',
                                    "Yakin ingin logout dari aplikasi?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Log logout activity
            self.log_admin_activity("Logout", "Administrator logout dari sistem")
            
            # Close database connection
            if self.db:
                self.db.close()
            
            # Restart aplikasi dengan login ulang
            QApplication.quit()
            python = sys.executable
            os.execl(python, python, *sys.argv)
    
    def log_admin_activity(self, activity, detail):
        """Log aktivitas admin"""
        if self.db and self.current_admin:
            try:
                self.db.add_log_activity(
                    self.current_admin.get('id_admin'),
                    activity,
                    detail,
                    "127.0.0.1"
                )
            except Exception as e:
                print(f"Error logging admin activity: {e}")
    
    def show_page(self, index):
        self.sidebar.reset_menu_selection()
        
        if index == 0:
            self.sidebar.menu_dashboard.setChecked(True)
            self.update_dashboard_data()
        elif index == 1:
            self.sidebar.menu_struktur.setChecked(True)
            self.struktur_component.load_data()
        elif index == 2:
            self.sidebar.menu_program_kerja.setChecked(True)
            self.program_kerja_component.kalender_widget.load_data()
        elif index == 3:
            self.sidebar.menu_jemaat.setChecked(True)
            self.jemaat_component.load_data()
        elif index == 4:
            self.sidebar.menu_inventaris.setChecked(True)
            self.inventaris_component.load_data()
        elif index == 5:
            self.sidebar.menu_pengumuman.setChecked(True)
            self.pengumuman_component.load_data()
        elif index == 6:
            self.sidebar.menu_riwayat.setChecked(True)
            self.riwayat_component.load_data()
        elif index == 7:
            self.sidebar.menu_dokumen.setChecked(True)
            self.dokumen_component.load_data()
        elif index == 8:
            self.sidebar.menu_keuangan.setChecked(True)
            self.keuangan_component.load_data()
        elif index == 9:
            self.sidebar.menu_pengguna.setChecked(True)
        elif index == 10:
            self.sidebar.menu_pengaturan.setChecked(True)
        
        self.content_stack.setCurrentIndex(index)
        
        # Update status bar dengan info halaman saat ini
        page_names = [
            "Dashboard", "Database Jemaat", "Jadwal Kegiatan", 
            "Manajemen Keuangan", "Pengumuman", "Riwayat", 
            "Dokumen", "Pengaturan Sistem"
        ]
        if 0 <= index < len(page_names):
            if self.db and self.db.connection:
                self.statusBar().showMessage(f"API Mode - {page_names[index]}")
            else:
                self.statusBar().showMessage(f"Offline Mode - {page_names[index]} (Limited)")
    
    def load_all_data(self):
        if not self.db:
            self.server_control.add_log_message("Tidak bisa memuat data, API shared hosting tidak terhubung.")
            return

        self.struktur_component.load_data()
        self.jemaat_component.load_data()
        self.program_kerja_component.kalender_widget.load_data()
        self.pengumuman_component.load_data()
        self.inventaris_component.load_data()
        self.riwayat_component.load_data()
        self.dokumen_component.load_data()
        self.update_dashboard_data()
        
        # Update sidebar status setelah load data
        if hasattr(self.sidebar, 'update_api_status'):
            self.sidebar.update_api_status()
        
        self.server_control.add_log_message("Semua data berhasil dimuat ulang dari API shared hosting.")
    
    def update_dashboard_data(self):
        if not self.db:
            return

        jemaat_data = self.jemaat_component.get_data()
        kegiatan_data = self.program_kerja_component.get_data()
        pengumuman_data = self.pengumuman_component.get_data()
        
        self.dashboard_component.update_statistics(
            jemaat_data, 
            kegiatan_data, 
            pengumuman_data, 
            self.db
        )
    
    def show_about(self):
        admin_name = self.current_admin.get('nama_lengkap', 'Administrator')
        mode = "API Mode" if self.db and self.db.connection else "Offline Mode"
        connection_status = "Terhubung ke API shared hosting" if self.db and self.db.connection else "Tidak terhubung (Mode Offline)"
        
        QMessageBox.about(self, "Tentang Aplikasi", 
                         f"Server Admin Gereja Katolik ({mode})\n"
                         f"Versi 2.1.0\n\n"
                         f"Sedang login sebagai: {admin_name}\n"
                         f"Username: {self.current_admin.get('username', 'admin')}\n\n"
                         f"Status Koneksi: {connection_status}\n\n"
                         f"Aplikasi admin untuk mengelola sistem gereja katolik "
                         f"dengan arsitektur API shared hosting.\n\n"
                         f"Fitur:\n"
                         f"- Manajemen Data Jemaat\n"
                         f"- Jadwal Kegiatan\n"
                         f"- Pengumuman\n"
                         f"- Kontrol API Server\n"
                         f"- Broadcast Message ke Client\n"
                         f"- Sistem Login Admin\n\n"
                         f"Database: API Mode via Shared Hosting\n"
                         f"API Endpoint: https://enternal.my.id/flask\n\n"
                         f"Dibuat dengan PyQt5 dan Flask API")
    
    def show_help(self):
        help_text = """
        BANTUAN APLIKASI SERVER ADMIN GEREJA KATOLIK (API MODE)
        
        === ARSITEKTUR SISTEM ===
        
        Aplikasi menggunakan arsitektur berikut:
        Client Desktop -> API Shared Hosting <- Server Admin Desktop
        
        - Semua client terhubung langsung ke API shared hosting
        - Server admin mengelola API dan data melalui shared hosting
        - Tidak ada server lokal yang berjalan di komputer admin
        
        === FITUR KONTROL API ===
        
        1. AKTIFKAN/NONAKTIFKAN API
        - Admin dapat mengaktifkan atau menonaktifkan API
        - Ketika API nonaktif, semua client tidak dapat mengakses sistem
        - Ketika API aktif, client dapat terhubung dan menggunakan sistem
        
        2. MONITORING CLIENT
        - Melihat daftar client yang sedang terhubung
        - Memantau status koneksi client
        - Melihat waktu koneksi client
        
        3. BROADCAST MESSAGE
        - Mengirim pesan ke semua client yang terhubung
        - Pesan akan diterima oleh semua client melalui API
        
        === MANAJEMEN DATA ===
        
        - Semua data (jemaat, kegiatan, pengumuman) disimpan di database shared hosting
        - Admin dapat melakukan CRUD operations melalui interface desktop
        - Client juga dapat mengakses data yang sama melalui API
        
        === KEAMANAN ===
        
        - Login admin wajib sebelum menggunakan aplikasi
        - Hanya admin yang dapat mengaktifkan/menonaktifkan API
        - Log aktivitas admin tercatat
        
        === KEUNGGULAN ARSITEKTUR INI ===
        
        - Tidak perlu port forwarding atau VPN
        - Client dapat mengakses dari mana saja selama ada internet
        - Database terpusat di shared hosting
        - Mudah maintenance dan skalabilitas
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Bantuan")
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def closeEvent(self, event):
        try:
            # Log logout activity
            self.log_admin_activity("Application Closed", "Administrator menutup aplikasi")

            # Stop all timers in components
            for component_name in ['dokumen_component', 'riwayat_component', 'server_control']:
                if hasattr(self, component_name):
                    component = getattr(self, component_name)
                    if hasattr(component, 'update_timer') and component.update_timer:
                        component.update_timer.stop()
                        component.update_timer.deleteLater()
                    if hasattr(component, 'status_timer') and component.status_timer:
                        component.status_timer.stop()
                        component.status_timer.deleteLater()

            # Stop client registration server
            if self.client_server:
                self.client_server.stop()

            if self.db:
                self.db.close()
        except Exception:
            # Silently ignore errors during shutdown
            pass
        finally:
            event.accept()


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Server Admin Gereja Katolik - API Mode")
    app.setApplicationVersion("2.1.0")
    app.setOrganizationName("Gereja Katolik")

    window = ServerMainWindow()
    window.show()

    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nShutting down gracefully...")
        window.close()
        sys.exit(0)