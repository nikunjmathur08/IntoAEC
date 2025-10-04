import os
from ultralytics import YOLO
import cv2

# ========== CONFIG ==========
MODEL_PATH = "runs/detect/train2/weights/best.pt"  # or your custom model .pt
IMAGE_PATH = "test-blueprint1.jpeg"  # input image
OUTPUT_DIR = "runs/detect/predict"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========== RUN YOLO ==========
model = YOLO(MODEL_PATH)
results = model(IMAGE_PATH)

# ========== SAVE IMAGE ==========
save_path = os.path.join(OUTPUT_DIR, "output.jpg")
results[0].save(save_path)
print(f" Saved image with boxes: {save_path}")

# ========== SAVE TEXT FILE ==========
txt_path = os.path.join(OUTPUT_DIR, "output.txt")
with open(txt_path, "w") as f:
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        f.write(f"{cls} {conf:.4f} {int(x1)} {int(y1)} {int(x2)} {int(y2)}\n")

print(f" Saved detections: {txt_path}")
