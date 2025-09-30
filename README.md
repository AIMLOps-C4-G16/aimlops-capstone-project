# AIMLOps Capstone Project

A comprehensive AI/ML system for intelligent image understanding and interaction through multiple interfaces. This project demonstrates modern MLOps practices with microservices architecture, containerization, and multi-modal AI capabilities.

## 🚀 Overview

This system provides intelligent image analysis capabilities through three primary interfaces:
- **Web Application**: Interactive React-based frontend for image upload and analysis
- **WhatsApp Bot**: Conversational interface for image queries via Twilio integration
- **REST API**: Direct programmatic access to all AI capabilities

### Key Features

- **Image Captioning**: AI-powered image description generation
- **Semantic Search**: Find images using natural language queries
- **Similarity Search**: Discover visually similar images
- **Image Indexing**: Build searchable databases from image collections

## 🏗 Architecture

The system follows a microservices architecture with five main components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Web     │    │   External      │    │  WhatsApp Bot   │
│   Frontend      │    │   Clients       │    │   (Twilio)      │
│   Port: 3000    │    │                 │    │   Port: 8003    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       │
┌─────────────────┐    ┌─────────────────┐              │
│  React Backend  │────► Image Query     │              │
│  (API Gateway)  │    │ Router          │              │
│  Port: 8002     │    │ Port: 8001      │              │
└─────────────────┘    └─────────────────┘              │
                                 │                       │
                                 ▼                       ▼
                ┌─────────────────────────────────────────┐
                │         IC Model API (Core ML)          │
                │              Port: 8000                 │
                │                                         │
                │ • Image Captioning (BLIP)               │
                │ • Semantic Search (CLIP)                │
                │ • Vector Database (ChromaDB)            │
                │ • GPU Acceleration                      │
                └─────────────────────────────────────────┘
```

### Component Details

1. **IC Model API** (`api/ic_model_api/`): Core ML backend with BLIP and CLIP models
2. **Image Query Router** (`image_query_router/`): LangChain-based intelligent query processing
3. **React Backend** (`frontend/custom-react/backend/`): API gateway for web frontend
4. **React Frontend** (`frontend/custom-react/`): Modern web interface
5. **WhatsApp Bot** (`frontend/whatsapp/`): Twilio-powered messaging interface

## 🛠 Technology Stack

### Backend & AI/ML
- **FastAPI**: High-performance Python web frameworks
- **Transformers**: Hugging Face models (BLIP, CLIP)
- **LangChain**: AI agent orchestration and tool integration
- **ChromaDB**: Vector database for semantic search
- **PyTorch**: Deep learning framework

### Frontend & Interfaces
- **React 19**: Modern web frontend with hooks
- **Twilio**: WhatsApp integration for messaging
- **Axios**: HTTP client for API communication

### Infrastructure & DevOps
- **Docker & Docker Compose**: Containerization and orchestration
- **NVIDIA Container Runtime**: GPU acceleration support
- **GitHub Actions**: CI/CD pipelines
- **AWS EC2**: Cloud deployment with auto-scaling
- **CORS**: Cross-origin resource sharing configuration

## 📋 Prerequisites

### Required
- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Git** for repository management
- **NVIDIA GPU** with CUDA support
- **NVIDIA Container Toolkit** for Docker GPU access

### For WhatsApp Integration
- **Twilio Account** with WhatsApp sandbox/production access
- **Public URL** (ngrok, AWS ELB, etc.) for webhook endpoints

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/your-username/aimlops-capstone-project.git
cd aimlops-capstone-project
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials:
# - HF_TOKEN: Hugging Face token for model access
# - TWILIO_*: WhatsApp bot credentials (optional)
# - PUBLIC_BASE_URL: Your public URL for webhooks (optional)
```

### 3. Launch the Full Stack

```bash
# Start all services with GPU support
docker-compose up --build

# Or without GPU (CPU only)
docker-compose up --build --no-deps ic-model-api
```

### 4. Access the Applications

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs (Core ML API)
- **Image Router API**: http://localhost:8001/docs
- **WhatsApp Bot**: Configure webhook to http://your-public-url:8003/webhook

## 📖 API Usage

### Core ML API (Port 8000)

#### Image Captioning
```bash
curl -X POST "http://localhost:8000/caption" \
  -F "file=@your-image.jpg"
```

