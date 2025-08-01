// Wall Component with drop zones
import React, { useEffect, useRef } from 'react';
import Tile from './Tile';

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
    const wallRef = useRef(null);
    
    useEffect(() => {
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
    
    return (
        <div ref={wallRef} className="wall">
            {/* Column labels */}
            <div className="wall-column-labels">
                <div className="wall-cell-label"></div>
                {['B', 'Y', 'R', 'K', 'W'].map((color, index) => (
                    <div key={index} className="wall-cell-label text-xs text-gray-600 font-medium">
                        {color}
                    </div>
                ))}
            </div>
            {wall.map((row, rowIndex) => (
                <div key={rowIndex} className="wall-row">
                    {/* Row label */}
                    <div className="wall-cell-label text-xs text-gray-600 font-medium">
                        Row {rowIndex + 1}
                    </div>
                    {row.map((cell, colIndex) => {
                        const isValidDestination = selectedTile && onDestinationClick && !cell;
                    
                    // Check if this wall cell is selected in edit mode
                    const isEditSelected = selectedElement && 
                        selectedElement.type === 'wall-cell' && 
                        selectedElement.data.playerIndex === playerIndex && 
                        selectedElement.data.rowIndex === rowIndex && 
                        selectedElement.data.colIndex === colIndex;
                    
                    return (
                        <div 
                            key={`${rowIndex}-${colIndex}`}
                            className={`wall-cell ${cell ? 'occupied' : ''} ${isValidDestination ? 'valid-drop' : ''} ${isEditSelected ? 'selected' : ''}`}
                            onClick={() => {
                                if (editMode && onElementSelect) {
                                    onElementSelect('wall-cell', { playerIndex, rowIndex, colIndex, tile: cell });
                                } else if (isValidDestination) {
                                    onDestinationClick('wall', { rowIndex, colIndex });
                                } else {
                                    onWallClick(rowIndex, colIndex);
                                }
                            }}
                            onContextMenu={(event) => {
                                if (editMode) {
                                    event.preventDefault();
                                    if (window.showContextMenu) {
                                        window.showContextMenu(event, 'wall-cell', { playerIndex, rowIndex, colIndex, tile: cell });
                                    }
                                }
                            }}
                            data-row={rowIndex}
                            data-col={colIndex}
                        >
                            {cell && <Tile color={cell} />}
                        </div>
                    );
                })
            ))}
        </div>
    );
}

export default Wall; 