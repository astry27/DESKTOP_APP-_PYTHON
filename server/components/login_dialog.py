# Path: server/components/login_dialog.py

import hashlib
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class LoginDialog(QDialog):
    """Dialog untuk login admin"""
    
    login_successful = pyqtSignal(dict)  # Signal ketika login berhasil dengan data admin
    
    def __init__(self, database_manager, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("Login Administrator - Gereja Katolik")
        self.setMinimumSize(350, 250)
        self.database_manager = database_manager
        self.admin_data = None
        self.login_attempts = 0
        self.max_attempts = 3
        
        # Set window flags untuk tidak bisa ditutup dengan X
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("Login Administrator")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Sistem Manajemen Gereja Katolik")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        layout.addWidget(subtitle_label)
        
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
        
        self.exit_button = QPushButton("Keluar")
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(self.exit_button)
        
        # Info label untuk menampilkan pesan
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #e74c3c; font-size: 12px; margin-top: 10px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Set default credentials untuk testing
        self.username_input.setText("admin")
        self.password_input.setText("admin123")
        
        # Setup connections
        self.login_button.clicked.connect(self.handle_login)
        self.exit_button.clicked.connect(self.handle_exit)
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Username dan password tidak boleh kosong.")
            return
        
        if not self.database_manager:
            QMessageBox.critical(self, "Error", "Database Manager tidak tersedia.")
            return
            
        self.login_button.setEnabled(False)
        self.login_button.setText("Memverifikasi...")
        
        try:
            # Authenticate admin
            success, result = self.authenticate_admin(username, password)
            
            if success and result:
                self.admin_data = result
                self.show_success("Login berhasil!")
                
                # Update last login di database
                self.update_last_login(result['id_admin'])
                
                # Emit signal dan tutup dialog
                self.login_successful.emit(result)
                self.accept()
            else:
                self.login_attempts += 1
                remaining = self.max_attempts - self.login_attempts
                
                if remaining > 0:
                    error_msg = f"Username atau password salah. Sisa percobaan: {remaining}"
                    QMessageBox.critical(self, "Login Gagal", error_msg)
                    self.show_error(error_msg)
                    self.password_input.clear()
                    self.password_input.setFocus()
                else:
                    QMessageBox.critical(self, "Login Ditolak", 
                                       "Anda telah mencoba login sebanyak 3 kali dengan gagal.\n"
                                       "Aplikasi akan ditutup untuk keamanan.")
                    self.close()
                    exit()
        except Exception as e:
            error_msg = f"Error saat login: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            self.show_error(error_msg)
        finally:
            self.login_button.setEnabled(True)
            self.login_button.setText("Login")
    
    def authenticate_admin(self, username, password):
        """Autentikasi admin menggunakan database"""
        try:
            # Buat request login ke API
            login_data = {
                'username': username,
                'password': password
            }
            
            # Coba authenticate melalui API client
            result = self.database_manager.api_client.authenticate_admin(login_data)
            
            if result["success"]:
                api_response = result["data"]
                if api_response.get("status") == "success":
                    return True, api_response.get("admin")
                else:
                    return False, api_response.get("message", "Login gagal")
            else:
                return False, result["data"]
                
        except Exception as e:
            return False, f"Error autentikasi: {str(e)}"
    
    def update_last_login(self, admin_id):
        """Update waktu last login admin"""
        try:
            if self.database_manager:
                self.database_manager.api_client.update_admin_last_login(admin_id)
        except Exception as e:
            print(f"Error updating last login: {e}")
    
    def show_error(self, message):
        """Tampilkan pesan error"""
        self.info_label.setText(message)
        self.info_label.setStyleSheet("color: #e74c3c; font-size: 12px; margin-top: 10px;")
    
    def show_success(self, message):
        """Tampilkan pesan sukses"""
        self.info_label.setText(message)
        self.info_label.setStyleSheet("color: #27ae60; font-size: 12px; margin-top: 10px;")
    
    def handle_exit(self):
        """Keluar dari aplikasi"""
        reply = QMessageBox.question(self, 'Konfirmasi',
                                   "Yakin ingin keluar dari aplikasi?",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.close()
            exit()
            
    def get_admin_data(self):
        return self.admin_data