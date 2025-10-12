# Path: client/components/dokumen_component.py

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QMessageBox, 
                             QFileDialog, QProgressBar, QLabel, QApplication, 
                             QComboBox, QLineEdit, QFormLayout, QDialog, QDialogButtonBox)
from PyQt5.QtCore import pyqtSignal

class UploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upload File")
        self.setMinimumSize(400, 200)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # File path
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(browse_btn)
        form_layout.addRow("File:", file_layout)
        
        # Kategori
        self.kategori_combo = QComboBox()
        self.kategori_combo.addItems(["Surat", "Laporan", "Foto", "Video", "Audio", "Lainnya"])
        self.kategori_combo.setCurrentText("Lainnya")
        form_layout.addRow("Kategori:", self.kategori_combo)
        
        # Keterangan
        self.keterangan_input = QLineEdit()
        self.keterangan_input.setPlaceholderText("Keterangan file...")
        form_layout.addRow("Keterangan:", self.keterangan_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)  # type: ignore
        buttons.rejected.connect(self.reject)  # type: ignore
        layout.addWidget(buttons)
        
        self.selected_file = None
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File untuk Upload", "", 
            "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx);;Excel Files (*.xlsx);;Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.file_path.setText(file_path)
            self.selected_file = file_path
    
    def get_upload_data(self):
        return {
            'file_path': self.selected_file,
            'kategori': self.kategori_combo.currentText(),
            'keterangan': self.keterangan_input.text()
        }

