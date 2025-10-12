#!/usr/bin/env python
# -- coding: utf-8 --
# Path: src/client/client_http.py

import sys
import os
import socket
import threading
import time
import traceback
import requests
import json
from typing import Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QPushButton, QTextEdit,
                            QStatusBar, QMessageBox, QLineEdit, QFormLayout,
                            QGroupBox, QSpinBox, QFileDialog, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

# Konstanta koneksi default
DEFAULT_HOST = '100.88.2.70'  # Tailscale IP server atau alamat IP normal
DEFAULT_PORT = 9000

class ClientThread(QThread):
    """Thread untuk mengelola koneksi client ke server HTTP"""
    connected = pyqtSignal(bool, str)  # Status koneksi (berhasil/gagal, pesan)
    message_received = pyqtSignal(str)  # Menerima pesan dari server
    disconnected = pyqtSignal(str)      # Terputus dari server (dengan alasan)
    
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}/api"
        self.connected_flag = False
        self.running = False
        self.last_message_id = 0
        self.session = requests.Session()  # Menggunakan session untuk performa lebih baik
    
    def run(self):
        """Menjalankan koneksi HTTP"""
        try:
            # Kirim pesan ke UI bahwa sedang mencoba koneksi
            self.connected.emit(False, f"Mencoba koneksi ke {self.host}:{self.port}...")
            
            # Coba koneksi dengan mengirim hostname
            hostname = socket.gethostname()
            response = self.session.post(
                f"{self.base_url}/connect",
                json={'hostname': hostname},
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                # Set flag dan emit signal
                self.connected_flag = True
                self.running = True
                self.connected.emit(True, f"Terhubung ke server {self.host}:{self.port}")
                
                # Proses pesan tertunda jika ada
                if 'pending_messages' in data and data['pending_messages']:
                    for msg in data['pending_messages']:
                        if msg['type'] == 'broadcast' or msg.get('target') == socket.gethostbyname(socket.gethostname()):
                            self.message_received.emit(msg['message'])
                
                # Loop untuk polling pesan baru dan heartbeat
                while self.running:
                    try:
                        # Polling pesan baru
                        self._poll_messages()
                        
                        # Heartbeat setiap 30 detik
                        self._send_heartbeat()
                        
                        # Sleep agar tidak terlalu banyak request
                        time.sleep(2)
                    except requests.RequestException as e:
                        # Mungkin server sedang down, coba lagi
                        self.message_received.emit(f"Kesalahan koneksi: {str(e)}")
                        time.sleep(5)  # Tunggu lebih lama sebelum retry
                    except Exception as e:
                        if self.running:  # Hanya log error jika masih running
                            error_msg = f"Error dalam loop komunikasi: {str(e)}"
                            self.disconnected.emit(error_msg)
                            self.running = False
                            self.connected_flag = False
                        break
            else:
                # Koneksi gagal
                error_msg = f"Server menolak koneksi dengan kode: {response.status_code}"
                self.connected_flag = False
                self.running = False
                self.connected.emit(False, error_msg)
                
        except requests.Timeout:
            # Timeout saat koneksi
            self.connected_flag = False
            self.running = False
            self.connected.emit(False, f"Timeout koneksi ke server: {self.host}:{self.port}. Pastikan server berjalan dan alamat benar.")
        except requests.ConnectionError as e:
            # Error koneksi (seperti connection refused)
            self.connected_flag = False
            self.running = False
            error_msg = f"Gagal terhubung ke server: {str(e)}"
            self.connected.emit(False, error_msg)
        except Exception as e:
            # Error lainnya
            self.connected_flag = False
            self.running = False
            error_detail = traceback.format_exc()
            self.connected.emit(False, f"Gagal terhubung ke server: {str(e)}\n\nDetail: {error_detail}")
    
    def _poll_messages(self):
        """Polling pesan dari server"""
        try:
            response = self.session.get(
                f"{self.base_url}/messages",
                params={'last_id': self.last_message_id},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    self.last_message_id = data.get('last_id', self.last_message_id)
                    
                    # Proses pesan baru
                    client_ip = socket.gethostbyname(socket.gethostname())
                    for msg in data.get('messages', []):
                        # Proses pesan broadcast atau pesan yang ditujukan ke client ini
                        if msg['type'] == 'broadcast' or msg.get('target') == client_ip:
                            self.message_received.emit(msg['message'])
        except Exception as e:
            if self.running:
                self.message_received.emit(f"Error saat polling pesan: {str(e)}")
    
    def _send_heartbeat(self):
        """Kirim heartbeat ke server"""
        try:
            response = self.session.post(
                f"{self.base_url}/heartbeat",
                timeout=5
            )
            # Tidak perlu proses response
        except Exception:
            # Abaikan error heartbeat, akan dicoba lagi nanti
            pass
    
    def send_message(self, message):
        """Mengirim pesan ke server"""
        if not self.connected_flag:
            return False
        
        try:
            response = self.session.post(
                f"{self.base_url}/message",
                json={'message': message},
                timeout=5
            )
            
            return response.status_code == 200
        except Exception as e:
            self.disconnected.emit(f"Error saat mengirim pesan: {str(e)}")
            self.running = False
            self.connected_flag = False
            return False
    
    def upload_file(self, filepath):
        """Mengirim file ke server"""
        if not self.connected_flag:
            return False, "Tidak terhubung ke server"
        
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (os.path.basename(filepath), f)}
                response = self.session.post(
                    f"{self.base_url}/upload",
                    files=files,
                    timeout=60  # Timeout lebih lama untuk upload file
                )
            
            if response.status_code == 200:
                return True, "File berhasil diupload"
            else:
                return False, f"Gagal upload file: {response.text}"
        except Exception as e:
            error_msg = f"Error saat upload file: {str(e)}"
            return False, error_msg
    
    def disconnect(self):
        """Memutuskan koneksi dari server"""
        if self.connected_flag:
            try:
                # Kirim notifikasi disconnect ke server
                self.session.post(
                    f"{self.base_url}/disconnect",
                    timeout=5
                )
            except:
                pass  # Abaikan error saat disconnect
        
        self.running = False
        self.connected_flag = False


class ClientWindow(QMainWindow):
    """Jendela utama aplikasi client"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client Gereja Katolik")
        self.setMinimumSize(800, 600)

        # Initialize client thread with type annotation
        self.client_thread: Optional[ClientThread] = None

        # Initialize status bar early with type annotation
        self.statusBar: QStatusBar = QStatusBar()

        # Setup UI
        self.setup_ui()

        # Set status bar
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Belum terhubung ke server")
    
    def setup_ui(self):
        """Setup antarmuka pengguna"""
        # Widget utama dan layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Bagian koneksi server
        connection_group = QGroupBox("Koneksi Server")
        connection_layout = QHBoxLayout()
        
        # Form koneksi
        form_layout = QFormLayout()
        self.host_input = QLineEdit(DEFAULT_HOST)
        self.port_input = QSpinBox()
        self.port_input.setRange(1000, 65535)
        self.port_input.setValue(DEFAULT_PORT)
        
        form_layout.addRow("Host:", self.host_input)
        form_layout.addRow("Port:", self.port_input)
        connection_layout.addLayout(form_layout)
        
        # Tombol koneksi
        button_layout = QVBoxLayout()
        self.connect_button = QPushButton("Hubungkan")
        self.connect_button.clicked.connect(self.connect_to_server)
        self.disconnect_button = QPushButton("Putuskan")
        self.disconnect_button.clicked.connect(self.disconnect_from_server)
        self.disconnect_button.setEnabled(False)
        
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)
        button_layout.addStretch()
        connection_layout.addLayout(button_layout)
        
        # Status koneksi
        status_layout = QVBoxLayout()
        self.connection_status = QLabel("Status: Tidak Terhubung")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.connection_status)
        status_layout.addStretch()
        connection_layout.addLayout(status_layout)
        
        connection_group.setLayout(connection_layout)
        main_layout.addWidget(connection_group)
        
        # Area komunikasi
        communication_group = QGroupBox("Komunikasi Server")
        communication_layout = QVBoxLayout()
        
        # Log komunikasi
        self.communication_log = QTextEdit()
        self.communication_log.setReadOnly(True)
        self.communication_log.setFont(QFont("Courier New", 10))
        communication_layout.addWidget(QLabel("Log Komunikasi:"))
        communication_layout.addWidget(self.communication_log)
        
        # Pengiriman pesan
        message_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ketik pesan...")
        self.message_input.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Kirim")
        self.send_button.clicked.connect(self.send_message)
        
        message_layout.addWidget(self.message_input)
        message_layout.addWidget(self.send_button)
        
        communication_layout.addLayout(message_layout)
        
        # Upload file
        upload_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)
        upload_layout.addWidget(self.upload_button)
        
        self.file_progress = QProgressBar()
        self.file_progress.setVisible(False)
        upload_layout.addWidget(self.file_progress)
        
        communication_layout.addLayout(upload_layout)
        
        # Tombol clear log
        clear_layout = QHBoxLayout()
        self.clear_log_button = QPushButton("Bersihkan Log")
        self.clear_log_button.clicked.connect(self.clear_log)
        clear_layout.addStretch()
        clear_layout.addWidget(self.clear_log_button)
        
        communication_layout.addLayout(clear_layout)
        
        communication_group.setLayout(communication_layout)
        main_layout.addWidget(communication_group)
        
        # Toggle enable/disable komponen komunikasi
        self.set_communication_enabled(False)
    
    def connect_to_server(self):
        """Menghubungkan ke server"""
        if self.client_thread and self.client_thread.connected_flag:
            self.log_message("Sudah terhubung ke server!")
            return
        
        host = self.host_input.text().strip()
        port = self.port_input.value()
        
        # Validasi input
        if not host:
            QMessageBox.warning(self, "Error", "Host tidak boleh kosong")
            return
        
        # Update UI
        self.connect_button.setEnabled(False)
        self.host_input.setEnabled(False)
        self.port_input.setEnabled(False)
        self.statusBar.showMessage(f"Menghubungkan ke {host}:{port}...")
        self.log_message(f"Mencoba terhubung ke server {host}:{port}...")
        
        # Buat thread koneksi
        self.client_thread = ClientThread(host, port)
        self.client_thread.connected.connect(self.handle_connection)
        self.client_thread.message_received.connect(self.handle_message)
        self.client_thread.disconnected.connect(self.handle_disconnection)
        
        # Mulai thread
        self.client_thread.start()
    
    def handle_connection(self, success, message):
        """Menangani hasil koneksi"""
        if success:
            # Koneksi berhasil
            self.connection_status.setText("Status: Terhubung")
            self.connection_status.setStyleSheet("color: green; font-weight: bold;")
            self.disconnect_button.setEnabled(True)
            self.set_communication_enabled(True)
            self.statusBar.showMessage("Terhubung ke server")
        else:
            # Koneksi gagal
            self.connection_status.setText("Status: Gagal Terhubung")
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")
            self.connect_button.setEnabled(True)
            self.host_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.statusBar.showMessage("Gagal terhubung ke server")
        
        self.log_message(message)
    
    def handle_message(self, message):
        """Menangani pesan dari server"""
        self.log_message(f"[Server]: {message}")
    
    def handle_disconnection(self, reason):
        """Menangani pemutusan koneksi"""
        self.connection_status.setText("Status: Terputus")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.host_input.setEnabled(True)
        self.port_input.setEnabled(True)
        self.set_communication_enabled(False)
        self.statusBar.showMessage("Terputus dari server")
        
        self.log_message(f"Terputus dari server: {reason}")
    
    def disconnect_from_server(self):
        """Memutuskan koneksi dari server"""
        if self.client_thread and self.client_thread.isRunning():
            self.client_thread.disconnect()
            self.client_thread.wait()  # Tunggu thread berhenti
            
            self.connection_status.setText("Status: Terputus (Manual)")
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.host_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.set_communication_enabled(False)
            self.statusBar.showMessage("Terputus dari server")
            
            self.log_message("Terputus dari server (Diputus secara manual)")
    
    def send_message(self):
        """Mengirim pesan ke server"""
        if not self.client_thread or not self.client_thread.connected_flag:
            self.log_message("Tidak dapat mengirim pesan: Tidak terhubung ke server")
            return
        
        message = self.message_input.text().strip()
        if not message:
            return
        
        success = self.client_thread.send_message(message)
        if success:
            self.log_message(f"[Saya]: {message}")
            self.message_input.clear()
        else:
            self.log_message("Gagal mengirim pesan")
    
    def upload_file(self):
        """Upload file ke server"""
        if not self.client_thread or not self.client_thread.connected_flag:
            self.log_message("Tidak dapat upload file: Tidak terhubung ke server")
            return
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Pilih File untuk Upload", "", "Semua File (.)"
        )
        
        if not filepath:
            return  # User membatalkan dialog
        
        self.log_message(f"Memulai upload file: {os.path.basename(filepath)}")
        self.file_progress.setVisible(True)
        self.file_progress.setValue(0)
        
        # Upload file di thread terpisah
        upload_thread = threading.Thread(
            target=self._upload_file_thread,
            args=(filepath,)
        )
        upload_thread.daemon = True
        upload_thread.start()
    
    def _upload_file_thread(self, filepath):
        """Thread untuk upload file"""
        try:
            # Simulasi progress (tidak ada cara langsung untuk mendapatkan progress dari requests)
            for i in range(1, 101, 10):
                time.sleep(0.2)  # Delay untuk simulasi
                # Update UI dari thread utama
                app = QApplication.instance()
                app.processEvents()
                self.file_progress.setValue(i)

            # Sebenarnya upload file
            if self.client_thread is None:
                self.log_message("Error: Client thread tidak tersedia")
                self.file_progress.setVisible(False)
                return

            success, message = self.client_thread.upload_file(filepath)
            
            # Update UI
            self.file_progress.setValue(100 if success else 0)
            self.log_message(message)
            
            # Sembunyikan progress bar setelah beberapa detik
            time.sleep(2)
            self.file_progress.setVisible(False)
        except Exception as e:
            self.log_message(f"Error saat upload file: {str(e)}")
            self.file_progress.setVisible(False)
    
    def set_communication_enabled(self, enabled):
        """Mengatur status aktif/nonaktif komponen komunikasi"""
        self.message_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.upload_button.setEnabled(enabled)
    
    def log_message(self, message):
        """Menambahkan pesan ke log komunikasi"""
        timestamp = time.strftime("%H:%M:%S")
        self.communication_log.append(f"[{timestamp}] {message}")
    
    def clear_log(self):
        """Bersihkan log komunikasi"""
        self.communication_log.clear()
        self.log_message("Log dibersihkan")
    
    def closeEvent(self, event):
        """Handle saat jendela ditutup"""
        if self.client_thread and self.client_thread.connected_flag:
            reply = QMessageBox.question(self, 'Konfirmasi',
                                        "Masih terhubung ke server. Yakin ingin keluar?",
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.disconnect_from_server()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set style
    app.setStyle("Fusion")
    
    window = ClientWindow()
    window.show()
    
    sys.exit(app.exec_())