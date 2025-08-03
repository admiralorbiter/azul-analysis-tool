// Scoring Optimization Test Positions - For Testing Scoring Optimization Detection (R2.2)
// These positions are designed to showcase various scoring optimization opportunities

window.scoringOptimizationTestPositions = (() => {
    // Helper function to create empty player
    const createEmptyPlayer = () => ({
        pattern_lines: [[], [], [], [], []],
        wall: Array(5).fill().map(() => Array(5).fill(null)),
        floor_line: [],
        score: 0
    });

    // Helper function to create game state from position data
    const createGameState = (positionData) => {
        const { players, factories, centerPool } = positionData.gameState;
        
        // Convert player data to the expected format
        const convertedPlayers = players.map(player => ({
            pattern_lines: player.patternLines.map((count, index) => {
                const colorIndex = player.patternLineColors[index];
                if (colorIndex === -1) {
                    return Array(count).fill(null);
                }
                // Convert numeric color index to string color
                const colorMap = ['B', 'Y', 'R', 'K', 'W'];
                const colorString = colorMap[colorIndex];
                return Array(count).fill(colorString);
            }),
            wall: player.wall,
            floor_line: player.floorTiles || [],
            score: player.score
        }));
        
        // Convert factories data
        const convertedFactories = factories.map(factory => {
            const factoryArray = [];
            Object.entries(factory.tiles).forEach(([color, count]) => {
                for (let i = 0; i < count; i++) {
                    factoryArray.push(['B', 'Y', 'R', 'K', 'W'][color]);
                }
            });
            return factoryArray;
        });
        
        // Convert center pool
        const convertedCenter = [];
        Object.entries(centerPool.tiles).forEach(([color, count]) => {
            for (let i = 0; i < count; i++) {
                convertedCenter.push(['B', 'Y', 'R', 'K', 'W'][color]);
            }
        });
        
        return {
            factories: convertedFactories,
            center: convertedCenter,
            players: convertedPlayers,
            fen_string: positionData.fen_string || "test_scoring_optimization_position"
        };
    };

    // Position definitions
    const simpleRowCompletion = {
        name: "Simple Row Completion",
        description: "Player has 4 tiles in row 0, needs 1 more to complete row for 2 points bonus.",
        difficulty: "beginner",
        tags: ["scoring-optimization", "row-completion", "wall-bonus", "testing"],
        generate: () => createGameState({
            fen_string: "simple_row_completion",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 0], // 4 tiles in row 0, missing last position
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    }
                ],
                factories: [
                    {
                        tiles: { 4: 2, 0: 1, 1: 1 } // White tiles available (needed for row completion)
                    },
                    {
                        tiles: { 1: 2, 2: 1, 3: 1 }
                    },
                    {
                        tiles: { 2: 2, 3: 1, 4: 1 }
                    },
                    {
                        tiles: { 3: 2, 4: 1, 0: 1 }
                    },
                    {
                        tiles: { 4: 2, 0: 1, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 }
                },
                currentPlayer: 0
            }
        })
    };

    const highValueColumnCompletion = {
        name: "High Value Column Completion",
        description: "Player has 4 tiles in column 0, needs 1 more to complete column for 7 points bonus (highest individual bonus).",
        difficulty: "intermediate",
        tags: ["scoring-optimization", "column-completion", "high-bonus", "testing"],
        generate: () => createGameState({
            fen_string: "high_value_column_completion",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 0, 0, 0, 0], // 4 tiles in column 0, missing last position
                            [1, 0, 0, 0, 0],
                            [1, 0, 0, 0, 0],
                            [1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]  // Missing tile here
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    }
                ],
                factories: [
                    {
                        tiles: { 0: 2, 1: 1, 2: 1 } // Blue tiles available (needed for column completion)
                    },
                    {
                        tiles: { 1: 2, 2: 1, 3: 1 }
                    },
                    {
                        tiles: { 2: 2, 3: 1, 4: 1 }
                    },
                    {
                        tiles: { 3: 2, 4: 1, 0: 1 }
                    },
                    {
                        tiles: { 4: 2, 0: 1, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 }
                },
                currentPlayer: 0
            }
        })
    };

    const colorSetCompletion = {
        name: "Color Set Completion",
        description: "Player has 4 blue tiles on wall, needs 1 more to complete blue color set for 10 points bonus (highest bonus in game).",
        difficulty: "intermediate",
        tags: ["scoring-optimization", "color-set-completion", "highest-bonus", "testing"],
        generate: () => createGameState({
            fen_string: "color_set_completion",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 0, 0, 0, 0], // Blue tile in row 0, col 0
                            [0, 0, 0, 0, 1], // Blue tile in row 1, col 4
                            [0, 0, 0, 1, 0], // Blue tile in row 2, col 3
                            [0, 0, 1, 0, 0], // Blue tile in row 3, col 2
                            [0, 0, 0, 0, 0]  // Missing blue tile here
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    }
                ],
                factories: [
                    {
                        tiles: { 0: 2, 1: 1, 2: 1 } // Blue tiles available
                    },
                    {
                        tiles: { 1: 2, 2: 1, 3: 1 }
                    },
                    {
                        tiles: { 2: 2, 3: 1, 4: 1 }
                    },
                    {
                        tiles: { 3: 2, 4: 1, 0: 1 }
                    },
                    {
                        tiles: { 4: 2, 0: 1, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 }
                },
                currentPlayer: 0
            }
        })
    };

    const highValuePatternLine = {
        name: "High Value Pattern Line",
        description: "Player has 3 tiles in pattern line 4 (capacity 5), needs 2 more for 15 points bonus (highest pattern line bonus).",
        difficulty: "intermediate",
        tags: ["scoring-optimization", "pattern-line", "high-value", "testing"],
        generate: () => createGameState({
            fen_string: "high_value_pattern_line",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 3], // 3 tiles in pattern line 4
                        patternLineColors: [-1, -1, -1, -1, 2], // Red tiles in line 4
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    }
                ],
                factories: [
                    {
                        tiles: { 0: 1, 1: 1, 2: 1 }
                    },
                    {
                        tiles: { 1: 1, 2: 3, 3: 1 } // 3 red tiles available
                    },
                    {
                        tiles: { 2: 1, 3: 1, 4: 1 }
                    },
                    {
                        tiles: { 3: 1, 4: 1, 0: 1 }
                    },
                    {
                        tiles: { 4: 1, 0: 1, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } // 2 red tiles in center
                },
                currentPlayer: 0
            }
        })
    };

    const floorLineRisk = {
        name: "Floor Line Risk",
        description: "Player has 3 tiles on floor line (-4 points penalty), opportunity to place tiles on wall to reduce penalty.",
        difficulty: "intermediate",
        tags: ["scoring-optimization", "floor-line", "penalty-reduction", "testing"],
        generate: () => createGameState({
            fen_string: "floor_line_risk",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: [0, 1, 2] // 3 tiles on floor (-4 points penalty)
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    }
                ],
                factories: [
                    {
                        tiles: { 0: 2, 1: 1, 2: 1 } // Blue tiles available
                    },
                    {
                        tiles: { 1: 2, 2: 1, 3: 1 }
                    },
                    {
                        tiles: { 2: 2, 3: 1, 4: 1 }
                    },
                    {
                        tiles: { 3: 2, 4: 1, 0: 1 }
                    },
                    {
                        tiles: { 4: 2, 0: 1, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 }
                },
                currentPlayer: 0
            }
        })
    };

    const multiplierSetup = {
        name: "Multiplier Setup",
        description: "Player has tiles positioned to enable multiple bonuses simultaneously (row + column + color set).",
        difficulty: "advanced",
        tags: ["scoring-optimization", "multiplier-setup", "complex", "testing"],
        generate: () => createGameState({
            fen_string: "multiplier_setup",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 0], // 4 tiles in row 0
                            [1, 0, 0, 0, 0], // 1 tile in column 0
                            [1, 0, 0, 0, 0], // 1 tile in column 0
                            [1, 0, 0, 0, 0], // 1 tile in column 0
                            [0, 0, 0, 0, 0]  // Missing tile here would complete row, column, and color set
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    }
                ],
                factories: [
                    {
                        tiles: { 0: 2, 1: 1, 2: 1 } // Blue tiles available
                    },
                    {
                        tiles: { 1: 2, 2: 1, 3: 1 }
                    },
                    {
                        tiles: { 2: 2, 3: 1, 4: 1 }
                    },
                    {
                        tiles: { 3: 2, 4: 1, 0: 1 }
                    },
                    {
                        tiles: { 4: 2, 0: 1, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 }
                },
                currentPlayer: 0
            }
        })
    };

    const patternLineOverflowRisk = {
        name: "Pattern Line Overflow Risk",
        description: "Player has 4 tiles in pattern line 4 (capacity 5), taking more tiles would cause overflow to floor line.",
        difficulty: "intermediate",
        tags: ["scoring-optimization", "pattern-line", "overflow-risk", "testing"],
        generate: () => createGameState({
            fen_string: "pattern_line_overflow_risk",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 4], // 4 tiles in pattern line 4 (capacity 5)
                        patternLineColors: [-1, -1, -1, -1, 2], // Red tiles in line 4
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    }
                ],
                factories: [
                    {
                        tiles: { 0: 1, 1: 1, 2: 1 }
                    },
                    {
                        tiles: { 1: 1, 2: 3, 3: 1 } // 3 red tiles available (would cause overflow)
                    },
                    {
                        tiles: { 2: 1, 3: 1, 4: 1 }
                    },
                    {
                        tiles: { 3: 1, 4: 1, 0: 1 }
                    },
                    {
                        tiles: { 4: 1, 0: 1, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } // 2 red tiles in center
                },
                currentPlayer: 0
            }
        })
    };

    const multipleCompletionOpportunities = {
        name: "Multiple Completion Opportunities",
        description: "Player has multiple completion opportunities: row 0 (4/5), column 1 (4/5), and blue color set (4/5).",
        difficulty: "advanced",
        tags: ["scoring-optimization", "multiple-opportunities", "complex", "testing"],
        generate: () => createGameState({
            fen_string: "multiple_completion_opportunities",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 0], // 4 tiles in row 0
                            [0, 1, 0, 0, 0], // 1 tile in column 1
                            [0, 1, 0, 0, 0], // 1 tile in column 1
                            [0, 1, 0, 0, 0], // 1 tile in column 1
                            [0, 1, 0, 0, 0]  // 1 tile in column 1
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    }
                ],
                factories: [
                    {
                        tiles: { 0: 2, 1: 1, 2: 1 } // Blue tiles available
                    },
                    {
                        tiles: { 1: 2, 2: 1, 3: 1 }
                    },
                    {
                        tiles: { 2: 2, 3: 1, 4: 1 }
                    },
                    {
                        tiles: { 3: 2, 4: 1, 0: 1 }
                    },
                    {
                        tiles: { 4: 2, 0: 1, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 }
                },
                currentPlayer: 0
            }
        })
    };

    // Return the organized structure
    return {
        "scoring-optimization": {
            name: "Scoring Optimization Tests",
            description: "Positions designed to test scoring optimization detection",
            icon: "🎯",
            positions: [
                simpleRowCompletion,
                highValueColumnCompletion,
                colorSetCompletion,
                highValuePatternLine,
                floorLineRisk,
                multiplierSetup,
                patternLineOverflowRisk,
                multipleCompletionOpportunities
            ]
        }
    };
})(); 