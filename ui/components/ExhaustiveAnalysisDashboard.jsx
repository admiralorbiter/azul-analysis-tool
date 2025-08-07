/**
 * Exhaustive Analysis Dashboard Component
 * 
 * Provides a comprehensive interface for the exhaustive search analysis system.
 * Features:
 * - Analysis mode selection (Quick/Standard/Deep/Exhaustive)
 * - Position count configuration
 * - Real-time progress tracking
 * - Analysis results visualization
 * - Database integration
 * - Session management
 * 
 * Version: 1.1.0
 */

const { useState, useEffect, useCallback, useRef } = React;

const ExhaustiveAnalysisDashboard = ({ 
    gameState, 
    setStatusMessage,
    className = '' 
}) => {
    // API (fallback to mock if backend not available)
    const api = (window.exhaustiveAnalysisAPI && Object.keys(window.exhaustiveAnalysisAPI).length)
        ? window.exhaustiveAnalysisAPI
        : (window.exhaustiveAnalysisAPI?.mock || {});
    
    // Debug API availability
    console.log('ExhaustiveAnalysisDashboard mounted');
    console.log('API availability:', {
        hasAPI: !!window.exhaustiveAnalysisAPI,
        apiKeys: window.exhaustiveAnalysisAPI ? Object.keys(window.exhaustiveAnalysisAPI) : [],
        hasStartFunction: !!api.startExhaustiveAnalysis,
        hasProgressFunction: !!api.getAnalysisProgress
    });

    // Analysis configuration state
    const [analysisMode, setAnalysisMode] = useState('quick');
    const [positionCount, setPositionCount] = useState(5);
    const [maxWorkers, setMaxWorkers] = useState(8);
    const [sessionId, setSessionId] = useState('');
    const [plannedPositions, setPlannedPositions] = useState(0);
    
    // Analysis state
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisProgress, setAnalysisProgress] = useState({
        currentPosition: 0,
        totalPositions: 0,
        successCount: 0,
        failureCount: 0,
        startTime: null,
        estimatedTimeRemaining: null
    });
    const pollTimerRef = useRef(null);
    
    // Results state
    const [analysisResults, setAnalysisResults] = useState(null);
    const [recentSessions, setRecentSessions] = useState([]);
    const [showResults, setShowResults] = useState(false);
    
    // Error state
    const [error, setError] = useState(null);
    
    // Analysis mode configuration
    const analysisModes = {
        quick: {
            label: 'Quick Analysis',
            description: 'Fast analysis for testing and validation',
            timePerPosition: '5-10s',
            movesPerPosition: 50,
            color: 'bg-green-500',
            icon: '⚡'
        },
        standard: {
            label: 'Standard Analysis',
            description: 'Balanced analysis for general use',
            timePerPosition: '15-30s',
            movesPerPosition: 100,
            color: 'bg-blue-500',
            icon: '📊'
        },
        deep: {
            label: 'Deep Analysis',
            description: 'Detailed analysis for comprehensive study',
            timePerPosition: '30-60s',
            movesPerPosition: 200,
            color: 'bg-purple-500',
            icon: '🔍'
        },
        exhaustive: {
            label: 'Exhaustive Analysis',
            description: 'Maximum depth analysis for critical positions',
            timePerPosition: '60s+',
            movesPerPosition: 500,
            color: 'bg-red-500',
            icon: '🎯'
        }
    };
    
    // Generate session ID
    const generateSessionId = useCallback(() => {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2, 8);
        return `session_${timestamp}_${random}`;
    }, []);

    // Aggregate quality distribution
    const aggregateQualityDistribution = useCallback((analyses) => {
        const agg = { '!!': 0, '!': 0, '=': 0, '?!': 0, '?': 0 };
        if (!Array.isArray(analyses)) return agg;
        analyses.forEach(a => {
            const d = a.quality_distribution || {};
            Object.keys(d).forEach(k => {
                if (agg[k] === undefined) agg[k] = 0;
                agg[k] += Number(d[k] || 0);
            });
        });
        return agg;
    }, []);
    
    // Start analysis
    const startAnalysis = useCallback(async () => {
        if (isAnalyzing) return;
        
        console.log('Starting analysis with config:', { analysisMode, positionCount, maxWorkers });
        
        const session = generateSessionId();
        setSessionId(session);
        setIsAnalyzing(true);
        setError(null);
        setShowResults(false);
        setPlannedPositions(positionCount);
        setAnalysisProgress({
            currentPosition: 0,
            totalPositions: positionCount,
            successCount: 0,
            failureCount: 0,
            startTime: Date.now(),
            estimatedTimeRemaining: null
        });
        
        setStatusMessage(`🚀 Starting ${analysisMode} analysis with ${positionCount} positions...`);
        
        try {
            // Start backend session
            console.log('Calling startExhaustiveAnalysis API...');
            if (api.startExhaustiveAnalysis) {
                const startResponse = await api.startExhaustiveAnalysis({
                    mode: analysisMode,
                    positions: positionCount,
                    maxWorkers,
                    sessionId: session
                });
                console.log('Start analysis response:', startResponse);
            } else {
                console.warn('startExhaustiveAnalysis API not available');
            }
            
            // Poll progress
            const poll = async () => {
                try {
                    console.log('Polling progress for session:', session);
                    if (!api.getAnalysisProgress) {
                        console.warn('getAnalysisProgress API not available');
                        return; // Fallback if API not available
                    }
                    const progress = await api.getAnalysisProgress(session);
                    const analyzed = progress.positions_analyzed || 0;
                    const planned = progress.planned_positions || positionCount;
                    const elapsed = progress.elapsed_seconds || ((Date.now() - analysisProgress.startTime) / 1000);
                    const remaining = analyzed > 0 && planned > 0 ? Math.max(0, (elapsed / analyzed) * (planned - analyzed)) : null;
                    
                    console.log('Progress update:', { progress, analyzed, planned, status: progress.status });
                    
                    setAnalysisProgress(prev => ({
                        ...prev,
                        currentPosition: analyzed,
                        totalPositions: planned,
                        successCount: analyzed,
                        estimatedTimeRemaining: remaining ? remaining.toFixed(1) : null
                    }));
                    
                    // Check for completion: either status is completed, or we've analyzed all planned positions (when planned > 0)
                    if (progress.status === 'completed' || (planned > 0 && analyzed >= planned)) {
                        console.log('Analysis completed! Status:', progress.status, 'Analyzed:', analyzed, 'Planned:', planned);
                        if (pollTimerRef.current) {
                            clearInterval(pollTimerRef.current);
                            pollTimerRef.current = null;
                        }
                        console.log('Fetching analysis results...');
                        // Fetch results & stats
                        let sessionData = null;
                        if (api.getAnalysisResults) {
                            const res = await api.getAnalysisResults(session);
                            sessionData = res.session || res; // support both shapes
                            console.log('Session data:', sessionData);
                        }
                        let stats = null;
                        if (api.getSessionStats) {
                            stats = await api.getSessionStats(session);
                            console.log('Session stats:', stats);
                        }
                        const positionsAnalyzed = stats?.positions_analyzed ?? analyzed;
                        const totalMoves = stats?.total_moves_analyzed ?? 0;
                        const totalTime = sessionData?.total_analysis_time ?? 0;
                        const avgTimePerPos = positionsAnalyzed > 0 ? (totalTime / positionsAnalyzed) : 0;
                        const dist = aggregateQualityDistribution(sessionData?.analyses || []);
                        const successRate = planned > 0 ? ((positionsAnalyzed / planned) * 100) : 0;
                        
                        const results = {
                            session_id: session,
                            mode: analysisMode,
                            positions_analyzed: positionsAnalyzed,
                            total_moves_analyzed: totalMoves,
                            total_analysis_time: totalTime,
                            average_time_per_position: avgTimePerPos,
                            success_rate: Math.round(successRate),
                            average_moves_per_position: positionsAnalyzed > 0 ? Math.round(totalMoves / positionsAnalyzed) : 0,
                            engine_stats: sessionData?.engine_stats || {},
                            quality_distribution: dist
                        };
                        console.log('Setting analysis results:', results);
                        setAnalysisResults(results);
                        setShowResults(true);
                        setIsAnalyzing(false);
                        setStatusMessage('✅ Analysis complete!');
                        // Refresh session list
                        loadRecentSessions();
                    }
                } catch (e) {
                    console.error('Progress poll failed:', e);
                    console.error('Error details:', {
                        message: e.message,
                        stack: e.stack,
                        session: session
                    });
                }
            };
            pollTimerRef.current = setInterval(poll, 1500);
            // Fire first poll immediately
            await poll();
        } catch (err) {
            console.error('Analysis start failed:', err);
            console.error('Error details:', {
                message: err.message,
                stack: err.stack,
                config: { analysisMode, positionCount, maxWorkers }
            });
            setError(`Analysis failed: ${err.message}`);
            setStatusMessage(`❌ Analysis failed: ${err.message}`);
            setIsAnalyzing(false);
        }
    }, [isAnalyzing, analysisMode, positionCount, maxWorkers, generateSessionId, api, aggregateQualityDistribution]);
    
    // Stop analysis
    const stopAnalysis = useCallback(async () => {
        try {
            if (pollTimerRef.current) {
                clearInterval(pollTimerRef.current);
                pollTimerRef.current = null;
            }
            if (api.stopAnalysis && sessionId) {
                await api.stopAnalysis(sessionId);
            }
            setIsAnalyzing(false);
            setStatusMessage('⏹️ Analysis stopped by user.');
        } catch (e) {
            setStatusMessage(`⚠️ Failed to stop: ${e.message}`);
        }
    }, [api, sessionId, setStatusMessage]);
    
    // Load recent sessions
    const loadRecentSessions = useCallback(async () => {
        try {
            if (!api.getRecentSessions) return;
            const res = await api.getRecentSessions(10);
            const sessions = res.sessions || res; // support both shapes
            setRecentSessions(Array.isArray(sessions) ? sessions : []);
        } catch (err) {
            console.error('Failed to load recent sessions:', err);
        }
    }, [api]);
    
    // Check for running sessions and reconnect
    const checkForRunningSessions = useCallback(async () => {
        try {
            if (!api.getRunningSessions) return;
            const res = await api.getRunningSessions();
            const sessions = res.sessions || res; // support both shapes
            
            // Look for any running sessions
            const runningSession = Array.isArray(sessions) && sessions.length > 0 ? sessions[0] : null;
            
            if (runningSession) {
                console.log('Found running session:', runningSession);
                setSessionId(runningSession.session_id);
                setIsAnalyzing(true);
                setAnalysisMode(runningSession.mode || 'quick');
                setPositionCount(runningSession.positions_analyzed || 5);
                
                // Start polling for this session
                const poll = async () => {
                    try {
                        console.log('Polling progress for existing session:', runningSession.session_id);
                        if (!api.getAnalysisProgress) {
                            console.warn('getAnalysisProgress API not available');
                            return;
                        }
                        const progress = await api.getAnalysisProgress(runningSession.session_id);
                        const analyzed = progress.positions_analyzed || 0;
                        const planned = progress.planned_positions || runningSession.positions_analyzed || 5;
                        const elapsed = progress.elapsed_seconds || 0;
                        const remaining = analyzed > 0 && planned > 0 ? Math.max(0, (elapsed / analyzed) * (planned - analyzed)) : null;
                        
                        console.log('Progress update for existing session:', { progress, analyzed, planned, status: progress.status });
                        
                        setAnalysisProgress(prev => ({
                            ...prev,
                            currentPosition: analyzed,
                            totalPositions: planned,
                            successCount: analyzed,
                            estimatedTimeRemaining: remaining ? remaining.toFixed(1) : null
                        }));
                        
                        // Check for completion
                        if (progress.status === 'completed' || (planned > 0 && analyzed >= planned)) {
                            console.log('Existing session completed! Status:', progress.status, 'Analyzed:', analyzed, 'Planned:', planned);
                            if (pollTimerRef.current) {
                                clearInterval(pollTimerRef.current);
                                pollTimerRef.current = null;
                            }
                            console.log('Fetching analysis results for existing session...');
                            
                            // Fetch results & stats
                            let sessionData = null;
                            if (api.getAnalysisResults) {
                                const res = await api.getAnalysisResults(runningSession.session_id);
                                sessionData = res.session || res;
                                console.log('Session data for existing session:', sessionData);
                            }
                            let stats = null;
                            if (api.getSessionStats) {
                                stats = await api.getSessionStats(runningSession.session_id);
                                console.log('Session stats for existing session:', stats);
                            }
                            const positionsAnalyzed = stats?.positions_analyzed ?? analyzed;
                            const totalMoves = stats?.total_moves_analyzed ?? 0;
                            const totalTime = sessionData?.total_analysis_time ?? 0;
                            const avgTimePerPos = positionsAnalyzed > 0 ? (totalTime / positionsAnalyzed) : 0;
                            const dist = aggregateQualityDistribution(sessionData?.analyses || []);
                            const successRate = planned > 0 ? ((positionsAnalyzed / planned) * 100) : 0;
                            
                            const results = {
                                session_id: runningSession.session_id,
                                mode: runningSession.mode || analysisMode,
                                positions_analyzed: positionsAnalyzed,
                                total_moves_analyzed: totalMoves,
                                total_analysis_time: totalTime,
                                average_time_per_position: avgTimePerPos,
                                success_rate: Math.round(successRate),
                                average_moves_per_position: positionsAnalyzed > 0 ? Math.round(totalMoves / positionsAnalyzed) : 0,
                                engine_stats: sessionData?.engine_stats || {},
                                quality_distribution: dist
                            };
                            console.log('Setting analysis results for existing session:', results);
                            setAnalysisResults(results);
                            setShowResults(true);
                            setIsAnalyzing(false);
                            setStatusMessage('✅ Analysis complete!');
                            loadRecentSessions();
                        }
                    } catch (e) {
                        console.error('Progress poll failed for existing session:', e);
                        console.error('Error details:', {
                            message: e.message,
                            stack: e.stack,
                            session: runningSession.session_id
                        });
                    }
                };
                pollTimerRef.current = setInterval(poll, 1500);
                await poll(); // Fire first poll immediately
                setStatusMessage(`🔄 Reconnected to running ${runningSession.mode} analysis (${runningSession.positions_analyzed || 0} positions analyzed)...`);
            }
        } catch (err) {
            console.error('Failed to check for running sessions:', err);
        }
    }, [api, aggregateQualityDistribution, loadRecentSessions]);
    
    // Load recent sessions on mount and cleanup poller on unmount
    useEffect(() => {
        loadRecentSessions();
        checkForRunningSessions(); // Check for running sessions
        
        // Clean up old completed sessions periodically
        const cleanupInterval = setInterval(() => {
            loadRecentSessions();
        }, 30000); // Refresh every 30 seconds
        
        return () => {
            if (pollTimerRef.current) {
                clearInterval(pollTimerRef.current);
                pollTimerRef.current = null;
            }
            clearInterval(cleanupInterval);
        };
    }, [loadRecentSessions, checkForRunningSessions]);
    
    // Calculate progress percentage
    const progressPercentage = analysisProgress.totalPositions > 0 
        ? Math.min(100, (analysisProgress.currentPosition / analysisProgress.totalPositions) * 100) 
        : 0;
    
    const totalDistCount = analysisResults ? Object.values(analysisResults.quality_distribution || {}).reduce((a, b) => a + b, 0) : 0;
    
    return React.createElement('div', {
        className: `exhaustive-analysis-dashboard p-6 bg-white rounded-lg shadow-lg ${className}`
    },
        
        // Header
        React.createElement('div', {
            className: 'mb-6'
        },
            React.createElement('h2', {
                className: 'text-2xl font-bold text-gray-800 mb-2'
            }, '🔬 Exhaustive Search Analysis'),
            React.createElement('p', {
                className: 'text-gray-600'
            }, 'Large-scale analysis of Azul move space with multi-engine evaluation')
        ),
        
        // Configuration Panel
        React.createElement('div', {
            className: 'grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6'
        },
            
            // Analysis Mode Selection
            React.createElement('div', {
                className: 'bg-gray-50 p-4 rounded-lg'
            },
                React.createElement('h3', {
                    className: 'text-lg font-semibold text-gray-800 mb-3'
                }, '📊 Analysis Configuration'),
                
                // Mode Selection
                React.createElement('div', {
                    className: 'mb-4'
                },
                    React.createElement('label', {
                        className: 'block text-sm font-medium text-gray-700 mb-2'
                    }, 'Analysis Mode'),
                    React.createElement('div', {
                        className: 'grid grid-cols-2 gap-2'
                    },
                        Object.entries(analysisModes).map(([mode, config]) =>
                            React.createElement('button', {
                                key: mode,
                                onClick: () => setAnalysisMode(mode),
                                className: `p-3 rounded-lg border-2 transition-colors ${
                                    analysisMode === mode 
                                        ? `${config.color} text-white border-${config.color.split('-')[1]}-600` 
                                        : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'
                                }`
                            },
                                React.createElement('div', {
                                    className: 'flex items-center space-x-2'
                                },
                                    React.createElement('span', {
                                        className: 'text-lg'
                                    }, config.icon),
                                    React.createElement('div', {
                                        className: 'text-left'
                                    },
                                        React.createElement('div', {
                                            className: 'font-medium'
                                        }, config.label),
                                        React.createElement('div', {
                                            className: 'text-xs opacity-75'
                                        }, config.timePerPosition)
                                    )
                                )
                            )
                        )
                    )
                ),
                
                // Position Count
                React.createElement('div', {
                    className: 'mb-4'
                },
                    React.createElement('label', {
                        className: 'block text-sm font-medium text-gray-700 mb-2'
                    }, 'Number of Positions'),
                    React.createElement('input', {
                        type: 'number',
                        min: 1,
                        max: 10000,
                        value: positionCount,
                        onChange: (e) => setPositionCount(parseInt(e.target.value) || 1),
                        className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
                    })
                ),
                
                // Max Workers
                React.createElement('div', {
                    className: 'mb-4'
                },
                    React.createElement('label', {
                        className: 'block text-sm font-medium text-gray-700 mb-2'
                    }, 'Max Workers'),
                    React.createElement('input', {
                        type: 'number',
                        min: 1,
                        max: 16,
                        value: maxWorkers,
                        onChange: (e) => setMaxWorkers(parseInt(e.target.value) || 1),
                        className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
                    })
                ),
                
                // Action Buttons
                React.createElement('div', {
                    className: 'flex space-x-3'
                },
                                         React.createElement('button', {
                         onClick: startAnalysis,
                         disabled: isAnalyzing,
                         className: `px-6 py-2 rounded-lg font-medium transition-colors ${
                             isAnalyzing 
                                 ? 'bg-blue-500 text-white cursor-not-allowed animate-pulse' 
                                 : 'bg-blue-600 text-white hover:bg-blue-700'
                         }`
                     }, isAnalyzing ? '⏳ Analyzing...' : '🚀 Start Analysis'),
                    
                    isAnalyzing && React.createElement('button', {
                        onClick: stopAnalysis,
                        className: 'px-6 py-2 rounded-lg font-medium bg-red-600 text-white hover:bg-red-700 transition-colors'
                    }, '⏹️ Stop')
                )
            ),
            
            // Progress Panel
            React.createElement('div', {
                className: 'bg-gray-50 p-4 rounded-lg'
            },
                React.createElement('h3', {
                    className: 'text-lg font-semibold text-gray-800 mb-3'
                }, '📈 Analysis Progress'),
                
                                 isAnalyzing ? React.createElement('div', {
                     className: 'space-y-4'
                 },
                     // Status Banner
                     React.createElement('div', {
                         className: 'bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4'
                     },
                         React.createElement('div', {
                             className: 'flex items-center space-x-2'
                         },
                             React.createElement('div', {
                                 className: 'animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600'
                             }),
                             React.createElement('span', {
                                 className: 'text-blue-800 font-medium'
                             }, '🔄 Analysis in Progress...'),
                             React.createElement('span', {
                                 className: 'text-blue-600 text-sm'
                             }, `Session: ${sessionId}`)
                         )
                     ),
                     
                     // Progress Bar
                     React.createElement('div', {
                         className: 'w-full bg-gray-200 rounded-full h-4'
                     },
                         React.createElement('div', {
                             className: 'bg-blue-600 h-4 rounded-full transition-all duration-300',
                             style: { width: `${progressPercentage}%` }
                         })
                     ),
                    
                    // Progress Stats
                    React.createElement('div', {
                        className: 'grid grid-cols-2 gap-4 text-sm'
                    },
                        React.createElement('div', {
                            className: 'text-center'
                        },
                            React.createElement('div', {
                                className: 'text-2xl font-bold text-blue-600'
                            }, analysisProgress.currentPosition),
                            React.createElement('div', {
                                className: 'text-gray-600'
                            }, 'Current Position')
                        ),
                        React.createElement('div', {
                            className: 'text-center'
                        },
                            React.createElement('div', {
                                className: 'text-2xl font-bold text-green-600'
                            }, analysisProgress.successCount),
                            React.createElement('div', {
                                className: 'text-gray-600'
                            }, 'Successful')
                        ),
                        React.createElement('div', {
                            className: 'text-center'
                        },
                            React.createElement('div', {
                                className: 'text-2xl font-bold text-purple-600'
                            }, analysisProgress.estimatedTimeRemaining || '--'),
                            React.createElement('div', {
                                className: 'text-gray-600'
                            }, 'Est. Time (s)')
                        )
                    )
                                 ) : React.createElement('div', {
                     className: 'text-center text-gray-500 py-8'
                 },
                     React.createElement('div', {
                         className: 'text-4xl mb-2'
                     }, '⏸️'),
                     React.createElement('p', null, 'No analysis in progress'),
                     showResults && analysisResults && React.createElement('div', {
                         className: 'mt-4 p-3 bg-green-50 border border-green-200 rounded-lg'
                     },
                         React.createElement('div', {
                             className: 'flex items-center space-x-2'
                         },
                             React.createElement('span', {
                                 className: 'text-green-600 text-lg'
                             }, '✅'),
                             React.createElement('span', {
                                 className: 'text-green-800 font-medium'
                             }, 'Analysis Complete!'),
                             React.createElement('span', {
                                 className: 'text-green-600 text-sm'
                             }, `${analysisResults.positions_analyzed} positions analyzed`)
                         )
                     )
                 )
            )
        ),
        
        // Results Panel
        showResults && analysisResults && React.createElement('div', {
            className: 'bg-gray-50 p-4 rounded-lg mb-6'
        },
            React.createElement('h3', {
                className: 'text-lg font-semibold text-gray-800 mb-3'
            }, '📊 Analysis Results'),
            
            React.createElement('div', {
                className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'
            },
                React.createElement('div', {
                    className: 'bg-white p-3 rounded-lg border'
                },
                    React.createElement('div', {
                        className: 'text-2xl font-bold text-blue-600'
                    }, analysisResults.positions_analyzed),
                    React.createElement('div', {
                        className: 'text-sm text-gray-600'
                    }, 'Positions Analyzed')
                ),
                React.createElement('div', {
                    className: 'bg-white p-3 rounded-lg border'
                },
                    React.createElement('div', {
                        className: 'text-2xl font-bold text-green-600'
                    }, `${analysisResults.success_rate}%`),
                    React.createElement('div', {
                        className: 'text-sm text-gray-600'
                    }, 'Success Rate')
                ),
                React.createElement('div', {
                    className: 'bg-white p-3 rounded-lg border'
                },
                    React.createElement('div', {
                        className: 'text-2xl font-bold text-purple-600'
                    }, analysisResults.total_moves_analyzed),
                    React.createElement('div', {
                        className: 'text-sm text-gray-600'
                    }, 'Total Moves')
                ),
                React.createElement('div', {
                    className: 'bg-white p-3 rounded-lg border'
                },
                    React.createElement('div', {
                        className: 'text-2xl font-bold text-orange-600'
                    }, `${(analysisResults.average_time_per_position || 0).toFixed(1)}s`),
                    React.createElement('div', {
                        className: 'text-sm text-gray-600'
                    }, 'Avg Time/Position')
                )
            ),
            
            // Quality Distribution with mini-bars
            React.createElement('div', {
                className: 'mt-4'
            },
                React.createElement('h4', {
                    className: 'text-md font-semibold text-gray-800 mb-2'
                }, 'Quality Distribution'),
                React.createElement('div', {
                    className: 'space-y-2'
                },
                    Object.entries(analysisResults.quality_distribution || {}).map(([tier, count]) => {
                        const percent = totalDistCount > 0 ? Math.round((count / totalDistCount) * 100) : 0;
                        return React.createElement('div', { key: tier },
                            React.createElement('div', { className: 'flex items-center justify-between text-sm text-gray-700' },
                                React.createElement('span', { className: 'font-medium' }, tier),
                                React.createElement('span', null, `${count} (${percent}%)`)
                            ),
                            React.createElement('div', { className: 'w-full bg-gray-200 rounded h-2' },
                                React.createElement('div', { className: 'h-2 rounded bg-blue-500', style: { width: `${percent}%` } })
                            )
                        );
                    })
                )
            )
        ),
        
        // Recent Sessions
        recentSessions.length > 0 && React.createElement('div', {
            className: 'bg-gray-50 p-4 rounded-lg'
        },
            React.createElement('h3', {
                className: 'text-lg font-semibold text-gray-800 mb-3'
            }, '📋 Recent Sessions'),
            
            React.createElement('div', {
                className: 'space-y-2'
            },
                recentSessions.map(session =>
                    React.createElement('div', {
                        key: session.session_id,
                        className: 'bg-white p-3 rounded border flex justify-between items-center'
                    },
                        React.createElement('div', {
                            className: 'flex items-center space-x-3'
                        },
                            React.createElement('span', {
                                className: `px-2 py-1 rounded text-xs font-medium ${
                                    session.mode === 'quick' ? 'bg-green-100 text-green-800' :
                                    session.mode === 'standard' ? 'bg-blue-100 text-blue-800' :
                                    session.mode === 'deep' ? 'bg-purple-100 text-purple-800' :
                                    'bg-red-100 text-red-800'
                                }`
                            }, session.mode),
                            React.createElement('div', {
                                className: 'text-sm'
                            },
                                React.createElement('div', {
                                    className: 'font-medium'
                                }, `${session.positions_analyzed || 0} positions`),
                                React.createElement('div', {
                                    className: 'text-gray-500'
                                }, (session.created_at ? new Date(session.created_at).toLocaleString() : ''))
                            )
                        ),
                        React.createElement('div', {
                            className: 'text-right text-sm'
                        },
                            React.createElement('div', {
                                className: 'font-medium'
                            }, `${Math.round(((session.successful_analyses || 0) / Math.max(1,(session.positions_analyzed || 1))) * 100)}% success`),
                            React.createElement('div', {
                                className: 'text-gray-500'
                            }, `${session.total_analysis_time ? (session.total_analysis_time / 60).toFixed(1) : '0.0'} min`)
                        )
                    )
                )
            )
        ),
        
        // Error Display
        error && React.createElement('div', {
            className: 'bg-red-50 border border-red-200 rounded-lg p-4 mt-4'
        },
            React.createElement('div', {
                className: 'flex items-center space-x-2'
            },
                React.createElement('span', {
                    className: 'text-red-500 text-lg'
                }, '❌'),
                React.createElement('span', {
                    className: 'text-red-800 font-medium'
                }, 'Analysis Error')
            ),
            React.createElement('p', {
                className: 'text-red-700 mt-2'
            }, error)
        )
    );
};

window.ExhaustiveAnalysisDashboard = ExhaustiveAnalysisDashboard;
