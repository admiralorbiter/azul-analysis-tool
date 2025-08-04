# Installation Guide

> **Complete setup instructions for the Azul Solver & Analysis Toolkit**

## 📋 **System Requirements**

### **Minimum Requirements**
- **Python 3.11+** (3.12 recommended)
- **Git** for cloning the repository
- **4GB RAM** (8GB recommended for neural features)
- **1GB disk space** (2GB recommended for models and data)

### **Recommended Requirements**
- **Python 3.12** for best performance
- **8GB RAM** for neural model training
- **SSD storage** for faster database operations
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

## 🛠️ **Installation Steps**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/AZUL-RESEARCH.git
cd AZUL-RESEARCH
```

### **2. Create Virtual Environment (Recommended)**
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**
```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### **4. Verify Installation**
```bash
# Test core functionality
python -c "from core.azul_model import AzulState; print('Core modules working')"

# Test neural modules (if installed)
python -c "from neural.azul_net import AzulNet; print('Neural modules working')"
```

## 🔧 **Configuration**

### **Environment Variables (Optional)**
```bash
# Set for development
export AZUL_DEBUG=1
export AZUL_LOG_LEVEL=INFO

# Set for production
export AZUL_PRODUCTION=1
export AZUL_LOG_LEVEL=WARNING
```

### **Database Setup**
The system uses SQLite by default. No additional setup required.

### **Neural Model Setup (Optional)**
```bash
# Download pre-trained models (if available)
python -c "from neural.azul_net import download_models; download_models()"
```

## 🚀 **Quick Start**

### **Start the Server**
```bash
python start_server.py
```

The server will start on `http://localhost:5000`

### **Access the Web Interface**
1. Open your browser to `http://localhost:5000`
2. You should see the Azul game board
3. Start analyzing positions immediately

## 🧪 **Testing the Installation**

### **Run Basic Tests**
```bash
# Run core tests
python -m pytest tests/test_core.py -v

# Run API tests
python -m pytest tests/test_api.py -v

# Run all tests
python -m pytest tests/ -v
```

### **Test API Endpoints**
```bash
# Test basic API functionality
curl http://localhost:5000/api/v1/health

# Test pattern detection
curl -X POST http://localhost:5000/api/v1/detect-patterns \
  -H "Content-Type: application/json" \
  -d '{"fen_string": "test_position", "current_player": 0}'
```

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Python Version Issues**
```bash
# Check Python version
python --version

# Should be 3.11 or higher
# If not, install Python 3.11+ from python.org
```

#### **Dependency Issues**
```bash
# Upgrade pip
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### **Port Already in Use**
```bash
# Check what's using port 5000
netstat -an | findstr :5000  # Windows
lsof -i :5000                # macOS/Linux

# Kill the process or use a different port
python start_server.py --port 5001
```

#### **Memory Issues**
```bash
# Reduce memory usage
export AZUL_LOW_MEMORY=1

# Or disable neural features
export AZUL_DISABLE_NEURAL=1
```

### **Performance Issues**

#### **Slow Startup**
- **SSD storage** recommended for database operations
- **8GB RAM** recommended for neural features
- **Disable neural features** if memory is limited

#### **Slow Analysis**
- **Reduce analysis depth** in configuration
- **Use quick analysis mode** for real-time play
- **Disable advanced features** if performance is critical

## 📚 **Next Steps**

### **After Installation**
1. **Read the [Quick Start](../QUICK_START.md)** guide
2. **Try the [First Steps](first-steps.md)** tutorial
3. **Explore the [Analysis Guides](../analysis/)** for detailed features
4. **Check the [API Reference](../../technical/api/endpoints.md)** for programmatic access

### **For Developers**
1. **Set up development environment** - See [Development Setup](../../technical/development/setup.md)
2. **Run the test suite** - Ensure everything works correctly
3. **Explore the codebase** - Understand the architecture
4. **Contribute improvements** - Follow the contribution guidelines

---

**Installation complete! You're ready to start analyzing Azul positions.** 🎯

The toolkit provides everything you need for competitive Azul analysis and research. 