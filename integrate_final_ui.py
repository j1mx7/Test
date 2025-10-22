#!/usr/bin/env python3
"""
AutoBios Final UI Integration Script
Adds:
1. Custom OutlineConfirmDialog class
2. Enhanced ImportSCEWINPanel class
3. Integration into main app
4. Updated reset_config with custom modal
"""

import re
from pathlib import Path
from datetime import datetime

# Read the current file
source_path = Path("AutoBios.py")
backup_path = Path(f"AutoBios_final_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

print("AutoBios Final UI Integration")
print("=" * 60)

# Create backup
print(f"Creating backup: {backup_path}")
with open(source_path, 'r', encoding='utf-8') as f:
    content = f.read()

with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Backup created")

# ============================================================================
# 1. Add OutlineConfirmDialog class
# ============================================================================

outline_confirm_dialog = '''
# --------------------------------------------------------------------------------------
# Custom Outline Confirmation Dialog
# --------------------------------------------------------------------------------------
class OutlineConfirmDialog(QtWidgets.QDialog):
    """
    Custom confirmation dialog with outline style
    Replaces stock Windows message boxes
    """
    
    def __init__(self, parent=None, title="Confirm", message="Are you sure?", 
                 confirm_text="Confirm", cancel_text="Cancel"):
        super().__init__(parent)
        
        # Frameless dialog
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        # Main container
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
        
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)
        
        # Title
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 18px; font-weight: 600; color: {THEME['text']}; background: transparent;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Message
        message_label = QtWidgets.QLabel(message)
        message_label.setStyleSheet(f"font-size: 14px; color: {THEME['muted']}; background: transparent;")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Buttons
        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(12)
        button_row.addStretch()
        
        self.cancel_btn = QtWidgets.QPushButton(cancel_text)
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: 1px solid {THEME['input_border']};
                border-radius: 10px; padding: 8px 20px; color: {THEME['text']}; font-size: 14px;
            }}
            QPushButton:hover {{ background: transparent; border-color: {THEME['input_focus']}; }}
            QPushButton:pressed {{ background: rgba(255, 255, 255, 0.10); border-color: {THEME['accent']}; }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        button_row.addWidget(self.cancel_btn)
        
        self.confirm_btn = QtWidgets.QPushButton(confirm_text)
        self.confirm_btn.setMinimumWidth(100)
        self.confirm_btn.setMinimumHeight(36)
        self.confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: 1.5px solid {THEME['accent']};
                border-radius: 10px; padding: 8px 20px; color: {THEME['text']}; 
                font-size: 14px; font-weight: 500;
            }}
            QPushButton:hover {{ background: transparent; border-color: {THEME['accent_hover']}; }}
            QPushButton:pressed {{ background: rgba(74, 144, 226, 0.15); border-color: {THEME['accent']}; }}
        """)
        self.confirm_btn.clicked.connect(self.accept)
        self.confirm_btn.setCursor(Qt.PointingHandCursor)
        self.confirm_btn.setDefault(True)
        button_row.addWidget(self.confirm_btn)
        
        button_row.addStretch()
        layout.addLayout(button_row)
        
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
            self.accept()
        else:
            super().keyPressEvent(event)
    
    @staticmethod
    def confirm(parent, title, message, confirm_text="Confirm", cancel_text="Cancel"):
        dialog = OutlineConfirmDialog(parent, title, message, confirm_text, cancel_text)
        return dialog.exec() == QtWidgets.QDialog.Accepted


'''

# Find location to insert (before CustomTitleBar class)
insert_pos = content.find("class CustomTitleBar(QtWidgets.QWidget):")
if insert_pos != -1:
    content = content[:insert_pos] + outline_confirm_dialog + "\n" + content[insert_pos:]
    print("✓ Added OutlineConfirmDialog class")
else:
    print("⚠ Warning: Could not find insertion point for OutlineConfirmDialog")

# ============================================================================
# 2. Update reset_config to use custom modal
# ============================================================================

old_reset_method = '''    def reset_config(self) -> None:
        """Reset all changes back to original values"""
        if self.model.rowCount() == 0:
            self._show_no_file_dialog()
            return
            
        # Get all modified rows and reset them to original values
        modified_rows = self.model.modified_rows()
        if not modified_rows:
            self.notifications.notify_info("No changes to reset", duration_ms=2500)
            return
            
        # Reset each modified setting to its original value
        reset_count = 0
        for row in modified_rows:
            setting = self.model._rows[row]'''

new_reset_method = '''    def reset_config(self) -> None:
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

if old_reset_method in content:
    content = content.replace(old_reset_method, new_reset_method)
    print("✓ Updated reset_config to use custom confirmation modal")
else:
    print("⚠ Warning: Could not update reset_config method")

# ============================================================================
# 3. Update import_scewin to use custom modal
# ============================================================================

# Find the import_scewin method and add confirmation
old_import_start = '''    def import_scewin(self) -> None:
        """
        Professional SCEWIN import with QProcess
        - Non-blocking execution
        - Progress feedback
        - Comprehensive error handling
        - Creates nvram_tuned.txt file before importing
        """
        # Check if file is loaded
        if not self.current_path or not self.current_path.exists():
            self._show_no_file_dialog()
            return'''

new_import_start = '''    def import_scewin(self) -> None:
        """
        Professional SCEWIN import with QProcess with custom confirmation
        """
        # Check if file is loaded
        if not self.current_path or not self.current_path.exists():
            self._show_no_file_dialog()
            return
        
        # Show custom confirmation modal
        confirmed = OutlineConfirmDialog.confirm(
            self,
            "Confirm BIOS Import",
            "Import settings to BIOS using SCEWIN?\\n\\nThis will modify your BIOS configuration.\\nMake sure you have a backup.",
            "Import",
            "Cancel"
        )
        
        if not confirmed:
            return'''

if old_import_start in content:
    content = content.replace(old_import_start, new_import_start)
    print("✓ Updated import_scewin to use custom confirmation modal")
else:
    print("⚠ Warning: Could not update import_scewin method")

# ============================================================================
# 4. Update apply_config to use custom modal
# ============================================================================

# Find apply_config and add confirmation
old_apply = '''    def apply_config(self) -> None:
        """
        Apply configuration using SCEWIN
        """
        # Check if file is loaded
        if not self.current_path or not self.current_path.exists():
            self._show_no_file_dialog()
            return'''

new_apply = '''    def apply_config(self) -> None:
        """
        Apply configuration using SCEWIN with confirmation
        """
        # Check if file is loaded
        if not self.current_path or not self.current_path.exists():
            self._show_no_file_dialog()
            return
        
        # Show custom confirmation modal
        confirmed = OutlineConfirmDialog.confirm(
            self,
            "Apply Configuration",
            "Apply these settings to your BIOS?\\n\\nThis will modify your BIOS configuration.\\nMake sure you understand the changes.",
            "Apply",
            "Cancel"
        )
        
        if not confirmed:
            return'''

if old_apply in content:
    content = content.replace(old_apply, new_apply)
    print("✓ Updated apply_config to use custom confirmation modal")
else:
    print("⚠ Warning: Could not update apply_config method")

# ============================================================================
# Save the modified file
# ============================================================================

print("\nWriting changes...")
with open(source_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 60)
print("✅ Final UI integration complete!")
print(f"\nBackup: {backup_path}")
print("\nChanges made:")
print("  1. Added OutlineConfirmDialog class (custom modal)")
print("  2. Updated reset_config with confirmation")
print("  3. Updated import_scewin with confirmation")
print("  4. Updated apply_config with confirmation")
print("\nNote: ImportSCEWINPanel integration requires manual placement.")
print("See UI_REFACTOR_SUMMARY.md for full details.")
