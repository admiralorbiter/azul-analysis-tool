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

    // Balanced Opening Subcategory

    const balancedStart = {
        name: "Balanced Start",
        description: "Standard opening with equal distribution of all colors",
        difficulty: "beginner",
        tags: ["opening", "balanced", "standard", "beginner-friendly", "2-player"],
        generate: () => ({
            factories: createBalancedFactories(),
            center: ['B', 'Y', 'R', 'K', 'W'],
            players: Array(2).fill().map(() => createEmptyPlayer())
        })
    };

    const blueFocusStart = {
        name: "Blue Focus Start",
        description: "Opening with emphasis on blue tiles - good for beginners",
        difficulty: "beginner",
        tags: ["opening", "blue-focus", "beginner-friendly", "color-strategy", "2-player"],
        generate: () => ({
            factories: createColorFocusedFactories('B', 'Y'),
            center: ['B', 'B', 'Y', 'R'],
            players: Array(2).fill().map(() => createEmptyPlayer())
        })
    };

    const yellowFocusStart = {
        name: "Yellow Focus Start",
        description: "Opening with emphasis on yellow tiles - balanced approach",
        difficulty: "beginner",
        tags: ["opening", "yellow-focus", "beginner-friendly", "color-strategy", "2-player"],
        generate: () => ({
            factories: createColorFocusedFactories('Y', 'B'),
            center: ['Y', 'Y', 'B', 'R'],
            players: Array(2).fill().map(() => createEmptyPlayer())
        })
    };

    // Aggressive Opening Subcategory

    const aggressiveStart = {
        name: "Aggressive Start",
        description: "High-risk opening with concentrated colors",
        difficulty: "intermediate",
        tags: ["opening", "aggressive", "high-risk", "concentrated", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'B', 'B', 'B'],
                ['Y', 'Y', 'Y', 'Y'],
                ['R', 'R', 'R', 'R'],
                ['K', 'K', 'K', 'K'],
                ['W', 'W', 'W', 'W']
            ],
            center: ['B', 'Y', 'R'],
            players: Array(2).fill().map(() => createEmptyPlayer())
        })
    };

    const centerHeavyStart = {
        name: "Center Heavy Start",
        description: "Opening with many tiles in center - tactical complexity",
        difficulty: "intermediate",
        tags: ["opening", "center-heavy", "tactical", "complex", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'B', 'Y', 'Y'],
                ['R', 'R', 'K', 'K'],
                ['W', 'W', 'B', 'B'],
                ['Y', 'Y', 'R', 'R'],
                ['K', 'K', 'W', 'W']
            ],
            center: ['B', 'Y', 'R', 'K', 'W', 'B', 'Y', 'R', 'K', 'W'],
            players: Array(2).fill().map(() => createEmptyPlayer())
        })
    };

    const factoryControlStart = {
        name: "Factory Control Start",
        description: "Strategic opening focusing on factory control",
        difficulty: "intermediate",
        tags: ["opening", "factory-control", "strategic", "control", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'Y', 'R', 'K', 'W'],
                ['B', 'Y', 'R', 'K', 'W'],
                ['B', 'Y', 'R', 'K', 'W'],
                ['B', 'Y', 'R', 'K', 'W'],
                ['B', 'Y', 'R', 'K', 'W']
            ],
            center: ['B', 'Y', 'R'],
            players: Array(2).fill().map(() => createEmptyPlayer())
        })
    };

    // Defensive Opening Subcategory

    const defensiveStart = {
        name: "Defensive Start",
        description: "Conservative opening with minimal risk",
        difficulty: "beginner",
        tags: ["opening", "defensive", "conservative", "low-risk", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'B', 'Y', 'Y'],
                ['R', 'R', 'K', 'K'],
                ['W', 'W', 'B', 'B'],
                ['Y', 'Y', 'R', 'R'],
                ['K', 'K', 'W', 'W']
            ],
            center: ['B', 'Y'],
            players: Array(2).fill().map(() => createEmptyPlayer())
        })
    };

    const safeStart = {
        name: "Safe Start",
        description: "Very conservative opening - good for learning",
        difficulty: "beginner",
        tags: ["opening", "safe", "conservative", "learning", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'B', 'B', 'B'],
                ['Y', 'Y', 'Y', 'Y'],
                ['R', 'R', 'R', 'R'],
                ['K', 'K', 'K', 'K'],
                ['W', 'W', 'W', 'W']
            ],
            center: ['B', 'Y'],
            players: Array(2).fill().map(() => createEmptyPlayer())
        })
    };

    const flexibleStart = {
        name: "Flexible Start",
        description: "Adaptable opening allowing multiple strategies",
        difficulty: "intermediate",
        tags: ["opening", "flexible", "adaptable", "multi-strategy", "2-player"],
        generate: () => ({
            factories: [
                ['B', 'B', 'Y', 'R'],
                ['K', 'W', 'B', 'Y'],
                ['Y', 'R', 'K', 'W'],
                ['W', 'B', 'Y', 'R'],
                ['R', 'K', 'W', 'B']
            ],
            center: ['B', 'Y', 'R', 'K'],
            players: Array(2).fill().map(() => createEmptyPlayer())
        })
    };

    // Return the organized structure
    return {
        "balanced": {
            name: "Balanced Openings",
            description: "Standard and balanced starting positions",
            icon: "⚖️",
            positions: [balancedStart, blueFocusStart, yellowFocusStart]
        },
        "aggressive": {
            name: "Aggressive Openings",
            description: "High-risk, high-reward starting positions",
            icon: "⚔️",
            positions: [aggressiveStart, centerHeavyStart, factoryControlStart]
        },
        "defensive": {
            name: "Defensive Openings",
            description: "Conservative and safe starting positions",
            icon: "🛡️",
            positions: [defensiveStart, safeStart, flexibleStart]
        }
    };
})(); 