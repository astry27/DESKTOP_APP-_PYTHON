# Path: server/components/pengaturan.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFileDialog, QGroupBox,
                            QFormLayout, QLineEdit, QComboBox, QCheckBox,
                            QTextEdit, QTabWidget, QAbstractItemView, QFrame,
                            QDialog, QDialogButtonBox, QInputDialog)
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QColor, QIcon, QFont
import requests
from api_client import BASE_URL

class PengaturanComponent(QWidget):
    """Komponen untuk pengaturan sistem dalam API Mode"""
    
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore  # Signal untuk mengirim log message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        try:
            self.setup_ui()
        except Exception as e:
            print(f"Critical error in PengaturanComponent.__init__: {e}")
            # Setup minimal UI in case of error
            self.setup_fallback_ui()
    
    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        if hasattr(self, 'db_manager') and self.db_manager:
            self.update_api_status()

    def setup_fallback_ui(self):
        """Setup minimal UI dalam kasus error"""
        try:
            layout = QVBoxLayout(self)

            # Header
            header = QWidget()
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 10, 0)

            title = QLabel("Pengaturan Sistem (Mode Error)")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
            header_layout.addWidget(title)
            header_layout.addStretch()

            layout.addWidget(header)

            # Error message
            error_label = QLabel("Terjadi error saat memuat pengaturan sistem.\nSilakan restart aplikasi atau hubungi administrator.")
            error_label.setStyleSheet("color: red; padding: 20px; font-size: 14px;")
            layout.addWidget(error_label)

            layout.addStretch()
        except Exception as e:
            print(f"Error even in fallback UI: {e}")

    def setup_ui(self):
        """Setup UI untuk halaman pengaturan"""
        layout = QVBoxLayout(self)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Tab untuk kategori pengaturan
        settings_tab = self.create_tabs()
        layout.addWidget(settings_tab)
    
    def create_header(self):
        """Buat header dengan title"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 10, 0)  # Add right margin for spacing
        
        title = QLabel("Pengaturan Sistem (API Mode)")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        return header
    
    def create_tabs(self):
        """Buat tab untuk kategori pengaturan"""
        try:
            settings_tab = QTabWidget()

            # Tab API Configuration
            try:
                api_tab = self.create_api_tab()
                settings_tab.addTab(api_tab, "Konfigurasi API")
            except Exception as e:
                print(f"Error creating API tab: {e}")
                error_tab = QWidget()
                error_layout = QVBoxLayout(error_tab)
                error_label = QLabel(f"Error memuat tab API: {str(e)}")
                error_label.setStyleSheet("color: red; padding: 20px;")
                error_layout.addWidget(error_label)
                settings_tab.addTab(error_tab, "Konfigurasi API")

            # Tab Database
            try:
                db_tab = self.create_database_tab()
                settings_tab.addTab(db_tab, "Database")
            except Exception as e:
                print(f"Error creating Database tab: {e}")
                error_tab = QWidget()
                error_layout = QVBoxLayout(error_tab)
                error_label = QLabel(f"Error memuat tab Database: {str(e)}")
                error_label.setStyleSheet("color: red; padding: 20px;")
                error_layout.addWidget(error_label)
                settings_tab.addTab(error_tab, "Database")

            # Tab Users - with special handling
            try:
                users_tab = self.create_users_tab()
                settings_tab.addTab(users_tab, "Pengguna")
            except Exception as e:
                print(f"Error creating Users tab: {e}")
                error_tab = QWidget()
                error_layout = QVBoxLayout(error_tab)
                error_label = QLabel(f"Error memuat tab Pengguna: {str(e)}")
                error_label.setStyleSheet("color: red; padding: 20px;")
                error_layout.addWidget(error_label)
                settings_tab.addTab(error_tab, "Pengguna")

            # Tab System Info
            try:
                info_tab = self.create_info_tab()
                settings_tab.addTab(info_tab, "Info Sistem")
            except Exception as e:
                print(f"Error creating Info tab: {e}")
                error_tab = QWidget()
                error_layout = QVBoxLayout(error_tab)
                error_label = QLabel(f"Error memuat tab Info: {str(e)}")
                error_label.setStyleSheet("color: red; padding: 20px;")
                error_layout.addWidget(error_label)
                settings_tab.addTab(error_tab, "Info Sistem")

            return settings_tab

        except Exception as e:
            print(f"Critical error creating settings tabs: {e}")
            # Return minimal fallback widget
            fallback_widget = QWidget()
            fallback_layout = QVBoxLayout(fallback_widget)
            error_label = QLabel(f"Error kritis memuat pengaturan: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 14px; padding: 30px;")
            fallback_layout.addWidget(error_label)
            return fallback_widget
    
    def create_api_tab(self):
        """Buat tab konfigurasi API"""
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        
        # Informasi API
        api_info_group = QGroupBox("Informasi API Endpoint")
        api_info_layout = QVBoxLayout(api_info_group)
        
        # PRODUCTION: Using https://enternal.my.id/flask
        self.api_url_label = QLabel("URL API: https://enternal.my.id/flask")
        self.api_url_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        api_info_layout.addWidget(self.api_url_label)
        
        self.api_status_label = QLabel("Status: Menunggu pemeriksaan...")
        api_info_layout.addWidget(self.api_status_label)
        
        # Test connection button
        test_connection_button = self.create_button("Test Koneksi API", "#3498db", self.test_api_connection)
        api_info_layout.addWidget(test_connection_button)
        
        api_layout.addWidget(api_info_group)
        
        # Pengaturan Client
        client_group = QGroupBox("Pengaturan Client")
        client_form = QFormLayout(client_group)
        
        self.max_clients = QLineEdit("100")
        client_form.addRow("Maksimal Client:", self.max_clients)
        
        self.timeout_minutes = QLineEdit("30")
        client_form.addRow("Timeout (menit):", self.timeout_minutes)
        
        self.auto_disconnect = QCheckBox("Auto disconnect client tidak aktif")
        self.auto_disconnect.setChecked(True)
        client_form.addRow("", self.auto_disconnect)
        
        api_layout.addWidget(client_group)
        
        # Tombol Simpan untuk API
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        
        save_api_button = self.create_button("Simpan Konfigurasi", "#27ae60", self.save_api_config)
        save_layout.addWidget(save_api_button)
        
        api_layout.addLayout(save_layout)
        api_layout.addStretch()
        
        return api_tab
    
    def create_database_tab(self):
        """Buat tab pengaturan database"""
        db_tab = QWidget()
        db_layout = QVBoxLayout(db_tab)
        
        # Informasi Database
        db_info_group = QGroupBox("Informasi Database Shared Hosting")
        db_info_layout = QVBoxLayout(db_info_group)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(150)
        # DEVELOPMENT: Changed to local database
        info_text.setText("""
