// Blocking Test Positions - For Testing Tile Blocking Detection (R2.1)
// These positions are designed to showcase various blocking opportunities

window.blockingTestPositions = (() => {
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
            fen_string: positionData.fen_string || "test_blocking_position"  // Use specific FEN string for each position
        };
    };

    // Position definitions
    const simpleBlueBlocking = {
        name: "Simple Blue Blocking",
        description: "Opponent has 1 blue tile in pattern line 0, needs 0 more. Blue tiles available in factory.",
        difficulty: "beginner",
        tags: ["blocking", "blue", "simple", "testing", "pattern-detection"],
        generate: () => createGameState({
            fen_string: "simple_blue_blocking",
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
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [1, 0, 0, 0, 0], // 1 blue tile in line 0
                        patternLineColors: [0, -1, -1, -1, -1], // Blue (0) in line 0
                        wall: [
                            [0, 0, 0, 0, 0], // Blue not on wall yet
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
                        tiles: { 0: 2, 1: 1, 2: 1 } // 2 blue tiles available
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

    const highUrgencyRedBlocking = {
        name: "High Urgency Red Blocking",
        description: "Opponent has 2 red tiles in pattern line 2 (capacity 3), needs 1 more. High urgency blocking opportunity.",
        difficulty: "intermediate",
        tags: ["blocking", "red", "high-urgency", "testing", "pattern-detection"],
        generate: () => createGameState({
            fen_string: "high_urgency_red_blocking",
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
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [0, 0, 2, 0, 0], // 2 red tiles in line 2
                        patternLineColors: [-1, -1, 2, -1, -1], // Red (2) in line 2
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0], // Red not on wall yet
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

    const multipleBlockingOpportunities = {
        name: "Multiple Blocking Opportunities",
        description: "Opponent has tiles in multiple pattern lines - blue in line 0, yellow in line 1, red in line 2. Multiple blocking options.",
        difficulty: "advanced",
        tags: ["blocking", "multiple", "complex", "testing", "pattern-detection"],
        generate: () => createGameState({
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
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [1, 1, 2, 0, 0], // Blue in line 0, Yellow in line 1, Red in line 2
                        patternLineColors: [0, 1, 2, -1, -1], // Blue(0), Yellow(1), Red(2)
                        wall: [
                            [0, 0, 0, 0, 0], // None on wall yet
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
                        tiles: { 0: 2, 1: 1, 2: 1 } // Blue tiles
                    },
                    {
                        tiles: { 1: 2, 2: 1, 3: 1 } // Yellow tiles
                    },
                    {
                        tiles: { 2: 2, 3: 1, 4: 1 } // Red tiles
                    },
                    {
                        tiles: { 3: 1, 4: 1, 0: 1 }
                    },
                    {
                        tiles: { 4: 1, 0: 1, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 }
                },
                currentPlayer: 0
            }
        })
    };

    const noBlockingColorOnWall = {
        name: "No Blocking - Color on Wall",
        description: "Opponent has blue tiles in pattern line, but blue is already on the wall. Should NOT detect blocking opportunity.",
        difficulty: "intermediate",
        tags: ["blocking", "no-blocking", "wall-complete", "testing", "pattern-detection"],
        generate: () => createGameState({
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
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 0,
                        patternLines: [1, 0, 0, 0, 0], // 1 blue tile in line 0
                        patternLineColors: [0, -1, -1, -1, -1], // Blue (0) in line 0
                        wall: [
                            [1, 0, 0, 0, 0], // Blue ALREADY on wall!
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
        "blocking": {
            name: "Blocking Detection Tests",
            description: "Positions designed to test tile blocking detection",
            icon: "🧪",
            positions: [simpleBlueBlocking, highUrgencyRedBlocking, multipleBlockingOpportunities, noBlockingColorOnWall]
        }
    };
})(); 