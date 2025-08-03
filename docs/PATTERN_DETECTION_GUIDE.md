# Pattern Detection System Guide

## Overview

The Pattern Detection System is a core feature of the Azul Solver & Analysis Toolkit that identifies tactical opportunities in game positions. Currently, it focuses on **tile blocking detection** - identifying when players can prevent opponents from completing pattern lines by taking specific tiles.

## Architecture

### Core Components

1. **`core/azul_patterns.py`** - Main pattern detection engine
2. **`api/routes.py`** - REST API endpoint (`/api/v1/detect-patterns`)
3. **`ui/components/PatternAnalysis.js`** - Frontend display component
4. **`ui/styles/pattern-analysis.css`** - UI styling
5. **`tests/test_pattern_detection.py`** - Unit tests

### Data Flow

```
Game State → Pattern Detector → API → UI Component → User Display
```

## How Pattern Detection Works

### 1. Pattern Detection Engine (`core/azul_patterns.py`)

The `AzulPatternDetector` class analyzes game states to identify blocking opportunities:

```python
class AzulPatternDetector:
    def __init__(self, blocking_urgency_threshold=0.7):
        self.blocking_urgency_threshold = blocking_urgency_threshold
    
    def detect_patterns(self, state: AzulState, current_player: int) -> PatternDetection:
        # Main detection method
        pass
```

#### Key Methods:

- **`detect_patterns()`** - Main entry point for pattern analysis
- **`_detect_blocking_opportunities()`** - Identifies blocking scenarios
- **`_analyze_pattern_line_blocking()`** - Analyzes individual pattern lines
- **`_calculate_blocking_urgency()`** - Computes urgency scores
- **`get_blocking_move_suggestions()`** - Generates concrete move suggestions

### 2. Blocking Opportunity Detection

The system identifies blocking opportunities by:

1. **Analyzing opponent pattern lines** - Checking which tiles opponents have in pattern lines
2. **Checking wall completion** - Ensuring the blocking color isn't already on the wall
3. **Counting available tiles** - Determining how many blocking tiles are available
4. **Calculating urgency** - Scoring the importance of the blocking opportunity

#### Urgency Calculation

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

### 3. API Integration

The pattern detection is exposed via a REST API endpoint:

```python
@api_bp.route('/detect-patterns', methods=['POST'])
def detect_patterns():
    # Handles pattern detection requests
    # Returns JSON with blocking opportunities and move suggestions
```

#### Request Format:
```json
{
    "fen_string": "high_urgency_red_blocking",
    "current_player": 0,
    "include_blocking_opportunities": true,
    "include_move_suggestions": true,
    "urgency_threshold": 0.6
}
```

#### Response Format:
```json
{
    "blocking_opportunities": [
        {
            "target_player": 1,
            "target_pattern_line": 2,
            "target_color": 2,
            "target_color_name": "red",
            "blocking_tiles_available": 9,
            "urgency_score": 0.8,
            "urgency_level": "MEDIUM",
            "blocking_factories": [0, 1, 2, 3, 4],
            "blocking_center": true,
            "description": "Block opponent 2's red tiles on pattern line 3..."
        }
    ],
    "move_suggestions": [
        {
            "type": "blocking",
            "urgency_score": 0.8,
            "suggested_action": {
                "action_type": 1,
                "source_id": 1,
                "tile_type": 2,
                "num_to_floor_line": 4
            },
            "description": "Take 4 red tiles from Factory 2..."
        }
    ],
    "total_patterns": 1,
    "patterns_detected": true,
    "confidence_score": 0.62
}
```

### 4. Frontend Integration

The `PatternAnalysis` React component displays detection results:

```javascript
function PatternAnalysis({ gameState, currentPlayer = 0, onPatternDetected }) {
    const [patterns, setPatterns] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    // Auto-detect patterns when game state changes
    useEffect(() => {
        // Reset state and trigger new analysis
        setPatterns(null);
        setError(null);
        
        if (gameState && gameState.fen_string) {
            detectPatterns();
        }
    }, [gameState?.fen_string, currentPlayer, gameState?.factories, gameState?.players]);
}
```

## Current Capabilities

### ✅ Implemented Features

1. **Tile Blocking Detection**
   - Identifies when opponents have tiles in pattern lines
   - Checks if blocking tiles are available in factories/center
   - Calculates urgency based on completion and availability
   - Generates specific move suggestions

