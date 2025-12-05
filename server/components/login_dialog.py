# Path: server/components/login_dialog.py

import hashlib
import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QCheckBox, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QSettings
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush

class LoginDialog(QDialog):
    """Dialog untuk login admin"""

    login_successful: pyqtSignal = pyqtSignal(dict)  # Signal ketika login berhasil dengan data admin  # type: ignore

    def __init__(self, database_manager, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("Login Administrator")
        self.setMinimumSize(1000, 550)
        self.setMaximumSize(1400, 750)
        self.resize(1200, 600)
        self.database_manager = database_manager
        self.admin_data = None
        self.login_attempts = 0
        self.max_attempts = 3

        # Set window flags untuk tidak bisa ditutup dengan X
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)  # type: ignore

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
        login_card.setMaximumHeight(400)

        # Layout untuk login card - vertical layout
        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(40, 25, 40, 25)
        card_layout.setSpacing(8)

        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: transparent; border: none;")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(3)
        header_layout.setContentsMargins(0, 0, 0, 8)

        title_label = QLabel("Sistem Manajemen Gereja Katolik")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; background-color: transparent; border: none;")
        header_layout.addWidget(title_label)

        subtitle_label = QLabel("Paroki Santa Maria Ratu Damai, Uluindano")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; background-color: transparent; border: none;")
        header_layout.addWidget(subtitle_label)

        card_layout.addWidget(header_frame)

        # Admin login title
        admin_title = QLabel("Administrator Login")
        admin_title.setFont(QFont("Arial", 12, QFont.Bold))
        admin_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        admin_title.setStyleSheet("color: #34495e; background-color: transparent; border: none; margin-bottom: 5px;")
        card_layout.addWidget(admin_title)

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

        # Checkbox Ingat Saya dengan checkmark yang terlihat jelas
        self.remember_checkbox = QCheckBox("  ☐  Ingat Saya")
        self.remember_checkbox.setChecked(False)

        # Connect state change untuk update text
        def update_checkbox_text(state):
            if state == Qt.CheckState.Checked:
                self.remember_checkbox.setText("  ☑  Ingat Saya")
            else:
                self.remember_checkbox.setText("  ☐  Ingat Saya")

        self.remember_checkbox.stateChanged.connect(update_checkbox_text)

        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #2c3e50;
                font-size: 14px;
                margin: 3px 0px;
                background-color: transparent;
                border: none;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 0px;
                height: 0px;
            }
        """)

        card_layout.addWidget(self.remember_checkbox)

        # Login button
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

        # Exit button
        self.exit_button = QPushButton("Keluar")
        self.exit_button.setMinimumHeight(38)
        self.exit_button.setCursor(Qt.PointingHandCursor)
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 9px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        card_layout.addWidget(self.exit_button)

        # Info label untuk menampilkan pesan
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("""
            color: #e74c3c;
            font-size: 11px;
            background-color: transparent;
            border: none;
            padding: 5px;
            margin-top: 3px;
        """)
        self.info_label.setWordWrap(True)
        card_layout.addWidget(self.info_label)

        # Add login card to main layout
        main_layout.addWidget(login_card)

        # Right spacer - equal untuk center card
        main_layout.addStretch(1)

        # Load saved credentials dari QSettings
        self.load_saved_credentials()

        # Setup connections
        self.login_button.clicked.connect(self.handle_login)
        self.exit_button.clicked.connect(self.handle_exit)
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def load_saved_credentials(self):
        """Load kredensial yang tersimpan dari QSettings"""
        settings = QSettings("GerejaKatolik", "ServerAdminPanel")
        remember = settings.value("remember_me", False, type=bool)

        if remember:
            username = settings.value("username", "", type=str)
            password = settings.value("password", "", type=str)

            if username and password:
                self.username_input.setText(username)
                self.password_input.setText(password)
                self.remember_checkbox.setChecked(True)

    def save_credentials(self):
        """Simpan kredensial ke QSettings jika checkbox dicentang"""
        settings = QSettings("GerejaKatolik", "ServerAdminPanel")

        if self.remember_checkbox.isChecked():
            # Simpan kredensial
            settings.setValue("remember_me", True)
            settings.setValue("username", self.username_input.text())
            settings.setValue("password", self.password_input.text())
        else:
            # Hapus kredensial tersimpan
            settings.setValue("remember_me", False)
            settings.remove("username")
            settings.remove("password")

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

                # Simpan kredensial jika checkbox dicentang
                self.save_credentials()

                # Update last login di database
                self.update_last_login(result['id_admin'])  # type: ignore

                # Emit signal dan tutup dialog
                self.login_successful.emit(result)  # type: ignore
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
                # API failed - return offline login mode
                self.database_manager.connection = False
                self.show_error("API tidak tersedia - mode offline")
                # Allow offline login with default credentials
                if username == "admin" and password == "admin123":
                    return True, {
                        'id_admin': 1,
                        'username': 'offline_admin',
                        'nama_lengkap': 'Administrator (Offline Mode)',
                        'peran': 'administrator'
                    }
                return False, "Offline mode - hanya admin/admin123 yang berlaku"

        except Exception as e:
            # Connection failed - try offline mode
            self.database_manager.connection = False
            self.show_error("Koneksi API gagal - mode offline")
            # Allow offline login with default credentials
            if username == "admin" and password == "admin123":
                return True, {
                    'id_admin': 1,
                    'username': 'offline_admin',
                    'nama_lengkap': 'Administrator (Offline Mode)',
                    'peran': 'administrator'
                }
            return False, f"Offline mode - hanya admin/admin123 yang berlaku"
    
    def update_last_login(self, admin_id):
        """Update waktu last login admin"""
        try:
            if self.database_manager:
                self.database_manager.api_client.update_admin_last_login(admin_id)
        except Exception as e:
            print(f"Error updating last login: {e}")
    
    def show_error(self, message):
        """Tampilkan pesan error"""
        self.info_label.setText(f"✗ {message}")
        self.info_label.setStyleSheet("""
            color: #e74c3c;
            font-size: 12px;
            background-color: transparent;
            border: none;
            padding: 8px;
            margin-top: 5px;
            font-weight: 600;
        """)

    def show_success(self, message):
        """Tampilkan pesan sukses"""
        self.info_label.setText(f"✓ {message}")
        self.info_label.setStyleSheet("""
            color: #27ae60;
            font-size: 12px;
            background-color: transparent;
            border: none;
            padding: 8px;
            margin-top: 5px;
            font-weight: 600;
        """)
    
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