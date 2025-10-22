# AutoBios - Complete Presets UI Redesign Specification

## ✅ Current Status

**Completed**:
- ✅ Qt error fixes (QPropertyAnimation, CSS outline)
- ✅ Professional Toast System (fully functional)
- ✅ Toast Manager initialized and ready
- ✅ AMD routing verified correct in code

**Pending**:
- 🚧 Presets UI 3-pane layout (designed, not implemented)

---

## 🎯 Design Goals

Transform the current 2-pane Presets UI into a modern, intuitive 3-pane layout:

### Current (2-Pane):
```
┌─────────────────────────────────────────┐
│ Left: Preset Table (filtered settings) │
├─────────────────────────────────────────┤
│ Right: Controls (Family switch, toggles)│
└─────────────────────────────────────────┘
```

### Target (3-Pane):
```
┌──────────┬───────────────┬─────────────────┐
│ Families │ Preset Cards  │ Details Panel   │
│ (~220px) │ (flexible)    │ (flexible)      │
├──────────┼───────────────┼─────────────────┤
│          │               │                 │
│ Basic    │ ┌──────────┐  │ Title           │
│ Advanced │ │AMD Adv   │  │ [Intel][AMD]    │
│ OEM/EC   │ │Tuning    │  │                 │
│ Perf     │ │[AMD]     │  │ Toggles:        │
│          │ │[Preview] │  │ ☐ Setting 1     │
│          │ └──────────┘  │ ☐ Setting 2     │
│          │               │                 │
│          │ ┌──────────┐  │ [Preview][Apply]│
│          │ │Intel Adv │  │                 │
│          │ │...       │  │                 │
└──────────┴───────────────┴─────────────────┘
```

---

## 📐 Layout Specification

### Main Container
```python
presets_tab = QtWidgets.QWidget()
main_layout = QtWidgets.QHBoxLayout(presets_tab)
main_layout.setContentsMargins(16, 16, 16, 16)
main_layout.setSpacing(16)
```

### Left Panel: Family Sidebar (~220px)

**Components**:
1. Title: "Preset Families" (16px, 600 weight)
2. QListWidget with families

**Families**:
- Basic
- Advanced
- OEM / EC
- Performance
- Undervolt (conditional)

**Styling**:
```css
QListWidget {
    background: transparent;
    border: none;
}
QListWidget::item {
    border-bottom: 2px solid transparent;
    padding: 12px 8px;
    color: muted;
}
QListWidget::item:selected {
    background: transparent;
    border-bottom: 2px solid accent;  /* Underline only */
}
```

**Data Structure**:
```python
families = [
    ("basic", "Basic"),
    ("advanced", "Advanced"),
    ("oem", "OEM / EC"),
    ("performance", "Performance"),
]
```

### Center Panel: Preset Cards

**Components**:
1. Title label (dynamic based on family)
2. QScrollArea with card container
3. Cards generated dynamically

**Card Structure**:
```
┌─────────────────────────────┐
│ AMD Advanced Tuning    ← Title (14px, 600)
│ Advanced performance   ← Description (12px)
│ [AMD] [Intel]         ← CPU Tags (chips)
│ [Preview]             ← Action button
└─────────────────────────────┘
```

**Card Styling**:
```css
QFrame#presetCard {
    background: transparent;
    border: 1px solid input_border;
    border-radius: 12px;
    padding: 16px;
}
QFrame#presetCard:hover {
    border-color: input_focus;
}
```

**Card Creation Logic**:
```python
def _create_preset_card(preset_id: str, title: str, desc: str, cpus: list[str]):
    card = QtWidgets.QFrame()
    card.setObjectName("presetCard")
    card.setCursor(Qt.PointingHandCursor)
    # ... styling ...
    
    layout = QtWidgets.QVBoxLayout(card)
    
    # Title
    title_label = QtWidgets.QLabel(title)
    # ... style ...
    
    # Description
    desc_label = QtWidgets.QLabel(desc)
    # ... style ...
    
    # CPU tags
    for cpu in cpus:
        tag = QtWidgets.QLabel(cpu)
        # Outline chip style
    
    # Click handler
    card.mousePressEvent = lambda e: self._on_card_clicked(preset_id)
    
    return card
```

### Right Panel: Details Panel

**Components**:
1. Header row:
   - Title (dynamic)
   - CPU segmented control

2. Scroll area with toggles

3. Footer:
   - Left: "Preview Changes" (outline)
   - Right: "Cancel" + "Apply Preset" (outline)

**Segmented Control**:
```python
cpu_container = QtWidgets.QWidget()
cpu_layout = QtWidgets.QHBoxLayout()
cpu_layout.setSpacing(0)

intel_btn = QtWidgets.QPushButton("Intel")
amd_btn = QtWidgets.QPushButton("AMD")

# Both checkable, exclusive (button group behavior)
# Style: transparent, 1px border, left rounded/right rounded
# Checked: accent background, white text
```

