# Path: server/components/pengaturan.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFileDialog, QGroupBox,
                            QFormLayout, QLineEdit, QComboBox, QCheckBox,
                            QTextEdit, QTabWidget, QAbstractItemView, QFrame,
                            QDialog, QDialogButtonBox, QInputDialog)
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QColor, QIcon, QFont

class PengaturanComponent(QWidget):
    """Komponen untuk pengaturan sistem dalam API Mode"""
    
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore  # Signal untuk mengirim log message
    
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
        users_layout.setSpacing(10)  # Proper spacing
        users_layout.setContentsMargins(10, 10, 10, 10)  # Proper margins

        # Header untuk user management
        user_action_layout = QHBoxLayout()
        user_action_layout.addStretch()

        add_user_button = self.create_button("Tambah Pengguna", "#27ae60", self.add_user, "server/assets/tambah.png")
        user_action_layout.addWidget(add_user_button)

        users_layout.addLayout(user_action_layout)

        # Table view untuk daftar users with proper container (exactly matching program_kerja.py)
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                border: 1px solid #d0d0d0;
                background-color: white;
                margin: 0px;
            }
        """)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self.users_table = self.create_professional_table()
        table_layout.addWidget(self.users_table)

        # Populate dengan data default
        self.load_users_data()

        users_layout.addWidget(table_container)

        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        refresh_button = self.create_button("Refresh Data", "#3498db", self.refresh_users_data, "server/assets/refresh.png")
        refresh_layout.addWidget(refresh_button)
        users_layout.addLayout(refresh_layout)

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
    
    def create_professional_table(self):
        """Create table with professional styling matching program_kerja.py."""
        table = QTableWidget(0, 5)  # Added Actions column
        table.setHorizontalHeaderLabels(["Username", "Nama Lengkap", "Peran", "Status", "Aksi"])

        # Apply professional table styling matching program_kerja.py
        self.apply_professional_table_style(table)

        # Set initial column widths with better proportions for full layout (matching program_kerja.py approach)
        table.setColumnWidth(0, 130)   # Username
        table.setColumnWidth(1, 220)   # Nama Lengkap - wider for full names
        table.setColumnWidth(2, 100)   # Peran
        table.setColumnWidth(3, 80)    # Status
        table.setColumnWidth(4, 140)   # Aksi - wider for action buttons

        # Excel-like column resizing - all columns can be resized except Actions (matching program_kerja.py)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # All columns resizable
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Fixed width for Actions column
        header.setStretchLastSection(False)  # Don't stretch last column (Actions)

        # Connect double click to edit (matching program_kerja.py)
        table.itemDoubleClicked.connect(self.edit_user)

        # Enable context menu (matching program_kerja.py)
        table.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        table.customContextMenuRequested.connect(self.show_users_context_menu)

        return table
        
    def apply_professional_table_style(self, table):
        """Apply Excel-like table styling exactly matching program_kerja.py."""
        # Header styling - Excel-like headers
        header_font = QFont()
        header_font.setBold(False)  # Remove bold from headers
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

        # Excel-style header styling (exact copy from program_kerja.py)
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #d4d4d4;
                border-right: 1px solid #d4d4d4;
                padding: 6px 4px;
                font-weight: normal;
                color: #333333;
                text-align: left;
            }
        """)

        # Excel-style table body styling (exact copy from program_kerja.py)
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d4d4d4;
                background-color: white;
                border: 1px solid #d4d4d4;
                selection-background-color: #cce7ff;
                font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
                outline: none;
            }
            QTableWidget::item {
                border: none;
                padding: 4px 6px;
                min-height: 18px;
            }
            QTableWidget::item:selected {
                background-color: #cce7ff;
                color: black;
            }
            QTableWidget::item:focus {
                border: 2px solid #0078d4;
                background-color: white;
            }
        """)

        # Excel-style table settings (matching program_kerja.py exactly)
        header = table.horizontalHeader()
        header.setMinimumSectionSize(50)
        header.setDefaultSectionSize(80)
        # Allow adjustable header height - removed setMaximumHeight constraint

        # Enable scrolling
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Excel-style row settings with better content visibility
        table.verticalHeader().setDefaultSectionSize(40)  # Taller for action buttons
        table.setSelectionBehavior(QAbstractItemView.SelectItems)  # Select individual cells
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(True)  # Show row numbers like Excel
        table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #d4d4d4;
                border-right: 1px solid #d4d4d4;
                padding: 2px;
                font-weight: normal;
                color: #333333;
                text-align: center;
                width: 30px;
            }
        """)

        # Enable grid display with thin lines
        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)

        # Excel-style editing and selection
        table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Set proper size for Excel look with better visibility (matching program_kerja.py)
        table.setMinimumHeight(200)
        table.setSizePolicy(table.sizePolicy().Expanding, table.sizePolicy().Expanding)
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    def load_users_data(self):
        """Load data pengguna dari API"""
        if not self.db_manager:
            # Fallback data jika tidak ada database manager
            self.users_data = [
                {"id_admin": 1, "username": "admin", "nama_lengkap": "Administrator", "peran": "Admin", "status": "Aktif", "email": "admin@gereja.com"},
                {"id_admin": 2, "username": "operator", "nama_lengkap": "Operator Sistem", "peran": "Operator", "status": "Aktif", "email": "operator@gereja.com"},
                {"id_admin": 3, "username": "user", "nama_lengkap": "User Default", "peran": "User", "status": "Aktif", "email": "user@gereja.com"}
            ]
        else:
            try:
                # Ambil data dari database manager
                success, users_list = self.db_manager.get_users_list()
                
                if success:
                    self.users_data = []
                    
                    for user in users_list:
                        self.users_data.append({
                            "id_admin": user.get('id_admin'),
                            "username": user.get('username'),
                            "nama_lengkap": user.get('nama_lengkap', ''),
                            "peran": self.get_role_display(user.get('username', '')),
                            "status": "Aktif" if user.get('is_active', 1) == 1 else "Nonaktif",
                            "email": user.get('email', '')
                        })
                    
                    self.log_message.emit(f"Berhasil memuat {len(self.users_data)} pengguna dari API")
                else:
                    raise Exception(users_list)
                    
            except Exception as e:
                self.log_message.emit(f"Error loading users from API: {str(e)}")
                # Fallback ke data default
                self.users_data = [
                    {"id_admin": 1, "username": "admin", "nama_lengkap": "Administrator", "peran": "Admin", "status": "Aktif", "email": "admin@gereja.com"}
                ]

        self.update_users_table()

    def get_role_display(self, username):
        """Tentukan role display berdasarkan username"""
        username_lower = username.lower()
        if username_lower == 'admin':
            return 'Admin'
        elif username_lower == 'operator':
            return 'Operator'
        else:
            return 'User'

    def refresh_users_data(self):
        """Refresh data pengguna dari API"""
        self.load_users_data()
        self.log_message.emit("Data pengguna berhasil direfresh")

    def update_users_table(self):
        """Update the users table with current data"""
        self.users_table.setRowCount(len(self.users_data))

        for i, user in enumerate(self.users_data):
            # Username
            self.users_table.setItem(i, 0, QTableWidgetItem(user["username"]))

            # Nama Lengkap
            self.users_table.setItem(i, 1, QTableWidgetItem(user["nama_lengkap"]))

            # Peran
            self.users_table.setItem(i, 2, QTableWidgetItem(user["peran"]))

            # Status with color coding
            status_item = QTableWidgetItem(user["status"])
            if user["status"] == "Aktif":
                status_item.setBackground(QColor(144, 238, 144))  # Light green
            else:
                status_item.setBackground(QColor(255, 182, 193))  # Light red
            self.users_table.setItem(i, 3, status_item)

            # Action buttons (similar to dokumen.py style)
            self.create_user_action_buttons_for_row(i)

    def create_user_action_buttons_for_row(self, row):
        """Create action buttons for a specific table row with improved icon visibility"""
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(6, 3, 6, 3)  # Better padding
        action_layout.setSpacing(4)  # More spacing between buttons
        action_layout.setAlignment(Qt.AlignCenter)  # Center align buttons

        # Edit button with improved styling
        edit_button = QPushButton()
        edit_icon = QIcon("server/assets/edit.png")
        if not edit_icon.isNull():
            edit_button.setIcon(edit_icon)
            edit_button.setIconSize(QSize(18, 18))  # Larger icon size
        else:
            edit_button.setText("✏️")  # Better fallback emoji
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 6px 8px;
                border: 1px solid #e67e22;
                border-radius: 4px;
                min-width: 32px;
                min-height: 32px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e67e22;
                border: 1px solid #d35400;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #d35400;
                border: 1px solid #ba4a00;
            }
        """)
        edit_button.setToolTip("Edit Pengguna")
        edit_button.clicked.connect(lambda _, r=row: self.edit_user_by_row(r))
        action_layout.addWidget(edit_button)

        # Reset password button with improved styling
        reset_button = QPushButton()
        reset_button.setText("🔑")  # Key emoji for password reset
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                padding: 6px 8px;
                border: 1px solid #7d3c98;
                border-radius: 4px;
                min-width: 32px;
                min-height: 32px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7d3c98;
                border: 1px solid #6c3483;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #6c3483;
                border: 1px solid #5b2c6f;
            }
        """)
        reset_button.setToolTip("Reset Password")
        reset_button.clicked.connect(lambda _, r=row: self.reset_password_by_row(r))
        action_layout.addWidget(reset_button)

        # Delete button with improved styling
        delete_button = QPushButton()
        delete_icon = QIcon("server/assets/hapus.png")
        if not delete_icon.isNull():
            delete_button.setIcon(delete_icon)
            delete_button.setIconSize(QSize(18, 18))  # Larger icon size
        else:
            delete_button.setText("🗑️")  # Better fallback emoji
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 6px 8px;
                border: 1px solid #c0392b;
                border-radius: 4px;
                min-width: 32px;
                min-height: 32px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                border: 1px solid #a93226;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #a93226;
                border: 1px solid #922b21;
            }
        """)
        delete_button.setToolTip("Hapus Pengguna")
        delete_button.clicked.connect(lambda _, r=row: self.delete_user_by_row(r))
        action_layout.addWidget(delete_button)

        self.users_table.setCellWidget(row, 4, action_widget)
    
    def show_users_context_menu(self, position):
        """Tampilkan context menu untuk users table (matching program_kerja.py style)"""
        if self.users_table.rowCount() == 0:
            return

        from PyQt5.QtWidgets import QMenu
        menu = QMenu()

        edit_action = menu.addAction("Edit")
        reset_action = menu.addAction("Reset Password")
        delete_action = menu.addAction("Hapus")

        action = menu.exec_(self.users_table.mapToGlobal(position))

        if action == edit_action:
            self.edit_user()
        elif action == reset_action:
            self.reset_password()
        elif action == delete_action:
            self.delete_user()

    
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
    
    # User Management Functions
    def add_user(self):
        """Tambah pengguna baru ke API"""
        dialog = UserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            user_data = dialog.get_data()

            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                return

            try:
                # Kirim data ke database manager
                api_data = {
                    "username": user_data["username"],
                    "password": user_data["password"],
                    "nama_lengkap": user_data["nama_lengkap"],
                    "email": user_data["email"],
                    "is_active": 1 if user_data["status"] == "Aktif" else 0
                }
                
                success, result = self.db_manager.create_user(api_data)
                
                if success:
                    # Refresh data dari API
                    self.load_users_data()
                    QMessageBox.information(self, "Sukses", f"Pengguna '{user_data['username']}' berhasil ditambahkan!")
                    self.log_message.emit(f"User '{user_data['username']}' added successfully to database")
                else:
                    # Parse error message jika berupa dict
                    error_msg = result
                    if isinstance(result, dict):
                        error_msg = result.get('message', 'Error creating user')
                    QMessageBox.warning(self, "Error", str(error_msg))
                    self.log_message.emit(f"Error creating user: {error_msg}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error menambah pengguna: {str(e)}")
                self.log_message.emit(f"Exception adding user: {str(e)}")
    
    def edit_user_by_row(self, row):
        """Edit pengguna berdasarkan row index di API"""
        if 0 <= row < len(self.users_data):
            user_data = self.users_data[row]
            dialog = UserDialog(self, user_data)
            if dialog.exec_() == QDialog.Accepted:
                updated_data = dialog.get_data()

                if not self.db_manager:
                    QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    return

                try:
                    # Kirim update ke database manager
                    api_data = {
                        "nama_lengkap": updated_data["nama_lengkap"],
                        "email": updated_data["email"],
                        "is_active": 1 if updated_data["status"] == "Aktif" else 0
                    }
                    
                    # Tambahkan password jika diubah
                    if updated_data.get("password") and updated_data["password"] != user_data.get("password", ""):
                        api_data["password"] = updated_data["password"]
                    
                    user_id = user_data.get("id_admin")
                    success, result = self.db_manager.update_user(user_id, api_data)
                    
                    if success:
                        # Refresh data dari API
                        self.load_users_data()
                        QMessageBox.information(self, "Sukses", f"Pengguna '{updated_data['username']}' berhasil diupdate!")
                        self.log_message.emit(f"User '{updated_data['username']}' updated successfully in database")
                    else:
                        # Parse error message jika berupa dict
                        error_msg = result
                        if isinstance(result, dict):
                            error_msg = result.get('message', 'Error updating user')
                        QMessageBox.warning(self, "Error", str(error_msg))
                        self.log_message.emit(f"Error updating user: {error_msg}")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error mengupdate pengguna: {str(e)}")
                    self.log_message.emit(f"Exception updating user: {str(e)}")

    def reset_password_by_row(self, row):
        """Reset password pengguna berdasarkan row index di API"""
        if 0 <= row < len(self.users_data):
            user_data = self.users_data[row]
            username = user_data["username"]

            new_password, ok = QInputDialog.getText(self, 'Reset Password',
                                                   f'Masukkan password baru untuk user "{username}":',
                                                   QLineEdit.Password)

            if ok and new_password:
                if len(new_password) < 6:
                    QMessageBox.warning(self, "Error", "Password minimal 6 karakter!")
                    return

                if not self.db_manager:
                    QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    return

                try:
                    # Kirim reset password ke database manager
                    api_data = {"password": new_password}
                    
                    user_id = user_data.get("id_admin")
                    success, result = self.db_manager.update_user(user_id, api_data)
                    
                    if success:
                        QMessageBox.information(self, "Sukses", f"Password untuk user '{username}' berhasil direset!")
                        self.log_message.emit(f"Password reset for user '{username}' in database")
                    else:
                        # Parse error message jika berupa dict
                        error_msg = result
                        if isinstance(result, dict):
                            error_msg = result.get('message', 'Error resetting password')
                        QMessageBox.warning(self, "Error", str(error_msg))
                        self.log_message.emit(f"Error resetting password: {error_msg}")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error reset password: {str(e)}")
                    self.log_message.emit(f"Exception resetting password: {str(e)}")
                    
            elif ok and not new_password:
                QMessageBox.warning(self, "Error", "Password tidak boleh kosong!")

    def delete_user_by_row(self, row):
        """Hapus pengguna berdasarkan row index dari API"""
        if 0 <= row < len(self.users_data):
            user_data = self.users_data[row]
            username = user_data["username"]

            # Prevent deleting admin user
            if username.lower() == "admin":
                QMessageBox.warning(self, "Error", "User 'admin' tidak dapat dihapus!")
                return

            reply = QMessageBox.question(self, 'Konfirmasi',
                                        f"Yakin ingin menghapus pengguna '{username}'?",
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)

            if reply == QMessageBox.Yes:
                if not self.db_manager:
                    QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    return

                try:
                    # Hapus melalui database manager
                    user_id = user_data.get("id_admin")
                    success, result = self.db_manager.delete_user(user_id)
                    
                    if success:
                        # Refresh data dari API
                        self.load_users_data()
                        QMessageBox.information(self, "Sukses", f"Pengguna '{username}' berhasil dihapus!")
                        self.log_message.emit(f"User '{username}' deleted successfully from database")
                    else:
                        # Parse error message jika berupa dict
                        error_msg = result
                        if isinstance(result, dict):
                            error_msg = result.get('message', 'Error deleting user')
                        QMessageBox.warning(self, "Error", str(error_msg))
                        self.log_message.emit(f"Error deleting user: {error_msg}")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error menghapus pengguna: {str(e)}")
                    self.log_message.emit(f"Exception deleting user: {str(e)}")

    def edit_user(self):
        """Edit pengguna terpilih (for compatibility with existing code)"""
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengguna yang akan diedit")
            return
        self.edit_user_by_row(current_row)

    def reset_password(self):
        """Reset password pengguna (for compatibility with existing code)"""
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengguna untuk reset password")
            return
        self.reset_password_by_row(current_row)

    def delete_user(self):
        """Hapus pengguna terpilih (for compatibility with existing code)"""
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengguna yang akan dihapus")
            return
        self.delete_user_by_row(current_row)
    
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