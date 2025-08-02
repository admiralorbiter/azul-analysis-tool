// Format utility functions for Azul Solver & Analysis Toolkit
// Extracted from main.js for modularity

// Tile color constants
const TILE_COLORS = {
    'R': '#ef4444', 'Y': '#eab308', 'B': '#3b82f6', 
    'W': '#f8fafc', 'K': '#8b5cf6'
};

// Get tile color based on tile type
function getTileColor(tile) {
    return TILE_COLORS[tile] || '#6b7280';
}

// Format move description for display
function formatMoveDescription(move) {
    if (!move) return 'No move available';
    return `Move: ${move.source_id} → ${move.pattern_line_dest} (${move.tile_type})`;
}

// Format selected element for display
function formatSelectedElement(element) {
    if (!element) return 'No element selected';
    return `${element.type}: ${JSON.stringify(element.data)}`;
}

// Get menu options based on element type
function getMenuOptions(elementType, elementData) {
    const options = [];
    switch (elementType) {
        case 'factory':
            options.push('Clear Factory', 'Add Tiles', 'Remove Tiles');
            break;
        case 'pattern-line':
            options.push('Clear Line', 'Add Tile', 'Remove Tile');
            break;
        case 'wall':
            options.push('Place Tile', 'Remove Tile', 'Clear Wall');
            break;
        case 'floor':
            options.push('Add Penalty', 'Remove Penalty', 'Clear Floor');
            break;
    }
    return options;
}

// Export format utilities to global scope
window.formatUtils = {
    TILE_COLORS,
    getTileColor,
    formatMoveDescription,
    formatSelectedElement,
    getMenuOptions
}; 