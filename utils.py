"""
UTILS.PY
========
Utility functions for Desktop Search Assistant

PURPOSE:
- Provide reusable helper functions used across the application
- Handle common tasks like directory creation, file paths, timestamps
- Keep code DRY (Don't Repeat Yourself)

FUNCTIONS:
- create_directories(): Ensure required folders exist
- get_timestamp(): Generate timestamped filenames
- resource_path(): Handle file/asset paths correctly
- log_debug(): Print debug messages when DEBUG_MODE is enabled
"""

import os
from datetime import datetime
import config

# ============================================================================
# DIRECTORY & FILE MANAGEMENT
# ============================================================================

def create_directories():
    """
    FUNCTION: create_directories()
    ============================
    
    PURPOSE:
    - Ensure all required directories exist before application runs
    - Prevents FileNotFoundError when saving screenshots
    - Creates directories if they don't exist
    
    PARAMETERS:
    - None
    
    RETURNS:
    - None
    
    EXAMPLE:
    >>> create_directories()
    # Creates 'screenshots/' folder if it doesn't exist
    
    HOW IT WORKS:
    1. Checks if SCREENSHOT_DIR exists
    2. If not, creates it using os.makedirs()
    3. Logs success message to console
    """
    try:
        if not os.path.exists(config.SCREENSHOT_DIR):
            os.makedirs(config.SCREENSHOT_DIR)
            log_debug(f"✓ Created directory: {config.SCREENSHOT_DIR}")
        else:
            log_debug(f"✓ Directory exists: {config.SCREENSHOT_DIR}")
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
        raise


def resource_path(relative_path):
    """
    FUNCTION: resource_path(relative_path)
    ======================================
    
    PURPOSE:
    - Convert relative file paths to absolute paths
    - Handle file paths correctly whether app is run normally or as .exe
    - Used for accessing assets, config files, etc.
    
    PARAMETERS:
    - relative_path (str): Relative path to file (e.g., "assets/icon.png")
    
    RETURNS:
    - (str) Absolute path to the resource
    
    EXAMPLE:
    >>> icon_path = resource_path("assets/icon.png")
    >>> print(icon_path)
    # Output: C:\\Users\\YourName\\Desktop\\app\\assets\\icon.png
    
    HOW IT WORKS:
    1. Get the base directory where the script is running
    2. Join it with the relative path provided
    3. Return the full absolute path
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# ============================================================================
# TIMESTAMP & NAMING
# ============================================================================

def get_timestamp():
    """
    FUNCTION: get_timestamp()
    =========================
    
    PURPOSE:
    - Generate timestamp for creating unique filenames
    - Useful for saving multiple screenshots without overwriting
    - Format: YYYY-MM-DD_HH-MM-SS
    
    PARAMETERS:
    - None
    
    RETURNS:
    - (str) Timestamp string (e.g., "2024-01-15_14-30-45")
    
    EXAMPLE:
    >>> timestamp = get_timestamp()
    >>> print(timestamp)
    # Output: 2024-01-15_14-30-45
    
    >>> filename = f"capture_{timestamp}.png"
    >>> print(filename)
    # Output: capture_2024-01-15_14-30-45.png
    
    HOW IT WORKS:
    1. Get current date and time
    2. Format it as YYYY-MM-DD_HH-MM-SS
    3. Return as string
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# ============================================================================
# LOGGING & DEBUGGING
# ============================================================================

def log_debug(message):
    """
    FUNCTION: log_debug(message)
    ============================
    
    PURPOSE:
    - Print debug messages only when DEBUG_MODE is True
    - Helps with development and troubleshooting
    - Easy way to enable/disable all debug output at once
    
    PARAMETERS:
    - message (str): Message to print
    
    RETURNS:
    - None
    
    EXAMPLE:
    >>> log_debug("Application started")
    # Prints only if config.DEBUG_MODE = True
    
    HOW IT WORKS:
    1. Check if DEBUG_MODE is enabled in config
    2. If True, print the message with timestamp
    3. If False, do nothing
    
    TO USE:
    - Set config.DEBUG_MODE = True for development
    - Set config.DEBUG_MODE = False for production
    """
    if config.DEBUG_MODE:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] DEBUG: {message}")


# ============================================================================
# VALIDATION & CHECKS
# ============================================================================

def validate_screenshot_path():
    """
    FUNCTION: validate_screenshot_path()
    ====================================
    
    PURPOSE:
    - Check if screenshot directory is accessible
    - Verify write permissions before trying to save
    - Prevents errors when saving screenshots
    
    PARAMETERS:
    - None
    
    RETURNS:
    - (bool) True if path is valid and writable, False otherwise
    
    EXAMPLE:
    >>> if validate_screenshot_path():
    ...     print("Safe to save screenshots")
    ... else:
    ...     print("Cannot save to this location")
    
    HOW IT WORKS:
    1. Check if directory exists
    2. Check if directory is writable
    3. Return True/False based on checks
    """
    try:
        if not os.path.exists(config.SCREENSHOT_DIR):
            os.makedirs(config.SCREENSHOT_DIR)
        
        # Test write permission
        test_file = os.path.join(config.SCREENSHOT_DIR, ".write_test")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        
        return True
    except Exception as e:
        log_debug(f"Screenshot path validation failed: {e}")
        return False


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_app():
    """
    FUNCTION: initialize_app()
    ==========================
    
    PURPOSE:
    - Run all initialization checks when app starts
    - Ensure all prerequisites are met
    - Centralized startup logic
    
    PARAMETERS:
    - None
    
    RETURNS:
    - (bool) True if all checks pass, False otherwise
    
    EXAMPLE:
    >>> if initialize_app():
    ...     print("App ready to run")
    ... else:
    ...     print("App initialization failed")
    
    HOW IT WORKS:
    1. Create required directories
    2. Validate screenshot path
    3. Log initialization complete
    4. Return success status
    """
    try:
        log_debug("Initializing application...")
        create_directories()
        
        if not validate_screenshot_path():
            print("❌ Cannot write to screenshot directory. Check permissions.")
            return False
        
        log_debug(f"✓ {config.APP_NAME} v{config.APP_VERSION} initialized")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False
