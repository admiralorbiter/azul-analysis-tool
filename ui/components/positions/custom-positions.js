// Custom Positions Module
// Contains user-created positions and management functions for 2-player Azul games

window.customPositions = (() => {
    // Helper function to create custom player
    const createCustomPlayer = (patternLines, wallState, floorLine, score) => ({
        pattern_lines: patternLines,
        wall: wallState,
        floor_line: floorLine,
        score: score
    });

    // Helper function to create custom wall
    const createCustomWall = (tilePositions) => {
        const wall = Array(5).fill().map(() => Array(5).fill(null));
        tilePositions.forEach(([row, col, color]) => {
            wall[row][col] = color;
        });
        return wall;
    };

    // Example custom position
    const exampleCustomPosition = {
        name: "Example Custom Position",
        description: "A sample custom position created by a user",
        difficulty: "intermediate",
        tags: ["custom", "example", "user-created", "2-player"],
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
                createCustomPlayer(
                    [['B'], ['Y'], ['R'], [], []],
                    createCustomWall([[0, 0, 'B'], [1, 1, 'Y']]),
                    [],
                    10 + playerIdx * 2
                )
            )
        })
    };

    // Function to save custom position to localStorage
    window.saveCustomPosition = (position) => {
        try {
            const customPositions = window.getCustomPositions();
            customPositions.push(position);
            localStorage.setItem('azul_custom_positions', JSON.stringify(customPositions));
            return true;
        } catch (error) {
            console.error('Failed to save custom position:', error);
            return false;
        }
    };

    // Function to get custom positions from localStorage
    window.getCustomPositions = () => {
        try {
            const stored = localStorage.getItem('azul_custom_positions');
            return stored ? JSON.parse(stored).map(pos => ({...pos, generate: eval(`(${pos.generate})`) })) : [exampleCustomPosition]; // Re-parse generate function
        } catch (error) {
            console.error('Failed to load custom positions:', error);
            return [exampleCustomPosition];
        }
    };

    // Function to delete custom position
    window.deleteCustomPosition = (positionName) => {
        try {
            const customPositions = window.getCustomPositions();
            const filtered = customPositions.filter(pos => pos.name !== positionName);
            localStorage.setItem('azul_custom_positions', JSON.stringify(filtered));
            return true;
        } catch (error) {
            console.error('Failed to delete custom position:', error);
            return false;
        }
    };

    // Function to create position from current game state
    window.createPositionFromGameState = (gameState, name, description, difficulty, tags) => {
        return {
            name: name,
            description: description,
            difficulty: difficulty,
            tags: tags,
            generate: () => gameState
        };
    };

    // Return the organized structure
    return {
        "user-created": {
            name: "User-Created Positions",
            description: "Custom positions created by users",
            icon: "💾",
            positions: window.getCustomPositions()
        }
    };
})(); 