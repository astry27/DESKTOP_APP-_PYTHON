# Path: server/components/server_control.py

import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QFormLayout, QPushButton, QLabel, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QTextEdit, QMessageBox, 
                            QInputDialog, QFileDialog)
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QIcon

class ServerControlComponent(QWidget):
    
    log_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.database_manager = None
        self.connected_clients = []
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
        
        control_group = self.create_control_panel()
        layout.addWidget(control_group)
    
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
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
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
        self.client_table = QTableWidget(0, 4)
        self.client_table.setHorizontalHeaderLabels(["IP Address", "Hostname", "Waktu Koneksi", "Status"])
        self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        client_layout.addWidget(self.client_table)
        
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
        """Load daftar client yang terhubung melalui API"""
        if not self.database_manager:
            return
        
        try:
            # Ambil data client yang terhubung dari API
            success, clients = self.database_manager.get_active_sessions()
            
            if success:
                self.connected_clients = clients
                self.update_client_table()
                self.clients_label.setText(str(len(clients)))
            else:
                self.connected_clients = []
                self.update_client_table()
                self.clients_label.setText("0")
        except Exception as e:
            self.log_message.emit(f"Error loading clients: {str(e)}")
    
    def update_client_table(self):
        """Update tabel client yang terhubung"""
        self.client_table.setRowCount(len(self.connected_clients))
        
        for i, client in enumerate(self.connected_clients):
            self.client_table.setItem(i, 0, QTableWidgetItem(client.get('client_ip', '')))
            self.client_table.setItem(i, 1, QTableWidgetItem(client.get('hostname', '')))
            
            connect_time = client.get('connect_time', '')
            if connect_time:
                if isinstance(connect_time, str):
                    try:
                        dt = datetime.datetime.fromisoformat(connect_time.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M:%S')
                    except:
                        time_str = str(connect_time)
                else:
                    time_str = str(connect_time)
            else:
                time_str = '-'
            
            self.client_table.setItem(i, 2, QTableWidgetItem(time_str))
            
            status = client.get('status', 'Unknown')
            status_item = QTableWidgetItem(status)
            if status == 'Terhubung':
                status_item.setBackground(QColor(200, 255, 200))
            else:
                status_item.setBackground(QColor(255, 200, 200))
            
            self.client_table.setItem(i, 3, status_item)
    
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