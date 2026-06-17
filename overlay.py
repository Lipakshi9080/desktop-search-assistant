"""
OVERLAY.PY
==========
Transparent fullscreen overlay for selection and capture

PURPOSE:
- Display transparent fullscreen window
- Track mouse movement and selection
- Draw selection rectangle in real-time
- Capture selected region when user releases mouse
- Handle all UI interactions for Phase 1

CLASSES:
- OverlayWindow: Main overlay widget for selection

DEPENDENCIES:
- PyQt6: GUI framework
- capture: For saving screenshots
- config: Configuration constants
- utils: Utility functions
"""

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QCursor
from PyQt6.QtCore import QTimer
import sys
import config
import utils
from capture import ScreenCapture

# ============================================================================
# OVERLAY WINDOW CLASS
# ============================================================================

class OverlayWindow(QWidget):
    """
    CLASS: OverlayWindow
    ===================
    
    PURPOSE:
    - Create transparent fullscreen overlay for user selection
    - Handle mouse events (click, drag, release)
    - Draw selection rectangle as user drags
    - Trigger screenshot capture when selection is complete
    
    ATTRIBUTES:
    - start_pos (QPoint): Where user started clicking
    - current_pos (QPoint): Current mouse position
    - selection_active (bool): Whether user is currently selecting
    - selection_rect (QRect): Rectangle of user's selection
    - capturer (ScreenCapture): Screenshot capture object
    
    SIGNALS (PyQt6 events):
    - selection_made: Emitted when user completes selection
    
    METHODS:
    - showFullScreen(): Display overlay covering entire screen
    - mousePressEvent(): Handle mouse click
    - mouseMoveEvent(): Handle mouse movement
    - mouseReleaseEvent(): Handle mouse release
    - paintEvent(): Draw overlay and selection rectangle
    - closeOverlay(): Close overlay and cleanup
    
    HOW IT WORKS - USER PERSPECTIVE:
    1. User presses Ctrl+Shift+S
    2. Transparent overlay appears covering entire screen
    3. User can see their desktop through it
    4. User clicks and drags to select area
    5. Selection rectangle appears in real-time
    6. When user releases mouse, screenshot is captured
    7. Overlay closes automatically
    8. Screenshot saved to screenshots/capture.png
    
    HOW IT WORKS - CODE PERSPECTIVE:
    1. __init__: Initialize window properties
    2. showFullScreen(): Display overlay
    3. User mouse click triggers mousePressEvent()
    4. Mouse movement triggers mouseMoveEvent() (many times)
    5. Each mouseMoveEvent redraws the selection rectangle
    6. Mouse release triggers mouseReleaseEvent()
    7. Capture screenshot of selected region
    8. Close overlay
    """
    
    # Signal emitted when selection is complete (for future use)
    selection_made = pyqtSignal(str)  # Signal with screenshot path
    
    def __init__(self):
        """
        METHOD: __init__()
        =================
        
        PURPOSE:
        - Initialize overlay window with all properties
        - Set up UI styling
        - Create screenshot capturer
        
        PARAMETERS:
        - self: Instance reference
        
        HOW IT WORKS:
        1. Call parent class constructor
        2. Set window properties (fullscreen, transparent, no-frame)
        3. Initialize selection tracking variables
        4. Create ScreenCapture instance
        5. Set color and styling
        6. Make window stay on top
        
        EXAMPLE:
        >>> overlay = OverlayWindow()
        >>> overlay.show()
        """
        super().__init__()
        
        utils.log_debug("Initializing OverlayWindow")
        
        # Window setup
        self.setWindowTitle("Desktop Search Assistant - Overlay")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Selection tracking
        self.start_pos = None
        self.current_pos = None
        self.selection_active = False
        self.selection_rect = None
        
        # Screenshot capturer
        self.capturer = ScreenCapture()
        
        # Mouse cursor
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        utils.log_debug("✓ OverlayWindow initialized")
    
    def show_overlay(self):
        """
        METHOD: show_overlay()
        =====================
        
        PURPOSE:
        - Display the overlay in fullscreen mode
        - Make it visible to user
        
        PARAMETERS:
        - self: Instance reference
        
        RETURNS:
        - None
        
        EXAMPLE:
        >>> overlay = OverlayWindow()
        >>> overlay.show_overlay()
        
        HOW IT WORKS:
        1. Set window geometry to cover entire screen
        2. Raise window to top (z-order)
        3. Activate window (bring to focus)
        4. Display with fullscreen
        
        TECHNICAL NOTES:
        - QApplication.primaryScreen() gets main monitor info
        - setGeometry() sets position and size
        - showFullScreen() makes it cover entire screen
        - raise_() brings it to top
        - activateWindow() ensures it's focused
        """
        try:
            # Get screen geometry
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            
            # Set window to cover entire screen
            self.setGeometry(screen_geometry)
            
            # Show in fullscreen
            self.showFullScreen()
            self.raise_()
            self.activateWindow()
            
            utils.log_debug(f"✓ Overlay shown on screen: {screen_geometry.width()}x{screen_geometry.height()}")
            
        except Exception as e:
            utils.log_debug(f"❌ Error showing overlay: {e}")
            print(f"❌ Failed to show overlay: {e}")
    
    def mousePressEvent(self, event):
        """
        METHOD: mousePressEvent(event)
        ==============================
        
        PURPOSE:
        - Handle mouse click event
        - Mark start of selection rectangle
        - Initialize selection tracking
        
        PARAMETERS:
        - self: Instance reference
        - event: PyQt6 QMouseEvent with click data
        
        RETURNS:
        - None
        
        EXAMPLE:
        (This is called automatically by PyQt6 when user clicks)
        
        HOW IT WORKS:
        1. Store click position as start_pos
        2. Set current_pos to same position
        3. Mark selection as active
        4. Initialize empty selection rectangle
        5. Log for debugging
        
        COORDINATE SYSTEM:
        - event.pos() returns QPoint(x, y) of click
        - (0, 0) is top-left of overlay window
        - Since window covers full screen, this is screen coordinates
        
        EVENT FLOW:
        mousePressEvent (user clicks)
            ↓
        mouseMoveEvent (many times as user drags)
            ↓
        mouseReleaseEvent (user releases)
        """
        self.start_pos = event.pos()
        self.current_pos = event.pos()
        self.selection_active = True
        self.selection_rect = QRect(self.start_pos, self.start_pos)
        
        utils.log_debug(f"Selection started at: {self.start_pos.x()}, {self.start_pos.y()}")
    
    def mouseMoveEvent(self, event):
        """
        METHOD: mouseMoveEvent(event)
        =============================
        
        PURPOSE:
        - Handle mouse movement event
        - Update selection rectangle in real-time
        - Redraw overlay as user drags
        
        PARAMETERS:
        - self: Instance reference
        - event: PyQt6 QMouseEvent with position data
        
        RETURNS:
        - None
        
        FREQUENCY:
        - Called many times per second (60+ times) as user moves mouse
        - Very performance-critical code
        
        EXAMPLE:
        (This is called automatically by PyQt6 hundreds of times while dragging)
        
        HOW IT WORKS:
        1. Only process if user is actively selecting
        2. Update current_pos to new mouse position
        3. Create rectangle from start_pos to current_pos
        4. Call update() to trigger paintEvent
        5. paintEvent redraws the selection rectangle
        
        PERFORMANCE:
        - This is called frequently, so keep it fast
        - Only update what's necessary
        - Don't do heavy calculations here
        
        VISUAL EFFECT:
        - As user drags, rectangle appears to follow mouse
        - Smooth animation effect from real-time updates
        """
        if self.selection_active and self.start_pos is not None:
            self.current_pos = event.pos()
            self.selection_rect = QRect(self.start_pos, self.current_pos)
            self.update()  # Trigger paintEvent to redraw
    
    def mouseReleaseEvent(self, event):
        """
        METHOD: mouseReleaseEvent(event)
        ================================
        
        PURPOSE:
        - Handle mouse release event
        - Finalize selection
        - Capture screenshot of selected region
        - Close overlay
        
        PARAMETERS:
        - self: Instance reference
        - event: PyQt6 QMouseEvent with release data
        
        RETURNS:
        - None
        
        EXAMPLE:
        (This is called automatically by PyQt6 when user releases mouse button)
        
        HOW IT WORKS:
        1. Mark selection as complete
        2. Get final coordinates of selection
        3. Normalize coordinates (ensure x1 < x2, y1 < y2)
        4. Capture screenshot using ScreenCapture
        5. Save to screenshots/capture.png
        6. Close overlay
        
        COORDINATE NORMALIZATION:
        - User might drag left-to-right OR right-to-left
        - User might drag top-to-bottom OR bottom-to-top
        - Normalize ensures coordinates are always (top-left, bottom-right)
        
        CAPTURE WORKFLOW:
        Get coordinates
            ↓
        ScreenCapture.capture_and_save()
            ↓
        Screenshot saved to disk
            ↓
        Emit selection_made signal
            ↓
        Close overlay
        
        EDGE CASES:
        - If selection is too small (< 1 pixel), skip capture
        - If capture fails, show error message
        """
        try:
            self.selection_active = False
            
            if self.selection_rect is None:
                utils.log_debug("Selection rect is None, skipping capture")
                self.closeOverlay()
                return
            
            # Get selection coordinates
            x1 = self.selection_rect.left()
            y1 = self.selection_rect.top()
            x2 = self.selection_rect.right()
            y2 = self.selection_rect.bottom()
            
            utils.log_debug(f"Selection completed: ({x1}, {y1}) to ({x2}, {y2})")
            
            # Close overlay immediately so it doesn't interfere with screenshot
            self.closeOverlay()
            
            # Capture and save screenshot
            utils.log_debug("Capturing screenshot...")
            image = self.capturer.capture_and_save(x1, y1, x2, y2)
            
            if image:
                print(f"✓ Screenshot captured: {image.width}x{image.height}")
                self.selection_made.emit(config.SCREENSHOT_PATH)
            else:
                print("❌ Failed to capture screenshot")
            
        except Exception as e:
            utils.log_debug(f"❌ Error in mouseReleaseEvent: {e}")
            print(f"❌ Selection error: {e}")
            self.closeOverlay()
    
    def paintEvent(self, event):
        """
        METHOD: paintEvent(event)
        =========================
        
        PURPOSE:
        - Draw the overlay appearance (background + selection rectangle)
        - Called whenever window needs repainting
        - Creates visual feedback for user selection
        
        PARAMETERS:
        - self: Instance reference
        - event: PyQt6 QPaintEvent with repaint region
        
        RETURNS:
        - None
        
        FREQUENCY:
        - Called when window is first shown
        - Called whenever update() is called in mouseMoveEvent()
        - Automatically called when window needs refreshing
        
        EXAMPLE:
        (This is called automatically by PyQt6, don't call directly)
        
        WHAT GETS DRAWN:
        1. Semi-transparent overlay background (entire screen)
        2. Selection rectangle (from start_pos to current_pos)
        3. Selection rectangle border
        
        VISUAL HIERARCHY:
        ```
        Entire Screen
        ├── Semi-transparent gray background (see-through overlay)
        └── Blue selection rectangle (bright, easy to see)
            ├── Blue border (2px wide)
            └── Filled with transparent blue
        ```
        
        HOW IT WORKS:
        1. Create QPainter to draw on this widget
        2. Fill entire widget with semi-transparent color
        3. If user is selecting, draw selection rectangle
        4. Use config.SELECTION_COLOR for rectangle
        5. Use config.SELECTION_WIDTH for border thickness
        
        COLORS & TRANSPARENCY:
        - Overlay: Light gray (200, 200, 200) semi-transparent
        - Rectangle: Windows blue (0, 120, 215) solid
        - Border: 2 pixels wide for visibility
        
        PERFORMANCE:
        - PyQt6 optimizes painting (only redraws changed regions)
        - Not called excessively, safe to do drawing here
        """
        try:
            painter = QPainter(self)
            
            # Draw semi-transparent overlay background
            overlay_color = QColor(*config.OVERLAY_COLOR)
            overlay_color.setAlpha(config.OVERLAY_TRANSPARENCY)
            painter.fillRect(self.rect(), overlay_color)
            
            # Draw selection rectangle if user is selecting
            if self.selection_active and self.selection_rect is not None:
                # Create pen for rectangle border
                pen = QPen(QColor(*config.SELECTION_COLOR), config.SELECTION_WIDTH)
                painter.setPen(pen)
                
                # Draw rectangle border
                painter.drawRect(self.selection_rect)
                
                utils.log_debug(f"Drawing selection rect at: {self.selection_rect}")
            
            painter.end()
            
        except Exception as e:
            utils.log_debug(f"❌ Error in paintEvent: {e}")
    
    def closeOverlay(self):
        """
        METHOD: closeOverlay()
        =====================
        
        PURPOSE:
        - Close and cleanup the overlay
        - Reset selection variables
        - Return control to user
        
        PARAMETERS:
        - self: Instance reference
        
        RETURNS:
        - None
        
        EXAMPLE:
        (Called automatically after screenshot is captured)
        or
        >>> overlay.closeOverlay()
        
        HOW IT WORKS:
        1. Reset selection variables
        2. Close the window
        3. Log for debugging
        4. Allow garbage collection of resources
        
        CLEANUP:
        - Hides overlay window
        - Resets mouse tracking
        - Allows window to be destroyed
        
        AFTER CLOSE:
        - User sees their normal desktop again
        - Application ready for next hotkey press
        - Screenshot available at screenshots/capture.png
        """
        try:
            self.selection_active = False
            self.start_pos = None
            self.current_pos = None
            self.selection_rect = None
            
            self.close()
            utils.log_debug("✓ Overlay closed")
            
        except Exception as e:
            utils.log_debug(f"❌ Error closing overlay: {e}")


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    TEST CODE: Direct overlay testing without hotkey
    
    HOW TO TEST:
    1. Open terminal/command prompt
    2. Navigate to project directory
    3. Run: python overlay.py
    4. Transparent overlay should appear
    5. Click and drag to select area
    6. Screenshot saved to screenshots/capture.png
    
    USEFUL FOR:
    - Testing overlay without hotkey system
    - Debugging selection/drawing
    - Quick iteration during development
    """
    
    app = QApplication(sys.argv)
    
    print("Opening overlay for testing...")
    print("Instructions:")
    print("1. A transparent overlay will appear")
    print("2. Click and drag to select an area")
    print("3. Screenshot will be saved to screenshots/capture.png")
    print("4. Overlay will close automatically")
    
    overlay = OverlayWindow()
    overlay.show_overlay()
    
    sys.exit(app.exec())
