// Shared constants for Azul Solver & Analysis Toolkit API modules

// API base URL for all API calls
// Detect if we're running in development mode (different port) or production (same server)
const isDevelopment = window.location.port && window.location.port !== '8000';
const API_BASE = isDevelopment ? 'http://localhost:8000/api/v1' : '/api/v1';

console.log('API Configuration:', {
    isDevelopment,
    currentPort: window.location.port,
    apiBase: API_BASE
});

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