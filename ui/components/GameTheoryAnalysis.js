// GameTheoryAnalysis.js - Enhanced Game Theory Analysis UI Component
const { useState, useEffect } = React;

const GameTheoryAnalysis = ({ gameState, onAnalysisComplete, onAnalysisStart, onAnalysisEnd }) => {
    const [analysisType, setAnalysisType] = useState('nash_equilibrium');
    const [isLoading, setIsLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [playerId, setPlayerId] = useState(0);
    const [opponentId, setOpponentId] = useState(1);
    const [predictionDepth, setPredictionDepth] = useState(3);
    const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
    const [analysisHistory, setAnalysisHistory] = useState([]);

    const analysisTypes = [
        { value: 'nash_equilibrium', label: '🎯 Nash Equilibrium Detection', description: 'Detect Nash equilibrium in current position', color: '#e74c3c' },
        { value: 'opponent_modeling', label: '🧠 Opponent Modeling', description: 'Model opponent behavior and strategy', color: '#3498db' },
        { value: 'strategic_analysis', label: '📊 Strategic Analysis', description: 'Comprehensive strategic position analysis', color: '#2ecc71' },
        { value: 'move_prediction', label: '🔮 Move Prediction', description: 'Predict opponent\'s likely moves', color: '#9b59b6' },
        { value: 'strategic_value', label: '💰 Strategic Value', description: 'Calculate strategic value of position', color: '#f39c12' }
    ];

    const performAnalysis = async () => {
        if (!gameState) {
            setError('No game state available for analysis');
            return;
        }

        setIsLoading(true);
        setError(null);
        
        // Notify parent component that analysis is starting
        if (onAnalysisStart) {
            onAnalysisStart();
        }

        try {
            let endpoint = '';
            let requestData = {
                game_state: gameState,
                player_id: playerId
            };

            switch (analysisType) {
                case 'nash_equilibrium':
                    endpoint = '/api/v1/game-theory/detect-nash-equilibrium';
                    break;
                case 'opponent_modeling':
                    endpoint = '/api/v1/game-theory/model-opponent';
                    requestData.opponent_id = opponentId;
                    break;
                case 'strategic_analysis':
                    endpoint = '/api/v1/game-theory/analyze-strategy';
                    break;
                case 'move_prediction':
                    endpoint = '/api/v1/game-theory/predict-opponent-moves';
                    requestData.opponent_id = opponentId;
                    requestData.depth = predictionDepth;
                    break;
                case 'strategic_value':
                    endpoint = '/api/v1/game-theory/calculate-strategic-value';
                    break;
                default:
                    throw new Error('Invalid analysis type');
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.success) {
                const analysisWithType = { ...data, analysis_type: analysisType };
                setResults(analysisWithType);
                setAnalysisHistory(prev => [analysisWithType, ...prev.slice(0, 4)]);
                if (onAnalysisComplete) {
                    onAnalysisComplete(analysisWithType);
                }
            } else {
                throw new Error(data.error || 'Analysis failed');
            }

        } catch (err) {
            setError(err.message);
            console.error('Game theory analysis error:', err);
        } finally {
            setIsLoading(false);
            // Notify parent component that analysis has ended
            if (onAnalysisEnd) {
                onAnalysisEnd();
            }
        }
    };

    const renderConfidenceChart = (confidence) => {
        const percentage = Math.round(confidence);
        const color = confidence >= 80 ? '#2ecc71' : confidence >= 60 ? '#f39c12' : '#e74c3c';
        
        return React.createElement('div', { className: 'confidence-chart' },
            React.createElement('div', { className: 'chart-container' },
                React.createElement('div', { 
                    className: 'chart-circle',
                    style: {
                        background: `conic-gradient(${color} ${percentage * 3.6}deg, rgba(255,255,255,0.1) 0deg)`
                    }
                }),
                React.createElement('div', { className: 'chart-label' },
                    React.createElement('span', { className: 'chart-value' }, `${percentage}%`),
                    React.createElement('span', { className: 'chart-text' }, 'Confidence')
                )
            )
        );
    };

    const renderMetricBar = (label, value, maxValue = 100, color = '#3498db') => {
        const percentage = (value / maxValue) * 100;
        
        return React.createElement('div', { className: 'metric-bar-container' },
            React.createElement('div', { className: 'metric-label' }, label),
            React.createElement('div', { className: 'metric-bar' },
                React.createElement('div', { 
                    className: 'metric-fill',
                    style: { width: `${percentage}%`, backgroundColor: color }
                })
            ),
            React.createElement('div', { className: 'metric-value' }, value)
        );
    };

    const renderNashEquilibriumResults = () => {
        if (!results) return null;

        return React.createElement('div', { className: 'analysis-results enhanced-results' },
            React.createElement('h3', { className: 'results-title' }, '🎯 Nash Equilibrium Analysis'),
            React.createElement('div', { className: 'results-grid' },
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Equilibrium Type:'),
                    React.createElement('span', { 
                        className: `equilibrium-type ${results.equilibrium_type}` 
                    }, results.equilibrium_type.replace('_', ' ').toUpperCase())
                ),
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Confidence:'),
                    renderConfidenceChart(results.confidence || 0)
                ),
                results.strategies && React.createElement('div', { className: 'result-item full-width' },
                    React.createElement('label', { className: 'result-label' }, 'Optimal Strategies:'),
                    React.createElement('div', { className: 'strategies-list' },
                        results.strategies.map((strategy, index) => 
                            React.createElement('div', { 
                                key: index, 
                                className: 'strategy-item' 
                            },
                                React.createElement('span', { className: 'strategy-name' }, strategy.name),
                                React.createElement('span', { className: 'strategy-probability' }, `${(strategy.probability * 100).toFixed(1)}%`)
                            )
                        )
                    )
                ),
                results.insights && React.createElement('div', { className: 'result-item full-width' },
                    React.createElement('label', { className: 'result-label' }, 'Strategic Insights:'),
                    React.createElement('ul', { className: 'insights-list' },
                        results.insights.map((insight, index) => 
                            React.createElement('li', { key: index }, insight)
                        )
                    )
                )
            )
        );
    };

    const renderOpponentModelingResults = () => {
        if (!results) return null;

        return React.createElement('div', { className: 'analysis-results enhanced-results' },
            React.createElement('h3', { className: 'results-title' }, '🧠 Opponent Modeling Analysis'),
            React.createElement('div', { className: 'results-grid' },
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Risk Tolerance:'),
                    renderMetricBar('Risk Tolerance', results.risk_tolerance || 0, 100, '#e74c3c')
                ),
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Aggression Level:'),
                    renderMetricBar('Aggression', results.aggression_level || 0, 100, '#f39c12')
                ),
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Strategic Tendency:'),
                    React.createElement('span', { className: 'strategic-tendency' }, results.strategic_tendency || 'Balanced')
                ),
                results.predicted_moves && React.createElement('div', { className: 'result-item full-width' },
                    React.createElement('label', { className: 'result-label' }, 'Predicted Behavior:'),
                    React.createElement('div', { className: 'predicted-behavior' },
                        results.predicted_moves.map((move, index) => 
                            React.createElement('div', { 
                                key: index, 
                                className: 'behavior-item' 
                            },
                                React.createElement('span', { className: 'behavior-type' }, move.type),
                                React.createElement('span', { className: 'behavior-confidence' }, `${(move.confidence * 100).toFixed(1)}%`)
                            )
                        )
                    )
                )
            )
        );
    };

    const renderStrategicAnalysisResults = () => {
        if (!results) return null;

        return React.createElement('div', { className: 'analysis-results enhanced-results' },
            React.createElement('h3', { className: 'results-title' }, '📊 Strategic Analysis'),
            React.createElement('div', { className: 'results-grid' },
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Strategic Value:'),
                    React.createElement('span', { className: 'strategic-value' }, results.strategic_value || 0)
                ),
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Game Phase:'),
                    React.createElement('span', { 
                        className: `game-phase ${results.game_phase}` 
                    }, results.game_phase?.replace('_', ' ').toUpperCase() || 'Unknown')
                ),
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Position Strength:'),
                    renderMetricBar('Strength', results.position_strength || 0, 100, '#2ecc71')
                ),
                results.recommendations && React.createElement('div', { className: 'result-item full-width' },
                    React.createElement('label', { className: 'result-label' }, 'Strategic Recommendations:'),
                    React.createElement('ul', { className: 'recommendations-list' },
                        results.recommendations.map((rec, index) => 
                            React.createElement('li', { key: index }, rec)
                        )
                    )
                )
            )
        );
    };

    const renderMovePredictionResults = () => {
        if (!results) return null;

        return React.createElement('div', { className: 'analysis-results enhanced-results' },
            React.createElement('h3', { className: 'results-title' }, '🔮 Move Prediction Analysis'),
            React.createElement('div', { className: 'results-grid' },
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Prediction Depth:'),
                    React.createElement('span', { className: 'prediction-depth' }, results.prediction_depth || predictionDepth)
                ),
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Overall Confidence:'),
                    renderConfidenceChart(results.confidence || 0)
                ),
                results.predicted_moves && React.createElement('div', { className: 'result-item full-width' },
                    React.createElement('label', { className: 'result-label' }, 'Predicted Move Sequence:'),
                    React.createElement('div', { className: 'predicted-moves' },
                        results.predicted_moves.map((move, index) => 
                            React.createElement('div', { 
                                key: index, 
                                className: 'predicted-move' 
                            },
                                React.createElement('span', { className: 'move-turn' }, `Turn ${index + 1}`),
                                React.createElement('span', { className: 'move-strategy' }, move.strategy),
                                React.createElement('span', { className: 'move-confidence' }, `${(move.confidence * 100).toFixed(1)}%`)
                            )
                        )
                    )
                )
            )
        );
    };

    const renderStrategicValueResults = () => {
        if (!results) return null;

        return React.createElement('div', { className: 'analysis-results enhanced-results' },
            React.createElement('h3', { className: 'results-title' }, '💰 Strategic Value Analysis'),
            React.createElement('div', { className: 'results-grid' },
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Strategic Value:'),
                    React.createElement('span', { className: 'strategic-value' }, results.strategic_value || 0)
                ),
                React.createElement('div', { className: 'result-item enhanced-item' },
                    React.createElement('label', { className: 'result-label' }, 'Confidence:'),
                    renderConfidenceChart(results.confidence || 0)
                ),
                results.value_components && React.createElement('div', { className: 'result-item full-width' },
                    React.createElement('label', { className: 'result-label' }, 'Value Components:'),
                    React.createElement('div', { className: 'value-components' },
                        results.value_components.map((component, index) => 
                            React.createElement('div', { 
                                key: index, 
                                className: 'component-item' 
                            },
                                React.createElement('span', { className: 'component-name' }, component.name),
                                React.createElement('span', { className: 'component-value' }, component.value)
                            )
                        )
                    )
                ),
                results.reasoning && React.createElement('div', { className: 'result-item full-width' },
                    React.createElement('label', { className: 'result-label' }, 'Strategic Reasoning:'),
                    React.createElement('p', { className: 'reasoning' }, results.reasoning)
                )
            )
        );
    };

    const renderResults = () => {
        if (!results) return null;

        switch (analysisType) {
            case 'nash_equilibrium':
                return renderNashEquilibriumResults();
            case 'opponent_modeling':
                return renderOpponentModelingResults();
            case 'strategic_analysis':
                return renderStrategicAnalysisResults();
            case 'move_prediction':
                return renderMovePredictionResults();
            case 'strategic_value':
                return renderStrategicValueResults();
            default:
                return null;
        }
    };

    const renderAnalysisHistory = () => {
        if (analysisHistory.length === 0) return null;

        return React.createElement('div', { className: 'analysis-history' },
            React.createElement('h4', { className: 'history-title' }, '📊 Recent Analyses'),
            React.createElement('div', { className: 'history-list' },
                analysisHistory.map((analysis, index) => 
                    React.createElement('div', { 
                        key: index, 
                        className: 'history-item' 
                    },
                        React.createElement('span', { className: 'history-type' }, 
                            analysisTypes.find(t => t.value === analysis.analysis_type)?.label || analysis.analysis_type
                        ),
                        React.createElement('span', { className: 'history-status' }, 
                            analysis.success ? '✅' : '❌'
                        )
                    )
                )
            )
        );
    };

    return React.createElement('div', { className: 'game-theory-analysis enhanced' },
        React.createElement('div', { className: 'analysis-header enhanced-header' },
            React.createElement('h2', { className: 'analysis-title' }, '🎯 Game Theory Analysis'),
            React.createElement('p', { className: 'analysis-subtitle' }, 'Advanced strategic analysis using game theory concepts')
        ),

        React.createElement('div', { className: 'analysis-controls enhanced-controls' },
            React.createElement('div', { className: 'control-group primary-controls' },
                React.createElement('label', { className: 'control-label' }, 'Analysis Type:'),
                React.createElement('select', { 
                    value: analysisType, 
                    onChange: (e) => setAnalysisType(e.target.value),
                    className: 'analysis-type-select enhanced-select'
                },
                    analysisTypes.map(type => 
                        React.createElement('option', { key: type.value, value: type.value }, type.label)
                    )
                ),
                React.createElement('div', { className: 'analysis-description enhanced-description' },
                    analysisTypes.find(t => t.value === analysisType)?.description
                )
            ),

            React.createElement('div', { className: 'control-group secondary-controls' },
                React.createElement('div', { className: 'player-controls' },
                    React.createElement('label', { className: 'control-label' }, 'Player ID:'),
                    React.createElement('input', { 
                        type: 'number', 
                        value: playerId, 
                        onChange: (e) => setPlayerId(parseInt(e.target.value)),
                        min: '0',
                        max: '3',
                        className: 'player-input enhanced-input'
                    })
                ),

                {(analysisType === 'opponent_modeling' || analysisType === 'move_prediction') && 
                    React.createElement('div', { className: 'opponent-controls' },
                        React.createElement('label', { className: 'control-label' }, 'Opponent ID:'),
                        React.createElement('input', { 
                            type: 'number', 
                            value: opponentId, 
                            onChange: (e) => setOpponentId(parseInt(e.target.value)),
                            min: '0',
                            max: '3',
                            className: 'opponent-input enhanced-input'
                        })
                    )
                },

                {analysisType === 'move_prediction' && 
                    React.createElement('div', { className: 'depth-controls' },
                        React.createElement('label', { className: 'control-label' }, 'Prediction Depth:'),
                        React.createElement('input', { 
                            type: 'number', 
                            value: predictionDepth, 
                            onChange: (e) => setPredictionDepth(parseInt(e.target.value)),
                            min: '1',
                            max: '5',
                            className: 'depth-input enhanced-input'
                        })
                    )
                }
            ),

            React.createElement('div', { className: 'control-group action-controls' },
                React.createElement('button', { 
                    onClick: () => setShowAdvancedOptions(!showAdvancedOptions),
                    className: 'advanced-toggle-btn'
                }, showAdvancedOptions ? '🔽 Hide Advanced' : '🔼 Show Advanced'),
                
                React.createElement('button', { 
                    onClick: performAnalysis,
                    disabled: isLoading || !gameState,
                    className: 'analyze-button enhanced-button'
                }, isLoading ? '🔄 Analyzing...' : '🎯 Analyze Position')
            )
        ),

        {showAdvancedOptions && React.createElement('div', { className: 'advanced-options' },
            React.createElement('h4', { className: 'advanced-title' }, 'Advanced Options'),
            React.createElement('div', { className: 'advanced-grid' },
                React.createElement('div', { className: 'advanced-item' },
                    React.createElement('label', { className: 'advanced-label' }, 'Analysis Depth:'),
                    React.createElement('select', { className: 'advanced-select' },
                        React.createElement('option', { value: 'basic' }, 'Basic'),
                        React.createElement('option', { value: 'standard' }, 'Standard'),
                        React.createElement('option', { value: 'advanced' }, 'Advanced'),
                        React.createElement('option', { value: 'expert' }, 'Expert')
                    )
                ),
                React.createElement('div', { className: 'advanced-item' },
                    React.createElement('label', { className: 'advanced-label' }, 'Include Historical Data:'),
                    React.createElement('input', { type: 'checkbox', defaultChecked: true, className: 'advanced-checkbox' })
                )
            )
        )},

        {error && React.createElement('div', { className: 'error-message enhanced-error' },
            React.createElement('span', { className: 'error-icon' }, '❌'),
            React.createElement('span', { className: 'error-text' }, `Error: ${error}`)
        )},

        renderAnalysisHistory(),
        renderResults()
    );
};

// Export to window for global access
window.GameTheoryAnalysis = GameTheoryAnalysis; 