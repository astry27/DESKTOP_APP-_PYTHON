# Path: server/components/struktur_wr.py
# WR (Wilayah Rohani) Tab Component

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                            QMessageBox, QFileDialog, QMenu, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import csv

from .struktur_base import BaseStrukturComponent, WordWrapHeaderView
from .dialogs import WRDialog


class StrukturWRComponent(BaseStrukturComponent):
    """Komponen untuk tab WR (Wilayah Rohani)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.wr_data = []
        self.wr_search_input = None
        self.wr_table_view = None
        self.wr_total_label = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI untuk tab WR"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header pencarian
        header_widget = self.create_wr_header()
        layout.addWidget(header_widget)

        # Header periode/judul
        periode_header = self.create_wr_periode_header()
        layout.addWidget(periode_header)

        # Table view
        self.wr_table_view = self.create_wr_table_view()
        layout.addWidget(self.wr_table_view)

        # Tombol aksi
        action_layout = self.create_wr_action_buttons()
        layout.addLayout(action_layout)

    def create_wr_header(self):
        """Buat header dengan search box untuk tab WR"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setSpacing(10)

        # Search input
        self.wr_search_input = QLineEdit()
        self.wr_search_input.setPlaceholderText("Cari berdasarkan nama, wilayah, jabatan, email, atau nomor HP...")
        self.wr_search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 11px;
                background-color: white;
            }
        """)
        self.wr_search_input.textChanged.connect(self.filter_wr_data)
        header_layout.addWidget(self.wr_search_input)

        refresh_btn = self.create_button("Refresh", "#3498db", self.refresh_wr_data, "server/assets/refresh.png")
        header_layout.addWidget(refresh_btn)

        add_btn = self.create_button("Tambah Pengurus", "#27ae60", self.add_wr, "server/assets/tambah.png")
        header_layout.addWidget(add_btn)

        header_widget.setStyleSheet("background-color: #f8f9fa;")
        return header_widget

    def create_wr_periode_header(self):
        """Buat header periode untuk WR"""
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

        # Judul gereja - line 1 (WR Header) - matching DPP styling
        title_label = QLabel("Pengurus Wilayah Rohani")
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
        self.wr_total_label = QLabel("Total: 0 pengurus (0 aktif)")
        self.wr_total_label.setAlignment(Qt.AlignCenter)
        font3 = QFont("Arial", 11, QFont.Normal)
        self.wr_total_label.setFont(font3)
        self.wr_total_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """)
        self.wr_total_label.setMinimumHeight(18)
        header_layout.addWidget(self.wr_total_label, 0, Qt.AlignCenter)

        return header_frame

    def create_wr_table_view(self):
        """Buat tabel dengan 10 kolom untuk data WR"""
        table = QTableWidget(0, 10)

        custom_header = WordWrapHeaderView(Qt.Horizontal, table)
        table.setHorizontalHeader(custom_header)

        table.setHorizontalHeaderLabels([
            "Foto", "Wilayah Rohani", "Nama Lengkap", "Jenis Kelamin",
            "Jabatan", "No. HP", "Email", "Alamat", "Masa Jabatan", "Status"
        ])

        self.apply_professional_table_style(table)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        table.setColumnWidth(0, 80)   # Foto
        table.setColumnWidth(1, 140)  # Wilayah Rohani
        table.setColumnWidth(2, 140)  # Nama Lengkap
        table.setColumnWidth(3, 100)  # Jenis Kelamin
        table.setColumnWidth(4, 120)  # Jabatan
        table.setColumnWidth(5, 120)  # No. HP
        table.setColumnWidth(6, 140)  # Email
        table.setColumnWidth(7, 150)  # Alamat
        table.setColumnWidth(8, 110)  # Masa Jabatan
        table.setColumnWidth(9, 100)  # Status

        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_wr_context_menu)

        QTimer.singleShot(100, lambda: self.update_wr_header_height(0, 0, 0))
        header.sectionResized.connect(self.update_wr_header_height)

        return table

    def update_wr_header_height(self, logicalIndex, oldSize, newSize):
        """Update header height untuk WR table"""
        if hasattr(self, 'wr_table_view') and self.wr_table_view:
            header = self.wr_table_view.horizontalHeader()
            header.setMinimumHeight(25)
            max_height = 25

            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            header.setFixedHeight(max_height)

    def load_wr_data(self):
        """Load data WR dari database"""
        if not self.db_manager:
            return

        success, result = self.db_manager.get_wr_list()
        if success:
            self.wr_data = result if isinstance(result, list) else []
        else:
            self.wr_data = []

        self.populate_wr_views()

    def populate_wr_views(self):
        """Populate table dengan data WR"""
        if hasattr(self, 'wr_table_view'):
            self.populate_wr_table_view()
        self.update_total_wr()

    def populate_wr_table_view(self):
        """Isi tabel WR dengan data"""
        self.wr_table_view.setRowCount(0)

        for row, item in enumerate(self.wr_data):
            self.wr_table_view.insertRow(row)

            # Foto - Load asynchronously
            foto_path = item.get('foto_path', '')
            foto_cell = self.load_image_async('wr', row, 0, foto_path)
            self.wr_table_view.setItem(row, 0, foto_cell)

            # Data fields
            fields = [
                'wilayah_rohani', 'nama_lengkap', 'jenis_kelamin',
                'jabatan', 'no_hp', 'email', 'alamat', 'masa_jabatan'
            ]
            for col, field in enumerate(fields, 1):
                value = item.get(field, '')
                cell = QTableWidgetItem(str(value) if value else "")
                self.wr_table_view.setItem(row, col, cell)

            # Column 9: Status
            status = item.get('status', '')
            status_item = QTableWidgetItem(status)

            if status == "Aktif":
                status_item.setBackground(Qt.green)
                status_item.setText("🟢 Aktif")
            elif status == "Tidak Aktif":
                status_item.setBackground(Qt.lightGray)
                status_item.setText("🔴 Tidak Aktif")

            self.wr_table_view.setItem(row, 9, status_item)

    def update_total_wr(self):
        """Update label total WR"""
        if hasattr(self, 'wr_total_label'):
            total = len(self.wr_data)
            aktif = sum(1 for x in self.wr_data if x.get('status') == 'Aktif')
            self.wr_total_label.setText(f"Total: {total} pengurus ({aktif} aktif)")

    def add_wr(self):
        """Tambah pengurus WR baru"""
        if not self.db_manager or not hasattr(self.db_manager, 'add_wr'):
            self.emit_message("Database tidak tersedia", "error")
            return

        dialog = WRDialog(self, wr_data=None)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            if not data.get('nama_lengkap'):
                self.emit_message("Nama lengkap harus diisi", "error")
                return
            if not data.get('wilayah_rohani'):
                self.emit_message("Wilayah rohani harus dipilih", "error")
                return

            success, result = self.db_manager.add_wr(data)
            if success:
                self.emit_message(f"Pengurus WR berhasil ditambahkan (ID: {result})", "success")
                self.load_wr_data()
            else:
                self.emit_message(f"Gagal menambahkan pengurus WR: {result}", "error")

    def edit_wr(self):
        """Edit pengurus WR yang dipilih"""
        current_row = self.wr_table_view.currentRow()
        if current_row < 0:
            self.emit_message("Silahkan pilih baris untuk diedit", "warning")
            return

        item = self.wr_data[current_row]
        self.edit_wr_dialog(item)

    def edit_wr_dialog(self, item):
        """Buka dialog edit untuk WR"""
        if not self.db_manager or not hasattr(self.db_manager, 'update_wr'):
            self.emit_message("Database tidak tersedia", "error")
            return

        dialog = WRDialog(self, wr_data=item)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            if not data.get('nama_lengkap'):
                self.emit_message("Nama lengkap harus diisi", "error")
                return
            if not data.get('wilayah_rohani'):
                self.emit_message("Wilayah rohani harus dipilih", "error")
                return

            success, result = self.db_manager.update_wr(item['id_wilayah'], data)
            if success:
                self.emit_message("Pengurus WR berhasil diperbarui", "success")
                self.load_wr_data()
            else:
                self.emit_message(f"Gagal memperbarui pengurus WR: {result}", "error")

    def delete_wr(self):
        """Hapus pengurus WR yang dipilih"""
        current_row = self.wr_table_view.currentRow()
        if current_row < 0:
            self.emit_message("Silahkan pilih baris untuk dihapus", "warning")
            return

        item = self.wr_data[current_row]
        nama = item.get('nama_lengkap', 'Unknown')
        wilayah = item.get('wilayah_rohani', 'Unknown')

        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Hapus pengurus:\n\nNama: {nama}\nWilayah: {wilayah}",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if not self.db_manager or not hasattr(self.db_manager, 'delete_wr'):
                self.emit_message("Database tidak tersedia", "error")
                return

            success, result = self.db_manager.delete_wr(item['id_wilayah'])
            if success:
                self.emit_message("Pengurus WR berhasil dihapus", "success")
                self.load_wr_data()
            else:
                self.emit_message(f"Gagal menghapus pengurus WR: {result}", "error")

    def filter_wr_data(self):
        """Filter data WR real-time"""
        search_text = self.wr_search_input.text().lower()

        if not search_text:
            self.populate_wr_views()
            return

        filtered = [item for item in self.wr_data if any(
            search_text in str(item.get(field, '')).lower()
            for field in ['nama_lengkap', 'jabatan', 'wilayah_rohani', 'email', 'no_hp', 'status']
        )]

        original = self.wr_data
        self.wr_data = filtered
        self.populate_wr_views()
        self.wr_data = original

    def refresh_wr_data(self):
        """Refresh data WR dari database"""
        self.wr_search_input.setText("")
        self.load_wr_data()

    def export_wr_data(self):
        """Export data WR ke CSV"""
        if not self.wr_data:
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
                    'Wilayah Rohani', 'Nama Lengkap', 'Jenis Kelamin',
                    'Jabatan', 'No. HP', 'Email', 'Alamat', 'Masa Jabatan', 'Status'
                ])

                for item in self.wr_data:
                    writer.writerow([
                        item.get('wilayah_rohani', ''),
                        item.get('nama_lengkap', ''),
                        item.get('jenis_kelamin', ''),
                        item.get('jabatan', ''),
                        item.get('no_hp', ''),
                        item.get('email', ''),
                        item.get('alamat', ''),
                        item.get('masa_jabatan', ''),
                        item.get('status', '')
                    ])

            self.emit_message("Data berhasil diekspor", "success")
        except Exception as e:
            self.emit_message(f"Gagal mengekspor data: {str(e)}", "error")

    def create_wr_action_buttons(self):
        """Buat tombol aksi untuk tab WR"""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.setSpacing(10)
        button_layout.addStretch()

        edit_btn = self.create_button("Edit", "#f39c12", self.edit_wr, "server/assets/edit.png")
        button_layout.addWidget(edit_btn)

        delete_btn = self.create_button("Hapus", "#e74c3c", self.delete_wr, "server/assets/hapus.png")
        button_layout.addWidget(delete_btn)

        export_btn = self.create_button(".CSV", "#16a085", self.export_wr_data, "server/assets/export.png")
        button_layout.addWidget(export_btn)

        return button_layout

    def show_wr_context_menu(self, position):
        """Tampilkan context menu untuk WR"""
        menu = QMenu()
        edit_action = menu.addAction("✏️ Edit")
        delete_action = menu.addAction("🗑️ Hapus")

        action = menu.exec_(self.wr_table_view.mapToGlobal(position))

        if action == edit_action:
            self.edit_wr()
        elif action == delete_action:
            self.delete_wr()
