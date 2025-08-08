// ComprehensivePatternAnalysis.js - Enhanced Pattern Analysis UI Component with Educational Overlays
const { useState, useEffect, useRef } = React;

function ComprehensivePatternAnalysis({
    gameState,
    currentPlayer = 0,
    onPatternDetected,
    onComprehensiveAnalysis,
    showEducational = true,
    autoAnalyze = true
}) {
    const [comprehensiveAnalysis, setComprehensiveAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showDetails, setShowDetails] = useState(false);
    const [selectedCategory, setSelectedCategory] = useState('all');
    const lastAnalyzedRef = useRef({ fen: null, player: null });
    
    // Comprehensive pattern detection API call
    const detectComprehensivePatterns = async () => {
        console.log('ComprehensivePatternAnalysis: detectComprehensivePatterns called');
        console.log('ComprehensivePatternAnalysis: gameState:', gameState);
        console.log('ComprehensivePatternAnalysis: fen_string:', gameState?.fen_string);
        
        if (!gameState || !gameState.fen_string) {
            console.log('ComprehensivePatternAnalysis: No game state or fen_string available');
            setError('No game state available');
            return;
        }
        
        // Always try to analyze patterns, regardless of FEN string format
        console.log('ComprehensivePatternAnalysis: Making API call with fen_string:', gameState.fen_string);
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch('/api/v1/detect-comprehensive-patterns', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fen_string: gameState.fen_string,
                    current_player: currentPlayer,
                    include_blocking_opportunities: true,
                    include_move_suggestions: true,
                    urgency_threshold: 0.6
                })
            });
            
            console.log('ComprehensivePatternAnalysis: API response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('ComprehensivePatternAnalysis: API response data:', data);
            setComprehensiveAnalysis(data);
            
            // Notify parent component
            if (onComprehensiveAnalysis) onComprehensiveAnalysis(data);
            if (onPatternDetected) onPatternDetected(data);
            
        } catch (err) {
            console.error('Comprehensive pattern detection error:', err);
            setError(`Comprehensive pattern detection failed: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };
    
    // Auto-detect patterns only when FEN or player changes (and autoAnalyze is enabled)
    useEffect(() => {
        const fen = gameState?.fen_string || null;
        if (!autoAnalyze) {
            console.log('ComprehensivePatternAnalysis: autoAnalyze disabled; skipping auto-detect');
            return;
        }
        if (!fen) {
            console.log('ComprehensivePatternAnalysis: No gameState or fen_string, skipping detectComprehensivePatterns');
            return;
        }

        const changed =
            lastAnalyzedRef.current.fen !== fen ||
            lastAnalyzedRef.current.player !== currentPlayer;

        if (!changed) {
            return; // No meaningful change; avoid re-running
        }

        // Prepare for new analysis when the position actually changes
        setComprehensiveAnalysis(null);
        setError(null);
        setShowDetails(false);
        setSelectedCategory('all');

        lastAnalyzedRef.current = { fen, player: currentPlayer };
        console.log('ComprehensivePatternAnalysis: Calling detectComprehensivePatterns');
        detectComprehensivePatterns();
    }, [gameState?.fen_string, currentPlayer, autoAnalyze]);

    // Log when a new analysis result arrives (avoid render-time spam)
    useEffect(() => {
        if (!comprehensiveAnalysis) return;
        const categories = Object.keys(comprehensiveAnalysis.patterns_by_category || {});
        const hasPatterns = categories.some(
            cat => (comprehensiveAnalysis.patterns_by_category[cat] || []).length > 0
        );
        console.log('ComprehensivePatternAnalysis: comprehensiveAnalysis:', comprehensiveAnalysis);
        console.log('ComprehensivePatternAnalysis: categories:', categories);
        console.log('ComprehensivePatternAnalysis: hasPatterns:', hasPatterns);
        console.log('ComprehensivePatternAnalysis: total_patterns:', comprehensiveAnalysis.total_patterns);
        console.log('ComprehensivePatternAnalysis: quality_metrics:', comprehensiveAnalysis.quality_metrics);
    }, [comprehensiveAnalysis]);
    
    // Color mapping for display
    const colorMap = {
        0: { name: 'Blue', class: 'blue-tile' },
        1: { name: 'Yellow', class: 'yellow-tile' },
        2: { name: 'Red', class: 'red-tile' },
        3: { name: 'Black', class: 'black-tile' },
        4: { name: 'White', class: 'white-tile' }
    };
    
    // Category styling
    const getCategoryClass = (category) => {
        const categoryMap = {
            'TACTICAL': 'category-tactical',
            'STRATEGIC': 'category-strategic', 
            'ENDGAME': 'category-endgame',
            'META': 'category-meta',
            'EDGE_CASE': 'category-edge-case'
        };
        return categoryMap[category] || 'category-default';
    };
    
    const getCategoryIcon = (category) => {
        const iconMap = {
            'TACTICAL': '⚔️',
            'STRATEGIC': '🎯',
            'ENDGAME': '🏁',
            'META': '🧠',
            'EDGE_CASE': '⚠️'
        };
        return iconMap[category] || '📊';
    };
    
    // Urgency level styling
    const getUrgencyClass = (urgencyLevel) => {
        if (urgencyLevel === 'HIGH') return 'urgency-high';
        if (urgencyLevel === 'MEDIUM') return 'urgency-medium';
        return 'urgency-low';
    };
    
    const getUrgencyIcon = (urgencyLevel) => {
        if (urgencyLevel === 'HIGH') return '🚨';
        if (urgencyLevel === 'MEDIUM') return '⚠️';
        return 'ℹ️';
    };
    
    // Complexity level styling
    const getComplexityClass = (complexityLevel) => {
        if (complexityLevel === 'HIGH') return 'complexity-high';
        if (complexityLevel === 'MEDIUM') return 'complexity-medium';
        return 'complexity-low';
    };
    
    if (loading) {
        return (
            <div className="comprehensive-pattern-analysis loading">
                <div className="loading-spinner">🔍</div>
                <div>Analyzing comprehensive patterns...</div>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="comprehensive-pattern-analysis error">
                <div className="error-icon">❌</div>
                <div className="error-message">{error}</div>
                <button onClick={detectComprehensivePatterns} className="retry-button">
                    Retry Analysis
                </button>
            </div>
        );
    }
    
    if (!comprehensiveAnalysis) {
        return (
            <div className="comprehensive-pattern-analysis empty">
                <div className="empty-icon">🎯</div>
                <div>No comprehensive patterns detected</div>
                <button onClick={detectComprehensivePatterns} className="retry-button">
                    🔍 Manual Analysis
                </button>
            </div>
        );
    }
    
    // Show the component even if quality metrics are 0, as long as we have analysis data
    if (comprehensiveAnalysis.success === false) {
        return (
            <div className="comprehensive-pattern-analysis error">
                <div className="error-icon">❌</div>
                <div className="error-message">Comprehensive analysis failed</div>
                <button onClick={detectComprehensivePatterns} className="retry-button">
                    Retry Analysis
                </button>
            </div>
        );
    }
    
    // Get all available categories
    const categories = Object.keys(comprehensiveAnalysis.patterns_by_category || {});
    const hasPatterns = categories.some(cat => comprehensiveAnalysis.patterns_by_category[cat].length > 0);
    
    // Debug logging moved to useEffect to avoid render-time spam
    
    return (
        <div className="comprehensive-pattern-analysis">
            <div className="comprehensive-header">
                <h3>🏆 Comprehensive Pattern Analysis</h3>
                <div className="comprehensive-summary">
                    <span className="pattern-count">
                        {comprehensiveAnalysis.total_patterns} pattern{comprehensiveAnalysis.total_patterns !== 1 ? 's' : ''} detected
                    </span>
                    <span className="quality-score">
                        Quality: {(comprehensiveAnalysis.quality_metrics?.confidence_score * 100).toFixed(0)}%
                    </span>
                </div>
                <button 
                    onClick={() => setShowDetails(!showDetails)}
                    className="toggle-details-button"
                >
                    {showDetails ? 'Hide Details' : 'Show Details'}
                </button>
            </div>
            
            {/* Quality Metrics */}
            {comprehensiveAnalysis.quality_metrics && (
                <div className="quality-metrics">
                    <h4>📊 Analysis Quality</h4>
                    <div className="metrics-grid">
                        <div className="metric-card">
                            <span className="metric-label">Coverage</span>
                            <span className="metric-value">
                                {(comprehensiveAnalysis.quality_metrics.coverage_score * 100).toFixed(0)}%
                            </span>
                        </div>
                        <div className="metric-card">
                            <span className="metric-label">Confidence</span>
                            <span className="metric-value">
                                {(comprehensiveAnalysis.quality_metrics.confidence_score * 100).toFixed(0)}%
                            </span>
                        </div>
                        <div className="metric-card">
                            <span className="metric-label">Complexity</span>
                            <span className="metric-value">
                                {(comprehensiveAnalysis.quality_metrics.complexity_score * 100).toFixed(0)}%
                            </span>
                        </div>
                    </div>
                </div>
            )}
            
            {/* Category Filter */}
            {categories.length > 0 && (
                <div className="category-filter">
                    <h4>📂 Pattern Categories</h4>
                    <div className="filter-buttons">
                        <button 
                            className={`filter-btn ${selectedCategory === 'all' ? 'active' : ''}`}
                            onClick={() => setSelectedCategory('all')}
                        >
                            All Categories ({comprehensiveAnalysis.total_patterns})
                        </button>
                        {categories.map(category => {
                            const patternCount = comprehensiveAnalysis.patterns_by_category[category].length;
                            if (patternCount === 0) return null;
                            return (
                                <button 
                                    key={category}
                                    className={`filter-btn ${selectedCategory === category ? 'active' : ''} ${getCategoryClass(category)}`}
                                    onClick={() => setSelectedCategory(category)}
                                >
                                    {getCategoryIcon(category)} {category} ({patternCount})
                                </button>
                            );
                        })}
                    </div>
                </div>
            )}
            
            {/* Patterns by Category */}
            {hasPatterns && (
                <div className="patterns-by-category">
                    {categories.map(category => {
                        const patterns = comprehensiveAnalysis.patterns_by_category[category];
                        if (patterns.length === 0) return null;
                        if (selectedCategory !== 'all' && selectedCategory !== category) return null;
                        
                        return (
                            <div key={category} className={`category-section ${getCategoryClass(category)}`}>
                                <h4>
                                    {getCategoryIcon(category)} {category} Patterns ({patterns.length})
                                </h4>
                                <div className="patterns-list">
                                    {patterns.map((pattern, index) => (
                                        <div key={index} className="pattern-card">
                                            <div className="pattern-header">
                                                <span className="pattern-name">{pattern.pattern_name}</span>
                                                <div className="pattern-badges">
                                                    <span className={`urgency-badge ${getUrgencyClass(pattern.urgency_level)}`}>
                                                        {getUrgencyIcon(pattern.urgency_level)} {pattern.urgency_level}
                                                    </span>
                                                    <span className={`complexity-badge ${getComplexityClass(pattern.complexity_level)}`}>
                                                        {pattern.complexity_level}
                                                    </span>
                                                </div>
                                            </div>
                                            
                                            <div className="pattern-description">
                                                {pattern.description}
                                            </div>
                                            
                                            {/* Educational Overlays */}
                                            {showEducational && (
                                                <div className="educational-overlays">
                                                    <PatternExplainer 
                                                        patternType={typeof pattern.pattern_name === 'string' ? pattern.pattern_name.toLowerCase().replace(/\s+/g, '_') : 'unknown_pattern'}
                                                        difficulty={typeof pattern.complexity_level === 'string' ? pattern.complexity_level.toLowerCase() : 'intermediate'}
                                                        patternData={pattern}
                                                    />
                                                    <PatternVisualizer 
                                                        pattern={pattern}
                                                        animationSpeed={1500}
                                                    />
                                                </div>
                                            )}
                                            
                                            {showDetails && (
                                                <div className="pattern-details">
                                                    <div className="detail-section">
                                                        <strong>Detection Criteria:</strong> {pattern.detection_criteria}
                                                    </div>
                                                    <div className="detail-section">
                                                        <strong>Success Metrics:</strong> {pattern.success_metrics}
                                                    </div>
                                                    <div className="detail-section">
                                                        <strong>Interaction Effects:</strong> {pattern.interaction_effects}
                                                    </div>
                                                    <div className="detail-section">
                                                        <strong>Examples:</strong> {pattern.examples}
                                                    </div>
                                                    <div className="detail-section">
                                                        <strong>Counter-patterns:</strong> {pattern.counter_patterns}
                                                    </div>
                                                    <div className="detail-section">
                                                        <strong>Prerequisites:</strong> {pattern.prerequisites}
                                                    </div>
                                                    <div className="detail-section">
                                                        <strong>Alternatives:</strong> {pattern.alternatives}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
            
            {/* Pattern Interactions */}
            {comprehensiveAnalysis.pattern_interactions && comprehensiveAnalysis.pattern_interactions.length > 0 && (
                <div className="pattern-interactions">
                    <h4>🔗 Pattern Interactions</h4>
                    <div className="interactions-list">
                        {comprehensiveAnalysis.pattern_interactions.map((interaction, index) => (
                            <div key={index} className="interaction-card">
                                <div className="interaction-header">
                                    <span className="interaction-patterns">
                                        {interaction.pattern_a} ↔ {interaction.pattern_b}
                                    </span>
                                    <span className="interaction-type">
                                        {interaction.interaction_type}
                                    </span>
                                </div>
                                <div className="interaction-description">
                                    {interaction.description}
                                </div>
                                <div className="interaction-strength">
                                    Strength: {interaction.strength}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            
            {/* Backward Compatible Results */}
            {comprehensiveAnalysis.backward_compatible && (
                <div className="backward-compatible">
                    <h4>🔄 Backward Compatible Results</h4>
                    <div className="bc-summary">
                        <span>Total Patterns: {comprehensiveAnalysis.backward_compatible.total_patterns}</span>
                        <span>Confidence: {(comprehensiveAnalysis.backward_compatible.confidence_score * 100).toFixed(0)}%</span>
                    </div>
                    
                    {comprehensiveAnalysis.backward_compatible.blocking_opportunities && (
                        <div className="blocking-opportunities">
                            <h5>🛡️ Blocking Opportunities</h5>
                            <div className="opportunities-list">
                                {comprehensiveAnalysis.backward_compatible.blocking_opportunities.map((opportunity, index) => (
                                    <div 
                                        key={index} 
                                        className={`opportunity-card ${getUrgencyClass(opportunity.urgency_level)}`}
                                    >
                                        <div className="opportunity-header">
                                            <span className="urgency-icon">
                                                {getUrgencyIcon(opportunity.urgency_level)}
                                            </span>
                                            <span className="target-info">
                                                Opponent {opportunity.target_player + 1} - 
                                                Pattern Line {opportunity.target_pattern_line + 1}
                                            </span>
                                            <span className="urgency-level">
                                                {opportunity.urgency_level}
                                            </span>
                                        </div>
                                        
                                        <div className="opportunity-details">
                                            <div className="color-info">
                                                <span className={`color-indicator ${colorMap[opportunity.target_color]?.class}`}>
                                                    {colorMap[opportunity.target_color]?.name}
                                                </span>
                                                <span className="tiles-needed">
                                                    Needs {opportunity.blocking_tiles_available} more tiles
                                                </span>
                                            </div>
                                            
                                            <div className="blocking-info">
                                                <span className="blocking-sources">
                                                    Available in: 
                                                    {opportunity.blocking_factories.map(f => ` Factory ${f + 1}`).join(',')}
                                                    {opportunity.blocking_center && ', Center'}
                                                </span>
                                            </div>
                                            
                                            {showDetails && (
                                                <div className="opportunity-description">
                                                    {opportunity.description}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
            
            {!hasPatterns && (
                <div className="no-patterns">
                    <div className="no-patterns-icon">🎯</div>
                    <div className="no-patterns-message">
                        No comprehensive patterns detected in this position.
                    </div>
                    <div className="no-patterns-hint">
                        Try analyzing a position with more complex tactical or strategic elements.
                    </div>
                </div>
            )}
        </div>
    );
}

// Memoize to avoid re-renders unless relevant props change
const MemoizedComprehensivePatternAnalysis = React.memo(
    ComprehensivePatternAnalysis,
    (prevProps, nextProps) => {
        const prevFen = prevProps.gameState?.fen_string;
        const nextFen = nextProps.gameState?.fen_string;
        return (
            prevFen === nextFen &&
            prevProps.currentPlayer === nextProps.currentPlayer &&
            prevProps.showEducational === nextProps.showEducational &&
            prevProps.autoAnalyze === nextProps.autoAnalyze
        );
    }
);

window.ComprehensivePatternAnalysis = MemoizedComprehensivePatternAnalysis;