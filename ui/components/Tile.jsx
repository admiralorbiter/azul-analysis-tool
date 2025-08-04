// Tile Component with proper drag-and-drop
// Using global React and window.gameConstants for compatibility

// Debug log to confirm component is loaded
console.log('Enhanced Tile component loaded');
console.log('Tile colors available:', window.gameConstants?.TILE_COLORS);

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
    const tileRef = React.useRef(null);
    
    React.useEffect(() => {
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
    
    return React.createElement('div', {
        ref: tileRef,
        className: `tile ${className} ${isSelected ? 'selected' : ''}`,
        style: { backgroundColor: window.gameConstants?.TILE_COLORS?.[color] || '#6b7280' },
        onClick: onClick,
        title: color,
        draggable: draggable,
        ...dataAttributes
    });
}

// Attach to window for backward compatibility
window.Tile = Tile; 