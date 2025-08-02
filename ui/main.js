// Main entry point for the React app
// Using global React and ReactDOM from CDN

const { createRoot } = ReactDOM;

// Debug component loading
console.log('Component loading status:', {
    AdvancedAnalysisControls: !!window.AdvancedAnalysisControls,
    ConfigurationPanel: !!window.ConfigurationPanel,
    DevelopmentToolsPanel: !!window.DevelopmentToolsPanel,
    TrainingConfigPanel: !!window.TrainingConfigPanel,
    App: !!window.App
});

// Import components from extracted modules with fallbacks
const {
    ValidationFeedback,
    BoardEditor,
    PositionLibrary,
    PositionPreview,
    AdvancedAnalysisControls,
    ConfigurationPanel,
    DevelopmentToolsPanel,
    TrainingConfigPanel,
    TrainingMonitor,
    TrainingHistoryComponent,
    NeuralTrainingPage,
    Router,
    Navigation,
    Tile,
    Factory,
    PatternLine,
    StatusMessage,
    MoveOption,
    ContextMenu,
    Wall,
    PlayerBoard
} = {
    ValidationFeedback: window.ValidationFeedback || (() => React.createElement('div', null, 'ValidationFeedback not loaded')),
    BoardEditor: window.BoardEditor || (() => React.createElement('div', null, 'BoardEditor not loaded')),
    PositionLibrary: window.PositionLibrary || (() => React.createElement('div', null, 'PositionLibrary not loaded')),
    PositionPreview: window.PositionPreview || (() => React.createElement('div', null, 'PositionPreview not loaded')),
    AdvancedAnalysisControls: window.AdvancedAnalysisControls || (() => React.createElement('div', null, 'AdvancedAnalysisControls not loaded')),
    ConfigurationPanel: window.ConfigurationPanel || (() => React.createElement('div', null, 'ConfigurationPanel not loaded')),
    DevelopmentToolsPanel: window.DevelopmentToolsPanel || (() => React.createElement('div', null, 'DevelopmentToolsPanel not loaded')),
    TrainingConfigPanel: window.TrainingConfigPanel || (() => React.createElement('div', null, 'TrainingConfigPanel not loaded')),
    TrainingMonitor: window.TrainingMonitor || (() => React.createElement('div', null, 'TrainingMonitor not loaded')),
    TrainingHistoryComponent: window.TrainingHistoryComponent || (() => React.createElement('div', null, 'TrainingHistoryComponent not loaded')),
    NeuralTrainingPage: window.NeuralTrainingPage || (() => React.createElement('div', null, 'NeuralTrainingPage not loaded')),
    Router: window.Router || (() => React.createElement('div', null, 'Router not loaded')),
    Navigation: window.Navigation || (() => React.createElement('div', null, 'Navigation not loaded')),
    Tile: window.Tile || (() => React.createElement('div', null, 'Tile not loaded')),
    Factory: window.Factory || (() => React.createElement('div', null, 'Factory not loaded')),
    PatternLine: window.PatternLine || (() => React.createElement('div', null, 'PatternLine not loaded')),
    StatusMessage: window.StatusMessage || (() => React.createElement('div', null, 'StatusMessage not loaded')),
    MoveOption: window.MoveOption || (() => React.createElement('div', null, 'MoveOption not loaded')),
    ContextMenu: window.ContextMenu || (() => React.createElement('div', null, 'ContextMenu not loaded')),
    Wall: window.Wall || (() => React.createElement('div', null, 'Wall not loaded')),
    PlayerBoard: window.PlayerBoard || (() => React.createElement('div', null, 'PlayerBoard not loaded'))
};

// Import App component from window with fallback
const App = window.App || (() => React.createElement('div', null, 'App component not loaded'));

// Load position modules by creating script tags
const loadPositionModules = () => {
    return new Promise((resolve) => {
        const modules = [
            'components/positions/opening-positions.js',
            'components/positions/midgame-positions.js',
            'components/positions/endgame-positions.js',
            'components/positions/educational-positions.js',
            'components/positions/custom-positions.js'
        ];
        
        let loadedCount = 0;
        
        modules.forEach((modulePath) => {
            const script = document.createElement('script');
            script.src = modulePath;
            script.onload = () => {
                loadedCount++;
                console.log(`Loaded: ${modulePath}`);
                if (loadedCount === modules.length) {
                    console.log('All position modules loaded');
                    resolve();
                }
            };
            script.onerror = (error) => {
                console.warn(`Failed to load ${modulePath}:`, error);
                loadedCount++;
                if (loadedCount === modules.length) {
                    console.log('All position modules attempted to load');
                    resolve();
                }
            };
            document.head.appendChild(script);
        });
    });
};

// Load position modules and then render the app
loadPositionModules().then(() => {
    console.log('All position modules loaded, rendering app');
    const root = createRoot(document.getElementById('root'));
    root.render(React.createElement(App));
}).catch(error => {
    console.error('Failed to load position modules:', error);
    // Render app anyway with fallback positions
    const root = createRoot(document.getElementById('root'));
    root.render(React.createElement(App));
});