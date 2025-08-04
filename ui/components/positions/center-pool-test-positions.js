// Center Pool Test Positions
// Test positions to verify center pool display functionality

window.centerPoolTestPositions = {
    // Test position with tiles in center pool
    centerPoolWithTiles: {
        name: "Center Pool with Tiles",
        description: "Test position with various tiles in the center pool",
        gameState: {
            players: [
                {
                    pattern_lines: [[], [], [], [], []],
                    wall: [
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false]
                    ],
                    floor_line: [],
                    score: 0
                },
                {
                    pattern_lines: [[], [], [], [], []],
                    wall: [
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false]
                    ],
                    floor_line: [],
                    score: 0
                }
            ],
            factories: [
                ['B', 'Y', 'R', 'K'],
                ['W', 'B', 'Y', 'R'],
                ['K', 'W', 'B', 'Y'],
                ['R', 'K', 'W', 'B'],
                ['Y', 'R', 'K', 'W']
            ],
            centre_pool: {
                tiles: { 0: 2, 1: 1, 2: 3, 3: 1, 4: 2 },
                total: 9
            },
            first_player_taken: false
        }
    },
    
    // Test position with empty center pool
    emptyCenterPool: {
        name: "Empty Center Pool",
        description: "Test position with no tiles in center pool",
        gameState: {
            players: [
                {
                    pattern_lines: [[], [], [], [], []],
                    wall: [
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false]
                    ],
                    floor_line: [],
                    score: 0
                },
                {
                    pattern_lines: [[], [], [], [], []],
                    wall: [
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false]
                    ],
                    floor_line: [],
                    score: 0
                }
            ],
            factories: [
                ['B', 'Y', 'R', 'K'],
                ['W', 'B', 'Y', 'R'],
                ['K', 'W', 'B', 'Y'],
                ['R', 'K', 'W', 'B'],
                ['Y', 'R', 'K', 'W']
            ],
            centre_pool: {
                tiles: { 0: 0, 1: 0, 2: 0, 3: 0, 4: 0 },
                total: 0
            },
            first_player_taken: false
        }
    },
    
    // Test position with first player marker taken
    centerPoolWithFirstPlayer: {
        name: "Center Pool with First Player Marker",
        description: "Test position with first player marker taken",
        gameState: {
            players: [
                {
                    pattern_lines: [[], [], [], [], []],
                    wall: [
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false]
                    ],
                    floor_line: [],
                    score: 0
                },
                {
                    pattern_lines: [[], [], [], [], []],
                    wall: [
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false],
                        [false, false, false, false, false]
                    ],
                    floor_line: [],
                    score: 0
                }
            ],
            factories: [
                ['B', 'Y', 'R', 'K'],
                ['W', 'B', 'Y', 'R'],
                ['K', 'W', 'B', 'Y'],
                ['R', 'K', 'W', 'B'],
                ['Y', 'R', 'K', 'W']
            ],
            centre_pool: {
                tiles: { 0: 1, 1: 2, 2: 1, 3: 0, 4: 1 },
                total: 5
            },
            first_player_taken: true
        }
    }
}; 