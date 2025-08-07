# 🚀 Strategic Pattern Analysis - Quick Start Guide

> **Immediate implementation guide for Phase 2.4 development**

## 🎯 **Quick Start Checklist**

### **Week 1: Core Framework Extension** (Priority: HIGHEST)

#### **Day 1-2: Strategic Pattern Detection Framework**
```bash
# Create core strategic pattern files
touch core/azul_strategic_patterns.py
touch core/azul_factory_control.py
touch core/azul_endgame_counting.py
touch core/azul_risk_reward.py
touch core/azul_strategic_utils.py
```

**Immediate Tasks:**
1. **Extend existing pattern detection architecture**
   - Review `core/azul_patterns.py` for integration points
   - Review `core/azul_scoring_optimization.py` for patterns
   - Review `core/azul_floor_line_patterns.py` for structure

2. **Create strategic pattern base classes**
   ```python
   # core/azul_strategic_patterns.py
   from dataclasses import dataclass
   from typing import List, Dict, Optional
   from .azul_model import AzulState
   
   @dataclass
   class StrategicPattern:
       """Base class for strategic patterns."""
       pattern_type: str
       strategic_value: float
       urgency_score: float
       confidence: float
       description: str
   
   class StrategicPatternDetector:
       """Main strategic pattern detection engine."""
       
       def __init__(self):
           self.factory_control_detector = FactoryControlDetector()
           self.endgame_counting_detector = EndgameCountingDetector()
           self.risk_reward_analyzer = RiskRewardAnalyzer()
       
       def detect_strategic_patterns(self, state: AzulState) -> Dict[str, List]:
           """Detect all strategic patterns in the current position."""
           return {
               'factory_control': self.factory_control_detector.detect_opportunities(state),
               'endgame_scenarios': self.endgame_counting_detector.analyze_scenarios(state),
               'risk_reward': self.risk_reward_analyzer.analyze_scenarios(state)
           }
   ```

#### **Day 3-4: Factory Control Implementation**
```python
# core/azul_factory_control.py
@dataclass
class FactoryControlOpportunity:
    """Represents a factory control opportunity."""
    control_type: str  # "domination", "disruption", "timing", "color_control"
    factory_id: int
    strategic_value: float
    urgency_score: float
    urgency_level: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    risk_assessment: str  # "low", "medium", "high"
    move_suggestions: List[str]
    confidence: float
    description: str

class FactoryControlDetector:
    """Factory control opportunity detection."""
    
    def detect_opportunities(self, state: AzulState) -> List[FactoryControlOpportunity]:
        opportunities = []
        
        # Factory domination detection
        opportunities.extend(self._detect_factory_domination(state))
        
        # Disruption control detection
        opportunities.extend(self._detect_disruption_control(state))
        
        # Timing control detection
        opportunities.extend(self._detect_timing_control(state))
        
        # Color control detection
        opportunities.extend(self._detect_color_control(state))
        
        return opportunities
    
    def _detect_factory_domination(self, state: AzulState) -> List[FactoryControlOpportunity]:
        """Detect opportunities to dominate key factories."""
        opportunities = []
        
        for factory_id, factory in enumerate(state.factories):
            # Analyze factory tile distribution
            tile_distribution = self._analyze_factory_distribution(factory)
            
            # Check for domination opportunities
            if self._is_domination_opportunity(tile_distribution):
                opportunities.append(FactoryControlOpportunity(
                    control_type="domination",
                    factory_id=factory_id,
                    strategic_value=self._calculate_domination_value(tile_distribution),
                    urgency_score=self._calculate_domination_urgency(tile_distribution),
                    urgency_level=self._get_urgency_level(self._calculate_domination_urgency(tile_distribution)),
                    risk_assessment="low",
                    move_suggestions=self._generate_domination_moves(factory_id, tile_distribution),
                    confidence=0.8,
                    description=f"Factory {factory_id} domination opportunity"
                ))
        
        return opportunities
```

