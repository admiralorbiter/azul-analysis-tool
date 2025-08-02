// NeuralTrainingPage Component
// Extracted from main.js Phase 4D

function NeuralTrainingPage({ 
    loading, setLoading, setStatusMessage,
    trainingConfig, setTrainingConfig,
    neuralExpanded, setNeuralExpanded
}) {
    const [activeTab, setActiveTab] = React.useState('training');
    const [trainingStatus, setTrainingStatus] = React.useState(null);
    const [trainingProgress, setTrainingProgress] = React.useState(null);
    const [availableModels, setAvailableModels] = React.useState([]);
    const [evaluationResults, setEvaluationResults] = React.useState(null);
    const [evaluationConfig, setEvaluationConfig] = React.useState({
        model: '',
        device: 'cpu',
        positions: 50,
        games: 20,
        searchTime: 0.5,
        maxRollouts: 50
    });
    const [comparisonResults, setComparisonResults] = React.useState(null);

    // Load available models on component mount
    React.useEffect(() => {
        loadAvailableModels();
    }, []);

    const loadAvailableModels = async () => {
        try {
            const models = await window.getAvailableModels();
            setAvailableModels(models.models || []);
        } catch (error) {
            console.error('Failed to load models:', error);
            setStatusMessage('error', 'Failed to load available models');
        }
    };

    const handleStartTraining = async () => {
        setLoading(true);
        setTrainingStatus(null);
        try {
            console.log('Starting neural training with config:', trainingConfig);
            const result = await window.startNeuralTraining(trainingConfig);
            console.log('Training result:', result);
            
            if (result.success) {
                setStatusMessage('success', 'Training started in background!');
                setTrainingStatus(result);
                
                // Start polling for status updates
                const sessionId = result.session_id;
                const pollInterval = setInterval(async () => {
                    try {
                        const statusResult = await window.getNeuralTrainingStatus(sessionId);
                        setTrainingStatus(statusResult);
                        
                        if (statusResult.status === 'completed' || statusResult.status === 'failed' || statusResult.status === 'stopped') {
                            clearInterval(pollInterval);
                            setLoading(false);
                            
                            if (statusResult.status === 'completed') {
                                setStatusMessage('success', 'Training completed successfully!');
                            } else if (statusResult.status === 'failed') {
                                setStatusMessage('error', `Training failed: ${statusResult.error || 'Unknown error'}`);
                            } else {
                                setStatusMessage('info', 'Training stopped by user');
                            }
                        }
                    } catch (error) {
                        console.error('Failed to get training status:', error);
                        clearInterval(pollInterval);
                        setLoading(false);
                        setStatusMessage('error', 'Failed to get training status');
                    }
                }, 2000); // Poll every 2 seconds
                
            } else {
                setStatusMessage('error', `Training failed: ${result.message || 'Unknown error'}`);
                setTrainingStatus({ success: false, message: result.message || 'Unknown error' });
                setLoading(false);
            }
        } catch (error) {
            console.error('Failed to start training:', error);
            setTrainingStatus({ success: false, message: error.message || 'Network error' });
            setStatusMessage('error', `Failed to start training: ${error.message || 'Network error'}`);
            setLoading(false);
        }
    };

    const handleEvaluateModel = async (modelConfig) => {
        setLoading(true);
        try {
            const result = await window.evaluateNeuralModel(modelConfig);
            
            // Check if evaluation is running in background
            if (result.background && result.session_id) {
                setStatusMessage('info', 'Evaluation started in background. Monitoring progress...');
                
                // Poll for status updates
                const pollStatus = async () => {
                    try {
                        const status = await window.getEvaluationStatus(result.session_id);
                        
                        if (status.status === 'completed') {
                            setEvaluationResults(status.results);
                            setStatusMessage('success', 'Model evaluation completed');
                            setLoading(false);
                        } else if (status.status === 'failed') {
                            setStatusMessage('error', `Evaluation failed: ${status.error}`);
                            setLoading(false);
                        } else {
                            // Still running, continue polling
                            setTimeout(pollStatus, 2000); // Poll every 2 seconds
                        }
                    } catch (error) {
                        console.error('Failed to get evaluation status:', error);
                        setStatusMessage('error', 'Failed to monitor evaluation progress');
                        setLoading(false);
                    }
                };
                
                // Start polling
                pollStatus();
            } else {
                // Immediate result (shouldn't happen with current implementation)
                setEvaluationResults(result);
                setStatusMessage('success', 'Model evaluation completed');
                setLoading(false);
            }
        } catch (error) {
            console.error('Failed to evaluate model:', error);
            setStatusMessage('error', 'Failed to evaluate model');
            setLoading(false);
        }
    };

    const handleCompareModels = async () => {
        setLoading(true);
        try {
            const results = [];
            for (const model of availableModels) {
                try {
                    const config = {
                        model: model.path,
                        device: evaluationConfig.device,
                        positions: evaluationConfig.positions,
                        games: evaluationConfig.games,
                        searchTime: evaluationConfig.searchTime,
                        maxRollouts: evaluationConfig.maxRollouts
                    };
                    const result = await window.evaluateNeuralModel(config);
                    results.push({
                        model_name: model.name,
                        ...result
                    });
                } catch (error) {
                    console.error(`Failed to evaluate model ${model.name}:`, error);
                }
            }
            setComparisonResults(results);
            setStatusMessage('success', `Comparison completed for ${results.length} models`);
        } catch (error) {
            console.error('Failed to compare models:', error);
            setStatusMessage('error', 'Failed to compare models');
        } finally {
            setLoading(false);
        }
    };

    const handleExportResults = () => {
        if (!evaluationResults) {
            setStatusMessage('error', 'No evaluation results to export');
            return;
        }

        try {
            const exportData = {
                timestamp: new Date().toISOString(),
                model: evaluationConfig.model,
                config: evaluationConfig,
                results: evaluationResults
            };

            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `azul_evaluation_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            setStatusMessage('success', 'Evaluation results exported successfully');
        } catch (error) {
            console.error('Failed to export results:', error);
            setStatusMessage('error', 'Failed to export results');
        }
    };

    return React.createElement('div', { className: 'neural-training-page p-6' },
        // Page Header
        React.createElement('div', { className: 'mb-6' },
            React.createElement('h1', { className: 'text-3xl font-bold text-purple-800 mb-2' }, '🧠 Neural Training Interface'),
            React.createElement('p', { className: 'text-gray-600' }, 'Train, evaluate, and manage neural network models for Azul analysis')
        ),

        // Tab Navigation
        React.createElement('div', { className: 'mb-6' },
            React.createElement('div', { className: 'flex border-b border-gray-200' },
                React.createElement('button', {
                    className: `px-4 py-2 ${activeTab === 'training' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500'}`,
                    onClick: () => setActiveTab('training')
                }, 'Training Configuration'),
                React.createElement('button', {
                    className: `px-4 py-2 ${activeTab === 'monitor' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500'}`,
                    onClick: () => setActiveTab('monitor')
                }, 'Training Monitor'),
                React.createElement('button', {
                    className: `px-4 py-2 ${activeTab === 'evaluation' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500'}`,
                    onClick: () => setActiveTab('evaluation')
                }, 'Model Evaluation'),
                React.createElement('button', {
                    className: `px-4 py-2 ${activeTab === 'history' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500'}`,
                    onClick: () => setActiveTab('history')
                }, 'Training History')
            )
        ),

        // Tab Content
        activeTab === 'training' && React.createElement('div', { className: 'neural-training-config' },
            React.createElement('h2', { className: 'text-xl font-semibold mb-4 text-purple-700' }, 'Training Configuration'),
            React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 gap-4' },
                // Model Configuration
                React.createElement('div', { className: 'space-y-4' },
                    React.createElement('h3', { className: 'font-semibold text-gray-700' }, 'Model Settings'),
                    React.createElement('div', { className: 'space-y-2' },
                        React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Model Size'),
                        React.createElement('select', {
                            value: trainingConfig.modelSize,
                            onChange: (e) => setTrainingConfig({...trainingConfig, modelSize: e.target.value}),
                            className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                        },
                            React.createElement('option', { value: 'small' }, 'Small (Fast)'),
                            React.createElement('option', { value: 'medium' }, 'Medium (Balanced)'),
                            React.createElement('option', { value: 'large' }, 'Large (Accurate)')
                        )
                    ),
                    React.createElement('div', { className: 'space-y-2' },
                        React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Device'),
                        React.createElement('select', {
                            value: trainingConfig.device,
                            onChange: (e) => setTrainingConfig({...trainingConfig, device: e.target.value}),
                            className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                        },
                            React.createElement('option', { value: 'cpu' }, 'CPU'),
                            React.createElement('option', { value: 'gpu' }, 'GPU (if available)')
                        )
                    )
                ),

                // Training Parameters
                React.createElement('div', { className: 'space-y-4' },
                    React.createElement('h3', { className: 'font-semibold text-gray-700' }, 'Training Parameters'),
                    React.createElement('div', { className: 'space-y-2' },
                        React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Epochs'),
                        React.createElement('input', {
                            type: 'number',
                            value: trainingConfig.epochs,
                            onChange: (e) => setTrainingConfig({...trainingConfig, epochs: parseInt(e.target.value)}),
                            min: 1,
                            max: 100,
                            className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                        })
                    ),
                    React.createElement('div', { className: 'space-y-2' },
                        React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Samples'),
                        React.createElement('input', {
                            type: 'number',
                            value: trainingConfig.samples,
                            onChange: (e) => setTrainingConfig({...trainingConfig, samples: parseInt(e.target.value)}),
                            min: 100,
                            max: 10000,
                            className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                        })
                    ),
                    React.createElement('div', { className: 'space-y-2' },
                        React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Batch Size'),
                        React.createElement('input', {
                            type: 'number',
                            value: trainingConfig.batchSize,
                            onChange: (e) => setTrainingConfig({...trainingConfig, batchSize: parseInt(e.target.value)}),
                            min: 1,
                            max: 128,
                            className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                        })
                    ),
                    React.createElement('div', { className: 'space-y-2' },
                        React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Learning Rate'),
                        React.createElement('input', {
                            type: 'number',
                            value: trainingConfig.learningRate,
                            onChange: (e) => setTrainingConfig({...trainingConfig, learningRate: parseFloat(e.target.value)}),
                            step: 0.0001,
                            min: 0.0001,
                            max: 0.1,
                            className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                        })
                    )
                )
            ),

            // Action Buttons
            React.createElement('div', { className: 'mt-6 flex space-x-4' },
                React.createElement('button', {
                    onClick: handleStartTraining,
                    disabled: loading,
                    className: 'px-8 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-200'
                }, loading ? '🚀 Starting Training...' : '🚀 Start Training'),
                React.createElement('button', {
                    onClick: () => window.saveNeuralConfig(trainingConfig),
                    className: 'px-6 py-3 bg-gray-600 text-white rounded-md hover:bg-gray-700 font-semibold'
                }, '💾 Save Configuration')
            ),

            // Training Status Display
            trainingStatus && React.createElement('div', { className: 'mt-4 p-4 bg-green-50 border border-green-200 rounded-md' },
                React.createElement('h4', { className: 'font-semibold text-green-800 mb-2' }, 'Training Status'),
                trainingStatus.status && React.createElement('div', { className: 'mb-3' },
                    React.createElement('div', { className: 'flex items-center justify-between mb-2' },
                        React.createElement('span', { className: 'text-sm font-medium text-gray-700' }, 
                            `Status: ${trainingStatus.status.charAt(0).toUpperCase() + trainingStatus.status.slice(1)}`
                        ),
                        trainingStatus.status === 'running' && React.createElement('button', {
                            onClick: async () => {
                                if (trainingStatus.session_id) {
                                    try {
                                        await window.stopNeuralTraining(trainingStatus.session_id);
                                        setStatusMessage('info', 'Training stop requested');
                                    } catch (error) {
                                        setStatusMessage('error', 'Failed to stop training');
                                    }
                                }
                            },
                            className: 'px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700'
                        }, '⏹️ Stop Training')
                    ),
                    trainingStatus.progress !== undefined && React.createElement('div', { className: 'mb-2' },
                        React.createElement('div', { className: 'w-full bg-gray-200 rounded-full h-2' },
                            React.createElement('div', { 
                                className: 'bg-purple-600 h-2 rounded-full transition-all duration-300',
                                style: { width: `${trainingStatus.progress}%` }
                            })
                        ),
                        React.createElement('p', { className: 'text-xs text-gray-600 mt-1' }, 
                            `${trainingStatus.progress}% complete`
                        )
                    )
                ),
                trainingStatus.logs && trainingStatus.logs.length > 0 && React.createElement('div', { className: 'mt-3' },
                    React.createElement('h5', { className: 'text-sm font-medium text-gray-700 mb-2' }, 'Training Logs'),
                    React.createElement('div', { className: 'bg-gray-100 p-3 rounded text-xs font-mono max-h-32 overflow-y-auto' },
                        trainingStatus.logs.map((log, index) => 
                            React.createElement('div', { key: index, className: 'text-gray-700' }, log)
                        )
                    )
                ),
                trainingStatus.results && React.createElement('div', { className: 'mt-3 p-3 bg-blue-50 rounded' },
                    React.createElement('h5', { className: 'text-sm font-medium text-blue-800 mb-2' }, 'Training Results'),
                    React.createElement('div', { className: 'text-sm text-blue-700' },
                        React.createElement('p', null, `Final Loss: ${trainingStatus.results.final_loss?.toFixed(4) || 'N/A'}`),
                        React.createElement('p', null, `Evaluation Error: ${trainingStatus.results.evaluation_error?.toFixed(4) || 'N/A'}`),
                        React.createElement('p', null, `Model Path: ${trainingStatus.results.model_path || 'N/A'}`)
                    )
                ),
                trainingStatus.error && React.createElement('div', { className: 'mt-3 p-3 bg-red-50 rounded' },
                    React.createElement('h5', { className: 'text-sm font-medium text-red-800 mb-2' }, 'Training Error'),
                    React.createElement('p', { className: 'text-sm text-red-700' }, trainingStatus.error)
                )
            ),

            // Important Note
            React.createElement('div', { className: 'mt-4 p-4 bg-blue-50 border border-blue-200 rounded-md' },
                React.createElement('h4', { className: 'font-semibold text-blue-800 mb-2' }, 'ℹ️ Training Information'),
                React.createElement('p', { className: 'text-blue-700 text-sm' }, 
                    'Training now runs in the background. You can monitor progress and stop training at any time. The server will remain responsive during training.'
                )
            )
        ),

        activeTab === 'monitor' && React.createElement(window.TrainingMonitor, {
            trainingStatus,
            setStatusMessage,
            loading,
            setLoading
        }),

        activeTab === 'evaluation' && React.createElement('div', { className: 'model-evaluator' },
            React.createElement('h2', { className: 'text-xl font-semibold mb-4 text-purple-700' }, 'Model Evaluation'),
            
            // Model Selection and Configuration
            React.createElement('div', { className: 'grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6' },
                // Model Selection Panel
                React.createElement('div', { className: 'bg-white rounded-lg shadow-md p-6' },
                    React.createElement('h3', { className: 'text-lg font-semibold mb-4 text-gray-800' }, '📋 Model Selection'),
                    React.createElement('div', { className: 'space-y-4' },
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Select Model'),
                            React.createElement('select', {
                                value: evaluationConfig.model || '',
                                onChange: (e) => setEvaluationConfig({...evaluationConfig, model: e.target.value}),
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            },
                                React.createElement('option', { value: '' }, 'Choose a model...'),
                                availableModels.map(model => 
                                    React.createElement('option', { 
                                        key: model.name, 
                                        value: model.path 
                                    }, `${model.name} (${model.size_mb}MB)`)
                                )
                            )
                        ),
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Device'),
                            React.createElement('select', {
                                value: evaluationConfig.device || 'cpu',
                                onChange: (e) => setEvaluationConfig({...evaluationConfig, device: e.target.value}),
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            },
                                React.createElement('option', { value: 'cpu' }, 'CPU'),
                                React.createElement('option', { value: 'gpu' }, 'GPU (if available)')
                            )
                        )
                    )
                ),

                // Evaluation Parameters Panel
                React.createElement('div', { className: 'bg-white rounded-lg shadow-md p-6' },
                    React.createElement('h3', { className: 'text-lg font-semibold mb-4 text-gray-800' }, '⚙️ Evaluation Parameters'),
                    React.createElement('div', { className: 'space-y-4' },
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Test Positions'),
                            React.createElement('input', {
                                type: 'number',
                                value: evaluationConfig.positions || 50,
                                onChange: (e) => setEvaluationConfig({...evaluationConfig, positions: parseInt(e.target.value)}),
                                min: 10,
                                max: 1000,
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            })
                        ),
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Test Games'),
                            React.createElement('input', {
                                type: 'number',
                                value: evaluationConfig.games || 20,
                                onChange: (e) => setEvaluationConfig({...evaluationConfig, games: parseInt(e.target.value)}),
                                min: 5,
                                max: 200,
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            })
                        ),
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Search Time (seconds)'),
                            React.createElement('input', {
                                type: 'number',
                                value: evaluationConfig.searchTime || 0.5,
                                onChange: (e) => setEvaluationConfig({...evaluationConfig, searchTime: parseFloat(e.target.value)}),
                                min: 0.1,
                                max: 5.0,
                                step: 0.1,
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            })
                        ),
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Max Rollouts'),
                            React.createElement('input', {
                                type: 'number',
                                value: evaluationConfig.maxRollouts || 50,
                                onChange: (e) => setEvaluationConfig({...evaluationConfig, maxRollouts: parseInt(e.target.value)}),
                                min: 10,
                                max: 500,
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            })
                        )
                    )
                )
            ),

            // Evaluation Controls
            React.createElement('div', { className: 'mb-6' },
                React.createElement('div', { className: 'flex flex-wrap gap-4' },
                    React.createElement('button', {
                        onClick: () => handleEvaluateModel(evaluationConfig),
                        disabled: loading || !evaluationConfig.model,
                        className: `px-6 py-3 rounded-lg font-semibold text-white transition-colors ${
                            loading || !evaluationConfig.model 
                                ? 'bg-gray-400 cursor-not-allowed' 
                                : 'bg-purple-600 hover:bg-purple-700'
                        }`
                    }, loading ? '🔄 Evaluating...' : '🚀 Start Evaluation'),
                    
                    React.createElement('button', {
                        onClick: () => handleCompareModels(),
                        disabled: loading || availableModels.length < 2,
                        className: `px-6 py-3 rounded-lg font-semibold text-white transition-colors ${
                            loading || availableModels.length < 2
                                ? 'bg-gray-400 cursor-not-allowed' 
                                : 'bg-blue-600 hover:bg-blue-700'
                        }`
                    }, '📊 Compare Models'),
                    
                    React.createElement('button', {
                        onClick: () => handleExportResults(),
                        disabled: !evaluationResults,
                        className: `px-6 py-3 rounded-lg font-semibold text-white transition-colors ${
                            !evaluationResults
                                ? 'bg-gray-400 cursor-not-allowed' 
                                : 'bg-green-600 hover:bg-green-700'
                        }`
                    }, '💾 Export Results')
                )
            ),

            // Evaluation Results Display
            evaluationResults && React.createElement('div', { className: 'bg-white rounded-lg shadow-md p-6 mb-6' },
                React.createElement('h3', { className: 'text-lg font-semibold mb-4 text-gray-800' }, '📊 Evaluation Results'),
                
                // Performance Metrics Grid
                React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6' },
                    // Model Info
                    React.createElement('div', { className: 'bg-blue-50 rounded-lg p-4' },
                        React.createElement('h4', { className: 'font-semibold text-blue-800 mb-2' }, 'Model Information'),
                        React.createElement('div', { className: 'space-y-1 text-sm' },
                            React.createElement('div', { className: 'flex justify-between' },
                                React.createElement('span', { className: 'text-gray-600' }, 'Parameters:'),
                                React.createElement('span', { className: 'font-medium' }, `${evaluationResults.model_parameters?.toLocaleString() || 'N/A'}`)
                            ),
                            React.createElement('div', { className: 'flex justify-between' },
                                React.createElement('span', { className: 'text-gray-600' }, 'Inference Time:'),
                                React.createElement('span', { className: 'font-medium' }, `${evaluationResults.inference_time_ms?.toFixed(2) || 'N/A'} ms`)
                            )
                        )
                    ),

                    // Performance Metrics
                    React.createElement('div', { className: 'bg-green-50 rounded-lg p-4' },
                        React.createElement('h4', { className: 'font-semibold text-green-800 mb-2' }, 'Performance'),
                        React.createElement('div', { className: 'space-y-1 text-sm' },
                            React.createElement('div', { className: 'flex justify-between' },
                                React.createElement('span', { className: 'text-gray-600' }, 'Win Rate:'),
                                React.createElement('span', { className: 'font-medium' }, `${(evaluationResults.win_rate * 100)?.toFixed(1) || 'N/A'}%`)
                            ),
                            React.createElement('div', { className: 'flex justify-between' },
                                React.createElement('span', { className: 'text-gray-600' }, 'Avg Score:'),
                                React.createElement('span', { className: 'font-medium' }, `${evaluationResults.avg_score?.toFixed(2) || 'N/A'}`)
                            ),
                            React.createElement('div', { className: 'flex justify-between' },
                                React.createElement('span', { className: 'text-gray-600' }, 'Avg Search Time:'),
                                React.createElement('span', { className: 'font-medium' }, `${evaluationResults.avg_search_time?.toFixed(3) || 'N/A'}s`)
                            )
                        )
                    ),

                    // Accuracy Metrics
                    React.createElement('div', { className: 'bg-purple-50 rounded-lg p-4' },
                        React.createElement('h4', { className: 'font-semibold text-purple-800 mb-2' }, 'Accuracy'),
                        React.createElement('div', { className: 'space-y-1 text-sm' },
                            React.createElement('div', { className: 'flex justify-between' },
                                React.createElement('span', { className: 'text-gray-600' }, 'Position Accuracy:'),
                                React.createElement('span', { className: 'font-medium' }, `${(evaluationResults.position_accuracy * 100)?.toFixed(1) || 'N/A'}%`)
                            ),
                            React.createElement('div', { className: 'flex justify-between' },
                                React.createElement('span', { className: 'text-gray-600' }, 'Move Agreement:'),
                                React.createElement('span', { className: 'font-medium' }, `${(evaluationResults.move_agreement * 100)?.toFixed(1) || 'N/A'}%`)
                            ),
                            React.createElement('div', { className: 'flex justify-between' },
                                React.createElement('span', { className: 'text-gray-600' }, 'Avg Rollouts:'),
                                React.createElement('span', { className: 'font-medium' }, `${evaluationResults.avg_rollouts?.toFixed(1) || 'N/A'}`)
                            )
                        )
                    )
                ),

                // Comparison Results
                (evaluationResults.vs_heuristic_win_rate !== null || evaluationResults.vs_random_win_rate !== null) && 
                React.createElement('div', { className: 'bg-yellow-50 rounded-lg p-4 mb-4' },
                    React.createElement('h4', { className: 'font-semibold text-yellow-800 mb-2' }, 'Comparison Results'),
                    React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 gap-4' },
                        evaluationResults.vs_heuristic_win_rate !== null && 
                        React.createElement('div', { className: 'text-sm' },
                            React.createElement('div', { className: 'flex justify-between' },
                                React.createElement('span', { className: 'text-gray-600' }, 'vs Heuristic:'),
                                React.createElement('span', { className: 'font-medium' }, `${(evaluationResults.vs_heuristic_win_rate * 100).toFixed(1)}%`)
                            )
                        ),
                        evaluationResults.vs_random_win_rate !== null && 
                        React.createElement('div', { className: 'text-sm' },
                            React.createElement('div', { className: 'flex justify-between' },
                                React.createElement('span', { className: 'text-gray-600' }, 'vs Random:'),
                                React.createElement('span', { className: 'font-medium' }, `${(evaluationResults.vs_random_win_rate * 100).toFixed(1)}%`)
                            )
                        )
                    )
                ),

                // Detailed Results Table
                React.createElement('div', { className: 'overflow-x-auto' },
                    React.createElement('table', { className: 'min-w-full bg-white border border-gray-200 rounded-lg' },
                        React.createElement('thead', { className: 'bg-gray-50' },
                            React.createElement('tr', {},
                                React.createElement('th', { className: 'px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Metric'),
                                React.createElement('th', { className: 'px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Value'),
                                React.createElement('th', { className: 'px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Description')
                            )
                        ),
                        React.createElement('tbody', { className: 'divide-y divide-gray-200' },
                            React.createElement('tr', {},
                                React.createElement('td', { className: 'px-4 py-2 text-sm font-medium text-gray-900' }, 'Model Parameters'),
                                React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, evaluationResults.model_parameters?.toLocaleString() || 'N/A'),
                                React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, 'Total trainable parameters in the model')
                            ),
                            React.createElement('tr', {},
                                React.createElement('td', { className: 'px-4 py-2 text-sm font-medium text-gray-900' }, 'Inference Time'),
                                React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, `${evaluationResults.inference_time_ms?.toFixed(2) || 'N/A'} ms`),
                                React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, 'Average time for single position evaluation')
                            ),
                            React.createElement('tr', {},
                                React.createElement('td', { className: 'px-4 py-2 text-sm font-medium text-gray-900' }, 'Win Rate'),
                                React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, `${(evaluationResults.win_rate * 100)?.toFixed(1) || 'N/A'}%`),
                                React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, 'Self-play win rate in test games')
                            ),
                            React.createElement('tr', {},
                                React.createElement('td', { className: 'px-4 py-2 text-sm font-medium text-gray-900' }, 'Position Accuracy'),
                                React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, `${(evaluationResults.position_accuracy * 100)?.toFixed(1) || 'N/A'}%`),
                                React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, 'Agreement with heuristic evaluation')
                            ),
                            React.createElement('tr', {},
                                React.createElement('td', { className: 'px-4 py-2 text-sm font-medium text-gray-900' }, 'Move Agreement'),
                                React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, `${(evaluationResults.move_agreement * 100)?.toFixed(1) || 'N/A'}%`),
                                React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, 'Agreement with heuristic move selection')
                            )
                        )
                    )
                )
            ),

            // Model Comparison Results
            comparisonResults && comparisonResults.length > 0 && React.createElement('div', { className: 'bg-white rounded-lg shadow-md p-6' },
                React.createElement('h3', { className: 'text-lg font-semibold mb-4 text-gray-800' }, '📊 Model Comparison'),
                React.createElement('div', { className: 'overflow-x-auto' },
                    React.createElement('table', { className: 'min-w-full bg-white border border-gray-200 rounded-lg' },
                        React.createElement('thead', { className: 'bg-gray-50' },
                            React.createElement('tr', {},
                                React.createElement('th', { className: 'px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Model'),
                                React.createElement('th', { className: 'px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Parameters'),
                                React.createElement('th', { className: 'px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Win Rate'),
                                React.createElement('th', { className: 'px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Accuracy'),
                                React.createElement('th', { className: 'px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' }, 'Inference Time')
                            )
                        ),
                        React.createElement('tbody', { className: 'divide-y divide-gray-200' },
                            comparisonResults.map((result, index) => 
                                React.createElement('tr', { key: index },
                                    React.createElement('td', { className: 'px-4 py-2 text-sm font-medium text-gray-900' }, result.model_name || 'Unknown'),
                                    React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, result.model_parameters?.toLocaleString() || 'N/A'),
                                    React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, `${(result.win_rate * 100)?.toFixed(1) || 'N/A'}%`),
                                    React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, `${(result.position_accuracy * 100)?.toFixed(1) || 'N/A'}%`),
                                    React.createElement('td', { className: 'px-4 py-2 text-sm text-gray-500' }, `${result.inference_time_ms?.toFixed(2) || 'N/A'} ms`)
                                )
                            )
                        )
                    )
                )
            )
        ),

        activeTab === 'history' && React.createElement(window.TrainingHistoryComponent, {
            setStatusMessage,
            loading,
            setLoading
        })
    );
} 