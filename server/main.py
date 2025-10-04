import os
import sys
import shutil
import tempfile
import detectron2
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import io
import base64
import json
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

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

app = FastAPI(title="IntoAEC YOLO Detection API", version="1.0.0")

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "../ml/demoprpoj/runs/detect/train2/weights/best.pt")
TEMP_DIR = os.path.join(SCRIPT_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# Global model variables to avoid reloading
yolo_model = None
detectron2_model = None
floorplan_analyzer = None

def load_yolo_model():
    """Load the YOLO model if not already loaded"""
    global yolo_model
    if yolo_model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"YOLO model file not found at: {MODEL_PATH}")
        
        # Fix for PyTorch 2.6+ weights_only security change
        import torch
        
        # Try loading with weights_only=False for trusted YOLO models
        try:
            # First try the normal loading
            yolo_model = YOLO(MODEL_PATH)
        except Exception as e:
            if "weights_only" in str(e):
                # If it's the weights_only issue, try with torch.load workaround
                print("🔧 Applying PyTorch 2.6+ compatibility fix for YOLO model loading...")
                
                # Temporarily patch torch.load to use weights_only=False
                original_load = torch.load
                def patched_load(*args, **kwargs):
                    kwargs['weights_only'] = False
                    return original_load(*args, **kwargs)
                
                torch.load = patched_load
                try:
                    yolo_model = YOLO(MODEL_PATH)
                finally:
                    # Restore original torch.load
                    torch.load = original_load
            else:
                raise e
        print(f"   YOLO model loaded from: {MODEL_PATH}")
    return yolo_model

def load_detectron2_model(keep_classes=None, enable_polygon_fitting=False):
    """Load the Detectron2 model if not already loaded"""
    global detectron2_model
    if not DETECTRON2_AVAILABLE:
        raise ImportError("Detectron2 is not available")
    
    # Create new model instance with filtering parameters
    detectron2_model = Detectron2Predictor(
        keep_classes=keep_classes,
        enable_polygon_fitting=enable_polygon_fitting
    )
    detectron2_model.load_model()
    print("   Detectron2 model loaded successfully")
    return detectron2_model

def load_floorplan_analyzer(min_conf=0.4):
    """Load the Floorplan Analyzer"""
    global floorplan_analyzer
    if not FLOORPLAN_ANALYZER_AVAILABLE:
        raise ImportError("Floorplan Analyzer is not available")
    
    floorplan_analyzer = FloorplanAnalyzer(min_conf=min_conf)
    print("   Floorplan Analyzer loaded successfully")
    return floorplan_analyzer

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

@app.get("/model/info")
async def model_info():
    """Get model information"""
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
            "model_path": MODEL_PATH,
            "model_type": "YOLOv8",
            "classes": yolo_model.names if hasattr(yolo_model, 'names') else {}
        }
        info["available_models"].append("yolo")
    except Exception as e:
        info["yolo"]["error"] = str(e)
    
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
            info["detectron2"]["error"] = str(e)
    
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
            info["floorplan"]["error"] = str(e)
    
    return info

