/**
 * Move Quality Analysis Component - Slice 1 Implementation
 * 
 * Displays move quality assessment results including:
 * - Primary move recommendation with quality tier
 * - Alternative moves ranking
 * - Quality scores and explanations
 * - Risk assessment
 * 
 * Integrates with all existing pattern detection systems.
 */

const { useState, useEffect } = React;

function MoveQualityAnalysis({ gameState, currentPlayer = 0, onMoveRecommendation }) {
    const [moveAnalysis, setMoveAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showAlternatives, setShowAlternatives] = useState(false);
    const [selectedMove, setSelectedMove] = useState(0);

    // Quality tier colors and icons
    const qualityTierDisplay = {
        '!!': { color: '#28a745', icon: '🌟', label: 'Brilliant' },
        '!': { color: '#17a2b8', icon: '💎', label: 'Excellent' },
        '=': { color: '#6c757d', icon: '⚪', label: 'Good' },
        '?!': { color: '#fd7e14', icon: '⚠️', label: 'Dubious' },
        '?': { color: '#dc3545', icon: '❌', label: 'Poor' }
    };

    // Risk level colors
    const riskColors = {
        'low': '#28a745',
        'medium': '#ffc107',
        'high': '#fd7e14',
        'critical': '#dc3545'
    };

    // Auto-analyze when game state changes
    useEffect(() => {
        if (gameState && gameState.fen_string) {
            analyzeMoveQuality();
        }
    }, [gameState?.fen_string, currentPlayer]);

    const analyzeMoveQuality = async () => {
        console.log('MoveQualityAnalysis: analyzeMoveQuality called');
        
        if (!gameState || !gameState.fen_string) {
            console.log('MoveQualityAnalysis: No game state available');
            setError('No game state available');
            return;
        }

        console.log('MoveQualityAnalysis: Analyzing FEN string:', gameState.fen_string);

        // Skip API calls for local position library states or test positions
        if (gameState.fen_string.startsWith('local_') ||
            gameState.fen_string.includes('test_') ||
            gameState.fen_string.startsWith('simple_') ||
            gameState.fen_string.startsWith('complex_') ||
            gameState.fen_string.startsWith('midgame_') ||
            gameState.fen_string.startsWith('endgame_') ||
            gameState.fen_string.startsWith('opening_') ||
            gameState.fen_string.includes('position') ||
            gameState.fen_string.length > 100) { // Base64 encoded strings are typically long
            console.log('MoveQualityAnalysis: Using mock data for position library FEN string (length:', gameState.fen_string.length, ')');
            setMoveAnalysis({
                message: 'Move quality analysis not available for position library states',
                best_move: null,
                alternatives: [],
                quality_tier: '=',
                score: 0
            });
            return;
        }

        setLoading(true);
        setError(null);

        console.log('MoveQualityAnalysis: Making API call for FEN string:', gameState.fen_string);

        try {
            const apiBase = window.API_CONSTANTS?.API_BASE || '/api/v1';
            const response = await fetch(`${apiBase}/analyze-move-quality`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fen_string: gameState.fen_string,
                    current_player: currentPlayer,
                    include_alternatives: true,
                    max_alternatives: 4
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.success) {
                setMoveAnalysis(data);
                
                // Notify parent component
                if (onMoveRecommendation) {
                    onMoveRecommendation(data);
                }
            } else {
                throw new Error(data.error || 'Move analysis failed');
            }

        } catch (err) {
            console.error('Move quality analysis error:', err);
            setError(`Analysis failed: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const MoveRecommendationCard = ({ move, isAlternative = false, index = 0 }) => {
        const tierInfo = qualityTierDisplay[move.quality_tier] || qualityTierDisplay['='];
        
        return React.createElement('div', {
            className: `move-recommendation-card ${isAlternative ? 'alternative' : 'primary'}`,
            style: {
                border: `2px solid ${tierInfo.color}`,
                borderRadius: '8px',
                padding: '12px',
                marginBottom: '8px',
                backgroundColor: isAlternative ? '#f8f9fa' : '#ffffff',
                cursor: isAlternative ? 'pointer' : 'default'
            },
            onClick: isAlternative ? () => setSelectedMove(index) : undefined
        }, [
            // Quality tier badge
            React.createElement('div', {
                key: 'tier-badge',
                style: {
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '8px'
                }
            }, [
                React.createElement('div', {
                    key: 'tier-info',
                    style: { display: 'flex', alignItems: 'center', gap: '8px' }
                }, [
                    React.createElement('span', {
                        key: 'tier-icon',
                        style: { fontSize: '16px' }
                    }, tierInfo.icon),
                    React.createElement('span', {
                        key: 'tier-text',
                        style: { 
                            fontWeight: 'bold', 
                            color: tierInfo.color,
                            fontSize: '14px'
                        }
                    }, `${move.quality_tier} ${tierInfo.label}`),
                ]),
                React.createElement('span', {
                    key: 'score',
                    style: { 
                        fontSize: '12px',
                        color: '#6c757d',
                        fontWeight: '500'
                    }
                }, `${move.quality_score}/100`)
            ]),

            // Move description
            React.createElement('div', {
                key: 'description',
                style: {
                    fontSize: '13px',
                    marginBottom: '8px',
                    color: '#495057'
                }
            }, move.move.description || 'Move description not available'),

            // Primary reason
            React.createElement('div', {
                key: 'reason',
                style: {
                    fontSize: '12px',
                    marginBottom: '8px',
                    color: '#6c757d',
                    fontStyle: 'italic'
                }
            }, move.primary_reason),

            // Component scores (if not alternative or if selected)
            (!isAlternative || selectedMove === index) && React.createElement('div', {
                key: 'components',
                style: {
                    display: 'flex',
                    gap: '12px',
                    fontSize: '11px',
                    color: '#6c757d'
                }
            }, [
                React.createElement('span', {
                    key: 'blocking',
                    title: 'Blocking Score'
                }, `🛡️ ${move.blocking_score.toFixed(1)}`),
                React.createElement('span', {
                    key: 'scoring',
                    title: 'Scoring Score'
                }, `🎯 ${move.scoring_score.toFixed(1)}`),
                React.createElement('span', {
                    key: 'floor',
                    title: 'Floor Line Score'
                }, `🏠 ${move.floor_line_score.toFixed(1)}`),
                React.createElement('span', {
                    key: 'strategic',
                    title: 'Strategic Score'
                }, `♟️ ${move.strategic_score.toFixed(1)}`)
            ])
        ]);
    };

    // Loading state
    if (loading) {
        return React.createElement('div', {
            className: 'move-quality-analysis loading',
            style: { padding: '16px', textAlign: 'center' }
        }, [
            React.createElement('div', {
                key: 'spinner',
                style: { marginBottom: '8px' }
            }, '⏳'),
            React.createElement('div', {
                key: 'text',
                style: { fontSize: '12px', color: '#6c757d' }
            }, 'Analyzing move quality...')
        ]);
    }

    // Error state
    if (error) {
        return React.createElement('div', {
            className: 'move-quality-analysis error',
            style: { 
                padding: '16px', 
                backgroundColor: '#f8d7da',
                color: '#721c24',
                borderRadius: '4px',
                fontSize: '12px'
            }
        }, [
            React.createElement('div', {
                key: 'icon',
                style: { fontWeight: 'bold', marginBottom: '4px' }
            }, '⚠️ Move Analysis Error'),
            React.createElement('div', { key: 'message' }, error),
            React.createElement('button', {
                key: 'retry',
                onClick: analyzeMoveQuality,
                style: {
                    marginTop: '8px',
                    padding: '4px 8px',
                    fontSize: '11px',
                    backgroundColor: '#721c24',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                }
            }, 'Retry')
        ]);
    }

    // Show message if present (e.g., for local_ FEN)
    if (moveAnalysis && moveAnalysis.message) {
        return React.createElement('div', { className: 'move-quality-analysis info' }, moveAnalysis.message);
    }

    // Only render MoveRecommendationCard if best_move is valid
    if (moveAnalysis && moveAnalysis.best_move) {
        return React.createElement('div', { className: 'move-quality-analysis' }, [
            React.createElement(MoveRecommendationCard, { move: moveAnalysis.best_move, isAlternative: false, key: 'best' }),
            ...(moveAnalysis.alternatives || []).map((alt, idx) =>
                React.createElement(MoveRecommendationCard, { move: alt, isAlternative: true, index: idx, key: `alt-${idx}` })
            )
        ]);
    }

    // Fallback: nothing to show
    return null;
}

// Export for use in other components
if (typeof window !== 'undefined') {
    window.MoveQualityAnalysis = MoveQualityAnalysis;
}