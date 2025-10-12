from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel, 
                             QMessageBox, QDialog, QFormLayout, QComboBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
import requests
from config import ServerConfig

class PenggunaDialog(QDialog):
    def __init__(self, parent=None, pengguna_data=None):
        super().__init__(parent)
        self.pengguna_data = pengguna_data
        self.setWindowTitle("Tambah Pengguna" if not pengguna_data else "Edit Pengguna")
        self.setFixedSize(400, 300)
        self.setup_ui()
        
        if pengguna_data:
            self.load_data()
    
    def setup_ui(self):
        layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.nama_lengkap_input = QLineEdit()
        self.email_input = QLineEdit()
        self.is_active_checkbox = QCheckBox()
        self.is_active_checkbox.setChecked(True)
        
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        layout.addRow("Nama Lengkap:", self.nama_lengkap_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Aktif:", self.is_active_checkbox)
        
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Simpan")
        self.cancel_button = QPushButton("Batal")
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow(button_layout)
        
        self.save_button.clicked.connect(self.save_pengguna)
        self.cancel_button.clicked.connect(self.reject)  # type: ignore
        
        self.setLayout(layout)
    
    def load_data(self):
        if self.pengguna_data:
            self.username_input.setText(self.pengguna_data.get('username', ''))
            self.nama_lengkap_input.setText(self.pengguna_data.get('nama_lengkap', ''))
            self.email_input.setText(self.pengguna_data.get('email', ''))
            self.is_active_checkbox.setChecked(bool(self.pengguna_data.get('is_active', True)))
            self.username_input.setEnabled(False)
    
    def save_pengguna(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        nama_lengkap = self.nama_lengkap_input.text().strip()
        email = self.email_input.text().strip()
        is_active = self.is_active_checkbox.isChecked()
        
        if not all([username, nama_lengkap, email]):
            QMessageBox.warning(self, "Error", "Username, nama lengkap, dan email harus diisi!")
            return
        
        if not self.pengguna_data and not password:
            QMessageBox.warning(self, "Error", "Password harus diisi untuk pengguna baru!")
            return
        
        data = {
            'username': username,
            'nama_lengkap': nama_lengkap,
            'email': email,
            'is_active': is_active
        }
        
        if password:
            data['password'] = password
        
        try:
            if self.pengguna_data:
                url = f"{ServerConfig.API_BASE_URL}/pengguna/{self.pengguna_data['id_pengguna']}"
                response = requests.put(url, json=data, timeout=10)
            else:
                url = f"{ServerConfig.API_BASE_URL}/pengguna"
                response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    QMessageBox.information(self, "Sukses", "Pengguna berhasil disimpan!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", result.get('message', 'Gagal menyimpan pengguna'))
            else:
                QMessageBox.warning(self, "Error", f"Error {response.status_code}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan pengguna: {str(e)}")

class PenggunaComponent(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_pengguna()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        title_label = QLabel("Manajemen Pengguna")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        
        self.add_button = QPushButton("Tambah Pengguna")
        self.add_button.clicked.connect(self.add_pengguna)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_pengguna)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        header_layout.addWidget(self.refresh_button)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Username", "Nama Lengkap", "Email", "Status", "Dibuat", "Aksi"
        ])
        
        layout.addLayout(header_layout)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_pengguna(self):
        try:
            response = requests.get(f"{ServerConfig.API_BASE_URL}/pengguna", timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    pengguna_list = result.get('data', [])
                    self.populate_table(pengguna_list)
                else:
                    QMessageBox.warning(self, "Error", result.get('message', 'Gagal mengambil data pengguna'))
            else:
                QMessageBox.warning(self, "Error", f"Error {response.status_code}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengambil data pengguna: {str(e)}")
    
    def populate_table(self, pengguna_list):
        self.table.setRowCount(len(pengguna_list))
        
        for row, pengguna in enumerate(pengguna_list):
            self.table.setItem(row, 0, QTableWidgetItem(str(pengguna.get('id_pengguna', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(pengguna.get('username', '')))
            self.table.setItem(row, 2, QTableWidgetItem(pengguna.get('nama_lengkap', '')))
            self.table.setItem(row, 3, QTableWidgetItem(pengguna.get('email', '')))
            
            status = "Aktif" if pengguna.get('is_active') else "Nonaktif"
            self.table.setItem(row, 4, QTableWidgetItem(status))
            
            created_at = pengguna.get('created_at', '')
            if 'T' in created_at:
                created_at = created_at.split('T')[0]
            self.table.setItem(row, 5, QTableWidgetItem(created_at))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(5, 0, 5, 0)
            
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda checked, p=pengguna: self.edit_pengguna(p))
            
            delete_button = QPushButton("Hapus")
            delete_button.clicked.connect(lambda checked, p=pengguna: self.delete_pengguna(p))
            
            action_layout.addWidget(edit_button)
            action_layout.addWidget(delete_button)
            action_widget.setLayout(action_layout)
            
            self.table.setCellWidget(row, 6, action_widget)
        
        self.table.resizeColumnsToContents()
    
    def add_pengguna(self):
        dialog = PenggunaDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_pengguna()
    
    def edit_pengguna(self, pengguna_data):
        dialog = PenggunaDialog(self, pengguna_data)
        if dialog.exec_() == QDialog.Accepted:
            self.load_pengguna()
    
    def delete_pengguna(self, pengguna_data):
        reply = QMessageBox.question(
            self, 
            "Konfirmasi Hapus", 
            f"Yakin ingin menghapus pengguna '{pengguna_data['username']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                url = f"{ServerConfig.API_BASE_URL}/pengguna/{pengguna_data['id_pengguna']}"
                response = requests.delete(url, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        QMessageBox.information(self, "Sukses", "Pengguna berhasil dihapus!")
                        self.load_pengguna()
                    else:
                        QMessageBox.warning(self, "Error", result.get('message', 'Gagal menghapus pengguna'))
                else:
                    QMessageBox.warning(self, "Error", f"Error {response.status_code}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus pengguna: {str(e)}")