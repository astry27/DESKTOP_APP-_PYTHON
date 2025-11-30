# Path: server/components/struktur_base.py
# Shared base classes and utilities for struktur components

import csv
import os
import threading
import requests
from hashlib import md5
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QGroupBox, QMessageBox, QDialog,
                            QFileDialog, QAbstractItemView, QFrame, QLineEdit,
                            QStyle, QStyleOptionHeader, QMenu)
from PyQt5.QtCore import pyqtSignal, QDate, Qt, QTimer, QSize, QRect, QThread
from PyQt5.QtGui import QPixmap, QIcon, QFont, QPainter, QColor


class WordWrapHeaderView(QHeaderView):
    """Custom header view with word wrap and center alignment support"""
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        # Set minimum height to ensure header is always visible
        self.setMinimumHeight(35)
        # Ensure header is visible on resize
        self.setSectionResizeMode(QHeaderView.Interactive)

    def sectionSizeFromContents(self, logicalIndex):
        """Calculate section size based on wrapped text"""
        if self.model():
            # Get header text
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                # Get current section width
                width = self.sectionSize(logicalIndex)
                if width <= 0:
                    width = self.defaultSectionSize()

                # Create font metrics with bold font
                font = self.font()
                font.setBold(True)
                font.setPointSize(max(font.pointSize(), 9))  # Ensure minimum font size
                from PyQt5.QtGui import QFontMetrics
                fm = QFontMetrics(font)

                # Calculate text rect with word wrap
                rect = fm.boundingRect(0, 0, width - 10, 2000,
                                      Qt.AlignCenter | Qt.TextWordWrap, str(text))

                # Return size with adequate padding (minimum 35px height)
                return QSize(width, max(rect.height() + 16, 35))

        return super().sectionSizeFromContents(logicalIndex)

    def paintSection(self, painter, rect, logicalIndex):
        """Paint section with word wrap and center alignment - always visible"""
        painter.save()

        # Ensure rect has minimum height
        if rect.height() < 35:
            rect.setHeight(35)

        # Draw background with consistent, visible color
        bg_color = QColor(242, 242, 242)  # #f2f2f2 - light gray background
        painter.fillRect(rect, bg_color)

        # Draw borders for Excel-like appearance
        border_color = QColor(180, 180, 180)  # Darker border for better visibility
        painter.setPen(border_color)
        # Right border
        painter.drawLine(rect.topRight(), rect.bottomRight())
        # Bottom border
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        # Get header text
        if self.model():
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                # Setup font with proper size
                font = self.font()
                font.setBold(True)
                font.setPointSize(max(font.pointSize(), 9))  # Ensure readable size
                painter.setFont(font)

                # Text color - darker for better contrast and visibility
                text_color = QColor(30, 30, 30)  # Very dark gray, almost black
                painter.setPen(text_color)

                # Draw text with word wrap and center alignment
                # Add padding to ensure text doesn't touch borders
                text_rect = rect.adjusted(6, 6, -6, -6)

                # Draw text with proper alignment and wrapping
                painter.drawText(text_rect,
                               Qt.AlignCenter | Qt.AlignVCenter | Qt.TextWordWrap,
                               str(text))

        painter.restore()


class ImageCache:
    """Thread-safe cache for downloaded images to avoid redundant network requests"""
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.lock = threading.Lock()

    def get(self, url):
        """Get cached image data, returns None if not cached"""
        with self.lock:
            return self.cache.get(url)

    def set(self, url, pixmap):
        """Set cached image data"""
        with self.lock:
            # Simple LRU-like behavior: clear cache if too large
            if len(self.cache) >= self.max_size:
                # Remove oldest entry (first one)
                first_key = next(iter(self.cache))
                del self.cache[first_key]
            self.cache[url] = pixmap

    def clear(self):
        """Clear all cache"""
        with self.lock:
            self.cache.clear()


