# Path: client/components/proker_component.py
# Program Kerja WR Component - User can only manage their own program kerja

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QPushButton, QFrame,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox,
                             QTextEdit, QDialog, QFormLayout, QFileDialog,
                             QAbstractItemView, QGroupBox, QMenu, QDateEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QDate
from PyQt5.QtGui import QFont, QColor, QIcon, QBrush, QPainter
import datetime
import csv

try:
    from reportlab.lib.pagesizes import letter, A4
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


class ProkerDetailDialog(QDialog):
    """Dialog untuk melihat detail program kerja WR"""

    def __init__(self, parent=None, proker_data=None):
        super().__init__(parent)
        self.proker_data = proker_data
        self.setup_ui()
        if proker_data:
            self.load_data()

    def setup_ui(self):
        self.setWindowTitle("Detail Program Kerja WR")
        self.setMinimumWidth(650)
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Form layout (read-only)
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(8)

        # Kategori
        self.kategori_label = QLabel()
        self.kategori_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
        form_layout.addRow("Kategori:", self.kategori_label)

        # Tanggal
        self.tanggal_label = QLabel()
        self.tanggal_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
        form_layout.addRow("Waktu Estimasi:", self.tanggal_label)

        # Judul
        self.judul_label = QLabel()
        self.judul_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
        self.judul_label.setWordWrap(True)
        form_layout.addRow("Judul Program:", self.judul_label)

        # Sasaran
        self.sasaran_label = QLabel()
        self.sasaran_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
        self.sasaran_label.setWordWrap(True)
        form_layout.addRow("Sasaran:", self.sasaran_label)

        # PIC
        self.pic_label = QLabel()
        self.pic_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
        form_layout.addRow("PIC:", self.pic_label)

        # Anggaran
        self.anggaran_label = QLabel()
        self.anggaran_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
        form_layout.addRow("Anggaran (Rp):", self.anggaran_label)

        # Sumber Anggaran
        self.sumber_label = QLabel()
        self.sumber_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
        form_layout.addRow("Sumber Anggaran:", self.sumber_label)

        # Keterangan
        self.keterangan_label = QLabel()
        self.keterangan_label.setStyleSheet("padding: 8px; background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 2px;")
        self.keterangan_label.setWordWrap(True)
        form_layout.addRow("Keterangan:", self.keterangan_label)

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
        close_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def load_data(self):
        """Load data for display"""
        if not self.proker_data:
            return

        self.kategori_label.setText(self.proker_data.get('kategori', 'N/A'))

        # Format tanggal ke dd/mm/yyyy
        estimasi_waktu = self.proker_data.get('estimasi_waktu', '')
        if estimasi_waktu:
            try:
                if isinstance(estimasi_waktu, str) and '-' in estimasi_waktu:
                    date_parts = estimasi_waktu.split('-')
                    if len(date_parts) == 3:
                        year, month, day = date_parts
                        tanggal_display = f"{day}/{month}/{year}"
                    else:
                        tanggal_display = estimasi_waktu
                else:
                    tanggal_display = str(estimasi_waktu)
            except:
                tanggal_display = str(estimasi_waktu)
        else:
            tanggal_display = 'N/A'

        self.tanggal_label.setText(tanggal_display)
        self.judul_label.setText(self.proker_data.get('judul', 'N/A'))
        self.sasaran_label.setText(self.proker_data.get('sasaran', 'N/A'))
        self.pic_label.setText(self.proker_data.get('penanggung_jawab', 'N/A'))

        # Format anggaran
        anggaran = self.proker_data.get('anggaran', 0)
        if anggaran:
            try:
                anggaran_val = float(anggaran)
                anggaran_text = f"Rp {anggaran_val:,.0f}".replace(',', '.')
            except:
                anggaran_text = f"Rp {anggaran}"
        else:
            anggaran_text = "Rp 0"

        self.anggaran_label.setText(anggaran_text)
        self.sumber_label.setText(self.proker_data.get('sumber_anggaran', 'N/A'))
        self.keterangan_label.setText(self.proker_data.get('keterangan', ''))


