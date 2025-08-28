# Path: client/components/login_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api_client import ApiClient

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("Login - Gereja Katolik Client")
        self.setMinimumSize(350, 250)
        self.user_data = None
        
        # Inisialisasi API client
        self.api_client = ApiClient()
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title_label = QLabel("Login ke Sistem")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        layout.addWidget(QLabel(""))
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px;")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px;")
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(self.login_button)
        
        # Server URL input
        server_layout = QVBoxLayout()
        
        server_label = QLabel("Server URL (opsional):")
        server_label.setStyleSheet("color: #7f8c8d; font-size: 11px; margin-top: 10px;")
        server_layout.addWidget(server_label)
        
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("http://localhost:8000 atau kosongkan untuk auto-detect")
        self.server_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        server_layout.addWidget(self.server_input)
        
        layout.addLayout(server_layout)
        
        # Test connection button
        self.test_button = QPushButton("Test Koneksi API")
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        layout.addWidget(self.test_button)
        
        # API Status label
        self.api_status_label = QLabel("Status API: Belum ditest")
        self.api_status_label.setAlignment(Qt.AlignCenter)
        self.api_status_label.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-top: 5px;")
        layout.addWidget(self.api_status_label)
        
        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        self.test_button.clicked.connect(self.test_connection)

    def test_connection(self):
        """Test koneksi ke API server"""
        self.test_button.setEnabled(False)
        self.test_button.setText("Testing...")
        self.api_status_label.setText("Status API: Testing...")
        self.api_status_label.setStyleSheet("color: #f39c12; font-size: 12px; margin-top: 5px;")
        
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
                self.api_status_label.setText("Status API: ✓ Terhubung")
                self.api_status_label.setStyleSheet("color: #27ae60; font-size: 12px; margin-top: 5px; font-weight: bold;")
                QMessageBox.information(self, "Koneksi Berhasil", 
                    f"Berhasil terhubung ke API server!\nURL: {self.api_client.base_url}")
            else:
                self.api_status_label.setText("Status API: ✗ Tidak terhubung")
                self.api_status_label.setStyleSheet("color: #e74c3c; font-size: 12px; margin-top: 5px; font-weight: bold;")
                error_msg = result.get("data", "Unknown error")
                QMessageBox.warning(self, "Koneksi Gagal", 
                    f"Tidak dapat terhubung ke API server:\n{error_msg}\n\nURL: {self.api_client.base_url}")
                
        except Exception as e:
            self.api_status_label.setText("Status API: ✗ Error")
            self.api_status_label.setStyleSheet("color: #e74c3c; font-size: 12px; margin-top: 5px; font-weight: bold;")
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