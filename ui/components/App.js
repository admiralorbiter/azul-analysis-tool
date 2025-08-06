// App.js - Main App component (Refactored)
const { useState, useEffect, useCallback } = React;

// Import custom hooks
const useGameState = window.useGameState;
const useUserActivity = window.useUserActivity;
const useEditMode = window.useEditMode;
const useAnalysis = window.useAnalysis;
const useConfiguration = window.useConfiguration;
const useKeyboardShortcuts = window.useKeyboardShortcuts;

// Import game components
const GameHeader = window.GameHeader;
const GameControls = window.GameControls;
const GameBoard = window.GameBoard;
const StatusBar = window.StatusBar;

// Import utility functions
const { exportPosition, importPosition, handleFileImport } = window.positionUtils || {};

// Import all component dependencies from window
const Router = window.Router;
const Navigation = window.Navigation;
const BoardEditor = window.BoardEditor;
const PositionLibrary = window.PositionLibrary;
const ContextMenu = window.ContextMenu;
const NeuralTrainingPage = window.NeuralTrainingPage;
const TestMoveQualityPage = window.TestMoveQualityPage;
const PerformanceAnalytics = window.PerformanceAnalytics;
const AdvancedAnalysisLab = window.AdvancedAnalysisLab;
const TacticalTrainingCenter = window.TacticalTrainingCenter;

// Import API dependencies from window
const defaultGameAPI = window.gameAPI || {};
const defaultNeuralAPI = window.neuralAPI || {};
const {
    analyzePosition = () => {},
    getHint = () => {},
    analyzeNeural = () => {},
    analyzeGame = () => {},
    saveGameState = () => Promise.resolve()
} = defaultGameAPI;

