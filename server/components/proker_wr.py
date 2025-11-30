# Path: server/components/proker_wr.py
# Program Kerja WR (Wilayah Rohani) Tab Component

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QFrame, QGroupBox, QMessageBox, QDialog, QComboBox,
                           QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                           QFileDialog, QMenu, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QBrush, QIcon

# Import WordWrapHeaderView from proker_base
from .proker_base import WordWrapHeaderView


class ProgramKerjaWRWidget(QWidget):
    """Widget untuk tab Program Kerja WR - program kerja dari wilayah rohani"""

    data_updated = pyqtSignal()
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.work_programs = []
        self.setup_ui()

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        if db_manager:
            self.load_data()

    def setup_ui(self):
        """Setup UI untuk program kerja WR"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title section
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 2px solid #ecf0f1;
                padding: 10px 0px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("Program Kerja Wilayah Rohani")
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

        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 0, 10, 0)
        content_layout.setSpacing(5)

        # Header with add button
        header = self.create_header()
        content_layout.addWidget(header)

        # Filter section
        filter_group = self.create_filters()
        content_layout.addWidget(filter_group)

        # Table
        table_widget = self.create_table()
        content_layout.addWidget(table_widget, 1)

        # Action buttons
        action_layout = self.create_action_buttons()
        content_layout.addLayout(action_layout, 0)

        layout.addWidget(content_widget)

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
        self.user_filter.currentTextChanged.connect(self.filter_programs)
        filter_layout.addWidget(self.user_filter)

        # Category filter
        category_label = QLabel("Kategori:")
        filter_layout.addWidget(category_label)

        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "Semua", "Ibadah", "Doa", "Katekese", "Sosial",
            "Rohani", "Administratif", "Perayaan", "Lainnya"
        ])
        self.category_filter.currentTextChanged.connect(self.filter_programs)
        filter_layout.addWidget(self.category_filter)

        # Bulan filter
        bulan_label = QLabel("Bulan:")
        filter_layout.addWidget(bulan_label)

        self.bulan_filter = QComboBox()
        self.bulan_filter.addItems([
            "Semua Bulan",
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ])
        self.bulan_filter.currentTextChanged.connect(self.filter_programs)
        filter_layout.addWidget(self.bulan_filter)

        filter_layout.addStretch()

        return filter_group

    def create_table(self):
        """Create table for program kerja WR"""
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

        self.program_table = QTableWidget(0, 9)

        # Set custom header with word wrap and center alignment
        custom_header = WordWrapHeaderView(Qt.Horizontal, self.program_table)
        self.program_table.setHorizontalHeader(custom_header)

        # Column order: Kategori, Judul, Bulan, Sasaran, PIC, Anggaran, Sumber Anggaran, Keterangan, User
        self.program_table.setHorizontalHeaderLabels([
            "Kategori", "Judul", "Waktu Estimasi", "Sasaran", "PIC",
            "Anggaran", "Sumber Anggaran", "Keterangan", "User"
        ])

        # Apply professional table styling
        self.apply_professional_table_style(self.program_table)

        # Set column widths
        self.program_table.setColumnWidth(0, 100)   # Kategori
        self.program_table.setColumnWidth(1, 180)   # Judul
        self.program_table.setColumnWidth(2, 100)   # Bulan
        self.program_table.setColumnWidth(3, 120)   # Sasaran
        self.program_table.setColumnWidth(4, 80)    # PIC
        self.program_table.setColumnWidth(5, 100)   # Anggaran
        self.program_table.setColumnWidth(6, 130)   # Sumber Anggaran
        self.program_table.setColumnWidth(7, 150)   # Keterangan
        self.program_table.setColumnWidth(8, 120)   # User

        header = self.program_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # Update header height when column is resized
        header.sectionResized.connect(lambda idx, old, new: self.update_header_height())

        # Enable context menu
        self.program_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.program_table.customContextMenuRequested.connect(self.show_context_menu)

        table_layout.addWidget(self.program_table)

        # Initial header height calculation
        QTimer.singleShot(100, self.update_header_height)

        return table_container

    def update_header_height(self):
        """Update header height when column is resized"""
        if hasattr(self, 'program_table'):
            header = self.program_table.horizontalHeader()
            header.setMinimumHeight(25)
            max_height = 25

            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            header.setFixedHeight(max_height)

    def apply_professional_table_style(self, table):
        """Apply Excel-like table styling"""
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

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

        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        header.setMinimumHeight(25)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(500)

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

        view_button = self.create_button("Lihat Detail", "#3498db", self.view_program, "server/assets/view.png")
        action_layout.addWidget(view_button)

        export_button = self.create_button("Export CSV", "#16a085", self.export_programs, "server/assets/export.png")
        action_layout.addWidget(export_button)

        return action_layout

    def create_button(self, text, color, slot, icon_path=None):
        """Create button with consistent style"""
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
        }
        return color_map.get(color, color)

    def show_context_menu(self, position):
        """Show context menu"""
        if self.program_table.rowCount() == 0:
            return

        menu = QMenu()
        view_action = menu.addAction("Lihat Detail")
        export_action = menu.addAction("Export")

        action = menu.exec_(self.program_table.mapToGlobal(position))

        if action == view_action:
            self.view_program()
        elif action == export_action:
            self.export_programs()

    def filter_programs(self):
        """Filter programs based on user, category, and bulan"""
        user_filter = self.user_filter.currentText()
        category_filter = self.category_filter.currentText()
        bulan_filter = self.bulan_filter.currentText()

        filtered_programs = []

        for program in self.work_programs:
            # User filter
            if user_filter != "Semua User":
                if program.get('user_name', '') != user_filter:
                    continue

            # Category filter
            if category_filter != "Semua":
                if program.get('category', '') != category_filter:
                    continue

            # Bulan filter
            if bulan_filter != "Semua Bulan":
                if program.get('month', '') != bulan_filter:
                    continue

            filtered_programs.append(program)

        self.populate_table(filtered_programs)

    def populate_table(self, programs):
        """Populate table with program data"""
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
            kategori_item = QTableWidgetItem(program.get('category', 'N/A'))

            # Column 1: Judul
            judul_item = QTableWidgetItem(program.get('title', 'N/A'))

            # Column 2: Estimasi Waktu
            waktu_item = QTableWidgetItem(program.get('month', 'N/A'))

            # Column 3: Sasaran
            sasaran_item = QTableWidgetItem(program.get('target', 'N/A'))

            # Column 4: PIC
            pic_item = QTableWidgetItem(program.get('responsible', 'N/A'))

            # Column 5: Anggaran
            budget_amount = program.get('budget_amount', '0')
            if budget_amount and budget_amount.strip():
                try:
                    amount = float(budget_amount.replace(',', '').replace('.', ''))
                    budget_formatted = f"Rp {amount:,.0f}".replace(',', '.')
                except:
                    budget_formatted = f"Rp {budget_amount}"
            else:
                budget_formatted = "Rp 0"
            budget_item = QTableWidgetItem(budget_formatted)

            # Column 6: Sumber Anggaran
            sumber_item = QTableWidgetItem(program.get('budget_source', 'N/A'))

            # Column 7: Keterangan
            keterangan_item = QTableWidgetItem(program.get('keterangan', ''))

            # Column 8: User
            user_item = QTableWidgetItem(program.get('user_name', 'N/A'))

            # Store data in first column
            kategori_item.setData(Qt.UserRole, program)

            # Set items in table
            self.program_table.setItem(row_idx, 0, kategori_item)
            self.program_table.setItem(row_idx, 1, judul_item)
            self.program_table.setItem(row_idx, 2, waktu_item)
            self.program_table.setItem(row_idx, 3, sasaran_item)
            self.program_table.setItem(row_idx, 4, pic_item)
            self.program_table.setItem(row_idx, 5, budget_item)
            self.program_table.setItem(row_idx, 6, sumber_item)
            self.program_table.setItem(row_idx, 7, keterangan_item)
            self.program_table.setItem(row_idx, 8, user_item)

        # Select first row if available
        if programs and self.program_table.rowCount() > 0:
            self.program_table.selectRow(0)

    def load_data(self):
        """Load data from database"""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            self.log_message.emit("Memuat data program kerja WR dari database...")
            success, programs = self.db_manager.get_program_kerja_wr_list()

            if success:
                self.work_programs = []
                for program in programs:
                    # Get username from API response (already joined)
                    # Priority: username > ID (tidak pakai nama_lengkap)
                    user_name = program.get('username', 'N/A')
                    if not user_name or user_name == '' or user_name == 'N/A':
                        user_name = f"User #{program.get('reported_by', 'N/A')}"

                    ui_data = {
                        'id': program.get('id_program_kerja_wr'),
                        'month': program.get('estimasi_waktu', ''),
                        'title': program.get('judul', ''),
                        'target': program.get('sasaran', ''),
                        'responsible': program.get('penanggung_jawab', ''),
                        'budget_amount': str(program.get('anggaran', 0)),
                        'budget_source': program.get('sumber_anggaran', ''),
                        'category': program.get('kategori', ''),
                        'keterangan': program.get('keterangan', ''),
                        'user_name': user_name,
                        'reported_by': program.get('reported_by')
                    }
                    self.work_programs.append(ui_data)

                self.update_user_filter()
                self.filter_programs()
                self.log_message.emit(f"Data program kerja WR berhasil dimuat: {len(self.work_programs)} program")
            else:
                self.log_message.emit(f"Gagal memuat data: {programs}")

        except Exception as e:
            self.log_message.emit(f"Error loading program kerja WR: {str(e)}")

    def update_user_filter(self):
        """Update user filter dropdown"""
        current_text = self.user_filter.currentText()
        self.user_filter.clear()
        self.user_filter.addItem("Semua User")

        # Get unique users
        users = set()
        for program in self.work_programs:
            user = program.get('user_name', '')
            if user and user != 'N/A':
                users.add(user)

        # Add users to filter
        for user in sorted(users):
            self.user_filter.addItem(user)

        # Restore previous selection if exists
        index = self.user_filter.findText(current_text)
        if index >= 0:
            self.user_filter.setCurrentIndex(index)

    def view_program(self):
        """View selected program details"""
        current_row = self.program_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih program yang akan dilihat")
            return

        kategori_item = self.program_table.item(current_row, 0)
        if not kategori_item or not kategori_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Warning", "Data program tidak valid")
            return

        program = kategori_item.data(Qt.UserRole)

        dialog = QDialog(self)
        dialog.setWindowTitle("Detail Program Kerja WR")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        detail_text = QTextEdit()
        detail_text.setReadOnly(True)

        detail_html = f"""
        <h2 style="color: #9b59b6;">{program.get('title', 'N/A')}</h2>
        <hr>
        <p><strong>Kategori:</strong> {program.get('category', 'N/A')}</p>
        <p><strong>Bulan:</strong> {program.get('month', 'N/A')}</p>
        <p><strong>Sasaran:</strong> {program.get('target', 'N/A')}</p>
        <p><strong>PIC:</strong> {program.get('responsible', 'N/A')}</p>
        <p><strong>Anggaran:</strong> Rp {program.get('budget_amount', '0')}</p>
        <p><strong>Sumber Anggaran:</strong> {program.get('budget_source', 'N/A')}</p>
        <p><strong>User:</strong> {program.get('user_name', 'N/A')}</p>
        <hr>
        <p><strong>Keterangan:</strong></p>
        <p>{program.get('keterangan', 'Tidak ada keterangan')}</p>
        """

        detail_text.setHtml(detail_html)
        layout.addWidget(detail_text)

        close_button = QPushButton("Tutup")
        close_button.clicked.connect(dialog.accept)  # type: ignore
        layout.addWidget(close_button)

        dialog.exec_()

    def export_programs(self):
        """Export programs to CSV"""
        if not self.work_programs:
            QMessageBox.warning(self, "Warning", "Tidak ada data program untuk diekspor")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Program Kerja WR", "program_kerja_wr.csv", "CSV Files (*.csv)"
        )
        if not filename:
            return

        import csv
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Kategori", "Judul", "Bulan", "Sasaran", "PIC",
                    "Anggaran", "Sumber Anggaran", "Keterangan", "User"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for item in self.work_programs:
                    writer.writerow({
                        "Kategori": item.get('category', ''),
                        "Judul": item.get('title', ''),
                        "Bulan": item.get('month', ''),
                        "Sasaran": item.get('target', ''),
                        "PIC": item.get('responsible', ''),
                        "Anggaran": item.get('budget_amount', ''),
                        "Sumber Anggaran": item.get('budget_source', ''),
                        "Keterangan": item.get('keterangan', ''),
                        "User": item.get('user_name', '')
                    })

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data program kerja WR diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")

    def get_data(self):
        """Get program data"""
        return self.work_programs
