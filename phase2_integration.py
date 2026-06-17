"""
PHASE2_INTEGRATION.PY
====================
Integration layer connecting Phase 1 (capture) to Phase 2 (OCR)

PURPOSE:
- Bridge between screenshot capture and text extraction
- Manage OCR pipeline
- Handle image preprocessing
- Return extracted text to Phase 3

WORKFLOW:
Phase 1: Screenshot captured → capture.png
    ↓
Phase 2 Integration: Load image → OCR → Extract text
    ↓
Phase 3: Use extracted text for search

CLASS:
- Phase2Manager: Orchestrates OCR pipeline
"""

import os
import config
import utils
from ocr import OCRProcessor
from PIL import Image

# ============================================================================
# PHASE 2 MANAGER CLASS
# ============================================================================

class Phase2Manager:
    """
    CLASS: Phase2Manager
    ===================
    
    PURPOSE:
    - Manage OCR extraction pipeline
    - Connect Phase 1 (capture) to Phase 3 (search)
    - Handle image processing and text extraction
    
    ATTRIBUTES:
    - ocr_processor (OCRProcessor): OCR engine instance
    - language (str): OCR language setting
    - last_extracted_text (str): Cache of last extraction
    
    METHODS:
    - process_screenshot(image_path): Extract text from screenshot
    - extract_text(image_path): Wrapper for OCR extraction
    - get_last_result(): Get cached extraction result
    - validate_tesseract(): Check if Tesseract is available
    
    HOW IT WORKS:
    1. Phase 1 captures screenshot → screenshots/capture.png
    2. Phase2Manager receives image path
    3. Load and validate image
    4. Run OCR extraction
    5. Cache result
    6. Return text to Phase 3 (Search)
    
    INTEGRATION FLOW:
    hotkeys.py (Phase 1)
        ↓
    overlay.py (capture screenshot)
        ↓
    Phase2Manager (this module)
        ↓
    ocr.py (Tesseract extraction)
        ↓
    search.py (Phase 3 - Google Search)
    """
    
    def __init__(self, language='eng'):
        """
        METHOD: __init__(language)
        ==========================
        
        PURPOSE:
        - Initialize Phase 2 manager
        - Set up OCR processor
        
        PARAMETERS:
        - self: Instance reference
        - language (str, optional): OCR language code
          Default: 'eng' (English)
        
        EXAMPLE:
        >>> phase2 = Phase2Manager(language='eng')
        
        HOW IT WORKS:
        1. Create OCRProcessor instance
        2. Store language setting
        3. Initialize result cache
        4. Log initialization
        """
        try:
            self.ocr_processor = OCRProcessor(language=language)
            self.language = language
            self.last_extracted_text = ""
            
            utils.log_debug(f"Phase2Manager initialized (language: {language})")
            print(f"✓ Phase 2 ready (OCR: {language})")
            
        except Exception as e:
            utils.log_debug(f"❌ Phase 2 initialization failed: {e}")
            print(f"❌ Phase 2 failed: {e}")
            raise
    
    def process_screenshot(self, image_path=None):
        """
        METHOD: process_screenshot(image_path)
        ======================================
        
        PURPOSE:
        - Main entry point for Phase 2 processing
        - Extract text from screenshot
        - Cache result for Phase 3
        
        PARAMETERS:
        - self: Instance reference
        - image_path (str, optional): Path to screenshot
          Default: config.SCREENSHOT_PATH (screenshots/capture.png)
        
        RETURNS:
        - str: Extracted text
          Returns empty string if extraction fails
        
        EXAMPLE:
        >>> phase2 = Phase2Manager()
        >>> text = phase2.process_screenshot()
        >>> print(f"Extracted: {text}")
        
        HOW IT WORKS:
        1. Determine image path
        2. Validate file exists
        3. Log processing start
        4. Call OCR processor
        5. Cache result
        6. Return text
        
        ERROR HANDLING:
        - Returns empty string if file not found
        - Returns empty string if OCR fails
        - Continues to Phase 3 even if extraction fails
        """
        try:
            # Use provided path or default
            if image_path is None:
                image_path = config.SCREENSHOT_PATH
            
            # Validate file exists
            if not os.path.exists(image_path):
                utils.log_debug(f"Screenshot not found: {image_path}")
                print(f"❌ Screenshot not found: {image_path}")
                return ""
            
            utils.log_debug(f"Phase 2: Processing screenshot: {image_path}")
            print(f"\n📸 Phase 2: Extracting text from screenshot...")
            
            # Extract text using OCR
            extracted_text = self.extract_text(image_path)
            
            # Cache result
            self.last_extracted_text = extracted_text
            
            # Log result
            char_count = len(extracted_text)
            word_count = len(extracted_text.split())
            
            utils.log_debug(f"✓ Extracted {char_count} chars, {word_count} words")
            print(f"✓ Extracted {word_count} words ({char_count} characters)")
            
            return extracted_text
            
        except Exception as e:
            utils.log_debug(f"❌ Error in process_screenshot: {e}")
            print(f"❌ Screenshot processing failed: {e}")
            return ""
    
    def extract_text(self, image_path):
        """
        METHOD: extract_text(image_path)
        ================================
        
        PURPOSE:
        - Wrapper for OCR extraction
        - Call OCRProcessor to extract text
        
        PARAMETERS:
        - self: Instance reference
        - image_path (str): Path to image file
        
        RETURNS:
        - str: Extracted text
        
        EXAMPLE:
        >>> phase2 = Phase2Manager()
        >>> text = phase2.extract_text("screenshots/capture.png")
        
        HOW IT WORKS:
        1. Pass image to OCRProcessor
        2. Get extracted text
        3. Return to caller
        
        This is a wrapper to allow:
        - Future enhancement (additional processing)
        - Easy testing of OCR module
        - Cleaner separation of concerns
        """
        try:
            text = self.ocr_processor.extract_text(image_path)
            return text
            
        except Exception as e:
            utils.log_debug(f"❌ Error extracting text: {e}")
            return ""
    
    def get_last_result(self):
        """
        METHOD: get_last_result()
        =========================
        
        PURPOSE:
        - Get cached result from last extraction
        - Useful if Phase 3 needs to retry search
        
        PARAMETERS:
        - self: Instance reference
        
        RETURNS:
        - str: Cached extracted text
        
        EXAMPLE:
        >>> phase2 = Phase2Manager()
        >>> text = phase2.process_screenshot()
        >>> # Later...
        >>> cached_text = phase2.get_last_result()
        >>> print(cached_text)  # Same as text
        
        CACHING:
        Allows Phase 3 to:
        - Try different search terms
        - Refine search results
        - Avoid re-running OCR
        """
        return self.last_extracted_text
    
    def validate_tesseract(self):
        """
        METHOD: validate_tesseract()
        ============================
        
        PURPOSE:
        - Check if Tesseract is installed
        - Validate OCR engine availability
        
        PARAMETERS:
        - self: Instance reference
        
        RETURNS:
        - bool: True if Tesseract is available
        
        EXAMPLE:
        >>> phase2 = Phase2Manager()
        >>> if phase2.validate_tesseract():
        ...     print("Ready to extract text")
        
        HOW IT WORKS:
        1. Try to create OCR processor
        2. Return True if successful
        3. Return False if Tesseract missing
        
        USEFUL FOR:
        - Pre-flight checks
        - Graceful error handling
        - User feedback on missing dependencies
        """
        try:
            self.ocr_processor._check_tesseract()
            return True
        except:
            return False


