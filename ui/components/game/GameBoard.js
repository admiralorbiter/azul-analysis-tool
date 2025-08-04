// GameBoard.js - Game board component with factories, center pool, and player boards
const { useState } = React;

// Import components from window
const Factory = window.Factory;
const PlayerBoard = window.PlayerBoard;
const CenterPool = window.CenterPool;

window.GameBoard = function GameBoard({
    gameState,
    editMode,
    selectedTile,
    setSelectedTile,
    handleElementSelect,
    selectedElements,
    heatmapEnabled,
    heatmapData,
    handlePatternLineDrop,
    onPlayerSwitch,
    currentPlayer,
    loading,
    engineThinking
}) {
    return React.createElement('div', {
        className: 'flex-1 space-y-3'
    },
        // Factories at top
        React.createElement('div', {
            className: 'bg-white rounded p-3 shadow-sm'
        },
            React.createElement('h3', {
                className: 'font-medium text-sm mb-2'
            }, '🏢 Factories'),
            React.createElement('div', {
                className: 'grid grid-cols-5 gap-2'
            },
                (gameState.factories || []).map((factory, index) => {
                    // Handle both old format (object with tiles) and new format (array)
                    let tilesArray = [];
                    if (Array.isArray(factory)) {
                        // New format: factory is already an array of tile strings
                        tilesArray = factory;
                    } else if (factory.tiles) {
                        // Old format: convert tiles object to array
                        const colorMap = { 0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W' };
                        Object.entries(factory.tiles).forEach(([colorIndex, count]) => {
                            const color = colorMap[parseInt(colorIndex)];
                            if (color && count > 0) {
                                for (let i = 0; i < count; i++) {
                                    tilesArray.push(color);
                                }
                            }
                        });
                    }
                    
                    return React.createElement(Factory, {
                        key: index,
                        tiles: tilesArray,
                        factoryIndex: index,
                        onTileClick: (factoryIndex, tileIndex, tile) => {
                            setSelectedTile({ sourceId: factoryIndex, tileIndex, tile });
                        },
                        selectedTile: selectedTile,
                        editMode: editMode,
                        onElementSelect: handleElementSelect,
                        selectedElements: selectedElements,
                        heatmapEnabled: heatmapEnabled,
                        heatmapData: heatmapData
                    });
                })
            )
        ),
        
        // Center Pool
        React.createElement(CenterPool, {
            gameState: gameState,
            editMode: editMode,
            selectedTile: selectedTile,
            setSelectedTile: setSelectedTile,
            handleElementSelect: handleElementSelect,
            selectedElements: selectedElements,
            heatmapEnabled: heatmapEnabled,
            heatmapData: heatmapData
        }),
        
        // Player boards - now with more space
        React.createElement('div', {
            className: 'bg-white rounded p-3 shadow-sm flex-1'
        },
            React.createElement('h3', {
                className: 'font-medium text-sm mb-2'
            }, '👥 Player Boards'),
            React.createElement('div', {
                className: 'grid grid-cols-1 xl:grid-cols-2 gap-4 h-full'
            },
                (gameState.players || []).map((player, index) => 
                    React.createElement(PlayerBoard, {
                        key: index,
                        player: player,
                        playerIndex: index,
                        isActive: index === currentPlayer,
                        editMode: editMode,
                        onElementSelect: handleElementSelect,
                        selectedElements: selectedElements,
                        onPatternLineDrop: handlePatternLineDrop,
                        onPlayerSwitch: (playerId) => onPlayerSwitch(playerId),
                        canInteract: !loading && !engineThinking
                    })
                )
            )
        )
    );
} 