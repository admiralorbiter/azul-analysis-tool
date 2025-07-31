# 🌐 Azul Solver REST API Usage Guide

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
- **Authentication**: Session-based authentication with rate limiting
- **Database Integration**: SQLite caching with compression and indexing
- **CORS Support**: Web UI integration ready
- **Health Monitoring**: Built-in health checks and statistics
- **Error Handling**: Comprehensive error responses

## 🔐 Authentication

### Creating a Session
```bash
curl -X POST http://localhost:8000/api/v1/auth/session \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "password": "test"
  }'
```

**Response:**
```json
{
  "session_id": "abc123def456",
  "expires_at": "2024-01-01T12:00:00Z",
  "user": {
    "username": "test",
    "permissions": ["read", "write", "admin"]
  }
}
```

### Using Authentication
```bash
# Include session token in all requests
curl -H "Authorization: Bearer abc123def456" \
  http://localhost:8000/api/v1/health
```

## 🎯 Game Analysis

### Exact Analysis (Alpha-Beta Search)
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
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
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
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
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
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
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

### Search Positions
```bash
# Basic search
curl -X GET "http://localhost:8000/api/v1/positions/search?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"

# Advanced search with filters
curl -X GET "http://localhost:8000/api/v1/positions/search?limit=20&offset=0&player_count=2&game_phase=midgame" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

### Bulk Operations
```bash
# Bulk import
curl -X POST http://localhost:8000/api/v1/positions/bulk \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
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
        "player_count": 3,
        "compressed_state": "..."
      }
    ],
    "overwrite": true
  }'

# Bulk export
curl -X GET "http://localhost:8000/api/v1/positions/bulk?limit=100&offset=0" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"

# Bulk delete
curl -X DELETE http://localhost:8000/api/v1/positions/bulk \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fen_strings": ["position1", "position2"]
  }'
```

## 📊 Analysis Cache

### Get Cached Analysis
```bash
curl -X GET http://localhost:8000/api/v1/analyses/start \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

### Store Analysis Result
```bash
curl -X POST http://localhost:8000/api/v1/analyses/start \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
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
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"

# Get recent analyses
curl -X GET "http://localhost:8000/api/v1/analyses/recent?limit=20&hours=24" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
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
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
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
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

### System Monitoring
```bash
curl http://localhost:8000/api/v1/performance/monitoring \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

## 🔧 Error Handling

### Common Error Responses

**401 Unauthorized:**
```json
{
  "error": "authentication_required",
  "message": "Valid session token required",
  "details": "Include Authorization header with Bearer token"
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
- Allowed origins: `http://localhost:3000`, `http://127.0.0.1:3000`
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type, Authorization

### Static File Serving
The API serves static files from the `ui/` directory:
```
http://localhost:8000/ui/index.html
http://localhost:8000/ui/static/css/style.css
http://localhost:8000/ui/static/js/app.js
```

## 📝 FEN String Format

The API uses a custom FEN-like string format for game positions:

```
<player_count>:<factory_state>:<center_state>:<player_states>
```

**Example:**
```
2:factory_0_blue_2_red_1_yellow_1:center_blue_1_red_1:player_0_pattern_0_blue_1_floor_0_score_0:player_1_pattern_0_red_1_floor_0_score_0
```

**Special Positions:**
- `"start"` - Initial game position
- `"midgame"` - Mid-game position for testing
- `"endgame"` - End-game position for testing

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