# Path: server/components/proker_base.py
# Shared base classes and utilities for program kerja components

import csv
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
                            QFormLayout, QLineEdit, QTextEdit, QDateEdit,
                            QDialogButtonBox, QComboBox, QSpinBox, QMenu, QFileDialog,
                            QMessageBox, QStyle, QStyleOptionHeader)
from PyQt5.QtCore import Qt, QSize, QRect, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QFont, QPainter, QColor


class WordWrapHeaderView(QHeaderView):
    """Custom header view with word wrap and center alignment support"""
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)

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

                # Create font metrics
                font = self.font()
                font.setBold(True)
                fm = self.fontMetrics()

                # Calculate text rect with word wrap
                rect = fm.boundingRect(0, 0, width - 8, 1000,
                                      Qt.AlignCenter | Qt.TextWordWrap, str(text))

                # Return size with padding
                return QSize(width, max(rect.height() + 12, 25))

        return super().sectionSizeFromContents(logicalIndex)

    def paintSection(self, painter, rect, logicalIndex):
        """Paint section with word wrap and center alignment"""
        painter.save()

        # Draw background with consistent color
        bg_color = QColor(242, 242, 242)  # #f2f2f2
        painter.fillRect(rect, bg_color)

        # Draw borders
        border_color = QColor(212, 212, 212)  # #d4d4d4
        painter.setPen(border_color)
        # Right border
        painter.drawLine(rect.topRight(), rect.bottomRight())
        # Bottom border
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        # Get header text
        if self.model():
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                # Setup font
                font = self.font()
                font.setBold(True)
                painter.setFont(font)

                # Text color
                text_color = QColor(51, 51, 51)  # #333333
                painter.setPen(text_color)

                # Draw text with word wrap and center alignment
                text_rect = rect.adjusted(4, 4, -4, -4)
                painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, str(text))

        painter.restore()


class WorkProgramDialog(QDialog):
    """Dialog untuk menambah/edit program kerja"""

    def __init__(self, parent=None, program_data=None):
        super().__init__(parent)
        self.program_data = program_data
        self.setup_ui()

        if program_data:
            self.load_data()

    def setup_ui(self):
        self.setWindowTitle("Program Kerja" if not self.program_data else "Edit Program Kerja")
        self.setModal(True)
        self.setFixedSize(500, 400)

        layout = QVBoxLayout(self)

        # Form layout - sesuai dengan kolom tabel baru
        form_layout = QFormLayout()

        # Kategori (tambah sebelum Estimasi Waktu)
        self.category_input = QComboBox()
        self.category_input.addItems([
            "Ibadah", "Doa", "Katekese", "Sosial",
            "Rohani", "Administratif", "Perayaan", "Lainnya"
        ])
        form_layout.addRow("Kategori:", self.category_input)

        # Estimasi Waktu (bulan dropdown - renamed from tanggal)
        self.month_input = QComboBox()
        self.month_input.addItems([
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ])
        form_layout.addRow("Estimasi Waktu (Bulan):", self.month_input)

        # Perayaan/Program (Judul Program yang akan direncanakan)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Masukkan judul program/perayaan")
        form_layout.addRow("Perayaan/Program:", self.title_input)

        # Sasaran (tujuan dari program/tokoh yang dituju)
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Sasaran/tujuan program atau tokoh yang dituju")
        form_layout.addRow("Sasaran:", self.target_input)

        # PIC (penanggung jawab)
        self.responsible_input = QLineEdit()
        self.responsible_input.setPlaceholderText("Person In Charge (PIC)")
        form_layout.addRow("PIC:", self.responsible_input)

        # Anggaran
        self.budget_amount_input = QLineEdit()
        self.budget_amount_input.setPlaceholderText("Jumlah anggaran (Rp)")
        form_layout.addRow("Anggaran:", self.budget_amount_input)

        # Sumber Anggaran
        self.budget_source_input = QComboBox()
        self.budget_source_input.addItems([
            "Kas Gereja", "Donasi Jemaat", "Sponsor External",
            "Dana Komisi", "APBG", "Kolekte Khusus", "Lainnya"
        ])
        form_layout.addRow("Sumber Anggaran:", self.budget_source_input)

        # Keterangan (tambah setelah Sumber Anggaran) - renamed from Deskripsi
        self.keterangan_input = QTextEdit()
        self.keterangan_input.setPlaceholderText("Keterangan lengkap program kerja (opsional)")
        self.keterangan_input.setMaximumHeight(80)
        form_layout.addRow("Keterangan:", self.keterangan_input)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_data(self):
        """Load data for editing"""
        if not self.program_data:
            return

        # Load kategori
        self.category_input.setCurrentText(self.program_data.get('category', 'Ibadah'))

        # Load estimasi waktu (bulan)
        month_str = self.program_data.get('month', '')
        if month_str:
            self.month_input.setCurrentText(month_str)

        # Load program title
        self.title_input.setText(self.program_data.get('title', ''))

        # Load target/sasaran
        self.target_input.setText(self.program_data.get('target', ''))

        # Load PIC
        self.responsible_input.setText(self.program_data.get('responsible', ''))

        # Load budget amount
        self.budget_amount_input.setText(self.program_data.get('budget_amount', ''))

        # Load budget source
        self.budget_source_input.setCurrentText(self.program_data.get('budget_source', 'Kas Gereja'))

        # Load keterangan
        self.keterangan_input.setText(self.program_data.get('keterangan', ''))

    def get_data(self):
        """Get form data sesuai dengan kolom tabel baru"""
        return {
            'category': self.category_input.currentText(),
            'month': self.month_input.currentText(),
            'title': self.title_input.text().strip(),
            'target': self.target_input.text().strip(),
            'responsible': self.responsible_input.text().strip(),
            'budget_amount': self.budget_amount_input.text().strip(),
            'budget_source': self.budget_source_input.currentText(),
            'keterangan': self.keterangan_input.toPlainText().strip()
        }
