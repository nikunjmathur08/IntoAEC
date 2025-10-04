import os
import cv2
import numpy as np
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.data.datasets import register_coco_instances
import json

class Detectron2Predictor:
    def __init__(self, model_path=None, config_path=None, num_classes=9, 
                 keep_classes=None, enable_polygon_fitting=False):
        """
        Initialize Detectron2 predictor for floor plan analysis
        
        Args:
            model_path: Path to the trained model weights (model_final.pth)
            config_path: Path to the config file
            num_classes: Number of classes in your dataset
            keep_classes: Set of class names to keep (e.g., {"floor", "Room"})
            enable_polygon_fitting: Whether to enable polygon fitting for room detection
        """
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set default paths
        if model_path is None:
            model_path = os.path.join(self.script_dir, "demoprpoj/output/model_final.pth")
        if config_path is None:
            config_path = os.path.join(self.script_dir, "demoprpoj/output/config.yaml")
            
        self.model_path = model_path
        self.config_path = config_path
        self.num_classes = num_classes
        self.predictor = None
        self.cfg = None
        self.keep_classes = keep_classes
        self.enable_polygon_fitting = enable_polygon_fitting
        
        # Class names for floor plan elements (customize based on your dataset)
        self.class_names = [
            "wall", "door", "window", "room", "stairs", 
            "bathroom", "kitchen", "bedroom", "living_room"
        ][:num_classes]
        
        self._setup_config()
        self._setup_metadata()
    
    def fit_polygon(self, mask, epsilon_factor=0.01):
        """
        Fit polygon to mask using contour approximation
        
        Args:
            mask: Binary mask array
            epsilon_factor: Factor for polygon approximation
            
        Returns:
            tuple: (polygons, bboxes) - list of polygon points and bounding boxes
        """
        mask_uint8 = (mask.astype(np.uint8)) * 255
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        polygons = []
        bboxes = []
        for cnt in contours:
            epsilon = epsilon_factor * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            polygons.append(approx.reshape(-1, 2).tolist())  # polygon points
            x, y, w, h = cv2.boundingRect(cnt)
            bboxes.append([x, y, x + w, y + h])
        return polygons, bboxes
    
    def _setup_config(self):
        """Setup Detectron2 configuration"""
        self.cfg = get_cfg()
        
        # Use Mask R-CNN with ResNet-50 FPN backbone
        self.cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
        
        # Load custom config if available
        if os.path.exists(self.config_path):
            self.cfg.merge_from_file(self.config_path)
        
        # Set model weights
        if os.path.exists(self.model_path):
            self.cfg.MODEL.WEIGHTS = self.model_path
        else:
            raise FileNotFoundError(f"Model weights not found at: {self.model_path}")
        
        # Set number of classes
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = self.num_classes
        
        # Set device (CPU or CUDA)
        self.cfg.MODEL.DEVICE = "cuda" if cv2.cuda.getCudaEnabledDeviceCount() > 0 else "cpu"
        
        # Set confidence threshold
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
        self.cfg.MODEL.RETINANET.SCORE_THRESH_TEST = 0.5
        
        print(f"✅ Config setup complete. Device: {self.cfg.MODEL.DEVICE}")
        print(f"📁 Model weights: {self.model_path}")
        print(f"🎯 Number of classes: {self.num_classes}")
    
    def _setup_metadata(self):
        """Setup metadata for visualization"""
        # Register custom dataset metadata
        if "my_dataset_val" not in MetadataCatalog:
            MetadataCatalog.get("my_dataset_val").set(
                thing_classes=self.class_names,
                evaluator_type="coco"
            )
    
    def load_model(self):
        """Load the Detectron2 predictor"""
        if self.predictor is None:
            self.predictor = DefaultPredictor(self.cfg)
            print("✅ Detectron2 predictor loaded successfully!")
        return self.predictor
    
    def predict(self, image_path):
        """
        Run inference on an image with optional class filtering and polygon fitting
        
        Args:
            image_path: Path to the input image
            
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
        print(f"🔍 Running Detectron2 inference...")
        outputs = self.predictor(im)
        
        # Process results
        instances = outputs["instances"].to("cpu")
        
        # Apply class filtering if specified
        if self.keep_classes is not None:
            print(f"🔍 Filtering classes to keep: {self.keep_classes}")
            keep_idx = []
            for i, cls_id in enumerate(instances.pred_classes):
                class_name = self.class_names[cls_id] if cls_id < len(self.class_names) else f"class_{cls_id}"
                if class_name in self.keep_classes:
                    keep_idx.append(i)
            
            if keep_idx:
                instances = instances[keep_idx]
                print(f"✅ Kept {len(keep_idx)} detections after class filtering")
            else:
                print("⚠️ No detections match the specified classes")
                # Create empty instances
                from detectron2.structures import Instances
                instances = Instances(instances.image_size)
        
        # Apply polygon fitting if enabled
        polygons_data = []
        if self.enable_polygon_fitting and len(instances) > 0 and instances.has("pred_masks"):
            print("🔍 Applying polygon fitting...")
            masks = instances.pred_masks.numpy()
            scores = instances.scores.numpy()
            classes = instances.pred_classes.numpy()
            
            # Sort masks by confidence
            order = np.argsort(-scores)
            masks = masks[order]
            classes = classes[order]
            scores = scores[order]
            
            # Resolve overlaps with polygon fitting
            final_masks, final_classes, final_scores, final_polygons, final_bboxes = [], [], [], [], []
            occupied = np.zeros(masks[0].shape, dtype=bool)
            
            for i, mask in enumerate(masks):
                polygons, bboxes = self.fit_polygon(mask)
                mask_clean = np.logical_and(mask, ~occupied)  # overlap removal
                if mask_clean.sum() > 0 and polygons:
                    final_masks.append(mask_clean)
                    final_classes.append(classes[i])
                    final_scores.append(scores[i])
                    final_polygons.append(polygons[0])  # take first polygon (outer contour)
                    final_bboxes.append(bboxes[0])
                    occupied = np.logical_or(occupied, mask_clean)
            
            # Build new Instances with filtered results
            from detectron2.structures import Instances
            import torch
            new_instances = Instances(instances.image_size)
            new_instances.pred_masks = torch.tensor(np.stack(final_masks))
            new_instances.pred_classes = torch.tensor(final_classes)
            new_instances.scores = torch.tensor(final_scores)
            instances = new_instances
            
            # Store polygon data
            for i in range(len(final_masks)):
                polygons_data.append({
                    "class": self.class_names[final_classes[i]],
                    "score": float(final_scores[i]),
                    "bbox": final_bboxes[i],          # [x1, y1, x2, y2]
                    "polygon": final_polygons[i]      # [[x,y], [x,y], ...]
                })
        
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
            scale=0.8
        )
        vis_output = v.draw_instance_predictions(instances)
        vis_image = vis_output.get_image()[:, :, ::-1]  # RGB to BGR
        
        result = {
            "predictions": predictions,
            "visualized_image": vis_image,
            "raw_outputs": outputs,
            "num_detections": len(instances)
        }
        
        # Add polygon data if available
        if polygons_data:
            result["polygons_data"] = polygons_data
        
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
                f"{base_name}_detectron2_result.jpg"
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
        
        for i, (cls_id, score, box) in enumerate(zip(
            predictions["classes"], 
            predictions["scores"], 
            predictions["boxes"]
        )):
            class_name = self.class_names[cls_id] if cls_id < len(self.class_names) else f"class_{cls_id}"
            
            if class_name not in summary["detections_by_class"]:
                summary["detections_by_class"][class_name] = 0
            summary["detections_by_class"][class_name] += 1
            
            detection_detail = {
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
            }
            
            # Add polygon data if available
            if "polygons_data" in results and i < len(results["polygons_data"]):
                detection_detail["polygon"] = results["polygons_data"][i]["polygon"]
            
            summary["detection_details"].append(detection_detail)
        
        # Add polygon data summary if available
        if "polygons_data" in results:
            summary["polygons_data"] = results["polygons_data"]
        
        return summary

def main():
    """
    Example usage of Detectron2 predictor
    """
    print("🚀 Detectron2 Floor Plan Analysis")
    
    # Initialize predictor
    predictor = Detectron2Predictor()
    
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
