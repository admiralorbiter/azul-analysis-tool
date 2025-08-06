// Tactical Training Center Component
// Systematic skill improvement through targeted exercises and adaptive training algorithms

const { useState, useEffect, useCallback } = React;

function TacticalTrainingCenter({ gameState, setStatusMessage }) {
    // State for training data
    const [trainingData, setTrainingData] = useState({
        currentPuzzle: null,
        puzzleHistory: [],
        skillRatings: {},
        performanceMetrics: {},
        trainingModules: []
    });
    
    const [selectedModule, setSelectedModule] = useState('pattern-recognition');
    const [difficulty, setDifficulty] = useState('medium');
    const [showHint, setShowHint] = useState(false);
    const [userAnswer, setUserAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('puzzles');
    
    // Mock data for demonstration (replace with real API calls)
    const mockTrainingData = {
        currentPuzzle: {
            id: 1,
            type: 'pattern-recognition',
            difficulty: 'medium',
            position: 'base64_encoded_position_here',
            question: 'Identify the best tactical opportunity in this position',
            hint: 'Look for blocking opportunities and tile placement patterns',
            solution: 'A1-B2',
            explanation: 'This move creates a strong blocking pattern and sets up future scoring opportunities',
            timeLimit: 120,
            points: 50
        },
        puzzleHistory: [
            { id: 1, type: 'pattern-recognition', difficulty: 'medium', result: 'correct', time: 45, points: 50 },
            { id: 2, type: 'move-quality', difficulty: 'hard', result: 'incorrect', time: 120, points: 0 },
            { id: 3, type: 'timing', difficulty: 'easy', result: 'correct', time: 30, points: 30 }
        ],
        skillRatings: {
            patternRecognition: 1250,
            moveQuality: 1180,
            timing: 1320,
            riskAssessment: 1200,
            endgamePlay: 1150
        },
        performanceMetrics: {
            totalPuzzles: 45,
            correctAnswers: 32,
            averageTime: 67,
            accuracyRate: 0.71,
            improvementRate: 0.15
        },
        trainingModules: [
            { id: 'pattern-recognition', name: 'Pattern Recognition', description: 'Identify tactical patterns and opportunities', difficulty: 'medium', progress: 0.75 },
            { id: 'move-quality', name: 'Move Quality Assessment', description: 'Evaluate move quality and strategic value', difficulty: 'hard', progress: 0.45 },
            { id: 'timing', name: 'Timing Optimization', description: 'Master the timing of moves and sequences', difficulty: 'medium', progress: 0.60 },
            { id: 'endgame', name: 'Endgame Practice', description: 'Practice endgame scenarios and counting', difficulty: 'hard', progress: 0.30 }
        ]
    };
    
    // Load training data
    const loadTrainingData = useCallback(async () => {
        setLoading(true);
        try {
            // TODO: Replace with real API call
            // const response = await fetch('/api/v1/training/data', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ module: selectedModule, difficulty: difficulty })
            // });
            // const data = await response.json();
            
            // For now, use mock data
            await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API delay
            setTrainingData(mockTrainingData);
            setStatusMessage('Training data loaded successfully');
        } catch (error) {
            console.error('Error loading training data:', error);
            setStatusMessage('Error loading training data');
        } finally {
            setLoading(false);
        }
    }, [selectedModule, difficulty, setStatusMessage]);
    
    // Load new puzzle
    const loadNewPuzzle = useCallback(async () => {
        setLoading(true);
        try {
            // TODO: Replace with real API call
            // const response = await fetch('/api/v1/training/puzzle', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ module: selectedModule, difficulty: difficulty })
            // });
            // const puzzle = await response.json();
            
            // For now, use mock data
            await new Promise(resolve => setTimeout(resolve, 800)); // Simulate API delay
            setTrainingData(prev => ({
                ...prev,
                currentPuzzle: mockTrainingData.currentPuzzle
            }));
            setUserAnswer('');
            setShowHint(false);
            setStatusMessage('New puzzle loaded');
        } catch (error) {
            console.error('Error loading puzzle:', error);
            setStatusMessage('Error loading puzzle');
        } finally {
            setLoading(false);
        }
    }, [selectedModule, difficulty, setStatusMessage]);
    
    // Submit answer
    const submitAnswer = useCallback(async () => {
        if (!userAnswer.trim()) return;
        
        setLoading(true);
        try {
            // TODO: Replace with real API call
            // const response = await fetch('/api/v1/training/submit', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ 
            //         puzzleId: trainingData.currentPuzzle.id,
            //         answer: userAnswer,
            //         timeSpent: timeSpent
            //     })
            // });
            // const result = await response.json();
            
            // For now, simulate answer checking
            await new Promise(resolve => setTimeout(resolve, 500));
            const isCorrect = userAnswer.toUpperCase() === trainingData.currentPuzzle.solution;
            
            setStatusMessage(isCorrect ? 'Correct! Well done!' : 'Incorrect. Try again!');
            
            if (isCorrect) {
                // Load next puzzle after a delay
                setTimeout(() => loadNewPuzzle(), 2000);
            }
        } catch (error) {
            console.error('Error submitting answer:', error);
            setStatusMessage('Error submitting answer');
        } finally {
            setLoading(false);
        }
    }, [userAnswer, trainingData.currentPuzzle, loadNewPuzzle, setStatusMessage]);
    
    // Load data on component mount and module change
    useEffect(() => {
        loadTrainingData();
    }, [loadTrainingData]);
    
    // Get skill rating color
    const getSkillRatingColor = (rating) => {
        if (rating >= 1300) return 'text-green-600';
        if (rating >= 1200) return 'text-blue-600';
        if (rating >= 1100) return 'text-yellow-600';
        return 'text-red-600';
    };
    
    // Get difficulty color
    const getDifficultyColor = (difficulty) => {
        switch (difficulty) {
            case 'easy': return 'text-green-600';
            case 'medium': return 'text-yellow-600';
            case 'hard': return 'text-red-600';
            default: return 'text-gray-600';
        }
    };
    
    // Render current puzzle
    const renderCurrentPuzzle = () => {
        const puzzle = trainingData.currentPuzzle;
        if (!puzzle) return React.createElement('div', { className: 'text-gray-500' }, 'No puzzle available');
        
        return React.createElement('div', { className: 'bg-white rounded-lg p-6 shadow-sm' },
            React.createElement('div', { className: 'flex items-center justify-between mb-4' },
                React.createElement('h3', { className: 'text-lg font-semibold' }, 'Current Puzzle'),
                React.createElement('div', { className: 'flex items-center space-x-2' },
                    React.createElement('span', { 
                        className: `px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(puzzle.difficulty)}`
                    }, puzzle.difficulty.toUpperCase()),
                    React.createElement('span', { className: 'text-sm text-gray-600' }, `${puzzle.points} pts`)
                )
            ),
            React.createElement('div', { className: 'mb-4' },
                React.createElement('p', { className: 'text-gray-700 mb-2' }, puzzle.question),
                React.createElement('div', { className: 'bg-gray-100 rounded p-4 mb-4' },
                    React.createElement('div', { className: 'text-sm text-gray-600' }, 'Position Preview'),
                    React.createElement('div', { className: 'text-xs text-gray-500 mt-1' }, 'Game board would be displayed here')
                )
            ),
            React.createElement('div', { className: 'space-y-3' },
                React.createElement('div', null,
                    React.createElement('label', { className: 'block text-sm font-medium text-gray-700 mb-1' }, 'Your Answer'),
                    React.createElement('input', {
                        type: 'text',
                        value: userAnswer,
                        onChange: (e) => setUserAnswer(e.target.value),
                        placeholder: 'Enter move (e.g., A1-B2)',
                        className: 'w-full border border-gray-300 rounded px-3 py-2 text-sm'
                    })
                ),
                React.createElement('div', { className: 'flex space-x-2' },
                    React.createElement('button', {
                        onClick: () => setShowHint(!showHint),
                        className: 'px-3 py-2 text-sm text-blue-600 hover:text-blue-700'
                    }, showHint ? 'Hide Hint' : 'Show Hint'),
                    React.createElement('button', {
                        onClick: submitAnswer,
                        disabled: loading || !userAnswer.trim(),
                        className: 'px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50'
                    }, loading ? 'Checking...' : 'Submit Answer')
                ),
                showHint && React.createElement('div', { className: 'p-3 bg-blue-50 rounded' },
                    React.createElement('div', { className: 'text-sm text-blue-800' }, puzzle.hint)
                )
            )
        );
    };
    
    // Render skill ratings
    const renderSkillRatings = () => {
        const ratings = trainingData.skillRatings;
        
        return React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm' },
            React.createElement('h3', { className: 'text-lg font-semibold mb-4' }, 'Skill Ratings'),
            React.createElement('div', { className: 'space-y-3' },
                Object.entries(ratings).map(([skill, rating]) => 
                    React.createElement('div', { key: skill, className: 'flex items-center justify-between' },
                        React.createElement('span', { className: 'text-sm capitalize' }, 
                            skill.replace(/([A-Z])/g, ' $1').trim()
                        ),
                        React.createElement('span', { 
                            className: `text-sm font-medium ${getSkillRatingColor(rating)}`
                        }, rating)
                    )
                )
            )
        );
    };
    
    // Render performance metrics
    const renderPerformanceMetrics = () => {
        const metrics = trainingData.performanceMetrics;
        
        return React.createElement('div', { className: 'grid grid-cols-2 md:grid-cols-4 gap-4 mb-6' },
            React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm' },
                React.createElement('div', { className: 'text-sm text-gray-600' }, 'Total Puzzles'),
                React.createElement('div', { className: 'text-2xl font-bold' }, metrics.totalPuzzles)
            ),
            React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm' },
                React.createElement('div', { className: 'text-sm text-gray-600' }, 'Accuracy Rate'),
                React.createElement('div', { className: 'text-2xl font-bold text-green-600' }, 
                    `${Math.round(metrics.accuracyRate * 100)}%`
                )
            ),
            React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm' },
                React.createElement('div', { className: 'text-sm text-gray-600' }, 'Avg Time'),
                React.createElement('div', { className: 'text-2xl font-bold' }, `${metrics.averageTime}s`)
            ),
            React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm' },
                React.createElement('div', { className: 'text-sm text-gray-600' }, 'Improvement'),
                React.createElement('div', { className: 'text-2xl font-bold text-blue-600' }, 
                    `+${Math.round(metrics.improvementRate * 100)}%`
                )
            )
        );
    };
    
    // Render training modules
    const renderTrainingModules = () => {
        const modules = trainingData.trainingModules;
        
        return React.createElement('div', { className: 'space-y-4' },
            React.createElement('h3', { className: 'text-lg font-semibold mb-4' }, 'Training Modules'),
            modules.map(module => 
                React.createElement('div', {
                    key: module.id,
                    className: 'bg-white rounded-lg p-4 shadow-sm border-l-4 border-blue-500'
                },
                    React.createElement('div', { className: 'flex items-center justify-between mb-2' },
                        React.createElement('h4', { className: 'text-md font-medium' }, module.name),
                        React.createElement('span', { 
                            className: `px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(module.difficulty)}`
                        }, module.difficulty)
                    ),
                    React.createElement('p', { className: 'text-sm text-gray-600 mb-3' }, module.description),
                    React.createElement('div', { className: 'flex items-center justify-between' },
                        React.createElement('div', { className: 'flex-1 mr-3' },
                            React.createElement('div', { className: 'w-full bg-gray-200 rounded-full h-2' },
                                React.createElement('div', {
                                    className: 'bg-blue-500 h-2 rounded-full',
                                    style: { width: `${module.progress * 100}%` }
                                })
                            )
                        ),
                        React.createElement('span', { className: 'text-sm font-medium' }, 
                            `${Math.round(module.progress * 100)}%`
                        )
                    )
                )
            )
        );
    };
    
    // Render tab content
    const renderTabContent = () => {
        switch (activeTab) {
            case 'puzzles':
                return renderCurrentPuzzle();
            case 'progress':
                return React.createElement('div', { className: 'space-y-6' },
                    renderPerformanceMetrics(),
                    React.createElement('div', { className: 'grid grid-cols-1 lg:grid-cols-2 gap-6' },
                        renderSkillRatings(),
                        renderTrainingModules()
                    )
                );
            default:
                return renderCurrentPuzzle();
        }
    };
    
    return React.createElement('div', { className: 'p-6 max-w-7xl mx-auto' },
        // Header
        React.createElement('div', { className: 'mb-6' },
            React.createElement('h1', { className: 'text-3xl font-bold text-gray-900 mb-2' }, '🎯 Tactical Training Center'),
            React.createElement('p', { className: 'text-gray-600' }, 
                'Systematic skill improvement through targeted exercises and adaptive training algorithms.'
            )
        ),
        
        // Controls
        React.createElement('div', { className: 'bg-white rounded-lg p-4 shadow-sm mb-6' },
            React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-3 gap-4' },
                React.createElement('div', null,
                    React.createElement('label', { className: 'block text-sm font-medium text-gray-700 mb-1' }, 'Training Module'),
                    React.createElement('select', {
                        value: selectedModule,
                        onChange: (e) => setSelectedModule(e.target.value),
                        className: 'w-full border border-gray-300 rounded px-3 py-1 text-sm'
                    },
                        React.createElement('option', { value: 'pattern-recognition' }, 'Pattern Recognition'),
                        React.createElement('option', { value: 'move-quality' }, 'Move Quality Assessment'),
                        React.createElement('option', { value: 'timing' }, 'Timing Optimization'),
                        React.createElement('option', { value: 'endgame' }, 'Endgame Practice')
                    )
                ),
                React.createElement('div', null,
                    React.createElement('label', { className: 'block text-sm font-medium text-gray-700 mb-1' }, 'Difficulty'),
                    React.createElement('select', {
                        value: difficulty,
                        onChange: (e) => setDifficulty(e.target.value),
                        className: 'w-full border border-gray-300 rounded px-3 py-1 text-sm'
                    },
                        React.createElement('option', { value: 'easy' }, 'Easy'),
                        React.createElement('option', { value: 'medium' }, 'Medium'),
                        React.createElement('option', { value: 'hard' }, 'Hard')
                    )
                ),
                React.createElement('div', { className: 'flex items-end' },
                    React.createElement('button', {
                        onClick: loadNewPuzzle,
                        disabled: loading,
                        className: 'w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50'
                    }, loading ? 'Loading...' : 'New Puzzle')
                )
            )
        ),
        
        // Tabs
        React.createElement('div', { className: 'mb-6' },
            React.createElement('div', { className: 'border-b border-gray-200' },
                React.createElement('nav', { className: 'flex space-x-8' },
                    ['puzzles', 'progress'].map(tab => 
                        React.createElement('button', {
                            key: tab,
                            onClick: () => setActiveTab(tab),
                            className: `py-2 px-1 border-b-2 font-medium text-sm ${
                                activeTab === tab 
                                    ? 'border-blue-500 text-blue-600' 
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`
                        }, tab.charAt(0).toUpperCase() + tab.slice(1))
                    )
                )
            )
        ),
        
        // Loading state
        loading && React.createElement('div', { className: 'text-center py-8' },
            React.createElement('div', { className: 'text-gray-500' }, 'Loading training data...')
        ),
        
        // Training content
        !loading && renderTabContent()
    );
}

window.TacticalTrainingCenter = TacticalTrainingCenter; 