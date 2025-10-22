#!/usr/bin/env python3
"""Fix Qt errors in AutoBios - Simple string replacement approach"""

from pathlib import Path
from datetime import datetime

source = Path("AutoBios.py")
backup = Path(f"AutoBios_qt_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

print("AutoBios - Qt Error Fixes")
print("=" * 70)

# Read
with open(source, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open(backup, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✓ Backup: {backup}")

changes = []

# FIX 1: Remove outline (Qt doesn't support it well)
old1 = '''            QLineEdit:focus, QLineEdit#searchInput:focus {{
                border: 1px solid {t['input_focus']};
                background: transparent;
                outline: 1px solid {t['input_focus']};
                outline-offset: -2px;
            }}'''

new1 = '''            QLineEdit:focus, QLineEdit#searchInput:focus {{
                border: 2px solid {t['input_focus']};
                background: transparent;
            }}'''

if old1 in content:
    content = content.replace(old1, new1)
    changes.append("Fixed outline in QLineEdit:focus")

# FIX 2: ToastNotification - add opacity effect in __init__
old2 = '''        self.setAutoFillBackground(False)

        # Unified rounded toast styling - matches all toasts
        self.setStyleSheet(f"""'''

new2 = '''        self.setAutoFillBackground(False)
        
        # Setup opacity effect for fade animations
        self._opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(1.0)

        # Unified rounded toast styling - matches all toasts
        self.setStyleSheet(f"""'''

if old2 in content:
    content = content.replace(old2, new2)
    changes.append("Added opacity effect to ToastNotification")

# FIX 3: Change fade_anim to animate opacity_effect
old3 = '''        self.fade_anim = QtCore.QPropertyAnimation(self, b"windowOpacity")'''
new3 = '''        self.fade_anim = QtCore.QPropertyAnimation(self._opacity_effect, b"opacity")'''

if old3 in content:
    content = content.replace(old3, new3)
    changes.append("Fixed fade_anim to use opacity effect")

# FIX 4: Fix hide_toast to use opacity effect
old4 = '''        # Fade out using opacity effect
        self.fade_anim.setStartValue(self._opacity_effect.opacity())
        self.fade_anim.setEndValue(0.0)'''

# Already fixed if above worked

# FIX 5: Fix show_toast
old5 = '''        self.show()
        self._opacity_effect.setOpacity(0.0)  # Start fully transparent

        # Fade in
        self.fade_anim.setStartValue(0.0)'''

if old5 not in content:
    # Need to add it
    old5_orig = '''        self.show()

        # Fade in
        self.fade_anim.setStartValue(0.0)'''
    
    new5 = '''        self.show()
        self._opacity_effect.setOpacity(0.0)  # Start fully transparent

        # Fade in
        self.fade_anim.setStartValue(0.0)'''
    
    if old5_orig in content:
        content = content.replace(old5_orig, new5)
        changes.append("Fixed show_toast opacity init")

# FIX 6: Fix hide_toast opacity read
old6 = '''        # Fade out
        self.fade_anim.setStartValue(self.windowOpacity())
        self.fade_anim.setEndValue(0.0)'''

new6 = '''        # Fade out
        self.fade_anim.setStartValue(self._opacity_effect.opacity())
        self.fade_anim.setEndValue(0.0)'''

if old6 in content:
    content = content.replace(old6, new6)
    changes.append("Fixed hide_toast to read opacity from effect")

# Write
with open(source, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Applied {len(changes)} fixes")
for c in changes:
    print(f"  - {c}")

# Validate
try:
    compile(content, 'AutoBios.py', 'exec')
    print("\n✓ Syntax OK")
except SyntaxError as e:
    print(f"\n❌ Syntax error at line {e.lineno}: {e.msg}")
    exit(1)

print("\n✅ Qt error fixes complete!")
print("\nThese fixes address:")
print("  • QPropertyAnimation on non-existent windowOpacity")
print("  • CSS outline property (not well supported)")
print("\nNext: Run app to verify no Qt warnings")