2. **Urgency Scoring**
   - **HIGH** (0.8-1.0): Critical blocking opportunities
   - **MEDIUM** (0.6-0.8): Important blocking opportunities  
   - **LOW** (0.0-0.6): Minor blocking opportunities

3. **Move Suggestion Generation**
   - Specific factory recommendations
   - Tile count suggestions
   - Floor line placement options
   - Detailed descriptions

4. **Real-time Analysis**
   - Automatic detection on game state changes
   - Loading states and error handling
   - Reset functionality for new positions

### 🧪 Test Positions

The system includes specialized test positions in `ui/components/positions/blocking-test-positions.js`:

1. **Simple Blue Blocking** - Basic blue tile blocking scenario
2. **High Urgency Red Blocking** - Red tiles with high urgency
3. **Multiple Blocking Opportunities** - Multiple colors in different lines
4. **No Blocking - Color on Wall** - Should NOT detect (color already on wall)

## How to Extend Pattern Detection

### 1. Adding New Pattern Types

To add a new pattern type (e.g., scoring opportunities, wall completion threats):

#### Step 1: Extend the Pattern Detector

```python
# In core/azul_patterns.py
class AzulPatternDetector:
    def detect_patterns(self, state: AzulState, current_player: int) -> PatternDetection:
        opportunities = []
        
        # Existing blocking detection
        opportunities.extend(self._detect_blocking_opportunities(state, current_player))
        
        # NEW: Add your pattern detection
        opportunities.extend(self._detect_scoring_opportunities(state, current_player))
        
        return PatternDetection(
            blocking_opportunities=opportunities,
            # Add new opportunity types here
            scoring_opportunities=scoring_opps,
            total_patterns=len(opportunities) + len(scoring_opps)
        )
    
    def _detect_scoring_opportunities(self, state: AzulState, current_player: int):
        # Implement your new pattern detection logic
        pass
```

#### Step 2: Update Data Structures

```python
# Add new data classes
@dataclass
class ScoringOpportunity:
    target_player: int
    pattern_line: int
    potential_score: int
    urgency_score: float
    description: str

@dataclass
class PatternDetection:
    blocking_opportunities: List[BlockingOpportunity]
    scoring_opportunities: List[ScoringOpportunity]  # NEW
    total_patterns: int
    patterns_detected: bool
    confidence_score: float
```

#### Step 3: Update API Response

```python
# In api/routes.py
@api_bp.route('/detect-patterns', methods=['POST'])
def detect_patterns():
    # ... existing code ...
    
    return jsonify({
        'blocking_opportunities': [opp.to_dict() for opp in result.blocking_opportunities],
        'scoring_opportunities': [opp.to_dict() for opp in result.scoring_opportunities],  # NEW
        'total_patterns': result.total_patterns,
        'patterns_detected': result.patterns_detected,
        'confidence_score': result.confidence_score
    })
```

#### Step 4: Update Frontend

```javascript
// In ui/components/PatternAnalysis.js
function PatternAnalysis({ gameState, currentPlayer = 0, onPatternDetected }) {
    // ... existing code ...
    
    return (
        <div className="pattern-analysis">
            {/* Existing blocking opportunities */}
            {patterns.blocking_opportunities && patterns.blocking_opportunities.length > 0 && (
                <div className="blocking-opportunities">
                    {/* ... existing code ... */}
                </div>
            )}
            
            {/* NEW: Scoring opportunities */}
            {patterns.scoring_opportunities && patterns.scoring_opportunities.length > 0 && (
                <div className="scoring-opportunities">
                    <h4>🎯 Scoring Opportunities</h4>
                    {/* Add your new UI components */}
                </div>
            )}
        </div>
    );
}
```

### 2. Adding New Test Positions

To add test positions for new pattern types:

```javascript
// In ui/components/positions/blocking-test-positions.js
const scoringOpportunityTest = {
    name: "Scoring Opportunity Test",
    description: "Position with clear scoring opportunities",
    difficulty: "intermediate",
    tags: ["scoring", "testing", "pattern-detection"],
    generate: () => createGameState({
        fen_string: "scoring_opportunity_test",
        gameState: {
            // Define your test position
        }
    })
};
```

### 3. Adding New API Handlers

For new FEN strings:

