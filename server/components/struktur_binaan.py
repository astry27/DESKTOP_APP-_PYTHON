# Path: server/components/struktur_binaan.py
# K. Binaan (Komunitas Binaan) Tab Component

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                            QMessageBox, QFileDialog, QMenu, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import csv

from .struktur_base import BaseStrukturComponent, WordWrapHeaderView
from .dialogs import KBinaanDialog


class StrukturBinaanComponent(BaseStrukturComponent):
    """Komponen untuk tab K. Binaan (Komunitas Binaan)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.binaan_data = []
        self.binaan_search_input = None
        self.binaan_table_view = None
        self.binaan_total_label = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI untuk tab K. Binaan"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header pencarian
        header_widget = self.create_binaan_header()
        layout.addWidget(header_widget)

        # Header periode/judul
        periode_header = self.create_binaan_periode_header()
        layout.addWidget(periode_header)

        # Table view
        self.binaan_table_view = self.create_binaan_table_view()
        layout.addWidget(self.binaan_table_view)

        # Tombol aksi
        action_layout = self.create_binaan_action_buttons()
        layout.addLayout(action_layout)

    def create_search_input(self):
        """Buat search input dengan styling"""
        search_input = QLineEdit()
        search_input.setPlaceholderText("Cari pengurus...")
        search_input.setFixedWidth(300)
        return search_input

    def create_binaan_header(self):
        """Buat header dengan search box dan tombol untuk tab K. Binaan"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 10, 0)

        # Search label
        header_layout.addWidget(QLabel("Cari:"))

        # Search input
        self.binaan_search_input = self.create_search_input()
        self.binaan_search_input.textChanged.connect(self.filter_binaan_data)
        header_layout.addWidget(self.binaan_search_input)

        # Refresh button
        refresh_btn = self.create_button("Refresh", "#3498db", self.refresh_binaan_data, "server/assets/refresh.png")
        header_layout.addWidget(refresh_btn)

        header_layout.addStretch()

        # Add button
        add_btn = self.create_button("Tambah Pengurus", "#27ae60", self.add_binaan, "server/assets/tambah.png")
        header_layout.addWidget(add_btn)

        return header_widget

    def create_binaan_periode_header(self):
        """Buat header periode dengan judul dan total untuk K. Binaan"""
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

        # Judul gereja - line 1 (K. Binaan Header) - matching DPP styling
        title_label = QLabel("Pengurus Kelompok Binaan")
        title_label.setAlignment(Qt.AlignCenter)
        font1 = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(font1)
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

        church_label = QLabel("Santa Maria Ratu Damai, Uluindano")
        church_label.setAlignment(Qt.AlignCenter)
        church_label.setStyleSheet("QLabel { color: #7f8c8d; font-size: 12px; padding: 2px; }")
        church_label.setMinimumHeight(22)
        header_layout.addWidget(church_label, 0, Qt.AlignCenter)

        self.binaan_total_label = QLabel("Total: 0 pengurus (0 aktif)")
        self.binaan_total_label.setAlignment(Qt.AlignCenter)
        self.binaan_total_label.setStyleSheet("QLabel { color: #95a5a6; font-size: 11px; padding: 2px; }")
        self.binaan_total_label.setMinimumHeight(18)
        header_layout.addWidget(self.binaan_total_label, 0, Qt.AlignCenter)

        return header_frame

    def create_binaan_table_view(self):
        """Buat tabel dengan 11 kolom untuk data K. Binaan"""
        table = QTableWidget(0, 11)

        custom_header = WordWrapHeaderView(Qt.Horizontal, table)
        table.setHorizontalHeader(custom_header)

        table.setHorizontalHeaderLabels([
            "Foto", "Kelompok Binaan", "Nama Lengkap", "Jenis Kelamin",
            "Jabatan", "No. HP", "Email", "Alamat", "Wilayah Rohani", "Masa Jabatan", "Status"
        ])

        self.apply_professional_table_style(table)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        table.setColumnWidth(0, 80)   # Foto
        table.setColumnWidth(1, 140)  # Kelompok Binaan
        table.setColumnWidth(2, 140)  # Nama Lengkap
        table.setColumnWidth(3, 100)  # Jenis Kelamin
        table.setColumnWidth(4, 120)  # Jabatan
        table.setColumnWidth(5, 120)  # No. HP
        table.setColumnWidth(6, 140)  # Email
        table.setColumnWidth(7, 150)  # Alamat
        table.setColumnWidth(8, 150)  # Wilayah Rohani
        table.setColumnWidth(9, 110)  # Masa Jabatan
        table.setColumnWidth(10, 100) # Status

        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_binaan_context_menu)

        QTimer.singleShot(100, lambda: self.update_binaan_header_height(0, 0, 0))
        header.sectionResized.connect(self.update_binaan_header_height)

        return table

    def update_binaan_header_height(self, logicalIndex, oldSize, newSize):
        """Update header height untuk K. Binaan table"""
        if hasattr(self, 'binaan_table_view') and self.binaan_table_view:
            header = self.binaan_table_view.horizontalHeader()
            header.setMinimumHeight(25)
            max_height = 25

            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            header.setFixedHeight(max_height)

    def load_binaan_data(self):
        """Load data K. Binaan dari database"""
        if not self.db_manager:
            return

        success, result = self.db_manager.get_binaan_list()
        if success:
            self.binaan_data = result if isinstance(result, list) else []
        else:
            self.binaan_data = []

        self.populate_binaan_views()

    def populate_binaan_views(self):
        """Populate table dengan data K. Binaan"""
        if hasattr(self, 'binaan_table_view'):
            self.populate_binaan_table_view()
        self.update_total_binaan()

    def populate_binaan_table_view(self):
        """Isi tabel K. Binaan dengan data"""
        self.binaan_table_view.setRowCount(0)

        for row, item in enumerate(self.binaan_data):
            self.binaan_table_view.insertRow(row)

            # Foto - Load asynchronously
            foto_path = item.get('foto_path', '')
            foto_cell = self.load_image_async('binaan', row, 0, foto_path)
            self.binaan_table_view.setItem(row, 0, foto_cell)

            # Data fields
            fields = [
                'kelompok_binaan', 'nama_lengkap', 'jenis_kelamin',
                'jabatan', 'no_hp', 'email', 'alamat', 'wilayah_rohani', 'masa_jabatan'
            ]
            for col, field in enumerate(fields, 1):
                value = item.get(field, '')
                cell = QTableWidgetItem(str(value) if value else "")
                self.binaan_table_view.setItem(row, col, cell)

            # Column 10: Status
            status = item.get('status', '')
            status_item = QTableWidgetItem(status)

            if status == "Aktif":
                status_item.setBackground(Qt.green)
                status_item.setText("🟢 Aktif")
            elif status == "Tidak Aktif":
                status_item.setBackground(Qt.lightGray)
                status_item.setText("🔴 Tidak Aktif")

            self.binaan_table_view.setItem(row, 10, status_item)

    def update_total_binaan(self):
        """Update label total K. Binaan"""
        if hasattr(self, 'binaan_total_label'):
            total = len(self.binaan_data)
            aktif = sum(1 for x in self.binaan_data if x.get('status') == 'Aktif')
            self.binaan_total_label.setText(f"Total: {total} pengurus ({aktif} aktif)")

    def add_binaan(self):
        """Tambah pengurus K. Binaan baru"""
        if not self.db_manager or not hasattr(self.db_manager, 'add_binaan'):
            self.emit_message("Database tidak tersedia", "error")
            return

        dialog = KBinaanDialog(self, binaan_data=None)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            if not data.get('nama_lengkap'):
                self.emit_message("Nama lengkap harus diisi", "error")
                return
            if not data.get('kelompok_binaan'):
                self.emit_message("Kelompok binaan harus dipilih", "error")
                return

            success, result = self.db_manager.add_binaan(data)
            if success:
                self.emit_message(f"Pengurus K. Binaan berhasil ditambahkan (ID: {result})", "success")
                self.load_binaan_data()
            else:
                self.emit_message(f"Gagal menambahkan pengurus K. Binaan: {result}", "error")

    def edit_binaan(self):
        """Edit pengurus K. Binaan yang dipilih"""
        current_row = self.binaan_table_view.currentRow()
        if current_row < 0:
            self.emit_message("Silahkan pilih baris untuk diedit", "warning")
            return

        item = self.binaan_data[current_row]
        self.edit_binaan_dialog(item)

    def edit_binaan_dialog(self, item):
        """Buka dialog edit untuk K. Binaan"""
        if not self.db_manager or not hasattr(self.db_manager, 'update_binaan'):
            self.emit_message("Database tidak tersedia", "error")
            return

        dialog = KBinaanDialog(self, binaan_data=item)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            if not data.get('nama_lengkap'):
                self.emit_message("Nama lengkap harus diisi", "error")
                return
            if not data.get('kelompok_binaan'):
                self.emit_message("Kelompok binaan harus dipilih", "error")
                return

            success, result = self.db_manager.update_binaan(item['id_binaan'], data)
            if success:
                self.emit_message("Pengurus K. Binaan berhasil diperbarui", "success")
                self.load_binaan_data()
            else:
                self.emit_message(f"Gagal memperbarui pengurus K. Binaan: {result}", "error")

    def delete_binaan(self):
        """Hapus pengurus K. Binaan yang dipilih"""
        current_row = self.binaan_table_view.currentRow()
        if current_row < 0:
            self.emit_message("Silahkan pilih baris untuk dihapus", "warning")
            return

        item = self.binaan_data[current_row]
        nama = item.get('nama_lengkap', 'Unknown')
        kelompok = item.get('kelompok_binaan', 'Unknown')

        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Hapus pengurus:\n\nNama: {nama}\nKelompok: {kelompok}",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if not self.db_manager or not hasattr(self.db_manager, 'delete_binaan'):
                self.emit_message("Database tidak tersedia", "error")
                return

            success, result = self.db_manager.delete_binaan(item['id_binaan'])
            if success:
                self.emit_message("Pengurus K. Binaan berhasil dihapus", "success")
                self.load_binaan_data()
            else:
                self.emit_message(f"Gagal menghapus pengurus K. Binaan: {result}", "error")

    def filter_binaan_data(self):
        """Filter data K. Binaan real-time"""
        search_text = self.binaan_search_input.text().lower()

        if not search_text:
            self.populate_binaan_views()
            return

        filtered = [item for item in self.binaan_data if any(
            search_text in str(item.get(field, '')).lower()
            for field in ['nama_lengkap', 'jabatan', 'kelompok_binaan', 'email', 'no_hp', 'wilayah_rohani', 'status']
        )]

        original = self.binaan_data
        self.binaan_data = filtered
        self.populate_binaan_views()
        self.binaan_data = original

    def refresh_binaan_data(self):
        """Refresh data K. Binaan dari database"""
        self.binaan_search_input.setText("")
        self.load_binaan_data()

    def export_binaan_data(self):
        """Export data K. Binaan ke CSV"""
        if not self.binaan_data:
            self.emit_message("Tidak ada data untuk diekspor", "warning")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan File CSV", "", "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Kelompok Binaan', 'Nama Lengkap', 'Jenis Kelamin',
                    'Jabatan', 'No. HP', 'Email', 'Alamat', 'Wilayah Rohani', 'Masa Jabatan', 'Status'
                ])

                for item in self.binaan_data:
                    writer.writerow([
                        item.get('kelompok_binaan', ''),
                        item.get('nama_lengkap', ''),
                        item.get('jenis_kelamin', ''),
                        item.get('jabatan', ''),
                        item.get('no_hp', ''),
                        item.get('email', ''),
                        item.get('alamat', ''),
                        item.get('wilayah_rohani', ''),
                        item.get('masa_jabatan', ''),
                        item.get('status', '')
                    ])

            self.emit_message("Data berhasil diekspor", "success")
        except Exception as e:
            self.emit_message(f"Gagal mengekspor data: {str(e)}", "error")

    def create_binaan_action_buttons(self):
        """Buat tombol aksi untuk tab K. Binaan"""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.setSpacing(10)
        button_layout.addStretch()

        edit_btn = self.create_button("Edit Terpilih", "#f39c12", self.edit_binaan, "server/assets/edit.png")
        button_layout.addWidget(edit_btn)

        delete_btn = self.create_button("Hapus Terpilih", "#e74c3c", self.delete_binaan, "server/assets/hapus.png")
        button_layout.addWidget(delete_btn)

        export_btn = self.create_button("Export Data", "#16a085", self.export_binaan_data, "server/assets/export.png")
        button_layout.addWidget(export_btn)

        return button_layout

    def show_binaan_context_menu(self, position):
        """Tampilkan context menu untuk K. Binaan"""
        menu = QMenu()
        edit_action = menu.addAction("✏️ Edit")
        delete_action = menu.addAction("🗑️ Hapus")

        action = menu.exec_(self.binaan_table_view.mapToGlobal(position))

        if action == edit_action:
            self.edit_binaan()
        elif action == delete_action:
            self.delete_binaan()
