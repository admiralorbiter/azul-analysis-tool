// PatternAnalysis.js - Pattern Detection UI Component
const { useState, useEffect } = React;

function PatternAnalysis({ gameState, currentPlayer = 0, onPatternDetected }) {
    const [patterns, setPatterns] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showDetails, setShowDetails] = useState(false);
    
    // Pattern detection API call
    const detectPatterns = async () => {
        if (!gameState || !gameState.fen_string) {
            setError('No game state available');
            return;
        }
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch('/api/v1/detect-patterns', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fen_string: gameState.fen_string,
                    current_player: currentPlayer,
                    include_blocking_opportunities: true,
                    include_move_suggestions: true,
                    urgency_threshold: 0.6  // Show more opportunities
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            setPatterns(data);
            
            // Notify parent component
            if (onPatternDetected) {
                onPatternDetected(data);
            }
            
        } catch (err) {
            console.error('Pattern detection error:', err);
            setError(`Pattern detection failed: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };
    
    // Auto-detect patterns when game state changes
    useEffect(() => {
        // Reset state when game state changes
        setPatterns(null);
        setError(null);
        setShowDetails(false);
        
        if (gameState && gameState.fen_string) {
            detectPatterns();
        }
    }, [gameState?.fen_string, currentPlayer, gameState?.factories, gameState?.players]);
    
    // Color mapping for display
    const colorMap = {
        0: { name: 'Blue', class: 'blue-tile' },
        1: { name: 'Yellow', class: 'yellow-tile' },
        2: { name: 'Red', class: 'red-tile' },
        3: { name: 'Black', class: 'black-tile' },
        4: { name: 'White', class: 'white-tile' }
    };
    
    // Urgency level styling
    const getUrgencyClass = (urgencyScore) => {
        if (urgencyScore > 0.8) return 'urgency-high';
        if (urgencyScore > 0.6) return 'urgency-medium';
        return 'urgency-low';
    };
    
    const getUrgencyIcon = (urgencyScore) => {
        if (urgencyScore > 0.8) return '🚨';
        if (urgencyScore > 0.6) return '⚠️';
        return 'ℹ️';
    };
    
    if (loading) {
        return (
            <div className="pattern-analysis loading">
                <div className="loading-spinner">🔍</div>
                <div>Analyzing patterns...</div>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="pattern-analysis error">
                <div className="error-icon">❌</div>
                <div className="error-message">{error}</div>
                <button onClick={detectPatterns} className="retry-button">
                    Retry Analysis
                </button>
            </div>
        );
    }
    
    if (!patterns) {
        return (
            <div className="pattern-analysis empty">
                <div className="empty-icon">🎯</div>
                <div>No patterns detected</div>
            </div>
        );
    }
    
    return (
        <div className="pattern-analysis">
            <div className="pattern-header">
                <h3>🎯 Pattern Analysis</h3>
                <div className="pattern-summary">
                    <span className="pattern-count">
                        {patterns.total_patterns} pattern{patterns.total_patterns !== 1 ? 's' : ''} detected
                    </span>
                    <span className="confidence-score">
                        Confidence: {(patterns.confidence_score * 100).toFixed(0)}%
                    </span>
                </div>
                <button 
                    onClick={() => setShowDetails(!showDetails)}
                    className="toggle-details-button"
                >
                    {showDetails ? 'Hide Details' : 'Show Details'}
                </button>
            </div>
            
            {patterns.blocking_opportunities && patterns.blocking_opportunities.length > 0 && (
                <div className="blocking-opportunities">
                    <h4>🛡️ Blocking Opportunities</h4>
                    <div className="opportunities-list">
                        {patterns.blocking_opportunities.map((opportunity, index) => (
                            <div 
                                key={index} 
                                className={`opportunity-card ${getUrgencyClass(opportunity.urgency_score)}`}
                            >
                                <div className="opportunity-header">
                                    <span className="urgency-icon">
                                        {getUrgencyIcon(opportunity.urgency_score)}
                                    </span>
                                    <span className="target-info">
                                        Opponent {opportunity.target_player + 1} - 
                                        Pattern Line {opportunity.target_pattern_line + 1}
                                    </span>
                                    <span className="urgency-level">
                                        {opportunity.urgency_level}
                                    </span>
                                </div>
                                
                                <div className="opportunity-details">
                                    <div className="color-info">
                                        <span className={`color-indicator ${colorMap[opportunity.target_color]?.class}`}>
                                            {colorMap[opportunity.target_color]?.name}
                                        </span>
                                        <span className="tiles-needed">
                                            Needs {opportunity.blocking_tiles_available} more tiles
                                        </span>
                                    </div>
                                    
                                    <div className="blocking-info">
                                        <span className="blocking-sources">
                                            Available in: 
                                            {opportunity.blocking_factories.map(f => ` Factory ${f + 1}`).join(',')}
                                            {opportunity.blocking_center && ', Center'}
                                        </span>
                                    </div>
                                    
                                    {showDetails && (
                                        <div className="opportunity-description">
                                            {opportunity.description}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            
            {patterns.move_suggestions && patterns.move_suggestions.length > 0 && (
                <div className="move-suggestions">
                    <h4>💡 Suggested Moves</h4>
                    <div className="suggestions-list">
                        {patterns.move_suggestions.slice(0, 3).map((suggestion, index) => (
                            <div key={index} className="suggestion-card">
                                <div className="suggestion-header">
                                    <span className="suggestion-type">Blocking Move</span>
                                    <span className="suggestion-urgency">
                                        Urgency: {suggestion.urgency_score.toFixed(2)}
                                    </span>
                                </div>
                                <div className="suggestion-action">
                                    Take {suggestion.suggested_action.num_to_floor_line} 
                                    {colorMap[suggestion.suggested_action.tile_type]?.name} tiles 
                                    from Factory {suggestion.suggested_action.source_id + 1}
                                </div>
                                <div className="suggestion-description">
                                    {suggestion.description}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            
            {patterns.total_patterns === 0 && (
                <div className="no-patterns">
                    <div className="no-patterns-icon">🎯</div>
                    <div className="no-patterns-message">
                        No tactical patterns detected in this position.
                    </div>
                    <div className="no-patterns-hint">
                        Try analyzing a position where opponents have tiles in pattern lines.
                    </div>
                </div>
            )}
        </div>
    );
}

// Export for use in other components
window.PatternAnalysis = PatternAnalysis; 