# Path: client/components/profile_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QFrame, QLineEdit, QFileDialog, QMessageBox, QWidget,
                            QGroupBox, QFormLayout, QTextEdit, QDialogButtonBox,
                            QGraphicsOpacityEffect, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QPixmap, QFont, QPainter, QPainterPath
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

        self.setWindowTitle("Profile User")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)  # type: ignore
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setFixedSize(380, 580)  # Diperbesar agar semua konten terlihat

        # Standard font for consistency
        self.standard_font = QFont("Segoe UI", 9)
        self.setFont(self.standard_font)

        # Modern styling - light theme tanpa sudut hitam
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 12px;
            }
        """)

        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        # Main widget dengan light theme modern
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create main content widget dengan background putih bersih
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
                color: #212529;
                border: none;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                text-align: left;
                padding: 12px 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                color: #212529;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Profile header section dengan light gradient background
        profile_header = QWidget()
        profile_header.setStyleSheet("""
            QWidget {
                background-color: #e9ecef;
                border-radius: 12px 12px 0 0;
                border: none;
            }
        """)

        profile_header_layout = QVBoxLayout(profile_header)
        profile_header_layout.setContentsMargins(24, 28, 24, 24)
        profile_header_layout.setSpacing(8)
        profile_header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Circular profile photo - clickable
        self.profile_image = QLabel()
        self.profile_image.setFixedSize(90, 90)
        self.profile_image.setStyleSheet("""
            QLabel {
                border: 3px solid #ffffff;
                border-radius: 45px;
                background-color: #0d6efd;
                color: #ffffff;
                font-size: 36px;
                font-weight: 700;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        self.profile_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_image.setText(self.get_initial_letter())
        self.profile_image.setCursor(Qt.CursorShape.PointingHandCursor)
        self.profile_image.mousePressEvent = lambda ev: self.select_profile_image()  # type: ignore

        # User name (bold) dan email
        self.name_label = QLabel(self.user_data.get('nama_lengkap', 'Unknown User'))
        self.name_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 17px;
            font-weight: 600;
            color: #212529;
            background: transparent;
            padding: 2px 0;
        """)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email_label = QLabel(self.user_data.get('email', 'user@example.com'))
        self.email_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            color: #6c757d;
            background: transparent;
            padding: 2px 0;
        """)
        self.email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Status label untuk connection status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11px;
            font-weight: 600;
            color: #198754;
            background-color: #d1e7dd;
            border-radius: 12px;
            padding: 4px 12px;
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
                background-color: #ffffff;
                border-radius: 0 0 12px 12px;
            }
        """)

        content_body_layout = QVBoxLayout(content_body)
        content_body_layout.setContentsMargins(24, 20, 24, 24)
        content_body_layout.setSpacing(16)

        # Username and Role info dengan spacing yang baik
        info_container = QWidget()
        info_layout = QFormLayout(info_container)
        info_layout.setSpacing(10)
        info_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        info_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)  # type: ignore
        info_layout.setContentsMargins(0, 0, 0, 16)

        username_title = QLabel("Username")
        username_title.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            color: #6c757d;
            font-weight: 500;
        """)
        self.username_label = QLabel(self.user_data.get('username', 'admin'))
        self.username_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            color: #212529;
            font-weight: 600;
        """)

        role_title = QLabel("Role")
        role_title.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            color: #6c757d;
            font-weight: 500;
        """)
        self.role_label = QLabel(self.user_data.get('peran', 'user'))
        self.role_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            color: #212529;
            font-weight: 600;
        """)

        info_layout.addRow(username_title, self.username_label)
        info_layout.addRow(role_title, self.role_label)

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

        # Action buttons dengan icons - diperbaiki agar tidak terpotong
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(10)

        # Edit Profile
        edit_profile_btn = self.create_action_button("profile.png", "Edit Profile")
        edit_profile_btn.clicked.connect(self.edit_profile)

        # Change Password
        change_password_btn = self.create_action_button("password.png", "Ganti Password")
        change_password_btn.clicked.connect(self.change_password)

        # Logout - dengan styling merah
        logout_btn = self.create_action_button("logout.png", "Logout")
        logout_btn.clicked.connect(self.handle_logout)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8d7da;
                border: 1px solid #f5c2c7;
                border-radius: 8px;
                padding: 12px 16px;
            }
            QPushButton:hover {
                background-color: #f1aeb5;
                border-color: #ea868f;
            }
            QPushButton:pressed {
                background-color: #ea868f;
            }
        """)
        logout_labels = logout_btn.findChildren(QLabel)
        if logout_labels:
            logout_labels[0].setStyleSheet("""
                QLabel {
                    background-color: #dc3545;
                    border-radius: 10px;
                    color: #ffffff;
                    font-weight: 600;
                }
            """)
            if len(logout_labels) > 1:
                logout_labels[1].setStyleSheet("""
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 13px;
                    color: #842029;
                    background: transparent;
                    font-weight: 600;
                """)
            if len(logout_labels) > 2:
                logout_labels[-1].setStyleSheet("""
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 14px;
                    color: #842029;
                    background: transparent;
                """)

        actions_layout.addWidget(edit_profile_btn)
        actions_layout.addWidget(change_password_btn)
        actions_layout.addWidget(logout_btn)

        # Add spacing agar button terakhir tidak terpotong
        actions_layout.addSpacing(8)

        # Add all sections to content layout
        content_body_layout.addWidget(separator)
        content_body_layout.addLayout(actions_layout)

        # Add header and body to main content layout
        content_layout.addWidget(profile_header)
        content_layout.addWidget(content_body)

        # Add content widget to main layout
        main_layout.addWidget(content_widget)

    def setup_animations(self):
        """Setup smooth animations and subtle shadow effects"""
        # Add subtle drop shadow untuk depth - tidak terlalu gelap
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(20)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(4)
        shadow_effect.setColor(Qt.GlobalColor.gray)  # Abu-abu lebih terang
        self.setGraphicsEffect(shadow_effect)

        # Fade in animation untuk dialog
        self.opacity_effect = QGraphicsOpacityEffect()

        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutQuart)


    def create_action_button(self, icon_filename, text):
        """Create action button with icon from assets folder - modern light theme"""
        button = QPushButton()
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(44)  # Tinggi minimum agar tidak terpotong

        layout = QHBoxLayout(button)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        # Icon label dengan background circular
        icon_label = QLabel()
        icon_label.setFixedSize(26, 26)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: #0d6efd;
                border-radius: 13px;
                color: #ffffff;
                font-weight: 600;
                font-size: 12px;
            }
        """)

        # Coba load icon dari assets
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', icon_filename)
        if os.path.exists(icon_path):
            try:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    icon_label.setPixmap(
                        pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    )
                    icon_label.setStyleSheet("""
                        QLabel {
                            background-color: #0d6efd;
                            border-radius: 13px;
                        }
                    """)
                else:
                    icon_label.setText("●")
            except Exception:
                icon_label.setText("●")
        else:
            icon_label.setText("●")

        # Text label
        text_label = QLabel(text)
        text_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            color: #212529;
            background: transparent;
            font-weight: 600;
        """)

        # Arrow label
        arrow_label = QLabel("›")
        arrow_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 18px;
            color: #adb5bd;
            background: transparent;
        """)

        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        layout.addWidget(arrow_label)

        return button

    # Remove unused methods - we only need create_action_button

    def get_initial_letter(self):
        """Get first letter of name for profile placeholder"""
        nama = self.user_data.get('nama_lengkap', 'U')
        if nama:
            return nama[0].upper()
        return 'U'

    def update_connection_status(self):
        """Update connection status dengan light theme"""
        if hasattr(self, 'status_label'):
            if self.connection_status:
                self.status_label.setText("Online")
                self.status_label.setStyleSheet("""
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 11px;
                    font-weight: 600;
                    color: #198754;
                    background-color: #d1e7dd;
                    border-radius: 12px;
                    padding: 4px 12px;
                """)
            else:
                self.status_label.setText("Offline")
                self.status_label.setStyleSheet("""
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 11px;
                    font-weight: 600;
                    color: #dc3545;
                    background-color: #f8d7da;
                    border-radius: 12px;
                    padding: 4px 12px;
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
                scaled_pixmap = pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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
                        # Upload to server first
                        if self.api_client:
                            upload_result = self.api_client.upload_profile_photo(dialog.selected_photo_path)
                            if not upload_result.get('success'):
                                QMessageBox.warning(self, "Warning", f"Gagal upload foto ke server: {upload_result.get('data')}")
                                # Continue anyway to update local UI

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

            # Call API to change password
            if self.api_client:
                result = self.api_client.change_password(self.user_data.get('id_pengguna'), current, new)
                if result['success']:
                    QMessageBox.information(self, "Sukses", "Password berhasil diubah!")
                else:
                    QMessageBox.warning(self, "Error", f"Gagal mengubah password: {result.get('data', 'Unknown error')}")
            else:
                QMessageBox.warning(self, "Error", "Tidak terhubung ke API")

    def handle_logout(self):
        """Handle logout button click - akan redirect ke login page"""
        reply = QMessageBox.question(
            self,
            "Konfirmasi Logout",
            "Apakah Anda yakin ingin logout?\n\nAnda akan diarahkan ke halaman login.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.logout_requested.emit()  # type: ignore
            self.safe_close()

    def update_user_data(self, user_data):
        """Update user data if changed"""
        self.user_data = user_data
        # Update the labels instead of rebuilding entire UI
        if hasattr(self, 'name_label'):
            self.name_label.setText(self.user_data.get('nama_lengkap', 'Unknown User'))
            self.username_label.setText(self.user_data.get('username', 'admin'))
            self.role_label.setText(self.user_data.get('peran', 'Administrator'))
            self.email_label.setText(self.user_data.get('email', 'user@example.com'))
            
            # Only reset to initial if no profile image is set
            if not self.profile_image_path:
                self.reset_profile_image()

    def load_profile_image(self, image_path):
        """Load profile image from path"""
        if image_path and os.path.exists(image_path):
            self.profile_image_path = image_path
            # Load via QImage to bypass QPixmap cache
            from PyQt5.QtGui import QImage
            image = QImage(image_path)
            pixmap = QPixmap()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
            
            if not pixmap.isNull():
                # Create circular cropped image with caching
                scaled_pixmap = pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                circular_pixmap = self.create_circular_pixmap(scaled_pixmap)
                self.cached_pixmap = circular_pixmap
                
                # COMPLETELY REMOVE stylesheet to avoid conflict
                # The border is now drawn inside the pixmap itself
                self.profile_image.setStyleSheet("border: none; background: transparent;")
                self.profile_image.clear()
                self.profile_image.setPixmap(circular_pixmap)
                self.profile_image.repaint()
            else:
                self.reset_profile_image()
        else:
            self.profile_image_path = None
            self.reset_profile_image()

    def reset_profile_image(self):
        """Reset profile image to initial letter with blue background"""
        self.profile_image_path = None  # Clear stored path
        self.profile_image.setPixmap(QPixmap())
        self.profile_image.setText(self.get_initial_letter())
        self.profile_image.setStyleSheet("""
            QLabel {
                border: 3px solid #ffffff;
                border-radius: 45px;
                background-color: #0d6efd;
                color: #ffffff;
                font-size: 36px;
                font-weight: 700;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

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
                self.username_label.setText(self.user_data.get('username', 'admin'))
                self.role_label.setText(self.user_data.get('peran', 'Administrator'))
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
