// UI Testing Positions - For Comprehensive UI Testing (Floor Line & Board Display)
// These positions are designed to test specific UI functionality and display features

window.uiTestingPositions = (() => {
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
            floor_line: (player.floorTiles || []).map(tileIndex => {
                // Convert numeric tile index to color string
                const colorMap = ['B', 'Y', 'R', 'K', 'W'];
                return colorMap[tileIndex] || 'W';
            }),
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
            fen_string: positionData.fen_string || "test_ui_position"
        };
    };

    // ===== FLOOR LINE PENALTY TESTING =====
    
    // Test floor line penalty display (1 tile = -1 point)
    const floor_line_penalty_1 = {
        name: "Floor Line Penalty - 1 Tile",
        description: "Test floor line display with 1 tile (-1 point penalty)",
        difficulty: "beginner",
        tags: ["floor_line", "penalty_display", "ui_testing", "1_tile"],
        generate: () => createGameState({
            fen_string: "floor_penalty_1",
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
                        floorTiles: [0] // 1 tile = -1 point
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    // Test floor line penalty display (2 tiles = -2 points)
    const floor_line_penalty_2 = {
        name: "Floor Line Penalty - 2 Tiles",
        description: "Test floor line display with 2 tiles (-2 points penalty)",
        difficulty: "beginner",
        tags: ["floor_line", "penalty_display", "ui_testing", "2_tiles"],
        generate: () => createGameState({
            fen_string: "floor_penalty_2",
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
                        floorTiles: [0, 1] // 2 tiles = -2 points
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    // Test floor line penalty display (3 tiles = -3 points)
    const floor_line_penalty_3 = {
        name: "Floor Line Penalty - 3 Tiles",
        description: "Test floor line display with 3 tiles (-3 points penalty)",
        difficulty: "intermediate",
        tags: ["floor_line", "penalty_display", "ui_testing", "3_tiles"],
        generate: () => createGameState({
            fen_string: "floor_penalty_3",
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
                        floorTiles: [0, 1, 2] // 3 tiles = -3 points
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    // Test floor line penalty display (4 tiles = -4 points)
    const floor_line_penalty_4 = {
        name: "Floor Line Penalty - 4 Tiles",
        description: "Test floor line display with 4 tiles (-4 points penalty)",
        difficulty: "intermediate",
        tags: ["floor_line", "penalty_display", "ui_testing", "4_tiles"],
        generate: () => createGameState({
            fen_string: "floor_penalty_4",
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
                        floorTiles: [0, 1, 2, 3] // 4 tiles = -4 points
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    // Test floor line penalty display (5 tiles = -5 points)
    const floor_line_penalty_5 = {
        name: "Floor Line Penalty - 5 Tiles",
        description: "Test floor line display with 5 tiles (-5 points penalty)",
        difficulty: "advanced",
        tags: ["floor_line", "penalty_display", "ui_testing", "5_tiles"],
        generate: () => createGameState({
            fen_string: "floor_penalty_5",
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
                        floorTiles: [0, 1, 2, 3, 4] // 5 tiles = -5 points
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    // Test floor line penalty display (6 tiles = -6 points)
    const floor_line_penalty_6 = {
        name: "Floor Line Penalty - 6 Tiles",
        description: "Test floor line display with 6 tiles (-6 points penalty)",
        difficulty: "expert",
        tags: ["floor_line", "penalty_display", "ui_testing", "6_tiles"],
        generate: () => createGameState({
            fen_string: "floor_penalty_6",
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
                        floorTiles: [0, 1, 2, 3, 4, 5] // 6 tiles = -6 points
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    // ===== BOARD DISPLAY TESTING =====

    // Test pattern line capacity display (1-5 tiles)
    const pattern_line_capacity_test = {
        name: "Pattern Line Capacity Test",
        description: "Test pattern line display with various capacities (1-5 tiles)",
        difficulty: "beginner",
        tags: ["pattern_lines", "capacity_display", "ui_testing", "board_display"],
        generate: () => createGameState({
            fen_string: "pattern_capacity_test",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 0,
                        patternLines: [1, 2, 3, 4, 5], // Test all capacities
                        patternLineColors: [0, 1, 2, 3, 4], // Different colors
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    // Test wall completion display
    const wall_completion_display_test = {
        name: "Wall Completion Display Test",
        description: "Test wall display with various completion patterns",
        difficulty: "intermediate",
        tags: ["wall_display", "completion_patterns", "ui_testing", "board_display"],
        generate: () => createGameState({
            fen_string: "wall_completion_test",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 0,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 1], // Complete row
                            [1, 0, 0, 0, 0], // Partial row
                            [0, 1, 0, 0, 0], // Partial row
                            [0, 0, 1, 0, 0], // Partial row
                            [0, 0, 0, 1, 0]  // Partial row
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    // Test factory display with various tile counts
    const factory_display_test = {
        name: "Factory Display Test",
        description: "Test factory display with various tile configurations",
        difficulty: "beginner",
        tags: ["factory_display", "tile_counts", "ui_testing", "board_display"],
        generate: () => createGameState({
            fen_string: "factory_display_test",
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
                    { tiles: { 0: 4, 1: 0, 2: 0, 3: 0, 4: 0 } }, // All blue
                    { tiles: { 0: 0, 1: 4, 2: 0, 3: 0, 4: 0 } }, // All yellow
                    { tiles: { 0: 0, 1: 0, 2: 4, 3: 0, 4: 0 } }, // All red
                    { tiles: { 0: 0, 1: 0, 2: 0, 3: 4, 4: 0 } }, // All black
                    { tiles: { 0: 0, 1: 0, 2: 0, 3: 0, 4: 4 } }  // All white
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    // Test center pool display with first player marker
    const center_pool_first_player_test = {
        name: "Center Pool First Player Test",
        description: "Test center pool display with first player marker",
        difficulty: "beginner",
        tags: ["center_pool", "first_player_marker", "ui_testing", "board_display"],
        generate: () => createGameState({
            fen_string: "center_first_player_test",
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 2, 1: 2, 2: 2, 3: 2, 4: 2 } } // More tiles for visibility
            }
        })
    };

    // Test score display with various scores
    const score_display_test = {
        name: "Score Display Test",
        description: "Test score display with various point values",
        difficulty: "beginner",
        tags: ["score_display", "ui_testing", "board_display"],
        generate: () => createGameState({
            fen_string: "score_display_test",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 45, // High score
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 1], // Complete row for points
                            [1, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 0],
                            [0, 0, 0, 1, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 12, // Lower score
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    // Return the position categories
    return {
        floor_line_penalties: {
            name: "Floor Line Penalty Testing",
            description: "Test floor line penalty display with various tile counts",
            positions: [
                floor_line_penalty_1,
                floor_line_penalty_2,
                floor_line_penalty_3,
                floor_line_penalty_4,
                floor_line_penalty_5,
                floor_line_penalty_6
            ]
        },
        board_display: {
            name: "Board Display Testing",
            description: "Test various board display components",
            positions: [
                pattern_line_capacity_test,
                wall_completion_display_test,
                factory_display_test,
                center_pool_first_player_test,
                score_display_test
            ]
        }
    };
})(); 