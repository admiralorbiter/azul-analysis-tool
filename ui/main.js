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

// Render the app
const root = createRoot(document.getElementById('root'));
root.render(React.createElement(App));