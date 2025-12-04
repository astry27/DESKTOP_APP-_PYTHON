# Path: server/components/proker_dpp.py
# Program Kerja DPP (Dewan Pengurus Paroki) Tab Component

import csv
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                            QGroupBox, QScrollArea, QMessageBox, QFileDialog, QMenu, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon

from .proker_base import WordWrapHeaderView, WorkProgramDialog


class ProgramKerjaDPPWidget(QWidget):
    """Widget untuk tab Program Kerja DPP"""

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

        # Title section
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                padding: 10px 0px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("Program Kerja Dewan Pastoral Paroki")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        layout.addWidget(title_frame)

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
        action_layout.setSpacing(10)

        action_layout.addStretch()

        # Edit button with icon
        edit_button = self.create_button("Edit", "#f39c12", self.edit_program, "server/assets/edit.png")
        action_layout.addWidget(edit_button)

        # Delete button with icon
        delete_button = self.create_button("Hapus", "#c0392b", self.delete_program, "server/assets/hapus.png")
        action_layout.addWidget(delete_button)

        # Export button with icon - changed to green color
        export_button = self.create_button(".CSV", "#27ae60", self.export_program, "server/assets/export.png")
        action_layout.addWidget(export_button)

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
        """Buat filter bulan dengan dropdown saja"""
        filter_group = QGroupBox()  # Remove title
        filter_layout = QHBoxLayout(filter_group)

        month_label = QLabel("Filter:")
        filter_layout.addWidget(month_label)

        self.month_filter = QComboBox()
        self.populate_month_filter()
        self.month_filter.currentTextChanged.connect(self.filter_programs)
        filter_layout.addWidget(self.month_filter)

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
        table = QTableWidget(0, 8)

        # Set custom header with word wrap and center alignment
        custom_header = WordWrapHeaderView(Qt.Horizontal, table)
        table.setHorizontalHeader(custom_header)

        table.setHorizontalHeaderLabels([
            "Kategori", "Perayaan/Program", "Estimasi Waktu", "Sasaran", "PIC", "Anggaran", "Sumber Anggaran", "Keterangan"
        ])

        # Apply professional table styling
        self.apply_professional_table_style(table)

        # Set initial column widths with better proportions for full layout
        table.setColumnWidth(0, 100)   # Kategori
        table.setColumnWidth(1, 200)   # Perayaan/Program
        table.setColumnWidth(2, 120)   # Estimasi Waktu
        table.setColumnWidth(3, 150)   # Sasaran
        table.setColumnWidth(4, 100)   # PIC
        table.setColumnWidth(5, 100)   # Anggaran
        table.setColumnWidth(6, 130)   # Sumber Anggaran
        table.setColumnWidth(7, 200)   # Deskripsi

        # Excel-like column resizing - all columns can be resized (matching struktur.py)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # All columns resizable
        header.setStretchLastSection(True)  # Last column stretches to fill space

        # Update header height when column is resized
        header.sectionResized.connect(lambda idx, old, new: self.update_program_header_height(table))

        # Enable context menu
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu)

        # Connect double click to edit
        table.itemDoubleClicked.connect(self.edit_program)

        # Initial header height calculation
        QTimer.singleShot(100, lambda: self.update_program_header_height(table))

        return table

    def update_program_header_height(self, table):
        """Update header height for program table when column is resized"""
        if table:
            header = table.horizontalHeader()
            # Force header to recalculate height
            header.setMinimumHeight(25)
            max_height = 25

            # Calculate required height for each section
            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            # Set header height to accommodate tallest section
            header.setFixedHeight(max_height)

    def apply_professional_table_style(self, table):
        """Apply Excel-like table styling with bold headers and word wrap."""
        # Header styling - Bold headers with center alignment
        header_font = QFont()
        header_font.setBold(True)  # Make headers bold
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

        # Header with bold text, center alignment, and word wrap
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #d4d4d4;
                border-right: 1px solid #d4d4d4;
                padding: 6px 4px;
                font-weight: bold;
                color: #333333;
            }
        """)

        # Configure header behavior
        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        header.setMinimumHeight(25)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(500)

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

        # Enable scrolling
        from PyQt5.QtWidgets import QAbstractItemView
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
        """Filter programs based on month filter (estimasi_waktu)"""
        month_filter = self.month_filter.currentText()

        filtered_programs = []

        for program in self.work_programs:
            # Month filter only
            if month_filter != "Semua Bulan":
                program_month = program.get('month', '')
                if program_month != month_filter:
                    continue

            filtered_programs.append(program)

        self.populate_program_list_filtered(filtered_programs)

    def populate_program_list_filtered(self, programs):
        """Populate program table with filtered programs"""
        self.program_table.setRowCount(0)

        # Sort programs by month and title
        month_order = {
            "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
            "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
            "September": 9, "Oktober": 10, "November": 11, "Desember": 12
        }
        sorted_programs = sorted(programs, key=lambda x: (month_order.get(x.get('month', ''), 13), x.get('title', '')))

        for row_idx, program in enumerate(sorted_programs):
            self.program_table.insertRow(row_idx)

            # Column 0: Kategori
            category_item = QTableWidgetItem(program.get('category', 'N/A'))

            # Column 1: Perayaan/Program (judul)
            program_text = program.get('title', 'N/A')
            program_item = QTableWidgetItem(program_text)

            # Column 2: Estimasi Waktu (bulan)
            month_item = QTableWidgetItem(program.get('month', 'N/A'))

            # Column 3: Sasaran
            target_item = QTableWidgetItem(program.get('target', 'N/A'))

            # Column 4: PIC
            pic_item = QTableWidgetItem(program.get('responsible', 'N/A'))

            # Column 5: Anggaran (format currency)
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

            # Column 6: Sumber Anggaran
            budget_source_item = QTableWidgetItem(program.get('budget_source', 'N/A'))

            # Column 7: Keterangan
            keterangan_item = QTableWidgetItem(program.get('keterangan', ''))

            # Store program data in first column
            category_item.setData(Qt.UserRole, program)

            # Set items in table (new column order)
            self.program_table.setItem(row_idx, 0, category_item)
            self.program_table.setItem(row_idx, 1, program_item)      # Perayaan/Program now in column 1
            self.program_table.setItem(row_idx, 2, month_item)        # Estimasi Waktu now in column 2
            self.program_table.setItem(row_idx, 3, target_item)
            self.program_table.setItem(row_idx, 4, pic_item)
            self.program_table.setItem(row_idx, 5, budget_item)
            self.program_table.setItem(row_idx, 6, budget_source_item)
            self.program_table.setItem(row_idx, 7, keterangan_item)

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

                if not data.get('month') or data['month'].strip() == '':
                    QMessageBox.warning(self, "Warning", "Estimasi waktu (bulan) harus dipilih")
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
                    data['id'] = str(int(time.time() * 1000))  # Use timestamp as ID
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

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Kategori", "Perayaan/Program", "Estimasi Waktu", "Sasaran", "PIC",
                    "Jumlah Anggaran", "Sumber Anggaran", "Keterangan"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in self.work_programs:
                    writer.writerow({
                        "Kategori": item.get('category', ''),
                        "Perayaan/Program": item.get('title', ''),
                        "Estimasi Waktu": item.get('month', ''),
                        "Sasaran": item.get('target', ''),
                        "PIC": item.get('responsible', ''),
                        "Jumlah Anggaran": item.get('budget_amount', ''),
                        "Sumber Anggaran": item.get('budget_source', ''),
                        "Keterangan": item.get('keterangan', '')
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
                        'month': program.get('estimasi_waktu', ''),  # Renamed from tanggal to estimasi_waktu
                        'title': program.get('judul', ''),
                        'target': program.get('sasaran', ''),
                        'responsible': program.get('penanggung_jawab', ''),
                        'budget_amount': program.get('anggaran', ''),
                        'budget_source': program.get('sumber_anggaran', 'Kas Gereja'),
                        'category': program.get('kategori', ''),
                        'keterangan': program.get('keterangan', '')  # Renamed from deskripsi to keterangan
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
