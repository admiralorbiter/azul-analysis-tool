// PatternLine Component
// Pattern line component for displaying tiles in player boards
// Enhanced with R1.1 validation integration

function PatternLine({ tiles, rowIndex, maxTiles, onTileClick, onDrop, selectedTile = null, onDestinationClick = null, editMode = false, onElementSelect = null, playerIndex = null, selectedElements = [], gameState = null, onPatternLineEdit = null }) {
    const patternLineRef = React.useRef(null);
    const [validationResult, setValidationResult] = React.useState(null);
    
    // Import validation components
    const PatternLineValidator = window.PatternLineValidator;
    const ValidationFeedback = window.ValidationFeedback;
    
    React.useEffect(() => {
        const patternLine = patternLineRef.current;
        if (!patternLine) return;
        
        const handleDragOver = (e) => {
            e.preventDefault();
            e.currentTarget.classList.add('drag-over');
        };
        
        const handleDragLeave = (e) => {
            e.currentTarget.classList.remove('drag-over');
        };
        
        const handleDrop = (e) => {
            e.preventDefault();
            e.currentTarget.classList.remove('drag-over');
            if (onDrop) onDrop(e, rowIndex);
        };
        
        patternLine.addEventListener('dragover', handleDragOver);
        patternLine.addEventListener('dragleave', handleDragLeave);
        patternLine.addEventListener('drop', handleDrop);
        
        return () => {
            patternLine.removeEventListener('dragover', handleDragOver);
            patternLine.removeEventListener('dragleave', handleDragLeave);
            patternLine.removeEventListener('drop', handleDrop);
        };
    }, [onDrop, rowIndex]);
    
    // Real-time validation for edit mode
    React.useEffect(() => {
        if (editMode && gameState && PatternLineValidator && playerIndex !== null) {
            // Get current pattern line state
            const agent = gameState.agents?.[playerIndex];
            if (agent) {
                const currentColor = agent.lines_tile?.[rowIndex] || -1;
                const currentCount = agent.lines_number?.[rowIndex] || 0;
                
                // Trigger validation check (simplified for demo)
                const result = {
                    valid: currentColor === -1 || currentCount <= maxTiles,
                    error: currentCount > maxTiles ? `Too many tiles: ${currentCount}/${maxTiles}` : null
                };
                setValidationResult(result);
            }
        }
    }, [editMode, gameState, playerIndex, rowIndex, maxTiles]);

    const handlePatternLineClick = (e) => {
        if (editMode && onElementSelect) {
            const isCtrlClick = e.ctrlKey;
            onElementSelect({
                type: 'pattern-line',
                data: { playerIndex, rowIndex, tiles, maxTiles }
            }, isCtrlClick);
        }
    };
    
    const handlePatternLineEdit = async (newColor, newCount) => {
        if (editMode && onPatternLineEdit) {
            const success = await onPatternLineEdit(playerIndex, rowIndex, newColor, newCount);
            if (success) {
                // Update validation state
                setValidationResult({ valid: true });
            }
        }
    };
    
    const handlePatternLineRightClick = (e) => {
        e.preventDefault();
        if (editMode && window.showContextMenu) {
            window.showContextMenu(e, 'pattern-line', { playerIndex, rowIndex, tiles });
        }
    };
    
    const isSelected = editMode && selectedElements.some(el => el.type === 'pattern-line' && el.data.rowIndex === rowIndex && el.data.playerIndex === playerIndex);
    const isEditSelected = editMode && isSelected;
    
    return React.createElement('div', {
        ref: patternLineRef,
        className: `pattern-line ${isEditSelected ? 'selected' : ''}`,
        onClick: handlePatternLineClick,
        onContextMenu: handlePatternLineRightClick
    },
        React.createElement('div', {
            className: 'flex items-center gap-2'
        },
            // Row label - more compact
            React.createElement('div', {
                className: 'text-xs text-gray-600 font-medium w-8 flex-shrink-0'
            }, `R${rowIndex + 1}`),
            React.createElement('div', {
                className: 'flex gap-1 flex-wrap'
            },
                tiles.map((tile, index) => 
                    React.createElement(Tile, {
                        key: index,
                        color: tile,
                        className: 'w-6 h-6',
                        onClick: () => onTileClick ? onTileClick(rowIndex, index, tile) : null
                    })
                ),
                Array.from({ length: maxTiles - tiles.length }, (_, index) => 
                    React.createElement('div', {
                        key: `empty-${index}`,
                        className: 'w-6 h-6 border border-gray-300 rounded bg-gray-50',
                        onClick: () => onDestinationClick ? onDestinationClick(rowIndex, tiles.length + index) : null
                    })
                )
            )
        ),
        
        // Add validation feedback for edit mode
        editMode && validationResult && !validationResult.valid && ValidationFeedback && React.createElement(ValidationFeedback, {
            validationResult: validationResult,
            position: 'right'
        }),
        
        // Add pattern line validator for real-time feedback
        editMode && PatternLineValidator && gameState && React.createElement(PatternLineValidator, {
            playerId: playerIndex,
            lineIndex: rowIndex,
            currentColor: gameState.agents?.[playerIndex]?.lines_tile?.[rowIndex] || -1,
            newColor: gameState.agents?.[playerIndex]?.lines_tile?.[rowIndex] || -1,
            currentCount: gameState.agents?.[playerIndex]?.lines_number?.[rowIndex] || 0,
            newCount: gameState.agents?.[playerIndex]?.lines_number?.[rowIndex] || 0
        })
    );
}

// Export for global access
window.PatternLine = PatternLine; 