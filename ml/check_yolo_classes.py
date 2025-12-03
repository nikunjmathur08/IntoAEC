"""
Quick script to check YOLO model classes
"""
from ultralytics import YOLO
import os

# Path to the YOLO model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "demoprpoj/runs/detect/train2/weights/best2.pt")

print(f"Loading YOLO model from: {MODEL_PATH}")
print("-" * 60)

# Load the model
model = YOLO(MODEL_PATH)

# Get class names
class_names = model.names
print(f"\n📋 YOLO Model Classes ({len(class_names)} total):\n")

# Display in a nice format
for class_id, class_name in class_names.items():
    print(f"  {class_id:2d}: {class_name}")

print("\n" + "-" * 60)
print(f"✅ Model can detect {len(class_names)} different classes")
