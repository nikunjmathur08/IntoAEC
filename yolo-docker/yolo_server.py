"""
YOLO-Only FastAPI Server for IntoAEC
Optimized for cloud deployment with minimal dependencies
"""

import os
import sys
import shutil
import tempfile
import base64
from typing import List, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import io

# Initialize FastAPI app
app = FastAPI(
    title="IntoAEC YOLO Detection API", 
    version="1.0.0",
    description="YOLO-only object detection service for floorplan analysis"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MODEL_PATH = "/app/model/best2.pt"
TEMP_DIR = "/app/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Global model variable
yolo_model = None

def load_yolo_model():
    """Load the YOLO model if not already loaded"""
    global yolo_model
    if yolo_model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"YOLO model file not found at: {MODEL_PATH}")
        
        try:
            yolo_model = YOLO(MODEL_PATH)
            print(f"✅ YOLO model loaded from: {MODEL_PATH}")
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            raise e
    return yolo_model

def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"❌ Error converting image to base64: {e}")
        return ""

def process_yolo_results(results, image_path: str) -> Dict[str, Any]:
    """Process YOLO results and return structured data"""
    try:
        result = results[0]
        detections = []
        
        # Process each detection
        if result.boxes is not None:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Get class name if available
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
        
        # Get image dimensions
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
        print(f"❌ Error processing YOLO results: {e}")
        return {
            "detections": [],
            "total_detections": 0,
            "image_dimensions": {"width": 0, "height": 0}
        }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "IntoAEC YOLO Detection API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check for container orchestration"""
    try:
        # Test model loading
        model = load_yolo_model()
        return {
            "status": "healthy",
            "model_loaded": model is not None,
            "model_path": MODEL_PATH
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/model/info")
async def model_info():
    """Get model information"""
    try:
        model = load_yolo_model()
        return {
            "model_type": "YOLOv8",
            "model_path": MODEL_PATH,
            "classes": model.names if hasattr(model, 'names') else {},
            "total_classes": len(model.names) if hasattr(model, 'names') else 0,
            "status": "loaded"
        }
    except Exception as e:
        return {
            "model_type": "YOLOv8",
            "model_path": MODEL_PATH,
            "error": str(e),
            "status": "error"
        }

@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...), 
    confidence: float = Query(0.25, description="Confidence threshold for detections"),
    iou_threshold: float = Query(0.45, description="IoU threshold for NMS")
):
    """
    Analyze uploaded image using YOLO model
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create temporary file for the uploaded image
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_image_path = temp_file.name
        
        try:
            # Load and run YOLO model
            model = load_yolo_model()
            print(f"🔍 Running YOLO inference on: {file.filename}")
            
            # Run inference with custom parameters
            results = model(
                temp_image_path,
                conf=confidence,
                iou=iou_threshold,
                verbose=False
            )
            
            # Process results
            processed_results = process_yolo_results(results, temp_image_path)
            
            # Create visualization
            output_image_path = os.path.join(TEMP_DIR, f"yolo_result_{file.filename}")
            annotated_image = results[0].plot()
            cv2.imwrite(output_image_path, annotated_image)
            print(f"💾 Saved result image: {output_image_path}")
            
            # Convert result image to base64
            result_image_base64 = image_to_base64(output_image_path)
            
            response_data = {
                "success": True,
                "filename": file.filename,
                "model_used": "yolo",
                "confidence_threshold": confidence,
                "iou_threshold": iou_threshold,
                "analysis_results": processed_results,
                "result_image": result_image_base64,
                "message": f"Successfully analyzed {file.filename} with YOLO. Found {processed_results['total_detections']} detections."
            }
            
            return JSONResponse(content=response_data)
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Model file not found: {str(e)}")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/batch")
async def analyze_batch(
    files: List[UploadFile] = File(...),
    confidence: float = Query(0.25, description="Confidence threshold for detections"),
    iou_threshold: float = Query(0.45, description="IoU threshold for NMS")
):
    """
    Analyze multiple images in batch using YOLO model
    """
    try:
        if len(files) > 10:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed per batch")
        
        # Load model once for batch processing
        model = load_yolo_model()
        results = []
        
        for file in files:
            if not file.content_type.startswith('image/'):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "File must be an image"
                })
                continue
            
            try:
                # Process each file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
                    shutil.copyfileobj(file.file, temp_file)
                    temp_image_path = temp_file.name
                
                # Run YOLO inference
                yolo_results = model(
                    temp_image_path,
                    conf=confidence,
                    iou=iou_threshold,
                    verbose=False
                )
                processed_results = process_yolo_results(yolo_results, temp_image_path)
                
                # Save result image
                output_image_path = os.path.join(TEMP_DIR, f"batch_yolo_{file.filename}")
                annotated_image = yolo_results[0].plot()
                cv2.imwrite(output_image_path, annotated_image)
                result_image_base64 = image_to_base64(output_image_path)
                
                results.append({
                    "filename": file.filename,
                    "success": True,
                    "model_used": "yolo",
                    "analysis_results": processed_results,
                    "result_image": result_image_base64
                })
                
                # Clean up
                if os.path.exists(temp_image_path):
                    os.unlink(temp_image_path)
                    
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
        
        return JSONResponse(content={
            "success": True,
            "total_files": len(files),
            "confidence_threshold": confidence,
            "iou_threshold": iou_threshold,
            "results": results
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting IntoAEC YOLO-Only Detection Server...")
    print(f"📁 Model path: {MODEL_PATH}")
    print(f"📁 Temp directory: {TEMP_DIR}")
    
    # Test model loading on startup
    print("\n🔧 Testing model availability...")
    try:
        load_yolo_model()
        print("✅ YOLO model loaded successfully!")
    except Exception as e:
        print(f"❌ Warning: Could not load YOLO model on startup: {e}")
        print("   Model will be loaded on first request.")
    
    print(f"\n🌐 Server starting on http://0.0.0.0:8000")
    print("📋 Available endpoints:")
    print("   - GET  / - Health check")
    print("   - GET  /health - Container health check")
    print("   - GET  /model/info - Model information")
    print("   - POST /analyze - Single image analysis")
    print("   - POST /analyze/batch - Batch image analysis")
    print("   Press Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
