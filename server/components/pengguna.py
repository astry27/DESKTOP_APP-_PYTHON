from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                             QMessageBox, QDialog, QFormLayout, QComboBox, QCheckBox,
                             QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor, QPainter
import requests
import os
from api_client import BASE_URL

class WordWrapHeaderView(QHeaderView):
    """Custom header view with word wrap and center alignment support"""
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)

    def sectionSizeFromContents(self, logicalIndex):
        """Calculate section size based on wrapped text"""
        if self.model():
            # Get header text
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                # Get current section width
                width = self.sectionSize(logicalIndex)
                if width <= 0:
                    width = self.defaultSectionSize()

                # Create font metrics
                font = self.font()
                font.setBold(True)
                fm = self.fontMetrics()

                # Calculate text rect with word wrap
                rect = fm.boundingRect(0, 0, width - 8, 1000,
                                      Qt.AlignCenter | Qt.TextWordWrap, str(text))

                # Return size with padding
                return QSize(width, max(rect.height() + 12, 25))

        return super().sectionSizeFromContents(logicalIndex)

    def paintSection(self, painter, rect, logicalIndex):
        """Paint section with word wrap and center alignment"""
        painter.save()

        # Draw background with consistent color
        bg_color = QColor(242, 242, 242)  # #f2f2f2
        painter.fillRect(rect, bg_color)

        # Draw borders
        border_color = QColor(212, 212, 212)  # #d4d4d4
        painter.setPen(border_color)
        # Right border
        painter.drawLine(rect.topRight(), rect.bottomRight())
        # Bottom border
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        # Get header text
        if self.model():
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                # Setup font
                font = self.font()
                font.setBold(True)
                painter.setFont(font)

                # Text color
                text_color = QColor(51, 51, 51)  # #333333
                painter.setPen(text_color)

                # Draw text with word wrap and center alignment
                text_rect = rect.adjusted(4, 4, -4, -4)
                painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, str(text))

        painter.restore()

