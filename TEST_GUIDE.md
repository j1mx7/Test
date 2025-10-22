# AutoBios - Testing Guide

## 🧪 Critical Fixes Testing

### Test A: Import Confirmation (MUST PASS)

**Issue Fixed**: Duplicate confirmation dialogs

**Steps**:
1. Launch AutoBios
2. Load an nvram.txt file
3. Click "Import (SCEWIN)" button
4. **Expected**: Custom modal appears (dark theme, outline buttons)
5. Click "Import" button
6. **Expected**: Modal closes, import starts
7. **CRITICAL**: Watch for second dialog
8. **✅ PASS**: If NO second QMessageBox appears
9. **❌ FAIL**: If stock Windows dialog pops up asking to confirm

**What Should Happen**:
- Single custom modal → Click Import → Immediate import → Toast notification
- NO second confirmation

**What Should NOT Happen**:
- Custom modal → Click Import → QMessageBox pops up → Have to confirm again

---

### Test B: AMD Advanced Preset Routing (MUST PASS)

**Issue Fixed**: AMD Advanced was loading Intel data

**Steps**:
1. Launch AutoBios
2. Load an nvram.txt file
3. Go to "Presets" tab
4. Find the family toggle switch (Intel/AMD)
5. Toggle to **AMD** (right position)
6. **Expected**: Label shows "AMD"
7. Click ">" arrow to navigate to Advanced page
8. **Expected**: Page title shows "Advanced Presets"
9. Look at preset names in the list
10. **Expected**: Should show AMD-specific presets
11. Toggle any preset ON (e.g., "Advanced Powersaving")
12. **Expected**: Preset table on left shows settings
13. **CRITICAL**: Verify settings are AMD-specific (not Intel)
14. Click "Apply Config"
15. **Expected**: Toast shows "Applied N changes"
16. **Expected**: Toast subtitle shows "AMD [PresetName]"

**✅ PASS**: If AMD family loads AMD_PRESETS_ADV data  
**❌ FAIL**: If AMD family loads INTEL_PRESETS_ADV data

**Debug Tip**: If test fails, the assertion at line ~4895 should trigger:
```
AssertionError: AMD family must use AMD_PRESETS_ADV
```

---

### Test C: Toast Notifications (MUST PASS)

**Issue Fixed**: Toasts positioned at bottom, needed top-right

**Steps**:
1. Launch AutoBios
2. Perform any action that shows a toast:
   - Import a file
   - Apply config
   - Reset settings
3. **Watch the toast notification**

**What to verify**:
- [ ] **Position**: Top-right corner
- [ ] **Distance from top**: ~56px (below custom title bar)
- [ ] **Distance from right**: ~16px
- [ ] **Animation in**: Slides DOWN from above (300ms)
- [ ] **Animation out**: Slides UP slightly + fades (200ms)
- [ ] **Duration**: Visible for ~3.5 seconds (success)
- [ ] **Opacity**: Slightly transparent (96%)
- [ ] **No overlap**: Doesn't cover window control buttons

**✅ PASS**: If toast appears top-right with smooth animations  
**❌ FAIL**: If toast appears at bottom or has no animation

---

## 🎨 Visual Verification

### Window Controls
**What to check**:
- [ ] Three buttons visible (Min, Max, Close)
- [ ] NO borders or boxes around buttons
- [ ] Just icons: ─ ☐ ✕
- [ ] Hover shows tint (not border change)
- [ ] Close button tint is reddish

**Reference**:
- Min/Max hover: `rgba(255, 255, 255, 0.12)` ~12% white
- Min/Max press: `rgba(255, 255, 255, 0.22)` ~22% white
- Close hover: `rgba(255, 80, 80, 0.15)` ~15% red
- Close press: `rgba(255, 80, 80, 0.25)` ~25% red

