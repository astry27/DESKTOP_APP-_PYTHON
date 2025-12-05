# Path: client/components/login_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api_client import ApiClient

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("Login - Client")
        self.setMinimumSize(1000, 550)
        self.setMaximumSize(1400, 750)
        self.resize(1200, 600)
        self.user_data = None

        # Inisialisasi API client
        self.api_client = ApiClient()

        self.setup_ui()

    def setup_ui(self):
        # Set background image
        background_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'SMRD.jpg')
        if os.path.exists(background_path):
            palette = QPalette()
            background = QPixmap(background_path)
            palette.setBrush(QPalette.Window, QBrush(background.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
            self.setPalette(palette)
            self.setAutoFillBackground(True)

        # Main layout dengan horizontal arrangement
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left and right spacers - equal untuk center card (landscape layout)
        main_layout.addStretch(1)

        # Login card container dengan semi-transparent background - landscape style
        login_card = QFrame()
        login_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 15px;
                padding: 0px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        # Landscape: lebih lebar, kurang tinggi
        login_card.setMaximumWidth(550)
        login_card.setMinimumWidth(500)
        login_card.setMaximumHeight(500)

        # Layout untuk login card - vertical layout
        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(40, 25, 40, 25)
        card_layout.setSpacing(8)

        # Header section with church name
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: transparent; border: none;")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(3)
        header_layout.setContentsMargins(0, 0, 0, 8)

        title_label = QLabel("Sistem Manajemen Gereja Katolik")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; background-color: transparent; border: none;")
        header_layout.addWidget(title_label)

        subtitle_label = QLabel("Paroki Santa Maria Ratu Damai, Uluindano")
        subtitle_label.setFont(QFont("Arial", 11))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; background-color: transparent; border: none;")
        header_layout.addWidget(subtitle_label)

        card_layout.addWidget(header_frame)

        # Login form title
        form_title = QLabel("Login User")
        form_title.setFont(QFont("Arial", 12, QFont.Bold))
        form_title.setAlignment(Qt.AlignCenter)
        form_title.setStyleSheet("color: #34495e; background-color: transparent; border: none; margin-bottom: 5px;")
        card_layout.addWidget(form_title)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(38)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 9px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        card_layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(38)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 9px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        card_layout.addWidget(self.password_input)

        # Login button dengan styling modern
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(40)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                padding: 10px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #21618c);
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        card_layout.addWidget(self.login_button)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #e0e0e0; max-height: 1px; margin: 8px 0px;")
        card_layout.addWidget(separator)

        # Server URL section dengan collapsible style
        server_label = QLabel("Server URL (opsional):")
        server_label.setStyleSheet("color: #7f8c8d; font-size: 11px; background-color: transparent; border: none;")
        card_layout.addWidget(server_label)

        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("http://localhost:8000 atau kosongkan untuk auto-detect")
        self.server_input.setMinimumHeight(35)
        self.server_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #f8f9fa;
                font-size: 11px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: white;
            }
        """)
        card_layout.addWidget(self.server_input)

        # Test connection button dengan styling minimal
        self.test_button = QPushButton("Test Koneksi API")
        self.test_button.setMinimumHeight(35)
        self.test_button.setCursor(Qt.PointingHandCursor)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
        """)
        card_layout.addWidget(self.test_button)

        # API Status label dengan icon-like indicator
        self.api_status_label = QLabel("● Status API: Belum ditest")
        self.api_status_label.setAlignment(Qt.AlignCenter)
        self.api_status_label.setStyleSheet("""
            color: #95a5a6;
            font-size: 11px;
            background-color: transparent;
            border: none;
            padding: 5px;
        """)
        card_layout.addWidget(self.api_status_label)

        # Add login card to main layout
        main_layout.addWidget(login_card)

        # Right spacer - equal untuk center card
        main_layout.addStretch(1)

        # Connect signals
        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        self.test_button.clicked.connect(self.test_connection)

    def test_connection(self):
        """Test koneksi ke API server"""
        self.test_button.setEnabled(False)
        self.test_button.setText("Testing...")
        self.api_status_label.setText("● Status API: Testing...")
        self.api_status_label.setStyleSheet("color: #f39c12; font-size: 11px; background-color: transparent; border: none; padding: 5px;")

        # Check if user provided custom URL
        custom_url = self.server_input.text().strip()
        if custom_url:
            print(f"Using custom server URL: {custom_url}")
            self.api_client.base_url = custom_url
        else:
            print("Re-detecting server...")
            self.api_client._detect_best_server()

        try:
            result = self.api_client.check_server_connection()

            if result.get("success"):
                self.api_status_label.setText("✓ Status API: Terhubung")
                self.api_status_label.setStyleSheet("color: #27ae60; font-size: 11px; background-color: transparent; border: none; padding: 5px; font-weight: bold;")
                QMessageBox.information(self, "Koneksi Berhasil",
                    f"Berhasil terhubung ke API server!\nURL: {self.api_client.base_url}")
            else:
                self.api_status_label.setText("✗ Status API: Tidak terhubung")
                self.api_status_label.setStyleSheet("color: #e74c3c; font-size: 11px; background-color: transparent; border: none; padding: 5px; font-weight: bold;")
                error_msg = result.get("data", "Unknown error")
                QMessageBox.warning(self, "Koneksi Gagal",
                    f"Tidak dapat terhubung ke API server:\n{error_msg}\n\nURL: {self.api_client.base_url}")

        except Exception as e:
            self.api_status_label.setText("✗ Status API: Error")
            self.api_status_label.setStyleSheet("color: #e74c3c; font-size: 11px; background-color: transparent; border: none; padding: 5px; font-weight: bold;")
            QMessageBox.critical(self, "Error", f"Error saat test koneksi:\n{str(e)}")

        finally:
            self.test_button.setEnabled(True)
            self.test_button.setText("Test Koneksi API")
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Username dan password tidak boleh kosong.")
            return
        
        # Check if user provided custom URL before login
        custom_url = self.server_input.text().strip()
        if custom_url and custom_url != self.api_client.base_url:
            print(f"Switching to custom server URL: {custom_url}")
            self.api_client.base_url = custom_url
        
        # Test koneksi terlebih dahulu
        print(f"Testing connection to: {self.api_client.base_url}")
        connection_test = self.api_client.check_server_connection()
        if not connection_test.get("success"):
            QMessageBox.critical(self, "Koneksi Gagal", 
                f"Tidak dapat terhubung ke server API:\n{connection_test.get('data', 'Unknown error')}\n\nURL: {self.api_client.base_url}\n\nSilahkan test koneksi terlebih dahulu.")
            return
            
        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")
        
        print(f"Attempting login for user: {username}")
        result = self.api_client.login(username, password)
        print(f"Login result: {result}")
        
        self.login_button.setEnabled(True)
        self.login_button.setText("Login")

        if result.get("success"):
            response_data = result.get("data", {})
            print(f"Response data: {response_data}")
            
            if response_data.get("status") == "success":
                user_data = response_data.get("user")
                if user_data:
                    self.user_data = user_data
                    user_name = user_data.get('nama_lengkap', 'Unknown')
                    user_role = user_data.get('peran', 'Unknown')
                    print(f"Login successful for: {user_name} ({user_role})")
                    QMessageBox.information(self, "Login Berhasil", f"Selamat datang, {user_name}!\nPeran: {user_role}")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Login Gagal", "Data user tidak ditemukan dalam response")
            else:
                error_msg = response_data.get("message", "Login gagal")
                QMessageBox.critical(self, "Login Gagal", f"Server response: {error_msg}")
        else:
            error_msg = result.get("data", "Terjadi kesalahan koneksi")
            QMessageBox.critical(self, "Login Gagal", f"Koneksi atau autentikasi gagal:\n{error_msg}")
            
    def get_user_data(self):
        return self.user_data