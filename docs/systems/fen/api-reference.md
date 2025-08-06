# 🔌 FEN API Reference

> **Complete API reference for the Azul FEN system**

## 🎯 **Overview**

The FEN API provides endpoints for validating, loading, and manipulating FEN strings. This reference covers all FEN-related API operations.

## 📋 **Endpoints**

### **FEN Validation**

#### **POST /api/v1/validate-fen**
Validates a FEN string and returns detailed information about its format and content.

**Request:**
```json
{
  "fen_string": "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
}
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

**Error Response:**
```json
{
  "valid": false,
  "error": "Invalid FEN format: expected 11 components, got 8",
  "format": "unknown"
}
```

### **Game State Loading**

#### **POST /api/v1/game_state**
Loads a game state from a FEN string and returns the complete game state.

**Request:**
```json
{
  "fen_string": "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
}
```

**Response:**
```json
{
  "success": true,
  "game_state": {
    "factories": [
      ["B", "Y", "R", "K"],
      ["W", "B", "Y", "R"],
      ["K", "W", "B", "Y"],
      ["R", "K", "W", "B"],
      ["Y", "R", "K", "W"]
    ],
    "center": ["B", "Y", "R", "K", "W"],
    "players": [
      {
        "wall": [[null, null, null, null, null], ...],
        "pattern_lines": [[], [], [], [], []],
        "floor": [],
        "score": 0
      },
      {
        "wall": [[null, null, null, null, null], ...],
        "pattern_lines": [[], [], [], [], []],
        "floor": [],
        "score": 0
      }
    ],
    "fen_string": "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Invalid FEN string: malformed format"
}
```

## 🔧 **Usage Examples**

### **Python Requests**

#### **Validate FEN String**
```python
import requests

def validate_fen(fen_string):
    response = requests.post(
        'http://localhost:8000/api/v1/validate-fen',
        json={'fen_string': fen_string}
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['valid'], result.get('details', {})
    else:
        return False, {'error': f'API error: {response.status_code}'}

# Usage
is_valid, details = validate_fen("BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0")
print(f"Valid: {is_valid}")
print(f"Details: {details}")
```

#### **Load Game State**
```python
import requests

def load_game_state(fen_string):
    response = requests.post(
        'http://localhost:8000/api/v1/game_state',
        json={'fen_string': fen_string}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            return result['game_state']
        else:
            return None, result.get('error', 'Unknown error')
    else:
        return None, f'API error: {response.status_code}'

# Usage
game_state, error = load_game_state("BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0")
if game_state:
    print(f"Loaded game with {len(game_state['players'])} players")
else:
    print(f"Error: {error}")
```

### **JavaScript Fetch**

#### **Validate FEN String**
```javascript
async function validateFEN(fenString) {
    try {
        const response = await fetch('/api/v1/validate-fen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fen_string: fenString })
        });
        
        const result = await response.json();
        return {
            valid: result.valid,
            details: result.details || {},
            error: result.error || null
        };
    } catch (error) {
        return {
            valid: false,
            details: {},
            error: `Network error: ${error.message}`
        };
    }
}

// Usage
const validation = await validateFEN("BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0");
console.log(`Valid: ${validation.valid}`);
console.log(`Details:`, validation.details);
```

#### **Load Game State**
```javascript
async function loadGameState(fenString) {
    try {
        const response = await fetch('/api/v1/game_state', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fen_string: fenString })
        });
        
        const result = await response.json();
        if (result.success) {
            return { gameState: result.game_state, error: null };
        } else {
            return { gameState: null, error: result.error };
        }
    } catch (error) {
        return { gameState: null, error: `Network error: ${error.message}` };
    }
}

// Usage
const { gameState, error } = await loadGameState("BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0");
if (gameState) {
    console.log(`Loaded game with ${gameState.players.length} players`);
} else {
    console.log(`Error: ${error}`);
}
```

### **cURL Examples**

#### **Validate FEN**
```bash
curl -X POST http://localhost:8000/api/v1/validate-fen \
  -H "Content-Type: application/json" \
  -d '{
    "fen_string": "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
  }'
```

#### **Load Game State**
```bash
curl -X POST http://localhost:8000/api/v1/game_state \
  -H "Content-Type: application/json" \
  -d '{
    "fen_string": "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
  }'
