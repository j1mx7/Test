# autobios_clean.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import re
import sys
import subprocess
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import List, Tuple, Optional, Union, Dict, Any, Callable
from datetime import datetime
from functools import partial
from difflib import get_close_matches
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal, QPersistentModelIndex

# Configure logging (console only, no file)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


def normalize_key(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("–", "-").replace("—", "-")
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s)
    return s

def build_normalized_map(d: Dict[str, Any]) -> Dict[str, Tuple[str, Any]]:
    out: Dict[str, Tuple[str, Any]] = {}
    for k, v in d.items():
        nk = normalize_key(k)
        if nk not in out or len(k) > len(out[nk][0]):  # längerer Originalname gewinnt
            out[nk] = (k, v)
    return out
# --------------------------------------------------------------------------------------
# App & paths
# --------------------------------------------------------------------------------------
APP_TITLE = "AutoBios"

if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", "."))
else:
    BASE_DIR = Path(__file__).resolve().parent

SCEWIN_EXE_NAME = "SCEWIN_64.exe"
SCEWIN_EXE_PATH = BASE_DIR / SCEWIN_EXE_NAME

DEFAULT_NVRAM_NAME = "nvram.txt"
DEFAULT_NVRAM_PATH = BASE_DIR / DEFAULT_NVRAM_NAME

# --------------------------------------------------------------------------------------
# Theme
# --------------------------------------------------------------------------------------
THEME = {
    # Background colors - deeper, more consistent
    "bg":            "#0a0e13",
    "card":          "#0f1419",
    "card_hover":    "#151b22",

    # Text colors - softer for reduced eye strain
    "text":          "#e4e6eb",
    "muted":         "#9ca3af",

    # Border and grid colors
    "border":        "#1a2332",
    "grid":          "#1f2937",

    # Input field colors
    "input_bg":      "#0d1117",
    "input_border":  "#30363d",
    "input_focus":   "#4a90e2",

    # Selection and state colors
    "selection":     "#1e3a5f",
    "tab_selected":  "#151d28",

    # Status colors
    "warn":          "#f59e0b",
    "success":       "#10b981",
    "error":         "#ef4444",

    # Switch colors
    "switch_off":    "#1f2937",
    "switch_on":     "#4a90e2",

    # Accent colors
    "accent":        "#4a90e2",
    "accent_hover":  "#5b9def",
    "accent_press":  "#3a7fcd",
}

# --------------------------------------------------------------------------------------
# Preset definitions
# --------------------------------------------------------------------------------------
PRESET_ORDER_BASIC = [
    "Basic Tuning",
    "Full Tuning",
    "Advanced Powersaving",
    "Bluetooth & WiFi",
]

# BASIC presets
INTEL_PRESETS_BASIC: Dict[str, Dict[str, Any]] = {
    "Basic Tuning": {
    "Boot Performance Mode": ['Turbo Performance'],
    "Boot performance mode": ['Turbo Performance'],
    "Power Down Mode": ['No Power Down'],
    "PCI Express Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "PCI Express Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "PCIE Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Power Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "EIST": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Race To Halt (RTH)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Race to Halt": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "DMI ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "DMI Gen3 ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Native ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "PCH ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "ASPM Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "PEG ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "C-State Auto Demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "C-State Un-demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "C-state Pre-Wake": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'], 
    "CPU Enhanced Halt(C1E)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "CPU Enhanced Halt": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "CPU C6 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "CPU C7 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "C0 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "C1 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'], 
    "C2 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'], 
    "C3 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "C6/C7 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'], 
    "C8 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "C10 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "CPU C-States": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Intel C-State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "C states": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Enhanced C-states": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Package C-State Demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Package C-State Un-demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "CState Pre-Wake": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "C-States Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Package C State Limit": ['C0/C1'],
    "Package C State limit": ['C0/C1'],
    },
    "Full Tuning": {
  "3DMark01 Enhancement": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Spread Spectrum": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Enable 8254 Clock Gate": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ACPI D3 Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ACPI D3Cold Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ACPI Sleep State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ACPI T-States": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ACPI Standby State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ACS": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Active LTR": ['80008000'],
  "ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Advanced Error Reporting": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "AP threads Idle Manner": ['RUN Loop'],
  "BCLK Aware Adaptive Voltage": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Bi-Directional PROCHOT": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Bi-directional PROCHOT#": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "BIST": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "BIST Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Boot Performance Mode": ['Turbo Performance'],
  "Boot performance mode": ['Turbo Performance'],
  "Bootup NumLock State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CER": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C-State Auto Demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C-State Un-demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C-state Pre-Wake": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C0 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C1 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C2 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C3 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C6/C7 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C6DRAM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C6Dram": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C7 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C8 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C10 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C-States Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "C states": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Control Iommu Pre-boot Behavior": ['Disable IOMMU'],
  "CPU CrashLog": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Cpu CrashLog (Device 10)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CPU C-States": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CPU C6 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CPU C7 State Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CPU CrashLog": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CPU Enhanced Halt": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CPU Enhanced Halt(C1E)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CrashLog Cdie Rearm": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CrashLog Feature": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CrashLog On All Reset": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CrashLog PMC Clear": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CrashLog PMC Rearm": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CrashLog enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CrashLog On All Reset": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CPU Thermal Monitor": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "DMI ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "DMI Gen3 ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "DLVR RFI Mitigation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "DDR PowerDown and idle counter": ['PCODE'],
  "DMI Thermal Setting": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Deep Sleep": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "DeepSx Wake on WLAN and BT Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Disable DSX ACPRESENT PullDown": ['Enabled', 'Enable'],
  "Disable PROCHOT# Output": ['Enabled', 'Enable'],
  "Disable VR Thermal Alert": ['Enabled', 'Enable'],
  "Dual Tau Boost": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "DPC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "EDPC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "EC CS Debug Light": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "EC CS Debug Ligh": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "EC Low Power Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "EC Notification": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Enable All Thermal Functions": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Enable Hibernation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Energy Efficient P-State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Energy Efficient Turbo": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Energy Performance Gain": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Enhanced C-states": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Enhanced Thermal Velocity Boost": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Enhanced TVB": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "EIST": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Enable Remote Platform Erase Feature": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "EPG DIMM Idd3N": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "EPG DIMM Idd3P": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "FER": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Force LTR Override": ['Enabled', 'Enable'],
  "For LPDDR Only DDR PowerDown and idle counter": ['PCODE'],
  "For LPDDR Only: DDR PowerDown and idle counter": ['PCODE'],
  "For LPDDR Only Throttler CKEMin Defeature": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "For LPDDR Only: Throttler CKEMin Defeature": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Foxville I225 Wake on LAN Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "HwP Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "HwP Autonomous Per Core P State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "HwP Autonomous EPP Grouping": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "HDC Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "IGD VTD": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "IGD VTD Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Idle LTR": ['80008000'],
  "Fine Granularity Refresh mode": ['Enabled', 'Enable'],
  "FLL OC mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Intel (VMX) Virtualization Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Intel C-State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Intel Speed-Shift Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Intel(R) Speed Shift Technology Interrupt Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Intel(R) SpeedStep(tm)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Interrupt Redirection Mode Selection": ['Round Robin'],
  "IOAPIC 24-119 Entries": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "IOP VTD": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "IOP VTD Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "IPU VTD": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "IPU VTD Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "L1 Low": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "L1 Substates": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "LAN Wake From DeepSx": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Legacy Game Compatibility Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Low Power S0 Idle Capability": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "LPMode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "LPM S0i2.0USB2PHY Sus Well Power Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "LTR": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "LTR Mechanism Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Max Power Savings Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Me State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ME State": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "NFER": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Native ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "DMI Link ASPM Control": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "OBFF": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PME SCI": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "OS IDLE Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PCH ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PCH Cross Throttling": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PCH Energy Reporting": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PCH Trace Hub Enable Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PCI Express Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PCI Express Power Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PCI-X Latency Timer": ['32 PCI Bus Clocks'],
  "PCIE Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PCIE Clock Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEG ASPM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP CPU": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP CSME": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP CSME": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP GNA": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP Graphics": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP HECI3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP I2C0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP I2C1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP I2C2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP I2C3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP I2C4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP I2C5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP I2C6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP I2C7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP IPU": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP LAN(GBE)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP PCIe GFX": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP PCIe LAN": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP PCIe Other": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP PCIe Storage": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP SATA": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP SPI": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP THC0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP THC1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP TCSS": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP UART": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP VMD": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP WLAN": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP XHCI": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP enumerated SATA ports": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PEP EMMC": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Per Core P state OS control mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Per Core P state os control mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Platform Power Management": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Power Down Mode": ['No Power Down , Disabled'],
  "Power Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Power Loading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PowerDown Energy Ch0Dimm0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PowerDown Energy Ch0Dimm1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PowerDown Energy Ch1Dimm0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PowerDown Energy Ch1Dimm1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PROCHOT Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PROCHOT Response": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PS2 Devices Support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PS2 Keyboard and mouse": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Package C State Limit": ['C0/C1'],
  "Package C State limit": ['C0/C1'],
  "Package C-State Demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Package C-State Un-demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Processor trace": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PROCHOT Response": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PROCHOT Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PROCHOT Response": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Ring Down Bin": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "RGB Fusion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "RGB Light": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "RSR": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Remote Platform Erase Feature": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "RFI Mitigation": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Race To Halt (RTH)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Race to Halt": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "SA GV": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "SA PLL Frequency": ['3200MHz', '3200 MHz'],
  "SA PLL Frequency Override": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off', '3200MHz', '3200 MHz'],
  "USB DbC Enable Mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "SMART Self Test": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "SMM Processor Trace": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "S0i": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "S0ix Auto Demotion": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "S0i": ['Disable', 'Disabled'],
  "Thermal Monitor": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Thermal Throttling Level": ['Manual'],
  "Thermal Velocity Boost": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Three Strike Counter": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "TVB Ratio Clipping": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "TVB Ratio Clipping Enhanced": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "TVB Voltage Optimizations": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "URR": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "USB2PHY Sus Well Power Gating": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "VT-d": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Wake On Touch": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Wake On WiGig": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Wake on LAN Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Wake on WLAN and BT Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Wake From Thunderbolt(TM) Devices": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "WoV (Wake on Voice)": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ZPODD": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Legacy IO Low Latency": ['Enabled', 'Enable'],
  "XHCI Hand-off": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "JTAG C10 Power Gate": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Hardware Prefetcher": ['Enabled', 'Enable'],
  "MonitorMWait": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Overclocking Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Intel(R) Turbo Boost Max Technology 3.0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Intel(R) Speed Shift Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PTM": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock9": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock10": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock11": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock12": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock13": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock14": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock15": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock16": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "ClkReq for Clock17": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Enable ClockRqe Messaging": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Dynamic Memory Boost": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Dynamic Memory Performance Boost": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Panel Scaling": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "P-state Capping": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Tcc Activation Offset": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Tcc Offset Time Window": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Tcc Offset Clamp Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Tcc Offset Lock Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "GT VR Fast Vmode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "SA VR Fast Vmode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "FIVR Spread Spectrum": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Overclocking Lock": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Disable Fast PKG C State Ramp for IA Domain": ['True'],
  "Disable Fast PKG C State Ramp for GT Domain": ['True'],
  "Disable Fast PKG C State Ramp for SA Domain": ['True'],
  "Timed MWAIT": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "EC Polling Period": ['255'],
  "PECI": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "IA CEP Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "GT CEP Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CState Pre-Wake": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Native PCIE Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "MachineCheck": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "UnderVolt Protection": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "SelfRefresh IdleTimer": ['65535'],
  "Throttler CKEMin Defeature": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "D3 Setting for Storage": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "FCLK Frequency for Early Power On": ['1GHz'],
  "SMM Use Delay Indication": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "SMM Use Block Indication": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "SMM Use SMM en-US Indication": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Core VR Fast Vmode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "HECI Timeouts": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "CPU Replaced Polling Disable": ['Enable', 'Enabled'],
  "HECI Message check Disable": ['Enable', 'Enabled'],
  "Active Trip Point 0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Active Trip Point 1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Passive Trip Point": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Active Trip Points": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Critical Trip Points": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "PCH Temp Read": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "Power Loss Notification Feature": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "HID Event Filter Driver": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "IA ICC Unlimited Mode": ['Enable', 'Enabled'],
  "GT ICC Unlimited Mode": ['Enable', 'Enabled'],
  "T1 Multipler": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "T2 Multipler": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "T3 Multipler": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
  "SATA Thermal Setting": ['Manual'],
  "Page Close Idle Timeout": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
},
    "Advanced Powersaving": {
    "C-States Control": ['Disable', 'Disabled'],
    "CPU Enhanced Halt(C1E)": ['Disable', 'Disabled'],
    "C3 State Support": ['Disable', 'Disabled'],
    "C6/C7 State Support": ['Disable', 'Disabled'],
    "C8 State Support": ['Disable', 'Disabled'],
    "C10 State Support": ['Disable', 'Disabled'],
    "Package C State limit": ['Disable', 'Disabled'],
    "C states": ['Disable', 'Disabled'],
    "Enhanced C-states": ['Disable', 'Disabled'],
    "C-State Auto Demotion": ['Disable', 'Disabled'],
    "C-State Un-demotion": ['Disable', 'Disabled'],
    "Package C-State Demotion": ['Disable', 'Disabled'],
    "Package C-State Un-demotion": ['Disable', 'Disabled'],
    "CState Pre-Wake": ['Disable', 'Disabled'],
    "AP threads Idle Manner": ['RUN Loop'],
    "EPG DIMM Idd3N": ['Disable', 'Disabled', '0'],
    "EPG DIMM Idd3P": ['Disable', 'Disabled', '0'],
    "Serial Io Uart Debug Power Gating": ['Disable', 'Disabled'],
    "PCI Express Clock Gating": ['Disable', 'Disabled'],
    "PCI Express Power Gating": ['Disable', 'Disabled'],
    "Power Gating": ['Disable', 'Disabled'],
    "Race To Halt (RTH)": ['Disable', 'Disabled'],
    "EC Low Power Mode": ['Disable', 'Disabled'],
    "C6DRAM": ['Disable', 'Disabled'],
    "ACPI T-States": ['Disable', 'Disabled', '0'],
    "ACPI D3Cold Support": ['Disable', 'Disabled'],
    "JTAG C10 Power Gate": ['Disable', 'Disabled'],
    "HDC Control": ['Disable', 'Disabled'],
    "Bi-Directional PROCHOT": ['Disable', 'Disabled'],
    "PBi-Directional PROCHOT#": ['Disable', 'Disabled'],
    "RC6(Render Standby)": ['Disable', 'Disabled'],
    "Enable 8254 Clock Gate": ['Disable', 'Disabled'],
    "ZPODD": ['Disable', 'Disabled'],
    "CPU EIST Function": ['Disable', 'Disabled'],
    "EIST": ['Disable', 'Disabled'],
    "Ring Down Bin": ['Disable', 'Disabled'],
    "Ring to Core offset": ['Disable', 'Disabled'],
    "Ring to Core offset (Down Bin)": ['Disable', 'Disabled'],
    "Intel(R) Speed Shift Technology Interrupt Control": ['Disable', 'Disabled'],
    "Intel(R) SpeedStep(tm)": ['Disable', 'Disabled'],
    "SpeedStep": ['Disable', 'Disabled'],
    "TVB Voltage Optimizations": ['Disable', 'Disabled'],
    "Enhanced Thermal Velocity Boost": ['Disable', 'Disabled'],
    "Thermal Velocity Boost": ['Disable', 'Disabled'],
    "Voltage Reduction Initiated TVB": ['Disable', 'Disabled'],
    "Enhanced TVB": ['Disable', 'Disabled'],
    "Frequency Clipping TVB": ['Disable', 'Disabled'],
    "BCLK Aware Adaptive Voltage": ['Disable', 'Disabled'],
    "Dual Tau Boost": ['Disable', 'Disabled'],
    "MonitorMWait": ['Disable', 'Disabled'],
    "Energy Efficient P-state": ['Disable', 'Disabled'],
    "Energy Efficient Turbo": ['Disable', 'Disabled'],
    "Energy Performance Gain": ['Disable', 'Disabled'],
    "Power Down Mode": ['No Power Down'],
    "LPMode": ['Disable', 'Disabled'],
    "Disable DSX ACPRESENT PullDown": ['Enable', 'Enabled'],
    "ACPI Sleep State": ['Disable', 'Disabled'],
    "PCH Cross Throttling": ['Disable', 'Disabled'],
    },


    "Bluetooth & WiFi": {
    "WAN Radio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Wi-Fi 6E for Japan": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Onboard CNVi Module Control": ['Disable Integrated', 'Disable', 'Disabled'],
    "CNVi mode": ['Disable Integrated', 'Disable', 'Disabled'],
    "WWAN Participant": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "WWAN": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Wifi Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Wifi Core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Wi-Fi Core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Wireless CNV Config Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "WWAN Reset Workaround": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Connectivity mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Onboard WAN Device": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "BT Core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Blue Tooth Enable": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Bluetooth PLDR support": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "BT core": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Bluetooth": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Bluetooth Controller": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Discrete Bluetooth Interface": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Bluetooth Sideband": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "BT Intel HFP": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "BT Intel A2DP": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "BT Intel LE Audio": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    "Onboard CNVi Module Control": ['Disable Integrated', 'Disable', 'Disabled'],
    "CNVi Mode": ['Disable Integrated', 'Disable', 'Disabled'],
    "Connectivity mode": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
    },
}

