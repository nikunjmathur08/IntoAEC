# """
# Window Detection Module
# Uses computer vision techniques to detect windows in floor plan images
# """
# import cv2
# import numpy as np
# from typing import List, Dict, Any, Tuple

# def detect_windows(image_path: str, min_area: int = 200, max_area: int = 8000) -> List[Dict[str, Any]]:
#     """
#     Detect windows in a floor plan image using improved computer vision techniques
    
#     Args:
#         image_path: Path to the floor plan image
#         min_area: Minimum area for window detection (pixels)
#         max_area: Maximum area for window detection (pixels)
    
#     Returns:
#         List of window detections with bounding boxes and confidence scores
#     """
#     # Load image
#     image = cv2.imread(image_path)
#     if image is None:
#         print(f"Error: Could not load image {image_path}")
#         return []
    
#     # Convert to grayscale
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
#     # Apply stronger Gaussian blur to reduce noise
#     blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    
#     # Use more conservative Canny edge detection for cleaner edges
#     edges = cv2.Canny(blurred, 80, 200)
    
#     # Apply morphological operations to clean up edges
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
#     edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
#     # Find contours
#     contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     # Detect walls first to improve window detection
#     wall_regions = detect_wall_regions(gray)
    
#     window_detections = []
    
#     for contour in contours:
#         # Calculate contour area
#         area = cv2.contourArea(contour)
        
#         # Filter by area - more restrictive for floor plan windows
#         if area < min_area or area > max_area:
#             continue
        
#         # Get bounding rectangle
#         x, y, w, h = cv2.boundingRect(contour)
        
#         # Calculate aspect ratio
#         aspect_ratio = w / h if h > 0 else 0
        
#         # More restrictive window characteristics for floor plans:
#         # - Windows are typically rectangular with specific aspect ratios
#         # - Should be near walls
#         # - Should have reasonable size for floor plan scale
        
#         if 1.2 <= aspect_ratio <= 4.0:  # More restrictive aspect ratio
#             # Calculate confidence based on improved window characteristics
#             confidence = calculate_improved_window_confidence(
#                 contour, x, y, w, h, aspect_ratio, image.shape, wall_regions
#             )
            
#             if confidence > 0.5:  # Higher confidence threshold
#                 detection = {
#                     "class_id": 999,  # Special ID for windows
#                     "class_name": "window",
#                     "confidence": round(confidence, 4),
#                     "bbox": {
#                         "x1": int(x),
#                         "y1": int(y),
#                         "x2": int(x + w),
#                         "y2": int(y + h),
#                         "width": int(w),
#                         "height": int(h)
#                     },
#                     "area": int(area),
#                     "aspect_ratio": round(aspect_ratio, 2)
#                 }
#                 window_detections.append(detection)
    
#     # Sort by confidence (highest first)
#     window_detections.sort(key=lambda x: x["confidence"], reverse=True)
    
#     # Remove overlapping detections (keep highest confidence)
#     filtered_detections = remove_overlapping_windows(window_detections, iou_threshold=0.2)
    
#     print(f"🔍 Window Detection: Found {len(filtered_detections)} potential windows")
#     return filtered_detections

# def detect_wall_regions(gray_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
#     """
#     Detect wall regions in the floor plan to help with window detection
    
#     Args:
#         gray_image: Grayscale image of the floor plan
    
#     Returns:
#         List of wall regions as (x, y, w, h) tuples
#     """
#     # Use adaptive thresholding to detect walls (typically darker/thicker lines)
#     thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
#                                    cv2.THRESH_BINARY_INV, 11, 2)
    
#     # Apply morphological operations to connect wall segments
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
#     thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
#     # Find contours of wall regions
#     contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     wall_regions = []
#     for contour in contours:
#         area = cv2.contourArea(contour)
#         if area > 500:  # Filter out small noise
#             x, y, w, h = cv2.boundingRect(contour)
#             wall_regions.append((x, y, w, h))
    
#     return wall_regions