### Top Tabs
**What to check**:
- [ ] "Settings List" and "Presets" tabs
- [ ] Both have transparent backgrounds
- [ ] Both have 1px border visible
- [ ] Active tab has colored underline at bottom (2px)
- [ ] Inactive tab has NO underline
- [ ] Hover brightens border (doesn't fill background)

### "No File Loaded" Dialog
**What to check**:
- [ ] Dialog is frameless (no Windows title bar)
- [ ] Dark theme matching app
- [ ] **Dashed drop zone** with 1px dashed border
- [ ] Folder icon 📁 centered above text
- [ ] Text: "Drag & drop nvram.txt or click to browse"
- [ ] Two buttons **side-by-side** (not stacked)
- [ ] Both buttons have outline style:
  - Transparent background
  - 1px solid border
  - 10px border radius
- [ ] NO filled/blue buttons

### Confirm Import Modal
**What to check**:
- [ ] Frameless dark modal
- [ ] Centered on parent window
- [ ] Title: "Confirm BIOS Import"
- [ ] Warning text about BIOS modification
- [ ] Mentions "Make sure you have a backup"
- [ ] Two outline buttons: "Cancel" / "Import"
- [ ] "Import" button has slightly stronger border (1.5px vs 1px)
- [ ] ESC key closes modal
- [ ] Enter key confirms import

### Toast Notifications
**What to check**:
- [ ] Appear at **top-right** (not bottom)
- [ ] Dark card background `rgba(15, 20, 25, 0.96)`
- [ ] Thin border `rgba(255, 255, 255, 0.06)`
- [ ] 12px border radius
- [ ] Icon + text layout (18px icon, 14px text)
- [ ] Color-coded icons:
  - Success: Green check ✓
  - Info: Blue info ℹ
  - Error: Red X ✕
- [ ] Smooth slide-down entrance
- [ ] Smooth slide-up exit
- [ ] Auto-dismiss timing

---

## 🔬 Debug Testing

### If Import Shows Double Confirmation:

**Check**:
```bash
grep -n "QMessageBox.question" AutoBios.py
```

**Expected**: No results (all removed)  
**If found**: Line numbers where legacy dialogs still exist

**Fix**: Remove those QMessageBox calls

### If AMD Shows Intel Data:

**Check**: Look for error in console:
```
AssertionError: AMD family must use AMD_PRESETS_ADV
```

**If no error**: The guard is working, but data might be wrong upstream

**Debug**:
```python
# Add temporary logging in _rebuild_preset_view_and_targets
print(f"Family: {self._preset_family}")
print(f"Adv map: {adv_map is AMD_PRESETS_ADV}")
```

### If Toasts Don't Appear:

**Check**: Console for errors
```
AttributeError: 'AutoBiosWindow' object has no attribute 'notifications'
```

**Verify**: `self.notifications = NotificationManager(self)` exists in `__init__`

**Test manually**:
```python
# In Python console while app is running
window.notifications.notify_success("Test toast")
```

---

## 📈 Performance Testing

### Toast Responsiveness
- [ ] Import → Toast appears within 100ms
- [ ] No lag or stutter in animation
- [ ] Multiple toasts don't queue (newer replaces older)

### Reset Performance
- [ ] Reset with 100+ settings completes in <500ms
- [ ] UI updates immediately
- [ ] No freezing or blocking

### Preset Apply Performance
- [ ] Applying 50+ preset settings completes quickly
- [ ] Toast shows immediately after
- [ ] No noticeable delay

---

## 🎯 Success Criteria

### Must Pass
- ✅ Import shows single confirmation only
- ✅ AMD presets load AMD data
- ✅ Toasts appear top-right
- ✅ No QMessageBox dialogs anywhere
- ✅ All buttons use outline style

### Should Pass
- ✅ Smooth 60fps animations
- ✅ Toasts readable for 3.5s
- ✅ Reset clears everything
- ✅ Keyboard shortcuts work

### Nice to Have
- ⏳ High-DPI scaling (150%, 200%)
- ⏳ Multi-monitor support
- ⏳ Accessibility (screen readers)

---

## 🐛 If Tests Fail

### Import Duplicate Confirmation Fails
```bash
# Rollback
cp AutoBios_critical_fixes_20251022_172500.py AutoBios.py
```

Then manually remove QMessageBox.question calls

### AMD Routing Fails
Check console for assertion error  
If assertion triggers → Data is correct, frontend bug  
If no assertion → Guard not working, check line ~4895

### Toasts Position Wrong
Check parent_rect calculation in `show_toast()`  
Verify title_bar_height = 40px is correct

---

## 📸 Screenshots Needed

For documentation/review:

1. `caption_buttons_states.gif` - Hover/press states
2. `no_file_loaded_dialog.png` - Dashed drop zone
3. `confirm_import_modal.gif` - Single modal flow
4. `amd_preset_apply.gif` - AMD routing + toast
5. `toast_notifications.gif` - Top-right animations
6. `full_reset_modal.png` - Reset confirmation

---

## ✅ Final Checklist

Before marking complete:

- [ ] All 3 critical tests pass (A, B, C)
- [ ] Window controls work correctly
- [ ] Tabs show correctly
- [ ] All modals use outline style
- [ ] No Windows message boxes appear
- [ ] Toasts animate smoothly
- [ ] App doesn't crash
- [ ] Syntax validates

---

**If all checkboxes are marked: ✅ READY FOR PRODUCTION**

---

Test Date: _________  
Tester: _________  
Platform: Windows ___ (version)  
DPI Scaling: ___%  
Result: ✅ Pass / ❌ Fail  

Notes:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

