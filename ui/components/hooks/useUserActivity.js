// useUserActivity.js - Custom hook for user activity tracking
const { useState, useEffect, useCallback } = React;

// Import API dependencies from window
const defaultGameAPI = window.gameAPI || {};
const {
    getGameState = () => Promise.resolve()
} = defaultGameAPI;

window.useUserActivity = function useUserActivity(gameState, setGameState, createStateHash, sessionStatus, loading, editMode, positionJustLoaded, hasStableState, lastStateHash, autoRefreshEnabled) {
    // User activity tracking
    const [userActive, setUserActive] = useState(false);
    const [lastUserActivity, setLastUserActivity] = useState(Date.now());
    
    // Track user activity
    const trackUserActivity = useCallback(() => {
        setUserActive(true);
        setLastUserActivity(Date.now());
        // Reset user active flag after 30 seconds of inactivity
        setTimeout(() => setUserActive(false), 30000);
    }, []);
    
    // Improved refresh game state periodically - only when necessary
    useEffect(() => {
        const interval = setInterval(() => {
            // Only refresh if:
            // 1. We're connected
            // 2. Not loading
            // 3. Not in edit mode
            // 4. Position wasn't just loaded
            // 5. We have a stable state (don't keep refreshing if state is unstable)
            // 6. User is not actively interacting (inactive for 30+ seconds)
            // 7. Auto-refresh is enabled
            const timeSinceActivity = Date.now() - lastUserActivity;
            const shouldRefresh = sessionStatus === 'connected' && 
                               !loading && 
                               !editMode && 
                               !positionJustLoaded && 
                               hasStableState && 
                               !userActive && 
                               timeSinceActivity > 30000 && // 30 seconds
                               autoRefreshEnabled;
                               
            if (shouldRefresh) {
                // Try to load saved state first, fall back to initial state
                getGameState('saved').catch(() => getGameState('initial')).then(async data => {
                    const newStateHash = createStateHash(data);
                    
                    // Only update if the state has actually changed
                    if (newStateHash !== lastStateHash) {
                        console.log('State changed, updating...');
                        await setGameState(data);
                        // Note: lastStateHash update should be handled by the parent component
                    } else {
                        console.log('State unchanged, skipping update');
                    }
                }).catch(error => {
                    console.error('Failed to refresh game state:', error);
                });
            }
        }, 15000); // Increased interval to 15 seconds to reduce unnecessary calls
        return () => clearInterval(interval);
    }, [sessionStatus, loading, editMode, positionJustLoaded, hasStableState, lastStateHash, createStateHash, userActive, lastUserActivity, autoRefreshEnabled, setGameState]);

    return {
        userActive,
        setUserActive,
        lastUserActivity,
        setLastUserActivity,
        trackUserActivity
    };
} 