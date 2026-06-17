"""
CAPTURE.PY
==========
Screenshot capture functionality for Desktop Search Assistant

PURPOSE:
- Handle capturing screenshot of selected screen region
- Convert captured image to PIL format for processing
- Save captured image to disk
- Provide image data for OCR and other processing

CLASS:
- ScreenCapture: Main class for capturing and saving screenshots

DEPENDENCIES:
- mss: Fast screenshot library
- Pillow (PIL): Image processing
- config: Configuration constants
- utils: Utility functions
"""

import mss
import mss.tools
from PIL import Image
import os
import config
import utils

# ============================================================================
# SCREEN CAPTURE CLASS
# ============================================================================

class ScreenCapture:
    """
    CLASS: ScreenCapture
    ===================
    
    PURPOSE:
    - Encapsulate all screenshot capture and saving logic
    - Provide clean interface for capturing screen regions
    - Handle image format conversion and storage
    
    ATTRIBUTES:
    - None (uses config constants)
    
    METHODS:
    - capture_region(x1, y1, x2, y2) -> PIL.Image: Capture region and return as PIL Image
    - save_screenshot(image, filepath) -> bool: Save image to disk
    - capture_and_save(x1, y1, x2, y2) -> bool: Capture and save in one call
    
    HOW IT WORKS:
    1. Uses MSS library to capture screen pixels
    2. Converts MSS format to PIL Image format
    3. Saves to disk if requested
    4. Returns image for further processing
    """
    
    def __init__(self):
        """
        METHOD: __init__()
        =================
        
        PURPOSE:
        - Initialize ScreenCapture instance
        - Set up MSS screenshot tool
        
        PARAMETERS:
        - self: Instance reference
        
        HOW IT WORKS:
        1. Create MSS instance for screenshot capturing
        2. Store as instance variable for reuse
        
        EXAMPLE:
        >>> from capture import ScreenCapture
        >>> capturer = ScreenCapture()
        """
        self.sct = mss.mss()
        utils.log_debug("ScreenCapture initialized")
    
    def capture_region(self, x1, y1, x2, y2):
        """
        METHOD: capture_region(x1, y1, x2, y2)
        ======================================
        
        PURPOSE:
        - Capture a rectangular region of the screen
        - Convert MSS format to PIL Image
        - Return image for processing
        
        PARAMETERS:
        - x1, y1: Top-left corner coordinates
        - x2, y2: Bottom-right corner coordinates
        
        RETURNS:
        - PIL.Image: Captured screenshot as PIL Image object
        - None: If capture fails
        
        EXAMPLE:
        >>> capturer = ScreenCapture()
        >>> img = capturer.capture_region(100, 100, 500, 500)
        >>> if img:
        ...     print(f"Captured {img.width}x{img.height} image")
        
        COORDINATE SYSTEM:
        - (0, 0) is top-left corner of screen
        - x increases to the right
        - y increases downward
        
        HOW IT WORKS:
        1. Normalize coordinates (handle negative widths/heights)
        2. Create monitor dict for MSS
        3. Capture pixels using MSS
        4. Convert MSS image to PIL Image
        5. Return PIL Image object
        
        TECHNICAL DETAILS:
        - MSS captures raw pixel data efficiently
        - PIL Image provides familiar image format
        - Coordinates must be integers
        """
        try:
            # Normalize coordinates (ensure x1 < x2, y1 < y2)
            left = min(x1, x2)
            top = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            # Handle edge case: user barely moved mouse (0-pixel selection)
            if width < 1 or height < 1:
                utils.log_debug(f"Selection too small: {width}x{height}")
                return None
            
            utils.log_debug(f"Capturing region: ({left}, {top}) {width}x{height}")
            
            # Create monitor dict for MSS (format: {'top': y, 'left': x, 'width': w, 'height': h})
            monitor = {
                'top': top,
                'left': left,
                'width': width,
                'height': height
            }
            
            # Capture using MSS
            screenshot = self.sct.grab(monitor)
            
            # Convert MSS image to PIL Image
            # MSS returns RGB format, PIL expects (width, height) tuple
            pil_image = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            
            utils.log_debug(f"✓ Successfully captured {pil_image.width}x{pil_image.height} image")
            return pil_image
            
        except Exception as e:
            utils.log_debug(f"❌ Error capturing region: {e}")
            print(f"❌ Capture failed: {e}")
            return None
    
    def save_screenshot(self, image, filepath):
        """
        METHOD: save_screenshot(image, filepath)
        ========================================
        
        PURPOSE:
        - Save PIL Image to disk in PNG format
        - Handle file I/O errors gracefully
        - Create directory if it doesn't exist
        
        PARAMETERS:
        - image (PIL.Image): Image object to save
        - filepath (str): Path where to save image
        
        RETURNS:
        - (bool) True if save successful, False otherwise
        
        EXAMPLE:
        >>> capturer = ScreenCapture()
        >>> img = capturer.capture_region(100, 100, 500, 500)
        >>> if capturer.save_screenshot(img, "screenshots/capture.png"):
        ...     print("Screenshot saved!")
        ... else:
        ...     print("Failed to save")
        
        HOW IT WORKS:
        1. Validate image object is not None
        2. Ensure directory exists (create if needed)
        3. Save image to filepath as PNG
        4. Log success/failure
        5. Return boolean result
        
        WHY PNG:
        - PNG is lossless (no quality degradation)
        - Good for text in OCR
        - Smaller files than BMP
        - Supports transparency (future use)
        """
        try:
            if image is None:
                print("❌ Cannot save: Image is None")
                return False
            
            # Ensure directory exists
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                utils.log_debug(f"Created directory: {directory}")
            
            # Save image as PNG
            image.save(filepath, 'PNG')
            
            file_size_kb = os.path.getsize(filepath) / 1024
            utils.log_debug(f"✓ Screenshot saved: {filepath} ({file_size_kb:.1f} KB)")
            print(f"✓ Screenshot saved to: {filepath}")
            
            return True
            
        except Exception as e:
            utils.log_debug(f"❌ Error saving screenshot: {e}")
            print(f"❌ Save failed: {e}")
            return False
    
    def capture_and_save(self, x1, y1, x2, y2, filepath=None):
        """
        METHOD: capture_and_save(x1, y1, x2, y2, filepath)
        ==================================================
        
        PURPOSE:
        - Capture region AND save to disk in one call
        - Convenience method combining capture_region and save_screenshot
        - Returns image object for further processing
        
        PARAMETERS:
        - x1, y1, x2, y2: Coordinates of region to capture
        - filepath (str, optional): Path to save. Default: config.SCREENSHOT_PATH
        
        RETURNS:
        - PIL.Image: Captured image if successful
        - None: If capture or save fails
        
        EXAMPLE:
        >>> capturer = ScreenCapture()
        >>> img = capturer.capture_and_save(100, 100, 500, 500)
        >>> if img:
        ...     print(f"Captured and saved {img.width}x{img.height} image")
        ... else:
        ...     print("Capture or save failed")
        
        HOW IT WORKS:
        1. Use default filepath if none provided
        2. Call capture_region() to get image
        3. If capture successful, save using save_screenshot()
        4. Return image object
        
        TYPICAL WORKFLOW:
        overlay.py (get coordinates)
          ↓
        capture.capture_and_save() (this method)
          ↓
        Image saved to disk
        Image returned for OCR
        """
        if filepath is None:
            filepath = config.SCREENSHOT_PATH
        
        # Capture the region
        image = self.capture_region(x1, y1, x2, y2)
        
        if image is None:
            return None
        
        # Save to disk
        if self.save_screenshot(image, filepath):
            return image
        else:
            return None


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    TEST CODE: Example usage of ScreenCapture
    
    This code runs if you execute: python capture.py
    
    HOW TO TEST:
    1. Open terminal/command prompt
    2. Navigate to project directory
    3. Run: python capture.py
    4. A screenshot of your screen will be captured and saved
    """
    
    print("Testing ScreenCapture...")
    
    # Initialize capture
    capturer = ScreenCapture()
    
    # Example: Capture top-left quarter of screen
    # Assuming screen is 1920x1080, top-left quarter is:
    # (0, 0) to (960, 540)
    
    img = capturer.capture_and_save(0, 0, 960, 540, "screenshots/test_capture.png")
    
    if img:
        print(f"✓ Test successful! Image size: {img.width}x{img.height}")
    else:
        print("❌ Test failed!")
