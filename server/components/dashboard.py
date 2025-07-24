# Path: server/components/dashboard.py

import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QGroupBox, 
                            QLabel, QListWidget, QTextBrowser, QScrollArea)
from PyQt5.QtCore import QDate

class DashboardComponent(QWidget):
    """Komponen dashboard untuk menampilkan statistik dan info terbaru"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI dashboard"""
        dashboard_layout = QGridLayout(self)
        
        # Wrapper untuk scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QGridLayout(scroll_content)
        
        # Statistik Jemaat
        jemaat_stats = self.create_stat_group("Statistik Jemaat")
        jemaat_layout = QVBoxLayout(jemaat_stats)
        
        self.jemaat_count_label = QLabel("Total Jemaat: Loading...")
        self.keluarga_count_label = QLabel("Keluarga: Loading...")
        self.lingkungan_count_label = QLabel("Lingkungan: 15")
        self.wilayah_count_label = QLabel("Wilayah: 5")
        
        jemaat_layout.addWidget(self.jemaat_count_label)
        jemaat_layout.addWidget(self.keluarga_count_label)
        jemaat_layout.addWidget(self.lingkungan_count_label)
        jemaat_layout.addWidget(self.wilayah_count_label)
        
        scroll_layout.addWidget(jemaat_stats, 0, 0)
        
        # Jadwal Hari Ini
        jadwal_today = self.create_stat_group("Jadwal Hari Ini")
        jadwal_layout = QVBoxLayout(jadwal_today)
        
        tanggal = QLabel(f"Tanggal: {QDate.currentDate().toString('dd MMMM yyyy')}")
        tanggal.setStyleSheet("font-weight: bold;")
        jadwal_layout.addWidget(tanggal)
        
        self.jadwal_today_list = QListWidget()
        jadwal_layout.addWidget(self.jadwal_today_list)
        
        scroll_layout.addWidget(jadwal_today, 0, 1)
        
        # Aktivitas Terbaru
        aktivitas = self.create_stat_group("Aktivitas Terbaru")
        aktivitas_layout = QVBoxLayout(aktivitas)
        
        self.aktivitas_list = QListWidget()
        aktivitas_layout.addWidget(self.aktivitas_list)
        
        scroll_layout.addWidget(aktivitas, 1, 0)
        
        # Pengumuman Terbaru
        pengumuman = self.create_stat_group("Pengumuman Terbaru")
        pengumuman_layout = QVBoxLayout(pengumuman)
        
        self.pengumuman_text = QTextBrowser()
        pengumuman_layout.addWidget(self.pengumuman_text)
        
        scroll_layout.addWidget(pengumuman, 1, 1)
        
        # Set layout untuk widget scrollable
        scroll_area.setWidget(scroll_content)
        dashboard_layout.addWidget(scroll_area)
    
    def create_stat_group(self, title):
        """Buat group box dengan style konsisten"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        return group
    
    def update_statistics(self, jemaat_data, kegiatan_data, pengumuman_data, db_manager=None):
        """Update statistik dashboard"""
        try:
            # Update statistik jemaat
            jemaat_count = len(jemaat_data) if jemaat_data else 0
            self.jemaat_count_label.setText(f"Total Jemaat: {jemaat_count}")
            
            # Estimasi keluarga (asumsi 1 keluarga = 3-4 orang)
            keluarga_count = max(1, jemaat_count // 4)
            self.keluarga_count_label.setText(f"Keluarga: {keluarga_count}")
            
            # Update jadwal hari ini
            self.update_today_schedule(kegiatan_data)
            
            # Update aktivitas terbaru
            self.update_recent_activities(db_manager)
            
            # Update pengumuman terbaru
            self.update_recent_announcements(pengumuman_data)
            
        except Exception as e:
            print(f"Error updating dashboard: {str(e)}")
    
    def update_today_schedule(self, kegiatan_data):
        """Update jadwal hari ini"""
        self.jadwal_today_list.clear()
        today = datetime.date.today()
        
        for kegiatan in kegiatan_data:
            try:
                tanggal_mulai = kegiatan.get('tanggal_mulai')
                if tanggal_mulai:
                    if hasattr(tanggal_mulai, 'date'):
                        kegiatan_date = tanggal_mulai.date()
                    else:
                        kegiatan_date = datetime.datetime.strptime(str(tanggal_mulai), '%Y-%m-%d').date()
                    
                    if kegiatan_date == today:
                        nama_kegiatan = kegiatan.get('nama_kegiatan', 'Kegiatan')
                        lokasi = kegiatan.get('lokasi', '')
                        self.jadwal_today_list.addItem(f"{nama_kegiatan} - {lokasi}")
            except:
                continue
        
        if self.jadwal_today_list.count() == 0:
            self.jadwal_today_list.addItem("Tidak ada kegiatan hari ini")
    
    def update_recent_activities(self, db_manager):
        """Update aktivitas terbaru"""
        self.aktivitas_list.clear()
        
        if db_manager:
            try:
                success, messages = db_manager.get_recent_messages(limit=5)
                if success and messages:
                    for msg in messages[-5:]:
                        timestamp = msg.get('waktu_kirim', datetime.datetime.now())
                        if hasattr(timestamp, 'strftime'):
                            time_str = timestamp.strftime('%H:%M')
                        else:
                            time_str = str(timestamp)[:5]
                        
                        pengirim = msg.get('nama_lengkap', 'System')
                        pesan = msg.get('pesan', '')[:50] + "..." if len(msg.get('pesan', '')) > 50 else msg.get('pesan', '')
                        
                        self.aktivitas_list.addItem(f"{time_str} - {pengirim}: {pesan}")
            except:
                pass
        
        if self.aktivitas_list.count() == 0:
            current_time = datetime.datetime.now().strftime("%H:%M")
            self.aktivitas_list.addItem(f"{current_time} - System: Dashboard diperbarui")
    
    def update_recent_announcements(self, pengumuman_data):
        """Update pengumuman terbaru"""
        if pengumuman_data:
            # Ambil 3 pengumuman terbaru
            latest_announcements = pengumuman_data[:3]
            
            html_content = "<h3>Pengumuman Terbaru</h3>"
            
            for i, pengumuman in enumerate(latest_announcements, 1):
                judul = pengumuman.get('judul', 'Tidak ada judul')
                isi = pengumuman.get('isi', 'Tidak ada isi')
                
                # Truncate isi
                if len(isi) > 100:
                    isi = isi[:100] + "..."
                
                html_content += f"""
                <p><b>{i}. {judul}</b><br>
                {isi}</p>
                """
            
            self.pengumuman_text.setHtml(html_content)
        else:
            self.pengumuman_text.setHtml("<h3>Pengumuman Terbaru</h3><p>Belum ada pengumuman</p>")