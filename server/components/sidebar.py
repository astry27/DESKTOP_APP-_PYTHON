# Path: server/components/sidebar.py

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from .vertical_submenu import VerticalSubMenu
from .expandable_menu_button import ExpandableMenuButton


class SidebarButton(QPushButton):
    """Custom button untuk sidebar"""
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setAutoExclusive(False)  # PENTING: Non-exclusive untuk kontrol manual
        self.setFixedHeight(45)

        # Set style untuk menu utama - background transparan, teks putih
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: normal;
                background-color: transparent;
                color: #ffffff;
                margin: 4px 8px;
            }
            QPushButton:hover {
                background-color: rgba(38, 139, 210, 0.12);
                color: #ffffff;
            }
            QPushButton:checked {
                background-color: rgba(38, 139, 210, 0.2);
                color: #ffffff;
                font-weight: bold;
                border-radius: 6px;
                border-left: 3px solid #2aa198;
                padding-left: 12px;
                margin: 4px 8px;
            }
        """)

        # Set icon dari file path
        self.icon_path = icon_path

        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(18, 18))

    def update_icon_state(self):
        """Update icon state - tidak melakukan apa-apa karena active icon sudah dihilangkan"""
        pass


class SidebarWidget(QWidget):
    """Widget untuk sidebar navigasi dengan menu bercabang"""

    # Signal untuk menu yang dipilih
    menu_selected = pyqtSignal(str)
    # Signal untuk logout
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)

        # Set style untuk sidebar utama - background biru gelap matching header
        self.setStyleSheet("background-color: #002B36;")

        # Layout utama
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header sidebar
        header = self.create_header()
        layout.addWidget(header)

        # Line pembatas antara header dan menu navigasi
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #586e75;")
        layout.addWidget(separator)

        # Scroll area untuk menu
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hilangkan scroll horizontal
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #002B36;
            }
            QScrollBar:vertical {
                width: 8px;
                background-color: #002B36;
            }
            QScrollBar::handle:vertical {
                background-color: #586e75;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #657b83;
            }
            QScrollBar:horizontal {
                height: 0px;
            }
        """)

        # Container untuk menu navigasi
        menu_container = QWidget()
        menu_container.setStyleSheet("background-color: #002B36;")
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

        # Tombol Logout - selalu di bawah
        logout_container = self.create_logout_button()
        layout.addWidget(logout_container, 0)  # No stretch - fixed height

    def on_dashboard_clicked(self):
        """Handle Dashboard menu click"""
        # PENTING: Prevent recursive call saat programmatic setChecked
        if self.menu_dashboard.isChecked():
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
        # PENTING: Prevent recursive call saat programmatic setChecked
        if self.menu_buku_kronik.isChecked():
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
        # PENTING: Prevent recursive call saat programmatic setChecked
        if self.menu_riwayat.isChecked():
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
        # PENTING: Prevent recursive call saat programmatic setChecked
        if self.menu_pengaturan.isChecked():
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
            # Deselect menu expandable lain dan hide submenu mereka
            self.menu_wilayah_rohani.set_expanded(False)
            self.menu_wilayah_rohani.setChecked(False)
            self.menu_wilayah_rohani.update_icon_state()
            self.submenu_wilayah_rohani.hide_submenu()

            self.menu_kelompok_kategorial.set_expanded(False)
            self.menu_kelompok_kategorial.setChecked(False)
            self.menu_kelompok_kategorial.update_icon_state()
            self.submenu_kelompok_kategorial.hide_submenu()

            # Reset semua submenu lain
            self.submenu_wilayah_rohani.reset_buttons()
            self.submenu_kelompok_kategorial.reset_buttons()
            # Reset submenu Pusat Paroki juga
            self.submenu_pusat_paroki.reset_buttons()
            # Pastikan menu Pusat Paroki tetap checked (highlighted)
            self.menu_pusat_paroki.setChecked(True)
            self.menu_pusat_paroki.update_icon_state()
            # Update icon untuk semua menu regular
            self.menu_dashboard.update_icon_state()
            self.menu_buku_kronik.update_icon_state()
            self.menu_riwayat.update_icon_state()
            self.menu_pengaturan.update_icon_state()
            # Show submenu Pusat Paroki
            self.submenu_pusat_paroki.show_submenu()
        else:
            self.submenu_pusat_paroki.hide_submenu()
            self.submenu_pusat_paroki.reset_buttons()
            self.menu_pusat_paroki.setChecked(False)
            self.menu_pusat_paroki.update_icon_state()

    def on_wilayah_rohani_toggled(self, expanded):
        """Handle Wilayah Rohani toggle"""
        if expanded:
            # Deselect semua regular menu
            self.deselect_all_regular_menus()
            # Deselect menu expandable lain dan hide submenu mereka
            self.menu_pusat_paroki.set_expanded(False)
            self.menu_pusat_paroki.setChecked(False)
            self.menu_pusat_paroki.update_icon_state()
            self.submenu_pusat_paroki.hide_submenu()

            self.menu_kelompok_kategorial.set_expanded(False)
            self.menu_kelompok_kategorial.setChecked(False)
            self.menu_kelompok_kategorial.update_icon_state()
            self.submenu_kelompok_kategorial.hide_submenu()

            # Reset semua submenu lain
            self.submenu_pusat_paroki.reset_buttons()
            self.submenu_kelompok_kategorial.reset_buttons()
            # Reset submenu Wilayah Rohani juga
            self.submenu_wilayah_rohani.reset_buttons()
            # Pastikan menu Wilayah Rohani tetap checked (highlighted)
            self.menu_wilayah_rohani.setChecked(True)
            self.menu_wilayah_rohani.update_icon_state()
            # Update icon untuk semua menu regular
            self.menu_dashboard.update_icon_state()
            self.menu_buku_kronik.update_icon_state()
            self.menu_riwayat.update_icon_state()
            self.menu_pengaturan.update_icon_state()
            # Show submenu Wilayah Rohani
            self.submenu_wilayah_rohani.show_submenu()
        else:
            self.submenu_wilayah_rohani.hide_submenu()
            self.submenu_wilayah_rohani.reset_buttons()
            self.menu_wilayah_rohani.setChecked(False)
            self.menu_wilayah_rohani.update_icon_state()

    def on_kelompok_kategorial_toggled(self, expanded):
        """Handle Kelompok Kategorial toggle"""
        if expanded:
            # Deselect semua regular menu
            self.deselect_all_regular_menus()
            # Deselect menu expandable lain dan hide submenu mereka
            self.menu_pusat_paroki.set_expanded(False)
            self.menu_pusat_paroki.setChecked(False)
            self.menu_pusat_paroki.update_icon_state()
            self.submenu_pusat_paroki.hide_submenu()

            self.menu_wilayah_rohani.set_expanded(False)
            self.menu_wilayah_rohani.setChecked(False)
            self.menu_wilayah_rohani.update_icon_state()
            self.submenu_wilayah_rohani.hide_submenu()

            # Reset semua submenu lain
            self.submenu_pusat_paroki.reset_buttons()
            self.submenu_wilayah_rohani.reset_buttons()
            # Reset submenu Kelompok Kategorial juga
            self.submenu_kelompok_kategorial.reset_buttons()
            # Pastikan menu Kelompok Kategorial tetap checked (highlighted)
            self.menu_kelompok_kategorial.setChecked(True)
            self.menu_kelompok_kategorial.update_icon_state()
            # Update icon untuk semua menu regular
            self.menu_dashboard.update_icon_state()
            self.menu_buku_kronik.update_icon_state()
            self.menu_riwayat.update_icon_state()
            self.menu_pengaturan.update_icon_state()
            # Show submenu Kelompok Kategorial
            self.submenu_kelompok_kategorial.show_submenu()
        else:
            self.submenu_kelompok_kategorial.hide_submenu()
            self.submenu_kelompok_kategorial.reset_buttons()
            self.menu_kelompok_kategorial.setChecked(False)
            self.menu_kelompok_kategorial.update_icon_state()

    def deselect_all_regular_menus(self):
        """Deselect semua regular menu (non-expandable)"""
        self.menu_dashboard.setChecked(False)
        self.menu_dashboard.update_icon_state()
        self.menu_buku_kronik.setChecked(False)
        self.menu_buku_kronik.update_icon_state()
        self.menu_riwayat.setChecked(False)
        self.menu_riwayat.update_icon_state()
        self.menu_pengaturan.setChecked(False)
        self.menu_pengaturan.update_icon_state()

    def deselect_all_expandable_menus(self):
        """Collapse semua expandable menu dan sembunyikan submenu"""
        self.menu_pusat_paroki.set_expanded(False)
        self.menu_pusat_paroki.setChecked(False)
        self.menu_pusat_paroki.update_icon_state()
        self.menu_wilayah_rohani.set_expanded(False)
        self.menu_wilayah_rohani.setChecked(False)
        self.menu_wilayah_rohani.update_icon_state()
        self.menu_kelompok_kategorial.set_expanded(False)
        self.menu_kelompok_kategorial.setChecked(False)
        self.menu_kelompok_kategorial.update_icon_state()
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

        # Tentukan parent menu mana yang diklik dan uncheck parent menu
        # Active state hanya pada submenu yang diklik
        # Jika submenu_pusat_paroki yang diklik
        if menu_id in ["struktur_dpp", "proker_dpp",
                       "kegiatan_paroki", "database_umat", "aset", "dokumen", "pengumuman", "tim_pembina"]:
            # Uncheck parent menu - active state pindah ke submenu
            self.menu_pusat_paroki.setChecked(False)
            self.menu_pusat_paroki.update_icon_state()
            # Deselect menu expandable lain
            self.menu_wilayah_rohani.setChecked(False)
            self.menu_wilayah_rohani.update_icon_state()
            self.menu_kelompok_kategorial.setChecked(False)
            self.menu_kelompok_kategorial.update_icon_state()
            # Reset submenu lain
            self.submenu_wilayah_rohani.reset_buttons()
            self.submenu_kelompok_kategorial.reset_buttons()
        # Jika submenu_wilayah_rohani yang diklik
        elif menu_id in ["struktur_wr", "keuangan_wr", "proker_wr", "kegiatan_wr"]:
            # Uncheck parent menu - active state pindah ke submenu
            self.menu_wilayah_rohani.setChecked(False)
            self.menu_wilayah_rohani.update_icon_state()
            # Deselect menu expandable lain
            self.menu_pusat_paroki.setChecked(False)
            self.menu_pusat_paroki.update_icon_state()
            self.menu_kelompok_kategorial.setChecked(False)
            self.menu_kelompok_kategorial.update_icon_state()
            # Reset submenu lain
            self.submenu_pusat_paroki.reset_buttons()
            self.submenu_kelompok_kategorial.reset_buttons()
        # Jika submenu_kelompok_kategorial yang diklik
        elif menu_id in ["struktur_kategorial", "keuangan_kategorial", "proker_kategorial"]:
            # Uncheck parent menu - active state pindah ke submenu
            self.menu_kelompok_kategorial.setChecked(False)
            self.menu_kelompok_kategorial.update_icon_state()
            # Deselect menu expandable lain
            self.menu_pusat_paroki.setChecked(False)
            self.menu_pusat_paroki.update_icon_state()
            self.menu_wilayah_rohani.setChecked(False)
            self.menu_wilayah_rohani.update_icon_state()
            # Reset submenu lain
            self.submenu_pusat_paroki.reset_buttons()
            self.submenu_wilayah_rohani.reset_buttons()

        # Update icon untuk semua menu regular juga
        self.menu_dashboard.update_icon_state()
        self.menu_buku_kronik.update_icon_state()
        self.menu_riwayat.update_icon_state()
        self.menu_pengaturan.update_icon_state()

        self.menu_selected.emit(menu_id)

    def deselect_other_expandable_menus(self, active_menu):
        """Deselect semua expandable menu kecuali yang aktif"""
        if active_menu != self.menu_pusat_paroki:
            self.menu_pusat_paroki.setChecked(False)
        if active_menu != self.menu_wilayah_rohani:
            self.menu_wilayah_rohani.setChecked(False)
        if active_menu != self.menu_kelompok_kategorial:
            self.menu_kelompok_kategorial.setChecked(False)

    def create_header(self):
        """Buat header sidebar dengan logo dan judul"""
        header = QWidget()
        header.setMinimumHeight(90)
        header.setStyleSheet("background-color: #002B36;")

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

    def create_logout_button(self):
        """Buat tombol logout dan refresh di bagian bawah sidebar"""
        logout_container = QWidget()
        logout_container.setFixedHeight(80)
        logout_container.setStyleSheet("background-color: #002B36; border-top: 1px solid #586e75;")

        main_layout = QVBoxLayout(logout_container)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(8)

        # Layout horizontal untuk button logout dan refresh
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        # Tombol Logout dengan icon (di kiri)
        logout_btn = QPushButton("Logout")
        logout_btn.setFixedHeight(40)
        logout_btn.setCursor(Qt.PointingHandCursor)

        # Set icon logout
        logout_icon_path = "server/assets/logout.png"
        if os.path.exists(logout_icon_path):
            logout_btn.setIcon(QIcon(logout_icon_path))
            logout_btn.setIconSize(QSize(18, 18))

        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #073642;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #0a4a5a;
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: #002b36;
            }
        """)
        logout_btn.clicked.connect(self.on_logout_clicked)

        # Tombol Refresh dengan icon dan teks (di kanan)
        refresh_btn = QPushButton(" Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setToolTip("Refresh data")

        # Set icon refresh
        refresh_icon_path = "server/assets/refresh.png"
        if os.path.exists(refresh_icon_path):
            refresh_btn.setIcon(QIcon(refresh_icon_path))
            refresh_btn.setIconSize(QSize(18, 18))

        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #073642;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #0a4a5a;
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: #002b36;
            }
        """)
        refresh_btn.clicked.connect(self.on_refresh_clicked)

        # Tambahkan ke layout: logout kiri, refresh kanan
        button_layout.addWidget(logout_btn, 1)
        button_layout.addWidget(refresh_btn, 1)

        main_layout.addLayout(button_layout)

        return logout_container

    def on_refresh_clicked(self):
        """Handle klik tombol refresh untuk reload data komponen saat ini"""
        # Emit signal untuk refresh data
        if hasattr(self.parent(), 'refresh_current_component'):
            self.parent().refresh_current_component()

    def on_logout_clicked(self):
        """Handle klik tombol logout dengan konfirmasi"""
        from PyQt5.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setWindowTitle("Konfirmasi Keluar")
        msg.setText("Keluar akan menutup sesi Anda saat ini. Lanjutkan?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)

        # Set button text ke bahasa Indonesia
        yes_btn = msg.button(QMessageBox.Yes)
        yes_btn.setText("Yes")
        cancel_btn = msg.button(QMessageBox.Cancel)
        cancel_btn.setText("Cancel")

        # Force transparent background untuk semua child labels (termasuk icon)
        for child in msg.findChildren(QLabel):
            child.setStyleSheet("background-color: transparent; background: transparent;")
            child.setAutoFillBackground(False)

        # Apply button styling langsung ke setiap button dengan force override
        button_style = """
            QPushButton {
                min-width: 75px;
                min-height: 23px;
                padding: 3px 10px;
                font-size: 11px;
                border: 1px solid #41ADFF !important;
                border-radius: 0px;
                background-color: #F0F0F0 !important;
                background: #F0F0F0 !important;
                color: #000000 !important;
            }
            QPushButton:hover {
                background-color: #e5f1fb !important;
                background: #e5f1fb !important;
                border: 1px solid #41ADFF !important;
            }
            QPushButton:pressed {
                background-color: #cce4f7 !important;
                background: #cce4f7 !important;
                border: 1px solid #41ADFF !important;
            }
        """
        yes_btn.setStyleSheet(button_style)
        yes_btn.setAutoFillBackground(True)
        cancel_btn.setStyleSheet(button_style)
        cancel_btn.setAutoFillBackground(True)

        # Custom styling untuk dialog konfirmasi - menghilangkan background icon dan update warna button
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
            }
            /* Hilangkan background pada semua label termasuk icon */
            QMessageBox QLabel {
                color: #000000;
                font-size: 12px;
                background-color: transparent;
                background: transparent;
                padding: 10px;
            }
            QMessageBox QLabel#qt_msgbox_label {
                background-color: transparent;
                background: transparent;
            }
            QMessageBox QLabel#qt_msgbox_icon_label {
                background-color: transparent;
                background: transparent;
            }
            /* Style untuk button dengan warna custom */
            QMessageBox QPushButton {
                min-width: 75px;
                min-height: 23px;
                padding: 3px 10px;
                font-size: 11px;
                border: 1px solid #41ADFF;
                border-radius: 0px;
                background-color: #F0F0F0;
                color: #000000;
            }
            QMessageBox QPushButton:hover {
                background-color: #e5f1fb;
                border: 1px solid #41ADFF;
            }
            QMessageBox QPushButton:pressed {
                background-color: #cce4f7;
                border: 1px solid #41ADFF;
            }
            QMessageBox QPushButton:focus {
                background-color: #e5f1fb;
                border: 1px solid #41ADFF;
                outline: none;
            }
        """)

        result = msg.exec_()

        if result == QMessageBox.Yes:
            # Emit signal logout untuk ditangani oleh main window
            self.logout_requested.emit()


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
