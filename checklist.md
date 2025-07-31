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

## 5 · Neural Assist (optional GPU) 📋
- [ ] Define tensor encoding (⩽ 100 ints → one‑hot / embed).
- [ ] Build tiny PyTorch MLP (≤ 100 k params) for value + policy.
- [ ] Batch inference (≥ 32 states) on RTX 30xx; record ms/1000 evals.
- [ ] Integrate into MCTS; compare win‑rate vs heuristic playouts.

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
- **✅ Bootstrap Complete**: Repository setup, CI skeleton, import conflicts resolved
- **✅ M1 Complete**: Rules engine (A1-A3) - All tests passing
- **✅ M2 Complete**: Exact search (A4-A5) - All tests passing, CLI integration complete
- **✅ M3 Complete**: Fast hint engine (A6) - All tests passing, < 200ms target achieved
- **✅ M4 Complete**: Database integration (B1) - All tests passing, SQLite caching operational
- **📋 M5-M9 Planned**: REST API, Web UI, neural modules, endgame solver
- **🎯 Target**: 17-week delivery timeline with weekly retrospectives