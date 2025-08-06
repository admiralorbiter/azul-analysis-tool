# 🧠 Neural System

> **Neural network integration for Azul position evaluation and move analysis**

## 📋 **System Overview**

The Neural System provides machine learning capabilities for analyzing Azul game positions and making strategic decisions. It includes PyTorch-based models, training pipelines, and integration with the MCTS search algorithm.

### **Key Features**
- **AzulNet Model**: PyTorch-based neural network with 892-feature tensor encoding
- **Training Pipeline**: Synthetic data generation and training system
- **MCTS Integration**: Neural rollout policy for improved search performance
- **Model Evaluation**: Comprehensive neural vs heuristic comparison framework
- **CLI Tools**: Training command with configurable options

## 🚀 **Quick Start**

### **Accessing Neural Features**
1. **Navigate to Neural Training**: Click "🧠 Neural Training" in the main navigation
2. **Training Interface**: Use the dedicated neural training page with multiple tabs
3. **Model Configuration**: Set model size, training parameters, and data sources
4. **Start Training**: Begin neural model training with real-time monitoring

### **Basic Usage**
```python
# Test neural modules
python -c "from neural.azul_net import AzulNet; print('Neural modules working')"

# Download pre-trained models
python -c "from neural.azul_net import download_models; download_models()"
```

## 📚 **Documentation**

### **User Guides**
- **[Training Guide](training.md)** - How to train neural models
- **[Evaluation Guide](evaluation.md)** - How to evaluate trained models
- **[Integration Guide](integration.md)** - Using neural models in analysis

### **Technical Documentation**
- **[API Reference](../../technical/api/neural-endpoints.md)** - Complete API documentation
- **[Technical Implementation](../../technical/implementation/neural-evaluation.md)** - Technical details
- **[Architecture](../../technical/implementation/neural-training.md)** - System architecture

### **Planning & Progress**
- **[Planning Documents](planning/)** - Development plans and progress tracking

## 🔗 **Related Systems**

### **Core Integration**
- **[FEN System](../fen/)** - Game state representation for neural input
- **[Position Library](../position-library/)** - Training data and position management
- **[Move Quality](../move-quality/)** - Neural-assisted move evaluation

### **Analysis Tools**
- **[Competitive Analysis](../competitive/)** - Neural-enhanced competitive analysis
- **[Game Theory](../../guides/competitive/advanced-analysis.md)** - Neural opponent modeling

## 📊 **System Status**

### **✅ Completed Features**
- **Model Architecture**: Complete PyTorch-based AzulNet implementation
- **Training Pipeline**: Synthetic data generation and training system
- **MCTS Integration**: Neural rollout policy for improved search
- **Policy-to-Move Mapping**: Complete implementation with multiple selection algorithms
- **GPU Optimization**: RTX 30xx specific optimizations and batch processing
- **Model Evaluation**: Comprehensive neural vs heuristic comparison framework
- **CLI Tools**: Training command with configurable options

### **🚧 In Progress**
- **Educational Integration**: Learning tools and pattern recognition display
- **Real-time Analysis**: Live quality updates and interactive game board

### **📋 Planned**
- **Advanced Model Architectures**: Larger models for improved accuracy
- **Real Game Data Training**: Training on actual competitive game data
- **Ensemble Methods**: Multiple model combination for better predictions

## 🎯 **Success Metrics**

### **Performance Targets**
- **Accuracy**: Neural evaluation should match or exceed heuristic accuracy
- **Speed**: 30% faster search with neural integration
- **Convergence**: Faster convergence in MCTS with neural rollouts

### **Quality Metrics**
- **Model Size**: ≤100k parameters for efficient inference
- **Feature Encoding**: 892-feature tensor representation
- **Training Data**: Synthetic data generation for consistent training

## 🔧 **Configuration**

### **System Requirements**
- **Memory**: 8GB RAM recommended for neural features
- **GPU**: Optional but recommended for training (RTX 30xx optimized)
- **Storage**: 2GB for model storage and training data

### **Environment Variables**
```bash
# Disable neural features if memory is limited
export AZUL_DISABLE_NEURAL=1

# Set GPU memory limit
export CUDA_VISIBLE_DEVICES=0
```

## 📈 **Usage Statistics**

- **API Endpoints**: 5+ neural-specific endpoints
- **Model Variants**: Small, Medium, Large architectures
- **Training Data**: Synthetic position generation
- **Integration Points**: MCTS, Move Quality, Game Theory

---

**Status**: **Production Ready** 🚀

The Neural System is fully functional and integrated with all major analysis tools. It provides significant performance improvements for position evaluation and move analysis.
