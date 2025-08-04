# Center Pool Testing Guide

This document describes the comprehensive test suite we've created to prevent center pool functionality regressions and similar issues in the future.

## Overview

The center pool functionality was a critical feature that had several issues:
1. **Center pool not visible in UI** - Fixed by creating `CenterPool.js` component
2. **Tiles not moving to center pool** - Fixed by correcting backend logic in `azul_model.py`
3. **First player marker not showing** - Fixed by adding `first_player_taken` to state conversion
4. **Drag-and-drop from center not working** - Fixed by updating `useAnalysis.js` logic
5. **UI not updating after moves** - Fixed by correcting response field handling

## Test Suites Created

### 1. `tests/test_center_pool_regression.py`
**Purpose**: Core regression tests to prevent the specific issues we fixed from recurring.

**Key Tests**:
- `test_center_pool_field_exists()` - Ensures `center` and `first_player_taken` fields exist
- `test_center_pool_initial_state()` - Verifies initial state is correct
- `test_frontend_state_update_logic()` - Tests the fix for `new_game_state` field handling
- `test_center_pool_drag_data_structure()` - Validates drag data structure
- `test_first_player_marker_display_logic()` - Tests first player marker logic

**Usage**:
```bash
# Run all center pool regression tests
python -m pytest tests/test_center_pool_regression.py -v

# Run specific test
python -m pytest tests/test_center_pool_regression.py::TestCenterPoolRegression::test_center_pool_field_exists -v
```

### 2. `tests/test_frontend_drag_drop_integration.py`
**Purpose**: Tests frontend drag-and-drop functionality and state updates.

**Key Tests**:
- `test_backend_response_structure()` - Validates API response structure
- `test_frontend_state_update_consistency()` - Ensures state consistency
- `test_center_pool_drag_data_structure()` - Tests center pool drag data
- `test_move_execution_response_handling()` - Tests move execution response handling
- `test_drag_and_drop_validation()` - Tests drag-and-drop validation logic

**Usage**:
```bash
# Run all frontend integration tests
python -m pytest tests/test_frontend_drag_drop_integration.py -v
```

### 3. `tests/test_backend_center_pool_logic.py`
**Purpose**: Tests core backend game mechanics for center pool functionality.

**Key Tests**:
- `test_initial_center_pool_state()` - Tests initial state
- `test_factory_move_puts_remaining_tiles_in_center()` - Tests factory move logic
- `test_taking_from_center_sets_first_player_marker()` - Tests first player marker logic
- `test_center_pool_tile_removal()` - Tests tile removal from center
- `test_center_pool_becomes_empty()` - Tests center pool emptying

**Usage**:
```bash
# Run all backend logic tests
python -m pytest tests/test_backend_center_pool_logic.py -v
```

### 4. `tests/test_center_pool_integration.py`
**Purpose**: End-to-end integration tests for center pool functionality.

**Key Tests**:
- `test_factory_move_puts_tiles_in_center()` - Tests factory to center flow
- `test_center_pool_drag_and_drop()` - Tests center to pattern line flow
- `test_center_pool_first_player_marker()` - Tests first player marker flow
- `test_multiple_center_pool_moves()` - Tests multiple center pool operations

**Usage**:
```bash
# Run all integration tests
python -m pytest tests/test_center_pool_integration.py -v
```

## Running the Complete Test Suite

To run all center pool related tests:

```bash
# Run all center pool tests
python -m pytest tests/test_center_pool_*.py -v

# Run with coverage
python -m pytest tests/test_center_pool_*.py --cov=core --cov=api -v
```

## What Each Test Prevents

### Backend Logic Tests
- **Prevents**: Incorrect tile movement to center pool
- **Prevents**: Wrong first player marker state
- **Prevents**: Center pool state inconsistencies

### Frontend Integration Tests
- **Prevents**: UI not updating after moves
- **Prevents**: Incorrect drag-and-drop behavior
- **Prevents**: Missing center pool component
- **Prevents**: Wrong response field handling

