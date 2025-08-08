// Helper Utility Functions

// Get tile color - use global gameConstants
function getTileColor(tile) {
    return window.gameConstants?.TILE_COLORS?.[tile] || '#6b7280';
}

// Format move description
function formatMoveDescription(move) {
    if (!move) return 'No move';
    
    if (typeof move === 'string') {
        return move;
    }
    
    if (move.description) {
        return move.description;
    }
    
    if (move.from && move.to) {
        return `${move.from} → ${move.to}`;
    }
    
    return JSON.stringify(move);
}

// Format selected element for display
function formatSelectedElement(element) {
    if (!element) return 'None';
    
    switch (element.type) {
        case 'factory':
            return `Factory ${element.data + 1}`;
        case 'factory-tile':
            return `${element.data.tile} tile in Factory ${element.data.factoryIndex + 1}`;
        case 'pattern-line':
            return `Pattern Line ${element.data.rowIndex + 1} (Player ${element.data.playerIndex + 1})`;
        case 'pattern-line-tile':
            return `${element.data.tile} tile in Pattern Line ${element.data.rowIndex + 1} (Player ${element.data.playerIndex + 1})`;
        case 'pattern-line-empty':
            return `Empty slot in Pattern Line ${element.data.rowIndex + 1} (Player ${element.data.playerIndex + 1})`;
        case 'wall-cell':
            if (element.data.tile) {
                return `${element.data.tile} tile at Wall (${element.data.rowIndex + 1}, ${element.data.colIndex + 1}) (Player ${element.data.playerIndex + 1})`;
            } else {
                return `Empty Wall cell (${element.data.rowIndex + 1}, ${element.data.colIndex + 1}) (Player ${element.data.playerIndex + 1})`;
            }
        case 'floor-tile':
            return `${element.data.tile} tile in Floor (Player ${element.data.playerIndex + 1})`;
        case 'floor-empty':
            return `Empty Floor slot (Player ${element.data.playerIndex + 1})`;
        default:
            return element.type || 'Unknown';
    }
}

// Get menu options by element type
function getMenuOptions(elementType, elementData) {
    switch (elementType) {
        case 'factory':
            return ['Edit Tiles', 'Clear Factory', 'Add Tile'];
        case 'factory-tile':
            return ['Remove Tile', 'Change Color', 'Move Tile'];
        case 'pattern-line':
            return ['Edit Tiles', 'Clear Line', 'Add Tile'];
        case 'pattern-line-tile':
            return ['Remove Tile', 'Change Color', 'Move Tile'];
        case 'pattern-line-empty':
            return ['Add Tile', 'Change Color'];
        case 'wall-cell':
            return ['Toggle Tile', 'Change Color', 'Remove Tile'];
        case 'floor-tile':
            return ['Remove Tile', 'Change Color', 'Move Tile'];
        case 'floor-empty':
            return ['Add Tile', 'Change Color'];
        default:
            return [];
    }
}

// Validate destination for selected tile
function isValidDestination(destinationType, destinationData, selectedTile) {
    if (!selectedTile) return false;
    
    // For now, allow all destinations
    // In the future, add validation logic here
    return true;
}

// Create tile data object
function createTileData(tile, sourceId, tileIndex, additionalData = {}) {
    return {
        tile,
        sourceId,
        tileIndex,
        ...additionalData
    };
}

// Format timestamp
function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
}

// Export functions to window.helpers
window.helpers = {
    getTileColor,
    formatMoveDescription,
    formatSelectedElement,
    getMenuOptions,
    isValidDestination,
    createTileData,
    formatTimestamp
}; 