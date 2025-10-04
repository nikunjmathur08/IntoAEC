"""
Security utilities for file validation and sanitization
"""
import os
import re
import magic
from typing import List, Optional, Tuple
from fastapi import HTTPException, UploadFile
import cv2
import numpy as np
from PIL import Image
import io

# Security configuration
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf', '.dwg'}
ALLOWED_MIME_TYPES = {
    'image/png', 'image/jpeg', 'image/jpg',
    'application/pdf',
    'application/acad', 'application/dwg', 'application/x-dwg',
    'application/x-autocad', 'image/vnd.dwg'
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILENAME_LENGTH = 255

# Dangerous file signatures to block
DANGEROUS_SIGNATURES = [
    b'<script',
    b'javascript:',
    b'vbscript:',
    b'data:text/html',
    b'<iframe',
    b'<object',
    b'<embed'
]

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other attacks"""
    if not filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty")
    
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > MAX_FILENAME_LENGTH:
        name, ext = os.path.splitext(filename)
        filename = name[:MAX_FILENAME_LENGTH - len(ext)] + ext
    
    # Ensure filename is not empty after sanitization
    if not filename or filename == '.' or filename == '..':
        filename = f"file_{os.urandom(8).hex()}"
    
    return filename

def validate_file_extension(filename: str) -> bool:
    """Validate file extension"""
    if not filename:
        return False
    
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS

def validate_file_size(file_size: int) -> bool:
    """Validate file size"""
    return 0 < file_size <= MAX_FILE_SIZE

def validate_mime_type(file_path: str, expected_mime: str) -> bool:
    """Validate file MIME type using python-magic"""
    try:
        detected_mime = magic.from_file(file_path, mime=True)
        return detected_mime in ALLOWED_MIME_TYPES
    except Exception:
        return False

def scan_file_content(file_content: bytes) -> Tuple[bool, str]:
    """Scan file content for malicious patterns"""
    try:
        # Check for dangerous signatures
        content_lower = file_content.lower()
        for signature in DANGEROUS_SIGNATURES:
            if signature in content_lower:
                return False, f"Dangerous content detected: {signature.decode()}"
        
        # Additional security checks
        if b'\x00' in file_content[:1024]:  # Null bytes in header
            return False, "Suspicious null bytes detected"
        
        return True, "File content is safe"
    except Exception as e:
        return False, f"Content scan failed: {str(e)}"

def validate_image_file(file_content: bytes) -> Tuple[bool, str]:
    """Validate image file integrity"""
    try:
        # Try to open with PIL
        image = Image.open(io.BytesIO(file_content))
        image.verify()
        
        # Try to open with OpenCV
        nparr = np.frombuffer(file_content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return False, "Invalid image format"
        
        # Check image dimensions (prevent extremely large images)
        height, width = img.shape[:2]
        if width > 10000 or height > 10000:
            return False, "Image dimensions too large"
        
        return True, "Image is valid"
    except Exception as e:
        return False, f"Image validation failed: {str(e)}"

def validate_pdf_file(file_content: bytes) -> Tuple[bool, str]:
    """Validate PDF file integrity"""
    try:
        # Check PDF signature
        if not file_content.startswith(b'%PDF-'):
            return False, "Invalid PDF signature"
        
        # Check for embedded JavaScript (security risk)
        if b'/JavaScript' in file_content or b'/JS' in file_content:
            return False, "PDF contains JavaScript (security risk)"
        
        return True, "PDF is valid"
    except Exception as e:
        return False, f"PDF validation failed: {str(e)}"

def validate_dwg_file(file_content: bytes) -> Tuple[bool, str]:
    """Validate DWG file integrity"""
    try:
        # DWG files start with specific bytes
        if len(file_content) < 6:
            return False, "File too short to be a valid DWG"
        
        # Check for DWG signature (simplified check)
        dwg_signatures = [
            b'AC1015',  # AutoCAD 2000
            b'AC1018',  # AutoCAD 2004
            b'AC1021',  # AutoCAD 2007
            b'AC1024',  # AutoCAD 2010
            b'AC1027',  # AutoCAD 2013
        ]
        
        for sig in dwg_signatures:
            if sig in file_content[:100]:
                return True, "DWG file is valid"
        
        return False, "Invalid DWG file signature"
    except Exception as e:
        return False, f"DWG validation failed: {str(e)}"

def comprehensive_file_validation(
    file: UploadFile, 
    temp_file_path: str
) -> Tuple[bool, str]:
    """Comprehensive file validation"""
    try:
        # 1. Validate filename
        sanitized_name = sanitize_filename(file.filename)
        if sanitized_name != file.filename:
            return False, "Invalid filename"
        
        # 2. Validate file extension
        if not validate_file_extension(file.filename):
            return False, f"File extension not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        
        # 3. Validate file size
        if not validate_file_size(file.size):
            return False, f"File size exceeds limit. Max: {MAX_FILE_SIZE // (1024*1024)}MB"
        
        # 4. Validate MIME type
        if not validate_mime_type(temp_file_path, file.content_type):
            return False, f"MIME type not allowed: {file.content_type}"
        
        # 5. Read file content for validation
        with open(temp_file_path, 'rb') as f:
            file_content = f.read()
        
        # 6. Scan for malicious content
        is_safe, safety_msg = scan_file_content(file_content)
        if not is_safe:
            return False, safety_msg
        
        # 7. File-type specific validation
        file_ext = os.path.splitext(file.filename.lower())[1]
        
        if file_ext in ['.png', '.jpg', '.jpeg']:
            is_valid, valid_msg = validate_image_file(file_content)
        elif file_ext == '.pdf':
            is_valid, valid_msg = validate_pdf_file(file_content)
        elif file_ext == '.dwg':
            is_valid, valid_msg = validate_dwg_file(file_content)
        else:
            is_valid, valid_msg = True, "File type validation skipped"
        
        if not is_valid:
            return False, valid_msg
        
        return True, "File validation passed"
        
    except Exception as e:
        return False, f"File validation error: {str(e)}"

def create_secure_temp_file(original_filename: str) -> str:
    """Create a secure temporary file with sanitized name"""
    import tempfile
    
    sanitized_name = sanitize_filename(original_filename)
    temp_dir = tempfile.gettempdir()
    secure_temp_path = os.path.join(temp_dir, f"secure_{os.urandom(16).hex()}_{sanitized_name}")
    
    return secure_temp_path

def cleanup_temp_file(file_path: str) -> None:
    """Safely cleanup temporary file"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"Warning: Could not cleanup temp file {file_path}: {e}")
