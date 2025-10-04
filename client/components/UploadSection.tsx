"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { saveFileToStorageAlt, generateSessionToken, saveAnalysisResults } from "../lib/localStorageUtils";
import { validateFile } from "../lib/fileUtils";
import { FaCloudUploadAlt, FaCheck, FaPlay, FaPlus, FaExclamationTriangle } from "react-icons/fa";

const allowedTypes = [
  "image/png",
  "application/pdf",
  "application/acad",
  "application/dwg",
  "application/x-dwg",
  "application/x-autocad",
  "image/vnd.dwg",
  "application/octet-stream",
];

export default function UploadSection() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [progress, setProgress] = useState(0);
  const [uploaded, setUploaded] = useState(false);
  const [fileNames, setFileNames] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [selectedModels, setSelectedModels] = useState<string[]>(['yolo', 'detectron2']);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleFileInputClick = () => {
    if (!mounted || uploading || !fileInputRef.current) return;
    fileInputRef.current.click();
  };

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0 || !mounted) return;

    setError(null);
    
    // Debug: Log the raw FileList
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      console.log(`File ${i}:`, {
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: file.lastModified,
        isFile: file instanceof File,
        constructor: file.constructor.name
      });
      
      // Test reading the first few bytes
      const reader = new FileReader();
      reader.readAsArrayBuffer(file.slice(0, 100));
      reader.onload = () => {
        const arrayBuffer = reader.result as ArrayBuffer;
        const uint8Array = new Uint8Array(arrayBuffer);
        
        // Convert to string to see if it contains form data
        const textDecoder = new TextDecoder();
        const text = textDecoder.decode(uint8Array);
      };
    }

    // First filter by type and size
    const typeValidFiles = Array.from(files).filter(
      (file) => {
        const isValidType = allowedTypes.includes(file.type) || file.name.toLowerCase().endsWith(".dwg");
        const isValidSize = file.size <= 10 * 1024 * 1024;
        
        if (!isValidType) {
          console.warn(`Invalid file type: ${file.name} (${file.type})`);
        }
        if (!isValidSize) {
          console.warn(`File too large: ${file.name} (${file.size} bytes)`);
        }
        
        return isValidType && isValidSize;
      }
    );

    if (typeValidFiles.length === 0) {
      setError("Invalid files. Only PNG, PDF, CAD files under 10MB are supported.");
      return;
    }

    // Then validate file content
    const validFiles = [];
    for (const file of typeValidFiles) {
      const isValid = await validateFile(file);
      if (isValid) {
        validFiles.push(file);
      } else {
        console.error(`File ${file.name} failed validation`);
        setError(`File ${file.name} appears to be corrupted or contains invalid data.`);
        return;
      }
    }

    setFileNames(validFiles.map((f) => f.name));
    setUploading(true);
    setProgress(0);
    const userToken = generateSessionToken();

    try {
      const uploadedFiles = [];

      for (let i = 0; i < validFiles.length; i++) {
        const file = validFiles[i];

        console.log(`Saving file ${i + 1}/${validFiles.length}:`, {
          originalName: file.name,
          size: file.size,
          type: file.type,
          lastModified: file.lastModified,
          isFile: file instanceof File,
          constructor: file.constructor.name
        });

        // Save to local storage using alternative method
        const savedFile = await saveFileToStorageAlt(file, userToken);

        if (!savedFile) {
          throw new Error(`Failed to save file: ${file.name}`);
        }

        uploadedFiles.push({ 
          id: savedFile.id,
          originalName: file.name,
          fileSize: file.size,
          fileType: file.type 
        });

        setProgress(Math.round(((i + 1) / validFiles.length) * 100));
      }

      setUploading(false);
      setUploaded(true);
      setError(null);

      // Store the current session token for analysis
      localStorage.setItem('currentSessionToken', userToken);
      
      // Don't redirect automatically - let user choose to analyze or go to dashboard

    } catch (uploadError: any) {
      console.error("Upload error details:", uploadError);
      
      let errorMessage = "Upload failed. Please try again.";
      
      if (uploadError.message) {
        errorMessage = uploadError.message;
      }
      
      setError(errorMessage);
      setUploading(false);
      setProgress(0);
    }
  };

  const resetUpload = () => {
    setUploaded(false);
    setUploading(false);
    setProgress(0);
    setFileNames([]);
    setError(null);
    setAnalyzing(false);
    setAnalysisResults(null);
  };

  const handleAnalysis = async () => {
    if (!mounted || analyzing) return;

    setAnalyzing(true);
    setError(null);

    try {
      // Get the current session token
      const userToken = localStorage.getItem('currentSessionToken');
      if (!userToken) {
        setError("No session found. Please upload files first.");
        setAnalyzing(false);
        return;
      }

      // Get uploaded files from localStorage using the correct session format
      const sessions = JSON.parse(localStorage.getItem('intoAEC_sessions') || '[]');
      
      const currentSession = sessions.find((session: any) => session.token === userToken);
      
      if (!currentSession || !currentSession.files || currentSession.files.length === 0) {
        setError("No files found in current session. Please upload files first.");
        setAnalyzing(false);
        return;
      }

      const files = currentSession.files;

      // Function to convert base64 to File
      const base64ToFile = (fileData: any): File => {
        // Handle base64 data - check if it has data URL prefix
        let base64Data = fileData.fileData;
        if (base64Data.includes(',')) {
          // Has data URL prefix like "data:image/png;base64,..."
          base64Data = base64Data.split(',')[1];
        }
        
        // Validate base64 data before decoding
        if (!base64Data || base64Data.length === 0) {
          throw new Error("Empty base64 data");
        }
        
        // Remove any whitespace or invalid characters
        base64Data = base64Data.replace(/[^A-Za-z0-9+/=]/g, '');
        
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: fileData.fileType });
        return new File([blob], fileData.fileName, { type: fileData.fileType });
      };

      // Function to analyze with a specific model
      const analyzeWithModel = async (fileData: any, modelType: string) => {
        try {
          
          const file = base64ToFile(fileData);

          // Create FormData for API call
          const formData = new FormData();
          formData.append('file', file);

          // Call FastAPI server with specified model
          const response = await fetch(`http://localhost:8000/analyze?model_type=${modelType}`, {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
          }

          const result = await response.json();
          return {
            filename: fileData.fileName,
            success: true,
            ...result
          };
        } catch (error: any) {
          console.error(`Error analyzing ${fileData.fileName} with ${modelType}:`, error);
          return {
            filename: fileData.fileName,
            success: false,
            model_used: modelType,
            error: error.message
          };
        }
      };

      // Create analysis promises for all files and selected models
      const analysisPromises: Promise<any>[] = [];

      for (const fileData of files) {
        for (const modelType of selectedModels) {
          analysisPromises.push(analyzeWithModel(fileData, modelType));
        }
      }

      // Wait for all analyses to complete
      const results = await Promise.all(analysisPromises);

      // Save results to localStorage
      saveAnalysisResults(userToken, results);
      
      // Check if any analysis succeeded
      const successfulResults = results.filter(r => r.success);
      if (successfulResults.length > 0) {
        // Redirect to dashboard with the session token
        router.push(`/dashboard?token=${userToken}`);
      } else {
        setError("❌ Analysis failed for all files. Please check server connection.");
        setAnalysisResults(results);
      }

    } catch (error: any) {
      console.error("Analysis error:", error);
      setError(`Analysis failed: ${error.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  if (!mounted) {
    return (
      <section className="relative py-20 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-white to-cyan-50/50" />
        <div className="relative z-10 max-w-4xl mx-auto">
          <div className="text-center">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-1/3 mx-auto mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="relative py-20 px-6 overflow-hidden">
      {/* Background with gradient and patterns */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-white to-cyan-50/50">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 right-10 w-24 h-24 bg-blue-500 rounded-full blur-2xl"></div>
          <div className="absolute bottom-10 left-10 w-32 h-32 bg-cyan-400 rounded-full blur-2xl"></div>
        </div>
      </div>

      {/* Floating decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-1/4 w-2 h-2 bg-blue-400 rounded-full opacity-30 animate-pulse"></div>
        <div
          className="absolute bottom-20 right-1/4 w-3 h-3 bg-cyan-400 transform rotate-45 opacity-20 animate-bounce"
          style={{ animationDelay: "1s" }}
        ></div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-12">
          <div
            className="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm border border-blue-100 rounded-full px-4 py-2 mb-6"
            style={{ boxShadow: "rgba(0, 0, 0, 0.1) 0px 4px 10px" }}
          >
            <FaCloudUploadAlt className="text-blue-600 text-sm" />
            <span
              className="text-sm font-medium text-slate-700"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              Upload & Analyze
            </span>
          </div>
          <h2
            className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-slate-900 to-blue-800 bg-clip-text text-transparent mb-4"
            style={{ fontFamily: "Inter, Poppins, sans-serif" }}
          >
            Ready to get started?
          </h2>
          <p
            className="text-slate-600 max-w-xl mx-auto"
            style={{
              fontFamily: "Inter, Poppins, sans-serif",
              fontSize: "16px",
            }}
          >
            Upload your architectural drawings and let our AI do the magic
          </p>
        </div>

        {/* Error Display - enhanced for 406 errors */}
        {error && (
          <div
            className={`mb-8 backdrop-blur-sm border rounded-2xl p-6 flex items-start gap-3 ${
              error.includes('✅') || error.includes('successful') 
                ? 'bg-green-50/80 border-green-200' 
                : error.includes('406') || error.includes('RLS')
                ? 'bg-orange-50/80 border-orange-200'
                : 'bg-red-50/80 border-red-200'
            }`}
            style={{ boxShadow: "rgba(0, 0, 0, 0.1) 0px 4px 15px" }}
          >
            <FaExclamationTriangle 
              className={`text-xl flex-shrink-0 mt-1 ${
                error.includes('✅') || error.includes('successful') 
                  ? 'text-green-500' 
                  : error.includes('406') || error.includes('RLS')
                  ? 'text-orange-500'
                  : 'text-red-500'
              }`} 
            />
            <div className="flex-1">
              <p
                className={`font-medium ${
                  error.includes('✅') || error.includes('successful') 
                    ? 'text-green-700' 
                    : error.includes('406') || error.includes('RLS')
                    ? 'text-orange-700'
                    : 'text-red-700'
                }`}
                style={{ fontFamily: "Inter, Poppins, sans-serif" }}
              >
                {error.includes('✅') || error.includes('successful') 
                  ? 'Connection Test' 
                  : error.includes('406') 
                  ? 'Database Permission Issue (406 Error)'
                  : 'Upload Error'}
              </p>
              <p
                className={`text-sm mt-1 ${
                  error.includes('✅') || error.includes('successful') 
                    ? 'text-green-600' 
                    : error.includes('406') || error.includes('RLS')
                    ? 'text-orange-600'
                    : 'text-red-600'
                }`}
                style={{ fontFamily: "Inter, Poppins, sans-serif" }}
              >
                {error}
              </p>
            </div>
            <button
              onClick={() => setError(null)}
              className={`text-xl leading-none hover:opacity-70 transition-opacity ${
                error.includes('✅') || error.includes('successful') 
                  ? 'text-green-500' 
                  : error.includes('406')
                  ? 'text-orange-500'
                  : 'text-red-500'
              }`}
            >
              ×
            </button>
          </div>
        )}

        {/* Rest of your component remains the same */}
        {!uploaded ? (
          <>
            <div
              onClick={handleFileInputClick}
              onDragOver={(e) => {
                e.preventDefault();
                e.stopPropagation();
              }}
              onDrop={(e) => {
                e.preventDefault();
                e.stopPropagation();
                if (!uploading) {
                  handleFiles(e.dataTransfer.files);
                }
              }}
              className={`group bg-white/70 backdrop-blur-sm hover:bg-white/90 transition-all duration-500 rounded-3xl text-center py-16 px-8 border-2 border-dashed hover:border-solid transform hover:scale-[1.02] hover:-translate-y-2 ${
                uploading ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
              }`}
              style={{
                borderColor: "#0066CC",
                boxShadow: "rgba(0, 0, 0, 0.1) 0px 8px 30px",
              }}
            >
              <div className="relative mb-8">
                <div
                  className={`w-24 h-24 mx-auto rounded-3xl flex items-center justify-center text-white text-4xl transition-all duration-500 ${
                    !uploading ? 'group-hover:scale-110 group-hover:rotate-6' : ''
                  }`}
                  style={{
                    backgroundColor: "#0066CC",
                    boxShadow: "rgba(0, 102, 204, 0.3) 0px 12px 35px",
                  }}
                >
                  <FaCloudUploadAlt />
                </div>
                <div
                  className="absolute inset-0 w-24 h-24 mx-auto rounded-3xl opacity-0 group-hover:opacity-20 transition-opacity duration-500"
                  style={{ backgroundColor: "#0066CC", filter: "blur(15px)" }}
                ></div>
              </div>

              <h3
                className="text-slate-800 mb-4 font-bold text-2xl group-hover:text-blue-800 transition-colors duration-300"
                style={{ fontFamily: "Inter, Poppins, sans-serif" }}
              >
                Drag & drop your files here
              </h3>
              <p
                className="text-slate-600 mb-2 text-lg group-hover:text-slate-700 transition-colors duration-300"
                style={{ fontFamily: "Inter, Poppins, sans-serif" }}
              >
                or click to browse and select files
              </p>
              <p
                className="text-slate-500 mb-8"
                style={{
                  fontFamily: "Inter, Poppins, sans-serif",
                  fontSize: "14px",
                }}
              >
                Supports: PNG, PDF, DWG (Max 10MB each)
              </p>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleFileInputClick();
                }}
                disabled={uploading}
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold px-8 py-4 rounded-2xl flex items-center gap-3 mx-auto transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                style={{
                  fontFamily: "Inter, Poppins, sans-serif",
                  fontSize: "16px",
                  boxShadow: "rgba(59, 130, 246, 0.3) 0px 8px 25px",
                }}
              >
                <FaPlus /> {uploading ? 'Uploading...' : 'Choose Files'}
              </button>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.png,.dwg"
              multiple
              onChange={(e) => handleFiles(e.target.files)}
              className="hidden"
              disabled={uploading}
            />

            {uploading && (
              <div
                className="mt-8 bg-white/70 backdrop-blur-sm rounded-2xl p-6 border border-white/50"
                style={{ boxShadow: "rgba(0, 0, 0, 0.1) 0px 8px 25px" }}
              >
                <div className="w-full h-4 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-300 relative overflow-hidden"
                    style={{
                      width: `${progress}%`,
                      background: "linear-gradient(90deg, #0066CC 0%, #00CCCC 100%)",
                    }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent transform -skew-x-12 animate-pulse"></div>
                  </div>
                </div>
                <p
                  className="text-slate-700 text-center mt-4 font-medium"
                  style={{ fontFamily: "Inter, Poppins, sans-serif" }}
                >
                  {`Uploading ${fileNames.length} file${fileNames.length > 1 ? 's' : ''}... ${progress}%`}
                </p>
                {fileNames.length > 0 && (
                  <div className="mt-2 text-sm text-slate-600 text-center">
                    <p style={{ fontFamily: "Inter, Poppins, sans-serif" }}>
                      Files: {fileNames.join(', ')}
                    </p>
                  </div>
                )}
                <div className="flex justify-center mt-4">
                  <button
                    onClick={() => {
                      setUploading(false);
                      setProgress(0);
                      setError(null);
                    }}
                    className="text-slate-500 hover:text-slate-700 text-sm transition-colors"
                    style={{ fontFamily: "Inter, Poppins, sans-serif" }}
                  >
                    Cancel Upload
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div
            className="text-center bg-white/80 backdrop-blur-sm rounded-3xl p-12 border border-white/50"
            style={{ boxShadow: "rgba(0, 0, 0, 0.1) 0px 8px 30px" }}
          >
            <div className="relative mb-8">
              <div
                className="w-20 h-20 mx-auto rounded-full flex items-center justify-center text-white text-2xl"
                style={{
                  backgroundColor: "#00CCCC",
                  boxShadow: "rgba(0, 204, 204, 0.3) 0px 8px 25px",
                }}
              >
                <FaCheck />
              </div>
            </div>
            <h3
              className="text-slate-800 mb-4 font-bold text-2xl"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              Upload Successful!
            </h3>
            <p
              className="text-slate-600 mb-8 text-lg"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              {fileNames.length > 1 
                ? `Your ${fileNames.length} files have been uploaded and are ready for analysis.`
                : 'Your floor plan has been uploaded and is ready for analysis.'
              }
            </p>
            
            {/* Model Selection */}
            <div className="mb-6">
              <div className="text-center mb-4">
                <p
                  className="text-sm font-medium text-slate-700 mb-3"
                  style={{ fontFamily: "Inter, Poppins, sans-serif" }}
                >
                  Select Analysis Models:
                </p>
                <div className="flex flex-col gap-2 max-w-md mx-auto">
                  {/* Combined Analysis - Special Option */}
                  <label className="flex items-center cursor-pointer bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-300 rounded-lg p-4 hover:border-blue-400 transition-colors shadow-sm">
                    <input
                      type="checkbox"
                      checked={selectedModels.includes('combined')}
                      onChange={(e) => {
                        if (e.target.checked) {
                          // If combined is selected, deselect individual models
                          setSelectedModels(['combined']);
                        } else {
                          setSelectedModels([]);
                        }
                      }}
                      className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <div className="ml-3 flex-1 text-left">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-slate-900">🎯 Combined Analysis (All Models)</span>
                        <span className="px-2 py-0.5 bg-blue-600 text-white text-xs rounded-full">RECOMMENDED</span>
                      </div>
                      <p className="text-xs text-slate-600 mt-1">
                        Runs YOLO, Detectron2, and Floorplan Analyzer together, then intelligently merges their results for the most accurate detection
                      </p>
                    </div>
                  </label>

                  {/* Divider */}
                  <div className="relative py-2">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-gray-300"></div>
                    </div>
                    <div className="relative flex justify-center text-xs">
                      <span className="bg-white px-2 text-gray-500">or select individual models</span>
                    </div>
                  </div>

                  {/* Individual Models */}
                  <label className={`flex items-center cursor-pointer bg-white border-2 rounded-lg p-3 transition-colors ${selectedModels.includes('combined') ? 'opacity-50 cursor-not-allowed border-gray-100' : 'border-gray-200 hover:border-blue-300'}`}>
                    <input
                      type="checkbox"
                      checked={selectedModels.includes('yolo') && !selectedModels.includes('combined')}
                      onChange={(e) => {
                        if (!selectedModels.includes('combined')) {
                          if (e.target.checked) {
                            setSelectedModels([...selectedModels, 'yolo']);
                          } else {
                            setSelectedModels(selectedModels.filter(m => m !== 'yolo'));
                          }
                        }
                      }}
                      disabled={selectedModels.includes('combined')}
                      className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:cursor-not-allowed"
                    />
                    <div className="ml-3 flex-1 text-left">
                      <span className="text-sm font-medium text-slate-800">YOLO</span>
                      <p className="text-xs text-slate-500">Fast object detection with bounding boxes</p>
                    </div>
                  </label>

                  <label className={`flex items-center cursor-pointer bg-white border-2 rounded-lg p-3 transition-colors ${selectedModels.includes('combined') ? 'opacity-50 cursor-not-allowed border-gray-100' : 'border-gray-200 hover:border-purple-300'}`}>
                    <input
                      type="checkbox"
                      checked={selectedModels.includes('detectron2') && !selectedModels.includes('combined')}
                      onChange={(e) => {
                        if (!selectedModels.includes('combined')) {
                          if (e.target.checked) {
                            setSelectedModels([...selectedModels, 'detectron2']);
                          } else {
                            setSelectedModels(selectedModels.filter(m => m !== 'detectron2'));
                          }
                        }
                      }}
                      disabled={selectedModels.includes('combined')}
                      className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500 disabled:cursor-not-allowed"
                    />
                    <div className="ml-3 flex-1 text-left">
                      <span className="text-sm font-medium text-slate-800">Detectron2</span>
                      <p className="text-xs text-slate-500">Advanced segmentation with masks</p>
                    </div>
                  </label>

                  <label className={`flex items-center cursor-pointer bg-white border-2 rounded-lg p-3 transition-colors ${selectedModels.includes('combined') ? 'opacity-50 cursor-not-allowed border-gray-100' : 'border-gray-200 hover:border-green-300'}`}>
                    <input
                      type="checkbox"
                      checked={selectedModels.includes('floorplan') && !selectedModels.includes('combined')}
                      onChange={(e) => {
                        if (!selectedModels.includes('combined')) {
                          if (e.target.checked) {
                            setSelectedModels([...selectedModels, 'floorplan']);
                          } else {
                            setSelectedModels(selectedModels.filter(m => m !== 'floorplan'));
                          }
                        }
                      }}
                      disabled={selectedModels.includes('combined')}
                      className="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500 disabled:cursor-not-allowed"
                    />
                    <div className="ml-3 flex-1 text-left">
                      <span className="text-sm font-medium text-slate-800">Floorplan Analyzer</span>
                      <p className="text-xs text-slate-500">OCR text detection + contour analysis</p>
                    </div>
                  </label>
                </div>
              </div>

              {selectedModels.length > 0 && (
                <div className={`border rounded-lg p-3 max-w-md mx-auto ${
                  selectedModels.includes('combined') 
                    ? 'bg-gradient-to-r from-blue-50 to-purple-50 border-blue-300' 
                    : 'bg-blue-50 border-blue-200'
                }`}>
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                    <p className="text-xs text-blue-800">
                      {selectedModels.includes('combined') ? (
                        <span>
                          <strong>Combined Analysis</strong> - All 3 models will be run and results intelligently merged for maximum accuracy
                        </span>
                      ) : (
                        <span>
                          <strong>{selectedModels.length}</strong> model{selectedModels.length > 1 ? 's' : ''} selected
                          {selectedModels.length > 1 && ' - Compare results side-by-side!'}
                        </span>
                      )}
                    </p>
                  </div>
                </div>
              )}

              {selectedModels.length === 0 && (
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 max-w-md mx-auto">
                  <p className="text-xs text-orange-800">
                    ⚠️ Please select at least one analysis option
                  </p>
                </div>
              )}
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={handleAnalysis}
                disabled={analyzing || selectedModels.length === 0}
                className={`bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold px-8 py-4 rounded-2xl flex items-center gap-3 mx-auto transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 ${(analyzing || selectedModels.length === 0) ? 'opacity-50 cursor-not-allowed' : ''}`}
                style={{
                  fontFamily: "Inter, Poppins, sans-serif",
                  fontSize: "16px",
                  boxShadow: "rgba(59, 130, 246, 0.3) 0px 8px 25px",
                }}
              >
                <FaPlay />
                {analyzing ? 'Analyzing...' : 'Start Analysis'}
              </button>
              <button
                onClick={resetUpload}
                className="bg-white/80 hover:bg-white border border-slate-300 text-slate-700 hover:text-slate-900 font-bold px-8 py-4 rounded-2xl flex items-center gap-3 mx-auto transition-all duration-300 transform hover:scale-105 hover:-translate-y-1"
                style={{
                  fontFamily: "Inter, Poppins, sans-serif",
                  fontSize: "16px",
                  boxShadow: "rgba(0, 0, 0, 0.1) 0px 4px 15px",
                }}
              >
                <FaPlus />
                Upload New Files
              </button>
            </div>
          </div>
        )}

        {/* Analysis Error Display - Only show if analysis failed */}
        {analysisResults && analysisResults.length > 0 && !analysisResults.some((r: any) => r.success) && (
          <div className="mt-8">
            <h3
              className="text-2xl font-bold text-slate-800 mb-6 text-center"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              Analysis Failed
            </h3>
            <div className="space-y-6">
              {analysisResults.map((result: any, index: number) => (
                <div
                  key={index}
                  className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-red-200"
                  style={{ boxShadow: "rgba(0, 0, 0, 0.1) 0px 4px 15px" }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4
                        className="text-lg font-semibold text-slate-800"
                        style={{ fontFamily: "Inter, Poppins, sans-serif" }}
                      >
                        {result.filename}
                      </h4>
                    </div>
                    <span
                      className="px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800"
                      style={{ fontFamily: "Inter, Poppins, sans-serif" }}
                    >
                      Failed
                    </span>
                  </div>
                  <p
                    className="text-red-600"
                    style={{ fontFamily: "Inter, Poppins, sans-serif" }}
                  >
                    Error: {result.error}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}