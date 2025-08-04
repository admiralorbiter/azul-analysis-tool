// Pattern Line Component with drop zones
import React, { useEffect, useRef } from 'react';
import Tile from './Tile';

function PatternLine({ 
    tiles, 
    rowIndex, 
    maxTiles, 
    onTileClick, 
    onDrop, 
    selectedTile = null, 
    onDestinationClick = null, 
    editMode = false, 
    onElementSelect = null, 
    playerIndex = null, 
    selectedElement = null 
}) {
    const patternLineRef = useRef(null);
    
    useEffect(() => {
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
            
            console.log('PatternLine drop event triggered');
            
            const tileData = e.dataTransfer.getData('application/json');
            console.log('Tile data from drop:', tileData);
            
            if (tileData) {
                const data = JSON.parse(tileData);
                console.log('Parsed data:', data);
                if (onDrop) {
                    console.log('Calling onDrop with:', data, rowIndex);
                    onDrop(data, rowIndex);
                } else {
                    console.log('onDrop is not defined');
                }
            } else {
                console.log('No tile data found in drop event');
            }
        };
        
        patternLine.addEventListener('dragover', handleDragOver);
        patternLine.addEventListener('dragleave', handleDragLeave);
        patternLine.addEventListener('drop', handleDrop);
        
        return () => {
            patternLine.removeEventListener('dragover', handleDragOver);
            patternLine.removeEventListener('dragleave', handleDragLeave);
            patternLine.removeEventListener('drop', handleDrop);
        };
    }, [onDrop, rowIndex, patternLineRef]);
    
    // Handle pattern line click in edit mode
    const handlePatternLineClick = () => {
        if (editMode && onElementSelect) {
            onElementSelect('pattern-line', { playerIndex, rowIndex });
        }
    };

    // Handle pattern line right-click for context menu
    const handlePatternLineRightClick = (event) => {
        if (editMode) {
            event.preventDefault();
            if (window.showContextMenu) {
                window.showContextMenu(event, 'pattern-line', { playerIndex, rowIndex });
            }
        }
    };
    
    // Check if this pattern line is selected
    const isSelected = selectedElement && 
        selectedElement.type === 'pattern-line' && 
        selectedElement.data.playerIndex === playerIndex && 
        selectedElement.data.rowIndex === rowIndex;
    
    const emptySlots = Math.max(0, maxTiles - tiles.length);
    const isValidDestination = selectedTile && onDestinationClick;
    
    return (
        <div 
            ref={patternLineRef} 
            className={`pattern-line ${isValidDestination ? 'valid-drop' : ''} ${isSelected ? 'selected' : ''}`}
            onClick={editMode ? handlePatternLineClick : undefined}
            onContextMenu={editMode ? handlePatternLineRightClick : undefined}
        >
            {/* Row label */}
            <div className="text-xs text-gray-600 font-medium">Row {rowIndex + 1}</div>
            <div className="flex gap-1">
                {tiles.map((tile, index) => {
                // Check if this tile is selected in edit mode
                const isEditSelected = selectedElement && 
                    selectedElement.type === 'pattern-line-tile' && 
                    selectedElement.data.playerIndex === playerIndex && 
                    selectedElement.data.rowIndex === rowIndex && 
                    selectedElement.data.tileIndex === index;
                
                return (
                    <Tile 
                        key={index}
                        color={tile}
                        onClick={(e) => {
                            if (editMode && onElementSelect) {
                                const isCtrlClick = e.ctrlKey || e.metaKey;
                                onElementSelect({
                                    type: 'pattern-line-tile',
                                    data: { playerIndex, rowIndex, tileIndex: index, tile }
                                }, isCtrlClick);
                            } else if (isValidDestination) {
                                onDestinationClick('pattern', { rowIndex, tileIndex: index });
                            } else {
                                onTileClick(rowIndex, index);
                            }
                        }}
                        onContextMenu={(event) => {
                            if (editMode) {
                                event.preventDefault();
                                if (window.showContextMenu) {
                                    window.showContextMenu(event, 'pattern-line-tile', { playerIndex, rowIndex, tileIndex: index, tile });
                                }
                            }
                        }}
                        className={isEditSelected ? 'selected' : ''}
                    />
                );
            })}
            {Array.from({ length: emptySlots }, (_, index) => {
                // Check if this empty slot is selected in edit mode
                const isEditSelected = selectedElement && 
                    selectedElement.type === 'pattern-line-empty' && 
                    selectedElement.data.playerIndex === playerIndex && 
                    selectedElement.data.rowIndex === rowIndex && 
                    selectedElement.data.emptyIndex === index;
                
                return (
                    <div 
                        key={`empty-${index}`}
                        className={`tile ${isEditSelected ? 'selected' : ''}`}
                        style={{ backgroundColor: 'transparent', border: '2px dashed #d1d5db' }}
                        onClick={(e) => {
                            if (editMode && onElementSelect) {
                                const isCtrlClick = e.ctrlKey || e.metaKey;
                                onElementSelect({
                                    type: 'pattern-line-empty',
                                    data: { playerIndex, rowIndex, emptyIndex: index }
                                }, isCtrlClick);
                            } else if (isValidDestination) {
                                onDestinationClick('pattern', { rowIndex, tileIndex: tiles.length + index });
                            }
                        }}
                        onContextMenu={(event) => {
                            if (editMode) {
                                event.preventDefault();
                                if (window.showContextMenu) {
                                    window.showContextMenu(event, 'pattern-line-empty', { playerIndex, rowIndex, emptyIndex: index });
                                }
                            }
                        }}
                    />
                );
            })}
            {Array.from({ length: emptySlots }, (_, index) => {
                // Check if this empty slot is selected in edit mode
                const isEditSelected = selectedElement && 
                    selectedElement.type === 'pattern-line-empty' && 
                    selectedElement.data.playerIndex === playerIndex && 
                    selectedElement.data.rowIndex === rowIndex && 
                    selectedElement.data.emptyIndex === index;
                
                return (
                    <div 
                        key={`empty-${index}`}
                        className={`tile ${isEditSelected ? 'selected' : ''}`}
                        style={{ backgroundColor: 'transparent', border: '2px dashed #d1d5db' }}
                        onClick={(e) => {
                            if (editMode && onElementSelect) {
                                const isCtrlClick = e.ctrlKey || e.metaKey;
                                onElementSelect({
                                    type: 'pattern-line-empty',
                                    data: { playerIndex, rowIndex, emptyIndex: index }
                                }, isCtrlClick);
                            } else if (isValidDestination) {
                                onDestinationClick('pattern', { rowIndex, tileIndex: tiles.length + index });
                            }
                        }}
                        onContextMenu={(event) => {
                            if (editMode) {
                                event.preventDefault();
                                if (window.showContextMenu) {
                                    window.showContextMenu(event, 'pattern-line-empty', { playerIndex, rowIndex, emptyIndex: index });
                                }
                            }
                            }
                        }}
                    />
                );
            })}
            </div>
        </div>
    );
}

export default PatternLine; 