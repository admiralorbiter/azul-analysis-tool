# 🌐 Azul Solver REST API Usage Guide

> **Note:** Board editing features (edit mode, element selection) are now available in the Web UI. Backend/CLI tests cover state logic; UI tests are manual only.

> Complete guide for using the Azul Solver REST API for game analysis, caching, and research.

## 🚀 Quick Start

### Starting the Server
```bash
# Basic server (default: http://127.0.0.1:8000)
python main.py serve

# With custom configuration
python main.py serve --host 0.0.0.0 --port 8080 --debug --database azul_cache.db
```

### Server Features
- **Authentication**: Session-based authentication with rate limiting (for analysis endpoints)
- **Database Integration**: SQLite caching with compression and indexing
- **CORS Support**: Web UI integration ready
- **Health Monitoring**: Built-in health checks and statistics
- **Error Handling**: Comprehensive error responses
- **Interactive Play**: Drag-and-drop move execution for web UI

## 🔐 Authentication

### Creating a Session
```bash
curl -X POST http://localhost:8000/api/v1/auth/session
```

**Response:**
```json
{
  "session_id": "abc123def456",
  "expires_in_minutes": 60,
  "message": "Session created successfully"
}
```

### Using Authentication
```bash
# Include X-Session-ID header on protected endpoints
curl -H "X-Session-ID: abc123def456" \
  http://localhost:8000/api/v1/health
```

**Note**: Interactive endpoints (`/api/v1/execute_move`, `/api/v1/game_state`, `/api/v1/reset_game`) do not require authentication for web UI integration.

## 🎮 Interactive Game Play

> **Note:** Board editing (edit mode, element selection) is available in the Web UI. Use the edit mode toggle in the Game Management panel to enable board editing. CLI/Backend tests cover state logic; UI tests are manual only.

### Execute Move
```bash
curl -X POST http://localhost:8000/api/v1/execute_move \
  -H "Content-Type: application/json" \
  -d '{
    "fen_string": "initial",
    "move": {
      "source_id": 0,
      "tile_type": 0,
      "pattern_line_dest": 0,
      "num_to_pattern_line": 1,
      "num_to_floor_line": 0
    },
    "agent_id": 0
  }'
```

**Response:**
```json
{
  "success": true,
  "new_state": {
    "agents": [...],
    "factories": [...],
    "center_pool": [...]
  },
  "move_applied": {
    "source_id": 0,
    "tile_type": 0,
    "pattern_line_dest": 0,
    "num_to_pattern_line": 1,
    "num_to_floor_line": 0
  }
}
```

### Get Game State
```bash
curl -X GET "http://localhost:8000/api/v1/game_state?fen_string=initial"
```

**Response:**
```json
{
  "success": true,
  "state": {
    "agents": [...],
    "factories": [...],
    "center_pool": [...]
  }
}
```

### Reset Game
```bash
curl -X POST http://localhost:8000/api/v1/reset_game
```

**Response:**
```json
{
  "success": true,
  "message": "Game reset to initial position"
}
```

## 🎯 Game Analysis

### Exact Analysis (Alpha-Beta Search)
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: YOUR_SESSION_ID" \
  -d '{
    "fen_string": "start",
    "depth": 3,
    "timeout": 4.0,
    "agent": 0
  }'
```

**Response:**
```json
{
  "analysis_id": "analysis_123",
  "fen_string": "start",
  "agent": 0,
  "search_type": "alpha_beta",
  "result": {
    "best_move": "take_from_factory:0:blue:pattern_line:0",
    "best_score": 15.5,
    "search_time": 2.34,
    "nodes_searched": 125000,
    "depth_reached": 3,
    "principal_variation": [
      "take_from_factory:0:blue:pattern_line:0",
      "take_from_factory:1:red:pattern_line:1"
    ]
  },
  "cached": false,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Fast Hints (MCTS)
```bash
curl -X POST http://localhost:8000/api/v1/hint \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: YOUR_SESSION_ID" \
  -d '{
    "fen_string": "start",
    "budget": 0.2,
    "rollouts": 100,
    "agent": 0
  }'
```

**Response:**
```json
{
  "analysis_id": "hint_456",
  "fen_string": "start",
  "agent": 0,
  "search_type": "mcts",
  "result": {
    "best_move": "take_from_factory:0:blue:pattern_line:0",
    "confidence": 0.85,
    "search_time": 0.15,
    "rollouts_completed": 100,
    "move_probabilities": {
      "take_from_factory:0:blue:pattern_line:0": 0.45,
      "take_from_factory:1:red:pattern_line:1": 0.30,
      "take_from_factory:2:yellow:pattern_line:2": 0.25
    }
  },
  "cached": false,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 💾 Position Cache

### Store Position
```bash
curl -X PUT http://localhost:8000/api/v1/positions/start \
  -H "X-Session-ID: YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "player_count": 2,
    "compressed_state": "base64_encoded_state_data",
    "metadata": {
      "game_phase": "opening",
      "tiles_remaining": 100,
      "created_by": "test_user"
    }
  }'
