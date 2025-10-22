"""
Custom Outline-Style Confirmation Modal for AutoBios
Replaces stock Windows message boxes with modern, themed dialogs
"""

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, Signal

# Import theme from main app (will be integrated into AutoBios.py)
THEME = {
    "bg": "#0a0e13",
    "card": "#0f1419",
    "card_hover": "#151b22",
    "text": "#e4e6eb",
    "muted": "#9ca3af",
    "border": "#1a2332",
    "input_border": "#30363d",
    "input_focus": "#4a90e2",
    "accent": "#4a90e2",
    "accent_hover": "#5b9def",
    "error": "#ef4444",
}


class OutlineConfirmDialog(QtWidgets.QDialog):
    """
    Custom confirmation dialog with outline style
    Features:
    - Frameless with rounded corners
    - Thin 1px outline buttons
    - Smooth fade-in animation
    - ESC/Enter keyboard handling
    - Centered within parent
    """
    
    def __init__(self, parent=None, title="Confirm", message="Are you sure?", 
                 confirm_text="Confirm", cancel_text="Cancel"):
        super().__init__(parent)
        
        # Frameless dialog with transparency
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        # Result
        self.confirmed = False
        
        # Main container with rounded corners
        container = QtWidgets.QWidget()
        container.setObjectName("dialogContainer")
        container.setStyleSheet(f"""
            QWidget#dialogContainer {{
                background: {THEME['card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        
        container_layout = QtWidgets.QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(container)
        
        # Content layout
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)
        
        # Title
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {THEME['text']};
            background: transparent;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Message
        message_label = QtWidgets.QLabel(message)
        message_label.setStyleSheet(f"""
            font-size: 14px;
            color: {THEME['muted']};
            background: transparent;
        """)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Buttons row
        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(12)
        button_row.addStretch()
        
        # Cancel button
        self.cancel_btn = QtWidgets.QPushButton(cancel_text)
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {THEME['input_border']};
                border-radius: 10px;
                padding: 8px 20px;
                color: {THEME['text']};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: transparent;
                border-color: {THEME['input_focus']};
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.10);
                border-color: {THEME['accent']};
            }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        button_row.addWidget(self.cancel_btn)
        
        # Confirm button (slightly stronger outline)
        self.confirm_btn = QtWidgets.QPushButton(confirm_text)
        self.confirm_btn.setMinimumWidth(100)
        self.confirm_btn.setMinimumHeight(36)
        self.confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1.5px solid {THEME['accent']};
                border-radius: 10px;
                padding: 8px 20px;
                color: {THEME['text']};
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: transparent;
                border-color: {THEME['accent_hover']};
            }}
            QPushButton:pressed {{
                background: rgba(74, 144, 226, 0.15);
                border-color: {THEME['accent']};
            }}
        """)
        self.confirm_btn.clicked.connect(self.accept)
        self.confirm_btn.setCursor(Qt.PointingHandCursor)
        self.confirm_btn.setDefault(True)
        button_row.addWidget(self.confirm_btn)
        
        button_row.addStretch()
        layout.addLayout(button_row)
        
        # Set fixed width
        self.setFixedWidth(440)
        
        # Fade-in animation
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        container.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(200)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        
    def showEvent(self, event):
        """Center dialog and start fade-in animation"""
        super().showEvent(event)
        
        # Center on parent
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2
            )
        
        # Start fade-in
        self.fade_in.start()
    
    def keyPressEvent(self, event):
        """Handle ESC and Enter keys"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
        else:
            super().keyPressEvent(event)
    
    def accept(self):
        """Confirm action"""
        self.confirmed = True
        super().accept()
    
    def reject(self):
        """Cancel action"""
        self.confirmed = False
        super().reject()
    
    @staticmethod
    def confirm(parent, title, message, confirm_text="Confirm", cancel_text="Cancel"):
        """Static method to show confirmation dialog"""
        dialog = OutlineConfirmDialog(parent, title, message, confirm_text, cancel_text)
        result = dialog.exec()
        return result == QtWidgets.QDialog.Accepted


# Example usage:
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    # Dark theme stylesheet
    app.setStyleSheet(f"""
        QWidget {{
            background: {THEME['bg']};
            color: {THEME['text']};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
    """)
    
    # Test window
    window = QtWidgets.QWidget()
    window.setWindowTitle("Test Outline Confirm Dialog")
    window.resize(600, 400)
    
    layout = QtWidgets.QVBoxLayout(window)
    
    test_btn = QtWidgets.QPushButton("Show Confirm Dialog")
    test_btn.clicked.connect(
        lambda: print("Confirmed!" if OutlineConfirmDialog.confirm(
            window, 
            "Confirm Action", 
            "Are you sure you want to proceed with this action?",
            "Yes, Proceed",
            "Cancel"
        ) else "Cancelled")
    )
    layout.addWidget(test_btn)
    
    window.show()
    sys.exit(app.exec())
