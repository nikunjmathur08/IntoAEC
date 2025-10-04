#!/bin/bash

# IntoAEC Docker Stop Script
# This script stops the entire application

set -e

echo "🛑 Stopping IntoAEC Application..."

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

# Stop all services
print_status "Stopping all services..."
docker-compose down

# Optionally remove volumes (uncomment if you want to clean up data)
# print_status "Removing volumes..."
# docker-compose down -v

# Optionally remove images (uncomment if you want to clean up images)
# print_status "Removing images..."
# docker-compose down --rmi all

print_success "✅ IntoAEC Application stopped successfully!"
echo ""
echo "To start again: ./start.sh"
echo "To clean up everything: docker-compose down -v --rmi all"
echo ""
