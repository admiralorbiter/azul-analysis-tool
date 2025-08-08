/**
 * MoveQuality Module - Main Entry Point
 * 
 * Refactored from the original MoveQualityDisplay.jsx (47KB, 1149 lines)
 * into smaller, focused components for better maintainability and performance.
 * 
 * Components:
 * - MoveQualityDisplay: Main container component
 * - QualityTierIndicator: Visual quality tier display
 * - QualityScoreBreakdown: Score breakdown with progress bars
 * - ConfidenceIndicator: Confidence level visualization
 * - EducationalContent: Educational explanations and tips
 * - DetailedAnalysis: Collapsible detailed analysis
 * 
 * Version: 2.0.0 - Refactored for modularity and performance
 */

console.log('Loading MoveQuality index.jsx...');

const { useState, useEffect } = React;

// Import sub-components
const QualityTierIndicator = window.QualityTierIndicator || (() => <div>QualityTierIndicator not loaded</div>);
const QualityScoreBreakdown = window.QualityScoreBreakdown || (() => <div>QualityScoreBreakdown not loaded</div>);
const ConfidenceIndicator = window.ConfidenceIndicator || (() => <div>ConfidenceIndicator not loaded</div>);
const EducationalContent = window.EducationalContent || (() => <div>EducationalContent not loaded</div>);
const DetailedAnalysis = window.DetailedAnalysis || (() => <div>DetailedAnalysis not loaded</div>);

// Import utilities (aliased to avoid accidental global re-declarations elsewhere)
const {
    analyzeMoveQuality: mq_analyzeMoveQuality,
    isRealGameData: mq_isRealGameData
} = window.moveQualityUtils || {};