**Styling**:
```css
QPushButton {
    background: transparent;
    border: 1px solid input_border;
    padding: 6px 16px;
    color: muted;
}
QPushButton:checked {
    background: accent;
    color: white;
    border-color: accent;
}
/* Left button: border-radius: 12px 0 0 12px */
/* Right button: border-radius: 0 12px 12px 0 */
```

**Toggle List**:
- Each setting from the preset shows as a row
- Setting name on left, current value on right
- Could use PresetRow widgets (from existing code) or simpler labels
- Grouped by category (EC, Audio, RGB, etc.)

---

## 🔄 Interaction Flow

### 1. Family Selection
```
User clicks "Advanced" in left sidebar
  ↓
_on_family_selected(row)
  ↓
Update center title: "Advanced"
  ↓
Clear previous cards
  ↓
Generate cards for Advanced family:
  - Intel Advanced presets (PRESET_ORDER_ADV_INTEL)
  - AMD Advanced presets (PRESET_ORDER_ADV_AMD)
  ↓
Show cards in center panel
```

### 2. Preset Card Click
```
User clicks "AMD Advanced Tuning" card
  ↓
_on_card_clicked(preset_id="adv_amd_tuning")
  ↓
Update details title: "AMD Advanced Tuning"
  ↓
Load preset data from AMD_PRESETS_ADV[preset_name]  ← CRITICAL: Must be AMD data!
  ↓
Clear previous toggles
  ↓
Generate toggles for each setting in preset
  ↓
Show in details panel
```

### 3. CPU Segmented Control
```
User clicks "AMD" button
  ↓
_on_cpu_selected("AMD")
  ↓
Set checked state: amd_btn.setChecked(True), intel_btn.setChecked(False)
  ↓
Update internal state: self._preset_family = "amd"
  ↓
If current preset has AMD variant, reload it
Otherwise, keep current selection
```

### 4. Apply Preset
```
User clicks "Apply Preset"
  ↓
_on_apply_preset()
  ↓
Verify file loaded (show "No file loaded" if not)
  ↓
Get active preset data based on preset_id
  ↓
Build normalized map from preset data
  ↓
Match settings to model rows
  ↓
Apply via existing _apply_targets_now() mechanism
  ↓
Show success toast: "Preset applied - AMD Advanced Tuning"
  ↓
Update counts
```

---

## 🐛 Critical Bug Fix: AMD Routing

**Problem**: AMD Advanced must ALWAYS load AMD data, never Intel data.

**Root Cause**: ID/mapping confusion or CPU selector overriding family.

**Solution**:

```python
def _on_card_clicked(self, preset_id: str):
    """Handle preset card click"""
    self._active_preset_id = preset_id
    
    # Determine preset data based on ID (not CPU selector!)
    if preset_id.startswith("basic_"):
        preset_name = preset_id.replace("basic_", "")
        # Basic presets work for both
        if self._selected_cpu == "Intel":
            preset_data = INTEL_PRESETS_BASIC.get(preset_name, {})
        else:
            preset_data = AMD_PRESETS_BASIC.get(preset_name, {})
    
    elif preset_id.startswith("adv_intel_"):
        preset_name = preset_id.replace("adv_intel_", "")
        preset_data = INTEL_PRESETS_ADV.get(preset_name, {})
        # Force Intel CPU selected
        self._selected_cpu = "Intel"
        self.cpu_intel_btn.setChecked(True)
        self.cpu_amd_btn.setChecked(False)
    
    elif preset_id.startswith("adv_amd_"):
        preset_name = preset_id.replace("adv_amd_", "")
        preset_data = AMD_PRESETS_ADV.get(preset_name, {})  # ← ALWAYS AMD!
        # Force AMD CPU selected
        self._selected_cpu = "AMD"
        self.cpu_intel_btn.setChecked(False)
        self.cpu_amd_btn.setChecked(True)
    
    # ... continue with toggle generation ...
```

**Key Points**:
1. Preset ID determines data source
2. `adv_amd_*` → Always use `AMD_PRESETS_ADV`
3. `adv_intel_*` → Always use `INTEL_PRESETS_ADV`
4. CPU selector follows preset, not vice versa
5. CPU selector only matters for Basic presets (which have both variants)

---

## 📋 Implementation Checklist

### Phase 1: Data Structures (30 min)
- [ ] Add preset ID constants
- [ ] Create card metadata (title, desc, cpus)
- [ ] Map IDs to preset data sources

### Phase 2: UI Components (60 min)
- [ ] Create left sidebar (family list)
- [ ] Create center panel (card container)
- [ ] Create right panel (details header, toggles, footer)
- [ ] Wire up main layout

### Phase 3: Card Generation (45 min)
- [ ] Implement `_create_preset_card()` method
- [ ] Implement `_on_family_selected()` method
- [ ] Generate cards for each family

### Phase 4: Details Panel (60 min)
- [ ] Implement `_on_card_clicked()` method
- [ ] Load preset data correctly (AMD fix!)
- [ ] Generate toggle rows
- [ ] Wire CPU segmented control

### Phase 5: Apply Logic (30 min)
- [ ] Implement `_on_apply_preset()` method
- [ ] Reuse existing `_apply_targets_now()` mechanism
- [ ] Show success toast
- [ ] Implement Cancel (clear selection)

