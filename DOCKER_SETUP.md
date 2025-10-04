# IntoAEC Docker Setup Guide

This guide will help you containerize and run the entire IntoAEC application using Docker.

## 🏗️ Architecture

The application consists of:
- **Frontend**: Next.js React application (Port 3000)
- **Backend**: Python FastAPI server (Port 8000)
- **ML Models**: YOLO, Detectron2, and Floorplan Analyzer

## 📋 Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- At least 8GB RAM (for ML models)
- At least 10GB free disk space

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
cd /Users/nikunjmathur/Developer/IntoAEC
```

### 2. Start the Application
```bash
# Start with build (first time)
./start.sh --build

# Or start normally (uses cache)
./start.sh
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Stop the Application
```bash
./stop.sh
```

## 🔧 Manual Docker Commands

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

### Clean Up
```bash
# Remove containers and volumes
docker-compose down -v

# Remove everything including images
docker-compose down -v --rmi all

# Clean up Docker system
docker system prune -a
```

## 📁 Directory Structure

```
IntoAEC/
├── client/                 # Next.js Frontend
│   ├── Dockerfile
│   ├── .dockerignore
│   └── ...
├── server/                 # Python Backend
│   ├── Dockerfile
│   ├── .dockerignore
│   └── ...
├── ml/                     # ML Models and Scripts
├── docker-compose.yml      # Main orchestration
├── start.sh               # Startup script
├── stop.sh                # Stop script
└── DOCKER_SETUP.md        # This file
```

## 🐳 Docker Services

### Frontend Service
- **Image**: Custom Next.js build
- **Port**: 3000
- **Environment**: Production
- **Dependencies**: Backend service

### Backend Service
- **Image**: Custom Python FastAPI build
- **Port**: 8000
- **Environment**: Production
- **Volumes**: ML models, temp files, uploads

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the ports
   lsof -i :3000
   lsof -i :8000
   
   # Kill processes if needed
   kill -9 <PID>
   ```

2. **Out of Memory**
   ```bash
   # Increase Docker memory limit
   # Docker Desktop -> Settings -> Resources -> Memory
   ```

3. **Build Failures**
   ```bash
   # Clean build
   docker-compose build --no-cache
   
   # Check logs
   docker-compose logs frontend
   docker-compose logs backend
   ```

4. **ML Models Not Loading**
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

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Backend Configuration
PYTHONPATH=/app
ENVIRONMENT=production

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=production

# Optional: Redis Configuration
REDIS_URL=redis://redis:6379
```

### Volume Mounts

The following directories are mounted:
- `./ml` → `/app/ml` (ML models, read-only)
- `./server/temp` → `/app/temp` (temporary files)
- `./server/uploads` → `/app/uploads` (uploaded files)

## 📊 Monitoring

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

### Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## 🚀 Production Deployment

### Security Considerations
1. Change default passwords
2. Use environment variables for secrets
3. Enable HTTPS
4. Configure firewall rules
5. Regular security updates

### Scaling
```bash
# Scale backend service
docker-compose up -d --scale backend=3

# Use load balancer (nginx)
# Add nginx service to docker-compose.yml
```

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify all services are running: `docker-compose ps`
3. Check resource usage: `docker stats`
4. Restart services: `docker-compose restart`
5. Clean rebuild: `./start.sh --build`

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Docker Guide](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)
