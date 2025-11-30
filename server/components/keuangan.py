# Path: server/components/keuangan.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QPushButton, QHeaderView,
                             QMessageBox, QLineEdit, QComboBox, QAbstractItemView,
                             QTabWidget, QDialog, QFormLayout, QDateEdit, QSpinBox,
                             QTextEdit, QFileDialog, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect, QTimer, QDate
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush
from database import DatabaseManager
import datetime

class WordWrapHeaderView(QHeaderView):
    """Custom header view with word wrap and center alignment support"""
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)

    def sectionSizeFromContents(self, logicalIndex):
        """Calculate section size based on wrapped text"""
        if self.model():
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                width = self.sectionSize(logicalIndex)
                if width <= 0:
                    width = self.defaultSectionSize()
                font = self.font()
                font.setBold(True)
                fm = self.fontMetrics()
                rect = fm.boundingRect(0, 0, width - 8, 1000,
                                      Qt.AlignCenter | Qt.TextWordWrap, str(text))
                return QSize(width, max(rect.height() + 12, 25))
        return super().sectionSizeFromContents(logicalIndex)

    def paintSection(self, painter, rect, logicalIndex):
        """Paint section with word wrap and center alignment"""
        painter.save()
        bg_color = QColor(242, 242, 242)
        painter.fillRect(rect, bg_color)
        border_color = QColor(212, 212, 212)
        painter.setPen(border_color)
        painter.drawLine(rect.topRight(), rect.bottomRight())
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        if self.model():
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                font = self.font()
                font.setBold(True)
                painter.setFont(font)
                text_color = QColor(51, 51, 51)
                painter.setPen(text_color)
                text_rect = rect.adjusted(4, 4, -4, -4)
                painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, str(text))
        painter.restore()

