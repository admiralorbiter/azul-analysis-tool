// Strategic Pattern Test Positions - For Testing Strategic Pattern Analysis (Phase 2.4)
// These positions are designed to showcase various strategic patterns including:
// - Factory control opportunities (domination, disruption, timing, color control)
// - Endgame counting scenarios (tile conservation, scoring potential, risk assessment)
// - Risk/reward calculations (floor line risk, blocking risk, timing risk, scoring risk)

window.strategicPatternTestPositions = (() => {
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
            fen_string: positionData.fen_string || "state_test_strategic_position"
        };
    };

    // ===== FACTORY CONTROL TEST POSITIONS =====

    const factoryDominationOpportunity = {
        name: "Factory Domination Opportunity",
        description: "Multiple blue tiles in factory 0, opponent needs blue tiles. High strategic value for factory control.",
        difficulty: "intermediate",
        tags: ["factory-control", "domination", "blue", "strategic", "testing"],
        generate: () => createGameState({
            fen_string: "state_factory_domination_blue",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 15,
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
                        score: 12,
                        patternLines: [2, 0, 0, 0, 0], // 2 blue tiles in line 0
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
                        tiles: { 0: 4, 1: 1 } // 4 blue tiles - domination opportunity!
                    },
                    {
                        tiles: { 1: 2, 2: 1, 3: 1 }
                    },
                    {
                        tiles: { 2: 2, 3: 1, 4: 1 }
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

    const factoryDisruptionOpportunity = {
        name: "Factory Disruption Opportunity",
        description: "Opponent has yellow tiles in pattern line, yellow tiles available in factory. Disruption control opportunity.",
        difficulty: "intermediate",
        tags: ["factory-control", "disruption", "yellow", "strategic", "testing"],
        generate: () => createGameState({
            fen_string: "state_factory_disruption_yellow",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 18,
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
                        score: 14,
                        patternLines: [0, 3, 0, 0, 0], // 3 yellow tiles in line 1
                        patternLineColors: [-1, 1, -1, -1, -1], // Yellow (1) in line 1
                        wall: [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0], // Yellow not on wall yet
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
                        tiles: { 0: 1, 1: 3, 2: 1 } // 3 yellow tiles available
                    },
                    {
                        tiles: { 1: 2, 2: 1, 3: 1 }
                    },
                    {
                        tiles: { 2: 2, 3: 1, 4: 1 }
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

    // ===== ENDGAME COUNTING TEST POSITIONS =====

    const endgameTileConservation = {
        name: "Endgame Tile Conservation",
        description: "Late game position with few tiles remaining. Critical for tile conservation and endgame optimization.",
        difficulty: "advanced",
        tags: ["endgame", "tile-conservation", "counting", "strategic", "testing"],
        generate: () => createGameState({
            fen_string: "state_endgame_tile_conservation",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 45,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 1], // Almost complete wall
                            [1, 1, 1, 1, 0],
                            [1, 1, 1, 0, 1],
                            [1, 1, 0, 1, 1],
                            [1, 0, 1, 1, 1]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 42,
                        patternLines: [0, 0, 0, 0, 0],
                        patternLineColors: [-1, -1, -1, -1, -1],
                        wall: [
                            [1, 1, 1, 1, 0],
                            [1, 1, 1, 0, 1],
                            [1, 1, 0, 1, 1],
                            [1, 0, 1, 1, 1],
                            [0, 1, 1, 1, 1]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    }
                ],
                factories: [
                    {
                        tiles: { 0: 1, 1: 1 } // Very few tiles remaining
                    },
                    {
                        tiles: { 2: 1, 3: 1 }
                    },
                    {
                        tiles: { 4: 1, 0: 1 }
                    },
                    {
                        tiles: { 1: 1, 2: 1 }
                    },
                    {
                        tiles: { 3: 1, 4: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 }
                },
                currentPlayer: 0
            }
        })
    };

    const endgameScoringPotential = {
        name: "Endgame Scoring Potential",
        description: "Position with high scoring potential through wall completion and pattern line optimization.",
        difficulty: "advanced",
        tags: ["endgame", "scoring-potential", "wall-completion", "strategic", "testing"],
        generate: () => createGameState({
            fen_string: "state_endgame_scoring_potential",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 38,
                        patternLines: [4, 0, 0, 0, 0], // 4 blue tiles in line 0
                        patternLineColors: [0, -1, -1, -1, -1], // Blue (0) in line 0
                        wall: [
                            [0, 1, 1, 1, 1], // Blue missing from wall
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 35,
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

    // ===== RISK/REWARD TEST POSITIONS =====

    const highRiskFloorLine = {
        name: "High Risk Floor Line",
        description: "Position with high floor line risk due to pattern line overflow potential.",
        difficulty: "intermediate",
        tags: ["risk-reward", "floor-line-risk", "overflow", "strategic", "testing"],
        generate: () => createGameState({
            fen_string: "state_high_risk_floor_line",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 22,
                        patternLines: [4, 3, 2, 1, 0], // Almost full pattern lines
                        patternLineColors: [0, 1, 2, 3, -1], // Multiple colors
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
                        score: 20,
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
                        tiles: { 0: 3, 1: 2, 2: 1 } // Many tiles available
                    },
                    {
                        tiles: { 1: 3, 2: 2, 3: 1 }
                    },
                    {
                        tiles: { 2: 3, 3: 2, 4: 1 }
                    },
                    {
                        tiles: { 3: 3, 4: 2, 0: 1 }
                    },
                    {
                        tiles: { 4: 3, 0: 2, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 2, 1: 2, 2: 2, 3: 2, 4: 2 }
                },
                currentPlayer: 0
            }
        })
    };

    const timingRiskScenario = {
        name: "Timing Risk Scenario",
        description: "Position requiring careful timing decisions to avoid blocking and optimize scoring.",
        difficulty: "advanced",
        tags: ["risk-reward", "timing-risk", "blocking", "strategic", "testing"],
        generate: () => createGameState({
            fen_string: "state_timing_risk_scenario",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 28,
                        patternLines: [2, 1, 0, 0, 0], // Some tiles in pattern lines
                        patternLineColors: [0, 1, -1, -1, -1], // Blue and yellow
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
                        score: 25,
                        patternLines: [1, 2, 0, 0, 0], // Opponent also has tiles
                        patternLineColors: [0, 1, -1, -1, -1], // Blue and yellow
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
                        tiles: { 0: 2, 1: 2, 2: 1 } // Limited tiles
                    },
                    {
                        tiles: { 1: 2, 2: 2, 3: 1 }
                    },
                    {
                        tiles: { 2: 2, 3: 2, 4: 1 }
                    },
                    {
                        tiles: { 3: 2, 4: 2, 0: 1 }
                    },
                    {
                        tiles: { 4: 2, 0: 2, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 }
                },
                currentPlayer: 0
            }
        })
    };

    // ===== COMPREHENSIVE STRATEGIC TEST POSITIONS =====

    const comprehensiveStrategicTest = {
        name: "Comprehensive Strategic Test",
        description: "Complex position combining factory control, endgame counting, and risk/reward scenarios.",
        difficulty: "expert",
        tags: ["comprehensive", "factory-control", "endgame", "risk-reward", "strategic", "testing"],
        generate: () => createGameState({
            fen_string: "state_comprehensive_strategic_test",
            gameState: {
                players: [
                    {
                        id: 0,
                        score: 35,
                        patternLines: [3, 2, 1, 0, 0], // Multiple pattern lines
                        patternLineColors: [0, 1, 2, -1, -1], // Blue, yellow, red
                        wall: [
                            [0, 1, 1, 1, 1], // Almost complete first row
                            [1, 0, 1, 1, 1],
                            [1, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    },
                    {
                        id: 1,
                        score: 32,
                        patternLines: [2, 3, 0, 0, 0], // Opponent has tiles
                        patternLineColors: [0, 1, -1, -1, -1], // Blue and yellow
                        wall: [
                            [0, 0, 1, 1, 1],
                            [0, 0, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1]
                        ],
                        floor: [0, 0, 0, 0, 0, 0, 0],
                        floorTiles: []
                    }
                ],
                factories: [
                    {
                        tiles: { 0: 3, 1: 2, 2: 1 } // Blue domination opportunity
                    },
                    {
                        tiles: { 1: 3, 2: 2, 3: 1 } // Yellow disruption opportunity
                    },
                    {
                        tiles: { 2: 2, 3: 2, 4: 1 } // Limited tiles
                    },
                    {
                        tiles: { 3: 2, 4: 2, 0: 1 }
                    },
                    {
                        tiles: { 4: 2, 0: 2, 1: 1 }
                    }
                ],
                centerPool: {
                    tiles: { 0: 2, 1: 2, 2: 1, 3: 1, 4: 1 }
                },
                currentPlayer: 0
            }
        })
    };

    // Return the organized structure
    return {
        "factory-control": {
            name: "Factory Control Tests",
            description: "Positions designed to test factory control opportunities (domination, disruption, timing, color control)",
            icon: "🏭",
            positions: [factoryDominationOpportunity, factoryDisruptionOpportunity]
        },
        "endgame-counting": {
            name: "Endgame Counting Tests",
            description: "Positions designed to test endgame counting scenarios (tile conservation, scoring potential, risk assessment)",
            icon: "🔢",
            positions: [endgameTileConservation, endgameScoringPotential]
        },
        "risk-reward": {
            name: "Risk/Reward Tests",
            description: "Positions designed to test risk/reward calculations (floor line risk, blocking risk, timing risk, scoring risk)",
            icon: "⚖️",
            positions: [highRiskFloorLine, timingRiskScenario]
        },
        "comprehensive": {
            name: "Comprehensive Strategic Tests",
            description: "Complex positions combining multiple strategic analysis types",
            icon: "🎯",
            positions: [comprehensiveStrategicTest]
        }
    };
})(); 