```

### Get Position
```bash
curl -X GET http://localhost:8000/api/v1/positions/start \
  -H "X-Session-ID: YOUR_SESSION_ID"
```

### Search Positions
```bash
# Basic search
curl -X GET "http://localhost:8000/api/v1/positions/search?limit=10&offset=0" \
  -H "X-Session-ID: YOUR_SESSION_ID"

# Advanced search with filters
curl -X GET "http://localhost:8000/api/v1/positions/search?limit=20&offset=0&player_count=2&game_phase=midgame" \
  -H "X-Session-ID: YOUR_SESSION_ID"
```

### Bulk Operations
```bash
# Bulk import
curl -X POST http://localhost:8000/api/v1/positions/bulk \
  -H "X-Session-ID: YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "positions": [
      {
        "fen_string": "position1",
        "player_count": 2,
        "compressed_state": "..."
      },
      {
        "fen_string": "position2", 
        "player_count": 2,
        "compressed_state": "..."
      }
    ],
    "overwrite": true
  }'

# Bulk export
curl -X GET "http://localhost:8000/api/v1/positions/bulk?limit=100&offset=0" \
  -H "X-Session-ID: YOUR_SESSION_ID"

# Bulk delete
curl -X DELETE http://localhost:8000/api/v1/positions/bulk \
  -H "X-Session-ID: YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "fen_strings": ["position1", "position2"]
  }'
```

## 📊 Analysis Cache

### Get Cached Analysis
```bash
curl -X GET http://localhost:8000/api/v1/analyses/start \
  -H "X-Session-ID: YOUR_SESSION_ID"
```

### Store Analysis Result
```bash
curl -X POST http://localhost:8000/api/v1/analyses/start \
  -H "X-Session-ID: YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": 0,
    "search_type": "alpha_beta",
    "result": {
      "best_move": "take_from_factory:0:blue:pattern_line:0",
      "best_score": 15.5,
      "search_time": 2.34,
      "nodes_searched": 125000,
      "depth_reached": 3
    },
    "parameters": {
      "depth": 3,
      "timeout": 4.0
    }
  }'
```

### Search Analyses
```bash
# Search by criteria
curl -X GET "http://localhost:8000/api/v1/analyses/search?search_type=alpha_beta&agent=0&limit=10" \
  -H "X-Session-ID: YOUR_SESSION_ID"

# Get recent analyses
curl -X GET "http://localhost:8000/api/v1/analyses/recent?limit=20&hours=24" \
  -H "X-Session-ID: YOUR_SESSION_ID"
```

## 📈 Performance & Monitoring

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "0.1.0",
  "components": {
    "database": "connected",
    "rate_limiter": "active",
    "session_manager": "active"
  }
}
```

### Performance Statistics
```bash
curl http://localhost:8000/api/v1/stats \
  -H "X-Session-ID: YOUR_SESSION_ID"
```

**Response:**
```json
{
  "api_stats": {
    "total_requests": 1250,
    "requests_per_minute": 15.2,
    "average_response_time": 0.045,
    "error_rate": 0.02
  },
  "database_stats": {
    "total_positions": 15000,
    "total_analyses": 25000,
    "cache_hit_rate": 0.85,
    "database_size_mb": 45.2
  },
  "search_stats": {
    "alpha_beta_requests": 800,
    "mcts_requests": 450,
    "average_search_time": 1.23,
    "average_nodes_per_second": 50000
  }
}
```

### Database Analytics
```bash
curl http://localhost:8000/api/v1/performance/analytics \
  -H "X-Session-ID: YOUR_SESSION_ID"
```

### System Monitoring
```bash
curl http://localhost:8000/api/v1/performance/monitoring \
  -H "X-Session-ID: YOUR_SESSION_ID"
```

## 🔧 Error Handling

### Common Error Responses

**401 Unauthorized:**
```json
{
  "error": "authentication_required",
  "message": "Valid session required",
  "details": "Include X-Session-ID header"
}
```