console.log('MoveQuality components loaded:', {
    QualityTierIndicator: !!window.QualityTierIndicator,
    QualityScoreBreakdown: !!window.QualityScoreBreakdown,
    ConfidenceIndicator: !!window.ConfidenceIndicator,
    EducationalContent: !!window.EducationalContent,
    DetailedAnalysis: !!window.DetailedAnalysis,
    moveQualityUtils: !!window.moveQualityUtils
});

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

    // Normalize FEN from either `fen` or legacy `fen_string`
    const getFenString = (state) => {
        if (!state) return null;
        return state.fen || state.fen_string || null;
    };

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
                    'Identify what makes this move risky',
                    'Look for safer alternatives',
                    'Consider the principle of least risk',
                    'Evaluate if the potential gains justify the risks'
                ],
                bestPractices: 'When you encounter dubious moves, analyze why they\'re risky. This helps you avoid similar mistakes.'
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
                explanation: 'This move has significant problems and should generally be avoided. It likely weakens your position or gives away advantages.',
                strategicReasoning: 'Poor moves often violate fundamental strategic principles. They may create weaknesses or miss opportunities.',
                learningTips: [
                    'Identify the specific problems with this move',
                    'Look for better alternatives',
                    'Understand the strategic principles being violated',
                    'Learn from the mistake to avoid repetition'
                ],
                bestPractices: 'Analyzing poor moves is crucial for improvement. Understand why they fail to avoid similar mistakes.'
            }
        }
    };

    // Perform analysis and update local state
    const runAnalysis = async () => {
        if (!mq_analyzeMoveQuality || !gameState) {
            return;
        }
        try {
            setLoading(true);
            setError(null);
            const result = await mq_analyzeMoveQuality(gameState, currentPlayer);
            setMoveAnalysis(result);
        } catch (err) {
            console.error('Move quality analysis failed:', err);
            setError(err?.message || 'Analysis failed');
        } finally {
            setLoading(false);
        }
    };

    // Check if we have real game data
    useEffect(() => {
        const fenString = getFenString(gameState);
        if (fenString) {
            const realData = mq_isRealGameData ? mq_isRealGameData(fenString) : false;
            setIsRealData(realData);
        }
    }, [gameState]);

    // Auto-analyze when game state changes
    useEffect(() => {
        if (gameState) {
            runAnalysis();
        }
    }, [gameState, currentPlayer]);

    const handleAnalyzeClick = () => {
        runAnalysis();
    };

    const handleLearnClick = () => {
        setShowEducational(!showEducational);
    };

    // Main render
    if (!gameState) {
        return (
            <div className={`move-quality-display ${className}`} style={{
                padding: '16px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                border: '1px solid #e9ecef'
            }}>
                <div style={{ textAlign: 'center', color: '#6c757d' }}>
                    <div style={{ fontSize: '14px', marginBottom: '8px' }}>
                        No game position loaded
                    </div>
                    <div style={{ fontSize: '12px' }}>
                        Load a position to analyze move quality
                    </div>
                </div>
            </div>
        );
    }

    if (loading) {
        return (
            <div className={`move-quality-display ${className}`} style={{
                padding: '16px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                border: '1px solid #e9ecef'
            }}>
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', marginBottom: '8px' }}>
                        Analyzing move quality...
                    </div>
                    <div style={{ fontSize: '12px', color: '#6c757d' }}>
                        This may take a few seconds
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className={`move-quality-display ${className}`} style={{
                padding: '16px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                border: '1px solid #e9ecef'
            }}>
                <div style={{ textAlign: 'center', color: '#dc3545' }}>
                    <div style={{ fontSize: '14px', marginBottom: '8px' }}>
                        Analysis Error
                    </div>
                    <div style={{ fontSize: '12px', marginBottom: '12px' }}>
                        {error}
                    </div>
                    <button
                        onClick={handleAnalyzeClick}
                        style={{
                            padding: '6px 12px',
                            backgroundColor: '#007bff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '12px',
                            cursor: 'pointer'
                        }}
                    >
                        Retry Analysis
                    </button>
                </div>
            </div>
        );
    }

    if (!moveAnalysis || !moveAnalysis.best_move) {
        return (
            <div className={`move-quality-display ${className}`} style={{
                padding: '16px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                border: '1px solid #e9ecef'
            }}>
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', marginBottom: '8px' }}>
                        Ready to analyze
                    </div>
                    <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '12px' }}>
                        Click to analyze move quality
                    </div>
                    <button
                        onClick={handleAnalyzeClick}
                        style={{
                            padding: '8px 16px',
                            backgroundColor: '#007bff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '12px',
                            cursor: 'pointer'
                        }}
                    >
                        Analyze Move Quality
                    </button>
                </div>
            </div>
        );
    }

    const quality = moveAnalysis.best_move;
    const config = qualityTierConfig[quality.quality_tier] || qualityTierConfig['='];

    return (
        <div className={`move-quality-display ${className}`} style={{
            padding: '16px',
            backgroundColor: '#f8f9fa',
            borderRadius: '8px',
            border: '1px solid #e9ecef',
            fontSize: '12px'
        }}>
            {/* Header with real data indicator */}
            <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '12px'
            }}>
                <h3 style={{ 
                    margin: 0, 
                    fontSize: '14px', 
                    color: '#333',
                    fontWeight: '600'
                }}>
                    Move Quality Assessment
                </h3>
                {isRealData && (
                    <span style={{
                        fontSize: '10px',
                        backgroundColor: '#28a745',
                        color: 'white',
                        padding: '2px 6px',
                        borderRadius: '4px'
                    }}>
                        Real Data
                    </span>
                )}
            </div>

            {/* Quality Tier Indicator */}
            <QualityTierIndicator quality={quality} config={config} />

            {/* Score Breakdown */}
            <QualityScoreBreakdown quality={quality} />

            {/* Confidence Indicator */}
            <ConfidenceIndicator quality={quality} />

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
            <DetailedAnalysis 
                quality={quality} 
                showDetails={showDetails}
                setShowDetails={setShowDetails}
            />

            {/* Analysis metadata */}
            <div style={{
                fontSize: '10px',
                color: '#999',
                textAlign: 'center',
                padding: '4px',
                borderTop: '1px solid #eee',
                marginTop: '12px'
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

// Export to window for global access (maintaining compatibility)
window.MoveQualityDisplay = MoveQualityDisplay;

console.log('MoveQualityDisplay exported to window:', {
    MoveQualityDisplay: !!window.MoveQualityDisplay,
    componentType: typeof window.MoveQualityDisplay
});

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MoveQualityDisplay;
}
