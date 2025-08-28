# Path: client/components/jemaat_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLabel, QPushButton, QFrame,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class JemaatClientComponent(QWidget):
    
    log_message = pyqtSignal(str)
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.jemaat_data = []
        self.filtered_data = []
        
        self.setup_ui()
        self.load_jemaat_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header info
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("Database Jemaat - Mode Client")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        
        desc_label = QLabel("Menampilkan data jemaat yang telah dibroadcast oleh admin untuk konsumsi umum")
        desc_label.setStyleSheet("color: #ecf0f1; font-size: 12px; margin-top: 5px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header_frame)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Search
        search_label = QLabel("Cari:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama jemaat...")
        self.search_input.textChanged.connect(self.filter_data)
        
        # Filter by status
        status_label = QLabel("Status:")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Semua", "Aktif", "Tidak Aktif"])
        self.status_filter.currentTextChanged.connect(self.filter_data)
        
        # Refresh button
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.clicked.connect(self.load_jemaat_data)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        
        toolbar_layout.addWidget(search_label)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(status_label)
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(refresh_button)
        
        layout.addLayout(toolbar_layout)
        
        # Table
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels([
            "Nama Lengkap", "Alamat", "Telepon", "Email", "Status", "Tanggal Bergabung"
        ])
        
        # Set column widths
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nama
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Alamat
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Telepon
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Tanggal
        
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(self.table_widget.SelectRows)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        layout.addWidget(self.table_widget)
        
        # Statistics
        self.stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total: 0 jemaat")
        self.active_label = QLabel("Aktif: 0")
        self.inactive_label = QLabel("Tidak Aktif: 0")
        
        self.stats_layout.addWidget(self.total_label)
        self.stats_layout.addWidget(self.active_label)
        self.stats_layout.addWidget(self.inactive_label)
        self.stats_layout.addStretch()
        
        layout.addLayout(self.stats_layout)
        
    def load_jemaat_data(self):
        """Load jemaat data from API (broadcast data only)"""
        try:
            result = self.api_client.get_broadcast_jemaat()  # This would be a new API endpoint
            
            if result["success"]:
                data = result.get("data", [])
                if isinstance(data, list):
                    self.jemaat_data = data
                elif isinstance(data, dict) and "data" in data:
                    self.jemaat_data = data["data"]
                else:
                    self.jemaat_data = []
                
                self.filtered_data = self.jemaat_data.copy()
                self.update_table()
                self.update_statistics()
                self.log_message.emit(f"Data jemaat berhasil dimuat: {len(self.jemaat_data)} record")
                
            else:
                error_msg = result.get("data", "Unknown error")
                QMessageBox.warning(self, "Error", f"Gagal memuat data jemaat:\\n{error_msg}")
                self.log_message.emit(f"Gagal memuat data jemaat: {error_msg}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saat memuat data jemaat:\\n{str(e)}")
            self.log_message.emit(f"Error memuat data jemaat: {str(e)}")
    
    def update_table(self):
        """Update table with filtered data"""
        self.table_widget.setRowCount(len(self.filtered_data))
        
        for row, jemaat in enumerate(self.filtered_data):
            # Nama Lengkap
            nama = jemaat.get('nama_lengkap', '') or jemaat.get('nama', '') or 'N/A'
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(nama)))
            
            # Alamat
            alamat = jemaat.get('alamat', '') or 'N/A'
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(alamat)))
            
            # Telepon
            telepon = jemaat.get('telepon', '') or jemaat.get('no_hp', '') or 'N/A'
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(telepon)))
            
            # Email
            email = jemaat.get('email', '') or 'N/A'
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(email)))
            
            # Status
            status = jemaat.get('status', '') or jemaat.get('status_aktif', '') or 'Unknown'
            status_item = QTableWidgetItem(str(status))
            if status.lower() == 'aktif':
                status_item.setBackground(Qt.green)
            elif status.lower() == 'tidak aktif':
                status_item.setBackground(Qt.red)
            self.table_widget.setItem(row, 4, status_item)
            
            # Tanggal Bergabung
            tanggal = jemaat.get('tanggal_bergabung', '') or jemaat.get('created_at', '') or 'N/A'
            if tanggal and tanggal != 'N/A':
                try:
                    from datetime import datetime
                    if 'T' in tanggal:
                        dt = datetime.fromisoformat(tanggal.replace('Z', '+00:00'))
                        tanggal = dt.strftime('%d/%m/%Y')
                except:
                    pass
            self.table_widget.setItem(row, 5, QTableWidgetItem(str(tanggal)))
    
    def filter_data(self):
        """Filter data based on search and status filter"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()
        
        self.filtered_data = []
        
        for jemaat in self.jemaat_data:
            # Search filter
            nama = (jemaat.get('nama_lengkap', '') or jemaat.get('nama', '')).lower()
            alamat = jemaat.get('alamat', '').lower()
            
            if search_text and search_text not in nama and search_text not in alamat:
                continue
            
            # Status filter
            status = jemaat.get('status', '') or jemaat.get('status_aktif', '')
            if status_filter != "Semua":
                if status_filter == "Aktif" and status.lower() != "aktif":
                    continue
                elif status_filter == "Tidak Aktif" and status.lower() != "tidak aktif":
                    continue
            
            self.filtered_data.append(jemaat)
        
        self.update_table()
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics labels"""
        total = len(self.filtered_data)
        aktif = len([j for j in self.filtered_data if (j.get('status', '') or j.get('status_aktif', '')).lower() == 'aktif'])
        tidak_aktif = total - aktif
        
        self.total_label.setText(f"Total: {total} jemaat")
        self.active_label.setText(f"Aktif: {aktif}")
        self.inactive_label.setText(f"Tidak Aktif: {tidak_aktif}")
        
        # Style the labels
        self.total_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.active_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.inactive_label.setStyleSheet("color: #e74c3c; font-weight: bold;")