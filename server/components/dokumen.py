# Path: server/components/dokumen.py

import os
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QHeaderView, QLabel, QPushButton,
                            QLineEdit, QMessageBox, QFrame, QProgressBar, QFileDialog,
                            QApplication, QAbstractItemView, QDialog, QComboBox, QFormLayout,
                            QDialogButtonBox, QMenu, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize, QRect
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter

class WordWrapHeaderView(QHeaderView):
    """Custom header view with word wrap and center alignment support"""
    def __init__(self, orientation, parent=None):  # type: ignore
        super().__init__(orientation, parent)  # type: ignore
        self.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)

    def sectionSizeFromContents(self, logicalIndex):
        """Calculate section size based on wrapped text"""
        if self.model():
            # Get header text
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                # Get current section width
                width = self.sectionSize(logicalIndex)
                if width <= 0:
                    width = self.defaultSectionSize()

                # Create font metrics
                font = self.font()
                font.setBold(True)
                fm = self.fontMetrics()

                # Calculate text rect with word wrap
                rect = fm.boundingRect(0, 0, width - 8, 1000,
                                      Qt.AlignCenter | Qt.TextWordWrap, str(text))

                # Return size with padding
                return QSize(width, max(rect.height() + 12, 25))

        return super().sectionSizeFromContents(logicalIndex)

    def paintSection(self, painter, rect, logicalIndex):
        """Paint section with word wrap and center alignment"""
        painter.save()

        # Draw background with consistent color
        bg_color = QColor(242, 242, 242)  # #f2f2f2
        painter.fillRect(rect, bg_color)

        # Draw borders
        border_color = QColor(212, 212, 212)  # #d4d4d4
        painter.setPen(border_color)
        # Right border
        painter.drawLine(rect.topRight(), rect.bottomRight())
        # Bottom border
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        # Get header text
        if self.model():
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                # Setup font
                font = self.font()
                font.setBold(True)
                painter.setFont(font)

                # Text color
                text_color = QColor(51, 51, 51)  # #333333
                painter.setPen(text_color)

                # Draw text with word wrap and center alignment
                text_rect = rect.adjusted(4, 4, -4, -4)
                painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, str(text))

        painter.restore()

