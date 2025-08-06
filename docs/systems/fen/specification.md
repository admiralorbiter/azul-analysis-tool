# 📋 FEN Format Specification

> **Complete specification for the Azul FEN (Forsyth-Edwards Notation) format**

## 🎯 Overview

The Azul FEN system provides a standardized way to represent complete game states in a compact, human-readable format. This specification defines the format structure, validation rules, and usage guidelines.

## 📐 Standard FEN Format

### **Format Structure**
```
factories/center/player1_wall/player1_pattern/player1_floor/player2_wall/player2_pattern/player2_floor/scores/round/current_player
```

### **Component Breakdown**

| Component | Description | Format | Example |
|-----------|-------------|--------|---------|
| **Factories** | 5 factories, 4 tiles each | `factory1\|factory2\|factory3\|factory4\|factory5` | `BYRK\|WBYR\|KWBY\|RKWB\|YRKW` |
| **Center** | Center pool tiles | `tiles` or `-` | `BYRKW` or `-` |
| **Player1 Wall** | 5x5 wall grid | `row1\|row2\|row3\|row4\|row5` | `-----\|-----\|-----\|-----\|-----` |
| **Player1 Pattern** | 5 pattern lines | `line1\|line2\|line3\|line4\|line5` | `-----\|-----\|-----\|-----\|-----` |
| **Player1 Floor** | Floor line tiles | `tiles` or `-` | `BYR` or `-` |
| **Player2 Wall** | 5x5 wall grid | `row1\|row2\|row3\|row4\|row5` | `-----\|-----\|-----\|-----\|-----` |
| **Player2 Pattern** | 5 pattern lines | `line1\|line2\|line3\|line4\|line5` | `-----\|-----\|-----\|-----\|-----` |
| **Player2 Floor** | Floor line tiles | `tiles` or `-` | `BYR` or `-` |
| **Scores** | Comma-separated scores | `score1,score2` | `0,0` |
| **Round** | Current round number | `number` | `1` |
| **Current Player** | Active player index | `index` | `0` |

### **Tile Color Codes**

| Color | Code | Description |
|-------|------|-------------|
| **B** | Blue | Blue tiles |
| **Y** | Yellow | Yellow tiles |
| **R** | Red | Red tiles |
| **K** | Black | Black tiles |
| **W** | White | White tiles |
| **-** | Empty | Empty space |

## 🔍 FEN Types

### **1. Standard FEN (Primary)**
Human-readable format for normal use:
```
BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0
```

### **2. Hash-based FEN**
For unique state identification:
```
state_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### **3. Base64 FEN**
For encoded game data:
```
base64_SGVsbG8gV29ybGQ=
```

### **4. Special Positions**
Pre-defined positions for testing:
- `"start"` - Initial game position
- `"midgame"` - Mid-game position
- `"endgame"` - End-game position
- `"initial"` - Persistent initial position

## ✅ Validation Rules

### **Format Validation**
1. **Structure**: Must have exactly 11 components separated by `/`
2. **Factories**: Must have exactly 5 factories, each with exactly 4 tiles
3. **Center**: Must be valid tiles or `-`
4. **Walls**: Must be 5x5 grids with valid tiles or `-`
5. **Pattern Lines**: Must be 5 lines with valid tiles or `-`
6. **Floor Lines**: Must be valid tiles or `-`
7. **Scores**: Must be comma-separated integers
8. **Round**: Must be a positive integer (1-10)
9. **Current Player**: Must be 0 or 1

### **Content Validation**
1. **Tile Count**: Total tiles must not exceed game limits
2. **Color Distribution**: Tile colors must be valid
3. **Wall Placement**: Wall tiles must follow Azul rules
4. **Pattern Line Rules**: Pattern lines must follow Azul rules
5. **Floor Line Rules**: Floor line must follow Azul rules

## 🚀 Usage Examples

### **Basic FEN Generation**
```python
from core.azul_model import AzulState

