# Floor Line Patterns Implementation

> **Technical implementation details for the floor line pattern detection system**

## 🏗️ **Architecture**

### **Core Components**
1. **`core/azul_floor_line_patterns.py`** - Main floor line pattern detection engine
2. **`api/routes.py`** - REST API endpoint (`/api/v1/detect-floor-line-patterns`)
3. **`ui/components/FloorLinePatternAnalysis.js`** - Frontend display component
4. **`ui/styles/floor-line-pattern-analysis.css`** - UI styling
5. **`tests/test_floor_line_patterns.py`** - Unit tests

### **Data Flow**
```
Game State → Floor Line Detector → API → UI Component → User Display
```

## 🔧 **Implementation Details**

### **Floor Line Pattern Detection Engine (`core/azul_floor_line_patterns.py`)**

The `AzulFloorLinePatternDetector` class analyzes game states to identify floor line opportunities:

```python
class AzulFloorLinePatternDetector:
    def __init__(self, urgency_threshold=0.6):
        self.urgency_threshold = urgency_threshold
    
    def detect_floor_line_patterns(self, state: AzulState, current_player: int) -> FloorLinePatternDetection:
        # Main detection method
        pass
```

#### **Key Methods:**

- **`detect_floor_line_patterns()`** - Main entry point for floor line analysis
- **`_detect_risk_mitigation_opportunities()`** - Identifies risk mitigation scenarios
- **`_detect_timing_optimization_opportunities()`** - Analyzes timing optimization
- **`_detect_trade_off_opportunities()`** - Evaluates wall vs floor trade-offs
- **`_detect_endgame_management_opportunities()`** - Identifies endgame strategies

### **Risk Mitigation Detection**

The system identifies risk mitigation opportunities by:

1. **Counting floor tiles** - Current tiles on floor line
2. **Calculating penalties** - Current penalty level (-1, -1, -2, -2, -2, -3, -3)
3. **Assessing risk levels** - CRITICAL, HIGH, MEDIUM, LOW based on tile count
4. **Finding recovery opportunities** - Wall placements that clear floor line

#### **Risk Level Classification:**

- **CRITICAL**: 6+ tiles on floor line (-3 points)
- **HIGH**: 4-5 tiles on floor line (-2 points)
- **MEDIUM**: 2-3 tiles on floor line (-1 to -2 points)
- **LOW**: 1 tile on floor line (-1 point)

#### **Urgency Calculation**

Urgency is calculated based on multiple factors:

```python
def _calculate_risk_urgency(self, floor_tiles: int, penalty: int, 
                           recovery_opportunities: int) -> float:
    # Risk urgency: more tiles = higher urgency
    risk_urgency = min(floor_tiles / 7.0, 1.0)
    
    # Penalty urgency: higher penalty = higher urgency
    penalty_urgency = min(abs(penalty) / 3.0, 1.0)
    
    # Recovery urgency: fewer opportunities = higher urgency
    recovery_urgency = 1.0 - min(recovery_opportunities / 5.0, 1.0)
    
    # Combine factors
    urgency = (risk_urgency * 0.4) + (penalty_urgency * 0.4) + (recovery_urgency * 0.2)
    return min(1.0, urgency)
```

### **Timing Optimization Detection**

The system analyzes timing optimization by:

1. **Assessing game phase** - Early, mid, or endgame
2. **Evaluating scoring opportunities** - Available wall completion bonuses
3. **Calculating efficiency** - Optimal timing for floor line clearing
4. **Considering multipliers** - Endgame scoring potential

### **Trade-off Analysis**

The system analyzes trade-offs by:

1. **Comparing wall bonuses** - Points from wall completion opportunities
2. **Calculating floor penalties** - Current and potential floor line penalties
3. **Evaluating net value** - Wall bonus minus floor penalty
4. **Assessing strategic value** - Long-term impact beyond immediate points

### **API Integration**

The floor line pattern detection is exposed via a REST API endpoint:

```python
@api_bp.route('/detect-floor-line-patterns', methods=['POST'])
def detect_floor_line_patterns():
    # Handles floor line pattern detection requests
    # Returns JSON with opportunities and move suggestions
```

#### **Request Format:**
```json
{
    "fen_string": "floor_line_risk_scenario",
    "current_player": 0,
    "include_risk_mitigation": true,
    "include_timing_optimization": true,
    "include_trade_off_analysis": true,
    "urgency_threshold": 0.6
}
```

