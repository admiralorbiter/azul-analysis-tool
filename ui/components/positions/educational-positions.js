// Educational Positions Module
// Contains learning scenarios and teaching positions for 2-player Azul games

window.educationalPositions = (() => {
    // Helper function to create simple player
    const createSimplePlayer = (patternLines, wallState, floorLine, score) => ({
        pattern_lines: patternLines,
        wall: wallState,
        floor: floorLine,
        score: score
    });

    // Helper function to create basic wall
    const createBasicWall = (tilePositions) => {
        const wall = Array(5).fill().map(() => Array(5).fill(null));
        tilePositions.forEach(([row, col, color]) => {
            wall[row][col] = color;
        });
        return wall;
    };

    // Helper function to generate standard FEN format
    const generateStandardFEN = (gameState) => {
        // Convert game state to standard FEN format
        // Format: factories/center/player1_wall/player1_pattern/player1_floor/player2_wall/player2_pattern/player2_floor/scores/round/current_player
        
        // 1. Factories (5 factories, 4 tiles each)
        const factories = gameState.factories.map(factory => {
            // Ensure exactly 4 tiles per factory
            const tiles = factory.slice(0, 4);
            while (tiles.length < 4) {
                tiles.push('-');
            }
            return tiles.join('');
        }).join('|');
        
        // 2. Center pool
        const center = gameState.center.length > 0 ? gameState.center.join('') : '-';
        
        // 3. Player data (wall/pattern/floor for each player)
        const players = gameState.players.map(player => {
            // Wall (5x5 grid)
            const wall = player.wall.map(row => 
                row.map(tile => tile || '-').join('')
            ).join('|');
            
            // Pattern lines (5 lines)
            const pattern = player.pattern_lines.map(line => 
                line.join('')
            ).join('|');
            
            // Floor line
            const floor = player.floor.length > 0 ? player.floor.join('') : '-';
            
            return `${wall}/${pattern}/${floor}`;
        });
        
        // 4. Scores
        const scores = gameState.players.map(p => p.score || 0).join(',');
        
        // 5. Round (default to 2 for educational positions)
        const round = '2';
        
        // 6. Current player (default to 0)
        const currentPlayer = '0';
        
        return `${factories}/${center}/${players[0]}/${players[1]}/${scores}/${round}/${currentPlayer}`;
    };

    // Beginner Lessons Subcategory

    const patternLineBasics = {
        name: "Pattern Line Basics",
        description: "Learn how pattern lines work - simple setup for beginners",
        difficulty: "beginner",
        tags: ["educational", "beginner", "pattern-lines", "learning", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'Y'],
                    ['R', 'K'],
                    ['W', 'B'],
                    ['Y', 'R'],
                    ['K', 'W']
                ],
                center: ['B', 'Y'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createSimplePlayer(
                        [['B'], ['Y'], [], [], []],
                        createBasicWall([[0, 0, 'B'], [1, 1, 'Y']]),
                        [],
                        5 + playerIdx * 2
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const wallPlacementBasics = {
        name: "Wall Placement Basics",
        description: "Understanding wall placement rules and scoring",
        difficulty: "beginner",
        tags: ["educational", "beginner", "wall-placement", "scoring", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'Y', 'R'],
                    ['K', 'W', 'B'],
                    ['Y', 'R', 'K'],
                    ['W', 'B', 'Y'],
                    ['R', 'K', 'W']
                ],
                center: ['B', 'Y', 'R'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createSimplePlayer(
                        [['B'], ['Y'], ['R'], [], []],
                        createBasicWall([
                            [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                            [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B']
                        ]),
                        [],
                        8 + playerIdx * 3
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const floorLinePenalty = {
        name: "Floor Line Penalty",
        description: "Learn about floor line penalties and how to avoid them",
        difficulty: "beginner",
        tags: ["educational", "beginner", "floor-line", "penalty", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'Y'],
                    ['R', 'K'],
                    ['W', 'B'],
                    ['Y', 'R'],
                    ['K', 'W']
                ],
                center: ['B', 'Y', 'R'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createSimplePlayer(
                        [['B', 'B', 'B'], ['Y', 'Y'], ['R'], [], []],
                        createBasicWall([[0, 0, 'B'], [1, 1, 'Y']]),
                        ['B', 'Y'],
                        3 + playerIdx * 2
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    // Intermediate Challenges Subcategory

    const wallCompletionStrategy = {
        name: "Wall Completion Strategy",
        description: "Learn strategic wall completion for maximum bonuses",
        difficulty: "intermediate",
        tags: ["educational", "intermediate", "wall-completion", "strategy", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'Y', 'R'],
                    ['K', 'W', 'B'],
                    ['Y', 'R', 'K'],
                    ['W', 'B', 'Y'],
                    ['R', 'K', 'W']
                ],
                center: ['B', 'Y', 'R'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createSimplePlayer(
                        [['B', 'B'], ['Y', 'Y'], ['R'], ['K'], ['W']],
                        createBasicWall([
                            [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                            [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B'],
                            [2, 0, 'R'], [2, 1, 'K'], [2, 2, 'W'], [2, 3, 'B'], [2, 4, 'Y']
                        ]),
                        [],
                        15 + playerIdx * 5
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const floorLineManagement = {
        name: "Floor Line Management",
        description: "Advanced floor line management and penalty avoidance",
        difficulty: "intermediate",
        tags: ["educational", "intermediate", "floor-line", "management", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'Y', 'R'],
                    ['K', 'W', 'B'],
                    ['Y', 'R', 'K'],
                    ['W', 'B', 'Y'],
                    ['R', 'K', 'W']
                ],
                center: ['B', 'Y', 'R', 'K', 'W'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createSimplePlayer(
                        [['B', 'B', 'B'], ['Y', 'Y'], ['R'], ['K'], ['W']],
                        createBasicWall([[0, 0, 'B'], [1, 1, 'Y'], [2, 2, 'R']]),
                        ['B', 'Y', 'R'],
                        12 + playerIdx * 4
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const colorCompletion = {
        name: "Color Completion",
        description: "Learn about color completion bonuses and strategies",
        difficulty: "intermediate",
        tags: ["educational", "intermediate", "color-completion", "bonus", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B'],
                    ['Y', 'Y'],
                    ['R', 'R'],
                    ['K', 'K'],
                    ['W', 'W']
                ],
                center: ['B', 'Y', 'R'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createSimplePlayer(
                        [['B', 'B'], ['Y', 'Y'], ['R', 'R'], ['K', 'K'], ['W', 'W']],
                        createBasicWall([
                            [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                            [1, 0, 'W'], [1, 1, 'B'], [1, 2, 'Y'], [1, 3, 'R'], [1, 4, 'K'],
                            [2, 0, 'K'], [2, 1, 'W'], [2, 2, 'B'], [2, 3, 'Y'], [2, 4, 'R']
                        ]),
                        [],
                        20 + playerIdx * 6
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    // Advanced Concepts Subcategory

    const timingAndEfficiency = {
        name: "Timing and Efficiency",
        description: "Learn about timing and tile efficiency optimization",
        difficulty: "advanced",
        tags: ["educational", "advanced", "timing", "efficiency", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'Y', 'R'],
                    ['K', 'W', 'B'],
                    ['Y', 'R', 'K'],
                    ['W', 'B', 'Y'],
                    ['R', 'K', 'W']
                ],
                center: ['B', 'Y', 'R', 'K', 'W'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createSimplePlayer(
                        [['B', 'B'], ['Y'], ['R'], ['K'], ['W']],
                        createBasicWall([
                            [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                            [1, 0, 'W'], [1, 1, 'B'], [1, 2, 'Y'], [1, 3, 'R'], [1, 4, 'K']
                        ]),
                        ['B', 'Y'],
                        18 + playerIdx * 5
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const defensivePlayConcepts = {
        name: "Defensive Play Concepts",
        description: "Learn defensive strategies and opponent blocking",
        difficulty: "advanced",
        tags: ["educational", "advanced", "defensive", "blocking", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'Y'],
                    ['R', 'R', 'K'],
                    ['W', 'W', 'B'],
                    ['Y', 'Y', 'R'],
                    ['K', 'K', 'W']
                ],
                center: ['B', 'Y', 'R'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createSimplePlayer(
                        [['B', 'B', 'B'], ['Y', 'Y'], ['R'], ['K'], ['W']],
                        createBasicWall([
                            [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                            [1, 0, 'W'], [1, 1, 'B'], [1, 2, 'Y'], [1, 3, 'R'], [1, 4, 'K']
                        ]),
                        [],
                        25 + playerIdx * 7
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const riskAssessment = {
        name: "Risk Assessment",
        description: "Learn to assess risks and make calculated decisions",
        difficulty: "advanced",
        tags: ["educational", "advanced", "risk-assessment", "decision-making", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'Y', 'R'],
                    ['K', 'W', 'B'],
                    ['Y', 'R', 'K'],
                    ['W', 'B', 'Y'],
                    ['R', 'K', 'W']
                ],
                center: ['B', 'Y', 'R', 'K', 'W', 'B', 'Y'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createSimplePlayer(
                        [['B', 'B'], ['Y', 'Y'], ['R'], ['K'], ['W']],
                        createBasicWall([
                            [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                            [1, 0, 'W'], [1, 1, 'B'], [1, 2, 'Y'], [1, 3, 'R'], [1, 4, 'K'],
                            [2, 0, 'K'], [2, 1, 'W'], [2, 2, 'B'], [2, 3, 'Y'], [2, 4, 'R']
                        ]),
                        ['B', 'Y', 'R'],
                        22 + playerIdx * 6
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    // Expert Concepts Subcategory

    const endgamePlanning = {
        name: "Endgame Planning",
        description: "Learn to plan for endgame scenarios and final scoring",
        difficulty: "expert",
        tags: ["educational", "expert", "endgame-planning", "final-scoring", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'Y'],
                    ['R', 'K'],
                    ['W', 'B'],
                    ['Y', 'R'],
                    ['K', 'W']
                ],
                center: ['B', 'Y', 'R'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createSimplePlayer(
                        [['B'], ['Y'], ['R'], ['K'], ['W']],
                        createBasicWall([
                            [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                            [1, 0, 'W'], [1, 1, 'B'], [1, 2, 'Y'], [1, 3, 'R'], [1, 4, 'K'],
                            [2, 0, 'K'], [2, 1, 'W'], [2, 2, 'B'], [2, 3, 'Y'], [2, 4, 'R'],
                            [3, 0, 'R'], [3, 1, 'K'], [3, 2, 'W'], [3, 3, 'B'], [3, 4, 'Y']
                        ]),
                        [],
                        35 + playerIdx * 8
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const competitiveAnalysis = {
        name: "Competitive Analysis",
        description: "Learn to analyze competitive scenarios and opponent strategies",
        difficulty: "expert",
        tags: ["educational", "expert", "competitive-analysis", "opponent-analysis", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'Y', 'R'],
                    ['K', 'W', 'B'],
                    ['Y', 'R', 'K'],
                    ['W', 'B', 'Y'],
                    ['R', 'K', 'W']
                ],
                center: ['B', 'Y', 'R', 'K', 'W'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createSimplePlayer(
                        [['B', 'B'], ['Y', 'Y'], ['R'], ['K'], ['W']],
                        createBasicWall([
                            [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                            [1, 0, 'W'], [1, 1, 'B'], [1, 2, 'Y'], [1, 3, 'R'], [1, 4, 'K'],
                            [2, 0, 'K'], [2, 1, 'W'], [2, 2, 'B'], [2, 3, 'Y'], [2, 4, 'R'],
                            [3, 0, 'R'], [3, 1, 'K'], [3, 2, 'W'], [3, 3, 'B'], [3, 4, 'Y'],
                            [4, 0, 'Y'], [4, 1, 'R'], [4, 2, 'K'], [4, 3, 'W'], [4, 4, 'B']
                        ]),
                        ['B', 'Y'],
                        40 + playerIdx * 10
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    // Return the module
    return {
        "beginner": {
            name: "Beginner Lessons",
            description: "Basic concepts and fundamental learning scenarios",
            positions: [patternLineBasics, wallPlacementBasics, floorLinePenalty]
        },
        "intermediate": {
            name: "Intermediate Challenges",
            description: "Advanced concepts and strategic learning scenarios",
            positions: [wallCompletionStrategy, floorLineManagement, colorCompletion]
        },
        "advanced": {
            name: "Advanced Concepts",
            description: "Complex strategies and advanced learning scenarios",
            positions: [timingAndEfficiency, defensivePlayConcepts, riskAssessment]
        },
        "expert": {
            name: "Expert Concepts",
            description: "Expert-level analysis and competitive scenarios",
            positions: [endgamePlanning, competitiveAnalysis]
        }
    };
})(); 