@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...), 
    model_type: str = Query("yolo", description="Model to use: 'yolo', 'detectron2', 'floorplan', or 'combined'"),
    keep_classes: str = Query(None, description="Comma-separated list of classes to keep (e.g., 'floor,Room')"),
    enable_polygon_fitting: bool = Query(False, description="Enable polygon fitting for room detection"),
    min_conf: float = Query(0.4, description="Minimum confidence for floorplan OCR detections"),
    iou_threshold: float = Query(0.3, description="IoU threshold for merging detections in combined mode")
):
    """
    Analyze uploaded image using specified model (YOLO, Detectron2, Floorplan Analyzer, or Combined)
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate model type
        if model_type not in ["yolo", "detectron2", "floorplan", "combined"]:
            raise HTTPException(status_code=400, detail="model_type must be 'yolo', 'detectron2', 'floorplan', or 'combined'")
        
        # Create temporary file for the uploaded image
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            # Copy uploaded file to temp file
            shutil.copyfileobj(file.file, temp_file)
            temp_image_path = temp_file.name
        
        try:
            if model_type == "yolo":
                # YOLO Analysis
                yolo_model = load_yolo_model()
                print(f"   Running YOLO inference on: {file.filename}")
                results = yolo_model(temp_image_path)
                
                # Save result image with bounding boxes
                output_image_path = os.path.join(TEMP_DIR, f"yolo_result_{file.filename}")
                
                # Use plot method to create annotated image
                annotated_image = results[0].plot()  # Returns numpy array with annotations
                
                # Save the annotated image using OpenCV
                cv2.imwrite(output_image_path, annotated_image)
                print(f"   Saved YOLO result image: {output_image_path}")
                
                # Process results
                processed_results = process_yolo_results(results, temp_image_path)
                
                # Convert result image to base64
                result_image_base64 = image_to_base64(output_image_path)
                
                response_data = {
                    "success": True,
                    "filename": file.filename,
                    "model_used": "yolo",
                    "analysis_results": processed_results,
                    "result_image": result_image_base64,
                    "message": f"Successfully analyzed {file.filename} with YOLO. Found {processed_results['total_detections']} detections."
                }
                
            elif model_type == "detectron2":
                # Detectron2 Analysis
                # Parse keep_classes parameter
                keep_classes_set = None
                if keep_classes:
                    keep_classes_set = set(cls.strip() for cls in keep_classes.split(','))
                    print(f"   Filtering classes to keep: {keep_classes_set}")
                
                detectron2_model = load_detectron2_model(
                    keep_classes=keep_classes_set,
                    enable_polygon_fitting=enable_polygon_fitting
                )
                print(f"   Running Detectron2 inference on: {file.filename}")
                
                # Run Detectron2 prediction with filtering
                results = detectron2_model.predict(temp_image_path)
                
                # Save result image
                output_image_path = os.path.join(TEMP_DIR, f"detectron2_result_{file.filename}")
                cv2.imwrite(output_image_path, results["visualized_image"])
                print(f"   Saved Detectron2 result image: {output_image_path}")
                
                # Get detection summary
                summary = detectron2_model.get_detection_summary(results)
                
                # Convert result image to base64
                result_image_base64 = image_to_base64(output_image_path)
                
                # Format results to match YOLO format for consistency
                formatted_detections = []
                for detection in summary["detection_details"]:
                    formatted_detections.append({
                        "class_id": detection["class_id"],
                        "class_name": detection["class_name"],
                        "confidence": detection["confidence"],
                        "bbox": detection["bbox"]
                    })
                
                response_data = {
                    "success": True,
                    "filename": file.filename,
                    "model_used": "detectron2",
                    "analysis_results": {
                        "detections": formatted_detections,
                        "total_detections": summary["total_detections"],
                        "detections_by_class": summary["detections_by_class"]
                    },
                    "result_image": result_image_base64,
                    "message": f"Successfully analyzed {file.filename} with Detectron2. Found {summary['total_detections']} detections."
                }
            
            elif model_type == "floorplan":
                # Floorplan Analyzer
                floorplan_model = load_floorplan_analyzer(min_conf=min_conf)
                print(f"🔍 Running Floorplan Analyzer on: {file.filename}")
                
                # Run analysis
                results = floorplan_model.analyze(temp_image_path)
                
                # Save result image
                output_image_path = os.path.join(TEMP_DIR, f"floorplan_result_{file.filename}")
                cv2.imwrite(output_image_path, results["visualized_image"])
                print(f"   Saved Floorplan result image: {output_image_path}")
                
                # Get detection summary
                summary = floorplan_model.get_detection_summary(results)
                
                # Convert result image to base64
                result_image_base64 = image_to_base64(output_image_path)
                
                # Format results
                formatted_detections = []
                for detection in summary["detection_details"]:
                    formatted_detections.append({
                        "class_id": detection["class_id"],
                        "class_name": detection["class_name"],
                        "confidence": detection["confidence"],
                        "bbox": detection["bbox"],
                        "fuzzy_score": detection.get("fuzzy_score", 0)
                    })
                
                response_data = {
                    "success": True,
                    "filename": file.filename,
                    "model_used": "floorplan",
                    "analysis_results": {
                        "detections": formatted_detections,
                        "total_detections": summary["total_detections"],
                        "detections_by_class": summary["detections_by_class"],
                        "num_contours": summary.get("num_contours", 0),
                        "scale_info": summary.get("scale_info", {})
                    },
                    "result_image": result_image_base64,
                    "message": f"Successfully analyzed {file.filename} with Floorplan Analyzer. Found {summary['total_detections']} labels and {summary.get('num_contours', 0)} contours."
                }
            
            elif model_type == "combined":
                # Combined Analysis - Run all three models and merge results
                if not DETECTION_MERGER_AVAILABLE:
                    raise HTTPException(status_code=500, detail="Detection merger not available")
                
                print(f"   Running COMBINED analysis on: {file.filename}")
                print("   This will run YOLO, Detectron2, and Floorplan Analyzer")
                
                # Initialize lists to store detections from each model
                yolo_detections = []
                detectron2_detections = []
                floorplan_detections = []
                
                # 1. Run YOLO
                try:
                    yolo_model = load_yolo_model()
                    print("   Running YOLO...")
                    yolo_results = yolo_model(temp_image_path)
                    yolo_processed = process_yolo_results(yolo_results, temp_image_path)
                    yolo_detections = yolo_processed.get('detections', [])
                    print(f"      Found {len(yolo_detections)} YOLO detections")
                except Exception as e:
                    print(f"   YOLO failed: {e}")
                
                # 2. Run Detectron2
                if DETECTRON2_AVAILABLE:
                    try:
                        keep_classes_set = None
                        if keep_classes:
                            keep_classes_set = set(cls.strip() for cls in keep_classes.split(','))
                        
                        detectron2_model = load_detectron2_model(
                            keep_classes=keep_classes_set,
                            enable_polygon_fitting=enable_polygon_fitting
                        )
                        print("   Running Detectron2...")
                        d2_results = detectron2_model.predict(temp_image_path)
                        d2_summary = detectron2_model.get_detection_summary(d2_results)
                        
                        # Format Detectron2 detections
                        for detection in d2_summary["detection_details"]:
                            detectron2_detections.append({
                                "class_id": detection["class_id"],
                                "class_name": detection["class_name"],
                                "confidence": detection["confidence"],
                                "bbox": detection["bbox"]
                            })
                        print(f"      Found {len(detectron2_detections)} Detectron2 detections")
                    except Exception as e:
                        print(f"   Detectron2 failed: {e}")
                else:
                    print("   Detectron2 not available")
                
                # 3. Run Floorplan Analyzer
                if FLOORPLAN_ANALYZER_AVAILABLE:
                    try:
                        floorplan_model = load_floorplan_analyzer()
                        if floorplan_model.min_conf != min_conf:
                            floorplan_model.min_conf = min_conf
                        
                        print("   Running Floorplan Analyzer...")
                        fp_results = floorplan_model.analyze(temp_image_path)
                        fp_summary = floorplan_model.get_detection_summary(fp_results)
                        
                        # Format Floorplan detections
                        for detection in fp_summary["detection_details"]:
                            floorplan_detections.append({
                                "class_id": detection["class_id"],
                                "class_name": detection["class_name"],
                                "confidence": detection["confidence"],
                                "bbox": detection["bbox"],
                                "fuzzy_score": detection.get("fuzzy_score", 0)
                            })
                        print(f"      Found {len(floorplan_detections)} Floorplan detections")
                    except Exception as e:
                        print(f"   Floorplan Analyzer failed: {e}")
                else:
                    print("   Floorplan Analyzer not available")
                
                # Merge detections from all models
                print(f"   Merging detections (IoU threshold: {iou_threshold})...")
                merged_detections = merge_detections(
                    yolo_detections=yolo_detections,
                    detectron2_detections=detectron2_detections,
                    floorplan_detections=floorplan_detections,
                    iou_threshold=iou_threshold
                )
                
                print(f"   Merged to {len(merged_detections)} unique detections")
                
                # Create combined visualization
                print("   Creating combined visualization...")
                combined_image = create_combined_visualization(
                    image_path=temp_image_path,
                    merged_detections=merged_detections,
                    show_model_tags=True
                )
                
                # Save combined result image
                output_image_path = os.path.join(TEMP_DIR, f"combined_result_{file.filename}")
                cv2.imwrite(output_image_path, combined_image)
                print(f"   Saved combined result image: {output_image_path}")
                
                # Convert to base64
                result_image_base64 = image_to_base64(output_image_path)
                
                # Get combined summary
                combined_summary = get_combined_summary(merged_detections)
                
                # Format response
                response_data = {
                    "success": True,
                    "filename": file.filename,
                    "model_used": "combined",
                    "analysis_results": {
                        "detections": merged_detections,
                        "total_detections": combined_summary["total_detections"],
                        "detections_by_class": combined_summary["detections_by_class"],
                        "detections_by_source_count": combined_summary["detections_by_source_count"],
                        "model_contributions": combined_summary["model_contributions"],
                        "unique_classes": combined_summary["unique_classes"]
                    },
                    "result_image": result_image_base64,
                    "message": (
                        f"Successfully analyzed {file.filename} with combined models. "
                        f"Found {combined_summary['total_detections']} unique detections "
                        f"({combined_summary['model_contributions']['yolo']} YOLO, "
                        f"{combined_summary['model_contributions']['detectron2']} Detectron2, "
                        f"{combined_summary['model_contributions']['floorplan']} Floorplan). "
                        f"{combined_summary['detections_by_source_count'].get(3, 0)} detections confirmed by all 3 models."
                    )
                }
            
            return JSONResponse(content=response_data)
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
            # Keep result image for a bit longer for debugging
                
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Model file not found: {str(e)}")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/batch")
async def analyze_batch(
    files: List[UploadFile] = File(...),
    model_type: str = Query("yolo", description="Model to use: 'yolo' or 'detectron2'"),
    keep_classes: str = Query(None, description="Comma-separated list of classes to keep (e.g., 'floor,Room')"),
    enable_polygon_fitting: bool = Query(False, description="Enable polygon fitting for room detection")
):
    """
    Analyze multiple images in batch using specified model
    """
    try:
        if len(files) > 10:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed per batch")
        
        # Validate model type
        if model_type not in ["yolo", "detectron2"]:
            raise HTTPException(status_code=400, detail="model_type must be 'yolo' or 'detectron2'")
        
        # Load appropriate model
        if model_type == "yolo":
            model = load_yolo_model()
        else:
            # Parse keep_classes parameter for detectron2
            keep_classes_set = None
            if keep_classes:
                keep_classes_set = set(cls.strip() for cls in keep_classes.split(','))
            
            model = load_detectron2_model(
                keep_classes=keep_classes_set,
                enable_polygon_fitting=enable_polygon_fitting
            )
        
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
                
                if model_type == "yolo":
                    # YOLO processing
                    yolo_results = model(temp_image_path)
                    processed_results = process_yolo_results(yolo_results, temp_image_path)
                    
                    # Save result image
                    output_image_path = os.path.join(TEMP_DIR, f"batch_yolo_{file.filename}")
                    
                    # Use plot method to create annotated image
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
                    
                else:  # detectron2
                    # Detectron2 processing
                    detectron2_results = model.predict(temp_image_path)
                    summary = model.get_detection_summary(detectron2_results)
                    
                    # Save result image
                    output_image_path = os.path.join(TEMP_DIR, f"batch_detectron2_{file.filename}")
                    cv2.imwrite(output_image_path, detectron2_results["visualized_image"])
                    result_image_base64 = image_to_base64(output_image_path)
                    
                    # Format results
                    formatted_detections = []
                    for detection in summary["detection_details"]:
                        formatted_detections.append({
                            "class_id": detection["class_id"],
                            "class_name": detection["class_name"],
                            "confidence": detection["confidence"],
                            "bbox": detection["bbox"]
                        })
                    
                    results.append({
                        "filename": file.filename,
                        "success": True,
                        "model_used": "detectron2",
                        "analysis_results": {
                            "detections": formatted_detections,
                            "total_detections": summary["total_detections"],
                            "detections_by_class": summary["detections_by_class"]
                        },
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
            "results": results
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting IntoAEC Multi-Model Detection Server...")
    print(f"📁 YOLO Model path: {MODEL_PATH}")
    print(f"📁 Temp directory: {TEMP_DIR}")
    print(f"🤖 Detectron2 available: {DETECTRON2_AVAILABLE}")
    
    # Try to load models on startup
    print("\n🔧 Testing model availability...")
    
    # Test YOLO
    try:
        load_yolo_model()
        print("  YOLO model loaded successfully!")
    except Exception as e:
        print(f"   Warning: Could not load YOLO model on startup: {e}")
        print("   YOLO model will be loaded on first request.")
    
    # Test Detectron2
    if DETECTRON2_AVAILABLE:
        try:
            load_detectron2_model()
            print("   Detectron2 model loaded successfully!")
        except Exception as e:
            print(f"   Warning: Could not load Detectron2 model on startup: {e}")
            print("   Detectron2 model will be loaded on first request.")
    else:
        print("   Detectron2 not available - install detectron2 to enable Mask R-CNN analysis")
    
    print(f"\n   Server starting on http://localhost:8000")
    print("   Available endpoints:")
    print("   - GET  /model/info - Check model availability")
    print("   - POST /analyze?model_type=yolo - YOLO analysis")
    print("   - POST /analyze?model_type=detectron2 - Detectron2 analysis")
    print("   - POST /analyze/batch?model_type=yolo - Batch YOLO analysis")
    print("   - POST /analyze/batch?model_type=detectron2 - Batch Detectron2 analysis")
    print("   Press Ctrl+C to stop the server\n")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
