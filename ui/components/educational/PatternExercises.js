// PatternExercises.js - Interactive pattern recognition exercises component
const { useState, useEffect } = React;

function PatternExercises({ difficulty = 'beginner', patternType, onComplete }) {
    const [currentExercise, setCurrentExercise] = useState(0);
    const [score, setScore] = useState(0);
    const [showResults, setShowResults] = useState(false);
    const [timeRemaining, setTimeRemaining] = useState(30);
    const [isActive, setIsActive] = useState(false);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [showFeedback, setShowFeedback] = useState(false);
    
    // Exercise database for different pattern types and difficulties
    const exerciseDatabase = {
        "blocking_pattern": {
            "beginner": [
                {
                    question: "What is the primary goal of a blocking pattern?",
                    options: [
                        "To score as many points as possible",
                        "To prevent opponents from completing their rows",
                        "To control all factory tiles",
                        "To finish the game quickly"
                    ],
                    correctAnswer: 1,
                    explanation: "Blocking patterns focus on denying opponents the tiles they need to complete their rows, which is fundamental to defensive Azul strategy."
                },
                {
                    question: "When is the best time to execute a blocking move?",
                    options: [
                        "Always in the first turn",
                        "When an opponent is close to completing a row",
                        "Only when you have no other options",
                        "Never - blocking is always bad"
                    ],
                    correctAnswer: 1,
                    explanation: "The optimal time to block is when an opponent is close to completing a row, as this maximizes the impact of your blocking move."
                }
            ],
            "intermediate": [
                {
                    question: "How do you identify the most valuable blocking opportunities?",
                    options: [
                        "Block the opponent with the most tiles",
                        "Block the opponent closest to completing a row",
                        "Block randomly to confuse opponents",
                        "Only block when you have extra tiles"
                    ],
                    correctAnswer: 1,
                    explanation: "The most valuable blocking opportunities are against opponents who are closest to completing rows, as this denies them immediate scoring."
                }
            ]
        },
        "scoring_pattern": {
            "beginner": [
                {
                    question: "What should you prioritize in a scoring pattern?",
                    options: [
                        "Taking tiles as quickly as possible",
                        "Balancing immediate scoring with long-term position building",
                        "Always completing the highest-scoring move",
                        "Ignoring opponent positions entirely"
                    ],
                    correctAnswer: 1,
                    explanation: "Effective scoring patterns balance immediate points with building strong positions for future turns."
                },
                {
                    question: "When should you complete a row for points?",
                    options: [
                        "As soon as you have enough tiles",
                        "When it gives you the most points possible",
                        "Only in the final turn",
                        "Never - rows are not worth completing"
                    ],
                    correctAnswer: 1,
                    explanation: "Complete rows when they give you the maximum possible points, considering both immediate and future scoring opportunities."
                }
            ],
            "intermediate": [
                {
                    question: "How do you calculate the optimal scoring sequence?",
                    options: [
                        "Always take the highest-scoring move",
                        "Consider both immediate points and future opportunities",
                        "Focus only on completing rows quickly",
                        "Ignore scoring and focus on blocking"
                    ],
                    correctAnswer: 1,
                    explanation: "Optimal scoring sequences consider both immediate points and how moves set up future scoring opportunities."
                }
            ]
        },
        "timing_pattern": {
            "beginner": [
                {
                    question: "Why is timing important in Azul?",
                    options: [
                        "It doesn't matter - just make moves quickly",
                        "The right move at the wrong time can be as bad as the wrong move",
                        "Timing only matters in the endgame",
                        "Timing is only important for blocking"
                    ],
                    correctAnswer: 1,
                    explanation: "Timing is crucial because the right move at the wrong time can waste opportunities or create problems for yourself."
                }
            ],
            "intermediate": [
                {
                    question: "How do you identify optimal timing for moves?",
                    options: [
                        "Always move as quickly as possible",
                        "Study the game state and consider the order of operations",
                        "Wait until the last possible moment",
                        "Timing doesn't matter in Azul"
                    ],
                    correctAnswer: 1,
                    explanation: "Optimal timing requires studying the game state and carefully considering the order of operations."
                }
            ]
        },
        "factory_control": {
            "beginner": [
                {
                    question: "What is factory control?",
                    options: [
                        "Owning all the factories",
                        "Controlling which tiles are available to opponents",
                        "Having the most tiles in your possession",
                        "Being the first player to take tiles"
                    ],
                    correctAnswer: 1,
                    explanation: "Factory control means controlling which tiles are available to opponents, giving you power over tile distribution."
                }
            ],
            "intermediate": [
                {
                    question: "How do you maintain factory control effectively?",
                    options: [
                        "Take tiles from every factory",
                        "Identify key factories and control access to them",
                        "Always take the most tiles possible",
                        "Ignore factory control and focus on scoring"
                    ],
                    correctAnswer: 1,
                    explanation: "Effective factory control involves identifying which factories are most valuable and controlling access to them."
                }
            ]
        },
        "endgame_pattern": {
            "beginner": [
                {
                    question: "What changes in endgame strategy?",
                    options: [
                        "Nothing - play the same as always",
                        "Efficiency and precision become more important than flexibility",
                        "Focus only on blocking opponents",
                        "Take as many tiles as possible"
                    ],
                    correctAnswer: 1,
                    explanation: "In endgame, efficiency and precision become more important than flexibility, as you have fewer turns to work with."
                }
            ],
            "intermediate": [
                {
                    question: "How do you optimize endgame scoring?",
                    options: [
                        "Take any available tiles",
                        "Count tiles carefully and plan exact sequences",
                        "Focus only on completing rows",
                        "Ignore scoring and focus on blocking"
                    ],
                    correctAnswer: 1,
                    explanation: "Endgame optimization requires careful tile counting and planning exact sequences for maximum efficiency."
                }
            ]
        }
    };
    
    // Get exercises for the current pattern type and difficulty
    const getExercises = () => {
        const exercises = exerciseDatabase[patternType]?.[difficulty] || [];
        if (exercises.length === 0) {
            // Fallback exercises
            return [
                {
                    question: "What is the main goal of this pattern type?",
                    options: [
                        "To score points",
                        "To block opponents", 
                        "To control the game",
                        "To finish quickly"
                    ],
                    correctAnswer: 0,
                    explanation: "Patterns generally aim to achieve strategic goals in the game."
                }
            ];
        }
        return exercises;
    };
    
    const exercises = getExercises();
    const currentExerciseData = exercises[currentExercise];
    
    // Timer effect
    useEffect(() => {
        let timer;
        if (isActive && timeRemaining > 0) {
            timer = setInterval(() => {
                setTimeRemaining(prev => prev - 1);
            }, 1000);
        } else if (timeRemaining === 0) {
            handleExerciseComplete();
        }
        return () => clearInterval(timer);
    }, [isActive, timeRemaining]);
    
    // Start exercise when component mounts
    useEffect(() => {
        setIsActive(true);
    }, []);
    
    // Handle answer selection
    const handleAnswerSelect = (answerIndex) => {
        setSelectedAnswer(answerIndex);
        setShowFeedback(true);
        
        // Check if answer is correct
        if (answerIndex === currentExerciseData.correctAnswer) {
            setScore(score + 1);
        }
        
        // Move to next exercise after a delay
        setTimeout(() => {
            setShowFeedback(false);
            setSelectedAnswer(null);
            if (currentExercise < exercises.length - 1) {
                setCurrentExercise(currentExercise + 1);
            } else {
                handleExerciseComplete();
            }
        }, 2000);
    };
    
    // Handle exercise completion
    const handleExerciseComplete = () => {
        setIsActive(false);
        setShowResults(true);
        if (onComplete) {
            onComplete({
                score: score,
                total: exercises.length,
                percentage: (score / exercises.length) * 100,
                patternType: patternType,
                difficulty: difficulty
            });
        }
    };
    
    // Restart exercises
    const restartExercises = () => {
        setCurrentExercise(0);
        setScore(0);
        setShowResults(false);
        setTimeRemaining(30);
        setIsActive(true);
        setSelectedAnswer(null);
        setShowFeedback(false);
    };
    
    // Get feedback class
    const getFeedbackClass = (answerIndex) => {
        if (!showFeedback) return '';
        if (answerIndex === currentExerciseData.correctAnswer) return 'correct';
        if (answerIndex === selectedAnswer) return 'incorrect';
        return '';
    };
    
    if (showResults) {
        return (
            <div className="pattern-exercises results">
                <div className="results-header">
                    <h5>🎯 Exercise Results</h5>
                </div>
                
                <div className="results-content">
                    <div className="score-display">
                        <div className="score-number">{score}/{exercises.length}</div>
                        <div className="score-percentage">
                            {Math.round((score / exercises.length) * 100)}%
                        </div>
                    </div>
                    
                    <div className="performance-feedback">
                        {score === exercises.length && (
                            <div className="perfect-score">
                                🏆 Perfect! You've mastered this pattern!
                            </div>
                        )}
                        {score >= exercises.length * 0.8 && score < exercises.length && (
                            <div className="good-score">
                                👍 Great job! You understand this pattern well.
                            </div>
                        )}
                        {score >= exercises.length * 0.6 && score < exercises.length * 0.8 && (
                            <div className="decent-score">
                                📚 Good effort! Keep practicing to improve.
                            </div>
                        )}
                        {score < exercises.length * 0.6 && (
                            <div className="needs-improvement">
                                📖 Keep studying! Review the pattern concepts.
                            </div>
                        )}
                    </div>
                    
                    <div className="pattern-summary">
                        <div className="summary-item">
                            <strong>Pattern Type:</strong> {patternType.replace('_', ' ')}
                        </div>
                        <div className="summary-item">
                            <strong>Difficulty:</strong> {difficulty}
                        </div>
                        <div className="summary-item">
                            <strong>Time Taken:</strong> {30 - timeRemaining} seconds
                        </div>
                    </div>
                </div>
                
                <div className="results-actions">
                    <button 
                        className="restart-button"
                        onClick={restartExercises}
                    >
                        🔄 Try Again
                    </button>
                    <button 
                        className="close-button"
                        onClick={() => setShowResults(false)}
                    >
                        ✖️ Close
                    </button>
                </div>
            </div>
        );
    }
    
    return (
        <div className="pattern-exercises">
            <div className="exercise-header">
                <h5>🎯 Pattern Recognition Exercise</h5>
                <div className="exercise-info">
                    <span className="exercise-counter">
                        {currentExercise + 1} of {exercises.length}
                    </span>
                    <span className="score-display">
                        Score: {score}/{currentExercise}
                    </span>
                    <span className="timer">
                        ⏱️ {timeRemaining}s
                    </span>
                </div>
            </div>
            
            <div className="exercise-content">
                <div className="question">
                    <h6>Question {currentExercise + 1}:</h6>
                    <p>{currentExerciseData.question}</p>
                </div>
                
                <div className="answer-options">
                    {currentExerciseData.options.map((option, index) => (
                        <button
                            key={index}
                            className={`answer-option ${getFeedbackClass(index)}`}
                            onClick={() => handleAnswerSelect(index)}
                            disabled={showFeedback}
                        >
                            <span className="option-letter">
                                {String.fromCharCode(65 + index)}
                            </span>
                            <span className="option-text">{option}</span>
                        </button>
                    ))}
                </div>
                
                {showFeedback && (
                    <div className="feedback">
                        <div className={`feedback-message ${selectedAnswer === currentExerciseData.correctAnswer ? 'correct' : 'incorrect'}`}>
                            {selectedAnswer === currentExerciseData.correctAnswer ? '✅ Correct!' : '❌ Incorrect'}
                        </div>
                        <div className="explanation">
                            {currentExerciseData.explanation}
                        </div>
                    </div>
                )}
            </div>
            
            <div className="exercise-progress">
                <div className="progress-bar">
                    <div 
                        className="progress-fill"
                        style={{ width: `${((currentExercise + 1) / exercises.length) * 100}%` }}
                    ></div>
                </div>
            </div>
        </div>
    );
}

// Export for use in other components
window.PatternExercises = PatternExercises; 