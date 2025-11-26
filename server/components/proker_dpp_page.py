# Path: server/components/proker_dpp_page.py
# Program Kerja DPP Standalone Page Component
# Menampilkan Program Kerja DPP tanpa tab

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

# Import widget yang sebenarnya
from .proker_dpp import ProgramKerjaDPPWidget


class ProkerDPPPageComponent(QWidget):
    """
    Program Kerja DPP Standalone Page Component
    Menampilkan konten Program Kerja DPP sebagai halaman standalone tanpa tab
    """

    data_updated = pyqtSignal()
    log_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.widget = None
        self.current_admin = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI dengan widget Program Kerja DPP"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Buat widget Program Kerja DPP
        self.widget = ProgramKerjaDPPWidget(self)

        # Hubungkan signals
        self.widget.data_updated.connect(self.data_updated.emit)
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
            self.widget.load_data()

    def get_data(self):
        """Get program kerja data"""
        if self.widget:
            return self.widget.get_data()
        return []
