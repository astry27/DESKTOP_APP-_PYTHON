# Path: client/components/keuangan_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QPushButton, QFrame,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox,
                             QTabWidget, QTextEdit, QProgressBar, QDialog,
                             QFormLayout, QDateEdit, QSpinBox, QFileDialog, QGroupBox,
                             QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QSize, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QPainter
import datetime
import json
import os
from datetime import date

class WordWrapHeaderView(QHeaderView):
    """Custom header view with word wrap and center alignment support"""
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)

    def sectionSizeFromContents(self, logicalIndex):
        """Calculate section size based on wrapped text"""
        if self.model():
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                width = self.sectionSize(logicalIndex)
                if width <= 0:
                    width = self.defaultSectionSize()

                font = self.font()
                font.setBold(True)
                fm = self.fontMetrics()

                rect = fm.boundingRect(0, 0, width - 8, 1000,
                                      Qt.AlignCenter | Qt.TextWordWrap, str(text))

                return QSize(width, max(rect.height() + 12, 25))

        return super().sectionSizeFromContents(logicalIndex)

    def paintSection(self, painter, rect, logicalIndex):
        """Paint section with word wrap and center alignment"""
        painter.save()

        bg_color = QColor(242, 242, 242)
        painter.fillRect(rect, bg_color)

        border_color = QColor(212, 212, 212)
        painter.setPen(border_color)
        painter.drawLine(rect.topRight(), rect.bottomRight())
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        if self.model():
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                font = self.font()
                font.setBold(True)
                painter.setFont(font)

                text_color = QColor(51, 51, 51)
                painter.setPen(text_color)

                text_rect = rect.adjusted(4, 4, -4, -4)
                painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, str(text))

        painter.restore()