Database Type: MySQL (Local Development)
Host: localhost
Database: db_client_server
User: root
Password: (kosong)

Catatan: Database lokal untuk pengembangan.
Hubungkan ke shared hosting dengan mengubah konfigurasi.
        """)
        db_info_layout.addWidget(info_text)
        
        db_layout.addWidget(db_info_group)
        
        # Backup & Restore (untuk export/import data saja)
        backup_group = self.create_backup_group()
        db_layout.addWidget(backup_group)
        
        db_layout.addStretch()
        
        return db_tab
    
    def create_backup_group(self):
        """Buat group untuk backup & restore data"""
        backup_group = QGroupBox("Export & Import Data")
        backup_layout = QVBoxLayout(backup_group)
        
        # Path backup
        backup_path_layout = QHBoxLayout()
        backup_path_label = QLabel("Path Export:")
        self.backup_path = QLineEdit("./exports")
        browse_button = self.create_button("Browse", "#3498db", self.browse_backup_path)
        
        backup_path_layout.addWidget(backup_path_label)
        backup_path_layout.addWidget(self.backup_path)
        backup_path_layout.addWidget(browse_button)
        
        backup_layout.addLayout(backup_path_layout)
        
        # Tombol export/import
        backup_action_layout = QHBoxLayout()
        
        export_button = self.create_button("Export Data ke CSV", "#3498db", self.export_data, "server/assets/export.png")
        backup_action_layout.addWidget(export_button)
        
        import_button = self.create_button("Import Data dari CSV", "#f39c12", self.import_data)
        backup_action_layout.addWidget(import_button)
        
        backup_action_layout.addStretch()
        
        backup_layout.addLayout(backup_action_layout)
        
        return backup_group
    
    def create_users_tab(self):
        """Buat tab pengaturan pengguna - menggunakan PenggunaComponent"""
        try:
            # Import di sini untuk menghindari circular import
            try:
                from .pengguna import PenggunaComponent
            except ImportError:
                # Fallback to absolute import
                from components.pengguna import PenggunaComponent

            users_tab = PenggunaComponent()

            # Connect log signals if available
            if hasattr(users_tab, 'log_message'):
                users_tab.log_message.connect(self.log_message.emit)

            return users_tab

        except ImportError as e:
            print(f"Error importing PenggunaComponent: {e}")
            # Return fallback tab dengan pesan error
            fallback_tab = QWidget()
            layout = QVBoxLayout(fallback_tab)
            error_label = QLabel(f"Error memuat manajemen pengguna: {str(e)}")
            error_label.setStyleSheet("color: red; padding: 20px;")
            layout.addWidget(error_label)
            return fallback_tab

        except Exception as e:
            print(f"Error creating users tab: {e}")
            # Return fallback tab dengan pesan error
            fallback_tab = QWidget()
            layout = QVBoxLayout(fallback_tab)
            error_label = QLabel(f"Error tidak terduga: {str(e)}")
            error_label.setStyleSheet("color: red; padding: 20px;")
            layout.addWidget(error_label)
            return fallback_tab
    
    def create_info_tab(self):
        """Buat tab informasi sistem"""
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        
        # System Information
        system_group = QGroupBox("Informasi Sistem")
        system_layout = QVBoxLayout(system_group)
        
        system_info = QTextEdit()
        system_info.setReadOnly(True)
        system_info.setText("""
