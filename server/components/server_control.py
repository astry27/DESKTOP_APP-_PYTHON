# Path: server/components/server_control.py

import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QFormLayout, QPushButton, QLabel, QTableWidget,
                            QTableWidgetItem, QHeaderView, QTextEdit, QMessageBox,
                            QInputDialog, QFileDialog, QAbstractItemView, QFrame)
from PyQt5.QtCore import pyqtSignal, QTimer, QSize, Qt
from PyQt5.QtGui import QColor, QIcon

class ServerControlComponent(QWidget):
    
    log_message = pyqtSignal(str)
    visibility_changed = pyqtSignal(bool)  # Signal for layout visibility change
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.database_manager = None
        self.connected_clients = []
        self.is_visible = True  # Track visibility state
        self.setup_ui()
        
        # Timer untuk auto-refresh status API dan client
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.auto_refresh_status)
        self.status_timer.start(10000)  # Cek setiap 10 detik
    
    def set_database_manager(self, database_manager):
        self.database_manager = database_manager
        self.auto_refresh_status()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toggle button for hide/show
        toggle_layout = QHBoxLayout()
        self.toggle_button = QPushButton("▼ Sembunyikan Kontrol Server")
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
                text-align: left;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_visibility)
        toggle_layout.addWidget(self.toggle_button)
        toggle_layout.addStretch()
        layout.addLayout(toggle_layout)
        
        # Control panel
        self.control_group = self.create_control_panel()
        layout.addWidget(self.control_group)
    
    def create_control_panel(self):
        control_group = QGroupBox("Kontrol API Server")
        control_layout = QHBoxLayout(control_group)
        
        # API Control Section
        api_form = QFormLayout()
        
        self.api_status_label = QLabel("Mengecek...")
        self.api_status_label.setStyleSheet("color: orange; font-weight: bold;")
        
        self.clients_label = QLabel("0")
        
        api_form.addRow("Status API:", self.api_status_label)
        api_form.addRow("Client Terhubung:", self.clients_label)
        control_layout.addLayout(api_form)
        
        # Button Controls
        button_layout = QVBoxLayout()
        
        self.enable_api_button = QPushButton("Aktifkan API")
        self.enable_api_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        
        self.disable_api_button = QPushButton("Nonaktifkan API")
        self.disable_api_button.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        
        self.refresh_button = QPushButton("Refresh Status")
        # Add refresh icon
        refresh_icon = QIcon("server/assets/refresh.png")
        if not refresh_icon.isNull():
            self.refresh_button.setIcon(refresh_icon)
            self.refresh_button.setIconSize(QSize(20, 20))  # Larger icon size for better visibility
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.enable_api_button.clicked.connect(self.enable_api)
        self.disable_api_button.clicked.connect(self.disable_api)
        self.refresh_button.clicked.connect(self.auto_refresh_status)
        
        button_layout.addWidget(self.enable_api_button)
        button_layout.addWidget(self.disable_api_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        control_layout.addLayout(button_layout)
        
        # Client and Log Layout
        client_log_layout = QVBoxLayout()
        
        # Client Table with professional styling
        client_group = QGroupBox("Client Terhubung")
        client_layout = QVBoxLayout(client_group)
        
        # Table view untuk daftar client with proper container
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
        
        self.client_table = self.create_professional_table()
        table_layout.addWidget(self.client_table)
        
        client_layout.addWidget(table_container)
        
        # Log Section
        log_group = QGroupBox("Log Aktivitas")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_button_layout = self.create_log_buttons()
        log_layout.addLayout(log_button_layout)
        
        client_log_layout.addWidget(client_group)
        client_log_layout.addWidget(log_group)
        
        control_layout.addLayout(client_log_layout, 1)
        
        # Initial status check
        self.auto_refresh_status()
        
        return control_group
    
    def create_log_buttons(self):
        log_button_layout = QHBoxLayout()
        
        self.clear_log_button = QPushButton("Bersihkan Log")
        self.clear_log_button.clicked.connect(self.clear_log)
        self.clear_log_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        self.save_log_button = QPushButton("Simpan Log")
        self.save_log_button.clicked.connect(self.save_log)
        self.save_log_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.broadcast_button = QPushButton("Broadcast Message")
        self.broadcast_button.clicked.connect(self.send_broadcast_message)
        self.broadcast_button.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #9b59b6;
            }
        """)
        
        log_button_layout.addWidget(self.clear_log_button)
        log_button_layout.addWidget(self.save_log_button)
        log_button_layout.addWidget(self.broadcast_button)
        
        return log_button_layout
    
    def create_professional_table(self):
        """Create table with professional styling."""
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["IP Address", "Hostname", "Waktu Koneksi", "Terakhir Aktif", "Status"])
        
        # Apply professional table styling
        self.apply_professional_table_style(table)
        
        # Set specific column widths
        column_widths = [120, 150, 130, 120, 100]  # Total: 620px
        for i, width in enumerate(column_widths):
            table.setColumnWidth(i, width)
        
        # Set minimum table width to sum of all columns
        table.setMinimumWidth(sum(column_widths) + 50)  # Add padding for scrollbar
        
        return table
        
    def apply_professional_table_style(self, table):
        """Apply Excel-like table styling with thin grid lines and minimal borders."""
        # Header styling - Excel-like headers
        from PyQt5.QtGui import QFont
        header_font = QFont()
        header_font.setBold(False)  # Remove bold from headers
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

        # Excel-style header styling
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

        # Excel-style table body styling
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

        # Excel-style table settings
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # Allow column resizing
        header.setStretchLastSection(False)  # Don't stretch last column
        header.setMinimumSectionSize(50)
        header.setDefaultSectionSize(80)
        # Allow adjustable header height - removed setMaximumHeight constraint

        # Enable scrolling
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Excel-style row settings
        table.verticalHeader().setDefaultSectionSize(20)  # Thin rows like Excel
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

        # Set compact size for Excel look
        table.setMinimumHeight(150)
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    def auto_refresh_status(self):
        """Auto refresh status API dan client yang terhubung"""
        self.check_api_status()
        self.load_connected_clients()
    
    def check_api_status(self):
        """Cek status API shared hosting"""
        if self.database_manager:
            success, status_data = self.database_manager.get_api_service_status()
            if success:
                api_enabled = status_data.get('api_enabled', False)
                if api_enabled:
                    self.api_status_label.setText("Aktif")
                    self.api_status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.enable_api_button.setEnabled(False)
                    self.disable_api_button.setEnabled(True)
                else:
                    self.api_status_label.setText("Nonaktif")
                    self.api_status_label.setStyleSheet("color: red; font-weight: bold;")
                    self.enable_api_button.setEnabled(True)
                    self.disable_api_button.setEnabled(False)
                return api_enabled
            else:
                self.api_status_label.setText("Error")
                self.api_status_label.setStyleSheet("color: red; font-weight: bold;")
                return False
        else:
            self.api_status_label.setText("Tidak Terhubung")
            self.api_status_label.setStyleSheet("color: gray; font-weight: bold;")
            return False
    
    def enable_api(self):
        """Aktifkan API shared hosting"""
        if self.database_manager:
            self.log_message.emit("Mengaktifkan API shared hosting...")
            success, message = self.database_manager.enable_api_service()
            if success:
                self.log_message.emit(f"Sukses: {message}")
                self.auto_refresh_status()
                QMessageBox.information(self, "Sukses", "API berhasil diaktifkan")
            else:
                self.log_message.emit(f"Gagal: {message}")
                QMessageBox.warning(self, "Error", f"Gagal mengaktifkan API: {message}")
    
    def disable_api(self):
        """Nonaktifkan API shared hosting"""
        reply = QMessageBox.question(self, 'Konfirmasi',
                                   "Yakin ingin menonaktifkan API? Semua client akan terputus.",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.database_manager:
                self.log_message.emit("Menonaktifkan API shared hosting...")
                success, message = self.database_manager.disable_api_service()
                if success:
                    self.log_message.emit(f"Sukses: {message}")
                    self.auto_refresh_status()
                    QMessageBox.information(self, "Sukses", "API berhasil dinonaktifkan")
                else:
                    self.log_message.emit(f"Gagal: {message}")
                    QMessageBox.warning(self, "Error", f"Gagal menonaktifkan API: {message}")
    
    def load_connected_clients(self):
        """Load daftar client yang benar-benar aktif melalui API"""
        if not self.database_manager:
            return
        
        try:
            # Ambil data client yang terhubung dari API
            success, result = self.database_manager.get_active_sessions()
            
            if success:
                # Handle berbagai format response dari API
                if isinstance(result, dict):
                    if 'data' in result:
                        clients = result['data']
                    elif 'clients' in result:
                        clients = result['clients']
                    else:
                        clients = []
                elif isinstance(result, list):
                    clients = result
                else:
                    clients = []
                
                # Filter hanya client yang benar-benar aktif/terhubung dengan timeout check
                import datetime
                active_clients = []
                current_time = datetime.datetime.now()
                
                for client in clients:
                    status = client.get('status', '').lower()
                    last_activity = client.get('last_activity') or client.get('connect_time')
                    
                    # Check jika client benar-benar aktif berdasarkan status dan waktu aktivitas terakhir
                    is_active = False
                    if status in ['aktif', 'active', 'terhubung', 'connected', 'online']:
                        if last_activity:
                            try:
                                if isinstance(last_activity, str):
                                    if 'T' in last_activity:
                                        last_time = datetime.datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                                    else:
                                        last_time = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
                                else:
                                    last_time = last_activity
                                
                                # Client dianggap aktif jika aktivitas terakhir kurang dari 5 menit yang lalu
                                time_diff = current_time - last_time.replace(tzinfo=None)
                                if time_diff.total_seconds() < 300:  # 5 menit
                                    is_active = True
                                else:
                                    # Update status jika sudah timeout
                                    client['status'] = 'timeout'
                            except:
                                # Jika tidak bisa parsing waktu, anggap tidak aktif
                                client['status'] = 'unknown'
                        else:
                            # Jika tidak ada waktu aktivitas, anggap tidak aktif
                            client['status'] = 'no_activity'
                    
                    if is_active:
                        active_clients.append(client)
                
                self.connected_clients = active_clients
                self.update_client_table()
                self.clients_label.setText(str(len(active_clients)))
                
                # Log untuk debugging
                total_sessions = len(clients)
                active_count = len(active_clients)
                self.log_message.emit(f"Total Sessions: {total_sessions}, Client Benar-benar Aktif: {active_count}")
                
            else:
                self.connected_clients = []
                self.update_client_table()
                self.clients_label.setText("0")
                self.log_message.emit("Gagal mengambil data sessions")
        except Exception as e:
            self.connected_clients = []
            self.update_client_table()
            self.clients_label.setText("0")
            self.log_message.emit(f"Error loading clients: {str(e)}")
    
    def update_client_table(self):
        """Update tabel client yang benar-benar terhubung"""
        self.client_table.setRowCount(len(self.connected_clients))
        
        for i, client in enumerate(self.connected_clients):
            self.client_table.setItem(i, 0, QTableWidgetItem(client.get('client_ip', 'Unknown')))
            self.client_table.setItem(i, 1, QTableWidgetItem(client.get('hostname', 'Unknown')))
            
            # Format waktu koneksi
            connect_time = client.get('connect_time', '')
            if connect_time:
                if isinstance(connect_time, str):
                    try:
                        # Handle different datetime formats
                        if 'T' in connect_time:
                            dt = datetime.datetime.fromisoformat(connect_time.replace('Z', '+00:00'))
                        else:
                            dt = datetime.datetime.strptime(connect_time, '%Y-%m-%d %H:%M:%S')
                        time_str = dt.strftime('%d/%m/%Y %H:%M:%S')
                    except:
                        time_str = str(connect_time)
                else:
                    time_str = str(connect_time)
            else:
                time_str = '-'
            
            self.client_table.setItem(i, 2, QTableWidgetItem(time_str))
            
            # Waktu terakhir aktif
            last_activity = client.get('last_activity') or client.get('connect_time', '')
            if last_activity:
                if isinstance(last_activity, str):
                    try:
                        # Handle different datetime formats
                        if 'T' in last_activity:
                            dt = datetime.datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                        else:
                            dt = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
                        last_active_str = dt.strftime('%d/%m/%Y %H:%M:%S')
                        
                        # Hitung waktu yang telah berlalu
                        current_time = datetime.datetime.now()
                        time_diff = current_time - dt.replace(tzinfo=None)
                        
                        if time_diff.total_seconds() < 60:
                            last_active_str += " (Sekarang)"
                        elif time_diff.total_seconds() < 3600:
                            minutes = int(time_diff.total_seconds() / 60)
                            last_active_str += f" ({minutes}m yang lalu)"
                        else:
                            hours = int(time_diff.total_seconds() / 3600)
                            last_active_str += f" ({hours}h yang lalu)"
                    except:
                        last_active_str = str(last_activity)
                else:
                    last_active_str = str(last_activity)
            else:
                last_active_str = 'Tidak diketahui'
            
            self.client_table.setItem(i, 3, QTableWidgetItem(last_active_str))
            
            # Status dengan warna yang sesuai
            status = client.get('status', 'Unknown')
            status_item = QTableWidgetItem(status)
            
            # Color coding berdasarkan status
            status_lower = status.lower()
            if status_lower in ['aktif', 'active', 'terhubung', 'connected', 'online']:
                status_item.setBackground(QColor(144, 238, 144))  # Light green
                status_item.setText('Aktif')
            elif status_lower in ['disconnect', 'disconnected', 'offline', 'terputus']:
                status_item.setBackground(QColor(255, 182, 193))  # Light red
                status_item.setText('Terputus')
            elif status_lower == 'timeout':
                status_item.setBackground(QColor(255, 165, 0, 100))  # Light orange
                status_item.setText('Timeout')
            else:
                status_item.setBackground(QColor(255, 255, 224))  # Light yellow
                status_item.setText(status)
            
            self.client_table.setItem(i, 4, status_item)
    
    def send_broadcast_message(self):
        """Kirim broadcast message ke semua client melalui API"""
        if not self.database_manager:
            QMessageBox.warning(self, "Warning", "Database manager tidak tersedia!")
            return
        
        # Cek apakah API aktif
        if not self.check_api_status():
            QMessageBox.warning(self, "Warning", "API tidak aktif! Aktifkan API terlebih dahulu.")
            return
        
        message, ok = QInputDialog.getText(self, "Kirim Pesan Broadcast", 
                                         "Masukkan pesan untuk semua client:")
        if ok and message:
            try:
                # Kirim broadcast melalui API
                success, result = self.database_manager.send_broadcast_message(message)
                
                if success:
                    QMessageBox.information(self, "Sukses", "Pesan broadcast berhasil dikirim")
                    self.log_message.emit(f"Pesan broadcast terkirim: {message}")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal mengirim pesan broadcast: {result}")
                    self.log_message.emit(f"Error broadcast: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error mengirim broadcast: {str(e)}")
                self.log_message.emit(f"Exception broadcast: {str(e)}")
    
    def add_log_message(self, message):
        """Tambah pesan ke log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_text.append(log_entry)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """Bersihkan log"""
        self.log_text.clear()
        self.log_message.emit("Log dibersihkan")
    
    def save_log(self):
        """Simpan log ke file"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Simpan Log Server", "server_log.txt", "Text Files (*.txt)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                
                QMessageBox.information(self, "Sukses", f"Log berhasil disimpan ke {filename}")
                self.log_message.emit(f"Log disimpan ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error menyimpan log: {str(e)}")
            self.log_message.emit(f"Exception saving log: {str(e)}")
    
    def is_api_active(self):
        """Cek apakah API sedang aktif"""
        return self.check_api_status()
    
    def toggle_visibility(self):
        """Toggle visibility of server control panel"""
        self.is_visible = not self.is_visible
        
        if self.is_visible:
            # Show the control panel
            self.control_group.show()
            self.toggle_button.setText("▼ Sembunyikan Kontrol Server")
        else:
            # Hide the control panel
            self.control_group.hide()
            self.toggle_button.setText("▶ Tampilkan Kontrol Server")
        
        # Emit signal to notify main layout of visibility change
        self.visibility_changed.emit(self.is_visible)
    
    def get_visibility_state(self):
        """Get current visibility state"""
        return self.is_visible
    
    def set_visibility(self, visible):
        """Set visibility programmatically"""
        if self.is_visible != visible:
            self.toggle_visibility()