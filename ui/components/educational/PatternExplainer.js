// PatternExplainer.js - Educational pattern explanation component
const { useState, useEffect } = React;

function PatternExplainer({ patternType, difficulty, patternData }) {
    const [showDetails, setShowDetails] = useState(false);
    const [educationalContent, setEducationalContent] = useState(null);
    const [loading, setLoading] = useState(false);
    
    // Pattern educational content database
    const patternEducationalContent = {
        "blocking_pattern": {
            difficulty: "beginner",
            explanation: "This pattern prevents opponents from completing their rows",
            strategicReasoning: "Blocking is fundamental to Azul strategy. By denying opponents the tiles they need, you can control the pace of the game and create opportunities for yourself.",
            learningTips: [
                "Look for opportunities to block while advancing your own position",
                "Consider the timing - blocking too early can waste resources",
                "Balance blocking with your own scoring opportunities",
                "Watch for patterns that opponents are building"
            ],
            successRate: 85,
            category: "defensive",
            examples: [
                "Taking a tile that an opponent needs for their incomplete row",
                "Controlling factory tiles to limit opponent options",
                "Strategic placement to deny scoring opportunities"
            ]
        },
        "scoring_pattern": {
            difficulty: "intermediate", 
            explanation: "This pattern maximizes scoring opportunities",
            strategicReasoning: "Efficient scoring patterns lead to consistent wins. The key is to balance immediate scoring with long-term position building.",
            learningTips: [
                "Balance immediate scoring with long-term position building",
                "Look for multi-point scoring opportunities",
                "Consider the timing of when to complete patterns",
                "Plan ahead for future scoring opportunities"
            ],
            successRate: 78,
            category: "offensive",
            examples: [
                "Completing a row for immediate points",
                "Setting up multiple scoring opportunities",
                "Timing pattern completion for maximum effect"
            ]
        },
        "timing_pattern": {
            difficulty: "advanced",
            explanation: "This pattern considers the timing of moves",
            strategicReasoning: "Timing is crucial in competitive Azul play. The right move at the wrong time can be as bad as the wrong move.",
            learningTips: [
                "Study the game state to understand optimal timing",
                "Consider the order of operations carefully",
                "Look for opportunities to delay or accelerate moves",
                "Understand the rhythm of the game"
            ],
            successRate: 72,
            category: "strategic",
            examples: [
                "Delaying a move to create better opportunities",
                "Accelerating pattern completion for timing advantage",
                "Coordinating multiple actions for maximum effect"
            ]
        },
        "factory_control": {
            difficulty: "intermediate",
            explanation: "This pattern focuses on controlling factory tiles",
            strategicReasoning: "Factory control gives you power over tile distribution and can limit opponent options while creating opportunities for yourself.",
            learningTips: [
                "Identify which factories are most valuable",
                "Consider the impact on all players, not just yourself",
                "Balance factory control with immediate scoring needs",
                "Use factory control to set up future opportunities"
            ],
            successRate: 75,
            category: "control",
            examples: [
                "Taking tiles from factories to limit opponent access",
                "Strategic factory selection to control tile flow",
                "Using factory control to set up scoring opportunities"
            ]
        },
        "endgame_pattern": {
            difficulty: "advanced",
            explanation: "This pattern is designed for endgame scenarios",
            strategicReasoning: "Endgame patterns require different thinking than early game patterns. Efficiency and precision become more important than flexibility.",
            learningTips: [
                "Focus on efficiency over flexibility in endgame",
                "Count tiles carefully and plan exact sequences",
                "Consider the impact of each move on final scoring",
                "Look for opportunities to deny opponents final points"
            ],
            successRate: 68,
            category: "endgame",
            examples: [
                "Precise tile counting and placement",
                "Denying opponents final scoring opportunities",
                "Optimizing for maximum endgame points"
            ]
        }
    };
    
    // Get educational content for the pattern type
    const getEducationalContent = (patternType) => {
        return patternEducationalContent[patternType] || {
            difficulty: "unknown",
            explanation: "This pattern type requires further analysis",
            strategicReasoning: "Pattern analysis is ongoing",
            learningTips: ["Study the pattern carefully", "Consider all strategic implications"],
            successRate: 50,
            category: "unknown",
            examples: ["Pattern analysis in progress"]
        };
    };
    
    // Load educational content when component mounts or pattern type changes
    useEffect(() => {
        if (patternType) {
            setEducationalContent(getEducationalContent(patternType));
        }
    }, [patternType]);
    
    // Get difficulty color class
    const getDifficultyClass = (difficulty) => {
        const difficultyMap = {
            'beginner': 'difficulty-beginner',
            'intermediate': 'difficulty-intermediate',
            'advanced': 'difficulty-advanced',
            'expert': 'difficulty-expert'
        };
        return difficultyMap[difficulty] || 'difficulty-unknown';
    };
    
    // Get category color class
    const getCategoryClass = (category) => {
        const categoryMap = {
            'defensive': 'category-defensive',
            'offensive': 'category-offensive',
            'strategic': 'category-strategic',
            'control': 'category-control',
            'endgame': 'category-endgame'
        };
        return categoryMap[category] || 'category-unknown';
    };
    
    if (!educationalContent) {
        return (
            <div className="pattern-explainer loading">
                <div className="loading-spinner">📚</div>
                <div>Loading educational content...</div>
            </div>
        );
    }
    
    return (
        <div className="pattern-explainer">
            <button 
                className="learn-button"
                onClick={() => setShowDetails(!showDetails)}
            >
                📚 Learn About {patternType.replace('_', ' ')} Pattern
            </button>
            
            {showDetails && (
                <div className="educational-content">
                    <div className="content-header">
                        <h4 className="pattern-title">
                            {patternType.replace('_', ' ').toUpperCase()} Pattern
                        </h4>
                        <div className="pattern-badges">
                            <span className={`difficulty-badge ${getDifficultyClass(educationalContent.difficulty)}`}>
                                {educationalContent.difficulty.toUpperCase()}
                            </span>
                            <span className={`category-badge ${getCategoryClass(educationalContent.category)}`}>
                                {educationalContent.category.toUpperCase()}
                            </span>
                            <span className="success-rate-badge">
                                {educationalContent.successRate}% Success Rate
                            </span>
                        </div>
                    </div>
                    
                    <div className="content-sections">
                        <div className="content-section">
                            <h5 className="section-title">📖 Explanation</h5>
                            <p className="explanation-text">{educationalContent.explanation}</p>
                        </div>
                        
                        <div className="content-section">
                            <h5 className="section-title">🧠 Strategic Reasoning</h5>
                            <p className="strategic-reasoning">{educationalContent.strategicReasoning}</p>
                        </div>
                        
                        <div className="content-section">
                            <h5 className="section-title">💡 Learning Tips</h5>
                            <ul className="learning-tips">
                                {educationalContent.learningTips.map((tip, index) => (
                                    <li key={index} className="learning-tip">
                                        {tip}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        
                        <div className="content-section">
                            <h5 className="section-title">🎯 Examples</h5>
                            <ul className="examples-list">
                                {educationalContent.examples.map((example, index) => (
                                    <li key={index} className="example-item">
                                        {example}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        
                        {patternData && (
                            <div className="content-section">
                                <h5 className="section-title">📊 Current Pattern Analysis</h5>
                                <div className="current-pattern-info">
                                    <p><strong>Pattern Name:</strong> {patternData.pattern_name || 'Unknown'}</p>
                                    <p><strong>Urgency Level:</strong> {patternData.urgency_level || 'Unknown'}</p>
                                    <p><strong>Complexity Level:</strong> {patternData.complexity_level || 'Unknown'}</p>
                                    <p><strong>Description:</strong> {patternData.description || 'No description available'}</p>
                                </div>
                            </div>
                        )}
                    </div>
                    
                    <div className="content-footer">
                        <button 
                            className="practice-button"
                            onClick={() => {
                                // TODO: Implement pattern practice functionality
                                console.log('Practice pattern:', patternType);
                            }}
                        >
                            🎯 Practice This Pattern
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

// Export for use in other components
window.PatternExplainer = PatternExplainer; 