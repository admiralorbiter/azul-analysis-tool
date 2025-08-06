// Performance Analytics Component
// Comprehensive player improvement tracking and competitive metrics dashboard

const { useState, useEffect, useCallback } = React;

function PerformanceAnalytics({ gameState, setStatusMessage }) {
    // State for analytics data
    const [analyticsData, setAnalyticsData] = useState({
        ratingProgression: [],
        performanceMetrics: {},
        skillBreakdown: {},
        recentGames: []
    });
    
    const [selectedTimeframe, setSelectedTimeframe] = useState('30d');
    const [selectedMetric, setSelectedMetric] = useState('overall');
    const [loading, setLoading] = useState(false);
    
    // Mock data for demonstration (replace with real API calls)
    const mockAnalyticsData = {
        ratingProgression: [
            { date: '2024-01-01', rating: 1200, category: 'overall' },
            { date: '2024-01-08', rating: 1220, category: 'overall' },
            { date: '2024-01-15', rating: 1240, category: 'overall' },
            { date: '2024-01-22', rating: 1260, category: 'overall' },
            { date: '2024-01-29', rating: 1280, category: 'overall' }
        ],
        performanceMetrics: {
            overall: { current: 1280, change: '+80', trend: 'up' },
            tactical: { current: 1250, change: '+50', trend: 'up' },
            positional: { current: 1300, change: '+100', trend: 'up' },
            endgame: { current: 1220, change: '+20', trend: 'stable' }
        },
        skillBreakdown: {
            patternRecognition: 85,
            moveQuality: 78,
            timing: 82,
            riskAssessment: 75,
            endgamePlay: 70
        },
        recentGames: [
            { id: 1, date: '2024-01-29', result: 'W', rating: 1280, opponent: 'Player A', analysis: 'Strong tactical play' },
            { id: 2, date: '2024-01-28', result: 'L', rating: 1260, opponent: 'Player B', analysis: 'Endgame mistakes' },
            { id: 3, date: '2024-01-27', result: 'W', rating: 1270, opponent: 'Player C', analysis: 'Good positional play' }
        ]
    };
    
    // Load analytics data
    const loadAnalyticsData = useCallback(async () => {
        setLoading(true);
        try {
            // TODO: Replace with real API call
            // const response = await fetch('/api/v1/analytics/performance', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ timeframe: selectedTimeframe })
            // });
            // const data = await response.json();
            
            // For now, use mock data
            await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API delay
            setAnalyticsData(mockAnalyticsData);
            setStatusMessage('Analytics data loaded successfully');
        } catch (error) {
            console.error('Error loading analytics data:', error);
            setStatusMessage('Error loading analytics data');
        } finally {
            setLoading(false);
        }
    }, [selectedTimeframe, setStatusMessage]);
    
    // Load data on component mount and timeframe change
    useEffect(() => {
        loadAnalyticsData();
    }, [loadAnalyticsData]);
    
    // Calculate trend indicator
    const getTrendIndicator = (trend) => {
        switch (trend) {
            case 'up': return '↗️';
            case 'down': return '↘️';
            case 'stable': return '→';
            default: return '→';
        }
    };
    
    // Get trend color
    const getTrendColor = (trend) => {
        switch (trend) {
            case 'up': return 'text-green-600';
            case 'down': return 'text-red-600';
            case 'stable': return 'text-gray-600';
            default: return 'text-gray-600';
        }
    };
    
    // Render rating progression chart
    const renderRatingChart = () => {
        const data = analyticsData.ratingProgression;
        if (!data.length) return React.createElement('div', { className: 'text-gray-500' }, 'No data available');
        
        return React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm' },
            React.createElement('h3', { className: 'text-lg font-semibold mb-4' }, 'Rating Progression'),
            React.createElement('div', { className: 'h-64 flex items-end justify-between' },
                data.map((point, index) => {
                    const height = ((point.rating - 1100) / 200) * 100; // Normalize to 0-100%
                    return React.createElement('div', {
                        key: index,
                        className: 'flex-1 mx-1 bg-blue-500 rounded-t',
                        style: { height: `${Math.max(height, 10)}%` },
                        React.createElement('div', { className: 'text-xs text-center mt-1' }, point.rating)
                    );
                })
            ),
            React.createElement('div', { className: 'flex justify-between text-xs text-gray-500 mt-2' },
                data.map((point, index) => 
                    React.createElement('div', { key: index }, new Date(point.date).toLocaleDateString())
                )
            )
        );
    };
    
    // Render performance metrics
    const renderPerformanceMetrics = () => {
        const metrics = analyticsData.performanceMetrics;
        
        return React.createElement('div', { className: 'grid grid-cols-2 md:grid-cols-4 gap-4 mb-6' },
            Object.entries(metrics).map(([category, data]) => 
                React.createElement('div', {
                    key: category,
                    className: 'bg-white rounded-lg p-4 shadow-sm border-l-4 border-blue-500'
                },
                    React.createElement('div', { className: 'text-sm text-gray-600 capitalize' }, category),
                    React.createElement('div', { className: 'text-2xl font-bold' }, data.current),
                    React.createElement('div', { 
                        className: `text-sm ${getTrendColor(data.trend)} flex items-center`
                    },
                        getTrendIndicator(data.trend),
                        React.createElement('span', { className: 'ml-1' }, data.change)
                    )
                )
            )
        );
    };
    
    // Render skill breakdown
    const renderSkillBreakdown = () => {
        const skills = analyticsData.skillBreakdown;
        
        return React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm mb-6' },
            React.createElement('h3', { className: 'text-lg font-semibold mb-4' }, 'Skill Breakdown'),
            React.createElement('div', { className: 'space-y-3' },
                Object.entries(skills).map(([skill, score]) => 
                    React.createElement('div', { key: skill, className: 'flex items-center justify-between' },
                        React.createElement('span', { className: 'text-sm capitalize' }, 
                            skill.replace(/([A-Z])/g, ' $1').trim()
                        ),
                        React.createElement('div', { className: 'flex items-center' },
                            React.createElement('div', { className: 'w-32 bg-gray-200 rounded-full h-2 mr-2' },
                                React.createElement('div', {
                                    className: 'bg-blue-500 h-2 rounded-full',
                                    style: { width: `${score}%` }
                                })
                            ),
                            React.createElement('span', { className: 'text-sm font-medium' }, `${score}%`)
                        )
                    )
                )
            )
        );
    };
    
    // Render recent games
    const renderRecentGames = () => {
        const games = analyticsData.recentGames;
        
        return React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm' },
            React.createElement('h3', { className: 'text-lg font-semibold mb-4' }, 'Recent Games'),
            React.createElement('div', { className: 'space-y-2' },
                games.map(game => 
                    React.createElement('div', {
                        key: game.id,
                        className: 'flex items-center justify-between p-3 bg-gray-50 rounded'
                    },
                        React.createElement('div', { className: 'flex items-center' },
                            React.createElement('span', { 
                                className: `w-6 h-6 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                                    game.result === 'W' ? 'bg-green-500' : 'bg-red-500'
                                }`
                            }, game.result),
                            React.createElement('div', { className: 'ml-3' },
                                React.createElement('div', { className: 'text-sm font-medium' }, game.opponent),
                                React.createElement('div', { className: 'text-xs text-gray-500' }, game.analysis)
                            )
                        ),
                        React.createElement('div', { className: 'text-right' },
                            React.createElement('div', { className: 'text-sm font-medium' }, game.rating),
                            React.createElement('div', { className: 'text-xs text-gray-500' }, 
                                new Date(game.date).toLocaleDateString()
                            )
                        )
                    )
                )
            )
        );
    };
    
    return React.createElement('div', { className: 'p-6 max-w-7xl mx-auto' },
        // Header
        React.createElement('div', { className: 'mb-6' },
            React.createElement('h1', { className: 'text-3xl font-bold text-gray-900 mb-2' }, '📈 Performance Analytics'),
            React.createElement('p', { className: 'text-gray-600' }, 
                'Track your improvement and identify areas for growth with comprehensive analytics and visualization tools.'
            )
        ),
        
        // Controls
        React.createElement('div', { className: 'flex flex-wrap gap-4 mb-6' },
            React.createElement('div', { className: 'flex items-center space-x-2' },
                React.createElement('label', { className: 'text-sm font-medium text-gray-700' }, 'Timeframe:'),
                React.createElement('select', {
                    value: selectedTimeframe,
                    onChange: (e) => setSelectedTimeframe(e.target.value),
                    className: 'border border-gray-300 rounded px-3 py-1 text-sm'
                },
                    React.createElement('option', { value: '7d' }, 'Last 7 days'),
                    React.createElement('option', { value: '30d' }, 'Last 30 days'),
                    React.createElement('option', { value: '90d' }, 'Last 90 days'),
                    React.createElement('option', { value: '1y' }, 'Last year')
                )
            ),
            React.createElement('div', { className: 'flex items-center space-x-2' },
                React.createElement('label', { className: 'text-sm font-medium text-gray-700' }, 'Metric:'),
                React.createElement('select', {
                    value: selectedMetric,
                    onChange: (e) => setSelectedMetric(e.target.value),
                    className: 'border border-gray-300 rounded px-3 py-1 text-sm'
                },
                    React.createElement('option', { value: 'overall' }, 'Overall'),
                    React.createElement('option', { value: 'tactical' }, 'Tactical'),
                    React.createElement('option', { value: 'positional' }, 'Positional'),
                    React.createElement('option', { value: 'endgame' }, 'Endgame')
                )
            ),
            React.createElement('button', {
                onClick: loadAnalyticsData,
                disabled: loading,
                className: 'px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50'
            }, loading ? 'Loading...' : 'Refresh')
        ),
        
        // Loading state
        loading && React.createElement('div', { className: 'text-center py-8' },
            React.createElement('div', { className: 'text-gray-500' }, 'Loading analytics data...')
        ),
        
        // Analytics content
        !loading && React.createElement('div', { className: 'space-y-6' },
            // Performance metrics
            renderPerformanceMetrics(),
            
            // Main content grid
            React.createElement('div', { className: 'grid grid-cols-1 lg:grid-cols-2 gap-6' },
                // Rating progression chart
                renderRatingChart(),
                
                // Skill breakdown
                renderSkillBreakdown()
            ),
            
            // Recent games
            renderRecentGames()
        )
    );
}

window.PerformanceAnalytics = PerformanceAnalytics; 