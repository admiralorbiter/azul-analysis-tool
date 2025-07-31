# Azul Solver & Toolkit – Build Checklist

## 0 · Project Bootstrap ✅
- [x] Create Git repository (azul‑solver) and push LICENSE (GPL v3) + README.
- [x] Set up Python 3.11 tool‑chain (pyenv, tox, ruff, pre‑commit, black).
- [x] Enable CI (GitHub Actions) → run unit tests & ruff --fix on every push.
- [x] Add issue labels & project board (engine, ui, perf, docs, infra).

## 1 · Game Engine Core (MVP) ✅
- [x] Import / re‑implement Azul rules engine (start from AzulRL MIT code).
- [x] Encode state as immutable dataclass of NumPy arrays + 64‑bit Zobrist key.
- [x] Implement fast clone / undo helpers (struct copy or diff stack).
- [x] Unit‑test 100 official rule cases (wall color, floor overflow, final bonuses).

## 2 · Exact Search Prototype ✅
- [x] Implement depth‑limited alpha‑beta with:
  - [x] Move generation filtering (illegal / score‑dominated moves gone).
  - [x] Iterative deepening & TT (64‑bit keys, replacement scheme).
  - [x] Move ordering: wall‑completion ≫ penalty‑free ≫ others.
- [x] CLI tool azsolver exact <FEN> → returns PV + exact score for depth≤3.
- [x] Micro‑benchmarks: nodes/sec; verify memory stays < 2 GB @ depth 3.

## 3 · Fast Hint Engine ✅
- [x] Plug heuristic evaluation (immediate score + pattern potential).
- [x] Add MCTS (UCT) with pluggable rollout policy:
  - [x] Plain random.
  - [x] Heavy playout heuristic.
  - [x] Neural (future phase).
- [x] Target ⩽ 200 ms / move on laptop (≤ 300 rollouts random, ≤ 100 heavy).
- [x] Export single‑move JSON hint: {move, evDelta, pv}.

## 4 · Database Integration ✅
- [x] Create SQLite schema (Position, Game, Analysis tables).
- [x] Enable WAL mode + index on hash.
- [x] Add Zstd compression helper; target ≤ 25 MB / 1 M states.
- [x] Alembic migration scripts; test SQLite → Postgres switch.

## 5 · Neural Assist (optional GPU) ✅
- [x] Define tensor encoding (⩽ 100 ints → one‑hot / embed).
- [x] Build tiny PyTorch MLP (≤ 100 k params) for value + policy.
- [x] Integrate into MCTS; compare win‑rate vs heuristic playouts.
- [ ] Batch inference (≥ 32 states) on RTX 30xx; record ms/1000 evals.
- [ ] Complete policy-to-move mapping for neural rollout policy.

## 6 · Research Utilities 📋
- [ ] Opening explorer: breadth‑first enumerate to ply 4 → store in DB.
- [ ] Replay annotator: parse BGA log → annotate blunders (ΔEV ≥ 3).
- [ ] Quiz generator: random mid‑game positions with ≥ 2 pt tactic.
- [ ] Add CLI commands aztools openings / annotate / quiz.

## 7 · Web API (Flask) 📋
- [ ] Flask blueprint /api/v1/analyze (POST state → JSON response).
- [ ] Auth middleware (JWT or session cookie).
- [ ] Rate‑limit (e.g., 10 heavy analyses / min / IP).
- [ ] Swagger / OpenAPI docs auto‑generated.

## 8 · Web UI 📋
- [ ] React + SVG board component with drag‑and‑drop tiles.
- [ ] Heat‑map overlay of EV deltas (green → red gradient).
- [ ] PV viewer panel (top 3 moves with score diff).
- [ ] "What‑if" sandbox mode (user explores branches).

## 9 · Performance & Profiling 📋
- [ ] Add cProfile + py-spy scripts; track top 5 hotspots.
- [ ] Cython / Numba accelerate apply_move & generate_moves.
- [ ] Memory watch‑dog (halt search @ max RAM or TT entries).
- [ ] Benchmark table (three test states) → update BENCH.md.

## 10 · Docker & Deployment 📋
- [ ] Multi‑stage python:3.11-slim build; wheels cached.
- [ ] Prod image < 300 MB; gunicorn entrypoint.
- [ ] Deploy on Fly.io (CPU) & optional GPU build (Nvidia runtime).
- [ ] Add health‑check endpoint /healthz.

## 11 · Documentation & Release 📋
- [ ] Write design doc (≤ 12 pages) summarizing algorithms & API.
- [ ] Tutorial notebook: solve sample position, request hint, view UI.
- [ ] Version v0.1.0 GitHub release; attach Docker image digest.
- [ ] Open‑source announcement post (BGG / Reddit r/boardgameAI).

## 12 · Risk Tracking & Mitigation 📋
- [ ] Maintain RISK_LOG.md with top 10 risks + status.
- [ ] Weekly review of open risks; close / re‑mitigate as needed.

---

## Current Status Summary
- **✅ Epic A Complete**: Engine Core (A1-A9) - All components operational with 252 tests passing
- **🎯 Epic B Next**: Data & Storage (B1-B3) - SQLite with PostgreSQL migration path
- **📋 Epic C Planned**: REST & CLI (C1-C4) - API endpoints and CLI tools
- **📋 Epic D Planned**: Web UI (D1-D7) - React components and interactive analysis
- **📋 Epic E Planned**: Infrastructure (E1-E5) - Docker, CI/CD, deployment
- **🎯 Target**: 17-week delivery timeline with weekly retrospectives

## Epic B - Data & Storage 🎯 **NEXT PRIORITY**

