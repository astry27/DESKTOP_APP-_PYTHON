# Path: server/components/struktur_kategorial.py
# K. Kategorial (Komunitas Kategorial) Tab Component

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                            QMessageBox, QFileDialog, QMenu, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
import csv

from .struktur_base import BaseStrukturComponent, WordWrapHeaderView
from .dialogs import KategorialDialog


class StrukturKategorialComponent(BaseStrukturComponent):
    """Komponen untuk tab K. Kategorial (Komunitas Kategorial)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.kategorial_data = []
        self.all_kategorial_data = []
        self.kategorial_search_input = None
        self.kategorial_table = None
        self.total_kategorial_label = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI untuk tab K. Kategorial"""
        layout = QVBoxLayout(self)

        header = self.create_kategorial_header()
        layout.addWidget(header)

        kategorial_header = self.create_kategorial_periode_header()
        layout.addWidget(kategorial_header)

        table_container = QFrame()
        table_container.setStyleSheet("QFrame { border: 1px solid #d0d0d0; background-color: white; margin: 0px; }")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self.kategorial_table = self.create_kategorial_table_view()
        table_layout.addWidget(self.kategorial_table)
        layout.addWidget(table_container)

        action_layout = self.create_kategorial_action_buttons()
        layout.addLayout(action_layout)

    def create_kategorial_header(self):
        """Buat header dengan kontrol pencarian dan tombol tambah untuk K. Kategorial"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 10, 0)

        header_layout.addWidget(QLabel("Cari:"))

        self.kategorial_search_input = QLineEdit()
        self.kategorial_search_input.setPlaceholderText("Cari pengurus kategorial...")
        self.kategorial_search_input.setFixedWidth(300)
        self.kategorial_search_input.textChanged.connect(self.filter_kategorial_data)
        header_layout.addWidget(self.kategorial_search_input)

        refresh_button = self.create_button("Refresh", "#3498db", self.refresh_kategorial_data, "server/assets/refresh.png")
        header_layout.addWidget(refresh_button)

        header_layout.addStretch()

        add_button = self.create_button("Tambah Pengurus", "#27ae60", self.add_kategorial, "server/assets/tambah.png")
        header_layout.addWidget(add_button)

        return header

    def create_kategorial_periode_header(self):
        """Buat header periode untuk K. Kategorial"""
        header_frame = QFrame()
        header_frame.setStyleSheet("QFrame { background-color: white; border: none; margin: 0px; padding: 0px; }")

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 12, 10, 12)
        header_layout.setSpacing(3)

        # Judul gereja - line 1 (K. Kategorial Header) - matching DPP styling
        kategorial_label = QLabel("Pengurus Kelompok Kategorial")
        kategorial_label.setAlignment(Qt.AlignCenter)
        font1 = QFont("Arial", 18, QFont.Bold)
        kategorial_label.setFont(font1)
        kategorial_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """)
        kategorial_label.setMinimumHeight(28)
        kategorial_label.setWordWrap(False)
        header_layout.addWidget(kategorial_label, 0, Qt.AlignCenter)

        # Nama gereja - line 2 (Church name - Sub judul) - matching DPP styling
        church_label = QLabel("Santa Maria Ratu Damai, Uluindano")
        church_label.setAlignment(Qt.AlignCenter)
        font2 = QFont("Arial", 12, QFont.Normal)
        church_label.setFont(font2)
        church_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """)
        church_label.setMinimumHeight(22)
        church_label.setWordWrap(False)
        header_layout.addWidget(church_label, 0, Qt.AlignCenter)

        # Info total pengurus
        self.total_kategorial_label = QLabel("Total: 0 pengurus (0 aktif)")
        self.total_kategorial_label.setAlignment(Qt.AlignCenter)
        font3 = QFont("Arial", 11, QFont.Normal)
        self.total_kategorial_label.setFont(font3)
        self.total_kategorial_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """)
        self.total_kategorial_label.setMinimumHeight(18)
        header_layout.addWidget(self.total_kategorial_label, 0, Qt.AlignCenter)

        return header_frame

    def create_kategorial_table_view(self):
        """Buat tampilan tabel K. Kategorial dengan 11 kolom"""
        table = QTableWidget(0, 11)

        custom_header = WordWrapHeaderView(Qt.Horizontal, table)
        table.setHorizontalHeader(custom_header)

        table.setHorizontalHeaderLabels([
            "Foto", "Kelompok Kategorial", "Nama Lengkap", "Jenis Kelamin", "Jabatan",
            "No. HP", "Email", "Alamat", "Wilayah Rohani", "Masa Jabatan", "Status"
        ])

        self.apply_professional_table_style(table)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        table.setColumnWidth(0, 80)   # Foto
        table.setColumnWidth(1, 150)  # Kelompok Kategorial
        table.setColumnWidth(2, 180)  # Nama Lengkap
        table.setColumnWidth(3, 120)  # Jenis Kelamin
        table.setColumnWidth(4, 150)  # Jabatan
        table.setColumnWidth(5, 120)  # No. HP
        table.setColumnWidth(6, 150)  # Email
        table.setColumnWidth(7, 180)  # Alamat
        table.setColumnWidth(8, 150)  # Wilayah Rohani
        table.setColumnWidth(9, 120)  # Masa Jabatan
        table.setColumnWidth(10, 100) # Status

        header.sectionResized.connect(self.update_kategorial_header_height)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_kategorial_context_menu)

        QTimer.singleShot(100, lambda: self.update_kategorial_header_height(0, 0, 0))

        return table

    def update_kategorial_header_height(self, logicalIndex, oldSize, newSize):
        """Update header height untuk K. Kategorial table"""
        if hasattr(self, 'kategorial_table') and self.kategorial_table:
            header = self.kategorial_table.horizontalHeader()
            header.setMinimumHeight(25)
            max_height = 25
            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())
            header.setFixedHeight(max_height)

    def load_kategorial_data(self):
        """Load data K. Kategorial dari database"""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            if not hasattr(self.db_manager, 'get_kategorial_list'):
                self.log_message.emit("Error: Database manager tidak memiliki method get_kategorial_list")
                return

            self.log_message.emit("Mencoba memuat data komunitas kategorial...")
            success, kategorial = self.db_manager.get_kategorial_list(search=None)

            if success:
                if isinstance(kategorial, dict) and 'data' in kategorial:
                    data_list = kategorial['data'] if kategorial['data'] is not None else []
                elif isinstance(kategorial, list):
                    data_list = kategorial
                else:
                    data_list = []

                self.all_kategorial_data = data_list.copy()
                self.kategorial_data = data_list

                self.populate_kategorial_views()
                self.log_message.emit(f"Data komunitas kategorial berhasil dimuat: {len(self.kategorial_data)} record")
            else:
                self.all_kategorial_data = []
                self.kategorial_data = []
                self.populate_kategorial_views()
                self.log_message.emit(f"Gagal memuat data komunitas kategorial: {kategorial}")

            self.log_message.emit("Proses loading data komunitas kategorial selesai")
        except Exception as e:
            self.log_message.emit(f"Exception saat memuat data komunitas kategorial: {str(e)}")
            self.all_kategorial_data = []
            self.kategorial_data = []
            self.populate_kategorial_views()

    def populate_kategorial_views(self):
        """Populate table view dengan data K. Kategorial"""
        self.populate_kategorial_table_view()
        self.update_total_kategorial()

    def populate_kategorial_table_view(self):
        """Populate table view dengan data K. Kategorial"""
        self.kategorial_table.setRowCount(0)

        if not self.kategorial_data:
            return

        for row_data in self.kategorial_data:
            row_pos = self.kategorial_table.rowCount()
            self.kategorial_table.insertRow(row_pos)

            foto_path = row_data.get('foto_path', '')
            foto_item = self.load_image_async('kategorial', row_pos, 0, foto_path)
            self.kategorial_table.setItem(row_pos, 0, foto_item)

            kelompok = row_data.get('kelompok_kategorial', '')
            if kelompok == 'Lainnya':
                kelompok = row_data.get('kelompok_kategorial_lainnya', 'Lainnya')
            kelompok_item = QTableWidgetItem(kelompok)
            self.kategorial_table.setItem(row_pos, 1, kelompok_item)

            nama_lengkap = row_data.get('nama_lengkap', '')
            nama_item = QTableWidgetItem(nama_lengkap)
            self.kategorial_table.setItem(row_pos, 2, nama_item)

            jenis_kelamin = row_data.get('jenis_kelamin', '')
            jk_item = QTableWidgetItem(jenis_kelamin if jenis_kelamin else "-")
            jk_item.setTextAlignment(Qt.AlignCenter)
            self.kategorial_table.setItem(row_pos, 3, jk_item)

            jabatan = row_data.get('jabatan', '')
            jabatan_item = QTableWidgetItem(jabatan if jabatan else "-")
            self.kategorial_table.setItem(row_pos, 4, jabatan_item)

            no_hp = row_data.get('no_hp', '')
            no_hp_item = QTableWidgetItem(no_hp if no_hp else "-")
            self.kategorial_table.setItem(row_pos, 5, no_hp_item)

            email = row_data.get('email', '')
            email_item = QTableWidgetItem(email if email else "-")
            self.kategorial_table.setItem(row_pos, 6, email_item)

            alamat = row_data.get('alamat', '')
            alamat_item = QTableWidgetItem(alamat if alamat else "-")
            self.kategorial_table.setItem(row_pos, 7, alamat_item)

            wilayah_rohani = row_data.get('wilayah_rohani', '')
            wilayah_item = QTableWidgetItem(wilayah_rohani if wilayah_rohani else "-")
            self.kategorial_table.setItem(row_pos, 8, wilayah_item)

            masa_jabatan = row_data.get('masa_jabatan', '')
            masa_jabatan_item = QTableWidgetItem(masa_jabatan if masa_jabatan else "-")
            self.kategorial_table.setItem(row_pos, 9, masa_jabatan_item)

            status = row_data.get('status', '')
            status_item = QTableWidgetItem(status)

            if status == "Aktif":
                status_item.setBackground(Qt.green)
                status_item.setText("[OK] Aktif")
            elif status == "Tidak Aktif":
                status_item.setBackground(Qt.lightGray)
                status_item.setText("[X] Tidak Aktif")
            else:
                status_item.setText(status if status else "-")

            self.kategorial_table.setItem(row_pos, 10, status_item)

    def update_total_kategorial(self):
        """Update label total pengurus K. Kategorial"""
        if not self.kategorial_data:
            self.total_kategorial_label.setText("Total: 0 pengurus (0 aktif)")
            return

        total = len(self.kategorial_data)
        aktif = len([data for data in self.kategorial_data if data.get('status', '') == 'Aktif'])
        self.total_kategorial_label.setText(f"Total: {total} pengurus ({aktif} aktif)")

    def filter_kategorial_data(self):
        """Filter data K. Kategorial berdasarkan keyword pencarian"""
        search_text = self.kategorial_search_input.text().lower().strip()

        if not search_text:
            if hasattr(self, 'all_kategorial_data') and self.all_kategorial_data:
                self.kategorial_data = self.all_kategorial_data.copy()
            self.populate_kategorial_views()
            return

        if not hasattr(self, 'all_kategorial_data') or not self.all_kategorial_data:
            self.all_kategorial_data = self.kategorial_data.copy() if self.kategorial_data else []

        filtered_data = []

        for data in self.all_kategorial_data:
            nama_lengkap = (data.get('nama_lengkap') or '').lower()
            jabatan = (data.get('jabatan') or '').lower()
            kelompok = (data.get('kelompok_kategorial') or '').lower()
            email = (data.get('email') or '').lower()
            no_hp = (data.get('no_hp') or '').lower()
            wilayah = (data.get('wilayah_rohani') or '').lower()
            status = (data.get('status') or '').lower()

            if (search_text in nama_lengkap or
                search_text in jabatan or
                search_text in kelompok or
                search_text in email or
                search_text in no_hp or
                search_text in wilayah or
                search_text in status):
                filtered_data.append(data)

        self.kategorial_data = filtered_data
        self.populate_kategorial_views()

    def refresh_kategorial_data(self):
        """Refresh data K. Kategorial dari database"""
        self.kategorial_search_input.clear()

        if hasattr(self, 'all_kategorial_data'):
            self.all_kategorial_data = []

        self.load_kategorial_data()
        self.log_message.emit("Data komunitas kategorial berhasil di-refresh")

    def add_kategorial(self):
        """Tambah pengurus komunitas kategorial baru"""
        dialog = KategorialDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            if not data['nama_lengkap']:
                QMessageBox.warning(self, "Error", "Nama lengkap harus diisi")
                return

            if not data['kelompok_kategorial']:
                QMessageBox.warning(self, "Error", "Kelompok kategorial harus dipilih")
                return

            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            if not hasattr(self.db_manager, 'add_kategorial'):
                QMessageBox.critical(self, "Error", "Method add_kategorial tidak tersedia")
                self.log_message.emit("Method add_kategorial tidak tersedia")
                return

            self.log_message.emit("Mencoba menambahkan pengurus komunitas kategorial...")
            success, result = self.db_manager.add_kategorial(data)
            if success:
                QMessageBox.information(self, "Sukses", "Pengurus komunitas kategorial berhasil ditambahkan.")
                self.load_kategorial_data()
                self.log_message.emit("Pengurus komunitas kategorial berhasil ditambahkan")
            else:
                QMessageBox.critical(self, "Error", f"Gagal menambahkan pengurus: {result}")
                self.log_message.emit(f"API Error - Gagal menambahkan pengurus: {result}")

    def edit_kategorial(self):
        """Edit pengurus komunitas kategorial yang dipilih"""
        current_row = self.kategorial_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengurus yang akan diedit")
            return

        if current_row >= len(self.kategorial_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return

        kategorial_data = self.kategorial_data[current_row]
        self.edit_kategorial_dialog(kategorial_data)

    def edit_kategorial_dialog(self, kategorial_data):
        """Buka dialog edit dengan data komunitas kategorial"""
        dialog = KategorialDialog(self, kategorial_data)
        if dialog.exec_() == dialog.Accepted:
            updated_data = dialog.get_data()

            if not updated_data['nama_lengkap']:
                QMessageBox.warning(self, "Error", "Nama lengkap harus diisi")
                return

            if not updated_data['kelompok_kategorial']:
                QMessageBox.warning(self, "Error", "Kelompok kategorial harus dipilih")
                return

            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            kategorial_id = kategorial_data.get('id_kategorial')
            if kategorial_id and hasattr(self.db_manager, 'update_kategorial'):
                success, result = self.db_manager.update_kategorial(kategorial_id, updated_data)
                if success:
                    QMessageBox.information(self, "Sukses", "Pengurus komunitas kategorial berhasil diupdate.")
                    self.load_kategorial_data()
                    self.log_message.emit("Pengurus komunitas kategorial berhasil diupdate")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal mengupdate pengurus: {result}")
                    self.log_message.emit(f"Error update pengurus: {result}")
            else:
                QMessageBox.critical(self, "Error", "Method update_kategorial tidak tersedia")

    def delete_kategorial(self):
        """Hapus pengurus komunitas kategorial yang dipilih"""
        current_row = self.kategorial_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengurus yang akan dihapus")
            return

        if current_row >= len(self.kategorial_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return

        kategorial_data = self.kategorial_data[current_row]
        self.delete_kategorial_confirm(kategorial_data)

    def delete_kategorial_confirm(self, kategorial_data):
        """Konfirmasi hapus pengurus komunitas kategorial"""
        nama_lengkap = kategorial_data.get('nama_lengkap', 'Unknown')
        kelompok = kategorial_data.get('kelompok_kategorial', '')

        reply = QMessageBox.question(self, 'Konfirmasi',
                                    f"Yakin ingin menghapus '{nama_lengkap}' dari {kelompok}?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return

            kategorial_id = kategorial_data.get('id_kategorial')
            if kategorial_id and hasattr(self.db_manager, 'delete_kategorial'):
                success, result = self.db_manager.delete_kategorial(kategorial_id)
                if success:
                    QMessageBox.information(self, "Sukses", "Pengurus komunitas kategorial berhasil dihapus.")
                    self.load_kategorial_data()
                    self.log_message.emit("Pengurus komunitas kategorial berhasil dihapus")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal menghapus pengurus: {result}")
                    self.log_message.emit(f"Error hapus pengurus: {result}")
            else:
                QMessageBox.critical(self, "Error", "Method delete_kategorial tidak tersedia")

    def export_kategorial_data(self):
        """Export data K. Kategorial ke file CSV"""
        if not self.kategorial_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Data Komunitas Kategorial", "kategorial.csv", "CSV Files (*.csv)")
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Kelompok Kategorial", "Nama Lengkap", "Jenis Kelamin", "Jabatan", "No. HP",
                    "Email", "Alamat", "Wilayah Rohani", "Masa Jabatan", "Status", "Foto Path"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in self.kategorial_data:
                    kelompok = item.get('kelompok_kategorial', '')
                    if kelompok == 'Lainnya':
                        kelompok = item.get('kelompok_kategorial_lainnya', 'Lainnya')

                    writer.writerow({
                        "Kelompok Kategorial": kelompok,
                        "Nama Lengkap": item.get('nama_lengkap', ''),
                        "Jenis Kelamin": item.get('jenis_kelamin', ''),
                        "Jabatan": item.get('jabatan', ''),
                        "No. HP": item.get('no_hp', ''),
                        "Email": item.get('email', ''),
                        "Alamat": item.get('alamat', ''),
                        "Wilayah Rohani": item.get('wilayah_rohani', ''),
                        "Masa Jabatan": item.get('masa_jabatan', ''),
                        "Status": item.get('status', ''),
                        "Foto Path": item.get('foto_path', '')
                    })

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data komunitas kategorial diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
            self.log_message.emit(f"Gagal mengekspor data: {str(e)}")

    def create_kategorial_action_buttons(self):
        """Buat tombol-tombol aksi untuk K. Kategorial"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        edit_button = self.create_button("Edit", "#f39c12", self.edit_kategorial, "server/assets/edit.png")
        action_layout.addWidget(edit_button)

        delete_button = self.create_button("Hapus", "#c0392b", self.delete_kategorial, "server/assets/hapus.png")
        action_layout.addWidget(delete_button)

        export_button = self.create_button(".CSV", "#16a085", self.export_kategorial_data, "server/assets/export.png")
        action_layout.addWidget(export_button)

        return action_layout

    def show_kategorial_context_menu(self, position):
        """Tampilkan context menu untuk K. Kategorial table"""
        if self.kategorial_table.rowCount() == 0:
            return

        menu = QMenu()

        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")

        action = menu.exec_(self.kategorial_table.mapToGlobal(position))

        if action == edit_action:
            self.edit_kategorial()
        elif action == delete_action:
            self.delete_kategorial()
