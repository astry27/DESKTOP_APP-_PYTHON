# Path: client/components/jadwal_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLabel, QPushButton, QFrame,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox,
                             QCalendarWidget, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor

class JadwalClientComponent(QWidget):
    
    log_message = pyqtSignal(str)
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.kegiatan_data = []
        self.filtered_data = []
        
        self.setup_ui()
        self.load_kegiatan_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header info
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #9b59b6;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("Jadwal Kegiatan Gereja - Mode Client")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        
        desc_label = QLabel("Menampilkan jadwal kegiatan gereja yang telah dibroadcast oleh admin")
        desc_label.setStyleSheet("color: #ecf0f1; font-size: 12px; margin-top: 5px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header_frame)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Calendar and controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        # Calendar
        calendar_label = QLabel("Kalender Kegiatan")
        calendar_label.setFont(QFont("Arial", 12, QFont.Bold))
        calendar_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        left_layout.addWidget(calendar_label)
        
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QCalendarWidget QTableView {
                selection-background-color: #3498db;
            }
        """)
        self.calendar.clicked.connect(self.calendar_date_changed)
        left_layout.addWidget(self.calendar)
        
        # Filters
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        filter_layout = QVBoxLayout(filter_frame)
        
        filter_label = QLabel("Filter Kegiatan")
        filter_label.setFont(QFont("Arial", 12, QFont.Bold))
        filter_layout.addWidget(filter_label)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari kegiatan...")
        self.search_input.textChanged.connect(self.filter_data)
        filter_layout.addWidget(QLabel("Cari:"))
        filter_layout.addWidget(self.search_input)
        
        # Category filter
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "Semua", "Ibadah", "Doa", "Katekese", "Sosial", 
            "Rohani", "Administratif", "Lainnya"
        ])
        self.category_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(QLabel("Kategori:"))
        filter_layout.addWidget(self.category_filter)
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Semua", "Akan Datang", "Sedang Berlangsung", "Selesai"])
        self.status_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        
        # Refresh button
        refresh_button = QPushButton("🔄 Refresh Data")
        refresh_button.clicked.connect(self.load_kegiatan_data)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        filter_layout.addWidget(refresh_button)
        
        left_layout.addWidget(filter_frame)
        left_layout.addStretch()
        
        # Right panel - Schedule table and details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Schedule table
        table_label = QLabel("Daftar Kegiatan")
        table_label.setFont(QFont("Arial", 12, QFont.Bold))
        table_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        right_layout.addWidget(table_label)
        
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels([
            "Nama Kegiatan", "Tanggal", "Waktu", "Tempat", "Kategori", "Status"
        ])
        
        # Set column widths
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nama
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Tanggal
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Waktu
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Tempat
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Kategori
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status
        
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(self.table_widget.SelectRows)
        self.table_widget.itemSelectionChanged.connect(self.show_kegiatan_detail)
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
                background-color: #9b59b6;
                color: white;
            }
        """)
        
        right_layout.addWidget(self.table_widget)
        
        # Detail panel
        detail_label = QLabel("Detail Kegiatan")
        detail_label.setFont(QFont("Arial", 12, QFont.Bold))
        detail_label.setStyleSheet("color: #2c3e50; margin: 10px 0px 5px 0px;")
        right_layout.addWidget(detail_label)
        
        self.detail_text = QTextEdit()
        self.detail_text.setMaximumHeight(150)
        self.detail_text.setReadOnly(True)
        self.detail_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        self.detail_text.setText("Pilih kegiatan untuk melihat detail...")
        right_layout.addWidget(self.detail_text)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 650])
        
        layout.addWidget(splitter)
        
        # Statistics
        self.stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total: 0 kegiatan")
        self.upcoming_label = QLabel("Akan Datang: 0")
        self.today_label = QLabel("Hari Ini: 0")
        
        self.stats_layout.addWidget(self.total_label)
        self.stats_layout.addWidget(self.upcoming_label)
        self.stats_layout.addWidget(self.today_label)
        self.stats_layout.addStretch()
        
        layout.addLayout(self.stats_layout)
        
    def load_kegiatan_data(self):
        """Load kegiatan data from API (broadcast data only)"""
        try:
            result = self.api_client.get_broadcast_kegiatan()  # This would be a new API endpoint
            
            if result["success"]:
                data = result.get("data", [])
                if isinstance(data, list):
                    self.kegiatan_data = data
                elif isinstance(data, dict) and "data" in data:
                    self.kegiatan_data = data["data"]
                else:
                    self.kegiatan_data = []
                
                self.filtered_data = self.kegiatan_data.copy()
                self.update_table()
                self.update_statistics()
                self.highlight_calendar_dates()
                self.log_message.emit(f"Data kegiatan berhasil dimuat: {len(self.kegiatan_data)} record")
                
            else:
                error_msg = result.get("data", "Unknown error")
                QMessageBox.warning(self, "Error", f"Gagal memuat data kegiatan:\\n{error_msg}")
                self.log_message.emit(f"Gagal memuat data kegiatan: {error_msg}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saat memuat data kegiatan:\\n{str(e)}")
            self.log_message.emit(f"Error memuat data kegiatan: {str(e)}")
    
    def update_table(self):
        """Update table with filtered data"""
        self.table_widget.setRowCount(len(self.filtered_data))
        
        for row, kegiatan in enumerate(self.filtered_data):
            # Nama Kegiatan
            nama = kegiatan.get('nama_kegiatan', '') or kegiatan.get('judul', '') or 'N/A'
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(nama)))
            
            # Tanggal
            tanggal = kegiatan.get('tanggal', '') or kegiatan.get('tanggal_kegiatan', '') or 'N/A'
            if tanggal and tanggal != 'N/A':
                try:
                    from datetime import datetime
                    if 'T' in tanggal:
                        dt = datetime.fromisoformat(tanggal.replace('Z', '+00:00'))
                        tanggal = dt.strftime('%d/%m/%Y')
                except:
                    pass
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(tanggal)))
            
            # Waktu
            waktu = kegiatan.get('waktu', '') or kegiatan.get('jam', '') or 'N/A'
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(waktu)))
            
            # Tempat
            tempat = kegiatan.get('tempat', '') or kegiatan.get('lokasi', '') or 'N/A'
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(tempat)))
            
            # Kategori
            kategori = kegiatan.get('kategori', '') or kegiatan.get('jenis', '') or 'Lainnya'
            self.table_widget.setItem(row, 4, QTableWidgetItem(str(kategori)))
            
            # Status
            status = self.get_kegiatan_status(kegiatan)
            status_item = QTableWidgetItem(status)
            
            # Color code status
            if status == "Akan Datang":
                status_item.setBackground(QColor("#3498db"))
                status_item.setForeground(QColor("white"))
            elif status == "Sedang Berlangsung":
                status_item.setBackground(QColor("#f39c12"))
                status_item.setForeground(QColor("white"))
            elif status == "Selesai":
                status_item.setBackground(QColor("#95a5a6"))
                status_item.setForeground(QColor("white"))
            
            self.table_widget.setItem(row, 5, status_item)
    
    def get_kegiatan_status(self, kegiatan):
        """Determine status of kegiatan based on date/time"""
        try:
            from datetime import datetime, date
            today = date.today()
            
            tanggal_str = kegiatan.get('tanggal', '') or kegiatan.get('tanggal_kegiatan', '')
            if not tanggal_str:
                return "Unknown"
            
            if 'T' in tanggal_str:
                kegiatan_date = datetime.fromisoformat(tanggal_str.replace('Z', '+00:00')).date()
            else:
                kegiatan_date = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
            
            if kegiatan_date > today:
                return "Akan Datang"
            elif kegiatan_date == today:
                return "Sedang Berlangsung"
            else:
                return "Selesai"
        except:
            return "Unknown"
    
    def filter_data(self):
        """Filter data based on search, category, and status"""
        search_text = self.search_input.text().lower()
        category_filter = self.category_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        self.filtered_data = []
        
        for kegiatan in self.kegiatan_data:
            # Search filter
            nama = (kegiatan.get('nama_kegiatan', '') or kegiatan.get('judul', '')).lower()
            tempat = kegiatan.get('tempat', '').lower()
            
            if search_text and search_text not in nama and search_text not in tempat:
                continue
            
            # Category filter
            kategori = kegiatan.get('kategori', '') or kegiatan.get('jenis', '') or 'Lainnya'
            if category_filter != "Semua" and kategori != category_filter:
                continue
            
            # Status filter
            status = self.get_kegiatan_status(kegiatan)
            if status_filter != "Semua" and status != status_filter:
                continue
            
            self.filtered_data.append(kegiatan)
        
        self.update_table()
        self.update_statistics()
    
    def calendar_date_changed(self, date):
        """Handle calendar date selection"""
        selected_date = date.toString("yyyy-MM-dd")
        
        # Filter kegiatan for selected date
        filtered_for_date = []
        for kegiatan in self.kegiatan_data:
            tanggal = kegiatan.get('tanggal', '') or kegiatan.get('tanggal_kegiatan', '')
            if tanggal and selected_date in tanggal:
                filtered_for_date.append(kegiatan)
        
        if filtered_for_date:
            self.filtered_data = filtered_for_date
            self.update_table()
            QMessageBox.information(self, "Kegiatan", 
                f"Ditemukan {len(filtered_for_date)} kegiatan pada {date.toString('dd/MM/yyyy')}")
        else:
            QMessageBox.information(self, "Kegiatan", 
                f"Tidak ada kegiatan pada {date.toString('dd/MM/yyyy')}")
    
    def highlight_calendar_dates(self):
        """Highlight dates that have kegiatan"""
        # This would require custom calendar implementation
        # For now, just update the calendar to current date
        pass
    
    def show_kegiatan_detail(self):
        """Show detail of selected kegiatan"""
        current_row = self.table_widget.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_data):
            kegiatan = self.filtered_data[current_row]
            
            detail_html = f"""
            <h3 style="color: #9b59b6;">{kegiatan.get('nama_kegiatan', 'N/A')}</h3>
            <p><strong>Tanggal:</strong> {kegiatan.get('tanggal', 'N/A')}</p>
            <p><strong>Waktu:</strong> {kegiatan.get('waktu', 'N/A')}</p>
            <p><strong>Tempat:</strong> {kegiatan.get('tempat', 'N/A')}</p>
            <p><strong>Kategori:</strong> {kegiatan.get('kategori', 'N/A')}</p>
            <p><strong>Deskripsi:</strong><br>{kegiatan.get('deskripsi', 'Tidak ada deskripsi')}</p>
            """
            
            self.detail_text.setHtml(detail_html)
        else:
            self.detail_text.setText("Pilih kegiatan untuk melihat detail...")
    
    def update_statistics(self):
        """Update statistics labels"""
        from datetime import date
        today = date.today()
        
        total = len(self.filtered_data)
        upcoming = 0
        today_count = 0
        
        for kegiatan in self.filtered_data:
            status = self.get_kegiatan_status(kegiatan)
            if status == "Akan Datang":
                upcoming += 1
            elif status == "Sedang Berlangsung":
                today_count += 1
        
        self.total_label.setText(f"Total: {total} kegiatan")
        self.upcoming_label.setText(f"Akan Datang: {upcoming}")
        self.today_label.setText(f"Hari Ini: {today_count}")
        
        # Style the labels
        self.total_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.upcoming_label.setStyleSheet("color: #3498db; font-weight: bold;")
        self.today_label.setStyleSheet("color: #e67e22; font-weight: bold;")