#### **Day 5-7: Endgame Counting Implementation**
```python
# core/azul_endgame_counting.py
@dataclass
class EndgameScenario:
    """Represents an endgame scenario analysis."""
    scenario_type: str  # "conservation", "optimization", "blocking", "timing"
    remaining_tiles: Dict[str, int]  # Color -> count
    scoring_potential: float
    optimal_sequence: List[str]
    risk_level: str  # "low", "medium", "high"
    urgency_score: float
    confidence: float
    description: str

class EndgameCountingDetector:
    """Endgame scenario analysis with precise counting."""
    
    def analyze_scenarios(self, state: AzulState) -> List[EndgameScenario]:
        scenarios = []
        
        # Tile conservation analysis
        scenarios.extend(self._analyze_tile_conservation(state))
        
        # Scoring potential calculation
        scenarios.extend(self._analyze_scoring_potential(state))
        
        # Move sequence optimization
        scenarios.extend(self._analyze_move_sequences(state))
        
        # Risk assessment
        scenarios.extend(self._analyze_endgame_risks(state))
        
        return scenarios
    
    def _analyze_tile_conservation(self, state: AzulState) -> List[EndgameScenario]:
        """Analyze tile conservation strategies."""
        scenarios = []
        
        # Count remaining tiles
        remaining_tiles = self._count_remaining_tiles(state)
        
        # Analyze conservation opportunities
        if self._is_conservation_opportunity(remaining_tiles):
            scenarios.append(EndgameScenario(
                scenario_type="conservation",
                remaining_tiles=remaining_tiles,
                scoring_potential=self._calculate_conservation_potential(remaining_tiles),
                optimal_sequence=self._generate_conservation_sequence(remaining_tiles),
                risk_level="low",
                urgency_score=self._calculate_conservation_urgency(remaining_tiles),
                confidence=0.9,
                description="Tile conservation opportunity detected"
            ))
        
        return scenarios
```

### **Week 2: API Integration** (Priority: HIGH)

#### **Day 1-3: REST API Endpoints**
```python
# api/routes.py - Add these endpoints
from core.azul_factory_control import FactoryControlDetector
from core.azul_endgame_counting import EndgameCountingDetector
from core.azul_risk_reward import RiskRewardAnalyzer

@app.route('/api/v1/detect-factory-control', methods=['POST'])
def detect_factory_control():
    """Detect factory control opportunities."""
    try:
        data = request.get_json()
        state = AzulState.from_dict(data['state'])
        
        detector = FactoryControlDetector()
        opportunities = detector.detect_opportunities(state)
        
        return jsonify({
            'success': True,
            'opportunities': [opp.__dict__ for opp in opportunities],
            'confidence': detector.calculate_confidence(opportunities)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/v1/analyze-endgame-scenarios', methods=['POST'])
def analyze_endgame_scenarios():
    """Analyze endgame scenarios with precise counting."""
    try:
        data = request.get_json()
        state = AzulState.from_dict(data['state'])
        
        detector = EndgameCountingDetector()
        scenarios = detector.analyze_scenarios(state)
        
        return jsonify({
            'success': True,
            'scenarios': [scenario.__dict__ for scenario in scenarios],
            'confidence': detector.calculate_confidence(scenarios)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/v1/analyze-risk-reward', methods=['POST'])
def analyze_risk_reward():
    """Analyze risk/reward scenarios."""
    try:
        data = request.get_json()
        state = AzulState.from_dict(data['state'])
        
        analyzer = RiskRewardAnalyzer()
        scenarios = analyzer.analyze_scenarios(state)
        
        return jsonify({
            'success': True,
            'scenarios': [scenario.__dict__ for scenario in scenarios],
            'confidence': analyzer.calculate_confidence(scenarios)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
```

#### **Day 4-7: Error Handling & Performance**
```python
# core/azul_strategic_utils.py
import time
from contextlib import contextmanager

class StrategicAnalysisCache:
    """Cache for strategic analysis results."""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
    
    def get_cached_result(self, state_hash: str, analysis_type: str) -> Optional[Dict]:
        """Get cached analysis result."""
        key = f"{state_hash}_{analysis_type}"
        return self.cache.get(key)
    
    def cache_result(self, state_hash: str, analysis_type: str, result: Dict):
        """Cache analysis result."""
        key = f"{state_hash}_{analysis_type}"
        
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = result

@contextmanager
def timeout(seconds):
    """Timeout context manager for analysis functions."""
    def signal_handler(signum, frame):
        raise TimeoutError("Analysis timed out")
    
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)
```

### **Week 3: UI Components** (Priority: MEDIUM)

