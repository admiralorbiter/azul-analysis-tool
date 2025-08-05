// API Configuration and Utility Functions

// API Configuration - Use existing API_BASE from constants.js
console.log('Loading utils/api.js, API_CONSTANTS:', window.API_CONSTANTS);
// Use the existing API_BASE from constants.js instead of declaring a new one
console.log('API_BASE available:', window.API_CONSTANTS?.API_BASE);
let sessionId = null;

// Initialize session
async function initializeSession() {
    try {
        const response = await fetch(`${window.API_CONSTANTS?.API_BASE}/auth/session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_agent: navigator.userAgent,
                ip_address: '127.0.0.1'
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            sessionId = data.session_id;
            console.log('Session initialized:', sessionId);
            return true;
        } else {
            console.error('Session creation failed:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Failed to initialize session:', error);
        return false;
    }
}

// API helper functions
async function analyzePosition(fenString) {
    if (!sessionId) {
        console.error('No session ID available');
        return null;
    }
    
    try {
        const response = await fetch(`${window.API_CONSTANTS?.API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-ID': sessionId
            },
            body: JSON.stringify({
                fen_string: fenString
            })
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            console.error('Analysis failed:', response.status);
            return null;
        }
    } catch (error) {
        console.error('Failed to analyze position:', error);
        return null;
    }
}

// Get game state
async function getGameState(fenString = 'initial') {
    if (!sessionId) {
        console.error('No session ID available');
        return null;
    }
    
    try {
        const response = await fetch(`${window.API_CONSTANTS?.API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-ID': sessionId
            },
            body: JSON.stringify({
                fen_string: fenString
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            return data.game_state;
        } else {
            console.error('Failed to get game state:', response.status);
            return null;
        }
    } catch (error) {
        console.error('Failed to get game state:', error);
        return null;
    }
}

// Get hint
async function getHint(fenString) {
    if (!sessionId) {
        console.error('No session ID available');
        return null;
    }
    
    try {
        const response = await fetch(`${window.API_CONSTANTS?.API_BASE}/hint`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-ID': sessionId
            },
            body: JSON.stringify({
                fen_string: fenString
            })
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            console.error('Hint failed:', response.status);
            return null;
        }
    } catch (error) {
        console.error('Failed to get hint:', error);
        return null;
    }
}

// Neural analysis
async function analyzeNeural(fenString) {
    if (!sessionId) {
        console.error('No session ID available');
        return null;
    }
    
    try {
        const response = await fetch(`${window.API_CONSTANTS?.API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-ID': sessionId
            },
            body: JSON.stringify({
                fen_string: fenString,
                use_neural: true
            })
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            console.error('Neural analysis failed:', response.status);
            return null;
        }
    } catch (error) {
        console.error('Failed to analyze with neural network:', error);
        return null;
    }
}

// Generic API call function
async function callAPI(endpoint, method = 'GET', data = null) {
    if (!sessionId) {
        console.error('No session ID available');
        return { success: false, error: 'No session ID available' };
    }
    
    try {
        const response = await fetch(`${window.API_CONSTANTS?.API_BASE}${endpoint}`, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-Session-ID': sessionId
            },
            body: data ? JSON.stringify(data) : undefined
        });
        
        if (response.ok) {
            const result = await response.json();
            return { success: true, ...result };
        } else {
            console.error(`API call failed: ${response.status}`);
            return { success: false, error: `HTTP ${response.status}` };
        }
    } catch (error) {
        console.error('API call error:', error);
        return { success: false, error: error.message };
    }
}

// Export functions to window.api
window.api = {
    initializeSession,
    analyzePosition,
    getGameState,
    getHint,
    analyzeNeural,
    callAPI,
    sessionId
}; 