### B1: Schema v1 - SQLite Foundation
- [ ] Design SQLite schema with WAL mode for performance
- [ ] Create `position` table with Zobrist hash indexing
- [ ] Create `analysis` table for caching search results
- [ ] Create `game` table for full game tracking
- [ ] Implement Zstd BLOB compression for state storage
- [ ] Add proper foreign key constraints and indexes
- [ ] Create database migration scripts
- [ ] Write comprehensive database tests (20+ tests)
- [ ] Performance target: < 1ms per position cache operation

### B2: Position Cache API
- [ ] Implement `get(hash)` method for position retrieval
- [ ] Implement `put(...)` method for position storage
- [ ] Add bulk import/export functionality
- [ ] Create cache eviction policies
- [ ] Add cache statistics and monitoring
- [ ] Integrate with existing search components
- [ ] Write API tests (15+ tests)
- [ ] Performance target: < 2ms per bulk operation

### B3: PostgreSQL Migration
- [ ] Set up Alembic for database migrations
- [ ] Create PostgreSQL connection pooling
- [ ] Implement performance optimization strategies
- [ ] Add database configuration management
- [ ] Create migration scripts for SQLite → PostgreSQL
- [ ] Add database health monitoring
- [ ] Write migration tests (10+ tests)
- [ ] Performance target: 50% improvement over SQLite

## Epic C - REST & CLI 📋 **PLANNED**

### C1: Analyze Endpoint
- [ ] Create `POST /api/v1/analyze` endpoint
- [ ] Implement request validation and error handling
- [ ] Add response format: `{bestMove, pv, evDelta}`
- [ ] Integrate with existing search components
- [ ] Add rate limiting and authentication
- [ ] Write API tests (15+ tests)
- [ ] Performance target: < 200ms response time

### C2: Quiz Endpoint
- [ ] Create `GET /api/v1/quiz/random` endpoint
- [ ] Implement position filtering and difficulty levels
- [ ] Add quiz generation algorithms
- [ ] Create quiz validation and scoring
- [ ] Write API tests (10+ tests)

### C3: CLI Exact Command
- [ ] Implement `azcli exact "<fen>" --depth 3` command
- [ ] Add command-line argument parsing
- [ ] Integrate with alpha-beta search
- [ ] Add output formatting options
- [ ] Write CLI tests (10+ tests)

### C4: CLI Hint Command
- [ ] Implement `azcli hint "<fen>" --budget 0.2s` command
- [ ] Add time budget management
- [ ] Integrate with MCTS for fast hints
- [ ] Add hint quality metrics
- [ ] Write CLI tests (10+ tests)

## Epic D - Web UI 📋 **PLANNED**

### D1: Board Renderer
- [ ] Create React + SVG board component
- [ ] Implement drag-and-drop tile functionality
- [ ] Add responsive design for mobile/desktop
- [ ] Create board state management
- [ ] Write component tests (15+ tests)

### D2: Heatmap Overlay
- [ ] Implement EV delta visualization
- [ ] Add color coding (green→red gradient)
- [ ] Create interactive tooltips
- [ ] Add legend and controls
- [ ] Write visualization tests (10+ tests)

### D3: PV Panel
- [ ] Create principal variation display
- [ ] Add move selection functionality
- [ ] Implement score difference display
- [ ] Add move history tracking
- [ ] Write panel tests (10+ tests)

### D4: What-if Sandbox
- [ ] Implement hypothetical move system
- [ ] Add engine auto-response
- [ ] Create branch exploration interface
- [ ] Add undo/redo functionality
- [ ] Write sandbox tests (15+ tests)

### D5: Replay Annotator
- [ ] Create log upload functionality
- [ ] Implement blunder detection (≥ Δ3)
- [ ] Add timeline visualization
- [ ] Create annotation export
- [ ] Write annotator tests (10+ tests)

### D6: Opening Explorer
- [ ] Implement tree browser interface
- [ ] Add position thumbnails
- [ ] Create frequency count display
- [ ] Add opening database integration
- [ ] Write explorer tests (10+ tests)

### D7: Auth & Rate-Limit
- [ ] Implement session-based authentication
- [ ] Add user database management
- [ ] Create rate limiting (10 heavy analyses/min)
- [ ] Add security measures
- [ ] Write auth tests (15+ tests)

## Epic E - Infrastructure 📋 **PLANNED**

### E1: CI/CD
- [ ] Set up GitHub Actions workflow
- [ ] Add linting and code quality checks
- [ ] Implement benchmark threshold monitoring
- [ ] Create Docker build pipeline
- [ ] Add automated testing matrix
- [ ] Write CI/CD tests (10+ tests)

### E2: Docker Image
- [ ] Create multi-stage Dockerfile
- [ ] Optimize for `python:3.11-slim` base
- [ ] Target final image < 300 MB
- [ ] Add gunicorn entrypoint
- [ ] Create Docker health checks
- [ ] Write Docker tests (5+ tests)

### E3: Fly.io Deploy
- [ ] Set up Fly.io application
- [ ] Configure 1 CPU / 256 MB resources
- [ ] Add health-check endpoint `/healthz`
- [ ] Implement deployment automation
- [ ] Add monitoring and logging
- [ ] Write deployment tests (5+ tests)

### E4: GPU Variant
- [ ] Create Nvidia base image
- [ ] Add Torch CUDA support
- [ ] Implement `USE_GPU=1` environment flag
- [ ] Add GPU performance monitoring
- [ ] Create GPU-specific tests (5+ tests)

### E5: Observability
- [ ] Add Prometheus metrics
- [ ] Monitor request latency
- [ ] Track nodes per second
- [ ] Monitor GPU utilization
- [ ] Create observability tests (5+ tests)