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

    // Beginner Lessons Subcategory

    const patternLineBasics = {
        name: "Pattern Line Basics",
        description: "Learn how pattern lines work - simple setup for beginners",
        difficulty: "beginner",
        tags: ["educational", "beginner", "pattern-lines", "learning", "2-player"],
        generate: () => ({
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
        })
    };

    const wallPlacementBasics = {
        name: "Wall Placement Basics",
        description: "Understanding wall placement rules and scoring",
        difficulty: "beginner",
        tags: ["educational", "beginner", "wall-placement", "scoring", "2-player"],
        generate: () => ({
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
        })
    };

    const floorLinePenalty = {
        name: "Floor Line Penalty",
        description: "Learn about floor line penalties and how to avoid them",
        difficulty: "beginner",
        tags: ["educational", "beginner", "floor-line", "penalty", "2-player"],
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
                createSimplePlayer(
                    [['B', 'B', 'B'], ['Y', 'Y'], ['R'], [], []],
                    createBasicWall([[0, 0, 'B'], [1, 1, 'Y']]),
                    ['B', 'Y'],
                    3 + playerIdx * 2
                )
            )
        })
    };

    // Intermediate Challenges Subcategory

    const rowCompletionStrategy = {
        name: "Row Completion Strategy",
        description: "Learn to complete rows for scoring bonuses",
        difficulty: "intermediate",
        tags: ["educational", "intermediate", "row-completion", "strategy", "2-player"],
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
                createSimplePlayer(
                    [['B', 'B', 'B', 'B'], ['Y', 'Y', 'Y'], ['R', 'R'], ['K'], []],
                    createBasicWall([
                        [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                        [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B']
                    ]),
                    [],
                    15 + playerIdx * 4
                )
            )
        })
    };

    const columnCompletionStrategy = {
        name: "Column Completion Strategy",
        description: "Learn to complete columns for scoring bonuses",
        difficulty: "intermediate",
        tags: ["educational", "intermediate", "column-completion", "strategy", "2-player"],
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
                createSimplePlayer(
                    [['B'], ['Y'], ['R'], ['K'], ['W']],
                    createBasicWall([
                        [0, 0, 'B'], [1, 0, 'Y'], [2, 0, 'R'], [3, 0, 'K'], [4, 0, 'W'],
                        [0, 1, 'Y'], [1, 1, 'R'], [2, 1, 'K'], [3, 1, 'W'], [4, 1, 'B'],
                        [0, 2, 'R'], [1, 2, 'K'], [2, 2, 'W'], [3, 2, 'B'], [4, 2, 'Y']
                    ]),
                    [],
                    18 + playerIdx * 5
                )
            )
        })
    };

    const colorCompletionBonus = {
        name: "Color Completion Bonus",
        description: "Learn about color completion bonuses and how to achieve them",
        difficulty: "intermediate",
        tags: ["educational", "intermediate", "color-completion", "bonus", "2-player"],
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
                createSimplePlayer(
                    [['B', 'B', 'B', 'B'], ['Y', 'Y', 'Y', 'Y'], ['R', 'R', 'R', 'R'], ['K', 'K', 'K', 'K'], ['W', 'W', 'W', 'W']],
                    createBasicWall([
                        [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                        [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B'],
                        [2, 0, 'R'], [2, 1, 'K'], [2, 2, 'W'], [2, 3, 'B'], [2, 4, 'Y'],
                        [3, 0, 'K'], [3, 1, 'W'], [3, 2, 'B'], [3, 3, 'Y'], [3, 4, 'R']
                    ]),
                    [],
                    25 + playerIdx * 6
                )
            )
        })
    };

    // Advanced Concepts Subcategory

    const wallCompletionStrategy = {
        name: "Wall Completion Strategy",
        description: "Advanced strategy for completing entire walls",
        difficulty: "advanced",
        tags: ["educational", "advanced", "wall-completion", "strategy", "2-player"],
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
                createSimplePlayer(
                    [['B', 'B', 'B', 'B'], ['Y', 'Y', 'Y', 'Y'], ['R', 'R', 'R', 'R'], ['K', 'K', 'K', 'K'], ['W', 'W', 'W', 'W']],
                    createBasicWall([
                        [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                        [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B'],
                        [2, 0, 'R'], [2, 1, 'K'], [2, 2, 'W'], [2, 3, 'B'], [2, 4, 'Y'],
                        [3, 0, 'K'], [3, 1, 'W'], [3, 2, 'B'], [3, 3, 'Y'], [3, 4, 'R'],
                        [4, 0, 'W'], [4, 1, 'B'], [4, 2, 'Y'], [4, 3, 'R'], [4, 4, 'K']
                    ]),
                    [],
                    35 + playerIdx * 8
                )
            )
        })
    };

    const endgamePlanning = {
        name: "Endgame Planning",
        description: "Learn to plan for the endgame and final scoring",
        difficulty: "advanced",
        tags: ["educational", "advanced", "endgame", "planning", "2-player"],
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
                createSimplePlayer(
                    [['B', 'B', 'B'], ['Y', 'Y'], ['R'], ['K'], ['W']],
                    createBasicWall([
                        [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                        [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B'],
                        [2, 0, 'R'], [2, 1, 'K'], [2, 2, 'W'], [2, 3, 'B'], [2, 4, 'Y'],
                        [3, 0, 'K'], [3, 1, 'W'], [3, 2, 'B'], [3, 3, 'Y'], [3, 4, 'R']
                    ]),
                    [],
                    28 + playerIdx * 5
                )
            )
        })
    };

    const tileEfficiencyLesson = {
        name: "Tile Efficiency Lesson",
        description: "Learn to maximize points per tile - efficiency optimization",
        difficulty: "advanced",
        tags: ["educational", "advanced", "tile-efficiency", "optimization", "2-player"],
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
                createSimplePlayer(
                    [['B'], ['Y'], ['R'], ['K'], ['W']],
                    createBasicWall([
                        [0, 0, 'B'], [1, 1, 'Y'], [2, 2, 'R'], [3, 3, 'K'], [4, 4, 'W']
                    ]),
                    [],
                    12 + playerIdx * 3
                )
            )
        })
    };

    // Expert Concepts Subcategory

    const competitiveStrategy = {
        name: "Competitive Strategy",
        description: "Advanced competitive play concepts and tactics",
        difficulty: "expert",
        tags: ["educational", "expert", "competitive", "strategy", "2-player"],
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
                createSimplePlayer(
                    [['B', 'B', 'B'], ['Y', 'Y'], ['R'], ['K'], ['W']],
                    createBasicWall([
                        [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                        [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B'],
                        [2, 0, 'R'], [2, 1, 'K'], [2, 2, 'W'], [2, 3, 'B'], [2, 4, 'Y'],
                        [3, 0, 'K'], [3, 1, 'W'], [3, 2, 'B'], [3, 3, 'Y'], [3, 4, 'R']
                    ]),
                    [],
                    22 + playerIdx * 4
                )
            )
        })
    };

    const timingCriticalLesson = {
        name: "Timing Critical Lesson",
        description: "Learn about critical timing decisions in competitive play",
        difficulty: "expert",
        tags: ["educational", "expert", "timing", "critical-decisions", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'B'],
                ['Y', 'Y'],
                ['R', 'R'],
                ['K', 'K'],
                ['W', 'W']
            ],
            center: ['B', 'Y', 'R', 'K', 'W'],
            players: Array(2).fill().map((_, playerIdx) => 
                createSimplePlayer(
                    [['B', 'B'], ['Y', 'Y'], ['R', 'R'], ['K', 'K'], ['W', 'W']],
                    createBasicWall([
                        [0, 0, 'B'], [0, 1, 'Y'], [0, 2, 'R'], [0, 3, 'K'], [0, 4, 'W'],
                        [1, 0, 'Y'], [1, 1, 'R'], [1, 2, 'K'], [1, 3, 'W'], [1, 4, 'B']
                    ]),
                    [],
                    30 + playerIdx * 5
                )
            )
        })
    };

    // Return the organized structure
    return {
        "beginner": {
            name: "Beginner Lessons",
            description: "Basic concepts and simple tactics",
            icon: "📚",
            positions: [patternLineBasics, wallPlacementBasics, floorLinePenalty]
        },
        "intermediate": {
            name: "Intermediate Challenges",
            description: "More complex strategies and concepts",
            icon: "🎯",
            positions: [rowCompletionStrategy, columnCompletionStrategy, colorCompletionBonus]
        },
        "advanced": {
            name: "Advanced Concepts",
            description: "Complex strategies and advanced techniques",
            icon: "🧠",
            positions: [wallCompletionStrategy, endgamePlanning, tileEfficiencyLesson]
        },
        "expert": {
            name: "Expert Concepts",
            description: "Master-level strategies and competitive play",
            icon: "🏆",
            positions: [competitiveStrategy, timingCriticalLesson]
        }
    };
})(); 