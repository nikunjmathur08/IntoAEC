"""
Floorplan Analyzer Wrapper
Integrates OCR-based floor plan analysis with contour detection and area calculation
"""
import sys
import os
import cv2
import numpy as np

# Add floorplan_analyzer to path
sys.path.append(os.path.join(os.path.dirname(__file__), "floorplan_analyzer"))

from floorplan_analyzer.ocr_utils import perform_ocr, auto_estimate_scale
from floorplan_analyzer.line_utils import detect_contours, calculate_area
from floorplan_analyzer.fuzzy_wuzzy import correct_labels

class FloorplanAnalyzer:
    def __init__(self, min_conf=0.4):
        """
        Initialize the Floorplan Analyzer
        
        Args:
            min_conf: Minimum confidence threshold for OCR detections
        """
        self.min_conf = min_conf
        print(f"✅ Floorplan Analyzer initialized (OCR + Contour Detection)")
    
    def analyze(self, image_path: str):
        """
        Analyze a floor plan image
        
        Args:
            image_path: Path to the floor plan image
            
        Returns:
            dict with analysis results including labels, contours, and visualized image
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Perform OCR to detect text labels
        labels = perform_ocr(image, min_conf=self.min_conf)
        labels = correct_labels(labels)
        
        # Detect contours (room boundaries)
        contours = detect_contours(image)
        
        # Auto-estimate scale from OCR results
        auto_scale = auto_estimate_scale(labels)
        px_per_unit = auto_scale if auto_scale else None
        
        # Calculate areas
        areas = []
        for i, cnt in enumerate(contours):
            area_pixels = float(cv2.contourArea(cnt))
            area_units = calculate_area(cnt, px_per_unit)
            areas.append({
                "contour_id": i,
                "area_pixels": area_pixels,
                "area_units": area_units
            })
        
        # Create visualization
        visualized_image = self._create_visualization(image.copy(), labels, contours)
        
        results = {
            "labels": labels,
            "num_labels": len(labels),
            "contours": len(contours),
            "areas": areas,
            "scale_px_per_unit": px_per_unit,
            "visualized_image": visualized_image
        }
        
        return results
    
    def _create_visualization(self, image, labels, contours):
        """
        Create visualization with labels and contours overlaid
        
        Args:
            image: Original image (BGR)
            labels: List of OCR labels with positions
            contours: List of detected contours
            
        Returns:
            Visualized image with annotations
        """
        # Draw contours in blue
        cv2.drawContours(image, contours, -1, (255, 0, 0), 2)
        
        # Draw labels with bounding boxes
        for label in labels:
            text = label.get("corrected_text", label.get("text", ""))
            bbox = label.get("bbox", [])
            conf = label.get("confidence", 0)
            fuzzy_score = label.get("fuzzy_score", 0)
            
            if bbox:
                # Draw bounding box for text
                pts = np.array(bbox).astype(int)
                cv2.polylines(image, [pts], True, (0, 255, 0), 2)
                
                # Put text label
                x, y = int(pts[0][0]), int(pts[0][1])
                
                # Color based on fuzzy score (how well it matched known labels)
                if fuzzy_score >= 75:
                    color = (0, 255, 0)  # Green for good match
                elif fuzzy_score >= 50:
                    color = (0, 165, 255)  # Orange for partial match
                else:
                    color = (0, 0, 255)  # Red for poor match
                
                # Add background rectangle for text
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(image, (x, y - text_size[1] - 10), 
                             (x + text_size[0], y), (0, 0, 0), -1)
                
                cv2.putText(image, text, (x, y - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Add confidence score
                conf_text = f"{int(conf * 100)}%"
                cv2.putText(image, conf_text, (x, y + 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return image
    
    def get_detection_summary(self, results):
        """
        Create a summary of detections compatible with the frontend format
        
        Args:
            results: Results from analyze()
            
        Returns:
            Dictionary with detection summary
        """
        detections = []
        
        # Add OCR labels as detections
        for label in results["labels"]:
            detections.append({
                "class_id": -1,  # OCR doesn't have class IDs
                "class_name": label.get("corrected_text", label.get("text", "Unknown")),
                "confidence": label.get("confidence", 0.0),
                "bbox": {
                    "x1": int(label["position"]["x"]),
                    "y1": int(label["position"]["y"]),
                    "x2": int(label["position"]["x"]) + 50,  # Approximate width
                    "y2": int(label["position"]["y"]) + 20,  # Approximate height
                    "width": 50,
                    "height": 20
                },
                "fuzzy_score": label.get("fuzzy_score", 0)
            })
        
        # Count detections by class
        detections_by_class = {}
        for det in detections:
            class_name = det["class_name"]
            detections_by_class[class_name] = detections_by_class.get(class_name, 0) + 1
        
        return {
            "detection_details": detections,
            "total_detections": len(detections),
            "detections_by_class": detections_by_class,
            "num_contours": results["contours"],
            "scale_info": {
                "px_per_unit": results.get("scale_px_per_unit"),
                "has_scale": results.get("scale_px_per_unit") is not None
            }
        }

