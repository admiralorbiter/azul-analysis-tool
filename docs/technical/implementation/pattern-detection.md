# Pattern Detection Implementation

> **Technical implementation details for the pattern detection system**

## 🏗️ **Architecture**

### **Core Components**
1. **`core/azul_patterns.py`** - Main pattern detection engine
2. **`api/routes.py`** - REST API endpoint (`/api/v1/detect-patterns`)
3. **`ui/components/PatternAnalysis.js`** - Frontend display component
4. **`ui/styles/pattern-analysis.css`** - UI styling
5. **`tests/test_pattern_detection.py`** - Unit tests

### **Data Flow**
```
Game State → Pattern Detector → API → UI Component → User Display
```

## 🔧 **Implementation Details**

### **Pattern Detection Engine (`core/azul_patterns.py`)**

The `AzulPatternDetector` class analyzes game states to identify blocking opportunities:

```python
class AzulPatternDetector:
    def __init__(self, blocking_urgency_threshold=0.7):
        self.blocking_urgency_threshold = blocking_urgency_threshold
    
    def detect_patterns(self, state: AzulState, current_player: int) -> PatternDetection:
        # Main detection method
        pass
```

#### **Key Methods:**

- **`detect_patterns()`** - Main entry point for pattern analysis
- **`_detect_blocking_opportunities()`** - Identifies blocking scenarios
- **`_analyze_pattern_line_blocking()`** - Analyzes individual pattern lines
- **`_calculate_blocking_urgency()`** - Computes urgency scores
- **`get_blocking_move_suggestions()`** - Generates concrete move suggestions

### **Blocking Opportunity Detection**

The system identifies blocking opportunities by:

1. **Analyzing opponent pattern lines** - Checking which tiles opponents have in pattern lines
2. **Checking wall completion** - Ensuring the blocking color isn't already on the wall
3. **Counting available tiles** - Determining how many blocking tiles are available
4. **Calculating urgency** - Scoring the importance of the blocking opportunity

#### **Urgency Calculation**

Urgency is calculated based on multiple factors:

```python
def _calculate_blocking_urgency(self, tiles_needed: int, tiles_available: int, 
                              current_tiles: int, line_capacity: int) -> float:
    # Completion urgency: fewer tiles needed = higher urgency
    completion_ratio = tiles_needed / line_capacity if line_capacity > 0 else 0
    completion_urgency = 1.0 - completion_ratio
    
    # Availability urgency: fewer tiles available = higher urgency
    availability_ratio = min(tiles_available / tiles_needed, 2.0) if tiles_needed > 0 else 0
    availability_urgency = 1.0 - (availability_ratio / 2.0)
    
    # Combine factors
    urgency = (completion_urgency * 0.6) + (availability_urgency * 0.4)
    return min(1.0, urgency)
```

### **API Integration**

The pattern detection is exposed via a REST API endpoint:

```python
@api_bp.route('/detect-patterns', methods=['POST'])
def detect_patterns():
    # Handles pattern detection requests
    # Returns JSON with blocking opportunities and move suggestions
```

#### **Request Format:**
```json
{
    "fen_string": "high_urgency_red_blocking",
    "current_player": 0,
    "include_blocking_opportunities": true,
    "include_move_suggestions": true,
    "urgency_threshold": 0.6
}
```

#### **Response Format:**
```json
{
    "blocking_opportunities": [
        {
            "color": "red",
            "opponent": 1,
            "pattern_line": 4,
            "tiles_needed": 1,
            "tiles_available": 2,
            "urgency": 0.85,
            "urgency_level": "HIGH"
        }
    ],
    "move_suggestions": [
        {
            "factory_index": 0,
            "color": "red",
            "pattern_line": 2,
            "explanation": "Block opponent's red pattern line 4"
        }
    ]
}
```

## 🎯 **Algorithm Details**

### **Blocking Detection Algorithm**

1. **For each opponent:**
   - Check all pattern lines for tiles
   - Calculate tiles needed to complete each line
   - Check if completion is possible (wall space available)

2. **For each blocking opportunity:**
   - Count available blocking tiles in factories/center
   - Calculate urgency based on completion ratio and availability
   - Generate move suggestions for blocking

3. **Filter and rank:**
   - Apply urgency threshold filtering
   - Rank opportunities by urgency level
   - Generate specific move recommendations

### **Urgency Scoring Factors**

- **Completion urgency (60% weight)**: How close opponent is to completing
- **Availability urgency (40% weight)**: How few blocking tiles are available
- **Scoring potential**: Value of the completed pattern line
- **Strategic importance**: Impact on game state

## 🧪 **Testing**

### **Test Coverage**
- **Unit tests** for all detection algorithms
- **Integration tests** for API endpoints
- **UI tests** for frontend components
- **Edge case testing** for complex scenarios

### **Test Positions**
- **High urgency scenarios** - Critical blocking opportunities
- **Medium urgency scenarios** - Moderate blocking situations
- **Low urgency scenarios** - Minor blocking opportunities
- **Edge cases** - Complex multi-player scenarios

## 🔧 **Configuration Options**

### **Urgency Thresholds**
- **HIGH**: 0.8+ (critical blocking opportunities)
- **MEDIUM**: 0.6-0.8 (moderate blocking opportunities)
- **LOW**: 0.4-0.6 (minor blocking opportunities)

### **Analysis Parameters**
- **Blocking urgency threshold**: Minimum urgency for detection
- **Include move suggestions**: Generate specific move recommendations
- **Analysis depth**: Quick vs thorough analysis

## 📊 **Performance Optimization**

### **Response Time Targets**
- **Pattern detection**: < 100ms
- **Move suggestions**: < 150ms
- **Real-time analysis**: < 200ms

### **Optimization Techniques**
- **Caching**: Cache analysis results for repeated positions
- **Early termination**: Stop analysis when threshold met
- **Parallel processing**: Analyze multiple opponents simultaneously
- **Memory optimization**: Efficient data structures for large states

## 🚀 **Future Enhancements**

### **Planned Improvements**
- **Multi-blocking detection** - Find moves that block multiple opponents
- **Strategic blocking** - Consider long-term blocking value
- **Machine learning integration** - Improve urgency scoring with ML
- **Advanced move suggestions** - More sophisticated move recommendations

### **Performance Goals**
- **Sub-50ms detection** for common scenarios
- **Real-time updates** during gameplay
- **Batch processing** for multiple position analysis

---

**The pattern detection system provides comprehensive blocking opportunity analysis with configurable urgency thresholds and detailed move suggestions.** 🎯 