# Move Quality API Endpoints

## Overview

Endpoints for move quality assessment and comprehensive evaluation backed by the Move Quality Assessment system.

Base path: `/api/v1`

## Authentication

These endpoints currently do not require authentication in code. If you have an active session workflow elsewhere, you may include `X-Session-ID`, but it is not required for these specific endpoints.

## Canonical Endpoints

Preferred, unified endpoints provided by the move analysis module.

## Endpoints

### Analyze Move Quality (canonical)

POST `/api/v1/analyze-move-quality`

Analyze the position for the current player and return the primary recommendation with quality tier and explanation. Optionally include alternative moves.

Request body:
```json
{
  "fen_string": "position_identifier_or_fen",
  "current_player": 0,
  "include_alternatives": true,
  "max_alternatives": 4
}
```

Response example:
```json
{
  "success": true,
  "primary_recommendation": {
    "move": { "description": "Take blue from factory 1 to pattern line 2" },
    "quality_tier": "=",
    "quality_score": 62.5,
    "blocking_score": 10.0,
    "scoring_score": 28.0,
    "floor_line_score": -5.0,
    "strategic_score": 5.0,
    "primary_reason": "Excellent scoring opportunity",
    "risk_level": "low"
  },
  "alternatives": [
    {
      "move": { "description": "..." },
      "quality_tier": "=",
      "quality_score": 58.2,
      "blocking_score": 8.0,
      "scoring_score": 24.0,
      "floor_line_score": -3.0,
      "strategic_score": 4.0,
      "primary_reason": "Solid blocking value",
      "risk_level": "low"
    }
  ],
  "total_moves_analyzed": 50,
  "analysis_summary": "Best move: = | 50 moves analyzed | Distribution: ...",
  "analysis_time_ms": 145.7,
  "is_real_data": false,
  "data_quality": "mock",
  "fen_string_analyzed": "initial"
}
```

Notes:
- `include_alternatives` returns up to `max_alternatives` alternative moves if available.
- `is_real_data` is inferred from the FEN format.

### Evaluate All Moves (canonical)

POST `/api/v1/evaluate-all-moves`

Evaluate all legal moves for a position and return a map of move descriptions to quality details, plus ranked lists.

Request body:
```json
{
  "fen_string": "position_identifier_or_fen",
  "player_id": 0
}
```

Response example:
```json
{
  "success": true,
  "all_moves_quality": {
    "Take blue from factory 1 to pattern line 2": {
      "overall_score": 62.5,
      "quality_tier": "=",
      "strategic_value": 5.0,
      "tactical_value": 28.0,
      "risk_assessment": 15.0,
      "opportunity_value": 10.0,
      "explanation": "...",
      "confidence_score": 0.8
    }
  },
  "best_moves": ["Take blue from factory 1 to pattern line 2"],
  "alternative_moves": ["Take red from center to pattern line 3"],
  "position_complexity": 0.6,
  "analysis_confidence": 0.8,
  "is_real_data": false,
  "analysis_time_ms": 187.1
}
```

### System Info

GET `/api/v1/move-quality-info`

Returns capabilities and configuration of the move quality system.

### Test Endpoint

GET `/api/v1/test-move-quality`

Runs a basic internal analysis to verify the pipeline is functional.

## Legacy Endpoints (compatibility)

These endpoints are registered for compatibility and may use slightly different payload field names.

### Assess a Specific Move (legacy)

POST `/api/v1/assess-move-quality`

Request body:
```json
{
  "state_fen": "game_state_fen_string",
  "player_id": 0,
  "move_key": "factory_0_tile_blue_pattern_line_1"
}
```

### Evaluate All Moves (legacy)

POST `/api/v1/evaluate-all-moves`

Request body:
```json
{
  "state_fen": "game_state_fen_string",
  "player_id": 0
}
```

## Curl examples

```bash
# Analyze move quality (canonical)
curl -X POST http://localhost:8000/api/v1/analyze-move-quality \
  -H "Content-Type: application/json" \
  -d '{
    "fen_string": "initial",
    "current_player": 0,
    "include_alternatives": true,
    "max_alternatives": 3
  }'

# Evaluate all moves (canonical)
curl -X POST http://localhost:8000/api/v1/evaluate-all-moves \
  -H "Content-Type: application/json" \
  -d '{
    "fen_string": "initial",
    "player_id": 0
  }'

# Assess a specific move (legacy)
curl -X POST http://localhost:8000/api/v1/assess-move-quality \
  -H "Content-Type: application/json" \
  -d '{
    "state_fen": "initial",
    "player_id": 0,
    "move_key": "factory_0_tile_blue_pattern_line_1"
  }'
```

## Notes and Limitations

- Alternative move identification uses current heuristics; diversity-aware selection is planned.
- Position complexity is a simple heuristic and may be refined.
- See `docs/KNOWN_LIMITATIONS.md` for engine-level notes (e.g., early-game MCTS rollout policy improvements planned).


