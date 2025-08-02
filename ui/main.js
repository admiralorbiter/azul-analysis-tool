// Main entry point for the React app
// Using global React and ReactDOM from CDN

const { createRoot } = ReactDOM;

// Debug component loading
console.log('Component loading status:', {
    AdvancedAnalysisControls: !!window.AdvancedAnalysisControls,
    ConfigurationPanel: !!window.ConfigurationPanel,
    DevelopmentToolsPanel: !!window.DevelopmentToolsPanel,
    TrainingConfigPanel: !!window.TrainingConfigPanel
});

// Import components from extracted modules with fallbacks
const {
    AdvancedAnalysisControls,
    ConfigurationPanel,
    DevelopmentToolsPanel,
    TrainingConfigPanel,
    TrainingMonitor,
    TrainingHistoryComponent,
    NeuralTrainingPage,
    Router,
    Navigation,
    Tile,
    Factory,
    PatternLine,
    StatusMessage,
    MoveOption,
    ContextMenu,
    Wall,
    PlayerBoard
} = {
    AdvancedAnalysisControls: window.AdvancedAnalysisControls || (() => React.createElement('div', null, 'AdvancedAnalysisControls not loaded')),
    ConfigurationPanel: window.ConfigurationPanel || (() => React.createElement('div', null, 'ConfigurationPanel not loaded')),
    DevelopmentToolsPanel: window.DevelopmentToolsPanel || (() => React.createElement('div', null, 'DevelopmentToolsPanel not loaded')),
    TrainingConfigPanel: window.TrainingConfigPanel || (() => React.createElement('div', null, 'TrainingConfigPanel not loaded')),
    TrainingMonitor: window.TrainingMonitor || (() => React.createElement('div', null, 'TrainingMonitor not loaded')),
    TrainingHistoryComponent: window.TrainingHistoryComponent || (() => React.createElement('div', null, 'TrainingHistoryComponent not loaded')),
    NeuralTrainingPage: window.NeuralTrainingPage || (() => React.createElement('div', null, 'NeuralTrainingPage not loaded')),
    Router: window.Router || (() => React.createElement('div', null, 'Router not loaded')),
    Navigation: window.Navigation || (() => React.createElement('div', null, 'Navigation not loaded')),
    Tile: window.Tile || (() => React.createElement('div', null, 'Tile not loaded')),
    Factory: window.Factory || (() => React.createElement('div', null, 'Factory not loaded')),
    PatternLine: window.PatternLine || (() => React.createElement('div', null, 'PatternLine not loaded')),
    StatusMessage: window.StatusMessage || (() => React.createElement('div', null, 'StatusMessage not loaded')),
    MoveOption: window.MoveOption || (() => React.createElement('div', null, 'MoveOption not loaded')),
    ContextMenu: window.ContextMenu || (() => React.createElement('div', null, 'ContextMenu not loaded')),
    Wall: window.Wall || (() => React.createElement('div', null, 'Wall not loaded')),
    PlayerBoard: window.PlayerBoard || (() => React.createElement('div', null, 'PlayerBoard not loaded'))
};

// Import utility functions (these will be defined inline)
// Use shared API constants - no need to redeclare since we're importing from modules
let sessionId = null;

// Router and Navigation components extracted to separate files



// API functions - No session required for local development
// Import game API functions from external module
const {
    initializeSession,
    analyzePosition,
    getHint,
    analyzeNeural,
    analyzeGame
} = window.gameAPI || {};

// Import neural API functions from external module
const {
    startNeuralTraining,
    getNeuralTrainingStatus,
    getNeuralTrainingProgress,
    getNeuralTrainingLogs,
    getAllTrainingSessions,
    deleteTrainingSession,
    stopNeuralTraining,
    evaluateNeuralModel,
    getEvaluationStatus,
    getAllEvaluationSessions,
    deleteEvaluationSession,
    getAvailableModels
} = window.neuralAPI || {};

// Import additional neural API functions
const {
    getNeuralConfig,
    saveNeuralConfig
} = window.neuralAPI || {};

// Import additional game API functions
const {
    getGameState,
    saveGameState
} = window.gameAPI || {};

// Import additional neural API functions
const {
    getTrainingHistory,
    getNeuralConfigurations,
    saveNeuralConfiguration,
    updateNeuralConfiguration,
    deleteNeuralConfiguration
} = window.neuralAPI || {};

// Import utility functions from modules
const {
    generateHeatmapData,
    getHeatmapColor
} = window.heatmapUtils || {};

const {
    getTileColor,
    formatMoveDescription,
    formatSelectedElement,
    getMenuOptions
} = window.formatUtils || {};

// Tile Component
// Tile component extracted to separate file

// Factory component extracted to separate file

// Import executeMove function from game API
const { executeMove } = window.gameAPI || {};

// PatternLine component extracted to separate file

// Wall Component - Extracted to separate file

// PlayerBoard Component - Extracted to separate file

// StatusMessage Component - Extracted to separate file

// MoveOption Component - Extracted to separate file

// ContextMenu Component - Extracted to separate file

// AdvancedAnalysisControls Component - Extracted to separate file

// ConfigurationPanel Component - Extracted to separate file

// DevelopmentToolsPanel Component - Extracted to separate file

