# Known Limitations and In-Progress Items

This page summarizes intentional gaps or areas under active development so users understand current behavior.

## Engine and Analysis
- MCTS rollout policy: Early-game behavior may return placeholder/low-confidence values; improvements planned (rollout policy, terminal detection, principal variation tracking).
- Alternative move identification: Present in responses, but selection/rationale will be improved for diversity and explanation quality.
- Position complexity score: Uses a simple heuristic; expect refinements for phase-aware complexity.

## API and UX
- Real-time push: Progress updates use polling; SSE or WebSockets may be added later for push updates.
- CORS configuration: Prefer Flask-CORS configuration as the single source of truth; custom middleware should be kept in sync.
- Auth model: Session header `X-Session-ID` is used for protected endpoints; some read-only endpoints are public for the UI’s convenience.

## Documentation
- Performance numbers are representative; throughput depends on hardware and dataset.
- Some archived docs reference old endpoints; the current sources of truth are `docs/api/` and `docs/technical/api/` (see `technical/api/INDEX.md`).

—
Keep this page aligned when closing any item above.