# ============================================================================
# STANDALONE TESTING
# ============================================================================

def demo_phase2():
    """
    FUNCTION: demo_phase2()
    =======================
    
    PURPOSE:
    - Demonstrate Phase 2 functionality
    - Test OCR extraction with sample image
    
    PARAMETERS:
    - None
    
    RETURNS:
    - None
    
    HOW TO USE:
    >>> python phase2_integration.py
    
    This will:
    1. Create Phase2Manager
    2. Try to extract from screenshots/capture.png
    3. Print extracted text
    
    TYPICAL OUTPUT:
    ✓ Phase 2 ready (OCR: eng)
    📸 Phase 2: Extracting text from screenshot...
    ✓ Extracted 150 words (890 characters)
    
    EXTRACTED TEXT:
    [Full text from image]
    """
    
    print("\n" + "="*60)
    print("PHASE 2: OCR Text Extraction")
    print("="*60 + "\n")
    
    try:
        # Create Phase 2 manager
        phase2 = Phase2Manager(language='eng')
        
        # Check if screenshot exists
        screenshot_path = config.SCREENSHOT_PATH
        
        if os.path.exists(screenshot_path):
            print(f"Screenshot found: {screenshot_path}\n")
            
            # Process screenshot
            extracted_text = phase2.process_screenshot()
            
            if extracted_text:
                print("\n" + "="*60)
                print("EXTRACTED TEXT:")
                print("="*60)
                print(extracted_text)
                print("="*60)
                
                return extracted_text
            else:
                print("❌ No text extracted from image")
                return ""
        else:
            print(f"❌ Screenshot not found: {screenshot_path}")
            print("\nTo generate screenshot:")
            print("1. Run Phase 1: python main.py")
            print("2. Press Ctrl+Shift+S")
            print("3. Select area to capture")
            print("4. Screenshot saved to screenshots/capture.png")
            print("5. Run this script again")
            return ""
            
    except Exception as e:
        print(f"❌ Phase 2 demo failed: {e}")
        import traceback
        traceback.print_exc()
        return ""


if __name__ == "__main__":
    """
    SCRIPT ENTRY POINT
    ==================
    
    Run Phase 2 demo: python phase2_integration.py
    """
    extracted_text = demo_phase2()
