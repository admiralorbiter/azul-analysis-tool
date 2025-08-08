# Development Setup Guide

## Overview

This guide covers setting up the development environment for the Azul Solver & Analysis Toolkit. It includes installation of dependencies, configuration, and running the application locally.

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher (for frontend development)
- **Git**: For version control
- **Memory**: At least 4GB RAM (8GB recommended for neural training)
- **Storage**: At least 2GB free space

### Operating System Support

- **Windows**: 10 or higher
- **macOS**: 10.15 or higher
- **Linux**: Ubuntu 18.04+ or equivalent

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/azul-analysis-tool.git
cd azul-analysis-tool
```

### 2. Python Environment Setup

#### Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install Python Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Verify Installation

```bash
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import flask; print(f'Flask version: {flask.__version__}')"
```

### 3. Frontend Setup

#### Install Node.js Dependencies

```bash
cd ui
npm install
```

#### Verify Frontend Setup

```bash
npm run build
```

### 4. Database Setup

#### Initialize Database

```bash
# From project root
python -c "from core.azul_database import AzulDatabase; db = AzulDatabase(); db.init_database()"
```

#### Verify Database

```bash
python -c "from core.azul_database import AzulDatabase; db = AzulDatabase(); print('Database initialized successfully')"
```

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# API Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///azul_research.db

# Neural Configuration
NEURAL_MODELS_DIR=models/
NEURAL_TRAINING_DIR=training/

# API Configuration
API_RATE_LIMIT=100
API_RATE_LIMIT_WINDOW=3600

# Development Configuration
DEBUG=True
LOG_LEVEL=DEBUG
```

### 2. PyTorch Configuration

#### CPU-Only Setup

```bash
# Install CPU-only PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### GPU Setup (Optional)

```bash
# Install CUDA-enabled PyTorch (requires NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Verify PyTorch

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### 3. Development Tools

#### Install Development Tools

```bash
# Code formatting
pip install black flake8 isort

# Testing
pip install pytest pytest-cov

# Type checking
pip install mypy

# Documentation
pip install sphinx sphinx-rtd-theme
```

#### Configure Development Tools

Create `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
```

## Running the Application

### 1. Backend Server

#### Start Flask Development Server

```bash
# From project root
python start_server.py
```

Or directly with Flask:

```bash
export FLASK_APP=api/app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

#### Verify Backend

```bash
curl http://localhost:8000/api/v1/health
```

### 2. Frontend Development Server

#### Start React Development Server

```bash
cd ui
npm start
```

#### Verify Frontend

Open `http://localhost:3000` in your browser.

### 3. Full Stack Development

#### Combined Development Setup

```bash
# Terminal 1: Backend
python start_server.py

# Terminal 2: Frontend
cd ui && npm start
```

## Development Workflow

### 1. Code Organization

#### Backend Structure

```
api/
├── app.py              # Main Flask application
├── routes/             # API route handlers
├── models/             # Data models
├── middleware/         # Request/response middleware
└── utils/              # API utilities

core/
├── azul_model.py       # Game state representation
├── azul_evaluator.py   # Position evaluation
├── azul_patterns.py    # Pattern detection
└── azul_neural.py      # Neural model integration
```

#### Frontend Structure

```
ui/
├── components/         # React components
├── api/               # API client modules
├── utils/             # Utility functions
└── styles/            # CSS styling
```

### 2. Development Commands

#### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Type checking
mypy .

# Run tests
pytest tests/
```

#### Database Operations

```bash
# Initialize database
python -c "from core.azul_database import AzulDatabase; db = AzulDatabase(); db.init_database()"

# Reset database
python -c "from core.azul_database import AzulDatabase; db = AzulDatabase(); db.reset_database()"
```

#### Neural Operations

```bash
# Test neural system
python -c "from neural.azul_net import AzulNet; net = AzulNet('small'); print('Neural system ready')"

# Train test model
python neural/train.py --model-size small --epochs 10
```

### 3. Testing

#### Run All Tests

```bash
pytest tests/ -v
```

#### Run Specific Test Categories

```bash
# API tests
pytest tests/test_api.py -v

