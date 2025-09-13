# Path: server/components/dialogs.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QTextEdit, QDateEdit, QComboBox, QGroupBox,
                            QDialogButtonBox, QPushButton, QLabel, QDoubleSpinBox, QWidget, QScrollArea)
from PyQt5.QtCore import QDate, QLocale, Qt

class JemaatDialog(QDialog):
    """Dialog untuk menambah/edit data jemaat"""
    def __init__(self, parent=None, jemaat_data=None):
        super().__init__(parent)
        self.jemaat_data = jemaat_data
        self.setWindowTitle("Tambah Jemaat" if not jemaat_data else "Edit Jemaat")
        self.setModal(True)
        self.setFixedSize(600, 700)
        
        # Setup UI
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # 1. DATA DIRI
        self.setup_data_diri(layout)
        
        # 2. SAKRAMEN BABTIS
        self.setup_sakramen_babtis(layout)
        
        # 3. SAKRAMEN EKARISTI
        self.setup_sakramen_ekaristi(layout)
        
        # 4. SAKRAMEN KRISMA
        self.setup_sakramen_krisma(layout)
        
        # 5. SAKRAMEN PERKAWINAN
        self.setup_sakramen_perkawinan(layout)
        
        # 6. STATUS
        self.setup_status(layout)
        
        scroll.setWidget(scroll_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # Jika edit, isi data
        if jemaat_data:
            self.load_data()
    
    def setup_data_diri(self, layout):
        """Setup section Data Diri"""
        data_diri_group = QGroupBox("1. DATA DIRI")
        data_diri_layout = QFormLayout(data_diri_group)
        
        self.wilayah_rohani_input = QLineEdit()
        self.wilayah_rohani_input.setMinimumWidth(300)
        self.nama_keluarga_input = QLineEdit()
        self.nama_keluarga_input.setMinimumWidth(300)
        self.nama_lengkap_input = QLineEdit()
        self.nama_lengkap_input.setMinimumWidth(300)
        self.tempat_lahir_input = QLineEdit()
        self.tempat_lahir_input.setMinimumWidth(300)
        
        self.tanggal_lahir_input = QDateEdit()
        self.tanggal_lahir_input.setCalendarPopup(True)
        self.tanggal_lahir_input.setDate(QDate.currentDate())  # Set to current date
        self.tanggal_lahir_input.setMinimumWidth(300)
        self.tanggal_lahir_input.dateChanged.connect(self.calculate_age)
        
        self.umur_input = QLineEdit()
        self.umur_input.setMinimumWidth(300)
        self.umur_input.setPlaceholderText("Umur akan dihitung otomatis")
        self.umur_input.setReadOnly(True)
        
        self.kategori_input = QComboBox()
        self.kategori_input.addItems(["Pilih Kategori", "Balita", "Anak-anak", "Remaja", "OMK", "KBK", "KIK", "Lansia"])
        self.kategori_input.setCurrentIndex(0)
        self.kategori_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.kategori_input)
        
        self.jenis_kelamin_input = QComboBox()
        self.jenis_kelamin_input.addItems(["Pilih jenis kelamin", "L", "P"])
        self.jenis_kelamin_input.setCurrentIndex(0)
        self.jenis_kelamin_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.jenis_kelamin_input)
        
        self.hubungan_keluarga_input = QComboBox()
        self.hubungan_keluarga_input.addItems(["Pilih hubungan dalam keluarga", "Kepala Keluarga", "Istri", "Anak", "Famili lain"])
        self.hubungan_keluarga_input.setCurrentIndex(0)
        self.hubungan_keluarga_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.hubungan_keluarga_input)
        
        self.pendidikan_terakhir_input = QComboBox()
        self.pendidikan_terakhir_input.addItems(["Pilih pendidikan terakhir", "SD", "SMP", "SMA", "SMK", "S1", "S2", "S3"])
        self.pendidikan_terakhir_input.setCurrentIndex(0)
        self.pendidikan_terakhir_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.pendidikan_terakhir_input)
        
        self.jenis_pekerjaan_input = QComboBox()
        self.jenis_pekerjaan_input.addItems(["Pilih status pekerjaan", "Pelajar", "Bekerja", "Tidak Bekerja"])
        self.jenis_pekerjaan_input.setCurrentIndex(0)
        self.jenis_pekerjaan_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.jenis_pekerjaan_input)
        self.jenis_pekerjaan_input.currentTextChanged.connect(self.on_jenis_pekerjaan_changed)
        
        self.detail_pekerjaan_input = QLineEdit()
        self.detail_pekerjaan_input.setMinimumWidth(300)
        self.detail_pekerjaan_input.setVisible(False)
        
        self.status_menikah_input = QComboBox()
        self.status_menikah_input.addItems(["Pilih status menikah", "Belum Menikah", "Sudah Menikah", "Duda", "Janda"])
        self.status_menikah_input.setCurrentIndex(0)
        self.status_menikah_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_menikah_input)
        
        # Legacy fields for compatibility
        self.alamat_input = QLineEdit()
        self.alamat_input.setMinimumWidth(300)
        self.email_input = QLineEdit()
        self.email_input.setMinimumWidth(300)
        
        data_diri_layout.addRow("Wilayah Rohani:", self.wilayah_rohani_input)
        data_diri_layout.addRow("Nama Keluarga:", self.nama_keluarga_input)
        data_diri_layout.addRow("Nama Lengkap:", self.nama_lengkap_input)
        data_diri_layout.addRow("Tempat Lahir:", self.tempat_lahir_input)
        data_diri_layout.addRow("Tanggal Lahir:", self.tanggal_lahir_input)
        data_diri_layout.addRow("Umur:", self.umur_input)
        data_diri_layout.addRow("Kategori:", self.kategori_input)
        data_diri_layout.addRow("Jenis Kelamin:", self.jenis_kelamin_input)
        data_diri_layout.addRow("Hubungan Keluarga:", self.hubungan_keluarga_input)
        data_diri_layout.addRow("Pendidikan Terakhir:", self.pendidikan_terakhir_input)
        data_diri_layout.addRow("Status Menikah:", self.status_menikah_input)
        data_diri_layout.addRow("Status Pekerjaan:", self.jenis_pekerjaan_input)
        
        # Store reference to detail pekerjaan label and field
        self.detail_pekerjaan_label = QLabel("Detail Pekerjaan:")
        data_diri_layout.addRow(self.detail_pekerjaan_label, self.detail_pekerjaan_input)
        # Initially hide both label and input
        self.detail_pekerjaan_label.setVisible(False)
        self.detail_pekerjaan_input.setVisible(False)
        
        # Trigger initial state for detail pekerjaan (should be hidden by default)
        self.on_jenis_pekerjaan_changed(self.jenis_pekerjaan_input.currentText())
        
        data_diri_layout.addRow("Alamat:", self.alamat_input)
        data_diri_layout.addRow("Email:", self.email_input)
        
        # Set consistent spacing and alignment
        data_diri_layout.setVerticalSpacing(5)
        data_diri_layout.setHorizontalSpacing(10)
        data_diri_layout.setFieldGrowthPolicy(data_diri_layout.AllNonFixedFieldsGrow)
        data_diri_layout.setLabelAlignment(Qt.AlignLeft)
        data_diri_layout.setRowWrapPolicy(data_diri_layout.DontWrapRows)
        data_diri_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(data_diri_group)
    
    def setup_sakramen_babtis(self, layout):
        """Setup section Sakramen Babtis"""
        babtis_group = QGroupBox("2. SAKRAMEN BABTIS")
        babtis_layout = QFormLayout(babtis_group)
        
        self.status_babtis_input = QComboBox()
        self.status_babtis_input.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_babtis_input.setCurrentIndex(0)
        self.status_babtis_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_babtis_input)
        self.status_babtis_input.currentTextChanged.connect(self.on_babtis_status_changed)
        
        self.tempat_babtis_input = QLineEdit()
        self.tempat_babtis_input.setMinimumWidth(300)
        self.tanggal_babtis_input = QDateEdit()
        self.tanggal_babtis_input.setCalendarPopup(True)
        self.tanggal_babtis_input.setDate(QDate.currentDate())
        self.tanggal_babtis_input.setMinimumWidth(300)
        self.nama_babtis_input = QLineEdit()
        self.nama_babtis_input.setMinimumWidth(300)
        
        # Initially hide babtis fields
        self.tempat_babtis_input.setVisible(False)
        self.tanggal_babtis_input.setVisible(False)
        self.nama_babtis_input.setVisible(False)
        
        babtis_layout.addRow("Status:", self.status_babtis_input)
        babtis_layout.addRow("Tempat Babtis:", self.tempat_babtis_input)
        babtis_layout.addRow("Tanggal Babtis:", self.tanggal_babtis_input)
        babtis_layout.addRow("Nama Babtis:", self.nama_babtis_input)
        
        # Set consistent spacing and alignment
        babtis_layout.setVerticalSpacing(5)
        babtis_layout.setHorizontalSpacing(10)
        babtis_layout.setFieldGrowthPolicy(babtis_layout.AllNonFixedFieldsGrow)
        babtis_layout.setLabelAlignment(Qt.AlignLeft)
        babtis_layout.setRowWrapPolicy(babtis_layout.DontWrapRows)
        babtis_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(babtis_group)
    
    def setup_sakramen_ekaristi(self, layout):
        """Setup section Sakramen Ekaristi"""
        ekaristi_group = QGroupBox("3. SAKRAMEN EKARISTI")
        ekaristi_layout = QFormLayout(ekaristi_group)
        
        self.status_ekaristi_input = QComboBox()
        self.status_ekaristi_input.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_ekaristi_input.setCurrentIndex(0)
        self.status_ekaristi_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_ekaristi_input)
        self.status_ekaristi_input.currentTextChanged.connect(self.on_ekaristi_status_changed)
        
        self.tempat_komuni_input = QLineEdit()
        self.tempat_komuni_input.setMinimumWidth(300)
        self.tanggal_komuni_input = QDateEdit()
        self.tanggal_komuni_input.setCalendarPopup(True)
        self.tanggal_komuni_input.setDate(QDate.currentDate())
        self.tanggal_komuni_input.setMinimumWidth(300)
        
        # Initially hide ekaristi fields
        self.tempat_komuni_input.setVisible(False)
        self.tanggal_komuni_input.setVisible(False)
        
        ekaristi_layout.addRow("Status:", self.status_ekaristi_input)
        ekaristi_layout.addRow("Tempat Komuni:", self.tempat_komuni_input)
        ekaristi_layout.addRow("Tanggal Komuni:", self.tanggal_komuni_input)
        
        # Set consistent spacing and alignment
        ekaristi_layout.setVerticalSpacing(5)
        ekaristi_layout.setHorizontalSpacing(10)
        ekaristi_layout.setFieldGrowthPolicy(ekaristi_layout.AllNonFixedFieldsGrow)
        ekaristi_layout.setLabelAlignment(Qt.AlignLeft)
        ekaristi_layout.setRowWrapPolicy(ekaristi_layout.DontWrapRows)
        ekaristi_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(ekaristi_group)
    
    def setup_sakramen_krisma(self, layout):
        """Setup section Sakramen Krisma"""
        krisma_group = QGroupBox("4. SAKRAMEN KRISMA")
        krisma_layout = QFormLayout(krisma_group)
        
        self.status_krisma_input = QComboBox()
        self.status_krisma_input.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_krisma_input.setCurrentIndex(0)
        self.status_krisma_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_krisma_input)
        self.status_krisma_input.currentTextChanged.connect(self.on_krisma_status_changed)
        
        self.tempat_krisma_input = QLineEdit()
        self.tempat_krisma_input.setMinimumWidth(300)
        self.tanggal_krisma_input = QDateEdit()
        self.tanggal_krisma_input.setCalendarPopup(True)
        self.tanggal_krisma_input.setDate(QDate.currentDate())
        self.tanggal_krisma_input.setMinimumWidth(300)
        
        # Initially hide perkawinan fields
        self.tempat_krisma_input.setVisible(False)
        self.tanggal_krisma_input.setVisible(False)
        
        krisma_layout.addRow("Status:", self.status_krisma_input)
        krisma_layout.addRow("Tempat Krisma:", self.tempat_krisma_input)
        krisma_layout.addRow("Tanggal:", self.tanggal_krisma_input)
        
        # Set consistent spacing and alignment
        krisma_layout.setVerticalSpacing(5)
        krisma_layout.setHorizontalSpacing(10)
        krisma_layout.setFieldGrowthPolicy(krisma_layout.AllNonFixedFieldsGrow)
        krisma_layout.setLabelAlignment(Qt.AlignLeft)
        krisma_layout.setRowWrapPolicy(krisma_layout.DontWrapRows)
        krisma_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(krisma_group)
    
    def setup_sakramen_perkawinan(self, layout):
        """Setup section Sakramen Perkawinan"""
        perkawinan_group = QGroupBox("5. SAKRAMEN PERKAWINAN")
        perkawinan_layout = QFormLayout(perkawinan_group)
        
        self.status_perkawinan_input = QComboBox()
        self.status_perkawinan_input.addItems(["Pilih status", "Belum", "Sudah"])
        self.status_perkawinan_input.setCurrentIndex(0)
        self.status_perkawinan_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_perkawinan_input)
        self.status_perkawinan_input.currentTextChanged.connect(self.on_perkawinan_status_changed)
        
        self.keuskupan_input = QLineEdit()
        self.keuskupan_input.setMinimumWidth(300)
        self.paroki_input = QLineEdit()
        self.paroki_input.setMinimumWidth(300)
        self.kota_perkawinan_input = QLineEdit()
        self.kota_perkawinan_input.setMinimumWidth(300)
        self.tanggal_perkawinan_input = QDateEdit()
        self.tanggal_perkawinan_input.setCalendarPopup(True)
        self.tanggal_perkawinan_input.setDate(QDate.currentDate())
        self.tanggal_perkawinan_input.setMinimumWidth(300)
        self.status_perkawinan_detail_input = QComboBox()
        self.status_perkawinan_detail_input.addItems(["Pilih status", "Sipil", "Gereja", "Sipil dan Gereja"])
        self.status_perkawinan_detail_input.setCurrentIndex(0)
        self.status_perkawinan_detail_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_perkawinan_detail_input)
        
        # Initially hide perkawinan fields
        self.keuskupan_input.setVisible(False)
        self.paroki_input.setVisible(False)
        self.kota_perkawinan_input.setVisible(False)
        self.tanggal_perkawinan_input.setVisible(False)
        self.status_perkawinan_detail_input.setVisible(False)
        
        perkawinan_layout.addRow("Status:", self.status_perkawinan_input)
        perkawinan_layout.addRow("Keuskupan:", self.keuskupan_input)
        perkawinan_layout.addRow("Paroki:", self.paroki_input)
        perkawinan_layout.addRow("Kota:", self.kota_perkawinan_input)
        perkawinan_layout.addRow("Tanggal:", self.tanggal_perkawinan_input)
        perkawinan_layout.addRow("Status Perkawinan:", self.status_perkawinan_detail_input)
        
        # Set consistent spacing and alignment
        perkawinan_layout.setVerticalSpacing(5)
        perkawinan_layout.setHorizontalSpacing(10)
        perkawinan_layout.setFieldGrowthPolicy(perkawinan_layout.AllNonFixedFieldsGrow)
        perkawinan_layout.setLabelAlignment(Qt.AlignLeft)
        perkawinan_layout.setRowWrapPolicy(perkawinan_layout.DontWrapRows)
        perkawinan_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(perkawinan_group)
    
    def setup_status(self, layout):
        """Setup section Status"""
        status_group = QGroupBox("6. STATUS")
        status_layout = QFormLayout(status_group)
        
        self.status_keanggotaan_input = QComboBox()
        self.status_keanggotaan_input.addItems(["Pilih Status", "Menetap", "Pindah", "Meninggal Dunia"])
        self.status_keanggotaan_input.setCurrentIndex(0)
        self.status_keanggotaan_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_keanggotaan_input)
        self.status_keanggotaan_input.currentTextChanged.connect(self.on_status_keanggotaan_changed)
        
        # Conditional fields for Pindah status
        self.wilayah_rohani_pindah_input = QLineEdit()
        self.wilayah_rohani_pindah_input.setMinimumWidth(300)
        self.wilayah_rohani_pindah_input.setVisible(False)
        
        self.paroki_pindah_input = QLineEdit()
        self.paroki_pindah_input.setMinimumWidth(300)
        self.paroki_pindah_input.setVisible(False)
        
        self.keuskupan_pindah_input = QLineEdit()
        self.keuskupan_pindah_input.setMinimumWidth(300)
        self.keuskupan_pindah_input.setVisible(False)
        
        status_layout.addRow("Status Keanggotaan:", self.status_keanggotaan_input)
        status_layout.addRow("Wilayah Rohani Tujuan:", self.wilayah_rohani_pindah_input)
        status_layout.addRow("Paroki Tujuan:", self.paroki_pindah_input)
        status_layout.addRow("Keuskupan Tujuan:", self.keuskupan_pindah_input)
        
        # Set consistent spacing and alignment
        status_layout.setVerticalSpacing(5)
        status_layout.setHorizontalSpacing(10)
        status_layout.setFieldGrowthPolicy(status_layout.AllNonFixedFieldsGrow)
        status_layout.setLabelAlignment(Qt.AlignLeft)
        status_layout.setRowWrapPolicy(status_layout.DontWrapRows)
        status_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(status_group)
    
    def setup_placeholder_style(self, combo_box):
        """Setup placeholder style for combo box"""
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
    
    def calculate_age(self):
        """Calculate age based on birth date"""
        try:
            birth_date = self.tanggal_lahir_input.date()
            current_date = QDate.currentDate()
            
            age = current_date.year() - birth_date.year()
            
            # Adjust if birthday hasn't occurred this year
            if (current_date.month() < birth_date.month() or 
                (current_date.month() == birth_date.month() and current_date.day() < birth_date.day())):
                age -= 1
            
            self.umur_input.setText(f"{age} tahun")
            
            # Auto-set kategori based on age
            if age < 2:
                self.kategori_input.setCurrentText("Balita")
            elif age < 12:
                self.kategori_input.setCurrentText("Anak-anak")
            elif age < 18:
                self.kategori_input.setCurrentText("Remaja")
            elif age < 30:
                self.kategori_input.setCurrentText("OMK")
            elif age < 50:
                self.kategori_input.setCurrentText("KBK")
            elif age < 60:
                self.kategori_input.setCurrentText("KIK")
            else:
                self.kategori_input.setCurrentText("Lansia")
                
        except Exception as e:
            self.umur_input.setText("")
    
    def on_status_keanggotaan_changed(self, text):
        """Handle perubahan status keanggotaan"""
        visible = (text == "Pindah")
        self.wilayah_rohani_pindah_input.setVisible(visible)
        self.paroki_pindah_input.setVisible(visible)
        self.keuskupan_pindah_input.setVisible(visible)
    
    def on_jenis_pekerjaan_changed(self, text):
        """Handle perubahan status pekerjaan"""
        # Detail pekerjaan hanya muncul saat pilih "Bekerja"
        visible = (text == "Bekerja")
        self.detail_pekerjaan_label.setVisible(visible)
        self.detail_pekerjaan_input.setVisible(visible)
    
    def on_babtis_status_changed(self, text):
        """Handle perubahan status babtis"""
        visible = (text == "Sudah")
        self.tempat_babtis_input.setVisible(visible)
        self.tanggal_babtis_input.setVisible(visible)
        self.nama_babtis_input.setVisible(visible)
    
    def on_ekaristi_status_changed(self, text):
        """Handle perubahan status ekaristi"""
        visible = (text == "Sudah")
        self.tempat_komuni_input.setVisible(visible)
        self.tanggal_komuni_input.setVisible(visible)
    
    def on_krisma_status_changed(self, text):
        """Handle perubahan status krisma"""
        visible = (text == "Sudah")
        self.tempat_krisma_input.setVisible(visible)
        self.tanggal_krisma_input.setVisible(visible)
    
    def on_perkawinan_status_changed(self, text):
        """Handle perubahan status perkawinan"""
        visible = (text == "Sudah")
        self.keuskupan_input.setVisible(visible)
        self.paroki_input.setVisible(visible)
        self.kota_perkawinan_input.setVisible(visible)
        self.tanggal_perkawinan_input.setVisible(visible)
        self.status_perkawinan_detail_input.setVisible(visible)
    
    def load_data(self):
        """Load data untuk edit"""
        if not self.jemaat_data:
            return
        
        # Data Diri
        self.wilayah_rohani_input.setText(str(self.jemaat_data.get('wilayah_rohani', '')))
        self.nama_keluarga_input.setText(str(self.jemaat_data.get('nama_keluarga', '')))
        self.nama_lengkap_input.setText(str(self.jemaat_data.get('nama_lengkap', '')))
        self.tempat_lahir_input.setText(str(self.jemaat_data.get('tempat_lahir', '')))
        self.alamat_input.setText(str(self.jemaat_data.get('alamat', '')))
        self.email_input.setText(str(self.jemaat_data.get('email', '')))
        self.detail_pekerjaan_input.setText(str(self.jemaat_data.get('detail_pekerjaan', '')))
        
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
        
        # Set combo box values with conversion from old format
        # Convert jenis kelamin dari format lama ke format baru
        jenis_kelamin = self.jemaat_data.get('jenis_kelamin', 'L')
        if jenis_kelamin == 'Laki-laki':
            jenis_kelamin = 'L'
        elif jenis_kelamin == 'Perempuan':
            jenis_kelamin = 'P'
        
        self.set_combo_value(self.jenis_kelamin_input, jenis_kelamin)
        self.set_combo_value(self.hubungan_keluarga_input, self.jemaat_data.get('hubungan_keluarga', 'Kepala Keluarga'))
        self.set_combo_value(self.pendidikan_terakhir_input, self.jemaat_data.get('pendidikan_terakhir', 'SMA'))
        self.set_combo_value(self.jenis_pekerjaan_input, self.jemaat_data.get('jenis_pekerjaan', 'Bekerja'))
        self.set_combo_value(self.status_menikah_input, self.jemaat_data.get('status_menikah', ''))
        self.set_combo_value(self.kategori_input, self.jemaat_data.get('kategori', ''))
        
        # Calculate age after setting birth date
        self.calculate_age()
        
        # Trigger pekerjaan changed to show/hide detail pekerjaan
        self.on_jenis_pekerjaan_changed(self.jenis_pekerjaan_input.currentText())
        
        # Sakramen Babtis
        self.set_combo_value(self.status_babtis_input, self.jemaat_data.get('status_babtis', 'Belum'))
        self.tempat_babtis_input.setText(str(self.jemaat_data.get('tempat_babtis', '')))
        self.nama_babtis_input.setText(str(self.jemaat_data.get('nama_babtis', '')))
        
        if self.jemaat_data.get('tanggal_babtis'):
            try:
                if isinstance(self.jemaat_data['tanggal_babtis'], str):
                    date = QDate.fromString(self.jemaat_data['tanggal_babtis'], "yyyy-MM-dd")
                else:
                    date = QDate(self.jemaat_data['tanggal_babtis'])
                self.tanggal_babtis_input.setDate(date)
            except:
                pass
        
        # Trigger babtis changed to show/hide fields
        self.on_babtis_status_changed(self.status_babtis_input.currentText())
        
        # Sakramen Ekaristi
        self.set_combo_value(self.status_ekaristi_input, self.jemaat_data.get('status_ekaristi', 'Belum'))
        self.tempat_komuni_input.setText(str(self.jemaat_data.get('tempat_komuni', '')))
        
        if self.jemaat_data.get('tanggal_komuni'):
            try:
                if isinstance(self.jemaat_data['tanggal_komuni'], str):
                    date = QDate.fromString(self.jemaat_data['tanggal_komuni'], "yyyy-MM-dd")
                else:
                    date = QDate(self.jemaat_data['tanggal_komuni'])
                self.tanggal_komuni_input.setDate(date)
            except:
                pass
        
        # Trigger ekaristi changed to show/hide fields
        self.on_ekaristi_status_changed(self.status_ekaristi_input.currentText())
        
        # Sakramen Krisma
        self.set_combo_value(self.status_krisma_input, self.jemaat_data.get('status_krisma', 'Belum'))
        self.tempat_krisma_input.setText(str(self.jemaat_data.get('tempat_krisma', '')))
        
        if self.jemaat_data.get('tanggal_krisma'):
            try:
                if isinstance(self.jemaat_data['tanggal_krisma'], str):
                    date = QDate.fromString(self.jemaat_data['tanggal_krisma'], "yyyy-MM-dd")
                else:
                    date = QDate(self.jemaat_data['tanggal_krisma'])
                self.tanggal_krisma_input.setDate(date)
            except:
                pass
        
        # Trigger krisma changed to show/hide fields
        self.on_krisma_status_changed(self.status_krisma_input.currentText())
        
        # Sakramen Perkawinan
        self.set_combo_value(self.status_perkawinan_input, self.jemaat_data.get('status_perkawinan', 'Belum'))
        self.keuskupan_input.setText(str(self.jemaat_data.get('keuskupan', '')))
        self.paroki_input.setText(str(self.jemaat_data.get('paroki', '')))
        self.kota_perkawinan_input.setText(str(self.jemaat_data.get('kota_perkawinan', '')))
        self.set_combo_value(self.status_perkawinan_detail_input, self.jemaat_data.get('status_perkawinan_detail', 'Sipil'))
        
        if self.jemaat_data.get('tanggal_perkawinan'):
            try:
                if isinstance(self.jemaat_data['tanggal_perkawinan'], str):
                    date = QDate.fromString(self.jemaat_data['tanggal_perkawinan'], "yyyy-MM-dd")
                else:
                    date = QDate(self.jemaat_data['tanggal_perkawinan'])
                self.tanggal_perkawinan_input.setDate(date)
            except:
                pass
        
        # Trigger perkawinan changed to show/hide fields
        self.on_perkawinan_status_changed(self.status_perkawinan_input.currentText())
        
        # Status
        self.set_combo_value(self.status_keanggotaan_input, self.jemaat_data.get('status_keanggotaan', 'Aktif'))
        
        # Conditional Pindah fields
        self.wilayah_rohani_pindah_input.setText(str(self.jemaat_data.get('wilayah_rohani_pindah', '')))
        self.paroki_pindah_input.setText(str(self.jemaat_data.get('paroki_pindah', '')))
        self.keuskupan_pindah_input.setText(str(self.jemaat_data.get('keuskupan_pindah', '')))
        
        # Trigger status keanggotaan changed to show/hide pindah fields
        self.on_status_keanggotaan_changed(self.status_keanggotaan_input.currentText())
    
    def set_combo_value(self, combo, value):
        """Set combo box value"""
        if not value or str(value).strip() == '':
            combo.setCurrentIndex(0)  # Set to placeholder
            return
            
        index = combo.findText(str(value))
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.setCurrentIndex(0)  # Fallback to placeholder
    
    def get_data(self):
        """Ambil data dari form"""
        # Helper function to get combo box value (excluding placeholder)
        def get_combo_value(combo_box):
            if combo_box.currentIndex() == 0:  # Placeholder selected
                return ''  # Return empty string for placeholder
            return combo_box.currentText()
        
        data = {
            # Data Diri
            'wilayah_rohani': self.wilayah_rohani_input.text().strip(),
            'nama_keluarga': self.nama_keluarga_input.text().strip(),
            'nama_lengkap': self.nama_lengkap_input.text().strip(),
            'tempat_lahir': self.tempat_lahir_input.text().strip(),
            'tanggal_lahir': self.tanggal_lahir_input.date().toString("yyyy-MM-dd"),
            'umur': self.umur_input.text().replace(' tahun', ''),
            'kategori': get_combo_value(self.kategori_input),
            'jenis_kelamin': get_combo_value(self.jenis_kelamin_input),
            'hubungan_keluarga': get_combo_value(self.hubungan_keluarga_input),
            'pendidikan_terakhir': get_combo_value(self.pendidikan_terakhir_input),
            'jenis_pekerjaan': get_combo_value(self.jenis_pekerjaan_input),
            'detail_pekerjaan': self.detail_pekerjaan_input.text().strip() if self.detail_pekerjaan_input.isVisible() else '',
            'status_menikah': get_combo_value(self.status_menikah_input),
            'alamat': self.alamat_input.text().strip(),
            'email': self.email_input.text().strip(),
            
            # Sakramen Babtis
            'status_babtis': get_combo_value(self.status_babtis_input),
            'tempat_babtis': self.tempat_babtis_input.text().strip() if self.tempat_babtis_input.isVisible() else '',
            'tanggal_babtis': self.tanggal_babtis_input.date().toString("yyyy-MM-dd") if self.tanggal_babtis_input.isVisible() else None,
            'nama_babtis': self.nama_babtis_input.text().strip() if self.nama_babtis_input.isVisible() else '',
            
            # Sakramen Ekaristi
            'status_ekaristi': get_combo_value(self.status_ekaristi_input),
            'tempat_komuni': self.tempat_komuni_input.text().strip() if self.tempat_komuni_input.isVisible() else '',
            'tanggal_komuni': self.tanggal_komuni_input.date().toString("yyyy-MM-dd") if self.tanggal_komuni_input.isVisible() else None,
            
            # Sakramen Krisma
            'status_krisma': get_combo_value(self.status_krisma_input),
            'tempat_krisma': self.tempat_krisma_input.text().strip() if self.tempat_krisma_input.isVisible() else '',
            'tanggal_krisma': self.tanggal_krisma_input.date().toString("yyyy-MM-dd") if self.tanggal_krisma_input.isVisible() else None,
            
            # Sakramen Perkawinan
            'status_perkawinan': get_combo_value(self.status_perkawinan_input),
            'keuskupan': self.keuskupan_input.text().strip() if self.keuskupan_input.isVisible() else '',
            'paroki': self.paroki_input.text().strip() if self.paroki_input.isVisible() else '',
            'kota_perkawinan': self.kota_perkawinan_input.text().strip() if self.kota_perkawinan_input.isVisible() else '',
            'tanggal_perkawinan': self.tanggal_perkawinan_input.date().toString("yyyy-MM-dd") if self.tanggal_perkawinan_input.isVisible() else None,
            'status_perkawinan_detail': get_combo_value(self.status_perkawinan_detail_input) if self.status_perkawinan_detail_input.isVisible() else '',
            
            # Status
            'status_keanggotaan': get_combo_value(self.status_keanggotaan_input),
            'wilayah_rohani_pindah': self.wilayah_rohani_pindah_input.text().strip() if self.wilayah_rohani_pindah_input.isVisible() else '',
            'paroki_pindah': self.paroki_pindah_input.text().strip() if self.paroki_pindah_input.isVisible() else '',
            'keuskupan_pindah': self.keuskupan_pindah_input.text().strip() if self.keuskupan_pindah_input.isVisible() else ''
        }
        
        return data


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
    def __init__(self, parent=None, pengumuman_data=None):
        super().__init__(parent)
        self.pengumuman_data = pengumuman_data
        self.setWindowTitle("Tambah Pengumuman" if not pengumuman_data else "Edit Pengumuman")
        self.setModal(True)
        self.setFixedSize(500, 450)
        
        # Setup UI
        layout = QVBoxLayout(self)
        
        # Form
        form_group = QGroupBox("Data Pengumuman")
        form_layout = QFormLayout(form_group)
        
        # 1. Tanggal - otomatis mengikuti data realtime dengan format Hari + Tanggal
        self.tanggal_input = QDateEdit()
        self.tanggal_input.setCalendarPopup(True)
        self.tanggal_input.setDate(QDate.currentDate())
        # Set custom display format: Day, dd/MM/yyyy (e.g., Senin, 12/09/2025)
        self.tanggal_input.setDisplayFormat("dddd, dd/MM/yyyy")
        self.tanggal_input.setReadOnly(False)  # Allow editing if needed
        
        # 2. Pembuat Pengumuman
        self.pembuat_input = QLineEdit()
        self.pembuat_input.setPlaceholderText("Nama pembuat pengumuman")
        
        # 3. Sasaran/Tujuan
        self.sasaran_input = QComboBox()
        self.sasaran_input.addItems([
            "Umum", "Jemaat Dewasa", "Anak-anak", "Remaja", "OMK", 
            "KBK", "KIK", "Lansia", "Pengurus", "Komisi", "Seksi"
        ])
        self.sasaran_input.setEditable(True)  # Allow custom input
        
        # 4. Judul Pengumuman
        self.judul_input = QLineEdit()
        self.judul_input.setPlaceholderText("Masukkan judul pengumuman")
        
        # 5. Isi Pengumuman
        self.isi_input = QTextEdit()
        self.isi_input.setMaximumHeight(120)
        self.isi_input.setPlaceholderText("Masukkan isi pengumuman lengkap")
        
        # Add form rows in the correct order matching table layout
        form_layout.addRow("Tanggal Pengumuman:", self.tanggal_input)
        form_layout.addRow("Pembuat Pengumuman:", self.pembuat_input)
        form_layout.addRow("Sasaran/Tujuan:", self.sasaran_input)
        form_layout.addRow("Judul Pengumuman:", self.judul_input)
        form_layout.addRow("Isi Pengumuman:", self.isi_input)
        
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
            
            # Load pembuat - check different possible field names
            pembuat = (self.pengumuman_data.get('pembuat') or 
                      self.pengumuman_data.get('dibuat_oleh_nama') or 
                      self.pengumuman_data.get('created_by_name') or 
                      self.pengumuman_data.get('admin_name') or 'Administrator')
            self.pembuat_input.setText(str(pembuat))
            
            # Load sasaran - check different possible field names
            sasaran = (self.pengumuman_data.get('sasaran') or 
                      self.pengumuman_data.get('target_audience') or 
                      self.pengumuman_data.get('kategori') or 'Umum')
            
            # Try to find exact match in combo box items
            index = self.sasaran_input.findText(str(sasaran))
            if index >= 0:
                self.sasaran_input.setCurrentIndex(index)
            else:
                # If not found in predefined items, set as custom text
                self.sasaran_input.setCurrentText(str(sasaran))
            
            # Handle tanggal - check for different date field names for compatibility
            tanggal_value = (self.pengumuman_data.get('tanggal') or 
                           self.pengumuman_data.get('tanggal_mulai') or 
                           self.pengumuman_data.get('tanggal_dibuat'))
            
            if tanggal_value:
                try:
                    if isinstance(tanggal_value, str):
                        date = QDate.fromString(tanggal_value, "yyyy-MM-dd")
                    else:
                        date = QDate(tanggal_value)
                    self.tanggal_input.setDate(date)
                except:
                    # If date parsing fails, use current date
                    self.tanggal_input.setDate(QDate.currentDate())
    
    def get_data(self):
        """Ambil data dari form"""
        return {
            'judul': self.judul_input.text().strip(),
            'isi': self.isi_input.toPlainText().strip(),
            'sasaran': self.sasaran_input.currentText().strip(),
            'pembuat': self.pembuat_input.text().strip(),
            'tanggal': self.tanggal_input.date().toString("yyyy-MM-dd"),
            'tanggal_mulai': self.tanggal_input.date().toString("yyyy-MM-dd"),  # For compatibility with existing database
            'dibuat_oleh': 1  # Default user ID, bisa disesuaikan dengan sistem login
        }