```

## ⚠️ **Error Handling**

### **Common Error Responses**

#### **Invalid FEN Format**
```json
{
  "valid": false,
  "error": "Invalid FEN format: expected 11 components, got 8",
  "format": "unknown"
}
```

#### **Invalid Tile Colors**
```json
{
  "valid": false,
  "error": "Invalid tile color: X (valid colors: B, Y, R, K, W, -)",
  "format": "unknown"
}
```

#### **API Server Error**
```json
{
  "success": false,
  "error": "Internal server error: FEN parsing failed"
}
```

### **HTTP Status Codes**

| Code | Description |
|------|-------------|
| **200** | Success - Valid FEN or game state loaded |
| **400** | Bad Request - Invalid FEN format |
| **500** | Internal Server Error - Server processing error |

## 🔍 **FEN Format Validation**

### **Validation Rules**

The API validates FEN strings according to these rules:

1. **Structure**: Must have exactly 11 components separated by `/`
2. **Factories**: Must have exactly 5 factories, each with exactly 4 tiles
3. **Center**: Must be valid tiles or `-`
4. **Walls**: Must be 5x5 grids with valid tiles or `-`
5. **Pattern Lines**: Must be 5 lines with valid tiles or `-`
6. **Floor Lines**: Must be valid tiles or `-`
7. **Scores**: Must be comma-separated integers
8. **Round**: Must be a positive integer (1-10)
9. **Current Player**: Must be 0 or 1

### **Valid Tile Colors**

| Color | Code | Description |
|-------|------|-------------|
| **B** | Blue | Blue tiles |
| **Y** | Yellow | Yellow tiles |
| **R** | Red | Red tiles |
| **K** | Black | Black tiles |
| **W** | White | White tiles |
| **-** | Empty | Empty space |

## 🎯 **Integration Examples**

### **React Component Integration**
```jsx
import React, { useState } from 'react';

function FENValidator() {
    const [fenInput, setFenInput] = useState('');
    const [validation, setValidation] = useState(null);
    const [loading, setLoading] = useState(false);

    const validateFEN = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/validate-fen', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fen_string: fenInput })
            });
            const result = await response.json();
            setValidation(result);
        } catch (error) {
            setValidation({ valid: false, error: error.message });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <textarea
                value={fenInput}
                onChange={(e) => setFenInput(e.target.value)}
                placeholder="Enter FEN string..."
                rows={4}
            />
            <button onClick={validateFEN} disabled={loading}>
                {loading ? 'Validating...' : 'Validate FEN'}
            </button>
            {validation && (
                <div>
                    <p>Valid: {validation.valid ? '✅' : '❌'}</p>
                    {validation.error && <p>Error: {validation.error}</p>}
                    {validation.details && (
                        <pre>{JSON.stringify(validation.details, null, 2)}</pre>
                    )}
                </div>
            )}
        </div>
    );
}
```

### **Python Integration**
```python
class FENClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def validate_fen(self, fen_string):
        """Validate a FEN string via API"""
        response = requests.post(
            f"{self.base_url}/api/v1/validate-fen",
            json={'fen_string': fen_string}
        )
        return response.json()
    
    def load_game_state(self, fen_string):
        """Load a game state from FEN via API"""
        response = requests.post(
            f"{self.base_url}/api/v1/game_state",
            json={'fen_string': fen_string}
        )
        return response.json()

# Usage
client = FENClient()
validation = client.validate_fen("BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0")
print(f"Valid: {validation['valid']}")
```

## 📊 **Performance Considerations**

### **Response Times**
- **Validation**: < 10ms for standard FEN strings
- **Game State Loading**: < 50ms for complete game states
- **Error Handling**: < 5ms for invalid FEN detection

### **Rate Limiting**
- **Default**: 100 requests per minute per IP
- **Authentication**: Higher limits for authenticated users
- **Bulk Operations**: Contact API for bulk validation needs

## 🔄 **Versioning**

### **Current Version**
- **API Version**: v1.0
- **FEN Format**: Standard format (11 components)
- **Backward Compatibility**: Full support for legacy FEN formats

### **Future Versions**
- **v1.1**: Planned FEN compression support
- **v1.2**: Planned FEN versioning support
- **v2.0**: Planned major format changes (with migration tools)

---

**Last Updated**: January 2025  
**API Version**: v1.0  
**Status**: ✅ **Production Ready**
