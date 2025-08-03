// App.js - Main App component
const { useState, useEffect, useCallback } = React;

// Import all component dependencies from window
const StatusMessage = window.StatusMessage;
const PlayerBoard = window.PlayerBoard;
const Factory = window.Factory;
const Router = window.Router;
const Navigation = window.Navigation;
const AdvancedAnalysisControls = window.AdvancedAnalysisControls;
const ConfigurationPanel = window.ConfigurationPanel;
const DevelopmentToolsPanel = window.DevelopmentToolsPanel;
const BoardEditor = window.BoardEditor;
const ValidationFeedback = window.ValidationFeedback;
const PositionLibrary = window.PositionLibrary;
const PatternAnalysis = window.PatternAnalysis;
const ScoringOptimizationAnalysis = window.ScoringOptimizationAnalysis;

// Import API dependencies from window
const defaultGameAPI = window.gameAPI || {};
const defaultNeuralAPI = window.neuralAPI || {};
const {
    initializeSession = () => Promise.resolve(),
    analyzePosition = () => {},
    getHint = () => {},
    analyzeNeural = () => {},
    analyzeGame = () => {},
    getGameState = () => Promise.resolve(),
    saveGameState = () => Promise.resolve(),
    executeMove = () => Promise.resolve({})
} = defaultGameAPI;
const {
    startNeuralTraining = () => {},
    getNeuralTrainingStatus = () => {},
    getNeuralTrainingProgress = () => {},
    getNeuralTrainingLogs = () => {},
    getAllTrainingSessions = () => {},
    deleteTrainingSession = () => {},
    stopNeuralTraining = () => {},
    evaluateNeuralModel = () => {},
    getEvaluationStatus = () => {},
    getAllEvaluationSessions = () => {},
    deleteEvaluationSession = () => {},
    getAvailableModels = () => {},
    getNeuralConfig = () => {},
    saveNeuralConfig = () => {}
} = defaultNeuralAPI;

