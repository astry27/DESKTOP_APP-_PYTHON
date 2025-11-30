# Path: client/components/kegiatan_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QPushButton, QFrame,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox,
                             QTextEdit, QDialog, QFormLayout, QDateEdit, QTimeEdit,
                             QFileDialog, QAbstractItemView, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTime, QSize, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QBrush, QPainter
import os
import datetime
import csv

try:
    from reportlab.lib.pagesizes import letter, A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

class WordWrapHeaderView(QHeaderView):
    """Custom header view with word wrap and center alignment support"""
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        # Set minimum height to ensure header is always visible
        self.setMinimumHeight(35)
        # Ensure header is visible on resize
        self.setSectionResizeMode(QHeaderView.Interactive)

    def sectionSizeFromContents(self, logicalIndex):
        """Calculate section size based on wrapped text"""
        if self.model():
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                width = self.sectionSize(logicalIndex)
                if width <= 0:
                    width = self.defaultSectionSize()

                # Create font metrics with bold font
                font = self.font()
                font.setBold(True)
                font.setPointSize(max(font.pointSize(), 9))  # Ensure minimum font size
                from PyQt5.QtGui import QFontMetrics
                fm = QFontMetrics(font)

                # Calculate text rect with word wrap
                rect = fm.boundingRect(0, 0, width - 10, 2000,
                                      Qt.AlignCenter | Qt.TextWordWrap, str(text))

                # Return size with adequate padding (minimum 35px height)
                return QSize(width, max(rect.height() + 16, 35))

        return super().sectionSizeFromContents(logicalIndex)

    def paintSection(self, painter, rect, logicalIndex):
        """Paint section with word wrap and center alignment - always visible"""
        painter.save()

        # Ensure rect has minimum height
        if rect.height() < 35:
            rect.setHeight(35)

        # Draw background with consistent, visible color
        bg_color = QColor(242, 242, 242)  # #f2f2f2 - light gray background
        painter.fillRect(rect, bg_color)

        # Draw borders for Excel-like appearance
        border_color = QColor(180, 180, 180)  # Darker border for better visibility
        painter.setPen(border_color)
        # Right border
        painter.drawLine(rect.topRight(), rect.bottomRight())
        # Bottom border
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        if self.model():
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                # Setup font with proper size
                font = self.font()
                font.setBold(True)
                font.setPointSize(max(font.pointSize(), 9))  # Ensure readable size
                painter.setFont(font)

                # Text color - darker for better contrast and visibility
                text_color = QColor(30, 30, 30)  # Very dark gray, almost black
                painter.setPen(text_color)

                # Draw text with word wrap and center alignment
                # Add padding to ensure text doesn't touch borders
                text_rect = rect.adjusted(6, 6, -6, -6)

                # Draw text with proper alignment and wrapping
                painter.drawText(text_rect,
                               Qt.AlignCenter | Qt.AlignVCenter | Qt.TextWordWrap,
                               str(text))

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
        self.kategori_input.addItem("-- Pilih Kategori --")
        self.kategori_input.addItems([
            "Misa", "Doa", "Sosial", "Pendidikan",
            "Ibadah", "Katekese", "Rohani",
            "Administratif", "Lainnya"
        ])
        self.kategori_input.setCurrentIndex(0)
        self.kategori_input.setMinimumHeight(32)
        # Style placeholder item dengan warna abu-abu
        self.kategori_input.setStyleSheet("""
            QComboBox {
                padding: 4px;
            }
        """)
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
        self.status_input.addItem("-- Pilih Status --")
        self.status_input.addItems([
            "Direncanakan", "Berlangsung", "Selesai", "Dibatalkan"
        ])
        self.status_input.setCurrentIndex(0)
        self.status_input.setMinimumHeight(32)
        # Style placeholder item dengan warna abu-abu
        self.status_input.setStyleSheet("""
            QComboBox {
                padding: 4px;
            }
        """)
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
        if self.kategori_input.currentIndex() == 0 or self.kategori_input.currentText().startswith("--"):
            QMessageBox.warning(self, "Validasi", "Kategori harus dipilih")
            return False

        if not self.nama_input.text().strip():
            QMessageBox.warning(self, "Validasi", "Nama kegiatan tidak boleh kosong")
            return False

        if not self.lokasi_input.text().strip():
            QMessageBox.warning(self, "Validasi", "Tempat kegiatan tidak boleh kosong")
            return False

        if not self.penanggungjawab_input.text().strip():
            QMessageBox.warning(self, "Validasi", "Penanggung jawab tidak boleh kosong")
            return False

        if self.status_input.currentIndex() == 0 or self.status_input.currentText().startswith("--"):
            QMessageBox.warning(self, "Validasi", "Status kegiatan harus dipilih")
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
        try:
            result = self.api_client.get_my_kegiatan_wr()

            if result.get('success'):
                response_data = result.get('data')

                # API mengembalikan list langsung
                if isinstance(response_data, list):
                    self.kegiatan_data = response_data
                else:
                    self.kegiatan_data = []
            else:
                error_msg = result.get('data', 'Unknown error')
                self.log_message.emit(f"Gagal memuat kegiatan WR: {error_msg}")
                self.kegiatan_data = []

            self.filtered_data = self.kegiatan_data.copy()
            self.update_table()
            self.log_message.emit(f"Data kegiatan WR berhasil dimuat: {len(self.kegiatan_data)} kegiatan")

        except Exception as e:
            import traceback
            self.log_message.emit(f"Error loading kegiatan WR data: {str(e)}")
            print(f"[DEBUG] kegiatan_component load_user_kegiatan_data error: {traceback.format_exc()}")
            self.kegiatan_data = []
            self.filtered_data = []
            self.update_table()

    def load_kegiatan_data(self):
        """Alias for load_user_kegiatan_data to maintain compatibility"""
        self.load_user_kegiatan_data()

    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Filter
        filter_group = self.create_filter()
        layout.addWidget(filter_group)

        # Table
        table_widget = self.create_table()
        layout.addWidget(table_widget, 1)

        # Action buttons
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout, 0)

    def create_header(self):
        """Create header with title"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                padding: 10px 0px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 10, 0)

        title = QLabel("Kegiatan Wilayah Rohani")
        title_font = QFont("Arial", 18, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        add_button = QPushButton("Tambah Kegiatan")
        # Add icon with fallback
        try:
            icon = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'add.png'))
            if not icon.isNull():
                add_button.setIcon(icon)
                add_button.setIconSize(QSize(16, 16))
        except:
            pass

        add_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        add_button.clicked.connect(self.add_kegiatan)
        header_layout.addWidget(add_button)

        return header

    def create_filter(self):
        """Create filter section"""
        filter_group = QGroupBox()
        filter_layout = QHBoxLayout(filter_group)

        # Kategori filter
        kategori_label = QLabel("Filter Kategori:")
        filter_layout.addWidget(kategori_label)

        self.kategori_filter = QComboBox()
        self.kategori_filter.addItems([
            "Semua", "Misa", "Doa", "Sosial", "Pendidikan",
            "Ibadah", "Katekese", "Rohani", "Administratif", "Lainnya"
        ])
        self.kategori_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.kategori_filter)

        filter_layout.addStretch()

        return filter_group

    def create_table(self):
        """Create table for kegiatan with proper header visibility"""
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

        self.table_widget = QTableWidget(0, 11)

        # Set custom header
        custom_header = WordWrapHeaderView(Qt.Horizontal, self.table_widget)
        self.table_widget.setHorizontalHeader(custom_header)

        self.table_widget.setHorizontalHeaderLabels([
            "Kategori", "Nama Kegiatan", "Sasaran Kegiatan", "Tujuan Kegiatan",
            "Tempat Kegiatan", "Tanggal Pelaksanaan",
            "Waktu Pelaksanaan", "Penanggung Jawab", "User", "Status Kegiatan", "Keterangan"
        ])

        # Apply table styling
        self.apply_table_style()

        # Set column widths
        self.table_widget.setColumnWidth(0, 100)   # Kategori
        self.table_widget.setColumnWidth(1, 150)   # Nama Kegiatan
        self.table_widget.setColumnWidth(2, 130)   # Sasaran Kegiatan
        self.table_widget.setColumnWidth(3, 130)   # Tujuan Kegiatan
        self.table_widget.setColumnWidth(4, 120)   # Tempat Kegiatan
        self.table_widget.setColumnWidth(5, 120)   # Tanggal Pelaksanaan
        self.table_widget.setColumnWidth(6, 120)   # Waktu Pelaksanaan
        self.table_widget.setColumnWidth(7, 100)   # Penanggung Jawab
        self.table_widget.setColumnWidth(8, 80)    # User
        self.table_widget.setColumnWidth(9, 100)   # Status Kegiatan
        self.table_widget.setColumnWidth(10, 150)  # Keterangan

        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        header.sectionResized.connect(self.update_header_height)

        # Double click to edit
        self.table_widget.itemDoubleClicked.connect(self.edit_kegiatan)

        table_layout.addWidget(self.table_widget)

        QTimer.singleShot(100, self.update_header_height)

        return table_container

    def update_header_height(self):
        """Update header height - ensure always visible"""
        if hasattr(self, 'table_widget'):
            header = self.table_widget.horizontalHeader()
            # Force minimum height to ensure visibility
            min_height = 35
            header.setMinimumHeight(min_height)
            max_height = min_height

            # Calculate required height for each section
            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                if size.height() > max_height:
                    max_height = size.height()

            # Set header height to accommodate tallest section with minimum guarantee
            final_height = max(max_height, min_height)
            header.setFixedHeight(final_height)

            # Force header repaint to ensure visibility
            header.viewport().update()

    def apply_table_style(self):
        """Apply table styling with proper header visibility"""
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)
        self.table_widget.horizontalHeader().setFont(header_font)

        # Header with bold text, center alignment, and word wrap
        # IMPORTANT: Ensure header is always visible with adequate height
        self.table_widget.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #b4b4b4;
                border-right: 1px solid #b4b4b4;
                padding: 8px 6px;
                font-weight: bold;
                color: #1e1e1e;
                min-height: 35px;
            }
        """)

        header = self.table_widget.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        # CRITICAL: Set minimum height to ensure visibility when maximized
        header.setMinimumHeight(35)
        header.setDefaultSectionSize(100)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(500)

        self.table_widget.setStyleSheet("""
            QTableWidget {
                gridline-color: #d4d4d4;
                background-color: white;
                border: 1px solid #d4d4d4;
                selection-background-color: #cce7ff;
                font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
                outline: none;
                color: black;
            }
            QTableWidget::item {
                border: none;
                padding: 4px 6px;
                min-height: 18px;
                color: black;
            }
            QTableWidget::item:selected {
                background-color: #cce7ff;
                color: black;
            }
            QTableWidget::item:focus {
                border: 2px solid #0078d4;
                background-color: white;
                color: black;
            }
        """)

        self.table_widget.verticalHeader().setDefaultSectionSize(24)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table_widget.setAlternatingRowColors(False)
        self.table_widget.verticalHeader().setVisible(True)
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
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.table_widget.setMinimumHeight(200)

    def create_action_buttons(self):
        """Create action buttons layout"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.setSpacing(5)

        # View detail button
        detail_button = QPushButton(" Lihat Detail")
        detail_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        try:
            detail_icon = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'view.png'))
            if not detail_icon.isNull():
                detail_button.setIcon(detail_icon)
                detail_button.setIconSize(QSize(14, 14))
        except:
            pass
        detail_button.clicked.connect(self.view_kegiatan)
        button_layout.addWidget(detail_button)

        # Edit button
        edit_button = QPushButton(" Edit")
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
        """)
        try:
            edit_icon = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'edit.png'))
            if not edit_icon.isNull():
                edit_button.setIcon(edit_icon)
                edit_button.setIconSize(QSize(14, 14))
        except:
            pass
        edit_button.clicked.connect(self.edit_kegiatan)
        button_layout.addWidget(edit_button)

        # Delete button
        delete_button = QPushButton(" Hapus")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        try:
            delete_icon = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'delete.png'))
            if not delete_icon.isNull():
                delete_button.setIcon(delete_icon)
                delete_button.setIconSize(QSize(14, 14))
        except:
            pass
        delete_button.clicked.connect(self.delete_kegiatan)
        button_layout.addWidget(delete_button)

        # Export CSV button
        export_csv_button = QPushButton(" .csv")
        export_csv_button.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
            QPushButton:pressed {
                background-color: #117a65;
            }
        """)
        try:
            export_icon = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'export.png'))
            if not export_icon.isNull():
                export_csv_button.setIcon(export_icon)
                export_csv_button.setIconSize(QSize(14, 14))
        except:
            pass
        export_csv_button.clicked.connect(self.export_kegiatan)
        button_layout.addWidget(export_csv_button)

        # Export PDF button
        export_pdf_button = QPushButton(" .pdf")
        export_pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        try:
            pdf_icon = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'pdf.png'))
            if not pdf_icon.isNull():
                export_pdf_button.setIcon(pdf_icon)
                export_pdf_button.setIconSize(QSize(14, 14))
        except:
            pass
        export_pdf_button.clicked.connect(self.export_kegiatan_pdf)
        button_layout.addWidget(export_pdf_button)

        button_layout.addStretch()

        return button_layout

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
            # Validate data
            if not dialog.validate():
                return

            data = dialog.get_data()

            try:
                self.log_message.emit(f"[DEBUG] Mengirim data: {data}")
                result = self.api_client.add_kegiatan_wr(data)
                self.log_message.emit(f"[DEBUG] Response add_kegiatan: success={result.get('success')}")

                if result.get("success"):
                    # Reload data to refresh the table
                    self.log_message.emit("✓ Kegiatan berhasil ditambahkan, me-reload data...")
                    self.load_kegiatan_data()

                    # Show success message
                    QMessageBox.information(self, "Sukses", "Kegiatan berhasil ditambahkan dan tabel telah diperbarui")
                    self.log_message.emit(f"✓ Kegiatan ditambahkan: {data['nama_kegiatan']}")
                    self.data_updated.emit()
                else:
                    error_msg = result.get('data', 'Unknown error')
                    QMessageBox.critical(self, "Error", f"Gagal menambah kegiatan:\n{error_msg}")
                    self.log_message.emit(f"✗ Gagal menambah kegiatan: {error_msg}")

            except Exception as e:
                import traceback
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
                self.log_message.emit(f"✗ Error add kegiatan: {str(e)}")
                self.log_message.emit(f"[DEBUG] Traceback: {traceback.format_exc()}")

    def view_kegiatan(self):
        """View selected kegiatan"""
        current_row = self.table_widget.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_data):
            kegiatan = self.filtered_data[current_row]

            # Create detail dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Detail Kegiatan WR")
            dialog.setMinimumSize(550, 500)

            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)

            # Form layout (read-only)
            form_layout = QFormLayout()
            form_layout.setSpacing(8)
            form_layout.setHorizontalSpacing(15)
            form_layout.setVerticalSpacing(8)

            # Kategori
            kategori_label = QLabel(kegiatan.get('kategori', 'N/A'))
            kategori_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
            form_layout.addRow("Kategori:", kategori_label)

            # Nama Kegiatan
            nama_label = QLabel(kegiatan.get('nama_kegiatan', 'N/A'))
            nama_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
            nama_label.setWordWrap(True)
            form_layout.addRow("Nama Kegiatan:", nama_label)

            # Tanggal Pelaksanaan
            tanggal = kegiatan.get('tanggal_pelaksanaan') or kegiatan.get('tanggal_mulai') or kegiatan.get('tanggal', 'N/A')
            tanggal_label = QLabel(str(tanggal))
            tanggal_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
            form_layout.addRow("Tanggal Pelaksanaan:", tanggal_label)

            # Waktu Mulai
            waktu = kegiatan.get('waktu_mulai') or kegiatan.get('waktu', 'N/A')
            waktu_label = QLabel(str(waktu))
            waktu_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
            form_layout.addRow("Waktu Mulai:", waktu_label)

            # Tempat Kegiatan
            tempat = kegiatan.get('tempat_kegiatan') or kegiatan.get('lokasi') or kegiatan.get('tempat', 'N/A')
            tempat_label = QLabel(str(tempat))
            tempat_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
            tempat_label.setWordWrap(True)
            form_layout.addRow("Tempat Kegiatan:", tempat_label)

            # Sasaran Kegiatan
            sasaran_label = QLabel(kegiatan.get('sasaran_kegiatan', 'N/A'))
            sasaran_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
            sasaran_label.setWordWrap(True)
            form_layout.addRow("Sasaran Kegiatan:", sasaran_label)

            # Tujuan Kegiatan
            tujuan_label = QLabel(kegiatan.get('tujuan_kegiatan', 'N/A'))
            tujuan_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
            tujuan_label.setWordWrap(True)
            form_layout.addRow("Tujuan Kegiatan:", tujuan_label)

            # Penanggung Jawab
            pic = kegiatan.get('penanggung_jawab') or kegiatan.get('penanggungjawab', 'N/A')
            pic_label = QLabel(str(pic))
            pic_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
            form_layout.addRow("Penanggung Jawab:", pic_label)

            # Status Kegiatan
            status = kegiatan.get('status_kegiatan') or kegiatan.get('status', 'Direncanakan')
            status_label = QLabel(str(status))
            status_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
            form_layout.addRow("Status Kegiatan:", status_label)

            # Keterangan
            keterangan_label = QLabel(kegiatan.get('keterangan', ''))
            keterangan_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
            keterangan_label.setWordWrap(True)
            form_layout.addRow("Keterangan:", keterangan_label)

            layout.addLayout(form_layout)
            layout.addStretch()

            # Close button
            close_button = QPushButton("Tutup")
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #bdc3c7;
                }
            """)
            close_button.clicked.connect(dialog.accept)

            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(close_button)
            layout.addLayout(button_layout)

            dialog.exec_()
        else:
            QMessageBox.warning(self, "Peringatan", "Pilih kegiatan terlebih dahulu")

    def edit_kegiatan(self):
        """Edit selected kegiatan"""
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih kegiatan yang akan diedit")
            return

        if current_row >= len(self.filtered_data):
            QMessageBox.warning(self, "Warning", "Data kegiatan tidak valid")
            return

        kegiatan = self.filtered_data[current_row]

        dialog = KegiatanDialog(self, kegiatan)
        if dialog.exec_() == QDialog.Accepted:
            # Validate data
            if not dialog.validate():
                return

            data = dialog.get_data()

            try:
                self.log_message.emit(f"[DEBUG] Update data: {data}")
                result = self.api_client.update_kegiatan_wr(kegiatan.get('id_kegiatan_wr'), data)
                self.log_message.emit(f"[DEBUG] Response update: success={result.get('success')}")

                if result.get("success"):
                    # Reload data to refresh the table
                    self.log_message.emit("✓ Kegiatan berhasil diperbarui, me-reload data...")
                    self.load_kegiatan_data()

                    QMessageBox.information(self, "Sukses", "Kegiatan berhasil diperbarui dan tabel telah diperbarui")
                    self.log_message.emit(f"✓ Kegiatan diperbarui: {data['nama_kegiatan']}")
                    self.data_updated.emit()
                else:
                    error_msg = result.get('data', 'Unknown error')
                    QMessageBox.critical(self, "Error", f"Gagal update kegiatan:\n{error_msg}")
                    self.log_message.emit(f"✗ Gagal update kegiatan: {error_msg}")

            except Exception as e:
                import traceback
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
                self.log_message.emit(f"✗ Error edit kegiatan: {str(e)}")
                self.log_message.emit(f"[DEBUG] Traceback: {traceback.format_exc()}")

    def delete_kegiatan(self):
        """Delete selected kegiatan"""
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih kegiatan yang akan dihapus")
            return

        if current_row >= len(self.filtered_data):
            QMessageBox.warning(self, "Warning", "Data kegiatan tidak valid")
            return

        kegiatan = self.filtered_data[current_row]

        reply = QMessageBox.question(self, "Konfirmasi",
                                    f"Yakin ingin menghapus kegiatan '{kegiatan.get('nama_kegiatan')}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.log_message.emit(f"[DEBUG] Delete kegiatan ID: {kegiatan.get('id_kegiatan_wr')}")
                result = self.api_client.delete_kegiatan_wr(kegiatan.get('id_kegiatan_wr'))
                self.log_message.emit(f"[DEBUG] Response delete: success={result.get('success')}")

                if result.get("success"):
                    # Reload data to refresh the table
                    self.log_message.emit("✓ Kegiatan berhasil dihapus, me-reload data...")
                    self.load_kegiatan_data()

                    QMessageBox.information(self, "Sukses", "Kegiatan berhasil dihapus dan tabel telah diperbarui")
                    self.log_message.emit(f"✓ Kegiatan dihapus: {kegiatan.get('nama_kegiatan')}")
                    self.data_updated.emit()
                else:
                    error_msg = result.get('data', 'Unknown error')
                    QMessageBox.critical(self, "Error", f"Gagal hapus kegiatan:\n{error_msg}")
                    self.log_message.emit(f"✗ Gagal hapus kegiatan: {error_msg}")

            except Exception as e:
                import traceback
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
                self.log_message.emit(f"✗ Error delete kegiatan: {str(e)}")
                self.log_message.emit(f"[DEBUG] Traceback: {traceback.format_exc()}")

    def export_kegiatan(self):
        """Export data to CSV"""
        if not self.filtered_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Kegiatan", "kegiatan_wr.csv", "CSV Files (*.csv)"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "Kategori", "Nama Kegiatan", "Tanggal", "Waktu", "Tempat", "Sasaran", "Tujuan", "PIC", "Status", "Keterangan"
                ])
                writer.writeheader()

                for kegiatan in self.filtered_data:
                    # Format tanggal ke dd/mm/yyyy untuk export
                    tanggal_mulai = kegiatan.get('tanggal_pelaksanaan') or kegiatan.get('tanggal_mulai') or kegiatan.get('tanggal', '')
                    if tanggal_mulai:
                        try:
                            if 'T' in str(tanggal_mulai):
                                dt = datetime.datetime.fromisoformat(str(tanggal_mulai).replace('Z', '+00:00'))
                            else:
                                dt = datetime.datetime.strptime(str(tanggal_mulai), '%Y-%m-%d')
                            tanggal_display = dt.strftime('%d/%m/%Y')
                        except:
                            tanggal_display = str(tanggal_mulai)
                    else:
                        tanggal_display = ''

                    # Format waktu
                    waktu = kegiatan.get('waktu_mulai') or kegiatan.get('waktu', '')
                    waktu_display = waktu[:5] if waktu and len(waktu) >= 5 else waktu

                    # Format tempat
                    tempat = kegiatan.get('tempat_kegiatan') or kegiatan.get('lokasi') or kegiatan.get('tempat', '')

                    # Format penanggung jawab
                    penanggung_jawab = kegiatan.get('penanggung_jawab') or kegiatan.get('penanggungjawab', '')

                    # Status
                    status = kegiatan.get('status_kegiatan') or kegiatan.get('status', '')

                    writer.writerow({
                        "Kategori": kegiatan.get('kategori', ''),
                        "Nama Kegiatan": kegiatan.get('nama_kegiatan', ''),
                        "Tanggal": tanggal_display,
                        "Waktu": waktu_display,
                        "Tempat": tempat,
                        "Sasaran": kegiatan.get('sasaran_kegiatan', ''),
                        "Tujuan": kegiatan.get('tujuan_kegiatan', ''),
                        "PIC": penanggung_jawab,
                        "Status": status,
                        "Keterangan": kegiatan.get('keterangan', '')
                    })

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data diekspor ke: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error export: {str(e)}")

    def export_kegiatan_pdf(self):
        """Export data to PDF with proper text wrapping and column fitting"""
        if not self.filtered_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor")
            return

        if not HAS_REPORTLAB:
            QMessageBox.critical(self, "Error",
                "Perpustakaan reportlab tidak terinstall.\n"
                "Silakan jalankan: pip install reportlab")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Kegiatan ke PDF", "kegiatan_wr.pdf", "PDF Files (*.pdf)"
        )

        if not filename:
            return

        try:
            # Create PDF document with landscape orientation for better fit
            doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
                                   rightMargin=15, leftMargin=15,
                                   topMargin=15, bottomMargin=15)

            # Container for elements
            elements = []

            # Add title
            style = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=style['Heading1'],
                fontSize=14,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=10,
                alignment=TA_CENTER
            )
            elements.append(Paragraph("Kegiatan Wilayah Rohani", title_style))
            elements.append(Spacer(1, 0.15*inch))

            # Create cell style for wrapping text
            cell_style = ParagraphStyle(
                'CellStyle',
                parent=style['Normal'],
                fontSize=7.5,
                leading=9,
                alignment=TA_LEFT,
                wordWrap='CJK'
            )

            # Prepare table data with wrapped paragraphs
            table_data = []

            # Header row
            headers = ["Kategori", "Nama Kegiatan", "Tanggal", "Waktu", "Tempat", "Sasaran",
                      "Tujuan", "PIC", "Status", "Keterangan"]
            table_data.append(headers)

            for kegiatan in self.filtered_data:
                # Format tanggal ke dd/mm/yyyy
                tanggal_mulai = kegiatan.get('tanggal_pelaksanaan') or kegiatan.get('tanggal_mulai') or kegiatan.get('tanggal', '')
                if tanggal_mulai:
                    try:
                        if 'T' in str(tanggal_mulai):
                            dt = datetime.datetime.fromisoformat(str(tanggal_mulai).replace('Z', '+00:00'))
                        else:
                            dt = datetime.datetime.strptime(str(tanggal_mulai), '%Y-%m-%d')
                        tanggal_display = dt.strftime('%d/%m/%Y')
                    except:
                        tanggal_display = str(tanggal_mulai)
                else:
                    tanggal_display = ''

                # Format waktu
                waktu = kegiatan.get('waktu_mulai') or kegiatan.get('waktu', '')
                waktu_display = waktu[:5] if waktu and len(waktu) >= 5 else waktu

                # Create wrapped paragraphs for long text fields
                kategori_text = str(kegiatan.get('kategori', '-'))
                nama_text = str(kegiatan.get('nama_kegiatan', '-'))
                tempat_text = str(kegiatan.get('tempat_kegiatan') or kegiatan.get('lokasi') or kegiatan.get('tempat', '-'))
                sasaran_text = str(kegiatan.get('sasaran_kegiatan', '-'))
                tujuan_text = str(kegiatan.get('tujuan_kegiatan', '-'))
                pic_text = str(kegiatan.get('penanggung_jawab', '-'))
                status_text = str(kegiatan.get('status_kegiatan', '-'))
                keterangan_text = str(kegiatan.get('keterangan', '-'))

                # Wrap text in Paragraph objects for proper text handling
                row = [
                    Paragraph(kategori_text, cell_style),
                    Paragraph(nama_text, cell_style),
                    Paragraph(tanggal_display, cell_style),
                    Paragraph(waktu_display, cell_style),
                    Paragraph(tempat_text, cell_style),
                    Paragraph(sasaran_text, cell_style),
                    Paragraph(tujuan_text, cell_style),
                    Paragraph(pic_text, cell_style),
                    Paragraph(status_text, cell_style),
                    Paragraph(keterangan_text, cell_style)
                ]
                table_data.append(row)

            # Create table with optimized column widths for landscape
            # Landscape A4: ~11 inches wide, minus margins = ~10.5 inches available
            table = Table(table_data, colWidths=[
                0.8*inch,   # Kategori
                1.2*inch,   # Nama Kegiatan
                0.9*inch,   # Tanggal
                0.8*inch,   # Waktu
                1.0*inch,   # Tempat
                1.0*inch,   # Sasaran
                1.0*inch,   # Tujuan
                0.9*inch,   # PIC
                0.8*inch,   # Status
                1.2*inch    # Keterangan
            ], splitByRow=True)

            # Style table with better formatting
            table_style = TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),

                # Data rows with proper alignment and padding
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7.5),

                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),

                # Grid and padding
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),

                # Set minimum row height for text wrapping
                ('MINHEIGHT', (0, 1), (-1, -1), 25),
            ])

            table.setStyle(table_style)
            elements.append(table)

            # Add summary
            elements.append(Spacer(1, 0.15*inch))
            summary_text = f"Total Kegiatan: {len(self.filtered_data)} | Tanggal Export: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
            summary_style = ParagraphStyle(
                'Summary',
                parent=style['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                alignment=TA_LEFT
            )
            elements.append(Paragraph(summary_text, summary_style))

            # Build PDF
            doc.build(elements)

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}\n\nFile PDF dapat dibuka dan dicetak.")
            self.log_message.emit(f"Data PDF diekspor ke: {filename}")

            # Try to open the PDF file
            import subprocess
            import sys
            try:
                if sys.platform == 'win32':
                    os.startfile(filename)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', filename])
                else:  # Linux
                    subprocess.Popen(['xdg-open', filename])
            except Exception as e:
                self.log_message.emit(f"[DEBUG] Tidak dapat membuka PDF otomatis: {e}")

        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error", f"Error export PDF: {str(e)}")
            self.log_message.emit(f"[DEBUG] Error PDF: {traceback.format_exc()}")

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

    def filter_data(self):
        """Filter data berdasarkan kategori"""
        kategori = self.kategori_filter.currentText()

        filtered = []
        for kegiatan in self.kegiatan_data:
            # Filter by kategori
            if kategori != "Semua" and kegiatan.get('kategori') != kategori:
                continue

            filtered.append(kegiatan)

        self.populate_table(filtered)

    def populate_table(self, kegiatan_list):
        """Populate table with data"""
        self.filtered_data = kegiatan_list
        self.update_table()

