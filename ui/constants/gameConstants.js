// Game Constants and Configuration

// Tile types
const TILE_TYPES = {
    RED: 'R',
    YELLOW: 'Y',
    BLUE: 'B',
    WHITE: 'W',
    BLACK: 'K',
    EMPTY: 'E'
};

// Tile colors mapping - Updated to match BGA colors
const TILE_COLORS = {
    'R': '#dc2626', // Bright vibrant red (BGA style)
    'Y': '#f59e0b', // Yellow with orange tint (BGA style)
    'B': '#06b6d4', // Bright teal/cyan blue (BGA style)
    'W': '#f8fafc', // Light off-white/cream (BGA style)
    'K': '#0f172a', // Very dark teal/black (BGA style)
    'E': '#f1f5f9'  // Empty - lighter gray
};

// Game modes
const GAME_MODES = {
    SANDBOX: 'sandbox',
    ANALYSIS: 'analysis',
    SETUP: 'setup'
};

// Element types for editing
const ELEMENT_TYPES = {
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
const CONTEXT_MENU_ACTIONS = {
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
const STATUS_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
};

// Default game configuration
const DEFAULT_GAME_CONFIG = {
    playerCount: 2,
    currentPlayer: 0,
    autoAdvanceTurn: false,
    gameMode: GAME_MODES.SANDBOX
};

// API endpoints
const API_ENDPOINTS = {
    SESSION: '/api/v1/auth/session',
    ANALYZE: '/api/v1/analyze',
    HINT: '/api/v1/hint',
    HEALTH: '/api/v1/health',
    STATS: '/api/v1/stats'
};

// Drag and drop configuration
const DRAG_CONFIG = {
    GHOST_OPACITY: 0.8,
    GHOST_ROTATION: 5,
    GHOST_SIZE: 40
};

// Visual feedback configuration
const VISUAL_CONFIG = {
    HOVER_SCALE: 1.1,
    SELECTED_SCALE: 1.15,
    TRANSITION_DURATION: '0.2s',
    HIGHLIGHT_COLOR: '#f59e0b',
    SUCCESS_COLOR: '#10b981',
    ERROR_COLOR: '#dc2626', // Updated to match BGA red
    INFO_COLOR: '#06b6d4'  // Updated to match BGA blue
};

// Export for ES6 modules
export {
    TILE_TYPES,
    TILE_COLORS,
    GAME_MODES,
    ELEMENT_TYPES,
    CONTEXT_MENU_ACTIONS,
    STATUS_TYPES,
    DEFAULT_GAME_CONFIG,
    API_ENDPOINTS,
    DRAG_CONFIG,
    VISUAL_CONFIG
};

// Also attach to window for backward compatibility
window.gameConstants = window.gameConstants || {};
window.gameConstants.TILE_TYPES = TILE_TYPES;
window.gameConstants.TILE_COLORS = TILE_COLORS;
window.gameConstants.GAME_MODES = GAME_MODES;
window.gameConstants.ELEMENT_TYPES = ELEMENT_TYPES;
window.gameConstants.CONTEXT_MENU_ACTIONS = CONTEXT_MENU_ACTIONS;
window.gameConstants.STATUS_TYPES = STATUS_TYPES;
window.gameConstants.DEFAULT_GAME_CONFIG = DEFAULT_GAME_CONFIG;
window.gameConstants.API_ENDPOINTS = API_ENDPOINTS;
window.gameConstants.DRAG_CONFIG = DRAG_CONFIG;
window.gameConstants.VISUAL_CONFIG = VISUAL_CONFIG; 