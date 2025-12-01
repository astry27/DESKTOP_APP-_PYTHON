# Path: client/components/dokumen_component.py

import datetime
import os
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QFileDialog,
    QProgressBar,
    QLabel,
    QApplication,
    QAbstractItemView,
    QFrame,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon


class DokumenComponent(QWidget):

    def __init__(self, api_client, config, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.config = config
        self.files_data = []
        self.table_widget = None  # type: ignore
        self.download_button = None  # type: ignore
        self.progress_bar = None  # type: ignore
        self.init_ui()
        self.load_files()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Header with title (matching proker_component.py style)
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                padding: 10px 0px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("Manajemen Dokumen")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Download button with icon
        self.download_button = QPushButton(" Download")
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.download_selected_file)
        try:
            download_icon = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'unduh.png'))
            if not download_icon.isNull():
                self.download_button.setIcon(download_icon)
                self.download_button.setIconSize(QSize(16, 16))
        except:
            pass
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #ecf0f1;
            }
            QPushButton:hover:!disabled {
                background-color: #2980b9;
            }
        """)
        header_layout.addWidget(self.download_button)

        # Refresh button with icon
        refresh_button = QPushButton(" Refresh")
        refresh_button.clicked.connect(self.load_files)
        try:
            refresh_icon = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'refresh.png'))
            if not refresh_icon.isNull():
                refresh_button.setIcon(refresh_icon)
                refresh_button.setIconSize(QSize(16, 16))
        except:
            pass
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        header_layout.addWidget(refresh_button)
        layout.addWidget(header)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels([
            "Nama Dokumen",
            "Kategori",
            "Bentuk",
            "Ukuran",
            "Keterangan",
            "Upload By",
            "Tanggal Upload",
        ])
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # Set preferred column widths (matching server/components/dokumen.py)
        self.table_widget.setColumnWidth(0, 200)
        self.table_widget.setColumnWidth(1, 140)
        self.table_widget.setColumnWidth(2, 140)
        self.table_widget.setColumnWidth(3, 100)
        self.table_widget.setColumnWidth(4, 150)
        self.table_widget.setColumnWidth(5, 120)
        self.table_widget.setColumnWidth(6, 140)

        self.table_widget.setFocusPolicy(Qt.StrongFocus)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.verticalHeader().setVisible(True)
        self.table_widget.verticalHeader().setDefaultSectionSize(34)

        self.table_widget.itemSelectionChanged.connect(self.update_download_button_state)
        self.table_widget.doubleClicked.connect(self.on_row_double_clicked)

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

    def on_files_loaded(self, success, data):
        if not success:
            QMessageBox.warning(self, "Error", f"Gagal memuat daftar file: {data}")
            self.files_data = []
            self.table_widget.setRowCount(0)
            self.update_download_button_state()
            return

        self.files_data = data or []
        self.table_widget.setRowCount(len(self.files_data))

        for row, file_info in enumerate(self.files_data):
            document_name = self._resolve_document_name(file_info)
            kategori_dokumen = self._resolve_document_category(file_info)
            bentuk_dokumen = self._resolve_bentuk_dokumen(file_info)
            size_display = self._format_file_size(file_info)
            description_text, description_tooltip = self._resolve_description(file_info)
            uploader = self._resolve_uploader(file_info)
            upload_date = self._resolve_upload_date(file_info)

            # Column 0: Nama Dokumen
            self.table_widget.setItem(row, 0, self._create_item(document_name))
            # Column 1: Kategori (jenis dokumen)
            self.table_widget.setItem(row, 1, self._create_item(kategori_dokumen))
            # Column 2: Bentuk Dokumen
            self.table_widget.setItem(row, 2, self._create_item(bentuk_dokumen))
            # Column 3: Ukuran
            self.table_widget.setItem(
                row,
                3,
                self._create_item(size_display, alignment=Qt.AlignRight | Qt.AlignVCenter)
            )
            # Column 4: Keterangan
            self.table_widget.setItem(
                row,
                4,
                self._create_item(description_text, tooltip=description_tooltip)
            )
            # Column 5: Upload By
            self.table_widget.setItem(row, 5, self._create_item(uploader))
            # Column 6: Tanggal Upload
            self.table_widget.setItem(
                row,
                6,
                self._create_item(
                    upload_date,
                    alignment=Qt.AlignCenter | Qt.AlignVCenter
                )
            )
            self.table_widget.setRowHeight(row, 34)

        self.update_download_button_state()

    def update_download_button_state(self):
        if not self.download_button:
            return
        has_selection = self.table_widget.rowCount() > 0 and self.table_widget.currentRow() >= 0
        self.download_button.setEnabled(has_selection)

    def on_row_double_clicked(self, model_index):
        if model_index.isValid():
            self.download_file(model_index.row())

    def download_selected_file(self):
        row = self.table_widget.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih dokumen terlebih dahulu")
            return
        self.download_file(row)

    def download_file(self, row):
        if row < 0 or row >= len(self.files_data):
            return

        file_info = self.files_data[row]
        file_name = self._resolve_document_name(file_info)
        file_id = self._resolve_document_id(file_info)

        if not file_id:
            QMessageBox.warning(self, "Error", "ID file tidak ditemukan")
            return

        download_dir = self.config.get('download_dir', os.path.expanduser("~/Downloads"))
        suggested_path = os.path.join(download_dir, file_name)
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan File",
            suggested_path
        )

        if not save_path:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        try:
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
        if self.progress_bar:
            self.progress_bar.setValue(value)

    def on_download_finished(self, success, message):
        if not self.progress_bar:
            return
        self.progress_bar.setVisible(False)
        if success:
            QMessageBox.information(self, "Sukses", message)
        else:
            QMessageBox.critical(self, "Gagal", message)

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _create_item(self, text, alignment=Qt.AlignLeft | Qt.AlignVCenter, tooltip=None):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(alignment)
        if tooltip:
            item.setToolTip(str(tooltip))
        return item

    def _resolve_document_name(self, file_info):
        name_keys = [
            'nama_dokumen', 'document_name', 'name', 'file_name',
            'filename', 'original_name', 'nama_file'
        ]
        for key in name_keys:
            value = file_info.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        for path_key in ('file_path', 'path'):
            path_value = file_info.get(path_key)
            if isinstance(path_value, str) and path_value.strip():
                return os.path.basename(path_value.strip())

        return "Unknown Document"

    def _resolve_document_category(self, file_info):
        category_keys = [
            'kategori_file', 'jenis_dokumen', 'document_type', 'kategori', 'category',
            'type', 'doc_type', 'document_category'
        ]
        for key in category_keys:
            value = file_info.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return "-"

    def _resolve_bentuk_dokumen(self, file_info):
        bentuk_keys = [
            'bentuk_dokumen', 'bentuk', 'form', 'document_form',
            'kategori_file'
        ]
        for key in bentuk_keys:
            value = file_info.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return "-"

    def _resolve_description(self, file_info):
        description_keys = [
            'keterangan', 'description', 'deskripsi', 'notes', 'remark', 'catatan'
        ]
        description = ""
        for key in description_keys:
            value = file_info.get(key)
            if isinstance(value, str) and value.strip():
                description = value.strip()
                break

        if not description:
            return "-", None

        if len(description) > 80:
            return description[:77] + "...", description
        return description, None

    def _format_file_size(self, file_info):
        size_candidates = [
            file_info.get('ukuran_file'),
            file_info.get('file_size'),
            file_info.get('size')
        ]
        size_bytes = 0
        for value in size_candidates:
            if value in (None, "", "None"):
                continue
            try:
                size_bytes = int(float(value))
                break
            except (ValueError, TypeError):
                continue

        if size_bytes >= 1_048_576:
            return f"{size_bytes / 1_048_576:.2f} MB"
        if size_bytes >= 1024:
            return f"{size_bytes / 1024:.2f} KB"
        return f"{size_bytes} B"

    def _resolve_file_type(self, file_info):
        raw_type = file_info.get('tipe_file') or file_info.get('mime_type') or file_info.get('content_type') or ""
        raw_type = str(raw_type).strip()
        type_lc = raw_type.lower()

        if type_lc:
            if 'pdf' in type_lc:
                return "PDF Document", raw_type
            if any(token in type_lc for token in ('word', 'document', 'msword', 'docx')):
                return "Word Document", raw_type
            if any(token in type_lc for token in ('excel', 'sheet', 'xlsx', 'xls')):
                return "Excel Spreadsheet", raw_type
            if any(token in type_lc for token in ('powerpoint', 'presentation', 'ppt')):
                return "PowerPoint", raw_type
            if any(token in type_lc for token in ('image', 'png', 'jpg', 'jpeg', 'gif', 'bmp')):
                return "Image", raw_type
            if 'video' in type_lc:
                return "Video", raw_type
            if 'audio' in type_lc:
                return "Audio", raw_type
            if 'text' in type_lc:
                return "Text File", raw_type
            if any(token in type_lc for token in ('zip', 'rar', 'compressed', 'archive')):
                return "Archive", raw_type

        name = self._resolve_document_name(file_info)
        if '.' in name:
            ext = name.split('.')[-1].lower()
            mapping = {
                'pdf': "PDF Document",
                'doc': "Word Document",
                'docx': "Word Document",
                'xls': "Excel Spreadsheet",
                'xlsx': "Excel Spreadsheet",
                'ppt': "PowerPoint",
                'pptx': "PowerPoint",
                'jpg': "Image",
                'jpeg': "Image",
                'png': "Image",
                'gif': "Image",
                'bmp': "Image",
                'txt': "Text File",
                'zip': "Archive",
                'rar': "Archive",
            }
            friendly = mapping.get(ext, f"{ext.upper()} File")
            return friendly, raw_type

        return "Unknown", raw_type

    def _resolve_uploader(self, file_info):
        uploader_keys = [
            'uploaded_by_name', 'uploaded_by', 'uploader',
            'created_by', 'creator', 'user_name'
        ]
        for key in uploader_keys:
            value = file_info.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return "System"

    def _resolve_upload_date(self, file_info):
        date_keys = [
            'tanggal_upload', 'upload_date', 'created_at',
            'date_uploaded', 'updated_at'
        ]
        for key in date_keys:
            value = file_info.get(key)
            if not value:
                continue
            if isinstance(value, str):
                text = value.strip()
                if not text:
                    continue
                try:
                    parsed = datetime.datetime.fromisoformat(text.replace('Z', '+00:00'))
                    return parsed.strftime('%d/%m/%Y %H:%M')
                except ValueError:
                    return text
            if hasattr(value, 'strftime'):
                return value.strftime('%d/%m/%Y %H:%M')
            return str(value)
        return "-"

    def _resolve_document_id(self, file_info):
        id_keys = ['id_dokumen', 'file_id', 'id']
        for key in id_keys:
            value = file_info.get(key)
            if value:
                return value
        return None
