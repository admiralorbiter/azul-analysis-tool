// AdvancedAnalysisControls Component
// Extracted from main.js for Phase 3 refactoring

const AdvancedAnalysisControls = ({ 
    loading, setLoading, analyzePosition, getHint, analyzeNeural, 
    gameState, setVariations, setHeatmapData, setStatusMessage, 
    moveHistory, analyzeGame, depth, setDepth, timeBudget, 
    setTimeBudget, rollouts, setRollouts, agentId, setAgentId 
}) => {

    const handleAnalyze = React.useCallback(() => {
        setLoading(true);
        analyzePosition(gameState.fen_string || 'initial', depth, timeBudget, agentId)
            .then(data => {
                if (data.success && data.analysis) {
                    setVariations([{
                        move: data.analysis.best_move,
                        score: data.analysis.best_score,
                        visits: data.analysis.nodes_searched
                    }]);
                    const heatmap = window.generateHeatmapData({ variations: [{
                        move: data.analysis.best_move,
                        score: data.analysis.best_score,
                        move_data: { source_id: 0, tile_type: 0 }
                    }] });
                    setHeatmapData(heatmap);
                    setStatusMessage(`Analysis complete: ${data.analysis.best_move} (${data.analysis.best_score.toFixed(2)})`);
                } else {
                    setStatusMessage('Analysis failed: Invalid response');
                }
            })
            .catch(error => {
                setStatusMessage(`Analysis failed: ${error.message}`);
            })
            .finally(() => setLoading(false));
    }, [loading, setLoading, analyzePosition, gameState, depth, timeBudget, rollouts, agentId, setVariations, setHeatmapData, setStatusMessage]);

    const handleQuickHint = React.useCallback(() => {
        setLoading(true);
        getHint(gameState.fen_string || 'initial', timeBudget, rollouts, agentId)
            .then(data => {
                if (data.success && data.hint) {
                    setStatusMessage(`Hint: ${data.hint.best_move} (EV: ${data.hint.expected_value.toFixed(2)})`);
                } else {
                    setStatusMessage('Hint failed: Invalid response');
                }
            })
            .catch(error => {
                setStatusMessage(`Hint failed: ${error.message}`);
            })
            .finally(() => setLoading(false));
    }, [loading, setLoading, getHint, gameState, timeBudget, rollouts, agentId, setStatusMessage]);

    const handleNeuralAnalysis = React.useCallback(() => {
        setLoading(true);
        analyzeNeural(gameState.fen_string || 'initial', 2.0, 100, agentId)
            .then(data => {
                if (data.success && data.analysis) {
                    setStatusMessage(`Neural: ${data.analysis.best_move} (${data.analysis.best_score.toFixed(2)})`);
                } else {
                    setStatusMessage('Neural analysis failed: Invalid response');
                }
            })
            .catch(error => {
                setStatusMessage(`Neural analysis failed: ${error.message}`);
            })
            .finally(() => setLoading(false));
    }, [loading, setLoading, analyzeNeural, gameState, agentId, setStatusMessage]);

    return React.createElement('div', {
        className: 'space-y-3'
    },
        React.createElement('div', {
            className: 'flex items-center space-x-2'
        },
            React.createElement('button', {
                className: `btn-primary btn-sm flex-1 ${loading ? 'opacity-50' : ''}`,
                onClick: handleAnalyze,
                disabled: loading
            }, loading ? '🤖 Analyzing...' : '🔍 Engine Analysis'),
            React.createElement('button', {
                className: `btn-info btn-sm flex-1 ${loading ? 'opacity-50' : ''}`,
                onClick: handleQuickHint,
                disabled: loading
            }, loading ? '💡 Thinking...' : '💡 Quick Hint')
        ),
        React.createElement('div', {
            className: 'flex items-center space-x-2'
        },
            React.createElement('button', {
                className: `btn-accent btn-sm flex-1 ${loading ? 'opacity-50' : ''}`,
                onClick: handleNeuralAnalysis,
                disabled: loading
            }, loading ? '🧠 Processing...' : '🧠 Neural Net'),
            React.createElement('button', {
                className: `btn-sm flex-1 ${loading ? 'btn-secondary opacity-50' : 'btn-outline'}`,
                onClick: () => {
                    setLoading(true);
                    const gameData = {
                        moves: moveHistory.map((move, index) => ({
                            move: move,
                            player: index % 2,
                            position_before: 'initial'
                        })),
                        players: ['Player 1', 'Player 2'],
                        result: { winner: null, score: [0, 0] }
                    };
                    
                    analyzeGame(gameData, 3)
                        .then(data => {
                            if (data.success) {
                                const blunderCount = data.summary.blunder_count;
                                setStatusMessage(`Game analysis complete: ${blunderCount} blunders found`);
                            } else {
                                setStatusMessage('Game analysis failed');
                            }
                        })
                        .catch(error => {
                            setStatusMessage(`Game analysis failed: ${error.message}`);
                        })
                        .finally(() => setLoading(false));
                },
                disabled: loading || moveHistory.length === 0
            }, loading ? '📊 Analyzing Game...' : '📊 Analyze Full Game')
        )
    );
};

// Make component globally available
window.AdvancedAnalysisControls = AdvancedAnalysisControls; 