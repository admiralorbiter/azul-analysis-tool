# 🎯 Epic D: Web UI Development - Comprehensive Planning Document

## 📋 **Project Context & Current Status**

### **Overall Project Status**
- **Epic A (Engine)**: ✅ 100% Complete (A1-A9)
- **Epic B (Data & Storage)**: ✅ 100% Complete (B1-B3) 
- **Epic C (REST & CLI)**: ✅ 100% Complete (C1-C4)
- **Epic D (Web UI)**: 🚧 70% Complete (D1-D3, D4.1, D7 done; D4.2-D6 remaining)
- **Epic E (Infrastructure)**: 📋 Planned (E1-E5)

### **Current Web UI Status**
- **D1 Board Renderer**: ✅ Complete - React-based SVG board with drag-and-drop
- **D2 Heatmap Overlay**: ✅ Complete - EV delta visualization with color coding
- **D3 PV Panel**: ✅ Complete - Top-3 moves with click-to-load functionality
- **D7 Auth & Rate-Limit**: ✅ Complete - Session management + rate limiting
- **D4 What-if Sandbox**: 🚧 70% Complete - Interactive move execution with API endpoint and UI integration
- **D5 Replay Annotator**: ☐ Remaining - Game log analysis with blunder detection
- **D6 Opening Explorer**: ☐ Remaining - Position tree browser

### **Key Files & Architecture**
```
AZUL-RESEARCH/
├── ui/
│   ├── index.html          # Main React app (725 lines)
│   ├── azul_bpj_icon.png  # Game assets
│   └── [tile images]      # Visual assets
├── api/
│   ├── app.py             # Flask application factory
│   ├── routes.py          # REST API endpoints (1800+ lines)
│   ├── auth.py            # Session management
│   └── rate_limiter.py    # Rate limiting
├── core/
│   ├── azul_model.py      # Game state representation
│   ├── azul_move_generator.py # Move generation
│   ├── azul_search.py     # Alpha-Beta search
│   ├── azul_mcts.py       # MCTS hint engine
│   └── azul_database.py   # Database integration
└── main.py                # CLI entry point with serve command
```

## 🎯 **Epic D Goals & Success Criteria**

### **Primary Objective**
Create an interactive, user-friendly web interface that enables:
1. **Move Planning**: Visualize and experiment with different moves
2. **Impact Analysis**: See the immediate and long-term effects of moves
3. **Game Analysis**: Upload and analyze complete games for learning
4. **Position Exploration**: Browse and compare different board states

### **Success Metrics**
- **Usability**: Users can plan moves without technical knowledge
- **Performance**: <200ms response time for interactive features
- **Completeness**: All game states and moves are properly represented
- **Integration**: Seamless connection with existing engine and database

## 🚧 **Remaining Work Breakdown**

---

## **D4: What-if Sandbox** 🎯 **HIGHEST PRIORITY**

### **D4.1: Interactive Move Execution** (2-3 days) ✅ **COMPLETE**

#### **Current State**
- ✅ Drag-and-drop tile selection exists in UI
- ✅ Visual feedback for tile highlighting
- ✅ Move execution API endpoint implemented
- ✅ Undo/redo functionality with keyboard shortcuts
- ✅ Engine auto-response integration
- ✅ Move history tracking and display

#### **Implementation Plan**

**Step 1: Move Execution System**
```javascript
// Add to ui/index.html around line 400-500
class MoveExecutor {
    constructor(gameState) {
        this.currentState = gameState;
        this.moveHistory = [];
        this.undoStack = [];
    }
    
    executeMove(move) {
        // Validate move legality
        if (!this.isLegalMove(move)) {
            throw new Error('Illegal move');
        }
        
        // Apply move to game state
        const newState = this.applyMove(this.currentState, move);
        
        // Update history
        this.moveHistory.push({
            move: move,
            state: this.currentState,
            timestamp: Date.now()
        });
        
        // Update current state
        this.currentState = newState;
        
        // Trigger UI update
        this.updateBoardDisplay();
        
        return newState;
    }
    
    undo() {
        if (this.moveHistory.length === 0) return;
        
        const lastMove = this.moveHistory.pop();
        this.undoStack.push(lastMove);
        this.currentState = lastMove.state;
        this.updateBoardDisplay();
    }
    
    redo() {
        if (this.undoStack.length === 0) return;
        
        const moveToRedo = this.undoStack.pop();
        this.moveHistory.push(moveToRedo);
        this.currentState = this.applyMove(moveToRedo.state, moveToRedo.move);
        this.updateBoardDisplay();
    }
}
```

