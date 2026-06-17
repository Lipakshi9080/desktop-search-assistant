"""
MAIN.PY
=======
Application entry point for Desktop Search Assistant

PURPOSE:
- Initialize application
- Set up hotkey listener
- Start GUI event loop
- Graceful error handling and shutdown

HOW TO RUN:
1. Open Command Prompt as Administrator (important!)
2. Navigate to project directory: cd path/to/desktop-search-assistant
3. Activate virtual environment: venv\Scripts\activate
4. Run: python main.py
5. Press Ctrl+Shift+S to activate overlay

EXECUTION FLOW:
main() called
    ↓
initialize_app() - create directories, validate paths
    ↓
HotkeyListener created - listens for Ctrl+Shift+S
    ↓
QApplication started - GUI event loop
    ↓
Waiting for hotkey press
    ↓
(User presses Ctrl+Shift+S)
    ↓
Overlay shown
    ↓
User selects area
    ↓
Screenshot captured and saved
    ↓
Back to waiting for hotkey
"""

import sys
import config
import utils
from hotkeys import HotkeyListener
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# ============================================================================
# APPLICATION SETUP
# ============================================================================

def create_application():
    """
    FUNCTION: create_application()
    ==============================
    
    PURPOSE:
    - Create and configure PyQt6 application
    - Set up basic application properties
    
    PARAMETERS:
    - None
    
    RETURNS:
    - QApplication: Configured Qt application instance
    
    HOW IT WORKS:
    1. Create QApplication instance (main Qt event loop)
    2. Set application name and version
    3. Configure app styling/properties
    4. Return app instance for event loop
    
    WHY QApplication:
    - Qt requires one QApplication per program
    - Manages event loop
    - Handles signals and slots
    - Required for GUI windows to work
    """
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)
    
    utils.log_debug(f"Created {config.APP_NAME} v{config.APP_VERSION}")
    
    return app


def setup_hotkey_listener(app):
    """
    FUNCTION: setup_hotkey_listener(app)
    ===================================
    
    PURPOSE:
    - Create and start global hotkey listener
    - Configure listener to show overlay when hotkey pressed
    
    PARAMETERS:
    - app (QApplication): Qt application instance
    
    RETURNS:
    - HotkeyListener: Active listener instance
    
    HOW IT WORKS:
    1. Create HotkeyListener with config hotkey
    2. Start listener (runs on background thread)
    3. Print instructions to user
    4. Return listener for future control
    
    BACKGROUND THREAD:
    - Listener runs on separate thread
    - Doesn't block GUI
    - Continues running in background
    - Can be stopped on app exit
    """
    try:
        listener = HotkeyListener(hotkey=config.HOTKEY)
        listener.start()
        
        print("\n" + "="*60)
        print(f"✓ {config.APP_NAME} Started")
        print("="*60)
        print(f"Hotkey: {config.HOTKEY}")
        print("Press Ctrl+Shift+S to activate overlay")
        print("Select area with mouse drag")
        print("Screenshot will be saved to: screenshots/capture.png")
        print("="*60 + "\n")
        
        return listener
        
    except Exception as e:
        print(f"❌ Failed to start hotkey listener: {e}")
        print("\n⚠️  IMPORTANT: On Windows, you MUST run as Administrator!")
        print("   Steps:")
        print("   1. Right-click Command Prompt")
        print("   2. Select 'Run as Administrator'")
        print("   3. Run: python main.py")
        sys.exit(1)


def main():
    """
    FUNCTION: main()
    ================
    
    PURPOSE:
    - Main application entry point
    - Orchestrate all initialization
    - Start event loop
    - Handle graceful shutdown
    
    PARAMETERS:
    - None
    
    RETURNS:
    - int: Exit code (0 for success, 1 for error)
    
    HOW IT WORKS:
    1. Initialize application files/directories
    2. Create Qt application
    3. Setup hotkey listener
    4. Start event loop (blocks until app exits)
    5. Cleanup on exit
    
    EXECUTION SEQUENCE:
    main()
        ↓
    utils.initialize_app() - setup directories
        ↓
    create_application() - create Qt app
        ↓
    setup_hotkey_listener() - start hotkey listener
        ↓
    app.exec() - event loop (blocks here)
        ↓
    (User presses Ctrl+C or closes app)
        ↓
    Cleanup
        ↓
    Exit
    
    ERROR HANDLING:
    - Catches all exceptions
    - Prints friendly error messages
    - Returns exit code
    - Cleans up resources
    
    ENTRY POINT:
    This function is called when script is executed:
    >>> python main.py
    """
    
    try:
        # Print startup info
        print(f"\n{'='*60}")
        print(f"Starting {config.APP_NAME}")
        print(f"{'='*60}\n")
        
        # Initialize application (create directories, etc.)
        if not utils.initialize_app():
            print("❌ Application initialization failed!")
            return 1
        
        # Create Qt application
        app = create_application()
        
        # Setup and start hotkey listener
        listener = setup_hotkey_listener(app)
        
        # Start event loop (blocks until app closes)
        print("Entering event loop... Press Ctrl+C to exit\n")
        exit_code = app.exec()
        
        # Cleanup on exit
        listener.stop()
        print(f"\n✓ {config.APP_NAME} closed")
        
        return exit_code
        
    except KeyboardInterrupt:
        # User pressed Ctrl+C
        print("\n\nShutdown requested (Ctrl+C)")
        listener.stop()
        print("✓ Application closed")
        return 0
        
    except Exception as e:
        # Unexpected error
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    SCRIPT ENTRY POINT
    ==================
    
    This code runs when you execute: python main.py
    
    It calls main() and exits with appropriate code
    """
    
    exit_code = main()
    sys.exit(exit_code)
