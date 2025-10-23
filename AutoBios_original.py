# AutoBios - Luxury Digital Interface
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import re
import sys
import subprocess
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import List, Tuple, Optional, Union, Dict, Any, Callable
from datetime import datetime
from functools import partial
from difflib import get_close_matches
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal, QPersistentModelIndex, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont, QFontDatabase, QPainter, QPen, QBrush, QColor, QLinearGradient, QRadialGradient, QPainterPath
from PySide6.QtWidgets import QGraphicsDropShadowEffect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# =============================================================================
# LUXURY THEME SYSTEM
# =============================================================================

class LuxuryTheme:
    """Sophisticated color palette embodying luxury and precision"""
    
    # Core neutrals - sophisticated and refined
    CHAMPAGNE = "#F7F3E9"      # Warm off-white
    PEARL = "#FEFEFE"          # Pure white
    PLATINUM = "#E8E8E8"       # Light gray
    GRAPHITE = "#4A4A4A"       # Medium gray
    CHARCOAL = "#2C2C2C"       # Dark gray
    OBSIDIAN = "#1A1A1A"       # Deep black
    
    # Accent colors - subtle luxury touches
    GOLD = "#D4AF37"           # Elegant gold
    ROSE_GOLD = "#E8B4B8"      # Soft rose gold
    SILVER = "#C0C0C0"         # Metallic silver
    
    # Semantic colors - refined and professional
    SUCCESS = "#4A7C59"        # Muted forest green
    WARNING = "#B8860B"        # Dark goldenrod
    ERROR = "#8B4513"          # Saddle brown (sophisticated error)
    INFO = "#4682B4"           # Steel blue
    
    # Transparency levels
    GLASS = "rgba(247, 243, 233, 0.95)"      # Champagne glass
    FROST = "rgba(248, 248, 248, 0.85)"      # Frosted glass
    SHADOW = "rgba(26, 26, 26, 0.15)"        # Subtle shadow
    
    # Typography
    FONT_FAMILY = "SF Pro Display"  # Apple's premium font
    FONT_WEIGHT_LIGHT = 300
    FONT_WEIGHT_REGULAR = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_SEMIBOLD = 600

# =============================================================================
# LUXURY STYLING SYSTEM
# =============================================================================

