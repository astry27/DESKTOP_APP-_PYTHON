# Path: server/components/dokumen.py

import os
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QLabel, QPushButton, 
                            QLineEdit, QMessageBox, QFrame, QProgressBar, QFileDialog,
                            QApplication, QAbstractItemView, QDialog, QComboBox, QFormLayout,
                            QDialogButtonBox, QMenu)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont

class UploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upload Dokumen")
        self.setModal(True)
        self.resize(400, 300)
        
        self.file_path = ""
        self.document_name = ""
        self.document_type = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Nama Dokumen
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Masukkan nama dokumen...")
        layout.addRow("Nama Dokumen:", self.name_input)
        
        # Jenis Dokumen
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Administrasi", "Keanggotaan", "Keuangan", 
            "Liturgi", "Legalitas"
        ])
        layout.addRow("Jenis Dokumen:", self.type_combo)
        
        # File Path
        file_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("Pilih file...")
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(self.browse_button)
        
        file_widget = QWidget()
        file_widget.setLayout(file_layout)
        layout.addRow("File:", file_widget)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Dokumen untuk Upload", "", 
            "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx);;Excel Files (*.xlsx);;PowerPoint (*.ppt *.pptx);;Images (*.png *.jpg *.jpeg);;Text Files (*.txt)"
        )
        
        if file_path:
            self.file_input.setText(file_path)
            self.file_path = file_path
            
            # Auto-fill name if empty
            if not self.name_input.text():
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                self.name_input.setText(file_name)
    
    def accept_dialog(self):
        self.document_name = self.name_input.text().strip()
        self.document_type = self.type_combo.currentText()
        
        if not self.document_name:
            QMessageBox.warning(self, "Error", "Nama dokumen harus diisi!")
            return
        
        if not self.file_path:
            QMessageBox.warning(self, "Error", "File harus dipilih!")
            return
        
        self.accept()