class KeuanganDialog(QDialog):
    """Dialog untuk tambah/edit transaksi keuangan kategorial"""
    def __init__(self, parent=None, keuangan_data=None):
        super().__init__(parent)
        self.keuangan_data = keuangan_data if keuangan_data else {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Tambah/Edit Transaksi Keuangan")
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(8)

        # Tanggal
        self.tanggal = QDateEdit()
        self.tanggal.setCalendarPopup(True)
        if self.keuangan_data.get('tanggal'):
            try:
                date_obj = datetime.datetime.strptime(self.keuangan_data['tanggal'], '%Y-%m-%d').date()
                self.tanggal.setDate(QDate.fromString(date_obj.isoformat(), Qt.ISODate))
            except:
                self.tanggal.setDate(QDate.currentDate())
        else:
            self.tanggal.setDate(QDate.currentDate())
        form_layout.addRow("Tanggal:", self.tanggal)

        # Jenis Transaksi
        self.jenis = QComboBox()
        self.jenis.addItems(['Pemasukan', 'Pengeluaran'])
        if self.keuangan_data.get('jenis'):
            index = self.jenis.findText(self.keuangan_data['jenis'])
            if index >= 0:
                self.jenis.setCurrentIndex(index)
        form_layout.addRow("Jenis Transaksi:", self.jenis)

        # Kategori
        self.kategori = QComboBox()
        self.kategori.addItems([
            "Kolekte", "Donasi", "Operasional",
            "Pemeliharaan", "Program", "Lainnya"
        ])
        if self.keuangan_data.get('kategori'):
            index = self.kategori.findText(self.keuangan_data['kategori'])
            if index >= 0:
                self.kategori.setCurrentIndex(index)
        form_layout.addRow("Kategori:", self.kategori)

        # Keterangan
        self.keterangan = QTextEdit()
        self.keterangan.setMaximumHeight(80)
        self.keterangan.setText(self.keuangan_data.get('keterangan', ''))
        form_layout.addRow("Keterangan:", self.keterangan)

        # Jumlah
        self.jumlah = QSpinBox()
        self.jumlah.setRange(0, 999999999)
        self.jumlah.setValue(int(self.keuangan_data.get('jumlah', 0)))
        self.jumlah.setSuffix(" Rupiah")
        form_layout.addRow("Jumlah:", self.jumlah)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_button = QPushButton("Simpan")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        save_button.clicked.connect(self.accept)

        cancel_button = QPushButton("Batal")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_data(self):
        return {
            'tanggal': self.tanggal.date().toString(Qt.ISODate),
            'jenis': self.jenis.currentText(),
            'kategori': self.kategori.currentText(),
            'keterangan': self.keterangan.toPlainText(),
            'jumlah': self.jumlah.value(),
        }

class KeuanganWRWidget(QWidget):
    """Tab WR - Keuangan dari input WR/client"""
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
        title = QLabel("Data Keuangan WR")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Cari:"))
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Cari keterangan...")
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
        self.table.setColumnCount(8)

        custom_header = WordWrapHeaderView(Qt.Horizontal, self.table)
        self.table.setHorizontalHeader(custom_header)

        self.table.setHorizontalHeaderLabels([
            "Tanggal Transaksi", "Jenis", "Kategori", "Keterangan",
            "Jumlah", "Saldo", "User", "Tanggal Input"
        ])

        self.apply_professional_table_style(self.table)

        self.table.setColumnWidth(0, 110)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 150)
        self.table.setColumnWidth(7, 140)

        header = self.table.horizontalHeader()
        header.sectionResized.connect(self.update_header_height)

        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

        layout.addWidget(self.table)

        # Ringkasan Keuangan
        stats_frame = QLabel("Ringkasan Keuangan:")
        stats_frame.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(stats_frame)

        self.stats_layout = QHBoxLayout()

        self.total_label = QLabel("Total Transaksi: 0")
        self.total_label.setFont(QFont("Arial", 9))
        self.stats_layout.addWidget(self.total_label)

        self.stats_layout.addWidget(QLabel("|"))

        self.pemasukan_label = QLabel("Total Pemasukan: Rp 0")
        self.pemasukan_label.setFont(QFont("Arial", 9, QFont.Bold))
        self.pemasukan_label.setStyleSheet("color: #27ae60;")
        self.stats_layout.addWidget(self.pemasukan_label)

        self.stats_layout.addWidget(QLabel("|"))

        self.pengeluaran_label = QLabel("Total Pengeluaran: Rp 0")
        self.pengeluaran_label.setFont(QFont("Arial", 9, QFont.Bold))
        self.pengeluaran_label.setStyleSheet("color: #e74c3c;")
        self.stats_layout.addWidget(self.pengeluaran_label)

        self.stats_layout.addWidget(QLabel("|"))

        self.saldo_label = QLabel("Saldo: Rp 0")
        self.saldo_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.stats_layout.addWidget(self.saldo_label)

        self.stats_layout.addStretch()
        layout.addLayout(self.stats_layout)

    def update_header_height(self, logicalIndex, oldSize, newSize):
        if hasattr(self, 'table'):
            header = self.table.horizontalHeader()
            header.setMinimumHeight(25)
            max_height = 25
            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())
            header.setFixedHeight(max_height)

    def apply_professional_table_style(self, table):
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #d4d4d4;
                border-right: 1px solid #d4d4d4;
                padding: 6px 4px;
                font-weight: bold;
                color: #333333;
            }
        """)

        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        header.setMinimumHeight(25)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(500)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

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
            }
        """)

        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        table.verticalHeader().setDefaultSectionSize(20)
        table.setSelectionBehavior(QAbstractItemView.SelectItems)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(True)
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

        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)
        table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        table.setMinimumHeight(150)
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    def load_data(self):
        try:
            success, data = self.db_manager.get_keuangan_list()
            if success:
                self.keuangan_data = data if isinstance(data, list) else []
                # Sort data by ID ascending (terlama ke terbaru)
                self.keuangan_data = sorted(self.keuangan_data, key=lambda x: x.get('id', 0), reverse=False)
                self.filtered_data = self.keuangan_data.copy()
                self.update_user_filter()
                self.update_table()
                self.update_stats()
                self.log_message.emit(f"Data keuangan WR dimuat: {len(self.keuangan_data)} record (diurutkan dari terlama)")
            else:
                QMessageBox.critical(self, "Error", f"Gagal memuat data: {data}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat data: {str(e)}")

    def update_user_filter(self):
        current_text = self.user_filter.currentText()
        self.user_filter.clear()
        self.user_filter.addItem("Semua User")

        users = set()
        for item in self.keuangan_data:
            user_name = item.get('nama_user') or item.get('dibuat_oleh') or item.get('username') or ''
            if user_name and user_name != 'System':
                users.add(user_name)

        for user in sorted(users):
            self.user_filter.addItem(user)

        index = self.user_filter.findText(current_text)
        if index >= 0:
            self.user_filter.setCurrentIndex(index)

    def filter_data(self):
        search = self.search_input.text().lower()
        jenis = self.jenis_filter.currentText()
        user_filter = self.user_filter.currentText()

        self.filtered_data = []
        for item in self.keuangan_data:
            if search and search not in str(item.get('keterangan', '')).lower():
                continue

            if jenis != "Semua" and item.get('kategori') != jenis:
                continue

            if user_filter != "Semua User":
                user_name = item.get('nama_user') or item.get('dibuat_oleh') or item.get('username') or ''
                if user_name != user_filter:
                    continue

            self.filtered_data.append(item)

        # Sort filtered data by ID ascending (terlama ke terbaru)
        self.filtered_data = sorted(self.filtered_data, key=lambda x: x.get('id', 0), reverse=False)

        self.update_table()
        self.update_stats()

    def update_table(self):
        self.table.setRowCount(len(self.filtered_data))

        # Calculate running balance (saldo)
        running_balance = 0.0

        for row, item in enumerate(self.filtered_data):
            # Format tanggal transaksi - dd/mm/yyyy saja tanpa hari
            tanggal = item.get('tanggal', '')
            if tanggal:
                try:
                    if isinstance(tanggal, str):
                        tanggal_str = tanggal.strip()

                        # Handle RFC 1123 / GMT format (Mon, 17 Nov 2025 00:00:00 GMT)
                        if 'GMT' in tanggal_str or tanggal_str.count(',') == 1:
                            try:
                                # Parse RFC 1123 format
                                from email.utils import parsedate_to_datetime
                                date_obj = parsedate_to_datetime(tanggal_str)
                            except:
                                # Fallback: extract date parts manually
                                # Format: "Mon, 17 Nov 2025 00:00:00 GMT"
                                try:
                                    parts = tanggal_str.split(',')[1].strip().split()  # "17 Nov 2025 00:00:00 GMT"
                                    date_part = ' '.join(parts[:3])  # "17 Nov 2025"
                                    date_obj = datetime.datetime.strptime(date_part, '%d %b %Y')
                                except:
                                    date_obj = None
                        # Handle ISO format with time (2025-01-15T10:30:00 or 2025-01-15 10:30:00)
                        elif 'T' in tanggal_str or (' ' in tanggal_str and ':' in tanggal_str):
                            try:
                                date_obj = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00'))
                            except:
                                parts = tanggal_str.split('T')[0] if 'T' in tanggal_str else tanggal_str.split(' ')[0]
                                date_obj = datetime.datetime.strptime(parts, '%Y-%m-%d')
                        # Handle date only format (2025-01-15)
                        elif '-' in tanggal_str:
                            parts = tanggal_str.split(' ')[0] if ' ' in tanggal_str else tanggal_str
                            date_obj = datetime.datetime.strptime(parts, '%Y-%m-%d')
                        # Handle already formatted dates (15/01/2025)
                        elif '/' in tanggal_str:
                            try:
                                date_obj = datetime.datetime.strptime(tanggal_str, '%d/%m/%Y')
                            except:
                                date_obj = datetime.datetime.strptime(tanggal_str, '%m/%d/%Y')
                        else:
                            date_obj = datetime.datetime.strptime(tanggal_str, '%Y-%m-%d')

                        if date_obj:
                            # Format sebagai dd/mm/yyyy saja tanpa hari
                            tanggal = date_obj.strftime('%d/%m/%Y')
                except:
                    pass
            self.table.setItem(row, 0, QTableWidgetItem(str(tanggal)))

            jenis_value = str(item.get('kategori', ''))
            jenis_item = QTableWidgetItem(jenis_value)
            jenis_item.setTextAlignment(Qt.AlignCenter)

            if jenis_value == 'Pemasukan':
                jenis_item.setBackground(QColor("#d5f4e6"))
                jenis_item.setForeground(QColor("#27ae60"))
            elif jenis_value == 'Pengeluaran':
                jenis_item.setBackground(QColor("#fadbd8"))
                jenis_item.setForeground(QColor("#c0392b"))

            jenis_item.setFlags(jenis_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, jenis_item)

            self.table.setItem(row, 2, QTableWidgetItem(str(item.get('sub_kategori', ''))))
            self.table.setItem(row, 3, QTableWidgetItem(str(item.get('keterangan', ''))))

            # Calculate jumlah and update running balance
            try:
                jumlah_value = float(item.get('jumlah', 0))
                if jenis_value == 'Pemasukan':
                    running_balance += jumlah_value
                else:
                    running_balance -= jumlah_value
                jumlah = f"Rp {jumlah_value:,.0f}"
            except:
                jumlah = "Rp 0"
            self.table.setItem(row, 4, QTableWidgetItem(jumlah))

            # Saldo column (running balance)
            saldo_item = QTableWidgetItem(f"Rp {running_balance:,.0f}")
            if running_balance >= 0:
                saldo_item.setForeground(QColor("#27ae60"))
            else:
                saldo_item.setForeground(QColor("#e74c3c"))
            self.table.setItem(row, 5, saldo_item)

            user_name = item.get('nama_user') or item.get('dibuat_oleh') or item.get('username') or 'System'
            self.table.setItem(row, 6, QTableWidgetItem(str(user_name)))

            tanggal_input = item.get('created_at', item.get('tanggal_input', ''))
            if tanggal_input:
                try:
                    if isinstance(tanggal_input, str):
                        if 'T' in tanggal_input or ' ' in tanggal_input:
                            date_obj = datetime.datetime.fromisoformat(tanggal_input.replace('Z', '+00:00'))
                            tanggal_input = date_obj.strftime('%d/%m/%Y %H:%M')
                        else:
                            date_obj = datetime.datetime.strptime(tanggal_input, '%Y-%m-%d')
                            tanggal_input = date_obj.strftime('%d/%m/%Y')
                except:
                    pass
            else:
                tanggal_input = '-'
            self.table.setItem(row, 7, QTableWidgetItem(str(tanggal_input)))

    def update_stats(self):
        total = len(self.filtered_data)
        pemasukan = sum(float(item.get('jumlah', 0)) for item in self.filtered_data if item.get('kategori') == 'Pemasukan')
        pengeluaran = sum(float(item.get('jumlah', 0)) for item in self.filtered_data if item.get('kategori') == 'Pengeluaran')
        saldo = pemasukan - pengeluaran

        self.total_label.setText(f"Total Transaksi: {total}")
        self.pemasukan_label.setText(f"Total Pemasukan: Rp {pemasukan:,.0f}")
        self.pengeluaran_label.setText(f"Total Pengeluaran: Rp {pengeluaran:,.0f}")
        self.saldo_label.setText(f"Saldo: Rp {saldo:,.0f}")

        if saldo >= 0:
            self.saldo_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.saldo_label.setStyleSheet("color: #e74c3c; font-weight: bold;")


