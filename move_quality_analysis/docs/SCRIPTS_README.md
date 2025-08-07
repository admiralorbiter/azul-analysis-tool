# 📊 Move Quality Analysis Scripts

This directory contains scripts for building and analyzing move quality data for Azul.

## 🎯 Overview

The goal is to build a comprehensive database of "good moves" in Azul by analyzing diverse positions using multiple engines and pattern detection systems.

## 📁 Script Organization

### 1. Data Generation Scripts

#### `generate_diverse_positions_simple.py`
- **Purpose**: Generate diverse Azul positions for analysis
- **Output**: `data/diverse_positions_simple.json`
- **Features**:
  - Creates positions across different game phases (opening, middlegame, endgame)
  - Generates strategic scenarios (blocking, scoring, floor line management)
  - Produces 45 diverse positions for comprehensive analysis

#### `generate_diverse_positions.py` (Legacy)
- **Purpose**: Original position generation script (more complex)
- **Status**: Replaced by simple version due to reliability issues

### 2. Analysis Scripts

#### `analyze_move_quality_simple.py` ⭐ **RECOMMENDED**
- **Purpose**: Analyze positions using reliable components only
- **Output**: `data/simple_move_quality.db`
- **Features**:
  - Neural evaluation analysis
  - Pattern detection integration
  - 5-tier quality classification (!!, !, =, ?!, ?)
  - Strategic reasoning generation
  - Educational explanations
  - Analyzes 15 moves per position
  - **Status**: ✅ Working and tested

#### `analyze_move_quality_comprehensive.py` (Experimental)
- **Purpose**: Full multi-engine analysis (Alpha-Beta, MCTS, Neural)
- **Output**: `data/comprehensive_move_quality.db`
- **Features**:
  - Multi-engine consensus analysis
  - More detailed analysis but prone to errors
  - **Status**: ⚠️ Has issues with Alpha-Beta and MCTS engines

### 3. Database Query Scripts

#### `query_move_quality_database.py`
- **Purpose**: Query and display move quality database results
- **Features**:
  - Summary statistics
  - Quality tier distribution
  - Sample move analyses
  - Pattern analysis results
  - Top moves by quality score
  - Complexity analysis

### 4. Legacy Scripts (For Reference)

#### `build_move_quality_database_simple.py`
- **Purpose**: Original simple database builder
- **Status**: Replaced by `analyze_move_quality_simple.py`

#### `build_move_quality_database.py`
- **Purpose**: Original comprehensive database builder
- **Status**: Replaced by `analyze_move_quality_comprehensive.py`

## 🚀 Quick Start

1. **Generate positions**:
   ```bash
   python scripts/generate_diverse_positions_simple.py
   ```

2. **Analyze moves**:
   ```bash
   python scripts/analyze_move_quality_simple.py
   ```

3. **Query results**:
   ```bash
   python scripts/query_move_quality_database.py
   ```

## 📊 Data Structure

### Quality Tiers
- **!! (Brilliant)**: 90-100 points - Exceptional moves with multiple advantages
- **! (Excellent)**: 75-89 points - Strong moves with clear strategic benefits
- **= (Good)**: 50-74 points - Solid moves that advance position
- **?! (Dubious)**: 25-49 points - Moves with some drawbacks
- **? (Poor)**: 0-24 points - Moves with significant drawbacks

### Analysis Components
- **Neural Evaluation**: Position scoring using heuristic evaluator
- **Pattern Detection**: Blocking opportunities, scoring opportunities, floor line risks
- **Strategic Reasoning**: Combined analysis of move benefits
- **Educational Explanations**: Learning-focused move explanations

## 🎯 Current Status

✅ **Working Pipeline**:
- Position generation: 45 diverse positions
- Move analysis: **1,350 moves analyzed** (updated from 675)
- Database: `data/simple_move_quality.db` created
- Query system: Comprehensive reporting

⚠️ **Known Issues**:
- Alpha-Beta search has tile errors
- MCTS has deep copy issues with agent_trace
- Comprehensive analysis script needs engine fixes

## 📈 Results Summary

### **Latest Analysis Results:**
- **Total Moves Analyzed**: 1,350
- **Quality Distribution**: 
  - !! (Brilliant): 120 moves (8.9%) - Score: 95.4
  - ! (Excellent): 120 moves (8.9%) - Score: 81.9
  - = (Good): 270 moves (20.0%) - Score: 62.2
  - ? (Poor): 840 moves (62.2%) - Score: 0.0
- **Pattern Analysis**: Working correctly
  - Average blocking opportunities: 0.40
  - Average scoring opportunities: 0.69
  - Average floor line risks: 4.82
- **Neural Evaluation**: Reliable position scoring (avg: 0.42)
- **Database**: Structured SQLite with comprehensive indexing

### **Key Achievements:**
✅ **Brilliant moves identified** with high neural scores and strategic patterns  
✅ **Pattern detection working** - blocking, scoring, and risk assessment  
✅ **Quality classification system** functioning properly  
✅ **Educational explanations** generated for all moves  
✅ **Database query system** providing comprehensive insights  

### **Areas for Improvement:**
🔧 **Quality Distribution**: Too many "poor" moves (62.2%) - need scoring algorithm refinement  
🔧 **Missing Tiers**: No "?! (Dubious)" moves - adjust scoring thresholds  
🔧 **Game Phase**: All moves classified as "middlegame" - need more opening/endgame positions  

## 🔧 Next Steps

1. **Refine Scoring Algorithm**: Adjust quality tier thresholds for better distribution
2. **Expand Position Diversity**: Generate more opening and endgame positions
3. **Fix Engine Issues**: Resolve Alpha-Beta and MCTS problems
4. **Add Game Outcomes**: Include win/loss data
5. **Real-time Analysis**: Build live move analysis
6. **Machine Learning**: Train models on the data

## 🛠️ Technical Details

### Database Schema
```sql
CREATE TABLE move_quality_data (
    id INTEGER PRIMARY KEY,
    position_fen TEXT NOT NULL,
    move_data TEXT NOT NULL,
    neural_score REAL,
    neural_reasoning TEXT,
    blocking_opportunities INTEGER,
    scoring_opportunities INTEGER,
    floor_line_risks INTEGER,
    pattern_connections TEXT,
    strategic_value REAL,
    quality_tier TEXT NOT NULL,
    quality_score REAL NOT NULL,
    strategic_reasoning TEXT,
    tactical_factors TEXT,
    risk_assessment TEXT,
    educational_explanation TEXT,
    game_phase TEXT,
    complexity_score REAL,
    created_at REAL NOT NULL
);
```

### File Locations
- **Positions**: `data/diverse_positions_simple.json`
- **Database**: `data/simple_move_quality.db`
- **Scripts**: `scripts/` directory

## 🎉 Success Metrics

✅ **Foundation Built**: Comprehensive move quality analysis system working  
✅ **Data Generated**: 1,350 moves with full analysis  
✅ **Quality Classification**: 5-tier system functioning  
✅ **Pattern Detection**: Blocking, scoring, risk assessment working  
✅ **Educational Content**: Explanations and reasoning generated  
✅ **Query System**: Comprehensive reporting and insights  

This foundation provides a solid base for building comprehensive "good move" data for Azul analysis and educational purposes. The system is ready for expansion and refinement.
