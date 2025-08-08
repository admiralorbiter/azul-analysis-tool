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

// Export constants to global scope for use by other modules
window.API_CONSTANTS = {
    API_BASE
}; 