# Core functionality tests
pytest tests/test_core.py -v

# Neural tests
pytest tests/test_neural.py -v
```

#### Coverage Report

```bash
pytest tests/ --cov=core --cov=api --cov-report=html
```

## Debugging

### 1. Backend Debugging

#### Enable Debug Mode

```bash
export FLASK_DEBUG=1
export FLASK_ENV=development
flask run
```

#### Logging Configuration

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Debug Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health

# System info
curl http://localhost:8000/api/v1/stats
```

### 2. Frontend Debugging

#### React Developer Tools

Install React Developer Tools browser extension for debugging.

#### Console Logging

```javascript
// Enable debug logging
localStorage.setItem('debug', 'true');
```

#### Network Debugging

Use browser developer tools to inspect API requests and responses.

### 3. Database Debugging

#### SQLite Browser

```bash
# Install SQLite browser
# Windows: Download from https://sqlitebrowser.org/
# macOS: brew install db-browser-for-sqlite
# Linux: sudo apt-get install sqlitebrowser

# Open database
sqlitebrowser azul_research.db
```

#### Command Line Debugging

```bash
# Connect to database
sqlite3 azul_research.db

# List tables
.tables

# Query data
SELECT * FROM neural_training_sessions LIMIT 5;
```

## Performance Optimization

### 1. Development Performance

#### Backend Optimization

```python
# Enable caching
from flask_caching import Cache
cache = Cache()

# Enable compression
from flask_compress import Compress
Compress(app)
```

#### Frontend Optimization

```bash
# Build optimized version
npm run build

# Analyze bundle size
npm run analyze
```

### 2. Memory Management

#### Python Memory

```python
import gc
import psutil

# Monitor memory usage
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")

# Force garbage collection
gc.collect()
```

#### Node.js Memory

```bash
# Monitor Node.js memory
node --max-old-space-size=4096 node_modules/.bin/react-scripts start
```

## Troubleshooting

### Common Issues

#### Python Dependencies

**Problem**: Import errors for PyTorch or other packages
**Solution**:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### Node.js Dependencies

**Problem**: Frontend build failures
**Solution**:
```bash
cd ui
rm -rf node_modules package-lock.json
npm install
```

#### Database Issues

**Problem**: Database connection errors
**Solution**:
```bash
# Reset database
python -c "from core.azul_database import AzulDatabase; db = AzulDatabase(); db.reset_database()"
```

#### Port Conflicts

**Problem**: Port 5000 or 3000 already in use
**Solution**:
```bash
# Find process using port
lsof -i :5000
kill -9 <PID>

# Or use different ports
flask run --port=5001
npm start -- --port=3001
```

### Performance Issues

#### Slow Neural Training

**Solutions**:
- Use GPU if available
- Reduce model size for testing
- Increase batch size if memory allows
- Use smaller datasets for development

#### Slow API Responses

**Solutions**:
- Enable caching
- Optimize database queries
- Use async processing for long operations
- Monitor resource usage

#### Frontend Performance

**Solutions**:
- Use production build for testing
- Optimize bundle size
- Enable code splitting
- Use React.memo for expensive components

## Deployment Preparation

### 1. Production Build

#### Backend Preparation

```bash
# Install production dependencies
pip install gunicorn

# Test production server
gunicorn api.app:app --bind 0.0.0.0:5000
```

#### Frontend Preparation

```bash
cd ui
npm run build
```

### 2. Environment Configuration

#### Production Environment Variables

```bash
FLASK_ENV=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost/azul_db
SECRET_KEY=your-production-secret-key
```

### 3. Docker Setup (Optional)

#### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "api.app:app", "--bind", "0.0.0.0:5000"]
```

#### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
  frontend:
    build: ./ui
    ports:
      - "3000:3000"
```

## Related Documentation

- [System Architecture](../architecture.md) - System architecture overview
- [API Reference](../api/endpoints.md) - Complete API documentation
- [Neural Training Guide](../../guides/neural/training.md) - Neural system setup
- [Quick Start Guide](../../QUICK_START.md) - Quick setup guide 