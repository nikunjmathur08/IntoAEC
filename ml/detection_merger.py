"""
Utility module for merging detections from multiple models (YOLO, Detectron2, Floorplan Analyzer)
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Tuple

def calculate_iou(box1: Dict[str, float], box2: Dict[str, float]) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes
    
    Args:
        box1: Dictionary with keys {x1, y1, x2, y2}
        box2: Dictionary with keys {x1, y1, x2, y2}
    
    Returns:
        IoU value between 0 and 1
    """
    # Get coordinates
    x1_1, y1_1, x2_1, y2_1 = box1['x1'], box1['y1'], box1['x2'], box1['y2']
    x1_2, y1_2, x2_2, y2_2 = box2['x1'], box2['y1'], box2['x2'], box2['y2']
    
    # Calculate intersection area
    x_left = max(x1_1, x1_2)
    y_top = max(y1_1, y1_2)
    x_right = min(x2_1, x2_2)
    y_bottom = min(y2_1, y2_2)
    
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    
    # Calculate union area
    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
    union_area = box1_area + box2_area - intersection_area
    
    if union_area == 0:
        return 0.0
    
    return intersection_area / union_area


def normalize_class_name(class_name: str) -> str:
    """
    Normalize class names for comparison across models
    Uses pattern matching to group similar elements automatically
    
    Args:
        class_name: Original class name from model
    
    Returns:
        Normalized class name
    """
    # Convert to lowercase and remove extra spaces
    normalized = class_name.lower().strip()
    
    # Pattern-based matching - check if the name contains certain keywords
    # This automatically handles variants like "bedroom 2", "master bedroom", etc.
    pattern_mappings = [
        # Format: (keywords_to_check, canonical_name)
        (['bedroom', 'bed room'], 'bedroom'),
        (['bathroom', 'bath room', 'restroom', 'washroom', 'wc', 'toilet', 'lavatory'], 'toilet'),
        (['kitchen', 'kitchenette'], 'kitchen'),
        (['living room', 'livingroom', 'lounge', 'family room'], 'living room'),
        (['dining room', 'diningroom', 'dining area', 'dining table'], 'dining room'),
        (['balcony', 'terrace', 'patio'], 'bedroom'),  # Group balconies with bedrooms
        (['foyer', 'entry', 'entrance', 'hallway', 'corridor'], 'bedroom'),  # Entry areas
        (['closet', 'wardrobe', 'storage'], 'cabinet'),
        (['office', 'study'], 'room'),
        (['laundry', 'utility'], 'room'),
        # COCO furniture classes
        (['couch', 'sofa'], 'sofa'),
        (['potted plant', 'plant'], 'room'),  # Group plants with generic room
    ]
    
    # Check pattern matches
    for keywords, canonical_name in pattern_mappings:
        for keyword in keywords:
            if keyword in normalized:
                return canonical_name
    
    # Exact match synonyms for specific cases
    exact_synonyms = {
        'wc': 'toilet',
        'door': 'door',
        'window': 'window',
        'wall': 'wall',
        'room': 'room',
        'table': 'table',
        'chair': 'chair',
        'bed': 'bed',
        'sofa': 'sofa',
        'refrigerator': 'refrigerator',
        'fridge': 'refrigerator',
        'sink': 'sink',
        'stairs': 'stairs',
        'staircase': 'stairs',
        'counter': 'counter',
        'countertop': 'counter',
    }
    
    # Check exact synonyms
    if normalized in exact_synonyms:
        return exact_synonyms[normalized]
    
    # If no match found, return normalized name
    return normalized


def are_same_class(class1: str, class2: str) -> bool:
    """
    Check if two class names refer to the same object type
    
    Args:
        class1: First class name
        class2: Second class name
    
    Returns:
        True if they represent the same class
    """
    return normalize_class_name(class1) == normalize_class_name(class2)


