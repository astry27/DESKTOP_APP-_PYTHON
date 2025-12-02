# Path: server/components/expandable_menu_button.py

import os
from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon


class ExpandableMenuButton(QWidget):
    """Button menu yang dapat di-expand untuk menampilkan submenu dengan dropdown icon"""

    toggled = pyqtSignal(bool)  # Signal ketika button di-toggle

    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(parent)
        self.is_expanded = False
        self.icon_path = icon_path
        self.icon_active_path = None
        self.original_text = text

        # Generate active icon path
        if icon_path and icon_path.endswith('.png'):
            base_path = icon_path[:-4]  # Remove .png
            active_path = base_path + '_active_icon.png'
            if os.path.exists(active_path):
                self.icon_active_path = active_path

        # Setup layout horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No margins untuk full width
        layout.setSpacing(0)  # No spacing

        # Main button untuk teks dan menu icon
        self.main_button = QPushButton(text)
        self.main_button.setCheckable(True)
        self.main_button.setFixedHeight(45)
        self.main_button.setFlat(True)
        self.main_button.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 10px 15px;
                margin: 4px 8px 4px 8px;
                font-size: 13px;
                font-weight: normal;
                background-color: transparent;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: rgba(38, 139, 210, 0.12);
                color: #ffffff;
            }
            QPushButton:checked {
                background-color: rgba(38, 139, 210, 0.2);
                color: #ffffff;
                font-weight: bold;
                border-radius: 6px;
            }
        """)

        # Set menu icon dari file path
        if icon_path and os.path.exists(icon_path):
            self.main_button.setIcon(QIcon(icon_path))
            self.main_button.setIconSize(QSize(18, 18))

        layout.addWidget(self.main_button)

        # Spacer untuk mendorong dropdown icon ke kanan
        layout.addStretch()

        # Dropdown icon button
        self.dropdown_button = QPushButton()
        self.dropdown_button.setCheckable(False)
        self.dropdown_button.setFixedHeight(45)
        self.dropdown_button.setFixedWidth(45)
        self.dropdown_button.setFlat(True)
        self.dropdown_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 10px 15px;
                margin: 0px;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: transparent;
            }
        """)
        # Connect dropdown button click ke fungsi yang sama
        self.dropdown_button.clicked.connect(self.on_clicked)

        layout.addWidget(self.dropdown_button)

        # Container styling
        self.setFixedHeight(45)
        self.setStyleSheet("""
            QWidget {
                border: none;
                margin: 0px;
                background-color: transparent;
            }
        """)

        # Update initial dropdown icon
        self.update_dropdown_icon()

        # Connect signals
        self.main_button.clicked.connect(self.on_clicked)

    def update_dropdown_icon(self):
        """Update dropdown icon berdasarkan state expanded/collapsed"""
        if self.is_expanded:
            icon_path = "server/assets/arrowup_icon.png"
        else:
            icon_path = "server/assets/arrowdown_icon.png"

        if os.path.exists(icon_path):
            self.dropdown_button.setIcon(QIcon(icon_path))
            self.dropdown_button.setIconSize(QSize(18, 18))

    def on_clicked(self):
        """Handle when button is clicked"""
        self.is_expanded = not self.is_expanded
        self.main_button.setChecked(self.is_expanded)
        self.update_dropdown_icon()
        self.update_icon()  # Update menu icon
        self.update_appearance()
        self.toggled.emit(self.is_expanded)

    def update_icon(self):
        """Update menu icon berdasarkan state expanded/collapsed"""
        if self.is_expanded and self.icon_active_path:
            self.main_button.setIcon(QIcon(self.icon_active_path))
        elif not self.is_expanded and self.icon_path:
            self.main_button.setIcon(QIcon(self.icon_path))

    def update_appearance(self):
        """Update appearance based on expanded state"""
        if self.is_expanded:
            # Active state - soft highlight background with border-left indicator
            self.main_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 6px;
                    border-left: 3px solid #2aa198;
                    text-align: left;
                    padding: 10px 15px;
                    padding-left: 12px;
                    margin: 4px 8px 4px 8px;
                    font-size: 13px;
                    font-weight: bold;
                    background-color: rgba(38, 139, 210, 0.2);
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: rgba(38, 139, 210, 0.25);
                    color: #ffffff;
                }
            """)
            # Dropdown button styling saat expanded
            self.dropdown_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: rgba(38, 139, 210, 0.2);
                    border-radius: 6px;
                    padding: 10px 15px;
                    margin: 4px 8px 4px 0px;
                    cursor: pointer;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: rgba(38, 139, 210, 0.25);
                }
            """)
            # Container background untuk active state
            self.setStyleSheet("""
                QWidget {
                    border: none;
                    margin: 0px;
                    background-color: transparent;
                }
            """)
        else:
            # Normal state - restore original styling
            self.main_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 6px;
                    text-align: left;
                    padding: 10px 15px;
                    margin: 4px 8px 4px 8px;
                    font-size: 13px;
                    font-weight: normal;
                    background-color: transparent;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: rgba(38, 139, 210, 0.12);
                    color: #ffffff;
                }
            """)
            # Dropdown button styling saat normal
            self.dropdown_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                    padding: 10px 15px;
                    margin: 4px 8px 4px 0px;
                    cursor: pointer;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: transparent;
                }
            """)
            # Container background untuk normal state
            self.setStyleSheet("""
                QWidget {
                    border: none;
                    margin: 0px;
                    background-color: transparent;
                }
            """)

    def setChecked(self, checked):
        """Set checked state"""
        self.is_expanded = checked
        self.main_button.setChecked(checked)
        self.update_dropdown_icon()
        self.update_icon()  # Update menu icon
        self.update_appearance()

    def set_expanded(self, expanded):
        """Set expansion state"""
        self.is_expanded = expanded
        self.main_button.setChecked(expanded)
        self.update_dropdown_icon()
        self.update_icon()  # Update menu icon
        self.update_appearance()
