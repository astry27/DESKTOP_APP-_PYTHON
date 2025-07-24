# Path: server/components/__init__.py

"""
Components package untuk aplikasi Server Gereja Katolik

Package ini berisi komponen-komponen modular yang membentuk aplikasi:
- dialogs: Dialog-dialog untuk input data
- sidebar: Komponen sidebar navigasi  
- dashboard: Komponen dashboard utama
- jemaat: Komponen manajemen data jemaat
- jadwal: Komponen manajemen jadwal kegiatan
- keuangan: Komponen manajemen keuangan
- pengumuman: Komponen manajemen pengumuman
- pengaturan: Komponen pengaturan sistem
- server_control: Komponen kontrol server

Setiap komponen dirancang sebagai widget PyQt5 yang independen
dengan komunikasi melalui signals dan slots.
"""

__version__ = "1.0.0"
__author__ = "Developer Team"

# Tidak melakukan import otomatis untuk menghindari circular import
# Import manual sesuai kebutuhan di setiap file yang menggunakan