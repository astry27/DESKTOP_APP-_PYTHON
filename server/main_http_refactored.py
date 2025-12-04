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
    from components.aset import AsetComponent
    from components.pengumuman import PengumumanComponent
    from components.pengaturan import PengaturanComponent
    from components.server_control import ServerControlComponent
    from components.riwayat import RiwayatComponent
    from components.dokumen import DokumenComponent
    from components.pengguna import PenggunaComponent
    from components.keuangan import KeuanganComponent
    from components.buku_kronik import BukuKronikComponent
    from components.kegiatan_paroki_page import KegiatanParokiPageComponent
    from components.kegiatan_wr_page import KegiatanWRPageComponent
    from components.proker_dpp_page import ProkerDPPPageComponent
    from components.proker_wr_page import ProkerWRPageComponent
    from components.struktur_wr_page import StrukturWRPageComponent
    from components.struktur_kategorial_page import StrukturKategorialPageComponent
    from components.keuangan_wr_page import KeuanganWRPageComponent
    from components.keuangan_kategorial_page import KeuanganKategorialPageComponent
    from components.proker_kategorial_page import ProkerKategorialPageComponent
    from components.tim_pembina import TimPembinaComponent
except ImportError as e:
    print(f"Error importing components: {e}")
    app = QApplication(sys.argv)
    temp_widget = QWidget()
    QMessageBox.critical(temp_widget, "Import Error", f"Gagal memuat komponen aplikasi:\n{e}\n\nPastikan semua file komponen berada di direktori yang benar.")
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
        self.show_login()
        
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
            # DatabaseManager sekarang lazy-load connection test
            # Actual connection status akan diketahui setelah login attempt
            print("Database Manager berhasil diinisialisasi.")
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
            print("Warning: Database Manager tidak tersedia")
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
        # PENTING: Set database manager agar server control bisa fetch data client
        if self.db:
            self.server_control.set_database_manager(self.db)
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
        self.struktur_component.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.struktur_component)

        # Index 2: Program Kerja (moved to standalone pages, keeping slot for backward compatibility)
        # NOTE: Program Kerja now uses standalone page components instead of tab interface
        placeholder_widget = QWidget()  # Placeholder for index 2
        self.content_stack.addWidget(placeholder_widget)

        # Index 3: Database Umat
        self.jemaat_component = JemaatComponent()
        self.jemaat_component.set_database_manager(self.db)
        self.jemaat_component.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.jemaat_component)

        # Index 4: Aset (sebelumnya Inventaris)
        self.aset_component = AsetComponent()
        self.aset_component.set_database_manager(self.db)
        self.aset_component.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.aset_component)

        # Index 5: Pengumuman
        self.pengumuman_component = PengumumanComponent()
        self.pengumuman_component.set_database_manager(self.db)
        self.pengumuman_component.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.pengumuman_component)

        # Index 6: Dokumen
        self.dokumen_component = DokumenComponent()
        self.dokumen_component.set_database_manager(self.db)
        self.dokumen_component.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.dokumen_component)

        # Index 7: Keuangan
        self.keuangan_component = KeuanganComponent(self.db)
        self.keuangan_component.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.keuangan_component)

        # Index 8: Tim Pembina
        self.tim_pembina_component = TimPembinaComponent()
        self.tim_pembina_component.set_database_manager(self.db)
        self.tim_pembina_component.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.tim_pembina_component)

        # Index 9: Riwayat
        self.riwayat_component = RiwayatComponent()
        self.riwayat_component.set_database_manager(self.db)
        self.content_stack.addWidget(self.riwayat_component)

        # Index 10: Pengaturan Sistem (termasuk Manajemen Pengguna)
        self.pengaturan_component = PengaturanComponent()
        self.pengaturan_component.set_database_manager(self.db)
        self.content_stack.addWidget(self.pengaturan_component)

        # Index 11: Buku Kronik
        self.buku_kronik_component = BukuKronikComponent()
        self.buku_kronik_component.set_database_manager(self.db)
        self.buku_kronik_component.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.buku_kronik_component)

        # Index 12: Kegiatan Paroki (standalone page)
        self.kegiatan_paroki_page = KegiatanParokiPageComponent()
        self.kegiatan_paroki_page.set_database_manager(self.db)
        self.kegiatan_paroki_page.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.kegiatan_paroki_page)

        # Index 13: Kegiatan WR (standalone page)
        self.kegiatan_wr_page = KegiatanWRPageComponent()
        self.kegiatan_wr_page.set_database_manager(self.db)
        self.kegiatan_wr_page.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.kegiatan_wr_page)

        # Index 14: Program Kerja DPP (standalone page)
        self.proker_dpp_page = ProkerDPPPageComponent()
        self.proker_dpp_page.set_database_manager(self.db)
        self.proker_dpp_page.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.proker_dpp_page)

        # Index 15: Program Kerja WR (standalone page)
        self.proker_wr_page = ProkerWRPageComponent()
        self.proker_wr_page.set_database_manager(self.db)
        self.proker_wr_page.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.proker_wr_page)

        # Index 16: Struktur WR (standalone page)
        self.struktur_wr_page = StrukturWRPageComponent()
        self.struktur_wr_page.set_database_manager(self.db)
        self.struktur_wr_page.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.struktur_wr_page)

        # Index 17: Struktur K. Kategorial (standalone page)
        self.struktur_kategorial_page = StrukturKategorialPageComponent()
        self.struktur_kategorial_page.set_database_manager(self.db)
        self.struktur_kategorial_page.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.struktur_kategorial_page)

        # Index 18: Keuangan WR (standalone page)
        self.keuangan_wr_page = KeuanganWRPageComponent()
        self.keuangan_wr_page.set_database_manager(self.db)
        self.keuangan_wr_page.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.keuangan_wr_page)

        # Index 19: Keuangan K. Kategorial (standalone page)
        self.keuangan_kategorial_page = KeuanganKategorialPageComponent()
        self.keuangan_kategorial_page.set_database_manager(self.db)
        self.keuangan_kategorial_page.set_current_admin(self.current_admin)
        admin_id = self.current_admin.get('id_admin')
        if admin_id:
            self.keuangan_kategorial_page.set_admin_id(admin_id)
        self.content_stack.addWidget(self.keuangan_kategorial_page)

        # Index 20: Program Kerja K. Kategorial (standalone page)
        self.proker_kategorial_page = ProkerKategorialPageComponent()
        self.proker_kategorial_page.set_database_manager(self.db)
        self.proker_kategorial_page.set_current_admin(self.current_admin)
        self.content_stack.addWidget(self.proker_kategorial_page)

        # Note: PenggunaComponent bisa diakses melalui PengaturanComponent

        self.server_control.set_database_manager(self.db)
    
    def setup_connections(self):
        # Main menu connections
        self.sidebar.menu_dashboard.clicked.connect(lambda: self.show_page(0))
        self.sidebar.menu_buku_kronik.clicked.connect(lambda: self.show_page(11))
        self.sidebar.menu_riwayat.clicked.connect(lambda: self.show_page(9))
        self.sidebar.menu_pengaturan.clicked.connect(lambda: self.show_page(10))

        # Submenu Pusat Paroki connections
        self.sidebar.submenu_pusat_paroki.menu_clicked.connect(self.on_pusat_paroki_menu_selected)

        # Submenu Wilayah Rohani connections
        self.sidebar.submenu_wilayah_rohani.menu_clicked.connect(self.on_wilayah_rohani_menu_selected)

        # Submenu Kelompok Kategorial connections
        self.sidebar.submenu_kelompok_kategorial.menu_clicked.connect(self.on_kelompok_kategorial_menu_selected)

        # Logout connection
        self.sidebar.logout_requested.connect(self.on_logout_requested)

        self.server_control.log_message.connect(self.server_control.add_log_message)

        components = [
            self.struktur_component,
            self.jemaat_component,
            self.aset_component,
            self.pengumuman_component,
            self.dokumen_component,
            self.keuangan_component,
            self.riwayat_component,
            self.pengaturan_component,
            self.buku_kronik_component,
            self.kegiatan_paroki_page,
            self.kegiatan_wr_page,
            self.proker_dpp_page,
            self.proker_wr_page,
            self.struktur_wr_page,
            self.struktur_kategorial_page,
            self.keuangan_wr_page,
            self.keuangan_kategorial_page,
            self.proker_kategorial_page
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
    
    def on_pusat_paroki_menu_selected(self, menu_id):
        """Handle Pusat Paroki submenu selection"""
        menu_map = {
            "struktur_dpp": (1, 0),          # Struktur Organisasi (Tab 0 - menampilkan DPP dan K. Binaan tabs)
            "proker_dpp": (14, None),        # Program Kerja DPP (standalone page - no tabs)
            "kegiatan_paroki": (12, None),   # Kegiatan Paroki (standalone page - no tabs)
            "database_umat": (3, None),      # Database Umat (no tabs)
            "aset": (4, None),               # Aset (no tabs)
            "dokumen": (6, None),            # Dokumen (no tabs)
            "pengumuman": (5, None),         # Pengumuman (no tabs)
            "tim_pembina": (8, None),        # Tim Pembina (no tabs)
        }
        if menu_id in menu_map:
            page_index, tab_index = menu_map[menu_id]
            self.show_page(page_index, tab_index)

    def on_wilayah_rohani_menu_selected(self, menu_id):
        """Handle Wilayah Rohani submenu selection"""
        menu_map = {
            "struktur_wr": (16, None),       # Struktur WR (standalone page - no tabs)
            "keuangan_wr": (18, None),       # Keuangan WR (standalone page - no tabs)
            "proker_wr": (15, None),         # Program Kerja WR (standalone page - no tabs)
            "kegiatan_wr": (13, None),       # Kegiatan WR (standalone page - no tabs)
        }
        if menu_id in menu_map:
            page_index, tab_index = menu_map[menu_id]
            self.show_page(page_index, tab_index)

    def on_kelompok_kategorial_menu_selected(self, menu_id):
        """Handle Kelompok Kategorial submenu selection"""
        menu_map = {
            "struktur_kategorial": (17, None),      # Struktur K. Kategorial (standalone page - no tabs)
            "keuangan_kategorial": (19, None),      # Keuangan K. Kategorial (standalone page - no tabs)
            "proker_kategorial": (20, None),        # Program Kerja K. Kategorial (standalone page - no tabs)
        }
        if menu_id in menu_map:
            page_index, tab_index = menu_map[menu_id]
            self.show_page(page_index, tab_index)

    def show_page(self, index, tab_index=None):
        """
        Show page dan optional tab index

        Args:
            index: Page index dalam content_stack
            tab_index: Tab index untuk component yang memiliki tabs (opsional)
        """
        self.sidebar.reset_menu_selection()

        if index == 0:
            self.sidebar.menu_dashboard.setChecked(True)
            self.update_dashboard_data()
        elif index == 1:
            self.sidebar.menu_pusat_paroki.setChecked(True)
            self.sidebar.submenu_pusat_paroki.show_submenu()
            self.struktur_component.load_data()
        elif index == 2:
            # Index 2 is now a placeholder - Program Kerja uses individual page components
            # Redirect to ProkerDPPPageComponent (index 14) as default
            self.sidebar.menu_pusat_paroki.setChecked(True)
            self.sidebar.submenu_pusat_paroki.show_submenu()
            self.show_page(14)  # Show ProkerDPPPageComponent instead
        elif index == 3:
            self.sidebar.menu_pusat_paroki.setChecked(True)
            self.sidebar.submenu_pusat_paroki.show_submenu()
            self.jemaat_component.load_data()
        elif index == 4:
            self.sidebar.menu_pusat_paroki.setChecked(True)
            self.sidebar.submenu_pusat_paroki.show_submenu()
            self.aset_component.load_data()
        elif index == 5:
            self.sidebar.menu_pusat_paroki.setChecked(True)
            self.sidebar.submenu_pusat_paroki.show_submenu()
            self.pengumuman_component.load_data()
        elif index == 6:
            self.sidebar.menu_pusat_paroki.setChecked(True)
            self.sidebar.submenu_pusat_paroki.show_submenu()
            self.dokumen_component.load_data()
        elif index == 7:
            self.sidebar.menu_wilayah_rohani.setChecked(True)
            self.sidebar.submenu_wilayah_rohani.show_submenu()
            self.keuangan_component.load_data()
        elif index == 8:
            # Index 8 is now a placeholder (Tim Pembina removed)
            # Redirect to dashboard
            self.show_page(0)
        elif index == 9:
            self.sidebar.menu_riwayat.setChecked(True)
            self.riwayat_component.load_data()
        elif index == 10:
            self.sidebar.menu_pengaturan.setChecked(True)
        elif index == 11:
            self.sidebar.menu_buku_kronik.setChecked(True)
            self.buku_kronik_component.load_data()
        elif index == 12:
            self.sidebar.menu_pusat_paroki.setChecked(True)
            self.sidebar.submenu_pusat_paroki.show_submenu()
            self.kegiatan_paroki_page.load_data()
        elif index == 13:
            self.sidebar.menu_wilayah_rohani.setChecked(True)
            self.sidebar.submenu_wilayah_rohani.show_submenu()
            self.kegiatan_wr_page.load_data()
        elif index == 14:
            self.sidebar.menu_pusat_paroki.setChecked(True)
            self.sidebar.submenu_pusat_paroki.show_submenu()
            self.proker_dpp_page.load_data()
        elif index == 15:
            self.sidebar.menu_wilayah_rohani.setChecked(True)
            self.sidebar.submenu_wilayah_rohani.show_submenu()
            self.proker_wr_page.load_data()
        elif index == 16:
            self.sidebar.menu_wilayah_rohani.setChecked(True)
            self.sidebar.submenu_wilayah_rohani.show_submenu()
            self.struktur_wr_page.load_data()
        elif index == 17:
            self.sidebar.menu_kelompok_kategorial.setChecked(True)
            self.sidebar.submenu_kelompok_kategorial.show_submenu()
            self.struktur_kategorial_page.load_data()

        elif index == 18:  # Keuangan WR
            self.sidebar.menu_wilayah_rohani.setChecked(True)
            self.sidebar.submenu_wilayah_rohani.show_submenu()
            self.keuangan_wr_page.load_data()

        elif index == 19:  # Keuangan K. Kategorial
            self.sidebar.menu_kelompok_kategorial.setChecked(True)
            self.sidebar.submenu_kelompok_kategorial.show_submenu()
            self.keuangan_kategorial_page.load_data()

        elif index == 20:  # Program Kerja K. Kategorial
            self.sidebar.menu_kelompok_kategorial.setChecked(True)
            self.sidebar.submenu_kelompok_kategorial.show_submenu()
            self.proker_kategorial_page.load_data()

        self.content_stack.setCurrentIndex(index)

        # Handle tab switching jika tab_index diberikan
        if tab_index is not None:
            self._switch_component_tab(index, tab_index)

        # Update status bar dengan info halaman saat ini
        page_names = [
            "Dashboard", "Struktur Organisasi", "Program Kerja",
            "Database Jemaat", "Aset", "Pengumuman",
            "Dokumen", "Keuangan", "Placeholder",
            "Riwayat", "Pengaturan Sistem", "Buku Kronik",
            "Kegiatan Paroki", "Kegiatan WR",
            "Program Kerja DPP", "Program Kerja WR",
            "Struktur WR", "Struktur K. Kategorial", "Keuangan WR", "Keuangan K. Kategorial",
            "Program Kerja K. Kategorial"
        ]
        if 0 <= index < len(page_names):
            if self.db and self.db.connection:
                self.statusBar().showMessage(f"API Mode - {page_names[index]}")
            else:
                self.statusBar().showMessage(f"Offline Mode - {page_names[index]} (Limited)")
    
    def _switch_component_tab(self, page_index, tab_index):
        """
        Switch tab dalam component yang memiliki tabs

        Args:
            page_index: Index halaman dalam content_stack
            tab_index: Index tab yang ingin ditampilkan
        """
        try:
            if page_index == 1:  # Struktur Component
                if hasattr(self.struktur_component, 'tab_widget'):
                    self.struktur_component.tab_widget.setCurrentIndex(tab_index)
            elif page_index == 7:  # Keuangan Component
                if hasattr(self.keuangan_component, 'tab_widget'):
                    self.keuangan_component.tab_widget.setCurrentIndex(tab_index)
            elif page_index == 9:  # Riwayat Component
                if hasattr(self.riwayat_component, 'tab_widget'):
                    self.riwayat_component.tab_widget.setCurrentIndex(tab_index)
            elif page_index == 10:  # Pengaturan Component
                if hasattr(self.pengaturan_component, 'tab_widget'):
                    self.pengaturan_component.tab_widget.setCurrentIndex(tab_index)
            # Note: Program Kerja pages (index 14, 15) don't have tabs anymore
        except Exception as e:
            print(f"Error switching tab: {e}")

    def load_all_data(self):
        if not self.db:
            self.server_control.add_log_message("Tidak bisa memuat data, API shared hosting tidak terhubung.")
            return

        self.struktur_component.load_data()
        self.jemaat_component.load_data()

        # Load program kerja pages (DPP, WR) and kegiatan pages (Paroki, WR)
        self.proker_dpp_page.load_data()
        self.proker_wr_page.load_data()
        self.kegiatan_paroki_page.load_data()
        self.kegiatan_wr_page.load_data()

        self.pengumuman_component.load_data()
        self.aset_component.load_data()
        self.dokumen_component.load_data()
        self.keuangan_component.load_data()
        self.riwayat_component.load_data()
        self.buku_kronik_component.load_data()

        # Load standalone kegiatan pages
        self.kegiatan_paroki_page.load_data()
        self.kegiatan_wr_page.load_data()

        # Load standalone program kerja pages
        self.proker_dpp_page.load_data()
        self.proker_wr_page.load_data()

        # Load standalone struktur pages
        self.struktur_wr_page.load_data()
        self.struktur_kategorial_page.load_data()

        # Load standalone keuangan pages
        self.keuangan_wr_page.load_data()
        self.keuangan_kategorial_page.load_data()

        # Load standalone proker kategorial page
        self.proker_kategorial_page.load_data()

        self.update_dashboard_data()

        # Update sidebar status setelah load data
        if hasattr(self.sidebar, 'update_api_status'):
            self.sidebar.update_api_status()

        self.server_control.add_log_message("Semua data berhasil dimuat ulang dari API shared hosting.")
    
    def update_dashboard_data(self):
        if not self.db:
            return

        jemaat_data = self.jemaat_component.get_data()
        # Get kegiatan data from individual page components
        kegiatan_paroki_data = self.kegiatan_paroki_page.get_data() if hasattr(self.kegiatan_paroki_page, 'get_data') else []
        kegiatan_wr_data = self.kegiatan_wr_page.get_data() if hasattr(self.kegiatan_wr_page, 'get_data') else []
        kegiatan_data = kegiatan_paroki_data + kegiatan_wr_data
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
                         # DEVELOPMENT: Changed from Shared Hosting to localhost
                         f"Database: API Mode (Local Development)\n"
                         f"API Endpoint: http://localhost:5000\n\n"
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

    def on_logout_requested(self):
        """Handle logout request dari sidebar"""
        try:
            # Log logout activity
            self.log_admin_activity("Logout", "Administrator logout dari sistem")

            # Stop all timers in components
            for component_name in ['dokumen_component', 'riwayat_component', 'server_control']:
                if hasattr(self, component_name):
                    component = getattr(self, component_name)
                    if hasattr(component, 'update_timer') and component.update_timer:
                        component.update_timer.stop()
                    if hasattr(component, 'status_timer') and component.status_timer:
                        component.status_timer.stop()

            # Reset current admin
            self.current_admin = None

            # Hide main window
            self.hide()

            # Show login dialog
            self.show_login()

            # Jika login berhasil, tampilkan kembali main window dan refresh
            if self.current_admin:
                # Update admin info di semua komponen
                self.dashboard_component.set_current_admin(self.current_admin)
                self.struktur_component.set_current_admin(self.current_admin)
                self.proker_dpp_page.set_current_admin(self.current_admin)
                self.kegiatan_paroki_page.set_current_admin(self.current_admin)
                self.aset_component.set_current_admin(self.current_admin)
                self.pengumuman_component.set_current_admin(self.current_admin)
                self.dokumen_component.set_current_admin(self.current_admin)
                self.keuangan_component.set_current_admin(self.current_admin)
                self.tim_pembina_component.set_current_admin(self.current_admin)
                self.buku_kronik_component.set_current_admin(self.current_admin)
                self.kegiatan_wr_page.set_current_admin(self.current_admin)
                self.proker_wr_page.set_current_admin(self.current_admin)
                self.struktur_wr_page.set_current_admin(self.current_admin)
                self.keuangan_wr_page.set_current_admin(self.current_admin)
                self.struktur_kategorial_page.set_current_admin(self.current_admin)
                self.keuangan_kategorial_page.set_current_admin(self.current_admin)
                self.proker_kategorial_page.set_current_admin(self.current_admin)

                # Update window title
                admin_name = self.current_admin.get('nama_lengkap', 'Administrator')
                self.setWindowTitle(f"Server Admin Panel - {admin_name} (API Mode)")

                # Log login baru
                self.log_admin_activity("Login berhasil", "Administrator login ke sistem")
                self.server_control.add_log_message(f"Login berhasil: {admin_name}")

                # Reload data
                if self.db and self.db.connection:
                    self.load_all_data()

                # Show main window again
                self.show()

                # Reset ke dashboard
                self.show_page(0)
            else:
                # Jika login gagal/dibatalkan, tutup aplikasi
                self.close()

        except Exception as e:
            print(f"Error saat logout: {str(e)}")
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat logout: {str(e)}")

    def refresh_current_component(self):
        """Refresh data pada komponen yang sedang aktif"""
        try:
            current_index = self.content_stack.currentIndex()

            # Mapping index ke komponen
            component_map = {
                0: ('dashboard_component', 'Dashboard'),
                1: ('jemaat_component', 'Database Umat'),
                2: ('struktur_component', 'Struktur Organisasi'),
                3: ('proker_dpp_page', 'Program Kerja DPP'),
                4: ('kegiatan_paroki_page', 'Kegiatan Paroki'),
                5: ('aset_component', 'Aset'),
                6: ('pengumuman_component', 'Pengumuman'),
                7: ('dokumen_component', 'Dokumen'),
                8: ('keuangan_component', 'Keuangan'),
                9: ('tim_pembina_component', 'Tim Pembina'),
                10: ('buku_kronik_component', 'Buku Kronik'),
                11: ('kegiatan_wr_page', 'Kegiatan WR'),
                12: ('proker_wr_page', 'Program Kerja WR'),
                13: ('struktur_wr_page', 'Struktur WR'),
                14: ('keuangan_wr_page', 'Keuangan WR'),
                15: ('struktur_kategorial_page', 'Struktur Kategorial'),
                16: ('keuangan_kategorial_page', 'Keuangan Kategorial'),
                17: ('proker_kategorial_page', 'Program Kerja Kategorial'),
                18: ('pengguna_component', 'Pengguna'),
                19: ('riwayat_component', 'Riwayat'),
                20: ('pengaturan_component', 'Pengaturan'),
                21: ('server_control', 'Kontrol Server'),
            }

            if current_index in component_map:
                component_name, display_name = component_map[current_index]

                if hasattr(self, component_name):
                    component = getattr(self, component_name)

                    # Panggil load_data jika ada
                    if hasattr(component, 'load_data'):
                        component.load_data()
                        self.server_control.add_log_message(f"Data {display_name} berhasil di-refresh")
                    elif hasattr(component, 'refresh_status'):
                        component.refresh_status()
                        self.server_control.add_log_message(f"{display_name} berhasil di-refresh")
                    else:
                        self.server_control.add_log_message(f"{display_name} tidak memiliki fungsi refresh")

        except Exception as e:
            print(f"Error saat refresh: {str(e)}")
            self.server_control.add_log_message(f"Error refresh: {str(e)}")

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