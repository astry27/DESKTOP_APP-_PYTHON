# Path: server/components/buku_kronik.py
# UI Component untuk Buku Kronik (Church Chronicles)

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QScrollArea, QMessageBox, QDialog, QFormLayout, QLineEdit,
                           QDateEdit, QTextEdit, QDialogButtonBox, QGroupBox, QFrame,
                           QFileDialog)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QDateTime, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QIcon
import datetime
from typing import Any, Dict


class PeistiwaDialog(QDialog):
    """Dialog untuk menambah/edit peristiwa kronik"""

    def __init__(self, parent=None, peristiwa_data=None, api_client=None, db_manager=None):
        super().__init__(parent)
        self.peristiwa_data = peristiwa_data
        self.api_client = api_client
        self.db_manager = db_manager
        self.setup_ui()

        if peristiwa_data:
            self.load_data()

    def setup_ui(self):
        self.setWindowTitle("Tambah Peristiwa" if not self.peristiwa_data else "Edit Peristiwa")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)

        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Tanggal
        self.tanggal_input = QDateEdit()
        self.tanggal_input.setDate(QDate.currentDate())
        self.tanggal_input.setCalendarPopup(True)
        self.tanggal_input.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Tanggal:", self.tanggal_input)

        # Peristiwa (required)
        self.peristiwa_input = QLineEdit()
        self.peristiwa_input.setPlaceholderText("Nama/deskripsi peristiwa yang terjadi")
        form_layout.addRow("Peristiwa:", self.peristiwa_input)

        # Keterangan (optional)
        self.keterangan_input = QTextEdit()
        self.keterangan_input.setPlaceholderText("Deskripsi detail peristiwa (opsional)")
        self.keterangan_input.setMinimumHeight(100)
        form_layout.addRow("Keterangan:", self.keterangan_input)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
        layout.addWidget(button_box)

    def load_data(self):
        """Load data for editing"""
        if not self.peristiwa_data:
            return

        # Parse tanggal
        tanggal_str = self.peristiwa_data.get('tanggal', '')
        if tanggal_str:
            try:
                if isinstance(tanggal_str, str):
                    # Format: YYYY-MM-DD
                    date_obj = datetime.datetime.strptime(tanggal_str.split('T')[0], '%Y-%m-%d').date()
                    self.tanggal_input.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except:
                pass

        self.peristiwa_input.setText(self.peristiwa_data.get('peristiwa', ''))
        self.keterangan_input.setText(self.peristiwa_data.get('keterangan', ''))

    def get_data(self) -> Dict[str, Any]:
        """Get form data"""
        return {
            'tanggal': self.tanggal_input.date().toString("yyyy-MM-dd"),
            'peristiwa': self.peristiwa_input.text().strip(),
            'keterangan': self.keterangan_input.toPlainText().strip()
        }


