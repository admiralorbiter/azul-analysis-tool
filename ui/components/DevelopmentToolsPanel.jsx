// DevelopmentToolsPanel Component
// Extracted from main.js for Phase 3 refactoring

const DevelopmentToolsPanel = ({ 
    loading, setLoading, setStatusMessage,
    devToolsExpanded, setDevToolsExpanded
}) => {
    const [healthData, setHealthData] = React.useState(null);
    const [statsData, setStatsData] = React.useState(null);
    const [performanceData, setPerformanceData] = React.useState(null);
    const [systemHealthData, setSystemHealthData] = React.useState(null);
    const [optimizationResult, setOptimizationResult] = React.useState(null);
    const [analyticsData, setAnalyticsData] = React.useState(null);
    const [monitoringData, setMonitoringData] = React.useState(null);

    // System Health Check
    const checkSystemHealth = React.useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/health');
            const data = await response.json();
            setHealthData(data);
            setStatusMessage('System health check completed');
        } catch (error) {
            setStatusMessage(`Health check failed: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [setLoading, setStatusMessage]);

    // API Statistics
    const getApiStats = React.useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/stats');
            const data = await response.json();
            setStatsData(data);
            setStatusMessage('API statistics retrieved');
        } catch (error) {
            setStatusMessage(`Failed to get API stats: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [setLoading, setStatusMessage]);

    // Performance Statistics
    const getPerformanceStats = React.useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/performance/stats');
            const data = await response.json();
            setPerformanceData(data);
            setStatusMessage('Performance statistics retrieved');
        } catch (error) {
            setStatusMessage(`Failed to get performance stats: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [setLoading, setStatusMessage]);

    // System Health (Detailed)
    const getSystemHealth = React.useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/performance/health');
            const data = await response.json();
            setSystemHealthData(data);
            setStatusMessage('Detailed system health retrieved');
        } catch (error) {
            setStatusMessage(`Failed to get system health: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [setLoading, setStatusMessage]);

    // Database Optimization
    const optimizeDatabase = React.useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/performance/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            setOptimizationResult(data);
            setStatusMessage('Database optimization completed');
        } catch (error) {
            setStatusMessage(`Database optimization failed: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [setLoading, setStatusMessage]);

    // Cache Analytics
    const getCacheAnalytics = React.useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/performance/analytics');
            const data = await response.json();
            setAnalyticsData(data);
            setStatusMessage('Cache analytics retrieved');
        } catch (error) {
            setStatusMessage(`Failed to get cache analytics: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [setLoading, setStatusMessage]);

    // Monitoring Data
    const getMonitoringData = React.useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/performance/monitoring');
            const data = await response.json();
            setMonitoringData(data);
            setStatusMessage('Monitoring data retrieved');
        } catch (error) {
            setStatusMessage(`Failed to get monitoring data: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [setLoading, setStatusMessage]);

    // Clear all data
    const clearAllData = React.useCallback(() => {
        setHealthData(null);
        setStatsData(null);
        setPerformanceData(null);
        setSystemHealthData(null);
        setOptimizationResult(null);
        setAnalyticsData(null);
        setMonitoringData(null);
        setStatusMessage('Development tools data cleared');
    }, [setStatusMessage]);

    return React.createElement('div', {
        className: 'development-tools'
    },
        React.createElement('h3', {
            className: 'font-medium text-sm mb-3 flex items-center justify-between text-purple-700'
        },
            React.createElement('span', null, '🔧 Development Tools'),
            React.createElement('button', {
                className: 'text-xs text-gray-500 hover:text-gray-700',
                onClick: () => setDevToolsExpanded(!devToolsExpanded)
            }, devToolsExpanded ? '−' : '+')
        ),
        
        devToolsExpanded && React.createElement('div', {
            className: 'space-y-3'
        },
            // System Health Check
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('button', {
                    className: `w-full btn-sm ${loading ? 'btn-secondary opacity-50' : 'btn-outline'}`,
                    onClick: checkSystemHealth,
                    disabled: loading
                }, loading ? '🏥 Checking Health...' : '🏥 System Health Check'),
                
                healthData && React.createElement('div', {
                    className: 'p-2 bg-green-50 rounded text-xs'
                },
                    React.createElement('div', { className: 'font-medium' }, 'System Status:'),
                    React.createElement('div', { className: 'text-green-700' }, `Status: ${healthData.status}`),
                    React.createElement('div', { className: 'text-gray-600' }, `Version: ${healthData.version}`),
                    React.createElement('div', { className: 'text-gray-600' }, `Timestamp: ${new Date(healthData.timestamp * 1000).toLocaleString()}`)
                )
            ),

            // API Statistics
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('button', {
                    className: `w-full btn-sm ${loading ? 'btn-secondary opacity-50' : 'btn-outline'}`,
                    onClick: getApiStats,
                    disabled: loading
                }, loading ? '📊 Getting Stats...' : '📊 API Statistics'),
                
                statsData && React.createElement('div', {
                    className: 'p-2 bg-blue-50 rounded text-xs'
                },
                    React.createElement('div', { className: 'font-medium' }, 'API Statistics:'),
                    React.createElement('div', { className: 'text-blue-700' }, `Rate Limits: ${JSON.stringify(statsData.rate_limits || {})}`),
                    React.createElement('div', { className: 'text-gray-600' }, `Session Stats: ${JSON.stringify(statsData.session_stats || {})}`)
                )
            ),

            // Performance Statistics
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('button', {
                    className: `w-full btn-sm ${loading ? 'btn-secondary opacity-50' : 'btn-outline'}`,
                    onClick: getPerformanceStats,
                    disabled: loading
                }, loading ? '⚡ Getting Performance...' : '⚡ Performance Stats'),
                
                performanceData && React.createElement('div', {
                    className: 'p-2 bg-purple-50 rounded text-xs'
                },
                    React.createElement('div', { className: 'font-medium' }, 'Performance Statistics:'),
                    React.createElement('div', { className: 'text-purple-700' }, `Cache Hit Rate: ${performanceData.cache_analytics?.cache_hit_rate?.toFixed(2) || 'N/A'}%`),
                    React.createElement('div', { className: 'text-gray-600' }, `Positions Cached: ${performanceData.cache_analytics?.positions_cached || 0}`),
                    React.createElement('div', { className: 'text-gray-600' }, `Analyses Cached: ${performanceData.cache_analytics?.analyses_cached || 0}`),
                    React.createElement('div', { className: 'text-gray-600' }, `Cache Size: ${performanceData.cache_analytics?.total_cache_size_mb?.toFixed(2) || 0} MB`)
                )
            ),

            // System Health (Detailed)
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('button', {
                    className: `w-full btn-sm ${loading ? 'btn-secondary opacity-50' : 'btn-outline'}`,
                    onClick: getSystemHealth,
                    disabled: loading
                }, loading ? '🔍 Getting Health...' : '🔍 Detailed Health'),
                
                systemHealthData && React.createElement('div', {
                    className: 'p-2 bg-orange-50 rounded text-xs'
                },
                    React.createElement('div', { className: 'font-medium' }, 'System Health:'),
                    React.createElement('div', { className: 'text-orange-700' }, `Status: ${systemHealthData.status}`),
                    systemHealthData.database && React.createElement('div', { className: 'text-gray-600' }, `Database: ${systemHealthData.database.status} (${systemHealthData.database.file_size_mb?.toFixed(2) || 0} MB)`),
                    systemHealthData.performance && React.createElement('div', { className: 'text-gray-600' }, `Performance: ${systemHealthData.performance.status} (${systemHealthData.performance.total_searches || 0} searches)`),
                    systemHealthData.cache && React.createElement('div', { className: 'text-gray-600' }, `Cache: ${systemHealthData.cache.status} (${systemHealthData.cache.total_size_mb?.toFixed(2) || 0} MB)`)
                )
            ),

            // Database Optimization
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('button', {
                    className: `w-full btn-sm ${loading ? 'btn-secondary opacity-50' : 'btn-outline'}`,
                    onClick: optimizeDatabase,
                    disabled: loading
                }, loading ? '🔧 Optimizing...' : '🔧 Optimize Database'),
                
                optimizationResult && React.createElement('div', {
                    className: 'p-2 bg-yellow-50 rounded text-xs'
                },
                    React.createElement('div', { className: 'font-medium' }, 'Optimization Result:'),
                    React.createElement('div', { className: 'text-yellow-700' }, `Success: ${optimizationResult.success ? 'Yes' : 'No'}`),
                    optimizationResult.optimization_result && React.createElement('div', { className: 'text-gray-600' }, `Result: ${JSON.stringify(optimizationResult.optimization_result)}`)
                )
            ),

            // Cache Analytics
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('button', {
                    className: `w-full btn-sm ${loading ? 'btn-secondary opacity-50' : 'btn-outline'}`,
                    onClick: getCacheAnalytics,
                    disabled: loading
                }, loading ? '📈 Getting Analytics...' : '📈 Cache Analytics'),
                
                analyticsData && React.createElement('div', {
                    className: 'p-2 bg-indigo-50 rounded text-xs'
                },
                    React.createElement('div', { className: 'font-medium' }, 'Cache Analytics:'),
                    React.createElement('div', { className: 'text-indigo-700' }, `Total Queries: ${analyticsData.total_queries || 0}`),
                    React.createElement('div', { className: 'text-gray-600' }, `Average Query Time: ${analyticsData.average_query_time_ms?.toFixed(2) || 0} ms`),
                    React.createElement('div', { className: 'text-gray-600' }, `Cache Efficiency: ${analyticsData.cache_efficiency?.toFixed(2) || 0}%`)
                )
            ),

            // Monitoring Data
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('button', {
                    className: `w-full btn-sm ${loading ? 'btn-secondary opacity-50' : 'btn-outline'}`,
                    onClick: getMonitoringData,
                    disabled: loading
                }, loading ? '📊 Getting Monitoring...' : '📊 Monitoring Data'),
                
                monitoringData && React.createElement('div', {
                    className: 'p-2 bg-teal-50 rounded text-xs'
                },
                    React.createElement('div', { className: 'font-medium' }, 'Monitoring Data:'),
                    React.createElement('div', { className: 'text-teal-700' }, `Active Sessions: ${monitoringData.active_sessions || 0}`),
                    React.createElement('div', { className: 'text-gray-600' }, `Memory Usage: ${monitoringData.memory_usage_mb?.toFixed(2) || 0} MB`),
                    React.createElement('div', { className: 'text-gray-600' }, `CPU Usage: ${monitoringData.cpu_usage?.toFixed(2) || 0}%`)
                )
            ),

            // Clear All Data
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('button', {
                    className: 'w-full btn-sm btn-outline',
                    onClick: clearAllData
                }, '🗑️ Clear All Data')
            )
        )
    );
};

// Make component globally available
window.DevelopmentToolsPanel = DevelopmentToolsPanel; 