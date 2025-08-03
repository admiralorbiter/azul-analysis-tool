// Game Constants and Configuration

// Tile types
window.gameConstants = window.gameConstants || {};
window.gameConstants.TILE_TYPES = {
    RED: 'R',
    YELLOW: 'Y',
    BLUE: 'B',
    WHITE: 'W',
    BLACK: 'K',
    EMPTY: 'W'
};

// Tile colors mapping - Updated to match BGA colors
window.gameConstants.TILE_COLORS = {
    'R': '#dc2626', // Bright vibrant red (BGA style)
    'Y': '#f59e0b', // Yellow with orange tint (BGA style)
    'B': '#06b6d4', // Bright teal/cyan blue (BGA style)
    'W': '#f8fafc', // Light off-white/cream (BGA style)
    'K': '#0f172a', // Very dark teal/black (BGA style)
    'W': '#f1f5f9'  // White (empty) - lighter gray
};

// Game modes
window.gameConstants.GAME_MODES = {
    SANDBOX: 'sandbox',
    ANALYSIS: 'analysis',
    SETUP: 'setup'
};

// Element types for editing
window.gameConstants.ELEMENT_TYPES = {
    FACTORY: 'factory',
    FACTORY_TILE: 'factory-tile',
    PATTERN_LINE: 'pattern-line',
    PATTERN_LINE_TILE: 'pattern-line-tile',
    PATTERN_LINE_EMPTY: 'pattern-line-empty',
    WALL_CELL: 'wall-cell',
    FLOOR_TILE: 'floor-tile',
    FLOOR_EMPTY: 'floor-empty'
};

// Context menu actions
window.gameConstants.CONTEXT_MENU_ACTIONS = {
    EDIT_TILES: 'Edit Tiles',
    CLEAR_FACTORY: 'Clear Factory',
    ADD_TILE: 'Add Tile',
    REMOVE_TILE: 'Remove Tile',
    CHANGE_COLOR: 'Change Color',
    MOVE_TILE: 'Move Tile',
    TOGGLE_TILE: 'Toggle Tile',
    CLEAR_LINE: 'Clear Line'
};

// Status message types
window.gameConstants.STATUS_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
};

// Default game configuration
window.gameConstants.DEFAULT_GAME_CONFIG = {
    playerCount: 2,
    currentPlayer: 0,
    autoAdvanceTurn: false,
    gameMode: window.gameConstants.GAME_MODES.SANDBOX
};

// API endpoints
window.gameConstants.API_ENDPOINTS = {
    SESSION: '/api/v1/auth/session',
    ANALYZE: '/api/v1/analyze',
    HINT: '/api/v1/hint',
    HEALTH: '/api/v1/health',
    STATS: '/api/v1/stats'
};

// Drag and drop configuration
window.gameConstants.DRAG_CONFIG = {
    GHOST_OPACITY: 0.8,
    GHOST_ROTATION: 5,
    GHOST_SIZE: 40
};

// Visual feedback configuration
window.gameConstants.VISUAL_CONFIG = {
    HOVER_SCALE: 1.1,
    SELECTED_SCALE: 1.15,
    TRANSITION_DURATION: '0.2s',
    HIGHLIGHT_COLOR: '#f59e0b',
    SUCCESS_COLOR: '#10b981',
    ERROR_COLOR: '#dc2626', // Updated to match BGA red
    INFO_COLOR: '#06b6d4'  // Updated to match BGA blue
}; 