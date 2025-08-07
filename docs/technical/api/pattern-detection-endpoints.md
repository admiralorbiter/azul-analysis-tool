# Pattern Detection API Endpoints

## Overview

The Pattern Detection API provides endpoints for analyzing game positions and identifying tactical opportunities, particularly tile blocking scenarios.

## Base URL

```
POST /api/v1/detect-patterns
```

## Authentication

Protected endpoints require a valid session. Include your session ID:

```
X-Session-ID: YOUR_SESSION_ID
```

## Endpoints

### Detect Patterns

**Endpoint:** `POST /api/v1/detect-patterns`

**Description:** Analyzes a game position to identify blocking opportunities and tactical patterns.

#### Request Format

```json
{
    "fen_string": "high_urgency_red_blocking",
    "current_player": 0,
    "include_blocking_opportunities": true,
    "include_move_suggestions": true,
    "urgency_threshold": 0.6,
    "max_results": 10
}
```

#### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fen_string` | string | required | FEN string or test position identifier |
| `current_player` | integer | 0 | Player index (0-based) |
| `include_blocking_opportunities` | boolean | true | Include blocking analysis |
| `include_move_suggestions` | boolean | true | Include concrete move suggestions |
| `urgency_threshold` | float | 0.7 | Minimum urgency score (0.0-1.0) |
| `max_results` | integer | 10 | Maximum number of patterns to return |

#### Response Format

```json
{
    "blocking_opportunities": [
        {
            "target_player": 1,
            "pattern_line": 2,
            "blocking_color": "red",
            "urgency_score": 0.85,
            "tiles_needed": 2,
            "tiles_available": 3,
            "description": "Block red tiles in pattern line 2"
        }
    ],
    "move_suggestions": [
        {
            "factory_index": 0,
            "color": "red",
            "target_pattern_line": 2,
            "urgency_score": 0.85,
            "description": "Take red tiles from factory 0"
        }
    ],
    "total_patterns": 1,
    "patterns_detected": true,
    "confidence_score": 0.92,
    "execution_time": 0.045
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `blocking_opportunities` | array | List of blocking opportunities found |
| `move_suggestions` | array | Concrete move suggestions |
| `total_patterns` | integer | Total number of patterns detected |
| `patterns_detected` | boolean | Whether any patterns were found |
| `confidence_score` | float | Overall confidence in analysis (0.0-1.0) |
| `execution_time` | float | Analysis execution time in seconds |

#### Blocking Opportunity Object

| Field | Type | Description |
|-------|------|-------------|
| `target_player` | integer | Player being blocked (0-based) |
| `pattern_line` | integer | Pattern line number (1-5) |
| `blocking_color` | string | Color to block ("red", "blue", "yellow", "black", "white") |
| `urgency_score` | float | Urgency score (0.0-1.0) |
| `tiles_needed` | integer | Tiles needed to complete pattern line |
| `tiles_available` | integer | Available tiles of blocking color |
| `description` | string | Human-readable description |

#### Move Suggestion Object

| Field | Type | Description |
|-------|------|-------------|
| `factory_index` | integer | Factory to take tiles from (0-4) |
| `color` | string | Color to take |
| `target_pattern_line` | integer | Pattern line to place tiles in |
| `urgency_score` | float | Urgency score (0.0-1.0) |
| `description` | string | Human-readable description |

## Test Positions

The API supports several predefined test positions for development and testing:

### Blocking Test Positions

| FEN String | Description | Difficulty |
|------------|-------------|------------|
| `high_urgency_red_blocking` | High urgency red blocking scenario | Intermediate |
| `medium_urgency_blue_blocking` | Medium urgency blue blocking | Beginner |
| `low_urgency_yellow_blocking` | Low urgency yellow blocking | Advanced |

### Usage Examples

#### Python Example

```python
import requests

url = "http://localhost:8000/api/v1/detect-patterns"
data = {
    "fen_string": "high_urgency_red_blocking",
    "current_player": 0,
    "urgency_threshold": 0.6
}

response = requests.post(url, json=data)
result = response.json()

if result["patterns_detected"]:
    for opportunity in result["blocking_opportunities"]:
        print(f"Block {opportunity['blocking_color']} in line {opportunity['pattern_line']}")
```

#### JavaScript Example

```javascript
const response = await fetch('/api/v1/detect-patterns', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-Session-ID': sessionId
    },
    body: JSON.stringify({
        fen_string: 'high_urgency_red_blocking',
        current_player: 0,
        urgency_threshold: 0.6
    })
});

const result = await response.json();

if (result.patterns_detected) {
    result.blocking_opportunities.forEach(opp => {
        console.log(`Block ${opp.blocking_color} in line ${opp.pattern_line}`);
    });
}
```

## Error Handling

### Common Error Responses

#### 400 Bad Request

```json
{
    "error": "Invalid FEN string format",
    "details": "Unsupported FEN format: invalid_position"
}
```

#### 422 Unprocessable Entity

```json
{
    "error": "Invalid game state",
    "details": "Game state validation failed"
}
```

#### 500 Internal Server Error

```json
{
    "error": "Pattern detection failed",
    "details": "Analysis engine error"
}
```

## Configuration

### Pattern Detection Settings

The API supports configurable parameters for pattern detection:

- **Urgency Threshold**: Minimum score for pattern inclusion (0.0-1.0)
- **Max Results**: Maximum number of patterns to return
- **Include Blocking**: Whether to include blocking analysis
- **Include Moves**: Whether to include move suggestions

### Performance Considerations

- **Execution Time**: Typically < 100ms for standard positions
- **Memory Usage**: Minimal for single position analysis
- **Caching**: Results cached for identical positions
- **Concurrent Requests**: Supports multiple simultaneous analyses

## Integration Notes

### Frontend Integration

The API is designed to work seamlessly with the React frontend:

1. **Real-time Analysis**: Call API on game state changes
2. **Debounced Requests**: Implement request debouncing for performance
3. **Error Handling**: Graceful fallback for API failures
4. **Loading States**: Show loading indicators during analysis

### Backend Integration

The API integrates with the core pattern detection engine:

1. **State Validation**: Validates game state before analysis
2. **Error Propagation**: Proper error handling and logging
3. **Performance Monitoring**: Execution time tracking
4. **Caching**: Result caching for performance

## Related Documentation

- [Pattern Detection User Guide](../guides/analysis/pattern-detection.md) - User guide for pattern detection
- [Pattern Detection Technical Guide](../implementation/pattern-detection.md) - Technical implementation details
- [API Reference](../api/endpoints.md) - Complete API documentation 