// Mid-Game Positions Module
// Contains tactical scenarios and scoring opportunities for 2-player Azul games

window.midgamePositions = (() => {
    // Helper function to create player with pattern lines
    const createPlayerWithPatternLines = (patternLines, wallState, floorLine, score) => ({
        pattern_lines: patternLines,
        wall: wallState,
        floor_line: floorLine,
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

    // Scoring Opportunities Subcategory

    const multiplierSetup = {
        name: "Multiplier Setup",
        description: "Positioning for row/column bonuses - focus on completing rows and columns for scoring multipliers",
        difficulty: "intermediate",
        tags: ["midgame", "scoring", "multiplier", "row-completion", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'Y'],
                ['Y', 'R'],
                ['R', 'K'],
                ['K', 'W'],
                ['W', 'B']
            ],
            center: ['B', 'Y'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayerWithPatternLines(
                    [['B', 'B'], ['Y', 'Y', 'Y'], [], [], []],
                    createWallWithTiles([[0, 0, 'B'], [1, 1, 'B']]),
                    [],
                    12 + playerIdx * 3
                )
            )
        })
    };

    const colorCompletionRace = {
        name: "Color Completion Race",
        description: "Competing for color completion bonuses - both players close to completing colors",
        difficulty: "advanced",
        tags: ["midgame", "scoring", "color-race", "competitive", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'R', 'W'],
                ['Y', 'K', 'B'],
                ['R', 'W', 'Y'],
                ['K', 'B', 'R'],
                ['W', 'Y', 'K']
            ],
            center: ['B', 'B', 'R', 'W'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayerWithPatternLines(
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
        })
    };

    const rowColumnBonus = {
        name: "Row/Column Bonus Setup",
        description: "Strategic positioning for row and column completion bonuses",
        difficulty: "advanced",
        tags: ["midgame", "scoring", "row-bonus", "column-bonus", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'Y'],
                ['R', 'K'],
                ['W', 'B'],
                ['Y', 'R'],
                ['K', 'W']
            ],
            center: ['B', 'Y', 'R'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayerWithPatternLines(
                    [['B', 'B'], ['Y', 'Y'], ['R', 'R'], ['K', 'K'], ['W']],
                    createWallWithTiles([
                        [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                        [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B'],
                        [2, 0, 'R'], [2, 1, 'K'], [2, 2, 'W'], [2, 3, 'B'], [2, 4, 'Y'],
                        [3, 0, 'K'], [3, 1, 'W'], [3, 2, 'B'], [3, 3, 'Y'], [3, 4, 'R']
                    ]),
                    [],
                    25 + playerIdx * 5
                )
            )
        })
    };

    // Blocking Tactics Subcategory

    const defensiveBlocking = {
        name: "Defensive Blocking",
        description: "Preventing opponent from completing patterns - defensive strategy focus",
        difficulty: "intermediate",
        tags: ["midgame", "blocking", "defensive", "prevention", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'Y', 'R'],
                ['K', 'W', 'B'],
                ['Y', 'R', 'K'],
                ['W', 'B', 'Y'],
                ['R', 'K', 'W']
            ],
            center: ['B', 'Y', 'R', 'K'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayerWithPatternLines(
                    [['B'], ['Y'], ['R'], ['K'], ['W']],
                    createWallWithTiles([
                        [0, 0, 'B'], [1, 1, 'Y'], [2, 2, 'R'], [3, 3, 'K'], [4, 4, 'W']
                    ]),
                    [],
                    15 + playerIdx * 4
                )
            )
        })
    };

    const resourceDenial = {
        name: "Resource Denial",
        description: "Denying key tiles to opponent - controlling the supply",
        difficulty: "advanced",
        tags: ["midgame", "blocking", "resource-denial", "control", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'B'],
                ['Y', 'Y'],
                ['R', 'R'],
                ['K', 'K'],
                ['W', 'W']
            ],
            center: ['B', 'Y', 'R'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayerWithPatternLines(
                    [['B', 'B', 'B'], ['Y', 'Y'], ['R'], [], []],
                    createWallWithTiles([
                        [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                        [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B']
                    ]),
                    [],
                    20 + playerIdx * 3
                )
            )
        })
    };

    const patternDisruption = {
        name: "Pattern Disruption",
        description: "Breaking opponent's planned patterns - tactical interference",
        difficulty: "advanced",
        tags: ["midgame", "blocking", "pattern-disruption", "tactical", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'Y', 'R', 'K'],
                ['Y', 'R', 'K', 'W'],
                ['R', 'K', 'W', 'B'],
                ['K', 'W', 'B', 'Y'],
                ['W', 'B', 'Y', 'R']
            ],
            center: ['B', 'Y', 'R', 'K', 'W'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayerWithPatternLines(
                    [['B', 'B'], ['Y'], ['R', 'R'], ['K'], ['W']],
                    createWallWithTiles([
                        [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                        [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B'],
                        [2, 0, 'R'], [2, 1, 'K'], [2, 2, 'W'], [2, 3, 'B'], [2, 4, 'Y']
                    ]),
                    [],
                    22 + playerIdx * 4
                )
            )
        })
    };

    // Efficiency Scenarios Subcategory

    const tileEfficiency = {
        name: "Tile Efficiency",
        description: "Maximizing points per tile - efficiency optimization",
        difficulty: "intermediate",
        tags: ["midgame", "efficiency", "optimization", "points-per-tile", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'Y'],
                ['R', 'K'],
                ['W', 'B'],
                ['Y', 'R'],
                ['K', 'W']
            ],
            center: ['B', 'Y', 'R'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayerWithPatternLines(
                    [['B'], ['Y'], ['R'], ['K'], ['W']],
                    createWallWithTiles([
                        [0, 0, 'B'], [1, 1, 'Y'], [2, 2, 'R'], [3, 3, 'K'], [4, 4, 'W']
                    ]),
                    [],
                    18 + playerIdx * 2
                )
            )
        })
    };

    const floorLineCrisis = {
        name: "Floor Line Crisis",
        description: "Managing floor line penalties while maximizing scoring",
        difficulty: "advanced",
        tags: ["midgame", "efficiency", "floor-line", "penalty-management", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'Y', 'R'],
                ['K', 'W', 'B'],
                ['Y', 'R', 'K'],
                ['W', 'B', 'Y'],
                ['R', 'K', 'W']
            ],
            center: ['B', 'Y', 'R', 'K', 'W'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayerWithPatternLines(
                    [['B', 'B', 'B'], ['Y', 'Y'], ['R'], ['K'], ['W']],
                    createWallWithTiles([
                        [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                        [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B']
                    ]),
                    ['B', 'Y', 'R'],
                    28 + playerIdx * 5
                )
            )
        })
    };

    const patternLineOptimization = {
        name: "Pattern Line Optimization",
        description: "Strategic use of pattern lines for maximum efficiency",
        difficulty: "intermediate",
        tags: ["midgame", "efficiency", "pattern-lines", "optimization", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'Y', 'R', 'K'],
                ['Y', 'R', 'K', 'W'],
                ['R', 'K', 'W', 'B'],
                ['K', 'W', 'B', 'Y'],
                ['W', 'B', 'Y', 'R']
            ],
            center: ['B', 'Y', 'R', 'K'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayerWithPatternLines(
                    [['B', 'B', 'B'], ['Y', 'Y'], ['R'], ['K'], ['W']],
                    createWallWithTiles([
                        [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                        [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B'],
                        [2, 0, 'R'], [2, 1, 'K'], [2, 2, 'W'], [2, 3, 'B'], [2, 4, 'Y']
                    ]),
                    [],
                    24 + playerIdx * 3
                )
            )
        })
    };

    // Return the organized structure
    return {
        "scoring": {
            name: "Scoring Opportunities",
            description: "Positions with clear scoring potential",
            icon: "🎯",
            positions: [multiplierSetup, colorCompletionRace, rowColumnBonus]
        },
        "blocking": {
            name: "Blocking Tactics",
            description: "Defensive and disruptive strategies",
            icon: "🛡️",
            positions: [defensiveBlocking, resourceDenial, patternDisruption]
        },
        "efficiency": {
            name: "Efficiency Scenarios",
            description: "Optimizing resource usage",
            icon: "⚡",
            positions: [tileEfficiency, floorLineCrisis, patternLineOptimization]
        }
    };
})(); 