class KeuanganDialog(QDialog):
    def __init__(self, parent=None, keuangan_data=None):
        super().__init__(parent)
        self.keuangan_data = keuangan_data if keuangan_data else {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Tambah/Edit Transaksi Keuangan")
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(8)

        # Tanggal
        self.tanggal = QDateEdit()
        self.tanggal.setCalendarPopup(True)
        if self.keuangan_data.get('tanggal'):
            try:
                date_obj = datetime.datetime.strptime(self.keuangan_data['tanggal'], '%Y-%m-%d').date()
                self.tanggal.setDate(QDate.fromString(date_obj.isoformat(), Qt.ISODate))
            except:
                self.tanggal.setDate(QDate.currentDate())
        else:
            self.tanggal.setDate(QDate.currentDate())
        form_layout.addRow("Tanggal Transaksi:", self.tanggal)

        # Jenis Transaksi
        self.jenis = QComboBox()
        self.jenis.addItems(['Pemasukan', 'Pengeluaran'])
        if self.keuangan_data.get('jenis'):
            index = self.jenis.findText(self.keuangan_data['jenis'])
            if index >= 0:
                self.jenis.setCurrentIndex(index)
        form_layout.addRow("Jenis Transaksi:", self.jenis)

        # Kategori
        self.kategori = QComboBox()
        self.kategori.addItems([
            "Kolekte", "Donasi", "Operasional",
            "Pemeliharaan", "Program", "Lainnya"
        ])
        if self.keuangan_data.get('kategori'):
            index = self.kategori.findText(self.keuangan_data['kategori'])
            if index >= 0:
                self.kategori.setCurrentIndex(index)
        form_layout.addRow("Kategori:", self.kategori)

        # Keterangan
        self.keterangan = QTextEdit()
        self.keterangan.setMaximumHeight(80)
        self.keterangan.setText(self.keuangan_data.get('keterangan', ''))
        form_layout.addRow("Keterangan:", self.keterangan)

        # Jumlah
        self.jumlah = QSpinBox()
        self.jumlah.setRange(0, 999999999)
        self.jumlah.setValue(int(self.keuangan_data.get('jumlah', 0)))
        self.jumlah.setSuffix(" Rupiah")
        form_layout.addRow("Jumlah:", self.jumlah)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_button = QPushButton("Simpan")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        save_button.clicked.connect(self.accept)  # type: ignore

        cancel_button = QPushButton("Batal")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_button.clicked.connect(self.reject)  # type: ignore

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_data(self):
        return {
            'tanggal': self.tanggal.date().toString(Qt.ISODate),
            'jenis': self.jenis.currentText(),
            'kategori': self.kategori.currentText(),
            'keterangan': self.keterangan.toPlainText(),
            'jumlah': self.jumlah.value(),
            'created_at': datetime.datetime.now().isoformat()
        }

class KeuanganClientComponent(QWidget):

    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.keuangan_data = []
        self.filtered_data = []
        self.sorted_data = []  # Data yang sudah di-sort untuk display di tabel
        self.current_user = None
        self._data_loaded = False  # Flag to track if data has been loaded

        self.setup_ui()

    def showEvent(self, event):
        """Override showEvent to load data when component is first shown"""
        super().showEvent(event)
        # Load data only once when first shown
        if not self._data_loaded:
            print("[DEBUG] KeuanganClientComponent shown, loading data...")
            QTimer.singleShot(100, self.load_user_keuangan_data)
            self._data_loaded = True
    
    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title section with professional styling
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

        title_label = QLabel("Manajemen Keuangan")
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

        # Tab widget for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #27ae60;
                color: white;
            }
        """)
        
        # Transactions tab
        self.transactions_tab = self.create_transactions_tab()
        transaction_icon = QIcon("client/assets/transaction.png")
        self.tab_widget.addTab(self.transactions_tab, transaction_icon, "Transaksi Keuangan")

        # Reports tab
        self.reports_tab = self.create_reports_tab()
        report_icon = QIcon("client/assets/report.png")
        self.tab_widget.addTab(self.reports_tab, report_icon, "Laporan")
        
        layout.addWidget(self.tab_widget)
    
    def create_transactions_tab(self):
        """Create transactions tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Professional Summary using server inventaris style
        self.create_financial_statistics_summary(layout)

        # Combined toolbar with search/filter and add button
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        # Search
        search_label = QLabel("Cari:")
        search_label.setStyleSheet("font-weight: 500; color: #2c3e50;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari keterangan transaksi...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.filter_data)

        # Type filter
        type_label = QLabel("Jenis:")
        type_label.setStyleSheet("font-weight: 500; color: #2c3e50;")
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Semua", "Pemasukan", "Pengeluaran"])
        self.type_filter.setFixedWidth(120)
        self.type_filter.currentTextChanged.connect(self.filter_data)

        # Category filter
        category_label = QLabel("Kategori:")
        category_label.setStyleSheet("font-weight: 500; color: #2c3e50;")
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "Semua", "Kolekte", "Persembahan", "Donasi", "Operasional",
            "Pemeliharaan", "Program", "Lainnya"
        ])
        self.category_filter.setFixedWidth(120)
        self.category_filter.currentTextChanged.connect(self.filter_data)

        # Add button in the same row
        add_button = self.create_professional_button("add.png", "Tambah Transaksi", "#27ae60", "#2ecc71")
        add_button.clicked.connect(self.add_transaksi)

        toolbar_layout.addWidget(search_label)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(type_label)
        toolbar_layout.addWidget(self.type_filter)
        toolbar_layout.addWidget(category_label)
        toolbar_layout.addWidget(self.category_filter)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(add_button)

        layout.addLayout(toolbar_layout)

        # Table with professional styling
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels([
            "Tanggal Transaksi", "Jenis", "Kategori", "Keterangan", "Jumlah (Rp)", "Saldo", "Aksi"
        ])

        custom_header = WordWrapHeaderView(Qt.Horizontal, self.table_widget)
        self.table_widget.setHorizontalHeader(custom_header)

        self.apply_professional_table_style()

        header = self.table_widget.horizontalHeader()
        header.setVisible(True)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionsMovable(False)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(80)
        header.setDefaultSectionSize(110)
        header.sectionResized.connect(self.update_header_height)

        for index in range(self.table_widget.columnCount()):
            if index == 3:
                header.setSectionResizeMode(index, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(index, QHeaderView.Interactive)

        self.table_widget.horizontalHeader().setFixedHeight(25)
        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

        # Set specific column widths
        self.table_widget.setColumnWidth(0, 100)  # Tanggal
        self.table_widget.setColumnWidth(1, 100)  # Jenis
        self.table_widget.setColumnWidth(2, 120)  # Kategori
        self.table_widget.setColumnWidth(4, 120)  # Jumlah
        self.table_widget.setColumnWidth(5, 120)  # Saldo
        self.table_widget.setColumnWidth(6, 140)  # Aksi

        self.table_widget.verticalHeader().setVisible(True)
        self.table_widget.verticalHeader().setDefaultSectionSize(36)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)

        self.table_widget.setAlternatingRowColors(False)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addWidget(self.table_widget)

        # Export button at bottom right
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        export_button = self.create_action_button("Export Data", "#16a085", "#1abc9c", "export.png")
        export_button.clicked.connect(self.export_data)
        export_button.setToolTip("Ekspor data ke CSV")
        export_layout.addWidget(export_button)

        layout.addLayout(export_layout)

        return tab

    def update_header_height(self, logical_index, old_size, new_size):
        """Update header height when column width changes to accommodate wrapped text"""
        if not hasattr(self, "table_widget"):
            return

        header = self.table_widget.horizontalHeader()
        header.setMinimumHeight(25)
        max_height = 25

        for index in range(header.count()):
            size = header.sectionSizeFromContents(index)
            max_height = max(max_height, size.height())

        header.setFixedHeight(max_height)

    def apply_professional_table_style(self):
        """Apply jemaat-style table styling for consistent appearance"""
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)
        self.table_widget.horizontalHeader().setFont(header_font)

        self.table_widget.horizontalHeader().setStyleSheet("""
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

        self.table_widget.setStyleSheet("""
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
                min-height: 18px;
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

        self.table_widget.verticalHeader().setStyleSheet("""
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

        self.table_widget.setShowGrid(True)
        self.table_widget.setGridStyle(Qt.SolidLine)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    def create_financial_statistics_summary(self, layout):
        """Create financial summary using server inventaris style"""
        stats_group = QGroupBox("Ringkasan Keuangan")
        stats_layout = QHBoxLayout(stats_group)

        # Initialize value labels
        self.total_transaksi_value = QLabel("0")
        self.total_pemasukan_label = QLabel("Rp 0")
        self.total_pengeluaran_label = QLabel("Rp 0")
        self.total_saldo_label = QLabel("Rp 0")

        # Add stat widgets using server inventaris style
        stats_layout.addWidget(self.create_stat_widget("TOTAL TRANSAKSI", self.total_transaksi_value, "#ddeaee", "#2c3e50"))
        stats_layout.addWidget(self.create_stat_widget("TOTAL PEMASUKAN", self.total_pemasukan_label, "#e8f8f5", "#27ae60"))
        stats_layout.addWidget(self.create_stat_widget("TOTAL PENGELUARAN", self.total_pengeluaran_label, "#fadbd8", "#e74c3c"))
        stats_layout.addWidget(self.create_stat_widget("SALDO AKHIR", self.total_saldo_label, "#e3f2fd", "#3498db"))

        layout.addWidget(stats_group)

    def create_stat_widget(self, label_text, value_label, bg_color, text_color):
        """Create statistical widget using server inventaris style"""
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 4px;
                padding: 6px;
            }}
        """)
        widget.setMaximumHeight(60)  # Limit height to make it smaller
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(6, 6, 6, 6)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                color: {text_color};
                font-size: 9px;
                font-family: Arial, sans-serif;
                background-color: transparent;
                min-height: 12px;
            }}
        """)

        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {text_color};
                font-family: Arial, sans-serif;
                background-color: transparent;
                padding: 2px;
                min-height: 16px;
            }}
        """)

        layout.addWidget(label)
        layout.addWidget(value_label)

        return widget

    def create_action_button(self, text, bg_color, hover_color, icon_name):
        """Create action button with icon and professional styling"""
        button = QPushButton(text)

        # Add icon if available
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', icon_name)
        if os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(12, 12))
            except Exception:
                pass

        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 {bg_color}, stop:1 {self.darken_color(bg_color)});
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-weight: 500;
                font-size: 11px;
                text-align: center;
                min-width: 90px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 {hover_color}, stop:1 {self.darken_color(hover_color)});
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }}
            QPushButton:pressed {{
                background: {self.darken_color(hover_color)};
            }}
        """)

        return button

    def create_professional_button(self, icon_name, text, bg_color, hover_color):
        """Create a professional button with icon and text"""
        button = QPushButton(text)
        button.setMinimumSize(150, 32)
        button.setMaximumSize(220, 32)

        # Add icon if available
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', icon_name)
        if os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(14, 14))
            except Exception:
                pass  # Continue without icon if loading fails

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: 1px solid {bg_color};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 500;
                text-align: center;
                margin: 1px 3px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border-color: {hover_color};
                box-shadow: 0 2px 4px rgba(0,0,0,0.15);
            }}
            QPushButton:pressed {{
                background-color: {bg_color};
                border-color: {bg_color};
                box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
            }}
            QPushButton::tooltip {{
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                border: none;
                padding: 3px 6px;
                border-radius: 3px;
                font-size: 10px;
                margin: 0px;
            }}
        """)

        return button

    def darken_color(self, color):
        """Darken a color for gradient effect"""
        color_map = {
            "#27ae60": "#229954",
            "#3498db": "#2980b9",
            "#e74c3c": "#c0392b",
            "#f39c12": "#e67e22",
            "#2ecc71": "#27ae60",
            "#2980b9": "#21618c",
            "#16a085": "#138d75",
            "#1abc9c": "#17a085"
        }
        return color_map.get(color, color)

    def create_financial_card(self, icon, title, value, color, bg_color):
        """Create professional financial card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
                margin: 5px;
                min-height: 120px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            QFrame:hover {{
                border-color: {color};
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Icon container
        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 20px;
                border: 2px solid {color};
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18px;")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #6c757d;
                font-size: 14px;
                font-weight: 600;
                margin: 0;
            }}
        """)

        header_layout.addWidget(icon_container)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 24px;
                font-weight: bold;
                margin-top: 10px;
            }}
        """)
        layout.addWidget(value_label)

        # Trend indicator (placeholder)
        trend_label = QLabel("―")
        trend_label.setStyleSheet("""
            QLabel {
                color: #adb5bd;
                font-size: 12px;
                font-style: italic;
            }
        """)
        layout.addWidget(trend_label)

        return card, value_label

    def create_summary_tab(self):
        """Create financial summary tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Summary cards
        cards_layout = QHBoxLayout()
        
        # Total Balance Card
        balance_card = self.create_summary_card("💰", "Saldo Total", "Rp 0", "#27ae60")
        self.balance_value = balance_card[1]
        cards_layout.addWidget(balance_card[0])
        
        # Monthly Income Card
        income_card = self.create_summary_card("📈", "Pemasukan Bulan Ini", "Rp 0", "#3498db")
        self.income_value = income_card[1]
        cards_layout.addWidget(income_card[0])
        
        # Monthly Expense Card
        expense_card = self.create_summary_card("📉", "Pengeluaran Bulan Ini", "Rp 0", "#e74c3c")
        self.expense_value = expense_card[1]
        cards_layout.addWidget(expense_card[0])
        
        layout.addLayout(cards_layout)
        
        # Charts placeholder
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 20px;
                margin-top: 20px;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        
        chart_title = QLabel("Grafik Keuangan")
        chart_title.setFont(QFont("Arial", 14, QFont.Bold))
        chart_title.setAlignment(Qt.AlignCenter)
        chart_layout.addWidget(chart_title)
        
        chart_placeholder = QLabel("Grafik keuangan akan ditampilkan di sini\\n(Dalam pengembangan)")
        chart_placeholder.setAlignment(Qt.AlignCenter)
        chart_placeholder.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-style: italic;
                font-size: 16px;
                padding: 100px;
            }
        """)
        chart_layout.addWidget(chart_placeholder)
        
        layout.addWidget(chart_frame)
        
        return tab
    
    def create_reports_tab(self):
        """Create reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Report controls
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 10px;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)

        controls_label = QLabel("Jenis Laporan:")
        controls_label.setFont(QFont("Arial", 12, QFont.Bold))

        self.report_type = QComboBox()
        self.report_type.addItems([
            "Laporan Bulanan",
            "Laporan Tahunan",
            "Laporan per Kategori",
            "Laporan Ringkasan"
        ])
        self.report_type.setMinimumWidth(180)

        # Period selection
        period_label = QLabel("Periode:")
        period_label.setFont(QFont("Arial", 11, QFont.Bold))

        self.month_filter = QComboBox()
        self.month_filter.addItems([
            "Semua Bulan", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ])
        self.month_filter.setMinimumWidth(120)

        self.year_filter = QComboBox()
        current_year = datetime.datetime.now().year
        for year in range(current_year - 5, current_year + 2):
            self.year_filter.addItem(str(year))
        self.year_filter.setCurrentText(str(current_year))
        self.year_filter.setMinimumWidth(80)

        generate_button = QPushButton("Generate Laporan")
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        generate_button.clicked.connect(self.generate_report)

        export_pdf_button = QPushButton("Export PDF")
        export_pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_pdf_button.clicked.connect(self.export_report_pdf)

        controls_layout.addWidget(controls_label)
        controls_layout.addWidget(self.report_type)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(period_label)
        controls_layout.addWidget(self.month_filter)
        controls_layout.addWidget(self.year_filter)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(generate_button)
        controls_layout.addWidget(export_pdf_button)
        controls_layout.addStretch()

        layout.addWidget(controls_frame)

        # Report content
        self.report_content = QTextEdit()
        self.report_content.setReadOnly(True)
        self.report_content.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
        """)

        # Default report content
        default_report = self.generate_default_report()
        self.report_content.setHtml(default_report)

        layout.addWidget(self.report_content)

        return tab
    
    def create_summary_card(self, icon, title, value, color):
        """Create summary card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 5px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 18px;
                font-weight: bold;
                margin-top: 5px;
            }}
        """)
        layout.addWidget(value_label)
        
        return card, value_label

    def get_user_data_file(self):
        """Get user-specific data file path"""
        if not self.current_user:
            # Get current user from api_client if available
            if hasattr(self.api_client, 'current_user') and self.api_client.current_user:
                self.current_user = self.api_client.current_user.get('username', 'unknown')
            else:
                self.current_user = 'unknown'

        # Create user data directory if not exists
        user_data_dir = os.path.join(os.path.dirname(__file__), '..', 'user_data')
        os.makedirs(user_data_dir, exist_ok=True)

        return os.path.join(user_data_dir, f'keuangan_{self.current_user}.json')

    def save_user_keuangan_data(self):
        """Save user-specific keuangan data to local file"""
        try:
            data_file = self.get_user_data_file()
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.keuangan_data, f, ensure_ascii=False, indent=2)
            self.log_message.emit(f"Data keuangan user {self.current_user} berhasil disimpan")
        except Exception as e:
            self.log_message.emit(f"Error saving user keuangan data: {str(e)}")

    def load_user_keuangan_data(self):
        """Load keuangan data from API"""
        print("[DEBUG] ========== load_user_keuangan_data START ==========")

        # Clear semua data lama
        self.keuangan_data = []
        self.filtered_data = []
        self.table_widget.setRowCount(0)

        try:
            # Check if user is logged in
            if not self.api_client.user_data:
                print("[ERROR] User not logged in, cannot load keuangan data")
                return

            user_id = self.api_client.user_data.get('id_pengguna')
            print(f"[DEBUG] Loading keuangan for user_id: {user_id}")

            result = self.api_client.get_keuangan()
            print(f"[DEBUG] get_keuangan API result: {result}")

            if result.get('success'):
                response_data = result.get('data', {})
                print(f"[DEBUG] Response data type: {type(response_data)}")
                print(f"[DEBUG] Response data keys: {response_data.keys() if isinstance(response_data, dict) else 'Not a dict'}")

                if isinstance(response_data, dict):
                    status = response_data.get('status')
                    print(f"[DEBUG] Response status: {status}")

                    if status == 'success':
                        data_list = response_data.get('data', [])
                        print(f"[DEBUG] Data list type: {type(data_list)}, length: {len(data_list) if isinstance(data_list, list) else 'Not a list'}")

                        if isinstance(data_list, list):
                            self.keuangan_data = data_list
                            print(f"[DEBUG] ✓ Loaded {len(self.keuangan_data)} keuangan records")

                            if self.keuangan_data:
                                print(f"[DEBUG] First record keys: {self.keuangan_data[0].keys()}")
                                print(f"[DEBUG] First record: {self.keuangan_data[0]}")
                        else:
                            print(f"[ERROR] Data is not a list: {data_list}")
                            self.keuangan_data = []
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        print(f"[ERROR] API returned error status: {error_msg}")
                        self.keuangan_data = []
                else:
                    print(f"[ERROR] Response data is not a dict: {response_data}")
                    self.keuangan_data = []
            else:
                error_msg = result.get('data', 'Unknown error')
                print(f"[ERROR] API call failed: {error_msg}")
                self.keuangan_data = []

            # Update filtered data and table
            self.filtered_data = self.keuangan_data.copy()
            print(f"[DEBUG] Filtered data length: {len(self.filtered_data)}")

            self.update_table()
            self.update_statistics()

            print(f"[DEBUG] ✓ Table and statistics updated")
            print("[DEBUG] ========== load_user_keuangan_data END ==========")

        except Exception as e:
            print(f"[ERROR] ========== EXCEPTION in load_user_keuangan_data ==========")
            print(f"[ERROR] Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            self.keuangan_data = []
            self.filtered_data = []
            self.update_table()

    def add_transaksi(self):
        """Add new transaction"""
        try:
            dialog = KeuanganDialog(self)
            # Gunakan QDialog.Accepted (bukan dialog.Accepted)
            if dialog.exec_() == QDialog.Accepted:
                new_data = dialog.get_data()
                print(f"[DEBUG] ========== ADD TRANSAKSI START ==========")
                print(f"[DEBUG] New transaksi data from dialog: {new_data}")

                # user_id sudah ditambahkan otomatis di api_client.add_keuangan()
                result = self.api_client.add_keuangan(new_data)
                print(f"[DEBUG] API add_keuangan result: {result}")

                if result.get('success'):
                    response_data = result.get('data', {})
                    if response_data.get('status') == 'success':
                        print(f"[DEBUG] Transaksi berhasil disimpan dengan ID: {response_data.get('id')}")
                        # Tunggu sebentar agar database selesai menyimpan
                        QTimer.singleShot(500, self.load_user_keuangan_data)
                        QMessageBox.information(self, "Sukses", "Transaksi baru berhasil ditambahkan")
                        self.log_message.emit("Transaksi baru berhasil ditambahkan")
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        print(f"[ERROR] API error: {error_msg}")
                        QMessageBox.warning(self, "Error", f"Gagal menambah transaksi: {error_msg}")
                else:
                    error_msg = result.get('data', 'Unknown error')
                    print(f"[ERROR] Connection error: {error_msg}")
                    QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {error_msg}")
        except Exception as e:
            print(f"[ERROR] Exception in add_transaksi: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error menambahkan transaksi: {str(e)}")
            self.log_message.emit(f"Error menambah transaksi: {str(e)}")

    def view_transaksi(self):
        """View selected transaction details"""
        current_row = self.table_widget.currentRow()
        if current_row < 0 or current_row >= len(self.filtered_data):
            QMessageBox.warning(self, "Warning", "Pilih transaksi yang akan dilihat")
            return

        selected_data = self.filtered_data[current_row]

        # Nama hari dalam Bahasa Indonesia
        nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

        # Format tanggal - Format: Hari, dd/mm/yyyy
        tanggal = selected_data.get('tanggal', 'N/A')
        tanggal_formatted = 'N/A'
        if tanggal and tanggal != 'N/A':
            try:
                dt = None
                if isinstance(tanggal, str):
                    tanggal_str = tanggal.strip()
                    # Jika ada waktu (T atau space dengan angka jam)
                    if 'T' in tanggal_str or (' ' in tanggal_str and ':' in tanggal_str):
                        try:
                            dt = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00'))
                        except:
                            parts = tanggal_str.split(' ')[0] if ' ' in tanggal_str else tanggal_str
                            dt = datetime.datetime.strptime(parts, '%Y-%m-%d')
                    elif '-' in tanggal_str:
                        parts = tanggal_str.split(' ')[0]
                        dt = datetime.datetime.strptime(parts, '%Y-%m-%d')
                    elif '/' in tanggal_str:
                        try:
                            dt = datetime.datetime.strptime(tanggal_str, '%d/%m/%Y')
                        except:
                            try:
                                dt = datetime.datetime.strptime(tanggal_str, '%m/%d/%Y')
                            except:
                                dt = None

                    if dt:
                        tanggal_formatted = dt.strftime('%d/%m/%Y')
                    else:
                        tanggal_formatted = str(tanggal)
            except Exception as e:
                print(f"[WARN] Failed to parse date in view_transaksi '{tanggal}': {e}")
                if ' ' in str(tanggal):
                    tanggal_formatted = str(tanggal).split(' ')[0]
                else:
                    tanggal_formatted = str(tanggal)
        tanggal = tanggal_formatted

        detail_text = f"""
