// Secure storage utilities with encryption
import CryptoJS from 'crypto-js';

interface SecureFileMetadata {
  id: string;
  fileName: string;
  originalName: string;
  fileSize: number;
  fileType: string;
  uploadDate: string;
  encryptedData: string; // Encrypted base64 data
  checksum: string; // For integrity verification
}

interface SecureUploadSession {
  token: string;
  files: SecureFileMetadata[];
  createdAt: string;
  expiresAt: string;
}

// Encryption configuration
const ENCRYPTION_KEY = 'intoAEC_secure_key_2024'; // In production, use environment variable
const SESSION_DURATION = 24 * 60 * 60 * 1000; // 24 hours

// Generate secure session token
export const generateSecureSessionToken = (): string => {
  const timestamp = Date.now();
  const randomBytes = crypto.getRandomValues(new Uint8Array(16));
  const randomString = Array.from(randomBytes, byte => byte.toString(16).padStart(2, '0')).join('');
  return `secure_${timestamp}_${randomString}`;
};

// Encrypt data
const encryptData = (data: string): string => {
  try {
    return CryptoJS.AES.encrypt(data, ENCRYPTION_KEY).toString();
  } catch (error) {
    console.error('Encryption failed:', error);
    throw new Error('Data encryption failed');
  }
};

// Decrypt data
const decryptData = (encryptedData: string): string => {
  try {
    const bytes = CryptoJS.AES.decrypt(encryptedData, ENCRYPTION_KEY);
    return bytes.toString(CryptoJS.enc.Utf8);
  } catch (error) {
    console.error('Decryption failed:', error);
    throw new Error('Data decryption failed');
  }
};

// Generate checksum for integrity verification
const generateChecksum = (data: string): string => {
  return CryptoJS.SHA256(data).toString();
};

// Verify checksum
const verifyChecksum = (data: string, checksum: string): boolean => {
  const calculatedChecksum = generateChecksum(data);
  return calculatedChecksum === checksum;
};

// Secure file to base64 with encryption
export const secureFileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    // Validate file
    if (!file || !(file instanceof File)) {
      reject(new Error('Invalid file object'));
      return;
    }

    if (file.size === 0) {
      reject(new Error('File is empty'));
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      reject(new Error('File size exceeds 10MB limit'));
      return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(file);
    
    reader.onload = () => {
      try {
        const result = reader.result as string;
        const base64Data = result.split(',')[1];
        
        if (!base64Data) {
          reject(new Error('Failed to convert file to base64'));
          return;
        }

        // Encrypt the base64 data
        const encryptedData = encryptData(base64Data);
        resolve(encryptedData);
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = (error) => {
      reject(error);
    };
  });
};

// Save file to secure storage
export const saveFileToSecureStorage = async (
  file: File, 
  sessionToken: string
): Promise<SecureFileMetadata> => {
  try {
    console.log('Converting file to secure base64:', file.name, file.type, file.size);
    
    const encryptedData = await secureFileToBase64(file);
    const checksum = generateChecksum(encryptedData);
    
    const fileMetadata: SecureFileMetadata = {
      id: `secure_file_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`,
      fileName: sanitizeFileName(file.name),
      originalName: file.name,
      fileSize: file.size,
      fileType: file.type || 'application/octet-stream',
      uploadDate: new Date().toISOString(),
      encryptedData: encryptedData,
      checksum: checksum
    };

    // Get existing sessions
    const existingSessions = getSecureSessions();
    
    // Find or create session
    let session = existingSessions.find(s => s.token === sessionToken);
    if (!session) {
      session = {
        token: sessionToken,
        files: [],
        createdAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + SESSION_DURATION).toISOString()
      };
      existingSessions.push(session);
    }

    // Add file to session
    session.files.push(fileMetadata);

    // Save back to localStorage
    localStorage.setItem('intoAEC_secure_sessions', JSON.stringify(existingSessions));
    console.log('Successfully saved to secure storage');

    return fileMetadata;
  } catch (error) {
    console.error('Error saving file to secure storage:', error);
    throw error;
  }
};

