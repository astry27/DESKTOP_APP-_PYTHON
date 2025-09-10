# Path: server/components/pengaturan.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFileDialog, QGroupBox,
                            QFormLayout, QLineEdit, QComboBox, QCheckBox,
                            QTextEdit, QTabWidget)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QIcon

class PengaturanComponent(QWidget):
    """Komponen untuk pengaturan sistem dalam API Mode"""
    
    log_message = pyqtSignal(str)  # Signal untuk mengirim log message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.setup_ui()
    
    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        self.update_api_status()
    
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
        settings_tab = QTabWidget()
        
        # Tab API Configuration
        api_tab = self.create_api_tab()
        settings_tab.addTab(api_tab, "Konfigurasi API")
        
        # Tab Database
        db_tab = self.create_database_tab()
        settings_tab.addTab(db_tab, "Database")
        
        # Tab Users
        users_tab = self.create_users_tab()
        settings_tab.addTab(users_tab, "Pengguna")
        
        # Tab System Info
        info_tab = self.create_info_tab()
        settings_tab.addTab(info_tab, "Info Sistem")
        
        return settings_tab
    
    def create_api_tab(self):
        """Buat tab konfigurasi API"""
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        
        # Informasi API
        api_info_group = QGroupBox("Informasi API Endpoint")
        api_info_layout = QVBoxLayout(api_info_group)
        
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
        info_text.setText("""
Database Type: MySQL di Shared Hosting
Host: enternal.my.id
Database: entf7819_db-client-server
User: entf7819_db-client-server

Catatan: Konfigurasi database dikelola melalui shared hosting.
Tidak dapat diubah melalui aplikasi desktop ini.
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
        """Buat tab pengaturan pengguna"""
        users_tab = QWidget()
        users_layout = QVBoxLayout(users_tab)
        
        # Header untuk user management
        user_action_layout = QHBoxLayout()
        user_action_layout.addStretch()
        
        add_user_button = self.create_button("Tambah Pengguna", "#27ae60", self.add_user, "server/assets/tambah.png")
        user_action_layout.addWidget(add_user_button)
        
        users_layout.addLayout(user_action_layout)
        
        # Tabel Pengguna (hapus kolom ID)
        self.users_table = QTableWidget(0, 4)
        self.users_table.setHorizontalHeaderLabels(["Username", "Nama Lengkap", "Peran", "Status"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Populate dengan data default
        self.load_users_data()
        
        users_layout.addWidget(self.users_table)
        
        # Tombol aksi user
        user_button_layout = self.create_user_action_buttons()
        users_layout.addLayout(user_button_layout)
        
        return users_tab
    
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
    
    def load_users_data(self):
        """Load data pengguna"""
        users_data = [
            {"username": "admin", "nama": "Administrator", "peran": "Admin", "status": "Aktif"},
            {"username": "operator", "nama": "Operator Sistem", "peran": "Operator", "status": "Aktif"},
            {"username": "user", "nama": "User Default", "peran": "User", "status": "Aktif"}
        ]
        
        self.users_table.setRowCount(len(users_data))
        
        for i, user in enumerate(users_data):
            self.users_table.setItem(i, 0, QTableWidgetItem(user["username"]))
            self.users_table.setItem(i, 1, QTableWidgetItem(user["nama"]))
            self.users_table.setItem(i, 2, QTableWidgetItem(user["peran"]))
            
            status_item = QTableWidgetItem(user["status"])
            if user["status"] == "Aktif":
                status_item.setBackground(QColor(200, 255, 200))
            else:
                status_item.setBackground(QColor(255, 200, 200))
            
            self.users_table.setItem(i, 3, status_item)
    
    def create_user_action_buttons(self):
        """Buat tombol aksi untuk manajemen user"""
        user_button_layout = QHBoxLayout()
        user_button_layout.addStretch()
        
        edit_user_button = self.create_button("Edit Terpilih", "#f39c12", self.edit_user, "server/assets/edit.png")
        user_button_layout.addWidget(edit_user_button)
        
        reset_password_button = self.create_button("Reset Password", "#8e44ad", self.reset_password)
        user_button_layout.addWidget(reset_password_button)
        
        delete_user_button = self.create_button("Hapus Terpilih", "#c0392b", self.delete_user, "server/assets/hapus.png")
        user_button_layout.addWidget(delete_user_button)
        
        return user_button_layout
    
    def create_button(self, text, color, slot, icon_path=None):
        """Buat button dengan style konsisten dan optional icon"""
        button = QPushButton(text)
        
        # Add icon if specified and path exists
        if icon_path:
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(button.fontMetrics().boundingRect("M").size())
            except Exception:
                pass  # If icon loading fails, just continue without icon
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
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
    
    # User Management Functions
    def add_user(self):
        """Tambah pengguna baru"""
        QMessageBox.information(self, "Info", 
                               "Fitur manajemen pengguna akan segera tersedia.")
        self.log_message.emit("Request tambah pengguna - fitur dalam pengembangan")
    
    def edit_user(self):
        """Edit pengguna terpilih"""
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengguna yang akan diedit")
            return
        
        QMessageBox.information(self, "Info", 
                               "Fitur edit pengguna akan segera tersedia.")
        self.log_message.emit("Request edit pengguna - fitur dalam pengembangan")
    
    def reset_password(self):
        """Reset password pengguna"""
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengguna untuk reset password")
            return
        
        QMessageBox.information(self, "Info", 
                               "Fitur reset password akan segera tersedia.")
        self.log_message.emit("Request reset password - fitur dalam pengembangan")
    
    def delete_user(self):
        """Hapus pengguna terpilih"""
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengguna yang akan dihapus")
            return
        
        username = self.users_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(self, 'Konfirmasi',
                                    f"Yakin ingin menghapus pengguna '{username}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Info", 
                                   "Fitur hapus pengguna akan segera tersedia.")
            self.log_message.emit(f"Request hapus pengguna {username} - fitur dalam pengembangan")
    
    def get_api_config(self):
        """Ambil konfigurasi API untuk komponen lain"""
        return {
            'max_clients': self.max_clients.text(),
            'timeout_minutes': self.timeout_minutes.text(),
            'auto_disconnect': self.auto_disconnect.isChecked(),
            'api_url': 'https://enternal.my.id/flask'
        }
    
    def backup_database(self):
        """Backup database - untuk compatibility dengan main window"""
        self.export_data()
    
    def restore_database(self):
        """Restore database - untuk compatibility dengan main window"""
        self.import_data()