class LuxuryStyling:
    """Centralized styling system for consistent luxury aesthetics"""
    
    @staticmethod
    def get_main_stylesheet() -> str:
        """Main application stylesheet with luxury design principles"""
        return f"""
        /* ===== LUXURY INTERFACE STYLES ===== */
        
        QWidget {{
            font-family: '{LuxuryTheme.FONT_FAMILY}', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-weight: {LuxuryTheme.FONT_WEIGHT_REGULAR};
            color: {LuxuryTheme.CHARCOAL};
            background: transparent;
        }}
        
        /* ===== MAIN WINDOW ===== */
        QWidget#mainContainer {{
            background: {LuxuryTheme.PEARL};
            border-radius: 20px;
            border: 1px solid {LuxuryTheme.PLATINUM};
        }}
        
        /* ===== TITLE BAR ===== */
        QWidget#titleBar {{
            background: transparent;
            border: none;
            border-radius: 20px 20px 0px 0px;
            padding: 0px;
        }}
        
        QLabel#title {{
            font-size: 24px;
            font-weight: {LuxuryTheme.FONT_WEIGHT_SEMIBOLD};
            color: {LuxuryTheme.OBSIDIAN};
            letter-spacing: -0.5px;
            padding: 0px;
            margin: 0px;
        }}
        
        QLabel#subtitle {{
            font-size: 14px;
            font-weight: {LuxuryTheme.FONT_WEIGHT_LIGHT};
            color: {LuxuryTheme.GRAPHITE};
            letter-spacing: 0.2px;
            padding: 0px;
            margin: 0px;
        }}
        
        /* ===== LUXURY BUTTONS ===== */
        QPushButton {{
            background: transparent;
            border: 1px solid {LuxuryTheme.PLATINUM};
            border-radius: 12px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: {LuxuryTheme.FONT_WEIGHT_MEDIUM};
            color: {LuxuryTheme.CHARCOAL};
            letter-spacing: 0.3px;
            min-height: 20px;
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background: {LuxuryTheme.CHAMPAGNE};
            border: 1px solid {LuxuryTheme.GOLD};
            color: {LuxuryTheme.OBSIDIAN};
        }}
        
        QPushButton:pressed {{
            background: {LuxuryTheme.PLATINUM};
            border: 1px solid {LuxuryTheme.GRAPHITE};
        }}
        
        QPushButton:disabled {{
            color: {LuxuryTheme.PLATINUM};
            border: 1px solid {LuxuryTheme.PLATINUM};
            background: transparent;
        }}
        
        /* ===== PRIMARY BUTTON ===== */
        QPushButton#primaryButton {{
            background: {LuxuryTheme.GOLD};
            border: 1px solid {LuxuryTheme.GOLD};
            color: {LuxuryTheme.PEARL};
            font-weight: {LuxuryTheme.FONT_WEIGHT_SEMIBOLD};
        }}
        
        QPushButton#primaryButton:hover {{
            background: {LuxuryTheme.ROSE_GOLD};
            border: 1px solid {LuxuryTheme.ROSE_GOLD};
        }}
        
        QPushButton#primaryButton:pressed {{
            background: {LuxuryTheme.CHARCOAL};
            border: 1px solid {LuxuryTheme.CHARCOAL};
        }}
        
        /* ===== LUXURY INPUT FIELDS ===== */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background: {LuxuryTheme.PEARL};
            border: 1px solid {LuxuryTheme.PLATINUM};
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 14px;
            font-weight: {LuxuryTheme.FONT_WEIGHT_REGULAR};
            color: {LuxuryTheme.CHARCOAL};
            selection-background-color: {LuxuryTheme.CHAMPAGNE};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {LuxuryTheme.GOLD};
            background: {LuxuryTheme.CHAMPAGNE};
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background: {LuxuryTheme.PLATINUM};
            color: {LuxuryTheme.GRAPHITE};
            border: 1px solid {LuxuryTheme.PLATINUM};
        }}
        
        /* ===== LUXURY COMBO BOXES ===== */
        QComboBox {{
            background: {LuxuryTheme.PEARL};
            border: 1px solid {LuxuryTheme.PLATINUM};
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 14px;
            font-weight: {LuxuryTheme.FONT_WEIGHT_REGULAR};
            color: {LuxuryTheme.CHARCOAL};
            min-height: 20px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {LuxuryTheme.GOLD};
            background: {LuxuryTheme.CHAMPAGNE};
        }}
        
        QComboBox:focus {{
            border: 1px solid {LuxuryTheme.GOLD};
            background: {LuxuryTheme.CHAMPAGNE};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {LuxuryTheme.GRAPHITE};
            margin-right: 8px;
        }}
        
        QComboBox QAbstractItemView {{
            background: {LuxuryTheme.PEARL};
            border: 1px solid {LuxuryTheme.PLATINUM};
            border-radius: 8px;
            selection-background-color: {LuxuryTheme.CHAMPAGNE};
            selection-color: {LuxuryTheme.CHARCOAL};
            outline: none;
        }}
        
        QComboBox QAbstractItemView::item {{
            padding: 12px 16px;
            border: none;
            min-height: 20px;
        }}
        
        QComboBox QAbstractItemView::item:hover {{
            background: {LuxuryTheme.CHAMPAGNE};
        }}
        
        /* ===== LUXURY TABLES ===== */
        QTableWidget {{
            background: {LuxuryTheme.PEARL};
            border: 1px solid {LuxuryTheme.PLATINUM};
            border-radius: 12px;
            gridline-color: {LuxuryTheme.PLATINUM};
            selection-background-color: {LuxuryTheme.CHAMPAGNE};
            selection-color: {LuxuryTheme.CHARCOAL};
            font-size: 13px;
            font-weight: {LuxuryTheme.FONT_WEIGHT_REGULAR};
        }}
        
        QTableWidget::item {{
            padding: 12px 16px;
            border: none;
            border-bottom: 1px solid {LuxuryTheme.PLATINUM};
        }}
        
        QTableWidget::item:selected {{
            background: {LuxuryTheme.CHAMPAGNE};
            color: {LuxuryTheme.CHARCOAL};
        }}
        
        QTableWidget::item:hover {{
            background: {LuxuryTheme.CHAMPAGNE};
        }}
        
        QHeaderView::section {{
            background: {LuxuryTheme.CHAMPAGNE};
            color: {LuxuryTheme.CHARCOAL};
            font-weight: {LuxuryTheme.FONT_WEIGHT_SEMIBOLD};
            font-size: 12px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            padding: 16px;
            border: none;
            border-bottom: 1px solid {LuxuryTheme.PLATINUM};
            border-right: 1px solid {LuxuryTheme.PLATINUM};
        }}
        
        QHeaderView::section:first {{
            border-top-left-radius: 12px;
        }}
        
        QHeaderView::section:last {{
            border-top-right-radius: 12px;
            border-right: none;
        }}
        
        /* ===== LUXURY SCROLLBARS ===== */
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {LuxuryTheme.PLATINUM};
            border-radius: 4px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {LuxuryTheme.GRAPHITE};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
        }}
        
        QScrollBar:horizontal {{
            background: transparent;
            height: 8px;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {LuxuryTheme.PLATINUM};
            border-radius: 4px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {LuxuryTheme.GRAPHITE};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: transparent;
        }}
        
        /* ===== LUXURY TOGGLE SWITCH ===== */
        QWidget#toggleSwitch {{
            background: {LuxuryTheme.PLATINUM};
            border-radius: 16px;
            border: 1px solid {LuxuryTheme.PLATINUM};
        }}
        
        QWidget#toggleSwitch:checked {{
            background: {LuxuryTheme.GOLD};
            border: 1px solid {LuxuryTheme.GOLD};
        }}
        
        QWidget#toggleHandle {{
            background: {LuxuryTheme.PEARL};
            border-radius: 14px;
            border: 1px solid {LuxuryTheme.PLATINUM};
        }}
        
        /* ===== LUXURY PROGRESS BAR ===== */
        QProgressBar {{
            background: {LuxuryTheme.PLATINUM};
            border: 1px solid {LuxuryTheme.PLATINUM};
            border-radius: 8px;
            text-align: center;
            font-weight: {LuxuryTheme.FONT_WEIGHT_MEDIUM};
            color: {LuxuryTheme.CHARCOAL};
        }}
        
        QProgressBar::chunk {{
            background: {LuxuryTheme.GOLD};
            border-radius: 7px;
        }}
        
        /* ===== LUXURY DIALOGS ===== */
        QDialog {{
            background: {LuxuryTheme.PEARL};
            border-radius: 16px;
            border: 1px solid {LuxuryTheme.PLATINUM};
        }}
        
        /* ===== LUXURY LABELS ===== */
        QLabel {{
            color: {LuxuryTheme.CHARCOAL};
            font-weight: {LuxuryTheme.FONT_WEIGHT_REGULAR};
        }}
        
        QLabel#sectionTitle {{
            font-size: 18px;
            font-weight: {LuxuryTheme.FONT_WEIGHT_SEMIBOLD};
            color: {LuxuryTheme.OBSIDIAN};
            letter-spacing: -0.3px;
            margin-bottom: 8px;
        }}
        
        QLabel#sectionSubtitle {{
            font-size: 13px;
            font-weight: {LuxuryTheme.FONT_WEIGHT_LIGHT};
            color: {LuxuryTheme.GRAPHITE};
            letter-spacing: 0.2px;
            margin-bottom: 16px;
        }}
        
        /* ===== LUXURY GROUP BOXES ===== */
        QGroupBox {{
            background: transparent;
            border: 1px solid {LuxuryTheme.PLATINUM};
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 8px;
            font-weight: {LuxuryTheme.FONT_WEIGHT_MEDIUM};
            color: {LuxuryTheme.CHARCOAL};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px 0 8px;
            background: {LuxuryTheme.PEARL};
            font-size: 13px;
            letter-spacing: 0.3px;
        }}
        
        /* ===== LUXURY TOOLTIPS ===== */
        QToolTip {{
            background: {LuxuryTheme.OBSIDIAN};
            color: {LuxuryTheme.PEARL};
            border: 1px solid {LuxuryTheme.GRAPHITE};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 12px;
            font-weight: {LuxuryTheme.FONT_WEIGHT_REGULAR};
        }}
        
        /* ===== LUXURY MENUS ===== */
        QMenu {{
            background: {LuxuryTheme.PEARL};
            border: 1px solid {LuxuryTheme.PLATINUM};
            border-radius: 8px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 16px;
            border-radius: 6px;
            margin: 1px;
        }}
        
        QMenu::item:selected {{
            background: {LuxuryTheme.CHAMPAGNE};
            color: {LuxuryTheme.CHARCOAL};
        }}
        
        QMenu::separator {{
            height: 1px;
            background: {LuxuryTheme.PLATINUM};
            margin: 4px 8px;
        }}
        """

