# 🎯 FEN Usage Examples

> **Practical examples for using the Azul FEN system**

## 🚀 Quick Start Examples

### **1. Basic FEN Generation**
```python
from core.azul_model import AzulState

# Create a new game
state = AzulState(2)

# Generate FEN string
fen = state.to_fen()
print(f"Generated FEN: {fen}")
```

### **2. FEN Validation**
```python
# Validate a FEN string
fen_string = "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"

if AzulState.validate_fen(fen_string):
    print("✅ Valid FEN string")
else:
    print("❌ Invalid FEN string")
```

### **3. Load Game from FEN**
```python
# Load a game state from FEN
fen_string = "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"

try:
    state = AzulState.from_fen(fen_string)
    print(f"✅ Loaded game with {len(state.agents)} players")
    print(f"Current player: {state.current_player}")
    print(f"Round: {state.round}")
except ValueError as e:
    print(f"❌ Error loading FEN: {e}")
```

## 🎮 Game Analysis Examples

### **4. Analyze Position from FEN**
```python
from analysis_engine.mathematical_optimization.azul_evaluator import AzulEvaluator

# Load position from FEN
fen_string = "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
state = AzulState.from_fen(fen_string)

# Analyze position
evaluator = AzulEvaluator()
evaluation = evaluator.evaluate_position(state, 0)

print(f"Position evaluation: {evaluation}")
```

### **5. Find Best Move from FEN**
```python
from analysis_engine.mathematical_optimization.azul_mcts import AzulMCTS

# Load position from FEN
fen_string = "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
state = AzulState.from_fen(fen_string)

# Find best move
mcts = AzulMCTS()
best_move = mcts.find_best_move(state, 0, time_limit=1.0)

print(f"Best move: {best_move}")
```

## 🌐 API Integration Examples

### **6. Validate FEN via API**
```python
import requests

# Validate FEN string via API
fen_string = "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"

response = requests.post(
    'http://localhost:8000/api/v1/validate-fen',
    json={'fen_string': fen_string}
)

if response.status_code == 200:
    result = response.json()
    if result['valid']:
        print("✅ FEN is valid")
        print(f"Format: {result['format']}")
    else:
        print("❌ FEN is invalid")
else:
    print(f"❌ API error: {response.status_code}")
```

### **7. Load Game State via API**
```python
import requests

# Load game state from FEN via API
fen_string = "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"

response = requests.post(
    'http://localhost:8000/api/v1/game_state',
    json={'fen_string': fen_string}
)

if response.status_code == 200:
    result = response.json()
    game_state = result['game_state']
    print("✅ Game state loaded")
    print(f"Factories: {len(game_state['factories'])}")
    print(f"Players: {len(game_state['players'])}")
else:
    print(f"❌ API error: {response.status_code}")
```

## 🎨 UI Integration Examples

