// Shared constants for Azul Solver & Analysis Toolkit API modules

// API base URL for all API calls
const API_BASE = '/api/v1';

// Tile colors mapping - Updated to match BGA colors
const TILE_COLORS = {
    'R': '#dc2626', // Bright vibrant red (BGA style)
    'Y': '#f59e0b', // Yellow with orange tint (BGA style)
    'B': '#06b6d4', // Bright teal/cyan blue (BGA style)
    'W': '#f8fafc', // Light off-white/cream (BGA style)
    'K': '#0f172a', // Very dark teal/black (BGA style)
    'E': '#f1f5f9'  // Empty - lighter gray
};

// Export constants to global scope for use by other modules
window.API_CONSTANTS = {
    API_BASE
};

// Export tile colors to global scope for components
window.gameConstants = window.gameConstants || {};
window.gameConstants.TILE_COLORS = TILE_COLORS; 