#### **Day 1-3: Factory Control Analysis UI**
```javascript
// ui/components/FactoryControlAnalysis.js
import React, { useState, useEffect } from 'react';

class FactoryControlAnalysis extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            opportunities: [],
            loading: false,
            error: null
        };
    }
    
    async analyzeFactoryControl() {
        this.setState({ loading: true, error: null });
        
        try {
            const response = await fetch('/api/v1/detect-factory-control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ state: this.props.gameState })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.setState({ 
                    opportunities: data.opportunities,
                    loading: false 
                });
            } else {
                this.setState({ 
                    error: data.error,
                    loading: false 
                });
            }
        } catch (error) {
            this.setState({ 
                error: 'Analysis failed',
                loading: false 
            });
        }
    }
    
    componentDidMount() {
        if (this.props.gameState) {
            this.analyzeFactoryControl();
        }
    }
    
    componentDidUpdate(prevProps) {
        if (prevProps.gameState !== this.props.gameState) {
            this.analyzeFactoryControl();
        }
    }
    
    render() {
        const { opportunities, loading, error } = this.state;
        
        if (loading) {
            return <div className="factory-control-analysis loading">Analyzing factory control...</div>;
        }
        
        if (error) {
            return <div className="factory-control-analysis error">Error: {error}</div>;
        }
        
        return (
            <div className="factory-control-analysis">
                <h3>Factory Control Analysis</h3>
                {opportunities.length === 0 ? (
                    <p>No factory control opportunities detected.</p>
                ) : (
                    <div className="opportunities">
                        {opportunities.map((opp, index) => (
                            <div key={index} className={`opportunity ${opp.urgency_level.toLowerCase()}`}>
                                <h4>{opp.control_type.replace('_', ' ').toUpperCase()}</h4>
                                <p><strong>Factory:</strong> {opp.factory_id}</p>
                                <p><strong>Strategic Value:</strong> {opp.strategic_value}</p>
                                <p><strong>Urgency:</strong> {opp.urgency_level}</p>
                                <p><strong>Risk:</strong> {opp.risk_assessment}</p>
                                <p><strong>Description:</strong> {opp.description}</p>
                                <div className="move-suggestions">
                                    <strong>Move Suggestions:</strong>
                                    <ul>
                                        {opp.move_suggestions.map((move, i) => (
                                            <li key={i}>{move}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        );
    }
}

export default FactoryControlAnalysis;
```

#### **Day 4-7: Endgame Counting & Risk/Reward UI**
```javascript
// ui/components/EndgameCountingAnalysis.js
// Similar structure to FactoryControlAnalysis but for endgame scenarios

// ui/components/RiskRewardAnalysis.js  
// Similar structure to FactoryControlAnalysis but for risk/reward scenarios
```

### **Week 4: Testing & Validation** (Priority: HIGH)

#### **Day 1-3: Test Suite Implementation**
```python
# tests/test_strategic_pattern_analysis.py
import unittest
from core.azul_strategic_patterns import StrategicPatternDetector
from core.azul_factory_control import FactoryControlDetector
from core.azul_endgame_counting import EndgameCountingDetector
from core.azul_risk_reward import RiskRewardAnalyzer

class TestStrategicPatternAnalysis(unittest.TestCase):
    
    def setUp(self):
        self.detector = StrategicPatternDetector()
        self.test_state = self.create_test_state()
    
    def test_factory_control_detection(self):
        """Test factory control opportunity detection."""
        opportunities = self.detector.factory_control_detector.detect_opportunities(self.test_state)
        
        self.assertIsInstance(opportunities, list)
        for opp in opportunities:
            self.assertIsInstance(opp, FactoryControlOpportunity)
            self.assertIn(opp.control_type, ['domination', 'disruption', 'timing', 'color_control'])
    
    def test_endgame_counting_analysis(self):
        """Test endgame scenario analysis."""
        scenarios = self.detector.endgame_counting_detector.analyze_scenarios(self.test_state)
        
        self.assertIsInstance(scenarios, list)
        for scenario in scenarios:
            self.assertIsInstance(scenario, EndgameScenario)
            self.assertIn(scenario.scenario_type, ['conservation', 'optimization', 'blocking', 'timing'])
    
    def test_risk_reward_calculation(self):
        """Test risk/reward scenario analysis."""
        scenarios = self.detector.risk_reward_analyzer.analyze_scenarios(self.test_state)
        
        self.assertIsInstance(scenarios, list)
        for scenario in scenarios:
            self.assertIsInstance(scenario, RiskRewardScenario)
            self.assertIn(scenario.scenario_type, ['floor_risk', 'blocking_risk', 'timing_risk', 'scoring_risk'])
    
    def create_test_state(self):
        """Create a test state for strategic analysis."""
        # Implementation for creating test state
        pass

if __name__ == '__main__':
    unittest.main()
```

