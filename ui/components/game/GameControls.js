// GameControls.js - Left sidebar controls component
const { useState } = React;

// Import components from window
const AdvancedAnalysisControls = window.AdvancedAnalysisControls;
const ConfigurationPanel = window.ConfigurationPanel;
const DevelopmentToolsPanel = window.DevelopmentToolsPanel;
const AnalysisResults = window.AnalysisResults;
const PatternAnalysis = window.PatternAnalysis;
const ComprehensivePatternAnalysis = window.ComprehensivePatternAnalysis;
const ScoringOptimizationAnalysis = window.ScoringOptimizationAnalysis;
const StrategicPatternAnalysis = window.StrategicPatternAnalysis;
const GameTheoryAnalysis = window.GameTheoryAnalysis;

window.GameControls = function GameControls({
    // Analysis state
    variations,
    loading,
    engineThinking,
    setVariations,
    setHeatmapData,
    setStatusMessage,
    moveHistory,
    depth,
    setDepth,
    timeBudget,
    setTimeBudget,
    rollouts,
    setRollouts,
    agentId,
    setAgentId,
    
    // Analysis functions
    analyzePosition,
    getHint,
    analyzeNeural,
    analyzeGame,
    
    // Game state
    gameState,
    currentPlayer,
    
    // Configuration state
    databasePath,
    setDatabasePath,
    modelPath,
    setModelPath,
    defaultTimeout,
    setDefaultTimeout,
    defaultDepth,
    setDefaultDepth,
    defaultRollouts,
    setDefaultRollouts,
    configExpanded,
    setConfigExpanded,
    
    // Development tools state
    devToolsExpanded,
    setDevToolsExpanded,
    
    // Auto-refresh state
    autoRefreshEnabled,
    setAutoRefreshEnabled,
    
    // Move controls
    handleUndo,
    handleRedo,
    
    // Heatmap state
    heatmapEnabled,
    setHeatmapEnabled
}) {
    return React.createElement('div', {
        className: 'w-1/4 min-w-80'
    },
        // Single unified controls panel
        React.createElement('div', {
            className: 'bg-white rounded p-4 shadow-sm h-full overflow-y-auto'
        },
            React.createElement('h3', {
                className: 'font-medium text-lg mb-4 text-blue-700 border-b pb-2'
            }, '🎮 Game Controls'),
            
            // Analysis Results Section
            React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '📊 Analysis Results'),
                React.createElement(AnalysisResults, {
                    variations: variations,
                    loading: loading,
                    engineThinking: engineThinking
                })
            ),
            
            // Action Controls Section
            React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '↶↷ Move Controls'),
                React.createElement('div', {
                    className: 'grid grid-cols-2 gap-2 mb-3'
                },
                    React.createElement('button', {
                        className: 'btn-warning btn-xs',
                        onClick: handleUndo,
                        disabled: moveHistory.length === 0 || loading
                    }, '↶ Undo'),
                    React.createElement('button', {
                        className: 'btn-secondary btn-xs',
                        onClick: handleRedo,
                        disabled: loading
                    }, '↷ Redo')
                )
            ),
            
            // Analysis Tools Section
            React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '🔍 Analysis Tools'),
                React.createElement(AdvancedAnalysisControls, {
                    loading: loading,
                    setLoading: () => {}, // This should be passed from parent
                    analyzePosition: analyzePosition,
                    getHint: getHint,
                    analyzeNeural: analyzeNeural,
                    gameState: gameState,
                    setVariations: setVariations,
                    setHeatmapData: setHeatmapData,
                    setStatusMessage: setStatusMessage,
                    moveHistory: moveHistory,
                    analyzeGame: analyzeGame,
                    depth: depth,
                    setDepth: setDepth,
                    timeBudget: timeBudget,
                    setTimeBudget: setTimeBudget,
                    rollouts: rollouts,
                    setRollouts: setRollouts,
                    agentId: agentId,
                    setAgentId: setAgentId
                })
            ),
            
            // Pattern Analysis Section (R2.1)
            React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '🎯 Pattern Analysis'),
                React.createElement(PatternAnalysis, {
                    gameState: gameState,
                    currentPlayer: currentPlayer,
                    onPatternDetected: (patterns) => {
                        if (patterns.patterns_detected) {
                            setStatusMessage(`🎯 ${patterns.total_patterns} tactical pattern${patterns.total_patterns !== 1 ? 's' : ''} detected`);
                        }
                    }
                })
            ),
            
            // Comprehensive Pattern Analysis Section
            React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '🏆 Comprehensive Pattern Analysis'),
                React.createElement(ComprehensivePatternAnalysis, {
                    gameState: gameState,
                    currentPlayer: currentPlayer,
                    onComprehensiveAnalysis: (analysis) => {
                        if (analysis.success && analysis.total_patterns > 0) {
                            const categories = Object.keys(analysis.patterns_by_category || {}).filter(cat => 
                                analysis.patterns_by_category[cat].length > 0
                            );
                            setStatusMessage(`🏆 ${analysis.total_patterns} patterns detected across ${categories.length} categories`);
                        }
                    }
                })
            ),
            
            // Scoring Optimization Analysis Section (R2.2)
            React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '🎯 Scoring Optimization Analysis'),
                React.createElement(ScoringOptimizationAnalysis, {
                    gameState: gameState,
                    currentPlayer: currentPlayer,
                    onOptimizationDetected: (optimizations) => {
                        if (optimizations.opportunities_detected) {
                            setStatusMessage(`🎯 ${optimizations.total_opportunities} scoring optimization opportunity${optimizations.total_opportunities !== 1 ? 'ies' : 'y'} detected`);
                        }
                    }
                })
            ),
            
            // Strategic Pattern Analysis Section (Phase 2.4)
            React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '🎯 Strategic Pattern Analysis'),
                React.createElement(StrategicPatternAnalysis, {
                    gameState: gameState,
                    currentPlayer: currentPlayer,
                    onStrategicAnalysis: (analysis) => {
                        if (analysis.factory_control_opportunities?.length > 0 || 
                            analysis.endgame_scenarios?.length > 0 || 
                            analysis.risk_reward_scenarios?.length > 0) {
                            const totalOpportunities = (analysis.factory_control_opportunities?.length || 0) + 
                                                     (analysis.endgame_scenarios?.length || 0) + 
                                                     (analysis.risk_reward_scenarios?.length || 0);
                            setStatusMessage(`🎯 ${totalOpportunities} strategic pattern opportunity${totalOpportunities !== 1 ? 'ies' : 'y'} detected`);
                        }
                    }
                })
            ),
            
            // Move Quality Analysis Section (R2.2)
            React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '🎯 Move Quality Assessment'),
                React.createElement(MoveQualityAnalysis, {
                    gameState: gameState,
                    currentPlayer: currentPlayer,
                    onMoveRecommendation: (analysis) => {
                        if (analysis.success && analysis.primary_recommendation) {
                            const tier = analysis.primary_recommendation.quality_tier;
                            const score = analysis.primary_recommendation.quality_score;
                            setStatusMessage(`🎯 Best move: ${tier} (${score.toFixed(1)}/100)`);
                        }
                    }
                })
            ),
            
            // Game Theory Analysis Section (Week 3)
            React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '🎯 Game Theory Analysis'),
                React.createElement(GameTheoryAnalysis, {
                    gameState: gameState,
                    onAnalysisComplete: (analysis) => {
                        if (analysis && analysis.success) {
                            setStatusMessage(`🎯 Game theory analysis completed`);
                        }
                    }
                })
            ),
            
            // Quick Actions Section
            React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '⚡ Quick Actions'),
                React.createElement('div', {
                    className: 'grid grid-cols-2 gap-2'
                },
                    React.createElement('button', {
                        className: 'btn-primary btn-xs',
                        onClick: () => setConfigExpanded(!configExpanded)
                    }, configExpanded ? '⚙️ Hide Config' : '⚙️ Show Config'),
                    React.createElement('button', {
                        className: 'btn-secondary btn-xs',
                        onClick: () => setDevToolsExpanded(!devToolsExpanded)
                    }, devToolsExpanded ? '🔧 Hide Dev Tools' : '🔧 Show Dev Tools'),
                    React.createElement('button', {
                        className: 'btn-info btn-xs',
                        onClick: () => setHeatmapEnabled(!heatmapEnabled)
                    }, heatmapEnabled ? '🔥 Hide Heatmap' : '🔥 Show Heatmap'),
                    React.createElement('button', {
                        className: `${autoRefreshEnabled ? 'btn-warning' : 'btn-success'} btn-xs`,
                        onClick: () => setAutoRefreshEnabled(!autoRefreshEnabled)
                    }, autoRefreshEnabled ? '⏸️ Disable Auto-Refresh' : '▶️ Enable Auto-Refresh')
                )
            ),
            
            // Collapsible Configuration Panel
            configExpanded && React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '⚙️ Configuration'),
                React.createElement(ConfigurationPanel, {
                    loading: loading,
                    setLoading: () => {}, // This should be passed from parent
                    setStatusMessage: setStatusMessage,
                    databasePath: databasePath,
                    setDatabasePath: setDatabasePath,
                    modelPath: modelPath,
                    setModelPath: setModelPath,
                    defaultTimeout: defaultTimeout,
                    setDefaultTimeout: setDefaultTimeout,
                    defaultDepth: defaultDepth,
                    setDefaultDepth: setDefaultDepth,
                    defaultRollouts: defaultRollouts,
                    setDefaultRollouts: setDefaultRollouts,
                    configExpanded: configExpanded,
                    setConfigExpanded: setConfigExpanded
                })
            ),
            
            // Collapsible Development Tools Panel
            devToolsExpanded && React.createElement('div', {
                className: 'mb-4'
            },
                React.createElement('h4', {
                    className: 'font-medium text-sm mb-2 text-gray-700'
                }, '🔧 Development Tools'),
                React.createElement(DevelopmentToolsPanel, {
                    loading: loading,
                    setLoading: () => {}, // This should be passed from parent
                    setStatusMessage: setStatusMessage,
                    devToolsExpanded: devToolsExpanded,
                    setDevToolsExpanded: setDevToolsExpanded
                })
            )
        )
    );
} 