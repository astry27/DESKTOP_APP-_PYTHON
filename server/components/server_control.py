# Path: server/components/server_control.py

import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QFormLayout, QPushButton, QLabel, QTableWidget,
                            QTableWidgetItem, QHeaderView, QTextEdit, QMessageBox,
                            QInputDialog, QFileDialog, QAbstractItemView, QFrame, QSizePolicy, QTabWidget)
from PyQt5.QtCore import pyqtSignal, QTimer, QSize, Qt
from PyQt5.QtGui import QColor, QIcon

class ServerControlComponent(QWidget):
    
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore
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

    def closeEvent(self, event):
        """Handle close event to stop timer"""
        if hasattr(self, 'status_timer') and self.status_timer:
            self.status_timer.stop()
            self.status_timer.deleteLater()
        event.accept()

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

        # Client Table
        client_group = QGroupBox("Client Terhubung")
        client_layout = QVBoxLayout(client_group)
        client_layout.setContentsMargins(8, 8, 8, 8)
        client_layout.setSpacing(4)

        self.client_table = self.create_professional_table_connected()
        self.client_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        client_layout.addWidget(self.client_table)

        client_log_layout.addWidget(client_group)
        
        # Log Section
        log_group = QGroupBox("Log Aktivitas")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_button_layout = self.create_log_buttons()
        log_layout.addLayout(log_button_layout)

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

        log_button_layout.addWidget(self.clear_log_button)
        log_button_layout.addWidget(self.save_log_button)
        log_button_layout.addStretch()

        return log_button_layout
    
    def create_professional_table_connected(self):
        """Create table for connected clients with professional styling."""
        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels(["ID", "IP Address", "Hostname", "Waktu Koneksi", "Terakhir Aktif", "Status"])

        # Apply professional table styling
        self.apply_professional_table_style(table)

        # Set initial column widths with better proportions for full layout
        table.setColumnWidth(0, 50)    # ID - small column
        table.setColumnWidth(1, 120)   # IP Address
        table.setColumnWidth(2, 180)   # Hostname - wider for content
        table.setColumnWidth(3, 150)   # Waktu Koneksi
        table.setColumnWidth(4, 150)   # Terakhir Aktif
        table.setColumnWidth(5, 100)   # Status

        # Excel-like column resizing - all columns can be resized
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # All columns resizable
        header.setStretchLastSection(True)  # Last column stretches to fill space

        # Connect double click to show client details (future enhancement)
        # table.itemDoubleClicked.connect(self.show_client_details)

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
        table.verticalHeader().setDefaultSectionSize(22)  # Slightly taller for client data
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

        # Set to fill available space
        table.setMinimumHeight(200)
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    def auto_refresh_status(self):
        """Auto refresh status API dan client yang terhubung"""
        try:
            self.check_api_status()
            self.load_connected_clients()
        except Exception as e:
            # Log error untuk debugging
            self.log_message.emit(f"[ERROR] auto_refresh_status: {str(e)}")
    
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
        """Load daftar client yang terhubung dari database (persistent session tracking)"""
        if not self.database_manager:
            self.log_message.emit("[!] Database manager belum diset, skip load_connected_clients")
            return

        try:
            # Ambil data client yang terhubung dari database via API
            # GET /admin/active-sessions - Query dari tabel client_connections
            self.log_message.emit("[DEBUG] Fetching active sessions from API...")
            success, result = self.database_manager.get_active_sessions()

            self.log_message.emit(f"[DEBUG] API Response - Success: {success}, Result type: {type(result)}")

            if success:
                # Result adalah list of clients dari database.py
                # Format: [{'id_connection': N, 'client_ip': '...', 'hostname': '...', 'status': 'Terhubung', ...}, ...]
                if isinstance(result, list):
                    clients = result
                    self.log_message.emit(f"[DEBUG] Result is list with {len(clients)} items")
                    self.log_message.emit(f"[OK] Berhasil mengambil {len(clients)} data client dari API")
                elif isinstance(result, dict):
                    # Jika masih dict (legacy format), ekstrak 'data' key
                    clients = result.get('data', [])
                    self.log_message.emit(f"[DEBUG] Result is dict, extracted {len(clients)} clients from 'data' key")
                    self.log_message.emit(f"[OK] Berhasil mengambil {len(clients)} data client dari API")
                else:
                    clients = []
                    self.log_message.emit(f"[!] Format data client tidak sesuai: {type(result)}, gunakan list kosong")

                # Process clients from database
                # Tabel client_connections:
                # - client_ip, hostname, status ('Terhubung'/'Terputus')
                # - connect_time, disconnect_time, last_activity
                self.connected_clients = []

                for client in clients:
                    # Status di database: 'Terhubung' atau 'Terputus'
                    status = client.get('status', '')
                    status_lower = status.lower() if status else ''

                    self.log_message.emit(f"[DEBUG] Client: {client.get('hostname', 'Unknown')} - Status: '{status}' (lower: '{status_lower}')")

                    # Hanya tampilkan client dengan status 'Terhubung'
                    # Client yang timeout sudah di-update statusnya oleh endpoint
                    if status_lower in ['terhubung', 'connected', 'aktif', 'active']:
                        self.connected_clients.append(client)
                        self.log_message.emit(f"[DEBUG] ✓ Client {client.get('hostname')} added to connected_clients")

                # Update UI table dengan data dari database (sudah ada deduplication di update_client_table)
                self.update_client_table()

                # Hitung unique clients setelah deduplication
                unique_ids = set()
                for client in self.connected_clients:
                    conn_id = client.get('id_connection')
                    if conn_id:
                        unique_ids.add(conn_id)

                unique_count = len(unique_ids)
                self.clients_label.setText(str(unique_count))

                # Log info hanya jika ada perubahan signifikan
                if not hasattr(self, '_last_active_count') or self._last_active_count != unique_count:
                    # Log detail client yang terhubung
                    client_details = []
                    for client in self.connected_clients:
                        if client.get('id_connection') in unique_ids:
                            hostname = client.get('hostname', 'Unknown')
                            ip = client.get('client_ip', 'Unknown')
                            client_details.append(f"{hostname} ({ip})")

                    if unique_count > 0:
                        self.log_message.emit(f"[+] Client Aktif: {unique_count} - {', '.join(list(set(client_details))[:3])}")
                    else:
                        self.log_message.emit(f"[+] Client Aktif: {unique_count}")
                    self._last_active_count = unique_count

            else:
                self.connected_clients = []
                self.update_client_table()
                self.clients_label.setText("0")
                error_msg = str(result) if isinstance(result, str) else "Unknown error"
                self.log_message.emit(f"[ERROR] Gagal mengambil data dari database: {error_msg}")

        except Exception as e:
            self.connected_clients = []
            self.update_client_table()
            self.clients_label.setText("0")
            self.log_message.emit(f"[ERROR] Exception loading clients: {str(e)[:100]}")
    
    def _parse_datetime(self, dt_str):
        """Parse datetime string dari berbagai format (GMT, ISO, MySQL)"""
        if not dt_str:
            return None

        if isinstance(dt_str, datetime.datetime):
            return dt_str

        try:
            # Format GMT dari API: "Fri, 24 Oct 2025 00:49:45 GMT"
            return datetime.datetime.strptime(dt_str, '%a, %d %b %Y %H:%M:%S %Z')
        except:
            try:
                # Format ISO dengan Z: "2025-10-24T14:30:45Z"
                return datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            except:
                try:
                    # Format MySQL: "2025-10-24 14:30:45"
                    return datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                except:
                    return None

    def update_client_table(self):
        """Update tabel client yang terhubung dari database - dengan deduplication"""
        self.log_message.emit(f"[DEBUG] update_client_table called with {len(self.connected_clients)} clients")

        # Gunakan dictionary untuk deduplikasi berdasarkan id_connection
        unique_clients = {}
        for client in self.connected_clients:
            conn_id = client.get('id_connection')
            if conn_id:
                # Jika ada duplikat, ambil yang last_activity paling baru
                if conn_id not in unique_clients:
                    unique_clients[conn_id] = client
                else:
                    # Bandingkan last_activity, pilih yang lebih baru
                    existing_activity = unique_clients[conn_id].get('last_activity', '')
                    new_activity = client.get('last_activity', '')
                    if new_activity > existing_activity:
                        unique_clients[conn_id] = client

        # Convert dict ke list dan urutkan berdasarkan last_activity
        clients_list = list(unique_clients.values())
        clients_list.sort(key=lambda x: x.get('last_activity', ''), reverse=True)

        self.log_message.emit(f"[DEBUG] After deduplication: {len(clients_list)} unique clients")
        self.log_message.emit(f"[DEBUG] Setting table row count to {len(clients_list)}")

        self.client_table.setRowCount(len(clients_list))

        for i, client in enumerate(clients_list):
            # Column 0: Connection ID
            conn_id = str(client.get('id_connection', '-'))
            id_item = QTableWidgetItem(conn_id)
            id_item.setTextAlignment(Qt.AlignCenter)
            self.client_table.setItem(i, 0, id_item)

            # Column 1: Client IP
            self.client_table.setItem(i, 1, QTableWidgetItem(client.get('client_ip', 'Unknown')))

            # Column 2: Hostname
            self.client_table.setItem(i, 2, QTableWidgetItem(client.get('hostname', 'Unknown')))

            # Column 3: Waktu Koneksi
            connect_time = client.get('connect_time', '')
            connect_dt = self._parse_datetime(connect_time)
            if connect_dt:
                time_str = connect_dt.strftime('%d/%m/%Y %H:%M:%S')
            else:
                time_str = '-'
            self.client_table.setItem(i, 3, QTableWidgetItem(time_str))

            # Column 4: Terakhir Aktif (dengan durasi relatif)
            last_activity = client.get('last_activity')
            last_dt = self._parse_datetime(last_activity)
            if last_dt:
                last_active_str = last_dt.strftime('%d/%m/%Y %H:%M:%S')

                # Hitung waktu yang telah berlalu
                current_time = datetime.datetime.now()
                time_diff = current_time - last_dt.replace(tzinfo=None)

                if time_diff.total_seconds() < 60:
                    last_active_str += " (Sekarang)"
                elif time_diff.total_seconds() < 3600:
                    minutes = int(time_diff.total_seconds() / 60)
                    last_active_str += f" ({minutes}m yang lalu)"
                elif time_diff.total_seconds() < 86400:
                    hours = int(time_diff.total_seconds() / 3600)
                    last_active_str += f" ({hours}h yang lalu)"
                else:
                    days = int(time_diff.total_seconds() / 86400)
                    last_active_str += f" ({days}d yang lalu)"
            else:
                last_active_str = 'Tidak diketahui'
            self.client_table.setItem(i, 4, QTableWidgetItem(last_active_str))

            # Column 5: Status dengan color coding
            status = client.get('status', 'Unknown')
            status_item = QTableWidgetItem(status)

            status_lower = status.lower() if status else ''
            if status_lower in ['terhubung', 'connected', 'aktif', 'active']:
                status_item.setBackground(QColor(144, 238, 144))  # 🟢 Light green
                status_item.setText('Aktif')
            elif status_lower in ['terputus', 'disconnect', 'disconnected', 'offline']:
                status_item.setBackground(QColor(255, 182, 193))  # 🔴 Light red
                status_item.setText('Terputus')
            elif status_lower == 'timeout':
                status_item.setBackground(QColor(255, 165, 0, 100))  # 🟠 Light orange
                status_item.setText('Timeout')
            else:
                status_item.setBackground(QColor(255, 255, 224))  # 🟡 Light yellow
                status_item.setText(status)

            self.client_table.setItem(i, 5, status_item)

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