#### **Day 4-7: Integration Testing**
```python
# tests/test_strategic_integration.py
import unittest
import requests
import json

class TestStrategicIntegration(unittest.TestCase):
    
    def setUp(self):
        self.base_url = "http://localhost:8000"
        self.test_state_dict = self.create_test_state_dict()
    
    def test_factory_control_api(self):
        """Test factory control API endpoint."""
        response = requests.post(
            f"{self.base_url}/api/v1/detect-factory-control",
            json={'state': self.test_state_dict}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('opportunities', data)
    
    def test_endgame_scenarios_api(self):
        """Test endgame scenarios API endpoint."""
        response = requests.post(
            f"{self.base_url}/api/v1/analyze-endgame-scenarios",
            json={'state': self.test_state_dict}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('scenarios', data)
    
    def test_risk_reward_api(self):
        """Test risk/reward API endpoint."""
        response = requests.post(
            f"{self.base_url}/api/v1/analyze-risk-reward",
            json={'state': self.test_state_dict}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('scenarios', data)
    
    def create_test_state_dict(self):
        """Create a test state dictionary for API testing."""
        # Implementation for creating test state dictionary
        pass

if __name__ == '__main__':
    unittest.main()
```

## 🎯 **Implementation Priorities**

### **Week 1 Priorities** (CRITICAL)
1. **Extend pattern detection framework** - Foundation for all strategic analysis
2. **Implement factory control detection** - Most immediately useful for competitive play
3. **Add endgame counting analysis** - Critical for endgame optimization
4. **Create risk/reward analysis** - Essential for strategic decision making

### **Week 2 Priorities** (HIGH)
1. **Add REST API endpoints** - Enable UI integration
2. **Implement error handling** - Ensure robustness
3. **Add performance optimization** - Meet response time targets
4. **Create caching system** - Improve performance

### **Week 3 Priorities** (MEDIUM)
1. **Create UI components** - User interface for strategic analysis
2. **Add visualization features** - Make analysis results clear
3. **Implement user interactions** - Enable user control
4. **Add responsive design** - Ensure usability

### **Week 4 Priorities** (HIGH)
1. **Write comprehensive tests** - Ensure reliability
2. **Create test positions** - Validate analysis accuracy
3. **Add integration testing** - Verify system integration
4. **Performance testing** - Meet performance targets

## 🚀 **Getting Started Right Now**

### **Step 1: Create Core Files**
```bash
# Create strategic pattern analysis files
mkdir -p core
touch core/azul_strategic_patterns.py
touch core/azul_factory_control.py
touch core/azul_endgame_counting.py
touch core/azul_risk_reward.py
touch core/azul_strategic_utils.py
```

### **Step 2: Start with Factory Control**
```python
# Begin with factory control detection (most immediately useful)
# Copy the FactoryControlDetector implementation above
# Test with existing game states
```

### **Step 3: Add API Endpoints**
```python
# Add the factory control API endpoint first
# Test with curl or Postman
```

### **Step 4: Create Basic UI**
```javascript
// Create basic factory control analysis component
// Test with existing UI integration
```

## 📊 **Success Metrics**

### **Performance Targets**
- **Factory Control Analysis**: < 300ms
- **Endgame Counting Analysis**: < 500ms  
- **Risk/Reward Analysis**: < 400ms
- **API Response Time**: < 200ms

### **Accuracy Targets**
- **Factory Control Detection**: > 85% accuracy
- **Endgame Counting**: > 90% accuracy
- **Risk/Reward Assessment**: > 80% accuracy

### **Usability Targets**
- **UI Responsiveness**: < 100ms for updates
- **Analysis Clarity**: Clear, actionable insights
- **Integration**: Seamless with existing tools

---

**This quick start guide provides immediate implementation steps for Strategic Pattern Analysis, focusing on the most critical components first.** 🚀

---

*Last Updated: December 2024*  
*Status: Ready for Implementation*  
*Priority: High - Essential for competitive analysis completion* 