# 🌌 Azul Solver & Analysis Toolkit

> **Goal:** Deliver a Python‑based engine, web UI, and research tools that (i) compute *exact* values for tactical depths, (ii) return sub‑200 ms live hints, and (iii) support long‑term strategy research.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-297%20passed-brightgreen.svg)](https://github.com/your-username/azul-solver)

## 🎯 Project Vision

| Pillar | Must‑Have Outcome |
| ------ | ---------------- |
| **Correctness** | Full rules compliance; deterministic engines yield identical outputs given identical seeds. |
| **Speed** | ≤ 200 ms hint latency on laptop (8‑core CPU) for 95th %ile mid‑game positions. |
| **Extensibility** | Plug‑in search modules (Alpha‑Beta, MCTS, Neural) & UI widgets without core rewrites. |
| **Reproducibility** | Docker image + CI matrix for Linux/macOS/Win. |
| **Licensing** | GPL v3 for engine/UI; third‑party assets clearly attributed. |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/azul-solver.git
cd azul-solver

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

### Basic Usage

#### 🎮 Start the REST API Server
```bash
# Start the Flask API server (default: http://127.0.0.1:8000)
python main.py serve

# With custom host/port
python main.py serve --host 0.0.0.0 --port 8080

# With debug mode
python main.py serve --debug

# With custom database
python main.py serve --database my_azul_cache.db
```

#### 🔍 Command Line Analysis
```bash
# Exact analysis of a position
python main.py exact "start" --depth 3 --timeout 4.0

# Fast hints (MCTS)
python main.py hint "start" --budget 0.2 --rollouts 100

# Check project status
python main.py status

# Run tests
python main.py test
```

## 📊 Current Status

### ✅ Completed Milestones

#### **M1 - Rules Engine (COMPLETE)** ✅
- **A1 State Model**: Immutable dataclass structure, Zobrist hashing, clone/undo methods
- **A2 Rule Validator**: Comprehensive rule validation with 28 tests
- **A3 Move Generator**: Fast move generation with performance optimization

#### **M2 - Exact Search (COMPLETE)** ✅
- **A4 Heuristic Evaluation**: Comprehensive scoring with pattern potential
- **A5 Alpha-Beta Search**: Iterative deepening with transposition table, depth-3 < 4s

#### **M3 - Fast Hint Engine (COMPLETE)** ✅
- **A6 MCTS Module**: UCT algorithm with rollout policies, < 200ms hints

#### **M4 - Database Integration (COMPLETE)** ✅
- **B1.1 WAL Mode & Performance**: WAL mode, memory optimization, performance pragmas
- **B1.2 Zstd Compression**: State compression with configurable levels
- **B1.3 Enhanced Indexing**: Composite indexes, query monitoring, optimization

#### **M5 - REST API (COMPLETE)** ✅
- **B2.1 Position Cache API**: get/put/delete methods, bulk operations, search
- **B2.2 Analysis Cache API**: MCTS/Alpha-Beta result caching, search, stats
- **B2.3 Performance API**: Statistics and monitoring endpoints

### 🚧 In Progress
- **M6 - Web UI (PLANNED)**: Interactive board, analysis interface, performance dashboard

## 🏗️ Architecture

```
AZUL-RESEARCH/
├── core/                    # ✅ Game engine (complete)
│   ├── azul_model.py       # Game state & rules
│   ├── azul_validator.py   # Rule validation
│   ├── azul_move_generator.py # Move generation
│   ├── azul_search.py      # Alpha-Beta search
│   ├── azul_mcts.py        # MCTS hint engine
│   ├── azul_database.py    # Database integration
│   └── azul_displayer.py   # Display interfaces
├── api/                    # ✅ REST API (complete)
│   ├── app.py             # Flask application
│   ├── routes.py          # API endpoints
│   ├── auth.py            # Authentication
│   └── rate_limiter.py    # Rate limiting
├── ui/                     # 📋 Web interface (planned)
├── neural/                 # 📋 PyTorch models (planned)
├── tools/                  # ✅ CLI utilities
├── tests/                  # ✅ Test suite (297 tests)
├── docs/                   # 📚 Documentation
│   ├── progress/          # Progress summaries
│   ├── planning/          # Project plans
│   └── research/          # Research findings
├── scripts/                # 🔧 Debug & profiling scripts
├── legacy/                 # 📜 Original reference code
└── main.py                 # ✅ CLI entry point
```

## 🌐 REST API Usage

### Starting the Server
```bash
# Basic server
python main.py serve

# With options
python main.py serve --host 0.0.0.0 --port 8080 --debug --database azul_cache.db
```

### API Endpoints

#### Authentication
```bash
# Create session
curl -X POST http://localhost:8000/api/v1/auth/session \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'
```

#### Analysis
```bash
# Exact analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -d '{
    "fen_string": "start",
    "depth": 3,
    "timeout": 4.0,
    "agent": 0
  }'

# Fast hints
curl -X POST http://localhost:8000/api/v1/hint \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -d '{
    "fen_string": "start",
    "budget": 0.2,
    "rollouts": 100,
    "agent": 0
  }'
```

#### Position Cache
```bash
# Store position
curl -X PUT http://localhost:8000/api/v1/positions/start \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"player_count": 2, "compressed_state": "..."}'

# Get position
curl -X GET http://localhost:8000/api/v1/positions/start \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"

# Search positions
curl -X GET "http://localhost:8000/api/v1/positions/search?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

#### Health & Stats
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Performance stats
curl http://localhost:8000/api/v1/stats \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_core.py -v

# Run with coverage
python -m pytest tests/ --cov=core --cov-report=html

# Quick functionality test
python main.py test
```

## 🎲 CLI Commands

```bash
# Start REST API server
python main.py serve [--host HOST] [--port PORT] [--debug] [--database DB]

# Exact analysis
python main.py exact "fen_string" [--depth DEPTH] [--timeout SECONDS] [--agent ID]

# Fast hints
python main.py hint "fen_string" [--budget SECONDS] [--rollouts COUNT] [--agent ID]

# Neural training
python main.py train [--config CONFIG] [--device DEVICE] [--epochs COUNT] [--samples COUNT]

# Model evaluation
python main.py evaluate [--model PATH] [--positions COUNT] [--games COUNT] [--device DEVICE]

# Performance profiling
python main.py profile [--state STATE] [--output FILE] [--budget SECONDS]

# Project status
python main.py status

# Basic tests
python main.py test
```

## 📚 Documentation

- [Project Plan](docs/planning/project_plan.md) - Detailed roadmap and milestones
- [Progress Tracker](PROGRESS_TRACKER.md) - Current status and achievements
- [API Documentation](docs/progress/M5_PROGRESS_SUMMARY.md) - REST API details
- [Database Integration](docs/progress/M4_PROGRESS_SUMMARY.md) - Database features
- [Search Algorithms](docs/progress/A5_PROGRESS_SUMMARY.md) - Alpha-Beta and MCTS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original Azul framework by Michelle Blom (GPL v3)
- Azul board game by Plan B Games
- Research community for feedback and testing

## 📞 Contact

- **Repository**: [https://github.com/your-username/azul-solver](https://github.com/your-username/azul-solver)
- **Issues**: [https://github.com/your-username/azul-solver/issues](https://github.com/your-username/azul-solver/issues)

---

**Current Status**: ✅ M1-M5 Complete → Ready for M6 Web UI Development 🎉
