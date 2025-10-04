"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class ModelType(str, Enum):
    YOLO = "yolo"
    DETECTRON2 = "detectron2"
    FLOORPLAN = "floorplan"
    COMBINED = "combined"

class AnalysisRequest(BaseModel):
    """Secure analysis request model"""
    model_type: ModelType = Field(..., description="Model type to use for analysis")
    keep_classes: Optional[str] = Field(None, max_length=500, description="Comma-separated list of classes to keep")
    enable_polygon_fitting: bool = Field(False, description="Enable polygon fitting for room detection")
    min_conf: float = Field(0.4, ge=0.0, le=1.0, description="Minimum confidence threshold")
    iou_threshold: float = Field(0.3, ge=0.0, le=1.0, description="IoU threshold for merging detections")
    
    @validator('keep_classes')
    def validate_keep_classes(cls, v):
        if v is not None:
            # Sanitize class names
            classes = [cls.strip().lower() for cls in v.split(',')]
            # Remove potentially dangerous characters
            sanitized_classes = []
            for cls_name in classes:
                if cls_name and len(cls_name) <= 50:  # Reasonable length limit
                    # Only allow alphanumeric, spaces, and common punctuation
                    if re.match(r'^[a-zA-Z0-9\s\-_]+$', cls_name):
                        sanitized_classes.append(cls_name)
            
            if not sanitized_classes:
                raise ValueError('No valid class names provided')
            
            return ','.join(sanitized_classes)
        return v

class BatchAnalysisRequest(BaseModel):
    """Secure batch analysis request model"""
    model_type: ModelType = Field(..., description="Model type to use for analysis")
    keep_classes: Optional[str] = Field(None, max_length=500, description="Comma-separated list of classes to keep")
    enable_polygon_fitting: bool = Field(False, description="Enable polygon fitting for room detection")
    max_files: int = Field(10, ge=1, le=50, description="Maximum number of files to process")

class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, max_length=100, description="Password")
    
    @validator('username')
    def validate_username(cls, v):
        # Only allow alphanumeric and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()

class RegisterRequest(BaseModel):
    """Registration request model"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password")
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()
    
    @validator('email')
    def validate_email(cls, v):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        # Password strength requirements
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class AnalysisResponse(BaseModel):
    """Secure analysis response model"""
    success: bool
    filename: str
    model_used: str
    analysis_results: Dict[str, Any]
    result_image: Optional[str] = None
    message: str
    processing_time: Optional[float] = None
    
    class Config:
        # Prevent arbitrary types in response
        arbitrary_types_allowed = False

class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: str
    detail: Optional[str] = None
    timestamp: str
    request_id: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    uptime: Optional[float] = None

# Import re for validators
import re
