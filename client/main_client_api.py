# Path: client/main_client_api.py

import sys
import os
import json
from typing import Optional, Dict, Any

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTabWidget, QTextEdit, QPushButton,
                            QLabel, QLineEdit, QMessageBox, QStatusBar, QFrame,
                            QSplitter, QSystemTrayIcon, QMenu, QDialog)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon

# Use absolute imports with type ignore to suppress warnings
from api_client import ApiClient  # type: ignore
from threading_utils import Worker, AsyncAPICall  # type: ignore
from components.login_dialog import LoginDialog  # type: ignore
from components.pengumuman_component import PengumumanComponent  # type: ignore
from components.dokumen_component import DokumenComponent  # type: ignore
from components.jemaat_component import JemaatClientComponent  # type: ignore
from components.keuangan_component import KeuanganClientComponent  # type: ignore
from components.proker_component import ProkerComponent  # type: ignore
from components.kegiatan_component import KegiatanClientComponent  # type: ignore
from components.profile_dialog import ProfileDialog  # type: ignore
from components.activity_dialog import ActivityDialog  # type: ignore

# ============================================================================
# CLIENT CONFIG - Pindah dari config.py ke sini untuk menghindari PyInstaller issues
# ============================================================================
class ClientConfig:
    """Konfigurasi aplikasi client"""

    # Path default untuk file konfigurasi pengguna
    CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), '.gereja_client_settings.json')

    # Default values
    DEFAULT_API_URL = os.getenv('DEFAULT_API_URL', 'http://localhost:3000')
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

# ============================================================================

