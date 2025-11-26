# Path: client/components/jemaat_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QPushButton, QFrame,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox,
                             QDialog, QFormLayout, QDateEdit, QTextEdit, QSpinBox,
                             QScrollArea, QGroupBox, QFileDialog, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QSize, QRect, QTimer
from typing import Optional, Dict, Any, List
from PyQt5.QtGui import QFont, QColor, QIcon, QPainter
import json
import os
from datetime import datetime, date

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

class JemaatDialog(QDialog):
    def __init__(self, parent=None, jemaat_data=None):
        super().__init__(parent)
        self.jemaat_data = jemaat_data if jemaat_data else {}
        self.setup_ui()

    def setup_placeholder_style(self, combo_box):
        """Setup placeholder style for combo box - matching server implementation"""
        # Initial style with placeholder appearance - keep default arrow
        combo_box.setStyleSheet("""
            QComboBox {
                color: #888888;
                font-style: italic;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #cccccc;
            }
            QComboBox QAbstractItemView::item {
                color: #000000;
                font-style: normal;
                font-weight: normal;
                padding: 4px;
                min-height: 18px;
            }
            QComboBox QAbstractItemView::item:first {
                color: #888888;
                font-style: italic;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e3f2fd;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        # Connect to handle style changes when user selects
        def on_selection_changed():
            if combo_box.currentIndex() == 0:
                # Placeholder selected - keep italic style for displayed text
                combo_box.setStyleSheet("""
                    QComboBox {
                        color: #888888;
                        font-style: italic;
                    }
                    QComboBox QAbstractItemView {
                        background-color: white;
                        border: 1px solid #cccccc;
                    }
                    QComboBox QAbstractItemView::item {
                        color: #000000;
                        font-style: normal;
                        font-weight: normal;
                        padding: 4px;
                        min-height: 18px;
                    }
                    QComboBox QAbstractItemView::item:first {
                        color: #888888;
                        font-style: italic;
                    }
                    QComboBox QAbstractItemView::item:hover {
                        background-color: #e3f2fd;
                    }
                    QComboBox QAbstractItemView::item:selected {
                        background-color: #3498db;
                        color: white;
                    }
                """)
            else:
                # Real value selected - normal style for displayed text
                combo_box.setStyleSheet("""
                    QComboBox {
                        color: #000000;
                        font-style: normal;
                    }
                    QComboBox QAbstractItemView {
                        background-color: white;
                        border: 1px solid #cccccc;
                    }
                    QComboBox QAbstractItemView::item {
                        color: #000000;
                        font-style: normal;
                        font-weight: normal;
                        padding: 4px;
                        min-height: 18px;
                    }
                    QComboBox QAbstractItemView::item:first {
                        color: #888888;
                        font-style: italic;
                    }
                    QComboBox QAbstractItemView::item:hover {
                        background-color: #e3f2fd;
                    }
                    QComboBox QAbstractItemView::item:selected {
                        background-color: #3498db;
                        color: white;
                    }
                """)

        combo_box.currentIndexChanged.connect(on_selection_changed)

    def setup_ui(self):
        self.setWindowTitle("Tambah/Edit Data Jemaat")
        self.setModal(True)
        self.resize(600, 700)

        layout = QVBoxLayout(self)

        # Scroll area for long form
        from PyQt5.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # 1. DATA PRIBADI
        self.setup_data_pribadi(scroll_layout)

        # 2. SAKRAMEN BABTIS
        self.setup_sakramen_babtis(scroll_layout)

        # 3. SAKRAMEN EKARISTI
        self.setup_sakramen_ekaristi(scroll_layout)

        # 4. SAKRAMEN KRISMA
        self.setup_sakramen_krisma(scroll_layout)

        # 5. SAKRAMEN PERKAWINAN
        self.setup_sakramen_perkawinan(scroll_layout)

        # 6. STATUS
        self.setup_status(scroll_layout)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        from PyQt5.QtWidgets import QDialogButtonBox
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
        layout.addWidget(button_box)

    def setup_data_pribadi(self, layout):
        """Setup section Data Pribadi"""
        from PyQt5.QtWidgets import QGroupBox
        data_pribadi_group = QGroupBox("1. DATA PRIBADI")
        data_pribadi_layout = QFormLayout(data_pribadi_group)

        self.wilayah_rohani = QComboBox()
        self.wilayah_rohani.addItems([
            "Pilih Wilayah Rohani",
            "ST. YOHANES BAPTISTA DE LA SALLE",
            "ST. ALOYSIUS GONZAGA",
            "ST. GREGORIUS AGUNG",
            "ST. DOMINICO SAVIO",
            "ST. THOMAS AQUINAS",
            "ST. ALBERTUS AGUNG",
            "ST. BONAVENTURA",
            "STA. KATARINA DARI SIENA",
            "STA. SISILIA",
            "ST. BLASIUS",
            "ST. CAROLUS BORROMEUS",
            "ST. BONIFASIUS",
            "ST. CORNELIUS",
            "STA. BRIGITTA",
            "ST. IGNASIUS DARI LOYOLA",
            "ST. PIUS X",
            "STA. AGNES",
            "ST. AGUSTINUS",
            "STA. FAUSTINA",
            "ST. YOHANES MARIA VIANNEY",
            "STA. MARIA GORETTI",
            "STA. PERPETUA",
            "ST. LUKAS",
            "STA. SKOLASTIKA",
            "STA. THERESIA DARI AVILLA",
            "ST. VINCENTIUS A PAULO"
        ])
        self.wilayah_rohani.setCurrentIndex(0)
        self.wilayah_rohani.setMinimumWidth(300)
        self.setup_placeholder_style(self.wilayah_rohani)
        if self.jemaat_data.get('wilayah_rohani'):
            index = self.wilayah_rohani.findText(self.jemaat_data['wilayah_rohani'])
            if index >= 0:
                self.wilayah_rohani.setCurrentIndex(index)

        self.nama_keluarga = QLineEdit(self.jemaat_data.get('nama_keluarga', ''))
        self.nama_keluarga.setMinimumWidth(300)

        self.no_kk = QLineEdit(self.jemaat_data.get('no_kk', ''))
        self.no_kk.setMinimumWidth(300)
        self.no_kk.setPlaceholderText("No. Kartu Keluarga (opsional)")

        self.nama_lengkap = QLineEdit(self.jemaat_data.get('nama_lengkap', ''))
        self.nama_lengkap.setMinimumWidth(300)

        self.tempat_lahir = QLineEdit(self.jemaat_data.get('tempat_lahir', ''))
        self.tempat_lahir.setMinimumWidth(300)

        self.nik = QLineEdit(self.jemaat_data.get('nik', ''))
        self.nik.setMinimumWidth(300)
        self.nik.setPlaceholderText("Nomor Identitas Kependudukan (opsional)")

        self.tanggal_lahir = QDateEdit()
        self.tanggal_lahir.setCalendarPopup(True)
        self.tanggal_lahir.setMinimumWidth(300)
        if self.jemaat_data.get('tanggal_lahir'):
            try:
                date_obj = datetime.strptime(self.jemaat_data['tanggal_lahir'], '%Y-%m-%d').date()
                self.tanggal_lahir.setDate(QDate.fromString(date_obj.isoformat(), Qt.DateFormat.ISODate)) # type: ignore
            except:
                self.tanggal_lahir.setDate(QDate.currentDate())
        else:
            self.tanggal_lahir.setDate(QDate.currentDate())

        self.umur = QLineEdit()
        self.umur.setMinimumWidth(300)
        self.umur.setReadOnly(True)
        self.umur.setPlaceholderText("Umur akan dihitung otomatis")

        # Connect after umur field is created
        self.tanggal_lahir.dateChanged.connect(self.calculate_age)  # type: ignore

        # Status Kekatolikan
        self.status_kekatolikan = QComboBox()
        self.status_kekatolikan.addItems(["Pilih Status Kekatolikan", "Kelahiran", "Babtisan", "Penerimaan", "Pindah Agama", "Lainnya"])
        self.status_kekatolikan.setCurrentIndex(0)
        self.status_kekatolikan.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_kekatolikan)
        self.status_kekatolikan.currentTextChanged.connect(self.on_status_kekatolikan_changed)  # type: ignore
        if self.jemaat_data.get('status_kekatolikan'):
            index = self.status_kekatolikan.findText(self.jemaat_data['status_kekatolikan'])
            if index >= 0:
                self.status_kekatolikan.blockSignals(True)
                self.status_kekatolikan.setCurrentIndex(index)
                self.status_kekatolikan.blockSignals(False)

        # Status Kekatolikan Lainnya (conditional field)
        self.status_kekatolikan_lainnya_label = QLabel("Status Kekatolikan Lainnya:")
        self.status_kekatolikan_lainnya = QLineEdit(self.jemaat_data.get('status_kekatolikan_lainnya', ''))
        self.status_kekatolikan_lainnya.setMinimumWidth(300)
        self.status_kekatolikan_lainnya.setVisible(False)
        self.status_kekatolikan_lainnya_label.setVisible(False)

        self.kategori = QComboBox()
        self.kategori.addItems(["Pilih Kategori", "Balita", "Anak-anak", "Remaja", "OMK", "KBK", "KIK", "Lansia"])
        self.kategori.setCurrentIndex(0)
        self.kategori.setMinimumWidth(300)
        self.setup_placeholder_style(self.kategori)
        if self.jemaat_data.get('kategori'):
            index = self.kategori.findText(self.jemaat_data['kategori'])
            if index >= 0:
                self.kategori.setCurrentIndex(index)

        self.jenis_kelamin = QComboBox()
        self.jenis_kelamin.addItems(["Pilih jenis kelamin", "L", "P"])
        self.jenis_kelamin.setCurrentIndex(0)
        self.jenis_kelamin.setMinimumWidth(300)
        self.setup_placeholder_style(self.jenis_kelamin)
        if self.jemaat_data.get('jenis_kelamin'):
            # Convert from full names to abbreviations
            if self.jemaat_data['jenis_kelamin'] in ['Laki-laki', 'L']:
                self.jenis_kelamin.setCurrentText("L")
            elif self.jemaat_data['jenis_kelamin'] in ['Perempuan', 'P']:
                self.jenis_kelamin.setCurrentText("P")

        self.hubungan_keluarga = QComboBox()
        self.hubungan_keluarga.addItems(["Pilih hubungan dalam keluarga", "Kepala Keluarga", "Istri", "Anak", "Famili lain"])
        self.hubungan_keluarga.setCurrentIndex(0)
        self.hubungan_keluarga.setMinimumWidth(300)
        self.setup_placeholder_style(self.hubungan_keluarga)
        if self.jemaat_data.get('hubungan_keluarga'):
            index = self.hubungan_keluarga.findText(self.jemaat_data['hubungan_keluarga'])
            if index >= 0:
                self.hubungan_keluarga.setCurrentIndex(index)

        self.pendidikan_terakhir = QComboBox()
        self.pendidikan_terakhir.addItems(["Pilih pendidikan terakhir", "SD", "SMP", "SMA", "SMK", "S1", "S2", "S3"])
        self.pendidikan_terakhir.setCurrentIndex(0)
        self.pendidikan_terakhir.setMinimumWidth(300)
        self.setup_placeholder_style(self.pendidikan_terakhir)
        if self.jemaat_data.get('pendidikan_terakhir'):
            index = self.pendidikan_terakhir.findText(self.jemaat_data['pendidikan_terakhir'])
            if index >= 0:
                self.pendidikan_terakhir.setCurrentIndex(index)

        self.status_menikah = QComboBox()
        self.status_menikah.addItems(["Pilih status menikah", "Belum Menikah", "Sudah Menikah", "Duda", "Janda"])
        self.status_menikah.setCurrentIndex(0)
        self.status_menikah.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_menikah)
        # Fixed: use database column name 'status_pernikahan'
        if self.jemaat_data.get('status_pernikahan'):
            index = self.status_menikah.findText(self.jemaat_data['status_pernikahan'])
            if index >= 0:
                self.status_menikah.setCurrentIndex(index)

        # Create detail_pekerjaan_label BEFORE connecting signal
        self.detail_pekerjaan_label = QLabel("Detail Pekerjaan:")

        self.detail_pekerjaan = QLineEdit(self.jemaat_data.get('detail_pekerjaan', ''))
        self.detail_pekerjaan.setMinimumWidth(300)
        self.detail_pekerjaan.setVisible(False)

        self.jenis_pekerjaan = QComboBox()
        self.jenis_pekerjaan.addItems(["Pilih status pekerjaan", "Pelajar", "Bekerja", "Tidak Bekerja"])
        self.jenis_pekerjaan.setCurrentIndex(0)
        self.jenis_pekerjaan.setMinimumWidth(300)
        self.setup_placeholder_style(self.jenis_pekerjaan)
        # Connect signal AFTER all related widgets are created
        self.jenis_pekerjaan.currentTextChanged.connect(self.on_jenis_pekerjaan_changed)  # type: ignore
        if self.jemaat_data.get('jenis_pekerjaan'):
            # Block signals during initialization to prevent premature signal firing
            self.jenis_pekerjaan.blockSignals(True)
            index = self.jenis_pekerjaan.findText(self.jemaat_data['jenis_pekerjaan'])
            if index >= 0:
                self.jenis_pekerjaan.setCurrentIndex(index)
            # Unblock signals after setting value
            self.jenis_pekerjaan.blockSignals(False)

        self.alamat = QLineEdit(self.jemaat_data.get('alamat', ''))
        self.alamat.setMinimumWidth(300)

        self.email = QLineEdit(self.jemaat_data.get('email', ''))
        self.email.setMinimumWidth(300)

        self.no_telepon = QLineEdit(self.jemaat_data.get('no_telepon', ''))
        self.no_telepon.setMinimumWidth(300)
        self.no_telepon.setPlaceholderText("Nomor telepon (opsional)")

        data_pribadi_layout.addRow("Wilayah Rohani:", self.wilayah_rohani)
        data_pribadi_layout.addRow("Nama Keluarga:", self.nama_keluarga)
        data_pribadi_layout.addRow("No. KK:", self.no_kk)
        data_pribadi_layout.addRow("Nama Lengkap:", self.nama_lengkap)
        data_pribadi_layout.addRow("NIK:", self.nik)
        data_pribadi_layout.addRow("Tempat Lahir:", self.tempat_lahir)
        data_pribadi_layout.addRow("Tanggal Lahir:", self.tanggal_lahir)
        data_pribadi_layout.addRow("Umur:", self.umur)
        data_pribadi_layout.addRow("Status Kekatolikan:", self.status_kekatolikan)
        data_pribadi_layout.addRow(self.status_kekatolikan_lainnya_label, self.status_kekatolikan_lainnya)
        data_pribadi_layout.addRow("Kategori:", self.kategori)
        data_pribadi_layout.addRow("Jenis Kelamin:", self.jenis_kelamin)
        data_pribadi_layout.addRow("Hubungan Keluarga:", self.hubungan_keluarga)
        data_pribadi_layout.addRow("Pendidikan Terakhir:", self.pendidikan_terakhir)
        data_pribadi_layout.addRow("Status Menikah:", self.status_menikah)
        data_pribadi_layout.addRow("Status Pekerjaan:", self.jenis_pekerjaan)

        # detail_pekerjaan_label sudah dibuat di atas, tinggal add ke layout
        data_pribadi_layout.addRow(self.detail_pekerjaan_label, self.detail_pekerjaan)
        self.detail_pekerjaan_label.setVisible(False)

        data_pribadi_layout.addRow("Alamat:", self.alamat)
        data_pribadi_layout.addRow("Email:", self.email)
        data_pribadi_layout.addRow("No. Telepon:", self.no_telepon)

        layout.addWidget(data_pribadi_group)

        # Calculate initial age
        self.calculate_age()

    def setup_sakramen_babtis(self, layout):
        """Setup section Sakramen Babtis"""
        from PyQt5.QtWidgets import QGroupBox
        babtis_group = QGroupBox("2. SAKRAMEN BABTIS")
        babtis_layout = QFormLayout(babtis_group)

        self.status_babtis = QComboBox()
        self.status_babtis.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_babtis.setCurrentIndex(0)
        self.status_babtis.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_babtis)
        self.status_babtis.currentTextChanged.connect(self.on_babtis_status_changed)  # type: ignore
        if self.jemaat_data.get('status_babtis'):
            # Block signals during initialization to prevent premature signal firing
            self.status_babtis.blockSignals(True)
            index = self.status_babtis.findText(self.jemaat_data['status_babtis'])
            if index >= 0:
                self.status_babtis.setCurrentIndex(index)
            # Unblock signals after setting value
            self.status_babtis.blockSignals(False)

        self.tempat_babtis = QLineEdit(self.jemaat_data.get('tempat_babtis', ''))
        self.tempat_babtis.setMinimumWidth(300)
        self.tempat_babtis.setVisible(False)

        self.tanggal_babtis = QDateEdit()
        self.tanggal_babtis.setCalendarPopup(True)
        self.tanggal_babtis.setDate(QDate.currentDate())
        self.tanggal_babtis.setMinimumWidth(300)
        self.tanggal_babtis.setVisible(False)
        if self.jemaat_data.get('tanggal_babtis'):
            try:
                date_obj = datetime.strptime(str(self.jemaat_data['tanggal_babtis']), '%Y-%m-%d').date()
                self.tanggal_babtis.setDate(QDate.fromString(date_obj.isoformat(), Qt.DateFormat.ISODate))
            except:
                pass

        self.nama_babtis = QLineEdit(self.jemaat_data.get('nama_babtis', ''))
        self.nama_babtis.setMinimumWidth(300)
        self.nama_babtis.setVisible(False)

        babtis_layout.addRow("Status:", self.status_babtis)
        babtis_layout.addRow("Tempat Babtis:", self.tempat_babtis)
        babtis_layout.addRow("Tanggal Babtis:", self.tanggal_babtis)
        babtis_layout.addRow("Nama Babtis:", self.nama_babtis)

        layout.addWidget(babtis_group)

    def setup_sakramen_ekaristi(self, layout):
        """Setup section Sakramen Ekaristi"""
        from PyQt5.QtWidgets import QGroupBox
        ekaristi_group = QGroupBox("3. SAKRAMEN EKARISTI")
        ekaristi_layout = QFormLayout(ekaristi_group)

        self.status_ekaristi = QComboBox()
        self.status_ekaristi.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_ekaristi.setCurrentIndex(0)
        self.status_ekaristi.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_ekaristi)
        self.status_ekaristi.currentTextChanged.connect(self.on_ekaristi_status_changed)  # type: ignore
        if self.jemaat_data.get('status_ekaristi'):
            # Block signals during initialization to prevent premature signal firing
            self.status_ekaristi.blockSignals(True)
            index = self.status_ekaristi.findText(self.jemaat_data['status_ekaristi'])
            if index >= 0:
                self.status_ekaristi.setCurrentIndex(index)
            # Unblock signals after setting value
            self.status_ekaristi.blockSignals(False)

        self.tempat_komuni = QLineEdit(self.jemaat_data.get('tempat_komuni', ''))
        self.tempat_komuni.setMinimumWidth(300)
        self.tempat_komuni.setVisible(False)

        self.tanggal_komuni = QDateEdit()
        self.tanggal_komuni.setCalendarPopup(True)
        self.tanggal_komuni.setDate(QDate.currentDate())
        self.tanggal_komuni.setMinimumWidth(300)
        self.tanggal_komuni.setVisible(False)
        if self.jemaat_data.get('tanggal_komuni'):
            try:
                date_obj = datetime.strptime(str(self.jemaat_data['tanggal_komuni']), '%Y-%m-%d').date()
                self.tanggal_komuni.setDate(QDate.fromString(date_obj.isoformat(), Qt.DateFormat.ISODate))
            except:
                pass

        ekaristi_layout.addRow("Status:", self.status_ekaristi)
        ekaristi_layout.addRow("Tempat Komuni:", self.tempat_komuni)
        ekaristi_layout.addRow("Tanggal Komuni:", self.tanggal_komuni)

        layout.addWidget(ekaristi_group)

    def setup_sakramen_krisma(self, layout):
        """Setup section Sakramen Krisma"""
        from PyQt5.QtWidgets import QGroupBox
        krisma_group = QGroupBox("4. SAKRAMEN KRISMA")
        krisma_layout = QFormLayout(krisma_group)

        self.status_krisma = QComboBox()
        self.status_krisma.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_krisma.setCurrentIndex(0)
        self.status_krisma.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_krisma)
        self.status_krisma.currentTextChanged.connect(self.on_krisma_status_changed)  # type: ignore
        if self.jemaat_data.get('status_krisma'):
            # Block signals during initialization to prevent premature signal firing
            self.status_krisma.blockSignals(True)
            index = self.status_krisma.findText(self.jemaat_data['status_krisma'])
            if index >= 0:
                self.status_krisma.setCurrentIndex(index)
            # Unblock signals after setting value
            self.status_krisma.blockSignals(False)

        self.tempat_krisma = QLineEdit(self.jemaat_data.get('tempat_krisma', ''))
        self.tempat_krisma.setMinimumWidth(300)
        self.tempat_krisma.setVisible(False)

        self.tanggal_krisma = QDateEdit()
        self.tanggal_krisma.setCalendarPopup(True)
        self.tanggal_krisma.setDate(QDate.currentDate())
        self.tanggal_krisma.setMinimumWidth(300)
        self.tanggal_krisma.setVisible(False)
        if self.jemaat_data.get('tanggal_krisma'):
            try:
                date_obj = datetime.strptime(str(self.jemaat_data['tanggal_krisma']), '%Y-%m-%d').date()
                self.tanggal_krisma.setDate(QDate.fromString(date_obj.isoformat(), Qt.DateFormat.ISODate))
            except:
                pass

        krisma_layout.addRow("Status:", self.status_krisma)
        krisma_layout.addRow("Tempat Krisma:", self.tempat_krisma)
        krisma_layout.addRow("Tanggal Krisma:", self.tanggal_krisma)

        layout.addWidget(krisma_group)

    def setup_sakramen_perkawinan(self, layout):
        """Setup section Sakramen Perkawinan"""
        from PyQt5.QtWidgets import QGroupBox
        perkawinan_group = QGroupBox("5. SAKRAMEN PERKAWINAN")
        perkawinan_layout = QFormLayout(perkawinan_group)

        self.status_perkawinan = QComboBox()
        self.status_perkawinan.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_perkawinan.setCurrentIndex(0)
        self.status_perkawinan.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_perkawinan)
        self.status_perkawinan.currentTextChanged.connect(self.on_perkawinan_status_changed)  # type: ignore
        if self.jemaat_data.get('status_perkawinan'):
            # Block signals during initialization to prevent premature signal firing
            self.status_perkawinan.blockSignals(True)
            index = self.status_perkawinan.findText(self.jemaat_data['status_perkawinan'])
            if index >= 0:
                self.status_perkawinan.setCurrentIndex(index)
            # Unblock signals after setting value
            self.status_perkawinan.blockSignals(False)

        self.keuskupan = QLineEdit(self.jemaat_data.get('keuskupan', ''))
        self.keuskupan.setMinimumWidth(300)
        self.keuskupan.setVisible(False)

        self.paroki = QLineEdit(self.jemaat_data.get('paroki', ''))
        self.paroki.setMinimumWidth(300)
        self.paroki.setVisible(False)

        self.kota_perkawinan = QLineEdit(self.jemaat_data.get('kota_perkawinan', ''))
        self.kota_perkawinan.setMinimumWidth(300)
        self.kota_perkawinan.setVisible(False)

        self.tanggal_perkawinan = QDateEdit()
        self.tanggal_perkawinan.setCalendarPopup(True)
        self.tanggal_perkawinan.setDate(QDate.currentDate())
        self.tanggal_perkawinan.setMinimumWidth(300)
        self.tanggal_perkawinan.setVisible(False)
        if self.jemaat_data.get('tanggal_perkawinan'):
            try:
                date_obj = datetime.strptime(str(self.jemaat_data['tanggal_perkawinan']), '%Y-%m-%d').date()
                self.tanggal_perkawinan.setDate(QDate.fromString(date_obj.isoformat(), Qt.DateFormat.ISODate))
            except:
                pass

        self.status_perkawinan_detail = QComboBox()
        self.status_perkawinan_detail.addItems(["Pilih jenis perkawinan", "Sipil", "Gereja", "Sipil dan Gereja"])
        self.status_perkawinan_detail.setCurrentIndex(0)
        self.status_perkawinan_detail.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_perkawinan_detail)
        self.status_perkawinan_detail.setVisible(False)
        if self.jemaat_data.get('status_perkawinan_detail'):
            index = self.status_perkawinan_detail.findText(self.jemaat_data['status_perkawinan_detail'])
            if index >= 0:
                self.status_perkawinan_detail.setCurrentIndex(index)

        perkawinan_layout.addRow("Status:", self.status_perkawinan)
        perkawinan_layout.addRow("Keuskupan:", self.keuskupan)
        perkawinan_layout.addRow("Paroki:", self.paroki)
        perkawinan_layout.addRow("Kota:", self.kota_perkawinan)
        perkawinan_layout.addRow("Tanggal Perkawinan:", self.tanggal_perkawinan)
        perkawinan_layout.addRow("Jenis Perkawinan:", self.status_perkawinan_detail)

        layout.addWidget(perkawinan_group)

    def setup_status(self, layout):
        """Setup section Status"""
        from PyQt5.QtWidgets import QGroupBox, QLabel
        status_group = QGroupBox("6. STATUS")
        status_layout = QFormLayout(status_group)

        # Store reference to labels for conditional visibility FIRST
        # This ensures they exist before signal handler tries to access them
        self.wilayah_rohani_pindah_label = QLabel("Wilayah Rohani Tujuan:")
        self.wilayah_rohani_pindah = QLineEdit(self.jemaat_data.get('wilayah_rohani_pindah', ''))
        self.wilayah_rohani_pindah.setMinimumWidth(300)

        self.paroki_pindah_label = QLabel("Paroki Tujuan:")
        self.paroki_pindah = QLineEdit(self.jemaat_data.get('paroki_pindah', ''))
        self.paroki_pindah.setMinimumWidth(300)

        self.keuskupan_pindah_label = QLabel("Keuskupan Tujuan:")
        self.keuskupan_pindah = QLineEdit(self.jemaat_data.get('keuskupan_pindah', ''))
        self.keuskupan_pindah.setMinimumWidth(300)

        # Status Keanggotaan dropdown - matching server exactly
        self.status_keanggotaan = QComboBox()
        self.status_keanggotaan.addItems(["Pilih Status", "Menetap", "Pindah", "Meninggal"])
        self.status_keanggotaan.setCurrentIndex(0)
        self.status_keanggotaan.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_keanggotaan)
        # Connect using both currentTextChanged and currentIndexChanged for robustness
        self.status_keanggotaan.currentTextChanged.connect(self.on_status_keanggotaan_changed)  # type: ignore
        self.status_keanggotaan.currentIndexChanged.connect(self._on_status_index_changed)  # type: ignore

        status_layout.addRow("Status Keanggotaan:", self.status_keanggotaan)
        # Don't add conditional rows yet - we'll add them dynamically
        # For now, just store them as hidden widgets

        # Set consistent spacing and alignment
        status_layout.setVerticalSpacing(5)
        status_layout.setHorizontalSpacing(10)
        status_layout.setFieldGrowthPolicy(status_layout.AllNonFixedFieldsGrow)
        status_layout.setLabelAlignment(Qt.AlignLeft)
        status_layout.setRowWrapPolicy(status_layout.DontWrapRows)
        status_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        layout.addWidget(status_group)

        # Store layout reference for visibility toggling
        self.status_layout = status_layout
        # Track which rows are added for conditional fields
        self.conditional_rows_added = False

        # Trigger initial state for status keanggotaan (should be hidden by default)
        self.on_status_keanggotaan_changed(self.status_keanggotaan.currentText())

    def calculate_age(self):
        """Calculate age based on birth date"""
        try:
            birth_date = self.tanggal_lahir.date().toPyDate()
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            self.umur.setText(str(age))
        except:
            self.umur.setText("0")

    def on_status_kekatolikan_changed(self, text):
        """Show/hide status kekatolikan lainnya field based on selection"""
        show_field = text == "Lainnya"
        self.status_kekatolikan_lainnya_label.setVisible(show_field)
        self.status_kekatolikan_lainnya.setVisible(show_field)

    def _get_status_kekatolikan_value(self):
        """Get status kekatolikan value, handling Lainnya case"""
        current_text = self.status_kekatolikan.currentText()

        # If placeholder or empty, return empty string
        if not current_text or current_text == "Pilih Status Kekatolikan":
            return ''

        # If Lainnya, combine with the input field value
        if current_text == "Lainnya":
            lainnya_value = self.status_kekatolikan_lainnya.text().strip()
            if lainnya_value:
                return f"Lainnya: {lainnya_value}"
            return "Lainnya"

        # Return the selected value
        return current_text

    def _on_status_index_changed(self, index):
        """Handler for status keanggotaan index change"""
        if index >= 0:
            text = self.status_keanggotaan.itemText(index)
            self.on_status_keanggotaan_changed(text)

    def on_status_keanggotaan_changed(self, text):
        """Show/hide conditional fields based on status keanggotaan"""
        # Ensure layout exists before trying to modify it
        if not hasattr(self, 'status_layout'):
            return

        visible = (text == "Pindah")
        layout = self.status_layout

        # Check if we need to add the conditional rows for the first time
        if visible and not self.conditional_rows_added:
            # Add conditional rows to layout when "Pindah" is selected
            layout.addRow(self.wilayah_rohani_pindah_label, self.wilayah_rohani_pindah)
            layout.addRow(self.paroki_pindah_label, self.paroki_pindah)
            layout.addRow(self.keuskupan_pindah_label, self.keuskupan_pindah)
            # Ensure they are visible
            self.wilayah_rohani_pindah_label.setVisible(True)
            self.wilayah_rohani_pindah.setVisible(True)
            self.paroki_pindah_label.setVisible(True)
            self.paroki_pindah.setVisible(True)
            self.keuskupan_pindah_label.setVisible(True)
            self.keuskupan_pindah.setVisible(True)
            self.conditional_rows_added = True
        # Remove rows if we should hide them
        elif not visible and self.conditional_rows_added:
            # Remove the rows in reverse order to avoid index shifting
            for row_idx in range(layout.rowCount() - 1, -1, -1):
                label_item = layout.itemAt(row_idx, layout.LabelRole)
                field_item = layout.itemAt(row_idx, layout.FieldRole)
                label_widget = label_item.widget() if label_item else None
                field_widget = field_item.widget() if field_item else None

                # Remove if this is one of our conditional rows
                if field_widget in [self.wilayah_rohani_pindah, self.paroki_pindah, self.keuskupan_pindah]:
                    # Remove all items in this row
                    if label_item:
                        layout.removeItem(label_item)
                    if field_item:
                        layout.removeItem(field_item)
            self.conditional_rows_added = False

    def on_jenis_pekerjaan_changed(self, text):
        """Show/hide detail pekerjaan based on selection"""
        if text == "Bekerja":
            self.detail_pekerjaan_label.setVisible(True)
            self.detail_pekerjaan.setVisible(True)
        else:
            self.detail_pekerjaan_label.setVisible(False)
            self.detail_pekerjaan.setVisible(False)

    def on_babtis_status_changed(self, text):
        """Show/hide babtis fields based on status"""
        show_fields = text == "Sudah"
        self.tempat_babtis.setVisible(show_fields)
        self.tanggal_babtis.setVisible(show_fields)
        self.nama_babtis.setVisible(show_fields)

    def on_ekaristi_status_changed(self, text):
        """Show/hide ekaristi fields based on status"""
        show_fields = text == "Sudah"
        self.tempat_komuni.setVisible(show_fields)
        self.tanggal_komuni.setVisible(show_fields)

    def on_krisma_status_changed(self, text):
        """Show/hide krisma fields based on status"""
        show_fields = text == "Sudah"
        self.tempat_krisma.setVisible(show_fields)
        self.tanggal_krisma.setVisible(show_fields)

    def on_perkawinan_status_changed(self, text):
        """Show/hide perkawinan fields based on status"""
        show_fields = text == "Sudah"
        self.keuskupan.setVisible(show_fields)
        self.paroki.setVisible(show_fields)
        self.kota_perkawinan.setVisible(show_fields)
        self.tanggal_perkawinan.setVisible(show_fields)
        self.status_perkawinan_detail.setVisible(show_fields)

    def get_data(self):
        """Extract all form data - ensures all fields are captured including conditional ones"""
        # Helper function to safely get combo box value
        def get_combo_value(combo, skip_index_0=True, allow_placeholder=False):
            """Get combo box value, optionally skip index 0 (placeholder)"""
            if skip_index_0 and combo.currentIndex() <= 0:
                return ''
            text = combo.currentText()
            # Filter out common placeholder texts only if not allowing placeholders
            if not allow_placeholder and text in ['Pilih', 'Pilih Kategori', 'Pilih jenis kelamin', 'Pilih hubungan dalam keluarga',
                       'Pilih pendidikan terakhir', 'Pilih status menikah', 'Pilih status pekerjaan',
                       'Pilih status', 'Pilih Wilayah Rohani', 'Pilih Status']:
                return ''
            return text

        # Helper function to safely get date value
        def get_date_value(date_edit, allow_null=True):
            """Get date value in ISO format, optionally allow null"""
            try:
                date_obj = date_edit.date()
                if not date_obj.isValid():
                    return None if allow_null else ''
                date_str = date_obj.toString(Qt.DateFormat.ISODate)
                # Check if it's a default/placeholder date
                if date_str in ['1900-01-01', '']:
                    return None if allow_null else ''
                return date_str
            except:
                return None if allow_null else ''

        # Capture ALL form data regardless of visibility
        data = {
            # Data Pribadi
            'wilayah_rohani': get_combo_value(self.wilayah_rohani),
            'nama_keluarga': self.nama_keluarga.text().strip(),
            'no_kk': self.no_kk.text().strip(),
            'nama_lengkap': self.nama_lengkap.text().strip(),
            'nik': self.nik.text().strip(),
            'tempat_lahir': self.tempat_lahir.text().strip(),
            'tanggal_lahir': get_date_value(self.tanggal_lahir, allow_null=True),
            'umur': self.umur.text().strip(),
            'status_kekatolikan': self._get_status_kekatolikan_value(),
            'kategori': get_combo_value(self.kategori),
            'jenis_kelamin': get_combo_value(self.jenis_kelamin),
            'hubungan_keluarga': get_combo_value(self.hubungan_keluarga),
            'pendidikan_terakhir': get_combo_value(self.pendidikan_terakhir),
            'status_menikah': get_combo_value(self.status_menikah),
            'jenis_pekerjaan': get_combo_value(self.jenis_pekerjaan),
            'detail_pekerjaan': self.detail_pekerjaan.text().strip(),
            'no_telepon': self.no_telepon.text().strip(),
            'alamat': self.alamat.text().strip(),
            'email': self.email.text().strip(),

            # Sakramen Babtis
            'status_babtis': get_combo_value(self.status_babtis),
            'tempat_babtis': self.tempat_babtis.text().strip(),  # Always capture, regardless of visibility
            'tanggal_babtis': get_date_value(self.tanggal_babtis),  # Always capture
            'nama_babtis': self.nama_babtis.text().strip(),  # Always capture

            # Sakramen Ekaristi
            'status_ekaristi': get_combo_value(self.status_ekaristi),
            'tempat_komuni': self.tempat_komuni.text().strip(),  # Always capture
            'tanggal_komuni': get_date_value(self.tanggal_komuni),  # Always capture

            # Sakramen Krisma
            'status_krisma': get_combo_value(self.status_krisma),
            'tempat_krisma': self.tempat_krisma.text().strip(),  # Always capture
            'tanggal_krisma': get_date_value(self.tanggal_krisma),  # Always capture

            # Sakramen Perkawinan
            'status_perkawinan': get_combo_value(self.status_perkawinan),
            'keuskupan': self.keuskupan.text().strip(),  # Always capture
            'paroki': self.paroki.text().strip(),  # Always capture
            'kota_perkawinan': self.kota_perkawinan.text().strip(),  # Always capture
            'tanggal_perkawinan': get_date_value(self.tanggal_perkawinan),  # Always capture
            'status_perkawinan_detail': get_combo_value(self.status_perkawinan_detail),  # Always capture

            # Status Keanggotaan
            'status_keanggotaan': get_combo_value(self.status_keanggotaan, skip_index_0=False, allow_placeholder=True),
            'wilayah_rohani_pindah': self.wilayah_rohani_pindah.text().strip(),
            'paroki_pindah': self.paroki_pindah.text().strip(),
            'keuskupan_pindah': self.keuskupan_pindah.text().strip()
        }

        return data

class JemaatViewDialog(QDialog):
    """Read-only dialog to view jemaat details"""

    def __init__(self, parent=None, jemaat_data=None):
        super().__init__(parent)
        self.jemaat_data = jemaat_data if jemaat_data else {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Detail Data Jemaat")
        self.setModal(True)
        self.resize(700, 600)

        layout = QVBoxLayout(self)

        # Header with name
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #3498db; color: white; padding: 15px; border-radius: 8px;")
        header_layout = QVBoxLayout(header_frame)

        name_label = QLabel(self.jemaat_data.get('nama_lengkap', 'Nama Tidak Tersedia'))
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        status_label = QLabel(f"Status: {self.jemaat_data.get('status', 'Unknown')}")
        status_label.setStyleSheet("font-size: 12px; color: #ecf0f1;")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(name_label)
        header_layout.addWidget(status_label)

        layout.addWidget(header_frame)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Data Pribadi
        self.add_data_section(scroll_layout, "DATA PRIBADI", [
            ("Wilayah Rohani", self.jemaat_data.get('wilayah_rohani', 'N/A')),
            ("Nama Keluarga", self.jemaat_data.get('nama_keluarga', 'N/A')),
            ("Nama Lengkap", self.jemaat_data.get('nama_lengkap', 'N/A')),
            ("Tempat Lahir", self.jemaat_data.get('tempat_lahir', 'N/A')),
            ("Tanggal Lahir", self.format_date(self.jemaat_data.get('tanggal_lahir', ''))),
            ("Umur", f"{self.jemaat_data.get('umur', 'N/A')} tahun"),
            ("Kategori", self.jemaat_data.get('kategori', 'N/A')),
            ("Jenis Kelamin", self.jemaat_data.get('jenis_kelamin', 'N/A')),
            ("Hubungan Keluarga", self.jemaat_data.get('hubungan_keluarga', 'N/A')),
            ("Pendidikan Terakhir", self.jemaat_data.get('pendidikan_terakhir', 'N/A')),
            ("Status Menikah", self.jemaat_data.get('status_pernikahan', 'N/A')),  # Fixed: use database column
            ("Pekerjaan", self.jemaat_data.get('jenis_pekerjaan', 'N/A')),
            ("Detail Pekerjaan", self.jemaat_data.get('detail_pekerjaan', 'N/A')),
            ("Alamat", self.jemaat_data.get('alamat', 'N/A')),
            ("Email", self.jemaat_data.get('email', 'N/A'))
        ])

        # Sakramen Babtis
        if self.jemaat_data.get('status_babtis') == 'Sudah':
            self.add_data_section(scroll_layout, "SAKRAMEN BABTIS", [
                ("Status", self.jemaat_data.get('status_babtis', 'N/A')),
                ("Tempat Babtis", self.jemaat_data.get('tempat_babtis', 'N/A')),
                ("Tanggal Babtis", self.format_date(self.jemaat_data.get('tanggal_babtis', ''))),
                ("Nama Babtis", self.jemaat_data.get('nama_babtis', 'N/A'))
            ])

        # Sakramen Ekaristi
        if self.jemaat_data.get('status_ekaristi') == 'Sudah':
            self.add_data_section(scroll_layout, "SAKRAMEN EKARISTI", [
                ("Status", self.jemaat_data.get('status_ekaristi', 'N/A')),
                ("Tempat Komuni", self.jemaat_data.get('tempat_komuni', 'N/A')),
                ("Tanggal Komuni", self.format_date(self.jemaat_data.get('tanggal_komuni', '')))
            ])

        # Sakramen Krisma
        if self.jemaat_data.get('status_krisma') == 'Sudah':
            self.add_data_section(scroll_layout, "SAKRAMEN KRISMA", [
                ("Status", self.jemaat_data.get('status_krisma', 'N/A')),
                ("Tempat Krisma", self.jemaat_data.get('tempat_krisma', 'N/A')),
                ("Tanggal Krisma", self.format_date(self.jemaat_data.get('tanggal_krisma', '')))
            ])

        # Sakramen Perkawinan
        if self.jemaat_data.get('status_perkawinan') == 'Sudah':
            self.add_data_section(scroll_layout, "SAKRAMEN PERKAWINAN", [
                ("Status", self.jemaat_data.get('status_perkawinan', 'N/A')),
                ("Keuskupan", self.jemaat_data.get('keuskupan', 'N/A')),
                ("Paroki", self.jemaat_data.get('paroki', 'N/A')),
                ("Kota", self.jemaat_data.get('kota_perkawinan', 'N/A')),
                ("Tanggal Perkawinan", self.format_date(self.jemaat_data.get('tanggal_perkawinan', '')))
            ])

        # Status
        self.add_data_section(scroll_layout, "STATUS KEANGGOTAAN", [
            ("Status Keanggotaan", self.jemaat_data.get('status_keanggotaan', 'N/A')),
            ("WR Tujuan", self.jemaat_data.get('wr_tujuan', 'N/A')),
            ("Paroki Tujuan", self.jemaat_data.get('paroki_tujuan', 'N/A'))
        ])

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Close button
        close_button = QPushButton("Tutup")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_button.clicked.connect(self.close)  # type: ignore

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def add_data_section(self, layout, title, data_list):
        """Add a data section with title and key-value pairs"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

        form_layout = QFormLayout(group)
        form_layout.setVerticalSpacing(4)  # Reduce vertical spacing between rows
        form_layout.setContentsMargins(8, 5, 8, 5)  # Reduce margins around the form

        for label_text, value in data_list:
            if value and value != 'N/A':
                value_label = QLabel(str(value))
                value_label.setStyleSheet("padding: 1px; font-weight: normal; margin: 0px;")
                value_label.setWordWrap(True)
                form_layout.addRow(f"{label_text}:", value_label)

        layout.addWidget(group)

    def format_date(self, date_str):
        """Format date string for display"""
        if not date_str or date_str == 'N/A':
            return 'N/A'
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%d/%m/%Y')
        except:
            return str(date_str)

class JemaatClientComponent(QWidget):

    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.jemaat_data = []
        self.filtered_data = []
        self.current_user = None

        self.setup_ui()

    def mousePressEvent(self, event):
        """Handle mouse press to clear table selection when clicking outside"""
        # Check if click is outside table widget
        if not self.table_widget.geometry().contains(event.pos()):
            self.table_widget.clearSelection()
            # Reset to NoSelection mode to prevent accidental selection
            self.table_widget.setSelectionMode(QTableWidget.NoSelection)
        super().mousePressEvent(event)

    def on_table_double_clicked(self, index):
        """Handle double click on table to select row"""
        if index.isValid():
            # Temporarily enable selection to select the row
            self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
            self.table_widget.selectRow(index.row())

    def on_vertical_header_clicked(self, row):
        """Handle click on vertical header (row number) to select row"""
        # Temporarily enable selection to select the row
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        self.table_widget.selectRow(row)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title section with professional styling
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 2px solid #ecf0f1;
                padding: 10px 0px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("Database Umat")
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
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addWidget(title_frame)

        # Toolbar dengan search dan tombol aksi
        toolbar_layout = QHBoxLayout()

        # Search
        search_label = QLabel("Cari:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama jemaat...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.filter_data)  # type: ignore

        # Filter Wilayah Rohani
        wilayah_label = QLabel("Filter Wilayah:")
        self.filter_wilayah = QComboBox()
        wilayah_list = [
            "Semua",
            "ST. YOHANES BAPTISTA DE LA SALLE",
            "ST. ALOYSIUS GONZAGA",
            "ST. GREGORIUS AGUNG",
            "ST. DOMINICO SAVIO",
            "ST. THOMAS AQUINAS",
            "ST. ALBERTUS AGUNG",
            "ST. BONAVENTURA",
            "STA. KATARINA DARI SIENA",
            "STA. SISILIA",
            "ST. BLASIUS",
            "ST. CAROLUS BORROMEUS",
            "ST. BONIFASIUS",
            "ST. CORNELIUS",
            "STA. BRIGITTA",
            "ST. IGNASIUS DARI LOYOLA",
            "ST. PIUS X",
            "STA. AGNES",
            "ST. AGUSTINUS",
            "STA. FAUSTINA",
            "ST. YOHANES MARIA VIANNEY",
            "STA. MARIA GORETTI",
            "STA. PERPETUA",
            "ST. LUKAS",
            "STA. SKOLASTIKA",
            "STA. THERESIA DARI AVILLA",
            "ST. VINCENTIUS A PAULO"
        ]
        self.filter_wilayah.addItems(wilayah_list)
        self.filter_wilayah.setFixedWidth(180)
        self.filter_wilayah.currentTextChanged.connect(self.filter_data)  # type: ignore

        # Filter Kategori
        kategori_label = QLabel("Filter Kategori:")
        self.filter_kategori = QComboBox()
        self.filter_kategori.addItems(["Semua", "Balita", "Anak-anak", "Remaja", "OMK", "KBK", "KIK", "Lansia"])
        self.filter_kategori.setFixedWidth(140)
        self.filter_kategori.currentTextChanged.connect(self.filter_data)  # type: ignore

        # Filter by status
        status_label = QLabel("Status:")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Semua", "Menetap", "Pindah", "Meninggal"])
        self.status_filter.currentTextChanged.connect(self.filter_data)  # type: ignore

        toolbar_layout.addWidget(search_label)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(wilayah_label)
        toolbar_layout.addWidget(self.filter_wilayah)
        toolbar_layout.addWidget(kategori_label)
        toolbar_layout.addWidget(self.filter_kategori)
        toolbar_layout.addWidget(status_label)
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addStretch()

        layout.addLayout(toolbar_layout)

        # Table dengan 38 kolom (tanpa No column) menggunakan header dengan word wrap - sesuai server dengan No. KK dan NIK
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(38)
        self.table_widget.setRowCount(0)

        # Gunakan header kustom agar tampilan sama dengan struktur.py
        custom_header = WordWrapHeaderView(Qt.Horizontal, self.table_widget)
        self.table_widget.setHorizontalHeader(custom_header)

        # Setup headers dengan nama kolom
        self.setup_table_headers()

        # Apply professional table styling
        self.apply_professional_table_style()

        # Setup column widths
        self.setup_column_widths()

        # Enable header features
        header = self.table_widget.horizontalHeader()
        header.setVisible(True)
        header.setSectionResizeMode(QHeaderView.Interactive)  # Enable drag to resize
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionsMovable(False)  # Disable column reordering
        header.sectionResized.connect(self.update_header_height)  # type: ignore

        # Freeze header (stays visible when scrolling)
        self.table_widget.horizontalHeader().setFixedHeight(25)
        QTimer.singleShot(100, lambda: self.update_header_height(0, 0, 0))

        # Vertical header settings
        self.table_widget.verticalHeader().setVisible(True)
        self.table_widget.verticalHeader().setDefaultSectionSize(20)

        # Table behavior settings
        self.table_widget.setAlternatingRowColors(False)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.NoSelection)  # Disable default selection
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only

        # Connect double click and vertical header click for selection
        self.table_widget.doubleClicked.connect(self.on_table_double_clicked)  # type: ignore
        self.table_widget.verticalHeader().sectionClicked.connect(self.on_vertical_header_clicked)  # type: ignore

        # Enable sorting
        self.table_widget.setSortingEnabled(True)

        # Add button above table on the right side
        add_button_layout = QHBoxLayout()
        add_button_layout.addStretch()

        add_button = self.create_professional_button("add.png", "Tambah Umat", "#27ae60", "#2ecc71")
        add_button.clicked.connect(self.add_jemaat)  # type: ignore
        add_button_layout.addWidget(add_button)
        add_button_layout.setContentsMargins(0, 5, 0, 5)  # Add vertical spacing

        layout.addLayout(add_button_layout)

        layout.addWidget(self.table_widget)

        # Action buttons in a row from the right side
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)  # Set consistent spacing between buttons
        buttons_layout.addStretch()

        # View button
        view_button = self.create_professional_button("view.png", "Lihat Detail", "#3498db", "#2980b9")
        view_button.clicked.connect(self.view_jemaat)  # type: ignore

        # Edit button
        edit_button = self.create_professional_button("edit.png", "Edit Data", "#f39c12", "#e67e22")
        edit_button.clicked.connect(self.edit_jemaat)  # type: ignore

        # Export button
        export_button = self.create_professional_button("export.png", "Export Data", "#9b59b6", "#8e44ad")
        export_button.clicked.connect(self.export_jemaat)  # type: ignore

        # Delete button
        delete_button = self.create_professional_button("delete.png", "Hapus Data", "#e74c3c", "#c0392b")
        delete_button.clicked.connect(self.delete_jemaat)  # type: ignore

        buttons_layout.addWidget(view_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(export_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()  # Add stretch at the end for better centering

        layout.addLayout(buttons_layout)

        # Statistics
        self.stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total: 0 jemaat")
        self.active_label = QLabel("Menetap: 0")
        self.inactive_label = QLabel("Pindah: 0")

        self.stats_layout.addWidget(self.total_label)
        self.stats_layout.addWidget(self.active_label)
        self.stats_layout.addWidget(self.inactive_label)
        self.stats_layout.addStretch()

        layout.addLayout(self.stats_layout)

    def create_professional_button(self, icon_name, text, bg_color, hover_color):
        """Create a professional button with icon and text"""
        button = QPushButton(f" {text}")  # Add space before text for icon spacing
        button.setMinimumSize(100, 28)
        button.setMaximumSize(130, 28)

        # Add icon if available
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', icon_name)
        if os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(16, 16))  # Slightly larger icon
            except Exception:
                pass  # Continue without icon if loading fails

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: 1px solid {bg_color};
                border-radius: 4px;
                padding: 4px 8px 4px 4px;
                font-size: 11px;
                font-weight: 500;
                text-align: left;
                padding-left: 6px;
                margin: 1px 3px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border-color: {hover_color};
                box-shadow: 0 2px 4px rgba(0,0,0,0.15);
            }}
            QPushButton:pressed {{
                background-color: {bg_color};
                border-color: {bg_color};
                box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
            }}
            QPushButton::tooltip {{
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                border: none;
                padding: 3px 6px;
                border-radius: 3px;
                font-size: 10px;
                margin: 0px;
            }}
        """)

        return button

    def setup_table_headers(self):
        """Setup header kolom tanpa No column - sesuai server (38 kolom data) dengan No. KK dan NIK"""
        headers = [
            # DATA PRIBADI (0-17) - added No. KK and NIK
            "Wilayah Rohani", "Nama Keluarga", "No. KK", "Nama Lengkap", "NIK", "Tempat Lahir",
            "Tanggal Lahir", "Umur", "Status Kekatolikan", "Kategori", "J. Kelamin",
            "Hubungan Keluarga", "Pend. Terakhir", "Status Menikah", "Status Pekerjaan",
            "Detail Pekerjaan", "Alamat", "Email/No.Hp",
            # SAKRAMEN BABTIS (18-21)
            "Status Babtis", "Tempat Babtis", "Tanggal Babtis", "Nama Babtis",
            # SAKRAMEN EKARISTI (22-24)
            "Status Ekaristi", "Tempat Komuni", "Tanggal Komuni",
            # SAKRAMEN KRISMA (25-27)
            "Status Krisma", "Tempat Krisma", "Tanggal Krisma",
            # SAKRAMEN PERKAWINAN (28-33)
            "Status Perkawinan", "Keuskupan", "Paroki", "Kota", "Tgl Perkawinan", "Status Perkawinan Detail",
            # STATUS (34-37) - TOTAL 38 COLUMNS
            "Status Keanggotaan", "WR Tujuan", "Paroki Tujuan", "Created By Pengguna"
        ]

        self.table_widget.setHorizontalHeaderLabels(headers)

    def setup_column_widths(self):
        """Set up column widths for better display (without No column - 38 columns total with No. KK and NIK)"""
        # DATA PRIBADI columns (0-17) - added No. KK and NIK
        self.table_widget.setColumnWidth(0, 110)  # Wilayah Rohani
        self.table_widget.setColumnWidth(1, 120)  # Nama Keluarga
        self.table_widget.setColumnWidth(2, 110)  # No. KK
        self.table_widget.setColumnWidth(3, 150)  # Nama Lengkap - wider
        self.table_widget.setColumnWidth(4, 110)  # NIK
        self.table_widget.setColumnWidth(5, 110)  # Tempat Lahir
        self.table_widget.setColumnWidth(6, 100)  # Tanggal Lahir
        self.table_widget.setColumnWidth(7, 60)   # Umur
        self.table_widget.setColumnWidth(8, 110)  # Status Kekatolikan
        self.table_widget.setColumnWidth(9, 90)   # Kategori
        self.table_widget.setColumnWidth(10, 80)  # J. Kelamin
        self.table_widget.setColumnWidth(11, 120) # Hubungan Keluarga
        self.table_widget.setColumnWidth(12, 110) # Pend. Terakhir
        self.table_widget.setColumnWidth(13, 110) # Status Menikah
        self.table_widget.setColumnWidth(14, 110) # Status Pekerjaan
        self.table_widget.setColumnWidth(15, 120) # Detail Pekerjaan
        self.table_widget.setColumnWidth(16, 180) # Alamat - wider
        self.table_widget.setColumnWidth(17, 130) # Email/No.Hp

        # Sakramen columns (18-33)
        for i in range(18, 34):
            self.table_widget.setColumnWidth(i, 100)

        # Status columns (34-37) - TOTAL 38 COLUMNS
        for i in range(34, 38):
            self.table_widget.setColumnWidth(i, 120)

    def update_header_height(self, logical_index, old_size, new_size):
        """Update header height based on wrapped text similar to struktur table"""
        if not hasattr(self, "table_widget"):
            return

        header = self.table_widget.horizontalHeader()
        header.setMinimumHeight(25)
        max_height = 25

        for index in range(header.count()):
            size = header.sectionSizeFromContents(index)
            max_height = max(max_height, size.height())

        header.setFixedHeight(max_height)

    def apply_professional_table_style(self):
        """Apply professional table styling matching struktur component"""
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)
        self.table_widget.horizontalHeader().setFont(header_font)

        self.table_widget.horizontalHeader().setStyleSheet("""
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

        header = self.table_widget.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        header.setMinimumHeight(25)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(500)

        self.table_widget.setStyleSheet("""
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

        self.table_widget.verticalHeader().setStyleSheet("""
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

        self.table_widget.setShowGrid(True)
        self.table_widget.setGridStyle(Qt.SolidLine)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.setAlternatingRowColors(False)
        self.table_widget.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    def get_user_data_file(self):
        """Get user-specific data file path"""
        if not self.current_user:
            # Get current user from api_client if available
            if hasattr(self.api_client, 'current_user') and self.api_client.current_user:
                self.current_user = self.api_client.current_user.get('username', 'unknown')
            else:
                self.current_user = 'unknown'

        # Create user data directory if not exists
        user_data_dir = os.path.join(os.path.dirname(__file__), '..', 'user_data')
        os.makedirs(user_data_dir, exist_ok=True)

        return os.path.join(user_data_dir, f'jemaat_{self.current_user}.json')

    def save_user_jemaat_data(self):
        """Save user-specific jemaat data to local file"""
        try:
            data_file = self.get_user_data_file()
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.jemaat_data, f, ensure_ascii=False, indent=2)
            self.log_message.emit(f"Data jemaat user {self.current_user} berhasil disimpan")  # type: ignore
        except Exception as e:
            self.log_message.emit(f"Error saving user jemaat data: {str(e)}")  # type: ignore

    def load_user_jemaat_data(self):
        """Load jemaat data from API"""
        try:
            result = self.api_client.get_jemaat()
            if result.get('success'):
                response_data = result.get('data', {})
                if response_data.get('status') == 'success':
                    self.jemaat_data = response_data.get('data', [])
                else:
                    self.jemaat_data = []
                    self.log_message.emit(f"API error: {response_data.get('message', 'Unknown error')}")  # type: ignore
            else:
                self.jemaat_data = []
                self.log_message.emit(f"Failed to connect to API: {result.get('data', 'Unknown error')}")  # type: ignore

            self.filtered_data = self.jemaat_data.copy()
            self.update_table()
            self.update_statistics()
            self.log_message.emit(f"Data jemaat berhasil dimuat dari API: {len(self.jemaat_data)} record")  # type: ignore

        except Exception as e:
            self.jemaat_data = []
            self.filtered_data = []
            self.update_table()
            self.log_message.emit(f"Error loading jemaat data from API: {str(e)}")  # type: ignore

    def add_jemaat(self):
        """Add new jemaat (Tambah Umat)"""
        try:
            dialog = JemaatDialog(self)

            # Check if dialog was accepted using QDialog.Accepted constant
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()

                # Validate required fields
                nama_lengkap = data.get('nama_lengkap', '').strip() if data.get('nama_lengkap') else ''
                if not nama_lengkap:
                    QMessageBox.warning(self, "Validasi", "Nama Lengkap harus diisi")
                    return

                jenis_kelamin = data.get('jenis_kelamin', '')
                if not jenis_kelamin:
                    QMessageBox.warning(self, "Validasi", "Jenis Kelamin harus dipilih")
                    return

                # Send ALL data from dialog to API - do not filter
                # The API/database will handle which fields to store
                full_data = {
                    # Data Pribadi
                    'wilayah_rohani': data.get('wilayah_rohani', ''),
                    'nama_keluarga': data.get('nama_keluarga', ''),
                    'no_kk': data.get('no_kk', ''),
                    'nama_lengkap': data.get('nama_lengkap', ''),
                    'nik': data.get('nik', ''),
                    'tempat_lahir': data.get('tempat_lahir', ''),
                    'tanggal_lahir': data.get('tanggal_lahir', ''),
                    'umur': data.get('umur', ''),
                    'status_kekatolikan': data.get('status_kekatolikan', ''),
                    'kategori': data.get('kategori', ''),
                    'jenis_kelamin': 'Laki-laki' if data.get('jenis_kelamin') == 'L' else 'Perempuan',
                    'hubungan_keluarga': data.get('hubungan_keluarga', ''),
                    'pendidikan_terakhir': data.get('pendidikan_terakhir', ''),
                    'status_menikah': data.get('status_menikah', ''),
                    'jenis_pekerjaan': data.get('jenis_pekerjaan', ''),
                    'detail_pekerjaan': data.get('detail_pekerjaan', ''),
                    'alamat': data.get('alamat', ''),
                    'email': data.get('email', ''),
                    'no_telepon': data.get('no_telepon', ''),

                    # Sakramen Babtis
                    'status_babtis': data.get('status_babtis', ''),
                    'tempat_babtis': data.get('tempat_babtis', ''),
                    'tanggal_babtis': data.get('tanggal_babtis', ''),
                    'nama_babtis': data.get('nama_babtis', ''),

                    # Sakramen Ekaristi
                    'status_ekaristi': data.get('status_ekaristi', ''),
                    'tempat_komuni': data.get('tempat_komuni', ''),
                    'tanggal_komuni': data.get('tanggal_komuni', ''),

                    # Sakramen Krisma
                    'status_krisma': data.get('status_krisma', ''),
                    'tempat_krisma': data.get('tempat_krisma', ''),
                    'tanggal_krisma': data.get('tanggal_krisma', ''),

                    # Sakramen Perkawinan
                    'status_perkawinan': data.get('status_perkawinan', ''),
                    'keuskupan': data.get('keuskupan', ''),
                    'paroki': data.get('paroki', ''),
                    'kota_perkawinan': data.get('kota_perkawinan', ''),
                    'tanggal_perkawinan': data.get('tanggal_perkawinan', ''),
                    'status_perkawinan_detail': data.get('status_perkawinan_detail', ''),

                    # Status Keanggotaan
                    'status_keanggotaan': data.get('status_keanggotaan', ''),
                    'wilayah_rohani_pindah': data.get('wilayah_rohani_pindah', ''),
                    'paroki_pindah': data.get('paroki_pindah', ''),
                    'keuskupan_pindah': data.get('keuskupan_pindah', '')
                }

                result = self.api_client.add_jemaat(full_data)
                if result.get('success'):
                    response_data = result.get('data', {})
                    if response_data.get('status') == 'success':
                        self.load_user_jemaat_data()
                        QMessageBox.information(self, "Sukses", "Data umat baru berhasil ditambahkan")
                        self.log_message.emit("Data umat baru berhasil ditambahkan")  # type: ignore
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        QMessageBox.warning(self, "Error", f"Gagal menambah umat: {error_msg}")
                        self.log_message.emit(f"Error adding umat: {error_msg}")  # type: ignore
                else:
                    error_msg = result.get('data', 'Unknown error')
                    QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {error_msg}")
                    self.log_message.emit(f"API connection error: {error_msg}")  # type: ignore
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saat tambah jemaat: {str(e)}")
            self.log_message.emit(f"Exception adding jemaat: {str(e)}")  # type: ignore

    def edit_jemaat(self):
        """Edit selected jemaat"""
        try:
            current_row = self.table_widget.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Warning", "Pilih data jemaat yang akan diedit")
                return

            # Get data dari item yang disimpan, bukan dari filtered_data index
            item = self.table_widget.item(current_row, 0)
            if not item:
                QMessageBox.warning(self, "Warning", "Pilih data jemaat yang akan diedit")
                return

            selected_data = item.data(Qt.UserRole)
            if not selected_data:
                QMessageBox.warning(self, "Warning", "Data tidak ditemukan")
                return

            dialog = JemaatDialog(self, selected_data)

            # Use QDialog.Accepted (class constant) not dialog.Accepted (instance attribute)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()

                # Validate required fields
                nama_lengkap = data.get('nama_lengkap', '').strip() if data.get('nama_lengkap') else ''
                if not nama_lengkap:
                    QMessageBox.warning(self, "Error", "Nama lengkap harus diisi")
                    return

                jenis_kelamin = data.get('jenis_kelamin', '')
                if not jenis_kelamin:
                    QMessageBox.warning(self, "Error", "Jenis kelamin harus dipilih")
                    return

                jemaat_id = selected_data.get('id_jemaat') or selected_data.get('id')

                if not jemaat_id:
                    QMessageBox.warning(self, "Error", "ID jemaat tidak ditemukan")
                    return

                # Send ALL data from dialog to API - do not filter
                # The API/database will handle which fields to store
                full_data = {
                    # Data Pribadi
                    'wilayah_rohani': data.get('wilayah_rohani', ''),
                    'nama_keluarga': data.get('nama_keluarga', ''),
                    'no_kk': data.get('no_kk', ''),
                    'nama_lengkap': data.get('nama_lengkap', ''),
                    'nik': data.get('nik', ''),
                    'tempat_lahir': data.get('tempat_lahir', ''),
                    'tanggal_lahir': data.get('tanggal_lahir', ''),
                    'umur': data.get('umur', ''),
                    'status_kekatolikan': data.get('status_kekatolikan', ''),
                    'kategori': data.get('kategori', ''),
                    'jenis_kelamin': 'Laki-laki' if data.get('jenis_kelamin') == 'L' else 'Perempuan',
                    'hubungan_keluarga': data.get('hubungan_keluarga', ''),
                    'pendidikan_terakhir': data.get('pendidikan_terakhir', ''),
                    'status_menikah': data.get('status_menikah', ''),
                    'jenis_pekerjaan': data.get('jenis_pekerjaan', ''),
                    'detail_pekerjaan': data.get('detail_pekerjaan', ''),
                    'alamat': data.get('alamat', ''),
                    'email': data.get('email', ''),
                    'no_telepon': data.get('no_telepon', ''),

                    # Sakramen Babtis
                    'status_babtis': data.get('status_babtis', ''),
                    'tempat_babtis': data.get('tempat_babtis', ''),
                    'tanggal_babtis': data.get('tanggal_babtis', ''),
                    'nama_babtis': data.get('nama_babtis', ''),

                    # Sakramen Ekaristi
                    'status_ekaristi': data.get('status_ekaristi', ''),
                    'tempat_komuni': data.get('tempat_komuni', ''),
                    'tanggal_komuni': data.get('tanggal_komuni', ''),

                    # Sakramen Krisma
                    'status_krisma': data.get('status_krisma', ''),
                    'tempat_krisma': data.get('tempat_krisma', ''),
                    'tanggal_krisma': data.get('tanggal_krisma', ''),

                    # Sakramen Perkawinan
                    'status_perkawinan': data.get('status_perkawinan', ''),
                    'keuskupan': data.get('keuskupan', ''),
                    'paroki': data.get('paroki', ''),
                    'kota_perkawinan': data.get('kota_perkawinan', ''),
                    'tanggal_perkawinan': data.get('tanggal_perkawinan', ''),
                    'status_perkawinan_detail': data.get('status_perkawinan_detail', ''),

                    # Status Keanggotaan
                    'status_keanggotaan': data.get('status_keanggotaan', ''),
                    'wilayah_rohani_pindah': data.get('wilayah_rohani_pindah', ''),
                    'paroki_pindah': data.get('paroki_pindah', ''),
                    'keuskupan_pindah': data.get('keuskupan_pindah', '')
                }

                result = self.api_client.update_jemaat(jemaat_id, full_data)
                if result.get('success'):
                    response_data = result.get('data', {})
                    if response_data.get('status') == 'success':
                        self.load_user_jemaat_data()  # Refresh data from API
                        QMessageBox.information(self, "Sukses", "Data jemaat berhasil diperbarui")
                        self.log_message.emit("Data jemaat berhasil diperbarui")  # type: ignore
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        QMessageBox.warning(self, "Error", f"Gagal update jemaat: {error_msg}")
                        self.log_message.emit(f"Error updating jemaat: {error_msg}")  # type: ignore
                else:
                    error_msg = result.get('data', 'Unknown error')
                    QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {error_msg}")
                    self.log_message.emit(f"API connection error: {error_msg}")  # type: ignore
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saat edit jemaat: {str(e)}")
            self.log_message.emit(f"Exception editing jemaat: {str(e)}")  # type: ignore

    def delete_jemaat(self):
        """Delete selected jemaat"""
        try:
            current_row = self.table_widget.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Warning", "Pilih data jemaat yang akan dihapus")
                return

            # Get data dari item yang disimpan, bukan dari filtered_data index
            item = self.table_widget.item(current_row, 0)
            if not item:
                QMessageBox.warning(self, "Warning", "Pilih data jemaat yang akan dihapus")
                return

            selected_data = item.data(Qt.UserRole)
            if not selected_data:
                QMessageBox.warning(self, "Warning", "Data tidak ditemukan")
                return

            jemaat_name = selected_data.get('nama_lengkap', 'Unknown')

            reply = QMessageBox.question(self, "Konfirmasi Penghapusan",
                                       f"Apakah Anda yakin ingin menghapus data jemaat '{jemaat_name}'?",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

            if reply == QMessageBox.Yes:
                jemaat_id = selected_data.get('id_jemaat') or selected_data.get('id')

                if not jemaat_id:
                    QMessageBox.warning(self, "Error", "ID jemaat tidak ditemukan")
                    return

                result = self.api_client.delete_jemaat(jemaat_id)
                if result.get('success'):
                    response_data = result.get('data', {})
                    if response_data.get('status') == 'success':
                        self.load_user_jemaat_data()  # Refresh data from API
                        QMessageBox.information(self, "Sukses", f"Data jemaat '{jemaat_name}' berhasil dihapus")
                        self.log_message.emit(f"Data jemaat berhasil dihapus: {jemaat_name}")  # type: ignore
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        QMessageBox.warning(self, "Error", f"Gagal hapus jemaat: {error_msg}")
                        self.log_message.emit(f"Error deleting jemaat: {error_msg}")  # type: ignore
                else:
                    error_msg = result.get('data', 'Unknown error')
                    QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {error_msg}")
                    self.log_message.emit(f"API connection error: {error_msg}")  # type: ignore
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saat hapus jemaat: {str(e)}")
            self.log_message.emit(f"Exception deleting jemaat: {str(e)}")  # type: ignore

    def view_jemaat(self):
        """View selected jemaat details"""
        try:
            current_row = self.table_widget.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Warning", "Pilih data jemaat yang akan dilihat")
                return

            # Get data dari item yang disimpan, bukan dari filtered_data index
            item = self.table_widget.item(current_row, 0)
            if item:
                selected_data = item.data(Qt.UserRole)
                if selected_data:
                    dialog = JemaatViewDialog(self, selected_data)
                    dialog.exec_()
                else:
                    QMessageBox.warning(self, "Warning", "Data tidak ditemukan")
            else:
                QMessageBox.warning(self, "Warning", "Pilih data jemaat yang akan dilihat")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saat menampilkan detail jemaat: {str(e)}")
            self.log_message.emit(f"Exception viewing jemaat details: {str(e)}")  # type: ignore

    def export_jemaat(self):
        """Export jemaat data to JSON file"""
        if not self.filtered_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data Jemaat",
            f"data_jemaat_{self.current_user}.json",
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.filtered_data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Export Berhasil", f"Data berhasil diekspor ke: {file_path}")
                self.log_message.emit(f"Data jemaat berhasil diekspor ke {file_path}")  # type: ignore
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Gagal mengekspor data: {str(e)}")
                self.log_message.emit(f"Error export data: {str(e)}")  # type: ignore

    def update_table(self):
        """Update table with filtered data"""
        # Disable sorting while updating
        self.table_widget.setSortingEnabled(False)

        # Set row count untuk data saja (tanpa header rows)
        self.table_widget.setRowCount(len(self.filtered_data))

        # Populate data starting from row 0 (tanpa No column)
        for index, jemaat in enumerate(self.filtered_data):
            row_pos = index  # Start from row 0

            # Helper function for date formatting
            def format_date(date_value):
                if not date_value:
                    return ''
                try:
                    if isinstance(date_value, str):
                        dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                        return dt.strftime('%d/%m/%Y')
                    elif hasattr(date_value, 'strftime'):
                        return date_value.strftime('%d/%m/%Y')
                except:
                    pass
                return str(date_value)

            # Helper function for gender formatting
            def format_gender(gender):
                if gender == 'Laki-laki':
                    return 'L'
                elif gender == 'Perempuan':
                    return 'P'
                return str(gender) if gender else ''

            # Helper function to convert empty values to "-"
            def format_value(value):
                if value is None or value == '' or value == 'None':
                    return '-'
                return str(value)

            # Helper function to get creator display name
            def get_creator_display(row_data):
                """Resolve nama pembuat data jemaat untuk tampilan tabel"""
                if not row_data:
                    return 'System'

                # Check various possible field names for creator
                possible_keys = [
                    'created_by_name',
                    'created_by_pengguna_name',
                    'created_by_pengguna_fullname',
                    'created_by_username',
                    'created_by',
                    'dibuat_oleh',
                    'dibuat_oleh_nama',
                    'nama_pembuat',
                    'nama_user',
                    'creator_name'
                ]

                for key in possible_keys:
                    value = row_data.get(key)
                    if value and value not in [None, '', 'None']:
                        return str(value)

                # Check nested creator_info
                creator_info = row_data.get('created_by_pengguna')
                if isinstance(creator_info, dict):
                    for sub_key in ['nama_lengkap', 'full_name', 'name', 'username']:
                        value = creator_info.get(sub_key)
                        if value and value not in [None, '', 'None']:
                            return str(value)

                return '-'

            # All data columns (0-37) matching server structure - tanpa No column (TOTAL 38 COLUMNS with No. KK and NIK)
            data_items = [
                # DATA PRIBADI (columns 0-17) - added No. KK and NIK
                format_value(jemaat.get('wilayah_rohani', '')),
                format_value(jemaat.get('nama_keluarga', '')),
                format_value(jemaat.get('no_kk', '')),  # Column 2: No. KK
                format_value(jemaat.get('nama_lengkap', '')),
                format_value(jemaat.get('nik', '')),  # Column 4: NIK
                format_value(jemaat.get('tempat_lahir', '')),
                format_date(jemaat.get('tanggal_lahir')) or '-',
                format_value(jemaat.get('umur', '')),
                format_value(jemaat.get('status_kekatolikan', '')),
                format_value(jemaat.get('kategori', '')),
                format_gender(jemaat.get('jenis_kelamin', '')) or '-',
                format_value(jemaat.get('hubungan_keluarga', '')),
                format_value(jemaat.get('pendidikan_terakhir', '')),
                format_value(jemaat.get('status_menikah', '')),
                format_value(jemaat.get('jenis_pekerjaan', '')),
                format_value(jemaat.get('detail_pekerjaan', '')),
                format_value(jemaat.get('alamat', '')),
                format_value(jemaat.get('email', '') or jemaat.get('no_telepon', '')),  # Email/No.Hp
                # SAKRAMEN BABTIS (columns 18-21)
                format_value(jemaat.get('status_babtis', '')),
                format_value(jemaat.get('tempat_babtis', '')),
                format_date(jemaat.get('tanggal_babtis')) or '-',
                format_value(jemaat.get('nama_babtis', '')),
                # SAKRAMEN EKARISTI (columns 22-24)
                format_value(jemaat.get('status_ekaristi', '')),
                format_value(jemaat.get('tempat_komuni', '')),
                format_date(jemaat.get('tanggal_komuni')) or '-',
                # SAKRAMEN KRISMA (columns 25-27)
                format_value(jemaat.get('status_krisma', '')),
                format_value(jemaat.get('tempat_krisma', '')),
                format_date(jemaat.get('tanggal_krisma')) or '-',
                # SAKRAMEN PERKAWINAN (columns 28-33)
                format_value(jemaat.get('status_perkawinan', '')),
                format_value(jemaat.get('keuskupan', '')),
                format_value(jemaat.get('paroki', '')),
                format_value(jemaat.get('kota_perkawinan', '')),
                format_date(jemaat.get('tanggal_perkawinan')) or '-',
                format_value(jemaat.get('status_perkawinan_detail', '')),
                # STATUS (columns 34-37) - TOTAL 38 COLUMNS
                format_value(jemaat.get('status_keanggotaan', 'Aktif')),
                format_value(jemaat.get('wilayah_rohani_pindah', '')),
                format_value(jemaat.get('paroki_pindah', '')),
                get_creator_display(jemaat)  # Column 37: Created By Pengguna
            ]

            # Add data to columns 0-37 (total 38 data columns)
            for col, item_text in enumerate(data_items):
                item = QTableWidgetItem(item_text)
                # Center align certain columns for better readability
                if col in [7, 8, 9, 10, 18, 19, 22, 23, 25, 26, 28, 34]:  # Status and categorical columns (adjusted for No. KK and NIK)
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                # Simpan full jemaat data di UserRole pada kolom pertama saja
                if col == 0:
                    item.setData(Qt.UserRole, jemaat)

                self.table_widget.setItem(row_pos, col, item)

        # Re-enable sorting after updating
        self.table_widget.setSortingEnabled(True)

    def filter_data(self):
        """Filter data based on search, dropdown filters, and status filter"""
        search_text = self.search_input.text().lower()
        filter_wilayah = self.filter_wilayah.currentText() if hasattr(self, 'filter_wilayah') else "Semua"
        filter_kategori = self.filter_kategori.currentText() if hasattr(self, 'filter_kategori') else "Semua"
        status_filter = self.status_filter.currentText()

        self.filtered_data = []

        for jemaat in self.jemaat_data:
            # Apply Wilayah Rohani filter
            if filter_wilayah != "Semua":
                wilayah_value = (jemaat.get('wilayah_rohani') or '').strip()
                if wilayah_value != filter_wilayah:
                    continue

            # Apply Kategori filter
            if filter_kategori != "Semua":
                kategori_value = (jemaat.get('kategori') or '').strip()
                if kategori_value != filter_kategori:
                    continue

            # Search filter
            nama = jemaat.get('nama_lengkap', '').lower()
            nama_keluarga = jemaat.get('nama_keluarga', '').lower()
            alamat = jemaat.get('alamat', '').lower()
            wilayah_rohani = jemaat.get('wilayah_rohani', '').lower()

            if search_text and search_text not in nama and search_text not in nama_keluarga and search_text not in alamat and search_text not in wilayah_rohani:
                continue

            # Status filter (using status_keanggotaan field)
            status = jemaat.get('status_keanggotaan', '') or ''
            if status_filter != "Semua":
                if status.lower() != status_filter.lower():
                    continue

            self.filtered_data.append(jemaat)

        self.update_table()
        self.update_statistics()

    def update_statistics(self):
        """Update statistics labels"""
        total = len(self.filtered_data)
        menetap = len([j for j in self.filtered_data if (j.get('status_keanggotaan', '') or '').lower() == 'menetap'])
        pindah = len([j for j in self.filtered_data if (j.get('status_keanggotaan', '') or '').lower() == 'pindah'])

        self.total_label.setText(f"Total: {total} jemaat")
        self.active_label.setText(f"Menetap: {menetap}")
        self.inactive_label.setText(f"Pindah: {pindah}")

        # Style the labels
        self.total_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.active_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.inactive_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
