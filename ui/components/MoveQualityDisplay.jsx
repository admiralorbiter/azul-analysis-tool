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
 * - EDUCATIONAL ENHANCEMENTS: Strategic explanations and learning tips
 * 
 * Version: 1.1.0 - Added educational explanations and strategic reasoning
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
    const [showEducational, setShowEducational] = useState(false);
    const [isRealData, setIsRealData] = useState(false);

    // Quality tier configuration with educational content
    const qualityTierConfig = {
        '!!': { 
            label: 'Brilliant', 
            color: '#FFD700', 
            icon: '⭐', 
            bgColor: '#FFF8DC',
            borderColor: '#FFD700',
            educational: {
                title: 'Brilliant Move - Strategic Masterpiece',
                explanation: 'This move demonstrates exceptional strategic thinking. It likely creates multiple threats, blocks opponent opportunities, and sets up future advantages.',
                strategicReasoning: 'Brilliant moves often combine tactical precision with long-term strategic vision. They may sacrifice immediate gains for superior position.',
                learningTips: [
                    'Look for moves that create multiple threats',
                    'Consider long-term strategic implications',
                    'Evaluate opponent\'s best responses',
                    'Balance immediate gains with future opportunities'
                ],
                bestPractices: 'When you find a brilliant move, take time to understand why it works. These moves often reveal deep strategic patterns.'
            }
        },
        '!': { 
            label: 'Excellent', 
            color: '#4CAF50', 
            icon: '💎', 
            bgColor: '#E8F5E8',
            borderColor: '#4CAF50',
            educational: {
                title: 'Excellent Move - Strong Strategic Play',
                explanation: 'This move is strategically sound and likely the best available option. It improves your position while limiting opponent opportunities.',
                strategicReasoning: 'Excellent moves typically maximize your advantages while minimizing risks. They follow sound strategic principles.',
                learningTips: [
                    'Focus on moves that improve your position',
                    'Consider the principle of least resistance',
                    'Evaluate risk-reward ratios carefully',
                    'Look for moves that limit opponent options'
                ],
                bestPractices: 'Excellent moves are the foundation of strong play. Practice identifying these moves consistently.'
            }
        },
        '=': { 
            label: 'Good', 
            color: '#2196F3', 
            icon: '👍', 
            bgColor: '#E3F2FD',
            borderColor: '#2196F3',
            educational: {
                title: 'Good Move - Solid Strategic Choice',
                explanation: 'This move is fundamentally sound and maintains a good position. While not exceptional, it avoids mistakes and keeps options open.',
                strategicReasoning: 'Good moves maintain equilibrium and avoid weakening your position. They provide a solid foundation for future play.',
                learningTips: [
                    'Prioritize moves that don\'t weaken your position',
                    'Maintain flexibility for future opportunities',
                    'Avoid moves that create unnecessary weaknesses',
                    'Consider the principle of least commitment'
                ],
                bestPractices: 'Good moves are the backbone of consistent play. Master these before attempting more complex strategies.'
            }
        },
        '?!': { 
            label: 'Dubious', 
            color: '#FF9800', 
            icon: '⚠️', 
            bgColor: '#FFF3E0',
            borderColor: '#FF9800',
            educational: {
                title: 'Dubious Move - Questionable Strategic Choice',
                explanation: 'This move has significant drawbacks or risks. While it might work in some situations, it\'s generally not recommended.',
                strategicReasoning: 'Dubious moves often involve unnecessary risks or fail to address key strategic concerns. They may create weaknesses.',
                learningTips: [
                    'Look for safer alternatives',
                    'Consider the risks before making the move',
                    'Evaluate if the potential gains justify the risks',
                    'Ask yourself if this move creates weaknesses'
                ],
                bestPractices: 'When you see a dubious move, look for better alternatives. Sometimes the best move is to avoid making a move.'
            }
        },
        '?': { 
            label: 'Poor', 
            color: '#F44336', 
            icon: '❌', 
            bgColor: '#FFEBEE',
            borderColor: '#F44336',
            educational: {
                title: 'Poor Move - Strategic Mistake',
                explanation: 'This move is strategically unsound and likely worsens your position. It may create weaknesses or miss better opportunities.',
                strategicReasoning: 'Poor moves often violate basic strategic principles. They may create weaknesses, miss opportunities, or play into opponent plans.',
                learningTips: [
                    'Look for moves that improve your position',
                    'Consider the strategic implications carefully',
                    'Avoid moves that create weaknesses',
                    'Think about what your opponent wants you to do'
                ],
                bestPractices: 'Learn from poor moves by understanding why they don\'t work. This helps avoid similar mistakes in the future.'
            }
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

    // Educational Content Component
    const EducationalContent = ({ quality, config }) => {
        if (!showEducational) {
            return (
                <button
                    onClick={() => setShowEducational(true)}
                    style={{
                        background: 'none',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        padding: '8px 12px',
                        fontSize: '12px',
                        color: '#666',
                        cursor: 'pointer',
                        width: '100%',
                        marginTop: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                    }}
                >
                    <span>🎓</span>
                    <span>Learn About This Move</span>
                </button>
            );
        }

        const educational = config.educational;

        return (
            <div className="educational-content">
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
                        fontWeight: '600',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                    }}>
                        <span>🎓</span>
                        <span>{educational.title}</span>
                    </h4>
                    <button
                        onClick={() => setShowEducational(false)}
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
                    {/* Explanation */}
                    <div style={{ marginBottom: '12px' }}>
                        <div style={{ 
                            fontWeight: 'bold', 
                            marginBottom: '4px',
                            color: '#333'
                        }}>
                            📖 Explanation
                        </div>
                        <div>{educational.explanation}</div>
                    </div>

                    {/* Strategic Reasoning */}
                    <div style={{ marginBottom: '12px' }}>
                        <div style={{ 
                            fontWeight: 'bold', 
                            marginBottom: '4px',
                            color: '#333'
                        }}>
                            ♟️ Strategic Reasoning
                        </div>
                        <div>{educational.strategicReasoning}</div>
                    </div>

                    {/* Learning Tips */}
                    <div style={{ marginBottom: '12px' }}>
                        <div style={{ 
                            fontWeight: 'bold', 
                            marginBottom: '4px',
                            color: '#333'
                        }}>
                            💡 Learning Tips
                        </div>
                        <ul style={{ 
                            margin: '4px 0', 
                            paddingLeft: '16px',
                            fontSize: '11px'
                        }}>
                            {educational.learningTips.map((tip, index) => (
                                <li key={index} style={{ marginBottom: '2px' }}>{tip}</li>
                            ))}
                        </ul>
                    </div>

                    {/* Best Practices */}
                    <div>
                        <div style={{ 
                            fontWeight: 'bold', 
                            marginBottom: '4px',
                            color: '#333'
                        }}>
                            ✅ Best Practices
                        </div>
                        <div style={{ 
                            backgroundColor: '#e8f5e8',
                            padding: '6px 8px',
                            borderRadius: '4px',
                            borderLeft: '3px solid #4CAF50'
                        }}>
                            {educational.bestPractices}
                        </div>
                    </div>
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
                        marginTop: '8px'
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

            {/* Educational content */}
            <EducationalContent quality={quality} config={config} />

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