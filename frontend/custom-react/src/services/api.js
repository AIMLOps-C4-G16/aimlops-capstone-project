import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:4488'; // Adjust this to your backend URL
const IMAGE_API_URL = process.env.REACT_APP_IMAGE_API_URL || 'http://localhost:4488'; // For image fetches by ID

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Unified process API
export const processImages = async ({ query, files }) => {
  try {
    const formData = new FormData();
    formData.append('query', query);
    if (files && files.length > 0) {
      files.forEach(file => formData.append('files', file));
    }
    const response = await apiClient.post('/process/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error in processImages:', error);
    throw error;
  }
};

// 1. getMultipleCaptions: query=caption, files required
export const getMultipleCaptions = async (files) => {
  const data = await processImages({ query: 'caption', files });
  return data.result.caption;
};

// 2. searchMultipleSimilar: query=similar, files required
export const searchMultipleSimilar = async (files) => {
  const data = await processImages({ query: 'similar', files });
  return data.result.similar_images?.map(image => getImageById(image));
};

// 1. getMultipleCaptions: query=caption, files required
export const getQuerySearch = async (query, files) => {
  const data = await processImages({ query: query, files });
  if(data?.result?.search_images){
    data.result.search_images = data.result.search_images?.map(image => getImageById(image));
  } 
  if(data?.result?.similar_images){
    data.result.similar_images = data.result.similar_images?.map(image => getImageById(image));
  }
  return data.result;
};

// 3. searchImages: query=searchText, no files
export const searchImages = async (searchText) => {
  const data = await processImages({ query: searchText });
  if(data.result?.search_images){
    return data.result.search_images?.map(image => getImageById(image));
  } 
  return data.result;
};

// Get image by ID for display
export const getImageById = (imageId) => {
  return `${IMAGE_API_URL}/image/${imageId}`;
};

// Helper function to validate image file
export const validateImageFile = (file) => {
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  const maxSize = 10 * 1024 * 1024; // 10MB

  if (!allowedTypes.includes(file.type)) {
    throw new Error('Please upload an image file (JPEG, PNG, GIF, or WebP)');
  }

  if (file.size > maxSize) {
    throw new Error('File size must be less than 10MB');
  }

  return true;
};
