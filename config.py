"""
CONFIG.PY
=========
Centralized configuration for Desktop Search Assistant

PURPOSE:
- Store all constants and settings in one place
- Make the application easily configurable
- Avoid magic numbers scattered throughout code

CONSTANTS:
- HOTKEY: Global keyboard shortcut to activate overlay
- SCREENSHOT_DIR: Where to save captured images
- OVERLAY_TRANSPARENCY: Overlay window opacity (0-255)
- OVERLAY_COLOR: Selection rectangle color (RGB)
- TEMP_FILENAME: Name of captured screenshot file
"""

# ============================================================================
# HOTKEY CONFIGURATION
# ============================================================================

HOTKEY = "ctrl+shift+s"  # Global hotkey to activate overlay
"""
Which key combination triggers the overlay.
Examples:
  - "ctrl+shift+s" - Ctrl + Shift + S
  - "alt+s" - Alt + S
  - "shift+f13" - Shift + F13
  
Note: Requires admin privileges on Windows to work globally
"""

# ============================================================================
# FILE & DIRECTORY CONFIGURATION
# ============================================================================

SCREENSHOT_DIR = "screenshots"
"""Directory where captured screenshots are saved"""

TEMP_FILENAME = "capture.png"
"""Temporary filename for captured screenshot"""

SCREENSHOT_PATH = f"{SCREENSHOT_DIR}/{TEMP_FILENAME}"
"""Full path to saved screenshot"""

# ============================================================================
# OVERLAY UI CONFIGURATION
# ============================================================================

OVERLAY_TRANSPARENCY = 50
"""
Overlay background transparency (0-255)
- 0: Fully transparent
- 255: Fully opaque
Lower values = more see-through
"""

OVERLAY_COLOR = (200, 200, 200)
"""Background color of overlay in RGB (Red, Green, Blue)"""

SELECTION_COLOR = (0, 120, 215)
"""Color of selection rectangle in RGB (Windows blue)"""

SELECTION_WIDTH = 2
"""Width of selection rectangle border in pixels"""

CURSOR_COLOR = (255, 0, 0)
"""Color of cursor crosshair in RGB (Red)"""

# ============================================================================
# OCR CONFIGURATION (Phase 2)
# ============================================================================

OCR_LANGUAGE = ["en"]
"""
Language(s) to detect in OCR
Examples: ["en"], ["en", "es"], ["zh", "ja"]
"""

OCR_GPU = False
"""
Use GPU for OCR (faster but requires CUDA)
Set to True if you have NVIDIA GPU with CUDA installed
"""

# ============================================================================
# SEARCH CONFIGURATION (Phase 3)
# ============================================================================

GOOGLE_SEARCH_URL = "https://www.google.com/search?q="
"""Base URL for Google Search"""

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

APP_NAME = "Desktop Search Assistant"
"""Application display name"""

APP_VERSION = "0.1.0"
"""Current application version"""

DEBUG_MODE = False
"""Enable debug printing (set to True for development)"""
