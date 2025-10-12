# Path: server/components/jemaat.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFileDialog, QAbstractItemView, QFrame,
                            QScrollArea, QSplitter)
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

# Import dialog secara langsung untuk menghindari circular import
from .dialogs import JemaatDialog

class JemaatComponent(QWidget):
    """Komponen untuk manajemen data jemaat"""
    
    data_updated = pyqtSignal()  # Signal ketika data berubah
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore  # Signal untuk mengirim log message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.jemaat_data = []
        self.db_manager = None
        self.setup_ui()
    
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
        
        header_layout.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari jemaat...")
        self.search_input.setFixedWidth(250)
        self.search_input.returnPressed.connect(self.search_jemaat)
        header_layout.addWidget(self.search_input)
        
        search_button = self.create_button("Cari", "#3498db", self.search_jemaat)
        header_layout.addWidget(search_button)
        
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
            search = self.search_input.text().strip() if hasattr(self, 'search_input') else None
            success, result = self.db_manager.get_jemaat_list(limit=1000, search=search)
            
            if success:
                self.jemaat_data = result
                self.populate_table()
                self.log_message.emit(f"Data jemaat berhasil dimuat: {len(result)} record")
                self.data_updated.emit()
            else:
                self.log_message.emit(f"Error loading jemaat data: {result}")
                QMessageBox.warning(self, "Error", f"Gagal memuat data jemaat: {result}")
        except Exception as e:
            self.log_message.emit(f"Exception loading jemaat data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error loading jemaat data: {str(e)}")
    
    def create_spreadsheet_grid(self, layout):
        """Create table with proper header format using table rows"""
        # Create table with 35 columns, start with 2 header rows + 0 data rows
        self.jemaat_table = QTableWidget(2, 35)

        # Hide horizontal header since we will use table cells as headers
        self.jemaat_table.horizontalHeader().setVisible(False)
        self.jemaat_table.verticalHeader().setVisible(True)  # Show row numbers like Excel

        # Set up two-level headers using table cells with colspan - IMPROVED STYLING
        self.setup_two_level_headers_with_improved_styling()

        # Configure table styling
        self.apply_professional_table_style(self.jemaat_table)

        # CRITICAL: Re-apply header styling SETELAH stylesheet diterapkan
        # Karena stylesheet akan override background colors
        self.reapply_header_styling()

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

    def setup_two_level_headers_with_improved_styling(self):
        """Setup table dengan 2-level headers dan styling seperti vertical header"""

        # ROW 0: Main category headers
        main_categories = [
            (0, "no", 1),
            (1, "DATA PRIBADI", 15),
            (16, "SAKRAMEN BABTIS", 4),
            (20, "SAKRAMEN EKARISTI", 3),
            (23, "SAKRAMEN KRISMA", 3),
            (26, "SAKRAMEN PERKAWINAN", 6),
            (32, "STATUS", 3)
        ]

        # ROW 1: Sub-headers
        column_headers = [
            "",  # Column 0 - empty under "no"
            "Wilayah Rohani", "Nama Keluarga", "Nama Lengkap", "Tempat Lahir",
            "Tanggal Lahir", "Umur", "Kategori", "J. Kelamin",
            "Hubungan Keluarga", "Pend. Terakhir", "Status Menikah", "Status Pekerjaan",
            "Detail Pekerjaan", "Alamat", "Email/No.Hp",
            "Status", "Tempat Babtis", "Tanggal Babtis", "Nama Babtis",
            "Status", "Tempat Komuni", "Tanggal Komuni",
            "Status", "Tempat Krisma", "Tanggal Krisma",
            "Status", "Keuskupan", "Paroki", "Kota", "Tanggal Perkawinan", "Status Perkawinan",
            "Status Keanggotaan", "WR Tujuan", "Paroki Tujuan"
        ]

        # Style yang sama dengan vertical header (row number di kiri)
        header_style_bg = QColor("#747171")
        header_style_fg = QColor("#333333")

        # Create ROW 0: Main headers - SAMA dengan inventaris header style
        for col_start, category_name, span in main_categories:
            item = QTableWidgetItem(category_name)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            # Styling SAMA dengan inventaris header: #f2f2f2
            item.setBackground(QColor("#f2f2f2"))
            item.setForeground(QColor("#333333"))

            font = QFont()
            font.setBold(False)  # Normal weight seperti inventaris
            font.setPointSize(9)
            item.setFont(font)

            item.setFlags(Qt.ItemIsEnabled)
            self.jemaat_table.setItem(0, col_start, item)

            if span > 1:
                self.jemaat_table.setSpan(0, col_start, 1, span)

        # Create ROW 1: Sub-headers - LEBIH TERANG dari main header
        for col, column_header in enumerate(column_headers):
            item = QTableWidgetItem(column_header)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            # Sub-header styling: lebih terang (#fafafa)
            item.setBackground(QColor("#fafafa"))
            item.setForeground(QColor("#555555"))

            font = QFont()
            font.setBold(False)
            font.setPointSize(9)
            item.setFont(font)

            item.setFlags(Qt.ItemIsEnabled)
            self.jemaat_table.setItem(1, col, item)

        # Set row heights - lebih tinggi untuk visibility
        self.jemaat_table.setRowHeight(0, 30)  # Main header - lebih tinggi
        self.jemaat_table.setRowHeight(1, 28)  # Sub-header

        # KEMBALIKAN nomor 1, 2, 3, 4 dst di vertical header
        # TIDAK override vertical header items, biarkan default (1, 2, 3, dst)

        # Set column widths
        self.setup_column_widths()

        # PENTING: Simpan reference untuk re-apply styling nanti
        self._header_cells_styling_data = []

        # Force semua header cells non-editable dengan styling khusus
        for row in range(2):
            for col in range(35):
                item = self.jemaat_table.item(row, col)
                if item:
                    # Non-editable
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    # Styling berbeda untuk main header vs sub-header
                    if row == 0:
                        # ROW 0: Main header - SAMA dengan inventaris header
                        bg_color = QColor("#f2f2f2")
                        fg_color = QColor("#333333")
                    else:
                        # ROW 1: Sub-header - LEBIH TERANG dari main header
                        bg_color = QColor("#fafafa")
                        fg_color = QColor("#555555")

                    item.setBackground(bg_color)
                    item.setForeground(fg_color)

                    font = QFont()
                    font.setBold(False)
                    font.setPointSize(9)
                    item.setFont(font)

                    # Simpan data untuk re-apply
                    self._header_cells_styling_data.append((row, col, bg_color, fg_color))

    def reapply_header_styling(self):
        """Re-apply header styling setelah stylesheet diterapkan"""
        if hasattr(self, '_header_cells_styling_data'):
            for row, col, bg_color, fg_color in self._header_cells_styling_data:
                item = self.jemaat_table.item(row, col)
                if item:
                    item.setBackground(bg_color)
                    item.setForeground(fg_color)
                    font = QFont()
                    font.setBold(False)
                    font.setPointSize(9)
                    item.setFont(font)

    def setup_table_headers(self):
        """Set up table headers like struktur.py with proper column names"""
        # Define all column headers in order
        column_headers = [
            "No",  # Column 0
            # DATA PRIBADI (columns 1-15)
            "Wilayah Rohani", "Nama Keluarga", "Nama Lengkap", "Tempat Lahir",
            "Tanggal Lahir", "Umur", "Kategori", "J. Kelamin",
            "Hubungan Keluarga", "Pend. Terakhir", "Status Menikah", "Status Pekerjaan",
            "Detail Pekerjaan", "Alamat", "Email/No.Hp",
            # SAKRAMEN BABTIS (columns 16-19)
            "Status Babtis", "Tempat Babtis", "Tanggal Babtis", "Nama Babtis",
            # SAKRAMEN EKARISTI (columns 20-22)
            "Status Ekaristi", "Tempat Komuni", "Tanggal Komuni",
            # SAKRAMEN KRISMA (columns 23-25)
            "Status Krisma", "Tempat Krisma", "Tanggal Krisma",
            # SAKRAMEN PERKAWINAN (columns 26-31)
            "Status Perkawinan", "Keuskupan", "Paroki", "Kota", "Tanggal Perkawinan", "Status Perkawinan",
            # STATUS (columns 32-34)
            "Status Keanggotaan", "WR Tujuan", "Paroki Tujuan"
        ]

        # Set column headers
        self.jemaat_table.setHorizontalHeaderLabels(column_headers)

        # Set initial column widths
        self.setup_column_widths()

    def apply_professional_table_style(self, table):
        """Apply Excel-style table styling exactly like struktur.py"""
        # Header styling - Excel-like headers (same as struktur.py)
        header_font = QFont()
        header_font.setBold(False)  # Remove bold from headers
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

        # Excel-style header styling (exact copy from struktur.py)
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #d4d4d4;
                border-right: 1px solid #d4d4d4;
                padding: 6px 4px;
                font-weight: normal;
                color: #333333;
                text-align: left;
            }
        """)

        # Excel-style table body styling dengan HEADER ROW STYLING
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

        # IMPORTANT: Force update header cells styling AFTER stylesheet
        # Stylesheet akan override background, jadi kita perlu re-apply
        table.viewport().update()

        # Excel-style table settings (exact copy from struktur.py)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # All columns resizable
        header.setStretchLastSection(True)  # Last column stretches to fill space
        header.setMinimumSectionSize(50)
        header.setDefaultSectionSize(80)

        # Enable scrolling (exact copy from struktur.py)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Excel-style row settings (exact copy from struktur.py)
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

        # Enable grid display with thin lines (exact copy from struktur.py)
        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)

        # Excel-style editing and selection (exact copy from struktur.py)
        table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Set compact size for Excel look (exact copy from struktur.py)
        table.setMinimumHeight(150)
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    # OLD METHOD - NO LONGER USED (replaced by setup_two_level_headers_with_improved_styling)
    # def setup_three_level_headers_with_colspan(self):
        """Setup table with proper two-level headers matching inventaris style"""

        # Hide horizontal header since we'll use table cells as headers, but keep vertical header like struktur.py
        self.jemaat_table.horizontalHeader().setVisible(False)
        self.jemaat_table.verticalHeader().setVisible(True)  # Show row numbers like Excel/struktur.py

        # ROW 0: Main category headers - "no" as single cell, then category headers with colspan
        # Structure matching image 2: "no" (col 0) | "DATA PRIBADI" (cols 1-15) | "SAKRAMEN BABTIS" | etc.
        main_categories = [
            (0, "no", 1),  # Column 0: single cell with lowercase "no"
            (1, "DATA PRIBADI", 15),  # Columns 1-15: spans 15 columns
            (16, "SAKRAMEN BABTIS", 4),  # Columns 16-19: spans 4 columns
            (20, "SAKRAMEN EKARISTI", 3),  # Columns 20-22: spans 3 columns
            (23, "SAKRAMEN KRISMA", 3),  # Columns 23-25: spans 3 columns
            (26, "SAKRAMEN PERKAWINAN", 6),  # Columns 26-31: spans 6 columns
            (32, "STATUS", 3)  # Columns 32-34: spans 3 columns
        ]

        # ROW 1: Individual column headers (sub-headers)
        # Column 0 is EMPTY (blank cell below "no"), then sub-headers start from column 1
        column_headers = [
            "",  # Column 0 - EMPTY/BLANK cell below "no"
            # DATA PRIBADI (15 columns: 1-15)
            "Wilayah Rohani", "Nama Keluarga", "Nama Lengkap", "Tempat Lahir",
            "Tanggal Lahir", "Umur", "Kategori", "J. Kelamin",
            "Hubungan Keluarga", "Pend. Terakhir", "Status Menikah", "Status Pekerjaan",
            "Detail Pekerjaan", "Alamat", "Email/No.Hp",
            # SAKRAMEN BABTIS (4 columns: 16-19)
            "Status", "Tempat Babtis", "Tanggal Babtis", "Nama Babtis",
            # SAKRAMEN EKARISTI (3 columns: 20-22)
            "Status", "Tempat Komuni", "Tanggal Komuni",
            # SAKRAMEN KRISMA (3 columns: 23-25)
            "Status", "Tempat Krisma", "Tanggal Krisma",
            # SAKRAMEN PERKAWINAN (6 columns: 26-31)
            "Status", "Keuskupan", "Paroki", "Kota", "Tanggal Perkawinan", "Status Perkawinan",
            # STATUS (3 columns: 32-34)
            "Status Keanggotaan", "WR Tujuan", "Paroki Tujuan"
        ]

        # Create ROW 0: Main category headers with colspan
        for col_start, category_name, span in main_categories:
            item = QTableWidgetItem(category_name)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            # Apply Excel-style header background
            item.setBackground(QColor("#f2f2f2"))
            item.setForeground(QColor("#333333"))

            # Font styling
            font = QFont()
            font.setBold(False)
            font.setPointSize(9)
            item.setFont(font)

            # Make header cells non-editable
            item.setFlags(Qt.ItemIsEnabled)

            self.jemaat_table.setItem(0, col_start, item)

            # Apply colspan for categories that span multiple columns
            if span > 1:
                self.jemaat_table.setSpan(0, col_start, 1, span)

        # Create ROW 1: Individual column headers (sub-headers)
        for col, column_header in enumerate(column_headers):
            item = QTableWidgetItem(column_header)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            item.setBackground(QColor("#f2f2f2"))
            item.setForeground(QColor("#333333"))

            # Font styling
            font = QFont()
            font.setBold(False)
            font.setPointSize(9)
            item.setFont(font)

            # Make header cells non-editable
            item.setFlags(Qt.ItemIsEnabled)

            self.jemaat_table.setItem(1, col, item)

        # Set row heights for headers (matching inventaris style)
        self.jemaat_table.setRowHeight(0, 30)  # Main category row
        self.jemaat_table.setRowHeight(1, 25)  # Sub-header column row

        # Set column widths
        self.setup_column_widths()

        # Make header rows non-editable and force refresh display
        for row in range(2):
            for col in range(35):
                item = self.jemaat_table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        # Ensure text is visible in spanned cells by explicitly setting text again
        self.ensure_spanned_text_visible()

        # Final step: ensure all styling is applied correctly
        self.apply_final_header_styling()

        # Force table to refresh and display all text properly
        self.jemaat_table.viewport().update()
        self.jemaat_table.repaint()

    def ensure_spanned_text_visible(self):
        """Ensure text in spanned cells is visible by explicitly setting text and styling again"""
        # Re-apply text and styling for "no" header cell in row 0 only
        no_item = self.jemaat_table.item(0, 0)
        if no_item:
            no_item.setText("no")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            # Apply Excel-style header styling
            no_item.setBackground(QColor("#f2f2f2"))
            no_item.setForeground(QColor("#333333"))
            font = QFont()
            font.setBold(False)
            font.setPointSize(9)
            no_item.setFont(font)

        # Ensure row 1 col 0 is EMPTY (no text)
        empty_item = self.jemaat_table.item(1, 0)
        if empty_item:
            empty_item.setText("")  # Keep it blank
            empty_item.setBackground(QColor("#f2f2f2"))
            empty_item.setForeground(QColor("#333333"))

        # Re-apply text and styling for colspan cells in first row
        sub_categories = [
            (1, "DATA PRIBADI"),
            (16, "SAKRAMEN BABTIS"),
            (20, "SAKRAMEN EKARISTI"),
            (23, "SAKRAMEN KRISMA"),
            (26, "SAKRAMEN PERKAWINAN"),
            (32, "STATUS")
        ]

        for col, text in sub_categories:
            item = self.jemaat_table.item(0, col)
            if item:
                item.setText(text)
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                # Apply struktur.py styling
                item.setBackground(QColor("#f2f2f2"))
                item.setForeground(QColor("#333333"))
                font = QFont()
                font.setBold(False)
                font.setPointSize(9)
                item.setFont(font)

    def apply_final_header_styling(self):
        """Apply final header styling to ensure inventaris/struktur.py consistency"""
        # Apply styling to all header cells in rows 0 and 1
        for row in range(2):  # Header rows
            for col in range(35):  # All columns (0-34)
                item = self.jemaat_table.item(row, col)
                if item and item.text():  # Only apply to non-empty cells
                    # Apply struktur.py header styling
                    item.setBackground(QColor("#f2f2f2"))
                    item.setForeground(QColor("#333333"))
                    font = QFont()
                    font.setBold(False)
                    font.setPointSize(9)
                    item.setFont(font)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

    def setup_column_widths(self):
        """Set up column widths for better display"""
        self.jemaat_table.setColumnWidth(0, 50)   # No. column
        # Make important columns wider
        self.jemaat_table.setColumnWidth(3, 150)  # Nama Lengkap - wider
        self.jemaat_table.setColumnWidth(14, 180)  # Alamat - wider
        self.jemaat_table.setColumnWidth(15, 140)  # Kontak - wider

        # Set standard width for other columns
        for i in [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]:  # DATA columns
            self.jemaat_table.setColumnWidth(i, 110)
        for i in range(16, 34):  # Sakramen and Status columns (updated to 34)
            self.jemaat_table.setColumnWidth(i, 100)
    
    
    def configure_simple_style(self, table):
        """Configure table with Excel-like styling and thin grid lines."""
        # Excel-style table styling
        header_font = QFont()
        header_font.setBold(False)  # Remove bold from headers
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

        # Excel-style professional styling matching struktur.py exactly
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

        # Excel-style table settings with proper sizing (matching struktur.py)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # All columns resizable like struktur.py
        header.setStretchLastSection(True)  # Last column stretches to fill space like struktur.py
        header.setMinimumSectionSize(50)
        header.setDefaultSectionSize(80)

        # Enable proper scrolling
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
        table.setGridStyle(Qt.SolidLine)
        table.setShowGrid(True)

        # Excel-style editing and selection
        table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Set compact size for Excel look
        table.setMinimumHeight(150)
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
        
        # Configure horizontal header (hidden since we use table cells)
        horizontal_header = table.horizontalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.Interactive)  # Allow drag resizing
        horizontal_header.setMinimumSectionSize(80)
        horizontal_header.setDefaultSectionSize(110)

        # Enable horizontal and vertical scrollbars
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    
    
    def populate_table(self):
        """Populate table with data rows (header ada di row 0 dan 1)"""
        # Set row count: 2 header rows + data rows
        self.jemaat_table.setRowCount(2 + len(self.jemaat_data))

        # Populate data starting from row 2 (after headers)
        for index, row_data in enumerate(self.jemaat_data):
            row_pos = 2 + index  # Start from row 2

            # Column 0: Row number (starting from 1)
            no_item = QTableWidgetItem(str(index + 1))
            no_item.setTextAlignment(Qt.AlignCenter)
            self.jemaat_table.setItem(row_pos, 0, no_item)
            
            # All data columns (1-34)
            data_items = [
                # DATA PRIBADI (columns 1-15)
                str(row_data.get('wilayah_rohani', '')),
                str(row_data.get('nama_keluarga', '')),
                str(row_data.get('nama_lengkap', '')),
                str(row_data.get('tempat_lahir', '')),
                self.format_date(row_data.get('tanggal_lahir')),
                str(row_data.get('umur', '')),
                str(row_data.get('kategori', '')),
                self.format_gender(row_data.get('jenis_kelamin', '')),
                str(row_data.get('hubungan_keluarga', '')),
                str(row_data.get('pendidikan_terakhir', '')),
                str(row_data.get('status_menikah', '')),
                str(row_data.get('jenis_pekerjaan', '')),
                str(row_data.get('detail_pekerjaan', '')),
                str(row_data.get('alamat', '')),
                str(row_data.get('email', '')),
                # SAKRAMEN BABTIS (columns 16-19)
                str(row_data.get('status_babtis', '')),
                str(row_data.get('tempat_babtis', '')),
                self.format_date(row_data.get('tanggal_babtis')),
                str(row_data.get('nama_babtis', '')),
                # SAKRAMEN EKARISTI (columns 20-22)
                str(row_data.get('status_ekaristi', '')),
                str(row_data.get('tempat_komuni', '')),
                self.format_date(row_data.get('tanggal_komuni')),
                # SAKRAMEN KRISMA (columns 23-25)
                str(row_data.get('status_krisma', '')),
                str(row_data.get('tempat_krisma', '')),
                self.format_date(row_data.get('tanggal_krisma')),
                # SAKRAMEN PERKAWINAN (columns 26-31)
                str(row_data.get('status_perkawinan', '')),
                str(row_data.get('keuskupan', '')),
                str(row_data.get('paroki', '')),
                str(row_data.get('kota_perkawinan', '')),
                self.format_date(row_data.get('tanggal_perkawinan')),
                str(row_data.get('status_perkawinan_detail', '')),
                # STATUS (columns 32-34) - as per user specification
                str(row_data.get('status_keanggotaan', 'Aktif')),
                str(row_data.get('wr_tujuan', '')),
                str(row_data.get('paroki_tujuan', ''))
            ]
            
            # Add data to columns 1-33 (total 34 columns including No. column)
            for col, item_text in enumerate(data_items, 1):
                item = QTableWidgetItem(item_text)
                # Center align certain columns for better readability
                if col in [0, 6, 7, 8, 16, 17, 20, 21, 23, 24, 26, 32]:  # Status and categorical columns
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.jemaat_table.setItem(row_pos, col, item)
    
    def format_date(self, date_value):
        """Format date for display in spreadsheet"""
        if not date_value:
            return ''
        if hasattr(date_value, 'strftime'):
            return date_value.strftime('%d/%m/%Y')
        return str(date_value)
    
    def format_gender(self, gender):
        """Format gender for display"""
        if gender == 'Laki-laki':
            return 'L'
        elif gender == 'Perempuan':
            return 'P'
        return str(gender)
    
    
    def add_jemaat(self):
        """Tambah jemaat baru"""
        dialog = JemaatDialog(self)
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
            
            try:
                # Filter data untuk compatibility dengan API yang ada
                # Hanya kirim field yang sudah ada di database lama
                filtered_data = {
                    'nama_lengkap': data.get('nama_lengkap', ''),
                    'alamat': data.get('alamat', ''),
                    'email': data.get('email', ''),
                    'tanggal_lahir': data.get('tanggal_lahir', ''),
                    'jenis_kelamin': 'Laki-laki' if data.get('jenis_kelamin') == 'L' else 'Perempuan'
                }
                
                success, result = self.db_manager.add_jemaat(filtered_data)
                
                if success:
                    QMessageBox.information(self, "Sukses", "Data jemaat berhasil ditambahkan")
                    self.load_data()
                    self.log_message.emit(f"Jemaat baru ditambahkan: {data['nama_lengkap']}")
                    
                    # Inform user about enhanced features
                    QMessageBox.information(self, "Info", 
                        "Data berhasil disimpan! Catatan: Fitur lengkap seperti sakramen dan wilayah rohani "
                        "akan tersedia setelah database server diupdate dengan schema terbaru.")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal menambahkan jemaat: {result}")
                    self.log_message.emit(f"Error adding jemaat: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error menambahkan jemaat: {str(e)}")
                self.log_message.emit(f"Exception adding jemaat: {str(e)}")
    
    def get_selected_row(self):
        """Get currently selected row index (adjusted for header rows)"""
        current_row = self.jemaat_table.currentRow()
        # Subtract 2 to account for header rows (rows 0 and 1)
        if current_row >= 2:
            return current_row - 2
        return -1  # Invalid selection (header row selected)
    
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
            
            try:
                # Filter data untuk compatibility dengan API yang ada
                # Hanya kirim field yang sudah ada di database lama
                filtered_data = {
                    'nama_lengkap': data.get('nama_lengkap', ''),
                    'alamat': data.get('alamat', ''),
                    'email': data.get('email', ''),
                    'tanggal_lahir': data.get('tanggal_lahir', ''),
                    'jenis_kelamin': 'Laki-laki' if data.get('jenis_kelamin') == 'L' else 'Perempuan'
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
    
    def search_jemaat(self):
        """Cari jemaat berdasarkan keyword"""
        self.load_data()
    
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
                        'Tanggal Lahir', 'Jenis Kelamin', 'Hubungan Keluarga', 'Pendidikan Terakhir',
                        'Jenis Pekerjaan', 'Detail Pekerjaan', 'Status Menikah', 'Alamat', 'Email',
                        'Status Babtis', 'Tempat Babtis', 'Tanggal Babtis', 'Nama Babtis',
                        'Status Ekaristi', 'Tempat Komuni', 'Tanggal Komuni',
                        'Status Krisma', 'Tempat Krisma', 'Tanggal Krisma',
                        'Status Perkawinan', 'Keuskupan', 'Paroki', 'Kota Perkawinan', 
                        'Tanggal Perkawinan', 'Status Perkawinan Detail', 'Status Keanggotaan'
                    ]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for data in self.jemaat_data:
                        writer.writerow({
                            'Nama Lengkap': data.get('nama_lengkap', ''),
                            'Wilayah Rohani': data.get('wilayah_rohani', ''),
                            'Nama Keluarga': data.get('nama_keluarga', ''),
                            'Tempat Lahir': data.get('tempat_lahir', ''),
                            'Tanggal Lahir': str(data.get('tanggal_lahir', '')),
                            'Jenis Kelamin': data.get('jenis_kelamin', ''),
                            'Hubungan Keluarga': data.get('hubungan_keluarga', ''),
                            'Pendidikan Terakhir': data.get('pendidikan_terakhir', ''),
                            'Jenis Pekerjaan': data.get('jenis_pekerjaan', ''),
                            'Detail Pekerjaan': data.get('detail_pekerjaan', ''),
                            'Status Menikah': data.get('status_menikah', ''),
                            'Alamat': data.get('alamat', ''),
                            'Email': data.get('email', ''),
                            'Status Babtis': data.get('status_babtis', ''),
                            'Tempat Babtis': data.get('tempat_babtis', ''),
                            'Tanggal Babtis': str(data.get('tanggal_babtis', '')),
                            'Nama Babtis': data.get('nama_babtis', ''),
                            'Status Ekaristi': data.get('status_ekaristi', ''),
                            'Tempat Komuni': data.get('tempat_komuni', ''),
                            'Tanggal Komuni': str(data.get('tanggal_komuni', '')),
                            'Status Krisma': data.get('status_krisma', ''),
                            'Tempat Krisma': data.get('tempat_krisma', ''),
                            'Tanggal Krisma': str(data.get('tanggal_krisma', '')),
                            'Status Perkawinan': data.get('status_perkawinan', ''),
                            'Keuskupan': data.get('keuskupan', ''),
                            'Paroki': data.get('paroki', ''),
                            'Kota Perkawinan': data.get('kota_perkawinan', ''),
                            'Tanggal Perkawinan': str(data.get('tanggal_perkawinan', '')),
                            'Status Perkawinan Detail': data.get('status_perkawinan_detail', ''),
                            'Status Keanggotaan': data.get('status_keanggotaan', '')
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
                from config import ServerConfig
                
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
        details = f"""
