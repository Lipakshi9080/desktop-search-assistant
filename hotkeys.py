"""
HOTKEYS.PY
==========
Global hotkey listener for Desktop Search Assistant

PURPOSE:
- Listen for global hotkey press (Ctrl+Shift+S)
- Works anywhere on Windows (even in other applications)
- Trigger overlay when hotkey is pressed
- Run hotkey listener in background thread

CLASS:
- HotkeyListener: Manages global hotkey detection

DEPENDENCIES:
- keyboard: Global hotkey library
- threading: Run listener in background
- config: Hotkey configuration
- utils: Utility functions
"""

import keyboard
import threading
import config
import utils
from overlay import OverlayWindow
from PyQt6.QtWidgets import QApplication

# ============================================================================
# HOTKEY LISTENER CLASS
# ============================================================================

class HotkeyListener:
    """
    CLASS: HotkeyListener
    ====================
    
    PURPOSE:
    - Listen for global hotkey presses
    - Trigger overlay when hotkey detected
    - Run in background thread so it doesn't block application
    
    ATTRIBUTES:
    - hotkey (str): The hotkey combination to listen for
    - callback (function): Function to call when hotkey pressed
    - is_running (bool): Whether listener is active
    - listener_thread (Thread): Background thread running listener
    
    METHODS:
    - start(): Begin listening for hotkey
    - stop(): Stop listening
    - on_hotkey_pressed(): Called when hotkey is detected
    - _run_listener(): Background thread loop
    
    HOW IT WORKS:
    1. Create HotkeyListener with hotkey and callback
    2. Call start() to begin listening
    3. Listener runs in background thread
    4. When user presses hotkey, callback is triggered
    5. Callback shows overlay
    6. User selects area and screenshot is captured
    7. Listener continues running for next hotkey press
    
    BACKGROUND THREAD:
    - Listener runs on separate thread so it doesn't freeze app
    - Main thread handles GUI
    - Communication via simple flag (is_running)
    
    WHY BACKGROUND THREAD:
    - Hotkey listening is blocking operation
    - If run on main thread, would freeze GUI
    - Background thread allows app to remain responsive
    """
    
    def __init__(self, hotkey=None, callback=None):
        """
        METHOD: __init__(hotkey, callback)
        ==================================
        
        PURPOSE:
        - Initialize hotkey listener
        - Set up hotkey configuration and callback
        
        PARAMETERS:
        - self: Instance reference
        - hotkey (str, optional): Hotkey combination (e.g., "ctrl+shift+s")
          Default: config.HOTKEY
        - callback (function, optional): Function to call when hotkey pressed
          Default: self.on_hotkey_pressed
        
        EXAMPLE:
        >>> from hotkeys import HotkeyListener
        >>> def show_overlay():
        ...     print("Overlay triggered!")
        >>> listener = HotkeyListener(hotkey="ctrl+shift+s", callback=show_overlay)
        >>> listener.start()
        
        HOW IT WORKS:
        1. Store hotkey configuration
        2. Store callback function
        3. Initialize state variables
        4. Prepare for background thread
        
        ATTRIBUTES SET:
        - self.hotkey: Which hotkey to listen for
        - self.callback: Function to call on hotkey press
        - self.is_running: Track listener state
        - self.listener_thread: Thread object (created later)
        """
        self.hotkey = hotkey or config.HOTKEY
        self.callback = callback or self.on_hotkey_pressed
        self.is_running = False
        self.listener_thread = None
        
        utils.log_debug(f"HotkeyListener initialized with hotkey: {self.hotkey}")
    
    def start(self):
        """
        METHOD: start()
        ===============
        
        PURPOSE:
        - Start listening for global hotkey
        - Create and start background thread
        - Allow listener to run without blocking GUI
        
        PARAMETERS:
        - self: Instance reference
        
        RETURNS:
        - None
        
        EXAMPLE:
        >>> listener = HotkeyListener()
        >>> listener.start()
        >>> print("Listening for hotkey... (press Ctrl+Shift+S)")
        
        HOW IT WORKS:
        1. Check if listener is already running
        2. Set is_running flag to True
        3. Create new thread for listener
        4. Set thread as daemon (auto-closes when app exits)
        5. Start the thread
        6. Log success message
        
        IMPORTANT NOTES:
        - Must run as Administrator on Windows for global hotkey
        - Daemon thread means it won't prevent app from closing
        - Only one listener can run at a time
        
        THREAD DAEMON:
        - daemon=True means thread exits when main app exits
        - Prevents "ghost" listener process after app closes
        """
        try:
            if self.is_running:
                utils.log_debug("⚠️  Hotkey listener already running")
                return
            
            self.is_running = True
            self.listener_thread = threading.Thread(target=self._run_listener, daemon=True)
            self.listener_thread.start()
            
            utils.log_debug(f"✓ Hotkey listener started (listening for: {self.hotkey})")
            print(f"✓ Listening for hotkey: {self.hotkey}")
            
        except Exception as e:
            utils.log_debug(f"❌ Error starting hotkey listener: {e}")
            print(f"❌ Failed to start listener: {e}")
            print("\n⚠️  ADMIN REQUIRED: On Windows, you may need to run as Administrator!")
            print("   Right-click Command Prompt → Run as Administrator")
            self.is_running = False
    
    def stop(self):
        """
        METHOD: stop()
        ==============
        
        PURPOSE:
        - Stop listening for hotkey
        - Cleanup resources
        - Allow graceful shutdown
        
        PARAMETERS:
        - self: Instance reference
        
        RETURNS:
        - None
        
        EXAMPLE:
        >>> listener = HotkeyListener()
        >>> listener.start()
        >>> # ... later ...
        >>> listener.stop()
        
        HOW IT WORKS:
        1. Set is_running flag to False
        2. This signals background thread to exit
        3. Unregister hotkey listener
        4. Wait for thread to finish
        5. Log success message
        
        CLEANUP:
        - Stops keyboard listener
        - Releases hotkey
        - Allows system to use the hotkey again
        """
        try:
            if not self.is_running:
                utils.log_debug("⚠️  Hotkey listener not running")
                return
            
            self.is_running = False
            keyboard.remove_hotkey(self.hotkey)
            
            if self.listener_thread:
                self.listener_thread.join(timeout=2)
            
            utils.log_debug("✓ Hotkey listener stopped")
            print(f"✓ Listener stopped")
            
        except Exception as e:
            utils.log_debug(f"❌ Error stopping listener: {e}")
    
    def on_hotkey_pressed(self):
        """
        METHOD: on_hotkey_pressed()
        ==========================
        
        PURPOSE:
        - Default callback when hotkey is detected
        - Create and show overlay
        - This is what runs when user presses Ctrl+Shift+S
        
        PARAMETERS:
        - self: Instance reference
        
        RETURNS:
        - None
        
        EXAMPLE:
        (Called automatically when user presses Ctrl+Shift+S)
        
        HOW IT WORKS:
        1. Log that hotkey was pressed
        2. Create OverlayWindow instance
        3. Show overlay fullscreen
        4. User can now select area
        5. After selection, overlay closes
        6. Listener continues running
        
        ERROR HANDLING:
        - If overlay creation fails, log error but continue
        - Listener remains active for next hotkey press
        
        WORKFLOW:
        User presses Ctrl+Shift+S
            ↓
        on_hotkey_pressed() called
            ↓
        OverlayWindow created
            ↓
        Overlay shown
            ↓
        User selects area
            ↓
        Screenshot captured
            ↓
        Back to listening for next hotkey
        """
        try:
            utils.log_debug("🔥 Hotkey pressed!")
            print("\n🔥 Hotkey detected! Opening overlay...")
            
            # Create overlay window
            overlay = OverlayWindow()
            overlay.show_overlay()
            
            # Connect signal for when selection is complete
            overlay.selection_made.connect(self.on_selection_complete)
            
        except Exception as e:
            utils.log_debug(f"❌ Error in hotkey callback: {e}")
            print(f"❌ Overlay error: {e}")
    
    def on_selection_complete(self, screenshot_path):
        """
        METHOD: on_selection_complete(screenshot_path)
        ==============================================
        
        PURPOSE:
        - Called when user completes selection
        - Prepare for next phases (OCR, search)
        - Can be extended in future phases
        
        PARAMETERS:
        - self: Instance reference
        - screenshot_path (str): Path to saved screenshot
        
        RETURNS:
        - None
        
        EXAMPLE:
        (Called automatically after user selects area)
        
        HOW IT WORKS - CURRENT (Phase 1):
        1. Log completion
        2. Print screenshot path
        3. Ready for next hotkey press
        
        HOW IT WORKS - FUTURE:
        Phase 2:
        - Send image to OCR module
        - Extract text
        
        Phase 3:
        - Send extracted text to Google Search
        - Open browser with search results
        
        SIGNAL CONNECTION:
        - This is called via PyQt6 signal
        - Allows communication between overlay and listener
        - Non-blocking, doesn't freeze application
        """
        try:
            utils.log_debug(f"Selection complete! Screenshot: {screenshot_path}")
            print(f"✓ Screenshot saved to: {screenshot_path}")
            
            # Phase 2 integration point (OCR)
            # TODO: Uncomment when Phase 2 is implemented
            # from ocr import OCRProcessor
            # ocr = OCRProcessor()
            # text = ocr.extract_text(screenshot_path)
            # print(f"Extracted text: {text}")
            
            # Phase 3 integration point (Search)
            # TODO: Uncomment when Phase 3 is implemented
            # from search import GoogleSearch
            # search = GoogleSearch()
            # search.search_text(text)
            
        except Exception as e:
            utils.log_debug(f"❌ Error in selection complete: {e}")
    
    def _run_listener(self):
        """
        METHOD: _run_listener()
        ======================
        
        PURPOSE:
        - Background thread function
        - Listen for hotkey indefinitely
        - This runs on background thread, not main thread
        
        PARAMETERS:
        - self: Instance reference
        
        RETURNS:
        - None (runs in infinite loop)
        
        EXAMPLE:
        (Called automatically by start() in background thread)
        
        HOW IT WORKS:
        1. Add hotkey listener using keyboard library
        2. While is_running is True, keyboard listens
        3. When hotkey pressed, callback is called
        4. When is_running becomes False, listener exits
        5. Thread terminates
        
        BACKGROUND THREAD:
        - This runs on separate thread
        - Doesn't block main GUI thread
        - Can be stopped via stop() method
        - Runs in infinite loop until stopped
        
        KEYBOARD LIBRARY:
        - keyboard.add_hotkey() registers listener
        - Listener is blocking (waits for hotkey)
        - Only returns when hotkey is pressed
        - Then callback is executed
        - Then goes back to waiting
        
        THREAD SAFETY:
        - Only accesses self.is_running flag
        - Flag is simple boolean, thread-safe
        - No complex synchronization needed
        """
        try:
            # Register hotkey listener
            keyboard.add_hotkey(self.hotkey, self.callback)
            
            # Keep thread alive - listener runs until stop() is called
            while self.is_running:
                threading.Event().wait(0.1)  # Sleep briefly to avoid busy-wait
            
            utils.log_debug("Listener thread exiting")
            
        except Exception as e:
            utils.log_debug(f"❌ Error in listener thread: {e}")
            self.is_running = False


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    TEST CODE: Direct hotkey listener testing
    
    HOW TO TEST:
    1. Open Command Prompt as Administrator
    2. Navigate to project directory
    3. Run: python hotkeys.py
    4. You'll see "Listening for hotkey..."
    5. Press Ctrl+Shift+S anywhere on screen
    6. Overlay should appear
    7. Select area and take screenshot
    8. Press Ctrl+C to stop listening
    
    IMPORTANT:
    - MUST run as Administrator on Windows
    - Global hotkeys won't work without admin privileges
    """
    
    from PyQt6.QtWidgets import QApplication
    import sys
    
    print("Starting hotkey listener test...")
    print("Instructions:")
    print("1. This will listen for Ctrl+Shift+S globally")
    print("2. Press Ctrl+Shift+S anywhere on your screen")
    print("3. Overlay will appear")
    print("4. Select area to capture")
    print("5. Press Ctrl+C to exit")
    print()
    
    # Create Qt application (needed for overlay)
    app = QApplication(sys.argv)
    
    # Create and start listener
    listener = HotkeyListener()
    listener.start()
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        listener.stop()
        print("✓ Goodbye!")
