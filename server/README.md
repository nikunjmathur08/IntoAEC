# IntoAEC Multi-Model FastAPI Server

A FastAPI server that provides both YOLO and Detectron2-based architectural drawing analysis for the IntoAEC application.

## Features

- **Multi-Model Support**: Choose between YOLO (object detection) and Detectron2 (instance segmentation)
- **File Upload**: Accept image uploads (PNG, JPG, JPEG)
- **YOLO Analysis**: Fast object detection with bounding boxes
- **Detectron2 Analysis**: Advanced instance segmentation with masks
- **Batch Processing**: Analyze multiple images at once with either model
- **CORS Support**: Ready for frontend integration
- **Base64 Results**: Returns processed images as base64 strings

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Detectron2 (Optional)**
   ```bash
   ./install_detectron2.sh
   ```

3. **Verify Model Paths**
   - YOLO model: `../ml/demoprpoj/runs/detect/train2/weights/best.pt`
   - Detectron2 model: `../ml/demoprpoj/output/model_final.pth`

3. **Run Server**
   ```bash
   python main.py
   ```
   
   Server will start on `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/` - Server health check

### Model Info
- **GET** `/model/info` - Get loaded model information

### Single Image Analysis
- **POST** `/analyze?model_type=yolo` - Analyze with YOLO
- **POST** `/analyze?model_type=detectron2` - Analyze with Detectron2
  - Upload: `multipart/form-data` with `file` field
  - Returns: JSON with detections and result image

### Batch Analysis
- **POST** `/analyze/batch?model_type=yolo` - Batch analyze with YOLO
- **POST** `/analyze/batch?model_type=detectron2` - Batch analyze with Detectron2
  - Upload: `multipart/form-data` with multiple `files`
  - Returns: JSON with results for each image

## Response Format

```json
{
  "success": true,
  "filename": "blueprint.png",
  "analysis_results": {
    "detections": [
      {
        "class_id": 0,
        "class_name": "door",
        "confidence": 0.8524,
        "bbox": {
          "x1": 100,
          "y1": 150,
          "x2": 200,
          "y2": 250,
          "width": 100,
          "height": 100
        }
      }
    ],
    "total_detections": 1,
    "image_dimensions": {
      "width": 1024,
      "height": 768
    }
  },
  "result_image": "base64_encoded_image_with_boxes",
  "message": "Successfully analyzed blueprint.png. Found 1 detections."
}
```

## Development

The server automatically reloads on code changes when run with `python main.py`.

## Frontend Integration

The server is configured to accept requests from:
- `http://localhost:3000` (Next.js dev server)
- `http://127.0.0.1:3000`
