# Path: server/components/dokumen.py

import os
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QLabel, QPushButton, 
                            QLineEdit, QMessageBox, QFrame, QProgressBar, QFileDialog,
                            QApplication, QAbstractItemView, QDialog, QComboBox, QFormLayout,
                            QDialogButtonBox, QMenu)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon

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
        
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #34495e; color: white; padding: 2px;")
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("Manajemen Dokumen Sistem")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        toolbar_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari dokumen...")
        self.search_input.textChanged.connect(self.filter_data)
        toolbar_layout.addWidget(QLabel("Cari:"))
        toolbar_layout.addWidget(self.search_input)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_data)
        self.refresh_button.setStyleSheet("""
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
        toolbar_layout.addWidget(self.refresh_button)
        
        self.upload_button = QPushButton("Upload Dokumen")
        self.upload_button.clicked.connect(self.upload_document)
        self.upload_button.setStyleSheet("""
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
        
        # Tabel dokumen (hapus kolom ID)
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels([
            "Nama Dokumen", "Jenis Dokumen", "Ukuran", "Tipe File", "Upload By", "Tanggal Upload", "Aksi"
        ])
        
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Enable context menu untuk aksi
        self.table_widget.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table_widget)
        
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
                           if doc.get('jenis_dokumen', '') == self.current_doc_type_filter]
        
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
            nama_dokumen = doc.get('nama_dokumen', '') or ''
            self.table_widget.setItem(i, 0, QTableWidgetItem(str(nama_dokumen)))
            
            # Jenis dokumen
            jenis_dokumen = doc.get('jenis_dokumen', '') or ''
            self.table_widget.setItem(i, 1, QTableWidgetItem(str(jenis_dokumen)))
            
            # Ukuran file
            size_bytes = doc.get('ukuran_file', 0) or 0
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
            
            # Tipe file
            file_type = doc.get('tipe_file', '') or ''
            if 'pdf' in file_type.lower():
                type_display = "PDF"
            elif 'word' in file_type.lower() or 'document' in file_type.lower():
                type_display = "Word"
            elif 'excel' in file_type.lower() or 'sheet' in file_type.lower():
                type_display = "Excel"
            elif 'image' in file_type.lower():
                type_display = "Image"
            else:
                type_display = file_type.split('/')[-1].upper() if '/' in file_type else file_type
            self.table_widget.setItem(i, 3, QTableWidgetItem(type_display))
            
            # Upload by
            upload_by = doc.get('uploaded_by_name', '') or 'Unknown'
            self.table_widget.setItem(i, 4, QTableWidgetItem(str(upload_by)))
            
            # Tanggal upload
            upload_date = doc.get('upload_date', '') or ''
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
            action_layout.setContentsMargins(2, 2, 2, 2)
            
            # View button with lihat.png icon
            view_button = QPushButton()
            view_icon = QIcon("server/assets/lihat.png")
            view_button.setIcon(view_icon)
            view_button.setIconSize(Qt.QSize(16, 16))
            view_button.setStyleSheet("""
                QPushButton { 
                    background-color: #f1c40f; 
                    color: white; 
                    padding: 6px; 
                    border: none; 
                    border-radius: 4px;
                    min-width: 30px;
                    max-width: 30px;
                    min-height: 30px;
                    max-height: 30px;
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
            download_button.setIconSize(Qt.QSize(16, 16))
            download_button.setStyleSheet("""
                QPushButton { 
                    background-color: #27ae60; 
                    color: white; 
                    padding: 6px; 
                    border: none; 
                    border-radius: 4px;
                    min-width: 30px;
                    max-width: 30px;
                    min-height: 30px;
                    max-height: 30px;
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
            delete_button.setIconSize(Qt.QSize(16, 16))
            delete_button.setStyleSheet("""
                QPushButton { 
                    background-color: #e74c3c; 
                    color: white; 
                    padding: 6px; 
                    border: none; 
                    border-radius: 4px;
                    min-width: 30px;
                    max-width: 30px;
                    min-height: 30px;
                    max-height: 30px;
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
                nama_dokumen = doc.get('nama_dokumen', '') or ''
                uploaded_by = doc.get('uploaded_by_name', '') or ''
                tipe_file = doc.get('tipe_file', '') or ''
                jenis_dokumen = doc.get('jenis_dokumen', '') or ''
                
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
            size = doc.get('ukuran_file', 0) or 0
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
            doc_name = doc.get('nama_dokumen', 'Unknown') or 'Unknown'
            jenis_dokumen = doc.get('jenis_dokumen', 'Unknown') or 'Unknown'
            size = doc.get('ukuran_file', 0) or 0
            file_type = doc.get('tipe_file', 'Unknown') or 'Unknown'
            uploaded_by = doc.get('uploaded_by_name', 'Unknown') or 'Unknown'
            upload_date = doc.get('upload_date', 'Unknown') or 'Unknown'
            
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
            doc_name = doc.get('nama_dokumen', 'Unknown') or 'document'
            doc_id = doc.get('id_dokumen')
            
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
                            if file_content:
                                with open(save_path, 'wb') as f:
                                    f.write(file_content)
                                
                                self.progress_bar.setValue(100)
                                QApplication.processEvents()
                                
                                QMessageBox.information(self, "Download", 
                                                      f"Dokumen '{doc_name}' berhasil didownload ke {save_path}")
                                self.log_message.emit(f"Download dokumen berhasil: {doc_name}")
                            else:
                                QMessageBox.warning(self, "Error", "File content kosong")
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
            doc_name = doc.get('nama_dokumen', 'Unknown') or 'Unknown'
            doc_id = doc.get('id_dokumen')
            
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