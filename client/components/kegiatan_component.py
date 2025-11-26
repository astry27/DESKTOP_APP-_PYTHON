# Path: client/components/kegiatan_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QPushButton, QFrame,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox,
                             QCalendarWidget, QTextEdit, QSplitter, QDialog,
                             QFormLayout, QDateEdit, QTimeEdit, QFileDialog, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTime, QSize, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QBrush, QPainter
import os
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

class KegiatanDialog(QDialog):
    """Dialog untuk menambah/edit kegiatan"""

    def __init__(self, parent=None, kegiatan_data=None):
        super().__init__(parent)
        self.kegiatan_data = kegiatan_data
        self.is_edit = kegiatan_data is not None
        self.setup_ui()

        if self.is_edit:
            self.load_data()

    def setup_ui(self):
        self.setWindowTitle("Edit Kegiatan" if self.is_edit else "Tambah Kegiatan")
        self.setMinimumWidth(600)
        self.setMinimumHeight(550)

        layout = QVBoxLayout(self)

        # Form layout - urutan sesuai dengan tabel
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # 1. Kategori - sesuai dengan ENUM di database
        self.kategori_input = QComboBox()
        self.kategori_input.addItems([
            "Misa", "Doa", "Sosial", "Pendidikan",
            "Ibadah", "Katekese", "Rohani",
            "Administratif", "Lainnya"
        ])
        form_layout.addRow("Kategori: *", self.kategori_input)

        # 2. Nama Kegiatan
        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Masukkan nama kegiatan")
        form_layout.addRow("Nama Kegiatan: *", self.nama_input)

        # 3. Sasaran Kegiatan
        self.sasaran_input = QTextEdit()
        self.sasaran_input.setPlaceholderText("Masukkan sasaran kegiatan (target peserta, kelompok, dll)")
        self.sasaran_input.setMaximumHeight(60)
        form_layout.addRow("Sasaran Kegiatan:", self.sasaran_input)

        # 4. Tujuan Kegiatan
        self.tujuan_input = QTextEdit()
        self.tujuan_input.setPlaceholderText("Masukkan tujuan kegiatan (maksud dan harapan)")
        self.tujuan_input.setMaximumHeight(60)
        form_layout.addRow("Tujuan Kegiatan:", self.tujuan_input)

        # 5. Tempat Kegiatan (Lokasi)
        self.lokasi_input = QLineEdit()
        self.lokasi_input.setPlaceholderText("Masukkan tempat/lokasi kegiatan")
        form_layout.addRow("Tempat Kegiatan: *", self.lokasi_input)

        # 4. Tanggal Pelaksanaan (single date only)
        self.tanggal_mulai_input = QDateEdit()
        self.tanggal_mulai_input.setCalendarPopup(True)
        self.tanggal_mulai_input.setDate(QDate.currentDate())
        self.tanggal_mulai_input.setDisplayFormat("dd/MM/yyyy")
        self.tanggal_mulai_input.setToolTip("Tanggal pelaksanaan kegiatan")
        form_layout.addRow("Tanggal Pelaksanaan: *", self.tanggal_mulai_input)

        # 5. Waktu Pelaksanaan (single time)
        time_layout = QHBoxLayout()

        self.waktu_mulai_input = QTimeEdit()
        self.waktu_mulai_input.setTime(QTime.currentTime())
        self.waktu_mulai_input.setDisplayFormat("HH:mm")
        self.waktu_mulai_input.setToolTip("Waktu pelaksanaan (contoh: 08:00)")

        time_label = QLabel(" WITA")
        time_label.setStyleSheet("font-weight: bold;")

        time_layout.addWidget(self.waktu_mulai_input)
        time_layout.addWidget(time_label)
        time_layout.addStretch()

        form_layout.addRow("Waktu Pelaksanaan: *", time_layout)

        # 6. Penanggung Jawab
        self.penanggungjawab_input = QLineEdit()
        self.penanggungjawab_input.setPlaceholderText("Nama penanggung jawab kegiatan")
        form_layout.addRow("Penanggung Jawab: *", self.penanggungjawab_input)

        # 7. Status Kegiatan
        self.status_input = QComboBox()
        self.status_input.addItems([
            "Direncanakan", "Berlangsung", "Selesai", "Dibatalkan"
        ])
        form_layout.addRow("Status Kegiatan: *", self.status_input)

        # Keterangan (opsional)
        self.keterangan_input = QTextEdit()
        self.keterangan_input.setPlaceholderText("Keterangan tambahan kegiatan (opsional)")
        self.keterangan_input.setMaximumHeight(80)
        form_layout.addRow("Keterangan:", self.keterangan_input)

        layout.addLayout(form_layout)

        # Info label
        info_label = QLabel("* Field wajib diisi")
        info_label.setStyleSheet("color: #e74c3c; font-size: 10px; font-style: italic;")
        layout.addWidget(info_label)

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
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        save_button.clicked.connect(self.accept)  # type: ignore

        cancel_button = QPushButton("Batal")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_button.clicked.connect(self.reject)  # type: ignore

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def load_data(self):
        """Load existing kegiatan data into form"""
        if not self.kegiatan_data:
            return

        self.nama_input.setText(self.kegiatan_data.get('nama_kegiatan', ''))

        # Sasaran Kegiatan
        self.sasaran_input.setPlainText(self.kegiatan_data.get('sasaran_kegiatan', ''))

        # Tujuan Kegiatan
        self.tujuan_input.setPlainText(self.kegiatan_data.get('tujuan_kegiatan', ''))

        # Parse tanggal_pelaksanaan
        tanggal_mulai_str = self.kegiatan_data.get('tanggal_pelaksanaan') or self.kegiatan_data.get('tanggal_mulai') or self.kegiatan_data.get('tanggal', '')
        if tanggal_mulai_str:
            try:
                if isinstance(tanggal_mulai_str, str):
                    date_obj = datetime.datetime.strptime(tanggal_mulai_str, '%Y-%m-%d')
                    self.tanggal_mulai_input.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except:
                pass

        # Parse waktu_mulai
        waktu_mulai_str = self.kegiatan_data.get('waktu_mulai') or self.kegiatan_data.get('waktu', '')
        if waktu_mulai_str:
            try:
                time_obj = datetime.datetime.strptime(waktu_mulai_str, '%H:%M').time()
                self.waktu_mulai_input.setTime(QTime(time_obj.hour, time_obj.minute))
            except:
                pass

        # Lokasi
        lokasi = self.kegiatan_data.get('tempat_kegiatan') or self.kegiatan_data.get('lokasi') or self.kegiatan_data.get('tempat', '')
        self.lokasi_input.setText(lokasi)

        # Kategori
        kategori = self.kegiatan_data.get('kategori', '')
        index = self.kategori_input.findText(kategori)
        if index >= 0:
            self.kategori_input.setCurrentIndex(index)

        # Status
        status = self.kegiatan_data.get('status_kegiatan') or self.kegiatan_data.get('status', 'Direncanakan')
        status_index = self.status_input.findText(status)
        if status_index >= 0:
            self.status_input.setCurrentIndex(status_index)

        # Penanggung Jawab
        penanggung_jawab = self.kegiatan_data.get('penanggung_jawab') or self.kegiatan_data.get('penanggungjawab', '')
        self.penanggungjawab_input.setText(penanggung_jawab)

        # Keterangan
        self.keterangan_input.setPlainText(self.kegiatan_data.get('keterangan', ''))

    def get_data(self):
        """Get form data - sesuai struktur tabel kegiatan_wr"""
        tanggal_pelaksanaan = self.tanggal_mulai_input.date().toString('yyyy-MM-dd')
        waktu_mulai = self.waktu_mulai_input.time().toString('HH:mm')

        return {
            'nama_kegiatan': self.nama_input.text().strip(),
            'sasaran_kegiatan': self.sasaran_input.toPlainText().strip(),
            'tujuan_kegiatan': self.tujuan_input.toPlainText().strip(),
            'tanggal_pelaksanaan': tanggal_pelaksanaan,
            'waktu_mulai': waktu_mulai,
            'tempat_kegiatan': self.lokasi_input.text().strip(),
            'kategori': self.kategori_input.currentText(),
            'status_kegiatan': self.status_input.currentText(),
            'penanggung_jawab': self.penanggungjawab_input.text().strip(),
            'keterangan': self.keterangan_input.toPlainText().strip()
        }

    def validate(self):
        """Validate form data"""
        if not self.nama_input.text().strip():
            QMessageBox.warning(self, "Validasi", "Nama kegiatan tidak boleh kosong")
            return False

        if not self.lokasi_input.text().strip():
            QMessageBox.warning(self, "Validasi", "Tempat kegiatan tidak boleh kosong")
            return False

        if not self.penanggungjawab_input.text().strip():
            QMessageBox.warning(self, "Validasi", "Penanggung jawab tidak boleh kosong")
            return False

        return True

    def accept(self):
        if self.validate():
            super().accept()