#### **Response Format:**
```json
{
    "risk_mitigation_opportunities": [
        {
            "risk_assessment": "CRITICAL",
            "floor_tiles": 6,
            "potential_penalty": -3,
            "recovery_opportunities": [
                {
                    "wall_position": [2, 3],
                    "penalty_reduction": 3,
                    "description": "Place tile on wall to clear floor line"
                }
            ],
            "urgency": 0.95,
            "urgency_level": "HIGH"
        }
    ],
    "timing_optimization_opportunities": [
        {
            "game_phase": "endgame",
            "optimal_timing": "immediate",
            "efficiency_gain": 5,
            "description": "Clear floor line now for endgame efficiency"
        }
    ],
    "trade_off_opportunities": [
        {
            "wall_bonus": 7,
            "floor_penalty": -2,
            "net_value": 5,
            "recommendation": "accept_penalty"
        }
    ]
}
```

## 🎯 **Algorithm Details**

### **Floor Line Detection Algorithm**

1. **Risk assessment:**
   - Count current floor tiles
   - Calculate current penalty level
   - Classify risk level (CRITICAL/HIGH/MEDIUM/LOW)
   - Identify recovery opportunities

2. **Timing optimization:**
   - Assess current game phase
   - Evaluate available scoring opportunities
   - Calculate optimal timing for floor line clearing
   - Consider endgame multiplier potential

3. **Trade-off analysis:**
   - Compare wall completion bonuses with floor penalties
   - Calculate net value of different options
   - Assess strategic value beyond immediate points
   - Consider opponent disruption potential

4. **Endgame management:**
   - Identify penalty minimization opportunities
   - Calculate efficiency gains from floor line clearing
   - Assess strategic placement opportunities
   - Plan for final scoring optimization

### **Risk Assessment Factors**

- **Floor tile count (40% weight)**: More tiles = higher risk
- **Penalty level (40% weight)**: Higher penalty = higher urgency
- **Recovery opportunities (20% weight)**: Fewer opportunities = higher urgency
- **Game phase**: Endgame considerations for timing
- **Strategic value**: Long-term impact beyond immediate points

## 🧪 **Testing**

### **Test Coverage**
- **Unit tests** for all detection algorithms
- **Integration tests** for API endpoints
- **UI tests** for frontend components
- **Edge case testing** for complex scenarios

### **Test Positions**
- **Critical risk scenarios** - High floor line penalties
- **Timing optimization scenarios** - Different game phases
- **Trade-off scenarios** - Wall vs floor decisions
- **Endgame scenarios** - Final round optimization

## 🔧 **Configuration Options**

### **Risk Thresholds**
- **CRITICAL**: 6+ tiles (immediate action required)
- **HIGH**: 4-5 tiles (action recommended)
- **MEDIUM**: 2-3 tiles (consider clearing)
- **LOW**: 1 tile (usually acceptable)

### **Analysis Parameters**
- **Include risk mitigation**: Detect risk mitigation opportunities
- **Include timing optimization**: Analyze timing optimization
- **Include trade-off analysis**: Evaluate wall vs floor trade-offs
- **Urgency threshold**: Minimum urgency for detection

## 📊 **Performance Optimization**

### **Response Time Targets**
- **Floor line analysis**: < 200ms
- **Risk assessment**: < 100ms
- **Timing optimization**: < 150ms
- **Trade-off analysis**: < 120ms

### **Optimization Techniques**
- **Caching**: Cache analysis results for repeated positions
- **Early termination**: Stop analysis when threshold met
- **Parallel processing**: Analyze different opportunity types simultaneously
- **Memory optimization**: Efficient data structures for floor line analysis

## 🚀 **Future Enhancements**

### **Planned Improvements**
- **Advanced timing analysis** - Consider game phase in floor line decisions
- **Opponent disruption assessment** - Factor in blocking opportunities
- **Machine learning integration** - Improve urgency scoring with ML
- **Advanced trade-off analysis** - More sophisticated wall vs floor evaluation

### **Performance Goals**
- **Sub-150ms detection** for common scenarios
- **Real-time updates** during gameplay
- **Batch processing** for multiple position analysis

---

**The floor line pattern detection system provides comprehensive analysis of floor line management opportunities with configurable risk thresholds and detailed move suggestions.** 🎯 