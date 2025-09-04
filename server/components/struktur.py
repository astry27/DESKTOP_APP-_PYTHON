# Path: server/components/struktur.py

import csv
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QGroupBox, QMessageBox, 
                            QFileDialog, QAbstractItemView, QFrame, QLineEdit)
from PyQt5.QtCore import pyqtSignal, QDate, Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont

# Import dialog struktur yang baru
from .dialogs import StrukturDialog

class StrukturComponent(QWidget):
    """Komponen untuk manajemen struktur kepengurusan gereja"""
    
    data_updated = pyqtSignal()
    log_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.struktur_data = []
        self.db_manager = None
        self.church_label = None
        self.church_name_label = None
        self.setup_ui()
        
        # Tidak perlu timer karena menggunakan style tetap
    
    def set_database_manager(self, db_manager):
        """Set database manager."""
        self.db_manager = db_manager
        # Auto load data setelah database manager di-set
        if self.db_manager:
            self.load_data()
    
    def setup_ui(self):
        """Setup UI untuk halaman struktur kepengurusan."""
        layout = QVBoxLayout(self)
        
        # Header Frame (matching dokumen.py style)
        header_frame = QFrame()
        header_frame.setFixedHeight(50)  # Set fixed height to ensure visibility
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e; 
                color: white; 
                border: none;
                margin: 0px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)  # Add proper margins
        
        title_label = QLabel("Struktur Kepengurusan DPP")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px; 
                font-weight: bold; 
                color: white;
                background: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Original header with buttons and search
        header = self.create_header()
        layout.addWidget(header)
        
        # Header Periode Pengurus
        periode_header = self.create_periode_header()
        layout.addWidget(periode_header)
        
        # Table view untuk daftar pengurus
        self.table_widget = self.create_table_view()
        layout.addWidget(self.table_widget)
        
        # Tombol aksi
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)

    def create_header(self):
        """Buat header dengan kontrol pencarian dan tombol tambah."""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search functionality
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari pengurus...")
        self.search_input.setFixedWidth(250)
        self.search_input.returnPressed.connect(self.search_struktur)
        header_layout.addWidget(self.search_input)
        
        search_button = self.create_button("Cari", "#3498db", self.search_struktur)
        header_layout.addWidget(search_button)
        
        clear_button = self.create_button("Reset", "#e67e22", self.clear_search)
        header_layout.addWidget(clear_button)
        
        header_layout.addStretch()
        
        add_button = self.create_button("Tambah Pengurus", "#27ae60", self.add_struktur)
        header_layout.addWidget(add_button)
        
        return header


    def create_periode_header(self):
        """Buat header periode pengurus."""
        header_frame = QFrame()
        header_frame.setStyleSheet("QFrame { background-color: white; border: none; }")
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 15, 0, 15)
        header_layout.setSpacing(8)
        
        # Judul gereja - line 1
        self.church_label = QLabel("Pengurus Dewan Pastoral Paroki")
        self.church_label.setAlignment(Qt.AlignCenter)
        font1 = QFont("Arial", 16, QFont.Bold)
        self.church_label.setFont(font1)
        self.church_label.setStyleSheet("QLabel { color: #2c3e50; }")
        header_layout.addWidget(self.church_label)
        
        # Nama gereja - line 2
        self.church_name_label = QLabel("Santa Maria Ratu Damai, Tomohon Selatan")
        self.church_name_label.setAlignment(Qt.AlignCenter)
        font2 = QFont("Arial", 14, QFont.Bold)
        self.church_name_label.setFont(font2)
        self.church_name_label.setStyleSheet("QLabel { color: #34495e; }")
        header_layout.addWidget(self.church_name_label)
        
        # Info total pengurus
        self.total_pengurus_label = QLabel("Total: 0 pengurus")
        self.total_pengurus_label.setAlignment(Qt.AlignCenter)
        font3 = QFont("Arial", 12)
        self.total_pengurus_label.setFont(font3)
        self.total_pengurus_label.setStyleSheet("QLabel { color: #7f8c8d; }")
        header_layout.addWidget(self.total_pengurus_label)
        
        return header_frame


    def create_table_view(self):
        """Buat tampilan tabel lengkap."""
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels([
            "Foto", "Nama Lengkap", "Jabatan", "Wilayah Rohani", "Informasi Kontak"
        ])
        
        # Set column widths specifically for better display
        table.setColumnWidth(0, 80)   # Foto column - fixed width
        table.setColumnWidth(1, 200)  # Nama Lengkap - wider
        table.setColumnWidth(2, 180)  # Jabatan
        table.setColumnWidth(3, 150)  # Wilayah Rohani
        table.horizontalHeader().setStretchLastSection(True)  # Kontak column stretches
        
        # Set row height for photo display
        table.verticalHeader().setDefaultSectionSize(60)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setAlternatingRowColors(True)
        
        # Enable context menu
        table.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        table.customContextMenuRequested.connect(self.show_context_menu_table)
        
        self.struktur_table = table
        return table


    def show_context_menu_table(self, position):
        """Tampilkan context menu untuk table view"""
        if self.struktur_table.rowCount() == 0:
            return
            
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")
        
        action = menu.exec_(self.struktur_table.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_struktur()
        elif action == delete_action:
            self.delete_struktur()

    def create_action_buttons(self):
        """Buat tombol-tombol aksi."""
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        edit_button = self.create_button("Edit Terpilih", "#f39c12", self.edit_struktur)
        action_layout.addWidget(edit_button)
        
        delete_button = self.create_button("Hapus Terpilih", "#c0392b", self.delete_struktur)
        action_layout.addWidget(delete_button)
        
        org_chart_button = self.create_button("Bagan Organisasi", "#9b59b6", self.show_org_chart)
        action_layout.addWidget(org_chart_button)
        
        export_button = self.create_button("Export Data", "#16a085", self.export_data)
        action_layout.addWidget(export_button)

        refresh_button = self.create_button("Refresh", "#8e44ad", self.load_data)
        action_layout.addWidget(refresh_button)
        
        return action_layout

    def create_button(self, text, color, slot):
        """Buat button dengan style konsisten."""
        button = QPushButton(text)
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
            "#9b59b6": "#8e44ad",  # Purple
            "#2ecc71": "#27ae60",  # Light green
            "#e74c3c": "#c0392b",  # Light red
        }
        return color_map.get(color, color)

    def load_data(self):
        """Load data struktur dari database."""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            # Test koneksi database terlebih dahulu
            if not hasattr(self.db_manager, 'get_struktur_list'):
                self.log_message.emit("Error: Database manager tidak memiliki method get_struktur_list")
                return
            
            # Load struktur dengan search filter jika ada
            search = self.search_input.text().strip() if hasattr(self, 'search_input') else None
            self.log_message.emit("Mencoba memuat data struktur...")
            success, struktur = self.db_manager.get_struktur_list(search=search)
            
            if success:
                # Handle different response formats
                if isinstance(struktur, dict) and 'data' in struktur:
                    self.struktur_data = struktur['data']
                elif isinstance(struktur, list):
                    self.struktur_data = struktur
                else:
                    self.struktur_data = []
                
                self.populate_views()
                self.log_message.emit(f"Data struktur berhasil dimuat: {len(self.struktur_data)} record")
            else:
                self.struktur_data = []
                self.populate_views()
                self.log_message.emit(f"Gagal memuat data struktur: {struktur}")
            
            self.log_message.emit("Proses loading data struktur selesai")
            self.data_updated.emit()
        except Exception as e:
            self.log_message.emit(f"Exception saat memuat data struktur: {str(e)}")
            # Reset data jika terjadi error
            self.struktur_data = []
            self.populate_views()

    def populate_views(self):
        """Populate table view dengan data struktur."""
        self.populate_table_view()
        self.update_total_pengurus()

    def update_total_pengurus(self):
        """Update label total pengurus."""
        total = len(self.struktur_data)
        aktif = len([data for data in self.struktur_data if data.get('status_aktif', '') == 'Aktif'])
        self.total_pengurus_label.setText(f"Total: {total} pengurus ({aktif} aktif)")

    def populate_table_view(self):
        """Populate table view dengan data struktur."""
        self.struktur_table.setRowCount(0)
        
        for row_data in self.struktur_data:
            row_pos = self.struktur_table.rowCount()
            self.struktur_table.insertRow(row_pos)
            
            # Foto - Column 0
            foto_path = row_data.get('foto_path', '')
            foto_item = QTableWidgetItem()
            if foto_path and os.path.exists(foto_path):
                try:
                    pixmap = QPixmap(foto_path)
                    if not pixmap.isNull():
                        # Resize photo to fit in cell (50x50 pixels)
                        scaled_pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        foto_item.setData(Qt.DecorationRole, scaled_pixmap)
                        foto_item.setText("")  # No text, just image
                    else:
                        foto_item.setText("📷")  # Camera icon if image can't load
                except Exception:
                    foto_item.setText("📷")  # Camera icon if error loading
            else:
                foto_item.setText("👤")  # Person icon if no photo
            foto_item.setTextAlignment(Qt.AlignCenter)
            self.struktur_table.setItem(row_pos, 0, foto_item)
            
            # Nama Lengkap dengan gelar - Column 1
            gelar_depan = row_data.get('gelar_depan', '')
            nama_lengkap = row_data.get('nama_lengkap', '')
            gelar_belakang = row_data.get('gelar_belakang', '')
            nama_display = f"{gelar_depan} {nama_lengkap} {gelar_belakang}".strip()
            
            nama_item = QTableWidgetItem(nama_display)
            # Add status klerus as subtitle
            status_klerus = row_data.get('status_klerus', '')
            if status_klerus:
                nama_item.setToolTip(f"Status: {status_klerus}")
            self.struktur_table.setItem(row_pos, 1, nama_item)
            
            # Jabatan dengan level - Column 2
            jabatan = row_data.get('jabatan_utama', '')
            level = row_data.get('level_hierarki', 9)
            level_name = self.get_level_name(level)
            jabatan_display = jabatan
            if jabatan:
                jabatan_display += f"\n({level_name})"
            
            jabatan_item = QTableWidgetItem(jabatan_display)
            jabatan_item.setToolTip(f"Level {level}: {level_name}")
            self.struktur_table.setItem(row_pos, 2, jabatan_item)
            
            # Wilayah Rohani - Column 3
            wilayah_rohani = row_data.get('wilayah_rohani', '')
            bidang_pelayanan = row_data.get('bidang_pelayanan', '')
            wilayah_display = wilayah_rohani
            if not wilayah_display and bidang_pelayanan:
                wilayah_display = f"Bidang: {bidang_pelayanan}"
            
            wilayah_item = QTableWidgetItem(wilayah_display)
            if bidang_pelayanan:
                wilayah_item.setToolTip(f"Bidang Pelayanan: {bidang_pelayanan}")
            self.struktur_table.setItem(row_pos, 3, wilayah_item)
            
            # Informasi Kontak - Column 4
            telepon = row_data.get('telepon', '')
            email = row_data.get('email', '')
            status_aktif = row_data.get('status_aktif', '')
            
            kontak_parts = []
            if telepon:
                kontak_parts.append(f"📞 {telepon}")
            if email:
                kontak_parts.append(f"✉️ {email}")
            if status_aktif:
                status_icon = "🟢" if status_aktif == "Aktif" else "🔴"
                kontak_parts.append(f"{status_icon} {status_aktif}")
            
            kontak_display = "\n".join(kontak_parts) if kontak_parts else "Tidak ada info kontak"
            
            kontak_item = QTableWidgetItem(kontak_display)
            if status_aktif != 'Aktif':
                kontak_item.setBackground(Qt.lightGray)
            self.struktur_table.setItem(row_pos, 4, kontak_item)

    def get_level_name(self, level):
        """Dapatkan nama level berdasarkan nomor."""
        level_names = {
            1: "Pastor Paroki / Pemimpin Tertinggi",
            2: "Wakil Pastor / Asisten Pastor",
            3: "Ketua Dewan",
            4: "Wakil Ketua Dewan",
            5: "Sekretaris",
            6: "Bendahara",
            7: "Koordinator Bidang",
            8: "Anggota Dewan",
            9: "Relawan/Pelayan"
        }
        return level_names.get(level, "Lainnya")
    


    def search_struktur(self):
        """Cari struktur berdasarkan keyword"""
        search_keyword = self.search_input.text().strip()
        
        if not search_keyword:
            # Jika tidak ada keyword, tampilkan semua data
            self.load_data()
            return
        
        # Jika ada keyword, filter data lokal
        if not self.struktur_data:
            self.log_message.emit("Tidak ada data untuk dicari. Load data terlebih dahulu.")
            return
        
        # Filter data berdasarkan keyword
        filtered_data = []
        search_lower = search_keyword.lower()
        
        for data in self.struktur_data:
            # Cari di berbagai field
            nama_lengkap = data.get('nama_lengkap', '').lower()
            jabatan = data.get('jabatan_utama', '').lower()
            wilayah = data.get('wilayah_rohani', '').lower()
            bidang = data.get('bidang_pelayanan', '').lower()
            gelar_depan = data.get('gelar_depan', '').lower()
            gelar_belakang = data.get('gelar_belakang', '').lower()
            status_klerus = data.get('status_klerus', '').lower()
            
            if (search_lower in nama_lengkap or 
                search_lower in jabatan or 
                search_lower in wilayah or 
                search_lower in bidang or
                search_lower in gelar_depan or
                search_lower in gelar_belakang or
                search_lower in status_klerus):
                filtered_data.append(data)
        
        # Simpan data asli dan tampilkan hasil filter
        if not hasattr(self, 'original_struktur_data'):
            self.original_struktur_data = self.struktur_data.copy()
        
        self.struktur_data = filtered_data
        self.populate_views()
        
        self.log_message.emit(f"Pencarian '{search_keyword}': ditemukan {len(filtered_data)} hasil")
    
    def clear_search(self):
        """Clear search dan tampilkan semua data"""
        if hasattr(self, 'original_struktur_data'):
            self.struktur_data = self.original_struktur_data
            self.original_struktur_data = None
            self.populate_views()
        self.search_input.clear()

    def add_struktur(self):
        """Tambah pengurus baru."""
        dialog = StrukturDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            
            # Validasi
            if not data['nama_lengkap']:
                QMessageBox.warning(self, "Error", "Nama lengkap harus diisi")
                return
            
            if not data['jabatan_utama']:
                QMessageBox.warning(self, "Error", "Jabatan utama harus diisi")
                return
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            # Check if method exists
            if not hasattr(self.db_manager, 'add_struktur'):
                QMessageBox.critical(self, "Error", "Method add_struktur tidak tersedia di database manager")
                self.log_message.emit("Method add_struktur tidak tersedia")
                return
            
            self.log_message.emit("Mencoba menambahkan pengurus...")
            success, result = self.db_manager.add_struktur(data)
            if success:
                QMessageBox.information(self, "Sukses", "Pengurus berhasil ditambahkan.")
                self.load_data()
                self.log_message.emit("Pengurus berhasil ditambahkan")
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

    def edit_struktur_by_id(self, data_id):
        """Edit pengurus berdasarkan ID"""
        struktur_data = None
        for data in self.struktur_data:
            if data.get('id_struktur') == data_id:
                struktur_data = data
                break
        
        if struktur_data:
            self.edit_struktur_dialog(struktur_data)

    def edit_struktur_dialog(self, struktur_data):
        """Buka dialog edit dengan data struktur"""
        dialog = StrukturDialog(self, struktur_data)
        if dialog.exec_() == dialog.Accepted:
            updated_data = dialog.get_data()
            
            # Validasi
            if not updated_data['nama_lengkap']:
                QMessageBox.warning(self, "Error", "Nama lengkap harus diisi")
                return
            
            if not updated_data['jabatan_utama']:
                QMessageBox.warning(self, "Error", "Jabatan utama harus diisi")
                return
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            # Update melalui API
            struktur_id = struktur_data.get('id_struktur')
            if struktur_id and hasattr(self.db_manager, 'update_struktur'):
                success, result = self.db_manager.update_struktur(struktur_id, updated_data)
                if success:
                    QMessageBox.information(self, "Sukses", "Pengurus berhasil diupdate.")
                    self.load_data()
                    self.log_message.emit("Pengurus berhasil diupdate")
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

    def delete_struktur_by_id(self, data_id):
        """Hapus pengurus berdasarkan ID"""
        struktur_data = None
        for data in self.struktur_data:
            if data.get('id_struktur') == data_id:
                struktur_data = data
                break
        
        if struktur_data:
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
                    self.log_message.emit("Pengurus berhasil dihapus")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal menghapus pengurus: {result}")
                    self.log_message.emit(f"Error hapus pengurus: {result}")
            else:
                QMessageBox.critical(self, "Error", "Method delete_struktur tidak tersedia")

    def show_org_chart(self):
        """Tampilkan bagan organisasi DPP"""
        if not self.struktur_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data struktur untuk ditampilkan.")
            return
        
        # Import dialog bagan organisasi
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget
            from PyQt5.QtCore import QRectF
            from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
            
            # Buat dialog untuk menampilkan bagan organisasi
            dialog = QDialog(self)
            dialog.setWindowTitle("Bagan Organisasi DPP - Santa Maria Ratu Damai")
            dialog.setModal(True)
            dialog.resize(1000, 700)
            
            layout = QVBoxLayout(dialog)
            
            # Header info
            header_label = QLabel(f"Bagan Organisasi DPP\nSanta Maria Ratu Damai, Tomohon Selatan\nTotal: {len(self.struktur_data)} pengurus")
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; margin: 10px; }")
            layout.addWidget(header_label)
            
            # Scroll area untuk bagan
            scroll_area = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            
            # Kelompokkan data berdasarkan level hierarki
            levels = {}
            for data in self.struktur_data:
                level = data.get('level_hierarki', 9)
                if level not in levels:
                    levels[level] = []
                levels[level].append(data)
            
            # Tampilkan per level (1 = tertinggi)
            for level in sorted(levels.keys()):
                level_frame = QFrame()
                level_frame.setStyleSheet("""
                    QFrame {
                        background-color: #f8f9fa;
                        border: 2px solid #dee2e6;
                        border-radius: 8px;
                        margin: 5px;
                        padding: 10px;
                    }
                """)
                
                level_layout = QVBoxLayout(level_frame)
                
                # Header level
                level_name = self.get_level_name(level)
                level_header = QLabel(f"Level {level}: {level_name}")
                level_header.setAlignment(Qt.AlignCenter)
                level_header.setStyleSheet("""
                    QLabel {
                        background-color: #34495e;
                        color: white;
                        font-weight: bold;
                        font-size: 12px;
                        padding: 8px;
                        border-radius: 4px;
                    }
                """)
                level_layout.addWidget(level_header)
                
                # Grid untuk anggota di level ini
                members_frame = QFrame()
                members_layout = QHBoxLayout(members_frame)
                members_layout.setSpacing(10)
                
                for person in levels[level]:
                    person_widget = self.create_person_widget(person)
                    members_layout.addWidget(person_widget)
                
                if not levels[level]:
                    no_member = QLabel("Tidak ada pengurus")
                    no_member.setAlignment(Qt.AlignCenter)
                    no_member.setStyleSheet("color: #7f8c8d; font-style: italic;")
                    members_layout.addWidget(no_member)
                
                members_layout.addStretch()
                level_layout.addWidget(members_frame)
                scroll_layout.addWidget(level_frame)
            
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            layout.addWidget(scroll_area)
            
            # Tombol tutup
            close_button = QPushButton("Tutup")
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menampilkan bagan organisasi: {str(e)}")
            self.log_message.emit(f"Error bagan organisasi: {str(e)}")
    
    def create_person_widget(self, person_data):
        """Buat widget untuk menampilkan informasi pengurus"""
        widget = QFrame()
        widget.setFixedSize(180, 120)
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 5px;
            }
            QFrame:hover {
                border-color: #2980b9;
                background-color: #ecf0f1;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(3)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Nama dengan gelar
        gelar_depan = person_data.get('gelar_depan', '')
        nama_lengkap = person_data.get('nama_lengkap', '')
        gelar_belakang = person_data.get('gelar_belakang', '')
        nama_display = f"{gelar_depan} {nama_lengkap} {gelar_belakang}".strip()
        
        nama_label = QLabel(nama_display)
        nama_label.setAlignment(Qt.AlignCenter)
        nama_label.setWordWrap(True)
        nama_label.setStyleSheet("QLabel { font-weight: bold; font-size: 10px; color: #2c3e50; }")
        layout.addWidget(nama_label)
        
        # Jabatan
        jabatan = person_data.get('jabatan_utama', '')
        jabatan_label = QLabel(jabatan)
        jabatan_label.setAlignment(Qt.AlignCenter)
        jabatan_label.setWordWrap(True)
        jabatan_label.setStyleSheet("QLabel { font-size: 9px; color: #34495e; }")
        layout.addWidget(jabatan_label)
        
        # Wilayah/Bidang
        wilayah = person_data.get('wilayah_rohani', '')
        bidang = person_data.get('bidang_pelayanan', '')
        area_text = wilayah if wilayah else f"Bidang: {bidang}" if bidang else ""
        
        if area_text:
            area_label = QLabel(area_text)
            area_label.setAlignment(Qt.AlignCenter)
            area_label.setWordWrap(True)
            area_label.setStyleSheet("QLabel { font-size: 8px; color: #7f8c8d; }")
            layout.addWidget(area_label)
        
        # Status
        status = person_data.get('status_aktif', '')
        if status:
            status_color = "#27ae60" if status == "Aktif" else "#e74c3c"
            status_label = QLabel(f"● {status}")
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setStyleSheet(f"QLabel {{ font-size: 8px; color: {status_color}; font-weight: bold; }}")
            layout.addWidget(status_label)
        
        return widget

    def export_data(self):
        """Export data struktur ke file CSV."""
        if not self.struktur_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Data Struktur", "struktur_kepengurusan.csv", "CSV Files (*.csv)")
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Nama Lengkap", "Gelar Depan", "Gelar Belakang", "Jenis Kelamin", 
                    "Tanggal Lahir", "Status Klerus", "Wilayah Rohani", "Level Hierarki", "Jabatan Utama",
                    "Bidang Pelayanan", "Tanggal Mulai", "Tanggal Berakhir", "Deskripsi Tugas",
                    "Status Aktif", "Email", "Telepon", "Alamat", "Foto Path"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in self.struktur_data:
                    writer.writerow({
                        "Nama Lengkap": item.get('nama_lengkap', ''),
                        "Gelar Depan": item.get('gelar_depan', ''),
                        "Gelar Belakang": item.get('gelar_belakang', ''),
                        "Jenis Kelamin": item.get('jenis_kelamin', ''),
                        "Tanggal Lahir": item.get('tanggal_lahir', ''),
                        "Status Klerus": item.get('status_klerus', ''),
                        "Wilayah Rohani": item.get('wilayah_rohani', ''),
                        "Level Hierarki": f"{item.get('level_hierarki', '')} - {self.get_level_name(item.get('level_hierarki', 9))}",
                        "Jabatan Utama": item.get('jabatan_utama', ''),
                        "Bidang Pelayanan": item.get('bidang_pelayanan', ''),
                        "Tanggal Mulai": item.get('tanggal_mulai_jabatan', ''),
                        "Tanggal Berakhir": item.get('tanggal_berakhir_jabatan', ''),
                        "Deskripsi Tugas": item.get('deskripsi_tugas', ''),
                        "Status Aktif": item.get('status_aktif', ''),
                        "Email": item.get('email', ''),
                        "Telepon": item.get('telepon', ''),
                        "Alamat": item.get('alamat', ''),
                        "Foto Path": item.get('foto_path', '')
                    })

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data struktur diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
            self.log_message.emit(f"Gagal mengekspor data: {str(e)}")
    
    def get_data(self):
        """Ambil data struktur untuk komponen lain."""
        return self.struktur_data