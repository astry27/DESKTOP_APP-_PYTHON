# Path: server/components/struktur_wr_page.py
# Struktur WR Standalone Page Component
# Menampilkan Struktur WR tanpa tab

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

# Import widget yang sebenarnya
from .struktur_wr import StrukturWRComponent


class StrukturWRPageComponent(QWidget):
    """
    Struktur WR Standalone Page Component
    Menampilkan konten Struktur WR sebagai halaman standalone tanpa tab
    """

    log_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.widget = None
        self.current_admin = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI dengan widget Struktur WR"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Buat widget Struktur WR
        self.widget = StrukturWRComponent(self)

        # Hubungkan signals
        self.widget.log_message.connect(self.log_message.emit)

        layout.addWidget(self.widget)

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        if self.widget:
            self.widget.set_database_manager(db_manager)

    def set_current_admin(self, admin_data):
        """Set the current admin data."""
        self.current_admin = admin_data

    def load_data(self):
        """Load data"""
        if self.widget:
            self.widget.load_wr_data()
