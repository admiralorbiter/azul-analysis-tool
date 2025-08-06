// ScoringOptimizationAnalysis.js - Scoring Optimization Detection UI Component
const { useState, useEffect } = React;

function ScoringOptimizationAnalysis({ gameState, currentPlayer = 0, onOptimizationDetected }) {
    const [optimizations, setOptimizations] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showDetails, setShowDetails] = useState(false);
    
    // Scoring optimization detection API call
    const detectScoringOptimization = async () => {
        if (!gameState || !gameState.fen_string) {
            setError('No game state available');
            return;
        }
        
        // Generate educational mock data for position library states
        if (gameState.fen_string.startsWith('local_')) {
            console.log('ScoringOptimizationAnalysis: Generating educational mock data for position library state');
            
            // Analyze position complexity for educational content
            const analyzePositionComplexity = (gameState) => {
                const factoryCount = gameState.factories?.length || 0;
                const centerTiles = gameState.center?.length || 0;
                const playerBoards = gameState.players?.length || 0;
                
                let complexity = 0;
                complexity += factoryCount * 10;
                complexity += centerTiles * 5;
                complexity += playerBoards * 15;
                complexity = Math.min(complexity, 100);
                
                return {
                    score: complexity,
                    level: complexity < 30 ? 'beginner' : complexity < 70 ? 'intermediate' : 'advanced',
                    factors: { factories: factoryCount, centerTiles: centerTiles, playerBoards: playerBoards }
                };
            };
            
            // Generate educational scoring optimization analysis
            const generateEducationalScoringOptimization = (gameState, currentPlayer) => {
                const positionComplexity = analyzePositionComplexity(gameState);
                const factories = gameState.factories || [];
                
                // Generate wall completion opportunities
                const wallCompletionOpportunities = [
                    {
                        row: 0,
                        col: 0,
                        color: 'B',
                        urgency_score: Math.max(6.0, positionComplexity.score / 10),
                        completion_value: Math.max(5, positionComplexity.score / 15),
                        description: `Educational wall completion: Blue tile at (0,0) offers ${positionComplexity.level} level scoring opportunity`,
                        confidence: 0.7
                    },
                    {
                        row: 1,
                        col: 1,
                        color: 'Y',
                        urgency_score: Math.max(5.0, positionComplexity.score / 12),
                        completion_value: Math.max(4, positionComplexity.score / 18),
                        description: `Educational wall completion: Yellow tile at (1,1) provides ${positionComplexity.level} level value`,
                        confidence: 0.65
                    }
                ];
                
                // Generate pattern line optimizations
                const patternLineOptimizations = [
                    {
                        pattern_line: 1,
                        target_color: 'B',
                        urgency_score: Math.max(7.0, positionComplexity.score / 8),
                        optimization_value: Math.max(6, positionComplexity.score / 12),
                        description: `Educational pattern line optimization: Line 1 for Blue tiles offers ${positionComplexity.level} level efficiency`,
                        confidence: 0.75
                    },
                    {
                        pattern_line: 2,
                        target_color: 'R',
                        urgency_score: Math.max(6.0, positionComplexity.score / 10),
                        optimization_value: Math.max(5, positionComplexity.score / 15),
                        description: `Educational pattern line optimization: Line 2 for Red tiles provides ${positionComplexity.level} level benefits`,
                        confidence: 0.7
                    }
                ];
                
                // Generate floor line optimizations
                const floorLineOptimizations = [
                    {
                        optimization_type: 'penalty_minimization',
                        urgency_score: Math.max(5.0, positionComplexity.score / 12),
                        penalty_reduction: Math.max(3, positionComplexity.score / 20),
                        description: `Educational floor line optimization: ${positionComplexity.level} level penalty minimization strategy`,
                        confidence: 0.65
                    }
                ];
                
                // Generate multiplier setups
                const multiplierSetups = [
                    {
                        multiplier_type: 'row_completion',
                        target_row: 0,
                        urgency_score: Math.max(8.0, positionComplexity.score / 7),
                        multiplier_value: Math.max(7, positionComplexity.score / 10),
                        description: `Educational multiplier setup: Row 0 completion offers ${positionComplexity.level} level multiplier value`,
                        confidence: 0.8
                    }
                ];
                
                // Generate move suggestions
                const moveSuggestions = factories.slice(0, 3).map((factory, index) => ({
                    move_type: 'factory_selection',
                    factory_id: index,
                    urgency_score: Math.max(6.0, positionComplexity.score / 10 - index),
                    expected_value: Math.max(5, positionComplexity.score / 15 - index * 2),
                    description: `Educational move suggestion: Factory ${index + 1} offers ${positionComplexity.level} level scoring optimization`,
                    confidence: 0.75 - (index * 0.1)
                }));
                
                return {
                    success: true,
                    wall_completion_opportunities: wallCompletionOpportunities,
                    pattern_line_optimizations: patternLineOptimizations,
                    floor_line_optimizations: floorLineOptimizations,
                    multiplier_setups: multiplierSetups,
                    move_suggestions: moveSuggestions,
                    position_complexity: positionComplexity,
                    educational_enabled: true,
                    data_quality: 'educational_mock',
                    analysis_summary: `Educational scoring optimization analysis for ${positionComplexity.level} complexity position`
                };
            };
            
            const educationalScoringData = generateEducationalScoringOptimization(gameState, currentPlayer);
            setOptimizations(educationalScoringData);
            
            // Notify parent component
            if (onOptimizationDetected) {
                onOptimizationDetected(educationalScoringData);
            }
            
            return;
        }
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch('/api/v1/detect-scoring-optimization', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fen_string: gameState.fen_string,
                    current_player: currentPlayer,
                    include_wall_completion: true,
                    include_pattern_line_optimization: true,
                    include_floor_line_optimization: true,
                    include_multiplier_setup: true,
                    include_move_suggestions: true,
                    urgency_threshold: 0.4  // Show more opportunities
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            setOptimizations(data);
            
            // Notify parent component
            if (onOptimizationDetected) {
                onOptimizationDetected(data);
            }
            
        } catch (err) {
            console.error('Scoring optimization detection error:', err);
            setError(`Scoring optimization detection failed: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };
    
    // Auto-detect optimizations when game state changes
    useEffect(() => {
        // Reset state when game state changes
        setOptimizations(null);
        setError(null);
        setShowDetails(false);
        
        if (gameState && gameState.fen_string) {
            detectScoringOptimization();
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
        if (urgencyScore >= 9.0) return 'urgency-critical';
        if (urgencyScore >= 7.0) return 'urgency-high';
        if (urgencyScore >= 4.0) return 'urgency-medium';
        return 'urgency-low';
    };
    
    const getUrgencyIcon = (urgencyScore) => {
        if (urgencyScore >= 9.0) return '🚨';
        if (urgencyScore >= 7.0) return '⚠️';
        if (urgencyScore >= 4.0) return '⚡';
        return 'ℹ️';
    };
    
    const renderTargetPosition = (targetPosition) => {
        if (!targetPosition || !Array.isArray(targetPosition)) {
            return '(?, ?)';
        }
        return `(${targetPosition[0] !== undefined ? targetPosition[0] : '?'}, ${targetPosition[1] !== undefined ? targetPosition[1] : '?'})`;
    };
    
    if (loading) {
        return (
            <div className="scoring-optimization-analysis loading">
                <div className="loading-spinner">🎯</div>
                <div>Analyzing scoring opportunities...</div>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="scoring-optimization-analysis error">
                <div className="error-icon">❌</div>
                <div className="error-message">{error}</div>
                <button 
                    className="btn-retry"
                    onClick={detectScoringOptimization}
                >
                    Retry Analysis
                </button>
            </div>
        );
    }
    
    if (!optimizations) {
        return (
            <div className="scoring-optimization-analysis">
                <div className="analysis-header">
                    <div className="header-icon">🎯</div>
                    <div className="header-content">
                        <h3>Scoring Optimization Analysis</h3>
                        <div className="summary-stats">
                            <span className="stat-item">
                                <span className="stat-number">0</span>
                                <span className="stat-label">opportunities</span>
                            </span>
                            <span className="stat-item">
                                <span className="stat-number">0%</span>
                                <span className="stat-label">confidence</span>
                            </span>
                        </div>
                    </div>
                    <button 
                        className="btn-details"
                        onClick={() => setShowDetails(!showDetails)}
                    >
                        Show Details
                    </button>
                </div>
                <div className="analysis-content">
                    <div className="no-optimizations">
                        <div className="no-optimizations-icon">🎯</div>
                        <div className="no-optimizations-message">
                            No scoring optimization opportunities detected in this position.
                        </div>
                        <div className="no-optimizations-suggestion">
                            Try analyzing a position with wall completion opportunities or high-value pattern lines.
                        </div>
                    </div>
                </div>
            </div>
        );
    }
    
    const totalOpportunities = optimizations.total_opportunities || 0;
    const confidenceScore = optimizations.confidence_score || 0;
    const opportunitiesDetected = optimizations.opportunities_detected || false;
    
    return (
        <div className="scoring-optimization-analysis">
            <div className="analysis-header">
                <div className="header-icon">🎯</div>
                <div className="header-content">
                    <h3>Scoring Optimization Analysis</h3>
                    <div className="summary-stats">
                        <span className="stat-item">
                            <span className="stat-number">{totalOpportunities}</span>
                            <span className="stat-label">opportunities</span>
                        </span>
                        <span className="stat-item">
                            <span className="stat-number">{Math.round(confidenceScore * 100)}%</span>
                            <span className="stat-label">confidence</span>
                        </span>
                        {optimizations.total_potential_bonus && (
                            <span className="stat-item">
                                <span className="stat-number">+{optimizations.total_potential_bonus}</span>
                                <span className="stat-label">potential bonus</span>
                            </span>
                        )}
                    </div>
                </div>
                <button 
                    className="btn-details"
                    onClick={() => setShowDetails(!showDetails)}
                >
                    {showDetails ? 'Hide Details' : 'Show Details'}
                </button>
            </div>
            
            {!opportunitiesDetected ? (
                <div className="analysis-content">
                    <div className="no-optimizations">
                        <div className="no-optimizations-icon">🎯</div>
                        <div className="no-optimizations-message">
                            No scoring optimization opportunities detected in this position.
                        </div>
                        <div className="no-optimizations-suggestion">
                            Try analyzing a position with wall completion opportunities or high-value pattern lines.
                        </div>
                    </div>
                </div>
            ) : (
                <div className="analysis-content">
                    {showDetails && (
                        <div className="optimization-details">
                            {/* Wall Completion Opportunities */}
                            {optimizations.wall_completion_opportunities && optimizations.wall_completion_opportunities.length > 0 && (
                                <div className="optimization-section">
                                    <h4>🏗️ Wall Completion Opportunities</h4>
                                    <div className="opportunity-list">
                                        {optimizations.wall_completion_opportunities.map((opp, index) => (
                                            <div key={index} className={`opportunity-item ${getUrgencyClass(opp.urgency_score)}`}>
                                                <div className="opportunity-header">
                                                    <span className="urgency-icon">{getUrgencyIcon(opp.urgency_score)}</span>
                                                    <span className="opportunity-type">{opp.opportunity_type}</span>
                                                    <span className="bonus-value">+{opp.bonus_value}</span>
                                                </div>
                                                <div className="opportunity-details">
                                                    <div className="target-info">
                                                        Target: {opp.target_color_name} at position {renderTargetPosition(opp.target_position)}
                                                    </div>
                                                    <div className="urgency-info">
                                                        Urgency: {opp.urgency_level} ({opp.urgency_score.toFixed(1)})
                                                    </div>
                                                    <div className="tiles-info">
                                                        Tiles needed: {opp.tiles_needed}, Available: {opp.tiles_available}
                                                    </div>
                                                    <div className="description">{opp.description}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            {/* Pattern Line Optimization */}
                            {optimizations.pattern_line_opportunities && optimizations.pattern_line_opportunities.length > 0 && (
                                <div className="optimization-section">
                                    <h4>📊 Pattern Line Optimization</h4>
                                    <div className="opportunity-list">
                                        {optimizations.pattern_line_opportunities.map((opp, index) => (
                                            <div key={index} className={`opportunity-item ${getUrgencyClass(opp.urgency_score)}`}>
                                                <div className="opportunity-header">
                                                    <span className="urgency-icon">{getUrgencyIcon(opp.urgency_score)}</span>
                                                    <span className="opportunity-type">{opp.opportunity_type}</span>
                                                    <span className="bonus-value">+{opp.bonus_value}</span>
                                                </div>
                                                <div className="opportunity-details">
                                                    <div className="target-info">
                                                        Target: {opp.target_color_name} at position {renderTargetPosition(opp.target_position)}
                                                    </div>
                                                    <div className="urgency-info">
                                                        Urgency: {opp.urgency_level} ({opp.urgency_score.toFixed(1)})
                                                    </div>
                                                    <div className="tiles-info">
                                                        Tiles needed: {opp.tiles_needed}, Available: {opp.tiles_available}
                                                    </div>
                                                    <div className="description">{opp.description}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            {/* Floor Line Optimization */}
                            {optimizations.floor_line_opportunities && optimizations.floor_line_opportunities.length > 0 && (
                                <div className="optimization-section">
                                    <h4>⚠️ Floor Line Risk Management</h4>
                                    <div className="opportunity-list">
                                        {optimizations.floor_line_opportunities.map((opp, index) => (
                                            <div key={index} className={`opportunity-item ${getUrgencyClass(opp.urgency_score)}`}>
                                                <div className="opportunity-header">
                                                    <span className="urgency-icon">{getUrgencyIcon(opp.urgency_score)}</span>
                                                    <span className="opportunity-type">{opp.opportunity_type}</span>
                                                    <span className="bonus-value">+{opp.bonus_value}</span>
                                                </div>
                                                <div className="opportunity-details">
                                                    <div className="target-info">
                                                        Target: {opp.target_color_name} at position {renderTargetPosition(opp.target_position)}
                                                    </div>
                                                    <div className="urgency-info">
                                                        Urgency: {opp.urgency_level} ({opp.urgency_score.toFixed(1)})
                                                    </div>
                                                    <div className="tiles-info">
                                                        Tiles needed: {opp.tiles_needed}, Available: {opp.tiles_available}
                                                    </div>
                                                    <div className="description">{opp.description}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            {/* Multiplier Setup */}
                            {optimizations.multiplier_opportunities && optimizations.multiplier_opportunities.length > 0 && (
                                <div className="optimization-section">
                                    <h4>🎯 Multiplier Setup</h4>
                                    <div className="opportunity-list">
                                        {optimizations.multiplier_opportunities.map((opp, index) => (
                                            <div key={index} className={`opportunity-item ${getUrgencyClass(opp.urgency_score)}`}>
                                                <div className="opportunity-header">
                                                    <span className="urgency-icon">{getUrgencyIcon(opp.urgency_score)}</span>
                                                    <span className="opportunity-type">{opp.opportunity_type}</span>
                                                    <span className="bonus-value">+{opp.bonus_value}</span>
                                                </div>
                                                <div className="opportunity-details">
                                                    <div className="target-info">
                                                        Target: {opp.target_color_name} at position {renderTargetPosition(opp.target_position)}
                                                    </div>
                                                    <div className="urgency-info">
                                                        Urgency: {opp.urgency_level} ({opp.urgency_score.toFixed(1)})
                                                    </div>
                                                    <div className="tiles-info">
                                                        Tiles needed: {opp.tiles_needed}, Available: {opp.tiles_available}
                                                    </div>
                                                    <div className="description">{opp.description}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            {/* Move Suggestions */}
                            {optimizations.move_suggestions && optimizations.move_suggestions.length > 0 && (
                                <div className="optimization-section">
                                    <h4>💡 Move Suggestions</h4>
                                    <div className="move-suggestions">
                                        {optimizations.move_suggestions.map((suggestion, index) => (
                                            <div key={index} className="move-suggestion">
                                                <span className="suggestion-icon">💡</span>
                                                <span className="suggestion-text">
                                                    {typeof suggestion === 'string' ? suggestion : suggestion.description || 'Move suggestion'}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                    
                    {!showDetails && (
                        <div className="optimization-summary">
                            <div className="summary-message">
                                {totalOpportunities} scoring optimization {totalOpportunities === 1 ? 'opportunity' : 'opportunities'} detected
                            </div>
                            <div className="summary-actions">
                                <button 
                                    className="btn-primary"
                                    onClick={() => setShowDetails(true)}
                                >
                                    View Details
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

window.ScoringOptimizationAnalysis = ScoringOptimizationAnalysis; 