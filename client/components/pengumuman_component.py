# Path: client/components/pengumuman_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QTextBrowser,
                             QMessageBox, QSplitter, QLabel, QHBoxLayout, QPushButton, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
import os

class PengumumanComponent(QWidget):
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.pengumuman_data = []
        self.init_ui()
        self.load_pengumuman()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Header with title (matching dokumen_component.py style)
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                padding: 10px 0px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("Pengumuman Gereja")
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

        refresh_button = QPushButton(" Refresh")
        refresh_button.clicked.connect(self.load_pengumuman)

        # Add refresh icon
        refresh_icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "refresh.png")
        if os.path.exists(refresh_icon_path):
            refresh_button.setIcon(QIcon(refresh_icon_path))
            refresh_button.setIconSize(QSize(16, 16))

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
        layout.addWidget(header, 0)

        # Splitter untuk list dan detail pengumuman
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel kiri - List pengumuman
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 5, 5, 10)
        left_layout.setSpacing(3)

        # List title
        list_title = QLabel("Daftar Pengumuman")
        list_title_font = QFont("Arial", 10, QFont.Bold)
        list_title.setFont(list_title_font)
        list_title.setStyleSheet("""
            QLabel {
                color: #34495e;
                padding: 0px;
                background-color: transparent;
            }
        """)
        left_layout.addWidget(list_title)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.display_pengumuman)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #ffffff;
                padding: 2px;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-bottom: 1px solid #e5e7eb;
                margin: 3px 2px;
                border-radius: 0px;
                background-color: transparent;
            }
            QListWidget::item:hover {
                background-color: #e8f4f8;
                border-left: 3px solid #3498db;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
                border: none;
                font-weight: 500;
            }
        """)
        left_layout.addWidget(self.list_widget)

        # Panel kanan - Detail pengumuman
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 10, 10)
        right_layout.setSpacing(3)

        detail_title = QLabel("Detail Pengumuman")
        detail_title_font = QFont("Arial", 10, QFont.Bold)
        detail_title.setFont(detail_title_font)
        detail_title.setStyleSheet("""
            QLabel {
                color: #34495e;
                padding: 0px;
                background-color: transparent;
            }
        """)
        right_layout.addWidget(detail_title)

        self.detail_browser = QTextBrowser()
        self.detail_browser.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 2px;
            }
        """)
        right_layout.addWidget(self.detail_browser)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        # Style splitter handle
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e5e7eb;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #9ca3af;
            }
        """)

        layout.addWidget(splitter, 1)

    def load_pengumuman(self):
        """Load pengumuman resmi dari API"""
        self.list_widget.clear()
        self.detail_browser.clear()
        self.list_widget.addItem("Memuat data pengumuman...")
        
        result = self.api_client.get_pengumuman()
        self.on_pengumuman_loaded(result["success"], result["data"])

    def on_pengumuman_loaded(self, success, data):
        """Handler ketika pengumuman berhasil dimuat"""
        self.list_widget.clear()
        if success:
            if data.get("status") == "success":
                self.pengumuman_data = data.get("data", [])
                if not self.pengumuman_data:
                    self.list_widget.addItem("Tidak ada pengumuman aktif.")
                else:
                    for item in self.pengumuman_data:
                        title = item.get('judul', 'Tanpa Judul')
                        # Add sasaran indicator for better visibility
                        sasaran = item.get('sasaran', '')
                        if sasaran and sasaran != 'Umum':
                            title = f"[{sasaran}] {title}"

                        self.list_widget.addItem(title)
            else:
                self.list_widget.addItem("Gagal memuat data.")
                QMessageBox.warning(self, "Error", f"API Error: {data.get('message', 'Unknown error')}")
        else:
            self.list_widget.addItem("Gagal memuat data.")
            QMessageBox.warning(self, "Error", f"Tidak dapat memuat pengumuman: {data}")

    def display_pengumuman(self, index):
        """Tampilkan detail pengumuman yang dipilih"""
        if 0 <= index < len(self.pengumuman_data):
            item = self.pengumuman_data[index]

            # Format tanggal dari created_at (sama dengan server)
            import datetime
            tanggal_value = item.get('created_at') or item.get('tanggal') or item.get('tanggal_mulai')

            # Indonesian names mapping
            day_names_id = {
                'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
                'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
            }
            month_names_id = {
                1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
                5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
                9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
            }

            periode = ''
            if tanggal_value:
                try:
                    date_obj = None

                    # Try RFC 822 format first (from API): "Thu, 09 Oct 2025 23:44:21 GMT"
                    if isinstance(tanggal_value, str):
                        try:
                            date_obj = datetime.datetime.strptime(tanggal_value, '%a, %d %b %Y %H:%M:%S GMT').date()
                        except:
                            # Try other formats
                            date_str = tanggal_value.split(' ')[0] if ' ' in tanggal_value else tanggal_value
                            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y']:
                                try:
                                    date_obj = datetime.datetime.strptime(date_str, fmt).date()
                                    break
                                except:
                                    continue

                    # Format to Indonesian
                    if date_obj:
                        english_day = date_obj.strftime('%A')
                        indonesian_day = day_names_id.get(english_day, english_day)
                        indonesian_month = month_names_id.get(date_obj.month, str(date_obj.month))
                        periode = f"{indonesian_day}, {date_obj.day:02d} {indonesian_month} {date_obj.year}"
                    else:
                        periode = str(tanggal_value)
                except:
                    periode = str(tanggal_value) if tanggal_value else 'Tidak ada tanggal'
            else:
                periode = 'Tidak ada tanggal'

            # Get data
            sasaran = item.get('sasaran', item.get('kategori', 'Umum'))
            penanggung_jawab = item.get('penanggung_jawab', item.get('pembuat', '-'))
            pembuat = item.get('pembuat', 'System')

            # Format isi with auto-bold labels
            isi_raw = item.get('isi', 'Tidak ada konten.')
            isi_formatted = isi_raw.replace('\n', '<br>')

            # Auto-bold labels like "Hari/Tanggal:", "Waktu:", "Tempat:", etc.
            import re
            label_pattern = r'([A-Za-z/]+(?:\s+[A-Za-z/]+)*)\s*:'

            def bold_label(match):
                label = match.group(1)
                return f'<b>{label}:</b>'

            isi_formatted = re.sub(label_pattern, bold_label, isi_formatted)

            html = f"""
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                }}
                .title {{
                    color: #2c3e50;
                    font-size: 20px;
                    font-weight: bold;
                    margin: 0 0 20px 0;
                    padding-bottom: 2px;
                    border-bottom: 2px solid #3498db;
                }}
                .info-row {{
                    margin: 10px 0;
                    padding: 8px 0;
                    border-bottom: 1px solid #ecf0f1;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #34495e;
                    display: inline-block;
                    min-width: 140px;
                }}
                .detail-value {{
                    color: #2c3e50;
                }}
                .content-section {{
                    margin-top: 20px;
                    padding-top: 2px;
                    border-top: 2px solid #ecf0f1;
                }}
                .content-title {{
                    font-weight: bold;
                    color: #2c3e50;
                    font-size: 14px;
                    margin-bottom: 12px;
                }}
                .detail-content {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    padding: 2px;
                    background-color: #f8f9fa;
                    border-left: 4px solid #3498db;
                    border-radius: 4px;
                    line-height: 1.8;
                    color: #2c3e50;
                }}
            </style>
            <div class="title">{item.get('judul', 'Tanpa Judul')}</div>
            <div class="info-row"><span class="detail-label">Tanggal:</span> <span class="detail-value">{periode}</span></div>
            <div class="info-row"><span class="detail-label">Pembuat:</span> <span class="detail-value">{pembuat}</span></div>
            <div class="info-row"><span class="detail-label">Penanggung Jawab:</span> <span class="detail-value">{penanggung_jawab}</span></div>
            <div class="info-row" style="border-bottom: none;"><span class="detail-label">Sasaran/Tujuan:</span> <span class="detail-value">{sasaran}</span></div>
            <div class="content-section">
                <div class="content-title">Isi Pengumuman:</div>
                <div class="detail-content">{isi_formatted}</div>
            </div>
            """
            self.detail_browser.setHtml(html)