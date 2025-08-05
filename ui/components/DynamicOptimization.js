// DynamicOptimization.js - Dynamic Programming Optimization Component
// Using global React and callAPI from window

class DynamicOptimization extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: false,
            error: null,
            selectedAnalysis: 'endgame_evaluation',
            selectedStrategy: 'scoring_maximization',
            turnsAhead: 3,
            evaluationDepth: 3,
            analysisResults: null,
            analysisTypes: [
                { value: 'endgame_evaluation', label: 'Endgame Evaluation' },
                { value: 'multi_turn_planning', label: 'Multi-Turn Planning' },
                { value: 'game_phase_analysis', label: 'Game Phase Analysis' },
                { value: 'strategy_optimization', label: 'Strategy Optimization' }
            ],
            strategyTypes: [
                { value: 'wall_completion', label: 'Wall Completion' },
                { value: 'penalty_minimization', label: 'Penalty Minimization' },
                { value: 'scoring_maximization', label: 'Scoring Maximization' }
            ]
        };
    }

    componentDidMount() {
        console.log('DynamicOptimization: componentDidMount');
        // Initialize session if not already done
        if (window.api && !window.api.sessionId) {
            console.log('DynamicOptimization: Initializing session');
            window.api.initializeSession().then(success => {
                console.log('DynamicOptimization: Session initialization result:', success);
            });
        }
    }

    async analyzeGame() {
        this.setState({ loading: true, error: null, result: null });
        
        try {
            // Ensure session is initialized
            if (window.api && !window.api.sessionId) {
                console.log('DynamicOptimization: Initializing session before analysis');
                const sessionSuccess = await window.api.initializeSession();
                if (!sessionSuccess) {
                    throw new Error('Failed to initialize session');
                }
            }
            
            const { selectedAnalysis, evaluationDepth } = this.state;
            const gameState = this.props.gameState;
            
            console.log('DynamicOptimization: Starting analysis', {
                selectedAnalysis,
                evaluationDepth,
                fenString: gameState.fen_string
            });
            
            let endpoint, payload;
            
            switch (selectedAnalysis) {
                case 'endgame_evaluation':
                    endpoint = '/evaluate-endgame';
                    payload = {
                        fen_string: gameState.fen_string,
                        depth: evaluationDepth
                    };
                    break;
                case 'multi_turn_planning':
                    endpoint = '/plan-multi-turn';
                    payload = {
                        fen_string: gameState.fen_string,
                        depth: evaluationDepth
                    };
                    break;
                case 'game_phase_analysis':
                    endpoint = '/analyze-game-phase';
                    payload = {
                        fen_string: gameState.fen_string
                    };
                    break;
                case 'strategy_optimization':
                    endpoint = '/optimize-endgame-strategy';
                    payload = {
                        fen_string: gameState.fen_string,
                        depth: evaluationDepth
                    };
                    break;
                default:
                    throw new Error(`Unknown analysis type: ${selectedAnalysis}`);
            }
            
            console.log('DynamicOptimization: Making API call', { endpoint, payload });
            
            const response = await (window.api?.callAPI || (() => {
                console.error('window.api.callAPI not available');
                return { success: false, error: 'API not available' };
            }))(endpoint, 'POST', payload);
            
            if (response.success) {
                console.log('DynamicOptimization: Analysis successful', response);
                this.setState({
                    analysisResults: response,
                    loading: false
                });
            } else {
                console.error('DynamicOptimization: Analysis failed', response);
                this.setState({
                    error: response.error || 'Analysis failed',
                    loading: false
                });
            }
        } catch (error) {
            console.error('DynamicOptimization: Analysis error', error);
            this.setState({
                error: `Analysis error: ${error.message}`,
                loading: false
            });
        }
    }

    renderEndgameEvaluation() {
        const { analysisResults } = this.state;
        if (!analysisResults || !analysisResults.endgame_evaluation) return null;

        const eval_data = analysisResults.endgame_evaluation;

        return (
            <div className="endgame-evaluation">
                <h3>Endgame Evaluation Results</h3>
                
                <div className="evaluation-summary">
                    <div className="summary-item">
                        <strong>Game Phase:</strong> {eval_data.game_phase}
                    </div>
                    <div className="summary-item">
                        <strong>Endgame Score:</strong> {eval_data.endgame_score.toFixed(2)}
                    </div>
                    <div className="summary-item">
                        <strong>Confidence:</strong> {(eval_data.confidence * 100).toFixed(1)}%
                    </div>
                    <div className="summary-item">
                        <strong>Evaluation Time:</strong> {eval_data.evaluation_time.toFixed(4)}s
                    </div>
                </div>

                <div className="evaluation-metrics">
                    <h4>Detailed Metrics</h4>
                    <div className="metrics-grid">
                        <div className="metric-item">
                            <label>Wall Completion:</label>
                            <span>{eval_data.wall_completion.toFixed(2)}</span>
                        </div>
                        <div className="metric-item">
                            <label>Floor Line Penalty:</label>
                            <span>{eval_data.floor_line_penalty}</span>
                        </div>
                        <div className="metric-item">
                            <label>Pattern Line Efficiency:</label>
                            <span>{(eval_data.pattern_line_efficiency * 100).toFixed(1)}%</span>
                        </div>
                        <div className="metric-item">
                            <label>Factory Control:</label>
                            <span>{(eval_data.factory_control * 100).toFixed(1)}%</span>
                        </div>
                        <div className="metric-item">
                            <label>Opponent Blocking:</label>
                            <span>{(eval_data.opponent_blocking_potential * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>

                {analysisResults.recommendations && (
                    <div className="recommendations">
                        <h4>Recommendations</h4>
                        <ul>
                            {analysisResults.recommendations.map((rec, index) => (
                                <li key={index}>{rec}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {analysisResults.risk_assessment && (
                    <div className="risk-assessment">
                        <h4>Risk Assessment</h4>
                        <div className="risk-grid">
                            {Object.entries(analysisResults.risk_assessment).map(([key, value]) => (
                                <div key={key} className="risk-item">
                                    <label>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</label>
                                    <span className={`risk-level risk-${value > 0.7 ? 'high' : value > 0.4 ? 'medium' : 'low'}`}>
                                        {(value * 100).toFixed(1)}%
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        );
    }

    renderMultiTurnPlanning() {
        const { analysisResults } = this.state;
        if (!analysisResults || !analysisResults.multi_turn_plan) return null;

        const plan = analysisResults.multi_turn_plan;

        return (
            <div className="multi-turn-planning">
                <h3>Multi-Turn Planning Results</h3>
                
                <div className="plan-summary">
                    <div className="summary-item">
                        <strong>Total Expected Score:</strong> {plan.total_expected_score.toFixed(2)}
                    </div>
                    <div className="summary-item">
                        <strong>Confidence Score:</strong> {(plan.confidence_score * 100).toFixed(1)}%
                    </div>
                    <div className="summary-item">
                        <strong>Planning Time:</strong> {analysisResults.planning_time.toFixed(4)}s
                    </div>
                    <div className="summary-item">
                        <strong>Move Sequence Length:</strong> {plan.move_sequence.length}
                    </div>
                </div>

                {plan.move_sequence.length > 0 && (
                    <div className="move-sequence">
                        <h4>Optimal Move Sequence</h4>
                        <div className="moves-list">
                            {plan.move_sequence.map((move, index) => (
                                <div key={index} className="move-item">
                                    <span className="move-number">{index + 1}.</span>
                                    <span className="move-type">{move.type.replace(/_/g, ' ')}</span>
                                    <span className="move-details">
                                        Factory {move.factory_idx} → {move.color === 1 ? 'Blue' : 
                                                                      move.color === 2 ? 'Yellow' : 
                                                                      move.color === 3 ? 'Red' : 
                                                                      move.color === 4 ? 'Black' : 'White'} 
                                        {move.pattern_line_idx !== undefined ? ` → Row ${move.pattern_line_idx}` : ''}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {plan.alternative_plans && plan.alternative_plans.length > 0 && (
                    <div className="alternative-plans">
                        <h4>Alternative Plans</h4>
                        {plan.alternative_plans.map((altPlan, index) => (
                            <div key={index} className="alternative-plan">
                                <div className="alt-plan-header">
                                    <strong>Plan {index + 2}:</strong> Score {altPlan.score.toFixed(2)}, 
                                    Confidence {(altPlan.confidence * 100).toFixed(1)}%, 
                                    Risk {(altPlan.risk * 100).toFixed(1)}%
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {plan.risk_assessment && (
                    <div className="plan-risk-assessment">
                        <h4>Risk Assessment</h4>
                        <div className="risk-grid">
                            {Object.entries(plan.risk_assessment).map(([key, value]) => (
                                <div key={key} className="risk-item">
                                    <label>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</label>
                                    <span className={`risk-level risk-${value > 0.7 ? 'high' : value > 0.4 ? 'medium' : 'low'}`}>
                                        {(value * 100).toFixed(1)}%
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {analysisResults.recommendations && (
                    <div className="planning-recommendations">
                        <h4>Planning Recommendations</h4>
                        <ul>
                            {analysisResults.recommendations.map((rec, index) => (
                                <li key={index}>{rec}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {analysisResults.execution_guidance && (
                    <div className="execution-guidance">
                        <h4>Execution Guidance</h4>
                        <div className="guidance-grid">
                            <div className="guidance-item">
                                <label>Execution Priority:</label>
                                <span className={`priority-${analysisResults.execution_guidance.execution_priority}`}>
                                    {analysisResults.execution_guidance.execution_priority}
                                </span>
                            </div>
                            <div className="guidance-item">
                                <label>Risk Monitoring:</label>
                                <span className={analysisResults.execution_guidance.risk_monitoring ? 'required' : 'not-required'}>
                                    {analysisResults.execution_guidance.risk_monitoring ? 'Required' : 'Not Required'}
                                </span>
                            </div>
                            <div className="guidance-item">
                                <label>Alternative Ready:</label>
                                <span className={analysisResults.execution_guidance.alternative_ready ? 'yes' : 'no'}>
                                    {analysisResults.execution_guidance.alternative_ready ? 'Yes' : 'No'}
                                </span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    }

    renderGamePhaseAnalysis() {
        const { analysisResults } = this.state;
        if (!analysisResults) return null;

        return (
            <div className="game-phase-analysis">
                <h3>Game Phase Analysis Results</h3>
                
                <div className="phase-summary">
                    <div className="summary-item">
                        <strong>Game Phase:</strong> {analysisResults.game_phase}
                    </div>
                    {analysisResults.phase_analysis && (
                        <>
                            <div className="summary-item">
                                <strong>Round Number:</strong> {analysisResults.phase_analysis.round_number}
                            </div>
                            <div className="summary-item">
                                <strong>Turns Remaining:</strong> {analysisResults.phase_analysis.turns_remaining}
                            </div>
                        </>
                    )}
                </div>

                {analysisResults.phase_analysis && analysisResults.phase_analysis.phase_characteristics && (
                    <div className="phase-characteristics">
                        <h4>Phase Characteristics</h4>
                        <div className="characteristics-grid">
                            {Object.entries(analysisResults.phase_analysis.phase_characteristics).map(([key, value]) => (
                                <div key={key} className="characteristic-item">
                                    <label>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</label>
                                    <span>{value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {analysisResults.phase_analysis && analysisResults.phase_analysis.strategic_focus && (
                    <div className="strategic-focus">
                        <h4>Strategic Focus Areas</h4>
                        <ul>
                            {analysisResults.phase_analysis.strategic_focus.map((focus, index) => (
                                <li key={index}>{focus}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {analysisResults.strategic_insights && (
                    <div className="strategic-insights">
                        <h4>Strategic Insights</h4>
                        <ul>
                            {analysisResults.strategic_insights.map((insight, index) => (
                                <li key={index}>{insight}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {analysisResults.phase_recommendations && (
                    <div className="phase-recommendations">
                        <h4>Phase-Specific Recommendations</h4>
                        <ul>
                            {analysisResults.phase_recommendations.map((rec, index) => (
                                <li key={index}>{rec}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        );
    }

    renderStrategyOptimization() {
        const { analysisResults } = this.state;
        if (!analysisResults) return null;

        return (
            <div className="strategy-optimization">
                <h3>Strategy Optimization Results</h3>
                
                <div className="strategy-summary">
                    <div className="summary-item">
                        <strong>Strategy Focus:</strong> {analysisResults.strategy_focus.replace(/_/g, ' ')}
                    </div>
                </div>

                {analysisResults.strategy_optimization && (
                    <div className="optimization-details">
                        <h4>Optimization Details</h4>
                        <div className="optimization-grid">
                            <div className="optimization-item">
                                <label>Expected Improvement:</label>
                                <span>{analysisResults.strategy_optimization.expected_improvement.toFixed(1)} points</span>
                            </div>
                            <div className="optimization-item">
                                <label>Implementation Priority:</label>
                                <span className={`priority-${analysisResults.strategy_optimization.implementation_priority}`}>
                                    {analysisResults.strategy_optimization.implementation_priority}
                                </span>
                            </div>
                        </div>

                        {analysisResults.strategy_optimization.optimization_actions && (
                            <div className="optimization-actions">
                                <h5>Optimization Actions</h5>
                                <ul>
                                    {analysisResults.strategy_optimization.optimization_actions.map((action, index) => (
                                        <li key={index}>{action}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}

                {analysisResults.recommendations && (
                    <div className="strategy-recommendations">
                        <h4>Strategy Recommendations</h4>
                        <ul>
                            {analysisResults.recommendations.map((rec, index) => (
                                <li key={index}>{rec}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        );
    }

    renderAnalysisResults() {
        const { selectedAnalysis, analysisResults } = this.state;

        if (!analysisResults) return null;

        switch (selectedAnalysis) {
            case 'endgame_evaluation':
                return this.renderEndgameEvaluation();
            case 'multi_turn_planning':
                return this.renderMultiTurnPlanning();
            case 'game_phase_analysis':
                return this.renderGamePhaseAnalysis();
            case 'strategy_optimization':
                return this.renderStrategyOptimization();
            default:
                return <div>Unknown analysis type</div>;
        }
    }

    render() {
        const { 
            loading, 
            error, 
            selectedAnalysis, 
            selectedStrategy, 
            turnsAhead, 
            evaluationDepth,
            analysisTypes,
            strategyTypes
        } = this.state;

        return (
            <div className="dynamic-optimization">
                <h2>Dynamic Programming Optimization</h2>
                <p>Use dynamic programming to evaluate endgame scenarios and plan optimal multi-turn sequences.</p>
                
                <div className="optimization-controls">
                    <div className="control-group">
                        <label htmlFor="analysis-type">Analysis Type:</label>
                        <select 
                            id="analysis-type"
                            value={selectedAnalysis}
                            onChange={(e) => this.setState({ selectedAnalysis: e.target.value })}
                        >
                            {analysisTypes.map(type => (
                                <option key={type.value} value={type.value}>
                                    {type.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    {selectedAnalysis === 'strategy_optimization' && (
                        <div className="control-group">
                            <label htmlFor="strategy-type">Strategy Focus:</label>
                            <select 
                                id="strategy-type"
                                value={selectedStrategy}
                                onChange={(e) => this.setState({ selectedStrategy: e.target.value })}
                            >
                                {strategyTypes.map(type => (
                                    <option key={type.value} value={type.value}>
                                        {type.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    {selectedAnalysis === 'multi_turn_planning' && (
                        <div className="control-group">
                            <label htmlFor="turns-ahead">Turns Ahead:</label>
                            <input 
                                id="turns-ahead"
                                type="number" 
                                min="1" 
                                max="5" 
                                value={turnsAhead}
                                onChange={(e) => this.setState({ turnsAhead: parseInt(e.target.value) })}
                            />
                        </div>
                    )}

                    <div className="control-group">
                        <label htmlFor="evaluation-depth">Evaluation Depth:</label>
                        <input 
                            id="evaluation-depth"
                            type="number" 
                            min="1" 
                            max="10" 
                            value={evaluationDepth}
                            onChange={(e) => this.setState({ evaluationDepth: parseInt(e.target.value) })}
                        />
                    </div>

                    <button 
                        className="analyze-button"
                        onClick={() => this.analyzeGame()}
                        disabled={loading}
                    >
                        {loading ? 'Analyzing...' : 'Analyze Game'}
                    </button>
                </div>

                {error && (
                    <div className="error-message">
                        <strong>Error:</strong> {error}
                    </div>
                )}

                {this.renderAnalysisResults()}
            </div>
        );
    }
}

window.DynamicOptimization = DynamicOptimization; 