# AIMLOps Capstone Project - Docker Setup

This document provides instructions for running the complete AIMLOps image processing system using Docker.

## Architecture Overview

The system consists of 5 containerized services:

1. **IC Model API** (Port 8000) - Core ML backend with HuggingFace models
2. **Image Query Router** (Port 8001) - Main image processing service
3. **React Backend** (Port 8002) - API gateway for web frontend
4. **React Frontend** (Port 3000) - Web user interface
5. **WhatsApp Bot** (Port 8003) - Messaging interface

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- **NVIDIA Docker runtime (REQUIRED for GPU support)**
- **NVIDIA GPU with CUDA support (REQUIRED)**
- 8GB+ RAM available
- 10GB+ disk space for models

⚠️ **Important**: The IC Model API service **requires** a GPU to function correctly. It will not work properly without GPU acceleration.

## Quick Start

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd aimlops-capstone-project

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Start All Services

```bash
# Start the complete stack
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 3. Access Services

- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (IC Model)
- **Image Router Docs**: http://localhost:8001/docs
- **WhatsApp Bot**: Configure webhook to http://localhost:8003

## Environment Configuration

### Required Variables

```bash
# HuggingFace token for model access
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Twilio configuration (for WhatsApp bot)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Public URL for webhooks (use ngrok/localtunnel for development)
PUBLIC_BASE_URL=https://your-ngrok-url.ngrok.io
```

### Optional Variables

```bash
# Custom ports (defaults shown)
IC_MODEL_API_PORT=8000
IMAGE_QUERY_ROUTER_PORT=8001
REACT_BACKEND_PORT=8002
REACT_FRONTEND_PORT=3000
WHATSAPP_BOT_PORT=8003
```

## Individual Service Management

### Start Specific Services

```bash
# Start only core ML services
docker-compose up -d ic-model-api image-query-router

# Start web interface only
docker-compose up -d react-backend react-frontend

# Start WhatsApp bot only
docker-compose up -d whatsapp-bot
```

### Service Dependencies

- **Image Query Router** depends on **IC Model API**
- **React Backend** depends on **Image Query Router**
- **React Frontend** depends on **React Backend**
- **WhatsApp Bot** depends on **IC Model API** (directly)

## GPU Support (REQUIRED)

The IC Model API service **requires** GPU access for proper operation:

### Install NVIDIA Docker Runtime

```bash
# For Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
   && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Verify GPU Access

```bash
# Test GPU access
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Should show your GPU information
```

## Development Workflow

### Live Development

```bash
# Use override for development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Rebuild specific service
docker-compose build react-frontend
docker-compose up -d react-frontend
```

### Debugging

```bash
# View service logs
docker-compose logs -f ic-model-api

# Execute into container
docker-compose exec react-backend sh

# Check service health
docker-compose ps
```

## Production Deployment

### Build for Production

```bash
# Build all images
docker-compose build

# Tag for registry
docker tag aimlops-capstone-project_ic-model-api your-registry/ic-model-api:latest

# Push to registry
docker push your-registry/ic-model-api:latest
```

### Resource Requirements

- **IC Model API**: 4GB RAM, **1 GPU (REQUIRED)**
- **Image Query Router**: 2GB RAM
- **React Backend**: 512MB RAM
- **React Frontend**: 256MB RAM
- **WhatsApp Bot**: 512MB RAM

## Troubleshooting

### Common Issues

1. **GPU not detected / IC Model API fails to start**
   ```bash
   # Check if NVIDIA drivers are installed
   nvidia-smi

   # Install NVIDIA Docker runtime (see GPU Support section above)

   # Verify Docker can access GPU
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```

2. **Port conflicts**
   ```bash
   # Check what's using ports
   sudo netstat -tulpn | grep :8000

   # Modify ports in docker-compose.yml or .env
   ```

3. **Out of memory**
   ```bash
   # Check container memory usage
   docker stats

   # Increase Docker daemon memory limit
   ```

4. **Service startup failures**
   ```bash
   # Check individual service logs
   docker-compose logs ic-model-api

   # Restart problematic service
   docker-compose restart ic-model-api
   ```

5. **HuggingFace token issues**
   ```bash
   # Verify HF_TOKEN is set correctly
   echo $HF_TOKEN

   # Check token permissions on HuggingFace Hub
   ```

### Health Checks

All services include health checks accessible via:

```bash
# Check all service health
docker-compose ps

# Manual health check
curl http://localhost:8000/docs  # IC Model API
curl http://localhost:8001/docs  # Image Query Router
curl http://localhost:8002/models  # React Backend
curl http://localhost:3000  # React Frontend
```

## API Testing

### Sample Requests

```bash
# Upload and caption image via Image Query Router
curl -X POST "http://localhost:8001/process/" \
     -H "Content-Type: multipart/form-data" \
     -F "query=caption" \
     -F "files=@image.jpg"

# Search similar images
curl -X POST "http://localhost:8001/process/" \
     -H "Content-Type: multipart/form-data" \
     -F "query=similar" \
     -F "files=@image.jpg"

# Index new image
curl -X POST "http://localhost:8001/process/" \
     -H "Content-Type: multipart/form-data" \
     -F "query=index" \
     -F "files=@image.jpg"

# Direct IC Model API calls
curl -X POST "http://localhost:8000/caption" \
     -H "Content-Type: multipart/form-data" \
     -F "image=@image.jpg"

curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: multipart/form-data" \
     -F "text=mountain landscape" \
     -F "num=5"
```

## WhatsApp Bot Setup

### Configure Webhook

1. Set up ngrok or localtunnel for public URL:
   ```bash
   # Using ngrok
   ngrok http 8003

   # Using localtunnel
   npx localtunnel --port 8003
   ```

2. Set webhook URL in Twilio console to: `https://your-ngrok-url.ngrok.io/whatsapp`

3. Update `PUBLIC_BASE_URL` in `.env` file

### WhatsApp Bot Commands

- Send **1** for image captioning
- Send **2** for text-based image search
- Send **3** for similar image search
- Send **4** for image indexing

## Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes model cache)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Complete cleanup
docker system prune -a
```

## Performance Notes

- **GPU Memory**: IC Model API requires **minimum 16GB VRAM**
- **Model Loading**: First startup takes 5-10 minutes to download models
- **Caching**: Models are cached in Docker volume for faster subsequent starts
- **Concurrent Requests**: Each service can handle multiple concurrent requests
- **Scaling**: Services can be scaled horizontally except IC Model API (GPU bound)

## Security Considerations

- All services run with non-root users where possible
- Secrets should be stored in `.env` file (not committed)
- Network isolation through custom Docker bridge
- Health checks prevent unhealthy containers from receiving traffic
- Use HTTPS in production deployments