// Enhanced Player Board Component with active player indication
// Using global React for compatibility

function PlayerBoard({ 
    player, 
    playerIndex, 
    onPatternLineClick, 
    onWallClick, 
    onPatternLineDrop, 
    onWallDrop, 
    selectedTile = null, 
    onDestinationClick = null,
    isActive = false,
    onPlayerSwitch = null,
    canInteract = true,
    gameMode = 'sandbox',
    editMode = false,
    onElementSelect = null,
    selectedElement = null
}) {
    const borderClass = isActive ? 'border-4 border-blue-500 bg-blue-50' : 'border-2 border-gray-300 bg-gray-50';
    const headerClass = isActive ? 'text-blue-700 font-bold' : 'text-gray-700';
    
    return React.createElement('div', {
        className: `${borderClass} p-4 rounded-lg mb-4 transition-all duration-200`
    },
        // Player Header with Enhanced Score Display
        React.createElement('div', {
            className: 'mb-3'
        },
            React.createElement('div', {
                className: `flex justify-between items-center mb-2 ${headerClass}`
            },
                React.createElement('h3', {
                    className: 'text-lg font-semibold'
                }, `Player ${playerIndex + 1}`),
                React.createElement('button', {
                    className: 'px-2 py-1 bg-gray-500 text-white rounded text-xs hover:bg-gray-600 transition-colors',
                    onClick: () => onPlayerSwitch ? onPlayerSwitch(playerIndex) : null
                }, 'Switch')
            ),
            // Enhanced Score Display
            React.createElement(window.ScoreDisplay, {
                player: player,
                playerIndex: playerIndex,
                isActive: isActive
            })
        ),

        // Pattern Lines
        React.createElement('div', {
            className: 'mb-4'
        },
            React.createElement('h5', {
                className: 'text-sm font-medium mb-2'
            }, 'Pattern Lines'),
            React.createElement('div', {
                className: 'space-y-2'
            },
                (player.pattern_lines || []).map((line, index) => 
                    React.createElement(window.PatternLine, {
                        key: index,
                        tiles: line,
                        rowIndex: index,
                        maxTiles: index + 1,
                        onTileClick: onPatternLineClick,
                        onDrop: onPatternLineDrop,
                        selectedTile: selectedTile,
                        onDestinationClick: onDestinationClick,
                        editMode: editMode,
                        onElementSelect: onElementSelect,
                        playerIndex: playerIndex,
                        selectedElement: selectedElement
                    })
                )
            )
        ),

        // Wall
        React.createElement('div', {
            className: 'mb-4'
        },
            React.createElement('h5', {
                className: 'text-sm font-medium mb-2'
            }, 'Wall'),
            React.createElement(window.Wall, {
                wall: player.wall || Array(5).fill().map(() => Array(5).fill(null)),
                onWallClick: onWallClick,
                onDrop: onWallDrop,
                selectedTile: selectedTile,
                onDestinationClick: onDestinationClick,
                editMode: editMode,
                onElementSelect: onElementSelect,
                playerIndex: playerIndex,
                selectedElement: selectedElement
            })
        ),
        
        // Floor
        React.createElement('div', {
            className: 'bg-gray-100 p-3 rounded-lg border border-gray-300'
        },
            React.createElement('div', {
                className: 'flex justify-between items-center mb-3'
            },
                React.createElement('h5', {
                    className: 'text-sm font-semibold text-gray-800'
                }, 'Floor Line'),
                React.createElement('div', {
                    className: 'flex items-center gap-2'
                },
                    React.createElement('span', {
                        className: 'text-xs text-gray-600'
                    }, 'Penalty:'),
                    React.createElement('span', {
                        className: 'text-sm font-bold text-red-600 bg-red-100 px-2 py-1 rounded'
                    }, `-${(player.floor_line || player.floor || []).length}`),
                    React.createElement('span', {
                        className: 'text-xs text-gray-500 ml-2'
                    }, `(${(player.floor_line || player.floor || []).length} tiles)`)
                )
            ),
            React.createElement('div', {
                className: 'flex gap-2'
            },
                (player.floor_line || player.floor || []).map((tile, index) => {
                    const isValidDestination = selectedTile && onDestinationClick;
                    
                    return React.createElement('div', {
                        key: index,
                        className: `floor-tile ${isValidDestination ? 'valid-drop' : ''}`,
                        onClick: () => {
                            if (isValidDestination) {
                                onDestinationClick('floor', { index });
                            }
                        }
                    },
                        tile && React.createElement(window.Tile, { 
                            color: tile,
                            className: 'w-8 h-8 shadow-sm'
                        })
                    );
                }),
                Array.from({ length: 7 - (player.floor_line || player.floor || []).length }, (_, index) => 
                    React.createElement('div', {
                        key: `empty-floor-${index}`,
                        className: 'w-8 h-8 border-2 border-dashed border-gray-400 rounded-lg bg-gray-50'
                    })
                )
            )
        )
    );
}

// Attach to window for backward compatibility
window.PlayerBoard = PlayerBoard; 