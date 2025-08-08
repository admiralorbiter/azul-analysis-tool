// Wall Component with enhanced visual design
// Using global React and window.gameConstants for compatibility



function Wall({ 
    wall, 
    onWallClick, 
    onDrop, 
    selectedTile = null, 
    onDestinationClick = null, 
    editMode = false, 
    onElementSelect = null, 
    playerIndex = null, 
    selectedElement = null 
}) {
    const wallRef = React.useRef(null);
    const [colorsLoaded, setColorsLoaded] = React.useState(false);
    
    // Check if gameConstants are loaded
    React.useEffect(() => {
        const checkColors = () => {
            if (window.gameConstants?.TILE_COLORS) {
                setColorsLoaded(true);
            } else {
                setTimeout(checkColors, 100);
            }
        };
        checkColors();
    }, []);
    
    // Azul wall color pattern - each row has a different starting color
    const wallColorPattern = [
        ['B', 'Y', 'R', 'K', 'W'], // Row 1: Blue, Yellow, Red, Black, White
        ['W', 'B', 'Y', 'R', 'K'], // Row 2: White, Blue, Yellow, Red, Black
        ['K', 'W', 'B', 'Y', 'R'], // Row 3: Black, White, Blue, Yellow, Red
        ['R', 'K', 'W', 'B', 'Y'], // Row 4: Red, Black, White, Blue, Yellow
        ['Y', 'R', 'K', 'W', 'B']  // Row 5: Yellow, Red, Black, White, Blue
    ];
    
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
            
            const tileData = e.dataTransfer.getData('application/json');
            if (tileData) {
                const data = JSON.parse(tileData);
                const rowIndex = parseInt(e.currentTarget.dataset.row);
                const colIndex = parseInt(e.currentTarget.dataset.col);
                if (onDrop) {
                    onDrop(data, rowIndex, colIndex);
                }
            }
        };
        
        const cells = wall.querySelectorAll('.wall-cell');
        cells.forEach(cell => {
            cell.addEventListener('dragover', handleDragOver);
            cell.addEventListener('dragleave', handleDragLeave);
            cell.addEventListener('drop', handleDrop);
        });
        
        return () => {
            cells.forEach(cell => {
                cell.removeEventListener('dragover', handleDragOver);
                cell.removeEventListener('dragleave', handleDragLeave);
                cell.removeEventListener('drop', handleDrop);
            });
        };
    }, [onDrop]);
    
    return React.createElement('div', {
        ref: wallRef,
        className: 'wall-container'
    },
        // Enhanced header with clear labeling
        React.createElement('div', {
            className: 'wall-header'
        },
            React.createElement('div', {
                className: 'wall-title'
            }, 'Wall'),
            React.createElement('div', {
                className: 'wall-subtitle'
            }, 'Complete rows and columns for bonus points')
        ),
        
        // Column labels with color indicators
        React.createElement('div', {
            className: 'wall-column-labels'
        },
            React.createElement('div', {
                className: 'wall-corner-label'
            }),
            ['B', 'Y', 'R', 'K', 'W'].map((color, index) => 
                React.createElement('div', {
                    key: index,
                    className: 'wall-column-label'
                },
                    React.createElement('div', {
                        className: 'color-indicator',
                        style: { backgroundColor: colorsLoaded ? (window.gameConstants?.TILE_COLORS?.[color] || '#6b7280') : '#6b7280' }
                    }),
                    React.createElement('span', {
                        className: 'color-letter'
                    }, color)
                )
            )
        ),
        
        // Wall grid with enhanced styling
        wall.map((row, rowIndex) => 
            React.createElement('div', {
                key: rowIndex,
                className: 'wall-row'
            },
                // Row label with row number
                React.createElement('div', {
                    className: 'wall-row-label'
                },
                    React.createElement('span', {
                        className: 'row-number'
                    }, `R${rowIndex + 1}`)
                ),
                
                // Wall cells with color pattern indicators
                row.map((cell, colIndex) => {
                    const isValidDestination = selectedTile && onDestinationClick && !cell;
                    const expectedColor = wallColorPattern[rowIndex][colIndex];
                    

                    
                    // Check if this wall cell is selected in edit mode
                    const isEditSelected = selectedElement && 
                        selectedElement.type === 'wall-cell' && 
                        selectedElement.data.playerIndex === playerIndex && 
                        selectedElement.data.rowIndex === rowIndex && 
                        selectedElement.data.colIndex === colIndex;
                    
                    return React.createElement('div', {
                        key: `${rowIndex}-${colIndex}`,
                        className: `wall-cell ${cell ? 'occupied' : 'empty'} ${isValidDestination ? 'valid-drop' : ''} ${isEditSelected ? 'selected' : ''}`,
                        onClick: () => {
                            if (editMode && onElementSelect) {
                                onElementSelect('wall-cell', { playerIndex, rowIndex, colIndex, tile: cell });
                            } else if (isValidDestination) {
                                onDestinationClick('wall', { rowIndex, colIndex });
                            } else {
                                onWallClick(rowIndex, colIndex);
                            }
                        },
                        onContextMenu: (event) => {
                            if (editMode) {
                                event.preventDefault();
                                if (window.showContextMenu) {
                                    window.showContextMenu(event, 'wall-cell', { playerIndex, rowIndex, colIndex, tile: cell });
                                }
                            }
                        },
                        'data-row': rowIndex,
                        'data-col': colIndex
                    },
                        // Show placed tile or color pattern indicator
                        cell ? 
                            React.createElement(window.Tile, { 
                                color: cell,
                                className: 'wall-tile'
                            }) :
                            React.createElement('div', {
                                className: 'color-pattern-indicator',
                                style: { 
                                    backgroundColor: colorsLoaded ? (window.gameConstants?.TILE_COLORS?.[expectedColor] || '#e5e7eb') : '#e5e7eb'
                                }
                            })
                    );
                })
            )
        ),
        
        // Wall completion indicators
        React.createElement('div', {
            className: 'wall-completion-info'
        },
            React.createElement('div', {
                className: 'completion-tip'
            },
                React.createElement('span', {
                    className: 'tip-icon'
                }, '💡'),
                React.createElement('span', {
                    className: 'tip-text'
                }, 'Complete rows (5 tiles) = 2 points each, Complete columns = 7 points each')
            )
        )
    );
}

// Attach to window for backward compatibility
window.Wall = Wall; 