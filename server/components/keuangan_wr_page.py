# Path: server/components/keuangan_wr_page.py
# Keuangan WR Standalone Page Component
# Menampilkan Keuangan WR tanpa tab

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

# Import widget yang sebenarnya
from .keuangan import KeuanganWRWidget


class KeuanganWRPageComponent(QWidget):
    """
    Keuangan WR Standalone Page Component
    Menampilkan konten Keuangan WR sebagai halaman standalone tanpa tab
    """

    log_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.widget = None
        self.current_admin = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI dengan widget Keuangan WR"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Buat widget Keuangan WR (akan diinisialisasi setelah db_manager tersedia)
        # Placeholder akan di-replace di set_database_manager

        layout.addStretch()

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager

        # Hapus widget placeholder jika ada
        while self.layout().count() > 1:
            item = self.layout().takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        # Buat widget Keuangan WR dengan db_manager
        self.widget = KeuanganWRWidget(db_manager, self)

        # Hubungkan signals
        self.widget.log_message.connect(self.log_message.emit)

        # Insert widget di awal layout sebelum stretch
        self.layout().insertWidget(0, self.widget)

    def set_current_admin(self, admin_data):
        """Set the current admin data."""
        self.current_admin = admin_data

    def load_data(self):
        """Load data"""
        if self.widget:
            self.widget.load_data()
