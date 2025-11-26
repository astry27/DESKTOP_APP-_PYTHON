# Path: client/components/proker_component.py
# Program Kerja WR Component - User can only manage their own program kerja

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QPushButton, QFrame,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox,
                             QTextEdit, QDialog, QFormLayout, QFileDialog,
                             QAbstractItemView, QGroupBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QBrush, QPainter
import datetime
import csv


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
        self.setMinimumWidth(600)
        self.setMinimumHeight(550)

        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # 1. Kategori
        self.kategori_input = QComboBox()
        self.kategori_input.addItems([
            "Ibadah", "Doa", "Katekese", "Sosial",
            "Rohani", "Administratif", "Perayaan", "Lainnya"
        ])
        form_layout.addRow("Kategori: *", self.kategori_input)

        # 2. Estimasi Waktu (Bulan)
        self.bulan_input = QComboBox()
        self.bulan_input.addItems([
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ])
        form_layout.addRow("Estimasi Waktu (Bulan): *", self.bulan_input)

        # 3. Judul Program Kerja
        self.judul_input = QLineEdit()
        self.judul_input.setPlaceholderText("Masukkan judul program kerja")
        form_layout.addRow("Judul Program: *", self.judul_input)

        # 4. Sasaran
        self.sasaran_input = QLineEdit()
        self.sasaran_input.setPlaceholderText("Sasaran/tujuan program atau tokoh yang dituju")
        form_layout.addRow("Sasaran:", self.sasaran_input)

        # 5. Penanggung Jawab (PIC)
        self.pic_input = QLineEdit()
        self.pic_input.setPlaceholderText("Person In Charge (PIC)")
        form_layout.addRow("PIC:", self.pic_input)

        # 6. Anggaran
        self.anggaran_input = QLineEdit()
        self.anggaran_input.setPlaceholderText("Jumlah anggaran dalam Rp (contoh: 1000000)")
        form_layout.addRow("Anggaran (Rp):", self.anggaran_input)

        # 7. Sumber Anggaran
        self.sumber_input = QComboBox()
        self.sumber_input.addItems([
            "Kas Gereja", "Donasi Jemaat", "Sponsor External",
            "Dana Komisi", "APBG", "Kolekte Khusus", "Lainnya"
        ])
        form_layout.addRow("Sumber Anggaran:", self.sumber_input)

        # 8. Keterangan
        self.keterangan_input = QTextEdit()
        self.keterangan_input.setPlaceholderText("Keterangan lengkap program kerja (opsional)")
        self.keterangan_input.setMaximumHeight(100)
        form_layout.addRow("Keterangan:", self.keterangan_input)

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

        self.kategori_input.setCurrentText(self.proker_data.get('kategori', 'Ibadah'))
        self.bulan_input.setCurrentText(self.proker_data.get('estimasi_waktu', 'Januari'))
        self.judul_input.setText(self.proker_data.get('judul', ''))
        self.sasaran_input.setText(self.proker_data.get('sasaran', ''))
        self.pic_input.setText(self.proker_data.get('penanggung_jawab', ''))
        self.anggaran_input.setText(str(self.proker_data.get('anggaran', '')))
        self.sumber_input.setCurrentText(self.proker_data.get('sumber_anggaran', 'Kas Gereja'))
        self.keterangan_input.setText(self.proker_data.get('keterangan', ''))

    def get_data(self):
        """Get form data"""
        try:
            anggaran = float(self.anggaran_input.text()) if self.anggaran_input.text() else 0
        except ValueError:
            anggaran = 0

        return {
            'kategori': self.kategori_input.currentText(),
            'estimasi_waktu': self.bulan_input.currentText(),
            'judul': self.judul_input.text().strip(),
            'sasaran': self.sasaran_input.text().strip(),
            'penanggung_jawab': self.pic_input.text().strip(),
            'anggaran': anggaran,
            'sumber_anggaran': self.sumber_input.currentText(),
            'keterangan': self.keterangan_input.toPlainText().strip()
        }


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
                border-bottom: 2px solid #ecf0f1;
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

        # Bulan filter
        bulan_label = QLabel("Filter Bulan:")
        filter_layout.addWidget(bulan_label)

        self.bulan_filter = QComboBox()
        self.bulan_filter.addItems([
            "Semua Bulan",
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ])
        self.bulan_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.bulan_filter)

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
            "Kategori", "Judul", "Bulan", "Sasaran", "PIC",
            "Anggaran", "Sumber Anggaran", "Keterangan"
        ])

        # Apply table styling
        self.apply_table_style()

        # Set column widths
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 180)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 130)
        self.table.setColumnWidth(7, 150)

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
        """Update header height"""
        if hasattr(self, 'table'):
            header = self.table.horizontalHeader()
            header.setMinimumHeight(25)
            max_height = 25

            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            header.setFixedHeight(max_height)

    def apply_table_style(self):
        """Apply table styling"""
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)
        self.table.horizontalHeader().setFont(header_font)

        self.table.horizontalHeader().setStyleSheet("""
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

        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        header.setMinimumHeight(25)
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
        """Create action buttons"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        edit_button = QPushButton("Edit")
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        edit_button.clicked.connect(self.edit_proker)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("Hapus")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        delete_button.clicked.connect(self.delete_proker)
        button_layout.addWidget(delete_button)

        export_button = QPushButton("Export CSV")
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
        """)
        export_button.clicked.connect(self.export_data)
        button_layout.addWidget(export_button)

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
        """Filter data berdasarkan kategori dan bulan"""
        kategori = self.kategori_filter.currentText()
        bulan = self.bulan_filter.currentText()

        filtered = []
        for proker in self.proker_list:
            if kategori != "Semua" and proker.get('kategori') != kategori:
                continue
            if bulan != "Semua Bulan" and proker.get('estimasi_waktu') != bulan:
                continue
            filtered.append(proker)

        self.populate_table(filtered)

    def populate_table(self, proker_list):
        """Populate table with data"""
        self.table.setRowCount(0)

        # Sort by bulan dan judul
        month_order = {
            "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
            "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
            "September": 9, "Oktober": 10, "November": 11, "Desember": 12
        }
        sorted_list = sorted(proker_list,
                            key=lambda x: (month_order.get(x.get('estimasi_waktu', ''), 13),
                                         x.get('judul', '')))

        for idx, proker in enumerate(sorted_list):
            self.table.insertRow(idx)

            # Column 0: Kategori
            kategori_item = QTableWidgetItem(proker.get('kategori', 'N/A'))

            # Column 1: Judul
            judul_item = QTableWidgetItem(proker.get('judul', 'N/A'))

            # Column 2: Bulan
            bulan_item = QTableWidgetItem(proker.get('estimasi_waktu', 'N/A'))

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
            self.table.setItem(idx, 2, bulan_item)
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
            self.log_message.emit("Memuat data program kerja...")
            result = self.api_client.get_program_kerja_wr_list()

            if result.get("success"):
                # Filter hanya data yang dibuat oleh user saat ini
                all_proker = result.get("data", {}).get("data", [])
                user_id = self.current_user.get('id') if self.current_user else None

                self.proker_list = [p for p in all_proker if p.get('reported_by') == user_id]
                self.filter_data()
                self.log_message.emit(f"Data program kerja berhasil dimuat: {len(self.proker_list)} program")
            else:
                self.log_message.emit(f"Gagal memuat data: {result.get('data', 'Unknown error')}")
                self.proker_list = []
                self.populate_table([])

        except Exception as e:
            self.log_message.emit(f"Error loading data: {str(e)}")
            self.proker_list = []
            self.populate_table([])

    def add_proker(self):
        """Add new program kerja"""
        dialog = ProkerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            if not data['judul'].strip():
                QMessageBox.warning(self, "Warning", "Judul program tidak boleh kosong")
                return

            try:
                result = self.api_client.add_program_kerja_wr(data)
                if result.get("success"):
                    self.load_data()
                    QMessageBox.information(self, "Sukses", "Program kerja berhasil ditambahkan")
                    self.log_message.emit(f"Program kerja berhasil ditambahkan: {data['judul']}")
                    self.data_updated.emit()
                else:
                    QMessageBox.critical(self, "Error", f"Gagal menambah program: {result.get('data', 'Unknown error')}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")

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

        # Check if user owns this data
        if proker.get('reported_by') != self.current_user.get('id'):
            QMessageBox.warning(self, "Warning", "Anda hanya dapat mengedit program kerja yang Anda buat")
            return

        dialog = ProkerDialog(self, proker)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            if not data['judul'].strip():
                QMessageBox.warning(self, "Warning", "Judul program tidak boleh kosong")
                return

            try:
                result = self.api_client.update_program_kerja_wr(proker.get('id_program_kerja_wr'), data)
                if result.get("success"):
                    self.load_data()
                    QMessageBox.information(self, "Sukses", "Program kerja berhasil diperbarui")
                    self.log_message.emit(f"Program kerja berhasil diperbarui: {data['judul']}")
                    self.data_updated.emit()
                else:
                    QMessageBox.critical(self, "Error", f"Gagal update program: {result.get('data', 'Unknown error')}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")

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

        # Check if user owns this data
        if proker.get('reported_by') != self.current_user.get('id'):
            QMessageBox.warning(self, "Warning", "Anda hanya dapat menghapus program kerja yang Anda buat")
            return

        reply = QMessageBox.question(self, "Konfirmasi",
                                    f"Yakin ingin menghapus program '{proker.get('judul')}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                result = self.api_client.delete_program_kerja_wr(proker.get('id_program_kerja_wr'))
                if result.get("success"):
                    self.load_data()
                    QMessageBox.information(self, "Sukses", "Program kerja berhasil dihapus")
                    self.log_message.emit(f"Program kerja berhasil dihapus: {proker.get('judul')}")
                    self.data_updated.emit()
                else:
                    QMessageBox.critical(self, "Error", f"Gagal hapus program: {result.get('data', 'Unknown error')}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def export_data(self):
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
                    "Kategori", "Judul", "Bulan", "Sasaran", "PIC",
                    "Anggaran", "Sumber Anggaran", "Keterangan"
                ])
                writer.writeheader()

                for proker in self.proker_list:
                    writer.writerow({
                        "Kategori": proker.get('kategori', ''),
                        "Judul": proker.get('judul', ''),
                        "Bulan": proker.get('estimasi_waktu', ''),
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
