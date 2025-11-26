# Path: server/components/jemaat.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFileDialog, QAbstractItemView, QFrame,
                            QScrollArea, QSplitter)
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize, QRect, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPainter

# Import dialog secara langsung untuk menghindari circular import
from .dialogs import JemaatDialog

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

class JemaatComponent(QWidget):
    """Komponen untuk manajemen data jemaat"""
    
    data_updated = pyqtSignal()  # Signal ketika data berubah
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore  # Signal untuk mengirim log message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.jemaat_data = []
        self.db_manager = None
        self.current_admin = None  # Tambahkan ini
        self._pengguna_lookup = {}
        self._pengguna_lookup_attempted = False
        self.setup_ui()

    def set_current_admin(self, admin_data):
        """Set the current admin data."""
        self.current_admin = admin_data

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
    
    def setup_ui(self):
        """Setup UI untuk halaman jemaat"""
        layout = QVBoxLayout(self)
        
        # Clean header without background (matching pengaturan style)
        header_frame = QWidget()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 10, 0)

        title_label = QLabel("Database Umat")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header_frame)
        
        # Original header with buttons
        header = self.create_header()
        layout.addWidget(header)
        
        # Create Excel-like spreadsheet grid with frozen headers and columns
        self.create_spreadsheet_grid(layout)
        
        # Tombol aksi
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)
    
    def show_context_menu(self, position):
        """Tampilkan context menu untuk edit/hapus"""
        sender = self.sender()
        if sender.rowCount() == 0:
            return
            
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")
        view_details_action = menu.addAction("Lihat Detail")
        
        action = menu.exec_(sender.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_jemaat()
        elif action == delete_action:
            self.delete_jemaat()
        elif action == view_details_action:
            self.view_jemaat_details()
    
    def create_header(self):
        """Buat header dengan kontrol (tanpa title karena sudah ada di header frame)"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 10, 0)  # Add right margin for spacing

        # Search functionality dengan label
        header_layout.addWidget(QLabel("Cari:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari umat...")
        self.search_input.setFixedWidth(300)
        # Gunakan textChanged untuk real-time search seperti di struktur
        self.search_input.textChanged.connect(self.filter_data)
        header_layout.addWidget(self.search_input)

        # Filter Wilayah Rohani menggunakan QComboBox
        header_layout.addWidget(QLabel("Filter Wilayah:"))

        from PyQt5.QtWidgets import QComboBox
        self.filter_wilayah = QComboBox()
        wilayah_list = [
            "Semua",
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
        self.filter_wilayah.addItems(wilayah_list)
        self.filter_wilayah.setFixedWidth(200)
        self.filter_wilayah.currentTextChanged.connect(self.filter_data)
        header_layout.addWidget(self.filter_wilayah)

        # Filter Kategori menggunakan QComboBox
        header_layout.addWidget(QLabel("Filter Kategori:"))

        self.filter_kategori = QComboBox()
        kategori_list = ["Semua", "Balita", "Anak-anak", "Remaja", "OMK", "KBK", "KIK", "Lansia"]
        self.filter_kategori.addItems(kategori_list)
        self.filter_kategori.setFixedWidth(150)
        self.filter_kategori.currentTextChanged.connect(self.filter_data)
        header_layout.addWidget(self.filter_kategori)

        header_layout.addStretch()

        add_button = self.create_button("Tambah Umat", "#27ae60", self.add_jemaat, "server/assets/tambah.png")
        header_layout.addWidget(add_button)

        return header
    
    def create_action_buttons(self):
        """Buat tombol-tombol aksi"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        edit_button = self.create_button("Edit Terpilih", "#f39c12", self.edit_jemaat, "server/assets/edit.png")
        action_layout.addWidget(edit_button)

        delete_button = self.create_button("Hapus Terpilih", "#c0392b", self.delete_jemaat, "server/assets/hapus.png")
        action_layout.addWidget(delete_button)

        export_button = self.create_button("Export Data", "#16a085", self.export_jemaat, "server/assets/export.png")
        action_layout.addWidget(export_button)

        broadcast_button = self.create_button("Broadcast ke Client", "#8e44ad", self.broadcast_jemaat, "server/assets/tambah.png")
        action_layout.addWidget(broadcast_button)

        return action_layout


    def create_button(self, text, color, slot, icon_path=None):
        """Buat button dengan style konsisten dan optional icon"""
        button = QPushButton(text)
        
        # Add icon if specified and path exists
        if icon_path:
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(20, 20))  # Larger icon size for better visibility
            except Exception:
                pass  # If icon loading fails, just continue without icon
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        button.clicked.connect(slot)
        return button
    
    def darken_color(self, color):
        """Buat warna lebih gelap untuk hover effect"""
        color_map = {
            "#3498db": "#2980b9",
            "#27ae60": "#2ecc71", 
            "#f39c12": "#f1c40f",
            "#c0392b": "#e74c3c",
            "#16a085": "#1abc9c",
            "#8e44ad": "#9b59b6"
        }
        return color_map.get(color, color)
    
    def load_data(self):
        """Load data jemaat dari database"""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            # Load semua data tanpa search filter untuk caching
            success, result = self.db_manager.get_jemaat_list(limit=1000, search=None)

            if success:
                # Simpan ke all_jemaat_data untuk filtering
                self.all_jemaat_data = result.copy() if result else []
                self.jemaat_data = result if result else []

                # Reset filter dropdowns ke "Semua"
                if hasattr(self, 'filter_wilayah'):
                    self.filter_wilayah.blockSignals(True)
                    self.filter_wilayah.setCurrentText("Semua")
                    self.filter_wilayah.blockSignals(False)

                if hasattr(self, 'filter_kategori'):
                    self.filter_kategori.blockSignals(True)
                    self.filter_kategori.setCurrentText("Semua")
                    self.filter_kategori.blockSignals(False)

                self.populate_table()
                self.log_message.emit(f"Data jemaat berhasil dimuat: {len(self.jemaat_data)} record")
                self.data_updated.emit()
            else:
                self.all_jemaat_data = []
                self.jemaat_data = []
                self.log_message.emit(f"Error loading jemaat data: {result}")
                QMessageBox.warning(self, "Error", f"Gagal memuat data jemaat: {result}")
        except Exception as e:
            self.all_jemaat_data = []
            self.jemaat_data = []
            self.log_message.emit(f"Exception loading jemaat data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error loading jemaat data: {str(e)}")
    
    def create_spreadsheet_grid(self, layout):
        """Create table with custom header view for proper word wrap"""
        # Create table with 38 columns (without No column) - added No. KK and NIK, start with 0 data rows
        self.jemaat_table = QTableWidget(0, 38)

        # Set custom header with word wrap and center alignment
        custom_header = WordWrapHeaderView(Qt.Horizontal, self.jemaat_table)
        self.jemaat_table.setHorizontalHeader(custom_header)

        # Show row numbers like Excel
        self.jemaat_table.verticalHeader().setVisible(True)

        # Set up single-row headers (resizable)
        self.setup_table_headers()

        # Configure table styling
        self.apply_professional_table_style(self.jemaat_table)

        # Setup column widths
        self.setup_column_widths()

        # Enable header features for resizing
        header = self.jemaat_table.horizontalHeader()
        header.setVisible(True)
        header.setSectionResizeMode(QHeaderView.Interactive)  # Enable drag to resize
        header.setStretchLastSection(True)  # Stretch last column
        header.setSectionsMovable(False)  # Disable column reordering

        # Update header height when column is resized
        header.sectionResized.connect(self.update_header_height)

        # Enable context menu
        self.jemaat_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.jemaat_table.customContextMenuRequested.connect(self.show_context_menu)

        # Table container for proper alignment
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

        table_layout.addWidget(self.jemaat_table)
        layout.addWidget(table_container)

        # Initial header height calculation (delayed to ensure proper rendering)
        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

    def update_header_height(self, logicalIndex, oldSize, newSize):
        """Update header height when column is resized"""
        if hasattr(self, 'jemaat_table'):
            header = self.jemaat_table.horizontalHeader()
            # Force header to recalculate height
            header.setMinimumHeight(25)
            max_height = 25

            # Calculate required height for each section
            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            # Set header height to accommodate tallest section
            header.setFixedHeight(max_height)

    def setup_table_headers(self):
        """Set up table headers like struktur.py with proper column names"""
        # Define all column headers in order (without No column - 38 columns total)
        # Added No. KK after Nama Keluarga dan NIK after Nama Lengkap
        column_headers = [
            # DATA PRIBADI (columns 0-17)
            "Wilayah Rohani", "Nama Keluarga", "No. KK", "Nama Lengkap", "NIK", "Tempat Lahir",
            "Tanggal Lahir", "Umur", "Status Kekatolikan", "Kategori", "J. Kelamin",
            "Hubungan Keluarga", "Pend. Terakhir", "Status Menikah", "Status Pekerjaan",
            "Detail Pekerjaan", "Alamat", "Email/No.Hp",
            # SAKRAMEN BABTIS (columns 18-21)
            "Status Babtis", "Tempat Babtis", "Tanggal Babtis", "Nama Babtis",
            # SAKRAMEN EKARISTI (columns 22-24)
            "Status Ekaristi", "Tempat Komuni", "Tanggal Komuni",
            # SAKRAMEN KRISMA (columns 25-27)
            "Status Krisma", "Tempat Krisma", "Tanggal Krisma",
            # SAKRAMEN PERKAWINAN (columns 28-33)
            "Status Perkawinan", "Keuskupan", "Paroki", "Kota", "Tanggal Perkawinan", "Status Perkawinan Detail",
            # STATUS (columns 34-37) - TOTAL 38 COLUMNS
            "Status Keanggotaan", "WR Tujuan", "Paroki Tujuan", "Created By Pengguna"
        ]

        # Set column headers
        self.jemaat_table.setHorizontalHeaderLabels(column_headers)

        # Set initial column widths
        self.setup_column_widths()

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

        # Excel-style row settings
        table.verticalHeader().setDefaultSectionSize(20)  # Thin rows like Excel
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

    def setup_column_widths(self):
        """Set up column widths for better display (38 columns total with No. KK and NIK)"""
        # Make important columns wider (adjusted indices for new columns)
        self.jemaat_table.setColumnWidth(1, 120)  # Nama Keluarga
        self.jemaat_table.setColumnWidth(2, 110)  # No. KK
        self.jemaat_table.setColumnWidth(3, 150)  # Nama Lengkap - wider
        self.jemaat_table.setColumnWidth(4, 110)  # NIK
        self.jemaat_table.setColumnWidth(16, 180)  # Alamat - wider
        self.jemaat_table.setColumnWidth(17, 140)  # Kontak - wider

        # Set standard width for other columns
        for i in [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:  # DATA columns
            self.jemaat_table.setColumnWidth(i, 110)
        for i in range(18, 38):  # Sakramen and Status columns
            self.jemaat_table.setColumnWidth(i, 100)

        # Make creator column slightly wider for names
        self.jemaat_table.setColumnWidth(37, 160)

    def populate_table(self):
        """Populate table with data rows (using normal headers)"""
        # Set row count: only data rows (headers are in QHeaderView)
        self.jemaat_table.setRowCount(len(self.jemaat_data))

        # Populate data starting from row 0
        for index, row_data in enumerate(self.jemaat_data):
            row_pos = index  # Start from row 0

            # All data columns (0-37, tanpa kolom No) - TOTAL 38 COLUMNS with No. KK and NIK
            data_items = [
                # DATA PRIBADI (columns 0-17) - added No. KK and NIK
                self.format_display(row_data.get('wilayah_rohani')),  # Column 0: Wilayah Rohani (from dropdown)
                self.format_display(row_data.get('nama_keluarga')),  # Column 1: Nama Keluarga
                self.format_numeric(row_data.get('no_kk')),  # Column 2: No. KK (numeric only)
                self.format_display(row_data.get('nama_lengkap')),  # Column 3: Nama Lengkap
                self.format_numeric(row_data.get('nik')),  # Column 4: NIK (numeric only)
                self.format_display(row_data.get('tempat_lahir')),
                self.format_date(row_data.get('tanggal_lahir')),
                self.format_display(row_data.get('umur')),
                self.format_display(row_data.get('status_kekatolikan')),
                self.format_display(row_data.get('kategori')),
                self.format_gender(row_data.get('jenis_kelamin')),
                self.format_display(row_data.get('hubungan_keluarga')),
                self.format_display(row_data.get('pendidikan_terakhir')),
                self.format_display(row_data.get('status_pernikahan')),  # Fixed: use database column name
                self.format_display(row_data.get('jenis_pekerjaan')),
                self.format_display(row_data.get('detail_pekerjaan')),
                self.format_display(row_data.get('alamat')),
                self.format_display(row_data.get('email')),
                # SAKRAMEN BABTIS (columns 18-21)
                self.format_display(row_data.get('status_babtis')),
                self.format_display(row_data.get('tempat_babtis')),
                self.format_date(row_data.get('tanggal_babtis')),
                self.format_display(row_data.get('nama_babtis')),
                # SAKRAMEN EKARISTI (columns 22-24)
                self.format_display(row_data.get('status_ekaristi')),
                self.format_display(row_data.get('tempat_komuni')),
                self.format_date(row_data.get('tanggal_komuni')),
                # SAKRAMEN KRISMA (columns 25-27)
                self.format_display(row_data.get('status_krisma')),
                self.format_display(row_data.get('tempat_krisma')),
                self.format_date(row_data.get('tanggal_krisma')),
                # SAKRAMEN PERKAWINAN (columns 28-33)
                self.format_display(row_data.get('status_perkawinan')),
                self.format_display(row_data.get('keuskupan')),
                self.format_display(row_data.get('paroki')),
                self.format_display(row_data.get('kota_perkawinan')),
                self.format_date(row_data.get('tanggal_perkawinan')),
                self.format_display(row_data.get('status_perkawinan_detail')),
                # STATUS (columns 34-37) - TOTAL 38 COLUMNS
                self.format_display(row_data.get('status_keanggotaan', 'Aktif')),
                self.format_display(row_data.get('wr_tujuan')),
                self.format_display(row_data.get('paroki_tujuan')),
                self.get_creator_display(row_data)
            ]

            # Add data to columns 0-37 (total 38 columns tanpa kolom No)
            for col, item_text in enumerate(data_items):
                item = QTableWidgetItem(item_text)
                # Center align certain columns for better readability
                if col in [7, 8, 9, 10, 18, 19, 22, 23, 25, 26, 28, 34]:  # Status and categorical columns
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.jemaat_table.setItem(row_pos, col, item)
    
    def format_numeric(self, value, default='-'):
        """Format numeric value (NIK, NO_KK) untuk display, hanya menampilkan angka saja"""
        if value is None:
            return default

        if isinstance(value, str):
            text = value.strip()
            if not text or text.lower() in ('none', 'null', 'nan', ''):
                return default
            # Ambil hanya karakter numerik
            numeric_text = ''.join(c for c in text if c.isdigit())
            return numeric_text if numeric_text else default

        if isinstance(value, (int, float)):
            return str(int(value))

        text = str(value).strip()
        if not text or text.lower() in ('none', 'null', 'nan'):
            return default
        # Ambil hanya karakter numerik
        numeric_text = ''.join(c for c in text if c.isdigit())
        return numeric_text if numeric_text else default

    def format_display(self, value, default='-'):
        """Format generic value for display, replacing kosong/None with '-'."""
        if value is None:
            return default

        if isinstance(value, str):
            text = value.strip()
            if not text or text.lower() in ('none', 'null', 'nan'):
                return default
            return text

        text = str(value).strip()
        if not text or text.lower() in ('none', 'null', 'nan'):
            return default
        return text

    def format_date(self, date_value):
        """Format date for display in spreadsheet"""
        if not date_value:
            return '-'
        if hasattr(date_value, 'strftime'):
            return date_value.strftime('%d/%m/%Y')
        if isinstance(date_value, str):
            text = date_value.strip()
            if not text or text.lower() in ('none', 'null', 'nan'):
                return '-'
            return text
        return self.format_display(date_value)
    
    def format_gender(self, gender):
        """Format gender for display"""
        if gender == 'Laki-laki':
            return 'L'
        elif gender == 'Perempuan':
            return 'P'
        return self.format_display(gender)

    def get_creator_display(self, row_data):
        """Resolve nama pembuat data jemaat untuk tampilan tabel."""
        if not row_data:
            return 'System'

        possible_keys = [
            'created_by_name',
            'created_by_pengguna_name',
            'created_by_pengguna_fullname',
            'created_by_username',
            'created_by',
            'dibuat_oleh',
            'dibuat_oleh_nama',
            'nama_pembuat',
            'nama_user',
            'creator_name'
        ]

        for key in possible_keys:
            value = row_data.get(key)
            display_value = self.format_display(value, default='')
            if display_value:
                return display_value

        creator_info = row_data.get('created_by_pengguna')
        if isinstance(creator_info, dict):
            for sub_key in ['nama_lengkap', 'full_name', 'name', 'username']:
                value = creator_info.get(sub_key)
                display_value = self.format_display(value, default='')
                if display_value:
                    return display_value
            return '-'

        if creator_info in (None, '', 'None'):
            return '-'

        if isinstance(creator_info, str) and not creator_info.isdigit():
            return self.format_display(creator_info)

        name = self.lookup_pengguna_name(creator_info)
        if name:
            return self.format_display(name)

        if creator_info not in (None, '', 'None'):
            try:
                numeric_id = int(creator_info)
                return f"User #{numeric_id}"
            except (TypeError, ValueError):
                return self.format_display(creator_info)

        return '-'

    def lookup_pengguna_name(self, pengguna_id):
        """Cari nama lengkap pengguna berdasarkan ID menggunakan cache lokal."""
        if pengguna_id in (None, '', 'None'):
            return ''

        try:
            pengguna_key = int(pengguna_id)
        except (TypeError, ValueError):
            return str(pengguna_id) if pengguna_id is not None else ''

        if pengguna_key in self._pengguna_lookup:
            return self._pengguna_lookup[pengguna_key]

        self.load_pengguna_lookup()
        return self._pengguna_lookup.get(pengguna_key, '')

    def load_pengguna_lookup(self):
        """Load data pengguna sekali untuk mapping ID -> nama pembuat."""
        if self._pengguna_lookup_attempted:
            return

        self._pengguna_lookup_attempted = True
        try:
            from API.config import ServerConfig
            import requests

            response = requests.get(
                f"{ServerConfig.API_BASE_URL}/pengguna",
                timeout=10
            )

            if response.status_code != 200:
                self._safe_log(f"Gagal memuat daftar pengguna: HTTP {response.status_code}")
                return

            payload = response.json() if response.text else {}
            users = payload.get('data', []) if isinstance(payload, dict) else []

            for user in users:
                try:
                    user_id = user.get('id_pengguna')
                    if user_id is None:
                        continue
                    name = user.get('nama_lengkap') or user.get('username')
                    if name:
                        self._pengguna_lookup[int(user_id)] = str(name)
                except Exception:
                    continue
        except Exception as exc:
            self._safe_log(f"Error memuat data pengguna: {exc}")

    def _safe_log(self, message):
        """Kirim log message jika signal tersedia, abaikan jika gagal."""
        try:
            self.log_message.emit(message)
        except Exception:
            pass
    
    
    def add_jemaat(self):
        """Tambah jemaat baru"""
        dialog = JemaatDialog(self)

        # Keep dialog open until valid data is entered
        while True:
            result = dialog.exec_()

            if result != dialog.Accepted:
                # User clicked Cancel - exit without saving
                return

            data = dialog.get_data()

            # ===== VALIDATION CHECKS =====
            # Check Nama Lengkap
            if not data['nama_lengkap'] or data['nama_lengkap'].strip() == '':
                QMessageBox.warning(dialog, "Data Tidak Lengkap",
                    "❌ Nama lengkap harus diisi!\n\nSilakan isikan nama lengkap dan coba lagi.")
                # Dialog stays open - user can correct and re-submit
                continue

            # Check Jenis Kelamin
            if not data['jenis_kelamin'] or data['jenis_kelamin'] == '':
                QMessageBox.warning(dialog, "Data Tidak Lengkap",
                    "❌ Jenis kelamin harus dipilih!\n\nSilakan pilih jenis kelamin dan coba lagi.")
                # Dialog stays open - user can correct and re-submit
                continue

            # Check Database Manager
            if not self.db_manager:
                QMessageBox.critical(dialog, "Error",
                    "❌ Database tidak tersedia!\n\nTidak dapat menambahkan data jemaat.")
                # Dialog stays open - system error, might be resolvable
                continue

            if not self.current_admin:
                QMessageBox.critical(dialog, "Error", "Data admin tidak ditemukan. Silakan login ulang.")
                return

            # All validations passed - break loop and proceed to submit
            break

        # ===== SUBMIT DATA =====
        try:
            # Prepare data for API - INCLUDE user_id (required by API)
            # Helper function to extract only numeric characters
            def get_numeric_only(value):
                if not value:
                    return ''
                numeric_text = ''.join(c for c in str(value) if c.isdigit())
                return numeric_text

            admin_id = self.current_admin.get('id_admin')
            if not admin_id:
                QMessageBox.critical(self, "Error", "ID Admin tidak valid. Tidak bisa menambahkan data.")
                return

            jenis_kelamin_short = data.get('jenis_kelamin')
            if jenis_kelamin_short == 'L':
                jenis_kelamin_full = 'Laki-laki'
            elif jenis_kelamin_short == 'P':
                jenis_kelamin_full = 'Perempuan'
            else:
                jenis_kelamin_full = ''

            filtered_data = {
                'user_id': admin_id,
                'wilayah_rohani': data.get('wilayah_rohani', ''),
                'nama_keluarga': data.get('nama_keluarga', ''),
                'no_kk': get_numeric_only(data.get('no_kk', '')),  # Only numeric characters
                'nama_lengkap': data.get('nama_lengkap', ''),
                'nik': get_numeric_only(data.get('nik', '')),  # Only numeric characters
                'tempat_lahir': data.get('tempat_lahir', ''),
                'tanggal_lahir': data.get('tanggal_lahir', ''),
                'umur': data.get('umur', ''),  # Include umur field
                'status_kekatolikan': data.get('status_kekatolikan', ''),
                'kategori': data.get('kategori', ''),
                'jenis_kelamin': jenis_kelamin_full,
                'hubungan_keluarga': data.get('hubungan_keluarga', ''),
                'pendidikan_terakhir': data.get('pendidikan_terakhir', ''),
                'status_menikah': data.get('status_menikah', ''),  # API maps to status_pernikahan
                'jenis_pekerjaan': data.get('jenis_pekerjaan', ''),
                'detail_pekerjaan': data.get('detail_pekerjaan', ''),
                'alamat': data.get('alamat', ''),
                'email': data.get('email', ''),
                'status_babtis': data.get('status_babtis', ''),
                'tempat_babtis': data.get('tempat_babtis', ''),
                'tanggal_babtis': data.get('tanggal_babtis', ''),
                'nama_babtis': data.get('nama_babtis', ''),
                'status_ekaristi': data.get('status_ekaristi', ''),
                'tempat_komuni': data.get('tempat_komuni', ''),
                'tanggal_komuni': data.get('tanggal_komuni', ''),
                'status_krisma': data.get('status_krisma', ''),
                'tempat_krisma': data.get('tempat_krisma', ''),
                'tanggal_krisma': data.get('tanggal_krisma', ''),
                'status_perkawinan': data.get('status_perkawinan', ''),
                'keuskupan': data.get('keuskupan', ''),
                'paroki': data.get('paroki', ''),
                'kota_perkawinan': data.get('kota_perkawinan', ''),
                'tanggal_perkawinan': data.get('tanggal_perkawinan', ''),
                'status_perkawinan_detail': data.get('status_perkawinan_detail', ''),
                'status_keanggotaan': data.get('status_keanggotaan', ''),
                'wr_tujuan': data.get('wilayah_rohani_pindah', ''),
                'paroki_tujuan': data.get('paroki_pindah', '')
            }

            success, result = self.db_manager.add_jemaat(filtered_data)

            if success:
                # Success - close dialog and show confirmation
                dialog.close()
                QMessageBox.information(self, "Sukses",
                    "✅ Data jemaat berhasil ditambahkan!\n\n" +
                    f"Nama: {data['nama_lengkap']}\n" +
                    f"Jenis Kelamin: {'Laki-laki' if data.get('jenis_kelamin') == 'L' else 'Perempuan'}\n" +
                    f"Data lengkap termasuk sakramen dan wilayah rohani telah disimpan.")
                self.load_data()
                self.log_message.emit(f"Jemaat baru ditambahkan: {data['nama_lengkap']}")
            else:
                # API Error - keep dialog open for user to fix
                error_msg = str(result)

                # Extract error details from response
                if isinstance(result, dict):
                    error_detail = result.get('data', error_msg)
                else:
                    error_detail = error_msg

                # Provide user-friendly error message based on error type
                if "Unknown column" in error_detail or "does not exist" in error_detail:
                    QMessageBox.critical(dialog, "Database Error",
                        "❌ Gagal menambahkan jemaat - Database schema error!\n\n" +
                        f"Detail: {error_detail}\n\n" +
                        "Hubungi administrator untuk menjalankan database migration.")
                elif "Duplicate" in error_detail:
                    QMessageBox.warning(dialog, "Data Duplikat",
                        "❌ Data jemaat dengan informasi ini sudah ada di database!\n\n" +
                        "Silakan periksa data dan coba lagi dengan data yang berbeda.")
                elif "400" in str(error_msg) or "user_id" in error_detail:
                    QMessageBox.warning(dialog, "Validation Error",
                        "❌ Gagal menambahkan jemaat - Data tidak lengkap!\n\n" +
                        f"Error: {error_detail}\n\n" +
                        "Silakan periksa semua field yang wajib diisi.")
                elif "500" in str(error_msg):
                    QMessageBox.critical(dialog, "Server Error",
                        "❌ Gagal menambahkan jemaat - Server error!\n\n" +
                        f"Error: {error_detail}\n\n" +
                        "Silakan coba lagi. Jika error berlanjut, hubungi administrator.")
                else:
                    QMessageBox.warning(dialog, "Error",
                        f"❌ Gagal menambahkan jemaat:\n\n{error_detail}\n\n" +
                        "Silakan coba lagi atau hubungi administrator.")

                self.log_message.emit(f"Error adding jemaat: {result}")
                # Dialog stays open - user can retry
                return

        except Exception as e:
            error_str = str(e)
            dialog.close()
            QMessageBox.critical(self, "Exception Error",
                f"❌ Terjadi kesalahan saat menambahkan jemaat:\n\n{error_str}\n\n" +
                "Silakan hubungi administrator jika error berlanjut.")
            self.log_message.emit(f"Exception adding jemaat: {error_str}")
    
    def get_selected_row(self):
        """Get currently selected row index"""
        current_row = self.jemaat_table.currentRow()
        # No adjustment needed with normal headers
        if current_row >= 0:
            return current_row
        return -1  # Invalid selection
    
    def edit_jemaat(self):
        """Edit jemaat terpilih"""
        current_row = self.get_selected_row()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih jemaat yang akan diedit")
            return
        
        if current_row >= len(self.jemaat_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return
        
        jemaat_data = self.jemaat_data[current_row]
        
        dialog = JemaatDialog(self, jemaat_data)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            
            # Validasi
            if not data['nama_lengkap']:
                QMessageBox.warning(self, "Error", "Nama lengkap harus diisi")
                return
            
            if not data['jenis_kelamin']:
                QMessageBox.warning(self, "Error", "Jenis kelamin harus dipilih")
                return
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            if not self.current_admin:
                QMessageBox.critical(self, "Error", "Data admin tidak ditemukan. Silakan login ulang.")
                return
            
            try:
                # Helper function to extract only numeric characters
                def get_numeric_only(value):
                    if not value:
                        return ''
                    numeric_text = ''.join(c for c in str(value) if c.isdigit())
                    return numeric_text

                admin_id = self.current_admin.get('id_admin')
                if not admin_id:
                    QMessageBox.critical(self, "Error", "ID Admin tidak valid. Tidak bisa mengupdate data.")
                    return

                jenis_kelamin_short = data.get('jenis_kelamin')
                if jenis_kelamin_short == 'L':
                    jenis_kelamin_full = 'Laki-laki'
                elif jenis_kelamin_short == 'P':
                    jenis_kelamin_full = 'Perempuan'
                else:
                    jenis_kelamin_full = ''

                # Send all data including no_kk and nik to API
                filtered_data = {
                    'user_id': admin_id,
                    'wilayah_rohani': data.get('wilayah_rohani', ''),
                    'nama_keluarga': data.get('nama_keluarga', ''),
                    'no_kk': get_numeric_only(data.get('no_kk', '')),  # Only numeric characters
                    'nama_lengkap': data.get('nama_lengkap', ''),
                    'nik': get_numeric_only(data.get('nik', '')),  # Only numeric characters
                    'tempat_lahir': data.get('tempat_lahir', ''),
                    'tanggal_lahir': data.get('tanggal_lahir', ''),
                    'umur': data.get('umur', ''),  # Include umur field
                    'status_kekatolikan': data.get('status_kekatolikan', ''),
                    'kategori': data.get('kategori', ''),
                    'jenis_kelamin': jenis_kelamin_full,
                    'hubungan_keluarga': data.get('hubungan_keluarga', ''),
                    'pendidikan_terakhir': data.get('pendidikan_terakhir', ''),
                    'status_menikah': data.get('status_menikah', ''),  # API maps to status_pernikahan
                    'jenis_pekerjaan': data.get('jenis_pekerjaan', ''),
                    'detail_pekerjaan': data.get('detail_pekerjaan', ''),
                    'alamat': data.get('alamat', ''),
                    'email': data.get('email', ''),
                    'status_babtis': data.get('status_babtis', ''),
                    'tempat_babtis': data.get('tempat_babtis', ''),
                    'tanggal_babtis': data.get('tanggal_babtis', ''),
                    'nama_babtis': data.get('nama_babtis', ''),
                    'status_ekaristi': data.get('status_ekaristi', ''),
                    'tempat_komuni': data.get('tempat_komuni', ''),
                    'tanggal_komuni': data.get('tanggal_komuni', ''),
                    'status_krisma': data.get('status_krisma', ''),
                    'tempat_krisma': data.get('tempat_krisma', ''),
                    'tanggal_krisma': data.get('tanggal_krisma', ''),
                    'status_perkawinan': data.get('status_perkawinan', ''),
                    'keuskupan': data.get('keuskupan', ''),
                    'paroki': data.get('paroki', ''),
                    'kota_perkawinan': data.get('kota_perkawinan', ''),
                    'tanggal_perkawinan': data.get('tanggal_perkawinan', ''),
                    'status_perkawinan_detail': data.get('status_perkawinan_detail', ''),
                    'status_keanggotaan': data.get('status_keanggotaan', ''),
                    'wr_tujuan': data.get('wilayah_rohani_pindah', ''),
                    'paroki_tujuan': data.get('paroki_pindah', '')
                }

                id_jemaat = jemaat_data['id_jemaat']
                success, result = self.db_manager.update_jemaat(id_jemaat, filtered_data)
                
                if success:
                    QMessageBox.information(self, "Sukses", "Data jemaat berhasil diupdate")
                    self.load_data()
                    self.log_message.emit(f"Jemaat diupdate: {data['nama_lengkap']}")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal mengupdate jemaat: {result}")
                    self.log_message.emit(f"Error updating jemaat: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error mengupdate jemaat: {str(e)}")
                self.log_message.emit(f"Exception updating jemaat: {str(e)}")
    
    def delete_jemaat(self):
        """Hapus jemaat terpilih"""
        current_row = self.get_selected_row()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih jemaat yang akan dihapus")
            return
        
        if current_row >= len(self.jemaat_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return
        
        jemaat_data = self.jemaat_data[current_row]
        nama = jemaat_data.get('nama_lengkap', 'Unknown')
        
        reply = QMessageBox.question(self, 'Konfirmasi',
                                    f"Yakin ingin menghapus jemaat '{nama}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            try:
                id_jemaat = jemaat_data.get('id_jemaat')
                if not id_jemaat:
                    QMessageBox.warning(self, "Error", "ID jemaat tidak ditemukan")
                    return
                
                success, result = self.db_manager.delete_jemaat(id_jemaat)
                
                if success:
                    QMessageBox.information(self, "Sukses", "Data jemaat berhasil dihapus")
                    self.load_data()
                    self.log_message.emit(f"Jemaat dihapus: {nama}")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal menghapus jemaat: {result}")
                    self.log_message.emit(f"Error deleting jemaat: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error menghapus jemaat: {str(e)}")
                self.log_message.emit(f"Exception deleting jemaat: {str(e)}")
    
    def filter_data(self):
        """Filter data jemaat berdasarkan keyword pencarian dan dropdown filters"""
        search_text = self.search_input.text().lower().strip()

        # Get selected filter values from comboboxes
        filter_wilayah = self.filter_wilayah.currentText() if hasattr(self, 'filter_wilayah') else "Semua"
        filter_kategori = self.filter_kategori.currentText() if hasattr(self, 'filter_kategori') else "Semua"

        # Simpan data asli jika belum disimpan
        if not hasattr(self, 'all_jemaat_data') or not self.all_jemaat_data:
            self.all_jemaat_data = self.jemaat_data.copy() if self.jemaat_data else []

        # Mulai dengan semua data
        filtered_data = self.all_jemaat_data.copy()

        # Filter berdasarkan Wilayah Rohani jika dipilih
        if filter_wilayah != "Semua":
            filtered_data = [data for data in filtered_data
                           if (data.get('wilayah_rohani') or '').strip() == filter_wilayah]

        # Filter berdasarkan Kategori jika dipilih
        if filter_kategori != "Semua":
            filtered_data = [data for data in filtered_data
                           if (data.get('kategori') or '').strip() == filter_kategori]

        # Filter berdasarkan keyword pencarian jika ada
        if search_text:
            search_filtered = []
            for data in filtered_data:
                # Cari di berbagai field - handle None values
                nama_lengkap = (data.get('nama_lengkap') or '').lower()
                wilayah_rohani = (data.get('wilayah_rohani') or '').lower()
                nama_keluarga = (data.get('nama_keluarga') or '').lower()
                tempat_lahir = (data.get('tempat_lahir') or '').lower()
                kategori = (data.get('kategori') or '').lower()
                jenis_kelamin = (data.get('jenis_kelamin') or '').lower()
                hubungan_keluarga = (data.get('hubungan_keluarga') or '').lower()
                alamat = (data.get('alamat') or '').lower()
                email = (data.get('email') or '').lower()
                status_keanggotaan = (data.get('status_keanggotaan') or '').lower()

                # Search di semua field yang relevan
                if (search_text in nama_lengkap or
                    search_text in wilayah_rohani or
                    search_text in nama_keluarga or
                    search_text in tempat_lahir or
                    search_text in kategori or
                    search_text in jenis_kelamin or
                    search_text in hubungan_keluarga or
                    search_text in alamat or
                    search_text in email or
                    search_text in status_keanggotaan):
                    search_filtered.append(data)

            filtered_data = search_filtered

        # Update display dengan data yang difilter
        self.jemaat_data = filtered_data
        self.populate_table()

    
    def export_jemaat(self):
        """Export data jemaat ke file CSV"""
        if not self.jemaat_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor")
            return
        
        try:
            import csv
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Data Jemaat", "data_jemaat.csv", "CSV Files (*.csv)"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = [
                        'Nama Lengkap', 'Wilayah Rohani', 'Nama Keluarga', 'Tempat Lahir',
                        'Tanggal Lahir', 'Umur', 'Status Kekatolikan', 'Jenis Kelamin', 'Hubungan Keluarga', 'Pendidikan Terakhir',
                        'Jenis Pekerjaan', 'Detail Pekerjaan', 'Status Menikah', 'Alamat', 'Email',
                        'Status Babtis', 'Tempat Babtis', 'Tanggal Babtis', 'Nama Babtis',
                        'Status Ekaristi', 'Tempat Komuni', 'Tanggal Komuni',
                        'Status Krisma', 'Tempat Krisma', 'Tanggal Krisma',
                        'Status Perkawinan', 'Keuskupan', 'Paroki', 'Kota Perkawinan',
                        'Tanggal Perkawinan', 'Status Perkawinan Detail', 'Status Keanggotaan',
                        'Created By Pengguna'
                    ]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for data in self.jemaat_data:
                        writer.writerow({
                            'Nama Lengkap': self.format_display(data.get('nama_lengkap')),
                            'Wilayah Rohani': self.format_display(data.get('wilayah_rohani')),
                            'Nama Keluarga': self.format_display(data.get('nama_keluarga')),
                            'Tempat Lahir': self.format_display(data.get('tempat_lahir')),
                            'Tanggal Lahir': self.format_date(data.get('tanggal_lahir')),
                            'Umur': self.format_display(data.get('umur')),
                            'Status Kekatolikan': self.format_display(data.get('status_kekatolikan')),
                            'Jenis Kelamin': self.format_gender(data.get('jenis_kelamin')),
                            'Hubungan Keluarga': self.format_display(data.get('hubungan_keluarga')),
                            'Pendidikan Terakhir': self.format_display(data.get('pendidikan_terakhir')),
                            'Jenis Pekerjaan': self.format_display(data.get('jenis_pekerjaan')),
                            'Detail Pekerjaan': self.format_display(data.get('detail_pekerjaan')),
                            'Status Menikah': self.format_display(data.get('status_pernikahan')),  # Fixed: use database column name
                            'Alamat': self.format_display(data.get('alamat')),
                            'Email': self.format_display(data.get('email')),
                            'Status Babtis': self.format_display(data.get('status_babtis')),
                            'Tempat Babtis': self.format_display(data.get('tempat_babtis')),
                            'Tanggal Babtis': self.format_date(data.get('tanggal_babtis')),
                            'Nama Babtis': self.format_display(data.get('nama_babtis')),
                            'Status Ekaristi': self.format_display(data.get('status_ekaristi')),
                            'Tempat Komuni': self.format_display(data.get('tempat_komuni')),
                            'Tanggal Komuni': self.format_date(data.get('tanggal_komuni')),
                            'Status Krisma': self.format_display(data.get('status_krisma')),
                            'Tempat Krisma': self.format_display(data.get('tempat_krisma')),
                            'Tanggal Krisma': self.format_date(data.get('tanggal_krisma')),
                            'Status Perkawinan': self.format_display(data.get('status_perkawinan')),
                            'Keuskupan': self.format_display(data.get('keuskupan')),
                            'Paroki': self.format_display(data.get('paroki')),
                            'Kota Perkawinan': self.format_display(data.get('kota_perkawinan')),
                            'Tanggal Perkawinan': self.format_date(data.get('tanggal_perkawinan')),
                            'Status Perkawinan Detail': self.format_display(data.get('status_perkawinan_detail')),
                            'Status Keanggotaan': self.format_display(data.get('status_keanggotaan')),
                            'Created By Pengguna': self.get_creator_display(data)
                        })
                
                QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
                self.log_message.emit(f"Data jemaat diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error export data: {str(e)}")
            self.log_message.emit(f"Exception exporting jemaat: {str(e)}")
    
    def broadcast_jemaat(self):
        """Broadcast data jemaat ke client"""
        if not self.jemaat_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk dibroadcast")
            return
        
        reply = QMessageBox.question(self, 'Konfirmasi Broadcast',
                                   f"Yakin ingin broadcast {len(self.jemaat_data)} data jemaat ke semua client?",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                import requests
                from API.config import ServerConfig
                
                data = {
                    'admin_id': 1,
                    'selected_ids': [jemaat.get('id_jemaat') for jemaat in self.jemaat_data if jemaat.get('id_jemaat')]
                }
                
                response = requests.post(f"{ServerConfig.API_BASE_URL}/broadcast/jemaat", 
                                       json=data, 
                                       headers={'Content-Type': 'application/json'},
                                       timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        total_data = result.get('total', 0)
                        QMessageBox.information(self, "Sukses", f"Data jemaat berhasil dibroadcast ke client!\nTotal data: {total_data}")
                        self.log_message.emit(f"Broadcast jemaat sukses: {total_data} data")
                    else:
                        QMessageBox.warning(self, "Error", f"Gagal broadcast: {result.get('message', 'Unknown error')}")
                        self.log_message.emit(f"Broadcast jemaat gagal: {result.get('message')}")
                else:
                    QMessageBox.warning(self, "Error", f"Server error: {response.status_code}")
                    self.log_message.emit(f"Broadcast jemaat error: HTTP {response.status_code}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error broadcast jemaat: {str(e)}")
                self.log_message.emit(f"Exception broadcasting jemaat: {str(e)}")
    
    def view_jemaat_details(self):
        """View detailed information of selected jemaat"""
        current_row = self.get_selected_row()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih jemaat untuk melihat detail")
            return
        
        if current_row >= len(self.jemaat_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return
        
        jemaat_data = self.jemaat_data[current_row]
        nama = jemaat_data.get('nama_lengkap', 'Unknown')
        
        # Create detailed view dialog
        from PyQt5.QtWidgets import QDialog, QTextEdit, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detail Jemaat - {nama}")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Create text display for all data
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Format all data nicely
        def display(key):
            return self.format_display(jemaat_data.get(key))

        details = f"""
<h2>DETAIL JEMAAT</h2>
<h3>DATA DIRI</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Nama Lengkap:</b></td><td>{display('nama_lengkap')}</td></tr>
<tr><td><b>Wilayah Rohani:</b></td><td>{display('wilayah_rohani')}</td></tr>
<tr><td><b>Nama Keluarga:</b></td><td>{display('nama_keluarga')}</td></tr>
<tr><td><b>Tempat Lahir:</b></td><td>{display('tempat_lahir')}</td></tr>
<tr><td><b>Tanggal Lahir:</b></td><td>{self.format_date(jemaat_data.get('tanggal_lahir'))}</td></tr>
<tr><td><b>Umur:</b></td><td>{display('umur')}</td></tr>
<tr><td><b>Kategori:</b></td><td>{display('kategori')}</td></tr>
<tr><td><b>Jenis Kelamin:</b></td><td>{self.format_gender(jemaat_data.get('jenis_kelamin'))}</td></tr>
<tr><td><b>Hubungan Keluarga:</b></td><td>{display('hubungan_keluarga')}</td></tr>
<tr><td><b>Pendidikan Terakhir:</b></td><td>{display('pendidikan_terakhir')}</td></tr>
<tr><td><b>Status Menikah:</b></td><td>{display('status_pernikahan')}</td></tr>
<tr><td><b>Status Pekerjaan:</b></td><td>{display('jenis_pekerjaan')}</td></tr>
<tr><td><b>Detail Pekerjaan:</b></td><td>{display('detail_pekerjaan')}</td></tr>
</table>

<h3>SAKRAMEN</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Status Babtis:</b></td><td>{display('status_babtis')}</td></tr>
<tr><td><b>Tempat Babtis:</b></td><td>{display('tempat_babtis')}</td></tr>
<tr><td><b>Tanggal Babtis:</b></td><td>{self.format_date(jemaat_data.get('tanggal_babtis'))}</td></tr>
<tr><td><b>Status Ekaristi:</b></td><td>{display('status_ekaristi')}</td></tr>
<tr><td><b>Tempat Komuni:</b></td><td>{display('tempat_komuni')}</td></tr>
<tr><td><b>Tanggal Komuni:</b></td><td>{self.format_date(jemaat_data.get('tanggal_komuni'))}</td></tr>
<tr><td><b>Status Krisma:</b></td><td>{display('status_krisma')}</td></tr>
<tr><td><b>Tempat Krisma:</b></td><td>{display('tempat_krisma')}</td></tr>
<tr><td><b>Tanggal Krisma:</b></td><td>{self.format_date(jemaat_data.get('tanggal_krisma'))}</td></tr>
</table>

<h3>KONTAK & ALAMAT</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Email:</b></td><td>{display('email')}</td></tr>
<tr><td><b>Alamat:</b></td><td>{display('alamat')}</td></tr>
</table>

<h3>STATUS</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Status Keanggotaan:</b></td><td>{display('status_keanggotaan')}</td></tr>
<tr><td><b>Created By:</b></td><td>{self.get_creator_display(jemaat_data)}</td></tr>
</table>
        """
        
        text_edit.setHtml(details)
        layout.addWidget(text_edit)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.clicked.connect(dialog.close)  # type: ignore
        layout.addWidget(button_box)
        
        dialog.exec_()
    
    def get_data(self):
        """Ambil data jemaat untuk komponen lain"""
        return self.jemaat_data