# def calculate_improved_window_confidence(contour: np.ndarray, x: int, y: int, w: int, h: int, 
#                                        aspect_ratio: float, image_shape: Tuple[int, int, int],
#                                        wall_regions: List[Tuple[int, int, int, int]]) -> float:
#     """
#     Calculate improved confidence score for a potential window detection
    
#     Args:
#         contour: Contour of the potential window
#         x, y, w, h: Bounding box coordinates and dimensions
#         aspect_ratio: Aspect ratio of the bounding box
#         image_shape: Shape of the original image (height, width, channels)
#         wall_regions: List of detected wall regions
    
#     Returns:
#         Confidence score between 0 and 1
#     """
#     confidence = 0.0
#     height, width = image_shape[:2]
    
#     # 1. Aspect ratio score (windows are typically rectangular, not square)
#     if 1.5 <= aspect_ratio <= 3.5:  # Good window aspect ratio for floor plans
#         confidence += 0.25
#     elif 1.2 <= aspect_ratio <= 4.0:  # Acceptable aspect ratio
#         confidence += 0.15
    
#     # 2. Size score (windows should be reasonably sized for floor plans)
#     area = w * h
#     if 300 <= area <= 3000:  # Good window size for floor plans
#         confidence += 0.25
#     elif 200 <= area <= 5000:  # Acceptable size
#         confidence += 0.15
    
#     # 3. Wall proximity score (windows should be near walls)
#     wall_proximity_score = calculate_wall_proximity(x, y, w, h, wall_regions)
#     confidence += wall_proximity_score * 0.3
    
#     # 4. Contour regularity score (windows have regular rectangular shapes)
#     perimeter = cv2.arcLength(contour, True)
#     if perimeter > 0:
#         rect_area = w * h
#         contour_area = cv2.contourArea(contour)
#         if rect_area > 0:
#             regularity = contour_area / rect_area
#             if regularity > 0.85:  # Very regular shape
#                 confidence += 0.15
#             elif regularity > 0.75:  # Somewhat regular
#                 confidence += 0.1
    
#     # 5. Position in image (windows are often in the middle to upper portion)
#     relative_y = y / height
#     if 0.1 <= relative_y <= 0.8:  # Good vertical position
#         confidence += 0.05
    
#     # 6. Edge alignment score (windows often align with image edges or walls)
#     edge_alignment_score = calculate_edge_alignment(x, y, w, h, width, height)
#     confidence += edge_alignment_score * 0.1
    
#     return min(confidence, 1.0)  # Cap at 1.0

# def calculate_wall_proximity(x: int, y: int, w: int, h: int, 
#                            wall_regions: List[Tuple[int, int, int, int]]) -> float:
#     """
#     Calculate how close a potential window is to detected walls
    
#     Args:
#         x, y, w, h: Bounding box of potential window
#         wall_regions: List of wall regions as (x, y, w, h) tuples
    
#     Returns:
#         Proximity score between 0 and 1
#     """
#     if not wall_regions:
#         return 0.0
    
#     window_center_x = x + w // 2
#     window_center_y = y + h // 2
    
#     min_distance = float('inf')
    
#     for wall_x, wall_y, wall_w, wall_h in wall_regions:
#         wall_center_x = wall_x + wall_w // 2
#         wall_center_y = wall_y + wall_h // 2
        
#         # Calculate distance between centers
#         distance = np.sqrt((window_center_x - wall_center_x)**2 + (window_center_y - wall_center_y)**2)
#         min_distance = min(min_distance, distance)
    
#     # Convert distance to score (closer = higher score)
#     # Windows within 50 pixels of walls get high score
#     if min_distance <= 50:
#         return 1.0
#     elif min_distance <= 100:
#         return 0.7
#     elif min_distance <= 200:
#         return 0.4
#     else:
#         return 0.0

# def calculate_edge_alignment(x: int, y: int, w: int, h: int, 
#                            image_width: int, image_height: int) -> float:
#     """
#     Calculate how well a potential window aligns with image edges or common wall positions
    
#     Args:
#         x, y, w, h: Bounding box of potential window
#         image_width, image_height: Dimensions of the image
    
#     Returns:
#         Alignment score between 0 and 1
#     """
#     alignment_score = 0.0
    