class ImageLoaderWorker(QThread):
    """Worker thread for loading images asynchronously"""
    image_loaded = pyqtSignal(str, object)  # url, pixmap
    error_occurred = pyqtSignal(str, str)   # url, error_message

    def __init__(self, cache=None):
        super().__init__()
        self.queue = []
        self.lock = threading.Lock()
        self.cache = cache or ImageCache()
        self.running = True

    def add_image(self, url):
        """Add image URL to loading queue"""
        with self.lock:
            if url not in self.queue:
                self.queue.append(url)

    def run(self):
        """Thread run loop - load images from queue"""
        while self.running:
            url = None
            with self.lock:
                if self.queue:
                    url = self.queue.pop(0)

            if url:
                try:
                    # Check cache first
                    cached = self.cache.get(url)
                    if cached:
                        self.image_loaded.emit(url, cached)
                        continue

                    # Download image with timeout
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        pixmap = QPixmap()
                        if pixmap.loadFromData(response.content):
                            # Scale and cache
                            scaled = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            self.cache.set(url, scaled)
                            self.image_loaded.emit(url, scaled)
                        else:
                            self.error_occurred.emit(url, "Failed to load image from data")
                    else:
                        self.error_occurred.emit(url, f"HTTP {response.status_code}")
                except requests.Timeout:
                    self.error_occurred.emit(url, "Request timeout")
                except Exception as e:
                    self.error_occurred.emit(url, str(e))
            else:
                # No images to load, sleep briefly
                threading.Event().wait(0.1)

    def stop(self):
        """Stop the worker thread"""
        self.running = False
        self.wait()


