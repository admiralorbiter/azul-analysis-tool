// Factory Component with drag-and-drop
import React, { useEffect, useRef } from 'react';
import Tile from './Tile';

function Factory({ 
    tiles, 
    onTileClick, 
    heatmap = null, 
    factoryIndex, 
    selectedTile = null, 
    onTileSelection = null, 
    editMode = false, 
    onElementSelect = null, 
    selectedElement = null 
}) {
    const factoryRef = useRef(null);
    
    useEffect(() => {
        const factory = factoryRef.current;
        if (!factory) return;
        
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
                // Handle drop on factory (not implemented yet)
                console.log('Drop on factory:', data);
            }
        };
        
        factory.addEventListener('dragover', handleDragOver);
        factory.addEventListener('dragleave', handleDragLeave);
        factory.addEventListener('drop', handleDrop);
        
        return () => {
            factory.removeEventListener('dragover', handleDragOver);
            factory.removeEventListener('dragleave', handleDragLeave);
            factory.removeEventListener('drop', handleDrop);
        };
    }, []);
    
    // Handle factory click in edit mode
    const handleFactoryClick = (event) => {
        if (editMode && onElementSelect) {
            onElementSelect('factory', factoryIndex);
        }
    };

    // Handle factory right-click for context menu
    const handleFactoryRightClick = (event) => {
        if (editMode) {
            event.preventDefault();
            // This will be handled by the parent component
            if (window.showContextMenu) {
                window.showContextMenu(event, 'factory', factoryIndex);
            }
        }
    };
    
    // Check if this factory is selected
    const isSelected = selectedElement && 
        selectedElement.type === 'factory' && 
        selectedElement.data === factoryIndex;
    
    // Debug: Log factory contents
    React.useEffect(() => {
        if (tiles && tiles.length > 0) {
            console.log(`Factory ${factoryIndex} contents:`, tiles);
        }
    }, [tiles, factoryIndex]);
    
    return (
        <div 
            ref={factoryRef} 
            className={`factory ${isSelected ? 'selected' : ''}`}
            onClick={editMode ? handleFactoryClick : undefined}
            onContextMenu={editMode ? handleFactoryRightClick : undefined}
        >
            <div className="text-xs text-gray-600 font-medium text-center">Factory {factoryIndex + 1}</div>
            <div className="flex flex-wrap gap-1">
                {tiles.map((tile, index) => {
                    const tileData = {
                        tile: tile,
                        factoryIndex: factoryIndex,
                        tileIndex: index,
                        sourceId: factoryIndex
                    };
                    const isSelected = selectedTile && 
                        selectedTile.tile === tile && 
                        selectedTile.factoryIndex === factoryIndex && 
                        selectedTile.tileIndex === index;
                    
                    // Check if this tile is selected in edit mode
                    const isEditSelected = selectedElement && 
                        selectedElement.type === 'factory-tile' && 
                        selectedElement.data.factoryIndex === factoryIndex && 
                        selectedElement.data.tileIndex === index;
                    
                    return (
                        <Tile 
                            key={index}
                            color={tile}
                            onClick={(e) => {
                                if (editMode && onElementSelect) {
                                    const isCtrlClick = e.ctrlKey || e.metaKey;
                                    onElementSelect({
                                        type: 'factory-tile',
                                        data: { factoryIndex, tileIndex: index, tile }
                                    }, isCtrlClick);
                                } else if (onTileSelection) {
                                    onTileSelection(tileData);
                                } else {
                                    onTileClick(tile, index);
                                }
                            }}
                            onContextMenu={(event) => {
                                if (editMode) {
                                    event.preventDefault();
                                    if (window.showContextMenu) {
                                        window.showContextMenu(event, 'factory-tile', { factoryIndex, tileIndex: index, tile });
                                    }
                                }
                            }}
                            className={`${heatmap ? `heatmap-${heatmap}` : ""} ${selectedTile && !isSelected ? 'valid-source' : ''} ${isEditSelected ? 'selected' : ''}`}
                            draggable={tile !== 'W' && tile !== 'E'} // Only non-empty tiles are draggable
                            isSelected={isSelected}
                            onDragStart={(e, tileElement) => {
                                console.log('Factory tile drag start:', tile, factoryIndex, index);
                                
                                // Validate that the tile exists in this factory using the tiles prop
                                if (!tiles || !tiles.includes(tile)) {
                                    console.error(`Tile ${tile} not found in factory ${factoryIndex}. Available tiles:`, tiles);
                                    e.preventDefault();
                                    return false;
                                }
                                
                                // Additional validation: ensure tile is draggable
                                if (tile === 'W' || tile === 'E' || !tile) {
                                    console.error(`Tile ${tile} is not draggable`);
                                    e.preventDefault();
                                    return false;
                                }
                                
                                const tileData = {
                                    tile: tile,
                                    factoryIndex: factoryIndex,
                                    tileIndex: index,
                                    sourceId: factoryIndex
                                };
                                e.dataTransfer.setData('application/json', JSON.stringify(tileData));
                                e.dataTransfer.effectAllowed = 'move';
                                tileElement.classList.add('dragging');
                                
                                // Create drag ghost
                                const dragGhost = tileElement.cloneNode(true);
                                dragGhost.classList.add('drag-ghost');
                                dragGhost.style.width = '40px';
                                dragGhost.style.height = '40px';
                                document.body.appendChild(dragGhost);
                                e.dataTransfer.setDragImage(dragGhost, 20, 20);
                            }}
                            onDragEnd={(e, tileElement) => {
                                tileElement.classList.remove('dragging');
                                const dragGhost = document.querySelector('.drag-ghost');
                                if (dragGhost) {
                                    document.body.removeChild(dragGhost);
                                }
                            }}
                        />
                    );
                })}
            </div>
        </div>
    );
}

export default Factory; 