class PenggunaDialog(QDialog):
    def __init__(self, parent=None, pengguna_data=None):
        super().__init__(parent)
        self.pengguna_data = pengguna_data
        self.setWindowTitle("Tambah Pengguna" if not pengguna_data else "Edit Pengguna")
        self.setFixedSize(400, 350)  # Increase height untuk field peran
        self.setup_ui()
        
        if pengguna_data:
            self.load_data()
    
    def setup_ui(self):
        layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.nama_lengkap_input = QLineEdit()
        self.email_input = QLineEdit()

        # Tambah dropdown untuk peran
        self.peran_combo = QComboBox()
        self.peran_combo.addItems(["user", "operator", "admin"])
        self.peran_combo.setCurrentText("user")  # Default role

        self.is_active_checkbox = QCheckBox()
        self.is_active_checkbox.setChecked(True)

        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        layout.addRow("Nama Lengkap:", self.nama_lengkap_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Peran:", self.peran_combo)
        layout.addRow("Aktif:", self.is_active_checkbox)
        
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Simpan")
        self.cancel_button = QPushButton("Batal")
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow(button_layout)
        
        self.save_button.clicked.connect(self.save_pengguna)
        self.cancel_button.clicked.connect(self.reject)  # type: ignore
        
        self.setLayout(layout)
    
    def load_data(self):
        if self.pengguna_data:
            self.username_input.setText(self.pengguna_data.get('username', ''))
            self.nama_lengkap_input.setText(self.pengguna_data.get('nama_lengkap', ''))
            self.email_input.setText(self.pengguna_data.get('email', ''))

            # Load peran
            peran = self.pengguna_data.get('peran', '') or self.pengguna_data.get('role', '') or 'user'
            peran_index = self.peran_combo.findText(peran)
            if peran_index >= 0:
                self.peran_combo.setCurrentIndex(peran_index)
            else:
                self.peran_combo.setCurrentText('user')  # Default fallback

            self.is_active_checkbox.setChecked(bool(self.pengguna_data.get('is_active', True)))
            self.username_input.setEnabled(False)
    
    def save_pengguna(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        nama_lengkap = self.nama_lengkap_input.text().strip()
        email = self.email_input.text().strip()
        peran = self.peran_combo.currentText()
        is_active = self.is_active_checkbox.isChecked()

        if not all([username, nama_lengkap, email]):
            QMessageBox.warning(self, "Error", "Username, nama lengkap, dan email harus diisi!")
            return

        if not self.pengguna_data and not password:
            QMessageBox.warning(self, "Error", "Password harus diisi untuk pengguna baru!")
            return

        # Validasi email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            QMessageBox.warning(self, "Error", "Format email tidak valid!")
            return

        # Validasi password length
        if password and len(password) < 6:
            QMessageBox.warning(self, "Error", "Password minimal 6 karakter!")
            return

        data = {
            'username': username,
            'nama_lengkap': nama_lengkap,
            'email': email,
            'peran': peran,
            'is_active': is_active
        }
        
        if password:
            data['password'] = password
        
        try:
            if self.pengguna_data:
                # Add source_table to data for proper routing
                if 'source_table' in self.pengguna_data:
                    data['source_table'] = self.pengguna_data['source_table']

                # Use 'id' field which works for both admin and pengguna tables
                user_id = self.pengguna_data.get('id') or self.pengguna_data.get('id_pengguna') or self.pengguna_data.get('id_admin')
                url = f"{BASE_URL}/pengguna/{user_id}"
                response = requests.put(url, json=data, timeout=10)
            else:
                url = f"{BASE_URL}/pengguna"
                response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    QMessageBox.information(self, "Sukses", "Pengguna berhasil disimpan!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", result.get('message', 'Gagal menyimpan pengguna'))
            else:
                QMessageBox.warning(self, "Error", f"Error {response.status_code}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan pengguna: {str(e)}")

class PenggunaComponent(QWidget):
    """Component for user management that can be used standalone or embedded"""

    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_pengguna()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        title_label = QLabel("Manajemen Pengguna")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        
        self.add_button = QPushButton("Tambah Pengguna")

        # Add icon from assets folder
        add_icon_path = os.path.join("server", "assets", "tambah.png")
        if os.path.exists(add_icon_path):
            self.add_button.setIcon(QIcon(add_icon_path))
            self.add_button.setIconSize(QSize(16, 16))

        self.add_button.clicked.connect(self.add_pengguna)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                text-align: left;
                padding-left: 24px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)

        self.refresh_button = QPushButton("Refresh")

        # Add icon from assets folder
        refresh_icon_path = os.path.join("server", "assets", "refresh.png")
        if os.path.exists(refresh_icon_path):
            self.refresh_button.setIcon(QIcon(refresh_icon_path))
            self.refresh_button.setIconSize(QSize(16, 16))

        self.refresh_button.clicked.connect(self.load_pengguna)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                text-align: left;
                padding-left: 24px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        header_layout.addWidget(self.refresh_button)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)

        # Set custom header with word wrap and center alignment
        custom_header = WordWrapHeaderView(Qt.Horizontal, self.table)
        self.table.setHorizontalHeader(custom_header)

        self.table.setHorizontalHeaderLabels([
            "Username", "Nama Lengkap", "Email", "Peran", "Status", "Dibuat", "Aksi"
        ])

        # Apply professional table styling matching struktur.py
        self.apply_professional_table_style(self.table)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def update_header_height(self, logicalIndex, oldSize, newSize):
        """Update header height when column is resized"""
        if hasattr(self, 'table'):
            header = self.table.horizontalHeader()
            # Force header to recalculate height
            header.setMinimumHeight(25)
            max_height = 25

            # Calculate required height for each section
            for i in range(header.count()):
                size = header.sectionSizeFromContents(i)
                max_height = max(max_height, size.height())

            # Set header height to accommodate tallest section
            header.setFixedHeight(max_height)

    def apply_professional_table_style(self, table):
        """Apply Excel-like table styling with thin grid lines and minimal borders."""
        # Set column widths
        table.setColumnWidth(0, 120)   # Username
        table.setColumnWidth(1, 200)   # Nama Lengkap - wider for content
        table.setColumnWidth(2, 180)   # Email - wider for email addresses
        table.setColumnWidth(3, 100)   # Peran
        table.setColumnWidth(4, 80)    # Status
        table.setColumnWidth(5, 120)   # Dibuat
        table.setColumnWidth(6, 130)   # Aksi - more space for 3 buttons with better spacing

        # Header styling - Bold headers with center alignment
        header_font = QFont()
        header_font.setBold(True)  # Make headers bold
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

        # Header with bold text, center alignment, and word wrap
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #d4d4d4;
                border-right: 1px solid #d4d4d4;
                padding: 6px 4px;
                font-weight: bold;
                color: #333333;
            }
        """)

        # Configure header behavior
        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        header.setMinimumHeight(25)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(500)
        header.setSectionResizeMode(QHeaderView.Interactive)  # All columns resizable
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Stretch action column to fill remaining space
        header.setStretchLastSection(True)  # Stretch last column to fit and align with border

        # Update header height when column is resized
        header.sectionResized.connect(self.update_header_height)

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

        # Enable scrolling
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Excel-style row settings - 36px for action buttons
        table.verticalHeader().setDefaultSectionSize(36)  # Taller for larger buttons to prevent cutting
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

        # Initial header height calculation (delayed to ensure proper rendering)
        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

    def load_pengguna(self):
        """Load data pengguna dari API"""
        try:
            self.log_message.emit("Memuat data pengguna...")
            response = requests.get(f"{BASE_URL}/pengguna", timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    pengguna_list = result.get('data', [])
                    self.populate_table(pengguna_list)
                    self.log_message.emit(f"Berhasil memuat {len(pengguna_list)} pengguna")
                else:
                    error_msg = result.get('message', 'Gagal mengambil data pengguna')
                    QMessageBox.warning(self, "Error", error_msg)
                    self.log_message.emit(f"Error: {error_msg}")
            else:
                error_msg = f"Error {response.status_code}"
                QMessageBox.warning(self, "Error", error_msg)
                self.log_message.emit(f"Error HTTP: {error_msg}")

        except Exception as e:
            error_msg = f"Gagal mengambil data pengguna: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            self.log_message.emit(f"Exception: {error_msg}")
    
    def populate_table(self, pengguna_list):
        self.table.setRowCount(len(pengguna_list))
        
        for row, pengguna in enumerate(pengguna_list):
            # Username
            self.table.setItem(row, 0, QTableWidgetItem(pengguna.get('username', '')))
            # Nama Lengkap
            self.table.setItem(row, 1, QTableWidgetItem(pengguna.get('nama_lengkap', '')))
            # Email
            self.table.setItem(row, 2, QTableWidgetItem(pengguna.get('email', '')))

            # Peran/Role - ambil dari database
            peran = pengguna.get('peran', '') or pengguna.get('role', '') or 'user'
            peran_display = peran.capitalize()  # Capitalize first letter
            peran_item = QTableWidgetItem(peran_display)
            peran_item.setTextAlignment(Qt.AlignCenter)  # Center align text
            self.table.setItem(row, 3, peran_item)

            # Status
            status = "Aktif" if pengguna.get('is_active') else "Nonaktif"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)  # Center align text
            self.table.setItem(row, 4, status_item)

            # Tanggal dibuat
            created_at = pengguna.get('created_at', '')
            if 'T' in created_at:
                created_at = created_at.split('T')[0]
            self.table.setItem(row, 5, QTableWidgetItem(created_at))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(8, 2, 8, 2)  # Better margins for spacing
            action_layout.setSpacing(5)  # More space between buttons

            # View button (blue)
            view_button = QPushButton()

            # Add view icon from assets folder
            view_icon_path = os.path.join("server", "assets", "lihat.png")
            if os.path.exists(view_icon_path):
                view_button.setIcon(QIcon(view_icon_path))
                view_button.setIconSize(QSize(14, 14))
            else:
                view_button.setText("👁️")

            view_button.clicked.connect(lambda checked, p=pengguna: self.view_pengguna(p))
            view_button.setFixedSize(32, 28)  # Slightly larger for better usability
            view_button.setToolTip("Lihat Detail")
            view_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)

            # Edit button (yellow)
            edit_button = QPushButton()

            # Add edit icon from assets folder
            edit_icon_path = os.path.join("server", "assets", "edit.png")
            if os.path.exists(edit_icon_path):
                edit_button.setIcon(QIcon(edit_icon_path))
                edit_button.setIconSize(QSize(14, 14))
            else:
                edit_button.setText("✏️")

            edit_button.clicked.connect(lambda checked, p=pengguna: self.edit_pengguna(p))
            edit_button.setFixedSize(32, 28)  # Slightly larger for better usability
            edit_button.setToolTip("Edit Data")
            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)

            # Delete button (red)
            delete_button = QPushButton()

            # Add delete icon from assets folder
            delete_icon_path = os.path.join("server", "assets", "hapus.png")
            if os.path.exists(delete_icon_path):
                delete_button.setIcon(QIcon(delete_icon_path))
                delete_button.setIconSize(QSize(14, 14))
            else:
                delete_button.setText("🗑️")

            delete_button.clicked.connect(lambda checked, p=pengguna: self.delete_pengguna(p))
            delete_button.setFixedSize(32, 28)  # Slightly larger for better usability
            delete_button.setToolTip("Hapus Data")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)

            action_layout.addWidget(view_button)
            action_layout.addWidget(edit_button)
            action_layout.addWidget(delete_button)
            action_widget.setLayout(action_layout)

            self.table.setCellWidget(row, 6, action_widget)  # Updated index untuk kolom aksi (was 7, now 6)
    
    def add_pengguna(self):
        """Tambah pengguna baru"""
        dialog = PenggunaDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_pengguna()
            self.log_message.emit("Pengguna baru berhasil ditambahkan")

    def view_pengguna(self, pengguna_data):
        """Lihat detail pengguna (read-only)"""
        dialog = PenggunaDialog(self, pengguna_data)

        # Set encrypted password display (stars)
        dialog.password_input.setText("********")  # Show stars to indicate password exists
        dialog.password_input.setReadOnly(True)

        # Make all fields read-only for view mode
        dialog.username_input.setReadOnly(True)
        dialog.nama_lengkap_input.setReadOnly(True)
        dialog.email_input.setReadOnly(True)
        dialog.peran_combo.setEnabled(False)
        dialog.is_active_checkbox.setEnabled(False)

        # Add gray background to read-only fields
        readonly_style = "background-color: #f0f0f0;"
        dialog.username_input.setStyleSheet(readonly_style)
        dialog.password_input.setStyleSheet(readonly_style)
        dialog.nama_lengkap_input.setStyleSheet(readonly_style)
        dialog.email_input.setStyleSheet(readonly_style)

        # Change window title and button text
        dialog.setWindowTitle("Detail Pengguna")
        dialog.save_button.setText("Tutup")
        dialog.cancel_button.setVisible(False)

        # Override save button to just close the dialog
        dialog.save_button.clicked.disconnect()
        dialog.save_button.clicked.connect(dialog.accept)

        dialog.exec_()
    
    def edit_pengguna(self, pengguna_data):
        """Edit data pengguna"""
        dialog = PenggunaDialog(self, pengguna_data)
        if dialog.exec_() == QDialog.Accepted:
            self.load_pengguna()
            self.log_message.emit(f"Data pengguna {pengguna_data.get('username', '')} berhasil diupdate")
    
    def delete_pengguna(self, pengguna_data):
        reply = QMessageBox.question(
            self, 
            "Konfirmasi Hapus", 
            f"Yakin ingin menghapus pengguna '{pengguna_data['username']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Use 'id' field which works for both admin and pengguna tables
                user_id = pengguna_data.get('id') or pengguna_data.get('id_pengguna') or pengguna_data.get('id_admin')
                url = f"{BASE_URL}/pengguna/{user_id}"
                response = requests.delete(url, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        QMessageBox.information(self, "Sukses", "Pengguna berhasil dihapus!")
                        self.load_pengguna()
                        self.log_message.emit(f"Pengguna {pengguna_data.get('username', '')} berhasil dihapus")
                    else:
                        error_msg = result.get('message', 'Gagal menghapus pengguna')
                        QMessageBox.warning(self, "Error", error_msg)
                        self.log_message.emit(f"Error hapus pengguna: {error_msg}")
                else:
                    error_msg = f"Error {response.status_code}"
                    QMessageBox.warning(self, "Error", error_msg)
                    self.log_message.emit(f"Error HTTP hapus pengguna: {error_msg}")

            except Exception as e:
                error_msg = f"Gagal menghapus pengguna: {str(e)}"
                QMessageBox.critical(self, "Error", error_msg)
                self.log_message.emit(f"Exception hapus pengguna: {error_msg}")