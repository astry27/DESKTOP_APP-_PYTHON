# Path: server/components/riwayat.py

import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QLabel, QLineEdit, 
                            QPushButton, QComboBox, QFrame, QMessageBox, QTabWidget,
                            QTextBrowser, QAbstractItemView, QDateEdit, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QDate, QSize
from PyQt5.QtGui import QColor, QIcon, QFont

class RiwayatComponent(QWidget):
    
    log_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.database_manager = None
        self.all_logs = []
        self.admin_activities = []
        self.client_activities = []
        self.setup_ui()
        self.setup_timer()
    
    def set_database_manager(self, database_manager):
        self.database_manager = database_manager
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Clean header without background (matching pengaturan style)
        header_frame = QWidget()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 10, 0)

        title_label = QLabel("Riwayat Aktivitas Sistem")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header_frame)
        
        # Filter controls
        filter_layout = self.create_filter_controls()
        layout.addLayout(filter_layout)
        
        # Tab widget untuk berbagai jenis riwayat
        self.tab_widget = QTabWidget()
        
        # Tab 1: Aktivitas Admin
        self.admin_tab = self.create_admin_activity_tab()
        self.tab_widget.addTab(self.admin_tab, "Aktivitas Admin")
        
        # Tab 2: Client Activities
        self.client_tab = self.create_client_activity_tab()
        self.tab_widget.addTab(self.client_tab, "Aktivitas Client")
        
        layout.addWidget(self.tab_widget)
        
        # Statistics
        stats_layout = self.create_statistics()
        layout.addLayout(stats_layout)
    
    def create_filter_controls(self):
        """Buat kontrol filter"""
        filter_layout = QHBoxLayout()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari aktivitas...")
        self.search_input.textChanged.connect(self.filter_data)
        filter_layout.addWidget(QLabel("Cari:"))
        filter_layout.addWidget(self.search_input)
        
        # Date filter
        filter_layout.addWidget(QLabel("Dari:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addDays(-7))
        filter_layout.addWidget(self.from_date)
        
        filter_layout.addWidget(QLabel("Sampai:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.to_date)
        
        # Filter button
        filter_button = QPushButton("Terapkan Filter")
        filter_button.clicked.connect(self.apply_date_filter)
        filter_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        filter_layout.addWidget(filter_button)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_data)
        # Add refresh icon
        refresh_icon = QIcon("server/assets/refresh.png")
        if not refresh_icon.isNull():
            self.refresh_button.setIcon(refresh_icon)
            self.refresh_button.setIconSize(QSize(20, 20))  # Larger icon size for better visibility
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        filter_layout.addWidget(self.refresh_button)
        
        filter_layout.addStretch()
        return filter_layout
    
    def create_admin_activity_tab(self):
        """Tab untuk aktivitas admin"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Table view untuk daftar admin activities with proper container
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
        
        self.admin_table = self.create_professional_admin_table()
        table_layout.addWidget(self.admin_table)
        
        layout.addWidget(table_container)
        
        return tab
        
    def create_professional_admin_table(self):
        """Create admin table with professional styling."""
        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels([
            "Waktu", "Admin", "Aktivitas", "Detail"
        ])
        
        # Apply professional table styling
        self.apply_professional_table_style(table)
        
        # Set specific column widths for admin table
        column_widths = [120, 100, 150, 200]  # Total: 570px
        for i, width in enumerate(column_widths):
            table.setColumnWidth(i, width)
        
        # Set minimum table width to sum of all columns
        table.setMinimumWidth(sum(column_widths) + 50)  # Add padding for scrollbar
        
        return table
    
    
    def create_client_activity_tab(self):
        """Tab untuk aktivitas client"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Table view untuk daftar client activities with proper container
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
        
        self.client_table = self.create_professional_client_table()
        table_layout.addWidget(self.client_table)
        
        layout.addWidget(table_container)
        
        return tab
        
    def create_professional_client_table(self):
        """Create client table with professional styling."""
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels([
            "Waktu", "Client IP", "Aktivitas", "Terakhir Aktif", "Status"
        ])
        
        # Apply professional table styling
        self.apply_professional_table_style(table)
        
        # Set specific column widths for client table
        column_widths = [120, 120, 150, 120, 100]  # Total: 610px
        for i, width in enumerate(column_widths):
            table.setColumnWidth(i, width)
        
        # Set minimum table width to sum of all columns
        table.setMinimumWidth(sum(column_widths) + 50)  # Add padding for scrollbar
        
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
        table.verticalHeader().setDefaultSectionSize(20)  # Thin rows like Excel
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

    def create_statistics(self):
        """Buat panel statistik"""
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total aktivitas: 0")
        self.admin_count_label = QLabel("Admin: 0")
        self.client_count_label = QLabel("Client: 0")
        self.last_update_label = QLabel("Terakhir diperbarui: -")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.admin_count_label)
        stats_layout.addWidget(self.client_count_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.last_update_label)
        
        return stats_layout
    
    def setup_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.auto_refresh)
        self.update_timer.start(30000)  # Refresh setiap 30 detik
    
    def load_data(self):
        """Load semua data riwayat dari API"""
        if not self.database_manager:
            self.log_message.emit("Database manager tidak tersedia")
            return
        
        try:
            # Load admin activities dari endpoint log
            self.load_admin_activities()
            
            # Load client activities
            self.load_client_activities()
            
            # Update tampilan
            self.update_all_tables()
            self.update_statistics()
            
            self.log_message.emit("Riwayat aktivitas berhasil dimuat dari API")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal memuat riwayat: {str(e)}")
            self.log_message.emit(f"Error memuat riwayat: {str(e)}")
    
    def load_admin_activities(self):
        """Load aktivitas admin dari endpoint log"""
        self.admin_activities = []
        
        if not self.database_manager:
            return
            
        try:
            success, result = self.database_manager.get_log_activities(limit=100)
            
            if success:
                for log in result:
                    if log.get('id_admin'):  # Filter hanya aktivitas admin
                        self.admin_activities.append({
                            'timestamp': log.get('timestamp'),
                            'admin': log.get('user_name', 'Unknown'),
                            'activity': log.get('aktivitas', ''),
                            'detail': log.get('detail', ''),
                            'ip_address': log.get('ip_address', '')
                        })
        except Exception as e:
            self.log_message.emit(f"Error loading admin activities: {str(e)}")
    
    
    def load_client_activities(self):
        """Load aktivitas client dengan status yang akurat"""
        self.client_activities = []
        
        if not self.database_manager:
            return
            
        try:
            success, result = self.database_manager.get_active_sessions()
            
            if success:
                # Handle berbagai format response dari API
                if isinstance(result, dict):
                    if 'data' in result:
                        sessions = result['data']
                    elif 'clients' in result:
                        sessions = result['clients']
                    else:
                        sessions = []
                elif isinstance(result, list):
                    sessions = result
                else:
                    sessions = []
                
                # Process semua sessions termasuk yang disconnect dengan waktu terakhir aktif
                import datetime
                current_time = datetime.datetime.now()
                
                for session in sessions:
                    status = session.get('status', 'Unknown')
                    client_ip = session.get('client_ip', 'Unknown')
                    last_activity = session.get('last_activity') or session.get('connect_time')
                    
                    # Cek apakah client benar-benar aktif berdasarkan waktu aktivitas terakhir
                    is_really_active = False
                    if status.lower() in ['aktif', 'active', 'terhubung', 'connected', 'online']:
                        if last_activity:
                            try:
                                if isinstance(last_activity, str):
                                    if 'T' in last_activity:
                                        last_time = datetime.datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                                    else:
                                        last_time = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
                                else:
                                    last_time = last_activity
                                
                                # Client dianggap aktif jika aktivitas terakhir kurang dari 5 menit yang lalu
                                time_diff = current_time - last_time.replace(tzinfo=None)
                                if time_diff.total_seconds() < 300:  # 5 menit
                                    is_really_active = True
                            except:
                                pass
                    
                    # Tentukan aktivitas dan status berdasarkan kondisi aktual
                    if is_really_active:
                        activity = 'Client aktif terhubung'
                        actual_status = 'Aktif'
                    elif status.lower() in ['disconnect', 'disconnected', 'offline', 'terputus']:
                        activity = 'Client terputus dari API'
                        actual_status = 'Terputus'
                    elif status.lower() in ['aktif', 'active', 'terhubung', 'connected', 'online'] and not is_really_active:
                        activity = 'Client timeout (tidak aktif > 5 menit)'
                        actual_status = 'Timeout'
                    else:
                        activity = 'Status client tidak diketahui'
                        actual_status = status
                    
                    # Format waktu terakhir aktif
                    if last_activity:
                        try:
                            if isinstance(last_activity, str):
                                if 'T' in last_activity:
                                    dt = datetime.datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                                else:
                                    dt = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
                            else:
                                dt = last_activity
                            
                            time_diff = current_time - dt.replace(tzinfo=None)
                            if time_diff.total_seconds() < 60:
                                last_seen = "Sekarang"
                            elif time_diff.total_seconds() < 3600:
                                minutes = int(time_diff.total_seconds() / 60)
                                last_seen = f"{minutes} menit yang lalu"
                            elif time_diff.total_seconds() < 86400:
                                hours = int(time_diff.total_seconds() / 3600)
                                last_seen = f"{hours} jam yang lalu"
                            else:
                                days = int(time_diff.total_seconds() / 86400)
                                last_seen = f"{days} hari yang lalu"
                        except:
                            last_seen = "Tidak diketahui"
                    else:
                        last_seen = "Tidak diketahui"
                    
                    self.client_activities.append({
                        'timestamp': session.get('connect_time'),
                        'client_ip': client_ip,
                        'activity': activity,
                        'status': actual_status,
                        'hostname': session.get('hostname', 'Unknown'),
                        'last_seen': last_seen,
                        'is_active': is_really_active
                    })
                
                # Sort berdasarkan timestamp (terbaru di atas)
                self.client_activities.sort(
                    key=lambda x: x.get('timestamp', ''), 
                    reverse=True
                )
                
        except Exception as e:
            self.log_message.emit(f"Error loading client activities: {str(e)}")
    
    def update_all_tables(self):
        """Update semua tabel dengan data yang dimuat"""
        self.update_admin_table()
        self.update_client_table()
    
    def update_admin_table(self):
        """Update tabel aktivitas admin"""
        self.admin_table.setRowCount(0)
        
        for i, activity in enumerate(self.admin_activities):
            self.admin_table.insertRow(i)
            
            timestamp = activity.get('timestamp')
            if isinstance(timestamp, datetime.datetime):
                time_str = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            elif isinstance(timestamp, str):
                try:
                    dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%d/%m/%Y %H:%M:%S')
                except:
                    time_str = str(timestamp)
            else:
                time_str = str(timestamp)
            
            self.admin_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.admin_table.setItem(i, 1, QTableWidgetItem(activity.get('admin', 'Unknown')))
            self.admin_table.setItem(i, 2, QTableWidgetItem(activity.get('activity', '')))
            self.admin_table.setItem(i, 3, QTableWidgetItem(activity.get('detail', '')))
            
            # Color coding berdasarkan jenis aktivitas
            activity_text = activity.get('activity', '').lower()
            if 'login' in activity_text:
                color = QColor(200, 255, 200)  # Hijau untuk login
            elif 'api' in activity_text:
                color = QColor(200, 200, 255)  # Biru untuk API
            elif 'backup' in activity_text or 'export' in activity_text:
                color = QColor(255, 255, 200)  # Kuning untuk backup/export
            else:
                color = QColor(255, 240, 240)  # Pink muda untuk lainnya
            
            for col in range(4):
                item = self.admin_table.item(i, col)
                if item:
                    item.setBackground(color)
    
    
    def update_client_table(self):
        """Update tabel aktivitas client dengan status yang akurat"""
        self.client_table.setRowCount(0)
        
        for i, activity in enumerate(self.client_activities):
            self.client_table.insertRow(i)
            
            # Format timestamp
            timestamp = activity.get('timestamp')
            if isinstance(timestamp, datetime.datetime):
                time_str = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            elif isinstance(timestamp, str):
                try:
                    # Handle different datetime formats
                    if 'T' in timestamp:
                        dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    time_str = dt.strftime('%d/%m/%Y %H:%M:%S')
                except:
                    time_str = str(timestamp)
            else:
                time_str = str(timestamp)
            
            self.client_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.client_table.setItem(i, 1, QTableWidgetItem(activity.get('client_ip', 'Unknown')))
            self.client_table.setItem(i, 2, QTableWidgetItem(activity.get('activity', '')))
            
            # Waktu terakhir aktif
            last_seen = activity.get('last_seen', 'Tidak diketahui')
            self.client_table.setItem(i, 3, QTableWidgetItem(last_seen))
            
            # Status dengan color coding yang benar
            status = activity.get('status', 'Unknown')
            status_item = QTableWidgetItem(status)
            
            status_lower = status.lower()
            if status_lower in ['aktif', 'active']:
                status_item.setBackground(QColor(144, 238, 144))  # Light green
                status_item.setText('Aktif')
            elif status_lower in ['disconnect', 'disconnected', 'offline', 'terputus']:
                status_item.setBackground(QColor(255, 182, 193))  # Light red  
                status_item.setText('Terputus')
            elif status_lower == 'timeout':
                status_item.setBackground(QColor(255, 165, 0, 100))  # Light orange
                status_item.setText('Timeout')
            else:
                status_item.setBackground(QColor(255, 255, 224))  # Light yellow
                status_item.setText(status)
            
            self.client_table.setItem(i, 4, status_item)
    
    def filter_data(self):
        """Filter data berdasarkan search text"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            self.update_all_tables()
            return
        
        # Filter admin activities
        filtered_admin = []
        for activity in self.admin_activities:
            if (search_text in activity.get('admin', '').lower() or
                search_text in activity.get('activity', '').lower() or
                search_text in activity.get('detail', '').lower()):
                filtered_admin.append(activity)
        
        
        # Filter client activities
        filtered_clients = []
        for client in self.client_activities:
            if (search_text in client.get('client_ip', '').lower() or
                search_text in client.get('activity', '').lower()):
                filtered_clients.append(client)
        
        # Update tables with filtered data
        original_admin = self.admin_activities
        original_clients = self.client_activities
        
        self.admin_activities = filtered_admin
        self.client_activities = filtered_clients
        
        self.update_all_tables()
        
        # Restore original data
        self.admin_activities = original_admin
        self.client_activities = original_clients
    
    def apply_date_filter(self):
        """Terapkan filter tanggal"""
        start_date = self.from_date.date().toPyDate()
        end_date = self.to_date.date().toPyDate()
        
        self.log_message.emit(f"Filter tanggal diterapkan: {start_date} - {end_date}")
        self.load_data()
    
    def update_statistics(self):
        """Update statistik riwayat"""
        total_activities = (len(self.admin_activities) + 
                          len(self.client_activities))
        
        self.total_label.setText(f"Total aktivitas: {total_activities}")
        self.admin_count_label.setText(f"Admin: {len(self.admin_activities)}")
        self.client_count_label.setText(f"Client: {len(self.client_activities)}")
        self.last_update_label.setText(f"Terakhir diperbarui: {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    def auto_refresh(self):
        """Auto refresh data"""
        self.load_data()
    
    def get_data(self):
        """Get semua data untuk komponen lain"""
        return {
            'admin_activities': self.admin_activities,
            'client_activities': self.client_activities
        }