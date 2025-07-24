# Path: client/components/pengumuman_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QTextBrowser, 
                             QMessageBox, QSplitter, QLabel, QHBoxLayout, QPushButton,
                             QTabWidget, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor

class PengumumanComponent(QWidget):
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.pengumuman_data = []
        self.broadcast_messages = []
        self.init_ui()
        self.load_pengumuman()
        self.setup_timer()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Tab widget untuk pengumuman dan broadcast
        self.tab_widget = QTabWidget()
        
        # Tab Pengumuman Resmi
        pengumuman_tab = self.create_pengumuman_tab()
        self.tab_widget.addTab(pengumuman_tab, "Pengumuman Resmi")
        
        # Tab Broadcast Messages
        broadcast_tab = self.create_broadcast_tab()
        self.tab_widget.addTab(broadcast_tab, "Pesan Broadcast")
        
        layout.addWidget(self.tab_widget)
    
    def create_pengumuman_tab(self):
        """Tab untuk pengumuman resmi dari database"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        splitter = QSplitter(Qt.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        list_header = QHBoxLayout()
        list_header.addWidget(QLabel("Daftar Pengumuman Resmi"))
        list_header.addStretch()
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_pengumuman)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        list_header.addWidget(refresh_button)
        
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.display_pengumuman)
        
        left_layout.addLayout(list_header)
        left_layout.addWidget(self.list_widget)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("Detail Pengumuman"))
        self.detail_browser = QTextBrowser()
        right_layout.addWidget(self.detail_browser)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        return tab_widget
    
    def create_broadcast_tab(self):
        """Tab untuk pesan broadcast dari admin"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Pesan Broadcast dari Admin"))
        header_layout.addStretch()
        
        refresh_broadcast_btn = QPushButton("Refresh")
        refresh_broadcast_btn.clicked.connect(self.load_broadcast_messages)
        refresh_broadcast_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        header_layout.addWidget(refresh_broadcast_btn)
        
        layout.addLayout(header_layout)
        
        # Splitter untuk list dan detail broadcast
        broadcast_splitter = QSplitter(Qt.Horizontal)
        
        # List broadcast messages
        broadcast_left = QWidget()
        broadcast_left_layout = QVBoxLayout(broadcast_left)
        
        self.broadcast_list = QListWidget()
        self.broadcast_list.currentRowChanged.connect(self.display_broadcast_message)
        broadcast_left_layout.addWidget(self.broadcast_list)
        
        # Detail broadcast message
        broadcast_right = QWidget()
        broadcast_right_layout = QVBoxLayout(broadcast_right)
        broadcast_right_layout.addWidget(QLabel("Detail Pesan"))
        
        self.broadcast_detail = QTextBrowser()
        broadcast_right_layout.addWidget(self.broadcast_detail)
        
        broadcast_splitter.addWidget(broadcast_left)
        broadcast_splitter.addWidget(broadcast_right)
        broadcast_splitter.setSizes([300, 500])
        
        layout.addWidget(broadcast_splitter)
        
        # Status update
        self.broadcast_status = QLabel("Siap menerima pesan broadcast...")
        self.broadcast_status.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(self.broadcast_status)
        
        return tab_widget
    
    def setup_timer(self):
        """Setup timer untuk auto refresh broadcast messages"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_refresh_broadcast)
        self.timer.start(10000)  # Refresh setiap 10 detik

    def load_pengumuman(self):
        """Load pengumuman resmi dari API"""
        self.list_widget.clear()
        self.detail_browser.clear()
        self.list_widget.addItem("Memuat data pengumuman...")
        
        result = self.api_client.get_pengumuman()
        self.on_pengumuman_loaded(result["success"], result["data"])

    def on_pengumuman_loaded(self, success, data):
        """Handler ketika pengumuman berhasil dimuat"""
        self.list_widget.clear()
        if success:
            if data.get("status") == "success":
                self.pengumuman_data = data.get("data", [])
                if not self.pengumuman_data:
                    self.list_widget.addItem("Tidak ada pengumuman aktif.")
                else:
                    for item in self.pengumuman_data:
                        title = item.get('judul', 'Tanpa Judul')
                        # Add priority indicator
                        priority = item.get('prioritas', 'Normal')
                        if priority == 'Urgent':
                            title = f"[URGENT] {title}"
                        elif priority == 'Tinggi':
                            title = f"[PENTING] {title}"
                        
                        self.list_widget.addItem(title)
            else:
                self.list_widget.addItem("Gagal memuat data.")
                QMessageBox.warning(self, "Error", f"API Error: {data.get('message', 'Unknown error')}")
        else:
            self.list_widget.addItem("Gagal memuat data.")
            QMessageBox.warning(self, "Error", f"Tidak dapat memuat pengumuman: {data}")

    def display_pengumuman(self, index):
        """Tampilkan detail pengumuman yang dipilih"""
        if 0 <= index < len(self.pengumuman_data):
            item = self.pengumuman_data[index]
            
            # Format tanggal
            tanggal_mulai = item.get('tanggal_mulai', 'N/A')
            tanggal_selesai = item.get('tanggal_selesai', 'N/A')
            
            html = f"""
            <div style="font-family: Arial, sans-serif;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                    {item.get('judul', 'Tanpa Judul')}
                </h2>
                
                <div style="background-color: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px;">
                    <p><strong>Kategori:</strong> {item.get('kategori', 'N/A')}</p>
                    <p><strong>Prioritas:</strong> <span style="color: #e74c3c; font-weight: bold;">{item.get('prioritas', 'N/A')}</span></p>
                    <p><strong>Periode:</strong> {tanggal_mulai} sampai {tanggal_selesai}</p>
                </div>
                
                <div style="line-height: 1.6; margin-top: 15px;">
                    {item.get('isi', 'Tidak ada konten.')}
                </div>
            </div>
            """
            self.detail_browser.setHtml(html)
    
    def load_broadcast_messages(self):
        """Load pesan broadcast dari admin"""
        self.broadcast_status.setText("Memuat pesan broadcast...")
        
        result = self.api_client.get_broadcast_messages(limit=50)
        if result["success"]:
            data = result["data"]
            if data.get("status") == "success":
                self.broadcast_messages = data.get("data", [])
                self.update_broadcast_list()
                self.broadcast_status.setText(f"Ditemukan {len(self.broadcast_messages)} pesan broadcast")
            else:
                self.broadcast_status.setText("Gagal memuat pesan broadcast")
                QMessageBox.warning(self, "Error", f"Gagal memuat broadcast: {data.get('message', 'Unknown error')}")
        else:
            self.broadcast_status.setText("Error koneksi ke server")
            QMessageBox.warning(self, "Error", f"Error koneksi: {result['data']}")
    
    def update_broadcast_list(self):
        """Update list pesan broadcast"""
        self.broadcast_list.clear()
        
        if not self.broadcast_messages:
            self.broadcast_list.addItem("Tidak ada pesan broadcast")
            return
        
        for i, message in enumerate(self.broadcast_messages):
            # Format waktu
            waktu_kirim = message.get('waktu_kirim', '')
            try:
                if waktu_kirim:
                    import datetime
                    if isinstance(waktu_kirim, str):
                        dt = datetime.datetime.fromisoformat(waktu_kirim.replace('Z', '+00:00'))
                        waktu_str = dt.strftime('%d/%m %H:%M')
                    else:
                        waktu_str = str(waktu_kirim)
                else:
                    waktu_str = "Unknown"
            except:
                waktu_str = str(waktu_kirim)
            
            # Format pesan untuk list (potong jika terlalu panjang)
            pesan = message.get('pesan', 'No message')
            if len(pesan) > 50:
                pesan_short = pesan[:50] + "..."
            else:
                pesan_short = pesan
            
            pengirim = message.get('pengirim_nama', 'Admin')
            
            list_text = f"[{waktu_str}] {pengirim}: {pesan_short}"
            self.broadcast_list.addItem(list_text)
    
    def display_broadcast_message(self, index):
        """Tampilkan detail pesan broadcast yang dipilih"""
        if 0 <= index < len(self.broadcast_messages):
            message = self.broadcast_messages[index]
            
            # Format waktu
            waktu_kirim = message.get('waktu_kirim', '')
            try:
                if waktu_kirim:
                    import datetime
                    if isinstance(waktu_kirim, str):
                        dt = datetime.datetime.fromisoformat(waktu_kirim.replace('Z', '+00:00'))
                        waktu_str = dt.strftime('%d/%m/%Y %H:%M:%S')
                    else:
                        waktu_str = str(waktu_kirim)
                else:
                    waktu_str = "Unknown"
            except:
                waktu_str = str(waktu_kirim)
            
            html = f"""
            <div style="font-family: Arial, sans-serif;">
                <div style="background-color: #3498db; color: white; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: white;">Pesan Broadcast dari Admin</h3>
                </div>
                
                <div style="background-color: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px;">
                    <p><strong>Pengirim:</strong> {message.get('pengirim_nama', 'Admin')}</p>
                    <p><strong>Waktu:</strong> {waktu_str}</p>
                    <p><strong>Status:</strong> {message.get('status', 'N/A')}</p>
                </div>
                
                <div style="background-color: #fff; padding: 15px; border-left: 4px solid #3498db; margin-top: 15px;">
                    <h4 style="color: #2c3e50; margin-top: 0;">Isi Pesan:</h4>
                    <p style="line-height: 1.6; font-size: 14px;">
                        {message.get('pesan', 'No message content')}
                    </p>
                </div>
            </div>
            """
            self.broadcast_detail.setHtml(html)
    
    def auto_refresh_broadcast(self):
        """Auto refresh pesan broadcast"""
        if self.tab_widget.currentIndex() == 1:  # Jika sedang di tab broadcast
            old_count = len(self.broadcast_messages)
            
            result = self.api_client.get_broadcast_messages(limit=50)
            if result["success"]:
                data = result["data"]
                if data.get("status") == "success":
                    new_messages = data.get("data", [])
                    
                    if len(new_messages) > old_count:
                        # Ada pesan baru
                        self.broadcast_messages = new_messages
                        self.update_broadcast_list()
                        self.broadcast_status.setText(f"Pesan baru diterima! Total: {len(self.broadcast_messages)} pesan")
                        self.broadcast_status.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
                        
                        # Reset style setelah 3 detik
                        QTimer.singleShot(3000, self.reset_status_style)
                    elif len(new_messages) != old_count:
                        # Update list jika ada perubahan
                        self.broadcast_messages = new_messages
                        self.update_broadcast_list()
                        self.broadcast_status.setText(f"Total: {len(self.broadcast_messages)} pesan broadcast")
    
    def reset_status_style(self):
        """Reset style status label"""
        self.broadcast_status.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        self.broadcast_status.setText(f"Total: {len(self.broadcast_messages)} pesan broadcast")