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
                            onClick: () => {
                                if (editMode) {
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
        
        // First player marker indicator
        gameState.first_player_taken && 
        React.createElement('div', {
            className: 'mt-2 text-xs text-blue-600 font-medium'
        }, '⭐ First player marker taken')
    );
}; 