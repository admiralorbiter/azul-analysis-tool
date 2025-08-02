# 📚 Azul Solver Documentation

> Complete documentation for the Azul Solver & Analysis Toolkit

## 🚀 Getting Started

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in minutes
- **[API Usage Guide](API_USAGE.md)** - Complete REST API documentation
- **[Setup Summary](SETUP_SUMMARY.md)** - Repository setup and cleanup details

## 📊 Current Status

### ✅ **Completed Milestones**

#### **M1 - Rules Engine (COMPLETE)**
- **A1**: State model with Zobrist hashing, clone/undo, immutability
- **A2**: Comprehensive rule validation and move generation
- **A3**: Performance optimizations and move generation improvements

#### **M2 - Exact Search (COMPLETE)**
- **A4**: Heuristic evaluation with pattern potential scoring
- **A5**: Alpha-Beta search with iterative deepening, depth-3 < 4s

#### **M3 - Fast Hint Engine (COMPLETE)**
- **A6**: MCTS module with UCT algorithm, < 200ms hints

#### **M4 - Database Integration (COMPLETE)**
- **B1.1**: WAL mode and performance optimization
- **B1.2**: Zstd compression for state storage
- **B1.3**: Enhanced indexing and query optimization

#### **M5 - REST API (COMPLETE)**
- **B2.1**: Position cache API with bulk operations
- **B2.2**: Analysis cache API with search and statistics
- **B2.3**: Performance API with monitoring and optimization

#### **M6 - Web UI (COMPLETE)**
- **B3.1**: Interactive game board display with React + SVG
- **B3.2**: Real-time analysis interface with drag-and-drop
- **B3.3**: Performance dashboard with database stats

#### **M7 - Neural Integration (IN PROGRESS)**
- **C1.1**: PyTorch model integration with AzulNet
- **C1.2**: Tensor encoding and neural MCTS integration
- **C1.3**: Training pipeline with synthetic data generation

### 🚧 **In Progress**
- **M7**: Neural Integration - Policy-to-move mapping and GPU optimization
- **M8**: Advanced Search - Neural MCTS and hybrid search
- **M9**: Production Deployment - Docker and CI/CD

## 🏗️ Architecture

### Core Components
- **Game Engine** (`core/`) - Complete rules engine with search algorithms
- **REST API** (`api/`) - Complete Flask-based API with authentication
- **Database** (`core/azul_database.py`) - SQLite with compression and indexing
- **Web UI** (`ui/`) - React-based interactive interface
- **Neural Network** (`neural/`) - PyTorch-based AzulNet model
- **Search Algorithms** - Alpha-Beta and MCTS implementations

### Development Status
- ✅ **Engine Core** - Complete with 297+ tests
- ✅ **REST API** - Complete with authentication and caching
- ✅ **Database** - Complete with compression and optimization
- ✅ **Web UI** - Complete with interactive features
- 🚧 **Neural Integration** - In progress (M7)
- 📋 **Production Deployment** - Planned (M9)

## 🧪 Testing

### Test Coverage
- **297+ tests** across all components
- **Core functionality** - Game state, rules, validation
- **Search algorithms** - Alpha-Beta and MCTS
- **API endpoints** - Authentication, analysis, caching
- **Database operations** - CRUD, compression, indexing
- **Neural components** - Model creation, training, inference

### Running Tests
```bash
# All tests
python -m pytest tests/ -v

# Specific categories
python -m pytest tests/test_core.py -v
python -m pytest tests/test_api.py -v
python -m pytest tests/test_search.py -v
python -m pytest tests/test_neural.py -v

# With coverage
python -m pytest tests/ --cov=core --cov-report=html
```

## 🚀 Usage Examples

### Command Line
```bash
# Start API server
python main.py serve

# Exact analysis
python main.py exact "start" --depth 3

# Fast hints
python main.py hint "start" --budget 0.2

# Neural training
python main.py train --config small --epochs 5

# Performance profiling
python main.py profile
```

### REST API
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Create session
curl -X POST http://localhost:8000/api/v1/auth/session \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