AMD_PRESETS_BASIC: Dict[str, Dict[str, Any]] = {
    "Basic Tuning": {
    "SoC/Uncore OC Mode": ['Enable', 'Enabled'],
    "Power Down Enable": ['Disable', 'Disabled'],
    "Global C-state Control": ['Disable', 'Disabled'],
    "DF Cstates": ['Disable', 'Disabled'],
    "DRAM Latency Enhance": ['Disable', 'Disabled'],
    "3DMark01 Enhancement": ['Disable', 'Disabled'],
    "Chipset Power Saving Features": ['Disable', 'Disabled'],
    "ACP Power Gating": ['Disable', 'Disabled'],
    },

    "Full Tuning": {
    "Global C-state Control": ['Disable', 'Disabled'],
    "IOMMU": ['Disable', 'Disabled'],
    "CSM": ['Disable', 'Disabled'],
    "PX Dynamic Mode": ['Disable', 'Disabled'],
    "Discrete GPU's Audio": ['Disable', 'Disabled'],
    "Adaptive S4": ['Disable', 'Disabled'],
    "LAN Power Enable": ['Disable', 'Disabled'],
    "PM L1 SS": ['Disable', 'Disabled'],
    "Unused GPP Clocks Off": ['Disable', 'Disabled'],
    "AMD Cool&Quiet function": ['Disable', 'Disabled'],
    "Clock Power Management(CLKREQ#)": ['Disable', 'Disabled'],
    "Win7 USB Wake Support": ['Disable', 'Disabled'],
    "ACP Power Gating": ['Disable', 'Disabled'],
    "ACP CLock Gating": ['Disable', 'Disabled'],
    "Power Down Enable": ['Disable', 'Disabled'],
    "ECO Mode": ['Disable', 'Disabled'],
    "LN2 Mode": ['Disable', 'Disabled'],
    "LCLK DPM": ['Disable', 'Disabled'],
    "LCLK DPM Enhanced PCIe Detection": ['Disable', 'Disabled'],
    "SMEE": ['Disable', 'Disabled'],
    "ACPI _CST C1 Declaration": ['Disable', 'Disabled'],
    "Indirect Branch Prediction Speculation": ['Disable', 'Disabled'],
    "Freeze DF module queues on error": ['Disable', 'Disabled'],
    "C6 Mode": ['Disable', 'Disabled'],
    "EPU Power Saving Mode": ['Disable', 'Disabled'],
    "3DMark01 Enhancement": ['Disable', 'Disabled'],
    "Isochronous Support": ['Disable', 'Disabled'],
    "PS2 Devices Support": ['Disable', 'Disabled'],
    "Network Stack Driver Support": ['Disable', 'Disabled'],
    "RGB Fusion": ['Disable', 'Disabled'],
    "Security Device Support": ['Disable', 'Disabled'],
    "ACPI Sleep State": ['Disable', 'Disabled'],
    "Onboard PCIE LAN PXE ROM": ['Disable', 'Disabled'],
    "Onboard LED": ['Disable', 'Disabled'],
    "CRB test": ['Disable', 'Disabled'],
    "NX Mode": ['Disable', 'Disabled'],
    "UMA Mode": ['Disable', 'Disabled'],
    "AB Clock Gating": ['Disable', 'Disabled'],
    "PCIB Clock Run": ['Disable', 'Disabled'],
    "SATA MAXGEN2 CAP OPTION": ['Disable', 'Disabled'],
    "Aggressive Link PM Capability": ['Disable', 'Disabled'],
    "Chipset Power Saving Features": ['Disable', 'Disabled'],
    "USB Phy Power Down": ['Disable', 'Disabled'],
    "Power Loading": ['Disable', 'Disabled'],
    "Wake on LAN": ['Disable', 'Disabled'],
    "SATA Partial State Capability": ['Disable', 'Disabled'],
    "SATA Slumber State Capability": ['Disable', 'Disabled'],
    "SATA Hot-Removable Support": ['Disable', 'Disabled'],
    "S0I3": ['Disable', 'Disabled'],
    "GPP Serial Debug Bus Enable": ['Disable', 'Disabled'],
    "AMD StartUp PWM Enable": ['Disable', 'Disabled'],
    "NBIO SyncFlood Generation": ['Disable', 'Disabled'],
    "Link Training Retry": ['Disable', 'Disabled'],
    "S3/Modern Standby Support": ['Disable', 'Disabled'],
    "ALink RAS Support": ['Disable', 'Disabled'],
    "MCA error thresh enable": ['Disable', 'Disabled'],
    "IPv4 HTTP Support": ['Disable', 'Disabled'],
    "IPv6 HTTP Support": ['Disable', 'Disabled'],
    "Ipv4 PXE Support": ['Disable', 'Disabled'],
    "Ipv6 PXE Support": ['Disable', 'Disabled'],
    "XHCI Hand-off": ['Disable', 'Disabled'],
    "Legacy USB Support": ['Disable', 'Disabled'],
    "EHCI Hand-off": ['Disable', 'Disabled'],
    "USB Mass Storage Driver Support": ['Disable', 'Disabled'],
    "Parallel Port": ['Disable', 'Disabled'],
    "SmartShift Control": ['Disable', 'Disabled'],
    "SmartShift Enable": ['Disable', 'Disabled'],
    "STAPM Boost": ['Disable', 'Disabled'],
    "Debug Port Table": ['Disable', 'Disabled'],
    "Debug Port Table 2": ['Disable', 'Disabled'],
    "BME DMA Mitigation": ['Disable', 'Disabled'],
    "ASPM Support": ['Disable', 'Disabled'],
    "_OSC For PCI0": ['Disable', 'Disabled'],
    "SB C1E Support": ['Disable', 'Disabled'],
    "Bootup NumLock State": ['Disable', 'Disabled'],
    "Wake on PME": ['Disable', 'Disabled'],
    "Thunderbolt Support": ['Disable', 'Disabled'],
    "D3 Cold Support": ['Disable', 'Disabled'],
    "D3Cold Support": ['Disable', 'Disabled'],
    "Platform First Error Handling": ['Disable', 'Disabled'],
    "SMU and PSP Debug Mode": ['Disable', 'Disabled'],
    "vPCIe ARI Support": ['Disable', 'Disabled'],
    "CV test": ['Disable', 'Disabled'],
    "Loopback Mode": ['Disable', 'Disabled'],
    "USB ecc SMI Enable": ['Disable', 'Disabled'],
    "eMMC Boot": ['Disable', 'Disabled'],
    "eMMC/SD Configure": ['Disable', 'Disabled'],
    "Data Scramble": ['Disable', 'Disabled'],
    "CPU PCIE ASPM Mode Control": ['Disable', 'Disabled'],
    "Fast Boot": ['Disable', 'Disabled'],
    "POST Beep": ['Disable', 'Disabled'],
    "CPU Fan Fail Warning Control": ['Disable', 'Disabled'],
    "I2C 1 Enable": ['Disable', 'Disabled'],
    "I2C 2 Enable": ['Disable', 'Disabled'],
    "I2C 3 Enable": ['Disable', 'Disabled'],
    "I2C 4 Enable": ['Disable', 'Disabled'],
    "I2C 5 Enable": ['Disable', 'Disabled'],
    "PPIN Opt-in": ['Disable', 'Disabled'],
    "CC6 memory region encryption": ['Disable', 'Disabled'],
    "DRAM scrub time": ['Disable', 'Disabled'],
    "Poison scrubber control": ['Disable', 'Disabled'],
    "Redirect scrubber control": ['Disable', 'Disabled'],
    "GMI encryption control": ['Disable', 'Disabled'],
    "xGMI encryption control": ['Disable', 'Disabled'],
    "Data Poisoning": ['Disable', 'Disabled'],
    "RCD Parity": ['Disable', 'Disabled'],
    "DRAM Address Command Parity Retry": ['Disable', 'Disabled'],
    "Write CRC Enable": ['Disable', 'Disabled'],
    "DRAM Write CRC Enable and Retry Limit": ['Disable', 'Disabled'],
    "DRAM ECC Enable": ['Disable', 'Disabled'],
    "DRAM UECC Retry": ['Disable', 'Disabled'],
    "BankGroupSwap": ['Disable', 'Disabled'],
    "Address Hash Bank": ['Disable', 'Disabled'],
    "Address Hash CS": ['Disable', 'Disabled'],
    "Address Hash Rm": ['Disable', 'Disabled'],
    "DMA Protection": ['Disable', 'Disabled'],
    "DMAr Support": ['Disable', 'Disabled'],
    "ACS Enable": ['Disable', 'Disabled'],
    "Enable AER Cap": ['Disable', 'Disabled'],
    "DF Cstates": ['Disable', 'Disabled'],
    "NBIO SyncFlood Reporting": ['Disable', 'Disabled'],
    "Log Poison Data from SLINK": ['Disable', 'Disabled'],
    "Edpc Control": ['Disable', 'Disabled'],
    "ESPI Enable": ['Disable', 'Disabled'],
    "ASPM Control for CPU": ['Disable', 'Disabled'],
    "SVM Mode": ['Disable', 'Disabled'],
    "Spread Spectrum": ['Disable', 'Disabled'],
    "Opcache Control": ['Disable', 'Disabled'],
    "CPU temperature Warning Control": ['Disable', 'Disabled'],
    "TSME": ['Disable', 'Disabled'],
    "ASPM Mode Control": ['Disable', 'Disabled'],
    "SR-IOV Support": ['Disable', 'Disabled'],
    "Int. Clk Differential Spread": ['Disable', 'Disabled'],
    "PCIe Ten Bit Tag Support": ['Disable', 'Disabled'],
    "NBIO Poison Consumption": ['Disable', 'Disabled'],
    "NBIO RAS Control": ['Disable', 'Disabled'],
    "Sata RAS Support": ['Disable', 'Disabled'],
    "Aggresive SATA Device Sleep Port 0": ['Disable', 'Disabled'],
    "Aggresive SATA Device Sleep Port 1": ['Disable', 'Disabled'],
    "Socket1 DevSlp0 Enable": ['Disable', 'Disabled'],
    "Socket1 DevSlp1 Enable": ['Disable', 'Disabled'],
    "Periodic Directory Rinse": ['Disable', 'Disabled'],
    "PSS Support": ['Disable', 'Disabled'],
    "Core Watchdog Timer Enable": ['Disable', 'Disabled'],
    "Streaming Stores Control": ['Disable', 'Disabled'],
    "Disable DF to external downstream IP SyncFloodPropagation": ['Disable', 'Disabled'],
    "Disable DF sync flood propagation": ['Disable', 'Disabled'],
    "xGMI Max Link Width Control": ['Disable', 'Disabled'],
    "xGMI Link Width Control": ['Disable', 'Disabled'],
    "ACPI Standby State": ['Disable', 'Disabled'],
    "NBIO DPM Control": ['Disable', 'Disabled'],
    "NBIO RAS Global Control": ['Disable', 'Disabled'],
    "PSP error injection support": ['Disable', 'Disabled'],
    "Determinism Control": ['Disable', 'Disabled'],
    "Restore On AC Power Loss": ['Disable', 'Disabled'],
    "APBDIS": ['1'],
    "Fixed SOC Pstate": ['Enable', 'Enabled'],
    "Determinism Slider": ['Enable', 'Enabled'],
    "SRIS": ['Enable', 'Enabled'],
    "BankGroupSwapAlt": ['Enable', 'Enabled'],
    "xGMI Force Link Width Control": ['Enable', 'Enabled'],
    "Core Performance Boost": ['Enable', 'Enabled'],
    "Above 4G Decoding": ['Enable', 'Enabled'],
    "Re-Size BAR Support": ['Enable', 'Enabled'],
    "DRAM Latency Enhance": ['Enable', 'Enabled'],
    "SoC/Uncore OC Mode": ['Enable', 'Enabled'],
    "FFE Write Training": ['Enable', 'Enabled'],
    "DFE Read Training": ['Enable', 'Enabled'],
    "Fast Short REP MOVSB": ['Enable', 'Enabled'],
    "Enhanced REP MOVSB/STOSB": ['Enable', 'Enabled'],
    "REP-MOV/STOS Streaming": ['Enable', 'Enabled'],
    "DRAM map inversion": ['Enable', 'Enabled'],
    "SPD Read Optimization": ['Enable', 'Enabled'],
    "PCIe Ten Bit Tag Support": ['Enable', 'Enabled'],
    "ACPI SRAT L3 Cache As NUMA Domain": ['Enable', 'Enabled'],
    "Extended Tag": ['Enable', 'Enabled'],
    "Sata Disabled AHCI Prefetch Function": ['Enable', 'Enabled'],
    "L1 Stream HW Prefetcher": ['Enable', 'Enabled'],
    "L2 Stream HW Prefetcher": ['Enable', 'Enabled'],
    "MsiDis in HPET": ['Enable', 'Enabled'],
    "DRAM Post Package Repair": ['Enable', 'Enabled'],
    "System probe filter": ['Enable', 'Enabled'],
    "CPPC": ['Enable', 'Enabled'],
    "CPPC Preferred Cores": ['Enable', 'Enabled'],
    "SPI 100MHz Support": ['Enable', 'Enabled'],
    "PSPP Policy": ['Performance'],
    "SATA CLK Mode Option": ['100mhz'],
    "Command Rate": ['1T'],
    "AMD KVM Mouse Protocol": ['Absolute'],
    "Memory interleaving size": ['1 KB'],
    "4-link xGMI max speed": ['25Gbps'],
    "3-link xGMI max speed": ['25Gbps'],
    "xGMI Force Link Width": ['2'],
    "xGMI Max Link Width": ['1'],
    "Socket 0 NBIO 0 Target DPM Level": ['2'],
    "Socket 0 NBIO 1 Target DPM Level": ['2'],
    "Socket 0 NBIO 2 Target DPM Level": ['2'],
    "Socket 0 NBIO 3 Target DPM Level": ['2'],
    "Socket 1 NBIO 0 Target DPM Level": ['2'],
    "Socket 1 NBIO 1 Target DPM Level": ['2'],
    "Socket 1 NBIO 2 Target DPM Level": ['2'],
    "Socket 1 NBIO 3 Target DPM Level": ['2'],
    "Power Supply Idle Control": ['Typical Current Idle'],
    "SB Clock Spread Spectrum Option": ['-0.362%'],
    "SPI Fast Read Speed": ['100MHz'],
    "SPI Read Mode": ['Fast Read'],
    },


    "Basic Powersavings": {
    "ACP Power Gating": ['Disable', 'Disabled'],
    "ACP Clock Gating": ['Disable', 'Disabled'],
    "ACP CLock Gating": ['Disable', 'Disabled'],
    "Global C-state Control": ['Disable', 'Disabled'],
    "Power Down Enable": ['Disable', 'Disabled'],
    "EPU Power Saving Mode": ['Disable', 'Disabled'],
    "PCIB Clock Run": ['Disable', 'Disabled'],
    "AB Clock Gating": ['Disable', 'Disabled'],
    "Chipset Power Saving Features": ['Disable', 'Disabled'],
    "ASPM Support": ["Disabled", "Disable"],
    "USB Phy Power Down" : ["Disabled", "Disable"],
    "DF Cstates": ["Disabled", "Disable"],
    "S3/Modern Standby Support": ['Disable', 'Disabled'],
    "D3Cold Support": ['Disable', 'Disabled'],
    "APBDIS": ['1'],
    },
    "Advanced Powersaving": {
    "EPU Power Saving Mode": ['Disable', 'Disabled'],
    "USB Phy Power Down" : ["Disabled", "Disable"],
    "Global C-state Control": ['Disable', 'Disabled'],
    "ACP Power Gating": ['Disable', 'Disabled'],
    "ACP Clock Gating": ['Disable', 'Disabled'],
    "ACP CLock Gating": ['Disable', 'Disabled'],
    "AB Clock Gating": ['Disable', 'Disabled'],
    "PCIB Clock Run": ['Disable', 'Disabled'],
    "DF Cstates": ['Disable', 'Disabled'],
    "SoC/Uncore OC Mode": ['Enabled', 'Enable'],
    "AMD Cool&Quiet function": ['Disable', 'Disabled'],
    "ACPI Standby State": ['Disable', 'Disabled'],
    "ACPI Sleep State": ['Disable', 'Disabled'],
    "ACPI _CST C1 Declaration": ['Disable', 'Disabled'],
    "SB C1E Support": ['Disable', 'Disabled'],
    "PCIe ASPM Mode": ['Disabled', 'Disable'],
    "ASPM Control for CPU": ['Disabled', 'Disable'],
    "ASPM Control": ['Disabled', 'Disable'],
    "ASPM Support": ['Disabled', 'Disable'],
    "ASPM": ['Disabled', 'Disable'],
    "S3 PCIe Save Restore Mode": ['Disabled', 'Disable'],
    "S3/Modern Standby Support": ['Disabled', 'Disable'],
    "Device Sleep for AHCI Port 0": ['Disabled', 'Disable'],
    "Device Sleep for AHCI Port 1": ['Disabled', 'Disable'],
    "Device Sleep for AHCI Port 2": ['Disabled', 'Disable'],
    "Device Sleep for AHCI Port 3": ['Disabled', 'Disable'],
    "Aggresive SATA Device Sleep Port 0": ['Disabled', 'Disable'],
    "Aggresive SATA Device Sleep Port 1": ['Disabled', 'Disable'],
    "Aggresive SATA Device Sleep Port 2": ['Disabled', 'Disable'],
    "Aggresive SATA Device Sleep Port 3": ['Disabled', 'Disable'],
    "Aggresive SATA Device Sleep Port 4": ['Disabled', 'Disable'],
    "Aggresive SATA Device Sleep Port 5": ['Disabled', 'Disable'],
    "Aggresive SATA Device Sleep Port 6": ['Disabled', 'Disable'],
    "Aggresive SATA Device Sleep Port 7": ['Disabled', 'Disable'],
    "Adaptive S4": ['Disabled', 'Disable'],
    "PM L1 SS": ['Disabled', 'Disable'],
    "Clock Power Management(CLKREQ#)": ['Disabled', 'Disable'],
    "Clock Power Management": ['Disabled', 'Disable'],
    "Chipset Power Saving Features": ['Disabled', 'Disable'],
    "Power Down Enable": ['Disabled', 'Disable'],
    "NPU Deep Sleep Enable": ['Disabled', 'Disable'],
    "ErP": ['Disabled', 'Disable'],
    "D3Cold Support": ['Disabled', 'Disable'],
    "APBDIS": ['1'],
    "Unused GPP Clocks Off": ['Disable', 'Disabled'],
    },
    "Bluetooth and WiFi": {
    },
}

# ADVANCED presets (page 2) — dummy example names per family
PRESET_ORDER_ADV_INTEL = [
"Disable C-States",
"CPU Powersavings",
"Disable Thermal Settings",
"Disable Voltage / Overclocking Limits",
"Tune Memory Settings",
"Enable PCI Delay Optimization",
"Disable Snoop",
"Disable Hyper Threading",
"Disable ClkReq",
"Frequency Settings",
"PCIe Management", 
"Disable Gating",
"Disable Spread Spectrum",
"Disable Sleep States",
"Disable WakeOn",
"Disable Security",
"Disable TPM & Secure Boot",
"Disable Virtualization",
"Disable Error Handling",
"Disable PCH Settings",
"Tune EC Settings",
"Disable Audio",
"Disable RGB",
"Disable PEP",
"Disable Legacy",
]
PRESET_ORDER_ADV_AMD = [
"Disable C-States",
"CPU Powersavings",
"Disable Thermal Settings",
"Disable Voltage / Overclocking Limits",
"Tune Memory Settings",
"Enable PCI Delay Optimization",
"Disable Snoop",
"Disable Hyper Threading",
"Disable ClkReq",
"Frequency Settings",
"PCIe Management",
"Disable Gating",
"Disable Spread Spectrum",
"Disable Sleep States",
"Disable WakeOn",
"Disable Security",
"Disable TPM & Secure Boot",
"Disable Virtualization",
"Disable Error Handling",
"Disable PCH Settings",
"Tune EC Settings",
"Disable Audio",
"Disable RGB",
"Disable PEP",
"Disable Legacy",
]