**429 Rate Limit Exceeded:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests",
  "details": "Rate limit: 100 requests per minute",
  "retry_after": 30
}
```

**400 Bad Request:**
```json
{
  "error": "validation_error",
  "message": "Invalid request parameters",
  "details": {
    "fen_string": "Required field",
    "depth": "Must be between 1 and 10"
  }
}
```

**500 Internal Server Error:**
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "details": "Please try again later"
}
```

## 🌐 Web UI Integration

### CORS Configuration
The API is configured with CORS support for web UI integration:
- Allowed origins: `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:8000`, `http://127.0.0.1:8000`
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type, X-Session-ID, Authorization

### Static File Serving
The API serves static files from the `ui/` directory:
```
http://localhost:8000/ui/index.html
http://localhost:8000/ui/static/css/style.css
http://localhost:8000/ui/static/js/app.js
```

## 📝 FEN String Format

The API uses a **standard FEN (Forsyth-Edwards Notation) format** for game positions. This format provides a compact, human-readable representation of the complete Azul game state.

### **Standard FEN Format**

The standard FEN format follows this structure:
```
factories/center/player1_wall/player1_pattern/player1_floor/player2_wall/player2_pattern/player2_floor/scores/round/current_player
```

**Format Breakdown:**
- **Factories**: 5 factories, each with 4 tiles (e.g., `BYRK|WBYR|KWBY|RKWB|YRKW`)
- **Center**: Center pool tiles (e.g., `BYRKW` or `-` if empty)
- **Player1 Wall**: 5x5 wall grid (e.g., `-----|-----|-----|-----|-----`)
- **Player1 Pattern**: 5 pattern lines (e.g., `-----|-----|-----|-----|-----`)
- **Player1 Floor**: Floor line tiles (e.g., `BYR` or `-` if empty)
- **Player2 Wall**: 5x5 wall grid
- **Player2 Pattern**: 5 pattern lines
- **Player2 Floor**: Floor line tiles
- **Scores**: Comma-separated scores (e.g., `0,0`)
- **Round**: Current round number (e.g., `1`)
- **Current Player**: Active player index (e.g., `0`)

**Example Standard FEN:**
```
BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0
```

### **FEN Types**

The system supports multiple FEN formats:

1. **Standard FEN** (Primary): Human-readable format as shown above
2. **Hash-based FEN** (`state_{hash}`): For unique state identification
3. **Base64 FEN** (`base64_{encoded}`): For encoded game data
4. **Special Positions**: Pre-defined positions like `"start"`, `"midgame"`, `"endgame"`, `"initial"`

### **FEN Validation**

The API provides FEN validation through the `/api/v1/validate-fen` endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/validate-fen \
  -H "Content-Type: application/json" \
  -d '{
    "fen_string": "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
  }'
```

**Response:**
```json
{
  "valid": true,
  "format": "standard",
  "details": {
    "factories": 5,
    "center_tiles": 5,
    "players": 2,
    "round": 1,
    "current_player": 0
  }
}
```

### **Game State Loading**

Load a game state from FEN using the `/api/v1/game_state` endpoint:

```bash
curl -X GET "http://localhost:8000/api/v1/game_state?fen_string=BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
```

**Response:**
```json
{
  "success": true,
  "game_state": {
    "factories": [...],
    "center": [...],
    "players": [...],
    "fen_string": "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
  }
}
```

### **Legacy FEN Format**

For backward compatibility, the API also supports the legacy FEN format:

```
<player_count>:<factory_state>:<center_state>:<player_states>
```

**Example:**
```
2:factory_0_blue_2_red_1_yellow_1:center_blue_1_red_1:player_0_pattern_0_blue_1_floor_0_score_0:player_1_pattern_0_red_1_floor_0_score_0
```

### **Special Positions**

- `"start"` - Initial game position
- `"midgame"` - Mid-game position for testing
- `"endgame"` - End-game position for testing
- `"initial"` - **Persistent initial position** - Uses a global state that persists across requests for interactive play

### **State Persistence**

For interactive web UI functionality, the API maintains a global game state when using `"initial"` as the FEN string. This ensures that:
- The game state persists across multiple move executions
- The UI's perceived state matches the backend's actual state
- Users can make multiple moves in sequence without state resets

To reset the persistent state, use the `/api/v1/reset_game` endpoint.

## ⚠️ Common Pitfalls & Solutions

### **1. FEN String Integration Issues**

**Problem**: New test positions not recognized by backend API
```python
# ERROR: ValueError: Unsupported FEN format: your_new_position
```

**Solution**: Always add FEN string handlers in `api/routes.py`
```python
# api/routes.py - Add to parse_fen_string function
elif fen_string == "your_new_position":
    # Create test position
    test_state = AzulState(2)
    # Set up position-specific state
    return test_state
