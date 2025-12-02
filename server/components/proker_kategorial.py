# Path: server/components/proker_kategorial.py
# Program Kerja K. Kategorial (Kelompok Kategorial) Tab Component

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QFrame, QGroupBox, QMessageBox, QDialog, QComboBox,
                           QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                           QFileDialog, QMenu, QTextEdit, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QBrush, QIcon

# Import WordWrapHeaderView from proker_base
from .proker_base import WordWrapHeaderView
from .dialogs import ProgramKerjaKategorialDialog


class ProgramKerjaKategorialWidget(QWidget):
    """Widget untuk tab Program Kerja K. Kategorial - program kerja dari kelompok kategorial"""

    data_updated = pyqtSignal()
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.work_programs = []
        self.setup_ui()

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        if db_manager:
            self.load_data()

    def setup_ui(self):
        """Setup UI untuk program kerja K. Kategorial"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title section - transparent background
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                padding: 10px 0px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("Program Kerja Kelompok Kategorial")
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

        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 0, 10, 0)
        content_layout.setSpacing(5)

        # Header with add button
        header = self.create_header()
        content_layout.addWidget(header)

        # Search and Filter section (combined without containers)
        search_filter_layout = self.create_search_filter()
        content_layout.addLayout(search_filter_layout)

        # Table
        table_widget = self.create_table()
        content_layout.addWidget(table_widget, 1)

        # Action buttons
        action_layout = self.create_action_buttons()
        content_layout.addLayout(action_layout, 0)

        layout.addWidget(content_widget)

    def create_header(self):
        """Create header with title and add button"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 5, 10, 5)

        # Title (optional, karena sudah ada di title_frame)
        # Bisa dihapus jika tidak diperlukan

        header_layout.addStretch()

        # Add button - posisi di kanan dengan ikon
        add_button = QPushButton(" Tambah Program Kerja")
        try:
            icon = QIcon("server/assets/tambah.png")
            if not icon.isNull():
                add_button.setIcon(icon)
                add_button.setIconSize(QSize(20, 20))
        except Exception:
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
        add_button.clicked.connect(self.add_program)
        header_layout.addWidget(add_button)

        return header

    def create_search_filter(self):
        """Create search and filter layout without containers"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)

        # Search input
        search_label = QLabel("Cari:")
        layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama program kerja...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.filter_programs)
        layout.addWidget(self.search_input)

        layout.addSpacing(20)

        # Kategori filter
        kategori_label = QLabel("Kategori:")
        layout.addWidget(kategori_label)

        self.kategori_filter = QComboBox()
        self.kategori_filter.addItems(["Semua", "Pastoral", "Sosial", "Pendidikan", "Liturgi", "Keuangan", "Lainnya"])
        self.kategori_filter.setFixedWidth(150)
        self.kategori_filter.currentTextChanged.connect(self.filter_programs)
        layout.addWidget(self.kategori_filter)

        layout.addSpacing(20)

        # Waktu filter
        waktu_label = QLabel("Waktu:")
        layout.addWidget(waktu_label)

        self.waktu_filter = QComboBox()
        months = [
            "Semua Waktu",
            "Januari", "Februari", "Maret", "April",
            "Mei", "Juni", "Juli", "Agustus",
            "September", "Oktober", "November", "Desember"
        ]
        self.waktu_filter.addItems(months)
        self.waktu_filter.setFixedWidth(150)
        self.waktu_filter.currentTextChanged.connect(self.filter_programs)
        layout.addWidget(self.waktu_filter)

        layout.addStretch()

        return layout

    def create_table(self):
        """Create table for program kerja kategorial"""
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

        self.program_table = QTableWidget(0, 9)

        # Set custom header with word wrap and center alignment
        custom_header = WordWrapHeaderView(Qt.Horizontal, self.program_table)
        self.program_table.setHorizontalHeader(custom_header)

        # Column order: Program Kerja, Subyek/Sasaran, Indikator, Model/Bentuk, Materi, Tempat, Waktu, PIC, Total Biaya
        self.program_table.setHorizontalHeaderLabels([
            "Program Kerja", "Subyek/Sasaran", "Indikator Pencapaian", "Model/Bentuk/Metode",
            "Materi", "Tempat", "Waktu", "PIC", "Total Biaya"
        ])

        # Apply professional table styling
        self.apply_professional_table_style(self.program_table)

        # Set column widths
        self.program_table.setColumnWidth(0, 130)   # Program Kerja
        self.program_table.setColumnWidth(1, 120)   # Subyek/Sasaran
        self.program_table.setColumnWidth(2, 120)   # Indikator
        self.program_table.setColumnWidth(3, 140)   # Model/Bentuk/Metode
        self.program_table.setColumnWidth(4, 100)   # Materi
        self.program_table.setColumnWidth(5, 100)   # Tempat
        self.program_table.setColumnWidth(6, 100)   # Waktu
        self.program_table.setColumnWidth(7, 80)    # PIC
        self.program_table.setColumnWidth(8, 120)   # Total Biaya

        header = self.program_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # Update header height when column is resized
        header.sectionResized.connect(lambda idx, old, new: self.update_header_height())

        # Enable context menu
        self.program_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.program_table.customContextMenuRequested.connect(self.show_context_menu)

        # Double click to view detail
        self.program_table.itemDoubleClicked.connect(self.view_program)

        table_layout.addWidget(self.program_table)

        # Initial header height calculation
        QTimer.singleShot(100, self.update_header_height)

        return table_container

    def update_header_height(self):
        """Update header height when column is resized"""
        if hasattr(self, 'program_table'):
            header = self.program_table.horizontalHeader()
            header.setMinimumHeight(25)
            max_height = 25

            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            header.setFixedHeight(max_height)

    def apply_professional_table_style(self, table):
        """Apply Excel-like table styling"""
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

        table.setStyleSheet("""
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

        header = table.horizontalHeader()
        header.setMinimumSectionSize(50)
        header.setDefaultSectionSize(80)

        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        table.verticalHeader().setDefaultSectionSize(24)
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
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        table.setMinimumHeight(200)
        table.setSizePolicy(table.sizePolicy().Expanding, table.sizePolicy().Expanding)

    def create_action_buttons(self):
        """Create action buttons layout dengan style yang konsisten"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        action_layout.setSpacing(5)

        # Detail button dengan ikon
        detail_button = QPushButton(" Lihat Detail")
        try:
            icon = QIcon("server/assets/lihat.png")
            if not icon.isNull():
                detail_button.setIcon(icon)
                detail_button.setIconSize(QSize(16, 16))
        except Exception:
            pass
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
        detail_button.clicked.connect(self.view_program)
        action_layout.addWidget(detail_button)

        # Edit button dengan ikon
        edit_button = QPushButton(" Edit")
        try:
            icon = QIcon("server/assets/edit.png")
            if not icon.isNull():
                edit_button.setIcon(icon)
                edit_button.setIconSize(QSize(16, 16))
        except Exception:
            pass
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
        edit_button.clicked.connect(self.edit_program)
        action_layout.addWidget(edit_button)

        # Delete button dengan ikon
        delete_button = QPushButton(" Hapus")
        try:
            icon = QIcon("server/assets/hapus.png")
            if not icon.isNull():
                delete_button.setIcon(icon)
                delete_button.setIconSize(QSize(16, 16))
        except Exception:
            pass
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
        delete_button.clicked.connect(self.delete_program)
        action_layout.addWidget(delete_button)

        # Export CSV button dengan ikon
        export_csv_button = QPushButton(" .csv")
        try:
            icon = QIcon("server/assets/export.png")
            if not icon.isNull():
                export_csv_button.setIcon(icon)
                export_csv_button.setIconSize(QSize(16, 16))
        except Exception:
            pass
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
        export_csv_button.clicked.connect(self.export_programs)
        action_layout.addWidget(export_csv_button)

        # Refresh button dengan ikon
        refresh_button = QPushButton(" Refresh")
        try:
            icon = QIcon("server/assets/refresh.png")
            if not icon.isNull():
                refresh_button.setIcon(icon)
                refresh_button.setIconSize(QSize(16, 16))
        except Exception:
            pass
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        refresh_button.clicked.connect(self.load_data)
        action_layout.addWidget(refresh_button)

        return action_layout


    def show_context_menu(self, position):
        """Show context menu dengan ikon"""
        if self.program_table.rowCount() == 0:
            return

        menu = QMenu()

        add_action = menu.addAction("➕ Tambah Program Kerja")
        view_action = menu.addAction("👁️ Lihat Detail")
        edit_action = menu.addAction("✏️ Edit Program")
        delete_action = menu.addAction("🗑️ Hapus Program")
        menu.addSeparator()
        export_action = menu.addAction("📄 Export CSV")
        refresh_action = menu.addAction("🔄 Refresh Data")

        action = menu.exec_(self.program_table.mapToGlobal(position))

        if action == add_action:
            self.add_program()
        elif action == view_action:
            self.view_program()
        elif action == edit_action:
            self.edit_program()
        elif action == delete_action:
            self.delete_program()
        elif action == export_action:
            self.export_programs()
        elif action == refresh_action:
            self.load_data()

    def filter_programs(self):
        """Filter programs based on search, kategori, and waktu"""
        search_text = self.search_input.text().lower()
        kategori_filter = self.kategori_filter.currentText()
        waktu_filter = self.waktu_filter.currentText()

        filtered_programs = []

        for program in self.work_programs:
            # Search filter
            if search_text:
                program_name = program.get('program_kerja', '').lower()
                subyek = program.get('subyek_sasaran', '').lower()
                pic = program.get('pic', '').lower()

                if search_text not in program_name and search_text not in subyek and search_text not in pic:
                    continue

            # Kategori filter (based on program_kerja content - simple matching)
            if kategori_filter != "Semua":
                program_kerja = program.get('program_kerja', '').lower()
                if kategori_filter.lower() not in program_kerja:
                    continue

            # Waktu filter (based on waktu field)
            if waktu_filter != "Semua Waktu":
                waktu = program.get('waktu', '').lower()
                if waktu_filter.lower() not in waktu:
                    continue

            filtered_programs.append(program)

        self.populate_table(filtered_programs)

    def populate_table(self, programs):
        """Populate table with program data"""
        self.program_table.setRowCount(0)

        for row_idx, program in enumerate(programs):
            self.program_table.insertRow(row_idx)

            # Column 0: Program Kerja
            program_kerja_item = QTableWidgetItem(program.get('program_kerja', 'N/A'))

            # Column 1: Subyek/Sasaran
            subyek_item = QTableWidgetItem(program.get('subyek_sasaran', 'N/A'))

            # Column 2: Indikator Pencapaian
            indikator_item = QTableWidgetItem(program.get('indikator_pencapaian', 'N/A'))

            # Column 3: Model/Bentuk/Metode
            model_item = QTableWidgetItem(program.get('model_bentuk_metode', 'N/A'))

            # Column 4: Materi
            materi_item = QTableWidgetItem(program.get('materi', 'N/A'))

            # Column 5: Tempat
            tempat_item = QTableWidgetItem(program.get('tempat', 'N/A'))

            # Column 6: Waktu
            waktu_item = QTableWidgetItem(program.get('waktu', 'N/A'))

            # Column 7: PIC
            pic_item = QTableWidgetItem(program.get('pic', 'N/A'))

            # Column 8: Total Biaya
            total = program.get('total', '0')
            if total and str(total).strip():
                try:
                    amount = float(str(total).replace(',', '').replace('.', ''))
                    total_formatted = f"Rp {amount:,.0f}".replace(',', '.')
                except:
                    total_formatted = f"Rp {total}"
            else:
                total_formatted = "Rp 0"
            total_item = QTableWidgetItem(total_formatted)

            # Store data in first column
            program_kerja_item.setData(Qt.UserRole, program)

            # Set items in table
            self.program_table.setItem(row_idx, 0, program_kerja_item)
            self.program_table.setItem(row_idx, 1, subyek_item)
            self.program_table.setItem(row_idx, 2, indikator_item)
            self.program_table.setItem(row_idx, 3, model_item)
            self.program_table.setItem(row_idx, 4, materi_item)
            self.program_table.setItem(row_idx, 5, tempat_item)
            self.program_table.setItem(row_idx, 6, waktu_item)
            self.program_table.setItem(row_idx, 7, pic_item)
            self.program_table.setItem(row_idx, 8, total_item)

        # Select first row if available
        if programs and self.program_table.rowCount() > 0:
            self.program_table.selectRow(0)

    def load_data(self):
        """Load data from database"""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            self.log_message.emit("Memuat data program kerja K. Kategorial dari database...")
            success, result = self.db_manager.get_program_kerja_kategorial_list()

            if success:
                # Handle different response structures
                programs = []

                self.log_message.emit(f"[DEBUG] API Response Type: {type(result)}")
                self.log_message.emit(f"[DEBUG] API Response: {str(result)[:200]}")

                if isinstance(result, list):
                    # Direct list of programs
                    programs = result
                elif isinstance(result, dict):
                    # Check for nested structure: {"data": [...]} or {"data": {"data": [...]}}
                    if 'data' in result:
                        nested = result['data']
                        if isinstance(nested, list):
                            # {"data": [...]}
                            programs = nested
                        elif isinstance(nested, dict) and 'data' in nested:
                            # {"data": {"data": [...]}}
                            programs = nested['data'] if isinstance(nested['data'], list) else []

                self.log_message.emit(f"[DEBUG] Parsed {len(programs)} programs from response")

                self.work_programs = []
                for program in programs:
                    ui_data = {
                        'id': program.get('id_program_kerja_k_kategorial'),
                        'program_kerja': program.get('program_kerja', ''),
                        'subyek_sasaran': program.get('subyek_sasaran', ''),
                        'indikator_pencapaian': program.get('indikator_pencapaian', ''),
                        'model_bentuk_metode': program.get('model_bentuk_metode', ''),
                        'materi': program.get('materi', ''),
                        'tempat': program.get('tempat', ''),
                        'waktu': program.get('waktu', ''),
                        'pic': program.get('pic', ''),
                        'perincian': program.get('perincian', ''),
                        'quantity': program.get('quantity', ''),
                        'satuan': program.get('satuan', ''),
                        'harga_satuan': program.get('harga_satuan', 0),
                        'frekuensi': program.get('frekuensi', 1),
                        'jumlah': program.get('jumlah', 0),
                        'total': program.get('total', 0),
                        'keterangan': program.get('keterangan', ''),
                        'created_by': program.get('created_by'),
                    }
                    self.work_programs.append(ui_data)

                self.filter_programs()
                self.log_message.emit(f"✓ Data program kerja K. Kategorial berhasil dimuat: {len(self.work_programs)} program")
            else:
                self.log_message.emit(f"✗ Gagal memuat data: {result}")

        except Exception as e:
            import traceback
            self.log_message.emit(f"✗ Error loading program kerja K. Kategorial: {str(e)}")
            self.log_message.emit(f"[DEBUG] Traceback: {traceback.format_exc()}")

    def view_program(self):
        """View selected program details"""
        current_row = self.program_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih program yang akan dilihat")
            return

        program_kerja_item = self.program_table.item(current_row, 0)
        if not program_kerja_item or not program_kerja_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Warning", "Data program tidak valid")
            return

        program = program_kerja_item.data(Qt.UserRole)

        dialog = QDialog(self)
        dialog.setWindowTitle("Detail Program Kerja K. Kategorial")
        dialog.setMinimumSize(600, 500)

        layout = QVBoxLayout(dialog)

        detail_text = QTextEdit()
        detail_text.setReadOnly(True)

        detail_html = f"""
        <h2 style="color: #9b59b6;">{program.get('program_kerja', 'N/A')}</h2>
        <hr>
        <p><strong>Subyek/Sasaran:</strong> {program.get('subyek_sasaran', 'N/A')}</p>
        <p><strong>Indikator Pencapaian:</strong> {program.get('indikator_pencapaian', 'N/A')}</p>
        <p><strong>Model/Bentuk/Metode:</strong> {program.get('model_bentuk_metode', 'N/A')}</p>
        <p><strong>Materi:</strong> {program.get('materi', 'N/A')}</p>
        <p><strong>Tempat:</strong> {program.get('tempat', 'N/A')}</p>
        <p><strong>Waktu:</strong> {program.get('waktu', 'N/A')}</p>
        <p><strong>PIC:</strong> {program.get('pic', 'N/A')}</p>
        <p><strong>Quantity:</strong> {program.get('quantity', 'N/A')} {program.get('satuan', '')}</p>
        <p><strong>Harga Satuan:</strong> Rp {program.get('harga_satuan', '0')}</p>
        <p><strong>Frekuensi:</strong> {program.get('frekuensi', '1')}</p>
        <p><strong>Total Biaya:</strong> Rp {program.get('total', '0')}</p>
        <hr>
        <p><strong>Perincian:</strong></p>
        <p>{program.get('perincian', 'Tidak ada perincian')}</p>
        <hr>
        <p><strong>Keterangan:</strong></p>
        <p>{program.get('keterangan', 'Tidak ada keterangan')}</p>
        """

        detail_text.setHtml(detail_html)
        layout.addWidget(detail_text)

        close_button = QPushButton("Tutup")
        close_button.clicked.connect(dialog.accept)  # type: ignore
        layout.addWidget(close_button)

        dialog.exec_()

    def add_program(self):
        """Add new program kerja kategorial"""
        if not self.db_manager:
            QMessageBox.warning(self, "Warning", "Database manager tidak tersedia")
            return

        dialog = ProgramKerjaKategorialDialog(self, None)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            # Validasi required fields
            if not data.get('program_kerja'):
                QMessageBox.warning(self, "Warning", "Program Kerja harus diisi")
                return

            try:
                self.log_message.emit("Menambahkan program kerja kategorial...")
                success, result = self.db_manager.add_program_kerja_kategorial(data)

                if success:
                    self.log_message.emit(f"Program kerja berhasil ditambahkan (ID: {result})")
                    self.load_data()

                    # Show success notification
                    QMessageBox.information(
                        self,
                        "Sukses",
                        f"Program kerja '{data.get('program_kerja')}' berhasil ditambahkan!"
                    )
                else:
                    QMessageBox.critical(self, "Error", f"Gagal menambahkan program: {result}")
                    self.log_message.emit(f"Gagal menambahkan program kerja: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
                self.log_message.emit(f"Error menambahkan program kerja: {str(e)}")

    def edit_program(self):
        """Edit selected program kerja kategorial"""
        current_row = self.program_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih program yang akan diedit")
            return

        program_item = self.program_table.item(current_row, 0)
        if not program_item or not program_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Warning", "Data program tidak valid")
            return

        program = program_item.data(Qt.UserRole)
        program_id = program.get('id')

        if not program_id:
            QMessageBox.warning(self, "Warning", "ID program tidak ditemukan")
            return

        dialog = ProgramKerjaKategorialDialog(self, program)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            # Validasi required fields
            if not data.get('program_kerja'):
                QMessageBox.warning(self, "Warning", "Program Kerja harus diisi")
                return

            try:
                self.log_message.emit("Mengupdate program kerja kategorial...")
                success, result = self.db_manager.update_program_kerja_kategorial(program_id, data)

                if success:
                    self.log_message.emit("Program kerja berhasil diupdate")
                    self.load_data()

                    # Show success notification
                    QMessageBox.information(
                        self,
                        "Sukses",
                        f"Program kerja '{data.get('program_kerja')}' berhasil diperbarui!"
                    )
                else:
                    QMessageBox.critical(self, "Error", f"Gagal mengupdate program: {result}")
                    self.log_message.emit(f"Gagal mengupdate program kerja: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
                self.log_message.emit(f"Error mengupdate program kerja: {str(e)}")

    def delete_program(self):
        """Delete selected program kerja kategorial"""
        current_row = self.program_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih program yang akan dihapus")
            return

        program_item = self.program_table.item(current_row, 0)
        if not program_item or not program_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Warning", "Data program tidak valid")
            return

        program = program_item.data(Qt.UserRole)
        program_id = program.get('id')
        program_name = program.get('program_kerja', 'Unknown')

        if not program_id:
            QMessageBox.warning(self, "Warning", "ID program tidak ditemukan")
            return

        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Hapus program kerja:\n\n{program_name}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.log_message.emit("Menghapus program kerja kategorial...")
                success, result = self.db_manager.delete_program_kerja_kategorial(program_id)

                if success:
                    self.log_message.emit("Program kerja berhasil dihapus")
                    self.load_data()

                    # Show success notification
                    QMessageBox.information(
                        self,
                        "Sukses",
                        f"Program kerja '{program_name}' berhasil dihapus!"
                    )
                else:
                    QMessageBox.critical(self, "Error", f"Gagal menghapus program: {result}")
                    self.log_message.emit(f"Gagal menghapus program kerja: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
                self.log_message.emit(f"Error menghapus program kerja: {str(e)}")

    def export_programs(self):
        """Export programs to CSV"""
        if not self.work_programs:
            QMessageBox.warning(self, "Warning", "Tidak ada data program untuk diekspor")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Program Kerja K. Kategorial", "program_kerja_kategorial.csv", "CSV Files (*.csv)"
        )
        if not filename:
            return

        import csv
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Program Kerja", "Subyek/Sasaran", "Indikator Pencapaian", "Model/Bentuk/Metode",
                    "Materi", "Tempat", "Waktu", "PIC", "Quantity", "Satuan",
                    "Harga Satuan", "Frekuensi", "Total Biaya", "Perincian", "Keterangan"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in self.work_programs:
                    writer.writerow({
                        "Program Kerja": item.get('program_kerja', ''),
                        "Subyek/Sasaran": item.get('subyek_sasaran', ''),
                        "Indikator Pencapaian": item.get('indikator_pencapaian', ''),
                        "Model/Bentuk/Metode": item.get('model_bentuk_metode', ''),
                        "Materi": item.get('materi', ''),
                        "Tempat": item.get('tempat', ''),
                        "Waktu": item.get('waktu', ''),
                        "PIC": item.get('pic', ''),
                        "Quantity": item.get('quantity', ''),
                        "Satuan": item.get('satuan', ''),
                        "Harga Satuan": item.get('harga_satuan', ''),
                        "Frekuensi": item.get('frekuensi', ''),
                        "Total Biaya": item.get('total', ''),
                        "Perincian": item.get('perincian', ''),
                        "Keterangan": item.get('keterangan', ''),
                    })

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data program kerja K. Kategorial diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")

    def get_data(self):
        """Get program data"""
        return self.work_programs
