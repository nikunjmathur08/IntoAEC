#!/bin/bash

# IntoAEC YOLO Docker Deployment Script
# This script helps deploy the YOLO-only container to various cloud platforms

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="intaec-yolo"
VERSION="latest"
REGION="us-central1"

echo -e "${BLUE}🚀 IntoAEC YOLO Docker Deployment Script${NC}"
echo "================================================"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker Desktop and try again.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is running${NC}"
}

# Function to build the Docker image
build_image() {
    echo -e "${YELLOW}🔨 Building Docker image...${NC}"
    docker build -t ${IMAGE_NAME}:${VERSION} .
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
}

# Function to test the container locally
test_local() {
    echo -e "${YELLOW}🧪 Testing container locally...${NC}"
    echo "Starting container on port 8000..."
    echo "You can test it at: http://localhost:8000"
    echo "Press Ctrl+C to stop the container"
    echo ""
    
    docker run --rm -p 8000:8000 ${IMAGE_NAME}:${VERSION}
}

# Function to deploy to Google Cloud Run
deploy_gcp() {
    echo -e "${YELLOW}☁️ Deploying to Google Cloud Run...${NC}"
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK${NC}"
        exit 1
    fi
    
    # Get project ID
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ No Google Cloud project set. Run: gcloud config set project YOUR_PROJECT_ID${NC}"
        exit 1
    fi
    
    echo "Using project: $PROJECT_ID"
    
    # Build and push to Google Container Registry
    echo "Building and pushing to GCR..."
    docker tag ${IMAGE_NAME}:${VERSION} gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${VERSION}
    docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${VERSION}
    
    # Deploy to Cloud Run
    echo "Deploying to Cloud Run..."
    gcloud run deploy ${IMAGE_NAME} \
        --image gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${VERSION} \
        --platform managed \
        --region ${REGION} \
        --allow-unauthenticated \
        --port 8000 \
        --memory 2Gi \
        --cpu 2 \
        --max-instances 10
    
    echo -e "${GREEN}✅ Deployed to Google Cloud Run${NC}"
    echo "Service URL: https://${IMAGE_NAME}-<hash>-uc.a.run.app"
}

# Function to deploy to AWS ECS
deploy_aws() {
    echo -e "${YELLOW}☁️ Deploying to AWS ECS...${NC}"
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI${NC}"
        exit 1
    fi
    
    # Get AWS account ID and region
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region)
    
    if [ -z "$ACCOUNT_ID" ]; then
        echo -e "${RED}❌ AWS credentials not configured. Run: aws configure${NC}"
        exit 1
    fi
    
    echo "Using AWS Account: $ACCOUNT_ID, Region: $AWS_REGION"
    
    # Login to ECR
    echo "Logging in to ECR..."
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
    
    # Create ECR repository if it doesn't exist
    echo "Creating ECR repository..."
    aws ecr create-repository --repository-name ${IMAGE_NAME} --region ${AWS_REGION} 2>/dev/null || echo "Repository already exists"
    
    # Build and push to ECR
    echo "Building and pushing to ECR..."
    docker tag ${IMAGE_NAME}:${VERSION} ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:${VERSION}
    docker push ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:${VERSION}
    
    echo -e "${GREEN}✅ Image pushed to ECR${NC}"
    echo "ECR URI: ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:${VERSION}"
    echo "Now create an ECS task definition and service using this image."
}

# Function to deploy to Azure Container Instances
deploy_azure() {
    echo -e "${YELLOW}☁️ Deploying to Azure Container Instances...${NC}"
    
    # Check if Azure CLI is installed
    if ! command -v az &> /dev/null; then
        echo -e "${RED}❌ Azure CLI not found. Please install Azure CLI${NC}"
        exit 1
    fi
    
    # Get Azure subscription and resource group
    SUBSCRIPTION=$(az account show --query id --output tsv)
    RESOURCE_GROUP="intaec-rg"
    REGISTRY_NAME="intaecregistry"
    
    if [ -z "$SUBSCRIPTION" ]; then
        echo -e "${RED}❌ Not logged in to Azure. Run: az login${NC}"
        exit 1
    fi
    
    echo "Using subscription: $SUBSCRIPTION"
    
    # Create resource group
    echo "Creating resource group..."
    az group create --name ${RESOURCE_GROUP} --location ${REGION} 2>/dev/null || echo "Resource group already exists"
    
    # Create container registry
    echo "Creating container registry..."
    az acr create --resource-group ${RESOURCE_GROUP} --name ${REGISTRY_NAME} --sku Basic 2>/dev/null || echo "Registry already exists"
    
    # Login to ACR
    echo "Logging in to ACR..."
    az acr login --name ${REGISTRY_NAME}
    
    # Build and push to ACR
    echo "Building and pushing to ACR..."
    docker tag ${IMAGE_NAME}:${VERSION} ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${VERSION}
    docker push ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${VERSION}
    
    # Deploy to Container Instances
    echo "Deploying to Container Instances..."
    az container create \
        --resource-group ${RESOURCE_GROUP} \
        --name ${IMAGE_NAME} \
        --image ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${VERSION} \
        --ports 8000 \
        --memory 2 \
        --cpu 2 \
        --registry-login-server ${REGISTRY_NAME}.azurecr.io \
        --registry-username $(az acr credential show --name ${REGISTRY_NAME} --query username --output tsv) \
        --registry-password $(az acr credential show --name ${REGISTRY_NAME} --query passwords[0].value --output tsv)
    
    echo -e "${GREEN}✅ Deployed to Azure Container Instances${NC}"
    echo "Get the IP address with: az container show --resource-group ${RESOURCE_GROUP} --name ${IMAGE_NAME} --query ipAddress.ip --output tsv"
}

# Main script
case "$1" in
    "build")
        check_docker
        build_image
        ;;
    "test")
        check_docker
        build_image
        test_local
        ;;
    "gcp")
        check_docker
        build_image
        deploy_gcp
        ;;
    "aws")
        check_docker
        build_image
        deploy_aws
        ;;
    "azure")
        check_docker
        build_image
        deploy_azure
        ;;
    *)
        echo "Usage: $0 {build|test|gcp|aws|azure}"
        echo ""
        echo "Commands:"
        echo "  build  - Build the Docker image"
        echo "  test   - Build and test locally"
        echo "  gcp    - Deploy to Google Cloud Run"
        echo "  aws    - Deploy to AWS ECS"
        echo "  azure  - Deploy to Azure Container Instances"
        echo ""
        echo "Examples:"
        echo "  $0 build"
        echo "  $0 test"
        echo "  $0 gcp"
        exit 1
        ;;
esac
