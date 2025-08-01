// Tile Component with proper drag-and-drop
import React, { useEffect, useRef } from 'react';
import { TILE_COLORS } from '../constants/gameConstants';

function Tile({ 
    color, 
    onClick, 
    className = "", 
    draggable = false, 
    onDragStart, 
    onDragEnd, 
    dataAttributes = {}, 
    isSelected = false 
}) {
    const tileRef = useRef(null);
    
    useEffect(() => {
        const tile = tileRef.current;
        if (!tile || !draggable) return;
        
        const handleDragStart = (e) => {
            if (onDragStart) {
                onDragStart(e, tile);
            }
        };
        
        const handleDragEnd = (e) => {
            if (onDragEnd) {
                onDragEnd(e, tile);
            }
        };
        
        tile.addEventListener('dragstart', handleDragStart);
        tile.addEventListener('dragend', handleDragEnd);
        
        return () => {
            tile.removeEventListener('dragstart', handleDragStart);
            tile.removeEventListener('dragend', handleDragEnd);
        };
    }, [draggable, onDragStart, onDragEnd]);
    
    return (
        <div 
            ref={tileRef}
            className={`tile ${className} ${isSelected ? 'selected' : ''}`}
            style={{ backgroundColor: TILE_COLORS[color] || '#6b7280' }}
            onClick={onClick}
            title={color}
            draggable={draggable}
            {...dataAttributes}
        />
    );
}

export default Tile; 