class KegiatanClientComponent(QWidget):

    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.kegiatan_data = []
        self.filtered_data = []

        self.setup_ui()
        self.load_kegiatan_data()

    def load_user_kegiatan_data(self):
        """Load kegiatan WR data from API - user-specific only"""
        # Clear semua data lama
        self.kegiatan_data = []
        self.filtered_data = []
        self.table_widget.setRowCount(0)

        try:
            result = self.api_client.get_my_kegiatan_wr()
            if result.get('success'):
                response_data = result.get('data', {})
                if isinstance(response_data, dict) and response_data.get('status') == 'success':
                    self.kegiatan_data = response_data.get('data', [])
                elif isinstance(response_data, list):
                    self.kegiatan_data = response_data
                else:
                    self.kegiatan_data = []
            else:
                self.kegiatan_data = []

            self.filtered_data = self.kegiatan_data.copy()
            self.update_table()
            self.update_calendar_indicators()
            self.update_statistics()
            self.log_message.emit(f"Data kegiatan WR berhasil dimuat: {len(self.kegiatan_data)} kegiatan")

        except Exception as e:
            self.log_message.emit(f"Error loading kegiatan WR data: {str(e)}")
            self.kegiatan_data = []
            self.filtered_data = []
            self.update_table()

    def load_kegiatan_data(self):
        """Alias for load_user_kegiatan_data to maintain compatibility"""
        self.load_user_kegiatan_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title section with professional styling
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 2px solid #ecf0f1;
                padding: 10px 0px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("Kegiatan Wilayah Rohani")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addWidget(title_frame)

        # Content area
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Main content with splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Calendar only
        left_panel = QWidget()
        left_panel.setMaximumWidth(320)
        left_panel.setMinimumWidth(280)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

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
        left_layout.addStretch()

        # Right panel - Filters, table and details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)

        # Combined toolbar with search/filter and add button (tanpa title)
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        # Search - ukuran sama dengan keuangan_component
        search_label = QLabel("Cari:")
        search_label.setStyleSheet("font-weight: 500; color: #2c3e50;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari kegiatan...")
        self.search_input.setFixedWidth(150)  # Smaller width matching reference image
        self.search_input.textChanged.connect(self.filter_data)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 4px 6px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                font-size: 11px;
                min-height: 24px;
                max-height: 24px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)

        # Category filter - sesuai dengan ENUM di database
        category_label = QLabel("Kategori:")
        category_label.setStyleSheet("font-weight: 500; color: #2c3e50;")
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "Semua", "Misa", "Doa", "Sosial", "Pendidikan",
            "Ibadah", "Katekese", "Rohani", "Administratif", "Lainnya"
        ])
        self.category_filter.setFixedWidth(120)
        self.category_filter.currentTextChanged.connect(self.filter_data)

        # Status filter
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-weight: 500; color: #2c3e50;")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Semua", "Akan Datang", "Sedang Berlangsung", "Selesai"])
        self.status_filter.setFixedWidth(140)
        self.status_filter.currentTextChanged.connect(self.filter_data)

        # Add button in the same row
        add_button = self.create_professional_button("add.png", "Tambah Kegiatan", "#27ae60", "#2ecc71")
        add_button.clicked.connect(self.add_kegiatan)

        toolbar_layout.addWidget(search_label)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(category_label)
        toolbar_layout.addWidget(self.category_filter)
        toolbar_layout.addWidget(status_label)
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(add_button)

        right_layout.addLayout(toolbar_layout)

        # Table with new layout order
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(11)
        self.table_widget.setHorizontalHeaderLabels([
            "Kategori", "Nama Kegiatan", "Sasaran Kegiatan", "Tujuan Kegiatan",
            "Tempat Kegiatan", "Tanggal Pelaksanaan",
            "Waktu Pelaksanaan", "Penanggung Jawab", "User", "Status Kegiatan", "Keterangan"
        ])

        custom_header = WordWrapHeaderView(Qt.Horizontal, self.table_widget)
        self.table_widget.setHorizontalHeader(custom_header)

        # Set column widths properly
        header = self.table_widget.horizontalHeader()
        self.table_widget.setColumnWidth(0, 100)  # Kategori
        self.table_widget.setColumnWidth(1, 200)  # Nama Kegiatan
        self.table_widget.setColumnWidth(2, 180)  # Sasaran Kegiatan
        self.table_widget.setColumnWidth(3, 180)  # Tujuan Kegiatan
        self.table_widget.setColumnWidth(4, 150)  # Tempat Kegiatan
        self.table_widget.setColumnWidth(5, 150)  # Tanggal Pelaksanaan
        self.table_widget.setColumnWidth(6, 150)  # Waktu Pelaksanaan
        self.table_widget.setColumnWidth(7, 120)  # Penanggung Jawab
        self.table_widget.setColumnWidth(8, 120)  # User
        self.table_widget.setColumnWidth(9, 120)  # Status Kegiatan
        self.table_widget.setColumnWidth(10, 200)  # Keterangan

        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setMinimumSectionSize(50)
        header.sectionResized.connect(self.update_header_height)
        header.setVisible(True)

        self.apply_professional_table_style()
        self.table_widget.horizontalHeader().setFixedHeight(25)
        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

        self.table_widget.setAlternatingRowColors(False)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.verticalHeader().setVisible(True)
        self.table_widget.verticalHeader().setDefaultSectionSize(24)

        # Set minimum height for table
        self.table_widget.setMinimumHeight(300)

        right_layout.addWidget(self.table_widget, 1)  # Stretch factor 1

        # Action buttons below table
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(3)  # Reduced spacing between buttons
        action_buttons_layout.addStretch()

        # View button
        view_button = self.create_professional_button("view.png", "Lihat Detail", "#3498db", "#2980b9")
        view_button.clicked.connect(self.view_kegiatan)

        # Edit button
        edit_button = self.create_professional_button("edit.png", "Edit Data", "#f39c12", "#e67e22")
        edit_button.clicked.connect(self.edit_kegiatan)

        # Delete button
        delete_button = self.create_professional_button("delete.png", "Hapus Data", "#e74c3c", "#c0392b")
        delete_button.clicked.connect(self.delete_kegiatan)

        # Refresh button
        refresh_button = self.create_professional_button("refresh.png", "Refresh", "#16a085", "#1abc9c")
        refresh_button.clicked.connect(self.load_kegiatan_data)

        # Export button
        export_button = self.create_professional_button("export.png", "Export Data", "#9b59b6", "#8e44ad")
        export_button.clicked.connect(self.export_kegiatan)

        action_buttons_layout.addWidget(view_button)
        action_buttons_layout.addWidget(edit_button)
        action_buttons_layout.addWidget(delete_button)
        action_buttons_layout.addWidget(refresh_button)
        action_buttons_layout.addWidget(export_button)
        action_buttons_layout.addStretch()

        right_layout.addLayout(action_buttons_layout)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])

        content_layout.addWidget(splitter)
        layout.addLayout(content_layout)

        # Statistics
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setContentsMargins(10, 10, 10, 10)
        self.total_label = QLabel("Total: 0 kegiatan")
        self.upcoming_label = QLabel("Akan Datang: 0")
        self.today_label = QLabel("Hari Ini: 0")

        self.stats_layout.addWidget(self.total_label)
        self.stats_layout.addWidget(self.upcoming_label)
        self.stats_layout.addWidget(self.today_label)
        self.stats_layout.addStretch()

        layout.addLayout(self.stats_layout)

    def update_header_height(self, logical_index, old_size, new_size):
        """Update header height when column widths change to fit wrapped text"""
        if not hasattr(self, "table_widget"):
            return

        header = self.table_widget.horizontalHeader()
        header.setMinimumHeight(25)
        max_height = 25
        for index in range(header.count()):
            size = header.sectionSizeFromContents(index)
            max_height = max(max_height, size.height())
        header.setFixedHeight(max_height)

    def apply_professional_table_style(self):
        """Apply jemaat-style table styling for consistent appearance"""
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)
        self.table_widget.horizontalHeader().setFont(header_font)

        self.table_widget.horizontalHeader().setStyleSheet("""
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

        self.table_widget.setStyleSheet("""
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

        self.table_widget.verticalHeader().setStyleSheet("""
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

        self.table_widget.setShowGrid(True)
        self.table_widget.setGridStyle(Qt.SolidLine)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    def create_professional_button(self, icon_name, text, bg_color, hover_color):
        """Create a professional button with icon and text"""
        button = QPushButton(f" {text}")  # Add space before text for icon spacing

        # Dynamic size based on text length to prevent cutoff
        # Calculate approximate width needed: icon(16) + spacing(6) + text(~8px per char) + padding(12)
        estimated_width = 16 + 6 + (len(text) * 7) + 12
        min_width = max(100, estimated_width)
        max_width = max(150, estimated_width + 20)

        button.setMinimumSize(min_width, 28)
        button.setMaximumSize(max_width, 28)

        # Add icon if available
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', icon_name)
        if os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(16, 16))  # Slightly larger icon
            except Exception:
                pass

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: 1px solid {bg_color};
                border-radius: 4px;
                padding: 4px 8px 4px 4px;
                font-size: 11px;
                font-weight: 500;
                text-align: left;
                padding-left: 6px;
                margin: 1px 2px;
                white-space: nowrap;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {bg_color};
                border-color: {bg_color};
            }}
        """)

        return button

    def add_kegiatan(self):
        """Add new kegiatan"""
        dialog = KegiatanDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            # Validasi data sebelum kirim
            if not data.get('nama_kegiatan'):
                QMessageBox.warning(self, "Validasi", "Nama kegiatan tidak boleh kosong")
                return

            if not data.get('tempat_kegiatan'):
                QMessageBox.warning(self, "Validasi", "Tempat kegiatan tidak boleh kosong")
                return

            try:
                # Log data yang akan dikirim untuk debugging
                self.log_message.emit(f"Mengirim data kegiatan WR: {data}")

                result = self.api_client.add_kegiatan_wr(data)

                # Log response dari server
                self.log_message.emit(f"Response dari server: {result}")

                if result.get("success"):
                    QMessageBox.information(self, "Sukses", "Kegiatan WR berhasil ditambahkan")
                    self.log_message.emit(f"Kegiatan WR '{data['nama_kegiatan']}' berhasil ditambahkan")
                    self.load_kegiatan_data()
                else:
                    error_msg = result.get('data', 'Unknown error')
                    QMessageBox.warning(self, "Error", f"Gagal menambahkan kegiatan WR:\n{error_msg}")
                    self.log_message.emit(f"Gagal menambahkan kegiatan WR: {error_msg}")
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                QMessageBox.critical(self, "Error", f"Error menambahkan kegiatan:\n{str(e)}")
                self.log_message.emit(f"Error menambahkan kegiatan: {str(e)}\n{error_detail}")

    def view_kegiatan(self):
        """View selected kegiatan"""
        current_row = self.table_widget.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_data):
            kegiatan = self.filtered_data[current_row]

            # Create detail dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Detail Kegiatan")
            dialog.setMinimumSize(500, 400)

            layout = QVBoxLayout(dialog)

            detail_text = QTextEdit()
            detail_text.setReadOnly(True)

            # Support both old and new field names
            tanggal = kegiatan.get('tanggal') or kegiatan.get('tanggal_mulai', 'N/A')
            waktu = kegiatan.get('waktu') or kegiatan.get('waktu_mulai', 'N/A')
            tempat = kegiatan.get('tempat') or kegiatan.get('lokasi', 'N/A')

            detail_html = f"""
            <h2 style="color: #9b59b6;">{kegiatan.get('nama_kegiatan', 'N/A')}</h2>
            <hr>
            <p><strong>Tanggal:</strong> {tanggal}</p>
            <p><strong>Waktu:</strong> {waktu}</p>
            <p><strong>Tempat:</strong> {tempat}</p>
            <p><strong>Kategori:</strong> {kegiatan.get('kategori', 'N/A')}</p>
            <p><strong>Status:</strong> {self.get_kegiatan_status(kegiatan)}</p>
            <hr>
            <p><strong>Deskripsi:</strong></p>
            <p>{kegiatan.get('deskripsi', 'Tidak ada deskripsi')}</p>
            """

            detail_text.setHtml(detail_html)
            layout.addWidget(detail_text)

            close_button = QPushButton("Tutup")
            close_button.clicked.connect(dialog.accept)  # type: ignore
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            layout.addWidget(close_button)

            dialog.exec_()
        else:
            QMessageBox.warning(self, "Peringatan", "Pilih kegiatan terlebih dahulu")

    def edit_kegiatan(self):
        """Edit selected kegiatan"""
        current_row = self.table_widget.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_data):
            kegiatan = self.filtered_data[current_row]

            dialog = KegiatanDialog(self, kegiatan)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()

                try:
                    kegiatan_id = kegiatan.get('id_kegiatan_wr') or kegiatan.get('id')
                    result = self.api_client.update_kegiatan_wr(kegiatan_id, data)
                    if result["success"]:
                        QMessageBox.information(self, "Sukses", "Kegiatan WR berhasil diupdate")
                        self.log_message.emit(f"Kegiatan WR '{data['nama_kegiatan']}' berhasil diupdate")
                        self.load_kegiatan_data()
                    else:
                        QMessageBox.warning(self, "Error", f"Gagal update kegiatan WR:\n{result['data']}")
                        self.log_message.emit(f"Gagal update kegiatan WR: {result['data']}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error update kegiatan:\n{str(e)}")
                    self.log_message.emit(f"Error update kegiatan: {str(e)}")
        else:
            QMessageBox.warning(self, "Peringatan", "Pilih kegiatan terlebih dahulu")

    def delete_kegiatan(self):
        """Delete selected kegiatan"""
        current_row = self.table_widget.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_data):
            kegiatan = self.filtered_data[current_row]

            reply = QMessageBox.question(self, "Konfirmasi",
                                       f"Apakah Anda yakin ingin menghapus kegiatan '{kegiatan.get('nama_kegiatan')}'?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    kegiatan_id = kegiatan.get('id_kegiatan_wr') or kegiatan.get('id')
                    result = self.api_client.delete_kegiatan_wr(kegiatan_id)
                    if result["success"]:
                        QMessageBox.information(self, "Sukses", "Kegiatan WR berhasil dihapus")
                        self.log_message.emit(f"Kegiatan WR '{kegiatan.get('nama_kegiatan')}' berhasil dihapus")
                        self.load_kegiatan_data()
                    else:
                        QMessageBox.warning(self, "Error", f"Gagal menghapus kegiatan WR:\n{result['data']}")
                        self.log_message.emit(f"Gagal menghapus kegiatan WR: {result['data']}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error menghapus kegiatan:\n{str(e)}")
                    self.log_message.emit(f"Error menghapus kegiatan: {str(e)}")
        else:
            QMessageBox.warning(self, "Peringatan", "Pilih kegiatan terlebih dahulu")

    def export_kegiatan(self):
        """Export kegiatan data to CSV file"""
        if not self.filtered_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data Kegiatan",
            f"data_kegiatan_{datetime.date.today().isoformat()}.csv",
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        'Kategori', 'Nama Kegiatan', 'Sasaran', 'Tujuan', 'Tempat', 'Tanggal', 'Waktu', 'Penanggung Jawab', 'Status', 'Keterangan'
                    ])
                    writer.writeheader()
                    for kegiatan in self.filtered_data:
                        # Support both old and new field names
                        tanggal = kegiatan.get('tanggal') or kegiatan.get('tanggal_mulai', '')
                        waktu = kegiatan.get('waktu') or kegiatan.get('waktu_mulai', '')
                        tempat = kegiatan.get('tempat') or kegiatan.get('lokasi', '')
                        penanggung_jawab = kegiatan.get('penanggung_jawab') or kegiatan.get('penanggungjawab', '')

                        writer.writerow({
                            'Kategori': kegiatan.get('kategori', ''),
                            'Nama Kegiatan': kegiatan.get('nama_kegiatan', ''),
                            'Sasaran': kegiatan.get('sasaran_kegiatan', ''),
                            'Tujuan': kegiatan.get('tujuan_kegiatan', ''),
                            'Tempat': tempat,
                            'Tanggal': tanggal,
                            'Waktu': waktu,
                            'Penanggung Jawab': penanggung_jawab,
                            'Status': self.get_kegiatan_status(kegiatan),
                            'Keterangan': kegiatan.get('keterangan', '')
                        })
                QMessageBox.information(self, "Export Berhasil", f"Data berhasil diekspor ke: {file_path}")
                self.log_message.emit(f"Data kegiatan berhasil diekspor ke {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Gagal mengekspor data: {str(e)}")
                self.log_message.emit(f"Error export data: {str(e)}")

    def update_table(self):
        """Update table with new column order"""
        self.table_widget.setRowCount(0)

        # Nama hari dalam Bahasa Indonesia
        nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

        for row, kegiatan in enumerate(self.filtered_data):
            self.table_widget.insertRow(row)
            self.table_widget.setRowHeight(row, 26)

            # 0. Kategori
            kategori = kegiatan.get('kategori', '') or 'Lainnya'
            kategori_item = QTableWidgetItem(str(kategori))
            kategori_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            # 1. Nama Kegiatan
            nama = kegiatan.get('nama_kegiatan', '') or 'N/A'
            nama_item = QTableWidgetItem(str(nama))
            nama_item.setData(Qt.UserRole, kegiatan)

            # 2. Sasaran Kegiatan
            sasaran = kegiatan.get('sasaran_kegiatan', '') or '-'
            sasaran_item = QTableWidgetItem(str(sasaran))

            # 3. Tujuan Kegiatan
            tujuan = kegiatan.get('tujuan_kegiatan', '') or '-'
            tujuan_item = QTableWidgetItem(str(tujuan))

            # 4. Tempat Kegiatan
            lokasi = kegiatan.get('tempat_kegiatan') or kegiatan.get('lokasi') or kegiatan.get('tempat', '') or 'N/A'
            lokasi_item = QTableWidgetItem(str(lokasi))

            # 5. Tanggal Pelaksanaan (Format: Hari, dd/mm/yyyy)
            tanggal_mulai = kegiatan.get('tanggal_pelaksanaan') or kegiatan.get('tanggal_mulai') or kegiatan.get('tanggal', '') or 'N/A'
            tanggal_formatted = 'N/A'
            if tanggal_mulai and tanggal_mulai != 'N/A':
                try:
                    if 'T' in str(tanggal_mulai):
                        dt = datetime.datetime.fromisoformat(str(tanggal_mulai).replace('Z', '+00:00'))
                    else:
                        dt = datetime.datetime.strptime(str(tanggal_mulai), '%Y-%m-%d')

                    # Format: dd/mm/yyyy
                    tanggal_formatted = dt.strftime('%d/%m/%Y')
                except:
                    tanggal_formatted = str(tanggal_mulai)
            tanggal_item = QTableWidgetItem(tanggal_formatted)
            tanggal_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            # 6. Waktu Pelaksanaan (Format: HH.MM WITA - selesai)
            waktu_mulai = kegiatan.get('waktu_mulai') or kegiatan.get('waktu', '') or 'N/A'
            waktu_selesai = kegiatan.get('waktu_selesai', '')

            waktu_formatted = 'N/A'
            if waktu_mulai and waktu_mulai != 'N/A':
                try:
                    # Remove seconds if present
                    if isinstance(waktu_mulai, str) and len(waktu_mulai) > 5:
                        waktu_mulai = waktu_mulai[:5]

                    # Replace colon with dot for display
                    waktu_display = waktu_mulai.replace(':', '.')

                    if waktu_selesai and waktu_selesai != 'N/A':
                        if isinstance(waktu_selesai, str) and len(waktu_selesai) > 5:
                            waktu_selesai = waktu_selesai[:5]
                        waktu_selesai_display = waktu_selesai.replace(':', '.')
                        waktu_formatted = f"{waktu_display} WITA - {waktu_selesai_display} WITA"
                    else:
                        waktu_formatted = f"{waktu_display} WITA - selesai"
                except:
                    waktu_formatted = str(waktu_mulai)
            waktu_item = QTableWidgetItem(waktu_formatted)
            waktu_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            # 7. Penanggung Jawab
            penanggung_jawab = kegiatan.get('penanggung_jawab') or kegiatan.get('penanggungjawab') or kegiatan.get('nama_lengkap') or kegiatan.get('username', 'Tidak Ada')
            penanggung_jawab_item = QTableWidgetItem(str(penanggung_jawab))

            # 8. User (Nama user yang melakukan input)
            user_name = kegiatan.get('username') or kegiatan.get('user_name') or kegiatan.get('created_by') or 'Tidak Ada'
            user_item = QTableWidgetItem(str(user_name))
            user_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            # 9. Status Kegiatan
            status_db = kegiatan.get('status_kegiatan') or kegiatan.get('status', '') or 'Direncanakan'
            status_db_item = QTableWidgetItem(str(status_db))

            # Ensure status text is always visible by setting alignment and proper styling
            status_db_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            # Color code status berdasarkan status database
            if status_db == "Direncanakan":
                status_db_item.setBackground(QBrush(QColor("#3498db")))
                status_db_item.setForeground(QBrush(QColor("white")))
            elif status_db == "Berlangsung":
                status_db_item.setBackground(QBrush(QColor("#f39c12")))
                status_db_item.setForeground(QBrush(QColor("white")))
            elif status_db == "Selesai":
                status_db_item.setBackground(QBrush(QColor("#2ecc71")))
                status_db_item.setForeground(QBrush(QColor("white")))
            elif status_db == "Dibatalkan":
                status_db_item.setBackground(QBrush(QColor("#e74c3c")))
                status_db_item.setForeground(QBrush(QColor("white")))

            # 10. Keterangan
            keterangan = kegiatan.get('keterangan', '') or ''
            keterangan_item = QTableWidgetItem(str(keterangan))

            # Set items ke tabel sesuai urutan baru
            self.table_widget.setItem(row, 0, kategori_item)
            self.table_widget.setItem(row, 1, nama_item)
            self.table_widget.setItem(row, 2, sasaran_item)
            self.table_widget.setItem(row, 3, tujuan_item)
            self.table_widget.setItem(row, 4, lokasi_item)
            self.table_widget.setItem(row, 5, tanggal_item)
            self.table_widget.setItem(row, 6, waktu_item)
            self.table_widget.setItem(row, 7, penanggung_jawab_item)
            self.table_widget.setItem(row, 8, user_item)
            self.table_widget.setItem(row, 9, status_db_item)
            self.table_widget.setItem(row, 10, keterangan_item)

    def update_calendar_indicators(self):
        """Update calendar to mark dates that have kegiatan"""
        # Get all dates from kegiatan_data
        kegiatan_dates = set()

        for kegiatan in self.kegiatan_data:
            # Support both old (tanggal) and new (tanggal_mulai) fields
            tanggal_str = kegiatan.get('tanggal_pelaksanaan') or kegiatan.get('tanggal_mulai') or kegiatan.get('tanggal', '')
            if tanggal_str:
                try:
                    if 'T' in str(tanggal_str):
                        tanggal_date = datetime.datetime.fromisoformat(str(tanggal_str).replace('Z', '+00:00')).date()
                    else:
                        tanggal_date = datetime.datetime.strptime(str(tanggal_str), '%Y-%m-%d').date()
                    kegiatan_dates.add(tanggal_date)
                except:
                    pass

        # Create a custom formatting for calendar
        # Mark dates with kegiatan by making them bold
        if hasattr(self.calendar, 'setDateTextFormat'):
            from PyQt5.QtGui import QTextCharFormat

            # Default format (for dates without kegiatan)
            default_format = QTextCharFormat()

            # Format for dates with kegiatan (bold)
            kegiatan_format = QTextCharFormat()
            kegiatan_format.setFontWeight(700)  # Bold

            # Current calendar month
            current_date = self.calendar.selectedDate().toPyDate()
            current_month = current_date.month()
            current_year = current_date.year()

            # Apply formatting
            for day in range(1, 32):
                try:
                    date_obj = datetime.date(current_year, current_month, day)
                    q_date = QDate(date_obj.year, date_obj.month, date_obj.day)

                    if date_obj in kegiatan_dates:
                        self.calendar.setDateTextFormat(q_date, kegiatan_format)
                    else:
                        self.calendar.setDateTextFormat(q_date, default_format)
                except ValueError:
                    # Invalid day for this month
                    pass

    def get_kegiatan_status(self, kegiatan):
        """Determine status of kegiatan based on date/time"""
        try:
            today = datetime.date.today()

            # Support both old (tanggal) and new (tanggal_mulai) fields
            tanggal_str = kegiatan.get('tanggal') or kegiatan.get('tanggal_mulai', '')
            if not tanggal_str:
                return "Unknown"

            if 'T' in tanggal_str:
                kegiatan_date = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00')).date()
            else:
                kegiatan_date = datetime.datetime.strptime(tanggal_str, '%Y-%m-%d').date()

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
            nama = (kegiatan.get('nama_kegiatan', '') or '').lower()
            # Support both old (tempat) and new (lokasi) fields
            tempat = (kegiatan.get('tempat') or kegiatan.get('lokasi', '') or '').lower()

            if search_text and search_text not in nama and search_text not in tempat:
                continue

            # Category filter
            kategori = kegiatan.get('kategori', '') or 'Lainnya'
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
            # Support multiple field names for date
            tanggal = kegiatan.get('tanggal_pelaksanaan') or kegiatan.get('tanggal_mulai') or kegiatan.get('tanggal', '')
            if tanggal and selected_date in tanggal:
                filtered_for_date.append(kegiatan)

        if filtered_for_date:
            self.filtered_data = filtered_for_date
            self.update_table()
            self.update_statistics()
            QMessageBox.information(self, "Kegiatan",
                f"Ditemukan {len(filtered_for_date)} kegiatan pada {date.toString('dd/MM/yyyy')}")
        else:
            self.filtered_data = []
            self.update_table()
            self.update_statistics()
            QMessageBox.information(self, "Kegiatan",
                f"Tidak ada kegiatan pada {date.toString('dd/MM/yyyy')}")


    def update_statistics(self):
        """Update statistics labels"""
        today = datetime.date.today()

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
