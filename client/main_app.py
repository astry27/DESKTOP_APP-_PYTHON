# Path: client/main_app.py

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QFrame, QPushButton, QStackedWidget,
                            QMessageBox, QStatusBar, QSystemTrayIcon, QMenu,
                            QDialog, QLineEdit, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap

from api_client import ApiClient
from components.login_dialog import LoginDialog
from components.pengumuman_component import PengumumanComponent
from components.dokumen_component import DokumenComponent
from components.jemaat_component import JemaatClientComponent
from components.jadwal_component import JadwalClientComponent
from components.keuangan_component import KeuanganClientComponent
from components.placeholder_component import PlaceholderComponent

class ClientAppWindow(QMainWindow):
    
    def __init__(self, api_client):
        super().__init__()
        self.setWindowTitle("Gereja Katolik Santa Maria Ratu Damai")
        self.setMinimumSize(1280, 720)
        self.resize(1400, 900)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
        
        self.api_client = api_client
        self.user_data = None
        self.is_connected = False
        
        self.setup_ui()
        self.setup_timers()
        self.setup_system_tray()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top Header/Logo
        self.header = self.create_header()
        main_layout.addWidget(self.header)
        
        # Horizontal Navbar
        self.navbar = self.create_navbar()
        main_layout.addWidget(self.navbar)
        
        # Main content area
        self.content_area = self.create_content_area()
        main_layout.addWidget(self.content_area)
        
        # Set initial page to Dashboard
        self.show_dashboard()
        
    def create_header(self):
        """Create clean professional header with welcome message"""
        header_frame = QFrame()
        header_frame.setFixedHeight(100)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                border: none;
                border-bottom: 2px solid #e9ecef;
            }
        """)
        
        layout = QHBoxLayout(header_frame)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)
        
        # Container untuk title dan subtitle dengan layout vertikal yang lebih baik
        title_container = QWidget()
        title_container.setMinimumWidth(600)
        title_container.setSizePolicy(title_container.sizePolicy().Expanding, title_container.sizePolicy().Preferred)
        
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        title_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Title utama dengan styling yang lebih profesional
        self.welcome_title_label = QLabel("Selamat Datang, Pengguna")
        self.welcome_title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: 700;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                border: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
                letter-spacing: 0.5px;
            }
        """)
        self.welcome_title_label.setWordWrap(True)
        self.welcome_title_label.setAlignment(Qt.AlignLeft)
        self.welcome_title_label.setSizePolicy(self.welcome_title_label.sizePolicy().Expanding, self.welcome_title_label.sizePolicy().Preferred)
        
        # Subtitle dengan spacing dan styling yang diperbaiki
        self.welcome_subtitle_label = QLabel("Gereja Katolik Santa Maria Ratu Damai, Tomohon")
        self.welcome_subtitle_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 15px;
                font-weight: 400;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                border: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
                letter-spacing: 0.3px;
            }
        """)
        self.welcome_subtitle_label.setWordWrap(True)
        self.welcome_subtitle_label.setAlignment(Qt.AlignLeft)
        self.welcome_subtitle_label.setSizePolicy(self.welcome_subtitle_label.sizePolicy().Expanding, self.welcome_subtitle_label.sizePolicy().Preferred)
        
        # Menambahkan label ke layout dengan alignment yang tepat
        title_layout.addWidget(self.welcome_title_label)
        title_layout.addWidget(self.welcome_subtitle_label)
        title_layout.addStretch()
        
        layout.addWidget(title_container)
        layout.addStretch()
        
        # User info and actions
        user_info_layout = QHBoxLayout()
        user_info_layout.setSpacing(20)
        
        # Connection status with cleaner design
        self.connection_status = QLabel("● Offline")
        self.connection_status.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 11px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 6px 12px;
                background-color: rgba(231, 76, 60, 0.08);
                border-radius: 16px;
                border: none;
            }
        """)
        user_info_layout.addWidget(self.connection_status)
        
        
        # Profile user button dengan dropdown
        self.profile_button = QPushButton("👤")
        self.profile_button.setFixedSize(40, 40)
        self.profile_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f5f99;
            }
        """)
        self.profile_button.clicked.connect(self.show_profile_menu)
        user_info_layout.addWidget(self.profile_button)
        
        layout.addLayout(user_info_layout)
        
        return header_frame
    
    def create_navbar(self):
        """Create clean professional navigation bar"""
        navbar_frame = QFrame()
        navbar_frame.setFixedHeight(55)
        navbar_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #34495e, stop: 1 #2c3e50);
                border: none;
                border-bottom: 1px solid rgba(52, 152, 219, 0.3);
            }
        """)
        
        layout = QHBoxLayout(navbar_frame)
        layout.setContentsMargins(40, 0, 40, 0)
        layout.setSpacing(5)
        
        # Menu items - clean web style without icons
        self.nav_buttons = {}
        menu_items = [
            ("dashboard", "Dashboard"),
            ("jemaat", "Database Jemaat"),
            ("jadwal", "Jadwal Kegiatan"),
            ("keuangan", "Manajemen Keuangan"),
            ("pengumuman", "Pengumuman"),
            ("dokumen", "Dokumen"),
            ("aktivitas", "Aktivitas")
        ]
        
        for key, title in menu_items:
            button = self.create_nav_button(title, key)
            self.nav_buttons[key] = button
            layout.addWidget(button)
        
        layout.addStretch()
        
        return navbar_frame
    
    def create_nav_button(self, title, key):
        """Create elegant navigation button"""
        button = QPushButton(title)
        button.setFixedHeight(55)
        button.setObjectName(f"nav_button_{key}")
        
        # Clean professional button styling - flat design
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #ecf0f1;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 16px 24px;
                margin: 2px 1px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)
        
        # Connect click event
        button.clicked.connect(lambda: self.navigate_to(key))
        
        return button
    
    def create_content_area(self):
        """Create modern web-style content area"""
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(content_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create all pages
        self.create_all_pages()
        
        return content_frame
    
    def create_all_pages(self):
        """Create all pages and add to stacked widget"""
        
        # Dashboard page
        self.dashboard_page = self.create_dashboard_page()
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # Database Jemaat page
        self.jemaat_page = PlaceholderComponent("Database Jemaat", "Data jemaat yang dibroadcast oleh admin", "#27ae60")
        self.stacked_widget.addWidget(self.jemaat_page)
        
        # Jadwal Kegiatan page  
        self.jadwal_page = PlaceholderComponent("Jadwal Kegiatan", "Jadwal kegiatan gereja yang dibroadcast", "#f39c12")
        self.stacked_widget.addWidget(self.jadwal_page)
        
        # Manajemen Keuangan page
        self.keuangan_page = PlaceholderComponent("Manajemen Keuangan", "Informasi keuangan gereja untuk transparansi", "#e74c3c")
        self.stacked_widget.addWidget(self.keuangan_page)
        
        # Pengumuman page
        self.pengumuman_page = PengumumanComponent(self.api_client)
        self.stacked_widget.addWidget(self.pengumuman_page)
        
        # Dokumen page
        from config import ClientConfig
        config = ClientConfig.load_settings()
        self.dokumen_page = DokumenComponent(self.api_client, config)
        self.stacked_widget.addWidget(self.dokumen_page)
        
        # Aktivitas page (placed at the end)
        self.aktivitas_page = PlaceholderComponent("Aktivitas", "Aktivitas dan kegiatan jemaat yang sedang berlangsung", "#16a085")
        self.stacked_widget.addWidget(self.aktivitas_page)
    
    def create_dashboard_page(self):
        """Create modern dashboard page"""
        page = QWidget()
        page.setStyleSheet("background-color: #f8f9fa;")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Page header with professional admin theme
        header_section = QFrame()
        header_section.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
                padding: 40px 0px;
                border-bottom: 3px solid #3498db;
            }
        """)
        header_layout = QVBoxLayout(header_section)
        header_layout.setContentsMargins(40, 40, 40, 40)
        
        # Page title
        title_label = QLabel("Dashboard")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        
        subtitle_label = QLabel("Selamat datang di Portal Gereja Katolik - Akses informasi jemaat dengan mudah")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                margin-bottom: 0px;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_section)
        
        # Content section
        content_section = QWidget()
        content_layout = QVBoxLayout(content_section)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Welcome card
        welcome_card = QFrame()
        welcome_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e9ecef;
                padding: 30px;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_card)
        
        welcome_title = QLabel("Selamat Datang")
        welcome_title.setStyleSheet("""
            QLabel {
                color: #212529;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 15px;
            }
        """)
        
        welcome_desc = QLabel("Portal ini memberikan akses kepada anggota jemaat untuk melihat informasi yang telah dibroadcast oleh admin gereja.")
        welcome_desc.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 16px;
                line-height: 1.5;
            }
        """)
        welcome_desc.setWordWrap(True)
        
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_desc)
        
        content_layout.addWidget(welcome_card)
        
        # Stats cards row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(20)
        
        # Connection card
        conn_card = self.create_modern_card("Status Koneksi", "Checking...", "#28a745")
        self.connection_card_value = conn_card[1]
        stats_row.addWidget(conn_card[0])
        
        # User info card
        user_card = self.create_modern_card("Informasi User", "Loading...", "#007bff")
        self.user_card_value = user_card[1]
        stats_row.addWidget(user_card[0])
        
        # Last update card
        update_card = self.create_modern_card("Update Terakhir", "Never", "#6f42c1")
        self.update_card_value = update_card[1]
        stats_row.addWidget(update_card[0])
        
        content_layout.addLayout(stats_row)
        content_layout.addStretch()
        
        layout.addWidget(content_section)
        
        return page
    
    def create_modern_card(self, title, value, color):
        """Create modern card for dashboard"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e9ecef;
                padding: 25px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
        """)
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(value_label)
        
        return card, value_label
    
    
    def navigate_to(self, page_key):
        """Navigate to specific page"""
        # Update button styles for elegant navbar
        for key, button in self.nav_buttons.items():
            if key == page_key:
                # Active button style - flat blue design
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        border: none;
                        color: white;
                        font-size: 14px;
                        font-weight: 600;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        padding: 16px 24px;
                        margin: 2px 1px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                        color: white;
                    }
                """)
            else:
                # Inactive button style - clean flat design
                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        color: #ecf0f1;
                        font-size: 14px;
                        font-weight: 500;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        padding: 16px 24px;
                        margin: 2px 1px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #3498db;
                        color: #ffffff;
                    }
                    QPushButton:pressed {
                        background-color: #2980b9;
                    }
                """)
        
        # Show page
        page_indices = {
            "dashboard": 0,
            "jemaat": 1,
            "jadwal": 2,
            "keuangan": 3,
            "pengumuman": 4,
            "dokumen": 5,
            "aktivitas": 6
        }
        
        self.stacked_widget.setCurrentIndex(page_indices.get(page_key, 0))
        
        # Load data for current page if connected
        if self.is_connected:
            self.refresh_current_page()
    
    def show_dashboard(self):
        """Show dashboard page"""
        self.navigate_to("dashboard")
    
    def refresh_current_page(self):
        """Refresh current page data"""
        current_index = self.stacked_widget.currentIndex()
        
        if current_index == 1:  # Jemaat
            if hasattr(self.jemaat_page, 'load_jemaat_data'):
                self.jemaat_page.load_jemaat_data()
                
        elif current_index == 2:  # Jadwal
            if hasattr(self.jadwal_page, 'load_kegiatan_data'):
                self.jadwal_page.load_kegiatan_data()
                
        elif current_index == 3:  # Keuangan
            if hasattr(self.keuangan_page, 'load_keuangan_data'):
                self.keuangan_page.load_keuangan_data()
                
        elif current_index == 4:  # Pengumuman
            if hasattr(self.pengumuman_page, 'load_pengumuman'):
                self.pengumuman_page.load_pengumuman()
            if hasattr(self.pengumuman_page, 'load_broadcast_messages'):
                self.pengumuman_page.load_broadcast_messages()
                
        elif current_index == 5:  # Dokumen
            if hasattr(self.dokumen_page, 'load_files'):
                self.dokumen_page.load_files()
                
        elif current_index == 6:  # Aktivitas
            if hasattr(self.aktivitas_page, 'load_aktivitas_data'):
                self.aktivitas_page.load_aktivitas_data()
    
    def set_user_data(self, user_data):
        """Set user data and update UI"""
        self.user_data = user_data
        if user_data:
            user_name = user_data.get('nama_lengkap', 'User')
            user_role = user_data.get('peran', 'Member')
            
            # Update welcome message in header with comma
            if hasattr(self, 'welcome_title_label'):
                self.welcome_title_label.setText(f"Selamat Datang, {user_name}")
            if hasattr(self, 'welcome_subtitle_label'):
                self.welcome_subtitle_label.setText(f"Portal Gereja Katolik - {user_role}")
            
            
            # Update dashboard user card
            user_info = f"Nama: {user_name}\nPeran: {user_role}"
            self.user_card_value.setText(user_info)
        else:
            # Reset to default when no user is logged in
            if hasattr(self, 'welcome_title_label'):
                self.welcome_title_label.setText("Selamat Datang, Pengguna")
            if hasattr(self, 'welcome_subtitle_label'):
                self.welcome_subtitle_label.setText("Portal Gereja Katolik Santa Maria Ratu Damai")
    
    def set_connection_status(self, connected):
        """Update connection status"""
        self.is_connected = connected
        
        if connected:
            self.connection_status.setText("● Online")
            self.connection_status.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-size: 12px;
                    font-weight: 500;
                }
            """)
            if hasattr(self, 'connection_card_value'):
                self.connection_card_value.setText("Terhubung")
                self.connection_card_value.setStyleSheet("color: #28a745; font-size: 24px; font-weight: bold;")
        else:
            self.connection_status.setText("● Offline") 
            self.connection_status.setStyleSheet("""
                QLabel {
                    color: #dc3545;
                    font-size: 12px;
                    font-weight: 500;
                }
            """)
            if hasattr(self, 'connection_card_value'):
                self.connection_card_value.setText("Tidak Terhubung")
                self.connection_card_value.setStyleSheet("color: #dc3545; font-size: 24px; font-weight: bold;")
    
    def darken_color(self, color):
        """Darken a color for hover effects"""
        color_map = {
            "#3498db": "#2980b9",  # Blue
            "#27ae60": "#229954",  # Green
            "#f39c12": "#e67e22",  # Orange
            "#e74c3c": "#c0392b",  # Red
            "#9b59b6": "#8e44ad",  # Purple
            "#34495e": "#2c3e50",  # Dark blue-gray
            "#f1c40f": "#f39c12",  # Yellow
            "#95a5a6": "#7f8c8d"   # Gray
        }
        return color_map.get(color, "#2c3e50")
    
    def setup_timers(self):
        """Setup timers for periodic updates"""
        # Timer untuk update dashboard
        self.dashboard_timer = QTimer()
        self.dashboard_timer.timeout.connect(self.update_dashboard)
        self.dashboard_timer.start(30000)  # Update every 30 seconds
    
    def update_dashboard(self):
        """Update dashboard information"""
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.update_card_value.setText(f"Terakhir: {current_time}")
    
    def setup_system_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
            
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Tampilkan")
            show_action.triggered.connect(self.show)
            
            quit_action = tray_menu.addAction("Keluar")
            quit_action.triggered.connect(self.close)  # type: ignore
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
    def show_profile_menu(self):
        """Tampilkan dropdown menu profile user"""
        if not self.user_data:
            QMessageBox.warning(self, "Perhatian", "Anda belum login!")
            return
            
        # Buat menu dropdown
        profile_menu = QMenu(self)
        profile_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 8px 0px;
                min-width: 220px;
            }
            QMenu::item {
                padding: 12px 20px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2c3e50;
                border: none;
            }
            QMenu::item:hover {
                background-color: #f8f9fa;
                color: #3498db;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e9ecef;
                margin: 8px 16px;
            }
        """)
        
        # Menu items
        user_name = self.user_data.get('nama_lengkap', 'User')
        user_role = self.user_data.get('peran', 'Member')
        
        # Header info user (non-clickable)
        user_info_text = f"{user_name}\n{user_role}"
        user_info_action = profile_menu.addAction(f"👤  {user_name}")
        user_info_action.setEnabled(False)
        user_info_action.setFont(QFont("Segoe UI", 12, QFont.Bold))
        
        role_action = profile_menu.addAction(f"     {user_role}")
        role_action.setEnabled(False)
        
        profile_menu.addSeparator()
        
        # Pengaturan akun
        settings_action = profile_menu.addAction("⚙️  Pengaturan Akun")
        settings_action.triggered.connect(self.show_account_settings)
        
        # Ubah kata sandi
        change_password_action = profile_menu.addAction("🔒  Ubah Kata Sandi")
        change_password_action.triggered.connect(self.show_change_password_dialog)
        
        profile_menu.addSeparator()
        
        # Logout
        logout_action = profile_menu.addAction("🚪  Logout")
        logout_action.triggered.connect(self.logout_user)
        
        # Tampilkan menu di posisi button
        button_pos = self.profile_button.mapToGlobal(self.profile_button.rect().bottomLeft())
        profile_menu.exec_(button_pos)
    
    def show_account_settings(self):
        """Tampilkan dialog pengaturan akun"""
        if not self.user_data:
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Pengaturan Akun")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Informasi Akun")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # User info
        user_info = QFormLayout()
        
        name_label = QLabel("Nama Lengkap:")
        name_value = QLabel(self.user_data.get('nama_lengkap', 'N/A'))
        name_value.setStyleSheet("font-weight: bold; color: #3498db;")
        
        role_label = QLabel("Peran:")
        role_value = QLabel(self.user_data.get('peran', 'N/A'))
        role_value.setStyleSheet("font-weight: bold; color: #27ae60;")
        
        username_label = QLabel("Username:")
        username_value = QLabel(self.user_data.get('username', 'N/A'))
        username_value.setStyleSheet("font-weight: bold; color: #6c757d;")
        
        user_info.addRow(name_label, name_value)
        user_info.addRow(role_label, role_value)
        user_info.addRow(username_label, username_value)
        
        layout.addLayout(user_info)
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Tutup")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(dialog.accept)  # type: ignore
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def show_change_password_dialog(self):
        """Tampilkan dialog ubah kata sandi"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ubah Kata Sandi")
        dialog.setFixedSize(400, 250)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #e9ecef;
                border-radius: 5px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Ubah Kata Sandi")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Form
        form_layout = QFormLayout()
        
        old_password = QLineEdit()
        old_password.setEchoMode(QLineEdit.Password)
        old_password.setPlaceholderText("Masukkan kata sandi lama")
        
        new_password = QLineEdit()
        new_password.setEchoMode(QLineEdit.Password)
        new_password.setPlaceholderText("Masukkan kata sandi baru")
        
        confirm_password = QLineEdit()
        confirm_password.setEchoMode(QLineEdit.Password)
        confirm_password.setPlaceholderText("Konfirmasi kata sandi baru")
        
        form_layout.addRow("Kata Sandi Lama:", old_password)
        form_layout.addRow("Kata Sandi Baru:", new_password)
        form_layout.addRow("Konfirmasi:", confirm_password)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)  # type: ignore
        
        save_btn = QPushButton("Simpan")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        save_btn.clicked.connect(lambda: self.change_password(
            old_password.text(),
            new_password.text(),
            confirm_password.text(),
            dialog
        ))
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def change_password(self, old_pass, new_pass, confirm_pass, dialog):
        """Proses ubah kata sandi"""
        if not all([old_pass, new_pass, confirm_pass]):
            QMessageBox.warning(dialog, "Error", "Semua field harus diisi!")
            return
            
        if new_pass != confirm_pass:
            QMessageBox.warning(dialog, "Error", "Kata sandi baru tidak cocok!")
            return
            
        if len(new_pass) < 6:
            QMessageBox.warning(dialog, "Error", "Kata sandi minimal 6 karakter!")
            return
        
        try:
            # Implementasi API call untuk ubah password
            username = self.user_data.get('username')
            result = self.api_client.change_password(username, old_pass, new_pass)
            
            if result.get('success'):
                QMessageBox.information(dialog, "Berhasil", "Kata sandi berhasil diubah!")
                dialog.accept()
            else:
                error_msg = result.get('data', 'Gagal mengubah kata sandi')
                QMessageBox.warning(dialog, "Error", f"Gagal mengubah kata sandi:\n{error_msg}")
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Terjadi kesalahan:\n{str(e)}")
    
    def logout_user(self):
        """Logout user dan kembali ke halaman login"""
        reply = QMessageBox.question(self, "Konfirmasi Logout", 
                                   "Apakah Anda yakin ingin logout?",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Reset user data
            self.user_data = None
            self.set_user_data(None)
            self.set_connection_status(False)
            
            # Clear API client session
            if hasattr(self.api_client, 'logout'):
                try:
                    self.api_client.logout()
                except:
                    pass
            
            # Tutup window dan kembali ke login
            self.hide()
            
            # Tampilkan dialog login lagi
            login_dialog = LoginDialog(self)
            if login_dialog.exec_() == QDialog.Accepted:
                user_data = login_dialog.get_user_data()
                if user_data:
                    self.set_user_data(user_data)
                    self.set_connection_status(True)
                    self.show()
                else:
                    self.close()
            else:
                self.close()