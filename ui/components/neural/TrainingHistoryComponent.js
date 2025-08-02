// TrainingHistoryComponent
// Extracted from main.js - Phase 4B

// Training History Component
function TrainingHistoryComponent({ setStatusMessage, loading, setLoading }) {
    const [trainingSessions, setTrainingSessions] = React.useState([]);
    const [configurations, setConfigurations] = React.useState([]);
    const [selectedSession, setSelectedSession] = React.useState(null);
    const [selectedConfiguration, setSelectedConfiguration] = React.useState(null);
    const [activeSubTab, setActiveSubTab] = React.useState('sessions');
    const [filters, setFilters] = React.useState({
        status: '',
        config_size: '',
        device: '',
        date_from: '',
        date_to: '',
        sort_by: 'created_at',
        sort_order: 'desc',
        limit: 20,
        offset: 0
    });
    const [configFilters, setConfigFilters] = React.useState({
        is_default: '',
        limit: 20,
        offset: 0
    });
    const [showConfigModal, setShowConfigModal] = React.useState(false);
    const [editingConfig, setEditingConfig] = React.useState(null);

    // Load data on component mount
    React.useEffect(() => {
        loadTrainingHistory();
        loadConfigurations();
    }, [filters, configFilters]);

    const loadTrainingHistory = async () => {
        try {
            setLoading(true);
            const result = await window.getTrainingHistory(filters);
            setTrainingSessions(result.sessions || []);
        } catch (error) {
            console.error('Failed to load training history:', error);
            setStatusMessage('error', 'Failed to load training history');
        } finally {
            setLoading(false);
        }
    };

    const loadConfigurations = async () => {
        try {
            const result = await window.getNeuralConfigurations(configFilters);
            setConfigurations(result.configurations || []);
        } catch (error) {
            console.error('Failed to load configurations:', error);
            setStatusMessage('error', 'Failed to load configurations');
        }
    };

    const handleDeleteSession = async (sessionId) => {
        try {
            await window.deleteTrainingSession(sessionId);
            setStatusMessage('success', 'Session deleted successfully');
            loadTrainingHistory();
        } catch (error) {
            setStatusMessage('error', 'Failed to delete session');
        }
    };

    const handleDeleteConfiguration = async (configId) => {
        try {
            await window.deleteNeuralConfiguration(configId);
            setStatusMessage('success', 'Configuration deleted successfully');
            loadConfigurations();
        } catch (error) {
            setStatusMessage('error', 'Failed to delete configuration');
        }
    };

    const handleSaveConfiguration = async (config) => {
        try {
            setLoading(true);
            if (editingConfig) {
                await window.updateNeuralConfiguration(editingConfig.config_id, config);
                setStatusMessage('success', 'Configuration updated successfully');
            } else {
                await window.saveNeuralConfiguration(config);
                setStatusMessage('success', 'Configuration saved successfully');
            }
            setShowConfigModal(false);
            setEditingConfig(null);
            loadConfigurations();
        } catch (error) {
            setStatusMessage('error', 'Failed to save configuration');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString();
    };

    const formatDuration = (startTime, endTime) => {
        if (!startTime || !endTime) return 'N/A';
        const start = new Date(startTime);
        const end = new Date(endTime);
        const diff = end - start;
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        return `${minutes}m ${seconds}s`;
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return 'text-green-600 bg-green-100';
            case 'running': return 'text-blue-600 bg-blue-100';
            case 'failed': return 'text-red-600 bg-red-100';
            case 'stopped': return 'text-yellow-600 bg-yellow-100';
            default: return 'text-gray-600 bg-gray-100';
        }
    };

    return React.createElement('div', { className: 'training-history-component' },
        // Header
        React.createElement('div', { className: 'mb-6' },
            React.createElement('h2', { className: 'text-xl font-semibold mb-4 text-purple-700' }, '📚 Training History & Management'),
            React.createElement('p', { className: 'text-gray-600' }, 'View historical training sessions, manage configurations, and analyze performance trends')
        ),

        // Sub-tab Navigation
        React.createElement('div', { className: 'mb-6' },
            React.createElement('div', { className: 'flex border-b border-gray-200' },
                React.createElement('button', {
                    className: `px-4 py-2 ${activeSubTab === 'sessions' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500'}`,
                    onClick: () => setActiveSubTab('sessions')
                }, '📊 Training Sessions'),
                React.createElement('button', {
                    className: `px-4 py-2 ${activeSubTab === 'configurations' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500'}`,
                    onClick: () => setActiveSubTab('configurations')
                }, '⚙️ Configurations')
            )
        ),

        // Training Sessions Tab
        activeSubTab === 'sessions' && React.createElement('div', { className: 'space-y-6' },
            // Filters
            React.createElement('div', { className: 'bg-white rounded-lg shadow-md p-6' },
                React.createElement('h3', { className: 'text-lg font-semibold mb-4 text-gray-800' }, '🔍 Filters & Sorting'),
                React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4' },
                    React.createElement('div', { className: 'space-y-2' },
                        React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Status'),
                        React.createElement('select', {
                            value: filters.status,
                            onChange: (e) => setFilters({...filters, status: e.target.value}),
                            className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                        },
                            React.createElement('option', { value: '' }, 'All Statuses'),
                            React.createElement('option', { value: 'completed' }, 'Completed'),
                            React.createElement('option', { value: 'running' }, 'Running'),
                            React.createElement('option', { value: 'failed' }, 'Failed'),
                            React.createElement('option', { value: 'stopped' }, 'Stopped')
                        )
                    ),
                    React.createElement('div', { className: 'space-y-2' },
                        React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Device'),
                        React.createElement('select', {
                            value: filters.device,
                            onChange: (e) => setFilters({...filters, device: e.target.value}),
                            className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                        },
                            React.createElement('option', { value: '' }, 'All Devices'),
                            React.createElement('option', { value: 'cpu' }, 'CPU'),
                            React.createElement('option', { value: 'gpu' }, 'GPU')
                        )
                    ),
                    React.createElement('div', { className: 'space-y-2' },
                        React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Sort By'),
                        React.createElement('select', {
                            value: filters.sort_by,
                            onChange: (e) => setFilters({...filters, sort_by: e.target.value}),
                            className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                        },
                            React.createElement('option', { value: 'created_at' }, 'Creation Date'),
                            React.createElement('option', { value: 'progress' }, 'Progress'),
                            React.createElement('option', { value: 'status' }, 'Status')
                        )
                    ),
                    React.createElement('div', { className: 'space-y-2' },
                        React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Sort Order'),
                        React.createElement('select', {
                            value: filters.sort_order,
                            onChange: (e) => setFilters({...filters, sort_order: e.target.value}),
                            className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                        },
                            React.createElement('option', { value: 'desc' }, 'Descending'),
                            React.createElement('option', { value: 'asc' }, 'Ascending')
                        )
                    )
                )
            ),

            // Sessions List
            React.createElement('div', { className: 'bg-white rounded-lg shadow-md' },
                React.createElement('div', { className: 'p-6 border-b border-gray-200' },
                    React.createElement('h3', { className: 'text-lg font-semibold text-gray-800' }, 'Training Sessions')
                ),
                React.createElement('div', { className: 'overflow-x-auto' },
                    React.createElement('table', { className: 'min-w-full divide-y divide-gray-200' },
                        React.createElement('thead', { className: 'bg-gray-50' },
                            React.createElement('tr', {},
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Session ID'),
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Status'),
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Progress'),
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Device'),
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Created'),
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Duration'),
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Actions')
                            )
                        ),
                        React.createElement('tbody', { className: 'bg-white divide-y divide-gray-200' },
                            trainingSessions.map(session => 
                                React.createElement('tr', { key: session.session_id, className: 'hover:bg-gray-50' },
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900' }, 
                                        session.session_id?.substring(0, 8) || 'N/A'
                                    ),
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap' },
                                        React.createElement('span', { 
                                            className: `inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(session.status)}`
                                        }, session.status || 'unknown')
                                    ),
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm text-gray-500' },
                                        session.progress !== undefined ? `${session.progress}%` : 'N/A'
                                    ),
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm text-gray-500' }, 
                                        session.device || 'N/A'
                                    ),
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm text-gray-500' }, 
                                        formatDate(session.created_at)
                                    ),
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm text-gray-500' }, 
                                        formatDuration(session.created_at, session.completed_at)
                                    ),
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm font-medium' },
                                        React.createElement('div', { className: 'flex space-x-2' },
                                            React.createElement('button', {
                                                onClick: () => setSelectedSession(session),
                                                className: 'text-purple-600 hover:text-purple-900'
                                            }, 'View'),
                                            React.createElement('button', {
                                                onClick: () => handleDeleteSession(session.session_id),
                                                className: 'text-red-600 hover:text-red-900'
                                            }, 'Delete')
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),

        // Configurations Tab
        activeSubTab === 'configurations' && React.createElement('div', { className: 'space-y-6' },
            // Configuration Management Header
            React.createElement('div', { className: 'bg-white rounded-lg shadow-md p-6' },
                React.createElement('div', { className: 'flex justify-between items-center' },
                    React.createElement('h3', { className: 'text-lg font-semibold text-gray-800' }, '⚙️ Configuration Templates'),
                    React.createElement('button', {
                        onClick: () => {
                            setEditingConfig(null);
                            setShowConfigModal(true);
                        },
                        className: 'px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 font-semibold'
                    }, '➕ Add Configuration')
                )
            ),

            // Configurations List
            React.createElement('div', { className: 'bg-white rounded-lg shadow-md' },
                React.createElement('div', { className: 'overflow-x-auto' },
                    React.createElement('table', { className: 'min-w-full divide-y divide-gray-200' },
                        React.createElement('thead', { className: 'bg-gray-50' },
                            React.createElement('tr', {},
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Name'),
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Model Size'),
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Device'),
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Epochs'),
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Default'),
                                React.createElement('th', { className: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Actions')
                            )
                        ),
                        React.createElement('tbody', { className: 'bg-white divide-y divide-gray-200' },
                            configurations.map(config => 
                                React.createElement('tr', { key: config.config_id, className: 'hover:bg-gray-50' },
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900' }, 
                                        config.name || 'Unnamed'
                                    ),
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm text-gray-500' }, 
                                        config.model_size || 'N/A'
                                    ),
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm text-gray-500' }, 
                                        config.device || 'N/A'
                                    ),
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm text-gray-500' }, 
                                        config.epochs || 'N/A'
                                    ),
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm text-gray-500' }, 
                                        config.is_default ? 'Yes' : 'No'
                                    ),
                                    React.createElement('td', { className: 'px-6 py-4 whitespace-nowrap text-sm font-medium' },
                                        React.createElement('div', { className: 'flex space-x-2' },
                                            React.createElement('button', {
                                                onClick: () => {
                                                    setEditingConfig(config);
                                                    setShowConfigModal(true);
                                                },
                                                className: 'text-blue-600 hover:text-blue-900'
                                            }, 'Edit'),
                                            React.createElement('button', {
                                                onClick: () => handleDeleteConfiguration(config.config_id),
                                                className: 'text-red-600 hover:text-red-900'
                                            }, 'Delete')
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),

        // Session Details Modal
        selectedSession && React.createElement('div', { className: 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50' },
            React.createElement('div', { className: 'relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white' },
                React.createElement('div', { className: 'mt-3' },
                    React.createElement('div', { className: 'flex justify-between items-center mb-4' },
                        React.createElement('h3', { className: 'text-lg font-semibold text-gray-900' }, 'Session Details'),
                        React.createElement('button', {
                            onClick: () => setSelectedSession(null),
                            className: 'text-gray-400 hover:text-gray-600'
                        }, '✕')
                    ),
                    React.createElement('div', { className: 'space-y-4' },
                        React.createElement('div', { className: 'grid grid-cols-2 gap-4' },
                            React.createElement('div', {},
                                React.createElement('p', { className: 'text-sm font-medium text-gray-500' }, 'Session ID'),
                                React.createElement('p', { className: 'text-sm text-gray-900' }, selectedSession.session_id)
                            ),
                            React.createElement('div', {},
                                React.createElement('p', { className: 'text-sm font-medium text-gray-500' }, 'Status'),
                                React.createElement('span', { 
                                    className: `inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(selectedSession.status)}`
                                }, selectedSession.status)
                            ),
                            React.createElement('div', {},
                                React.createElement('p', { className: 'text-sm font-medium text-gray-500' }, 'Progress'),
                                React.createElement('p', { className: 'text-sm text-gray-900' }, 
                                    selectedSession.progress !== undefined ? `${selectedSession.progress}%` : 'N/A'
                                )
                            ),
                            React.createElement('div', {},
                                React.createElement('p', { className: 'text-sm font-medium text-gray-500' }, 'Device'),
                                React.createElement('p', { className: 'text-sm text-gray-900' }, selectedSession.device || 'N/A')
                            )
                        ),
                        selectedSession.logs && selectedSession.logs.length > 0 && React.createElement('div', {},
                            React.createElement('p', { className: 'text-sm font-medium text-gray-500 mb-2' }, 'Training Logs'),
                            React.createElement('div', { className: 'bg-gray-100 p-3 rounded text-xs font-mono max-h-32 overflow-y-auto' },
                                selectedSession.logs.map((log, index) => 
                                    React.createElement('div', { key: index, className: 'text-gray-700' }, log)
                                )
                            )
                        ),
                        selectedSession.results && React.createElement('div', {},
                            React.createElement('p', { className: 'text-sm font-medium text-gray-500 mb-2' }, 'Training Results'),
                            React.createElement('div', { className: 'bg-blue-50 p-3 rounded' },
                                React.createElement('p', { className: 'text-sm text-blue-700' }, 
                                    `Final Loss: ${selectedSession.results.final_loss?.toFixed(4) || 'N/A'}`
                                ),
                                React.createElement('p', { className: 'text-sm text-blue-700' }, 
                                    `Evaluation Error: ${selectedSession.results.evaluation_error?.toFixed(4) || 'N/A'}`
                                ),
                                React.createElement('p', { className: 'text-sm text-blue-700' }, 
                                    `Model Path: ${selectedSession.results.model_path || 'N/A'}`
                                )
                            )
                        )
                    )
                )
            )
        ),

        // Configuration Modal
        showConfigModal && React.createElement(window.ConfigurationModal, {
            config: editingConfig,
            onSave: handleSaveConfiguration,
            onCancel: () => {
                setShowConfigModal(false);
                setEditingConfig(null);
            },
            loading
        })
    );
}

// Export for global access
window.TrainingHistoryComponent = TrainingHistoryComponent; 