// Floor Line Test Positions - For Testing Floor Line Management Patterns (R2.1)
// These positions are designed to showcase various floor line management scenarios

window.floorLineTestPositions = (() => {
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
            fen_string: positionData.fen_string || "test_floor_line_position"
        };
    };

    // Risk Mitigation Positions
    const risk_mitigation_critical = {
        name: "Critical Risk Mitigation",
        description: "Player has 6 tiles on floor line - critical risk that needs immediate attention",
        difficulty: "expert",
        tags: ["floor_line", "risk_mitigation", "critical", "penalty_reduction", "testing"],
        generate: () => createGameState({
            fen_string: "critical_floor_risk",
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
                        floorTiles: [0, 1, 2, 3, 4, 5] // 6 tiles on floor line
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } }, // Blue tiles available
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    const risk_mitigation_high = {
        name: "High Risk Mitigation",
        description: "Player has 4 tiles on floor line - high risk that should be addressed soon",
        difficulty: "advanced",
        tags: ["floor_line", "risk_mitigation", "high", "penalty_reduction", "testing"],
        generate: () => createGameState({
            fen_string: "high_floor_risk",
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
                        floorTiles: [0, 1, 2, 3] // 4 tiles on floor line
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

    const risk_mitigation_medium = {
        name: "Medium Risk Mitigation",
        description: "Player has 2 tiles on floor line - medium risk with good mitigation opportunities",
        difficulty: "intermediate",
        tags: ["floor_line", "risk_mitigation", "medium", "penalty_reduction", "testing"],
        generate: () => createGameState({
            fen_string: "medium_floor_risk",
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
                        floorTiles: [0, 1] // 2 tiles on floor line
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

    // Timing Optimization Positions
    const early_game_timing = {
        name: "Early Game Timing",
        description: "Early game position with floor tiles that should be cleared strategically",
        difficulty: "intermediate",
        tags: ["floor_line", "timing", "early_game", "strategic_clearance", "testing"],
        generate: () => createGameState({
            fen_string: "early_game_floor_timing",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 5, // Early game score
                        patternLines: [1, 0, 0, 0, 0],
                        patternLineColors: [0, -1, -1, -1, -1],
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: [0, 1] // 2 tiles on floor line
                    },
                    {
                        id: 1,
                        score: 3,
                        patternLines: [0, 1, 0, 0, 0],
                        patternLineColors: [-1, 1, -1, -1, -1],
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

    const mid_game_timing = {
        name: "Mid Game Timing",
        description: "Mid game position requiring strategic floor line management",
        difficulty: "advanced",
        tags: ["floor_line", "timing", "mid_game", "strategic_management", "testing"],
        generate: () => createGameState({
            fen_string: "mid_game_floor_timing",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 25, // Mid game score
                        patternLines: [2, 1, 1, 0, 0],
                        patternLineColors: [0, 1, 2, -1, -1],
                        wall: [
                            [1, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: [0, 1, 2] // 3 tiles on floor line
                    },
                    {
                        id: 1,
                        score: 22,
                        patternLines: [1, 2, 0, 1, 0],
                        patternLineColors: [3, 4, -1, 0, -1],
                        wall: [
                            [0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0],
                            [1, 0, 0, 0, 0],
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

    const endgame_timing = {
        name: "Endgame Timing",
        description: "Endgame position with critical floor line penalties to minimize",
        difficulty: "expert",
        tags: ["floor_line", "timing", "endgame", "penalty_minimization", "testing"],
        generate: () => createGameState({
            fen_string: "endgame_floor_timing",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 65, // Endgame score
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: [0, 1, 2, 3, 4] // 5 tiles on floor line
                    },
                    {
                        id: 1,
                        score: 58,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1]
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

    // Trade-off Positions
    const wall_completion_trade_off = {
        name: "Wall Completion Trade-off",
        description: "Position where accepting floor penalty enables valuable wall completion",
        difficulty: "advanced",
        tags: ["floor_line", "trade_off", "wall_completion", "strategic_acceptance", "testing"],
        generate: () => createGameState({
            fen_string: "wall_completion_trade_off",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 30,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 0], // Almost complete row
                            [1, 1, 1, 0, 1],
                            [1, 1, 0, 1, 1],
                            [1, 0, 1, 1, 1],
                            [0, 1, 1, 1, 1]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 28,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1]
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

    // Endgame Management Positions
    const endgame_penalty_minimization = {
        name: "Endgame Penalty Minimization",
        description: "Endgame position with multiple floor tiles requiring strategic clearance",
        difficulty: "expert",
        tags: ["floor_line", "endgame", "penalty_minimization", "strategic_clearance", "testing"],
        generate: () => createGameState({
            fen_string: "endgame_penalty_minimization",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 70,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: [0, 1, 2, 3, 4, 5] // 6 tiles on floor line
                    },
                    {
                        id: 1,
                        score: 65,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1]
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

    // Blocking Opportunities
    const opponent_blocking_opportunity = {
        name: "Opponent Blocking Opportunity",
        description: "Position where taking floor penalty blocks opponent's valuable completion",
        difficulty: "advanced",
        tags: ["floor_line", "blocking", "opponent_disruption", "strategic_penalty", "testing"],
        generate: () => createGameState({
            fen_string: "opponent_blocking_opportunity",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 25,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 20,
                        patternLines: [2, 0, 0, 0, 0], // Almost complete pattern line
                        patternLineColors: [0, -1, -1, -1, -1], // Blue tiles
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
                    { tiles: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1 } }, // Blue tiles available
                    { tiles: { 0: 1, 1: 2, 2: 1, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 2, 3: 1, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 2, 4: 1 } },
                    { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 2 } }
                ],
                centerPool: { tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 } }
            }
        })
    };

    // Efficiency Patterns
    const efficient_floor_clearance = {
        name: "Efficient Floor Clearance",
        description: "Position with multiple opportunities for efficient floor line clearing",
        difficulty: "intermediate",
        tags: ["floor_line", "efficiency", "clearance", "optimization", "testing"],
        generate: () => createGameState({
            fen_string: "efficient_floor_clearance",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 15,
                        patternLines: [1, 1, 0, 0, 0],
                        patternLineColors: [0, 1, -1, -1, -1],
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: [0, 1, 2] // 3 tiles on floor line
                    },
                    {
                        id: 1,
                        score: 12,
                        patternLines: [0, 1, 1, 0, 0],
                        patternLineColors: [-1, 2, 3, -1, -1],
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

    // Complex Scenarios
    const complex_risk_reward = {
        name: "Complex Risk-Reward Analysis",
        description: "Complex position requiring analysis of multiple floor line trade-offs",
        difficulty: "expert",
        tags: ["floor_line", "complex", "risk_reward", "multi_factor_analysis", "testing"],
        generate: () => createGameState({
            fen_string: "complex_risk_reward",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 45,
                        patternLines: [2, 1, 1, 0, 0],
                        patternLineColors: [0, 1, 2, -1, -1],
                        wall: [
                            [1, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: [0, 1, 2, 3] // 4 tiles on floor line
                    },
                    {
                        id: 1,
                        score: 42,
                        patternLines: [1, 2, 0, 1, 0],
                        patternLineColors: [3, 4, -1, 0, -1],
                        wall: [
                            [0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0],
                            [1, 0, 0, 0, 0],
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
        risk_mitigation: {
            name: "Risk Mitigation",
            description: "Positions with floor line risk that needs mitigation",
            positions: [risk_mitigation_critical, risk_mitigation_high, risk_mitigation_medium]
        },
        timing_optimization: {
            name: "Timing Optimization",
            description: "Positions requiring strategic floor line timing",
            positions: [early_game_timing, mid_game_timing, endgame_timing]
        },
        trade_offs: {
            name: "Trade-offs",
            description: "Positions where floor penalties enable valuable completions",
            positions: [wall_completion_trade_off]
        },
        endgame_management: {
            name: "Endgame Management",
            description: "Endgame positions with critical floor line penalties",
            positions: [endgame_penalty_minimization]
        },
        blocking: {
            name: "Blocking Opportunities",
            description: "Positions where floor line can be used for blocking",
            positions: [opponent_blocking_opportunity]
        },
        efficiency: {
            name: "Efficiency Patterns",
            description: "Positions with floor line efficiency optimization",
            positions: [efficient_floor_clearance]
        },
        complex: {
            name: "Complex Scenarios",
            description: "Complex positions requiring multi-factor analysis",
            positions: [complex_risk_reward]
        }
    };
})();