# Path: server/components/kegiatan_wr.py
# Kegiatan WR (Wilayah Rohani) Tab Component

import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                           QFileDialog, QMenu, QMessageBox, QDialog, QTextEdit,
                           QGroupBox, QComboBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QBrush, QColor, QIcon

# Import WordWrapHeaderView from proker_base
from .proker_base import WordWrapHeaderView


class KegiatanWRWidget(QWidget):
    """Widget untuk tab Kegiatan WR - menampilkan kegiatan dari client"""

    data_updated = pyqtSignal()
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.kegiatan_data = []
        self.setup_ui()

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        if db_manager:
            self.load_data()

    def setup_ui(self):
        """Setup UI untuk kegiatan WR"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title section
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

        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 0, 10, 0)
        content_layout.setSpacing(5)

        # Header with refresh button
        header = self.create_header()
        content_layout.addWidget(header)

        # Filter section
        filter_group = self.create_filters()
        content_layout.addWidget(filter_group)

        # Table
        table_widget = self.create_table()
        content_layout.addWidget(table_widget, 1)

        # Action buttons
        action_layout = self.create_action_buttons()
        content_layout.addLayout(action_layout, 0)

        layout.addWidget(content_widget)

    def create_header(self):
        """Create header with refresh button"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 5, 10, 5)

        header_layout.addStretch()

        refresh_button = self.create_button("Refresh Data", "#3498db", self.load_data, "server/assets/refresh.png")
        header_layout.addWidget(refresh_button)

        return header

    def create_filters(self):
        """Create filter section (matching Kegiatan Paroki - dropdown only)"""
        filter_group = QGroupBox()
        filter_layout = QHBoxLayout(filter_group)

        # User filter
        user_label = QLabel("Filter User:")
        filter_layout.addWidget(user_label)

        self.user_filter = QComboBox()
        self.user_filter.addItem("Semua User")
        self.user_filter.currentTextChanged.connect(self.filter_kegiatan)
        filter_layout.addWidget(self.user_filter)

        # Category filter
        category_label = QLabel("Kategori:")
        filter_layout.addWidget(category_label)

        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "Semua", "Ibadah", "Doa", "Katekese", "Sosial",
            "Rohani", "Administratif", "Lainnya"
        ])
        self.category_filter.currentTextChanged.connect(self.filter_kegiatan)
        filter_layout.addWidget(self.category_filter)

        filter_layout.addStretch()

        return filter_group

    def create_table(self):
        """Create table for kegiatan paroki with new column order"""
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

        self.kegiatan_table = QTableWidget(0, 9)

        # Set custom header with word wrap and center alignment
        custom_header_kegiatan = WordWrapHeaderView(Qt.Horizontal, self.kegiatan_table)
        self.kegiatan_table.setHorizontalHeader(custom_header_kegiatan)

        # New column order: Kategori, Nama Kegiatan, Keterangan, Lokasi, Tanggal, Waktu, Biaya, Penanggung Jawab, Status
        self.kegiatan_table.setHorizontalHeaderLabels([
            "Kategori", "Nama Kegiatan", "Keterangan", "Lokasi", "Tanggal Kegiatan",
            "Waktu Kegiatan", "Biaya", "Penanggung Jawab", "Status"
        ])

        # Apply professional table styling
        self.apply_professional_table_style(self.kegiatan_table)

        # Set column widths - sesuai new order
        self.kegiatan_table.setColumnWidth(0, 100)   # Kategori
        self.kegiatan_table.setColumnWidth(1, 180)   # Nama Kegiatan
        self.kegiatan_table.setColumnWidth(2, 150)   # Keterangan
        self.kegiatan_table.setColumnWidth(3, 120)   # Lokasi
        self.kegiatan_table.setColumnWidth(4, 120)   # Tanggal Kegiatan
        self.kegiatan_table.setColumnWidth(5, 110)   # Waktu Kegiatan
        self.kegiatan_table.setColumnWidth(6, 100)   # Biaya
        self.kegiatan_table.setColumnWidth(7, 130)   # Penanggung Jawab
        self.kegiatan_table.setColumnWidth(8, 100)   # Status

        header = self.kegiatan_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # Update header height when column is resized
        header.sectionResized.connect(lambda idx, old, new: self.update_kegiatan_header_height())

        # Enable context menu
        self.kegiatan_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.kegiatan_table.customContextMenuRequested.connect(self.show_context_menu)

        table_layout.addWidget(self.kegiatan_table)

        # Initial header height calculation
        QTimer.singleShot(100, self.update_kegiatan_header_height)

        return table_container

    def update_kegiatan_header_height(self):
        """Update header height for kegiatan table when column is resized"""
        if hasattr(self, 'kegiatan_table'):
            header = self.kegiatan_table.horizontalHeader()
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
        """Apply Excel-like table styling with bold headers and word wrap"""
        header_font = QFont()
        header_font.setBold(True)  # Make headers bold
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

        # Configure header behavior with center alignment
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
        """Create action buttons layout"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        view_button = self.create_button("Lihat Detail", "#3498db", self.view_kegiatan, "server/assets/view.png")
        action_layout.addWidget(view_button)

        export_button = self.create_button("Export CSV", "#16a085", self.export_kegiatan, "server/assets/export.png")
        action_layout.addWidget(export_button)

        return action_layout

    def create_button(self, text, color, slot, icon_path=None):
        """Create button with consistent style and optional icon"""
        button = QPushButton(text)

        if icon_path:
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(20, 20))
            except Exception:
                pass

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
        """Darken color for hover effect"""
        color_map = {
            "#3498db": "#2980b9",
            "#27ae60": "#2ecc71",
            "#f39c12": "#f1c40f",
            "#c0392b": "#e74c3c",
            "#16a085": "#1abc9c",
            "#8e44ad": "#9b59b6",
            "#9b59b6": "#8e44ad"
        }
        return color_map.get(color, color)

    def show_context_menu(self, position):
        """Show context menu for view"""
        if self.kegiatan_table.rowCount() == 0:
            return

        menu = QMenu()
        view_action = menu.addAction("Lihat Detail")
        export_action = menu.addAction("Export")

        action = menu.exec_(self.kegiatan_table.mapToGlobal(position))

        if action == view_action:
            self.view_kegiatan()
        elif action == export_action:
            self.export_kegiatan()

    def load_data(self):
        """Load kegiatan data from database"""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            self.log_message.emit("Memuat data kegiatan WR dari database...")
            success, kegiatan_list = self.db_manager.get_kegiatan_wr_list()

            if success:
                self.kegiatan_data = kegiatan_list
                self.update_user_filter()
                self.filter_kegiatan()
                self.log_message.emit(f"Data kegiatan WR berhasil dimuat: {len(self.kegiatan_data)} kegiatan")
            else:
                self.log_message.emit(f"Gagal memuat data kegiatan WR: {kegiatan_list}")
                self.kegiatan_data = []
                self.populate_table([])

        except Exception as e:
            self.log_message.emit(f"Error loading kegiatan WR data: {str(e)}")
            self.kegiatan_data = []
            self.populate_table([])

    def update_user_filter(self):
        """Update user filter dropdown with unique users"""
        current_text = self.user_filter.currentText()
        self.user_filter.clear()
        self.user_filter.addItem("Semua User")

        # Get unique users
        users = set()
        for kegiatan in self.kegiatan_data:
            user = kegiatan.get('dibuat_oleh', '')
            if user:
                users.add(user)

        # Add users to filter
        for user in sorted(users):
            self.user_filter.addItem(user)

        # Restore previous selection if it exists
        index = self.user_filter.findText(current_text)
        if index >= 0:
            self.user_filter.setCurrentIndex(index)

    def filter_kegiatan(self):
        """Filter kegiatan based on user and category"""
        user_filter = self.user_filter.currentText()
        category_filter = self.category_filter.currentText()

        filtered_kegiatan = []

        for kegiatan in self.kegiatan_data:
            # User filter
            if user_filter != "Semua User":
                if kegiatan.get('dibuat_oleh', '') != user_filter:
                    continue

            # Category filter
            if category_filter != "Semua":
                if kegiatan.get('kategori', '') != category_filter:
                    continue

            filtered_kegiatan.append(kegiatan)

        self.populate_table(filtered_kegiatan)


    def populate_table(self, kegiatan_list):
        """Populate table with kegiatan data - sesuai struktur database yang sebenarnya"""
        self.kegiatan_table.setRowCount(0)

        for row_idx, kegiatan in enumerate(kegiatan_list):
            self.kegiatan_table.insertRow(row_idx)

            # Column 0: Kategori (database field: kategori)
            kategori_item = QTableWidgetItem(kegiatan.get('kategori', 'N/A'))

            # Column 1: Nama Kegiatan (database field: nama_kegiatan)
            nama = kegiatan.get('nama_kegiatan', 'N/A')
            nama_item = QTableWidgetItem(nama)

            # Column 2: Keterangan (database field: keterangan only)
            keterangan = kegiatan.get('keterangan', '')
            keterangan_item = QTableWidgetItem(str(keterangan))

            # Column 3: Lokasi (database field: lokasi - renamed from tempat_kegiatan)
            lokasi = kegiatan.get('lokasi', 'N/A')
            lokasi_item = QTableWidgetItem(str(lokasi))

            # Column 4: Tanggal Kegiatan (database field: tanggal_pelaksanaan)
            tanggal_mulai = kegiatan.get('tanggal_pelaksanaan', 'N/A')
            try:
                if tanggal_mulai and tanggal_mulai != 'N/A':
                    if isinstance(tanggal_mulai, str):
                        # Handle ISO format dengan 'T'
                        if 'T' in tanggal_mulai:
                            date_obj = datetime.datetime.fromisoformat(tanggal_mulai.replace('Z', '+00:00')).date()
                        else:
                            date_obj = datetime.datetime.strptime(tanggal_mulai.split(' ')[0], '%Y-%m-%d').date()
                    else:
                        date_obj = tanggal_mulai
                    formatted_date = date_obj.strftime('%d/%m/%Y')
                else:
                    formatted_date = 'N/A'
            except Exception as e:
                formatted_date = str(tanggal_mulai)
            tanggal_item = QTableWidgetItem(formatted_date)

            # Column 5: Waktu Kegiatan (database field: waktu_mulai)
            waktu_mulai = kegiatan.get('waktu_mulai', 'N/A')
            if waktu_mulai and waktu_mulai != 'N/A':
                try:
                    if isinstance(waktu_mulai, str) and len(waktu_mulai) > 5:
                        waktu_mulai = waktu_mulai[:5]
                except:
                    pass
            waktu_item = QTableWidgetItem(str(waktu_mulai))

            # Column 6: Biaya (database field: biaya)
            biaya = kegiatan.get('biaya', '')
            if biaya and biaya != '':
                try:
                    amount = float(str(biaya).replace(',', '').replace('.', ''))
                    biaya_formatted = f"Rp {amount:,.0f}".replace(',', '.')
                except:
                    biaya_formatted = str(biaya)
            else:
                biaya_formatted = '-'
            biaya_item = QTableWidgetItem(biaya_formatted)

            # Column 7: Penanggung Jawab (database field: penanggung_jawab)
            penanggung_jawab = kegiatan.get('penanggung_jawab', 'N/A')
            penanggung_jawab_item = QTableWidgetItem(str(penanggung_jawab))

            # Column 8: Status (database field: status)
            status = kegiatan.get('status', 'Direncanakan')
            status_item = QTableWidgetItem(str(status))

            # Color code status berdasarkan status database
            if status == "Direncanakan":
                status_item.setBackground(QBrush(QColor("#3498db")))
                status_item.setForeground(QBrush(QColor("white")))
            elif status == "Berlangsung":
                status_item.setBackground(QBrush(QColor("#f39c12")))
                status_item.setForeground(QBrush(QColor("white")))
            elif status == "Selesai":
                status_item.setBackground(QBrush(QColor("#2ecc71")))
                status_item.setForeground(QBrush(QColor("white")))
            elif status == "Dibatalkan":
                status_item.setBackground(QBrush(QColor("#e74c3c")))
                status_item.setForeground(QBrush(QColor("white")))
            else:
                status_item.setForeground(QBrush(QColor(0, 0, 0)))  # Black text

            # Store kegiatan data in first column
            kategori_item.setData(Qt.UserRole, kegiatan)

            # Set items in table - kolom sesuai database yang sebenarnya
            self.kegiatan_table.setItem(row_idx, 0, kategori_item)
            self.kegiatan_table.setItem(row_idx, 1, nama_item)
            self.kegiatan_table.setItem(row_idx, 2, keterangan_item)
            self.kegiatan_table.setItem(row_idx, 3, lokasi_item)
            self.kegiatan_table.setItem(row_idx, 4, tanggal_item)
            self.kegiatan_table.setItem(row_idx, 5, waktu_item)
            self.kegiatan_table.setItem(row_idx, 6, biaya_item)
            self.kegiatan_table.setItem(row_idx, 7, penanggung_jawab_item)
            self.kegiatan_table.setItem(row_idx, 8, status_item)

        # Select first row if available
        if kegiatan_list and self.kegiatan_table.rowCount() > 0:
            self.kegiatan_table.selectRow(0)

    def get_kegiatan_status(self, kegiatan):
        """Determine status of kegiatan based on status field or date (database field: status)"""
        # First, check if there's a status field from database
        status_db = kegiatan.get('status', '')
        if status_db:
            return status_db

        # Otherwise, calculate based on tanggal_pelaksanaan
        try:
            today = datetime.date.today()
            # Use database field name: tanggal_pelaksanaan
            tanggal_str = kegiatan.get('tanggal_pelaksanaan', '')

            if not tanggal_str:
                return "Unknown"

            # Handle both string and date object
            if isinstance(tanggal_str, str):
                # Handle ISO format
                if 'T' in tanggal_str:
                    kegiatan_date = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00')).date()
                else:
                    kegiatan_date = datetime.datetime.strptime(tanggal_str.split(' ')[0], '%Y-%m-%d').date()
            else:
                kegiatan_date = tanggal_str

            if kegiatan_date > today:
                return "Direncanakan"
            elif kegiatan_date == today:
                return "Berlangsung"
            else:
                return "Selesai"
        except:
            return "Unknown"

    def view_kegiatan(self):
        """View selected kegiatan details"""
        current_row = self.kegiatan_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih kegiatan yang akan dilihat")
            return

        nama_item = self.kegiatan_table.item(current_row, 0)
        if not nama_item or not nama_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Warning", "Data kegiatan tidak valid")
            return

        kegiatan = nama_item.data(Qt.UserRole)

        # Create detail dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Detail Kegiatan Paroki")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        detail_text = QTextEdit()
        detail_text.setReadOnly(True)

        # Use kegiatan_wr field names (aligned with database schema)
        tanggal = kegiatan.get('tanggal_pelaksanaan', 'N/A')
        waktu_kegiatan = kegiatan.get('waktu_mulai', 'N/A')
        lokasi = kegiatan.get('lokasi', 'N/A')
        biaya = kegiatan.get('biaya', 'N/A')
        keterangan = kegiatan.get('keterangan', 'Tidak ada keterangan')

        detail_html = f"""
        <h2 style="color: #9b59b6;">{kegiatan.get('nama_kegiatan', 'N/A')}</h2>
        <hr>
        <p><strong>Kategori:</strong> {kegiatan.get('kategori', 'N/A')}</p>
        <p><strong>Tanggal Kegiatan:</strong> {tanggal}</p>
        <p><strong>Waktu Kegiatan:</strong> {waktu_kegiatan}</p>
        <p><strong>Lokasi:</strong> {lokasi}</p>
        <p><strong>Biaya:</strong> {biaya}</p>
        <p><strong>Penanggung Jawab:</strong> {kegiatan.get('penanggung_jawab', 'N/A')}</p>
        <p><strong>Status:</strong> {self.get_kegiatan_status(kegiatan)}</p>
        <hr>
        <p><strong>Keterangan:</strong></p>
        <p>{keterangan}</p>
        """

        detail_text.setHtml(detail_html)
        layout.addWidget(detail_text)

        close_button = QPushButton("Tutup")
        close_button.clicked.connect(dialog.accept)  # type: ignore
        layout.addWidget(close_button)

        dialog.exec_()

    def export_kegiatan(self):
        """Export kegiatan WR to CSV"""
        if self.kegiatan_table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Tidak ada data kegiatan untuk diekspor.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Kegiatan WR", "kegiatan_wr.csv", "CSV Files (*.csv)"
        )
        if not filename:
            return

        import csv
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Kategori", "Nama Kegiatan", "Keterangan", "Lokasi",
                    "Tanggal Kegiatan", "Waktu Kegiatan", "Biaya", "Penanggung Jawab", "Status"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in range(self.kegiatan_table.rowCount()):
                    kategori_item = self.kegiatan_table.item(row, 0)
                    if kategori_item and kategori_item.data(Qt.UserRole):
                        kegiatan = kategori_item.data(Qt.UserRole)
                        # Use kegiatan_wr field names (aligned with database schema)
                        tanggal = kegiatan.get('tanggal_pelaksanaan', '')
                        waktu = kegiatan.get('waktu_mulai', '')
                        lokasi = kegiatan.get('lokasi', '')
                        biaya = kegiatan.get('biaya', '')
                        penanggung_jawab = kegiatan.get('penanggung_jawab', '')

                        writer.writerow({
                            "Kategori": kegiatan.get('kategori', ''),
                            "Nama Kegiatan": kegiatan.get('nama_kegiatan', ''),
                            "Keterangan": kegiatan.get('keterangan', ''),
                            "Lokasi": lokasi,
                            "Tanggal Kegiatan": tanggal,
                            "Waktu Kegiatan": waktu,
                            "Biaya": biaya,
                            "Penanggung Jawab": penanggung_jawab,
                            "Status": self.get_kegiatan_status(kegiatan)
                        })

            QMessageBox.information(self, "Sukses", f"Data kegiatan WR berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data kegiatan WR diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
            self.log_message.emit(f"Gagal mengekspor data: {str(e)}")

    def get_data(self):
        """Get kegiatan data for other components"""
        return self.kegiatan_data