AMD_PRESETS_ADV: Dict[str, Dict[str, Any]] = {
    "Disable C-States": {
       "Global C-state Control": ['Disable', 'Disabled'],
       "C6 Mode": ['Disable', 'Disabled'],
       "DF Cstates": ['Disable', 'Disabled'],
       "ACPI _CST C1 Declaration": ['Disable', 'Disabled'],
       "SB C1E Support": ['Disable', 'Disabled'],
       "AMD Cool&Quiet function": ['Disable', 'Disabled'],
       "PSS Support": ['Disable', 'Disabled'],
    },

    "Disable SMT": {
    "SMT Control": ['Disable', 'Disabled'],
    "SMT Mode": ['Disable', 'Disabled'],
    "SMT": ['Disable', 'Disabled'],
    },

    "Disable Gating": {
        "Clock Power Management(CLKREQ#)": ['Disable', 'Disabled'],
        "Unused GPP Clocks Off": ['Disable', 'Disabled'],
        "AB Clock Gating": ['Disable', 'Disabled'],
        "ACP Power Gating": ['Disable', 'Disabled'],
        "ACP CLock Gating": ['Disable', 'Disabled'],
        "PCIB Clock Run": ['Disable', 'Disabled'],
    },

    "Disable Sleep/Standby states": {
       "ACPI Sleep State": ["Disabled", "Disable", "0"],
       "Aggresive SATA Device Sleep Port 0": ["Disabled", "Disable", "0"],
       "Aggresive SATA Device Sleep Port 1": ["Disabled", "Disable", "0"],
       "S3/Modern Standby Support": ["Disabled", "Disable", "0"],
       "ACPI Standby State": ["Disabled", "Disable", "0"],
       "S0I3": ["Disabled", "Disable", "0"],
       "Adaptive S4": ["Disabled", "Disable", "0"],
    },


    "PCIe & Link Power Management": {
        "ASPM Support": ['Disable', 'Disabled'],
        "CPU PCIE ASPM Mode Control": ['Disable', 'Disabled'],
        "ASPM Control for CPU": ['Disable', 'Disabled'],
        "PM L1 SS": ['Disable', 'Disabled'],
        "Aggressive Link PM Capability": ['Disable', 'Disabled'],
        "LCLK DPM": ['Disable', 'Disabled'],
        "LCLK DPM Enhanced PCIe Detection": ['Disable', 'Disabled'],
        "USB Phy Power Down": ['Disable', 'Disabled'],
        "Adaptive S4": ['Disable', 'Disabled'],
        "S0I3": ['Disable', 'Disabled'],
        "EPU Power Saving Mode": ['Disable', 'Disabled'],
        "ECO Mode": ['Disable', 'Disabled'],
        "Power Down Enable": ['Disable', 'Disabled'],
        "D3 Cold Support": ['Disable', 'Disabled'],
        "D3Cold Support": ['Disable', 'Disabled']
    },

    "SATA Power Management": {
        "SATA Partial State Capability": ['Disable', 'Disabled'],
        "SATA Slumber State Capability": ['Disable', 'Disabled'],
        "Aggresive SATA Device Sleep Port 0": ['Disable', 'Disabled'],
        "Aggresive SATA Device Sleep Port 1": ['Disable', 'Disabled'],
        "Socket1 DevSlp0 Enable": ['Disable', 'Disabled'],
        "Socket1 DevSlp1 Enable": ['Disable', 'Disabled']
    },

    "Disable Security And Virtualization": {
        "IOMMU": ['Disable', 'Disabled'],
        "SVM Mode": ['Disable', 'Disabled'],
        "TSME": ['Disable', 'Disabled'],
        "SMEE": ['Disable', 'Disabled'],
        "PPIN Opt-in": ['Disable', 'Disabled'],
        "Indirect Branch Prediction Speculation": ['Disable', 'Disabled'],
        "DMA Protection": ['Disable', 'Disabled'],
        "DMAr Support": ['Disable', 'Disabled'],
        "BME DMA Mitigation": ['Disable', 'Disabled'],
        "NX Mode": ['Disable', 'Disabled'],
        "Security Device Support": ['Disable', 'Disabled'],
        "CC6 memory region encryption": ['Disable', 'Disabled'],
        "GMI encryption control": ['Disable', 'Disabled'],
        "xGMI encryption control": ['Disable', 'Disabled'],
        "Data Scramble": ['Disable', 'Disabled']
    },

    "Disable Legacy and port functions ": {
        "CSM": ['Disable', 'Disabled'],
        "Legacy USB Support": ['Disable', 'Disabled'],
        "XHCI Hand-off": ['Disable', 'Disabled'],
        "EHCI Hand-off": ['Disable', 'Disabled'],
        "PS2 Devices Support": ['Disable', 'Disabled'],
        "Parallel Port": ['Disable', 'Disabled'],
        "Isochronous Support": ['Disable', 'Disabled'],
        "3DMark01 Enhancement": ['Disable', 'Disabled'],
        "ESPI Enable": ['Disable', 'Disabled'],
        "Thunderbolt Support": ['Enable', 'Enabled']
    },

    "Disable Onboard Device Features": {
        "Discrete GPU's Audio": ['Disable', 'Disabled'],
        "Onboard PCIE LAN PXE ROM": ['Disable', 'Disabled'],
        "Network Stack Driver Support": ['Disable', 'Disabled'],
        "Wake on LAN": ['Disable', 'Disabled'],
        "LAN Power Enable": ['Disable', 'Disabled'],
        "Onboard LED": ['Disable', 'Disabled'],
        "RGB Fusion": ['Disable', 'Disabled'],
        "Thunderbolt Support": ['Disable', 'Disabled'],
        "I2C 1 Enable": ['Disable', 'Disabled'],
        "I2C 2 Enable": ['Disable', 'Disabled'],
        "I2C 3 Enable": ['Disable', 'Disabled'],
        "I2C 4 Enable": ['Disable', 'Disabled'],
        "I2C 5 Enable": ['Disable', 'Disabled'],
        "eMMC Boot": ['Disable', 'Disabled'],
        "eMMC/SD Configure": ['Disable', 'Disabled'],
        "ESPI Enable": ['Disable', 'Disabled']
    },

    "Disable Prefetchers And Instruction Handling": {
        "L1 Stream HW Prefetcher": ['Enable', 'Enabled'],
        "L2 Stream HW Prefetcher": ['Enable', 'Enabled'],
        "Streaming Stores Control": ['Disable', 'Disabled'],
        "Opcache Control": ['Disable', 'Disabled'],
        "Fast Short REP MOVSB": ['Enable', 'Enabled'],
        "Enhanced REP MOVSB/STOSB": ['Enable', 'Enabled'],
        "REP-MOV/STOS Streaming": ['Enable', 'Enabled']
    },

    "Disable Memory Error Detection": {
        "DRAM ECC Enable": ['Disable', 'Disabled'],
        "Data Poisoning": ['Disable', 'Disabled'],
        "DRAM scrub time": ['Disable', 'Disabled'],
        "Poison scrubber control": ['Disable', 'Disabled'],
        "Redirect scrubber control": ['Disable', 'Disabled'],
        "RCD Parity": ['Disable', 'Disabled'],
        "Write CRC Enable": ['Disable', 'Disabled'],
        "DRAM Write CRC Enable and Retry Limit": ['Disable', 'Disabled'],
        "DRAM Address Command Parity Retry": ['Disable', 'Disabled'],
        "DRAM UECC Retry": ['Disable', 'Disabled'],
        "DRAM Post Package Repair": ['Enable', 'Enabled']
    },

    "Enable Memory Performance settings": {
        "Command Rate": ['1T'],
        "DRAM Latency Enhance": ['Enable', 'Enabled'],
        "SPD Read Optimization": ['Enable', 'Enabled'],
        "FFE Write Training": ['Enable', 'Enabled'],
        "DFE Read Training": ['Enable', 'Enabled']
    },

    "Memory Organization and address mapping": {
        "BankGroupSwap": ['Disable', 'Disabled'],
        "BankGroupSwapAlt": ['Enable', 'Enabled'],
        "Address Hash Bank": ['Disable', 'Disabled'],
        "Address Hash CS": ['Disable', 'Disabled'],
        "Address Hash Rm": ['Disable', 'Disabled'],
        "Memory interleaving size": ['1 KB'],
        "DRAM map inversion": ['Enable', 'Enabled'],
        "Data Scramble": ['Disable', 'Disabled'],
        "Periodic Directory Rinse": ['Disable', 'Disabled'],
        "ACPI SRAT L3 Cache As NUMA Domain": ['Enable', 'Enabled']
    },

    "Enable Re-Size BAR": {
        "Re-Size BAR Support": ['Enable', 'Enabled'],
        "Above 4G Decoding": ['Enable', 'Enabled']
    },

    "Optimize PCIe for Performance": {
        "Above 4G Decoding": ['Enable', 'Enabled'],
        "PCIe Ten Bit Tag Support": ['Enable', 'Enabled'],
        "SRIS": ['Enable', 'Enabled'],
        "_OSC For PCI0": ['Disable', 'Disabled'],
        "Extended Tag": ['Enable', 'Enabled'],
        "Link Training Retry": ['Disable', 'Disabled']
    },

    "Optimize xGMI": {
        "xGMI Force Link Width": ['2'],
        "xGMI Force Link Width Control": ['Enable', 'Enabled'],
        "xGMI Max Link Width": ['1'],
        "xGMI Max Link Width Control": ['Disable', 'Disabled'],
        "xGMI Link Width Control": ['Disable', 'Disabled'],
        "3-link xGMI max speed": ['25Gbps'],
        "4-link xGMI max speed": ['25Gbps']
    },

    "Disable Network PXE & Protocols": {
        "Network Stack Driver Support": ['Disable', 'Disabled'],
        "Onboard PCIE LAN PXE ROM": ['Disable', 'Disabled'],
        "Ipv4 PXE Support": ['Disable', 'Disabled'],
        "Ipv6 PXE Support": ['Disable', 'Disabled'],
        "IPv4 HTTP Support": ['Disable', 'Disabled'],
        "IPv6 HTTP Support": ['Disable', 'Disabled']
    },

    "Disable Spread Spectrum": {
        "Spread Spectrum": ['Disable', 'Disabled'],
        "Int. Clk Differential Spread": ['Disable', 'Disabled'],
        "SB Clock Spread Spectrum Option": ['-0.362%']
    },

    "Enable SoC/Uncore OC Mode": {
        "SoC/Uncore OC Mode": ['Enable', 'Enabled']
    },

    "Disable Determinism Control": {
        "Determinism Control": ['Disable', 'Disabled'],
        "Determinism Slider": ['Enable', 'Enabled']
    },

    "Disable Error Reporting & Handling": {
        "Platform First Error Handling": ['Disable', 'Disabled'],
        "Enable AER Cap": ['Disable', 'Disabled'],
        "Freeze DF module queues on error": ['Disable', 'Disabled'],
        "NBIO RAS Control": ['Disable', 'Disabled'],
        "NBIO RAS Global Control": ['Disable', 'Disabled'],
        "Sata RAS Support": ['Disable', 'Disabled'],
        "ALink RAS Support": ['Disable', 'Disabled'],
        "MCA error thresh enable": ['Disable', 'Disabled'],
        "NBIO SyncFlood Generation": ['Disable', 'Disabled'],
        "NBIO SyncFlood Reporting": ['Disable', 'Disabled'],
        "Disable DF to external downstream IP SyncFloodPropagation": ['Disable', 'Disabled'],
        "Disable DF sync flood propagation": ['Disable', 'Disabled'],
        "NBIO Poison Consumption": ['Disable', 'Disabled'],
        "Log Poison Data from SLINK": ['Disable', 'Disabled']
    },

    "Disable Debugging and Diagnostics": {
        "Core Watchdog Timer Enable": ['Disable', 'Disabled'],
        "PSP error injection support": ['Disable', 'Disabled'],
        "SMU and PSP Debug Mode": ['Disable', 'Disabled'],
        "Debug Port Table": ['Disable', 'Disabled'],
        "Debug Port Table 2": ['Disable', 'Disabled'],
        "GPP Serial Debug Bus Enable": ['Disable', 'Disabled'],
        "Edpc Control": ['Disable', 'Disabled'],
        "USB ecc SMI Enable": ['Disable', 'Disabled'],
        "System probe filter": ['Enable', 'Enabled'],
        "CRB test": ['Disable', 'Disabled'],
        "CV test": ['Disable', 'Disabled'],
        "Loopback Mode": ['Disable', 'Disabled']
    },

    "Disable System Warnings": {
        "CPU Fan Fail Warning Control": ['Disable', 'Disabled'],
        "CPU temperature Warning Control": ['Disable', 'Disabled'],
        "POST Beep": ['Disable', 'Disabled']
    },

    "Optimize SPI Speed": {
        "SPI 100MHz Support": ['Enable', 'Enabled'],
        "SPI Fast Read Speed": ['100MHz'],
        "SPI Read Mode": ['Fast Read']}
}


