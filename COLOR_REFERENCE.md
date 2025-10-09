# Bounding Box Color Reference Guide

## Quick Reference Table

| Object Type | Color Name | RGB Value | BGR Value (OpenCV) | Hex Color |
|------------|-----------|-----------|-------------------|-----------|
| Wall | Red | (255, 0, 0) | (0, 0, 255) | #FF0000 |
| Window | Blue | (0, 0, 255) | (255, 0, 0) | #0000FF |
| Door | Green | (0, 255, 0) | (0, 255, 0) | #00FF00 |
| Table | Orange | (255, 165, 0) | (0, 165, 255) | #FFA500 |
| Refrigerator | Purple | (128, 0, 128) | (128, 0, 128) | #800080 |
| Toilet/Bathroom | Cyan | (0, 255, 255) | (255, 255, 0) | #00FFFF |
| Room | Light Pink | (255, 192, 203) | (203, 192, 255) | #FFC0CB |
| Bedroom | Deep Pink | (255, 20, 147) | (147, 20, 255) | #FF1493 |
| Kitchen | Dark Orange | (255, 140, 0) | (0, 140, 255) | #FF8C00 |
| Living Room | Brown | (210, 105, 30) | (30, 105, 210) | #D2691E |
| Stairs | Gray | (128, 128, 128) | (128, 128, 128) | #808080 |
| Chair | Hot Pink | (255, 105, 180) | (180, 105, 255) | #FF69B4 |
| Bed | Deep Sky Blue | (0, 191, 255) | (255, 191, 0) | #00BFFF |
| Sofa | Orange Red | (255, 69, 0) | (0, 69, 255) | #FF4500 |
| Sink | Blue Violet | (138, 43, 226) | (226, 43, 138) | #8A2B E2 |
| Cabinet | Saddle Brown | (139, 69, 19) | (19, 69, 139) | #8B4513 |
| Counter | Indian Red | (205, 92, 92) | (92, 92, 205) | #CD5C5C |
| Unknown/Other | White | (255, 255, 255) | (255, 255, 255) | #FFFFFF |

## Visual Color Guide

### Primary Structural Elements
- **Wall** - Red (most prominent structural element)
- **Window** - Blue (openings in walls)
- **Door** - Green (entries/exits)

### Furniture
- **Table** - Orange
- **Chair** - Hot Pink
- **Bed** - Deep Sky Blue
- **Sofa** - Orange Red

### Appliances
- **Refrigerator** - Purple
- **Sink** - Blue Violet

### Room Types
- **Room** (Generic) - Light Pink
- **Bedroom** - Deep Pink
- **Kitchen** - Dark Orange
- **Living Room** - Brown
- **Toilet/Bathroom** - Navy Blue

### Storage & Surfaces
- **Cabinet** - Saddle Brown
- **Counter** - Indian Red

### Other
- **Stairs** - Gray
- **Unknown** - Black

## Color Coding Rationale

1. **Wall (Red)** - Most important structural element, red catches attention
2. **Window (Blue)** - Blue represents sky/outside view
3. **Door (Green)** - Green for "go" / entry points
4. **Table (Orange)** - Warm, inviting color for gathering spaces
5. **Refrigerator (Purple)** - Distinct color for large appliances
6. **Bathroom (Cyan)** - Water-related, hence cyan/aqua
7. **Room Types** - Various shades of pink/orange/brown to distinguish room functions
8. **Furniture** - Diverse bright colors for easy identification
9. **Storage** - Earth tones (browns) for cabinets/counters
10. **Unknown (White)** - Neutral color for unclassified objects

## Adding Custom Colors

To add or modify colors, edit the `class_colors` dictionary in `/ml/detection_merger.py`:

```python
class_colors = {
    'wall': (0, 0, 255),           # BGR format
    'your_class': (B, G, R),       # Add your class here
    # ...
}
```

**Note:** OpenCV uses BGR (Blue, Green, Red) format, not RGB!

## Class Name Normalization

Class names are automatically normalized to lowercase and trimmed. Common synonyms are supported:

- `toilet`, `bathroom`, `wc`, `restroom` → all map to `toilet`
- `refrigerator`, `fridge` → both map to `refrigerator`
- `bed room` → normalized to `bedroom`
- `living room`, `livingroom` → both map to `living room`

## Legend Display

The visualization automatically generates a legend showing only detected classes:

- Small colored box representing the class color
- Class name label in white text
- Positioned in the top-left corner of the image
- Only shows classes that are actually detected in the current image
