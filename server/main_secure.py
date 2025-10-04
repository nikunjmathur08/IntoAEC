"""
Secure IntoAEC Multi-Model Detection Server
"""
import os
import sys
import shutil
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import io
import base64
import json
import logging

# Security imports
from auth import authenticate_user, create_access_token, verify_token, create_user, Token, LoginRequest, RegisterRequest
from security import comprehensive_file_validation, create_secure_temp_file, cleanup_temp_file, sanitize_filename
from models import AnalysisRequest, BatchAnalysisRequest, AnalysisResponse, ErrorResponse, HealthResponse

# ML imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../ml"))

try:
    from detectron2_inference import Detectron2Predictor
    DETECTRON2_AVAILABLE = True
    print("  Detectron2 module loaded successfully")
except ImportError as e:
    DETECTRON2_AVAILABLE = False
    print(f"   Detectron2 not available: {e}")
    print("   Only YOLO analysis will be available")

try:
    from floorplan_analyzer_wrapper import FloorplanAnalyzer
    FLOORPLAN_ANALYZER_AVAILABLE = True
    print("   Floorplan Analyzer module loaded successfully")
except ImportError as e:
    FLOORPLAN_ANALYZER_AVAILABLE = False
    print(f"   Floorplan Analyzer not available: {e}")
    print("   Install requirements: pip install easyocr rapidfuzz")

try:
    from detection_merger import merge_detections, create_combined_visualization, get_combined_summary
    DETECTION_MERGER_AVAILABLE = True
    print("   Detection Merger module loaded successfully")
