#!/usr/bin/env python3
"""
Example script showing how to use the new class filtering functionality
Similar to the user's original code but using the modified Detectron2Predictor
"""

import os
import sys
import json

# Add the ml directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "ml"))

try:
    from detectron2_inference import Detectron2Predictor
    print("✅ Detectron2 module loaded successfully")
except ImportError as e:
    print(f"❌ Could not import Detectron2: {e}")
    sys.exit(1)

def main():
    """
    Example usage similar to the user's original code
    """
    print("🚀 Detectron2 Class Filtering Example")
    print("=" * 50)
    
    # Define classes to keep (similar to user's KEEP_CLASSES)
    KEEP_CLASSES = {"floor", "room"}  # Adjust based on your class names
    
    # Initialize predictor with class filtering and polygon fitting
    predictor = Detectron2Predictor(
        keep_classes=KEEP_CLASSES,
        enable_polygon_fitting=True
    )
    
    # Test image path
    test_image = "ml/demoprpoj/test-blueprint2.jpeg"
    
    if not os.path.exists(test_image):
        print(f"⚠️ Test image not found: {test_image}")
        print("Please provide a valid image path")
        return
    
    try:
        # Run prediction with filtering
        print(f"🔍 Running inference on: {test_image}")
        results = predictor.predict(test_image)
        
        # Get summary
        summary = predictor.get_detection_summary(results)
        
        print(f"\n📊 Detection Summary:")
        print(f"Total detections: {summary['total_detections']}")
        print(f"Detections by class: {summary['detections_by_class']}")
        
        # Show detailed results
        print(f"\n📝 Detailed results:")
        for detection in summary['detection_details']:
            print(f"  - {detection['class_name']}: {detection['confidence']:.3f} confidence")
            if 'polygon' in detection:
                print(f"    Polygon points: {len(detection['polygon'])} points")
        
        # Save JSON output (similar to user's original code)
        if "polygons_data" in summary:
            json_output = summary["polygons_data"]
            
            with open("detected_polygons.json", "w") as f:
                json.dump(json_output, f, indent=4)
            
            print(f"\n💾 Exported {len(json_output)} polygons to detected_polygons.json")
            
            # Show first polygon as example
            if json_output:
                first_poly = json_output[0]
                print(f"\n📐 Example polygon:")
                print(f"  Class: {first_poly['class']}")
                print(f"  Score: {first_poly['score']:.3f}")
                print(f"  Bbox: {first_poly['bbox']}")
                print(f"  Polygon points: {len(first_poly['polygon'])} points")
        
        # Save visualization
        output_image_path = "result_polygons.png"
        import cv2
        cv2.imwrite(output_image_path, results["visualized_image"])
        print(f"\n💾 Saved visualization: {output_image_path}")
        
        print(f"\n✅ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