#     # Check horizontal alignment (windows often align with top/bottom edges)
#     if y < 20 or (y + h) > (image_height - 20):  # Near top or bottom edge
#         alignment_score += 0.5
    
#     # Check vertical alignment (windows often align with left/right edges)
#     if x < 20 or (x + w) > (image_width - 20):  # Near left or right edge
#         alignment_score += 0.5
    
#     # Check if window is positioned at common wall locations (quarter positions)
#     quarter_width = image_width // 4
#     quarter_height = image_height // 4
    
#     if (x < quarter_width or x > 3 * quarter_width or 
#         y < quarter_height or y > 3 * quarter_height):
#         alignment_score += 0.3
    
#     return min(alignment_score, 1.0)

# def detect_window_patterns(gray_image: np.ndarray) -> List[Dict[str, Any]]:
#     """
#     Detect specific window patterns commonly found in floor plans
    
#     Args:
#         gray_image: Grayscale image of the floor plan
    
#     Returns:
#         List of detected window patterns
#     """
#     window_patterns = []
    
#     # Detect horizontal window lines (common in floor plans)
#     horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
#     horizontal_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, horizontal_kernel)
    
#     # Detect vertical window lines
#     vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
#     vertical_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, vertical_kernel)
    
#     # Combine horizontal and vertical lines
#     window_lines = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0)
    
#     # Find contours of window line patterns
#     contours, _ = cv2.findContours(window_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     for contour in contours:
#         area = cv2.contourArea(contour)
#         if 100 < area < 2000:  # Reasonable size for window patterns
#             x, y, w, h = cv2.boundingRect(contour)
#             aspect_ratio = w / h if h > 0 else 0
            
#             # Check if it looks like a window pattern
#             if 1.5 <= aspect_ratio <= 5.0:  # Windows are typically wider than tall
#                 window_patterns.append({
#                     'bbox': (x, y, w, h),
#                     'area': area,
#                     'aspect_ratio': aspect_ratio,
#                     'type': 'line_pattern'
#                 })
    
#     return window_patterns

# def calculate_window_confidence(contour: np.ndarray, x: int, y: int, w: int, h: int, 
#                               aspect_ratio: float, image_shape: Tuple[int, int, int]) -> float:
#     """
#     Calculate confidence score for a potential window detection
    
#     Args:
#         contour: Contour of the potential window
#         x, y, w, h: Bounding box coordinates and dimensions
#         aspect_ratio: Aspect ratio of the bounding box
#         image_shape: Shape of the original image (height, width, channels)
    
#     Returns:
#         Confidence score between 0 and 1
#     """
#     confidence = 0.0
#     height, width = image_shape[:2]
    
#     # 1. Aspect ratio score (windows are typically rectangular)
#     if 1.5 <= aspect_ratio <= 2.5:  # Good window aspect ratio
#         confidence += 0.3
#     elif 1.0 <= aspect_ratio <= 3.0:  # Acceptable aspect ratio
#         confidence += 0.2
    
#     # 2. Size score (windows should be reasonably sized)
#     area = w * h
#     if 200 <= area <= 5000:  # Good window size
#         confidence += 0.2
#     elif 100 <= area <= 10000:  # Acceptable size
#         confidence += 0.1
    
#     # 3. Location score (windows are often near edges or walls)
#     edge_distance = min(x, y, width - x - w, height - y - h)
#     if edge_distance < 50:  # Near edge (likely a wall)
#         confidence += 0.2
#     elif edge_distance < 100:  # Somewhat near edge
#         confidence += 0.1
    
#     # 4. Contour regularity score (windows have regular shapes)
#     perimeter = cv2.arcLength(contour, True)
#     if perimeter > 0:
#         # Calculate how close the contour is to a perfect rectangle
#         rect_area = w * h
#         contour_area = cv2.contourArea(contour)
#         if rect_area > 0:
#             regularity = contour_area / rect_area
#             if regularity > 0.8:  # Very regular shape
#                 confidence += 0.2
#             elif regularity > 0.6:  # Somewhat regular
#                 confidence += 0.1
    