# Exact analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fen_string": "start", "depth": 3, "time_budget": 4.0, "agent_id": 0}'
```

### Web UI
- **URL**: `http://127.0.0.1:8000`
- **Features**: Interactive game board, real-time analysis, drag-and-drop tiles
- **Status**: Fully operational with all features working

## 📊 Performance Metrics

### Search Performance
- **Alpha-Beta**: Depth-3 search < 4 seconds
- **MCTS**: < 200ms hint generation
- **Neural Inference**: < 1ms per evaluation
- **Cache Hit Rate**: > 80% for repeated positions

### Database Performance
- **WAL Mode**: Concurrent read/write access
- **Compression Ratio**: ~70% space savings with Zstd
- **Query Performance**: Sub-millisecond response times
- **Index Coverage**: 15+ optimized indexes

### API Performance
- **Response Time**: < 5ms for cached operations
- **Authentication**: Session-based with rate limiting
- **Bulk Operations**: Efficient batch processing
- **Error Handling**: Comprehensive error responses

### Web UI Performance
- **Initial Load**: ~28KB, loads instantly
- **API Calls**: Real-time with proper error handling
- **User Feedback**: Immediate status updates

## 🔧 Development

### Project Structure
```
AZUL-RESEARCH/
├── core/           # ✅ Game engine (complete)
├── api/            # ✅ REST API (complete)
├── ui/             # ✅ Web interface (complete)
├── neural/         # 🚧 Neural components (in progress)
├── tests/          # ✅ Test suite (297 tests)
├── docs/           # 📚 Documentation
├── scripts/        # 🔧 Debug & profiling
├── legacy/         # 📜 Original reference code
└── main.py         # ✅ CLI entry point
```

### Development Workflow
1. **Start Development Server**: `python main.py serve --debug`
2. **Run Tests**: `python -m pytest tests/ -v`
3. **Check Status**: `python main.py status`
4. **Profile Performance**: `python main.py profile`
5. **Train Neural Model**: `python main.py train --config small`

## 📈 Recent Achievements

### ✅ **Web UI Integration (M6)**
- **Interactive Board**: React + SVG game board with drag-and-drop
- **Real-time Analysis**: Fast hints and exact analysis integration
- **Database Integration**: SQLite caching operational without errors
- **API Compatibility**: All endpoints working correctly
- **Performance Targets**: All response times within targets

### ✅ **Neural Integration (M7)**
- **Tensor Encoding**: Comprehensive state representation
- **AzulNet Model**: PyTorch-based policy+value network
- **MCTS Integration**: Neural rollout policy
- **Training Pipeline**: Synthetic data generation and training
- **CLI Integration**: Training command with config options

### ✅ **Main.js Refactoring**
- **99% Reduction**: From 4,926 lines to ~50 lines
- **Modular Architecture**: 20 new modules created
- **Component Extraction**: 80+ functions extracted
- **Testing**: All functionality verified working

## 🎯 Next Steps

### **Immediate (M7 Completion)**
1. **Policy Mapping**: Complete neural policy-to-move mapping
2. **GPU Optimization**: Add batch inference capabilities
3. **Model Evaluation**: Compare neural vs heuristic performance

### **Short Term (M8)**
1. **Advanced Search**: Neural MCTS and hybrid search
2. **Opening Book**: Position database and book moves
3. **Performance Validation**: Benchmark against known positions

### **Medium Term (M9)**
1. **Production Deployment**: Docker containerization
2. **CI/CD Pipeline**: Automated testing and deployment
3. **v1.0 Release**: Complete documentation and deployment

## 📞 Support

- **Documentation**: This directory contains all guides
- **API Reference**: See `API_USAGE.md` for complete API docs
- **Progress Tracking**: Review `PROGRESS_TRACKER.md` for status
- **Issues**: Report problems on GitHub Issues

---

**Current Status**: ✅ M1-M6 Complete, 🚧 M7 Neural Integration in Progress → Ready for M8 Advanced Search 🎉 