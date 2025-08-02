// Game API functions for Azul Solver & Analysis Toolkit
// Extracted from main.js for modularity

// Use shared API constants - must be loaded after constants.js
const GAME_API_BASE = window.API_CONSTANTS?.API_BASE || '/api/v1';

// Session Management
async function initializeSession() {
    // Skip session initialization for local development
    console.log('Session initialization skipped for local development');
    return { session_id: 'local-dev' };
}

// Game Analysis Functions
async function analyzePosition(fenString, depth = 3, timeBudget = 4.0, agentId = 0) {
    try {
        const response = await fetch(`${GAME_API_BASE}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                fen_string: fenString,
                depth: depth,
                time_budget: timeBudget,
                agent_id: agentId
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to analyze position:', error);
        throw error;
    }
}

async function getHint(fenString, budget = 0.2, rollouts = 100, agentId = 0) {
    try {
        const response = await fetch(`${GAME_API_BASE}/hint`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                fen_string: fenString,
                budget: budget,
                rollouts: rollouts,
                agent_id: agentId
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to get hint:', error);
        throw error;
    }
}

async function analyzeNeural(fenString, timeBudget = 2.0, maxRollouts = 100, agentId = 0) {
    try {
        const response = await fetch(`${GAME_API_BASE}/analyze_neural`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                fen: fenString,
                time_budget: timeBudget,
                max_rollouts: maxRollouts,
                agent_id: agentId
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to analyze with neural network:', error);
        throw error;
    }
}

async function analyzeGame(gameData, analysisDepth = 3) {
    try {
        const response = await fetch(`${GAME_API_BASE}/analyze_game`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                game_data: gameData,
                analysis_depth: analysisDepth
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to analyze game:', error);
        throw error;
    }
}

// Game State Management Functions
async function getGameState(fenString = 'initial') {
    try {
        const response = await fetch(`${GAME_API_BASE}/game_state?fen_string=${fenString}`);
        const data = await response.json();
        // Return the nested game_state property
        return data.game_state || data;
    } catch (error) {
        console.error('Failed to get game state:', error);
        throw error;
    }
}

async function saveGameState(gameState, fenString = 'initial') {
    try {
        const response = await fetch(`${GAME_API_BASE}/game_state`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                fen_string: fenString,
                game_state: gameState
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to save game state:', error);
        throw error;
    }
}

// Move Execution Function
async function executeMove(fenString, move, agentId = 0) {
    try {
        const response = await fetch(`${GAME_API_BASE}/execute_move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                fen_string: fenString,
                move: move,
                agent_id: agentId
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to execute move:', error);
        throw error;
    }
}

// Export all game API functions
window.gameAPI = {
    initializeSession,
    analyzePosition,
    getHint,
    analyzeNeural,
    analyzeGame,
    getGameState,
    saveGameState,
    executeMove
}; 