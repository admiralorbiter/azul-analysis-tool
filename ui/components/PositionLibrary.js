// Position Library Component for R1.2 Implementation
// Handles expanded position categories, tagging, and management

const { useState, useCallback, useMemo } = React;

const PositionLibrary = React.memo(function PositionLibrary({
    gameState,
    setGameState,
    setStatusMessage,
    sessionToken,
    onClose
}) {
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedTags, setSelectedTags] = useState([]);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [customPositions, setCustomPositions] = useState([]);
    const [modulesLoaded, setModulesLoaded] = useState(false);
    const [previewPosition, setPreviewPosition] = useState(null);
    
    // Check if modules are loaded
    React.useEffect(() => {
        const checkModulesLoaded = () => {
            const hasOpening = window.openingPositions && Object.keys(window.openingPositions).length > 0;
            const hasMidgame = window.midgamePositions && Object.keys(window.midgamePositions).length > 0;
            const hasEndgame = window.endgamePositions && Object.keys(window.endgamePositions).length > 0;
            const hasEducational = window.educationalPositions && Object.keys(window.educationalPositions).length > 0;
            const hasCustom = window.customPositions && Object.keys(window.customPositions).length > 0;
            const hasBlockingTest = window.blockingTestPositions && Object.keys(window.blockingTestPositions).length > 0;
            const hasScoringOptimization = window.scoringOptimizationTestPositions && Object.keys(window.scoringOptimizationTestPositions).length > 0;
            
            if (hasOpening || hasMidgame || hasEndgame || hasEducational || hasCustom || hasBlockingTest || hasScoringOptimization) {
                setModulesLoaded(true);
            } else {
                // Check again in 100ms if modules aren't loaded yet
                setTimeout(checkModulesLoaded, 100);
            }
        };
        
        checkModulesLoaded();
    }, []);
    
    // Import position modules with proper fallbacks
    const openingPositions = window.openingPositions || {};
    const midgamePositions = window.midgamePositions || {};
    const endgamePositions = window.endgamePositions || {};
    const educationalPositions = window.educationalPositions || {};
    const customPositionsModule = window.customPositions || {};
    const blockingTestPositions = window.blockingTestPositions || {};
    const scoringOptimizationTestPositions = window.scoringOptimizationTestPositions || {};

    // Expanded position categories for R1.2 (modular structure)
    const positionCategories = {
        opening: {
            name: "Opening Positions",
            description: "Game start scenarios and early tactical decisions",
            icon: "🎯",
            subcategories: openingPositions || {
                "balanced": {
                    name: "Balanced Openings",
                    description: "Standard and balanced starting positions",
                    positions: []
                },
                "aggressive": {
                    name: "Aggressive Openings", 
                    description: "High-risk, high-reward starting positions",
                    positions: []
                },
                "defensive": {
                    name: "Defensive Openings",
                    description: "Conservative and safe starting positions", 
                    positions: []
                }
            }
        },
        midgame: {
            name: "Mid-Game Scenarios",
            description: "Tactical positions with developing patterns",
            icon: "⚔️",
            subcategories: midgamePositions || {
                "scoring": {
                    name: "Scoring Opportunities",
                    description: "Positions with clear scoring potential",
                    positions: []
                },
                "blocking": {
                    name: "Blocking Tactics",
                    description: "Positions requiring defensive play",
                    positions: []
                },
                "efficiency": {
                    name: "Efficiency Scenarios",
                    description: "Positions requiring optimal tile usage",
                    positions: []
                }
            }
        },
        endgame: {
            name: "Endgame Positions",
            description: "Final round optimization and counting",
            icon: "🏁",
            subcategories: endgamePositions || {
                "optimization": {
                    name: "Final Optimization",
                    description: "Maximizing endgame scoring",
                    positions: []
                },
                "counting": {
                    name: "Precise Counting",
                    description: "Positions requiring exact tile counting",
                    positions: []
                },
                "completion": {
                    name: "Wall Completion",
                    description: "Positions focusing on wall completion",
                    positions: []
                }
            }
        },
        educational: {
            name: "Educational Puzzles",
            description: "Learning scenarios for skill development",
            icon: "🎓",
            subcategories: educationalPositions || {
                "beginner": {
                    name: "Beginner Lessons",
                    description: "Basic concepts and simple tactics",
                    positions: []
                },
                "intermediate": {
                    name: "Intermediate Challenges",
                    description: "Advanced tactics and strategic thinking",
                    positions: []
                },
                "advanced": {
                    name: "Advanced Concepts",
                    description: "Expert-level strategic concepts",
                    positions: []
                }
            }
        },
        custom: {
            name: "Custom Positions",
            description: "User-created positions",
            icon: "💾",
            subcategories: customPositionsModule || {
                "user-created": {
                    name: "User-Created Positions",
                    description: "Custom positions created by users",
                    positions: []
                }
            }
        },
        testing: {
            name: "Testing Positions",
            description: "Positions designed for testing specific features",
            icon: "🧪",
            subcategories: {
                ...blockingTestPositions,
                ...scoringOptimizationTestPositions
            }
        }
    };

    // Available tags for filtering (2-player only)
    const availableTags = [
        "opening", "midgame", "endgame", "educational", "testing",
        "beginner", "intermediate", "advanced", "expert",
        "scoring", "blocking", "optimization", "counting",
        "2-player",
        "balanced", "aggressive", "color-focus", "high-interaction",
        "multiplier", "color-race", "floor-line", "final-round",
        "tie-breaker", "conservation", "pattern-lines", "wall-strategy",
        "pattern-detection", "simple", "complex", "multiple", "no-blocking",
        "scoring-optimization", "row-completion", "column-completion", "color-set-completion",
        "pattern-line", "multiplier-setup", "overflow-risk", "multiple-opportunities"
    ];

    // Load position with validation
    const loadPosition = useCallback(async (position) => {
        try {
            const newState = position.generate();
            
            // For local development, skip validation if no session token
            if (!sessionToken) {
                setGameState(newState);
                setStatusMessage(`✅ Loaded position: ${position.name} (local mode - auto-refresh disabled)`);
                
                // Set flag to prevent automatic refresh from overwriting the loaded position
                if (window.setPositionJustLoaded) {
                    window.setPositionJustLoaded(true);
                }
                
                onClose();
                return;
            }
            
            // Validate the generated position
            const response = await fetch('/api/v1/validate-board-state', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${sessionToken}`
                },
                body: JSON.stringify({
                    game_state: newState,
                    validation_type: 'complete'
                })
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    // Unauthorized - load position without validation for local development
                    setGameState(newState);
                    setStatusMessage(`✅ Loaded position: ${position.name} (local mode - auto-refresh disabled)`);
                    
                    // Set flag to prevent automatic refresh from overwriting the loaded position
                    if (window.setPositionJustLoaded) {
                        window.setPositionJustLoaded(true);
                    }
                    
                    onClose();
                    return;
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const validation = await response.json();
            if (!validation.valid) {
                const errorMessage = validation.errors && validation.errors.length > 0 
                    ? validation.errors[0] 
                    : 'Unknown validation error';
                setStatusMessage(`❌ Position validation failed: ${errorMessage}`);
                return;
            }
            
            setGameState(newState);
            setStatusMessage(`✅ Loaded position: ${position.name} (auto-refresh disabled - use 🔄 Refresh to resume)`);
            
            // Set flag to prevent automatic refresh from overwriting the loaded position
            if (window.setPositionJustLoaded) {
                window.setPositionJustLoaded(true);
                // Don't reset the flag automatically - let user manually refresh when needed
            }
            
            onClose();
            
        } catch (error) {
            console.error('Position loading error:', error);
            // For local development, try to load the position anyway
            try {
                const newState = position.generate();
                setGameState(newState);
                setStatusMessage(`✅ Loaded position: ${position.name} (local mode - auto-refresh disabled)`);
                
                // Set flag to prevent automatic refresh from overwriting the loaded position
                if (window.setPositionJustLoaded) {
                    window.setPositionJustLoaded(true);
                }
                
                onClose();
            } catch (fallbackError) {
                setStatusMessage(`⚠️ Failed to load position: ${error.message}`);
            }
        }
    }, [sessionToken, setGameState, setStatusMessage, onClose]);

    // Filter positions based on search and tags
    const filteredPositions = useMemo(() => {
        let positions = [];
        
        // Collect all positions from categories
        Object.values(positionCategories).forEach(category => {
            Object.values(category.subcategories).forEach(subcategory => {
                positions.push(...subcategory.positions.map(pos => ({
                    ...pos,
                    category: category.name,
                    subcategory: subcategory.name
                })));
            });
        });
        
        // Add custom positions
        positions.push(...customPositions);
        
        // Filter by category
        if (selectedCategory !== 'all') {
            positions = positions.filter(pos => 
                pos.tags.includes(selectedCategory) || 
                pos.category.toLowerCase().includes(selectedCategory)
            );
        }
        
        // Filter by search term
        if (searchTerm) {
            positions = positions.filter(pos =>
                pos.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                pos.description.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        
        // Filter by tags
        if (selectedTags.length > 0) {
            positions = positions.filter(pos =>
                selectedTags.some(tag => pos.tags.includes(tag))
            );
        }
        
        return positions;
    }, [positionCategories, customPositions, selectedCategory, searchTerm, selectedTags]);

    // Toggle tag selection
    const toggleTag = useCallback((tag) => {
        setSelectedTags(prev => 
            prev.includes(tag) 
                ? prev.filter(t => t !== tag)
                : [...prev, tag]
        );
    }, []);

    return React.createElement('div', {
        className: 'position-library-overlay'
    },
        // Header
        React.createElement('div', {
            className: 'library-header'
        },
            React.createElement('h2', null, '📚 Position Library'),
            React.createElement('button', {
                className: 'btn-close',
                onClick: onClose
            }, '×')
        ),
        
        // Loading state
        !modulesLoaded && React.createElement('div', {
            className: 'loading-state'
        },
            React.createElement('div', {
                className: 'loading-spinner'
            }),
            React.createElement('p', null, 'Loading position library...')
        ),
        
        // Search and filters
        modulesLoaded && React.createElement('div', {
            className: 'library-controls'
        },
            React.createElement('div', {
                className: 'search-section'
            },
                React.createElement('input', {
                    type: 'text',
                    placeholder: 'Search positions...',
                    value: searchTerm,
                    onChange: (e) => setSearchTerm(e.target.value),
                    className: 'search-input'
                })
            ),
            
            React.createElement('div', {
                className: 'category-filters'
            },
                React.createElement('select', {
                    value: selectedCategory,
                    onChange: (e) => setSelectedCategory(e.target.value),
                    className: 'category-select'
                },
                    React.createElement('option', { value: 'all' }, 'All Categories'),
                    ...Object.entries(positionCategories).map(([key, category]) =>
                        React.createElement('option', { key, value: key }, category.name)
                    )
                )
            ),
            
            React.createElement('div', {
                className: 'tag-filters'
            },
                React.createElement('h4', null, 'Filter by Tags:'),
                React.createElement('div', {
                    className: 'tag-list'
                },
                    ...availableTags.map(tag =>
                        React.createElement('button', {
                            key: tag,
                            className: `tag-btn ${selectedTags.includes(tag) ? 'selected' : ''}`,
                            onClick: () => toggleTag(tag)
                        }, tag)
                    )
                )
            )
        ),
        
        // Position grid
        modulesLoaded && React.createElement('div', {
            className: 'position-grid'
        },
            ...filteredPositions.map((position, index) =>
                React.createElement('div', {
                    key: index,
                    className: 'position-card'
                },
                    React.createElement('div', {
                        className: 'position-header'
                    },
                        React.createElement('h3', null, position.name),
                        React.createElement('span', {
                            className: `difficulty-badge ${position.difficulty}`
                        }, position.difficulty)
                    ),
                    React.createElement('p', {
                        className: 'position-description'
                    }, position.description),
                    React.createElement('div', {
                        className: 'position-tags'
                    },
                        ...position.tags.map(tag =>
                            React.createElement('span', {
                                key: tag,
                                className: 'position-tag'
                            }, tag)
                        )
                    ),
                    React.createElement('div', {
                        className: 'position-actions'
                    },
                        React.createElement('button', {
                            className: 'btn-primary',
                            onClick: () => loadPosition(position)
                        }, 'Load Position'),
                        React.createElement('button', {
                            className: 'btn-secondary',
                            onClick: () => setPreviewPosition(position)
                        }, 'Preview')
                    )
                )
            )
        ),
        
        // Empty state
        filteredPositions.length === 0 && React.createElement('div', {
            className: 'empty-state'
        },
            React.createElement('h3', null, 'No positions found'),
            React.createElement('p', null, 'Try adjusting your search or filters')
        ),
        
        // Position Preview Modal
        previewPosition && React.createElement(PositionPreview, {
            position: previewPosition,
            onClose: () => setPreviewPosition(null),
            onLoadPosition: loadPosition
        })
    );
});

// Export to global scope
window.PositionLibrary = PositionLibrary; 