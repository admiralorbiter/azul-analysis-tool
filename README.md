# 🌌 Azul Solver & Analysis Toolkit

> **Goal:** Deliver a Python‑based engine, web UI, and research tools that (i) compute *exact* values for tactical depths, (ii) return sub‑200 ms live hints, and (iii) support long‑term strategy research.

## 🎯 Project Overview

This repository contains a comprehensive Azul game engine and analysis toolkit built on top of the original Azul framework. The project provides:

- **Fast Game Engine**: Deterministic, rules-compliant Azul implementation with sub-200ms hint generation
- **Exact Search**: Alpha-beta and MCTS algorithms for tactical analysis
- **Web UI**: Interactive board visualization with heatmaps and move analysis
- **Research Tools**: Opening explorer, replay annotator, and quiz generator
- **Neural Integration**: Optional PyTorch-based neural evaluation (GPU support)

## 🚀 Key Features

| Feature | Status | Target |
|---------|--------|--------|
| **Engine Core** | 🚧 In Progress | Rules compliance, immutable state model |
| **Exact Search** | 📋 Planned | Depth-3 analysis in ≤4s |
| **Fast Hints** | 📋 Planned | ≤200ms response time |
| **Web UI** | 📋 Planned | React + SVG board renderer |
| **Neural Module** | 📋 Planned | GPU-accelerated evaluation |

## 🛠️ Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run exact analysis
python run.py exact "<fen_string>" --depth 3

# Start web server
python run.py serve --host 0.0.0.0 --port 8000
```

## 📋 Development Roadmap

See [project_plan.md](project_plan.md) for detailed development roadmap and [checklist.md](checklist.md) for build tasks.

### Current Milestone: M1 - Rules Engine
- [ ] State model with immutable dataclass + NumPy arrays
- [ ] Rule validator with 100 golden tests
- [ ] Move generator for compound moves
- [ ] Basic CLI interface

## 🏗️ Architecture

```
azul-solver/
├── core/           # Game engine (state, rules, search)
├── api/            # REST API (Flask)
├── ui/             # Web interface (React)
├── neural/         # PyTorch models
├── tools/          # Research utilities
└── tests/          # Comprehensive test suite
```

## 📊 Performance Targets

- **Hint Latency**: ≤200ms on 8-core laptop (95th percentile)
- **Exact Search**: Depth-3 analysis in ≤4s
- **Memory Usage**: <2GB for depth-3 search
- **Database**: ≤30MB for 1M compressed states

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project is built on top of the original Azul framework that provided the base game implementation. The original framework was designed to support policy learning for the Azul board game, published by Plan B Games.

### Original Framework Purpose
The original framework allowed students to implement algorithms for learning AI players for Azul and evaluate the performance of these players against human/other AI players. Students could create Player subclasses for their AI players that select moves based on learned policies.

### Game Information
- [Azul on Wikipedia](https://en.wikipedia.org/wiki/Azul_(board_game))
- [Azul on BoardGameGeek](https://boardgamegeek.com/boardgame/230802/azul)
- [Plan B Games - Azul](https://www.planbgames.com/en/news/azul-c16.html)

## 📈 Project Status

This project is actively under development. See the [project board](https://github.com/your-username/azul-solver/projects) for current progress and upcoming milestones.

---

**Note**: This project extends the original educational framework into a production-ready Azul analysis toolkit while maintaining the core game logic and rules compliance.
