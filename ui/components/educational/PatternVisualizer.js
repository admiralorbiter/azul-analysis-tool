// PatternVisualizer.js - Animated pattern demonstration component
const { useState, useEffect } = React;

function PatternVisualizer({ pattern, animationSpeed = 1500, showControls = true }) {
    const [currentStep, setCurrentStep] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [showAnimation, setShowAnimation] = useState(false);
    
    // Pattern animation steps for different pattern types
    const getPatternSteps = (patternType) => {
        const patternSteps = {
            "blocking_pattern": [
                { step: 1, description: "Identify opponent's incomplete row", action: "🔍 Scan opponent boards" },
                { step: 2, description: "Locate needed tiles in factories", action: "🏭 Check factory tiles" },
                { step: 3, description: "Take tiles to deny opponent", action: "✋ Take blocking tiles" },
                { step: 4, description: "Place tiles strategically", action: "📋 Place to block" },
                { step: 5, description: "Verify blocking effectiveness", action: "✅ Confirm block" }
            ],
            "scoring_pattern": [
                { step: 1, description: "Identify scoring opportunities", action: "🎯 Find scoring chances" },
                { step: 2, description: "Calculate potential points", action: "📊 Count points" },
                { step: 3, description: "Select optimal tiles", action: "🎲 Choose best tiles" },
                { step: 4, description: "Place tiles for maximum score", action: "📋 Place strategically" },
                { step: 5, description: "Verify scoring achieved", action: "✅ Confirm points" }
            ],
            "timing_pattern": [
                { step: 1, description: "Analyze game state timing", action: "⏰ Assess timing" },
                { step: 2, description: "Identify optimal move order", action: "📋 Plan sequence" },
                { step: 3, description: "Execute timing-dependent moves", action: "⚡ Execute moves" },
                { step: 4, description: "Monitor timing effects", action: "👁️ Watch effects" },
                { step: 5, description: "Adjust timing as needed", action: "🔄 Adjust timing" }
            ],
            "factory_control": [
                { step: 1, description: "Identify valuable factories", action: "🏭 Find key factories" },
                { step: 2, description: "Analyze factory tile distribution", action: "📊 Count tiles" },
                { step: 3, description: "Take control of key factories", action: "✋ Control factories" },
                { step: 4, description: "Limit opponent access", action: "🚫 Block access" },
                { step: 5, description: "Maintain factory control", action: "🛡️ Maintain control" }
            ],
            "endgame_pattern": [
                { step: 1, description: "Count remaining tiles", action: "🔢 Count tiles" },
                { step: 2, description: "Calculate final scoring", action: "📊 Plan scoring" },
                { step: 3, description: "Execute precise sequences", action: "⚡ Execute precisely" },
                { step: 4, description: "Deny opponent points", action: "🚫 Block opponents" },
                { step: 5, description: "Maximize final score", action: "🏆 Maximize score" }
            ]
        };
        
        return patternSteps[patternType] || [
            { step: 1, description: "Analyze pattern", action: "🔍 Analyze" },
            { step: 2, description: "Plan execution", action: "📋 Plan" },
            { step: 3, description: "Execute pattern", action: "⚡ Execute" },
            { step: 4, description: "Verify results", action: "✅ Verify" }
        ];
    };
    
    // Get pattern type from pattern data
    const getPatternType = (pattern) => {
        if (!pattern) return "unknown";
        
        const patternName = pattern.pattern_name?.toLowerCase() || "";
        
        if (patternName.includes("block")) return "blocking_pattern";
        if (patternName.includes("score")) return "scoring_pattern";
        if (patternName.includes("timing") || patternName.includes("time")) return "timing_pattern";
        if (patternName.includes("factory") || patternName.includes("control")) return "factory_control";
        if (patternName.includes("endgame") || patternName.includes("end")) return "endgame_pattern";
        
        return "unknown";
    };
    
    const patternType = getPatternType(pattern);
    const steps = getPatternSteps(patternType);
    
    // Animation timer effect
    useEffect(() => {
        let timer;
        if (isPlaying && showAnimation) {
            timer = setInterval(() => {
                setCurrentStep(prev => (prev + 1) % steps.length);
            }, animationSpeed);
        }
        return () => clearInterval(timer);
    }, [isPlaying, showAnimation, animationSpeed, steps.length]);
    
    // Play/pause animation
    const toggleAnimation = () => {
        if (!showAnimation) {
            setShowAnimation(true);
            setIsPlaying(true);
        } else {
            setIsPlaying(!isPlaying);
        }
    };
    
    // Reset animation
    const resetAnimation = () => {
        setCurrentStep(0);
        setIsPlaying(false);
    };
    
    // Go to specific step
    const goToStep = (step) => {
        setCurrentStep(step);
        setIsPlaying(false);
    };
    
    // Get step status class
    const getStepStatusClass = (stepIndex) => {
        if (stepIndex === currentStep) return 'step-current';
        if (stepIndex < currentStep) return 'step-completed';
        return 'step-pending';
    };
    
    // Get step status icon
    const getStepStatusIcon = (stepIndex) => {
        if (stepIndex === currentStep) return '⚡';
        if (stepIndex < currentStep) return '✅';
        return '⏳';
    };
    
    return (
        <div className="pattern-visualizer">
            <div className="visualizer-header">
                <h5 className="visualizer-title">
                    🎬 Pattern Animation: {patternType.replace('_', ' ').toUpperCase()}
                </h5>
                {showControls && (
                    <div className="animation-controls">
                        <button 
                            className={`play-button ${isPlaying ? 'paused' : 'playing'}`}
                            onClick={toggleAnimation}
                        >
                            {isPlaying ? '⏸️ Pause' : '▶️ Play'}
                        </button>
                        <button 
                            className="reset-button"
                            onClick={resetAnimation}
                        >
                            🔄 Reset
                        </button>
                    </div>
                )}
            </div>
            
            {showAnimation && (
                <div className="animation-content">
                    <div className="current-step-display">
                        <div className="step-number">
                            Step {currentStep + 1} of {steps.length}
                        </div>
                        <div className="step-description">
                            {steps[currentStep].description}
                        </div>
                        <div className="step-action">
                            {steps[currentStep].action}
                        </div>
                    </div>
                    
                    <div className="steps-progress">
                        <div className="progress-bar">
                            <div 
                                className="progress-fill"
                                style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
                            ></div>
                        </div>
                    </div>
                    
                    <div className="steps-list">
                        {steps.map((step, index) => (
                            <div 
                                key={index}
                                className={`step-item ${getStepStatusClass(index)}`}
                                onClick={() => goToStep(index)}
                            >
                                <span className="step-icon">
                                    {getStepStatusIcon(index)}
                                </span>
                                <div className="step-content">
                                    <div className="step-title">
                                        Step {step.step}: {step.description}
                                    </div>
                                    <div className="step-action-text">
                                        {step.action}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            
            {!showAnimation && (
                <div className="animation-prompt">
                    <div className="prompt-icon">🎬</div>
                    <div className="prompt-text">
                        Click "Play" to see an animated demonstration of this pattern
                    </div>
                    <button 
                        className="start-animation-button"
                        onClick={toggleAnimation}
                    >
                        ▶️ Start Animation
                    </button>
                </div>
            )}
            
            {pattern && (
                <div className="pattern-info">
                    <div className="info-item">
                        <strong>Pattern:</strong> {pattern.pattern_name || 'Unknown'}
                    </div>
                    <div className="info-item">
                        <strong>Urgency:</strong> {pattern.urgency_level || 'Unknown'}
                    </div>
                    <div className="info-item">
                        <strong>Complexity:</strong> {pattern.complexity_level || 'Unknown'}
                    </div>
                </div>
            )}
        </div>
    );
}

// Export for use in other components
window.PatternVisualizer = PatternVisualizer; 