```python
# In api/routes.py
elif fen_string == "scoring_opportunity_test":
    print("DEBUG: Creating scoring opportunity test position")
    random.seed(42)
    test_state = AzulState(2)
    
    # Set up your test position
    # ... configure the state ...
    
    random.seed()
    return test_state
```

### 4. Adding Unit Tests

```python
# In tests/test_pattern_detection.py
def test_scoring_opportunity_detection(self):
    """Test detection of scoring opportunities."""
    detector = AzulPatternDetector()
    
    # Create test state with scoring opportunities
    state = create_test_state_with_scoring_opportunities()
    
    result = detector.detect_patterns(state, current_player=0)
    
    self.assertGreater(len(result.scoring_opportunities), 0)
    # Add more specific assertions
```

## Configuration Options

### Pattern Detection Settings

```python
# In core/azul_patterns.py
class AzulPatternDetector:
    def __init__(self, 
                 blocking_urgency_threshold=0.7,
                 scoring_urgency_threshold=0.6,  # NEW
                 max_patterns_per_type=5):
        self.blocking_urgency_threshold = blocking_urgency_threshold
        self.scoring_urgency_threshold = scoring_urgency_threshold  # NEW
        self.max_patterns_per_type = max_patterns_per_type
```

### API Configuration

```python
# In api/routes.py
@api_bp.route('/detect-patterns', methods=['POST'])
def detect_patterns():
    # Configurable parameters
    urgency_threshold = data.get('urgency_threshold', 0.7)
    include_blocking = data.get('include_blocking_opportunities', True)
    include_scoring = data.get('include_scoring_opportunities', False)  # NEW
    max_results = data.get('max_results', 10)
```

## Performance Considerations

### Optimization Strategies

1. **Caching**: Cache pattern detection results for identical positions
2. **Early Termination**: Stop analysis when sufficient patterns are found
3. **Parallel Processing**: Analyze different pattern types concurrently
4. **Incremental Updates**: Only re-analyze changed components

### Monitoring

```python
# Add performance monitoring
import time

def detect_patterns(self, state: AzulState, current_player: int) -> PatternDetection:
    start_time = time.time()
    
    # ... pattern detection logic ...
    
    execution_time = time.time() - start_time
    print(f"Pattern detection completed in {execution_time:.3f}s")
    
    return result
```

## Troubleshooting

### Common Issues

1. **No patterns detected**
   - Check if `urgency_threshold` is too high
   - Verify game state has valid pattern line data
   - Ensure FEN string is properly handled

2. **Incorrect color detection**
   - Verify color mapping in position data
   - Check pattern line color conversion
   - Ensure API handlers create correct test states

3. **UI not updating**
   - Check `useEffect` dependencies in PatternAnalysis
   - Verify game state changes trigger re-analysis
   - Ensure proper state reset on new positions

### Debug Tools

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints in pattern detection
def _detect_blocking_opportunities(self, state: AzulState, current_player: int):
    print(f"DEBUG: Analyzing {len(state.agents)} players")
    print(f"DEBUG: Current player: {current_player}")
    # ... rest of method
```

## Future Enhancements

### Planned Features

1. **Multi-pattern Detection**
   - Wall completion threats
   - Floor line optimization
   - Factory efficiency analysis

2. **Advanced Scoring**
   - End-game scoring opportunities
   - Multi-turn planning
   - Risk assessment

3. **Machine Learning Integration**
   - Pattern recognition from game data
   - Adaptive urgency thresholds
   - Personalized suggestions

4. **Real-time Analysis**
   - Live game analysis
   - Move-by-move pattern tracking
   - Predictive pattern detection

## Contributing

When extending the pattern detection system:

1. **Follow the existing architecture** - Use the established patterns
2. **Add comprehensive tests** - Ensure new features are well-tested
3. **Update documentation** - Keep this guide current
4. **Consider performance** - Monitor impact on analysis speed
5. **Maintain backward compatibility** - Don't break existing functionality

## Related Documentation

- [COMPETITIVE_FEATURES_SUMMARY.md](./COMPETITIVE_FEATURES_SUMMARY.md) - Feature overview
- [COMPETITIVE_RESEARCH_ROADMAP.md](./COMPETITIVE_RESEARCH_ROADMAP.md) - Development roadmap
- [API_USAGE.md](./API_USAGE.md) - API documentation
- [QUICK_START.md](./QUICK_START.md) - Getting started guide 