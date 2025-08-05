# 🏠 Floor Line Management Patterns - Implementation Guide

> **Comprehensive guide for floor line management pattern detection in Azul**

## 📋 Overview

The Floor Line Management Patterns system extends the pattern detection engine to identify strategic opportunities related to floor line usage. This includes risk mitigation, timing optimization, trade-off analysis, and endgame management strategies.

## 🎯 Key Features

### **Risk Mitigation Detection**
- **Critical Risk**: 6+ tiles on floor line (-3 points)
- **High Risk**: 4-5 tiles on floor line (-2 points)  
- **Medium Risk**: 2-3 tiles on floor line (-1 to -2 points)
- **Low Risk**: 1 tile on floor line (-1 point)

### **Timing Optimization Patterns**
- **Early Game**: Strategic floor line usage for future opportunities
- **Mid Game**: Balanced floor line management during scoring phases
- **Endgame**: Aggressive floor line clearing for final scoring

### **Trade-off Analysis**
- **Wall vs Floor**: Evaluating wall completion value against floor penalties
- **Multiplier Setup**: Accepting floor penalties for multiple bonus combinations
- **Blocking Value**: Using floor line strategically to block opponents

### **Endgame Management**
- **Penalty Minimization**: Reducing floor line penalties in final rounds
- **Efficiency Optimization**: Clearing floor line for maximum point efficiency
- **Strategic Placement**: Using floor line for optimal tile placement

## 🏗️ Technical Implementation

### **Core Components**

#### **Backend Implementation**
```python
# core/azul_floor_line_patterns.py
class AzulFloorLinePatternDetector:
    def detect_floor_line_patterns(self, state: AzulState, player_id: int) -> FloorLinePatternDetection:
        # Main detection method
        pass
    
    def _detect_risk_mitigation_opportunities(self, state: AzulState, player_id: int) -> List[FloorLineOpportunity]:
        # Risk mitigation detection
        pass
    
    def _detect_timing_optimization_opportunities(self, state: AzulState, player_id: int) -> List[FloorLineOpportunity]:
        # Timing optimization detection
        pass
    
    # ... additional detection methods
```

#### **API Integration**
```python
# api/routes.py
@api_bp.route('/detect-floor-line-patterns', methods=['POST'])
def detect_floor_line_patterns():
    # RESTful endpoint for floor line pattern detection
    pass
```

#### **Frontend Component**
```javascript
// ui/components/FloorLinePatternAnalysis.js
class FloorLinePatternAnalysis extends React.Component {
    // React component for displaying floor line pattern analysis
}
```

### **Data Models**

#### **FloorLineOpportunity**
```python
@dataclass
class FloorLineOpportunity:
    opportunity_type: str  # "risk_mitigation", "timing_optimization", etc.
    target_position: Optional[Tuple[int, int]]  # Row, column for wall placement
    target_color: Optional[int]  # Color needed for placement
    current_floor_tiles: int  # Current tiles on floor line
    potential_penalty: int  # Current or potential floor line penalty
    penalty_reduction: int  # Points saved by taking action
    urgency_score: float  # 0-10 urgency rating
    risk_assessment: str  # "low", "medium", "high", "critical"
    description: str  # Human-readable description
    move_suggestions: List[Dict]  # Specific move recommendations
    strategic_value: float  # Strategic importance beyond immediate points
```

#### **FloorLinePatternDetection**
```python
@dataclass
class FloorLinePatternDetection:
    risk_mitigation_opportunities: List[FloorLineOpportunity]
    timing_optimization_opportunities: List[FloorLineOpportunity]
    trade_off_opportunities: List[FloorLineOpportunity]
    endgame_management_opportunities: List[FloorLineOpportunity]
    blocking_opportunities: List[FloorLineOpportunity]
    efficiency_opportunities: List[FloorLineOpportunity]
    total_opportunities: int
    total_penalty_risk: int
    confidence_score: float
```

## 🧪 Test Positions

### **FEN String Support**
The system includes comprehensive FEN string support for all floor line test positions:

```python
# api/routes.py - FEN string handlers
elif fen_string == "critical_floor_risk":
    # Create critical floor risk test position
    test_state.agents[0].floor_tiles = [0, 1, 2, 3, 4, 5]  # 6 tiles on floor line

elif fen_string == "high_floor_risk":
    # Create high floor risk test position
    test_state.agents[0].floor_tiles = [0, 1, 2, 3]  # 4 tiles on floor line

elif fen_string == "medium_floor_risk":
    # Create medium floor risk test position
    test_state.agents[0].floor_tiles = [0, 1]  # 2 tiles on floor line

# ... additional FEN handlers for all 12 test positions
```

### **Test Position Categories**
1. **Risk Mitigation Positions**
   - `critical_floor_risk`: 6 tiles on floor line
   - `high_floor_risk`: 4 tiles on floor line
   - `medium_floor_risk`: 2 tiles on floor line

2. **Timing Optimization Positions**
   - `early_game_floor_timing`: 1 tile on floor line
   - `mid_game_floor_timing`: 3 tiles on floor line
   - `endgame_floor_timing`: 5 tiles on floor line

3. **Trade-off Analysis Positions**
   - `wall_completion_trade_off`: Floor penalty vs wall completion
   - `complex_risk_reward`: Multiple strategic considerations

4. **Endgame Management Positions**
   - `endgame_penalty_minimization`: Penalty reduction strategies
   - `efficient_floor_clearance`: Optimal clearing strategies

5. **Blocking Opportunities**
   - `opponent_blocking_opportunity`: Strategic blocking using floor line

