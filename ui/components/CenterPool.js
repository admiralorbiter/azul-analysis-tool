// CenterPool.js - Center pool component for displaying tiles in the middle area
const { useState } = React;

// Import components from window
const Tile = window.Tile;

window.CenterPool = function CenterPool({
    gameState,
    editMode,
    selectedTile,
    setSelectedTile,
    handleElementSelect,
    selectedElements,
    heatmapEnabled,
    heatmapData
}) {
    // Convert center tiles to array format for display
    const getTilesArray = () => {
        if (!gameState.center || !Array.isArray(gameState.center)) {
            return [];
        }
        
        // gameState.center is already an array of tile strings (e.g., ['B', 'Y', 'R'])
        return gameState.center;
    };

    const tiles = getTilesArray();
    const totalTiles = tiles.length;
    
    // Check if first player marker is available (not taken yet)
    const firstPlayerMarkerAvailable = !gameState.first_player_taken;

    return React.createElement('div', {
        className: 'bg-white rounded p-3 shadow-sm'
    },
        React.createElement('div', {
            className: 'flex items-center justify-between mb-2'
        },
            React.createElement('h3', {
                className: 'font-medium text-sm'
            }, '🎯 Center Pool'),
            React.createElement('span', {
                className: 'text-xs text-gray-500'
            }, `${totalTiles} tiles`)
        ),
        
        React.createElement('div', {
            className: 'min-h-[60px] bg-gray-50 rounded p-2 border-2 border-dashed border-gray-200'
        },
            // First player marker display
            firstPlayerMarkerAvailable && 
            React.createElement('div', {
                className: 'mb-2 p-2 bg-yellow-100 border-2 border-yellow-300 rounded flex items-center justify-center'
            },
                React.createElement('div', {
                    className: 'flex items-center space-x-2'
                },
                    React.createElement('span', {
                        className: 'text-2xl'
                    }, '⭐'),
                    React.createElement('span', {
                        className: 'text-sm font-medium text-yellow-800'
                    }, 'First Player Marker'),
                    React.createElement('span', {
                        className: 'text-xs text-yellow-600 bg-yellow-200 px-2 py-1 rounded'
                    }, '-1 penalty')
                )
            ),
            
            // Regular tiles display
            totalTiles > 0 ? 
                React.createElement('div', {
                    className: 'flex flex-wrap gap-1'
                },
                    tiles.map((tile, index) => 
                        React.createElement(Tile, {
                            key: `center-${index}`,
                            color: tile,
                            draggable: true,
                            onDragStart: (e) => {
                                const dragData = {
                                    sourceType: 'center',
                                    sourceId: 'center',
                                    tileIndex: index,
                                    tile: tile
                                };
                                e.dataTransfer.setData('application/json', JSON.stringify(dragData));
                                e.dataTransfer.effectAllowed = 'move';
                            },
                            onClick: (e) => {
                                if (editMode && handleElementSelect) {
                                    const isCtrlClick = e.ctrlKey || e.metaKey;
                                    handleElementSelect({
                                        type: 'center-tile',
                                        data: { sourceId: 'center', tileIndex: index, tile }
                                    }, isCtrlClick);
                                } else if (editMode) {
                                    setSelectedTile({ 
                                        sourceId: 'center', 
                                        tileIndex: index, 
                                        tile: tile 
                                    });
                                }
                            },
                            selected: selectedTile && 
                                     selectedTile.sourceId === 'center' && 
                                     selectedTile.tileIndex === index,
                            editMode: editMode,
                            onElementSelect: handleElementSelect,
                            selectedElements: selectedElements,
                            heatmapEnabled: heatmapEnabled,
                            heatmapData: heatmapData
                        })
                    )
                ) :
                React.createElement('div', {
                    className: 'flex items-center justify-center h-full text-gray-400 text-sm'
                }, 'No tiles in center pool')
        ),
        
        // First player marker status
        gameState.first_player_taken && 
        React.createElement('div', {
            className: 'mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700'
        }, 
            React.createElement('div', {
                className: 'flex items-center space-x-1'
            },
                React.createElement('span', {
                    className: 'text-blue-600'
                }, '✅'),
                React.createElement('span', {
                    className: 'font-medium'
                }, 'First player marker taken')
            )
        )
    );
}; 