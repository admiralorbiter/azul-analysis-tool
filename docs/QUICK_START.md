# 🚀 Quick Start Guide

> Get up and running with the Azul Solver & Analysis Toolkit in minutes.

## 📋 Prerequisites

- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **Git** - [Download here](https://git-scm.com/downloads)
- **8GB+ RAM** - For optimal performance
- **Modern browser** - For web UI (Chrome, Firefox, Safari, Edge)

## ⚡ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/azul-solver.git
cd azul-solver
```

### 2. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 3. Verify Installation
```bash
# Run basic tests
python main.py test

# Check project status
python main.py status
```

## 🎮 First Steps

### Start the REST API Server
```bash
# Start the server (default: http://127.0.0.1:8000)
python main.py serve

# With debug mode for development
python main.py serve --debug

# With custom configuration
python main.py serve --host 0.0.0.0 --port 8080 --database my_cache.db
```

### Test the API
```bash
# Health check (no authentication required)
curl http://localhost:8000/api/v1/health

# Create a session
curl -X POST http://localhost:8000/api/v1/auth/session \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

# Get session token from response and use it
export TOKEN="your_session_token_here"

# Test exact analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "fen_string": "start",
    "depth": 3,
    "timeout": 4.0,
    "agent": 0
  }'
```

## 🎯 Command Line Usage

### Exact Analysis
```bash
# Analyze a position with Alpha-Beta search
python main.py exact "start" --depth 3 --timeout 4.0

# Analyze for specific player
python main.py exact "start" --depth 3 --agent 1

# Use custom database for caching
python main.py exact "start" --depth 3 --database my_cache.db
```

### Fast Hints
```bash
# Get MCTS hints
python main.py hint "start" --budget 0.2 --rollouts 100

# Custom hint parameters
python main.py hint "start" --budget 0.5 --rollouts 500 --agent 0
```

### Performance Profiling
```bash
# Profile the engine
python main.py profile --state midgame --output results.json

# Custom profiling
python main.py profile --budget 4.0 --hint-budget 0.2 --move-budget 0.001
```

## 🌐 Web Interface

### Access the Web UI
1. Start the server: `python main.py serve`
2. Open your browser to: `http://localhost:8000/ui/`
3. Create a session and start analyzing!

### Web UI Features
- **Interactive Game Board** - Drag and drop tile placement
- **Real-time Analysis** - Live hints and exact analysis
- **Position Management** - Save and load game positions
- **Performance Dashboard** - Monitor system performance

## 📊 Database Features

### Position Caching
```bash
# Store a position
curl -X PUT http://localhost:8000/api/v1/positions/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "player_count": 2,
    "compressed_state": "...",
    "metadata": {"game_phase": "opening"}
  }'

# Search positions
curl -X GET "http://localhost:8000/api/v1/positions/search?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Analysis Caching
```bash
# Get cached analysis
curl -X GET http://localhost:8000/api/v1/analyses/start \
  -H "Authorization: Bearer $TOKEN"

# Search analyses
curl -X GET "http://localhost:8000/api/v1/analyses/search?search_type=alpha_beta" \
  -H "Authorization: Bearer $TOKEN"
```

## 🧪 Testing

### Run All Tests
```bash
# Run complete test suite
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=core --cov-report=html

# Run specific test category
python -m pytest tests/test_core.py -v
python -m pytest tests/test_api.py -v
python -m pytest tests/test_search.py -v
```

### Quick Functionality Test
```bash
# Basic engine test
python main.py test

# API functionality test
python -m pytest tests/test_api.py::test_health_endpoint -v
```

## 🔧 Development

### Project Structure
```
AZUL-RESEARCH/
├── core/           # Game engine (complete)
├── api/            # REST API (complete)
├── ui/             # Web interface (planned)
├── neural/         # Neural components (planned)
├── tests/          # Test suite
├── docs/           # Documentation
├── scripts/        # Debug & profiling
└── main.py         # CLI entry point
```

### Development Workflow
1. **Start Development Server**: `python main.py serve --debug`
2. **Run Tests**: `python -m pytest tests/ -v`
3. **Check Status**: `python main.py status`
4. **Profile Performance**: `python main.py profile`

### Common Commands
```bash
# Development server with debug
python main.py serve --debug

# Run specific test
python -m pytest tests/test_core.py::test_game_initialization -v

# Profile move generator
python scripts/profile_move_generator.py

# Debug API issues
python scripts/debug_api_error.py

# Benchmark performance
python scripts/benchmark_move_generator.py
```

## 📚 Next Steps

### For Users
1. **Explore the API**: Try different analysis depths and positions
2. **Use the Web UI**: Interactive analysis and position management
3. **Cache Results**: Build up a database of analyzed positions
4. **Monitor Performance**: Check system stats and health

### For Developers
1. **Study the Architecture**: Review `core/` and `api/` modules
2. **Add Tests**: Extend the test suite with new scenarios
3. **Optimize Performance**: Profile and improve search algorithms
4. **Contribute Features**: Implement new analysis methods

### For Researchers
1. **Database Integration**: Use bulk operations for large datasets
2. **Custom Analysis**: Extend the search algorithms
3. **Performance Monitoring**: Track analysis statistics
4. **Position Management**: Organize research positions

## 🆘 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure you're in the project directory
cd azul-solver

# Install dependencies
pip install -r requirements.txt

# Check Python path
python -c "import core.azul_model; print('✅ Imports work')"
```

**Server Won't Start:**
```bash
# Check if port is in use
netstat -an | grep 8000

# Try different port
python main.py serve --port 8080

# Check logs
python main.py serve --debug
```

**API Authentication:**
```bash
# Create session first
curl -X POST http://localhost:8000/api/v1/auth/session \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

# Use returned token in Authorization header
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/health
```

**Database Issues:**
```bash
# Check database file
ls -la azul_cache.db

# Recreate database
rm azul_cache.db
python main.py serve --database new_cache.db
```

## 📞 Getting Help

- **Documentation**: Check `docs/` directory for detailed guides
- **API Reference**: See `docs/API_USAGE.md` for complete API documentation
- **Progress Tracking**: Review `PROGRESS_TRACKER.md` for current status
- **Issues**: Report problems on GitHub Issues

---

**Ready to analyze some Azul positions? Start with `python main.py serve` and explore! 🎉** 