Detail Transaksi:

Tanggal: {tanggal}
Jenis: {selected_data.get('jenis', 'N/A')}
Kategori: {selected_data.get('kategori', 'N/A')}
Keterangan: {selected_data.get('keterangan', 'N/A')}
Jumlah: Rp {selected_data.get('jumlah', 0):,.0f}
"""

        QMessageBox.information(self, "Detail Transaksi", detail_text)

    def edit_transaksi(self):
        """Edit selected transaction"""
        try:
            current_row = self.table_widget.currentRow()
            if current_row < 0 or current_row >= len(self.filtered_data):
                QMessageBox.warning(self, "Warning", "Pilih transaksi yang akan diedit")
                return

            selected_data = self.filtered_data[current_row]
            dialog = KeuanganDialog(self, selected_data)
            # Gunakan QDialog.Accepted (bukan KeuanganDialog.Accepted)
            if dialog.exec_() == QDialog.Accepted:
                updated_data = dialog.get_data()
                keuangan_id = selected_data.get('id_keuangan') or selected_data.get('id')

                if not keuangan_id:
                    QMessageBox.warning(self, "Error", "ID transaksi tidak ditemukan")
                    return

                print(f"[DEBUG] Updating transaksi ID: {keuangan_id} with data: {updated_data}")

                result = self.api_client.update_keuangan(keuangan_id, updated_data)
                print(f"[DEBUG] API update_keuangan result: {result}")

                if result.get('success'):
                    response_data = result.get('data', {})
                    if response_data.get('status') == 'success':
                        print(f"[DEBUG] Transaksi berhasil diupdate")
                        QTimer.singleShot(500, self.load_user_keuangan_data)
                        QMessageBox.information(self, "Sukses", "Transaksi berhasil diperbarui")
                        self.log_message.emit("Transaksi berhasil diperbarui")
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        print(f"[ERROR] API error: {error_msg}")
                        QMessageBox.warning(self, "Error", f"Gagal update transaksi: {error_msg}")
                else:
                    error_msg = result.get('data', 'Unknown error')
                    print(f"[ERROR] Connection error: {error_msg}")
                    QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {error_msg}")
        except Exception as e:
            print(f"[ERROR] Exception in edit_transaksi: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error mengedit transaksi: {str(e)}")
            self.log_message.emit(f"Error edit transaksi: {str(e)}")

    def delete_transaksi(self):
        """Delete selected transaction"""
        try:
            current_row = self.table_widget.currentRow()
            if current_row < 0 or current_row >= len(self.filtered_data):
                QMessageBox.warning(self, "Warning", "Pilih transaksi yang akan dihapus")
                return

            selected_data = self.filtered_data[current_row]
            keterangan = selected_data.get('keterangan', 'Unknown')  # Hanya keterangan
            reply = QMessageBox.question(self, "Konfirmasi",
                                       f"Apakah Anda yakin ingin menghapus transaksi '{keterangan}'?",
                                       QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                keuangan_id = selected_data.get('id_keuangan') or selected_data.get('id')

                if not keuangan_id:
                    QMessageBox.warning(self, "Error", "ID transaksi tidak ditemukan")
                    return

                print(f"[DEBUG] Deleting transaksi ID: {keuangan_id}")

                result = self.api_client.delete_keuangan(keuangan_id)
                print(f"[DEBUG] API delete_keuangan result: {result}")

                if result.get('success'):
                    response_data = result.get('data', {})
                    if response_data.get('status') == 'success':
                        print(f"[DEBUG] Transaksi berhasil dihapus")
                        QTimer.singleShot(500, self.load_user_keuangan_data)
                        QMessageBox.information(self, "Sukses", "Transaksi berhasil dihapus")
                        self.log_message.emit("Transaksi berhasil dihapus")
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        print(f"[ERROR] API error: {error_msg}")
                        QMessageBox.warning(self, "Error", f"Gagal hapus transaksi: {error_msg}")
                else:
                    error_msg = result.get('data', 'Unknown error')
                    print(f"[ERROR] Connection error: {error_msg}")
                    QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {error_msg}")
        except Exception as e:
            print(f"[ERROR] Exception in delete_transaksi: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error menghapus transaksi: {str(e)}")
            self.log_message.emit(f"Error delete transaksi: {str(e)}")

    def create_action_buttons_for_row(self, row):
        """Create action buttons for table row - matching dokumen.py style"""
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(3, 3, 3, 3)  # Balanced margins for perfect centering
        action_layout.setSpacing(3)  # Compact spacing between buttons
        action_layout.setAlignment(Qt.AlignCenter)  # Center align buttons

        # View button with view.png icon
        view_button = QPushButton()
        view_icon = QIcon("client/assets/view.png")
        view_button.setIcon(view_icon)
        view_button.setIconSize(QSize(16, 16))  # Slightly larger icon for visibility
        view_button.setFixedSize(28, 28)  # Slightly larger button
        view_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        view_button.setToolTip("Lihat Detail Transaksi")
        view_button.clicked.connect(lambda _, r=row: self.view_row_transaksi(r))
        action_layout.addWidget(view_button)

        # Edit button with edit.png icon
        edit_button = QPushButton()
        edit_icon = QIcon("client/assets/edit.png")
        edit_button.setIcon(edit_icon)
        edit_button.setIconSize(QSize(16, 16))  # Slightly larger icon for visibility
        edit_button.setFixedSize(28, 28)  # Slightly larger button
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        edit_button.setToolTip("Edit Transaksi")
        edit_button.clicked.connect(lambda _, r=row: self.edit_row_transaksi(r))
        action_layout.addWidget(edit_button)

        # Delete button with delete.png icon
        delete_button = QPushButton()
        delete_icon = QIcon("client/assets/delete.png")
        delete_button.setIcon(delete_icon)
        delete_button.setIconSize(QSize(16, 16))  # Slightly larger icon for visibility
        delete_button.setFixedSize(28, 28)  # Slightly larger button
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        delete_button.setToolTip("Hapus Transaksi")
        delete_button.clicked.connect(lambda _, r=row: self.delete_row_transaksi(r))
        action_layout.addWidget(delete_button)

        return action_widget

    def view_row_transaksi(self, row):
        """View transaction from specific row - using sorted_data"""
        try:
            if row < 0 or row >= len(self.sorted_data):
                print(f"[ERROR] Invalid row index: {row}, sorted_data length: {len(self.sorted_data)}")
                return

            selected_data = self.sorted_data[row]
            print(f"[DEBUG] view_row_transaksi row={row}, data: {selected_data}")

            # Nama hari dalam Bahasa Indonesia
            nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

            # Format tanggal - Format: Hari, dd/mm/yyyy
            tanggal = selected_data.get('tanggal', 'N/A')
            tanggal_formatted = 'N/A'
            if tanggal and tanggal != 'N/A':
                try:
                    dt = None
                    if isinstance(tanggal, str):
                        tanggal_str = tanggal.strip()
                        # Handle berbagai format
                        if 'T' in tanggal_str or (' ' in tanggal_str and ':' in tanggal_str):
                            try:
                                dt = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00'))
                            except:
                                parts = tanggal_str.split(' ')[0] if ' ' in tanggal_str else tanggal_str
                                dt = datetime.datetime.strptime(parts, '%Y-%m-%d')
                        elif '-' in tanggal_str:
                            parts = tanggal_str.split(' ')[0]
                            dt = datetime.datetime.strptime(parts, '%Y-%m-%d')
                        elif '/' in tanggal_str:
                            try:
                                dt = datetime.datetime.strptime(tanggal_str, '%d/%m/%Y')
                            except:
                                try:
                                    dt = datetime.datetime.strptime(tanggal_str, '%m/%d/%Y')
                                except:
                                    dt = None

                        if dt:
                            tanggal_formatted = dt.strftime('%d/%m/%Y')
                        else:
                            tanggal_formatted = str(tanggal)
                except Exception as e:
                    print(f"[WARN] Failed to parse date in view_row_transaksi: {e}")
                    if ' ' in str(tanggal):
                        tanggal_formatted = str(tanggal).split(' ')[0]
                    else:
                        tanggal_formatted = str(tanggal)
            tanggal = tanggal_formatted

            detail_text = f"""