class BukuKronikComponent(QWidget):
    """Komponen utama Buku Kronik untuk menampilkan peristiwa/kejadian gereja"""

    data_updated = pyqtSignal()
    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_client = None
        self.db_manager = None
        self.peristiwa_list = []
        self.selected_peristiwa_id = None
        self.data_loaded = False  # Flag untuk track apakah data sudah pernah di-load
        self.current_admin = None
        self.setup_ui()

    def set_api_client(self, api_client):
        """Set API client"""
        self.api_client = api_client

    def set_database_manager(self, db_manager):
        """Set database manager - ini yang trigger initial load"""
        self.db_manager = db_manager
        if db_manager and not self.data_loaded:
            self.load_data()
            self.data_loaded = True

    def set_current_admin(self, admin_data):
        """Set the current admin data."""
        self.current_admin = admin_data

    def setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ========== HEADER ==========
        header = self.create_header()
        layout.addWidget(header)

        # ========== SEARCH/FILTER SECTION ==========
        filter_group = self.create_filter_section()
        layout.addWidget(filter_group)

        # ========== KRONIK LIST CONTAINER ==========
        # Scrollable area untuk daftar peristiwa
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #d0d0d0;
                background-color: white;
            }
        """)

        # Container untuk daftar peristiwa
        self.kronik_container = QWidget()
        self.kronik_layout = QVBoxLayout(self.kronik_container)
        self.kronik_layout.setContentsMargins(10, 10, 10, 10)
        self.kronik_layout.setSpacing(0)  # No spacing, separator handles visual separation

        scroll_area.setWidget(self.kronik_container)
        layout.addWidget(scroll_area, 1)

        # ========== ACTION BUTTONS ==========
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)

    def create_header(self):
        """Create header with title and add button"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Buku Kronik - Pencatatan Peristiwa Gereja")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        add_button = QPushButton(" Tambah Peristiwa")
        try:
            icon = QIcon("server/assets/tambah.png")
            if not icon.isNull():
                add_button.setIcon(icon)
                add_button.setIconSize(QSize(18, 18))
        except Exception:
            pass
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_button.clicked.connect(self.add_peristiwa)
        header_layout.addWidget(add_button)

        return header

    def create_filter_section(self):
        """Create filter section for search and date range"""
        filter_group = QGroupBox()
        filter_group.setStyleSheet("""
            QGroupBox {
                border: none;
                background-color: transparent;
                padding: 5px;
            }
        """)
        filter_layout = QHBoxLayout(filter_group)
        filter_layout.setContentsMargins(5, 5, 5, 10)

        # Search label and input
        search_label = QLabel("Cari:")
        filter_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari peristiwa atau keterangan...")
        self.search_input.setMaximumWidth(250)
        self.search_input.setMinimumHeight(32)
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input)

        # Spacer
        filter_layout.addSpacing(20)

        # Filter by date range
        date_label = QLabel("Periode:")
        filter_layout.addWidget(date_label)

        # Start date
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setMaximumWidth(120)
        self.start_date.setMinimumHeight(32)
        # Set to 1 year ago by default
        self.start_date.setDate(QDate.currentDate().addYears(-1))
        self.start_date.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.start_date)

        # Separator
        separator_label = QLabel("-")
        filter_layout.addWidget(separator_label)

        # End date
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setMaximumWidth(120)
        self.end_date.setMinimumHeight(32)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.end_date)

        filter_layout.addStretch()

        # Refresh button
        refresh_button = QPushButton(" Refresh")
        try:
            icon = QIcon("server/assets/refresh.png")
            if not icon.isNull():
                refresh_button.setIcon(icon)
                refresh_button.setIconSize(QSize(16, 16))
        except Exception:
            pass
        refresh_button.setMaximumWidth(110)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_button.clicked.connect(self.load_data)
        filter_layout.addWidget(refresh_button)

        return filter_group

    def create_action_buttons(self):
        """Create action buttons layout"""
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 10, 0, 0)

        action_layout.addStretch()

        # Export PDF button
        pdf_button = QPushButton(".PDF")
        try:
            icon = QIcon("server/assets/export.png")
            if not icon.isNull():
                pdf_button.setIcon(icon)
                pdf_button.setIconSize(QSize(16, 16))
        except Exception:
            pass
        pdf_button.setMaximumWidth(140)
        pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        pdf_button.clicked.connect(self.export_to_pdf)
        action_layout.addWidget(pdf_button)

        return action_layout

    def create_peristiwa_card(self, peristiwa):
        """Create a clean row layout for each peristiwa with separator line"""
        # Main container
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Content widget (with white background)
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: none;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 12, 10, 12)
        content_layout.setSpacing(6)

        # Tanggal (bold, simple style)
        tanggal_str = peristiwa.get('tanggal', 'N/A')
        if tanggal_str and tanggal_str != 'N/A':
            try:
                if isinstance(tanggal_str, str) and 'T' in tanggal_str:
                    date_obj = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00')).date()
                else:
                    date_obj = datetime.datetime.strptime(tanggal_str.split('T')[0], '%Y-%m-%d').date()

                tanggal_display = date_obj.strftime('%d %B %Y')  # Format: 11 November 2024
            except:
                tanggal_display = tanggal_str
        else:
            tanggal_display = 'Tanggal tidak ada'

        tanggal_label = QLabel(tanggal_display)
        tanggal_font = QFont()
        tanggal_font.setPointSize(9)
        tanggal_font.setBold(True)
        tanggal_label.setFont(tanggal_font)
        tanggal_label.setStyleSheet("color: #34495e; background-color: transparent;")
        content_layout.addWidget(tanggal_label)

        # Peristiwa (judul dengan warna yang sama seperti tanggal)
        peristiwa_label = QLabel(peristiwa.get('peristiwa', 'Peristiwa tidak ada'))
        peristiwa_font = QFont()
        peristiwa_font.setPointSize(10)
        peristiwa_font.setBold(False)
        peristiwa_label.setFont(peristiwa_font)
        peristiwa_label.setWordWrap(True)
        peristiwa_label.setStyleSheet("color: #34495e; background-color: transparent;")
        content_layout.addWidget(peristiwa_label)

        # Keterangan (jika ada, dengan warna yang sama)
        keterangan = peristiwa.get('keterangan', '')
        if keterangan:
            keterangan_label = QLabel(keterangan)
            keterangan_font = QFont()
            keterangan_font.setPointSize(9)
            keterangan_label.setFont(keterangan_font)
            keterangan_label.setWordWrap(True)
            keterangan_label.setStyleSheet("color: #34495e; background-color: transparent;")
            content_layout.addWidget(keterangan_label)

        # Action buttons layout (in horizontal line)
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 8, 0, 0)
        button_layout.setSpacing(8)

        # Edit button (kuning dengan ikon PNG)
        edit_btn = QPushButton(" Edit")
        try:
            icon = QIcon("server/assets/edit.png")
            if not icon.isNull():
                edit_btn.setIcon(icon)
                edit_btn.setIconSize(QSize(14, 14))
        except Exception:
            pass
        edit_btn.setFixedSize(80, 28)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 4px 10px;
                border: none;
                border-radius: 3px;
                font-size: 9pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_peristiwa(peristiwa))
        button_layout.addWidget(edit_btn)

        # Delete button (merah dengan ikon PNG)
        delete_btn = QPushButton(" Hapus")
        try:
            icon = QIcon("server/assets/hapus.png")
            if not icon.isNull():
                delete_btn.setIcon(icon)
                delete_btn.setIconSize(QSize(14, 14))
        except Exception:
            pass
        delete_btn.setFixedSize(85, 28)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 4px 10px;
                border: none;
                border-radius: 3px;
                font-size: 9pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_peristiwa(peristiwa))
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()

        content_layout.addLayout(button_layout)
        container_layout.addWidget(content_widget)

        # Separator line (garis pemisah)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet("background-color: #e0e0e0; min-height: 1px; max-height: 1px;")
        container_layout.addWidget(separator)

        return container

    def load_data(self):
        """Load data from database manager - called only when needed"""
        try:
            if not self.db_manager:
                self.log_message.emit("Database manager tidak tersedia")
                self.populate_kronik_list([])
                return

            self.log_message.emit("Memuat data buku kronik...")
            success, result = self.db_manager.get_buku_kronik_list()

            if success:
                # Handle different response formats
                if isinstance(result, dict) and 'data' in result:
                    # Response wrapped in dict with 'data' key
                    data_list = result.get('data', [])
                elif isinstance(result, list):
                    # Direct list response
                    data_list = result
                else:
                    # Fallback
                    data_list = []

                self.peristiwa_list = data_list if data_list else []

                self.populate_kronik_list(self.peristiwa_list)
                self.log_message.emit(f"Buku kronik berhasil dimuat: {len(self.peristiwa_list)} peristiwa")
                self.data_updated.emit()
            else:
                self.peristiwa_list = []
                self.populate_kronik_list([])
                error_msg = result if isinstance(result, str) else str(result)
                self.log_message.emit(f"Gagal memuat buku kronik: {error_msg}")
        except Exception as e:
            self.log_message.emit(f"Error loading buku kronik: {str(e)}")
            self.peristiwa_list = []
            self.populate_kronik_list([])

    def populate_kronik_list(self, peristiwa_list):
        """Populate the kronik list with peristiwa cards"""
        # Clear existing cards
        while self.kronik_layout.count():
            child = self.kronik_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not peristiwa_list:
            empty_label = QLabel("Belum ada peristiwa yang dicatat")
            empty_font = QFont()
            empty_font.setItalic(True)
            empty_label.setFont(empty_font)
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #95a5a6; padding: 40px;")
            self.kronik_layout.addWidget(empty_label)
            return

        # Add peristiwa cards
        for peristiwa in peristiwa_list:
            card = self.create_peristiwa_card(peristiwa)
            self.kronik_layout.addWidget(card)

        # Add stretch at the end
        self.kronik_layout.addStretch()

    def apply_filters(self):
        """Apply search text and date range filters"""
        search_text = self.search_input.text().lower()
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()

        # Filter peristiwa based on search text and date range
        filtered = []
        for peristiwa in self.peristiwa_list:
            # Check search text match
            text_match = True
            if search_text:
                text_match = (
                    search_text in peristiwa.get('peristiwa', '').lower() or
                    search_text in peristiwa.get('keterangan', '').lower()
                )

            # Check date range match
            date_match = True
            tanggal_str = peristiwa.get('tanggal', '')
            if tanggal_str:
                try:
                    if isinstance(tanggal_str, str) and 'T' in tanggal_str:
                        date_obj = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00')).date()
                    else:
                        date_obj = datetime.datetime.strptime(tanggal_str.split('T')[0], '%Y-%m-%d').date()

                    # Check if date is within range
                    date_match = start_date <= date_obj <= end_date
                except:
                    # If date parsing fails, exclude from results
                    date_match = False
            else:
                # No date = exclude from filtered results
                date_match = False

            # Add to filtered list if both conditions match
            if text_match and date_match:
                filtered.append(peristiwa)

        self.populate_kronik_list(filtered)

    def add_peristiwa(self):
        """Add new peristiwa"""
        try:
            dialog = PeistiwaDialog(self, db_manager=self.db_manager)
            if dialog.exec_() == dialog.Accepted:
                data: Dict[str, Any] = dialog.get_data()

                # Validate required fields
                if not data['peristiwa'].strip():
                    QMessageBox.warning(self, "Validasi", "Peristiwa tidak boleh kosong")
                    self.log_message.emit("Validasi gagal: Peristiwa kosong")
                    return

                if not data['tanggal']:
                    QMessageBox.warning(self, "Validasi", "Tanggal tidak boleh kosong")
                    self.log_message.emit("Validasi gagal: Tanggal kosong")
                    return

                if not self.db_manager:
                    QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    self.log_message.emit("Error: Database manager tidak tersedia")
                    return

                # Add created_by (admin ID) - default to 1 if not available
                data['created_by'] = 1

                self.log_message.emit("Menambahkan peristiwa...")
                success, result = self.db_manager.add_buku_kronik(data)

                if success:
                    QMessageBox.information(self, "Sukses", "Peristiwa berhasil ditambahkan")
                    self.log_message.emit("Peristiwa berhasil ditambahkan")
                    # Clear search filter sebelum reload
                    self.search_input.clear()
                    # Reload data dengan delay untuk memastikan data tersimpan
                    QTimer.singleShot(300, self.load_data)
                    QTimer.singleShot(500, lambda: self.data_updated.emit())
                else:
                    error_msg = result if isinstance(result, str) else str(result)
                    QMessageBox.critical(self, "Error", f"Gagal tambah peristiwa: {error_msg}")
                    self.log_message.emit(f"Error adding peristiwa: {error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal tambah peristiwa: {str(e)}")
            self.log_message.emit(f"Exception adding peristiwa: {str(e)}")

    def edit_peristiwa(self, peristiwa):
        """Edit existing peristiwa"""
        try:
            dialog = PeistiwaDialog(self, peristiwa, db_manager=self.db_manager)
            if dialog.exec_() == dialog.Accepted:
                data: Dict[str, Any] = dialog.get_data()

                # Validate required fields
                if not data['peristiwa'].strip():
                    QMessageBox.warning(self, "Validasi", "Peristiwa tidak boleh kosong")
                    self.log_message.emit("Validasi gagal: Peristiwa kosong")
                    return

                if not data['tanggal']:
                    QMessageBox.warning(self, "Validasi", "Tanggal tidak boleh kosong")
                    self.log_message.emit("Validasi gagal: Tanggal kosong")
                    return

                if not self.db_manager:
                    QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    self.log_message.emit("Error: Database manager tidak tersedia")
                    return

                peristiwa_id = peristiwa.get("id_kronik")
                self.log_message.emit(f"Mengupdate peristiwa ID {peristiwa_id}...")
                success, result = self.db_manager.update_buku_kronik(peristiwa_id, data)

                if success:
                    QMessageBox.information(self, "Sukses", "Peristiwa berhasil diperbarui")
                    self.log_message.emit("Peristiwa berhasil diperbarui")
                    # Clear search filter sebelum reload
                    self.search_input.clear()
                    # Reload data dengan delay
                    QTimer.singleShot(300, self.load_data)
                    QTimer.singleShot(500, lambda: self.data_updated.emit())
                else:
                    error_msg = result if isinstance(result, str) else str(result)
                    QMessageBox.critical(self, "Error", f"Gagal update peristiwa: {error_msg}")
                    self.log_message.emit(f"Error updating peristiwa: {error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal edit peristiwa: {str(e)}")
            self.log_message.emit(f"Exception editing peristiwa: {str(e)}")

    def delete_peristiwa(self, peristiwa):
        """Delete peristiwa"""
        try:
            peristiwa_name = peristiwa.get('peristiwa', 'Peristiwa')

            reply = QMessageBox.question(self, 'Konfirmasi',
                                        f"Yakin ingin menghapus peristiwa '{peristiwa_name}'?",
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)

            if reply == QMessageBox.Yes:
                if not self.db_manager:
                    QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    self.log_message.emit("Error: Database manager tidak tersedia")
                    return

                peristiwa_id = peristiwa.get("id_kronik")
                self.log_message.emit(f"Menghapus peristiwa ID {peristiwa_id}...")
                success, result = self.db_manager.delete_buku_kronik(peristiwa_id)

                if success:
                    QMessageBox.information(self, "Sukses", "Peristiwa berhasil dihapus")
                    self.log_message.emit(f"Peristiwa berhasil dihapus: {peristiwa_name}")
                    # Clear search filter sebelum reload
                    self.search_input.clear()
                    # Reload data dengan delay
                    QTimer.singleShot(300, self.load_data)
                    QTimer.singleShot(500, lambda: self.data_updated.emit())
                else:
                    error_msg = result if isinstance(result, str) else str(result)
                    QMessageBox.critical(self, "Error", f"Gagal hapus peristiwa: {error_msg}")
                    self.log_message.emit(f"Error deleting peristiwa: {error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal hapus peristiwa: {str(e)}")
            self.log_message.emit(f"Exception deleting peristiwa: {str(e)}")

    def export_to_pdf(self):
        """Export buku kronik to PDF"""
        if not self.peristiwa_list:
            QMessageBox.warning(self, "Warning", "Tidak ada data peristiwa untuk diekspor")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Buku Kronik ke PDF", "buku_kronik.pdf", "PDF Files (*.pdf)"
        )
        if not filename:
            return

        try:
            # Try to use reportlab for PDF generation
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import cm
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib import colors
                from reportlab.lib.enums import TA_CENTER
            except ImportError:
                QMessageBox.critical(
                    self, "Error",
                    "Library ReportLab tidak tersedia.\n\nInstall dengan: pip install reportlab"
                )
                return

            # Create PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            title = Paragraph("BUKU KRONIK - PENCATATAN PERISTIWA GEREJA", title_style)
            story.append(title)
            story.append(Spacer(1, 0.5*cm))

            # Add each peristiwa
            for idx, peristiwa in enumerate(self.peristiwa_list, 1):
                # Date
                tanggal_str = peristiwa.get('tanggal', 'N/A')
                if tanggal_str and tanggal_str != 'N/A':
                    try:
                        if isinstance(tanggal_str, str) and 'T' in tanggal_str:
                            date_obj = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00')).date()
                        else:
                            date_obj = datetime.datetime.strptime(tanggal_str.split('T')[0], '%Y-%m-%d').date()
                        tanggal_display = date_obj.strftime('%d %B %Y')
                    except:
                        tanggal_display = tanggal_str
                else:
                    tanggal_display = 'Tanggal tidak ada'

                # Date style
                date_style = ParagraphStyle(
                    'DateStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.HexColor('#34495e'),
                    fontName='Helvetica-Bold',
                    spaceAfter=6
                )
                date_para = Paragraph(f"<b>{tanggal_display}</b>", date_style)
                story.append(date_para)

                # Peristiwa (event title)
                event_style = ParagraphStyle(
                    'EventStyle',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#34495e'),
                    spaceAfter=6
                )
                event_text = peristiwa.get('peristiwa', 'Peristiwa tidak ada')
                event_para = Paragraph(event_text, event_style)
                story.append(event_para)

                # Keterangan (if exists)
                keterangan = peristiwa.get('keterangan', '')
                if keterangan:
                    keterangan_style = ParagraphStyle(
                        'KeteranganStyle',
                        parent=styles['Normal'],
                        fontSize=9,
                        textColor=colors.HexColor('#34495e'),
                        spaceAfter=12
                    )
                    keterangan_para = Paragraph(keterangan, keterangan_style)
                    story.append(keterangan_para)

                # Add separator line
                if idx < len(self.peristiwa_list):
                    story.append(Spacer(1, 0.3*cm))

            # Build PDF
            doc.build(story)

            QMessageBox.information(self, "Sukses", f"Buku kronik berhasil diekspor ke:\n{filename}")
            self.log_message.emit(f"Buku kronik berhasil diekspor ke: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export PDF: {str(e)}")
            self.log_message.emit(f"Error exporting PDF: {str(e)}")

    def get_data(self):
        """Get peristiwa data"""
        return self.peristiwa_list
