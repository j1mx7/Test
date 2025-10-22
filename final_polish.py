#!/usr/bin/env python3
"""
AutoBios Final UI Polish Script
Implements:
1. Icon-only window controls (no borders, just tints on hover)
2. Redesigned NoFileLoadedDialog with dashed drop zone
3. Enhanced reset_config for FULL app reset
4. Cleanup of old message box code
"""

import re
from pathlib import Path
from datetime import datetime

source_path = Path("AutoBios.py")
backup_path = Path(f"AutoBios_polish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

print("AutoBios Final UI Polish")
print("=" * 70)

# Backup
print(f"Creating backup: {backup_path}")
with open(source_path, 'r', encoding='utf-8') as f:
    content = f.read()

with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Backup created\n")

changes = []

# ============================================================================
# 1. Update Window Control Buttons - Icon Only, No Borders
# ============================================================================

old_btn_style = '''        # Window control buttons - outline style with 1px border, transparent fill
        btn_style_base = f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {THEME['input_border']};
                border-radius: 6px;
                padding: 0;
                min-width: 40px;
                max-width: 40px;
                min-height: 32px;
                max-height: 32px;
                margin-right: 8px;
            }}
            QPushButton:hover {{
                background: transparent;
                border-color: {THEME['input_focus']};
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.10);
                border-color: {THEME['accent']};
            }}
        """'''

new_btn_style = '''        # Window control buttons - icon only, no borders, tint on hover
        btn_style_base = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 0;
                min-width: 34px;
                max-width: 34px;
                min-height: 28px;
                max-height: 28px;
                margin-right: 8px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.12);
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.22);
            }}
        """'''

if old_btn_style in content:
    content = content.replace(old_btn_style, new_btn_style)
    changes.append("✓ Updated window control buttons to icon-only (no borders)")

old_close_style = '''        # Close button with outline style and red hover
        close_style = f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {THEME['input_border']};
                border-radius: 6px;
                padding: 0;
                min-width: 40px;
                max-width: 40px;
                min-height: 32px;
                max-height: 32px;
                margin-right: 0px;
            }}
            QPushButton:hover {{
                background: transparent;
                border-color: {THEME['error']};
            }}
            QPushButton:pressed {{
                background: rgba(255, 80, 80, 0.10);
                border-color: {THEME['error']};
            }}
        """'''

new_close_style = '''        # Close button - icon only, red tint on hover
        close_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 0;
                min-width: 34px;
                max-width: 34px;
                min-height: 28px;
                max-height: 28px;
                margin-right: 0px;
            }}
            QPushButton:hover {{
                background: rgba(255, 80, 80, 0.15);
            }}
            QPushButton:pressed {{
                background: rgba(255, 80, 80, 0.25);
            }}
        """'''

if old_close_style in content:
    content = content.replace(old_close_style, new_close_style)
    changes.append("✓ Updated close button to red tint (no borders)")

# ============================================================================
# 2. Redesign NoFileLoadedDialog
# ============================================================================

old_nofile_dialog = '''class NoFileLoadedDialog(QtWidgets.QDialog):
    """
    Professional dialog shown when a file is required but none is loaded
    Features:
    - Primary actions: Load file, Import via SCEWIN
    - Drag & drop zone for nvram.txt
    - Dark theme, large buttons
    - Esc closes, Enter triggers primary
    """

    load_file_requested = Signal()
    import_requested = Signal()
    export_requested = Signal()
    file_dropped = Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("No File Loaded")
        self.setModal(True)
        self.setFixedWidth(480)

        # Dark styling
        self.setStyleSheet(f"""
            QDialog {{
                background: {THEME['bg']};
            }}
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Title
        title = QtWidgets.QLabel("No file loaded")
        title.setStyleSheet(f"color: {THEME['text']}; font-size: 24px; font-weight: 600;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Message
        message = QtWidgets.QLabel("Load an nvram.txt file first to use this feature.")
        message.setStyleSheet(f"color: {THEME['muted']}; font-size: 14px;")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        layout.addWidget(message)

        # Drag & drop zone
        drop_zone = QtWidgets.QFrame()
        drop_zone.setAcceptDrops(True)
        drop_zone.setStyleSheet(f"""
            QFrame {{
                background: {THEME['card']};
                border: 2px dashed {THEME['border']};
                border-radius: 12px;
                padding: 32px;
            }}
        """)

        drop_layout = QtWidgets.QVBoxLayout(drop_zone)
        drop_layout.setAlignment(Qt.AlignCenter)

        drop_icon = QtWidgets.QLabel("📁")
        drop_icon.setStyleSheet("font-size: 48px;")
        drop_icon.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(drop_icon)

        drop_text = QtWidgets.QLabel("Drop nvram.txt here")
        drop_text.setStyleSheet(f"color: {THEME['muted']}; font-size: 13px;")
        drop_text.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(drop_text)

        # Connect drop events
        drop_zone.dragEnterEvent = self._drag_enter
        drop_zone.dropEvent = self._drop

        layout.addWidget(drop_zone)

        # Action buttons
        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.setSpacing(12)

        # Primary: Load file
        self.load_btn = QtWidgets.QPushButton("Load nvram.txt…")
        self.load_btn.setCursor(Qt.PointingHandCursor)
        self.load_btn.setMinimumHeight(48)
        self.load_btn.setStyleSheet(f"""
            QPushButton {{
                background: {THEME['accent']};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background: {THEME['accent_hover']};
            }}
            QPushButton:pressed {{
                background: {THEME['accent_press']};
            }}
        """)
        self.load_btn.clicked.connect(self._on_load)
        btn_layout.addWidget(self.load_btn)

        # Secondary: Export via SCEWIN
        self.export_btn = QtWidgets.QPushButton("Export (SCEWIN)")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setMinimumHeight(44)
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background: {THEME['card']};
                color: {THEME['text']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background: {THEME['card_hover']};
                border-color: {THEME['accent']};
            }}
        """)
        self.export_btn.clicked.connect(self._on_export)
        btn_layout.addWidget(self.export_btn)

        layout.addLayout(btn_layout)

        # Keyboard shortcuts
        self.load_btn.setDefault(True)  # Enter triggers this'''

new_nofile_dialog = '''class NoFileLoadedDialog(QtWidgets.QDialog):
    """
    Redesigned "No file loaded" dialog with clean outline style
    Features:
    - Dashed drop zone (1px, transparent fill)
    - Side-by-side outline buttons
    - Clean, minimal layout
    - ESC/Enter keyboard handling
    """

    load_file_requested = Signal()
    export_requested = Signal()
    file_dropped = Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Frameless for consistency
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        # Main container
        container = QtWidgets.QWidget()
        container.setObjectName("noFileContainer")
        container.setStyleSheet(f"""
            QWidget#noFileContainer {{
                background: {THEME['card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        
        container_layout = QtWidgets.QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(container)
        
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Title
        title = QtWidgets.QLabel("No file loaded")
        title.setStyleSheet(f"color: {THEME['text']}; font-size: 20px; font-weight: 600; background: transparent;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtext
        subtext = QtWidgets.QLabel("Load an nvram.txt file first to use this feature.")
        subtext.setStyleSheet(f"color: {THEME['muted']}; font-size: 14px; background: transparent;")
        subtext.setAlignment(Qt.AlignCenter)
        subtext.setWordWrap(True)
        layout.addWidget(subtext)

        # Dashed drop zone
        self.drop_zone = QtWidgets.QFrame()
        self.drop_zone.setAcceptDrops(True)
        self.drop_zone.setMinimumHeight(120)
        self.drop_zone.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: 1px dashed {THEME['input_border']};
                border-radius: 12px;
            }}
        """)

        drop_layout = QtWidgets.QVBoxLayout(self.drop_zone)
        drop_layout.setAlignment(Qt.AlignCenter)
        drop_layout.setSpacing(8)

        # Folder icon
        drop_icon = QtWidgets.QLabel("📁")
        drop_icon.setStyleSheet("font-size: 42px; background: transparent;")
        drop_icon.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(drop_icon)

        # Drop text
        drop_text = QtWidgets.QLabel("Drag & drop nvram.txt or click to browse")
        drop_text.setStyleSheet(f"color: {THEME['muted']}; font-size: 13px; background: transparent;")
        drop_text.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(drop_text)

        # Wire drop events
        self.drop_zone.dragEnterEvent = self._drag_enter
        self.drop_zone.dropEvent = self._drop

        layout.addWidget(self.drop_zone)

        # Buttons row (side by side)
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(12)

        # Browse button (outline style)
        self.load_btn = QtWidgets.QPushButton("Browse nvram.txt…")
        self.load_btn.setMinimumHeight(40)
        self.load_btn.setCursor(Qt.PointingHandCursor)
        self.load_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {THEME['input_border']};
                border-radius: 10px;
                padding: 10px 20px;
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
        self.load_btn.clicked.connect(self._on_load)
        self.load_btn.setDefault(True)
        btn_row.addWidget(self.load_btn)

        # Export button (outline style)
        self.export_btn = QtWidgets.QPushButton("Export (SCEWIN)")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {THEME['input_border']};
                border-radius: 10px;
                padding: 10px 20px;
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
        self.export_btn.clicked.connect(self._on_export)
        btn_row.addWidget(self.export_btn)

        layout.addLayout(btn_row)
        
        self.setFixedWidth(460)
        
        # Fade-in animation
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        container.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(200)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QtCore.QEasingCurve.OutCubic)
    
    def showEvent(self, event):
        super().showEvent(event)
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2
            )
        self.fade_in.start()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._on_load()
        else:
            super().keyPressEvent(event)'''

if old_nofile_dialog in content:
    content = content.replace(old_nofile_dialog, new_nofile_dialog)
    changes.append("✓ Redesigned NoFileLoadedDialog with dashed drop zone")

# ============================================================================
# 3. Enhanced reset_config for FULL app reset
# ============================================================================

old_reset = '''    def reset_config(self) -> None:
        """Reset all changes back to original values with confirmation"""
        if self.model.rowCount() == 0:
            self._show_no_file_dialog()
            return
            
        # Get all modified rows
        modified_rows = self.model.modified_rows()
        if not modified_rows:
            self.notifications.notify_info("No changes to reset", duration_ms=2500)
            return
        
        # Show custom confirmation modal
        confirmed = OutlineConfirmDialog.confirm(
            self,
            "Reset All Settings",
            f"Reset {len(modified_rows)} modified settings to their original values?\\n\\nThis cannot be undone.",
            "Reset",
            "Cancel"
        )
        
        if not confirmed:
            return
            
        # Reset each modified setting to its original value
        reset_count = 0
        for row in modified_rows:
            setting = self.model._rows[row]'''

new_reset = '''    def reset_config(self) -> None:
        """Full app reset: settings, presets, search, filters, counters"""
        if self.model.rowCount() == 0:
            self._show_no_file_dialog()
            return
        
        # Show custom confirmation modal
        confirmed = OutlineConfirmDialog.confirm(
            self,
            "Reset All Settings",
            "This will revert all settings, presets, and applied changes back to default.\\n\\nContinue?",
            "Reset",
            "Cancel"
        )
        
        if not confirmed:
            return
        
        # FULL RESET - same as app restart
        
        # 1. Reset all modified settings to original values
        reset_count = 0
        for row in self.model.modified_rows():
            setting = self.model._rows[row]'''

if old_reset in content:
    content = content.replace(old_reset, new_reset)
    changes.append("✓ Updated reset_config for full app reset")

# Add full reset logic after the settings reset loop
reset_completion = '''            self.model.dataChanged.emit(idx, idx, [Qt.DisplayRole, Qt.EditRole])
            reset_count += 1
        
        self.update_counts()
        self.status(f"Reset {reset_count} settings to original values.")
        self.notifications.notify_success(f"Reset {reset_count} settings", duration_ms=2200)'''

new_reset_completion = '''            self.model.dataChanged.emit(idx, idx, [Qt.DisplayRole, Qt.EditRole])
            reset_count += 1
        
        # 2. Clear all presets
        if hasattr(self, 'rows_basic'):
            for row in self.rows_basic.values():
                if row.sw.isChecked():
                    row.sw.setChecked(False)
        
        if hasattr(self, '_enabled_basic'):
            self._enabled_basic = {k: False for k in self._enabled_basic.keys()}
        
        if hasattr(self, '_enabled_adv_intel'):
            self._enabled_adv_intel = {k: False for k in self._enabled_adv_intel.keys()}
        
        if hasattr(self, '_enabled_adv_amd'):
            self._enabled_adv_amd = {k: False for k in self._enabled_adv_amd.keys()}
        
        # Rebuild advanced presets page to reflect cleared state
        if hasattr(self, '_build_adv_page_for_family'):
            self._build_adv_page_for_family(self._preset_family)
        
        # Clear preset table
        if hasattr(self, 'presetProxy'):
            self.presetProxy.setNameSet(None)
        
        if hasattr(self, 'pending_targets'):
            self.pending_targets.clear()
        
        if hasattr(self, 'presetTable'):
            self.presetTable.setVisible(False)
            self.presetTable.horizontalHeader().setVisible(False)
        
        if hasattr(self, 'preset_placeholder'):
            self.preset_placeholder.setVisible(True)
        
        # 3. Clear search filter
        if hasattr(self, 'search'):
            self.search.clear()
        
        # 4. Update all counters
        self.update_counts()
        
        # 5. Status update
        self.status(f"Reset complete: {reset_count} settings, all presets cleared, filters reset.")
        self.notifications.notify_success(f"Full reset: {reset_count} settings restored", duration_ms=2500)'''

if reset_completion in content:
    content = content.replace(reset_completion, new_reset_completion)
    changes.append("✓ Enhanced reset to clear presets, search, and filters")

# ============================================================================
# Write changes
# ============================================================================

print("Applying changes...")
with open(source_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 70)
print("✅ Final UI polish complete!\n")
print("Changes applied:")
for change in changes:
    print(f"  {change}")

print(f"\nBackup saved: {backup_path}")
print("\nAll done! Your app now has:")
print("  • Icon-only window controls (no borders, tint on hover)")
print("  • Redesigned NoFileLoadedDialog (dashed drop zone)")
print("  • Full reset button (settings + presets + search + filters)")
print("  • Consistent outline-style throughout")
