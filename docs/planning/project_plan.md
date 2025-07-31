# 🌌 Azul Solver & Analysis Toolkit — Robust Planning Document
> **Goal:** Deliver a Python‑based engine, web UI, and research tools that (i) compute *exact* values for tactical depths, (ii) return sub‑200 ms live hints, and (iii) support long‑term strategy research.

---

## 1 · Product Vision & Non‑Negotiables
| Pillar | Must‑Have Outcome |
| ------ | ---------------- |
| **Correctness** | Full rules compliance; deterministic engines yield identical outputs given identical seeds. |
| **Speed** | ≤ 200 ms hint latency on laptop (8‑core CPU) for 95th %ile mid‑game positions. |
| **Extensibility** | Plug‑in search modules (Alpha‑Beta, MCTS, Neural) & UI widgets without core rewrites. |
| **Reproducibility** | Docker image + CI matrix for Linux/macOS/Win. |
| **Licensing** | GPL v3 for engine/UI; third‑party assets clearly attributed. |

---

## 2 · Epic Breakdown & Core Feature Sets

### EPIC A — Engine (core/`azul_core`) ✅ **COMPLETE**
| Story | Details | Done? |
| ----- | ------- | ----- |
| **A1 State Model** | Immutable dataclass + NumPy arrays; 64‑bit Zobrist key; `clone()`, `undo()` diff stack. | ☑ |
| **A2 Rule Validator** | Enforce draft → placement → floor penalties → scoring & bonuses; 100 golden tests. | ☑ |
| **A3 Move Generator** | Enumerate legal *compound* moves (`DraftOption × PlacementTarget`), return vector mask. | ☑ |
| **A4 Heuristic Eval v1** | Immediate score + pattern‑potential + penalty est.; O(1). | ☑ |
| **A5 Alpha–Beta Module** | Iterative deepening, move ordering, killer/hist heuristics, TT replacement table. | ☑ |
| **A6 MCTS Module** | UCT + virtual loss; pluggable rollout policy (`random`, `heavy`, `nn`). | ☑ |
| **A7 Neural Bridge** | Torch `AzulNet` (policy+value); GPU batcher; fall‑back to CPU eager. | ☑ |
| **A8 Exact Endgame Solver** | Retrograde DB for ≤ N‑tile positions; symmetry hashing. | ☑ |
| **A9 Profiling Harness** | `pytest‑bench` benches, `cProfile` + `py‑spy` scripts; perf budget alerts. | ☑ |

### EPIC B — Data & Storage (`azul_db`) 🎯 **NEXT PRIORITY**
| Story | Details | Done? |
| ----- | ------- | ----- |
| **B1 Schema v1** | SQLite WAL; tables: `position`, `analysis`, `game`; Zstd BLOB compression. | ☐ |
| **B2 Position Cache API** | `get(hash)`, `put(...)`, bulk import/export. | ☐ |

### EPIC C — REST & CLI (`azul_api`, `azcli`) 📋 **PLANNED**
| Story | Path | Done? |
| ----- | ---- | ----- |
| **C1 Analyze** | `POST /api/v1/analyze` → `{bestMove, pv, evDelta}` | ☐ |
| **C2 Quiz** | `GET /api/v1/quiz/random` with filters | ☐ |
| **C3 CLI Exact** | `azcli exact "<fen>" --depth 3` | ☐ |
| **C4 CLI Hint** | `azcli hint "<fen>" --budget 0.2s` | ☐ |

### EPIC D — Web UI (`ui/` React + Tailwind + SVG) 📋 **PLANNED**
| Story | Acceptance Criteria | Done? |
| ----- | ------------------ | ----- |
| **D1 Board Renderer** | Factories + center + player boards in responsive SVG; drag‑n‑drop tiles. | ☑ |
| **D2 Heatmap Overlay** | Tiles/factories tinted according to EV delta (green→red); legend. | ☑ |
| **D3 PV Panel** | Top‑3 moves list with score diff; click to load what‑if variation. | ☑ |
| **D4 What‑if Sandbox** | User can play hypothetical moves; engine auto‑responds. | ☐ |
| **D5 Replay Annotator** | Upload log → timeline w/ blunder markers ≥ Δ3. | ☐ |
| **D6 Opening Explorer** | Tree browser: position thumbnails, frequency counts. | ☐ |
| **D7 Auth & Rate‑Limit** | Session cookie + user DB; 10 heavy analyses/min. | ☑ |

