# Position Management Quick Reference

## 🚀 **Quick Commands**

### List All Positions
```bash
python tools/position_manager.py list
```

### Add New Position
```bash
python tools/position_manager.py add
```

### Show Setup Template
```bash
python tools/position_manager.py template
```

## 📋 **Position Categories**

| Category | Purpose | Example Tags |
|----------|---------|--------------|
| **blocking** | Pattern analysis and blocking opportunities | `blocking`, `pattern-analysis`, `testing` |
| **scoring-optimization** | Wall completion and bonus opportunities | `scoring-optimization`, `wall-bonus`, `testing` |
| **floor-line** | Floor line penalty management | `floor-line`, `penalty`, `testing` |
| **strategic** | Strategic timing and trade-offs | `strategic`, `timing`, `trade-offs` |
| **move-quality** | Move efficiency and quality assessment | `move-quality`, `efficiency`, `testing` |

## 🎨 **Color Mapping**

| Number | Color | Description |
|--------|-------|-------------|
| `0` | Blue | Blue tiles |
| `1` | Yellow | Yellow tiles |
| `2` | Red | Red tiles |
| `3` | Black | Black tiles |
| `4` | White | White tiles |

## 📝 **Setup Structure**

```json
{
  "position_name": {
    "description": "Human-readable description",
    "category": "blocking|scoring-optimization|floor-line|strategic|move-quality",
    "difficulty": "beginner|intermediate|advanced",
    "tags": ["tag1", "tag2", "tag3"],
    "setup": {
      "player_0_lines": {
        "line_index": {"color": 0, "count": 1}
      },
      "player_1_lines": {
        "line_index": {"color": 0, "count": 1}
      },
      "player_0_wall": {
        "row,col": 1
      },
      "player_1_wall": {
        "row,col": 1
      },
      "factories": {
        "factory_index": {"color": count}
      },
      "center_pool": {
        "color": count
      }
    }
  }
}
```

## 🧪 **Test Position Examples**

### Simple Blocking Test
```json
{
  "simple_blue_blocking": {
    "description": "Simple blue blocking test position",
    "category": "blocking",
    "difficulty": "beginner",
    "tags": ["blocking", "blue", "simple", "testing"],
    "setup": {
      "player_1_lines": {
        "0": {"color": 0, "count": 1}
      },
      "factories": {
        "0": {"0": 2},
        "1": {"0": 1}
      },
      "center_pool": {"0": 1}
    }
  }
}
```

### Scoring Optimization Test
```json
{
  "high_value_column_completion": {
    "description": "High value column completion test position",
    "category": "scoring-optimization",
    "difficulty": "intermediate",
    "tags": ["scoring-optimization", "column-completion", "wall-bonus"],
    "setup": {
      "player_0_wall": {
        "0,2": 1,
        "1,2": 1,
        "2,2": 1,
        "3,2": 1
      },
      "factories": {
        "0": {"2": 2},
        "1": {"2": 1}
      },
      "center_pool": {"2": 1}
    }
  }
}
```

## 🔧 **Interactive Setup Guide**

When using `python tools/position_manager.py add`:

### Player Pattern Lines
```
Format: line,color,count
Example: 0,0,1 (1 blue tile in line 0)
```

### Wall Tiles
```
Format: row,col
Example: 0,0 (tile at row 0, column 0)
```

### Factory Tiles
```
Format: factory,color,count
Example: 0,0,2 (2 blue tiles in factory 0)
```

### Center Pool Tiles
```
Format: color,count
Example: 0,1 (1 blue tile in center)
```

## 🎯 **Testing Workflow**

1. **Create Test Position**
   ```bash
   python tools/position_manager.py add
   ```

2. **Restart Server**
   ```bash
   python start_server.py
   ```

3. **Load Position in UI**
   - Go to Position Library
   - Select your new position
   - Click "Load Position"

4. **Test Analysis Tools**
   - Pattern Analysis
   - Scoring Optimization
   - Floor Line Patterns
   - Strategic Analysis
   - Move Quality Assessment

## 🐛 **Troubleshooting**

### Position Not Loading
- Check position name in `data/positions.json`
- Verify setup structure is correct
- Restart server after adding positions

### API Errors
- Verify position exists in database
- Check setup creates valid game state
- Test with position manager tool

### Common Issues
- **Invalid JSON**: Check syntax in setup
- **Missing Fields**: Ensure all required fields present
- **Invalid Coordinates**: Row/col must be 0-4
- **Invalid Colors**: Must be 0-4 (Blue=0, Yellow=1, etc.)

## 📚 **Related Documentation**

- [Position Management System](docs/technical/position-management.md)
- [API Documentation](docs/api/)
- [Testing Guide](docs/testing/)
- [UI Testing Checklist](docs/planning/UI_TESTING_WORKFLOW_CHECKLIST.md) 