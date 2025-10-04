import cv2
import numpy as np
import torch
import matplotlib.pyplot as plt
from segment_anything import sam_model_registry, SamPredictor
from pathlib import Path

# === CONFIG ===
image_path = Path("test-blueprint2.jpeg")
yolo_txt_path = Path("runs/detect/predict/output.txt")
output_path = Path("runs/segment/output_clean_masked.jpg")

sam_checkpoint = "checkpoints/sam_vit_h_4b8939.pth"
model_type = "vit_h"
device = "cuda" if torch.cuda.is_available() else "cpu"

# === LOAD IMAGE ===
image = cv2.imread(str(image_path))
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# === LOAD YOLO BOXES ===
boxes = []
with open(yolo_txt_path, "r") as f:
    for line in f:
        parts = line.strip().split()
        cls_id, conf = int(parts[0]), float(parts[1])
        x1, y1, x2, y2 = map(int, parts[2:])
        boxes.append((x1, y1, x2, y2, cls_id))

# === LOAD SAM ===
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint).to(device)
predictor = SamPredictor(sam)
predictor.set_image(image_rgb)

# === MASK PAINTING ===
overlay = np.zeros_like(image_rgb, dtype=np.uint8)
colors = plt.get_cmap("tab20", len(boxes) + 1)
 # ✅ FIXED here

for i, (x1, y1, x2, y2, cls_id) in enumerate(boxes):
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    input_point = np.array([[cx, cy]])
    input_label = np.array([1])

    masks, scores, logits = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        box=np.array([x1, y1, x2, y2]),
        multimask_output=True
    )

    best_mask = masks[np.argmax(scores)]
    color = np.array(colors(i)[:3]) * 255
    overlay[best_mask] = color.astype(np.uint8)

# === BLEND AND SAVE ===
blended = cv2.addWeighted(image_rgb, 0.6, overlay, 0.4, 0)
cv2.imwrite(str(output_path), cv2.cvtColor(blended, cv2.COLOR_RGB2BGR))
print(f" Clean masks saved to: {output_path}")