# =============================================================================
# LUXURY ANIMATION SYSTEM
# =============================================================================

class LuxuryAnimation(QPropertyAnimation):
    """Smooth, fluid animations for luxury feel"""
    
    def __init__(self, target, property_name, duration=200, easing=QEasingCurve.OutCubic):
        super().__init__(target, property_name.encode())
        self.setDuration(duration)
        self.setEasingCurve(easing)

class FadeAnimation(LuxuryAnimation):
    """Elegant fade in/out animations"""
    
    def __init__(self, target, fade_in=True, duration=300):
        super().__init__(target, b"windowOpacity", duration)
        self.fade_in = fade_in
        if fade_in:
            self.setStartValue(0.0)
            self.setEndValue(1.0)
        else:
            self.setStartValue(1.0)
            self.setEndValue(0.0)

class SlideAnimation(LuxuryAnimation):
    """Smooth slide animations"""
    
    def __init__(self, target, direction="right", duration=250):
        super().__init__(target, b"pos", duration)
        self.direction = direction

# =============================================================================
# LUXURY CUSTOM WIDGETS
# =============================================================================

class LuxuryButton(QtWidgets.QPushButton):
    """Elegant button with luxury styling and animations"""
    
    def __init__(self, text="", parent=None, primary=False):
        super().__init__(text, parent)
        self.primary = primary
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Configure luxury button appearance"""
        if self.primary:
            self.setObjectName("primaryButton")
        
        # Add subtle shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(LuxuryTheme.SHADOW))
        self.setGraphicsEffect(shadow)
    
    def setup_animations(self):
        """Setup hover and press animations"""
        self.hover_animation = LuxuryAnimation(self, b"geometry", 150)
        self.press_animation = LuxuryAnimation(self, b"geometry", 100)
    
    def enterEvent(self, event):
        """Smooth hover effect"""
        if not self.isEnabled():
            return
        
        # Subtle scale effect
        current_rect = self.geometry()
        new_rect = current_rect.adjusted(-1, -1, 1, 1)
        self.hover_animation.setStartValue(current_rect)
        self.hover_animation.setEndValue(new_rect)
        self.hover_animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Return to normal size"""
        if not self.isEnabled():
            return
        
        current_rect = self.geometry()
        original_rect = current_rect.adjusted(1, 1, -1, -1)
        self.hover_animation.setStartValue(current_rect)
        self.hover_animation.setEndValue(original_rect)
        self.hover_animation.start()
        super().leaveEvent(event)

