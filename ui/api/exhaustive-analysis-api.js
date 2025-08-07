/**
 * Exhaustive Analysis API Module
 * 
 * Provides API functions for the exhaustive search analysis system.
 * Connects the UI with the robust_exhaustive_analyzer.py backend.
 * 
 * Version: 1.0.0
 */

// Base API URL
const EXHAUSTIVE_API_BASE = '/api/v1';

/**
 * Start exhaustive analysis
 * @param {Object} config - Analysis configuration
 * @param {string} config.mode - Analysis mode (quick/standard/deep/exhaustive)
 * @param {number} config.positions - Number of positions to analyze
 * @param {number} config.maxWorkers - Maximum number of workers
 * @param {string} config.sessionId - Session ID for tracking
 * @returns {Promise<Object>} Analysis results
 */
async function startExhaustiveAnalysis(config) {
    try {
        const response = await fetch(`${EXHAUSTIVE_API_BASE}/exhaustive-analysis/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to start exhaustive analysis:', error);
        throw error;
    }
}

/**
 * Get analysis progress
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} Progress information
 */
async function getAnalysisProgress(sessionId) {
    try {
        const response = await fetch(`${EXHAUSTIVE_API_BASE}/exhaustive-analysis/progress/${sessionId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to get analysis progress:', error);
        throw error;
    }
}

/**
 * Stop analysis
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} Stop confirmation
 */
async function stopAnalysis(sessionId) {
    try {
        const response = await fetch(`${EXHAUSTIVE_API_BASE}/exhaustive-analysis/stop/${sessionId}`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to stop analysis:', error);
        throw error;
    }
}

/**
 * Get analysis results
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} Analysis results
 */
async function getAnalysisResults(sessionId) {
    try {
        const response = await fetch(`${EXHAUSTIVE_API_BASE}/exhaustive-analysis/results/${sessionId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to get analysis results:', error);
        throw error;
    }
}

/**
 * Get recent sessions
 * @param {number} limit - Number of sessions to retrieve
 * @returns {Promise<Array>} Recent sessions
 */
async function getRecentSessions(limit = 10) {
    try {
        const response = await fetch(`${EXHAUSTIVE_API_BASE}/exhaustive-analysis/sessions?limit=${limit}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to get recent sessions:', error);
        throw error;
    }
}

/**
 * Get running sessions
 * @returns {Promise<Array>} Running sessions
 */
async function getRunningSessions() {
    try {
        const response = await fetch(`${EXHAUSTIVE_API_BASE}/exhaustive-analysis/sessions?status=running&limit=10`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to get running sessions:', error);
        throw error;
    }
}

/**
 * Get session statistics
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} Session statistics
 */
async function getSessionStats(sessionId) {
    try {
        const response = await fetch(`${EXHAUSTIVE_API_BASE}/exhaustive-analysis/stats/${sessionId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to get session stats:', error);
        throw error;
    }
}

/**
 * Delete session
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} Deletion confirmation
 */
async function deleteSession(sessionId) {
    try {
        const response = await fetch(`${EXHAUSTIVE_API_BASE}/exhaustive-analysis/sessions/${sessionId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to delete session:', error);
        throw error;
    }
}

/**
 * Export analysis results
 * @param {string} sessionId - Session ID
 * @param {string} format - Export format (json/csv/excel)
 * @returns {Promise<Blob>} Exported data
 */
async function exportAnalysisResults(sessionId, format = 'json') {
    try {
        const response = await fetch(`${EXHAUSTIVE_API_BASE}/exhaustive-analysis/export/${sessionId}?format=${format}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.blob();
    } catch (error) {
        console.error('Failed to export analysis results:', error);
        throw error;
    }
}

/**
 * Get system status
 * @returns {Promise<Object>} System status information
 */
async function getSystemStatus() {
    try {
        const response = await fetch(`${EXHAUSTIVE_API_BASE}/exhaustive-analysis/status`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to get system status:', error);
        throw error;
    }
}

/**
 * Mock API functions for development/testing
 * These can be used when the backend is not available
 */
const mockExhaustiveAnalysisAPI = {
    startExhaustiveAnalysis: async (config) => {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return {
            success: true,
            session_id: `session_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
            status: 'started',
            message: 'Analysis started successfully'
        };
    },

    getAnalysisProgress: async (sessionId) => {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            session_id: sessionId,
            current_position: Math.floor(Math.random() * 100),
            total_positions: 100,
            success_count: Math.floor(Math.random() * 100),
            failure_count: 0,
            start_time: new Date(Date.now() - 300000).toISOString(),
            estimated_time_remaining: Math.floor(Math.random() * 60)
        };
    },

    getAnalysisResults: async (sessionId) => {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return {
            session_id: sessionId,
            mode: 'quick',
            positions_analyzed: 100,
            total_moves_analyzed: 5000,
            total_analysis_time: 1800.0,
            successful_analyses: 100,
            failed_analyses: 0,
            success_rate: 100.0,
            average_time_per_position: 18.0,
            average_moves_per_position: 50,
            engine_stats: {
                alpha_beta_success: 400,
                mcts_success: 0,
                neural_success: 400,
                pattern_success: 500
            },
            quality_distribution: {
                '!!': 5,
                '!': 15,
                '=': 40,
                '?!': 30,
                '?': 10
            }
        };
    },

    getRecentSessions: async (limit = 10) => {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return Array.from({ length: limit }, (_, i) => ({
            session_id: `session_${Date.now() - i * 3600000}_${Math.random().toString(36).substring(2, 8)}`,
            mode: ['quick', 'standard', 'deep', 'exhaustive'][Math.floor(Math.random() * 4)],
            positions_analyzed: Math.floor(Math.random() * 1000) + 10,
            total_analysis_time: Math.floor(Math.random() * 3600) + 60,
            success_rate: Math.floor(Math.random() * 20) + 80,
            created_at: new Date(Date.now() - i * 3600000).toISOString()
        }));
    },

    stopAnalysis: async (sessionId) => {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            success: true,
            session_id: sessionId,
            status: 'stopped',
            message: 'Analysis stopped successfully'
        };
    },

    getSessionStats: async (sessionId) => {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            session_id: sessionId,
            mode: 'quick',
            positions_analyzed: 100,
            total_moves_analyzed: 5000,
            total_analysis_time: 1800.0,
            successful_analyses: 100,
            failed_analyses: 0,
            success_rate: 100.0,
            engine_stats: {
                alpha_beta_success: 400,
                mcts_success: 0,
                neural_success: 400,
                pattern_success: 500
            }
        };
    },

    deleteSession: async (sessionId) => {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            success: true,
            session_id: sessionId,
            message: 'Session deleted successfully'
        };
    },

    exportAnalysisResults: async (sessionId, format = 'json') => {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockData = {
            session_id: sessionId,
            results: Array.from({ length: 100 }, (_, i) => ({
                position_id: i + 1,
                quality_score: Math.random() * 100,
                quality_tier: ['!!', '!', '=', '?!', '?'][Math.floor(Math.random() * 5)]
            }))
        };
        
        const blob = new Blob([JSON.stringify(mockData, null, 2)], {
            type: 'application/json'
        });
        
        return blob;
    },

    getSystemStatus: async () => {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            status: 'operational',
            version: '1.0.0',
            uptime: Math.floor(Math.random() * 86400),
            active_sessions: Math.floor(Math.random() * 10),
            total_sessions: Math.floor(Math.random() * 1000) + 100,
            database_size: Math.floor(Math.random() * 1000000) + 100000
        };
    }
};

// Export API functions
window.exhaustiveAnalysisAPI = {
    startExhaustiveAnalysis,
    getAnalysisProgress,
    stopAnalysis,
    getAnalysisResults,
    getRecentSessions,
    getRunningSessions,
    getSessionStats,
    deleteSession,
    exportAnalysisResults,
    getSystemStatus,
    // Mock API for development
    mock: mockExhaustiveAnalysisAPI
};
