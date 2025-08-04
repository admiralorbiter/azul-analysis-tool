// PlayerBoard Component
// Extracted from main.js

function PlayerBoard({ player, playerIndex, onPatternLineClick, onWallClick, onPatternLineDrop, onWallDrop, selectedTile = null, onDestinationClick = null, isActive = false, onPlayerSwitch = null, canInteract = true, gameMode = 'sandbox', editMode = false, onElementSelect = null, selectedElements = [] }) {
    const borderClass = isActive ? 'border-4 border-blue-500 bg-blue-50' : 'border-2 border-gray-300 bg-gray-50';
    const headerClass = isActive ? 'text-blue-700 font-bold' : 'text-gray-700';
    
    return React.createElement('div', {
        className: `player-board ${borderClass} p-3 rounded-lg mb-3`
    },
        React.createElement('div', {
            className: `flex justify-between items-center mb-3 ${headerClass}`
        },
            React.createElement('h3', {
                className: 'text-lg font-semibold'
            }, `Player ${playerIndex + 1}`),
            React.createElement('div', {
                className: 'flex space-x-2 items-center'
            },
                React.createElement('button', {
                    className: 'px-2 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600',
                    onClick: () => onPlayerSwitch ? onPlayerSwitch(playerIndex) : null
                }, 'Switch'),
                React.createElement('span', {
                    className: 'text-sm font-medium'
                }, `Score: ${player.score || 0}`)
            )
        ),
        React.createElement('div', {
            className: 'grid grid-cols-2 gap-3'
        },
            React.createElement('div', {
                className: 'pattern-lines'
            },
                React.createElement('h4', {
                    className: 'text-sm font-medium mb-2 text-gray-700'
                }, 'Pattern Lines'),
                player.pattern_lines.map((line, index) => 
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
                        selectedElements: selectedElements
                    })
                )
            ),
            React.createElement('div', {
                className: 'wall-section'
            },
                React.createElement('h4', {
                    className: 'text-sm font-medium mb-2 text-gray-700'
                }, 'Wall'),
                React.createElement(window.Wall, {
                    wall: player.wall,
                    onWallClick: onWallClick,
                    onDrop: onWallDrop,
                    selectedTile: selectedTile,
                    onDestinationClick: onDestinationClick,
                    editMode: editMode,
                    onElementSelect: onElementSelect,
                    playerIndex: playerIndex,
                    selectedElements: selectedElements
                })
            )
        ),
        React.createElement('div', {
            className: 'floor-line mt-3 bg-gray-100 p-3 rounded-lg border border-gray-300'
        },
            React.createElement('div', {
                className: 'flex justify-between items-center mb-3'
            },
                React.createElement('h4', {
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
                className: 'flex flex-wrap gap-2'
            },
                (player.floor_line || player.floor || []).map((tile, index) => 
                    tile === 'FP' ? 
                        // First player marker
                        React.createElement('div', {
                            key: index,
                            className: 'w-8 h-8 bg-yellow-200 border-2 border-yellow-500 rounded-lg flex items-center justify-center shadow-sm',
                            title: 'First Player Marker (-1 penalty)'
                        },
                            React.createElement('span', {
                                className: 'text-sm text-yellow-700 font-bold'
                            }, '⭐')
                        ) :
                        // Regular tile
                        React.createElement(window.Tile, {
                            key: index,
                            color: tile,
                            className: 'w-8 h-8 shadow-sm'
                        })
                ),
                Array.from({ length: 7 - (player.floor_line || player.floor || []).length }, (_, index) => 
                    React.createElement('div', {
                        key: `empty-floor-${index}`,
                        className: 'w-8 h-8 border-2 border-dashed border-gray-400 rounded-lg bg-gray-50',
                        onContextMenu: (e) => {
                            e.preventDefault();
                            if (editMode && window.showContextMenu) {
                                window.showContextMenu(e, 'floor', { playerIndex, floorIndex: index });
                            }
                        }
                    })
                )
            )
        )
    );
}

window.PlayerBoard = PlayerBoard; 