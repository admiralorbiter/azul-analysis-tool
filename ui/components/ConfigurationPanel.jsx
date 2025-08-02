// ConfigurationPanel Component
// Extracted from main.js for Phase 3 refactoring

const ConfigurationPanel = ({ 
    loading, setLoading, setStatusMessage,
    databasePath, setDatabasePath,
    modelPath, setModelPath,
    defaultTimeout, setDefaultTimeout,
    defaultDepth, setDefaultDepth,
    defaultRollouts, setDefaultRollouts,
    configExpanded, setConfigExpanded
}) => {
    const [configLoading, setConfigLoading] = React.useState(false);
    
    // Load configuration from localStorage on mount
    React.useEffect(() => {
        const savedConfig = localStorage.getItem('azul_config');
        if (savedConfig) {
            try {
                const config = JSON.parse(savedConfig);
                setDatabasePath(config.databasePath || 'azul_cache.db');
                setModelPath(config.modelPath || 'models/azul_net_small.pth');
                setDefaultTimeout(config.defaultTimeout || 4.0);
                setDefaultDepth(config.defaultDepth || 3);
                setDefaultRollouts(config.defaultRollouts || 100);
            } catch (error) {
                console.error('Failed to load configuration:', error);
            }
        }
    }, [setDatabasePath, setModelPath, setDefaultTimeout, setDefaultDepth, setDefaultRollouts]);
    
    // Save configuration to localStorage
    const saveConfiguration = React.useCallback(() => {
        const config = {
            databasePath,
            modelPath,
            defaultTimeout,
            defaultDepth,
            defaultRollouts
        };
        localStorage.setItem('azul_config', JSON.stringify(config));
        setStatusMessage('Configuration saved');
    }, [databasePath, modelPath, defaultTimeout, defaultDepth, defaultRollouts, setStatusMessage]);
    
    // Test database connection
    const testDatabaseConnection = React.useCallback(async () => {
        setConfigLoading(true);
        try {
            const response = await fetch(`${window.API_CONSTANTS?.API_BASE || '/api/v1'}/health`);
            const data = await response.json();
            if (data.success) {
                setStatusMessage('Database connection successful');
            } else {
                setStatusMessage('Database connection failed');
            }
        } catch (error) {
            setStatusMessage(`Database test failed: ${error.message}`);
        } finally {
            setConfigLoading(false);
        }
    }, [setStatusMessage]);
    
    // Test model loading
    const testModelLoading = React.useCallback(async () => {
        setConfigLoading(true);
        try {
            // This would need a model test endpoint
            setStatusMessage('Model test feature coming soon...');
        } catch (error) {
            setStatusMessage(`Model test failed: ${error.message}`);
        } finally {
            setConfigLoading(false);
        }
    }, [setStatusMessage]);
    
    return React.createElement('div', {
        className: 'analysis-tools'
    },
        React.createElement('h3', {
            className: 'font-medium text-sm mb-3 flex items-center justify-between text-green-700'
        },
            React.createElement('span', null, '⚙️ Configuration'),
            React.createElement('button', {
                className: 'text-xs text-gray-500 hover:text-gray-700',
                onClick: () => setConfigExpanded(!configExpanded)
            }, configExpanded ? '−' : '+')
        ),
        
        configExpanded && React.createElement('div', {
            className: 'space-y-3'
        },
            // Database Configuration
            React.createElement('div', {
                className: 'bg-gray-50 p-3 rounded-lg border border-gray-200'
            },
                React.createElement('h4', {
                    className: 'text-sm font-medium text-gray-700 mb-2'
                }, '💾 Database Settings'),
                
                React.createElement('div', {
                    className: 'space-y-2'
                },
                    React.createElement('div', {
                        className: 'flex items-center space-x-2'
                    },
                        React.createElement('label', {
                            className: 'text-xs text-gray-600 w-20'
                        }, 'Database:'),
                        React.createElement('input', {
                            type: 'text',
                            value: databasePath,
                            onChange: (e) => setDatabasePath(e.target.value),
                            placeholder: 'azul_cache.db',
                            className: 'flex-1 text-xs border border-gray-300 rounded px-2 py-1'
                        }),
                        React.createElement('button', {
                            className: 'btn-sm btn-outline',
                            onClick: testDatabaseConnection,
                            disabled: configLoading
                        }, configLoading ? 'Testing...' : 'Test')
                    )
                )
            ),
            
            // Model Configuration
            React.createElement('div', {
                className: 'bg-gray-50 p-3 rounded-lg border border-gray-200'
            },
                React.createElement('h4', {
                    className: 'text-sm font-medium text-gray-700 mb-2'
                }, '🧠 Neural Model'),
                
                React.createElement('div', {
                    className: 'space-y-2'
                },
                    React.createElement('div', {
                        className: 'flex items-center space-x-2'
                    },
                        React.createElement('label', {
                            className: 'text-xs text-gray-600 w-20'
                        }, 'Model:'),
                        React.createElement('input', {
                            type: 'text',
                            value: modelPath,
                            onChange: (e) => setModelPath(e.target.value),
                            placeholder: 'models/azul_net_small.pth',
                            className: 'flex-1 text-xs border border-gray-300 rounded px-2 py-1'
                        }),
                        React.createElement('button', {
                            className: 'btn-sm btn-outline',
                            onClick: testModelLoading,
                            disabled: configLoading
                        }, configLoading ? 'Testing...' : 'Test')
                    )
                )
            ),
            
            // Default Settings
            React.createElement('div', {
                className: 'bg-gray-50 p-3 rounded-lg border border-gray-200'
            },
                React.createElement('h4', {
                    className: 'text-sm font-medium text-gray-700 mb-2'
                }, '⚙️ Default Settings'),
                
                React.createElement('div', {
                    className: 'space-y-2'
                },
                    // Default Timeout
                    React.createElement('div', {
                        className: 'flex items-center justify-between'
                    },
                        React.createElement('label', {
                            className: 'text-xs text-gray-600'
                        }, 'Timeout (s):'),
                        React.createElement('input', {
                            type: 'range',
                            min: '0.1',
                            max: '10.0',
                            step: '0.1',
                            value: defaultTimeout,
                            onChange: (e) => setDefaultTimeout(parseFloat(e.target.value)),
                            className: 'w-20 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer'
                        }),
                        React.createElement('span', {
                            className: 'text-xs text-gray-700 w-8 text-center'
                        }, defaultTimeout.toFixed(1))
                    ),
                    
                    // Default Depth
                    React.createElement('div', {
                        className: 'flex items-center justify-between'
                    },
                        React.createElement('label', {
                            className: 'text-xs text-gray-600'
                        }, 'Depth:'),
                        React.createElement('input', {
                            type: 'range',
                            min: '1',
                            max: '5',
                            value: defaultDepth,
                            onChange: (e) => setDefaultDepth(parseInt(e.target.value)),
                            className: 'w-20 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer'
                        }),
                        React.createElement('span', {
                            className: 'text-xs text-gray-700 w-4 text-center'
                        }, defaultDepth)
                    ),
                    
                    // Default Rollouts
                    React.createElement('div', {
                        className: 'flex items-center justify-between'
                    },
                        React.createElement('label', {
                            className: 'text-xs text-gray-600'
                        }, 'Rollouts:'),
                        React.createElement('input', {
                            type: 'range',
                            min: '10',
                            max: '1000',
                            step: '10',
                            value: defaultRollouts,
                            onChange: (e) => setDefaultRollouts(parseInt(e.target.value)),
                            className: 'w-20 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer'
                        }),
                        React.createElement('span', {
                            className: 'text-xs text-gray-700 w-12 text-center'
                        }, defaultRollouts)
                    )
                )
            ),
            
            // Save Configuration Button
            React.createElement('div', {
                className: 'flex space-x-2'
            },
                React.createElement('button', {
                    className: 'btn-sm btn-success flex-1',
                    onClick: saveConfiguration
                }, '💾 Save Config'),
                
                React.createElement('button', {
                    className: 'btn-sm btn-outline flex-1',
                    onClick: () => {
                        // Reset to defaults
                        setDatabasePath('azul_cache.db');
                        setModelPath('models/azul_net_small.pth');
                        setDefaultTimeout(4.0);
                        setDefaultDepth(3);
                        setDefaultRollouts(100);
                        setStatusMessage('Configuration reset to defaults');
                    }
                }, '🔄 Reset')
            )
        )
    );
};

// Make component globally available
window.ConfigurationPanel = ConfigurationPanel; 