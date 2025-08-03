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
        if (!gameState || !gameState.fen_string) {
            setError('No game state available');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await fetch('/api/v1/analyze-move-quality', {
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

    // No analysis yet
    if (!moveAnalysis) {
        return React.createElement('div', {
            className: 'move-quality-analysis empty',
            style: { 
                padding: '16px', 
                textAlign: 'center',
                color: '#6c757d',
                fontSize: '12px'
            }
        }, 'Move quality analysis will appear when a position is loaded');
    }

    return React.createElement('div', {
        className: 'move-quality-analysis'
    }, [
        // Header
        React.createElement('div', {
            key: 'header',
            style: {
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '12px'
            }
        }, [
            React.createElement('h4', {
                key: 'title',
                style: { 
                    margin: 0, 
                    fontSize: '14px', 
                    fontWeight: '600',
                    color: '#495057'
                }
            }, '🎯 Move Quality Analysis'),
            React.createElement('span', {
                key: 'stats',
                style: { 
                    fontSize: '11px', 
                    color: '#6c757d'
                }
            }, `${moveAnalysis.total_moves_analyzed} moves analyzed`)
        ]),

        // Primary recommendation
        React.createElement('div', {
            key: 'primary',
            style: { marginBottom: '16px' }
        }, [
            React.createElement('div', {
                key: 'primary-label',
                style: {
                    fontSize: '12px',
                    fontWeight: '600',
                    color: '#495057',
                    marginBottom: '8px'
                }
            }, 'Recommended Move:'),
            React.createElement(MoveRecommendationCard, {
                key: 'primary-card',
                move: moveAnalysis.primary_recommendation,
                isAlternative: false
            })
        ]),

        // Alternatives toggle
        moveAnalysis.alternatives && moveAnalysis.alternatives.length > 0 && React.createElement('div', {
            key: 'alternatives-section'
        }, [
            React.createElement('button', {
                key: 'toggle',
                onClick: () => setShowAlternatives(!showAlternatives),
                style: {
                    width: '100%',
                    padding: '8px',
                    fontSize: '12px',
                    backgroundColor: '#f8f9fa',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    marginBottom: showAlternatives ? '12px' : '0'
                }
            }, `${showAlternatives ? '▼' : '▶'} Show ${moveAnalysis.alternatives.length} Alternative${moveAnalysis.alternatives.length !== 1 ? 's' : ''}`),

            // Alternatives list
            showAlternatives && React.createElement('div', {
                key: 'alternatives-list',
                style: { maxHeight: '300px', overflowY: 'auto' }
            }, moveAnalysis.alternatives.map((alt, index) => 
                React.createElement(MoveRecommendationCard, {
                    key: `alt-${index}`,
                    move: alt,
                    isAlternative: true,
                    index: index
                })
            ))
        ]),

        // Analysis summary
        React.createElement('div', {
            key: 'summary',
            style: {
                marginTop: '12px',
                padding: '8px',
                backgroundColor: '#f8f9fa',
                borderRadius: '4px',
                fontSize: '11px',
                color: '#6c757d'
            }
        }, [
            React.createElement('div', {
                key: 'summary-text',
                style: { marginBottom: '4px' }
            }, moveAnalysis.analysis_summary),
            moveAnalysis.analysis_time_ms && React.createElement('div', {
                key: 'timing',
                style: { fontSize: '10px', color: '#adb5bd' }
            }, `Analysis completed in ${moveAnalysis.analysis_time_ms}ms`)
        ])
    ]);
}

// Export for use in other components
if (typeof window !== 'undefined') {
    window.MoveQualityAnalysis = MoveQualityAnalysis;
}