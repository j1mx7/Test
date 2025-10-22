#!/usr/bin/env python3
"""
AutoBios UI Refactor Script
Applies all outline-style UI/UX changes to AutoBios.py
"""

import re
from pathlib import Path
from datetime import datetime

# Read the original file
source_path = Path("AutoBios.py")
backup_path = Path(f"AutoBios_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

print("AutoBios UI Refactor Script")
print("=" * 50)

# Create backup
print(f"Creating backup: {backup_path}")
with open(source_path, 'r', encoding='utf-8') as f:
    content = f.read()

with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Backup created successfully")

# Apply changes
changes_made = []

# Change 1: Window control buttons - Min/Max style
old_btn_style = '''        # Window control buttons - premium styling with 8px gaps
        btn_style_base = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 0;
                min-width: 40px;
                max-width: 40px;
                min-height: 32px;
                max-height: 32px;
                margin-right: 8px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.06);
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.10);
            }}
        """'''

new_btn_style = '''        # Window control buttons - outline style with 1px border, transparent fill
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

if old_btn_style in content:
    content = content.replace(old_btn_style, new_btn_style)
    changes_made.append("✓ Updated window control buttons (Min/Max) to outline style")
else:
    print("⚠ Warning: Could not find window control button style")

# Change 2: Close button style
old_close_style = '''        # Close button with premium SVG and red hover
        close_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 0;
                min-width: 40px;
                max-width: 40px;
                min-height: 32px;
                max-height: 32px;
                margin-right: 0px;
            }}
            QPushButton:hover {{
                background: rgba(255, 80, 80, 0.18);
            }}
            QPushButton:pressed {{
                background: rgba(255, 60, 60, 0.25);
            }}
        """'''

new_close_style = '''        # Close button with outline style and red hover
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

if old_close_style in content:
    content = content.replace(old_close_style, new_close_style)
    changes_made.append("✓ Updated close button to outline style")
else:
    print("⚠ Warning: Could not find close button style")

# Change 3: Top tabs stylesheet
old_tabs = '''            /* Top tabs with hover */
            QTabBar#topTabs {{ qproperty-drawBase:0; background:transparent; }}
            QTabBar#topTabs::tab {{ background:{t['card']}; color:{t['muted']}; padding:14px 24px; margin:0 8px;
                                     border:1px solid {t['border']}; border-radius:12px; font-weight:500; font-size:14px; }}
            QTabBar#topTabs::tab:hover {{ background:{t['card_hover']}; border-color:{t['input_border']}; }}
            QTabBar#topTabs::tab:selected {{ background:{t['tab_selected']}; color:{t['text']}; border-color:{t['input_focus']};d}}'''

new_tabs = '''            /* Top tabs - outline style with transparent fill and thin underline indicator */
            QTabBar#topTabs {{ qproperty-drawBase:0; background:transparent; }}
            QTabBar#topTabs::tab {{ 
                background: transparent; 
                color: {t['muted']}; 
                padding: 14px 24px; 
                margin: 0 8px;
                border: 1px solid {t['input_border']}; 
                border-radius: 12px; 
                font-weight: 500; 
                font-size: 14px; 
            }}
            QTabBar#topTabs::tab:hover {{ 
                background: transparent; 
                border-color: {t['input_focus']}; 
            }}
            QTabBar#topTabs::tab:selected {{ 
                background: transparent; 
                color: {t['text']}; 
                border: 1px solid {t['input_focus']};
                border-bottom: 2px solid {t['accent']};
            }}'''

if old_tabs in content:
    content = content.replace(old_tabs, new_tabs)
    changes_made.append("✓ Updated top tabs to outline style with underline")
else:
    print("⚠ Warning: Could not find top tabs stylesheet")

# Change 4: Remove Clear List button
# Remove button creation
content = re.sub(
    r'\s*# Clear list \(first\)\s*\n\s*self\.btn_clear = QtWidgets\.QPushButton\("Clear list"\)\s*\n\s*self\.btn_clear\.setMinimumHeight\(40\)\s*\n',
    '\n',
    content
)

# Remove signal connection
content = re.sub(
    r'\s*self\.btn_clear\.clicked\.connect\(self\.clear_preset_list\)\s*\n',
    '',
    content
)

# Remove from layout
content = re.sub(
    r'\s*rw\.addWidget\(self\.btn_clear\)\s*\n',
    '',
    content
)

changes_made.append("✓ Removed Clear List button from Presets tab")

# Change 5: Global button styles
old_button_style = '''            /* Buttons with smooth effects */
            QPushButton {{ background:{t['tab_selected']}; border:1px solid {t['input_border']}; border-radius:16px;
                           padding:12px 24px; color:{t['text']}; font-weight:500; }}
            QPushButton:hover {{ background:{t['card_hover']}; border-color:{t['input_focus']}; }}
            QPushButton:pressed {{ background:{t['card']}; border-color:{t['accent']}; }}
            QPushButton:disabled {{ background:{t['card']}; color:{t['muted']}; border-color:{t['border']}; }}'''

new_button_style = '''            /* Buttons - outline style with transparent fill */
            QPushButton {{ 
                background: transparent; 
                border: 1px solid {t['input_border']}; 
                border-radius: 12px;
                padding: 12px 24px; 
                color: {t['text']}; 
                font-weight: 500; 
            }}
            QPushButton:hover {{ 
                background: transparent; 
                border-color: {t['input_focus']}; 
            }}
            QPushButton:pressed {{ 
                background: rgba(255, 255, 255, 0.10); 
                border-color: {t['accent']}; 
            }}
            QPushButton:disabled {{ 
                background: transparent; 
                color: {t['muted']}; 
                border-color: {t['border']}; 
            }}'''

if old_button_style in content:
    content = content.replace(old_button_style, new_button_style)
    changes_made.append("✓ Updated global button styles to outline pattern")
else:
    print("⚠ Warning: Could not find global button styles")

# Change 6: Input/Search field styles
old_input_style = '''            /* Search input with visible color block */
            QLineEdit, QLineEdit#searchInput {{
                background: {t['card']};
                border: 2px solid {t['input_border']};
                border-radius: 12px;
                padding: 12px 18px;
                color: {t['text']};
                font-size: 14px;
                selection-background-color: {t['selection']};
            }}
            QLineEdit:hover, QLineEdit#searchInput:hover {{
                border-color: {t['input_focus']};
                background: {t['card_hover']};
            }}
            QLineEdit:focus, QLineEdit#searchInput:focus {{
                border: 2px solid {t['input_focus']};
                background: {t['card_hover']};
            }}'''

new_input_style = '''            /* Search input - outline style with transparent fill */
            QLineEdit, QLineEdit#searchInput {{
                background: transparent;
                border: 1px solid {t['input_border']};
                border-radius: 12px;
                padding: 12px 18px;
                color: {t['text']};
                font-size: 14px;
                selection-background-color: {t['selection']};
            }}
            QLineEdit:hover, QLineEdit#searchInput:hover {{
                border-color: {t['input_focus']};
                background: transparent;
            }}
            QLineEdit:focus, QLineEdit#searchInput:focus {{
                border: 1px solid {t['input_focus']};
                background: transparent;
                outline: 1px solid {t['input_focus']};
                outline-offset: -2px;
            }}'''

if old_input_style in content:
    content = content.replace(old_input_style, new_input_style)
    changes_made.append("✓ Updated input/search fields to outline style")
else:
    print("⚠ Warning: Could not find input styles")

# Write the modified content
print(f"\nApplying {len(changes_made)} changes...")
with open(source_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Print summary
print("\n" + "=" * 50)
print("Changes Applied:")
for change in changes_made:
    print(f"  {change}")

print(f"\n✅ All changes applied successfully!")
print(f"Original file backed up to: {backup_path}")
print(f"\nNote: The ImportSCEWINPanel class and integration must be added manually.")
print(f"See UI_REFACTOR_SUMMARY.md for full implementation details.")
