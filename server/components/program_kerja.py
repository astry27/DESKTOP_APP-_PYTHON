# Path: server/components/program_kerja.py

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QFrame, QCalendarWidget, QTextEdit, QSplitter, QListWidget, 
                           QListWidgetItem, QGroupBox, QScrollArea, QMessageBox, 
                           QDialog, QFormLayout, QLineEdit, QTextEdit as QTextEditDialog, 
                           QDateEdit, QDialogButtonBox, QComboBox, QSpinBox, QTabWidget,
                           QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                           QFileDialog, QMenu)
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
        self.setFixedSize(450, 300)  # Ukuran lebih kecil karena field lebih sedikit
        
        layout = QVBoxLayout(self)
        
        # Form layout - hanya field yang sesuai dengan kolom tabel
        form_layout = QFormLayout()

        # Tanggal (hanya format tanggal saja)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")  # Format tanggal saja
        form_layout.addRow("Tanggal:", self.date_input)

        # Perayaan/Program (Judul Program yang akan direncanakan)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Masukkan judul program/perayaan")
        form_layout.addRow("Perayaan/Program:", self.title_input)

        # Sasaran (tujuan dari program/tokoh yang dituju)
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Sasaran/tujuan program atau tokoh yang dituju")
        form_layout.addRow("Sasaran:", self.target_input)

        # PIC (penanggung jawab)
        self.responsible_input = QLineEdit()
        self.responsible_input.setPlaceholderText("Person In Charge (PIC)")
        form_layout.addRow("PIC:", self.responsible_input)

        # Anggaran
        self.budget_amount_input = QLineEdit()
        self.budget_amount_input.setPlaceholderText("Jumlah anggaran (Rp)")
        form_layout.addRow("Anggaran:", self.budget_amount_input)

        # Sumber Anggaran
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
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
        layout.addWidget(button_box)
    
    def load_data(self):
        """Load data for editing"""
        if not self.program_data:
            return

        # Load date
        date_str = self.program_data.get('date', '')
        if date_str:
            try:
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                self.date_input.setDate(QDate(date_obj))
            except:
                pass

        # Load program title
        self.title_input.setText(self.program_data.get('title', ''))

        # Load target/sasaran
        self.target_input.setText(self.program_data.get('target', ''))

        # Load PIC
        self.responsible_input.setText(self.program_data.get('responsible', ''))

        # Load budget amount
        self.budget_amount_input.setText(self.program_data.get('budget_amount', ''))

        # Load budget source
        self.budget_source_input.setCurrentText(self.program_data.get('budget_source', 'Kas Gereja'))
    
    def get_data(self):
        """Get form data sesuai dengan kolom tabel"""
        return {
            'date': self.date_input.date().toString('yyyy-MM-dd'),
            'title': self.title_input.text().strip(),
            'target': self.target_input.text().strip(),
            'responsible': self.responsible_input.text().strip(),
            'budget_amount': self.budget_amount_input.text().strip(),
            'budget_source': self.budget_source_input.currentText()
        }

