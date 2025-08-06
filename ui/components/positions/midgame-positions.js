// Mid-Game Positions Module
// Contains tactical scenarios and scoring opportunities for 2-player Azul games

window.midgamePositions = (() => {
    // Helper function to create player with pattern lines
    const createPlayer = (patternLines, wallState, floorLine, score) => ({
        pattern_lines: patternLines,
        wall: wallState,
        floor: floorLine,
        score: score
    });

    // Helper function to create wall with specific tiles
    const createWallWithTiles = (tilePositions) => {
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
        
        // 5. Round (default to 3 for midgame positions)
        const round = '3';
        
        // 6. Current player (default to 0)
        const currentPlayer = '0';
        
        return `${factories}/${center}/${players[0]}/${players[1]}/${scores}/${round}/${currentPlayer}`;
    };

    // Scoring Opportunities Subcategory

    const multiplierSetup = {
        name: "Multiplier Setup",
        description: "Positioning for row/column bonuses - focus on completing rows and columns for scoring multipliers",
        difficulty: "intermediate",
        tags: ["midgame", "scoring", "multiplier", "row-completion", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'Y', 'Y'],
                    ['Y', 'Y', 'R', 'R'],
                    ['R', 'R', 'K', 'K'],
                    ['K', 'K', 'W', 'W'],
                    ['W', 'W', 'B', 'B']
                ],
                center: ['B', 'Y'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [['B', 'B'], ['Y', 'Y', 'Y'], [], [], []],
                        createWallWithTiles([[0, 0, 'B'], [1, 1, 'B']]),
                        [],
                        12 + playerIdx * 3
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const colorCompletionRace = {
        name: "Color Completion Race",
        description: "Competing for color completion bonuses - both players close to completing colors",
        difficulty: "advanced",
        tags: ["midgame", "scoring", "color-race", "competitive", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'R', 'W'],
                    ['Y', 'Y', 'K', 'B'],
                    ['R', 'R', 'W', 'Y'],
                    ['K', 'K', 'B', 'R'],
                    ['W', 'W', 'Y', 'K']
                ],
                center: ['B', 'B', 'R', 'W'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [['B', 'B', 'B'], [], ['R', 'R'], [], ['W']],
                        createWallWithTiles(
                            playerIdx === 0 
                                ? [[0, 0, 'B'], [0, 1, 'B'], [0, 2, 'B'], [0, 3, 'B'], [0, 4, 'B']]
                                : [[0, 0, 'B'], [1, 0, 'B'], [2, 0, 'B'], [3, 0, 'B'], [4, 0, 'B']]
                        ),
                        [],
                        18 + playerIdx * 6
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const rowColumnBonus = {
        name: "Row/Column Bonus Setup",
        description: "Strategic positioning for row and column completion bonuses",
        difficulty: "advanced",
        tags: ["midgame", "scoring", "row-bonus", "column-bonus", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'Y', 'Y'],
                    ['R', 'R', 'K', 'K'],
                    ['W', 'W', 'B', 'B'],
                    ['Y', 'Y', 'R', 'R'],
                    ['K', 'K', 'W', 'W']
                ],
                center: ['B', 'Y', 'R'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [['B', 'B'], ['Y', 'Y'], ['R', 'R'], ['K', 'K'], ['W']],
                        createWallWithTiles([
                            [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                            [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B'],
                            [2, 0, 'R'], [2, 1, 'K'], [2, 2, 'W'], [2, 3, 'B'], [2, 4, 'Y'],
                            [3, 0, 'K'], [3, 1, 'W'], [3, 2, 'B'], [3, 3, 'Y'], [3, 4, 'R']
                        ]),
                        [],
                        25 + playerIdx * 8
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    // Blocking Tactics Subcategory

    const floorLineCrisis = {
        name: "Floor Line Crisis",
        description: "Managing floor line penalties while pursuing scoring opportunities",
        difficulty: "intermediate",
        tags: ["midgame", "blocking", "floor-line", "penalty", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'Y', 'Y'],
                    ['R', 'R', 'K', 'K'],
                    ['W', 'W', 'B', 'B'],
                    ['Y', 'Y', 'R', 'R'],
                    ['K', 'K', 'W', 'W']
                ],
                center: ['B', 'Y', 'R', 'K'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [['B'], ['Y'], ['R'], ['K'], ['W']],
                        createWallWithTiles([[0, 0, 'B'], [1, 1, 'Y']]),
                        ['B', 'Y', 'R'],
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

    const patternLineBlocking = {
        name: "Pattern Line Blocking",
        description: "Strategic blocking using pattern lines to deny opponent opportunities",
        difficulty: "advanced",
        tags: ["midgame", "blocking", "pattern-line", "strategic", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'Y', 'Y'],
                    ['R', 'R', 'K', 'K'],
                    ['W', 'W', 'B', 'B'],
                    ['Y', 'Y', 'R', 'R'],
                    ['K', 'K', 'W', 'W']
                ],
                center: ['B', 'Y'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [['B', 'B', 'B', 'B'], ['Y', 'Y', 'Y'], ['R', 'R'], ['K'], []],
                        createWallWithTiles([[0, 0, 'B'], [0, 1, 'B'], [0, 2, 'B'], [0, 3, 'B']]),
                        [],
                        20 + playerIdx * 7
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const wallBlocking = {
        name: "Wall Blocking",
        description: "Using wall placement to block opponent's scoring opportunities",
        difficulty: "advanced",
        tags: ["midgame", "blocking", "wall", "defensive", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'Y', 'Y'],
                    ['R', 'R', 'K', 'K'],
                    ['W', 'W', 'B', 'B'],
                    ['Y', 'Y', 'R', 'R'],
                    ['K', 'K', 'W', 'W']
                ],
                center: ['B', 'Y', 'R'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [['B'], ['Y'], ['R'], ['K'], ['W']],
                        createWallWithTiles([
                            [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                            [1, 0, 'W'], [1, 1, 'B'], [1, 2, 'Y'], [1, 3, 'R'], [1, 4, 'K'],
                            [2, 0, 'K'], [2, 1, 'W'], [2, 2, 'B'], [2, 3, 'Y'], [2, 4, 'R']
                        ]),
                        [],
                        30 + playerIdx * 10
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    // Efficiency Scenarios Subcategory

    const tileEfficiencyPuzzle = {
        name: "Tile Efficiency Puzzle",
        description: "Maximizing tile usage efficiency - getting the most value from each tile",
        difficulty: "intermediate",
        tags: ["midgame", "efficiency", "tile-usage", "optimization", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'Y', 'Y'],
                    ['R', 'R', 'K', 'K'],
                    ['W', 'W', 'B', 'B'],
                    ['Y', 'Y', 'R', 'R'],
                    ['K', 'K', 'W', 'W']
                ],
                center: ['B', 'Y', 'R', 'K', 'W'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [['B'], ['Y'], ['R'], ['K'], ['W']],
                        createWallWithTiles([[0, 0, 'B'], [1, 1, 'Y'], [2, 2, 'R']]),
                        [],
                        18 + playerIdx * 4
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const timingCriticalDecision = {
        name: "Timing Critical Decision",
        description: "Critical timing decisions - when to take tiles vs when to wait",
        difficulty: "advanced",
        tags: ["midgame", "timing", "decision", "critical", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'Y', 'Y'],
                    ['R', 'R', 'K', 'K'],
                    ['W', 'W', 'B', 'B'],
                    ['Y', 'Y', 'R', 'R'],
                    ['K', 'K', 'W', 'W']
                ],
                center: ['B', 'Y', 'R', 'K', 'W', 'B', 'Y'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [['B', 'B'], ['Y', 'Y'], ['R'], ['K'], ['W']],
                        createWallWithTiles([[0, 0, 'B'], [0, 1, 'B'], [1, 1, 'Y'], [1, 2, 'Y']]),
                        ['B', 'Y'],
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

    // Return the module
    return {
        "scoring": {
            name: "Scoring Opportunities",
            description: "Positions focused on maximizing scoring potential",
            positions: [multiplierSetup, colorCompletionRace, rowColumnBonus]
        },
        "blocking": {
            name: "Blocking Tactics",
            description: "Strategic blocking and defensive play scenarios",
            positions: [floorLineCrisis, patternLineBlocking, wallBlocking]
        },
        "efficiency": {
            name: "Efficiency Scenarios",
            description: "Optimization and timing-based challenges",
            positions: [tileEfficiencyPuzzle, timingCriticalDecision]
        }
    };
})(); 