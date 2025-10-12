# Path: client/components/profile_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QFrame, QLineEdit, QFileDialog, QMessageBox, QWidget,
                            QGroupBox, QFormLayout, QTextEdit, QDialogButtonBox,
                            QGraphicsOpacityEffect, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QPixmap, QFont, QPainter, QPainterPath, QIcon
import os

class ProfileDialog(QDialog):
    profile_updated: pyqtSignal = pyqtSignal(dict)  # type: ignore
    logout_requested: pyqtSignal = pyqtSignal()  # type: ignore
    photo_updated: pyqtSignal = pyqtSignal(str)  # Signal when photo is updated  # type: ignore
    dialog_closed: pyqtSignal = pyqtSignal()  # Signal when dialog is closed  # type: ignore

    def __init__(self, user_data, connection_status, api_client, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.connection_status = connection_status
        self.api_client = api_client
        self.profile_image_path = None
        self.cached_pixmap = None  # Cache for profile image
        self.is_closing = False  # Flag to prevent multiple close events

        self.setWindowTitle("Profile User")  # Set proper title
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)  # Normal dialog with close button  # type: ignore
        self.setModal(True)  # Make it modal so it doesn't interfere with main window
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)  # Don't delete on close
        self.setFixedSize(320, 450)

        # Standard font for consistency
        self.standard_font = QFont("Segoe UI", 9)
        self.setFont(self.standard_font)

        # Modern styling with white background, rounded corners, and shadow effect
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: none;
                border-radius: 12px;
            }
        """)

        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        # Main widget with white background and shadow effect
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create main content widget
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
                color: #2c3e50;
                border: none;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QPushButton {
                background: transparent;
                border: none;
                text-align: left;
                padding: 12px 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: #2c3e50;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
            QPushButton:pressed {
                background-color: #e9ecef;
            }
        """)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 25, 20, 25)
        content_layout.setSpacing(0)

        # Profile header section with contrasting background
        profile_header = QWidget()
        profile_header.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 12px 12px 0 0;
                border-bottom: 1px solid #e9ecef;
            }
        """)

        profile_header_layout = QVBoxLayout(profile_header)
        profile_header_layout.setContentsMargins(20, 25, 20, 20)
        profile_header_layout.setSpacing(12)
        profile_header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Circular profile photo (80x80) - clickable
        self.profile_image = QLabel()
        self.profile_image.setFixedSize(80, 80)
        self.profile_image.setStyleSheet("""
            QLabel {
                border: 3px solid #dee2e6;
                border-radius: 40px;
                background-color: white;
                color: #495057;
                font-size: 28px;
                font-weight: bold;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
        """)
        self.profile_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_image.setText(self.get_initial_letter())
        self.profile_image.setCursor(Qt.CursorShape.PointingHandCursor)
        self.profile_image.mousePressEvent = lambda ev: self.select_profile_image()  # type: ignore

        # User name (bold) and email (smaller, gray)
        self.name_label = QLabel(self.user_data.get('nama_lengkap', 'Unknown User'))
        self.name_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 18px;
            font-weight: bold;
            color: #212529;
            background: transparent;
            margin: 0;
        """)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email_label = QLabel(self.user_data.get('email', 'user@example.com'))
        self.email_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            color: #6c757d;
            background: transparent;
            margin: 0;
        """)
        self.email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Status label for connection status
        self.status_label = QLabel("● Online")
        self.status_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            color: #60B861;
            font-weight: 500;
            background: transparent;
            margin: 0;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        profile_header_layout.addWidget(self.profile_image)
        profile_header_layout.addWidget(self.name_label)
        profile_header_layout.addWidget(self.email_label)
        profile_header_layout.addWidget(self.status_label)

        # Content body section
        content_body = QWidget()
        content_body.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 0 0 12px 12px;
            }
        """)

        content_body_layout = QVBoxLayout(content_body)
        content_body_layout.setContentsMargins(20, 20, 20, 20)
        content_body_layout.setSpacing(0)

        # Username and Role info with consistent spacing and alignment
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(8)  # Consistent spacing between username and role
        info_layout.setContentsMargins(0, 0, 0, 15)

        # Create labels with consistent formatting for aligned colons
        self.username_label = QLabel(f"Username  : {self.user_data.get('username', 'admin')}")
        self.username_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            color: #495057;
            padding: 4px 0;
        """)

        self.role_label = QLabel(f"Role      : {self.user_data.get('peran', 'Administrator')}")
        self.role_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            color: #495057;
            padding: 4px 0;
        """)

        info_layout.addWidget(self.username_label)
        info_layout.addWidget(self.role_label)

        content_body_layout.addWidget(info_container)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Plain)
        separator.setStyleSheet("""
            QFrame {
                color: #dee2e6;
                background-color: #dee2e6;
                border: none;
                height: 1px;
            }
        """)

        # Action buttons with icons
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(0)

        # Edit Profile
        edit_profile_btn = self.create_action_button("profile.png", "Edit Profile")
        edit_profile_btn.clicked.connect(self.edit_profile)

        # Change Password
        change_password_btn = self.create_action_button("password.png", "Ganti Password")
        change_password_btn.clicked.connect(self.change_password)

        # Logout
        logout_btn = self.create_action_button("logout.png", "Logout")
        logout_btn.clicked.connect(self.handle_logout)

        actions_layout.addWidget(edit_profile_btn)
        actions_layout.addWidget(change_password_btn)
        actions_layout.addWidget(logout_btn)

        # Add all sections to content layout
        content_body_layout.addWidget(separator)
        content_body_layout.addLayout(actions_layout)

        # Add header and body to main content layout
        content_layout.addWidget(profile_header)
        content_layout.addWidget(content_body)

        # Add content widget to main layout
        main_layout.addWidget(content_widget)

    def setup_animations(self):
        """Setup smooth animations and shadow effects for the dialog"""
        # Add drop shadow effect for modern look
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(30)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(10)
        shadow_effect.setColor(Qt.GlobalColor.black)
        self.setGraphicsEffect(shadow_effect)

        # Fade in animation for the dialog
        self.opacity_effect = QGraphicsOpacityEffect()

        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(250)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutQuart)


    def create_icon_label(self, emoji):
        """Create icon label with emoji"""
        label = QLabel(emoji)
        label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding-right: 8px;
            }
        """)
        return label

    def create_action_button(self, icon_filename, text):
        """Create action button with icon from assets folder"""
        button = QPushButton()
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Create horizontal layout for icon and text
        layout = QHBoxLayout(button)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(15)

        # Try to load icon from assets folder
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', icon_filename)
        if os.path.exists(icon_path):
            try:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon_label.setPixmap(scaled_pixmap)
                else:
                    icon_label.setText("●")  # Fallback bullet point
            except Exception:
                icon_label.setText("●")  # Fallback bullet point
        else:
            icon_label.setText("●")  # Fallback bullet point

        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Text label
        text_label = QLabel(text)
        text_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            color: #2c3e50;
            background: transparent;
        """)

        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()

        button.setLayout(layout)
        return button

    # Remove unused methods - we only need create_action_button

    def get_initial_letter(self):
        """Get first letter of name for profile placeholder"""
        nama = self.user_data.get('nama_lengkap', 'U')
        if nama:
            return nama[0].upper()
        return 'U'

    def update_connection_status(self):
        """Update connection status"""
        if hasattr(self, 'status_label'):
            if self.connection_status:
                self.status_label.setText("● Online")
                self.status_label.setStyleSheet("""
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                    color: #60B861;
                    font-weight: 500;
                    background: transparent;
                    margin: 0;
                """)
            else:
                self.status_label.setText("● Offline")
                self.status_label.setStyleSheet("""
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                    color: #A94442;
                    font-weight: 500;
                    background: transparent;
                    margin: 0;
                """)

    def select_profile_image(self):
        """Select new profile image"""
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(
            self,
            "Pilih Foto Profil",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)"
        )

        if image_path:
            self.profile_image_path = image_path
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Create circular cropped image with caching
                scaled_pixmap = pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                circular_pixmap = self.create_circular_pixmap(scaled_pixmap)
                self.cached_pixmap = circular_pixmap  # Cache the processed image
                self.profile_image.setPixmap(circular_pixmap)
                self.profile_image.setText("")

                # Emit signal to update main window
                self.photo_updated.emit(image_path)  # type: ignore

                QMessageBox.information(self, "Sukses", "Foto profil berhasil diubah!")
            else:
                QMessageBox.warning(self, "Error", "Format gambar tidak didukung")

    def create_circular_pixmap(self, pixmap):
        """Create circular pixmap from rectangular pixmap"""
        size = min(pixmap.width(), pixmap.height())
        target_pixmap = QPixmap(size, size)
        target_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(target_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return target_pixmap

    def edit_profile(self):
        """Show edit profile dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QHBoxLayout, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Profile")
        dialog.setModal(True)
        dialog.setFixedSize(450, 350)

        layout = QVBoxLayout(dialog)

        # Photo section
        photo_layout = QHBoxLayout()
        photo_layout.setSpacing(15)

        # Photo preview
        photo_preview = QLabel()
        photo_preview.setFixedSize(80, 80)
        photo_preview.setStyleSheet("""
            QLabel {
                border: 2px solid #dee2e6;
                border-radius: 40px;
                background-color: white;
                color: #495057;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        photo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set current photo or initial
        if hasattr(self, 'cached_pixmap') and self.cached_pixmap:
            photo_preview.setPixmap(self.cached_pixmap)
        else:
            photo_preview.setText(self.get_initial_letter())

        # Photo buttons
        photo_buttons = QVBoxLayout()
        select_photo_btn = QPushButton("Pilih Foto")
        select_photo_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        remove_photo_btn = QPushButton("Hapus Foto")
        remove_photo_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        photo_buttons.addWidget(select_photo_btn)
        photo_buttons.addWidget(remove_photo_btn)
        photo_buttons.addStretch()

        photo_layout.addWidget(photo_preview)
        photo_layout.addLayout(photo_buttons)
        photo_layout.addStretch()

        layout.addLayout(photo_layout)

        # Form section
        form_layout = QFormLayout()

        # Create input fields
        nama_input = QLineEdit(self.user_data.get('nama_lengkap', ''))
        username_input = QLineEdit(self.user_data.get('username', ''))
        email_input = QLineEdit(self.user_data.get('email', ''))

        # Style the input fields
        input_style = """
            QLineEdit {
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """
        nama_input.setStyleSheet(input_style)
        username_input.setStyleSheet(input_style)
        email_input.setStyleSheet(input_style)

        form_layout.addRow("Nama Lengkap:", nama_input)
        form_layout.addRow("Username:", username_input)
        form_layout.addRow("Email:", email_input)

        layout.addLayout(form_layout)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  # type: ignore
        button_box.accepted.connect(dialog.accept)  # type: ignore
        button_box.rejected.connect(dialog.reject)  # type: ignore
        layout.addWidget(button_box)

        # Photo selection functionality
        def select_photo():
            file_dialog = QFileDialog()
            image_path, _ = file_dialog.getOpenFileName(
                dialog,
                "Pilih Foto Profil",
                "",
                "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)"
            )

            if image_path:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    circular_pixmap = self.create_circular_pixmap(scaled_pixmap)
                    photo_preview.setPixmap(circular_pixmap)
                    photo_preview.setText("")
                    # Store path for later use
                    dialog.selected_photo_path = image_path
                else:
                    QMessageBox.warning(dialog, "Error", "Format gambar tidak didukung")

        def remove_photo():
            photo_preview.setPixmap(QPixmap())
            photo_preview.setText(self.get_initial_letter())
            dialog.selected_photo_path = None

        select_photo_btn.clicked.connect(select_photo)
        remove_photo_btn.clicked.connect(remove_photo)

        # Initialize photo path
        dialog.selected_photo_path = getattr(self, 'profile_image_path', None)

        if dialog.exec_() == QDialog.Accepted:
            # Validate input
            if not all([nama_input.text(), username_input.text(), email_input.text()]):
                QMessageBox.warning(self, "Error", "Semua field harus diisi!")
                return

            if '@' not in email_input.text() or '.' not in email_input.text():
                QMessageBox.warning(self, "Error", "Format email tidak valid!")
                return

            # Update user data
            self.user_data['nama_lengkap'] = nama_input.text()
            self.user_data['username'] = username_input.text()
            self.user_data['email'] = email_input.text()

            # Update photo if changed
            if hasattr(dialog, 'selected_photo_path'):
                if dialog.selected_photo_path != self.profile_image_path:
                    if dialog.selected_photo_path:
                        self.profile_image_path = dialog.selected_photo_path
                        pixmap = QPixmap(dialog.selected_photo_path)
                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                            circular_pixmap = self.create_circular_pixmap(scaled_pixmap)
                            self.cached_pixmap = circular_pixmap
                            self.profile_image.setPixmap(circular_pixmap)
                            self.profile_image.setText("")
                            # Emit signal to update main window
                            self.photo_updated.emit(dialog.selected_photo_path)  # type: ignore
                    else:
                        # Photo removed
                        self.profile_image_path = None
                        self.cached_pixmap = None
                        self.profile_image.setPixmap(QPixmap())
                        self.profile_image.setText(self.get_initial_letter())
                        self.photo_updated.emit("")  # type: ignore

            # Emit update signal
            self.profile_updated.emit(self.user_data)  # type: ignore

            # Update UI labels
            self.update_user_data(self.user_data)

            QMessageBox.information(self, "Sukses", "Profile berhasil diperbarui!")

    def change_password(self):
        """Show change password dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Ganti Password")
        dialog.setModal(True)
        dialog.setFixedSize(350, 200)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        current_password = QLineEdit()
        current_password.setEchoMode(QLineEdit.Password)
        current_password.setPlaceholderText("Password saat ini")

        new_password = QLineEdit()
        new_password.setEchoMode(QLineEdit.Password)
        new_password.setPlaceholderText("Password baru")

        confirm_password = QLineEdit()
        confirm_password.setEchoMode(QLineEdit.Password)
        confirm_password.setPlaceholderText("Konfirmasi password")

        # Style the input fields
        input_style = """
            QLineEdit {
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """
        current_password.setStyleSheet(input_style)
        new_password.setStyleSheet(input_style)
        confirm_password.setStyleSheet(input_style)

        form_layout.addRow("Password Lama:", current_password)
        form_layout.addRow("Password Baru:", new_password)
        form_layout.addRow("Konfirmasi:", confirm_password)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  # type: ignore
        button_box.accepted.connect(dialog.accept)  # type: ignore
        button_box.rejected.connect(dialog.reject)  # type: ignore
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            current = current_password.text()
            new = new_password.text()
            confirm = confirm_password.text()

            if not all([current, new, confirm]):
                QMessageBox.warning(self, "Error", "Semua field harus diisi!")
                return

            if new != confirm:
                QMessageBox.warning(self, "Error", "Password baru dan konfirmasi tidak cocok!")
                return

            if len(new) < 6:
                QMessageBox.warning(self, "Error", "Password minimal 6 karakter!")
                return

            QMessageBox.information(self, "Sukses", "Password berhasil diubah!")

    def handle_logout(self):
        """Handle logout button click"""
        reply = QMessageBox.question(
            self,
            "Konfirmasi Logout",
            "Apakah Anda yakin ingin logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.logout_requested.emit()  # type: ignore
            self.close()

    def update_user_data(self, user_data):
        """Update user data if changed"""
        self.user_data = user_data
        # Update the labels instead of rebuilding entire UI
        if hasattr(self, 'name_label'):
            self.name_label.setText(self.user_data.get('nama_lengkap', 'Unknown User'))
            self.username_label.setText(f"Username  : {self.user_data.get('username', 'admin')}")
            self.role_label.setText(f"Role      : {self.user_data.get('peran', 'Administrator')}")
            self.email_label.setText(self.user_data.get('email', 'user@example.com'))
            self.profile_image.setText(self.get_initial_letter())

    def update_connection_status_external(self, is_connected):
        """Update connection status from external"""
        self.connection_status = is_connected
        self.update_connection_status()

    def closeEvent(self, event):
        """Handle close event safely"""
        if not self.is_closing:
            self.is_closing = True
            self.dialog_closed.emit()  # type: ignore
            # Hide instead of closing to keep dialog instance alive
            event.ignore()
            self.hide()
            # Reset closing flag after hiding
            QTimer.singleShot(500, lambda: setattr(self, 'is_closing', False))  # type: ignore
        else:
            event.ignore()

    def focusOutEvent(self, event):
        """Handle focus out event - don't auto close"""
        super().focusOutEvent(event)
        # Removed auto-close behavior to prevent accidental closing

    def safe_close(self):
        """Safely close the dialog"""
        if not self.is_closing:
            self.is_closing = True
            self.hide()  # Use hide() instead of close() to keep dialog instance alive
            self.dialog_closed.emit()  # type: ignore
            # Reset closing flag after a short delay
            QTimer.singleShot(500, lambda: setattr(self, 'is_closing', False))  # type: ignore

    def showEvent(self, event):
        """Reset closing flag when dialog is shown"""
        super().showEvent(event)
        self.is_closing = False
        # Always update user data display when shown
        if self.user_data:
            if hasattr(self, 'name_label'):
                self.name_label.setText(self.user_data.get('nama_lengkap', 'Unknown User'))
                self.username_label.setText(f"Username  : {self.user_data.get('username', 'admin')}")
                self.role_label.setText(f"Role      : {self.user_data.get('peran', 'Administrator')}")
                self.email_label.setText(self.user_data.get('email', 'user@example.com'))
                self.profile_image.setText(self.get_initial_letter())
        # Update connection status when dialog is shown
        self.update_connection_status()
        # Center the dialog on parent
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)
        if hasattr(self, 'fade_animation'):
            self.fade_animation.start()