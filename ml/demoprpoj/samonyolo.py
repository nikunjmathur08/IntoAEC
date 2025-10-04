import os
import cv2
import numpy as np
import torch
import matplotlib.pyplot as plt
from segment_anything import sam_model_registry, SamPredictor

# ====== CONFIG ======
TXT_PATH = "runs/detect/predict/output.txt"
IMAGE_PATH = "runs/detect/predict/output.jpg"
CHECKPOINT_PATH = "checkpoints/sam_vit_h_4b8939.pth"  # Make sure it's downloaded
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_TYPE = "vit_h"

# ====== LOAD IMAGE ======
image = cv2.imread(IMAGE_PATH)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# ====== LOAD SAM ======
sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH).to(DEVICE)
predictor = SamPredictor(sam)
predictor.set_image(image_rgb)

# ====== READ DETECTIONS (already pixel coords) ======
boxes = []
with open(TXT_PATH, 'r') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) != 6:
            continue
        _, conf, x1, y1, x2, y2 = parts
        box = [int(float(x1)), int(float(y1)), int(float(x2)), int(float(y2))]
        boxes.append(box)

# ====== PREDICT MASKS ======
masks = []
for box in boxes:
    mask, _, _ = predictor.predict(box=np.array(box), multimask_output=False)
    masks.append(mask[0])

# ====== OVERLAY MASKS ======
output = image_rgb.copy()
colors = plt.cm.get_cmap("tab20", len(masks) + 1)

for i, mask in enumerate(masks):
    color = np.array(colors(i)[:3]) * 255
    output[mask] = output[mask] * 0.4 + color * 0.6

# ====== SAVE OUTPUT ======
os.makedirs("runs/segment", exist_ok=True)
cv2.imwrite("runs/segment/output_masked.jpg", cv2.cvtColor(output, cv2.COLOR_RGB2BGR))
print(" Saved: runs/segment/output_masked.jpg")
