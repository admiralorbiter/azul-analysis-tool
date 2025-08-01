// Enhanced Player Board Component with active player indication
import React from 'react';
import PatternLine from './PatternLine';
import Wall from './Wall';
import Tile from './Tile';

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
    
    return (
        <div className={`${borderClass} p-4 rounded-lg mb-4 transition-all duration-200`}>
            <div className="flex justify-between items-center mb-3">
                <h4 className={`text-lg font-medium ${headerClass}`}>
                    Player {playerIndex + 1}
                    {isActive && <span className="ml-2 text-sm">👑 Active</span>}
                    <span className="ml-2 text-sm text-gray-500">Score: {player.score || 0}</span>
                </h4>
                
                {onPlayerSwitch && canInteract && gameMode === 'sandbox' && (
                    <button
                        onClick={() => onPlayerSwitch(playerIndex)}
                        disabled={isActive}
                        className={`px-3 py-1 text-sm rounded transition-colors ${
                            isActive 
                                ? 'bg-blue-200 text-blue-800 cursor-not-allowed' 
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                    >
                        {isActive ? 'Playing' : 'Switch'}
                    </button>
                )}
            </div>
            
            {/* Pattern Lines */}
            <div className="mb-4">
                <h5 className="text-sm font-medium mb-2">Pattern Lines</h5>
                {player.pattern_lines.map((line, index) => (
                    <PatternLine 
                        key={index}
                        tiles={line}
                        rowIndex={index}
                        maxTiles={index + 1}
                        onTileClick={onPatternLineClick}
                        onDrop={onPatternLineDrop}
                        selectedTile={selectedTile}
                        onDestinationClick={onDestinationClick}
                        editMode={editMode}
                        onElementSelect={onElementSelect}
                        playerIndex={playerIndex}
                        selectedElement={selectedElement}
                    />
                ))}
            </div>

            {/* Wall */}
            <div className="mb-4">
                <h5 className="text-sm font-medium mb-2">Wall</h5>
                <Wall 
                    wall={player.wall}
                    onWallClick={onWallClick}
                    onDrop={onWallDrop}
                    selectedTile={selectedTile}
                    onDestinationClick={onDestinationClick}
                    editMode={editMode}
                    onElementSelect={onElementSelect}
                    playerIndex={playerIndex}
                    selectedElement={selectedElement}
                />
            </div>
            
            {/* Floor */}
            <div>
                <h5 className="text-sm font-medium mb-2">Floor</h5>
                <div className="flex gap-1">
                    {player.floor.map((tile, index) => {
                        // Check if this floor tile is selected in edit mode
                        const isEditSelected = selectedElement && 
                            selectedElement.type === 'floor-tile' && 
                            selectedElement.data.playerIndex === playerIndex && 
                            selectedElement.data.tileIndex === index;
                        
                        return (
                            <Tile 
                                key={index} 
                                color={tile}
                                className={isEditSelected ? 'selected' : ''}
                                onClick={() => {
                                    if (editMode && onElementSelect) {
                                        onElementSelect('floor-tile', { playerIndex, tileIndex: index, tile });
                                    }
                                }}
                                onContextMenu={(event) => {
                                    if (editMode) {
                                        event.preventDefault();
                                        if (window.showContextMenu) {
                                            window.showContextMenu(event, 'floor-tile', { playerIndex, tileIndex: index, tile });
                                        }
                                    }
                                }}
                            />
                        );
                    })}
                    {Array.from({ length: Math.max(0, 7 - player.floor.length) }, (_, index) => {
                        // Check if this empty floor slot is selected in edit mode
                        const isEditSelected = selectedElement && 
                            selectedElement.type === 'floor-empty' && 
                            selectedElement.data.playerIndex === playerIndex && 
                            selectedElement.data.emptyIndex === index;
                        
                        return (
                            <div 
                                key={`floor-empty-${index}`}
                                className={`tile ${isEditSelected ? 'selected' : ''}`}
                                style={{ backgroundColor: 'transparent', border: '2px dashed #d1d5db' }}
                                onClick={() => {
                                    if (editMode && onElementSelect) {
                                        onElementSelect('floor-empty', { playerIndex, emptyIndex: index });
                                    }
                                }}
                                onContextMenu={(event) => {
                                    if (editMode) {
                                        event.preventDefault();
                                        if (window.showContextMenu) {
                                            window.showContextMenu(event, 'floor-empty', { playerIndex, emptyIndex: index });
                                        }
                                    }
                                }}
                            />
                        );
                    })}
                </div>
            </div>
        </div>
    );
}

export default PlayerBoard; 