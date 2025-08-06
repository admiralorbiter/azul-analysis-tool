/**
 * Test FEN UI Components
 * 
 * Demonstrates the FEN display, input, and management components
 * for testing the UI support implementation.
 * 
 * Version: 1.0.0 - Initial implementation
 */

const { useState, useEffect } = React;

const TestFENUI = () => {
    const [gameState, setGameState] = useState(null);
    const [testMode, setTestMode] = useState('display');

    // Sample game states for testing
    const sampleGameStates = [
        {
            name: 'Empty Game',
            gameState: {
                fen_string: '-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-|--|---|----|-----/-/-----|-----|-----|-----|-----/-|--|---|----|-----/-/0,0/1/0',
                factories: [[], [], [], [], []],
                center: [],
                players: [
                    {
                        pattern_lines: [[], [], [], [], []],
                        wall: Array(5).fill().map(() => Array(5).fill(null)),
                        floor: [],
                        score: 0
                    },
                    {
                        pattern_lines: [[], [], [], [], []],
                        wall: Array(5).fill().map(() => Array(5).fill(null)),
                        floor: [],
                        score: 0
                    }
                ]
            }
        },
        {
            name: 'Sample Position',
            gameState: {
                fen_string: 'BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-|--|---|----|-----/-/-----|-----|-----|-----|-----/-|--|---|----|-----/-/0,0/1/0',
                factories: [
                    ['B', 'Y', 'R', 'K'],
                    ['W', 'B', 'Y', 'R'],
                    ['K', 'W', 'B', 'Y'],
                    ['R', 'K', 'W', 'B'],
                    ['Y', 'R', 'K', 'W']
                ],
                center: ['B', 'Y', 'R', 'K', 'W'],
                players: [
                    {
                        pattern_lines: [[], [], [], [], []],
                        wall: Array(5).fill().map(() => Array(5).fill(null)),
                        floor: [],
                        score: 0
                    },
                    {
                        pattern_lines: [[], [], [], [], []],
                        wall: Array(5).fill().map(() => Array(5).fill(null)),
                        floor: [],
                        score: 0
                    }
                ]
            }
        },
        {
            name: 'Midgame Position',
            gameState: {
                fen_string: 'BBYY|RRKK|WWBB|YYRR|KKWW/BYR/B----|-----|-----|-----|-----/-|--|---|----|-----/-/-----|-----|-----|-----|-----/-|--|---|----|-----/-/15,20/3/0',
                factories: [
                    ['B', 'B', 'Y', 'Y'],
                    ['R', 'R', 'K', 'K'],
                    ['W', 'W', 'B', 'B'],
                    ['Y', 'Y', 'R', 'R'],
                    ['K', 'K', 'W', 'W']
                ],
                center: ['B', 'Y', 'R'],
                players: [
                    {
                        pattern_lines: [['B'], [], [], [], []],
                        wall: [
                            ['B', null, null, null, null],
                            [null, null, null, null, null],
                            [null, null, null, null, null],
                            [null, null, null, null, null],
                            [null, null, null, null, null]
                        ],
                        floor: [],
                        score: 15
                    },
                    {
                        pattern_lines: [[], [], [], [], []],
                        wall: Array(5).fill().map(() => Array(5).fill(null)),
                        floor: [],
                        score: 20
                    }
                ]
            }
        }
    ];

    // Initialize with first sample
    useEffect(() => {
        setGameState(sampleGameStates[0].gameState);
    }, []);

    const handleFENLoad = (newGameState) => {
        setGameState(newGameState);
        console.log('FEN loaded:', newGameState);
    };

    return React.createElement('div', {
        style: {
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '20px',
            fontFamily: 'Arial, sans-serif'
        }
    },
        // Header
        React.createElement('div', {
            style: {
                textAlign: 'center',
                marginBottom: '30px',
                padding: '20px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px'
            }
        },
            React.createElement('h1', {
                style: {
                    margin: '0 0 10px 0',
                    color: '#495057',
                    fontSize: '24px'
                }
            }, '🎯 FEN UI Support Test'),
            React.createElement('p', {
                style: {
                    margin: '0',
                    color: '#6c757d',
                    fontSize: '14px'
                }
            }, 'Testing the new FEN display, input, and management components')
        ),

        // Test mode selector
        React.createElement('div', {
            style: {
                marginBottom: '20px',
                padding: '16px',
                backgroundColor: '#ffffff',
                border: '1px solid #dee2e6',
                borderRadius: '8px'
            }
        },
            React.createElement('h3', {
                style: {
                    margin: '0 0 12px 0',
                    fontSize: '16px',
                    color: '#495057'
                }
            }, '🧪 Test Configuration'),
            React.createElement('div', {
                style: {
                    display: 'flex',
                    gap: '12px',
                    flexWrap: 'wrap'
                }
            },
                React.createElement('label', {
                    style: { display: 'flex', alignItems: 'center', gap: '6px' }
                },
                    React.createElement('input', {
                        type: 'radio',
                        name: 'testMode',
                        value: 'display',
                        checked: testMode === 'display',
                        onChange: (e) => setTestMode(e.target.value)
                    }),
                    'FEN Display Only'
                ),
                React.createElement('label', {
                    style: { display: 'flex', alignItems: 'center', gap: '6px' }
                },
                    React.createElement('input', {
                        type: 'radio',
                        name: 'testMode',
                        value: 'input',
                        checked: testMode === 'input',
                        onChange: (e) => setTestMode(e.target.value)
                    }),
                    'FEN Input Only'
                ),
                React.createElement('label', {
                    style: { display: 'flex', alignItems: 'center', gap: '6px' }
                },
                    React.createElement('input', {
                        type: 'radio',
                        name: 'testMode',
                        value: 'manager',
                        checked: testMode === 'manager',
                        onChange: (e) => setTestMode(e.target.value)
                    }),
                    'FEN Manager (Combined)'
                )
            )
        ),

        // Sample game state selector
        React.createElement('div', {
            style: {
                marginBottom: '20px',
                padding: '16px',
                backgroundColor: '#ffffff',
                border: '1px solid #dee2e6',
                borderRadius: '8px'
            }
        },
            React.createElement('h3', {
                style: {
                    margin: '0 0 12px 0',
                    fontSize: '16px',
                    color: '#495057'
                }
            }, '📋 Sample Game States'),
            React.createElement('div', {
                style: {
                    display: 'flex',
                    gap: '8px',
                    flexWrap: 'wrap'
                }
            },
                sampleGameStates.map((sample, index) => 
                    React.createElement('button', {
                        key: index,
                        onClick: () => setGameState(sample.gameState),
                        style: {
                            padding: '8px 12px',
                            fontSize: '12px',
                            backgroundColor: gameState === sample.gameState ? '#007bff' : '#6c757d',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }
                    }, sample.name)
                )
            )
        ),

        // Component test area
        React.createElement('div', {
            style: {
                display: 'grid',
                gridTemplateColumns: '1fr',
                gap: '20px'
            }
        },
            // FEN Display test
            testMode === 'display' && React.createElement('div', {
                style: {
                    padding: '16px',
                    backgroundColor: '#ffffff',
                    border: '1px solid #dee2e6',
                    borderRadius: '8px'
                }
            },
                React.createElement('h3', {
                    style: {
                        margin: '0 0 12px 0',
                        fontSize: '16px',
                        color: '#495057'
                    }
                }, '📋 FEN Display Component'),
                React.createElement(window.FENDisplay, {
                    gameState: gameState,
                    showDetails: true
                })
            ),

            // FEN Input test
            testMode === 'input' && React.createElement('div', {
                style: {
                    padding: '16px',
                    backgroundColor: '#ffffff',
                    border: '1px solid #dee2e6',
                    borderRadius: '8px'
                }
            },
                React.createElement('h3', {
                    style: {
                        margin: '0 0 12px 0',
                        fontSize: '16px',
                        color: '#495057'
                    }
                }, '📥 FEN Input Component'),
                React.createElement(window.FENInput, {
                    onFENLoad: handleFENLoad
                })
            ),

            // FEN Manager test
            testMode === 'manager' && React.createElement('div', {
                style: {
                    padding: '16px',
                    backgroundColor: '#ffffff',
                    border: '1px solid #dee2e6',
                    borderRadius: '8px'
                }
            },
                React.createElement('h3', {
                    style: {
                        margin: '0 0 12px 0',
                        fontSize: '16px',
                        color: '#495057'
                    }
                }, '🎛️ FEN Manager Component'),
                React.createElement(window.FENManager, {
                    gameState: gameState,
                    onFENLoad: handleFENLoad
                })
            )
        ),

        // Current game state info
        React.createElement('div', {
            style: {
                marginTop: '20px',
                padding: '16px',
                backgroundColor: '#f8f9fa',
                border: '1px solid #dee2e6',
                borderRadius: '8px'
            }
        },
            React.createElement('h3', {
                style: {
                    margin: '0 0 12px 0',
                    fontSize: '16px',
                    color: '#495057'
                }
            }, '📊 Current Game State Info'),
            React.createElement('div', {
                style: {
                    fontSize: '12px',
                    color: '#6c757d'
                }
            },
                React.createElement('p', { style: { margin: '4px 0' } },
                    React.createElement('strong', null, 'FEN String: '),
                    gameState?.fen_string || 'None'
                ),
                React.createElement('p', { style: { margin: '4px 0' } },
                    React.createElement('strong', null, 'Factories: '),
                    gameState?.factories?.length || 0, ' factories'
                ),
                React.createElement('p', { style: { margin: '4px 0' } },
                    React.createElement('strong', null, 'Center Tiles: '),
                    gameState?.center?.length || 0, ' tiles'
                ),
                React.createElement('p', { style: { margin: '4px 0' } },
                    React.createElement('strong', null, 'Players: '),
                    gameState?.players?.length || 0, ' players'
                )
            )
        )
    );
};

// Export for use in other components
window.TestFENUI = TestFENUI; 