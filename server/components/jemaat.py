# Path: server/components/jemaat.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFileDialog, QAbstractItemView, QFrame,
                            QScrollArea, QSplitter)
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPalette, QColor

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
        
        title_label = QLabel("Database Umat")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Original header with buttons
        header = self.create_header()
        layout.addWidget(header)
        
        # Create Excel-like spreadsheet grid with frozen headers and columns
        self.create_spreadsheet_grid(layout)
        
        # Tombol aksi
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)
    
    def show_context_menu(self, position):
        """Tampilkan context menu untuk edit/hapus"""
        sender = self.sender()
        if sender.rowCount() == 0:
            return
            
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")
        view_details_action = menu.addAction("Lihat Detail")
        
        action = menu.exec_(sender.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_jemaat()
        elif action == delete_action:
            self.delete_jemaat()
        elif action == view_details_action:
            self.view_jemaat_details()
    
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
    
    def create_spreadsheet_grid(self, layout):
        """Create simple white table with multi-level headers"""
        # Create container for headers and table
        table_container = QWidget()
        container_layout = QVBoxLayout(table_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Add main header row
        self.create_main_header_row(container_layout)
        
        # Single table with all columns - no splitting or frozen columns
        self.jemaat_table = QTableWidget(0, 32)  # All fields from dialog
        
        # Set up all column headers to match dialog fields exactly
        self.setup_complete_headers()
        
        # Configure simple white table styling
        self.configure_simple_style(self.jemaat_table)
        
        # Enable context menu
        self.jemaat_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.jemaat_table.customContextMenuRequested.connect(self.show_context_menu)
        
        container_layout.addWidget(self.jemaat_table)
        layout.addWidget(table_container)
    
    def create_main_header_row(self, layout):
        """Create main header row with category labels - clean white styling with proper alignment"""
        main_header_frame = QFrame()
        main_header_frame.setFixedHeight(35)
        main_header_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        
        main_header_layout = QHBoxLayout(main_header_frame)
        main_header_layout.setContentsMargins(0, 0, 0, 0)
        main_header_layout.setSpacing(0)
        
        # Define header groups with their column counts (removed colors)
        header_groups = [
            ("DATA DIRI", 15),        # 15 columns: Nama Lengkap to Email
            ("SAKRAMEN BABTIS", 4),   # 4 columns: Status to Nama Babtis
            ("SAKRAMEN EKARISTI", 3),  # 3 columns: Status to Tanggal Komuni
            ("SAKRAMEN KRISMA", 3),    # 3 columns: Status to Tanggal Krisma
            ("SAKRAMEN PERKAWINAN", 6), # 6 columns: Status to Detail
            ("STATUS", 1)             # 1 column: Status Keanggotaan
        ]
        
        # Create main header labels with exact width matching table columns
        for i, (group_name, col_count) in enumerate(header_groups):
            # Calculate exact width to match table columns perfectly
            exact_width = col_count * 120
            
            group_label = QLabel(group_name)
            group_label.setFixedWidth(exact_width)
            group_label.setFixedHeight(35)
            group_label.setAlignment(Qt.AlignCenter)
            
            # Apply border only to the right except for the last header
            border_style = "border-right: 1px solid #e0e0e0;" if i < len(header_groups) - 1 else ""
            
            group_label.setStyleSheet(f"""
                QLabel {{
                    background: white;
                    color: #333;
                    font-weight: bold;
                    font-size: 10px;
                    {border_style}
                    padding: 8px;
                    margin: 0px;
                }}
            """)
            main_header_layout.addWidget(group_label)
        
        # Add stretch to fill remaining space
        main_header_layout.addStretch()
        
        layout.addWidget(main_header_frame)
    
    def setup_complete_headers(self):
        """Setup sub-column headers under main categories with exact width alignment"""
        sub_header_labels = [
            # DATA DIRI (15 columns)
            "Nama Lengkap", "Wilayah Rohani", "Nama Keluarga", "Tempat Lahir", 
            "Tanggal Lahir", "Umur", "Kategori", "Jenis Kelamin", 
            "Hubungan Keluarga", "Pendidikan Terakhir", "Status Pekerjaan", "Detail Pekerjaan",
            "Status Menikah", "Alamat", "Email",
            # SAKRAMEN BABTIS (4 columns)
            "Status Babtis", "Tempat Babtis", "Tanggal Babtis", "Nama Babtis",
            # SAKRAMEN EKARISTI (3 columns)
            "Status Ekaristi", "Tempat Komuni", "Tanggal Komuni",
            # SAKRAMEN KRISMA (3 columns)
            "Status Krisma", "Tempat Krisma", "Tanggal Krisma",
            # SAKRAMEN PERKAWINAN (6 columns)
            "Status Perkawinan", "Keuskupan", "Paroki", "Kota Perkawinan", 
            "Tanggal Perkawinan", "Status Perkawinan Detail",
            # STATUS (1 column)
            "Status Keanggotaan"
        ]
        
        self.jemaat_table.setHorizontalHeaderLabels(sub_header_labels)
        
        # Set exact column widths to match main header calculations
        column_width = 120
        for i in range(len(sub_header_labels)):
            self.jemaat_table.setColumnWidth(i, column_width)
        
        # Ensure horizontal header is visible and properly styled
        horizontal_header = self.jemaat_table.horizontalHeader()
        horizontal_header.setVisible(True)
        horizontal_header.setStretchLastSection(False)
        horizontal_header.setSectionResizeMode(QHeaderView.Fixed)
    
    def configure_simple_style(self, table):
        """Configure table with simple white styling"""
        # Basic table settings
        table.setAlternatingRowColors(True)
        table.setGridStyle(Qt.SolidLine)
        table.setShowGrid(True)
        
        # Simple white styling
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #fafafa;
                selection-background-color: #b3d9ff;
                selection-color: black;
                border: 1px solid #e0e0e0;
            }
            QTableWidget::item {
                padding: 6px 8px;
                border: none;
                font-size: 9pt;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTableWidget::item:selected {
                background: #b3d9ff;
                color: black;
            }
            QHeaderView::section {
                background: white;
                border: 1px solid #e0e0e0;
                padding: 8px;
                font-weight: bold;
                font-size: 9pt;
                color: #333;
            }
            QHeaderView::section:hover {
                background: #f5f5f5;
            }
        """)
        
        # Row selection behavior
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Set default row height
        table.verticalHeader().setDefaultSectionSize(32)
        table.verticalHeader().setVisible(True)
        table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background: white;
                border: 1px solid #e0e0e0;
                padding: 4px;
                font-size: 8pt;
                color: #666;
                text-align: center;
                min-width: 30px;
            }
        """)
    
    
    def populate_table(self):
        """Populate table with all complete data matching dialog fields"""
        self.jemaat_table.setRowCount(0)
        
        for row_data in self.jemaat_data:
            row_pos = self.jemaat_table.rowCount()
            self.jemaat_table.insertRow(row_pos)
            
            # All columns matching dialog fields exactly in order
            data_items = [
                # DATA DIRI (15 columns)
                str(row_data.get('nama_lengkap', '')),
                str(row_data.get('wilayah_rohani', '')),
                str(row_data.get('nama_keluarga', '')),
                str(row_data.get('tempat_lahir', '')),
                self.format_date(row_data.get('tanggal_lahir')),
                str(row_data.get('umur', '')),
                str(row_data.get('kategori', '')),
                self.format_gender(row_data.get('jenis_kelamin', '')),
                str(row_data.get('hubungan_keluarga', '')),
                str(row_data.get('pendidikan_terakhir', '')),
                str(row_data.get('jenis_pekerjaan', '')),
                str(row_data.get('detail_pekerjaan', '')),
                str(row_data.get('status_menikah', '')),
                str(row_data.get('alamat', '')),
                str(row_data.get('email', '')),
                # SAKRAMEN BABTIS (4 columns)
                str(row_data.get('status_babtis', '')),
                str(row_data.get('tempat_babtis', '')),
                self.format_date(row_data.get('tanggal_babtis')),
                str(row_data.get('nama_babtis', '')),
                # SAKRAMEN EKARISTI (3 columns)
                str(row_data.get('status_ekaristi', '')),
                str(row_data.get('tempat_komuni', '')),
                self.format_date(row_data.get('tanggal_komuni')),
                # SAKRAMEN KRISMA (3 columns)
                str(row_data.get('status_krisma', '')),
                str(row_data.get('tempat_krisma', '')),
                self.format_date(row_data.get('tanggal_krisma')),
                # SAKRAMEN PERKAWINAN (6 columns)
                str(row_data.get('status_perkawinan', '')),
                str(row_data.get('keuskupan', '')),
                str(row_data.get('paroki', '')),
                str(row_data.get('kota_perkawinan', '')),
                self.format_date(row_data.get('tanggal_perkawinan')),
                str(row_data.get('status_perkawinan_detail', '')),
                # STATUS (1 column)
                str(row_data.get('status_keanggotaan', 'Aktif'))
            ]
            
            for col, item_text in enumerate(data_items):
                item = QTableWidgetItem(item_text)
                self.jemaat_table.setItem(row_pos, col, item)
    
    def format_date(self, date_value):
        """Format date for display in spreadsheet"""
        if not date_value:
            return ''
        if hasattr(date_value, 'strftime'):
            return date_value.strftime('%d/%m/%Y')
        return str(date_value)
    
    def format_gender(self, gender):
        """Format gender for display"""
        if gender == 'Laki-laki':
            return 'L'
        elif gender == 'Perempuan':
            return 'P'
        return str(gender)
    
    
    def add_jemaat(self):
        """Tambah jemaat baru"""
        dialog = JemaatDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            
            # Validasi
            if not data['nama_lengkap']:
                QMessageBox.warning(self, "Error", "Nama lengkap harus diisi")
                return
            
            if not data['jenis_kelamin']:
                QMessageBox.warning(self, "Error", "Jenis kelamin harus dipilih")
                return
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            try:
                # Filter data untuk compatibility dengan API yang ada
                # Hanya kirim field yang sudah ada di database lama
                filtered_data = {
                    'nama_lengkap': data.get('nama_lengkap', ''),
                    'alamat': data.get('alamat', ''),
                    'email': data.get('email', ''),
                    'tanggal_lahir': data.get('tanggal_lahir', ''),
                    'jenis_kelamin': 'Laki-laki' if data.get('jenis_kelamin') == 'L' else 'Perempuan'
                }
                
                success, result = self.db_manager.add_jemaat(filtered_data)
                
                if success:
                    QMessageBox.information(self, "Sukses", "Data jemaat berhasil ditambahkan")
                    self.load_data()
                    self.log_message.emit(f"Jemaat baru ditambahkan: {data['nama_lengkap']}")
                    
                    # Inform user about enhanced features
                    QMessageBox.information(self, "Info", 
                        "Data berhasil disimpan! Catatan: Fitur lengkap seperti sakramen dan wilayah rohani "
                        "akan tersedia setelah database server diupdate dengan schema terbaru.")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal menambahkan jemaat: {result}")
                    self.log_message.emit(f"Error adding jemaat: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error menambahkan jemaat: {str(e)}")
                self.log_message.emit(f"Exception adding jemaat: {str(e)}")
    
    def get_selected_row(self):
        """Get currently selected row index"""
        return self.jemaat_table.currentRow()
    
    def edit_jemaat(self):
        """Edit jemaat terpilih"""
        current_row = self.get_selected_row()
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
            
            if not data['jenis_kelamin']:
                QMessageBox.warning(self, "Error", "Jenis kelamin harus dipilih")
                return
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            try:
                # Filter data untuk compatibility dengan API yang ada
                # Hanya kirim field yang sudah ada di database lama
                filtered_data = {
                    'nama_lengkap': data.get('nama_lengkap', ''),
                    'alamat': data.get('alamat', ''),
                    'email': data.get('email', ''),
                    'tanggal_lahir': data.get('tanggal_lahir', ''),
                    'jenis_kelamin': 'Laki-laki' if data.get('jenis_kelamin') == 'L' else 'Perempuan'
                }
                
                id_jemaat = jemaat_data['id_jemaat']
                success, result = self.db_manager.update_jemaat(id_jemaat, filtered_data)
                
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
        current_row = self.get_selected_row()
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
                    fieldnames = [
                        'Nama Lengkap', 'Wilayah Rohani', 'Nama Keluarga', 'Tempat Lahir', 
                        'Tanggal Lahir', 'Jenis Kelamin', 'Hubungan Keluarga', 'Pendidikan Terakhir',
                        'Jenis Pekerjaan', 'Detail Pekerjaan', 'Status Menikah', 'Alamat', 'Email',
                        'Status Babtis', 'Tempat Babtis', 'Tanggal Babtis', 'Nama Babtis',
                        'Status Ekaristi', 'Tempat Komuni', 'Tanggal Komuni',
                        'Status Krisma', 'Tempat Krisma', 'Tanggal Krisma',
                        'Status Perkawinan', 'Keuskupan', 'Paroki', 'Kota Perkawinan', 
                        'Tanggal Perkawinan', 'Status Perkawinan Detail', 'Status Keanggotaan'
                    ]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for data in self.jemaat_data:
                        writer.writerow({
                            'Nama Lengkap': data.get('nama_lengkap', ''),
                            'Wilayah Rohani': data.get('wilayah_rohani', ''),
                            'Nama Keluarga': data.get('nama_keluarga', ''),
                            'Tempat Lahir': data.get('tempat_lahir', ''),
                            'Tanggal Lahir': str(data.get('tanggal_lahir', '')),
                            'Jenis Kelamin': data.get('jenis_kelamin', ''),
                            'Hubungan Keluarga': data.get('hubungan_keluarga', ''),
                            'Pendidikan Terakhir': data.get('pendidikan_terakhir', ''),
                            'Jenis Pekerjaan': data.get('jenis_pekerjaan', ''),
                            'Detail Pekerjaan': data.get('detail_pekerjaan', ''),
                            'Status Menikah': data.get('status_menikah', ''),
                            'Alamat': data.get('alamat', ''),
                            'Email': data.get('email', ''),
                            'Status Babtis': data.get('status_babtis', ''),
                            'Tempat Babtis': data.get('tempat_babtis', ''),
                            'Tanggal Babtis': str(data.get('tanggal_babtis', '')),
                            'Nama Babtis': data.get('nama_babtis', ''),
                            'Status Ekaristi': data.get('status_ekaristi', ''),
                            'Tempat Komuni': data.get('tempat_komuni', ''),
                            'Tanggal Komuni': str(data.get('tanggal_komuni', '')),
                            'Status Krisma': data.get('status_krisma', ''),
                            'Tempat Krisma': data.get('tempat_krisma', ''),
                            'Tanggal Krisma': str(data.get('tanggal_krisma', '')),
                            'Status Perkawinan': data.get('status_perkawinan', ''),
                            'Keuskupan': data.get('keuskupan', ''),
                            'Paroki': data.get('paroki', ''),
                            'Kota Perkawinan': data.get('kota_perkawinan', ''),
                            'Tanggal Perkawinan': str(data.get('tanggal_perkawinan', '')),
                            'Status Perkawinan Detail': data.get('status_perkawinan_detail', ''),
                            'Status Keanggotaan': data.get('status_keanggotaan', '')
                        })
                
                QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
                self.log_message.emit(f"Data jemaat diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error export data: {str(e)}")
            self.log_message.emit(f"Exception exporting jemaat: {str(e)}")
    
    def view_jemaat_details(self):
        """View detailed information of selected jemaat"""
        current_row = self.get_selected_row()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih jemaat untuk melihat detail")
            return
        
        if current_row >= len(self.jemaat_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return
        
        jemaat_data = self.jemaat_data[current_row]
        nama = jemaat_data.get('nama_lengkap', 'Unknown')
        
        # Create detailed view dialog
        from PyQt5.QtWidgets import QDialog, QTextEdit, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detail Jemaat - {nama}")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Create text display for all data
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Format all data nicely
        details = f"""
<h2>DETAIL JEMAAT</h2>
<h3>DATA DIRI</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Nama Lengkap:</b></td><td>{jemaat_data.get('nama_lengkap', '')}</td></tr>
<tr><td><b>Wilayah Rohani:</b></td><td>{jemaat_data.get('wilayah_rohani', '')}</td></tr>
<tr><td><b>Nama Keluarga:</b></td><td>{jemaat_data.get('nama_keluarga', '')}</td></tr>
<tr><td><b>Tempat Lahir:</b></td><td>{jemaat_data.get('tempat_lahir', '')}</td></tr>
<tr><td><b>Tanggal Lahir:</b></td><td>{self.format_date(jemaat_data.get('tanggal_lahir'))}</td></tr>
<tr><td><b>Umur:</b></td><td>{jemaat_data.get('umur', '')}</td></tr>
<tr><td><b>Kategori:</b></td><td>{jemaat_data.get('kategori', '')}</td></tr>
<tr><td><b>Jenis Kelamin:</b></td><td>{jemaat_data.get('jenis_kelamin', '')}</td></tr>
<tr><td><b>Hubungan Keluarga:</b></td><td>{jemaat_data.get('hubungan_keluarga', '')}</td></tr>
<tr><td><b>Pendidikan Terakhir:</b></td><td>{jemaat_data.get('pendidikan_terakhir', '')}</td></tr>
<tr><td><b>Status Menikah:</b></td><td>{jemaat_data.get('status_menikah', '')}</td></tr>
<tr><td><b>Status Pekerjaan:</b></td><td>{jemaat_data.get('jenis_pekerjaan', '')}</td></tr>
</table>

<h3>SAKRAMEN</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Status Babtis:</b></td><td>{jemaat_data.get('status_babtis', '')}</td></tr>
<tr><td><b>Tempat Babtis:</b></td><td>{jemaat_data.get('tempat_babtis', '')}</td></tr>
<tr><td><b>Tanggal Babtis:</b></td><td>{self.format_date(jemaat_data.get('tanggal_babtis'))}</td></tr>
<tr><td><b>Status Ekaristi:</b></td><td>{jemaat_data.get('status_ekaristi', '')}</td></tr>
<tr><td><b>Tempat Komuni:</b></td><td>{jemaat_data.get('tempat_komuni', '')}</td></tr>
<tr><td><b>Tanggal Komuni:</b></td><td>{self.format_date(jemaat_data.get('tanggal_komuni'))}</td></tr>
<tr><td><b>Status Krisma:</b></td><td>{jemaat_data.get('status_krisma', '')}</td></tr>
<tr><td><b>Tempat Krisma:</b></td><td>{jemaat_data.get('tempat_krisma', '')}</td></tr>
<tr><td><b>Tanggal Krisma:</b></td><td>{self.format_date(jemaat_data.get('tanggal_krisma'))}</td></tr>
</table>

<h3>KONTAK & ALAMAT</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Email:</b></td><td>{jemaat_data.get('email', '')}</td></tr>
<tr><td><b>Alamat:</b></td><td>{jemaat_data.get('alamat', '')}</td></tr>
</table>

<h3>STATUS</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr><td><b>Status Keanggotaan:</b></td><td>{jemaat_data.get('status_keanggotaan', '')}</td></tr>
</table>
        """
        
        text_edit.setHtml(details)
        layout.addWidget(text_edit)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.clicked.connect(dialog.close)
        layout.addWidget(button_box)
        
        dialog.exec_()
    
    def get_data(self):
        """Ambil data jemaat untuk komponen lain"""
        return self.jemaat_data