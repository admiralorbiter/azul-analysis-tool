// GameTheoryPage.js - Dedicated Game Theory Analysis Page
const { useState, useEffect } = React;

const GameTheoryPage = ({ gameState, setStatusMessage }) => {
    const [activeTab, setActiveTab] = useState('analysis');
    const [analysisHistory, setAnalysisHistory] = useState([]);
    const [selectedAnalysis, setSelectedAnalysis] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [quickStats, setQuickStats] = useState({
        totalAnalyses: 0,
        successRate: 0,
        lastAnalysis: null,
        mostUsedType: 'nash_equilibrium'
    });

    const tabs = [
        { id: 'analysis', label: '🎯 Analysis', icon: '🎯' },
        { id: 'history', label: '📊 History', icon: '📊' },
        { id: 'insights', label: '💡 Insights', icon: '💡' },
        { id: 'settings', label: '⚙️ Settings', icon: '⚙️' }
    ];

    const addToHistory = (analysis) => {
        const timestamp = new Date().toLocaleString();
        const historyItem = {
            id: Date.now(),
            timestamp,
            analysis,
            type: analysis.analysis_type || 'unknown'
        };
        setAnalysisHistory(prev => [historyItem, ...prev.slice(0, 9)]); // Keep last 10
        
        // Update quick stats
        const newStats = {
            totalAnalyses: quickStats.totalAnalyses + 1,
            successRate: ((quickStats.totalAnalyses * quickStats.successRate + (analysis.success ? 1 : 0)) / (quickStats.totalAnalyses + 1)) * 100,
            lastAnalysis: timestamp,
            mostUsedType: analysis.analysis_type || quickStats.mostUsedType
        };
        setQuickStats(newStats);
    };

    const renderQuickStats = () => {
        return React.createElement('div', { className: 'quick-stats' },
            React.createElement('div', { className: 'stats-grid' },
                React.createElement('div', { className: 'stat-card' },
                    React.createElement('div', { className: 'stat-icon' }, '📊'),
                    React.createElement('div', { className: 'stat-content' },
                        React.createElement('div', { className: 'stat-value' }, quickStats.totalAnalyses),
                        React.createElement('div', { className: 'stat-label' }, 'Total Analyses')
                    )
                ),
                React.createElement('div', { className: 'stat-card' },
                    React.createElement('div', { className: 'stat-icon' }, '✅'),
                    React.createElement('div', { className: 'stat-content' },
                        React.createElement('div', { className: 'stat-value' }, `${quickStats.successRate.toFixed(1)}%`),
                        React.createElement('div', { className: 'stat-label' }, 'Success Rate')
                    )
                ),
                React.createElement('div', { className: 'stat-card' },
                    React.createElement('div', { className: 'stat-icon' }, '🎯'),
                    React.createElement('div', { className: 'stat-content' },
                        React.createElement('div', { className: 'stat-value' }, quickStats.mostUsedType.replace('_', ' ')),
                        React.createElement('div', { className: 'stat-label' }, 'Most Used')
                    )
                ),
                React.createElement('div', { className: 'stat-card' },
                    React.createElement('div', { className: 'stat-icon' }, '⏰'),
                    React.createElement('div', { className: 'stat-content' },
                        React.createElement('div', { className: 'stat-value' }, quickStats.lastAnalysis ? 'Recent' : 'None'),
                        React.createElement('div', { className: 'stat-label' }, 'Last Analysis')
                    )
                )
            )
        );
    };

    const renderAnalysisTab = () => {
        return React.createElement('div', { className: 'analysis-tab' },
            React.createElement('div', { className: 'analysis-header-section' },
                React.createElement('h2', { className: 'text-2xl font-bold mb-4 text-gray-800' }, '🎯 Game Theory Analysis'),
                React.createElement('p', { className: 'text-gray-600 mb-6' }, 
                    'Advanced strategic analysis using game theory concepts including Nash equilibrium, opponent modeling, and strategic value calculation.'
                )
            ),
            renderQuickStats(),
            React.createElement('div', { className: 'analysis-content' },
                React.createElement(GameTheoryAnalysis, {
                    gameState: gameState,
                    onAnalysisComplete: (analysis) => {
                        addToHistory(analysis);
                        if (analysis && analysis.success) {
                            setStatusMessage(`🎯 Game theory analysis completed: ${analysis.analysis_type || 'analysis'}`);
                        } else if (analysis && !analysis.success) {
                            setStatusMessage(`❌ Game theory analysis failed: ${analysis.error || 'Unknown error'}`);
                        }
                    },
                    onAnalysisStart: () => setIsLoading(true),
                    onAnalysisEnd: () => setIsLoading(false)
                })
            )
        );
    };

    const renderHistoryTab = () => {
        if (analysisHistory.length === 0) {
            return React.createElement('div', { className: 'empty-history' },
                React.createElement('div', { className: 'text-center py-12' },
                    React.createElement('div', { className: 'text-6xl mb-4' }, '📊'),
                    React.createElement('h3', { className: 'text-xl font-semibold mb-2' }, 'No Analysis History'),
                    React.createElement('p', { className: 'text-gray-600' }, 'Run your first game theory analysis to see results here.')
                )
            );
        }

        return React.createElement('div', { className: 'history-tab' },
            React.createElement('h3', { className: 'text-xl font-semibold mb-4' }, '📊 Analysis History'),
            React.createElement('div', { className: 'history-grid' },
                analysisHistory.map(item => 
                    React.createElement('div', {
                        key: item.id,
                        className: `history-item ${selectedAnalysis?.id === item.id ? 'selected' : ''}`,
                        onClick: () => setSelectedAnalysis(item)
                    },
                        React.createElement('div', { className: 'history-header' },
                            React.createElement('span', { className: 'history-type' }, item.type),
                            React.createElement('span', { className: 'history-timestamp' }, item.timestamp)
                        ),
                        React.createElement('div', { className: 'history-summary' },
                            React.createElement('span', { className: 'history-status' }, 
                                item.analysis.success ? '✅ Success' : '❌ Failed'
                            )
                        )
                    )
                )
            ),
            selectedAnalysis && React.createElement('div', { className: 'selected-analysis-details' },
                React.createElement('h4', { className: 'text-lg font-semibold mb-3' }, 'Analysis Details'),
                React.createElement('div', { className: 'analysis-details-content' },
                    React.createElement('pre', { className: 'analysis-json' }, 
                        JSON.stringify(selectedAnalysis.analysis, null, 2)
                    )
                )
            )
        );
    };

    const renderInsightsTab = () => {
        return React.createElement('div', { className: 'insights-tab' },
            React.createElement('h3', { className: 'text-xl font-semibold mb-4' }, '💡 Game Theory Insights'),
            React.createElement('div', { className: 'insights-grid' },
                React.createElement('div', { className: 'insight-card' },
                    React.createElement('div', { className: 'insight-icon' }, '🎯'),
                    React.createElement('h4', { className: 'insight-title' }, 'Nash Equilibrium'),
                    React.createElement('p', { className: 'insight-description' }, 
                        'Detect optimal strategies where no player can unilaterally improve their outcome.'
                    )
                ),
                React.createElement('div', { className: 'insight-card' },
                    React.createElement('div', { className: 'insight-icon' }, '🧠'),
                    React.createElement('h4', { className: 'insight-title' }, 'Opponent Modeling'),
                    React.createElement('p', { className: 'insight-description' }, 
                        'Predict opponent behavior based on game state and strategic patterns.'
                    )
                ),
                React.createElement('div', { className: 'insight-card' },
                    React.createElement('div', { className: 'insight-icon' }, '📊'),
                    React.createElement('h4', { className: 'insight-title' }, 'Strategic Analysis'),
                    React.createElement('p', { className: 'insight-description' }, 
                        'Comprehensive evaluation of position strength and strategic opportunities.'
                    )
                ),
                React.createElement('div', { className: 'insight-card' },
                    React.createElement('div', { className: 'insight-icon' }, '🔮'),
                    React.createElement('h4', { className: 'insight-title' }, 'Move Prediction'),
                    React.createElement('p', { className: 'insight-description' }, 
                        'Forecast opponent moves to plan counter-strategies.'
                    )
                ),
                React.createElement('div', { className: 'insight-card' },
                    React.createElement('div', { className: 'insight-icon' }, '💰'),
                    React.createElement('h4', { className: 'insight-title' }, 'Strategic Value'),
                    React.createElement('p', { className: 'insight-description' }, 
                        'Calculate the strategic value and potential of current positions.'
                    )
                )
            )
        );
    };

    const renderSettingsTab = () => {
        return React.createElement('div', { className: 'settings-tab' },
            React.createElement('h3', { className: 'text-xl font-semibold mb-4' }, '⚙️ Game Theory Settings'),
            React.createElement('div', { className: 'settings-grid' },
                React.createElement('div', { className: 'setting-group' },
                    React.createElement('label', { className: 'setting-label' }, 'Default Analysis Type'),
                    React.createElement('select', { className: 'setting-select' },
                        React.createElement('option', { value: 'nash_equilibrium' }, 'Nash Equilibrium'),
                        React.createElement('option', { value: 'opponent_modeling' }, 'Opponent Modeling'),
                        React.createElement('option', { value: 'strategic_analysis' }, 'Strategic Analysis'),
                        React.createElement('option', { value: 'move_prediction' }, 'Move Prediction'),
                        React.createElement('option', { value: 'strategic_value' }, 'Strategic Value')
                    )
                ),
                React.createElement('div', { className: 'setting-group' },
                    React.createElement('label', { className: 'setting-label' }, 'Default Prediction Depth'),
                    React.createElement('input', { 
                        type: 'range', 
                        min: '1', 
                        max: '5', 
                        defaultValue: '3',
                        className: 'setting-range'
                    }),
                    React.createElement('span', { className: 'setting-value' }, '3')
                ),
                React.createElement('div', { className: 'setting-group' },
                    React.createElement('label', { className: 'setting-label' }, 'Auto-save Analysis Results'),
                    React.createElement('input', { type: 'checkbox', defaultChecked: true, className: 'setting-checkbox' })
                )
            )
        );
    };

    const renderTabContent = () => {
        switch (activeTab) {
            case 'analysis':
                return renderAnalysisTab();
            case 'history':
                return renderHistoryTab();
            case 'insights':
                return renderInsightsTab();
            case 'settings':
                return renderSettingsTab();
            default:
                return renderAnalysisTab();
        }
    };

    return React.createElement('div', { className: 'game-theory-page' },
        // Tab Navigation
        React.createElement('div', { className: 'tab-navigation' },
            tabs.map(tab => 
                React.createElement('button', {
                    key: tab.id,
                    className: `tab-button ${activeTab === tab.id ? 'active' : ''}`,
                    onClick: () => setActiveTab(tab.id)
                },
                    React.createElement('span', { className: 'tab-icon' }, tab.icon),
                    React.createElement('span', { className: 'tab-label' }, tab.label)
                )
            )
        ),
        
        // Tab Content
        React.createElement('div', { className: 'tab-content' },
            renderTabContent()
        )
    );
};

// Export to window for global access
window.GameTheoryPage = GameTheoryPage; 