# Path: server/components/jemaat.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFileDialog, QAbstractItemView, QFrame)
from PyQt5.QtCore import QObject, pyqtSignal

# Import dialog secara langsung untuk menghindari circular import
from components.dialogs import JemaatDialog

class JemaatComponent(QWidget):
    """Komponen untuk manajemen data jemaat"""
    
    data_updated = pyqtSignal()  # Signal ketika data berubah
    log_message = pyqtSignal(str)  # Signal untuk mengirim log message
    
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
        
        # Header Frame (matching dokumen.py style)
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #34495e; color: white; padding: 2px;")
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("Database Jemaat")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Original header with buttons
        header = self.create_header()
        layout.addWidget(header)
        
        # Tabel Jemaat (hapus kolom ID)
        self.jemaat_table = QTableWidget(0, 6)
        self.jemaat_table.setHorizontalHeaderLabels([
            "Nama Lengkap", "Alamat", "No. Telepon", 
            "Email", "Tanggal Lahir", "Jenis Kelamin"
        ])
        self.jemaat_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.jemaat_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.jemaat_table.setAlternatingRowColors(True)
        
        # Enable context menu untuk edit/hapus
        self.jemaat_table.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        self.jemaat_table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.jemaat_table)
        
        # Tombol aksi
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)
    
    def show_context_menu(self, position):
        """Tampilkan context menu untuk edit/hapus"""
        if self.jemaat_table.rowCount() == 0:
            return
            
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")
        
        action = menu.exec_(self.jemaat_table.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_jemaat()
        elif action == delete_action:
            self.delete_jemaat()
    
    def create_header(self):
        """Buat header dengan kontrol (tanpa title karena sudah ada di header frame)"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        header_layout.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari jemaat...")
        self.search_input.setFixedWidth(250)
        self.search_input.returnPressed.connect(self.search_jemaat)
        header_layout.addWidget(self.search_input)
        
        search_button = self.create_button("Cari", "#3498db", self.search_jemaat)
        header_layout.addWidget(search_button)
        
        add_button = self.create_button("Tambah Jemaat", "#27ae60", self.add_jemaat)
        header_layout.addWidget(add_button)
        
        return header
    
    def create_action_buttons(self):
        """Buat tombol-tombol aksi"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        edit_button = self.create_button("Edit Terpilih", "#f39c12", self.edit_jemaat)
        action_layout.addWidget(edit_button)
        
        delete_button = self.create_button("Hapus Terpilih", "#c0392b", self.delete_jemaat)
        action_layout.addWidget(delete_button)
        
        export_button = self.create_button("Export Data", "#16a085", self.export_jemaat)
        action_layout.addWidget(export_button)
        
        refresh_button = self.create_button("Refresh", "#8e44ad", self.load_data)
        action_layout.addWidget(refresh_button)
        
        return action_layout
    
    def create_button(self, text, color, slot):
        """Buat button dengan style konsisten"""
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
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
    
    def populate_table(self):
        """Populate tabel dengan data jemaat"""
        self.jemaat_table.setRowCount(0)
        
        for row_data in self.jemaat_data:
            row_pos = self.jemaat_table.rowCount()
            self.jemaat_table.insertRow(row_pos)
            
            # Konversi data ke string dengan penanganan None (tanpa kolom ID)
            self.jemaat_table.setItem(row_pos, 0, QTableWidgetItem(str(row_data.get('nama_lengkap', ''))))
            self.jemaat_table.setItem(row_pos, 1, QTableWidgetItem(str(row_data.get('alamat', ''))))
            self.jemaat_table.setItem(row_pos, 2, QTableWidgetItem(str(row_data.get('no_telepon', ''))))
            self.jemaat_table.setItem(row_pos, 3, QTableWidgetItem(str(row_data.get('email', ''))))
            
            # Handle tanggal lahir
            tanggal_lahir = row_data.get('tanggal_lahir')
            if tanggal_lahir:
                if hasattr(tanggal_lahir, 'strftime'):
                    tanggal_str = tanggal_lahir.strftime('%d/%m/%Y')
                else:
                    tanggal_str = str(tanggal_lahir)
            else:
                tanggal_str = ''
                
            self.jemaat_table.setItem(row_pos, 4, QTableWidgetItem(tanggal_str))
            self.jemaat_table.setItem(row_pos, 5, QTableWidgetItem(str(row_data.get('jenis_kelamin', ''))))
    
    def add_jemaat(self):
        """Tambah jemaat baru"""
        dialog = JemaatDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            
            # Validasi
            if not data['nama_lengkap']:
                QMessageBox.warning(self, "Error", "Nama lengkap harus diisi")
                return
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            try:
                success, result = self.db_manager.add_jemaat(data)
                
                if success:
                    QMessageBox.information(self, "Sukses", "Data jemaat berhasil ditambahkan")
                    self.load_data()
                    self.log_message.emit(f"Jemaat baru ditambahkan: {data['nama_lengkap']}")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal menambahkan jemaat: {result}")
                    self.log_message.emit(f"Error adding jemaat: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error menambahkan jemaat: {str(e)}")
                self.log_message.emit(f"Exception adding jemaat: {str(e)}")
    
    def edit_jemaat(self):
        """Edit jemaat terpilih"""
        current_row = self.jemaat_table.currentRow()
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
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            try:
                id_jemaat = jemaat_data['id_jemaat']
                success, result = self.db_manager.update_jemaat(id_jemaat, data)
                
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
        current_row = self.jemaat_table.currentRow()
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
                    fieldnames = ['Nama Lengkap', 'Alamat', 'No. Telepon', 'Email', 'Tanggal Lahir', 'Jenis Kelamin']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for data in self.jemaat_data:
                        writer.writerow({
                            'Nama Lengkap': data.get('nama_lengkap', ''),
                            'Alamat': data.get('alamat', ''),
                            'No. Telepon': data.get('no_telepon', ''),
                            'Email': data.get('email', ''),
                            'Tanggal Lahir': str(data.get('tanggal_lahir', '')),
                            'Jenis Kelamin': data.get('jenis_kelamin', '')
                        })
                
                QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
                self.log_message.emit(f"Data jemaat diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error export data: {str(e)}")
            self.log_message.emit(f"Exception exporting jemaat: {str(e)}")
    
    def get_data(self):
        """Ambil data jemaat untuk komponen lain"""
        return self.jemaat_data