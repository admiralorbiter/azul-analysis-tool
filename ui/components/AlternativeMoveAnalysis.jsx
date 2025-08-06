/**
 * Alternative Move Analysis Component - Slice 3 Phase 2
 * 
 * Enhanced UI component for comparing alternative moves side-by-side.
 * Features:
 * - Side-by-side move comparison
 * - Move quality ranking
 * - Detailed move analysis
 * - Interactive move selection
 * - Real data detection and enhanced analysis
 * 
 * Version: 1.0.0 - Initial implementation
 */

const { useState, useEffect } = React;

const AlternativeMoveAnalysis = ({ 
    gameState, 
    currentPlayer = 0, 
    onMoveSelection,
    className = '' 
}) => {
    const [moveAnalysis, setMoveAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedMoveIndex, setSelectedMoveIndex] = useState(0);
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
            analyzeAlternativeMoves();
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

    const analyzeAlternativeMoves = async () => {
        console.log('AlternativeMoveAnalysis: analyzeAlternativeMoves called');
        
        if (!gameState || !gameState.fen_string) {
            console.log('AlternativeMoveAnalysis: No game state available');
            setError('No game state available');
            return;
        }

        console.log('AlternativeMoveAnalysis: Analyzing FEN string:', gameState.fen_string);

        // Detect if this is real game data
        const realData = isRealGameData(gameState.fen_string);
        setIsRealData(realData);
        console.log('AlternativeMoveAnalysis: Is real game data:', realData);

        // Prepare FEN string for API call
        let apiFenString = gameState.fen_string;
        
        // If it's a long base64 string without prefix, add the prefix
        if (realData && gameState.fen_string.length > 100 && !gameState.fen_string.startsWith('base64_')) {
            // Check if it looks like base64 (contains only base64 characters)
            const base64Pattern = /^[A-Za-z0-9+/=]+$/;
            if (base64Pattern.test(gameState.fen_string)) {
                apiFenString = 'base64_' + gameState.fen_string;
                console.log('AlternativeMoveAnalysis: Added base64_ prefix to FEN string');
            }
        }

        // Generate educational mock data for position library states
        if (gameState.fen_string.startsWith('local_')) {
            console.log('AlternativeMoveAnalysis: Generating educational mock data for position library state');
            
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
            
            // Generate realistic alternative moves
            const generateEducationalAlternatives = (gameState, currentPlayer) => {
                const alternatives = [];
                const factories = gameState.factories || [];
                const colors = ['B', 'W', 'Y', 'R', 'K'];
                
                // Generate educational alternatives
                factories.forEach((factory, factoryIndex) => {
                    if (factory && factory.length > 0) {
                        const color = factory[0];
                        [1, 2, 3, 4, 5].forEach(line => {
                            alternatives.push({
                                quality_tier: ['!', '=', '?!'][alternatives.length % 3],
                                quality_score: 75 - (alternatives.length * 5),
                                blocking_score: 80 - (alternatives.length * 8),
                                strategic_score: 70 - (alternatives.length * 6),
                                floor_line_score: 65 - (alternatives.length * 7),
                                scoring_score: 80 - (alternatives.length * 9),
                                confidence_score: 0.8 - (alternatives.length * 0.1),
                                primary_reason: `Educational alternative ${alternatives.length + 1}: ${color} tile to pattern line ${line}`,
                                move_description: `Take ${color} tile from factory ${factoryIndex + 1} to pattern line ${line}`,
                                risk_level: alternatives.length < 2 ? 'low' : alternatives.length < 4 ? 'medium' : 'high'
                            });
                        });
                    }
                });
                
                return alternatives.slice(0, 5);
            };
            
            const positionComplexity = analyzePositionComplexity(gameState);
            const educationalAlternatives = generateEducationalAlternatives(gameState, currentPlayer);
            
            const educationalMockData = {
                success: true,
                alternatives: educationalAlternatives,
                analysis_complete: true,
                is_real_data: false,
                data_quality: 'educational_mock',
                educational_enabled: true,
                position_complexity: positionComplexity,
                total_moves_analyzed: educationalAlternatives.length,
                analysis_summary: `Educational alternative analysis for ${positionComplexity.level} complexity position`
            };
            
            setMoveAnalysis(educationalMockData);
            setIsRealData(false);
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);

        console.log('AlternativeMoveAnalysis: Making API call for alternative moves');

        try {
            const apiBase = window.API_CONSTANTS?.API_BASE || '/api/v1';
            const response = await fetch(`${apiBase}/evaluate-all-moves`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fen_string: apiFenString,
                    player_id: currentPlayer
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            console.log('AlternativeMoveAnalysis: API response received:', data);

            if (data.success) {
                // Update real data status from API response
                setIsRealData(data.is_real_data || false);
                
                // Convert all_moves_quality to alternatives format
                const alternatives = Object.entries(data.all_moves_quality || {})
                    .map(([move_key, move_data]) => ({
                        move_key,
                        quality_tier: move_data.quality_tier,
                        quality_score: move_data.overall_score,
                        blocking_score: move_data.strategic_value, // Approximate
                        strategic_score: move_data.strategic_value,
                        floor_line_score: move_data.risk_assessment, // Approximate
                        scoring_score: move_data.tactical_value, // Approximate
                        confidence_score: move_data.confidence_score,
                        primary_reason: move_data.explanation,
                        move_description: move_key
                    }))
                    .sort((a, b) => b.quality_score - a.quality_score)
                    .slice(0, 5); // Top 5 moves
                
                setMoveAnalysis({
                    success: true,
                    alternatives: alternatives,
                    analysis_complete: true,
                    is_real_data: data.is_real_data || false,
                    data_quality: data.data_quality || 'mock',
                    analysis_enhanced: data.analysis_enhanced || null,
                    total_moves_analyzed: data.total_moves_analyzed || 0,
                    analysis_time_ms: data.analysis_time_ms || 0
                });
                
                if (onMoveSelection && alternatives.length > 0) {
                    onMoveSelection(alternatives[0]);
                }
            } else {
                setError(data.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('AlternativeMoveAnalysis: API call failed:', error);
            setError(`Analysis failed: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleMoveSelection = (moveIndex) => {
        setSelectedMoveIndex(moveIndex);
        if (onMoveSelection && moveAnalysis && moveAnalysis.alternatives) {
            onMoveSelection(moveAnalysis.alternatives[moveIndex]);
        }
    };

    // Loading state
    if (loading) {
        return (
            <div className={`alternative-move-analysis loading ${className}`}>
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
                        Analyzing alternative moves...
                    </div>
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className={`alternative-move-analysis error ${className}`}>
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
                        ⚠️ Alternative Move Analysis Error
                    </div>
                    <div style={{ marginBottom: '8px' }}>{error}</div>
                    <button
                        onClick={analyzeAlternativeMoves}
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

    // Empty state
    if (!moveAnalysis || !moveAnalysis.success || !moveAnalysis.alternatives || moveAnalysis.alternatives.length === 0) {
        return (
            <div className={`alternative-move-analysis empty ${className}`}>
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
                        🔄
                    </div>
                    <div>Alternative move analysis will appear here</div>
                </div>
            </div>
        );
    }

    const alternatives = moveAnalysis.alternatives;
    const selectedMove = alternatives[selectedMoveIndex];

    return (
        <div className={`alternative-move-analysis ${className}`}>
            {/* Header with real data indicator */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '12px',
                padding: '8px 12px',
                backgroundColor: '#f8f9fa',
                border: '1px solid #e0e0e0',
                borderRadius: '6px'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '16px' }}>🔄</span>
                    <div>
                        <div style={{ 
                            fontWeight: 'bold', 
                            fontSize: '14px',
                            color: '#333'
                        }}>
                            Alternative Moves
                        </div>
                        <div style={{ 
                            fontSize: '12px', 
                            color: '#666' 
                        }}>
                            {alternatives.length} moves analyzed
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

            {/* Move selection tabs */}
            <div style={{
                display: 'flex',
                gap: '4px',
                marginBottom: '12px',
                overflowX: 'auto'
            }}>
                {alternatives.map((move, index) => {
                    const config = qualityTierConfig[move.quality_tier] || qualityTierConfig['='];
                    const isSelected = index === selectedMoveIndex;
                    
                    return (
                        <button
                            key={index}
                            onClick={() => handleMoveSelection(index)}
                            style={{
                                flex: '0 0 auto',
                                padding: '6px 8px',
                                backgroundColor: isSelected ? config.bgColor : 'transparent',
                                border: `1px solid ${isSelected ? config.borderColor : '#ddd'}`,
                                borderRadius: '4px',
                                fontSize: '10px',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px',
                                minWidth: '60px',
                                justifyContent: 'center'
                            }}
                        >
                            <span>{config.icon}</span>
                            <span style={{ 
                                color: isSelected ? config.color : '#666',
                                fontWeight: isSelected ? 'bold' : 'normal'
                            }}>
                                {index + 1}
                            </span>
                        </button>
                    );
                })}
            </div>

            {/* Selected move details */}
            {selectedMove && (
                <div style={{
                    padding: '12px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '6px',
                    border: '1px solid #e0e0e0'
                }}>
                    {/* Move header */}
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '8px'
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span style={{ fontSize: '14px' }}>
                                {qualityTierConfig[selectedMove.quality_tier]?.icon || '⚪'}
                            </span>
                            <span style={{ 
                                fontSize: '12px', 
                                fontWeight: 'bold',
                                color: qualityTierConfig[selectedMove.quality_tier]?.color || '#666'
                            }}>
                                {qualityTierConfig[selectedMove.quality_tier]?.label || 'Move'} #{selectedMoveIndex + 1}
                            </span>
                        </div>
                        <span style={{ 
                            fontSize: '12px', 
                            fontWeight: 'bold',
                            color: '#666'
                        }}>
                            {selectedMove.quality_score?.toFixed(1) || 'N/A'}/100
                        </span>
                    </div>

                    {/* Move description */}
                    <div style={{
                        marginBottom: '8px',
                        fontSize: '11px',
                        color: '#555',
                        lineHeight: '1.3'
                    }}>
                        <strong>Move:</strong> {selectedMove.move_description}
                    </div>

                    {/* Score breakdown */}
                    <div style={{ marginBottom: '8px' }}>
                        <div style={{ 
                            fontSize: '10px', 
                            fontWeight: 'bold', 
                            marginBottom: '4px',
                            color: '#333'
                        }}>
                            Score Breakdown
                        </div>
                        <div style={{ display: 'grid', gap: '3px' }}>
                            {[
                                { key: 'blocking_score', label: 'Blocking', icon: '🛡️', color: '#4CAF50' },
                                { key: 'scoring_score', label: 'Scoring', icon: '🎯', color: '#2196F3' },
                                { key: 'strategic_score', label: 'Strategic', icon: '♟️', color: '#FF9800' },
                                { key: 'floor_line_score', label: 'Floor', icon: '🏠', color: '#9C27B0' }
                            ].map(({ key, label, icon, color }) => (
                                <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <span style={{ fontSize: '10px' }}>{icon}</span>
                                    <span style={{ 
                                        fontSize: '9px', 
                                        minWidth: '40px',
                                        color: '#666'
                                    }}>
                                        {label}
                                    </span>
                                    <div style={{ 
                                        flex: 1, 
                                        height: '6px', 
                                        backgroundColor: '#e0e0e0',
                                        borderRadius: '3px',
                                        overflow: 'hidden'
                                    }}>
                                        <div style={{
                                            height: '100%',
                                            width: `${(selectedMove[key] || 0)}%`,
                                            backgroundColor: color,
                                            transition: 'width 0.3s ease'
                                        }} />
                                    </div>
                                    <span style={{ 
                                        fontSize: '9px', 
                                        color: '#666',
                                        minWidth: '20px',
                                        textAlign: 'right'
                                    }}>
                                        {(selectedMove[key] || 0).toFixed(0)}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Analysis */}
                    <div style={{
                        fontSize: '10px',
                        color: '#555',
                        lineHeight: '1.3',
                        fontStyle: 'italic'
                    }}>
                        {selectedMove.primary_reason || 'No detailed analysis available.'}
                    </div>
                </div>
            )}

            {/* Analysis metadata */}
            <div style={{
                fontSize: '10px',
                color: '#999',
                textAlign: 'center',
                padding: '4px',
                borderTop: '1px solid #eee',
                marginTop: '8px'
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