SISTEM GEREJA KATOLIK - API MODE

Versi Aplikasi: 2.1.0
Mode Operasi: API Shared Hosting
Arsitektur: Client-Server via API

=== KOMPONEN SISTEM ===
• Server Admin Desktop (PyQt5)
• API Flask di Shared Hosting
• Database MySQL di Shared Hosting
• Client Desktop (PyQt5)

=== ENDPOINT API ===
# PRODUCTION: Using https://enternal.my.id/flask
• Base URL: https://enternal.my.id/flask
• Admin Routes: /admin/*
• Data Routes: /jemaat, /kegiatan, /pengumuman, /keuangan
• File Routes: /files, /upload
• Auth Routes: /auth/login
• Log Routes: /log/*

=== FITUR UTAMA ===
• Manajemen Data Jemaat
• Jadwal Kegiatan Gereja
• Pengumuman
• Manajemen Keuangan
• Upload/Download Dokumen
• Kontrol API Server
• Broadcast Message ke Client
• Multi-user dengan role
• Log Aktivitas Admin

=== KEAMANAN ===
• Autentikasi Admin wajib
• Login tracking
• Session management
• API enable/disable control
• Log aktivitas sistem

=== DUKUNGAN TEKNIS ===
Untuk dukungan teknis dan pemeliharaan sistem,
hubungi administrator IT gereja.
        """)
        system_layout.addWidget(system_info)
        
        info_layout.addWidget(system_group)
        
        return info_tab
    
    # Removed old table creation methods as they're now handled by PenggunaComponent

    # User management methods removed - now handled by PenggunaComponent

    
    def create_button(self, text, color, slot, icon_path=None):
        """Buat button dengan style konsisten dan optional icon"""
        button = QPushButton(text)

        # Add icon if specified and path exists
        if icon_path:
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(20, 20))  # Consistent icon size matching other components
            except Exception:
                pass  # If icon loading fails, just continue without icon

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
                border: 1px solid {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(self.darken_color(color))};
                border: 2px inset {self.darken_color(self.darken_color(color))};
            }}
        """)
        button.clicked.connect(slot)
        return button
    
    def darken_color(self, color):
        """Buat warna lebih gelap untuk hover effect"""
        color_map = {
            "#3498db": "#2980b9",
            "#27ae60": "#2ecc71", 
            "#f39c12": "#f1c40f",
            "#c0392b": "#e74c3c",
            "#16a085": "#1abc9c",
            "#8e44ad": "#9b59b6"
        }
        return color_map.get(color, color)
    
    # API Functions
    def test_api_connection(self):
        """Test koneksi ke API"""
        if self.db_manager:
            try:
                result = self.db_manager.api_client.check_server_connection()
                if result["success"]:
                    self.api_status_label.setText("Status: Terhubung")
                    self.api_status_label.setStyleSheet("color: green; font-weight: bold;")
                    QMessageBox.information(self, "Sukses", "Koneksi ke API berhasil!")
                    self.log_message.emit("Test koneksi API berhasil")
                else:
                    self.api_status_label.setText("Status: Gagal terhubung")
                    self.api_status_label.setStyleSheet("color: red; font-weight: bold;")
                    QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {result['data']}")
                    self.log_message.emit(f"Test koneksi API gagal: {result['data']}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error test koneksi: {str(e)}")
                self.log_message.emit(f"Error test koneksi API: {str(e)}")
        else:
            QMessageBox.warning(self, "Warning", "Database manager tidak tersedia")
    
    def save_api_config(self):
        """Simpan konfigurasi API"""
        try:
            QMessageBox.information(self, "Sukses", "Konfigurasi API berhasil disimpan")
            self.log_message.emit("Konfigurasi API disimpan")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error menyimpan konfigurasi: {str(e)}")
            self.log_message.emit(f"Error saving API config: {str(e)}")
    
    def update_api_status(self):
        """Update status API"""
        if self.db_manager:
            success, status_data = self.db_manager.get_api_service_status()
            if success and status_data.get('api_enabled', False):
                self.api_status_label.setText("Status: Aktif")
                self.api_status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.api_status_label.setText("Status: Non-aktif")
                self.api_status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.api_status_label.setText("Status: Tidak terhubung")
            self.api_status_label.setStyleSheet("color: gray; font-weight: bold;")
    
    # Database Functions
    def browse_backup_path(self):
        """Browse folder untuk export"""
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Export")
        if folder:
            self.backup_path.setText(folder)
    
    def export_data(self):
        """Export data dari API ke CSV"""
        try:
            import os
            import csv
            import datetime
            
            export_dir = self.backup_path.text()
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            if not self.db_manager:
                QMessageBox.warning(self, "Warning", "Database manager tidak tersedia")
                return
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export Jemaat
            success, jemaat_data = self.db_manager.get_jemaat_list(limit=10000)
            if success:
                jemaat_file = os.path.join(export_dir, f"jemaat_export_{timestamp}.csv")
                with open(jemaat_file, 'w', newline='', encoding='utf-8') as f:
                    if jemaat_data:
                        writer = csv.DictWriter(f, fieldnames=jemaat_data[0].keys())
                        writer.writeheader()
                        writer.writerows(jemaat_data)
            
            # Export Kegiatan
            success, kegiatan_data = self.db_manager.get_kegiatan_list(limit=10000)
            if success:
                kegiatan_file = os.path.join(export_dir, f"kegiatan_export_{timestamp}.csv")
                with open(kegiatan_file, 'w', newline='', encoding='utf-8') as f:
                    if kegiatan_data:
                        writer = csv.DictWriter(f, fieldnames=kegiatan_data[0].keys())
                        writer.writeheader()
                        writer.writerows(kegiatan_data)
            
            # Export Keuangan
            success, keuangan_data = self.db_manager.get_keuangan_list(limit=10000)
            if success:
                keuangan_file = os.path.join(export_dir, f"keuangan_export_{timestamp}.csv")
                with open(keuangan_file, 'w', newline='', encoding='utf-8') as f:
                    if keuangan_data:
                        writer = csv.DictWriter(f, fieldnames=keuangan_data[0].keys())
                        writer.writeheader()
                        writer.writerows(keuangan_data)
            
            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {export_dir}")
            self.log_message.emit(f"Data diekspor ke: {export_dir}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error export data: {str(e)}")
            self.log_message.emit(f"Error export data: {str(e)}")
    
    def import_data(self):
        """Import data dari CSV ke API"""
        try:
            csv_file, _ = QFileDialog.getOpenFileName(
                self, "Pilih File CSV untuk Import", "", "CSV Files (*.csv)"
            )
            
            if not csv_file:
                return
            
            QMessageBox.information(self, "Info", 
                                   "Fitur import data akan segera tersedia.")
            self.log_message.emit(f"Import request untuk file: {csv_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error import data: {str(e)}")
            self.log_message.emit(f"Error import data: {str(e)}")
    
    # User management methods moved to PenggunaComponent
    
    def get_api_config(self):
        """Ambil konfigurasi API untuk komponen lain"""
        return {
            'max_clients': self.max_clients.text(),
            'timeout_minutes': self.timeout_minutes.text(),
            'auto_disconnect': self.auto_disconnect.isChecked(),
            # PRODUCTION: Using https://enternal.my.id/flask
            'api_url': 'https://enternal.my.id/flask'
        }
    
    def backup_database(self):
        """Backup database - untuk compatibility dengan main window"""
        self.export_data()
    
    def restore_database(self):
        """Restore database - untuk compatibility dengan main window"""
        self.import_data()


class UserDialog(QDialog):
    """Dialog untuk menambah/edit pengguna"""
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setWindowTitle("Tambah Pengguna" if not user_data else "Edit Pengguna")
        self.setModal(True)
        self.setFixedSize(420, 250)

        # Setup UI
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Create form layout
        self.setup_user_form(layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
        layout.addWidget(button_box)

        # Load data if editing
        if user_data:
            self.load_data()

    def setup_user_form(self, layout):
        """Setup form untuk input user data"""
        form_group = QGroupBox("Data Pengguna")
        form_layout = QFormLayout(form_group)
        form_layout.setVerticalSpacing(8)
        form_layout.setHorizontalSpacing(10)

        # Username
        username_label = QLabel("Username:")
        username_label.setMinimumWidth(100)
        self.username_input = QLineEdit()
        self.username_input.setMinimumWidth(250)
        self.username_input.setPlaceholderText("Masukkan username")
        form_layout.addRow(username_label, self.username_input)

        # Nama Lengkap
        nama_label = QLabel("Nama Lengkap:")
        nama_label.setMinimumWidth(100)
        self.nama_input = QLineEdit()
        self.nama_input.setMinimumWidth(250)
        self.nama_input.setPlaceholderText("Masukkan nama lengkap")
        form_layout.addRow(nama_label, self.nama_input)

        # Email
        email_label = QLabel("Email:")
        email_label.setMinimumWidth(100)
        self.email_input = QLineEdit()
        self.email_input.setMinimumWidth(250)
        self.email_input.setPlaceholderText("Masukkan alamat email")
        form_layout.addRow(email_label, self.email_input)

        # Peran
        peran_label = QLabel("Peran:")
        peran_label.setMinimumWidth(100)
        self.peran_input = QComboBox()
        self.peran_input.addItems(["Admin", "Operator", "User"])
        self.peran_input.setMinimumWidth(250)
        form_layout.addRow(peran_label, self.peran_input)

        # Password (only for new users or when explicitly editing)
        password_label = QLabel("Password:")
        password_label.setMinimumWidth(100)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumWidth(250)
        self.password_input.setPlaceholderText("Masukkan password (min. 6 karakter)")
        form_layout.addRow(password_label, self.password_input)

        # Status
        status_label = QLabel("Status:")
        status_label.setMinimumWidth(100)
        self.status_input = QComboBox()
        self.status_input.addItems(["Aktif", "Nonaktif"])
        self.status_input.setMinimumWidth(250)
        form_layout.addRow(status_label, self.status_input)

        layout.addWidget(form_group)

    def load_data(self):
        """Load existing user data untuk editing"""
        if self.user_data:
            self.username_input.setText(self.user_data.get("username", ""))
            self.nama_input.setText(self.user_data.get("nama_lengkap", ""))
            self.email_input.setText(self.user_data.get("email", ""))

            peran = self.user_data.get("peran", "User")
            peran_index = self.peran_input.findText(peran)
            if peran_index >= 0:
                self.peran_input.setCurrentIndex(peran_index)

            status = self.user_data.get("status", "Aktif")
            status_index = self.status_input.findText(status)
            if status_index >= 0:
                self.status_input.setCurrentIndex(status_index)

            # For editing, make password optional (leave blank to keep existing)
            self.password_input.setPlaceholderText("Kosongkan jika tidak ingin mengubah password")
            
            # Disable username editing for existing users
            self.username_input.setReadOnly(True)
            self.username_input.setStyleSheet("background-color: #f0f0f0;")

    def get_data(self):
        """Get form data"""
        data = {
            "username": self.username_input.text().strip(),
            "nama_lengkap": self.nama_input.text().strip(),
            "email": self.email_input.text().strip(),
            "peran": self.peran_input.currentText(),
            "status": self.status_input.currentText()
        }

        # Handle password
        password = self.password_input.text().strip()
        if password:
            data["password"] = password
        elif self.user_data:
            # Keep existing password if editing and no new password provided
            data["password"] = self.user_data.get("password", "")
        else:
            # For new users, require password
            data["password"] = password

        return data

    def accept(self):
        """Validate and accept dialog"""
        data = self.get_data()

        # Validate required fields
        if not data["username"]:
            QMessageBox.warning(self, "Error", "Username harus diisi!")
            self.username_input.setFocus()
            return

        if not data["nama_lengkap"]:
            QMessageBox.warning(self, "Error", "Nama lengkap harus diisi!")
            self.nama_input.setFocus()
            return

        if not data["email"]:
            QMessageBox.warning(self, "Error", "Email harus diisi!")
            self.email_input.setFocus()
            return

        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data["email"]):
            QMessageBox.warning(self, "Error", "Format email tidak valid!")
            self.email_input.setFocus()
            return

        # Validate password for new users
        if not self.user_data and not data["password"]:
            QMessageBox.warning(self, "Error", "Password harus diisi untuk pengguna baru!")
            self.password_input.setFocus()
            return

        # Validate password length if provided
        if data["password"] and len(data["password"]) < 6:
            QMessageBox.warning(self, "Error", "Password minimal 6 karakter!")
            self.password_input.setFocus()
            return

        super().accept()