function App() {
    // Routing State
    const [currentPage, setCurrentPage] = useState('main');
    
    // State declarations
    const [sessionStatus, setSessionStatus] = useState('connecting');
    const [statusMessage, setStatusMessage] = useState('Initializing...');
    const [loading, setLoading] = useState(false);
    const [gameState, setGameState] = useState(null);
    
    // Debug setGameState calls
    const debugSetGameState = useCallback((newState) => {
        console.log('App: setGameState called with:', newState);
        setGameState(newState);
    }, []);
    
    // Add state stability tracking
    const [hasStableState, setHasStableState] = useState(false);
    const [lastStateHash, setLastStateHash] = useState(null);
    const [userActive, setUserActive] = useState(false);
    const [lastUserActivity, setLastUserActivity] = useState(Date.now());
    
    // Helper function to create a simple hash of game state for comparison
    const createStateHash = useCallback((state) => {
        if (!state) return null;
        try {
            // Create a simple hash based on factories and player scores
            const factoriesHash = JSON.stringify(state.factories || []);
            const scoresHash = JSON.stringify(state.players?.map(p => p.score) || []);
            return `${factoriesHash}_${scoresHash}`;
        } catch (error) {
            console.error('Error creating state hash:', error);
            return null;
        }
    }, []);
    
    // Track user activity
    const trackUserActivity = useCallback(() => {
        setUserActive(true);
        setLastUserActivity(Date.now());
        // Reset user active flag after 30 seconds of inactivity
        setTimeout(() => setUserActive(false), 30000);
    }, []);
    
    // Manual refresh function
    const manualRefresh = useCallback(() => {
        if (sessionStatus === 'connected' && !loading) {
            setLoading(true);
            getGameState('saved').catch(() => getGameState('initial')).then(data => {
                debugSetGameState(data);
                setStatusMessage('Game state refreshed manually');
                setLastStateHash(createStateHash(data));
            }).catch(error => {
                console.error('Failed to refresh game state:', error);
                setStatusMessage('Failed to refresh game state');
            }).finally(() => {
                setLoading(false);
            });
        }
    }, [sessionStatus, loading, createStateHash]);
    const [selectedTile, setSelectedTile] = useState(null);
    const [editMode, setEditMode] = useState(false);
    const [selectedElements, setSelectedElements] = useState([]);
    const [clipboard, setClipboard] = useState(null);
    const [editHints, setEditHints] = useState(true);
    const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, options: [] });
    const [variations, setVariations] = useState([]);
    const [moveAnnotations, setMoveAnnotations] = useState({});
    const [moveHistory, setMoveHistory] = useState([]);
    const [currentPlayer, setCurrentPlayer] = useState(0);
    const [engineThinking, setEngineThinking] = useState(false);
    const [heatmapEnabled, setHeatmapEnabled] = useState(false);
    const [heatmapData, setHeatmapData] = useState(null);
    const [analysisExpanded, setAnalysisExpanded] = useState(true);
    const [advancedExpanded, setAdvancedExpanded] = useState(true);
    
    // Advanced Analysis Controls State
    const [depth, setDepth] = useState(3);
    const [timeBudget, setTimeBudget] = useState(4.0);
    const [rollouts, setRollouts] = useState(100);
    const [agentId, setAgentId] = useState(0);
    
    // Configuration Panel State
    const [databasePath, setDatabasePath] = useState('azul_cache.db');
    const [modelPath, setModelPath] = useState('models/azul_net_small.pth');
    const [defaultTimeout, setDefaultTimeout] = useState(4.0);
    const [defaultDepth, setDefaultDepth] = useState(3);
    const [defaultRollouts, setDefaultRollouts] = useState(100);
    const [configExpanded, setConfigExpanded] = useState(false);
    
    // Development Tools Panel State
    const [devToolsExpanded, setDevToolsExpanded] = useState(false);
    
    // Position Library State (R1.2)
    const [showPositionLibrary, setShowPositionLibrary] = useState(false);
    const [positionJustLoaded, setPositionJustLoaded] = useState(false);
    
    // Auto-refresh configuration
    const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
    

    

    
    // Neural Training State
    const [neuralExpanded, setNeuralExpanded] = useState(false);
    const [trainingConfig, setTrainingConfig] = useState({
        modelSize: 'small',
        device: 'cpu',
        epochs: 5,
        samples: 500,
        batchSize: 16,
        learningRate: 0.001
    });

    // Initialize session
    useEffect(() => {
        initializeSession()
            .then(() => {
                setSessionStatus('connected');
                setStatusMessage('Connected to server');
                // Try to load saved state first, fall back to initial state
                return getGameState('saved').catch(() => {
                    console.log('No saved state found, loading initial state');
                    return getGameState('initial');
                });
            })
            .then(data => {
                console.log('Game state loaded:', data);
                debugSetGameState(data);
                setStatusMessage('Game loaded');
                setHasStableState(true);
                setLastStateHash(createStateHash(data));
            })
            .catch(error => {
                setSessionStatus('error');
                setStatusMessage(`Connection failed: ${error.message}`);
            });
    }, []);

    // Improved refresh game state periodically - only when necessary
    useEffect(() => {
        const interval = setInterval(() => {
            // Only refresh if:
            // 1. We're connected
            // 2. Not loading
            // 3. Not in edit mode
            // 4. Position wasn't just loaded
            // 5. We have a stable state (don't keep refreshing if state is unstable)
            // 6. User is not actively interacting (inactive for 30+ seconds)
            // 7. Auto-refresh is enabled
            const timeSinceActivity = Date.now() - lastUserActivity;
            const shouldRefresh = sessionStatus === 'connected' && 
                               !loading && 
                               !editMode && 
                               !positionJustLoaded && 
                               hasStableState && 
                               !userActive && 
                               timeSinceActivity > 30000 && // 30 seconds
                               autoRefreshEnabled;
                               
            if (shouldRefresh) {
                // Try to load saved state first, fall back to initial state
                getGameState('saved').catch(() => getGameState('initial')).then(data => {
                    const newStateHash = createStateHash(data);
                    
                    // Only update if the state has actually changed
                    if (newStateHash !== lastStateHash) {
                        console.log('State changed, updating...');
                        debugSetGameState(data);
                        setLastStateHash(newStateHash);
                    } else {
                        console.log('State unchanged, skipping update');
                    }
                }).catch(error => {
                    console.error('Failed to refresh game state:', error);
                });
            }
        }, 15000); // Increased interval to 15 seconds to reduce unnecessary calls
        return () => clearInterval(interval);
    }, [sessionStatus, loading, editMode, positionJustLoaded, hasStableState, lastStateHash, createStateHash, userActive, lastUserActivity, autoRefreshEnabled]);

    // Clear selection function
    const clearSelection = useCallback(() => {
        setSelectedTile(null);
        setSelectedElements([]);
        setStatusMessage('Selection cleared');
    }, []);

    // Edit mode functions
    const handleEditModeToggle = useCallback(() => {
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
    const handleElementSelect = useCallback((element, isCtrlClick = false) => {
        if (!editMode) return;

        const elementId = `${element.type}_${element.data.factoryIndex || element.data.playerIndex || 0}_${element.data.rowIndex || 0}_${element.data.colIndex || element.data.tileIndex || 0}`;
        
        setSelectedElements(prev => {
            if (isCtrlClick) {
                const isAlreadySelected = prev.some(el => el.id === elementId);
                if (isAlreadySelected) {
                    return prev.filter(el => el.id !== elementId);
                } else {
                    return [...prev, { ...element, id: elementId }];
                }
            } else {
                return [{ ...element, id: elementId }];
            }
        });

        const count = isCtrlClick ? 'multiple' : '1';
        setStatusMessage(`Selected ${count} element(s). Use 1-5 for colors, Delete to remove, Ctrl+C/V to copy/paste.`);
    }, [editMode]);

    // Apply tile color to selected elements
    const applyTileColor = useCallback((colorKey) => {
        if (!editMode || selectedElements.length === 0) return;

        const colorMap = { '1': 'B', '2': 'Y', '3': 'R', '4': 'K', '5': 'W' };
        const color = colorMap[colorKey];
        
        if (!color) return;

        console.log(`Applying ${color} tiles to:`, selectedElements);
        
        const newGameState = JSON.parse(JSON.stringify(gameState));
        
        selectedElements.forEach(element => {
            if (element.type === 'factory') {
                const factoryIndex = element.data.factoryIndex;
                if (newGameState.factories && newGameState.factories[factoryIndex]) {
                    newGameState.factories[factoryIndex].push(color);
                }
            } else if (element.type === 'pattern-line') {
                const { playerIndex, rowIndex } = element.data;
                if (newGameState.players && newGameState.players[playerIndex]) {
                    const player = newGameState.players[playerIndex];
                    if (player.pattern_lines && player.pattern_lines[rowIndex]) {
                        player.pattern_lines[rowIndex].push(color);
                    }
                }
            } else if (element.type === 'wall-cell') {
                const { playerIndex, rowIndex, colIndex } = element.data;
                if (newGameState.players && newGameState.players[playerIndex]) {
                    const player = newGameState.players[playerIndex];
                    if (player.wall && player.wall[rowIndex] && player.wall[rowIndex][colIndex] === null) {
                        player.wall[rowIndex][colIndex] = color;
                    }
                }
            }
        });
        
        debugSetGameState(newGameState);
        setStatusMessage(`Applied ${color} tiles to ${selectedElements.length} location(s)`);
        
        saveGameState(newGameState).then(() => {
            setStatusMessage(`Applied ${color} tiles to ${selectedElements.length} location(s) - Saved to server`);
        }).catch(error => {
            console.error('Failed to save game state:', error);
            setStatusMessage(`Applied ${color} tiles but failed to save to server`);
        });
        
        setSelectedElements([]);
    }, [editMode, selectedElements, gameState]);

    // Remove tiles from selected elements
    const removeSelectedTiles = useCallback(() => {
        if (!editMode || selectedElements.length === 0) return;

        console.log('Removing tiles from:', selectedElements);
        
        const newGameState = JSON.parse(JSON.stringify(gameState));
        
        selectedElements.forEach(element => {
            if (element.type === 'factory') {
                const factoryIndex = element.data.factoryIndex;
                if (newGameState.factories && newGameState.factories[factoryIndex]) {
                    newGameState.factories[factoryIndex] = [];
                }
            } else if (element.type === 'pattern-line') {
                const { playerIndex, rowIndex } = element.data;
                if (newGameState.players && newGameState.players[playerIndex]) {
                    const player = newGameState.players[playerIndex];
                    if (player.pattern_lines && player.pattern_lines[rowIndex]) {
                        player.pattern_lines[rowIndex] = [];
                    }
                }
            } else if (element.type === 'wall-cell') {
                const { playerIndex, rowIndex, colIndex } = element.data;
                if (newGameState.players && newGameState.players[playerIndex]) {
                    const player = newGameState.players[playerIndex];
                    if (player.wall && player.wall[rowIndex] && player.wall[rowIndex][colIndex] !== null) {
                        player.wall[rowIndex][colIndex] = null;
                    }
                }
            }
        });
        
        debugSetGameState(newGameState);
        setStatusMessage(`Removed tiles from ${selectedElements.length} location(s)`);
        
        saveGameState(newGameState).then(() => {
            setStatusMessage(`Removed tiles from ${selectedElements.length} location(s) - Saved to server`);
        }).catch(error => {
            console.error('Failed to save game state:', error);
            setStatusMessage(`Removed tiles but failed to save to server`);
        });
        
        setSelectedElements([]);
    }, [editMode, selectedElements, gameState]);

    // Copy selected elements
    const copySelection = useCallback(() => {
        if (!editMode || selectedElements.length === 0) return;

        setClipboard([...selectedElements]);
        setStatusMessage(`Copied ${selectedElements.length} element(s) to clipboard`);
    }, [editMode, selectedElements]);

    // Paste clipboard to selected location
    const pasteSelection = useCallback(() => {
        if (!editMode || !clipboard || selectedElements.length !== 1) {
            setStatusMessage('Select exactly one location to paste to');
            return;
        }

        console.log('Pasting from clipboard:', clipboard, 'to:', selectedElements[0]);
        
        const newGameState = JSON.parse(JSON.stringify(gameState));
        const targetElement = selectedElements[0];
        
        clipboard.forEach(element => {
            if (element.type === 'factory' && targetElement.type === 'factory') {
                const sourceFactoryIndex = element.data.factoryIndex;
                const targetFactoryIndex = targetElement.data.factoryIndex;
                
                if (newGameState.factories && newGameState.factories[sourceFactoryIndex]) {
                    const tilesToCopy = [...newGameState.factories[sourceFactoryIndex]];
                    newGameState.factories[targetFactoryIndex] = tilesToCopy;
                }
            } else if (element.type === 'pattern-line' && targetElement.type === 'pattern-line') {
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
        
        debugSetGameState(newGameState);
        setStatusMessage(`Pasted ${clipboard.length} element(s)`);
        
        saveGameState(newGameState).then(() => {
            setStatusMessage(`Pasted ${clipboard.length} element(s) - Saved to server`);
        }).catch(error => {
            console.error('Failed to save game state:', error);
            setStatusMessage(`Pasted elements but failed to save to server`);
        });
        
        setSelectedElements([]);
    }, [editMode, clipboard, selectedElements, gameState]);
    
    // Handle move execution
    const handleMoveExecution = useCallback(async (move) => {
        if (!gameState) return;
        
        setLoading(true);
        setStatusMessage('Executing move...');
        
        try {
            // Use the current FEN string from game state, or 'initial' as fallback
            const currentFen = gameState.fen_string || 'initial';
            console.log('Executing move with FEN:', currentFen);
            const result = await executeMove(currentFen, move, currentPlayer);
            
            if (result.success) {
                const newGameState = await getGameState(result.new_fen);
                debugSetGameState(newGameState);
                
                setMoveHistory(prev => [...prev, {
                    move: move,
                    result: result,
                    timestamp: Date.now(),
                    player: currentPlayer
                }]);
                
                setStatusMessage(`Move executed: ${result.move_executed}`);
                
                setSelectedTile(null);
                
                if (result.engine_response && !result.game_over) {
                    setEngineThinking(true);
                    setStatusMessage(`Engine thinking... Best move: ${result.engine_response.move}`);
                    
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
                
                getGameState().then(freshState => {
                    debugSetGameState(freshState);
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
    const getTileType = useCallback((tileColor) => {
        const mapping = { 'B': 0, 'Y': 1, 'R': 2, 'K': 3, 'W': 4 };
        return mapping[tileColor] !== undefined ? mapping[tileColor] : 0;
    }, []);
    
    // Handle pattern line drop
    const handlePatternLineDrop = useCallback((e, rowIndex) => {
        e.preventDefault();
        
        try {
            const dragData = JSON.parse(e.dataTransfer.getData('application/json'));
            console.log('Drop data received:', dragData);
            
            if (dragData.sourceType === 'factory') {
                const factory = gameState?.factories?.[dragData.sourceId];
                if (!factory) {
                    setStatusMessage(`Factory ${dragData.sourceId} not found`);
                    return;
                }
                
                const tileExists = factory.includes(dragData.tile);
                if (!tileExists) {
                    setStatusMessage(`Tile ${dragData.tile} not found in factory ${dragData.sourceId}`);
                    console.log('Available tiles in factory:', factory);
                    return;
                }
                
                const tileType = getTileType(dragData.tile);
                
                const tilesOfColor = factory.filter(tile => tile === dragData.tile).length;
                
                const activePlayer = gameState?.players?.[currentPlayer];
                const currentPatternLine = activePlayer?.pattern_lines?.[rowIndex] || [];
                const maxPatternLineCapacity = rowIndex + 1;
                const currentTilesInLine = currentPatternLine.length;
                const availableSpace = maxPatternLineCapacity - currentTilesInLine;
                
                const tilesToPattern = Math.min(tilesOfColor, availableSpace);
                const tilesToFloor = tilesOfColor - tilesToPattern;
                
                if (availableSpace <= 0) {
                    setStatusMessage(`Pattern line ${rowIndex} is already full!`);
                    return;
                }
                
                if (tilesOfColor === 0) {
                    setStatusMessage(`No ${dragData.tile} tiles found in factory ${dragData.sourceId}`);
                    return;
                }
                
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
                console.log(`All factories:`, gameState?.factories);
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
    const exportPosition = useCallback(() => {
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
    
    const importPosition = useCallback((file) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const data = JSON.parse(e.target.result);
                
                getGameState(data.fen).then(newGameState => {
                    debugSetGameState(newGameState);
                    
                    if (data.moveHistory) {
                        setMoveHistory(data.moveHistory);
                    }
                    
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
    
    const handleFileImport = useCallback((e) => {
        const file = e.target.files[0];
        if (file) {
            importPosition(file);
        }
        e.target.value = '';
    }, [importPosition]);
    
    // Context menu functions
    const showContextMenu = useCallback((e, elementType, elementData) => {
        e.preventDefault();
        const options = window.getMenuOptions ? window.getMenuOptions(elementType, elementData) : [];
        setContextMenu({
            visible: true,
            x: e.clientX,
            y: e.clientY,
            options: options
        });
    }, []);
    
    const hideContextMenu = useCallback(() => {
        setContextMenu({ visible: false, x: 0, y: 0, options: [] });
    }, []);
    
    const handleContextMenuAction = useCallback((action) => {
        console.log('Context menu action:', action);
        hideContextMenu();
        setStatusMessage(`Action: ${action}`);
    }, [hideContextMenu]);
    
    // Expose functions globally for components
    useEffect(() => {
        window.showContextMenu = showContextMenu;
        window.hideContextMenu = hideContextMenu;
        window.setPositionJustLoaded = setPositionJustLoaded;
    }, [showContextMenu, hideContextMenu, setPositionJustLoaded]);
    
    // Handle clicks outside context menu
    useEffect(() => {
        const handleClickOutside = () => hideContextMenu();
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, [hideContextMenu]);
    
    // Undo/Redo functionality
    const handleUndo = useCallback(() => {
        if (moveHistory.length === 0) return;
        
        const lastMove = moveHistory[moveHistory.length - 1];
        setMoveHistory(prev => prev.slice(0, -1));
        setStatusMessage(`Undid move: ${JSON.stringify(lastMove.move)}`);
    }, [moveHistory]);
    
    const handleRedo = useCallback(() => {
        setStatusMessage('Redo functionality coming soon');
    }, []);
    
    // Keyboard shortcuts
    useEffect(() => {
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
                    setStatusMessage('Select All not implemented yet');
                }
            }
        };
        
        document.addEventListener('keydown', handleKeyPress);
        return () => document.removeEventListener('keydown', handleKeyPress);
    }, [editMode, clearSelection, handleEditModeToggle, handleUndo, handleRedo, applyTileColor, removeSelectedTiles, copySelection, pasteSelection]);
    
    // Update body class for edit mode
    useEffect(() => {
        document.body.classList.toggle('edit-mode', editMode);
    }, [editMode]);

    // Render tree
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
        React.createElement(Navigation, {
            currentPage: currentPage,
            onPageChange: setCurrentPage
        }),
        
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
                                className: 'btn-info',
                                onClick: () => setShowPositionLibrary(true)
                            }, '📚 Position Library'),
                            React.createElement('button', {
                                className: 'btn-success',
                                onClick: () => {
                                    if (gameState) {
                                        saveGameState(gameState, 'saved').then(() => {
                                            setStatusMessage('✅ Board position saved successfully');
                                        }).catch(error => {
                                            setStatusMessage(`❌ Failed to save: ${error.message}`);
                                        });
                                    } else {
                                        setStatusMessage('❌ No game state to save');
                                    }
                                },
                                disabled: !gameState
                            }, '💾 Save Position'),
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
            
            // Main content - Condensed single-screen layout
            React.createElement('div', {
                className: 'max-w-full mx-auto px-4 py-2',
                onMouseMove: trackUserActivity,
                onClick: trackUserActivity,
                onKeyDown: trackUserActivity
            },
                // Compact status bar
                React.createElement('div', {
                    className: 'mb-3'
                },
                    React.createElement(StatusMessage, {
                        type: sessionStatus === 'connected' ? 'success' : 'error',
                        message: statusMessage
                    }),
                    React.createElement('div', {
                        className: 'flex justify-between items-center p-2 bg-blue-50 rounded text-sm'
                    },
                        React.createElement('div', {
                            className: 'flex items-center space-x-2'
                        },
                            React.createElement('span', {
                                className: 'font-medium'
                            }, `Player: ${currentPlayer + 1}`),
                            engineThinking && React.createElement('span', {
                                className: 'text-blue-600'
                            }, '🤖 Thinking...'),
                            positionJustLoaded && React.createElement('span', {
                                className: 'text-green-600 font-medium'
                            }, '📚 Position Loaded'),
                            userActive && React.createElement('span', {
                                className: 'text-orange-600'
                            }, '👤 Active'),
                            !autoRefreshEnabled && React.createElement('span', {
                                className: 'text-red-600'
                            }, '⏸️ Auto-Refresh Off')
                        ),
                        React.createElement('div', {
                            className: 'flex items-center space-x-2'
                        },
                            React.createElement('span', {
                                className: 'text-gray-600'
                            }, `Moves: ${moveHistory.length}`),
                            React.createElement('button', {
                                className: 'btn-secondary btn-xs',
                                onClick: manualRefresh,
                                disabled: loading
                            }, '🔄 Refresh')
                        )
                    )
                ),
                
                // Enhanced Board Editor (R1.1) - appears when edit mode is enabled
                editMode && BoardEditor && React.createElement(BoardEditor, {
                    gameState: gameState,
                    setGameState: debugSetGameState,
                    editMode: editMode,
                    selectedElements: selectedElements,
                    onElementSelect: handleElementSelect,
                    setStatusMessage: setStatusMessage,
                    sessionToken: window.sessionStorage?.getItem('sessionToken') || null
                }),
                
                // Position Library (R1.2) - appears when library is opened
                showPositionLibrary && PositionLibrary && React.createElement(PositionLibrary, {
                    gameState: gameState,
                    setGameState: debugSetGameState,
                    setStatusMessage: setStatusMessage,
                    sessionToken: window.sessionStorage?.getItem('sessionToken') || null,
                    onClose: () => setShowPositionLibrary(false)
                }),
                
                // Main game layout - 2 columns: Controls | Game Board
                React.createElement('div', {
                    className: 'flex gap-4 h-[calc(100vh-200px)]'
                },
                    // Left Sidebar - Unified Controls Panel (25% width)
                    React.createElement('div', {
                        className: 'w-1/4 min-w-80'
                    },
                        // Single unified controls panel
                        React.createElement('div', {
                            className: 'bg-white rounded p-4 shadow-sm h-full overflow-y-auto'
                        },
                            React.createElement('h3', {
                                className: 'font-medium text-lg mb-4 text-blue-700 border-b pb-2'
                            }, '🎮 Game Controls'),
                            
                            // Analysis Results Section
                            React.createElement('div', {
                                className: 'mb-4'
                            },
                                React.createElement('h4', {
                                    className: 'font-medium text-sm mb-2 text-gray-700'
                                }, '📊 Analysis Results'),
                                React.createElement(AnalysisResults, {
                                    variations: variations,
                                    loading: loading,
                                    engineThinking: engineThinking
                                })
                            ),
                            
                            // Action Controls Section
                            React.createElement('div', {
                                className: 'mb-4'
                            },
                                React.createElement('h4', {
                                    className: 'font-medium text-sm mb-2 text-gray-700'
                                }, '↶↷ Move Controls'),
                                React.createElement('div', {
                                    className: 'grid grid-cols-2 gap-2 mb-3'
                                },
                                    React.createElement('button', {
                                        className: 'btn-warning btn-xs',
                                        onClick: handleUndo,
                                        disabled: moveHistory.length === 0 || loading
                                    }, '↶ Undo'),
                                    React.createElement('button', {
                                        className: 'btn-secondary btn-xs',
                                        onClick: handleRedo,
                                        disabled: loading
                                    }, '↷ Redo')
                                )
                            ),
                            
                            // Analysis Tools Section
                            React.createElement('div', {
                                className: 'mb-4'
                            },
                                React.createElement('h4', {
                                    className: 'font-medium text-sm mb-2 text-gray-700'
                                }, '🔍 Analysis Tools'),
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
                                })
                            ),
                            
                            // Pattern Analysis Section (R2.1)
                            React.createElement('div', {
                                className: 'mb-4'
                            },
                                React.createElement('h4', {
                                    className: 'font-medium text-sm mb-2 text-gray-700'
                                }, '🎯 Pattern Analysis'),
                                React.createElement(PatternAnalysis, {
                                    gameState: gameState,
                                    currentPlayer: currentPlayer,
                                    onPatternDetected: (patterns) => {
                                        if (patterns.patterns_detected) {
                                            setStatusMessage(`🎯 ${patterns.total_patterns} tactical pattern${patterns.total_patterns !== 1 ? 's' : ''} detected`);
                                        }
                                    }
                                })
                            ),
                            
                            // Scoring Optimization Analysis Section (R2.2)
                            React.createElement('div', {
                                className: 'mb-4'
                            },
                                React.createElement('h4', {
                                    className: 'font-medium text-sm mb-2 text-gray-700'
                                }, '🎯 Scoring Optimization Analysis'),
                                React.createElement(ScoringOptimizationAnalysis, {
                                    gameState: gameState,
                                    currentPlayer: currentPlayer,
                                    onOptimizationDetected: (optimizations) => {
                                        if (optimizations.opportunities_detected) {
                                            setStatusMessage(`🎯 ${optimizations.total_opportunities} scoring optimization opportunity${optimizations.total_opportunities !== 1 ? 'ies' : 'y'} detected`);
                                        }
                                    }
                                })
                            ),
                            
                            // Quick Actions Section
                            React.createElement('div', {
                                className: 'mb-4'
                            },
                                React.createElement('h4', {
                                    className: 'font-medium text-sm mb-2 text-gray-700'
                                }, '⚡ Quick Actions'),
                                React.createElement('div', {
                                    className: 'grid grid-cols-2 gap-2'
                                },
                                    React.createElement('button', {
                                        className: 'btn-primary btn-xs',
                                        onClick: () => setConfigExpanded(!configExpanded)
                                    }, configExpanded ? '⚙️ Hide Config' : '⚙️ Show Config'),
                                    React.createElement('button', {
                                        className: 'btn-secondary btn-xs',
                                        onClick: () => setDevToolsExpanded(!devToolsExpanded)
                                    }, devToolsExpanded ? '🔧 Hide Dev Tools' : '🔧 Show Dev Tools'),
                                    React.createElement('button', {
                                        className: 'btn-info btn-xs',
                                        onClick: () => setHeatmapEnabled(!heatmapEnabled)
                                    }, heatmapEnabled ? '🔥 Hide Heatmap' : '🔥 Show Heatmap'),
                                    React.createElement('button', {
                                        className: `${autoRefreshEnabled ? 'btn-warning' : 'btn-success'} btn-xs`,
                                        onClick: () => setAutoRefreshEnabled(!autoRefreshEnabled)
                                    }, autoRefreshEnabled ? '⏸️ Disable Auto-Refresh' : '▶️ Enable Auto-Refresh')
                                )
                            ),
                            
                            // Collapsible Configuration Panel
                            configExpanded && React.createElement('div', {
                                className: 'mb-4'
                            },
                                React.createElement('h4', {
                                    className: 'font-medium text-sm mb-2 text-gray-700'
                                }, '⚙️ Configuration'),
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
                                })
                            ),
                            
                            // Collapsible Development Tools Panel
                            devToolsExpanded && React.createElement('div', {
                                className: 'mb-4'
                            },
                                React.createElement('h4', {
                                    className: 'font-medium text-sm mb-2 text-gray-700'
                                }, '🔧 Development Tools'),
                                React.createElement(DevelopmentToolsPanel, {
                                    loading: loading,
                                    setLoading: setLoading,
                                    setStatusMessage: setStatusMessage,
                                    devToolsExpanded: devToolsExpanded,
                                    setDevToolsExpanded: setDevToolsExpanded
                                })
                            )
                        )
                    ),
                    
                    // Right - Game Board (75% width for maximum board space)
                    React.createElement('div', {
                        className: 'flex-1 space-y-3'
                    },
                        // Factories at top
                        React.createElement('div', {
                            className: 'bg-white rounded p-3 shadow-sm'
                        },
                            React.createElement('h3', {
                                className: 'font-medium text-sm mb-2'
                            }, '🏢 Factories'),
                            React.createElement('div', {
                                className: 'grid grid-cols-5 gap-2'
                            },
                                (gameState.factories || []).map((factory, index) => {
                                    // Handle both old format (object with tiles) and new format (array)
                                    let tilesArray = [];
                                    if (Array.isArray(factory)) {
                                        // New format: factory is already an array of tile strings
                                        tilesArray = factory;
                                    } else if (factory.tiles) {
                                        // Old format: convert tiles object to array
                                        const colorMap = { 0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W' };
                                        Object.entries(factory.tiles).forEach(([colorIndex, count]) => {
                                            const color = colorMap[parseInt(colorIndex)];
                                            if (color && count > 0) {
                                                for (let i = 0; i < count; i++) {
                                                    tilesArray.push(color);
                                                }
                                            }
                                        });
                                    }
                                    
                                    return React.createElement(Factory, {
                                        key: index,
                                        tiles: tilesArray,
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
                                    });
                                })
                            )
                        ),
                        
                        // Player boards - now with more space
                        React.createElement('div', {
                            className: 'bg-white rounded p-3 shadow-sm flex-1'
                        },
                            React.createElement('h3', {
                                className: 'font-medium text-sm mb-2'
                            }, '👥 Player Boards'),
                            React.createElement('div', {
                                className: 'grid grid-cols-1 xl:grid-cols-2 gap-4 h-full'
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
                    )
                )
            )
        ),
        
        // Context menu - moved to correct level
        React.createElement(ContextMenu, {
            visible: contextMenu.visible,
            x: contextMenu.x,
            y: contextMenu.y,
            options: contextMenu.options,
            onAction: handleContextMenuAction,
            onClose: hideContextMenu
        })
    );
}

window.App = App;