class DokumenComponent(QWidget):
    
    log_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.database_manager = None
        self.all_documents = []
        self.filtered_documents = []
        self.current_doc_type_filter = "Semua"
        self.current_file_type_filter = "Semua"
        self.setup_ui()
        self.setup_timer()
    
    def set_database_manager(self, database_manager):
        self.database_manager = database_manager
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Clean header without background (matching pengaturan style)
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 10, 0)

        title_label = QLabel("Manajemen Dokumen Sistem")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header)
        
        toolbar_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari dokumen...")
        self.search_input.textChanged.connect(self.filter_data)
        toolbar_layout.addWidget(QLabel("Cari:"))
        toolbar_layout.addWidget(self.search_input)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_data)
        # Add refresh icon
        refresh_icon = QIcon("server/assets/refresh.png")
        if not refresh_icon.isNull():
            self.refresh_button.setIcon(refresh_icon)
            self.refresh_button.setIconSize(QSize(20, 20))  # Larger icon size for better visibility
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        toolbar_layout.addWidget(self.refresh_button)
        
        self.upload_button = QPushButton("Upload Dokumen")
        self.upload_button.clicked.connect(self.upload_document)
        # Add upload icon
        upload_icon = QIcon("server/assets/upload.png")
        if not upload_icon.isNull():
            self.upload_button.setIcon(upload_icon)
            self.upload_button.setIconSize(QSize(20, 20))  # Larger icon size for better visibility
        self.upload_button.setStyleSheet("""
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
        toolbar_layout.addWidget(self.upload_button)
        
        self.filter_button = QPushButton("Filter")
        self.filter_button.clicked.connect(self.show_filter_menu)
        self.filter_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        toolbar_layout.addWidget(self.filter_button)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Table view untuk daftar dokumen with proper container
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
        
        self.table_widget = self.create_professional_table()
        table_layout.addWidget(self.table_widget)
        
        layout.addWidget(table_container)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total dokumen: 0")
        self.size_label = QLabel("Total ukuran: 0 KB")
        self.last_update_label = QLabel("Terakhir diperbarui: -")
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.size_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.last_update_label)
        layout.addLayout(stats_layout)
    
    def create_professional_table(self):
        """Create table with professional styling."""
        table = QTableWidget(0, 7)
        table.setHorizontalHeaderLabels([
            "Nama Dokumen", "Jenis Dokumen", "Ukuran", "Tipe File", "Upload By", "Tanggal Upload", "Aksi"
        ])
        
        # Apply professional table styling
        self.apply_professional_table_style(table)
        
        # Set specific column widths
        column_widths = [200, 120, 80, 80, 120, 120, 100]  # Total: 820px
        for i, width in enumerate(column_widths):
            table.setColumnWidth(i, width)
        
        # Set minimum table width to sum of all columns
        table.setMinimumWidth(sum(column_widths) + 50)  # Add padding for scrollbar
        
        # Enable context menu
        table.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        table.customContextMenuRequested.connect(self.show_context_menu)
        
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

    def show_filter_menu(self):
        """Tampilkan menu filter"""
        menu = QMenu(self)
        
        # Filter Jenis Dokumen
        doc_type_menu = menu.addMenu("Jenis Dokumen")
        doc_types = ["Semua", "Administrasi", "Keanggotaan", "Keuangan", "Liturgi", "Legalitas"]
        for doc_type in doc_types:
            action = doc_type_menu.addAction(doc_type)
            action.triggered.connect(lambda checked, dt=doc_type: self.set_doc_type_filter(dt))
            if doc_type == self.current_doc_type_filter:
                action.setChecked(True)
        
        # Filter Jenis File
        file_type_menu = menu.addMenu("Jenis File")
        file_types = ["Semua", ".DOCX", ".PDF", ".TXT", ".XLS", ".PPT", ".JPG", ".JPEG", ".PNG", "Lainnya"]
        for file_type in file_types:
            action = file_type_menu.addAction(file_type)
            action.triggered.connect(lambda checked, ft=file_type: self.set_file_type_filter(ft))
            if file_type == self.current_file_type_filter:
                action.setChecked(True)
        
        # Reset Filter
        menu.addSeparator()
        reset_action = menu.addAction("Reset Filter")
        reset_action.triggered.connect(self.reset_filters)
        
        menu.exec_(self.filter_button.mapToGlobal(self.filter_button.rect().bottomLeft()))
    
    def set_doc_type_filter(self, doc_type):
        """Set filter jenis dokumen"""
        self.current_doc_type_filter = doc_type
        self.apply_filters()
        self.log_message.emit(f"Filter jenis dokumen: {doc_type}")
    
    def set_file_type_filter(self, file_type):
        """Set filter jenis file"""
        self.current_file_type_filter = file_type
        self.apply_filters()
        self.log_message.emit(f"Filter jenis file: {file_type}")
    
    def reset_filters(self):
        """Reset semua filter"""
        self.current_doc_type_filter = "Semua"
        self.current_file_type_filter = "Semua"
        self.apply_filters()
        self.log_message.emit("Filter direset")
    
    def apply_filters(self):
        """Terapkan filter ke dokumen"""
        filtered_docs = self.all_documents.copy()
        
        # Filter berdasarkan jenis dokumen
        if self.current_doc_type_filter != "Semua":
            filtered_docs = [doc for doc in filtered_docs 
                           if (doc.get('jenis_dokumen', '') == self.current_doc_type_filter or
                               doc.get('document_type', '') == self.current_doc_type_filter or
                               doc.get('category', '') == self.current_doc_type_filter)]
        
        # Filter berdasarkan jenis file
        if self.current_file_type_filter != "Semua":
            if self.current_file_type_filter == "Lainnya":
                common_types = ['.DOCX', '.PDF', '.TXT', '.XLS', '.PPT', '.JPG', '.JPEG', '.PNG']
                filtered_docs = [doc for doc in filtered_docs 
                               if not any(doc.get('nama_dokumen', '').upper().endswith(ext) for ext in common_types)]
            else:
                filtered_docs = [doc for doc in filtered_docs 
                               if doc.get('nama_dokumen', '').upper().endswith(self.current_file_type_filter)]
        
        self.filtered_documents = filtered_docs
        self.update_table_display(self.filtered_documents)
        self.update_statistics()

    def show_context_menu(self, position):
        """Tampilkan context menu untuk aksi dokumen"""
        if self.table_widget.rowCount() == 0:
            return
            
        menu = QMenu()
        
        view_action = menu.addAction("Lihat Info")
        download_action = menu.addAction("Download")
        delete_action = menu.addAction("Hapus")
        
        action = menu.exec_(self.table_widget.mapToGlobal(position))
        
        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            if action == view_action:
                self.view_document(current_row)
            elif action == download_action:
                self.download_document(current_row)
            elif action == delete_action:
                self.delete_document(current_row)
    
    def setup_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.auto_refresh)
        self.update_timer.start(60000)
    
    def load_data(self):
        if not self.database_manager:
            self.all_documents = []
            self.update_table_display(self.all_documents)
            self.update_statistics()
            self.log_message.emit("Database manager tidak tersedia")
            return
        
        try:
            success, result = self.database_manager.get_files_list()
            
            if success:
                # Check if result is list or dict
                if isinstance(result, list):
                    self.all_documents = result
                elif isinstance(result, dict) and result.get("status") == "success":
                    self.all_documents = result.get("data", [])
                else:
                    self.all_documents = []
                
                # Debug logging - print first document structure
                if self.all_documents and len(self.all_documents) > 0:
                    first_doc = self.all_documents[0]
                    self.log_message.emit(f"DEBUG: Sample document keys: {list(first_doc.keys())}")
                    # Log document type fields specifically
                    doc_type_fields = [k for k in first_doc.keys() if 'dokumen' in k.lower() or 'document' in k.lower() or 'type' in k.lower() or 'category' in k.lower()]
                    if doc_type_fields:
                        self.log_message.emit(f"DEBUG: Document type related fields: {doc_type_fields}")
                        for field in doc_type_fields:
                            self.log_message.emit(f"DEBUG: {field} = '{first_doc.get(field, 'NOT_SET')}'")
                    else:
                        self.log_message.emit("DEBUG: No document type fields found")
                
                # Sort documents berdasarkan tanggal upload (file lama dulu, baru kemudian)
                # Ini memastikan nomor urut sesuai dengan urutan upload
                try:
                    self.all_documents.sort(key=lambda x: x.get('upload_date', '') or x.get('tanggal_upload', '') or '')
                except:
                    pass  # Jika sorting gagal, tetap pakai urutan original
                
                self.filtered_documents = self.all_documents.copy()
                self.update_table_display(self.filtered_documents)
                self.update_statistics()
                self.log_message.emit(f"Daftar dokumen berhasil dimuat: {len(self.all_documents)} file")
            else:
                self.all_documents = []
                self.update_table_display(self.all_documents)
                self.update_statistics()
                error_msg = str(result) if result else "Unknown error"
                self.log_message.emit(f"Gagal memuat dokumen: {error_msg}")
                
        except Exception as e:
            self.all_documents = []
            self.update_table_display(self.all_documents)
            self.update_statistics()
            self.log_message.emit(f"Error memuat dokumen: {str(e)}")
    
    def update_table_display(self, documents):
        if not documents:
            documents = []
            
        self.table_widget.setRowCount(len(documents))
        
        for i, doc in enumerate(documents):
            # Nama dokumen
            nama_dokumen = doc.get('nama_dokumen', '') or doc.get('file_name', '') or doc.get('filename', '') or ''
            self.table_widget.setItem(i, 0, QTableWidgetItem(str(nama_dokumen)))
            
            # Jenis dokumen - diambil dari input saat upload dengan fallback yang lebih lengkap
            jenis_dokumen = (doc.get('jenis_dokumen', '') or 
                           doc.get('document_type', '') or 
                           doc.get('category', '') or 
                           doc.get('type', '') or 
                           doc.get('doc_type', '') or
                           doc.get('file_category', '') or
                           doc.get('document_category', '') or '')
            
            # Debug logging untuk jenis dokumen
            if i == 0 and not jenis_dokumen:  # Hanya log jika document type kosong
                self.log_message.emit(f"WARNING: Document type empty for first document")
                available_keys = [k for k in doc.keys() if 'jenis' in k.lower() or 'dokumen' in k.lower() or 'document' in k.lower() or 'type' in k.lower() or 'category' in k.lower()]
                if available_keys:
                    self.log_message.emit(f"Available type-related keys: {available_keys}")
                    for key in available_keys:
                        value = doc.get(key, '')
                        self.log_message.emit(f"  {key}: '{value}'")
            
            self.table_widget.setItem(i, 1, QTableWidgetItem(str(jenis_dokumen)))
            
            # Ukuran file
            size_bytes = doc.get('ukuran_file', 0) or doc.get('file_size', 0) or doc.get('size', 0) or 0
            try:
                size_bytes = int(size_bytes)
                if size_bytes > 1048576:
                    size_str = f"{size_bytes / 1048576:.2f} MB"
                elif size_bytes > 1024:
                    size_str = f"{size_bytes / 1024:.2f} KB"
                else:
                    size_str = f"{size_bytes} B"
            except (ValueError, TypeError):
                size_str = "0 B"
            self.table_widget.setItem(i, 2, QTableWidgetItem(size_str))
            
            # Tipe file - diambil dari ekstensi file
            file_type = doc.get('tipe_file', '') or doc.get('mime_type', '') or doc.get('content_type', '') or ''
            file_name = doc.get('nama_dokumen', '') or doc.get('file_name', '') or doc.get('filename', '') or ''
            
            # Jika file_type kosong, coba ambil dari ekstensi file
            if not file_type and file_name:
                file_extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
                if file_extension == 'pdf':
                    type_display = "PDF"
                elif file_extension in ['docx', 'doc']:
                    type_display = "Word"
                elif file_extension in ['xlsx', 'xls']:
                    type_display = "Excel"
                elif file_extension in ['pptx', 'ppt']:
                    type_display = "PowerPoint"
                elif file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                    type_display = "Image"
                elif file_extension == 'txt':
                    type_display = "Text"
                else:
                    type_display = file_extension.upper() if file_extension else "Unknown"
            else:
                # Parse dari mime type
                if 'pdf' in file_type.lower():
                    type_display = "PDF"
                elif 'word' in file_type.lower() or 'document' in file_type.lower():
                    type_display = "Word"
                elif 'excel' in file_type.lower() or 'sheet' in file_type.lower():
                    type_display = "Excel"
                elif 'powerpoint' in file_type.lower() or 'presentation' in file_type.lower():
                    type_display = "PowerPoint"
                elif 'image' in file_type.lower():
                    type_display = "Image"
                elif 'text' in file_type.lower():
                    type_display = "Text"
                else:
                    type_display = file_type.split('/')[-1].upper() if '/' in file_type else file_type or "Unknown"
            
            self.table_widget.setItem(i, 3, QTableWidgetItem(type_display))
            
            # Upload by
            upload_by = (doc.get('uploaded_by_name', '') or 
                        doc.get('uploaded_by', '') or 
                        doc.get('uploader', '') or 'Unknown')
            self.table_widget.setItem(i, 4, QTableWidgetItem(str(upload_by)))
            
            # Tanggal upload
            upload_date = (doc.get('upload_date', '') or 
                          doc.get('tanggal_upload', '') or 
                          doc.get('created_at', '') or 
                          doc.get('date_uploaded', '') or '')
            if upload_date:
                if isinstance(upload_date, str):
                    try:
                        parsed_date = datetime.datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                        date_str = parsed_date.strftime('%d/%m/%Y %H:%M')
                    except:
                        date_str = str(upload_date)
                else:
                    date_str = str(upload_date)
            else:
                date_str = "-"
            self.table_widget.setItem(i, 5, QTableWidgetItem(date_str))
            
            # Aksi buttons with icons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(1, 1, 1, 1)
            action_layout.setSpacing(2)
            
            # View button with lihat.png icon
            view_button = QPushButton()
            view_icon = QIcon("server/assets/lihat.png")
            view_button.setIcon(view_icon)
            view_button.setIconSize(QSize(18, 18))  # Larger icon size for better visibility
            view_button.setStyleSheet("""
                QPushButton { 
                    background-color: #f1c40f; 
                    color: white; 
                    padding: 2px; 
                    border: none; 
                    border-radius: 2px;
                    min-width: 24px;
                    max-width: 24px;
                    min-height: 24px;
                    max-height: 24px;
                }
                QPushButton:hover { 
                    background-color: #f39c12; 
                }
                QPushButton:pressed {
                    background-color: #d68910;
                }
            """)
            view_button.setToolTip("Lihat Info Dokumen")
            view_button.clicked.connect(lambda _, row=i: self.view_document(row))
            action_layout.addWidget(view_button)
            
            # Download button with unduh.png icon
            download_button = QPushButton()
            download_icon = QIcon("server/assets/unduh.png")
            download_button.setIcon(download_icon)
            download_button.setIconSize(QSize(18, 18))  # Larger icon size for better visibility
            download_button.setStyleSheet("""
                QPushButton { 
                    background-color: #27ae60; 
                    color: white; 
                    padding: 2px; 
                    border: none; 
                    border-radius: 2px;
                    min-width: 24px;
                    max-width: 24px;
                    min-height: 24px;
                    max-height: 24px;
                }
                QPushButton:hover { 
                    background-color: #2ecc71; 
                }
                QPushButton:pressed {
                    background-color: #229954;
                }
            """)
            download_button.setToolTip("Download Dokumen")
            download_button.clicked.connect(lambda _, row=i: self.download_document(row))
            action_layout.addWidget(download_button)
            
            # Delete button with hapus.png icon
            delete_button = QPushButton()
            delete_icon = QIcon("server/assets/hapus.png")
            delete_button.setIcon(delete_icon)
            delete_button.setIconSize(QSize(18, 18))  # Larger icon size for better visibility
            delete_button.setStyleSheet("""
                QPushButton { 
                    background-color: #e74c3c; 
                    color: white; 
                    padding: 2px; 
                    border: none; 
                    border-radius: 2px;
                    min-width: 24px;
                    max-width: 24px;
                    min-height: 24px;
                    max-height: 24px;
                }
                QPushButton:hover { 
                    background-color: #c0392b; 
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            delete_button.setToolTip("Hapus Dokumen")
            delete_button.clicked.connect(lambda _, row=i: self.delete_document(row))
            action_layout.addWidget(delete_button)
            
            self.table_widget.setCellWidget(i, 6, action_widget)
    
    def filter_data(self):
        search_text = self.search_input.text().lower()
        
        if not search_text:
            self.apply_filters()
        else:
            filtered_docs = []
            source_docs = self.filtered_documents if hasattr(self, 'filtered_documents') else self.all_documents
            
            for doc in source_docs:
                nama_dokumen = doc.get('nama_dokumen', '') or doc.get('file_name', '') or doc.get('filename', '') or ''
                uploaded_by = (doc.get('uploaded_by_name', '') or 
                             doc.get('uploaded_by', '') or 
                             doc.get('uploader', '') or '')
                tipe_file = doc.get('tipe_file', '') or doc.get('mime_type', '') or doc.get('content_type', '') or ''
                jenis_dokumen = (doc.get('jenis_dokumen', '') or 
                               doc.get('document_type', '') or 
                               doc.get('category', '') or '')
                
                if (search_text in nama_dokumen.lower() or 
                    search_text in uploaded_by.lower() or
                    search_text in tipe_file.lower() or
                    search_text in jenis_dokumen.lower()):
                    filtered_docs.append(doc)
            
            self.update_table_display(filtered_docs)
            self.total_label.setText(f"Total dokumen: {len(filtered_docs)}")
    
    def update_statistics(self):
        total_docs = len(self.all_documents)
        total_size = 0
        
        for doc in self.all_documents:
            size = doc.get('ukuran_file', 0) or doc.get('file_size', 0) or doc.get('size', 0) or 0
            try:
                total_size += int(size)
            except (ValueError, TypeError):
                continue
        
        if total_size > 1048576:
            size_str = f"{total_size / 1048576:.2f} MB"
        elif total_size > 1024:
            size_str = f"{total_size / 1024:.2f} KB"
        else:
            size_str = f"{total_size} B"
        
        self.total_label.setText(f"Total dokumen: {total_docs}")
        self.size_label.setText(f"Total ukuran: {size_str}")
        self.last_update_label.setText(f"Terakhir diperbarui: {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    def view_document(self, row):
        current_docs = self.filtered_documents if hasattr(self, 'filtered_documents') else self.all_documents
        if row < len(current_docs):
            doc = current_docs[row]
            doc_name = doc.get('nama_dokumen', 'Unknown') or doc.get('file_name', 'Unknown') or 'Unknown'
            jenis_dokumen = doc.get('jenis_dokumen', 'Unknown') or doc.get('document_type', 'Unknown') or 'Unknown'
            size = doc.get('ukuran_file', 0) or doc.get('file_size', 0) or 0
            file_type = doc.get('tipe_file', 'Unknown') or doc.get('mime_type', 'Unknown') or 'Unknown'
            uploaded_by = doc.get('uploaded_by_name', 'Unknown') or doc.get('uploaded_by', 'Unknown') or 'Unknown'
            upload_date = doc.get('upload_date', 'Unknown') or doc.get('tanggal_upload', 'Unknown') or 'Unknown'
            
            QMessageBox.information(
                self, "Info Dokumen", 
                f"Nama: {doc_name}\n"
                f"Jenis Dokumen: {jenis_dokumen}\n"
                f"Ukuran: {size} bytes\n"
                f"Tipe: {file_type}\n"
                f"Upload by: {uploaded_by}\n"
                f"Tanggal: {upload_date}"
            )
            self.log_message.emit(f"Melihat info dokumen: {doc_name}")
    
    def download_document(self, row):
        current_docs = self.filtered_documents if hasattr(self, 'filtered_documents') else self.all_documents
        if row < len(current_docs):
            doc = current_docs[row]
            doc_name = doc.get('nama_dokumen', 'Unknown') or doc.get('file_name', 'Unknown') or 'document'
            doc_id = doc.get('id_dokumen') or doc.get('file_id') or doc.get('id')
            
            if not doc_id:
                QMessageBox.warning(self, "Error", "ID dokumen tidak ditemukan")
                return
            
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Simpan Dokumen", doc_name, 
                "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx);;Excel Files (*.xlsx)"
            )
            
            if save_path:
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                
                try:
                    if self.database_manager:
                        self.progress_bar.setValue(25)
                        QApplication.processEvents()
                        
                        success, result = self.database_manager.download_file_from_api(doc_id)
                        
                        self.progress_bar.setValue(75)
                        QApplication.processEvents()
                        
                        if success:
                            file_content = result.get('content')
                            if file_content and isinstance(file_content, bytes):
                                try:
                                    with open(save_path, 'wb') as f:
                                        f.write(file_content)
                                    
                                    self.progress_bar.setValue(100)
                                    QApplication.processEvents()
                                    
                                    QMessageBox.information(self, "Download", 
                                        f"File berhasil didownload ke: {save_path}")
                                    self.log_message.emit(f"File berhasil didownload: {doc_name}")
                                    
                                except Exception as e:
                                    self.log_message.emit(f"Error saving file: {str(e)}")
                                    QMessageBox.critical(self, "Error", f"Gagal menyimpan file: {str(e)}")
                            else:
                                self.log_message.emit(f"ERROR: Invalid file content - type: {type(file_content)}")
                                QMessageBox.critical(self, "Error", "Format file tidak valid dari server")
                        else:
                            QMessageBox.critical(self, "Error", f"Gagal download dokumen: {result}")
                            self.log_message.emit(f"Error download dokumen: {result}")
                    else:
                        QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Gagal download dokumen: {str(e)}")
                    self.log_message.emit(f"Error download dokumen: {str(e)}")
                finally:
                    self.progress_bar.setVisible(False)
    
    def delete_document(self, row):
        current_docs = self.filtered_documents if hasattr(self, 'filtered_documents') else self.all_documents
        if row < len(current_docs):
            doc = current_docs[row]
            doc_name = doc.get('nama_dokumen', 'Unknown') or doc.get('file_name', 'Unknown') or 'Unknown'
            doc_id = doc.get('id_dokumen') or doc.get('file_id') or doc.get('id')
            
            if not doc_id:
                QMessageBox.warning(self, "Error", "ID dokumen tidak ditemukan")
                return
            
            reply = QMessageBox.question(
                self, "Konfirmasi Hapus", 
                f"Yakin ingin menghapus dokumen '{doc_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    if self.database_manager:
                        success, result = self.database_manager.delete_file(doc_id)
                        if success:
                            QMessageBox.information(self, "Sukses", "Dokumen berhasil dihapus")
                            self.load_data()
                            self.log_message.emit(f"Dokumen dihapus: {doc_name}")
                        else:
                            QMessageBox.critical(self, "Error", f"Gagal menghapus dokumen: {result}")
                            self.log_message.emit(f"Error hapus dokumen: {result}")
                    else:
                        QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error menghapus dokumen: {str(e)}")
                    self.log_message.emit(f"Exception hapus dokumen: {str(e)}")
    
    def upload_document(self):
        # Tampilkan dialog upload
        dialog = UploadDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            self.log_message.emit("Upload dibatalkan oleh user")
            return
        
        file_path = dialog.file_path
        document_name = dialog.document_name
        document_type = dialog.document_type
        
        if not self.database_manager:
            QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
            self.log_message.emit("Error: Database manager tidak tersedia untuk upload")
            return
        
        # Check if upload_file method exists
        if not hasattr(self.database_manager, 'upload_file'):
            QMessageBox.critical(self, "Error", "Method upload_file tidak ditemukan di database manager")
            self.log_message.emit("Error: Method upload_file tidak tersedia")
            return
        
        # Validate file exists and accessible
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", "File tidak ditemukan")
            self.log_message.emit(f"Error: File tidak ditemukan - {file_path}")
            return
        
        try:
            # Check file size (max 50MB)
            file_size = os.path.getsize(file_path)
            self.log_message.emit(f"Ukuran file: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
            
            if file_size > 52428800:  # 50MB
                QMessageBox.warning(self, "Error", "Ukuran file terlalu besar (max 50MB)")
                self.log_message.emit(f"Error: File terlalu besar - {file_size} bytes")
                return
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal mengecek ukuran file: {str(e)}")
            self.log_message.emit(f"Error mengecek ukuran file: {str(e)}")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        try:
            self.log_message.emit(f"Memulai upload file: {document_name}")
            self.log_message.emit(f"DEBUG Upload - document_name: '{document_name}'")
            self.log_message.emit(f"DEBUG Upload - document_type: '{document_type}'")
            self.log_message.emit(f"DEBUG Upload - file_path: '{file_path}'")
            
            # Progress simulation
            for i in range(1, 51, 10):
                self.progress_bar.setValue(i)
                QApplication.processEvents()
            
            self.log_message.emit("Memanggil database_manager.upload_file...")
            
            # Upload file melalui API dengan informasi tambahan
            try:
                # Try with new parameters first
                success, result = self.database_manager.upload_file(
                    file_path, 
                    document_name=document_name, 
                    document_type=document_type
                )
                self.log_message.emit(f"DEBUG Upload - API call dengan parameter berhasil")
            except TypeError:
                # Fallback to old method if new parameters not supported
                self.log_message.emit("Database manager belum mendukung parameter baru, menggunakan method lama...")
                success, result = self.database_manager.upload_file(file_path)
            
            self.progress_bar.setValue(75)
            QApplication.processEvents()
            
            self.log_message.emit(f"Hasil upload - Success: {success}, Result: {result}")
            
            if success:
                self.progress_bar.setValue(100)
                QApplication.processEvents()
                
                QMessageBox.information(self, "Sukses", f"Dokumen '{document_name}' berhasil diupload!")
                self.log_message.emit(f"Dokumen {document_name} ({document_type}) berhasil diupload")
                self.load_data()
            else:
                error_msg = str(result) if result else "Unknown error"
                QMessageBox.critical(self, "Error", f"Gagal upload dokumen: {error_msg}")
                self.log_message.emit(f"Gagal upload dokumen: {error_msg}")
        except AttributeError as e:
            error_msg = f"Method tidak ditemukan: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            self.log_message.emit(f"AttributeError upload dokumen: {error_msg}")
        except Exception as e:
            error_msg = f"Error upload dokumen: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            self.log_message.emit(f"Exception upload dokumen: {error_msg}")
        finally:
            self.progress_bar.setVisible(False)
    
    def auto_refresh(self):
        self.load_data()
    
    def get_data(self):
        return self.all_documents