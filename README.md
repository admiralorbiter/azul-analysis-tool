# Azul Analysis Tool

A comprehensive analysis and training tool for the board game Azul, featuring advanced pattern detection, scoring optimization, and strategic analysis capabilities.

## 🚀 **Quick Start**

### Installation
```bash
git clone <repository-url>
cd azul-analysis-tool
pip install -r requirements.txt
```

### Running the Application
```bash
python start_server.py
```
Then open `http://localhost:8000/ui/` in your browser.

## 🎯 **Key Features**

### **Analysis Tools**
- **Pattern Analysis** - Detect blocking opportunities and strategic patterns
- **Scoring Optimization** - Identify wall completion opportunities and bonuses
- **Floor Line Patterns** - Analyze penalty management and floor line strategies
- **Strategic Analysis** - Evaluate timing, trade-offs, and strategic decisions
- **Move Quality Assessment** - Assess move efficiency and quality with real data integration

### **🆕 NEW: Real Data Integration & Alternative Move Analysis**
- **Base64 FEN Parser** - Robust parsing of encoded game states
- **Real Data Detection** - Intelligent detection of real vs test data
- **Alternative Move Analysis** - Side-by-side comparison of multiple moves
- **Interactive Move Selection** - Clickable move selection with quality indicators
- **Enhanced API Endpoints** - Real data detection and comprehensive move evaluation

### **🆕 NEW: Scalable Position Management**
- **Dynamic Position Loading** - Positions stored in shared JSON database
- **Position Manager Tool** - Easy creation and management of test positions
- **Categorized Positions** - Organized by type and difficulty
- **Version Controlled** - Position database can be version controlled

## 📚 **Position Management**

### List Available Positions
```bash
python tools/position_manager.py list
```

### Add New Test Position
```bash
python tools/position_manager.py add
```

### Show Setup Template
```bash
python tools/position_manager.py template
```

### Position Categories
- **blocking** - Pattern analysis and blocking opportunities
- **scoring-optimization** - Wall completion and bonus opportunities  
- **floor-line** - Floor line penalty management
- **strategic** - Strategic timing and trade-offs
- **move-quality** - Move efficiency and quality assessment

## 🧪 **Testing**

### Available Test Positions
- `simple_blue_blocking` - Basic blocking pattern test
- `high_urgency_red_blocking` - High urgency blocking test
- `high_value_column_completion` - Scoring optimization test
- `simple_row_completion` - Row completion test
- `color_set_completion` - Color set completion test

### Adding Custom Test Positions
```bash
python tools/position_manager.py add
# Follow interactive prompts to create new positions
```

## 🏗️ **Architecture**

### Frontend
- React-based UI with real-time game state management
- Interactive board editing and position library
- Analysis result visualization
- Real data indicators and alternative move analysis

### Backend
- FastAPI-based REST API
- Advanced pattern detection algorithms
- Neural network integration for move evaluation
- Dynamic position loading system
- Enhanced FEN parser with base64 support

### Data Management
- Shared position database (`data/positions.json`)
- Version controlled position definitions
- Scalable position management system
- Real data detection and quality assessment

## 📖 **Documentation**

- [API Documentation](docs/api/)
- [Technical Implementation](docs/technical/)
- [Position Management](docs/technical/position-management.md)
- [Testing Guide](docs/testing/)
- [Move Quality Assessment](docs/move_quality/)

## 🔧 **Development**

### Project Structure
```
azul-analysis-tool/
├── api/                    # Backend API
├── core/                   # Core game logic
├── data/                   # Position database
├── docs/                   # Documentation
├── neural/                 # Neural network components
├── tools/                  # Management tools
├── ui/                     # Frontend components
└── tests/                  # Test suite
```

### Key Components
- **Position Loader** (`api/utils/position_loader.py`) - Dynamic position loading
- **Position Manager** (`tools/position_manager.py`) - Position management tool
- **State Parser** (`api/utils/state_parser.py`) - Game state parsing
- **Analysis APIs** - Pattern detection, scoring optimization, etc.

## 🎮 **Usage Examples**

### Pattern Analysis Testing
1. Load a test position (e.g., `simple_blue_blocking`)
2. Click "Pattern Analysis" button
3. Review detected patterns and blocking opportunities

### Scoring Optimization Testing
1. Load a scoring test position (e.g., `high_value_column_completion`)
2. Click "Scoring Optimization" button
3. Review wall completion opportunities and bonuses

### Adding Custom Positions
1. Run `python tools/position_manager.py add`
2. Follow interactive prompts
3. Restart server to load new positions

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Add test positions using the position manager
4. Test with existing analysis tools
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
