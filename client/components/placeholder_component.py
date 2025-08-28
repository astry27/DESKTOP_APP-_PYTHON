# Path: client/components/placeholder_component.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class PlaceholderComponent(QWidget):
    
    def __init__(self, page_name, page_description, color="#007bff", parent=None):
        super().__init__(parent)
        self.page_name = page_name
        self.page_description = page_description
        self.color = color
        
        self.setup_ui()
    
    def setup_ui(self):
        # Set background
        self.setStyleSheet("background-color: #f8f9fa;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Page header
        header_section = QFrame()
        header_section.setStyleSheet(f"""
            QFrame {{
                background: linear-gradient(135deg, {self.color} 0%, {self.adjust_color(self.color)} 100%);
                padding: 40px 0px;
            }}
        """)
        header_layout = QVBoxLayout(header_section)
        header_layout.setContentsMargins(40, 40, 40, 40)
        
        # Page title
        title_label = QLabel(self.page_name)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        
        subtitle_label = QLabel(self.page_description)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                margin-bottom: 0px;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_section)
        
        # Content section
        content_section = QWidget()
        content_layout = QVBoxLayout(content_section)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Coming soon card
        coming_soon_card = QFrame()
        coming_soon_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e9ecef;
                padding: 50px 30px;
            }
        """)
        coming_soon_layout = QVBoxLayout(coming_soon_card)
        coming_soon_layout.setAlignment(Qt.AlignCenter)
        
        # Icon
        icon_label = QLabel("🚧")
        icon_label.setStyleSheet("font-size: 64px; margin-bottom: 20px;")
        icon_label.setAlignment(Qt.AlignCenter)
        coming_soon_layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel("Halaman Dalam Pengembangan")
        message_label.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 15px;
                text-align: center;
            }}
        """)
        message_label.setAlignment(Qt.AlignCenter)
        coming_soon_layout.addWidget(message_label)
        
        # Description
        desc_label = QLabel(f"Fitur {self.page_name} sedang dalam tahap pengembangan dan akan segera tersedia.")
        desc_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 16px;
                text-align: center;
                line-height: 1.5;
            }
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        coming_soon_layout.addWidget(desc_label)
        
        content_layout.addWidget(coming_soon_card)
        content_layout.addStretch()
        
        layout.addWidget(content_section)
    
    def adjust_color(self, color):
        """Adjust color for gradient effect"""
        color_map = {
            "#007bff": "#0056b3",
            "#28a745": "#1e7e34", 
            "#dc3545": "#a02622",
            "#ffc107": "#d39e00",
            "#6f42c1": "#4e2a84",
            "#fd7e14": "#d65205"
        }
        return color_map.get(color, "#0056b3")