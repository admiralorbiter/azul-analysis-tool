// Neural API functions for Azul Solver & Analysis Toolkit
// Extracted from main.js for modularity

// Use shared API constants - must be loaded after constants.js
const NEURAL_API_BASE = window.API_CONSTANTS?.API_BASE || '/api/v1';

// Neural Training Functions
async function startNeuralTraining(config) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/train`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to start neural training:', error);
        throw error;
    }
}

async function getNeuralTrainingStatus(sessionId) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/status/${sessionId}`);
        return await response.json();
    } catch (error) {
        console.error('Failed to get training status:', error);
        throw error;
    }
}

async function getNeuralTrainingProgress(sessionId) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/progress/${sessionId}`);
        return await response.json();
    } catch (error) {
        console.error('Failed to get training progress:', error);
        throw error;
    }
}

async function getNeuralTrainingLogs(sessionId) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/logs/${sessionId}`);
        return await response.json();
    } catch (error) {
        console.error('Failed to get training logs:', error);
        throw error;
    }
}

async function getAllTrainingSessions() {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/sessions`);
        return await response.json();
    } catch (error) {
        console.error('Failed to get training sessions:', error);
        throw error;
    }
}

async function deleteTrainingSession(sessionId) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/sessions/${sessionId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to delete training session:', error);
        throw error;
    }
}

async function stopNeuralTraining(sessionId) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/stop/${sessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to stop training:', error);
        throw error;
    }
}

// Neural Model Evaluation Functions
async function evaluateNeuralModel(config) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        const result = await response.json();
        
        // If evaluation started in background, return session info
        if (result.success && result.session_id) {
            return {
                ...result,
                background: true
            };
        }
        
        return result;
    } catch (error) {
        console.error('Failed to evaluate model:', error);
        throw error;
    }
}

async function getEvaluationStatus(sessionId) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/evaluate/status/${sessionId}`);
        return await response.json();
    } catch (error) {
        console.error('Failed to get evaluation status:', error);
        throw error;
    }
}

async function getAllEvaluationSessions() {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/evaluation-sessions`);
        return await response.json();
    } catch (error) {
        console.error('Failed to get evaluation sessions:', error);
        throw error;
    }
}

async function deleteEvaluationSession(sessionId) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/evaluation-sessions/${sessionId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to delete evaluation session:', error);
        throw error;
    }
}

// Neural Model Management Functions
async function getAvailableModels() {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/models`);
        return await response.json();
    } catch (error) {
        console.error('Failed to get available models:', error);
        throw error;
    }
}

async function getNeuralConfig() {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/config`);
        return await response.json();
    } catch (error) {
        console.error('Failed to get neural config:', error);
        throw error;
    }
}

async function saveNeuralConfig(config) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to save neural config:', error);
        throw error;
    }
}

// Neural Configuration Management Functions
async function getTrainingHistory(filters = {}) {
    try {
        const queryParams = new URLSearchParams(filters).toString();
        const response = await fetch(`${NEURAL_API_BASE}/neural/training-history?${queryParams}`);
        return await response.json();
    } catch (error) {
        console.error('Failed to get training history:', error);
        throw error;
    }
}

async function getNeuralConfigurations(filters = {}) {
    try {
        const queryParams = new URLSearchParams(filters).toString();
        const response = await fetch(`${NEURAL_API_BASE}/neural/configurations?${queryParams}`);
        return await response.json();
    } catch (error) {
        console.error('Failed to get neural configurations:', error);
        throw error;
    }
}

async function saveNeuralConfiguration(config) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/configurations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to save neural configuration:', error);
        throw error;
    }
}

async function updateNeuralConfiguration(configId, config) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/configurations/${configId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to update neural configuration:', error);
        throw error;
    }
}

async function deleteNeuralConfiguration(configId) {
    try {
        const response = await fetch(`${NEURAL_API_BASE}/neural/configurations/${configId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to delete neural configuration:', error);
        throw error;
    }
}

// Export all neural API functions
window.neuralAPI = {
    startNeuralTraining,
    getNeuralTrainingStatus,
    getNeuralTrainingProgress,
    getNeuralTrainingLogs,
    getAllTrainingSessions,
    deleteTrainingSession,
    stopNeuralTraining,
    evaluateNeuralModel,
    getEvaluationStatus,
    getAllEvaluationSessions,
    deleteEvaluationSession,
    getAvailableModels,
    getNeuralConfig,
    saveNeuralConfig,
    getTrainingHistory,
    getNeuralConfigurations,
    saveNeuralConfiguration,
    updateNeuralConfiguration,
    deleteNeuralConfiguration
}; 