def merge_detections(
    yolo_detections: List[Dict[str, Any]],
    detectron2_detections: List[Dict[str, Any]],
    floorplan_detections: List[Dict[str, Any]],
    iou_threshold: float = 0.3,
    confidence_weight: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Merge detections from multiple models using IoU-based matching
    
    Strategy:
    1. For overlapping detections (IoU > threshold) of the same class:
       - Keep the detection with highest confidence
       - Record which models detected it
    2. For non-overlapping detections:
       - Keep all unique detections
    3. Preserve model source information
    
    Args:
        yolo_detections: List of detections from YOLO
        detectron2_detections: List of detections from Detectron2
        floorplan_detections: List of detections from Floorplan Analyzer
        iou_threshold: Threshold for considering boxes as overlapping
        confidence_weight: Optional weights for each model's confidence
    
    Returns:
        List of merged detections with source model information
    """
    if confidence_weight is None:
        confidence_weight = {
            'yolo': 1.0,
            'detectron2': 1.0,
            'floorplan': 0.9  # Slightly lower weight for OCR-based detections
        }
    
    # Prepare all detections with source information
    all_detections = []
    
    for det in yolo_detections:
        all_detections.append({
            **det,
            'source': 'yolo',
            'weighted_confidence': det['confidence'] * confidence_weight['yolo']
        })
    
    for det in detectron2_detections:
        all_detections.append({
            **det,
            'source': 'detectron2',
            'weighted_confidence': det['confidence'] * confidence_weight['detectron2']
        })
    
    for det in floorplan_detections:
        all_detections.append({
            **det,
            'source': 'floorplan',
            'weighted_confidence': det['confidence'] * confidence_weight['floorplan']
        })
    
    if not all_detections:
        return []
    
    # Sort by weighted confidence (highest first)
    all_detections.sort(key=lambda x: x['weighted_confidence'], reverse=True)
    
    merged_detections = []
    used_indices = set()
    
    for i, det1 in enumerate(all_detections):
        if i in used_indices:
            continue
        
        # Start with the current detection
        merged_det = {
            'class_name': det1['class_name'],
            'class_id': det1.get('class_id', -1),
            'confidence': det1['confidence'],
            'bbox': det1['bbox'],
            'sources': [det1['source']],
            'source_confidences': {det1['source']: det1['confidence']},
            'fuzzy_score': det1.get('fuzzy_score', None)
        }
        
        used_indices.add(i)
        
        # Check for overlapping detections from other models
        for j, det2 in enumerate(all_detections):
            if j <= i or j in used_indices:
                continue
            
            # Check if they represent the same class
            if not are_same_class(det1['class_name'], det2['class_name']):
                continue
            
            # Calculate IoU
            iou = calculate_iou(det1['bbox'], det2['bbox'])
            
            if iou > iou_threshold:
                # Merge this detection
                merged_det['sources'].append(det2['source'])
                merged_det['source_confidences'][det2['source']] = det2['confidence']
                
                # Update confidence to average of all sources
                confidences = list(merged_det['source_confidences'].values())
                merged_det['confidence'] = sum(confidences) / len(confidences)
                
                # If fuzzy_score exists in either, keep the higher one
                if det2.get('fuzzy_score') is not None:
                    if merged_det['fuzzy_score'] is None:
                        merged_det['fuzzy_score'] = det2['fuzzy_score']
                    else:
                        merged_det['fuzzy_score'] = max(merged_det['fuzzy_score'], det2['fuzzy_score'])
                
                used_indices.add(j)
        
        # Normalize the class name for consistency
        merged_det['class_name'] = normalize_class_name(merged_det['class_name']).title()
        merged_det['num_models_detected'] = len(merged_det['sources'])
        
        merged_detections.append(merged_det)
    
    return merged_detections


def create_visualization_with_class_colors(
    image_path: str,
    detections: List[Dict[str, Any]],
    model_name: str = ""
) -> np.ndarray:
    """
    Create a visualization with class-based colors for any model's detections
    
    Args:
        image_path: Path to the original image or numpy array
        detections: List of detections with bbox and class_name
        model_name: Optional name of the model (for display)
    
    Returns:
        Annotated image as numpy array
    """
    # Read image
    if isinstance(image_path, str):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")
    else:
        # Assume it's already a numpy array
        image = image_path.copy()
    
    for det in detections:
        bbox = det['bbox']
        x1, y1, x2, y2 = int(bbox['x1']), int(bbox['y1']), int(bbox['x2']), int(bbox['y2'])
        
        # Get class-based color
        color = get_class_color(det['class_name'])
        
        # Draw bounding box
        thickness = 2
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
        
        # Prepare label
        label = f"{det['class_name']} {det['confidence']:.2f}"
        
        # Draw label background
        (label_width, label_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
        )
        cv2.rectangle(
            image,
            (x1, y1 - label_height - baseline - 5),
            (x1 + label_width, y1),
            color,
            -1
        )
        
        # Draw label text
        cv2.putText(
            image,
            label,
            (x1, y1 - baseline - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2
        )
    
    # Add legend with detected classes
    detected_classes = set()
    for det in detections:
        detected_classes.add(normalize_class_name(det['class_name']))
    
    # Build legend for detected classes
        class_legend_map = {
            'wall': ("Wall", (0, 0, 255)),
            'window': ("Window", (255, 0, 0)),
            'door': ("Door", (0, 255, 0)),
            'table': ("Table", (0, 165, 255)),
            'refrigerator': ("Refrigerator", (128, 0, 128)),
            'toilet': ("Toilet/Bathroom", (138, 62, 2)),
        'room': ("Room", (203, 192, 255)),
        'bedroom': ("Bedroom", (147, 20, 255)),
        'kitchen': ("Kitchen", (0, 140, 255)),
        'living room': ("Living Room", (30, 105, 210)),
        'stairs': ("Stairs", (128, 128, 128)),
        'chair': ("Chair", (180, 105, 255)),
        'bed': ("Bed", (255, 191, 0)),
        'sofa': ("Sofa", (0, 69, 255)),
        'sink': ("Sink", (226, 43, 138)),
        'cabinet': ("Cabinet", (19, 69, 139)),
        'counter': ("Counter", (92, 92, 205)),
    }
    
    legend_items = []
    for class_key in detected_classes:
        if class_key in class_legend_map:
            legend_items.append(class_legend_map[class_key])
    
    # Add legend to image
    if legend_items:
        legend_y = 30
        # Add model name if provided
        if model_name:
            cv2.putText(image, f"Model: {model_name}", (10, legend_y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            legend_y += 25
        
        for label, color in legend_items:
            cv2.rectangle(image, (10, legend_y - 15), (30, legend_y - 5), color, -1)
            cv2.putText(image, label, (35, legend_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            legend_y += 20
    
    return image


def get_class_color(class_name: str) -> Tuple[int, int, int]:
    """
    Get color for a class based on object type
    Colors are in BGR format for OpenCV
    
    Args:
        class_name: Name of the detected class
    
    Returns:
        BGR color tuple
    """
    # Normalize class name for matching
    normalized = normalize_class_name(class_name)
    
    # Class-based color mapping (BGR format)
    class_colors = {
        'wall': (0, 0, 255),          # Red for walls
        'window': (255, 0, 0),        # Blue for windows
        'door': (0, 255, 0),          # Green for doors
        'table': (0, 165, 255),       # Orange for tables
        'refrigerator': (128, 0, 128),# Purple for refrigerators
        'fridge': (128, 0, 128),      # Purple for refrigerators (synonym)
        'toilet': (138, 62, 2),       # Navy Blue for toilets/bathrooms (BGR: #023e8a)
        'bathroom': (138, 62, 2),     # Navy Blue for bathrooms
        'room': (203, 192, 255),      # Light pink for rooms
        'bedroom': (147, 20, 255),    # Deep pink for bedrooms
        'kitchen': (0, 140, 255),     # Dark orange for kitchen
        'living room': (30, 105, 210),# Brown for living room
        'stairs': (128, 128, 128),    # Gray for stairs
        'chair': (180, 105, 255),     # Hot pink for chairs
        'bed': (255, 191, 0),         # Deep sky blue for beds
        'sofa': (0, 69, 255),         # Orange red for sofas
        'sink': (226, 43, 138),       # Blue violet for sinks
        'cabinet': (19, 69, 139),     # Saddle brown for cabinets
        'counter': (92, 92, 205),     # Indian red for counters
    }
    
    # Return color for class, or black if not found
    return class_colors.get(normalized, (0, 0, 0))


def create_combined_visualization(
    image_path: str,
    merged_detections: List[Dict[str, Any]],
    show_model_tags: bool = True,
    use_class_colors: bool = True
) -> np.ndarray:
    """
    Create a combined visualization showing all merged detections
    
    Args:
        image_path: Path to the original image
        merged_detections: List of merged detections
        show_model_tags: Whether to show which models detected each object
        use_class_colors: If True, use class-based colors; if False, use model-based colors
    
    Returns:
        Annotated image as numpy array
    """
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image from {image_path}")
    
    # Color mapping for different model combinations (if not using class colors)
    model_color_map = {
        ('yolo',): (255, 0, 0),  # Blue - YOLO only
        ('detectron2',): (255, 0, 255),  # Magenta - Detectron2 only
        ('floorplan',): (0, 255, 0),  # Green - Floorplan only
        ('yolo', 'detectron2'): (255, 165, 0),  # Orange - YOLO + Detectron2
        ('yolo', 'floorplan'): (0, 255, 255),  # Yellow - YOLO + Floorplan
        ('detectron2', 'floorplan'): (255, 255, 0),  # Cyan - Detectron2 + Floorplan
        ('yolo', 'detectron2', 'floorplan'): (0, 0, 255),  # Red - All three
    }
    
    for det in merged_detections:
        bbox = det['bbox']
        x1, y1, x2, y2 = int(bbox['x1']), int(bbox['y1']), int(bbox['x2']), int(bbox['y2'])
        
        # Determine color based on class or source models
        if use_class_colors:
            color = get_class_color(det['class_name'])
        else:
            sources_tuple = tuple(sorted(det['sources']))
            color = model_color_map.get(sources_tuple, (128, 128, 128))  # Gray as default
        
        # Draw bounding box (thicker if detected by multiple models)
        thickness = 2 if det['num_models_detected'] == 1 else 3
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
        
        # Prepare label
        label = f"{det['class_name']}"
        
        if show_model_tags and det['num_models_detected'] > 1:
            label += f" ({det['num_models_detected']} models)"
        
        # Add confidence
        label += f" {det['confidence']:.2f}"
        
        # Draw label background
        (label_width, label_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
        )
        cv2.rectangle(
            image,
            (x1, y1 - label_height - baseline - 5),
            (x1 + label_width, y1),
            color,
            -1
        )
        
        # Draw label text
        cv2.putText(
            image,
            label,
            (x1, y1 - baseline - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2
        )
    
    # Add legend based on color mode
    if use_class_colors:
        # Show class-based color legend with only classes that are detected
        detected_classes = set()
        for det in merged_detections:
            detected_classes.add(normalize_class_name(det['class_name']))
        
        # Build legend for detected classes
        legend_items = []
        class_legend_map = {
            'wall': ("Wall", (0, 0, 255)),
            'window': ("Window", (255, 0, 0)),
            'door': ("Door", (0, 255, 0)),
            'table': ("Table", (0, 165, 255)),
            'refrigerator': ("Refrigerator", (128, 0, 128)),
            'toilet': ("Toilet/Bathroom", (138, 62, 2)),
            'room': ("Room", (203, 192, 255)),
            'bedroom': ("Bedroom", (147, 20, 255)),
            'kitchen': ("Kitchen", (0, 140, 255)),
            'living room': ("Living Room", (30, 105, 210)),
            'stairs': ("Stairs", (128, 128, 128)),
            'chair': ("Chair", (180, 105, 255)),
            'bed': ("Bed", (255, 191, 0)),
            'sofa': ("Sofa", (0, 69, 255)),
            'sink': ("Sink", (226, 43, 138)),
            'cabinet': ("Cabinet", (19, 69, 139)),
            'counter': ("Counter", (92, 92, 205)),
        }
        
        for class_key in detected_classes:
            if class_key in class_legend_map:
                legend_items.append(class_legend_map[class_key])
        
        # Add legend to image
        if legend_items:
            legend_y = 30
            for label, color in legend_items:
                cv2.rectangle(image, (10, legend_y - 15), (30, legend_y - 5), color, -1)
                cv2.putText(image, label, (35, legend_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                legend_y += 20
    else:
        # Show model-based color legend
        legend_y = 30
        legend_items = [
            ("All 3 Models", (0, 0, 255)),
            ("YOLO + D2", (255, 165, 0)),
            ("YOLO + FP", (0, 255, 255)),
            ("D2 + FP", (255, 255, 0)),
            ("YOLO Only", (255, 0, 0)),
            ("D2 Only", (255, 0, 255)),
            ("FP Only", (0, 255, 0)),
        ]
        
        for label, color in legend_items:
            cv2.rectangle(image, (10, legend_y - 15), (30, legend_y - 5), color, -1)
            cv2.putText(image, label, (35, legend_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            legend_y += 20
    
    return image


def get_combined_summary(merged_detections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a summary of the combined analysis
    
    Args:
        merged_detections: List of merged detections
    
    Returns:
        Summary dictionary with statistics
    """
    detections_by_class = {}
    detections_by_source_count = {1: 0, 2: 0, 3: 0}
    model_contributions = {'yolo': 0, 'detectron2': 0, 'floorplan': 0}
    
    for det in merged_detections:
        # Count by class
        class_name = det['class_name']
        if class_name not in detections_by_class:
            detections_by_class[class_name] = 0
        detections_by_class[class_name] += 1
        
        # Count by number of models
        num_models = det['num_models_detected']
        detections_by_source_count[num_models] = detections_by_source_count.get(num_models, 0) + 1
        
        # Count model contributions
        for source in det['sources']:
            model_contributions[source] += 1
    
    return {
        'total_detections': len(merged_detections),
        'detections_by_class': detections_by_class,
        'detections_by_source_count': detections_by_source_count,
        'model_contributions': model_contributions,
        'detection_details': merged_detections,
        'unique_classes': len(detections_by_class)
    }

