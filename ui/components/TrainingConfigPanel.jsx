// TrainingConfigPanel Component
// Extracted from main.js for Phase 3 refactoring

const TrainingConfigPanel = ({ 
    loading, setLoading, setStatusMessage,
    trainingConfig, setTrainingConfig,
    neuralExpanded, setNeuralExpanded
}) => {
    // Training configuration state
    const [modelSize, setModelSize] = React.useState('small');
    const [device, setDevice] = React.useState('cpu');
    const [epochs, setEpochs] = React.useState(5);
    const [samples, setSamples] = React.useState(500);
    const [batchSize, setBatchSize] = React.useState(16);
    const [learningRate, setLearningRate] = React.useState(0.001);
    const [availableDevices, setAvailableDevices] = React.useState(['cpu']);

    // Load available devices on component mount
    React.useEffect(() => {
        // For now, we'll assume CPU is always available
        // In a real implementation, this would check for CUDA availability
        setAvailableDevices(['cpu']);
    }, []);

    // Start training function
    const handleStartTraining = React.useCallback(async () => {
        setLoading(true);
        try {
            const config = {
                modelSize,
                device,
                epochs,
                samples,
                batchSize,
                learningRate
            };
            
            const response = await window.startNeuralTraining(config);
            if (response.success) {
                setStatusMessage('Neural training started successfully');
                // Store the session ID for monitoring
                if (response.session_id) {
                    localStorage.setItem('neural_training_session', response.session_id);
                }
            } else {
                setStatusMessage(`Training failed: ${response.error || 'Unknown error'}`);
            }
        } catch (error) {
            setStatusMessage(`Training failed: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [modelSize, device, epochs, samples, batchSize, learningRate, setLoading, setStatusMessage]);

    // Save configuration
    const handleSaveConfig = React.useCallback(async () => {
        try {
            const config = {
                modelSize,
                device,
                epochs,
                samples,
                batchSize,
                learningRate
            };
            
            await window.saveNeuralConfig(config);
            setStatusMessage('Training configuration saved');
        } catch (error) {
            setStatusMessage(`Failed to save config: ${error.message}`);
        }
    }, [modelSize, device, epochs, samples, batchSize, learningRate, setStatusMessage]);

    return React.createElement('div', {
        className: 'neural-training-config'
    },
        React.createElement('h3', {
            className: 'font-medium text-sm mb-3 flex items-center justify-between text-purple-700'
        },
            React.createElement('span', null, '🧠 Neural Training'),
            React.createElement('button', {
                className: 'text-xs text-gray-500 hover:text-gray-700',
                onClick: () => setNeuralExpanded(!neuralExpanded)
            }, neuralExpanded ? '−' : '+')
        ),
        
        // Collapsible neural training content
        neuralExpanded && React.createElement('div', {
            className: 'space-y-3'
        },
            // Model Configuration
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('label', {
                    className: 'block text-xs font-medium text-gray-700'
                }, 'Model Size'),
                React.createElement('select', {
                    className: 'w-full text-sm border border-gray-300 rounded px-2 py-1',
                    value: modelSize,
                    onChange: (e) => setModelSize(e.target.value)
                },
                    React.createElement('option', { value: 'small' }, 'Small (64 hidden, 2 layers)'),
                    React.createElement('option', { value: 'medium' }, 'Medium (128 hidden, 3 layers)'),
                    React.createElement('option', { value: 'large' }, 'Large (256 hidden, 4 layers)')
                )
            ),
            
            // Device Selection
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('label', {
                    className: 'block text-xs font-medium text-gray-700'
                }, 'Device'),
                React.createElement('div', {
                    className: 'flex space-x-2'
                },
                    availableDevices.map(dev => 
                        React.createElement('label', {
                            key: dev,
                            className: 'flex items-center space-x-1'
                        },
                            React.createElement('input', {
                                type: 'radio',
                                name: 'device',
                                value: dev,
                                checked: device === dev,
                                onChange: (e) => setDevice(e.target.value),
                                className: 'text-purple-600'
                            }),
                            React.createElement('span', {
                                className: 'text-xs'
                            }, dev.toUpperCase())
                        )
                    )
                )
            ),
            
            // Training Parameters
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('label', {
                    className: 'block text-xs font-medium text-gray-700'
                }, 'Epochs (1-100)'),
                React.createElement('input', {
                    type: 'range',
                    min: '1',
                    max: '100',
                    value: epochs,
                    onChange: (e) => setEpochs(parseInt(e.target.value)),
                    className: 'w-full'
                }),
                React.createElement('div', {
                    className: 'text-xs text-gray-500'
                }, `${epochs} epochs`)
            ),
            
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('label', {
                    className: 'block text-xs font-medium text-gray-700'
                }, 'Samples (100-10000)'),
                React.createElement('input', {
                    type: 'range',
                    min: '100',
                    max: '10000',
                    step: '100',
                    value: samples,
                    onChange: (e) => setSamples(parseInt(e.target.value)),
                    className: 'w-full'
                }),
                React.createElement('div', {
                    className: 'text-xs text-gray-500'
                }, `${samples.toLocaleString()} samples`)
            ),
            
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('label', {
                    className: 'block text-xs font-medium text-gray-700'
                }, 'Batch Size (8-64)'),
                React.createElement('input', {
                    type: 'range',
                    min: '8',
                    max: '64',
                    step: '8',
                    value: batchSize,
                    onChange: (e) => setBatchSize(parseInt(e.target.value)),
                    className: 'w-full'
                }),
                React.createElement('div', {
                    className: 'text-xs text-gray-500'
                }, `${batchSize} batch size`)
            ),
            
            React.createElement('div', {
                className: 'space-y-2'
            },
                React.createElement('label', {
                    className: 'block text-xs font-medium text-gray-700'
                }, 'Learning Rate (0.0001-0.01)'),
                React.createElement('input', {
                    type: 'range',
                    min: '0.0001',
                    max: '0.01',
                    step: '0.0001',
                    value: learningRate,
                    onChange: (e) => setLearningRate(parseFloat(e.target.value)),
                    className: 'w-full'
                }),
                React.createElement('div', {
                    className: 'text-xs text-gray-500'
                }, `${learningRate.toFixed(4)} learning rate`)
            ),
            
            // Action Buttons
            React.createElement('div', {
                className: 'grid grid-cols-2 gap-2'
            },
                React.createElement('button', {
                    className: `w-full btn-sm ${loading ? 'btn-secondary opacity-50' : 'btn-success'}`,
                    onClick: handleStartTraining,
                    disabled: loading
                }, loading ? '🚀 Starting...' : '🚀 Start Training'),
                
                React.createElement('button', {
                    className: 'w-full btn-sm btn-outline',
                    onClick: handleSaveConfig
                }, '💾 Save Config')
            )
        )
    );
};

// Make component globally available
window.TrainingConfigPanel = TrainingConfigPanel; 