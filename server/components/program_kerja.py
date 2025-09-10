# Path: server/components/program_kerja.py

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QFrame, QCalendarWidget, QTextEdit, QSplitter, QListWidget, 
                           QListWidgetItem, QGroupBox, QScrollArea, QMessageBox, 
                           QDialog, QFormLayout, QLineEdit, QTextEdit as QTextEditDialog, 
                           QDateEdit, QDialogButtonBox, QComboBox, QSpinBox, QTabWidget,
                           QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QTextCharFormat, QBrush, QIcon
import datetime

# Import existing JadwalComponent
from .jadwal import JadwalComponent

class WorkProgramDialog(QDialog):
    """Dialog untuk menambah/edit program kerja"""
    
    def __init__(self, parent=None, program_data=None):
        super().__init__(parent)
        self.program_data = program_data
        self.setup_ui()
        
        if program_data:
            self.load_data()
    
    def setup_ui(self):
        self.setWindowTitle("Program Kerja" if not self.program_data else "Edit Program Kerja")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Masukkan judul program kerja")
        form_layout.addRow("Judul Program:", self.title_input)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow("Tanggal:", self.date_input)
        
        # Time
        time_layout = QHBoxLayout()
        self.hour_input = QSpinBox()
        self.hour_input.setRange(0, 23)
        self.hour_input.setValue(9)
        self.minute_input = QSpinBox()
        self.minute_input.setRange(0, 59)
        self.minute_input.setValue(0)
        time_layout.addWidget(self.hour_input)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(self.minute_input)
        time_layout.addStretch()
        form_layout.addRow("Waktu:", time_layout)
        
        # Category
        self.category_input = QComboBox()
        self.category_input.addItems([
            "Ibadah", "Kegiatan Sosial", "Rapat", "Pelatihan", 
            "Kunjungan", "Acara Khusus", "Lainnya"
        ])
        form_layout.addRow("Kategori:", self.category_input)
        
        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Tempat kegiatan")
        form_layout.addRow("Lokasi:", self.location_input)
        
        # Description
        self.description_input = QTextEditDialog()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("Deskripsi program kerja")
        form_layout.addRow("Deskripsi:", self.description_input)
        
        # Responsible person (PIC)
        self.responsible_input = QLineEdit()
        self.responsible_input.setPlaceholderText("Person In Charge (PIC)")
        form_layout.addRow("PIC:", self.responsible_input)
        
        # Target audience
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Sasaran/Target peserta")
        form_layout.addRow("Sasaran:", self.target_input)
        
        # Budget amount
        self.budget_amount_input = QLineEdit()
        self.budget_amount_input.setPlaceholderText("Jumlah anggaran (Rp)")
        form_layout.addRow("Jumlah Anggaran:", self.budget_amount_input)
        
        # Budget source
        self.budget_source_input = QComboBox()
        self.budget_source_input.addItems([
            "Kas Gereja", "Donasi Jemaat", "Sponsor External", 
            "Dana Komisi", "APBG", "Kolekte Khusus", "Lainnya"
        ])
        form_layout.addRow("Sumber Anggaran:", self.budget_source_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_data(self):
        """Load data for editing"""
        if not self.program_data:
            return
            
        self.title_input.setText(self.program_data.get('title', ''))
        
        date_str = self.program_data.get('date', '')
        if date_str:
            try:
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                self.date_input.setDate(QDate(date_obj))
            except:
                pass
        
        time_str = self.program_data.get('time', '09:00')
        try:
            hour, minute = time_str.split(':')
            self.hour_input.setValue(int(hour))
            self.minute_input.setValue(int(minute))
        except:
            pass
        
        self.category_input.setCurrentText(self.program_data.get('category', 'Lainnya'))
        self.location_input.setText(self.program_data.get('location', ''))
        self.description_input.setPlainText(self.program_data.get('description', ''))
        self.responsible_input.setText(self.program_data.get('responsible', ''))
        self.target_input.setText(self.program_data.get('target', ''))
        self.budget_amount_input.setText(self.program_data.get('budget_amount', ''))
        self.budget_source_input.setCurrentText(self.program_data.get('budget_source', 'Kas Gereja'))
    
    def get_data(self):
        """Get form data"""
        return {
            'title': self.title_input.text().strip(),
            'date': self.date_input.date().toString('yyyy-MM-dd'),
            'time': f"{self.hour_input.value():02d}:{self.minute_input.value():02d}",
            'category': self.category_input.currentText(),
            'location': self.location_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'responsible': self.responsible_input.text().strip(),
            'target': self.target_input.text().strip(),
            'budget_amount': self.budget_amount_input.text().strip(),
            'budget_source': self.budget_source_input.currentText()
        }

class KalenderKerjaWidget(QWidget):
    """Widget untuk tab Kalender Kerja"""
    
    data_updated = pyqtSignal()
    log_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.work_programs = []
        self.setup_ui()
        self.load_sample_data()
    
    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        if db_manager:
            self.load_data()
    
    def setup_ui(self):
        """Setup UI untuk kalender kerja"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main program list layout only
        main_widget = self.create_main_program_widget()
        layout.addWidget(main_widget)
    
    
    
    def create_main_program_widget(self):
        """Create main program widget with search and filters"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 0, 10, 0)  # Add left and right margins to match jadwal kegiatan
        layout.setSpacing(5)  # Reduce spacing to match jadwal.py
        
        # Header with add button (matching jadwal.py style)
        header = self.create_header()
        layout.addWidget(header)
        
        # Filter section (matching jadwal.py style with QGroupBox)
        filter_group = self.create_month_filter()
        layout.addWidget(filter_group)
        
        # Simple program table only
        table_widget = self.create_simple_program_table()
        layout.addWidget(table_widget)
        
        # Action buttons
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)
        
        return widget
    
    def create_header(self):
        """Buat header dengan kontrol (matching jadwal.py style)"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 5, 10, 5)  # Add right margin for spacing
        
        header_layout.addStretch()
        
        add_button = self.create_button("Tambah Program", "#27ae60", self.add_work_program, "server/assets/tambah.png")
        header_layout.addWidget(add_button)
        
        return header
    
    def create_month_filter(self):
        """Buat filter bulan (exactly matching jadwal.py style)"""
        filter_group = QGroupBox()  # Remove title
        filter_layout = QHBoxLayout(filter_group)
        
        month_label = QLabel("Bulan:")
        filter_layout.addWidget(month_label)
        
        self.month_filter = QComboBox()
        self.populate_month_filter()
        self.month_filter.currentTextChanged.connect(self.filter_programs)
        filter_layout.addWidget(self.month_filter)
        
        apply_filter = self.create_button("Terapkan Filter", "#3498db", self.filter_programs)
        filter_layout.addWidget(apply_filter)
        
        show_all_button = self.create_button("Tampilkan Semua", "#9b59b6", self.show_all_programs)
        filter_layout.addWidget(show_all_button)
        
        filter_layout.addStretch()
        
        return filter_group
    
    def populate_month_filter(self):
        """Populate month filter with all months"""
        months = [
            "Semua Bulan",
            "Januari", "Februari", "Maret", "April", 
            "Mei", "Juni", "Juli", "Agustus",
            "September", "Oktober", "November", "Desember"
        ]
        self.month_filter.addItems(months)
    
    def create_simple_program_table(self):
        """Create simple program table like jadwal.py style"""
        # Program table with simple styling
        self.program_table = QTableWidget(0, 6)
        self.program_table.setHorizontalHeaderLabels([
            "Tanggal", "Perayaan/Program", "Sasaran", "PIC", "Jumlah Anggaran", "Sumber Anggaran"
        ])
        
        # Make headers bold
        header = self.program_table.horizontalHeader()
        font = QFont()
        font.setBold(True)
        header.setFont(font)
        
        # Use stretch mode like jadwal.py
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.program_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.program_table.setAlternatingRowColors(True)
        
        # Enable context menu untuk edit/hapus
        self.program_table.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        self.program_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Connect double click to edit
        self.program_table.itemDoubleClicked.connect(self.edit_program)
        
        return self.program_table
    
    def create_action_buttons(self):
        """Buat tombol-tombol aksi (exactly matching jadwal.py)"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        edit_button = self.create_button("Edit Terpilih", "#f39c12", self.edit_program, "server/assets/edit.png")
        action_layout.addWidget(edit_button)
        
        delete_button = self.create_button("Hapus Terpilih", "#c0392b", self.delete_program, "server/assets/hapus.png")
        action_layout.addWidget(delete_button)
        
        export_button = self.create_button("Export Program", "#16a085", self.export_program, "server/assets/export.png")
        action_layout.addWidget(export_button)
        
        refresh_button = self.create_button("Refresh", "#8e44ad", self.load_data, "server/assets/refresh.png")
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
        """Buat warna lebih gelap untuk hover effect (exactly matching jadwal.py)"""
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
    
    def show_context_menu(self, position):
        """Tampilkan context menu untuk edit/hapus"""
        if self.program_table.rowCount() == 0:
            return
            
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")
        
        action = menu.exec_(self.program_table.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_program()
        elif action == delete_action:
            self.delete_program()
    
    def filter_programs(self):
        """Filter programs based on month filter only"""
        month_filter = self.month_filter.currentText()
        
        filtered_programs = []
        
        for program in self.work_programs:
            # Month filter only
            if month_filter != "Semua Bulan":
                program_date = program.get('date', '')
                if program_date:
                    try:
                        prog_date_obj = datetime.datetime.strptime(program_date, '%Y-%m-%d')
                        # Map Indonesian month names
                        month_names = {
                            1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
                            5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
                            9: "September", 10: "Oktober", 11: "November", 12: "Desember"
                        }
                        prog_month_name = month_names.get(prog_date_obj.month, "")
                        if prog_month_name != month_filter:
                            continue
                    except:
                        continue
            
            filtered_programs.append(program)
        
        self.populate_program_list_filtered(filtered_programs)
    
    def show_all_programs(self):
        """Tampilkan semua program tanpa filter"""
        self.month_filter.setCurrentText("Semua Bulan")
        self.filter_programs()
    
    def populate_program_list_filtered(self, programs):
        """Populate program table with filtered programs"""
        self.program_table.setRowCount(0)
        
        # Sort programs by date and time
        sorted_programs = sorted(programs, key=lambda x: (x.get('date', ''), x.get('time', '')))
        
        for row_idx, program in enumerate(sorted_programs):
            self.program_table.insertRow(row_idx)
            
            # Format date
            date = program.get('date', 'N/A')
            try:
                date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d %b %Y')
            except:
                formatted_date = date
            
            # Create table items with new structure
            date_item = QTableWidgetItem(formatted_date)
            
            # Combine title and time for program column
            program_text = f"{program.get('title', 'N/A')} ({program.get('time', 'N/A')})"
            program_item = QTableWidgetItem(program_text)
            
            target_item = QTableWidgetItem(program.get('target', 'N/A'))
            pic_item = QTableWidgetItem(program.get('responsible', 'N/A'))
            
            # Format budget amount
            budget_amount = program.get('budget_amount', '0')
            if budget_amount and budget_amount.strip():
                try:
                    # Format as currency if it's a number
                    amount = float(budget_amount.replace(',', '').replace('.', ''))
                    budget_formatted = f"Rp {amount:,.0f}".replace(',', '.')
                except:
                    budget_formatted = f"Rp {budget_amount}"
            else:
                budget_formatted = "Rp 0"
            budget_item = QTableWidgetItem(budget_formatted)
            
            budget_source_item = QTableWidgetItem(program.get('budget_source', 'N/A'))
            
            # Store program data in first column
            date_item.setData(Qt.UserRole, program)
            
            # Set items in table
            self.program_table.setItem(row_idx, 0, date_item)
            self.program_table.setItem(row_idx, 1, program_item)
            self.program_table.setItem(row_idx, 2, target_item)
            self.program_table.setItem(row_idx, 3, pic_item)
            self.program_table.setItem(row_idx, 4, budget_item)
            self.program_table.setItem(row_idx, 5, budget_source_item)
        
        # Select first row if available
        if programs and self.program_table.rowCount() > 0:
            self.program_table.selectRow(0)
    
    
    def load_sample_data(self):
        """Initialize empty work programs list - data will be added only when user inputs"""
        self.work_programs = []
        
        # Use the filter approach to populate the empty table
        if hasattr(self, 'program_table'):
            self.filter_programs()
    
    
    def populate_program_list(self, filter_date=None):
        """Populate program list - use filtered approach"""
        if filter_date:
            # Filter by specific date and update the main list
            filtered_programs = [p for p in self.work_programs if p['date'] == filter_date]
            self.populate_program_list_filtered(filtered_programs)
        else:
            # Use the filter_programs method to apply all current filters
            self.filter_programs()
    
    
    def add_work_program(self):
        """Add new work program"""
        dialog = WorkProgramDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            
            # Validation
            if not data['title']:
                QMessageBox.warning(self, "Error", "Judul program harus diisi")
                return
            
            # Add to local data (in real app, save to database)
            new_program = data.copy()
            new_program['id'] = max([p.get('id', 0) for p in self.work_programs] + [0]) + 1
            
            self.work_programs.append(new_program)
            
            # Update UI
            self.filter_programs()  # Use filtered approach
            
            self.log_message.emit(f"Program kerja baru ditambahkan: {data['title']}")
            self.data_updated.emit()
    
    def edit_program(self):
        """Edit selected program"""
        current_row = self.program_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih program yang akan diedit")
            return
        
        date_item = self.program_table.item(current_row, 0)
        if not date_item or not date_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Warning", "Data program tidak valid")
            return
        
        program = date_item.data(Qt.UserRole)
        dialog = WorkProgramDialog(self, program)
        
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            
            # Update program data
            for i, p in enumerate(self.work_programs):
                if p.get('id') == program.get('id'):
                    self.work_programs[i].update(data)
                    break
            
            # Update UI
            self.filter_programs()  # Use filtered approach
            
            self.log_message.emit(f"Program kerja diupdate: {data['title']}")
            self.data_updated.emit()
    
    def delete_program(self):
        """Delete selected program"""
        current_row = self.program_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih program yang akan dihapus")
            return
        
        date_item = self.program_table.item(current_row, 0)
        if not date_item or not date_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Warning", "Data program tidak valid")
            return
        
        program = date_item.data(Qt.UserRole)
        title = program.get('title', 'Program')
        
        reply = QMessageBox.question(self, 'Konfirmasi',
                                   f"Yakin ingin menghapus program '{title}'?",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Remove from data
            self.work_programs = [p for p in self.work_programs if p.get('id') != program.get('id')]
            
            # Update UI
            self.filter_programs()  # Use filtered approach
            
            self.log_message.emit(f"Program kerja dihapus: {title}")
            self.data_updated.emit()
    
    def export_program(self):
        """Export program kerja ke CSV (matching jadwal.py functionality)"""
        if not self.work_programs:
            QMessageBox.warning(self, "Warning", "Tidak ada data program untuk diekspor.")
            return

        from PyQt5.QtWidgets import QFileDialog
        import csv
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Program Kerja", "program_kerja.csv", "CSV Files (*.csv)"
        )
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Tanggal", "Perayaan/Program", "Sasaran", "PIC", 
                    "Jumlah Anggaran", "Sumber Anggaran", "Kategori", 
                    "Lokasi", "Deskripsi", "Waktu"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in self.work_programs:
                    writer.writerow({
                        "Tanggal": item.get('date', ''),
                        "Perayaan/Program": item.get('title', ''),
                        "Sasaran": item.get('target', ''),
                        "PIC": item.get('responsible', ''),
                        "Jumlah Anggaran": item.get('budget_amount', ''),
                        "Sumber Anggaran": item.get('budget_source', ''),
                        "Kategori": item.get('category', ''),
                        "Lokasi": item.get('location', ''),
                        "Deskripsi": item.get('description', ''),
                        "Waktu": item.get('time', '')
                    })

            QMessageBox.information(self, "Sukses", f"Data program kerja berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data program kerja diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
            self.log_message.emit(f"Gagal mengekspor data: {str(e)}")
    
    def load_data(self):
        """Load data from database or use sample data"""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia, menggunakan data contoh...")
            self.load_sample_data()
            return
        
        try:
            # TODO: Implement actual database loading when API is available
            # For example: self.work_programs = self.db_manager.get_work_programs()
            
            self.log_message.emit("Memuat data kalender program kerja dari database...")
            
            # For now, use sample data until database methods are implemented
            self.load_sample_data()
            self.log_message.emit("Data kalender program kerja berhasil dimuat")
            
        except Exception as e:
            self.log_message.emit(f"Error loading calendar data: {str(e)}")
            # Fallback to sample data
            self.load_sample_data()
    
    def get_data(self):
        """Get calendar data for other components"""
        return self.work_programs

class ProgramKerjaComponent(QWidget):
    """Komponen utama Program Kerja dengan 2 tab: Kalender Kerja dan Jadwal Kegiatan"""
    
    data_updated = pyqtSignal()
    log_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.setup_ui()
    
    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        
        # Set database manager for both tabs
        self.kalender_widget.set_database_manager(db_manager)
        self.jadwal_widget.set_database_manager(db_manager)
    
    def setup_ui(self):
        """Setup UI dengan tab widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #34495e; color: white; padding: 2px;")
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("Program Kerja")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Sub judul
        subtitle_frame = QFrame()
        subtitle_frame.setStyleSheet("background-color: #f0f0f0; padding: 8px;")
        subtitle_layout = QHBoxLayout(subtitle_frame)
        
        subtitle_label = QLabel("Pusat Penjadwalan dan Manajemen Kegiatan")
        subtitle_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        subtitle_layout.addWidget(subtitle_label)
        subtitle_layout.addStretch()
        
        layout.addWidget(subtitle_frame)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: Daftar Program Kerja
        self.kalender_widget = KalenderKerjaWidget()
        self.tab_widget.addTab(self.kalender_widget, "Daftar Program Kerja")
        
        # Tab 2: Jadwal Kegiatan (existing component)
        self.jadwal_widget = JadwalComponent()
        self.tab_widget.addTab(self.jadwal_widget, "Jadwal Kegiatan")
        
        layout.addWidget(self.tab_widget)
        
        # Connect signals
        self.connect_signals()
        
        # Hide jadwal component header after setup is complete
        self.hide_jadwal_header()
    
    def hide_jadwal_header(self):
        """Hide the header frame of jadwal component when used in tab"""
        try:
            # Find and hide the header frame with the specific style
            layout = self.jadwal_widget.layout()
            if layout:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item and item.widget():
                        widget = item.widget()
                        if (isinstance(widget, QFrame) and 
                            hasattr(widget, 'styleSheet') and 
                            widget.styleSheet() and 
                            "background-color: #34495e" in widget.styleSheet()):
                            widget.hide()
                            break
        except Exception as e:
            # If there's any error, just ignore it
            pass
    
    def connect_signals(self):
        """Connect signals from child widgets"""
        # Connect kalender widget signals
        self.kalender_widget.data_updated.connect(self.data_updated.emit)
        self.kalender_widget.log_message.connect(self.log_message.emit)
        
        # Connect jadwal widget signals
        if hasattr(self.jadwal_widget, 'data_updated'):
            self.jadwal_widget.data_updated.connect(self.data_updated.emit)
        if hasattr(self.jadwal_widget, 'log_message'):
            self.jadwal_widget.log_message.connect(self.log_message.emit)
    
    def get_data(self):
        """Get combined data from both tabs"""
        return {
            'calendar_data': self.kalender_widget.get_data(),
            'schedule_data': self.jadwal_widget.get_data() if hasattr(self.jadwal_widget, 'get_data') else []
        }