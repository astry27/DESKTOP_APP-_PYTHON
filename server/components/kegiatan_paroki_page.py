# Path: server/components/kegiatan_paroki_page.py
# Kegiatan Paroki Standalone Page Component
# Displays Kegiatan Paroki without tabs

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

# Import the actual Kegiatan Paroki widget
from .kegiatan_paroki import ProgramKerjaKegiatanParokiWidget


class KegiatanParokiPageComponent(QWidget):
    """
    Kegiatan Paroki Standalone Page Component
    Displays the Kegiatan Paroki content as a standalone page without tabs
    """

    data_updated = pyqtSignal()
    log_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.kegiatan_widget = None
        self.current_admin = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI with Kegiatan Paroki widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create the Kegiatan Paroki widget
        self.kegiatan_widget = ProgramKerjaKegiatanParokiWidget(self)

        # Connect signals
        self.kegiatan_widget.data_updated.connect(self.data_updated.emit)
        self.kegiatan_widget.log_message.connect(self.log_message.emit)

        layout.addWidget(self.kegiatan_widget)

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager
        if self.kegiatan_widget:
            self.kegiatan_widget.set_database_manager(db_manager)

    def set_current_admin(self, admin_data):
        """Set the current admin data."""
        self.current_admin = admin_data

    def load_data(self):
        """Load data"""
        if self.kegiatan_widget:
            self.kegiatan_widget.load_data()

    def get_data(self):
        """Get kegiatan data"""
        if self.kegiatan_widget:
            return self.kegiatan_widget.get_data()
        return []
