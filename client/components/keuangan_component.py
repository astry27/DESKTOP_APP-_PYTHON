# Path: client/components/keuangan_component.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLabel, QPushButton, QFrame,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox,
                             QTabWidget, QTextEdit, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import datetime

class KeuanganClientComponent(QWidget):
    
    log_message = pyqtSignal(str)
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.keuangan_data = []
        self.filtered_data = []
        
        self.setup_ui()
        self.load_keuangan_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header info
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #27ae60;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("Manajemen Keuangan Gereja - Mode Client")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        
        desc_label = QLabel("Menampilkan informasi keuangan gereja yang telah dibroadcast oleh admin untuk transparansi")
        desc_label.setStyleSheet("color: #ecf0f1; font-size: 12px; margin-top: 5px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header_frame)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #27ae60;
                color: white;
            }
        """)
        
        # Transactions tab
        self.transactions_tab = self.create_transactions_tab()
        self.tab_widget.addTab(self.transactions_tab, "💰 Transaksi Keuangan")
        
        # Summary tab
        self.summary_tab = self.create_summary_tab()
        self.tab_widget.addTab(self.summary_tab, "📊 Ringkasan Keuangan")
        
        # Reports tab
        self.reports_tab = self.create_reports_tab()
        self.tab_widget.addTab(self.reports_tab, "📋 Laporan")
        
        layout.addWidget(self.tab_widget)
    
    def create_transactions_tab(self):
        """Create transactions tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Search
        search_label = QLabel("Cari:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari keterangan transaksi...")
        self.search_input.textChanged.connect(self.filter_data)
        
        # Type filter
        type_label = QLabel("Jenis:")
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Semua", "Pemasukan", "Pengeluaran"])
        self.type_filter.currentTextChanged.connect(self.filter_data)
        
        # Category filter
        category_label = QLabel("Kategori:")
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "Semua", "Kolekte", "Persembahan", "Donasi", "Operasional", 
            "Pemeliharaan", "Program", "Lainnya"
        ])
        self.category_filter.currentTextChanged.connect(self.filter_data)
        
        # Refresh button
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.clicked.connect(self.load_keuangan_data)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        
        toolbar_layout.addWidget(search_label)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(type_label)
        toolbar_layout.addWidget(self.type_filter)
        toolbar_layout.addWidget(category_label)
        toolbar_layout.addWidget(self.category_filter)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(refresh_button)
        
        layout.addLayout(toolbar_layout)
        
        # Table
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels([
            "Tanggal", "Jenis", "Kategori", "Keterangan", "Jumlah (Rp)", "Saldo"
        ])
        
        # Set column widths
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Tanggal
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Jenis
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Kategori
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Keterangan
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Jumlah
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Saldo
        
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(self.table_widget.SelectRows)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #27ae60;
                color: white;
            }
        """)
        
        layout.addWidget(self.table_widget)
        
        # Statistics
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.total_pemasukan = QLabel("Total Pemasukan: Rp 0")
        self.total_pengeluaran = QLabel("Total Pengeluaran: Rp 0")
        self.saldo_akhir = QLabel("Saldo: Rp 0")
        
        stats_layout.addWidget(self.total_pemasukan)
        stats_layout.addWidget(self.total_pengeluaran)
        stats_layout.addWidget(self.saldo_akhir)
        stats_layout.addStretch()
        
        layout.addWidget(stats_frame)
        
        return tab
    
    def create_summary_tab(self):
        """Create financial summary tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Summary cards
        cards_layout = QHBoxLayout()
        
        # Total Balance Card
        balance_card = self.create_summary_card("💰", "Saldo Total", "Rp 0", "#27ae60")
        self.balance_value = balance_card[1]
        cards_layout.addWidget(balance_card[0])
        
        # Monthly Income Card
        income_card = self.create_summary_card("📈", "Pemasukan Bulan Ini", "Rp 0", "#3498db")
        self.income_value = income_card[1]
        cards_layout.addWidget(income_card[0])
        
        # Monthly Expense Card
        expense_card = self.create_summary_card("📉", "Pengeluaran Bulan Ini", "Rp 0", "#e74c3c")
        self.expense_value = expense_card[1]
        cards_layout.addWidget(expense_card[0])
        
        layout.addLayout(cards_layout)
        
        # Charts placeholder
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 20px;
                margin-top: 20px;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        
        chart_title = QLabel("Grafik Keuangan")
        chart_title.setFont(QFont("Arial", 14, QFont.Bold))
        chart_title.setAlignment(Qt.AlignCenter)
        chart_layout.addWidget(chart_title)
        
        chart_placeholder = QLabel("Grafik keuangan akan ditampilkan di sini\\n(Dalam pengembangan)")
        chart_placeholder.setAlignment(Qt.AlignCenter)
        chart_placeholder.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-style: italic;
                font-size: 16px;
                padding: 100px;
            }
        """)
        chart_layout.addWidget(chart_placeholder)
        
        layout.addWidget(chart_frame)
        
        return tab
    
    def create_reports_tab(self):
        """Create reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Report controls
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 10px;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)
        
        controls_label = QLabel("Laporan Keuangan:")
        controls_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        report_type = QComboBox()
        report_type.addItems([
            "Laporan Bulanan", "Laporan Tahunan", 
            "Laporan Kategori", "Laporan Transparansi"
        ])
        
        generate_button = QPushButton("Generate Laporan")
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        
        controls_layout.addWidget(controls_label)
        controls_layout.addWidget(report_type)
        controls_layout.addWidget(generate_button)
        controls_layout.addStretch()
        
        layout.addWidget(controls_frame)
        
        # Report content
        self.report_content = QTextEdit()
        self.report_content.setReadOnly(True)
        self.report_content.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        
        # Default report content
        default_report = self.generate_default_report()
        self.report_content.setHtml(default_report)
        
        layout.addWidget(self.report_content)
        
        return tab
    
    def create_summary_card(self, icon, title, value, color):
        """Create summary card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 5px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 18px;
                font-weight: bold;
                margin-top: 5px;
            }}
        """)
        layout.addWidget(value_label)
        
        return card, value_label
    
    def load_keuangan_data(self):
        """Load keuangan data from API (broadcast data only)"""
        try:
            result = self.api_client.get_broadcast_keuangan()  # This would be a new API endpoint
            
            if result["success"]:
                data = result.get("data", [])
                if isinstance(data, list):
                    self.keuangan_data = data
                elif isinstance(data, dict) and "data" in data:
                    self.keuangan_data = data["data"]
                else:
                    self.keuangan_data = []
                
                self.filtered_data = self.keuangan_data.copy()
                self.update_table()
                self.update_statistics()
                self.update_summary()
                self.log_message.emit(f"Data keuangan berhasil dimuat: {len(self.keuangan_data)} record")
                
            else:
                error_msg = result.get("data", "Unknown error")
                QMessageBox.warning(self, "Error", f"Gagal memuat data keuangan:\\n{error_msg}")
                self.log_message.emit(f"Gagal memuat data keuangan: {error_msg}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saat memuat data keuangan:\\n{str(e)}")
            self.log_message.emit(f"Error memuat data keuangan: {str(e)}")
    
    def update_table(self):
        """Update table with filtered data"""
        self.table_widget.setRowCount(len(self.filtered_data))
        running_balance = 0
        
        for row, transaksi in enumerate(self.filtered_data):
            # Tanggal
            tanggal = transaksi.get('tanggal', '') or transaksi.get('created_at', '') or 'N/A'
            if tanggal and tanggal != 'N/A':
                try:
                    if 'T' in tanggal:
                        dt = datetime.datetime.fromisoformat(tanggal.replace('Z', '+00:00'))
                        tanggal = dt.strftime('%d/%m/%Y')
                except:
                    pass
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(tanggal)))
            
            # Jenis
            jenis = transaksi.get('jenis', '') or transaksi.get('tipe', '') or 'N/A'
            jenis_item = QTableWidgetItem(str(jenis))
            if jenis.lower() == 'pemasukan':
                jenis_item.setBackground(QColor("#d5f4e6"))
                jenis_item.setForeground(QColor("#27ae60"))
            elif jenis.lower() == 'pengeluaran':
                jenis_item.setBackground(QColor("#fadbd8"))
                jenis_item.setForeground(QColor("#e74c3c"))
            self.table_widget.setItem(row, 1, jenis_item)
            
            # Kategori
            kategori = transaksi.get('kategori', '') or 'Lainnya'
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(kategori)))
            
            # Keterangan
            keterangan = transaksi.get('keterangan', '') or transaksi.get('deskripsi', '') or 'N/A'
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(keterangan)))
            
            # Jumlah
            jumlah = transaksi.get('jumlah', 0) or transaksi.get('nominal', 0) or 0
            try:
                jumlah = float(jumlah)
                if jenis.lower() == 'pemasukan':
                    running_balance += jumlah
                    jumlah_text = f"+{jumlah:,.0f}"
                else:
                    running_balance -= jumlah
                    jumlah_text = f"-{jumlah:,.0f}"
            except:
                jumlah_text = "0"
                
            jumlah_item = QTableWidgetItem(jumlah_text)
            if jenis.lower() == 'pemasukan':
                jumlah_item.setForeground(QColor("#27ae60"))
            else:
                jumlah_item.setForeground(QColor("#e74c3c"))
            self.table_widget.setItem(row, 4, jumlah_item)
            
            # Saldo
            saldo_item = QTableWidgetItem(f"{running_balance:,.0f}")
            if running_balance >= 0:
                saldo_item.setForeground(QColor("#27ae60"))
            else:
                saldo_item.setForeground(QColor("#e74c3c"))
            self.table_widget.setItem(row, 5, saldo_item)
    
    def filter_data(self):
        """Filter data based on search, type, and category"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        category_filter = self.category_filter.currentText()
        
        self.filtered_data = []
        
        for transaksi in self.keuangan_data:
            # Search filter
            keterangan = (transaksi.get('keterangan', '') or transaksi.get('deskripsi', '')).lower()
            
            if search_text and search_text not in keterangan:
                continue
            
            # Type filter
            jenis = transaksi.get('jenis', '') or transaksi.get('tipe', '')
            if type_filter != "Semua" and jenis.lower() != type_filter.lower():
                continue
            
            # Category filter
            kategori = transaksi.get('kategori', '') or 'Lainnya'
            if category_filter != "Semua" and kategori != category_filter:
                continue
            
            self.filtered_data.append(transaksi)
        
        self.update_table()
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics labels"""
        total_pemasukan = 0
        total_pengeluaran = 0
        
        for transaksi in self.filtered_data:
            jumlah = transaksi.get('jumlah', 0) or transaksi.get('nominal', 0) or 0
            try:
                jumlah = float(jumlah)
                jenis = transaksi.get('jenis', '') or transaksi.get('tipe', '')
                
                if jenis.lower() == 'pemasukan':
                    total_pemasukan += jumlah
                else:
                    total_pengeluaran += jumlah
            except:
                pass
        
        saldo = total_pemasukan - total_pengeluaran
        
        self.total_pemasukan.setText(f"Total Pemasukan: Rp {total_pemasukan:,.0f}")
        self.total_pengeluaran.setText(f"Total Pengeluaran: Rp {total_pengeluaran:,.0f}")
        self.saldo_akhir.setText(f"Saldo: Rp {saldo:,.0f}")
        
        # Style the labels
        self.total_pemasukan.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 14px;")
        self.total_pengeluaran.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")
        
        if saldo >= 0:
            self.saldo_akhir.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 16px;")
        else:
            self.saldo_akhir.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 16px;")
    
    def update_summary(self):
        """Update summary cards"""
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        
        monthly_income = 0
        monthly_expense = 0
        total_balance = 0
        
        for transaksi in self.keuangan_data:
            jumlah = transaksi.get('jumlah', 0) or transaksi.get('nominal', 0) or 0
            try:
                jumlah = float(jumlah)
                jenis = transaksi.get('jenis', '') or transaksi.get('tipe', '')
                
                # Check if transaction is from current month
                tanggal_str = transaksi.get('tanggal', '') or transaksi.get('created_at', '')
                if tanggal_str:
                    try:
                        if 'T' in tanggal_str:
                            dt = datetime.datetime.fromisoformat(tanggal_str.replace('Z', '+00:00'))
                        else:
                            dt = datetime.datetime.strptime(tanggal_str, '%Y-%m-%d')
                        
                        if jenis.lower() == 'pemasukan':
                            total_balance += jumlah
                            if dt.month == current_month and dt.year == current_year:
                                monthly_income += jumlah
                        else:
                            total_balance -= jumlah
                            if dt.month == current_month and dt.year == current_year:
                                monthly_expense += jumlah
                    except:
                        pass
            except:
                pass
        
        self.balance_value.setText(f"Rp {total_balance:,.0f}")
        self.income_value.setText(f"Rp {monthly_income:,.0f}")
        self.expense_value.setText(f"Rp {monthly_expense:,.0f}")
    
    def generate_default_report(self):
        """Generate default financial report"""
        current_date = datetime.datetime.now().strftime("%d/%m/%Y")
        
        return f"""
        <h2 style="color: #27ae60; text-align: center;">LAPORAN KEUANGAN GEREJA</h2>
        <p style="text-align: center; color: #7f8c8d;">Tanggal: {current_date}</p>
        <hr>
        
        <h3 style="color: #2c3e50;">RINGKASAN KEUANGAN</h3>
        <p>📊 <strong>Total Transaksi:</strong> {len(self.keuangan_data)} record</p>
        <p>💰 <strong>Saldo Saat Ini:</strong> Rp 0 (akan dihitung)</p>
        <p>📈 <strong>Pemasukan Bulan Ini:</strong> Rp 0</p>
        <p>📉 <strong>Pengeluaran Bulan Ini:</strong> Rp 0</p>
        
        <h3 style="color: #2c3e50;">KATEGORI UTAMA</h3>
        <p>• Kolekte Mingguan</p>
        <p>• Persembahan Khusus</p>
        <p>• Donasi Anggota</p>
        <p>• Biaya Operasional</p>
        <p>• Pemeliharaan Gereja</p>
        
        <hr>
        <p style="color: #7f8c8d; font-size: 10px; text-align: center;">
        Laporan ini menampilkan data keuangan yang telah dibroadcast untuk transparansi.<br>
        Data lengkap hanya tersedia bagi admin gereja.
        </p>
        """