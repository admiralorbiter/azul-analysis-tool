# 🔧 FEN Troubleshooting Guide

> **Solutions to common FEN system issues and problems**

## 🎯 **Common Issues**

### **1. Invalid FEN Format**

#### **Problem**
```
ERROR: Invalid FEN format: expected 11 components, got 8
```

#### **Causes**
- Missing components in FEN string
- Incorrect separator usage
- Malformed FEN structure

#### **Solutions**

**Check FEN Structure:**
```python
# Verify FEN has all 11 components
fen_parts = fen_string.split('/')
if len(fen_parts) != 11:
    print(f"Expected 11 parts, got {len(fen_parts)}")
    print("Missing components:", 11 - len(fen_parts))
```

**Correct FEN Format:**
```
factories/center/player1_wall/player1_pattern/player1_floor/player2_wall/player2_pattern/player2_floor/scores/round/current_player
```

**Example Valid FEN:**
```
BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/0,0/1/0
```

### **2. Invalid Tile Colors**

#### **Problem**
```
ERROR: Invalid tile color: X (valid colors: B, Y, R, K, W, -)
```

#### **Causes**
- Using invalid color codes
- Case sensitivity issues
- Special characters in tile data

#### **Solutions**

**Valid Color Codes:**
| Color | Code | Description |
|-------|------|-------------|
| **B** | Blue | Blue tiles |
| **Y** | Yellow | Yellow tiles |
| **R** | Red | Red tiles |
| **K** | Black | Black tiles |
| **W** | White | White tiles |
| **-** | Empty | Empty space |

**Validation Function:**
```python
def validate_tile_colors(fen_string):
    valid_colors = {'B', 'Y', 'R', 'K', 'W', '-'}
    for char in fen_string:
        if char.isalpha() and char not in valid_colors:
            return False, f"Invalid color: {char}"
    return True, "Valid colors"
```

### **3. Incorrect Factory Count**

#### **Problem**
```
ERROR: Factory 0 has 3 tiles, expected 4
```

#### **Causes**
- Wrong number of factories
- Incorrect tiles per factory
- Missing or extra tiles

#### **Solutions**

**Factory Requirements:**
- **Number of Factories**: Exactly 5
- **Tiles per Factory**: Exactly 4 tiles each
- **Total Tiles**: 20 tiles across all factories

**Validation Function:**
```python
def validate_factories(fen_string):
    parts = fen_string.split('/')
    factories = parts[0].split('|')
    
    if len(factories) != 5:
        return False, f"Expected 5 factories, got {len(factories)}"
    
    for i, factory in enumerate(factories):
        if len(factory) != 4:
            return False, f"Factory {i} has {len(factory)} tiles, expected 4"
    
    return True, "Valid factories"
```

### **4. Invalid Wall Placement**

#### **Problem**
```
ERROR: Invalid wall placement at row 0, col 0
```

#### **Causes**
- Duplicate tiles in same row/column
- Invalid tile placement rules
- Incorrect wall structure

#### **Solutions**

**Wall Rules:**
- No duplicate tiles in same row
- No duplicate tiles in same column
- 5x5 grid structure
- Valid tile colors only

**Validation Function:**
```python
def validate_wall(wall_string):
    rows = wall_string.split('|')
    if len(rows) != 5:
        return False, "Expected 5 wall rows"
    
    for row in rows:
        if len(row) != 5:
            return False, "Each row must have 5 columns"
    
    # Check for duplicates in rows and columns
    for i, row in enumerate(rows):
        for j, tile in enumerate(row):
            if tile != '-':
                # Check row for duplicates
                if row.count(tile) > 1:
                    return False, f"Duplicate tile {tile} in row {i}"
                
                # Check column for duplicates
                for k in range(5):
                    if k != i and rows[k][j] == tile:
                        return False, f"Duplicate tile {tile} in column {j}"
    
    return True, "Valid wall"
```

### **5. API Connection Issues**

#### **Problem**
```
ERROR: Connection refused: localhost:8000
```

#### **Causes**
- Server not running
- Wrong port number
- Network connectivity issues

#### **Solutions**

**Check Server Status:**
```bash
# Check if server is running
curl http://localhost:8000/health

# Start server if needed
python main.py serve
```

**Verify Port Configuration:**
```python
import requests

def check_server(base_url="http://localhost:8000"):
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.Timeout:
        return False

# Usage
if check_server():
    print("✅ Server is running")
else:
    print("❌ Server is not accessible")
```

