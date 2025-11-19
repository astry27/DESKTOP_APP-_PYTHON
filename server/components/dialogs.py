# Path: server/components/dialogs.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QComboBox, QGroupBox,
                            QDialogButtonBox, QPushButton, QLabel, QDoubleSpinBox, QWidget, QScrollArea,
                            QMessageBox)
from PyQt5.QtCore import QDate, QTime, QLocale, Qt
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QColor

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
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
        main_layout.addWidget(button_box)
        
        # Jika edit, isi data
        if jemaat_data:
            self.load_data()
    
    def setup_data_diri(self, layout):
        """Setup section Data Diri"""
        data_diri_group = QGroupBox("1. DATA DIRI")
        data_diri_layout = QFormLayout(data_diri_group)

        self.wilayah_rohani_input = QComboBox()
        self.wilayah_rohani_input.addItems([
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
        self.wilayah_rohani_input.setCurrentIndex(0)
        self.wilayah_rohani_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.wilayah_rohani_input)

        self.nama_keluarga_input = QLineEdit()
        self.nama_keluarga_input.setMinimumWidth(300)

        self.no_kk_input = QLineEdit()
        self.no_kk_input.setMinimumWidth(300)
        self.no_kk_input.setPlaceholderText("Nomor Kartu Keluarga")

        self.nama_lengkap_input = QLineEdit()
        self.nama_lengkap_input.setMinimumWidth(300)

        self.nik_input = QLineEdit()
        self.nik_input.setMinimumWidth(300)
        self.nik_input.setPlaceholderText("Nomor Identitas Kependudukan")
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

        self.status_kekatolikan_input = QComboBox()
        self.status_kekatolikan_input.addItems([
            "Pilih Status Kekatolikan", "Kelahiran", "Babtisan", "Penerimaan", "Pindah Agama", "Lainnya"
        ])
        self.status_kekatolikan_input.setCurrentIndex(0)
        self.status_kekatolikan_input.setMinimumWidth(300)
        self.setup_placeholder_style(self.status_kekatolikan_input)
        self.status_kekatolikan_input.currentTextChanged.connect(self.on_status_kekatolikan_changed)

        self.status_kekatolikan_lainnya_input = QLineEdit()
        self.status_kekatolikan_lainnya_input.setMinimumWidth(300)
        self.status_kekatolikan_lainnya_input.setPlaceholderText("Masukkan status kekatolikan lainnya")
        self.status_kekatolikan_lainnya_input.setVisible(False)

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
        data_diri_layout.addRow("No. Kartu Keluarga (KK):", self.no_kk_input)
        data_diri_layout.addRow("Nama Lengkap:", self.nama_lengkap_input)
        data_diri_layout.addRow("NIK (Nomor Identitas Kependudukan):", self.nik_input)
        data_diri_layout.addRow("Tempat Lahir:", self.tempat_lahir_input)
        data_diri_layout.addRow("Tanggal Lahir:", self.tanggal_lahir_input)
        data_diri_layout.addRow("Umur:", self.umur_input)
        data_diri_layout.addRow("Status Kekatolikan:", self.status_kekatolikan_input)
        self.status_kekatolikan_lainnya_label = QLabel("Status Kekatolikan (Lainnya):")
        data_diri_layout.addRow(self.status_kekatolikan_lainnya_label, self.status_kekatolikan_lainnya_input)
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

    def on_status_kekatolikan_changed(self, text):
        """Handle perubahan status kekatolikan"""
        visible = (text == "Lainnya")
        self.status_kekatolikan_lainnya_input.setVisible(visible)
        self.status_kekatolikan_lainnya_label.setVisible(visible)

    def load_data(self):
        """Load data untuk edit"""
        if not self.jemaat_data:
            return

        # Data Diri
        self.set_combo_value(self.wilayah_rohani_input, self.jemaat_data.get('wilayah_rohani', ''))
        self.nama_keluarga_input.setText(str(self.jemaat_data.get('nama_keluarga', '')))
        self.no_kk_input.setText(str(self.jemaat_data.get('no_kk', '')))
        self.nama_lengkap_input.setText(str(self.jemaat_data.get('nama_lengkap', '')))
        self.nik_input.setText(str(self.jemaat_data.get('nik', '')))
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

        # Load status_kekatolikan
        status_kekatolikan = self.jemaat_data.get('status_kekatolikan', '')
        if status_kekatolikan and status_kekatolikan.lower() not in ['pilih status kekatolikan', '', 'none']:
            # Check if it's one of the predefined values
            if status_kekatolikan in ["Kelahiran", "Babtisan", "Penerimaan", "Pindah Agama", "Lainnya"]:
                self.set_combo_value(self.status_kekatolikan_input, status_kekatolikan)
            else:
                # If it's a custom value, set to Lainnya and populate the custom input
                self.set_combo_value(self.status_kekatolikan_input, "Lainnya")
                self.status_kekatolikan_lainnya_input.setText(str(status_kekatolikan))

        # Calculate age after setting birth date
        self.calculate_age()
        
        # Trigger pekerjaan changed to show/hide detail pekerjaan
        self.on_jenis_pekerjaan_changed(self.jenis_pekerjaan_input.currentText())

        # Trigger status_kekatolikan changed to show/hide lainnya field
        self.on_status_kekatolikan_changed(self.status_kekatolikan_input.currentText())
        
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
    
    def _get_status_kekatolikan_value(self):
        """Get status_kekatolikan value, handling Lainnya custom input"""
        current_text = self.status_kekatolikan_input.currentText()
        if current_text == "Lainnya":
            # Return custom input value if Lainnya is selected
            custom_value = self.status_kekatolikan_lainnya_input.text().strip()
            return custom_value if custom_value else ''
        elif current_text == "Pilih Status Kekatolikan":
            return ''
        else:
            return current_text

    def get_data(self):
        """Ambil data dari form"""
        # Helper function to get combo box value (excluding placeholder)
        def get_combo_value(combo_box):
            if combo_box.currentIndex() == 0:  # Placeholder selected
                return ''  # Return empty string for placeholder
            return combo_box.currentText()

        data = {
            # Data Diri
            'wilayah_rohani': get_combo_value(self.wilayah_rohani_input),
            'nama_keluarga': self.nama_keluarga_input.text().strip(),
            'no_kk': self.no_kk_input.text().strip(),
            'nama_lengkap': self.nama_lengkap_input.text().strip(),
            'nik': self.nik_input.text().strip(),
            'tempat_lahir': self.tempat_lahir_input.text().strip(),
            'tanggal_lahir': self.tanggal_lahir_input.date().toString("yyyy-MM-dd"),
            'umur': self.umur_input.text().replace(' tahun', ''),
            'status_kekatolikan': self._get_status_kekatolikan_value(),
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
    def __init__(self, parent=None, kegiatan_data=None):
        super().__init__(parent)
        self.kegiatan_data = kegiatan_data
        self.setWindowTitle("Tambah Kegiatan" if not kegiatan_data else "Edit Kegiatan")
        self.setModal(True)
        self.setFixedSize(550, 700)

        # Setup UI
        layout = QVBoxLayout(self)

        # Scroll area for long form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Form
        form_group = QGroupBox("Data Kegiatan")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(8)

        # Row 1: Nama Kegiatan
        self.nama_input = QLineEdit()
        form_layout.addRow("Nama Kegiatan:", self.nama_input)

        # Row 2: Lokasi
        self.lokasi_input = QLineEdit()
        form_layout.addRow("Lokasi:", self.lokasi_input)

        # Row 3: Tanggal Kegiatan
        self.tanggal_input = QDateEdit()
        self.tanggal_input.setCalendarPopup(True)
        self.tanggal_input.setDate(QDate.currentDate())
        form_layout.addRow("Tanggal Kegiatan:", self.tanggal_input)

        # Row 4: Waktu Kegiatan
        self.waktu_input = QTimeEdit()
        self.waktu_input.setTime(QTime(8, 0))
        form_layout.addRow("Waktu Kegiatan:", self.waktu_input)

        # Row 5: Penanggung Jawab (PIC)
        self.penanggung_jawab_input = QLineEdit()
        form_layout.addRow("Penanggung Jawab:", self.penanggung_jawab_input)

        # Row 6: Kategori
        self.kategori_input = QComboBox()
        self.kategori_input.addItems(['Misa', 'Doa', 'Sosial', 'Pendidikan', 'Ibadah', 'Katekese', 'Rohani', 'Administratif', 'Lainnya'])
        form_layout.addRow("Kategori:", self.kategori_input)

        # Row 7: Status
        self.status_input = QComboBox()
        self.status_input.addItems(['Direncanakan', 'Berlangsung', 'Selesai', 'Dibatalkan'])
        form_layout.addRow("Status:", self.status_input)

        # Row 8: Biaya
        self.biaya_input = QLineEdit()
        self.biaya_input.setPlaceholderText("Masukkan biaya (opsional)")
        form_layout.addRow("Biaya (Rp):", self.biaya_input)

        # Row 9: Sasaran Kegiatan
        self.sasaran_input = QTextEdit()
        self.sasaran_input.setMaximumHeight(70)
        self.sasaran_input.setPlaceholderText("Sasaran/target kegiatan (opsional)")
        form_layout.addRow("Sasaran Kegiatan:", self.sasaran_input)

        # Row 10: Keterangan
        self.keterangan_input = QTextEdit()
        self.keterangan_input.setMaximumHeight(70)
        form_layout.addRow("Keterangan:", self.keterangan_input)

        scroll_layout.addWidget(form_group)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
        layout.addWidget(button_box)

        # Jika edit, isi data
        if kegiatan_data:
            self.load_data()
    
    def load_data(self):
        """Load data untuk edit"""
        if self.kegiatan_data:
            # Basic fields
            self.nama_input.setText(str(self.kegiatan_data.get('nama_kegiatan', '')))
            self.lokasi_input.setText(str(self.kegiatan_data.get('lokasi', '')))
            self.penanggung_jawab_input.setText(str(self.kegiatan_data.get('penanggung_jawab', '')))
            self.sasaran_input.setPlainText(str(self.kegiatan_data.get('sasaran_kegiatan', '')))
            self.keterangan_input.setPlainText(str(self.kegiatan_data.get('keterangan', '')))

            # Set biaya
            biaya = self.kegiatan_data.get('biaya', 0)
            self.biaya_input.setText(str(int(biaya)) if biaya else '')

            # Set kategori
            kategori = self.kegiatan_data.get('kategori', 'Lainnya')
            index = self.kategori_input.findText(kategori)
            if index >= 0:
                self.kategori_input.setCurrentIndex(index)

            # Set status
            status = self.kegiatan_data.get('status', 'Direncanakan')
            index = self.status_input.findText(status)
            if index >= 0:
                self.status_input.setCurrentIndex(index)

            # Handle tanggal kegiatan
            if self.kegiatan_data.get('tanggal_kegiatan'):
                try:
                    if isinstance(self.kegiatan_data['tanggal_kegiatan'], str):
                        date = QDate.fromString(self.kegiatan_data['tanggal_kegiatan'], "yyyy-MM-dd")
                    else:
                        date = QDate(self.kegiatan_data['tanggal_kegiatan'])
                    self.tanggal_input.setDate(date)
                except:
                    pass

            # Handle waktu kegiatan
            if self.kegiatan_data.get('waktu_kegiatan'):
                try:
                    if isinstance(self.kegiatan_data['waktu_kegiatan'], str):
                        time = QTime.fromString(self.kegiatan_data['waktu_kegiatan'], "hh:mm:ss")
                    else:
                        time = QTime(self.kegiatan_data['waktu_kegiatan'])
                    self.waktu_input.setTime(time)
                except:
                    pass
    
    def get_data(self):
        """Ambil data dari form sesuai struktur database kegiatan"""
        # Parse biaya as float, default to 0 if empty
        biaya_str = self.biaya_input.text().strip()
        try:
            biaya = float(biaya_str) if biaya_str else 0
        except ValueError:
            biaya = 0

        return {
            'nama_kegiatan': self.nama_input.text().strip(),
            'lokasi': self.lokasi_input.text().strip(),
            'tanggal_kegiatan': self.tanggal_input.date().toString("yyyy-MM-dd"),
            'waktu_kegiatan': self.waktu_input.time().toString("hh:mm:ss"),
            'penanggung_jawab': self.penanggung_jawab_input.text().strip(),
            'kategori': self.kategori_input.currentText(),
            'status': self.status_input.currentText(),
            'biaya': biaya,
            'sasaran_kegiatan': self.sasaran_input.toPlainText().strip(),
            'keterangan': self.keterangan_input.toPlainText().strip()
        }

class PengumumanDialog(QDialog):
    """Dialog untuk menambah/edit pengumuman"""
    def __init__(self, parent=None, pengumuman_data=None):
        super().__init__(parent)
        self.pengumuman_data = pengumuman_data
        self.setWindowTitle("Tambah Pengumuman" if not pengumuman_data else "Edit Pengumuman")
        self.setModal(True)
        self.setFixedSize(500, 520)  # Increased height for new field

        # Setup UI
        layout = QVBoxLayout(self)

        # Form
        form_group = QGroupBox("Data Pengumuman")
        form_layout = QFormLayout(form_group)

        # 1. Tanggal - auto filled from created_at (read-only display)
        self.tanggal_input = QLineEdit()
        from PyQt5.QtCore import QDate
        current_date = QDate.currentDate()
        # Format: Hari, dd NamaBulan yyyy
        day_names = {
            1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis',
            5: 'Jumat', 6: 'Sabtu', 7: 'Minggu'
        }
        month_names = {
            1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
            5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
        }
        day_name = day_names.get(current_date.dayOfWeek(), '')
        day_num = current_date.day()
        month_name = month_names.get(current_date.month(), '')
        year_num = current_date.year()
        date_display = f"{day_name}, {day_num:02d} {month_name} {year_num}"
        self.tanggal_input.setText(date_display)
        self.tanggal_input.setReadOnly(True)
        self.tanggal_input.setStyleSheet("background-color: #f0f0f0; font-weight: bold; color: #2c3e50;")

        # 2. Pembuat Pengumuman (auto-filled, read-only)
        self.pembuat_input = QLineEdit()
        self.pembuat_input.setPlaceholderText("Otomatis terisi dari user login")
        self.pembuat_input.setReadOnly(True)
        self.pembuat_input.setStyleSheet("background-color: #f0f0f0;")

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

        # 6. Penanggung Jawab
        self.penanggung_jawab_input = QLineEdit()
        self.penanggung_jawab_input.setPlaceholderText("Nama penanggung jawab (opsional)")

        # Add form rows in the correct order matching table layout
        # Table columns: Tanggal, Pembuat, Sasaran/Tujuan, Judul Pengumuman, Isi Pengumuman, Penanggung Jawab
        form_layout.addRow("Tanggal:", self.tanggal_input)
        form_layout.addRow("Pembuat:", self.pembuat_input)
        form_layout.addRow("Sasaran/Tujuan:", self.sasaran_input)
        form_layout.addRow("Judul Pengumuman:", self.judul_input)
        form_layout.addRow("Isi Pengumuman:", self.isi_input)
        form_layout.addRow("Penanggung Jawab:", self.penanggung_jawab_input)
        
        layout.addWidget(form_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
        layout.addWidget(button_box)
        
        # Jika edit, isi data
        if pengumuman_data:
            self.load_data()
    
    def load_data(self):
        """Load data untuk edit"""
        if self.pengumuman_data:
            # Load judul
            self.judul_input.setText(str(self.pengumuman_data.get('judul', '')))

            # Load isi
            self.isi_input.setText(str(self.pengumuman_data.get('isi', '')))

            # Load pembuat (read-only)
            pembuat = (self.pengumuman_data.get('pembuat') or
                      self.pengumuman_data.get('dibuat_oleh_nama') or
                      self.pengumuman_data.get('created_by_name') or
                      self.pengumuman_data.get('admin_name') or 'Administrator')
            self.pembuat_input.setText(str(pembuat))

            # Load sasaran
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

            # Load penanggung_jawab
            penanggung_jawab = self.pengumuman_data.get('penanggung_jawab', pembuat)
            self.penanggung_jawab_input.setText(str(penanggung_jawab))

            # Handle tanggal display - use created_at for display
            tanggal_value = (self.pengumuman_data.get('created_at') or
                           self.pengumuman_data.get('tanggal') or
                           self.pengumuman_data.get('tanggal_mulai'))

            if tanggal_value:
                try:
                    from PyQt5.QtCore import QDate
                    import datetime

                    # Parse the date
                    if hasattr(tanggal_value, 'date'):
                        date_obj = tanggal_value.date()
                    elif isinstance(tanggal_value, str):
                        date_part = tanggal_value.split(' ')[0] if ' ' in tanggal_value else tanggal_value
                        date_obj = datetime.datetime.strptime(date_part, '%Y-%m-%d').date()
                    else:
                        date_obj = tanggal_value

                    # Format Indonesian date
                    day_names = {
                        1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis',
                        5: 'Jumat', 6: 'Sabtu', 7: 'Minggu'
                    }
                    month_names = {
                        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
                        5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
                        9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
                    }

                    day_num = date_obj.isoweekday()  # 1=Monday, 7=Sunday
                    day_name = day_names.get(day_num, '')
                    month_name = month_names.get(date_obj.month, '')
                    date_display = f"{day_name}, {date_obj.day:02d} {month_name} {date_obj.year}"
                    self.tanggal_input.setText(date_display)
                except:
                    pass  # Keep current date display if parsing fails
    
    def get_data(self):
        """Ambil data dari form - sesuai dengan struktur tabel baru"""
        # Get penanggung_jawab, default to pembuat if empty
        penanggung_jawab = self.penanggung_jawab_input.text().strip()
        pembuat = self.pembuat_input.text().strip()
        if not penanggung_jawab:
            penanggung_jawab = pembuat if pembuat else 'Administrator'

        return {
            # Required fields matching new table structure
            'judul': self.judul_input.text().strip(),
            'isi': self.isi_input.toPlainText().strip(),
            'sasaran': self.sasaran_input.currentText().strip(),
            'pembuat': pembuat,
            'penanggung_jawab': penanggung_jawab,
            'is_active': True  # Default active
        }

class AsetDialog(QDialog):
    """Dialog untuk menambah/edit data aset dengan all fields."""
    def __init__(self, parent=None, aset_data=None):
        super().__init__(parent)
        self.aset_data = aset_data
        self.setWindowTitle("Tambah Aset" if not aset_data else "Edit Aset")
        self.setModal(True)
        self.setFixedSize(600, 700)

        # Setup UI with scroll area for many fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)

        # Setup form
        self.setup_aset_form(layout)

        scroll.setWidget(scroll_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
        main_layout.addWidget(button_box)

        # Jika edit, isi data
        if aset_data:
            self.load_data()

    def setup_aset_form(self, layout):
        """Setup form untuk aset dengan semua field yang diperlukan"""
        form_group = QGroupBox("Data Aset")
        form_layout = QFormLayout(form_group)

        # Set proper form layout spacing
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setVerticalSpacing(8)
        form_layout.setHorizontalSpacing(10)

        # 1. Kode Aset
        kode_label = QLabel("Kode Aset:")
        kode_label.setMinimumWidth(140)
        self.kode_aset_input = QLineEdit()
        self.kode_aset_input.setMinimumWidth(350)
        self.kode_aset_input.setPlaceholderText("Contoh: AST-001")
        form_layout.addRow(kode_label, self.kode_aset_input)

        # 2. Nama Aset
        nama_label = QLabel("Nama Aset:")
        nama_label.setMinimumWidth(140)
        self.nama_aset_input = QLineEdit()
        self.nama_aset_input.setMinimumWidth(350)
        self.nama_aset_input.setPlaceholderText("Masukkan nama aset")
        form_layout.addRow(nama_label, self.nama_aset_input)

        # 3. Jenis Aset
        jenis_label = QLabel("Jenis Aset:")
        jenis_label.setMinimumWidth(140)
        self.jenis_aset_input = QComboBox()
        self.jenis_aset_input.addItems(["Pilih Jenis", "Bergerak", "Tidak Bergerak"])
        self.jenis_aset_input.setCurrentIndex(0)
        self.jenis_aset_input.setMinimumWidth(350)
        self.setup_placeholder_style(self.jenis_aset_input)
        form_layout.addRow(jenis_label, self.jenis_aset_input)

        # 4. Kategori
        kategori_label = QLabel("Kategori:")
        kategori_label.setMinimumWidth(140)
        self.kategori_input = QComboBox()
        self.kategori_input.addItems(["Pilih Kategori", "Tanah", "Bangunan", "Liturgi", "Elektronik", "Kendaraan", "Furniture", "Lainnya"])
        self.kategori_input.setCurrentIndex(0)
        self.kategori_input.setMinimumWidth(350)
        self.setup_placeholder_style(self.kategori_input)
        form_layout.addRow(kategori_label, self.kategori_input)

        # 5. Merk/Tipe (Optional)
        merk_label = QLabel("Merk/Tipe (opsional):")
        merk_label.setMinimumWidth(140)
        self.merk_tipe_input = QLineEdit()
        self.merk_tipe_input.setMinimumWidth(350)
        self.merk_tipe_input.setPlaceholderText("Contoh: Samsung, Toyota, dll")
        form_layout.addRow(merk_label, self.merk_tipe_input)

        # 6. Tahun Perolehan
        tahun_label = QLabel("Tahun Perolehan:")
        tahun_label.setMinimumWidth(140)
        self.tahun_perolehan_input = QDoubleSpinBox()
        self.tahun_perolehan_input.setRange(1900, 2100)
        self.tahun_perolehan_input.setValue(2025)
        self.tahun_perolehan_input.setDecimals(0)
        self.tahun_perolehan_input.setMinimumWidth(350)
        form_layout.addRow(tahun_label, self.tahun_perolehan_input)

        # 7. Sumber Perolehan
        sumber_label = QLabel("Sumber Perolehan:")
        sumber_label.setMinimumWidth(140)
        self.sumber_perolehan_input = QComboBox()
        self.sumber_perolehan_input.addItems(["Pilih Sumber", "Pembelian", "Hibah", "Sumbangan Umat", "Donatur", "Bantuan Keuskupan", "Lainnya"])
        self.sumber_perolehan_input.setCurrentIndex(0)
        self.sumber_perolehan_input.setMinimumWidth(350)
        self.setup_placeholder_style(self.sumber_perolehan_input)
        form_layout.addRow(sumber_label, self.sumber_perolehan_input)

        # 8. Nilai (Rp)
        nilai_label = QLabel("Nilai (Rp):")
        nilai_label.setMinimumWidth(140)
        self.nilai_input = QDoubleSpinBox()
        self.nilai_input.setRange(0, 999_999_999_999)
        self.nilai_input.setGroupSeparatorShown(True)
        self.nilai_input.setValue(0)
        self.nilai_input.setMinimumWidth(350)
        locale = QLocale(QLocale.Indonesian, QLocale.Indonesia)
        self.nilai_input.setLocale(locale)
        form_layout.addRow(nilai_label, self.nilai_input)

        # 9. Kondisi
        kondisi_label = QLabel("Kondisi:")
        kondisi_label.setMinimumWidth(140)
        self.kondisi_input = QComboBox()
        self.kondisi_input.addItems(["Baik", "Rusak Ringan", "Rusak Berat", "Tidak Terpakai"])
        self.kondisi_input.setCurrentIndex(0)
        self.kondisi_input.setMinimumWidth(350)
        form_layout.addRow(kondisi_label, self.kondisi_input)

        # 10. Lokasi
        lokasi_label = QLabel("Lokasi:")
        lokasi_label.setMinimumWidth(140)
        self.lokasi_input = QComboBox()
        self.lokasi_input.addItems(["Pilih Lokasi", "Gereja Utama", "Aula", "Pastoran", "Sekretariat", "Gudang", "Lainnya"])
        self.lokasi_input.setCurrentIndex(0)
        self.lokasi_input.setMinimumWidth(350)
        self.setup_placeholder_style(self.lokasi_input)
        form_layout.addRow(lokasi_label, self.lokasi_input)

        # 11. Status
        status_label = QLabel("Status:")
        status_label.setMinimumWidth(140)
        self.status_input = QComboBox()
        self.status_input.addItems(["Aktif", "Tidak Aktif", "Dalam Perbaikan", "Dijual/Dihapus"])
        self.status_input.setCurrentIndex(0)
        self.status_input.setMinimumWidth(350)
        form_layout.addRow(status_label, self.status_input)

        # 12. Penanggung Jawab
        pj_label = QLabel("Penanggung Jawab:")
        pj_label.setMinimumWidth(140)
        self.penanggung_jawab_input = QLineEdit()
        self.penanggung_jawab_input.setMinimumWidth(350)
        self.penanggung_jawab_input.setPlaceholderText("Masukkan nama penanggung jawab")
        form_layout.addRow(pj_label, self.penanggung_jawab_input)

        # 13. Keterangan (Text Area)
        keterangan_label = QLabel("Keterangan:")
        keterangan_label.setMinimumWidth(140)
        self.keterangan_input = QTextEdit()
        self.keterangan_input.setMinimumWidth(350)
        self.keterangan_input.setMinimumHeight(80)
        self.keterangan_input.setPlaceholderText("Masukkan keterangan tambahan")
        form_layout.addRow(keterangan_label, self.keterangan_input)

        layout.addWidget(form_group)

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
            # Check if any placeholder combo has index 0 (placeholder selected)
            if combo_box.currentIndex() == 0 and combo_box in [self.jenis_aset_input, self.kategori_input, self.sumber_perolehan_input, self.lokasi_input]:
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
            combo.setCurrentIndex(0)  # Set to placeholder
            return

        index = combo.findText(str(value))
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.setCurrentIndex(0)

    def load_data(self):
        """Load data untuk edit"""
        if not self.aset_data:
            return

        # Load semua field dari aset_data
        self.kode_aset_input.setText(str(self.aset_data.get('kode_aset', '')))
        self.nama_aset_input.setText(str(self.aset_data.get('nama_aset', '')))
        self.set_combo_value(self.jenis_aset_input, self.aset_data.get('jenis_aset', ''))
        self.set_combo_value(self.kategori_input, self.aset_data.get('kategori', ''))
        self.merk_tipe_input.setText(str(self.aset_data.get('merk_tipe', '')))
        self.tahun_perolehan_input.setValue(float(self.aset_data.get('tahun_perolehan', 2025)))
        self.set_combo_value(self.sumber_perolehan_input, self.aset_data.get('sumber_perolehan', ''))
        self.nilai_input.setValue(float(self.aset_data.get('nilai', 0)))
        self.set_combo_value(self.kondisi_input, self.aset_data.get('kondisi', 'Baik'))
        self.set_combo_value(self.lokasi_input, self.aset_data.get('lokasi', ''))
        self.set_combo_value(self.status_input, self.aset_data.get('status', 'Aktif'))
        self.penanggung_jawab_input.setText(str(self.aset_data.get('penanggung_jawab', '')))
        self.keterangan_input.setText(str(self.aset_data.get('keterangan', '')))

    def get_data(self):
        """Ambil data dari form - semua field aset"""
        def get_combo_value(combo_box):
            if combo_box.currentIndex() == 0:
                return ''  # Return empty for placeholder
            return combo_box.currentText()

        return {
            'kode_aset': self.kode_aset_input.text().strip(),
            'nama_aset': self.nama_aset_input.text().strip(),
            'jenis_aset': get_combo_value(self.jenis_aset_input),
            'kategori': get_combo_value(self.kategori_input),
            'merk_tipe': self.merk_tipe_input.text().strip(),
            'tahun_perolehan': int(self.tahun_perolehan_input.value()),
            'sumber_perolehan': get_combo_value(self.sumber_perolehan_input),
            'nilai': self.nilai_input.value(),
            'kondisi': self.kondisi_input.currentText(),
            'lokasi': get_combo_value(self.lokasi_input),
            'status': self.status_input.currentText(),
            'penanggung_jawab': self.penanggung_jawab_input.text().strip(),
            'keterangan': self.keterangan_input.toPlainText().strip()
        }


# Keep InventarisDialog as alias for backward compatibility
InventarisDialog = AsetDialog


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

        self.keterangan_input = QLineEdit()
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
        
        form_layout.addRow("Kategori:", self.kategori_input)
        form_layout.addRow("Tanggal:", self.tanggal_input)
        form_layout.addRow("Keterangan:", self.keterangan_input)
        form_layout.addRow("Sub-Kategori:", self.sub_kategori_input)
        form_layout.addRow("Jumlah (Rp):", self.jumlah_input)
        
        layout.addWidget(form_group)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
        layout.addWidget(button_box)

    def get_data(self):
        """Ambil data dari form."""
        return {
            'kategori': self.kategori_input.text(),
            'tanggal': self.tanggal_input.date().toString("yyyy-MM-dd"),
            'keterangan': self.keterangan_input.text().strip(),
            'sub_kategori': self.sub_kategori_input.text().strip(),
            'jumlah': self.jumlah_input.value()
        }


class StrukturDialog(QDialog):
    """Dialog untuk menambah/edit struktur kepengurusan gereja."""
    def __init__(self, parent=None, struktur_data=None):
        super().__init__(parent)
        self.struktur_data = struktur_data
        self.parent_component = parent  # Store reference to parent component
        self.uploaded_photo_path = None  # Store server photo path
        self.setWindowTitle("Tambah Pengurus" if not struktur_data else "Edit Pengurus")
        self.setModal(True)
        self.setFixedSize(500, 500)

        # Setup UI - Single unified form
        layout = QVBoxLayout(self)
        
        # Create single form layout without sub-headers
        self.setup_unified_form(layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
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

        # Jenis Kelamin
        self.jenis_kelamin_input = QComboBox()
        self.jenis_kelamin_input.addItems(["Pilih Jenis Kelamin", "Laki-laki", "Perempuan"])
        self.jenis_kelamin_input.setCurrentIndex(0)
        self.jenis_kelamin_input.setMinimumWidth(350)
        form_layout.addRow("Jenis Kelamin:", self.jenis_kelamin_input)

        # Jabatan
        self.jabatan_utama_input = QLineEdit()
        self.jabatan_utama_input.setMinimumWidth(350)
        self.jabatan_utama_input.setPlaceholderText("Contoh: Pastor Paroki, Ketua Dewan, Koordinator Liturgi")
        form_layout.addRow("Jabatan*:", self.jabatan_utama_input)
        
        # Wilayah Rohani
        self.wilayah_rohani_input = QComboBox()
        self.wilayah_rohani_input.addItems([
            "Pilih Wilayah Rohani", "ST. YOHANES BAPTISTA DE LA SALLE", "ST. ALOYSIUS GONZAGA",
            "ST. GREGORIUS AGUNG", "ST. DOMINICO SAVIO", "ST. THOMAS AQUINAS", "ST. ALBERTUS AGUNG",
            "ST. BONAVENTURA", "STA. KATARINA DARI SIENA", "STA. SISILIA", "ST. BLASIUS",
            "ST. CAROLUS BORROMEUS", "ST. BONIFASIUS", "ST. CORNELIUS", "STA. BRIGITTA",
            "ST. IGNASIUS DARI LOYOLA", "ST. PIUS X", "STA. AGNES", "ST. AGUSTINUS",
            "STA. FAUSTINA", "ST. YOHANES MARIA VIANNEY", "STA. MARIA GORETTI", "STA. PERPETUA",
            "ST. LUKAS", "STA. SKOLASTIKA", "STA. THERESIA DARI AVILLA", "ST. VINCENTIUS A PAULO"
        ])
        self.wilayah_rohani_input.setCurrentIndex(0)
        self.wilayah_rohani_input.setMinimumWidth(350)
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

        # Periode
        self.periode_input = QLineEdit()
        self.periode_input.setMinimumWidth(350)
        self.periode_input.setPlaceholderText("2024-2027")
        self.periode_input.setMaxLength(9)  # Format: YYYY-YYYY (9 karakter)
        form_layout.addRow("Periode:", self.periode_input)

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
        """Browse untuk memilih foto dan upload ke server"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
        from PyQt5.QtCore import Qt
        
        filename, _ = QFileDialog.getOpenFileName(
            self, "Pilih Foto", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if filename:
            # Show progress dialog
            progress = QProgressDialog("Mengupload foto ke server...", "Batal", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(10)
            
            try:
                # Get database manager from parent component
                if hasattr(self.parent_component, 'db_manager') and self.parent_component.db_manager:
                    db_manager = self.parent_component.db_manager
                    
                    progress.setValue(30)
                    
                    # Upload foto ke server
                    success, result = db_manager.upload_struktur_photo_new(filename)
                    progress.setValue(80)
                    
                    if success:
                        # Store server photo path
                        self.uploaded_photo_path = result.get('photo_path', '')
                        photo_url = result.get('photo_url', '')
                        
                        # Update display with server path/URL
                        self.foto_path_input.setText(f"Server: {photo_url}")
                        self.foto_path_input.setToolTip(f"File uploaded to server: {self.uploaded_photo_path}")
                        
                        progress.setValue(100)
                        QMessageBox.information(self, "Sukses", "Foto berhasil diupload ke server!")
                    else:
                        progress.setValue(100)
                        QMessageBox.warning(self, "Error Upload", f"Gagal upload foto ke server:\n{result}")
                        # Fallback to local path
                        self.foto_path_input.setText(filename)
                        self.uploaded_photo_path = None
                else:
                    progress.setValue(100)
                    QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    # Fallback to local path
                    self.foto_path_input.setText(filename)
                    self.uploaded_photo_path = None
                    
            except Exception as e:
                progress.setValue(100)
                QMessageBox.critical(self, "Error", f"Error saat upload foto:\n{str(e)}")
                # Fallback to local path
                self.foto_path_input.setText(filename)
                self.uploaded_photo_path = None
            
            finally:
                progress.close()
    
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
        self.set_combo_value(self.jenis_kelamin_input, self.struktur_data.get('jenis_kelamin', ''))
        self.jabatan_utama_input.setText(str(self.struktur_data.get('jabatan_utama', '')))
        self.set_combo_value(self.wilayah_rohani_input, self.struktur_data.get('wilayah_rohani', ''))
        self.set_combo_value(self.status_aktif_input, self.struktur_data.get('status_aktif', 'Aktif'))
        self.email_input.setText(str(self.struktur_data.get('email', '')))
        self.telepon_input.setText(str(self.struktur_data.get('telepon', '')))
        self.periode_input.setText(str(self.struktur_data.get('periode', '')))
        self.foto_path_input.setText(str(self.struktur_data.get('foto_path', '')))

    def get_data(self):
        """Ambil data dari form - hanya field yang diperlukan untuk tabel"""
        # Get jenis kelamin value
        jenis_kelamin_value = self.jenis_kelamin_input.currentText()
        if jenis_kelamin_value == "Pilih Jenis Kelamin":
            jenis_kelamin_value = None  # Use NULL if not selected

        # Get wilayah rohani value
        wilayah_rohani_value = self.wilayah_rohani_input.currentText()
        if wilayah_rohani_value == "Pilih Wilayah Rohani":
            wilayah_rohani_value = None  # Use NULL if not selected

        return {
            # INFORMASI UTAMA - tampil di tabel (Foto, Nama Lengkap, Jabatan, Wilayah Rohani, Informasi Kontak)
            'nama_lengkap': self.nama_lengkap_input.text().strip(),
            'jenis_kelamin': jenis_kelamin_value,
            'jabatan_utama': self.jabatan_utama_input.text().strip(),
            'wilayah_rohani': wilayah_rohani_value,
            'status_aktif': self.status_aktif_input.currentText(),

            # KONTAK & FOTO - tampil di tabel sebagai Informasi Kontak
            'email': self.email_input.text().strip(),
            'telepon': self.telepon_input.text().strip(),
            'periode': self.periode_input.text().strip(),
            'foto_path': self.uploaded_photo_path or self.foto_path_input.text().strip()
        }


class KategorialDialog(QDialog):
    """Dialog untuk menambah/edit pengurus komunitas kategorial."""
    def __init__(self, parent=None, kategorial_data=None):
        super().__init__(parent)
        self.kategorial_data = kategorial_data
        self.parent_component = parent
        self.uploaded_photo_path = None
        self.setWindowTitle("Tambah Pengurus Kategorial" if not kategorial_data else "Edit Pengurus Kategorial")
        self.setModal(True)
        self.setFixedSize(550, 650)

        # Setup UI
        layout = QVBoxLayout(self)

        # Create form with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Kelompok Kategorial with grouped options (simplified style with non-selectable headers)
        self.kelompok_kategorial_input = QComboBox()
        self.kelompok_kategorial_input.setMinimumWidth(350)

        # Use QStandardItemModel to make headers non-selectable
        model = QStandardItemModel()

        # Placeholder
        placeholder_item = QStandardItem("Pilih Kelompok Kategorial")
        model.appendRow(placeholder_item)

        # Section 1: Pusat Paroki (non-selectable header)
        header1 = QStandardItem("─── Pusat Paroki ───")
        header1.setSelectable(False)
        header1.setEnabled(False)
        header1.setForeground(QColor(150, 150, 150))  # Gray out the header
        model.appendRow(header1)

        # Items in Pusat Paroki
        pusat_items = ["OMK", "KBK", "KIK", "Lansia", "Legio Mariae", "Legio Christi"]
        for item_text in pusat_items:
            item = QStandardItem(item_text)
            model.appendRow(item)

        # Section 2: Kemasyarakatan (non-selectable header)
        header2 = QStandardItem("─── Kemasyarakatan ───")
        header2.setSelectable(False)
        header2.setEnabled(False)
        header2.setForeground(QColor(150, 150, 150))  # Gray out the header
        model.appendRow(header2)

        # Items in Kemasyarakatan
        kemasyarakatan_items = ["WKRI", "Pemuda Katolik", "KMK", "PMKRI"]
        for item_text in kemasyarakatan_items:
            item = QStandardItem(item_text)
            model.appendRow(item)

        # Lainnya option
        lainnya_item = QStandardItem("Lainnya")
        model.appendRow(lainnya_item)

        self.kelompok_kategorial_input.setModel(model)
        self.kelompok_kategorial_input.setCurrentIndex(0)
        self.kelompok_kategorial_input.currentIndexChanged.connect(self.on_kelompok_changed)

        form_layout.addRow("Kelompok Kategorial*:", self.kelompok_kategorial_input)

        # Field untuk "Lainnya"
        self.kelompok_lainnya_input = QLineEdit()
        self.kelompok_lainnya_input.setMinimumWidth(350)
        self.kelompok_lainnya_input.setPlaceholderText("Masukkan nama kelompok kategorial lain")
        self.kelompok_lainnya_input.setVisible(False)
        form_layout.addRow("Kelompok Lainnya:", self.kelompok_lainnya_input)

        # Nama Lengkap
        self.nama_lengkap_input = QLineEdit()
        self.nama_lengkap_input.setMinimumWidth(350)
        form_layout.addRow("Nama Lengkap*:", self.nama_lengkap_input)

        # Jenis Kelamin
        self.jenis_kelamin_input = QComboBox()
        self.jenis_kelamin_input.addItems([
            "Pilih Jenis Kelamin",
            "Laki-laki",
            "Perempuan"
        ])
        self.jenis_kelamin_input.setCurrentIndex(0)
        self.jenis_kelamin_input.setMinimumWidth(350)
        self.setup_placeholder_style(self.jenis_kelamin_input)
        form_layout.addRow("Jenis Kelamin:", self.jenis_kelamin_input)

        # Jabatan
        self.jabatan_input = QLineEdit()
        self.jabatan_input.setMinimumWidth(350)
        self.jabatan_input.setPlaceholderText("Contoh: Ketua, Sekretaris, Bendahara")
        form_layout.addRow("Jabatan:", self.jabatan_input)

        # No. HP
        self.no_hp_input = QLineEdit()
        self.no_hp_input.setMinimumWidth(350)
        self.no_hp_input.setPlaceholderText("08123456789")
        form_layout.addRow("No. HP:", self.no_hp_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setMinimumWidth(350)
        self.email_input.setPlaceholderText("email@example.com")
        form_layout.addRow("Email:", self.email_input)

        # Alamat
        self.alamat_input = QTextEdit()
        self.alamat_input.setMinimumWidth(350)
        self.alamat_input.setMinimumHeight(80)
        self.alamat_input.setMaximumHeight(100)
        self.alamat_input.setPlaceholderText("Alamat lengkap")
        form_layout.addRow("Alamat:", self.alamat_input)

        # Wilayah Rohani
        self.wilayah_rohani_input = QComboBox()
        self.wilayah_rohani_input.addItems([
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
        self.wilayah_rohani_input.setCurrentIndex(0)
        self.wilayah_rohani_input.setMinimumWidth(350)
        self.setup_placeholder_style(self.wilayah_rohani_input)
        form_layout.addRow("Wilayah Rohani:", self.wilayah_rohani_input)

        # Masa Jabatan
        self.masa_jabatan_input = QLineEdit()
        self.masa_jabatan_input.setMinimumWidth(350)
        self.masa_jabatan_input.setPlaceholderText("Contoh: 2023-2025")
        form_layout.addRow("Masa Jabatan:", self.masa_jabatan_input)

        # Status
        self.status_input = QComboBox()
        self.status_input.addItems(["Aktif", "Tidak Aktif"])
        self.status_input.setCurrentIndex(0)
        self.status_input.setMinimumWidth(350)
        form_layout.addRow("Status:", self.status_input)

        # Foto - with Browse button (matching DPP style)
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

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
        layout.addWidget(button_box)

        # Load data jika edit
        if kategorial_data:
            self.load_data()

    def on_kelompok_changed(self):
        """Handle perubahan pilihan kelompok kategorial"""
        current_text = self.kelompok_kategorial_input.currentText().strip()
        # Show "Lainnya" field only if "Lainnya" option is selected
        if current_text == "Lainnya":
            self.kelompok_lainnya_input.setVisible(True)
        else:
            self.kelompok_lainnya_input.setVisible(False)

    def browse_foto(self):
        """Browse untuk memilih foto dan upload ke server"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
        from PyQt5.QtCore import Qt

        filename, _ = QFileDialog.getOpenFileName(
            self, "Pilih Foto", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if filename:
            progress = QProgressDialog("Mengupload foto ke server...", "Batal", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(10)

            try:
                if hasattr(self.parent_component, 'db_manager') and self.parent_component.db_manager:
                    db_manager = self.parent_component.db_manager

                    progress.setValue(30)

                    # Upload foto ke server
                    success, result = db_manager.upload_struktur_photo_new(filename)
                    progress.setValue(80)

                    if success:
                        self.uploaded_photo_path = result.get('photo_path', '')
                        photo_url = result.get('photo_url', '')

                        self.foto_path_input.setText(f"Server: {photo_url}")
                        self.foto_path_input.setToolTip(f"File uploaded to server: {self.uploaded_photo_path}")

                        progress.setValue(100)
                        QMessageBox.information(self, "Sukses", "Foto berhasil diupload ke server!")
                    else:
                        progress.setValue(100)
                        QMessageBox.warning(self, "Error Upload", f"Gagal upload foto ke server:\n{result}")
                        self.foto_path_input.setText(filename)
                        self.uploaded_photo_path = None
                else:
                    progress.setValue(100)
                    QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    self.foto_path_input.setText(filename)
                    self.uploaded_photo_path = None

            except Exception as e:
                progress.setValue(100)
                QMessageBox.critical(self, "Error", f"Error saat upload foto:\n{str(e)}")
                self.foto_path_input.setText(filename)
                self.uploaded_photo_path = None

            finally:
                progress.close()

    def set_combo_value(self, combo, value):
        """Set combo box value"""
        # Find the index by text
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
            return

        # Fallback to placeholder if not found
        combo.setCurrentIndex(0)

    def load_data(self):
        """Load data kategorial untuk edit"""
        self.nama_lengkap_input.setText(str(self.kategorial_data.get('nama_lengkap', '')))

        # Jenis Kelamin
        jenis_kelamin = self.kategorial_data.get('jenis_kelamin', '')
        self.set_combo_value(self.jenis_kelamin_input, jenis_kelamin)

        kelompok = self.kategorial_data.get('kelompok_kategorial', '')
        self.set_combo_value(self.kelompok_kategorial_input, kelompok)

        if kelompok == 'Lainnya':
            self.kelompok_lainnya_input.setText(str(self.kategorial_data.get('kelompok_kategorial_lainnya', '')))
            self.kelompok_lainnya_input.setVisible(True)

        self.jabatan_input.setText(str(self.kategorial_data.get('jabatan', '')))
        self.no_hp_input.setText(str(self.kategorial_data.get('no_hp', '')))
        self.email_input.setText(str(self.kategorial_data.get('email', '')))
        self.alamat_input.setText(str(self.kategorial_data.get('alamat', '')))

        wilayah = self.kategorial_data.get('wilayah_rohani', '')
        self.set_combo_value(self.wilayah_rohani_input, wilayah)

        self.masa_jabatan_input.setText(str(self.kategorial_data.get('masa_jabatan', '')))
        self.set_combo_value(self.status_input, self.kategorial_data.get('status', 'Aktif'))
        self.foto_path_input.setText(str(self.kategorial_data.get('foto_path', '')))

    def get_data(self):
        """Ambil data dari form"""
        # Get kelompok value from dropdown
        kelompok = self.kelompok_kategorial_input.currentText()

        # Skip separator items (those with dashes)
        if "───" in kelompok:
            kelompok = ""

        if kelompok == "Pilih Kelompok Kategorial":
            kelompok = ""

        kelompok_lainnya = ""
        if kelompok == "Lainnya":
            kelompok_lainnya = self.kelompok_lainnya_input.text().strip()

        jenis_kelamin = self.jenis_kelamin_input.currentText()
        if jenis_kelamin == "Pilih Jenis Kelamin":
            jenis_kelamin = ""

        return {
            'kelompok_kategorial': kelompok,
            'kelompok_kategorial_lainnya': kelompok_lainnya,
            'nama_lengkap': self.nama_lengkap_input.text().strip(),
            'jenis_kelamin': jenis_kelamin,
            'jabatan': self.jabatan_input.text().strip(),
            'no_hp': self.no_hp_input.text().strip(),
            'email': self.email_input.text().strip(),
            'alamat': self.alamat_input.toPlainText().strip(),
            'wilayah_rohani': self.wilayah_rohani_input.currentText() if self.wilayah_rohani_input.currentIndex() > 0 else "",
            'masa_jabatan': self.masa_jabatan_input.text().strip(),
            'status': self.status_input.currentText(),
            'foto_path': self.uploaded_photo_path or self.foto_path_input.text().strip()
        }


class WRDialog(QDialog):
    """Dialog untuk menambah/edit pengurus Wilayah Rohani."""
    def __init__(self, parent=None, wr_data=None):
        super().__init__(parent)
        self.wr_data = wr_data
        self.parent_component = parent
        self.uploaded_photo_path = None
        self.setWindowTitle("Tambah Pengurus Wilayah Rohani" if not wr_data else "Edit Pengurus Wilayah Rohani")
        self.setModal(True)
        self.setFixedSize(550, 650)

        layout = QVBoxLayout(self)

        # Create scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Wilayah Rohani
        self.wilayah_rohani_input = QComboBox()
        self.wilayah_rohani_input.addItems([
            "Pilih Wilayah Rohani", "ST. YOHANES BAPTISTA DE LA SALLE", "ST. ALOYSIUS GONZAGA",
            "ST. GREGORIUS AGUNG", "ST. DOMINICO SAVIO", "ST. THOMAS AQUINAS", "ST. ALBERTUS AGUNG",
            "ST. BONAVENTURA", "STA. KATARINA DARI SIENA", "STA. SISILIA", "ST. BLASIUS",
            "ST. CAROLUS BORROMEUS", "ST. BONIFASIUS", "ST. CORNELIUS", "STA. BRIGITTA",
            "ST. IGNASIUS DARI LOYOLA", "ST. PIUS X", "STA. AGNES", "ST. AGUSTINUS",
            "STA. FAUSTINA", "ST. YOHANES MARIA VIANNEY", "STA. MARIA GORETTI", "STA. PERPETUA",
            "ST. LUKAS", "STA. SKOLASTIKA", "STA. THERESIA DARI AVILLA", "ST. VINCENTIUS A PAULO"
        ])
        self.wilayah_rohani_input.setCurrentIndex(0)
        self.wilayah_rohani_input.setMinimumWidth(350)
        self.setup_placeholder_style(self.wilayah_rohani_input)
        form_layout.addRow("Wilayah Rohani*:", self.wilayah_rohani_input)

        # Nama Lengkap
        self.nama_lengkap_input = QLineEdit()
        self.nama_lengkap_input.setMinimumWidth(350)
        form_layout.addRow("Nama Lengkap*:", self.nama_lengkap_input)

        # Jenis Kelamin
        self.jenis_kelamin_input = QComboBox()
        self.jenis_kelamin_input.addItems(["Pilih Jenis Kelamin", "Laki-laki", "Perempuan"])
        self.jenis_kelamin_input.setCurrentIndex(0)
        self.jenis_kelamin_input.setMinimumWidth(350)
        self.setup_placeholder_style(self.jenis_kelamin_input)
        form_layout.addRow("Jenis Kelamin:", self.jenis_kelamin_input)

        # Jabatan
        self.jabatan_input = QLineEdit()
        self.jabatan_input.setMinimumWidth(350)
        self.jabatan_input.setPlaceholderText("Contoh: Ketua, Sekretaris, Bendahara")
        form_layout.addRow("Jabatan:", self.jabatan_input)

        # No. HP
        self.no_hp_input = QLineEdit()
        self.no_hp_input.setMinimumWidth(350)
        self.no_hp_input.setPlaceholderText("08123456789")
        form_layout.addRow("No. HP:", self.no_hp_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setMinimumWidth(350)
        self.email_input.setPlaceholderText("email@example.com")
        form_layout.addRow("Email:", self.email_input)

        # Alamat
        self.alamat_input = QTextEdit()
        self.alamat_input.setMinimumWidth(350)
        self.alamat_input.setMinimumHeight(80)
        self.alamat_input.setMaximumHeight(100)
        self.alamat_input.setPlaceholderText("Alamat lengkap")
        form_layout.addRow("Alamat:", self.alamat_input)

        # Masa Jabatan
        self.masa_jabatan_input = QLineEdit()
        self.masa_jabatan_input.setMinimumWidth(350)
        self.masa_jabatan_input.setPlaceholderText("Contoh: 2023-2025")
        form_layout.addRow("Masa Jabatan:", self.masa_jabatan_input)

        # Status
        self.status_input = QComboBox()
        self.status_input.addItems(["Aktif", "Tidak Aktif"])
        self.status_input.setCurrentIndex(0)
        self.status_input.setMinimumWidth(350)
        form_layout.addRow("Status:", self.status_input)

        # Foto - with Browse button (matching DPP style)
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

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)  # type: ignore
        button_box.rejected.connect(self.reject)  # type: ignore
        layout.addWidget(button_box)

        # Load data if edit
        if wr_data:
            self.load_data()

    def browse_foto(self):
        """Browse untuk memilih foto dan upload ke server"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
        from PyQt5.QtCore import Qt

        filename, _ = QFileDialog.getOpenFileName(self, "Pilih Foto", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if filename:
            progress = QProgressDialog("Mengupload foto ke server...", "Batal", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(10)

            try:
                if hasattr(self.parent_component, 'db_manager') and self.parent_component.db_manager:
                    db_manager = self.parent_component.db_manager
                    progress.setValue(30)
                    success, result = db_manager.upload_struktur_photo_new(filename)
                    progress.setValue(80)

                    if success:
                        self.uploaded_photo_path = result.get('photo_path', '')
                        photo_url = result.get('photo_url', '')
                        self.foto_path_input.setText(f"Server: {photo_url}")
                        self.foto_path_input.setToolTip(f"File uploaded to server: {self.uploaded_photo_path}")
                        progress.setValue(100)
                        QMessageBox.information(self, "Sukses", "Foto berhasil diupload ke server!")
                    else:
                        progress.setValue(100)
                        QMessageBox.warning(self, "Error Upload", f"Gagal upload foto ke server:\n{result}")
                        self.foto_path_input.setText(filename)
                        self.uploaded_photo_path = None
                else:
                    progress.setValue(100)
                    QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    self.foto_path_input.setText(filename)
                    self.uploaded_photo_path = None

            except Exception as e:
                progress.setValue(100)
                QMessageBox.critical(self, "Error", f"Error saat upload foto:\n{str(e)}")
                self.foto_path_input.setText(filename)
                self.uploaded_photo_path = None

            finally:
                progress.close()

    def set_combo_value(self, combo, value):
        """Set combo box value"""
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.setCurrentIndex(0)

    def load_data(self):
        """Load data WR untuk edit"""
        self.nama_lengkap_input.setText(str(self.wr_data.get('nama_lengkap', '')))
        wilayah = self.wr_data.get('wilayah_rohani', '')
        self.set_combo_value(self.wilayah_rohani_input, wilayah)
        jenis_kelamin = self.wr_data.get('jenis_kelamin', '')
        self.set_combo_value(self.jenis_kelamin_input, jenis_kelamin)
        self.jabatan_input.setText(str(self.wr_data.get('jabatan', '')))
        self.no_hp_input.setText(str(self.wr_data.get('no_hp', '')))
        self.email_input.setText(str(self.wr_data.get('email', '')))
        self.alamat_input.setText(str(self.wr_data.get('alamat', '')))
        self.masa_jabatan_input.setText(str(self.wr_data.get('masa_jabatan', '')))
        self.set_combo_value(self.status_input, self.wr_data.get('status', 'Aktif'))
        self.foto_path_input.setText(str(self.wr_data.get('foto_path', '')))

    def get_data(self):
        """Ambil data dari form"""
        wilayah = self.wilayah_rohani_input.currentText()
        if wilayah == "Pilih Wilayah Rohani":
            wilayah = ""
        jenis_kelamin = self.jenis_kelamin_input.currentText()
        if jenis_kelamin == "Pilih Jenis Kelamin":
            jenis_kelamin = ""
        return {
            'wilayah_rohani': wilayah,
            'nama_lengkap': self.nama_lengkap_input.text().strip(),
            'jenis_kelamin': jenis_kelamin,
            'jabatan': self.jabatan_input.text().strip(),
            'no_hp': self.no_hp_input.text().strip(),
            'email': self.email_input.text().strip(),
            'alamat': self.alamat_input.toPlainText().strip(),
            'masa_jabatan': self.masa_jabatan_input.text().strip(),
            'status': self.status_input.currentText(),
            'foto_path': self.uploaded_photo_path or self.foto_path_input.text().strip()
        }
class KBinaanDialog(QDialog):
    """Dialog untuk menambah/edit pengurus Kelompok Binaan."""
    def __init__(self, parent=None, binaan_data=None):
        super().__init__(parent)
        self.binaan_data = binaan_data
        self.parent_component = parent
        self.uploaded_photo_path = None
        self.setWindowTitle("Tambah Pengurus Kelompok Binaan" if not binaan_data else "Edit Pengurus Kelompok Binaan")
        self.setModal(True)
        self.setFixedSize(550, 650)

        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)
        form_layout.setVerticalSpacing(6)
        form_layout.setHorizontalSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Kelompok Binaan
        self.kelompok_binaan_input = QComboBox()
        self.kelompok_binaan_input.addItems(["Pilih Kelompok Binaan", "Sekami", "PPA", "Lainnya"])
        self.kelompok_binaan_input.setCurrentIndex(0)
        self.kelompok_binaan_input.setMinimumWidth(400)
        self.kelompok_binaan_input.currentTextChanged.connect(self.on_kelompok_changed)
        form_layout.addRow("Kelompok Binaan*:", self.kelompok_binaan_input)

        # Kelompok Binaan Lainnya (hidden by default)
        self.kelompok_binaan_lainnya_input = QLineEdit()
        self.kelompok_binaan_lainnya_input.setMinimumWidth(400)
        self.kelompok_binaan_lainnya_input.setVisible(False)
        form_layout.addRow("Kelompok Lainnya:", self.kelompok_binaan_lainnya_input)

        # Nama Lengkap
        self.nama_lengkap_input = QLineEdit()
        self.nama_lengkap_input.setMinimumWidth(400)
        form_layout.addRow("Nama Lengkap*:", self.nama_lengkap_input)

        # Jenis Kelamin
        self.jenis_kelamin_input = QComboBox()
        self.jenis_kelamin_input.addItems(["Pilih Jenis Kelamin", "Laki-laki", "Perempuan"])
        self.jenis_kelamin_input.setCurrentIndex(0)
        self.jenis_kelamin_input.setMinimumWidth(400)
        form_layout.addRow("Jenis Kelamin:", self.jenis_kelamin_input)

        # Jabatan
        self.jabatan_input = QLineEdit()
        self.jabatan_input.setMinimumWidth(400)
        form_layout.addRow("Jabatan:", self.jabatan_input)

        # No. HP
        self.no_hp_input = QLineEdit()
        self.no_hp_input.setMinimumWidth(400)
        form_layout.addRow("No. HP:", self.no_hp_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setMinimumWidth(400)
        form_layout.addRow("Email:", self.email_input)

        # Alamat
        self.alamat_input = QTextEdit()
        self.alamat_input.setMinimumWidth(400)
        self.alamat_input.setFixedHeight(80)
        form_layout.addRow("Alamat:", self.alamat_input)

        # Wilayah Rohani
        self.wilayah_rohani_input = QComboBox()
        self.wilayah_rohani_input.addItems([
            "Pilih Wilayah Rohani", "ST. YOHANES BAPTISTA DE LA SALLE", "ST. ALOYSIUS GONZAGA",
            "ST. GREGORIUS AGUNG", "ST. DOMINICO SAVIO", "ST. THOMAS AQUINAS", "ST. ALBERTUS AGUNG",
            "ST. BONAVENTURA", "STA. KATARINA DARI SIENA", "STA. SISILIA", "ST. BLASIUS",
            "ST. CAROLUS BORROMEUS", "ST. BONIFASIUS", "ST. CORNELIUS", "STA. BRIGITTA",
            "ST. IGNASIUS DARI LOYOLA", "ST. PIUS X", "STA. AGNES", "ST. AGUSTINUS",
            "STA. FAUSTINA", "ST. YOHANES MARIA VIANNEY", "STA. MARIA GORETTI", "STA. PERPETUA",
            "ST. LUKAS", "STA. SKOLASTIKA", "STA. THERESIA DARI AVILLA", "ST. VINCENTIUS A PAULO"
        ])
        self.wilayah_rohani_input.setCurrentIndex(0)
        self.wilayah_rohani_input.setMinimumWidth(400)
        form_layout.addRow("Wilayah Rohani:", self.wilayah_rohani_input)

        # Masa Jabatan
        self.masa_jabatan_input = QLineEdit()
        self.masa_jabatan_input.setPlaceholderText("contoh: 2023-2025")
        self.masa_jabatan_input.setMinimumWidth(400)
        form_layout.addRow("Masa Jabatan:", self.masa_jabatan_input)

        # Status
        self.status_input = QComboBox()
        self.status_input.addItems(["Aktif", "Tidak Aktif"])
        self.status_input.setCurrentIndex(0)
        self.status_input.setMinimumWidth(400)
        form_layout.addRow("Status:", self.status_input)

        # Foto
        photo_layout = QHBoxLayout()
        self.foto_path_input = QLineEdit()
        self.foto_path_input.setMinimumWidth(300)
        self.foto_path_input.setReadOnly(True)
        photo_layout.addWidget(self.foto_path_input)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_foto)
        photo_layout.addWidget(browse_btn)
        form_layout.addRow("Foto:", photo_layout)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        if binaan_data:
            self.load_data()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_kelompok_changed(self):
        is_lainnya = self.kelompok_binaan_input.currentText() == "Lainnya"
        self.kelompok_binaan_lainnya_input.setVisible(is_lainnya)

    def browse_foto(self):
        """Browse untuk memilih foto dan upload ke server"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
        from PyQt5.QtCore import Qt

        filename, _ = QFileDialog.getOpenFileName(self, "Pilih Foto", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if filename:
            progress = QProgressDialog("Mengupload foto ke server...", "Batal", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(10)

            try:
                if hasattr(self.parent_component, 'db_manager') and self.parent_component.db_manager:
                    db_manager = self.parent_component.db_manager
                    progress.setValue(30)
                    success, result = db_manager.upload_struktur_photo_new(filename)
                    progress.setValue(80)

                    if success:
                        self.uploaded_photo_path = result.get('photo_path', '')
                        photo_url = result.get('photo_url', '')
                        self.foto_path_input.setText(f"Server: {photo_url}")
                        self.foto_path_input.setToolTip(f"File uploaded to server: {self.uploaded_photo_path}")
                        progress.setValue(100)
                        QMessageBox.information(self, "Sukses", "Foto berhasil diupload ke server!")
                    else:
                        progress.setValue(100)
                        QMessageBox.warning(self, "Error Upload", f"Gagal upload foto ke server:\n{result}")
                        self.foto_path_input.setText(filename)
                        self.uploaded_photo_path = None
                else:
                    progress.setValue(100)
                    QMessageBox.warning(self, "Error", "Database manager tidak tersedia")
                    self.foto_path_input.setText(filename)
                    self.uploaded_photo_path = None

            except Exception as e:
                progress.setValue(100)
                QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat upload foto:\n{str(e)}")
                self.foto_path_input.setText(filename)
                self.uploaded_photo_path = None

    def set_combo_value(self, combo, value):
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def load_data(self):
        self.nama_lengkap_input.setText(str(self.binaan_data.get("nama_lengkap", "")))
        kelompok = self.binaan_data.get("kelompok_binaan", "")
        self.set_combo_value(self.kelompok_binaan_input, kelompok)
        jenis_kelamin = self.binaan_data.get("jenis_kelamin", "")
        self.set_combo_value(self.jenis_kelamin_input, jenis_kelamin)
        self.jabatan_input.setText(str(self.binaan_data.get("jabatan", "")))
        self.no_hp_input.setText(str(self.binaan_data.get("no_hp", "")))
        self.email_input.setText(str(self.binaan_data.get("email", "")))
        self.alamat_input.setText(str(self.binaan_data.get("alamat", "")))
        wilayah = self.binaan_data.get("wilayah_rohani", "")
        self.set_combo_value(self.wilayah_rohani_input, wilayah)
        self.masa_jabatan_input.setText(str(self.binaan_data.get("masa_jabatan", "")))
        self.set_combo_value(self.status_input, self.binaan_data.get("status", "Aktif"))
        self.foto_path_input.setText(str(self.binaan_data.get("foto_path", "")))

    def get_data(self):
        kelompok = self.kelompok_binaan_input.currentText()
        if kelompok == "Pilih Kelompok Binaan":
            kelompok = ""
        jenis_kelamin = self.jenis_kelamin_input.currentText()
        if jenis_kelamin == "Pilih Jenis Kelamin":
            jenis_kelamin = ""
        wilayah = self.wilayah_rohani_input.currentText()
        if wilayah == "Pilih Wilayah Rohani":
            wilayah = ""
        return {
            "kelompok_binaan": kelompok,
            "kelompok_binaan_lainnya": self.kelompok_binaan_lainnya_input.text().strip() if kelompok == "Lainnya" else "",
            "nama_lengkap": self.nama_lengkap_input.text().strip(),
            "jenis_kelamin": jenis_kelamin,
            "jabatan": self.jabatan_input.text().strip(),
            "no_hp": self.no_hp_input.text().strip(),
            "email": self.email_input.text().strip(),
            "alamat": self.alamat_input.toPlainText().strip(),
            "wilayah_rohani": wilayah,
            "masa_jabatan": self.masa_jabatan_input.text().strip(),
            "status": self.status_input.currentText(),
            "foto_path": self.uploaded_photo_path or self.foto_path_input.text().strip()
        }


class TimPembinaDialog(QDialog):
    """Dialog untuk menambah/edit Tim Pembina"""
    def __init__(self, parent=None, tim_data=None):
        super().__init__(parent)
        self.tim_data = tim_data
        self.setWindowTitle("Tambah Tim Pembina" if not tim_data else "Edit Tim Pembina")
        self.setModal(True)
        self.setFixedSize(500, 350)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # Jenis Pelayanan dropdown (first field - Tim Pembina)
        self.jenis_pelayanan_input = QComboBox()
        self.jenis_pelayanan_input.addItems([
            "Pilih Jenis Pelayanan",
            "Liturgi",
            "Katekese",
            "Perkawinan",
            "Keluarga",
            "Konsultasi",
            "Lainnya"
        ])
        self.jenis_pelayanan_input.setMinimumWidth(300)
        self.jenis_pelayanan_input.currentIndexChanged.connect(self.on_jenis_pelayanan_changed)
        form_layout.addRow("Tim Pembina:", self.jenis_pelayanan_input)

        # Jenis Pelayanan Lainnya (akan ditampilkan jika user memilih "Lainnya")
        self.jenis_pelayanan_lain_label = QLabel("Tim Pembina Lainnya:")
        self.jenis_pelayanan_lain_input = QLineEdit()
        self.jenis_pelayanan_lain_input.setMinimumWidth(300)
        self.jenis_pelayanan_lain_input.setPlaceholderText("Masukkan tim pembina lainnya")
        form_layout.addRow(self.jenis_pelayanan_lain_label, self.jenis_pelayanan_lain_input)
        self.jenis_pelayanan_lain_label.setVisible(False)
        self.jenis_pelayanan_lain_input.setVisible(False)

        # Tanggal Pelantikan
        self.tanggal_pelantikan_input = QDateEdit()
        self.tanggal_pelantikan_input.setCalendarPopup(True)
        self.tanggal_pelantikan_input.setDate(QDate.currentDate())
        self.tanggal_pelantikan_input.setMinimumWidth(300)
        form_layout.addRow("Tanggal Pelantikan:", self.tanggal_pelantikan_input)

        # Keterangan
        self.keterangan_input = QTextEdit()
        self.keterangan_input.setMinimumWidth(300)
        self.keterangan_input.setMinimumHeight(80)
        form_layout.addRow("Keterangan:", self.keterangan_input)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        if tim_data:
            self.load_data()

    def on_jenis_pelayanan_changed(self):
        """Show/hide 'Lainnya' field based on dropdown selection"""
        is_lainnya = self.jenis_pelayanan_input.currentText() == "Lainnya"
        self.jenis_pelayanan_lain_label.setVisible(is_lainnya)
        self.jenis_pelayanan_lain_input.setVisible(is_lainnya)

    def load_data(self):
        """Load data untuk edit - Opsi B"""
        if not self.tim_data:
            return

        # Load tim_pembina (the dropdown - jenis pelayanan value)
        tim_pembina = self.tim_data.get('tim_pembina', '')
        valid_options = ["Liturgi", "Katekese", "Perkawinan", "Keluarga", "Konsultasi"]

        if tim_pembina:
            if tim_pembina in valid_options:
                # Standard option
                index = self.jenis_pelayanan_input.findText(tim_pembina)
                if index >= 0:
                    self.jenis_pelayanan_input.setCurrentIndex(index)
            elif tim_pembina == "Lainnya":
                # "Lainnya" was selected, load custom value from nama_lainnya
                self.jenis_pelayanan_input.setCurrentIndex(self.jenis_pelayanan_input.findText("Lainnya"))
                nama_lainnya = self.tim_data.get('nama_lainnya', '')
                if nama_lainnya:
                    self.jenis_pelayanan_lain_input.setText(str(nama_lainnya))
                    self.jenis_pelayanan_lain_label.setVisible(True)
                    self.jenis_pelayanan_lain_input.setVisible(True)

        tanggal = self.tim_data.get('tanggal_pelantikan', '')
        if tanggal:
            try:
                if isinstance(tanggal, str):
                    date = QDate.fromString(tanggal, "yyyy-MM-dd")
                else:
                    date = QDate(tanggal)
                self.tanggal_pelantikan_input.setDate(date)
            except:
                pass

        self.keterangan_input.setPlainText(str(self.tim_data.get('keterangan', '')))

    def get_data(self):
        """Ambil data dari form - Opsi B: menggunakan tim_pembina_lainnya table"""
        tim_pembina = self.jenis_pelayanan_input.currentText()
        nama_lainnya = ''

        # If Lainnya is selected, get custom value
        if tim_pembina == "Lainnya":
            nama_lainnya = self.jenis_pelayanan_lain_input.text().strip()

        return {
            'tim_pembina': tim_pembina if tim_pembina != "Pilih Jenis Pelayanan" else '',
            'nama_lainnya': nama_lainnya,  # Custom value untuk tim_pembina_lainnya table
            'tanggal_pelantikan': self.tanggal_pelantikan_input.date().toString("yyyy-MM-dd"),
            'keterangan': self.keterangan_input.toPlainText().strip()
        }


class TimPembinaPesertaDialog(QDialog):
    """Dialog untuk menambah peserta Tim Pembina"""
    def __init__(self, parent=None, tim_id=None, db_manager=None):
        super().__init__(parent)
        self.tim_id = tim_id
        self.db_manager = db_manager
        self.selected_jemaat = None
        self.setWindowTitle("Tambah Peserta Tim Pembina")
        self.setModal(True)
        self.setFixedSize(500, 350)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # Nama Lengkap dengan search
        self.nama_lengkap_input = QLineEdit()
        self.nama_lengkap_input.setPlaceholderText("Ketik nama untuk mencari umat...")
        self.nama_lengkap_input.setMinimumWidth(300)
        self.nama_lengkap_input.textChanged.connect(self.on_search_jemaat)
        form_layout.addRow("Nama Lengkap:", self.nama_lengkap_input)

        # Wilayah Rohani (read-only)
        self.wilayah_rohani_input = QLineEdit()
        self.wilayah_rohani_input.setReadOnly(True)
        self.wilayah_rohani_input.setMinimumWidth(300)
        form_layout.addRow("Wilayah Rohani:", self.wilayah_rohani_input)

        # Jabatan
        self.jabatan_input = QComboBox()
        self.jabatan_input.addItems([
            "Pilih Jabatan",
            "Pembina",
            "Ketua",
            "Sekretaris",
            "Bendahara",
            "Koordinator",
            "Anggota Sie",
            "Anggota Biasa"
        ])
        self.jabatan_input.setMinimumWidth(300)
        self.jabatan_input.currentTextChanged.connect(self.on_jabatan_changed)
        form_layout.addRow("Jabatan:", self.jabatan_input)

        # Koordinator Bidang (hidden by default)
        self.koordinator_bidang_input = QLineEdit()
        self.koordinator_bidang_input.setMinimumWidth(300)
        self.koordinator_bidang_input.setVisible(False)
        self.koordinator_bidang_label = QLabel("Koordinator Bidang:")
        self.koordinator_bidang_label.setVisible(False)
        form_layout.addRow(self.koordinator_bidang_label, self.koordinator_bidang_input)

        # Sie Bidang (hidden by default)
        self.sie_bidang_input = QLineEdit()
        self.sie_bidang_input.setMinimumWidth(300)
        self.sie_bidang_input.setVisible(False)
        self.sie_bidang_label = QLabel("Sie Bidang:")
        self.sie_bidang_label.setVisible(False)
        form_layout.addRow(self.sie_bidang_label, self.sie_bidang_input)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_search_jemaat(self, keyword):
        """Search umat dalam database jemaat"""
        if not self.db_manager:
            return

        if len(keyword) < 2:
            self.selected_jemaat = None
            self.wilayah_rohani_input.clear()
            return

        try:
            result = self.db_manager.search_jemaat_by_nama(keyword)
            if isinstance(result, dict) and result.get('success'):
                jemaat_list = result.get('data', [])
                if jemaat_list:
                    # Auto-select if only one match
                    if len(jemaat_list) == 1:
                        self.selected_jemaat = jemaat_list[0]
                        self.nama_lengkap_input.setText(self.selected_jemaat.get('nama_lengkap', ''))
                        self.wilayah_rohani_input.setText(self.selected_jemaat.get('wilayah_rohani', ''))
                    else:
                        # If multiple matches, show in completer
                        nama_list = [j.get('nama_lengkap', '') for j in jemaat_list]
                        # Store all jemaat for later selection
                        self.jemaat_list = jemaat_list
                else:
                    QMessageBox.information(self, "Tidak Ditemukan", "Umat tidak terdaftar")
                    self.selected_jemaat = None
                    self.wilayah_rohani_input.clear()
            else:
                QMessageBox.information(self, "Tidak Ditemukan", "Umat tidak terdaftar")
                self.selected_jemaat = None
                self.wilayah_rohani_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error searching jemaat: {str(e)}")

    def on_jabatan_changed(self, jabatan):
        """Handle jabatan selection changed"""
        if jabatan == "Koordinator":
            self.koordinator_bidang_input.setVisible(True)
            self.koordinator_bidang_label.setVisible(True)
            self.sie_bidang_input.setVisible(False)
            self.sie_bidang_label.setVisible(False)
        elif jabatan == "Anggota Sie":
            self.sie_bidang_input.setVisible(True)
            self.sie_bidang_label.setVisible(True)
            self.koordinator_bidang_input.setVisible(False)
            self.koordinator_bidang_label.setVisible(False)
        else:
            self.koordinator_bidang_input.setVisible(False)
            self.koordinator_bidang_label.setVisible(False)
            self.sie_bidang_input.setVisible(False)
            self.sie_bidang_label.setVisible(False)

    def get_data(self):
        """Ambil data dari form"""
        data = {
            'id_jemaat': self.selected_jemaat.get('id_jemaat') if self.selected_jemaat else None,
            'nama_lengkap': self.nama_lengkap_input.text().strip(),
            'wilayah_rohani': self.wilayah_rohani_input.text().strip(),
            'jabatan': self.jabatan_input.currentText() if self.jabatan_input.currentIndex() > 0 else '',
            'koordinator_bidang': self.koordinator_bidang_input.text().strip() if self.koordinator_bidang_input.isVisible() else '',
            'sie_bidang': self.sie_bidang_input.text().strip() if self.sie_bidang_input.isVisible() else ''
        }
        return data


class ProgramKerjaKategorialDialog(QDialog):
    """Dialog untuk menambah/edit program kerja kelompok kategorial"""

    def __init__(self, parent=None, program_data=None):
        super().__init__(parent)
        self.program_data = program_data
        self.setWindowTitle("Tambah Program Kerja Kategorial" if not program_data else "Edit Program Kerja Kategorial")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(650)

        self.setup_ui()

        if program_data:
            self.load_data()

    def setup_ui(self):
        """Setup UI untuk dialog program kerja kategorial"""
        layout = QVBoxLayout(self)

        # Create scroll area for form
        from PyQt5.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(10)

        # Program Kerja (nama program)
        self.program_kerja_input = QLineEdit()
        self.program_kerja_input.setPlaceholderText("Nama program kerja kategorial")
        self.program_kerja_input.setMinimumWidth(500)
        form_layout.addRow("Program Kerja*:", self.program_kerja_input)

        # Kategori
        self.kategori_input = QComboBox()
        self.kategori_input.addItems([
            "Ibadah", "Doa", "Katekese", "Sosial",
            "Rohani", "Administratif", "Perayaan", "Lainnya"
        ])
        form_layout.addRow("Kategori*:", self.kategori_input)

        # Subyek/Sasaran
        self.subyek_sasaran_input = QLineEdit()
        self.subyek_sasaran_input.setPlaceholderText("Sasaran atau subjek program")
        form_layout.addRow("Subyek/Sasaran:", self.subyek_sasaran_input)

        # Indikator Pencapaian
        self.indikator_input = QLineEdit()
        self.indikator_input.setPlaceholderText("Indikator pencapaian program")
        form_layout.addRow("Indikator Pencapaian:", self.indikator_input)

        # Model/Bentuk/Metode
        self.model_bentuk_input = QLineEdit()
        self.model_bentuk_input.setPlaceholderText("Model, bentuk, atau metode pelaksanaan")
        form_layout.addRow("Model/Bentuk/Metode:", self.model_bentuk_input)

        # Materi
        self.materi_input = QLineEdit()
        self.materi_input.setPlaceholderText("Materi yang akan disampaikan")
        form_layout.addRow("Materi:", self.materi_input)

        # Tempat
        self.tempat_input = QLineEdit()
        self.tempat_input.setPlaceholderText("Lokasi pelaksanaan program")
        form_layout.addRow("Tempat:", self.tempat_input)

        # Waktu
        self.waktu_input = QLineEdit()
        self.waktu_input.setPlaceholderText("Tanggal dan waktu pelaksanaan")
        form_layout.addRow("Waktu:", self.waktu_input)

        # PIC (Person In Charge)
        self.pic_input = QLineEdit()
        self.pic_input.setPlaceholderText("Penanggung jawab program")
        form_layout.addRow("PIC:", self.pic_input)

        # Perincian
        self.perincian_input = QTextEdit()
        self.perincian_input.setPlaceholderText("Rincian detail pelaksanaan program")
        self.perincian_input.setMaximumHeight(60)
        form_layout.addRow("Perincian:", self.perincian_input)

        # Quantity
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Jumlah/kuantitas")
        form_layout.addRow("Quantity:", self.quantity_input)

        # Satuan
        self.satuan_input = QLineEdit()
        self.satuan_input.setPlaceholderText("Satuan (orang, paket, dll)")
        form_layout.addRow("Satuan:", self.satuan_input)

        # Harga Satuan
        self.harga_satuan_input = QLineEdit()
        self.harga_satuan_input.setPlaceholderText("Harga per satuan (Rp)")
        form_layout.addRow("Harga Satuan:", self.harga_satuan_input)

        # Frekuensi
        self.frekuensi_input = QLineEdit()
        self.frekuensi_input.setPlaceholderText("Berapa kali dilaksanakan")
        self.frekuensi_input.setText("1")
        form_layout.addRow("Frekuensi:", self.frekuensi_input)

        # Keterangan
        self.keterangan_input = QTextEdit()
        self.keterangan_input.setPlaceholderText("Keterangan tambahan (opsional)")
        self.keterangan_input.setMaximumHeight(60)
        form_layout.addRow("Keterangan:", self.keterangan_input)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_data(self):
        """Load data untuk edit mode"""
        if not self.program_data:
            return

        self.program_kerja_input.setText(self.program_data.get('program_kerja', ''))
        self.kategori_input.setCurrentText(self.program_data.get('kategori', 'Lainnya'))
        self.subyek_sasaran_input.setText(self.program_data.get('subyek_sasaran', ''))
        self.indikator_input.setText(self.program_data.get('indikator_pencapaian', ''))
        self.model_bentuk_input.setText(self.program_data.get('model_bentuk_metode', ''))
        self.materi_input.setText(self.program_data.get('materi', ''))
        self.tempat_input.setText(self.program_data.get('tempat', ''))
        self.waktu_input.setText(self.program_data.get('waktu', ''))
        self.pic_input.setText(self.program_data.get('pic', ''))
        self.perincian_input.setPlainText(self.program_data.get('perincian', ''))
        self.quantity_input.setText(str(self.program_data.get('quantity', '')))
        self.satuan_input.setText(self.program_data.get('satuan', ''))
        self.harga_satuan_input.setText(str(self.program_data.get('harga_satuan', '')))
        self.frekuensi_input.setText(str(self.program_data.get('frekuensi', '1')))
        self.keterangan_input.setPlainText(self.program_data.get('keterangan', ''))

    def get_data(self):
        """Get form data"""
        return {
            'program_kerja': self.program_kerja_input.text().strip(),
            'kategori': self.kategori_input.currentText(),
            'subyek_sasaran': self.subyek_sasaran_input.text().strip(),
            'indikator_pencapaian': self.indikator_input.text().strip(),
            'model_bentuk_metode': self.model_bentuk_input.text().strip(),
            'materi': self.materi_input.text().strip(),
            'tempat': self.tempat_input.text().strip(),
            'waktu': self.waktu_input.text().strip(),
            'pic': self.pic_input.text().strip(),
            'perincian': self.perincian_input.toPlainText().strip(),
            'quantity': self.quantity_input.text().strip(),
            'satuan': self.satuan_input.text().strip(),
            'harga_satuan': self.harga_satuan_input.text().strip(),
            'frekuensi': self.frekuensi_input.text().strip(),
            'keterangan': self.keterangan_input.toPlainText().strip(),
        }


class TimPesertaDialog(QDialog):
    """Dialog untuk menambah/edit peserta Tim Pembina (simplified single-table approach)"""
    def __init__(self, parent=None, peserta_data=None, db_manager=None):
        super().__init__(parent)
        self.peserta_data = peserta_data
        self.db_manager = db_manager
        self.selected_jemaat = None
        self.setWindowTitle("Tambah Peserta Tim" if not peserta_data else "Edit Peserta Tim")
        self.setModal(True)
        self.setFixedSize(550, 450)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # Nama Peserta (searchable from jemaat)
        self.nama_peserta_input = QLineEdit()
        self.nama_peserta_input.setPlaceholderText("Ketik nama untuk mencari umat...")
        self.nama_peserta_input.setMinimumWidth(350)
        self.nama_peserta_input.textChanged.connect(self.on_search_jemaat)
        form_layout.addRow("Nama Peserta:", self.nama_peserta_input)

        # Wilayah Rohani (dropdown)
        self.wilayah_rohani_input = QComboBox()
        self.wilayah_rohani_input.setMinimumWidth(350)
        self.wilayah_rohani_input.addItem("Pilih Wilayah Rohani")
        self.load_wilayah_list()  # Load immediately
        form_layout.addRow("Wilayah Rohani:", self.wilayah_rohani_input)

        # Jabatan (dropdown with fixed options)
        self.jabatan_input = QComboBox()
        self.jabatan_input.setMinimumWidth(350)
        self.jabatan_input.addItems([
            "Pilih Jabatan",
            "Pembina",
            "Ketua",
            "Sekretaris",
            "Bendahara",
            "Koordinator",
            "Anggota Sie",
            "Anggota Biasa"
        ])
        form_layout.addRow("Jabatan:", self.jabatan_input)

        # Tim Pembina (dropdown)
        self.nama_tim_input = QComboBox()
        self.nama_tim_input.setMinimumWidth(350)
        self.nama_tim_input.addItem("Pilih Tim")
        self.load_tim_list()
        form_layout.addRow("Tim Pembina:", self.nama_tim_input)

        # Tahun (dropdown with realtime years starting from 2025)
        self.tahun_input = QComboBox()
        self.tahun_input.setMinimumWidth(350)
        self.tahun_input.addItem("Pilih Tahun")
        current_year = QDate.currentDate().year()
        for year in range(2025, current_year + 5):
            self.tahun_input.addItem(str(year))
        form_layout.addRow("Tahun:", self.tahun_input)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Load data if editing
        if peserta_data:
            self.load_data()

    def load_tim_list(self):
        """Load tim pembina list from database"""
        if not self.db_manager:
            return

        try:
            success, result = self.db_manager.get_tim_pembina()
            if success and isinstance(result, dict) and result.get('success'):
                tim_list = result.get('data', [])
                for tim in tim_list:
                    tim_name = tim.get('nama_tim', tim.get('tim_pembina', ''))
                    if tim_name:
                        self.nama_tim_input.addItem(tim_name)
        except Exception as e:
            print(f"[TimPesertaDialog] Error loading tim list: {str(e)}")

    def load_wilayah_list(self):
        """Load wilayah rohani list from jemaat database"""
        if not self.db_manager:
            return

        try:
            # Get unique wilayah rohani from jemaat
            success, result = self.db_manager.get_jemaat_list()
            if success and isinstance(result, dict) and result.get('success'):
                jemaat_list = result.get('data', [])
                wilayah_set = set()
                for jemaat in jemaat_list:
                    wr = jemaat.get('wilayah_rohani', '')
                    if wr:
                        wilayah_set.add(wr)

                self.wilayah_rohani_input.blockSignals(True)
                self.wilayah_rohani_input.clear()
                self.wilayah_rohani_input.addItem("Pilih Wilayah Rohani")
                for wr in sorted(wilayah_set):
                    self.wilayah_rohani_input.addItem(wr)
                self.wilayah_rohani_input.blockSignals(False)
        except Exception as e:
            print(f"[TimPesertaDialog] Error loading wilayah list: {str(e)}")

    def on_search_jemaat(self, keyword):
        """Search umat dalam database jemaat"""
        if not self.db_manager:
            return

        if len(keyword) < 2:
            self.selected_jemaat = None
            self.wilayah_rohani_input.setCurrentIndex(0)
            return

        try:
            result = self.db_manager.search_jemaat_by_nama(keyword)
            if isinstance(result, dict) and result.get('success'):
                jemaat_list = result.get('data', [])
                if jemaat_list:
                    # Auto-select if only one match
                    if len(jemaat_list) == 1:
                        self.selected_jemaat = jemaat_list[0]
                        self.nama_peserta_input.setText(self.selected_jemaat.get('nama_lengkap', ''))
                        wilayah = self.selected_jemaat.get('wilayah_rohani', '')
                        if wilayah:
                            index = self.wilayah_rohani_input.findText(wilayah)
                            if index >= 0:
                                self.wilayah_rohani_input.setCurrentIndex(index)
                    else:
                        # Multiple matches - store for later selection
                        self.jemaat_list = jemaat_list
                        # Auto-select first if multiple
                        self.selected_jemaat = jemaat_list[0]
                        self.nama_peserta_input.setText(self.selected_jemaat.get('nama_lengkap', ''))
                        wilayah = self.selected_jemaat.get('wilayah_rohani', '')
                        if wilayah:
                            index = self.wilayah_rohani_input.findText(wilayah)
                            if index >= 0:
                                self.wilayah_rohani_input.setCurrentIndex(index)
                else:
                    self.selected_jemaat = None
                    self.wilayah_rohani_input.setCurrentIndex(0)
            else:
                self.selected_jemaat = None
                self.wilayah_rohani_input.setCurrentIndex(0)
        except Exception as e:
            print(f"[TimPesertaDialog] Error searching jemaat: {str(e)}")

    def load_data(self):
        """Load data untuk edit"""
        if not self.peserta_data:
            return

        # Load nama peserta
        nama_peserta = self.peserta_data.get('nama_peserta', '')
        if nama_peserta:
            self.nama_peserta_input.setText(nama_peserta)
            self.selected_jemaat = {'nama_lengkap': nama_peserta, 'id_jemaat': self.peserta_data.get('id_jemaat')}

        # Load wilayah rohani
        wilayah = self.peserta_data.get('wilayah_rohani', '')
        if not wilayah:
            self.load_wilayah_list()
        if wilayah:
            index = self.wilayah_rohani_input.findText(wilayah)
            if index >= 0:
                self.wilayah_rohani_input.setCurrentIndex(index)

        # Load jabatan
        jabatan = self.peserta_data.get('jabatan', '')
        if jabatan:
            index = self.jabatan_input.findText(jabatan)
            if index >= 0:
                self.jabatan_input.setCurrentIndex(index)

        # Load tim pembina
        nama_tim = self.peserta_data.get('nama_tim', self.peserta_data.get('tim_pembina', ''))
        if nama_tim:
            index = self.nama_tim_input.findText(nama_tim)
            if index >= 0:
                self.nama_tim_input.setCurrentIndex(index)

        # Load tahun
        tahun = str(self.peserta_data.get('tahun', ''))
        if tahun and tahun != '':
            index = self.tahun_input.findText(tahun)
            if index >= 0:
                self.tahun_input.setCurrentIndex(index)

    def get_data(self):
        """Ambil data dari form"""
        return {
            'id_jemaat': self.selected_jemaat.get('id_jemaat') if self.selected_jemaat else None,
            'nama_peserta': self.nama_peserta_input.text().strip(),
            'wilayah_rohani': self.wilayah_rohani_input.currentText() if self.wilayah_rohani_input.currentText() != "Pilih Wilayah Rohani" else '',
            'jabatan': self.jabatan_input.currentText() if self.jabatan_input.currentText() != "Pilih Jabatan" else '',
            'nama_tim': self.nama_tim_input.currentText() if self.nama_tim_input.currentText() != "Pilih Tim" else '',
            'tahun': int(self.tahun_input.currentText()) if self.tahun_input.currentText() != "Pilih Tahun" else None,
        }