<h2>DETAIL JEMAAT</h2>
<h3>DATA DIRI</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Nama Lengkap:</b></td><td>{jemaat_data.get('nama_lengkap', '')}</td></tr>
<tr><td><b>Wilayah Rohani:</b></td><td>{jemaat_data.get('wilayah_rohani', '')}</td></tr>
<tr><td><b>Nama Keluarga:</b></td><td>{jemaat_data.get('nama_keluarga', '')}</td></tr>
<tr><td><b>Tempat Lahir:</b></td><td>{jemaat_data.get('tempat_lahir', '')}</td></tr>
<tr><td><b>Tanggal Lahir:</b></td><td>{self.format_date(jemaat_data.get('tanggal_lahir'))}</td></tr>
<tr><td><b>Umur:</b></td><td>{jemaat_data.get('umur', '')}</td></tr>
<tr><td><b>Kategori:</b></td><td>{jemaat_data.get('kategori', '')}</td></tr>
<tr><td><b>Jenis Kelamin:</b></td><td>{jemaat_data.get('jenis_kelamin', '')}</td></tr>
<tr><td><b>Hubungan Keluarga:</b></td><td>{jemaat_data.get('hubungan_keluarga', '')}</td></tr>
<tr><td><b>Pendidikan Terakhir:</b></td><td>{jemaat_data.get('pendidikan_terakhir', '')}</td></tr>
<tr><td><b>Status Menikah:</b></td><td>{jemaat_data.get('status_menikah', '')}</td></tr>
<tr><td><b>Status Pekerjaan:</b></td><td>{jemaat_data.get('jenis_pekerjaan', '')}</td></tr>
</table>

