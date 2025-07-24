# Path: client/main.py

import sys
from PyQt5.QtWidgets import QApplication, QDialog

from client.components.login_dialog import LoginDialog
from main_app import ClientAppWindow

def main():
    """Fungsi utama untuk menjalankan aplikasi client."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    login_dialog = LoginDialog()
    
    # Tampilkan dialog login dan tunggu hasilnya
    if login_dialog.exec_() == QDialog.Accepted:
        # Jika login berhasil, ambil api_client dan tampilkan jendela utama
        api_client = login_dialog.api_client
        main_window = ClientAppWindow(api_client)
        main_window.show()
        sys.exit(app.exec_())
    else:
        # Jika login dibatalkan, aplikasi selesai
        sys.exit(0)

if __name__ == "__main__":
    main()