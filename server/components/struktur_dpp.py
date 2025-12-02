# Path: server/components/struktur_dpp.py
# DPP (Dewan Pengurus Paroki) Tab Component

import csv
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QFrame, QMessageBox, QDialog,
                            QFileDialog, QScrollArea, QMenu)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor

from .struktur_base import BaseStrukturComponent, WordWrapHeaderView


class StrukturDPPComponent(BaseStrukturComponent):
    """Komponen untuk tab DPP (Dewan Pengurus Paroki)"""

    data_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.struktur_data = []
        self.all_struktur_data = []
        self.church_label = None
        self.church_name_label = None
        self.total_pengurus_label = None
        self.struktur_table = None
        self.search_input = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI untuk tab DPP"""
        layout = QVBoxLayout(self)

        # Header dengan buttons dan search
        header = self.create_header()
        layout.addWidget(header)

        # Header Periode Pengurus
        periode_header = self.create_periode_header()
        layout.addWidget(periode_header)

        # Table view untuk daftar pengurus
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

        self.struktur_table = self.create_table_view()
        table_layout.addWidget(self.struktur_table)

        layout.addWidget(table_container)

        # Tombol aksi
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)

    def create_header(self):
        """Buat header dengan kontrol pencarian dan tombol tambah"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 10, 0)

        # Search functionality
        header_layout.addWidget(QLabel("Cari:"))

        self.search_input = self.create_search_input()
        self.search_input.textChanged.connect(self.filter_data)
        header_layout.addWidget(self.search_input)

        # Tombol Refresh
        refresh_button = self.create_button("Refresh", "#3498db", self.refresh_data, "server/assets/refresh.png")
        header_layout.addWidget(refresh_button)

        header_layout.addStretch()

        add_button = self.create_button("Tambah Pengurus", "#27ae60", self.add_struktur, "server/assets/tambah.png")
        header_layout.addWidget(add_button)

        return header

    def create_search_input(self):
        """Buat search input dengan styling"""
        from PyQt5.QtWidgets import QLineEdit
        search_input = QLineEdit()
        search_input.setPlaceholderText("Cari pengurus...")
        search_input.setFixedWidth(300)
        return search_input

    def create_periode_header(self):
        """Buat header periode pengurus dengan proper sizing"""
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

        # Judul gereja - line 1 (DPP Header)
        self.church_label = QLabel("Pengurus Dewan Pastoral Paroki")
        self.church_label.setAlignment(Qt.AlignCenter)
        font1 = QFont("Arial", 18, QFont.Bold)
        self.church_label.setFont(font1)
        self.church_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """)
        self.church_label.setMinimumHeight(28)
        self.church_label.setWordWrap(False)
        header_layout.addWidget(self.church_label, 0, Qt.AlignCenter)

        # Nama gereja - line 2 (Church name - Sub judul)
        self.church_name_label = QLabel("Santa Maria Ratu Damai, Uluindano")
        self.church_name_label.setAlignment(Qt.AlignCenter)
        font2 = QFont("Arial", 12, QFont.Normal)
        self.church_name_label.setFont(font2)
        self.church_name_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """)
        self.church_name_label.setMinimumHeight(22)
        self.church_name_label.setWordWrap(False)
        header_layout.addWidget(self.church_name_label, 0, Qt.AlignCenter)

        # Info total pengurus
        self.total_pengurus_label = QLabel("Total: 0 pengurus (0 aktif)")
        self.total_pengurus_label.setAlignment(Qt.AlignCenter)
        font3 = QFont("Arial", 11, QFont.Normal)
        self.total_pengurus_label.setFont(font3)
        self.total_pengurus_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                background-color: transparent;
                border: none;
                padding: 2px;
            }
        """)
        self.total_pengurus_label.setMinimumHeight(18)
        header_layout.addWidget(self.total_pengurus_label, 0, Qt.AlignCenter)

        return header_frame

    def create_table_view(self):
        """Buat tampilan tabel dengan style profesional"""
        table = QTableWidget(0, 9)

        # Set custom header with word wrap and center alignment
        custom_header = WordWrapHeaderView(Qt.Horizontal, table)
        table.setHorizontalHeader(custom_header)

        table.setHorizontalHeaderLabels([
            "Foto", "Nama Lengkap", "Jenis Kelamin", "Jabatan", "Wilayah Rohani", "Status", "Email", "Telepon", "Periode"
        ])

        # Apply professional table styling
        self.apply_professional_table_style(table)

        # Excel-like column resizing - all columns can be resized
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # Set initial column widths
        table.setColumnWidth(0, 80)   # Foto
        table.setColumnWidth(1, 200)  # Nama Lengkap
        table.setColumnWidth(2, 120)  # Jenis Kelamin
        table.setColumnWidth(3, 180)  # Jabatan
        table.setColumnWidth(4, 180)  # Wilayah Rohani
        table.setColumnWidth(5, 100)  # Status
        table.setColumnWidth(6, 200)  # Email
        table.setColumnWidth(7, 120)  # Telepon
        table.setColumnWidth(8, 120)  # Periode

        # Update header height when column is resized
        header.sectionResized.connect(self.update_header_height)

        # Enable context menu
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu_table)

        # Initial header height calculation (delayed to ensure proper rendering)
        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

        return table

    def update_header_height(self, logicalIndex, oldSize, newSize):
        """Update header height when column is resized"""
        if hasattr(self, 'struktur_table') and self.struktur_table:
            header = self.struktur_table.horizontalHeader()
            # Force header to recalculate height
            header.setMinimumHeight(25)
            max_height = 25

            # Calculate required height for each section
            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            # Set header height to accommodate tallest section
            header.setFixedHeight(max_height)

    def create_action_buttons(self):
        """Buat tombol-tombol aksi"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        edit_button = self.create_button("Edit Terpilih", "#f39c12", self.edit_struktur, "server/assets/edit.png")
        action_layout.addWidget(edit_button)

        delete_button = self.create_button("Hapus Terpilih", "#c0392b", self.delete_struktur, "server/assets/hapus.png")
        action_layout.addWidget(delete_button)

        export_button = self.create_button("Export Data", "#16a085", self.export_data, "server/assets/export.png")
        action_layout.addWidget(export_button)

        return action_layout

    def show_context_menu_table(self, position):
        """Tampilkan context menu untuk table view"""
        if self.struktur_table.rowCount() == 0:
            return

        menu = QMenu()

        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")

        action = menu.exec_(self.struktur_table.mapToGlobal(position))

        if action == edit_action:
            self.edit_struktur()
        elif action == delete_action:
            self.delete_struktur()

    def load_data(self):
        """Load data struktur dari database"""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            if not hasattr(self.db_manager, 'get_struktur_list'):
                self.log_message.emit("Error: Database manager tidak memiliki method get_struktur_list")
                return

            self.log_message.emit("Mencoba memuat data struktur DPP...")
            success, struktur = self.db_manager.get_struktur_list(search=None)

            if success:
                if isinstance(struktur, dict) and 'data' in struktur:
                    data_list = struktur['data'] if struktur['data'] is not None else []
                elif isinstance(struktur, list):
                    data_list = struktur
                else:
                    data_list = []

                self.all_struktur_data = data_list.copy()
                self.struktur_data = data_list

                self.populate_views()
                self.log_message.emit(f"Data struktur DPP berhasil dimuat: {len(self.struktur_data)} record")
            else:
                self.all_struktur_data = []
                self.struktur_data = []
                self.populate_views()
                self.log_message.emit(f"Gagal memuat data struktur DPP: {struktur}")

            self.log_message.emit("Proses loading data struktur DPP selesai")
            self.data_updated.emit()
        except Exception as e:
            self.log_message.emit(f"Exception saat memuat data struktur DPP: {str(e)}")
            self.all_struktur_data = []
            self.struktur_data = []
            self.populate_views()

    def populate_views(self):
        """Populate table view dengan data struktur"""
        self.populate_table_view()
        self.update_total_pengurus()

    def populate_table_view(self):
        """Populate table view dengan data sesuai dengan field input dialog"""
        self.struktur_table.setRowCount(0)

        if not self.struktur_data:
            return

        for row_data in self.struktur_data:
            row_pos = self.struktur_table.rowCount()
            self.struktur_table.insertRow(row_pos)

            # Column 0: Foto - Load asynchronously
            foto_path = row_data.get('foto_path', '')
            foto_item = self.load_image_async('struktur', row_pos, 0, foto_path)
            self.struktur_table.setItem(row_pos, 0, foto_item)

            # Column 1: Nama Lengkap
            nama_lengkap = row_data.get('nama_lengkap', '')
            nama_item = QTableWidgetItem(nama_lengkap)
            self.struktur_table.setItem(row_pos, 1, nama_item)

            # Column 2: Jenis Kelamin
            jenis_kelamin = row_data.get('jenis_kelamin', '')
            jk_item = QTableWidgetItem(jenis_kelamin if jenis_kelamin else "-")
            jk_item.setTextAlignment(Qt.AlignCenter)
            self.struktur_table.setItem(row_pos, 2, jk_item)

            # Column 3: Jabatan
            jabatan = row_data.get('jabatan_utama', '')
            jabatan_item = QTableWidgetItem(jabatan)
            self.struktur_table.setItem(row_pos, 3, jabatan_item)

            # Column 4: Wilayah Rohani
            wilayah_rohani = row_data.get('wilayah_rohani', '')
            wilayah_item = QTableWidgetItem(wilayah_rohani)
            self.struktur_table.setItem(row_pos, 4, wilayah_item)

            # Column 5: Status
            status_aktif = row_data.get('status_aktif', '')
            status_item = QTableWidgetItem(status_aktif)

            if status_aktif == "Aktif":
                status_item.setBackground(Qt.green)
                status_item.setText("🟢 Aktif")
            elif status_aktif == "Tidak Aktif":
                status_item.setBackground(Qt.lightGray)
                status_item.setText("🔴 Tidak Aktif")
            elif status_aktif == "Cuti":
                status_item.setBackground(Qt.yellow)
                status_item.setText("🟡 Cuti")

            self.struktur_table.setItem(row_pos, 5, status_item)

            # Column 6: Email
            email = row_data.get('email', '')
            email_item = QTableWidgetItem(email if email else "-")
            self.struktur_table.setItem(row_pos, 6, email_item)

            # Column 7: Telepon
            telepon = row_data.get('telepon', '')
            telepon_item = QTableWidgetItem(telepon if telepon else "-")
            self.struktur_table.setItem(row_pos, 7, telepon_item)

            # Column 8: Periode
            periode = row_data.get('periode', '')
            periode_item = QTableWidgetItem(periode if periode else "-")
            periode_item.setTextAlignment(Qt.AlignCenter)
            self.struktur_table.setItem(row_pos, 8, periode_item)

    def update_total_pengurus(self):
        """Update label total pengurus"""
        if not self.struktur_data:
            self.total_pengurus_label.setText("Total: 0 pengurus (0 aktif)")
            return

        total = len(self.struktur_data)
        aktif = len([data for data in self.struktur_data if data.get('status_aktif', '') == 'Aktif'])
        self.total_pengurus_label.setText(f"Total: {total} pengurus ({aktif} aktif)")

    def filter_data(self):
        """Filter data pengurus berdasarkan keyword pencarian (real-time search)"""
        search_text = self.search_input.text().lower().strip()

        if not search_text:
            if hasattr(self, 'all_struktur_data') and self.all_struktur_data:
                self.struktur_data = self.all_struktur_data.copy()
            self.populate_views()
            return

        if not hasattr(self, 'all_struktur_data') or not self.all_struktur_data:
            self.all_struktur_data = self.struktur_data.copy() if self.struktur_data else []

        filtered_data = []

        for data in self.all_struktur_data:
            nama_lengkap = (data.get('nama_lengkap') or '').lower()
            jabatan = (data.get('jabatan_utama') or '').lower()
            wilayah = (data.get('wilayah_rohani') or '').lower()
            email = (data.get('email') or '').lower()
            telepon = (data.get('telepon') or '').lower()
            periode = (data.get('periode') or '').lower()
            jenis_kelamin = (data.get('jenis_kelamin') or '').lower()
            status_aktif = (data.get('status_aktif') or '').lower()

            if (search_text in nama_lengkap or
                search_text in jabatan or
                search_text in wilayah or
                search_text in email or
                search_text in telepon or
                search_text in periode or
                search_text in jenis_kelamin or
                search_text in status_aktif):
                filtered_data.append(data)

        self.struktur_data = filtered_data
        self.populate_views()

    def refresh_data(self):
        """Refresh data dari database"""
        self.search_input.clear()

        if hasattr(self, 'all_struktur_data'):
            self.all_struktur_data = []

        self.load_data()
        self.log_message.emit("Data struktur DPP berhasil di-refresh")

    def add_struktur(self):
        """Tambah pengurus baru"""
        from .dialogs import StrukturDialog
        dialog = StrukturDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            if not data['nama_lengkap']:
                QMessageBox.warning(self, "Error", "Nama lengkap harus diisi")
                return

            if not data['jabatan_utama']:
                QMessageBox.warning(self, "Error", "Jabatan utama harus diisi")
                return

            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            if not hasattr(self.db_manager, 'add_struktur'):
                QMessageBox.critical(self, "Error", "Method add_struktur tidak tersedia di database manager")
                self.log_message.emit("Method add_struktur tidak tersedia")
                return

            self.log_message.emit("Mencoba menambahkan pengurus DPP...")
            success, result = self.db_manager.add_struktur(data)
            if success:
                QMessageBox.information(self, "Sukses", "Pengurus berhasil ditambahkan.")
                self.load_data()
                self.log_message.emit("Pengurus DPP berhasil ditambahkan")
            else:
                QMessageBox.critical(self, "Error", f"Gagal menambahkan pengurus: {result}")
                self.log_message.emit(f"API Error - Gagal menambahkan pengurus: {result}")

    def edit_struktur(self):
        """Edit pengurus yang dipilih dari tabel"""
        current_row = self.struktur_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengurus yang akan diedit")
            return

        if current_row >= len(self.struktur_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return

        struktur_data = self.struktur_data[current_row]
        self.edit_struktur_dialog(struktur_data)

    def edit_struktur_dialog(self, struktur_data):
        """Buka dialog edit dengan data struktur"""
        from .dialogs import StrukturDialog
        dialog = StrukturDialog(self, struktur_data)
        if dialog.exec_() == dialog.Accepted:
            updated_data = dialog.get_data()

            if not updated_data['nama_lengkap']:
                QMessageBox.warning(self, "Error", "Nama lengkap harus diisi")
                return

            if not updated_data['jabatan_utama']:
                QMessageBox.warning(self, "Error", "Jabatan utama harus diisi")
                return

            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            struktur_id = struktur_data.get('id_struktur')
            if struktur_id and hasattr(self.db_manager, 'update_struktur'):
                success, result = self.db_manager.update_struktur(struktur_id, updated_data)
                if success:
                    QMessageBox.information(self, "Sukses", "Pengurus berhasil diupdate.")
                    self.load_data()
                    self.log_message.emit("Pengurus DPP berhasil diupdate")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal mengupdate pengurus: {result}")
                    self.log_message.emit(f"Error update pengurus: {result}")
            else:
                QMessageBox.critical(self, "Error", "Method update_struktur tidak tersedia")

    def delete_struktur(self):
        """Hapus pengurus yang dipilih dari tabel"""
        current_row = self.struktur_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengurus yang akan dihapus")
            return

        if current_row >= len(self.struktur_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return

        struktur_data = self.struktur_data[current_row]
        self.delete_struktur_confirm(struktur_data)

    def delete_struktur_confirm(self, struktur_data):
        """Konfirmasi hapus pengurus"""
        nama_lengkap = struktur_data.get('nama_lengkap', 'Unknown')
        jabatan = struktur_data.get('jabatan_utama', '')

        reply = QMessageBox.question(self, 'Konfirmasi',
                                    f"Yakin ingin menghapus pengurus '{nama_lengkap}' dengan jabatan '{jabatan}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            struktur_id = struktur_data.get('id_struktur')
            if struktur_id and hasattr(self.db_manager, 'delete_struktur'):
                success, result = self.db_manager.delete_struktur(struktur_id)
                if success:
                    QMessageBox.information(self, "Sukses", "Pengurus berhasil dihapus.")
                    self.load_data()
                    self.log_message.emit("Pengurus DPP berhasil dihapus")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal menghapus pengurus: {result}")
                    self.log_message.emit(f"Error hapus pengurus: {result}")
            else:
                QMessageBox.critical(self, "Error", "Method delete_struktur tidak tersedia")

    def export_data(self):
        """Export data struktur ke file CSV"""
        if not self.struktur_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Data Struktur DPP", "struktur_dpp.csv", "CSV Files (*.csv)")
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Nama Lengkap", "Jenis Kelamin", "Jabatan Utama", "Wilayah Rohani",
                    "Status Aktif", "Email", "Telepon", "Periode", "Foto Path"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in self.struktur_data:
                    writer.writerow({
                        "Nama Lengkap": item.get('nama_lengkap', ''),
                        "Jenis Kelamin": item.get('jenis_kelamin', ''),
                        "Jabatan Utama": item.get('jabatan_utama', ''),
                        "Wilayah Rohani": item.get('wilayah_rohani', ''),
                        "Status Aktif": item.get('status_aktif', ''),
                        "Email": item.get('email', ''),
                        "Telepon": item.get('telepon', ''),
                        "Periode": item.get('periode', ''),
                        "Foto Path": item.get('foto_path', '')
                    })

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data struktur DPP diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
            self.log_message.emit(f"Gagal mengekspor data: {str(e)}")

    def get_data(self):
        """Ambil data struktur untuk komponen lain"""
        return self.struktur_data