class ProkerDialog(QDialog):
    """Dialog untuk menambah/edit program kerja WR"""

    def __init__(self, parent=None, proker_data=None):
        super().__init__(parent)
        self.proker_data = proker_data
        self.is_edit = proker_data is not None
        self.setup_ui()

        if self.is_edit:
            self.load_data()

    def setup_ui(self):
        self.setWindowTitle("Edit Program Kerja WR" if self.is_edit else "Tambah Program Kerja WR")
        self.setMinimumWidth(650)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(8)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # 1. Kategori
        self.kategori_input = QComboBox()
        self.kategori_input.addItem("-- Pilih Kategori --", "")
        self.kategori_input.addItems([
            "Ibadah", "Doa", "Katekese", "Sosial",
            "Rohani", "Administratif", "Perayaan", "Lainnya"
        ])
        self.kategori_input.setCurrentIndex(0)
        self.kategori_input.setMinimumHeight(32)
        form_layout.addRow("Kategori: *", self.kategori_input)

        # 2. Tanggal Pelaksanaan
        self.tanggal_input = QDateEdit()
        self.tanggal_input.setCalendarPopup(True)
        self.tanggal_input.setDisplayFormat("dd/MM/yyyy")
        self.tanggal_input.setDate(QDate.currentDate())
        self.tanggal_input.setMinimumHeight(32)
        form_layout.addRow("Waktu Estimasi: *", self.tanggal_input)

        # 3. Judul Program Kerja
        self.judul_input = QLineEdit()
        self.judul_input.setPlaceholderText("Masukkan judul program kerja")
        self.judul_input.setMinimumHeight(32)
        form_layout.addRow("Judul Program: *", self.judul_input)

        # 4. Sasaran
        self.sasaran_input = QLineEdit()
        self.sasaran_input.setPlaceholderText("Sasaran/tujuan program atau tokoh yang dituju")
        self.sasaran_input.setMinimumHeight(32)
        form_layout.addRow("Sasaran:", self.sasaran_input)

        # 5. Penanggung Jawab (PIC)
        self.pic_input = QLineEdit()
        self.pic_input.setPlaceholderText("Person In Charge (PIC)")
        self.pic_input.setMinimumHeight(32)
        form_layout.addRow("PIC:", self.pic_input)

        # 6. Anggaran
        self.anggaran_input = QLineEdit()
        self.anggaran_input.setPlaceholderText("Jumlah anggaran dalam Rp (contoh: 1000000)")
        self.anggaran_input.setMinimumHeight(32)
        form_layout.addRow("Anggaran (Rp):", self.anggaran_input)

        # 7. Sumber Anggaran
        self.sumber_input = QComboBox()
        self.sumber_input.addItem("-- Pilih Sumber Anggaran --", "")
        self.sumber_input.addItems([
            "Kas Gereja", "Donasi Jemaat", "Sponsor External",
            "Dana Komisi", "APBG", "Kolekte Khusus", "Lainnya"
        ])
        self.sumber_input.setCurrentIndex(0)
        self.sumber_input.setMinimumHeight(32)
        form_layout.addRow("Sumber Anggaran:", self.sumber_input)

        # 8. Keterangan
        self.keterangan_input = QTextEdit()
        self.keterangan_input.setPlaceholderText("Keterangan lengkap program kerja (opsional)")
        self.keterangan_input.setMinimumHeight(60)
        self.keterangan_input.setMaximumHeight(80)
        form_layout.addRow("Keterangan:", self.keterangan_input)

        layout.addLayout(form_layout)

        # Add required field note
        note_label = QLabel("* Field wajib diisi")
        note_label.setStyleSheet("color: #e74c3c; font-size: 10pt; font-style: italic;")
        layout.addWidget(note_label)

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
                border-radius: 3px;
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
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #bdc3c7;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def load_data(self):
        """Load data for editing"""
        if not self.proker_data:
            return

        # Set kategori - skip placeholder
        kategori = self.proker_data.get('kategori', '')
        if kategori:
            index = self.kategori_input.findText(kategori)
            if index >= 0:
                self.kategori_input.setCurrentIndex(index)

        # Set tanggal from database (format: YYYY-MM-DD or already as date)
        estimasi_waktu = self.proker_data.get('estimasi_waktu', '')
        if estimasi_waktu:
            try:
                # Handle if it's a string date (YYYY-MM-DD)
                if isinstance(estimasi_waktu, str):
                    date_parts = estimasi_waktu.split('-')
                    if len(date_parts) == 3:
                        year, month, day = map(int, date_parts)
                        self.tanggal_input.setDate(QDate(year, month, day))
                # Handle if it's already a date object
                elif hasattr(estimasi_waktu, 'year'):
                    self.tanggal_input.setDate(QDate(estimasi_waktu.year, estimasi_waktu.month, estimasi_waktu.day))
            except:
                # If parsing fails, use current date
                self.tanggal_input.setDate(QDate.currentDate())

        self.judul_input.setText(self.proker_data.get('judul', ''))
        self.sasaran_input.setText(self.proker_data.get('sasaran', ''))
        self.pic_input.setText(self.proker_data.get('penanggung_jawab', ''))

        anggaran = self.proker_data.get('anggaran', '')
        if anggaran:
            self.anggaran_input.setText(str(anggaran))

        # Set sumber anggaran - skip placeholder
        sumber = self.proker_data.get('sumber_anggaran', '')
        if sumber:
            index = self.sumber_input.findText(sumber)
            if index >= 0:
                self.sumber_input.setCurrentIndex(index)

        self.keterangan_input.setText(self.proker_data.get('keterangan', ''))

    def get_data(self):
        """Get form data"""
        try:
            anggaran = float(self.anggaran_input.text()) if self.anggaran_input.text() else 0
        except ValueError:
            anggaran = 0

        # Get kategori (skip placeholder)
        kategori = self.kategori_input.currentText()
        if kategori.startswith("--"):
            kategori = ""

        # Get tanggal in YYYY-MM-DD format for database
        tanggal = self.tanggal_input.date().toString("yyyy-MM-dd")

        # Get sumber anggaran (skip placeholder)
        sumber = self.sumber_input.currentText()
        if sumber.startswith("--"):
            sumber = ""

        return {
            'kategori': kategori,
            'estimasi_waktu': tanggal,  # Now sends date in YYYY-MM-DD format
            'judul': self.judul_input.text().strip(),
            'sasaran': self.sasaran_input.text().strip(),
            'penanggung_jawab': self.pic_input.text().strip(),
            'anggaran': anggaran,
            'sumber_anggaran': sumber,
            'keterangan': self.keterangan_input.toPlainText().strip()
        }

    def validate_data(self):
        """Validate form data"""
        errors = []

        # Check required fields
        if not self.judul_input.text().strip():
            errors.append("Judul program harus diisi")

        kategori = self.kategori_input.currentText()
        if not kategori or kategori.startswith("--"):
            errors.append("Kategori harus dipilih")

        # Tanggal is always valid (QDateEdit always has a date)
        # But we can check if it's a valid future/past date if needed
        # For now, any date is acceptable

        return errors


