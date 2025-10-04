// lib/localStorageUtils.ts

export interface FileMetadata {
  id: string;
  fileName: string;
  originalName: string;
  fileSize: number;
  fileType: string;
  uploadDate: string;
  fileData: string; // base64 encoded file data
}

export interface UploadSession {
  token: string;
  files: FileMetadata[];
  createdAt: string;
}

const STORAGE_KEY = 'intoAEC_files';
const SESSION_KEY = 'intoAEC_sessions';

// Generate a unique token for each upload session
export const generateSessionToken = (): string => {
  return `session_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
};

// Convert file to base64
export const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    console.log('FileReader processing file:', {
      name: file.name,
      type: file.type,
      size: file.size,
      lastModified: file.lastModified
    });
    
    // Validate that this is actually a file and not form data
    if (!file || !(file instanceof File)) {
      reject(new Error('Invalid file object'));
      return;
    }
    
    if (file.size === 0) {
      reject(new Error('File is empty'));
      return;
    }
    
    // For images, check if the file starts with proper image headers
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.readAsArrayBuffer(file);
      reader.onload = () => {
        const arrayBuffer = reader.result as ArrayBuffer;
        const uint8Array = new Uint8Array(arrayBuffer);
        
        // Check for common image file signatures
        const isPNG = uint8Array[0] === 0x89 && uint8Array[1] === 0x50 && uint8Array[2] === 0x4E && uint8Array[3] === 0x47;
        const isJPEG = uint8Array[0] === 0xFF && uint8Array[1] === 0xD8;
        
        console.log('File signature check:', { isPNG, isJPEG, firstBytes: Array.from(uint8Array.slice(0, 8)) });
        
        if (!isPNG && !isJPEG && file.type.startsWith('image/')) {
          console.warn('File does not appear to be a valid image based on file signature');
        }
        
        // Now read as data URL
        const dataReader = new FileReader();
        dataReader.readAsDataURL(file);
        dataReader.onload = () => {
          const result = dataReader.result as string;
          console.log('FileReader result length:', result.length);
          console.log('FileReader result preview:', result.substring(0, 100));
          
          // Remove the data URL prefix (e.g., "data:image/png;base64,")
          const base64 = result.split(',')[1];
          if (!base64) {
            console.error('No base64 data found in result');
            reject(new Error('Failed to convert file to base64'));
            return;
          }
          
          console.log('Base64 data length:', base64.length);
          console.log('Base64 data preview:', base64.substring(0, 50));
          
          resolve(base64);
        };
        dataReader.onerror = error => {
          console.error('Data URL FileReader error:', error);
          reject(error);
        };
      };
      reader.onerror = error => {
        console.error('ArrayBuffer FileReader error:', error);
        reject(error);
      };
    } else {
      // For non-images, just read as data URL
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        console.log('FileReader result length:', result.length);
        console.log('FileReader result preview:', result.substring(0, 100));
        
        // Remove the data URL prefix (e.g., "data:image/png;base64,")
        const base64 = result.split(',')[1];
        if (!base64) {
          console.error('No base64 data found in result');
          reject(new Error('Failed to convert file to base64'));
          return;
        }
        
        console.log('Base64 data length:', base64.length);
        console.log('Base64 data preview:', base64.substring(0, 50));
        
        resolve(base64);
      };
      reader.onerror = error => {
        console.error('FileReader error:', error);
        reject(error);
      };
    }
  });
};

// Convert base64 back to blob for display
export const base64ToBlob = (base64: string, mimeType: string): Blob => {
  const byteCharacters = atob(base64);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: mimeType });
};

// Save file to local storage using alternative method
export const saveFileToStorageAlt = async (file: File, sessionToken: string): Promise<FileMetadata> => {
  try {
    console.log('Converting file to base64 (alternative method):', file.name, file.type, file.size);
    
    // Use alternative file processing
    const { fileToBase64Alternative } = await import('./fileUtils');
    const fileData = await fileToBase64Alternative(file);
    console.log('Base64 conversion successful, length:', fileData.length);
    
    const fileMetadata: FileMetadata = {
      id: `file_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`,
      fileName: file.name,
      originalName: file.name,
      fileSize: file.size,
      fileType: file.type || 'application/octet-stream',
      uploadDate: new Date().toISOString(),
      fileData: fileData
    };

    // Get existing sessions
    const existingSessions = getSessions();
    
    // Find or create session
    let session = existingSessions.find(s => s.token === sessionToken);
    if (!session) {
      session = {
        token: sessionToken,
        files: [],
        createdAt: new Date().toISOString()
      };
      existingSessions.push(session);
    }

    // Add file to session
    session.files.push(fileMetadata);

    // Save back to localStorage
    console.log('Saving to localStorage, sessions count:', existingSessions.length);
    localStorage.setItem(SESSION_KEY, JSON.stringify(existingSessions));
    console.log('Successfully saved to localStorage');

    return fileMetadata;
  } catch (error) {
    console.error('Error saving file to storage (alternative method):', error);
    throw error;
  }
};

// Save file to local storage (original method)
export const saveFileToStorage = async (file: File, sessionToken: string): Promise<FileMetadata> => {
  try {
    console.log('Converting file to base64:', file.name, file.type, file.size);
    const fileData = await fileToBase64(file);
    console.log('Base64 conversion successful, length:', fileData.length);
    
    const fileMetadata: FileMetadata = {
      id: `file_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`,
      fileName: file.name,
      originalName: file.name,
      fileSize: file.size,
      fileType: file.type || 'application/octet-stream',
      uploadDate: new Date().toISOString(),
      fileData: fileData
    };

    // Get existing sessions
    const existingSessions = getSessions();
    
    // Find or create session
    let session = existingSessions.find(s => s.token === sessionToken);
    if (!session) {
      session = {
        token: sessionToken,
        files: [],
        createdAt: new Date().toISOString()
      };
      existingSessions.push(session);
    }

    // Add file to session
    session.files.push(fileMetadata);

    // Save back to localStorage
    console.log('Saving to localStorage, sessions count:', existingSessions.length);
    localStorage.setItem(SESSION_KEY, JSON.stringify(existingSessions));
    console.log('Successfully saved to localStorage');

    return fileMetadata;
  } catch (error) {
    console.error('Error saving file to storage:', error);
    throw error;
  }
};

// Get all sessions
export const getSessions = (): UploadSession[] => {
  try {
    const sessions = localStorage.getItem(SESSION_KEY);
    return sessions ? JSON.parse(sessions) : [];
  } catch (error) {
    console.error('Error reading sessions from storage:', error);
    return [];
  }
};

// Get files for a specific session
export const getFilesForSession = (sessionToken: string): FileMetadata[] => {
  const sessions = getSessions();
  const session = sessions.find(s => s.token === sessionToken);
  return session ? session.files : [];
};

// Get the latest file for a session
export const getLatestFileForSession = (sessionToken: string): FileMetadata | null => {
  const files = getFilesForSession(sessionToken);
  if (files.length === 0) return null;
  
  // Sort by upload date and get the latest
  return files.sort((a, b) => new Date(b.uploadDate).getTime() - new Date(a.uploadDate).getTime())[0];
};

// Create a blob URL for file display
export const createFileUrl = (fileMetadata: FileMetadata): string => {
  try {
    const blob = base64ToBlob(fileMetadata.fileData, fileMetadata.fileType);
    return URL.createObjectURL(blob);
  } catch (error) {
    console.error('Error creating blob URL:', error);
    // Fallback to data URL
    return `data:${fileMetadata.fileType};base64,${fileMetadata.fileData}`;
  }
};

// Create a data URL directly (alternative method)
export const createDataUrl = (fileMetadata: FileMetadata): string => {
  return `data:${fileMetadata.fileType};base64,${fileMetadata.fileData}`;
};

// Clean up blob URLs to prevent memory leaks
export const revokeFileUrl = (url: string): void => {
  URL.revokeObjectURL(url);
};

// Get file type for display purposes
export const getFileDisplayType = (fileName: string): 'image' | 'pdf' | 'cad' | 'unknown' => {
  const lowerName = fileName.toLowerCase();
  if (lowerName.endsWith('.pdf')) return 'pdf';
  if (lowerName.endsWith('.png') || lowerName.endsWith('.jpg') || lowerName.endsWith('.jpeg')) return 'image';
  if (lowerName.endsWith('.dwg')) return 'cad';
  return 'unknown';
};

// Clear all stored data (useful for testing)
export const clearAllStorage = (): void => {
  localStorage.removeItem(SESSION_KEY);
  localStorage.removeItem(STORAGE_KEY);
  console.log('Cleared all local storage data');
};

// Clear data for a specific session
export const clearSessionData = (sessionToken: string): void => {
  const sessions = getSessions();
  const filteredSessions = sessions.filter(s => s.token !== sessionToken);
  localStorage.setItem(SESSION_KEY, JSON.stringify(filteredSessions));
  console.log(`Cleared data for session: ${sessionToken}`);
};

// Get storage usage info
export const getStorageInfo = (): { sessions: number; totalFiles: number; totalSize: number } => {
  const sessions = getSessions();
  const totalFiles = sessions.reduce((sum, session) => sum + session.files.length, 0);
  const totalSize = sessions.reduce((sum, session) => 
    sum + session.files.reduce((fileSum, file) => fileSum + file.fileSize, 0), 0
  );
  
  return {
    sessions: sessions.length,
    totalFiles,
    totalSize
  };
};

// Analysis Results Storage
const ANALYSIS_RESULTS_KEY = 'intoAEC_analysisResults';

export const saveAnalysisResults = (sessionToken: string, results: any[]): void => {
  try {
    localStorage.setItem(ANALYSIS_RESULTS_KEY, JSON.stringify({
      sessionToken,
      results,
      timestamp: new Date().toISOString()
    }));
    console.log('Analysis results saved to localStorage');
  } catch (error) {
    console.error('Error saving analysis results:', error);
  }
};

export const getAnalysisResults = (sessionToken?: string): any[] => {
  try {
    const data = localStorage.getItem(ANALYSIS_RESULTS_KEY);
    if (!data) return [];
    
    const parsed = JSON.parse(data);
    
    // If sessionToken is provided, only return results for that session
    if (sessionToken && parsed.sessionToken !== sessionToken) {
      return [];
    }
    
    return parsed.results || [];
  } catch (error) {
    console.error('Error reading analysis results:', error);
    return [];
  }
};

export const clearAnalysisResults = (): void => {
  localStorage.removeItem(ANALYSIS_RESULTS_KEY);
  console.log('Analysis results cleared');
};
