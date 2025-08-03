// useConfiguration.js - Custom hook for configuration panel state
const { useState } = React;

window.useConfiguration = function useConfiguration() {
    // Configuration Panel State
    const [databasePath, setDatabasePath] = useState('azul_cache.db');
    const [modelPath, setModelPath] = useState('models/azul_net_small.pth');
    const [defaultTimeout, setDefaultTimeout] = useState(4.0);
    const [defaultDepth, setDefaultDepth] = useState(3);
    const [defaultRollouts, setDefaultRollouts] = useState(100);
    const [configExpanded, setConfigExpanded] = useState(false);
    
    // Development Tools Panel State
    const [devToolsExpanded, setDevToolsExpanded] = useState(false);
    
    // Auto-refresh configuration
    const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
    
    // Neural Training State
    const [neuralExpanded, setNeuralExpanded] = useState(false);
    const [trainingConfig, setTrainingConfig] = useState({
        modelSize: 'small',
        device: 'cpu',
        epochs: 5,
        samples: 500,
        batchSize: 16,
        learningRate: 0.001
    });

    return {
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
        
        // Neural training state
        neuralExpanded,
        setNeuralExpanded,
        trainingConfig,
        setTrainingConfig
    };
} 