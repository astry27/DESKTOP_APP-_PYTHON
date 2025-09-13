# Path: server/components/dashboard.py

import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QGroupBox, 
                            QLabel, QListWidget, QTextBrowser, QScrollArea, QHBoxLayout)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont

class StatisticsChart(QWidget):
    """Widget untuk menampilkan chart statistik jemaat"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 200)
        self.setMaximumSize(400, 250)
        
        # Data statistik default
        self.jemaat_data = {
            'total': 0,
            'keluarga': 0,
            'lingkungan': 15,
            'wilayah': 5,
            'kategori': {
                'Balita': 0,
                'Anak-anak': 0,
                'Remaja': 0,
                'OMK': 0,
                'KBK': 0,
                'KIK': 0,
                'Lansia': 0
            }
        }
    
    def update_data(self, jemaat_data):
        """Update data statistik"""
        total_jemaat = len(jemaat_data) if jemaat_data else 0
        self.jemaat_data['total'] = total_jemaat
        self.jemaat_data['keluarga'] = max(1, total_jemaat // 4)
        
        # Reset kategori
        for kategori in self.jemaat_data['kategori']:
            self.jemaat_data['kategori'][kategori] = 0
        
        # Hitung berdasarkan kategori dari data jemaat
        if jemaat_data:
            for jemaat in jemaat_data:
                kategori = jemaat.get('kategori', '')
                if kategori in self.jemaat_data['kategori']:
                    self.jemaat_data['kategori'][kategori] += 1
        
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Draw the statistics chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(250, 250, 250))
        
        # Draw title
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(QColor(52, 73, 94))
        painter.drawText(10, 20, "Statistik Jemaat")
        
        # Draw main statistics (pie chart)
        self.draw_pie_chart(painter)
        
        # Draw category statistics (bar chart)
        self.draw_bar_chart(painter)
    
    def draw_pie_chart(self, painter):
        """Draw pie chart for main statistics"""
        center_x, center_y = 80, 80
        radius = 40
        
        # Data for pie chart
        total = max(1, self.jemaat_data['total'])
        keluarga = self.jemaat_data['keluarga']
        
        # Colors
        colors = [QColor(52, 152, 219), QColor(46, 204, 113), 
                 QColor(241, 196, 15), QColor(231, 76, 60)]
        
        # Draw pie slices
        start_angle = 0
        
        # Keluarga slice
        if keluarga > 0:
            angle = int(360 * keluarga / total)
            painter.setBrush(QBrush(colors[0]))
            painter.setPen(QPen(Qt.white, 2))
            painter.drawPie(center_x - radius, center_y - radius, 
                          radius * 2, radius * 2, start_angle * 16, angle * 16)
            start_angle += angle
        
        # Individual members slice
        remaining = total - keluarga
        if remaining > 0:
            angle = int(360 * remaining / total)
            painter.setBrush(QBrush(colors[1]))
            painter.drawPie(center_x - radius, center_y - radius, 
                          radius * 2, radius * 2, start_angle * 16, angle * 16)
        
        # Legend
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QColor(44, 62, 80))
        
        y_pos = 140
        painter.fillRect(10, y_pos, 10, 10, colors[0])
        painter.drawText(25, y_pos + 8, f"Keluarga: {keluarga}")
        
        painter.fillRect(10, y_pos + 15, 10, 10, colors[1])
        painter.drawText(25, y_pos + 23, f"Total Jemaat: {total}")
    
    def draw_bar_chart(self, painter):
        """Draw bar chart for category statistics"""
        start_x, start_y = 180, 50
        bar_width = 20
        max_height = 100
        
        # Get category data
        kategori_data = self.jemaat_data['kategori']
        max_value = max(kategori_data.values()) if any(kategori_data.values()) else 1
        
        # Colors for bars
        colors = [QColor(52, 152, 219), QColor(46, 204, 113), QColor(155, 89, 182),
                 QColor(241, 196, 15), QColor(230, 126, 34), QColor(231, 76, 60), 
                 QColor(149, 165, 166)]
        
        x_pos = start_x
        color_idx = 0
        
        for kategori, count in kategori_data.items():
            if max_value > 0:
                bar_height = int(max_height * count / max_value)
            else:
                bar_height = 0
            
            # Draw bar
            painter.setBrush(QBrush(colors[color_idx % len(colors)]))
            painter.setPen(QPen(Qt.white, 1))
            painter.drawRect(x_pos, start_y + max_height - bar_height, 
                           bar_width, bar_height)
            
            # Draw count on top of bar
            if count > 0:
                painter.setPen(QColor(44, 62, 80))
                painter.setFont(QFont("Arial", 7))
                painter.drawText(x_pos + 5, start_y + max_height - bar_height - 5, str(count))
            
            # Draw category label (rotated)
            painter.save()
            painter.translate(x_pos + bar_width//2, start_y + max_height + 5)
            painter.rotate(45)
            painter.setFont(QFont("Arial", 6))
            painter.drawText(0, 0, kategori[:3])  # Show first 3 letters
            painter.restore()
            
            x_pos += bar_width + 5
            color_idx += 1

class DashboardComponent(QWidget):
    """Komponen dashboard untuk menampilkan statistik dan info terbaru"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI dashboard"""
        main_layout = QVBoxLayout(self)

        # Clean header without background (matching pengaturan style)
        header_frame = QWidget()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 10, 0)

        title_label = QLabel("Dashboard")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        main_layout.addWidget(header_frame)

        # Dashboard content
        dashboard_widget = QWidget()
        dashboard_layout = QGridLayout(dashboard_widget)
        main_layout.addWidget(dashboard_widget)

        # Wrapper untuk scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QGridLayout(scroll_content)
        
        # Statistik Jemaat dengan Chart
        jemaat_stats = self.create_stat_group("Statistik Jemaat")
        jemaat_layout = QVBoxLayout(jemaat_stats)
        
        # Add statistics chart
        self.statistics_chart = StatisticsChart()
        jemaat_layout.addWidget(self.statistics_chart)
        
        # Add summary labels below chart
        summary_layout = QHBoxLayout()
        
        self.jemaat_count_label = QLabel("Total: 0")
        self.jemaat_count_label.setStyleSheet("font-weight: bold; color: #2ecc71;")
        
        self.keluarga_count_label = QLabel("Keluarga: 0")
        self.keluarga_count_label.setStyleSheet("font-weight: bold; color: #3498db;")
        
        self.lingkungan_count_label = QLabel("Lingkungan: 15")
        self.lingkungan_count_label.setStyleSheet("font-weight: bold; color: #f39c12;")
        
        self.wilayah_count_label = QLabel("Wilayah: 5")
        self.wilayah_count_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        
        summary_layout.addWidget(self.jemaat_count_label)
        summary_layout.addWidget(self.keluarga_count_label)
        summary_layout.addWidget(self.lingkungan_count_label)
        summary_layout.addWidget(self.wilayah_count_label)
        
        jemaat_layout.addLayout(summary_layout)
        
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
            self.jemaat_count_label.setText(f"Total: {jemaat_count}")
            
            # Estimasi keluarga (asumsi 1 keluarga = 3-4 orang)
            keluarga_count = max(1, jemaat_count // 4)
            self.keluarga_count_label.setText(f"Keluarga: {keluarga_count}")
            
            # Update statistics chart with actual data
            self.statistics_chart.update_data(jemaat_data if jemaat_data else [])
            
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