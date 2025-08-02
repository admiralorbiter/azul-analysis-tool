// Tile Component
// Individual tile component for the Azul game board

function Tile({ color, onClick, className = "", draggable = false, onDragStart, onDragEnd, dataAttributes = {}, isSelected = false }) {
    const tileRef = React.useRef(null);
    
    React.useEffect(() => {
        const tile = tileRef.current;
        if (!tile) return;
        
        const handleDragStart = (e) => {
            if (onDragStart) onDragStart(e);
            e.dataTransfer.effectAllowed = 'move';
        };
        
        const handleDragEnd = (e) => {
            if (onDragEnd) onDragEnd(e);
        };
        
        if (draggable) {
            tile.addEventListener('dragstart', handleDragStart);
            tile.addEventListener('dragend', handleDragEnd);
        }
        
        return () => {
            if (draggable) {
                tile.removeEventListener('dragstart', handleDragStart);
                tile.removeEventListener('dragend', handleDragEnd);
            }
        };
    }, [draggable, onDragStart, onDragEnd]);
    
    const selectedClass = isSelected ? 'ring-2 ring-blue-500 ring-offset-2' : '';
    
    return React.createElement('div', {
        ref: tileRef,
        className: `tile ${className} ${selectedClass}`,
        style: { backgroundColor: getTileColor(color) },
        onClick: onClick,
        draggable: draggable,
        ...dataAttributes
    });
}

// Export for global access
window.Tile = Tile; 