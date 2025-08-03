// Wall Component
// Extracted from main.js

function Wall({ wall, onWallClick, onDrop, selectedTile = null, onDestinationClick = null, editMode = false, onElementSelect = null, playerIndex = null, selectedElements = [] }) {
    const wallRef = React.useRef(null);
    
    React.useEffect(() => {
        const wall = wallRef.current;
        if (!wall) return;
        
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
            if (onDrop) onDrop(e);
        };
        
        wall.addEventListener('dragover', handleDragOver);
        wall.addEventListener('dragleave', handleDragLeave);
        wall.addEventListener('drop', handleDrop);
        
        return () => {
            wall.removeEventListener('dragover', handleDragOver);
            wall.removeEventListener('dragleave', handleDragLeave);
            wall.removeEventListener('drop', handleDrop);
        };
    }, [onDrop]);
    
    return React.createElement('div', {
        ref: wallRef,
        className: 'wall'
    },
        // Column labels - more compact
        React.createElement('div', {
            className: 'flex gap-1 mb-1'
        },
            React.createElement('div', { 
                className: 'w-6 h-4 text-xs text-gray-500 font-medium flex items-center justify-center' 
            }, ''),
            ['B', 'Y', 'R', 'K', 'W'].map((color, index) => 
                React.createElement('div', {
                    key: index,
                    className: 'w-6 h-4 text-xs text-gray-600 font-medium flex items-center justify-center'
                }, color)
            )
        ),
        wall.map((row, rowIndex) => 
            React.createElement('div', {
                key: rowIndex,
                className: 'flex gap-1 mb-1'
            },
                // Row label - more compact
                React.createElement('div', {
                    className: 'w-6 h-6 text-xs text-gray-600 font-medium flex items-center justify-center'
                }, `R${rowIndex + 1}`),
                row.map((cell, colIndex) => {
                    const isSelected = editMode && selectedElements.some(el => 
                        el.type === 'wall-cell' && 
                        el.data.playerIndex === playerIndex && 
                        el.data.rowIndex === rowIndex && 
                        el.data.colIndex === colIndex
                    );
                    
                    return React.createElement('div', {
                        key: colIndex,
                        className: `w-6 h-6 border border-gray-300 rounded flex items-center justify-center ${cell ? 'bg-gray-100' : 'bg-white'} ${isSelected ? 'ring-2 ring-blue-500' : ''}`,
                        onClick: (e) => {
                            if (editMode && onElementSelect) {
                                const isCtrlClick = e.ctrlKey;
                                onElementSelect({
                                    type: 'wall-cell',
                                    data: { playerIndex, rowIndex, colIndex, cell }
                                }, isCtrlClick);
                            } else if (onWallClick) {
                                onWallClick(rowIndex, colIndex, cell);
                            }
                        },
                        onContextMenu: (e) => {
                            e.preventDefault();
                            if (editMode && window.showContextMenu) {
                                window.showContextMenu(e, 'wall', { playerIndex, rowIndex, colIndex, cell });
                            }
                        }
                    },
                        cell ? React.createElement(window.Tile, { 
                            color: cell,
                            className: 'w-4 h-4'
                        }) : null
                    );
                })
            )
        )
    );
}

window.Wall = Wall; 