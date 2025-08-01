# 📚 Azul Solver Documentation

> Complete documentation for the Azul Solver & Analysis Toolkit

## 🚀 Getting Started

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in minutes
- **[API Usage Guide](API_USAGE.md)** - Complete REST API documentation
- **[Setup Summary](SETUP_SUMMARY.md)** - Repository setup and cleanup details

## 📊 Progress & Planning

### Progress Tracking
- **[Progress Tracker](../PROGRESS_TRACKER.md)** - Current status and achievements
- **[Documentation Status](DOCUMENTATION_STATUS.md)** - Documentation completeness

### Planning Documents
- **[Project Plan](planning/project_plan.md)** - Detailed roadmap and milestones
- **[Checklist](planning/checklist.md)** - Build checklist with current status
- **[Epic Planning Summary](planning/EPIC_PLANNING_SUMMARY.md)** - Epic-level planning

## 📈 Milestone Progress

### ✅ Completed Milestones

#### **M1 - Rules Engine (COMPLETE)**
- **[A1 Progress Summary](progress/A1_PROGRESS_SUMMARY.md)** - State model implementation
- **[A2 Progress Summary](progress/A2_PROGRESS_SUMMARY.md)** - Rule validator implementation
- **[A3 Progress Summary](progress/A3_PROGRESS_SUMMARY.md)** - Move generator implementation
- **[A3 Optimization Summary](progress/A3_OPTIMIZATION_SUMMARY.md)** - Performance optimizations

#### **M2 - Exact Search (COMPLETE)**
- **[A5 Progress Summary](progress/A5_PROGRESS_SUMMARY.md)** - Alpha-Beta search implementation

#### **M3 - Fast Hint Engine (COMPLETE)**
- **[A8 Progress Summary](progress/A8_PROGRESS_SUMMARY.md)** - MCTS implementation
- **[A9 Progress Summary](progress/A9_PROGRESS_SUMMARY.md)** - Hint engine completion

#### **M4 - Database Integration (COMPLETE)**
- **[M4 Progress Summary](progress/M4_PROGRESS_SUMMARY.md)** - Database schema and features
- **[M5 Progress Summary](progress/M5_PROGRESS_SUMMARY.md)** - REST API implementation

#### **M5 - REST API (COMPLETE)**
- **[CLI Integration Summary](progress/CLI_INTEGRATION_SUMMARY.md)** - Command line interface
- **[Web UI Integration Summary](progress/WEB_UI_INTEGRATION_SUMMARY.md)** - Web interface planning

### 🚧 In Progress
- **[M6 Progress Summary](progress/M6_PROGRESS_SUMMARY.md)** - Web UI development
- **[M7 Neural Integration Summary](progress/M7_NEURAL_INTEGRATION_SUMMARY.md)** - Neural components

## 🔬 Research

- **[Research Findings](../Azul Solver and Analysis Toolkit – Research Findings.pdf)** - Academic research paper
- **[Game Documentation](research/azul.md)** - Azul game rules and mechanics

## 🏗️ Architecture

### Core Components
- **Game Engine** (`core/`) - Complete rules engine with search algorithms
- **REST API** (`api/`) - Complete Flask-based API with authentication
- **Database** (`core/azul_database.py`) - SQLite with compression and indexing
- **Search Algorithms** - Alpha-Beta and MCTS implementations

### Development Status
- ✅ **Engine Core** - Complete with 297+ tests
- ✅ **REST API** - Complete with authentication and caching
- ✅ **Database** - Complete with compression and optimization
- 📋 **Web UI** - Planned for M6
- 📋 **Neural Integration** - Planned for M7

## 🧪 Testing

### Test Coverage
- **297+ tests** across all components
- **Core functionality** - Game state, rules, validation
- **Search algorithms** - Alpha-Beta and MCTS
- **API endpoints** - Authentication, analysis, caching
- **Database operations** - CRUD, compression, indexing

### Running Tests
```bash
# All tests
python -m pytest tests/ -v

# Specific categories
python -m pytest tests/test_core.py -v
python -m pytest tests/test_api.py -v
python -m pytest tests/test_search.py -v

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
  -d '{"fen_string": "start", "depth": 3, "timeout": 4.0, "agent": 0}'
```

## 📊 Performance Metrics

### Search Performance
- **Alpha-Beta**: Depth-3 search < 4 seconds
- **MCTS**: < 200ms hint generation
- **Move Generation**: < 15µs per call
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

## 🔧 Development

### Project Structure
```
AZUL-RESEARCH/
├── core/           # ✅ Game engine (complete)
├── api/            # ✅ REST API (complete)
├── ui/             # 📋 Web interface (planned)
├── neural/         # 📋 Neural components (planned)
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

## 📞 Support

- **Documentation**: This directory contains all guides
- **API Reference**: See `API_USAGE.md` for complete API docs
- **Progress Tracking**: Review `PROGRESS_TRACKER.md` for status
- **Issues**: Report problems on GitHub Issues

---

**Current Status**: ✅ M1-M5 Complete → Ready for M6 Web UI Development 🎉 

## 🆕 Board Editing Progress (F1.1)

- **Edit Mode Toggle**: Implemented in the Web UI (Game Management panel)
- **State Management**: `editMode` and `selectedElement` React state added
- **Visual Feedback**: CSS for edit mode, hover, and selection
- **Keyboard Support**: Escape key exits edit mode
- **CLI/Backend Tests**: Automated tests for state logic, validation, and API endpoint mocks (see `tests/test_board_editing_cli.py`)
- **UI Tests**: Manual only (no Selenium/UI automation)

### Next Steps
- **Element Selection**: Add click handlers and context menus for board elements
- **Context Menus**: Right-click editing options for factories, pattern lines, wall, floor
- **Documentation**: Keep this section updated as new board editing features are added

**Status:** F1.1 (Edit Mode Toggle) complete and tested. Ready for F1.1 Piece 2 (Element Selection System). 