class KalenderKerjaWidget(QWidget):
    """Widget untuk tab Kalender Kerja"""

    data_updated = pyqtSignal()
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore
    
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
        """Create main program widget with search and filters that fills the layout"""
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

        # Simple program table only - with stretch factor to fill space
        table_widget = self.create_simple_program_table()
        layout.addWidget(table_widget, 1)  # Add stretch factor 1 to make table expand

        # Action buttons - fixed size, no stretch
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout, 0)  # No stretch for action buttons

        return widget
    
    def create_action_buttons(self):
        """Create action buttons layout"""
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 5, 0, 5)
        
        # Edit button
        edit_button = self.create_button("Edit Program", "#3498db", self.edit_program)
        action_layout.addWidget(edit_button)
        
        # Delete button  
        delete_button = self.create_button("Hapus Program", "#c0392b", self.delete_program)
        action_layout.addWidget(delete_button)
        
        # Export button
        export_button = self.create_button("Export CSV", "#f39c12", self.export_program)
        action_layout.addWidget(export_button)
        
        action_layout.addStretch()
        return action_layout
    
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
        """Create simple program table with professional styling that fills layout - matching struktur.py style"""
        # Table view untuk daftar program with proper container (exactly matching struktur.py)
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

        self.program_table = self.create_professional_table()
        table_layout.addWidget(self.program_table)

        return table_container
        
    def create_professional_table(self):
        """Create table with professional styling."""
        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels([
            "Tanggal", "Perayaan/Program", "Sasaran", "PIC", "Anggaran", "Sumber Anggaran"
        ])
        
        # Apply professional table styling
        self.apply_professional_table_style(table)

        # Set initial column widths with better proportions for full layout
        table.setColumnWidth(0, 100)   # Tanggal
        table.setColumnWidth(1, 280)   # Perayaan/Program - wider for content
        table.setColumnWidth(2, 160)   # Sasaran
        table.setColumnWidth(3, 120)   # PIC
        table.setColumnWidth(4, 130)   # Anggaran
        table.setColumnWidth(5, 160)   # Sumber Anggaran - wider for dropdown text

        # Excel-like column resizing - all columns can be resized (matching struktur.py)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # All columns resizable
        header.setStretchLastSection(True)  # Last column stretches to fill space

        # Enable context menu
        table.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        table.customContextMenuRequested.connect(self.show_context_menu)

        # Connect double click to edit
        table.itemDoubleClicked.connect(self.edit_program)
        
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
                color: black;
            }
            QTableWidget::item {
                border: none;
                padding: 4px 6px;
                min-height: 18px;
                color: black;
            }
            QTableWidget::item:selected {
                background-color: #cce7ff;
                color: black;
            }
            QTableWidget::item:focus {
                border: 2px solid #0078d4;
                background-color: white;
                color: black;
            }
        """)

        # Excel-style table settings (matching struktur.py exactly)
        header = table.horizontalHeader()
        header.setMinimumSectionSize(50)
        header.setDefaultSectionSize(80)
        # Allow adjustable header height - removed setMaximumHeight constraint

        # Enable scrolling
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Excel-style row settings with better content visibility
        table.verticalHeader().setDefaultSectionSize(24)  # Slightly taller for program content
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

        # Set proper size for Excel look with better visibility
        table.setMinimumHeight(200)
        table.setSizePolicy(table.sizePolicy().Expanding, table.sizePolicy().Expanding)
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
    
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
        
        return action_layout
    
    def create_button(self, text, color, slot, icon_path=None):
        """Buat button dengan style konsisten dan optional icon matching sidebar menu buttons"""
        button = QPushButton(text)

        # Add icon if specified and path exists
        if icon_path:
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(20, 20))  # Standard icon size matching other sidebar components
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
            
            # Program column hanya judul program (tanpa waktu)
            program_text = program.get('title', 'N/A')
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
            try:
                # Delete from database if available
                if self.db_manager and program.get('id'):
                    success, result = self.db_manager.delete_program_kerja(program['id'])
                    if success:
                        # Reload data from database
                        self.load_data()
                        self.log_message.emit(f"Program kerja berhasil dihapus: {title}")
                        self.data_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", f"Gagal hapus program dari database: {result}")
                else:
                    # Fallback to local storage
                    self.work_programs = [p for p in self.work_programs if p.get('id') != program.get('id')]
                    self.filter_programs()
                    self.log_message.emit(f"Program kerja dihapus (lokal): {title}")
                    self.data_updated.emit()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal hapus program: {str(e)}")
    
    def add_work_program(self):
        """Add new work program"""
        try:
            dialog = WorkProgramDialog(self)
            if dialog.exec_() == dialog.Accepted:
                data = dialog.get_data()
                
                # Validate required fields
                if not data['title'].strip():
                    QMessageBox.warning(self, "Warning", "Judul program tidak boleh kosong")
                    return
                
                # Save to database if available
                if self.db_manager:
                    success, result = self.db_manager.add_program_kerja(data)
                    if success:
                        # Reload data from database
                        self.load_data()
                        self.log_message.emit(f"Program kerja berhasil ditambahkan: {data['title']}")
                        self.data_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", f"Gagal menambah program ke database: {result}")
                else:
                    # Fallback to local storage
                    import time
                    data['id'] = int(time.time() * 1000)  # Use timestamp as ID
                    self.work_programs.append(data)
                    self.filter_programs()
                    self.log_message.emit(f"Program kerja ditambahkan (lokal): {data['title']}")
                    self.data_updated.emit()
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menambah program: {str(e)}")
    
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
        
        try:
            dialog = WorkProgramDialog(self, program)
            if dialog.exec_() == dialog.Accepted:
                data = dialog.get_data()
                
                # Validate required fields
                if not data['title'].strip():
                    QMessageBox.warning(self, "Warning", "Judul program tidak boleh kosong")
                    return
                
                # Update to database if available
                if self.db_manager and program.get('id'):
                    success, result = self.db_manager.update_program_kerja(program['id'], data)
                    if success:
                        # Reload data from database
                        self.load_data()
                        self.log_message.emit(f"Program kerja berhasil diupdate: {data['title']}")
                        self.data_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", f"Gagal update program ke database: {result}")
                else:
                    # Fallback to local storage
                    for i, p in enumerate(self.work_programs):
                        if p.get('id') == program.get('id'):
                            self.work_programs[i].update(data)
                            break
                    
                    self.filter_programs()
                    self.log_message.emit(f"Program kerja diupdate (lokal): {data['title']}")
                    self.data_updated.emit()
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal edit program: {str(e)}")
    
    def export_program(self):
        """Export program kerja ke CSV (matching jadwal.py functionality)"""
        if not self.work_programs:
            QMessageBox.warning(self, "Warning", "Tidak ada data program untuk diekspor.")
            return

        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Program Kerja", "program_kerja.csv", "CSV Files (*.csv)"
        )
        if not filename:
            return

        import csv
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
            self.log_message.emit("Memuat data program kerja dari database...")
            success, programs = self.db_manager.get_program_kerja_list()
            
            if success:
                # Convert database format to UI format
                self.work_programs = []
                for program in programs:
                    ui_data = {
                        'id': program.get('id_program_kerja'),
                        'date': program.get('tanggal'),
                        'title': program.get('judul', ''),
                        'target': program.get('sasaran', ''),
                        'responsible': program.get('penanggung_jawab', ''),
                        'budget_amount': program.get('anggaran', ''),
                        'budget_source': program.get('sumber_anggaran', 'Kas Gereja'),
                        'category': program.get('kategori', ''),
                        'location': program.get('lokasi', ''),
                        'description': program.get('deskripsi', ''),
                        'time': program.get('waktu', ''),
                        'status': program.get('status', 'Direncanakan')
                    }
                    self.work_programs.append(ui_data)
                
                self.filter_programs()  # Update UI
                self.log_message.emit(f"Data program kerja berhasil dimuat: {len(self.work_programs)} program")
            else:
                self.log_message.emit(f"Gagal memuat data program kerja: {programs}")
                self.load_sample_data()
            
        except Exception as e:
            self.log_message.emit(f"Error loading program kerja data: {str(e)}")
            # Fallback to sample data
            self.load_sample_data()
    
    def get_data(self):
        """Get calendar data for other components"""
        return self.work_programs

class KegiatanWRWidget(QWidget):
    """Widget untuk tab Kegiatan WR - menampilkan kegiatan dari client"""

    data_updated = pyqtSignal()
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.kegiatan_data = []
        self.setup_ui()

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        if db_manager:
            self.load_data()

    def setup_ui(self):
        """Setup UI untuk kegiatan WR"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)

        # Header with refresh button
        header = self.create_header()
        layout.addWidget(header)

        # Filter section
        filter_group = self.create_filters()
        layout.addWidget(filter_group)

        # Table
        table_widget = self.create_table()
        layout.addWidget(table_widget, 1)

        # Action buttons
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout, 0)

    def create_header(self):
        """Create header with refresh button"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 5, 10, 5)

        header_layout.addStretch()

        refresh_button = self.create_button("Refresh Data", "#3498db", self.load_data, "server/assets/refresh.png")
        header_layout.addWidget(refresh_button)

        return header

    def create_filters(self):
        """Create filter section"""
        filter_group = QGroupBox()
        filter_layout = QHBoxLayout(filter_group)

        # User filter
        user_label = QLabel("Filter User:")
        filter_layout.addWidget(user_label)

        self.user_filter = QComboBox()
        self.user_filter.addItem("Semua User")
        self.user_filter.currentTextChanged.connect(self.filter_kegiatan)
        filter_layout.addWidget(self.user_filter)

        # Category filter
        category_label = QLabel("Kategori:")
        filter_layout.addWidget(category_label)

        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "Semua", "Ibadah", "Doa", "Katekese", "Sosial",
            "Rohani", "Administratif", "Lainnya"
        ])
        self.category_filter.currentTextChanged.connect(self.filter_kegiatan)
        filter_layout.addWidget(self.category_filter)

        # Apply filter button
        apply_filter = self.create_button("Terapkan Filter", "#3498db", self.filter_kegiatan)
        filter_layout.addWidget(apply_filter)

        show_all_button = self.create_button("Tampilkan Semua", "#9b59b6", self.show_all_kegiatan)
        filter_layout.addWidget(show_all_button)

        filter_layout.addStretch()

        return filter_group

    def create_table(self):
        """Create table for kegiatan WR with 'Dibuat Oleh' column"""
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

        self.kegiatan_table = QTableWidget(0, 8)
        self.kegiatan_table.setHorizontalHeaderLabels([
            "Nama Kegiatan", "Tanggal Mulai", "Tanggal Selesai", "Waktu",
            "Lokasi", "Kategori", "Status DB", "User"
        ])

        # Apply professional table styling
        self.apply_professional_table_style(self.kegiatan_table)

        # Set column widths - sesuai database
        self.kegiatan_table.setColumnWidth(0, 180)  # Nama Kegiatan
        self.kegiatan_table.setColumnWidth(1, 100)  # Tanggal Mulai
        self.kegiatan_table.setColumnWidth(2, 100)  # Tanggal Selesai
        self.kegiatan_table.setColumnWidth(3, 70)   # Waktu
        self.kegiatan_table.setColumnWidth(4, 120)  # Lokasi
        self.kegiatan_table.setColumnWidth(5, 100)  # Kategori
        self.kegiatan_table.setColumnWidth(6, 100)  # Status DB
        self.kegiatan_table.setColumnWidth(7, 120)  # User

        header = self.kegiatan_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # Enable context menu
        self.kegiatan_table.setContextMenuPolicy(3)
        self.kegiatan_table.customContextMenuRequested.connect(self.show_context_menu)

        table_layout.addWidget(self.kegiatan_table)

        return table_container

    def apply_professional_table_style(self, table):
        """Apply Excel-like table styling"""
        header_font = QFont()
        header_font.setBold(False)
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

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

        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d4d4d4;
                background-color: white;
                border: 1px solid #d4d4d4;
                selection-background-color: #cce7ff;
                font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
                outline: none;
                color: black;
            }
            QTableWidget::item {
                border: none;
                padding: 4px 6px;
                min-height: 18px;
                color: black;
            }
            QTableWidget::item:selected {
                background-color: #cce7ff;
                color: black;
            }
            QTableWidget::item:focus {
                border: 2px solid #0078d4;
                background-color: white;
                color: black;
            }
        """)

        header = table.horizontalHeader()
        header.setMinimumSectionSize(50)
        header.setDefaultSectionSize(80)

        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        table.verticalHeader().setDefaultSectionSize(24)
        table.setSelectionBehavior(QAbstractItemView.SelectItems)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(True)
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

        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        table.setMinimumHeight(200)
        table.setSizePolicy(table.sizePolicy().Expanding, table.sizePolicy().Expanding)

    def create_action_buttons(self):
        """Create action buttons layout"""
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        view_button = self.create_button("Lihat Detail", "#3498db", self.view_kegiatan, "server/assets/view.png")
        action_layout.addWidget(view_button)

        export_button = self.create_button("Export CSV", "#16a085", self.export_kegiatan, "server/assets/export.png")
        action_layout.addWidget(export_button)

        return action_layout

    def create_button(self, text, color, slot, icon_path=None):
        """Create button with consistent style and optional icon"""
        button = QPushButton(text)

        if icon_path:
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(20, 20))
            except Exception:
                pass

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
        """Darken color for hover effect"""
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
        """Show context menu for view"""
        if self.kegiatan_table.rowCount() == 0:
            return

        menu = QMenu()
        view_action = menu.addAction("Lihat Detail")
        export_action = menu.addAction("Export")

        action = menu.exec_(self.kegiatan_table.mapToGlobal(position))

        if action == view_action:
            self.view_kegiatan()
        elif action == export_action:
            self.export_kegiatan()

    def load_data(self):
        """Load kegiatan data from database"""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            self.log_message.emit("Memuat data kegiatan WR dari database...")
            success, kegiatan_list = self.db_manager.get_kegiatan_wr_list()

            if success:
                self.kegiatan_data = kegiatan_list
                self.update_user_filter()
                self.filter_kegiatan()
                self.log_message.emit(f"Data kegiatan WR berhasil dimuat: {len(self.kegiatan_data)} kegiatan")
            else:
                self.log_message.emit(f"Gagal memuat data kegiatan WR: {kegiatan_list}")
                self.kegiatan_data = []
                self.populate_table([])

        except Exception as e:
            self.log_message.emit(f"Error loading kegiatan WR data: {str(e)}")
            self.kegiatan_data = []
            self.populate_table([])

    def update_user_filter(self):
        """Update user filter dropdown with unique users"""
        current_text = self.user_filter.currentText()
        self.user_filter.clear()
        self.user_filter.addItem("Semua User")

        # Get unique users
        users = set()
        for kegiatan in self.kegiatan_data:
            user = kegiatan.get('dibuat_oleh', '')
            if user:
                users.add(user)

        # Add users to filter
        for user in sorted(users):
            self.user_filter.addItem(user)

        # Restore previous selection if it exists
        index = self.user_filter.findText(current_text)
        if index >= 0:
            self.user_filter.setCurrentIndex(index)

    def filter_kegiatan(self):
        """Filter kegiatan based on user and category"""
        user_filter = self.user_filter.currentText()
        category_filter = self.category_filter.currentText()

        filtered_kegiatan = []

        for kegiatan in self.kegiatan_data:
            # User filter
            if user_filter != "Semua User":
                if kegiatan.get('dibuat_oleh', '') != user_filter:
                    continue

            # Category filter
            if category_filter != "Semua":
                if kegiatan.get('kategori', '') != category_filter:
                    continue

            filtered_kegiatan.append(kegiatan)

        self.populate_table(filtered_kegiatan)

    def show_all_kegiatan(self):
        """Show all kegiatan without filters"""
        self.user_filter.setCurrentText("Semua User")
        self.category_filter.setCurrentText("Semua")
        self.filter_kegiatan()

    def populate_table(self, kegiatan_list):
        """Populate table with kegiatan data - sesuai struktur database"""
        self.kegiatan_table.setRowCount(0)

        for row_idx, kegiatan in enumerate(kegiatan_list):
            self.kegiatan_table.insertRow(row_idx)

            # Nama Kegiatan
            nama = kegiatan.get('nama_kegiatan', 'N/A')
            nama_item = QTableWidgetItem(nama)

            # Tanggal Pelaksanaan (kegiatan_wr uses tanggal_pelaksanaan)
            tanggal_mulai = kegiatan.get('tanggal_pelaksanaan') or kegiatan.get('tanggal_mulai') or kegiatan.get('tanggal', 'N/A')
            try:
                if tanggal_mulai and tanggal_mulai != 'N/A':
                    # Handle both date string and date object
                    if isinstance(tanggal_mulai, str):
                        date_obj = datetime.datetime.strptime(str(tanggal_mulai), '%Y-%m-%d')
                    else:
                        date_obj = tanggal_mulai
                    formatted_date_mulai = date_obj.strftime('%d %b %Y')
                else:
                    formatted_date_mulai = 'N/A'
            except Exception as e:
                formatted_date_mulai = str(tanggal_mulai)
            tanggal_mulai_item = QTableWidgetItem(formatted_date_mulai)

            # Tanggal Selesai
            tanggal_selesai = kegiatan.get('tanggal_selesai', 'N/A')
            try:
                if tanggal_selesai and tanggal_selesai != 'N/A' and tanggal_selesai != '':
                    # Handle both date string and date object
                    if isinstance(tanggal_selesai, str):
                        date_obj = datetime.datetime.strptime(str(tanggal_selesai), '%Y-%m-%d')
                    else:
                        date_obj = tanggal_selesai
                    formatted_date_selesai = date_obj.strftime('%d %b %Y')
                else:
                    formatted_date_selesai = 'N/A'
            except Exception as e:
                formatted_date_selesai = str(tanggal_selesai) if tanggal_selesai else 'N/A'
            tanggal_selesai_item = QTableWidgetItem(formatted_date_selesai)

            # Waktu Mulai
            waktu = kegiatan.get('waktu_mulai') or kegiatan.get('waktu', 'N/A')
            if waktu and waktu != 'N/A':
                try:
                    # Remove seconds if present
                    if isinstance(waktu, str) and len(waktu) > 5:
                        waktu = waktu[:5]
                except:
                    pass
            waktu_item = QTableWidgetItem(str(waktu))

            # Lokasi/Tempat Kegiatan (kegiatan_wr uses tempat_kegiatan)
            lokasi = kegiatan.get('tempat_kegiatan') or kegiatan.get('lokasi') or kegiatan.get('tempat', 'N/A')
            lokasi_item = QTableWidgetItem(str(lokasi))

            # Kategori
            kategori_item = QTableWidgetItem(kegiatan.get('kategori', 'N/A'))

            # Status dari database (kegiatan_wr uses status_kegiatan)
            status_db = kegiatan.get('status_kegiatan') or kegiatan.get('status', 'Direncanakan')
            status_db_item = QTableWidgetItem(str(status_db))

            # Color code status berdasarkan status database
            if status_db == "Direncanakan":
                status_db_item.setBackground(QBrush(QColor("#3498db")))
                status_db_item.setForeground(QBrush(QColor("white")))
            elif status_db == "Berlangsung":
                status_db_item.setBackground(QBrush(QColor("#f39c12")))
                status_db_item.setForeground(QBrush(QColor("white")))
            elif status_db == "Selesai":
                status_db_item.setBackground(QBrush(QColor("#2ecc71")))
                status_db_item.setForeground(QBrush(QColor("white")))
            elif status_db == "Dibatalkan":
                status_db_item.setBackground(QBrush(QColor("#e74c3c")))
                status_db_item.setForeground(QBrush(QColor("white")))
            else:
                # For empty or other status, use default black text on white background
                status_db_item.setForeground(QBrush(QColor(0, 0, 0)))  # Black text

            # User (username atau nama_lengkap)
            user_info = kegiatan.get('nama_lengkap') or kegiatan.get('username') or kegiatan.get('dibuat_oleh', 'N/A')
            user_item = QTableWidgetItem(str(user_info))

            # Store kegiatan data in first column
            nama_item.setData(Qt.UserRole, kegiatan)

            # Set items in table
            self.kegiatan_table.setItem(row_idx, 0, nama_item)
            self.kegiatan_table.setItem(row_idx, 1, tanggal_mulai_item)
            self.kegiatan_table.setItem(row_idx, 2, tanggal_selesai_item)
            self.kegiatan_table.setItem(row_idx, 3, waktu_item)
            self.kegiatan_table.setItem(row_idx, 4, lokasi_item)
            self.kegiatan_table.setItem(row_idx, 5, kategori_item)
            self.kegiatan_table.setItem(row_idx, 6, status_db_item)
            self.kegiatan_table.setItem(row_idx, 7, user_item)

        # Select first row if available
        if kegiatan_list and self.kegiatan_table.rowCount() > 0:
            self.kegiatan_table.selectRow(0)

    def get_kegiatan_status(self, kegiatan):
        """Determine status of kegiatan based on date or status_kegiatan field"""
        # First, check if there's a status_kegiatan field from database
        status_db = kegiatan.get('status_kegiatan') or kegiatan.get('status', '')
        if status_db:
            return status_db

        # Otherwise, calculate based on date
        try:
            today = datetime.date.today()
            # Use kegiatan_wr field name with fallback
            tanggal_str = kegiatan.get('tanggal_pelaksanaan') or kegiatan.get('tanggal', '')

            if not tanggal_str:
                return "Unknown"

            # Handle both string and date object
            if isinstance(tanggal_str, str):
                kegiatan_date = datetime.datetime.strptime(tanggal_str, '%Y-%m-%d').date()
            else:
                kegiatan_date = tanggal_str

            if kegiatan_date > today:
                return "Akan Datang"
            elif kegiatan_date == today:
                return "Sedang Berlangsung"
            else:
                return "Selesai"
        except:
            return "Unknown"

    def view_kegiatan(self):
        """View selected kegiatan details"""
        current_row = self.kegiatan_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih kegiatan yang akan dilihat")
            return

        nama_item = self.kegiatan_table.item(current_row, 0)
        if not nama_item or not nama_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Warning", "Data kegiatan tidak valid")
            return

        kegiatan = nama_item.data(Qt.UserRole)

        # Create detail dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Detail Kegiatan WR")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        detail_text = QTextEdit()
        detail_text.setReadOnly(True)

        # Use kegiatan_wr field names with fallbacks
        tanggal = kegiatan.get('tanggal_pelaksanaan') or kegiatan.get('tanggal', 'N/A')
        waktu_mulai = kegiatan.get('waktu_mulai', '')
        waktu_selesai = kegiatan.get('waktu_selesai', '')
        waktu = f"{waktu_mulai} - {waktu_selesai}" if waktu_mulai and waktu_selesai else kegiatan.get('waktu', 'N/A')
        tempat = kegiatan.get('tempat_kegiatan') or kegiatan.get('tempat', 'N/A')
        dibuat_oleh = kegiatan.get('nama_lengkap') or kegiatan.get('username') or kegiatan.get('dibuat_oleh', 'N/A')

        detail_html = f"""
        <h2 style="color: #9b59b6;">{kegiatan.get('nama_kegiatan', 'N/A')}</h2>
        <hr>
        <p><strong>Tanggal:</strong> {tanggal}</p>
        <p><strong>Waktu:</strong> {waktu}</p>
        <p><strong>Tempat:</strong> {tempat}</p>
        <p><strong>Kategori:</strong> {kegiatan.get('kategori', 'N/A')}</p>
        <p><strong>Status:</strong> {self.get_kegiatan_status(kegiatan)}</p>
        <p><strong>Dibuat Oleh:</strong> {dibuat_oleh}</p>
        <hr>
        <p><strong>Deskripsi:</strong></p>
        <p>{kegiatan.get('deskripsi', 'Tidak ada deskripsi')}</p>
        """

        detail_text.setHtml(detail_html)
        layout.addWidget(detail_text)

        close_button = QPushButton("Tutup")
        close_button.clicked.connect(dialog.accept)  # type: ignore
        layout.addWidget(close_button)

        dialog.exec_()

    def export_kegiatan(self):
        """Export kegiatan WR to CSV"""
        if self.kegiatan_table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Tidak ada data kegiatan untuk diekspor.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Kegiatan WR", "kegiatan_wr.csv", "CSV Files (*.csv)"
        )
        if not filename:
            return

        import csv
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Nama Kegiatan", "Tanggal", "Waktu", "Tempat",
                    "Kategori", "Status", "Dibuat Oleh", "Deskripsi"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in range(self.kegiatan_table.rowCount()):
                    nama_item = self.kegiatan_table.item(row, 0)
                    if nama_item and nama_item.data(Qt.UserRole):
                        kegiatan = nama_item.data(Qt.UserRole)
                        # Use kegiatan_wr field names with fallbacks
                        tanggal = kegiatan.get('tanggal_pelaksanaan') or kegiatan.get('tanggal', '')
                        waktu_mulai = kegiatan.get('waktu_mulai', '')
                        waktu_selesai = kegiatan.get('waktu_selesai', '')
                        waktu = f"{waktu_mulai} - {waktu_selesai}" if waktu_mulai and waktu_selesai else kegiatan.get('waktu', '')
                        tempat = kegiatan.get('tempat_kegiatan') or kegiatan.get('tempat', '')
                        dibuat_oleh = kegiatan.get('nama_lengkap') or kegiatan.get('username') or kegiatan.get('dibuat_oleh', '')

                        writer.writerow({
                            "Nama Kegiatan": kegiatan.get('nama_kegiatan', ''),
                            "Tanggal": tanggal,
                            "Waktu": waktu,
                            "Tempat": tempat,
                            "Kategori": kegiatan.get('kategori', ''),
                            "Status": self.get_kegiatan_status(kegiatan),
                            "Dibuat Oleh": dibuat_oleh,
                            "Deskripsi": kegiatan.get('deskripsi', '')
                        })

            QMessageBox.information(self, "Sukses", f"Data kegiatan WR berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data kegiatan WR diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
            self.log_message.emit(f"Gagal mengekspor data: {str(e)}")

    def get_data(self):
        """Get kegiatan data for other components"""
        return self.kegiatan_data


class ProgramKerjaComponent(QWidget):
    """Komponen utama Program Kerja dengan 3 tab: Kalender Kerja, Kegiatan WR, dan Jadwal Kegiatan"""

    data_updated = pyqtSignal()
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.setup_ui()

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager

        # Set database manager for all tabs
        self.kalender_widget.set_database_manager(db_manager)
        self.kegiatan_wr_widget.set_database_manager(db_manager)
        self.jadwal_widget.set_database_manager(db_manager)
    
    def create_header(self):
        """Buat header dengan title matching sidebar menu style"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 10)  # Add proper margins: left, top, right, bottom

        title = QLabel("Program Kerja dan Penjadwalan")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        return header

    def create_tabs(self):
        """Buat tab untuk komponen program kerja matching pengaturan style"""
        tab_widget = QTabWidget()

        # Tab 1: Daftar Program Kerja
        self.kalender_widget = KalenderKerjaWidget()
        tab_widget.addTab(self.kalender_widget, "Daftar Program Kerja")

        # Tab 2: Kegiatan Paroki (admin only, existing component - renamed from Jadwal Kegiatan)
        self.jadwal_widget = JadwalComponent()
        tab_widget.addTab(self.jadwal_widget, "Kegiatan Paroki")

        # Tab 3: Kegiatan WR (data dari client)
        self.kegiatan_wr_widget = KegiatanWRWidget()
        tab_widget.addTab(self.kegiatan_wr_widget, "Kegiatan WR")

        return tab_widget

    def setup_ui(self):
        """Setup UI dengan tab widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header matching pengaturan style exactly
        header = self.create_header()
        layout.addWidget(header)

        # Tab widget matching pengaturan style
        self.tab_widget = self.create_tabs()
        layout.addWidget(self.tab_widget)
        
        # Connect signals
        self.connect_signals()
        
        # Hide jadwal component header after setup is complete
        self.hide_jadwal_header()
    
    def hide_jadwal_header(self):
        """Hide the header frame of jadwal component when used in tab"""
        try:
            # Find and hide both the old style header and the new clean header
            layout = self.jadwal_widget.layout()
            if layout:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item and item.widget():
                        widget = item.widget()
                        # Hide old style header with background color
                        if (isinstance(widget, QFrame) and
                            hasattr(widget, 'styleSheet') and
                            widget.styleSheet() and
                            "background-color: #34495e" in widget.styleSheet()):
                            widget.hide()
                            break
                        # Also hide the clean header with "Jadwal Kegiatan" title
                        elif (isinstance(widget, QWidget) and
                              widget.layout() and
                              isinstance(widget.layout(), QHBoxLayout)):
                            # Check if this widget contains a label with "Jadwal Kegiatan"
                            widget_layout = widget.layout()
                            for j in range(widget_layout.count()):
                                sub_item = widget_layout.itemAt(j)
                                if (sub_item and sub_item.widget() and
                                    isinstance(sub_item.widget(), QLabel) and
                                    "Jadwal Kegiatan" in sub_item.widget().text()):
                                    widget.hide()
                                    return
        except Exception as e:
            # If there's any error, just ignore it
            pass
    
    def connect_signals(self):
        """Connect signals from child widgets"""
        # Connect kalender widget signals
        self.kalender_widget.data_updated.connect(self.data_updated.emit)
        self.kalender_widget.log_message.connect(self.log_message.emit)

        # Connect kegiatan WR widget signals
        self.kegiatan_wr_widget.data_updated.connect(self.data_updated.emit)
        self.kegiatan_wr_widget.log_message.connect(self.log_message.emit)

        # Connect jadwal widget signals
        if hasattr(self.jadwal_widget, 'data_updated'):
            self.jadwal_widget.data_updated.connect(self.data_updated.emit)
        if hasattr(self.jadwal_widget, 'log_message'):
            self.jadwal_widget.log_message.connect(self.log_message.emit)

    def get_data(self):
        """Get combined data from all tabs"""
        return {
            'calendar_data': self.kalender_widget.get_data(),
            'kegiatan_wr_data': self.kegiatan_wr_widget.get_data(),
            'schedule_data': self.jadwal_widget.get_data() if hasattr(self.jadwal_widget, 'get_data') else []
        }