#### Semantic Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "sunset over mountains", "top_k": 5}'
```

#### Index Images
```bash
curl -X POST "http://localhost:8000/index" \
  -F "file=@image1.jpg" \
  -F "file=@image2.jpg"
```

### Image Query Router (Port 8001)

#### Intelligent Processing
```bash
curl -X POST "http://localhost:8001/process/" \
  -F "query=Find images similar to this sunset" \
  -F "files=@sunset.jpg"
```

## 🎯 Use Cases & Examples

### 1. Content Management
- **Digital Asset Libraries**: Index and search large image collections
- **E-commerce**: Product discovery through visual similarity
- **Media Archives**: Automated tagging and content retrieval

### 2. Customer Engagement
- **WhatsApp Commerce**: Visual product search via messaging
- **Customer Support**: Image-based problem identification
- **Interactive Catalogs**: Natural language product discovery

### 3. Research & Development
- **Dataset Analysis**: Automated image categorization and analysis
- **Content Moderation**: AI-powered content filtering
- **Visual Quality Assurance**: Automated defect detection

## 🔧 Development

### Local Development Setup

```bash
# Install individual service dependencies
cd api && pip install -r requirements.ic-model.txt
cd ../image_query_router && pip install -r requirements.txt
cd ../frontend/custom-react && npm install
cd backend && npm install
```

### Running Services Individually

```bash
# Core ML API
cd api && uvicorn ic_model_api.main:app --reload --port 8000

# Image Query Router
cd image_query_router && uvicorn main:app --reload --port 8001

# React Backend
cd frontend/custom-react/backend && npm start

# React Frontend
cd frontend/custom-react && npm start
```

### Testing

```bash
# API Testing
pytest api/tests/
python -m pytest image_query_router/tests/

# Frontend Testing
cd frontend/custom-react && npm test
```

## 🌐 Deployment

### AWS EC2 Deployment

The project includes automated AWS deployment via GitHub Actions:

1. **Configure AWS Secrets** in your GitHub repository:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `SERVICES_ENV` (base64 encoded .env file)

2. **Deploy**: Push to main branch or trigger manual deployment

3. **GPU Instance**: Automatically provisions GPU-enabled EC2 instances for ML workloads

### Custom Deployment

```bash
# Production build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build

# With custom environment
ENV=production docker-compose up --build
```

## 🔒 Security & Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `HF_TOKEN` | Hugging Face API token for model access | Yes |
| `TWILIO_ACCOUNT_SID` | Twilio account identifier | For WhatsApp |
| `TWILIO_AUTH_TOKEN` | Twilio authentication token | For WhatsApp |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp number | For WhatsApp |
| `PUBLIC_BASE_URL` | Public URL for webhook endpoints | For WhatsApp |

### Security Best Practices

- **API Rate Limiting**: Implemented across all endpoints
- **Input Validation**: Comprehensive request validation
- **CORS Configuration**: Restricted cross-origin access
- **Health Checks**: Automated service monitoring
- **Resource Limits**: Memory and CPU constraints in Docker

## 📊 Monitoring & Observability

### Health Checks

All services include comprehensive health check endpoints:

```bash
# Check service status
curl http://localhost:8000/docs  # Core ML API
curl http://localhost:8001/docs  # Image Router
curl http://localhost:8002/models  # React Backend
curl http://localhost:8003/health  # WhatsApp Bot
```

### Logging

- **Structured Logging**: JSON-formatted logs across all services
- **Error Tracking**: Comprehensive error handling and reporting
- **Performance Metrics**: Request timing and resource usage

## 🤝 Contributing

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Commit Changes**: `git commit -m 'Add amazing feature'`
4. **Push to Branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines

- **Code Quality**: Follow PEP 8 for Python, ESLint for JavaScript
- **Testing**: Maintain >80% test coverage
- **Documentation**: Update README for new features
- **Performance**: Profile CPU/memory usage for ML operations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hugging Face**: Pre-trained BLIP and CLIP models
- **LangChain**: AI agent framework and tools
- **Twilio**: WhatsApp integration platform
- **FastAPI**: High-performance web framework
- **React**: Modern frontend development

## 📞 Support

- **Documentation**: [Full documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/aimlops-capstone-project/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/aimlops-capstone-project/discussions)

---

**Built with ❤️ for the AI/ML community**