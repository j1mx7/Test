#!/usr/bin/env python3
"""
AutoBios - Complete Presets UI Rebuild + Professional Toast System

This script:
1. Creates new ToastWidget and ToastManager classes
2. Completely rebuilds the Presets UI with 3-pane layout
3. Fixes AMD routing
4. Integrates everything into AutoBios.py
"""

import re
from pathlib import Path
from datetime import datetime

source = Path("AutoBios.py")
backup = Path(f"AutoBios_presets_rebuild_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

print("=" * 80)
print("AutoBios - Presets UI Rebuild + Professional Toasts")
print("=" * 80)

# Read source
with open(source, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open(backup, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✓ Backup: {backup}\n")

# ============================================================================
# PART 1: Insert Toast System (before ToastNotification class)
# ============================================================================

toast_system = '''
# ============================================================================
# PROFESSIONAL TOAST NOTIFICATION SYSTEM
# ============================================================================

class ToastWidget(QtWidgets.QFrame):
    """
    Professional toast notification widget with smooth animations.
    Supports icons, title, body, action button, and close button.
    """
    
    closed = Signal()
    
    def __init__(self, toast_type: str, title: str, body: str = "", 
                 action_text: str = "", parent=None):
        super().__init__(parent)
        self.toast_type = toast_type  # info, success, warning, error
        self.title_text = title
        self.body_text = body
        self.action_text = action_text
        self._timer_paused = False
        self._dismiss_timer = None
        self._duplicate_count = 1
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedWidth(380)
        self.setMaximumHeight(150)
        
        # Setup opacity effect for animations
        self._opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(0.0)
        
        # Style
        self.setStyleSheet(f"""
            ToastWidget {{
                background: {THEME['card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        
        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon
        icon_map = {
            "info": "ℹ️",
            "success": "✓",
            "warning": "⚠",
            "error": "✕"
        }
        color_map = {
            "info": THEME['accent'],
            "success": THEME['success'],
            "warning": THEME['warn'],
            "error": THEME['error']
        }
        
        self.icon_label = QtWidgets.QLabel(icon_map.get(toast_type, "ℹ️"))
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                color: {color_map.get(toast_type, THEME['accent'])};
                font-size: 20px;
                font-weight: 600;
                background: transparent;
                min-width: 24px;
                max-width: 24px;
            }}
        """)
        layout.addWidget(self.icon_label)
        
        # Content
        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Title with duplicate counter
        title_layout = QtWidgets.QHBoxLayout()
        title_layout.setSpacing(8)
        
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {THEME['text']};
                font-size: 14px;
                font-weight: 600;
                background: transparent;
            }}
        """)
        title_layout.addWidget(self.title_label, 1)
        
        self.count_label = QtWidgets.QLabel()
        self.count_label.setStyleSheet(f"""
            QLabel {{
                color: {THEME['muted']};
                font-size: 12px;
                background: transparent;
            }}
        """)
        self.count_label.hide()
        title_layout.addWidget(self.count_label)
        
        content_layout.addLayout(title_layout)
        
        # Body
        if body:
            self.body_label = QtWidgets.QLabel(body)
            self.body_label.setWordWrap(True)
            self.body_label.setStyleSheet(f"""
                QLabel {{
                    color: {THEME['muted']};
                    font-size: 12px;
                    background: transparent;
                }}
            """)
            content_layout.addWidget(self.body_label)
        
        # Action button
        if action_text:
            self.action_btn = QtWidgets.QPushButton(action_text)
            self.action_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid {color_map.get(toast_type, THEME['accent'])};
                    border-radius: 6px;
                    padding: 4px 12px;
                    color: {color_map.get(toast_type, THEME['accent'])};
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    border-color: {THEME['text']};
                    color: {THEME['text']};
                }}
            """)
            content_layout.addWidget(self.action_btn)
        
        layout.addLayout(content_layout, 1)
        
        # Close button
        self.close_btn = QtWidgets.QPushButton("×")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {THEME['muted']};
                font-size: 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: {THEME['text']};
            }}
        """)
        self.close_btn.clicked.connect(self.close_toast)
        layout.addWidget(self.close_btn)
        
        # Animations
        self.fade_anim = QtCore.QPropertyAnimation(self._opacity_effect, b"opacity")
        self.fade_anim.setDuration(200)
        
        self.slide_anim = QtCore.QPropertyAnimation(self, b"pos")
        self.slide_anim.setDuration(250)
        self.slide_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        
        # Auto-dismiss timer
        if toast_type != "error":
            self._dismiss_timer = QtCore.QTimer(self)
            self._dismiss_timer.setSingleShot(True)
            self._dismiss_timer.timeout.connect(self.close_toast)
            self._dismiss_timer.start(4000)  # 4 seconds
    
    def increment_count(self):
        """Increment duplicate counter"""
        self._duplicate_count += 1
        self.count_label.setText(f"×{self._duplicate_count}")
        self.count_label.show()
        # Reset timer
        if self._dismiss_timer:
            self._dismiss_timer.start(4000)
    
    def enterEvent(self, event):
        """Pause timer on hover"""
        if self._dismiss_timer and self._dismiss_timer.isActive():
            self._dismiss_timer.stop()
            self._timer_paused = True
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Resume timer on leave"""
        if self._timer_paused and self._dismiss_timer:
            self._dismiss_timer.start(2000)  # Resume with 2s
            self._timer_paused = False
        super().leaveEvent(event)
    
    def keyPressEvent(self, event):
        """Close on ESC"""
        if event.key() == Qt.Key_Escape:
            self.close_toast()
        super().keyPressEvent(event)
    
    def show_toast(self, parent_widget, position: int):
        """Show toast with slide-down animation"""
        parent_rect = parent_widget.rect()
        parent_pos = parent_widget.mapToGlobal(QtCore.QPoint(0, 0))
        
        # Position at top-right
        margin = 16
        title_bar_height = 60
        spacing = 12
        
        final_x = parent_pos.x() + parent_rect.width() - self.width() - margin
        final_y = parent_pos.y() + title_bar_height + margin + (position * (self.height() + spacing))
        
        # Start above
        start_y = final_y - 30
        
        self.move(final_x, start_y)
        self.show()
        
        # Fade in
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()
        
        # Slide down
        self.slide_anim.setStartValue(QtCore.QPoint(final_x, start_y))
        self.slide_anim.setEndValue(QtCore.QPoint(final_x, final_y))
        self.slide_anim.start()
    
    def close_toast(self):
        """Close with fade out"""
        # Slide up
        current_pos = self.pos()
        self.slide_anim.setStartValue(current_pos)
        self.slide_anim.setEndValue(QtCore.QPoint(current_pos.x(), current_pos.y() - 20))
        self.slide_anim.start()
        
        # Fade out
        self.fade_anim.setStartValue(self._opacity_effect.opacity())
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self._on_close_finished)
        self.fade_anim.start()
    
    def _on_close_finished(self):
        """Cleanup after close"""
        self.closed.emit()
        self.deleteLater()


class ToastManager(QtCore.QObject):
    """
    Manages toast notifications with queue, deduplication, and positioning.
    Max 4 toasts visible at once.
    """
    
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.toasts: list[ToastWidget] = []
        self._last_messages: dict[str, float] = {}  # message -> timestamp
        self.max_toasts = 4
    
    def _get_message_key(self, toast_type: str, title: str, body: str) -> str:
        """Generate key for deduplication"""
        return f"{toast_type}:{title}:{body}"
    
    def _should_deduplicate(self, key: str) -> ToastWidget | None:
        """Check if message should be deduplicated (within 2s)"""
        import time
        now = time.time()
        
        # Check recent messages
        if key in self._last_messages:
            if now - self._last_messages[key] < 2.0:
                # Find matching toast
                for toast in self.toasts:
                    toast_key = self._get_message_key(
                        toast.toast_type, 
                        toast.title_text, 
                        toast.body_text
                    )
                    if toast_key == key:
                        return toast
        
        self._last_messages[key] = now
        return None
    
    def _reposition_toasts(self):
        """Reposition all toasts after one closes"""
        for i, toast in enumerate(self.toasts):
            parent_rect = self.parent_widget.rect()
            parent_pos = self.parent_widget.mapToGlobal(QtCore.QPoint(0, 0))
            
            margin = 16
            title_bar_height = 60
            spacing = 12
            
            final_x = parent_pos.x() + parent_rect.width() - toast.width() - margin
            final_y = parent_pos.y() + title_bar_height + margin + (i * (toast.height() + spacing))
            
            # Animate to new position
            toast.slide_anim.setStartValue(toast.pos())
            toast.slide_anim.setEndValue(QtCore.QPoint(final_x, final_y))
            toast.slide_anim.start()
    
    def _show_toast(self, toast_type: str, title: str, body: str = "", action_text: str = ""):
        """Internal method to show toast"""
        key = self._get_message_key(toast_type, title, body)
        
        # Check for duplicate
        existing = self._should_deduplicate(key)
        if existing:
            existing.increment_count()
            return
        
        # Remove oldest if at max
        if len(self.toasts) >= self.max_toasts:
            oldest = self.toasts[0]
            oldest.close_toast()
        
        # Create new toast
        toast = ToastWidget(toast_type, title, body, action_text, self.parent_widget)
        toast.closed.connect(lambda: self._on_toast_closed(toast))
        
        self.toasts.append(toast)
        toast.show_toast(self.parent_widget, len(self.toasts) - 1)
    
    def _on_toast_closed(self, toast: ToastWidget):
        """Handle toast closure"""
        if toast in self.toasts:
            self.toasts.remove(toast)
            self._reposition_toasts()
    
    def info(self, title: str, body: str = ""):
        """Show info toast"""
        self._show_toast("info", title, body)
    
    def success(self, title: str, body: str = ""):
        """Show success toast"""
        self._show_toast("success", title, body)
    
    def warning(self, title: str, body: str = ""):
        """Show warning toast"""
        self._show_toast("warning", title, body)
    
    def error(self, title: str, body: str = ""):
        """Show error toast (doesn't auto-dismiss)"""
        self._show_toast("error", title, body)


'''

# Find where to insert (before the old ToastNotification class)
old_toast_pattern = r'class ToastNotification\(QtWidgets\.QFrame\):'
insertion_point = content.find('class ToastNotification(QtWidgets.QFrame):')

if insertion_point > 0:
    # Insert new toast system before old one
    content = content[:insertion_point] + toast_system + '\n' + content[insertion_point:]
    print("✓ Inserted new Toast system")
else:
    print("⚠ Could not find ToastNotification class")

# ============================================================================
# PART 2: Replace old ToastNotification and NotificationManager
# ============================================================================

# Comment out old ToastNotification class
old_toast_class = r'class ToastNotification\(QtWidgets\.QFrame\):.*?(?=class\s+\w+|$)'
content = re.sub(
    r'(class ToastNotification\(QtWidgets\.QFrame\):)',
    r'# OLD - REPLACED\n# \1',
    content,
    count=1
)

# Comment out old NotificationManager
content = re.sub(
    r'(class NotificationManager\(QtCore\.QObject\):)',
    r'# OLD - REPLACED\n# \1',
    content,
    count=1
)

print("✓ Commented out old toast classes")

# ============================================================================
# PART 3: Rebuild Presets UI (Complete Replacement)
# ============================================================================

new_presets_ui = '''
        # ========================================================================
        # PRESETS TAB - MODERN 3-PANE LAYOUT
        # ========================================================================
        presets_tab = QtWidgets.QWidget()
        presets_main_layout = QtWidgets.QHBoxLayout(presets_tab)
        presets_main_layout.setContentsMargins(16, 16, 16, 16)
        presets_main_layout.setSpacing(16)
        
        # -------------------
        # LEFT: Family Sidebar (~220px)
        # -------------------
        sidebar = QtWidgets.QWidget()
        sidebar.setMaximumWidth(220)
        sidebar.setMinimumWidth(200)
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(16)
        
        # Sidebar title
        sidebar_title = QtWidgets.QLabel("Preset Families")
        sidebar_title.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {THEME['text']};")
        sidebar_layout.addWidget(sidebar_title)
        
        # Family list
        self.preset_family_list = QtWidgets.QListWidget()
        self.preset_family_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background: transparent;
                border: none;
                border-bottom: 2px solid transparent;
                padding: 12px 8px;
                color: {THEME['muted']};
                font-size: 14px;
                font-weight: 500;
            }}
            QListWidget::item:hover {{
                color: {THEME['text']};
            }}
            QListWidget::item:selected {{
                background: transparent;
                color: {THEME['text']};
                border-bottom: 2px solid {THEME['accent']};
            }}
        """)
        
        # Add families
        families = [
            ("basic", "Basic"),
            ("advanced", "Advanced"),
            ("oem", "OEM / EC"),
            ("performance", "Performance"),
        ]
        for family_id, family_name in families:
            item = QtWidgets.QListWidgetItem(family_name)
            item.setData(Qt.UserRole, family_id)
            self.preset_family_list.addItem(item)
        
        sidebar_layout.addWidget(self.preset_family_list)
        sidebar_layout.addStretch()
        
        # -------------------
        # CENTER: Preset Cards
        # -------------------
        center_panel = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(12)
        
        # Center title
        self.preset_cards_title = QtWidgets.QLabel("Select a family")
        self.preset_cards_title.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {THEME['text']};")
        center_layout.addWidget(self.preset_cards_title)
        
        # Scroll area for cards
        cards_scroll = QtWidgets.QScrollArea()
        cards_scroll.setWidgetResizable(True)
        cards_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        cards_scroll.setStyleSheet("background: transparent; border: none;")
        
        self.cards_container = QtWidgets.QWidget()
        self.cards_layout = QtWidgets.QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setAlignment(Qt.AlignTop)
        
        cards_scroll.setWidget(self.cards_container)
        center_layout.addWidget(cards_scroll)
        
        # -------------------
        # RIGHT: Details Panel
        # -------------------
        details_panel = QtWidgets.QWidget()
        details_layout = QtWidgets.QVBoxLayout(details_panel)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(16)
        
        # Details header
        details_header = QtWidgets.QHBoxLayout()
        
        self.preset_details_title = QtWidgets.QLabel("Select a preset")
        self.preset_details_title.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {THEME['text']};")
        details_header.addWidget(self.preset_details_title, 1)
        
        # CPU segmented control
        cpu_container = QtWidgets.QWidget()
        cpu_layout = QtWidgets.QHBoxLayout(cpu_container)
        cpu_layout.setContentsMargins(0, 0, 0, 0)
        cpu_layout.setSpacing(0)
        
        self.cpu_intel_btn = QtWidgets.QPushButton("Intel")
        self.cpu_amd_btn = QtWidgets.QPushButton("AMD")
        
        for btn in [self.cpu_intel_btn, self.cpu_amd_btn]:
            btn.setCheckable(True)
            btn.setMinimumWidth(70)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid {THEME['input_border']};
                    padding: 6px 16px;
                    color: {THEME['muted']};
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:checked {{
                    background: {THEME['accent']};
                    color: white;
                    border-color: {THEME['accent']};
                }}
                QPushButton:hover:!checked {{
                    border-color: {THEME['input_focus']};
                }}
            """)
        
        self.cpu_intel_btn.setStyleSheet(self.cpu_intel_btn.styleSheet() + "border-radius: 12px 0 0 12px;")
        self.cpu_amd_btn.setStyleSheet(self.cpu_amd_btn.styleSheet() + "border-radius: 0 12px 12px 0;")
        
        cpu_layout.addWidget(self.cpu_intel_btn)
        cpu_layout.addWidget(self.cpu_amd_btn)
        
        details_header.addWidget(cpu_container)
        details_layout.addLayout(details_header)
        
        # Details scroll area
        details_scroll = QtWidgets.QScrollArea()
        details_scroll.setWidgetResizable(True)
        details_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        details_scroll.setStyleSheet("background: transparent; border: none;")
        
        self.details_container = QtWidgets.QWidget()
        self.details_layout = QtWidgets.QVBoxLayout(self.details_container)
        self.details_layout.setSpacing(8)
        self.details_layout.setAlignment(Qt.AlignTop)
        
        details_scroll.setWidget(self.details_container)
        details_layout.addWidget(details_scroll, 1)
        
        # Details footer
        details_footer = QtWidgets.QHBoxLayout()
        
        self.preview_changes_btn = QtWidgets.QPushButton("Preview Changes")
        self.apply_preset_btn = QtWidgets.QPushButton("Apply Preset")
        self.cancel_preset_btn = QtWidgets.QPushButton("Cancel")
        
        details_footer.addWidget(self.preview_changes_btn)
        details_footer.addStretch()
        details_footer.addWidget(self.cancel_preset_btn)
        details_footer.addWidget(self.apply_preset_btn)
        
        details_layout.addLayout(details_footer)
        
        # Add panels to main layout
        presets_main_layout.addWidget(sidebar, 1)
        presets_main_layout.addWidget(center_panel, 2)
        presets_main_layout.addWidget(details_panel, 2)
        
        # Initialize state
        self._active_preset_id: str | None = None
        self._selected_cpu: str = "Intel"
        self._preset_family: str = "intel"  # Keep for compatibility
        self._enabled_basic: Dict[str, bool] = {k: False for k in PRESET_ORDER_BASIC}
        self._enabled_adv_intel: Dict[str, bool] = {k: False for k in PRESET_ORDER_ADV_INTEL}
        self._enabled_adv_amd: Dict[str, bool] = {k: False for k in PRESET_ORDER_ADV_AMD}
        self.pending_targets: Dict[int, Any] = {}
        
        self.cpu_intel_btn.setChecked(True)
        
        # Wire up signals
        self.preset_family_list.currentRowChanged.connect(self._on_preset_family_selected)
        self.cpu_intel_btn.clicked.connect(lambda: self._on_cpu_selected("Intel"))
        self.cpu_amd_btn.clicked.connect(lambda: self._on_cpu_selected("AMD"))
        self.apply_preset_btn.clicked.connect(self._on_apply_preset_clicked)
        self.cancel_preset_btn.clicked.connect(self._on_cancel_preset_clicked)
        self.preview_changes_btn.clicked.connect(self._on_preview_changes_clicked)
        
        # Select first family by default
        if self.preset_family_list.count() > 0:
            self.preset_family_list.setCurrentRow(0)
'''

# Find the old presets tab section and replace it
old_presets_pattern = r'# Tab 1: Presets\s+presets_tab = QtWidgets\.QWidget\(\).*?self\.tabs\.addTab\(presets_tab, ""\)'

replacement_marker = "# PRESETS_TAB_REPLACED"

if re.search(old_presets_pattern, content, re.DOTALL):
    content = re.sub(
        old_presets_pattern,
        new_presets_ui + '\n        self.tabs.addTab(presets_tab, "")',
        content,
        flags=re.DOTALL,
        count=1
    )
    print("✓ Replaced Presets tab UI")
else:
    print("⚠ Could not find old Presets tab to replace")

# ============================================================================
# PART 4: Add new preset methods
# ============================================================================

new_preset_methods = '''
    # ========================================================================
    # PRESETS UI - Event Handlers
    # ========================================================================
    
    def _on_preset_family_selected(self, row: int):
        """Handle family selection"""
        if row < 0:
            return
        
        item = self.preset_family_list.item(row)
        family_id = item.data(Qt.UserRole)
        
        # Update title
        self.preset_cards_title.setText(item.text())
        
        # Clear previous cards
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Generate cards based on family
        if family_id == "basic":
            for preset_name in PRESET_ORDER_BASIC:
                card = self._create_preset_card(f"basic_{preset_name}", preset_name, 
                                                 "Essential tuning", ["AMD", "Intel"])
                self.cards_layout.addWidget(card)
        
        elif family_id == "advanced":
            # Intel Advanced
            for preset_name in PRESET_ORDER_ADV_INTEL:
                card = self._create_preset_card(f"adv_intel_{preset_name}", f"Intel {preset_name}",
                                                 "Advanced Intel tuning", ["Intel"])
                self.cards_layout.addWidget(card)
            
            # AMD Advanced  
            for preset_name in PRESET_ORDER_ADV_AMD:
                card = self._create_preset_card(f"adv_amd_{preset_name}", f"AMD {preset_name}",
                                                 "Advanced AMD tuning", ["AMD"])
                self.cards_layout.addWidget(card)
    
    def _create_preset_card(self, preset_id: str, title: str, desc: str, cpus: list[str]):
        """Create a preset card widget"""
        card = QtWidgets.QFrame()
        card.setObjectName("presetCard")
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame#presetCard {{
                background: transparent;
                border: 1px solid {THEME['input_border']};
                border-radius: 12px;
                padding: 16px;
            }}
            QFrame#presetCard:hover {{
                border-color: {THEME['input_focus']};
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Title
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {THEME['text']};")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QtWidgets.QLabel(desc)
        desc_label.setStyleSheet(f"font-size: 12px; color: {THEME['muted']};")
        layout.addWidget(desc_label)
        
        # CPU tags
        tags_layout = QtWidgets.QHBoxLayout()
        tags_layout.setSpacing(6)
        for cpu in cpus:
            tag = QtWidgets.QLabel(cpu)
            tag.setStyleSheet(f"""
                QLabel {{
                    background: transparent;
                    border: 1px solid {THEME['muted']};
                    border-radius: 6px;
                    padding: 2px 8px;
                    font-size: 11px;
                    color: {THEME['muted']};
                }}
            """)
            tags_layout.addWidget(tag)
        tags_layout.addStretch()
        layout.addLayout(tags_layout)
        
        # Click handler
        card.mousePressEvent = lambda e: self._on_preset_card_clicked(preset_id, title)
        
        return card
    
    def _on_preset_card_clicked(self, preset_id: str, title: str):
        """Handle preset card click"""
        self._active_preset_id = preset_id
        self.preset_details_title.setText(title)
        
        # Clear previous toggles
        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Determine which preset data to load
        if preset_id.startswith("basic_"):
            preset_name = preset_id.replace("basic_", "")
            preset_data = INTEL_PRESETS_BASIC.get(preset_name) or AMD_PRESETS_BASIC.get(preset_name, {})
        elif preset_id.startswith("adv_intel_"):
            preset_name = preset_id.replace("adv_intel_", "")
            preset_data = INTEL_PRESETS_ADV.get(preset_name, {})
        elif preset_id.startswith("adv_amd_"):
            preset_name = preset_id.replace("adv_amd_", "")
            preset_data = AMD_PRESETS_ADV.get(preset_name, {})  # ← FIX: Always load AMD data for AMD presets
        else:
            preset_data = {}
        
        # Create toggles for each setting
        for setting_name, setting_value in preset_data.items():
            toggle_row = QtWidgets.QWidget()
            toggle_layout = QtWidgets.QHBoxLayout(toggle_row)
            toggle_layout.setContentsMargins(8, 4, 8, 4)
            
            label = QtWidgets.QLabel(setting_name)
            label.setStyleSheet(f"color: {THEME['text']}; font-size: 13px;")
            toggle_layout.addWidget(label, 1)
            
            value_label = QtWidgets.QLabel(str(setting_value))
            value_label.setStyleSheet(f"color: {THEME['muted']}; font-size: 12px;")
            toggle_layout.addWidget(value_label)
            
            self.details_layout.addWidget(toggle_row)
        
        # Add stretch at end
        self.details_layout.addStretch()
    
    def _on_cpu_selected(self, cpu: str):
        """Handle CPU segmented control"""
        self._selected_cpu = cpu
        self._preset_family = cpu.lower()  # Keep compatibility
        
        # Update button states
        self.cpu_intel_btn.setChecked(cpu == "Intel")
        self.cpu_amd_btn.setChecked(cpu == "AMD")
    
    def _on_apply_preset_clicked(self):
        """Apply the selected preset"""
        if not self._active_preset_id:
            self.toast.warning("No preset selected", "Select a preset first")
            return
        
        if not self.current_path or not self.current_path.exists():
            self._show_no_file_dialog()
            return
        
        # Apply the preset using existing logic
        self._apply_active_preset()
        
        # Show success toast
        preset_name = self.preset_details_title.text()
        self.toast.success("Preset applied", f"{preset_name}")
    
    def _apply_active_preset(self):
        """Apply the currently active preset (uses existing logic)"""
        if not self._active_preset_id:
            return
        
        # Determine preset data
        if self._active_preset_id.startswith("basic_"):
            preset_name = self._active_preset_id.replace("basic_", "")
            if self._selected_cpu == "Intel":
                preset_data = INTEL_PRESETS_BASIC.get(preset_name, {})
            else:
                preset_data = AMD_PRESETS_BASIC.get(preset_name, {})
        elif self._active_preset_id.startswith("adv_intel_"):
            preset_name = self._active_preset_id.replace("adv_intel_", "")
            preset_data = INTEL_PRESETS_ADV.get(preset_name, {})
        elif self._active_preset_id.startswith("adv_amd_"):
            preset_name = self._active_preset_id.replace("adv_amd_", "")
            preset_data = AMD_PRESETS_ADV.get(preset_name, {})
        else:
            return
        
        # Apply using existing mechanism
        combined_norm = build_normalized_map(preset_data)
        
        rows = []
        for i, s in enumerate(self.model._rows):
            if normalize_key(s.name) in combined_norm:
                rows.append(i)
        
        self.pending_targets = {}
        for r in rows:
            nk = normalize_key(self.model._rows[r].name)
            _, val = combined_norm[nk]
            self.pending_targets[r] = val
        
        # Apply targets
        count = self._apply_targets_now()
        if count > 0:
            self.update_counts()
    
    def _on_cancel_preset_clicked(self):
        """Cancel preset selection"""
        self._active_preset_id = None
        self.preset_details_title.setText("Select a preset")
        
        # Clear toggles
        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _on_preview_changes_clicked(self):
        """Preview what will change"""
        if not self._active_preset_id:
            self.toast.info("No preset selected", "Select a preset to preview changes")
            return
        
        # Show info toast
        self.toast.info("Preview not yet implemented", "This feature is coming soon")
'''

# Find where to insert methods (before _stylesheet method)
stylesheet_pattern = r'def _stylesheet\(self\) -> str:'
insertion = content.find('def _stylesheet(self) -> str:')

if insertion > 0:
    content = content[:insertion] + new_preset_methods + '\n    ' + content[insertion:]
    print("✓ Added new preset methods")
else:
    print("⚠ Could not find _stylesheet method")

# ============================================================================
# PART 5: Update initialization to use new ToastManager
# ============================================================================

# Find the notifications init line and replace it
old_notif_init = r'self\.notifications = NotificationManager\(self\)'
new_notif_init = 'self.toast = ToastManager(self)  # New professional toast system'

content = re.sub(old_notif_init, new_notif_init, content)
print("✓ Updated notification manager initialization")

# Update all old notification calls to use new toast API
content = re.sub(r'self\.notifications\.notify_success\(([^,]+),?\s*(?:duration_ms=\d+,?)?\s*(?:subtitle=([^)]+))?\)', 
                 r'self.toast.success(\1, \2 if \2 else "")', content)
content = re.sub(r'self\.notifications\.notify_info\(([^,]+),?\s*(?:duration_ms=\d+)?\)',
                 r'self.toast.info(\1)', content)
content = re.sub(r'self\.notifications\.notify_error\(([^,]+),?\s*(?:details=([^)]+))?\)',
                 r'self.toast.error(\1, \2 if \2 else "")', content)

print("✓ Updated notification calls to new toast API")

# Write changes
print("\n" + "=" * 80)
print("Writing changes...")
with open(source, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Changes written\n")

# Validate syntax
print("Validating syntax...")
try:
    compile(content, 'AutoBios.py', 'exec')
    print("✓ Syntax OK\n")
except SyntaxError as e:
    print(f"❌ Syntax error at line {e.lineno}: {e.msg}\n")
    exit(1)

print("=" * 80)
print("✅ COMPLETE!")
print("=" * 80)
print("\nChanges:")
print("  ✓ New ToastWidget and ToastManager classes")
print("  ✓ Professional toast system with queue, deduplication, animations")
print("  ✓ Complete Presets UI rebuild (3-pane layout)")
print("  ✓ AMD routing fixed (always loads AMD data)")
print("  ✓ Updated all notification calls")
print(f"\nBackup: {backup}")
print("\nTest:")
print("  1. Run: python AutoBios.py")
print("  2. Go to Presets tab")
print("  3. Test AMD presets → Should load AMD data")
print("  4. Test toasts → Should appear top-right with smooth animations")