INTEL_PRESETS_ADV: Dict[str, Dict[str, Any]] = {

    "Disable C-States": {
        "CPU C-States": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "C-States Control": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Intel C-State": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "C states": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Enhanced C-states": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Package C State Limit": ['C0/C1'],
        "Package C State limit": ['C0/C1'],
        "C0 State Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "C1 State Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CPU Enhanced Halt(C1E)": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CPU Enhanced Halt": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "C2 State Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "C3 State Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CPU C6 State Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CPU C7 State Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "C6/C7 State Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "C8 State Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "C10 State Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "C-State Auto Demotion": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "C-State Un-demotion": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Package C-State Demotion": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Package C-State Un-demotion": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "C-state Pre-Wake": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CState Pre-Wake": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "CPU Powersavings": {
        "AP threads Idle Manner": ['RUN Loop'],
        "Boot Performance Mode": ['Turbo Performance'],
        "Boot performance mode": ['Turbo Performance'],
        "Race To Halt (RTH)": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Race to Halt": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "MonitorMWait": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Timed MWAIT": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Dual Tau Boost": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "EIST": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Intel(R) SpeedShift Technology": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Intel Speed-Shift Technology": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Intel(R) SpeedShift Technology Interrupt Control": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Intel(R) SpeedStep(tm)": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Intel(R) Turbo Boost Max Technology 3.0": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Energy Efficient P-State": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Energy Efficient Turbo": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Energy Performance Gain": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "HwP Lock": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "HwP Autonomous Per Core P State": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "HwP Autonomous EPP Grouping": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "P-state Capping": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Per Core P state OS control mode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Per Core P state os control mode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Hardware Prefetcher": ['Enabled','Enable']    
    },
    "Disable Thermal Settings": {
        "Bi-Directional PROCHOT": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Bi-directional PROCHOT#": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PROCHOT Lock": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PROCHOT Response": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Disable PROCHOT# Output": ['Enable', 'Enabled'],
        "CPU Thermal Monitor": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Thermal Monitor": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Enable All Thermal Functions": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Thermal Throttling Level": ['Manual'],
        "Active Trip Point 0": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Active Trip Point 1": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Active Trip Points": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Passive Trip Point": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Critical Trip Points": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Tcc Activation Offset": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Tcc Offset Time Window": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Tcc Offset Clamp Enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Tcc Offset Lock Enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PECI": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable Voltage / Overclocking Limits": {
        "FLL OC mode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "BCLK Aware Adaptive Voltage": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Overclocking Lock": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Ring Down Bin": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "IA ICC Unlimited Mode": ['Enable','Enabled'],
        "GT ICC Unlimited Mode": ['Enable','Enabled'],
        "IA CEP Enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "GT CEP Enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Thermal Velocity Boost": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Enhanced Thermal Velocity Boost": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Enhanced TVB": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "TVB Ratio Clipping": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "TVB Ratio Clipping Enhanced": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "TVB Voltage Optimizations": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "UnderVolt Protection": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Disable VR Thermal Alert": ['Enable', 'Enabled'],
        "Core VR Fast Vmode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "GT VR Fast Vmode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "SA VR Fast Vmode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "FIVR Spread Spectrum": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Tune Memory Settings": {
        "DDR PowerDown and idle counter": ['PCODE'],
        "For LPDDR Only DDR PowerDown and idle counter": ['PCODE'],
        "For LPDDR Only: DDR PowerDown and idle counter": ['PCODE'],
        "PowerDown Energy Ch0Dimm0": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PowerDown Energy Ch0Dimm1": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PowerDown Energy Ch1Dimm0": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PowerDown Energy Ch1Dimm1": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Power Down Mode": ['No Power Down'],
        "SA GV": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "For LPDDR Only Throttler CKEMin Defeature": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "For LPDDR Only: Throttler CKEMin Defeature": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Throttler CKEMin Defeature": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Dynamic Memory Boost": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Dynamic Memory Performance Boost": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Fine Granularity Refresh mode": ['Enabled','Enable'],
        "SelfRefresh IdleTimer": ['65535'],
        "Page Close Idle Timeout": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "EPG DIMM Idd3N": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "EPG DIMM Idd3P": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Enable PCI Delay Optimization": {
        "PCI Delay Optimization": ['Enabled', 'Enable'],
    },
    "Disable Snoop": {
        "Non Snoop Latency Value": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        "Snoop Latency Value": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled'],
        "Non Snoop Latency Override": ['Manual', 'Enabled', 'Enable'],
        "Snoop Latency Override": ['Manual', 'Enabled', 'Enable'],
        "Non Snoop Latency Multiplier": '1 ns',
        "Snoop Latency Multiplier": '1 ns'
    },
    "Disable Hyper Threading" : {
        "Hyper-Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
        "Hyper Threading": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
        "Hyper-Threading Technology": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'Ignore'],
    },
    "Disable ClkReq" : {
        "Enable ClockRqe Messaging": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock0": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock1": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock2": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock3": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock4": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock5": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock6": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock7": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock8": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock9": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock10": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock11": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock12": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock13": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock14": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock15": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock16": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
        "ClkReq for Clock17": ['0', 'Disable', 'Disabled', 'No Constraint', 'Suspend Disabled', 'OFF', 'Off'],
    },
    "Frequency Settings": {
        "FCLK Frequency for Early Power On": ['1GHz'],
        "SA PLL Frequency": ['3200MHz','3200 MHz'],
        "SA PLL Frequency Override": ['3200MHz','3200 MHz']
    },
    "PCIe Management": {
        "ASPM": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "DMI ASPM": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "DMI Gen3 ASPM": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "DMI Link ASPM Control": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Native ASPM": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PCH ASPM": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEG ASPM": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "L1 Low": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "L1 Substates": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable Gating": {
        "PCI Express Power Gating": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PCI Express Clock Gating": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PCIE Clock Gating": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Power Gating": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Clock Gating": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Enable 8254 Clock Gate": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "JTAG C10 Power Gate": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "LPM S0i2.0USB2PHY Sus Well Power Gating": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "USB2PHY Sus Well Power Gating": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "SB2PHY Sus Well Power Gating": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Max Power Savings Mode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "OS IDLE Mode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Power Loss Notification Feature": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "LPMode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "D3 Setting for Storage": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Legacy IO Low Latency": ['Enabled','Enable']
    },
    "Disable Spread Spectrum": {
        "Spread Spectrum": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "RFI Mitigation": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "DLVR RFI Mitigation": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable Sleep States": {
        "ACPI Sleep State": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "ACPI Standby State": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "ACPI D3 Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "ACPI D3Cold Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "ACPI T-States": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Deep Sleep": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Enable Hibernation": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Low Power S0 Idle Capability": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "S0i": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "S0ix Auto Demotion": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable WakeOn": {
        "Wake On WiGig": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "LAN Wake From DeepSx": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Wake on LAN Enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Wake on WLAN and BT Enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "DeepSx Wake on WLAN and BT Enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Wake On Touch": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Wake From Thunderbolt(TM) Devices": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "WoV (Wake on Voice)": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Foxville I225 Wake on LAN Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable Security": {
        "Total Memory Encryption": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "AES": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "ASF Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "BME DMA Mitigation": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Disable TBT PCIE Tree BME": ['Enable', 'Enabled'],
        "PTID Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Enable Remote Platform Erase Feature": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Remote Platform Erase Feature": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable TPM & Secure Boot": {
        "Secure Boot": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Secure Boot Mode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "SECURE BOOT": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "TPM State": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Intel Platform Trust Technology (PTT)": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Intel Platform Trust Technology": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Intel Trusted Execution Technology": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable Virtualization": {
        "Intel (VMX) Virtualization Technology": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "VT-d": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Control Iommu Pre-boot Behavior": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "IGD VTD": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "IGD VTD Enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "IOP VTD": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "IOP VTD Enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "IPU VTD": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "IPU VTD Enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable Error Handling": {
        "MachineCheck": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CPU CrashLog": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Cpu CrashLog (Device 10)": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CrashLog Cdie Rearm": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CrashLog Feature": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CrashLog On All Reset": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CrashLog PMC Clear": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CrashLog PMC Rearm": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CrashLog enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Advanced Error Reporting": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "CER": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "FER": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "NFER": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "DPC": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "EDPC": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Processor trace": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PCH Trace Hub Enable Mode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "SMART Self Test": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Three Strike Counter": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable PCH Settings": {
        "PCH Cross Throttling": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PCH Energy Reporting": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PCH Temp Read": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "DMI Thermal Setting": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Tune EC Settings": {
        "EC CS Debug Light": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "EC CS Debug Ligh": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "EC Low Power Mode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "EC Notification": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "EC Polling Period": ['255']
    },
    "Disable Audio": {
        "HD Audio Enable": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "NB Azalia": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Audio Controller": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "HDA Link": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "USB Audio Offload": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "HD Audio Controller": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Onboard HDMI HD Audio": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "Onboard HD Audio": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "HD Audio": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable RGB": {
        "RGB Fusion": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "RGB Light": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable PEP": {
        "PEP Audio": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP CPU": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP CSME": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP GNA": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP Graphics": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP HECI3": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP I2C0": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP I2C1": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP I2C2": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP I2C3": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP I2C4": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP I2C5": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP I2C6": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP I2C7": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP IPU": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP LAN(GBE)": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP PCIe GFX": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP PCIe LAN": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP PCIe Other": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP PCIe Storage": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP SATA": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP SPI": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP THC0": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP THC1": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP TCSS": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP UART": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP VMD": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP WLAN": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP XHCI": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP enumerated SATA ports": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PEP EMMC": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    },
    "Disable Legacy": {
        "Legacy Game Compatibility Mode": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PS2 Devices Support": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "PS2 Keyboard and mouse": ['0','Disable','Disabled','No Constraint','Suspend Disabled'],
        "XHCI Hand-off": ['0','Disable','Disabled','No Constraint','Suspend Disabled']
    }

}


# --------------------------------------------------------------------------------------
# Parsing utilities
# --------------------------------------------------------------------------------------
SETUP_Q_RE = re.compile(r"^\s*Setup\s+Question\s*=\s*(.+?)\s*$", re.IGNORECASE)
HELP_STR_RE = re.compile(r"^\s*Help\s+String\s*=\s*(.+?)\s*$", re.IGNORECASE)
OPTIONS_START_RE = re.compile(r"^\s*Options\s*=", re.IGNORECASE)
OPTION_LINE_RE = re.compile(r"^\s*(\*)?\s*\[\s*([0-9A-Fa-f]{2})\s*]\s*(.*?)\s*(?://.*)?\s*$")
VALUE_LINE_RE = re.compile(r"^\s*Value\s*=\s*(?:<\s*)?([0-9A-Fa-fx]+)(?:\s*>)?\s*(?://.*)?$", re.IGNORECASE)
RANGE_HINT_RE = re.compile(r"(\d+)\s*-\s*(\d+)")

BOOL_TRUE = {"enabled", "enable", "on", "true", "yes", "1"}
BOOL_FALSE = {"disabled", "disable", "off", "false", "no", "0"}


class SettingKind(Enum):
    OPTIONS = auto()
    VALUE = auto()


@dataclass
class Setting:
    name: str
    kind: SettingKind
    block_lines: List[str]
    options: List[Tuple[str, str]] = field(default_factory=list)
    current_index: int = 0
    value: Optional[str] = None
    value_min: Optional[int] = None
    value_max: Optional[int] = None
    value_has_brackets: bool = True
    _orig_index: int = field(init=False, default=0)
    _orig_value: Optional[str] = field(init=False, default=None)

    def __post_init__(self) -> None:
        if self.kind is SettingKind.OPTIONS:
            self.current_index = (
                max(0, min(self.current_index, len(self.options) - 1))
                if self.options else 0
            )
        self._orig_index = self.current_index
        self._orig_value = self.value

    @property
    def current_label(self) -> str:
        if self.kind is SettingKind.OPTIONS:
            return self.options[self.current_index][1] if self.options else ""
        return str(self.value or "")

    def set_current_by_label(self, label: str) -> bool:
        if self.kind is not SettingKind.OPTIONS:
            return False
        t = label.strip().lower()
        if t in BOOL_TRUE:
            t = "enabled"
        if t in BOOL_FALSE:
            t = "disabled"
        for i, (_, lab) in enumerate(self.options):
            normalized = lab.strip().lower()
            if normalized in BOOL_TRUE:
                normalized = "enabled"
            if normalized in BOOL_FALSE:
                normalized = "disabled"
            if normalized == t or lab.strip().lower() == t:
                if i == self.current_index:
                    return False
                self.current_index = i
                return True
        return False

    def set_current_by_code(self, code: str) -> bool:
        if self.kind is not SettingKind.OPTIONS:
            return False
        for i, (c, _) in enumerate(self.options):
            if c.lower() == str(code).lower():
                if i == self.current_index:
                    return False
                self.current_index = i
                return True
        return False

    def set_value(self, new_val: Union[int, str]) -> bool:
        if self.kind is not SettingKind.VALUE:
            return False
        s = str(new_val).strip()
        try:
            if s.lower().startswith("0x") or re.fullmatch(r"[0-9A-Fa-f]+", s):
                int(s.replace("0x", ""), 16)
                if re.fullmatch(r"[0-9A-Fa-f]+", s):
                    s = s.upper()
            else:
                iv = int(s, 10)
                if self.value_min is not None:
                    iv = max(iv, self.value_min)
                if self.value_max is not None:
                    iv = min(iv, self.value_max)
                s = str(iv)
        except Exception:
            return False
        if s == (self.value or ""):
            return False
        self.value = s
        return True


def _collect_block(lines: List[str], start: int) -> Tuple[List[str], int]:
    blk = [lines[start]]
    i = start + 1
    while i < len(lines):
        if SETUP_Q_RE.match(lines[i]):
            break
        blk.append(lines[i])
        i += 1
    return blk, i


def _parse_range_hint(block_lines: List[str]) -> Tuple[Optional[int], Optional[int]]:
    for ln in block_lines:
        m = HELP_STR_RE.match(ln)
        if not m:
            continue
        r = RANGE_HINT_RE.search(m.group(1))
        if r:
            a, b = int(r.group(1)), int(r.group(2))
            if a <= b:
                return a, b
    return None, None


def _parse_inline_option_tail(tail: str) -> Optional[Tuple[bool, str, str]]:
    t = tail.strip()
    if not t:
        return None
    m = OPTION_LINE_RE.match(t)
    if not m:
        return None
    return (m.group(1) is not None, m.group(2).strip(), m.group(3).strip())


def parse_scewin_nvram(text: str) -> List[Setting]:
    lines = text.splitlines()
    i = 0
    out: List[Setting] = []

    while i < len(lines):
        mq = SETUP_Q_RE.match(lines[i])
        if not mq:
            i += 1
            continue

        name = mq.group(1).strip()
        block, i = _collect_block(lines, i)

        value_str: Optional[str] = None
        value_has_brackets = True
        for ln in block:
            mv = VALUE_LINE_RE.match(ln)
            if mv:
                value_str = mv.group(1).strip()
                value_has_brackets = "<" in ln and ">" in ln
                break

        opts: List[Tuple[str, str]] = []
        current_index = 0
        saw_opts = False
        j = 0
        while j < len(block):
            ln = block[j]
            ms = OPTIONS_START_RE.match(ln)
            if not ms:
                j += 1
                continue
            saw_opts = True

            parts = ln.split("=", 1)
            tail = parts[1] if len(parts) == 2 else ""
            parsed = _parse_inline_option_tail(tail)
            if parsed:
                code = parsed[1]
                label = parsed[2]
                star = "*" if current_index == 0 else ""
                opts.append((code, label))
                if star:
                    current_index = 0
                j += 1
                while j < len(block):
                    om = OPTION_LINE_RE.match(block[j])
                    if not om:
                        break
                    is_cur = om.group(1) is not None
                    code = om.group(2).strip()
                    label = om.group(3).strip()
                    if is_cur:
                        current_index = len(opts)
                    opts.append((code, label))
                    j += 1
                break

            j += 1

        if saw_opts and opts:
            out.append(Setting(name, SettingKind.OPTIONS, block, opts, current_index))
        elif value_str is not None:
            vmin, vmax = _parse_range_hint(block)
            out.append(
                Setting(
                    name,
                    SettingKind.VALUE,
                    block,
                    value=value_str,
                    value_min=vmin,
                    value_max=vmax,
                    value_has_brackets=value_has_brackets,
                )
            )
        else:
            out.append(Setting(name, SettingKind.VALUE, block, value=""))

    return out


# --------------------------------------------------------------------------------------
# Rewrite (only changed settings)
# --------------------------------------------------------------------------------------
HEADER_TEMPLATE = """\
// Script File Name : {fname}
// Created on {date} at {time}
// AMISCE Utility. Ver 5.05.01.0002
// Copyright (c) 2021 AMI. All rights reserved.
HIICrc32= CC76FA3

"""  # <-- trailing blank line kept

def rewrite_block_with_change(s: Setting) -> List[str]:
    blk = s.block_lines[:]

    if s.kind is SettingKind.OPTIONS:
        out: List[str] = []
        option_idx = -1
        in_opts = False
        for ln in blk:
            if OPTIONS_START_RE.match(ln):
                parts = ln.split("=", 1)
                if len(parts) == 2:
                    head, tail = parts[0], parts[1]
                    parsed = _parse_inline_option_tail(tail)
                    if parsed:
                        option_idx = 0
                        code = parsed[1]
                        label = parsed[2]
                        star = "*" if s.current_index == 0 else ""
                        out.append(f"{head}= {star}[{code}]{label}")
                        in_opts = True
                        continue
                out.append(ln)
                in_opts = True
                continue

            if in_opts:
                om = OPTION_LINE_RE.match(ln)
                if not om:
                    out.append(ln)
                    in_opts = False
                    continue
                option_idx += 1
                code = om.group(2).strip()
                label = om.group(3).rstrip()
                star = "*" if option_idx == s.current_index else ""
                indent = ln[: len(ln) - len(ln.lstrip())] or " "
                out.append(f"{indent}{star}[{code}]{label}")
                continue

            out.append(ln)
        return out

    out = []
    for ln in blk:
        if VALUE_LINE_RE.match(ln):
            indent = ln[: len(ln) - len(ln.lstrip())]
            out.append(f"{indent}Value =<{s.value}>" if s.value_has_brackets else f"{indent}Value ={s.value}")
        else:
            out.append(ln)
    return out


# --------------------------------------------------------------------------------------
# Qt Model
# --------------------------------------------------------------------------------------
class SettingsModel(QAbstractTableModel):
    HEADERS = ["Setting", "Current", "Options", "State"]
    stagedChanged = Signal()

    def __init__(self, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self._rows: List[Setting] = []
        self._staged: set[int] = set()
        self._applied: set[int] = set()
        # Performance optimization: cache for data lookups
        self._data_cache: Dict[Tuple[int, int, int], Any] = {}

    def load(self, settings: List[Setting]) -> None:
        self.beginResetModel()
        self._rows = settings
        self._staged.clear()
        self._applied.clear()
        self._data_cache.clear()  # Clear cache on load
        self.endResetModel()
        self.stagedChanged.emit()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return 4

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):  # type: ignore[override]
        if not index.isValid():
            return None

        row = index.row()
        c = index.column()

        # Fast path: use cache for frequently accessed display data
        if role == Qt.DisplayRole and c in (0, 2):
            cache_key = (row, c, role)
            if cache_key in self._data_cache:
                return self._data_cache[cache_key]

        s = self._rows[row]

        if role in (Qt.DisplayRole, Qt.EditRole):
            if c == 0:
                cache_key = (row, c, Qt.DisplayRole)
                self._data_cache[cache_key] = s.name
                return s.name
            if c == 1:
                return s.current_label
            if c == 2:
                cache_key = (row, c, Qt.DisplayRole)
                if s.kind is SettingKind.OPTIONS:
                    result = ", ".join([lab for _, lab in s.options])
                else:
                    rng: List[str] = []
                    if s.value_min is not None:
                        rng.append(str(s.value_min))
                    if s.value_max is not None:
                        rng.append(str(s.value_max))
                    result = "Value" + (f" ({'-'.join(rng)})" if rng else "")
                self._data_cache[cache_key] = result
                return result
            if c == 3:
                is_original = (
                    (s.kind is SettingKind.OPTIONS and s.current_index == s._orig_index)
                    or (s.kind is SettingKind.VALUE and (s.value or "") == (s._orig_value or ""))
                )
                return "Original" if is_original else "Edited"

        if role == Qt.ForegroundRole and c == 3:
            is_original = (
                (s.kind is SettingKind.OPTIONS and s.current_index == s._orig_index)
                or (s.kind is SettingKind.VALUE and (s.value or "") == (s._orig_value or ""))
            )
            if not is_original:
                return QtGui.QBrush(QtGui.QColor(THEME["warn"]))

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):  # type: ignore[override]
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return str(section + 1)

    def flags(self, index: QModelIndex):  # type: ignore[override]
        if not index.isValid():
            return Qt.ItemIsEnabled
        base = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() == 1:
            base |= Qt.ItemIsEditable
        return base

    def _update_sets_after_edit(self, row: int) -> None:
        s = self._rows[row]
        is_original = (
            (s.kind is SettingKind.OPTIONS and s.current_index == s._orig_index)
            or (s.kind is SettingKind.VALUE and (s.value or "") == (s._orig_value or ""))
        )
        if is_original:
            self._staged.discard(row)
            self._applied.discard(row)
        else:
            self._staged.add(row)

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:  # type: ignore[override]
        if not index.isValid() or index.column() != 1 or role != Qt.EditRole:
            return False
        row = index.row()
        s = self._rows[row]
        before = s.current_label
        changed = (
            s.set_current_by_label(str(value))
            or s.set_current_by_code(str(value))
            if s.kind is SettingKind.OPTIONS
            else s.set_value(value)
        )
        after = s.current_label
        if not changed and before == after:
            return False
        self._update_sets_after_edit(row)
        # Clear cache for affected cells
        self._invalidate_cache_for_row(row)
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        self.dataChanged.emit(self.index(row, 3), self.index(row, 3), [Qt.DisplayRole])
        self.stagedChanged.emit()
        return True

    def apply_staged(self) -> int:
        cnt = len(self._staged)
        self._applied.update(self._staged)
        self._staged.clear()
        if self.rowCount() > 0:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(self.rowCount() - 1, self.columnCount() - 1),
                [Qt.DisplayRole],
            )
        self.stagedChanged.emit()
        return cnt

    def get_counts(self) -> Tuple[int, int]:
        edited = 0
        for s in self._rows:
            if (
                (s.kind is SettingKind.OPTIONS and s.current_index != s._orig_index)
                or (s.kind is SettingKind.VALUE and (s.value or "") != (s._orig_value or ""))
            ):
                edited += 1
        return edited, len(self._applied)

    def modified_rows(self) -> List[int]:
        return [
            i
            for i, s in enumerate(self._rows)
            if (
                (s.kind is SettingKind.OPTIONS and s.current_index != s._orig_index)
                or (s.kind is SettingKind.VALUE and (s.value or "") != (s._orig_value or ""))
            )
        ]

    def rows_matching_names(self, names_lower: set[str]) -> List[int]:
        return [i for i, s in enumerate(self._rows) if s.name.strip().lower() in names_lower]

    def _disabled_index_for(self, s: Setting) -> Optional[int]:
        if s.kind is not SettingKind.OPTIONS or not s.options:
            return None
        best = None
        for i, (code, lab) in enumerate(s.options):
            L = lab.lower()
            if "disable" in L or L.strip() in {"disabled", "off", "false"}:
                return i
            if code.strip().lower() == "00":
                best = i
        return best if best is not None else 0
    def _invalidate_cache_for_row(self, row: int) -> None:
        """Clear cache entries for a specific row to ensure fresh data."""
        keys_to_remove = [k for k in self._data_cache.keys() if k[0] == row]
        for key in keys_to_remove:
            del self._data_cache[key]


# -------- Proxy to filter by exact name set --------
class NameSetProxy(QtCore.QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self._names: Optional[set[str]] = None

    def setNameSet(self, names: Optional[set[str]]):
        self._names = {n.strip().lower() for n in names} if names else None
        self.invalidateFilter()

    def filterAcceptsRow(self, r: int, p: QModelIndex) -> bool:  # type: ignore[override]
        if not self._names:
            return False
        m: SettingsModel = self.sourceModel()  # type: ignore[assignment]
        name = (m.index(r, 0, p).data() or "").strip().lower()
        return name in self._names


# --------------------------------------------------------------------------------------
# Delegate: combo or line edit
# --------------------------------------------------------------------------------------
class ComboOrLineDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._editing_index = None

    def paint(self, painter, option, index):
        # Don't paint the text if we're currently editing this cell
        if index.column() == 1 and self._editing_index == index:
            # Just paint the background/selection, not the text
            self.initStyleOption(option, index)
            option.text = ""  # Clear text so it doesn't show under editor
            QtWidgets.QApplication.style().drawControl(
                QtWidgets.QStyle.CE_ItemViewItem, option, painter
            )
        else:
            super().paint(painter, option, index)

    def _style_line(self, w: QtWidgets.QWidget) -> None:
        w.setStyleSheet(
            f"""
            QLineEdit{{
                background:transparent;
                border:none;
                padding:2px 4px;
                color:{THEME['text']};
                font-size:14px;
                font-weight:500;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                selection-background-color:{THEME['accent']};
                selection-color:#ffffff;
            }}
            """
        )

    def _style_combo(self, cb: QtWidgets.QComboBox) -> None:
        cb.setView(QtWidgets.QListView())
        cb.view().setUniformItemSizes(True)
        cb.setMaxVisibleItems(30)
        cb.setFocusPolicy(Qt.StrongFocus)
        cb.setStyleSheet(
            f"""
            QComboBox{{
                background:{THEME['input_bg']};
                border:1px solid transparent;
                border-radius:4px;
                padding:6px 24px 6px 10px;
                color:{THEME['text']};
                font-size:14px;
            }}
            QComboBox:hover{{
                background:{THEME['card']};
                border:1px solid {THEME['input_focus']};
            }}
            QComboBox::drop-down{{border:0;width:20px;}}
            QComboBox QAbstractItemView{{
                background:{THEME['card']};
                border:1px solid {THEME['input_border']};
                border-radius:8px;
                selection-background-color:{THEME['accent']};
                selection-color:#ffffff;
                outline:0;
            }}
            QComboBox QAbstractItemView::item{{padding:8px;border-radius:4px;}}
            QComboBox QAbstractItemView::item:hover{{background:{THEME['card_hover']};}}
            QComboBox QAbstractItemView::item:selected{{background:{THEME['accent']};color:#ffffff;}}
            """
        )

    def createEditor(self, parent, option, index):  # type: ignore[override]
        if index.column() != 1:
            return super().createEditor(parent, option, index)

        model = index.model()
        pindex = QPersistentModelIndex(index)
        setter = lambda val: model.setData(pindex, val, Qt.EditRole)

        src_row = model.mapToSource(index).row() if isinstance(model, QtCore.QSortFilterProxyModel) else index.row()
        src_model: SettingsModel = model.sourceModel() if isinstance(model, QtCore.QSortFilterProxyModel) else model  # type: ignore[assignment]
        s: Setting = src_model._rows[src_row]

        if s.kind is SettingKind.OPTIONS:
            cb = QtWidgets.QComboBox(parent)
            self._style_combo(cb)
            cb.addItems([lab for _, lab in s.options])
            QtCore.QTimer.singleShot(30, lambda: (cb.setFocus(Qt.PopupFocusReason), cb.showPopup()))

            def _apply(i: int) -> None:
                setter(cb.itemText(i))
                self.commitData.emit(cb)
                self.closeEditor.emit(cb, QtWidgets.QStyledItemDelegate.NoHint)

            cb.activated.connect(_apply)
            return cb

        le = QtWidgets.QLineEdit(parent)
        self._style_line(le)
        rx = QtCore.QRegularExpression(r"^(?:0x)?[0-9A-Fa-f]+|\d+$")
        le.setValidator(QtGui.QRegularExpressionValidator(rx))
        le.textEdited.connect(lambda _t: setter(le.text()))
        le.editingFinished.connect(lambda: setter(le.text()))

        # Mark this index as being edited
        self._editing_index = QPersistentModelIndex(index)

        return le

    def setEditorData(self, editor, index):  # type: ignore[override]
        if index.column() != 1:
            return super().setEditorData(editor, index)
        if isinstance(editor, QtWidgets.QComboBox):
            current = index.data(Qt.DisplayRole) or ""
            i = editor.findText(current)
            editor.setCurrentIndex(max(0, i))
        else:
            editor.setText(str(index.data(Qt.DisplayRole) or ""))

    def setModelData(self, editor, model, index):  # type: ignore[override]
        return

    def destroyEditor(self, editor, index):  # type: ignore[override]
        # Clear editing flag when editor is destroyed
        self._editing_index = None
        super().destroyEditor(editor, index)


# --------------------------------------------------------------------------------------
# Custom Rounded ScrollBar (actually works!)
# --------------------------------------------------------------------------------------
class RoundedScrollBar(QtWidgets.QScrollBar):
    def __init__(self, orientation=Qt.Vertical, parent=None):
        super().__init__(orientation, parent)
        self.setStyleSheet("background: transparent; border: none;")
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        # Calculate handle position and size
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)

        # Get handle rectangle
        style = self.style()
        handle_rect = style.subControlRect(
            QtWidgets.QStyle.CC_ScrollBar, opt,
            QtWidgets.QStyle.SC_ScrollBarSlider, self
        )

        # Draw rounded handle with antialiasing
        if handle_rect.isValid():
            painter.setPen(Qt.NoPen)

            # Determine color based on state
            if self.isSliderDown():
                color = QtGui.QColor(THEME['accent'])
            elif handle_rect.contains(self.mapFromGlobal(QtGui.QCursor.pos())):
                color = QtGui.QColor(THEME['input_focus'])
            else:
                color = QtGui.QColor(THEME['input_border'])

            painter.setBrush(color)

            # Draw SMOOTH pill-shaped scrollbar (not spiky!)
            # Use half the width as radius for perfect pill shape
            if self.orientation() == Qt.Vertical:
                radius = handle_rect.width() / 2.0 - 2
            else:
                radius = handle_rect.height() / 2.0 - 2
            painter.drawRoundedRect(handle_rect.adjusted(2, 2, -2, -2), radius, radius)

        painter.end()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.update()  # Repaint on hover

# --------------------------------------------------------------------------------------
# ToggleSwitch
# --------------------------------------------------------------------------------------
class ToggleSwitch(QtWidgets.QAbstractButton):
    offsetChanged = QtCore.Signal(float)

    def __init__(self, parent=None, *, width=54, height=32, knob_margin=3):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent; border: none;")

        self._w, self._h = width, height
        self._m = knob_margin
        self._offset = 0.0
        self.setFixedSize(self._w, self._h)

        self._track_off = QtGui.QColor(THEME["switch_off"])
        self._track_on  = QtGui.QColor(THEME["switch_on"])
        self._knob      = QtGui.QColor("#FFFFFF")

        self._anim = QtCore.QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
        self.toggled.connect(self._animate_to)

    def getOffset(self) -> float: return self._offset
    def setOffset(self, v: float) -> None:
        v = max(0.0, min(1.0, float(v)))
        if v == self._offset: return
        self._offset = v
        self.offsetChanged.emit(v)
        self.update()
    offset = QtCore.Property(float, fget=getOffset, fset=setOffset)

    def _animate_to(self, on: bool) -> None:
        self._anim.stop()
        self._anim.setStartValue(self.offset)
        self._anim.setEndValue(1.0 if on else 0.0)
        self._anim.start()

    def sizeHint(self) -> QtCore.QSize:  # type: ignore[override]
        return QtCore.QSize(self._w, self._h)

    def paintEvent(self, _):  # type: ignore[override]
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        w, h, m = self._w, self._h, self._m
        r = h / 2.0

        def mix(a: QtGui.QColor, b: QtGui.QColor, t: float) -> QtGui.QColor:
            return QtGui.QColor(
                int(a.red() + (b.red() - a.red()) * t),
                int(a.green() + (b.green() - a.green()) * t),
                int(a.blue() + (b.blue() - a.blue()) * t),
            )

        track_rect = QtCore.QRectF(0, 0, w, h)
        track_color = mix(self._track_off, self._track_on, self._offset)
        grad = QtGui.QLinearGradient(track_rect.topLeft(), track_rect.bottomLeft())
        grad.setColorAt(0.0, track_color.lighter(112))
        grad.setColorAt(1.0, track_color.darker(106))
        p.setPen(Qt.NoPen)
        p.setBrush(grad)
        p.drawRoundedRect(track_rect.adjusted(0.5, 0.5, -0.5, -0.5), r, r)

        knob_d = h - 2 * m
        x_min = m
        x_max = w - m - knob_d
        x = x_min + (x_max - x_min) * self._offset
        knob_rect = QtCore.QRectF(x, m, knob_d, knob_d)
        p.setBrush(self._knob)
        p.setPen(Qt.NoPen)
        p.drawEllipse(knob_rect)
        p.end()


# --------------------------------------------------------------------------------------
# Dynamic Stacked Widget (sizes to current page, not largest page)
# --------------------------------------------------------------------------------------
class DynamicStackedWidget(QtWidgets.QStackedWidget):
    """QStackedWidget that sizes based on current page, not largest page.
    This prevents phantom scrollbars when switching between pages of different sizes."""

    def sizeHint(self):  # type: ignore[override]
        """Return size hint of current widget only"""
        current = self.currentWidget()
        if current:
            return current.sizeHint()
        return QtCore.QSize(0, 0)

    def minimumSizeHint(self):  # type: ignore[override]
        """Return minimum size hint of current widget only"""
        current = self.currentWidget()
        if current:
            return current.minimumSizeHint()
        return QtCore.QSize(0, 0)


# --------------------------------------------------------------------------------------
# Glow-Dialog + Dim-Overlay
# --------------------------------------------------------------------------------------
class DimOverlay(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._opacity = 0.0
        self.hide()

        # Smooth fade animation
        self._fade_anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self._fade_anim.setDuration(200)
        self._fade_anim.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

    def showEvent(self, e):
        self.resize(self.parentWidget().size())
        self.setWindowOpacity(0.0)
        super().showEvent(e)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.start()

    def resizeEvent(self, e):
        self.resize(self.parentWidget().size())
        super().resizeEvent(e)

    def paintEvent(self, _):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        opacity = int(170 * self.windowOpacity())
        p.fillRect(self.rect(), QtGui.QColor(10, 14, 20, opacity))
        p.end()

    def fadeOut(self):
        """Smoothly fade out the overlay"""
        self._fade_anim.setStartValue(self.windowOpacity())
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.finished.connect(self.hide)
        self._fade_anim.start()


class GlowMessageBox(QtWidgets.QDialog):
    def __init__(self, parent, title: str, text: str, button_text: str = "OK"):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.card = QtWidgets.QFrame(objectName="glowCard")
        self.card.setStyleSheet(f"""
            QFrame#glowCard{{
                background:{THEME['card']};
                border-radius:18px;
                border:1px solid {THEME['border']};
            }}
            QLabel#glowTitle{{ font-size:16px; font-weight:700; color:{THEME['text']}; }}
            QLabel#glowText{{ color:{THEME['muted']}; line-height: 1.3; }}
            QPushButton#glowPrimary{{
                background:{THEME['accent']}; color:white; border:0; border-radius:12px; padding:10px 18px;
            }}
            QPushButton#glowPrimary:hover{{ background:{THEME['accent_hover']}; }}
            QPushButton#glowPrimary:pressed{{ background:{THEME['accent_press']}; }}
        """)
        lay = QtWidgets.QVBoxLayout(self.card)
        lay.setContentsMargins(18, 18, 18, 16)
        lay.setSpacing(10)

        head = QtWidgets.QHBoxLayout()
        ic = QtWidgets.QLabel()
        ic.setPixmap(self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxWarning).pixmap(28, 28))
        t = QtWidgets.QLabel(title, objectName="glowTitle")
        head.addWidget(ic, 0, Qt.AlignTop)
        head.addSpacing(8)
        head.addWidget(t, 1, Qt.AlignVCenter)
        lay.addLayout(head)

        body = QtWidgets.QLabel(text, objectName="glowText")
        body.setWordWrap(True)
        lay.addWidget(body)

        btn = QtWidgets.QPushButton(button_text, objectName="glowPrimary")
        btn.setMinimumHeight(40)
        btn.clicked.connect(self.accept)
        lay.addWidget(btn, 0, Qt.AlignRight)

        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 16)
        shadow.setColor(QtGui.QColor(0, 0, 0, 130))
        self.card.setGraphicsEffect(shadow)

        outer.addWidget(self.card)

    def resizeEvent(self, e):
        path = QtGui.QPainterPath()
        rect = self.rect()
        rrect = QtCore.QRectF(8, 8, rect.width() - 16, rect.height() - 16)
        path.addRoundedRect(rrect, 18, 18)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
        super().resizeEvent(e)

    def paintEvent(self, _):
        p = QtGui.QPainter(self)
        p.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
        p.fillRect(self.rect(), QtCore.Qt.transparent)
        p.end()

    def showCentered(self):
        p = self.parentWidget()
        self.adjustSize()
        self.move(p.geometry().center() - self.rect().center())

        # Smooth scale and fade-in animation
        self.setWindowOpacity(0.0)
        self.card.setProperty("scale", 0.9)

        fade = QtCore.QPropertyAnimation(self, b"windowOpacity")
        fade.setDuration(250)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        fade.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

        return self.exec()


# --------------------------------------------------------------------------------------
# SCEWIN Process Runner with QProcess
# --------------------------------------------------------------------------------------
@dataclass
class ScewinResult:
    """Result of a SCEWIN operation"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    error_message: Optional[str] = None

class ScewinRunner(QtCore.QObject):
    finished = Signal(ScewinResult)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.timeout_timer = None

    def run_import(self, nvram_path: Path, exe_path: Path = SCEWIN_EXE_PATH) -> None:
        """
        Import BIOS settings: SCEWIN_64.exe /I /S nvram.txt
        Non-blocking execution with QProcess
        """
        logging.info(f"Starting SCEWIN import: {nvram_path}")

        if not exe_path.exists():
            logging.error(f"SCEWIN not found: {exe_path}")
            result = ScewinResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="",
                error_message=f"SCEWIN_64.exe not found at {exe_path}"
            )
            self.finished.emit(result)
            return

        if not nvram_path.exists():
            logging.error(f"NVRAM file not found: {nvram_path}")
            result = ScewinResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="",
                error_message=f"File not found: {nvram_path}"
            )
            self.finished.emit(result)
            return

        self.process = QtCore.QProcess(self)
        self.process.setWorkingDirectory(str(nvram_path.parent))

        # Connect signals
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)

        # Setup timeout (30 seconds)
        self.timeout_timer = QtCore.QTimer(self)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self._on_timeout)
        self.timeout_timer.start(30000)  # 30s

        # Start process
        args = ["/I", "/S", nvram_path.name]
        logging.info(f"Executing: {exe_path} {' '.join(args)}")
        self.process.start(str(exe_path), args)

    def run_export(self, output_name: str = DEFAULT_NVRAM_NAME, exe_path: Path = SCEWIN_EXE_PATH) -> None:
        """
        Export BIOS settings: SCEWIN_64.exe /O /S nvram.txt
        Non-blocking execution with QProcess
        """
        logging.info(f"Starting SCEWIN export: {output_name}")

        if not exe_path.exists():
            logging.error(f"SCEWIN not found: {exe_path}")
            result = ScewinResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="",
                error_message=f"SCEWIN_64.exe not found at {exe_path}"
            )
            self.finished.emit(result)
            return

        self.process = QtCore.QProcess(self)
        self.process.setWorkingDirectory(str(exe_path.parent))

        # Connect signals
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)

        # Setup timeout (30 seconds)
        self.timeout_timer = QtCore.QTimer(self)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self._on_timeout)
        self.timeout_timer.start(30000)  # 30s

        # Start process
        args = ["/O", "/S", output_name]
        logging.info(f"Executing: {exe_path} {' '.join(args)}")
        self.process.start(str(exe_path), args)

    def _on_finished(self, exit_code: int, exit_status):
        """Handle process completion"""
        if self.timeout_timer:
            self.timeout_timer.stop()

        if not self.process:
            return

        stdout = self.process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
        stderr = self.process.readAllStandardError().data().decode('utf-8', errors='ignore')

        success = (exit_code == 0)

        if success:
            logging.info(f"SCEWIN completed successfully (exit code {exit_code})")
        else:
            logging.error(f"SCEWIN failed with exit code {exit_code}")
            logging.error(f"stderr: {stderr}")

        result = ScewinResult(
            success=success,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            error_message=stderr if not success else None
        )

        self.finished.emit(result)

    def _on_error(self, error):
        """Handle process errors"""
        if self.timeout_timer:
            self.timeout_timer.stop()

        error_messages = {
            QtCore.QProcess.FailedToStart: "Failed to start SCEWIN (missing or permission denied)",
            QtCore.QProcess.Crashed: "SCEWIN crashed",
            QtCore.QProcess.Timedout: "SCEWIN timed out",
            QtCore.QProcess.WriteError: "Write error",
            QtCore.QProcess.ReadError: "Read error",
            QtCore.QProcess.UnknownError: "Unknown error"
        }

        error_msg = error_messages.get(error, f"Process error: {error}")
        logging.error(f"SCEWIN error: {error_msg}")

        result = ScewinResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr="",
            error_message=error_msg
        )

        self.finished.emit(result)

    def _on_timeout(self):
        """Handle timeout"""
        if self.process:
            logging.error("SCEWIN timed out after 30 seconds")
            self.process.kill()

            result = ScewinResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="",
                error_message="Process timed out after 30 seconds"
            )

            self.finished.emit(result)


# --------------------------------------------------------------------------------------
# Modern Toast Notification System
# --------------------------------------------------------------------------------------
class ToastNotification(QtWidgets.QFrame):
    """
    Modern dark toast notification with animations
    - Slides up from bottom center
    - Fades in/out smoothly
    - Auto-dismisses or stays on error
    - Optional action button
    """

    def __init__(self, text: str, toast_type: str = "info", duration_ms: int = 2200,
                 details: str = None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setObjectName("ToastBubble")
        self.setAutoFillBackground(False)
        
        # Setup opacity effect for fade animations
        self._opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(1.0)

        # Unified rounded toast styling - matches all toasts
        self.setStyleSheet(f"""
            QWidget#ToastBubble {{
                background: rgba(15, 20, 25, 0.96);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 12px;
                padding: 0px;
                margin: 0px;
            }}
            QWidget#ToastBubble QLabel {{
                background: transparent;
                border: none;
                padding-left: 0px;
                margin-left: 0px;
                padding-right: 0px;
                margin-right: 0px;
            }}
        """)

        self.setMaximumWidth(500)
        self.setMinimumWidth(300)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        # Icon + Text row with zero spacing
        top_row = QtWidgets.QHBoxLayout()
        top_row.setSpacing(0)
        top_row.setContentsMargins(0, 0, 0, 0)

        # Icon - use SVG for crisp rendering
        icon_label = QtWidgets.QLabel()
        color_map = {
            "success": THEME['success'],
            "error": THEME['error'],
            "info": THEME['accent']
        }
        icon_color = color_map.get(toast_type, THEME['text'])
        icon_label.setPixmap(self._create_icon_svg(toast_type, icon_color))
        icon_label.setContentsMargins(0, 0, 0, 0)
        icon_label.setFixedSize(18, 18)
        top_row.addWidget(icon_label)

        # Message text - ensure no leading space
        msg_label = QtWidgets.QLabel(text.strip())
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"color: {THEME['text']}; font-size: 14px; padding: 0px; margin: 0px;")
        msg_label.setContentsMargins(6, 0, 0, 0)
        top_row.addWidget(msg_label, 1)

        layout.addLayout(top_row)

        # Optional details expander
        if details:
            details_btn = QtWidgets.QPushButton("Show Details")
            details_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {THEME['accent']};
                    border: none;
                    text-align: left;
                    padding: 4px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    color: {THEME['accent_hover']};
                    text-decoration: underline;
                }}
            """)

            details_text = QtWidgets.QTextEdit()
            details_text.setReadOnly(True)
            details_text.setPlainText(details)
            details_text.setMaximumHeight(100)
            details_text.setStyleSheet(f"""
                QTextEdit {{
                    background: {THEME['input_bg']};
                    color: {THEME['muted']};
                    border: 1px solid {THEME['border']};
                    border-radius: 4px;
                    padding: 8px;
                    font-family: monospace;
                    font-size: 11px;
                }}
            """)
            details_text.hide()

            def toggle_details():
                if details_text.isVisible():
                    details_text.hide()
                    details_btn.setText("Show Details")
                else:
                    details_text.show()
                    details_btn.setText("Hide Details")
                self.adjustSize()

            details_btn.clicked.connect(toggle_details)
            layout.addWidget(details_btn)
            layout.addWidget(details_text)

        self.adjustSize()

        # Animations
        self.fade_anim = QtCore.QPropertyAnimation(self._opacity_effect, b"opacity")
        self.fade_anim.setDuration(200)
        self.fade_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        self.slide_anim = QtCore.QPropertyAnimation(self, b"pos")
        self.slide_anim.setDuration(300)
        self.slide_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        # Auto-dismiss timer (unless error with details)
        if toast_type != "error" or not details:
            QtCore.QTimer.singleShot(duration_ms, self.hide_toast)

    def _create_icon_svg(self, toast_type: str, color: str) -> QtGui.QPixmap:
        """Create tight SVG icon with no padding - 18x18 viewBox"""
        pixmap = QtGui.QPixmap(18, 18)
        pixmap.fill(Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        pen = QtGui.QPen(QtGui.QColor(color))
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        if toast_type == "success":
            # Checkmark - tight fit
            path = QtGui.QPainterPath()
            path.moveTo(4, 9)
            path.lineTo(7, 12)
            path.lineTo(14, 5)
            painter.drawPath(path)
        elif toast_type == "error":
            # X mark - tight fit
            painter.drawLine(5, 5, 13, 13)
            painter.drawLine(13, 5, 5, 13)
        else:  # info
            # i icon - tight fit
            painter.drawEllipse(8, 4, 2, 2)
            painter.drawLine(9, 8, 9, 14)

        painter.end()
        return pixmap

    def show_toast(self, parent_widget):
        """Show toast at top-right with slide-down animation"""
        # Position at top-right of parent (below custom title bar)
        parent_rect = parent_widget.geometry()
        
        # Title bar height + margins
        title_bar_height = 40
        top_margin = 16
        right_margin = 16
        
        # Final position (top-right, below title bar)
        final_x = parent_rect.right() - self.width() - right_margin
        final_y = parent_rect.top() + title_bar_height + top_margin

        # Start position (above screen for slide-down)
        start_x = final_x
        start_y = parent_rect.top() - self.height()

        self.move(start_x, start_y)
        self.show()
        self._opacity_effect.setOpacity(0.0)  # Start fully transparent

        # Fade in
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(0.96)  # Slightly transparent
        self.fade_anim.start()

        # Slide down
        self.slide_anim.setStartValue(QtCore.QPoint(start_x, start_y))
        self.slide_anim.setEndValue(QtCore.QPoint(final_x, final_y))
        self.slide_anim.start()

    def hide_toast(self):
        """Hide toast with slide-up and fade-out animation"""
        # Slide up slightly while fading
        current_pos = self.pos()
        self.slide_anim.setStartValue(current_pos)
        self.slide_anim.setEndValue(QtCore.QPoint(current_pos.x(), current_pos.y() - 20))
        self.slide_anim.setDuration(200)
        self.slide_anim.start()
        
        # Fade out
        self.fade_anim.setStartValue(self._opacity_effect.opacity())
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self.deleteLater)
        self.fade_anim.start()



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



