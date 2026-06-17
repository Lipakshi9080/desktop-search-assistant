"""
OCR.PY
======
Optical Character Recognition (OCR) module for text extraction

PURPOSE:
- Extract text from screenshots using Tesseract OCR
- Process images and return recognized text
- Handle OCR errors gracefully
- Support preprocessing for better accuracy

CLASS:
- OCRProcessor: Main OCR processing class

DEPENDENCIES:
- pytesseract: Python wrapper for Tesseract OCR
- Tesseract-OCR: Must be installed separately on system
- PIL: Image processing
- config: Configuration
- utils: Utility functions

INSTALLATION:
Windows:
  1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
  2. Run installer (default path: C:\Program Files\Tesseract-OCR)
  3. pytesseract will find it automatically

Linux:
  sudo apt-get install tesseract-ocr

macOS:
  brew install tesseract
"""

import pytesseract
from PIL import Image
import config
import utils
import os

# ============================================================================
# OCR PROCESSOR CLASS
# ============================================================================

class OCRProcessor:
    """
    CLASS: OCRProcessor
    ==================
    
    PURPOSE:
    - Extract text from images using Tesseract OCR
    - Process screenshots captured by Phase 1
    - Return recognized text for Phase 3 (Search)
    
    ATTRIBUTES:
    - tesseract_path (str): Path to Tesseract executable
    - language (str): Language for OCR (default: 'eng')
    - preprocessor: Image preprocessing pipeline
    
    METHODS:
    - extract_text(image_path): Extract text from image file
    - extract_text_from_image(image): Extract text from PIL Image
    - preprocess_image(image): Enhance image for better OCR
    - _validate_image(image): Check if image is valid
    - _check_tesseract(): Verify Tesseract is installed
    
    HOW IT WORKS:
    1. Screenshot captured in Phase 1 (capture.png)
    2. OCRProcessor receives image path
    3. Image is loaded and preprocessed
    4. Tesseract performs OCR
    5. Extracted text returned to caller
    6. Phase 3 uses text for Google Search
    
    WORKFLOW:
    extract_text(image_path)
        ↓
    Load image from file
        ↓
    Preprocess image (enhance contrast, denoise, etc.)
        ↓
    Tesseract OCR
        ↓
    Post-process text (clean up, remove extra spaces)
        ↓
    Return extracted text
    
    ACCURACY:
    - Better quality images = better OCR accuracy
    - Preprocessing improves accuracy by ~20-30%
    - Large text (14pt+) = high accuracy
    - Small text (8pt-) = lower accuracy
    """
    
    def __init__(self, tesseract_path=None, language='eng'):
        """
        METHOD: __init__(tesseract_path, language)
        =========================================
        
        PURPOSE:
        - Initialize OCR processor
        - Set up Tesseract path and language
        - Validate Tesseract installation
        
        PARAMETERS:
        - self: Instance reference
        - tesseract_path (str, optional): Path to Tesseract executable
          Default: Auto-detect (Windows: C:\Program Files\Tesseract-OCR\tesseract.exe)
        - language (str, optional): OCR language code
          Default: 'eng' (English)
          Examples: 'fra' (French), 'deu' (German), 'chi_sim' (Simplified Chinese)
        
        EXAMPLE:
        >>> ocr = OCRProcessor()
        >>> ocr = OCRProcessor(language='fra')  # French OCR
        
        HOW IT WORKS:
        1. Store language setting
        2. Set Tesseract path (auto-detect if not provided)
        3. Validate Tesseract installation
        4. Initialize preprocessing
        5. Log initialization
        
        PATH AUTO-DETECTION:
        - Windows: Checks default Tesseract installation paths
        - Linux/Mac: Uses system PATH
        - User can override with tesseract_path parameter
        """
        try:
            self.language = language
            self.tesseract_path = tesseract_path or self._find_tesseract()
            
            # Set Tesseract path for pytesseract
            if self.tesseract_path:
                pytesseract.pytesseract.pytesseract_cmd = self.tesseract_path
            
            # Verify Tesseract is available
            self._check_tesseract()
            
            utils.log_debug(f"OCRProcessor initialized (language: {self.language})")
            print(f"✓ OCR ready (language: {self.language})")
            
        except Exception as e:
            utils.log_debug(f"❌ Error initializing OCRProcessor: {e}")
            print(f"❌ OCR initialization failed: {e}")
            raise
    
    def _find_tesseract(self):
        """
        METHOD: _find_tesseract()
        =========================
        
        PURPOSE:
        - Auto-detect Tesseract installation on system
        - Try common installation paths
        
        PARAMETERS:
        - self: Instance reference
        
        RETURNS:
        - str: Path to tesseract.exe, or None if not found
        
        COMMON PATHS:
        Windows:
        - C:\Program Files\Tesseract-OCR\tesseract.exe
        - C:\Program Files (x86)\Tesseract-OCR\tesseract.exe
        
        Linux/Mac:
        - /usr/bin/tesseract
        - /usr/local/bin/tesseract
        
        HOW IT WORKS:
        1. Try common installation paths
        2. Check if file exists at each path
        3. Return first valid path found
        4. Return None if not found anywhere
        """
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                utils.log_debug(f"Found Tesseract at: {path}")
                return path
        
        return None
    
    def _check_tesseract(self):
        """
        METHOD: _check_tesseract()
        ==========================
        
        PURPOSE:
        - Verify Tesseract is installed and working
        - Provide helpful error messages if missing
        
        PARAMETERS:
        - self: Instance reference
        
        RETURNS:
        - None
        
        RAISES:
        - Exception: If Tesseract is not found
        
        ERROR MESSAGES:
        Helpful messages for different installation scenarios
        
        HOW IT WORKS:
        1. Try to get Tesseract version
        2. If succeeds, Tesseract is working
        3. If fails, raise exception with installation instructions
        """
        try:
            version = pytesseract.get_tesseract_version()
            utils.log_debug(f"Tesseract version: {version}")
            
        except Exception as e:
            error_msg = f"""
            ❌ Tesseract OCR not found!
            
            Installation Instructions:
            
            Windows:
              1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
              2. Run installer (keep default path)
              3. Restart this application
            
            Linux (Ubuntu/Debian):
              sudo apt-get install tesseract-ocr
            
            Linux (Fedora):
              sudo dnf install tesseract
            
            macOS:
              brew install tesseract
            
            Error: {e}
            """
            raise Exception(error_msg)
    
    def extract_text(self, image_path):
        """
        METHOD: extract_text(image_path)
        ================================
        
        PURPOSE:
        - Extract text from image file on disk
        - Main entry point for OCR processing
        
        PARAMETERS:
        - self: Instance reference
        - image_path (str): Path to image file
          Example: "screenshots/capture.png"
        
        RETURNS:
        - str: Extracted text from image
          Returns empty string if extraction fails
        
        EXAMPLE:
        >>> ocr = OCRProcessor()
        >>> text = ocr.extract_text("screenshots/capture.png")
        >>> print(text)
        "The extracted text from the image"
        
        HOW IT WORKS:
        1. Verify file exists
        2. Load image from disk
        3. Preprocess image
        4. Extract text using Tesseract
        5. Clean up text
        6. Return result
        
        ERROR HANDLING:
        - Returns empty string if file not found
        - Returns empty string if OCR fails
        - Logs errors for debugging
        """
        try:
            # Verify file exists
            if not os.path.exists(image_path):
                utils.log_debug(f"Image file not found: {image_path}")
                print(f"❌ Image not found: {image_path}")
                return ""
            
            utils.log_debug(f"Loading image: {image_path}")
            
            # Load image
            image = Image.open(image_path)
            
            # Extract text
            text = self.extract_text_from_image(image)
            
            utils.log_debug(f"Extracted {len(text)} characters from image")
            
            return text
            
        except Exception as e:
            utils.log_debug(f"❌ Error extracting text: {e}")
            print(f"❌ OCR extraction failed: {e}")
            return ""
    
    def extract_text_from_image(self, image):
        """
        METHOD: extract_text_from_image(image)
        =====================================
        
        PURPOSE:
        - Extract text from PIL Image object
        - Core OCR processing function
        
        PARAMETERS:
        - self: Instance reference
        - image (PIL.Image): Image to process
        
        RETURNS:
        - str: Extracted text
        
        EXAMPLE:
        >>> from PIL import Image
        >>> ocr = OCRProcessor()
        >>> img = Image.open("screenshot.png")
        >>> text = ocr.extract_text_from_image(img)
        
        HOW IT WORKS:
        1. Validate image is valid
        2. Preprocess image (enhance for OCR)
        3. Run Tesseract OCR
        4. Post-process text (cleanup)
        5. Return clean text
        
        PREPROCESSING:
        - Convert to grayscale (B&W)
        - Increase contrast
        - Remove noise
        - Improves OCR accuracy significantly
        
        POST-PROCESSING:
        - Remove extra whitespace
        - Clean control characters
        - Normalize line breaks
        """
        try:
            # Validate image
            if not self._validate_image(image):
                return ""
            
            utils.log_debug("Preprocessing image for OCR")
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Extract text using Tesseract
            utils.log_debug("Running Tesseract OCR")
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.language,
                config='--psm 6'  # PSM 6: Assume single uniform block of text
            )
            
            # Post-process text
            text = self._postprocess_text(text)
            
            return text
            
        except Exception as e:
            utils.log_debug(f"❌ Error in extract_text_from_image: {e}")
            return ""
    
    def preprocess_image(self, image):
        """
        METHOD: preprocess_image(image)
        ===============================
        
        PURPOSE:
        - Enhance image for better OCR accuracy
        - Apply filters and transformations
        
        PARAMETERS:
        - self: Instance reference
        - image (PIL.Image): Image to preprocess
        
        RETURNS:
        - PIL.Image: Processed image
        
        PREPROCESSING STEPS:
        1. Convert to RGB (handle different formats)
        2. Convert to grayscale (B&W)
        3. Increase contrast (make text darker)
        4. Resize if needed (OCR works better with larger text)
        5. Apply sharpening filter
        
        EXAMPLE:
        >>> ocr = OCRProcessor()
        >>> img = Image.open("screenshot.png")
        >>> processed = ocr.preprocess_image(img)
        
        HOW IT WORKS:
        Preprocessing dramatically improves OCR:
        
        Without preprocessing:
          Accuracy: ~70%
        
        With preprocessing:
          Accuracy: ~90%+
        
        IMAGE FILTERS:
        - Grayscale: Removes color noise
        - Contrast: Makes text darker/clearer
        - Sharpening: Makes edges crisper
        """
        try:
            from PIL import ImageEnhance, ImageFilter
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2)  # 2x contrast boost
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2)
            
            # Apply threshold (make it pure black and white)
            image = image.point(lambda x: 0 if x < 150 else 255, '1')
            
            return image
            
        except Exception as e:
            utils.log_debug(f"❌ Error preprocessing image: {e}")
            return image
    
    def _validate_image(self, image):
        """
        METHOD: _validate_image(image)
        ==============================
        
        PURPOSE:
        - Check if image is valid for OCR
        - Verify image dimensions and format
        
        PARAMETERS:
        - self: Instance reference
        - image (PIL.Image): Image to validate
        
        RETURNS:
        - bool: True if valid, False otherwise
        
        VALIDATION CHECKS:
        - Image is not None
        - Image has width and height
        - Image is large enough (at least 50x50 pixels)
        
        HOW IT WORKS:
        1. Check image exists (not None)
        2. Check image has dimensions
        3. Check minimum size (very small images = poor OCR)
        4. Return True if all checks pass
        """
        try:
            if image is None:
                utils.log_debug("Image is None")
                return False
            
            width, height = image.size
            
            if width < 50 or height < 50:
                utils.log_debug(f"Image too small: {width}x{height}")
                return False
            
            return True
            
        except Exception as e:
            utils.log_debug(f"❌ Error validating image: {e}")
            return False
    
    def _postprocess_text(self, text):
        """
        METHOD: _postprocess_text(text)
        ===============================
        
        PURPOSE:
        - Clean up extracted text
        - Remove noise and formatting artifacts
        
        PARAMETERS:
        - self: Instance reference
        - text (str): Raw OCR output
        
        RETURNS:
        - str: Cleaned text
        
        CLEANING STEPS:
        1. Remove extra whitespace
        2. Remove control characters
        3. Normalize line breaks
        4. Strip leading/trailing spaces
        
        EXAMPLE:
        >>> raw = "Hello  \\n\\n  World  \\x00"
        >>> clean = ocr._postprocess_text(raw)
        >>> print(clean)
        "Hello\nWorld"
        
        HOW IT WORKS:
        OCR output often has:
        - Extra spaces and tabs
        - Line breaks in wrong places
        - Special characters
        
        Post-processing cleans this up
        for better search results
        """
        try:
            # Remove control characters
            text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
            
            # Remove extra whitespace
            lines = [line.strip() for line in text.split('\n')]
            text = '\n'.join(line for line in lines if line)
            
            # Replace multiple newlines with single
            while '\n\n\n' in text:
                text = text.replace('\n\n\n', '\n\n')
            
            return text.strip()
            
        except Exception as e:
            utils.log_debug(f"❌ Error postprocessing text: {e}")
            return text


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    TEST CODE: Direct OCR testing
    
    HOW TO TEST:
    1. Take a screenshot with Phase 1
    2. Run: python ocr.py
    3. It will extract text from screenshots/capture.png
    4. Print extracted text to console
    
    USEFUL FOR:
    - Testing OCR without Phase 1 overlay
    - Debugging text extraction
    - Experimenting with preprocessing
    """
    
    import config
    
    print("Starting OCR test...")
    print("="*60)
    
    try:
        # Create OCR processor
        ocr = OCRProcessor(language='eng')
        
        # Try to extract from Phase 1 screenshot
        screenshot_path = config.SCREENSHOT_PATH
        
        if os.path.exists(screenshot_path):
            print(f"\nExtracting text from: {screenshot_path}\n")
            text = ocr.extract_text(screenshot_path)
            
            print("="*60)
            print("EXTRACTED TEXT:")
            print("="*60)
            print(text)
            print("="*60)
            print(f"\nTotal characters: {len(text)}")
        else:
            print(f"Screenshot not found: {screenshot_path}")
            print("\nTo test OCR:")
            print("1. Run Phase 1: python main.py")
            print("2. Press Ctrl+Shift+S")
            print("3. Select area on screen")
            print("4. Run this script again: python ocr.py")
            
    except Exception as e:
        print(f"\n❌ OCR test failed: {e}")
        import traceback
        traceback.print_exc()
