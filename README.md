# IntoAEC - AI-Powered Architectural Drawing Analysis Platform

<div align="center">

**Transform architectural drawings into actionable insights with AI-powered computer vision**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation) • [API](#-api-reference)

</div>

## Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [ML Models](#-ml-models)
- [Security](#-security)
- [Docker Deployment](#-docker-deployment)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

## Overview

**IntoAEC** is a comprehensive AI-powered platform designed for the Architecture, Engineering and Construction (AEC) industry. It leverages advanced computer vision and machine learning models to automatically analyze architectural drawings, floor plans and blueprints, providing instant insights, measurements and cost estimations.

### Key Capabilities

- **Multi-Model Analysis**: YOLO, Detectron2 and custom Floorplan Analyzer
- **Automatic Measurements**: Extract room dimensions and areas
- **Cost Estimation**: Generate material and labor cost breakdowns
- **Element Detection**: Identify walls, doors, windows, rooms and furniture
- **Smart Insights**: Optimize designs and reduce project costs
- **Enterprise Security**: JWT authentication, rate limiting and secure file handling

## Features

### AI-Powered Analysis
- **YOLO Object Detection**: Fast detection of architectural elements with bounding boxes
- **Detectron2 Instance Segmentation**: Advanced segmentation with precise masks and polygons
- **Floorplan Analyzer**: OCR-based text extraction with contour detection for room identification
- **Combined Analysis**: Merge results from multiple models with intelligent deduplication

### Automatic Measurements
- Extract room dimensions automatically
- Calculate areas and perimeters
- Auto-detect scale from floor plan annotations
- Support for multiple measurement units

### Cost Estimation
- Material quantity calculations
- Labor cost estimations
- Per-room and total project costs
- Customizable pricing models

### Modern Web Interface
- Built with Next.js 15 and React 19
- Responsive design with Tailwind CSS
- Real-time analysis progress tracking
- Interactive visualization of results
- Dashboard with project history

### Enterprise-Grade Security
- JWT-based authentication
- Password hashing with bcrypt
- Rate limiting (5 requests/minute for analysis)
- File validation and sanitization
- CORS protection
- Security headers (HSTS, CSP, etc.)

### Cloud-Ready Deployment
- Docker containerization
- Docker Compose orchestration
- Health checks and auto-restart
- Scalable architecture
- Production-ready configuration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                        │
│  Next.js 15 + React 19 + TypeScript + Tailwind CSS          │
│  (Port 3000)                                                │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend Layer                          │
│  FastAPI + Uvicorn (Port 8000)                              │
│  • Authentication & Authorization                           │
│  • File Upload & Validation                                 │
│  • Rate Limiting & Security                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼─────────────────┐
           ▼               ▼                 ▼
        ┌──────────┐  ┌────────────┐  ┌──────────────┐
        │   YOLO   │  │ Detectron2 │  │  Floorplan   │
        │ Detector │  │ Segmenter  │  │   Analyzer   │
        └──────────┘  └────────────┘  └──────────────┘
             │             │              │
             └─────────────┼──────────────┘
                           ▼
                 ┌──────────────────┐
                 │ Detection Merger │
                 │  (IoU-based)     │
                 └──────────────────┘
```

### Tech Stack

#### Frontend
- **Framework**: Next.js 15.3.4 with App Router
- **UI Library**: React 19
- **Styling**: Tailwind CSS 4
- **Language**: TypeScript 5
- **Icons**: Lucide React, React Icons
- **Security**: Crypto-JS, JS-Cookie

#### Backend
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn with standard extras
- **Authentication**: Python-JOSE, Passlib with bcrypt
- **Security**: SlowAPI (rate limiting), python-magic (file validation)
- **ML Libraries**: PyTorch, Ultralytics YOLO, Detectron2, OpenCV, EasyOCR

#### ML Models
- **YOLO v8**: Object detection (yolov8n.pt, yolov8l.pt, yolov8s-seg.pt)
- **Detectron2**: Instance segmentation with Mask R-CNN
- **Floorplan Analyzer**: EasyOCR + Contour Detection + Fuzzy Matching

#### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Version Control**: Git with Git LFS for large model files

## Quick Start

### Prerequisites

- **Docker** (version 20.10+) and **Docker Compose** (version 2.0+)
- At least **8GB RAM** (for ML models)
- At least **10GB free disk space**

### One-Command Start

```bash
# Clone the repository
git clone https://github.com/nikunjmathur08/IntoAEC.git
cd IntoAEC

# Start the application (with build)
./start.sh --build

# Or start without rebuild
./start.sh
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Stop the Application

```bash
./stop.sh
```

## Installation

### Option 1: Docker (Recommended)

See [Quick Start](#-quick-start) above.

### Option 2: Manual Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/nikunjmathur08/IntoAEC.git
cd IntoAEC
```

#### 2. Setup Backend

```bash
cd server
pip install -r requirements.txt

# Install Detectron2 (optional but recommended)
./install_detectron2.sh

# Install Floorplan Analyzer dependencies
pip install easyocr rapidfuzz

# Start the server
python main.py
```

The backend will start on `http://localhost:8000`

#### 3. Setup Frontend

```bash
cd client
npm install

# Development mode
npm run dev

# Production build
npm run build
npm start
```

The frontend will start on `http://localhost:3000`

## Usage

### 1. Upload a Floor Plan

- Navigate to http://localhost:3000
- Click "Upload Blueprint" or drag and drop your file
- Supported formats: PNG, JPG, JPEG, PDF

### 2. Select Analysis Models

Choose which models to run:
- **YOLO** - Fast object detection
- **Detectron2** - Advanced instance segmentation
- **Floorplan Analyzer** - OCR + contour detection
- **Combined** - Merge all model results

### 3. View Results

- **Visualizations**: Annotated images with detected elements
- **Detections**: List of identified rooms, walls, doors, windows
- **Measurements**: Room dimensions and areas
- **Cost Estimation**: Material and labor costs

### 4. Dashboard

- View analysis history
- Compare multiple floor plans
- Export results as JSON or images

## API Reference

### Authentication

#### Register User
```bash
POST /auth/register
Content-Type: application/json

{
  "username": "user@example.com",
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Login
```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

Returns:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Analysis Endpoints

#### Single Image Analysis
```bash
POST /analyze?model_type=yolo
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@floorplan.png
```

**Parameters:**
- `model_type`: `yolo`, `detectron2`, `floorplan`, or `combined`
- `keep_classes`: Comma-separated list of classes to keep (optional)
- `enable_polygon_fitting`: Enable polygon fitting (boolean, default: false)
- `min_conf`: Minimum confidence for OCR (float, default: 0.4)
- `iou_threshold`: IoU threshold for merging (float, default: 0.3)

**Response:**
```json
{
  "success": true,
  "filename": "floorplan.png",
  "model_type": "yolo",
  "detections": [
    {
      "class": "room",
      "confidence": 0.95,
      "bbox": [100, 150, 400, 500],
      "area": 105000
    }
  ],
  "summary": {
    "total_detections": 15,
    "classes": {"room": 5, "door": 4, "window": 6}
  },
  "result_image": "data:image/png;base64,..."
}
```

#### Batch Analysis
```bash
POST /analyze/batch?model_type=combined
Authorization: Bearer <token>
Content-Type: multipart/form-data

files=@plan1.png
files=@plan2.png
```

#### Model Information
```bash
GET /model/info
```

Returns available models and their status.

#### Health Check
```bash
GET /health
```

## ML Models

### YOLO (Ultralytics)

- **Purpose**: Fast object detection
- **Model Files**: 
  - `yolov8n.pt` - Nano (fastest)
  - `yolov8l.pt` - Large (most accurate)
  - `yolov8s-seg.pt` - Segmentation variant
- **Classes**: Wall, Door, Window, Room, Stairs, Bathroom, Kitchen, Bedroom, Living Room
- **Performance**: ~50ms per image

### Detectron2 (Facebook Research)

- **Purpose**: Instance segmentation with masks
- **Architecture**: Mask R-CNN with ResNet-50 backbone
- **Model File**: `model_final.pth`
- **Features**: 
  - Precise segmentation masks
  - Polygon fitting for room boundaries
  - Class filtering
- **Performance**: ~200ms per image

### Floorplan Analyzer (Custom)

- **Purpose**: OCR-based text extraction and room detection
- **Components**:
  - **EasyOCR**: Text detection and recognition
  - **Contour Detection**: Room boundary identification
  - **Fuzzy Matching**: Label correction (e.g., "Livng Rom" → "Living Room")
  - **Scale Estimation**: Auto-detect scale from annotations
- **Performance**: ~500ms per image

### Detection Merger

- **Purpose**: Combine results from multiple models
- **Algorithm**: IoU-based non-maximum suppression
- **Features**:
  - Intelligent deduplication
  - Confidence-based prioritization
  - Class normalization


## Security

IntoAEC implements enterprise-grade security measures:

### Authentication & Authorization
- JWT-based token authentication
- Password hashing with bcrypt
- Secure session management
- Token expiration (30 minutes for access tokens)

### File Upload Security
- File type validation (MIME type checking)
- File size limits (10MB max)
- Filename sanitization (prevent path traversal)
- Malicious content scanning
- Secure temporary file handling

### Rate Limiting
- 5 requests/minute for analysis endpoints
- IP-based tracking
- Configurable limits via environment variables

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HSTS)
- `Content-Security-Policy` (CSP)
- `Referrer-Policy: strict-origin-when-cross-origin`

### CORS Protection
- Restricted origins (no wildcards)
- Limited HTTP methods (GET, POST)
- Credential handling

For more details, see [SECURITY_IMPLEMENTATION.md](SECURITY_IMPLEMENTATION.md)

## Docker Deployment

### Development Environment

```bash
# Start with hot-reload
docker-compose -f docker-compose.dev.yml up --build

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Production Environment

```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Secure Deployment

```bash
# Deploy with security configurations
./deploy_secure.sh
```

This script:
- Generates secure secrets
- Sets up environment variables
- Configures SSL/TLS (if certificates provided)
- Enables all security features

For more details, see:
- [DOCKER_SETUP.md](DOCKER_SETUP.md)
- [README_DOCKER_DEPLOYMENT.md](README_DOCKER_DEPLOYMENT.md)


## Project Structure

```
IntoAEC/
├── client/                     # Next.js Frontend
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx            # Home page
│   │   ├── layout.tsx          # Root layout
│   │   ├── dashboard/          # Dashboard page
│   │   └── cost-estimation/    # Cost estimation page
│   ├── components/             # React components
│   │   ├── Navbar.tsx
│   │   ├── HeroSection.tsx
│   │   ├── FeaturesGrid.tsx
│   │   ├── UploadSection.tsx
│   │   ├── Dashboard.tsx
│   │   ├── LoginForm.tsx
│   │   └── CostEstimation/     # Cost estimation components
│   ├── lib/                    # Utility functions
│   │   ├── estimationData.ts
│   │   ├── estimationUtils.ts
│   │   ├── fileUtils.ts
│   │   └── secureStorage.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
│
├── server/                     # FastAPI Backend
│   ├── main.py                 # Main FastAPI application
│   ├── main_secure.py          # Secure version with auth
│   ├── auth.py                 # Authentication module
│   ├── security.py             # Security utilities
│   ├── models.py               # Pydantic models
│   ├── requirements.txt        # Python dependencies
│   ├── install_detectron2.sh   # Detectron2 installation script
│   ├── start.sh                # Server startup script
│   ├── temp/                   # Temporary file storage
│   └── Dockerfile
│
├── ml/                          # Machine Learning Models
│   ├── detectron2_inference.py  # Detectron2 wrapper
│   ├── detection_merger.py      # Multi-model merger
│   ├── floorplan_analyzer_wrapper.py  # Floorplan analyzer
│   ├── floorplan_analyzer/      # Floorplan analyzer module
│   │   ├── main.py
│   │   ├── ocr_utils.py         # OCR utilities
│   │   ├── line_utils.py        # Contour detection
│   │   ├── fuzzy_wuzzy.py       # Label correction
│   │   └── export_utils.py      # Export utilities
│   └── demoprpoj/               # Model files and datasets
│       ├── yolov8n.pt
│       ├── yolov8l.pt
│       ├── yolov8s-seg.pt
│       ├── deeplabv3_floorplan.pth
│       ├── runs/                # Training runs
│       ├── dataset/             # Training datasets
│       └── checkpoints/         # Model checkpoints
│
├── docker-compose.yml           # Production Docker config
├── docker-compose.dev.yml       # Development Docker config
├── start.sh                     # Application startup script
├── stop.sh                      # Application shutdown script
├── deploy_secure.sh             # Secure deployment script
├── .gitignore                   # Git ignore rules
├── .gitattributes               # Git LFS configuration
├── .dockerignore                # Docker ignore rules
│
├── DOCKER_SETUP.md              # Docker setup guide
├── README_DOCKER_DEPLOYMENT.md  # Docker deployment guide
├── SECURITY_IMPLEMENTATION.md   # Security documentation
├── FLOORPLAN_ANALYZER_SETUP.md  # Floorplan analyzer guide
└── README.md                    # You're here :p
```

## Development

### Frontend Development

```bash
cd client
npm run dev        # Start dev server with hot-reload
npm run build      # Build for production
npm run lint       # Run ESLint
```

### Backend Development

```bash
cd server
python main.py     # Start FastAPI server
# Server auto-reloads on file changes
```

### Adding New ML Models

1. Create a new predictor class in `ml/`
2. Add model initialization in `server/main.py`
3. Update the `/analyze` endpoint to support the new model
4. Add model info to `/model/info` endpoint

### Environment Variables

#### Backend (.env)
```bash
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3000
MAX_FILE_SIZE=10485760
RATE_LIMIT=5/minute
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Performance

### Benchmarks (Single Image)

| Model | Avg Time | Memory | Accuracy |
|-------|----------|--------|----------|
| YOLO v8n | ~50ms | 500MB | Good |
| YOLO v8l | ~150ms | 1.5GB | Excellent |
| Detectron2 | ~200ms | 2GB | Excellent |
| Floorplan Analyzer | ~500ms | 1GB | Good |
| Combined | ~800ms | 2.5GB | Best |

*Tested on: MacBook Pro M4, 16GB RAM*


## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for the AEC Industry**

</div>