class LuxuryInput(QtWidgets.QLineEdit):
    """Elegant input field with luxury styling"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Configure luxury input appearance"""
        self.setMinimumHeight(44)  # Touch-friendly height
        self.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: 1px solid #E8E8E8;
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: 400;
                color: #2C2C2C;
            }
            QLineEdit:focus {
                border: 1px solid #D4AF37;
                background: #F7F3E9;
            }
        """)
    
    def setup_animations(self):
        """Setup focus animations"""
        self.focus_animation = LuxuryAnimation(self, b"geometry", 200)

class LuxuryCard(QtWidgets.QFrame):
    """Elegant card container with luxury styling"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Configure luxury card appearance"""
        self.setFrameStyle(QtWidgets.QFrame.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background: {LuxuryTheme.PEARL};
                border: 1px solid {LuxuryTheme.PLATINUM};
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        
        # Add subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(LuxuryTheme.SHADOW))
        self.setGraphicsEffect(shadow)
    
    def setup_animations(self):
        """Setup hover animations"""
        self.hover_animation = LuxuryAnimation(self, b"geometry", 200)

class LuxuryToggle(QtWidgets.QWidget):
    """Elegant toggle switch with luxury styling"""
    
    toggled = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checked = False
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Configure luxury toggle appearance"""
        self.setFixedSize(52, 28)
        self.setObjectName("toggleSwitch")
        
        # Handle
        self.handle = QtWidgets.QWidget(self)
        self.handle.setObjectName("toggleHandle")
        self.handle.setFixedSize(24, 24)
        self.handle.move(2, 2)
        
        self.setStyleSheet(f"""
            QWidget#toggleSwitch {{
                background: {LuxuryTheme.PLATINUM};
                border-radius: 14px;
                border: 1px solid {LuxuryTheme.PLATINUM};
            }}
            QWidget#toggleSwitch:checked {{
                background: {LuxuryTheme.GOLD};
                border: 1px solid {LuxuryTheme.GOLD};
            }}
            QWidget#toggleHandle {{
                background: {LuxuryTheme.PEARL};
                border-radius: 12px;
                border: 1px solid {LuxuryTheme.PLATINUM};
            }}
        """)
    
    def setup_animations(self):
        """Setup toggle animations"""
        self.toggle_animation = LuxuryAnimation(self.handle, b"pos", 200)
    
    def mousePressEvent(self, event):
        """Handle toggle click"""
        self.toggle()
        super().mousePressEvent(event)
    
    def toggle(self):
        """Toggle the switch state"""
        self.checked = not self.checked
        self.update_handle_position()
        self.toggled.emit(self.checked)
    
    def update_handle_position(self):
        """Animate handle to new position"""
        if self.checked:
            new_pos = self.handle.pos()
            new_pos.setX(26)  # Move to right
        else:
            new_pos = self.handle.pos()
            new_pos.setX(2)   # Move to left
        
        self.toggle_animation.setStartValue(self.handle.pos())
        self.toggle_animation.setEndValue(new_pos)
        self.toggle_animation.start()

# =============================================================================
# LUXURY MAIN WINDOW
# =============================================================================

class LuxuryTitleBar(QtWidgets.QWidget):
    """Elegant title bar with luxury styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Configure luxury title bar appearance"""
        self.setFixedHeight(60)
        self.setObjectName("titleBar")
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)
        
        # App title
        self.title_label = QtWidgets.QLabel("AutoBios")
        self.title_label.setObjectName("title")
        layout.addWidget(self.title_label)
        
        # Spacer
        layout.addStretch()
        
        # Window controls
        self.minimize_btn = self.create_control_button("−")
        self.maximize_btn = self.create_control_button("□")
        self.close_btn = self.create_control_button("×")
        
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
        
        # Connect signals
        self.minimize_btn.clicked.connect(self.parent_window.showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.parent_window.close)
    
    def create_control_button(self, text):
        """Create window control button"""
        btn = QtWidgets.QPushButton(text)
        btn.setFixedSize(32, 32)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 16px;
                font-size: 16px;
                font-weight: {LuxuryTheme.FONT_WEIGHT_MEDIUM};
                color: {LuxuryTheme.GRAPHITE};
            }}
            QPushButton:hover {{
                background: {LuxuryTheme.CHAMPAGNE};
                border: 1px solid {LuxuryTheme.PLATINUM};
                color: {LuxuryTheme.CHARCOAL};
            }}
        """)
        return btn
    
    def setup_animations(self):
        """Setup title bar animations"""
        self.hover_animation = LuxuryAnimation(self, b"geometry", 200)
    
    def toggle_maximize(self):
        """Toggle window maximized state"""
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()
    
    def mousePressEvent(self, event):
        """Handle title bar drag"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

class AutoBiosWindow(QtWidgets.QWidget):
    """Main luxury application window"""
    
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_ui()
        self.setup_animations()
    
    def setup_window(self):
        """Configure main window properties"""
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        # Set window title
        self.setWindowTitle("AutoBios - Luxury Digital Interface")
    
    def setup_ui(self):
        """Setup the luxury user interface"""
        # Main container with luxury styling
        self.main_container = QtWidgets.QWidget()
        self.main_container.setObjectName("mainContainer")
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.main_container)
        
        # Container layout
        container_layout = QtWidgets.QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Title bar
        self.title_bar = LuxuryTitleBar(self)
        container_layout.addWidget(self.title_bar)
        
        # Content area
        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        container_layout.addWidget(self.content_widget)
        
        # Apply luxury styling
        self.setStyleSheet(LuxuryStyling.get_main_stylesheet())
        
        # Create content
        self.create_content()
    
    def create_content(self):
        """Create the main content area"""
        layout = QtWidgets.QVBoxLayout(self.content_widget)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(24)
        
        # Header section
        self.create_header(layout)
        
        # Main content cards
        self.create_main_content(layout)
        
        # Footer section
        self.create_footer(layout)
    
    def create_header(self, layout):
        """Create luxury header section"""
        header_card = LuxuryCard()
        header_layout = QtWidgets.QVBoxLayout(header_card)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(12)
        
        # Main title
        title = QtWidgets.QLabel("Professional BIOS Management")
        title.setObjectName("sectionTitle")
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QtWidgets.QLabel("Precision tools for advanced system configuration")
        subtitle.setObjectName("sectionSubtitle")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_card)
    
    def create_main_content(self, layout):
        """Create main content area with cards"""
        # Create horizontal layout for cards
        cards_layout = QtWidgets.QHBoxLayout()
        cards_layout.setSpacing(20)
        
        # File Management Card
        file_card = self.create_file_management_card()
        cards_layout.addWidget(file_card)
        
        # Configuration Card
        config_card = self.create_configuration_card()
        cards_layout.addWidget(config_card)
        
        # Actions Card
        actions_card = self.create_actions_card()
        cards_layout.addWidget(actions_card)
        
        layout.addLayout(cards_layout)
    
    def create_file_management_card(self):
        """Create file management card"""
        card = LuxuryCard()
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(16)
        
        # Title
        title = QtWidgets.QLabel("File Management")
        title.setObjectName("sectionTitle")
        card_layout.addWidget(title)
        
        # File input
        file_input = LuxuryInput("Select BIOS file...")
        card_layout.addWidget(file_input)
        
        # File buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        browse_btn = LuxuryButton("Browse", primary=True)
        import_btn = LuxuryButton("Import")
        export_btn = LuxuryButton("Export")
        
        buttons_layout.addWidget(browse_btn)
        buttons_layout.addWidget(import_btn)
        buttons_layout.addWidget(export_btn)
        
        card_layout.addLayout(buttons_layout)
        
        return card
    
    def create_configuration_card(self):
        """Create configuration card"""
        card = LuxuryCard()
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(16)
        
        # Title
        title = QtWidgets.QLabel("Configuration")
        title.setObjectName("sectionTitle")
        card_layout.addWidget(title)
        
        # Settings
        settings_group = QtWidgets.QGroupBox("Advanced Settings")
        settings_layout = QtWidgets.QVBoxLayout(settings_group)
        settings_layout.setSpacing(12)
        
        # Toggle switches
        for setting in ["Auto-optimize", "Debug mode", "Verbose logging"]:
            setting_layout = QtWidgets.QHBoxLayout()
            setting_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QtWidgets.QLabel(setting)
            label.setStyleSheet(f"color: {LuxuryTheme.CHARCOAL}; font-weight: {LuxuryTheme.FONT_WEIGHT_MEDIUM};")
            
            toggle = LuxuryToggle()
            
            setting_layout.addWidget(label)
            setting_layout.addStretch()
            setting_layout.addWidget(toggle)
            
            settings_layout.addLayout(setting_layout)
        
        card_layout.addWidget(settings_group)
        
        return card
    
    def create_actions_card(self):
        """Create actions card"""
        card = LuxuryCard()
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(16)
        
        # Title
        title = QtWidgets.QLabel("Actions")
        title.setObjectName("sectionTitle")
        card_layout.addWidget(title)
        
        # Action buttons
        actions_layout = QtWidgets.QVBoxLayout()
        actions_layout.setSpacing(12)
        
        # Primary actions
        analyze_btn = LuxuryButton("Analyze System", primary=True)
        optimize_btn = LuxuryButton("Optimize Settings")
        backup_btn = LuxuryButton("Create Backup")
        restore_btn = LuxuryButton("Restore Backup")
        
        actions_layout.addWidget(analyze_btn)
        actions_layout.addWidget(optimize_btn)
        actions_layout.addWidget(backup_btn)
        actions_layout.addWidget(restore_btn)
        
        card_layout.addLayout(actions_layout)
        
        return card
    
    def create_footer(self, layout):
        """Create luxury footer section"""
        footer_card = LuxuryCard()
        footer_layout = QtWidgets.QHBoxLayout(footer_card)
        footer_layout.setContentsMargins(24, 16, 24, 16)
        footer_layout.setSpacing(16)
        
        # Status info
        status_label = QtWidgets.QLabel("System Ready")
        status_label.setStyleSheet(f"""
            color: {LuxuryTheme.SUCCESS};
            font-weight: {LuxuryTheme.FONT_WEIGHT_MEDIUM};
            font-size: 13px;
        """)
        footer_layout.addWidget(status_label)
        
        footer_layout.addStretch()
        
        # Version info
        version_label = QtWidgets.QLabel("v2.0.0")
        version_label.setStyleSheet(f"""
            color: {LuxuryTheme.GRAPHITE};
            font-size: 12px;
        """)
        footer_layout.addWidget(version_label)
        
        layout.addWidget(footer_card)
    
    def setup_animations(self):
        """Setup window animations"""
        self.fade_animation = FadeAnimation(self, fade_in=True, duration=400)
        self.slide_animation = SlideAnimation(self, direction="right", duration=300)
    
    def showEvent(self, event):
        """Handle window show event with animation"""
        self.fade_animation.start()
        super().showEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event with animation"""
        self.fade_animation.finished.connect(lambda: super().closeEvent(event))
        self.fade_animation.setDirection(self.fade_animation.Backward)
        self.fade_animation.start()

# =============================================================================
# LUXURY APPLICATION
# =============================================================================

class LuxuryApplication(QtWidgets.QApplication):
    """Main luxury application class"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setup_application()
    
    def setup_application(self):
        """Configure luxury application properties"""
        # Set application properties
        self.setApplicationName("AutoBios")
        self.setApplicationVersion("2.0.0")
        self.setOrganizationName("Luxury Digital Tools")
        
        # Set application icon (if available)
        # self.setWindowIcon(QtGui.QIcon("icon.png"))
        
        # Configure font
        font = QFont(LuxuryTheme.FONT_FAMILY, 10, LuxuryTheme.FONT_WEIGHT_REGULAR)
        self.setFont(font)
        
        # Enable high DPI scaling
        self.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main application entry point"""
    app = LuxuryApplication(sys.argv)
    
    # Create and show main window
    window = AutoBiosWindow()
    window.show()
    
    # Center window on screen
    screen = app.primaryScreen().geometry()
    window_geometry = window.frameGeometry()
    center_point = screen.center()
    window_geometry.moveCenter(center_point)
    window.move(window_geometry.topLeft())
    
    # Start application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()