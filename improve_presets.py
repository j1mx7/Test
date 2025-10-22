#!/usr/bin/env python3
"""
Improve the original 2-pane preset layout without changing the structure.
Fix AMD routing and make it cleaner.
"""
from pathlib import Path
from datetime import datetime

source = Path("AutoBios.py")
backup = Path(f"AutoBios_improved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(source, 'r') as f:
    content = f.read()

with open(backup, 'w') as f:
    f.write(content)

print(f"Backup: {backup}")

# Find and verify _current_adv_map method
if "def _current_adv_map(self)" in content:
    print("✓ Found _current_adv_map")
else:
    print("❌ _current_adv_map not found")

# Find the AMD routing logic
if 'self._preset_family == "amd"' in content:
    print("✓ Found AMD family check")
else:
    print("❌ AMD family check not found")