### Regression Tests
- **Prevents**: Missing required fields in game state
- **Prevents**: Incorrect data types
- **Prevents**: Broken drag data structures
- **Prevents**: Missing first player marker display

## Key Fixes That Are Tested

### 1. Backend Fix: `core/azul_model.py`
```python
def RemoveTiles(self, number, tile_type):
    """Remove tiles from the display (alias for ReactionTiles for clarity)."""
    self.ReactionTiles(number, tile_type)
```

**Test**: `test_backend_center_pool_logic.py::test_center_pool_tile_removal()`

### 2. Frontend Fix: `ui/components/hooks/useAnalysis.js`
```javascript
const newGameState = result.new_game_state || result.game_state || await getGameState(result.new_fen);
```

**Test**: `test_center_pool_regression.py::test_frontend_state_update_logic()`

### 3. State Conversion Fix: `api/utils/state_converter.py`
```python
'first_player_taken': azul_state.first_agent_taken
```

**Test**: `test_center_pool_regression.py::test_center_pool_field_exists()`

### 4. Component Fix: `ui/components/CenterPool.js`
```javascript
gameState.first_player_taken && 
React.createElement('div', {
    className: 'mt-2 text-xs text-blue-600 font-medium'
}, '⭐ First player marker taken')
```

**Test**: `test_center_pool_regression.py::test_first_player_marker_display_logic()`

## Adding New Tests

When adding new center pool functionality, follow these patterns:

### 1. Backend Logic Tests
```python
def test_new_center_pool_feature(self):
    """Test new center pool feature."""
    # Setup
    initial_state = self.get_game_state()
    
    # Action
    result = self.execute_move("initial", move)
    
    # Assert
    assert result["success"] is True
    assert "expected_field" in result["new_game_state"]
```

### 2. Frontend Integration Tests
```python
def test_new_frontend_feature(self):
    """Test new frontend feature."""
    # Mock the expected behavior
    expected_behavior = {
        "field": "value",
        "another_field": True
    }
    
    # Test the logic
    result = simulate_frontend_logic(expected_behavior)
    
    # Assert
    assert result["field"] == "value"
```

### 3. Regression Tests
```python
def test_new_regression_prevention(self):
    """Test that prevents new regression."""
    # Test the specific fix
    def simulate_fix(data):
        return data.get("new_field", "default")
    
    # Test cases
    test_cases = [
        ({"new_field": "value"}, "value"),
        ({}, "default"),
    ]
    
    for input_data, expected in test_cases:
        result = simulate_fix(input_data)
        assert result == expected
```

## Continuous Integration

These tests should be run:
1. **Before every commit** - To prevent regressions
2. **In CI/CD pipeline** - To catch issues early
3. **After refactoring** - To ensure functionality is preserved
4. **When adding new features** - To ensure compatibility

## Troubleshooting

### Common Issues

1. **Server not running**: Tests will be skipped if server is not available
2. **API changes**: Update test expectations when API changes
3. **State changes**: Update tests when game state structure changes

### Debugging Failed Tests

1. **Check server status**: Ensure server is running on localhost:8000
2. **Check API responses**: Use browser dev tools or curl to verify API
3. **Check game state**: Verify the current game state structure
4. **Check test data**: Ensure test data matches expected format

## Future Enhancements

1. **Visual regression tests** - Screenshot comparison for UI changes
2. **Performance tests** - Ensure center pool operations remain fast
3. **Stress tests** - Test with many tiles in center pool
4. **Accessibility tests** - Ensure center pool is accessible

## Conclusion

This comprehensive test suite ensures that:
- ✅ Center pool is always visible when it should be
- ✅ Tiles move correctly to and from center pool
- ✅ First player marker appears correctly
- ✅ Drag-and-drop works from center pool
- ✅ UI updates properly after moves
- ✅ Backend and frontend stay in sync

By running these tests regularly, we can prevent the issues we encountered from happening again and ensure the center pool functionality remains robust and reliable. 