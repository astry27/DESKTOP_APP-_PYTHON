# Path: client/components/activity_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                            QListWidgetItem, QPushButton, QLabel, QFrame,
                            QTextEdit, QTabWidget, QWidget, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import datetime

class ActivityDialog(QDialog):

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.activity_log = []

        self.setWindowTitle("")  # Remove title
        self.setWindowFlags(Qt.WindowType.Popup)  # Popup window that closes when clicked outside
        self.setModal(False)  # Not modal so it can close when focus is lost
        self.setMinimumSize(600, 500)

        self.init_ui()
        self.load_activities()

        # Timer untuk auto refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(30000)  # Refresh setiap 30 detik

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Tab widget untuk jenis aktivitas
        self.tab_widget = QTabWidget()

        # Tab Semua Aktivitas
        all_tab = self.create_all_activities_tab()
        self.tab_widget.addTab(all_tab, "Semua Aktivitas")

        # Tab Notifikasi
        notification_tab = self.create_notifications_tab()
        self.tab_widget.addTab(notification_tab, "Notifikasi")

        layout.addWidget(self.tab_widget)

    def create_all_activities_tab(self):
        """Tab untuk semua aktivitas"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        self.activity_list = QListWidget()
        self.activity_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                font-family: Arial, sans-serif;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border: none;
                background: transparent;
            }
            QListWidget::item:selected {
                background: transparent;
                color: #2c3e50;
            }
        """)
        self.activity_list.setAlternatingRowColors(False)

        layout.addWidget(self.activity_list)

        return tab_widget

    def create_notifications_tab(self):
        """Tab untuk notifikasi khusus"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        # Info notifikasi
        info_label = QLabel("Notifikasi penting dari sistem:")
        info_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-bottom: 10px; border: none; background: transparent;")
        layout.addWidget(info_label)

        self.notification_list = QListWidget()
        self.notification_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                font-family: Arial, sans-serif;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border: none;
                background: transparent;
                color: #2c3e50;
            }
            QListWidget::item:selected {
                background: transparent;
                color: #2c3e50;
            }
        """)

        layout.addWidget(self.notification_list)

        return tab_widget

    def add_activity(self, activity_type, message, is_notification=False):
        """Tambah aktivitas baru"""
        timestamp = datetime.datetime.now()
        activity = {
            'timestamp': timestamp,
            'type': activity_type,
            'message': message,
            'is_notification': is_notification
        }

        # Tambahkan ke awal list (aktivitas terbaru di atas)
        self.activity_log.insert(0, activity)

        # Batasi maksimal 100 aktivitas
        if len(self.activity_log) > 100:
            self.activity_log = self.activity_log[:100]

        self.update_activity_display()

    def update_activity_display(self):
        """Update tampilan aktivitas"""
        # Update list semua aktivitas
        self.activity_list.clear()
        for activity in self.activity_log:
            timestamp_str = activity['timestamp'].strftime("%d/%m/%Y %H:%M:%S")
            activity_text = f"[{timestamp_str}] {activity['type']}: {activity['message']}"

            item = QListWidgetItem(activity_text)

            # Text color only based on type - no backgrounds
            if activity['type'] == 'ERROR':
                item.setForeground(QColor(169, 68, 66))    # Dark red
            elif activity['type'] == 'SUCCESS':
                item.setForeground(QColor(60, 118, 61))    # Dark green
            elif activity['type'] == 'WARNING':
                item.setForeground(QColor(133, 100, 4))    # Dark yellow
            elif activity['type'] == 'INFO':
                item.setForeground(QColor(49, 112, 143))   # Dark blue
            else:
                item.setForeground(QColor(44, 62, 80))     # Default dark gray

            self.activity_list.addItem(item)

        # Update notifikasi
        self.notification_list.clear()
        notifications = [act for act in self.activity_log if act.get('is_notification', False)]

        for notification in notifications:
            timestamp_str = notification['timestamp'].strftime("%d/%m %H:%M")
            notif_text = f"[{timestamp_str}] {notification['message']}"

            item = QListWidgetItem(notif_text)
            self.notification_list.addItem(item)

    def load_activities(self):
        """Load aktivitas (simulasi - akan diganti dengan data real dari API)"""
        # Contoh aktivitas default
        default_activities = [
            {
                'timestamp': datetime.datetime.now() - datetime.timedelta(minutes=5),
                'type': 'INFO',
                'message': 'Client berhasil terhubung ke API',
                'is_notification': True
            },
            {
                'timestamp': datetime.datetime.now() - datetime.timedelta(minutes=10),
                'type': 'SUCCESS',
                'message': 'Login berhasil',
                'is_notification': True
            },
            {
                'timestamp': datetime.datetime.now() - datetime.timedelta(minutes=15),
                'type': 'INFO',
                'message': 'Memuat data pengumuman',
                'is_notification': False
            },
            {
                'timestamp': datetime.datetime.now() - datetime.timedelta(minutes=20),
                'type': 'SUCCESS',
                'message': 'Data jemaat berhasil dimuat',
                'is_notification': False
            },
            {
                'timestamp': datetime.datetime.now() - datetime.timedelta(minutes=25),
                'type': 'INFO',
                'message': 'Heartbeat ke server berhasil',
                'is_notification': False
            }
        ]

        # Hanya tambahkan aktivitas default jika belum ada aktivitas
        if not self.activity_log:
            self.activity_log = default_activities

        self.update_activity_display()

    def auto_refresh(self):
        """Auto refresh aktivitas (placeholder)"""
        # TODO: Implementasi get aktivitas dari API
        # Untuk saat ini, hanya update tampilan
        pass

    def clear_activities(self):
        """Bersihkan semua aktivitas"""
        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            "Apakah Anda yakin ingin membersihkan semua riwayat aktivitas?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.activity_log.clear()
            self.update_activity_display()
            QMessageBox.information(self, "Info", "Riwayat aktivitas berhasil dibersihkan")

    def closeEvent(self, event):
        """Stop timer saat dialog ditutup"""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        event.accept()

    # Methods untuk dipanggil dari main window
    def log_connection_success(self):
        self.add_activity('SUCCESS', 'Berhasil terhubung ke server', True)

    def log_connection_failed(self):
        self.add_activity('ERROR', 'Gagal terhubung ke server', True)

    def log_login_success(self, username):
        self.add_activity('SUCCESS', f'Login berhasil sebagai {username}', True)

    def log_logout(self):
        self.add_activity('INFO', 'User logout dari sistem', True)

    def log_data_refresh(self, component):
        self.add_activity('INFO', f'Data {component} berhasil dimuat ulang', False)

    def log_error(self, error_message):
        self.add_activity('ERROR', error_message, True)

    def log_warning(self, warning_message):
        self.add_activity('WARNING', warning_message, True)