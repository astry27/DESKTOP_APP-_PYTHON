# Path: server/components/jadwal.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFileDialog, QGroupBox,
                            QDateEdit, QFormLayout, QAbstractItemView)
from PyQt5.QtCore import QObject, pyqtSignal, QDate

# Import dialog secara langsung untuk menghindari circular import  
from components.dialogs import KegiatanDialog

class JadwalComponent(QWidget):
    """Komponen untuk manajemen jadwal kegiatan"""
    
    data_updated = pyqtSignal()  # Signal ketika data berubah
    log_message = pyqtSignal(str)  # Signal untuk mengirim log message
    
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
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Filter tanggal
        filter_group = self.create_date_filter()
        layout.addWidget(filter_group)
        
        # Tabel Jadwal (hapus kolom ID, tambah kolom deskripsi)
        self.jadwal_table = QTableWidget(0, 6)
        self.jadwal_table.setHorizontalHeaderLabels([
            "Nama Kegiatan", "Deskripsi", "Lokasi", "Tanggal Mulai", 
            "Tanggal Selesai", "Penanggung Jawab"
        ])
        self.jadwal_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.jadwal_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.jadwal_table.setAlternatingRowColors(True)
        
        # Enable context menu untuk edit/hapus
        self.jadwal_table.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        self.jadwal_table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.jadwal_table)
        
        # Tombol aksi
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)
    
    def show_context_menu(self, position):
        """Tampilkan context menu untuk edit/hapus"""
        if self.jadwal_table.rowCount() == 0:
            return
            
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")
        
        action = menu.exec_(self.jadwal_table.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_kegiatan()
        elif action == delete_action:
            self.delete_kegiatan()
    
    def create_header(self):
        """Buat header dengan title dan kontrol"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Jadwal Kegiatan")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_button = self.create_button("Tambah Kegiatan", "#27ae60", self.add_kegiatan)
        header_layout.addWidget(add_button)
        
        return header
    
    def create_date_filter(self):
        """Buat filter tanggal"""
        filter_group = QGroupBox("Filter Tanggal")
        filter_layout = QHBoxLayout(filter_group)
        
        from_date_label = QLabel("Dari:")
        filter_layout.addWidget(from_date_label)
        
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        # Set tanggal awal 1 bulan yang lalu
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.from_date)
        
        to_date_label = QLabel("Sampai:")
        filter_layout.addWidget(to_date_label)
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        # Set tanggal akhir 6 bulan ke depan
        self.to_date.setDate(QDate.currentDate().addMonths(6))
        filter_layout.addWidget(self.to_date)
        
        apply_filter = self.create_button("Terapkan Filter", "#3498db", self.filter_kegiatan)
        filter_layout.addWidget(apply_filter)
        
        show_all_button = self.create_button("Tampilkan Semua", "#9b59b6", self.show_all_kegiatan)
        filter_layout.addWidget(show_all_button)
        
        filter_layout.addStretch()
        
        return filter_group
    
    def create_action_buttons(self):
        """Buat tombol-tombol aksi"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        edit_button = self.create_button("Edit Terpilih", "#f39c12", self.edit_kegiatan)
        action_layout.addWidget(edit_button)
        
        delete_button = self.create_button("Hapus Terpilih", "#c0392b", self.delete_kegiatan)
        action_layout.addWidget(delete_button)
        
        export_button = self.create_button("Export Jadwal", "#16a085", self.export_kegiatan)
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
        """Populate tabel dengan data kegiatan"""
        self.log_message.emit(f"Menampilkan {len(self.kegiatan_data)} kegiatan ke tabel")
        
        # Clear table first
        self.jadwal_table.setRowCount(0)
        
        if not self.kegiatan_data:
            self.log_message.emit("Tidak ada data kegiatan untuk ditampilkan")
            return
        
        for row_index, row_data in enumerate(self.kegiatan_data):
            self.jadwal_table.insertRow(row_index)
            
            # Debug log untuk setiap row
            self.log_message.emit(f"Menambah row {row_index}: {row_data.get('nama_kegiatan', 'No Name')}")
            
            # Kolom 0: Nama Kegiatan
            nama_kegiatan = str(row_data.get('nama_kegiatan', ''))
            self.jadwal_table.setItem(row_index, 0, QTableWidgetItem(nama_kegiatan))
            
            # Kolom 1: Deskripsi
            deskripsi = str(row_data.get('deskripsi', ''))
            # Truncate deskripsi jika terlalu panjang
            if len(deskripsi) > 50:
                deskripsi = deskripsi[:50] + "..."
            self.jadwal_table.setItem(row_index, 1, QTableWidgetItem(deskripsi))
            
            # Kolom 2: Lokasi
            lokasi = str(row_data.get('lokasi', ''))
            self.jadwal_table.setItem(row_index, 2, QTableWidgetItem(lokasi))
            
            # Kolom 3: Tanggal Mulai
            tanggal_mulai = row_data.get('tanggal_mulai')
            tanggal_mulai_str = self.format_date(tanggal_mulai)
            self.jadwal_table.setItem(row_index, 3, QTableWidgetItem(tanggal_mulai_str))
            
            # Kolom 4: Tanggal Selesai
            tanggal_selesai = row_data.get('tanggal_selesai')
            tanggal_selesai_str = self.format_date(tanggal_selesai)
            self.jadwal_table.setItem(row_index, 4, QTableWidgetItem(tanggal_selesai_str))
            
            # Kolom 5: Penanggung Jawab
            penanggungjawab = str(row_data.get('penanggungjawab', ''))
            self.jadwal_table.setItem(row_index, 5, QTableWidgetItem(penanggungjawab))
        
        self.log_message.emit(f"Selesai menampilkan {self.jadwal_table.rowCount()} kegiatan")
    
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
    
    def show_all_kegiatan(self):
        """Tampilkan semua kegiatan tanpa filter tanggal"""
        self.load_data()
    
    def filter_kegiatan(self):
        """Filter kegiatan berdasarkan tanggal"""
        if not self.kegiatan_data:
            self.log_message.emit("Tidak ada data untuk difilter")
            return
        
        try:
            start_date = self.from_date.date().toPyDate()
            end_date = self.to_date.date().toPyDate()
            
            filtered_data = []
            for item in self.kegiatan_data:
                tanggal_mulai = item.get('tanggal_mulai')
                if tanggal_mulai:
                    try:
                        if isinstance(tanggal_mulai, str):
                            import datetime
                            item_date = datetime.datetime.strptime(tanggal_mulai, '%Y-%m-%d').date()
                        elif hasattr(tanggal_mulai, 'date'):
                            item_date = tanggal_mulai.date()
                        else:
                            item_date = tanggal_mulai
                        
                        if start_date <= item_date <= end_date:
                            filtered_data.append(item)
                    except:
                        # Jika error parsing tanggal, masukkan ke hasil filter
                        filtered_data.append(item)
                else:
                    # Jika tidak ada tanggal, masukkan ke hasil filter
                    filtered_data.append(item)
            
            # Simpan data asli dan replace dengan data yang difilter
            original_data = self.kegiatan_data
            self.kegiatan_data = filtered_data
            self.populate_table()
            self.kegiatan_data = original_data  # Restore data asli
            
            self.log_message.emit(f"Filter diterapkan: {len(filtered_data)} dari {len(original_data)} kegiatan")
        except Exception as e:
            self.log_message.emit(f"Error filtering data: {str(e)}")
    
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
        current_row = self.jadwal_table.currentRow()
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
        current_row = self.jadwal_table.currentRow()
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