class InventarisDialog(QDialog):
    """Dialog untuk menambah/edit data inventaris."""
    def __init__(self, parent=None, inventaris_data=None):
        super().__init__(parent)
        self.inventaris_data = inventaris_data
        self.setWindowTitle("Tambah Inventaris" if not inventaris_data else "Edit Inventaris")
        self.setModal(True)
        self.setFixedSize(500, 550)

        # Setup UI
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # 1. INFORMASI DASAR
        self.setup_informasi_dasar(layout)
        
        # 2. DETAIL BARANG
        self.setup_detail_barang(layout)
        
        # 3. STATUS & LOKASI
        self.setup_status_lokasi(layout)
        
        scroll.setWidget(scroll_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # Jika edit, isi data
        if inventaris_data:
            self.load_data()

    def setup_informasi_dasar(self, layout):
        """Setup section Informasi Dasar"""
        info_group = QGroupBox("1. INFORMASI DASAR")
        info_layout = QFormLayout(info_group)
        
        self.nama_barang_input = QLineEdit()
        self.nama_barang_input.setMinimumWidth(350)
        
        self.kode_barang_input = QLineEdit()
        self.kode_barang_input.setMinimumWidth(350)
        self.kode_barang_input.setPlaceholderText("Contoh: INV-001")
        
        self.kategori_input = QComboBox()
        self.kategori_input.addItems(["Pilih Kategori", "Peralatan Liturgi", "Furniture", "Elektronik", "Alat Tulis", "Perlengkapan Kantor", "Lainnya"])
        self.kategori_input.setCurrentIndex(0)
        self.kategori_input.setMinimumWidth(350)
        self.setup_placeholder_style(self.kategori_input)
        
        self.merk_input = QLineEdit()
        self.merk_input.setMinimumWidth(350)
        
        info_layout.addRow("Nama Barang:", self.nama_barang_input)
        info_layout.addRow("Kode Barang:", self.kode_barang_input)
        info_layout.addRow("Kategori:", self.kategori_input)
        info_layout.addRow("Merk/Brand:", self.merk_input)
        
        layout.addWidget(info_group)
    
    def setup_detail_barang(self, layout):
        """Setup section Detail Barang"""
        detail_group = QGroupBox("2. DETAIL BARANG")
        detail_layout = QFormLayout(detail_group)
        
        self.jumlah_input = QDoubleSpinBox()
        self.jumlah_input.setRange(1, 1000)
        self.jumlah_input.setValue(1)
        self.jumlah_input.setMinimumWidth(350)
        
        self.satuan_input = QComboBox()
        self.satuan_input.addItems(["Pilih Satuan", "Unit", "Buah", "Set", "Pasang", "Lembar", "Roll", "Meter", "Kg", "Liter"])
        self.satuan_input.setCurrentIndex(0)
        self.satuan_input.setMinimumWidth(350)
        self.setup_placeholder_style(self.satuan_input)
        
        self.harga_satuan_input = QDoubleSpinBox()
        self.harga_satuan_input.setRange(0, 1_000_000_000)
        self.harga_satuan_input.setGroupSeparatorShown(True)
        self.harga_satuan_input.setValue(0)
        self.harga_satuan_input.setMinimumWidth(350)
        
        # Set locale Indonesia
        locale = QLocale(QLocale.Indonesian, QLocale.Indonesia)
        self.harga_satuan_input.setLocale(locale)
        
        self.tanggal_beli_input = QDateEdit()
        self.tanggal_beli_input.setCalendarPopup(True)
        self.tanggal_beli_input.setDate(QDate.currentDate())
        self.tanggal_beli_input.setMinimumWidth(350)
        
        self.supplier_input = QLineEdit()
        self.supplier_input.setMinimumWidth(350)
        
        detail_layout.addRow("Jumlah:", self.jumlah_input)
        detail_layout.addRow("Satuan:", self.satuan_input)
        detail_layout.addRow("Harga Satuan (Rp):", self.harga_satuan_input)
        detail_layout.addRow("Tanggal Beli:", self.tanggal_beli_input)
        detail_layout.addRow("Supplier:", self.supplier_input)
        
        layout.addWidget(detail_group)
    
    def setup_status_lokasi(self, layout):
        """Setup section Status & Lokasi"""
        status_group = QGroupBox("3. STATUS & LOKASI")
        status_layout = QFormLayout(status_group)
        
        self.kondisi_input = QComboBox()
        self.kondisi_input.addItems(["Pilih Kondisi", "Baik", "Rusak Ringan", "Rusak Berat", "Hilang"])
        self.kondisi_input.setCurrentIndex(0)
        self.kondisi_input.setMinimumWidth(350)
        self.setup_placeholder_style(self.kondisi_input)
        
        self.lokasi_input = QLineEdit()
        self.lokasi_input.setMinimumWidth(350)
        self.lokasi_input.setPlaceholderText("Contoh: Ruang Pastor, Aula, Sekretariat")
        
        self.penanggung_jawab_input = QLineEdit()
        self.penanggung_jawab_input.setMinimumWidth(350)
        
        self.keterangan_input = QTextEdit()
        self.keterangan_input.setMaximumHeight(80)
        self.keterangan_input.setMinimumWidth(350)
        
        status_layout.addRow("Kondisi:", self.kondisi_input)
        status_layout.addRow("Lokasi:", self.lokasi_input)
        status_layout.addRow("Penanggung Jawab:", self.penanggung_jawab_input)
        status_layout.addRow("Keterangan:", self.keterangan_input)
        
        layout.addWidget(status_group)
    
    def setup_placeholder_style(self, combo_box):
        """Setup placeholder style for combo box"""
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
        
        def on_selection_changed():
            if combo_box.currentIndex() == 0:
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
    
    def set_combo_value(self, combo, value):
        """Set combo box value"""
        if not value or str(value).strip() == '':
            combo.setCurrentIndex(0)
            return
            
        index = combo.findText(str(value))
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.setCurrentIndex(0)
    
    def load_data(self):
        """Load data untuk edit"""
        if not self.inventaris_data:
            return
        
        # Informasi Dasar
        self.nama_barang_input.setText(str(self.inventaris_data.get('nama_barang', '')))
        self.kode_barang_input.setText(str(self.inventaris_data.get('kode_barang', '')))
        self.set_combo_value(self.kategori_input, self.inventaris_data.get('kategori', ''))
        self.merk_input.setText(str(self.inventaris_data.get('merk', '')))
        
        # Detail Barang
        self.jumlah_input.setValue(float(self.inventaris_data.get('jumlah', 1)))
        self.set_combo_value(self.satuan_input, self.inventaris_data.get('satuan', ''))
        self.harga_satuan_input.setValue(float(self.inventaris_data.get('harga_satuan', 0)))
        self.supplier_input.setText(str(self.inventaris_data.get('supplier', '')))
        
        # Tanggal beli
        if self.inventaris_data.get('tanggal_beli'):
            try:
                if isinstance(self.inventaris_data['tanggal_beli'], str):
                    date = QDate.fromString(self.inventaris_data['tanggal_beli'], "yyyy-MM-dd")
                else:
                    date = QDate(self.inventaris_data['tanggal_beli'])
                self.tanggal_beli_input.setDate(date)
            except:
                pass
        
        # Status & Lokasi
        self.set_combo_value(self.kondisi_input, self.inventaris_data.get('kondisi', ''))
        self.lokasi_input.setText(str(self.inventaris_data.get('lokasi', '')))
        self.penanggung_jawab_input.setText(str(self.inventaris_data.get('penanggung_jawab', '')))
        self.keterangan_input.setText(str(self.inventaris_data.get('keterangan', '')))

    def get_data(self):
        """Ambil data dari form"""
        def get_combo_value(combo_box):
            if combo_box.currentIndex() == 0:
                return ''
            return combo_box.currentText()
        
        return {
            'nama_barang': self.nama_barang_input.text().strip(),
            'kode_barang': self.kode_barang_input.text().strip(),
            'kategori': get_combo_value(self.kategori_input),
            'merk': self.merk_input.text().strip(),
            'jumlah': self.jumlah_input.value(),
            'satuan': get_combo_value(self.satuan_input),
            'harga_satuan': self.harga_satuan_input.value(),
            'tanggal_beli': self.tanggal_beli_input.date().toString("yyyy-MM-dd"),
            'supplier': self.supplier_input.text().strip(),
            'kondisi': get_combo_value(self.kondisi_input),
            'lokasi': self.lokasi_input.text().strip(),
            'penanggung_jawab': self.penanggung_jawab_input.text().strip(),
            'keterangan': self.keterangan_input.toPlainText().strip()
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
        self.jumlah_input.setValue(0)
        
        # Set locale Indonesia untuk format pemisah ribuan dengan titik
        locale = QLocale(QLocale.Indonesian, QLocale.Indonesia)
        self.jumlah_input.setLocale(locale)
        
        # Custom behavior untuk select all saat focus
        def on_focus_in(event):
            self.jumlah_input.selectAll()
            QDoubleSpinBox.focusInEvent(self.jumlah_input, event)
        
        self.jumlah_input.focusInEvent = on_focus_in
        
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


class StrukturDialog(QDialog):
    """Dialog untuk menambah/edit struktur kepengurusan gereja."""
    def __init__(self, parent=None, struktur_data=None):
        super().__init__(parent)
        self.struktur_data = struktur_data
        self.setWindowTitle("Tambah Pengurus" if not struktur_data else "Edit Pengurus")
        self.setModal(True)
        self.setFixedSize(500, 500)

        # Setup UI - Single unified form
        layout = QVBoxLayout(self)
        
        # Create single form layout without sub-headers
        self.setup_unified_form(layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Jika edit, isi data
        if struktur_data:
            self.load_data()

    def setup_unified_form(self, layout):
        """Setup single unified form without sub-headers"""
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Nama Lengkap
        self.nama_lengkap_input = QLineEdit()
        self.nama_lengkap_input.setMinimumWidth(350)
        form_layout.addRow("Nama Lengkap*:", self.nama_lengkap_input)
        
        # Jabatan
        self.jabatan_utama_input = QLineEdit()
        self.jabatan_utama_input.setMinimumWidth(350)
        self.jabatan_utama_input.setPlaceholderText("Contoh: Pastor Paroki, Ketua Dewan, Koordinator Liturgi")
        form_layout.addRow("Jabatan*:", self.jabatan_utama_input)
        
        # Wilayah Rohani
        self.wilayah_rohani_input = QLineEdit()
        self.wilayah_rohani_input.setMinimumWidth(350)
        self.wilayah_rohani_input.setPlaceholderText("Contoh: Wilayah Santo Yusuf, Wilayah Santa Maria")
        form_layout.addRow("Wilayah Rohani*:", self.wilayah_rohani_input)
        
        # Status Aktif
        self.status_aktif_input = QComboBox()
        self.status_aktif_input.addItems(["Aktif", "Tidak Aktif", "Cuti"])
        self.status_aktif_input.setCurrentIndex(0)
        self.status_aktif_input.setMinimumWidth(350)
        form_layout.addRow("Status:", self.status_aktif_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setMinimumWidth(350)
        self.email_input.setPlaceholderText("contoh@gereja.com")
        form_layout.addRow("Email:", self.email_input)
        
        # Telepon
        self.telepon_input = QLineEdit()
        self.telepon_input.setMinimumWidth(350)
        self.telepon_input.setPlaceholderText("08123456789")
        form_layout.addRow("Telepon:", self.telepon_input)
        
        # Foto path dengan tombol browse
        foto_container = QWidget()
        foto_layout = QHBoxLayout(foto_container)
        foto_layout.setContentsMargins(0, 0, 0, 0)
        
        self.foto_path_input = QLineEdit()
        self.foto_path_input.setPlaceholderText("Path ke file foto")
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_foto)
        browse_button.setMaximumWidth(80)
        
        foto_layout.addWidget(self.foto_path_input)
        foto_layout.addWidget(browse_button)
        
        form_layout.addRow("Foto:", foto_container)
        
        layout.addLayout(form_layout)
    
    
    def browse_foto(self):
        """Browse untuk memilih foto"""
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getOpenFileName(
            self, "Pilih Foto", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if filename:
            self.foto_path_input.setText(filename)
    
    def setup_placeholder_style(self, combo_box):
        """Setup placeholder style for combo box"""
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
        
        def on_selection_changed():
            if combo_box.currentIndex() == 0:
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
    
    def set_combo_value(self, combo, value):
        """Set combo box value"""
        if not value or str(value).strip() == '':
            combo.setCurrentIndex(0)
            return
            
        index = combo.findText(str(value))
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.setCurrentIndex(0)
    
    def load_data(self):
        """Load data untuk edit"""
        if not self.struktur_data:
            return
        
        # Load all form data
        self.nama_lengkap_input.setText(str(self.struktur_data.get('nama_lengkap', '')))
        self.jabatan_utama_input.setText(str(self.struktur_data.get('jabatan_utama', '')))
        self.wilayah_rohani_input.setText(str(self.struktur_data.get('wilayah_rohani', '')))
        self.set_combo_value(self.status_aktif_input, self.struktur_data.get('status_aktif', 'Aktif'))
        self.email_input.setText(str(self.struktur_data.get('email', '')))
        self.telepon_input.setText(str(self.struktur_data.get('telepon', '')))
        self.foto_path_input.setText(str(self.struktur_data.get('foto_path', '')))

    def get_data(self):
        """Ambil data dari form - hanya field yang diperlukan untuk tabel"""
        return {
            # INFORMASI UTAMA - tampil di tabel (Foto, Nama Lengkap, Jabatan, Wilayah Rohani, Informasi Kontak)
            'nama_lengkap': self.nama_lengkap_input.text().strip(),
            'jabatan_utama': self.jabatan_utama_input.text().strip(),
            'wilayah_rohani': self.wilayah_rohani_input.text().strip(),
            'status_aktif': self.status_aktif_input.currentText(),
            
            # KONTAK & FOTO - tampil di tabel sebagai Informasi Kontak
            'email': self.email_input.text().strip(),
            'telepon': self.telepon_input.text().strip(),
            'foto_path': self.foto_path_input.text().strip(),
            
            # Default values untuk field yang diperlukan oleh sistem
            'gelar_depan': '',
            'gelar_belakang': '',
            'jenis_kelamin': '',
            'tanggal_lahir': '',
            'status_klerus': 'Awam',
            'level_hierarki': 9,
            'bidang_pelayanan': '',
            'tanggal_mulai_jabatan': '',
            'tanggal_berakhir_jabatan': '',
            'alamat': '',
            'deskripsi_tugas': ''
        }