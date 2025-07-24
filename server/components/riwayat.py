# Path: server/components/riwayat.py

import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QLabel, QLineEdit, 
                            QPushButton, QComboBox, QFrame, QMessageBox, QTabWidget,
                            QTextBrowser, QAbstractItemView, QDateEdit, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QDate
from PyQt5.QtGui import QColor

class RiwayatComponent(QWidget):
    
    log_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.database_manager = None
        self.all_logs = []
        self.admin_activities = []
        self.system_messages = []
        self.client_activities = []
        self.setup_ui()
        self.setup_timer()
    
    def set_database_manager(self, database_manager):
        self.database_manager = database_manager
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #34495e; color: white; padding: 10px;")
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("Riwayat Aktivitas Sistem")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
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
        
        # Tab 2: Pesan Broadcast
        self.message_tab = self.create_message_tab()
        self.tab_widget.addTab(self.message_tab, "Pesan Broadcast")
        
        # Tab 3: Client Activities
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
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
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
        
        self.admin_table = QTableWidget(0, 4)
        self.admin_table.setHorizontalHeaderLabels([
            "Waktu", "Admin", "Aktivitas", "Detail"
        ])
        
        header = self.admin_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        self.admin_table.setAlternatingRowColors(True)
        self.admin_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.admin_table)
        
        return tab
    
    def create_message_tab(self):
        """Tab untuk pesan broadcast"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.message_table = QTableWidget(0, 4)
        self.message_table.setHorizontalHeaderLabels([
            "Waktu", "Pengirim", "Pesan", "Status"
        ])
        
        header = self.message_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.message_table.setAlternatingRowColors(True)
        self.message_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.message_table)
        
        return tab
    
    def create_client_activity_tab(self):
        """Tab untuk aktivitas client"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.client_table = QTableWidget(0, 4)
        self.client_table.setHorizontalHeaderLabels([
            "Waktu", "Client IP", "Aktivitas", "Status"
        ])
        
        header = self.client_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.client_table.setAlternatingRowColors(True)
        self.client_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.client_table)
        
        return tab
    
    def create_statistics(self):
        """Buat panel statistik"""
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total aktivitas: 0")
        self.admin_count_label = QLabel("Admin: 0")
        self.message_count_label = QLabel("Pesan: 0")
        self.client_count_label = QLabel("Client: 0")
        self.last_update_label = QLabel("Terakhir diperbarui: -")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.admin_count_label)
        stats_layout.addWidget(self.message_count_label)
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
            
            # Load broadcast messages
            self.load_broadcast_messages()
            
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
    
    def load_broadcast_messages(self):
        """Load pesan broadcast dari API"""
        self.system_messages = []
        
        if not self.database_manager:
            return
            
        try:
            success, result = self.database_manager.get_recent_messages(limit=50)
            
            if success:
                if isinstance(result, dict) and 'data' in result:
                    messages = result['data']
                elif isinstance(result, list):
                    messages = result
                else:
                    messages = []
                
                for msg in messages:
                    if msg.get('is_broadcast', False):
                        self.system_messages.append({
                            'timestamp': msg.get('waktu_kirim'),
                            'sender': msg.get('pengirim_nama', 'System'),
                            'message': msg.get('pesan', ''),
                            'status': msg.get('status', 'Terkirim')
                        })
        except Exception as e:
            self.log_message.emit(f"Error loading broadcast messages: {str(e)}")
    
    def load_client_activities(self):
        """Load aktivitas client dari API"""
        self.client_activities = []
        
        if not self.database_manager:
            return
            
        try:
            success, result = self.database_manager.get_active_sessions()
            
            if success:
                if isinstance(result, dict) and 'data' in result:
                    sessions = result['data']
                elif isinstance(result, list):
                    sessions = result
                else:
                    sessions = []
                
                for session in sessions:
                    self.client_activities.append({
                        'timestamp': session.get('connect_time'),
                        'client_ip': session.get('client_ip', 'Unknown'),
                        'activity': 'Client terhubung ke API',
                        'status': session.get('status', 'Unknown')
                    })
        except Exception as e:
            self.log_message.emit(f"Error loading client activities: {str(e)}")
    
    def update_all_tables(self):
        """Update semua tabel dengan data yang dimuat"""
        self.update_admin_table()
        self.update_message_table()
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
    
    def update_message_table(self):
        """Update tabel pesan broadcast"""
        self.message_table.setRowCount(0)
        
        for i, message in enumerate(self.system_messages):
            self.message_table.insertRow(i)
            
            timestamp = message.get('timestamp')
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
            
            self.message_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.message_table.setItem(i, 1, QTableWidgetItem(message.get('sender', 'Unknown')))
            
            # Truncate pesan jika terlalu panjang
            msg_text = message.get('message', '')
            if len(msg_text) > 100:
                msg_text = msg_text[:100] + "..."
            self.message_table.setItem(i, 2, QTableWidgetItem(msg_text))
            
            status = message.get('status', 'Unknown')
            status_item = QTableWidgetItem(status)
            if status == 'Terkirim':
                status_item.setBackground(QColor(200, 255, 200))
            else:
                status_item.setBackground(QColor(255, 200, 200))
            
            self.message_table.setItem(i, 3, status_item)
    
    def update_client_table(self):
        """Update tabel aktivitas client"""
        self.client_table.setRowCount(0)
        
        for i, activity in enumerate(self.client_activities):
            self.client_table.insertRow(i)
            
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
            
            self.client_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.client_table.setItem(i, 1, QTableWidgetItem(activity.get('client_ip', 'Unknown')))
            self.client_table.setItem(i, 2, QTableWidgetItem(activity.get('activity', '')))
            
            status = activity.get('status', 'Unknown')
            status_item = QTableWidgetItem(status)
            if status == 'Terhubung':
                status_item.setBackground(QColor(200, 255, 200))
            else:
                status_item.setBackground(QColor(255, 200, 200))
            
            self.client_table.setItem(i, 3, status_item)
    
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
        
        # Filter messages
        filtered_messages = []
        for msg in self.system_messages:
            if (search_text in msg.get('sender', '').lower() or
                search_text in msg.get('message', '').lower()):
                filtered_messages.append(msg)
        
        # Filter client activities
        filtered_clients = []
        for client in self.client_activities:
            if (search_text in client.get('client_ip', '').lower() or
                search_text in client.get('activity', '').lower()):
                filtered_clients.append(client)
        
        # Update tables with filtered data
        original_admin = self.admin_activities
        original_messages = self.system_messages
        original_clients = self.client_activities
        
        self.admin_activities = filtered_admin
        self.system_messages = filtered_messages
        self.client_activities = filtered_clients
        
        self.update_all_tables()
        
        # Restore original data
        self.admin_activities = original_admin
        self.system_messages = original_messages
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
                          len(self.system_messages) + 
                          len(self.client_activities))
        
        self.total_label.setText(f"Total aktivitas: {total_activities}")
        self.admin_count_label.setText(f"Admin: {len(self.admin_activities)}")
        self.message_count_label.setText(f"Pesan: {len(self.system_messages)}")
        self.client_count_label.setText(f"Client: {len(self.client_activities)}")
        self.last_update_label.setText(f"Terakhir diperbarui: {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    def auto_refresh(self):
        """Auto refresh data"""
        self.load_data()
    
    def get_data(self):
        """Get semua data untuk komponen lain"""
        return {
            'admin_activities': self.admin_activities,
            'system_messages': self.system_messages,
            'client_activities': self.client_activities
        }