### EPIC E — Infrastructure 📋 **PLANNED**
| Story | Key Tasks | Done? |
| ----- | -------- | ----- |
| **E1 CI/CD** | GitHub Actions: lint, tests, bench thresholds, Docker build, push to GHCR. | ☐ |
| **E2 Docker Image** | Multi‑stage `python:3.11-slim`; final < 300 MB; entry `gunicorn wsgi:app`. | ☐ |
| **E3 Fly.io Deploy** | `fly launch` with 1 CPU / 256 MB; health‑check `/healthz`. | ☐ |
| **E4 GPU Variant** | Optional Nvidia base + Torch CUDA; env flag `USE_GPU=1`. | ☐ |
| **E5 Observability** | Prometheus metrics: request latency, nodes/sec, GPU util. | ☐ |

---

## 3 · Delivery Roadmap (Gantt‑ish)
| Milestone | Duration | Output |
| ----------| -------- | ------ |
| **M0 Bootstrap** | 1 w | Repo, CI, basic Docker skeleton. |
| **M1 Rules Engine** | 2 w | A1‑A3 complete; golden tests pass. |
| **M2 Exact Search α** | 2 w | A4‑A5; CLI exact; depth‑3 <4 s. |
| **M3 Fast Hint β** | 2 w | A6, B1, C1/C4; 200 ms budget met. |
| **M4 Web UI α** | 3 w | D1‑D3; live hints in browser. |
| **M5 Research Tools** | 2 w | B2‑B3, D4‑D6, CLI quiz. |
| **M6 Neural Add‑on** | 3 w | A7 + GPU batcher; >60 % win vs heuristic. |
| **M7 Endgame DB** | 1 w | A8 retrograde tables; integrated into search. |
| **M8 Perf & Harden** | 2 w | A9, E1‑E5; load test 50 concurrent users. |
| **M9 v1 Release** | 1 w | Tagged v1.0, docs, demo video, blog post. |

*(Total ~17 weeks; adjust after each retrospective.)*

---

## 4 · Acceptance Criteria Snapshot

| Feature | Test |
| ------- | ---- |
| **Engine depth‑3** | `azcli exact "<initial>" --depth 3` completes ≤ 4 s, returns legal PV. |
| **200 ms hint** | `azcli hint "<midgame>" --budget 0.2` return includes `evDelta` & `bestMove` in JSON. |
| **UI drag‑drop** | User drags tiles from factory to pattern line; server validates, board re‑renders. |
| **Heatmap** | Hover tooltip shows numeric ΔEV; color scale matches legend spec. |
| **DB compression** | 1 M states disk usage ≤ 30 MB (verified via `du`). |
| **Rate limit** | Exceeding 10 heavy calls/min responds `429` with retry‑after header. |

---

## 5 · Risk Register (top 5)
| # | Risk | Exposure | Mitigation |
| - | ---- | -------- | ---------- |
| R1 | Python performance insufficient → >200 ms hints | High | Cython hot‑loops, tune rollout count, fallback to heuristic only. |
| R2 | DB lock contention under multi‑user | Med | WAL, async queue, Postgres migration path. |
| R3 | UI SVG drag on mobile glitchy | Med | Add touch handlers, fallback buttons. |
| R4 | Neural module slows hints | Low | Toggle, async pre‑compute, GPU batching. |
| R5 | Licensing conflicts (GPL code) | Low | Use MIT components only; legal review before merge. |

---

## 6 · Definitions & Glossary
| Term | Meaning |
| ---- | ------- |
| **FEN** | Compact text encoding of Azul state for CLI/API. |
| **EV delta** | Expected value difference from best move vs chosen move. |
| **Heavy Playout** | Monte‑Carlo rollout guided by heuristic policy. |
| **TT** | Transposition Table; hash map of explored states. |

---

## 7 · Task Templates (example)

```md
### Story A3 — Move Generator
- [ ] ✓ Parse factories + center, enumerate color choices.  
- [ ] ✓ Cross‑product with placement targets (rows + floor).  
- [ ] ✓ Return both *Move* struct & bit‑index for policy mask.  
- [ ] ✓ Benchmark: ≤ 15 µs / call (Numba JIT).  
- [ ] ✓ Unit‑tests: random 1 000 states → generator moves ✓ legal & complete.

```