class DokumenComponent(QWidget):
    
    def __init__(self, api_client, config, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.config = config
        self.files_data = []
        self.init_ui()
        self.load_files()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Daftar Dokumen dari Server"))
        header_layout.addStretch()
        
        upload_button = QPushButton("Upload File")
        upload_button.clicked.connect(self.upload_file)
        upload_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        header_layout.addWidget(upload_button)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_files)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        header_layout.addWidget(refresh_button)
        layout.addLayout(header_layout)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["Nama File", "Kategori", "Ukuran", "Tipe", "Upload By", "Aksi"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        layout.addWidget(self.table_widget)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    def load_files(self):
        self.table_widget.setRowCount(0)
        
        result = self.api_client.get_files()
        if result["success"]:
            data = result["data"]
            if data.get("status") == "success":
                self.on_files_loaded(True, data.get("data", []))
            else:
                self.on_files_loaded(False, data.get("message", "API Error"))
        else:
            self.on_files_loaded(False, result["data"])
    
    def upload_file(self):
        dialog = UploadDialog(self)
        if dialog.exec_() == dialog.Accepted:
            upload_data = dialog.get_upload_data()
            
            if not upload_data['file_path']:
                QMessageBox.warning(self, "Error", "Pilih file untuk diupload")
                return
            
            if not os.path.exists(upload_data['file_path']):
                QMessageBox.warning(self, "Error", "File tidak ditemukan")
                return
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            try:
                # Progress update
                for i in range(1, 51, 10):
                    self.progress_bar.setValue(i)
                    QApplication.processEvents()
                
                # Upload file menggunakan API
                result = self.api_client.upload_file(
                    upload_data['file_path'],
                    upload_data['kategori'],
                    upload_data['keterangan']
                )
                
                self.progress_bar.setValue(75)
                QApplication.processEvents()
                
                if result["success"]:
                    response_data = result["data"]
                    if response_data.get("status") == "success":
                        self.progress_bar.setValue(100)
                        QApplication.processEvents()
                        
                        QMessageBox.information(self, "Sukses", "File berhasil diupload ke server!")
                        self.load_files()  # Refresh daftar file
                    else:
                        QMessageBox.critical(self, "Error", f"Upload gagal: {response_data.get('message', 'Unknown error')}")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal upload file: {result['data']}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error upload file: {str(e)}")
            finally:
                self.progress_bar.setVisible(False)

    def on_files_loaded(self, success, data):
        if not success:
            QMessageBox.warning(self, "Error", f"Gagal memuat daftar file: {data}")
            return

        self.files_data = data
        self.table_widget.setRowCount(len(self.files_data))

        for i, file_info in enumerate(self.files_data):
            # -----------------------------
            # Nama file
            nama_file = file_info.get('nama_dokumen', 'Unknown')
            self.table_widget.setItem(i, 0, QTableWidgetItem(nama_file))

            # Kategori
            kategori = file_info.get('kategori', 'Lainnya') or 'Lainnya'
            self.table_widget.setItem(i, 1, QTableWidgetItem(kategori))

            # Ukuran
            size_bytes = file_info.get('ukuran_file') or 0
            try:
                size_bytes = int(size_bytes)
            except (ValueError, TypeError):
                size_bytes = 0

            if size_bytes > 1_048_576:
                size_str = f"{size_bytes / 1_048_576:.2f} MB"
            elif size_bytes > 1024:
                size_str = f"{size_bytes / 1024:.2f} KB"
            else:
                size_str = f"{size_bytes} B"
            self.table_widget.setItem(i, 2, QTableWidgetItem(size_str))

            # -----------------------------
            # Tipe file  (PERBAIKAN DI SINI)
            raw_tipe_file = file_info.get('tipe_file')       # Bisa None
            tipe_file_lc  = str(raw_tipe_file or '').lower()  # Selalu string

            if 'pdf' in tipe_file_lc:
                type_display = "PDF"
            elif any(key in tipe_file_lc for key in ('word', 'document', 'msword')):
                type_display = "Word"
            elif any(key in tipe_file_lc for key in ('excel', 'sheet')):
                type_display = "Excel"
            elif any(key in tipe_file_lc for key in ('image', 'png', 'jpg', 'jpeg')):
                type_display = "Image"
            else:
                # Ambil ekstensi atau sub‑type MIME kalau ada
                if '/' in tipe_file_lc:
                    type_display = tipe_file_lc.split('/')[-1].upper()
                else:
                    type_display = (tipe_file_lc or 'UNKNOWN').upper()
            self.table_widget.setItem(i, 3, QTableWidgetItem(type_display))

            # -----------------------------
            # Upload by
            upload_by = file_info.get('uploaded_by_name', 'Unknown')
            self.table_widget.setItem(i, 4, QTableWidgetItem(upload_by))

            # Tombol aksi (download)
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            download_btn = QPushButton("Download")
            download_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 4px 8px;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            download_btn.clicked.connect(lambda _, r=i: self.download_file(r))
            btn_layout.addWidget(download_btn)

            self.table_widget.setCellWidget(i, 5, btn_widget)   
    def download_file(self, row):
        if row >= len(self.files_data):
            return
            
        file_info = self.files_data[row]
        file_name = file_info.get('nama_dokumen', 'document')
        file_id = file_info.get('id_dokumen')
        
        if not file_id:
            QMessageBox.warning(self, "Error", "ID file tidak ditemukan")
            return
        
        download_dir = self.config.get('download_dir', os.path.expanduser("~/Downloads"))
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan File", 
            os.path.join(download_dir, file_name)
        )

        if not save_path:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        try:
            # Progress update
            self.progress_bar.setValue(25)
            QApplication.processEvents()
            
            result = self.api_client.download_file(file_id)
            
            self.progress_bar.setValue(75)
            QApplication.processEvents()
            
            if result["success"]:
                file_content = result["data"]
                
                with open(save_path, 'wb') as f:
                    f.write(file_content)
                
                self.progress_bar.setValue(100)
                QApplication.processEvents()
                
                QMessageBox.information(self, "Sukses", f"File berhasil didownload ke {save_path}")
            else:
                QMessageBox.critical(self, "Error", f"Gagal download file: {result['data']}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error download file: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_download_finished(self, success, message):
        self.progress_bar.setVisible(False)
        if success:
            QMessageBox.information(self, "Sukses", message)
        else:
            QMessageBox.critical(self, "Gagal", message)