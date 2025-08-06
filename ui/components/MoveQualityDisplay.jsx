/**
 * Move Quality Display Component - Slice 3 Phase 1
 * 
 * Enhanced UI component for displaying move quality assessment results.
 * Features:
 * - Quality tier indicator with visual design
 * - Score breakdown with progress bars
 * - Confidence indicator
 * - Detailed analysis sections
 * - Responsive design with consistent styling
 * - Real data detection and enhanced analysis
 * 
 * Version: 1.0.2 - Enhanced real data detection and base64 FEN support
 */

const { useState, useEffect } = React;

const MoveQualityDisplay = ({ 
    gameState, 
    currentPlayer = 0, 
    onMoveRecommendation,
    className = '' 
}) => {
    const [moveAnalysis, setMoveAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showDetails, setShowDetails] = useState(false);
    const [isRealData, setIsRealData] = useState(false);

    // Quality tier configuration
    const qualityTierConfig = {
        '!!': { 
            label: 'Brilliant', 
            color: '#FFD700', 
            icon: '⭐', 
            bgColor: '#FFF8DC',
            borderColor: '#FFD700'
        },
        '!': { 
            label: 'Excellent', 
            color: '#4CAF50', 
            icon: '💎', 
            bgColor: '#E8F5E8',
            borderColor: '#4CAF50'
        },
        '=': { 
            label: 'Good', 
            color: '#2196F3', 
            icon: '👍', 
            bgColor: '#E3F2FD',
            borderColor: '#2196F3'
        },
        '?!': { 
            label: 'Dubious', 
            color: '#FF9800', 
            icon: '⚠️', 
            bgColor: '#FFF3E0',
            borderColor: '#FF9800'
        },
        '?': { 
            label: 'Poor', 
            color: '#F44336', 
            icon: '❌', 
            bgColor: '#FFEBEE',
            borderColor: '#F44336'
        }
    };

    // Auto-analyze when game state changes
    useEffect(() => {
        if (gameState && gameState.fen_string) {
            analyzeMoveQuality();
        }
    }, [gameState?.fen_string, currentPlayer]);

    // Helper function to detect real game data
    const isRealGameData = (fenString) => {
        if (!fenString) return false;
        
        // Check for base64 encoded strings
        if (fenString.startsWith('base64_')) {
            return true;
        }
        
        // Check for long encoded strings (likely real game data)
        if (fenString.length > 100) {
            // Exclude known test/position library patterns
            const testPatterns = [
                'local_', 'test_', 'simple_', 'complex_', 'midgame_', 
                'endgame_', 'opening_', 'position'
            ];
            if (!testPatterns.some(pattern => fenString.includes(pattern))) {
                return true;
            }
        }
        
        // Check for standard FEN format (contains game state data)
        if (fenString.includes('|') || fenString.includes('/')) {
            return true;
        }
        
        // Check for complex game states that might not follow standard patterns
        if (fenString.length > 50 && !fenString.match(/^(initial|saved|test_|simple_|complex_|midgame_|endgame_|opening_|position|local_)/)) {
            return true;
        }
        
        return false;
    };

    const analyzeMoveQuality = async () => {
        console.log('MoveQualityDisplay: analyzeMoveQuality called');
        
        if (!gameState || !gameState.fen_string) {
            console.log('MoveQualityDisplay: No game state available');
            setError('No game state available');
            return;
        }

        console.log('MoveQualityDisplay: Analyzing FEN string:', gameState.fen_string);
        console.log('MoveQualityDisplay: FEN string type:', typeof gameState.fen_string);
        console.log('MoveQualityDisplay: FEN string length:', gameState.fen_string.length);

        // Detect if this is real game data
        const realData = isRealGameData(gameState.fen_string);
        setIsRealData(realData);
        console.log('MoveQualityDisplay: Is real game data:', realData);

        // Prepare FEN string for API call
        let apiFenString = gameState.fen_string;
        
        // If it's a long base64 string without prefix, add the prefix
        if (realData && gameState.fen_string.length > 100 && !gameState.fen_string.startsWith('base64_')) {
            // Check if it looks like base64 (contains only base64 characters)
            const base64Pattern = /^[A-Za-z0-9+/=]+$/;
            if (base64Pattern.test(gameState.fen_string)) {
                apiFenString = 'base64_' + gameState.fen_string;
                console.log('MoveQualityDisplay: Added base64_ prefix to FEN string');
            }
        }

        // Skip API calls for local position library states
        if (gameState.fen_string.startsWith('local_')) {
            console.log('MoveQualityDisplay: Using mock data for local_ FEN string');
            console.log('MoveQualityDisplay: FEN string starts with local_:', gameState.fen_string.startsWith('local_'));
            setMoveAnalysis({
                message: 'Move quality analysis not available for position library states',
                best_move: null,
                alternatives: [],
                quality_tier: '=',
                score: 0,
                is_real_data: false
            });
            return;
        }

        // For testing purposes, provide mock data if FEN string is test data or position library data
        // Also handle cases where the FEN string might be a simple identifier
        if (!realData && (gameState.fen_string.includes('test_') || 
            gameState.fen_string.startsWith('simple_') ||
            gameState.fen_string.startsWith('complex_') ||
            gameState.fen_string.startsWith('midgame_') ||
            gameState.fen_string.startsWith('endgame_') ||
            gameState.fen_string.startsWith('opening_') ||
            gameState.fen_string.includes('position') ||
            gameState.fen_string === 'initial' ||
            gameState.fen_string === 'saved' ||
            gameState.fen_string.length < 50)) {
            console.log('MoveQualityDisplay: Using mock data for position library FEN string (length:', gameState.fen_string.length, ')');
            const mockQuality = {
                quality_tier: '!',
                quality_score: 75.5,
                blocking_score: 80.0,
                strategic_score: 70.0,
                floor_line_score: 65.0,
                scoring_score: 85.0,
                confidence_score: 0.8,
                primary_reason: 'This is a strong move that balances tactical and strategic considerations.',
                move_description: 'Takes blue tile from factory 1 to pattern line 2'
            };
            
            setMoveAnalysis({
                success: true,
                best_move: mockQuality,
                alternatives: [
                    { ...mockQuality, quality_tier: '=', quality_score: 65.0, move_description: 'Alternative: Take red tile to pattern line 1' },
                    { ...mockQuality, quality_tier: '?!', quality_score: 45.0, move_description: 'Alternative: Take yellow tile to floor line' }
                ],
                analysis_complete: true,
                is_real_data: false
            });
            return;
        }

        setLoading(true);
        setError(null);

        console.log('MoveQualityDisplay: Making API call for FEN string:', apiFenString);

        try {
            const apiBase = window.API_CONSTANTS?.API_BASE || '/api/v1';
            const response = await fetch(`${apiBase}/analyze-move-quality`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fen_string: apiFenString,
                    current_player: currentPlayer,
                    include_alternatives: true,
                    max_alternatives: 4
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            console.log('MoveQualityDisplay: API response received:', data);

            if (data.success) {
                // Update real data status from API response
                setIsRealData(data.is_real_data || false);
                
                setMoveAnalysis({
                    success: true,
                    best_move: data.primary_recommendation,
                    alternatives: data.alternatives || [],
                    analysis_complete: true,
                    is_real_data: data.is_real_data || false,
                    data_quality: data.data_quality || 'mock',
                    analysis_enhanced: data.analysis_enhanced || null,
                    total_moves_analyzed: data.total_moves_analyzed || 0,
                    analysis_time_ms: data.analysis_time_ms || 0
                });
                
                if (onMoveRecommendation) {
                    onMoveRecommendation(data);
                }
            } else {
                setError(data.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('MoveQualityDisplay: API call failed:', error);
            setError(`Analysis failed: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    // Quality Tier Indicator Component
    const QualityTierIndicator = ({ quality }) => {
        const tierInfo = qualityTierConfig[quality.quality_tier] || qualityTierConfig['='];
        
        return (
            <div 
                className="quality-tier-indicator"
                style={{
                    backgroundColor: tierInfo.bgColor,
                    border: `2px solid ${tierInfo.borderColor}`,
                    borderRadius: '8px',
                    padding: '12px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '16px'
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '20px' }}>{tierInfo.icon}</span>
                    <div>
                        <div style={{ 
                            fontWeight: 'bold', 
                            color: tierInfo.color,
                            fontSize: '16px'
                        }}>
                            {tierInfo.label}
                        </div>
                        <div style={{ 
                            fontSize: '12px', 
                            color: '#666',
                            marginTop: '2px'
                        }}>
                            {quality.quality_tier} Tier
                        </div>
                    </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ 
                        fontSize: '18px', 
                        fontWeight: 'bold',
                        color: tierInfo.color
                    }}>
                        {quality.quality_score.toFixed(1)}
                    </div>
                    <div style={{ 
                        fontSize: '12px', 
                        color: '#666'
                    }}>
                        / 100
                    </div>
                </div>
            </div>
        );
    };

    // Score Breakdown Component
    const QualityScoreBreakdown = ({ quality }) => {
        const scoreComponents = [
            { 
                label: 'Tactical Value', 
                score: quality.blocking_score, 
                color: '#2196F3',
                icon: '🎯'
            },
            { 
                label: 'Strategic Value', 
                score: quality.strategic_score, 
                color: '#4CAF50',
                icon: '♟️'
            },
            { 
                label: 'Risk Assessment', 
                score: quality.floor_line_score, 
                color: '#FF9800',
                icon: '⚠️'
            },
            { 
                label: 'Opportunity Value', 
                score: quality.scoring_score, 
                color: '#9C27B0',
                icon: '💎'
            }
        ];

        return (
            <div className="score-breakdown">
                <h4 style={{ 
                    margin: '0 0 12px 0', 
                    fontSize: '14px', 
                    color: '#333',
                    fontWeight: '600'
                }}>
                    Score Breakdown
                </h4>
                <div style={{ display: 'grid', gap: '12px' }}>
                    {scoreComponents.map((component, index) => (
                        <ScoreBar 
                            key={index}
                            label={component.label}
                            score={component.score}
                            color={component.color}
                            icon={component.icon}
                        />
                    ))}
                </div>
            </div>
        );
    };

    // Individual Score Bar Component
    const ScoreBar = ({ label, score, color, icon }) => {
        const percentage = Math.min(100, Math.max(0, score));
        
        return (
            <div className="score-bar">
                <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '4px'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ fontSize: '14px' }}>{icon}</span>
                        <span style={{ 
                            fontSize: '12px', 
                            color: '#555',
                            fontWeight: '500'
                        }}>
                            {label}
                        </span>
                    </div>
                    <span style={{ 
                        fontSize: '12px', 
                        color: '#666',
                        fontWeight: '600'
                    }}>
                        {score.toFixed(1)}
                    </span>
                </div>
                <div style={{
                    width: '100%',
                    height: '6px',
                    backgroundColor: '#E0E0E0',
                    borderRadius: '3px',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        width: `${percentage}%`,
                        height: '100%',
                        backgroundColor: color,
                        borderRadius: '3px',
                        transition: 'width 0.3s ease'
                    }} />
                </div>
            </div>
        );
    };

    // Confidence Indicator Component
    const ConfidenceIndicator = ({ quality }) => {
        const confidence = quality.confidence_score || 0.5;
        const confidenceLevel = confidence >= 0.8 ? 'High' : 
                               confidence >= 0.6 ? 'Medium' : 'Low';
        const confidenceColor = confidence >= 0.8 ? '#4CAF50' : 
                               confidence >= 0.6 ? '#FF9800' : '#F44336';
        
        return (
            <div className="confidence-indicator">
                <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '8px'
                }}>
                    <span style={{ 
                        fontSize: '12px', 
                        color: '#555',
                        fontWeight: '500'
                    }}>
                        Analysis Confidence
                    </span>
                    <span style={{ 
                        fontSize: '12px', 
                        color: confidenceColor,
                        fontWeight: '600'
                    }}>
                        {confidenceLevel}
                    </span>
                </div>
                <div style={{
                    width: '100%',
                    height: '4px',
                    backgroundColor: '#E0E0E0',
                    borderRadius: '2px',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        width: `${confidence * 100}%`,
                        height: '100%',
                        backgroundColor: confidenceColor,
                        borderRadius: '2px',
                        transition: 'width 0.3s ease'
                    }} />
                </div>
            </div>
        );
    };

    // Detailed Analysis Component
    const DetailedAnalysis = ({ quality }) => {
        if (!showDetails) {
            return (
                <button
                    onClick={() => setShowDetails(true)}
                    style={{
                        background: 'none',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        padding: '8px 12px',
                        fontSize: '12px',
                        color: '#666',
                        cursor: 'pointer',
                        width: '100%',
                        marginTop: '12px'
                    }}
                >
                    Show Detailed Analysis
                </button>
            );
        }

        return (
            <div className="detailed-analysis">
                <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '12px'
                }}>
                    <h4 style={{ 
                        margin: 0, 
                        fontSize: '14px', 
                        color: '#333',
                        fontWeight: '600'
                    }}>
                        Detailed Analysis
                    </h4>
                    <button
                        onClick={() => setShowDetails(false)}
                        style={{
                            background: 'none',
                            border: 'none',
                            fontSize: '12px',
                            color: '#666',
                            cursor: 'pointer'
                        }}
                    >
                        Hide
                    </button>
                </div>
                
                <div style={{ 
                    backgroundColor: '#f8f9fa',
                    borderRadius: '6px',
                    padding: '12px',
                    fontSize: '12px',
                    lineHeight: '1.4',
                    color: '#555'
                }}>
                    {quality.primary_reason || 'No detailed analysis available.'}
                </div>
            </div>
        );
    };

    // Loading state
    if (loading) {
        return (
            <div className={`move-quality-display loading ${className}`}>
                <div style={{ 
                    textAlign: 'center', 
                    padding: '20px',
                    color: '#666'
                }}>
                    <div style={{ 
                        fontSize: '24px', 
                        marginBottom: '8px' 
                    }}>
                        ⏳
                    </div>
                    <div style={{ fontSize: '14px' }}>
                        Analyzing move quality...
                    </div>
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className={`move-quality-display error ${className}`}>
                <div style={{ 
                    backgroundColor: '#f8d7da',
                    color: '#721c24',
                    borderRadius: '6px',
                    padding: '12px',
                    fontSize: '12px'
                }}>
                    <div style={{ 
                        fontWeight: 'bold', 
                        marginBottom: '4px' 
                    }}>
                        ⚠️ Move Analysis Error
                    </div>
                    <div style={{ marginBottom: '8px' }}>{error}</div>
                    <button
                        onClick={analyzeMoveQuality}
                        style={{
                            padding: '4px 8px',
                            fontSize: '11px',
                            backgroundColor: '#721c24',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }}
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    // Show message if present (e.g., for local_ FEN)
    if (moveAnalysis && moveAnalysis.message) {
        return (
            <div className={`move-quality-display info ${className}`}>
                <div style={{ 
                    backgroundColor: '#d1ecf1',
                    color: '#0c5460',
                    borderRadius: '6px',
                    padding: '12px',
                    fontSize: '12px'
                }}>
                    {moveAnalysis.message}
                </div>
            </div>
        );
    }

    // Render main content
    if (!moveAnalysis || !moveAnalysis.success) {
        return (
            <div className={`move-quality-display empty ${className}`}>
                <div style={{ 
                    textAlign: 'center', 
                    padding: '20px',
                    color: '#666',
                    fontSize: '14px'
                }}>
                    <div style={{ 
                        fontSize: '24px', 
                        marginBottom: '8px' 
                    }}>
                        🎯
                    </div>
                    <div>Move quality analysis will appear here</div>
                </div>
            </div>
        );
    }

    const quality = moveAnalysis.best_move;
    const config = qualityTierConfig[quality.quality_tier] || qualityTierConfig['='];

    return (
        <div className={`move-quality-display ${className}`}>
            {/* Header with real data indicator */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '12px',
                padding: '8px 12px',
                backgroundColor: config.bgColor,
                border: `1px solid ${config.borderColor}`,
                borderRadius: '6px'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '16px' }}>{config.icon}</span>
                    <div>
                        <div style={{ 
                            fontWeight: 'bold', 
                            color: config.color,
                            fontSize: '14px'
                        }}>
                            {config.label} Move
                        </div>
                        <div style={{ 
                            fontSize: '12px', 
                            color: '#666' 
                        }}>
                            {quality.quality_score?.toFixed(1) || 'N/A'}/100
                        </div>
                    </div>
                </div>
                
                {/* Real data indicator */}
                {isRealData && (
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        padding: '2px 6px',
                        backgroundColor: '#4CAF50',
                        color: 'white',
                        borderRadius: '4px',
                        fontSize: '10px',
                        fontWeight: 'bold'
                    }}>
                        <span>🎯</span>
                        <span>REAL DATA</span>
                    </div>
                )}
            </div>

            {/* Enhanced analysis info for real data */}
            {isRealData && moveAnalysis.analysis_enhanced && (
                <div style={{
                    marginBottom: '12px',
                    padding: '8px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    fontSize: '11px',
                    color: '#666'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span>Analysis Confidence: {(moveAnalysis.analysis_enhanced.analysis_confidence * 100).toFixed(0)}%</span>
                        <span>Complexity: {(moveAnalysis.analysis_enhanced.position_complexity * 100).toFixed(0)}%</span>
                    </div>
                    {moveAnalysis.analysis_enhanced.educational_insights && moveAnalysis.analysis_enhanced.educational_insights.length > 0 && (
                        <div style={{ marginTop: '4px' }}>
                            <strong>Insights:</strong> {moveAnalysis.analysis_enhanced.educational_insights[0]}
                        </div>
                    )}
                </div>
            )}

            {/* Score breakdown */}
            <div style={{ marginBottom: '12px' }}>
                <div style={{ 
                    fontSize: '12px', 
                    fontWeight: 'bold', 
                    marginBottom: '8px',
                    color: '#333'
                }}>
                    Score Breakdown
                </div>
                <div style={{ display: 'grid', gap: '6px' }}>
                    {[
                        { key: 'blocking_score', label: 'Blocking', icon: '🛡️', color: '#4CAF50' },
                        { key: 'scoring_score', label: 'Scoring', icon: '🎯', color: '#2196F3' },
                        { key: 'strategic_score', label: 'Strategic', icon: '♟️', color: '#FF9800' },
                        { key: 'floor_line_score', label: 'Floor Line', icon: '🏠', color: '#9C27B0' }
                    ].map(({ key, label, icon, color }) => (
                        <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ fontSize: '12px' }}>{icon}</span>
                            <span style={{ 
                                fontSize: '11px', 
                                minWidth: '60px',
                                color: '#666'
                            }}>
                                {label}
                            </span>
                            <div style={{ 
                                flex: 1, 
                                height: '8px', 
                                backgroundColor: '#e0e0e0',
                                borderRadius: '4px',
                                overflow: 'hidden'
                            }}>
                                <div style={{
                                    height: '100%',
                                    width: `${(quality[key] || 0)}%`,
                                    backgroundColor: color,
                                    transition: 'width 0.3s ease'
                                }} />
                            </div>
                            <span style={{ 
                                fontSize: '10px', 
                                color: '#666',
                                minWidth: '25px',
                                textAlign: 'right'
                            }}>
                                {(quality[key] || 0).toFixed(0)}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Confidence indicator */}
            <div style={{ marginBottom: '12px' }}>
                <div style={{ 
                    fontSize: '12px', 
                    fontWeight: 'bold', 
                    marginBottom: '4px',
                    color: '#333'
                }}>
                    Confidence
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ 
                        flex: 1, 
                        height: '6px', 
                        backgroundColor: '#e0e0e0',
                        borderRadius: '3px',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            height: '100%',
                            width: `${(quality.confidence_score || 0) * 100}%`,
                            backgroundColor: quality.confidence_score > 0.7 ? '#4CAF50' : 
                                          quality.confidence_score > 0.4 ? '#FF9800' : '#F44336',
                            transition: 'width 0.3s ease'
                        }} />
                    </div>
                    <span style={{ 
                        fontSize: '10px', 
                        color: '#666',
                        minWidth: '30px'
                    }}>
                        {((quality.confidence_score || 0) * 100).toFixed(0)}%
                    </span>
                </div>
            </div>

            {/* Move description */}
            {quality.move_description && (
                <div style={{ 
                    marginBottom: '12px',
                    padding: '8px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    fontSize: '11px',
                    color: '#555'
                }}>
                    <strong>Move:</strong> {quality.move_description}
                </div>
            )}

            {/* Detailed analysis */}
            <div style={{ marginBottom: '12px' }}>
                <button
                    onClick={() => setShowDetails(!showDetails)}
                    style={{
                        width: '100%',
                        padding: '6px 8px',
                        backgroundColor: 'transparent',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '11px',
                        cursor: 'pointer',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}
                >
                    <span>Detailed Analysis</span>
                    <span>{showDetails ? '▼' : '▶'}</span>
                </button>
                
                {showDetails && (
                    <div style={{
                        marginTop: '8px',
                        padding: '8px',
                        backgroundColor: '#f8f9fa',
                        borderRadius: '4px',
                        fontSize: '11px',
                        lineHeight: '1.4',
                        color: '#555'
                    }}>
                        {quality.primary_reason || 'No detailed analysis available.'}
                    </div>
                )}
            </div>

            {/* Analysis metadata */}
            <div style={{
                fontSize: '10px',
                color: '#999',
                textAlign: 'center',
                padding: '4px',
                borderTop: '1px solid #eee'
            }}>
                {moveAnalysis.total_moves_analyzed > 0 && (
                    <span>Analyzed {moveAnalysis.total_moves_analyzed} moves</span>
                )}
                {moveAnalysis.analysis_time_ms > 0 && (
                    <span style={{ marginLeft: '8px' }}>
                        in {moveAnalysis.analysis_time_ms}ms
                    </span>
                )}
            </div>
        </div>
    );
};

// Export to window for global access
window.MoveQualityDisplay = MoveQualityDisplay; 