# Create a new game state
state = AzulState(2)

# Generate FEN string
fen_string = state.to_fen()
print(fen_string)
# Output: BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0
```

### **FEN Validation**
```python
# Validate FEN string
is_valid = AzulState.validate_fen(fen_string)
if is_valid:
    print("Valid FEN string")
else:
    print("Invalid FEN string")
```

### **FEN Parsing**
```python
# Parse FEN string back to game state
state = AzulState.from_fen(fen_string)
print(f"Game state loaded with {len(state.agents)} players")
```

### **Round-trip Conversion**
```python
# Test round-trip conversion
original_state = AzulState(2)
fen = original_state.to_fen()
parsed_state = AzulState.from_fen(fen)
round_trip_fen = parsed_state.to_fen()

# Verify round-trip works
assert fen == round_trip_fen
print("Round-trip conversion successful")
```

## 🔧 API Integration

### **FEN Validation Endpoint**
```bash
curl -X POST http://localhost:8000/api/v1/validate-fen \
  -H "Content-Type: application/json" \
  -d '{"fen_string": "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"}'
```

### **Game State Loading**
```bash
curl -X POST http://localhost:8000/api/v1/game_state \
  -H "Content-Type: application/json" \
  -d '{"fen_string": "BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0"}'
```

## 🎨 UI Integration

### **FEN Display Component**
```jsx
<FENDisplay 
  fenString={gameState.fen_string}
  onCopy={() => navigator.clipboard.writeText(gameState.fen_string)}
/>
```

### **FEN Input Component**
```jsx
<FENInput 
  onLoad={(fen) => loadGameState(fen)}
  examples={exampleFENs}
/>
```

### **FEN Manager Component**
```jsx
<FENManager 
  fenString={gameState.fen_string}
  onLoad={(fen) => loadGameState(fen)}
  onCopy={() => navigator.clipboard.writeText(gameState.fen_string)}
/>
```

## ⚠️ Common Issues

### **1. Invalid FEN Format**
**Problem**: Malformed FEN string
```
ERROR: Invalid FEN format: BYRK|WBYR|KWBY|RKWB|YRKW
```

**Solution**: Ensure FEN has all 11 required components
```
BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0
```

### **2. Invalid Tile Colors**
**Problem**: Unknown tile color code
```
ERROR: Invalid tile color: X
```

**Solution**: Use only valid color codes (B, Y, R, K, W, -)

### **3. Incorrect Factory Count**
**Problem**: Wrong number of factories or tiles
```
ERROR: Factory 0 has 3 tiles, expected 4
```

**Solution**: Ensure exactly 5 factories with exactly 4 tiles each

### **4. Invalid Wall Placement**
**Problem**: Wall tiles don't follow Azul rules
```
ERROR: Invalid wall placement at row 0, col 0
```

**Solution**: Follow Azul wall placement rules (no duplicates in rows/columns)

## 📚 Best Practices

### **1. Always Validate**
```python
# Validate FEN before use
if not AzulState.validate_fen(fen_string):
    raise ValueError("Invalid FEN string")
```

### **2. Use Standard Format**
```python
# Prefer standard FEN for new implementations
fen = state.to_fen()  # Standard format
```

### **3. Handle Errors Gracefully**
```python
try:
    state = AzulState.from_fen(fen_string)
except ValueError as e:
    print(f"FEN parsing error: {e}")
```

### **4. Test Round-trip Conversion**
```python
# Verify FEN integrity
original_fen = state.to_fen()
parsed_state = AzulState.from_fen(original_fen)
round_trip_fen = parsed_state.to_fen()
assert original_fen == round_trip_fen
```

## 🔄 Version History

### **v1.0 (Current)**
- Standard FEN format implementation
- Comprehensive validation rules
- Round-trip conversion support
- API integration
- UI components

### **Future Enhancements**
- FEN compression for long strings
- FEN versioning for format changes
- Advanced validation rules
- Performance optimizations

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Status**: ✅ Complete
