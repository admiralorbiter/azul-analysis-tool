// Opening Positions Module
// Contains initial game setups and opening strategies for 2-player Azul games

window.openingPositions = (() => {
    // Helper function to create empty player
    const createEmptyPlayer = () => ({
        pattern_lines: [[], [], [], [], []],
        wall: Array(5).fill().map(() => Array(5).fill(null)),
        floor: [],
        score: 0
    });

    // Helper function to create balanced factories
    const createBalancedFactories = () => [
        ['B', 'Y', 'R', 'K', 'W'],
        ['Y', 'R', 'K', 'W', 'B'],
        ['R', 'K', 'W', 'B', 'Y'],
        ['K', 'W', 'B', 'Y', 'R'],
        ['W', 'B', 'Y', 'R', 'K']
    ];

    // Helper function to create color-focused factories
    const createColorFocusedFactories = (primaryColor, secondaryColor) => [
        [primaryColor, primaryColor, secondaryColor, secondaryColor],
        [primaryColor, primaryColor, secondaryColor, secondaryColor],
        [primaryColor, primaryColor, secondaryColor, secondaryColor],
        [primaryColor, primaryColor, secondaryColor, secondaryColor],
        [primaryColor, primaryColor, secondaryColor, secondaryColor]
    ];

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
        
        // 5. Round (default to 1 for opening positions)
        const round = '1';
        
        // 6. Current player (default to 0)
        const currentPlayer = '0';
        
        return `${factories}/${center}/${players[0]}/${players[1]}/${scores}/${round}/${currentPlayer}`;
    };

    // Balanced Opening Subcategory

    const balancedStart = {
        name: "Balanced Start",
        description: "Standard opening with equal distribution of all colors",
        difficulty: "beginner",
        tags: ["opening", "balanced", "standard", "beginner-friendly", "2-player"],
        generate: () => {
            const gameState = {
                factories: createBalancedFactories(),
                center: ['B', 'Y', 'R', 'K', 'W'],
                players: Array(2).fill().map(() => createEmptyPlayer())
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const blueFocusStart = {
        name: "Blue Focus Start",
        description: "Opening with emphasis on blue tiles - good for beginners",
        difficulty: "beginner",
        tags: ["opening", "blue-focus", "beginner-friendly", "color-strategy", "2-player"],
        generate: () => {
            const gameState = {
                factories: createColorFocusedFactories('B', 'Y'),
                center: ['B', 'B', 'Y', 'R'],
                players: Array(2).fill().map(() => createEmptyPlayer())
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const yellowFocusStart = {
        name: "Yellow Focus Start",
        description: "Opening with emphasis on yellow tiles - balanced approach",
        difficulty: "beginner",
        tags: ["opening", "yellow-focus", "beginner-friendly", "color-strategy", "2-player"],
        generate: () => {
            const gameState = {
                factories: createColorFocusedFactories('Y', 'B'),
                center: ['Y', 'Y', 'B', 'R'],
                players: Array(2).fill().map(() => createEmptyPlayer())
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    // Aggressive Opening Subcategory

    const aggressiveStart = {
        name: "Aggressive Start",
        description: "High-risk opening with concentrated colors",
        difficulty: "intermediate",
        tags: ["opening", "aggressive", "high-risk", "concentrated", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'B', 'B'],
                    ['Y', 'Y', 'Y', 'Y'],
                    ['R', 'R', 'R', 'R'],
                    ['K', 'K', 'K', 'K'],
                    ['W', 'W', 'W', 'W']
                ],
                center: ['B', 'Y', 'R'],
                players: Array(2).fill().map(() => createEmptyPlayer())
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const centerHeavyStart = {
        name: "Center Heavy Start",
        description: "Opening with many tiles in center - tactical complexity",
        difficulty: "intermediate",
        tags: ["opening", "center-heavy", "tactical", "complex", "2-player"],
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
                players: Array(2).fill().map(() => createEmptyPlayer())
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const mixedAggressiveStart = {
        name: "Mixed Aggressive Start",
        description: "Aggressive opening with mixed color distribution",
        difficulty: "intermediate",
        tags: ["opening", "aggressive", "mixed", "high-interaction", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'Y', 'R'],
                    ['Y', 'Y', 'R', 'K'],
                    ['R', 'R', 'K', 'W'],
                    ['K', 'K', 'W', 'B'],
                    ['W', 'W', 'B', 'Y']
                ],
                center: ['B', 'Y', 'R', 'K'],
                players: Array(2).fill().map(() => createEmptyPlayer())
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    // Defensive Opening Subcategory

    const defensiveStart = {
        name: "Defensive Start",
        description: "Conservative opening with minimal risk",
        difficulty: "beginner",
        tags: ["opening", "defensive", "conservative", "low-risk", "2-player"],
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
                players: Array(2).fill().map(() => createEmptyPlayer())
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const safeStart = {
        name: "Safe Start",
        description: "Very conservative opening - good for learning",
        difficulty: "beginner",
        tags: ["opening", "safe", "conservative", "learning", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'B', 'B'],
                    ['Y', 'Y', 'Y', 'Y'],
                    ['R', 'R', 'R', 'R'],
                    ['K', 'K', 'K', 'K'],
                    ['W', 'W', 'W', 'W']
                ],
                center: ['B', 'Y'],
                players: Array(2).fill().map(() => createEmptyPlayer())
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    const flexibleStart = {
        name: "Flexible Start",
        description: "Adaptable opening allowing multiple strategies",
        difficulty: "intermediate",
        tags: ["opening", "flexible", "adaptable", "multi-strategy", "2-player"],
        generate: () => {
            const gameState = {
                factories: [
                    ['B', 'B', 'Y', 'R'],
                    ['K', 'W', 'B', 'Y'],
                    ['Y', 'R', 'K', 'W'],
                    ['W', 'B', 'Y', 'R'],
                    ['R', 'K', 'W', 'B']
                ],
                center: ['B', 'Y', 'R', 'K'],
                players: Array(2).fill().map(() => createEmptyPlayer())
            };
            
            return {
                ...gameState,
                fen_string: generateStandardFEN(gameState)
            };
        }
    };

    // Return the module
    return {
        "balanced": {
            name: "Balanced Openings",
            description: "Standard and balanced starting positions",
            positions: [balancedStart, blueFocusStart, yellowFocusStart]
        },
        "aggressive": {
            name: "Aggressive Openings", 
            description: "High-risk, high-reward starting positions",
            positions: [aggressiveStart, centerHeavyStart, mixedAggressiveStart]
        },
        "defensive": {
            name: "Defensive Openings",
            description: "Conservative and safe starting positions", 
            positions: [defensiveStart, safeStart, flexibleStart]
        }
    };
})(); 