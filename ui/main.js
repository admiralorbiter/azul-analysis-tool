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
    PlayerBoard,
    PatternAnalysis,
    ComprehensivePatternAnalysis,
    ScoringOptimizationAnalysis,
    FloorLinePatternAnalysis,
    MoveQualityAnalysis,
    DynamicOptimization,
    CenterPool,
    GameTheoryAnalysis,
    GameTheoryPage
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
    PlayerBoard: window.PlayerBoard || (() => React.createElement('div', null, 'PlayerBoard not loaded')),
    PatternAnalysis: window.PatternAnalysis || (() => React.createElement('div', null, 'PatternAnalysis not loaded')),
    ComprehensivePatternAnalysis: window.ComprehensivePatternAnalysis || (() => React.createElement('div', null, 'ComprehensivePatternAnalysis not loaded')),
    ScoringOptimizationAnalysis: window.ScoringOptimizationAnalysis || (() => React.createElement('div', null, 'ScoringOptimizationAnalysis not loaded')),
    FloorLinePatternAnalysis: window.FloorLinePatternAnalysis || (() => React.createElement('div', null, 'FloorLinePatternAnalysis not loaded')),
    MoveQualityAnalysis: window.MoveQualityAnalysis || (() => React.createElement('div', null, 'MoveQualityAnalysis not loaded')),
    DynamicOptimization: window.DynamicOptimization || (() => React.createElement('div', null, 'DynamicOptimization not loaded')),
    CenterPool: window.CenterPool || (() => React.createElement('div', null, 'CenterPool not loaded')),
    GameTheoryAnalysis: window.GameTheoryAnalysis || (() => React.createElement('div', null, 'GameTheoryAnalysis not loaded')),
    GameTheoryPage: window.GameTheoryPage || (() => React.createElement('div', null, 'GameTheoryPage not loaded'))
};

// Import custom hooks and components
const {
    useGameState,
    useUserActivity,
    useEditMode,
    useAnalysis,
    useConfiguration,
    useKeyboardShortcuts,
    GameHeader,
    GameControls,
    GameBoard,
    StatusBar,
    exportPosition,
    importPosition,
    handleFileImport
} = {
    useGameState: window.useGameState || {},
    useUserActivity: window.useUserActivity || {},
    useEditMode: window.useEditMode || {},
    useAnalysis: window.useAnalysis || {},
    useConfiguration: window.useConfiguration || {},
    useKeyboardShortcuts: window.useKeyboardShortcuts || {},
    GameHeader: window.GameHeader || (() => React.createElement('div', null, 'GameHeader not loaded')),
    GameControls: window.GameControls || (() => React.createElement('div', null, 'GameControls not loaded')),
    GameBoard: window.GameBoard || (() => React.createElement('div', null, 'GameBoard not loaded')),
    StatusBar: window.StatusBar || (() => React.createElement('div', null, 'StatusBar not loaded')),
    exportPosition: window.exportPosition || (() => {}),
    importPosition: window.importPosition || (() => {}),
    handleFileImport: window.handleFileImport || (() => {})
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
            'components/positions/custom-positions.js',
            'components/positions/blocking-test-positions.js',
            'components/positions/scoring-optimization-test-positions.js',
            'components/positions/floor-line-test-positions.js',
            'components/positions/strategic-pattern-test-positions.js',
            'components/positions/ui-testing-positions.js'
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