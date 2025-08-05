// GameTheoryAnalysis.js - Game Theory Analysis UI Component
const { useState, useEffect } = React;

const GameTheoryAnalysis = ({ gameState, onAnalysisComplete }) => {
    const [analysisType, setAnalysisType] = useState('nash_equilibrium');
    const [isLoading, setIsLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [playerId, setPlayerId] = useState(0);
    const [opponentId, setOpponentId] = useState(1);
    const [predictionDepth, setPredictionDepth] = useState(3);

    const analysisTypes = [
        { value: 'nash_equilibrium', label: '🎯 Nash Equilibrium Detection', description: 'Detect Nash equilibrium in current position' },
        { value: 'opponent_modeling', label: '🧠 Opponent Modeling', description: 'Model opponent behavior and strategy' },
        { value: 'strategic_analysis', label: '📊 Strategic Analysis', description: 'Comprehensive strategic position analysis' },
        { value: 'move_prediction', label: '🔮 Move Prediction', description: 'Predict opponent\'s likely moves' },
        { value: 'strategic_value', label: '💰 Strategic Value', description: 'Calculate strategic value of position' }
    ];

    const performAnalysis = async () => {
        if (!gameState) {
            setError('No game state available for analysis');
            return;
        }

        setIsLoading(true);
        setError(null);

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
                setResults(data);
                if (onAnalysisComplete) {
                    onAnalysisComplete(data);
                }
            } else {
                throw new Error(data.error || 'Analysis failed');
            }

        } catch (err) {
            setError(err.message);
            console.error('Game theory analysis error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const renderNashEquilibriumResults = () => {
        if (!results) return null;

        return (
            <div className="analysis-results">
                <h3>🎯 Nash Equilibrium Analysis</h3>
                <div className="result-grid">
                    <div className="result-item">
                        <label>Equilibrium Type:</label>
                        <span className={`equilibrium-type ${results.equilibrium_type}`}>
                            {results.equilibrium_type.replace('_', ' ').toUpperCase()}
                        </span>
                    </div>
                    <div className="result-item">
                        <label>Confidence:</label>
                        <span className="confidence-score">
                            {(results.confidence * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div className="result-item">
                        <label>Strategic Insights:</label>
                        <ul className="insights-list">
                            {results.strategic_insights?.map((insight, index) => (
                                <li key={index}>{insight}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        );
    };

    const renderOpponentModelingResults = () => {
        if (!results?.opponent_model) return null;

        const model = results.opponent_model;

        return (
            <div className="analysis-results">
                <h3>🧠 Opponent Modeling Results</h3>
                <div className="result-grid">
                    <div className="result-item">
                        <label>Player ID:</label>
                        <span>{model.player_id}</span>
                    </div>
                    <div className="result-item">
                        <label>Risk Tolerance:</label>
                        <span className="metric-bar">
                            <div className="bar-fill" style={{ width: `${model.risk_tolerance * 100}%` }}></div>
                            {(model.risk_tolerance * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div className="result-item">
                        <label>Aggression Level:</label>
                        <span className="metric-bar">
                            <div className="bar-fill" style={{ width: `${model.aggression_level * 100}%` }}></div>
                            {(model.aggression_level * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div className="result-item">
                        <label>Predictability:</label>
                        <span className="metric-bar">
                            <div className="bar-fill" style={{ width: `${model.predictability_score * 100}%` }}></div>
                            {(model.predictability_score * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div className="result-item full-width">
                        <label>Strategy Profile:</label>
                        <div className="strategy-profile">
                            {Object.entries(model.strategy_profile).map(([strategy, probability]) => (
                                <div key={strategy} className="strategy-item">
                                    <span className="strategy-name">{strategy.replace('_', ' ')}</span>
                                    <span className="strategy-probability">{(probability * 100).toFixed(1)}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderStrategicAnalysisResults = () => {
        if (!results?.strategic_analysis) return null;

        const analysis = results.strategic_analysis;

        return (
            <div className="analysis-results">
                <h3>📊 Strategic Analysis Results</h3>
                <div className="result-grid">
                    <div className="result-item">
                        <label>Strategic Value:</label>
                        <span className="strategic-value">{analysis.strategic_value.toFixed(1)}</span>
                    </div>
                    <div className="result-item">
                        <label>Game Phase:</label>
                        <span className={`game-phase ${analysis.game_phase}`}>
                            {analysis.game_phase.replace('_', ' ').toUpperCase()}
                        </span>
                    </div>
                    <div className="result-item">
                        <label>Confidence:</label>
                        <span className="confidence-score">
                            {(analysis.confidence * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div className="result-item full-width">
                        <label>Recommended Actions:</label>
                        <ul className="recommendations-list">
                            {analysis.recommended_actions?.map((action, index) => (
                                <li key={index}>{action}</li>
                            ))}
                        </ul>
                    </div>
                    <div className="result-item full-width">
                        <label>Risk Assessment:</label>
                        <div className="risk-assessment">
                            {Object.entries(analysis.risk_assessment).map(([risk, level]) => (
                                <div key={risk} className="risk-item">
                                    <span className="risk-name">{risk.replace('_', ' ')}</span>
                                    <span className="risk-level">
                                        <div className="risk-bar">
                                            <div className="risk-fill" style={{ width: `${level * 100}%` }}></div>
                                        </div>
                                        {(level * 100).toFixed(1)}%
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderMovePredictionResults = () => {
        if (!results?.predicted_moves) return null;

        return (
            <div className="analysis-results">
                <h3>🔮 Move Prediction Results</h3>
                <div className="result-grid">
                    <div className="result-item">
                        <label>Prediction Confidence:</label>
                        <span className="confidence-score">
                            {(results.confidence * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div className="result-item">
                        <label>Reasoning:</label>
                        <span className="reasoning">{results.reasoning}</span>
                    </div>
                    <div className="result-item full-width">
                        <label>Predicted Moves:</label>
                        <div className="predicted-moves">
                            {results.predicted_moves.map((move, index) => (
                                <div key={index} className="predicted-move">
                                    <span className="move-turn">Turn {move.turn}</span>
                                    <span className="move-strategy">{move.strategy.replace('_', ' ')}</span>
                                    <span className="move-confidence">{(move.confidence * 100).toFixed(1)}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderStrategicValueResults = () => {
        if (!results) return null;

        return (
            <div className="analysis-results">
                <h3>💰 Strategic Value Analysis</h3>
                <div className="result-grid">
                    <div className="result-item">
                        <label>Strategic Value:</label>
                        <span className="strategic-value">{results.strategic_value.toFixed(1)}</span>
                    </div>
                    <div className="result-item">
                        <label>Confidence:</label>
                        <span className="confidence-score">
                            {(results.confidence * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div className="result-item full-width">
                        <label>Value Components:</label>
                        <div className="value-components">
                            {Object.entries(results.components).map(([component, value]) => (
                                <div key={component} className="component-item">
                                    <span className="component-name">{component.replace('_', ' ')}</span>
                                    <span className="component-value">{value.toFixed(1)}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
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

    return (
        <div className="game-theory-analysis">
            <div className="analysis-header">
                <h2>🎯 Game Theory Analysis</h2>
                <p>Advanced strategic analysis using game theory concepts</p>
            </div>

            <div className="analysis-controls">
                <div className="control-group">
                    <label>Analysis Type:</label>
                    <select 
                        value={analysisType} 
                        onChange={(e) => setAnalysisType(e.target.value)}
                        className="analysis-type-select"
                    >
                        {analysisTypes.map(type => (
                            <option key={type.value} value={type.value}>
                                {type.label}
                            </option>
                        ))}
                    </select>
                    <div className="analysis-description">
                        {analysisTypes.find(t => t.value === analysisType)?.description}
                    </div>
                </div>

                <div className="control-group">
                    <label>Player ID:</label>
                    <input 
                        type="number" 
                        value={playerId} 
                        onChange={(e) => setPlayerId(parseInt(e.target.value))}
                        min="0"
                        max="3"
                        className="player-input"
                    />
                </div>

                {(analysisType === 'opponent_modeling' || analysisType === 'move_prediction') && (
                    <div className="control-group">
                        <label>Opponent ID:</label>
                        <input 
                            type="number" 
                            value={opponentId} 
                            onChange={(e) => setOpponentId(parseInt(e.target.value))}
                            min="0"
                            max="3"
                            className="opponent-input"
                        />
                    </div>
                )}

                {analysisType === 'move_prediction' && (
                    <div className="control-group">
                        <label>Prediction Depth:</label>
                        <input 
                            type="number" 
                            value={predictionDepth} 
                            onChange={(e) => setPredictionDepth(parseInt(e.target.value))}
                            min="1"
                            max="5"
                            className="depth-input"
                        />
                    </div>
                )}

                <button 
                    onClick={performAnalysis}
                    disabled={isLoading || !gameState}
                    className="analyze-button"
                >
                    {isLoading ? '🔄 Analyzing...' : '🎯 Analyze Position'}
                </button>
            </div>

            {error && (
                <div className="error-message">
                    ❌ Error: {error}
                </div>
            )}

            {renderResults()}
        </div>
    );
};

// Export to window for global access
window.GameTheoryAnalysis = GameTheoryAnalysis; 