class LoadingSpinner(QtWidgets.QWidget):
    """Modern loading spinner with smooth animation"""
    
    def __init__(self, parent=None, size=24, color=None):
        super().__init__(parent)
        self.size = size
        self.color = color or THEME['accent']
        self.angle = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def start(self):
        """Start the spinning animation"""
        self.timer.start(16)  # ~60 FPS
        self.show()
        
    def stop(self):
        """Stop the spinning animation"""
        self.timer.stop()
        self.hide()
        
    def update_animation(self):
        """Update the rotation angle"""
        self.angle = (self.angle + 8) % 360
        self.update()
        
    def paintEvent(self, event):
        """Paint the spinning circle"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Create a circular gradient
        gradient = QtGui.QConicalGradient(self.size // 2, self.size // 2, self.angle)
        gradient.setColorAt(0, QtGui.QColor(self.color))
        gradient.setColorAt(0.7, QtGui.QColor(self.color))
        gradient.setColorAt(0.8, QtGui.QColor(self.color).lighter(150))
        gradient.setColorAt(1, Qt.transparent)
        
        # Draw the spinner
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawEllipse(2, 2, self.size - 4, self.size - 4)


class ProgressBar(QtWidgets.QWidget):
    """Modern progress bar with smooth animation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.maximum = 100
        self.animation = QtCore.QPropertyAnimation(self, b"value")
        self.animation.setDuration(200)
        self.setFixedHeight(6)
        self.setStyleSheet(f"""
            QWidget {{
                background: {THEME['input_border']};
                border-radius: 3px;
            }}
        """)
        
    def setValue(self, value):
        """Set progress value with animation"""
        self.value = max(0, min(value, self.maximum))
        self.animation.stop()
        self.animation.setStartValue(self.value)
        self.animation.setEndValue(self.value)
        self.animation.start()
        self.update()
        
    def setMaximum(self, maximum):
        """Set maximum value"""
        self.maximum = maximum
        
    def paintEvent(self, event):
        """Paint the progress bar"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(THEME['input_border'])))
        painter.drawRoundedRect(self.rect(), 3, 3)
        
        # Progress
        if self.value > 0:
            progress_width = int((self.value / self.maximum) * self.width())
            progress_rect = QtCore.QRect(0, 0, progress_width, self.height())
            
            gradient = QtGui.QLinearGradient(0, 0, progress_width, 0)
            gradient.setColorAt(0, QtGui.QColor(THEME['accent']))
            gradient.setColorAt(1, QtGui.QColor(THEME['accent_hover']))
            
            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawRoundedRect(progress_rect, 3, 3)


class NotificationManager(QtCore.QObject):
    """
    Centralized toast notification system with deduplication
    Replaces old glow dialogs with modern non-blocking toasts
    """

    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self._last_messages: Dict[str, float] = {}  # message -> timestamp
        self._debounce_ms = 1000  # 1 second debounce

    def _should_show(self, message: str) -> bool:
        """Check if message should be shown (not duplicate within debounce period)"""
        import time
        now = time.time() * 1000  # milliseconds
        key = message.lower().strip()

        if key in self._last_messages:
            elapsed = now - self._last_messages[key]
            if elapsed < self._debounce_ms:
                return False

        self._last_messages[key] = now
        return True

    def notify_success(self, text: str, duration_ms: int = 3500, subtitle: str = None):
        """Show success toast (no action buttons)"""
        if not self._should_show(text):
            return

        display_text = text
        if subtitle:
            display_text = f"{text}\n{subtitle}"

        toast = ToastNotification(display_text, "success", duration_ms, parent=self.parent_widget)
        toast.show_toast(self.parent_widget)

    def notify_error(self, text: str, details: str = None):
        """Show error toast with optional details expander"""
        if not self._should_show(text):
            return

        toast = ToastNotification(text, "error", 5000, details=details, parent=self.parent_widget)
        toast.show_toast(self.parent_widget)

    def notify_info(self, text: str, duration_ms: int = 2200):
        """Show info toast"""
        if not self._should_show(text):
            return

        toast = ToastNotification(text, "info", duration_ms, parent=self.parent_widget)
        toast.show_toast(self.parent_widget)


# --------------------------------------------------------------------------------------
# "No File Loaded" Professional Dialog
# --------------------------------------------------------------------------------------
class NoFileLoadedDialog(QtWidgets.QDialog):
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
            super().keyPressEvent(event)

    def _drag_enter(self, event):
        """Accept .txt files"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith('.txt') for url in urls):
                event.acceptProposedAction()

    def _drop(self, event):
        """Handle dropped file"""
        urls = event.mimeData().urls()
        txt_files = [url.toLocalFile() for url in urls if url.toLocalFile().lower().endswith('.txt')]

        if txt_files:
            self.file_dropped.emit(Path(txt_files[0]))
            self.accept()

    def _on_load(self):
        """Load file requested"""
        self.load_file_requested.emit()
        self.accept()

    def _on_import(self):
        """Import via SCEWIN requested"""
        self.import_requested.emit()
        self.accept()

    def _on_export(self):
        """Export via SCEWIN requested"""
        self.export_requested.emit()
        # Don't close dialog yet - let export process handle it


# --------------------------------------------------------------------------------------
# Global Drag & Drop Overlay
# --------------------------------------------------------------------------------------
class DragDropOverlay(QtWidgets.QWidget):
    """
    Full-window overlay shown when dragging files over the main window
    Shows "Upload and load file" with a drop zone
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()

        # Semi-transparent dark background
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Center container
        center_widget = QtWidgets.QWidget()
        center_widget.setStyleSheet(f"""
            QWidget {{
                background: {THEME['card']};
                border: 2px dashed {THEME['accent']};
                border-radius: 24px;
            }}
        """)

        center_layout = QtWidgets.QVBoxLayout(center_widget)
        center_layout.setContentsMargins(60, 60, 60, 60)
        center_layout.setAlignment(Qt.AlignCenter)

        # Icon
        icon_label = QtWidgets.QLabel("📁")
        icon_label.setStyleSheet("font-size: 64px; background: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(icon_label)

        # Text
        text_label = QtWidgets.QLabel("Upload and load file")
        text_label.setStyleSheet(f"font-size: 24px; font-weight: 600; color: {THEME['text']}; background: transparent; border: none;")
        text_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(text_label)

        # Add center widget to main layout
        layout.addStretch()
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(center_widget)
        h_layout.addStretch()
        layout.addLayout(h_layout)
        layout.addStretch()

    def show_overlay(self, parent_rect):
        """Show overlay covering parent window"""
        self.setGeometry(parent_rect)
        self.show()
        self.raise_()

    def paintEvent(self, event):
        """Draw semi-transparent background"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Semi-transparent overlay
        overlay_color = QtGui.QColor(THEME['bg'])
        overlay_color.setAlpha(230)  # 90% opacity
        painter.fillRect(self.rect(), overlay_color)


# --------------------------------------------------------------------------------------
# Custom Dark Title Bar
# --------------------------------------------------------------------------------------

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



