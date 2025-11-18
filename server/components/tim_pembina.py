# Path: server/components/tim_pembina.py
# type: ignore
# noinspection PyTypeChecker

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
                            QTableWidget, QTableWidgetItem, QMessageBox, QDialog,
                            QHeaderView, QAbstractItemView, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from .dialogs import TimPesertaDialog


class TimPembinaComponent(QWidget):
    """Komponen untuk manajemen Tim Pembina (peserta tim)"""

    data_updated = pyqtSignal()
    log_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.peserta_data = []
        self.db_manager = None
        self.filtered_data = []
        self.current_tahun_filter = None
        self.current_tim_filter = None
        self.current_jabatan_filter = None
        self.tim_list = []
        self.jabatan_list = []
        self.setup_ui()

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        self.load_data()

    def setup_ui(self):
        """Setup UI untuk halaman Tim Pembina Peserta"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)

        # Title
        title_label = QLabel("Manajemen Tim Pembina")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        # Info label
        self.info_label = QLabel("Total: 0 peserta")
        info_font = QFont()
        info_font.setPointSize(9)
        self.info_label.setFont(info_font)
        self.info_label.setStyleSheet("color: #666; font-weight: normal;")
        header_layout.addWidget(self.info_label)

        main_layout.addLayout(header_layout)

        # Button and filter layout
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        # Tambah Peserta button
        self.tambah_peserta_btn = QPushButton("+ Tambah Peserta")
        self.tambah_peserta_btn.setMinimumHeight(36)
        self.tambah_peserta_btn.setMaximumWidth(150)
        self.tambah_peserta_btn.setCursor(Qt.PointingHandCursor)
        self.tambah_peserta_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.tambah_peserta_btn.clicked.connect(self.on_tambah_peserta)
        toolbar_layout.addWidget(self.tambah_peserta_btn)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setMinimumHeight(36)
        self.refresh_btn.setMaximumWidth(110)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_data)
        toolbar_layout.addWidget(self.refresh_btn)

        # Filters
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(QLabel("Filter:"))

        # Tahun filter
        toolbar_layout.addWidget(QLabel("Tahun:"))
        self.tahun_filter = QComboBox()
        self.tahun_filter.setMinimumWidth(100)
        self.tahun_filter.currentTextChanged.connect(self.apply_filters)
        toolbar_layout.addWidget(self.tahun_filter)

        # Tim Pembina filter
        toolbar_layout.addWidget(QLabel("Tim:"))
        self.tim_filter = QComboBox()
        self.tim_filter.setMinimumWidth(150)
        self.tim_filter.currentTextChanged.connect(self.apply_filters)
        toolbar_layout.addWidget(self.tim_filter)

        # Jabatan filter
        toolbar_layout.addWidget(QLabel("Jabatan:"))
        self.jabatan_filter = QComboBox()
        self.jabatan_filter.setMinimumWidth(130)
        self.jabatan_filter.currentTextChanged.connect(self.apply_filters)
        toolbar_layout.addWidget(self.jabatan_filter)

        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        # Table widget
        self.peserta_table = QTableWidget()
        self.peserta_table.setColumnCount(6)
        self.peserta_table.setHorizontalHeaderLabels([
            "Nama Peserta", "Wilayah Rohani", "Jabatan", "Tim Pembina", "Tahun", "Aksi"
        ])

        # Configure table appearance
        self.peserta_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f9f9f9;
                gridline-color: #eee;
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """)

        # Set column widths
        header = self.peserta_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nama Peserta
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # WR
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Jabatan
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Tim Pembina
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Tahun
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Aksi

        self.peserta_table.setAlternatingRowColors(True)
        self.peserta_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.peserta_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.peserta_table.setMinimumHeight(400)
        self.peserta_table.verticalHeader().setDefaultSectionSize(35)

        main_layout.addWidget(self.peserta_table)

    def load_data(self):
        """Load peserta data dari database"""
        if not self.db_manager:
            self.log_message.emit("❌ Database manager tidak tersedia")
            self.update_info_label()
            return

        try:
            self.log_message.emit("📥 Memuat data tim pembina...")
            success, result = self.db_manager.get_tim_pembina_peserta()

            if success and isinstance(result, dict) and result.get('success'):
                self.peserta_data = result.get('data', [])
                self.populate_filters()
                self.populate_peserta_table()
                self.update_info_label()
                self.log_message.emit(f"✅ Data tim pembina berhasil dimuat: {len(self.peserta_data)} peserta")
                self.data_updated.emit()
            else:
                self.peserta_data = []
                self.populate_filters()
                self.populate_peserta_table()
                self.update_info_label()
                error_msg = result if isinstance(result, str) else str(result)
                self.log_message.emit(f"⚠️ Error loading tim pembina: {error_msg}")
        except Exception as e:
            self.peserta_data = []
            self.populate_filters()
            self.populate_peserta_table()
            print(f"[Tim Pembina] Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            self.log_message.emit(f"❌ Exception loading tim pembina: {str(e)}")

    def populate_filters(self):
        """Populate filter dropdowns from data"""
        # Get unique tahun values
        tahun_set = set()
        tim_set = set()
        jabatan_set = set()

        for peserta in self.peserta_data:
            tahun = peserta.get('tahun')
            if tahun:
                tahun_set.add(str(tahun))
            tim = peserta.get('nama_tim', peserta.get('tim_pembina', ''))
            if tim:
                tim_set.add(tim)
            jabatan = peserta.get('jabatan', '')
            if jabatan:
                jabatan_set.add(jabatan)

        # Sort tahun descending (newest first)
        tahun_list = sorted(tahun_set, reverse=True)

        # Update Tahun filter
        self.tahun_filter.blockSignals(True)
        self.tahun_filter.clear()
        self.tahun_filter.addItem("-- Semua Tahun --")
        for tahun in tahun_list:
            self.tahun_filter.addItem(str(tahun))
        self.tahun_filter.blockSignals(False)

        # Update Tim filter
        self.tim_filter.blockSignals(True)
        self.tim_filter.clear()
        self.tim_filter.addItem("-- Semua Tim --")
        for tim in sorted(tim_set):
            self.tim_filter.addItem(tim)
        self.tim_filter.blockSignals(False)

        # Update Jabatan filter
        self.jabatan_filter.blockSignals(True)
        self.jabatan_filter.clear()
        self.jabatan_filter.addItem("-- Semua Jabatan --")
        for jabatan in sorted(jabatan_set):
            self.jabatan_filter.addItem(jabatan)
        self.jabatan_filter.blockSignals(False)

    def apply_filters(self):
        """Apply filters to peserta data"""
        tahun_filter = self.tahun_filter.currentText()
        tim_filter = self.tim_filter.currentText()
        jabatan_filter = self.jabatan_filter.currentText()

        self.filtered_data = self.peserta_data.copy()

        # Filter by tahun
        if tahun_filter != "-- Semua Tahun --":
            self.filtered_data = [p for p in self.filtered_data if str(p.get('tahun', '')) == tahun_filter]

        # Filter by tim
        if tim_filter != "-- Semua Tim --":
            self.filtered_data = [p for p in self.filtered_data if (p.get('nama_tim', p.get('tim_pembina', '')) == tim_filter)]

        # Filter by jabatan
        if jabatan_filter != "-- Semua Jabatan --":
            self.filtered_data = [p for p in self.filtered_data if p.get('jabatan', '') == jabatan_filter]

        self.populate_peserta_table()
        self.update_info_label()

    def populate_peserta_table(self):
        """Populate table dengan peserta data"""
        self.peserta_table.setRowCount(0)

        if not self.filtered_data:
            self.peserta_table.insertRow(0)
            empty_item = QTableWidgetItem("Tidak ada data. Klik 'Tambah Peserta' untuk menambah data baru.")
            empty_item.setFont(QFont("Arial", 10))
            empty_item.setForeground(QColor("#999"))
            self.peserta_table.setItem(0, 0, empty_item)
            self.peserta_table.setSpan(0, 0, 1, 6)
            return

        for row, peserta in enumerate(self.filtered_data):
            self.peserta_table.insertRow(row)
            self.peserta_table.setRowHeight(row, 35)

            # Column 0: Nama Peserta
            nama_item = QTableWidgetItem(peserta.get('nama_peserta', '-'))
            nama_item.setFont(QFont("Arial", 10))
            self.peserta_table.setItem(row, 0, nama_item)

            # Column 1: Wilayah Rohani
            wr_item = QTableWidgetItem(peserta.get('wilayah_rohani', '-'))
            wr_item.setFont(QFont("Arial", 10))
            wr_item.setTextAlignment(Qt.AlignCenter)
            self.peserta_table.setItem(row, 1, wr_item)

            # Column 2: Jabatan
            jabatan_item = QTableWidgetItem(peserta.get('jabatan', '-'))
            jabatan_item.setFont(QFont("Arial", 10))
            jabatan_item.setTextAlignment(Qt.AlignCenter)
            self.peserta_table.setItem(row, 2, jabatan_item)

            # Column 3: Tim Pembina
            tim_item = QTableWidgetItem(peserta.get('nama_tim', peserta.get('tim_pembina', '-')))
            tim_item.setFont(QFont("Arial", 10))
            self.peserta_table.setItem(row, 3, tim_item)

            # Column 4: Tahun
            tahun_item = QTableWidgetItem(str(peserta.get('tahun', '-')))
            tahun_item.setFont(QFont("Arial", 10))
            tahun_item.setTextAlignment(Qt.AlignCenter)
            self.peserta_table.setItem(row, 4, tahun_item)

            # Column 5: Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(5)

            # Edit button
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setMaximumWidth(70)
            edit_btn.setMinimumHeight(28)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 9px;
                    padding: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1f618d;
                }
            """)
            peserta_id = peserta.get('id_tim_pembina')
            edit_btn.clicked.connect(lambda checked, pid=peserta_id: self.on_edit_peserta(pid))
            action_layout.addWidget(edit_btn)

            # Delete button
            delete_btn = QPushButton("🗑️ Hapus")
            delete_btn.setMaximumWidth(75)
            delete_btn.setMinimumHeight(28)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 9px;
                    padding: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            delete_btn.clicked.connect(lambda checked, pid=peserta_id: self.on_delete_peserta(pid))
            action_layout.addWidget(delete_btn)

            action_layout.addStretch()
            action_widget.setLayout(action_layout)
            self.peserta_table.setCellWidget(row, 5, action_widget)

    def update_info_label(self):
        """Update info label dengan total peserta"""
        total_peserta = len(self.filtered_data) if self.filtered_data else 0
        self.info_label.setText(f"Total: {total_peserta} peserta")

    def on_tambah_peserta(self):
        """Handle tambah peserta button clicked"""
        dialog = TimPesertaDialog(self, db_manager=self.db_manager)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            # Validation
            if not data.get('nama_peserta'):
                QMessageBox.warning(self, "Validasi", "Nama peserta harus dipilih")
                return

            if not data.get('wilayah_rohani'):
                QMessageBox.warning(self, "Validasi", "Wilayah Rohani harus dipilih")
                return

            if not data.get('jabatan') or data.get('jabatan') == "Pilih Jabatan":
                QMessageBox.warning(self, "Validasi", "Jabatan harus dipilih")
                return

            if not data.get('nama_tim') or data.get('nama_tim') == "Pilih Tim":
                QMessageBox.warning(self, "Validasi", "Tim Pembina harus dipilih")
                return

            if not data.get('tahun'):
                QMessageBox.warning(self, "Validasi", "Tahun harus dipilih")
                return

            if not self.db_manager:
                QMessageBox.critical(self, "Error", "Database manager tidak tersedia")
                return

            try:
                self.log_message.emit("Menambahkan peserta tim pembina...")
                success, result = self.db_manager.add_tim_pembina_peserta_new(data)
                if success and isinstance(result, dict) and result.get('success'):
                    QMessageBox.information(self, "Sukses", "Peserta berhasil ditambahkan")
                    self.log_message.emit("Peserta berhasil ditambahkan")
                    QTimer.singleShot(300, self.load_data)
                    QTimer.singleShot(600, lambda: self.data_updated.emit())
                else:
                    error_msg = result if isinstance(result, str) else str(result)
                    QMessageBox.critical(self, "Error", f"Gagal menambah peserta: {error_msg}")
                    self.log_message.emit(f"Error adding peserta: {error_msg}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Exception: {str(e)}")
                self.log_message.emit(f"Exception adding peserta: {str(e)}")

    def on_edit_peserta(self, peserta_id):
        """Handle edit peserta button clicked"""
        peserta_data = next((p for p in self.peserta_data if p.get('id_tim_pembina') == peserta_id), None)
        if not peserta_data:
            QMessageBox.warning(self, "Error", "Peserta tidak ditemukan")
            return

        dialog = TimPesertaDialog(self, peserta_data=peserta_data, db_manager=self.db_manager)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            # Validation
            if not data.get('nama_peserta'):
                QMessageBox.warning(self, "Validasi", "Nama peserta harus dipilih")
                return

            if not data.get('wilayah_rohani'):
                QMessageBox.warning(self, "Validasi", "Wilayah Rohani harus dipilih")
                return

            if not data.get('jabatan') or data.get('jabatan') == "Pilih Jabatan":
                QMessageBox.warning(self, "Validasi", "Jabatan harus dipilih")
                return

            if not data.get('nama_tim') or data.get('nama_tim') == "Pilih Tim":
                QMessageBox.warning(self, "Validasi", "Tim Pembina harus dipilih")
                return

            if not data.get('tahun'):
                QMessageBox.warning(self, "Validasi", "Tahun harus dipilih")
                return

            if not self.db_manager:
                QMessageBox.critical(self, "Error", "Database manager tidak tersedia")
                return

            try:
                self.log_message.emit(f"Mengupdate peserta ID {peserta_id}...")
                success, result = self.db_manager.update_tim_pembina_peserta(peserta_id, data)
                if success and isinstance(result, dict) and result.get('success'):
                    QMessageBox.information(self, "Sukses", "Peserta berhasil diupdate")
                    self.log_message.emit("Peserta berhasil diupdate")
                    QTimer.singleShot(300, self.load_data)
                    QTimer.singleShot(600, lambda: self.data_updated.emit())
                else:
                    error_msg = result if isinstance(result, str) else str(result)
                    QMessageBox.critical(self, "Error", f"Gagal mengupdate peserta: {error_msg}")
                    self.log_message.emit(f"Error updating peserta: {error_msg}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Exception: {str(e)}")
                self.log_message.emit(f"Exception updating peserta: {str(e)}")

    def on_delete_peserta(self, peserta_id):
        """Handle delete peserta button clicked"""
        peserta_data = next((p for p in self.peserta_data if p.get('id_tim_pembina') == peserta_id), None)
        if not peserta_data:
            QMessageBox.warning(self, "Error", "Peserta tidak ditemukan")
            return

        peserta_nama = peserta_data.get('nama_peserta', 'Peserta')
        reply = QMessageBox.question(
            self,
            'Konfirmasi Penghapusan',
            f"Yakin ingin menghapus peserta '{peserta_nama}'?\n\nTindakan ini tidak dapat dibatalkan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if not self.db_manager:
                QMessageBox.critical(self, "Error", "Database manager tidak tersedia")
                return

            try:
                self.log_message.emit(f"Menghapus peserta ID {peserta_id}...")
                success, result = self.db_manager.delete_tim_pembina_peserta_new(peserta_id)
                if success and isinstance(result, dict) and result.get('success'):
                    QMessageBox.information(self, "Sukses", f"Peserta '{peserta_nama}' berhasil dihapus")
                    self.log_message.emit("Peserta berhasil dihapus")
                    QTimer.singleShot(300, self.load_data)
                    QTimer.singleShot(600, lambda: self.data_updated.emit())
                else:
                    error_msg = result if isinstance(result, str) else str(result)
                    QMessageBox.critical(self, "Error", f"Gagal menghapus peserta: {error_msg}")
                    self.log_message.emit(f"Error deleting peserta: {error_msg}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Exception: {str(e)}")
                self.log_message.emit(f"Exception deleting peserta: {str(e)}")
