// useGameState.js - Custom hook for game state management
const { useState, useEffect, useCallback } = React;

// Import API dependencies from window
const defaultGameAPI = window.gameAPI || {};
const {
    initializeSession = () => Promise.resolve(),
    getGameState = () => Promise.resolve(),
    saveGameState = () => Promise.resolve(),
    executeMove = () => Promise.resolve({})
} = defaultGameAPI;

window.useGameState = function useGameState() {
    // Core state
    const [sessionStatus, setSessionStatus] = useState('connecting');
    const [statusMessage, setStatusMessage] = useState('Initializing...');
    const [loading, setLoading] = useState(false);
    const [gameState, setGameState] = useState(null);
    
    // State stability tracking
    const [hasStableState, setHasStableState] = useState(false);
    const [lastStateHash, setLastStateHash] = useState(null);
    
    // Helper function to create a simple hash of game state for comparison
    const createStateHash = useCallback((state) => {
        if (!state) return null;
        try {
            // Create a simple hash based on factories and player scores
            const factoriesHash = JSON.stringify(state.factories || []);
            const scoresHash = JSON.stringify(state.players?.map(p => p.score) || []);
            return `${factoriesHash}_${scoresHash}`;
        } catch (error) {
            console.error('Error creating state hash:', error);
            return null;
        }
    }, []);
    
    // Debug setGameState calls
    const debugSetGameState = useCallback(async (newState) => {
        console.log('App: setGameState called with:', newState);
        
        // For position library data, handle it locally without backend processing
        if (newState && newState.factories && newState.center && newState.players) {
            console.log('App: Position library data detected, handling locally');
            // Generate a local FEN string for position library data
            const stateHash = btoa(JSON.stringify(newState)).slice(0, 8);
            const localFen = `local_${stateHash}`;
            
            // Add FEN string to the state
            const stateWithFen = { ...newState, fen_string: localFen };
            console.log('App: Setting position library state locally:', stateWithFen);
            setGameState(stateWithFen);
            return;
        }
        
        // If the new state doesn't have a proper fen_string, get one from the backend
        if (newState && (!newState.fen_string || newState.fen_string === 'initial')) {
            try {
                // Send the state to backend to get a proper FEN string
                const response = await fetch('/api/v1/game_state', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        fen_string: 'initial',
                        game_state: newState
                    })
                });
                
                if (response.ok) {
                    // Get the updated state with proper FEN string
                    const stateWithFen = await fetch('/api/v1/game_state?fen_string=initial').then(r => r.json());
                    const updatedState = stateWithFen.game_state || stateWithFen;
                    console.log('App: Updated state with FEN:', updatedState);
                    setGameState(updatedState);
                    return;
                }
            } catch (error) {
                console.warn('Failed to get FEN string for state, using original:', error);
            }
        }
        
        setGameState(newState);
    }, []);
    
    // Manual refresh function
    const manualRefresh = useCallback(() => {
        if (sessionStatus === 'connected' && !loading) {
            setLoading(true);
            getGameState('saved').catch(() => getGameState('initial')).then(async data => {
                await debugSetGameState(data);
                setStatusMessage('Game state refreshed manually');
                setLastStateHash(createStateHash(data));
            }).catch(error => {
                console.error('Failed to refresh game state:', error);
                setStatusMessage('Failed to refresh game state');
            }).finally(() => {
                setLoading(false);
            });
        }
    }, [sessionStatus, loading, createStateHash, debugSetGameState]);

    // Initialize session
    useEffect(() => {
        initializeSession()
            .then(() => {
                setSessionStatus('connected');
                setStatusMessage('Connected to server');
                // Try to load saved state first, fall back to initial state
                return getGameState('saved').catch(() => {
                    console.log('No saved state found, loading initial state');
                    return getGameState('initial');
                });
            })
            .then(async data => {
                console.log('Game state loaded:', data);
                await debugSetGameState(data);
                setStatusMessage('Game loaded');
                setHasStableState(true);
                setLastStateHash(createStateHash(data));
            })
            .catch(error => {
                setSessionStatus('error');
                setStatusMessage(`Connection failed: ${error.message}`);
            });
    }, [debugSetGameState, createStateHash]);

    return {
        // State
        sessionStatus,
        setSessionStatus,
        statusMessage,
        setStatusMessage,
        loading,
        setLoading,
        gameState,
        setGameState: debugSetGameState,
        hasStableState,
        setHasStableState,
        lastStateHash,
        setLastStateHash,
        
        // Functions
        createStateHash,
        manualRefresh,
        debugSetGameState
    };
} 