<h3>SAKRAMEN</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Status Babtis:</b></td><td>{jemaat_data.get('status_babtis', '')}</td></tr>
<tr><td><b>Tempat Babtis:</b></td><td>{jemaat_data.get('tempat_babtis', '')}</td></tr>
<tr><td><b>Tanggal Babtis:</b></td><td>{self.format_date(jemaat_data.get('tanggal_babtis'))}</td></tr>
<tr><td><b>Status Ekaristi:</b></td><td>{jemaat_data.get('status_ekaristi', '')}</td></tr>
<tr><td><b>Tempat Komuni:</b></td><td>{jemaat_data.get('tempat_komuni', '')}</td></tr>
<tr><td><b>Tanggal Komuni:</b></td><td>{self.format_date(jemaat_data.get('tanggal_komuni'))}</td></tr>
<tr><td><b>Status Krisma:</b></td><td>{jemaat_data.get('status_krisma', '')}</td></tr>
<tr><td><b>Tempat Krisma:</b></td><td>{jemaat_data.get('tempat_krisma', '')}</td></tr>
<tr><td><b>Tanggal Krisma:</b></td><td>{self.format_date(jemaat_data.get('tanggal_krisma'))}</td></tr>
</table>

<h3>KONTAK & ALAMAT</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Email:</b></td><td>{jemaat_data.get('email', '')}</td></tr>
<tr><td><b>Alamat:</b></td><td>{jemaat_data.get('alamat', '')}</td></tr>
</table>

<h3>STATUS</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Status Keanggotaan:</b></td><td>{jemaat_data.get('status_keanggotaan', '')}</td></tr>
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