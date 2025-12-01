# Path: server/components/vertical_submenu.py

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon


class VerticalSubMenuButton(QPushButton):
    """Custom button untuk submenu vertikal dengan support untuk icon"""
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(45)
        self.icon_path = icon_path
        self.icon_active_path = None

        # Set style untuk submenu - indentasi dalam dengan warna background solid
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 4px;
                text-align: left;
                padding: 8px 12px 8px 40px;
                font-size: 12px;
                font-weight: 400;
                background-color: #FFFFFF;
                color: #7F8C8D;
                margin: 3px 8px;
            }
            QPushButton:hover {
                background-color: #ECF0F1;
                color: #2C3E50;
                font-weight: 500;
            }
            QPushButton:checked {
                background-color: #12101E;
                color: #FFFFFF;
                font-weight: 500;
                border-radius: 4px;
            }
        """)

        # Set icon dari file path
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(16, 16))

            # Generate active icon path (icon.png -> icon_active_icon.png)
            if icon_path.endswith('.png'):
                base_path = icon_path[:-4]  # Remove .png
                active_path = base_path + '_active_icon.png'
                if os.path.exists(active_path):
                    self.icon_active_path = active_path

    def update_icon_state(self):
        """Update icon berdasarkan checked state"""
        if self.isChecked() and self.icon_active_path:
            self.setIcon(QIcon(self.icon_active_path))
        elif not self.isChecked() and self.icon_path:
            self.setIcon(QIcon(self.icon_path))


class VerticalSubMenu(QWidget):
    """Widget untuk submenu vertikal yang dapat disembunyikan"""
    menu_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
            }
        """)

        # Layout utama vertikal dengan padding untuk rounded corners submenu
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 4, 0, 4)
        self.layout.setSpacing(0)

        self.buttons = {}
        self.setVisible(False)  # Hidden by default

    def add_button(self, button_id, text, icon_path=None):
        """Tambahkan button ke submenu dengan optional icon"""
        button = VerticalSubMenuButton(text, icon_path)
        button.clicked.connect(lambda checked: self.on_button_clicked(button_id, button))
        self.layout.addWidget(button)
        self.buttons[button_id] = button
        return button

    def on_button_clicked(self, button_id, button):
        """Handle button click"""
        # Uncheck semua button lain
        for bid, btn in self.buttons.items():
            if bid != button_id:
                btn.setChecked(False)
                btn.update_icon_state()
            else:
                btn.update_icon_state()

        # Emit signal
        self.menu_clicked.emit(button_id)

    def set_active_button(self, button_id):
        """Set button aktif"""
        for bid, btn in self.buttons.items():
            btn.setChecked(bid == button_id)
            btn.update_icon_state()

    def reset_buttons(self):
        """Reset semua button"""
        for btn in self.buttons.values():
            btn.setChecked(False)
            btn.update_icon_state()

    def show_submenu(self):
        """Tampilkan submenu"""
        self.setVisible(True)

    def hide_submenu(self):
        """Sembunyikan submenu"""
        self.setVisible(False)
