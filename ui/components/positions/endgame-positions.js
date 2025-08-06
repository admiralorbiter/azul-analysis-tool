// End-Game Positions Module
// Contains final optimization and precise counting scenarios for 2-player Azul games

window.endgamePositions = (() => {
    // Helper function to create player with advanced wall state
    const createPlayer = (patternLines, wallState, floorLine, score) => ({
        pattern_lines: patternLines,
        wall: wallState,
        floor: floorLine,
        score: score
    });

    // Helper function to create nearly complete wall
    const createNearCompleteWall = (completionLevel) => {
        const wall = Array(5).fill().map(() => Array(5).fill(null));
        
        // Fill based on completion level (0-1, where 1 is fully complete)
        const tilesToPlace = Math.floor(completionLevel * 25);
        
        for (let i = 0; i < tilesToPlace; i++) {
            const row = Math.floor(i / 5);
            const col = i % 5;
            const colors = ['B', 'Y', 'R', 'K', 'W'];
            wall[row][col] = colors[(row + col) % 5];
        }
        
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
        
        // 5. Round (default to 8 for endgame positions)
        const round = '8';
        
        // 6. Current player (default to 0)
        const currentPlayer = '0';
        
        return `${factories}/${center}/${players[0]}/${players[1]}/${scores}/${round}/${currentPlayer}`;
    };

    // Final Optimization Subcategory

    const lastRoundEfficiency = {
        name: "Last Round Efficiency",
        description: "Final moves for maximum points - optimize every tile placement",
        difficulty: "expert",
        tags: ["endgame", "optimization", "final-round", "maximum-points", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['R'],
                    ['R'],
                    ['R'],
                    ['R'],
                    ['R']
                ],
                center: ['R', 'R', 'R', 'W'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [[], [], ['R', 'R', 'R'], [], ['W']],
                        createNearCompleteWall(0.6),
                        ['R', 'W'],
                        45 + playerIdx * 8
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const tieBreakerScenario = {
        name: "Tie-Breaker Scenario",
        description: "Close game with precise counting needed - every point matters",
        difficulty: "expert",
        tags: ["endgame", "optimization", "tie-breaker", "precise-counting", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['K'],
                    ['K'],
                    ['K'],
                    ['K'],
                    ['K']
                ],
                center: ['K', 'K'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [[], [], [], ['K', 'K'], []],
                        createNearCompleteWall(0.8),
                        [],
                        52 + playerIdx * 2
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const bonusScoring = {
        name: "Bonus Scoring Maximization",
        description: "Focus on completing rows, columns, and colors for maximum bonuses",
        difficulty: "expert",
        tags: ["endgame", "optimization", "bonus-scoring", "row-completion", "2-player"],
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
                    createPlayer(
                        [['B'], ['Y'], ['R'], ['K'], ['W']],
                        createNearCompleteWall(0.7),
                        [],
                        48 + playerIdx * 5
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    // Precise Counting Subcategory

    const tileConservationPuzzle = {
        name: "Tile Conservation Puzzle",
        description: "Managing limited tiles for optimal endgame scoring",
        difficulty: "expert",
        tags: ["endgame", "counting", "tile-conservation", "limited-resources", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B'],
                    ['Y'],
                    ['R'],
                    ['K'],
                    ['W']
                ],
                center: ['B', 'Y'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [['B'], ['Y'], ['R'], ['K'], ['W']],
                        createNearCompleteWall(0.9),
                        [],
                        55 + playerIdx * 3
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const negativePointsManagement = {
        name: "Negative Points Management",
        description: "Minimizing floor line penalties in final scoring",
        difficulty: "advanced",
        tags: ["endgame", "counting", "penalty-minimization", "floor-line", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'Y'],
                    ['R', 'K'],
                    ['W', 'B'],
                    ['Y', 'R'],
                    ['K', 'W']
                ],
                center: ['B', 'Y', 'R', 'K', 'W'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [['B'], ['Y'], ['R'], ['K'], ['W']],
                        createNearCompleteWall(0.5),
                        ['B', 'Y', 'R', 'K', 'W'],
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

    const colorCompletionRace = {
        name: "Color Completion Race",
        description: "Final race to complete color sets for bonus points",
        difficulty: "expert",
        tags: ["endgame", "counting", "color-completion", "race", "2-player"],
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
                    createPlayer(
                        [['B', 'B'], ['Y', 'Y'], ['R', 'R'], ['K', 'K'], ['W', 'W']],
                        createNearCompleteWall(0.6),
                        [],
                        42 + playerIdx * 6
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    // Wall Completion Subcategory

    const rowCompletionChallenge = {
        name: "Row Completion Challenge",
        description: "Strategic completion of rows for maximum row bonuses",
        difficulty: "advanced",
        tags: ["endgame", "wall-completion", "row-bonus", "strategic", "2-player"],
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
                    createPlayer(
                        [['B'], ['Y'], ['R'], ['K'], ['W']],
                        createNearCompleteWall(0.8),
                        [],
                        50 + playerIdx * 4
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const columnCompletionChallenge = {
        name: "Column Completion Challenge",
        description: "Strategic completion of columns for maximum column bonuses",
        difficulty: "advanced",
        tags: ["endgame", "wall-completion", "column-bonus", "strategic", "2-player"],
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
                    createPlayer(
                        [['B'], ['Y'], ['R'], ['K'], ['W']],
                        createNearCompleteWall(0.7),
                        [],
                        47 + playerIdx * 5
                    )
                )
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const fullWallCompletion = {
        name: "Full Wall Completion",
        description: "Ultimate challenge - completing entire wall for maximum bonuses",
        difficulty: "expert",
        tags: ["endgame", "wall-completion", "full-wall", "ultimate-challenge", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B'],
                    ['Y'],
                    ['R'],
                    ['K'],
                    ['W']
                ],
                center: ['B', 'Y', 'R', 'K', 'W'],
                players: Array(2).fill().map((_, playerIdx) => 
                    createPlayer(
                        [['B'], ['Y'], ['R'], ['K'], ['W']],
                        createNearCompleteWall(0.95),
                        [],
                        60 + playerIdx * 10
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
        "optimization": {
            name: "Final Optimization",
            description: "Endgame scenarios focused on maximizing final scoring",
            positions: [lastRoundEfficiency, tieBreakerScenario, bonusScoring]
        },
        "counting": {
            name: "Precise Counting",
            description: "Scenarios requiring exact calculation and resource management",
            positions: [tileConservationPuzzle, negativePointsManagement, colorCompletionRace]
        },
        "completion": {
            name: "Wall Completion",
            description: "Strategic wall completion challenges for maximum bonuses",
            positions: [rowCompletionChallenge, columnCompletionChallenge, fullWallCompletion]
        }
    };
})(); 