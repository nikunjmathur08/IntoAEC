# IntoAEC - Comprehensive Knowledge Transfer Document

**Version:** 2.0.0  
**Last Updated:** October 22, 2025  
**Document Purpose:** Complete technical handover guide for future developers

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Component Deep Dive](#4-component-deep-dive)
5. [Data Flow & Integration](#5-data-flow--integration)
6. [Machine Learning Models](#6-machine-learning-models)
7. [Security Implementation](#7-security-implementation)
8. [Deployment Guide](#8-deployment-guide)
9. [Development Workflow](#9-development-workflow)
10. [API Reference](#10-api-reference)
11. [Troubleshooting Guide](#11-troubleshooting-guide)
12. [Maintenance & Operations](#12-maintenance--operations)

---

## 1. Executive Summary

### 1.1 What is IntoAEC?

IntoAEC is an AI-powered platform designed for the Architecture, Engineering, and Construction (AEC) industry. It analyzes architectural drawings, floor plans, and blueprints using advanced computer vision models to automatically detect rooms, walls, doors, windows, furniture, and other architectural elements.

**Core Capabilities:**
- Multi-model AI analysis (YOLO, Detectron2, Floorplan Analyzer, Window Detector)
- Automatic room detection and labeling
- Intelligent detection merging with IoU-based deduplication
- Cost estimation based on detected elements
- Real-time analysis with visual feedback
- Enterprise-grade security (JWT auth, rate limiting, file validation)

### 1.2 Business Value

- **Time Savings:** Automates manual floor plan analysis (80% faster)
- **Accuracy:** Multi-model consensus improves detection accuracy
- **Cost Estimation:** Instant material and labor cost calculations
- **Scalability:** Batch processing for multiple floor plans
- **Integration Ready:** RESTful API for easy integration

### 1.3 Project Status

- **Current Version:** 2.0.0
- **Production Ready:** Yes (with security features enabled)
- **Active Development:** Ongoing
- **Last Major Update:** Security implementation (Oct 2025)

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER (Port 3000)                    │
│  Next.js 15 + React 19 + TypeScript + Tailwind CSS              │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐        │
│  │  HomePage    │ │  Dashboard   │ │ Cost Estimation │        │
│  └──────────────┘ └──────────────┘ └─────────────────┘        │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/REST API
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND LAYER (Port 8000)                     │
│  FastAPI + Uvicorn                                               │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────┐       │
│  │ Auth Layer  │ │  Rate Limit  │ │ File Validation   │       │
│  │ (JWT/Bcrypt)│ │  (SlowAPI)   │ │ (Python-Magic)    │       │
│  └─────────────┘ └──────────────┘ └───────────────────┘       │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Model Inference
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ML LAYER (In-Memory)                          │
│  ┌────────────┐ ┌──────────────┐ ┌─────────────────┐          │
│  │  YOLO v8   │ │  Detectron2  │ │   Floorplan     │          │
│  │  Object    │ │  Instance    │ │   Analyzer      │          │
│  │  Detection │ │  Segmentation│ │   (OCR)         │          │
│  └────────────┘ └──────────────┘ └─────────────────┘          │
│          └──────────────┬────────────────┘                      │
│                         ▼                                        │
│              ┌──────────────────────┐                           │
│              │  Detection Merger    │                           │
│              │  (IoU-based NMS)     │                           │
│              └──────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Directory Structure

```
IntoAEC/
├── client/                         # Frontend Application
│   ├── app/                        # Next.js App Router
│   │   ├── page.tsx               # Homepage
│   │   ├── layout.tsx             # Root layout
│   │   ├── globals.css            # Global styles
│   │   ├── dashboard/
│   │   │   └── page.tsx           # Dashboard page
│   │   └── cost-estimation/
│   │       └── page.tsx           # Cost estimation page
│   ├── components/                 # React Components
│   │   ├── Navbar.tsx
│   │   ├── HeroSection.tsx
│   │   ├── FeaturesGrid.tsx
│   │   ├── UploadSection.tsx
│   │   ├── Dashboard.tsx
│   │   ├── LoginForm.tsx
│   │   ├── AuthProvider.tsx
│   │   └── CostEstimation/
│   │       ├── EstimationHeader.tsx
│   │       ├── EstimationTable.tsx
│   │       ├── EstimationTableRow.tsx
│   │       ├── TotalCostCard.tsx
│   │       └── BackgroundDecorations.tsx
│   ├── lib/                        # Utility Functions
│   │   ├── estimationData.ts      # Cost estimation data
│   │   ├── estimationUtils.ts     # Calculation utilities
│   │   ├── fileUtils.ts           # File handling
│   │   ├── secureStorage.ts       # Encrypted localStorage
│   │   └── classColors.ts         # Color mapping for classes
│   ├── package.json               # Node dependencies
│   ├── tsconfig.json              # TypeScript config
│   ├── next.config.ts             # Next.js config
│   └── Dockerfile                 # Frontend container
│
├── server/                         # Backend Application
│   ├── main.py                    # Main FastAPI app (unsecured)
│   ├── main_secure.py             # Secure FastAPI app (JWT auth)
│   ├── auth.py                    # Authentication module
│   ├── security.py                # Security utilities
│   ├── models.py                  # Pydantic models
│   ├── requirements.txt           # Python dependencies
│   ├── start.sh                   # Server startup script
│   ├── install_detectron2.sh      # Detectron2 installer
│   ├── temp/                      # Temporary file storage
│   └── Dockerfile                 # Backend container
│
├── ml/                             # Machine Learning Components
│   ├── detectron2_inference.py    # Detectron2 wrapper
│   ├── detection_merger.py        # Multi-model merger
│   ├── floorplan_analyzer_wrapper.py  # Floorplan analyzer
│   ├── window_detector.py         # Window detection (CV)
│   ├── floorplan_analyzer/        # Floorplan analyzer module
│   │   ├── main.py
│   │   ├── ocr_utils.py           # EasyOCR wrapper
│   │   ├── line_utils.py          # Contour detection
│   │   ├── fuzzy_wuzzy.py         # Label correction
│   │   ├── export_utils.py        # Export utilities
│   │   └── requirements.txt
│   └── demoprpoj/                 # Model files & datasets
│       ├── yolov8n.pt            # YOLO Nano
│       ├── yolov8l.pt            # YOLO Large
│       ├── yolov8s-seg.pt        # YOLO Segmentation
│       ├── deeplabv3_floorplan.pth
│       ├── runs/                  # Training runs
│       └── dataset/               # Training datasets
│
├── docker-compose.yml              # Production Docker config
├── docker-compose.dev.yml          # Development Docker config
├── start.sh                        # Application startup
├── stop.sh                         # Application shutdown
├── deploy_secure.sh                # Secure deployment
├── .gitignore
├── .gitattributes                  # Git LFS config
├── .dockerignore
│
├── README.md                       # Main documentation
├── DOCKER_SETUP.md                 # Docker guide
├── SECURITY_IMPLEMENTATION.md      # Security docs
├── FLOORPLAN_ANALYZER_SETUP.md     # Floorplan analyzer
├── COLOR_REFERENCE.md              # Color scheme
└── KNOWLEDGE_TRANSFER.md           # This document
```

---

## 3. Technology Stack

### 3.1 Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 15.3.4 | React framework with App Router |
| **React** | 19.0.0 | UI library |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 4.x | Styling framework |
| **Lucide React** | 0.525.0 | Icon library |
| **CryptoJS** | 4.2.0 | Client-side encryption |
| **JS-Cookie** | 3.0.5 | Cookie management |

**Why These Choices:**
- **Next.js 15:** Server-side rendering, App Router, excellent DX
- **React 19:** Latest features, improved performance
- **Tailwind:** Rapid UI development, responsive by default
- **CryptoJS:** Secure data storage in localStorage

### 3.2 Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.104.1 | High-performance async API framework |
| **Uvicorn** | 0.24.0 | ASGI server |
| **PyTorch** | ≥1.8.0 | ML framework |
| **Ultralytics YOLO** | ≥8.0.0 | Object detection |
| **Detectron2** | Latest | Instance segmentation |
| **OpenCV** | ≥4.8.0 | Image processing |
| **EasyOCR** | Latest | Text detection |
| **Python-JOSE** | 3.3.0 | JWT tokens |
| **Passlib** | 1.7.4 | Password hashing |
| **SlowAPI** | 0.1.9 | Rate limiting |
| **Python-Magic** | 0.4.27 | File type detection |

**Why These Choices:**
- **FastAPI:** Async support, automatic OpenAPI docs, Pydantic validation
- **PyTorch:** Industry standard for ML, good GPU support
- **YOLO:** Fast object detection (50ms inference)
- **Detectron2:** High-accuracy segmentation
- **SlowAPI:** Simple, effective rate limiting

### 3.3 DevOps Stack

| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |
| **Git LFS** | Large model file management |
| **Bash Scripts** | Automation (start.sh, stop.sh) |

---

## 4. Component Deep Dive

### 4.1 Frontend Components

#### 4.1.1 App Router Structure

**File:** `client/app/page.tsx`  
**Purpose:** Homepage with hero, features, and upload section

```typescript
// Main landing page composition
export default function Page() {
  return (
    <main className="bg-gradient-to-br from-white to-gray-50">
      <Navbar />           // Navigation bar
      <HeroSection />      // Hero with CTA
      <FeaturesGrid />     // Feature showcase
      <UploadSection />    // File upload interface
    </main>
  );
}
```

**Key Features:**
- Responsive design (mobile-first)
- Server-side rendering for SEO
- Lazy loading for images

#### 4.1.2 Dashboard Component

**File:** `client/components/Dashboard.tsx`  
**Purpose:** Analysis results visualization

**Features:**
- Display detection results from all models
- Show annotated images
- Class-based filtering
- Export functionality

**State Management:**
- Uses React hooks (useState, useEffect)
- Local storage for persistence
- No Redux (keeping it simple)

#### 4.1.3 Authentication

**File:** `client/components/LoginForm.tsx`  
**Purpose:** User login/registration

**Flow:**
1. User enters credentials
2. POST request to `/auth/login`
3. Receive JWT token
4. Store encrypted in localStorage
5. Include token in all API requests

**Security Features:**
- Encrypted storage (CryptoJS AES-256)
- Automatic token refresh
- Session expiration (30 minutes)

#### 4.1.4 Secure Storage

**File:** `client/lib/secureStorage.ts`  
**Purpose:** Encrypted localStorage wrapper

```typescript
// Encryption with AES-256
export function encryptData(data: string): string {
  return CryptoJS.AES.encrypt(data, SECRET_KEY).toString();
}

// Decryption with error handling
export function decryptData(encrypted: string): string {
  const bytes = CryptoJS.AES.decrypt(encrypted, SECRET_KEY);
  return bytes.toString(CryptoJS.enc.Utf8);
}
```

**Key Features:**
- AES-256 encryption
- Checksum validation
- Session expiration (24 hours)
- Automatic cleanup of expired data

### 4.2 Backend Components

#### 4.2.1 Main API Server

**File:** `server/main.py` (unsecured) or `server/main_secure.py` (secured)

**Key Endpoints:**

```python
# Health check (public)
GET /health

# Model information (requires auth)
GET /model/info

# Single image analysis (requires auth, rate limited)
POST /analyze?model_type=yolo&keep_classes=...

# Batch analysis (requires auth)
POST /analyze/batch

# Authentication
POST /auth/login
POST /auth/register
```

**Features:**
- Async request handling
- Global model caching (loaded once)
- Automatic file cleanup
- Comprehensive error handling

#### 4.2.2 Authentication Module

**File:** `server/auth.py`

**Key Functions:**

```python
# Password hashing with bcrypt
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT token creation
def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# Token verification
def verify_token(token: str) -> Optional[TokenData]:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return TokenData(username=payload.get("sub"))
```

**Security Features:**
- Bcrypt password hashing (cost factor: 12)
- JWT with HS256 algorithm
- Token expiration (30 minutes)
- Refresh token support (7 days)
- In-memory user database (replace with DB in production)

#### 4.2.3 Security Module

**File:** `server/security.py`

**Validation Pipeline:**

```python
1. Sanitize filename (remove path traversal)
2. Validate file extension (.png, .jpg, .jpeg, .pdf, .dwg)
3. Validate file size (max 10MB)
4. Validate MIME type (python-magic)
5. Scan for malicious content (signatures, null bytes)
6. File-type specific validation (PIL, OpenCV)
```

**Blocked Patterns:**
- `<script>`, `<iframe>`, `<object>` tags
- `javascript:`, `vbscript:` protocols
- Null bytes in header
- Invalid image formats
- PDF with JavaScript

---

## 5. Data Flow & Integration

### 5.1 Complete Analysis Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER UPLOADS IMAGE                        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: UploadSection.tsx                                      │
│  1. File validation (client-side)                                │
│  2. Create FormData                                              │
│  3. Add JWT token to Authorization header                        │
│  4. POST to /analyze endpoint                                    │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP Request
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND: Security Middleware                                     │
│  1. Verify JWT token                                             │
│  2. Check rate limit (5 requests/minute)                         │
│  3. Add security headers                                         │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND: /analyze Endpoint                                       │
│  1. Comprehensive file validation                                │
│  2. Create secure temporary file                                 │
│  3. Route to selected model(s)                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
         ┌────────┴────────┬────────────┐
         ▼                 ▼            ▼
┌────────────────┐ ┌──────────────┐ ┌──────────────┐
│  YOLO Model    │ │ Detectron2   │ │ Floorplan    │
│  (~50ms)       │ │ (~200ms)     │ │ Analyzer     │
│                │ │              │ │ (~500ms)     │
└────────┬───────┘ └──────┬───────┘ └──────┬───────┘
         │                 │                │
         └────────┬────────┴────────────────┘
                  │ Raw Detections
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ Detection Merger (detection_merger.py)                           │
│  1. Normalize class names                                        │
│  2. Calculate IoU for all pairs                                  │
│  3. Merge overlapping detections (IoU > threshold)               │
│  4. Average confidences from multiple models                     │
│  5. Track source models for each detection                       │
└─────────────────┬───────────────────────────────────────────────┘
                  │ Merged Detections
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ Visualization (create_combined_visualization)                    │
│  1. Draw bounding boxes with class-based colors                  │
│  2. Add labels with confidence scores                            │
│  3. Show model source tags                                       │
│  4. Generate legend                                              │
│  5. Encode image to base64                                       │
└─────────────────┬───────────────────────────────────────────────┘
                  │ JSON Response
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: Dashboard Display                                      │
│  1. Decode base64 image                                          │
│  2. Parse detection results                                      │
│  3. Display annotated image                                      │
│  4. Show statistics and class counts                             │
│  5. Enable filtering and export                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Model Integration Details

#### 5.2.1 YOLO Integration

**File:** Integrated in `server/main.py`

**Flow:**
```python
# Load model (once, cached globally)
yolo_model = YOLO(MODEL_PATH)

# Run inference
results = yolo_model(image_path)

# Process results
for box in results[0].boxes:
    x1, y1, x2, y2 = box.xyxy[0].tolist()
    cls = int(box.cls[0])
    conf = float(box.conf[0])
    # Store detection...
```

**Model Files:**
- `ml/demoprpoj/runs/detect/train2/weights/best.pt` (custom trained)
- `ml/demoprpoj/yolov8n.pt` (nano - fastest)
- `ml/demoprpoj/yolov8l.pt` (large - most accurate)

**Classes Detected:**
- Architectural: wall, door, window, room, stairs
- Room Types: bathroom, kitchen, bedroom, living_room

#### 5.2.2 Detectron2 Integration

**File:** `ml/detectron2_inference.py`

**Flow:**
```python
# Initialize with config
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.WEIGHTS = "path/to/model_final.pth"
predictor = DefaultPredictor(cfg)

# Run inference
outputs = predictor(image)
instances = outputs["instances"].to("cpu")

# Apply class filtering (optional)
if keep_classes:
    instances = instances[matching_indices]

# Apply polygon fitting (optional)
if enable_polygon_fitting:
    polygons, bboxes = fit_polygon(mask)
```

**Features:**
- Instance segmentation masks
- Polygon fitting for room boundaries
- Class filtering capability
- Overlap resolution

**Model File:**
- `ml/demoprpoj/output/model_final.pth` (custom trained)
- Fallback: Pretrained COCO Mask R-CNN

#### 5.2.3 Floorplan Analyzer Integration

**File:** `ml/floorplan_analyzer_wrapper.py`

**Flow:**
```python
# Perform OCR
labels = perform_ocr(image, min_conf=0.4)

# Correct labels with fuzzy matching
labels = correct_labels(labels)

# Detect contours (room boundaries)
contours = detect_contours(image)

# Auto-estimate scale
scale = auto_estimate_scale(labels)

# Calculate areas
areas = [calculate_area(cnt, scale) for cnt in contours]
```

**Components:**
- **EasyOCR:** Multi-language text detection
- **Fuzzy Matching:** Label correction (rapidfuzz)
- **Contour Detection:** Room boundary identification
- **Scale Estimation:** Auto-detect from annotations

**Known Labels (fuzzy_wuzzy.py):**
```python
KNOWN_LABELS = [
    "Living Room", "Bedroom", "Bathroom", "Kitchen",
    "Dining Room", "Hallway", "Closet", "Entry",
    "Balcony", "Garage", "Master Bedroom", "Guest Room",
    # ... 20+ more
]
```

#### 5.2.4 Detection Merger

**File:** `ml/detection_merger.py`

**Algorithm:**

```python
def merge_detections(yolo_dets, d2_dets, fp_dets, iou_threshold=0.3):
    # 1. Add source information
    all_dets = []
    for det in yolo_dets:
        det['source'] = 'yolo'
        all_dets.append(det)
    # ... same for d2 and fp
    
    # 2. Sort by confidence
    all_dets.sort(key=lambda x: x['confidence'], reverse=True)
    
    # 3. Merge overlapping detections
    merged = []
    used = set()
    for i, det1 in enumerate(all_dets):
        if i in used:
            continue
        
        # Find overlapping detections of same class
        for j, det2 in enumerate(all_dets[i+1:], i+1):
            if j in used:
                continue
            
            if are_same_class(det1, det2):
                iou = calculate_iou(det1['bbox'], det2['bbox'])
                if iou > iou_threshold:
                    # Merge: average confidence, record sources
                    det1['sources'].append(det2['source'])
                    det1['confidence'] = mean([...confidences])
                    used.add(j)
        
        merged.append(det1)
    
    return merged
```

**Key Features:**
- IoU-based matching
- Class name normalization
- Confidence averaging
- Source tracking
- Support for 4 models (YOLO, Detectron2, Floorplan, Window Detector)

**Class Normalization:**
```python
# Pattern-based matching
'bedroom 2' → 'bedroom'
'master bedroom' → 'bedroom'
'bathroom' / 'restroom' / 'wc' → 'toilet'
'living room' / 'lounge' → 'living room'
```

---

## 6. Machine Learning Models

### 6.1 Model Comparison

| Model | Type | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| **YOLO v8n** | Object Detection | ~50ms | Good | Fast real-time detection |
| **YOLO v8l** | Object Detection | ~150ms | Excellent | High-accuracy detection |
| **Detectron2** | Instance Segmentation | ~200ms | Excellent | Precise masks & polygons |
| **Floorplan Analyzer** | OCR + CV | ~500ms | Good | Text labels & contours |
| **Window Detector** | Computer Vision | ~100ms | Good | Specialized window detection |
| **Combined** | All Models | ~800ms | Best | Multi-model consensus |

### 6.2 Model Training

#### 6.2.1 YOLO Training

**Dataset:** CubiCasa5K + Custom annotations
- Training images: 1,000+
- Validation images: 200+
- Classes: 9 (wall, door, window, etc.)

**Training Command:**
```bash
yolo train model=yolov8n.pt data=dataset/data.yaml epochs=100 imgsz=640
```

**Trained Model Location:**
- `ml/demoprpoj/runs/detect/train2/weights/best.pt`

**Training Configuration (data.yaml):**
```yaml
train: dataset/train/images
val: dataset/valid/images
nc: 9
names: ['wall', 'door', 'window', 'room', 'stairs', 
        'bathroom', 'kitchen', 'bedroom', 'living_room']
```

#### 6.2.2 Detectron2 Training

**Dataset:** COCO-formatted annotations
- Custom floor plan dataset
- Instance segmentation masks
- Polygon annotations

**Training Script:** (Not included, but follows standard Detectron2 training)
```python
from detectron2.engine import DefaultTrainer
cfg.DATASETS.TRAIN = ("my_dataset_train",)
cfg.SOLVER.MAX_ITER = 10000
trainer = DefaultTrainer(cfg)
trainer.train()
```

**Model Location:**
- `ml/demoprpoj/output/model_final.pth`

### 6.3 Model Inference Optimization

#### 6.3.1 Model Caching

**Implementation:** Global model variables
```python
# Models are loaded once and cached
yolo_model = None
detectron2_model = None
floorplan_analyzer = None

def load_yolo_model():
    global yolo_model
    if yolo_model is None:
        yolo_model = YOLO(MODEL_PATH)
    return yolo_model
```

**Benefits:**
- No reload overhead (3-5 seconds per request)
- Consistent memory usage
- Faster response times

#### 6.3.2 Batch Processing

**Endpoint:** `POST /analyze/batch`

**Features:**
- Process up to 10 images per request
- Parallel model inference (asyncio)
- Shared model instances
- Bulk response format

#### 6.3.3 GPU Acceleration

**Auto-Detection:**
```python
cfg.MODEL.DEVICE = "cuda" if cv2.cuda.getCudaEnabledDeviceCount() > 0 else "cpu"
```

**Performance:**
- CPU: ~800ms per image (combined)
- GPU: ~250ms per image (combined)

---

## 7. Security Implementation

### 7.1 Authentication Flow

```
┌───────────────────────────────────────────────────────────────┐
│ 1. USER REGISTRATION                                           │
│    POST /auth/register                                         │
│    {username, email, password}                                 │
│    → Password hashed with bcrypt (cost=12)                     │
│    → User stored in memory (or DB)                             │
└─────────────────────┬─────────────────────────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────────────────────┐
│ 2. USER LOGIN                                                  │
│    POST /auth/login                                            │
│    {username, password}                                        │
│    → Verify password hash                                      │
│    → Generate JWT token (HS256)                                │
│    → Return: {access_token, expires_in: 1800}                 │
└─────────────────────┬─────────────────────────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────────────────────┐
│ 3. TOKEN STORAGE (CLIENT)                                      │
│    → Encrypt token with AES-256                                │
│    → Store in localStorage                                     │
│    → Set expiration timestamp                                  │
└─────────────────────┬─────────────────────────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────────────────────┐
│ 4. API REQUESTS                                                │
│    → Include: Authorization: Bearer <token>                    │
│    → Server verifies token signature                           │
│    → Check expiration                                          │
│    → Extract user info from payload                            │
└───────────────────────────────────────────────────────────────┘
```

### 7.2 Security Features

#### 7.2.1 Password Security

**Hashing:** Bcrypt with cost factor 12
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(plain_password)
```

**Why Bcrypt:**
- Adaptive (cost factor can increase)
- Salt included automatically
- Slow by design (prevents brute force)

#### 7.2.2 JWT Tokens

**Implementation:**
```python
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

token = jwt.encode(
    {"sub": username, "exp": expire_time},
    SECRET_KEY,
    algorithm=ALGORITHM
)
```

**Token Payload:**
```json
{
  "sub": "user@example.com",
  "user_id": "abc123",
  "exp": 1698765432
}
```

#### 7.2.3 Rate Limiting

**Implementation:** SlowAPI

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("5/minute")
async def analyze_image(...):
    # Only 5 requests per minute per IP
```

**Limits:**
- `/analyze`: 5 requests/minute
- `/model/info`: 10 requests/minute
- `/health`: Unlimited

#### 7.2.4 File Validation

**Multi-Layer Validation:**

```python
def comprehensive_file_validation(file, temp_path):
    # Layer 1: Filename sanitization
    sanitized = sanitize_filename(file.filename)
    
    # Layer 2: Extension check
    allowed = {'.png', '.jpg', '.jpeg', '.pdf', '.dwg'}
    if ext not in allowed:
        return False, "Invalid extension"
    
    # Layer 3: File size (max 10MB)
    if file.size > 10 * 1024 * 1024:
        return False, "File too large"
    
    # Layer 4: MIME type (python-magic)
    detected_mime = magic.from_file(temp_path, mime=True)
    if detected_mime not in ALLOWED_MIME_TYPES:
        return False, "Invalid MIME type"
    
    # Layer 5: Malicious content scan
    if scan_for_malicious_patterns(file_content):
        return False, "Malicious content detected"
    
    # Layer 6: File-specific validation (PIL, OpenCV)
    if not validate_image_integrity(file_content):
        return False, "Corrupted image"
    
    return True, "OK"
```

#### 7.2.5 Security Headers

**Applied to all responses:**
```python
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-XSS-Protection"] = "1; mode=block"
response.headers["Strict-Transport-Security"] = "max-age=31536000"
response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
response.headers["Content-Security-Policy"] = "default-src 'self'"
```

#### 7.2.6 CORS Configuration

**Restricted Origins:**
```python
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # NO wildcards!
    allow_credentials=True,
    allow_methods=["GET", "POST"],   # Limited methods
    allow_headers=["Authorization", "Content-Type"],
)
```

### 7.3 Security Best Practices

#### Production Deployment Checklist:

- [ ] Change `SECRET_KEY` to strong random value (32+ bytes)
- [ ] Set `ENVIRONMENT=production`
- [ ] Use HTTPS (TLS 1.2+)
- [ ] Enable firewall rules (allow only 80/443)
- [ ] Set up proper logging
- [ ] Replace in-memory user DB with persistent storage
- [ ] Enable database connection encryption
- [ ] Set up automated backups
- [ ] Configure monitoring/alerting
- [ ] Regular security audits
- [ ] Update dependencies monthly

---

## 8. Deployment Guide

### 8.1 Quick Start (Docker)

**Prerequisites:**
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 10GB free disk space

**Commands:**

```bash
# Clone repository
git clone <repo-url>
cd IntoAEC

# Start application
./start.sh --build

# Access applications
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs

# Stop application
./stop.sh
```

### 8.2 Docker Configuration

#### 8.2.1 Docker Compose (Production)

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  frontend:
    build: ./client
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - ENVIRONMENT=production
    volumes:
      - ./ml:/app/ml:ro           # Read-only ML models
      - ./server/temp:/app/temp   # Temporary files
      - ./server/uploads:/app/uploads
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### 8.2.2 Frontend Dockerfile

**File:** `client/Dockerfile`

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Build Next.js app
RUN npm run build

# Expose port
EXPOSE 3000

# Start server
CMD ["npm", "start"]
```

#### 8.2.3 Backend Dockerfile

**File:** `server/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.3 Manual Installation (Development)

#### 8.3.1 Backend Setup

```bash
# Navigate to server directory
cd server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Detectron2 (optional)
./install_detectron2.sh

# Install Floorplan Analyzer dependencies
pip install easyocr rapidfuzz

# Set environment variables
export PYTHONPATH=$(pwd)/..
export SECRET_KEY=your-secret-key

# Start server
python main.py
```

#### 8.3.2 Frontend Setup

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Development mode (with hot reload)
npm run dev

# Production build
npm run build
npm start
```

### 8.4 Environment Variables

#### Backend (.env)

```bash
# Security
SECRET_KEY=your-very-secure-secret-key-at-least-32-characters
ADMIN_PASSWORD=secure-admin-password

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Application
ENVIRONMENT=production
PYTHONPATH=/app

# Rate Limiting
RATE_LIMIT=5/minute

# File Upload
MAX_FILE_SIZE=10485760  # 10MB in bytes
```

#### Frontend (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Build Configuration
NODE_ENV=production
```

### 8.5 Production Deployment

#### 8.5.1 Secure Deployment Script

**File:** `deploy_secure.sh`

```bash
#!/bin/bash
# Automated secure deployment

# Generate secure secrets
export SECRET_KEY=$(openssl rand -base64 32)

# Set production environment
export ENVIRONMENT=production

# Set allowed origins
export ALLOWED_ORIGINS=https://yourdomain.com

# Build and start with Docker Compose
docker-compose build --no-cache
docker-compose up -d

echo "✅ Application deployed securely!"
```

#### 8.5.2 Production Checklist

**Infrastructure:**
- [ ] Use reverse proxy (Nginx/Traefik)
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Set up firewall (UFW/iptables)
- [ ] Configure log rotation
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Enable automated backups

**Security:**
- [ ] Change all default passwords
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Configure security headers
- [ ] Set up fail2ban
- [ ] Regular security audits

**Performance:**
- [ ] Enable CDN for static assets
- [ ] Configure caching headers
- [ ] Set up load balancing (if needed)
- [ ] Monitor resource usage
- [ ] Optimize Docker images

---

## 9. Development Workflow

### 9.1 Setting Up Development Environment

```bash
# 1. Clone repository
git clone <repo-url>
cd IntoAEC

# 2. Install Git LFS (for model files)
git lfs install
git lfs pull

# 3. Set up backend
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

# 4. Set up frontend (in new terminal)
cd client
npm install
npm run dev

# 5. Access development servers
# Frontend: http://localhost:3000 (hot reload enabled)
# Backend:  http://localhost:8000 (auto-reload enabled)
```

### 9.2 Code Organization

#### Frontend Structure

```
client/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Route pages
│   ├── layout.tsx         # Layout components
│   └── */page.tsx         # Nested routes
├── components/            # React components
│   ├── Navbar.tsx
│   └── */                 # Component folders
├── lib/                   # Utilities & helpers
│   ├── *.ts              # Utility functions
│   └── *.tsx             # Utility components
└── public/               # Static assets
```

#### Backend Structure

```
server/
├── main.py                # Main FastAPI app
├── main_secure.py         # Secure version
├── auth.py                # Authentication
├── security.py            # Security utilities
├── models.py              # Pydantic models
└── temp/                  # Temporary files
```

#### ML Structure

```
ml/
├── detectron2_inference.py      # Detectron2 wrapper
├── detection_merger.py          # Multi-model merger
├── floorplan_analyzer_wrapper.py
├── floorplan_analyzer/          # OCR module
│   ├── main.py
│   ├── ocr_utils.py
│   ├── line_utils.py
│   └── fuzzy_wuzzy.py
└── demoprpoj/                   # Models & datasets
```

### 9.3 Adding New Features

#### Example: Adding a New ML Model

```python
# 1. Create model wrapper (ml/new_model.py)
class NewModelPredictor:
    def __init__(self):
        self.model = load_model()
    
    def predict(self, image_path):
        # Run inference
        return results
    
    def get_detection_summary(self, results):
        # Format results
        return summary

# 2. Import in server/main.py
from new_model import NewModelPredictor

# 3. Add endpoint
@app.post("/analyze")
async def analyze_image(model_type: str = Query(...)):
    if model_type == "new_model":
        model = load_new_model()
        results = model.predict(temp_image_path)
        # ... process results

# 4. Update frontend (client/components/UploadSection.tsx)
<select name="model_type">
  <option value="yolo">YOLO</option>
  <option value="detectron2">Detectron2</option>
  <option value="new_model">New Model</option>
</select>
```

### 9.4 Testing

#### Backend Testing

```bash
# Run manual tests
cd server
python test_class_filtering.py
python security_test.py

# Test endpoints with curl
curl http://localhost:8000/health
curl -X POST http://localhost:8000/analyze \
  -H "Authorization: Bearer <token>" \
  -F "file=@test-image.png" \
  -F "model_type=yolo"
```

#### Frontend Testing

```bash
# Run Next.js dev server
npm run dev

# Lint code
npm run lint

# Build for production (checks for errors)
npm run build
```

### 9.5 Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 3. Push to remote
git push origin feature/new-feature

# 4. Create pull request
# 5. Review and merge

# Commit Convention (Conventional Commits)
# feat: New feature
# fix: Bug fix
# docs: Documentation changes
# style: Code style changes
# refactor: Code refactoring
# test: Adding tests
# chore: Maintenance tasks
```

### 9.6 Debugging

#### Backend Debugging

```python
# Enable debug logging in main.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"🔍 DEBUG: {variable_name}")

# Check FastAPI automatic docs
# http://localhost:8000/docs
```

#### Frontend Debugging

```typescript
// Console logging
console.log("DEBUG:", data);

// React DevTools (Browser Extension)
// Check component state and props

// Network tab
// Inspect API requests/responses
```

#### Docker Debugging

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute commands in container
docker-compose exec backend bash
docker-compose exec frontend sh

# Inspect container
docker inspect intoaec_backend_1

# Check resource usage
docker stats
```

---

## 10. API Reference

### 10.1 Authentication Endpoints

#### POST /auth/register

**Description:** Register a new user

**Request:**
```json
{
  "username": "user@example.com",
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "message": "User created successfully",
  "username": "user@example.com"
}
```

**Errors:**
- 400: Invalid input or user already exists

---

#### POST /auth/login

**Description:** Authenticate user and receive JWT token

**Request:**
```json
{
  "username": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:**
- 401: Incorrect username or password

---

### 10.2 Analysis Endpoints

#### GET /model/info

**Description:** Get information about available models

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response (200):**
```json
{
  "available_models": ["yolo", "detectron2", "floorplan"],
  "yolo": {
    "available": true,
    "model_type": "YOLOv8",
    "classes": {...}
  },
  "detectron2": {
    "available": true,
    "model_type": "Mask R-CNN",
    "classes": [...]
  },
  "floorplan": {
    "available": true,
    "model_type": "OCR + Contour Detection"
  }
}
```

**Rate Limit:** 10 requests/minute

---

#### POST /analyze

**Description:** Analyze a single floor plan image

**Headers:**
- `Authorization: Bearer <token>` (required)
- `Content-Type: multipart/form-data`

**Form Data:**
- `file`: Image file (required)

**Query Parameters:**
- `model_type`: `yolo` | `detectron2` | `floorplan` | `combined` (default: `yolo`)
- `keep_classes`: Comma-separated class names to filter (optional)
- `enable_polygon_fitting`: `true` | `false` (default: `false`)
- `min_conf`: OCR confidence threshold (default: `0.4`)
- `iou_threshold`: IoU threshold for merging (default: `0.3`)

**Example:**
```bash
curl -X POST "http://localhost:8000/analyze?model_type=combined&iou_threshold=0.3" \
  -H "Authorization: Bearer <token>" \
  -F "file=@floorplan.png"
```

**Response (200):**
```json
{
  "success": true,
  "filename": "floorplan.png",
  "model_used": "combined",
  "analysis_results": {
    "detections": [
      {
        "class_name": "Living Room",
        "confidence": 0.95,
        "bbox": {
          "x1": 100,
          "y1": 150,
          "x2": 400,
          "y2": 500,
          "width": 300,
          "height": 350
        },
        "sources": ["yolo", "detectron2", "floorplan"],
        "num_models_detected": 3
      }
    ],
    "total_detections": 15,
    "detections_by_class": {
      "Living Room": 1,
      "Bedroom": 3,
      "Bathroom": 2,
      "Door": 5,
      "Window": 4
    },
    "model_contributions": {
      "yolo": 12,
      "detectron2": 10,
      "floorplan": 8
    }
  },
  "result_image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "message": "Successfully analyzed floorplan.png",
  "processing_time": 0.85
}
```

**Rate Limit:** 5 requests/minute

**Errors:**
- 400: Invalid file or parameters
- 401: Unauthorized (invalid or missing token)
- 429: Rate limit exceeded
- 500: Internal server error

---

#### POST /analyze/batch

**Description:** Analyze multiple images in batch

**Headers:**
- `Authorization: Bearer <token>` (required)
- `Content-Type: multipart/form-data`

**Form Data:**
- `files`: Multiple image files (max 10)

**Query Parameters:**
- `model_type`: `yolo` | `detectron2` (required)
- `keep_classes`: Class filter (optional)
- `enable_polygon_fitting`: Boolean (optional)

**Response (200):**
```json
{
  "success": true,
  "total_files": 3,
  "results": [
    {
      "filename": "plan1.png",
      "success": true,
      "analysis_results": {...},
      "result_image": "base64..."
    },
    {
      "filename": "plan2.png",
      "success": false,
      "error": "Invalid image format"
    }
  ]
}
```

---

### 10.3 Utility Endpoints

#### GET /health

**Description:** Health check (public endpoint)

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-22T12:34:56.789Z"
}
```

---

#### GET /

**Description:** Root endpoint

**Response (200):**
```json
{
  "message": "IntoAEC YOLO Detection API is running!",
  "status": "healthy"
}
```

---

### 10.4 Response Formats

#### Success Response

```json
{
  "success": true,
  "filename": "image.png",
  "model_used": "yolo",
  "analysis_results": { /* detection data */ },
  "result_image": "base64_encoded_image",
  "message": "Analysis complete",
  "processing_time": 0.5
}
```

#### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## 11. Troubleshooting Guide

### 11.1 Common Issues & Solutions

#### Issue: Port Already in Use

**Symptoms:**
- `Error: Address already in use`
- Cannot start frontend/backend

**Solution:**
```bash
# Check what's using the port
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# Kill the process
kill -9 <PID>

# Or use different ports in docker-compose.yml
ports:
  - "3001:3000"  # Map to different host port
```

---

#### Issue: Docker Out of Memory

**Symptoms:**
- `docker: Error response from daemon: OCI runtime create failed`
- Models fail to load

**Solution:**
```bash
# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory: 8GB+

# Or use CPU-only mode (slower)
# In detectron2_inference.py:
cfg.MODEL.DEVICE = "cpu"
```

---

#### Issue: Model File Not Found

**Symptoms:**
- `FileNotFoundError: YOLO model file not found`

**Solution:**
```bash
# Pull LFS files
git lfs install
git lfs pull

# Verify model files exist
ls -lh ml/demoprpoj/runs/detect/train2/weights/best.pt

# If missing, re-download or use pretrained models
```

---

#### Issue: Authentication Fails

**Symptoms:**
- `401 Unauthorized`
- Token expired

**Solution:**
```bash
# Check if token is valid
curl http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Verify SECRET_KEY is set correctly
echo $SECRET_KEY

# Check token expiration (30 minutes by default)
```

---

#### Issue: File Upload Fails Validation

**Symptoms:**
- `400 File validation failed`

**Solution:**
```bash
# Check file size (max 10MB)
ls -lh image.png

# Verify file type
file image.png

# Ensure MIME type is correct
# Allowed: image/png, image/jpeg, application/pdf

# Remove any embedded scripts or malicious content
```

---

#### Issue: Detectron2 Not Available

**Symptoms:**
- `Detectron2 not available`

**Solution:**
```bash
# Install Detectron2
cd server
./install_detectron2.sh

# Or manually:
pip install 'git+https://github.com/facebookresearch/detectron2.git'

# Verify installation
python -c "import detectron2; print(detectron2.__version__)"
```

---

#### Issue: OCR Not Working (Floorplan Analyzer)

**Symptoms:**
- `Floorplan Analyzer not available`

**Solution:**
```bash
# Install EasyOCR and RapidFuzz
pip install easyocr rapidfuzz

# First run downloads models (~400MB)
# Wait for download to complete

# Check if GPU is used (optional)
# EasyOCR uses GPU by default if available
```

---

#### Issue: Docker Build Fails

**Symptoms:**
- Build errors during `docker-compose build`

**Solution:**
```bash
# Clean build (no cache)
docker-compose build --no-cache

# Check Docker logs
docker-compose logs backend

# Verify Dockerfile syntax
# Check base image availability

# Increase Docker build memory
# Docker Desktop → Settings → Resources
```

---

#### Issue: Frontend Not Loading

**Symptoms:**
- Blank page
- `ERR_CONNECTION_REFUSED`

**Solution:**
```bash
# Check if frontend is running
curl http://localhost:3000

# View frontend logs
docker-compose logs frontend

# Verify environment variables
cat client/.env.local

# Rebuild frontend
cd client
npm install
npm run build
npm start
```

---

#### Issue: CORS Errors

**Symptoms:**
- `Access-Control-Allow-Origin` error in browser console

**Solution:**
```python
# Check CORS configuration in server/main.py
ALLOWED_ORIGINS = ["http://localhost:3000"]

# Verify frontend URL matches
# In client/.env.local:
NEXT_PUBLIC_API_URL=http://localhost:8000

# Restart both services after changes
```

---

### 11.2 Debugging Checklist

When debugging issues, follow this checklist:

1. **Check Services Status**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   curl http://localhost:3000
   ```

2. **View Logs**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

3. **Check Resource Usage**
   ```bash
   docker stats
   free -h  # Memory
   df -h    # Disk space
   ```

4. **Verify Environment Variables**
   ```bash
   docker-compose exec backend env
   cat client/.env.local
   ```

5. **Test API Endpoints**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Model info (with auth)
   curl http://localhost:8000/model/info \
     -H "Authorization: Bearer <token>"
   ```

6. **Check File Permissions**
   ```bash
   ls -la server/temp/
   ls -la ml/demoprpoj/
   ```

7. **Restart Services**
   ```bash
   docker-compose restart
   # Or
   docker-compose down && docker-compose up -d
   ```

---

### 11.3 Performance Optimization

#### Slow Analysis (>5 seconds)

**Possible Causes:**
- CPU-only mode (no GPU)
- Large images (>4K resolution)
- Multiple models running simultaneously
- Insufficient memory

**Solutions:**
```bash
# Enable GPU if available
# Check: nvidia-smi

# Resize images before upload
convert input.png -resize 2048x2048 output.png

# Use single model instead of combined
# ?model_type=yolo  (faster)

# Increase system resources
```

---

#### High Memory Usage

**Solutions:**
```bash
# Limit model batch size
# In detectron2_inference.py:
cfg.DATALOADER.NUM_WORKERS = 2

# Clean up temp files regularly
rm server/temp/*

# Monitor memory usage
docker stats
```

---

### 11.4 Logging & Monitoring

#### Enable Debug Logging

**Backend:**
```python
# In server/main.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Frontend:**
```typescript
// In client/lib/api.ts
console.log("API Request:", url, data);
console.log("API Response:", response);
```

#### Log Files

```bash
# Backend logs (if file logging enabled)
tail -f server/server.log

# Docker logs
docker-compose logs -f --tail=100 backend

# System logs
journalctl -u docker -f
```

---

## 12. Maintenance & Operations

### 12.1 Regular Maintenance Tasks

#### Daily

- [ ] Monitor server logs for errors
- [ ] Check disk space (`df -h`)
- [ ] Verify services are running (`docker-compose ps`)

#### Weekly

- [ ] Review rate limit logs
- [ ] Check for failed authentication attempts
- [ ] Clean up old temporary files
- [ ] Review application logs

#### Monthly

- [ ] Update dependencies
  ```bash
  cd server && pip list --outdated
  cd client && npm outdated
  ```
- [ ] Security audit
- [ ] Review and rotate logs
- [ ] Performance optimization review

#### Quarterly

- [ ] Major version updates
- [ ] Security penetration testing
- [ ] Disaster recovery test
- [ ] Documentation review

---

### 12.2 Backup & Recovery

#### What to Backup

1. **User Database** (if persistent storage added)
2. **Uploaded Files** (`server/uploads/`)
3. **Model Files** (`ml/demoprpoj/`)
4. **Configuration Files** (`.env`, `docker-compose.yml`)

#### Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/backups/intoaec/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup uploads
tar -czf "$BACKUP_DIR/uploads.tar.gz" server/uploads/

# Backup ML models (if not in git)
tar -czf "$BACKUP_DIR/models.tar.gz" ml/demoprpoj/*.pt

# Backup config
cp docker-compose.yml "$BACKUP_DIR/"
cp .env "$BACKUP_DIR/"

echo "Backup complete: $BACKUP_DIR"
```

#### Recovery

```bash
# Restore from backup
cd /backups/intoaec/20251022/
tar -xzf uploads.tar.gz -C /path/to/IntoAEC/server/
tar -xzf models.tar.gz -C /path/to/IntoAEC/ml/demoprpoj/

# Restart services
cd /path/to/IntoAEC
docker-compose restart
```

---

### 12.3 Scaling Considerations

#### Horizontal Scaling

**Using Docker Swarm or Kubernetes:**

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Add load balancer (Nginx)
# Configure round-robin or least-connections
```

**Load Balancer Configuration (Nginx):**

```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

#### Vertical Scaling

- Increase Docker container resources
- Use larger instance types (AWS EC2, GCP Compute)
- Add GPU for faster inference

#### Model Optimization

- Use ONNX for faster inference
- Quantize models (INT8)
- Model distillation (smaller models)
- Cache common predictions

---

### 12.4 Monitoring Setup

#### Prometheus + Grafana

**docker-compose.monitoring.yml:**

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

**Metrics to Monitor:**
- Request rate (requests/second)
- Response time (ms)
- Error rate (5xx responses)
- Memory usage (MB)
- CPU usage (%)
- Model inference time (ms)

---

### 12.5 Updating the Application

#### Update Process

```bash
# 1. Backup current state
./backup.sh

# 2. Pull latest changes
git pull origin main
git lfs pull

# 3. Update dependencies
cd server && pip install -r requirements.txt
cd client && npm install

# 4. Rebuild Docker images
docker-compose build --no-cache

# 5. Stop old containers
docker-compose down

# 6. Start new containers
docker-compose up -d

# 7. Verify deployment
curl http://localhost:8000/health
curl http://localhost:3000

# 8. Monitor logs for issues
docker-compose logs -f
```

#### Rollback Plan

```bash
# 1. Stop current containers
docker-compose down

# 2. Checkout previous version
git checkout <previous-commit>
git lfs pull

# 3. Rebuild and start
docker-compose build
docker-compose up -d

# 4. Restore backups if needed
tar -xzf /backups/intoaec/latest/uploads.tar.gz -C server/
```

---

### 12.6 Database Migration (Future)

**When transitioning from in-memory to persistent storage:**

**PostgreSQL Setup:**

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: intoaec
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/intoaec
```

**SQLAlchemy Setup:**

```python
# server/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

---

### 12.7 Security Auditing

#### Regular Security Checks

```bash
# Check for outdated dependencies with known vulnerabilities
cd server && pip-audit
cd client && npm audit

# Scan Docker images for vulnerabilities
docker scan intoaec_backend

# Check SSL/TLS configuration
sslscan yourdomain.com

# Test for common vulnerabilities
nmap -sV --script=vuln localhost
```

#### Security Headers Verification

```bash
# Check security headers
curl -I https://yourdomain.com | grep -E "(X-|Strict|Content-Security)"
```

---

## Appendix A: Useful Commands

### Docker Commands

```bash
# View all containers
docker ps -a

# View logs
docker logs <container_id>

# Execute command in container
docker exec -it <container_id> bash

# Remove all stopped containers
docker container prune

# Remove all unused images
docker image prune -a

# View disk usage
docker system df
```

### Git Commands

```bash
# Check LFS files
git lfs ls-files

# Pull LFS files
git lfs pull

# Track large files
git lfs track "*.pt"
git lfs track "*.pth"

# Check repository size
git count-objects -vH
```

### Curl Commands

```bash
# GET request
curl http://localhost:8000/health

# POST request with JSON
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# POST request with file
curl -X POST http://localhost:8000/analyze \
  -H "Authorization: Bearer <token>" \
  -F "file=@image.png"

# Save response to file
curl http://localhost:8000/model/info > model_info.json
```

---

## Appendix B: Contact & Support

### Key Stakeholders

- **Project Owner:** [Your Name]
- **Technical Lead:** [Your Name]
- **Repository:** [GitHub URL]

### Getting Help

1. **Documentation:** Check README files and this KT document
2. **API Docs:** http://localhost:8000/docs (when server is running)
3. **GitHub Issues:** Report bugs and feature requests
4. **Community:** [Discord/Slack channel if applicable]

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| **AEC** | Architecture, Engineering, and Construction industry |
| **YOLO** | You Only Look Once - object detection algorithm |
| **Detectron2** | Facebook's instance segmentation framework |
| **OCR** | Optical Character Recognition - text extraction from images |
| **IoU** | Intersection over Union - overlap metric for bounding boxes |
| **JWT** | JSON Web Token - authentication token format |
| **NMS** | Non-Maximum Suppression - deduplication algorithm |
| **Mask R-CNN** | Region-based Convolutional Neural Network for segmentation |
| **FastAPI** | Modern Python web framework for APIs |
| **Next.js** | React framework for production |
| **Docker** | Container platform for application deployment |

---

## Appendix D: Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | Oct 2025 | Security implementation, JWT auth, rate limiting |
| 1.5.0 | Sep 2025 | Combined model analysis, detection merger |
| 1.0.0 | Aug 2025 | Initial release with YOLO and Detectron2 |

---

**Document End**

**Last Updated:** October 22, 2025  
**Next Review:** January 2026

---

For questions or clarifications, please contact the development team.

**Good luck with the project! 🚀**

