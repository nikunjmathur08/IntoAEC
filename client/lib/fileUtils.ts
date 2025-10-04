// Alternative file handling utilities

// Convert file to base64 using a different approach
export const fileToBase64Alternative = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    console.log('Alternative file processing:', {
      name: file.name,
      type: file.type,
      size: file.size,
      lastModified: file.lastModified
    });

    // Method 1: Try using FileReader with readAsArrayBuffer first
    const reader = new FileReader();
    reader.readAsArrayBuffer(file);
    reader.onload = () => {
      const arrayBuffer = reader.result as ArrayBuffer;
      const uint8Array = new Uint8Array(arrayBuffer);
      
      console.log('File loaded as ArrayBuffer, size:', arrayBuffer.byteLength);
      console.log('First 20 bytes:', Array.from(uint8Array.slice(0, 20)));
      
      // Check if it's a valid image by looking at the file signature
      if (file.type.startsWith('image/png')) {
        const isPNG = uint8Array[0] === 0x89 && uint8Array[1] === 0x50 && uint8Array[2] === 0x4E && uint8Array[3] === 0x47;
        if (!isPNG) {
          console.error('File does not have PNG signature');
          reject(new Error('File does not appear to be a valid PNG'));
          return;
        }
      } else if (file.type.startsWith('image/jpeg')) {
        const isJPEG = uint8Array[0] === 0xFF && uint8Array[1] === 0xD8;
        if (!isJPEG) {
          console.error('File does not have JPEG signature');
          reject(new Error('File does not appear to be a valid JPEG'));
          return;
        }
      }
      
      // Convert ArrayBuffer to base64
      let binary = '';
      const bytes = new Uint8Array(arrayBuffer);
      const len = bytes.byteLength;
      for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      const base64 = btoa(binary);
      
      console.log('Converted to base64, length:', base64.length);
      console.log('Base64 preview:', base64.substring(0, 50));
      
      resolve(base64);
    };
    
    reader.onerror = (error) => {
      console.error('FileReader error:', error);
      reject(error);
    };
  });
};

// Test if a file is valid by checking its content
export const validateFile = async (file: File): Promise<boolean> => {
  try {
    const arrayBuffer = await file.arrayBuffer();
    const uint8Array = new Uint8Array(arrayBuffer);
    
    console.log('Validating file:', file.name);
    console.log('File size:', file.size);
    console.log('ArrayBuffer size:', arrayBuffer.byteLength);
    console.log('First 10 bytes:', Array.from(uint8Array.slice(0, 10)));
    
    // Check for form data signatures
    const textDecoder = new TextDecoder();
    const firstChunk = textDecoder.decode(uint8Array.slice(0, 100));
    console.log('First 100 chars as text:', firstChunk);
    
    if (firstChunk.includes('WebKitFormBoundary') || firstChunk.includes('Content-Disposition')) {
      console.error('File contains form data instead of actual file content');
      return false;
    }
    
    // Check for valid image signatures
    if (file.type.startsWith('image/png')) {
      const isPNG = uint8Array[0] === 0x89 && uint8Array[1] === 0x50 && uint8Array[2] === 0x4E && uint8Array[3] === 0x47;
      console.log('PNG signature check:', isPNG);
      return isPNG;
    }
    
    if (file.type.startsWith('image/jpeg')) {
      const isJPEG = uint8Array[0] === 0xFF && uint8Array[1] === 0xD8;
      console.log('JPEG signature check:', isJPEG);
      return isJPEG;
    }
    
    // For other file types, just check it's not form data
    return true;
    
  } catch (error) {
    console.error('File validation error:', error);
    return false;
  }
};

// Create a data URL from file using alternative method
export const createDataUrlFromFile = async (file: File): Promise<string> => {
  try {
    const base64 = await fileToBase64Alternative(file);
    return `data:${file.type};base64,${base64}`;
  } catch (error) {
    console.error('Error creating data URL:', error);
    throw error;
  }
};
