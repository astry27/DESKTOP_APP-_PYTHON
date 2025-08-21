# Path: client/main_client_api.py

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTabWidget, QTextEdit, QPushButton,
                            QLabel, QLineEdit, QMessageBox, QStatusBar, QFrame,
                            QSplitter, QSystemTrayIcon, QMenu)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from api_client import ApiClient
from components.login_dialog import LoginDialog
from components.pengumuman_component import PengumumanComponent
from components.dokumen_component import DokumenComponent
from config import ClientConfig

class ClientMainWindow(QMainWindow):
    
    message_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client Gereja Katolik - API Mode")
        self.setMinimumSize(1000, 700)
        
        self.api_client = ApiClient()
        self.user_data = None
        self.is_connected = False
        self.config = ClientConfig.load_settings()
        # self.last_message_count = 0
        
        self.setup_ui()
        self.setup_timers()
        self.setup_system_tray()
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Belum terhubung ke API")
        
        self.show_login()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #2c3e50; color: white; padding: 10px;")
        header_layout = QHBoxLayout(header_frame)
        
        self.title_label = QLabel("Sistem Informasi Gereja Katolik - Client API")
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setStyleSheet("color: white;")
        
        self.user_label = QLabel("Belum Login")
        self.user_label.setStyleSheet("color: #ecf0f1;")
        
        self.connection_label = QLabel("Offline")
        self.connection_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("User:"))
        header_layout.addWidget(self.user_label)
        header_layout.addWidget(QLabel("|"))
        header_layout.addWidget(QLabel("Status:"))
        header_layout.addWidget(self.connection_label)
        
        main_layout.addWidget(header_frame)
        
        # Main content dengan splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Tab Widget untuk konten utama
        self.tab_widget = QTabWidget()
        
        # Tab Dashboard/Info
        self.dashboard_tab = self.create_dashboard_tab()
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
        
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
        comm_header = QLabel("Panel Komunikasi")
        comm_header.setFont(QFont("Arial", 12, QFont.Bold))
        comm_header.setStyleSheet("background-color: #34495e; color: white; padding: 8px; border-radius: 4px;")
        layout.addWidget(comm_header)
        
        # Log komunikasi
        log_label = QLabel("Log Sistem:")
        log_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(log_label)
        
        self.communication_log = QTextEdit()
        self.communication_log.setReadOnly(True)
        self.communication_log.setFont(QFont("Courier New", 9))
        self.communication_log.setMaximumHeight(200)
        layout.addWidget(self.communication_log)
        
        # Input pesan ke admin
        message_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ketik pesan untuk admin...")
        self.message_input.returnPressed.connect(self.send_message_to_admin)
        
        self.send_button = QPushButton("Kirim")
        self.send_button.clicked.connect(self.send_message_to_admin)
        self.send_button.setEnabled(False)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        message_layout.addWidget(self.message_input)
        message_layout.addWidget(self.send_button)
        
        layout.addLayout(message_layout)
        
        # Notifikasi broadcast
        self.broadcast_notification = QLabel("Siap menerima broadcast...")
        self.broadcast_notification.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(self.broadcast_notification)
        
        # Clear log button
        clear_layout = QHBoxLayout()
        clear_layout.addStretch()
        
        self.clear_log_button = QPushButton("Bersihkan Log")
        self.clear_log_button.clicked.connect(self.clear_communication_log)
        self.clear_log_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 4px 8px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        clear_layout.addWidget(self.clear_log_button)
        
        layout.addLayout(clear_layout)
        layout.addStretch()
        
        return comm_widget
    
    def create_control_buttons(self):
        """Buat tombol kontrol"""
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        
        self.connect_button = QPushButton("Hubungkan ke API")
        self.connect_button.clicked.connect(self.connect_to_api)
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        
        self.disconnect_button = QPushButton("Putuskan Koneksi")
        self.disconnect_button.clicked.connect(self.disconnect_from_api)
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
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
        
        control_layout.addWidget(self.connect_button)
        control_layout.addWidget(self.disconnect_button)
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
            self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
            
            # Context menu untuk tray
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Tampilkan")
            show_action.triggered.connect(self.show)
            
            quit_action = tray_menu.addAction("Keluar")
            quit_action.triggered.connect(self.close)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
    def show_login(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == login_dialog.Accepted:
            self.user_data = login_dialog.get_user_data()
            if self.user_data:
                self.user_label.setText(self.user_data.get('nama_lengkap', 'Unknown'))
                self.user_info_label.setText(f"""
                Nama: {self.user_data.get('nama_lengkap', 'Unknown')}
                Username: {self.user_data.get('username', 'Unknown')}
                Peran: {self.user_data.get('peran', 'Unknown')}
                """)
                self.add_log("Login berhasil sebagai " + self.user_data.get('nama_lengkap', 'Unknown'))
                self.connect_to_api()
            else:
                self.close()
        else:
            self.close()
    
    def connect_to_api(self):
        self.add_log("Mencoba terhubung ke API...")
        
        # Test koneksi API
        result = self.api_client.check_server_connection()
        if result["success"]:
            # Register client
            register_result = self.api_client.register_client()
            if register_result["success"]:
                self.is_connected = True
                self.connection_label.setText("Online")
                self.connection_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                
                self.api_status_label.setText("Terhubung ke API")
                self.api_status_label.setStyleSheet("color: #27ae60; font-size: 14px;")
                
                self.connect_button.setEnabled(False)
                self.disconnect_button.setEnabled(True)
                # self.send_button.setEnabled(True)
                
                self.statusBar.showMessage("Terhubung ke API shared hosting")
                print("Berhasil terhubung ke API dan terdaftar sebagai client")
                
                # Load semua data
                self.refresh_all_data()
                
                # Update API status info
                api_data = result["data"]
                if "api_enabled" in api_data:
                    status_text = "Aktif" if api_data["api_enabled"] else "Nonaktif"
                    self.api_version_label.setText(f"Status API: {status_text}")
                
                # Start timers
                self.heartbeat_timer.start()
                # self.broadcast_timer.start()
                
            else:
                QMessageBox.warning(self, "Error", f"Gagal registrasi client: {register_result['data']}")
                self.add_log(f"Gagal registrasi client: {register_result['data']}")
        else:
            QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {result['data']}")
            self.add_log(f"Gagal terhubung ke API: {result['data']}")
    
    def disconnect_from_api(self):
        if self.is_connected:
            # Disconnect dari API
            result = self.api_client.disconnect_client()
            self.add_log("Memutuskan koneksi dari API...")
        
        self.is_connected = False
        self.connection_label.setText("Offline")
        self.connection_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        self.api_status_label.setText("Terputus dari API")
        self.api_status_label.setStyleSheet("color: #e74c3c; font-size: 14px;")
        
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        # self.send_button.setEnabled(False)
        
        self.statusBar.showMessage("Terputus dari API")
        print("Koneksi API terputus")
        
        # Stop timers
        self.heartbeat_timer.stop()
        # self.broadcast_timer.stop()
    
    def send_heartbeat(self):
        """Kirim heartbeat ke server"""
        if self.is_connected:
            result = self.api_client.heartbeat()
            if not result["success"]:
                self.add_log("Heartbeat gagal - koneksi mungkin terputus")
    
    # def send_message_to_admin(self):
    #     """Kirim pesan ke admin"""
    #     if not self.is_connected:
    #         QMessageBox.warning(self, "Error", "Tidak terhubung ke API")
    #         return
        
    #     message = self.message_input.text().strip()
    #     if not message:
    #         return
        
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
        
    #     result = self.api_client.get_broadcast_messages(limit=20)
    #     if result["success"]:
    #         data = result["data"]
    #         if data.get("status") == "success":
    #             messages = data.get("data", [])
    #             current_count = len(messages)
                
    #             if current_count > self.last_message_count:
    #                 # Ada pesan baru
    #                 new_message_count = current_count - self.last_message_count
    #                 self.broadcast_notification.setText(f"Pesan broadcast baru: +{new_message_count}")
    #                 self.broadcast_notification.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
                    
    #                 # Tampilkan notifikasi sistem tray jika ada
    #                 if hasattr(self, 'tray_icon') and new_message_count > 0:
    #                     self.tray_icon.showMessage(
    #                         "Pesan Broadcast Baru",
    #                         f"Diterima {new_message_count} pesan broadcast dari admin",
    #                         QSystemTrayIcon.Information,
    #                         3000
    #                     )
                    
    #                 # Log pesan terbaru
    #                 if messages:
    #                     latest_message = messages[0]
    #                     pesan_content = latest_message.get('pesan', '')
    #                     if len(pesan_content) > 50:
    #                         pesan_content = pesan_content[:50] + "..."
    #                     self.add_log(f"[Broadcast Admin]: {pesan_content}")
                    
    #                 # Reset notification style setelah 5 detik
    #                 QTimer.singleShot(5000, self.reset_broadcast_notification)
                    
    #             self.last_message_count = current_count
    
    # def reset_broadcast_notification(self):
    #     """Reset style notifikasi broadcast"""
    #     self.broadcast_notification.setText("Siap menerima broadcast...")
    #     self.broadcast_notification.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
    
    def refresh_all_data(self):
        if not self.is_connected:
            return

        print("Memuat ulang semua data...")
        
        # Refresh pengumuman
        self.pengumuman_component.load_pengumuman()
        self.pengumuman_component.load_broadcast_messages()
        
        # Refresh dokumen
        if hasattr(self.dokumen_component, 'load_files'):
            self.dokumen_component.load_files()
        
        print("Data berhasil dimuat ulang")
    
    def periodic_update(self):
        if self.is_connected:
            # Refresh data secara berkala
            current_tab = self.tab_widget.currentIndex()
            
            if current_tab == 1:  # Tab Pengumuman
                self.pengumuman_component.auto_refresh_broadcast()
            elif current_tab == 2:  # Tab Dokumen
                pass  # Dokumen tidak perlu auto refresh
    
    def add_log(self, message):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.communication_log.append(log_entry)
        scrollbar = self.communication_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    # def clear_communication_log(self):
    #     self.communication_log.clear()
    #     self.add_log("Log komunikasi dibersihkan")
    
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
    window.show()
    
    sys.exit(app.exec_())