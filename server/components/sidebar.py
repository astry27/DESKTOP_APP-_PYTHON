# Path: server/components/sidebar.py

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from .vertical_submenu import VerticalSubMenu
from .expandable_menu_button import ExpandableMenuButton


class SidebarButton(QPushButton):
    """Custom button untuk sidebar"""
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(45)

        # Set style dengan bold font untuk menu utama - background putih, teks profesional
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: bold;
                background-color: #FFFFFF;
                color: #2C3E50;
                margin: 4px 8px;
            }
            QPushButton:hover {
                background-color: #ECF0F1;
                color: #1A252F;
            }
            QPushButton:checked {
                background-color: #002B36;
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 6px;
                margin: 4px 8px;
            }
        """)

        # Set icon dari file path
        self.icon_path = icon_path
        self.icon_active_path = None

        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(18, 18))

            # Generate active icon path (dashboard_icon.png -> dashboard_active_icon.png)
            if icon_path.endswith('.png'):
                base_path = icon_path[:-4]  # Remove .png
                active_path = base_path + '_active_icon.png'
                if os.path.exists(active_path):
                    self.icon_active_path = active_path

        # Connect clicked signal untuk switch icon saat checked
        self.clicked.connect(self.on_clicked)

    def update_icon_state(self):
        """Update icon berdasarkan checked state"""
        if self.isChecked() and self.icon_active_path:
            self.setIcon(QIcon(self.icon_active_path))
        elif not self.isChecked() and self.icon_path:
            self.setIcon(QIcon(self.icon_path))

    def on_clicked(self):
        """Handle click untuk switch icon saat checked/unchecked"""
        self.update_icon_state()


class SidebarWidget(QWidget):
    """Widget untuk sidebar navigasi dengan menu bercabang"""

    # Signal untuk menu yang dipilih
    menu_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.db_manager = None

        # Set style untuk sidebar utama - background putih
        self.setStyleSheet("background-color: #FFFFFF;")

        # Layout utama
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header sidebar
        header = self.create_header()
        layout.addWidget(header)

        # Scroll area untuk menu
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hilangkan scroll horizontal
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #FFFFFF;
            }
            QScrollBar:vertical {
                width: 8px;
                background-color: #FFFFFF;
            }
            QScrollBar::handle:vertical {
                background-color: #BDC3C7;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #95A5A6;
            }
            QScrollBar:horizontal {
                height: 0px;
            }
        """)

        # Container untuk menu navigasi
        menu_container = QWidget()
        menu_container.setStyleSheet("background-color: #FFFFFF;")
        self.menu_layout = QVBoxLayout(menu_container)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(0)  # Spacing ditangani oleh margin di button

        # Add stretch di akhir untuk menghilangkan scroll yang tidak perlu
        # stretch ini akan ditambahkan nanti

        # Path ke ikon-ikon
        assets_path = "server/assets/"

        # ============ MENU DASHBOARD ============
        self.menu_dashboard = SidebarButton("Dashboard", os.path.join(assets_path, "dashboard_icon.png"))
        self.menu_dashboard.clicked.connect(self.on_dashboard_clicked)
        self.menu_layout.addWidget(self.menu_dashboard)

        # ============ MENU PUSAT PAROKI (EXPANDABLE) ============
        self.menu_pusat_paroki = ExpandableMenuButton("Pusat Paroki", os.path.join(assets_path, "paroki_icon.png"))
        self.menu_layout.addWidget(self.menu_pusat_paroki)

        # Submenu Pusat Paroki (sorted alphabetically)
        self.submenu_pusat_paroki = VerticalSubMenu()
        self.submenu_pusat_paroki.add_button("aset", "Aset", os.path.join(assets_path, "inventory_icon.png"))
        self.submenu_pusat_paroki.add_button("database_umat", "Database Umat", os.path.join(assets_path, "jemaat_icon.png"))
        self.submenu_pusat_paroki.add_button("dokumen", "Dokumen", os.path.join(assets_path, "dokumen_icon.png"))
        self.submenu_pusat_paroki.add_button("kegiatan_paroki", "Kegiatan Paroki", os.path.join(assets_path, "jadwal_icon.png"))
        self.submenu_pusat_paroki.add_button("pengumuman", "Pengumuman", os.path.join(assets_path, "pengumuman_icon.png"))
        self.submenu_pusat_paroki.add_button("proker_dpp", "Program Kerja - DPP", os.path.join(assets_path, "kalender_icon.png"))
        self.submenu_pusat_paroki.add_button("struktur_dpp", "Struktur Organisasi", os.path.join(assets_path, "structure_icon.png"))
        self.submenu_pusat_paroki.add_button("tim_pembina", "Tim Pembina", os.path.join(assets_path, "tim.png"))
        self.menu_layout.addWidget(self.submenu_pusat_paroki)

        # Connect Pusat Paroki toggle
        self.menu_pusat_paroki.toggled.connect(self.on_pusat_paroki_toggled)
        self.submenu_pusat_paroki.menu_clicked.connect(self.on_submenu_clicked)

        # ============ MENU WILAYAH ROHANI (EXPANDABLE) ============
        self.menu_wilayah_rohani = ExpandableMenuButton("Wilayah Rohani", os.path.join(assets_path, "wr_icon.png"))
        self.menu_layout.addWidget(self.menu_wilayah_rohani)

        # Submenu Wilayah Rohani (sorted alphabetically)
        self.submenu_wilayah_rohani = VerticalSubMenu()
        self.submenu_wilayah_rohani.add_button("kegiatan_wr", "Kegiatan (WR)", os.path.join(assets_path, "jadwal_icon.png"))
        self.submenu_wilayah_rohani.add_button("keuangan_wr", "Keuangan (WR)", os.path.join(assets_path, "keuangan_icon.png"))
        self.submenu_wilayah_rohani.add_button("proker_wr", "Program Kerja (WR)", os.path.join(assets_path, "kalender_icon.png"))
        self.submenu_wilayah_rohani.add_button("struktur_wr", "Struktur Organisasi", os.path.join(assets_path, "structure_icon.png"))
        self.menu_layout.addWidget(self.submenu_wilayah_rohani)

        # Connect Wilayah Rohani toggle
        self.menu_wilayah_rohani.toggled.connect(self.on_wilayah_rohani_toggled)
        self.submenu_wilayah_rohani.menu_clicked.connect(self.on_submenu_clicked)

        # ============ MENU KELOMPOK KATEGORIAL (EXPANDABLE) ============
        self.menu_kelompok_kategorial = ExpandableMenuButton("Kelompok Kategorial", os.path.join(assets_path, "kategorial_icon.png"))
        self.menu_layout.addWidget(self.menu_kelompok_kategorial)

        # Submenu Kelompok Kategorial (sorted alphabetically)
        self.submenu_kelompok_kategorial = VerticalSubMenu()
        self.submenu_kelompok_kategorial.add_button("keuangan_kategorial", "Keuangan (K. Kategorial)", os.path.join(assets_path, "keuangan_icon.png"))
        self.submenu_kelompok_kategorial.add_button("proker_kategorial", "Program Kerja", os.path.join(assets_path, "kalender_icon.png"))
        self.submenu_kelompok_kategorial.add_button("struktur_kategorial", "Struktur Organisasi", os.path.join(assets_path, "structure_icon.png"))
        self.menu_layout.addWidget(self.submenu_kelompok_kategorial)

        # Connect Kelompok Kategorial toggle
        self.menu_kelompok_kategorial.toggled.connect(self.on_kelompok_kategorial_toggled)
        self.submenu_kelompok_kategorial.menu_clicked.connect(self.on_submenu_clicked)

        # ============ MENU BUKU KRONIK ============
        # Icon akan switch otomatis antara book_icon.png (tidak aktif) dan book_active_icon.png (aktif)
        self.menu_buku_kronik = SidebarButton("Buku Kronik", os.path.join(assets_path, "book_icon.png"))
        self.menu_buku_kronik.clicked.connect(self.on_buku_kronik_clicked)
        self.menu_layout.addWidget(self.menu_buku_kronik)

        # ============ MENU RIWAYAT ============
        self.menu_riwayat = SidebarButton("Riwayat", os.path.join(assets_path, "riwayat_icon.png"))
        self.menu_riwayat.clicked.connect(self.on_riwayat_clicked)
        self.menu_layout.addWidget(self.menu_riwayat)

        # ============ MENU PENGATURAN SISTEM ============
        self.menu_pengaturan = SidebarButton("Pengaturan Sistem", os.path.join(assets_path, "pengaturan_icon.png"))
        self.menu_pengaturan.clicked.connect(self.on_pengaturan_clicked)
        self.menu_layout.addWidget(self.menu_pengaturan)

        # Add stretch untuk menghilangkan scroll dan membuat menu kompak
        self.menu_layout.addStretch(1)

        # Scroll area
        scroll_area.setWidget(menu_container)
        layout.addWidget(scroll_area, 1)  # Stretch factor 1 - grow dengan tersedia space

        # Status API - selalu di bawah
        status_container = self.create_status_container()
        layout.addWidget(status_container, 0)  # No stretch - fixed height

        # Timer untuk update status API secara berkala
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_api_status)
        self.status_timer.start(10000)  # Update setiap 10 detik

    def on_dashboard_clicked(self):
        """Handle Dashboard menu click"""
        # Deselect semua menu expandable dan sembunyikan submenu
        self.deselect_all_expandable_menus()
        # Deselect semua menu utama lain
        self.menu_buku_kronik.setChecked(False)
        self.menu_riwayat.setChecked(False)
        self.menu_pengaturan.setChecked(False)
        # Reset semua submenu
        self.submenu_pusat_paroki.reset_buttons()
        self.submenu_wilayah_rohani.reset_buttons()
        self.submenu_kelompok_kategorial.reset_buttons()
        # Dashboard tetap selected
        self.menu_dashboard.setChecked(True)

        # Update icon untuk semua menu
        self.menu_dashboard.update_icon_state()
        self.menu_buku_kronik.update_icon_state()
        self.menu_riwayat.update_icon_state()
        self.menu_pengaturan.update_icon_state()

        self.menu_selected.emit("dashboard")

    def on_buku_kronik_clicked(self):
        """Handle Buku Kronik menu click"""
        # Deselect semua menu expandable dan sembunyikan submenu
        self.deselect_all_expandable_menus()
        # Deselect semua menu utama lain
        self.menu_dashboard.setChecked(False)
        self.menu_riwayat.setChecked(False)
        self.menu_pengaturan.setChecked(False)
        # Reset semua submenu
        self.submenu_pusat_paroki.reset_buttons()
        self.submenu_wilayah_rohani.reset_buttons()
        self.submenu_kelompok_kategorial.reset_buttons()
        # Buku Kronik tetap selected
        self.menu_buku_kronik.setChecked(True)

        # Update icon untuk semua menu (pastikan icon berubah sesuai state)
        self.menu_dashboard.update_icon_state()
        self.menu_buku_kronik.update_icon_state()
        self.menu_riwayat.update_icon_state()
        self.menu_pengaturan.update_icon_state()

        self.menu_selected.emit("buku_kronik")

    def on_riwayat_clicked(self):
        """Handle Riwayat menu click"""
        # Deselect semua menu expandable dan sembunyikan submenu
        self.deselect_all_expandable_menus()
        # Deselect semua menu utama lain
        self.menu_dashboard.setChecked(False)
        self.menu_buku_kronik.setChecked(False)
        self.menu_pengaturan.setChecked(False)
        # Reset semua submenu
        self.submenu_pusat_paroki.reset_buttons()
        self.submenu_wilayah_rohani.reset_buttons()
        self.submenu_kelompok_kategorial.reset_buttons()
        # Riwayat tetap selected
        self.menu_riwayat.setChecked(True)

        # Update icon untuk semua menu
        self.menu_dashboard.update_icon_state()
        self.menu_buku_kronik.update_icon_state()
        self.menu_riwayat.update_icon_state()
        self.menu_pengaturan.update_icon_state()

        self.menu_selected.emit("riwayat")

    def on_pengaturan_clicked(self):
        """Handle Pengaturan Sistem menu click"""
        # Deselect semua menu expandable dan sembunyikan submenu
        self.deselect_all_expandable_menus()
        # Deselect semua menu utama lain
        self.menu_dashboard.setChecked(False)
        self.menu_buku_kronik.setChecked(False)
        self.menu_riwayat.setChecked(False)
        # Reset semua submenu
        self.submenu_pusat_paroki.reset_buttons()
        self.submenu_wilayah_rohani.reset_buttons()
        self.submenu_kelompok_kategorial.reset_buttons()
        # Pengaturan tetap selected
        self.menu_pengaturan.setChecked(True)

        # Update icon untuk semua menu
        self.menu_dashboard.update_icon_state()
        self.menu_buku_kronik.update_icon_state()
        self.menu_riwayat.update_icon_state()
        self.menu_pengaturan.update_icon_state()

        self.menu_selected.emit("pengaturan_sistem")

    def on_pusat_paroki_toggled(self, expanded):
        """Handle Pusat Paroki toggle"""
        if expanded:
            # Deselect semua regular menu
            self.deselect_all_regular_menus()
            # Deselect menu expandable lain
            self.menu_wilayah_rohani.setChecked(False)
            self.menu_kelompok_kategorial.setChecked(False)
            # Reset semua submenu lain
            self.submenu_wilayah_rohani.reset_buttons()
            self.submenu_kelompok_kategorial.reset_buttons()
            # Pastikan menu Pusat Paroki tetap checked (highlighted)
            self.menu_pusat_paroki.setChecked(True)
            # Show submenu Pusat Paroki
            self.submenu_pusat_paroki.show_submenu()
        else:
            self.submenu_pusat_paroki.hide_submenu()
            self.submenu_pusat_paroki.reset_buttons()

    def on_wilayah_rohani_toggled(self, expanded):
        """Handle Wilayah Rohani toggle"""
        if expanded:
            # Deselect semua regular menu
            self.deselect_all_regular_menus()
            # Deselect menu expandable lain
            self.menu_pusat_paroki.setChecked(False)
            self.menu_kelompok_kategorial.setChecked(False)
            # Reset semua submenu lain
            self.submenu_pusat_paroki.reset_buttons()
            self.submenu_kelompok_kategorial.reset_buttons()
            # Pastikan menu Wilayah Rohani tetap checked (highlighted)
            self.menu_wilayah_rohani.setChecked(True)
            # Show submenu Wilayah Rohani
            self.submenu_wilayah_rohani.show_submenu()
        else:
            self.submenu_wilayah_rohani.hide_submenu()
            self.submenu_wilayah_rohani.reset_buttons()

    def on_kelompok_kategorial_toggled(self, expanded):
        """Handle Kelompok Kategorial toggle"""
        if expanded:
            # Deselect semua regular menu
            self.deselect_all_regular_menus()
            # Deselect menu expandable lain
            self.menu_pusat_paroki.setChecked(False)
            self.menu_wilayah_rohani.setChecked(False)
            # Reset semua submenu lain
            self.submenu_pusat_paroki.reset_buttons()
            self.submenu_wilayah_rohani.reset_buttons()
            # Pastikan menu Kelompok Kategorial tetap checked (highlighted)
            self.menu_kelompok_kategorial.setChecked(True)
            # Show submenu Kelompok Kategorial
            self.submenu_kelompok_kategorial.show_submenu()
        else:
            self.submenu_kelompok_kategorial.hide_submenu()
            self.submenu_kelompok_kategorial.reset_buttons()

    def deselect_all_regular_menus(self):
        """Deselect semua regular menu (non-expandable)"""
        self.menu_dashboard.setChecked(False)
        self.menu_buku_kronik.setChecked(False)
        self.menu_riwayat.setChecked(False)
        self.menu_pengaturan.setChecked(False)

    def deselect_all_expandable_menus(self):
        """Collapse semua expandable menu dan sembunyikan submenu"""
        self.menu_pusat_paroki.set_expanded(False)
        self.menu_wilayah_rohani.set_expanded(False)
        self.menu_kelompok_kategorial.set_expanded(False)
        self.submenu_pusat_paroki.hide_submenu()
        self.submenu_wilayah_rohani.hide_submenu()
        self.submenu_kelompok_kategorial.hide_submenu()

    def hide_other_submenus(self, active_submenu):
        """Sembunyikan submenu lain"""
        if active_submenu != self.submenu_pusat_paroki:
            self.submenu_pusat_paroki.hide_submenu()
            self.menu_pusat_paroki.set_expanded(False)

        if active_submenu != self.submenu_wilayah_rohani:
            self.submenu_wilayah_rohani.hide_submenu()
            self.menu_wilayah_rohani.set_expanded(False)

        if active_submenu != self.submenu_kelompok_kategorial:
            self.submenu_kelompok_kategorial.hide_submenu()
            self.menu_kelompok_kategorial.set_expanded(False)

    def on_submenu_clicked(self, menu_id):
        """Handle submenu click"""
        # Deselect semua regular menu saat submenu diklik
        self.deselect_all_regular_menus()

        # Tentukan parent menu mana yang diklik dan pastikan tetap checked
        # Jika submenu_pusat_paroki yang diklik
        if menu_id in ["struktur_dpp", "proker_dpp",
                       "kegiatan_paroki", "database_umat", "aset", "dokumen", "pengumuman", "tim_pembina"]:
            self.menu_pusat_paroki.setChecked(True)
            # Deselect menu expandable lain
            self.menu_wilayah_rohani.setChecked(False)
            self.menu_kelompok_kategorial.setChecked(False)
            # Reset submenu lain
            self.submenu_wilayah_rohani.reset_buttons()
            self.submenu_kelompok_kategorial.reset_buttons()
        # Jika submenu_wilayah_rohani yang diklik
        elif menu_id in ["struktur_wr", "keuangan_wr", "proker_wr", "kegiatan_wr"]:
            self.menu_wilayah_rohani.setChecked(True)
            # Deselect menu expandable lain
            self.menu_pusat_paroki.setChecked(False)
            self.menu_kelompok_kategorial.setChecked(False)
            # Reset submenu lain
            self.submenu_pusat_paroki.reset_buttons()
            self.submenu_kelompok_kategorial.reset_buttons()
        # Jika submenu_kelompok_kategorial yang diklik
        elif menu_id in ["struktur_kategorial", "keuangan_kategorial", "proker_kategorial"]:
            self.menu_kelompok_kategorial.setChecked(True)
            # Deselect menu expandable lain
            self.menu_pusat_paroki.setChecked(False)
            self.menu_wilayah_rohani.setChecked(False)
            # Reset submenu lain
            self.submenu_pusat_paroki.reset_buttons()
            self.submenu_wilayah_rohani.reset_buttons()

        self.menu_selected.emit(menu_id)

    def deselect_other_expandable_menus(self, active_menu):
        """Deselect semua expandable menu kecuali yang aktif"""
        if active_menu != self.menu_pusat_paroki:
            self.menu_pusat_paroki.setChecked(False)
        if active_menu != self.menu_wilayah_rohani:
            self.menu_wilayah_rohani.setChecked(False)
        if active_menu != self.menu_kelompok_kategorial:
            self.menu_kelompok_kategorial.setChecked(False)

    def set_database_manager(self, db_manager):
        """Set database manager untuk cek status API"""
        self.db_manager = db_manager
        self.update_api_status()

    def create_header(self):
        """Buat header sidebar dengan logo dan judul"""
        header = QWidget()
        header.setMinimumHeight(90)
        header.setStyleSheet("background-color: #002B36; border-bottom: 1px solid #2D2B3F;")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 8, 10, 8)
        header_layout.setSpacing(8)

        # Logo di sebelah kiri
        logo_label = QLabel()
        logo_path = "server/assets/logo_gereja.png"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Jika logo tidak ada, buat placeholder
            logo_label.setText("LOGO")
            logo_label.setStyleSheet("color: white; font-weight: bold; background-color: #2D2B3F; border-radius: 25px; text-align: center;")

        logo_label.setFixedSize(50, 50)
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)

        # Layout vertikal untuk judul dan subtitle - KOMPAK 3 BARIS
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(1)
        title_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Baris 1: PAROKI SANTA MARIA
        title_line1 = QLabel("PAROKI SANTA MARIA")
        title_line1.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 11px;
                font-weight: bold;
                background-color: transparent;
                margin: 0px;
                padding: 0px;
            }
        """)
        title_line1.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Baris 2: RATU DAMAI, ULUINDANO
        title_line2 = QLabel("RATU DAMAI, ULUINDANO")
        title_line2.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 11px;
                font-weight: bold;
                background-color: transparent;
                margin: 0px;
                padding: 0px;
            }
        """)
        title_line2.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Baris 3: Admin Panel (API Mode)
        subtitle = QLabel("Admin Panel (API Mode)")
        subtitle.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 9px;
                background-color: transparent;
                margin: 0px;
                padding: 0px;
            }
        """)
        subtitle.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        title_layout.addWidget(title_line1, 0)
        title_layout.addWidget(title_line2, 0)
        title_layout.addWidget(subtitle, 0)

        header_layout.addLayout(title_layout, 1)

        return header

    def create_status_container(self):
        """Buat container untuk status API"""
        status_container = QWidget()
        status_container.setFixedHeight(80)
        status_container.setStyleSheet("background-color: #F8F9FA; border-top: 1px solid #E0E0E0;")

        status_layout = QVBoxLayout(status_container)
        status_layout.setContentsMargins(15, 8, 15, 8)
        status_layout.setAlignment(Qt.AlignCenter)

        # Status API dengan ikon
        self.api_status = QLabel("🔴 API: Mengecek...")
        self.api_status.setStyleSheet("""
            color: #e74c3c;
            font-size: 11px;
            font-weight: bold;
            padding: 3px;
            background-color: rgba(231, 76, 60, 0.1);
            border-radius: 3px;
        """)
        self.api_status.setAlignment(Qt.AlignCenter)

        # Status koneksi
        self.connection_status = QLabel("🌐 Koneksi: Tidak diketahui")
        self.connection_status.setStyleSheet("""
            color: #f39c12;
            font-size: 10px;
            padding: 2px;
            background-color: rgba(243, 156, 18, 0.1);
            border-radius: 3px;
        """)
        self.connection_status.setAlignment(Qt.AlignCenter)

        status_layout.addWidget(self.api_status)
        status_layout.addWidget(self.connection_status)

        return status_container

    def update_api_status(self):
        """Update status API dari database manager"""
        if not self.db_manager:
            self.set_api_offline()
            return

        try:
            # Cek status API
            success, status_data = self.db_manager.get_api_service_status()

            if success and status_data.get('api_enabled', False):
                self.set_api_active()

                # Cek jumlah client yang benar-benar terhubung/aktif
                client_success, result = self.db_manager.get_active_sessions()
                if client_success:
                    # Handle berbagai format response dari API
                    if isinstance(result, dict):
                        if 'data' in result:
                            clients = result['data']
                        elif 'clients' in result:
                            clients = result['clients']
                        else:
                            clients = []
                    elif isinstance(result, list):
                        clients = result
                    else:
                        clients = []

                    # Filter hanya client yang benar-benar aktif dengan timeout check
                    import datetime
                    active_clients = []
                    current_time = datetime.datetime.now()

                    for client in clients:
                        status = client.get('status', '').lower()
                        last_activity = client.get('last_activity') or client.get('connect_time')

                        # Check jika client benar-benar aktif berdasarkan status dan waktu aktivitas terakhir
                        is_active = False
                        if status in ['aktif', 'active', 'terhubung', 'connected', 'online']:
                            if last_activity:
                                try:
                                    if isinstance(last_activity, str):
                                        if 'T' in last_activity:
                                            last_time = datetime.datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                                        else:
                                            last_time = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
                                    else:
                                        last_time = last_activity

                                    # Client dianggap aktif jika aktivitas terakhir kurang dari 5 menit yang lalu
                                    time_diff = current_time - last_time.replace(tzinfo=None)
                                    if time_diff.total_seconds() < 300:  # 5 menit
                                        is_active = True
                                except:
                                    pass

                        if is_active:
                            active_clients.append(client)

                    client_count = len(active_clients)
                    self.connection_status.setText(f"🌐 Client Aktif: {client_count}")
                    self.connection_status.setStyleSheet("""
                        color: #27ae60;
                        font-size: 10px;
                        padding: 2px;
                        background-color: rgba(39, 174, 96, 0.1);
                        border-radius: 3px;
                    """)
                else:
                    self.connection_status.setText("🌐 Koneksi: Error")
                    self.connection_status.setStyleSheet("""
                        color: #e74c3c;
                        font-size: 10px;
                        padding: 2px;
                        background-color: rgba(231, 76, 60, 0.1);
                        border-radius: 3px;
                    """)
            else:
                self.set_api_offline()
        except:
            self.set_api_error()

    def set_api_active(self):
        """Set status API aktif"""
        self.api_status.setText("🟢 API: Aktif")
        self.api_status.setStyleSheet("""
            color: #2ecc71;
            font-size: 11px;
            font-weight: bold;
            padding: 3px;
            background-color: rgba(46, 204, 113, 0.1);
            border-radius: 3px;
        """)

    def set_api_offline(self):
        """Set status API non-aktif"""
        self.api_status.setText("🔴 API: Non-aktif")
        self.api_status.setStyleSheet("""
            color: #e74c3c;
            font-size: 11px;
            font-weight: bold;
            padding: 3px;
            background-color: rgba(231, 76, 60, 0.1);
            border-radius: 3px;
        """)

        self.connection_status.setText("🌐 Tidak ada koneksi")
        self.connection_status.setStyleSheet("""
            color: #7f8c8d;
            font-size: 10px;
            padding: 2px;
            background-color: rgba(127, 140, 141, 0.1);
            border-radius: 3px;
        """)

    def set_api_error(self):
        """Set status API error"""
        self.api_status.setText("⚠️ API: Error")
        self.api_status.setStyleSheet("""
            color: #f39c12;
            font-size: 11px;
            font-weight: bold;
            padding: 3px;
            background-color: rgba(243, 156, 18, 0.1);
            border-radius: 3px;
        """)

        self.connection_status.setText("🌐 Koneksi bermasalah")
        self.connection_status.setStyleSheet("""
            color: #f39c12;
            font-size: 10px;
            padding: 2px;
            background-color: rgba(243, 156, 18, 0.1);
            border-radius: 3px;
        """)

    def reset_menu_selection(self):
        """Reset semua pilihan menu"""
        self.menu_dashboard.setChecked(False)
        self.menu_pusat_paroki.setChecked(False)
        self.menu_wilayah_rohani.setChecked(False)
        self.menu_kelompok_kategorial.setChecked(False)
        self.menu_buku_kronik.setChecked(False)
        self.menu_riwayat.setChecked(False)
        self.menu_pengaturan.setChecked(False)

        # Reset submenu
        self.submenu_pusat_paroki.reset_buttons()
        self.submenu_wilayah_rohani.reset_buttons()
        self.submenu_kelompok_kategorial.reset_buttons()

    def show_submenu(self, submenu):
        """Tampilkan submenu tertentu"""
        submenu.show_submenu()

    def hide_submenu(self, submenu):
        """Sembunyikan submenu tertentu"""
        submenu.hide_submenu()