class UploadDialog(QDialog):
    def __init__(self, parent=None):  # type: ignore
        super().__init__(parent)  # type: ignore
        self.setWindowTitle("Upload Dokumen")
        self.setModal(True)
        self.resize(550, 380)  # More compact size
        self.setMinimumWidth(500)

        self.file_path = ""
        self.document_name = ""
        self.document_type = ""
        self.bentuk = ""
        self.keterangan = ""

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(8)  # Reduced spacing

        # ===== FORM CONTENT SECTION =====
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setVerticalSpacing(8)  # Reduced from 10
        form_layout.setHorizontalSpacing(12)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # ===== PILIH DOKUMEN (FILE) =====
        file_label = QLabel("Pilih Dokumen *:")
        file_label.setMinimumWidth(110)
        file_widget = QWidget()
        file_layout = QHBoxLayout(file_widget)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(5)

        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("Belum ada file dipilih...")
        file_layout.addWidget(self.file_input, 1)

        self.browse_button = QPushButton("Pilih File")
        self.browse_button.clicked.connect(self.browse_file)
        self.browse_button.setFixedWidth(80)
        self.browse_button.setFixedHeight(30)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 6px 12px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        file_layout.addWidget(self.browse_button)

        form_layout.addRow(file_label, file_widget)

        # ===== NAMA DOKUMEN (EDITABLE) =====
        nama_label = QLabel("Nama Dokumen *:")
        nama_label.setMinimumWidth(110)
        self.name_input = QLineEdit()
        self.name_input.setReadOnly(False)  # Now editable
        self.name_input.setPlaceholderText("Nama file otomatis muncul di sini, bisa diedit...")
        form_layout.addRow(nama_label, self.name_input)

        # ===== KATEGORI DOKUMEN =====
        jenis_label = QLabel("Kategori Dokumen *:")
        jenis_label.setMinimumWidth(110)
        self.type_combo = QComboBox()
        self.type_combo.addItem("-- Pilih Kategori Dokumen --")  # Default non-selectable placeholder
        self.type_combo.addItems([
            "Dokumen Sakramental & Liturgi",
            "Dokumen Data Umat (Pastoral)",
            "Dokumen Administrasi & Surat-Menyurat",
            "Dokumen Keuangan",
            "Dokumen Aset & Inventaris",
            "Dokumen Organisasi & Program Pastoral",
            "Dokumen Katekese & Pembinaan",
            "Dokumen Kegiatan & Dokumentasi",
            "Dokumen Arsip Digital & Media",
            "Dokumen Lainnya"
        ])
        self.type_combo.setCurrentIndex(0)  # Set to placeholder
        form_layout.addRow(jenis_label, self.type_combo)

        # ===== BENTUK DOKUMEN =====
        bentuk_label = QLabel("Bentuk Dokumen *:")
        bentuk_label.setMinimumWidth(110)
        self.bentuk_combo = QComboBox()
        self.bentuk_combo.addItem("-- Pilih Bentuk Dokumen --")  # Default non-selectable placeholder
        self.bentuk_combo.addItems([
            "Surat Masuk",
            "Surat Keluar",
            "Proposal",
            "Laporan",
            "Laporan Pertanggungjawaban (LPJ)",
            "Notulen",
            "Daftar Hadir",
            "Formulir",
            "Sertifikat/Piagam",
            "Jadwal/Agenda/Calendar",
            "Panduan/Pedoman",
            "SOP (Standar Operasional Prosedur)",
            "Rencana Anggaran",
            "Kuitansi",
            "Invoice/Faktur",
            "Bukti Pembayaran/Bukti Transfer",
            "Daftar Inventaris",
            "Dokumen Kontrak/Perjanjian",
            "Dokumen Legal Aset",
            "Arsip Dokumentasi",
            "Publikasi/Media (poster, brosur, banner, konten medsos)",
            "Database/Spreadsheet Data (arsip digital)",
            "Lainnya"
        ])
        self.bentuk_combo.setCurrentIndex(0)  # Set to placeholder
        form_layout.addRow(bentuk_label, self.bentuk_combo)

        # ===== KETERANGAN (OPTIONAL) =====
        keterangan_label = QLabel("Keterangan:")
        keterangan_label.setMinimumWidth(110)
        keterangan_label.setAlignment(Qt.AlignTop)
        self.keterangan_input = QTextEdit()
        self.keterangan_input.setPlaceholderText("Masukkan deskripsi tentang dokumen ini (opsional)...")
        self.keterangan_input.setMinimumHeight(45)
        self.keterangan_input.setMaximumHeight(65)
        form_layout.addRow(keterangan_label, self.keterangan_input)

        main_layout.addLayout(form_layout)

        # ===== INFO LABEL =====
        info_label = QLabel("* Field wajib diisi")
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 10px;")
        main_layout.addWidget(info_label)

        # ===== BUTTON SECTION =====
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 8, 0, 0)
        button_layout.addStretch()

        self.cancel_button = QPushButton("Batal")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setFixedWidth(85)
        self.cancel_button.setFixedHeight(32)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a7b;
            }
        """)

        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.accept_dialog)
        self.upload_button.setFixedWidth(85)
        self.upload_button.setFixedHeight(32)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 6px 16px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.upload_button)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()  # Add stretch to prevent extra space at bottom
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Dokumen untuk Upload", "",
            "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx);;Excel Files (*.xlsx);;PowerPoint (*.ppt *.pptx);;Images (*.png *.jpg *.jpeg);;Text Files (*.txt)"
        )

        if file_path:
            self.file_input.setText(file_path)
            self.file_path = file_path

            # Selalu isi nama dokumen dengan nama file (termasuk ekstensi)
            file_name = os.path.basename(file_path)
            self.name_input.setText(file_name)
    
    def accept_dialog(self):
        self.document_name = self.name_input.text().strip()
        self.document_type = self.type_combo.currentText()
        self.bentuk = self.bentuk_combo.currentText()
        self.keterangan = self.keterangan_input.toPlainText().strip()

        if not self.document_name:
            QMessageBox.warning(self, "Error", "Nama dokumen harus diisi!")
            return

        if not self.file_path:
            QMessageBox.warning(self, "Error", "File harus dipilih!")
            return

        # Validate kategori dokumen - must not be placeholder
        if self.document_type == "-- Pilih Kategori Dokumen --" or not self.document_type:
            QMessageBox.warning(self, "Error", "Kategori dokumen harus dipilih!")
            return

        # Validate bentuk dokumen - must not be placeholder
        if self.bentuk == "-- Pilih Bentuk Dokumen --" or not self.bentuk:
            QMessageBox.warning(self, "Error", "Bentuk dokumen harus dipilih!")
            return

        self.accept()

class DokumenComponent(QWidget):

    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, parent=None):  # type: ignore
        super().__init__(parent)  # type: ignore
        self.database_manager = None
        self.all_documents = []
        self.filtered_documents = []
        self._user_cache = {}  # Cache untuk mapping user_id ke nama
        self._admin_cache = {}  # Cache untuk mapping admin_id ke nama
        self.current_admin = None
        self.setup_ui()
        self.setup_timer()
    
    def set_database_manager(self, database_manager):
        self.database_manager = database_manager
        self.load_user_cache()  # Load user cache saat database manager di-set
        self.load_data()

    def set_current_admin(self, admin_data):
        """Set the current admin data."""
        self.current_admin = admin_data

    def load_user_cache(self):
        """Load cache untuk mapping user_id dan admin_id ke nama"""
        if not self.database_manager:
            return

        try:
            # Load pengguna (users)
            success, users = self.database_manager.get_pengguna_list()
            if success and users:
                for user in users:
                    user_id = user.get('id_pengguna')
                    nama = user.get('nama_lengkap') or user.get('username')
                    if user_id and nama:
                        self._user_cache[str(user_id)] = nama
                self.log_message.emit(f"Loaded {len(self._user_cache)} users to cache")
        except Exception as e:
            self.log_message.emit(f"Error loading user cache: {str(e)}")

        try:
            # Load admin
            success, admins = self.database_manager.get_admin_list()
            if success and admins:
                for admin in admins:
                    admin_id = admin.get('id_admin')
                    nama = admin.get('nama_lengkap') or admin.get('username')
                    if admin_id and nama:
                        self._admin_cache[str(admin_id)] = nama
                self.log_message.emit(f"Loaded {len(self._admin_cache)} admins to cache")
        except Exception as e:
            self.log_message.emit(f"Error loading admin cache: {str(e)}")

    def get_uploader_name(self, doc):
        """Get nama uploader dari dokumen dengan lookup ke cache"""
        # Cek field nama langsung
        upload_by = (doc.get('uploaded_by_name', '') or
                    doc.get('uploader_name', '') or
                    doc.get('user_name', '') or
                    doc.get('admin_name', ''))

        if upload_by:
            return str(upload_by)

        # Cek ID user dan lookup ke cache
        user_id = (doc.get('uploaded_by', '') or
                  doc.get('user_id', '') or
                  doc.get('id_pengguna', ''))

        if user_id:
            user_id_str = str(user_id)
            # Cek di user cache
            if user_id_str in self._user_cache:
                return self._user_cache[user_id_str]
            # Cek di admin cache
            if user_id_str in self._admin_cache:
                return self._admin_cache[user_id_str]
            # Return User #ID jika tidak ditemukan di cache
            return f"User #{user_id}"

        # Cek admin_id
        admin_id = doc.get('admin_id', '') or doc.get('id_admin', '')
        if admin_id:
            admin_id_str = str(admin_id)
            if admin_id_str in self._admin_cache:
                return self._admin_cache[admin_id_str]
            return f"Admin #{admin_id}"

        return 'System'
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Clean header without background (matching pengaturan style)
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 10, 0)

        title_label = QLabel("Manajemen Dokumen Sistem")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header)
        
        toolbar_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari dokumen...")
        self.search_input.textChanged.connect(self.filter_data)
        toolbar_layout.addWidget(QLabel("Cari:"))
        toolbar_layout.addWidget(self.search_input)
        
        self.upload_button = QPushButton("Upload Dokumen")
        self.upload_button.clicked.connect(self.upload_document)
        # Add upload icon
        upload_icon = QIcon("server/assets/upload.png")
        if not upload_icon.isNull():
            self.upload_button.setIcon(upload_icon)
            self.upload_button.setIconSize(QSize(20, 20))  # Larger icon size for better visibility
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        toolbar_layout.addWidget(self.upload_button)

        # Filter Jenis Dokumen menggunakan QComboBox
        toolbar_layout.addWidget(QLabel("Filter Jenis:"))
        self.filter_doc_type = QComboBox()
        self.filter_doc_type.addItems([
            "Semua",
            "Dokumen Sakramental & Liturgi",
            "Dokumen Data Umat (Pastoral)",
            "Dokumen Administrasi & Surat-Menyurat",
            "Dokumen Keuangan",
            "Dokumen Aset & Inventaris",
            "Dokumen Organisasi & Program Pastoral",
            "Dokumen Katekese & Pembinaan",
            "Dokumen Kegiatan & Dokumentasi",
            "Dokumen Arsip Digital & Media",
            "Dokumen Lainnya"
        ])
        self.filter_doc_type.setFixedWidth(220)
        self.filter_doc_type.currentTextChanged.connect(self.apply_filters)
        toolbar_layout.addWidget(self.filter_doc_type)

        # Filter Jenis File menggunakan QComboBox
        toolbar_layout.addWidget(QLabel("Filter File:"))
        self.filter_file_type = QComboBox()
        self.filter_file_type.addItems(["Semua", ".DOCX", ".PDF", ".TXT", ".XLS", ".PPT", ".JPG", ".JPEG", ".PNG", "Lainnya"])
        self.filter_file_type.setFixedWidth(120)
        self.filter_file_type.currentTextChanged.connect(self.apply_filters)
        toolbar_layout.addWidget(self.filter_file_type)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Table view untuk daftar dokumen with proper container
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
        
        self.table_widget = self.create_professional_table()
        table_layout.addWidget(self.table_widget)
        
        layout.addWidget(table_container)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total dokumen: 0")
        self.size_label = QLabel("Total ukuran: 0 KB")
        self.last_update_label = QLabel("Terakhir diperbarui: -")
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.size_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.last_update_label)
        layout.addLayout(stats_layout)
    
    def create_professional_table(self):
        """Create table with professional styling matching struktur.py."""
        table = QTableWidget(0, 8)

        # Set custom header with word wrap and center alignment
        custom_header = WordWrapHeaderView(Qt.Horizontal, table)
        table.setHorizontalHeader(custom_header)

        table.setHorizontalHeaderLabels([
            "Nama Dokumen", "Jenis Dokumen", "Keterangan", "Ukuran", "Tipe File", "Upload By", "Tanggal Upload", "Aksi"
        ])

        # Apply professional table styling matching struktur.py
        self.apply_professional_table_style(table)

        # Set initial column widths with better proportions for full layout
        table.setColumnWidth(0, 200)   # Nama Dokumen - wider for content
        table.setColumnWidth(1, 130)   # Jenis Dokumen
        table.setColumnWidth(2, 180)   # Keterangan - wider for description text
        table.setColumnWidth(3, 80)    # Ukuran
        table.setColumnWidth(4, 100)   # Tipe File
        table.setColumnWidth(5, 120)   # Upload By
        table.setColumnWidth(6, 130)   # Tanggal Upload
        table.setColumnWidth(7, 100)   # Aksi

        # Excel-like column resizing - all columns can be resized
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # All columns resizable
        header.setStretchLastSection(True)  # Last column stretches to fill space

        # Update header height when column is resized
        header.sectionResized.connect(self.update_header_height)

        # Enable context menu
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu)

        # Initial header height calculation (delayed to ensure proper rendering)
        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

        return table

    def update_header_height(self, logicalIndex, oldSize, newSize):
        """Update header height when column is resized"""
        if hasattr(self, 'table_widget'):
            header = self.table_widget.horizontalHeader()
            # Force header to recalculate height
            header.setMinimumHeight(25)
            max_height = 25

            # Calculate required height for each section
            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            # Set header height to accommodate tallest section
            header.setFixedHeight(max_height)

    def apply_professional_table_style(self, table):
        """Apply Excel-like table styling with thin grid lines and minimal borders."""
        # Header styling - Bold headers with center alignment
        header_font = QFont()
        header_font.setBold(True)  # Make headers bold
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

        # Header with bold text, center alignment, and word wrap
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

        # Configure header behavior
        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        header.setMinimumHeight(25)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(500)

        # Excel-style table body styling
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
                background-color: white;
            }
        """)

        # Excel-style table settings - header configuration
        header = table.horizontalHeader()
        # Header height will adjust based on content wrapping
        header.setDefaultSectionSize(80)

        # Enable scrolling
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Excel-style row settings - keep 32px for action buttons
        table.verticalHeader().setDefaultSectionSize(32)  # Optimized height for action buttons
        table.setSelectionBehavior(QAbstractItemView.SelectItems)  # Select individual cells
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(True)  # Show row numbers like Excel
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

        # Enable grid display with thin lines
        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)

        # Excel-style editing and selection
        table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Set compact size for Excel look
        table.setMinimumHeight(150)
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    def apply_filters(self):
        """Terapkan filter ke dokumen berdasarkan dropdown selections"""
        # Get current filter values from dropdowns
        filter_doc_type = self.filter_doc_type.currentText() if hasattr(self, 'filter_doc_type') else "Semua"
        filter_file_type = self.filter_file_type.currentText() if hasattr(self, 'filter_file_type') else "Semua"

        filtered_docs = self.all_documents.copy()

        # Filter berdasarkan jenis dokumen
        if filter_doc_type != "Semua":
            filtered_docs = [doc for doc in filtered_docs
                           if (doc.get('jenis_dokumen', '') == filter_doc_type or
                               doc.get('document_type', '') == filter_doc_type or
                               doc.get('category', '') == filter_doc_type)]

        # Filter berdasarkan jenis file
        if filter_file_type != "Semua":
            if filter_file_type == "Lainnya":
                common_types = ['.DOCX', '.PDF', '.TXT', '.XLS', '.PPT', '.JPG', '.JPEG', '.PNG']
                filtered_docs = [doc for doc in filtered_docs
                               if not any(doc.get('nama_dokumen', '').upper().endswith(ext) for ext in common_types)]
            else:
                filtered_docs = [doc for doc in filtered_docs
                               if doc.get('nama_dokumen', '').upper().endswith(filter_file_type)]

        self.filtered_documents = filtered_docs
        self.update_table_display(self.filtered_documents)
        self.update_statistics()

    def show_context_menu(self, position):
        """Tampilkan context menu untuk aksi dokumen"""
        if self.table_widget.rowCount() == 0:
            return
            
        menu = QMenu()
        
        view_action = menu.addAction("Lihat Info")
        download_action = menu.addAction("Download")
        delete_action = menu.addAction("Hapus")
        
        action = menu.exec_(self.table_widget.mapToGlobal(position))
        
        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            if action == view_action:
                self.view_document(current_row)
            elif action == download_action:
                self.download_document(current_row)
            elif action == delete_action:
                self.delete_document(current_row)
    
    def setup_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.auto_refresh)
        self.update_timer.start(60000)

    def closeEvent(self, event):
        """Handle close event to stop timer"""
        if hasattr(self, 'update_timer') and self.update_timer:
            self.update_timer.stop()
            self.update_timer.deleteLater()
        event.accept()
    
    def load_data(self):
        if not self.database_manager:
            self.all_documents = []
            self.update_table_display(self.all_documents)
            self.update_statistics()
            self.log_message.emit("Database manager tidak tersedia")
            return
        
        try:
            success, result = self.database_manager.get_files_list()
            
            if success:
                # Check if result is list or dict
                if isinstance(result, list):
                    self.all_documents = result
                elif isinstance(result, dict) and result.get("status") == "success":
                    self.all_documents = result.get("data", [])
                else:
                    self.all_documents = []
                
                # Debug logging - print first document structure
                if self.all_documents and len(self.all_documents) > 0:
                    first_doc = self.all_documents[0]
                    self.log_message.emit(f"DEBUG: Sample document keys: {list(first_doc.keys())}")
                    # Log document type fields specifically
                    doc_type_fields = [k for k in first_doc.keys() if 'dokumen' in k.lower() or 'document' in k.lower() or 'type' in k.lower() or 'category' in k.lower()]
                    if doc_type_fields:
                        self.log_message.emit(f"DEBUG: Document type related fields: {doc_type_fields}")
                        for field in doc_type_fields:
                            self.log_message.emit(f"DEBUG: {field} = '{first_doc.get(field, 'NOT_SET')}'")
                    else:
                        self.log_message.emit("DEBUG: No document type fields found")
                
                # Sort documents berdasarkan tanggal upload (file lama dulu, baru kemudian)
                # Ini memastikan nomor urut sesuai dengan urutan upload
                try:
                    self.all_documents.sort(key=lambda x: x.get('upload_date', '') or x.get('tanggal_upload', '') or '')
                except:
                    pass  # Jika sorting gagal, tetap pakai urutan original
                
                self.filtered_documents = self.all_documents.copy()

                # Reset filter dropdowns ke "Semua"
                if hasattr(self, 'filter_doc_type'):
                    self.filter_doc_type.blockSignals(True)
                    self.filter_doc_type.setCurrentText("Semua")
                    self.filter_doc_type.blockSignals(False)

                if hasattr(self, 'filter_file_type'):
                    self.filter_file_type.blockSignals(True)
                    self.filter_file_type.setCurrentText("Semua")
                    self.filter_file_type.blockSignals(False)

                self.update_table_display(self.filtered_documents)
                self.update_statistics()
                self.log_message.emit(f"Daftar dokumen berhasil dimuat: {len(self.all_documents)} file")
            else:
                self.all_documents = []
                self.update_table_display(self.all_documents)
                self.update_statistics()
                error_msg = str(result) if result else "Unknown error"
                self.log_message.emit(f"Gagal memuat dokumen: {error_msg}")
                
        except Exception as e:
            self.all_documents = []
            self.update_table_display(self.all_documents)
            self.update_statistics()
            self.log_message.emit(f"Error memuat dokumen: {str(e)}")
    
    def update_table_display(self, documents):
        if not documents:
            documents = []
            
        self.table_widget.setRowCount(len(documents))
        
        for i, doc in enumerate(documents):
            # Nama dokumen - prioritas pada nama yang diinput user
            nama_dokumen = (doc.get('nama_dokumen', '') or
                           doc.get('document_name', '') or
                           doc.get('name', '') or
                           doc.get('file_name', '') or
                           doc.get('filename', '') or
                           doc.get('original_name', '') or '')

            # Jika masih kosong, gunakan nama file tanpa path
            if not nama_dokumen:
                file_path = doc.get('file_path', '') or doc.get('path', '') or ''
                if file_path:
                    nama_dokumen = os.path.basename(file_path)
                else:
                    nama_dokumen = 'Unknown Document'

            self.table_widget.setItem(i, 0, QTableWidgetItem(str(nama_dokumen)))
            
            # Jenis dokumen - diambil dari input saat upload dengan fallback yang lebih lengkap
            jenis_dokumen = (doc.get('jenis_dokumen', '') or 
                           doc.get('document_type', '') or 
                           doc.get('category', '') or 
                           doc.get('type', '') or 
                           doc.get('doc_type', '') or
                           doc.get('file_category', '') or
                           doc.get('document_category', '') or '')
            
            # Debug logging untuk jenis dokumen
            if i == 0 and not jenis_dokumen:  # Hanya log jika document type kosong
                self.log_message.emit(f"WARNING: Document type empty for first document")
                available_keys = [k for k in doc.keys() if 'jenis' in k.lower() or 'dokumen' in k.lower() or 'document' in k.lower() or 'type' in k.lower() or 'category' in k.lower()]
                if available_keys:
                    self.log_message.emit(f"Available type-related keys: {available_keys}")
                    for key in available_keys:
                        value = doc.get(key, '')
                        self.log_message.emit(f"  {key}: '{value}'")
            
            self.table_widget.setItem(i, 1, QTableWidgetItem(str(jenis_dokumen)))

            # Keterangan
            keterangan = doc.get('keterangan', '') or ''
            # Truncate long description for table display
            if len(keterangan) > 50:
                keterangan_display = keterangan[:47] + "..."
            else:
                keterangan_display = keterangan
            keterangan_item = QTableWidgetItem(str(keterangan_display))
            keterangan_item.setToolTip(str(keterangan))  # Show full text on hover
            self.table_widget.setItem(i, 2, keterangan_item)

            # Ukuran file
            size_bytes = doc.get('ukuran_file', 0) or doc.get('file_size', 0) or doc.get('size', 0) or 0
            try:
                size_bytes = int(size_bytes)
                if size_bytes > 1048576:
                    size_str = f"{size_bytes / 1048576:.2f} MB"
                elif size_bytes > 1024:
                    size_str = f"{size_bytes / 1024:.2f} KB"
                else:
                    size_str = f"{size_bytes} B"
            except (ValueError, TypeError):
                size_str = "0 B"
            self.table_widget.setItem(i, 3, QTableWidgetItem(size_str))

            # Tipe file - diambil dari ekstensi file
            file_type = doc.get('tipe_file', '') or doc.get('mime_type', '') or doc.get('content_type', '') or ''
            file_name = doc.get('nama_dokumen', '') or doc.get('file_name', '') or doc.get('filename', '') or ''
            
            # Jika file_type kosong, coba ambil dari ekstensi file
            if not file_type and file_name:
                file_extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
                if file_extension == 'pdf':
                    type_display = "PDF"
                elif file_extension in ['docx', 'doc']:
                    type_display = "Word"
                elif file_extension in ['xlsx', 'xls']:
                    type_display = "Excel"
                elif file_extension in ['pptx', 'ppt']:
                    type_display = "PowerPoint"
                elif file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                    type_display = "Image"
                elif file_extension == 'txt':
                    type_display = "Text"
                else:
                    type_display = file_extension.upper() if file_extension else "Unknown"
            else:
                # Parse dari mime type
                if 'pdf' in file_type.lower():
                    type_display = "PDF"
                elif 'word' in file_type.lower() or 'document' in file_type.lower():
                    type_display = "Word"
                elif 'excel' in file_type.lower() or 'sheet' in file_type.lower():
                    type_display = "Excel"
                elif 'powerpoint' in file_type.lower() or 'presentation' in file_type.lower():
                    type_display = "PowerPoint"
                elif 'image' in file_type.lower():
                    type_display = "Image"
                elif 'text' in file_type.lower():
                    type_display = "Text"
                else:
                    type_display = file_type.split('/')[-1].upper() if '/' in file_type else file_type or "Unknown"

            self.table_widget.setItem(i, 4, QTableWidgetItem(type_display))

            # Upload by - gunakan method get_uploader_name untuk lookup yang benar
            upload_by = self.get_uploader_name(doc)
            self.table_widget.setItem(i, 5, QTableWidgetItem(str(upload_by)))
            
            # Tanggal upload
            upload_date = (doc.get('upload_date', '') or 
                          doc.get('tanggal_upload', '') or 
                          doc.get('created_at', '') or 
                          doc.get('date_uploaded', '') or '')
            if upload_date:
                if isinstance(upload_date, str):
                    try:
                        parsed_date = datetime.datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                        date_str = parsed_date.strftime('%d/%m/%Y %H:%M')
                    except:
                        date_str = str(upload_date)
                else:
                    date_str = str(upload_date)
            else:
                date_str = "-"
            self.table_widget.setItem(i, 6, QTableWidgetItem(date_str))

            # Aksi buttons with icons - improved sizing and perfect centering
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(3, 3, 3, 3)  # Balanced margins for perfect centering
            action_layout.setSpacing(3)  # Compact spacing between buttons
            action_layout.setAlignment(Qt.AlignCenter)  # Center align buttons

            # View button with lihat.png icon - smaller, more balanced sizing
            view_button = QPushButton()
            view_icon = QIcon("server/assets/lihat.png")
            if not view_icon.isNull():
                view_button.setIcon(view_icon)
                view_button.setIconSize(QSize(12, 12))  # Smaller icon size
            else:
                view_button.setText("👁")  # Fallback emoji if icon not found
                view_button.setStyleSheet("""
                    QPushButton {
                        font-size: 10px;
                    }
                """)
            view_button.setFixedSize(22, 22)  # Fixed square size for consistency
            view_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 2px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
            """)
            view_button.setToolTip("Lihat Info Dokumen")
            view_button.clicked.connect(lambda _, row=i: self.view_document(row))
            action_layout.addWidget(view_button)

            # Download button with unduh.png icon - smaller, more balanced sizing
            download_button = QPushButton()
            download_icon = QIcon("server/assets/unduh.png")
            if not download_icon.isNull():
                download_button.setIcon(download_icon)
                download_button.setIconSize(QSize(12, 12))  # Smaller icon size
            else:
                download_button.setText("⬇")  # Fallback emoji if icon not found
                download_button.setStyleSheet("""
                    QPushButton {
                        font-size: 10px;
                    }
                """)
            download_button.setFixedSize(22, 22)  # Fixed square size for consistency
            download_button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 2px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
            """)
            download_button.setToolTip("Download Dokumen")
            download_button.clicked.connect(lambda _, row=i: self.download_document(row))
            action_layout.addWidget(download_button)

            # Delete button with hapus.png icon - smaller, more balanced sizing
            delete_button = QPushButton()
            delete_icon = QIcon("server/assets/hapus.png")
            if not delete_icon.isNull():
                delete_button.setIcon(delete_icon)
                delete_button.setIconSize(QSize(12, 12))  # Smaller icon size
            else:
                delete_button.setText("🗑")  # Fallback emoji if icon not found
                delete_button.setStyleSheet("""
                    QPushButton {
                        font-size: 10px;
                    }
                """)
            delete_button.setFixedSize(22, 22)  # Fixed square size for consistency
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 2px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            delete_button.setToolTip("Hapus Dokumen")
            delete_button.clicked.connect(lambda _, row=i: self.delete_document(row))
            action_layout.addWidget(delete_button)

            self.table_widget.setCellWidget(i, 7, action_widget)
    
    def filter_data(self):
        search_text = self.search_input.text().lower()
        
        if not search_text:
            self.apply_filters()
        else:
            filtered_docs = []
            source_docs = self.filtered_documents if hasattr(self, 'filtered_documents') else self.all_documents
            
            for doc in source_docs:
                # Nama dokumen dengan mapping yang sama seperti di update_table_display
                nama_dokumen = (doc.get('nama_dokumen', '') or
                               doc.get('document_name', '') or
                               doc.get('name', '') or
                               doc.get('file_name', '') or
                               doc.get('filename', '') or
                               doc.get('original_name', '') or '')

                # Upload by - gunakan method get_uploader_name
                uploaded_by = self.get_uploader_name(doc)

                tipe_file = doc.get('tipe_file', '') or doc.get('mime_type', '') or doc.get('content_type', '') or ''
                jenis_dokumen = (doc.get('jenis_dokumen', '') or
                               doc.get('document_type', '') or
                               doc.get('category', '') or '')
                keterangan = doc.get('keterangan', '') or ''

                if (search_text in nama_dokumen.lower() or
                    search_text in uploaded_by.lower() or
                    search_text in tipe_file.lower() or
                    search_text in jenis_dokumen.lower() or
                    search_text in keterangan.lower()):
                    filtered_docs.append(doc)
            
            self.update_table_display(filtered_docs)
            self.total_label.setText(f"Total dokumen: {len(filtered_docs)}")
    
    def update_statistics(self):
        total_docs = len(self.all_documents)
        total_size = 0
        
        for doc in self.all_documents:
            size = doc.get('ukuran_file', 0) or doc.get('file_size', 0) or doc.get('size', 0) or 0
            try:
                total_size += int(size)
            except (ValueError, TypeError):
                continue
        
        if total_size > 1048576:
            size_str = f"{total_size / 1048576:.2f} MB"
        elif total_size > 1024:
            size_str = f"{total_size / 1024:.2f} KB"
        else:
            size_str = f"{total_size} B"
        
        self.total_label.setText(f"Total dokumen: {total_docs}")
        self.size_label.setText(f"Total ukuran: {size_str}")
        self.last_update_label.setText(f"Terakhir diperbarui: {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    def view_document(self, row):
        """Preview dokumen - download dan tampilkan preview"""
        current_docs = self.filtered_documents if hasattr(self, 'filtered_documents') else self.all_documents
        if row < len(current_docs):
            doc = current_docs[row]
            doc_name = (doc.get('nama_dokumen', '') or
                       doc.get('document_name', '') or
                       doc.get('name', '') or
                       doc.get('file_name', '') or
                       doc.get('filename', '') or 'document')

            doc_id = doc.get('id_dokumen') or doc.get('file_id') or doc.get('id')

            if not doc_id:
                QMessageBox.warning(self, "Error", "ID dokumen tidak ditemukan")
                return

            if not self.database_manager:
                QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                return

            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            try:
                self.log_message.emit(f"Mengunduh dokumen untuk preview: {doc_name}")
                self.progress_bar.setValue(25)
                QApplication.processEvents()

                success, result = self.database_manager.download_file_from_api(doc_id)

                self.progress_bar.setValue(75)
                QApplication.processEvents()

                if success:
                    file_content = result.get('content')
                    if file_content and isinstance(file_content, bytes):
                        self.progress_bar.setValue(100)
                        QApplication.processEvents()

                        # Tampilkan preview berdasarkan tipe file
                        self.show_document_preview(doc_name, file_content)
                        self.log_message.emit(f"Preview dokumen: {doc_name}")
                    else:
                        QMessageBox.critical(self, "Error", "Format file tidak valid dari server")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal mengunduh dokumen: {result}")
                    self.log_message.emit(f"Error preview dokumen: {result}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal preview dokumen: {str(e)}")
                self.log_message.emit(f"Error preview dokumen: {str(e)}")
            finally:
                self.progress_bar.setVisible(False)

    def show_document_preview(self, filename, content):
        """Tampilkan preview dokumen dalam dialog"""
        # Deteksi tipe file dari nama
        file_ext = os.path.splitext(filename)[1].lower()

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Preview: {filename}")
        dialog.resize(800, 600)

        layout = QVBoxLayout(dialog)

        if file_ext in ['.txt', '.log', '.md', '.csv']:
            # Preview teks
            try:
                text_content = content.decode('utf-8', errors='ignore')
                text_edit = QTextEdit()
                text_edit.setReadOnly(True)
                text_edit.setPlainText(text_content)
                layout.addWidget(text_edit)
            except Exception as e:
                error_label = QLabel(f"Error menampilkan teks: {str(e)}")
                layout.addWidget(error_label)

        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            # Preview gambar
            try:
                from PyQt5.QtGui import QPixmap
                from PyQt5.QtWidgets import QScrollArea

                pixmap = QPixmap()
                pixmap.loadFromData(content)

                if not pixmap.isNull():
                    image_label = QLabel()
                    image_label.setPixmap(pixmap)
                    image_label.setScaledContents(False)

                    scroll_area = QScrollArea()
                    scroll_area.setWidget(image_label)
                    scroll_area.setWidgetResizable(True)
                    layout.addWidget(scroll_area)
                else:
                    error_label = QLabel("Gagal memuat gambar")
                    layout.addWidget(error_label)
            except Exception as e:
                error_label = QLabel(f"Error menampilkan gambar: {str(e)}")
                layout.addWidget(error_label)

        elif file_ext == '.pdf':
            # Untuk PDF, tampilkan pesan dan tombol untuk membuka eksternal
            info_label = QLabel(f"<b>File PDF: {filename}</b><br><br>"
                              "Preview PDF tidak didukung secara langsung.<br>"
                              "Silakan download file untuk melihat isinya.")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

        else:
            # File lain yang tidak didukung preview
            info_label = QLabel(f"<b>File: {filename}</b><br><br>"
                              f"Tipe file: {file_ext}<br>"
                              f"Ukuran: {len(content)} bytes<br><br>"
                              "Preview tidak didukung untuk tipe file ini.<br>"
                              "Silakan download file untuk melihat isinya.")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.clicked.connect(dialog.close)  # type: ignore
        layout.addWidget(button_box)

        dialog.exec_()
    
    def download_document(self, row):
        current_docs = self.filtered_documents if hasattr(self, 'filtered_documents') else self.all_documents
        if row < len(current_docs):
            doc = current_docs[row]
            # Gunakan mapping yang konsisten dengan display
            doc_name = (doc.get('nama_dokumen', '') or
                       doc.get('document_name', '') or
                       doc.get('name', '') or
                       doc.get('file_name', '') or
                       doc.get('filename', '') or 'document')

            doc_id = doc.get('id_dokumen') or doc.get('file_id') or doc.get('id')
            
            if not doc_id:
                QMessageBox.warning(self, "Error", "ID dokumen tidak ditemukan")
                return
            
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Simpan Dokumen", doc_name, 
                "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx);;Excel Files (*.xlsx)"
            )
            
            if save_path:
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                
                try:
                    if self.database_manager:
                        self.progress_bar.setValue(25)
                        QApplication.processEvents()
                        
                        success, result = self.database_manager.download_file_from_api(doc_id)
                        
                        self.progress_bar.setValue(75)
                        QApplication.processEvents()
                        
                        if success:
                            file_content = result.get('content')
                            if file_content and isinstance(file_content, bytes):
                                try:
                                    with open(save_path, 'wb') as f:
                                        f.write(file_content)
                                    
                                    self.progress_bar.setValue(100)
                                    QApplication.processEvents()
                                    
                                    QMessageBox.information(self, "Download", 
                                        f"File berhasil didownload ke: {save_path}")
                                    self.log_message.emit(f"File berhasil didownload: {doc_name}")
                                    
                                except Exception as e:
                                    self.log_message.emit(f"Error saving file: {str(e)}")
                                    QMessageBox.critical(self, "Error", f"Gagal menyimpan file: {str(e)}")
                            else:
                                self.log_message.emit(f"ERROR: Invalid file content - type: {type(file_content)}")
                                QMessageBox.critical(self, "Error", "Format file tidak valid dari server")
                        else:
                            QMessageBox.critical(self, "Error", f"Gagal download dokumen: {result}")
                            self.log_message.emit(f"Error download dokumen: {result}")
                    else:
                        QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Gagal download dokumen: {str(e)}")
                    self.log_message.emit(f"Error download dokumen: {str(e)}")
                finally:
                    self.progress_bar.setVisible(False)
    
    def delete_document(self, row):
        current_docs = self.filtered_documents if hasattr(self, 'filtered_documents') else self.all_documents
        if row < len(current_docs):
            doc = current_docs[row]
            # Gunakan mapping yang konsisten dengan display
            doc_name = (doc.get('nama_dokumen', '') or
                       doc.get('document_name', '') or
                       doc.get('name', '') or
                       doc.get('file_name', '') or
                       doc.get('filename', '') or 'Unknown')

            doc_id = doc.get('id_dokumen') or doc.get('file_id') or doc.get('id')
            
            if not doc_id:
                QMessageBox.warning(self, "Error", "ID dokumen tidak ditemukan")
                return
            
            reply = QMessageBox.question(
                self, "Konfirmasi Hapus", 
                f"Yakin ingin menghapus dokumen '{doc_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    if self.database_manager:
                        success, result = self.database_manager.delete_file(doc_id)
                        if success:
                            QMessageBox.information(self, "Sukses", "Dokumen berhasil dihapus")
                            self.load_data()
                            self.log_message.emit(f"Dokumen dihapus: {doc_name}")
                        else:
                            QMessageBox.critical(self, "Error", f"Gagal menghapus dokumen: {result}")
                            self.log_message.emit(f"Error hapus dokumen: {result}")
                    else:
                        QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error menghapus dokumen: {str(e)}")
                    self.log_message.emit(f"Exception hapus dokumen: {str(e)}")
    
    def upload_document(self):
        # Tampilkan dialog upload
        dialog = UploadDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            self.log_message.emit("Upload dibatalkan oleh user")
            return

        file_path = dialog.file_path
        document_name = dialog.document_name
        document_type = dialog.document_type
        bentuk = dialog.bentuk
        keterangan = dialog.keterangan

        if not self.database_manager:
            QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
            self.log_message.emit("Error: Database manager tidak tersedia untuk upload")
            return

        # Check if upload_file method exists
        if not hasattr(self.database_manager, 'upload_file'):
            QMessageBox.critical(self, "Error", "Method upload_file tidak ditemukan di database manager")
            self.log_message.emit("Error: Method upload_file tidak tersedia")
            return

        # Validate file exists and accessible
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", "File tidak ditemukan")
            self.log_message.emit(f"Error: File tidak ditemukan - {file_path}")
            return

        try:
            # Check file size (max 50MB)
            file_size = os.path.getsize(file_path)
            self.log_message.emit(f"Ukuran file: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")

            if file_size > 52428800:  # 50MB
                QMessageBox.warning(self, "Error", "Ukuran file terlalu besar (max 50MB)")
                self.log_message.emit(f"Error: File terlalu besar - {file_size} bytes")
                return
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal mengecek ukuran file: {str(e)}")
            self.log_message.emit(f"Error mengecek ukuran file: {str(e)}")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        try:
            self.log_message.emit(f"Memulai upload file: {document_name}")
            self.log_message.emit(f"DEBUG Upload - document_name: '{document_name}'")
            self.log_message.emit(f"DEBUG Upload - document_type: '{document_type}'")
            self.log_message.emit(f"DEBUG Upload - bentuk: '{bentuk}'")
            self.log_message.emit(f"DEBUG Upload - keterangan: '{keterangan}'")
            self.log_message.emit(f"DEBUG Upload - file_path: '{file_path}'")

            # Progress simulation
            for i in range(1, 51, 10):
                self.progress_bar.setValue(i)
                QApplication.processEvents()

            self.log_message.emit("Memanggil database_manager.upload_file...")

            # Upload file melalui API dengan informasi tambahan
            try:
                # Try with new parameters first (including bentuk and keterangan)
                success, result = self.database_manager.upload_file(
                    file_path,
                    document_name=document_name,
                    document_type=document_type,
                    keterangan=keterangan,
                    bentuk=bentuk
                )
                self.log_message.emit(f"DEBUG Upload - API call dengan parameter berhasil")
            except TypeError:
                # Fallback to old method if new parameters not supported
                self.log_message.emit("Database manager belum mendukung parameter keterangan, mencoba tanpa keterangan...")
                try:
                    success, result = self.database_manager.upload_file(
                        file_path,
                        document_name=document_name,
                        document_type=document_type
                    )
                except TypeError:
                    # Final fallback to basic method
                    self.log_message.emit("Database manager belum mendukung parameter baru, menggunakan method lama...")
                    success, result = self.database_manager.upload_file(file_path)
            
            self.progress_bar.setValue(75)
            QApplication.processEvents()
            
            self.log_message.emit(f"Hasil upload - Success: {success}, Result: {result}")
            
            if success:
                self.progress_bar.setValue(100)
                QApplication.processEvents()
                
                QMessageBox.information(self, "Sukses", f"Dokumen '{document_name}' berhasil diupload!")
                self.log_message.emit(f"Dokumen {document_name} ({document_type}) berhasil diupload")
                self.load_data()
            else:
                error_msg = str(result) if result else "Unknown error"
                QMessageBox.critical(self, "Error", f"Gagal upload dokumen: {error_msg}")
                self.log_message.emit(f"Gagal upload dokumen: {error_msg}")
        except AttributeError as e:
            error_msg = f"Method tidak ditemukan: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            self.log_message.emit(f"AttributeError upload dokumen: {error_msg}")
        except Exception as e:
            error_msg = f"Error upload dokumen: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            self.log_message.emit(f"Exception upload dokumen: {error_msg}")
        finally:
            self.progress_bar.setVisible(False)
    
    def auto_refresh(self):
        try:
            self.load_data()
        except Exception:
            # Silently ignore errors during auto-refresh to prevent warnings
            pass
    
    def get_data(self):
        return self.all_documents