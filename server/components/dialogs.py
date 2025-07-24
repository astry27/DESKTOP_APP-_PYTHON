# Path: server/components/dialogs.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QTextEdit, QDateEdit, QComboBox, QGroupBox,
                            QDialogButtonBox, QPushButton, QLabel, QDoubleSpinBox)
from PyQt5.QtCore import QDate

class JemaatDialog(QDialog):
    """Dialog untuk menambah/edit data jemaat"""
    # ... (kode JemaatDialog yang sudah ada)
    def __init__(self, parent=None, jemaat_data=None):
        super().__init__(parent)
        self.jemaat_data = jemaat_data
        self.setWindowTitle("Tambah Jemaat" if not jemaat_data else "Edit Jemaat")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        # Setup UI
        layout = QVBoxLayout(self)
        
        # Form
        form_group = QGroupBox("Data Jemaat")
        form_layout = QFormLayout(form_group)
        
        self.nama_input = QLineEdit()
        self.alamat_input = QLineEdit()
        self.telepon_input = QLineEdit()
        self.email_input = QLineEdit()
        self.tanggal_lahir_input = QDateEdit()
        self.tanggal_lahir_input.setCalendarPopup(True)
        self.tanggal_lahir_input.setDate(QDate.currentDate().addYears(-30))
        self.kelamin_input = QComboBox()
        self.kelamin_input.addItems(["Laki-laki", "Perempuan"])
        
        form_layout.addRow("Nama Lengkap:", self.nama_input)
        form_layout.addRow("Alamat:", self.alamat_input)
        form_layout.addRow("No. Telepon:", self.telepon_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Tanggal Lahir:", self.tanggal_lahir_input)
        form_layout.addRow("Jenis Kelamin:", self.kelamin_input)
        
        layout.addWidget(form_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Jika edit, isi data
        if jemaat_data:
            self.load_data()
    
    def load_data(self):
        """Load data untuk edit"""
        if self.jemaat_data:
            self.nama_input.setText(str(self.jemaat_data.get('nama_lengkap', '')))
            self.alamat_input.setText(str(self.jemaat_data.get('alamat', '')))
            self.telepon_input.setText(str(self.jemaat_data.get('no_telepon', '')))
            self.email_input.setText(str(self.jemaat_data.get('email', '')))
            
            # Handle tanggal lahir
            if self.jemaat_data.get('tanggal_lahir'):
                try:
                    if isinstance(self.jemaat_data['tanggal_lahir'], str):
                        date = QDate.fromString(self.jemaat_data['tanggal_lahir'], "yyyy-MM-dd")
                    else:
                        date = QDate(self.jemaat_data['tanggal_lahir'])
                    self.tanggal_lahir_input.setDate(date)
                except:
                    pass
            
            # Set kelamin
            kelamin = str(self.jemaat_data.get('jenis_kelamin', ''))
            index = self.kelamin_input.findText(kelamin)
            if index >= 0:
                self.kelamin_input.setCurrentIndex(index)
    
    def get_data(self):
        """Ambil data dari form"""
        return {
            'nama_lengkap': self.nama_input.text().strip(),
            'alamat': self.alamat_input.text().strip(),
            'no_telepon': self.telepon_input.text().strip(),
            'email': self.email_input.text().strip(),
            'tanggal_lahir': self.tanggal_lahir_input.date().toString("yyyy-MM-dd"),
            'jenis_kelamin': self.kelamin_input.currentText()
        }


class KegiatanDialog(QDialog):
    """Dialog untuk menambah/edit kegiatan"""
    # ... (kode KegiatanDialog yang sudah ada)
    def __init__(self, parent=None, kegiatan_data=None):
        super().__init__(parent)
        self.kegiatan_data = kegiatan_data
        self.setWindowTitle("Tambah Kegiatan" if not kegiatan_data else "Edit Kegiatan")
        self.setModal(True)
        self.setFixedSize(450, 350)
        
        # Setup UI
        layout = QVBoxLayout(self)
        
        # Form
        form_group = QGroupBox("Data Kegiatan")
        form_layout = QFormLayout(form_group)
        
        self.nama_input = QLineEdit()
        self.deskripsi_input = QTextEdit()
        self.deskripsi_input.setMaximumHeight(80)
        self.lokasi_input = QLineEdit()
        self.tanggal_mulai_input = QDateEdit()
        self.tanggal_mulai_input.setCalendarPopup(True)
        self.tanggal_mulai_input.setDate(QDate.currentDate())
        self.tanggal_selesai_input = QDateEdit()
        self.tanggal_selesai_input.setCalendarPopup(True)
        self.tanggal_selesai_input.setDate(QDate.currentDate())
        self.penanggung_jawab_input = QLineEdit()
        
        form_layout.addRow("Nama Kegiatan:", self.nama_input)
        form_layout.addRow("Deskripsi:", self.deskripsi_input)
        form_layout.addRow("Lokasi:", self.lokasi_input)
        form_layout.addRow("Tanggal Mulai:", self.tanggal_mulai_input)
        form_layout.addRow("Tanggal Selesai:", self.tanggal_selesai_input)
        form_layout.addRow("Penanggung Jawab:", self.penanggung_jawab_input)
        
        layout.addWidget(form_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Jika edit, isi data
        if kegiatan_data:
            self.load_data()
    
    def load_data(self):
        """Load data untuk edit"""
        if self.kegiatan_data:
            self.nama_input.setText(str(self.kegiatan_data.get('nama_kegiatan', '')))
            self.deskripsi_input.setText(str(self.kegiatan_data.get('deskripsi', '')))
            self.lokasi_input.setText(str(self.kegiatan_data.get('lokasi', '')))
            self.penanggung_jawab_input.setText(str(self.kegiatan_data.get('penanggungjawab', '')))
            
            # Handle tanggal
            if self.kegiatan_data.get('tanggal_mulai'):
                try:
                    if isinstance(self.kegiatan_data['tanggal_mulai'], str):
                        date = QDate.fromString(self.kegiatan_data['tanggal_mulai'], "yyyy-MM-dd")
                    else:
                        date = QDate(self.kegiatan_data['tanggal_mulai'])
                    self.tanggal_mulai_input.setDate(date)
                except:
                    pass
            
            if self.kegiatan_data.get('tanggal_selesai'):
                try:
                    if isinstance(self.kegiatan_data['tanggal_selesai'], str):
                        date = QDate.fromString(self.kegiatan_data['tanggal_selesai'], "yyyy-MM-dd")
                    else:
                        date = QDate(self.kegiatan_data['tanggal_selesai'])
                    self.tanggal_selesai_input.setDate(date)
                except:
                    pass
    
    def get_data(self):
        """Ambil data dari form"""
        return {
            'nama_kegiatan': self.nama_input.text().strip(),
            'deskripsi': self.deskripsi_input.toPlainText().strip(),
            'lokasi': self.lokasi_input.text().strip(),
            'tanggal_mulai': self.tanggal_mulai_input.date().toString("yyyy-MM-dd"),
            'tanggal_selesai': self.tanggal_selesai_input.date().toString("yyyy-MM-dd"),
            'penanggungjawab': self.penanggung_jawab_input.text().strip()
        }

class PengumumanDialog(QDialog):
    """Dialog untuk menambah/edit pengumuman"""
    # ... (kode PengumumanDialog yang sudah ada)
    def __init__(self, parent=None, pengumuman_data=None):
        super().__init__(parent)
        self.pengumuman_data = pengumuman_data
        self.setWindowTitle("Tambah Pengumuman" if not pengumuman_data else "Edit Pengumuman")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        # Setup UI
        layout = QVBoxLayout(self)
        
        # Form
        form_group = QGroupBox("Data Pengumuman")
        form_layout = QFormLayout(form_group)
        
        self.judul_input = QLineEdit()
        self.isi_input = QTextEdit()
        self.isi_input.setMaximumHeight(150)
        self.tanggal_mulai_input = QDateEdit()
        self.tanggal_mulai_input.setCalendarPopup(True)
        self.tanggal_mulai_input.setDate(QDate.currentDate())
        self.tanggal_selesai_input = QDateEdit()
        self.tanggal_selesai_input.setCalendarPopup(True)
        self.tanggal_selesai_input.setDate(QDate.currentDate().addDays(7))
        
        form_layout.addRow("Judul:", self.judul_input)
        form_layout.addRow("Isi:", self.isi_input)
        form_layout.addRow("Tanggal Mulai:", self.tanggal_mulai_input)
        form_layout.addRow("Tanggal Selesai:", self.tanggal_selesai_input)
        
        layout.addWidget(form_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Jika edit, isi data
        if pengumuman_data:
            self.load_data()
    
    def load_data(self):
        """Load data untuk edit"""
        if self.pengumuman_data:
            self.judul_input.setText(str(self.pengumuman_data.get('judul', '')))
            self.isi_input.setText(str(self.pengumuman_data.get('isi', '')))
            
            # Handle tanggal
            if self.pengumuman_data.get('tanggal_mulai'):
                try:
                    if isinstance(self.pengumuman_data['tanggal_mulai'], str):
                        date = QDate.fromString(self.pengumuman_data['tanggal_mulai'], "yyyy-MM-dd")
                    else:
                        date = QDate(self.pengumuman_data['tanggal_mulai'])
                    self.tanggal_mulai_input.setDate(date)
                except:
                    pass
            
            if self.pengumuman_data.get('tanggal_selesai'):
                try:
                    if isinstance(self.pengumuman_data['tanggal_selesai'], str):
                        date = QDate.fromString(self.pengumuman_data['tanggal_selesai'], "yyyy-MM-dd")
                    else:
                        date = QDate(self.pengumuman_data['tanggal_selesai'])
                    self.tanggal_selesai_input.setDate(date)
                except:
                    pass
    
    def get_data(self):
        """Ambil data dari form"""
        return {
            'judul': self.judul_input.text().strip(),
            'isi': self.isi_input.toPlainText().strip(),
            'tanggal_mulai': self.tanggal_mulai_input.date().toString("yyyy-MM-dd"),
            'tanggal_selesai': self.tanggal_selesai_input.date().toString("yyyy-MM-dd"),
            'dibuat_oleh': 1  # Default user ID, bisa disesuaikan dengan sistem login
        }

class KeuanganDialog(QDialog):
    """Dialog untuk menambah/edit data keuangan."""
    def __init__(self, parent=None, kategori="Pemasukan"):
        super().__init__(parent)
        self.setWindowTitle(f"Tambah {kategori}")
        self.setModal(True)
        self.setFixedSize(450, 350)

        # UI Elements
        layout = QVBoxLayout(self)
        form_group = QGroupBox(f"Data {kategori}")
        form_layout = QFormLayout(form_group)

        self.kategori_input = QLineEdit(kategori)
        self.kategori_input.setReadOnly(True)
        
        self.tanggal_input = QDateEdit()
        self.tanggal_input.setCalendarPopup(True)
        self.tanggal_input.setDate(QDate.currentDate())
        
        self.deskripsi_input = QLineEdit()
        self.sub_kategori_input = QLineEdit()
        
        self.jumlah_input = QDoubleSpinBox()
        self.jumlah_input.setRange(0, 1_000_000_000)
        self.jumlah_input.setGroupSeparatorShown(True)
        
        self.penanggung_jawab_input = QLineEdit()

        form_layout.addRow("Kategori:", self.kategori_input)
        form_layout.addRow("Tanggal:", self.tanggal_input)
        form_layout.addRow("Deskripsi:", self.deskripsi_input)
        form_layout.addRow("Sub-Kategori:", self.sub_kategori_input)
        form_layout.addRow("Jumlah (Rp):", self.jumlah_input)
        form_layout.addRow("Penanggung Jawab:", self.penanggung_jawab_input)
        
        layout.addWidget(form_group)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        """Ambil data dari form."""
        return {
            'kategori': self.kategori_input.text(),
            'tanggal': self.tanggal_input.date().toString("yyyy-MM-dd"),
            'deskripsi': self.deskripsi_input.text().strip(),
            'sub_kategori': self.sub_kategori_input.text().strip(),
            'jumlah': self.jumlah_input.value(),
            'penanggung_jawab': self.penanggung_jawab_input.text().strip()
        }