# AI Image Assistant Backend

A temporary Node.js backend API server for the AI Image Assistant frontend.

## Features

- **Models API**: Get list of available AI models
- **Caption Generation**: Generate captions for uploaded images
- **Similar Image Search**: Find similar images based on uploaded image
- **Text-based Image Search**: Search images using text queries
- **File Upload Support**: Handle image file uploads (max 10MB)
- **CORS Enabled**: Configured for frontend integration

## API Endpoints

### GET /models
Returns list of available AI models.

**Response:**
```json
[
  {
    "id": "model-a",
    "name": "Model A",
    "description": "Advanced image analysis model"
  }
]
```

### POST /caption
Generate captions for an uploaded image.

**Request:**
- `image_file`: Image file (multipart/form-data)
- `model`: Model ID (form field)

**Response:**
```json
{
  "captions": [
    "A beautiful landscape with mountains in the background.",
    "Scenic view of nature with trees and sky."
  ]
}
```

### POST /search_similar
Find similar images based on uploaded image.

**Request:**
- `image_file`: Image file (multipart/form-data)
- `model`: Model ID (form field)

**Response:**
```json
{
  "images": [
    "https://picsum.photos/200/200?random=1",
    "https://picsum.photos/200/200?random=2"
  ]
}
```

### POST /search
Search images using text query.

**Request:**
```json
{
  "query": "mountain landscape",
  "model": "model-a"
}
```

**Response:**
```json
{
  "images": [
    "https://picsum.photos/200/200?random=1",
    "https://picsum.photos/200/200?random=2"
  ]
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "OK",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
npm install
```

3. Start the server:
```bash
npm start
```

For development with auto-restart:
```bash
npm run dev
```

## Configuration

- **Port**: 8000 (configurable in server.js)
- **File Upload Limit**: 10MB
- **Allowed File Types**: Images only (JPEG, PNG, GIF, WebP)
- **CORS**: Enabled for frontend integration

## Usage

The server will start on `http://localhost:8000` and is ready to accept requests from the frontend application.

All endpoints return mock data with simulated processing delays to mimic real API behavior. 