// PatternLine Component
// Pattern line component for displaying tiles in player boards

function PatternLine({ tiles, rowIndex, maxTiles, onTileClick, onDrop, selectedTile = null, onDestinationClick = null, editMode = false, onElementSelect = null, playerIndex = null, selectedElements = [] }) {
    const patternLineRef = React.useRef(null);
    
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
    
    const handlePatternLineClick = (e) => {
        if (editMode && onElementSelect) {
            const isCtrlClick = e.ctrlKey;
            onElementSelect({
                type: 'pattern-line',
                data: { playerIndex, rowIndex, tiles, maxTiles }
            }, isCtrlClick);
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
        )
    );
}

// Export for global access
window.PatternLine = PatternLine; 