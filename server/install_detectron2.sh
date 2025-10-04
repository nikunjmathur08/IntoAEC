#!/bin/bash

# Detectron2 Installation Script for IntoAEC Server

echo "🔧 Installing Detectron2 for IntoAEC Server..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Check Python version
python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python version: $python_version"

# Install PyTorch first (required for Detectron2)
echo "📥 Installing PyTorch..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install Detectron2
echo "📥 Installing Detectron2..."
pip install 'git+https://github.com/facebookresearch/detectron2.git'

# Verify installation
echo "✅ Verifying Detectron2 installation..."
python -c "
try:
    import detectron2
    from detectron2.utils.logger import setup_logger
    setup_logger()
    print('✅ Detectron2 installed successfully!')
    print(f'   Version: {detectron2.__version__}')
except ImportError as e:
    print(f'❌ Detectron2 installation failed: {e}')
    exit(1)
"

echo "🎉 Detectron2 installation complete!"
echo "   You can now use both YOLO and Detectron2 models in the server."
