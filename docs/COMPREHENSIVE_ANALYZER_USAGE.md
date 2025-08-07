# Comprehensive Move Quality Analyzer - Usage Guide

## Overview

The Comprehensive Move Quality Analyzer is an enhanced analysis system that provides deep, multi-faceted evaluation of Azul moves with parallel processing capabilities and extensive configuration options.

## Features

- **Parallel Processing**: Utilizes multiple CPU cores for faster analysis
- **Comprehensive Move Generation**: Generates all possible moves with prioritization
- **Advanced Analysis**: Pattern analysis, strategic evaluation, risk assessment, and more
- **Educational Insights**: Detailed explanations and tactical insights
- **Configuration System**: Flexible configuration with JSON/YAML support
- **API Integration**: REST API endpoints for easy integration
- **Database Storage**: Persistent storage of analysis results

## Quick Start

### 1. Basic Usage

```python
from move_quality_analysis.scripts.comprehensive_move_quality_analyzer import (
    ComprehensiveMoveQualityAnalyzer, ComprehensiveAnalysisConfig
)
from core.azul_model import AzulState

# Create configuration
config = ComprehensiveAnalysisConfig(
    max_workers=4,
    batch_size=50,
    max_analysis_time=30
)

# Initialize analyzer
analyzer = ComprehensiveMoveQualityAnalyzer(config)

# Analyze a position
state = AzulState(2)
state_fen = state.to_fen()

# Generate and analyze moves
move_data = {
    'move_type': 'factory_to_pattern',
    'factory_id': 0,
    'color': 0,
    'count': 4,
    'target_line': 1
}

result = analyzer.analyze_single_move(state_fen, move_data)
print(f"Move quality: {result.quality_tier.value} ({result.quality_score:.1f})")
```

### 2. Move Generation

```python
from move_quality_analysis.scripts.enhanced_move_generator import EnhancedMoveGenerator

# Initialize move generator
generator = EnhancedMoveGenerator(max_moves_per_position=200, enable_filtering=True)

# Generate all possible moves for a position
moves = generator.generate_all_moves(state, player_id=0)

# Get move summary
summary = generator.generate_move_summary(moves)
print(f"Generated {len(moves)} moves")
```

### 3. Configuration Management

```python
from move_quality_analysis.scripts.analysis_config import ConfigurationManager

# Load configuration
manager = ConfigurationManager()
config = manager.load_configuration()

# Get preset configurations
presets = manager.get_mode_presets()
quick_config = presets['quick']
comprehensive_config = presets['comprehensive']
```

## API Usage

### Analyze Position

```bash
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

### Generate Moves

```bash
curl -X POST http://localhost:5000/api/v1/generate-moves \
  -H "Content-Type: application/json" \
  -d '{
    "state_fen": "your_fen_string_here",
    "player_id": 0,
    "enable_filtering": true,
    "max_moves": 200
  }'
```

### Get Configuration

```bash
curl http://localhost:5000/api/v1/config
```

### Update Configuration

```bash
curl -X POST http://localhost:5000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "config_overrides": {
      "processing": {"max_workers": 8},
      "move_generation": {"max_moves_per_position": 300}
    }
  }'
