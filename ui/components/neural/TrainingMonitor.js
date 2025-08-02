// TrainingMonitor Component
// Extracted from main.js - Phase 4A

// Enhanced Training Monitor Component
function TrainingMonitor({ trainingStatus, setStatusMessage, loading, setLoading }) {
    const [allSessions, setAllSessions] = React.useState([]);
    const [allEvaluationSessions, setAllEvaluationSessions] = React.useState([]);
    const [selectedSession, setSelectedSession] = React.useState(null);
    const [selectedEvaluationSession, setSelectedEvaluationSession] = React.useState(null);
    const [refreshInterval, setRefreshInterval] = React.useState(null);
    const [activeTab, setActiveTab] = React.useState('training'); // 'training' or 'evaluation'

    // Load all sessions on mount
    React.useEffect(() => {
        loadAllSessions();
        const interval = setInterval(loadAllSessions, 3000); // Refresh every 3 seconds
        setRefreshInterval(interval);
        
        return () => {
            if (interval) clearInterval(interval);
        };
    }, []);

    const loadAllSessions = async () => {
        try {
            // Load training sessions
            const trainingResult = await window.getAllTrainingSessions();
            setAllSessions(trainingResult.sessions || []);
            
            // Auto-select active training session if none selected
            if (!selectedSession && trainingResult.sessions) {
                const activeSession = trainingResult.sessions.find(s => s.status === 'running');
                if (activeSession) {
                    setSelectedSession(activeSession);
                }
            }
            
            // Load evaluation sessions
            const evaluationResult = await window.getAllEvaluationSessions();
            setAllEvaluationSessions(evaluationResult.sessions || []);
            
            // Auto-select active evaluation session if none selected
            if (!selectedEvaluationSession && evaluationResult.sessions) {
                const activeEvaluationSession = evaluationResult.sessions.find(s => s.status === 'running');
                if (activeEvaluationSession) {
                    setSelectedEvaluationSession(activeEvaluationSession);
                }
            }
        } catch (error) {
            console.error('Failed to load sessions:', error);
        }
    };

    const handleStopSession = async (sessionId) => {
        try {
            await window.stopNeuralTraining(sessionId);
            setStatusMessage('info', 'Training stop requested');
        } catch (error) {
            setStatusMessage('error', 'Failed to stop training');
        }
    };

    const handleDeleteSession = async (sessionId) => {
        try {
            await window.deleteTrainingSession(sessionId);
            setStatusMessage('success', 'Session deleted');
            loadAllSessions();
        } catch (error) {
            setStatusMessage('error', 'Failed to delete session');
        }
    };

    const handleDeleteEvaluationSession = async (sessionId) => {
        try {
            await window.deleteEvaluationSession(sessionId);
            setStatusMessage('success', 'Evaluation session deleted');
            loadAllSessions();
        } catch (error) {
            setStatusMessage('error', 'Failed to delete evaluation session');
        }
    };

    const formatDuration = (startTime, endTime) => {
        const start = new Date(startTime);
        const end = endTime ? new Date(endTime) : new Date();
        const duration = Math.floor((end - start) / 1000);
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        return `${minutes}m ${seconds}s`;
    };

    const formatETA = (estimatedTime) => {
        if (!estimatedTime) return 'Calculating...';
        const minutes = Math.floor(estimatedTime / 60);
        const seconds = Math.floor(estimatedTime % 60);
        return `${minutes}m ${seconds}s`;
    };

    const formatElapsedTime = (elapsedTime) => {
        if (!elapsedTime) return '0s';
        const minutes = Math.floor(elapsedTime / 60);
        const seconds = Math.floor(elapsedTime % 60);
        return `${minutes}m ${seconds}s`;
    };

    return React.createElement('div', { className: 'training-monitor p-4' },
        React.createElement('h2', { className: 'text-xl font-semibold mb-4 text-purple-700' }, 'Live Training & Evaluation Monitor'),
        
        // Tab Navigation
        React.createElement('div', { className: 'flex space-x-1 mb-6' },
            React.createElement('button', {
                className: `px-4 py-2 rounded-t-lg font-medium ${
                    activeTab === 'training' 
                        ? 'bg-purple-600 text-white' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`,
                onClick: () => setActiveTab('training')
            }, `Training Sessions (${allSessions.length})`),
            React.createElement('button', {
                className: `px-4 py-2 rounded-t-lg font-medium ${
                    activeTab === 'evaluation' 
                        ? 'bg-purple-600 text-white' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`,
                onClick: () => setActiveTab('evaluation')
            }, `Evaluation Sessions (${allEvaluationSessions.length})`)
        ),
        
        // Training Sessions Tab
        activeTab === 'training' && React.createElement('div', { className: 'mb-6' },
            React.createElement('h3', { className: 'text-lg font-medium mb-3 text-gray-700' }, 'Training Sessions'),
            allSessions.length === 0 ? 
                React.createElement('div', { className: 'text-gray-500 text-center py-8' }, 'No training sessions found') :
                React.createElement('div', { className: 'space-y-3' },
                    allSessions.map(session => 
                        React.createElement('div', { 
                            key: session.session_id,
                            className: `p-4 border rounded-lg cursor-pointer transition-colors ${
                                selectedSession?.session_id === session.session_id 
                                    ? 'border-purple-500 bg-purple-50' 
                                    : 'border-gray-200 hover:border-purple-300'
                            }`,
                            onClick: () => setSelectedSession(session)
                        },
                            React.createElement('div', { className: 'flex justify-between items-start' },
                                React.createElement('div', { className: 'flex-1' },
                                    React.createElement('div', { className: 'flex items-center space-x-2 mb-2' },
                                        React.createElement('span', { 
                                            className: `px-2 py-1 text-xs rounded-full ${
                                                session.status === 'running' ? 'bg-green-100 text-green-800' :
                                                session.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                                                session.status === 'failed' ? 'bg-red-100 text-red-800' :
                                                'bg-gray-100 text-gray-800'
                                            }`
                                        }, session.status),
                                        React.createElement('span', { className: 'text-sm text-gray-600' }, 
                                            `Session: ${session.session_id.slice(0, 8)}...`
                                        )
                                    ),
                                    React.createElement('div', { className: 'text-sm text-gray-600' },
                                        React.createElement('p', null, `Started: ${new Date(session.start_time).toLocaleString()}`),
                                        session.end_time && React.createElement('p', null, 
                                            `Duration: ${formatDuration(session.start_time, session.end_time)}`
                                        ),
                                        session.estimated_total_time && React.createElement('p', null,
                                            `ETA: ${formatETA(session.estimated_total_time)}`
                                        )
                                    )
                                ),
                                React.createElement('div', { className: 'flex space-x-2' },
                                    session.status === 'running' && React.createElement('button', {
                                        onClick: (e) => {
                                            e.stopPropagation();
                                            handleStopSession(session.session_id);
                                        },
                                        className: 'px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700'
                                    }, 'Stop'),
                                    React.createElement('button', {
                                        onClick: (e) => {
                                            e.stopPropagation();
                                            handleDeleteSession(session.session_id);
                                        },
                                        className: 'px-3 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700'
                                    }, 'Delete')
                                )
                            ),
                            React.createElement('div', { className: 'mt-3' },
                                React.createElement('div', { className: 'w-full bg-gray-200 rounded-full h-2' },
                                    React.createElement('div', { 
                                        className: 'bg-purple-600 h-2 rounded-full transition-all duration-300',
                                        style: { width: `${session.progress || 0}%` }
                                    })
                                ),
                                React.createElement('p', { className: 'text-xs text-gray-600 mt-1' }, 
                                    `${session.progress || 0}% complete`
                                )
                            )
                        )
                    )
                )
        ),

        // Evaluation Sessions Tab
        activeTab === 'evaluation' && React.createElement('div', { className: 'mb-6' },
            React.createElement('h3', { className: 'text-lg font-medium mb-3 text-gray-700' }, 'Evaluation Sessions'),
            allEvaluationSessions.length === 0 ? 
                React.createElement('div', { className: 'text-gray-500 text-center py-8' }, 'No evaluation sessions found') :
                React.createElement('div', { className: 'space-y-3' },
                    allEvaluationSessions.map(session => 
                        React.createElement('div', { 
                            key: session.session_id,
                            className: `p-4 border rounded-lg cursor-pointer transition-colors ${
                                selectedEvaluationSession?.session_id === session.session_id 
                                    ? 'border-purple-500 bg-purple-50' 
                                    : 'border-gray-200 hover:border-purple-300'
                            }`,
                            onClick: () => setSelectedEvaluationSession(session)
                        },
                            React.createElement('div', { className: 'flex justify-between items-start' },
                                React.createElement('div', { className: 'flex-1' },
                                    React.createElement('div', { className: 'flex items-center space-x-2 mb-2' },
                                        React.createElement('span', { 
                                            className: `px-2 py-1 text-xs rounded-full ${
                                                session.status === 'running' ? 'bg-green-100 text-green-800' :
                                                session.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                                                session.status === 'failed' ? 'bg-red-100 text-red-800' :
                                                'bg-gray-100 text-gray-800'
                                            }`
                                        }, session.status),
                                        React.createElement('span', { className: 'text-sm text-gray-600' }, 
                                            `Session: ${session.session_id.slice(0, 8)}...`
                                        )
                                    ),
                                    React.createElement('div', { className: 'text-sm text-gray-600' },
                                        React.createElement('p', null, `Started: ${new Date(session.start_time).toLocaleString()}`),
                                        session.elapsed_time && React.createElement('p', null, 
                                            `Elapsed: ${formatElapsedTime(session.elapsed_time)}`
                                        ),
                                        session.config && React.createElement('p', null,
                                            `Model: ${session.config.model_path || 'Unknown'}`
                                        )
                                    )
                                ),
                                React.createElement('div', { className: 'flex space-x-2' },
                                    React.createElement('button', {
                                        onClick: (e) => {
                                            e.stopPropagation();
                                            handleDeleteEvaluationSession(session.session_id);
                                        },
                                        className: 'px-3 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700'
                                    }, 'Delete')
                                )
                            ),
                            React.createElement('div', { className: 'mt-3' },
                                React.createElement('div', { className: 'w-full bg-gray-200 rounded-full h-2' },
                                    React.createElement('div', { 
                                        className: 'bg-purple-600 h-2 rounded-full transition-all duration-300',
                                        style: { width: `${session.progress || 0}%` }
                                    })
                                ),
                                React.createElement('p', { className: 'text-xs text-gray-600 mt-1' }, 
                                    `${session.progress || 0}% complete`
                                )
                            )
                        )
                    )
                )
        ),

        // Selected Training Session Details
        activeTab === 'training' && selectedSession && React.createElement('div', { className: 'border-t pt-6' },
            React.createElement('h3', { className: 'text-lg font-medium mb-4 text-gray-700' }, 'Training Session Details'),
            
            // Loss Visualization
            selectedSession.loss_history && selectedSession.loss_history.length > 0 && 
            React.createElement('div', { className: 'mb-6' },
                React.createElement('h4', { className: 'text-md font-medium mb-3 text-gray-600' }, 'Training Loss'),
                React.createElement('div', { className: 'bg-white border rounded-lg p-4' },
                    React.createElement('div', { className: 'h-48 flex items-end space-x-1' },
                        selectedSession.loss_history.map((loss, index) => 
                            React.createElement('div', {
                                key: index,
                                className: 'bg-purple-500 rounded-t',
                                style: {
                                    width: '4px',
                                    height: `${Math.max(2, (loss / Math.max(...selectedSession.loss_history)) * 180)}px`
                                }
                            })
                        )
                    ),
                    React.createElement('div', { className: 'flex justify-between text-xs text-gray-500 mt-2' },
                        React.createElement('span', null, 'Epoch 1'),
                        React.createElement('span', null, `Epoch ${selectedSession.loss_history.length}`)
                    )
                )
            ),

            // Resource Monitoring
            (selectedSession.cpu_usage && selectedSession.cpu_usage.length > 0) &&
            React.createElement('div', { className: 'mb-6' },
                React.createElement('h4', { className: 'text-md font-medium mb-3 text-gray-600' }, 'Resource Usage'),
                React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 gap-4' },
                    React.createElement('div', { className: 'bg-white border rounded-lg p-4' },
                        React.createElement('h5', { className: 'text-sm font-medium text-gray-700 mb-2' }, 'CPU Usage'),
                        React.createElement('div', { className: 'flex items-center space-x-2' },
                            React.createElement('div', { className: 'flex-1 bg-gray-200 rounded-full h-2' },
                                React.createElement('div', { 
                                    className: 'bg-blue-500 h-2 rounded-full',
                                    style: { width: `${selectedSession.cpu_usage[selectedSession.cpu_usage.length - 1] || 0}%` }
                                })
                            ),
                            React.createElement('span', { className: 'text-sm text-gray-600' },
                                `${selectedSession.cpu_usage[selectedSession.cpu_usage.length - 1] || 0}%`
                            )
                        )
                    ),
                    React.createElement('div', { className: 'bg-white border rounded-lg p-4' },
                        React.createElement('h5', { className: 'text-sm font-medium text-gray-700 mb-2' }, 'Memory Usage'),
                        React.createElement('div', { className: 'flex items-center space-x-2' },
                            React.createElement('div', { className: 'flex-1 bg-gray-200 rounded-full h-2' },
                                React.createElement('div', { 
                                    className: 'bg-green-500 h-2 rounded-full',
                                    style: { width: `${selectedSession.memory_usage[selectedSession.memory_usage.length - 1] || 0}%` }
                                })
                            ),
                            React.createElement('span', { className: 'text-sm text-gray-600' },
                                `${selectedSession.memory_usage[selectedSession.memory_usage.length - 1] || 0}%`
                            )
                        )
                    )
                )
            ),

            // Training Logs
            selectedSession.logs && selectedSession.logs.length > 0 &&
            React.createElement('div', { className: 'mb-6' },
                React.createElement('h4', { className: 'text-md font-medium mb-3 text-gray-600' }, 'Training Logs'),
                React.createElement('div', { className: 'bg-gray-100 p-4 rounded-lg max-h-48 overflow-y-auto' },
                    selectedSession.logs.map((log, index) => 
                        React.createElement('div', { 
                            key: index, 
                            className: 'text-sm font-mono text-gray-700 mb-1' 
                        }, log)
                    )
                )
            ),

            // Results
            selectedSession.results && 
            React.createElement('div', { className: 'mb-6' },
                React.createElement('h4', { className: 'text-md font-medium mb-3 text-gray-600' }, 'Training Results'),
                React.createElement('div', { className: 'bg-blue-50 border border-blue-200 rounded-lg p-4' },
                    React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 gap-4' },
                        React.createElement('div', null,
                            React.createElement('p', { className: 'text-sm text-blue-700' },
                                `Final Loss: ${selectedSession.results.final_loss?.toFixed(4) || 'N/A'}`
                            ),
                            React.createElement('p', { className: 'text-sm text-blue-700' },
                                `Evaluation Error: ${selectedSession.results.evaluation_error?.toFixed(4) || 'N/A'}`
                            )
                        ),
                        React.createElement('div', null,
                            React.createElement('p', { className: 'text-sm text-blue-700' },
                                `Model Path: ${selectedSession.results.model_path || 'N/A'}`
                            ),
                            React.createElement('p', { className: 'text-sm text-blue-700' },
                                `Config: ${selectedSession.results.config || 'N/A'}`
                            )
                        )
                    )
                )
            )
        ),

        // Selected Evaluation Session Details
        activeTab === 'evaluation' && selectedEvaluationSession && React.createElement('div', { className: 'border-t pt-6' },
            React.createElement('h3', { className: 'text-lg font-medium mb-4 text-gray-700' }, 'Evaluation Session Details'),
            
            // Evaluation Configuration
            selectedEvaluationSession.config && 
            React.createElement('div', { className: 'mb-6' },
                React.createElement('h4', { className: 'text-md font-medium mb-3 text-gray-600' }, 'Evaluation Configuration'),
                React.createElement('div', { className: 'bg-blue-50 border border-blue-200 rounded-lg p-4' },
                    React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 gap-4' },
                        React.createElement('div', null,
                            React.createElement('p', { className: 'text-sm text-blue-700' },
                                `Model: ${selectedEvaluationSession.config.model_path || 'N/A'}`
                            ),
                            React.createElement('p', { className: 'text-sm text-blue-700' },
                                `Device: ${selectedEvaluationSession.config.device || 'N/A'}`
                            ),
                            React.createElement('p', { className: 'text-sm text-blue-700' },
                                `Positions: ${selectedEvaluationSession.config.num_positions || 'N/A'}`
                            )
                        ),
                        React.createElement('div', null,
                            React.createElement('p', { className: 'text-sm text-blue-700' },
                                `Games: ${selectedEvaluationSession.config.num_games || 'N/A'}`
                            ),
                            React.createElement('p', { className: 'text-sm text-blue-700' },
                                `Search Time: ${selectedEvaluationSession.config.search_time || 'N/A'}s`
                            ),
                            React.createElement('p', { className: 'text-sm text-blue-700' },
                                `Max Rollouts: ${selectedEvaluationSession.config.max_rollouts || 'N/A'}`
                            )
                        )
                    )
                )
            ),

            // Evaluation Results
            selectedEvaluationSession.results && 
            React.createElement('div', { className: 'mb-6' },
                React.createElement('h4', { className: 'text-md font-medium mb-3 text-gray-600' }, 'Evaluation Results'),
                React.createElement('div', { className: 'bg-green-50 border border-green-200 rounded-lg p-4' },
                    React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 gap-4' },
                        React.createElement('div', null,
                            React.createElement('p', { className: 'text-sm text-green-700' },
                                `Win Rate: ${(selectedEvaluationSession.results.win_rate * 100).toFixed(1)}%`
                            ),
                            React.createElement('p', { className: 'text-sm text-green-700' },
                                `Position Accuracy: ${(selectedEvaluationSession.results.position_accuracy * 100).toFixed(1)}%`
                            ),
                            React.createElement('p', { className: 'text-sm text-green-700' },
                                `Move Agreement: ${(selectedEvaluationSession.results.move_agreement * 100).toFixed(1)}%`
                            )
                        ),
                        React.createElement('div', null,
                            React.createElement('p', { className: 'text-sm text-green-700' },
                                `Inference Time: ${selectedEvaluationSession.results.inference_time?.toFixed(3) || 'N/A'}ms`
                            ),
                            React.createElement('p', { className: 'text-sm text-green-700' },
                                `Model Parameters: ${selectedEvaluationSession.results.model_parameters?.toLocaleString() || 'N/A'}`
                            ),
                            selectedEvaluationSession.results.comparison_results && 
                            React.createElement('p', { className: 'text-sm text-green-700' },
                                `vs Heuristic: ${(selectedEvaluationSession.results.comparison_results.heuristic_win_rate * 100).toFixed(1)}%`
                            )
                        )
                    )
                )
            ),

            // Error Information
            selectedEvaluationSession.error && 
            React.createElement('div', { className: 'mb-6' },
                React.createElement('h4', { className: 'text-md font-medium mb-3 text-gray-600' }, 'Error Information'),
                React.createElement('div', { className: 'bg-red-50 border border-red-200 rounded-lg p-4' },
                    React.createElement('p', { className: 'text-sm text-red-700' }, selectedEvaluationSession.error)
                )
            )
        )
    );
}

// Export for global access
window.TrainingMonitor = TrainingMonitor; 