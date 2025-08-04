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

    // Final Optimization Subcategory

    const lastRoundEfficiency = {
        name: "Last Round Efficiency",
        description: "Final moves for maximum points - optimize every tile placement",
        difficulty: "expert",
        tags: ["endgame", "optimization", "final-round", "maximum-points", "2-player"],
        generate: () => ({
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
        })
    };

    const tieBreakerScenario = {
        name: "Tie-Breaker Scenario",
        description: "Close game with precise counting needed - every point matters",
        difficulty: "expert",
        tags: ["endgame", "optimization", "tie-breaker", "precise-counting", "2-player"],
        generate: () => ({
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
        })
    };

    const bonusScoring = {
        name: "Bonus Scoring Maximization",
        description: "Focus on completing rows, columns, and colors for maximum bonuses",
        difficulty: "expert",
        tags: ["endgame", "optimization", "bonus-scoring", "row-completion", "2-player"],
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
                createPlayer(
                    [['B'], ['Y'], ['R'], ['K'], ['W']],
                    createNearCompleteWall(0.7),
                    [],
                    40 + playerIdx * 3
                )
            )
        })
    };

    // Precise Counting Subcategory

    const finalTileCounting = {
        name: "Final Tile Counting",
        description: "Precise counting of remaining tiles for optimal endgame decisions",
        difficulty: "expert",
        tags: ["endgame", "counting", "precise", "final-tiles", "2-player"],
        generate: () => ({
            factories: [
                ['W'],
                ['W'],
                ['W'],
                ['W'],
                ['W']
            ],
            center: ['W', 'W', 'W'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayer(
                    [[], [], [], [], ['W', 'W', 'W']],
                    createNearCompleteWall(0.9),
                    [],
                    65 + playerIdx * 5
                )
            )
        })
    };

    const scoreOptimization = {
        name: "Score Optimization",
        description: "Maximizing final score through strategic tile placement",
        difficulty: "expert",
        tags: ["endgame", "optimization", "score-maximization", "strategic", "2-player"],
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
                createPlayer(
                    [['B', 'B'], ['Y'], ['R'], ['K'], ['W']],
                    createNearCompleteWall(0.75),
                    [],
                    48 + playerIdx * 4
                )
            )
        })
    };

    const penaltyMinimization = {
        name: "Penalty Minimization",
        description: "Avoiding floor line penalties while maximizing scoring",
        difficulty: "advanced",
        tags: ["endgame", "penalty", "minimization", "floor-line", "2-player"],
        generate: () => ({
            factories: [
                ['R', 'K'],
                ['W', 'B'],
                ['Y', 'R'],
                ['K', 'W'],
                ['B', 'Y']
            ],
            center: ['R', 'K', 'W'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayer(
                    [['R'], ['K'], ['W'], ['B'], ['Y']],
                    createNearCompleteWall(0.6),
                    ['R', 'K'],
                    35 + playerIdx * 7
                )
            )
        })
    };

    // Wall Completion Subcategory

    const fullWallCompletion = {
        name: "Full Wall Completion",
        description: "Race to complete entire wall for maximum bonuses",
        difficulty: "expert",
        tags: ["endgame", "wall-completion", "full-wall", "bonus", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'Y', 'R', 'K', 'W'],
                ['Y', 'R', 'K', 'W', 'B'],
                ['R', 'K', 'W', 'B', 'Y'],
                ['K', 'W', 'B', 'Y', 'R'],
                ['W', 'B', 'Y', 'R', 'K']
            ],
            center: ['B', 'Y', 'R', 'K', 'W'],
            players: Array(2).fill().map((_, playerIdx) => 
                createPlayer(
                    [['B', 'B', 'B', 'B'], ['Y', 'Y', 'Y', 'Y'], ['R', 'R', 'R', 'R'], ['K', 'K', 'K', 'K'], ['W', 'W', 'W', 'W']],
                    createNearCompleteWall(0.95),
                    [],
                    80 + playerIdx * 10
                )
            )
        })
    };

    const rowCompletionRace = {
        name: "Row Completion Race",
        description: "Competing to complete rows for scoring bonuses",
        difficulty: "advanced",
        tags: ["endgame", "row-completion", "race", "competitive", "2-player"],
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
                createPlayer(
                    [['B', 'B', 'B', 'B'], ['Y', 'Y', 'Y'], ['R', 'R'], ['K'], []],
                    createNearCompleteWall(0.6),
                    [],
                    55 + playerIdx * 8
                )
            )
        })
    };

    const columnCompletionFocus = {
        name: "Column Completion Focus",
        description: "Strategic focus on completing columns for vertical bonuses",
        difficulty: "advanced",
        tags: ["endgame", "column-completion", "vertical", "strategic", "2-player"],
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
                createPlayer(
                    [['B'], ['Y'], ['R'], ['K'], ['W']],
                    createNearCompleteWall(0.6),
                    [],
                    42 + playerIdx * 6
                )
            )
        })
    };

    // Return the organized structure
    return {
        "optimization": {
            name: "Final Optimization",
            description: "Maximizing endgame scoring",
            icon: "🎯",
            positions: [lastRoundEfficiency, tieBreakerScenario, bonusScoring]
        },
        "counting": {
            name: "Precise Counting",
            description: "Exact tile counting scenarios",
            icon: "🧮",
            positions: [finalTileCounting, scoreOptimization, penaltyMinimization]
        },
        "completion": {
            name: "Wall Completion",
            description: "Completing walls and patterns",
            icon: "🏆",
            positions: [fullWallCompletion, rowCompletionRace, columnCompletionFocus]
        }
    };
})(); 