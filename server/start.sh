#!/bin/bash

# IntoAEC FastAPI Server Startup Script

echo "🚀 Starting IntoAEC FastAPI Server..."
echo "📁 Working directory: $(pwd)"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Conda first."
    exit 1
fi

# Check if environment exists, create if it doesn't
if ! conda env list | grep -q "IntoAEC"; then
    echo "📦 Creating Conda environment 'IntoAEC'..."
    conda create -n IntoAEC python=3.10 -y
fi

# Activate conda environment
echo "🔧 Activating Conda environment..."
conda activate IntoAEC || source activate IntoAEC

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Check if model file exists
MODEL_PATH="../ml/demoprpoj/runs/detect/train2/weights/best.pt"
if [ ! -f "$MODEL_PATH" ]; then
    echo "⚠️  Warning: Model file not found at $MODEL_PATH"
    echo "   Please make sure your YOLO model is trained and available."
fi

# Start the server
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "   Press Ctrl+C to stop the server"
echo ""
python main.py