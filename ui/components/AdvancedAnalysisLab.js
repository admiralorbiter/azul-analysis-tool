// Advanced Analysis Lab Component
// Research-grade analysis tools with multi-engine comparison and advanced evaluation capabilities

const { useState, useEffect, useCallback } = React;

function AdvancedAnalysisLab({ gameState, setStatusMessage }) {
    // State for analysis data
    const [analysisData, setAnalysisData] = useState({
        multiEngineResults: {},
        consensusAnalysis: {},
        evaluationComparison: {},
        searchDepthAnalysis: {}
    });
    
    const [selectedEngines, setSelectedEngines] = useState(['alpha-beta', 'mcts', 'neural']);
    const [analysisDepth, setAnalysisDepth] = useState(3);
    const [timeLimit, setTimeLimit] = useState(5000);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('multi-engine');
    
    // Mock data for demonstration (replace with real API calls)
    const mockAnalysisData = {
        multiEngineResults: {
            'alpha-beta': {
                evaluation: -0.15,
                confidence: 0.85,
                depth: 3,
                time: 1200,
                bestMove: 'A1-B2',
                analysis: 'Slightly better for Black'
            },
            'mcts': {
                evaluation: -0.12,
                confidence: 0.78,
                rollouts: 1000,
                time: 800,
                bestMove: 'A1-B2',
                analysis: 'Equal position with slight edge to Black'
            },
            'neural': {
                evaluation: -0.18,
                confidence: 0.92,
                depth: 2,
                time: 600,
                bestMove: 'A1-B2',
                analysis: 'Black has a clear advantage'
            }
        },
        consensusAnalysis: {
            agreement: 0.75,
            bestMove: 'A1-B2',
            confidence: 0.82,
            disagreement: ['neural', 'mcts'],
            reasoning: 'Alpha-Beta and Neural agree on the best move, MCTS suggests alternative'
        },
        evaluationComparison: {
            ranges: {
                'alpha-beta': [-0.25, -0.05],
                'mcts': [-0.20, -0.04],
                'neural': [-0.30, -0.10]
            },
            convergence: 0.70,
            outliers: ['neural']
        },
        searchDepthAnalysis: {
            'alpha-beta': {
                depth1: -0.10,
                depth2: -0.12,
                depth3: -0.15,
                convergence: true
            },
            'mcts': {
                rollouts100: -0.08,
                rollouts500: -0.10,
                rollouts1000: -0.12,
                convergence: true
            },
            'neural': {
                depth1: -0.15,
                depth2: -0.18,
                convergence: true
            }
        }
    };
    
    // Load analysis data
    const loadAnalysisData = useCallback(async () => {
        setLoading(true);
        try {
            // TODO: Replace with real API call
            // const response = await fetch('/api/v1/analysis/advanced', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({
            //         engines: selectedEngines,
            //         depth: analysisDepth,
            //         timeLimit: timeLimit,
            //         gameState: gameState
            //     })
            // });
            // const data = await response.json();
            
            // For now, use mock data
            await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
            setAnalysisData(mockAnalysisData);
            setStatusMessage('Advanced analysis completed successfully');
        } catch (error) {
            console.error('Error loading analysis data:', error);
            setStatusMessage('Error performing advanced analysis');
        } finally {
            setLoading(false);
        }
    }, [selectedEngines, analysisDepth, timeLimit, gameState, setStatusMessage]);
    
    // Load data on component mount and parameter changes
    useEffect(() => {
        loadAnalysisData();
    }, [loadAnalysisData]);
    
    // Get evaluation color
    const getEvaluationColor = (evaluation) => {
        if (evaluation > 0.1) return 'text-green-600';
        if (evaluation < -0.1) return 'text-red-600';
        return 'text-gray-600';
    };
    
    // Get confidence color
    const getConfidenceColor = (confidence) => {
        if (confidence > 0.8) return 'text-green-600';
        if (confidence > 0.6) return 'text-yellow-600';
        return 'text-red-600';
    };
    
    // Render multi-engine comparison
    const renderMultiEngineComparison = () => {
        const results = analysisData.multiEngineResults;
        
        return React.createElement('div', { className: 'space-y-4' },
            React.createElement('h3', { className: 'text-lg font-semibold mb-4' }, 'Multi-Engine Analysis'),
            Object.entries(results).map(([engine, data]) => 
                React.createElement('div', {
                    key: engine,
                    className: 'bg-white rounded-lg p-4 shadow-sm border-l-4 border-blue-500'
                },
                    React.createElement('div', { className: 'flex items-center justify-between mb-3' },
                        React.createElement('h4', { className: 'text-md font-medium capitalize' }, 
                            engine.replace('-', ' ')
                        ),
                        React.createElement('span', { 
                            className: `px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(data.confidence)}`
                        }, `${Math.round(data.confidence * 100)}% confidence`)
                    ),
                    React.createElement('div', { className: 'grid grid-cols-2 gap-4' },
                        React.createElement('div', null,
                            React.createElement('div', { className: 'text-sm text-gray-600' }, 'Evaluation'),
                            React.createElement('div', { 
                                className: `text-lg font-bold ${getEvaluationColor(data.evaluation)}`
                            }, data.evaluation.toFixed(2))
                        ),
                        React.createElement('div', null,
                            React.createElement('div', { className: 'text-sm text-gray-600' }, 'Best Move'),
                            React.createElement('div', { className: 'text-lg font-medium' }, data.bestMove)
                        ),
                        React.createElement('div', null,
                            React.createElement('div', { className: 'text-sm text-gray-600' }, 'Depth/Rollouts'),
                            React.createElement('div', { className: 'text-lg font-medium' }, 
                                data.depth || data.rollouts
                            )
                        ),
                        React.createElement('div', null,
                            React.createElement('div', { className: 'text-sm text-gray-600' }, 'Time (ms)'),
                            React.createElement('div', { className: 'text-lg font-medium' }, data.time)
                        )
                    ),
                    React.createElement('div', { className: 'mt-3 p-2 bg-gray-50 rounded' },
                        React.createElement('div', { className: 'text-sm text-gray-700' }, data.analysis)
                    )
                )
            )
        );
    };
    
    // Render consensus analysis
    const renderConsensusAnalysis = () => {
        const consensus = analysisData.consensusAnalysis;
        
        return React.createElement('div', { className: 'space-y-4' },
            React.createElement('h3', { className: 'text-lg font-semibold mb-4' }, 'Consensus Analysis'),
            React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm' },
                React.createElement('div', { className: 'grid grid-cols-2 gap-4 mb-4' },
                    React.createElement('div', null,
                        React.createElement('div', { className: 'text-sm text-gray-600' }, 'Agreement Level'),
                        React.createElement('div', { className: 'text-lg font-bold text-green-600' }, 
                            `${Math.round(consensus.agreement * 100)}%`
                        )
                    ),
                    React.createElement('div', null,
                        React.createElement('div', { className: 'text-sm text-gray-600' }, 'Consensus Move'),
                        React.createElement('div', { className: 'text-lg font-medium' }, consensus.bestMove)
                    ),
                    React.createElement('div', null,
                        React.createElement('div', { className: 'text-sm text-gray-600' }, 'Confidence'),
                        React.createElement('div', { 
                            className: `text-lg font-bold ${getConfidenceColor(consensus.confidence)}`
                        }, `${Math.round(consensus.confidence * 100)}%`)
                    ),
                    React.createElement('div', null,
                        React.createElement('div', { className: 'text-sm text-gray-600' }, 'Disagreements'),
                        React.createElement('div', { className: 'text-lg font-medium' }, 
                            consensus.disagreement.join(', ')
                        )
                    )
                ),
                React.createElement('div', { className: 'p-3 bg-blue-50 rounded' },
                    React.createElement('div', { className: 'text-sm font-medium text-blue-800' }, 'Reasoning'),
                    React.createElement('div', { className: 'text-sm text-blue-700 mt-1' }, consensus.reasoning)
                )
            )
        );
    };
    
    // Render evaluation comparison
    const renderEvaluationComparison = () => {
        const comparison = analysisData.evaluationComparison;
        
        return React.createElement('div', { className: 'space-y-4' },
            React.createElement('h3', { className: 'text-lg font-semibold mb-4' }, 'Evaluation Comparison'),
            React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm' },
                React.createElement('div', { className: 'mb-4' },
                    React.createElement('div', { className: 'text-sm text-gray-600 mb-2' }, 'Evaluation Ranges'),
                    Object.entries(comparison.ranges).map(([engine, range]) => 
                        React.createElement('div', {
                            key: engine,
                            className: 'flex items-center justify-between mb-2'
                        },
                            React.createElement('span', { className: 'text-sm capitalize' }, 
                                engine.replace('-', ' ')
                            ),
                            React.createElement('span', { className: 'text-sm font-medium' }, 
                                `[${range[0].toFixed(2)}, ${range[1].toFixed(2)}]`
                            )
                        )
                    )
                ),
                React.createElement('div', { className: 'grid grid-cols-2 gap-4' },
                    React.createElement('div', null,
                        React.createElement('div', { className: 'text-sm text-gray-600' }, 'Convergence'),
                        React.createElement('div', { className: 'text-lg font-bold text-green-600' }, 
                            `${Math.round(comparison.convergence * 100)}%`
                        )
                    ),
                    React.createElement('div', null,
                        React.createElement('div', { className: 'text-sm text-gray-600' }, 'Outliers'),
                        React.createElement('div', { className: 'text-lg font-medium' }, 
                            comparison.outliers.join(', ')
                        )
                    )
                )
            )
        );
    };
    
    // Render search depth analysis
    const renderSearchDepthAnalysis = () => {
        const depthAnalysis = analysisData.searchDepthAnalysis;
        
        return React.createElement('div', { className: 'space-y-4' },
            React.createElement('h3', { className: 'text-lg font-semibold mb-4' }, 'Search Depth Analysis'),
            Object.entries(depthAnalysis).map(([engine, data]) => 
                React.createElement('div', {
                    key: engine,
                    className: 'bg-white rounded-lg p-4 shadow-sm'
                },
                    React.createElement('h4', { className: 'text-md font-medium capitalize mb-3' }, 
                        engine.replace('-', ' ')
                    ),
                    React.createElement('div', { className: 'space-y-2' },
                        Object.entries(data).filter(([key]) => key !== 'convergence').map(([depth, evaluation]) => 
                            React.createElement('div', {
                                key: depth,
                                className: 'flex items-center justify-between'
                            },
                                React.createElement('span', { className: 'text-sm' }, depth),
                                React.createElement('span', { 
                                    className: `text-sm font-medium ${getEvaluationColor(evaluation)}`
                                }, evaluation.toFixed(2))
                            )
                        )
                    ),
                    React.createElement('div', { className: 'mt-3 flex items-center' },
                        React.createElement('span', { className: 'text-sm text-gray-600 mr-2' }, 'Convergence:'),
                        React.createElement('span', { 
                            className: `text-sm font-medium ${data.convergence ? 'text-green-600' : 'text-red-600'}`
                        }, data.convergence ? '✓' : '✗')
                    )
                )
            )
        );
    };
    
    // Render tab content
    const renderTabContent = () => {
        switch (activeTab) {
            case 'multi-engine':
                return renderMultiEngineComparison();
            case 'consensus':
                return renderConsensusAnalysis();
            case 'evaluation':
                return renderEvaluationComparison();
            case 'depth':
                return renderSearchDepthAnalysis();
            default:
                return renderMultiEngineComparison();
        }
    };
    
    return React.createElement('div', { className: 'p-6 max-w-7xl mx-auto' },
        // Header
        React.createElement('div', { className: 'mb-6' },
            React.createElement('h1', { className: 'text-3xl font-bold text-gray-900 mb-2' }, '🔍 Advanced Analysis Lab'),
            React.createElement('p', { className: 'text-gray-600' }, 
                'Research-grade analysis tools with multi-engine comparison and advanced evaluation capabilities.'
            )
        ),
        
        // Controls
        React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm mb-6' },
            React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-4 gap-4' },
                React.createElement('div', null,
                    React.createElement('label', { className: 'block text-sm font-medium text-gray-700 mb-1' }, 'Engines'),
                    React.createElement('div', { className: 'space-y-1' },
                        ['alpha-beta', 'mcts', 'neural'].map(engine => 
                            React.createElement('label', {
                                key: engine,
                                className: 'flex items-center'
                            },
                                React.createElement('input', {
                                    type: 'checkbox',
                                    checked: selectedEngines.includes(engine),
                                    onChange: (e) => {
                                        if (e.target.checked) {
                                            setSelectedEngines([...selectedEngines, engine]);
                                        } else {
                                            setSelectedEngines(selectedEngines.filter(e => e !== engine));
                                        }
                                    },
                                    className: 'mr-2'
                                }),
                                React.createElement('span', { className: 'text-sm capitalize' }, 
                                    engine.replace('-', ' ')
                                )
                            )
                        )
                    )
                ),
                React.createElement('div', null,
                    React.createElement('label', { className: 'block text-sm font-medium text-gray-700 mb-1' }, 'Depth'),
                    React.createElement('input', {
                        type: 'number',
                        value: analysisDepth,
                        onChange: (e) => setAnalysisDepth(parseInt(e.target.value)),
                        min: 1,
                        max: 10,
                        className: 'w-full border border-gray-300 rounded px-3 py-1 text-sm'
                    })
                ),
                React.createElement('div', null,
                    React.createElement('label', { className: 'block text-sm font-medium text-gray-700 mb-1' }, 'Time Limit (ms)'),
                    React.createElement('input', {
                        type: 'number',
                        value: timeLimit,
                        onChange: (e) => setTimeLimit(parseInt(e.target.value)),
                        min: 1000,
                        max: 30000,
                        step: 1000,
                        className: 'w-full border border-gray-300 rounded px-3 py-1 text-sm'
                    })
                ),
                React.createElement('div', { className: 'flex items-end' },
                    React.createElement('button', {
                        onClick: loadAnalysisData,
                        disabled: loading,
                        className: 'w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50'
                    }, loading ? 'Analyzing...' : 'Run Analysis')
                )
            )
        ),
        
        // Tabs
        React.createElement('div', { className: 'mb-6' },
            React.createElement('div', { className: 'border-b border-gray-200' },
                React.createElement('nav', { className: 'flex space-x-8' },
                    ['multi-engine', 'consensus', 'evaluation', 'depth'].map(tab => 
                        React.createElement('button', {
                            key: tab,
                            onClick: () => setActiveTab(tab),
                            className: `py-2 px-1 border-b-2 font-medium text-sm ${
                                activeTab === tab 
                                    ? 'border-blue-500 text-blue-600' 
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`
                        }, tab.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '))
                    )
                )
            )
        ),
        
        // Loading state
        loading && React.createElement('div', { className: 'text-center py-8' },
            React.createElement('div', { className: 'text-gray-500' }, 'Performing advanced analysis...')
        ),
        
        // Analysis content
        !loading && renderTabContent()
    );
}

window.AdvancedAnalysisLab = AdvancedAnalysisLab; 