class CustomTitleBar(QtWidgets.QWidget):
    """
    Custom dark title bar replacing default Windows title bar
    Features:
    - App title on left
    - Window controls (min, max/restore, close) on right with SVG icons
    - Hover and pressed states
    - Double-click to maximize/restore
    - Drag to move window
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet(f"background: {THEME['card']}; border-bottom: 1px solid {THEME['border']};")

        self.parent_window = parent
        self.is_maximized = False
        self.drag_position = None

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 0, 0)
        layout.setSpacing(0)

        layout.addStretch()

        # Window control buttons - icon only, no borders, tint on hover
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
        """

        # Minimize button with premium SVG
        self.min_btn = QtWidgets.QPushButton()
        self.min_btn.setIcon(self._create_minimize_icon())
        self.min_btn.setIconSize(QtCore.QSize(18, 18))
        self.min_btn.setStyleSheet(btn_style_base)
        self.min_btn.clicked.connect(lambda: parent.showMinimized() if parent else None)
        self.min_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.min_btn)

        # Maximize/Restore button with premium SVG
        self.max_btn = QtWidgets.QPushButton()
        self.max_btn.setIcon(self._create_maximize_icon())
        self.max_btn.setIconSize(QtCore.QSize(18, 18))
        self.max_btn.setStyleSheet(btn_style_base)
        self.max_btn.clicked.connect(self.toggle_maximize)
        self.max_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.max_btn)

        # Close button - icon only, red tint on hover
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
        """
        self.close_btn = QtWidgets.QPushButton()
        self.close_btn.setIcon(self._create_close_icon())
        self.close_btn.setIconSize(QtCore.QSize(18, 18))
        self.close_btn.setStyleSheet(close_style)
        self.close_btn.clicked.connect(lambda: parent.close() if parent else None)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.close_btn)

        # Connect to window state changes for automatic icon toggling
        if parent:
            parent.windowStateChanged = self._sync_max_icon

    def _create_minimize_icon(self) -> QtGui.QIcon:
        """Create premium minimize icon (horizontal line) - 18x18 tight viewBox"""
        pixmap = QtGui.QPixmap(18, 18)
        pixmap.fill(Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtGui.QColor(THEME['text']))
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(4, 9, 14, 9)
        painter.end()
        return QtGui.QIcon(pixmap)

    def _create_maximize_icon(self) -> QtGui.QIcon:
        """Create premium maximize icon (square) - 18x18 tight viewBox"""
        pixmap = QtGui.QPixmap(18, 18)
        pixmap.fill(Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtGui.QColor(THEME['text']))
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawRect(4, 4, 10, 10)
        painter.end()
        return QtGui.QIcon(pixmap)

    def _create_restore_icon(self) -> QtGui.QIcon:
        """Create premium restore icon (overlapping squares) - 18x18 tight viewBox"""
        pixmap = QtGui.QPixmap(18, 18)
        pixmap.fill(Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtGui.QColor(THEME['text']))
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        # Back square (offset)
        painter.drawRect(7, 4, 7, 7)
        # Front square
        painter.drawRect(4, 7, 7, 7)
        painter.end()
        return QtGui.QIcon(pixmap)

    def _create_close_icon(self) -> QtGui.QIcon:
        """Create premium close icon (X) - 18x18 tight viewBox"""
        pixmap = QtGui.QPixmap(18, 18)
        pixmap.fill(Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtGui.QColor(THEME['text']))
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(5, 5, 13, 13)
        painter.drawLine(13, 5, 5, 13)
        painter.end()
        return QtGui.QIcon(pixmap)

    def toggle_maximize(self):
        """Toggle maximize/restore"""
        if not self.parent_window:
            return

        if self.is_maximized:
            self.parent_window.showNormal()
            self.max_btn.setIcon(self._create_maximize_icon())
            self.is_maximized = False
        else:
            self.parent_window.showMaximized()
            self.max_btn.setIcon(self._create_restore_icon())
            self.is_maximized = True

    def _sync_max_icon(self, state):
        """Sync maximize/restore icon based on window state"""
        if state == Qt.WindowMaximized:
            self.max_btn.setIcon(self._create_restore_icon())
            self.is_maximized = True
        else:
            self.max_btn.setIcon(self._create_maximize_icon())
            self.is_maximized = False

    def mousePressEvent(self, event):
        """Start drag"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Drag window"""
        if event.buttons() == Qt.LeftButton and self.drag_position:
            if self.is_maximized:
                # Restore before dragging
                self.toggle_maximize()
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """Double-click to maximize/restore"""
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()


