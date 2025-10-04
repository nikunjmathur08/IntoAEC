#!/usr/bin/env python3
"""
Test script to demonstrate the new class filtering functionality
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

def test_class_filtering():
    """Test the class filtering functionality"""
    print("🚀 Testing Detectron2 Class Filtering")
    print("=" * 50)
    
    # Test image path (you can change this to your test image)
    test_image = "ml/demoprpoj/test-blueprint2.jpeg"
    
    if not os.path.exists(test_image):
        print(f"⚠️ Test image not found: {test_image}")
        print("Please provide a valid image path")
        return
    
    try:
        # Test 1: No filtering (default behavior)
        print("\n📋 Test 1: No class filtering")
        predictor_default = Detectron2Predictor()
        results_default = predictor_default.predict(test_image)
        summary_default = predictor_default.get_detection_summary(results_default)
        
        print(f"Total detections: {summary_default['total_detections']}")
        print(f"Classes detected: {list(summary_default['detections_by_class'].keys())}")
        
        # Test 2: Filter to keep only specific classes
        print("\n📋 Test 2: Filter to keep only 'room' and 'floor' classes")
        keep_classes = {"room", "floor"}
        predictor_filtered = Detectron2Predictor(keep_classes=keep_classes)
        results_filtered = predictor_filtered.predict(test_image)
        summary_filtered = predictor_filtered.get_detection_summary(results_filtered)
        
        print(f"Total detections after filtering: {summary_filtered['total_detections']}")
        print(f"Classes detected: {list(summary_filtered['detections_by_class'].keys())}")
        
        # Test 3: Enable polygon fitting
        print("\n📋 Test 3: Enable polygon fitting for room detection")
        predictor_polygon = Detectron2Predictor(
            keep_classes=keep_classes,
            enable_polygon_fitting=True
        )
        results_polygon = predictor_polygon.predict(test_image)
        summary_polygon = predictor_polygon.get_detection_summary(results_polygon)
        
        print(f"Total detections with polygon fitting: {summary_polygon['total_detections']}")
        print(f"Classes detected: {list(summary_polygon['detections_by_class'].keys())}")
        
        # Show polygon data if available
        if "polygons_data" in summary_polygon:
            print(f"Polygon data available for {len(summary_polygon['polygons_data'])} detections")
            for i, poly_data in enumerate(summary_polygon['polygons_data'][:2]):  # Show first 2
                print(f"  Detection {i+1}: {poly_data['class']} (score: {poly_data['score']:.3f})")
                print(f"    Polygon points: {len(poly_data['polygon'])} points")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_class_filtering()
