# Path: server/components/tim_pembina.py
# Tim Pembina Component for Pusat Paroki Menu

import csv
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QFrame, QMessageBox, QDialog,
                            QFileDialog, QLineEdit, QComboBox, QFormLayout,
                            QDialogButtonBox, QCompleter)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont

from .struktur_base import BaseStrukturComponent, WordWrapHeaderView


class TimPembinaDialog(QDialog):
    """Dialog untuk tambah/edit Tim Pembina Peserta"""

    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.is_edit = data is not None
        self.db_manager = parent.db_manager if parent else None
        self.jemaat_data = []

        self.setWindowTitle("Edit Tim Pembina" if self.is_edit else "Tambah Tim Pembina")
        self.setModal(True)
        self.resize(600, 500)

        self.setup_ui()

        if self.is_edit and data:
            self.populate_data(data)

    def setup_ui(self):
        """Setup UI untuk dialog"""
        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(8)  # Reduced spacing from 15 to 8

        # Nama Peserta dengan autocomplete dan button Cari Umat
        nama_layout = QHBoxLayout()
        self.nama_peserta_input = QLineEdit()
        self.nama_peserta_input.setPlaceholderText("Ketik nama atau klik 'Cari Umat' untuk memilih dari database")
        self.nama_peserta_input.textChanged.connect(self.on_nama_changed)
        nama_layout.addWidget(self.nama_peserta_input)

        self.cari_umat_button = QPushButton("Cari Umat")
        self.cari_umat_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.cari_umat_button.clicked.connect(self.search_jemaat)
        nama_layout.addWidget(self.cari_umat_button)

        form_layout.addRow("Nama Peserta *:", nama_layout)

        # Tim Pembina dropdown
        self.tim_pembina_combo = QComboBox()
        self.tim_pembina_combo.addItem("-- Pilih Tim Pembina --")  # Default placeholder
        self.tim_pembina_combo.addItems([
            "Liturgi", "Katekese", "Perkawinan", "Keluarga", "Konsultasi", "Lainnya"
        ])
        self.tim_pembina_combo.currentTextChanged.connect(self.on_tim_pembina_changed)
        form_layout.addRow("Tim Pembina *:", self.tim_pembina_combo)

        # Tim Pembina Lainnya (hidden by default)
        self.tim_pembina_lainnya_input = QLineEdit()
        self.tim_pembina_lainnya_input.setPlaceholderText("Masukkan nama tim pembina lainnya")
        self.tim_pembina_lainnya_label = QLabel("Tim Pembina (Lainnya) *:")
        form_layout.addRow(self.tim_pembina_lainnya_label, self.tim_pembina_lainnya_input)
        self.tim_pembina_lainnya_label.hide()
        self.tim_pembina_lainnya_input.hide()

        # Wilayah Rohani dropdown
        self.wilayah_rohani_combo = QComboBox()
        self.wilayah_rohani_combo.addItem("-- Pilih Wilayah Rohani --")  # Default placeholder
        wilayah_list = [
            "ST. YOHANES BAPTISTA DE LA SALLE",
            "ST. ALOYSIUS GONZAGA",
            "ST. GREGORIUS AGUNG",
            "ST. DOMINICO SAVIO",
            "ST. THOMAS AQUINAS",
            "ST. ALBERTUS AGUNG",
            "ST. BONAVENTURA",
            "STA. KATARINA DARI SIENA",
            "STA. SISILIA",
            "ST. BLASIUS",
            "ST. CAROLUS BORROMEUS",
            "ST. BONIFASIUS",
            "ST. CORNELIUS",
            "STA. BRIGITTA",
            "ST. IGNASIUS DARI LOYOLA",
            "ST. PIUS X",
            "STA. AGNES",
            "ST. AGUSTINUS",
            "STA. FAUSTINA",
            "ST. YOHANES MARIA VIANNEY",
            "STA. MARIA GORETTI",
            "STA. PERPETUA",
            "ST. LUKAS",
            "STA. SKOLASTIKA",
            "STA. THERESIA DARI AVILLA",
            "ST. VINCENTIUS A PAULO"
        ]
        self.wilayah_rohani_combo.addItems(wilayah_list)
        form_layout.addRow("Wilayah Rohani *:", self.wilayah_rohani_combo)

        # Jabatan dropdown
        self.jabatan_combo = QComboBox()
        self.jabatan_combo.addItem("-- Pilih Jabatan --")  # Default placeholder
        self.jabatan_combo.addItems([
            "Pembina", "Ketua", "Sekretaris", "Bendahara", "Koordinator", "Anggota Sie", "Anggota Biasa"
        ])
        form_layout.addRow("Jabatan *:", self.jabatan_combo)

        # Tahun dropdown (dynamic)
        self.tahun_combo = QComboBox()
        self.tahun_combo.addItem("-- Pilih Tahun --")  # Default placeholder
        current_year = datetime.now().year
        for year in range(current_year, current_year + 20):
            self.tahun_combo.addItem(str(year))
        form_layout.addRow("Tahun *:", self.tahun_combo)

        layout.addLayout(form_layout)

        # Info label
        info_label = QLabel("* Field wajib diisi")
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 10px;")
        layout.addWidget(info_label)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Style buttons
        button_box.button(QDialogButtonBox.Ok).setText("Simpan")
        button_box.button(QDialogButtonBox.Cancel).setText("Batal")
        button_box.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton[text="Simpan"] {
                background-color: #27ae60;
                color: white;
                border: none;
            }
            QPushButton[text="Simpan"]:hover {
                background-color: #229954;
            }
            QPushButton[text="Batal"] {
                background-color: #95a5a6;
                color: white;
                border: none;
            }
            QPushButton[text="Batal"]:hover {
                background-color: #7f8c8d;
            }
        """)

        layout.addWidget(button_box)

        # Hidden fields for tracking
        self.id_jemaat = None
        self.is_manual_entry = True

    def on_tim_pembina_changed(self, text):
        """Show/hide Tim Pembina Lainnya field based on selection"""
        if text == "Lainnya":
            self.tim_pembina_lainnya_label.show()
            self.tim_pembina_lainnya_input.show()
        else:
            self.tim_pembina_lainnya_label.hide()
            self.tim_pembina_lainnya_input.hide()
            self.tim_pembina_lainnya_input.clear()

    def on_nama_changed(self, text):
        """Mark as manual entry when user types"""
        # Only mark as manual if user is typing and hasn't selected from jemaat
        if not hasattr(self, '_selecting_from_jemaat') or not self._selecting_from_jemaat:
            self.is_manual_entry = True
            self.id_jemaat = None

    def search_jemaat(self):
        """Open dialog to search and select from jemaat database"""
        search_text = self.nama_peserta_input.text().strip()

        if not self.db_manager:
            QMessageBox.warning(self, "Error", "Database tidak tersedia")
            return

        # Search jemaat (empty string will return all jemaat with limit)
        success, result = self.db_manager.search_jemaat_for_tim_pembina(search_text if search_text else '')

        if not success:
            QMessageBox.warning(self, "Error", f"Gagal mencari umat: {result}")
            return

        if not result or len(result) == 0:
            if search_text:
                QMessageBox.information(self, "Info", f"Tidak ada umat ditemukan dengan kata kunci '{search_text}'")
            else:
                QMessageBox.information(self, "Info", "Tidak ada data umat tersedia di database")
            return

        # Show selection dialog
        dialog = JemaatSelectionDialog(self, result)
        if dialog.exec_() == QDialog.Accepted:
            selected = dialog.get_selected()
            if selected:
                self._selecting_from_jemaat = True
                self.nama_peserta_input.setText(selected['nama_lengkap'])
                self.id_jemaat = selected['id_jemaat']
                self.is_manual_entry = False

                # Auto-fill Wilayah Rohani if available
                if selected.get('wilayah_rohani'):
                    index = self.wilayah_rohani_combo.findText(selected['wilayah_rohani'])
                    if index >= 0:
                        self.wilayah_rohani_combo.setCurrentIndex(index)

                self._selecting_from_jemaat = False

    def populate_data(self, data):
        """Populate form with existing data for editing"""
        self.nama_peserta_input.setText(data.get('nama_peserta', ''))

        # Tim Pembina
        tim_pembina = data.get('tim_pembina', '')
        index = self.tim_pembina_combo.findText(tim_pembina)
        if index >= 0:
            self.tim_pembina_combo.setCurrentIndex(index)
        else:
            self.tim_pembina_combo.setCurrentIndex(0)  # Reset to placeholder

        # Tim Pembina Lainnya
        if tim_pembina == "Lainnya" and data.get('tim_pembina_lainnya'):
            self.tim_pembina_lainnya_input.setText(data.get('tim_pembina_lainnya'))

        # Wilayah Rohani
        wilayah = data.get('wilayah_rohani', '')
        index = self.wilayah_rohani_combo.findText(wilayah)
        if index >= 0:
            self.wilayah_rohani_combo.setCurrentIndex(index)
        else:
            self.wilayah_rohani_combo.setCurrentIndex(0)  # Reset to placeholder

        # Jabatan
        jabatan = data.get('jabatan', '')
        index = self.jabatan_combo.findText(jabatan)
        if index >= 0:
            self.jabatan_combo.setCurrentIndex(index)
        else:
            self.jabatan_combo.setCurrentIndex(0)  # Reset to placeholder

        # Tahun
        tahun = str(data.get('tahun', ''))
        index = self.tahun_combo.findText(tahun)
        if index >= 0:
            self.tahun_combo.setCurrentIndex(index)
        else:
            self.tahun_combo.setCurrentIndex(0)  # Reset to placeholder

        # Set tracking fields
        self.id_jemaat = data.get('id_jemaat')
        self.is_manual_entry = bool(data.get('is_manual_entry', 1))

    def get_data(self):
        """Get form data"""
        tim_pembina = self.tim_pembina_combo.currentText()
        wilayah_rohani = self.wilayah_rohani_combo.currentText()
        jabatan = self.jabatan_combo.currentText()
        tahun_text = self.tahun_combo.currentText()

        data = {
            'nama_peserta': self.nama_peserta_input.text().strip(),
            'is_manual_entry': 1 if self.is_manual_entry else 0,
            'id_jemaat': self.id_jemaat,
            'tim_pembina': tim_pembina if not tim_pembina.startswith("--") else "",
            'tim_pembina_lainnya': self.tim_pembina_lainnya_input.text().strip() if tim_pembina == "Lainnya" else None,
            'wilayah_rohani': wilayah_rohani if not wilayah_rohani.startswith("--") else "",
            'jabatan': jabatan if not jabatan.startswith("--") else "",
            'tahun': int(tahun_text) if tahun_text and not tahun_text.startswith("--") else 0
        }

        return data


class JemaatSelectionDialog(QDialog):
    """Dialog untuk memilih jemaat dari hasil pencarian"""

    def __init__(self, parent=None, jemaat_list=None):
        super().__init__(parent)
        self.jemaat_list = jemaat_list or []
        self.filtered_jemaat_list = jemaat_list or []
        self.selected_jemaat = None

        self.setWindowTitle("Pilih Umat")
        self.setModal(True)
        self.resize(700, 400)

        self.setup_ui()

    def setup_ui(self):
        """Setup UI untuk dialog"""
        layout = QVBoxLayout(self)

        # Header with title and count
        header_layout = QHBoxLayout()
        title_label = QLabel("Pilih Umat dari Database")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        header_layout.addWidget(title_label)

        self.count_label = QLabel(f"({len(self.jemaat_list)} umat)")
        self.count_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Search input
        search_layout = QHBoxLayout()
        search_label = QLabel("Cari:")
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ketik nama umat atau wilayah rohani untuk mencari...")
        self.search_input.setFixedHeight(30)
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table with only 2 columns: Nama Lengkap and Wilayah Rohani
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Nama Lengkap", "Wilayah Rohani"])

        # Table styling
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.on_accept)

        # Professional styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                gridline-color: #e0e0e0;
                border: 1px solid #d0d0d0;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: none;
                border-right: 1px solid #d0d0d0;
                font-weight: bold;
                color: #2c3e50;
            }
        """)

        # Populate table with initial data
        self.populate_table(self.jemaat_list)

        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        pilih_button = QPushButton("Pilih")
        pilih_button.setFixedWidth(100)
        pilih_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        pilih_button.clicked.connect(self.on_accept)
        button_layout.addWidget(pilih_button)

        batal_button = QPushButton("Batal")
        batal_button.setFixedWidth(100)
        batal_button.setStyleSheet("""
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
        batal_button.clicked.connect(self.reject)
        button_layout.addWidget(batal_button)

        layout.addLayout(button_layout)

    def populate_table(self, jemaat_list):
        """Populate table with jemaat data"""
        self.table.setRowCount(0)

        for jemaat in jemaat_list:
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)

            # Column 0: Nama Lengkap
            nama_item = QTableWidgetItem(jemaat.get('nama_lengkap', ''))
            nama_item.setFont(QFont("Arial", 10))
            self.table.setItem(row_pos, 0, nama_item)

            # Column 1: Wilayah Rohani
            wilayah_item = QTableWidgetItem(jemaat.get('wilayah_rohani', '-'))
            wilayah_item.setFont(QFont("Arial", 10))
            self.table.setItem(row_pos, 1, wilayah_item)

        # Set column widths
        self.table.setColumnWidth(0, 300)
        self.table.setColumnWidth(1, 350)

    def filter_table(self):
        """Filter table based on search input"""
        search_text = self.search_input.text().lower().strip()

        if not search_text:
            # No search, show all
            self.filtered_jemaat_list = self.jemaat_list.copy()
        else:
            # Filter based on nama_lengkap or wilayah_rohani
            self.filtered_jemaat_list = [
                jemaat for jemaat in self.jemaat_list
                if (search_text in (jemaat.get('nama_lengkap', '') or '').lower() or
                    search_text in (jemaat.get('wilayah_rohani', '') or '').lower())
            ]

        # Update table
        self.populate_table(self.filtered_jemaat_list)

        # Update count label
        self.count_label.setText(f"({len(self.filtered_jemaat_list)} umat)")

    def on_accept(self):
        """Handle accept with validation"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih salah satu umat dari tabel")
            return

        self.selected_jemaat = self.filtered_jemaat_list[current_row]
        self.accept()

    def get_selected(self):
        """Get selected jemaat"""
        return self.selected_jemaat


