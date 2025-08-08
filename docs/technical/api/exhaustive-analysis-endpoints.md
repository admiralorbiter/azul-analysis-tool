# Exhaustive Analysis API Endpoints

Comprehensive endpoints for managing large-scale/exhaustive analysis sessions and retrieving results. Unless noted, endpoints require a valid `X-Session-ID` header.

Base path: `/api/v1`

## Start a session

- Method: `POST`
- Path: `/exhaustive-analysis/start`
- Body:
  - `mode`: `"quick" | "standard" | "deep" | "exhaustive"` (default: `standard`)
  - `positions`: integer count to analyze (alias: `num_positions`)
  - `maxWorkers`: optional integer worker count
  - `sessionId`: optional custom session id
- Response: `{ success, message, session_id, pid, log_file }`

## Check progress

- Method: `GET`
- Path: `/exhaustive-analysis/progress/{session_id}`
- Response: `{ success, session_id, status, positions_analyzed, planned_positions, progress_percent, elapsed_seconds }`

## Stop a session

- Method: `POST`
- Path: `/exhaustive-analysis/stop/{session_id}`
- Response: `{ success, session_id, status: "stopped" }`

## List sessions

- Method: `GET`
- Path: `/exhaustive-analysis/sessions`
- Query params: `status` (running|completed|failed|stopped), `limit` (default 50)
- Response: `{ success, sessions: [...] }`

## Session details and results

- Method: `GET`
- Path: `/exhaustive-session/{session_id}`
- Alias: `GET /exhaustive-analysis/results/{session_id}`
- Response: `{ success, session: { ...analyses[] } }`

## Session stats (aggregated)

- Method: `GET`
- Path: `/exhaustive-analysis/stats/{session_id}`
- Response: `{ success, positions_analyzed, planned_positions, total_moves_analyzed, average_quality_score }`

## Delete a session (and its analyses)

- Method: `DELETE`
- Path: `/exhaustive-analysis/sessions/{session_id}`
- Response: `{ success, session_id }`

## System status

- Method: `GET`
- Path: `/exhaustive-analysis/status`
- Response: `{ success, status, running_sessions, total_runtime_sessions }`

## Export session

- Method: `GET`
- Path: `/exhaustive-analysis/export/{session_id}`
- Response: same shape as session details

## Latest comprehensive analysis for a position

- Method: `GET`
- Path: `/exhaustive-analysis/{position_fen}`
- Response: `{ success, analysis }` (latest for that position)

### Analysis object

The `analysis` object aggregates the latest comprehensive results for a position. Important fields:

- `position_fen`: string – canonical FEN identifier used for the lookup
- `game_phase`: string – opening|mid|end
- `total_moves_analyzed`: integer
- `quality_distribution`: object – JSON map of quality tier → count
- `average_quality_score`: number
- `best_move_score`: number
- `worst_move_score`: number
- `engine_consensus`: object – per-engine agreement/score
- `disagreement_level`: number (0.0–1.0)
- `position_complexity`: number (0.0–1.0)
- `strategic_themes`: string[] – high-level themes detected for the position
- `tactical_opportunities`: string[] – concrete tactical opportunities available
- `analysis_time`: number (seconds)
- `created_at`: ISO timestamp
- `moves`: array of per-move comprehensive results

Example (truncated):

```json
{
  "success": true,
  "analysis": {
    "position_fen": "initial",
    "total_moves_analyzed": 42,
    "quality_distribution": {"!!": 1, "!": 7, "=": 25, "?!": 7, "?": 2},
    "engine_consensus": {"alpha_beta": 0.7, "mcts": 0.68, "neural": 0.69},
    "position_complexity": 0.62,
    "strategic_themes": [
      "Factory control pressure",
      "Endgame setup available"
    ],
    "tactical_opportunities": [
      "Immediate block on blue",
      "Double-score setup on row 3"
    ],
    "moves": [
      { "move_data": {"description": "..."}, "overall_quality_score": 82.5, "quality_tier": "!" }
    ]
  }
}
```

## Related endpoints

These support discovery and insights around analyzed data:

- `GET /best-analyses` → top analyses by average score
- `GET /analysis-stats` → global aggregated stats
- `POST /search-positions` → filter positions by quality/phase/disagreement

## Notes

- Positions and analyses are persisted in the SQLite database; see schema in summaries under `docs/`.
- Some endpoints may return additional fields when the server runs in debug mode (e.g., a `debug` object on progress).
- Progress polling cadence in the UI is typically ~1.5s; servers without websockets should prefer polling.