### Phase 6: Testing (45 min)
- [ ] Test all families load correctly
- [ ] Test AMD Advanced → loads AMD data
- [ ] Test Intel Advanced → loads Intel data
- [ ] Test Basic → respects CPU selector
- [ ] Test Apply → settings change
- [ ] Test Cancel → clears selection
- [ ] Test Preview (if implemented)

**Total Estimated Time**: ~4.5 hours

---

## 🎨 Visual Design Tokens

```python
# Spacing
SIDEBAR_WIDTH = 220
CARD_PADDING = 16
PANEL_MARGIN = 16
PANEL_SPACING = 16

# Typography
TITLE_SIZE = 16
TITLE_WEIGHT = 600
CARD_TITLE_SIZE = 14
CARD_TITLE_WEIGHT = 600
BODY_SIZE = 12
TAG_SIZE = 11

# Colors (from THEME)
BORDER = THEME['input_border']
BORDER_HOVER = THEME['input_focus']
BORDER_ACTIVE = THEME['accent']
TEXT = THEME['text']
MUTED = THEME['muted']
ACCENT = THEME['accent']
```

---

## 🧪 Test Cases

### Test 1: Family Switching
```
1. Click "Basic" → Should show Basic presets
2. Click "Advanced" → Should show Intel + AMD Advanced presets
3. Click "OEM/EC" → Should show OEM presets
```

### Test 2: AMD Routing (CRITICAL)
```
1. Click "Advanced" family
2. Click "AMD Advanced Tuning" card
3. Details panel should show AMD preset data
4. CPU selector should auto-select "AMD"
5. Click "Apply Preset"
6. Verify settings applied from AMD_PRESETS_ADV (not INTEL_PRESETS_ADV)
7. Toast should show "Preset applied - AMD Advanced Tuning"
```

### Test 3: Intel Routing
```
1. Click "Advanced" family
2. Click "Intel Advanced Tuning" card
3. Details panel should show Intel preset data
4. CPU selector should auto-select "Intel"
5. Click "Apply Preset"
6. Verify settings applied from INTEL_PRESETS_ADV
```

### Test 4: Basic Presets with CPU Selector
```
1. Click "Basic" family
2. Click a Basic preset card
3. Toggle CPU selector between Intel and AMD
4. Details should update to show respective variant
5. Apply should use correct variant
```

### Test 5: Toast Integration
```
1. Apply any preset
2. Should show success toast with preset name
3. Toast should appear top-right
4. Toast should auto-dismiss after 4s
5. Hover should pause timer
```

---

## 🔧 Implementation Tips

### 1. Preserve Existing Logic
Don't reinvent the wheel. Reuse:
- `normalize_key()` for setting name matching
- `build_normalized_map()` for preset data processing
- `_apply_targets_now()` for applying changes
- `self.model._rows` for accessing settings
- `self.pending_targets` for staging changes

### 2. Gradual Migration
Keep old code commented out initially:
```python
# OLD PRESETS UI - REMOVE AFTER TESTING
# presets_tab = QtWidgets.QWidget()
# ...old code...

# NEW PRESETS UI
presets_tab = QtWidgets.QWidget()
...new code...
```

### 3. Use Existing Widgets
If PresetRow works well, reuse it in details panel:
```python
for setting_name, setting_value in preset_data.items():
    # Option A: Reuse PresetRow
    row = PresetRow(setting_name, on=True)
    
    # Option B: Simple label rows
    row = QtWidgets.QWidget()
    # ...
```

### 4. Debug Helpers
Add logging to verify correct data loading:
```python
def _on_card_clicked(self, preset_id: str):
    logging.info(f"Selected preset: {preset_id}")
    # ... load data ...
    logging.info(f"Loaded {len(preset_data)} settings from {source}")
```

---

## 📊 Comparison: Old vs New

| Aspect | Old (2-Pane) | New (3-Pane) |
|--------|--------------|--------------|
| Family selection | Toggle switch (Intel/AMD only) + Page nav | Sidebar list (all families) |
| Preset browsing | Page navigation (arrows) | Visual cards (click) |
| CPU selection | Top toggle (affects all) | Per-preset segmented control |
| Settings preview | Table on left | Toggles in details panel |
| Visual hierarchy | Flat | Clear: Family → Preset → Details |
| AMD routing | Prone to confusion | Explicit ID-based routing |

---

## 🚀 Ready to Implement?

**Prerequisites**:
1. ✅ Qt errors fixed
2. ✅ Toast system ready
3. ✅ Existing preset data intact (PRESET_ORDER_*, *_PRESETS_*)

**Next Steps**:
1. Set aside 4-5 hours of focused time
2. Follow implementation checklist above
3. Test thoroughly with AMD and Intel presets
4. Deploy when all tests pass

**Or**: Implement incrementally:
- Week 1: Sidebar + Cards
- Week 2: Details panel
- Week 3: Apply logic + Testing

---

**Design Date**: 2025-10-22  
**Status**: Complete specification, ready for implementation  
**Risk**: Medium (requires careful testing)  
**Reward**: Significantly improved UX
