# Path: server/components/dashboard.py

import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QGroupBox, 
                            QLabel, QListWidget, QTextBrowser, QScrollArea, QHBoxLayout)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont

class StatisticsChart(QWidget):
    """Widget untuk menampilkan chart statistik umat"""

    def __init__(self, parent=None):  # type: ignore
        super().__init__(parent)  # type: ignore
        self.setMinimumSize(700, 420)
        self.setMaximumSize(900, 450)

        # Data statistik default
        self.jemaat_data = {
            'total': 0,
            'keluarga': 0,
            'lingkungan': 15,
            'wilayah': 5,
            'laki_laki': 0,
            'perempuan': 0,
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

        # Data sakramen default
        self.sakramen_data = {
            'baptis': {'sudah': 0, 'belum': 0},
            'ekaristi': {'sudah': 0, 'belum': 0},
            'krisma': {'sudah': 0, 'belum': 0},
            'perkawinan': {'sudah': 0, 'belum': 0}
        }
    
    def update_data(self, jemaat_data):
        """Update data statistik"""
        total_jemaat = len(jemaat_data) if jemaat_data else 0
        self.jemaat_data['total'] = total_jemaat

        # Hitung jumlah keluarga dari No. KK yang unik (same No. KK = 1 family)
        unique_no_kk = set()
        if jemaat_data:
            for jemaat in jemaat_data:
                no_kk = jemaat.get('no_kk', '')
                if no_kk and no_kk.strip():  # Only count if No. KK exists and not empty
                    unique_no_kk.add(no_kk.strip())

        # Jumlah keluarga = jumlah unique No. KK
        self.jemaat_data['keluarga'] = len(unique_no_kk) if unique_no_kk else max(1, total_jemaat // 4)

        # Reset kategori dan gender
        for kategori in self.jemaat_data['kategori']:
            self.jemaat_data['kategori'][kategori] = 0
        self.jemaat_data['laki_laki'] = 0
        self.jemaat_data['perempuan'] = 0

        # Reset sakramen
        for sakramen in self.sakramen_data:
            self.sakramen_data[sakramen]['sudah'] = 0
            self.sakramen_data[sakramen]['belum'] = 0

        # Hitung berdasarkan kategori dan jenis kelamin dari data jemaat
        if jemaat_data:
            for jemaat in jemaat_data:
                # Kategori
                kategori = jemaat.get('kategori', '')
                if kategori in self.jemaat_data['kategori']:
                    self.jemaat_data['kategori'][kategori] += 1

                # Jenis kelamin
                jenis_kelamin = (jemaat.get('jenis_kelamin') or '').lower()
                if jenis_kelamin in ['laki-laki', 'l', 'male']:
                    self.jemaat_data['laki_laki'] += 1
                elif jenis_kelamin in ['perempuan', 'p', 'female']:
                    self.jemaat_data['perempuan'] += 1

                # Sakramen (gunakan nama kolom yang benar setelah migration 21)
                # Baptis - gunakan status_babtis atau tanggal_babtis
                status_baptis = (jemaat.get('status_babtis') or '').lower()
                if status_baptis == 'sudah' or jemaat.get('tanggal_babtis'):
                    self.sakramen_data['baptis']['sudah'] += 1
                else:
                    self.sakramen_data['baptis']['belum'] += 1

                # Ekaristi - gunakan status_ekaristi atau tanggal_komuni
                status_ekaristi = (jemaat.get('status_ekaristi') or '').lower()
                if status_ekaristi == 'sudah' or jemaat.get('tanggal_komuni'):
                    self.sakramen_data['ekaristi']['sudah'] += 1
                else:
                    self.sakramen_data['ekaristi']['belum'] += 1

                # Krisma - gunakan status_krisma atau tanggal_krisma
                status_krisma = (jemaat.get('status_krisma') or '').lower()
                if status_krisma == 'sudah' or jemaat.get('tanggal_krisma'):
                    self.sakramen_data['krisma']['sudah'] += 1
                else:
                    self.sakramen_data['krisma']['belum'] += 1

                # Perkawinan - gunakan status_perkawinan atau tanggal_perkawinan
                status_perkawinan = (jemaat.get('status_perkawinan') or '').lower()
                if status_perkawinan == 'sudah' or jemaat.get('tanggal_perkawinan'):
                    self.sakramen_data['perkawinan']['sudah'] += 1
                else:
                    self.sakramen_data['perkawinan']['belum'] += 1

        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Draw the statistics chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background with gradient
        painter.fillRect(self.rect(), QColor(255, 255, 255))

        # Draw border
        painter.setPen(QPen(QColor(220, 220, 220), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        # Draw title
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.setPen(QColor(52, 73, 94))
        painter.drawText(15, 25, "Statistik Umat")

        # Draw category statistics (improved bar chart) - LEFT SIDE
        self.draw_improved_bar_chart(painter)

        # Draw sacrament summary (RIGHT SIDE)
        self.draw_sacrament_summary(painter)

        # Draw summary statistics (BOTTOM)
        self.draw_summary_stats(painter)
    
    def draw_gender_pie_chart(self, painter):
        """Draw pie chart for gender statistics"""
        center_x, center_y = 120, 100
        radius = 50

        # Data for pie chart
        laki_laki = self.jemaat_data['laki_laki']
        perempuan = self.jemaat_data['perempuan']
        total = max(1, laki_laki + perempuan)

        if total > 0:
            # Colors for gender
            male_color = QColor(52, 152, 219)  # Blue
            female_color = QColor(231, 76, 60)  # Pink/Red

            # Draw pie slices
            start_angle = 0

            # Male slice
            if laki_laki > 0:
                angle = int(360 * laki_laki / total)
                painter.setBrush(QBrush(male_color))
                painter.setPen(QPen(Qt.white, 2))
                painter.drawPie(center_x - radius, center_y - radius,
                              radius * 2, radius * 2, start_angle * 16, angle * 16)
                start_angle += angle

            # Female slice
            if perempuan > 0:
                angle = int(360 * perempuan / total)
                painter.setBrush(QBrush(female_color))
                painter.drawPie(center_x - radius, center_y - radius,
                              radius * 2, radius * 2, start_angle * 16, angle * 16)

        # Gender legend
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        painter.setPen(QColor(44, 62, 80))

        legend_y = 170
        painter.fillRect(15, legend_y, 12, 12, male_color)
        painter.drawText(32, legend_y + 10, f"Laki-laki: {laki_laki}")

        painter.fillRect(15, legend_y + 20, 12, 12, female_color)
        painter.drawText(32, legend_y + 30, f"Perempuan: {perempuan}")

        # Total
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(QColor(52, 73, 94))
        painter.drawText(15, legend_y + 50, f"Total Umat: {self.jemaat_data['total']}")

    def draw_sacrament_summary(self, painter):
        """Draw sacrament summary statistics on the RIGHT side (vertikal style seperti ringkasan statistik)"""
        start_x, start_y = 420, 75
        box_width = 250
        box_height = 205

        # Background seperti ringkasan statistik (light gray background)
        painter.setBrush(QBrush(QColor(248, 249, 250)))
        painter.setPen(QPen(QColor(220, 220, 220), 1))
        painter.drawRoundedRect(start_x, start_y, box_width, box_height, 5, 5)

        # Title
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(QColor(52, 73, 94))
        painter.drawText(start_x + 15, start_y + 20, "Ringkasan Sakramen")

        # Sacrament data (vertikal layout seperti ringkasan statistik)
        sacraments = [
            ('Baptis', 'baptis'),
            ('Ekaristi', 'ekaristi'),
            ('Krisma', 'krisma'),
            ('Perkawinan', 'perkawinan')
        ]

        # Layout dalam dua kolom vertikal
        col1_x = start_x + 20
        col2_x = start_x + 140
        y_offset = start_y + 45

        painter.setFont(QFont("Arial", 9))
        painter.setPen(QColor(44, 62, 80))

        row = 0
        for display_name, key in sacraments:
            sudah = self.sakramen_data[key]['sudah']
            belum = self.sakramen_data[key]['belum']

            # Tentukan posisi kolom
            if row < 2:
                x_pos = col1_x
            else:
                x_pos = col2_x

            # Hitung posisi y
            y_pos = y_offset + ((row % 2) * 75)

            # Sacrament name (bold)
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            painter.setPen(QColor(52, 73, 94))
            painter.drawText(x_pos, y_pos, f"{display_name}")

            # Data (normal font)
            painter.setFont(QFont("Arial", 9))
            painter.setPen(QColor(44, 62, 80))
            painter.drawText(x_pos, y_pos + 18, f"Sudah : {sudah}")
            painter.drawText(x_pos, y_pos + 36, f"Belum : {belum}")

            row += 1

    def draw_improved_bar_chart(self, painter):
        """Draw improved bar chart for category statistics on LEFT SIDE"""
        start_x, start_y = 25, 75
        bar_width = 35
        max_height = 140
        spacing = 8

        # Get category data
        kategori_data = self.jemaat_data['kategori']
        max_value = max(kategori_data.values()) if any(kategori_data.values()) else 1

        # Modern colors for bars (matching the image colors)
        colors = [
            QColor(52, 152, 219),   # Blue - Balita
            QColor(46, 204, 113),   # Green - Anak-anak
            QColor(155, 89, 182),   # Purple - Remaja
            QColor(241, 196, 15),   # Yellow - OMK
            QColor(230, 126, 34),   # Orange - KBK
            QColor(231, 76, 60),    # Red - KIK
            QColor(149, 165, 166)   # Gray - Lansia
        ]

        # Chart title
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(QColor(52, 73, 94))
        painter.drawText(start_x, 60, "Distribusi Kategori")

        x_pos = start_x
        color_idx = 0

        for kategori, count in kategori_data.items():
            if max_value > 0:
                bar_height = max(5, int(max_height * count / max_value))
            else:
                bar_height = 5

            # Draw bar with gradient effect
            color = colors[color_idx % len(colors)]
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 1))
            painter.drawRoundedRect(x_pos, start_y + max_height - bar_height,
                                  bar_width, bar_height, 3, 3)

            # Draw count on top of bar
            if count > 0:
                painter.setPen(QColor(44, 62, 80))
                painter.setFont(QFont("Arial", 8, QFont.Bold))
                text_x = x_pos + bar_width//2 - 5
                painter.drawText(text_x, start_y + max_height - bar_height - 8, str(count))

            # Draw category label
            painter.setPen(QColor(44, 62, 80))
            painter.setFont(QFont("Arial", 7))

            # Split long category names
            label = kategori
            if len(label) > 6:
                label = label[:6] + "."

            text_width = painter.fontMetrics().width(label)
            text_x = x_pos + (bar_width - text_width) // 2
            painter.drawText(text_x, start_y + max_height + 15, label)

            x_pos += bar_width + spacing
            color_idx += 1

    def draw_summary_stats(self, painter):
        """Draw summary statistics boxes at the bottom"""
        # Summary statistics at the bottom
        summary_y = 300

        # Background for summary (light gray background)
        painter.setBrush(QBrush(QColor(248, 249, 250)))
        painter.setPen(QPen(QColor(220, 220, 220), 1))
        painter.drawRoundedRect(15, summary_y, self.width() - 30, 80, 5, 5)

        # Summary title
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(QColor(52, 73, 94))
        painter.drawText(25, summary_y + 20, "Ringkasan Statistik")

        # Stats layout dalam dua baris
        col1_x = 35
        col2_x = 250
        col3_x = 465
        stats_y = summary_y + 45

        painter.setFont(QFont("Arial", 9))
        painter.setPen(QColor(44, 62, 80))

        # Row 1
        # Column 1 - Total Jemaat
        painter.drawText(col1_x, stats_y, "Total Umat")
        painter.drawText(col1_x + 110, stats_y, f": {self.jemaat_data['total']}")

        # Column 2 - Laki-laki
        painter.drawText(col2_x, stats_y, "Laki-laki")
        painter.drawText(col2_x + 70, stats_y, f": {self.jemaat_data['laki_laki']}")

        # Column 3 - Lingkungan
        painter.drawText(col3_x, stats_y, "Lingkungan")
        painter.drawText(col3_x + 70, stats_y, f": {self.jemaat_data['lingkungan']}")

        # Row 2
        # Column 1 - Jumlah Keluarga
        painter.drawText(col1_x, stats_y + 20, "Jumlah Keluarga")
        painter.drawText(col1_x + 110, stats_y + 20, f": {self.jemaat_data['keluarga']}")

        # Column 2 - Perempuan
        painter.drawText(col2_x, stats_y + 20, "Perempuan")
        painter.drawText(col2_x + 70, stats_y + 20, f": {self.jemaat_data['perempuan']}")

        # Column 3 - Wilayah
        painter.drawText(col3_x, stats_y + 20, "Wilayah")
        painter.drawText(col3_x + 70, stats_y + 20, f": {self.jemaat_data['wilayah']}")

class DashboardComponent(QWidget):
    """Komponen dashboard untuk menampilkan statistik dan info terbaru"""

    def __init__(self, parent=None):  # type: ignore
        super().__init__(parent)  # type: ignore
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
        
        # Statistik Jemaat dengan Chart (improved layout)
        jemaat_stats = self.create_improved_stat_group("Statistik Umat")
        jemaat_layout = QVBoxLayout(jemaat_stats)
        jemaat_layout.setContentsMargins(15, 20, 15, 15)

        # Add statistics chart
        self.statistics_chart = StatisticsChart()
        jemaat_layout.addWidget(self.statistics_chart)

        # Add some spacing
        jemaat_layout.addStretch()

        scroll_layout.addWidget(jemaat_stats, 0, 0, 1, 2)  # Span 2 columns
        
        # Jadwal Hari Ini
        jadwal_today = self.create_stat_group("Jadwal Hari Ini")
        jadwal_layout = QVBoxLayout(jadwal_today)

        tanggal = QLabel(f"Tanggal: {QDate.currentDate().toString('dd MMMM yyyy')}")
        tanggal.setStyleSheet("font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        jadwal_layout.addWidget(tanggal)

        self.jadwal_today_list = QListWidget()
        self.jadwal_today_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        jadwal_layout.addWidget(self.jadwal_today_list)

        scroll_layout.addWidget(jadwal_today, 1, 0)
        
        # Aktivitas Terbaru
        aktivitas = self.create_stat_group("Aktivitas Terbaru")
        aktivitas_layout = QVBoxLayout(aktivitas)

        self.aktivitas_list = QListWidget()
        self.aktivitas_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        aktivitas_layout.addWidget(self.aktivitas_list)

        scroll_layout.addWidget(aktivitas, 1, 1)
        
        # Pengumuman Terbaru
        pengumuman = self.create_stat_group("Pengumuman Terbaru")
        pengumuman_layout = QVBoxLayout(pengumuman)

        self.pengumuman_text = QTextBrowser()
        self.pengumuman_text.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        pengumuman_layout.addWidget(self.pengumuman_text)

        scroll_layout.addWidget(pengumuman, 2, 0, 1, 2)  # Span 2 columns
        
        # Set column stretch for better layout
        scroll_layout.setColumnStretch(0, 1)
        scroll_layout.setColumnStretch(1, 1)

        # Set layout untuk widget scrollable
        scroll_area.setWidget(scroll_content)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
        """)
        dashboard_layout.addWidget(scroll_area)
    
    def create_stat_group(self, title):
        """Buat group box dengan style konsisten"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                background-color: #ffffff;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                font-size: 13px;
            }
        """)
        return group

    def create_improved_stat_group(self, title):
        """Buat group box dengan style yang lebih baik untuk statistik"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                background-color: #ffffff;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                font-size: 13px;
            }
        """)
        return group
    
    def update_statistics(self, jemaat_data, kegiatan_data, pengumuman_data, db_manager=None):
        """Update statistik dashboard"""
        try:
            # Update statistik jemaat - labels are now handled in the chart
            
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