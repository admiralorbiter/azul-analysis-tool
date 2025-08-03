/**
 * BoardEditor Component - Enhanced board state editor with rule validation
 * 
 * This component extends the existing edit mode with comprehensive
 * validation, position templates, and advanced editing features.
 */

const { useState, useEffect, useCallback, useRef } = React;

function BoardEditor({
    gameState,
    setGameState,
    editMode,
    selectedElements,
    onElementSelect,
    setStatusMessage,
    sessionToken
}) {
    // Enhanced editor state
    const [validationEnabled, setValidationEnabled] = useState(true);
    const [showValidationPanel, setShowValidationPanel] = useState(true);
    const [globalValidation, setGlobalValidation] = useState(null);
    const [elementValidations, setElementValidations] = useState({});
    const [positionTemplates, setPositionTemplates] = useState([]);
    const [showTemplatePanel, setShowTemplatePanel] = useState(false);
    const [undoStack, setUndoStack] = useState([]);
    const [redoStack, setRedoStack] = useState([]);
    
    // Import validation components
    const ValidationFeedback = window.ValidationFeedback;
    const GlobalValidationStatus = window.GlobalValidationStatus;
    const PatternLineValidator = window.PatternLineValidator;
    const TileCountValidator = window.TileCountValidator;
    
    // Save state to undo stack before changes
    const saveToUndoStack = useCallback(() => {
        if (gameState) {
            setUndoStack(prev => [...prev.slice(-9), JSON.parse(JSON.stringify(gameState))]);
            setRedoStack([]);
        }
    }, [gameState]);
    
    // Enhanced pattern line editing with validation
    const editPatternLine = useCallback(async (playerIndex, lineIndex, newColor, newCount) => {
        if (!gameState || !validationEnabled) return;
        
        const agent = gameState.agents[playerIndex];
        const currentColor = agent.lines_tile[lineIndex];
        const currentCount = agent.lines_number[lineIndex];
        
        // Real-time validation
        try {
            const response = await fetch('/api/v1/validate-pattern-line-edit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_color: currentColor,
                    new_color: newColor,
                    current_count: currentCount,
                    new_count: newCount,
                    line_index: lineIndex
                })
            });
            
            const validation = await response.json();
            
            if (!validation.valid) {
                setStatusMessage(`❌ ${validation.error}`);
                return false;
            }
            
            // Save to undo stack before making changes
            saveToUndoStack();
            
            // Apply the change
            const newGameState = JSON.parse(JSON.stringify(gameState));
            newGameState.agents[playerIndex].lines_tile[lineIndex] = newColor;
            newGameState.agents[playerIndex].lines_number[lineIndex] = newCount;
            
            await setGameState(newGameState);
            setStatusMessage(`✅ Pattern line ${lineIndex + 1} updated`);
            return true;
            
        } catch (error) {
            console.error('Validation error:', error);
            setStatusMessage(`⚠️ Validation failed: ${error.message}`);
            return false;
        }
    }, [gameState, validationEnabled, saveToUndoStack, setGameState, setStatusMessage]);
    
    // Enhanced factory editing with validation
    const editFactory = useCallback(async (factoryIndex, color, change) => {
        if (!gameState || !validationEnabled) return;
        
        const factory = gameState.factories[factoryIndex];
        const currentCount = factory.tiles[color] || 0;
        const newCount = Math.max(0, currentCount + change);
        
        // Validate tile conservation
        try {
            const response = await fetch('/api/v1/validate-tile-count', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    game_state: gameState,
                    changed_color: color,
                    changed_amount: change
                })
            });
            
            const validation = await response.json();
            
            if (!validation.valid) {
                setStatusMessage(`❌ ${validation.error}`);
                return false;
            }
            
            // Save to undo stack
            saveToUndoStack();
            
            // Apply change
            const newGameState = JSON.parse(JSON.stringify(gameState));
            newGameState.factories[factoryIndex].tiles[color] = newCount;
            
            // Update total count
            newGameState.factories[factoryIndex].total = Object.values(newGameState.factories[factoryIndex].tiles).reduce((sum, count) => sum + count, 0);
            
            await setGameState(newGameState);
            setStatusMessage(`✅ Factory ${factoryIndex + 1} updated`);
            return true;
            
        } catch (error) {
            console.error('Validation error:', error);
            setStatusMessage(`⚠️ Validation failed: ${error.message}`);
            return false;
        }
    }, [gameState, validationEnabled, saveToUndoStack, setGameState, setStatusMessage]);
    
    // Wall tile editing with validation
    const editWallTile = useCallback(async (playerIndex, row, col, shouldPlace) => {
        if (!gameState || !validationEnabled) return;
        
        saveToUndoStack();
        
        const newGameState = JSON.parse(JSON.stringify(gameState));
        newGameState.agents[playerIndex].grid_state[row][col] = shouldPlace ? 1 : 0;
        
        await setGameState(newGameState);
        setStatusMessage(`✅ Wall tile ${shouldPlace ? 'placed' : 'removed'}`);
        return true;
    }, [gameState, validationEnabled, saveToUndoStack, setGameState, setStatusMessage]);
    
    // Position templates
    const positionTemplateOptions = [
        {
            name: "Starting Position",
            description: "Fresh game start with full factories",
            generate: () => ({
                // Generate standard starting position
                factories: Array(5).fill().map(() => ({
                    tiles: { 0: 4, 1: 0, 2: 0, 3: 0, 4: 0 },
                    total: 4
                })),
                centre_pool: { tiles: {}, total: 0 },
                agents: Array(2).fill().map(() => ({
                    lines_tile: [-1, -1, -1, -1, -1],
                    lines_number: [0, 0, 0, 0, 0],
                    grid_state: Array(5).fill().map(() => Array(5).fill(0)),
                    floor_tiles: [],
                    score: 0
                }))
            })
        },
        {
            name: "Mid-Game Scenario",
            description: "Half-completed walls with pattern lines",
            generate: () => ({
                // Generate mid-game position
                factories: Array(5).fill().map((_, i) => ({
                    tiles: { 0: i % 2, 1: (i + 1) % 3, 2: (i + 2) % 2, 3: 0, 4: i % 2 },
                    total: (i % 2) + ((i + 1) % 3) + ((i + 2) % 2) + (i % 2)
                })),
                centre_pool: { tiles: { 0: 2, 1: 1 }, total: 3 },
                agents: Array(2).fill().map((_, playerIdx) => ({
                    lines_tile: [0, 1, -1, 2, -1],
                    lines_number: [1, 2, 0, 3, 0],
                    grid_state: Array(5).fill().map((_, row) => 
                        Array(5).fill().map((_, col) => (row + col) % 3 === playerIdx ? 1 : 0)
                    ),
                    floor_tiles: [],
                    score: 15 + playerIdx * 5
                }))
            })
        },
        {
            name: "Endgame Position",
            description: "Nearly completed walls, final scoring",
            generate: () => ({
                // Generate endgame position
                factories: Array(5).fill().map(() => ({
                    tiles: { 0: 0, 1: 0, 2: 1, 3: 0, 4: 0 },
                    total: 1
                })),
                centre_pool: { tiles: { 2: 3, 4: 1 }, total: 4 },
                agents: Array(2).fill().map((_, playerIdx) => ({
                    lines_tile: [-1, -1, 2, -1, 4],
                    lines_number: [0, 0, 3, 0, 1],
                    grid_state: Array(5).fill().map((_, row) => 
                        Array(5).fill().map((_, col) => row < 3 ? 1 : 0)
                    ),
                    floor_tiles: [2, 4],
                    score: 45 + playerIdx * 8
                }))
            })
        }
    ];
    
    // Load position template
    const loadTemplate = useCallback(async (template) => {
        try {
            saveToUndoStack();
            const newState = template.generate();
            
            // Validate the generated position
            if (validationEnabled) {
                const response = await fetch('/api/v1/validate-board-state', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${sessionToken}`
                    },
                    body: JSON.stringify({
                        game_state: newState,
                        validation_type: 'complete'
                    })
                });
                
                const validation = await response.json();
                if (!validation.valid) {
                    setStatusMessage(`❌ Template validation failed: ${validation.errors[0]}`);
                    return;
                }
            }
            
            setGameState(newState);
            setStatusMessage(`✅ Loaded template: ${template.name}`);
            setShowTemplatePanel(false);
            
        } catch (error) {
            console.error('Template loading error:', error);
            setStatusMessage(`⚠️ Failed to load template: ${error.message}`);
        }
    }, [saveToUndoStack, validationEnabled, sessionToken, setGameState, setStatusMessage]);
    
    // Undo/Redo functionality
    const handleUndo = useCallback(() => {
        if (undoStack.length === 0) return;
        
        const previousState = undoStack[undoStack.length - 1];
        setRedoStack(prev => [gameState, ...prev.slice(0, 9)]);
        setUndoStack(prev => prev.slice(0, -1));
        setGameState(previousState);
        setStatusMessage('↶ Undid last change');
    }, [undoStack, gameState, setGameState, setStatusMessage]);
    
    const handleRedo = useCallback(() => {
        if (redoStack.length === 0) return;
        
        const nextState = redoStack[0];
        setUndoStack(prev => [...prev.slice(-9), gameState]);
        setRedoStack(prev => prev.slice(1));
        setGameState(nextState);
        setStatusMessage('↷ Redid last change');
    }, [redoStack, gameState, setGameState, setStatusMessage]);
    
    // Render the enhanced board editor UI
    if (!editMode) return null;
    
    return React.createElement('div', {
        className: 'board-editor-overlay'
    },
        // Enhanced edit mode controls
        React.createElement('div', {
            className: 'edit-controls-panel'
        },
            React.createElement('div', {
                className: 'edit-controls-header'
            },
                React.createElement('h3', null, '🛠️ Board Editor'),
                React.createElement('div', {
                    className: 'edit-controls-actions'
                },
                    React.createElement('button', {
                        className: `btn-sm ${validationEnabled ? 'btn-success' : 'btn-secondary'}`,
                        onClick: () => setValidationEnabled(!validationEnabled)
                    }, validationEnabled ? '✅ Validation On' : '⚠️ Validation Off'),
                    React.createElement('button', {
                        className: 'btn-sm btn-primary',
                        onClick: () => setShowTemplatePanel(!showTemplatePanel)
                    }, '📋 Templates'),
                    React.createElement('button', {
                        className: 'btn-sm btn-secondary',
                        onClick: handleUndo,
                        disabled: undoStack.length === 0
                    }, '↶ Undo'),
                    React.createElement('button', {
                        className: 'btn-sm btn-secondary',
                        onClick: handleRedo,
                        disabled: redoStack.length === 0
                    }, '↷ Redo')
                )
            ),
            
            // Validation status panel
            validationEnabled && showValidationPanel && React.createElement('div', {
                className: 'validation-panel'
            },
                React.createElement('h4', null, '🔍 Validation Status'),
                GlobalValidationStatus && React.createElement(GlobalValidationStatus, {
                    gameState: gameState
                })
            ),
            
            // Position templates panel
            showTemplatePanel && React.createElement('div', {
                className: 'templates-panel'
            },
                React.createElement('h4', null, '📋 Position Templates'),
                React.createElement('div', {
                    className: 'template-grid'
                },
                    ...positionTemplateOptions.map((template, index) =>
                        React.createElement('div', {
                            key: index,
                            className: 'template-card',
                            onClick: () => loadTemplate(template)
                        },
                            React.createElement('h5', null, template.name),
                            React.createElement('p', null, template.description),
                            React.createElement('button', {
                                className: 'btn-sm btn-primary'
                            }, 'Load Template')
                        )
                    )
                )
            )
        ),
        
        // Enhanced editing hints
        React.createElement('div', {
            className: 'edit-hints-panel'
        },
            React.createElement('h4', null, '💡 Editing Hints'),
            React.createElement('ul', null,
                React.createElement('li', null, '🎯 Click elements to select them'),
                React.createElement('li', null, '🎨 Use keys 1-5 to set tile colors'),
                React.createElement('li', null, '🗑️ Press Delete to remove tiles'),
                React.createElement('li', null, '📋 Ctrl+C/V to copy/paste'),
                React.createElement('li', null, '⚡ Real-time validation prevents illegal moves'),
                React.createElement('li', null, '📚 Use templates for quick setup')
            )
        )
    );
}

window.BoardEditor = BoardEditor;