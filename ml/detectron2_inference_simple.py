import os
import cv2
import numpy as np
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

class Detectron2PredictorSimple:
    """
    Simplified Detectron2 predictor for floor plan analysis.
    This is an alternative implementation with a simpler approach and higher confidence threshold.
    """

    def __init__(self, model_path=None, num_classes=9, score_threshold=0.70):
        """
        Initialize simplified Detectron2 predictor

        Args:
            model_path: Path to the trained model weights (model_final_2.pth)
            num_classes: Number of classes in your dataset
            score_threshold: Confidence threshold for detections (default 0.70 for higher precision)
        """
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Set default model path
        if model_path is None:
            model_path = os.path.join(self.script_dir, "demoprpoj/output/model_final_2.pth")

        self.model_path = model_path
        self.num_classes = num_classes
        self.score_threshold = score_threshold
        self.predictor = None
        self.cfg = None

        # ACTUAL class names from the Roboflow dataset training
        # This model was trained on floor plan room/furniture segmentation
        # Dataset: https://universe.roboflow.com/shaad-vezb0/floor-plan-segmentation-dtr4r-dtk5k
        self.class_names = [
            "Balcony",
            "Bed",
            "Bedroom",
            "Dining Room",
            "Dining table",
            "Foyer",
            "Kitchen",
            "Living Room",
            "Sofa"
        ][:num_classes]

        self._setup_config()
        self._setup_metadata()

    def _setup_config(self):
        """Setup Detectron2 configuration with simplified approach"""
        self.cfg = get_cfg()

        # Load base config - Mask R-CNN with ResNet-50 FPN backbone
        self.cfg.merge_from_file(
            model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
        )

        # REQUIRE the trained model - NO FALLBACK to COCO
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"❌ Trained Detectron2 model not found at: {self.model_path}\n"
                f"This model is required for floor plan segmentation.\n"
                f"Expected file: model_final_2.pth\n"
                f"Please ensure the model file exists or train a new model."
            )

        self.cfg.MODEL.WEIGHTS = self.model_path
        print(f"📁 Using trained model: {self.model_path}")

        # Set number of classes
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = self.num_classes

        # Set higher confidence threshold for better precision
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.score_threshold

        # Set test dataset (for metadata)
        self.cfg.DATASETS.TEST = ("my_dataset_val",)

        # Set device
        self.cfg.MODEL.DEVICE = "cuda" if cv2.cuda.getCudaEnabledDeviceCount() > 0 else "cpu"

        print(f"✅ Simplified config setup complete")
        print(f"   Device: {self.cfg.MODEL.DEVICE}")
        print(f"   Confidence threshold: {self.score_threshold}")
        print(f"   Number of classes: {self.num_classes}")
        print(f"   Classes: {', '.join(self.class_names)}")

    def _setup_metadata(self):
        """Setup metadata for visualization"""
        if "my_dataset_val" not in MetadataCatalog:
            MetadataCatalog.get("my_dataset_val").set(
                thing_classes=self.class_names,
                evaluator_type="coco"
            )

    def load_model(self):
        """Load the Detectron2 predictor"""
        if self.predictor is None:
            self.predictor = DefaultPredictor(self.cfg)
            print("✅ Simplified Detectron2 predictor loaded!")
        return self.predictor

    def predict(self, image_path):
        """
        Run inference on an image with simplified approach

        Args:
            image_path: Path to the input image or numpy array

        Returns:
            dict: Prediction results with instances, visualized image, etc.
        """
        if self.predictor is None:
            self.load_model()

        # Read image
        if isinstance(image_path, str):
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            im = cv2.imread(image_path)
        else:
            # Assume it's already a numpy array
            im = image_path

        if im is None:
            raise ValueError("Could not load image")

        # Run inference
        print(f"🔍 Running simplified Detectron2 inference...")
        outputs = self.predictor(im)

        # Get instances on CPU
        instances = outputs["instances"].to("cpu")

        # Extract predictions
        predictions = {
            "boxes": instances.pred_boxes.tensor.numpy() if len(instances) > 0 else np.array([]),
            "classes": instances.pred_classes.numpy() if len(instances) > 0 else np.array([]),
            "scores": instances.scores.numpy() if len(instances) > 0 else np.array([]),
            "masks": instances.pred_masks.numpy() if len(instances) > 0 and instances.has("pred_masks") else None
        }

        # Create visualization
        v = Visualizer(
            im[:, :, ::-1],  # BGR to RGB
            metadata=MetadataCatalog.get("my_dataset_val"),
            scale=1.2  # Slightly larger scale for better visibility
        )
        vis_output = v.draw_instance_predictions(instances)
        vis_image = vis_output.get_image()[:, :, ::-1]  # RGB to BGR

        result = {
            "predictions": predictions,
            "visualized_image": vis_image,
            "raw_outputs": outputs,
            "num_detections": len(instances)
        }

        return result

    def predict_and_save(self, image_path, output_path=None):
        """
        Run inference and save the visualized result

        Args:
            image_path: Path to input image
            output_path: Path to save the output image

        Returns:
            dict: Prediction results
        """
        results = self.predict(image_path)

        if output_path is None:
            # Generate output path
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(
                os.path.dirname(image_path),
                f"{base_name}_detectron2_simple_result.jpg"
            )

        # Save visualization
        cv2.imwrite(output_path, results["visualized_image"])
        print(f"💾 Saved result image: {output_path}")

        results["output_path"] = output_path
        return results

    def get_detection_summary(self, results):
        """
        Get a summary of detections

        Args:
            results: Results from predict() method

        Returns:
            dict: Summary of detections
        """
        predictions = results["predictions"]
        summary = {
            "total_detections": len(predictions["classes"]),
            "detections_by_class": {},
            "detection_details": []
        }

        for cls_id, score, box in zip(
            predictions["classes"],
            predictions["scores"],
            predictions["boxes"]
        ):
            class_name = self.class_names[cls_id] if cls_id < len(self.class_names) else f"class_{cls_id}"

            if class_name not in summary["detections_by_class"]:
                summary["detections_by_class"][class_name] = 0
            summary["detections_by_class"][class_name] += 1

            summary["detection_details"].append({
                "class_id": int(cls_id),
                "class_name": class_name,
                "confidence": float(score),
                "bbox": {
                    "x1": float(box[0]),
                    "y1": float(box[1]),
                    "x2": float(box[2]),
                    "y2": float(box[3]),
                    "width": float(box[2] - box[0]),
                    "height": float(box[3] - box[1])
                }
            })

        return summary

def main():
    """
    Example usage of simplified Detectron2 predictor
    """
    print("🚀 Simplified Detectron2 Floor Plan Analysis")

    # Initialize predictor with higher confidence threshold
    predictor = Detectron2PredictorSimple(score_threshold=0.70)

    # Test image path
    test_image = os.path.join(predictor.script_dir, "demoprpoj/test-blueprint2.jpeg")

    if not os.path.exists(test_image):
        print(f"⚠️ Test image not found: {test_image}")
        print("Please provide a valid image path")
        return

    try:
        # Run prediction
        results = predictor.predict_and_save(test_image)

        # Get summary
        summary = predictor.get_detection_summary(results)

        print(f"\n📊 Detection Summary:")
        print(f"Total detections: {summary['total_detections']}")
        print(f"Detections by class: {summary['detections_by_class']}")

        print(f"\n📝 Detailed results:")
        for detection in summary['detection_details']:
            print(f"  - {detection['class_name']}: {detection['confidence']:.3f} confidence")

        print(f"\n✅ Analysis complete! Check the output image.")

    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        raise

if __name__ == "__main__":
    main()