### **8. React Component Usage**
```jsx
import React, { useState } from 'react';

// FEN Display Component
function FENDisplay({ fenString, onCopy }) {
  return (
    <div className="fen-display">
      <h3>Current FEN</h3>
      <div className="fen-string">
        <code>{fenString}</code>
        <button onClick={onCopy}>Copy</button>
      </div>
    </div>
  );
}

// FEN Input Component
function FENInput({ onLoad, examples }) {
  const [fenInput, setFenInput] = useState('');
  const [isValid, setIsValid] = useState(false);

  const validateFEN = async (fen) => {
    try {
      const response = await fetch('/api/v1/validate-fen', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fen_string: fen })
      });
      const result = await response.json();
      return result.valid;
    } catch (error) {
      return false;
    }
  };

  const handleInputChange = async (e) => {
    const fen = e.target.value;
    setFenInput(fen);
    const valid = await validateFEN(fen);
    setIsValid(valid);
  };

  const handleLoad = () => {
    if (isValid) {
      onLoad(fenInput);
    }
  };

  return (
    <div className="fen-input">
      <h3>Load FEN</h3>
      <textarea
        value={fenInput}
        onChange={handleInputChange}
        placeholder="Paste FEN string here..."
        rows={4}
      />
      <div className="validation-status">
        {isValid ? '✅ Valid' : '❌ Invalid'}
      </div>
      <button onClick={handleLoad} disabled={!isValid}>
        Load Game
      </button>
      <div className="examples">
        <h4>Example FENs:</h4>
        {examples.map((example, index) => (
          <button key={index} onClick={() => setFenInput(example.fen)}>
            {example.name}
          </button>
        ))}
      </div>
    </div>
  );
}

// Usage
function GameInterface() {
  const [gameState, setGameState] = useState(null);

  const handleLoadFEN = (fen) => {
    // Load game state from FEN
    fetch('/api/v1/game_state', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fen_string: fen })
    })
    .then(response => response.json())
    .then(result => setGameState(result.game_state));
  };

  const handleCopyFEN = () => {
    if (gameState?.fen_string) {
      navigator.clipboard.writeText(gameState.fen_string);
    }
  };

  return (
    <div>
      <FENDisplay 
        fenString={gameState?.fen_string || ''} 
        onCopy={handleCopyFEN} 
      />
      <FENInput 
        onLoad={handleLoadFEN}
        examples={[
          { name: 'Opening Position', fen: 'BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0' },
          { name: 'Midgame Position', fen: 'BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/B----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/5,3/3/0' }
        ]}
      />
    </div>
  );
}
```

## 📊 Position Library Examples

### **9. Generate FEN from Position Library**
```javascript
// From ui/components/positions/opening-positions.js
const balancedStart = {
  name: "Balanced Start",
  description: "Standard opening with equal distribution of all colors",
  difficulty: "beginner",
  tags: ["opening", "balanced", "standard", "beginner-friendly", "2-player"],
  generate: () => {
    const gameState = {
      factories: createBalancedFactories(),
      center: ['B', 'Y', 'R', 'K', 'W'],
      players: Array(2).fill().map(() => createEmptyPlayer())
    };

    return {
      ...gameState,
      fen_string: generateStandardFEN(gameState)
    };
  }
};

// Generate FEN from position
const position = balancedStart.generate();
console.log(`Position: ${position.name}`);
console.log(`FEN: ${position.fen_string}`);
```

### **10. Load Position Library FEN**
```python
# Load a position from the position library
from ui.components.positions.opening_positions import balancedStart

# Generate position with FEN
position = balancedStart.generate()
fen_string = position['fen_string']

# Load into game state
state = AzulState.from_fen(fen_string)
print(f"Loaded position: {position['name']}")
print(f"FEN: {fen_string}")
```

## 🔄 Round-trip Conversion Examples

### **11. Test FEN Integrity**
```python
def test_fen_round_trip():
    """Test that FEN conversion is lossless"""
    
    # Create original state
    original_state = AzulState(2)
    
    # Convert to FEN
    fen = original_state.to_fen()
    print(f"Original FEN: {fen}")
    
    # Convert back to state
    parsed_state = AzulState.from_fen(fen)
    
    # Convert back to FEN
    round_trip_fen = parsed_state.to_fen()
    print(f"Round-trip FEN: {round_trip_fen}")
    
    # Verify they match
    if fen == round_trip_fen:
        print("✅ Round-trip conversion successful")
        return True
    else:
        print("❌ Round-trip conversion failed")
        return False

# Run test
test_fen_round_trip()
```

### **12. Batch FEN Validation**
```python
def validate_fen_batch(fen_strings):
    """Validate multiple FEN strings"""
    
    results = []
    for i, fen in enumerate(fen_strings):
        try:
            is_valid = AzulState.validate_fen(fen)
            results.append({
                'index': i,
                'fen': fen,
                'valid': is_valid,
                'error': None
            })
        except Exception as e:
            results.append({
                'index': i,
                'fen': fen,
                'valid': False,
                'error': str(e)
            })
    
    return results

# Test multiple FENs
test_fens = [
    "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0",
    "invalid_fen_string",
    "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
]

results = validate_fen_batch(test_fens)
for result in results:
    status = "✅" if result['valid'] else "❌"
    print(f"{status} FEN {result['index']}: {result['valid']}")
    if result['error']:
        print(f"   Error: {result['error']}")
```

