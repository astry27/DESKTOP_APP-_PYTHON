# Path: client/components/jemaat_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QPushButton, QFrame,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox,
                             QDialog, QFormLayout, QDateEdit, QTextEdit, QSpinBox,
                             QScrollArea, QGroupBox, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QSize
from typing import Optional, Dict, Any, List
from PyQt5.QtGui import QFont, QColor, QIcon
import json
import os
from datetime import datetime, date

class JemaatDialog(QDialog):
    def __init__(self, parent=None, jemaat_data=None):
        super().__init__(parent)
        self.jemaat_data = jemaat_data if jemaat_data else {}
        self.setup_ui()

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
        data_pribadi_group = QGroupBox("DATA PRIBADI")
        data_pribadi_layout = QFormLayout(data_pribadi_group)

        self.wilayah_rohani = QLineEdit(self.jemaat_data.get('wilayah_rohani', ''))
        self.wilayah_rohani.setMinimumWidth(300)

        self.nama_keluarga = QLineEdit(self.jemaat_data.get('nama_keluarga', ''))
        self.nama_keluarga.setMinimumWidth(300)

        self.nama_lengkap = QLineEdit(self.jemaat_data.get('nama_lengkap', ''))
        self.nama_lengkap.setMinimumWidth(300)

        self.tempat_lahir = QLineEdit(self.jemaat_data.get('tempat_lahir', ''))
        self.tempat_lahir.setMinimumWidth(300)

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

        self.kategori = QComboBox()
        self.kategori.addItems(["Pilih Kategori", "Balita", "Anak-anak", "Remaja", "OMK", "KBK", "KIK", "Lansia"])
        self.kategori.setMinimumWidth(300)
        if self.jemaat_data.get('kategori'):
            index = self.kategori.findText(self.jemaat_data['kategori'])
            if index >= 0:
                self.kategori.setCurrentIndex(index)

        self.jenis_kelamin = QComboBox()
        self.jenis_kelamin.addItems(["Pilih jenis kelamin", "L", "P"])
        self.jenis_kelamin.setMinimumWidth(300)
        if self.jemaat_data.get('jenis_kelamin'):
            # Convert from full names to abbreviations
            if self.jemaat_data['jenis_kelamin'] in ['Laki-laki', 'L']:
                self.jenis_kelamin.setCurrentText("L")
            elif self.jemaat_data['jenis_kelamin'] in ['Perempuan', 'P']:
                self.jenis_kelamin.setCurrentText("P")

        self.hubungan_keluarga = QComboBox()
        self.hubungan_keluarga.addItems(["Pilih hubungan dalam keluarga", "Kepala Keluarga", "Istri", "Anak", "Famili lain"])
        self.hubungan_keluarga.setMinimumWidth(300)
        if self.jemaat_data.get('hubungan_keluarga'):
            index = self.hubungan_keluarga.findText(self.jemaat_data['hubungan_keluarga'])
            if index >= 0:
                self.hubungan_keluarga.setCurrentIndex(index)

        self.pendidikan_terakhir = QComboBox()
        self.pendidikan_terakhir.addItems(["Pilih pendidikan terakhir", "SD", "SMP", "SMA", "SMK", "S1", "S2", "S3"])
        self.pendidikan_terakhir.setMinimumWidth(300)
        if self.jemaat_data.get('pendidikan_terakhir'):
            index = self.pendidikan_terakhir.findText(self.jemaat_data['pendidikan_terakhir'])
            if index >= 0:
                self.pendidikan_terakhir.setCurrentIndex(index)

        self.status_menikah = QComboBox()
        self.status_menikah.addItems(["Pilih status menikah", "Belum Menikah", "Sudah Menikah", "Duda", "Janda"])
        self.status_menikah.setMinimumWidth(300)
        if self.jemaat_data.get('status_menikah'):
            index = self.status_menikah.findText(self.jemaat_data['status_menikah'])
            if index >= 0:
                self.status_menikah.setCurrentIndex(index)

        self.jenis_pekerjaan = QComboBox()
        self.jenis_pekerjaan.addItems(["Pilih status pekerjaan", "Pelajar", "Bekerja", "Tidak Bekerja"])
        self.jenis_pekerjaan.setMinimumWidth(300)
        self.jenis_pekerjaan.currentTextChanged.connect(self.on_jenis_pekerjaan_changed)  # type: ignore
        if self.jemaat_data.get('jenis_pekerjaan'):
            index = self.jenis_pekerjaan.findText(self.jemaat_data['jenis_pekerjaan'])
            if index >= 0:
                self.jenis_pekerjaan.setCurrentIndex(index)

        self.detail_pekerjaan = QLineEdit(self.jemaat_data.get('detail_pekerjaan', ''))
        self.detail_pekerjaan.setMinimumWidth(300)
        self.detail_pekerjaan.setVisible(False)

        self.alamat = QLineEdit(self.jemaat_data.get('alamat', ''))
        self.alamat.setMinimumWidth(300)

        self.email = QLineEdit(self.jemaat_data.get('email', ''))
        self.email.setMinimumWidth(300)

        data_pribadi_layout.addRow("Wilayah Rohani:", self.wilayah_rohani)
        data_pribadi_layout.addRow("Nama Keluarga:", self.nama_keluarga)
        data_pribadi_layout.addRow("Nama Lengkap:", self.nama_lengkap)
        data_pribadi_layout.addRow("Tempat Lahir:", self.tempat_lahir)
        data_pribadi_layout.addRow("Tanggal Lahir:", self.tanggal_lahir)
        data_pribadi_layout.addRow("Umur:", self.umur)
        data_pribadi_layout.addRow("Kategori:", self.kategori)
        data_pribadi_layout.addRow("Jenis Kelamin:", self.jenis_kelamin)
        data_pribadi_layout.addRow("Hubungan Keluarga:", self.hubungan_keluarga)
        data_pribadi_layout.addRow("Pendidikan Terakhir:", self.pendidikan_terakhir)
        data_pribadi_layout.addRow("Status Menikah:", self.status_menikah)
        data_pribadi_layout.addRow("Status Pekerjaan:", self.jenis_pekerjaan)

        self.detail_pekerjaan_label = QLabel("Detail Pekerjaan:")
        data_pribadi_layout.addRow(self.detail_pekerjaan_label, self.detail_pekerjaan)
        self.detail_pekerjaan_label.setVisible(False)

        data_pribadi_layout.addRow("Alamat:", self.alamat)
        data_pribadi_layout.addRow("Email:", self.email)

        layout.addWidget(data_pribadi_group)

        # Calculate initial age
        self.calculate_age()

    def setup_sakramen_babtis(self, layout):
        """Setup section Sakramen Babtis"""
        from PyQt5.QtWidgets import QGroupBox
        babtis_group = QGroupBox("SAKRAMEN BABTIS")
        babtis_layout = QFormLayout(babtis_group)

        self.status_babtis = QComboBox()
        self.status_babtis.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_babtis.setMinimumWidth(300)
        self.status_babtis.currentTextChanged.connect(self.on_babtis_status_changed)  # type: ignore
        if self.jemaat_data.get('status_babtis'):
            index = self.status_babtis.findText(self.jemaat_data['status_babtis'])
            if index >= 0:
                self.status_babtis.setCurrentIndex(index)

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
        ekaristi_group = QGroupBox("SAKRAMEN EKARISTI")
        ekaristi_layout = QFormLayout(ekaristi_group)

        self.status_ekaristi = QComboBox()
        self.status_ekaristi.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_ekaristi.setMinimumWidth(300)
        self.status_ekaristi.currentTextChanged.connect(self.on_ekaristi_status_changed)  # type: ignore
        if self.jemaat_data.get('status_ekaristi'):
            index = self.status_ekaristi.findText(self.jemaat_data['status_ekaristi'])
            if index >= 0:
                self.status_ekaristi.setCurrentIndex(index)

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
        krisma_group = QGroupBox("SAKRAMEN KRISMA")
        krisma_layout = QFormLayout(krisma_group)

        self.status_krisma = QComboBox()
        self.status_krisma.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_krisma.setMinimumWidth(300)
        self.status_krisma.currentTextChanged.connect(self.on_krisma_status_changed)  # type: ignore
        if self.jemaat_data.get('status_krisma'):
            index = self.status_krisma.findText(self.jemaat_data['status_krisma'])
            if index >= 0:
                self.status_krisma.setCurrentIndex(index)

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
        perkawinan_group = QGroupBox("SAKRAMEN PERKAWINAN")
        perkawinan_layout = QFormLayout(perkawinan_group)

        self.status_perkawinan = QComboBox()
        self.status_perkawinan.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_perkawinan.setMinimumWidth(300)
        self.status_perkawinan.currentTextChanged.connect(self.on_perkawinan_status_changed)  # type: ignore
        if self.jemaat_data.get('status_perkawinan'):
            index = self.status_perkawinan.findText(self.jemaat_data['status_perkawinan'])
            if index >= 0:
                self.status_perkawinan.setCurrentIndex(index)

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

        perkawinan_layout.addRow("Status:", self.status_perkawinan)
        perkawinan_layout.addRow("Keuskupan:", self.keuskupan)
        perkawinan_layout.addRow("Paroki:", self.paroki)
        perkawinan_layout.addRow("Kota:", self.kota_perkawinan)
        perkawinan_layout.addRow("Tanggal Perkawinan:", self.tanggal_perkawinan)

        layout.addWidget(perkawinan_group)

    def setup_status(self, layout):
        """Setup section Status"""
        from PyQt5.QtWidgets import QGroupBox
        status_group = QGroupBox("STATUS")
        status_layout = QFormLayout(status_group)

        self.status_keanggotaan = QComboBox()
        self.status_keanggotaan.addItems(["Aktif", "Tidak Aktif", "Pindah"])
        self.status_keanggotaan.setMinimumWidth(300)
        if self.jemaat_data.get('status_keanggotaan'):
            index = self.status_keanggotaan.findText(self.jemaat_data['status_keanggotaan'])
            if index >= 0:
                self.status_keanggotaan.setCurrentIndex(index)
            else:
                # Handle legacy 'status' field
                if self.jemaat_data.get('status') == 'Aktif':
                    self.status_keanggotaan.setCurrentText('Aktif')
                elif self.jemaat_data.get('status') == 'Tidak Aktif':
                    self.status_keanggotaan.setCurrentText('Tidak Aktif')

        self.wr_tujuan = QLineEdit(self.jemaat_data.get('wr_tujuan', ''))
        self.wr_tujuan.setMinimumWidth(300)

        self.paroki_tujuan = QLineEdit(self.jemaat_data.get('paroki_tujuan', ''))
        self.paroki_tujuan.setMinimumWidth(300)

        status_layout.addRow("Status Keanggotaan:", self.status_keanggotaan)
        status_layout.addRow("WR Tujuan:", self.wr_tujuan)
        status_layout.addRow("Paroki Tujuan:", self.paroki_tujuan)

        layout.addWidget(status_group)

    def calculate_age(self):
        """Calculate age based on birth date"""
        try:
            birth_date = self.tanggal_lahir.date().toPyDate()
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            self.umur.setText(str(age))
        except:
            self.umur.setText("0")

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

    def get_data(self):
        return {
            # Data Pribadi
            'wilayah_rohani': self.wilayah_rohani.text(),
            'nama_keluarga': self.nama_keluarga.text(),
            'nama_lengkap': self.nama_lengkap.text(),
            'tempat_lahir': self.tempat_lahir.text(),
            'tanggal_lahir': self.tanggal_lahir.date().toString(Qt.DateFormat.ISODate),
            'umur': self.umur.text(),
            'kategori': self.kategori.currentText() if self.kategori.currentIndex() > 0 else '',
            'jenis_kelamin': self.jenis_kelamin.currentText() if self.jenis_kelamin.currentIndex() > 0 else '',
            'hubungan_keluarga': self.hubungan_keluarga.currentText() if self.hubungan_keluarga.currentIndex() > 0 else '',
            'pendidikan_terakhir': self.pendidikan_terakhir.currentText() if self.pendidikan_terakhir.currentIndex() > 0 else '',
            'status_menikah': self.status_menikah.currentText() if self.status_menikah.currentIndex() > 0 else '',
            'jenis_pekerjaan': self.jenis_pekerjaan.currentText() if self.jenis_pekerjaan.currentIndex() > 0 else '',
            'detail_pekerjaan': self.detail_pekerjaan.text(),
            'alamat': self.alamat.text(),
            'email': self.email.text(),

            # Sakramen Babtis
            'status_babtis': self.status_babtis.currentText() if self.status_babtis.currentIndex() > 0 else '',
            'tempat_babtis': self.tempat_babtis.text(),
            'tanggal_babtis': self.tanggal_babtis.date().toString(Qt.DateFormat.ISODate) if self.tempat_babtis.isVisible() else None,
            'nama_babtis': self.nama_babtis.text(),

            # Sakramen Ekaristi
            'status_ekaristi': self.status_ekaristi.currentText() if self.status_ekaristi.currentIndex() > 0 else '',
            'tempat_komuni': self.tempat_komuni.text(),
            'tanggal_komuni': self.tanggal_komuni.date().toString(Qt.DateFormat.ISODate) if self.tempat_komuni.isVisible() else None,

            # Sakramen Krisma
            'status_krisma': self.status_krisma.currentText() if self.status_krisma.currentIndex() > 0 else '',
            'tempat_krisma': self.tempat_krisma.text(),
            'tanggal_krisma': self.tanggal_krisma.date().toString(Qt.DateFormat.ISODate) if self.tempat_krisma.isVisible() else None,

            # Sakramen Perkawinan
            'status_perkawinan': self.status_perkawinan.currentText() if self.status_perkawinan.currentIndex() > 0 else '',
            'keuskupan': self.keuskupan.text(),
            'paroki': self.paroki.text(),
            'kota_perkawinan': self.kota_perkawinan.text(),
            'tanggal_perkawinan': self.tanggal_perkawinan.date().toString(Qt.DateFormat.ISODate) if self.keuskupan.isVisible() else None,

            # Status
            'status_keanggotaan': self.status_keanggotaan.currentText(),
            'status': self.status_keanggotaan.currentText(),
            'wr_tujuan': self.wr_tujuan.text(),
            'paroki_tujuan': self.paroki_tujuan.text(),

            # Metadata
            'tanggal_bergabung': date.today().isoformat(),
            'created_at': datetime.now().isoformat()
        }

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
            ("Status Menikah", self.jemaat_data.get('status_menikah', 'N/A')),
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

        # Header dengan title
        header_frame = QWidget()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 10, 0)

        title_label = QLabel("Database Umat")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header_frame)

        # Toolbar dengan search dan tombol aksi
        toolbar_layout = QHBoxLayout()

        # Search
        search_label = QLabel("Cari:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama jemaat...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.filter_data)  # type: ignore

        # Filter by status
        status_label = QLabel("Status:")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Semua", "Aktif", "Tidak Aktif"])
        self.status_filter.currentTextChanged.connect(self.filter_data)  # type: ignore

        toolbar_layout.addWidget(search_label)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(status_label)
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addStretch()

        layout.addLayout(toolbar_layout)

        # Table dengan 35 kolom menggunakan header normal
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(35)
        self.table_widget.setRowCount(0)

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

        # Freeze header (stays visible when scrolling)
        self.table_widget.horizontalHeader().setFixedHeight(25)

        # Vertical header settings
        self.table_widget.verticalHeader().setVisible(True)
        self.table_widget.verticalHeader().setDefaultSectionSize(24)

        # Table behavior settings
        self.table_widget.setAlternatingRowColors(True)
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

        add_button = self.create_professional_button("add.png", "Tambah Jemaat", "#27ae60", "#2ecc71")
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
        self.active_label = QLabel("Aktif: 0")
        self.inactive_label = QLabel("Tidak Aktif: 0")

        self.stats_layout.addWidget(self.total_label)
        self.stats_layout.addWidget(self.active_label)
        self.stats_layout.addWidget(self.inactive_label)
        self.stats_layout.addStretch()

        layout.addLayout(self.stats_layout)

    def create_professional_button(self, icon_name, text, bg_color, hover_color):
        """Create a professional button with icon and text"""
        button = QPushButton(text)
        button.setMinimumSize(100, 28)
        button.setMaximumSize(130, 28)

        # Add icon if available
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', icon_name)
        if os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(14, 14))
            except Exception:
                pass  # Continue without icon if loading fails

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: 1px solid {bg_color};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 500;
                text-align: center;
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
        """Setup header kolom normal dengan 35 kolom"""
        headers = [
            "No",
            # DATA PRIBADI (1-15)
            "Wilayah Rohani", "Nama Keluarga", "Nama Lengkap", "Tempat Lahir",
            "Tanggal Lahir", "Umur", "Kategori", "J. Kelamin",
            "Hubungan Keluarga", "Pend. Terakhir", "Status Menikah", "Status Pekerjaan",
            "Detail Pekerjaan", "Alamat", "Email/No.Hp",
            # SAKRAMEN BABTIS (16-19)
            "Status Babtis", "Tempat Babtis", "Tanggal Babtis", "Nama Babtis",
            # SAKRAMEN EKARISTI (20-22)
            "Status Ekaristi", "Tempat Komuni", "Tanggal Komuni",
            # SAKRAMEN KRISMA (23-25)
            "Status Krisma", "Tempat Krisma", "Tanggal Krisma",
            # SAKRAMEN PERKAWINAN (26-31)
            "Status Perkawinan", "Keuskupan", "Paroki", "Kota", "Tgl Perkawinan", "Status Perkawinan Detail",
            # STATUS (32-34)
            "Status Keanggotaan", "WR Tujuan", "Paroki Tujuan"
        ]

        self.table_widget.setHorizontalHeaderLabels(headers)

    def setup_column_widths(self):
        """Set up column widths for better display"""
        self.table_widget.setColumnWidth(0, 50)   # No
        self.table_widget.setColumnWidth(1, 110)  # Wilayah Rohani
        self.table_widget.setColumnWidth(2, 120)  # Nama Keluarga
        self.table_widget.setColumnWidth(3, 150)  # Nama Lengkap - wider
        self.table_widget.setColumnWidth(4, 110)  # Tempat Lahir
        self.table_widget.setColumnWidth(5, 100)  # Tanggal Lahir
        self.table_widget.setColumnWidth(6, 60)   # Umur
        self.table_widget.setColumnWidth(7, 90)   # Kategori
        self.table_widget.setColumnWidth(8, 80)   # J. Kelamin
        self.table_widget.setColumnWidth(9, 120)  # Hubungan Keluarga
        self.table_widget.setColumnWidth(10, 110) # Pend. Terakhir
        self.table_widget.setColumnWidth(11, 110) # Status Menikah
        self.table_widget.setColumnWidth(12, 110) # Status Pekerjaan
        self.table_widget.setColumnWidth(13, 120) # Detail Pekerjaan
        self.table_widget.setColumnWidth(14, 180) # Alamat - wider
        self.table_widget.setColumnWidth(15, 130) # Email/No.Hp

        # Sakramen columns
        for i in range(16, 32):
            self.table_widget.setColumnWidth(i, 100)

        # Status columns
        for i in range(32, 35):
            self.table_widget.setColumnWidth(i, 120)

    def apply_professional_table_style(self):
        """Apply professional clean table styling"""
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #d0d0d0;
                gridline-color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
                outline: none;
            }
            QTableWidget::item {
                padding: 4px;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                border: none;
            }
            QTableWidget::item:selected:active {
                background-color: #bbdefb;
                color: #0d47a1;
            }
            QTableWidget:focus {
                outline: none;
                border: 1px solid #90caf9;
            }
            QHeaderView::section {
                background-color: #f8f8f8;
                border: 1px solid #d0d0d0;
                border-left: none;
                padding: 6px 4px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
                font-weight: 600;
                color: #2c3e50;
            }
            QHeaderView::section:hover {
                background-color: #e8e8e8;
            }
            QHeaderView::section:first {
                border-left: 1px solid #d0d0d0;
            }
        """)

        # Vertical header styling
        self.table_widget.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f8f8f8;
                border: 1px solid #d0d0d0;
                border-top: none;
                padding: 2px;
                font-weight: normal;
                color: #555;
                width: 40px;
            }
        """)

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
        """Add new jemaat"""
        dialog = JemaatDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            new_data = {k: v for k, v in new_data.items() if v not in [None, '', 'Pilih Kategori', 'Pilih jenis kelamin', 'Pilih hubungan dalam keluarga', 'Pilih pendidikan terakhir', 'Pilih status menikah', 'Pilih status pekerjaan', 'Pilih status']}
            result = self.api_client.add_jemaat(new_data)
            if result.get('success'):
                response_data = result.get('data', {})
                if response_data.get('status') == 'success':
                    self.load_user_jemaat_data()
                    self.log_message.emit("Data jemaat baru berhasil ditambahkan")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal menambah jemaat: {response_data.get('message', 'Unknown error')}")
            else:
                QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {result.get('data', 'Unknown error')}")

    def edit_jemaat(self):
        """Edit selected jemaat"""
        current_row = self.table_widget.currentRow()
        if current_row < 0 or current_row >= len(self.filtered_data):
            QMessageBox.warning(self, "Warning", "Pilih data jemaat yang akan diedit")
            return

        selected_data = self.filtered_data[current_row]
        dialog = JemaatDialog(self, selected_data)
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.get_data()
            jemaat_id = selected_data.get('id_jemaat') or selected_data.get('id')
            
            result = self.api_client.update_jemaat(jemaat_id, updated_data)
            if result.get('success'):
                response_data = result.get('data', {})
                if response_data.get('status') == 'success':
                    self.load_user_jemaat_data()  # Refresh data from API
                    self.log_message.emit("Data jemaat berhasil diperbarui")  # type: ignore
                else:
                    QMessageBox.warning(self, "Error", f"Gagal update jemaat: {response_data.get('message', 'Unknown error')}")
            else:
                QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {result.get('data', 'Unknown error')}")

    def delete_jemaat(self):
        """Delete selected jemaat"""
        current_row = self.table_widget.currentRow()
        if current_row < 0 or current_row >= len(self.filtered_data):
            QMessageBox.warning(self, "Warning", "Pilih data jemaat yang akan dihapus")
            return

        selected_data = self.filtered_data[current_row]
        reply = QMessageBox.question(self, "Konfirmasi",
                                   f"Apakah Anda yakin ingin menghapus data jemaat '{selected_data.get('nama_lengkap', 'Unknown')}'?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            jemaat_id = selected_data.get('id_jemaat') or selected_data.get('id')
            result = self.api_client.delete_jemaat(jemaat_id)
            if result.get('success'):
                response_data = result.get('data', {})
                if response_data.get('status') == 'success':
                    self.load_user_jemaat_data()  # Refresh data from API
                    self.log_message.emit("Data jemaat berhasil dihapus")  # type: ignore
                else:
                    QMessageBox.warning(self, "Error", f"Gagal hapus jemaat: {response_data.get('message', 'Unknown error')}")
            else:
                QMessageBox.warning(self, "Error", f"Gagal terhubung ke API: {result.get('data', 'Unknown error')}")

    def view_jemaat(self):
        """View selected jemaat details"""
        current_row = self.table_widget.currentRow()
        if current_row < 0 or current_row >= len(self.filtered_data):
            QMessageBox.warning(self, "Warning", "Pilih data jemaat yang akan dilihat")
            return

        selected_data = self.filtered_data[current_row]
        dialog = JemaatViewDialog(self, selected_data)
        dialog.exec_()

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

        # Populate data starting from row 0
        for index, jemaat in enumerate(self.filtered_data):
            row_pos = index  # Start from row 0

            # Column 0: Row number (starting from 1)
            no_item = QTableWidgetItem(str(index + 1))
            no_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row_pos, 0, no_item)

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

            # All data columns (1-34) matching server structure
            data_items = [
                # DATA PRIBADI (columns 1-15)
                str(jemaat.get('wilayah_rohani', '')),
                str(jemaat.get('nama_keluarga', '')),
                str(jemaat.get('nama_lengkap', '')),
                str(jemaat.get('tempat_lahir', '')),
                format_date(jemaat.get('tanggal_lahir')),
                str(jemaat.get('umur', '')),
                str(jemaat.get('kategori', '')),
                format_gender(jemaat.get('jenis_kelamin', '')),
                str(jemaat.get('hubungan_keluarga', '')),
                str(jemaat.get('pendidikan_terakhir', '')),
                str(jemaat.get('status_menikah', '')),
                str(jemaat.get('jenis_pekerjaan', '')),
                str(jemaat.get('detail_pekerjaan', '')),
                str(jemaat.get('alamat', '')),
                str(jemaat.get('email', '') or jemaat.get('telepon', '')),  # Email/No.Hp
                # SAKRAMEN BABTIS (columns 16-19)
                str(jemaat.get('status_babtis', '')),
                str(jemaat.get('tempat_babtis', '')),
                format_date(jemaat.get('tanggal_babtis')),
                str(jemaat.get('nama_babtis', '')),
                # SAKRAMEN EKARISTI (columns 20-22)
                str(jemaat.get('status_ekaristi', '')),
                str(jemaat.get('tempat_komuni', '')),
                format_date(jemaat.get('tanggal_komuni')),
                # SAKRAMEN KRISMA (columns 23-25)
                str(jemaat.get('status_krisma', '')),
                str(jemaat.get('tempat_krisma', '')),
                format_date(jemaat.get('tanggal_krisma')),
                # SAKRAMEN PERKAWINAN (columns 26-31)
                str(jemaat.get('status_perkawinan', '')),
                str(jemaat.get('keuskupan', '')),
                str(jemaat.get('paroki', '')),
                str(jemaat.get('kota_perkawinan', '')),
                format_date(jemaat.get('tanggal_perkawinan')),
                str(jemaat.get('status_perkawinan_detail', '')),
                # STATUS (columns 32-34)
                str(jemaat.get('status_keanggotaan', 'Aktif')),
                str(jemaat.get('wr_tujuan', '')),
                str(jemaat.get('paroki_tujuan', ''))
            ]

            # Add data to columns 1-34 (total 34 data columns + 1 No column = 35 columns)
            for col, item_text in enumerate(data_items, 1):
                item = QTableWidgetItem(item_text)
                # Center align certain columns for better readability
                if col in [0, 6, 7, 8, 16, 17, 20, 21, 23, 24, 26, 32]:  # Status and categorical columns
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table_widget.setItem(row_pos, col, item)

        # Re-enable sorting after updating
        self.table_widget.setSortingEnabled(True)

    def filter_data(self):
        """Filter data based on search and status filter"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()

        self.filtered_data = []

        for jemaat in self.jemaat_data:
            # Search filter
            nama = jemaat.get('nama_lengkap', '').lower()
            nama_keluarga = jemaat.get('nama_keluarga', '').lower()
            alamat = jemaat.get('alamat', '').lower()

            if search_text and search_text not in nama and search_text not in nama_keluarga and search_text not in alamat:
                continue

            # Status filter
            status = jemaat.get('status', '')
            if status_filter != "Semua":
                if status_filter == "Aktif" and status.lower() != "aktif":
                    continue
                elif status_filter == "Tidak Aktif" and status.lower() != "tidak aktif":
                    continue

            self.filtered_data.append(jemaat)

        self.update_table()
        self.update_statistics()

    def update_statistics(self):
        """Update statistics labels"""
        total = len(self.filtered_data)
        aktif = len([j for j in self.filtered_data if j.get('status', '').lower() == 'aktif'])
        tidak_aktif = total - aktif

        self.total_label.setText(f"Total: {total} jemaat")
        self.active_label.setText(f"Aktif: {aktif}")
        self.inactive_label.setText(f"Tidak Aktif: {tidak_aktif}")

        # Style the labels
        self.total_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.active_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.inactive_label.setStyleSheet("color: #e74c3c; font-weight: bold;")