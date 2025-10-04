# Floorplan Analyzer Integration

The Floorplan Analyzer is now integrated as a third model option alongside YOLO and Detectron2.

## What it Does

The Floorplan Analyzer provides:
- **OCR Text Detection**: Extracts room labels and text from floor plans
- **Contour Detection**: Identifies room boundaries and shapes
- **Fuzzy Matching**: Corrects OCR results to known room names (Living Room, Bedroom, etc.)
- **Scale Estimation**: Auto-detects scale from numeric values in the floor plan
- **Area Calculation**: Calculates area of detected regions

## Setup

### 1. Install Dependencies

The floorplan analyzer requires additional Python packages:

```bash
cd /Users/nikunjmathur/Developer/IntoAEC/server
pip install easyocr rapidfuzz
```

### 2. Verify Installation

Start the FastAPI server:

```bash
cd /Users/nikunjmathur/Developer/IntoAEC/server
python main.py
```

You should see:
```
✅ Floorplan Analyzer module loaded successfully
```

### 3. Check Model Availability

Visit http://localhost:8000/model/info to check which models are available:

```json
{
  "available_models": ["yolo", "detectron2", "floorplan"],
  "floorplan": {
    "available": true,
    "model_type": "OCR + Contour Detection",
    "description": "EasyOCR-based text detection with contour analysis"
  }
}
```

## Usage

### Frontend

1. Upload your floor plan image
2. Select which models to run:
   - ☑ YOLO - Object detection
   - ☑ Detectron2 - Instance segmentation
   - ☑ **Floorplan Analyzer** - Text + contour detection
3. Click "Start Analysis"
4. View combined results on the dashboard

### Backend API

#### Single File Analysis

```bash
curl -X POST "http://localhost:8000/analyze?model_type=floorplan&min_conf=0.4" \
  -F "file=@path/to/floorplan.png"
```

#### Parameters

- `model_type`: `"floorplan"` for the floorplan analyzer
- `min_conf`: Minimum confidence threshold for OCR (default: 0.4)

#### Response Format

```json
{
  "success": true,
  "filename": "floorplan.png",
  "model_used": "floorplan",
  "analysis_results": {
    "detections": [
      {
        "class_name": "Living Room",
        "confidence": 0.95,
        "bbox": {...},
        "fuzzy_score": 85
      }
    ],
    "total_detections": 12,
    "detections_by_class": {
      "Living Room": 1,
      "Bedroom": 3,
      "Bathroom": 2
    },
    "num_contours": 15,
    "scale_info": {
      "px_per_unit": 10.5,
      "has_scale": true
    }
  },
  "result_image": "base64_encoded_image",
  "message": "Successfully analyzed floorplan.png with Floorplan Analyzer..."
}
```

## Features

### Text Detection (OCR)
- Uses EasyOCR for multi-language text detection
- Extracts room labels, dimensions, and annotations
- Returns bounding boxes and confidence scores

### Fuzzy Matching
- Automatically corrects OCR mistakes
- Matches detected text to known room names:
  - Living Room, Bedroom, Bathroom, Kitchen, Dining Room
  - Hallway, Closet, Entry, Balcony, Garage
  - Master Bedroom, Guest Room, Office, Study
  - And 20+ more common room names

### Contour Detection
- Identifies room boundaries using edge detection
- Calculates area of each detected region
- Filters out noise and small artifacts

### Scale Detection
- Auto-detects scale from numeric values in the image
- Converts pixel measurements to real-world units
- Useful for area calculations and measurements

## Visualization

The result image includes:
- **Green boxes**: Text labels with high fuzzy match score (>75%)
- **Orange boxes**: Partial match (50-75%)
- **Red boxes**: Low match (<50%)
- **Blue contours**: Detected room boundaries
- **Confidence scores**: Shown below each label

## Combined Analysis

When running multiple models simultaneously:

```
Combined Results Panel:
┌──────────────────────────────┐
│ Living Room            1     │
│ YOLO: 0 | D2: 0 | FP: 1     │
└──────────────────────────────┘

┌──────────────────────────────┐
│ Door                   8     │
│ YOLO: 5 | D2: 3 | FP: 0     │
└──────────────────────────────┘
```

The dashboard intelligently combines results from all three models:
- YOLO: Object detection (doors, windows, furniture)
- Detectron2: Segmentation masks (walls, floors)
- Floorplan: Text labels (room names) + contours

## Troubleshooting

### Model Not Available

If you see:
```
⚠️ Floorplan Analyzer not available
```

Install the required packages:
```bash
pip install easyocr rapidfuzz
```

### Low Detection Quality

- Adjust `min_conf` parameter (try 0.3 for more detections, 0.6 for higher quality)
- Ensure image has clear, readable text
- Works best with high-resolution floor plans

### Memory Issues

EasyOCR requires significant memory. If you encounter issues:
- Set `gpu=False` in `ocr_utils.py` (already set by default)
- Close other applications
- Process one image at a time

## File Structure

```
ml/
├── floorplan_analyzer/           # Original implementation
│   ├── main.py                   # Standalone CLI tool
│   ├── ocr_utils.py             # EasyOCR wrapper
│   ├── line_utils.py            # Contour detection
│   ├── fuzzy_wuzzy.py           # Fuzzy matching
│   └── export_utils.py          # PTH/JSON export
├── floorplan_analyzer_wrapper.py # FastAPI integration wrapper
└── detectron2_inference.py       # Other models

server/
└── main.py                       # FastAPI endpoints with floorplan support
```

## Next Steps

1. Fine-tune OCR confidence thresholds for your use case
2. Customize `KNOWN_LABELS` in `fuzzy_wuzzy.py` for domain-specific terms
3. Adjust contour detection parameters in `line_utils.py` for better room boundary detection
4. Integrate scale measurements with the scale drawing tool in the dashboard

## Credits

- **EasyOCR**: Text detection engine
- **RapidFuzz**: Fast fuzzy string matching
- **OpenCV**: Image processing and contour detection