class BaseStrukturComponent(QWidget):
    """Base class for struktur components with shared functionality"""

    log_message: pyqtSignal = pyqtSignal(str)  # type: ignore

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None

        # Initialize image cache and loader for async image loading
        self.image_cache = ImageCache(max_size=150)
        self.image_loader = ImageLoaderWorker(self.image_cache)
        self.image_loader.image_loaded.connect(self.on_image_loaded)
        self.image_loader.error_occurred.connect(self.on_image_error)
        self.image_loader.start()

        # Store image URLs for table cells for later updates
        self.pending_images = {}  # Maps (table_name, row, col) to url

    def set_database_manager(self, db_manager):
        """Set database manager"""
        self.db_manager = db_manager

    def emit_message(self, message, message_type="info"):
        """Emit log message dengan type (info, success, warning, error)"""
        formatted_message = f"[{message_type.upper()}] {message}"
        self.log_message.emit(formatted_message)

    def on_image_loaded(self, url, pixmap):
        """Callback when image is loaded from cache or network"""
        # Update any pending table cells with this image
        keys_to_remove = []
        for key, img_url in self.pending_images.items():
            if img_url == url:
                table_name, row, col = key
                # Determine correct attribute name based on table_name
                attr_name = self.get_table_attr_name(table_name)
                table = getattr(self, attr_name, None)
                if table and row < table.rowCount():
                    item = QTableWidgetItem()
                    item.setData(Qt.DecorationRole, pixmap)
                    item.setText("")
                    item.setToolTip(f"Image: {url}")
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(row, col, item)
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.pending_images[key]

    def on_image_error(self, url, error_message):
        """Callback when image fails to load"""
        pass

    def get_table_attr_name(self, table_name):
        """Get the attribute name for a table based on table name"""
        if table_name in ('wr', 'binaan'):
            return f'{table_name}_table_view'
        elif table_name == 'kategorial':
            return 'kategorial_table'
        else:
            return f'{table_name}_table'

    def load_image_async(self, table_name, row, col, foto_path):
        """Queue image for async loading, return placeholder item"""
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignCenter)

        if not foto_path:
            item.setText("👤")
            item.setToolTip("No photo")
            return item

        try:
            # Check if it's a server URL
            if foto_path.startswith(('http://', 'https://')):
                # Check cache first for immediate display
                cached = self.image_cache.get(foto_path)
                if cached:
                    item.setData(Qt.DecorationRole, cached)
                    item.setText("")
                    item.setToolTip(f"Image: {foto_path}")
                else:
                    # Queue for async loading
                    item.setText("⏳")  # Loading indicator
                    item.setToolTip("Loading image...")
                    key = (table_name, row, col)
                    self.pending_images[key] = foto_path
                    self.image_loader.add_image(foto_path)
            elif foto_path.startswith(('/uploads/', 'uploads/')):
                # Local server path
                local_path = foto_path[1:] if foto_path.startswith('/') else foto_path
                if os.path.exists(local_path):
                    pixmap = QPixmap(local_path)
                    if not pixmap.isNull():
                        scaled = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        item.setData(Qt.DecorationRole, scaled)
                        item.setText("")
                        item.setToolTip(f"Local image: {local_path}")
                    else:
                        item.setText("🖼️")
                        item.setToolTip(f"Unable to load: {local_path}")
                else:
                    item.setText("🖼️")
                    item.setToolTip(f"Not found: {local_path}")
            elif os.path.exists(foto_path):
                # Local file
                pixmap = QPixmap(foto_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    item.setData(Qt.DecorationRole, scaled)
                    item.setText("")
                    item.setToolTip(f"Local: {foto_path}")
                else:
                    item.setText("📷")
                    item.setToolTip("Unable to load image")
            else:
                item.setText("📷")
                item.setToolTip("File not found")
        except Exception as e:
            item.setText("❌")
            item.setToolTip(f"Error: {str(e)}")

        return item

    def create_button(self, text, color, slot, icon_path=None):
        """Buat button dengan style konsisten dan optional icon"""
        button = QPushButton(text)

        # Add icon if specified and path exists
        if icon_path:
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    button.setIcon(icon)
                    button.setIconSize(QSize(20, 20))
            except Exception:
                pass

        hover_color = self.darken_color(color)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border: 1px solid {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(hover_color)};
                border: 2px inset {self.darken_color(hover_color)};
            }}
        """)
        button.clicked.connect(slot)
        return button

    def darken_color(self, color):
        """Buat warna lebih gelap untuk hover effect"""
        color_map = {
            "#27ae60": "#229954",  # Hijau
            "#c0392b": "#a93226",  # Merah
            "#3498db": "#2980b9",  # Biru
            "#16a085": "#138d75",  # Teal
            "#8e44ad": "#7d3c98",  # Ungu
            "#f39c12": "#e67e22",  # Orange
            "#9b59b6": "#8e44ad",  # Purple
            "#2ecc71": "#27ae60",  # Light green
            "#e74c3c": "#c0392b",  # Light red
        }
        return color_map.get(color, color)

    def apply_professional_table_style(self, table):
        """Apply Excel-like table styling with thin grid lines and minimal borders"""
        # Header styling - Bold headers with center alignment
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)
        table.horizontalHeader().setFont(header_font)

        # Header with bold text, center alignment, and word wrap
        # IMPORTANT: Ensure header is always visible with adequate height
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #b4b4b4;
                border-right: 1px solid #b4b4b4;
                padding: 8px 6px;
                font-weight: bold;
                color: #1e1e1e;
                min-height: 35px;
            }
        """)

        # Configure header behavior
        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setSectionsClickable(True)
        # CRITICAL: Set minimum height to ensure visibility when maximized
        header.setMinimumHeight(35)
        header.setDefaultSectionSize(100)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(500)

        # Excel-style table body styling
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d4d4d4;
                background-color: white;
                border: 1px solid #d4d4d4;
                selection-background-color: #cce7ff;
                font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
                outline: none;
            }
            QTableWidget::item {
                border: none;
                padding: 4px 6px;
                min-height: 18px;
            }
            QTableWidget::item:selected {
                background-color: #cce7ff;
                color: black;
            }
            QTableWidget::item:focus {
                border: 2px solid #0078d4;
                background-color: white;
            }
        """)

        # Excel-style table settings - header configuration
        header = table.horizontalHeader()
        header.setDefaultSectionSize(80)

        # Enable scrolling
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Excel-style row settings
        table.verticalHeader().setDefaultSectionSize(20)
        table.setSelectionBehavior(QAbstractItemView.SelectItems)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(True)
        table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                border: none;
                border-bottom: 1px solid #d4d4d4;
                border-right: 1px solid #d4d4d4;
                padding: 2px;
                font-weight: normal;
                color: #333333;
                text-align: center;
                width: 30px;
            }
        """)

        # Enable grid display with thin lines
        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)

        # Excel-style editing and selection
        table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Set compact size for Excel look
        table.setMinimumHeight(150)
        table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)

    def closeEvent(self, event):
        """Cleanup when component closes - stop the image loader thread"""
        try:
            if hasattr(self, 'image_loader') and self.image_loader:
                self.image_loader.stop()
        except Exception:
            pass
        super().closeEvent(event)
