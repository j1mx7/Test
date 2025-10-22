#!/usr/bin/env python3
"""
Add Professional Toast System to AutoBios
Safe, standalone addition that won't break existing code
"""

from pathlib import Path
from datetime import datetime

source = Path("AutoBios.py")
backup = Path(f"AutoBios_toasts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

print("=" * 80)
print("AutoBios - Adding Professional Toast System")
print("=" * 80)

# Read
with open(source, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open(backup, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✓ Backup: {backup}\n")

# Find where to insert (before LoadingSpinner class)
insertion_point = content.find('class LoadingSpinner(QtWidgets.QWidget):')

if insertion_point < 0:
    print("❌ Could not find LoadingSpinner class")
    exit(1)

# New professional toast system
new_toast_system = '''
# ============================================================================
# PROFESSIONAL TOAST NOTIFICATION SYSTEM
# ============================================================================

class ProToastWidget(QtWidgets.QFrame):
    """
    Professional toast notification with modern design.
    Features: icons, title, body, action button, close button, smooth animations.
    """
    
    closed = Signal()
    
    def __init__(self, toast_type: str, title: str, body: str = "", action_text: str = "", parent=None):
        super().__init__(parent)
        self.toast_type = toast_type
        self.title_text = title
        self.body_text = body
        self._timer_paused = False
        self._dismiss_timer = None
        self._duplicate_count = 1
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedWidth(380)
        self.setMaximumHeight(150)
        
        # Opacity effect for animations
        self._opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(0.0)
        
        # Style
        self.setStyleSheet(f"""
            ProToastWidget {{
                background: {THEME['card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        
        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon and color
        icon_map = {"info": "ℹ", "success": "✓", "warning": "⚠", "error": "✕"}
        color_map = {
            "info": THEME['accent'],
            "success": THEME['success'],
            "warning": THEME['warn'],
            "error": THEME['error']
        }
        
        icon_label = QtWidgets.QLabel(icon_map.get(toast_type, "ℹ"))
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {color_map.get(toast_type, THEME['accent'])};
                font-size: 20px;
                font-weight: 600;
                background: transparent;
                min-width: 24px;
            }}
        """)
        layout.addWidget(icon_label)
        
        # Content
        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Title with counter
        title_layout = QtWidgets.QHBoxLayout()
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setStyleSheet(f"color: {THEME['text']}; font-size: 14px; font-weight: 600; background: transparent;")
        title_layout.addWidget(self.title_label, 1)
        
        self.count_label = QtWidgets.QLabel()
        self.count_label.setStyleSheet(f"color: {THEME['muted']}; font-size: 12px; background: transparent;")
        self.count_label.hide()
        title_layout.addWidget(self.count_label)
        content_layout.addLayout(title_layout)
        
        # Body
        if body:
            body_label = QtWidgets.QLabel(body)
            body_label.setWordWrap(True)
            body_label.setStyleSheet(f"color: {THEME['muted']}; font-size: 12px; background: transparent;")
            content_layout.addWidget(body_label)
        
        layout.addLayout(content_layout, 1)
        
        # Close button
        close_btn = QtWidgets.QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {THEME['muted']};
                font-size: 20px;
            }}
            QPushButton:hover {{ color: {THEME['text']}; }}
        """)
        close_btn.clicked.connect(self.close_toast)
        layout.addWidget(close_btn)
        
        # Animations
        self.fade_anim = QtCore.QPropertyAnimation(self._opacity_effect, b"opacity")
        self.fade_anim.setDuration(200)
        
        self.slide_anim = QtCore.QPropertyAnimation(self, b"pos")
        self.slide_anim.setDuration(250)
        self.slide_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        
        # Auto-dismiss (except errors)
        if toast_type != "error":
            self._dismiss_timer = QtCore.QTimer(self)
            self._dismiss_timer.setSingleShot(True)
            self._dismiss_timer.timeout.connect(self.close_toast)
            self._dismiss_timer.start(4000)
    
    def increment_count(self):
        """Increment duplicate counter"""
        self._duplicate_count += 1
        self.count_label.setText(f"×{self._duplicate_count}")
        self.count_label.show()
        if self._dismiss_timer:
            self._dismiss_timer.start(4000)
    
    def enterEvent(self, event):
        """Pause timer on hover"""
        if self._dismiss_timer and self._dismiss_timer.isActive():
            self._dismiss_timer.stop()
            self._timer_paused = True
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Resume timer"""
        if self._timer_paused and self._dismiss_timer:
            self._dismiss_timer.start(2000)
            self._timer_paused = False
        super().leaveEvent(event)
    
    def keyPressEvent(self, event):
        """ESC closes"""
        if event.key() == Qt.Key_Escape:
            self.close_toast()
        super().keyPressEvent(event)
    
    def show_toast(self, parent_widget, position: int):
        """Show with animation"""
        parent_rect = parent_widget.rect()
        parent_pos = parent_widget.mapToGlobal(QtCore.QPoint(0, 0))
        
        margin = 16
        title_bar_height = 60
        spacing = 12
        
        final_x = parent_pos.x() + parent_rect.width() - self.width() - margin
        final_y = parent_pos.y() + title_bar_height + margin + (position * (self.height() + spacing))
        start_y = final_y - 30
        
        self.move(final_x, start_y)
        self.show()
        
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()
        
        self.slide_anim.setStartValue(QtCore.QPoint(final_x, start_y))
        self.slide_anim.setEndValue(QtCore.QPoint(final_x, final_y))
        self.slide_anim.start()
    
    def close_toast(self):
        """Close with animation"""
        current_pos = self.pos()
        self.slide_anim.setStartValue(current_pos)
        self.slide_anim.setEndValue(QtCore.QPoint(current_pos.x(), current_pos.y() - 20))
        self.slide_anim.start()
        
        self.fade_anim.setStartValue(self._opacity_effect.opacity())
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(lambda: (self.closed.emit(), self.deleteLater()))
        self.fade_anim.start()


class ProToastManager(QtCore.QObject):
    """
    Professional toast manager with queue, deduplication, and positioning.
    Max 4 toasts visible.
    """
    
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.toasts: list = []
        self._last_messages: dict = {}
        self.max_toasts = 4
    
    def _get_key(self, toast_type: str, title: str, body: str) -> str:
        return f"{toast_type}:{title}:{body}"
    
    def _should_dedupe(self, key: str):
        """Check for duplicate within 2s"""
        import time
        now = time.time()
        
        if key in self._last_messages and now - self._last_messages[key] < 2.0:
            for toast in self.toasts:
                if self._get_key(toast.toast_type, toast.title_text, toast.body_text) == key:
                    return toast
        
        self._last_messages[key] = now
        return None
    
    def _reposition(self):
        """Reposition all toasts"""
        for i, toast in enumerate(self.toasts):
            parent_rect = self.parent_widget.rect()
            parent_pos = self.parent_widget.mapToGlobal(QtCore.QPoint(0, 0))
            
            final_x = parent_pos.x() + parent_rect.width() - toast.width() - 16
            final_y = parent_pos.y() + 60 + 16 + (i * (toast.height() + 12))
            
            toast.slide_anim.setStartValue(toast.pos())
            toast.slide_anim.setEndValue(QtCore.QPoint(final_x, final_y))
            toast.slide_anim.start()
    
    def _show(self, toast_type: str, title: str, body: str = ""):
        """Show toast"""
        key = self._get_key(toast_type, title, body)
        
        existing = self._should_dedupe(key)
        if existing:
            existing.increment_count()
            return
        
        if len(self.toasts) >= self.max_toasts:
            self.toasts[0].close_toast()
        
        toast = ProToastWidget(toast_type, title, body, "", self.parent_widget)
        toast.closed.connect(lambda: self._on_closed(toast))
        
        self.toasts.append(toast)
        toast.show_toast(self.parent_widget, len(self.toasts) - 1)
    
    def _on_closed(self, toast):
        """Handle close"""
        if toast in self.toasts:
            self.toasts.remove(toast)
            self._reposition()
    
    def info(self, title: str, body: str = ""):
        self._show("info", title, body)
    
    def success(self, title: str, body: str = ""):
        self._show("success", title, body)
    
    def warning(self, title: str, body: str = ""):
        self._show("warning", title, body)
    
    def error(self, title: str, body: str = ""):
        self._show("error", title, body)


'''

# Insert new system
content = content[:insertion_point] + new_toast_system + '\n' + content[insertion_point:]

print("✓ Added Professional Toast System")

# Add toast manager initialization (find where notifications manager is created)
notif_init_pattern = r'(self\.notifications = NotificationManager\(self\))'
if notif_init_pattern in content:
    content = content.replace(
        'self.notifications = NotificationManager(self)',
        'self.notifications = NotificationManager(self)  # Legacy\n        self.toast = ProToastManager(self)  # New professional toasts'
    )
    print("✓ Added toast manager initialization")
else:
    print("⚠ Could not find notification manager init - add manually")

# Write
with open(source, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ Changes written")

# Validate
try:
    compile(content, 'AutoBios.py', 'exec')
    print("✓ Syntax OK\n")
except SyntaxError as e:
    print(f"❌ Syntax error at line {e.lineno}: {e.msg}\n")
    exit(1)

print("=" * 80)
print("✅ Professional Toast System Added!")
print("=" * 80)
print("\nAPI:")
print("  self.toast.info('Title', 'Body')")
print("  self.toast.success('Title', 'Body')")
print("  self.toast.warning('Title', 'Body')")
print("  self.toast.error('Title', 'Body')")
print("\nFeatures:")
print("  • Top-right positioning")
print("  • Smooth slide-down/up animations")
print("  • Auto-dismiss (except errors)")
print("  • Deduplication with ×N counter")
print("  • Hover pauses timer")
print("  • ESC closes")
print("  • Max 4 visible")
print(f"\nBackup: {backup}")
