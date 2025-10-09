"use client";

import { useEffect, useState, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { getLatestFileForSession, createDataUrl, getFileDisplayType, getAnalysisResults } from "../lib/localStorageUtils";
import { getClassColorHex, getClassColorRGBA } from "../lib/classColors";
import { 
  FaHome, 
  FaFolder, 
  FaFileAlt, 
  FaRuler, 
  FaEraser,
} from "react-icons/fa";

interface ScaleLine {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  realWorldLength: number;
  unit: string;
}

interface CombinedDetection {
  className: string;
  totalCount: number;
  yoloCount: number;
  detectron2Count: number;
  floorplanCount: number;
  avgConfidence: number;
  models: string[];
  detectionInstances?: any[];
}

interface CategoryGroup {
  name: string;
  icon: string;
  detections: CombinedDetection[];
  color: string;
}

export default function Dashboard() {
  const searchParams = useSearchParams();
  const userToken = searchParams?.get("token");
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [fileType, setFileType] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analysisResults, setAnalysisResults] = useState<any[]>([]);
  const [selectedResultIndex, setSelectedResultIndex] = useState<number>(0);

  // Line drawing states
  const [isDrawingMode, setIsDrawingMode] = useState(false);
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(null);
  const [currentPoint, setCurrentPoint] = useState<{ x: number; y: number } | null>(null);
  const [scaleLine, setScaleLine] = useState<ScaleLine | null>(null);
  const [showScaleInput, setShowScaleInput] = useState(false);
  const [scaleInput, setScaleInput] = useState("");
  const [scaleUnit, setScaleUnit] = useState("meters");
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageElement, setImageElement] = useState<HTMLImageElement | null>(null);
  const [highlightedDetection, setHighlightedDetection] = useState<any>(null);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['rooms', 'elements', 'labels']));
  const [highlightTimeout, setHighlightTimeout] = useState<NodeJS.Timeout | null>(null);
  
  const [viewMode, setViewMode] = useState<'original' | 'annotated'>('original');

  useEffect(() => {
    console.log("Dashboard mounted with token:", userToken);
    if (!userToken) {
      setError("No user token provided");
      setLoading(false);
      return;
    }

    const fetchLatestFile = async () => {
      try {
        setLoading(true);
        setError(null);

        const fileInfo = getLatestFileForSession(userToken);

        if (!fileInfo) {
          setError("No files found for this session. Please upload a file first.");
          return;
        }

        const fileUrl = createDataUrl(fileInfo);
        setFileUrl(fileUrl);
        setFileName(fileInfo.originalName);

        const displayType = getFileDisplayType(fileInfo.originalName);
        setFileType(displayType);

        // Load analysis results
        const results = getAnalysisResults(userToken);
        console.log("Loaded analysis results:", results);
        setAnalysisResults(results);

      } catch (err: any) {
        console.error("Unexpected error:", err);
        setError(`Unexpected error: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchLatestFile();
  }, [userToken]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (highlightTimeout) {
        clearTimeout(highlightTimeout);
      }
    };
  }, [highlightTimeout]);

  const getCombinedDetections = (): CombinedDetection[] => {
    if (analysisResults.length === 0) return [];

    const detectionMap = new Map<string, CombinedDetection>();

    analysisResults.forEach(result => {
      if (!result.success || !result.analysis_results?.detections) return;

      const modelName = result.model_used || 'unknown';

      // Check if this is a combined analysis result
      if (modelName === 'combined') {
        result.analysis_results.detections.forEach((detection: any) => {
          const className = detection.class_name;
          
          if (!detectionMap.has(className)) {
            detectionMap.set(className, {
              className,
              totalCount: 0,
              yoloCount: 0,
              detectron2Count: 0,
              floorplanCount: 0,
              avgConfidence: 0,
              models: [],
              detectionInstances: []
            });
          }

          const combined = detectionMap.get(className)!;
          combined.totalCount += 1;
          
          combined.detectionInstances!.push({
            ...detection,
            model: modelName,
            resultIndex: analysisResults.indexOf(result)
          });
          
          const sources = detection.sources || [];
          if (sources.includes('yolo')) {
            combined.yoloCount += 1;
            if (!combined.models.includes('yolo')) {
              combined.models.push('yolo');
            }
          }
          if (sources.includes('detectron2')) {
            combined.detectron2Count += 1;
            if (!combined.models.includes('detectron2')) {
              combined.models.push('detectron2');
            }
          }
          if (sources.includes('floorplan')) {
            combined.floorplanCount += 1;
            if (!combined.models.includes('floorplan')) {
              combined.models.push('floorplan');
            }
          }

          combined.avgConfidence = (combined.avgConfidence * (combined.totalCount - 1) + detection.confidence) / combined.totalCount;
        });
      } else {
        // For individual model results
        result.analysis_results.detections.forEach((detection: any) => {
          const className = detection.class_name;
          
          if (!detectionMap.has(className)) {
            detectionMap.set(className, {
              className,
              totalCount: 0,
              yoloCount: 0,
              detectron2Count: 0,
              floorplanCount: 0,
              avgConfidence: 0,
              models: [],
              detectionInstances: []
            });
          }

          const combined = detectionMap.get(className)!;
          combined.totalCount += 1;
          
          // Store individual detection instance with bbox info
          combined.detectionInstances!.push({
            ...detection,
            model: modelName,
            resultIndex: analysisResults.indexOf(result)
          });
          
          if (modelName === 'yolo') {
            combined.yoloCount += 1;
          } else if (modelName === 'detectron2') {
            combined.detectron2Count += 1;
          } else if (modelName === 'floorplan') {
            combined.floorplanCount += 1;
          }

          if (!combined.models.includes(modelName)) {
            combined.models.push(modelName);
          }

          // Update average confidence
          combined.avgConfidence = (combined.avgConfidence * (combined.totalCount - 1) + detection.confidence) / combined.totalCount;
        });
      }
    });

    return Array.from(detectionMap.values()).sort((a, b) => b.totalCount - a.totalCount);
  };

  // Categorize detections into logical groups
  const categorizeDetections = (detections: CombinedDetection[]): CategoryGroup[] => {
    const roomTypes = ['bedroom', 'bathroom', 'kitchen', 'living room', 'dining room', 'toilet', 'wc', 'entry',
                       'restroom', 'hallway', 'corridor', 'balcony', 'terrace', 'garage', 'storage',
                       'laundry', 'office', 'study', 'closet', 'pantry', 'utility', 'foyer', 'entrance', 'porch', 'stairs'];
    
    const elementTypes = ['door', 'window', 'sink', 'bathtub', 'shower', 'stairs', 'fireplace',
                          'column', 'wall', 'furniture', 'cabinet', 'counter', 'appliance', 'fixture'];
    
    const labelTypes = ['label', 'text', 'dimension', 'note', 'symbol', 'scale'];
    
    const categories: CategoryGroup[] = [
      { name: 'Rooms', icon: '🏠', detections: [], color: 'blue' },
      { name: 'Elements & Fixtures', icon: '🚪', detections: [], color: 'purple' },
      { name: 'Labels & Text', icon: '📝', detections: [], color: 'green' },
      { name: 'Other', icon: '📦', detections: [], color: 'gray' }
    ];
    
    detections.forEach(detection => {
      const classNameLower = detection.className.toLowerCase();
      
      if (roomTypes.some(room => classNameLower.includes(room))) {
        categories[0].detections.push(detection);
      } else if (elementTypes.some(elem => classNameLower.includes(elem))) {
        categories[1].detections.push(detection);
      } else if (labelTypes.some(label => classNameLower.includes(label))) {
        categories[2].detections.push(detection);
      } else {
        categories[3].detections.push(detection);
      }
    });
    
    // Return only categories that have detections
    return categories.filter(cat => cat.detections.length > 0);
  };

  // Toggle category expansion
  const toggleCategory = (categoryName: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryName)) {
      newExpanded.delete(categoryName);
    } else {
      newExpanded.add(categoryName);
    }
    setExpandedCategories(newExpanded);
  };

  // Total detections across all models
  const getTotalDetections = (): number => {
    return analysisResults.reduce((total, result) => {
      if (result.success && result.analysis_results?.total_detections) {
        return total + result.analysis_results.total_detections;
      }
      return total;
    }, 0);
  };

  // Get the image to display based on view mode
  const getDisplayImage = () => {
    if (viewMode === 'original') {
      // Show original clean image
      return fileUrl;
    } else {
      // Show annotated result from selected model
      if (analysisResults.length === 0) return fileUrl;
      
      const selectedResult = analysisResults[selectedResultIndex];
      if (selectedResult && selectedResult.success && selectedResult.result_image) {
        return `data:image/jpeg;base64,${selectedResult.result_image}`;
      }
      
      return fileUrl;
    }
  };

  const displayImage = getDisplayImage();

  // Animation loop for pulsing highlight effect and persistent scale line
  useEffect(() => {
    // Run animation if there's a highlighted detection OR a scale line OR drawing in progress
    if (!highlightedDetection && !scaleLine && !isDrawing) return;
    
    const animate = () => {
      if (imageLoaded && imageElement && canvasRef.current && containerRef.current) {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Set canvas size to match image
        canvas.width = imageElement.naturalWidth;
        canvas.height = imageElement.naturalHeight;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw highlighted detection boxes if any
        if (highlightedDetection && highlightedDetection.bbox) {
          const bbox = highlightedDetection.bbox;
          
          // Calculate dimensions with scale
          const imageScale = imageElement.naturalWidth / imageElement.width;
          const x1 = bbox.x1;
          const y1 = bbox.y1;
          const x2 = bbox.x2;
          const y2 = bbox.y2;
          
          // Draw enhanced highlight that works well on both clean and annotated images
          ctx.save();
          
          // Get class-based color for this detection
          const className = highlightedDetection.class_name || 'unknown';
          const classColorHex = getClassColorHex(className);
          
          // Create a more prominent highlight for annotated view with pulsing effect
          const highlightColor = classColorHex;
          const glowIntensity = viewMode === 'annotated' ? 35 : 25;
          
          // Add subtle pulsing effect
          const pulseIntensity = Math.sin(Date.now() * 0.005) * 0.3 + 0.7; // Subtle pulse
          
          ctx.shadowColor = highlightColor;
          ctx.shadowBlur = glowIntensity * pulseIntensity;
          ctx.strokeStyle = highlightColor;
          ctx.lineWidth = (viewMode === 'annotated' ? 6 : 4) * pulseIntensity;
          ctx.setLineDash([]);
          ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
          
          ctx.shadowBlur = 0;
          ctx.strokeStyle = viewMode === 'annotated' ? '#FFFFFF' : '#FFFFFF';
          ctx.lineWidth = (viewMode === 'annotated' ? 3 : 2) * pulseIntensity;
          ctx.strokeRect(x1 + 3, y1 + 3, (x2 - x1) - 6, (y2 - y1) - 6);
          
          const fillOpacity = (viewMode === 'annotated' ? 0.25 : 0.15) * pulseIntensity;
          ctx.fillStyle = getClassColorRGBA(className, fillOpacity);
          ctx.fillRect(x1, y1, x2 - x1, y2 - y1);
          
          ctx.restore();
          
          const labelText = highlightedDetection.class_name || 'Detection';
          ctx.font = `bold ${viewMode === 'annotated' ? '16px' : '14px'} Inter, sans-serif`;
          const textMetrics = ctx.measureText(labelText);
          const textWidth = textMetrics.width;
          const textHeight = viewMode === 'annotated' ? 16 : 14;
          const padding = viewMode === 'annotated' ? 8 : 6;
          ctx.fillStyle = highlightColor;
          ctx.fillRect(x1, y1 - textHeight - padding * 2, textWidth + padding * 2, textHeight + padding * 2);
          
          ctx.strokeStyle = '#FFFFFF';
          ctx.lineWidth = 1;
          ctx.strokeRect(x1, y1 - textHeight - padding * 2, textWidth + padding * 2, textHeight + padding * 2);
          
          ctx.fillStyle = '#FFFFFF';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'top';
          ctx.fillText(labelText, x1 + padding, y1 - textHeight - padding);
          
          if (viewMode === 'annotated') {
            ctx.fillStyle = highlightColor;
            ctx.font = 'bold 12px Inter, sans-serif';
            ctx.fillText('HIGHLIGHTED', x1 + padding, y1 - textHeight - padding + textHeight + 2);
          }
        }

        // Draw scale line if exists
        if (scaleLine) {
          ctx.strokeStyle = '#3B82F6';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.moveTo(scaleLine.startX, scaleLine.startY);
          ctx.lineTo(scaleLine.endX, scaleLine.endY);
          ctx.stroke();

          // Draw endpoints
          ctx.fillStyle = '#3B82F6';
          ctx.beginPath();
          ctx.arc(scaleLine.startX, scaleLine.startY, 6, 0, 2 * Math.PI);
          ctx.fill();
          ctx.beginPath();
          ctx.arc(scaleLine.endX, scaleLine.endY, 6, 0, 2 * Math.PI);
          ctx.fill();

          // Draw label
          const midX = (scaleLine.startX + scaleLine.endX) / 2;
          const midY = (scaleLine.startY + scaleLine.endY) / 2;
          ctx.fillStyle = '#3B82F6';
          ctx.font = 'bold 16px Inter, sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(`${scaleLine.realWorldLength} ${scaleLine.unit}`, midX, midY - 10);
        }

        // Draw current line being drawn
        if (isDrawing && startPoint && currentPoint) {
          ctx.strokeStyle = '#10B981';
          ctx.lineWidth = 3;
          ctx.setLineDash([5, 5]);
          ctx.beginPath();
          ctx.moveTo(startPoint.x, startPoint.y);
          ctx.lineTo(currentPoint.x, currentPoint.y);
          ctx.stroke();
          ctx.setLineDash([]);

          // Draw start point
          ctx.fillStyle = '#10B981';
          ctx.beginPath();
          ctx.arc(startPoint.x, startPoint.y, 6, 0, 2 * Math.PI);
          ctx.fill();
        }
      }
      
      // Continue animation if needed
      if (highlightedDetection || scaleLine || isDrawing) {
        requestAnimationFrame(animate);
      }
    };
    
    animate();
  }, [highlightedDetection, scaleLine, isDrawing, startPoint, currentPoint, imageLoaded, imageElement, viewMode]);

  // This useEffect is now handled by the animation loop above
  // Keeping it commented for reference if needed for non-animated elements
  /*
  useEffect(() => {
    // Removed: now handled by main animation loop
  }, []);
  */

  const handleCanvasMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawingMode || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    setIsDrawing(true);
    setStartPoint({ x, y });
    setCurrentPoint({ x, y });
  };

  const handleCanvasMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    setCurrentPoint({ x, y });
  };

  const handleCanvasMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !startPoint || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    setIsDrawing(false);
    setCurrentPoint(null);
    
    // Show scale input dialog
    setShowScaleInput(true);
    setScaleLine({
      startX: startPoint.x,
      startY: startPoint.y,
      endX: x,
      endY: y,
      realWorldLength: 0,
      unit: scaleUnit
    });
  };

  const handleSaveScale = () => {
    if (!scaleLine || !scaleInput) return;

    const length = parseFloat(scaleInput);
    if (isNaN(length) || length <= 0) {
      alert("Please enter a valid positive number for the scale");
      return;
    }

    const updatedScaleLine: ScaleLine = {
      ...scaleLine,
      realWorldLength: length,
      unit: scaleUnit
    };

    setScaleLine(updatedScaleLine);
    setShowScaleInput(false);
    setStartPoint(null);
    setIsDrawingMode(false);

    // Calculate pixels per unit for future use
    const pixelLength = Math.sqrt(
      Math.pow(updatedScaleLine.endX - updatedScaleLine.startX, 2) +
      Math.pow(updatedScaleLine.endY - updatedScaleLine.startY, 2)
    );
    const pixelsPerUnit = pixelLength / length;
    
    // Store in localStorage for later use
    if (userToken) {
      localStorage.setItem(`scale_${userToken}`, JSON.stringify({
        scaleLine: updatedScaleLine,
        pixelsPerUnit
      }));
    }

    console.log(`Scale set: ${length} ${scaleUnit} = ${pixelLength.toFixed(2)} pixels`);
    console.log(`Pixels per ${scaleUnit}: ${pixelsPerUnit.toFixed(2)}`);
  };

  const handleCancelScale = () => {
    setShowScaleInput(false);
    setScaleLine(null);
    setStartPoint(null);
    setCurrentPoint(null);
    setIsDrawing(false);
    setScaleInput("");
  };

  const toggleDrawingMode = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDrawingMode(!isDrawingMode);
    console.log("Drawing mode toggled:", !isDrawingMode);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your file...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow-lg max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Error Loading File</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.href = "/"}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Upload
          </button>
        </div>
      </div>
    );
  }

  const combinedDetections = getCombinedDetections();
  const categorizedDetections = categorizeDetections(combinedDetections);
  const totalDetections = getTotalDetections();
  const hasMultipleModels = analysisResults.filter(r => r.success).length > 1;

  const handleDetectionHover = (detection: any) => {
    // Clear any existing timeout
    if (highlightTimeout) {
      clearTimeout(highlightTimeout);
      setHighlightTimeout(null);
    }
    setHighlightedDetection(detection);
    setIsDrawingMode(false); // Exit drawing mode when highlighting
  };

  const handleDetectionLeave = () => {
    // Add a small delay to prevent flickering when moving between elements
    const timeout = setTimeout(() => {
      setHighlightedDetection(null);
    }, 100);
    setHighlightTimeout(timeout);
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Top Header */}
      <div className="h-16 flex items-center justify-between px-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-blue-800">IntoAEC</h1>
        <div className="flex items-center gap-4">
          <button
            onClick={() => window.location.href = "/"}
            className="text-gray-600 hover:text-gray-900 transition-colors"
          >
            <FaHome className="text-xl" />
          </button>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">

        {/* Workspace Navigation */}
        <div className="p-6">
          <h2 className="text-sm font-semibold text-gray-800 uppercase tracking-wide mb-4">
            WORKSPACE
          </h2>
          <nav className="space-y-2">
            <a href="#" className="flex items-center space-x-3 text-blue-600 bg-blue-50 rounded-lg px-3 py-2 transition-colors">
              <FaHome className="text-blue-600" />
              <span className="font-medium">Dashboard</span>
            </a>
            <a href="#" className="flex items-center space-x-3 text-gray-700 hover:bg-gray-100 rounded-lg px-3 py-2 transition-colors">
              <FaFolder className="text-gray-500" />
              <span>Projects</span>
            </a>
            <a href="#" className="flex items-center space-x-3 text-gray-700 hover:bg-gray-100 rounded-lg px-3 py-2 transition-colors">
              <FaFileAlt className="text-gray-500" />
              <span>Templates</span>
            </a>
          </nav>
        </div>

        {/* File Info */}
        {fileName && (
          <div className="px-6 pb-6">
            <h2 className="text-sm font-semibold text-gray-800 uppercase tracking-wide mb-4">
              CURRENT FILE
            </h2>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center space-x-3">
                <FaFileAlt className="text-blue-600" />
                <span className="text-sm text-gray-700 truncate">{fileName}</span>
              </div>
            </div>
          </div>
        )}

        {/* Model Selector - if multiple results */}
        {hasMultipleModels && (
          <div className="px-6 pb-6">
            <h2 className="text-sm font-semibold text-gray-800 uppercase tracking-wide mb-4">
              VIEWING MODEL
            </h2>
            <div className="space-y-2">
              {analysisResults.filter(r => r.success).map((result, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedResultIndex(index)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                    selectedResultIndex === index
                      ? 'bg-blue-50 text-blue-600 border-2 border-blue-200'
                      : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm">
                      {result.model_used?.toUpperCase() || 'Unknown'}
                    </span>
                    {result.success && (
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                        {result.analysis_results?.total_detections || 0}
                      </span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
        </div>

        {/* Main Content - Canvas Area */}
        <div className="flex-1 relative bg-white flex flex-col items-center justify-center p-6">
          {/* Grid Background */}
          <div 
            className="absolute inset-0 opacity-40 pointer-events-none"
            style={{
              backgroundImage: `
                radial-gradient(circle, #9ca3af 1px, transparent 1px)
              `,
              backgroundSize: '20px 20px'
            }}
          />
          
          {/* File Display - Centered */}
          <div ref={containerRef} className="relative z-10 flex items-center justify-center" style={{ maxHeight: 'calc(100vh - 250px)', maxWidth: '100%' }} onMouseLeave={handleDetectionLeave}>
            {fileType === "image" ? (
              <div className="relative" style={{ maxHeight: 'calc(100vh - 250px)', maxWidth: '100%' }}>
                <img
                  src={displayImage!}
                  alt="Floor plan analysis"
                  className="max-w-full max-h-full object-contain rounded-lg shadow-lg border"
                  style={{ maxHeight: 'calc(100vh - 250px)' }}
                  onLoad={(e) => {
                    setImageLoaded(true);
                    setImageElement(e.currentTarget);
                  }}
                  onMouseLeave={handleDetectionLeave}
                />
                <canvas
                  ref={canvasRef}
                  className={`absolute top-0 left-0 w-full h-full ${isDrawingMode ? 'cursor-crosshair' : 'pointer-events-none'}`}
                  style={{ 
                    pointerEvents: isDrawingMode ? 'auto' : 'none',
                    zIndex: isDrawingMode ? 30 : 20,  // Ensure canvas is above image
                  }}
                  onMouseDown={handleCanvasMouseDown}
                  onMouseMove={handleCanvasMouseMove}
                  onMouseUp={handleCanvasMouseUp}
                  onMouseLeave={handleDetectionLeave}
                />
              </div>
            ) : fileType === "pdf" ? (
              <iframe
                src={fileUrl!}
                className="w-full border-0 rounded-lg shadow-lg"
                title="PDF Viewer"
                style={{ height: 'calc(100vh - 250px)' }}
              />
            ) : fileType === "cad" ? (
              <div className="text-center p-8 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="text-yellow-600 text-6xl mb-4">📐</div>
                <h3 className="text-lg font-semibold text-yellow-800 mb-2">CAD File Detected</h3>
                <p className="text-yellow-700 mb-4">
                  CAD files (.dwg) cannot be previewed in the browser.
                </p>
                <a
                  href={fileUrl!}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700 transition-colors"
                >
                  Download CAD File
                </a>
              </div>
            ) : (
              <div className="text-center p-8 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="text-gray-400 text-6xl mb-4">📄</div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Unsupported File Type</h3>
                <p className="text-gray-600">This file type cannot be previewed.</p>
              </div>
            )}
          </div>

          {/* Bottom Toolbar - Below Image */}
          <div className="relative z-10 mt-6 flex justify-center gap-3">
            {/* View Mode Toggle */}
            {analysisResults.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg border border-gray-200 px-2 py-2 flex items-center">
                <button 
                  className={`px-4 py-2 rounded-md transition-all text-xs font-medium ${
                    viewMode === 'original' 
                      ? 'bg-blue-600 text-white shadow-md' 
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                  onClick={() => {
                    setViewMode('original');
                    // Clear highlight when switching modes for better UX
                    if (viewMode === 'annotated') {
                      setHighlightedDetection(null);
                    }
                  }}
                  title="Show Original Clean Image"
                >
                  Clean View
                </button>
                <button 
                  className={`px-4 py-2 rounded-md transition-all text-xs font-medium ${
                    viewMode === 'annotated' 
                      ? 'bg-purple-600 text-white shadow-md' 
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                  onClick={() => {
                    setViewMode('annotated');
                    // Clear highlight when switching to annotated mode
                    setHighlightedDetection(null);
                  }}
                  title="Show Model Annotations"
                >
                  Annotated
                </button>
              </div>
            )}

            {/* Tools */}
            <div className="bg-white rounded-lg shadow-lg border border-gray-200 px-4 py-3 flex items-center space-x-3">
              <button 
                className={`p-2 rounded transition-colors ${
                  isDrawingMode ? 'bg-blue-50 border-2 border-blue-200' : 'hover:bg-gray-100'
                }`}
                onClick={toggleDrawingMode}
                title="Draw Scale Line"
              >
                <FaRuler className={`text-sm ${isDrawingMode ? 'text-blue-600' : 'text-gray-600'}`} />
              </button>
              {scaleLine && (
                <button 
                  className="p-2 hover:bg-gray-100 rounded transition-colors"
                  onClick={(e) => {
                    e.stopPropagation();
                    setScaleLine(null);
                  }}
                  title="Clear Scale"
                >
                  <FaEraser className="text-gray-600 text-sm" />
                </button>
              )}
            </div>
          </div>

          {/* Scale Input Modal */}
          {showScaleInput && (
            <div className="absolute inset-0 backdrop-blur-sm flex items-center justify-center z-50">
              <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Set Scale</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Enter the real-world length of the line you drew:
                </p>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Length
                    </label>
                    <input
                      type="number"
                      value={scaleInput}
                      onChange={(e) => setScaleInput(e.target.value)}
                      placeholder="e.g., 10"
                      className="w-full px-2 py-2 border border-gray-300 text-black rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      autoFocus
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Unit
                    </label>
                    <select
                      value={scaleUnit}
                      onChange={(e) => setScaleUnit(e.target.value)}
                      className="w-full px-2 py-2 border border-gray-300 text-black rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="meters">Meters</option>
                      <option value="feet">Feet</option>
                      <option value="inches">Inches</option>
                      <option value="centimeters">Centimeters</option>
                    </select>
                  </div>
                </div>
                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    onClick={handleCancelScale}
                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSaveScale}
                    className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                  >
                    Save Scale
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Drawing Mode Indicator */}
          {isDrawingMode && (
            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg z-40">
              <p className="text-sm font-medium">
                Click and drag to draw a scale line
              </p>
            </div>
          )}

          {/* Scale Display */}
          {scaleLine && scaleLine.realWorldLength > 0 && (
            <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg border border-gray-200 p-3 z-40">
              <h4 className="text-xs font-semibold text-gray-900 mb-1">Scale</h4>
              <p className="text-sm text-gray-600">
                {scaleLine.realWorldLength} {scaleLine.unit}
              </p>
            </div>
          )}
        </div>

        {/* Analysis Results Panel - Elegant Combined View */}
        <div className="w-80 bg-white border-l border-gray-200 flex flex-col" style={{ maxHeight: '100vh' }}>
          {/* Fixed Header */}
          <div className="p-6 border-b border-gray-200 bg-white flex-shrink-0">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-lg font-semibold text-gray-900">Analysis Results</h2>
            </div>
            <p className="text-sm text-gray-600">
              {analysisResults.length > 0 
                ? `${totalDetections} total detections found`
                : 'No analysis results available yet'
              }
            </p>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto p-6 pt-4" style={{ maxHeight: 'calc(100vh - 140px)' }}>
            {combinedDetections.length > 0 ? (
              <div className="space-y-4">
                {/* Summary Card */}
                <div className="rounded-xl p-4 border border-blue-100 bg-gradient-to-br from-blue-50 to-white">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-gray-900">Detection Summary</h3>
                    <span className="text-2xl font-bold text-blue-600">{totalDetections}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-600 mb-2">
                    <span>Unique Elements: {combinedDetections.length}</span>
                    {hasMultipleModels && (
                      <>
                        <span>•</span>
                        <span>Multiple Models</span>
                      </>
                    )}
                  </div>
                  
                  {/* View Mode Indicator */}
                  <div className={`mt-2 p-2 rounded-lg text-xs ${
                    viewMode === 'original' 
                      ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                      : 'bg-purple-50 text-purple-700 border border-purple-200'
                  }`}>
                    <div className="flex items-center gap-1 font-medium mb-1">
                      {viewMode === 'original' ? 'Clean View' : 'Annotated View'}
                    </div>
                    <p className="text-xs opacity-90">
                      Hover over any detection below to highlight it on the image
                      {viewMode === 'annotated' && ' (overlay on model annotations)'}
                    </p>
                  </div>

                </div>

                {/* Categorized Detections */}
                {categorizedDetections.map((category, catIndex) => (
                  <div key={catIndex} className="border border-gray-200 rounded-lg overflow-hidden">
                    {/* Category Header */}
                    <button
                      onClick={() => toggleCategory(category.name)}
                      className={`w-full flex items-center justify-between p-3 transition-colors ${
                        expandedCategories.has(category.name)
                          ? `bg-${category.color}-50 hover:bg-${category.color}-100`
                          : 'bg-gray-50 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{category.icon}</span>
                        <h3 className="text-sm font-semibold text-gray-900">{category.name}</h3>
                        <span className="text-xs bg-white px-2 py-0.5 rounded-full text-gray-600">
                          {category.detections.reduce((sum, det) => sum + det.totalCount, 0)}
                        </span>
                      </div>
                      <svg
                        className={`w-5 h-5 text-gray-600 transition-transform ${
                          expandedCategories.has(category.name) ? 'transform rotate-180' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    {/* Category Content */}
                    {expandedCategories.has(category.name) && (
                      <div className="p-2 space-y-1 bg-white">
                        {category.detections.map((detection, detIndex) => {
                          const classColorHex = getClassColorHex(detection.className);
                          return (
                          <div key={detIndex} className="space-y-1">
                            {/* Class Header with Count - shown when there are multiple instances */}
                            {detection.detectionInstances && detection.detectionInstances.length > 1 && (
                              <div className="flex items-center justify-between px-2 py-1.5 bg-gray-100 rounded-md border-l-4" style={{ borderLeftColor: classColorHex }}>
                                <div className="flex items-center gap-2">
                                  <div 
                                    className="w-2.5 h-2.5 rounded-full"
                                    style={{ backgroundColor: classColorHex }}
                                  />
                                  <span className="text-xs font-semibold text-gray-700 capitalize">
                                    {detection.className}
                                  </span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                  <span 
                                    className="text-xs font-bold px-2 py-0.5 rounded-full text-white"
                                    style={{ backgroundColor: classColorHex }}
                                  >
                                    {detection.totalCount}
                                  </span>
                                  <span className="text-xs text-gray-500">
                                    {detection.totalCount === 1 ? 'item' : 'items'}
                                  </span>
                                </div>
                              </div>
                            )}
                            
                            {/* Show each individual instance */}
                            {detection.detectionInstances && detection.detectionInstances.length > 0 ? (
                              detection.detectionInstances.map((instance, instIndex) => {
                                return (
                                <div
                                  key={instIndex}
                                  onMouseEnter={() => handleDetectionHover(instance)}
                                  onMouseLeave={handleDetectionLeave}
                                  className={`w-full text-left p-3 rounded-lg transition-all duration-200 cursor-pointer border-l-4 ${
                                    highlightedDetection === instance
                                      ? 'bg-gray-100 border-2 shadow-lg transform scale-[1.02]'
                                      : 'bg-gray-50 hover:bg-gray-100 border border-gray-200 hover:shadow-md'
                                  }`}
                                  style={{
                                    borderLeftColor: classColorHex,
                                    ...(highlightedDetection === instance ? { borderColor: classColorHex } : {})
                                  }}
                                >
                                  <div className="flex items-center justify-between">
                                    <div className="flex-1">
                                      <div className="flex items-center gap-2">
                                        {/* Color indicator dot */}
                                        <div 
                                          className="w-3 h-3 rounded-full"
                                          style={{ backgroundColor: classColorHex }}
                                        />
                                        <div className="flex items-center gap-1.5">
                                          <h4 className="font-medium text-gray-900 capitalize text-sm">
                                            {detection.className}
                                          </h4>
                                          {detection.detectionInstances!.length > 1 ? (
                                            <span className="text-xs text-gray-500">
                                              #{instIndex + 1} of {detection.totalCount}
                                            </span>
                                          ) : (
                                            <span 
                                              className="text-xs font-semibold px-1.5 py-0.5 rounded text-white"
                                              style={{ backgroundColor: classColorHex }}
                                            >
                                              1
                                            </span>
                                          )}
                                        </div>
                                      </div>
                                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                                        <span className="text-xs text-gray-500">
                                          {(instance.confidence * 100).toFixed(0)}%
                                        </span>
                                        {instance.model && (
                                          <span className={`text-xs px-2 py-0.5 rounded ${
                                            instance.model === 'yolo'
                                              ? 'bg-blue-100 text-blue-700'
                                              : instance.model === 'detectron2'
                                              ? 'bg-purple-100 text-purple-700'
                                              : instance.model === 'floorplan'
                                              ? 'bg-green-100 text-green-700'
                                              : 'bg-gray-100 text-gray-700'
                                          }`}>
                                            {instance.model === 'yolo' ? 'YOLO' : 
                                             instance.model === 'detectron2' ? 'D2' : 
                                             instance.model === 'floorplan' ? 'FP' : 
                                             instance.sources ? `${instance.sources.length} models` : instance.model}
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                    <div className="ml-2">
                                      {highlightedDetection === instance ? (
                                        <span style={{ color: classColorHex }}>
                                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                          </svg>
                                        </span>
                                      ) : (
                                        <span className="text-gray-400">
                                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                          </svg>
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              );
                              })
                            ) : (
                              <div className="p-3 bg-gray-50 rounded-lg border-l-4 border border-gray-200" style={{ borderLeftColor: classColorHex }}>
                                <div className="flex items-center justify-between">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                      <div 
                                        className="w-3 h-3 rounded-full"
                                        style={{ backgroundColor: classColorHex }}
                                      />
                                      <h4 className="font-medium text-gray-900 capitalize text-sm">
                                        {detection.className}
                                      </h4>
                                      <span 
                                        className="text-xs font-bold px-2 py-0.5 rounded-full text-white ml-1"
                                        style={{ backgroundColor: classColorHex }}
                                      >
                                        {detection.totalCount}
                                      </span>
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">
                                      {detection.totalCount} {detection.totalCount === 1 ? 'item' : 'items'} detected
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        );
                        })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : analysisResults.length > 0 ? (
              <div className="text-center py-8">
                <div className="text-red-400 text-4xl mb-3">⚠️</div>
                <p className="text-sm text-gray-500">
                  Analysis completed but no detections found
                </p>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-gray-400 text-4xl mb-3">📊</div>
                <p className="text-sm text-gray-500">
                  Upload and analyze files to see results here
                </p>
              </div>
            )}
          </div>
        </div>
        </div>
      </div>
  );
}