# 🌌 Azul Solver & Analysis Toolkit

> **Goal:** Deliver a Python‑based engine, web UI, and research tools that (i) compute *exact* values for tactical depths, (ii) return sub‑200 ms live hints, and (iii) support long‑term strategy research.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-15%20passed-brightgreen.svg)](https://github.com/your-username/azul-solver)

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
```bash
# Test the engine
python main.py test

# Check project status
python main.py status

# See all available commands
python main.py --help
```

## 📊 Current Status

### ✅ Completed (M0 - Bootstrap)
- [x] Repository setup and cleanup
- [x] Import conflicts resolved
- [x] Project structure organized (`core/`, `api/`, `ui/`, `neural/`, `tools/`, `tests/`)
- [x] Python packaging setup (`pyproject.toml`, `requirements.txt`)
- [x] CLI interface and basic testing (15 tests passing)
- [x] Professional package structure with proper exports

### 🚧 In Progress (M1 - Rules Engine)
- [x] **A1 State Model**: Basic structure ✅
  - [x] Immutable dataclass structure (AzulState)
  - [x] NumPy arrays for grid state
  - [ ] 64-bit Zobrist key implementation
  - [ ] clone() and undo() methods
  
- [ ] **A2 Rule Validator**: Partial ⚠️
  - [x] Basic rule structure exists
  - [ ] 100 golden tests for rule compliance
  - [ ] Full validation of drafting → placement → scoring

- [ ] **A3 Move Generator**: Not started 📋
  - [ ] Enumerate legal compound moves
  - [ ] Return vector mask for policy networks
  - [ ] Performance optimization (≤15 µs/call target)

### 📋 Planned Milestones
- **M2** (2 weeks): Exact Search α - Alpha-Beta, CLI exact analysis
- **M3** (2 weeks): Fast Hint β - MCTS, 200ms budget
- **M4** (3 weeks): Web UI α - React board, live hints
- **M5** (2 weeks): Research Tools - Database, analysis tools
- **M6** (3 weeks): Neural Add-on - PyTorch models, GPU support
- **M7** (1 week): Endgame DB - Retrograde tables
- **M8** (2 weeks): Performance & Harden - Profiling, deployment
- **M9** (1 week): v1 Release - Documentation, demo

## 🏗️ Architecture

```
AZUL-RESEARCH/
├── core/                    # ✅ Game engine
│   ├── __init__.py         # Package exports
│   ├── template.py         # Base classes
│   ├── azul_model.py       # Game state & rules
│   ├── azul_utils.py       # Constants & utilities
│   └── azul_displayer.py   # Display interfaces
├── api/                    # 📋 REST API (planned)
├── ui/                     # 📋 Web interface (planned)
├── neural/                 # 📋 PyTorch models (planned)
├── tools/                  # ✅ CLI utilities
├── tests/                  # ✅ Test suite (15 passing tests)
├── legacy/                 # 📋 Original framework
├── resources/              # 🎨 Assets
├── main.py                 # ✅ CLI entry point
└── pyproject.toml          # ✅ Package configuration
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_core.py -v

# Run with coverage
python -m pytest tests/ --cov=core --cov-report=html
```

## 🎲 CLI Commands

```bash
# Basic engine verification
python main.py test

# Project status and milestones
python main.py status

# Exact analysis (planned for M2)
python main.py exact "<fen>" --depth 3

# Fast hints (planned for M3)
python main.py hint "<fen>" --budget 0.2

# Web server (planned for M4)
python main.py serve --host 127.0.0.1 --port 8000
```

## 📚 Documentation

- [Project Plan](project_plan.md) - Detailed roadmap and milestones
- [Checklist](checklist.md) - Build checklist with current status
- [Setup Summary](SETUP_SUMMARY.md) - Repository setup and cleanup details

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

**Current Status**: ✅ Bootstrap Complete → Ready for M1 Implementation