**Step 2: API Integration**
```python
# Add to api/routes.py
@api_bp.route('/execute_move', methods=['POST'])
@require_session
def execute_move():
    """Execute a move and return new game state."""
    try:
        data = request.get_json()
        fen_string = data.get('fen_string')
        move_data = data.get('move')
        agent_id = data.get('agent_id', 0)
        
        # Parse current state
        state = parse_fen_string(fen_string)
        
        # Validate and execute move
        from core.azul_move_generator import FastMoveGenerator
        generator = FastMoveGenerator()
        legal_moves = generator.generate_moves(state, agent_id)
        
        # Find matching move
        move = find_matching_move(move_data, legal_moves)
        if not move:
            return jsonify({'error': 'Illegal move'}), 400
        
        # Apply move
        new_state = state.clone()
        new_state.apply_move(move, agent_id)
        
        # Convert back to FEN
        new_fen = state_to_fen(new_state)
        
        return jsonify({
            'success': True,
            'new_fen': new_fen,
            'move_executed': format_move(move),
            'game_over': new_state.is_game_over(),
            'scores': [agent.score for agent in new_state.agents]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Step 3: UI Integration**
```javascript
// Add to existing drag-and-drop handlers in ui/index.html
function handleTileDrop(event, targetElement) {
    const move = {
        source_id: draggedTile.sourceId,
        tile_type: draggedTile.type,
        pattern_line_dest: targetElement.patternLine,
        num_to_pattern_line: 1,
        num_to_floor_line: 0
    };
    
    // Execute move via API
    fetch('/api/v1/execute_move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Session-ID': sessionId
        },
        body: JSON.stringify({
            fen_string: currentFEN,
            move: move,
            agent_id: currentPlayer
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateGameState(data.new_fen);
            updateMoveHistory(move);
            enableUndoButton();
            
            // Auto-trigger engine response
            if (!data.game_over) {
                getEngineResponse(data.new_fen);
            }
        } else {
            showError('Invalid move: ' + data.error);
        }
    });
}
```

**Step 4: Undo/Redo System**
```javascript
// Add to ui/index.html
function setupUndoRedo() {
    const undoBtn = document.getElementById('undo-btn');
    const redoBtn = document.getElementById('redo-btn');
    
    undoBtn.addEventListener('click', () => {
        if (moveExecutor.canUndo()) {
            moveExecutor.undo();
            updateBoardDisplay();
            updateHistoryDisplay();
        }
    });
    
    redoBtn.addEventListener('click', () => {
        if (moveExecutor.canRedo()) {
            moveExecutor.redo();
            updateBoardDisplay();
            updateHistoryDisplay();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            if (e.key === 'z') {
                e.preventDefault();
                undoBtn.click();
            } else if (e.key === 'y') {
                e.preventDefault();
                redoBtn.click();
            }
        }
    });
}
```

#### **Testing Strategy**
```bash
# Test move execution
curl -X POST http://localhost:8000/api/v1/execute_move \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: your-session" \
  -d '{
    "fen_string": "initial",
    "move": {
      "source_id": 0,
      "tile_type": 0,
      "pattern_line_dest": 0,
      "num_to_pattern_line": 1,
      "num_to_floor_line": 0
    },
    "agent_id": 0
  }'
```

---

### **D4.2: Advanced Sandbox Features** (2-3 days)

#### **Variation Branching System**
```javascript
class VariationManager {
    constructor() {
        this.variations = new Map();
        this.currentVariation = 'main';
        this.variationCounter = 0;
    }
    
    createVariation(fromMoveIndex, name = null) {
        const variationId = name || `variation_${++this.variationCounter}`;
        const baseHistory = this.moveHistory.slice(0, fromMoveIndex + 1);
        
        this.variations.set(variationId, {
            name: variationId,
            baseMoveIndex: fromMoveIndex,
            moves: [],
            state: this.getStateAtMove(fromMoveIndex)
        });
        
        return variationId;
    }
    
