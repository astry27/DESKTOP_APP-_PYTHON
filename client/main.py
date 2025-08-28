# Path: client/main.py

import sys
from PyQt5.QtWidgets import QApplication, QDialog

from components.login_dialog import LoginDialog
from main_app import ClientAppWindow

def main():
    """Fungsi utama untuk menjalankan aplikasi client."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application properties
    app.setApplicationName("Gereja Katolik Client")
    app.setOrganizationName("Gereja Katolik")

    login_dialog = LoginDialog()
    
    # Tampilkan dialog login dan tunggu hasilnya
    if login_dialog.exec_() == QDialog.Accepted:
        # Jika login berhasil, ambil api_client dan user data
        api_client = login_dialog.api_client
        user_data = login_dialog.get_user_data()
        
        # Buat dan setup main window
        main_window = ClientAppWindow(api_client)
        main_window.set_user_data(user_data)
        
        # Setup koneksi ke server
        main_window.set_connection_status(True)  # Set as connected after login
        
        main_window.show()
        sys.exit(app.exec_())
    else:
        # Jika login dibatalkan, aplikasi selesai
        sys.exit(0)

if __name__ == "__main__":
    main()