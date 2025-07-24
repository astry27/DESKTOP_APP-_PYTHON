# Path: server/components/keuangan.py

import datetime
import csv
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QGroupBox, QTabWidget, QMessageBox, 
                            QFileDialog, QAbstractItemView)
from PyQt5.QtCore import pyqtSignal, QDate

# Import dialog keuangan yang baru
from .dialogs import KeuanganDialog

class KeuanganComponent(QWidget):
    """Komponen untuk manajemen keuangan"""
    
    data_updated = pyqtSignal()
    log_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pemasukan_data = []
        self.pengeluaran_data = []
        self.db_manager = None
        self.setup_ui()
    
    def set_database_manager(self, db_manager):
        """Set database manager."""
        self.db_manager = db_manager
    
    def setup_ui(self):
        """Setup UI untuk halaman keuangan."""
        layout = QVBoxLayout(self)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Statistik Keuangan
        stats_group = self.create_statistics()
        layout.addWidget(stats_group)
        
        # Tab untuk pemasukan dan pengeluaran
        self.tab_widget = self.create_tabs()
        layout.addWidget(self.tab_widget)
        
        # Tombol aksi
        action_layout = self.create_action_buttons()
        layout.addLayout(action_layout)

    def create_header(self):
        """Buat header dengan title dan kontrol."""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Manajemen Keuangan")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_income_button = self.create_button("Tambah Pemasukan", "#27ae60", self.add_income)
        header_layout.addWidget(add_income_button)
        
        add_expense_button = self.create_button("Tambah Pengeluaran", "#c0392b", self.add_expense)
        header_layout.addWidget(add_expense_button)
        
        return header

    def create_statistics(self):
        """Buat panel statistik keuangan."""
        stats_group = QGroupBox("Ringkasan Keuangan")
        stats_layout = QHBoxLayout(stats_group)
        
        self.saldo_value = QLabel("Rp 0")
        self.pemasukan_bulan_ini_value = QLabel("Rp 0")
        self.pengeluaran_bulan_ini_value = QLabel("Rp 0")
        
        stats_layout.addWidget(self.create_stat_widget("TOTAL SALDO", self.saldo_value, "#ecf0f1", "#2c3e50"))
        stats_layout.addWidget(self.create_stat_widget("PEMASUKAN BULAN INI", self.pemasukan_bulan_ini_value, "#e8f8f5", "#27ae60"))
        stats_layout.addWidget(self.create_stat_widget("PENGELUARAN BULAN INI", self.pengeluaran_bulan_ini_value, "#fdedec", "#c0392b"))
        
        return stats_group

    def create_stat_widget(self, label_text, value_label, bg_color, text_color):
        """Buat widget statistik dengan style."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {bg_color}; border-radius: 5px; padding: 10px;")
        layout = QVBoxLayout(widget)
        
        label = QLabel(label_text)
        label.setStyleSheet(f"font-weight: bold; color: {text_color};")
        value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {text_color};")
        
        layout.addWidget(label)
        layout.addWidget(value_label)
        
        return widget

    def create_tabs(self):
        """Buat tab untuk pemasukan dan pengeluaran."""
        tab_widget = QTabWidget()
        
        self.income_table = self.create_table()
        self.expense_table = self.create_table()
        
        tab_widget.addTab(self.income_table, "Pemasukan")
        tab_widget.addTab(self.expense_table, "Pengeluaran")
        
        return tab_widget

    def create_table(self):
        """Buat tabel keuangan."""
        table = QTableWidget(0, 5)  # Hapus kolom ID
        table.setHorizontalHeaderLabels(["Tanggal", "Sub-Kategori", "Deskripsi", "Jumlah (Rp)", "Penanggung Jawab"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setAlternatingRowColors(True)
        
        # Enable context menu untuk edit/hapus
        table.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        table.customContextMenuRequested.connect(self.show_context_menu)
        
        return table

    def show_context_menu(self, position):
        """Tampilkan context menu untuk edit/hapus"""
        sender = self.sender()
        if sender.rowCount() == 0:
            return
            
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Hapus")
        
        action = menu.exec_(sender.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_transaction(sender)
        elif action == delete_action:
            self.delete_transaction(sender)

    def edit_transaction(self, table):
        """Edit transaksi yang dipilih"""
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih transaksi yang akan diedit")
            return
        
        # Tentukan apakah pemasukan atau pengeluaran
        if table == self.income_table:
            data_source = self.pemasukan_data
            kategori = "Pemasukan"
        else:
            data_source = self.pengeluaran_data
            kategori = "Pengeluaran"
        
        if current_row >= len(data_source):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return
        
        transaction_data = data_source[current_row]
        
        # Buka dialog edit dengan data existing
        dialog = KeuanganDialog(self, kategori=kategori)
        
        # Load data ke dialog
        dialog.tanggal_input.setDate(QDate.fromString(str(transaction_data.get('tanggal', '')), "yyyy-MM-dd"))
        dialog.deskripsi_input.setText(str(transaction_data.get('deskripsi', '')))
        dialog.sub_kategori_input.setText(str(transaction_data.get('sub_kategori', '')))
        dialog.jumlah_input.setValue(float(transaction_data.get('jumlah', 0)))
        dialog.penanggung_jawab_input.setText(str(transaction_data.get('penanggung_jawab', '')))
        
        if dialog.exec_() == dialog.Accepted:
            updated_data = dialog.get_data()
            
            if not updated_data['deskripsi'] or updated_data['jumlah'] <= 0:
                QMessageBox.warning(self, "Input Tidak Valid", "Deskripsi dan Jumlah harus diisi dengan benar.")
                return
            
            # Update melalui API
            transaction_id = transaction_data.get('id_keuangan')
            if transaction_id and self.db_manager:
                success, result = self.db_manager.update_keuangan(transaction_id, updated_data)
                if success:
                    QMessageBox.information(self, "Sukses", "Transaksi berhasil diupdate.")
                    self.load_data()
                    self.log_message.emit(f"Transaksi {kategori} berhasil diupdate")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal mengupdate transaksi: {result}")
                    self.log_message.emit(f"Error update transaksi: {result}")

    def delete_transaction(self, table):
        """Hapus transaksi yang dipilih"""
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih transaksi yang akan dihapus")
            return
        
        # Tentukan apakah pemasukan atau pengeluaran
        if table == self.income_table:
            data_source = self.pemasukan_data
            kategori = "Pemasukan"
        else:
            data_source = self.pengeluaran_data
            kategori = "Pengeluaran"
        
        if current_row >= len(data_source):
            QMessageBox.warning(self, "Error", "Data tidak valid")
            return
        
        transaction_data = data_source[current_row]
        deskripsi = transaction_data.get('deskripsi', 'Unknown')
        
        reply = QMessageBox.question(self, 'Konfirmasi',
                                    f"Yakin ingin menghapus transaksi '{deskripsi}'?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            transaction_id = transaction_data.get('id_keuangan')
            if transaction_id and self.db_manager:
                success, result = self.db_manager.delete_keuangan(transaction_id)
                if success:
                    QMessageBox.information(self, "Sukses", "Transaksi berhasil dihapus.")
                    self.load_data()
                    self.log_message.emit(f"Transaksi {kategori} berhasil dihapus")
                else:
                    QMessageBox.critical(self, "Error", f"Gagal menghapus transaksi: {result}")
                    self.log_message.emit(f"Error hapus transaksi: {result}")

    def create_action_buttons(self):
        """Buat tombol-tombol aksi."""
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        report_button = self.create_button("Laporan Keuangan", "#3498db", self.generate_report)
        action_layout.addWidget(report_button)
        
        export_button = self.create_button("Export Data", "#16a085", self.export_data)
        action_layout.addWidget(export_button)

        refresh_button = self.create_button("Refresh", "#8e44ad", self.load_data)
        action_layout.addWidget(refresh_button)
        
        return action_layout

    def create_button(self, text, color, slot):
        """Buat button dengan style konsisten."""
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: white; padding: 8px 15px; border: none; border-radius: 4px; font-weight: bold;")
        button.clicked.connect(slot)
        return button

    def load_data(self):
        """Load data keuangan dari database."""
        if not self.db_manager:
            self.log_message.emit("Database tidak tersedia")
            return

        try:
            # Load pemasukan
            success, pemasukan = self.db_manager.get_keuangan_list(category="Pemasukan")
            if success:
                self.pemasukan_data = pemasukan
                self.populate_table(self.income_table, self.pemasukan_data)
                self.log_message.emit(f"Data pemasukan berhasil dimuat: {len(pemasukan)} record")
            else:
                self.log_message.emit(f"Gagal memuat data pemasukan: {pemasukan}")

            # Load pengeluaran
            success, pengeluaran = self.db_manager.get_keuangan_list(category="Pengeluaran")
            if success:
                self.pengeluaran_data = pengeluaran
                self.populate_table(self.expense_table, self.pengeluaran_data)
                self.log_message.emit(f"Data pengeluaran berhasil dimuat: {len(pengeluaran)} record")
            else:
                self.log_message.emit(f"Gagal memuat data pengeluaran: {pengeluaran}")
            
            self.update_statistics()
            self.log_message.emit("Data keuangan berhasil dimuat")
            self.data_updated.emit()
        except Exception as e:
            self.log_message.emit(f"Exception saat memuat data keuangan: {str(e)}")

    def populate_table(self, table, data):
        """Populate tabel dengan data."""
        table.setRowCount(0)
        for row_data in data:
            row_pos = table.rowCount()
            table.insertRow(row_pos)
            
            # Tanggal
            tanggal = row_data.get('tanggal')
            tanggal_str = tanggal.strftime('%d/%m/%Y') if hasattr(tanggal, 'strftime') else str(tanggal)
            table.setItem(row_pos, 0, QTableWidgetItem(tanggal_str))

            # Sub kategori
            table.setItem(row_pos, 1, QTableWidgetItem(str(row_data.get('sub_kategori', ''))))
            
            # Deskripsi
            table.setItem(row_pos, 2, QTableWidgetItem(str(row_data.get('deskripsi', ''))))
            
            # Jumlah - Format sebagai currency Indonesia
            jumlah = row_data.get('jumlah', 0)
            try:
                jumlah_float = float(jumlah)
                jumlah_str = f"Rp {jumlah_float:,.0f}".replace(',', '.')
            except (ValueError, TypeError):
                jumlah_str = f"Rp 0"
            table.setItem(row_pos, 3, QTableWidgetItem(jumlah_str))
            
            # Penanggung jawab
            table.setItem(row_pos, 4, QTableWidgetItem(str(row_data.get('penanggung_jawab', ''))))

    def update_statistics(self):
        """Update panel statistik."""
        if not self.db_manager: 
            return

        # Update saldo total
        success, saldo = self.db_manager.get_saldo_total()
        if success and saldo:
            try:
                saldo_amount = float(saldo.get('saldo', 0))
                self.saldo_value.setText(f"Rp {saldo_amount:,.0f}".replace(',', '.'))
            except (ValueError, TypeError):
                self.saldo_value.setText("Rp 0")
        else:
            self.saldo_value.setText("Rp 0")

        # Update pemasukan & pengeluaran bulan ini
        today = datetime.date.today()
        success, bulanan = self.db_manager.get_saldo_keuangan_bulanan(today.year, today.month)
        if success and bulanan:
            data = bulanan[0]
            try:
                pemasukan = float(data.get('total_pemasukan', 0) or 0)
                pengeluaran = float(data.get('total_pengeluaran', 0) or 0)
                self.pemasukan_bulan_ini_value.setText(f"Rp {pemasukan:,.0f}".replace(',', '.'))
                self.pengeluaran_bulan_ini_value.setText(f"Rp {pengeluaran:,.0f}".replace(',', '.'))
            except (ValueError, TypeError):
                self.pemasukan_bulan_ini_value.setText("Rp 0")
                self.pengeluaran_bulan_ini_value.setText("Rp 0")
        else:
            self.pemasukan_bulan_ini_value.setText("Rp 0")
            self.pengeluaran_bulan_ini_value.setText("Rp 0")

    def add_income(self):
        """Tambah pemasukan baru."""
        self.add_transaction("Pemasukan")

    def add_expense(self):
        """Tambah pengeluaran baru."""
        self.add_transaction("Pengeluaran")

    def add_transaction(self, kategori):
        """Buka dialog untuk menambah transaksi baru."""
        dialog = KeuanganDialog(self, kategori=kategori)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            if not data['deskripsi'] or data['jumlah'] <= 0:
                QMessageBox.warning(self, "Input Tidak Valid", "Deskripsi dan Jumlah harus diisi dengan benar.")
                return
            
            if not self.db_manager:
                QMessageBox.warning(self, "Error", "Database tidak tersedia")
                return
            
            success, result = self.db_manager.add_keuangan(data)
            if success:
                QMessageBox.information(self, "Sukses", f"{kategori} berhasil ditambahkan.")
                self.load_data()
                self.log_message.emit(f"{kategori} berhasil ditambahkan")
            else:
                QMessageBox.critical(self, "Error", f"Gagal menambahkan {kategori}: {result}")
                self.log_message.emit(f"Gagal menambahkan {kategori}: {result}")

    def generate_report(self):
        """Generate laporan keuangan sederhana."""
        if not self.db_manager:
            QMessageBox.warning(self, "Error", "Database tidak tersedia.")
            return

        success, saldo_data = self.db_manager.get_saldo_total()
        if not success or not saldo_data:
            QMessageBox.warning(self, "Error", "Tidak dapat mengambil data saldo.")
            return

        try:
            total_pemasukan = float(saldo_data.get('total_pemasukan', 0) or 0)
            total_pengeluaran = float(saldo_data.get('total_pengeluaran', 0) or 0)
            saldo_akhir = float(saldo_data.get('saldo', 0) or 0)

            report_text = (
                f"Laporan Keuangan Keseluruhan\n\n"
                f"Total Pemasukan: Rp {total_pemasukan:,.0f}\n".replace(',', '.') +
                f"Total Pengeluaran: Rp {total_pengeluaran:,.0f}\n".replace(',', '.') +
                f"--------------------------------------------------\n" +
                f"Saldo Akhir: Rp {saldo_akhir:,.0f}".replace(',', '.')
            )
            QMessageBox.information(self, "Laporan Keuangan", report_text)
            self.log_message.emit("Laporan keuangan dibuat.")
        except (ValueError, TypeError) as e:
            QMessageBox.warning(self, "Error", f"Error memformat laporan: {e}")

    def export_data(self):
        """Export data keuangan ke file CSV."""
        if not self.pemasukan_data and not self.pengeluaran_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diekspor.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Data Keuangan", "laporan_keuangan.csv", "CSV Files (*.csv)")
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["Tanggal", "Kategori", "Sub-Kategori", "Deskripsi", "Jumlah", "Penanggung Jawab"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                # Tulis data pemasukan
                for item in self.pemasukan_data:
                    writer.writerow({
                        "Tanggal": item.get('tanggal'),
                        "Kategori": item.get('kategori'),
                        "Sub-Kategori": item.get('sub_kategori'),
                        "Deskripsi": item.get('deskripsi'),
                        "Jumlah": item.get('jumlah'),
                        "Penanggung Jawab": item.get('penanggung_jawab')
                    })
                
                # Tulis data pengeluaran
                for item in self.pengeluaran_data:
                    writer.writerow({
                        "Tanggal": item.get('tanggal'),
                        "Kategori": item.get('kategori'),
                        "Sub-Kategori": item.get('sub_kategori'),
                        "Deskripsi": item.get('deskripsi'),
                        "Jumlah": item.get('jumlah'),
                        "Penanggung Jawab": item.get('penanggung_jawab')
                    })

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {filename}")
            self.log_message.emit(f"Data keuangan diekspor ke: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")
            self.log_message.emit(f"Gagal mengekspor data: {str(e)}")
    
    def get_data(self):
        """Ambil data keuangan untuk komponen lain."""
        return {
            'pemasukan': self.pemasukan_data,
            'pengeluaran': self.pengeluaran_data
        }