// Main App Component
function App() {
    // Routing State
    const [currentPage, setCurrentPage] = React.useState('main');
    
    // State declarations
    const [sessionStatus, setSessionStatus] = React.useState('connecting');
    const [statusMessage, setStatusMessage] = React.useState('Initializing...');
    const [loading, setLoading] = React.useState(false);
    const [gameState, setGameState] = React.useState(null);
    const [selectedTile, setSelectedTile] = React.useState(null);
    const [editMode, setEditMode] = React.useState(false);
    const [selectedElements, setSelectedElements] = React.useState([]); // Array of selected elements
    const [clipboard, setClipboard] = React.useState(null); // For copy/paste
    const [editHints, setEditHints] = React.useState(true); // Show keyboard hints
    const [contextMenu, setContextMenu] = React.useState({ visible: false, x: 0, y: 0, options: [] });
    const [variations, setVariations] = React.useState([]);
    const [moveAnnotations, setMoveAnnotations] = React.useState({});
    const [moveHistory, setMoveHistory] = React.useState([]);
    const [currentPlayer, setCurrentPlayer] = React.useState(0);
    const [engineThinking, setEngineThinking] = React.useState(false);
    const [heatmapEnabled, setHeatmapEnabled] = React.useState(false);
    const [heatmapData, setHeatmapData] = React.useState(null);
    const [analysisExpanded, setAnalysisExpanded] = React.useState(true); // New state for analysis panel expansion
    const [advancedExpanded, setAdvancedExpanded] = React.useState(true); // New state for advanced tools expansion
    
    // Advanced Analysis Controls State
    const [depth, setDepth] = React.useState(3);
    const [timeBudget, setTimeBudget] = React.useState(4.0);
    const [rollouts, setRollouts] = React.useState(100);
    const [agentId, setAgentId] = React.useState(0);
    
    // Configuration Panel State
    const [databasePath, setDatabasePath] = React.useState('azul_cache.db');
    const [modelPath, setModelPath] = React.useState('models/azul_net_small.pth');
    const [defaultTimeout, setDefaultTimeout] = React.useState(4.0);
    const [defaultDepth, setDefaultDepth] = React.useState(3);
    const [defaultRollouts, setDefaultRollouts] = React.useState(100);
    const [configExpanded, setConfigExpanded] = React.useState(false);
    
    // Development Tools Panel State
    const [devToolsExpanded, setDevToolsExpanded] = React.useState(false);
    
    // Neural Training State
    const [neuralExpanded, setNeuralExpanded] = React.useState(false);
    const [trainingConfig, setTrainingConfig] = React.useState({
        modelSize: 'small',
        device: 'cpu',
        epochs: 5,
        samples: 500,
        batchSize: 16,
        learningRate: 0.001
    });
    
    // Initialize session
    React.useEffect(() => {
        initializeSession()
            .then(() => {
                setSessionStatus('connected');
                setStatusMessage('Connected to server');
                return getGameState();
            })
            .then(data => {
                console.log('Initial game state:', data);
                setGameState(data);
                setStatusMessage('Game loaded');
            })
            .catch(error => {
                setSessionStatus('error');
                setStatusMessage(`Connection failed: ${error.message}`);
            });
    }, []);
    
    // Refresh game state periodically to stay in sync (but not during edit mode)
    React.useEffect(() => {
        const interval = setInterval(() => {
            if (sessionStatus === 'connected' && !loading && !editMode) {
                getGameState().then(data => {
                    setGameState(data);
                }).catch(error => {
                    console.error('Failed to refresh game state:', error);
                });
            }
        }, 5000); // Refresh every 5 seconds
        
        return () => clearInterval(interval);
    }, [sessionStatus, loading, editMode]);
    
    // Clear selection function
    const clearSelection = React.useCallback(() => {
        setSelectedTile(null);
        setSelectedElements([]);
        setStatusMessage('Selection cleared');
    }, []);
    
    // Edit mode functions
    const handleEditModeToggle = React.useCallback(() => {
        const newEditMode = !editMode;
        setEditMode(newEditMode);
        
        if (newEditMode) {
            setStatusMessage('Edit mode enabled. Click tiles to select, use 1-5 for colors, Delete to remove.');
            setSelectedElements([]);
        } else {
            setStatusMessage('Edit mode disabled.');
            setSelectedElements([]);
            setClipboard(null);
        }
    }, [editMode]);

    // Handle element selection in edit mode
    const handleElementSelect = React.useCallback((element, isCtrlClick = false) => {
        if (!editMode) return;

        const elementId = `${element.type}_${element.data.factoryIndex || element.data.playerIndex || 0}_${element.data.rowIndex || 0}_${element.data.colIndex || element.data.tileIndex || 0}`;
        
        setSelectedElements(prev => {
            if (isCtrlClick) {
                // Multi-select with Ctrl+click
                const isAlreadySelected = prev.some(el => el.id === elementId);
                if (isAlreadySelected) {
                    return prev.filter(el => el.id !== elementId);
                } else {
                    return [...prev, { ...element, id: elementId }];
                }
            } else {
                // Single select
                return [{ ...element, id: elementId }];
            }
        });

        const count = isCtrlClick ? 'multiple' : '1';
        setStatusMessage(`Selected ${count} element(s). Use 1-5 for colors, Delete to remove, Ctrl+C/V to copy/paste.`);
    }, [editMode]);

    // Apply tile color to selected elements
    const applyTileColor = React.useCallback((colorKey) => {
        if (!editMode || selectedElements.length === 0) return;

        const colorMap = { '1': 'B', '2': 'Y', '3': 'R', '4': 'K', '5': 'W' };
        const color = colorMap[colorKey];
        
        if (!color) return;

        console.log(`Applying ${color} tiles to:`, selectedElements);
        
        // Create a deep copy of the game state to modify
        const newGameState = JSON.parse(JSON.stringify(gameState));
        
        selectedElements.forEach(element => {
            if (element.type === 'factory') {
                // Add tile to factory
                const factoryIndex = element.data.factoryIndex;
                if (newGameState.factories && newGameState.factories[factoryIndex]) {
                    newGameState.factories[factoryIndex].push(color);
                }
            } else if (element.type === 'pattern-line') {
                // Add tile to pattern line
                const { playerIndex, rowIndex } = element.data;
                if (newGameState.players && newGameState.players[playerIndex]) {
                    const player = newGameState.players[playerIndex];
                    if (player.pattern_lines && player.pattern_lines[rowIndex]) {
                        player.pattern_lines[rowIndex].push(color);
                    }
                }
            } else if (element.type === 'wall-cell') {
                // Place tile on wall
                const { playerIndex, rowIndex, colIndex } = element.data;
                if (newGameState.players && newGameState.players[playerIndex]) {
                    const player = newGameState.players[playerIndex];
                    if (player.wall && player.wall[rowIndex] && player.wall[rowIndex][colIndex] === null) {
                        player.wall[rowIndex][colIndex] = color;
                    }
                }
            }
        });
        
        // Update the game state
        setGameState(newGameState);
        setStatusMessage(`Applied ${color} tiles to ${selectedElements.length} location(s)`);
        
        // Save the updated state to the server
        saveGameState(newGameState).then(() => {
            setStatusMessage(`Applied ${color} tiles to ${selectedElements.length} location(s) - Saved to server`);
        }).catch(error => {
            console.error('Failed to save game state:', error);
            setStatusMessage(`Applied ${color} tiles but failed to save to server`);
        });
        
        // Clear selection after applying
        setSelectedElements([]);
    }, [editMode, selectedElements, gameState]);

    // Remove tiles from selected elements
    const removeSelectedTiles = React.useCallback(() => {
        if (!editMode || selectedElements.length === 0) return;

        console.log('Removing tiles from:', selectedElements);
        
        // Create a deep copy of the game state to modify
        const newGameState = JSON.parse(JSON.stringify(gameState));
        
        selectedElements.forEach(element => {
            if (element.type === 'factory') {
                // Remove all tiles from factory
                const factoryIndex = element.data.factoryIndex;
                if (newGameState.factories && newGameState.factories[factoryIndex]) {
                    newGameState.factories[factoryIndex] = [];
                }
            } else if (element.type === 'pattern-line') {
                // Remove all tiles from pattern line
                const { playerIndex, rowIndex } = element.data;
                if (newGameState.players && newGameState.players[playerIndex]) {
                    const player = newGameState.players[playerIndex];
                    if (player.pattern_lines && player.pattern_lines[rowIndex]) {
                        player.pattern_lines[rowIndex] = [];
                    }
                }
            } else if (element.type === 'wall-cell') {
                // Remove tile from wall
                const { playerIndex, rowIndex, colIndex } = element.data;
                if (newGameState.players && newGameState.players[playerIndex]) {
                    const player = newGameState.players[playerIndex];
                    if (player.wall && player.wall[rowIndex] && player.wall[rowIndex][colIndex] !== null) {
                        player.wall[rowIndex][colIndex] = null;
                    }
                }
            }
        });
        
        // Update the game state
        setGameState(newGameState);
        setStatusMessage(`Removed tiles from ${selectedElements.length} location(s)`);
        
        // Save the updated state to the server
        saveGameState(newGameState).then(() => {
            setStatusMessage(`Removed tiles from ${selectedElements.length} location(s) - Saved to server`);
        }).catch(error => {
            console.error('Failed to save game state:', error);
            setStatusMessage(`Removed tiles but failed to save to server`);
        });
        
        // Clear selection after removing
        setSelectedElements([]);
    }, [editMode, selectedElements, gameState]);

    // Copy selected elements
    const copySelection = React.useCallback(() => {
        if (!editMode || selectedElements.length === 0) return;

        setClipboard([...selectedElements]);
        setStatusMessage(`Copied ${selectedElements.length} element(s) to clipboard`);
    }, [editMode, selectedElements]);

    // Paste clipboard to selected location
    const pasteSelection = React.useCallback(() => {
        if (!editMode || !clipboard || selectedElements.length !== 1) {
            setStatusMessage('Select exactly one location to paste to');
            return;
        }

        console.log('Pasting from clipboard:', clipboard, 'to:', selectedElements[0]);
        
        // Create a deep copy of the game state to modify
        const newGameState = JSON.parse(JSON.stringify(gameState));
        const targetElement = selectedElements[0];
        
        clipboard.forEach(element => {
            if (element.type === 'factory' && targetElement.type === 'factory') {
                // Copy tiles from source factory to target factory
                const sourceFactoryIndex = element.data.factoryIndex;
                const targetFactoryIndex = targetElement.data.factoryIndex;
                
                if (newGameState.factories && newGameState.factories[sourceFactoryIndex]) {
                    const tilesToCopy = [...newGameState.factories[sourceFactoryIndex]];
                    newGameState.factories[targetFactoryIndex] = tilesToCopy;
                }
            } else if (element.type === 'pattern-line' && targetElement.type === 'pattern-line') {
                // Copy tiles from source pattern line to target pattern line
                const sourcePlayerIndex = element.data.playerIndex;
                const sourceRowIndex = element.data.rowIndex;
                const targetPlayerIndex = targetElement.data.playerIndex;
                const targetRowIndex = targetElement.data.rowIndex;
                
                if (newGameState.players && newGameState.players[sourcePlayerIndex] && newGameState.players[targetPlayerIndex]) {
                    const sourcePlayer = newGameState.players[sourcePlayerIndex];
                    const targetPlayer = newGameState.players[targetPlayerIndex];
                    
                    if (sourcePlayer.pattern_lines && sourcePlayer.pattern_lines[sourceRowIndex]) {
                        const tilesToCopy = [...sourcePlayer.pattern_lines[sourceRowIndex]];
                        targetPlayer.pattern_lines[targetRowIndex] = tilesToCopy;
                    }
                }
            }
        });
        
        // Update the game state
        setGameState(newGameState);
        setStatusMessage(`Pasted ${clipboard.length} element(s)`);
        
        // Save the updated state to the server
        saveGameState(newGameState).then(() => {
            setStatusMessage(`Pasted ${clipboard.length} element(s) - Saved to server`);
        }).catch(error => {
            console.error('Failed to save game state:', error);
            setStatusMessage(`Pasted elements but failed to save to server`);
        });
        
        setSelectedElements([]);
    }, [editMode, clipboard, selectedElements, gameState]);
    
    // Handle move execution
    const handleMoveExecution = React.useCallback(async (move) => {
        if (!gameState) return;
        
        setLoading(true);
        setStatusMessage('Executing move...');
        
        try {
            const result = await executeMove(gameState.fen_string || 'initial', move, currentPlayer);
            
            if (result.success) {
                // Update game state with new FEN
                const newGameState = await getGameState(result.new_fen);
                setGameState(newGameState);
                
                // Add to move history
                setMoveHistory(prev => [...prev, {
                    move: move,
                    result: result,
                    timestamp: Date.now(),
                    player: currentPlayer
                }]);
                
                setStatusMessage(`Move executed: ${result.move_executed}`);
                
                // Clear selection
                setSelectedTile(null);
                
                // Handle engine response
                if (result.engine_response && !result.game_over) {
                    setEngineThinking(true);
                    setStatusMessage(`Engine thinking... Best move: ${result.engine_response.move}`);
                    
                    // Auto-advance to next player or apply engine move
                    setTimeout(() => {
                        setEngineThinking(false);
                        setCurrentPlayer(prev => (prev + 1) % (gameState.players?.length || 2));
                    }, 1000);
                }
                
                if (result.game_over) {
                    setStatusMessage(`Game Over! Final scores: ${result.scores.join(', ')}`);
                }
            } else {
                console.error('Move failed:', result);
                setStatusMessage(`Move failed: ${result.error || 'Unknown error'}`);
                
                // Reset game state to ensure consistency
                getGameState().then(freshState => {
                    setGameState(freshState);
                    console.log('Game state refreshed after failed move');
                });
            }
        } catch (error) {
            setStatusMessage(`Error executing move: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [gameState, currentPlayer]);
    
    // Helper function to convert tile color to type
    const getTileType = React.useCallback((tileColor) => {
        const mapping = { 'B': 0, 'Y': 1, 'R': 2, 'K': 3, 'W': 4 };
        return mapping[tileColor] !== undefined ? mapping[tileColor] : 0;
    }, []);
    
    // Handle pattern line drop
    const handlePatternLineDrop = React.useCallback((e, rowIndex) => {
        e.preventDefault();
        
        try {
            const dragData = JSON.parse(e.dataTransfer.getData('application/json'));
            console.log('Drop data received:', dragData);
            
            if (dragData.sourceType === 'factory') {
                // Validate that the factory still has this tile
                const factory = gameState?.factories?.[dragData.sourceId];
                if (!factory) {
                    setStatusMessage(`Factory ${dragData.sourceId} not found`);
                    return;
                }
                
                // Check if the tile exists in the factory
                const tileExists = factory.includes(dragData.tile);
                if (!tileExists) {
                    setStatusMessage(`Tile ${dragData.tile} not found in factory ${dragData.sourceId}`);
                    console.log('Available tiles in factory:', factory);
                    return;
                }
                
                const tileType = getTileType(dragData.tile);
                
                // Count how many tiles of this color are in the factory
                const tilesOfColor = factory.filter(tile => tile === dragData.tile).length;
                
                // In Azul, you take ALL tiles of the chosen color
                // Check current pattern line state
                const activePlayer = gameState?.players?.[currentPlayer];
                const currentPatternLine = activePlayer?.pattern_lines?.[rowIndex] || [];
                const maxPatternLineCapacity = rowIndex + 1; // Pattern line 0 holds 1, line 1 holds 2, etc.
                const currentTilesInLine = currentPatternLine.length;
                const availableSpace = maxPatternLineCapacity - currentTilesInLine;
                
                // Determine how many go to pattern line vs floor line
                const tilesToPattern = Math.min(tilesOfColor, availableSpace);
                const tilesToFloor = tilesOfColor - tilesToPattern;
                
                // Validate the move makes sense
                if (availableSpace <= 0) {
                    setStatusMessage(`Pattern line ${rowIndex} is already full!`);
                    return;
                }
                
                if (tilesOfColor === 0) {
                    setStatusMessage(`No ${dragData.tile} tiles found in factory ${dragData.sourceId}`);
                    return;
                }
                
                // Check if pattern line already has different colored tiles
                if (currentTilesInLine > 0) {
                    const existingTileColor = currentPatternLine[0];
                    if (existingTileColor !== dragData.tile) {
                        setStatusMessage(`Pattern line ${rowIndex} already contains ${existingTileColor} tiles!`);
                        return;
                    }
                }
                
                const move = {
                    source_id: dragData.sourceId,
                    tile_type: tileType,
                    pattern_line_dest: rowIndex,
                    num_to_pattern_line: tilesToPattern,
                    num_to_floor_line: tilesToFloor
                };
                
                console.log('=== MOVE DEBUG ===');
                console.log(`Factory ${dragData.sourceId} contents:`, factory);
                console.log(`Taking ${tilesOfColor} ${dragData.tile} tiles (type ${tileType})`);
                console.log(`Pattern line ${rowIndex}: ${currentTilesInLine}/${maxPatternLineCapacity} tiles`);
                console.log(`Available space: ${availableSpace}`);
                console.log(`Distribution: ${tilesToPattern} to pattern line, ${tilesToFloor} to floor`);
                console.log('Move object:', move);
                console.log('==================');
                
                setStatusMessage(`Taking ${tilesOfColor} ${dragData.tile} tiles: ${tilesToPattern} to pattern line, ${tilesToFloor} to floor`);
                handleMoveExecution(move);
            }
        } catch (error) {
            console.error('Drop error:', error);
            setStatusMessage(`Invalid drop data: ${error.message}`);
        }
    }, [handleMoveExecution, gameState, getTileType]);
    
    // Position export/import functions
    const exportPosition = React.useCallback(() => {
        if (!gameState) return;
        
        const exportData = {
            fen: gameState.fen_string || 'initial',
            moveHistory: moveHistory,
            currentPlayer: currentPlayer,
            timestamp: Date.now(),
            description: `Azul position - ${moveHistory.length} moves`,
            metadata: {
                scores: gameState.players?.map(p => p.score) || [],
                gameMode: 'sandbox'
            }
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `azul_position_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        setStatusMessage('Position exported successfully');
    }, [gameState, moveHistory, currentPlayer]);
    
    const importPosition = React.useCallback((file) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const data = JSON.parse(e.target.result);
                
                // Load the game state from FEN
                getGameState(data.fen).then(newGameState => {
                    setGameState(newGameState);
                    
                    // Restore move history if available
                    if (data.moveHistory) {
                        setMoveHistory(data.moveHistory);
                    }
                    
                    // Restore current player if available
                    if (data.currentPlayer !== undefined) {
                        setCurrentPlayer(data.currentPlayer);
                    }
                    
                    setStatusMessage(`Position imported: ${data.description || 'Unknown position'}`);
                }).catch(error => {
                    setStatusMessage(`Failed to load imported position: ${error.message}`);
                });
            } catch (error) {
                setStatusMessage(`Invalid position file: ${error.message}`);
            }
        };
        reader.readAsText(file);
    }, []);
    
    const handleFileImport = React.useCallback((e) => {
        const file = e.target.files[0];
        if (file) {
            importPosition(file);
        }
        // Reset the input value so the same file can be selected again
        e.target.value = '';
    }, [importPosition]);
    
    // Context menu functions
    const showContextMenu = React.useCallback((e, elementType, elementData) => {
        e.preventDefault();
        const options = getMenuOptions(elementType, elementData);
        setContextMenu({
            visible: true,
            x: e.clientX,
            y: e.clientY,
            options: options
        });
    }, []);
    
    const hideContextMenu = React.useCallback(() => {
        setContextMenu({ visible: false, x: 0, y: 0, options: [] });
    }, []);
    
    const handleContextMenuAction = React.useCallback((action) => {
        console.log('Context menu action:', action);
        hideContextMenu();
        setStatusMessage(`Action: ${action}`);
    }, [hideContextMenu]);
    
    // Expose functions globally for components
    React.useEffect(() => {
        window.showContextMenu = showContextMenu;
        window.hideContextMenu = hideContextMenu;
    }, [showContextMenu, hideContextMenu]);
    
    // Handle clicks outside context menu
    React.useEffect(() => {
        const handleClickOutside = () => hideContextMenu();
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, [hideContextMenu]);
    
    // Undo/Redo functionality
    const handleUndo = React.useCallback(() => {
        if (moveHistory.length === 0) return;
        
        const lastMove = moveHistory[moveHistory.length - 1];
        // For now, just remove from history - full undo would need state restoration
        setMoveHistory(prev => prev.slice(0, -1));
        setStatusMessage(`Undid move: ${JSON.stringify(lastMove.move)}`);
    }, [moveHistory]);
    
    const handleRedo = React.useCallback(() => {
        // TODO: Implement proper redo with state stack
        setStatusMessage('Redo functionality coming soon');
    }, []);
    
    // Keyboard shortcuts
    React.useEffect(() => {
        const handleKeyPress = (e) => {
            if (e.key === 'Escape') {
                if (editMode) {
                    setSelectedElements([]);
                    setStatusMessage('Selection cleared');
                } else {
                clearSelection();
                }
            } else if (e.key === 'e' && e.ctrlKey) {
                e.preventDefault();
                handleEditModeToggle();
            } else if (e.key === 'z' && e.ctrlKey && !editMode) {
                e.preventDefault();
                handleUndo();
            } else if (e.key === 'y' && e.ctrlKey && !editMode) {
                e.preventDefault();
                handleRedo();
            } else if (editMode) {
                // Edit mode keyboard shortcuts
                if (['1', '2', '3', '4', '5'].includes(e.key)) {
                    e.preventDefault();
                    applyTileColor(e.key);
                } else if (e.key === 'Delete' || e.key === 'Backspace') {
                    e.preventDefault();
                    removeSelectedTiles();
                } else if (e.key === 'c' && e.ctrlKey) {
                    e.preventDefault();
                    copySelection();
                } else if (e.key === 'v' && e.ctrlKey) {
                    e.preventDefault();
                    pasteSelection();
                } else if (e.key === 'a' && e.ctrlKey) {
                    e.preventDefault();
                    // Select all tiles in current view
                    setStatusMessage('Select All not implemented yet');
                }
            }
        };
        
        document.addEventListener('keydown', handleKeyPress);
        return () => document.removeEventListener('keydown', handleKeyPress);
    }, [editMode, clearSelection, handleEditModeToggle, handleUndo, handleRedo, applyTileColor, removeSelectedTiles, copySelection, pasteSelection]);
    
    // Update body class for edit mode
    React.useEffect(() => {
        document.body.classList.toggle('edit-mode', editMode);
    }, [editMode]);
    
    if (!gameState) {
        return React.createElement('div', {
            className: 'flex items-center justify-center min-h-screen'
        },
            React.createElement('div', {
                className: 'text-center'
            },
                React.createElement('h1', {
                    className: 'text-2xl font-bold mb-4'
                }, 'Azul Solver & Analysis Toolkit'),
                React.createElement(StatusMessage, {
                    type: sessionStatus === 'connected' ? 'success' : 'error',
                    message: statusMessage
                })
            )
        );
    }
    
    return React.createElement(Router, {
        currentPage: currentPage,
        onPageChange: setCurrentPage
    },
        // Navigation
        React.createElement(Navigation, {
            currentPage: currentPage,
            onPageChange: setCurrentPage
        }),
        
        // Page Content
        currentPage === 'main' && React.createElement('div', {
            className: 'min-h-screen bg-gray-100'
        },
        // Header
        React.createElement('header', {
            className: 'bg-white shadow-sm border-b'
        },
            React.createElement('div', {
                className: 'max-w-8xl mx-auto px-6 py-4'
            },
                React.createElement('div', {
                    className: 'flex justify-between items-center'
                },
                    React.createElement('h1', {
                        className: 'text-2xl font-bold text-gray-900'
                    }, 'Azul Solver & Analysis Toolkit'),
                    React.createElement('div', {
                        className: 'flex space-x-4 xl:space-x-6'
                    },
                        React.createElement('button', {
                            className: `btn-edit ${editMode ? 'active' : ''}`,
                            onClick: handleEditModeToggle
                        }, editMode ? '✏️ Exit Edit' : '✏️ Edit Mode'),
                        React.createElement('button', {
                            className: 'btn-success',
                            onClick: () => getGameState().then(setGameState)
                        }, '🔄 Reset Game'),
                        React.createElement('button', {
                            className: 'btn-primary btn-sm',
                            onClick: () => {
                                getGameState().then(data => {
                                    setGameState(data);
                                    setStatusMessage('Game state refreshed');
                                }).catch(error => {
                                    setStatusMessage(`Refresh failed: ${error.message}`);
                                });
                            }
                        }, '🔄 Refresh'),
                        React.createElement('div', {
                            className: 'btn-group'
                        },
                            React.createElement('button', {
                                className: 'btn-info btn-sm',
                                onClick: exportPosition,
                                disabled: !gameState
                            }, '💾 Export'),
                            React.createElement('label', {
                                className: 'btn-info btn-sm cursor-pointer',
                                htmlFor: 'position-import'
                            }, '📁 Import'),
                            React.createElement('input', {
                                id: 'position-import',
                                type: 'file',
                                accept: '.json',
                                onChange: handleFileImport,
                                style: { display: 'none' }
                            })
                        )
                    )
                )
            )
        ),
        
        // Main content
        React.createElement('div', {
            className: 'max-w-8xl mx-auto px-6 py-6'
        },
            // Status message and current player
            React.createElement('div', {
                className: 'mb-6 space-y-2'
            },
            React.createElement(StatusMessage, {
                type: sessionStatus === 'connected' ? 'success' : 'error',
                message: statusMessage
            }),
                React.createElement('div', {
                    className: 'flex justify-between items-center p-4 bg-blue-50 rounded-lg'
                },
                    React.createElement('div', {
                        className: 'flex items-center space-x-2'
                    },
                        React.createElement('span', {
                            className: 'font-medium'
                        }, `Current Player: ${currentPlayer + 1}`),
                        engineThinking && React.createElement('span', {
                            className: 'text-sm text-blue-600'
                        }, '🤖 Engine thinking...')
                    ),
                    React.createElement('div', {
                        className: 'text-sm text-gray-600'
                    }, `Moves: ${moveHistory.length}`)
                )
            ),
            
            // Game board and player boards - Enhanced layout for larger screens
            React.createElement('div', {
                className: 'grid grid-cols-1 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-6'
            },
                // Game boards (factories + player boards) - takes more columns on larger screens
                React.createElement('div', {
                    className: 'lg:col-span-3 xl:col-span-4 2xl:col-span-5 space-y-6'
                },
                    // Factories
                    React.createElement('div', null,
                    React.createElement('h2', {
                        className: 'text-xl font-semibold mb-4'
                    }, 'Factories'),
                    React.createElement('div', {
                        className: 'grid grid-cols-5 md:grid-cols-5 lg:grid-cols-5 xl:grid-cols-5 2xl:grid-cols-5 gap-4 xl:gap-6'
                    },
                        (gameState.factories || []).map((factory, index) => 
                            React.createElement(Factory, {
                                key: index,
                                tiles: factory,
                                factoryIndex: index,
                                onTileClick: (factoryIndex, tileIndex, tile) => {
                                    setSelectedTile({ sourceId: factoryIndex, tileIndex, tile });
                                    setStatusMessage(`Selected ${tile} from factory ${factoryIndex}`);
                                },
                                selectedTile: selectedTile,
                                editMode: editMode,
                                onElementSelect: handleElementSelect,
                                    selectedElements: selectedElements,
                                    heatmapEnabled: heatmapEnabled,
                                    heatmapData: heatmapData
                            })
                        )
                    )
                ),
                
                    // Player boards - side by side layout
                    React.createElement('div', null,
                        React.createElement('h2', {
                            className: 'text-xl font-semibold mb-3'
                        }, 'Player Boards'),
                        React.createElement('div', {
                            className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2 2xl:grid-cols-2 gap-4 xl:gap-6'
                        },
                            (gameState.players || []).map((player, index) => 
                                React.createElement(PlayerBoard, {
                                    key: index,
                                    player: player,
                                    playerIndex: index,
                                    isActive: index === currentPlayer,
                                    editMode: editMode,
                                    onElementSelect: handleElementSelect,
                                    selectedElements: selectedElements,
                                    onPatternLineDrop: handlePatternLineDrop,
                                    onPlayerSwitch: (playerId) => setCurrentPlayer(playerId),
                                    canInteract: !loading && !engineThinking
                                })
                            )
                        )
                    )
                ),
                
                // Analysis panel - takes 1 column on the right, but more space on larger screens
                React.createElement('div', {
                    className: 'lg:col-span-1 xl:col-span-1 2xl:col-span-1 analysis-panel'
                },
                    React.createElement('h2', {
                        className: 'analysis-title'
                    }, '🔍 Analysis & Controls'),
                    React.createElement('div', {
                        className: 'space-y-3'
                    },
                        // Action buttons - compact
                        React.createElement('div', {
                            className: 'btn-group w-full'
                    },
                        React.createElement('button', {
                                className: 'btn-warning btn-sm flex-1',
                                onClick: handleUndo,
                                disabled: moveHistory.length === 0 || loading
                            }, '↶ Undo'),
                            React.createElement('button', {
                                className: 'btn-secondary btn-sm flex-1',
                                onClick: handleRedo,
                                disabled: loading
                            }, '↷ Redo')
                        ),
                        
                        // Analysis Tools - Organized with better labels
                        React.createElement('div', {
                            className: 'analysis-tools'
                        },
                            React.createElement('h3', {
                                className: 'font-medium text-sm mb-3 flex items-center justify-between text-blue-700'
                            },
                                React.createElement('span', null, '🔍 Position Analysis'),
                                React.createElement('button', {
                                    className: 'text-xs text-gray-500 hover:text-gray-700',
                                    onClick: () => setAnalysisExpanded(!analysisExpanded)
                                }, analysisExpanded ? '−' : '+')
                            ),
                            
                            // Collapsible analysis content
                            analysisExpanded && React.createElement('div', {
                                className: 'space-y-3'
                            },
                                                            // Advanced Analysis Controls
                            React.createElement(AdvancedAnalysisControls, {
                                loading: loading,
                                setLoading: setLoading,
                                analyzePosition: analyzePosition,
                                getHint: getHint,
                                analyzeNeural: analyzeNeural,
                                gameState: gameState,
                                setVariations: setVariations,
                                setHeatmapData: setHeatmapData,
                                setStatusMessage: setStatusMessage,
                                moveHistory: moveHistory,
                                analyzeGame: analyzeGame,
                                depth: depth,
                                setDepth: setDepth,
                                timeBudget: timeBudget,
                                setTimeBudget: setTimeBudget,
                                rollouts: rollouts,
                                setRollouts: setRollouts,
                                agentId: agentId,
                                setAgentId: setAgentId
                            }),
                            
                            // Advanced Analysis Settings Panel
                            React.createElement('div', {
                                className: 'bg-gray-50 p-3 rounded-lg border border-gray-200'
                            },
                                React.createElement('h4', {
                                    className: 'text-sm font-medium text-gray-700 mb-3'
                                }, '⚙️ Analysis Settings'),
                                
                                React.createElement('div', {
                                    className: 'space-y-3'
                                },
                                    // Depth control
                                    React.createElement('div', {
                                        className: 'flex items-center justify-between'
                                    },
                                        React.createElement('label', {
                                            className: 'text-xs text-gray-600'
                                        }, 'Depth:'),
                                        React.createElement('input', {
                                            type: 'range',
                                            min: '1',
                                            max: '5',
                                            value: depth,
                                            onChange: (e) => setDepth(parseInt(e.target.value)),
                                            className: 'w-20 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer'
                                        }),
                                        React.createElement('span', {
                                            className: 'text-xs text-gray-700 w-4 text-center'
                                        }, depth)
                                    ),
                                    
                                    // Time budget control
                                    React.createElement('div', {
                                        className: 'flex items-center justify-between'
                                    },
                                        React.createElement('label', {
                                            className: 'text-xs text-gray-600'
                                        }, 'Time (s):'),
                                        React.createElement('input', {
                                            type: 'range',
                                            min: '0.1',
                                            max: '10.0',
                                            step: '0.1',
                                            value: timeBudget,
                                            onChange: (e) => setTimeBudget(parseFloat(e.target.value)),
                                            className: 'w-20 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer'
                                        }),
                                        React.createElement('span', {
                                            className: 'text-xs text-gray-700 w-8 text-center'
                                        }, timeBudget.toFixed(1))
                                    ),
                                    
                                    // Rollouts control
                                    React.createElement('div', {
                                        className: 'flex items-center justify-between'
                                    },
                                        React.createElement('label', {
                                            className: 'text-xs text-gray-600'
                                        }, 'Rollouts:'),
                                        React.createElement('input', {
                                            type: 'range',
                                            min: '10',
                                            max: '1000',
                                            step: '10',
                                            value: rollouts,
                                            onChange: (e) => setRollouts(parseInt(e.target.value)),
                                            className: 'w-20 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer'
                                        }),
                                        React.createElement('span', {
                                            className: 'text-xs text-gray-700 w-12 text-center'
                                        }, rollouts)
                                    ),
                                    
                                    // Agent selection
                                    React.createElement('div', {
                                        className: 'flex items-center justify-between'
                                    },
                                        React.createElement('label', {
                                            className: 'text-xs text-gray-600'
                                        }, 'Agent:'),
                                        React.createElement('select', {
                                            value: agentId,
                                            onChange: (e) => setAgentId(parseInt(e.target.value)),
                                            className: 'text-xs border border-gray-300 rounded px-2 py-1'
                                        },
                                            React.createElement('option', { value: 0 }, 'Player 1'),
                                            React.createElement('option', { value: 1 }, 'Player 2')
                                        )
                                    )
                                )
                            ),
                            
                            // Heatmap toggle
                            React.createElement('div', {
                                className: 'flex items-center space-x-2'
                            },
                                React.createElement('button', {
                                    className: `btn-sm flex-1 ${heatmapEnabled ? 'btn-success' : 'btn-secondary'}`,
                                    onClick: () => {
                                        setHeatmapEnabled(!heatmapEnabled);
                                        setStatusMessage(heatmapEnabled ? 'Heatmap disabled' : 'Heatmap enabled');
                                    },
                                    disabled: !heatmapData
                                }, heatmapEnabled ? '🔥 Heatmap ON' : '🔥 Heatmap OFF')
                            ),
                                
                                // Analysis results display
                                variations.length > 0 && React.createElement('div', {
                                    className: 'bg-gradient-to-r from-blue-50 to-purple-50 p-3 rounded-lg border border-blue-200'
                                },
                                    React.createElement('div', { 
                                        className: 'font-semibold mb-2 text-blue-800 text-sm' 
                                    }, '📊 Analysis Results'),
                                    React.createElement('div', { 
                                        className: 'text-xs space-y-1' 
                                    },
                                        React.createElement('div', { 
                                            className: 'font-medium text-blue-700' 
                                        }, 'Best Move:'),
                                        React.createElement('div', { 
                                            className: 'bg-white p-2 rounded border' 
                                        }, `${variations[0].move} (${variations[0].score.toFixed(2)})`),
                                        variations[0].visits && React.createElement('div', { 
                                            className: 'text-gray-600 mt-1' 
                                        }, `Nodes searched: ${variations[0].visits}`)
                                    )
                                )
                            )
                        ),
                        
                        // Configuration Panel
                        React.createElement(ConfigurationPanel, {
                            loading: loading,
                            setLoading: setLoading,
                            setStatusMessage: setStatusMessage,
                            databasePath: databasePath,
                            setDatabasePath: setDatabasePath,
                            modelPath: modelPath,
                            setModelPath: setModelPath,
                            defaultTimeout: defaultTimeout,
                            setDefaultTimeout: setDefaultTimeout,
                            defaultDepth: defaultDepth,
                            setDefaultDepth: setDefaultDepth,
                            defaultRollouts: defaultRollouts,
                            setDefaultRollouts: setDefaultRollouts,
                            configExpanded: configExpanded,
                            setConfigExpanded: setConfigExpanded
                        }),
                        
                        // Development Tools Panel
                        React.createElement(DevelopmentToolsPanel, {
                            loading: loading,
                            setLoading: setLoading,
                            setStatusMessage: setStatusMessage,
                            devToolsExpanded: devToolsExpanded,
                            setDevToolsExpanded: setDevToolsExpanded
                        }),
                        
                        // Advanced Tools - Organized with better labels
                        React.createElement('div', {
                            className: 'analysis-tools'
                        },
                            React.createElement('h3', {
                                className: 'font-medium text-sm mb-3 flex items-center justify-between text-purple-700'
                            },
                                React.createElement('span', null, '🛠️ Advanced Tools'),
                                React.createElement('button', {
                                    className: 'text-xs text-gray-500 hover:text-gray-700',
                                    onClick: () => setAdvancedExpanded(!advancedExpanded)
                                }, advancedExpanded ? '−' : '+')
                            ),
                            
                            advancedExpanded && React.createElement('div', {
                                className: 'space-y-3'
                            },
                                React.createElement('div', {
                                    className: 'space-y-2'
                                },
                                    React.createElement('button', {
                                        className: `w-full btn-sm ${loading ? 'btn-secondary opacity-50' : 'btn-outline'}`,
                                        onClick: () => {
                                            setLoading(true);
                                            const gameData = {
                                                moves: moveHistory.map((move, index) => ({
                                                    move: move,
                                                    player: index % 2,
                                                    position_before: 'initial'
                                                })),
                                                players: ['Player 1', 'Player 2'],
                                                result: { winner: null, score: [0, 0] }
                                            };
                                            
                                            analyzeGame(gameData, 3)
                                                .then(data => {
                                                    if (data.success) {
                                                        const blunderCount = data.summary.blunder_count;
                                                        setStatusMessage(`Game analysis complete: ${blunderCount} blunders found`);
                                                    } else {
                                                        setStatusMessage('Game analysis failed');
                                                    }
                                                })
                                                .catch(error => {
                                                    setStatusMessage(`Game analysis failed: ${error.message}`);
                                                })
                                                .finally(() => setLoading(false));
                                        },
                                        disabled: loading || moveHistory.length === 0
                                    }, loading ? '📊 Analyzing Game...' : '📊 Analyze Full Game'),
                                    
                                    React.createElement('div', {
                                        className: 'grid grid-cols-2 gap-2'
                                    },
                                        React.createElement('button', {
                                            className: 'w-full btn-sm btn-outline',
                                            onClick: () => {
                                                setStatusMessage('Position database feature coming soon...');
                                            },
                                            disabled: loading
                                        }, '💾 Save Position'),
                                        
                                        React.createElement('button', {
                                            className: 'w-full btn-sm btn-outline',
                                            onClick: () => {
                                                setStatusMessage('Similar positions feature coming soon...');
                                            },
                                            disabled: loading
                                        }, '🔍 Find Similar')
                                    )
                                )
                            )
                        ),
                        
                        // Edit Mode Keyboard Hints - only show when edit mode is active
                        editMode && editHints && React.createElement('div', {
                            className: 'keyboard-hints mt-3 p-3 bg-orange-50 rounded text-xs'
                        },
            React.createElement('div', {
                                className: 'flex justify-between items-center mb-2'
                            },
                                React.createElement('h3', {
                                    className: 'font-medium'
                                }, '⌨️ Shortcuts'),
                                React.createElement('button', {
                                    className: 'text-xs text-gray-500 hover:text-gray-700',
                                    onClick: () => setEditHints(false)
                                }, '✕')
                            ),
                            React.createElement('div', {
                                className: 'grid grid-cols-2 gap-2 text-xs'
                            },
                                React.createElement('div', null,
                                    React.createElement('div', { className: 'font-medium' }, 'Selection:'),
                                    React.createElement('div', null, 'Click - Select'),
                                    React.createElement('div', null, 'Ctrl+Click - Multi-select'),
                                    React.createElement('div', null, 'Esc - Clear selection')
                                ),
                                React.createElement('div', null,
                                    React.createElement('div', { className: 'font-medium' }, 'Actions:'),
                                    React.createElement('div', null, '1-5 - Add tile colors'),
                                    React.createElement('div', null, 'Del - Remove tiles'),
                                    React.createElement('div', null, 'Ctrl+C/V - Copy/Paste')
                                )
                            ),
                            React.createElement('div', {
                                className: 'mt-2 p-1 bg-orange-100 rounded text-xs'
                            },
                                React.createElement('strong', null, 'Colors: '),
                                '1=Blue, 2=Yellow, 3=Red, 4=Black, 5=White'
                            ),
                            selectedElements.length > 0 && React.createElement('div', {
                                className: 'mt-2 p-1 bg-blue-100 rounded text-xs'
                            },
                                React.createElement('strong', null, `${selectedElements.length} element(s) selected`)
                            )
                        ),
                        
                        // Move history - compact
                        moveHistory.length > 0 && React.createElement('div', {
                            className: 'mt-3'
                        },
                            React.createElement('h3', {
                                className: 'font-medium text-sm mb-2'
                            }, '📜 Move History'),
                            React.createElement('div', {
                                className: 'max-h-24 overflow-y-auto space-y-1'
                            },
                                moveHistory.slice(-3).map((historyItem, index) => 
                                    React.createElement('div', {
                        key: index,
                                        className: 'text-xs p-1 bg-gray-100 rounded'
                                    },
                                        React.createElement('div', {
                                            className: 'font-medium'
                                        }, `P${historyItem.player + 1}`),
                                        React.createElement('div', null, historyItem.result.move_executed || 'Move executed')
                                    )
                                )
                            )
                        )
                    )
                )
            ),
            
            // Debug panel
            React.createElement('div', {
                className: 'mt-3 p-3 bg-gray-50 rounded-lg'
            },
                React.createElement('h3', {
                    className: 'font-semibold mb-2'
                }, 'Debug Info'),
                React.createElement('div', {
                    className: 'text-xs space-y-1'
                },
                    React.createElement('div', null, `Session: ${sessionId ? 'Connected' : 'Disconnected'}`),
                    React.createElement('div', null, `Game State: ${gameState ? 'Loaded' : 'Loading'}`),
                    React.createElement('div', null, `Factories: ${gameState?.factories?.length || 0}`),
                    React.createElement('div', null, `Players: ${gameState?.players?.length || 0}`),
                    React.createElement('details', null,
                        React.createElement('summary', {
                            className: 'cursor-pointer font-medium'
                        }, 'Server State'),
                React.createElement('pre', {
                            className: 'text-xs mt-2 bg-white p-2 rounded overflow-auto max-h-40'
                        }, gameState ? JSON.stringify(gameState, null, 2) : 'Loading...')
                    )
                )
            ),
            
            // Selected element display
            selectedElements.length > 0 && React.createElement('div', {
                className: 'mt-3 p-3 bg-blue-50 rounded-lg'
            },
                React.createElement('h3', {
                    className: 'font-semibold mb-2'
                }, `Selected Elements (${selectedElements.length})`),
                selectedElements.map((element, index) => 
                    React.createElement('div', {
                        key: index,
                        className: 'mb-2 p-2 bg-blue-100 rounded'
                    },
                        React.createElement('strong', null, `${element.type}: `),
                        formatSelectedElement(element)
                    )
                )
            )
        ),
        
        // Context menu
        React.createElement(ContextMenu, {
            visible: contextMenu.visible,
            x: contextMenu.x,
            y: contextMenu.y,
            options: contextMenu.options,
            onAction: handleContextMenuAction,
            onClose: hideContextMenu
        })
        ),
        
        // Neural Training Page
        currentPage === 'neural' && React.createElement(NeuralTrainingPage, {
            loading: loading,
            setLoading: setLoading,
            setStatusMessage: setStatusMessage,
            trainingConfig: trainingConfig,
            setTrainingConfig: setTrainingConfig,
            neuralExpanded: neuralExpanded,
            setNeuralExpanded: setNeuralExpanded
        })
    );
}

// Neural Training Components
// TrainingConfigPanel Component - Extracted to separate file

// Render the app
const root = createRoot(document.getElementById('root'));
root.render(React.createElement(App));