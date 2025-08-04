// StrategicPatternAnalysis.js - Strategic Pattern Analysis UI Component
const { useState, useEffect } = React;

function StrategicPatternAnalysis({ gameState, currentPlayer = 0, onStrategicAnalysis }) {
    const [strategicAnalysis, setStrategicAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showDetails, setShowDetails] = useState(false);
    
    // Strategic analysis API call
    const analyzeStrategicPatterns = async () => {
        if (!gameState || !gameState.fen_string) {
            setError('No game state available');
            return;
        }
        
        // Skip API calls for local position library states
        if (gameState.fen_string.startsWith('local_')) {
            setStrategicAnalysis({
                message: 'Strategic analysis not available for position library states',
                factory_control: [],
                endgame_scenarios: [],
                risk_reward_scenarios: [],
                move_suggestions: []
            });
            return;
        }
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch('/api/v1/analyze-strategic-patterns', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fen_string: gameState.fen_string,
                    current_player: currentPlayer,
                    include_factory_control: true,
                    include_endgame_scenarios: true,
                    include_risk_reward: true,
                    include_move_suggestions: true
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            setStrategicAnalysis(data);
            
            // Notify parent component
            if (onStrategicAnalysis) {
                onStrategicAnalysis(data);
            }
            
        } catch (err) {
            console.error('Strategic analysis error:', err);
            setError(`Strategic analysis failed: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };
    
    // Auto-analyze when game state changes
    useEffect(() => {
        // Reset state when game state changes
        setStrategicAnalysis(null);
        setError(null);
        setShowDetails(false);
        
        if (gameState && gameState.fen_string) {
            analyzeStrategicPatterns();
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
    
    // Confidence level styling
    const getConfidenceClass = (confidence) => {
        if (confidence > 0.8) return 'confidence-high';
        if (confidence > 0.6) return 'confidence-medium';
        return 'confidence-low';
    };
    
    const getConfidenceIcon = (confidence) => {
        if (confidence > 0.8) return '🎯';
        if (confidence > 0.6) return '⚡';
        return '💡';
    };
    
    if (loading) {
        return (
            <div className="strategic-analysis loading">
                <div className="loading-spinner">🎯</div>
                <div>Analyzing strategic patterns...</div>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="strategic-analysis error">
                <div className="error-icon">❌</div>
                <div className="error-message">{error}</div>
            </div>
        );
    }
    
    // Calculate summary metrics
    const strategicData = strategicAnalysis?.strategic_analysis || strategicAnalysis;
    const factoryControlCount = strategicData?.factory_control_opportunities?.length || 0;
    const endgameScenarioCount = strategicData?.endgame_scenarios?.length || 0;
    const riskRewardCount = strategicData?.risk_reward_scenarios?.length || 0;
    const moveSuggestionsCount = strategicData?.strategic_move_suggestions?.length || 0;
    const totalOpportunities = factoryControlCount + endgameScenarioCount + riskRewardCount;
    const confidence = strategicData?.confidence || 0;
    
    return (
        <div className="strategic-analysis">
            <div className="analysis-header">
                <div className="analysis-title">
                    <span className="analysis-icon">🎯</span>
                    Strategic Pattern Analysis
                </div>
                <div className="analysis-metrics">
                    <div className="metric-box">
                        {totalOpportunities} OPPORTUNITIES
                    </div>
                    <div className="confidence-display">
                        Confidence: {Math.round(confidence * 100)}%
                    </div>
                    <button 
                        className={`details-button ${showDetails ? 'active' : ''}`}
                        onClick={() => setShowDetails(!showDetails)}
                    >
                        {showDetails ? 'Hide Details' : 'Show Details'}
                    </button>
                </div>
            </div>
            
            {!strategicAnalysis || totalOpportunities === 0 ? (
                <div className="analysis-content no-results">
                    <div className="no-results-icon">🎯</div>
                    <div className="no-results-message">
                        No strategic patterns detected in this position.
                    </div>
                    <div className="no-results-hint">
                        Try analyzing a position with factory control opportunities, endgame scenarios, or risk/reward decisions.
                    </div>
                </div>
            ) : (
                <div className="analysis-content">
                    {showDetails && (
                        <div className="detailed-analysis">
                            {/* Factory Control Opportunities */}
                            {factoryControlCount > 0 && (
                                <div className="analysis-section">
                                    <h4 className="section-title">🏭 Factory Control Opportunities</h4>
                                    <div className="opportunity-list">
                                        {strategicData.factory_control_opportunities.map((opportunity, index) => (
                                            <div key={index} className="opportunity-item">
                                                <div className="opportunity-header">
                                                    <span className="opportunity-type">{opportunity.control_type}</span>
                                                    <span className={`confidence-badge ${getConfidenceClass(opportunity.confidence)}`}>
                                                        {Math.round(opportunity.confidence * 100)}%
                                                    </span>
                                                </div>
                                                <div className="opportunity-description">
                                                    {opportunity.description}
                                                </div>
                                                {opportunity.move_suggestions && (
                                                    <div className="recommended-actions">
                                                        <strong>Move Suggestions:</strong> {opportunity.move_suggestions.join(', ')}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            {/* Endgame Scenarios */}
                            {endgameScenarioCount > 0 && (
                                <div className="analysis-section">
                                    <h4 className="section-title">🔢 Endgame Scenarios</h4>
                                    <div className="opportunity-list">
                                        {strategicData.endgame_scenarios.map((scenario, index) => (
                                            <div key={index} className="opportunity-item">
                                                <div className="opportunity-header">
                                                    <span className="opportunity-type">{scenario.scenario_type}</span>
                                                    <span className={`confidence-badge ${getConfidenceClass(scenario.confidence)}`}>
                                                        {Math.round(scenario.confidence * 100)}%
                                                    </span>
                                                </div>
                                                <div className="opportunity-description">
                                                    {scenario.description}
                                                </div>
                                                {scenario.optimal_sequence && (
                                                    <div className="recommended-actions">
                                                        <strong>Optimal Sequence:</strong> {scenario.optimal_sequence.join(', ')}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            {/* Risk/Reward Scenarios */}
                            {riskRewardCount > 0 && (
                                <div className="analysis-section">
                                    <h4 className="section-title">⚖️ Risk/Reward Analysis</h4>
                                    <div className="opportunity-list">
                                        {strategicData.risk_reward_scenarios.map((scenario, index) => (
                                            <div key={index} className="opportunity-item">
                                                <div className="opportunity-header">
                                                    <span className="opportunity-type">{scenario.scenario_type}</span>
                                                    <span className={`confidence-badge ${getConfidenceClass(scenario.confidence)}`}>
                                                        {Math.round(scenario.confidence * 100)}%
                                                    </span>
                                                </div>
                                                <div className="opportunity-description">
                                                    {scenario.description}
                                                </div>
                                                <div className="risk-reward-metrics">
                                                    <span className="risk-metric">Risk: {Math.round(scenario.risk_score * 100)}%</span>
                                                    <span className="reward-metric">Reward: {Math.round(scenario.reward_score * 100)}%</span>
                                                </div>
                                                {scenario.recommendation && (
                                                    <div className="recommended-actions">
                                                        <strong>Recommendation:</strong> {scenario.recommendation}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            {/* Strategic Move Suggestions */}
                            {moveSuggestionsCount > 0 && (
                                <div className="analysis-section">
                                    <h4 className="section-title">🎯 Strategic Move Suggestions</h4>
                                    <div className="suggestion-list">
                                        {strategicAnalysis.strategic_move_suggestions.map((suggestion, index) => (
                                            <div key={index} className="suggestion-item">
                                                <span className="suggestion-number">{index + 1}.</span>
                                                <span className="suggestion-text">{suggestion}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            {/* Position Assessment */}
                            {strategicAnalysis.position_assessment && (
                                <div className="analysis-section">
                                    <h4 className="section-title">📊 Position Assessment</h4>
                                    <div className="position-assessment">
                                        <div className="assessment-text">
                                            {strategicAnalysis.position_assessment}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                    
                    {!showDetails && (
                        <div className="summary-view">
                            <div className="summary-icon">{getConfidenceIcon(confidence)}</div>
                            <div className="summary-message">
                                {totalOpportunities} strategic opportunities detected
                            </div>
                            <div className="summary-breakdown">
                                {factoryControlCount > 0 && <span className="breakdown-item">🏭 {factoryControlCount} factory control</span>}
                                {endgameScenarioCount > 0 && <span className="breakdown-item">🔢 {endgameScenarioCount} endgame</span>}
                                {riskRewardCount > 0 && <span className="breakdown-item">⚖️ {riskRewardCount} risk/reward</span>}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// Export for use in other components
window.StrategicPatternAnalysis = StrategicPatternAnalysis; 