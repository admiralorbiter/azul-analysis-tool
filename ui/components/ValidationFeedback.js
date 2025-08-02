/**
 * ValidationFeedback Component
 * 
 * Provides real-time visual feedback for rule violations during board editing.
 * Integrates with the BoardStateValidator to prevent illegal positions.
 */

// ValidationFeedback Component
function ValidationFeedback({ validationResult, targetElement, position = 'bottom' }) {
    if (!validationResult) return null;
    
    const { valid, error, suggestion, affected_elements } = validationResult;
    
    if (valid) {
        return (
            <div className="validation-feedback validation-success">
                <span className="validation-icon">✅</span>
                <span className="validation-message">Valid placement</span>
            </div>
        );
    }
    
    return (
        <div className={`validation-feedback validation-error position-${position}`}>
            <div className="validation-content">
                <span className="validation-icon">⚠️</span>
                <div className="validation-text">
                    <div className="validation-error-message">{error}</div>
                    {suggestion && (
                        <div className="validation-suggestion">
                            <span className="suggestion-icon">💡</span>
                            {suggestion}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

// PatternLineValidator - Real-time validation for pattern line editing
function PatternLineValidator({ playerId, lineIndex, currentColor, newColor, currentCount, newCount }) {
    const [validationResult, setValidationResult] = React.useState(null);
    
    React.useEffect(() => {
        // Real-time validation using simplified validator
        const result = validatePatternLineEditSimple(currentColor, newColor, currentCount, newCount, lineIndex + 1);
        setValidationResult(result);
    }, [currentColor, newColor, currentCount, newCount, lineIndex]);
    
    return <ValidationFeedback validationResult={validationResult} position="right" />;
}

// TileCountValidator - Validates tile conservation during editing
function TileCountValidator({ gameState, changedColor, changedAmount }) {
    const [validationResult, setValidationResult] = React.useState(null);
    
    React.useEffect(() => {
        if (!gameState || changedColor === undefined) return;
        
        // Count current tiles of this color
        const currentCount = countTilesOfColor(gameState, changedColor);
        const newCount = currentCount + changedAmount;
        
        let result = { valid: true };
        if (newCount > 20) {
            result = {
                valid: false,
                error: `Too many ${getColorName(changedColor)} tiles: ${newCount}/20`,
                suggestion: `Remove ${newCount - 20} tiles to maintain game balance`
            };
        } else if (newCount < 0) {
            result = {
                valid: false,
                error: `Cannot have negative tile count`,
                suggestion: `Add ${Math.abs(newCount)} tiles back`
            };
        }
        
        setValidationResult(result);
    }, [gameState, changedColor, changedAmount]);
    
    return <ValidationFeedback validationResult={validationResult} position="top" />;
}

// WallPlacementValidator - Validates wall tile placement
function WallPlacementValidator({ agent, row, col, isPlaced, wouldPlace }) {
    const [validationResult, setValidationResult] = React.useState(null);
    
    React.useEffect(() => {
        if (!agent || row === undefined || col === undefined) return;
        
        let result = { valid: true };
        
        if (wouldPlace && !isPlaced) {
            // Check if already filled
            if (agent.grid_state[row][col] === 1) {
                result = {
                    valid: false,
                    error: `Wall position (${row + 1}, ${col + 1}) is already filled`,
                    suggestion: `Choose an empty position`
                };
            }
        }
        
        setValidationResult(result);
    }, [agent, row, col, isPlaced, wouldPlace]);
    
    return <ValidationFeedback validationResult={validationResult} position="bottom" />;
}

// GlobalValidationStatus - Shows overall board validation status
function GlobalValidationStatus({ gameState }) {
    const [validationResult, setValidationResult] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    
    React.useEffect(() => {
        if (!gameState) return;
        
        setLoading(true);
        
        // Debounced validation to avoid too many API calls
        const validateTimeout = setTimeout(async () => {
            try {
                // Skip validation if no game state or invalid structure
                if (!gameState || typeof gameState !== 'object') {
                    setValidationResult({ valid: true });
                    setLoading(false);
                    return;
                }
                
                // Get session token from various possible sources
                const token = sessionToken || 
                             window.sessionStorage?.getItem('sessionToken') || 
                             window.localStorage?.getItem('sessionToken');
                
                const response = await fetch('/api/v1/validate-board-state', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token && { 'Authorization': `Bearer ${token}` })
                    },
                    body: JSON.stringify({ game_state: gameState })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    // Ensure we have the expected structure
                    setValidationResult({
                        valid: result.valid ?? true,
                        errors: result.errors || [],
                        warnings: result.warnings || []
                    });
                } else if (response.status === 401) {
                    // Authentication error - hide validation for now
                    setValidationResult({ valid: true });
                } else {
                    // If validation endpoint fails, assume position is valid
                    console.warn('Validation endpoint failed, assuming valid position');
                    setValidationResult({ valid: true });
                }
            } catch (error) {
                console.error('Validation error:', error);
                // On any error, assume position is valid
                setValidationResult({ valid: true });
            } finally {
                setLoading(false);
            }
        }, 1000); // Increased debounce to 1 second to reduce API calls
        
        return () => clearTimeout(validateTimeout);
    }, [gameState]);
    
    if (loading) {
        return (
            <div className="global-validation-status loading">
                <span className="validation-icon">⏳</span>
                <span>Validating position...</span>
            </div>
        );
    }
    
    if (!validationResult) return null;
    
    const { valid, errors, warnings } = validationResult;
    
    return (
        <div className={`global-validation-status ${valid ? 'valid' : 'invalid'}`}>
            <div className="validation-header">
                <span className="validation-icon">
                    {valid ? '✅' : '⚠️'}
                </span>
                <span className="validation-title">
                    {valid ? 'Position Valid' : 'Validation Issues'}
                </span>
            </div>
            
            {errors && errors.length > 0 && (
                <div className="validation-errors">
                    <h4>Errors:</h4>
                    <ul>
                        {errors.map((error, index) => (
                            <li key={index} className="validation-error-item">
                                <span className="error-icon">⚠️</span>
                                {error}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            
            {warnings && warnings.length > 0 && (
                <div className="validation-warnings">
                    <h4>Warnings:</h4>
                    <ul>
                        {warnings.map((warning, index) => (
                            <li key={index} className="validation-warning-item">
                                <span className="warning-icon">⚠️</span>
                                {warning}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

// Utility functions
function validatePatternLineEditSimple(currentColor, newColor, currentCount, newCount, lineCapacity) {
    // Critical rule: Single color per pattern line
    if (currentColor !== -1 && currentColor !== newColor) {
        return {
            valid: false,
            error: "Pattern lines can only contain one color",
            suggestion: "Clear the line first or choose the same color"
        };
    }
    
    // Capacity rule
    if (newCount > lineCapacity) {
        return {
            valid: false,
            error: `Line can only hold ${lineCapacity} tiles`,
            suggestion: `Reduce count to ${lineCapacity} or less`
        };
    }
    
    return { valid: true };
}

function countTilesOfColor(gameState, color) {
    let count = 0;
    
    // Count in factories
    if (gameState.factories) {
        gameState.factories.forEach(factory => {
            if (factory.tiles && factory.tiles[color]) {
                count += factory.tiles[color];
            }
        });
    }
    
    // Count in center pool
    if (gameState.centre_pool && gameState.centre_pool.tiles && gameState.centre_pool.tiles[color]) {
        count += gameState.centre_pool.tiles[color];
    }
    
    // Count in player areas
    if (gameState.agents) {
        gameState.agents.forEach(agent => {
            // Pattern lines
            for (let i = 0; i < 5; i++) {
                if (agent.lines_tile[i] === color) {
                    count += agent.lines_number[i];
                }
            }
            
            // Wall tiles
            for (let row = 0; row < 5; row++) {
                for (let col = 0; col < 5; col++) {
                    if (agent.grid_state[row][col] === 1 && agent.grid_scheme[row][col] === color) {
                        count += 1;
                    }
                }
            }
            
            // Floor tiles
            if (agent.floor_tiles) {
                agent.floor_tiles.forEach(tile => {
                    if (tile === color) count += 1;
                });
            }
        });
    }
    
    return count;
}

function getColorName(color) {
    const colorNames = ["Blue", "Yellow", "Red", "Black", "White"];
    return colorNames[color] || `Unknown(${color})`;
}

// Export components
window.ValidationFeedback = ValidationFeedback;
window.PatternLineValidator = PatternLineValidator;
window.TileCountValidator = TileCountValidator;
window.WallPlacementValidator = WallPlacementValidator;
window.GlobalValidationStatus = GlobalValidationStatus;