class KeuanganKategorialWidget(QWidget):
    """Tab K. Kategorial - Keuangan kategorial dikelola admin dengan CRUD"""
    log_message = pyqtSignal(str)

    def __init__(self, db_manager, admin_id=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.admin_id = admin_id
        self.keuangan_data = []
        self.filtered_data = []
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Keuangan Kategorial")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()

        add_btn = QPushButton("Tambah")
        add_btn.clicked.connect(self.add_data)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        header_layout.addWidget(add_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Cari:"))
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Cari keterangan...")
        self.search_input.textChanged.connect(self.filter_data)
        filter_layout.addWidget(self.search_input)

        filter_layout.addWidget(QLabel("Jenis:"))
        self.jenis_filter = QComboBox(self)
        self.jenis_filter.addItems(["Semua", "Pemasukan", "Pengeluaran"])
        self.jenis_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.jenis_filter)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)

        custom_header = WordWrapHeaderView(Qt.Horizontal, self.table)
        self.table.setHorizontalHeader(custom_header)

        self.table.setHorizontalHeaderLabels([
            "Tanggal", "Jenis", "Kategori", "Keterangan", "Jumlah", "Aksi"
        ])

        self.apply_professional_table_style(self.table)

        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 120)

        header = self.table.horizontalHeader()
        header.sectionResized.connect(self.update_header_height)

        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

        layout.addWidget(self.table)

        # Stats
        stats_frame = QLabel("Ringkasan Keuangan:")
        stats_frame.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(stats_frame)

        self.stats_layout = QHBoxLayout()

        self.total_label = QLabel("Total Transaksi: 0")
        self.total_label.setFont(QFont("Arial", 9))
        self.stats_layout.addWidget(self.total_label)

        self.stats_layout.addWidget(QLabel("|"))

        self.pemasukan_label = QLabel("Total Pemasukan: Rp 0")
        self.pemasukan_label.setFont(QFont("Arial", 9, QFont.Bold))
        self.pemasukan_label.setStyleSheet("color: #27ae60;")
        self.stats_layout.addWidget(self.pemasukan_label)

        self.stats_layout.addWidget(QLabel("|"))

        self.pengeluaran_label = QLabel("Total Pengeluaran: Rp 0")
        self.pengeluaran_label.setFont(QFont("Arial", 9, QFont.Bold))
        self.pengeluaran_label.setStyleSheet("color: #e74c3c;")
        self.stats_layout.addWidget(self.pengeluaran_label)

        self.stats_layout.addWidget(QLabel("|"))

        self.saldo_label = QLabel("Saldo: Rp 0")
        self.saldo_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.stats_layout.addWidget(self.saldo_label)

        self.stats_layout.addStretch()
        layout.addLayout(self.stats_layout)

    def update_header_height(self, logicalIndex, oldSize, newSize):
        if hasattr(self, 'table'):
            header = self.table.horizontalHeader()
            header.setMinimumHeight(25)
            max_height = 25
            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())
            header.setFixedHeight(max_height)

    def apply_professional_table_style(self, table):
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #d4d4d4;
                border-right: 1px solid #d4d4d4;
                padding: 6px 4px;
                font-weight: bold;
                color: #333333;
            }
        """)

        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        header.setMinimumHeight(25)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(500)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

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
        """)

        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        table.verticalHeader().setDefaultSectionSize(20)
        table.setSelectionBehavior(QAbstractItemView.SelectItems)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(True)
        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)
        table.setMinimumHeight(150)

    def load_data(self):
        try:
            success, data = self.db_manager.get_keuangan_kategorial_list()
            if success:
                self.keuangan_data = data if isinstance(data, list) else []
                self.filtered_data = self.keuangan_data.copy()
                self.update_table()
                self.update_stats()
                self.log_message.emit(f"Data keuangan kategorial dimuat: {len(self.keuangan_data)} record")
            else:
                self.log_message.emit(f"Gagal memuat data: {data}")
        except Exception as e:
            self.log_message.emit(f"Error: {str(e)}")

    def filter_data(self):
        search = self.search_input.text().lower()
        jenis = self.jenis_filter.currentText()

        self.filtered_data = []
        for item in self.keuangan_data:
            if search and search not in str(item.get('keterangan', '')).lower():
                continue

            if jenis != "Semua" and item.get('jenis') != jenis:
                continue

            self.filtered_data.append(item)

        self.update_table()
        self.update_stats()

    def update_table(self):
        self.table.setRowCount(len(self.filtered_data))

        for row, item in enumerate(self.filtered_data):
            # Format tanggal transaksi - dd/mm/yyyy saja tanpa hari
            tanggal = item.get('tanggal', '')
            if tanggal:
                try:
                    if isinstance(tanggal, str):
                        tanggal_str = tanggal.strip()

                        # Handle RFC 1123 / GMT format (Mon, 17 Nov 2025 00:00:00 GMT)
                        if 'GMT' in tanggal_str or tanggal_str.count(',') == 1:
                            try:
                                # Parse RFC 1123 format
                                from email.utils import parsedate_to_datetime
                                date_obj = parsedate_to_datetime(tanggal_str)
                            except:
                                # Fallback: extract date parts manually
                                # Format: "Mon, 17 Nov 2025 00:00:00 GMT"
                                try:
                                    parts = tanggal_str.split(',')[1].strip().split()  # "17 Nov 2025 00:00:00 GMT"
                                    date_part = ' '.join(parts[:3])  # "17 Nov 2025"
                                    date_obj = datetime.datetime.strptime(date_part, '%d %b %Y')
                                except:
                                    date_obj = None
                        # Handle ISO format with time (2025-01-15T10:30:00 or 2025-01-15 10:30:00)
                        elif 'T' in tanggal_str or (' ' in tanggal_str and ':' in tanggal_str):
                            try:
                                date_obj = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00'))
                            except:
                                parts = tanggal_str.split('T')[0] if 'T' in tanggal_str else tanggal_str.split(' ')[0]
                                date_obj = datetime.datetime.strptime(parts, '%Y-%m-%d')
                        # Handle date only format (2025-01-15)
                        elif '-' in tanggal_str:
                            parts = tanggal_str.split(' ')[0] if ' ' in tanggal_str else tanggal_str
                            date_obj = datetime.datetime.strptime(parts, '%Y-%m-%d')
                        # Handle already formatted dates (15/01/2025)
                        elif '/' in tanggal_str:
                            try:
                                date_obj = datetime.datetime.strptime(tanggal_str, '%d/%m/%Y')
                            except:
                                date_obj = datetime.datetime.strptime(tanggal_str, '%m/%d/%Y')
                        else:
                            date_obj = datetime.datetime.strptime(tanggal_str, '%Y-%m-%d')

                        if date_obj:
                            # Format sebagai dd/mm/yyyy saja tanpa hari
                            tanggal = date_obj.strftime('%d/%m/%Y')
                except:
                    pass
            self.table.setItem(row, 0, QTableWidgetItem(str(tanggal)))

            jenis_value = str(item.get('jenis', ''))
            jenis_item = QTableWidgetItem(jenis_value)
            jenis_item.setTextAlignment(Qt.AlignCenter)

            if jenis_value == 'Pemasukan':
                jenis_item.setBackground(QColor("#d5f4e6"))
                jenis_item.setForeground(QColor("#27ae60"))
            elif jenis_value == 'Pengeluaran':
                jenis_item.setBackground(QColor("#fadbd8"))
                jenis_item.setForeground(QColor("#c0392b"))

            jenis_item.setFlags(jenis_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, jenis_item)

            self.table.setItem(row, 2, QTableWidgetItem(str(item.get('kategori', ''))))
            self.table.setItem(row, 3, QTableWidgetItem(str(item.get('keterangan', ''))))

            jumlah = f"Rp {float(item.get('jumlah', 0)):,.0f}"
            self.table.setItem(row, 4, QTableWidgetItem(jumlah))

            # Aksi buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)

            edit_btn = QPushButton("Edit")
            edit_btn.setMaximumWidth(50)
            edit_btn.setStyleSheet("background-color: #f39c12; color: white; border: none; border-radius: 3px;")
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_data(r))
            action_layout.addWidget(edit_btn)

            delete_btn = QPushButton("Hapus")
            delete_btn.setMaximumWidth(60)
            delete_btn.setStyleSheet("background-color: #e74c3c; color: white; border: none; border-radius: 3px;")
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_data(r))
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 5, action_widget)

    def update_stats(self):
        total = len(self.filtered_data)
        pemasukan = sum(float(item.get('jumlah', 0)) for item in self.filtered_data if item.get('jenis') == 'Pemasukan')
        pengeluaran = sum(float(item.get('jumlah', 0)) for item in self.filtered_data if item.get('jenis') == 'Pengeluaran')
        saldo = pemasukan - pengeluaran

        self.total_label.setText(f"Total Transaksi: {total}")
        self.pemasukan_label.setText(f"Total Pemasukan: Rp {pemasukan:,.0f}")
        self.pengeluaran_label.setText(f"Total Pengeluaran: Rp {pengeluaran:,.0f}")
        self.saldo_label.setText(f"Saldo: Rp {saldo:,.0f}")

        if saldo >= 0:
            self.saldo_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.saldo_label.setStyleSheet("color: #e74c3c; font-weight: bold;")

    def add_data(self):
        dialog = KeuanganDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                success, result = self.db_manager.add_keuangan_kategorial(data, self.admin_id)
                if success:
                    self.load_data()
                    self.log_message.emit(f"Data keuangan berhasil ditambahkan")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def set_admin_id(self, admin_id):
        """Set admin ID for this widget"""
        self.admin_id = admin_id

    def edit_data(self, row):
        if row < 0 or row >= len(self.filtered_data):
            return
        item = self.filtered_data[row]
        dialog = KeuanganDialog(self, item)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                success, result = self.db_manager.update_keuangan_kategorial(item.get('id_keuangan_kategorial'), data)
                if success:
                    self.load_data()
                    self.log_message.emit(f"Data keuangan berhasil diupdate")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def delete_data(self, row):
        if row < 0 or row >= len(self.filtered_data):
            return
        item = self.filtered_data[row]
        reply = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus data ini?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                success, result = self.db_manager.delete_keuangan_kategorial(item.get('id_keuangan_kategorial'))
                if success:
                    self.load_data()
                    self.log_message.emit(f"Data keuangan berhasil dihapus")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")


class KeuanganComponent(QWidget):
    """Main Keuangan Component dengan tab WR dan K. Kategorial"""
    log_message = pyqtSignal(str)

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_admin = None

        layout = QVBoxLayout(self)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Tab WR
        self.wr_widget = KeuanganWRWidget(db_manager, self)
        self.wr_widget.log_message.connect(self.on_log_message)
        self.tab_widget.addTab(self.wr_widget, "WR")

        # Tab K. Kategorial
        self.kategorial_widget = KeuanganKategorialWidget(db_manager, self)
        self.kategorial_widget.log_message.connect(self.on_log_message)
        self.tab_widget.addTab(self.kategorial_widget, "K. Kategorial")

        layout.addWidget(self.tab_widget)

    def load_data(self):
        """Load data in both tabs"""
        try:
            self.wr_widget.load_data()
            self.kategorial_widget.load_data()
            self.log_message.emit("Data keuangan dimuat")
        except Exception as e:
            self.log_message.emit(f"Error loading data: {str(e)}")

    def set_current_admin(self, admin_data):
        """Set the current admin data."""
        self.current_admin = admin_data

    def on_log_message(self, message):
        """Relay log messages"""
        self.log_message.emit(message)