```

**Best Practice**: 
- Add FEN handlers immediately when creating new test positions
- Test API endpoints with new FEN strings before frontend integration
- Update error messages to include new FEN strings

### **2. Standard FEN Validation**

**Problem**: Invalid FEN format causing parsing errors
```python
# ERROR: Invalid FEN format: malformed_fen_string
```

**Solution**: Use the FEN validation endpoint before processing
```python
# Validate FEN before use
response = requests.post('/api/v1/validate-fen', json={'fen_string': fen})
if response.json()['valid']:
    # Process valid FEN
    game_state = parse_fen_string(fen)
else:
    # Handle invalid FEN
    print(f"Invalid FEN: {response.json()['error']}")
```

**Best Practice**:
- Always validate FEN strings before processing
- Use the standard FEN format for new implementations
- Provide clear error messages for invalid FEN strings

### **3. TileDisplay Count Method Issues**

**Problem**: `'TileDisplay' object has no attribute 'count'`
```python
# INCORRECT
total_available += factory.count(color)
total_available += state.center_pool.count(color)
```

**Solution**: Use dictionary access pattern
```python
# CORRECT
if color in factory.tiles:
    total_available += factory.tiles[color]
if color in state.centre_pool.tiles:
    total_available += state.centre_pool.tiles[color]
```

**Best Practice**: 
- Always check if color exists in tiles dictionary before accessing
- Use `centre_pool` (not `center_pool`) for center pool access
- Follow the pattern established in `azul_scoring_optimization.py`

### **4. AgentState Attribute Issues**

**Problem**: `'AgentState' object has no attribute 'pattern_lines'`
```python
# INCORRECT
if len(opponent_state.pattern_lines[pattern_line]) > 0:
    color_in_line = opponent_state.pattern_lines[pattern_line][0]
```

**Solution**: Use correct attribute names
```python
# CORRECT
if opponent_state.lines_number[pattern_line] > 0:
    color_in_line = opponent_state.lines_tile[pattern_line]
```

**Best Practice**:
- Use `lines_number` for tile count in pattern lines
- Use `lines_tile` for color in pattern lines
- Reference existing working code in `azul_scoring_optimization.py`

### **5. Frontend Module Loading Issues**

**Problem**: New test positions not appearing in position library

**Solution**: Update module loading in `ui/main.js`
```javascript
// ui/main.js
const modules = [
    'components/positions/blocking-test-positions.js',
    'components/positions/scoring-optimization-test-positions.js',
    'components/positions/floor-line-test-positions.js',  // Add new module
    // ... other modules
];
```

**Best Practice**:
- Add new position modules to the modules array
- Update `PositionLibrary.js` to recognize new modules
- Use window-based pattern for test position files

### **5. React Key Duplication Issues**

**Problem**: React warnings about duplicate keys in position library

**Solution**: Remove duplicate entries from availableTags array
```javascript
// ui/components/PositionLibrary.js
const availableTags = [
    "opening", "midgame", "endgame", "blocking", "scoring", "floor-line",
    // Remove duplicates like "blocking" and "floor-line" if already present
];
```

## 🚀 Performance Tips

1. **Use Caching**: The API automatically caches analysis results
2. **Batch Operations**: Use bulk endpoints for multiple operations
3. **Connection Pooling**: Reuse HTTP connections for multiple requests
4. **Compression**: Enable gzip compression for large responses
5. **Rate Limiting**: Respect rate limits to avoid throttling

## 🔍 Debugging

### Enable Debug Mode
```bash
python main.py serve --debug
```

### Check Logs
The API provides detailed logging in debug mode:
- Request/response logging
- Database query logging
- Performance metrics
- Error stack traces

### API Information
```bash
curl http://localhost:8000/api
```

**Response:**
```json
{
  "name": "Azul Solver & Analysis Toolkit API",
  "version": "0.1.0",
  "endpoints": {
    "auth": "/api/v1/auth",
    "analysis": "/api/v1/analyze", 
    "hint": "/api/v1/hint",
    "health": "/api/v1/health",
    "stats": "/api/v1/stats",
    "positions": "/api/v1/positions",
    "analyses": "/api/v1/analyses"
  }
}
```

---

**Next Steps**: Ready for Web UI development with this robust API foundation! 🎉 