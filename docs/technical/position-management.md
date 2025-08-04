# Position Management System

## Overview

The position management system provides a scalable way to add and manage test positions for the Azul analysis tool. Instead of hardcoding positions in the backend, positions are stored in a shared JSON database that both frontend and backend can access.

## Architecture

### Components

1. **`data/positions.json`** - Shared position database
2. **`api/utils/position_loader.py`** - Backend position loader
3. **`tools/position_manager.py`** - Management tool for adding positions
4. **`api/utils/state_parser.py`** - Updated to use dynamic position loading

### Benefits

- ✅ **Scalable**: Add new positions without code changes
- ✅ **Shared**: Frontend and backend use same position definitions
- ✅ **Organized**: Positions categorized by type and difficulty
- ✅ **Maintainable**: Easy to add, remove, or modify positions
- ✅ **Versioned**: Position database can be version controlled

## Usage

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

## Position Structure

Each position in the database has this structure:

```json
{
  "position_name": {
    "description": "Human-readable description",
    "category": "blocking|scoring-optimization|floor-line|strategic",
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

## Color Mapping

- `0` = Blue
- `1` = Yellow  
- `2` = Red
- `3` = Black
- `4` = White

## Examples

### Simple Blocking Position

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

### Scoring Optimization Position

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

## Migration from Hardcoded Positions

The system automatically migrates from hardcoded positions to the database:

1. **Fallback positions** are provided for basic functionality
2. **Database positions** take precedence over hardcoded ones
3. **Unknown positions** fall back to initial state

## Adding Positions for Testing

### For Pattern Analysis Testing

```bash
python tools/position_manager.py add
# Name: pattern_test_1
# Category: blocking
# Difficulty: beginner
# Tags: blocking, pattern-analysis, testing
```

### For Scoring Optimization Testing

```bash
python tools/position_manager.py add
# Name: scoring_test_1  
# Category: scoring-optimization
# Difficulty: intermediate
# Tags: scoring-optimization, wall-bonus, testing
```

### For Floor Line Testing

```bash
python tools/position_manager.py add
# Name: floor_line_test_1
# Category: floor-line
# Difficulty: advanced
# Tags: floor-line, penalty, testing
```

## Best Practices

1. **Use descriptive names**: `simple_blue_blocking` not `test1`
2. **Add proper tags**: Helps with filtering and organization
3. **Test positions**: Verify they work with all analysis tools
4. **Document setup**: Include comments explaining the position's purpose
5. **Version control**: Commit position database changes

## Troubleshooting

### Position Not Found

If a position isn't loading:

1. Check the position name in `data/positions.json`
2. Verify the setup structure is correct
3. Restart the server after adding new positions
4. Check console logs for loading errors

### API Errors

If APIs return errors for positions:

1. Verify the position exists in the database
2. Check that the setup creates a valid game state
3. Test with the position manager tool
4. Check server logs for detailed error messages 