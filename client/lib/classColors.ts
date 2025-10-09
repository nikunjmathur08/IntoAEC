/**
 * Class-based color mapping for floor plan elements
 * Colors match the server-side visualization (BGR converted to Hex)
 */

export interface ClassColor {
  hex: string;
  rgb: { r: number; g: number; b: number };
  name: string;
}

// Normalize class name for matching
// Uses pattern matching to group similar elements automatically
export function normalizeClassName(className: string): string {
  const normalized = className.toLowerCase().trim();
  
  // Pattern-based matching - check if the name contains certain keywords
  const patternMappings: [string[], string][] = [
    // Format: [keywords_to_check, canonical_name]
    [['bedroom', 'bed room'], 'bedroom'],
    [['bathroom', 'bath room', 'restroom', 'washroom', 'wc', 'toilet', 'lavatory'], 'toilet'],
    [['kitchen', 'kitchenette'], 'kitchen'],
    [['living room', 'livingroom', 'lounge', 'family room'], 'living room'],
    [['dining room', 'diningroom', 'dining area', 'dining table'], 'dining room'],
    [['balcony', 'terrace', 'patio'], 'bedroom'], // Group balconies with bedrooms
    [['foyer', 'entry', 'entrance', 'hallway', 'corridor'], 'bedroom'], // Entry areas
    [['closet', 'wardrobe', 'storage'], 'cabinet'],
    [['office', 'study'], 'room'],
    [['laundry', 'utility'], 'room'],
    // COCO furniture classes
    [['couch', 'sofa'], 'sofa'],
    [['potted plant', 'plant'], 'room'], // Group plants with generic room
  ];
  
  // Check pattern matches
  for (const [keywords, canonicalName] of patternMappings) {
    for (const keyword of keywords) {
      if (normalized.includes(keyword)) {
        return canonicalName;
      }
    }
  }
  
  // Exact match synonyms for specific cases
  const exactSynonyms: Record<string, string> = {
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
  };
  
  // Check exact synonyms
  if (normalized in exactSynonyms) {
    return exactSynonyms[normalized];
  }
  
  // If no match found, return normalized name
  return normalized;
}

// Class color mapping (converted from server-side BGR to hex)
const classColorMap: Record<string, ClassColor> = {
  'wall': {
    hex: '#FF0000',  // Red
    rgb: { r: 255, g: 0, b: 0 },
    name: 'Wall'
  },
  'window': {
    hex: '#0000FF',  // Blue
    rgb: { r: 0, g: 0, b: 255 },
    name: 'Window'
  },
  'door': {
    hex: '#588157',  // Green
    rgb: { r: 88, g: 129, b: 87 },
    name: 'Door'
  },
  'table': {
    hex: '#FFA500',  // Orange
    rgb: { r: 255, g: 165, b: 0 },
    name: 'Table'
  },
  'refrigerator': {
    hex: '#800080',  // Purple
    rgb: { r: 128, g: 0, b: 128 },
    name: 'Refrigerator'
  },
  'toilet': {
    hex: '#023e8a',  // Navy Blue
    rgb: { r: 2, g: 62, b: 138 },
    name: 'Toilet/Bathroom'
  },
  'room': {
    hex: '#FFC0CB',  // Light Pink
    rgb: { r: 255, g: 192, b: 203 },
    name: 'Room'
  },
  'bedroom': {
    hex: '#FF1493',  // Deep Pink
    rgb: { r: 255, g: 20, b: 147 },
    name: 'Bedroom'
  },
  'kitchen': {
    hex: '#FF8C00',  // Dark Orange
    rgb: { r: 255, g: 140, b: 0 },
    name: 'Kitchen'
  },
  'living room': {
    hex: '#D2691E',  // Brown
    rgb: { r: 210, g: 105, b: 30 },
    name: 'Living Room'
  },
  'stairs': {
    hex: '#808080',  // Gray
    rgb: { r: 128, g: 128, b: 128 },
    name: 'Stairs'
  },
  'chair': {
    hex: '#FF69B4',  // Hot Pink
    rgb: { r: 255, g: 105, b: 180 },
    name: 'Chair'
  },
  'bed': {
    hex: '#00BFFF',  // Deep Sky Blue
    rgb: { r: 0, g: 191, b: 255 },
    name: 'Bed'
  },
  'sofa': {
    hex: '#FF4500',  // Orange Red
    rgb: { r: 255, g: 69, b: 0 },
    name: 'Sofa'
  },
  'sink': {
    hex: '#8A2BE2',  // Blue Violet
    rgb: { r: 138, g: 43, b: 226 },
    name: 'Sink'
  },
  'cabinet': {
    hex: '#8B4513',  // Saddle Brown
    rgb: { r: 139, g: 69, b: 19 },
    name: 'Cabinet'
  },
  'counter': {
    hex: '#CD5C5C',  // Indian Red
    rgb: { r: 205, g: 92, b: 92 },
    name: 'Counter'
  },
};

// Get color for a class
export function getClassColor(className: string): ClassColor {
  const normalized = normalizeClassName(className);
  return classColorMap[normalized] || {
    hex: '#000000',  // White for unknown
    rgb: { r: 0, g: 0, b: 0 },
    name: className
  };
}

// Get hex color for a class
export function getClassColorHex(className: string): string {
  return getClassColor(className).hex;
}

// Get RGB color for a class
export function getClassColorRGB(className: string): { r: number; g: number; b: number } {
  return getClassColor(className).rgb;
}

// Get RGBA string for a class with optional alpha
export function getClassColorRGBA(className: string, alpha: number = 1): string {
  const { r, g, b } = getClassColor(className).rgb;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// Get all available class colors
export function getAllClassColors(): Record<string, ClassColor> {
  return { ...classColorMap };
}

// Check if a class has a defined color
export function hasClassColor(className: string): boolean {
  const normalized = normalizeClassName(className);
  return normalized in classColorMap;
}

