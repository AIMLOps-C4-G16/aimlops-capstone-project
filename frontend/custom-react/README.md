# AI Image Assistant - Frontend & Backend

A React-based frontend application with a Node.js backend for AI-powered image analysis, captioning, and search functionality.

## Project Structure

```
custom-react/
├── backend/           # Node.js Express server
│   ├── package.json
│   ├── server.js
│   └── README.md
├── src/              # React frontend application
│   ├── components/   # React components
│   ├── services/     # API service functions
│   └── ...
├── package.json      # Frontend dependencies
└── README.md         # This file
```

## Prerequisites

- **Node.js** (version 16 or higher)
- **npm** (comes with Node.js)
- **Git** (for cloning the repository)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd custom-react
```

### 2. Install Frontend Dependencies

```bash
# Install React frontend dependencies
npm install
```

**Frontend Dependencies:**
- React 19.1.0
- React DOM 19.1.0
- Axios (for API calls)
- React OAuth Google
- JWT Decode
- React Scripts

### 3. Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Install backend dependencies
npm install
```

**Backend Dependencies:**
- Express.js (web framework)
- Multer (file upload handling)
- CORS (Cross-Origin Resource Sharing)
- Nodemon (development server)

## Starting the Servers

### Option 1: Start Both Servers (Recommended)

Open two terminal windows/tabs:

**Terminal 1 - Backend Server:**
```bash
cd backend
npm start
# or for development with auto-restart:
npm run dev
```

**Terminal 2 - Frontend Server:**
```bash
# From the root directory
npm start
```

### Option 2: Start Servers Individually

**Backend Server:**
```bash
cd backend
npm start          # Production mode
npm run dev        # Development mode with auto-restart
```

**Frontend Server:**
```bash
npm start          # Starts React development server
```

## Server URLs & Ports

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000

## Backend URL Configuration

The backend URL is configured in the frontend API service file:

**File:** `src/services/api.js`

```javascript
// Line 4: Change this URL to match your backend server
const API_BASE_URL = 'http://localhost:8000';
```

### Configuration Options:

1. **Local Development:**
   ```javascript
   const API_BASE_URL = 'http://localhost:8000';
   ```

2. **Production/Remote Backend:**
   ```javascript
   const API_BASE_URL = 'https://your-backend-domain.com';
   ```

3. **Different Port:**
   ```javascript
   const API_BASE_URL = 'http://localhost:5000'; // If backend runs on port 5000
   ```

4. **Environment Variable (Recommended for production):**
   ```javascript
   const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
   ```

## Available Scripts

### Frontend Scripts (from root directory)
```bash
npm start          # Start development server
npm run build      # Build for production
npm test           # Run tests
npm run eject      # Eject from Create React App
```

### Backend Scripts (from backend directory)
```bash
npm start          # Start production server
npm run dev        # Start development server with auto-restart
```

## API Endpoints

The backend provides the following endpoints:

- `GET /models` - Get available AI models
- `POST /caption` - Generate captions for uploaded image
- `POST /caption_multiple` - Generate captions for multiple images
- `POST /search_similar` - Find similar images
- `POST /search_similar_multiple` - Find similar images for multiple files
- `POST /search` - Text-based image search

## Development Notes

### File Upload Limits
- Maximum file size: 10MB per image
- Supported formats: JPEG, PNG, GIF, WebP
- Maximum files per request: 10 (for multiple uploads)

### CORS Configuration
The backend is configured to allow requests from the frontend development server. If you change the frontend port, update the CORS configuration in `backend/server.js`.

### Environment Variables
For production deployment, consider using environment variables for:
- Backend URL
- API keys
- Database connections
- Port configurations

## Troubleshooting

### Common Issues:

1. **Port Already in Use:**
   ```bash
   # Kill process on port 3000 (frontend)
   lsof -ti:3000 | xargs kill -9
   
   # Kill process on port 8000 (backend)
   lsof -ti:8000 | xargs kill -9
   ```

2. **Module Not Found Errors:**
   ```bash
   # Clear npm cache and reinstall
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **CORS Errors:**
   - Ensure backend is running on port 8000
   - Check that frontend is making requests to the correct backend URL
   - Verify CORS configuration in `backend/server.js`

4. **File Upload Issues:**
   - Check file size (must be < 10MB)
   - Verify file format (JPEG, PNG, GIF, WebP only)
   - Ensure proper form data structure

## Production Deployment

### Frontend Build:
```bash
npm run build
```

### Backend Production:
```bash
cd backend
npm start
```

### Environment Configuration:
Set up environment variables for production:
- `REACT_APP_API_URL` - Backend API URL
- `PORT` - Backend server port
- `NODE_ENV` - Environment (production/development)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