#     # 5. Position in image (windows are often in the middle to upper portion)
#     relative_y = y / height
#     if 0.1 <= relative_y <= 0.7:  # Good vertical position
#         confidence += 0.1
    
#     return min(confidence, 1.0)  # Cap at 1.0

# def remove_overlapping_windows(detections: List[Dict[str, Any]], iou_threshold: float = 0.3) -> List[Dict[str, Any]]:
#     """
#     Remove overlapping window detections, keeping the one with highest confidence
    
#     Args:
#         detections: List of window detections
#         iou_threshold: IoU threshold for considering detections as overlapping
    
#     Returns:
#         Filtered list of non-overlapping detections
#     """
#     if len(detections) <= 1:
#         return detections
    
#     # Sort by confidence (highest first)
#     sorted_detections = sorted(detections, key=lambda x: x["confidence"], reverse=True)
    
#     filtered = []
#     used_indices = set()
    
#     for i, det1 in enumerate(sorted_detections):
#         if i in used_indices:
#             continue
        
#         filtered.append(det1)
#         used_indices.add(i)
        
#         # Check for overlaps with remaining detections
#         for j, det2 in enumerate(sorted_detections[i+1:], i+1):
#             if j in used_indices:
#                 continue
            
#             # Calculate IoU
#             iou = calculate_iou(det1["bbox"], det2["bbox"])
#             if iou > iou_threshold:
#                 used_indices.add(j)
    
#     return filtered

# def calculate_iou(box1: Dict[str, int], box2: Dict[str, int]) -> float:
#     """
#     Calculate Intersection over Union (IoU) of two bounding boxes
    
#     Args:
#         box1, box2: Bounding boxes with x1, y1, x2, y2 coordinates
    
#     Returns:
#         IoU value between 0 and 1
#     """
#     # Calculate intersection coordinates
#     x1 = max(box1["x1"], box2["x1"])
#     y1 = max(box1["y1"], box2["y1"])
#     x2 = min(box1["x2"], box2["x2"])
#     y2 = min(box1["y2"], box2["y2"])
    
#     # Check if there's an intersection
#     if x2 <= x1 or y2 <= y1:
#         return 0.0
    
#     # Calculate intersection area
#     intersection_area = (x2 - x1) * (y2 - y1)
    
#     # Calculate union area
#     box1_area = (box1["x2"] - box1["x1"]) * (box1["y2"] - box1["y1"])
#     box2_area = (box2["x2"] - box2["x1"]) * (box2["y2"] - box2["y1"])
#     union_area = box1_area + box2_area - intersection_area
    
#     # Calculate IoU
#     if union_area == 0:
#         return 0.0
    
#     return intersection_area / union_area

# def create_window_visualization(image_path: str, window_detections: List[Dict[str, Any]]) -> np.ndarray:
#     """
#     Create visualization of detected windows on the original image
    
#     Args:
#         image_path: Path to the original image
#         window_detections: List of window detections
    
#     Returns:
#         Image with window detections visualized
#     """
#     image = cv2.imread(image_path)
#     if image is None:
#         return None
    
#     # Draw each window detection
#     for detection in window_detections:
#         bbox = detection["bbox"]
#         confidence = detection["confidence"]
        
#         # Draw bounding box in blue (window color)
#         cv2.rectangle(image, (bbox["x1"], bbox["y1"]), (bbox["x2"], bbox["y2"]), (255, 0, 0), 2)
        
#         # Draw confidence score
#         label = f"Window: {confidence:.2f}"
#         cv2.putText(image, label, (bbox["x1"], bbox["y1"] - 10), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
#     return image

# # Test function
# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) > 1:
#         image_path = sys.argv[1]
#         windows = detect_windows(image_path)
#         print(f"Detected {len(windows)} windows:")
#         for i, window in enumerate(windows):
#             print(f"  {i+1}. Confidence: {window['confidence']:.3f}, "
#                   f"BBox: ({window['bbox']['x1']}, {window['bbox']['y1']}, "
#                   f"{window['bbox']['x2']}, {window['bbox']['y2']})")
#     else:
#         print("Usage: python window_detector.py <image_path>")
