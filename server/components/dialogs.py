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
        
        self.jenis_kelamin_input = QComboBox()
        self.jenis_kelamin_input.addItems(["Pilih Jenis Kelamin", "L", "P"])
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
        self.jenis_pekerjaan_input.addItems(["Pilih pekerjaan", "Pelajar", "Bekerja", "Tidak Bekerja"])
        self.jenis_pekerjaan_input.setCurrentIndex(0)
        self.jenis_pekerjaan_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.jenis_pekerjaan_input)
        self.jenis_pekerjaan_input.currentTextChanged.connect(self.on_pekerjaan_changed)
        
        self.detail_pekerjaan_input = QLineEdit()
        self.detail_pekerjaan_input.setMinimumWidth(300)
        self.detail_pekerjaan_input.setVisible(False)
        
        self.status_menikah_input = QComboBox()
        self.status_menikah_input.addItems(["Pilih status", "Sudah Menikah", "Belum Menikah"])
        self.status_menikah_input.setCurrentIndex(0)
        self.status_menikah_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_menikah_input)
        
        # Legacy fields for compatibility
        self.alamat_input = QLineEdit()
        self.alamat_input.setMinimumWidth(300)
        self.no_telepon_input = QLineEdit()
        self.no_telepon_input.setMinimumWidth(300)
        self.email_input = QLineEdit()
        self.email_input.setMinimumWidth(300)
        
        data_diri_layout.addRow("Wilayah Rohani:", self.wilayah_rohani_input)
        data_diri_layout.addRow("Nama Keluarga:", self.nama_keluarga_input)
        data_diri_layout.addRow("Nama Lengkap:", self.nama_lengkap_input)
        data_diri_layout.addRow("Tempat Lahir:", self.tempat_lahir_input)
        data_diri_layout.addRow("Tanggal Lahir:", self.tanggal_lahir_input)
        data_diri_layout.addRow("Jenis Kelamin:", self.jenis_kelamin_input)
        data_diri_layout.addRow("Hubungan Keluarga:", self.hubungan_keluarga_input)
        data_diri_layout.addRow("Pendidikan Terakhir:", self.pendidikan_terakhir_input)
        data_diri_layout.addRow("Status Menikah:", self.status_menikah_input)
        data_diri_layout.addRow("Jenis Pekerjaan:", self.jenis_pekerjaan_input)
        data_diri_layout.addRow("Detail Pekerjaan:", self.detail_pekerjaan_input)
        data_diri_layout.addRow("Alamat:", self.alamat_input)
        data_diri_layout.addRow("No. Telepon:", self.no_telepon_input)
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
        self.status_keanggotaan_input.addItems(["Pilih Status", "Aktif", "Pindah", "Meninggal Dunia", "Tidak Aktif"])
        self.status_keanggotaan_input.setCurrentIndex(0)
        self.status_keanggotaan_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_keanggotaan_input)
        
        status_layout.addRow("Status Keanggotaan:", self.status_keanggotaan_input)
        
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
    
    def on_pekerjaan_changed(self, text):
        """Handle perubahan jenis pekerjaan"""
        self.detail_pekerjaan_input.setVisible(text == "Tidak Bekerja")
    
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
        self.no_telepon_input.setText(str(self.jemaat_data.get('no_telepon', '')))
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
        self.set_combo_value(self.status_menikah_input, self.jemaat_data.get('status_menikah', 'Belum Menikah'))
        
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
        
        # Status
        self.set_combo_value(self.status_keanggotaan_input, self.jemaat_data.get('status_keanggotaan', 'Aktif'))
    
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
            'jenis_kelamin': get_combo_value(self.jenis_kelamin_input),
            'hubungan_keluarga': get_combo_value(self.hubungan_keluarga_input),
            'pendidikan_terakhir': get_combo_value(self.pendidikan_terakhir_input),
            'jenis_pekerjaan': get_combo_value(self.jenis_pekerjaan_input),
            'detail_pekerjaan': self.detail_pekerjaan_input.text().strip() if self.detail_pekerjaan_input.isVisible() else '',
            'status_menikah': get_combo_value(self.status_menikah_input),
            'alamat': self.alamat_input.text().strip(),
            'no_telepon': self.no_telepon_input.text().strip(),
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
            'status_keanggotaan': get_combo_value(self.status_keanggotaan_input)
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