class ClientMainWindow(QMainWindow):

    message_received: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client Gereja Katolik - API Mode")
        self.setMinimumSize(1000, 700)

        self.api_client = ApiClient()
        self.user_data = None
        self.is_connected = False
        self.config = ClientConfig.load_settings()
        # self.last_message_count = 0

        # Initialize status bar early
        self.status_bar: QStatusBar = QStatusBar()

        # Dialog instances
        self.profile_dialog = None
        self.activity_dialog = None

        # Profile icon state
        self.profile_showing_text = False
        
        self.setup_ui()
        self.setup_timers()
        self.setup_system_tray()

        # Set status bar (already initialized above)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Belum terhubung ke API")
        
        self.show_login()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_frame = QFrame()
        header_frame.setMinimumHeight(90)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #073642;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(12)

        # Logo gereja
        logo_label = QLabel()
        logo_path = "client/assets/logo_gereja.png"
        if os.path.exists(logo_path):
            try:
                from PyQt5.QtGui import QPixmap
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    logo_label.setPixmap(pixmap.scaled(65, 65, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    logo_label.setFixedSize(65, 65)
                else:
                    logo_label.setText("")
            except Exception:
                logo_label.setText("")
        else:
            logo_label.setText("")
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)

        # Title and subtitle container
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        title_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Main title - 1 baris
        title_label = QLabel("PAROKI SANTA MARIA RATU DAMAI, ULUINDANO")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #ecf0f1; background-color: transparent;")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Panel Wilayah Rohani (Client)")
        subtitle_label.setFont(QFont("Arial", 9))
        subtitle_label.setStyleSheet("color: #bdc3c7; background-color: transparent;")
        subtitle_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_layout.addWidget(subtitle_label)

        header_layout.addWidget(title_container, 1)

        # Icon layout for right side
        icons_layout = QHBoxLayout()

        # Activity history icon
        self.activity_icon = QPushButton()
        self.activity_icon.setFixedSize(35, 35)

        # Try to load notification icon
        notification_icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'notification.png')
        if os.path.exists(notification_icon_path):
            try:
                icon = QIcon(notification_icon_path)
                if not icon.isNull():
                    self.activity_icon.setIcon(icon)
                    self.activity_icon.setIconSize(QSize(20, 20))
                else:
                    self.activity_icon.setText("🔔")  # Fallback to emoji
            except Exception:
                self.activity_icon.setText("🔔")  # Fallback to emoji
        else:
            self.activity_icon.setText("🔔")  # Fallback to emoji

        self.activity_icon.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 17px;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.activity_icon.setToolTip("Riwayat Aktivitas")
        self.activity_icon.clicked.connect(self.show_activity_dialog)  # type: ignore

        # User profile photo icon
        self.profile_icon = QPushButton()
        self.profile_icon.setFixedSize(35, 35)
        self.profile_icon.setText("U")  # Will be updated with user initial
        self.profile_icon.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 17px;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #d5d8dc;
                border-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #bdc3c7;
            }
        """)
        self.profile_icon.setToolTip("Profil Pengguna")
        self.profile_icon.clicked.connect(self.show_profile_dialog)  # type: ignore

        # Store profile image path for custom photos
        self.profile_image_path = None

        # Connection status
        self.connection_status_widget = QWidget()
        status_layout = QVBoxLayout(self.connection_status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(2)

        self.user_label = QLabel("Belum Login")
        self.user_label.setStyleSheet("color: #ecf0f1; font-size: 11px;")

        self.connection_label = QLabel("● Offline")
        self.connection_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 10px;")

        status_layout.addWidget(self.user_label)
        status_layout.addWidget(self.connection_label)

        # Add to icons layout
        icons_layout.addWidget(self.connection_status_widget)
        icons_layout.addWidget(self.activity_icon)
        icons_layout.addWidget(self.profile_icon)

        # Add to header layout
        header_layout.addStretch()
        header_layout.addLayout(icons_layout)
        
        main_layout.addWidget(header_frame)
        
        # Main content dengan splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tab Widget untuk konten utama
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # Tab Dashboard/Info
        self.dashboard_tab = self.create_dashboard_tab()
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")

        # Tab Database Umat
        self.jemaat_component = JemaatClientComponent(self.api_client)
        self.jemaat_component.log_message.connect(self.add_log)
        self.tab_widget.addTab(self.jemaat_component, "Database Umat")

        # Tab Keuangan WR
        self.keuangan_component = KeuanganClientComponent(self.api_client)
        self.keuangan_component.log_message.connect(self.add_log)
        self.tab_widget.addTab(self.keuangan_component, "Keuangan WR")

        # Tab Program Kerja WR
        self.proker_component = ProkerComponent(self, self.api_client, self.user_data)
        self.proker_component.log_message.connect(self.add_log)
        self.tab_widget.addTab(self.proker_component, "Program Kerja WR")

        # Tab Kegiatan WR
        self.kegiatan_component = KegiatanClientComponent(self.api_client)
        self.kegiatan_component.log_message.connect(self.add_log)
        self.tab_widget.addTab(self.kegiatan_component, "Kegiatan WR")

        # Tab Pengumuman
        self.pengumuman_component = PengumumanComponent(self.api_client)
        self.tab_widget.addTab(self.pengumuman_component, "Pengumuman")

        # Tab Dokumen
        self.dokumen_component = DokumenComponent(self.api_client, self.config)
        self.tab_widget.addTab(self.dokumen_component, "Dokumen")
        
        splitter.addWidget(self.tab_widget)
        
        # # Panel komunikasi di sebelah kanan
        # communication_panel = self.create_communication_panel()
        # splitter.addWidget(communication_panel)
        
        # Set ukuran splitter
        # splitter.setSizes([700, 300])
        # main_layout.addWidget(splitter)
        main_layout.addWidget(self.tab_widget)
        
        # Control buttons
        control_layout = self.create_control_buttons()
        main_layout.addLayout(control_layout)
    
    def create_dashboard_tab(self):
        """Membangun tab Dashboard dengan kotak‑kotak informasi rapi."""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)

        # ===== helper umum untuk membuat kotak informasi =====
        def _build_box(title: str):
            frame = QFrame()
            frame.setObjectName("infoBox")
            frame.setStyleSheet("""
                /* HANYA berlaku untuk QFrame bernama infoBox */
                QFrame#infoBox {
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    background: #ffffff;
                }
                /* Hilangkan border / padding turunan pada semua QLabel di kotak ini */
                QFrame#infoBox QLabel {
                    border: 0px;
                    padding: 0px;
                }
            """)
            inner = QVBoxLayout(frame)
            inner.setContentsMargins(12, 12, 12, 12)   # ganti fungsi padding lama
            title_lbl = QLabel(title)
            title_lbl.setFont(QFont("Arial", 12, QFont.Bold))
            inner.addWidget(title_lbl)
            return frame, inner
        # =====================================================

        # 1) Status koneksi -----------------------------------
        status_frame, status_layout = _build_box("Status Koneksi API")
        self.api_status_label = QLabel("Belum terhubung")
        self.api_status_label.setStyleSheet("color: #e74c3c; font-size: 14px;")
        status_layout.addWidget(self.api_status_label)

        self.client_info_label = QLabel(f"IP Client: {self.api_client.client_ip}")
        self.client_info_label.setStyleSheet("color: #7f8c8d;")
        status_layout.addWidget(self.client_info_label)

        # Informasi perangkat
        device_info = self.api_client.device_info
        device_text = f"Perangkat: {device_info.get('platform', 'Unknown')} {device_info.get('platform_version', '')}"
        self.device_info_label = QLabel(device_text)
        self.device_info_label.setStyleSheet("color: #7f8c8d;")
        status_layout.addWidget(self.device_info_label)
        
        hostname_text = f"Hostname: {self.api_client.client_hostname}"
        self.hostname_label = QLabel(hostname_text)
        self.hostname_label.setStyleSheet("color: #7f8c8d;")
        status_layout.addWidget(self.hostname_label)
        layout.addWidget(status_frame)

        # 2) Informasi API ------------------------------------
        info_frame, info_layout = _build_box("Informasi API")
        self.api_url_label = QLabel(f"URL API: {self.api_client.base_url}")
        info_layout.addWidget(self.api_url_label)

        self.api_version_label = QLabel("Status API: Memuat...")
        info_layout.addWidget(self.api_version_label)
        layout.addWidget(info_frame)

        # 3) Informasi Pengguna -------------------------------
        user_frame, user_layout = _build_box("Informasi Pengguna")
        self.user_info_label = QLabel("Belum login")
        user_layout.addWidget(self.user_info_label)
        layout.addWidget(user_frame)

        layout.addStretch()
        return dashboard_widget
    
    # def create_communication_panel(self):
    #     """Buat panel komunikasi"""
    #     comm_widget = QWidget()
    #     comm_widget.setMaximumWidth(350)
    #     layout = QVBoxLayout(comm_widget)
        
        # Header panel komunikasi
        # comm_header = QLabel("Panel Komunikasi")
        # comm_header.setFont(QFont("Arial", 12, QFont.Bold))
        # comm_header.setStyleSheet("background-color: #34495e; color: white; padding: 8px; border-radius: 4px;")
        # layout.addWidget(comm_header)
        
        # Log komunikasi
        # log_label = QLabel("Log Sistem:")
        # log_label.setFont(QFont("Arial", 10, QFont.Bold))
        # layout.addWidget(log_label)
        
        # self.communication_log = QTextEdit()
        # self.communication_log.setReadOnly(True)
        # self.communication_log.setFont(QFont("Courier New", 9))
        # self.communication_log.setMaximumHeight(200)
        # layout.addWidget(self.communication_log)
        
        # Input pesan ke admin
        # message_layout = QHBoxLayout()
        
        # self.message_input = QLineEdit()
        # self.message_input.setPlaceholderText("Ketik pesan untuk admin...")
        # self.message_input.returnPressed.connect(self.send_message_to_admin)
        
        # self.send_button = QPushButton("Kirim")
        # self.send_button.clicked.connect(self.send_message_to_admin)
        # self.send_button.setEnabled(False)
        # self.send_button.setStyleSheet("""
        #     QPushButton {
        #         background-color: #3498db;
        #         color: white;
        #         padding: 6px 12px;
        #         border: none;
        #         border-radius: 4px;
        #     }
        #     QPushButton:hover {
        #         background-color: #2980b9;
        #     }
        # """)
        
        # message_layout.addWidget(self.message_input)
        # message_layout.addWidget(self.send_button)
        
        # layout.addLayout(message_layout)
        
        # Notifikasi broadcast
        # self.broadcast_notification = QLabel("Siap menerima broadcast...")
        # self.broadcast_notification.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        # layout.addWidget(self.broadcast_notification)
        
        # Clear log button
        # clear_layout = QHBoxLayout()
        # clear_layout.addStretch()
        
        # self.clear_log_button = QPushButton("Bersihkan Log")
        # self.clear_log_button.clicked.connect(self.clear_communication_log)
        # self.clear_log_button.setStyleSheet("""
        #     QPushButton {
        #         background-color: #95a5a6;
        #         color: white;
        #         padding: 4px 8px;
        #         border: none;
        #         border-radius: 3px;
        #     }
        #     QPushButton:hover {
        #         background-color: #7f8c8d;
        #     }
        # """)
        # clear_layout.addWidget(self.clear_log_button)
        
        # layout.addLayout(clear_layout)
        # layout.addStretch()
        
        # return comm_widget
    
    def create_control_buttons(self):
        """Buat tombol kontrol"""
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        
        # Connection toggle button with text-only style
        self.connection_toggle_button = QPushButton("Hubungkan ke API")
        self.connection_toggle_button.clicked.connect(self.toggle_connection)
        self.connection_toggle_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #3498db;
                padding: 8px 16px;
                text-decoration: underline;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #2980b9;
                text-decoration: underline;
            }
            QPushButton:pressed {
                color: #1c5a7a;
            }
        """)
        
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.refresh_all_data)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        control_layout.addWidget(self.connection_toggle_button)
        control_layout.addWidget(self.refresh_button)
        
        return control_layout
    
    def setup_timers(self):
        # Timer untuk check koneksi dan update data
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.periodic_update)
        self.update_timer.start(15000)  # Update setiap 15 detik
        
        # Timer untuk heartbeat ke server
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.send_heartbeat)
        self.heartbeat_timer.start(30000)  # Heartbeat setiap 30 detik
        
        # Timer untuk check broadcast messages
        # self.broadcast_timer = QTimer()
        # self.broadcast_timer.timeout.connect(self.check_new_broadcasts)
        # self.broadcast_timer.start(5000)  # Check setiap 5 detik
    
    def setup_system_tray(self):
        """Setup system tray untuk notifikasi"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Set icon (gunakan icon default jika tidak ada)
            self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
            
            # Context menu untuk tray
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Tampilkan")
            show_action.triggered.connect(self.show)  # type: ignore
            
            quit_action = tray_menu.addAction("Keluar")
            quit_action.triggered.connect(self.close)  # type: ignore
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
    def show_login(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            self.user_data = login_dialog.get_user_data()
            if self.user_data:
                self.api_client.user_data = self.user_data
                self.user_label.setText(self.user_data.get('nama_lengkap', 'Unknown'))
                self.user_info_label.setText(f"Nama: {self.user_data.get('nama_lengkap', 'Unknown')}\nUsername: {self.user_data.get('username', 'Unknown')}\nPeran: {self.user_data.get('peran', 'Unknown')}")
                self.add_log("Login berhasil sebagai " + self.user_data.get('nama_lengkap', 'Unknown'))

                # Tampilkan window utama setelah login berhasil
                self.show()
                self.raise_()
                self.activateWindow()

                # Check and download profile photo if exists
                foto_profil = self.user_data.get('foto_profil')
                if foto_profil:
                    try:
                        # Debug print
                        print(f"[DEBUG] Found profile photo: {foto_profil}")
                        cache_dir = os.path.join(current_dir, 'cache', 'profiles')
                        result = self.api_client.download_profile_photo(foto_profil, cache_dir)
                        if result['success']:
                            self.profile_image_path = result['data']
                            self.add_log(f"Foto profil berhasil diunduh: {self.profile_image_path}")
                            print(f"[DEBUG] Photo downloaded to: {self.profile_image_path}")
                        else:
                            self.add_log(f"Gagal mengunduh foto profil: {result['data']}")
                            print(f"[DEBUG] Download failed: {result['data']}")
                    except Exception as e:
                        print(f"[ERROR] Error downloading profile photo: {e}")

                # Update profile icon
                self.update_profile_icon()

                # Clear dan refresh semua component setelah user_data di-set
                self.keuangan_component.keuangan_data = []
                self.keuangan_component.filtered_data = []
                self.jemaat_component.jemaat_data = []
                self.jemaat_component.filtered_data = []

                self.keuangan_component.load_user_keuangan_data()
                self.jemaat_component.load_user_jemaat_data()

                # Log activity
                if self.activity_dialog:
                    username = self.user_data.get('nama_lengkap', 'Unknown')
                    self.activity_dialog.log_login_success(username)

                # Connect ke API
                self.connect_to_api()
            else:
                QMessageBox.critical(self, "Error", "Data user tidak valid")
                self.close()
        else:
            self.close()

    def update_profile_icon(self):
        """Update profile icon with user's initial or photo"""
        if self.user_data:
            nama = self.user_data.get('nama_lengkap', 'U')
            if nama:
                initial = nama[0].upper()

                # Check if there's a saved profile photo
                if hasattr(self, 'profile_image_path') and self.profile_image_path:
                    try:
                        from PyQt5.QtGui import QPixmap, QPainter, QPainterPath, QImage
                        # Load via QImage to bypass QPixmap cache
                        image = QImage(self.profile_image_path)
                        if not image.isNull():
                            pixmap = QPixmap.fromImage(image)
                            
                            # Create circular pixmap
                            size = 35
                            scaled_pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                            circular_pixmap = QPixmap(size, size)
                            circular_pixmap.fill(Qt.GlobalColor.transparent)

                            painter = QPainter(circular_pixmap)
                            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                            path = QPainterPath()
                            path.addEllipse(0, 0, size, size)
                            painter.setClipPath(path)
                            
                            # Center the image
                            x = (size - scaled_pixmap.width()) // 2
                            y = (size - scaled_pixmap.height()) // 2
                            painter.drawPixmap(x, y, scaled_pixmap)
                            
                            painter.end()

                            self.profile_icon.setIcon(QIcon(circular_pixmap))
                            self.profile_icon.setIconSize(QSize(31, 31))
                            self.profile_icon.setText("")
                        else:
                            # Invalid image, fallback to text
                            self.profile_icon.setIcon(QIcon())
                            self.profile_icon.setText(initial)
                    except Exception as e:
                        print(f"Error loading profile image: {e}")
                        self.profile_icon.setIcon(QIcon())
                        self.profile_icon.setText(initial)
                else:
                    # No photo, show initial
                    self.profile_icon.setIcon(QIcon())
                    self.profile_icon.setText(initial)

    def update_profile_photo(self, image_path):
        """Update profile photo when changed from profile dialog"""
        if image_path:
            self.profile_image_path = image_path
        else:
            # Photo removed
            self.profile_image_path = None
        self.update_profile_icon()

    def toggle_connection(self):
        """Toggle connection status"""
        if self.is_connected:
            self.disconnect_from_api()
        else:
            self.connect_to_api()

    def update_connection_button(self):
        """Update connection button text and style based on connection status"""
        if self.is_connected:
            self.connection_toggle_button.setText("Terhubung")
            self.connection_toggle_button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #27ae60;
                    padding: 8px 16px;
                    text-decoration: underline;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    color: #2ecc71;
                    text-decoration: underline;
                }
                QPushButton:pressed {
                    color: #1e8449;
                }
            """)
        else:
            self.connection_toggle_button.setText("Hubungkan ke API")
            self.connection_toggle_button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #3498db;
                    padding: 8px 16px;
                    text-decoration: underline;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    color: #2980b9;
                    text-decoration: underline;
                }
                QPushButton:pressed {
                    color: #1c5a7a;
                }
            """)

    def on_tab_changed(self, index):
        """Refresh data when tab changes"""
        if self.api_client.user_data:
            if index == 1:  # Database Umat tab
                self.jemaat_component.load_user_jemaat_data()
            elif index == 2:  # Keuangan WR tab
                self.keuangan_component.load_user_keuangan_data()

    def connect_to_api(self):
        """Connect to API using background thread"""
        self.add_log("Mencoba terhubung ke API...")
        self.connection_label.setText("● Mencoba...")
        self.connection_label.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 10px;")

        # Create worker thread untuk connection check
        worker = AsyncAPICall(self.api_client.check_server_connection)
        worker.success.connect(self._on_connection_check_success)
        worker.error.connect(self._on_connection_check_error)
        self._connection_worker = worker
        worker.start()

    def _on_connection_check_success(self, result):
        """Handle successful server connection check"""
        self.add_log("Server connection OK, registering client...")

        # Now register client
        worker = AsyncAPICall(self.api_client.register_client)
        worker.success.connect(self._on_client_registration_success)
        worker.error.connect(self._on_client_registration_error)
        self._registration_worker = worker
        worker.start()

    def _on_connection_check_error(self, error_type, error_msg):
        """Handle server connection check error"""
        QMessageBox.warning(self, f"Error {error_type}", f"Gagal terhubung ke API:\n{error_msg}")
        self.add_log(f"ERROR: Gagal terhubung ke API - {error_msg}")
        print(f"[ERROR] API connection failed: {error_type} - {error_msg}")

        self.connection_label.setText("● Offline")
        self.connection_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 10px;")

    def _on_client_registration_success(self, result):
        """Handle successful client registration"""
        self.is_connected = True
        self.connection_label.setText("● Online")
        self.connection_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 10px;")

        self.api_status_label.setText("Terhubung ke API")
        self.api_status_label.setStyleSheet("color: #27ae60; font-size: 14px;")
        self.status_bar.showMessage("Terhubung ke API dan terdaftar")

        # Update connection button
        self.update_connection_button()

        # Log informasi client
        user_name = self.user_data.get('nama_lengkap', 'Unknown') if self.user_data else 'Unknown'
        user_role = self.user_data.get('peran', 'Unknown') if self.user_data else 'Unknown'
        session_id = self.api_client.session_id
        connection_id = self.api_client.connection_id
        device_info = self.api_client.device_info

        self.add_log(f"Client terdaftar: {user_name} ({user_role})")
        self.add_log(f"IP Address: {self.api_client.client_ip}")
        self.add_log(f"Hostname: {self.api_client.client_hostname}")
        self.add_log(f"Perangkat: {device_info.get('platform', 'Unknown')} {device_info.get('platform_version', '')}")
        self.add_log(f"Session ID: {session_id}")
        if connection_id:
            self.add_log(f"Connection ID: {connection_id}")

        print(f"=== CLIENT CONNECTED ===")
        print(f"User: {user_name} ({user_role})")
        print(f"Device: {device_info.get('platform', 'Unknown')} - {self.api_client.client_hostname}")
        print(f"IP: {self.api_client.client_ip}")
        print(f"Session: {session_id}")
        if connection_id:
            print(f"Connection ID: {connection_id}")
        print(f"=======================")

        # Load data in parallel (NON-BLOCKING)
        self.add_log("Loading data in background...")
        self.refresh_all_data()

        # Start timers untuk heartbeat
        self.heartbeat_timer.start()

        # Log activity
        if self.activity_dialog:
            self.activity_dialog.log_connection_success()

    def _on_client_registration_error(self, error_type, error_msg):
        """Handle client registration error"""
        QMessageBox.warning(self, f"Error {error_type}", f"Gagal registrasi client:\n{error_msg}")
        self.add_log(f"ERROR: Gagal registrasi client - {error_msg}")
        print(f"[ERROR] Client registration failed: {error_type} - {error_msg}")

        self.connection_label.setText("● Offline")
        self.connection_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 10px;")
    
    def disconnect_from_api(self):
        if self.is_connected:
            # Disconnect dari API
            result = self.api_client.disconnect_client()
            self.add_log("Memutuskan koneksi dari API...")
        
        self.is_connected = False
        self.connection_label.setText("● Offline")
        self.connection_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 10px;")
        
        self.api_status_label.setText("Terputus dari API")
        self.api_status_label.setStyleSheet("color: #e74c3c; font-size: 14px;")

        # Update connection button
        self.update_connection_button()
        
        self.status_bar.showMessage("Terputus dari API")
        print("Koneksi API terputus")
        
        # Stop timers
        self.heartbeat_timer.stop()
        # self.broadcast_timer.stop()
    
    def send_heartbeat(self):
        """Kirim heartbeat ke server untuk update status"""
        if self.is_connected and self.api_client.session_id:
            result = self.api_client.heartbeat()
            if not result["success"]:
                # Heartbeat gagal tidak masalah, log saja
                print(f"[DEBUG] Heartbeat failed: {result.get('data', 'Unknown error')}")
    
    def auto_reconnect(self):
        """Coba reconnect otomatis ke API"""
        if self.user_data:
            self.add_log("Mencoba reconnect otomatis...")
            self.disconnect_from_api()
            self.connect_to_api()
    
    # def send_message_to_admin(self):
    #     """Kirim pesan ke admin"""
    #     if not self.is_connected:
    #         QMessageBox.warning(self, "Error", "Tidak terhubung ke API")
    #         return
    #     
    #     message = self.message_input.text().strip()
    #     if not message:
    #         return
    #     
    #     result = self.api_client.send_message_to_admin(message)
    #     if result["success"]:
    #         self.add_log(f"[Pesan ke Admin]: {message}")
    #         self.message_input.clear()
    #     else:
    #         self.add_log(f"Gagal mengirim pesan: {result['data']}")
    
    # def check_new_broadcasts(self):
    #     """Check pesan broadcast baru dari admin"""
    #     if not self.is_connected:
    #         return
    #     
    #     result = self.api_client.get_broadcast_messages(limit=20)
    #     if result["success"]:
    #         data = result["data"]
    #         if data.get("status") == "success":
    #             messages = data.get("data", [])
    #             current_count = len(messages)
    #             
    #             if current_count > self.last_message_count:
    #                 # Ada pesan baru
    #                 new_message_count = current_count - self.last_message_count
    #                 self.broadcast_notification.setText(f"Pesan broadcast baru: +{new_message_count}")
    #                 self.broadcast_notification.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
    #                 
    #                 # Tampilkan notifikasi sistem tray jika ada
    #                 if hasattr(self, 'tray_icon') and new_message_count > 0:
    #                     self.tray_icon.showMessage(
    #                         "Pesan Broadcast Baru",
    #                         f"Diterima {new_message_count} pesan broadcast dari admin",
    #                         QSystemTrayIcon.Information,
    #                         3000
    #                     )
    #                 
    #                 # Log pesan terbaru
    #                 if messages:
    #                     latest_message = messages[0]
    #                     pesan_content = latest_message.get('pesan', '')
    #                     if len(pesan_content) > 50:
    #                         pesan_content = pesan_content[:50] + "..."
    #                     self.add_log(f"[Broadcast Admin]: {pesan_content}")
    #                 
    #                 # Reset notification style setelah 5 detik
    #                 QTimer.singleShot(5000, self.reset_broadcast_notification)
    #                 
    #             self.last_message_count = current_count
    
    # def reset_broadcast_notification(self):
    #     """Reset style notifikasi broadcast"""
    #     self.broadcast_notification.setText("Siap menerima broadcast...")
    #     self.broadcast_notification.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")

    def refresh_all_data(self):
        """Load all data - components handle their own threading safely"""
        if not self.is_connected:
            return

        print("Refreshing all data...")
        self.add_log("Memuat data: jemaat, keuangan, program kerja, kegiatan, pengumuman, dokumen...")

        # Each component loads its own data with proper threading (thread-safe)
        # Components emit signals for UI updates, ensuring main thread updates
        if hasattr(self.jemaat_component, 'load_user_jemaat_data'):
            self.jemaat_component.load_user_jemaat_data()

        if hasattr(self.keuangan_component, 'load_user_keuangan_data'):
            self.keuangan_component.load_user_keuangan_data()

        if hasattr(self.proker_component, 'load_data'):
            self.proker_component.load_data()

        if hasattr(self.kegiatan_component, 'load_kegiatan_data'):
            self.kegiatan_component.load_kegiatan_data()

        self.pengumuman_component.load_pengumuman()

        if hasattr(self.dokumen_component, 'load_files'):
            self.dokumen_component.load_files()
    
    def periodic_update(self):
        if self.is_connected:
            # Refresh data secara berkala
            current_tab = self.tab_widget.currentIndex()

            if current_tab == 1:  # Tab Database Umat
                # Auto refresh jemaat data jika diperlukan
                if hasattr(self.jemaat_component, 'auto_refresh_data'):
                    self.jemaat_component.auto_refresh_data()
            elif current_tab == 2:  # Tab Keuangan WR
                # Auto refresh keuangan data jika diperlukan
                if hasattr(self.keuangan_component, 'auto_refresh_data'):
                    self.keuangan_component.auto_refresh_data()
            elif current_tab == 3:  # Tab Kegiatan WR
                # Auto refresh kegiatan data jika diperlukan
                if hasattr(self.kegiatan_component, 'auto_refresh_data'):
                    self.kegiatan_component.auto_refresh_data()
            elif current_tab == 4:  # Tab Pengumuman
                # Auto refresh pengumuman jika diperlukan
                if hasattr(self.pengumuman_component, 'load_pengumuman'):
                    self.pengumuman_component.load_pengumuman()
            elif current_tab == 5:  # Tab Dokumen
                pass  # Dokumen tidak perlu auto refresh
    
    def add_log(self, message):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Print to console jika communication_log tidak tersedia
        if hasattr(self, 'communication_log'):
            self.communication_log.append(log_entry)
            scrollbar = self.communication_log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            print(log_entry)
    
    # def clear_communication_log(self):
    #     self.communication_log.clear()
    #     self.add_log("Log komunikasi dibersihkan")

    def show_profile_dialog(self):
        """Show user profile dialog and toggle button text"""
        if not self.user_data:
            QMessageBox.warning(self, "Error", "User data tidak tersedia")
            return

        # Toggle button appearance
        if not self.profile_showing_text:
            # Show text instead of icon
            self.profile_icon.setText("Profil Pengguna")
            self.profile_icon.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #2c3e50;
                    border: none;
                    font-size: 12px;
                    font-weight: normal;
                    text-align: center;
                }
                QPushButton:hover {
                    color: #3498db;
                    text-decoration: underline;
                }
            """)
            self.profile_showing_text = True

            # Show profile dialog
            if self.profile_dialog is None:
                self.profile_dialog = ProfileDialog(
                    self.user_data,
                    self.is_connected,
                    self.api_client,
                    self
                )
                self.profile_dialog.logout_requested.connect(self.handle_logout)  # type: ignore
                self.profile_dialog.photo_updated.connect(self.update_profile_photo)  # type: ignore
                self.profile_dialog.dialog_closed.connect(self.restore_profile_icon)  # type: ignore
            else:
                # Update data jika dialog sudah ada
                self.profile_dialog.update_user_data(self.user_data)
                self.profile_dialog.update_connection_status_external(self.is_connected)

            # Load current profile image
            if hasattr(self, 'profile_image_path') and self.profile_image_path:
                self.profile_dialog.load_profile_image(self.profile_image_path)
            else:
                # Force reset if no image path exists for current user
                self.profile_dialog.reset_profile_image()

            self.profile_dialog.show()
            self.profile_dialog.raise_()
            self.profile_dialog.activateWindow()
        else:
            # Already showing text, just show dialog
            if self.profile_dialog and not self.profile_dialog.is_closing:
                self.profile_dialog.show()
                self.profile_dialog.raise_()
                self.profile_dialog.activateWindow()

    def restore_profile_icon(self):
        """Restore profile icon to original state"""
        if self.profile_showing_text:
            self.profile_showing_text = False
            
            # Restore stylesheet
            self.profile_icon.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    border: 2px solid #bdc3c7;
                    border-radius: 17px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #d5d8dc;
                    border-color: #95a5a6;
                }
                QPushButton:pressed {
                    background-color: #bdc3c7;
                }
            """)
            
            # Update icon to show photo or initial
            self.update_profile_icon()

    def show_activity_dialog(self):
        """Show activity history dialog"""
        if self.activity_dialog is None:
            self.activity_dialog = ActivityDialog(self.api_client, self)

        self.activity_dialog.show()
        self.activity_dialog.raise_()
        self.activity_dialog.activateWindow()

    def handle_logout(self):
        """Handle logout from profile dialog - redirect to login page"""
        # Log activity
        if self.activity_dialog:
            self.activity_dialog.log_logout()

        # Disconnect dari API
        if self.is_connected:
            self.disconnect_from_api()

        # Close dialogs
        if self.profile_dialog:
            self.profile_dialog.close()
            self.profile_dialog = None  # FORCE DESTROY INSTANCE
        if self.activity_dialog:
            self.activity_dialog.close()
            self.activity_dialog = None  # FORCE DESTROY INSTANCE

        # Clear all component data
        self.clear_all_data()

        # Reset user data
        self.user_data = None
        self.api_client.user_data = None
        self.profile_image_path = None  # CRITICAL: Clear cached profile image path

        # Reset UI state
        self.user_label.setText("Guest")
        self.user_info_label.setText("Silakan login untuk mengakses sistem")

        # Add logout log
        self.add_log("User logout - mengarahkan ke halaman login...")

        # Hide main window content
        self.hide()

        # Show login dialog again
        self.show_login()

        # If login successful, show window again
        if self.user_data:
            self.show()
            self.add_log(f"Login kembali sebagai {self.user_data.get('nama_lengkap', 'Unknown')}")
            # Reconnect to API
            self.connect_to_api()
        else:
            # If login cancelled or failed, exit aplikasi
            self.add_log("Login dibatalkan - menutup aplikasi")
            self.close()

    def clear_all_data(self):
        """Clear semua data dari component saat logout"""
        # Clear jemaat data
        if hasattr(self, 'jemaat_component') and self.jemaat_component:
            self.jemaat_component.jemaat_data = []
            if hasattr(self.jemaat_component, 'populate_table'):
                self.jemaat_component.populate_table()

        # Clear keuangan data
        if hasattr(self, 'keuangan_component') and self.keuangan_component:
            self.keuangan_component.keuangan_data = []
            if hasattr(self.keuangan_component, 'populate_table'):
                self.keuangan_component.populate_table()

        # Clear program kerja WR data
        if hasattr(self, 'proker_component') and self.proker_component:
            self.proker_component.proker_list = []
            if hasattr(self.proker_component, 'populate_table'):
                self.proker_component.populate_table([])

        # Clear kegiatan data
        if hasattr(self, 'kegiatan_component') and self.kegiatan_component:
            self.kegiatan_component.kegiatan_data = []
            if hasattr(self.kegiatan_component, 'populate_table'):
                self.kegiatan_component.populate_table([])

        # Clear pengumuman data
        if hasattr(self, 'pengumuman_component') and self.pengumuman_component:
            self.pengumuman_component.pengumuman_data = []
            if hasattr(self.pengumuman_component, 'populate_table'):
                self.pengumuman_component.populate_table()

        # Clear dokumen data
        if hasattr(self, 'dokumen_component') and self.dokumen_component:
            self.dokumen_component.dokumen_data = []
            if hasattr(self.dokumen_component, 'populate_table'):
                self.dokumen_component.populate_table()

        # Clear log
        if hasattr(self, 'log_text'):
            self.log_text.clear()

    def closeEvent(self, event):
        if self.is_connected:
            reply = QMessageBox.question(self, 'Konfirmasi',
                                        "Masih terhubung ke API. Yakin ingin keluar?",
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.disconnect_from_api()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = ClientMainWindow()
    # Window akan ditampilkan setelah login berhasil
    # window.show() tidak dipanggil di sini
    
    sys.exit(app.exec_())