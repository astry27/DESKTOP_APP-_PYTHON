# Path: server/components/struktur.py
# Main struktur component that manages all tabs (DPP, WR, K. Kategorial, K. Binaan)

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QFrame
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont

from .struktur_dpp import StrukturDPPComponent
from .struktur_wr import StrukturWRComponent
from .struktur_kategorial import StrukturKategorialComponent
from .struktur_binaan import StrukturBinaanComponent


class StrukturComponent(QWidget):
    """Main struktur component managing all tabs (DPP, WR, K. Kategorial, K. Binaan)"""

    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.current_admin = None

        # Initialize all tab components
        self.dpp_component = StrukturDPPComponent(self)
        self.wr_component = StrukturWRComponent(self)
        self.kategorial_component = StrukturKategorialComponent(self)
        self.binaan_component = StrukturBinaanComponent(self)

        # Connect log messages from all components
        self.dpp_component.log_message.connect(self.on_component_log)
        self.wr_component.log_message.connect(self.on_component_log)
        self.kategorial_component.log_message.connect(self.on_component_log)
        self.binaan_component.log_message.connect(self.on_component_log)

        self.setup_ui()

    def setup_ui(self):
        """Setup UI untuk halaman struktur organisasi dengan tabs"""
        layout = QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Add hanya 2 tabs: DPP (Tab 0) dan K. Binaan (Tab 1)
        # WR dan K. Kategorial akan ditampilkan sebagai standalone pages dari menu mereka masing-masing
        self.tab_widget.addTab(self.dpp_component, "DPP")
        self.tab_widget.addTab(self.binaan_component, "K. Binaan")

        layout.addWidget(self.tab_widget)

    def set_database_manager(self, db_manager):
        """Set database manager for all components"""
        self.db_manager = db_manager

        # Set database manager for all tab components
        self.dpp_component.set_database_manager(db_manager)
        self.wr_component.set_database_manager(db_manager)
        self.kategorial_component.set_database_manager(db_manager)
        self.binaan_component.set_database_manager(db_manager)

        # Load data from all components
        self.dpp_component.load_data()
        self.wr_component.load_wr_data()
        self.kategorial_component.load_kategorial_data()
        self.binaan_component.load_binaan_data()

    def set_current_admin(self, admin_data):
        """Set the current admin data."""
        self.current_admin = admin_data

    def on_component_log(self, message):
        """Forward log messages from components"""
        self.log_message.emit(message)

    def load_data(self):
        """Reload data from all components"""
        self.dpp_component.load_data()
        self.wr_component.load_wr_data()
        self.kategorial_component.load_kategorial_data()
        self.binaan_component.load_binaan_data()
