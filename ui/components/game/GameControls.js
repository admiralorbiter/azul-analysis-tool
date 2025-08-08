// GameControls.js - Left sidebar controls component
const { useState, useEffect } = React;

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

// Helper: defaults and persisted panel visibility
function getDefaultPanelsForMode(mode) {
    switch (mode) {
        case 'RESEARCH':
            return { essential: true, helpful: true, advanced: true, settings: false };
        case 'LEARNING':
            return { essential: true, helpful: false, advanced: false, settings: false };
        case 'COMPETITIVE':
            return { essential: true, helpful: false, advanced: false, settings: false };
        case 'ANALYSIS':
        default:
            return { essential: true, helpful: true, advanced: false, settings: false };
    }
}

function loadPersistedPanels(mode) {
    try {
        const saved = window.localStorage?.getItem(`ui.toolPanels.${mode}`);
        if (saved) {
            const parsed = JSON.parse(saved);
            const defaults = getDefaultPanelsForMode(mode);
            return {
                essential: parsed.essential ?? defaults.essential,
                helpful: parsed.helpful ?? defaults.helpful,
                advanced: parsed.advanced ?? defaults.advanced,
                settings: parsed.settings ?? defaults.settings
            };
        }
    } catch (err) {
        console.warn('Failed to load panel visibility from localStorage', err);
    }
    return getDefaultPanelsForMode(mode);
}

