# AutoBios - Presets UI Redesign Complete ✅

## Overview
Complete redesign of the Presets UI with clean, premium styling and bulletproof AMD/Intel separation.

---

## 🎨 Visual Improvements

### Segmented Control (Replaced Toggle)
**Before**: Ugly on/off toggle with separate label  
**After**: Clean segmented control `[ AMD ] [ Intel ]`

- **Outline style**: 1px border, 12px radius, transparent fill
- **Active state**: 2px bottom underline (accent color)
- **Keyboard nav**: Left/Right arrows to switch, Enter to confirm
- **Position**: Top-right of "Preset Configuration" card header

### Preset Rows
- **Hairline dividers**: 1px borders between each toggle
- **Improved spacing**: 12px horizontal padding, 10px vertical
- **Better typography**: 13px labels, 500 font weight
- **Clean switches**: Smaller toggle (48x26px) with outline style

---

## 🔧 Technical Changes

### 1. New SegmentedControl Widget
```python
class SegmentedControl(QtWidgets.QWidget):
    currentChanged = Signal(str)  # Emits "AMD" or "Intel"
```

**Features:**
- Options: ["AMD", "Intel"]
- Default: Intel (matches existing behavior)
- Keyboard accessible
- Outline-only styling per visual rules

### 2. Vendor-Specific Preset Names

**AMD Advanced** (25 options):
- CPPC & Preferred Cores *(new AMD-specific)*
- PBO & Scalar Limits *(new AMD-specific)*
- Global C-State Control
- Memory PowerDown Modes *(new AMD-specific)*
- SMU Debug & Telemetry *(new AMD-specific)*
- SMT Control
- Clock Gating Control
- PCIe ASPM & ClkReq
- Sleep & Standby States
- Security & fTPM
- Virtualization (SVM)
- ...and more

**Intel Advanced** (25 options):
- Speed Shift (HWP) *(new Intel-specific)*
- Turbo Boost Power Limits *(new Intel-specific)*
- Package C-States
- ICC Max Current *(new Intel-specific)*
- DPTF Thermal Limits *(new Intel-specific)*
- Hyper-Threading Control
- Clock Gating Control
- PCIe ASPM & ClkReq
- Sleep & Standby States
- Security & TPM
- Virtualization (VT-x/VT-d)
- ...and more

### 3. Bulletproof Routing

**Guard Assertion** (existing, verified):
```python
if self._preset_family == "amd":
    assert adv_map is AMD_PRESETS_ADV, "AMD family must use AMD_PRESETS_ADV"
else:
    assert adv_map is INTEL_PRESETS_ADV, "Intel family must use INTEL_PRESETS_ADV"
```

**Updated Handler**:
```python
def _on_family_switch(self, cpu: str) -> None:
    """Handle CPU family change from segmented control (AMD/Intel)"""
    fam = cpu.lower()  # "AMD" or "Intel" → "amd" or "intel"
    self._preset_family = fam
    self._build_adv_page_for_family(fam)
    self._rebuild_preset_view_and_targets()
```

**Guarantees:**
- Segmented control emits "AMD" or "Intel" (string)
- Handler converts to lowercase for internal use
- `_preset_family` drives all preset data lookups
- Assertion guards prevent data mixing
- AMD can NEVER load Intel presets

---

## 📋 Visual Rules Applied

✅ **Controls**: Outline-only (1px), 12px radius, transparent fill  
✅ **Hover**: Slightly brighter stroke  
✅ **Press**: Short 10% fill  
✅ **Focus**: Subtle inner ring  
✅ **Typography**: 16px section titles, 13px labels, 500-600 weights  
✅ **Spacing**: 12px grid, 10px row padding  
✅ **Dividers**: Hairline 1px between items  
✅ **No fills**: No chips, bars, or colored backgrounds  

---

## 🧪 Testing

Run:
```bash
python AutoBios.py
```

**Test Steps:**
1. Load `nvram.txt` file
2. Go to **Presets** tab
3. Verify segmented control shows `[ AMD ] [ Intel ]` (Intel selected)
4. Click **AMD** → Advanced page shows AMD-specific presets
5. Click **Intel** → Advanced page shows Intel-specific presets
6. Toggle some presets → Verify table updates
7. Click "Apply Config" → Verify changes apply correctly

**Expected:**
- Clean outline styling throughout
- Hairline dividers between toggle rows
- AMD Advanced: Shows "CPPC & Preferred Cores", "PBO & Scalar", etc.
- Intel Advanced: Shows "Speed Shift (HWP)", "Turbo Boost Power", etc.
- No visual regressions
- No assertion errors

---

## 📦 Files Changed

**Modified:**
- `AutoBios.py` (5,543 lines)

**Added:**
- `SegmentedControl` widget class
- Updated AMD/Intel Advanced preset names
- Hairline dividers in `PresetRow`

**Removed:**
- `ToggleSwitch` usage for CPU family (kept for preset toggles)
- `familyLabel` widget
- Old generic preset names

**Backup:**
- `AutoBios_redesign_backup_20251022_191325.py`

---

## ✨ Summary

This redesign delivers:
- **Premium UI**: Clean, modern, outline-style controls
- **Vendor Clarity**: Distinct AMD vs Intel Advanced options
- **Bulletproof Logic**: Guards prevent AMD/Intel data mixing
- **Better UX**: Segmented control is clearer than toggle
- **Visual Consistency**: Follows strict design rules

Status: **✅ Complete and Ready**

---

*Redesign completed: 2025-10-22*