except ImportError as e:
    DETECTION_MERGER_AVAILABLE = False
    print(f"   Detection Merger not available: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="IntoAEC Secure Detection API", 
    version="2.0.0",
    description="Secure multi-model floor plan analysis API",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security middleware
security = HTTPBearer()

# Secure CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "../ml/demoprpoj/runs/detect/train2/weights/best.pt")
TEMP_DIR = os.path.join(SCRIPT_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# Global model variables to avoid reloading
yolo_model = None
detectron2_model = None
floorplan_analyzer = None

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    token_data = verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

# Rate limiting decorator
def rate_limit(limit: str):
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

def load_yolo_model():
    """Load the YOLO model if not already loaded"""
    global yolo_model
    if yolo_model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("YOLO model file not found")
        
        try:
            yolo_model = YOLO(MODEL_PATH)
            logger.info(f"YOLO model loaded from: {MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise HTTPException(status_code=500, detail="Model loading failed")
    return yolo_model

def load_detectron2_model(keep_classes=None, enable_polygon_fitting=False):
    """Load the Detectron2 model if not already loaded"""
    global detectron2_model
    if not DETECTRON2_AVAILABLE:
        raise HTTPException(status_code=500, detail="Detectron2 is not available")
    
    try:
        detectron2_model = Detectron2Predictor(
            keep_classes=keep_classes,
            enable_polygon_fitting=enable_polygon_fitting
        )
        detectron2_model.load_model()
        logger.info("Detectron2 model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Detectron2 model: {e}")
        raise HTTPException(status_code=500, detail="Detectron2 model loading failed")
    return detectron2_model

def load_floorplan_analyzer(min_conf=0.4):
    """Load the Floorplan Analyzer"""
    global floorplan_analyzer
    if not FLOORPLAN_ANALYZER_AVAILABLE:
        raise HTTPException(status_code=500, detail="Floorplan Analyzer is not available")
    
    try:
        floorplan_analyzer = FloorplanAnalyzer(min_conf=min_conf)
        logger.info("Floorplan Analyzer loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Floorplan Analyzer: {e}")
        raise HTTPException(status_code=500, detail="Floorplan Analyzer loading failed")
    return floorplan_analyzer

def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        logger.error(f"Error converting image to base64: {e}")
        return ""

def process_yolo_results(results, image_path: str) -> Dict[str, Any]:
    """Process YOLO results and return structured data"""
    try:
        result = results[0]
        detections = []
        
        if result.boxes is not None:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                class_name = result.names[cls] if result.names and cls in result.names else f"class_{cls}"
                
                detection = {
                    "class_id": cls,
                    "class_name": class_name,
                    "confidence": round(conf, 4),
                    "bbox": {
                        "x1": int(x1),
                        "y1": int(y1),
                        "x2": int(x2),
                        "y2": int(y2),
                        "width": int(x2 - x1),
                        "height": int(y2 - y1)
                    }
                }
                detections.append(detection)
        
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        
        return {
            "detections": detections,
            "total_detections": len(detections),
            "image_dimensions": {
                "width": width,
                "height": height
            }
        }
    except Exception as e:
        logger.error(f"Error processing YOLO results: {e}")
        return {
            "detections": [],
            "total_detections": 0,
            "image_dimensions": {"width": 0, "height": 0}
        }

# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="2.0.0"
    )

@app.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Authenticate user and return access token"""
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username, "user_id": user.user_id})
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800  # 30 minutes
    )

@app.post("/auth/register")
async def register(register_data: RegisterRequest):
    """Register a new user"""
    try:
        from auth import create_user
        user = create_user(
            username=register_data.username,
            email=register_data.email,
            password=register_data.password
        )
        return {"message": "User created successfully", "username": user.username}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/model/info")
@rate_limit("10/minute")
async def model_info(current_user = Depends(get_current_user)):
    """Get model information (requires authentication)"""
    info = {
        "available_models": [],
        "yolo": {"available": False, "error": None},
        "detectron2": {"available": DETECTRON2_AVAILABLE, "error": None},
        "floorplan": {"available": FLOORPLAN_ANALYZER_AVAILABLE, "error": None}
    }
    
    # Check YOLO
    try:
        yolo_model = load_yolo_model()
        info["yolo"] = {
            "available": True,
            "model_type": "YOLOv8",
            "classes": yolo_model.names if hasattr(yolo_model, 'names') else {}
        }
        info["available_models"].append("yolo")
    except Exception as e:
        info["yolo"]["error"] = "Model loading failed"
        logger.error(f"YOLO model check failed: {e}")
    
    # Check Detectron2
    if DETECTRON2_AVAILABLE:
        try:
            detectron2_model = load_detectron2_model()
            info["detectron2"] = {
                "available": True,
                "model_type": "Mask R-CNN",
                "classes": detectron2_model.class_names
            }
            info["available_models"].append("detectron2")
        except Exception as e:
            info["detectron2"]["error"] = "Model loading failed"
            logger.error(f"Detectron2 model check failed: {e}")
    
    # Check Floorplan Analyzer
    if FLOORPLAN_ANALYZER_AVAILABLE:
        try:
            floorplan_model = load_floorplan_analyzer()
            info["floorplan"] = {
                "available": True,
                "model_type": "OCR + Contour Detection",
                "description": "EasyOCR-based text detection with contour analysis"
            }
            info["available_models"].append("floorplan")
        except Exception as e:
            info["floorplan"]["error"] = "Model loading failed"
            logger.error(f"Floorplan Analyzer check failed: {e}")
    
    return info

@app.post("/analyze", response_model=AnalysisResponse)
@rate_limit("5/minute")
async def analyze_image(
    request: Request,
    file: UploadFile = File(...),
    model_type: str = "yolo",
    keep_classes: Optional[str] = None,
    enable_polygon_fitting: bool = False,
    min_conf: float = 0.4,
    iou_threshold: float = 0.3,
    current_user = Depends(get_current_user)
):
    """Analyze uploaded image using specified model (requires authentication)"""
    start_time = time.time()
    temp_image_path = None
    
    try:
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create secure temporary file
        temp_image_path = create_secure_temp_file(file.filename)
        
        # Save uploaded file
        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Comprehensive file validation
        is_valid, validation_msg = comprehensive_file_validation(file, temp_image_path)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"File validation failed: {validation_msg}")
        
        # Validate model type
        if model_type not in ["yolo", "detectron2", "floorplan", "combined"]:
            raise HTTPException(status_code=400, detail="Invalid model type")
        
        # Process based on model type
        if model_type == "yolo":
            yolo_model = load_yolo_model()
            results = yolo_model(temp_image_path)
            processed_results = process_yolo_results(results, temp_image_path)
            
            # Save result image
            output_image_path = os.path.join(TEMP_DIR, f"yolo_result_{sanitize_filename(file.filename)}")
            annotated_image = results[0].plot()
            cv2.imwrite(output_image_path, annotated_image)
            result_image_base64 = image_to_base64(output_image_path)
            
            response_data = AnalysisResponse(
                success=True,
                filename=sanitize_filename(file.filename),
                model_used="yolo",
                analysis_results=processed_results,
                result_image=result_image_base64,
                message=f"Successfully analyzed {file.filename} with YOLO. Found {processed_results['total_detections']} detections.",
                processing_time=time.time() - start_time
            )
        
        # Add other model processing here...
        else:
            raise HTTPException(status_code=400, detail="Model type not implemented yet")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")
    finally:
        # Cleanup temporary files
        if temp_image_path and os.path.exists(temp_image_path):
            cleanup_temp_file(temp_image_path)

@app.get("/health")
async def health_check():
    """Public health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    print("🚀 Starting IntoAEC Secure Multi-Model Detection Server...")
    print(f"📁 YOLO Model path: {MODEL_PATH}")
    print(f"📁 Temp directory: {TEMP_DIR}")
    print(f"🤖 Detectron2 available: {DETECTRON2_AVAILABLE}")
    print(f"🔐 Security features enabled")
    
    # Test model loading
    print("\n🔧 Testing model availability...")
    
    try:
        load_yolo_model()
        print("  YOLO model loaded successfully!")
    except Exception as e:
        print(f"   Warning: Could not load YOLO model on startup: {e}")
    
    print(f"\n   Server starting on http://localhost:8000")
    print("   Available endpoints:")
    print("   - POST /auth/login - User authentication")
    print("   - POST /auth/register - User registration")
    print("   - GET  /model/info - Check model availability (authenticated)")
    print("   - POST /analyze - Image analysis (authenticated)")
    print("   - GET  /health - Health check")
    print("   Press Ctrl+C to stop the server\n")
    
    uvicorn.run("main_secure:app", host="0.0.0.0", port=8000, reload=False)
