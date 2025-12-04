# Path: server/components/inventaris.py (Upgraded to Aset - Asset Management)

import datetime
import csv
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QGroupBox, QMessageBox,
                            QFileDialog, QAbstractItemView, QFrame, QLineEdit, QComboBox,
                            QStyle, QStyledItemDelegate)
from PyQt5.QtCore import pyqtSignal, QDate, Qt, QSize, QRect, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor, QBrush, QPainter

# Import dialog aset yang sudah diupgrade
from .dialogs import AsetDialog

# Custom delegate untuk preserve warna cell saat selection
class ColorPreservingDelegate(QStyledItemDelegate):
    """Custom delegate yang mempertahankan warna cell bahkan saat selected"""
    def paint(self, painter, option, index):
        # Get the background and foreground colors from the item data
        bg_color = index.data(Qt.BackgroundRole)
        fg_color = index.data(Qt.ForegroundRole)

        # If we have custom colors, use them
        if bg_color and fg_color:
            # Paint background
            painter.save()
            painter.fillRect(option.rect, bg_color)

            # Paint text - extract color from brush if needed
            if isinstance(fg_color, QBrush):
                painter.setPen(fg_color.color())
            else:
                painter.setPen(fg_color)

            text = index.data(Qt.DisplayRole)
            font = index.data(Qt.FontRole)
            if font:
                painter.setFont(font)

            # Center alignment for text
            painter.drawText(option.rect, Qt.AlignCenter | Qt.AlignVCenter, str(text))

            # Draw focus border if focused
            if option.state & QStyle.State_HasFocus:
                pen = painter.pen()
                pen.setColor(QColor(0, 120, 212))  # #0078d4
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawRect(option.rect.adjusted(0, 0, -1, -1))

            painter.restore()
        else:
            # Use default delegate for non-colored cells
            super().paint(painter, option, index)

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

