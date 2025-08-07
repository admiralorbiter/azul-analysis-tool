# Move Quality Analysis - Usage Guide

## 🚀 **Quick Start**

### **1. Basic Analysis**
```python
from move_quality_analysis.scripts.comprehensive_move_quality_analyzer import (
    ComprehensiveMoveQualityAnalyzer, ComprehensiveAnalysisConfig
)

# Create configuration
config = ComprehensiveAnalysisConfig(
    max_workers=4,
    batch_size=50,
    max_analysis_time=30
)

# Initialize analyzer
analyzer = ComprehensiveMoveQualityAnalyzer(config)

# Analyze a move
result = analyzer.analyze_single_move(state_fen, move_data)
print(f"Quality: {result.quality_tier.value} ({result.quality_score:.1f})")
```

### **2. Exhaustive Search**
```python
from move_quality_analysis.scripts.exhaustive_search import ComprehensiveExhaustiveAnalyzer

# Initialize exhaustive analyzer
analyzer = ComprehensiveExhaustiveAnalyzer()

# Generate and analyze test positions
positions = analyzer.generate_comprehensive_test_positions()
for state, game_phase in positions:
    analysis = analyzer.analyze_position_comprehensive(state, game_phase)
    print(f"Position: {analysis.average_quality_score:.1f} average quality")
```

### **3. API Usage**
```bash
# Analyze a position
curl -X POST http://localhost:5000/api/v1/analyze-position \
  -H "Content-Type: application/json" \
  -d '{
    "state_fen": "your_fen_string_here",
    "player_id": 0,
    "config_overrides": {
      "processing": {"max_workers": 4},
      "move_generation": {"max_moves_per_position": 100}
    }
  }'
```

## ⚙️ **Configuration Options**

### **Processing Settings**
- `max_workers`: Number of parallel workers (default: 8)
- `batch_size`: Batch size for processing (default: 100)
- `max_analysis_time`: Maximum analysis time per move (default: 30s)
- `memory_limit_gb`: Memory limit in GB (default: 4.0)
- `enable_caching`: Enable result caching (default: true)

### **Analysis Modes**
- **Quick Mode**: Fast analysis with limited depth (2 workers, 10s max time)
- **Standard Mode**: Balanced analysis (4 workers, 20s max time)
- **Comprehensive Mode**: Full analysis with all features (8 workers, 30s max time)
- **Research Mode**: Maximum depth analysis (12 workers, 60s max time)

## 📊 **Quality Tiers**

- `!!` (BRILLIANT): 85-100 points - Exceptional moves
- `!` (EXCELLENT): 70-84 points - Very good moves
- `=` (GOOD): 45-69 points - Solid moves
- `?!` (DUBIOUS): 20-44 points - Questionable moves
- `?` (POOR): 0-19 points - Poor moves

## 🗄️ **Database**

### **Tables**
- `comprehensive_analysis_results`: Main results storage
- `comprehensive_move_analyses`: Exhaustive search move analysis results
- `position_analyses`: Exhaustive search position analysis results

### **Data Stored**
- Complete analysis results with all scores
- Educational content and explanations
- Processing metadata and performance metrics
- Configuration used for each analysis

## 🧪 **Testing**

### **Run Tests**
```bash
# Basic functionality test
python test_comprehensive_analyzer.py

# Example usage
python example_comprehensive_analysis.py

# Exhaustive search test
python scripts/exhaustive_search.py
```

### **Test Results**
- **Move Generation**: 20-50 moves per position in <0.1s
- **Analysis Speed**: 0.005s per move (200 moves/second)
- **Parallel Processing**: Scales with CPU cores
- **Memory Usage**: <2GB for typical analysis

## 📁 **File Structure**

```
move_quality_analysis/
├── scripts/
│   ├── comprehensive_move_quality_analyzer.py     # Main analyzer
│   ├── enhanced_move_generator.py                # Move generation
│   ├── analysis_config.py                        # Configuration
│   └── exhaustive_search.py                      # Exhaustive search
├── docs/
│   └── SCRIPTS_README.md                         # Scripts documentation
├── data/
│   ├── comprehensive_analysis_results.db          # Main database
│   ├── comprehensive_exhaustive_analysis.db      # Exhaustive search results
│   └── [Other data files]
├── README.md                                      # Main documentation
├── STATUS_AND_PLANNING.md                        # Status and roadmap
└── USAGE_GUIDE.md                                # This file
```

## ⚠️ **Current Limitations**

### **Exhaustive Search**
- Alpha-Beta and MCTS engines temporarily disabled
- Basic functionality working with pattern analysis and quality assessment
- See `STATUS_AND_PLANNING.md` for detailed status

### **Quality Distribution**
- Too many "poor" moves (62.2%) - needs refinement
- Scoring weights need adjustment for better balance
- Position-specific thresholds needed

## 🎯 **Next Steps**

1. **Test the System**: Run the test scripts
2. **Configure for Your Environment**: Set up configuration files
3. **Integrate with Your UI**: Use the API endpoints
4. **Debug Exhaustive Search**: Fix engine integration issues
5. **Refine Quality Assessment**: Adjust scoring algorithms

## 📚 **Additional Documentation**

- `README.md`: Comprehensive overview and implementation details
- `STATUS_AND_PLANNING.md`: Current status and development roadmap
- `docs/SCRIPTS_README.md`: Detailed scripts documentation
