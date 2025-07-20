import axios from 'axios';

// Base API configuration
const API_BASE_URL = 'http://localhost:8000'; // Adjust this to your backend URL

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions

// 1. Get list of models
export const getModels = async () => {
  try {
    const response = await apiClient.get('/models');
    return response.data;
  } catch (error) {
    console.error('Error fetching models:', error);
    // Return mock data if API fails
    return [
      { id: 'model-a', name: 'Model A', description: 'Advanced image analysis model' },
      { id: 'model-b', name: 'Model B', description: 'High-performance captioning model' },
      { id: 'model-c', name: 'Model C', description: 'Multi-purpose AI model' },
      { id: 'model-d', name: 'Model D', description: 'Specialized search model' }
    ];
  }
};

// 2. Caption Search - POST /caption with image file and model parameter
export const getCaption = async (imageFile, model) => {
  try {
    const formData = new FormData();
    formData.append('image_file', imageFile);
    formData.append('model', model);

    const response = await apiClient.post('/caption', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('Error getting caption:', error);
    // Return mock data if API fails
    return {
      captions: [
        'A beautiful landscape with mountains in the background.',
        'Scenic view of nature with trees and sky.',
        'Outdoor photography capturing natural beauty.',
        'Peaceful mountain scenery with clear blue sky.'
      ]
    };
  }
};

// 2b. Multiple Caption Search - POST /caption with multiple image files
export const getMultipleCaptions = async (imageFiles, model) => {
  try {
    const formData = new FormData();
    
    // Append multiple files
    imageFiles.forEach((file, index) => {
      formData.append(`image_files`, file);
    });
    formData.append('model', model);

    const response = await apiClient.post('/caption_multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('Error getting multiple captions:', error);
    // Return mock data if API fails - single combined caption
    return {
      captions: [
        `A collection of ${imageFiles.length} diverse images showcasing various subjects and scenes.`,
        `Multiple photographs featuring different perspectives and compositions.`,
        `A varied set of images with rich visual content and interesting details.`,
        `An assortment of pictures displaying different themes and visual elements.`
      ]
    };
  }
};

// 3. Similar Images Search - POST /search_similar with image file and model parameter
export const searchSimilar = async (imageFile, model) => {
  try {
    const formData = new FormData();
    formData.append('image_file', imageFile);
    formData.append('model', model);

    const response = await apiClient.post('/search_similar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('Error searching similar images:', error);
    // Return mock data if API fails
    return {
      images: [
        'https://picsum.photos/200/200?random=1',
        'https://picsum.photos/200/200?random=2',
        'https://picsum.photos/200/200?random=3',
        'https://picsum.photos/200/200?random=4',
        'https://picsum.photos/200/200?random=5',
        'https://picsum.photos/200/200?random=6'
      ]
    };
  }
};

// 3b. Multiple Similar Images Search - POST /search_similar with multiple image files
export const searchMultipleSimilar = async (imageFiles, model) => {
  try {
    const formData = new FormData();
    
    // Append multiple files
    imageFiles.forEach((file, index) => {
      formData.append(`image_files`, file);
    });
    formData.append('model', model);

    const response = await apiClient.post('/search_similar_multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('Error searching multiple similar images:', error);
    // Return mock data if API fails - process each file individually
    const results = [];
    for (let i = 0; i < imageFiles.length; i++) {
      results.push({
        file: {
          originalname: imageFiles[i].name,
          size: imageFiles[i].size,
          mimetype: imageFiles[i].type
        },
        images: [
          `https://picsum.photos/200/200?random=${i * 6 + 1}`,
          `https://picsum.photos/200/200?random=${i * 6 + 2}`,
          `https://picsum.photos/200/200?random=${i * 6 + 3}`,
          `https://picsum.photos/200/200?random=${i * 6 + 4}`,
          `https://picsum.photos/200/200?random=${i * 6 + 5}`,
          `https://picsum.photos/200/200?random=${i * 6 + 6}`
        ]
      });
    }
    return { results };
  }
};

// 4. Plain text search - POST /search with text and model parameter
export const searchImages = async (searchText, model) => {
  try {
    const response = await apiClient.post('/search', {
      query: searchText,
      model: model
    });
    
    return response.data;
  } catch (error) {
    console.error('Error searching images:', error);
    // Return mock data if API fails
    return {
      images: [
        'https://picsum.photos/200/200?random=7',
        'https://picsum.photos/200/200?random=8',
        'https://picsum.photos/200/200?random=9',
        'https://picsum.photos/200/200?random=10',
        'https://picsum.photos/200/200?random=11',
        'https://picsum.photos/200/200?random=12'
      ]
    };
  }
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