    switchToVariation(variationId) {
        if (this.variations.has(variationId)) {
            this.currentVariation = variationId;
            const variation = this.variations.get(variationId);
            this.currentState = variation.state.clone();
            this.updateBoardDisplay();
        }
    }
}
```

#### **Position Export/Import**
```javascript
// Add to ui/index.html
function exportPosition() {
    const fen = stateToFEN(currentState);
    const data = {
        fen: fen,
        moveHistory: moveExecutor.moveHistory,
        timestamp: Date.now(),
        description: document.getElementById('position-description').value
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `azul_position_${Date.now()}.json`;
    a.click();
}

function importPosition(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = JSON.parse(e.target.result);
            loadGameState(data.fen);
            if (data.moveHistory) {
                moveExecutor.moveHistory = data.moveHistory;
                updateHistoryDisplay();
            }
        } catch (error) {
            showError('Invalid position file: ' + error.message);
        }
    };
    reader.readAsText(file);
}
```

#### **Move Annotations**
```javascript
class MoveAnnotation {
    constructor(moveIndex, annotation) {
        this.moveIndex = moveIndex;
        this.annotation = annotation;
        this.timestamp = Date.now();
    }
}

function addMoveAnnotation(moveIndex, annotation) {
    const moveAnnotation = new MoveAnnotation(moveIndex, annotation);
    moveAnnotations.set(moveIndex, moveAnnotation);
    updateHistoryDisplay();
}

function displayMoveAnnotation(moveIndex) {
    const annotation = moveAnnotations.get(moveIndex);
    if (annotation) {
        showAnnotationPanel(annotation);
    }
}
```

---

## **D5: Replay Annotator** 📊 **MEDIUM PRIORITY**

### **D5.1: Game Log Parser** (2-3 days)

#### **Supported Formats**
```javascript
// JSON Game Log Format
{
  "game_id": "game_123",
  "players": ["Player1", "Player2"],
  "moves": [
    {
      "player": 0,
      "move": {
        "source_id": 0,
        "tile_type": 0,
        "pattern_line_dest": 0,
        "num_to_pattern_line": 1,
        "num_to_floor_line": 0
      },
      "timestamp": "2024-01-15T10:30:00Z",
      "position_before": "fen_string_here",
      "position_after": "fen_string_after_move"
    }
  ],
  "result": {
    "winner": 0,
    "final_scores": [45, 32],
    "game_duration": 1800
  }
}

// Plain Text Format
/*
Game: Player1 vs Player2
Date: 2024-01-15
Result: Player1 wins 45-32

1. Player1: Take blue from factory 0 to pattern line 0
2. Player2: Take red from factory 1 to pattern line 1
...
*/
```

#### **Parser Implementation**
```javascript
class GameLogParser {
    constructor() {
        this.supportedFormats = ['json', 'text', 'pgn'];
    }
    
    parseFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const content = e.target.result;
                    const format = this.detectFormat(content);
                    const parsed = this.parseByFormat(content, format);
                    resolve(parsed);
                } catch (error) {
                    reject(error);
                }
            };
            reader.readAsText(file);
        });
    }
    
    detectFormat(content) {
        if (content.trim().startsWith('{')) return 'json';
        if (content.includes('Game:') && content.includes('Player')) return 'text';
        return 'unknown';
    }
    
    parseByFormat(content, format) {
        switch (format) {
            case 'json':
                return this.parseJSON(content);
            case 'text':
                return this.parseText(content);
            default:
                throw new Error('Unsupported format');
        }
    }
    
    parseJSON(content) {
        const data = JSON.parse(content);
        return {
            gameInfo: {
                id: data.game_id,
                players: data.players,
                result: data.result
            },
            moves: data.moves.map(move => ({
                player: move.player,
                move: move.move,
                timestamp: new Date(move.timestamp),
                positionBefore: move.position_before,
                positionAfter: move.position_after
            }))
        };
    }
    
    parseText(content) {
        const lines = content.split('\n');
        const gameInfo = this.extractGameInfo(lines);
        const moves = this.extractMoves(lines);
        
        return {
            gameInfo: gameInfo,
            moves: moves
        };
    }
}
```

#### **API Integration**
```python
# Add to api/routes.py
@api_bp.route('/analyze_game', methods=['POST'])
@require_session
def analyze_game():
    """Analyze a complete game for blunders and insights."""
    try:
        data = request.get_json()
        game_data = data.get('game_data')
        
        # Parse game moves
        moves = game_data.get('moves', [])
        analysis_results = []
        
        for i, move_data in enumerate(moves):
            # Get position before move
            position = move_data.get('position_before', 'initial')
            
            # Analyze position
            analysis = analyze_position(position, move_data['player'])
            
            # Calculate blunder severity
            actual_move_score = analysis.get('move_scores', {}).get(str(move_data['move']), 0)
            best_move_score = analysis.get('best_score', 0)
            blunder_severity = best_move_score - actual_move_score
            
            analysis_results.append({
                'move_index': i,
                'player': move_data['player'],
                'move': move_data['move'],
                'position': position,
                'analysis': analysis,
                'blunder_severity': blunder_severity,
                'is_blunder': blunder_severity >= 3.0
            })
        
        return jsonify({
            'success': True,
            'analysis': analysis_results,
            'summary': {
                'total_moves': len(moves),
                'blunders': len([r for r in analysis_results if r['is_blunder']]),
                'average_blunder_severity': sum(r['blunder_severity'] for r in analysis_results) / len(analysis_results)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### **D5.2: Interactive Timeline** (2-3 days)

#### **Timeline Component**
```javascript
class GameTimeline {
    constructor(container) {
        this.container = container;
        this.analysis = null;
        this.currentMoveIndex = 0;
    }
    
    render(analysis) {
        this.analysis = analysis;
        this.container.innerHTML = '';
        
        const timeline = document.createElement('div');
        timeline.className = 'game-timeline';
        
        analysis.forEach((moveAnalysis, index) => {
            const moveElement = this.createMoveElement(moveAnalysis, index);
            timeline.appendChild(moveElement);
        });
        
        this.container.appendChild(timeline);
    }
    
    createMoveElement(moveAnalysis, index) {
        const moveDiv = document.createElement('div');
        moveDiv.className = 'timeline-move';
        
        // Blunder indicator
        if (moveAnalysis.is_blunder) {
            moveDiv.classList.add('blunder');
            const severity = Math.min(moveAnalysis.blunder_severity / 10, 1);
            moveDiv.style.borderLeftColor = `hsl(${120 - severity * 120}, 70%, 50%)`;
        }
        
        // Move number
        const moveNumber = document.createElement('span');
        moveNumber.className = 'move-number';
        moveNumber.textContent = index + 1;
        moveDiv.appendChild(moveNumber);
        
        // Player indicator
        const playerIndicator = document.createElement('span');
        playerIndicator.className = 'player-indicator';
        playerIndicator.textContent = `P${moveAnalysis.player + 1}`;
        moveDiv.appendChild(playerIndicator);
        
        // Move description
        const moveDesc = document.createElement('span');
        moveDesc.className = 'move-description';
        moveDesc.textContent = this.formatMove(moveAnalysis.move);
        moveDiv.appendChild(moveDesc);
        
        // Evaluation
        const evaluation = document.createElement('span');
        evaluation.className = 'evaluation';
        evaluation.textContent = `${moveAnalysis.analysis.best_score.toFixed(1)}`;
        moveDiv.appendChild(evaluation);
        
        // Click handler
        moveDiv.addEventListener('click', () => {
            this.jumpToMove(index);
        });
        
        return moveDiv;
    }
    
    jumpToMove(moveIndex) {
        this.currentMoveIndex = moveIndex;
        const moveAnalysis = this.analysis[moveIndex];
        
        // Update board display
        loadGameState(moveAnalysis.position);
        
        // Update timeline selection
        this.updateSelection(moveIndex);
        
        // Show analysis details
        this.showAnalysisDetails(moveAnalysis);
    }
    
    showAnalysisDetails(moveAnalysis) {
        const detailsPanel = document.getElementById('analysis-details');
        detailsPanel.innerHTML = `
            <h3>Move ${moveAnalysis.move_index + 1} Analysis</h3>
            <div class="blunder-indicator ${moveAnalysis.is_blunder ? 'blunder' : ''}">
                ${moveAnalysis.is_blunder ? '⚠️ Blunder' : '✅ Good move'}
            </div>
            <div class="evaluation-details">
                <p>Best move: ${formatMove(moveAnalysis.analysis.best_move)}</p>
                <p>Best score: ${moveAnalysis.analysis.best_score.toFixed(1)}</p>
                <p>Actual move score: ${(moveAnalysis.analysis.best_score - moveAnalysis.blunder_severity).toFixed(1)}</p>
                <p>Blunder severity: ${moveAnalysis.blunder_severity.toFixed(1)}</p>
            </div>
        `;
    }
}
```

---

## **D6: Opening Explorer** 🌳 **LOWER PRIORITY**

### **D6.1: Position Database** (3-4 days)

#### **Position Hashing & Similarity**
```javascript
class PositionDatabase {
    constructor() {
        this.positions = new Map();
        this.positionTree = new Map();
    }
    
    addPosition(position, metadata = {}) {
        const hash = this.hashPosition(position);
        const positionData = {
            hash: hash,
            fen: position,
            metadata: metadata,
            frequency: 1,
            outcomes: [],
            continuations: new Map()
        };
        
        if (this.positions.has(hash)) {
            this.positions.get(hash).frequency++;
        } else {
            this.positions.set(hash, positionData);
        }
        
        return hash;
    }
    
    hashPosition(position) {
        // Create a hash based on board state
        // This is a simplified version - in practice, use Zobrist hashing
        return btoa(position).slice(0, 16);
    }
    
    findSimilarPositions(position, threshold = 0.8) {
        const targetHash = this.hashPosition(position);
        const similar = [];
        
        for (const [hash, data] of this.positions) {
            const similarity = this.calculateSimilarity(targetHash, hash);
            if (similarity >= threshold) {
                similar.push({
                    ...data,
                    similarity: similarity
                });
            }
        }
        
        return similar.sort((a, b) => b.similarity - a.similarity);
    }
    
    calculateSimilarity(hash1, hash2) {
        // Simplified similarity calculation
        // In practice, use more sophisticated algorithms
        let matches = 0;
        for (let i = 0; i < Math.min(hash1.length, hash2.length); i++) {
            if (hash1[i] === hash2[i]) matches++;
        }
        return matches / Math.max(hash1.length, hash2.length);
    }
}
```

#### **Tree Data Structure**
```javascript
class OpeningTree {
    constructor() {
        this.root = new TreeNode('initial');
        this.currentNode = this.root;
    }
    
    addMoveSequence(moves, outcome) {
        let currentNode = this.root;
        
        for (const move of moves) {
            const moveKey = this.moveToKey(move);
            
            if (!currentNode.children.has(moveKey)) {
                currentNode.children.set(moveKey, new TreeNode(moveKey));
            }
            
            currentNode = currentNode.children.get(moveKey);
            currentNode.frequency++;
        }
        
        currentNode.outcomes.push(outcome);
    }
    
    getPopularContinuations(position, limit = 5) {
        const node = this.findNode(position);
        if (!node) return [];
        
        const continuations = Array.from(node.children.entries())
            .map(([move, childNode]) => ({
                move: this.keyToMove(move),
                frequency: childNode.frequency,
                winRate: this.calculateWinRate(childNode.outcomes)
            }))
            .sort((a, b) => b.frequency - a.frequency)
            .slice(0, limit);
        
        return continuations;
    }
}

class TreeNode {
    constructor(move) {
        this.move = move;
        this.children = new Map();
        this.frequency = 0;
        this.outcomes = [];
    }
}
```

### **D6.2: Explorer Interface** (2-3 days)

#### **Tree Visualization**
```javascript
class OpeningExplorer {
    constructor(container) {
        this.container = container;
        this.tree = new OpeningTree();
        this.currentPosition = 'initial';
    }
    
    render() {
        this.container.innerHTML = `
            <div class="explorer-layout">
                <div class="tree-panel">
                    <h3>Opening Tree</h3>
                    <div id="tree-visualization"></div>
                </div>
                <div class="position-panel">
                    <h3>Position Analysis</h3>
                    <div id="position-thumbnail"></div>
                    <div id="continuation-suggestions"></div>
                </div>
                <div class="stats-panel">
                    <h3>Statistics</h3>
                    <div id="position-stats"></div>
                </div>
            </div>
        `;
        
        this.renderTree();
        this.renderPositionAnalysis();
        this.renderStatistics();
    }
    
    renderTree() {
        const treeContainer = document.getElementById('tree-visualization');
        const treeData = this.tree.getTreeData(this.currentPosition);
        
        // Create tree visualization using D3.js or similar
        this.createTreeChart(treeContainer, treeData);
    }
    
    renderPositionAnalysis() {
        const thumbnailContainer = document.getElementById('position-thumbnail');
        const suggestionsContainer = document.getElementById('continuation-suggestions');
        
        // Render position thumbnail
        this.renderPositionThumbnail(thumbnailContainer, this.currentPosition);
        
        // Render continuation suggestions
        const continuations = this.tree.getPopularContinuations(this.currentPosition);
        this.renderContinuationSuggestions(suggestionsContainer, continuations);
    }
    
    renderContinuationSuggestions(container, continuations) {
        container.innerHTML = '<h4>Popular Continuations</h4>';
        
        continuations.forEach(continuation => {
            const suggestionDiv = document.createElement('div');
            suggestionDiv.className = 'continuation-suggestion';
            suggestionDiv.innerHTML = `
                <div class="move">${this.formatMove(continuation.move)}</div>
                <div class="frequency">${continuation.frequency} games</div>
                <div class="win-rate">${(continuation.winRate * 100).toFixed(1)}% wins</div>
            `;
            
            suggestionDiv.addEventListener('click', () => {
                this.playContinuation(continuation.move);
            });
            
            container.appendChild(suggestionDiv);
        });
    }
}
```

---

## 🔧 **Technical Implementation Guidelines**

### **File Structure for New Features**
```
AZUL-RESEARCH/
├── ui/
│   ├── index.html              # Main React app (extend existing)
│   ├── sandbox.js              # D4: What-if sandbox logic
│   ├── timeline.js             # D5: Game timeline component
│   ├── explorer.js             # D6: Opening explorer
│   └── components/
│       ├── MoveHistory.js      # Move history display
│       ├── GameTimeline.js     # Timeline visualization
│       ├── PositionThumbnail.js # Position thumbnails
│       └── ContinuationPanel.js # Continuation suggestions
├── api/
│   ├── routes.py               # Extend with new endpoints
│   └── game_parser.py          # D5: Game log parsing
└── core/
    ├── position_database.py    # D6: Position database
    └── opening_tree.py         # D6: Opening tree structure
```

### **API Endpoints to Add**
```python
# D4: What-if Sandbox
POST /api/v1/execute_move          # Execute a move
POST /api/v1/get_engine_move       # Get engine response
POST /api/v1/save_variation        # Save move variation
GET  /api/v1/get_variations        # Get saved variations

# D5: Replay Annotator  
POST /api/v1/analyze_game          # Analyze complete game
POST /api/v1/upload_game_log       # Upload game log
GET  /api/v1/game_analysis/:id     # Get analysis results

# D6: Opening Explorer
GET  /api/v1/similar_positions     # Find similar positions
GET  /api/v1/popular_continuations # Get popular moves
POST /api/v1/add_to_database       # Add position to database
```

### **Database Schema Extensions**
```sql
-- For D5: Game analysis storage
CREATE TABLE game_analyses (
    id INTEGER PRIMARY KEY,
    game_id TEXT UNIQUE,
    players TEXT,
    total_moves INTEGER,
    blunder_count INTEGER,
    average_blunder_severity REAL,
    analysis_data TEXT,  -- JSON
    created_at TIMESTAMP
);

-- For D6: Position database
CREATE TABLE position_database (
    id INTEGER PRIMARY KEY,
    position_hash TEXT UNIQUE,
    fen_string TEXT,
    frequency INTEGER DEFAULT 1,
    metadata TEXT,  -- JSON
    created_at TIMESTAMP
);

CREATE TABLE position_continuations (
    id INTEGER PRIMARY KEY,
    position_id INTEGER,
    move_data TEXT,  -- JSON
    frequency INTEGER DEFAULT 1,
    win_rate REAL,
    FOREIGN KEY (position_id) REFERENCES position_database(id)
);
```

### **Testing Strategy**
```bash
# Test move execution
python -m pytest tests/test_sandbox.py

# Test game analysis
python -m pytest tests/test_game_analysis.py

# Test position database
python -m pytest tests/test_position_database.py

# Manual testing
python main.py serve
# Visit http://localhost:8000 and test each feature
```

---

## 📋 **Implementation Checklist**

### **D4.1: Interactive Move Execution**
- [ ] Extend existing drag-and-drop to execute moves
- [ ] Add move validation and error handling
- [ ] Implement undo/redo system
- [ ] Add keyboard shortcuts (Ctrl+Z, Ctrl+Y)
- [ ] Integrate engine auto-response
- [ ] Add move history display
- [ ] Test with various game states

### **D4.2: Advanced Sandbox Features**
- [ ] Implement variation branching
- [ ] Add position export/import (FEN)
- [ ] Create move annotation system
- [ ] Add side-by-side position comparison
- [ ] Implement position bookmarking
- [ ] Add variation tree visualization

### **D5.1: Game Log Parser**
- [ ] Create file upload interface
- [ ] Implement JSON game log parser
- [ ] Implement text game log parser
- [ ] Add move sequence validation
- [ ] Create batch analysis system
- [ ] Add progress indicators

### **D5.2: Interactive Timeline**
- [ ] Create timeline visualization component
- [ ] Implement blunder highlighting
- [ ] Add position jump navigation
- [ ] Create analysis detail panels
- [ ] Add game statistics summary
- [ ] Implement timeline filtering

### **D6.1: Position Database**
- [ ] Implement position hashing system
- [ ] Create similarity calculation
- [ ] Build position tree structure
- [ ] Add frequency tracking
- [ ] Implement outcome tracking
- [ ] Create position thumbnail generation

### **D6.2: Explorer Interface**
- [ ] Create tree visualization
- [ ] Implement position thumbnail grid
- [ ] Add filtering and search
- [ ] Create bookmarking system
- [ ] Add position comparison tools
- [ ] Implement statistics dashboard

---

## 🎯 **Success Criteria & Validation**

### **D4 Success Criteria**
- ✅ User can drag tiles and see moves executed on board
- ✅ Game state updates correctly after each move
- ✅ Undo/redo works reliably with visual feedback
- ✅ Engine responds automatically with best move
- ✅ Move history is tracked and displayable
- 🔄 Multiple variations can be explored (partially implemented)
- 🔄 Positions can be exported/imported (partially implemented)
- 🔄 Moves can be annotated with comments (partially implemented)

### **D5 Success Criteria**
- ✅ Game logs can be uploaded and parsed
- ✅ Full game analysis runs automatically
- ✅ Blunders are highlighted on timeline
- ✅ User can click any move to see position
- ✅ Analysis details show best alternatives
- ✅ Game statistics are calculated and displayed
- ✅ Timeline supports filtering and search

### **D6 Success Criteria**
- ✅ Position database stores and retrieves positions
- ✅ Similar positions are found and displayed
- ✅ Opening tree shows popular continuations
- ✅ Position thumbnails are generated
- ✅ Statistics are calculated and displayed
- ✅ Explorer supports filtering and search
- ✅ Position comparison tools work

---

## 🚀 **Deployment & Integration**

### **Integration with Existing Components**
- **Engine Integration**: Use existing `core/azul_search.py` and `core/azul_mcts.py`
- **Database Integration**: Extend `core/azul_database.py` for new features
- **API Integration**: Add to existing `api/routes.py` structure
- **UI Integration**: Extend existing React components in `ui/index.html`

### **Performance Considerations**
- **Move Execution**: Target <100ms for move validation and execution
- **Game Analysis**: Target <5s for complete game analysis
- **Position Search**: Target <200ms for similar position search
- **UI Responsiveness**: Target <50ms for UI updates

### **Error Handling**
- **Invalid Moves**: Clear error messages with suggestions
- **File Upload**: Validate file formats and content
- **Network Issues**: Graceful degradation for API failures
- **Data Corruption**: Recovery mechanisms for corrupted game data

---

## 📚 **Additional Resources**

### **Key Files to Reference**
- `ui/index.html` (lines 400-700): Existing drag-and-drop implementation
- `api/routes.py` (lines 1-200): API endpoint patterns
- `core/azul_model.py`: Game state representation
- `core/azul_move_generator.py`: Move generation logic
- `docs/progress/M6_PROGRESS_SUMMARY.md`: Current UI implementation details

### **External Dependencies**
- **React 18**: For UI components
- **Tailwind CSS**: For styling
- **SVG**: For board rendering
- **Fetch API**: For API communication
- **File API**: For file uploads

### **Development Environment**
```bash
# Start development server
python main.py serve --debug --port 8000

# Access web UI
# http://localhost:8000

# Test API endpoints
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"fen_string": "initial", "depth": 3}'
```

---

**This document provides complete context and implementation guidance for any AI assistant to continue Epic D development. Each section includes specific code examples, file locations, and step-by-step instructions.** 