class TimPembinaComponent(BaseStrukturComponent):
    """Komponen untuk Tim Pembina di menu Pusat Paroki"""

    log_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tim_pembina_data = []
        self.all_tim_pembina_data = []
        self.total_label = None
        self.tim_pembina_table = None
        self.search_input = None
        self.tim_pembina_filter = None
        self.wilayah_rohani_filter = None
        self.jabatan_filter = None
        self.tahun_filter = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI untuk Tim Pembina"""
        layout = QVBoxLayout(self)

        # Header dengan buttons dan search
        header = self.create_header()
        layout.addWidget(header)

        # Filter row
        filter_row = self.create_filter_row()
        layout.addWidget(filter_row)

        # Header Title
        title_header = self.create_title_header()
        layout.addWidget(title_header)

        # Table view
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

        self.tim_pembina_table = self.create_table_view()
        table_layout.addWidget(self.tim_pembina_table)

        layout.addWidget(table_container)

        # Action buttons
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)

    def create_header(self):
        """Buat header dengan kontrol pencarian dan tombol tambah"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 10, 0)

        # Search functionality
        header_layout.addWidget(QLabel("Cari:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama peserta, tim, wilayah, jabatan...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.filter_data)
        header_layout.addWidget(self.search_input)

        # Tombol Refresh
        refresh_button = self.create_button("Refresh", "#3498db", self.refresh_data, "server/assets/refresh.png")
        header_layout.addWidget(refresh_button)

        header_layout.addStretch()

        add_button = self.create_button("Tambah Tim", "#27ae60", self.add_tim_pembina, "server/assets/tambah.png")
        header_layout.addWidget(add_button)

        return header

    def create_filter_row(self):
        """Buat row untuk filter dropdown"""
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 5, 10, 5)

        # Tim Pembina filter
        filter_layout.addWidget(QLabel("Tim Pembina:"))
        self.tim_pembina_filter = QComboBox()
        self.tim_pembina_filter.addItems([
            "Semua", "Liturgi", "Katekese", "Perkawinan", "Keluarga", "Konsultasi", "Lainnya"
        ])
        self.tim_pembina_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.tim_pembina_filter)

        filter_layout.addSpacing(20)

        # Wilayah Rohani filter
        filter_layout.addWidget(QLabel("Wilayah Rohani:"))
        self.wilayah_rohani_filter = QComboBox()
        self.wilayah_rohani_filter.addItem("Semua")
        wilayah_list = [
            "ST. YOHANES BAPTISTA DE LA SALLE",
            "ST. ALOYSIUS GONZAGA",
            "ST. GREGORIUS AGUNG",
            "ST. DOMINICO SAVIO",
            "ST. THOMAS AQUINAS",
            "ST. ALBERTUS AGUNG",
            "ST. BONAVENTURA",
            "STA. KATARINA DARI SIENA",
            "STA. SISILIA",
            "ST. BLASIUS",
            "ST. CAROLUS BORROMEUS",
            "ST. BONIFASIUS",
            "ST. CORNELIUS",
            "STA. BRIGITTA",
            "ST. IGNASIUS DARI LOYOLA",
            "ST. PIUS X",
            "STA. AGNES",
            "ST. AGUSTINUS",
            "STA. FAUSTINA",
            "ST. YOHANES MARIA VIANNEY",
            "STA. MARIA GORETTI",
            "STA. PERPETUA",
            "ST. LUKAS",
            "STA. SKOLASTIKA",
            "STA. THERESIA DARI AVILLA",
            "ST. VINCENTIUS A PAULO"
        ]
        self.wilayah_rohani_filter.addItems(wilayah_list)
        self.wilayah_rohani_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.wilayah_rohani_filter)

        filter_layout.addSpacing(20)

        # Jabatan filter
        filter_layout.addWidget(QLabel("Jabatan:"))
        self.jabatan_filter = QComboBox()
        self.jabatan_filter.addItems([
            "Semua", "Pembina", "Ketua", "Sekretaris", "Bendahara", "Koordinator", "Anggota Sie", "Anggota Biasa"
        ])
        self.jabatan_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.jabatan_filter)

        filter_layout.addSpacing(20)

        # Tahun filter
        filter_layout.addWidget(QLabel("Tahun:"))
        self.tahun_filter = QComboBox()
        self.tahun_filter.addItem("Semua")
        current_year = datetime.now().year
        for year in range(current_year + 10, current_year - 10, -1):
            self.tahun_filter.addItem(str(year))
        self.tahun_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.tahun_filter)

        filter_layout.addStretch()

        return filter_widget

    def create_title_header(self):
        """Buat header title untuk Tim Pembina"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 12, 10, 12)
        header_layout.setSpacing(3)

        # Title
        title_label = QLabel("Daftar Tim Pembina")
        title_label.setAlignment(Qt.AlignCenter)
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
        title_label.setMinimumHeight(28)
        title_label.setWordWrap(False)
        header_layout.addWidget(title_label, 0, Qt.AlignCenter)

        # Subtitle
        subtitle_label = QLabel("Santa Maria Ratu Damai, Uluindano")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Arial", 12, QFont.Normal)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """)
        subtitle_label.setMinimumHeight(22)
        subtitle_label.setWordWrap(False)
        header_layout.addWidget(subtitle_label, 0, Qt.AlignCenter)

        # Total info
        self.total_label = QLabel("Total: 0 peserta")
        self.total_label.setAlignment(Qt.AlignCenter)
        total_font = QFont("Arial", 11, QFont.Normal)
        self.total_label.setFont(total_font)
        self.total_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                background-color: transparent;
                border: none;
                padding: 2px;
            }
        """)
        self.total_label.setMinimumHeight(18)
        header_layout.addWidget(self.total_label, 0, Qt.AlignCenter)

        return header_frame

    def create_table_view(self):
        """Buat tampilan tabel dengan style profesional"""
        table = QTableWidget(0, 5)

        # Set custom header with word wrap
        custom_header = WordWrapHeaderView(Qt.Horizontal, table)
        table.setHorizontalHeader(custom_header)

        table.setHorizontalHeaderLabels([
            "Nama Peserta", "Tim Pembina", "Wilayah Rohani", "Jabatan", "Tahun"
        ])

        # Apply professional table styling
        self.apply_professional_table_style(table)

        # Column resizing
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # Set initial column widths
        table.setColumnWidth(0, 250)  # Nama Peserta
        table.setColumnWidth(1, 150)  # Tim Pembina
        table.setColumnWidth(2, 250)  # Wilayah Rohani
        table.setColumnWidth(3, 150)  # Jabatan
        table.setColumnWidth(4, 100)  # Tahun

        # Update header height when column is resized
        header.sectionResized.connect(self.update_header_height)

        # Enable context menu
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu)

        # Initial header height calculation
        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

        return table

    def update_header_height(self, logicalIndex, oldSize, newSize):
        """Update header height when column is resized"""
        if hasattr(self, 'tim_pembina_table') and self.tim_pembina_table:
            header = self.tim_pembina_table.horizontalHeader()
            header.setMinimumHeight(25)
            max_height = 25

            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            header.setFixedHeight(max_height)

    def create_action_buttons(self):
        """Buat tombol-tombol aksi"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        edit_button = self.create_button("Edit Terpilih", "#f39c12", self.edit_tim_pembina, "server/assets/edit.png")
        action_layout.addWidget(edit_button)

        delete_button = self.create_button("Hapus Terpilih", "#c0392b", self.delete_tim_pembina, "server/assets/hapus.png")
        action_layout.addWidget(delete_button)

        export_button = self.create_button("Export Data", "#16a085", self.export_data, "server/assets/export.png")
        action_layout.addWidget(export_button)

        return action_layout

    def show_context_menu(self, position):
        """Tampilkan context menu untuk table"""
        if self.tim_pembina_table.rowCount() == 0:
            return

        from PyQt5.QtWidgets import QMenu
        menu = QMenu()

        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")

        action = menu.exec_(self.tim_pembina_table.mapToGlobal(position))

        if action == edit_action:
            self.edit_tim_pembina()
        elif action == delete_action:
            self.delete_tim_pembina()

    def load_data(self):
        """Load data tim pembina dari database"""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            if not hasattr(self.db_manager, 'get_tim_pembina_list'):
                self.log_message.emit("Error: Database manager tidak memiliki method get_tim_pembina_list")
                return

            self.log_message.emit("Mencoba memuat data Tim Pembina...")
            success, result = self.db_manager.get_tim_pembina_list()

            if success:
                if isinstance(result, dict) and 'data' in result:
                    data_list = result['data'] if result['data'] is not None else []
                elif isinstance(result, list):
                    data_list = result
                else:
                    data_list = []

                self.all_tim_pembina_data = data_list.copy()
                self.tim_pembina_data = data_list

                self.populate_table()
                self.update_total_label()
                self.log_message.emit(f"Data Tim Pembina berhasil dimuat: {len(self.tim_pembina_data)} record")
            else:
                self.all_tim_pembina_data = []
                self.tim_pembina_data = []
                self.populate_table()
                self.update_total_label()
                self.log_message.emit(f"Gagal memuat data Tim Pembina: {result}")

        except Exception as e:
            self.log_message.emit(f"Exception saat memuat data Tim Pembina: {str(e)}")
            self.all_tim_pembina_data = []
            self.tim_pembina_data = []
            self.populate_table()
            self.update_total_label()

    def populate_table(self):
        """Populate table dengan data tim pembina"""
        self.tim_pembina_table.setRowCount(0)

        if not self.tim_pembina_data:
            return

        for row_data in self.tim_pembina_data:
            row_pos = self.tim_pembina_table.rowCount()
            self.tim_pembina_table.insertRow(row_pos)

            # Column 0: Nama Peserta
            nama_peserta = row_data.get('nama_peserta', '')
            nama_item = QTableWidgetItem(nama_peserta)
            self.tim_pembina_table.setItem(row_pos, 0, nama_item)

            # Column 1: Tim Pembina
            tim_pembina = row_data.get('tim_pembina', '')
            if tim_pembina == 'Lainnya' and row_data.get('tim_pembina_lainnya'):
                tim_pembina = row_data.get('tim_pembina_lainnya')
            tim_item = QTableWidgetItem(tim_pembina)
            self.tim_pembina_table.setItem(row_pos, 1, tim_item)

            # Column 2: Wilayah Rohani
            wilayah = row_data.get('wilayah_rohani', '')
            wilayah_item = QTableWidgetItem(wilayah)
            self.tim_pembina_table.setItem(row_pos, 2, wilayah_item)

            # Column 3: Jabatan
            jabatan = row_data.get('jabatan', '')
            jabatan_item = QTableWidgetItem(jabatan)
            self.tim_pembina_table.setItem(row_pos, 3, jabatan_item)

            # Column 4: Tahun
            tahun = str(row_data.get('tahun', ''))
            tahun_item = QTableWidgetItem(tahun)
            tahun_item.setTextAlignment(Qt.AlignCenter)
            self.tim_pembina_table.setItem(row_pos, 4, tahun_item)

    def update_total_label(self):
        """Update label total peserta"""
        total = len(self.tim_pembina_data)
        self.total_label.setText(f"Total: {total} peserta")

    def filter_data(self):
        """Filter data berdasarkan search dan filter dropdown"""
        search_text = self.search_input.text().lower().strip()
        tim_filter = self.tim_pembina_filter.currentText()
        wilayah_filter = self.wilayah_rohani_filter.currentText()
        jabatan_filter = self.jabatan_filter.currentText()
        tahun_filter = self.tahun_filter.currentText()

        if not hasattr(self, 'all_tim_pembina_data') or not self.all_tim_pembina_data:
            self.all_tim_pembina_data = self.tim_pembina_data.copy() if self.tim_pembina_data else []

        filtered_data = []

        for data in self.all_tim_pembina_data:
            # Search text filter
            if search_text:
                nama_peserta = (data.get('nama_peserta') or '').lower()
                tim_pembina = (data.get('tim_pembina') or '').lower()
                tim_lainnya = (data.get('tim_pembina_lainnya') or '').lower()
                wilayah = (data.get('wilayah_rohani') or '').lower()
                jabatan = (data.get('jabatan') or '').lower()

                if not (search_text in nama_peserta or
                       search_text in tim_pembina or
                       search_text in tim_lainnya or
                       search_text in wilayah or
                       search_text in jabatan):
                    continue

            # Tim Pembina filter
            if tim_filter and tim_filter != "Semua":
                if data.get('tim_pembina') != tim_filter:
                    continue

            # Wilayah Rohani filter
            if wilayah_filter and wilayah_filter != "Semua":
                if data.get('wilayah_rohani') != wilayah_filter:
                    continue

            # Jabatan filter
            if jabatan_filter and jabatan_filter != "Semua":
                if data.get('jabatan') != jabatan_filter:
                    continue

            # Tahun filter
            if tahun_filter and tahun_filter != "Semua":
                if str(data.get('tahun')) != tahun_filter:
                    continue

            filtered_data.append(data)

        self.tim_pembina_data = filtered_data
        self.populate_table()
        self.update_total_label()

    def refresh_data(self):
        """Refresh data dari database"""
        self.search_input.clear()
        self.tim_pembina_filter.setCurrentIndex(0)
        self.wilayah_rohani_filter.setCurrentIndex(0)
        self.jabatan_filter.setCurrentIndex(0)
        self.tahun_filter.setCurrentIndex(0)

        if hasattr(self, 'all_tim_pembina_data'):
            self.all_tim_pembina_data = []

        self.load_data()
        self.log_message.emit("Data Tim Pembina berhasil di-refresh")

    def add_tim_pembina(self):
        """Tambah peserta Tim Pembina baru"""
        dialog = TimPembinaDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            if not data['nama_peserta']:
                QMessageBox.warning(self, "Error", "Nama peserta harus diisi")
                return

            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            if not hasattr(self.db_manager, 'add_tim_pembina'):
                QMessageBox.critical(self, "Error", "Method add_tim_pembina tidak tersedia di database manager")
                return

            self.log_message.emit("Mencoba menambahkan peserta Tim Pembina...")
            success, result = self.db_manager.add_tim_pembina(data)
            if success:
                QMessageBox.information(self, "Sukses", "Peserta Tim Pembina berhasil ditambahkan.")
                self.load_data()
                self.log_message.emit("Peserta Tim Pembina berhasil ditambahkan")
            else:
                QMessageBox.critical(self, "Error", f"Gagal menambahkan peserta: {result}")
                self.log_message.emit(f"Error menambahkan peserta: {result}")

    def edit_tim_pembina(self):
        """Edit peserta Tim Pembina yang dipilih"""
        current_row = self.tim_pembina_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih peserta yang akan diedit")
            return

        if current_row >= len(self.tim_pembina_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return

        tim_pembina_data = self.tim_pembina_data[current_row]
        dialog = TimPembinaDialog(self, tim_pembina_data)
        if dialog.exec_() == dialog.Accepted:
            updated_data = dialog.get_data()

            if not updated_data['nama_peserta']:
                QMessageBox.warning(self, "Error", "Nama peserta harus diisi")
                return

            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            tim_pembina_id = tim_pembina_data.get('id_tim_pembina')
            if tim_pembina_id and hasattr(self.db_manager, 'update_tim_pembina'):
                success, result = self.db_manager.update_tim_pembina(tim_pembina_id, updated_data)
                if success:
                    QMessageBox.information(self, "Sukses", "Peserta Tim Pembina berhasil diupdate.")
                    self.load_data()
                    self.log_message.emit("Peserta Tim Pembina berhasil diupdate")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal mengupdate peserta: {result}")
                    self.log_message.emit(f"Error update peserta: {result}")
            else:
                QMessageBox.critical(self, "Error", "Method update_tim_pembina tidak tersedia")

    def delete_tim_pembina(self):
        """Hapus peserta Tim Pembina yang dipilih"""
        current_row = self.tim_pembina_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih peserta yang akan dihapus")
            return

        if current_row >= len(self.tim_pembina_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return

        tim_pembina_data = self.tim_pembina_data[current_row]
        nama_peserta = tim_pembina_data.get('nama_peserta', 'Unknown')
        tim_pembina = tim_pembina_data.get('tim_pembina', '')

        reply = QMessageBox.question(self, 'Konfirmasi',
                                    f"Yakin ingin menghapus peserta '{nama_peserta}' dari tim '{tim_pembina}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            tim_pembina_id = tim_pembina_data.get('id_tim_pembina')
            if tim_pembina_id and hasattr(self.db_manager, 'delete_tim_pembina'):
                success, result = self.db_manager.delete_tim_pembina(tim_pembina_id)
                if success:
                    QMessageBox.information(self, "Sukses", "Peserta Tim Pembina berhasil dihapus.")
                    self.load_data()
                    self.log_message.emit("Peserta Tim Pembina berhasil dihapus")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal menghapus peserta: {result}")
                    self.log_message.emit(f"Error hapus peserta: {result}")
            else:
                QMessageBox.critical(self, "Error", "Method delete_tim_pembina tidak tersedia")

    def export_data(self):
        """Export data Tim Pembina ke file CSV"""
        if not self.tim_pembina_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Data Tim Pembina", "tim_pembina.csv", "CSV Files (*.csv)")
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Nama Peserta", "Tim Pembina", "Wilayah Rohani", "Jabatan", "Tahun"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in self.tim_pembina_data:
                    tim_pembina = item.get('tim_pembina', '')
                    if tim_pembina == 'Lainnya' and item.get('tim_pembina_lainnya'):
                        tim_pembina = item.get('tim_pembina_lainnya')

                    writer.writerow({
                        "Nama Peserta": item.get('nama_peserta', ''),
                        "Tim Pembina": tim_pembina,
                        "Wilayah Rohani": item.get('wilayah_rohani', ''),
                        "Jabatan": item.get('jabatan', ''),
                        "Tahun": item.get('tahun', '')
                    })

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data Tim Pembina diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
            self.log_message.emit(f"Gagal mengekspor data: {str(e)}")

    def set_current_admin(self, admin_data):
        """Set current admin data"""
        self.current_admin = admin_data