# --------------------------------------------------------------------------------------
# Preset row widget
# --------------------------------------------------------------------------------------
class PresetRow(QtWidgets.QWidget):
    toggled = Signal(str, bool)  # preset_name, enabled

    def __init__(self, name: str, on: bool = False, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        self.name = name
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(8)

        self.lbl = QtWidgets.QLabel(name)
        self.lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.sw = ToggleSwitch(self)
        self.sw.setChecked(on)
        # precise binding
        self.sw.toggled.connect(lambda state, n=name: self.toggled.emit(n, state))

        lay.addWidget(self.lbl, 1)
        lay.addWidget(self.sw, 0, Qt.AlignRight | Qt.AlignVCenter)


# --------------------------------------------------------------------------------------
# Page Dots
# --------------------------------------------------------------------------------------
class PageDots(QtWidgets.QWidget):
    pageChanged = Signal(int)  # 0 or 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self._index = -1
        self.setFixedHeight(32)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

        h = QtWidgets.QHBoxLayout(self)
        h.setContentsMargins(0, 6, 0, 0)
        h.setSpacing(12)
        h.addStretch(1)

        self.btn0 = QtWidgets.QPushButton()
        self.btn1 = QtWidgets.QPushButton()
        for i, b in enumerate((self.btn0, self.btn1)):
            b.setFixedSize(14, 14)
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(self._dot_styles(False))
            b.clicked.connect(partial(self.setIndex, i))
            h.addWidget(b)

        h.addStretch(1)
        self.setIndex(0)

    def _dot_styles(self, on: bool) -> str:
        base = THEME["input_border"]
        fill = THEME["input_focus"]
        if on:
            return f"QPushButton{{border-radius:7px;background:{fill};border:0;}}"
        return f"QPushButton{{border-radius:7px;background:transparent;border:1px solid {base};}} QPushButton:hover{{background:{THEME['tab_selected']};}}"

    def setIndex(self, idx: int):
        idx = 0 if idx <= 0 else 1
        if self._index == idx:
            return
        self._index = idx
        self.btn0.setChecked(idx == 0)
        self.btn1.setChecked(idx == 1)
        self.btn0.setStyleSheet(self._dot_styles(idx == 0))
        self.btn1.setStyleSheet(self._dot_styles(idx == 1))
        self.pageChanged.emit(idx)

    def index(self) -> int:
        return self._index


# --------------------------------------------------------------------------------------
# UI - Main Application Window
# --------------------------------------------------------------------------------------
class AutoBiosWindow(QtWidgets.QWidget):

    def __init__(self) -> None:
        super().__init__()

        # Frameless window with custom title bar and rounded corners
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)  # For rounded corners
        self.resize(1280, 760)

        # Enable drag & drop for nvram.txt files
        self.setAcceptDrops(True)

        # Initialize notification system
        self.notifications = NotificationManager(self)

        # Initialize SCEWIN runner
        self.scewin_runner = ScewinRunner(self)
        self.scewin_runner.finished.connect(self._on_scewin_finished)
        self._current_scewin_operation = None  # "import" or "export"

        # Drag & drop overlay
        self.drag_overlay = DragDropOverlay(self)
        self._drag_active = False

        # Resize tracking for corner/edge resize
        self._resize_margin = 10
        self._resize_direction = None

        # Main container with rounded corners
        main_container = QtWidgets.QWidget()
        main_container.setObjectName("mainContainer")
        main_container.setStyleSheet(f"""
            QWidget#mainContainer {{
                background: {THEME['bg']};
                border-radius: 12px;
                border: 1px solid {THEME['input_border']};
            }}
        """)

        container_layout = QtWidgets.QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(main_container)

        # Main layout with custom title bar
        main_layout = QtWidgets.QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom title bar
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Content wrapper
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background: transparent;")
        main_layout.addWidget(content_widget)

        # Apply stylesheet after layout setup
        self.setStyleSheet(self._stylesheet())

        root = QtWidgets.QVBoxLayout(content_widget)
        root.setContentsMargins(24, 20, 24, 20)  # Premium spacing
        root.setSpacing(18)  # Better visual hierarchy

        # Header - completely transparent, no background
        header = QtWidgets.QWidget()
        header.setObjectName("header")
        header.setAutoFillBackground(False)
        header.setAttribute(Qt.WA_StyledBackground, False)
        header.setAttribute(Qt.WA_NoSystemBackground, True)

        # Completely transparent palette
        pal = header.palette()
        pal.setColor(QtGui.QPalette.Window, Qt.transparent)
        pal.setBrush(QtGui.QPalette.Window, Qt.transparent)
        header.setPalette(pal)

        hv = QtWidgets.QVBoxLayout(header)
        hv.setContentsMargins(20, 14, 20, 14)  # Premium header spacing
        hv.setSpacing(14)  # Better spacing

        top_row = QtWidgets.QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(12)

        title = QtWidgets.QLabel(APP_TITLE)
        title.setObjectName("title")
        title.setAccessibleName("app-title")
        title.setAutoFillBackground(False)
        title.setAttribute(Qt.WA_StyledBackground, False)
        title.setAttribute(Qt.WA_NoSystemBackground, True)
        title.setAttribute(Qt.WA_TranslucentBackground, True)

        # Completely transparent palette
        title_pal = title.palette()
        title_pal.setColor(QtGui.QPalette.Window, Qt.transparent)
        title_pal.setBrush(QtGui.QPalette.Window, Qt.transparent)
        title.setPalette(title_pal)

        # No graphics effects
        title.setGraphicsEffect(None)

        top_row.addWidget(title, 0, Qt.AlignLeft | Qt.AlignVCenter)

        self.topTabs = QtWidgets.QTabBar(objectName="topTabs")
        self.topTabs.addTab("Settings List")
        self.topTabs.addTab("Presets")
        self.topTabs.setExpanding(True)
        self.topTabs.setDrawBase(False)
        self.topTabs.setUsesScrollButtons(False)
        self.topTabs.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        top_row.addWidget(self.topTabs, 1)

        self.counts = QtWidgets.QLabel("0 edited • 0 applied", objectName="counts")
        self.counts.setAccessibleName("edit-counts")
        top_row.addWidget(self.counts, 0, Qt.AlignRight | Qt.AlignVCenter)

        hv.addLayout(top_row)

        self.search = QtWidgets.QLineEdit(placeholderText="Search (setting / option)")
        self.search.setObjectName("searchInput")
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(640)
        self.search.setMaximumWidth(1000)
        self.search.setAlignment(Qt.AlignLeft)
        self.search.setAccessibleName("search-field")
        self.search.setAttribute(Qt.WA_StyledBackground, True)
        self.search.setAutoFillBackground(True)
        hv.addWidget(self.search, 0, Qt.AlignHCenter)

        root.addWidget(header, 0)

        # Tabs
        self.tabs = QtWidgets.QTabWidget(objectName="tabs")
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().hide()
        self.tabs.setStyleSheet("background: transparent;")
        root.addWidget(self.tabs, 1)

        # Model + Filter
        self.model = SettingsModel()
        self.model.stagedChanged.connect(self.update_counts)

        self.proxy = QtCore.QSortFilterProxyModel()
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)
        self.proxy.setDynamicSortFilter(False)  # Disable dynamic sorting for performance

        # Optimized search with debouncing (50ms delay for instant response)
        self._search_timer = QtCore.QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(50)  # Ultra-fast: 50ms for instant response
        self._search_timer.timeout.connect(self._apply_search_filter)
        self.search.textChanged.connect(self._on_search_changed)

        # Tab 0: Settings
        settings_tab = QtWidgets.QWidget()
        settings_tab.setStyleSheet("background: transparent;")
        v = QtWidgets.QVBoxLayout(settings_tab)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(12)

        self.table = QtWidgets.QTableView(objectName="cardTable")
        self.table.setModel(self.proxy)
        self.table.setItemDelegateForColumn(1, ComboOrLineDelegate(self.table))
        self.table.setSortingEnabled(False)
        self.table.horizontalHeader().setSortIndicatorShown(False)
        self.table.setShowGrid(False)  # Disable grid, use CSS borders instead
        self.table.setWordWrap(False)
        self.table.setFrameShape(QtWidgets.QFrame.NoFrame)

        # Install custom rounded scrollbars
        self.table.setVerticalScrollBar(RoundedScrollBar(Qt.Vertical))
        self.table.setHorizontalScrollBar(RoundedScrollBar(Qt.Horizontal))

        vh = self.table.verticalHeader()
        vh.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        vh.setDefaultSectionSize(32)
        self.table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.table.setViewportMargins(0, 0, 0, 16)  # Increased bottom margin
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.SelectedClicked | QtWidgets.QAbstractItemView.EditKeyPressed
        )

        # Performance optimizations for table rendering
        self.table.viewport().setAttribute(Qt.WA_StaticContents)  # Reduce repaints
        self.table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)  # Smooth scrolling
        self.table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)  # Smooth scrolling
        self.table.setAlternatingRowColors(False)  # Disable alternating colors for performance
        self.table.clicked.connect(self._force_edit_col1)
        v.addWidget(self.table, 1)

        self.empty_main = QtWidgets.QLabel("Load a file to see settings.", alignment=Qt.AlignCenter, objectName="placeholder")
        v.addWidget(self.empty_main, 1)

        self.table.horizontalHeader().setVisible(False)
        self.table.setVisible(False)
        self.empty_main.setVisible(True)

        self.tabs.addTab(settings_tab, "")

        # Tab 1: Presets
        presets_tab = QtWidgets.QWidget()
        presets_tab.setStyleSheet("background: transparent;")
        p_outer = QtWidgets.QVBoxLayout(presets_tab)
        p_outer.setContentsMargins(16, 16, 16, 16)
        p_outer.setSpacing(12)

        splitter = QtWidgets.QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(12)  # Visible gap between panels
        splitter.setChildrenCollapsible(False)
        splitter.setStyleSheet(f"QSplitter::handle {{ background: {THEME['bg']}; }}")

        # Left list of matched settings
        left_wrap = QtWidgets.QWidget()
        lw = QtWidgets.QVBoxLayout(left_wrap)
        lw.setContentsMargins(0, 0, 0, 0)
        lw.setSpacing(10)

        self.presetProxy = NameSetProxy()
        self.presetProxy.setSourceModel(self.model)

        self.presetTable = QtWidgets.QTableView(objectName="presetListTable")
        self.presetTable.setModel(self.presetProxy)
        self.presetTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.presetTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.presetTable.setWordWrap(False)
        self.presetTable.setShowGrid(False)  # Disable grid to avoid double lines

        # Install custom rounded scrollbars
        self.presetTable.setVerticalScrollBar(RoundedScrollBar(Qt.Vertical))
        self.presetTable.setHorizontalScrollBar(RoundedScrollBar(Qt.Horizontal))

        self.presetTable.verticalHeader().setVisible(False)
        self.presetTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.presetTable.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.presetTable.setColumnWidth(1, 260)
        self.presetTable.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.presetTable.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.presetTable.setViewportMargins(0, 0, 0, 16)  # Increased bottom margin

        # Performance optimizations for preset table
        self.presetTable.viewport().setAttribute(Qt.WA_StaticContents)  # Reduce repaints

        self.presetTable.setColumnHidden(2, True)
        self.presetTable.setColumnHidden(3, True)
        self.presetTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.presetTable.verticalHeader().setDefaultSectionSize(32)
        self.presetTable.setFrameShape(QtWidgets.QFrame.NoFrame)
        lw.addWidget(self.presetTable, 1)

        self.preset_placeholder = QtWidgets.QLabel(
            "Use the toggles on the right to show preset settings.",
            alignment=Qt.AlignCenter
        )
        lw.addWidget(self.preset_placeholder, 1)
        self.presetTable.horizontalHeader().setVisible(False)
        self.presetTable.setVisible(False)
        self.preset_placeholder.setVisible(True)

        # Right card with controls and pages
        right_outer = QtWidgets.QFrame(objectName="sideOuter")
        right_outer.setMinimumWidth(420)
        ro = QtWidgets.QVBoxLayout(right_outer)
        ro.setContentsMargins(0, 0, 0, 0)
        ro.setSpacing(0)

        # inner card
        right_wrap = QtWidgets.QFrame(objectName="sideCard")
        right_wrap.setStyleSheet("background: transparent;")
        rw = QtWidgets.QVBoxLayout(right_wrap)
        rw.setContentsMargins(14, 14, 14, 14)
        rw.setSpacing(12)

        lbl = QtWidgets.QLabel("Preset tools")

        # Family switch row (no errors on toggle)
        self.familySwitch = ToggleSwitch()
        self.familySwitch.setObjectName("familySwitch")
        self.familySwitch.setChecked(False)  # Intel default
        self.familyLabel = QtWidgets.QLabel("Intel", objectName="familyLabel")
        self.familyLabel.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        topCenter = QtWidgets.QHBoxLayout()
        topCenter.setContentsMargins(0, 0, 0, 0)
        topCenter.setSpacing(10)
        topCenter.addStretch(1)
        topCenter.addWidget(self.familySwitch, 0, Qt.AlignVCenter)
        topCenter.addWidget(self.familyLabel, 0, Qt.AlignVCenter)
        topCenter.addStretch(1)
        centerRow = QtWidgets.QWidget()
        centerRow.setLayout(topCenter)
        centerRow.setAttribute(Qt.WA_TranslucentBackground, True)
        centerRow.setStyleSheet("background: transparent; border: none;")
        # Scroll area for page content (only scrolls when needed!)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Only show when needed!
        self.scroll.setStyleSheet("background: transparent;")

        # Install custom rounded scrollbar
        self.scroll.setVerticalScrollBar(RoundedScrollBar(Qt.Vertical))
        self.scrollContent = QtWidgets.QWidget()
        self.scrollContent.setStyleSheet("background: transparent;")
        sc_lo = QtWidgets.QVBoxLayout(self.scrollContent)
        sc_lo.setContentsMargins(0, 0, 0, 0)
        sc_lo.setSpacing(0)
        sc_lo.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)  # Fit content exactly

        # PAGES - Custom stacked widget that sizes to current page only
        self.pages = DynamicStackedWidget()
        self.pages.setStyleSheet("background: transparent;")
        self._page_basic = QtWidgets.QWidget()
        self._page_basic.setStyleSheet("background: transparent;")
        self._page_adv = QtWidgets.QWidget()
        self._page_adv.setStyleSheet("background: transparent;")

        # Page: BASIC
        vb = QtWidgets.QVBoxLayout(self._page_basic)
        vb.setContentsMargins(0, 0, 0, 0)
        vb.setSpacing(8)
        vb.setAlignment(Qt.AlignTop)  # Align items to top
        self.rows_basic: Dict[str, PresetRow] = {}
        for name in PRESET_ORDER_BASIC:
            r = PresetRow(name, on=False)
            r.toggled.connect(lambda _name, state, n=name: self._on_preset_toggle_basic(n, state))
            self.rows_basic[name] = r
            vb.addWidget(r, 0, Qt.AlignTop)  # Align each widget to top

        # Page: ADVANCED (only active family shown)
        self.adv_container = QtWidgets.QWidget()
        self.adv_container.setStyleSheet("background: transparent;")
        self.adv_layout = QtWidgets.QVBoxLayout(self.adv_container)
        self.adv_layout.setContentsMargins(0, 0, 0, 0)
        self.adv_layout.setSpacing(8)
        self.adv_layout.setAlignment(Qt.AlignTop)  # Align to top
        self.rows_adv_intel: Dict[str, PresetRow] = {}
        self.rows_adv_amd: Dict[str, PresetRow] = {}
        self._enabled_adv_intel = {}
        self._enabled_adv_amd = {}
        self._build_adv_page_for_family("intel")  # initial build

        av = QtWidgets.QVBoxLayout(self._page_adv)
        av.setContentsMargins(0, 0, 0, 0)
        av.setSpacing(0)
        av.setAlignment(Qt.AlignTop)  # Align to top
        av.addWidget(self.adv_container, 0, Qt.AlignTop)

        self.pages.addWidget(self._page_basic)
        self.pages.addWidget(self._page_adv)

        sc_lo.addWidget(self.pages)
        self.scroll.setWidget(self.scrollContent)





        # State
        self._preset_family = "intel"
        self._enabled_basic: Dict[str, bool] = {k: False for k in PRESET_ORDER_BASIC}
        self._enabled_adv_intel: Dict[str, bool] = {k: False for k in PRESET_ORDER_ADV_INTEL}
        self._enabled_adv_amd: Dict[str, bool] = {k: False for k in PRESET_ORDER_ADV_AMD}
        self.pending_targets: Dict[int, Any] = {}
        self.current_path: Optional[Path] = None
        self.file_loaded: bool = False  # Track if file is loaded for Advanced page gating

        # Wire up
        self.familySwitch.toggled.connect(self._on_family_switch)        # Layout right
        rw.addWidget(lbl)
        rw.addWidget(centerRow, 0, Qt.AlignHCenter)
        rw.addWidget(self.scroll, 1)

        # New Page Navigation with Arrows
        nav_widget = QtWidgets.QWidget(objectName="presetNav")
        nav_layout = QtWidgets.QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(16)
        nav_layout.setAlignment(Qt.AlignCenter)

        self.btn_page_left = QtWidgets.QPushButton("<")
        self.btn_page_left.setObjectName("presetNavButton")
        self.btn_page_left.setCursor(Qt.PointingHandCursor)

        self.lbl_page_title = QtWidgets.QLabel()
        self.lbl_page_title.setObjectName("presetPageTitle")

        self.btn_page_right = QtWidgets.QPushButton(">")
        self.btn_page_right.setObjectName("presetNavButton")
        self.btn_page_right.setCursor(Qt.PointingHandCursor)

        nav_layout.addWidget(self.btn_page_left)
        nav_layout.addWidget(self.lbl_page_title)
        nav_layout.addWidget(self.btn_page_right)

        # Connect signals
        self.btn_page_left.clicked.connect(lambda: self._navigate_presets(-1))
        self.btn_page_right.clicked.connect(lambda: self._navigate_presets(1))

        # Add the new navigation widget and set its initial state
        rw.addWidget(nav_widget, 0, Qt.AlignHCenter)
        self._update_preset_nav_ui() # Set initial state

        ro.addWidget(right_wrap)

        splitter.addWidget(left_wrap)
        splitter.addWidget(right_outer)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        p_outer.addWidget(splitter, 1)

        self.tabs.addTab(presets_tab, "")

        # Sync tabs
        self.topTabs.currentChanged.connect(self.tabs.setCurrentIndex)
        self.tabs.currentChanged.connect(self.topTabs.setCurrentIndex)
        self.topTabs.setCurrentIndex(0)

        # Footer
        footer = QtWidgets.QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(12)

        self.status_label = QtWidgets.QLabel("Ready. Drag & drop nvram.txt files here to load.")
        footer.addWidget(self.status_label)
        footer.addStretch(1)

        # Action buttons - SCEWIN Import/Export + File operations
        self.btn_import = QtWidgets.QPushButton("Import (SCEWIN)")
        self.btn_export = QtWidgets.QPushButton("Export (SCEWIN)")
        self.btn_load = QtWidgets.QPushButton("Load File")
        self.btn_save = QtWidgets.QPushButton("Save File")
        self.btn_apply = QtWidgets.QPushButton("Apply Config")
        self.btn_reset = QtWidgets.QPushButton("Reset")

        # Connect button actions
        self.btn_import.clicked.connect(self.import_scewin)
        self.btn_export.clicked.connect(self.export_scewin)
        self.btn_load.clicked.connect(self.load_file)
        self.btn_save.clicked.connect(self.save_file)
        self.btn_apply.clicked.connect(self.apply_config)
        self.btn_reset.clicked.connect(self.reset_config)

        # Add buttons to footer (Apply at very right, Reset to its left)
        for b in (self.btn_import, self.btn_export, self.btn_load, self.btn_save, self.btn_reset, self.btn_apply):
            footer.addWidget(b)

        root.addLayout(footer)

        # Autoload and columns
        self.try_autoload()
        QtCore.QTimer.singleShot(50, self.tune_columns)

        # Shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+O"), self, activated=self.load_file)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+S"), self, activated=self.save_file)

        # Overlay for dialogs
        self._overlay = DimOverlay(self)

        # Initialize loading components
        self._init_loading_components()
        
        # Professional toast system
        self.toast = ProToastManager(self)
        
        # Premium fade-in animation
        self._init_fade_in_animation()


    def _init_loading_components(self) -> None:
        """Initialize loading spinners and progress bars for better UX"""
        # Main loading spinner for file operations
        self.loading_spinner = LoadingSpinner(self, size=32, color=THEME['accent'])
        self.loading_spinner.hide()
        
        # Progress bar for import/export operations
        self.progress_bar = ProgressBar(self)
        self.progress_bar.hide()
        
        # Loading overlay for blocking operations
        self.loading_overlay = QtWidgets.QWidget(self)
        self.loading_overlay.setStyleSheet(f"""
            QWidget {{
                background: rgba(10, 14, 19, 200);
                border-radius: 12px;
            }}
        """)
        self.loading_overlay.hide()
        
        # Loading content layout
        loading_layout = QtWidgets.QVBoxLayout(self.loading_overlay)
        loading_layout.setAlignment(Qt.AlignCenter)
        
        # Loading text
        self.loading_text = QtWidgets.QLabel("Processing...")
        self.loading_text.setStyleSheet(f"""
            QLabel {{
                color: {THEME['text']};
                font-size: 16px;
                font-weight: 600;
                background: transparent;
            }}
        """)
        self.loading_text.setAlignment(Qt.AlignCenter)
        
        # Loading spinner for overlay
        self.overlay_spinner = LoadingSpinner(self, size=40, color=THEME['accent'])
        
        loading_layout.addWidget(self.overlay_spinner)
        loading_layout.addWidget(self.loading_text)
        loading_layout.addWidget(self.progress_bar)
        
        # Position overlay to cover the main content area
        self.loading_overlay.setGeometry(24, 20, self.width() - 48, self.height() - 40)
        
    def resizeEvent(self, event):
        """Handle window resize to update loading overlay position"""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay') and self.loading_overlay.isVisible():
            self.loading_overlay.setGeometry(24, 20, self.width() - 48, self.height() - 40)

    def _init_fade_in_animation(self) -> None:
        """Premium fade-in animation for polished startup."""
        opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)

        self._startup_fade = QtCore.QPropertyAnimation(opacity_effect, b"opacity")
        self._startup_fade.setDuration(300)
        self._startup_fade.setStartValue(0.0)
        self._startup_fade.setEndValue(1.0)
        self._startup_fade.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        QtCore.QTimer.singleShot(0, self._startup_fade.start)

    def show_loading(self, text: str = "Processing...", show_progress: bool = False) -> None:
        """Show loading overlay with optional progress bar"""
        self.loading_text.setText(text)
        self.loading_overlay.show()
        self.overlay_spinner.start()
        
        if show_progress:
            self.progress_bar.show()
            self.progress_bar.setValue(0)
        else:
            self.progress_bar.hide()
            
        # Update overlay position
        self.loading_overlay.setGeometry(24, 20, self.width() - 48, self.height() - 40)
        
    def hide_loading(self) -> None:
        """Hide loading overlay"""
        self.loading_overlay.hide()
        self.overlay_spinner.stop()
        self.progress_bar.hide()
        
    def update_progress(self, value: int, maximum: int = 100) -> None:
        """Update progress bar value"""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

    def _navigate_presets(self, delta: int) -> None:
            """Navigate between preset pages using a delta (-1 for left, +1 for right)."""
            current_index = self.pages.currentIndex()
            new_index = current_index + delta
            # Clamp index between 0 and the number of pages - 1
            new_index = max(0, min(self.pages.count() - 1, new_index))
            
            if new_index != current_index:
                self.pages.setCurrentIndex(new_index)
                # Reset scroll position to top when switching pages
                self.scroll.verticalScrollBar().setValue(0)
                QtCore.QTimer.singleShot(0, self.scrollContent.updateGeometry)
                self._update_preset_nav_ui()

    def _update_preset_nav_ui(self) -> None:
            """Update the arrow buttons and title based on the current page."""
            index = self.pages.currentIndex()
            
            # Update title and button enabled states
            if index == 0:
                self.lbl_page_title.setText("Basic Presets")
                self.btn_page_left.setEnabled(False)
                self.btn_page_right.setEnabled(True)
            else:  # index == 1
                self.lbl_page_title.setText("Advanced Presets")
                self.btn_page_left.setEnabled(True)
                self.btn_page_right.setEnabled(False)

    # ---------- Style ----------
    def _stylesheet(self) -> str:
        t = THEME
        # SCROLLBAR - ABSOLUTE FINAL ATTEMPT WITH MAXIMUM ROUNDING
        scrollbars = f"""
        QScrollBar:vertical {{
            background: transparent;
            width: 14px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical {{
            background: {THEME['input_border']};
            min-height: 80px;
            border-radius: 7px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {THEME['input_focus']};
        }}
        QScrollBar::handle:vertical:pressed {{
            background: {THEME['accent']};
        }}
        QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {{
            border: none;
            background: none;
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QScrollBar:horizontal {{
            background: transparent;
            height: 14px;
            margin: 2px;
        }}
        QScrollBar::handle:horizontal {{
            background: {THEME['input_border']};
            min-width: 80px;
            border-radius: 7px;
            margin: 2px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {THEME['input_focus']};
        }}
        QScrollBar::handle:horizontal:pressed {{
            background: {THEME['accent']};
        }}
        QScrollBar::sub-line:horizontal, QScrollBar::add-line:horizontal {{
            border: none;
            background: none;
            width: 0px;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        """

        return (
            f"""
            /* Global 12px rounded corners - single source of truth */
            * {{
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}

            /* Core widgets with global radius */
            QWidget, QFrame, QGroupBox, QTabWidget::pane, QTabBar::tab,
            QPushButton, QLineEdit, QComboBox, QListView, QTreeView, QTableView,
            QScrollArea, QToolButton, QMenu, QDialog, QStatusBar {{
                border-radius: 12px;
            }}

            QWidget {{ background-color: {t['bg']}; color: {t['text']}; }}
            QLabel {{ background: transparent; border-radius: 0px; }}

            /* Header - completely transparent, no box */
            QWidget#header {{ background:none !important; border:none !important; padding:2px; }}
            QWidget#header * {{ background:transparent !important;}}
            QLabel#title {{
                font-size:24px;
                font-weight:700;
                color:{t['text']};
                letter-spacing:-0.5px;
                background:none !important;
                border:none !important;
                padding:0px !important;
                margin:0px !important;
            }}
            QLabel#counts {{ color:{t['muted']}; font-size:13px; }}

            /* Top tabs - outline style with transparent fill and thin underline indicator */
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
            }}

            /* Search input - outline style with transparent fill */
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
                border: 2px solid {t['input_focus']};
                background: transparent;
            }}

            /* Tables with hover effects */
            QTableView#cardTable {{
                background:{t['bg']};
                border:1px solid {t['border']};
                border-radius:12px;
                selection-background-color:{t['selection']};
                outline:0;
                padding:0px 0px 8px 0px;
            }}
            QTableView#cardTable::item {{
                padding:8px;
                border:0;
                border-bottom:1px solid {t['grid']};
                margin:0px;
            }}
            QTableView#cardTable::item:hover {{ background:{t['card_hover']}; }}

            QHeaderView::section {{ background:{t['card']}; color:{t['muted']}; border:0; border-right:1px solid {t['border']};
                                     padding:14px; font-weight:600; text-transform:uppercase; font-size:12px; letter-spacing:0.5px; }}
            QHeaderView::section:hover {{ background:{t['card_hover']}; }}
            QHeaderView::section:first {{ border-top-left-radius:12px; }}
            QHeaderView::section:last {{ border-top-right-radius:12px; border-right:0; }}
            QTableCornerButton::section {{ background:{t['card']}; border:0; border-top-left-radius:12px; }}

            /* Preset table */
            QTableView#presetListTable {{
                background:{t['bg']};
                border:1px solid {t['border']};
                border-radius:12px;
                selection-background-color:{t['selection']};
                outline:0;
                padding:0px 0px 8px 0px;
            }}
            QTableView#presetListTable::item {{
                padding:8px;
                border:0;
                border-bottom:1px solid {t['grid']};
                margin:0px;
            }}
            QTableView#presetListTable::item:hover {{ background:{t['card_hover']}; }}

            /* Side panel - fully separated */
            QFrame#sideOuter {{
                background:{t['card']};
                border:1px solid {t['border']};
                border-radius:18px;
            }}
            QFrame#sideCard {{ background:transparent; border:0; }}

            /* Buttons - outline style with transparent fill */
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
            }}

            /* Placeholder */
            QLabel#placeholder {{ color:{t['muted']}; font-size:15px; }}

            ToggleSwitch, ToggleSwitch * {{ background: transparent; border: 0; }}
            {scrollbars}

            /* Preset Page Navigation Arrows */
            QWidget#presetNav {{ background: transparent; }}
            QLabel#presetPageTitle {{
                font-size: 14px;
                font-weight: 600;
                color: {{t['text']}};
                background: transparent;
            }}
            QPushButton#presetNavButton {{
                background: transparent;
                color: {{t['muted']}};
                border: 1px solid {{t['border']}};
                font-size: 16px;
                font-weight: bold;
                min-width: 36px;
                max-width: 36px;
                min-height: 36px;
                max-height: 36px;
                border-radius: 18px; /* Makes it a circle */
            }}
            QPushButton#presetNavButton:hover {{
                background: {{t['card_hover']}};
                color: {{t['accent_hover']}}; /* This is the blue hover color */
                border-color: {{t['accent']}};
            }}
            QPushButton#presetNavButton:pressed {{
                background: {{t['card']}};
            }}
            QPushButton#presetNavButton:disabled {{
                color: {{t['border']}};
                background: transparent;
            }}
            """
        )

    def tune_columns(self) -> None:
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        h.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(1, 260)
        h.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        h.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(3, 120)

    def _force_edit_col1(self, idx: QtCore.QModelIndex) -> None:
        if idx.column() == 1:
            self.table.edit(idx)

    def _require_file_loaded(self) -> bool:
        """Check if file is loaded, show dialog if not"""
        if not self.file_loaded:
            self._show_no_file_dialog()
            return False
        return True

    # -------- Actions --------
    def status(self, msg: str) -> None:
        self.status_label.setText(msg)

    def try_autoload(self) -> None:
        if DEFAULT_NVRAM_PATH.exists():
            try:
                self.load_path(DEFAULT_NVRAM_PATH)
            except Exception as e:
                self.status(f"Autoload failed: {e}")

    def _show_no_file_dialog(self):
        """Show professional 'No file loaded' dialog"""
        dialog = NoFileLoadedDialog(self)
        dialog.load_file_requested.connect(self.load_file)
        dialog.import_requested.connect(self.import_scewin)
        dialog.export_requested.connect(lambda: self._export_from_dialog(dialog))
        dialog.file_dropped.connect(self.load_path)
        dialog.exec()

    def _export_from_dialog(self, dialog: NoFileLoadedDialog) -> None:
        """
        Export SCEWIN from the No File Loaded dialog
        - Disables dialog buttons
        - Shows inline spinner
        - Closes dialog on success
        - Keeps dialog open on failure
        """
        # Locate SCEWIN executable
        exe = SCEWIN_EXE_PATH if SCEWIN_EXE_PATH.exists() else None
        if exe is None:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                dialog, "Select SCEWIN_64.exe", str(BASE_DIR),
                "Executable (SCEWIN_64.exe);;All files (*.*)"
            )
            if not path:
                self.notifications.notify_error("SCEWIN_64.exe not found")
                return
            exe = Path(path)

        # Disable dialog buttons and show progress
        dialog.load_btn.setEnabled(False)
        dialog.export_btn.setEnabled(False)
        dialog.export_btn.setText("Exporting...")

        # Store dialog reference and operation type
        self._dialog_export_context = dialog
        self._current_scewin_operation = "export_from_dialog"
        self._export_exe_path = exe

        # Execute non-blocking export
        logging.info("Starting export from BIOS (from dialog)")
        self.scewin_runner.run_export(DEFAULT_NVRAM_NAME, exe)
        self.status("Exporting BIOS settings...")

    def import_scewin(self) -> None:
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
            "Import settings to BIOS using SCEWIN?\n\nThis will modify your BIOS configuration.\nMake sure you have a backup.",
            "Import",
            "Cancel"
        )
        
        if not confirmed:
            return

        # Locate SCEWIN executable
        exe = SCEWIN_EXE_PATH if SCEWIN_EXE_PATH.exists() else None
        if exe is None:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select SCEWIN_64.exe", str(BASE_DIR),
                "Executable (SCEWIN_64.exe);;All files (*.*)"
            )
            if not path:
                self.notifications.notify_error("SCEWIN_64.exe not found")
                return
            exe = Path(path)

        # Create nvram_tuned.txt file in the same directory as SCEWIN
        # Only include modified/applied settings (like save_file does)
        rows = self.model.modified_rows()
        if not rows:
            self.status("No changes to import.")
            self.notifications.notify_info("No changes to import", duration_ms=2500)
            return
            
        nvram_tuned_path = exe.parent / "nvram_tuned.txt"
        try:
            # Create content with only modified settings (same logic as save_file)
            blocks: List[str] = []
            for r in rows:
                blocks.extend(rewrite_block_with_change(self.model._rows[r]))
                blocks.append("")  # separator
            
            header = HEADER_TEMPLATE.format(
                fname="nvram_tuned.txt",
                date=datetime.now().strftime("%m/%d/%y"),
                time=datetime.now().strftime("%H:%M:%S"),
            )
            content = header + "\n".join(blocks)
            
            with open(nvram_tuned_path, 'w', encoding='utf-8') as target_file:
                target_file.write(content)
            
            logging.info(f"Created nvram_tuned.txt at: {nvram_tuned_path} with {len(rows)} modified settings")
        except Exception as e:
            logging.error(f"Failed to create nvram_tuned.txt: {e}")
            self.notifications.notify_error(f"Failed to create nvram_tuned.txt: {e}")
            return

        # Disable import button and show progress (confirmation already done above)
        self.btn_import.setEnabled(False)
        self.btn_import.setText("Importing...")
        self._current_scewin_operation = "import"

        # Execute non-blocking import using the created nvram_tuned.txt file
        logging.info(f"Starting import: {nvram_tuned_path}")
        self.scewin_runner.run_import(nvram_tuned_path, exe)
        self.status(f"Importing {self.current_path.name} to BIOS...")

    def export_scewin(self) -> None:
        """
        Professional SCEWIN export with QProcess and success feedback
        - Non-blocking execution
        - Progress feedback
        - Success toast with "Reveal" action
        """
        # Locate SCEWIN executable
        exe = SCEWIN_EXE_PATH if SCEWIN_EXE_PATH.exists() else None
        if exe is None:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select SCEWIN_64.exe", str(BASE_DIR),
                "Executable (SCEWIN_64.exe);;All files (*.*)"
            )
            if not path:
                self.notifications.notify_error("SCEWIN_64.exe not found")
                return
            exe = Path(path)

        # Disable export button and show progress
        self.btn_export.setEnabled(False)
        self.btn_export.setText("Exporting...")
        self._current_scewin_operation = "export"
        self._export_exe_path = exe  # Store for later use

        # Execute non-blocking export
        logging.info("Starting export from BIOS")
        self.scewin_runner.run_export(DEFAULT_NVRAM_NAME, exe)
        self.status("Exporting BIOS settings...")

    def _on_scewin_finished(self, result: ScewinResult):
        """
        Handle SCEWIN operation completion
        - Re-enable buttons
        - Show success or error notification
        - Load exported file if needed
        """
        operation = self._current_scewin_operation

        # Re-enable buttons
        self.btn_import.setEnabled(True)
        self.btn_import.setText("Import (SCEWIN)")
        self.btn_export.setEnabled(True)
        self.btn_export.setText("Export (SCEWIN)")

        if result.success:
            if operation == "import":
                self.status("Import successful!")
                self.notifications.notify_success("BIOS settings imported successfully")
                logging.info("Import completed successfully")

            elif operation == "export":
                self.status("Export successful!")
                exported_path = self._export_exe_path.parent / DEFAULT_NVRAM_NAME

                # Success toast - compact, text only
                self.notifications.notify_success(
                    "Exported successfully",
                    duration_ms=3000
                )
                logging.info(f"Export completed: {exported_path}")

                # Auto-load the exported file (without showing "Loaded" toast)
                try:
                    txt = exported_path.read_text(encoding="utf-8", errors="ignore")
                    settings = parse_scewin_nvram(txt)
                    self.model.load(settings)
                    self.current_path = exported_path
                    self.file_loaded = True
                    self.table.horizontalHeader().setVisible(True)
                    self.table.setVisible(True)
                    self.empty_main.setVisible(False)
                    self.update_counts()
                    self.status(f"Loaded: {exported_path.name} ({len(settings)} settings).")
                    self.tune_columns()
                except Exception as e:
                    logging.error(f"Failed to load exported file: {e}")

            elif operation == "export_from_dialog":
                self.status("Export successful!")
                exported_path = self._export_exe_path.parent / DEFAULT_NVRAM_NAME

                # Success toast - compact, text only
                self.notifications.notify_success(
                    "Exported successfully",
                    duration_ms=3000
                )
                logging.info(f"Export completed: {exported_path}")

                # Close the dialog
                if hasattr(self, '_dialog_export_context'):
                    self._dialog_export_context.accept()
                    delattr(self, '_dialog_export_context')

                # Auto-load the exported file (without showing "Loaded" toast)
                try:
                    txt = exported_path.read_text(encoding="utf-8", errors="ignore")
                    settings = parse_scewin_nvram(txt)
                    self.model.load(settings)
                    self.current_path = exported_path
                    self.file_loaded = True
                    self.table.horizontalHeader().setVisible(True)
                    self.table.setVisible(True)
                    self.empty_main.setVisible(False)
                    self.update_counts()
                    self.status(f"Loaded: {exported_path.name} ({len(settings)} settings).")
                    self.tune_columns()
                except Exception as e:
                    logging.error(f"Failed to load exported file: {e}")
        else:
            # Error handling
            error_msg = result.error_message or f"Exit code: {result.exit_code}"

            if operation == "import":
                self.status(f"Import failed: {error_msg}")
                self.notifications.notify_error("Import failed", details=error_msg)
                logging.error(f"Import failed: {error_msg}")

            elif operation == "export":
                self.status(f"Export failed: {error_msg}")
                self.notifications.notify_error("Export failed", details=error_msg)
                logging.error(f"Export failed: {error_msg}")

            elif operation == "export_from_dialog":
                self.status(f"Export failed: {error_msg}")
                self.notifications.notify_error("Export failed", details=error_msg)
                logging.error(f"Export failed: {error_msg}")

                # Re-enable dialog buttons on failure
                if hasattr(self, '_dialog_export_context'):
                    self._dialog_export_context.load_btn.setEnabled(True)
                    self._dialog_export_context.export_btn.setEnabled(True)
                    self._dialog_export_context.export_btn.setText("Export (SCEWIN)")

        self._current_scewin_operation = None

    def load_file(self) -> None:
        start = str(self.current_path.parent if self.current_path else BASE_DIR)
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open nvram.txt", start, "Text (*.txt);;All files (*.*)")
        if not path:
            return
        self.load_path(Path(path))

    def load_path(self, path: Path) -> None:
        self.table.setUpdatesEnabled(False)
        try:
            txt = path.read_text(encoding="utf-8", errors="ignore")
            settings = parse_scewin_nvram(txt)
            self.model.load(settings)
            self.current_path = path
            self.file_loaded = True  # Mark file as loaded
            self.table.horizontalHeader().setVisible(True)
            self.table.setVisible(True)
            self.empty_main.setVisible(False)
            self.update_counts()
            self.status(f"Loaded: {path.name} ({len(settings)} settings).")
            self.tune_columns()

            # Show success toast
            self.notifications.notify_success(f"Loaded {path.name}", duration_ms=2200)
        finally:
            self.table.setUpdatesEnabled(True)

    def save_file(self) -> None:
        rows = self.model.modified_rows()
        if not rows:
            self.status("No changes to save.")
            return
        blocks: List[str] = []
        for r in rows:
            blocks.extend(rewrite_block_with_change(self.model._rows[r]))
            blocks.append("")  # separator
        header = HEADER_TEMPLATE.format(
            fname=DEFAULT_NVRAM_NAME,
            date=datetime.now().strftime("%m/%d/%y"),
            time=datetime.now().strftime("%H:%M:%S"),
        )
        content = header + "\n".join(blocks)
        start = str(self.current_path.parent if self.current_path else BASE_DIR)
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save nvram.txt (only edited settings)",
            os.path.join(start, DEFAULT_NVRAM_NAME),
            "Text (*.txt)",
        )
        if not save_path:
            return
        Path(save_path).write_text(content, encoding="utf-8")
        self.status(f"Saved: {Path(save_path).name} ({len(rows)} edited settings).")

        # Show success toast with elided path
        path_str = str(Path(save_path))
        if len(path_str) > 50:
            path_str = path_str[:25] + "..." + path_str[-22:]

        self.notifications.notify_success(f"Saved file to {path_str}", duration_ms=2500)

    # -------- Presets logic --------
    def _current_basic_map(self) -> Dict[str, Dict[str, Any]]:
        return INTEL_PRESETS_BASIC if self._preset_family == "intel" else AMD_PRESETS_BASIC

    def _current_adv_map(self) -> Tuple[List[str], Dict[str, Dict[str, Any]], Dict[str, bool]]:
        if self._preset_family == "intel":
            return PRESET_ORDER_ADV_INTEL, INTEL_PRESETS_ADV, self._enabled_adv_intel
        return PRESET_ORDER_ADV_AMD, AMD_PRESETS_ADV, self._enabled_adv_amd

    def _build_adv_page_for_family(self, fam: str) -> None:
        # clear layout
        while self.adv_layout.count():
            item = self.adv_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        if fam == "intel":
            self.rows_adv_intel = {}
            for name in PRESET_ORDER_ADV_INTEL:
                r = PresetRow(name, on=self._enabled_adv_intel.get(name, False))
                r.toggled.connect(lambda _name, state, n=name: self._on_adv_specific_toggle("intel", n, state))
                self.rows_adv_intel[name] = r
                self.adv_layout.addWidget(r, 0, Qt.AlignTop)  # Align to top
        else:
            self.rows_adv_amd = {}
            for name in PRESET_ORDER_ADV_AMD:
                r = PresetRow(name, on=self._enabled_adv_amd.get(name, False))
                r.toggled.connect(lambda _name, state, n=name: self._on_adv_specific_toggle("amd", n, state))
                self.rows_adv_amd[name] = r
                self.adv_layout.addWidget(r, 0, Qt.AlignTop)  # Align to top

    def _revert_row_switch(self, row: PresetRow, target_state: bool) -> None:
        row.sw.blockSignals(True)
        row.sw.setChecked(target_state)
        row.sw.blockSignals(False)

    def _on_preset_toggle_basic(self, preset_name: str, enabled: bool) -> None:
        if not self._require_file_loaded():
            self._revert_row_switch(self.rows_basic[preset_name], False)
            return

        self._enabled_basic[preset_name] = enabled
        self._rebuild_preset_view_and_targets()

    def _on_adv_specific_toggle(self, family: str, preset_name: str, enabled: bool) -> None:
        if not self._require_file_loaded():
            rows = self.rows_adv_intel if family == "intel" else self.rows_adv_amd
            self._revert_row_switch(rows[preset_name], False)
            return

        if family == "intel":
            self._enabled_adv_intel[preset_name] = enabled
        else:
            self._enabled_adv_amd[preset_name] = enabled
        self._rebuild_preset_view_and_targets()

    def _rebuild_preset_view_and_targets(self) -> None:
        combined: Dict[str, Any] = {}

        basic_map = self._current_basic_map()
        for name in PRESET_ORDER_BASIC:
            if self._enabled_basic.get(name):
                combined.update(basic_map.get(name, {}))

        order, adv_map, enabled_map = self._current_adv_map()
        
        # GUARD: Ensure correct family data is used
        if self._preset_family == "amd":
            assert adv_map is AMD_PRESETS_ADV, "AMD family must use AMD_PRESETS_ADV"
        else:
            assert adv_map is INTEL_PRESETS_ADV, "Intel family must use INTEL_PRESETS_ADV"
        
        for name in order:
            if enabled_map.get(name):
                combined.update(adv_map.get(name, {}))

        combined_norm = build_normalized_map(combined)

        rows = []
        for i, s in enumerate(self.model._rows):
            if normalize_key(s.name) in combined_norm:
                rows.append(i)

        self.pending_targets = {}
        for r in rows:
            nk = normalize_key(self.model._rows[r].name)
            _, val = combined_norm[nk]
            self.pending_targets[r] = val

        visible_names = {self.model._rows[r].name for r in self.pending_targets.keys()}
        self.presetProxy.setNameSet({n.lower() for n in visible_names})
        has_any = bool(self.pending_targets)
        self.presetTable.horizontalHeader().setVisible(has_any)
        self.preset_placeholder.setVisible(not has_any)
        self.presetTable.setVisible(has_any)

        fam = "Intel" if self._preset_family == "intel" else "AMD"
        self.status(f"{fam} presets: {len(self.pending_targets)} item(s).")

    def clear_preset_list(self) -> None:
        # clear all toggles across both pages
        for k in list(self._enabled_basic.keys()):
            self._enabled_basic[k] = False
            self._revert_row_switch(self.rows_basic[k], False)

        for k in list(self._enabled_adv_intel.keys()):
            self._enabled_adv_intel[k] = False
        for k in list(self._enabled_adv_amd.keys()):
            self._enabled_adv_amd[k] = False

        # rebuild current adv page to reflect cleared state
        self._build_adv_page_for_family(self._preset_family)

        self.presetProxy.setNameSet(None)
        self.pending_targets.clear()
        self.presetTable.setVisible(False)
        self.presetTable.horizontalHeader().setVisible(False)
        self.preset_placeholder.setVisible(True)
        self.status("Preset list cleared.")

    def _on_family_switch(self, on: bool) -> None:
        fam = "amd" if on else "intel"
        self._preset_family = fam
        self.familyLabel.setText("AMD" if on else "Intel")
        self._build_adv_page_for_family(fam)
        self._rebuild_preset_view_and_targets()

    def _apply_targets_now(self) -> int:
        def _norm_label(x: str) -> str:
            t = x.strip().lower()
            if t in BOOL_TRUE:  t = "enabled"
            if t in BOOL_FALSE: t = "disabled"
            return t

        def _detect_value_type(setting: Setting, target_val: str) -> tuple[str, str]:
            """
            Detect value type from NVRAM block context
            Returns: (formatted_value, type_name)
            """
            val_str = str(target_val).strip()

            # 1. Check NVRAM block for existing format hints
            for line in setting.block_lines:
                if "Value" in line and "=" in line:
                    # Extract current value format
                    value_part = line.split("=", 1)[1].split("//")[0].strip()

                    # Decimal format: Value = <123>
                    if value_part.startswith("<") and value_part.endswith(">"):
                        # Preset says "0" or "Disable" → convert to <0>
                        if val_str.lower() in {"0", "disable", "disabled"}:
                            return ("<0>", "decimal")
                        try:
                            num = int(val_str, 10)
                            return (f"<{num}>", "decimal")
                        except:
                            return (f"<{val_str}>", "decimal")

                    # Boolean format: Value = 0 // Enabled = 1, Disabled = 0
                    if "//" in line and ("Enabled" in line or "Disabled" in line):
                        # Preset says "Disable" → 0, "Enable" → 1
                        if val_str.lower() in {"0", "disable", "disabled", "off"}:
                            return ("0", "boolean")
                        if val_str.lower() in {"1", "enable", "enabled", "on"}:
                            return ("1", "boolean")
                        return (val_str, "boolean")

                    # Hex format: Value = 80008000 (8+ hex chars)
                    if re.fullmatch(r"[0-9A-Fa-f]{4,}", value_part):
                        # Preserve hex format
                        if val_str.lower().startswith("0x"):
                            val_str = val_str[2:]
                        return (val_str.upper(), "hex")

                    break

            # 2. Fallback: guess from target value
            if val_str.lower().startswith("0x"):
                return (val_str[2:].upper(), "hex")

            if re.fullmatch(r"[0-9A-Fa-f]{8,}", val_str):
                return (val_str.upper(), "hex")

            try:
                int(val_str, 10)
                return (f"<{val_str}>", "decimal")
            except:
                return (val_str, "text")

        changed = 0
        for row, target in self.pending_targets.items():
            s = self.model._rows[row]

            if s.kind is SettingKind.OPTIONS:
                desired_labels = target if isinstance(target, list) else [target]
                desired_labels = [str(l) for l in desired_labels]

                # 1) Wenn der aktuelle Wert bereits einem gewünschten entspricht → nichts tun, kein Fallback
                if any(_norm_label(s.current_label) == _norm_label(lab) for lab in desired_labels):
                    continue

                # 2) Versuche eine der gewünschten Optionen zu setzen (per Label ODER Code)
                applied_here = False
                for lab in desired_labels:
                    if self.model.setData(self.model.index(row, 1), lab, Qt.EditRole):
                        applied_here = True
                        break

                # 3) Nur wenn nichts passte, ganz zum Schluss Fallback auf "Disabled"-Index
                if not applied_here:
                    idx = self.model._disabled_index_for(s)
                    if idx is not None and idx != s.current_index:
                        s.current_index = idx
                        self.model._update_sets_after_edit(row)
                        applied_here = True

                if applied_here:
                    changed += 1

            else:
                # VALUE - intelligente Typ-Erkennung
                # Wenn target eine Liste ist, nimm ersten Wert
                val_raw = target[0] if isinstance(target, list) else target

                # Erkenne Datentyp und formatiere entsprechend
                formatted_val, val_type = _detect_value_type(s, str(val_raw))

                # Logging für Debugging
                logging.debug(f"Setting '{s.name}': {val_raw} → {formatted_val} (type: {val_type})")

                # Wenn der Wert schon identisch ist, nichts tun
                # --- Preserve angle brackets if the existing cell used them
                existing = str(s.value or "").strip()
                uses_brackets = existing.startswith("<") and existing.endswith(">")
                formatted_core = formatted_val.strip("<>")
                formatted_with_style = f"<{formatted_core}>" if uses_brackets else formatted_core

                # If compare ignores brackets, keep that, but set with the preserved style
                current_val = str(s.value or "").strip().strip("<>")
                check_val = formatted_core
                if current_val == check_val:
                    continue

                # Set with preserved style
                if self.model.setData(self.model.index(row, 1), formatted_with_style, Qt.EditRole):
                    changed += 1

        return changed

    # Note: show_glow_error replaced by NotificationManager.notify_error()
    # Kept for backward compatibility during transition
    def show_glow_error(self, title: str, text: str):
        self.notifications.notify_error(text, details=title if title != text else None)

    def apply_config(self) -> None:
        if self.model.rowCount() == 0:
            self._show_no_file_dialog()
            return
        
        # Track which presets are being applied
        active_presets = []
        if self.pending_targets:
            # Get active basic presets
            for name in PRESET_ORDER_BASIC:
                if self._enabled_basic.get(name):
                    active_presets.append(name)
            
            # Get active advanced presets
            order, _, enabled_map = self._current_adv_map()
            for name in order:
                if enabled_map.get(name):
                    family_label = "AMD" if self._preset_family == "amd" else "Intel"
                    active_presets.append(f"{family_label} {name}")
            
            ch = self._apply_targets_now()
            self.status(f"Preset staged {ch} change(s).")
        
        cnt = self.model.apply_staged()
        self.update_counts()
        
        # Enhanced status and notification
        if cnt == 0:
            self.status("No changes to apply.")
            self.notifications.notify_info("No changes to apply", duration_ms=2500)
        else:
            change_word = "change" if cnt == 1 else "changes"
            
            # Build status message with preset info
            if active_presets:
                preset_list = ", ".join(active_presets[:3])  # Show first 3
                if len(active_presets) > 3:
                    preset_list += f" +{len(active_presets) - 3} more"
                self.status(f"Applied {cnt} {change_word}: {preset_list}")
                self.notifications.notify_success(
                    f"Applied {cnt} {change_word}",
                    subtitle=preset_list if len(preset_list) < 50 else None,
                    duration_ms=3500
                )
            else:
                self.status(f"Applied {cnt} {change_word}.")
                self.notifications.notify_success(f"Applied {cnt} {change_word}", duration_ms=3500)

    def reset_config(self) -> None:
        """Full app reset: settings, presets, search, filters, counters"""
        if self.model.rowCount() == 0:
            self._show_no_file_dialog()
            return
        
        # Show custom confirmation modal
        confirmed = OutlineConfirmDialog.confirm(
            self,
            "Reset All Settings",
            "This will revert all settings, presets, and applied changes back to default.\n\nContinue?",
            "Reset",
            "Cancel"
        )
        
        if not confirmed:
            return
        
        # FULL RESET - same as app restart
        
        # 1. Reset all modified settings to original values
        reset_count = 0
        for row in self.model.modified_rows():
            setting = self.model._rows[row]
            
            # Reset OPTIONS type settings to original index
            if setting.kind is SettingKind.OPTIONS and setting._orig_index is not None:
                if setting.current_index != setting._orig_index:
                    setting.current_index = setting._orig_index
                    reset_count += 1
                    self.model._invalidate_cache_for_row(row)
            
            # Reset VALUE type settings to original value
            elif setting.kind is SettingKind.VALUE and setting._orig_value is not None:
                if (setting.value or "") != (setting._orig_value or ""):
                    setting.value = setting._orig_value
                    reset_count += 1
                    self.model._invalidate_cache_for_row(row)
        
        # Clear the applied changes tracking
        self.model._applied.clear()
        self.model._staged.clear()
        
        # 2. Clear ALL presets (Basic + Advanced)
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
        
        # Rebuild advanced presets to reflect cleared state
        if hasattr(self, '_build_adv_page_for_family') and hasattr(self, '_preset_family'):
            self._build_adv_page_for_family(self._preset_family)
        
        # Clear preset targets and table
        if hasattr(self, 'pending_targets'):
            self.pending_targets.clear()
        
        if hasattr(self, 'presetProxy'):
            self.presetProxy.setNameSet(None)
        
        if hasattr(self, 'presetTable'):
            self.presetTable.setVisible(False)
            self.presetTable.horizontalHeader().setVisible(False)
        
        if hasattr(self, 'preset_placeholder'):
            self.preset_placeholder.setVisible(True)
        
        # 3. Clear search filter
        if hasattr(self, 'search'):
            self.search.clear()
        
        # 4. Update the UI
        self.update_counts()
        self.status(f"Full reset complete: {reset_count} settings restored, presets cleared, filters reset.")
        
        # Show success notification
        if reset_count > 0:
            self.notifications.notify_success(f"Full reset: {reset_count} settings + all presets", duration_ms=2500)
        else:
            self.notifications.notify_info("Reset complete (no changes to restore)", duration_ms=2500)

    def update_counts(self) -> None:
        edited, applied = self.model.get_counts()
        self.counts.setText(f"{edited} edited • {applied} applied")


    # --------------------------------------------------------------------------------------
    # Window Resize Support (Edges and Corners)
    # --------------------------------------------------------------------------------------

    def _get_resize_direction(self, pos):
        """Determine resize direction based on mouse position"""
        rect = self.rect()
        margin = self._resize_margin

        left = pos.x() <= margin
        right = pos.x() >= rect.width() - margin
        top = pos.y() <= margin
        bottom = pos.y() >= rect.height() - margin

        if top and left:
            return "top_left"
        elif top and right:
            return "top_right"
        elif bottom and left:
            return "bottom_left"
        elif bottom and right:
            return "bottom_right"
        elif left:
            return "left"
        elif right:
            return "right"
        elif top:
            return "top"
        elif bottom:
            return "bottom"
        return None

    def mousePressEvent(self, event):
        """Handle mouse press for resize"""
        if event.button() == Qt.LeftButton:
            self._resize_direction = self._get_resize_direction(event.position().toPoint())
            if self._resize_direction:
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geometry = self.geometry()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for resize cursor and resizing"""
        pos = event.position().toPoint()

        # Update cursor based on position
        if not event.buttons():
            direction = self._get_resize_direction(pos)
            if direction in ["top_left", "bottom_right"]:
                self.setCursor(Qt.SizeFDiagCursor)
            elif direction in ["top_right", "bottom_left"]:
                self.setCursor(Qt.SizeBDiagCursor)
            elif direction in ["left", "right"]:
                self.setCursor(Qt.SizeHorCursor)
            elif direction in ["top", "bottom"]:
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

        # Perform resize if dragging
        if event.buttons() == Qt.LeftButton and self._resize_direction:
            delta = event.globalPosition().toPoint() - self._resize_start_pos
            geo = self._resize_start_geometry
            new_geo = QtCore.QRect(geo)

            # Apply resize based on direction
            if "left" in self._resize_direction:
                new_geo.setLeft(geo.left() + delta.x())
            if "right" in self._resize_direction:
                new_geo.setRight(geo.right() + delta.x())
            if "top" in self._resize_direction:
                new_geo.setTop(geo.top() + delta.y())
            if "bottom" in self._resize_direction:
                new_geo.setBottom(geo.bottom() + delta.y())

            # Enforce minimum size
            if new_geo.width() >= self.minimumWidth() and new_geo.height() >= self.minimumHeight():
                self.setGeometry(new_geo)

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release to end resize"""
        if event.button() == Qt.LeftButton:
            self._resize_direction = None
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    # --------------------------------------------------------------------------------------
    # Drag & Drop Support
    # --------------------------------------------------------------------------------------

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            # Accept if at least one .txt file is being dragged
            if any(url.toLocalFile().lower().endswith('.txt') for url in urls):
                event.acceptProposedAction()
                self._drag_active = True
                self.drag_overlay.show_overlay(self.rect())
                self.status("Drop nvram.txt file to load it...")
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        self._drag_active = False
        self.drag_overlay.hide()
        self.status("Ready. Drag & drop nvram.txt files here to load.")

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        # Hide overlay first
        self._drag_active = False
        self.drag_overlay.hide()

        if not event.mimeData().hasUrls():
            return

        urls = event.mimeData().urls()
        # Filter for .txt files
        txt_files = [url.toLocalFile() for url in urls if url.toLocalFile().lower().endswith('.txt')]

        if not txt_files:
            self.status("Invalid file type.")
            self.notifications.notify_error("Invalid file type. Please drop a .txt file.")
            return

        # Load the first .txt file
        dropped_path = Path(txt_files[0])
        if dropped_path.exists():
            event.acceptProposedAction()
            self.status(f"Loading dropped file: {dropped_path.name}")
            try:
                self.load_path(dropped_path)
                # Success toast
                self.notifications.notify_success(f"Loaded {dropped_path.name}")
            except Exception as e:
                self.status(f"Failed to load dropped file: {e}")
                self.notifications.notify_error(f"Could not load {dropped_path.name}", details=str(e))
        else:
            self.status(f"Dropped file not found: {dropped_path.name}")
            self.notifications.notify_error(f"File not found: {dropped_path.name}")

    # --------------------------------------------------------------------------------------
    # Search Filter (Optimized with debouncing)
    # --------------------------------------------------------------------------------------

    def _on_search_changed(self) -> None:
        """Handle search text changes"""
        # Start/restart the search timer
        self._search_timer.start()

    def _apply_search_filter(self) -> None:
        """Optimized search filter with FixedString matching (much faster than regex)"""
        text = self.search.text().strip()

        # Batch the filter update to avoid multiple redraws
        self.table.setUpdatesEnabled(False)
        try:
            if not text:
                self.proxy.setFilterFixedString("")
            else:
                # Use FixedString for fast substring matching (no regex overhead)
                self.proxy.setFilterFixedString(text)
                
            # Update counts with filtered results
            self.update_counts()
        finally:
            self.table.setUpdatesEnabled(True)



# --------------------------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------------------------
def main() -> None:
    try:
        QtGui.QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except AttributeError:
        pass

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)

    win = AutoBiosWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
