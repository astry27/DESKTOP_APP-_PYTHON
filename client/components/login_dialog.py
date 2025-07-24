# Path: client/components/login_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("Login - API Mode")
        self.setMinimumSize(350, 200)
        self.user_data = None
        self.api_client = None
        
        if parent and hasattr(parent, 'api_client'):
            self.api_client = parent.api_client
        
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
        
        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Username dan password tidak boleh kosong.")
            return
        
        if not self.api_client:
            QMessageBox.critical(self, "Error", "API Client tidak tersedia.")
            return
            
        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")
        
        result = self.api_client.login(username, password)
        
        self.login_button.setEnabled(True)
        self.login_button.setText("Login")

        if result.get("success"):
            response_data = result.get("data", {})
            if response_data.get("status") == "success":
                self.user_data = response_data.get("user")
                QMessageBox.information(self, "Login Berhasil", "Login berhasil!")
                self.accept()
            else:
                QMessageBox.critical(self, "Login Gagal", response_data.get("message", "Login gagal"))
        else:
            QMessageBox.critical(self, "Login Gagal", result.get("data", "Terjadi kesalahan koneksi"))
            
    def get_user_data(self):
        return self.user_data