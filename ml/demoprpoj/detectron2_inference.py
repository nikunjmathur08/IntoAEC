import os
import cv2
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from detectron2.config import get_cfg
from detectron2 import model_zoo

# Set up configuration
cfg = get_cfg()
# Use a pre-trained model from model zoo for demonstration
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
cfg.MODEL.DEVICE = "cpu"  # Use CPU for compatibility
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # Set threshold for this model

# Create predictor
predictor = DefaultPredictor(cfg)

# Run inference on an image (using one of the available images)
im = cv2.imread("test-blueprint.png")
if im is None:
    print("Error: Could not load image 'test-blueprint.png'. Please check if the file exists.")
    exit(1)

outputs = predictor(im)

# Visualize
v = Visualizer(im[:, :, ::-1], metadata=MetadataCatalog.get("coco_2017_val"), scale=0.5)
out = v.draw_instance_predictions(outputs["instances"].to("cpu"))

# Save the output image instead of displaying (since we're not in Colab)
output_path = "detectron2_output.jpg"
cv2.imwrite(output_path, out.get_image()[:, :, ::-1])
print(f"Output saved to: {output_path}")

# Also display the image if possible
try:
    cv2.imshow("Detectron2 Output", out.get_image()[:, :, ::-1])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
except:
    print("Could not display image (no display available)")
