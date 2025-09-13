# Path: server/components/pengumuman.py

import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QGroupBox, QCheckBox,
                            QTextBrowser, QAbstractItemView, QFrame)
from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtGui import QColor, QIcon, QFont

# Import dialog secara langsung untuk menghindari circular import
from components.dialogs import PengumumanDialog

class PengumumanComponent(QWidget):
    """Komponen untuk manajemen pengumuman"""
    
    data_updated = pyqtSignal()  # Signal ketika data berubah
    log_message = pyqtSignal(str)  # Signal untuk mengirim log message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pengumuman_data = []
        self.db_manager = None
        self.setup_ui()
    
    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
    
    def setup_ui(self):
        """Setup UI untuk halaman pengumuman"""
        layout = QVBoxLayout(self)
        
        # Clean header without background (matching pengaturan style)
        header_frame = QWidget()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 10, 0)

        title_label = QLabel("Manajemen Pengumuman")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header_frame)
        
        # Original header with buttons
        header = self.create_header()
        layout.addWidget(header)
        
        # Filter
        filter_group = self.create_filter()
        layout.addWidget(filter_group)
        
        # Table view untuk daftar pengumuman with proper container
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
        
        self.pengumuman_table = self.create_professional_table()
        table_layout.addWidget(self.pengumuman_table)
        
        layout.addWidget(table_container)
        
        # Tampilan detail pengumuman
        detail_group = QGroupBox("Detail Pengumuman")
        detail_layout = QVBoxLayout(detail_group)
        
        self.pengumuman_detail = QTextBrowser()
        detail_layout.addWidget(self.pengumuman_detail)
        
        layout.addWidget(detail_group)
        
        # Tombol aksi
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)
    
    def create_professional_table(self):
        """Create table with professional styling."""
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels([
            "Tanggal", "Pembuat", "Sasaran/Tujuan", "Judul Pengumuman", "Isi Pengumuman"
        ])
        
        # Apply professional table styling
        self.apply_professional_table_style(table)
        
        # Set specific column widths
        column_widths = [120, 100, 120, 200, 250]  # Total: 790px
        for i, width in enumerate(column_widths):
            table.setColumnWidth(i, width)
        
        # Set minimum table width to sum of all columns
        table.setMinimumWidth(sum(column_widths) + 50)  # Add padding for scrollbar
        
        # Additional table settings
        table.setWordWrap(True)  # Enable word wrap for content
        table.itemSelectionChanged.connect(self.show_pengumuman_detail)
        
        # Enable context menu
        table.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        table.customContextMenuRequested.connect(self.show_context_menu)
        
        return table
        
    def apply_professional_table_style(self, table):
        """Apply Excel-like table styling with thin grid lines and minimal borders."""
        # Header styling - Excel-like headers
        header_font = QFont()
        header_font.setBold(False)  # Remove bold from headers
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

        # Excel-style header styling
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #d4d4d4;
                border-right: 1px solid #d4d4d4;
                padding: 6px 4px;
                font-weight: normal;
                color: #333333;
                text-align: left;
            }
        """)

        # Excel-style table body styling
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d4d4d4;
                background-color: white;
                border: 1px solid #d4d4d4;
                selection-background-color: #cce7ff;
                font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
                outline: none;
            }
            QTableWidget::item {
                border: none;
                padding: 4px 6px;
                min-height: 20px;
            }
            QTableWidget::item:selected {
                background-color: #cce7ff;
                color: black;
            }
            QTableWidget::item:focus {
                border: 2px solid #0078d4;
                background-color: white;
            }
        """)

        # Excel-style table settings
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # Allow column resizing
        header.setStretchLastSection(False)  # Don't stretch last column
        header.setMinimumSectionSize(50)
        header.setDefaultSectionSize(80)
        # Allow adjustable header height - removed setMaximumHeight constraint

        # Enable scrolling
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Excel-style row settings
        table.verticalHeader().setDefaultSectionSize(25)  # Slightly taller for announcement content
        table.setSelectionBehavior(QAbstractItemView.SelectItems)  # Select individual cells
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(True)  # Show row numbers like Excel
        table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #d4d4d4;
                border-right: 1px solid #d4d4d4;
                padding: 2px;
                font-weight: normal;
                color: #333333;
                text-align: center;
                width: 30px;
            }
        """)

        # Enable grid display with thin lines
        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)

        # Excel-style editing and selection
        table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Set compact size for Excel look
        table.setMinimumHeight(150)
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    def show_context_menu(self, position):
        """Tampilkan context menu untuk edit/hapus"""
        if self.pengumuman_table.rowCount() == 0:
            return
            
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")
        broadcast_action = menu.addAction("Broadcast ke Client")
        
        action = menu.exec_(self.pengumuman_table.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_pengumuman()
        elif action == delete_action:
            self.delete_pengumuman()
        elif action == broadcast_action:
            self.broadcast_pengumuman()
    
    def create_header(self):
        """Buat header dengan kontrol (tanpa title karena sudah ada di header frame)"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 10, 0)  # Add right margin for spacing
        
        header_layout.addStretch()
        
        add_button = self.create_button("Tambah Pengumuman", "#27ae60", self.add_pengumuman, "server/assets/tambah.png")
        header_layout.addWidget(add_button)
        
        return header
    
    def create_filter(self):
        """Buat filter pengumuman"""
        filter_group = QGroupBox("Filter Pengumuman")
        filter_layout = QHBoxLayout(filter_group)
        
        self.active_only = QCheckBox("Hanya Pengumuman Aktif")
        self.active_only.setChecked(True)
        self.active_only.stateChanged.connect(self.load_data)
        filter_layout.addWidget(self.active_only)
        
        filter_layout.addStretch()
        
        return filter_group
    
    def create_action_buttons(self):
        """Buat tombol-tombol aksi"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        edit_button = self.create_button("Edit Terpilih", "#f39c12", self.edit_pengumuman, "server/assets/edit.png")
        action_layout.addWidget(edit_button)
        
        delete_button = self.create_button("Hapus Terpilih", "#c0392b", self.delete_pengumuman, "server/assets/hapus.png")
        action_layout.addWidget(delete_button)
        
        broadcast_button = self.create_button("Broadcast ke Client", "#8e44ad", self.broadcast_pengumuman)
        action_layout.addWidget(broadcast_button)
        
        refresh_button = self.create_button("Refresh", "#3498db", self.load_data, "server/assets/refresh.png")
        action_layout.addWidget(refresh_button)
        
        return action_layout
    
    def create_button(self, text, color, slot, icon_path=None):
        """Buat button dengan style konsisten dan optional icon"""
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
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
                text-align: left;
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
        """Load data pengumuman dari database"""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return
        
        try:
            active_only = self.active_only.isChecked() if hasattr(self, 'active_only') else True
            
            success, result = self.db_manager.get_pengumuman_list(active_only=active_only, limit=1000)
            
            if success:
                self.pengumuman_data = result
                self.populate_table()
                self.log_message.emit(f"Data pengumuman berhasil dimuat: {len(result)} record")
                self.data_updated.emit()
            else:
                self.log_message.emit(f"Error loading pengumuman data: {result}")
                QMessageBox.warning(self, "Error", f"Gagal memuat data pengumuman: {result}")
        except Exception as e:
            self.log_message.emit(f"Exception loading pengumuman data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error loading pengumuman data: {str(e)}")
    
    def populate_table(self):
        """Populate tabel dengan data pengumuman"""
        self.pengumuman_table.setRowCount(0)
        
        for row_data in self.pengumuman_data:
            row_pos = self.pengumuman_table.rowCount()
            self.pengumuman_table.insertRow(row_pos)
            
            # Column 0: Tanggal (format Hari, dd/MM/yyyy)
            # Check different possible date field names for compatibility
            tanggal_value = (row_data.get('tanggal') or 
                           row_data.get('tanggal_mulai') or 
                           row_data.get('tanggal_dibuat'))
            
            if tanggal_value:
                try:
                    if hasattr(tanggal_value, 'strftime'):
                        # If it's a datetime object, format it with day name (Indonesian day names)
                        day_names = {
                            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
                            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
                        }
                        english_day = tanggal_value.strftime('%A')
                        indonesian_day = day_names.get(english_day, english_day)
                        tanggal_display = f"{indonesian_day}, {tanggal_value.strftime('%d/%m/%Y')}"
                    else:
                        # If it's a string, parse and format it
                        if isinstance(tanggal_value, str):
                            try:
                                date_obj = datetime.datetime.strptime(str(tanggal_value), '%Y-%m-%d')
                                day_names = {
                                    'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
                                    'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
                                }
                                english_day = date_obj.strftime('%A')
                                indonesian_day = day_names.get(english_day, english_day)
                                tanggal_display = f"{indonesian_day}, {date_obj.strftime('%d/%m/%Y')}"
                            except:
                                # If parsing fails, just use the string as is
                                tanggal_display = str(tanggal_value)
                        else:
                            tanggal_display = str(tanggal_value)
                except:
                    tanggal_display = str(tanggal_value) if tanggal_value else ''
            else:
                tanggal_display = ''
            
            tanggal_item = QTableWidgetItem(tanggal_display)
            tanggal_item.setTextAlignment(Qt.AlignCenter)
            self.pengumuman_table.setItem(row_pos, 0, tanggal_item)
            
            # Column 1: Pembuat - try various field names for creator
            pembuat = (row_data.get('pembuat') or 
                      row_data.get('dibuat_oleh_nama') or 
                      row_data.get('created_by_name') or 
                      row_data.get('admin_name') or 
                      'System')
            pembuat_item = QTableWidgetItem(str(pembuat))
            pembuat_item.setTextAlignment(Qt.AlignCenter)
            self.pengumuman_table.setItem(row_pos, 1, pembuat_item)
            
            # Column 2: Sasaran/Tujuan - now directly from input field
            sasaran = row_data.get('sasaran', row_data.get('target_audience', row_data.get('kategori', 'Umum')))
            sasaran_item = QTableWidgetItem(str(sasaran))
            sasaran_item.setTextAlignment(Qt.AlignCenter)
            self.pengumuman_table.setItem(row_pos, 2, sasaran_item)
            
            # Column 3: Judul Pengumuman
            judul = str(row_data.get('judul', ''))
            judul_item = QTableWidgetItem(judul)
            judul_item.setToolTip(judul)  # Show full title in tooltip
            self.pengumuman_table.setItem(row_pos, 3, judul_item)
            
            # Column 4: Isi Pengumuman (truncate dan format untuk display)
            isi = str(row_data.get('isi', ''))
            # Remove HTML tags if present and clean text
            import re
            isi_clean = re.sub(r'<[^>]+>', '', isi)  # Remove HTML tags
            isi_clean = isi_clean.strip()
            
            # Truncate for table display but keep reasonable length
            if len(isi_clean) > 150:
                isi_display = isi_clean[:150] + "..."
            else:
                isi_display = isi_clean
                
            isi_item = QTableWidgetItem(isi_display)
            isi_item.setToolTip(isi_clean)  # Show full text in tooltip
            self.pengumuman_table.setItem(row_pos, 4, isi_item)
    
    def determine_status(self, tanggal_mulai, tanggal_selesai):
        """Tentukan status pengumuman berdasarkan tanggal"""
        today = datetime.date.today()
        try:
            if tanggal_mulai and tanggal_selesai:
                if hasattr(tanggal_mulai, 'date'):
                    start = tanggal_mulai.date()
                else:
                    start = datetime.datetime.strptime(str(tanggal_mulai), '%Y-%m-%d').date()
                
                if hasattr(tanggal_selesai, 'date'):
                    end = tanggal_selesai.date()
                else:
                    end = datetime.datetime.strptime(str(tanggal_selesai), '%Y-%m-%d').date()
                
                if today < start:
                    return "Belum Aktif", QColor(255, 255, 200)  # Kuning
                elif start <= today <= end:
                    return "Aktif", QColor(200, 255, 200)  # Hijau
                else:
                    return "Kadaluarsa", QColor(255, 200, 200)  # Merah
            else:
                return "Tidak Diketahui", QColor(240, 240, 240)  # Abu-abu
        except:
            return "Error", QColor(240, 240, 240)
    
    def show_pengumuman_detail(self):
        """Tampilkan detail pengumuman yang dipilih"""
        current_row = self.pengumuman_table.currentRow()
        if current_row < 0 or current_row >= len(self.pengumuman_data):
            self.pengumuman_detail.clear()
            return
        
        pengumuman_data = self.pengumuman_data[current_row]
        
        # Format tanggal untuk detail
        tanggal_value = (pengumuman_data.get('tanggal') or 
                        pengumuman_data.get('tanggal_mulai') or 
                        pengumuman_data.get('tanggal_dibuat'))
        
        if tanggal_value:
            try:
                if hasattr(tanggal_value, 'strftime'):
                    # If it's a datetime object, format it with day name (Indonesian)
                    day_names = {
                        'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
                        'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
                    }
                    english_day = tanggal_value.strftime('%A')
                    indonesian_day = day_names.get(english_day, english_day)
                    periode = f"{indonesian_day}, {tanggal_value.strftime('%d/%m/%Y')}"
                elif isinstance(tanggal_value, str):
                    try:
                        date_obj = datetime.datetime.strptime(str(tanggal_value), '%Y-%m-%d')
                        day_names = {
                            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
                            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
                        }
                        english_day = date_obj.strftime('%A')
                        indonesian_day = day_names.get(english_day, english_day)
                        periode = f"{indonesian_day}, {date_obj.strftime('%d/%m/%Y')}"
                    except:
                        periode = str(tanggal_value)
                else:
                    periode = str(tanggal_value)
            except:
                periode = str(tanggal_value)
        else:
            periode = "Tidak ada tanggal"
        
        sasaran = pengumuman_data.get('sasaran', pengumuman_data.get('target_audience', pengumuman_data.get('kategori', 'Umum')))
        
        html_content = f"""
        <h3>{pengumuman_data.get('judul', 'Tidak ada judul')}</h3>
        <p><b>Tanggal:</b> {periode}</p>
        <p><b>Dibuat oleh:</b> {pengumuman_data.get('pembuat', 'System')}</p>
        <p><b>Sasaran/Tujuan:</b> {sasaran}</p>
        <hr>
        <div>{pengumuman_data.get('isi', 'Tidak ada isi pengumuman')}</div>
        """
        
        self.pengumuman_detail.setHtml(html_content)
    
    def add_pengumuman(self):
        """Tambah pengumuman baru"""
        dialog = PengumumanDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            
            # Validasi
            if not data['judul']:
                QMessageBox.warning(self, "Error", "Judul pengumuman harus diisi")
                return
            
            if not data['isi']:
                QMessageBox.warning(self, "Error", "Isi pengumuman harus diisi")
                return
                
            if not data['sasaran']:
                QMessageBox.warning(self, "Error", "Sasaran/Tujuan harus diisi")
                return
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            try:
                # Tambah informasi admin yang membuat
                data['dibuat_oleh_admin'] = 1  # Default admin ID
                
                # Try to get current user name from database manager or use default
                try:
                    if hasattr(self.db_manager, 'current_user_name'):
                        data['pembuat'] = self.db_manager.current_user_name
                    elif hasattr(self.db_manager, 'get_current_admin'):
                        admin_info = self.db_manager.get_current_admin()
                        if admin_info and isinstance(admin_info, dict):
                            data['pembuat'] = admin_info.get('username', 'Administrator')
                        else:
                            data['pembuat'] = 'Administrator'
                    else:
                        data['pembuat'] = 'Administrator'
                except:
                    data['pembuat'] = 'Administrator'
                
                # Log the data being sent for debugging
                self.log_message.emit(f"Menambahkan pengumuman: {data['judul']} oleh {data['pembuat']} untuk {data['sasaran']}")
                
                success, result = self.db_manager.add_pengumuman(data)
                
                if success:
                    QMessageBox.information(self, "Sukses", 
                        f"Pengumuman '{data['judul']}' berhasil ditambahkan!\n"
                        f"Sasaran: {data['sasaran']}\n"
                        f"Tanggal: {data['tanggal']}")
                    self.load_data()
                    self.log_message.emit(f"Pengumuman baru ditambahkan: {data['judul']} untuk {data['sasaran']}")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal menambahkan pengumuman: {result}")
                    self.log_message.emit(f"Error adding pengumuman: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error menambahkan pengumuman: {str(e)}")
                self.log_message.emit(f"Exception adding pengumuman: {str(e)}")
    
    def edit_pengumuman(self):
        """Edit pengumuman terpilih"""
        current_row = self.pengumuman_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengumuman yang akan diedit")
            return
        
        if current_row >= len(self.pengumuman_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return
        
        pengumuman_data = self.pengumuman_data[current_row]
        
        dialog = PengumumanDialog(self, pengumuman_data)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            
            # Validasi
            if not data['judul']:
                QMessageBox.warning(self, "Error", "Judul pengumuman harus diisi")
                return
            
            if not data['isi']:
                QMessageBox.warning(self, "Error", "Isi pengumuman harus diisi")
                return
                
            if not data['sasaran']:
                QMessageBox.warning(self, "Error", "Sasaran/Tujuan harus diisi")
                return
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            try:
                # Update pengumuman melalui API
                pengumuman_id = pengumuman_data.get('id_pengumuman')
                if not pengumuman_id:
                    QMessageBox.warning(self, "Error", "ID pengumuman tidak ditemukan")
                    return
                
                success, result = self.db_manager.update_pengumuman(pengumuman_id, data)
                
                if success:
                    QMessageBox.information(self, "Sukses", "Pengumuman berhasil diupdate")
                    self.load_data()
                    self.log_message.emit(f"Pengumuman diupdate: {data['judul']}")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal mengupdate pengumuman: {result}")
                    self.log_message.emit(f"Error updating pengumuman: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error mengupdate pengumuman: {str(e)}")
                self.log_message.emit(f"Exception updating pengumuman: {str(e)}")
    
    def delete_pengumuman(self):
        """Hapus pengumuman terpilih"""
        current_row = self.pengumuman_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengumuman yang akan dihapus")
            return
        
        if current_row >= len(self.pengumuman_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return
        
        pengumuman_data = self.pengumuman_data[current_row]
        judul = pengumuman_data.get('judul', 'Unknown')
        
        reply = QMessageBox.question(self, 'Konfirmasi',
                                    f"Yakin ingin menghapus pengumuman '{judul}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            try:
                pengumuman_id = pengumuman_data.get('id_pengumuman')
                if not pengumuman_id:
                    QMessageBox.warning(self, "Error", "ID pengumuman tidak ditemukan")
                    return
                
                success, result = self.db_manager.delete_pengumuman(pengumuman_id)
                
                if success:
                    QMessageBox.information(self, "Sukses", "Pengumuman berhasil dihapus")
                    self.load_data()
                    self.log_message.emit(f"Pengumuman dihapus: {judul}")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal menghapus pengumuman: {result}")
                    self.log_message.emit(f"Error deleting pengumuman: {result}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error menghapus pengumuman: {str(e)}")
                self.log_message.emit(f"Exception deleting pengumuman: {str(e)}")
    
    def broadcast_pengumuman(self):
        """Broadcast pengumuman terpilih ke semua client melalui API"""
        current_row = self.pengumuman_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih pengumuman yang akan dibroadcast")
            return
        
        if current_row >= len(self.pengumuman_data):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return
        
        if not self.db_manager:
            QMessageBox.warning(self, "Warning", "Database manager tidak tersedia!")
            return
        
        # Cek status API dulu
        success, api_status = self.db_manager.get_api_service_status()
        if not success or not api_status.get('api_enabled', False):
            QMessageBox.warning(self, "Warning", "API tidak aktif! Aktifkan API terlebih dahulu.")
            return
        
        pengumuman_data = self.pengumuman_data[current_row]
        judul = pengumuman_data.get('judul', 'Pengumuman')
        isi = pengumuman_data.get('isi', '')
        
        # Truncate isi jika terlalu panjang
        if len(isi) > 200:
            isi = isi[:200] + "..."
        
        message = f"PENGUMUMAN: {judul} - {isi}"
        
        try:
            success, result = self.db_manager.send_broadcast_message(message)
            
            if success:
                QMessageBox.information(self, "Sukses", "Pengumuman berhasil dibroadcast ke semua client melalui API")
                self.log_message.emit(f"Pengumuman dibroadcast via API: {judul}")
            else:
                QMessageBox.warning(self, "Error", f"Gagal broadcast pengumuman: {result}")
                self.log_message.emit(f"Error broadcast pengumuman: {result}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error broadcast pengumuman: {str(e)}")
            self.log_message.emit(f"Exception broadcast pengumuman: {str(e)}")
    
    def get_data(self):
        """Ambil data pengumuman untuk komponen lain"""
        return self.pengumuman_data