Detail Transaksi:

Tanggal: {tanggal}
Jenis: {selected_data.get('jenis', 'N/A')}
Kategori: {selected_data.get('kategori', 'N/A')}
Keterangan: {selected_data.get('keterangan', 'N/A')}
Jumlah: Rp {selected_data.get('jumlah', 0):,.0f}
"""

            QMessageBox.information(self, "Detail Transaksi", detail_text)
        except Exception as e:
            print(f"[ERROR] Exception in view_row_transaksi: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error menampilkan detail: {str(e)}")

    def edit_row_transaksi(self, row):
        """Edit transaction from specific row - using sorted_data"""
        try:
            if row < 0 or row >= len(self.sorted_data):
                print(f"[ERROR] Invalid row index: {row}, sorted_data length: {len(self.sorted_data)}")
                return

            selected_data = self.sorted_data[row]
            print(f"[DEBUG] edit_row_transaksi row={row}, data: {selected_data}")

            dialog = KeuanganDialog(self, selected_data)
            if dialog.exec_() == QDialog.Accepted:
                updated_data = dialog.get_data()
                keuangan_id = selected_data.get('id_keuangan') or selected_data.get('id')

                if not keuangan_id:
                    QMessageBox.warning(self, "Error", "ID transaksi tidak ditemukan")
                    return

                print(f"[DEBUG] Updating transaksi ID: {keuangan_id} with data: {updated_data}")

                result = self.api_client.update_keuangan(keuangan_id, updated_data)
                print(f"[DEBUG] API update_keuangan result: {result}")

                if result.get('success'):
                    response_data = result.get('data', {})
                    if response_data.get('status') == 'success':
                        print(f"[DEBUG] Transaksi berhasil diupdate")
                        QTimer.singleShot(500, self.load_user_keuangan_data)
                        QMessageBox.information(self, "Sukses", "Transaksi berhasil diperbarui")
                        self.log_message.emit("Transaksi berhasil diperbarui")
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        print(f"[ERROR] API error: {error_msg}")
                        QMessageBox.warning(self, "Error", f"Gagal update transaksi: {error_msg}")
                else:
                    error_msg = result.get('data', 'Unknown error')
                    print(f"[ERROR] Connection error: {error_msg}")
                    QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {error_msg}")
        except Exception as e:
            print(f"[ERROR] Exception in edit_row_transaksi: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error mengedit transaksi: {str(e)}")
            self.log_message.emit(f"Error edit transaksi: {str(e)}")

    def delete_row_transaksi(self, row):
        """Delete transaction from specific row - using sorted_data"""
        try:
            if row < 0 or row >= len(self.sorted_data):
                print(f"[ERROR] Invalid row index: {row}, sorted_data length: {len(self.sorted_data)}")
                return

            selected_data = self.sorted_data[row]
            print(f"[DEBUG] delete_row_transaksi row={row}, data: {selected_data}")

            keterangan = selected_data.get('keterangan', 'Unknown')
            reply = QMessageBox.question(self, "Konfirmasi",
                                       f"Apakah Anda yakin ingin menghapus transaksi '{keterangan}'?",
                                       QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                keuangan_id = selected_data.get('id_keuangan') or selected_data.get('id')

                if not keuangan_id:
                    QMessageBox.warning(self, "Error", "ID transaksi tidak ditemukan")
                    return

                print(f"[DEBUG] Deleting transaksi ID: {keuangan_id}")

                result = self.api_client.delete_keuangan(keuangan_id)
                print(f"[DEBUG] API delete_keuangan result: {result}")

                if result.get('success'):
                    response_data = result.get('data', {})
                    if response_data.get('status') == 'success':
                        print(f"[DEBUG] Transaksi berhasil dihapus")
                        QTimer.singleShot(500, self.load_user_keuangan_data)
                        QMessageBox.information(self, "Sukses", "Transaksi berhasil dihapus")
                        self.log_message.emit("Transaksi berhasil dihapus")
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        print(f"[ERROR] API error: {error_msg}")
                        QMessageBox.warning(self, "Error", f"Gagal hapus transaksi: {error_msg}")
                else:
                    error_msg = result.get('data', 'Unknown error')
                    print(f"[ERROR] Connection error: {error_msg}")
                    QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {error_msg}")
        except Exception as e:
            print(f"[ERROR] Exception in delete_row_transaksi: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error menghapus transaksi: {str(e)}")
            self.log_message.emit(f"Error delete transaksi: {str(e)}")

    def export_data(self):
        """Export transaction data to CSV"""
        if not self.filtered_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data Keuangan",
            f"keuangan_{self.current_user}_{date.today().isoformat()}.csv",
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Tanggal', 'Jenis', 'Kategori', 'Keterangan', 'Jumlah']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for transaksi in self.filtered_data:
                        # Format tanggal - hanya tanggal tanpa jam
                        tanggal = transaksi.get('tanggal', '')
                        if tanggal:
                            try:
                                if isinstance(tanggal, str):
                                    if 'T' in tanggal or (' ' in tanggal and ':' in tanggal):
                                        dt = datetime.datetime.fromisoformat(tanggal.replace('Z', '+00:00'))
                                        tanggal = dt.strftime('%d/%m/%Y')
                                    elif '-' in tanggal:
                                        parts = tanggal.split(' ')[0]
                                        dt = datetime.datetime.strptime(parts, '%Y-%m-%d')
                                        tanggal = dt.strftime('%d/%m/%Y')
                            except:
                                if ' ' in str(tanggal):
                                    tanggal = str(tanggal).split(' ')[0]

                        writer.writerow({
                            'Tanggal': tanggal,
                            'Jenis': transaksi.get('jenis', ''),
                            'Kategori': transaksi.get('kategori', ''),
                            'Keterangan': transaksi.get('keterangan', ''),
                            'Jumlah': transaksi.get('jumlah', 0)
                        })

                QMessageBox.information(self, "Export Berhasil", f"Data berhasil diekspor ke:\\n{file_path}")
                self.log_message.emit(f"Data keuangan berhasil diekspor ke {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mengekspor data:\\n{str(e)}")
                self.log_message.emit(f"Error export data: {str(e)}")

    def load_keuangan_data(self):
        """Load keuangan data from API (broadcast data only)"""
        try:
            result = self.api_client.get_broadcast_keuangan()  # This would be a new API endpoint
            
            if result["success"]:
                data = result.get("data", [])
                if isinstance(data, list):
                    self.keuangan_data = data
                elif isinstance(data, dict) and "data" in data:
                    self.keuangan_data = data["data"]
                else:
                    self.keuangan_data = []
                
                self.filtered_data = self.keuangan_data.copy()
                self.update_table()
                self.update_statistics()
                self.update_summary()
                self.log_message.emit(f"Data keuangan berhasil dimuat: {len(self.keuangan_data)} record")
                
            else:
                error_msg = result.get("data", "Unknown error")
                QMessageBox.warning(self, "Error", f"Gagal memuat data keuangan:\\n{error_msg}")
                self.log_message.emit(f"Gagal memuat data keuangan: {error_msg}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saat memuat data keuangan:\\n{str(e)}")
            self.log_message.emit(f"Error memuat data keuangan: {str(e)}")

    def update_table(self):
        """Update table with filtered data (optimized for performance)"""
        print(f"[DEBUG] update_table called with {len(self.filtered_data)} records")

        self.table_widget.setRowCount(len(self.filtered_data))

        if len(self.filtered_data) == 0:
            print("[DEBUG] No data to display in table")
            return

        # Sort data by date (oldest first) for correct running balance calculation
        self.sorted_data = sorted(self.filtered_data, key=lambda x: x.get('tanggal', '') or x.get('created_at', '') or '')

        print(f"[DEBUG] Sorted {len(self.sorted_data)} records for display")

        # OPTIMIZATION: Prepare all data first, then update table in batch
        # This reduces GUI updates and improves responsiveness
        table_data = self._prepare_table_data()
        self._populate_table_optimized(table_data)

        print(f"[DEBUG] Table populated with {len(self.sorted_data)} rows successfully")

    def _prepare_table_data(self):
        """Prepare table data without updating GUI (CPU-bound work)"""
        """OPTIMIZATION: Separates data preparation from GUI updates"""
        running_balance = 0
        table_data = []

        for transaksi in self.sorted_data:
            # Parse tanggal
            tanggal = transaksi.get('tanggal', '') or transaksi.get('created_at', '') or 'N/A'
            tanggal_formatted = self._format_date(tanggal)

            # Get jenis and kategori
            jenis = (transaksi.get('jenis', '') or transaksi.get('kategori', '') or 'N/A').lower()
            kategori = transaksi.get('sub_kategori') or transaksi.get('kategori', 'Lainnya')
            keterangan = transaksi.get('keterangan', 'N/A')

            # Calculate jumlah and running balance
            jumlah = transaksi.get('jumlah', 0) or transaksi.get('nominal', 0) or 0
            try:
                jumlah = float(jumlah)
                if jenis == 'pemasukan':
                    running_balance += jumlah
                    jumlah_text = f"+{jumlah:,.0f}"
                else:
                    running_balance -= jumlah
                    jumlah_text = f"-{jumlah:,.0f}"
            except:
                jumlah_text = "0"

            # Store prepared data
            table_data.append({
                'tanggal_formatted': tanggal_formatted,
                'jenis': jenis,
                'jenis_display': transaksi.get('jenis', '') or transaksi.get('kategori', '') or 'N/A',
                'kategori': kategori,
                'keterangan': keterangan,
                'jumlah_text': jumlah_text,
                'running_balance': running_balance,
                'transaksi': transaksi
            })

        return table_data

    def _format_date(self, tanggal):
        """Format date string in Indonesian format (dd/mm/yyyy) - tanggal saja tanpa hari"""
        tanggal_formatted = 'N/A'

        if tanggal and tanggal != 'N/A':
            try:
                dt = None
                if isinstance(tanggal, str):
                    tanggal_str = tanggal.strip()

                    # Handle RFC 1123 / GMT format (Mon, 17 Nov 2025 00:00:00 GMT)
                    if 'GMT' in tanggal_str or tanggal_str.count(',') == 1:
                        try:
                            # Parse RFC 1123 format
                            from email.utils import parsedate_to_datetime
                            dt = parsedate_to_datetime(tanggal_str)
                        except:
                            # Fallback: extract date parts manually
                            # Format: "Mon, 17 Nov 2025 00:00:00 GMT"
                            try:
                                parts = tanggal_str.split(',')[1].strip().split()  # "17 Nov 2025 00:00:00 GMT"
                                date_part = ' '.join(parts[:3])  # "17 Nov 2025"
                                dt = datetime.datetime.strptime(date_part, '%d %b %Y')
                            except:
                                pass
                    # Handle ISO format with time (2025-01-15T10:30:00 or 2025-01-15 10:30:00)
                    elif 'T' in tanggal_str or (' ' in tanggal_str and ':' in tanggal_str):
                        try:
                            dt = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00'))
                        except:
                            parts = tanggal_str.split('T')[0] if 'T' in tanggal_str else tanggal_str.split(' ')[0]
                            dt = datetime.datetime.strptime(parts, '%Y-%m-%d')
                    # Handle date only format (2025-01-15)
                    elif '-' in tanggal_str:
                        parts = tanggal_str.split(' ')[0] if ' ' in tanggal_str else tanggal_str
                        dt = datetime.datetime.strptime(parts, '%Y-%m-%d')
                    # Handle already formatted dates (15/01/2025)
                    elif '/' in tanggal_str:
                        try:
                            dt = datetime.datetime.strptime(tanggal_str, '%d/%m/%Y')
                        except:
                            try:
                                dt = datetime.datetime.strptime(tanggal_str, '%m/%d/%Y')
                            except:
                                dt = None

                if dt:
                    # Format sebagai dd/mm/yyyy saja tanpa hari
                    tanggal_formatted = dt.strftime('%d/%m/%Y')
                else:
                    tanggal_formatted = str(tanggal)
            except Exception as e:
                print(f"[WARN] Failed to parse date '{tanggal}': {e}")
                if ' ' in str(tanggal):
                    tanggal_formatted = str(tanggal).split(' ')[0]
                else:
                    tanggal_formatted = str(tanggal)

        return tanggal_formatted

    def _populate_table_optimized(self, table_data):
        """OPTIMIZATION: Populate table with prepared data (GUI-bound work only)"""
        self.table_widget.setUpdatesEnabled(False)  # Disable updates during population

        try:
            for row, data in enumerate(table_data):
                # Set row height once
                self.table_widget.setRowHeight(row, 36)

                # Tanggal
                tanggal_item = QTableWidgetItem(data['tanggal_formatted'])
                tanggal_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, 0, tanggal_item)

                # Jenis
                jenis_item = QTableWidgetItem(data['jenis_display'])
                if data['jenis'] == 'pemasukan':
                    jenis_item.setBackground(QColor("#d5f4e6"))
                    jenis_item.setForeground(QColor("#27ae60"))
                elif data['jenis'] == 'pengeluaran':
                    jenis_item.setBackground(QColor("#fadbd8"))
                    jenis_item.setForeground(QColor("#e74c3c"))
                self.table_widget.setItem(row, 1, jenis_item)

                # Kategori
                self.table_widget.setItem(row, 2, QTableWidgetItem(data['kategori']))

                # Keterangan
                self.table_widget.setItem(row, 3, QTableWidgetItem(data['keterangan']))

                # Jumlah
                jumlah_item = QTableWidgetItem(data['jumlah_text'])
                if data['jenis'] == 'pemasukan':
                    jumlah_item.setForeground(QColor("#27ae60"))
                else:
                    jumlah_item.setForeground(QColor("#e74c3c"))
                self.table_widget.setItem(row, 4, jumlah_item)

                # Saldo
                saldo_item = QTableWidgetItem(f"{data['running_balance']:,.0f}")
                if data['running_balance'] >= 0:
                    saldo_item.setForeground(QColor("#27ae60"))
                else:
                    saldo_item.setForeground(QColor("#e74c3c"))
                self.table_widget.setItem(row, 5, saldo_item)

                # Action buttons
                action_widget = self.create_action_buttons_for_row(row)
                self.table_widget.setCellWidget(row, 6, action_widget)
        finally:
            self.table_widget.setUpdatesEnabled(True)  # Re-enable updates
    
    def filter_data(self):
        """Filter data based on search, type, and category"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        category_filter = self.category_filter.currentText()
        
        self.filtered_data = []
        
        for transaksi in self.keuangan_data:
            # Search filter
            keterangan = (transaksi.get('keterangan', '') or '').lower()  # Hanya keterangan

            if search_text and search_text not in keterangan:
                continue
            
            # Type filter
            jenis = transaksi.get('jenis', '') or transaksi.get('tipe', '')
            if type_filter != "Semua" and jenis.lower() != type_filter.lower():
                continue
            
            # Category filter - support both endpoint formats
            # Endpoint /keuangan uses sub_kategori, endpoint /my uses kategori
            kategori = transaksi.get('sub_kategori') or transaksi.get('kategori', 'Lainnya')
            if category_filter != "Semua" and kategori != category_filter:
                continue
            
            self.filtered_data.append(transaksi)
        
        self.update_table()
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics labels using server inventaris style"""
        total_pemasukan = 0
        total_pengeluaran = 0
        total_transaksi = len(self.filtered_data)

        for transaksi in self.filtered_data:
            jumlah = transaksi.get('jumlah', 0) or transaksi.get('nominal', 0) or 0
            try:
                jumlah = float(jumlah)
                jenis = transaksi.get('jenis', '') or transaksi.get('tipe', '')

                if jenis.lower() == 'pemasukan':
                    total_pemasukan += jumlah
                else:
                    total_pengeluaran += jumlah
            except:
                pass

        saldo = total_pemasukan - total_pengeluaran

        # Update summary widgets using server inventaris style
        if hasattr(self, 'total_transaksi_value'):
            self.total_transaksi_value.setText(str(total_transaksi))

        if hasattr(self, 'total_pemasukan_label'):
            self.total_pemasukan_label.setText(f"Rp {total_pemasukan:,.0f}")

        if hasattr(self, 'total_pengeluaran_label'):
            self.total_pengeluaran_label.setText(f"Rp {total_pengeluaran:,.0f}")

        if hasattr(self, 'total_saldo_label'):
            self.total_saldo_label.setText(f"Rp {saldo:,.0f}")
            # Update saldo color dynamically while maintaining server style
            color = "#3498db" if saldo >= 0 else "#e74c3c"
            bg_color = "#e3f2fd" if saldo >= 0 else "#fadbd8"

            # Update parent widget background color too
            if self.total_saldo_label.parent():
                self.total_saldo_label.parent().setStyleSheet(f"""
                    QWidget {{
                        background-color: {bg_color};
                        border-radius: 4px;
                        padding: 6px;
                    }}
                """)

            self.total_saldo_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    font-weight: bold;
                    color: {color};
                    font-family: Arial, sans-serif;
                    background-color: transparent;
                    padding: 2px;
                    min-height: 16px;
                }}
            """)
    
    def update_summary(self):
        """Update summary cards (not needed anymore as we use update_statistics)"""
        pass
    
    def generate_default_report(self):
        """Generate default financial report for current user"""
        current_date = datetime.datetime.now().strftime("%d/%m/%Y")
        user_name = self.api_client.user_data.get('nama_lengkap', 'User') if self.api_client.user_data else 'User'

        # Calculate totals
        total_transaksi = len(self.filtered_data)
        total_pemasukan = sum(t.get('jumlah', 0) for t in self.filtered_data if (t.get('jenis', '') or '').lower() == 'pemasukan')
        total_pengeluaran = sum(t.get('jumlah', 0) for t in self.filtered_data if (t.get('jenis', '') or '').lower() == 'pengeluaran')
        saldo = total_pemasukan - total_pengeluaran

        return f"""
        <h2 style="color: #27ae60; text-align: center;">LAPORAN KEUANGAN PRIBADI</h2>
        <p style="text-align: center; color: #7f8c8d;">Nama: {user_name}</p>
        <p style="text-align: center; color: #7f8c8d;">Tanggal Laporan: {current_date}</p>
        <hr>

        <h3 style="color: #2c3e50;">📊 RINGKASAN KEUANGAN</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #ecf0f1;">
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Total Transaksi</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right;"><strong>{total_transaksi}</strong></td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Total Pemasukan</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right; color: #27ae60;"><strong>Rp {total_pemasukan:,.0f}</strong></td>
            </tr>
            <tr style="background-color: #ecf0f1;">
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Total Pengeluaran</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right; color: #e74c3c;"><strong>Rp {total_pengeluaran:,.0f}</strong></td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Saldo Akhir</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right; color: {'#27ae60' if saldo >= 0 else '#e74c3c'};"><strong>Rp {saldo:,.0f}</strong></td>
            </tr>
        </table>

        <h3 style="color: #2c3e50; margin-top: 20px;">📋 DAFTAR TRANSAKSI TERAKHIR</h3>
        <p style="color: #7f8c8d; font-size: 11px;">Menampilkan 10 transaksi terakhir</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
            <tr style="background-color: #34495e; color: white;">
                <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Tanggal</th>
                <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Jenis</th>
                <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Kategori</th>
                <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Keterangan</th>
                <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: right;">Jumlah</th>
            </tr>
        </table>

        <hr>
        <p style="color: #7f8c8d; font-size: 10px; text-align: center;">
        Laporan ini menampilkan data keuangan pribadi Anda.<br>
        Dihasilkan otomatis oleh sistem pada {current_date}.
        </p>
        """

    def generate_report(self):
        """Generate financial report based on selected criteria"""
        try:
            report_type = self.report_type.currentText()
            month = self.month_filter.currentIndex()  # 0 = Semua, 1-12 = Jan-Des
            year = int(self.year_filter.currentText())

            # Filter data berdasarkan periode
            filtered_data = self.filtered_data.copy()

            if month > 0:  # Jika bulan dipilih
                filtered_data = [
                    t for t in filtered_data
                    if self._get_month_from_date(t.get('tanggal', '')) == month
                    and self._get_year_from_date(t.get('tanggal', '')) == year
                ]
            else:  # Semua bulan tahun terpilih
                filtered_data = [
                    t for t in filtered_data
                    if self._get_year_from_date(t.get('tanggal', '')) == year
                ]

            # Generate report berdasarkan jenis laporan
            if report_type == "Laporan Bulanan":
                html = self._generate_monthly_report(filtered_data, month, year)
            elif report_type == "Laporan Tahunan":
                html = self._generate_yearly_report(filtered_data, year)
            elif report_type == "Laporan per Kategori":
                html = self._generate_category_report(filtered_data, year)
            else:  # Laporan Ringkasan
                html = self._generate_summary_report(filtered_data, month, year)

            self.report_content.setHtml(html)
            self.log_message.emit(f"Laporan {report_type} berhasil digenerate")

        except Exception as e:
            print(f"[ERROR] Error generating report: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Gagal generate laporan: {str(e)}")

    def _get_month_from_date(self, date_str):
        """Extract month from date string"""
        try:
            if 'T' in date_str or ' ' in date_str:
                dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return dt.month
        except:
            return 0

    def _get_year_from_date(self, date_str):
        """Extract year from date string"""
        try:
            if 'T' in date_str or ' ' in date_str:
                dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return dt.year
        except:
            return 0

    def _generate_monthly_report(self, data, month, year):
        """Generate monthly financial report"""
        month_names = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                      'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        month_name = month_names[month] if month > 0 else 'Semua Bulan'

        total_pemasukan = sum(t.get('jumlah', 0) for t in data if (t.get('jenis', '') or '').lower() == 'pemasukan')
        total_pengeluaran = sum(t.get('jumlah', 0) for t in data if (t.get('jenis', '') or '').lower() == 'pengeluaran')
        saldo = total_pemasukan - total_pengeluaran

        html = f"""
        <h2 style="color: #27ae60; text-align: center;">LAPORAN KEUANGAN BULANAN</h2>
        <p style="text-align: center; color: #7f8c8d;"><strong>{month_name} {year}</strong></p>
        <hr>

        <h3 style="color: #2c3e50;">📊 RINGKASAN BULANAN</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #ecf0f1;">
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Total Transaksi</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right;"><strong>{len(data)}</strong></td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Total Pemasukan</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right; color: #27ae60;"><strong>Rp {total_pemasukan:,.0f}</strong></td>
            </tr>
            <tr style="background-color: #ecf0f1;">
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Total Pengeluaran</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right; color: #e74c3c;"><strong>Rp {total_pengeluaran:,.0f}</strong></td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Saldo Akhir</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right; color: {'#27ae60' if saldo >= 0 else '#e74c3c'};"><strong>Rp {saldo:,.0f}</strong></td>
            </tr>
        </table>

        <h3 style="color: #2c3e50; margin-top: 20px;">📋 DETAIL TRANSAKSI</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
            <tr style="background-color: #34495e; color: white;">
                <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Tanggal</th>
                <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Jenis</th>
                <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Kategori</th>
                <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Keterangan</th>
                <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: right;">Jumlah</th>
            </tr>
        """

        # Nama hari dalam Bahasa Indonesia
        nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

        for transaksi in sorted(data, key=lambda x: x.get('tanggal', '')):
            tanggal = transaksi.get('tanggal', 'N/A')
            tanggal_formatted = 'N/A'
            try:
                dt = None
                if tanggal and tanggal != 'N/A':
                    if 'T' in tanggal or (' ' in tanggal and ':' in tanggal):
                        try:
                            dt = datetime.datetime.fromisoformat(tanggal.replace('Z', '+00:00'))
                        except:
                            parts = tanggal.split(' ')[0] if ' ' in tanggal else tanggal
                            dt = datetime.datetime.strptime(parts, '%Y-%m-%d')
                    elif '-' in tanggal:
                        parts = tanggal.split(' ')[0]
                        dt = datetime.datetime.strptime(parts, '%Y-%m-%d')
                    elif '/' in tanggal:
                        try:
                            dt = datetime.datetime.strptime(tanggal, '%d/%m/%Y')
                        except:
                            try:
                                dt = datetime.datetime.strptime(tanggal, '%m/%d/%Y')
                            except:
                                dt = None

                    if dt:
                        tanggal_formatted = dt.strftime('%d/%m/%Y')
                    else:
                        tanggal_formatted = str(tanggal)
            except Exception as e:
                print(f"[WARN] Failed to parse date in HTML report: {e}")
                if ' ' in str(tanggal):
                    tanggal_formatted = str(tanggal).split(' ')[0]
                else:
                    tanggal_formatted = str(tanggal)
            tanggal = tanggal_formatted

            jenis = transaksi.get('jenis', 'N/A')
            kategori = transaksi.get('kategori', 'N/A')
            keterangan = transaksi.get('keterangan', 'N/A')
            jumlah = transaksi.get('jumlah', 0)
            warna = '#27ae60' if jenis.lower() == 'pemasukan' else '#e74c3c'

            html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #bdc3c7;">{tanggal}</td>
                <td style="padding: 8px; border: 1px solid #bdc3c7; color: {warna};"><strong>{jenis}</strong></td>
                <td style="padding: 8px; border: 1px solid #bdc3c7;">{kategori}</td>
                <td style="padding: 8px; border: 1px solid #bdc3c7;">{keterangan}</td>
                <td style="padding: 8px; border: 1px solid #bdc3c7; text-align: right; color: {warna};"><strong>Rp {jumlah:,.0f}</strong></td>
            </tr>
            """

        html += """
        </table>
        <hr>
        <p style="color: #7f8c8d; font-size: 10px; text-align: center;">
        Laporan ini menampilkan data keuangan pribadi Anda untuk periode yang dipilih.
        </p>
        """

        return html

    def _generate_yearly_report(self, data, year):
        """Generate yearly financial report"""
        total_pemasukan = sum(t.get('jumlah', 0) for t in data if (t.get('jenis', '') or '').lower() == 'pemasukan')
        total_pengeluaran = sum(t.get('jumlah', 0) for t in data if (t.get('jenis', '') or '').lower() == 'pengeluaran')
        saldo = total_pemasukan - total_pengeluaran

        html = f"""
        <h2 style="color: #27ae60; text-align: center;">LAPORAN KEUANGAN TAHUNAN</h2>
        <p style="text-align: center; color: #7f8c8d;"><strong>Tahun {year}</strong></p>
        <hr>

        <h3 style="color: #2c3e50;">📊 RINGKASAN TAHUNAN</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #ecf0f1;">
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Total Transaksi</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right;"><strong>{len(data)}</strong></td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Total Pemasukan</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right; color: #27ae60;"><strong>Rp {total_pemasukan:,.0f}</strong></td>
            </tr>
            <tr style="background-color: #ecf0f1;">
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Total Pengeluaran</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right; color: #e74c3c;"><strong>Rp {total_pengeluaran:,.0f}</strong></td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>Saldo Akhir</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right; color: {'#27ae60' if saldo >= 0 else '#e74c3c'};"><strong>Rp {saldo:,.0f}</strong></td>
            </tr>
        </table>

        <h3 style="color: #2c3e50; margin-top: 20px;">📈 GRAFIK PERBANDINGAN</h3>
        <p style="color: #7f8c8d;">Pemasukan: Rp {total_pemasukan:,.0f} | Pengeluaran: Rp {total_pengeluaran:,.0f}</p>

        <hr>
        <p style="color: #7f8c8d; font-size: 10px; text-align: center;">
        Laporan tahunan ini menampilkan ringkasan keuangan pribadi Anda sepanjang tahun {year}.
        </p>
        """

        return html

    def _generate_category_report(self, data, year):
        """Generate category-based financial report"""
        categories = {}
        for transaksi in data:
            kategori = transaksi.get('kategori', 'Lainnya')
            jumlah = transaksi.get('jumlah', 0)
            if kategori not in categories:
                categories[kategori] = 0
            categories[kategori] += jumlah

        html = f"""
        <h2 style="color: #27ae60; text-align: center;">LAPORAN KEUANGAN PER KATEGORI</h2>
        <p style="text-align: center; color: #7f8c8d;"><strong>Tahun {year}</strong></p>
        <hr>

        <h3 style="color: #2c3e50;">📊 RINCIAN PER KATEGORI</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
            <tr style="background-color: #34495e; color: white;">
                <th style="padding: 10px; border: 1px solid #bdc3c7; text-align: left;">Kategori</th>
                <th style="padding: 10px; border: 1px solid #bdc3c7; text-align: right;">Jumlah</th>
                <th style="padding: 10px; border: 1px solid #bdc3c7; text-align: right;">Persentase</th>
            </tr>
        """

        total = sum(categories.values())
        for kategori, jumlah in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            persen = (jumlah / total * 100) if total > 0 else 0
            html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #bdc3c7;"><strong>{kategori}</strong></td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right;">Rp {jumlah:,.0f}</td>
                <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: right;">{persen:.1f}%</td>
            </tr>
            """

        html += """
        </table>

        <hr>
        <p style="color: #7f8c8d; font-size: 10px; text-align: center;">
        Laporan ini menunjukkan distribusi keuangan Anda berdasarkan kategori transaksi.
        </p>
        """

        return html

    def _generate_summary_report(self, data, month, year):
        """Generate summary financial report"""
        month_names = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                      'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        period_str = f"{month_names[month]} {year}" if month > 0 else f"Tahun {year}"

        total_pemasukan = sum(t.get('jumlah', 0) for t in data if (t.get('jenis', '') or '').lower() == 'pemasukan')
        total_pengeluaran = sum(t.get('jumlah', 0) for t in data if (t.get('jenis', '') or '').lower() == 'pengeluaran')
        saldo = total_pemasukan - total_pengeluaran

        html = f"""
        <h2 style="color: #27ae60; text-align: center;">RINGKASAN KEUANGAN PRIBADI</h2>
        <p style="text-align: center; color: #7f8c8d;"><strong>Periode: {period_str}</strong></p>
        <hr>

        <h3 style="color: #2c3e50;">📊 RINGKASAN KEUANGAN</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #d5f4e6;">
                <td style="padding: 15px; border: 1px solid #bdc3c7;"><strong>✓ Total Pemasukan</strong></td>
                <td style="padding: 15px; border: 1px solid #bdc3c7; text-align: right; color: #27ae60; font-size: 16px;"><strong>Rp {total_pemasukan:,.0f}</strong></td>
            </tr>
            <tr style="background-color: #fadbd8;">
                <td style="padding: 15px; border: 1px solid #bdc3c7;"><strong>✗ Total Pengeluaran</strong></td>
                <td style="padding: 15px; border: 1px solid #bdc3c7; text-align: right; color: #e74c3c; font-size: 16px;"><strong>Rp {total_pengeluaran:,.0f}</strong></td>
            </tr>
            <tr style="background-color: {'#d5f4e6' if saldo >= 0 else '#fadbd8'};">
                <td style="padding: 15px; border: 1px solid #bdc3c7;"><strong>💰 Saldo Akhir</strong></td>
                <td style="padding: 15px; border: 1px solid #bdc3c7; text-align: right; color: {'#27ae60' if saldo >= 0 else '#e74c3c'}; font-size: 18px;"><strong>Rp {saldo:,.0f}</strong></td>
            </tr>
        </table>

        <p style="color: #7f8c8d; text-align: center; margin-top: 20px; font-size: 11px;">
        Total {len(data)} transaksi dalam periode {period_str}
        </p>

        <hr>
        <p style="color: #7f8c8d; font-size: 10px; text-align: center;">
        Laporan ringkasan keuangan pribadi Anda.
        </p>
        """

        return html

    def export_report_pdf(self):
        """Export current report to HTML"""
        try:
            # Untuk sekarang, kita akan export sebagai HTML
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Laporan",
                "",
                "HTML Files (*.html);;Text Files (*.txt)"
            )

            if file_path:
                report_html = self.report_content.toHtml()

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <title>Laporan Keuangan</title>
                        <style>
                            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; }}
                            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                            th, td {{ padding: 10px; border: 1px solid #bdc3c7; }}
                            h2 {{ color: #27ae60; text-align: center; }}
                            h3 {{ color: #2c3e50; }}
                        </style>
                    </head>
                    <body>
                        {report_html}
                    </body>
                    </html>
                    """)

                QMessageBox.information(self, "Export Berhasil", f"Laporan berhasil diekspor ke:\\n{file_path}")
                self.log_message.emit(f"Laporan berhasil diekspor ke {file_path}")

        except Exception as e:
            print(f"[ERROR] Error exporting report: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Gagal mengekspor laporan:\\n{str(e)}")
