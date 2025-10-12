# Path: server/components/keuangan.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QPushButton, QHeaderView,
                             QMessageBox, QLineEdit, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from database import DatabaseManager

class KeuanganComponent(QWidget):

    log_message = pyqtSignal(str)
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.keuangan_data = []
        self.filtered_data = []
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Data Keuangan")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Cari:"))
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Cari deskripsi...")
        self.search_input.textChanged.connect(self.filter_data)
        filter_layout.addWidget(self.search_input)

        filter_layout.addWidget(QLabel("Jenis:"))
        self.jenis_filter = QComboBox(self)
        self.jenis_filter.addItems(["Semua", "Pemasukan", "Pengeluaran"])
        self.jenis_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.jenis_filter)

        filter_layout.addWidget(QLabel("User:"))
        self.user_filter = QComboBox(self)
        self.user_filter.addItem("Semua User")
        self.user_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.user_filter)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Tanggal Transaksi", "Jenis", "Kategori", "Deskripsi",
            "Jumlah", "User", "Tanggal Input"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)

        # Set column widths
        self.table.setColumnWidth(0, 110)  # Tanggal Transaksi
        self.table.setColumnWidth(1, 100)  # Jenis
        self.table.setColumnWidth(2, 120)  # Kategori
        self.table.setColumnWidth(3, 200)  # Deskripsi
        self.table.setColumnWidth(4, 120)  # Jumlah
        self.table.setColumnWidth(5, 150)  # User (nama user client)
        self.table.setColumnWidth(6, 140)  # Tanggal Input

        header.setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Stats
        self.stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total: 0")
        self.pemasukan_label = QLabel("Pemasukan: Rp 0")
        self.pengeluaran_label = QLabel("Pengeluaran: Rp 0")
        self.saldo_label = QLabel("Saldo: Rp 0")
        
        self.stats_layout.addWidget(self.total_label)
        self.stats_layout.addWidget(self.pemasukan_label)
        self.stats_layout.addWidget(self.pengeluaran_label)
        self.stats_layout.addWidget(self.saldo_label)
        self.stats_layout.addStretch()
        layout.addLayout(self.stats_layout)
    
    def load_data(self):
        try:
            success, data = self.db_manager.get_keuangan_list()
            if success:
                self.keuangan_data = data if isinstance(data, list) else []
                self.filtered_data = self.keuangan_data.copy()
                self.update_user_filter()
                self.update_table()
                self.update_stats()
                self.log_message.emit(f"Data keuangan dimuat: {len(self.keuangan_data)} record")
            else:
                QMessageBox.critical(self, "Error", f"Gagal memuat data: {data}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat data: {str(e)}")

    def update_user_filter(self):
        """Update user filter dropdown with unique users"""
        current_text = self.user_filter.currentText()
        self.user_filter.clear()
        self.user_filter.addItem("Semua User")

        # Get unique users (prioritas: nama_user/nama lengkap > dibuat_oleh/username)
        users = set()
        for item in self.keuangan_data:
            # Prioritas sama dengan yang ditampilkan di tabel
            user_name = item.get('nama_user') or item.get('dibuat_oleh') or item.get('username') or ''
            if user_name and user_name != 'System':
                users.add(user_name)

        # Add users to filter
        for user in sorted(users):
            self.user_filter.addItem(user)

        # Restore previous selection if it exists
        index = self.user_filter.findText(current_text)
        if index >= 0:
            self.user_filter.setCurrentIndex(index)
    
    def filter_data(self):
        search = self.search_input.text().lower()
        jenis = self.jenis_filter.currentText()
        user_filter = self.user_filter.currentText()

        self.filtered_data = []
        for item in self.keuangan_data:
            # Search filter
            if search and search not in str(item.get('deskripsi', '')).lower():
                continue

            # Jenis filter
            if jenis != "Semua" and item.get('kategori') != jenis:
                continue

            # User filter (sama dengan prioritas di tabel)
            if user_filter != "Semua User":
                user_name = item.get('nama_user') or item.get('dibuat_oleh') or item.get('username') or ''
                if user_name != user_filter:
                    continue

            self.filtered_data.append(item)

        self.update_table()
        self.update_stats()
    
    def update_table(self):
        self.table.setRowCount(len(self.filtered_data))

        for row, item in enumerate(self.filtered_data):
            # Tanggal Transaksi
            tanggal = item.get('tanggal', '')
            if tanggal:
                try:
                    import datetime
                    if isinstance(tanggal, str):
                        date_obj = datetime.datetime.strptime(tanggal, '%Y-%m-%d')
                        tanggal = date_obj.strftime('%d/%m/%Y')
                except:
                    pass
            self.table.setItem(row, 0, QTableWidgetItem(str(tanggal)))

            # Jenis
            jenis_item = QTableWidgetItem(str(item.get('kategori', '')))
            if item.get('kategori') == 'Pemasukan':
                jenis_item.setBackground(QColor("#d5f4e6"))
            else:
                jenis_item.setBackground(QColor("#fadbd8"))
            self.table.setItem(row, 1, jenis_item)

            # Kategori
            self.table.setItem(row, 2, QTableWidgetItem(str(item.get('sub_kategori', ''))))

            # Deskripsi
            self.table.setItem(row, 3, QTableWidgetItem(str(item.get('deskripsi', ''))))

            # Jumlah
            jumlah = f"Rp {float(item.get('jumlah', 0)):,.0f}"
            self.table.setItem(row, 4, QTableWidgetItem(jumlah))

            # User (nama user client yang melakukan input)
            # Prioritas: nama_user (nama lengkap) > dibuat_oleh (username) > username (fallback) > 'System'
            user_name = item.get('nama_user') or item.get('dibuat_oleh') or item.get('username') or 'System'
            self.table.setItem(row, 5, QTableWidgetItem(str(user_name)))

            # Tanggal Input (created_at atau waktu input)
            tanggal_input = item.get('created_at', item.get('tanggal_input', ''))
            if tanggal_input:
                try:
                    import datetime
                    if isinstance(tanggal_input, str):
                        # Handle both datetime and date formats
                        if 'T' in tanggal_input or ' ' in tanggal_input:
                            # Datetime format
                            date_obj = datetime.datetime.fromisoformat(tanggal_input.replace('Z', '+00:00'))
                            tanggal_input = date_obj.strftime('%d/%m/%Y %H:%M')
                        else:
                            # Date only format
                            date_obj = datetime.datetime.strptime(tanggal_input, '%Y-%m-%d')
                            tanggal_input = date_obj.strftime('%d/%m/%Y')
                except:
                    pass
            else:
                tanggal_input = '-'
            self.table.setItem(row, 6, QTableWidgetItem(str(tanggal_input)))
    
    def update_stats(self):
        total = len(self.filtered_data)
        pemasukan = sum(float(item.get('jumlah', 0)) for item in self.filtered_data if item.get('kategori') == 'Pemasukan')
        pengeluaran = sum(float(item.get('jumlah', 0)) for item in self.filtered_data if item.get('kategori') == 'Pengeluaran')
        saldo = pemasukan - pengeluaran
        
        self.total_label.setText(f"Total: {total}")
        self.pemasukan_label.setText(f"Pemasukan: Rp {pemasukan:,.0f}")
        self.pengeluaran_label.setText(f"Pengeluaran: Rp {pengeluaran:,.0f}")
        self.saldo_label.setText(f"Saldo: Rp {saldo:,.0f}")
        
        # Color coding
        self.pemasukan_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.pengeluaran_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        if saldo >= 0:
            self.saldo_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.saldo_label.setStyleSheet("color: #e74c3c; font-weight: bold;")