```

## Configuration Options

### Processing Configuration

- `max_workers`: Number of parallel workers (default: 8)
- `batch_size`: Batch size for processing (default: 100)
- `max_analysis_time`: Maximum analysis time per move in seconds (default: 30)
- `memory_limit_gb`: Memory limit in GB (default: 4.0)
- `enable_caching`: Enable result caching (default: true)
- `retry_failed_analyses`: Retry failed analyses (default: true)

### Analysis Components

- `enable_pattern_analysis`: Enable pattern detection (default: true)
- `enable_strategic_analysis`: Enable strategic analysis (default: true)
- `enable_risk_analysis`: Enable risk assessment (default: true)
- `enable_board_state_analysis`: Enable board state analysis (default: true)
- `enable_opponent_denial`: Enable opponent denial analysis (default: true)
- `enable_timing_analysis`: Enable timing analysis (default: true)
- `enable_neural_evaluation`: Enable neural network evaluation (default: false)
- `enable_ml_integration`: Enable ML integration (default: false)

### Move Generation

- `max_moves_per_position`: Maximum moves per position (default: 200)
- `enable_move_filtering`: Enable move filtering (default: true)
- `enable_move_prioritization`: Enable move prioritization (default: true)
- `enable_move_clustering`: Enable move clustering (default: true)
- `min_strategic_value`: Minimum strategic value threshold (default: 5.0)
- `min_likelihood`: Minimum likelihood threshold (default: 0.05)
- `min_validation_score`: Minimum validation score threshold (default: 0.1)

## Analysis Modes

### Quick Mode
- Fast analysis with limited depth
- 2 workers, 25 batch size, 10s max time
- 50 moves per position
- No neural evaluation

### Standard Mode
- Balanced analysis
- 4 workers, 50 batch size, 20s max time
- 100 moves per position

### Comprehensive Mode
- Full analysis with all features
- 8 workers, 100 batch size, 30s max time
- 200 moves per position
- Neural evaluation enabled

### Research Mode
- Maximum depth analysis
- 12 workers, 200 batch size, 60s max time
- 500 moves per position
- All features enabled including profiling

## Quality Tiers

The analyzer uses a 5-tier quality classification system:

- `!!` (BRILLIANT): 85-100 points - Exceptional moves
- `!` (EXCELLENT): 70-84 points - Very good moves
- `=` (GOOD): 45-69 points - Solid moves
- `?!` (DUBIOUS): 20-44 points - Questionable moves
- `?` (POOR): 0-19 points - Poor moves

## Analysis Results

Each analysis result includes:

- **Core Scores**: Pattern score, strategic score, risk score, quality score
- **Advanced Analysis**: Board state impact, opponent denial, timing score, risk-reward ratio
- **Educational Content**: Strategic reasoning, tactical insights, educational explanation
- **Metadata**: Confidence intervals, analysis methods used, processing metadata

## Database Integration

The analyzer automatically stores results in SQLite databases:

- `comprehensive_analysis_results.db`: Main results database
- `analysis_cache.db`: Caching database for performance
- Indexed for fast queries on position_id, quality_score, and quality_tier

## Performance Optimization

### Environment Variables

Set these environment variables to override configuration:

```bash
export ANALYSIS_MAX_WORKERS=8
export ANALYSIS_BATCH_SIZE=100
export ANALYSIS_MAX_TIME=30
export ANALYSIS_MODE=comprehensive
export ANALYSIS_STRATEGY=multi_process
export ANALYSIS_DB_PATH=/path/to/database.db
export ANALYSIS_LOG_LEVEL=INFO
```

### Configuration Files

Create configuration files in JSON or YAML format:

```json
{
  "analysis_mode": "comprehensive",
  "processing": {
    "max_workers": 8,
    "batch_size": 100,
    "max_analysis_time": 30
  },
  "move_generation": {
    "max_moves_per_position": 200,
    "enable_filtering": true
  }
}
```

## Testing

Run the test suite to verify functionality:

```bash
python test_comprehensive_analyzer.py
```

This will test:
- Basic functionality
- Configuration system
- API integration
- Database integration

## Integration with Existing Systems

The comprehensive analyzer integrates with your existing infrastructure:

- **Core Model**: Uses `AzulState` and `AzulGameRule` from `core/`
- **Move Quality**: Integrates with existing `AzulMoveQualityAssessor`
- **API**: Extends your existing Flask API with new endpoints
- **Database**: Uses your existing database patterns
- **Pattern Detection**: Leverages existing pattern detection systems

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project root is in Python path
2. **Memory Issues**: Reduce `max_workers` or `batch_size`
3. **Timeout Errors**: Increase `max_analysis_time`
4. **Database Errors**: Check file permissions for database directory

### Debug Mode

Enable debug mode for detailed logging:

```python
config = ComprehensiveAnalysisConfig(enable_debug_mode=True)
```

### Performance Monitoring

Enable profiling for performance analysis:

```python
config = ComprehensiveAnalysisConfig(enable_profiling=True)
```

## Next Steps

1. **Run Tests**: Execute the test suite to verify everything works
2. **Configure**: Set up configuration files for your environment
3. **Integrate**: Use the API endpoints in your applications
4. **Optimize**: Adjust settings based on your hardware and requirements
5. **Extend**: Add custom analysis components as needed

The comprehensive analyzer provides a solid foundation for advanced Azul move quality analysis with the flexibility to adapt to different use cases and performance requirements. 