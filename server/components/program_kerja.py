# Path: server/components/program_kerja.py

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QFrame, QCalendarWidget, QTextEdit, QSplitter, QListWidget, 
                           QListWidgetItem, QGroupBox, QScrollArea, QMessageBox, 
                           QDialog, QFormLayout, QLineEdit, QTextEdit as QTextEditDialog, 
                           QDateEdit, QDialogButtonBox, QComboBox, QSpinBox, QTabWidget,
                           QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QTextCharFormat, QBrush
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
        
        # Responsible person
        self.responsible_input = QLineEdit()
        self.responsible_input.setPlaceholderText("Penanggung jawab")
        form_layout.addRow("Penanggung Jawab:", self.responsible_input)
        
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
    
    def get_data(self):
        """Get form data"""
        return {
            'title': self.title_input.text().strip(),
            'date': self.date_input.date().toString('yyyy-MM-dd'),
            'time': f"{self.hour_input.value():02d}:{self.minute_input.value():02d}",
            'category': self.category_input.currentText(),
            'location': self.location_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'responsible': self.responsible_input.text().strip()
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
        
        # Upcoming events reminder section
        reminder_widget = self.create_upcoming_events_widget()
        layout.addWidget(reminder_widget)
        
        # Main program list layout 
        main_widget = self.create_main_program_widget()
        layout.addWidget(main_widget)
    
    def create_upcoming_events_widget(self):
        """Create upcoming events/reminders widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 5)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("📅 Pengingat Kegiatan Mendatang")
        header.setStyleSheet("""
            QLabel {
                background-color: #27ae60;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Upcoming events list
        self.upcoming_events_widget = QWidget()
        self.upcoming_events_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
            }
        """)
        
        self.upcoming_events_layout = QVBoxLayout(self.upcoming_events_widget)
        self.upcoming_events_layout.setContentsMargins(15, 10, 15, 10)
        self.upcoming_events_layout.setSpacing(5)
        
        # Initially show empty state
        self.update_upcoming_events()
        
        layout.addWidget(self.upcoming_events_widget)
        
        return widget
    
    def update_upcoming_events(self):
        """Update upcoming events display"""
        # Clear current layout
        for i in reversed(range(self.upcoming_events_layout.count())):
            self.upcoming_events_layout.itemAt(i).widget().setParent(None)
        
        # Get upcoming events (next 7 days)
        today = datetime.date.today()
        upcoming = []
        
        for program in self.work_programs:
            try:
                program_date = datetime.datetime.strptime(program['date'], '%Y-%m-%d').date()
                days_diff = (program_date - today).days
                
                # Include events from today and next 7 days
                if 0 <= days_diff <= 7:
                    upcoming.append((program, days_diff))
            except:
                continue
        
        # Sort by date
        upcoming.sort(key=lambda x: x[1])
        
        if not upcoming:
            # Show empty state
            empty_label = QLabel("📝 Tidak ada kegiatan dalam 7 hari ke depan")
            empty_label.setStyleSheet("""
                QLabel {
                    color: #7f8c8d;
                    font-style: italic;
                    padding: 20px;
                    text-align: center;
                }
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            self.upcoming_events_layout.addWidget(empty_label)
        else:
            # Show upcoming events
            for program, days_diff in upcoming:
                event_widget = self.create_event_reminder_item(program, days_diff)
                self.upcoming_events_layout.addWidget(event_widget)
    
    def create_event_reminder_item(self, program, days_diff):
        """Create individual event reminder item"""
        item_widget = QWidget()
        item_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-left: 4px solid #3498db;
                border-radius: 4px;
                margin: 2px 0px;
            }
            QWidget:hover {
                background-color: #f8f9fa;
                border-left-color: #2980b9;
            }
        """)
        
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        # Date info
        if days_diff == 0:
            date_text = "Hari ini"
            date_color = "#e74c3c"  # Red for today
        elif days_diff == 1:
            date_text = "Besok"
            date_color = "#f39c12"  # Orange for tomorrow
        else:
            date_text = f"{days_diff} hari lagi"
            date_color = "#3498db"  # Blue for future
        
        date_label = QLabel(date_text)
        date_label.setStyleSheet(f"""
            QLabel {{
                color: {date_color};
                font-weight: bold;
                font-size: 11px;
                min-width: 70px;
            }}
        """)
        date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(date_label)
        
        # Event details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(2)
        
        # Title and time
        title_time = QLabel(f"{program.get('title', 'N/A')} - {program.get('time', 'N/A')}")
        title_time.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        details_layout.addWidget(title_time)
        
        # Location and category
        location_category = QLabel(f"📍 {program.get('location', 'N/A')} • {program.get('category', 'N/A')}")
        location_category.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 10px;
            }
        """)
        details_layout.addWidget(location_category)
        
        layout.addLayout(details_layout)
        layout.addStretch()
        
        # Responsible person
        responsible_label = QLabel(program.get('responsible', 'N/A'))
        responsible_label.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 10px;
                font-style: italic;
            }
        """)
        responsible_label.setAlignment(Qt.AlignRight)
        layout.addWidget(responsible_label)
        
        return item_widget
    
    
    def create_main_program_widget(self):
        """Create main program widget with search and filters"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Control panel with search and filters
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(10)
        
        # Title
        control_title = QLabel("📋 Daftar Program Kerja")
        control_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        control_layout.addWidget(control_title)
        
        # Search and filter row
        filter_row = QHBoxLayout()
        
        # Search by keyword
        search_label = QLabel("🔍 Cari:")
        search_label.setStyleSheet("font-weight: bold; color: #34495e;")
        filter_row.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari program berdasarkan judul, lokasi, atau penanggung jawab...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.filter_programs)
        filter_row.addWidget(self.search_input)
        
        control_layout.addLayout(filter_row)
        
        # Filter row
        filter_row2 = QHBoxLayout()
        
        # Category filter
        category_label = QLabel("📂 Kategori:")
        category_label.setStyleSheet("font-weight: bold; color: #34495e;")
        filter_row2.addWidget(category_label)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "Semua Kategori", "Ibadah", "Kegiatan Sosial", "Rapat", 
            "Pelatihan", "Kunjungan", "Acara Khusus", "Lainnya"
        ])
        self.category_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                min-width: 150px;
            }
        """)
        self.category_filter.currentTextChanged.connect(self.filter_programs)
        filter_row2.addWidget(self.category_filter)
        
        # Month range filter
        month_label = QLabel("📅 Bulan:")
        month_label.setStyleSheet("font-weight: bold; color: #34495e;")
        filter_row2.addWidget(month_label)
        
        self.month_filter = QComboBox()
        self.populate_month_filter()
        self.month_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                min-width: 150px;
            }
        """)
        self.month_filter.currentTextChanged.connect(self.filter_programs)
        filter_row2.addWidget(self.month_filter)
        
        filter_row2.addStretch()
        
        # Add program button
        add_button = QPushButton("➕ Tambah Program")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        add_button.clicked.connect(self.add_work_program)
        filter_row2.addWidget(add_button)
        
        control_layout.addLayout(filter_row2)
        layout.addWidget(control_frame)
        
        # Program list with details
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left: Program list
        list_widget = self.create_program_list_widget()
        content_splitter.addWidget(list_widget)
        
        # Right: Program details
        details_widget = self.create_program_details_widget()
        content_splitter.addWidget(details_widget)
        
        # Set splitter proportions
        content_splitter.setStretchFactor(0, 2)  # Program list gets more space
        content_splitter.setStretchFactor(1, 1)  # Details gets less space
        content_splitter.setSizes([500, 300])
        
        layout.addWidget(content_splitter)
        
        return widget
    
    def populate_month_filter(self):
        """Populate month filter with current and upcoming months"""
        current_date = datetime.date.today()
        months = ["Semua Bulan"]
        
        # Add current month and next 11 months
        for i in range(12):
            month_date = current_date.replace(day=1)
            if i > 0:
                # Calculate next month
                if month_date.month == 12:
                    month_date = month_date.replace(year=month_date.year + 1, month=1)
                else:
                    month_date = month_date.replace(month=month_date.month + 1)
                current_date = month_date
            
            month_text = current_date.strftime("%B %Y")
            month_value = current_date.strftime("%Y-%m")
            months.append(f"{month_text}")
        
        self.month_filter.addItems(months)
    
    def create_program_list_widget(self):
        """Create program table widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("📋 Daftar Program")
        header.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px 6px 0 0;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Program count info
        self.program_count_label = QLabel("Total: 0 program")
        self.program_count_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 8px 12px;
                color: #2c3e50;
                font-weight: bold;
                border-bottom: 1px solid #bdc3c7;
            }
        """)
        layout.addWidget(self.program_count_label)
        
        # Program table
        self.program_table = QTableWidget(0, 6)
        self.program_table.setHorizontalHeaderLabels([
            "Tanggal", "Waktu", "Judul Program", "Kategori", "Lokasi", "Penanggung Jawab"
        ])
        
        # Set column widths
        self.program_table.setColumnWidth(0, 100)  # Tanggal
        self.program_table.setColumnWidth(1, 70)   # Waktu
        self.program_table.setColumnWidth(2, 200)  # Judul Program
        self.program_table.setColumnWidth(3, 120)  # Kategori
        self.program_table.setColumnWidth(4, 150)  # Lokasi
        self.program_table.horizontalHeader().setStretchLastSection(True)  # Penanggung Jawab stretches
        
        # Table styling
        self.program_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e9ecef;
                gridline-color: #f8f9fa;
                selection-background-color: #3498db;
                selection-color: white;
                border-radius: 0 0 6px 6px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f8f9fa;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #bdc3c7;
            }
        """)
        
        # Table properties
        self.program_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.program_table.setAlternatingRowColors(True)
        self.program_table.verticalHeader().setVisible(False)
        
        # Connect signals
        self.program_table.itemClicked.connect(self.update_program_details_from_table)
        self.program_table.itemDoubleClicked.connect(self.edit_program)
        
        layout.addWidget(self.program_table)
        
        return widget
    
    def create_program_details_widget(self):
        """Create program details widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("📄 Detail Program")
        header.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px 6px 0 0;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Program details
        self.program_details = QTextEdit()
        self.program_details.setReadOnly(True)
        self.program_details.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #e9ecef;
                padding: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                border-radius: 0 0 6px 6px;
            }
        """)
        layout.addWidget(self.program_details)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        edit_button = QPushButton("✏️ Edit")
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        edit_button.clicked.connect(self.edit_program)
        button_layout.addWidget(edit_button)
        
        delete_button = QPushButton("🗑️ Hapus")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_button.clicked.connect(self.delete_program)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def filter_programs(self):
        """Filter programs based on search and filter criteria"""
        search_text = self.search_input.text().lower().strip()
        category_filter = self.category_filter.currentText()
        month_filter = self.month_filter.currentText()
        
        filtered_programs = []
        
        for program in self.work_programs:
            # Search filter
            if search_text:
                title = program.get('title', '').lower()
                location = program.get('location', '').lower()
                responsible = program.get('responsible', '').lower()
                description = program.get('description', '').lower()
                
                if not (search_text in title or search_text in location or 
                       search_text in responsible or search_text in description):
                    continue
            
            # Category filter
            if category_filter != "Semua Kategori":
                if program.get('category', '') != category_filter:
                    continue
            
            # Month filter
            if month_filter != "Semua Bulan":
                program_date = program.get('date', '')
                if program_date:
                    try:
                        prog_date_obj = datetime.datetime.strptime(program_date, '%Y-%m-%d')
                        prog_month_year = prog_date_obj.strftime("%B %Y")
                        if prog_month_year != month_filter:
                            continue
                    except:
                        continue
            
            filtered_programs.append(program)
        
        self.populate_program_list_filtered(filtered_programs)
    
    def populate_program_list_filtered(self, programs):
        """Populate program table with filtered programs"""
        self.program_table.setRowCount(0)
        
        # Update count
        self.program_count_label.setText(f"Total: {len(programs)} program")
        
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
            
            # Create table items
            date_item = QTableWidgetItem(formatted_date)
            time_item = QTableWidgetItem(program.get('time', 'N/A'))
            title_item = QTableWidgetItem(program.get('title', 'N/A'))
            category_item = QTableWidgetItem(program.get('category', 'N/A'))
            location_item = QTableWidgetItem(program.get('location', 'N/A'))
            responsible_item = QTableWidgetItem(program.get('responsible', 'N/A'))
            
            # Store program data in first column
            date_item.setData(Qt.UserRole, program)
            
            # Set items in table
            self.program_table.setItem(row_idx, 0, date_item)
            self.program_table.setItem(row_idx, 1, time_item)
            self.program_table.setItem(row_idx, 2, title_item)
            self.program_table.setItem(row_idx, 3, category_item)
            self.program_table.setItem(row_idx, 4, location_item)
            self.program_table.setItem(row_idx, 5, responsible_item)
        
        # Select first row if available
        if programs and self.program_table.rowCount() > 0:
            self.program_table.selectRow(0)
            self.update_program_details_from_table()
    
    
    def load_sample_data(self):
        """Load sample work programs - start empty per user request"""
        self.work_programs = []
        # Update upcoming events display
        if hasattr(self, 'upcoming_events_layout'):
            self.update_upcoming_events()
        # Use the new filter approach to populate the table
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
    
    def update_program_details_from_table(self):
        """Update program details display from table selection"""
        current_row = self.program_table.currentRow()
        if current_row < 0:
            self.program_details.clear()
            return
        
        date_item = self.program_table.item(current_row, 0)
        if not date_item or not date_item.data(Qt.UserRole):
            self.program_details.clear()
            return
        
        program = date_item.data(Qt.UserRole)
        
        details_html = f"""
        <h3 style="color: #2c3e50; margin-bottom: 10px;">{program.get('title', 'N/A')}</h3>
        <p><strong>Tanggal:</strong> {program.get('date', 'N/A')}</p>
        <p><strong>Waktu:</strong> {program.get('time', 'N/A')}</p>
        <p><strong>Kategori:</strong> {program.get('category', 'N/A')}</p>
        <p><strong>Lokasi:</strong> {program.get('location', 'N/A')}</p>
        <p><strong>Penanggung Jawab:</strong> {program.get('responsible', 'N/A')}</p>
        <p><strong>Deskripsi:</strong></p>
        <p style="background-color: #f8f9fa; padding: 8px; border-left: 3px solid #3498db;">
        {program.get('description', 'Tidak ada deskripsi')}
        </p>
        """
        
        self.program_details.setHtml(details_html)
    
    def update_program_details(self):
        """Update program details display - legacy method for compatibility"""
        self.update_program_details_from_table()
    
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
            self.update_upcoming_events()
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
            self.update_upcoming_events()
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
            self.update_upcoming_events()
            self.filter_programs()  # Use filtered approach
            
            self.log_message.emit(f"Program kerja dihapus: {title}")
            self.data_updated.emit()
    
    def load_data(self):
        """Load data from database (placeholder)"""
        if not self.db_manager:
            return
        
        # TODO: Implement database loading when API is available
        self.log_message.emit("Loading calendar data from database...")
        
        # For now, use sample data
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
        
        # Tab 1: Kalender Kerja
        self.kalender_widget = KalenderKerjaWidget()
        self.tab_widget.addTab(self.kalender_widget, "Kalender Kerja")
        
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