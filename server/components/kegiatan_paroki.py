# Path: server/components/kegiatan_paroki.py
# Kegiatan Paroki (Admin Jadwal Kegiatan) Component

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFileDialog, QGroupBox,
                            QDateEdit, QFormLayout, QAbstractItemView, QFrame, QComboBox)
from PyQt5.QtCore import QObject, pyqtSignal, QDate, QSize, Qt, QRect, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter, QBrush

# Import dialog secara langsung untuk menghindari circular import
from .dialogs import KegiatanDialog

# Import WordWrapHeaderView from proker_base
from .proker_base import WordWrapHeaderView

class ProgramKerjaKegiatanParokiWidget(QWidget):
    """Komponen untuk manajemen jadwal kegiatan"""

    data_updated = pyqtSignal()  # Signal ketika data berubah
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore  # Signal untuk mengirim log message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.kegiatan_data = []
        self.db_manager = None
        self.setup_ui()

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        # Load data segera setelah database manager di-set
        if self.db_manager:
            self.load_data()

    def setup_ui(self):
        """Setup UI untuk halaman jadwal"""
        layout = QVBoxLayout(self)

        # Clean header without background (matching pengaturan style)
        header_frame = QWidget()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 10, 0)

        title_label = QLabel("Kegiatan Pusat Paroki")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header_frame)

        # Original header with buttons
        header = self.create_header()
        layout.addWidget(header)

        # Filter bulan
        filter_group = self.create_month_filter()
        layout.addWidget(filter_group)

        # Table view untuk daftar jadwal with proper container
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

        self.kegiatan_paroki_table = self.create_professional_table()
        table_layout.addWidget(self.kegiatan_paroki_table)

        layout.addWidget(table_container)

        # Tombol aksi
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)

    def create_professional_table(self):
        """Create table with professional styling."""
        table = QTableWidget(0, 9)

        # Set custom header with word wrap and center alignment
        custom_header = WordWrapHeaderView(Qt.Horizontal, table)
        table.setHorizontalHeader(custom_header)

        table.setHorizontalHeaderLabels([
            "Nama Kegiatan", "Sasaran", "Lokasi", "Tanggal",
            "Waktu", "PIC", "Biaya", "Status", "Keterangan"
        ])

        # Apply professional table styling
        self.apply_professional_table_style(table)

        # Set specific column widths
        column_widths = [150, 150, 120, 110, 80, 120, 100, 100, 150]  # Total
        for i, width in enumerate(column_widths):
            table.setColumnWidth(i, width)

        # Set minimum table width to sum of all columns
        table.setMinimumWidth(sum(column_widths) + 50)  # Add padding for scrollbar

        # Update header height when column is resized
        header = table.horizontalHeader()
        header.sectionResized.connect(self.update_header_height)

        # Enable context menu
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu)

        # Initial header height calculation (delayed to ensure proper rendering)
        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

        return table

    def update_header_height(self, logicalIndex, oldSize, newSize):
        """Update header height when column is resized"""
        if hasattr(self, 'kegiatan_paroki_table'):
            header = self.kegiatan_paroki_table.horizontalHeader()
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

    def show_context_menu(self, position):
        """Tampilkan context menu untuk edit/hapus"""
        if self.kegiatan_paroki_table.rowCount() == 0:
            return

        from PyQt5.QtWidgets import QMenu
        menu = QMenu()

        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")

        action = menu.exec_(self.kegiatan_paroki_table.mapToGlobal(position))

        if action == edit_action:
            self.edit_kegiatan()
        elif action == delete_action:
            self.delete_kegiatan()

    def create_header(self):
        """Buat header dengan kontrol (tanpa title karena sudah ada di header frame)"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 10, 0)  # Add right margin for spacing

        header_layout.addStretch()

        add_button = self.create_button("Tambah Kegiatan", "#27ae60", self.add_kegiatan, "server/assets/tambah.png")
        header_layout.addWidget(add_button)

        return header

    def create_month_filter(self):
        """Buat filter bulan dan kategori (matching Kegiatan WR)"""
        filter_group = QGroupBox()  # Remove title like program_kerja.py
        filter_layout = QHBoxLayout(filter_group)

        # Filter Bulan
        month_label = QLabel("Filter Bulan:")
        filter_layout.addWidget(month_label)

        self.month_filter = QComboBox()
        self.populate_month_filter()
        self.month_filter.currentTextChanged.connect(self.filter_kegiatan)
        filter_layout.addWidget(self.month_filter)

        # Filter Kategori - sesuai database schema
        category_label = QLabel("Kategori:")
        filter_layout.addWidget(category_label)

        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "Semua", "Misa", "Doa", "Sosial", "Pendidikan", "Ibadah", "Katekese", "Rohani", "Administratif", "Lainnya"
        ])
        self.category_filter.currentTextChanged.connect(self.filter_kegiatan)
        filter_layout.addWidget(self.category_filter)

        filter_layout.addStretch()

        return filter_group

    def populate_month_filter(self):
        """Populate month filter with all months"""
        months = [
            "Semua Bulan",
            "Januari", "Februari", "Maret", "April",
            "Mei", "Juni", "Juli", "Agustus",
            "September", "Oktober", "November", "Desember"
        ]
        self.month_filter.addItems(months)

    def create_action_buttons(self):
        """Buat tombol-tombol aksi"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        edit_button = self.create_button("Edit", "#f39c12", self.edit_kegiatan, "server/assets/edit.png")
        action_layout.addWidget(edit_button)

        delete_button = self.create_button("Hapus", "#c0392b", self.delete_kegiatan, "server/assets/hapus.png")
        action_layout.addWidget(delete_button)

        export_button = self.create_button(".CSV", "#16a085", self.export_kegiatan, "server/assets/export.png")
        action_layout.addWidget(export_button)

        return action_layout

    def create_button(self, text, color, slot, icon_path=None):
        """Buat button dengan style konsisten dan optional icon matching sidebar menu buttons"""
        button = QPushButton(text)

        # Add icon if specified and path exists
        if icon_path:
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(20, 20))  # Standard icon size matching other sidebar components
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
        """Buat warna lebih gelap untuk hover effect matching pengaturan style"""
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

    def load_data(self):
        """Load data kegiatan dari database"""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            self.log_message.emit("Memuat data kegiatan...")

            # Panggil API tanpa filter tanggal dulu untuk memastikan semua data tampil
            success, result = self.db_manager.get_kegiatan_list(limit=1000)

            if success:
                # Cek apakah result adalah list atau dict dengan data
                if isinstance(result, dict) and 'data' in result:
                    self.kegiatan_data = result['data']
                elif isinstance(result, list):
                    self.kegiatan_data = result
                else:
                    self.kegiatan_data = []

                self.log_message.emit(f"Data kegiatan berhasil dimuat: {len(self.kegiatan_data)} record")

                # Reset filter data backup
                if hasattr(self, 'original_kegiatan_data'):
                    delattr(self, 'original_kegiatan_data')

                # Debug: print beberapa data untuk memastikan
                if self.kegiatan_data:
                    first_item = self.kegiatan_data[0]
                    self.log_message.emit(f"Sample data: {first_item.get('nama_kegiatan', 'No Name')}")

                self.populate_table()
                self.data_updated.emit()
            else:
                self.kegiatan_data = []
                self.populate_table()
                self.log_message.emit(f"Error loading kegiatan data: {result}")
                QMessageBox.warning(self, "Error", f"Gagal memuat data kegiatan: {result}")
        except Exception as e:
            self.kegiatan_data = []
            self.populate_table()
            self.log_message.emit(f"Exception loading kegiatan data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error loading kegiatan data: {str(e)}")

    def populate_table(self):
        """Populate tabel dengan data kegiatan sesuai database schema"""
        self.log_message.emit(f"Menampilkan {len(self.kegiatan_data)} kegiatan ke tabel")

        # Clear table first
        self.kegiatan_paroki_table.setRowCount(0)

        if not self.kegiatan_data:
            self.log_message.emit("Tidak ada data kegiatan untuk ditampilkan")
            return

        for row_index, row_data in enumerate(self.kegiatan_data):
            self.kegiatan_paroki_table.insertRow(row_index)

            # Kolom 0: Nama Kegiatan
            nama_kegiatan = str(row_data.get('nama_kegiatan', ''))
            self.kegiatan_paroki_table.setItem(row_index, 0, QTableWidgetItem(nama_kegiatan))

            # Kolom 1: Sasaran Kegiatan (from database field sasaran_kegiatan)
            sasaran = str(row_data.get('sasaran_kegiatan', ''))
            self.kegiatan_paroki_table.setItem(row_index, 1, QTableWidgetItem(sasaran))

            # Kolom 2: Lokasi
            lokasi = str(row_data.get('lokasi', ''))
            self.kegiatan_paroki_table.setItem(row_index, 2, QTableWidgetItem(lokasi))

            # Kolom 3: Tanggal Kegiatan (use tanggal_kegiatan from database)
            tanggal = row_data.get('tanggal_kegiatan')
            tanggal_str = self.format_date(tanggal)
            self.kegiatan_paroki_table.setItem(row_index, 3, QTableWidgetItem(tanggal_str))

            # Kolom 4: Waktu Kegiatan (use waktu_kegiatan from database)
            waktu = str(row_data.get('waktu_kegiatan', ''))
            if waktu and waktu != 'None' and len(waktu) > 5:
                waktu = waktu[:5]
            self.kegiatan_paroki_table.setItem(row_index, 4, QTableWidgetItem(waktu))

            # Kolom 5: PIC (Penanggung Jawab)
            pic = str(row_data.get('penanggung_jawab', ''))
            self.kegiatan_paroki_table.setItem(row_index, 5, QTableWidgetItem(pic))

            # Kolom 6: Biaya
            biaya = row_data.get('biaya', '')
            if biaya and biaya != '' and biaya != 0:
                try:
                    amount = float(str(biaya).replace(',', '').replace('.', ''))
                    biaya_formatted = f"Rp {amount:,.0f}".replace(',', '.')
                except:
                    biaya_formatted = str(biaya)
            else:
                biaya_formatted = '-'
            biaya_item = QTableWidgetItem(biaya_formatted)
            biaya_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.kegiatan_paroki_table.setItem(row_index, 6, biaya_item)

            # Kolom 7: Status - Center aligned, no styling (normal text style)
            status = str(row_data.get('status', 'Direncanakan'))
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.kegiatan_paroki_table.setItem(row_index, 7, status_item)

            # Kolom 8: Keterangan
            keterangan = str(row_data.get('keterangan', ''))
            self.kegiatan_paroki_table.setItem(row_index, 8, QTableWidgetItem(keterangan))

        self.log_message.emit(f"Selesai menampilkan {self.kegiatan_paroki_table.rowCount()} kegiatan")

    def format_date(self, date_value):
        """Format tanggal untuk ditampilkan"""
        if not date_value:
            return ''

        try:
            if hasattr(date_value, 'strftime'):
                return date_value.strftime('%d/%m/%Y')
            elif isinstance(date_value, str):
                # Coba parse berbagai format tanggal
                import datetime
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']:
                    try:
                        parsed_date = datetime.datetime.strptime(date_value, fmt)
                        return parsed_date.strftime('%d/%m/%Y')
                    except ValueError:
                        continue
                # Jika gagal parse, return string asli
                return str(date_value)
            else:
                return str(date_value)
        except Exception as e:
            self.log_message.emit(f"Error formatting date {date_value}: {str(e)}")
            return str(date_value) if date_value else ''

    def filter_kegiatan(self):
        """Filter kegiatan berdasarkan bulan dan kategori"""
        if not hasattr(self, 'original_kegiatan_data'):
            # Backup data asli saat pertama kali filter
            self.original_kegiatan_data = self.kegiatan_data.copy()

        month_filter = self.month_filter.currentText()
        category_filter = self.category_filter.currentText()

        # Start dengan semua data
        filtered_data = self.original_kegiatan_data.copy()

        # Filter berdasarkan bulan - gunakan tanggal_kegiatan dari database
        if month_filter != "Semua Bulan":
            temp_filtered = []
            for item in filtered_data:
                tanggal = item.get('tanggal_kegiatan')
                if tanggal:
                    try:
                        if isinstance(tanggal, str):
                            import datetime
                            item_date = datetime.datetime.strptime(tanggal, '%Y-%m-%d')
                        elif hasattr(tanggal, 'date'):
                            item_date = tanggal
                        else:
                            continue

                        # Map Indonesian month names
                        month_names = {
                            1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
                            5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
                            9: "September", 10: "Oktober", 11: "November", 12: "Desember"
                        }
                        item_month_name = month_names.get(item_date.month, "")

                        if item_month_name == month_filter:
                            temp_filtered.append(item)
                    except:
                        # Jika error parsing tanggal, skip item ini
                        continue
            filtered_data = temp_filtered

        # Filter berdasarkan kategori
        if category_filter != "Semua":
            temp_filtered = []
            for item in filtered_data:
                kategori = item.get('kategori', '')
                if kategori == category_filter:
                    temp_filtered.append(item)
            filtered_data = temp_filtered

        self.kegiatan_data = filtered_data

        self.populate_table()
        self.log_message.emit(f"Filter diterapkan: {len(self.kegiatan_data)} kegiatan ditampilkan")

    def add_kegiatan(self):
        """Tambah kegiatan baru"""
        dialog = KegiatanDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            # Validasi
            if not data['nama_kegiatan']:
                QMessageBox.warning(self, "Error", "Nama kegiatan harus diisi")
                return

            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            try:
                success, result = self.db_manager.add_kegiatan(data)

                if success:
                    QMessageBox.information(self, "Sukses", "Data kegiatan berhasil ditambahkan")
                    # Reload data setelah menambah
                    self.load_data()
                    self.log_message.emit(f"Kegiatan baru ditambahkan: {data['nama_kegiatan']}")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal menambahkan kegiatan: {result}")
                    self.log_message.emit(f"Error adding kegiatan: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error menambahkan kegiatan: {str(e)}")
                self.log_message.emit(f"Exception adding kegiatan: {str(e)}")

    def edit_kegiatan(self):
        """Edit kegiatan terpilih"""
        current_row = self.kegiatan_paroki_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih kegiatan yang akan diedit")
            return

        if current_row >= len(self.kegiatan_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return

        kegiatan_data = self.kegiatan_data[current_row]

        dialog = KegiatanDialog(self, kegiatan_data)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            # Validasi
            if not data['nama_kegiatan']:
                QMessageBox.warning(self, "Error", "Nama kegiatan harus diisi")
                return

            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            try:
                # Update kegiatan melalui API
                kegiatan_id = kegiatan_data.get('id_kegiatan')
                if not kegiatan_id:
                    QMessageBox.warning(self, "Error", "ID kegiatan tidak ditemukan")
                    return

                success, result = self.db_manager.update_kegiatan(kegiatan_id, data)

                if success:
                    QMessageBox.information(self, "Sukses", "Data kegiatan berhasil diupdate")
                    self.load_data()
                    self.log_message.emit(f"Kegiatan diupdate: {data['nama_kegiatan']}")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal mengupdate kegiatan: {result}")
                    self.log_message.emit(f"Error updating kegiatan: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error mengupdate kegiatan: {str(e)}")
                self.log_message.emit(f"Exception updating kegiatan: {str(e)}")

    def delete_kegiatan(self):
        """Hapus kegiatan terpilih"""
        current_row = self.kegiatan_paroki_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih kegiatan yang akan dihapus")
            return

        if current_row >= len(self.kegiatan_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return

        kegiatan_data = self.kegiatan_data[current_row]
        nama = kegiatan_data.get('nama_kegiatan', 'Unknown')

        reply = QMessageBox.question(self, 'Konfirmasi',
                                    f"Yakin ingin menghapus kegiatan '{nama}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            try:
                kegiatan_id = kegiatan_data.get('id_kegiatan')
                if not kegiatan_id:
                    QMessageBox.warning(self, "Error", "ID kegiatan tidak ditemukan")
                    return

                success, result = self.db_manager.delete_kegiatan(kegiatan_id)

                if success:
                    QMessageBox.information(self, "Sukses", "Data kegiatan berhasil dihapus")
                    self.load_data()
                    self.log_message.emit(f"Kegiatan dihapus: {nama}")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal menghapus kegiatan: {result}")
                    self.log_message.emit(f"Error deleting kegiatan: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error menghapus kegiatan: {str(e)}")
                self.log_message.emit(f"Exception deleting kegiatan: {str(e)}")

    def export_kegiatan(self):
        """Export data kegiatan ke file CSV"""
        if not self.kegiatan_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor")
            return

        try:
            import csv

            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Data Kegiatan", "data_kegiatan.csv", "CSV Files (*.csv)"
            )

            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Nama Kegiatan', 'Deskripsi', 'Lokasi', 'Tanggal Mulai', 'Tanggal Selesai', 'Penanggung Jawab']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for data in self.kegiatan_data:
                        writer.writerow({
                            'Nama Kegiatan': data.get('nama_kegiatan', ''),
                            'Deskripsi': data.get('deskripsi', ''),
                            'Lokasi': data.get('lokasi', ''),
                            'Tanggal Mulai': str(data.get('tanggal_mulai', '')),
                            'Tanggal Selesai': str(data.get('tanggal_selesai', '')),
                            'Penanggung Jawab': data.get('penanggungjawab', '')
                        })

                QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
                self.log_message.emit(f"Data kegiatan diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error export data: {str(e)}")
            self.log_message.emit(f"Exception exporting kegiatan: {str(e)}")

    def get_data(self):
        """Ambil data kegiatan untuk komponen lain"""
        return self.kegiatan_data