// Get secure sessions
export const getSecureSessions = (): SecureUploadSession[] => {
  try {
    const sessions = localStorage.getItem('intoAEC_secure_sessions');
    if (!sessions) return [];
    
    const parsedSessions = JSON.parse(sessions);
    
    // Filter out expired sessions
    const now = new Date();
    const validSessions = parsedSessions.filter((session: SecureUploadSession) => 
      new Date(session.expiresAt) > now
    );
    
    // Update localStorage with filtered sessions
    if (validSessions.length !== parsedSessions.length) {
      localStorage.setItem('intoAEC_secure_sessions', JSON.stringify(validSessions));
    }
    
    return validSessions;
  } catch (error) {
    console.error('Error reading secure sessions:', error);
    return [];
  }
};

// Get files for a specific session
export const getSecureFilesForSession = (sessionToken: string): SecureFileMetadata[] => {
  const sessions = getSecureSessions();
  const session = sessions.find(s => s.token === sessionToken);
  return session ? session.files : [];
};

// Get the latest file for a session
export const getLatestSecureFileForSession = (sessionToken: string): SecureFileMetadata | null => {
  const files = getSecureFilesForSession(sessionToken);
  if (files.length === 0) return null;
  
  return files.sort((a, b) => new Date(b.uploadDate).getTime() - new Date(a.uploadDate).getTime())[0];
};

// Decrypt and create data URL
export const createSecureDataUrl = (fileMetadata: SecureFileMetadata): string => {
  try {
    const decryptedData = decryptData(fileMetadata.encryptedData);
    
    // Verify integrity
    if (!verifyChecksum(decryptedData, fileMetadata.checksum)) {
      throw new Error('File integrity check failed');
    }
    
    return `data:${fileMetadata.fileType};base64,${decryptedData}`;
  } catch (error) {
    console.error('Error creating secure data URL:', error);
    throw new Error('Failed to decrypt file data');
  }
};

// Sanitize filename
const sanitizeFileName = (filename: string): string => {
  // Remove path components
  const basename = filename.split('/').pop() || filename;
  
  // Remove dangerous characters
  const sanitized = basename.replace(/[<>:"/\\|?*]/g, '_');
  
  // Limit length
  if (sanitized.length > 255) {
    const ext = sanitized.split('.').pop();
    const name = sanitized.substring(0, 255 - ext.length - 1);
    return `${name}.${ext}`;
  }
  
  return sanitized || `file_${Date.now()}`;
};

// Clear expired sessions
export const clearExpiredSessions = (): void => {
  const sessions = getSecureSessions();
  console.log(`Cleared ${sessions.length} expired sessions`);
};

// Clear all secure storage
export const clearAllSecureStorage = (): void => {
  localStorage.removeItem('intoAEC_secure_sessions');
  console.log('Cleared all secure storage data');
};

// Get storage usage info
export const getSecureStorageInfo = (): { 
  sessions: number; 
  totalFiles: number; 
  totalSize: number;
  expiredSessions: number;
} => {
  const sessions = getSecureSessions();
  const totalFiles = sessions.reduce((sum, session) => sum + session.files.length, 0);
  const totalSize = sessions.reduce((sum, session) => 
    sum + session.files.reduce((fileSum, file) => fileSum + file.fileSize, 0), 0
  );
  
  return {
    sessions: sessions.length,
    totalFiles,
    totalSize,
    expiredSessions: 0 // This would need to be calculated based on expiration
  };
};

// Authentication utilities
export const setAuthToken = (token: string): void => {
  localStorage.setItem('auth_token', token);
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

export const clearAuthToken = (): void => {
  localStorage.removeItem('auth_token');
};

// API request with authentication
export const makeAuthenticatedRequest = async (
  url: string, 
  options: RequestInit = {}
): Promise<Response> => {
  const token = getAuthToken();
  
  if (!token) {
    throw new Error('No authentication token found');
  }
  
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  return fetch(url, {
    ...options,
    headers
  });
};