function App() {
    // Routing State
    const [currentPage, setCurrentPage] = useState('main');
    
    // Position Library State (R1.2)
    const [showPositionLibrary, setShowPositionLibrary] = useState(false);
    const [positionJustLoaded, setPositionJustLoaded] = useState(false);
    
    // Context menu state
    const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, options: [] });
    
    // Initialize custom hooks
    const gameStateHook = useGameState();
    const {
        sessionStatus,
        statusMessage,
        setStatusMessage,
        loading,
        setLoading,
        gameState,
        setGameState,
        hasStableState,
        lastStateHash,
        setLastStateHash,
        manualRefresh
    } = gameStateHook;
    
    const editModeHook = useEditMode(gameState, setGameState, setStatusMessage);
    const {
        editMode,
        selectedElements,
        selectedTile,
        setSelectedTile,
        clearSelection,
        handleEditModeToggle,
        handleElementSelect,
        applyTileColor,
        removeSelectedTiles,
        copySelection,
        pasteSelection
    } = editModeHook;
    
    const analysisHook = useAnalysis(gameState, setGameState, setStatusMessage, setLoading);
    const {
        variations,
        setVariations,
        heatmapEnabled,
        setHeatmapEnabled,
        heatmapData,
        setHeatmapData,
        currentPlayer,
        setCurrentPlayer,
        engineThinking,
        moveHistory,
        setMoveHistory,
        handleMoveExecution,
        handlePatternLineDrop,
        handleUndo,
        handleRedo
    } = analysisHook;
    
    const configHook = useConfiguration();
    const {
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
        devToolsExpanded,
        setDevToolsExpanded,
        autoRefreshEnabled,
        setAutoRefreshEnabled,
        trainingConfig,
        setTrainingConfig,
        neuralExpanded,
        setNeuralExpanded
    } = configHook;
    
    // User activity hook
    const userActivityHook = useUserActivity(
        gameState, setGameState, gameStateHook.createStateHash,
        sessionStatus, loading, editMode, positionJustLoaded,
        hasStableState, lastStateHash, autoRefreshEnabled
    );
    const {
        userActive,
        trackUserActivity
    } = userActivityHook;
    
    // Keyboard shortcuts hook
    useKeyboardShortcuts({
        editMode,
        clearSelection,
        handleEditModeToggle,
        handleUndo,
        handleRedo,
        applyTileColor,
        removeSelectedTiles,
        copySelection,
        pasteSelection
    });
    
    // Position export/import functions
    const handleExportPosition = useCallback(() => {
        const message = exportPosition(gameState, moveHistory, currentPlayer);
        if (message) {
            setStatusMessage(message);
        }
    }, [gameState, moveHistory, currentPlayer, setStatusMessage]);
    
    const handleImportPosition = useCallback((file) => {
        importPosition(file, setGameState, setMoveHistory, setCurrentPlayer, setStatusMessage);
    }, [setGameState, setMoveHistory, setCurrentPlayer, setStatusMessage]);
    
    const handleFileImportCallback = useCallback((e) => {
        handleFileImport(e, handleImportPosition);
    }, [handleImportPosition]);
    
    // Context menu functions
    const showContextMenu = useCallback((e, elementType, elementData) => {
        e.preventDefault();
        const options = window.getMenuOptions ? window.getMenuOptions(elementType, elementData) : [];
        setContextMenu({
            visible: true,
            x: e.clientX,
            y: e.clientY,
            options: options
        });
    }, []);
    
    const hideContextMenu = useCallback(() => {
        setContextMenu({ visible: false, x: 0, y: 0, options: [] });
    }, []);
    
    const handleContextMenuAction = useCallback((action) => {
        console.log('Context menu action:', action);
        hideContextMenu();
        setStatusMessage(`Action: ${action}`);
    }, [hideContextMenu, setStatusMessage]);
    
    // Expose functions globally for components
    useEffect(() => {
        window.showContextMenu = showContextMenu;
        window.hideContextMenu = hideContextMenu;
        window.setPositionJustLoaded = setPositionJustLoaded;
    }, [showContextMenu, hideContextMenu, setPositionJustLoaded]);
    
    // Handle clicks outside context menu
    useEffect(() => {
        const handleClickOutside = () => hideContextMenu();
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, [hideContextMenu]);

    // Render tree
    if (!gameState) {
        return React.createElement('div', {
            className: 'flex items-center justify-center min-h-screen'
        },
            React.createElement('div', {
                className: 'text-center'
            },
                React.createElement('h1', {
                    className: 'text-2xl font-bold mb-4'
                }, 'Azul Solver & Analysis Toolkit'),
                React.createElement('div', {
                    className: 'text-center'
                },
                    React.createElement('div', {
                        className: sessionStatus === 'connected' ? 'text-green-600' : 'text-red-600'
                    }, statusMessage)
                )
            )
        );
    }
    
    return React.createElement(Router, {
        currentPage: currentPage,
        onPageChange: setCurrentPage
    },
        React.createElement(Navigation, {
            currentPage: currentPage,
            onPageChange: setCurrentPage
        }),
        
        currentPage === 'main' && React.createElement('div', {
            className: 'min-h-screen bg-gray-100'
        },
            // Header
            React.createElement(GameHeader, {
                editMode: editMode,
                gameState: gameState,
                handleEditModeToggle: handleEditModeToggle,
                showPositionLibrary: showPositionLibrary,
                setShowPositionLibrary: setShowPositionLibrary,
                exportPosition: handleExportPosition,
                handleFileImport: handleFileImportCallback,
                saveGameState: saveGameState,
                setStatusMessage: setStatusMessage
            }),
            
            // Main content - Condensed single-screen layout
            React.createElement('div', {
                className: 'max-w-full mx-auto px-4 py-2',
                onMouseMove: trackUserActivity,
                onClick: trackUserActivity,
                onKeyDown: trackUserActivity
            },
                // Compact status bar
                React.createElement(StatusBar, {
                    sessionStatus: sessionStatus,
                    statusMessage: statusMessage,
                    currentPlayer: currentPlayer,
                    engineThinking: engineThinking,
                    positionJustLoaded: positionJustLoaded,
                    userActive: userActive,
                    autoRefreshEnabled: autoRefreshEnabled,
                    moveHistory: moveHistory,
                    manualRefresh: manualRefresh,
                    loading: loading,
                    gameState: gameState
                }),
                
                // Enhanced Board Editor (R1.1) - appears when edit mode is enabled
                editMode && BoardEditor && React.createElement(BoardEditor, {
                    gameState: gameState,
                    setGameState: setGameState,
                    editMode: editMode,
                    selectedElements: selectedElements,
                    onElementSelect: handleElementSelect,
                    setStatusMessage: setStatusMessage,
                    sessionToken: window.sessionStorage?.getItem('sessionToken') || null
                }),
                
                // Position Library (R1.2) - appears when library is opened
                showPositionLibrary && PositionLibrary && React.createElement(PositionLibrary, {
                    gameState: gameState,
                    setGameState: setGameState,
                    setStatusMessage: setStatusMessage,
                    sessionToken: window.sessionStorage?.getItem('sessionToken') || null,
                    onClose: () => setShowPositionLibrary(false)
                }),
                
                // Main game layout - 2 columns: Controls | Game Board
                React.createElement('div', {
                    className: 'flex gap-4 h-[calc(100vh-200px)]'
                },
                    // Left Sidebar - Unified Controls Panel (25% width)
                    React.createElement(GameControls, {
                        // Analysis state
                        variations: variations,
                        loading: loading,
                        engineThinking: engineThinking,
                        setVariations: setVariations,
                        setHeatmapData: setHeatmapData,
                        setStatusMessage: setStatusMessage,
                        moveHistory: moveHistory,
                        depth: analysisHook.depth,
                        setDepth: analysisHook.setDepth,
                        timeBudget: analysisHook.timeBudget,
                        setTimeBudget: analysisHook.setTimeBudget,
                        rollouts: analysisHook.rollouts,
                        setRollouts: analysisHook.setRollouts,
                        agentId: analysisHook.agentId,
                        setAgentId: analysisHook.setAgentId,
                        
                        // Analysis functions
                        analyzePosition: analyzePosition,
                        getHint: getHint,
                        analyzeNeural: analyzeNeural,
                        analyzeGame: analyzeGame,
                        
                        // Game state
                        gameState: gameState,
                        currentPlayer: currentPlayer,
                        
                        // Configuration state
                        databasePath: databasePath,
                        setDatabasePath: setDatabasePath,
                        modelPath: modelPath,
                        setModelPath: setModelPath,
                        defaultTimeout: defaultTimeout,
                        setDefaultTimeout: setDefaultTimeout,
                        defaultDepth: defaultDepth,
                        setDefaultDepth: setDefaultDepth,
                        defaultRollouts: defaultRollouts,
                        setDefaultRollouts: setDefaultRollouts,
                        configExpanded: configExpanded,
                        setConfigExpanded: setConfigExpanded,
                        
                        // Development tools state
                        devToolsExpanded: devToolsExpanded,
                        setDevToolsExpanded: setDevToolsExpanded,
                        
                        // Auto-refresh state
                        autoRefreshEnabled: autoRefreshEnabled,
                        setAutoRefreshEnabled: setAutoRefreshEnabled,
                        
                        // Move controls
                        handleUndo: handleUndo,
                        handleRedo: handleRedo,
                        
                        // Heatmap state
                        heatmapEnabled: heatmapEnabled
                    }),
                    
                    // Right - Game Board (75% width for maximum board space)
                    React.createElement('div', {
                        className: 'relative flex-1'
                    },
                        React.createElement(GameBoard, {
                            gameState: gameState,
                            editMode: editMode,
                            selectedTile: selectedTile,
                            setSelectedTile: setSelectedTile,
                            handleElementSelect: handleElementSelect,
                            selectedElements: selectedElements,
                            heatmapEnabled: heatmapEnabled,
                            heatmapData: heatmapData,
                            handlePatternLineDrop: handlePatternLineDrop,
                            onPlayerSwitch: setCurrentPlayer,
                            currentPlayer: currentPlayer,
                            loading: loading,
                            engineThinking: engineThinking
                        })
                    )
                )
            )
        ),
        
        // Neural Training Page
        currentPage === 'neural' && React.createElement(NeuralTrainingPage, {
            loading: loading,
            setLoading: setLoading,
            setStatusMessage: setStatusMessage,
            trainingConfig: trainingConfig,
            setTrainingConfig: setTrainingConfig,
            neuralExpanded: neuralExpanded,
            setNeuralExpanded: setNeuralExpanded
        }),
        
        // Dynamic Optimization Page
        currentPage === 'dynamic-optimization' && (() => {
            console.log('Dynamic Optimization page selected');
            console.log('window.DynamicOptimization:', window.DynamicOptimization);
            console.log('gameState:', gameState);
            console.log('currentPlayer:', currentPlayer);
            
            if (!window.DynamicOptimization) {
                return React.createElement('div', { className: 'p-4' }, 
                    React.createElement('h2', null, 'Dynamic Optimization'),
                    React.createElement('p', null, 'DynamicOptimization component not loaded. Check console for errors.')
                );
            }
            
            return React.createElement(window.DynamicOptimization, {
                gameState: gameState,
                currentPlayer: currentPlayer,
                onAnalysisComplete: (results) => {
                    setStatusMessage('Dynamic optimization completed');
                    console.log('Dynamic optimization results:', results);
                }
            });
        })(),
        
        // Game Theory Page
        currentPage === 'game-theory' && React.createElement(GameTheoryPage, {
            gameState: gameState,
            setStatusMessage: setStatusMessage
        }),
        
        // Test Move Quality Page
        currentPage === 'test-move-quality' && React.createElement(TestMoveQualityPage, {
            gameState: gameState,
            setStatusMessage: setStatusMessage
        }),
        
        // Performance Analytics Page
        currentPage === 'performance-analytics' && React.createElement(PerformanceAnalytics, {
            gameState: gameState,
            setStatusMessage: setStatusMessage
        }),
        
        // Advanced Analysis Lab Page
        currentPage === 'advanced-analysis' && React.createElement(AdvancedAnalysisLab, {
            gameState: gameState,
            setStatusMessage: setStatusMessage
        }),
        
        // Tactical Training Center Page
        currentPage === 'tactical-training' && React.createElement(TacticalTrainingCenter, {
            gameState: gameState,
            setStatusMessage: setStatusMessage
        }),
        
        // Context menu - moved to correct level
        React.createElement(ContextMenu, {
            visible: contextMenu.visible,
            x: contextMenu.x,
            y: contextMenu.y,
            options: contextMenu.options,
            onAction: handleContextMenuAction,
            onClose: hideContextMenu
        })
    );
}

window.App = App;