// Reusable collapsible panel
function ToolPanel({ title, icon, panelId, isOpen, onToggle, toolCount, children }) {
    const headerProps = {
        className: `panel-header ${isOpen ? 'open' : ''}`,
        onClick: onToggle,
        role: 'button',
        tabIndex: 0,
        'aria-expanded': isOpen,
        'aria-controls': panelId,
        onKeyDown: (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onToggle();
            }
        }
    };

    return React.createElement('div', { className: `tool-panel ${isOpen ? 'open' : ''}` },
        React.createElement('div', headerProps,
            React.createElement('div', { className: 'panel-title' },
                icon && React.createElement('span', { className: 'panel-icon' }, icon),
                React.createElement('h4', { className: 'panel-text' }, title)
            ),
            React.createElement('div', { className: 'panel-meta' },
                toolCount != null && React.createElement('span', { className: 'panel-badge' }, `${toolCount}`),
                React.createElement('span', { className: `panel-chevron ${isOpen ? 'rotated' : ''}` }, '▾')
            )
        ),
        isOpen && React.createElement('div', { id: panelId, className: 'panel-content' }, children)
    );
}

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
    setHeatmapEnabled,
    // Workspace
    workspaceMode = 'ANALYSIS'
}) {
    // Category visibility with persistence (per workspace mode)
    const [panelVisibility, setPanelVisibility] = useState(() => loadPersistedPanels(workspaceMode));
    const showAdvanced = workspaceMode === 'RESEARCH' || workspaceMode === 'ANALYSIS';
    const [showAllTools, setShowAllTools] = useState(() => {
        try { return window.localStorage?.getItem('ui.showAllTools') === 'true'; } catch { return false; }
    });
    useEffect(() => {
        try { window.localStorage?.setItem('ui.showAllTools', String(showAllTools)); } catch {}
    }, [showAllTools]);
    const effectiveShowAdvanced = showAdvanced || showAllTools;
    useEffect(() => {
        try {
            window.localStorage?.setItem(`ui.toolPanels.${workspaceMode}`, JSON.stringify(panelVisibility));
        } catch (err) {
            console.warn('Failed to persist panel visibility', err);
        }
    }, [panelVisibility, workspaceMode]);

    // Reset recommended defaults when workspace changes
    useEffect(() => {
        setPanelVisibility(loadPersistedPanels(workspaceMode));
    }, [workspaceMode]);

    const togglePanel = (panelKey) => setPanelVisibility(prev => ({ ...prev, [panelKey]: !prev[panelKey] }));
    const setAllPanels = (open) => setPanelVisibility({
        essential: open,
        helpful: open,
        advanced: effectiveShowAdvanced ? open : false,
        settings: open
    });

    // Suggestions logic
    function computeToolSuggestions(state) {
        const suggestions = [];
        const availableMoves = state?.availableMoves || state?.available_moves || [];
        const phase = state?.gamePhase || state?.phase;
        const patternsDetected = state?.detectedPatterns?.length || state?.pattern_analysis?.total_patterns || 0;
        const remainingTiles = state?.remaining_tiles_count ?? null;

        if (availableMoves.length > 3) {
            suggestions.push({ tool: 'Move Quality', panel: 'essential', action: () => setPanelVisibility(v => ({ ...v, essential: true })), reason: 'Multiple moves available' });
        }
        if (patternsDetected > 0) {
            suggestions.push({ tool: 'Pattern Analysis', panel: 'essential', action: () => setPanelVisibility(v => ({ ...v, essential: true })), reason: 'Patterns detected' });
        }
        if (phase === 'endgame' || (typeof remainingTiles === 'number' && remainingTiles <= 20)) {
            suggestions.push({ tool: 'Game Theory', panel: 'advanced', action: () => setPanelVisibility(v => ({ ...v, advanced: true })), reason: 'Endgame approaching' });
        }
        if (workspaceMode === 'RESEARCH') {
            suggestions.push({ tool: 'Advanced Controls', panel: 'advanced', action: () => setPanelVisibility(v => ({ ...v, advanced: true })), reason: 'Research mode' });
        }
        return suggestions.slice(0, 3);
    }
    const suggestions = computeToolSuggestions(gameState || {});

    return React.createElement('div', {
        className: 'w-1/4 min-w-80'
    },
        // Single unified controls panel
        React.createElement('div', {
            className: 'bg-white rounded p-4 shadow-sm h-full overflow-y-auto'
        },
            React.createElement('div', { className: 'flex items-center justify-between mb-3' },
                React.createElement('h3', { className: 'font-medium text-lg text-blue-700' }, '🎮 Game Controls'),
                React.createElement('div', { className: 'panel-toolbar' },
                    React.createElement('button', { className: `panel-action ${showAllTools ? 'active' : ''}`, onClick: () => setShowAllTools(v => !v), title: showAllTools ? 'Hide advanced tools' : 'Show all tools' }, showAllTools ? 'Hide advanced' : 'Show all'),
                    React.createElement('button', { className: 'panel-action', onClick: () => setAllPanels(true), title: 'Expand all' }, 'Expand all'),
                    React.createElement('button', { className: 'panel-action', onClick: () => setAllPanels(false), title: 'Collapse all' }, 'Collapse all')
                )
            ),

            // Essential tools
            React.createElement(ToolPanel, {
                title: 'Essential',
                icon: '⭐',
                panelId: 'panel-essential',
                isOpen: panelVisibility.essential,
                onToggle: () => togglePanel('essential'),
                toolCount: 4
            },
                // Suggested tools list
                suggestions.length > 0 && React.createElement('div', { className: 'mb-3' },
                    React.createElement('div', { className: 'text-xs text-gray-600 mb-1' }, 'Suggested Tools'),
                    React.createElement('div', { className: 'flex flex-wrap gap-2' },
                        suggestions.map((s, idx) => (
                            React.createElement('button', {
                                key: `${s.tool}-${idx}`,
                                className: 'panel-action',
                                onClick: s.action,
                                title: s.reason
                            }, s.tool)
                        ))
                    )
                ),
                // Analysis results
                React.createElement('div', { className: 'mb-4' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '📊 Analysis Results'),
                    React.createElement(AnalysisResults, { variations, loading, engineThinking })
                ),
                // Move controls
                React.createElement('div', { className: 'mb-4' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '↶↷ Move Controls'),
                    React.createElement('div', { className: 'grid grid-cols-2 gap-2 mb-3' },
                        React.createElement('button', { className: 'btn-warning btn-xs', onClick: handleUndo, disabled: moveHistory.length === 0 || loading }, '↶ Undo'),
                        React.createElement('button', { className: 'btn-secondary btn-xs', onClick: handleRedo, disabled: loading }, '↷ Redo')
                    )
                ),
                // Move Quality
                React.createElement('div', { className: 'mb-4' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '🎯 Move Quality Assessment'),
                    React.createElement(window.MoveQualityDisplay, {
                        gameState,
                        currentPlayer,
                        onMoveRecommendation: (analysis) => {
                            if (analysis.success && analysis.primary_recommendation) {
                                const tier = analysis.primary_recommendation.quality_tier;
                                const score = analysis.primary_recommendation.quality_score;
                                setStatusMessage(`🎯 Best move: ${tier} (${score.toFixed(1)}/100)`);
                            }
                        }
                    })
                ),
                // Pattern analysis
                React.createElement('div', { className: 'mb-2' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '🎯 Pattern Analysis'),
                    React.createElement(PatternAnalysis, {
                        gameState,
                        currentPlayer,
                        onPatternDetected: (patterns) => {
                            if (patterns.patterns_detected) {
                                setStatusMessage(`🎯 ${patterns.total_patterns} tactical pattern${patterns.total_patterns !== 1 ? 's' : ''} detected`);
                            }
                        }
                    })
                )
            ),

            // Helpful tools
            React.createElement(ToolPanel, {
                title: 'Helpful',
                icon: '🧰',
                panelId: 'panel-helpful',
                isOpen: panelVisibility.helpful,
                onToggle: () => togglePanel('helpful'),
                toolCount: (1 + ((workspaceMode === 'ANALYSIS' || workspaceMode === 'COMPETITIVE' || showAllTools) ? 2 : 0))
            },
                React.createElement('div', { className: 'mb-4' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '🏆 Comprehensive Pattern Analysis'),
                    React.createElement(ComprehensivePatternAnalysis, {
                        gameState,
                        currentPlayer,
                        autoAnalyze: autoRefreshEnabled,
                        onComprehensiveAnalysis: (analysis) => {
                            if (analysis.success && analysis.total_patterns > 0) {
                                const categories = Object.keys(analysis.patterns_by_category || {}).filter(cat => (analysis.patterns_by_category[cat].length > 0));
                                setStatusMessage(`🏆 ${analysis.total_patterns} patterns detected across ${categories.length} categories`);
                            }
                        }
                    })
                ),
                (workspaceMode === 'ANALYSIS' || workspaceMode === 'COMPETITIVE' || showAllTools) && React.createElement('div', { className: 'mb-4' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '🎯 Scoring Optimization Analysis'),
                    React.createElement(ScoringOptimizationAnalysis, {
                        gameState,
                        currentPlayer,
                        onOptimizationDetected: (optimizations) => {
                            if (optimizations.opportunities_detected) {
                                setStatusMessage(`🎯 ${optimizations.total_opportunities} scoring optimization opportunity${optimizations.total_opportunities !== 1 ? 'ies' : 'y'} detected`);
                            }
                        }
                    })
                ),
                (workspaceMode === 'ANALYSIS' || workspaceMode === 'COMPETITIVE' || showAllTools) && React.createElement('div', { className: 'mb-2' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '🎯 Strategic Pattern Analysis'),
                    React.createElement(StrategicPatternAnalysis, {
                        gameState,
                        currentPlayer,
                        onStrategicAnalysis: (analysis) => {
                            if (analysis.factory_control_opportunities?.length > 0 || analysis.endgame_scenarios?.length > 0 || analysis.risk_reward_scenarios?.length > 0) {
                                const totalOpportunities = (analysis.factory_control_opportunities?.length || 0) + (analysis.endgame_scenarios?.length || 0) + (analysis.risk_reward_scenarios?.length || 0);
                                setStatusMessage(`🎯 ${totalOpportunities} strategic pattern opportunity${totalOpportunities !== 1 ? 'ies' : 'y'} detected`);
                            }
                        }
                    })
                )
            ),

            // Advanced tools (hidden in Learning/Competitive unless show-all)
            effectiveShowAdvanced && React.createElement(ToolPanel, {
                title: 'Advanced',
                icon: '🧪',
                panelId: 'panel-advanced',
                isOpen: panelVisibility.advanced,
                onToggle: () => togglePanel('advanced'),
                toolCount: 3
            },
                // Analysis tools
                React.createElement('div', { className: 'mb-4' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '🔍 Analysis Tools'),
                    React.createElement(AdvancedAnalysisControls, {
                        loading: loading,
                        setLoading: () => {},
                        analyzePosition,
                        getHint,
                        analyzeNeural,
                        gameState,
                        setVariations,
                        setHeatmapData,
                        setStatusMessage,
                        moveHistory,
                        analyzeGame,
                        depth,
                        setDepth,
                        timeBudget,
                        setTimeBudget,
                        rollouts,
                        setRollouts,
                        agentId,
                        setAgentId
                    })
                ),
                // Alternative moves
                React.createElement('div', { className: 'mb-4' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '🔄 Alternative Move Analysis'),
                    React.createElement(window.AlternativeMoveAnalysis, {
                        gameState,
                        currentPlayer,
                        onMoveSelection: (selectedMove) => {
                            if (selectedMove) {
                                const tier = selectedMove.quality_tier;
                                const score = selectedMove.quality_score;
                                setStatusMessage(`🔄 Selected move: ${tier} (${score.toFixed(1)}/100)`);
                            }
                        }
                    })
                ),
                // Game theory
                React.createElement('div', { className: 'mb-2' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '🎯 Game Theory Analysis'),
                    React.createElement(GameTheoryAnalysis, {
                        gameState,
                        onAnalysisComplete: (analysis) => {
                            if (analysis && analysis.success) {
                                setStatusMessage('🎯 Game theory analysis completed');
                            }
                        }
                    })
                )
            ),

            // Settings & utilities
            React.createElement(ToolPanel, {
                title: 'Settings & Utilities',
                icon: '⚙️',
                panelId: 'panel-settings',
                isOpen: panelVisibility.settings,
                onToggle: () => togglePanel('settings')
            },
                // Quick actions
                React.createElement('div', { className: 'mb-4' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '⚡ Quick Actions'),
                    React.createElement('div', { className: 'grid grid-cols-2 gap-2' },
                        React.createElement('button', { className: 'btn-primary btn-xs', onClick: () => setConfigExpanded(!configExpanded) }, configExpanded ? '⚙️ Hide Config' : '⚙️ Show Config'),
                        React.createElement('button', { className: 'btn-secondary btn-xs', onClick: () => setDevToolsExpanded(!devToolsExpanded) }, devToolsExpanded ? '🔧 Hide Dev Tools' : '🔧 Show Dev Tools'),
                        React.createElement('button', { className: 'btn-info btn-xs', onClick: () => setHeatmapEnabled(!heatmapEnabled) }, heatmapEnabled ? '🔥 Hide Heatmap' : '🔥 Show Heatmap'),
                        React.createElement('button', { className: `${autoRefreshEnabled ? 'btn-warning' : 'btn-success'} btn-xs`, onClick: () => setAutoRefreshEnabled(!autoRefreshEnabled) }, autoRefreshEnabled ? '⏸️ Disable Auto-Refresh' : '▶️ Enable Auto-Refresh')
                    )
                ),
                // Config panel (collapsible by its own toggle)
                configExpanded && React.createElement('div', { className: 'mb-4' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '⚙️ Configuration'),
                    React.createElement(ConfigurationPanel, {
                        loading,
                        setLoading: () => {},
                        setStatusMessage,
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
                        setConfigExpanded
                    })
                ),
                // Dev tools panel (collapsible by its own toggle)
                devToolsExpanded && React.createElement('div', { className: 'mb-2' },
                    React.createElement('h4', { className: 'font-medium text-sm mb-2 text-gray-700' }, '🔧 Development Tools'),
                    React.createElement(DevelopmentToolsPanel, {
                        loading,
                        setLoading: () => {},
                        setStatusMessage,
                        devToolsExpanded,
                        setDevToolsExpanded
                    })
                )
            )
        )
    );
} 