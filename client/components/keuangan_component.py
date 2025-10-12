# Path: client/components/keuangan_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QPushButton, QFrame,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox,
                             QTabWidget, QTextEdit, QProgressBar, QDialog,
                             QFormLayout, QDateEdit, QSpinBox, QFileDialog, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QSize
from PyQt5.QtGui import QFont, QColor, QIcon
import datetime
import json
import os
from datetime import date

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
        form_layout.addRow("Tanggal:", self.tanggal)

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
        self.current_user = None

        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)

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
            "Tanggal", "Jenis", "Kategori", "Keterangan", "Jumlah (Rp)", "Saldo", "Aksi"
        ])

        # Professional styling
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                gridline-color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 6px 4px;
                border-bottom: 1px solid #f0f0f0;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                border: 2px solid #2196f3;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #d0d0d0;
                border-left: none;
                padding: 6px 4px;
                font-weight: 600;
                font-size: 12px;
                color: #495057;
                text-align: center;
            }
            QHeaderView::section:first {
                border-left: 1px solid #d0d0d0;
                border-top-left-radius: 7px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 7px;
            }
        """)

        # Set column widths with better proportions
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Tanggal
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Jenis
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Kategori
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Keterangan
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Jumlah
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Saldo
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # Aksi

        # Set specific column widths
        self.table_widget.setColumnWidth(0, 100)  # Tanggal
        self.table_widget.setColumnWidth(1, 100)  # Jenis
        self.table_widget.setColumnWidth(2, 120)  # Kategori
        self.table_widget.setColumnWidth(4, 120)  # Jumlah
        self.table_widget.setColumnWidth(5, 120)  # Saldo
        self.table_widget.setColumnWidth(6, 80)   # Aksi

        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(self.table_widget.SelectRows)
        
        layout.addWidget(self.table_widget)

        # Export button at bottom right
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        export_button = self.create_action_button("Export Data", "#16a085", "#1abc9c", "export.png")
        export_button.clicked.connect(self.export_data)
        export_layout.addWidget(export_button)

        layout.addLayout(export_layout)

        return tab

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
        button.setMinimumSize(100, 28)
        button.setMaximumSize(130, 28)

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
        
        controls_label = QLabel("Laporan Keuangan:")
        controls_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        report_type = QComboBox()
        report_type.addItems([
            "Laporan Bulanan", "Laporan Tahunan", 
            "Laporan Kategori", "Laporan Transparansi"
        ])
        
        generate_button = QPushButton("Generate Laporan")
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        
        controls_layout.addWidget(controls_label)
        controls_layout.addWidget(report_type)
        controls_layout.addWidget(generate_button)
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
                font-family: 'Courier New', monospace;
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
        # Clear semua data lama
        self.keuangan_data = []
        self.filtered_data = []
        self.table_widget.setRowCount(0)

        try:
            result = self.api_client.get_keuangan()
            if result.get('success'):
                response_data = result.get('data', {})
                if response_data.get('status') == 'success':
                    self.keuangan_data = response_data.get('data', [])
                else:
                    self.keuangan_data = []
            else:
                self.keuangan_data = []

            self.filtered_data = self.keuangan_data.copy()
            self.update_table()
            self.update_statistics()

        except Exception as e:
            self.keuangan_data = []
            self.filtered_data = []
            self.update_table()

    def add_transaksi(self):
        """Add new transaction"""
        dialog = KeuanganDialog(self)
        if dialog.exec_() == KeuanganDialog.Accepted:
            new_data = dialog.get_data()
            result = self.api_client.add_keuangan(new_data)
            if result.get('success'):
                response_data = result.get('data', {})
                if response_data.get('status') == 'success':
                    self.load_user_keuangan_data()  # Refresh data from API
                    self.log_message.emit("Transaksi baru berhasil ditambahkan")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal menambah transaksi: {response_data.get('message', 'Unknown error')}")
            else:
                QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {result.get('data', 'Unknown error')}")

    def view_transaksi(self):
        """View selected transaction details"""
        current_row = self.table_widget.currentRow()
        if current_row < 0 or current_row >= len(self.filtered_data):
            QMessageBox.warning(self, "Warning", "Pilih transaksi yang akan dilihat")
            return

        selected_data = self.filtered_data[current_row]

        # Format tanggal
        tanggal = selected_data.get('tanggal', 'N/A')
        if tanggal != 'N/A':
            try:
                dt = datetime.datetime.fromisoformat(tanggal)
                tanggal = dt.strftime('%d/%m/%Y')
            except:
                pass

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
        current_row = self.table_widget.currentRow()
        if current_row < 0 or current_row >= len(self.filtered_data):
            QMessageBox.warning(self, "Warning", "Pilih transaksi yang akan diedit")
            return

        selected_data = self.filtered_data[current_row]
        dialog = KeuanganDialog(self, selected_data)
        if dialog.exec_() == KeuanganDialog.Accepted:
            updated_data = dialog.get_data()
            keuangan_id = selected_data.get('id_keuangan') or selected_data.get('id')

            result = self.api_client.update_keuangan(keuangan_id, updated_data)
            if result.get('success'):
                response_data = result.get('data', {})
                if response_data.get('status') == 'success':
                    self.load_user_keuangan_data()
                    self.log_message.emit("Transaksi berhasil diperbarui")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal update transaksi: {response_data.get('message', 'Unknown error')}")
            else:
                QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {result.get('data', 'Unknown error')}")

    def delete_transaksi(self):
        """Delete selected transaction"""
        current_row = self.table_widget.currentRow()
        if current_row < 0 or current_row >= len(self.filtered_data):
            QMessageBox.warning(self, "Warning", "Pilih transaksi yang akan dihapus")
            return

        selected_data = self.filtered_data[current_row]
        keterangan = selected_data.get('keterangan') or selected_data.get('deskripsi') or 'Unknown'
        reply = QMessageBox.question(self, "Konfirmasi",
                                   f"Apakah Anda yakin ingin menghapus transaksi '{keterangan}'?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            keuangan_id = selected_data.get('id_keuangan') or selected_data.get('id')
            result = self.api_client.delete_keuangan(keuangan_id)
            if result.get('success'):
                response_data = result.get('data', {})
                if response_data.get('status') == 'success':
                    self.load_user_keuangan_data()
                    self.log_message.emit("Transaksi berhasil dihapus")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal hapus transaksi: {response_data.get('message', 'Unknown error')}")
            else:
                QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {result.get('data', 'Unknown error')}")

    def create_action_buttons_for_row(self, row):
        """Create action buttons for table row"""
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(2, 1, 2, 1)
        action_layout.setSpacing(2)

        # View button
        view_btn = QPushButton()
        view_icon = QIcon("client/assets/view.png")
        view_btn.setIcon(view_icon)
        view_btn.setIconSize(QSize(12, 12))
        view_btn.setIconSize(QSize(10, 10))
        view_btn.setFixedSize(20, 20)
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border: 1px solid #2980b9;
                border-radius: 2px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                box-shadow: 0 1px 2px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        view_btn.setToolTip("Lihat Detail")
        view_btn.clicked.connect(lambda checked, r=row: self.view_row_transaksi(r))

        # Edit button
        edit_btn = QPushButton()
        edit_icon = QIcon("client/assets/edit.png")
        edit_btn.setIcon(edit_icon)
        edit_btn.setIconSize(QSize(12, 12))
        edit_btn.setIconSize(QSize(10, 10))
        edit_btn.setFixedSize(20, 20)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                border: 1px solid #e67e22;
                border-radius: 2px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #e67e22;
                box-shadow: 0 1px 2px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        edit_btn.setToolTip("Edit Transaksi")
        edit_btn.clicked.connect(lambda checked, r=row: self.edit_row_transaksi(r))

        # Delete button
        delete_btn = QPushButton()
        delete_icon = QIcon("client/assets/delete.png")
        delete_btn.setIcon(delete_icon)
        delete_btn.setIconSize(QSize(12, 12))
        delete_btn.setIconSize(QSize(10, 10))
        delete_btn.setFixedSize(20, 20)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border: 1px solid #c0392b;
                border-radius: 2px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                box-shadow: 0 1px 2px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        delete_btn.setToolTip("Hapus Transaksi")
        delete_btn.clicked.connect(lambda checked, r=row: self.delete_row_transaksi(r))

        action_layout.addWidget(view_btn)
        action_layout.addWidget(edit_btn)
        action_layout.addWidget(delete_btn)

        return action_widget

    def view_row_transaksi(self, row):
        """View transaction from specific row"""
        if row < len(self.filtered_data):
            self.table_widget.selectRow(row)
            self.view_transaksi()

    def edit_row_transaksi(self, row):
        """Edit transaction from specific row"""
        if row < len(self.filtered_data):
            self.table_widget.selectRow(row)
            self.edit_transaksi()

    def delete_row_transaksi(self, row):
        """Delete transaction from specific row"""
        if row < len(self.filtered_data):
            self.table_widget.selectRow(row)
            self.delete_transaksi()

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
                        # Format tanggal
                        tanggal = transaksi.get('tanggal', '')
                        if tanggal:
                            try:
                                dt = datetime.datetime.fromisoformat(tanggal)
                                tanggal = dt.strftime('%d/%m/%Y')
                            except:
                                pass

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
        """Update table with filtered data"""
        self.table_widget.setRowCount(len(self.filtered_data))
        running_balance = 0

        # Sort data by date (oldest first) for correct running balance calculation
        sorted_data = sorted(self.filtered_data, key=lambda x: x.get('tanggal', '') or x.get('created_at', '') or '')

        for row, transaksi in enumerate(sorted_data):  # ✅ Data ASC, saldo benar
            # Tanggal
            tanggal = transaksi.get('tanggal', '') or transaksi.get('created_at', '') or 'N/A'
            if tanggal and tanggal != 'N/A':
                try:
                    if 'T' in tanggal:
                        dt = datetime.datetime.fromisoformat(tanggal.replace('Z', '+00:00'))
                        tanggal = dt.strftime('%d/%m/%Y')
                except:
                    pass
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(tanggal)))

            # Jenis
            jenis = transaksi.get('jenis', '') or transaksi.get('kategori', '') or 'N/A'
            jenis_item = QTableWidgetItem(str(jenis))
            if jenis.lower() == 'pemasukan':
                jenis_item.setBackground(QColor("#d5f4e6"))
                jenis_item.setForeground(QColor("#27ae60"))
            elif jenis.lower() == 'pengeluaran':
                jenis_item.setBackground(QColor("#fadbd8"))
                jenis_item.setForeground(QColor("#e74c3c"))
            self.table_widget.setItem(row, 1, jenis_item)

            # Kategori (sub_kategori dari API atau kategori dari /my endpoint)
            # Endpoint /keuangan menggunakan sub_kategori, endpoint /my menggunakan kategori
            kategori = transaksi.get('sub_kategori') or transaksi.get('kategori', 'Lainnya')
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(kategori)))

            # Keterangan
            keterangan = transaksi.get('keterangan', '') or transaksi.get('deskripsi', '') or 'N/A'
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(keterangan)))

            # Jumlah
            jumlah = transaksi.get('jumlah', 0) or transaksi.get('nominal', 0) or 0
            try:
                jumlah = float(jumlah)
                if jenis.lower() == 'pemasukan':
                    running_balance += jumlah
                    jumlah_text = f"+{jumlah:,.0f}"
                else:
                    running_balance -= jumlah
                    jumlah_text = f"-{jumlah:,.0f}"
            except:
                jumlah_text = "0"

            jumlah_item = QTableWidgetItem(jumlah_text)
            if jenis.lower() == 'pemasukan':
                jumlah_item.setForeground(QColor("#27ae60"))
            else:
                jumlah_item.setForeground(QColor("#e74c3c"))
            self.table_widget.setItem(row, 4, jumlah_item)

            # Saldo
            saldo_item = QTableWidgetItem(f"{running_balance:,.0f}")
            if running_balance >= 0:
                saldo_item.setForeground(QColor("#27ae60"))
            else:
                saldo_item.setForeground(QColor("#e74c3c"))
            self.table_widget.setItem(row, 5, saldo_item)

            # Action buttons
            action_widget = self.create_action_buttons_for_row(row)
            self.table_widget.setCellWidget(row, 6, action_widget)
    
    def filter_data(self):
        """Filter data based on search, type, and category"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        category_filter = self.category_filter.currentText()
        
        self.filtered_data = []
        
        for transaksi in self.keuangan_data:
            # Search filter
            keterangan = (transaksi.get('keterangan', '') or transaksi.get('deskripsi', '')).lower()
            
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
        """Generate default financial report"""
        current_date = datetime.datetime.now().strftime("%d/%m/%Y")
        
        return f"""
        <h2 style="color: #27ae60; text-align: center;">LAPORAN KEUANGAN GEREJA</h2>
        <p style="text-align: center; color: #7f8c8d;">Tanggal: {current_date}</p>
        <hr>
        
        <h3 style="color: #2c3e50;">RINGKASAN KEUANGAN</h3>
        <p>📊 <strong>Total Transaksi:</strong> {len(self.keuangan_data)} record</p>
        <p>💰 <strong>Saldo Saat Ini:</strong> Rp 0 (akan dihitung)</p>
        <p>📈 <strong>Pemasukan Bulan Ini:</strong> Rp 0</p>
        <p>📉 <strong>Pengeluaran Bulan Ini:</strong> Rp 0</p>
        
        <h3 style="color: #2c3e50;">KATEGORI UTAMA</h3>
        <p>• Kolekte Mingguan</p>
        <p>• Persembahan Khusus</p>
        <p>• Donasi Anggota</p>
        <p>• Biaya Operasional</p>
        <p>• Pemeliharaan Gereja</p>
        
        <hr>
        <p style="color: #7f8c8d; font-size: 10px; text-align: center;">
        Laporan ini menampilkan data keuangan yang telah dibroadcast untuk transparansi.<br>
        Data lengkap hanya tersedia bagi admin gereja.
        </p>
        """