class ProkerComponent(QWidget):
    """Component untuk Program Kerja WR - User dapat mengelola data mereka sendiri saja"""

    data_updated = pyqtSignal()
    log_message = pyqtSignal(str)

    def __init__(self, parent=None, api_client=None, current_user=None):
        super().__init__(parent)
        self.api_client = api_client
        self.current_user = current_user
        self.proker_list = []
        self.setup_ui()
        self.load_data()

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

        title = QLabel("Program Kerja Wilayah Rohani")
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

        add_button = QPushButton("Tambah Program Kerja")
        # Add icon with fallback
        try:
            icon = QIcon("client/assets/add.png")
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
        add_button.clicked.connect(self.add_proker)
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
            "Semua", "Ibadah", "Doa", "Katekese", "Sosial",
            "Rohani", "Administratif", "Perayaan", "Lainnya"
        ])
        self.kategori_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.kategori_filter)

        # Period filter (Year/Month)
        period_label = QLabel("Filter Periode:")
        filter_layout.addWidget(period_label)

        self.period_filter = QComboBox()
        # Populate with current year and nearby years
        current_year = QDate.currentDate().year()
        self.period_filter.addItem("Semua Periode", "all")
        for year in range(current_year - 2, current_year + 3):
            for month in range(1, 13):
                month_name = QDate(year, month, 1).toString("MMMM yyyy")
                self.period_filter.addItem(month_name, f"{year}-{month:02d}")
        self.period_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.period_filter)

        filter_layout.addStretch()

        return filter_group

    def create_table(self):
        """Create table for program kerja"""
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

        self.table = QTableWidget(0, 8)

        # Set custom header
        custom_header = WordWrapHeaderView(Qt.Horizontal, self.table)
        self.table.setHorizontalHeader(custom_header)

        self.table.setHorizontalHeaderLabels([
            "Kategori", "Judul", "Waktu Estimasi", "Sasaran", "PIC",
            "Anggaran", "Sumber Anggaran", "Keterangan"
        ])

        # Apply table styling
        self.apply_table_style()

        # Set column widths
        self.table.setColumnWidth(0, 100)  # Kategori
        self.table.setColumnWidth(1, 180)  # Judul
        self.table.setColumnWidth(2, 110)  # Tanggal (dd/mm/yyyy needs more space)
        self.table.setColumnWidth(3, 120)  # Sasaran
        self.table.setColumnWidth(4, 80)   # PIC
        self.table.setColumnWidth(5, 100)  # Anggaran
        self.table.setColumnWidth(6, 130)  # Sumber Anggaran
        self.table.setColumnWidth(7, 150)  # Keterangan

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        header.sectionResized.connect(self.update_header_height)

        # Context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # Double click to edit
        self.table.itemDoubleClicked.connect(self.edit_proker)

        table_layout.addWidget(self.table)

        QTimer.singleShot(100, self.update_header_height)

        return table_container

    def update_header_height(self):
        """Update header height - ensure always visible"""
        if hasattr(self, 'table'):
            header = self.table.horizontalHeader()
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
        """Apply table styling"""
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)
        self.table.horizontalHeader().setFont(header_font)

        # Header with bold text, center alignment, and word wrap
        # IMPORTANT: Ensure header is always visible with adequate height
        self.table.horizontalHeader().setStyleSheet("""
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

        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        # CRITICAL: Set minimum height to ensure visibility when maximized
        header.setMinimumHeight(35)
        header.setDefaultSectionSize(100)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(500)

        self.table.setStyleSheet("""
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

        self.table.verticalHeader().setDefaultSectionSize(24)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setStyleSheet("""
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

        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.SolidLine)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.table.setMinimumHeight(200)

    def create_action_buttons(self):
        """Create action buttons with icons"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.setSpacing(5)

        # Detail button
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
            detail_icon = QIcon("client/assets/view.png")
            if not detail_icon.isNull():
                detail_button.setIcon(detail_icon)
                detail_button.setIconSize(QSize(14, 14))
        except:
            pass
        detail_button.clicked.connect(self.view_detail)
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
            edit_icon = QIcon("client/assets/edit.png")
            if not edit_icon.isNull():
                edit_button.setIcon(edit_icon)
                edit_button.setIconSize(QSize(14, 14))
        except:
            pass
        edit_button.clicked.connect(self.edit_proker)
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
            delete_icon = QIcon("client/assets/delete.png")
            if not delete_icon.isNull():
                delete_button.setIcon(delete_icon)
                delete_button.setIconSize(QSize(14, 14))
        except:
            pass
        delete_button.clicked.connect(self.delete_proker)
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
            export_icon = QIcon("client/assets/export.png")
            if not export_icon.isNull():
                export_csv_button.setIcon(export_icon)
                export_csv_button.setIconSize(QSize(14, 14))
        except:
            pass
        export_csv_button.clicked.connect(self.export_data_csv)
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
            export_icon = QIcon("client/assets/export.png")
            if not export_icon.isNull():
                export_pdf_button.setIcon(export_icon)
                export_pdf_button.setIconSize(QSize(14, 14))
        except:
            pass
        export_pdf_button.clicked.connect(self.export_data_pdf)
        button_layout.addWidget(export_pdf_button)

        return button_layout

    def show_context_menu(self, position):
        """Show context menu"""
        if self.table.rowCount() == 0:
            return

        menu = QMenu()
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")

        action = menu.exec_(self.table.mapToGlobal(position))

        if action == edit_action:
            self.edit_proker()
        elif action == delete_action:
            self.delete_proker()

    def filter_data(self):
        """Filter data berdasarkan kategori dan periode (bulan/tahun)"""
        kategori = self.kategori_filter.currentText()
        period_data = self.period_filter.currentData()

        filtered = []
        for proker in self.proker_list:
            # Filter by kategori
            if kategori != "Semua" and proker.get('kategori') != kategori:
                continue

            # Filter by period (year-month)
            if period_data != "all":
                estimasi_waktu = proker.get('estimasi_waktu', '')
                if estimasi_waktu:
                    # Extract year-month from date (YYYY-MM-DD format)
                    try:
                        if isinstance(estimasi_waktu, str) and len(estimasi_waktu) >= 7:
                            year_month = estimasi_waktu[:7]  # Get YYYY-MM
                            if year_month != period_data:
                                continue
                        else:
                            continue
                    except:
                        continue

            filtered.append(proker)

        self.populate_table(filtered)

    def populate_table(self, proker_list):
        """Populate table with data"""
        self.table.setRowCount(0)

        # Sort by date (estimasi_waktu) and judul
        def get_sort_key(proker):
            estimasi = proker.get('estimasi_waktu', '')
            # Try to parse date for sorting
            if estimasi:
                try:
                    # Parse YYYY-MM-DD format
                    if isinstance(estimasi, str) and '-' in estimasi:
                        return (estimasi, proker.get('judul', ''))
                except:
                    pass
            # If no valid date, put at end
            return ('9999-12-31', proker.get('judul', ''))

        sorted_list = sorted(proker_list, key=get_sort_key)

        for idx, proker in enumerate(sorted_list):
            self.table.insertRow(idx)

            # Column 0: Kategori
            kategori_item = QTableWidgetItem(proker.get('kategori', 'N/A'))

            # Column 1: Judul
            judul_item = QTableWidgetItem(proker.get('judul', 'N/A'))

            # Column 2: Tanggal (format dd/mm/yyyy)
            estimasi_waktu = proker.get('estimasi_waktu', '')
            if estimasi_waktu:
                try:
                    # Convert YYYY-MM-DD to dd/MM/yyyy
                    if isinstance(estimasi_waktu, str) and '-' in estimasi_waktu:
                        date_parts = estimasi_waktu.split('-')
                        if len(date_parts) == 3:
                            year, month, day = date_parts
                            tanggal_display = f"{day}/{month}/{year}"
                        else:
                            tanggal_display = estimasi_waktu
                    else:
                        tanggal_display = str(estimasi_waktu)
                except:
                    tanggal_display = str(estimasi_waktu)
            else:
                tanggal_display = 'N/A'

            tanggal_item = QTableWidgetItem(tanggal_display)

            # Column 3: Sasaran
            sasaran_item = QTableWidgetItem(proker.get('sasaran', 'N/A'))

            # Column 4: PIC
            pic_item = QTableWidgetItem(proker.get('penanggung_jawab', 'N/A'))

            # Column 5: Anggaran
            anggaran = proker.get('anggaran', 0)
            if anggaran:
                try:
                    anggaran_val = float(anggaran)
                    anggaran_text = f"Rp {anggaran_val:,.0f}".replace(',', '.')
                except:
                    anggaran_text = f"Rp {anggaran}"
            else:
                anggaran_text = "Rp 0"
            anggaran_item = QTableWidgetItem(anggaran_text)

            # Column 6: Sumber Anggaran
            sumber_item = QTableWidgetItem(proker.get('sumber_anggaran', 'N/A'))

            # Column 7: Keterangan
            keterangan_item = QTableWidgetItem(proker.get('keterangan', ''))

            # Store data in first column
            kategori_item.setData(Qt.UserRole, proker)

            # Add items
            self.table.setItem(idx, 0, kategori_item)
            self.table.setItem(idx, 1, judul_item)
            self.table.setItem(idx, 2, tanggal_item)  # Changed from bulan_item to tanggal_item
            self.table.setItem(idx, 3, sasaran_item)
            self.table.setItem(idx, 4, pic_item)
            self.table.setItem(idx, 5, anggaran_item)
            self.table.setItem(idx, 6, sumber_item)
            self.table.setItem(idx, 7, keterangan_item)

        # Select first row
        if proker_list and self.table.rowCount() > 0:
            self.table.selectRow(0)

    def load_data(self):
        """Load data from API"""
        if not self.api_client:
            self.log_message.emit("API Client tidak tersedia")
            return

        try:
            self.log_message.emit("Memuat data program kerja WR...")
            result = self.api_client.get_program_kerja_wr_list()

            self.log_message.emit(f"[DEBUG] API Response: success={result.get('success')}")

            if result.get("success"):
                # Get data from API response
                response_data = result.get("data", {})

                # Handle different response structures
                # API returns: {"status": "success", "data": [...]}
                if isinstance(response_data, dict):
                    if "status" in response_data and response_data.get("status") == "success":
                        # Response structure: {"status": "success", "data": [...]}
                        self.proker_list = response_data.get("data", [])
                    elif "data" in response_data:
                        # Response structure: {"data": [...]}
                        self.proker_list = response_data.get("data", [])
                    else:
                        # Unknown dict structure, treat as empty
                        self.proker_list = []
                elif isinstance(response_data, list):
                    # Direct list response
                    self.proker_list = response_data
                else:
                    self.proker_list = []

                self.log_message.emit(f"[DEBUG] Total records from API (already filtered by API): {len(self.proker_list)}")

                # Debug: Show first record if available
                if len(self.proker_list) > 0:
                    first = self.proker_list[0]
                    self.log_message.emit(f"[DEBUG] Sample record - Judul: {first.get('judul')}, reported_by: {first.get('reported_by')}")

                # Refresh table display (no need to filter by user_id, API already did it)
                self.filter_data()
                self.log_message.emit(f"✓ Data program kerja berhasil dimuat: {len(self.proker_list)} program")
            else:
                error_msg = result.get('data', 'Unknown error')
                self.log_message.emit(f"✗ Gagal memuat data: {error_msg}")
                self.proker_list = []
                self.populate_table([])

        except Exception as e:
            import traceback
            self.log_message.emit(f"✗ Error loading data: {str(e)}")
            self.log_message.emit(f"[DEBUG] Traceback: {traceback.format_exc()}")
            self.proker_list = []
            self.populate_table([])

    def add_proker(self):
        """Add new program kerja"""
        dialog = ProkerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Validate data
            errors = dialog.validate_data()
            if errors:
                QMessageBox.warning(self, "Validasi Gagal", "\n".join(errors))
                return

            data = dialog.get_data()

            try:
                self.log_message.emit(f"[DEBUG] Mengirim data: {data}")
                result = self.api_client.add_program_kerja_wr(data)
                self.log_message.emit(f"[DEBUG] Response add_proker: success={result.get('success')}")

                if result.get("success"):
                    # Reload data to refresh the table
                    self.log_message.emit("✓ Program kerja berhasil ditambahkan, me-reload data...")
                    self.load_data()

                    # Show success message
                    QMessageBox.information(self, "Sukses", "Program kerja berhasil ditambahkan dan tabel telah diperbarui")
                    self.log_message.emit(f"✓ Program kerja ditambahkan: {data['judul']}")
                    self.data_updated.emit()
                else:
                    error_msg = result.get('data', 'Unknown error')
                    QMessageBox.critical(self, "Error", f"Gagal menambah program:\n{error_msg}")
                    self.log_message.emit(f"✗ Gagal menambah program: {error_msg}")

            except Exception as e:
                import traceback
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
                self.log_message.emit(f"✗ Error add proker: {str(e)}")
                self.log_message.emit(f"[DEBUG] Traceback: {traceback.format_exc()}")

    def edit_proker(self):
        """Edit selected program kerja"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih program yang akan diedit")
            return

        kategori_item = self.table.item(current_row, 0)
        if not kategori_item or not kategori_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Warning", "Data program tidak valid")
            return

        proker = kategori_item.data(Qt.UserRole)

        # No need to check reported_by here because API already filters data by user_id
        # Only data owned by current user is shown in the table

        dialog = ProkerDialog(self, proker)
        if dialog.exec_() == QDialog.Accepted:
            # Validate data
            errors = dialog.validate_data()
            if errors:
                QMessageBox.warning(self, "Validasi Gagal", "\n".join(errors))
                return

            data = dialog.get_data()

            try:
                self.log_message.emit(f"[DEBUG] Update data: {data}")
                result = self.api_client.update_program_kerja_wr(proker.get('id_program_kerja_wr'), data)
                self.log_message.emit(f"[DEBUG] Response update: success={result.get('success')}")

                if result.get("success"):
                    # Reload data to refresh the table
                    self.log_message.emit("✓ Program kerja berhasil diperbarui, me-reload data...")
                    self.load_data()

                    QMessageBox.information(self, "Sukses", "Program kerja berhasil diperbarui dan tabel telah diperbarui")
                    self.log_message.emit(f"✓ Program kerja diperbarui: {data['judul']}")
                    self.data_updated.emit()
                else:
                    error_msg = result.get('data', 'Unknown error')
                    QMessageBox.critical(self, "Error", f"Gagal update program:\n{error_msg}")
                    self.log_message.emit(f"✗ Gagal update program: {error_msg}")

            except Exception as e:
                import traceback
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
                self.log_message.emit(f"✗ Error edit proker: {str(e)}")
                self.log_message.emit(f"[DEBUG] Traceback: {traceback.format_exc()}")

    def delete_proker(self):
        """Delete selected program kerja"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih program yang akan dihapus")
            return

        kategori_item = self.table.item(current_row, 0)
        if not kategori_item or not kategori_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Warning", "Data program tidak valid")
            return

        proker = kategori_item.data(Qt.UserRole)

        # No need to check reported_by here because API already filters data by user_id
        # Only data owned by current user is shown in the table

        reply = QMessageBox.question(self, "Konfirmasi",
                                    f"Yakin ingin menghapus program '{proker.get('judul')}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.log_message.emit(f"[DEBUG] Delete program ID: {proker.get('id_program_kerja_wr')}")
                result = self.api_client.delete_program_kerja_wr(proker.get('id_program_kerja_wr'))
                self.log_message.emit(f"[DEBUG] Response delete: success={result.get('success')}")

                if result.get("success"):
                    # Reload data to refresh the table
                    self.log_message.emit("✓ Program kerja berhasil dihapus, me-reload data...")
                    self.load_data()

                    QMessageBox.information(self, "Sukses", "Program kerja berhasil dihapus dan tabel telah diperbarui")
                    self.log_message.emit(f"✓ Program kerja dihapus: {proker.get('judul')}")
                    self.data_updated.emit()
                else:
                    error_msg = result.get('data', 'Unknown error')
                    QMessageBox.critical(self, "Error", f"Gagal hapus program:\n{error_msg}")
                    self.log_message.emit(f"✗ Gagal hapus program: {error_msg}")

            except Exception as e:
                import traceback
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
                self.log_message.emit(f"✗ Error delete proker: {str(e)}")
                self.log_message.emit(f"[DEBUG] Traceback: {traceback.format_exc()}")

    def view_detail(self):
        """View detail of selected program kerja"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih program yang akan dilihat detailnya")
            return

        kategori_item = self.table.item(current_row, 0)
        if not kategori_item or not kategori_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Warning", "Data program tidak valid")
            return

        proker = kategori_item.data(Qt.UserRole)
        dialog = ProkerDetailDialog(self, proker)
        dialog.exec_()

    def export_data_csv(self):
        """Export data to CSV"""
        if not self.proker_list:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Program Kerja", "program_kerja_wr.csv", "CSV Files (*.csv)"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "Kategori", "Judul", "Tanggal", "Sasaran", "PIC",
                    "Anggaran", "Sumber Anggaran", "Keterangan"
                ])
                writer.writeheader()

                for proker in self.proker_list:
                    # Format tanggal ke dd/mm/yyyy untuk export
                    estimasi_waktu = proker.get('estimasi_waktu', '')
                    if estimasi_waktu:
                        try:
                            if isinstance(estimasi_waktu, str) and '-' in estimasi_waktu:
                                date_parts = estimasi_waktu.split('-')
                                if len(date_parts) == 3:
                                    year, month, day = date_parts
                                    tanggal_display = f"{day}/{month}/{year}"
                                else:
                                    tanggal_display = estimasi_waktu
                            else:
                                tanggal_display = str(estimasi_waktu)
                        except:
                            tanggal_display = str(estimasi_waktu)
                    else:
                        tanggal_display = ''

                    writer.writerow({
                        "Kategori": proker.get('kategori', ''),
                        "Judul": proker.get('judul', ''),
                        "Tanggal": tanggal_display,
                        "Sasaran": proker.get('sasaran', ''),
                        "PIC": proker.get('penanggung_jawab', ''),
                        "Anggaran": proker.get('anggaran', ''),
                        "Sumber Anggaran": proker.get('sumber_anggaran', ''),
                        "Keterangan": proker.get('keterangan', '')
                    })

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data diekspor ke: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error export: {str(e)}")

    def export_data_pdf(self):
        """Export data to PDF with proper text wrapping and column fitting"""
        if not self.proker_list:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor")
            return

        if not HAS_REPORTLAB:
            QMessageBox.critical(self, "Error",
                "Perpustakaan reportlab tidak terinstall.\n"
                "Silakan jalankan: pip install reportlab")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Program Kerja ke PDF", "program_kerja_wr.pdf", "PDF Files (*.pdf)"
        )

        if not filename:
            return

        try:
            # Create PDF document with landscape orientation for better fit
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import landscape, A4

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
            elements.append(Paragraph("Program Kerja Wilayah Rohani", title_style))
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
            headers = ["Kategori", "Judul", "Waktu\nEstimasi", "Sasaran", "PIC",
                      "Anggaran", "Sumber\nAnggaran", "Keterangan"]
            table_data.append(headers)

            for proker in self.proker_list:
                # Format tanggal ke dd/mm/yyyy
                estimasi_waktu = proker.get('estimasi_waktu', '')
                if estimasi_waktu:
                    try:
                        if isinstance(estimasi_waktu, str) and '-' in estimasi_waktu:
                            date_parts = estimasi_waktu.split('-')
                            if len(date_parts) == 3:
                                year, month, day = date_parts
                                tanggal_display = f"{day}/{month}/{year}"
                            else:
                                tanggal_display = estimasi_waktu
                        else:
                            tanggal_display = str(estimasi_waktu)
                    except:
                        tanggal_display = str(estimasi_waktu)
                else:
                    tanggal_display = ''

                # Format anggaran
                anggaran = proker.get('anggaran', 0)
                if anggaran:
                    try:
                        anggaran_val = float(anggaran)
                        anggaran_text = f"Rp {anggaran_val:,.0f}".replace(',', '.')
                    except:
                        anggaran_text = f"Rp {anggaran}"
                else:
                    anggaran_text = "Rp 0"

                # Create wrapped paragraphs for long text fields
                kategori_text = str(proker.get('kategori', '-'))
                judul_text = str(proker.get('judul', '-'))
                sasaran_text = str(proker.get('sasaran', '-'))
                pic_text = str(proker.get('penanggung_jawab', '-'))
                sumber_text = str(proker.get('sumber_anggaran', '-'))
                keterangan_text = str(proker.get('keterangan', '-'))

                # Wrap text in Paragraph objects for proper text handling
                row = [
                    Paragraph(kategori_text, cell_style),
                    Paragraph(judul_text, cell_style),
                    Paragraph(tanggal_display, cell_style),
                    Paragraph(sasaran_text, cell_style),
                    Paragraph(pic_text, cell_style),
                    Paragraph(anggaran_text, cell_style),
                    Paragraph(sumber_text, cell_style),
                    Paragraph(keterangan_text, cell_style)
                ]
                table_data.append(row)

            # Create table with optimized column widths for landscape
            # Landscape A4: ~11 inches wide, minus margins = ~10.5 inches available
            table = Table(table_data, colWidths=[
                0.8*inch,   # Kategori
                1.4*inch,   # Judul
                0.9*inch,   # Waktu Estimasi
                1.2*inch,   # Sasaran
                0.9*inch,   # PIC
                1.1*inch,   # Anggaran
                1.1*inch,   # Sumber Anggaran
                1.5*inch    # Keterangan
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
            summary_text = f"Total Program Kerja: {len(self.proker_list)} | Tanggal Export: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
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
            import os
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
