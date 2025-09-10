# Path: server/components/inventaris.py

import datetime
import csv
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QGroupBox, QMessageBox, 
                            QFileDialog, QAbstractItemView, QFrame, QLineEdit)
from PyQt5.QtCore import pyqtSignal, QDate, Qt, QSize
from PyQt5.QtGui import QIcon

# Import dialog inventaris yang baru
from .dialogs import InventarisDialog

class InventarisComponent(QWidget):
    """Komponen untuk manajemen inventaris"""
    
    data_updated = pyqtSignal()
    log_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inventaris_data = []
        self.db_manager = None
        self.setup_ui()
    
    def set_database_manager(self, db_manager):
        """Set database manager."""
        self.db_manager = db_manager
        # Auto load data setelah database manager di-set
        if self.db_manager:
            self.load_data()
    
    def setup_ui(self):
        """Setup UI untuk halaman inventaris."""
        layout = QVBoxLayout(self)
        
        # Header Frame (matching dokumen.py style)
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #34495e; color: white; padding: 2px;")
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("Manajemen Inventaris")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Original header with buttons and search
        header = self.create_header()
        layout.addWidget(header)
        
        # Statistik Inventaris
        stats_group = self.create_statistics()
        layout.addWidget(stats_group)
        
        # Tabel inventaris
        self.inventaris_table = self.create_table()
        layout.addWidget(self.inventaris_table)
        
        # Tombol aksi
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)

    def create_header(self):
        """Buat header dengan kontrol pencarian dan tombol tambah."""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 10, 0)  # Add right margin for spacing
        
        # Search functionality
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari inventaris...")
        self.search_input.setFixedWidth(250)
        self.search_input.returnPressed.connect(self.search_inventaris)
        header_layout.addWidget(self.search_input)
        
        search_button = self.create_button("Cari", "#3498db", self.search_inventaris)
        header_layout.addWidget(search_button)
        
        header_layout.addStretch()
        
        add_button = self.create_button("Tambah Inventaris", "#27ae60", self.add_inventaris, "server/assets/tambah.png")
        header_layout.addWidget(add_button)
        
        return header

    def create_statistics(self):
        """Buat panel statistik inventaris."""
        stats_group = QGroupBox("Ringkasan Inventaris")
        stats_layout = QHBoxLayout(stats_group)
        
        self.total_items_value = QLabel("0")
        self.total_value_value = QLabel("Rp 0")
        self.good_condition_value = QLabel("0")
        self.need_attention_value = QLabel("0")
        
        stats_layout.addWidget(self.create_stat_widget("TOTAL ITEM", self.total_items_value, "#ddeaee", "#2c3e50"))
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
                border-radius: 5px; 
                padding: 10px;
            }}
        """)
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold; 
                color: {text_color};
                font-size: 12px;
                font-family: Arial, sans-serif;
                background-color: transparent;
                min-height: 20px;
            }}
        """)
        
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px; 
                font-weight: bold; 
                color: {text_color};
                font-family: Arial, sans-serif;
                background-color: transparent;
                padding: 5px;
                min-height: 25px;
            }}
        """)
        
        layout.addWidget(label)
        layout.addWidget(value_label)
        
        return widget

    def create_table(self):
        """Buat tabel inventaris."""
        table = QTableWidget(0, 8)
        table.setHorizontalHeaderLabels([
            "Kode Barang", "Nama Barang", "Kategori", "Jumlah", 
            "Kondisi", "Lokasi", "Harga Satuan", "Penanggung Jawab"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setAlternatingRowColors(True)
        
        # Enable context menu untuk edit/hapus
        table.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        table.customContextMenuRequested.connect(self.show_context_menu)
        
        return table

    def show_context_menu(self, position):
        """Tampilkan context menu untuk edit/hapus"""
        if self.inventaris_table.rowCount() == 0:
            return
            
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")
        
        action = menu.exec_(self.inventaris_table.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_inventaris()
        elif action == delete_action:
            self.delete_inventaris()

    def create_action_buttons(self):
        """Buat tombol-tombol aksi."""
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        edit_button = self.create_button("Edit Terpilih", "#f39c12", self.edit_inventaris, "server/assets/edit.png")
        action_layout.addWidget(edit_button)
        
        delete_button = self.create_button("Hapus Terpilih", "#c0392b", self.delete_inventaris, "server/assets/hapus.png")
        action_layout.addWidget(delete_button)
        
        export_button = self.create_button("Export Data", "#16a085", self.export_data, "server/assets/export.png")
        action_layout.addWidget(export_button)

        refresh_button = self.create_button("Refresh", "#8e44ad", self.load_data, "server/assets/refresh.png")
        action_layout.addWidget(refresh_button)
        
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
                    button.setIconSize(QSize(20, 20))  # Larger icon size for better visibility
            except Exception:
                pass  # If icon loading fails, just continue without icon
        
        hover_color = self.darken_color(color)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; 
                color: white; 
                padding: 8px 15px; 
                border: none; 
                border-radius: 4px; 
                font-weight: bold;
                font-family: Arial, sans-serif;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border: 1px solid {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(hover_color)};
                border: 2px inset {self.darken_color(hover_color)};
            }}
        """)
        button.clicked.connect(slot)
        return button
    
    def darken_color(self, color):
        """Buat warna lebih gelap untuk hover effect"""
        color_map = {
            "#27ae60": "#229954",  # Hijau
            "#c0392b": "#a93226",  # Merah
            "#3498db": "#2980b9",  # Biru
            "#16a085": "#138d75",  # Teal
            "#8e44ad": "#7d3c98",  # Ungu
            "#f39c12": "#e67e22",  # Orange
            "#2ecc71": "#27ae60",  # Light green
            "#e74c3c": "#c0392b",  # Light red
        }
        return color_map.get(color, color)

    def load_data(self):
        """Load data inventaris dari database."""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            # Test koneksi database terlebih dahulu
            if not hasattr(self.db_manager, 'get_inventaris_list'):
                self.log_message.emit("Error: Database manager tidak memiliki method get_inventaris_list")
                return
            
            # Load inventaris dengan search filter jika ada
            search = self.search_input.text().strip() if hasattr(self, 'search_input') else None
            self.log_message.emit("Mencoba memuat data inventaris...")
            success, inventaris = self.db_manager.get_inventaris_list(search=search)
            
            if success:
                # Handle different response formats
                if isinstance(inventaris, dict) and 'data' in inventaris:
                    self.inventaris_data = inventaris['data']
                elif isinstance(inventaris, list):
                    self.inventaris_data = inventaris
                else:
                    self.inventaris_data = []
                
                self.populate_table()
                self.log_message.emit(f"Data inventaris berhasil dimuat: {len(self.inventaris_data)} record")
            else:
                self.inventaris_data = []
                self.populate_table()
                self.log_message.emit(f"Gagal memuat data inventaris: {inventaris}")
            
            self.update_statistics()
            self.log_message.emit("Proses loading data inventaris selesai")
            self.data_updated.emit()
        except Exception as e:
            self.log_message.emit(f"Exception saat memuat data inventaris: {str(e)}")
            # Reset data jika terjadi error
            self.inventaris_data = []
            self.populate_table()
            self.update_statistics()

    def populate_table(self):
        """Populate tabel dengan data inventaris."""
        self.inventaris_table.setRowCount(0)
        for row_data in self.inventaris_data:
            row_pos = self.inventaris_table.rowCount()
            self.inventaris_table.insertRow(row_pos)
            
            # Kode Barang
            self.inventaris_table.setItem(row_pos, 0, QTableWidgetItem(str(row_data.get('kode_barang', ''))))
            
            # Nama Barang
            self.inventaris_table.setItem(row_pos, 1, QTableWidgetItem(str(row_data.get('nama_barang', ''))))
            
            # Kategori
            self.inventaris_table.setItem(row_pos, 2, QTableWidgetItem(str(row_data.get('kategori', ''))))
            
            # Jumlah dengan satuan
            jumlah = row_data.get('jumlah', 0)
            satuan = row_data.get('satuan', '')
            jumlah_str = f"{jumlah} {satuan}".strip()
            self.inventaris_table.setItem(row_pos, 3, QTableWidgetItem(jumlah_str))
            
            # Kondisi dengan styling
            kondisi = str(row_data.get('kondisi', ''))
            kondisi_item = QTableWidgetItem(kondisi)
            if kondisi == 'Baik':
                kondisi_item.setBackground(Qt.green)
                kondisi_item.setForeground(Qt.white)
            elif kondisi in ['Rusak Ringan', 'Rusak Berat']:
                kondisi_item.setBackground(Qt.red)
                kondisi_item.setForeground(Qt.white)
            elif kondisi == 'Hilang':
                kondisi_item.setBackground(Qt.darkRed)
                kondisi_item.setForeground(Qt.white)
            self.inventaris_table.setItem(row_pos, 4, kondisi_item)
            
            # Lokasi
            self.inventaris_table.setItem(row_pos, 5, QTableWidgetItem(str(row_data.get('lokasi', ''))))
            
            # Harga Satuan - Format sebagai currency Indonesia
            harga = row_data.get('harga_satuan', 0)
            try:
                harga_float = float(harga)
                harga_str = f"Rp {harga_float:,.0f}".replace(',', '.')
            except (ValueError, TypeError):
                harga_str = f"Rp 0"
            self.inventaris_table.setItem(row_pos, 6, QTableWidgetItem(harga_str))
            
            # Penanggung jawab
            self.inventaris_table.setItem(row_pos, 7, QTableWidgetItem(str(row_data.get('penanggung_jawab', ''))))

    def update_statistics(self):
        """Update panel statistik."""
        if not self.inventaris_data:
            self.total_items_value.setText("0")
            self.total_value_value.setText("Rp 0")
            self.good_condition_value.setText("0")
            self.need_attention_value.setText("0")
            return

        # Hitung total item
        total_items = len(self.inventaris_data)
        self.total_items_value.setText(str(total_items))
        
        # Hitung nilai total
        total_value = 0
        good_condition = 0
        need_attention = 0
        
        for item in self.inventaris_data:
            try:
                harga = float(item.get('harga_satuan', 0))
                jumlah = float(item.get('jumlah', 0))
                total_value += harga * jumlah
            except (ValueError, TypeError):
                continue
            
            kondisi = item.get('kondisi', '')
            if kondisi == 'Baik':
                good_condition += 1
            elif kondisi in ['Rusak Ringan', 'Rusak Berat', 'Hilang']:
                need_attention += 1
        
        # Update tampilan
        self.total_value_value.setText(f"Rp {total_value:,.0f}".replace(',', '.'))
        self.good_condition_value.setText(str(good_condition))
        self.need_attention_value.setText(str(need_attention))

    def search_inventaris(self):
        """Cari inventaris berdasarkan keyword"""
        self.load_data()

    def add_inventaris(self):
        """Tambah inventaris baru."""
        dialog = InventarisDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            
            # Validasi
            if not data['nama_barang']:
                QMessageBox.warning(self, "Error", "Nama barang harus diisi")
                return
            
            if not data['kode_barang']:
                QMessageBox.warning(self, "Error", "Kode barang harus diisi")
                return
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            # Check if method exists
            if not hasattr(self.db_manager, 'add_inventaris'):
                QMessageBox.critical(self, "Error", "Method add_inventaris tidak tersedia di database manager")
                self.log_message.emit("Method add_inventaris tidak tersedia")
                return
            
            self.log_message.emit("Mencoba menambahkan inventaris...")
            success, result = self.db_manager.add_inventaris(data)
            if success:
                QMessageBox.information(self, "Sukses", "Inventaris berhasil ditambahkan.")
                self.load_data()
                self.log_message.emit("Inventaris berhasil ditambahkan")
            else:
                QMessageBox.critical(self, "Error", f"Gagal menambahkan inventaris: {result}")
                self.log_message.emit(f"API Error - Gagal menambahkan inventaris: {result}")

    def edit_inventaris(self):
        """Edit inventaris yang dipilih"""
        current_row = self.inventaris_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih inventaris yang akan diedit")
            return
        
        if current_row >= len(self.inventaris_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return
        
        inventaris_data = self.inventaris_data[current_row]
        
        dialog = InventarisDialog(self, inventaris_data)
        if dialog.exec_() == dialog.Accepted:
            updated_data = dialog.get_data()
            
            # Validasi
            if not updated_data['nama_barang']:
                QMessageBox.warning(self, "Error", "Nama barang harus diisi")
                return
            
            if not updated_data['kode_barang']:
                QMessageBox.warning(self, "Error", "Kode barang harus diisi")
                return
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            # Update melalui API
            inventaris_id = inventaris_data.get('id_inventaris')
            if inventaris_id and hasattr(self.db_manager, 'update_inventaris'):
                success, result = self.db_manager.update_inventaris(inventaris_id, updated_data)
                if success:
                    QMessageBox.information(self, "Sukses", "Inventaris berhasil diupdate.")
                    self.load_data()
                    self.log_message.emit("Inventaris berhasil diupdate")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal mengupdate inventaris: {result}")
                    self.log_message.emit(f"Error update inventaris: {result}")
            else:
                QMessageBox.critical(self, "Error", "Method update_inventaris tidak tersedia")

    def delete_inventaris(self):
        """Hapus inventaris yang dipilih"""
        current_row = self.inventaris_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih inventaris yang akan dihapus")
            return
        
        if current_row >= len(self.inventaris_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return
        
        inventaris_data = self.inventaris_data[current_row]
        nama_barang = inventaris_data.get('nama_barang', 'Unknown')
        
        reply = QMessageBox.question(self, 'Konfirmasi',
                                    f"Yakin ingin menghapus inventaris '{nama_barang}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            inventaris_id = inventaris_data.get('id_inventaris')
            if inventaris_id and hasattr(self.db_manager, 'delete_inventaris'):
                success, result = self.db_manager.delete_inventaris(inventaris_id)
                if success:
                    QMessageBox.information(self, "Sukses", "Inventaris berhasil dihapus.")
                    self.load_data()
                    self.log_message.emit("Inventaris berhasil dihapus")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal menghapus inventaris: {result}")
                    self.log_message.emit(f"Error hapus inventaris: {result}")
            else:
                QMessageBox.critical(self, "Error", "Method delete_inventaris tidak tersedia")

    def export_data(self):
        """Export data inventaris ke file CSV."""
        if not self.inventaris_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Data Inventaris", "data_inventaris.csv", "CSV Files (*.csv)")
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Kode Barang", "Nama Barang", "Kategori", "Merk", "Jumlah", "Satuan",
                    "Harga Satuan", "Tanggal Beli", "Supplier", "Kondisi", "Lokasi",
                    "Penanggung Jawab", "Keterangan"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in self.inventaris_data:
                    writer.writerow({
                        "Kode Barang": item.get('kode_barang', ''),
                        "Nama Barang": item.get('nama_barang', ''),
                        "Kategori": item.get('kategori', ''),
                        "Merk": item.get('merk', ''),
                        "Jumlah": item.get('jumlah', ''),
                        "Satuan": item.get('satuan', ''),
                        "Harga Satuan": item.get('harga_satuan', ''),
                        "Tanggal Beli": item.get('tanggal_beli', ''),
                        "Supplier": item.get('supplier', ''),
                        "Kondisi": item.get('kondisi', ''),
                        "Lokasi": item.get('lokasi', ''),
                        "Penanggung Jawab": item.get('penanggung_jawab', ''),
                        "Keterangan": item.get('keterangan', '')
                    })

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data inventaris diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
            self.log_message.emit(f"Gagal mengekspor data: {str(e)}")
    
    def get_data(self):
        """Ambil data inventaris untuk komponen lain."""
        return self.inventaris_data