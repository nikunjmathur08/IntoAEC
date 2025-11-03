import os
import cv2
import matplotlib.pyplot as plt
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

# ===============================
# Load Configuration
# ===============================
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file(
    "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"
))

# Update these paths for your local machine
cfg.MODEL.WEIGHTS = "demoprpoj/output/model_final_2.pth"  # path to trained model
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 9  # number of classes in your dataset
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.50  # confidence threshold
cfg.DATASETS.TEST = ("my_dataset_val", )
cfg.MODEL.DEVICE = "cpu"  # force CPU to avoid CUDA requirement

# Initialize predictor
predictor = DefaultPredictor(cfg)

# ===============================
# Run Inference on Single Image
# ===============================
image_path = "floorplan.png"  # path to your image
im = cv2.imread(image_path)
outputs = predictor(im)

# ===============================
# Visualize Results
# ===============================
v = Visualizer(im[:, :, ::-1], MetadataCatalog.get("my_dataset_val"), scale=1.2)
out = v.draw_instance_predictions(outputs["instances"].to("cpu"))

plt.figure(figsize=(12, 8))
plt.imshow(out.get_image()[:, :, ::-1])
plt.axis("off")
plt.show()