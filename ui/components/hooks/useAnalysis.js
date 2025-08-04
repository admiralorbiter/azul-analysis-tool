// useAnalysis.js - Custom hook for analysis-related state and functions
const { useState, useCallback } = React;

// Import API dependencies from window
const defaultGameAPI = window.gameAPI || {};
const {
    executeMove = () => Promise.resolve({}),
    getGameState = () => Promise.resolve()
} = defaultGameAPI;

window.useAnalysis = function useAnalysis(gameState, setGameState, setStatusMessage, setLoading) {
    // Analysis state
    const [variations, setVariations] = useState([]);
    const [heatmapEnabled, setHeatmapEnabled] = useState(false);
    const [heatmapData, setHeatmapData] = useState(null);
    const [analysisExpanded, setAnalysisExpanded] = useState(true);
    const [advancedExpanded, setAdvancedExpanded] = useState(true);
    
    // Advanced Analysis Controls State
    const [depth, setDepth] = useState(3);
    const [timeBudget, setTimeBudget] = useState(4.0);
    const [rollouts, setRollouts] = useState(100);
    const [agentId, setAgentId] = useState(0);
    
    // Game state
    const [currentPlayer, setCurrentPlayer] = useState(0);
    const [engineThinking, setEngineThinking] = useState(false);
    const [moveHistory, setMoveHistory] = useState([]);
    const [moveAnnotations, setMoveAnnotations] = useState({});
    
    // Helper function to convert tile color to type
    const getTileType = useCallback((tileColor) => {
        const mapping = { 'B': 0, 'Y': 1, 'R': 2, 'K': 3, 'W': 4 };
        return mapping[tileColor] !== undefined ? mapping[tileColor] : 0;
    }, []);
    
    // Helper function to apply a move locally to the game state
    const applyMoveLocally = useCallback((currentState, move, playerIndex) => {
        console.log('Applying move locally:', move);
        
        // Create a deep copy of the current state
        const newState = JSON.parse(JSON.stringify(currentState));
        
        // Apply the move based on its type
        if (move.source_id !== undefined && move.tile_type !== undefined) {
            const tileType = move.tile_type;
            const patternLineDest = move.pattern_line_dest;
            const numToPatternLine = move.num_to_pattern_line || 0;
            const numToFloor = move.num_to_floor_line || 0;
            const tileColorMap = { 0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W' };
            const tileColor = tileColorMap[tileType];
            
            if (move.source_id >= 0) {
                // Factory to pattern line move
                const factoryIndex = move.source_id;
                const factory = newState.factories[factoryIndex];
                const tilesToRemove = numToPatternLine + numToFloor;
                
                // Remove the specified number of tiles of this color from the factory
                let removed = 0;
                for (let i = factory.length - 1; i >= 0 && removed < tilesToRemove; i--) {
                    if (factory[i] === tileColor) {
                        factory.splice(i, 1);
                        removed++;
                    }
                }
                
                // Move remaining tiles from factory to center
                const remainingTiles = factory.filter(tile => tile !== tileColor);
                newState.center.push(...remainingTiles);
                newState.factories[factoryIndex] = [];
            } else {
                // Center pool to pattern line move
                const centerPool = newState.center;
                const tilesToRemove = numToPatternLine + numToFloor;
                
                // Remove the specified number of tiles of this color from the center pool
                let removed = 0;
                for (let i = centerPool.length - 1; i >= 0 && removed < tilesToRemove; i--) {
                    if (centerPool[i] === tileColor) {
                        centerPool.splice(i, 1);
                        removed++;
                    }
                }
                
                // Handle first player marker - if this is the first time taking from center pool
                if (!newState.first_player_taken) {
                    newState.first_player_taken = true;
                    console.log('First player marker taken from center pool');
                    
                    // Add first player marker to player's floor line
                    const player = newState.players[playerIndex];
                    if (!player.floor_line) {
                        player.floor_line = [];
                    }
                    player.floor_line.push('FP'); // First Player marker
                }
            }
            
            // Add tiles to pattern line
            if (numToPatternLine > 0 && patternLineDest >= 0 && patternLineDest < 5) {
                const player = newState.players[playerIndex];
                const patternLine = player.pattern_lines[patternLineDest];
                const maxCapacity = patternLineDest + 1;
                
                // Add tiles to pattern line (up to capacity)
                const tilesToAdd = Math.min(numToPatternLine, maxCapacity - patternLine.length);
                for (let i = 0; i < tilesToAdd; i++) {
                    patternLine.push(tileColor);
                }
            }
            
            // Add tiles to floor
            if (numToFloor > 0) {
                const player = newState.players[playerIndex];
                if (!player.floor_line) {
                    player.floor_line = [];
                }
                for (let i = 0; i < numToFloor; i++) {
                    player.floor_line.push(tileColor);
                }
            }
        }
        
        // Generate a new local FEN string
        const stateHash = btoa(JSON.stringify(newState)).slice(0, 8);
        newState.fen_string = `local_${stateHash}`;
        
        console.log('New state after local move:', newState);
        return newState;
    }, []);
    
    // Handle move execution
    const handleMoveExecution = useCallback(async (move) => {
        if (!gameState) {
            setStatusMessage('No game state available');
            return;
        }
        
        setLoading(true);
        setStatusMessage('Executing move...');
        
        try {
            // Check if this is a local position library state
            const currentFen = gameState.fen_string || 'initial';
            console.log('Executing move with FEN:', currentFen);
            
            if (currentFen.startsWith('local_')) {
                // This is a local position library state - handle move locally
                console.log('App: Handling move for local position library state');
                setStatusMessage('Move executed locally (position library mode)');
                
                // Create a new game state with the move applied
                const newGameState = applyMoveLocally(gameState, move, currentPlayer);
                
                // Update the game state
                await setGameState(newGameState);
                
                // Update move history
                setMoveHistory(prev => [...prev, {
                    move: move,
                    result: { success: true, move_executed: 'local' },
                    timestamp: Date.now(),
                    player: currentPlayer
                }]);
                
                setStatusMessage('Move executed locally');
                setLoading(false);
                return;
            }
            
            const result = await executeMove(currentFen, move, currentPlayer);
            
            if (result.success) {
                // Use the game state returned directly from execute_move
                const newGameState = result.new_game_state || result.game_state || await getGameState(result.new_fen);
                await setGameState(newGameState);
                
                setMoveHistory(prev => [...prev, {
                    move: move,
                    result: result,
                    timestamp: Date.now(),
                    player: currentPlayer
                }]);
                
                setStatusMessage(`Move executed: ${result.move_executed}`);
                
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
                
                getGameState().then(async freshState => {
                    await setGameState(freshState);
                    console.log('Game state refreshed after failed move');
                });
            }
        } catch (error) {
            setStatusMessage(`Error executing move: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [gameState, currentPlayer, setGameState, setStatusMessage, setLoading]);
    
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
            } else if (dragData.sourceType === 'center') {
                const centerPool = gameState?.center || [];
                if (!centerPool) {
                    setStatusMessage('Center pool not found');
                    return;
                }
                
                const tileExists = centerPool.includes(dragData.tile);
                if (!tileExists) {
                    setStatusMessage(`Tile ${dragData.tile} not found in center pool`);
                    console.log('Available tiles in center pool:', centerPool);
                    return;
                }
                
                const tileType = getTileType(dragData.tile);
                
                const tilesOfColor = centerPool.filter(tile => tile === dragData.tile).length;
                
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
                    setStatusMessage(`No ${dragData.tile} tiles found in center pool`);
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
                    source_id: -1, // Center pool is represented as -1
                    tile_type: tileType,
                    pattern_line_dest: rowIndex,
                    num_to_pattern_line: tilesToPattern,
                    num_to_floor_line: tilesToFloor
                };
                
                console.log('=== MOVE DEBUG ===');
                console.log(`Center pool contents:`, centerPool);
                console.log(`Taking ${tilesOfColor} ${dragData.tile} tiles (type ${tileType})`);
                console.log(`Pattern line ${rowIndex}: ${currentTilesInLine}/${maxPatternLineCapacity} tiles`);
                console.log(`Available space: ${availableSpace}`);
                console.log(`Distribution: ${tilesToPattern} to pattern line, ${tilesToFloor} to floor`);
                console.log('Move object:', move);
                console.log('==================');
                
                setStatusMessage(`Taking ${tilesOfColor} ${dragData.tile} tiles from center: ${tilesToPattern} to pattern line, ${tilesToFloor} to floor`);
                handleMoveExecution(move);
            }
        } catch (error) {
            console.error('Drop error:', error);
            setStatusMessage(`Invalid drop data: ${error.message}`);
        }
    }, [handleMoveExecution, gameState, getTileType, currentPlayer, setStatusMessage]);
    
    // Undo/Redo functionality
    const handleUndo = useCallback(() => {
        if (moveHistory.length === 0) return;
        
        const lastMove = moveHistory[moveHistory.length - 1];
        setMoveHistory(prev => prev.slice(0, -1));
        setStatusMessage(`Undid move: ${JSON.stringify(lastMove.move)}`);
    }, [moveHistory, setStatusMessage]);
    
    const handleRedo = useCallback(() => {
        setStatusMessage('Redo functionality coming soon');
    }, [setStatusMessage]);

    return {
        // Analysis state
        variations,
        setVariations,
        heatmapEnabled,
        setHeatmapEnabled,
        heatmapData,
        setHeatmapData,
        analysisExpanded,
        setAnalysisExpanded,
        advancedExpanded,
        setAdvancedExpanded,
        
        // Analysis controls
        depth,
        setDepth,
        timeBudget,
        setTimeBudget,
        rollouts,
        setRollouts,
        agentId,
        setAgentId,
        
        // Game state
        currentPlayer,
        setCurrentPlayer,
        engineThinking,
        setEngineThinking,
        moveHistory,
        setMoveHistory,
        moveAnnotations,
        setMoveAnnotations,
        
        // Functions
        getTileType,
        handleMoveExecution,
        handlePatternLineDrop,
        handleUndo,
        handleRedo
    };
} 