class AsetComponent(QWidget):
    """Komponen untuk manajemen aset (upgraded dari inventaris)"""

    data_updated = pyqtSignal()
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, parent=None):
        super().__init__(parent)
        self.aset_data = []
        self.db_manager = None
        self.current_admin = None
        self.setup_ui()

    def set_database_manager(self, db_manager):
        """Set database manager."""
        self.db_manager = db_manager
        # Auto load data setelah database manager di-set
        if self.db_manager:
            self.load_data()

    def set_current_admin(self, admin_data):
        """Set the current admin data."""
        self.current_admin = admin_data

    def setup_ui(self):
        """Setup UI untuk halaman aset."""
        layout = QVBoxLayout(self)

        # Clean header without background (matching pengaturan style)
        header_frame = QWidget()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 10, 0)

        title_label = QLabel("Manajemen Aset")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header_frame)

        # Original header with buttons and search
        header = self.create_header()
        layout.addWidget(header)

        # Statistik Aset
        stats_group = self.create_statistics()
        layout.addWidget(stats_group)

        # Tabel aset
        self.aset_table_container = self.create_table()
        layout.addWidget(self.aset_table_container)

        # Tombol aksi
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)

    def create_header(self):
        """Buat header dengan kontrol pencarian dan tombol tambah - Simple Layout matching jemaat style."""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 10, 0)

        # Search functionality dengan label
        header_layout.addWidget(QLabel("Cari:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama aset...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.filter_data)
        header_layout.addWidget(self.search_input)

        # Filter Kondisi
        header_layout.addWidget(QLabel("Kondisi:"))

        self.filter_kondisi = QComboBox()
        self.filter_kondisi.addItems(["Semua", "Baik", "Rusak Ringan", "Rusak Berat", "Tidak Terpakai"])
        self.filter_kondisi.setFixedWidth(150)
        self.filter_kondisi.currentTextChanged.connect(self.filter_data)
        header_layout.addWidget(self.filter_kondisi)

        # Filter Status
        header_layout.addWidget(QLabel("Status:"))

        self.filter_status = QComboBox()
        self.filter_status.addItems(["Semua", "Aktif", "Tidak Aktif", "Dalam Perbaikan", "Dijual/Dihapus"])
        self.filter_status.setFixedWidth(150)
        self.filter_status.currentTextChanged.connect(self.filter_data)
        header_layout.addWidget(self.filter_status)

        # Filter Tahun Perolehan
        header_layout.addWidget(QLabel("Tahun:"))

        self.filter_tahun = QComboBox()
        self.filter_tahun.addItem("Semua")
        self.filter_tahun.setFixedWidth(120)
        self.filter_tahun.currentTextChanged.connect(self.filter_data)
        header_layout.addWidget(self.filter_tahun)

        header_layout.addStretch()

        add_button = self.create_button("Tambah Aset", "#27ae60", self.add_aset, "server/assets/tambah.png")
        header_layout.addWidget(add_button)

        return header

    def create_statistics(self):
        """Buat panel statistik aset."""
        stats_group = QGroupBox("Ringkasan Aset")
        stats_layout = QHBoxLayout(stats_group)

        self.total_items_value = QLabel("0")
        self.total_value_value = QLabel("Rp 0")
        self.good_condition_value = QLabel("0")
        self.need_attention_value = QLabel("0")

        stats_layout.addWidget(self.create_stat_widget("TOTAL ASET", self.total_items_value, "#ddeaee", "#2c3e50"))
        stats_layout.addWidget(self.create_stat_widget("NILAI TOTAL", self.total_value_value, "#e8f8f5", "#27ae60"))
        stats_layout.addWidget(self.create_stat_widget("KONDISI BAIK", self.good_condition_value, "#e3f2fd", "#3498db"))
        stats_layout.addWidget(self.create_stat_widget("PERLU PERHATIAN", self.need_attention_value, "#fdf2e9", "#e67e22"))

        return stats_group

    def create_stat_widget(self, label_text, value_label, bg_color, text_color):
        """Buat widget statistik dengan style."""
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 4px;
                padding: 6px;
            }}
        """)
        widget.setMaximumHeight(60)
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(6, 6, 6, 6)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                color: {text_color};
                font-size: 9px;
                font-family: Arial, sans-serif;
                background-color: transparent;
                min-height: 12px;
            }}
        """)

        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {text_color};
                font-family: Arial, sans-serif;
                background-color: transparent;
                padding: 2px;
                min-height: 16px;
            }}
        """)

        layout.addWidget(label)
        layout.addWidget(value_label)

        return widget

    def create_table(self):
        """Buat tabel aset dengan style profesional."""
        # Table view dalam container frame
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

        table = QTableWidget(0, 13)

        # Set custom header with word wrap and center alignment
        custom_header = WordWrapHeaderView(Qt.Horizontal, table)
        table.setHorizontalHeader(custom_header)

        table.setHorizontalHeaderLabels([
            "Kode Aset", "Nama Aset", "Jenis", "Kategori", "Merk/Tipe",
            "Tahun", "Sumber", "Nilai (Rp)", "Kondisi", "Lokasi", "Status", "Penanggung Jawab", "Keterangan"
        ])

        # Apply professional styling matching struktur.py
        self.apply_professional_table_style(table)

        # Set initial column widths
        table.setColumnWidth(0, 100)   # Kode Aset
        table.setColumnWidth(1, 140)   # Nama Aset
        table.setColumnWidth(2, 90)    # Jenis
        table.setColumnWidth(3, 110)   # Kategori
        table.setColumnWidth(4, 100)   # Merk/Tipe
        table.setColumnWidth(5, 80)    # Tahun
        table.setColumnWidth(6, 120)   # Sumber
        table.setColumnWidth(7, 120)   # Nilai
        table.setColumnWidth(8, 100)   # Kondisi
        table.setColumnWidth(9, 110)   # Lokasi
        table.setColumnWidth(10, 120)  # Status
        table.setColumnWidth(11, 140)  # Penanggung Jawab
        table.setColumnWidth(12, 150)  # Keterangan

        # Excel-like column resizing
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # Update header height when column is resized
        header.sectionResized.connect(self.update_header_height)

        # Enable context menu
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu)

        # Connect double click to edit
        table.itemDoubleClicked.connect(self.edit_aset)

        table_layout.addWidget(table)
        self.aset_table = table

        # Initial header height calculation
        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

        return table_container

    def update_header_height(self, logicalIndex, oldSize, newSize):
        """Update header height when column is resized"""
        if hasattr(self, 'aset_table'):
            header = self.aset_table.horizontalHeader()
            header.setMinimumHeight(25)
            max_height = 25

            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            header.setFixedHeight(max_height)

    def apply_professional_table_style(self, table):
        """Apply Excel-like table styling."""
        # Header styling
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

        # Configure header behavior
        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        header.setMinimumHeight(25)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(500)

        # Excel-style table body styling - carefully tuned to preserve colored cells
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d4d4d4;
                background-color: white;
                border: 1px solid #d4d4d4;
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
                border: 2px solid #0078d4;
                outline: none;
            }
            QTableWidget::item:focus {
                border: 2px solid #0078d4;
                outline: none;
            }
        """)

        # Apply custom delegate untuk preserve colored cells
        delegate = ColorPreservingDelegate(table)
        table.setItemDelegate(delegate)

        # Excel-style settings
        header = table.horizontalHeader()
        header.setDefaultSectionSize(80)

        # Enable scrolling
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Excel-style row settings
        table.verticalHeader().setDefaultSectionSize(30)
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

        # Enable grid display
        table.setShowGrid(True)
        table.setGridStyle(Qt.PenStyle.SolidLine)

        # Excel-style editing and selection
        table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Set compact size
        table.setMinimumHeight(150)
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    def show_context_menu(self, position):
        """Tampilkan context menu untuk edit/hapus"""
        if self.aset_table.rowCount() == 0:
            return

        from PyQt5.QtWidgets import QMenu
        menu = QMenu()

        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")

        action = menu.exec_(self.aset_table.mapToGlobal(position))

        if action == edit_action:
            self.edit_aset()
        elif action == delete_action:
            self.delete_aset()

    def create_action_buttons(self):
        """Buat tombol-tombol aksi."""
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        action_layout.addStretch()

        edit_button = self.create_button("Edit", "#f39c12", self.edit_aset, "server/assets/edit.png")
        action_layout.addWidget(edit_button)

        delete_button = self.create_button("Hapus", "#c0392b", self.delete_aset, "server/assets/hapus.png")
        action_layout.addWidget(delete_button)

        export_button = self.create_button(".CSV", "#16a085", self.export_data, "server/assets/export.png")
        action_layout.addWidget(export_button)

        return action_layout

    def create_button(self, text, color, slot, icon_path=None):
        """Buat button dengan style konsisten dan optional icon."""
        button = QPushButton(text)

        # Add icon if specified and path exists
        if icon_path:
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(20, 20))
            except Exception:
                pass

        hover_color = self.lighten_color(color)
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
                background-color: {hover_color};
            }}
        """)
        button.clicked.connect(slot)
        return button

    def lighten_color(self, color):
        """Buat warna lebih terang untuk hover effect"""
        color_map = {
            "#27ae60": "#2ecc71",  # Hijau -> lebih terang
            "#c0392b": "#e74c3c",  # Merah -> lebih terang
            "#3498db": "#5dade2",  # Biru -> lebih terang
            "#16a085": "#1abc9c",  # Teal -> lebih terang
            "#8e44ad": "#9b59b6",  # Ungu -> lebih terang
            "#f39c12": "#f1c40f",  # Orange -> lebih terang
            "#2ecc71": "#52d97e",  # Light green -> lebih terang
            "#e74c3c": "#ec7063",  # Light red -> lebih terang
        }
        return color_map.get(color, color)

    def load_data(self):
        """Load data aset dari database."""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            # Test koneksi database terlebih dahulu
            if not hasattr(self.db_manager, 'get_aset_list'):
                self.log_message.emit("Error: Database manager tidak memiliki method get_aset_list")
                return

            self.log_message.emit("Mencoba memuat data aset...")
            # Load semua data tanpa search filter untuk caching
            success, aset = self.db_manager.get_aset_list(search=None)

            if success:
                # Handle different response formats
                if isinstance(aset, dict) and 'data' in aset:
                    data_list = aset['data'] if aset['data'] else []
                elif isinstance(aset, list):
                    data_list = aset if aset else []
                else:
                    data_list = []

                # Simpan ke all_aset_data untuk filtering
                self.all_aset_data = data_list.copy()
                self.aset_data = data_list

                self.populate_table()
                self.log_message.emit(f"Data aset berhasil dimuat: {len(self.aset_data)} record")
                # Update tahun filter dropdown setelah data loaded
                self.update_tahun_filter()
            else:
                self.all_aset_data = []
                self.aset_data = []
                self.populate_table()
                self.log_message.emit(f"Gagal memuat data aset: {aset}")

            self.update_statistics()
            self.log_message.emit("Proses loading data aset selesai")
            self.data_updated.emit()
        except Exception as e:
            self.log_message.emit(f"Exception saat memuat data aset: {str(e)}")
            # Reset data jika terjadi error
            self.all_aset_data = []
            self.aset_data = []
            self.populate_table()
            self.update_statistics()

    def populate_table(self):
        """Populate tabel dengan data aset."""
        self.aset_table.setRowCount(0)
        for row_data in self.aset_data:
            row_pos = self.aset_table.rowCount()
            self.aset_table.insertRow(row_pos)

            # Kode Aset - Center aligned
            kode_item = QTableWidgetItem(str(row_data.get('kode_aset', '')))
            kode_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.aset_table.setItem(row_pos, 0, kode_item)

            # Nama Aset - Left aligned
            nama_item = QTableWidgetItem(str(row_data.get('nama_aset', '')))
            nama_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.aset_table.setItem(row_pos, 1, nama_item)

            # Jenis Aset - Center aligned
            jenis_item = QTableWidgetItem(str(row_data.get('jenis_aset', '')))
            jenis_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.aset_table.setItem(row_pos, 2, jenis_item)

            # Kategori - Center aligned
            kategori_item = QTableWidgetItem(str(row_data.get('kategori', '')))
            kategori_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.aset_table.setItem(row_pos, 3, kategori_item)

            # Merk/Tipe - Left aligned
            merk_item = QTableWidgetItem(str(row_data.get('merk_tipe', '')))
            merk_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.aset_table.setItem(row_pos, 4, merk_item)

            # Tahun Perolehan - Center aligned
            tahun_item = QTableWidgetItem(str(row_data.get('tahun_perolehan', '')))
            tahun_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.aset_table.setItem(row_pos, 5, tahun_item)

            # Sumber Perolehan - Left aligned
            sumber_item = QTableWidgetItem(str(row_data.get('sumber_perolehan', '')))
            sumber_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.aset_table.setItem(row_pos, 6, sumber_item)

            # Nilai - Right aligned for currency
            nilai = row_data.get('nilai', 0)
            try:
                nilai_float = float(nilai)
                nilai_str = f"Rp {nilai_float:,.0f}".replace(',', '.')
            except (ValueError, TypeError):
                nilai_str = f"Rp 0"
            nilai_item = QTableWidgetItem(nilai_str)
            nilai_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.aset_table.setItem(row_pos, 7, nilai_item)

            # Kondisi - Center aligned, no styling
            kondisi = str(row_data.get('kondisi', '')).strip()
            kondisi_item = QTableWidgetItem(kondisi)
            kondisi_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.aset_table.setItem(row_pos, 8, kondisi_item)

            # Lokasi - Left aligned
            lokasi_item = QTableWidgetItem(str(row_data.get('lokasi', '')))
            lokasi_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.aset_table.setItem(row_pos, 9, lokasi_item)

            # Status - Center aligned, no styling
            status = str(row_data.get('status', '')).strip()
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.aset_table.setItem(row_pos, 10, status_item)

            # Penanggung Jawab - Left aligned
            pj_item = QTableWidgetItem(str(row_data.get('penanggung_jawab', '')))
            pj_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.aset_table.setItem(row_pos, 11, pj_item)

            # Keterangan - Left aligned
            keterangan_item = QTableWidgetItem(str(row_data.get('keterangan', '')))
            keterangan_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.aset_table.setItem(row_pos, 12, keterangan_item)

    def update_statistics(self):
        """Update panel statistik."""
        if not self.aset_data:
            self.total_items_value.setText("0")
            self.total_value_value.setText("Rp 0")
            self.good_condition_value.setText("0")
            self.need_attention_value.setText("0")
            return

        # Hitung total aset
        total_items = len(self.aset_data)
        self.total_items_value.setText(str(total_items))

        # Hitung nilai total
        total_value = 0
        good_condition = 0
        need_attention = 0

        for item in self.aset_data:
            try:
                nilai = float(item.get('nilai', 0))
                total_value += nilai
            except (ValueError, TypeError):
                continue

            kondisi = item.get('kondisi', '')
            if kondisi == 'Baik':
                good_condition += 1
            elif kondisi in ['Rusak Ringan', 'Rusak Berat', 'Tidak Terpakai']:
                need_attention += 1

        # Update tampilan
        self.total_value_value.setText(f"Rp {total_value:,.0f}".replace(',', '.'))
        self.good_condition_value.setText(str(good_condition))
        self.need_attention_value.setText(str(need_attention))

    def update_tahun_filter(self):
        """Update tahun perolehan filter dropdown berdasarkan data yang tersedia"""
        if not hasattr(self, 'filter_tahun'):
            return

        # Get unique years from data
        current_text = self.filter_tahun.currentText()
        self.filter_tahun.blockSignals(True)  # Temporarily block signals to prevent filter_data trigger
        self.filter_tahun.clear()
        self.filter_tahun.addItem("Semua")

        # Collect unique years
        tahun_list = set()
        if hasattr(self, 'all_aset_data') and self.all_aset_data:
            for item in self.all_aset_data:
                tahun = item.get('tahun_perolehan')
                if tahun:
                    tahun_str = str(tahun).strip()
                    if tahun_str and tahun_str.isdigit():
                        tahun_list.add(tahun_str)

        # Sort tahun in descending order (newest first)
        tahun_sorted = sorted(tahun_list, reverse=True)
        for tahun in tahun_sorted:
            self.filter_tahun.addItem(tahun)

        # Restore previous selection if exists
        index = self.filter_tahun.findText(current_text)
        if index >= 0:
            self.filter_tahun.setCurrentIndex(index)

        self.filter_tahun.blockSignals(False)  # Re-enable signals

    def filter_data(self):
        """Filter data aset berdasarkan keyword pencarian, kondisi, status, dan tahun"""
        search_text = self.search_input.text().lower().strip()
        filter_kondisi = self.filter_kondisi.currentText() if hasattr(self, 'filter_kondisi') else "Semua"
        filter_status = self.filter_status.currentText() if hasattr(self, 'filter_status') else "Semua"
        filter_tahun = self.filter_tahun.currentText() if hasattr(self, 'filter_tahun') else "Semua"

        # Jika tidak ada filter, restore dari cache
        if not search_text and filter_kondisi == "Semua" and filter_status == "Semua" and filter_tahun == "Semua":
            # Restore original data jika ada
            if hasattr(self, 'all_aset_data') and self.all_aset_data:
                self.aset_data = self.all_aset_data.copy()
            self.populate_table()
            self.update_statistics()
            return

        # Simpan data asli jika belum disimpan
        if not hasattr(self, 'all_aset_data') or not self.all_aset_data:
            self.all_aset_data = self.aset_data.copy() if self.aset_data else []

        # Filter data berdasarkan keyword, kondisi, dan status
        filtered_data = []

        for data in self.all_aset_data:
            # Filter berdasarkan kondisi terlebih dahulu
            if filter_kondisi != "Semua":
                kondisi = (data.get('kondisi') or '').strip()
                if kondisi != filter_kondisi:
                    continue

            # Filter berdasarkan status
            if filter_status != "Semua":
                status = (data.get('status') or '').strip()
                if status != filter_status:
                    continue

            # Filter berdasarkan tahun perolehan
            if filter_tahun != "Semua":
                tahun = str(data.get('tahun_perolehan') or '').strip()
                if tahun != filter_tahun:
                    continue

            # Jika ada search text, filter berdasarkan keyword
            if search_text:
                # Cari di berbagai field
                kode_aset = (data.get('kode_aset') or '').lower()
                nama_aset = (data.get('nama_aset') or '').lower()
                kategori = (data.get('kategori') or '').lower()
                merk_tipe = (data.get('merk_tipe') or '').lower()
                lokasi = (data.get('lokasi') or '').lower()
                penanggung_jawab = (data.get('penanggung_jawab') or '').lower()
                sumber_perolehan = (data.get('sumber_perolehan') or '').lower()

                # Search di semua field yang relevan
                if not (search_text in kode_aset or
                        search_text in nama_aset or
                        search_text in kategori or
                        search_text in merk_tipe or
                        search_text in lokasi or
                        search_text in penanggung_jawab or
                        search_text in sumber_perolehan):
                    continue

            # Jika lolos semua filter, tambahkan ke hasil
            filtered_data.append(data)

        # Update display dengan data yang difilter
        self.aset_data = filtered_data
        self.populate_table()
        self.update_statistics()

    def refresh_data(self):
        """Refresh data dari database"""
        # Clear search input
        self.search_input.clear()

        # Reset filter kondisi ke "Semua"
        if hasattr(self, 'filter_kondisi'):
            self.filter_kondisi.setCurrentText("Semua")

        # Reset filter status ke "Semua"
        if hasattr(self, 'filter_status'):
            self.filter_status.setCurrentText("Semua")

        # Reset filter tahun ke "Semua"
        if hasattr(self, 'filter_tahun'):
            self.filter_tahun.setCurrentText("Semua")

        # Clear cached data
        if hasattr(self, 'all_aset_data'):
            self.all_aset_data = []

        # Reload data from database
        self.load_data()

        self.log_message.emit("Data aset berhasil di-refresh")

    def add_aset(self):
        """Tambah aset baru."""
        dialog = AsetDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            # Validasi
            if not data['nama_aset']:
                QMessageBox.warning(self, "Error", "Nama aset harus diisi")
                return

            if not data['kode_aset']:
                QMessageBox.warning(self, "Error", "Kode aset harus diisi")
                return

            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            # Check if method exists
            if not hasattr(self.db_manager, 'add_aset'):
                QMessageBox.critical(self, "Error", "Method add_aset tidak tersedia di database manager")
                self.log_message.emit("Method add_aset tidak tersedia")
                return

            self.log_message.emit("Mencoba menambahkan aset...")
            success, result = self.db_manager.add_aset(data)
            if success:
                QMessageBox.information(self, "Sukses", "Aset berhasil ditambahkan.")
                self.load_data()
                self.log_message.emit("Aset berhasil ditambahkan")
            else:
                QMessageBox.critical(self, "Error", f"Gagal menambahkan aset: {result}")
                self.log_message.emit(f"API Error - Gagal menambahkan aset: {result}")

    def edit_aset(self):
        """Edit aset yang dipilih"""
        current_row = self.aset_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih aset yang akan diedit")
            return

        if current_row >= len(self.aset_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return

        aset_data = self.aset_data[current_row]

        dialog = AsetDialog(self, aset_data)
        if dialog.exec_() == dialog.Accepted:
            updated_data = dialog.get_data()

            # Validasi
            if not updated_data['nama_aset']:
                QMessageBox.warning(self, "Error", "Nama aset harus diisi")
                return

            if not updated_data['kode_aset']:
                QMessageBox.warning(self, "Error", "Kode aset harus diisi")
                return

            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            # Update melalui API
            aset_id = aset_data.get('id_aset')
            if aset_id and hasattr(self.db_manager, 'update_aset'):
                success, result = self.db_manager.update_aset(aset_id, updated_data)
                if success:
                    QMessageBox.information(self, "Sukses", "Aset berhasil diupdate.")
                    self.load_data()
                    self.log_message.emit("Aset berhasil diupdate")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal mengupdate aset: {result}")
                    self.log_message.emit(f"Error update aset: {result}")
            else:
                QMessageBox.critical(self, "Error", "Method update_aset tidak tersedia")

    def delete_aset(self):
        """Hapus aset yang dipilih"""
        current_row = self.aset_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih aset yang akan dihapus")
            return

        if current_row >= len(self.aset_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return

        aset_data = self.aset_data[current_row]
        nama_aset = aset_data.get('nama_aset', 'Unknown')

        reply = QMessageBox.question(self, 'Konfirmasi',
                                    f"Yakin ingin menghapus aset '{nama_aset}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            aset_id = aset_data.get('id_aset')
            if aset_id and hasattr(self.db_manager, 'delete_aset'):
                success, result = self.db_manager.delete_aset(aset_id)
                if success:
                    QMessageBox.information(self, "Sukses", "Aset berhasil dihapus.")
                    self.load_data()
                    self.log_message.emit("Aset berhasil dihapus")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal menghapus aset: {result}")
                    self.log_message.emit(f"Error hapus aset: {result}")
            else:
                QMessageBox.critical(self, "Error", "Method delete_aset tidak tersedia")

    def export_data(self):
        """Export data aset ke file CSV."""
        if not self.aset_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Data Aset", "data_aset.csv", "CSV Files (*.csv)")
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Kode Aset", "Nama Aset", "Jenis", "Kategori", "Merk/Tipe", "Tahun Perolehan",
                    "Sumber Perolehan", "Nilai", "Kondisi", "Lokasi", "Status", "Penanggung Jawab", "Keterangan"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in self.aset_data:
                    writer.writerow({
                        "Kode Aset": item.get('kode_aset', ''),
                        "Nama Aset": item.get('nama_aset', ''),
                        "Jenis": item.get('jenis_aset', ''),
                        "Kategori": item.get('kategori', ''),
                        "Merk/Tipe": item.get('merk_tipe', ''),
                        "Tahun Perolehan": item.get('tahun_perolehan', ''),
                        "Sumber Perolehan": item.get('sumber_perolehan', ''),
                        "Nilai": item.get('nilai', ''),
                        "Kondisi": item.get('kondisi', ''),
                        "Lokasi": item.get('lokasi', ''),
                        "Status": item.get('status', ''),
                        "Penanggung Jawab": item.get('penanggung_jawab', ''),
                        "Keterangan": item.get('keterangan', '')
                    })

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data aset diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
            self.log_message.emit(f"Gagal mengekspor data: {str(e)}")

    def get_data(self):
        """Ambil data aset untuk komponen lain."""
        return self.aset_data
