# Path: server/components/sidebar.py

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap

class SidebarButton(QPushButton):
    """Custom button untuk sidebar"""
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(50)
        
        # Set style
        self.setStyleSheet("""
            QPushButton {
                border: none;
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
                background-color: #2c3e50;
                color: #ecf0f1;
                border-left: 5px solid transparent;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #34495e;
                border-left: 5px solid #3498db;
                font-weight: bold;
            }
        """)
        
        # Set icon dari file path
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(20, 20))

class SidebarWidget(QWidget):
    """Widget untuk sidebar navigasi"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.db_manager = None
        
        # Set style untuk sidebar utama
        self.setStyleSheet("background-color: #2c3e50;")
        
        # Layout utama
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header sidebar
        header = self.create_header()
        layout.addWidget(header)
        
        # Container untuk menu navigasi
        menu_container = QWidget()
        menu_layout = QVBoxLayout(menu_container)
        menu_layout.setContentsMargins(0, 10, 0, 10)
        menu_layout.setSpacing(0)
        
        # Path ke ikon-ikon
        assets_path = "server/assets/"
        
        # Buat menu buttons dengan icon
        self.menu_dashboard = SidebarButton("Dashboard", os.path.join(assets_path, "dashboard_icon.png"))
        self.menu_jemaat = SidebarButton("Database Jemaat", os.path.join(assets_path, "jemaat_icon.png"))
        self.menu_jadwal = SidebarButton("Jadwal Kegiatan", os.path.join(assets_path, "jadwal_icon.png"))
        self.menu_keuangan = SidebarButton("Manajemen Keuangan", os.path.join(assets_path, "keuangan_icon.png"))
        self.menu_pengumuman = SidebarButton("Pengumuman", os.path.join(assets_path, "pengumuman_icon.png"))
        self.menu_riwayat = SidebarButton("Riwayat", os.path.join(assets_path, "riwayat_icon.png"))
        self.menu_dokumen = SidebarButton("Dokumen", os.path.join(assets_path, "dokumen_icon.png"))
        self.menu_pengaturan = SidebarButton("Pengaturan Sistem", os.path.join(assets_path, "pengaturan_icon.png"))
        
        # Tambahkan menu ke container
        menu_layout.addWidget(self.menu_dashboard)
        menu_layout.addWidget(self.menu_jemaat)
        menu_layout.addWidget(self.menu_jadwal)
        menu_layout.addWidget(self.menu_keuangan)
        menu_layout.addWidget(self.menu_pengumuman)
        menu_layout.addWidget(self.menu_riwayat)
        menu_layout.addWidget(self.menu_dokumen)
        menu_layout.addWidget(self.menu_pengaturan)
        
        # Tambahkan menu container ke layout utama
        layout.addWidget(menu_container)
        
        # Spacer elastis untuk mendorong status ke bawah
        layout.addStretch(1)
        
        # Status API - selalu di bawah
        status_container = self.create_status_container()
        layout.addWidget(status_container)
        
        # Timer untuk update status API secara berkala
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_api_status)
        self.status_timer.start(10000)  # Update setiap 10 detik
        
    def set_database_manager(self, db_manager):
        """Set database manager untuk cek status API"""
        self.db_manager = db_manager
        self.update_api_status()
        
    def create_header(self):
        """Buat header sidebar dengan logo dan judul"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #2c3e50; border-bottom: 1px solid #34495e;")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 15, 0)
        header_layout.setSpacing(10)

        # Logo di sebelah kiri
        logo_label = QLabel()
        logo_path = "server/assets/logo_gereja.png"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Jika logo tidak ada, buat placeholder
            logo_label.setText("LOGO")
            logo_label.setStyleSheet("color: white; font-weight: bold; background-color: #34495e; border-radius: 25px; text-align: center;")
            
        logo_label.setFixedSize(50, 50)
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)

        # Layout vertikal untuk judul dan subtitle
        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        title_layout.setAlignment(Qt.AlignVCenter)

        title = QLabel("Gereja Katolik")
        title.setStyleSheet("color: #ecf0f1; font-size: 15px; font-weight: bold;")
        
        subtitle = QLabel("Admin Panel (API Mode)")
        subtitle.setStyleSheet("color: #bdc3c7; font-size: 11px;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        return header
    
    def create_status_container(self):
        """Buat container untuk status API"""
        status_container = QWidget()
        status_container.setFixedHeight(80)
        status_container.setStyleSheet("background-color: #1a252f; border-top: 1px solid #34495e;")
        
        status_layout = QVBoxLayout(status_container)
        status_layout.setContentsMargins(15, 8, 15, 8)
        status_layout.setAlignment(Qt.AlignCenter)
        
        # Status API dengan ikon
        self.api_status = QLabel("🔴 API: Mengecek...")
        self.api_status.setStyleSheet("""
            color: #e74c3c; 
            font-size: 11px;
            font-weight: bold;
            padding: 3px;
            background-color: rgba(231, 76, 60, 0.1);
            border-radius: 3px;
        """)
        self.api_status.setAlignment(Qt.AlignCenter)
        
        # Status koneksi
        self.connection_status = QLabel("🌐 Koneksi: Tidak diketahui")
        self.connection_status.setStyleSheet("""
            color: #f39c12; 
            font-size: 10px;
            padding: 2px;
            background-color: rgba(243, 156, 18, 0.1);
            border-radius: 3px;
        """)
        self.connection_status.setAlignment(Qt.AlignCenter)
        
        status_layout.addWidget(self.api_status)
        status_layout.addWidget(self.connection_status)
        
        return status_container
    
    def update_api_status(self):
        """Update status API dari database manager"""
        if not self.db_manager:
            self.set_api_offline()
            return
        
        try:
            # Cek status API
            success, status_data = self.db_manager.get_api_service_status()
            
            if success and status_data.get('api_enabled', False):
                self.set_api_active()
                
                # Cek jumlah client yang terhubung
                client_success, clients = self.db_manager.get_active_sessions()
                if client_success:
                    if isinstance(clients, dict) and 'data' in clients:
                        client_count = len(clients['data'])
                    elif isinstance(clients, list):
                        client_count = len(clients)
                    else:
                        client_count = 0
                    
                    self.connection_status.setText(f"🌐 Client Aktif: {client_count}")
                    self.connection_status.setStyleSheet("""
                        color: #27ae60; 
                        font-size: 10px;
                        padding: 2px;
                        background-color: rgba(39, 174, 96, 0.1);
                        border-radius: 3px;
                    """)
                else:
                    self.connection_status.setText("🌐 Koneksi: Error")
                    self.connection_status.setStyleSheet("""
                        color: #e74c3c; 
                        font-size: 10px;
                        padding: 2px;
                        background-color: rgba(231, 76, 60, 0.1);
                        border-radius: 3px;
                    """)
            else:
                self.set_api_offline()
        except Exception as e:
            self.set_api_error()
    
    def set_api_active(self):
        """Set status API aktif"""
        self.api_status.setText("🟢 API: Aktif")
        self.api_status.setStyleSheet("""
            color: #2ecc71; 
            font-size: 11px;
            font-weight: bold;
            padding: 3px;
            background-color: rgba(46, 204, 113, 0.1);
            border-radius: 3px;
        """)
    
    def set_api_offline(self):
        """Set status API non-aktif"""
        self.api_status.setText("🔴 API: Non-aktif")
        self.api_status.setStyleSheet("""
            color: #e74c3c; 
            font-size: 11px;
            font-weight: bold;
            padding: 3px;
            background-color: rgba(231, 76, 60, 0.1);
            border-radius: 3px;
        """)
        
        self.connection_status.setText("🌐 Tidak ada koneksi")
        self.connection_status.setStyleSheet("""
            color: #7f8c8d; 
            font-size: 10px;
            padding: 2px;
            background-color: rgba(127, 140, 141, 0.1);
            border-radius: 3px;
        """)
    
    def set_api_error(self):
        """Set status API error"""
        self.api_status.setText("⚠️ API: Error")
        self.api_status.setStyleSheet("""
            color: #f39c12; 
            font-size: 11px;
            font-weight: bold;
            padding: 3px;
            background-color: rgba(243, 156, 18, 0.1);
            border-radius: 3px;
        """)
        
        self.connection_status.setText("🌐 Koneksi bermasalah")
        self.connection_status.setStyleSheet("""
            color: #f39c12; 
            font-size: 10px;
            padding: 2px;
            background-color: rgba(243, 156, 18, 0.1);
            border-radius: 3px;
        """)
    
    def reset_menu_selection(self):
        """Reset semua pilihan menu"""
        self.menu_dashboard.setChecked(False)
        self.menu_jemaat.setChecked(False)
        self.menu_jadwal.setChecked(False)
        self.menu_keuangan.setChecked(False)
        self.menu_pengumuman.setChecked(False)
        self.menu_riwayat.setChecked(False)
        self.menu_dokumen.setChecked(False)
        self.menu_pengaturan.setChecked(False)