## ⚠️ Common Pitfalls & Solutions

### **1. FEN String Integration Issues**

**Problem**: New test positions not recognized by backend API
```python
# ERROR: ValueError: Unsupported FEN format: critical_floor_risk
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

### **2. TileDisplay Count Method Issues**

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

### **3. AgentState Attribute Issues**

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

### **4. Frontend Module Loading Issues**

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

## 🔧 API Usage

### **Floor Line Pattern Detection**
```bash
# POST request to detect floor line patterns
curl -X POST http://localhost:8000/api/v1/detect-floor-line-patterns \
  -H "Content-Type: application/json" \
  -d '{
    "fen_string": "critical_floor_risk",
    "current_player": 0,
    "include_risk_mitigation": true,
    "include_timing_optimization": true,
    "include_trade_offs": true,
    "include_endgame_management": true,
    "include_blocking_opportunities": true,
    "include_efficiency_opportunities": true,
    "include_move_suggestions": true,
    "urgency_threshold": 0.7
  }'
```

### **Response Format**
```json
{
  "risk_mitigation_opportunities": [...],
  "timing_optimization_opportunities": [...],
  "trade_off_opportunities": [...],
  "endgame_management_opportunities": [...],
  "blocking_opportunities": [...],
  "efficiency_opportunities": [...],
  "total_opportunities": 5,
  "total_penalty_risk": -3,
  "confidence_score": 0.85
}
```

## 📊 Urgency Scoring System

### **Risk Levels**
- **CRITICAL**: 9.0-10.0 (6+ floor tiles)
- **HIGH**: 7.0-8.9 (4-5 floor tiles)
- **MEDIUM**: 4.0-6.9 (2-3 floor tiles)
- **LOW**: 1.0-3.9 (1 floor tile)

### **Calculation Factors**
- **Current Penalty**: Base urgency on absolute penalty value
- **Risk Level**: Multiplier based on risk assessment
- **Tile Availability**: Diminishing returns for available tiles
- **Game Phase**: Early/mid/endgame timing considerations
- **Strategic Value**: Long-term strategic importance

## 🎯 Strategic Value Calculation

### **Risk Mitigation Value**
```python
def _calculate_risk_mitigation_strategic_value(self, floor_tiles: int, penalty_reduction: int) -> float:
    return penalty_reduction * (1 + floor_tiles * 0.2)
```

### **Timing Strategic Value**
```python
def _calculate_timing_strategic_value(self, game_phase: str, floor_tiles: int) -> float:
    phase_multipliers = {"early": 0.5, "mid": 1.0, "endgame": 1.5}
    return floor_tiles * phase_multipliers.get(game_phase, 1.0)
```

### **Endgame Strategic Value**
```python
def _calculate_endgame_strategic_value(self, floor_tiles: int, penalty: int) -> float:
    return abs(penalty) * (1 + floor_tiles * 0.3)
```

## 🧪 Testing

### **Unit Tests**
```python
# tests/test_floor_line_patterns.py
class TestAzulFloorLinePatternDetector(unittest.TestCase):
    def setUp(self):
        self.detector = AzulFloorLinePatternDetector()
        self.basic_state = AzulState(2)
    
    def test_risk_mitigation_detection(self):
        # Test risk mitigation detection
        pass
    
    def test_timing_optimization_detection(self):
        # Test timing optimization detection
        pass
    
    # ... additional test methods
```

### **API Testing**
```bash
# Test all floor line test positions
for position in critical_floor_risk high_floor_risk medium_floor_risk early_game_floor_timing mid_game_floor_timing endgame_floor_timing wall_completion_trade_off endgame_penalty_minimization opponent_blocking_opportunity efficient_floor_clearance complex_risk_reward; do
    curl -X POST http://localhost:8000/api/v1/detect-floor-line-patterns \
      -H "Content-Type: application/json" \
      -d "{\"fen_string\": \"$position\", \"current_player\": 0}"
done
```

## 📈 Performance Considerations

### **Optimization Strategies**
1. **Caching**: Cache pattern detection results for repeated positions
2. **Early Termination**: Stop detection if no opportunities found
3. **Threshold Filtering**: Only return opportunities above urgency threshold
4. **Lazy Evaluation**: Calculate strategic values only when needed

### **Memory Management**
- Reuse FloorLineOpportunity objects where possible
- Limit move suggestions to top 5 per opportunity type
- Use efficient data structures for tile counting

## 🔮 Future Enhancements

### **Planned Features**
1. **Machine Learning Integration**: Use neural networks for pattern recognition
2. **Advanced Analytics**: Statistical analysis of floor line patterns
3. **Performance Tracking**: Track pattern detection accuracy over time
4. **Custom Patterns**: Allow users to define custom floor line patterns

### **Integration Opportunities**
1. **Game Analysis**: Integrate with complete game analysis system
2. **Training System**: Use patterns for tactical training exercises
3. **Opening Theory**: Incorporate floor line patterns into opening theory
4. **Performance Dashboard**: Add floor line metrics to analytics dashboard

## 📚 Related Documentation

- [Pattern Detection Guide](./PATTERN_DETECTION_GUIDE.md)
- [Scoring Optimization Patterns](./SCORING_OPTIMIZATION_PATTERNS.md)
- [API Usage Guide](./API_USAGE.md)
- [Competitive Features Summary](./COMPETITIVE_FEATURES_SUMMARY.md)

---

**Last Updated**: August 2025  
**Status**: ✅ **COMPLETED & TESTED**  
**Version**: 1.0.0 