# Path: server/components/dokumen.py

import os
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QLabel, QPushButton, 
                            QLineEdit, QMessageBox, QFrame, QProgressBar, QFileDialog,
                            QApplication, QAbstractItemView)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon

class DokumenComponent(QWidget):
    
    log_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.database_manager = None
        self.all_documents = []
        self.setup_ui()
        self.setup_timer()
    
    def set_database_manager(self, database_manager):
        self.database_manager = database_manager
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #34495e; color: white; padding: 10px;")
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
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Tabel dokumen (hapus kolom ID)
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels([
            "Nama Dokumen", "Ukuran", "Tipe File", "Upload By", "Tanggal Upload", "Aksi"
        ])
        
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
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
    
    def show_context_menu(self, position):
        """Tampilkan context menu untuk aksi dokumen"""
        if self.table_widget.rowCount() == 0:
            return
            
        from PyQt5.QtWidgets import QMenu
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
                
                self.update_table_display(self.all_documents)
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
            self.table_widget.setItem(i, 1, QTableWidgetItem(size_str))
            
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
            self.table_widget.setItem(i, 2, QTableWidgetItem(type_display))
            
            # Upload by
            upload_by = doc.get('uploaded_by_name', '') or 'Unknown'
            self.table_widget.setItem(i, 3, QTableWidgetItem(str(upload_by)))
            
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
            self.table_widget.setItem(i, 4, QTableWidgetItem(date_str))
            
            # Aksi buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            
            view_button = QPushButton("Lihat")
            view_button.setStyleSheet("QPushButton { background-color: #3498db; color: white; padding: 2px 6px; border: none; border-radius: 2px; }")
            view_button.clicked.connect(lambda _, row=i: self.view_document(row))
            action_layout.addWidget(view_button)
            
            download_button = QPushButton("Download")
            download_button.setStyleSheet("QPushButton { background-color: #27ae60; color: white; padding: 2px 6px; border: none; border-radius: 2px; }")
            download_button.clicked.connect(lambda _, row=i: self.download_document(row))
            action_layout.addWidget(download_button)
            
            delete_button = QPushButton("Hapus")
            delete_button.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; padding: 2px 6px; border: none; border-radius: 2px; }")
            delete_button.clicked.connect(lambda _, row=i: self.delete_document(row))
            action_layout.addWidget(delete_button)
            
            self.table_widget.setCellWidget(i, 5, action_widget)
    
    def filter_data(self):
        search_text = self.search_input.text().lower()
        
        if not search_text:
            filtered_docs = self.all_documents
        else:
            filtered_docs = []
            for doc in self.all_documents:
                nama_dokumen = doc.get('nama_dokumen', '') or ''
                uploaded_by = doc.get('uploaded_by_name', '') or ''
                tipe_file = doc.get('tipe_file', '') or ''
                
                if (search_text in nama_dokumen.lower() or 
                    search_text in uploaded_by.lower() or
                    search_text in tipe_file.lower()):
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
        if row < len(self.all_documents):
            doc = self.all_documents[row]
            doc_name = doc.get('nama_dokumen', 'Unknown') or 'Unknown'
            size = doc.get('ukuran_file', 0) or 0
            file_type = doc.get('tipe_file', 'Unknown') or 'Unknown'
            uploaded_by = doc.get('uploaded_by_name', 'Unknown') or 'Unknown'
            upload_date = doc.get('upload_date', 'Unknown') or 'Unknown'
            
            QMessageBox.information(
                self, "Info Dokumen", 
                f"Nama: {doc_name}\n"
                f"Ukuran: {size} bytes\n"
                f"Tipe: {file_type}\n"
                f"Upload by: {uploaded_by}\n"
                f"Tanggal: {upload_date}"
            )
            self.log_message.emit(f"Melihat info dokumen: {doc_name}")
    
    def download_document(self, row):
        if row < len(self.all_documents):
            doc = self.all_documents[row]
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
        if row < len(self.all_documents):
            doc = self.all_documents[row]
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
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Dokumen untuk Upload", "", 
            "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx);;Excel Files (*.xlsx);;Images (*.png *.jpg *.jpeg)"
        )
        
        if not file_path:
            return
        
        if not self.database_manager:
            QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
            return
        
        # Check file size (max 50MB)
        file_size = os.path.getsize(file_path)
        if file_size > 52428800:  # 50MB
            QMessageBox.warning(self, "Error", "Ukuran file terlalu besar (max 50MB)")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        try:
            # Progress simulation
            for i in range(1, 51, 10):
                self.progress_bar.setValue(i)
                QApplication.processEvents()
            
            # Upload file melalui API
            success, result = self.database_manager.upload_file(file_path)
            
            self.progress_bar.setValue(75)
            QApplication.processEvents()
            
            if success:
                self.progress_bar.setValue(100)
                QApplication.processEvents()
                
                QMessageBox.information(self, "Sukses", "Dokumen berhasil diupload!")
                self.log_message.emit(f"Dokumen {os.path.basename(file_path)} berhasil diupload")
                self.load_data()
            else:
                error_msg = str(result) if result else "Unknown error"
                QMessageBox.critical(self, "Error", f"Gagal upload dokumen: {error_msg}")
                self.log_message.emit(f"Gagal upload dokumen: {error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error upload dokumen: {str(e)}")
            self.log_message.emit(f"Error upload dokumen: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
    
    def auto_refresh(self):
        self.load_data()
    
    def get_data(self):
        return self.all_documents