## 🎯 Advanced Examples

### **13. Custom FEN Generation**
```python
def create_custom_fen(factories, center, players, scores, round_num, current_player):
    """Create a custom FEN string from components"""
    
    # Format factories
    factory_str = '|'.join([''.join(factory) for factory in factories])
    
    # Format center
    center_str = ''.join(center) if center else '-'
    
    # Format players
    player_strs = []
    for player in players:
        # Wall
        wall = '|'.join([''.join(row) for row in player['wall']])
        # Pattern lines
        pattern = '|'.join([''.join(line) for line in player['pattern_lines']])
        # Floor
        floor = ''.join(player['floor']) if player['floor'] else '-'
        player_strs.append(f"{wall}/{pattern}/{floor}")
    
    # Format scores
    scores_str = ','.join(map(str, scores))
    
    # Combine all components
    fen = f"{factory_str}/{center_str}/{player_strs[0]}/{player_strs[1]}/{scores_str}/{round_num}/{current_player}"
    
    return fen

# Example usage
factories = [
    ['B', 'Y', 'R', 'K'],
    ['W', 'B', 'Y', 'R'],
    ['K', 'W', 'B', 'Y'],
    ['R', 'K', 'W', 'B'],
    ['Y', 'R', 'K', 'W']
]

center = ['B', 'Y', 'R', 'K', 'W']
players = [
    {
        'wall': [['-']*5 for _ in range(5)],
        'pattern_lines': [['-']*i for i in range(1, 6)],
        'floor': []
    },
    {
        'wall': [['-']*5 for _ in range(5)],
        'pattern_lines': [['-']*i for i in range(1, 6)],
        'floor': []
    }
]

scores = [0, 0]
round_num = 1
current_player = 0

custom_fen = create_custom_fen(factories, center, players, scores, round_num, current_player)
print(f"Custom FEN: {custom_fen}")
```

### **14. FEN Analysis**
```python
def analyze_fen_structure(fen_string):
    """Analyze the structure of a FEN string"""
    
    parts = fen_string.split('/')
    
    if len(parts) != 11:
        return {'error': f'Expected 11 parts, got {len(parts)}'}
    
    analysis = {
        'factories': {
            'count': len(parts[0].split('|')),
            'tiles_per_factory': [len(f) for f in parts[0].split('|')]
        },
        'center': {
            'tiles': len(parts[1]) if parts[1] != '-' else 0,
            'content': parts[1]
        },
        'player1': {
            'wall_rows': len(parts[2].split('|')),
            'pattern_lines': len(parts[3].split('|')),
            'floor_tiles': len(parts[4]) if parts[4] != '-' else 0
        },
        'player2': {
            'wall_rows': len(parts[5].split('|')),
            'pattern_lines': len(parts[6].split('|')),
            'floor_tiles': len(parts[7]) if parts[7] != '-' else 0
        },
        'scores': {
            'count': len(parts[8].split(',')),
            'values': [int(s) for s in parts[8].split(',')]
        },
        'round': int(parts[9]),
        'current_player': int(parts[10])
    }
    
    return analysis

# Analyze a FEN string
fen = "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"
analysis = analyze_fen_structure(fen)
print("FEN Analysis:")
for key, value in analysis.items():
    print(f"  {key}: {value}")
```

## 📝 Summary

These examples demonstrate the comprehensive FEN system capabilities:

- **Basic Operations**: Generation, validation, parsing
- **API Integration**: RESTful endpoints for FEN operations
- **UI Components**: React components for FEN display and input
- **Position Library**: Integration with pre-defined positions
- **Advanced Features**: Custom generation, analysis, batch processing

The FEN system provides a robust foundation for game state representation and sharing across the Azul analysis tool ecosystem.

---

**Last Updated**: January 2025  
**Status**: ✅ Complete
