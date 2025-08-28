# Path: client/components/dashboard_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QPushButton, QGridLayout, QScrollArea,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter
import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api_client import ApiClient

class DashboardComponent(QWidget):
    
    def __init__(self, api_client, user_data=None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user_data = user_data
        self.is_connected = False
        
        self.setup_ui()
        self.setup_timers()
        self.load_dashboard_data()
    
    def setup_ui(self):
        """Setup dashboard UI dengan navbar styling yang konsisten"""
        self.setStyleSheet("background-color: #f8f9fa;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Page header dengan styling yang sama seperti navbar
        header_section = QFrame()
        header_section.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
                padding: 40px 0px;
                border: none;
            }
        """)
        header_layout = QVBoxLayout(header_section)
        header_layout.setContentsMargins(40, 40, 40, 40)
        
        # Single comprehensive title with better contrast
        title_label = QLabel("Dashboard - Portal Manajemen Gereja Katolik")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 26px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 8px 0px;
                text-align: left;
                background-color: transparent;
            }
        """)
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        description_label = QLabel("Sistem terpadu untuk mengelola aktivitas, data jemaat, keuangan, dan administrasi gereja")
        description_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 15px;
                font-weight: normal;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 8px 0px;
                text-align: left;
                background-color: transparent;
                opacity: 0.9;
            }
        """)
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(description_label)
        
        layout.addWidget(header_section)
        
        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                width: 12px;
                background-color: #f1f3f4;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdc1c6;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #9aa0a6;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Main dashboard summary section (Connection status and basic info)
        self.create_main_dashboard_summary(content_layout)
        
        # Professional data summary sections
        self.create_professional_data_sections(content_layout)
        
        # Additional info section (System stats)
        self.create_additional_info_section(content_layout)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
    
    def create_main_dashboard_summary(self, parent_layout):
        """Create main dashboard summary with connection status and basic info"""
        # Main summary container
        summary_card = QFrame()
        summary_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
                padding: 30px;
                margin: 10px 0px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
        """)
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setSpacing(30)
        
        # Top section with welcome and connection
        top_section = QHBoxLayout()
        top_section.setSpacing(40)
        
        # Left side - Welcome section
        welcome_container = QVBoxLayout()
        welcome_container.setSpacing(15)
        
        # Welcome header with icon
        welcome_header = QHBoxLayout()
        welcome_header.setSpacing(15)
        
        welcome_icon = QLabel("🏛️")
        welcome_icon.setStyleSheet("font-size: 36px;")
        
        welcome_text = QVBoxLayout()
        welcome_text.setSpacing(5)
        
        self.welcome_title = QLabel("Dashboard Portal Gereja")
        self.welcome_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                background-color: transparent;
            }
        """)
        
        self.user_greeting = QLabel("Selamat Datang")
        self.user_greeting.setStyleSheet("""
            QLabel {
                color: #2980b9;
                font-size: 17px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                background-color: transparent;
            }
        """)
        
        welcome_desc = QLabel("Sistem Manajemen Gereja Katolik Santa Maria Ratu Damai")
        welcome_desc.setStyleSheet("""
            QLabel {
                color: #5a6c7d;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                background-color: transparent;
            }
        """)
        welcome_desc.setWordWrap(True)
        
        welcome_text.addWidget(self.welcome_title)
        welcome_text.addWidget(self.user_greeting)
        welcome_text.addWidget(welcome_desc)
        
        welcome_header.addWidget(welcome_icon)
        welcome_header.addLayout(welcome_text)
        welcome_header.addStretch()
        
        welcome_container.addLayout(welcome_header)
        top_section.addLayout(welcome_container, 2)
        
        # Right side - Connection status
        connection_container = QVBoxLayout()
        connection_container.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        # Connection status card
        self.connection_indicator = QFrame()
        self.connection_indicator.setMinimumSize(280, 90)
        self.connection_indicator.setMaximumHeight(120)
        self.connection_indicator.setStyleSheet("""
            QFrame {
                background-color: #fff5f5;
                border: none;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 2px 4px rgba(231, 76, 60, 0.1);
            }
        """)
        
        indicator_layout = QHBoxLayout(self.connection_indicator)
        indicator_layout.setSpacing(15)
        
        self.connection_icon = QLabel("🔴")
        self.connection_icon.setStyleSheet("font-size: 32px;")
        
        status_info = QVBoxLayout()
        status_info.setSpacing(5)
        
        status_label = QLabel("Status Koneksi")
        status_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                background-color: transparent;
            }
        """)
        
        self.connection_status = QLabel("Terputus dari Server")
        self.connection_status.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                background-color: transparent;
            }
        """)
        
        self.connection_detail = QLabel("Mencoba menghubungkan...")
        self.connection_detail.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                background-color: transparent;
            }
        """)
        
        status_info.addWidget(status_label)
        status_info.addWidget(self.connection_status)
        status_info.addWidget(self.connection_detail)
        
        indicator_layout.addWidget(self.connection_icon)
        indicator_layout.addLayout(status_info)
        
        connection_container.addWidget(self.connection_indicator)
        top_section.addLayout(connection_container, 1)
        
        summary_layout.addLayout(top_section)
        
        # Bottom section - Stats cards
        stats_section = QVBoxLayout()
        stats_section.setSpacing(15)
        
        # Stats header
        stats_header = QLabel("📋 Ringkasan Sistem")
        stats_header.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 17px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                padding-left: 5px;
                background-color: transparent;
            }
        """)
        stats_section.addWidget(stats_header)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        # Create stat cards
        self.server_status_card = self.create_modern_stat_card("Status Server", "Checking...", "🖥️", "#3498db")
        stats_grid.addWidget(self.server_status_card[0], 0, 0)
        
        self.last_sync_card = self.create_modern_stat_card("Sinkronisasi", "Never", "🔄", "#9b59b6")
        stats_grid.addWidget(self.last_sync_card[0], 0, 1)
        
        self.user_info_card = self.create_modern_stat_card("User Info", "Loading...", "👤", "#2ecc71")
        stats_grid.addWidget(self.user_info_card[0], 0, 2)
        
        self.system_info_card = self.create_modern_stat_card("Sistem", "Client v1.0", "⚙️", "#f39c12")
        stats_grid.addWidget(self.system_info_card[0], 0, 3)
        
        stats_section.addLayout(stats_grid)
        summary_layout.addLayout(stats_section)
        
        parent_layout.addWidget(summary_card)
    
    def create_modern_stat_card(self, title, value, icon, color):
        """Create modern stat card with clean design"""
        card = QFrame()
        card.setFixedHeight(110)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: none;
                padding: 15px;
                margin: 3px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            }}
            QFrame:hover {{
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                background-color: #fafafa;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #5a6c7d;
                font-size: 11px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin: 0px;
                background-color: transparent;
            }
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                background-color: transparent;
            }}
        """)
        value_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        return card, value_label
    
    def create_stats_card(self, title, value, color, icon):
        """Create individual stats card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e9ecef;
                padding: 25px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 20px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        layout.addWidget(value_label)
        
        return card, value_label
    
    def create_additional_info_section(self, parent_layout):
        """Create quick access navigation section"""
        nav_card = QFrame()
        nav_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
                padding: 25px;
                margin: 15px 0px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
        """)
        nav_layout = QVBoxLayout(nav_card)
        nav_layout.setSpacing(25)
        
        # Section header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        header_icon = QLabel("⚡")
        header_icon.setStyleSheet("font-size: 28px;")
        
        header_text = QVBoxLayout()
        header_text.setSpacing(5)
        
        title_label = QLabel("Navigasi Cepat")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
            }
        """)
        
        subtitle_label = QLabel("Akses langsung ke semua fitur sistem")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
            }
        """)
        
        header_text.addWidget(title_label)
        header_text.addWidget(subtitle_label)
        
        header_layout.addWidget(header_icon)
        header_layout.addLayout(header_text)
        header_layout.addStretch()
        
        nav_layout.addLayout(header_layout)
        
        # Quick access buttons grid
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(15)
        
        # Navigation buttons
        nav_buttons = [
            ("📋", "Database Jemaat", "Kelola data jemaat", "#27ae60"),
            ("📅", "Jadwal Kegiatan", "Atur jadwal gereja", "#f39c12"),
            ("💰", "Keuangan", "Manajemen keuangan", "#e74c3c"),
            ("📢", "Pengumuman", "Buat pengumuman", "#3498db"),
            ("📄", "Dokumen", "Kelola dokumen", "#9b59b6"),
            ("🏃", "Aktivitas", "Pantau aktivitas", "#16a085")
        ]
        
        for i, (icon, title, desc, color) in enumerate(nav_buttons):
            row = i // 3
            col = i % 3
            button = self.create_modern_nav_button(icon, title, desc, color)
            buttons_layout.addWidget(button, row, col)
        
        nav_layout.addLayout(buttons_layout)
        parent_layout.addWidget(nav_card)
    
    def create_modern_nav_button(self, icon, title, description, color):
        """Create modern navigation button"""
        button = QPushButton()
        button.setFixedSize(200, 90)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                text-align: left;
                font-family: 'Segoe UI', Arial, sans-serif;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }}
            QPushButton:hover {{
                background-color: {color};
                color: white;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background-color: {color};
                color: white;
                transform: translateY(0px);
            }}
        """)
        
        # Button layout
        button_layout = QHBoxLayout(button)
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(15, 10, 15, 10)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px;")
        icon_label.setFixedWidth(35)
        
        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                background-color: transparent;
            }}
        """)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #5a6c7d;
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                background-color: transparent;
            }
        """)
        desc_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        
        button_layout.addWidget(icon_label)
        button_layout.addLayout(text_layout)
        button_layout.addStretch()
        
        # Connect navigation
        page_map = {
            "Database Jemaat": "jemaat",
            "Jadwal Kegiatan": "jadwal", 
            "Keuangan": "keuangan",
            "Pengumuman": "pengumuman",
            "Dokumen": "dokumen",
            "Aktivitas": "aktivitas"
        }
        
        if title in page_map:
            button.clicked.connect(lambda: self.navigate_to_page(page_map[title]))
        
        return button
    
    def create_professional_data_sections(self, parent_layout):
        """Create professional data sections"""
        # Section header
        section_header = QFrame()
        section_header.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                padding: 20px;
                margin: 15px 0px;
                border: none;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            }
        """)
        
        header_layout = QHBoxLayout(section_header)
        header_layout.setSpacing(20)
        
        header_icon = QLabel("📈")
        header_icon.setStyleSheet("font-size: 32px;")
        
        header_text = QVBoxLayout()
        header_text.setSpacing(5)
        
        main_title = QLabel("Ringkasan Data Gereja")
        main_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
            }
        """)
        
        sub_title = QLabel("Informasi terkini dari semua departemen gereja")
        sub_title.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
            }
        """)
        
        header_text.addWidget(main_title)
        header_text.addWidget(sub_title)
        
        header_layout.addWidget(header_icon)
        header_layout.addLayout(header_text)
        header_layout.addStretch()
        
        parent_layout.addWidget(section_header)
        
        # Main data grid
        data_container = QFrame()
        data_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        data_layout = QGridLayout(data_container)
        data_layout.setSpacing(20)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setRowStretch(0, 1)
        data_layout.setRowStretch(1, 1)
        data_layout.setColumnStretch(0, 1)
        data_layout.setColumnStretch(1, 1)
        
        # Create modern data sections
        self.create_modern_schedule_section(data_layout, 0, 0)
        self.create_modern_announcements_section(data_layout, 0, 1)
        self.create_modern_statistics_section(data_layout, 1, 0)
        self.create_modern_financial_section(data_layout, 1, 1)
        self.create_modern_activity_section(data_layout, 2, 0, colspan=2)
        
        parent_layout.addWidget(data_container)
    
    def create_modern_schedule_section(self, parent_layout, row, col):
        """Create upcoming schedule section"""
        schedule_card = QFrame()
        schedule_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                min-height: 350px;
            }
        """)
        schedule_card.setSizePolicy(schedule_card.sizePolicy().Expanding, schedule_card.sizePolicy().Expanding)
        
        layout = QVBoxLayout(schedule_card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header with gradient background
        header_bg = QFrame()
        header_bg.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        
        header_layout = QHBoxLayout(header_bg)
        header_layout.setSpacing(15)
        
        icon_label = QLabel("📅")
        icon_label.setStyleSheet("font-size: 28px;")
        
        title_label = QLabel("Jadwal Kegiatan Terdekat")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
            }
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header_bg)
        
        # Schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(3)
        self.schedule_table.setHorizontalHeaderLabels(["Tanggal", "Kegiatan", "Waktu"])
        self.schedule_table.setMinimumHeight(180)
        self.schedule_table.setMaximumHeight(220)
        self.schedule_table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                border: none;
                border-radius: 8px;
                gridline-color: #e9ecef;
                selection-background-color: #e3f2fd;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                outline: none;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e9ecef;
            }
            QHeaderView::section {
                background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        # Configure table
        header = self.schedule_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.schedule_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.schedule_table)
        
        # View all button
        view_all_btn = QPushButton("Lihat Semua Jadwal →")
        view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f39c12;
                border: 2px solid #f39c12;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #f39c12;
                color: white;
            }
        """)
        view_all_btn.clicked.connect(lambda: self.navigate_to_page("jadwal"))
        layout.addWidget(view_all_btn, 0, Qt.AlignRight)
        
        parent_layout.addWidget(schedule_card, row, col)
        parent_layout.setRowStretch(row, 1)
        parent_layout.setColumnStretch(col, 1)
    
    def create_modern_announcements_section(self, parent_layout, row, col):
        """Create latest announcements section"""
        announcements_card = QFrame()
        announcements_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                min-height: 350px;
            }
        """)
        announcements_card.setSizePolicy(announcements_card.sizePolicy().Expanding, announcements_card.sizePolicy().Expanding)
        
        layout = QVBoxLayout(announcements_card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header with gradient background
        header_bg = QFrame()
        header_bg.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        
        header_layout = QHBoxLayout(header_bg)
        header_layout.setSpacing(15)
        
        icon_label = QLabel("📢")
        icon_label.setStyleSheet("font-size: 28px;")
        
        title_label = QLabel("Pengumuman Terbaru")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
            }
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header_bg)
        
        # Announcements container with scrolling
        scroll_announcements = QScrollArea()
        scroll_announcements.setWidgetResizable(True)
        scroll_announcements.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_announcements.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_announcements.setMinimumHeight(180)
        scroll_announcements.setMaximumHeight(220)
        scroll_announcements.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #e9ecef;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #6c757d;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #495057;
            }
        """)
        
        self.announcements_container = QWidget()
        self.announcements_layout = QVBoxLayout(self.announcements_container)
        self.announcements_layout.setContentsMargins(10, 10, 10, 10)
        self.announcements_layout.setSpacing(10)
        
        scroll_announcements.setWidget(self.announcements_container)
        
        # Default message
        self.no_announcements_label = QLabel("Belum ada pengumuman terbaru")
        self.no_announcements_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
                text-align: center;
                padding: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        self.no_announcements_label.setAlignment(Qt.AlignCenter)
        self.announcements_layout.addWidget(self.no_announcements_label)
        
        layout.addWidget(scroll_announcements)
        
        # View all button
        view_all_btn = QPushButton("Lihat Semua Pengumuman →")
        view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
        """)
        view_all_btn.clicked.connect(lambda: self.navigate_to_page("pengumuman"))
        layout.addWidget(view_all_btn, 0, Qt.AlignRight)
        
        parent_layout.addWidget(announcements_card, row, col)
        parent_layout.setRowStretch(row, 1)
        parent_layout.setColumnStretch(col, 1)
    
    def create_modern_statistics_section(self, parent_layout, row, col):
        """Create congregation statistics summary section"""
        stats_card = QFrame()
        stats_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                min-height: 350px;
            }
        """)
        stats_card.setSizePolicy(stats_card.sizePolicy().Expanding, stats_card.sizePolicy().Expanding)
        
        layout = QVBoxLayout(stats_card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header with gradient background
        header_bg = QFrame()
        header_bg.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        
        header_layout = QHBoxLayout(header_bg)
        header_layout.setSpacing(15)
        
        icon_label = QLabel("📊")
        icon_label.setStyleSheet("font-size: 28px;")
        
        title_label = QLabel("Statistik Ringkas Jemaat")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
            }
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header_bg)
        
        # Statistics grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        # Define statistics items
        self.stat_items = {
            "total_jemaat": self.create_stat_item("Total Jemaat", "0", "#27ae60"),
            "keluarga": self.create_stat_item("Keluarga", "0", "#3498db"),
            "laki_laki": self.create_stat_item("Laki-laki", "0", "#9b59b6"),
            "perempuan": self.create_stat_item("Perempuan", "0", "#e74c3c")
        }
        
        # Add items to grid
        stats_grid.addWidget(self.stat_items["total_jemaat"], 0, 0)
        stats_grid.addWidget(self.stat_items["keluarga"], 0, 1)
        stats_grid.addWidget(self.stat_items["laki_laki"], 1, 0)
        stats_grid.addWidget(self.stat_items["perempuan"], 1, 1)
        
        layout.addLayout(stats_grid)
        
        # View all button
        view_all_btn = QPushButton("Lihat Database Jemaat →")
        view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #27ae60;
                border: 2px solid #27ae60;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #27ae60;
                color: white;
            }
        """)
        view_all_btn.clicked.connect(lambda: self.navigate_to_page("jemaat"))
        layout.addWidget(view_all_btn, 0, Qt.AlignRight)
        
        parent_layout.addWidget(stats_card, row, col)
        parent_layout.setRowStretch(row, 1)
        parent_layout.setColumnStretch(col, 1)
    
    def create_stat_item(self, title, value, color):
        """Create individual statistic item"""
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                border-left: 3px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(item)
        layout.setSpacing(5)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        value_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        # Store reference to value label for updates
        item.value_label = value_label
        
        return item
    
    def create_modern_financial_section(self, parent_layout, row, col):
        """Create simple financial chart section"""
        finance_card = QFrame()
        finance_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                min-height: 350px;
            }
        """)
        finance_card.setSizePolicy(finance_card.sizePolicy().Expanding, finance_card.sizePolicy().Expanding)
        
        layout = QVBoxLayout(finance_card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header with gradient background
        header_bg = QFrame()
        header_bg.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        
        header_layout = QHBoxLayout(header_bg)
        header_layout.setSpacing(15)
        
        icon_label = QLabel("💰")
        icon_label.setStyleSheet("font-size: 28px;")
        
        title_label = QLabel("Grafik Keuangan")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
            }
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header_bg)
        
        # Financial summary
        finance_summary = QFrame()
        finance_summary.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: none;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        summary_layout = QGridLayout(finance_summary)
        summary_layout.setSpacing(15)
        
        # Define financial items
        self.finance_items = {
            "total_pemasukan": self.create_finance_item("Total Pemasukan", "Rp 0", "#28a745"),
            "total_pengeluaran": self.create_finance_item("Total Pengeluaran", "Rp 0", "#dc3545"),
            "saldo": self.create_finance_item("Saldo", "Rp 0", "#fd7e14"),
            "bulan_ini": self.create_finance_item("Bulan Ini", "Rp 0", "#6f42c1")
        }
        
        # Add items to grid
        summary_layout.addWidget(self.finance_items["total_pemasukan"], 0, 0)
        summary_layout.addWidget(self.finance_items["total_pengeluaran"], 0, 1)
        summary_layout.addWidget(self.finance_items["saldo"], 1, 0)
        summary_layout.addWidget(self.finance_items["bulan_ini"], 1, 1)
        
        layout.addWidget(finance_summary)
        
        # Simple chart placeholder
        chart_placeholder = QLabel("📈 Grafik Trend Keuangan")
        chart_placeholder.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 30px;
                text-align: center;
                color: #6c757d;
                font-size: 16px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        chart_placeholder.setAlignment(Qt.AlignCenter)
        chart_placeholder.setMinimumHeight(100)
        
        layout.addWidget(chart_placeholder)
        
        # View all button
        view_all_btn = QPushButton("Lihat Detail Keuangan →")
        view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e74c3c;
                border: 2px solid #e74c3c;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: white;
            }
        """)
        view_all_btn.clicked.connect(lambda: self.navigate_to_page("keuangan"))
        layout.addWidget(view_all_btn, 0, Qt.AlignRight)
        
        parent_layout.addWidget(finance_card, row, col)
        parent_layout.setRowStretch(row, 1)
        parent_layout.setColumnStretch(col, 1)
    
    def create_finance_item(self, title, value, color):
        """Create individual financial item"""
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(item)
        layout.setSpacing(5)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        value_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 11px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        # Store reference to value label for updates
        item.value_label = value_label
        
        return item
    
    def create_action_button(self, icon, title, description, color):
        """Create individual action button"""
        button = QPushButton()
        button.setFixedHeight(100)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                text-align: left;
                padding: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{
                border-color: {color};
                background-color: #f8f9fa;
            }}
            QPushButton:pressed {{
                background-color: #e9ecef;
            }}
        """)
        
        # Button content
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
            }
        """)
        
        button_layout.addLayout(header_layout)
        button_layout.addWidget(desc_label)
        
        # Set layout to button
        widget = QWidget()
        widget.setLayout(button_layout)
        button_layout_main = QVBoxLayout(button)
        button_layout_main.addWidget(widget)
        
        # Connect to navigation (will be handled by parent)
        page_map = {
            "Database Jemaat": "jemaat",
            "Jadwal Kegiatan": "jadwal", 
            "Keuangan": "keuangan",
            "Pengumuman": "pengumuman",
            "Dokumen": "dokumen",
            "Aktivitas": "aktivitas"
        }
        
        if title in page_map:
            button.clicked.connect(lambda: self.navigate_to_page(page_map[title]))
        
        return button
    
    def create_modern_activity_section(self, parent_layout, row, col, colspan=1):
        """Create recent activity section"""
        activity_card = QFrame()
        activity_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
                padding: 25px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                min-height: 250px;
            }
        """)
        activity_layout = QVBoxLayout(activity_card)
        activity_layout.setSpacing(15)
        
        # Header with gradient background
        header_bg = QFrame()
        header_bg.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #6f42c1 0%, #5a32a3 100%);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        
        header_layout = QHBoxLayout(header_bg)
        header_layout.setSpacing(15)
        
        icon_label = QLabel("📋")
        icon_label.setStyleSheet("font-size: 28px;")
        
        section_title = QLabel("Log Aktivitas Sistem")
        section_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
            }
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(section_title)
        header_layout.addStretch()
        
        activity_layout.addWidget(header_bg)
        
        # Activity container
        activity_container = QFrame()
        activity_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: none;
                border-radius: 8px;
                max-height: 200px;
            }
        """)
        
        activity_container_layout = QVBoxLayout(activity_container)
        activity_container_layout.setContentsMargins(15, 15, 15, 15)
        activity_container_layout.setSpacing(8)
        
        # Activity list
        self.activity_list = QVBoxLayout()
        self.activity_list.setSpacing(8)
        
        # Default message
        self.no_activity_label = QLabel("Belum ada aktivitas sistem hari ini")
        self.no_activity_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
                text-align: center;
                padding: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        self.no_activity_label.setAlignment(Qt.AlignCenter)
        self.activity_list.addWidget(self.no_activity_label)
        
        activity_container_layout.addLayout(self.activity_list)
        activity_layout.addWidget(activity_container)
        
        if colspan > 1:
            parent_layout.addWidget(activity_card, row, col, 1, colspan)
        else:
            parent_layout.addWidget(activity_card, row, col)
    
    def setup_timers(self):
        """Setup periodic update timers"""
        # Update dashboard every 30 seconds
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard_info)
        self.update_timer.start(30000)
        
        # Update time every second
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time_display)
        self.time_timer.start(1000)
    
    def load_dashboard_data(self):
        """Load initial dashboard data"""
        self.update_user_info()
        self.update_connection_status()
        self.load_recent_activity()
        self.update_system_info()
        self.load_schedule_data()
        self.load_announcements_data()
        self.load_statistics_data()
        self.load_financial_data()
    
    def update_user_info(self):
        """Update user information display"""
        if self.user_data:
            user_name = self.user_data.get('nama_lengkap', 'Unknown')
            user_role = self.user_data.get('peran', 'Member')
            
            self.user_greeting.setText(f"Selamat Datang, {user_name}")
            self.user_info_card[1].setText(f"{user_name}\n({user_role})")
            self.user_info_card[1].setStyleSheet("color: #007bff; font-size: 14px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif;")
        else:
            self.user_greeting.setText("Selamat Datang")
            self.user_info_card[1].setText("Not Logged In")
            self.user_info_card[1].setStyleSheet("color: #dc3545; font-size: 14px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif;")
    
    def update_connection_status(self):
        """Update connection status"""
        try:
            if self.api_client:
                result = self.api_client.check_server_connection()
                if result.get("success"):
                    self.is_connected = True
                    # Update main connection indicator
                    self.connection_icon.setText("🟢")
                    self.connection_status.setText("Terhubung ke Server")
                    self.connection_detail.setText("Koneksi stabil dan aman")
                    self.connection_status.setStyleSheet("""
                        QLabel {
                            color: #27ae60;
                            font-size: 16px;
                            font-weight: bold;
                            font-family: 'Segoe UI', Arial, sans-serif;
                            margin: 0px;
                        }
                    """)
                    self.connection_indicator.setStyleSheet("""
                        QFrame {
                            background-color: #edfff3;
                            border: none;
                            border-radius: 10px;
                            padding: 15px;
                            box-shadow: 0 2px 4px rgba(39, 174, 96, 0.1);
                        }
                    """)
                    
                    # Update server status card
                    self.server_status_card[1].setText("Online")
                    self.server_status_card[1].setStyleSheet("color: #17a2b8; font-size: 16px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif;")
                else:
                    self.is_connected = False
                    self._update_disconnected_status()
        except Exception as e:
            self.is_connected = False
            self._update_disconnected_status()
    
    def _update_disconnected_status(self):
        """Update UI for disconnected status"""
        # Update main connection indicator
        self.connection_icon.setText("🔴")
        self.connection_status.setText("Terputus dari Server")
        self.connection_detail.setText("Mencoba menghubungkan kembali...")
        self.connection_status.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
            }
        """)
        self.connection_indicator.setStyleSheet("""
            QFrame {
                background-color: #fff5f5;
                border: none;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 2px 4px rgba(231, 76, 60, 0.1);
            }
        """)
        
        # Update server status card
        self.server_status_card[1].setText("Offline")
        self.server_status_card[1].setStyleSheet("color: #dc3545; font-size: 16px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif;")
    
    def update_system_info(self):
        """Update system information"""
        import platform
        system_info = f"Client v1.0\n{platform.system()}"
        self.system_info_card[1].setText(system_info)
        self.system_info_card[1].setStyleSheet("color: #20c997; font-size: 14px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif;")
    
    def load_recent_activity(self):
        """Load recent activity data"""
        # Clear existing activity
        for i in reversed(range(self.activity_list.count())):
            child = self.activity_list.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        try:
            if self.api_client and self.is_connected:
                # Try to get recent activities from API
                activities = []
                
                # Get recent activities from API
                current_time = datetime.datetime.now()
                activities = []
                
                # Add system activities
                if self.user_data:
                    user_name = self.user_data.get('nama_lengkap', 'User')
                    activities.extend([
                        {
                            "icon": "🟢",
                            "title": f"Sistem terhubung ke server",
                            "time": current_time.strftime("%H:%M"),
                            "color": "#28a745"
                        },
                        {
                            "icon": "👤", 
                            "title": f"Login berhasil - {user_name}",
                            "time": current_time.strftime("%H:%M"),
                            "color": "#007bff"
                        },
                        {
                            "icon": "🔄",
                            "title": "Data dashboard disinkronkan",
                            "time": current_time.strftime("%H:%M"),
                            "color": "#6f42c1"
                        }
                    ])
                else:
                    activities.extend([
                        {
                            "icon": "🔴",
                            "title": "Sistem terputus dari server",
                            "time": current_time.strftime("%H:%M"),
                            "color": "#dc3545"
                        }
                    ])
                
                # Try to get additional activities from API if available
                try:
                    result = self.api_client.get("/api/activities/recent")
                    if result.get("success"):
                        api_activities = result.get("data", [])
                        for activity in api_activities[:2]:  # Add up to 2 API activities
                            activities.append({
                                "icon": activity.get("icon", "📋"),
                                "title": activity.get("title", "Activity"),
                                "time": activity.get("time", current_time.strftime("%H:%M")),
                                "color": activity.get("color", "#6c757d")
                            })
                except:
                    pass  # Continue with existing activities if API call fails
                
                if activities:
                    for activity in activities:
                        self.add_activity_item(activity)
                else:
                    self.no_activity_label = QLabel("Tidak ada log aktivitas")
                    self.no_activity_label.setStyleSheet("""
                        QLabel {
                            color: #6c757d;
                            font-size: 12px;
                            text-align: center;
                            padding: 15px;
                            font-family: 'Segoe UI', Arial, sans-serif;
                        }
                    """)
                    self.no_activity_label.setAlignment(Qt.AlignCenter)
                    self.activity_list.addWidget(self.no_activity_label)
            else:
                # Show offline activities
                current_time = datetime.datetime.now()
                offline_activity = {
                    "icon": "🔴",
                    "title": "Sistem sedang offline - Tidak dapat terhubung ke server",
                    "time": current_time.strftime("%H:%M"),
                    "color": "#dc3545"
                }
                self.add_activity_item(offline_activity)
                
        except Exception as e:
            print(f"Error loading activities: {str(e)}")
    
    def add_activity_item(self, activity):
        """Add an activity item to the list"""
        item_frame = QFrame()
        item_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                padding: 10px;
                margin: 2px;
                border-left: 3px solid #6f42c1;
            }
        """)
        
        item_layout = QHBoxLayout(item_frame)
        item_layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(activity.get("icon", "📝"))
        icon_label.setStyleSheet("font-size: 16px;")
        icon_label.setFixedWidth(25)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(3)
        
        title_label = QLabel(activity.get("title", "Unknown Activity"))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {activity.get("color", "#212529")};
                font-size: 12px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        
        time_label = QLabel(activity.get("time", ""))
        time_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(time_label)
        
        item_layout.addWidget(icon_label)
        item_layout.addLayout(content_layout)
        item_layout.addStretch()
        
        self.activity_list.addWidget(item_frame)
    
    def update_dashboard_info(self):
        """Update dashboard information periodically"""
        self.update_connection_status()
        
        # Periodically refresh data sections if connected
        if self.is_connected:
            # Refresh every 5 minutes to avoid overloading the server
            current_time = datetime.datetime.now()
            if not hasattr(self, '_last_data_refresh') or \
               (current_time - self._last_data_refresh).total_seconds() > 300:
                self.load_schedule_data()
                self.load_announcements_data()
                self.load_statistics_data() 
                self.load_financial_data()
                self._last_data_refresh = current_time
        
        # Update data count if connected
        if self.is_connected:
            try:
                # Refresh all data sections
                self.load_schedule_data()
                self.load_announcements_data() 
                self.load_statistics_data()
                self.load_financial_data()
                
                # Update last sync time
                current_time = datetime.datetime.now()
                sync_time = current_time.strftime("%H:%M")
                self.last_sync_card[1].setText(f"Synced {sync_time}")
                self.last_sync_card[1].setStyleSheet("color: #6f42c1; font-size: 12px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif;")
            except:
                self.last_sync_card[1].setText("Sync Error")
                self.last_sync_card[1].setStyleSheet("color: #dc3545; font-size: 12px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif;")
    
    def update_time_display(self):
        """Update time-based displays"""
        current_time = datetime.datetime.now()
        time_str = current_time.strftime("%H:%M:%S")
        self.last_sync_card[1].setText(f"Last: {time_str}")
        self.last_sync_card[1].setStyleSheet("color: #6f42c1; font-size: 14px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif;")
    
    def navigate_to_page(self, page_key):
        """Signal parent to navigate to specific page"""
        # This method should be connected to parent navigation
        print(f"Navigate to: {page_key}")
        # You can emit a signal here or call parent method
        if hasattr(self.parent(), 'navigate_to'):
            self.parent().navigate_to(page_key)
    
    def set_user_data(self, user_data):
        """Update user data"""
        self.user_data = user_data
        self.update_user_info()
    
    def set_connection_status(self, connected):
        """Update connection status"""
        self.is_connected = connected
        self.update_connection_status()
    
    def refresh_data(self):
        """Refresh all dashboard data"""
        self.load_dashboard_data()
    
    def load_schedule_data(self):
        """Load upcoming schedule data from API"""
        try:
            if self.api_client and self.is_connected:
                # Make API call to get upcoming schedule
                result = self.api_client.get("/api/jadwal/upcoming")
                if result.get("success"):
                    schedule_data = result.get("data", [])
                    self.update_schedule_table(schedule_data)
                else:
                    self.update_schedule_table([])
            else:
                self.update_schedule_table([])
        except Exception as e:
            print(f"Error loading schedule data: {str(e)}")
            self.update_schedule_table([])
    
    def update_schedule_table(self, schedule_data):
        """Update schedule table with data"""
        self.schedule_table.setRowCount(len(schedule_data))
        
        if not schedule_data:
            # Show message when no data
            self.schedule_table.setRowCount(1)
            self.schedule_table.setItem(0, 0, QTableWidgetItem("-"))
            self.schedule_table.setItem(0, 1, QTableWidgetItem("Belum ada jadwal terbaru"))
            self.schedule_table.setItem(0, 2, QTableWidgetItem("-"))
        else:
            for row, schedule in enumerate(schedule_data[:5]):  # Show only 5 recent items
                # Format date
                tanggal = schedule.get('tanggal', '-')
                if tanggal != '-':
                    try:
                        from datetime import datetime
                        date_obj = datetime.strptime(tanggal, '%Y-%m-%d')
                        tanggal = date_obj.strftime('%d/%m')
                    except:
                        pass
                
                self.schedule_table.setItem(row, 0, QTableWidgetItem(tanggal))
                self.schedule_table.setItem(row, 1, QTableWidgetItem(schedule.get('nama_kegiatan', '-')))
                self.schedule_table.setItem(row, 2, QTableWidgetItem(schedule.get('waktu_mulai', '-')))
    
    def load_announcements_data(self):
        """Load latest announcements data from API"""
        try:
            if self.api_client and self.is_connected:
                # Make API call to get latest announcements
                result = self.api_client.get("/api/pengumuman/latest")
                if result.get("success"):
                    announcements_data = result.get("data", [])
                    self.update_announcements_list(announcements_data)
                else:
                    self.update_announcements_list([])
            else:
                self.update_announcements_list([])
        except Exception as e:
            print(f"Error loading announcements data: {str(e)}")
            self.update_announcements_list([])
    
    def update_announcements_list(self, announcements_data):
        """Update announcements list with data"""
        # Clear existing announcements
        for i in reversed(range(self.announcements_layout.count())):
            child = self.announcements_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not announcements_data:
            # Show default message
            self.no_announcements_label = QLabel("Belum ada pengumuman terbaru")
            self.no_announcements_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font-size: 14px;
                    text-align: center;
                    padding: 20px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
            """)
            self.no_announcements_label.setAlignment(Qt.AlignCenter)
            self.announcements_layout.addWidget(self.no_announcements_label)
        else:
            for announcement in announcements_data[:3]:  # Show only 3 recent items
                self.add_announcement_item(announcement)
    
    def add_announcement_item(self, announcement):
        """Add an announcement item to the list"""
        item_frame = QFrame()
        item_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                padding: 12px;
                margin: 2px;
                border-left: 3px solid #3498db;
            }
        """)
        
        item_layout = QVBoxLayout(item_frame)
        item_layout.setSpacing(5)
        
        # Title
        title_label = QLabel(announcement.get("judul", "Pengumuman"))
        title_label.setStyleSheet("""
            QLabel {
                color: #212529;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        title_label.setWordWrap(True)
        
        # Date and content preview
        content = announcement.get("isi", "")[:100]  # Limit to 100 chars
        if len(content) == 100:
            content += "..."
            
        content_label = QLabel(content)
        content_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        content_label.setWordWrap(True)
        
        # Date
        tanggal = announcement.get('tanggal_dibuat', '')
        if tanggal:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(tanggal, '%Y-%m-%d')
                tanggal = date_obj.strftime('%d %b %Y')
            except:
                pass
        
        date_label = QLabel(f"📅 {tanggal}")
        date_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        item_layout.addWidget(title_label)
        item_layout.addWidget(content_label)
        item_layout.addWidget(date_label)
        
        self.announcements_layout.addWidget(item_frame)
    
    def load_statistics_data(self):
        """Load congregation statistics data from API"""
        try:
            if self.api_client and self.is_connected:
                # Make API call to get statistics
                result = self.api_client.get("/api/jemaat/statistics")
                if result.get("success"):
                    stats_data = result.get("data", {})
                    self.update_statistics_display(stats_data)
                else:
                    self.update_statistics_display({})
            else:
                self.update_statistics_display({})
        except Exception as e:
            print(f"Error loading statistics data: {str(e)}")
            self.update_statistics_display({})
    
    def update_statistics_display(self, stats_data):
        """Update statistics display with data"""
        # Update each statistic item
        self.stat_items["total_jemaat"].value_label.setText(str(stats_data.get("total_jemaat", 0)))
        self.stat_items["keluarga"].value_label.setText(str(stats_data.get("total_keluarga", 0)))
        self.stat_items["laki_laki"].value_label.setText(str(stats_data.get("laki_laki", 0)))
        self.stat_items["perempuan"].value_label.setText(str(stats_data.get("perempuan", 0)))
    
    def load_financial_data(self):
        """Load financial data from API"""
        try:
            if self.api_client and self.is_connected:
                # Make API call to get financial summary
                result = self.api_client.get("/api/keuangan/summary")
                if result.get("success"):
                    finance_data = result.get("data", {})
                    self.update_financial_display(finance_data)
                else:
                    self.update_financial_display({})
            else:
                self.update_financial_display({})
        except Exception as e:
            print(f"Error loading financial data: {str(e)}")
            self.update_financial_display({})
    
    def update_financial_display(self, finance_data):
        """Update financial display with data"""
        def format_currency(amount):
            try:
                return f"Rp {int(amount):,}".replace(',', '.')
            except:
                return "Rp 0"
        
        # Update each financial item
        self.finance_items["total_pemasukan"].value_label.setText(
            format_currency(finance_data.get("total_pemasukan", 0))
        )
        self.finance_items["total_pengeluaran"].value_label.setText(
            format_currency(finance_data.get("total_pengeluaran", 0))
        )
        self.finance_items["saldo"].value_label.setText(
            format_currency(finance_data.get("saldo", 0))
        )
        self.finance_items["bulan_ini"].value_label.setText(
            format_currency(finance_data.get("bulan_ini", 0))
        )