#!/usr/bin/env python3
"""
Test script to demonstrate class-based color visualization
Creates a sample image with various object detections and visualizes them
"""

import cv2
import numpy as np
from detection_merger import create_visualization_with_class_colors, get_class_color

def create_sample_image():
    """Create a sample floor plan image for testing"""
    # Create a blank white image
    image = np.ones((800, 1000, 3), dtype=np.uint8) * 255
    
    # Draw a simple floor plan outline
    cv2.rectangle(image, (50, 50), (950, 750), (200, 200, 200), 2)
    
    # Add some room divisions
    cv2.line(image, (500, 50), (500, 750), (200, 200, 200), 2)
    cv2.line(image, (50, 400), (950, 400), (200, 200, 200), 2)
    
    # Add text labels for context
    cv2.putText(image, "Sample Floor Plan", (400, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    return image

def create_sample_detections():
    """Create sample detections for testing"""
    detections = [
        # Walls
        {"class_name": "wall", "confidence": 0.95, 
         "bbox": {"x1": 50, "y1": 50, "x2": 950, "y2": 70}},
        {"class_name": "wall", "confidence": 0.93, 
         "bbox": {"x1": 50, "y1": 730, "x2": 950, "y2": 750}},
        
        # Windows
        {"class_name": "window", "confidence": 0.89, 
         "bbox": {"x1": 200, "y1": 50, "x2": 280, "y2": 70}},
        {"class_name": "window", "confidence": 0.87, 
         "bbox": {"x1": 700, "y1": 50, "x2": 780, "y2": 70}},
        
        # Doors
        {"class_name": "door", "confidence": 0.92, 
         "bbox": {"x1": 450, "y1": 50, "x2": 550, "y2": 70}},
        {"class_name": "door", "confidence": 0.90, 
         "bbox": {"x1": 250, "y1": 400, "x2": 300, "y2": 450}},
        
        # Furniture - Kitchen
        {"class_name": "table", "confidence": 0.85, 
         "bbox": {"x1": 150, "y1": 150, "x2": 350, "y2": 280}},
        {"class_name": "refrigerator", "confidence": 0.88, 
         "bbox": {"x1": 100, "y1": 100, "x2": 140, "y2": 180}},
        {"class_name": "sink", "confidence": 0.82, 
         "bbox": {"x1": 400, "y1": 100, "x2": 450, "y2": 140}},
        
        # Furniture - Living Room
        {"class_name": "sofa", "confidence": 0.86, 
         "bbox": {"x1": 600, "y1": 150, "x2": 850, "y2": 250}},
        {"class_name": "table", "confidence": 0.84, 
         "bbox": {"x1": 650, "y1": 280, "x2": 800, "y2": 350}},
        {"class_name": "chair", "confidence": 0.81, 
         "bbox": {"x1": 600, "y1": 280, "x2": 640, "y2": 340}},
        
        # Furniture - Bedroom
        {"class_name": "bed", "confidence": 0.90, 
         "bbox": {"x1": 150, "y1": 500, "x2": 400, "y2": 680}},
        {"class_name": "cabinet", "confidence": 0.83, 
         "bbox": {"x1": 100, "y1": 450, "x2": 140, "y2": 550}},
        
        # Bathroom
        {"class_name": "toilet", "confidence": 0.87, 
         "bbox": {"x1": 600, "y1": 500, "x2": 660, "y2": 580}},
        {"class_name": "sink", "confidence": 0.85, 
         "bbox": {"x1": 700, "y1": 500, "x2": 750, "y2": 540}},
    ]
    
    return detections

def print_color_reference():
    """Print a reference of all colors"""
    print("\n" + "="*60)
    print("CLASS-BASED COLOR REFERENCE")
    print("="*60)
    
    classes = [
        "wall", "window", "door", "table", "refrigerator",
        "toilet", "room", "bedroom", "kitchen", "living room",
        "stairs", "chair", "bed", "sofa", "sink", "cabinet", "counter"
    ]
    
    for class_name in classes:
        color = get_class_color(class_name)
        # Convert BGR to RGB for display
        rgb = (color[2], color[1], color[0])
        print(f"  {class_name:15s} - RGB{rgb} / BGR{color}")
    
    print("="*60 + "\n")

def main():
    """Main test function"""
    print("\n🎨 Testing Class-Based Color Visualization")
    print("="*60)
    
    # Print color reference
    print_color_reference()
    
    # Create sample image and detections
    print("📝 Creating sample floor plan...")
    image = create_sample_image()
    
    print("🔍 Creating sample detections...")
    detections = create_sample_detections()
    print(f"   Created {len(detections)} sample detections")
    
    # Create visualization
    print("🎨 Generating visualization with class-based colors...")
    visualized = create_visualization_with_class_colors(
        image,
        detections,
        model_name="Test Demo"
    )
    
    # Save result
    output_path = "test_color_visualization.jpg"
    cv2.imwrite(output_path, visualized)
    print(f"✅ Saved visualization to: {output_path}")
    
    # Print detection summary
    print("\n📊 Detection Summary:")
    class_counts = {}
    for det in detections:
        class_name = det["class_name"]
        class_counts[class_name] = class_counts.get(class_name, 0) + 1
    
    for class_name, count in sorted(class_counts.items()):
        color = get_class_color(class_name)
        rgb = (color[2], color[1], color[0])
        print(f"  {class_name:15s}: {count} detections - Color: RGB{rgb}")
    
    print("\n✨ Test complete! Open test_color_visualization.jpg to see results.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

