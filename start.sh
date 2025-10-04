#!/bin/bash

# IntoAEC Docker Startup Script
# This script helps you start the entire application with Docker

set -e

echo "🚀 Starting IntoAEC Application with Docker..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p server/temp server/uploads

# Check if we should build from scratch
if [ "$1" = "--build" ] || [ "$1" = "-b" ]; then
    print_status "Building images from scratch..."
    docker-compose build --no-cache
elif [ "$1" = "--pull" ] || [ "$1" = "-p" ]; then
    print_status "Pulling latest images..."
    docker-compose pull
else
    print_status "Building images (using cache if available)..."
    docker-compose build
fi

# Start the services
print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check if services are running
print_status "Checking service status..."

# Check backend health
if curl -f http://localhost:8000/health &> /dev/null; then
    print_success "Backend is running on http://localhost:8000"
else
    print_warning "Backend might still be starting up..."
fi

# Check frontend
if curl -f http://localhost:3000 &> /dev/null; then
    print_success "Frontend is running on http://localhost:3000"
else
    print_warning "Frontend might still be starting up..."
fi

echo ""
print_success "🎉 IntoAEC Application is starting up!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "To restart: docker-compose restart"
echo ""
