import easyocr
import numpy as np
import cv2
import re

reader = easyocr.Reader(["en"], gpu=False)

def is_ui_element(text):
    """
    Check if the OCR text appears to be a UI element rather than a floor plan label.
    
    Filters out:
    - Hierarchical list patterns like "#1 of 3", "#2 of 3", "8 #1 of 3"
    - UI-related text like "items", "models", percentages
    - Simple numeric-only text that might be list item numbers
    - UI dropdown/selector patterns
    - Dimension-like patterns that are actually UI labels
    """
    if not text or len(text.strip()) == 0:
        return True
    
    text_lower = text.lower().strip()
    text_original = text.strip()
    
    # Filter patterns that indicate UI elements (hierarchical list items)
    # Patterns like "#1 of 3", "8 #1 of 3", "10"" #1 of 2", "13' #1 of 2"
    hierarchical_patterns = [
        r'#\d+\s+of\s+\d+',  # "#1 of 3" anywhere in text
        r'\d+\s+#\d+\s+of\s+\d+',  # "8 #1 of 3" (number then #X of Y)
        r'\d+["\']?\s*#\d+\s+of\s+\d+',  # "8" #1 of 3", "10"" #1 of 2", "13' #1 of 2"
        r'^\d+["\']+\s*#\d+\s+of\s+\d+',  # "10"" #1 of 2" (more quotes)
    ]
    
    for pattern in hierarchical_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    
    # Filter UI-related keywords and patterns
    ui_patterns = [
        r'\d+\s+items?',  # "2 items", "3 items"
        r'\d+\s+models?',  # "1 models", "2 models"
        r'^\d+%$',  # Standalone percentages like "93%", "100%"
        r'\d+%',  # Any percentage (percentages in OCR are typically UI elements)
        r'from\s+\d+["\']?\s+sill\s+height',  # "From 6" Sill Height"
    ]
    
    for pattern in ui_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    
    # Filter standalone simple quoted dimensions that are likely UI labels
    # Patterns like "8"", "10"", "3"" when they appear alone
    if re.match(r'^\d+["\']+$', text_original.strip()):
        return True
    
    # Filter just a number with quote: "8", "10""
    if re.match(r'^\d+["\']\s*$', text_original.strip()):
        return True
    
    # Filter standalone numbers (likely category numbers or list item numbers)
    if re.match(r'^\d+\s*$', text_original.strip()):
        # But allow longer numbers that might be dimensions
        if len(text_original.strip()) <= 3:
            return True
    
    # Filter out common UI terms
    ui_keywords = ['items', 'models', 'item', 'model', 'other', 'collapse', 'expand']
    if text_lower in ui_keywords:
        return True
    
    # Filter out text that contains both a number and UI words (like "3 items", "2 models")
    if any(keyword in text_lower for keyword in ['items', 'models', 'item', 'model']) and any(c.isdigit() for c in text_lower):
        return True
    
    # Filter out very short numeric-only text (likely UI list items or category numbers)
    # But be careful - don't filter legitimate small dimensions with units
    stripped = text_lower.replace('"', '').replace("'", '').replace('x', '').replace('×', '').replace('%', '').strip()
    # If it's just 1-3 digits with no meaningful context, it's likely a UI element
    if len(stripped) <= 3 and stripped.replace('.', '').replace('-', '').isdigit():
        return True
    
    return False

def filter_ui_elements(labels):
    """
    Filter out OCR results that appear to be UI elements.
    
    Args:
        labels: List of OCR label dictionaries
        
    Returns:
        Filtered list of labels
    """
    filtered = []
    for label in labels:
        text = label.get("text", "")
        if not is_ui_element(text):
            filtered.append(label)
    return filtered

def perform_ocr(image, min_conf=0.3, filter_ui=True):
    """
    Perform OCR on an image and optionally filter out UI elements.
    
    Args:
        image: Image to process
        min_conf: Minimum confidence threshold
        filter_ui: Whether to filter out UI-like elements (default: True)
        
    Returns:
        List of OCR label dictionaries
    """
    results = reader.readtext(image)
    labels = []
    for (bbox, text, conf) in results:
        if conf >= min_conf:
            pts = np.array(bbox).astype(int).tolist()
            x, y = int(pts[0][0]), int(pts[0][1])
            labels.append({
                "text": text,
                "confidence": float(conf),
                "position": {"x": x, "y": y},
                "bbox": pts
            })
    
    # Filter out UI elements if requested
    if filter_ui:
        original_count = len(labels)
        labels = filter_ui_elements(labels)
        filtered_count = original_count - len(labels)
        if filtered_count > 0:
            print(f"   Filtered out {filtered_count} UI-like OCR results")
    
    return labels

def auto_estimate_scale(labels):
    """Try to detect numeric values (dimensions) from OCR results to use as scale."""
    for lbl in labels:
        text = lbl["text"].replace(" ", "")
        if text.replace(".", "").isdigit():
            try:
                return float(text)
            except:
                continue
    return None
