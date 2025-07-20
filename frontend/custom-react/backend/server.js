const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 8000;

// Middleware
app.use(cors());
app.use(express.json());

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ 
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    // Check file type
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'), false);
    }
  }
});

// Configure multer for multiple file uploads
const uploadMultiple = multer({ 
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit per file
    files: 10 // Maximum 10 files
  },
  fileFilter: (req, file, cb) => {
    // Check file type
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'), false);
    }
  }
});

// Mock data
const mockModels = [
  { id: 'model-a', name: 'Model A', description: 'Advanced image analysis model' },
  { id: 'model-b', name: 'Model B', description: 'High-performance captioning model' },
  { id: 'model-c', name: 'Model C', description: 'Multi-purpose AI model' },
  { id: 'model-d', name: 'Model D', description: 'Specialized search model' }
];

const mockCaptions = [
  'A beautiful landscape with mountains in the background.',
  'Scenic view of nature with trees and sky.',
  'Outdoor photography capturing natural beauty.',
  'Peaceful mountain scenery with clear blue sky.',
  'Stunning sunset over the horizon.',
  'Majestic peaks reaching into the clouds.',
  'Serene lake reflecting the surrounding mountains.',
  'Vibrant autumn colors in the forest.'
];

const mockImages = [
  'https://picsum.photos/200/200?random=1',
  'https://picsum.photos/200/200?random=2',
  'https://picsum.photos/200/200?random=3',
  'https://picsum.photos/200/200?random=4',
  'https://picsum.photos/200/200?random=5',
  'https://picsum.photos/200/200?random=6',
  'https://picsum.photos/200/200?random=7',
  'https://picsum.photos/200/200?random=8'
];

// Helper function to get random items from array
const getRandomItems = (array, count) => {
  const shuffled = [...array].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
};

// Helper function to simulate API delay
const simulateDelay = (ms = 1000) => new Promise(resolve => setTimeout(resolve, ms));

// Routes

// GET /models - Get list of available models
app.get('/models', async (req, res) => {
  try {
    await simulateDelay(500);
    res.json(mockModels);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch models' });
  }
});

// POST /caption - Generate captions for uploaded image
app.post('/caption', upload.single('image_file'), async (req, res) => {
  try {
    const { model } = req.body;
    const imageFile = req.file;

    if (!imageFile) {
      return res.status(400).json({ error: 'No image file provided' });
    }

    if (!model) {
      return res.status(400).json({ error: 'Model parameter is required' });
    }

    console.log(`Caption request - Model: ${model}, File: ${imageFile.originalname}, Size: ${imageFile.size} bytes`);

    await simulateDelay(2000); // Simulate processing time

    // Return 3-5 random captions
    const captions = getRandomItems(mockCaptions, Math.floor(Math.random() * 3) + 3);
    
    res.json({ captions });
  } catch (error) {
    console.error('Caption error:', error);
    res.status(500).json({ error: 'Failed to generate captions' });
  }
});

// POST /search_similar - Find similar images
app.post('/search_similar', upload.single('image_file'), async (req, res) => {
  try {
    const { model } = req.body;
    const imageFile = req.file;

    if (!imageFile) {
      return res.status(400).json({ error: 'No image file provided' });
    }

    if (!model) {
      return res.status(400).json({ error: 'Model parameter is required' });
    }

    console.log(`Similar search request - Model: ${model}, File: ${imageFile.originalname}, Size: ${imageFile.size} bytes`);

    await simulateDelay(2500); // Simulate processing time

    // Return 4-8 random similar images
    const images = getRandomItems(mockImages, Math.floor(Math.random() * 4) + 4);
    
    res.json({ images });
  } catch (error) {
    console.error('Similar search error:', error);
    res.status(500).json({ error: 'Failed to find similar images' });
  }
});

// POST /caption_multiple - Generate captions for multiple uploaded images
app.post('/caption_multiple', uploadMultiple.array('image_files', 10), async (req, res) => {
  try {
    const { model } = req.body;
    const imageFiles = req.files;

    if (!imageFiles || imageFiles.length === 0) {
      return res.status(400).json({ error: 'No image files provided' });
    }

    if (!model) {
      return res.status(400).json({ error: 'Model parameter is required' });
    }

    console.log(`Multiple caption request - Model: ${model}, Files: ${imageFiles.length}`);

    await simulateDelay(2000 * imageFiles.length); // Simulate processing time based on file count

    // Generate a single combined caption for all images
    const combinedCaptions = [
      `A collection of ${imageFiles.length} diverse images showcasing various subjects and scenes.`,
      `Multiple photographs featuring different perspectives and compositions.`,
      `A varied set of images with rich visual content and interesting details.`,
      `An assortment of pictures displaying different themes and visual elements.`
    ];
    
    res.json({ captions: combinedCaptions });
  } catch (error) {
    console.error('Multiple caption error:', error);
    res.status(500).json({ error: 'Failed to generate captions' });
  }
});

// POST /search_similar_multiple - Find similar images for multiple files
app.post('/search_similar_multiple', uploadMultiple.array('image_files', 10), async (req, res) => {
  try {
    const { model } = req.body;
    const imageFiles = req.files;

    if (!imageFiles || imageFiles.length === 0) {
      return res.status(400).json({ error: 'No image files provided' });
    }

    if (!model) {
      return res.status(400).json({ error: 'Model parameter is required' });
    }

    console.log(`Multiple similar search request - Model: ${model}, Files: ${imageFiles.length}`);

    await simulateDelay(2500 * imageFiles.length); // Simulate processing time based on file count

    // Process each file and return results
    const results = imageFiles.map((file, index) => {
      const images = getRandomItems(mockImages, Math.floor(Math.random() * 4) + 4);
      return {
        file: {
          originalname: file.originalname,
          size: file.size,
          mimetype: file.mimetype
        },
        images
      };
    });
    
    res.json({ results });
  } catch (error) {
    console.error('Multiple similar search error:', error);
    res.status(500).json({ error: 'Failed to find similar images' });
  }
});

// POST /search - Search images by text query
app.post('/search', async (req, res) => {
  try {
    const { query, model } = req.body;

    if (!query) {
      return res.status(400).json({ error: 'Query parameter is required' });
    }

    if (!model) {
      return res.status(400).json({ error: 'Model parameter is required' });
    }

    console.log(`Text search request - Model: ${model}, Query: "${query}"`);

    await simulateDelay(1500); // Simulate processing time

    // Return 4-8 random images based on query
    const images = getRandomItems(mockImages, Math.floor(Math.random() * 4) + 4);
    
    res.json({ images });
  } catch (error) {
    console.error('Text search error:', error);
    res.status(500).json({ error: 'Failed to search images' });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Server error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Backend server running on http://localhost:${PORT}`);
  console.log(`📋 Available endpoints:`);
  console.log(`   GET  /health - Health check`);
  console.log(`   GET  /models - Get available models`);
  console.log(`   POST /caption - Generate image captions`);
  console.log(`   POST /caption_multiple - Generate captions for multiple images`);
  console.log(`   POST /search_similar - Find similar images`);
  console.log(`   POST /search_similar_multiple - Find similar images for multiple files`);
  console.log(`   POST /search - Search images by text`);
  console.log(`\n🔧 CORS enabled for frontend integration`);
  console.log(`📁 File uploads supported (max 10MB per file, up to 10 files)`);
}); 