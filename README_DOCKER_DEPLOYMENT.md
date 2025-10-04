# IntoAEC - Docker Deployment Guide

## 🏗️ Project Overview

IntoAEC is a comprehensive AEC (Architecture, Engineering, Construction) application that combines:
- **Frontend**: Next.js React application for cost estimation and project management
- **Backend**: Python FastAPI server with ML capabilities
- **ML Models**: YOLO, Detectron2, and Floorplan Analyzer for blueprint analysis

## 📋 Prerequisites

Before running this application, ensure you have:

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **At least 8GB RAM** (required for ML models)
- **At least 10GB free disk space**
- **Git** (for cloning the repository)

### Installing Docker

**On macOS:**
```bash
# Install Docker Desktop
brew install --cask docker
```

**On Linux (Ubuntu/Debian):**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**On Windows:**
- Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd IntoAEC
```

### 2. Make Scripts Executable
```bash
chmod +x start.sh stop.sh
```

### 3. Start the Application
```bash
# First time setup (builds all images)
./start.sh --build

# Subsequent runs (uses cached images)
./start.sh
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Stop the Application
```bash
./stop.sh
```

## 🔧 Manual Docker Commands

If you prefer to run Docker commands manually:

### Build and Start
```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Development Mode
```bash
# Start with live reload (development)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 🐳 Docker Services

### Frontend Service
- **Port**: 3000
- **Technology**: Next.js React application
- **Environment**: Production optimized
- **Dependencies**: Backend service

### Backend Service
- **Port**: 8000
- **Technology**: Python FastAPI with ML capabilities
- **Environment**: Production optimized
- **Volumes**: ML models, temp files, uploads
- **Health Check**: Built-in health monitoring

## 📁 Project Structure

```
IntoAEC/
├── client/                    # Next.js Frontend
│   ├── Dockerfile            # Frontend container config
│   ├── package.json          # Node.js dependencies
│   └── ...
├── server/                   # Python Backend
│   ├── Dockerfile            # Backend container config
│   ├── requirements.txt      # Python dependencies
│   └── ...
├── ml/                       # ML Models and Scripts
│   ├── demoprpoj/           # YOLO models
│   └── floorplan_analyzer/   # Floorplan analysis tools
├── docker-compose.yml        # Main orchestration
├── docker-compose.dev.yml    # Development overrides
├── start.sh                  # Startup script
├── stop.sh                   # Stop script
└── DOCKER_SETUP.md          # Detailed Docker guide
```

## 🔍 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8000

# Kill processes if needed
kill -9 <PID>
```

**2. Out of Memory**
- Increase Docker memory limit in Docker Desktop settings
- Ensure at least 8GB RAM is available
- Close other memory-intensive applications

**3. Build Failures**
```bash
# Clean build
docker-compose build --no-cache

# Check logs
docker-compose logs frontend
docker-compose logs backend
```

**4. ML Models Not Loading**
```bash
# Check if models are mounted
docker-compose exec backend ls -la /app/ml

# Verify model files exist
ls -la ml/
```

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check container status
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

## 🧹 Clean Up

### Remove Everything
```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Clean up Docker system
docker system prune -a
```

### Reset to Fresh State
```bash
# Complete cleanup
docker-compose down -v --rmi all
docker system prune -a

# Rebuild from scratch
./start.sh --build
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory (optional):

```env
# Backend Configuration
PYTHONPATH=/app
ENVIRONMENT=production

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=production
```

### Volume Mounts

The following directories are automatically mounted:
- `./ml` → `/app/ml` (ML models, read-only)
- `./server/temp` → `/app/temp` (temporary files)
- `./server/uploads` → `/app/uploads` (uploaded files)

## 📊 Monitoring

### Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Service Status
```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs backend
docker-compose logs frontend
```

## 🚀 Production Deployment

### Security Considerations
1. Change default passwords and API keys
2. Use environment variables for secrets
3. Enable HTTPS with reverse proxy
4. Configure firewall rules
5. Regular security updates

### Scaling
```bash
# Scale backend service
docker-compose up -d --scale backend=3
```

## 🆘 Support

If you encounter issues:

1. **Check the logs**: `docker-compose logs -f`
2. **Verify all services are running**: `docker-compose ps`
3. **Check resource usage**: `docker stats`
4. **Restart services**: `docker-compose restart`
5. **Clean rebuild**: `./start.sh --build`

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Docker Guide](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)

## 🎯 Quick Reference

| Command | Description |
|---------|-------------|
| `./start.sh` | Start the application |
| `./start.sh --build` | Start with fresh build |
| `./stop.sh` | Stop the application |
| `docker-compose logs -f` | View logs |
| `docker-compose ps` | Check status |
| `docker-compose restart` | Restart services |
| `docker-compose down -v` | Stop and clean up |

---

**Need Help?** Check the logs first: `docker-compose logs -f`
