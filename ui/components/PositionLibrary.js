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
    
    // Expanded position categories for R1.2
    const positionCategories = {
        opening: {
            name: "Opening Positions",
            description: "Game start scenarios and early tactical decisions",
            icon: "🎯",
            subcategories: {
                "2-player": {
                    name: "2-Player Openings",
                    description: "Duel scenarios with focused strategies",
                    positions: [
                        {
                            name: "Balanced Start",
                            description: "Standard opening with mixed factory colors",
                            difficulty: "beginner",
                            tags: ["opening", "balanced", "2-player"],
                                                         generate: () => ({
                                 factories: [
                                     ['B', 'B', 'Y', 'R'],
                                     ['B', 'Y', 'R', 'K'],
                                     ['Y', 'R', 'K', 'W'],
                                     ['R', 'K', 'W', 'B'],
                                     ['K', 'W', 'B', 'Y']
                                 ],
                                 center: [],
                                 players: Array(2).fill().map(() => ({
                                     pattern_lines: [[], [], [], [], []],
                                     wall: Array(5).fill().map(() => Array(5).fill(null)),
                                     floor_line: [],
                                     score: 0
                                 }))
                             })
                        },
                        {
                            name: "Color-Focused Start",
                            description: "Factories with concentrated colors for aggressive play",
                            difficulty: "intermediate",
                            tags: ["opening", "aggressive", "color-focus", "2-player"],
                                                         generate: () => ({
                                 factories: [
                                     ['B', 'B', 'B', 'B'],
                                     ['B', 'B', 'B', 'B'],
                                     ['B', 'B', 'B', 'B'],
                                     ['B', 'B', 'B', 'B'],
                                     ['B', 'B', 'B', 'B']
                                 ],
                                 center: [],
                                 players: Array(2).fill().map(() => ({
                                     pattern_lines: [[], [], [], [], []],
                                     wall: Array(5).fill().map(() => Array(5).fill(null)),
                                     floor_line: [],
                                     score: 0
                                 }))
                             })
                        }
                    ]
                }
            }
        },
        midgame: {
            name: "Mid-Game Scenarios",
            description: "Tactical positions with developing patterns",
            icon: "⚔️",
            subcategories: {
                "scoring": {
                    name: "Scoring Opportunities",
                    description: "Positions with clear scoring potential",
                    positions: [
                        {
                            name: "Multiplier Setup",
                            description: "Positioning for row/column bonuses",
                            difficulty: "intermediate",
                            tags: ["midgame", "scoring", "multiplier"],
                                                         generate: () => ({
                                 factories: [
                                     ['B', 'Y'],
                                     ['Y', 'R'],
                                     ['R', 'K'],
                                     ['K', 'W'],
                                     ['W', 'B']
                                 ],
                                 center: ['B', 'Y'],
                                 players: Array(2).fill().map((_, playerIdx) => ({
                                     pattern_lines: [['B', 'B'], ['Y', 'Y', 'Y'], [], [], []],
                                     wall: Array(5).fill().map((_, row) => 
                                         Array(5).fill().map((_, col) => 
                                             row < 2 && col < 2 ? 'B' : null
                                         )
                                     ),
                                     floor_line: [],
                                     score: 12 + playerIdx * 3
                                 }))
                             })
                        },
                        {
                            name: "Color Completion Race",
                            description: "Competing for color completion bonuses",
                            difficulty: "advanced",
                            tags: ["midgame", "scoring", "color-race"],
                                                         generate: () => ({
                                 factories: [
                                     ['B', 'R', 'W'],
                                     ['Y', 'K', 'B'],
                                     ['R', 'W', 'Y'],
                                     ['K', 'B', 'R'],
                                     ['W', 'Y', 'K']
                                 ],
                                 center: ['B', 'B', 'R', 'W'],
                                 players: Array(2).fill().map((_, playerIdx) => ({
                                     pattern_lines: [['B', 'B', 'B'], [], ['R', 'R'], [], ['W']],
                                     wall: Array(5).fill().map((_, row) => 
                                         Array(5).fill().map((_, col) => 
                                             (row + col) % 2 === playerIdx ? 'B' : null
                                         )
                                     ),
                                     floor_line: [],
                                     score: 18 + playerIdx * 6
                                 }))
                             })
                        }
                    ]
                },
                "blocking": {
                    name: "Blocking Tactics",
                    description: "Positions requiring defensive play",
                    positions: [
                        {
                            name: "Floor Line Crisis",
                            description: "Managing negative points while scoring",
                            difficulty: "expert",
                            tags: ["midgame", "blocking", "floor-line"],
                                                         generate: () => ({
                                 factories: [
                                     ['B', 'Y'],
                                     ['B', 'Y'],
                                     ['B', 'Y'],
                                     ['B', 'Y'],
                                     ['B', 'Y']
                                 ],
                                 center: ['B', 'B', 'B', 'Y', 'Y'],
                                 players: Array(2).fill().map((_, playerIdx) => ({
                                     pattern_lines: [['B', 'B', 'B', 'B'], ['Y', 'Y', 'Y', 'Y'], [], [], []],
                                     wall: Array(5).fill().map((_, row) => 
                                         Array(5).fill().map((_, col) => 
                                             row < 2 ? 'B' : null
                                         )
                                     ),
                                     floor_line: ['B', 'Y', 'B'],
                                     score: 8 + playerIdx * 4
                                 }))
                             })
                        }
                    ]
                }
            }
        },
        endgame: {
            name: "Endgame Positions",
            description: "Final round optimization and counting",
            icon: "🏁",
            subcategories: {
                "optimization": {
                    name: "Final Optimization",
                    description: "Maximizing endgame scoring",
                    positions: [
                        {
                            name: "Last Round Efficiency",
                            description: "Final moves for maximum points",
                            difficulty: "expert",
                            tags: ["endgame", "optimization", "final-round"],
                                                         generate: () => ({
                                 factories: [
                                     ['R'],
                                     ['R'],
                                     ['R'],
                                     ['R'],
                                     ['R']
                                 ],
                                 center: ['R', 'R', 'R', 'W'],
                                 players: Array(2).fill().map((_, playerIdx) => ({
                                     pattern_lines: [[], [], ['R', 'R', 'R'], [], ['W']],
                                     wall: Array(5).fill().map((_, row) => 
                                         Array(5).fill().map((_, col) => row < 3 ? 'B' : null)
                                     ),
                                     floor_line: ['R', 'W'],
                                     score: 45 + playerIdx * 8
                                 }))
                             })
                        },
                        {
                            name: "Tie-Breaker Scenario",
                            description: "Close game with precise counting needed",
                            difficulty: "expert",
                            tags: ["endgame", "optimization", "tie-breaker"],
                                                         generate: () => ({
                                 factories: [
                                     ['K'],
                                     ['K'],
                                     ['K'],
                                     ['K'],
                                     ['K']
                                 ],
                                 center: ['K', 'K'],
                                 players: Array(2).fill().map((_, playerIdx) => ({
                                     pattern_lines: [[], [], [], ['K', 'K'], []],
                                     wall: Array(5).fill().map((_, row) => 
                                         Array(5).fill().map((_, col) => 
                                             row === 3 ? 'B' : (row < 3 ? 'B' : null)
                                         )
                                     ),
                                     floor_line: [],
                                     score: 52 + playerIdx * 2
                                 }))
                             })
                        }
                    ]
                },
                "counting": {
                    name: "Precise Counting",
                    description: "Positions requiring exact tile counting",
                    positions: [
                        {
                            name: "Tile Conservation Puzzle",
                            description: "Ensuring all tiles are accounted for",
                            difficulty: "expert",
                            tags: ["endgame", "counting", "conservation"],
                                                         generate: () => ({
                                 factories: [
                                     [],
                                     [],
                                     [],
                                     [],
                                     []
                                 ],
                                 center: ['B', 'Y', 'R'],
                                 players: Array(2).fill().map((_, playerIdx) => ({
                                     pattern_lines: [[], [], [], [], []],
                                     wall: Array(5).fill().map((_, row) => 
                                         Array(5).fill().map((_, col) => 
                                             row < 4 ? 'B' : null
                                         )
                                     ),
                                     floor_line: ['B', 'Y', 'R'],
                                     score: 48 + playerIdx * 1
                                 }))
                             })
                        }
                    ]
                }
            }
        },
        educational: {
            name: "Educational Puzzles",
            description: "Learning scenarios for skill development",
            icon: "🎓",
            subcategories: {
                "beginner": {
                    name: "Beginner Lessons",
                    description: "Basic concepts and simple tactics",
                    positions: [
                        {
                            name: "Pattern Line Basics",
                            description: "Understanding pattern line mechanics",
                            difficulty: "beginner",
                            tags: ["educational", "beginner", "pattern-lines"],
                                                         generate: () => ({
                                 factories: [
                                     ['B', 'B'],
                                     ['B', 'B'],
                                     ['B', 'B'],
                                     ['B', 'B'],
                                     ['B', 'B']
                                 ],
                                 center: [],
                                 players: Array(2).fill().map(() => ({
                                     pattern_lines: [[], [], [], [], []],
                                     wall: Array(5).fill().map(() => Array(5).fill(null)),
                                     floor_line: [],
                                     score: 0
                                 }))
                             })
                        }
                    ]
                },
                "intermediate": {
                    name: "Intermediate Challenges",
                    description: "Advanced tactics and strategic thinking",
                    positions: [
                        {
                            name: "Wall Completion Strategy",
                            description: "Planning for wall completion bonuses",
                            difficulty: "intermediate",
                            tags: ["educational", "intermediate", "wall-strategy"],
                                                         generate: () => ({
                                 factories: [
                                     ['B', 'Y'],
                                     ['B', 'Y'],
                                     ['B', 'Y'],
                                     ['B', 'Y'],
                                     ['B', 'Y']
                                 ],
                                 center: ['B', 'Y'],
                                 players: Array(2).fill().map((_, playerIdx) => ({
                                     pattern_lines: [['B', 'B'], ['Y', 'Y', 'Y'], [], [], []],
                                     wall: Array(5).fill().map((_, row) => 
                                         Array(5).fill().map((_, col) => 
                                             row < 2 ? 'B' : null
                                         )
                                     ),
                                     floor_line: [],
                                     score: 6 + playerIdx * 3
                                 }))
                             })
                        }
                    ]
                }
            }
        }
    };

    // Available tags for filtering (2-player only)
    const availableTags = [
        "opening", "midgame", "endgame", "educational",
        "beginner", "intermediate", "advanced", "expert",
        "scoring", "blocking", "optimization", "counting",
        "2-player",
        "balanced", "aggressive", "color-focus", "high-interaction",
        "multiplier", "color-race", "floor-line", "final-round",
        "tie-breaker", "conservation", "pattern-lines", "wall-strategy"
    ];

    // Load position with validation
    const loadPosition = useCallback(async (position) => {
        try {
            const newState = position.generate();
            
            // For local development, skip validation if no session token
            if (!sessionToken) {
                setGameState(newState);
                setStatusMessage(`✅ Loaded position: ${position.name} (local mode)`);
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
                    setStatusMessage(`✅ Loaded position: ${position.name} (local mode)`);
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
            setStatusMessage(`✅ Loaded position: ${position.name}`);
            
            // Set flag to prevent automatic refresh from overwriting the loaded position
            if (window.setPositionJustLoaded) {
                window.setPositionJustLoaded(true);
                // Reset the flag after 10 seconds to allow normal refresh to resume
                setTimeout(() => {
                    window.setPositionJustLoaded(false);
                }, 10000);
            }
            
            onClose();
            
        } catch (error) {
            console.error('Position loading error:', error);
            // For local development, try to load the position anyway
            try {
                const newState = position.generate();
                setGameState(newState);
                setStatusMessage(`✅ Loaded position: ${position.name} (local mode)`);
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
        
        // Search and filters
        React.createElement('div', {
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
        React.createElement('div', {
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
                            onClick: () => {/* TODO: Preview position */}
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
        )
    );
});

// Export to global scope
window.PositionLibrary = PositionLibrary; 