### **6. FEN Parsing Errors**

#### **Problem**
```
ERROR: FEN parsing failed: malformed string
```

#### **Causes**
- Corrupted FEN string
- Encoding issues
- Special characters

#### **Solutions**

**Sanitize FEN String:**
```python
def sanitize_fen(fen_string):
    # Remove extra whitespace
    fen = fen_string.strip()
    
    # Replace common encoding issues
    fen = fen.replace('\\', '|')
    fen = fen.replace(' ', '')
    
    # Validate basic structure
    if fen.count('/') != 10:
        return None, "Invalid FEN structure"
    
    return fen, None

# Usage
clean_fen, error = sanitize_fen(raw_fen)
if clean_fen:
    # Use clean_fen
    pass
else:
    print(f"Error: {error}")
```

## 🔍 **Debugging Tools**

### **FEN Structure Analyzer**
```python
def analyze_fen_structure(fen_string):
    """Analyze FEN string structure for debugging"""
    
    parts = fen_string.split('/')
    
    analysis = {
        'total_parts': len(parts),
        'expected_parts': 11,
        'valid_structure': len(parts) == 11,
        'parts': {}
    }
    
    if len(parts) >= 1:
        factories = parts[0].split('|')
        analysis['parts']['factories'] = {
            'count': len(factories),
            'expected': 5,
            'valid': len(factories) == 5,
            'tiles_per_factory': [len(f) for f in factories]
        }
    
    if len(parts) >= 2:
        analysis['parts']['center'] = {
            'tiles': len(parts[1]) if parts[1] != '-' else 0,
            'content': parts[1]
        }
    
    return analysis

# Usage
analysis = analyze_fen_structure(fen_string)
print("FEN Analysis:")
for key, value in analysis.items():
    print(f"  {key}: {value}")
```

### **FEN Validation Tool**
```python
def comprehensive_fen_validation(fen_string):
    """Comprehensive FEN validation with detailed error reporting"""
    
    errors = []
    warnings = []
    
    # Check structure
    parts = fen_string.split('/')
    if len(parts) != 11:
        errors.append(f"Expected 11 parts, got {len(parts)}")
    
    # Check factories
    if len(parts) >= 1:
        factories = parts[0].split('|')
        if len(factories) != 5:
            errors.append(f"Expected 5 factories, got {len(factories)}")
        else:
            for i, factory in enumerate(factories):
                if len(factory) != 4:
                    errors.append(f"Factory {i} has {len(factory)} tiles, expected 4")
    
    # Check tile colors
    valid_colors = {'B', 'Y', 'R', 'K', 'W', '-'}
    for char in fen_string:
        if char.isalpha() and char not in valid_colors:
            errors.append(f"Invalid tile color: {char}")
            break
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

# Usage
result = comprehensive_fen_validation(fen_string)
if result['valid']:
    print("✅ FEN is valid")
else:
    print("❌ FEN has errors:")
    for error in result['errors']:
        print(f"  - {error}")
```

## 🎯 **Best Practices**

### **1. Always Validate Before Use**
```python
# Validate FEN before processing
if not AzulState.validate_fen(fen_string):
    print("Invalid FEN, skipping processing")
    return
```

### **2. Handle Errors Gracefully**
```python
try:
    state = AzulState.from_fen(fen_string)
except ValueError as e:
    print(f"FEN parsing error: {e}")
    # Provide fallback or user-friendly error
```

### **3. Use Standard Format**
```python
# Prefer standard FEN format
fen = state.to_fen()  # Standard format
```

### **4. Test Round-trip Conversion**
```python
# Verify FEN integrity
original_fen = state.to_fen()
parsed_state = AzulState.from_fen(original_fen)
round_trip_fen = parsed_state.to_fen()
assert original_fen == round_trip_fen
```

## 📞 **Getting Help**

### **When to Seek Help**
- FEN validation errors persist after troubleshooting
- API endpoints return unexpected errors
- Performance issues with large FEN strings
- Integration problems with other systems

### **Information to Provide**
- Complete FEN string (if not sensitive)
- Error messages and stack traces
- Steps to reproduce the issue
- Environment details (Python version, OS, etc.)

### **Resources**
- **[FEN Specification](specification.md)** - Complete format specification
- **[Usage Examples](usage-examples.md)** - Practical examples
- **[API Reference](api-reference.md)** - API documentation

---

**Last Updated**: January 2025  
**Status**: ✅ **Complete** - Comprehensive troubleshooting guide
