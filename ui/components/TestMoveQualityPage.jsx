const { useState } = React;

const TestMoveQualityPage = () => {
    const [testMode, setTestMode] = useState('mock');
    const [testPosition, setTestPosition] = useState('opening');

    // Mock game state for testing
    const mockGameState = {
        fen_string: "eyJjZW50ZXIiOlsiYmx1ZSIsInJlZCJdLCJmYWN0b3JpZXMiOltbWyJibHVlIiwicmVkIiwieWVsbG93Il0sWyJibGFjayIsIndoaXRlIiwicmVkIl0sWyJibHVlIiwieWVsbG93IiwiYmxhY2siXSxbIndoaXRlIiwicmVkIiwiYmx1ZSJdLFsieWVsbG93IiwiYmxhY2siLCJ3aGl0ZSJdXSwicGxheWVycyI6W3sicGF0dGVybl9saW5lcyI6W1tdLFtdLFtdLFtdLFtdXSwid2FsbCI6W1tudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdXSwic2NvcmUiOjB9LHsicGF0dGVybl9saW5lcyI6W1tdLFtdLFtdLFtdLFtdXSwid2FsbCI6W1tudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdXSwic2NvcmUiOjB9XSwidHVybiI6MCwiZmlyc3RfcGxheWVyX3Rha2VuIjpmYWxzZX0=",
        factories: [
            { tiles: ['blue', 'red', 'yellow'] },
            { tiles: ['black', 'white', 'red'] },
            { tiles: ['blue', 'yellow', 'black'] },
            { tiles: ['white', 'red', 'blue'] },
            { tiles: ['yellow', 'black', 'white'] }
        ],
        center: ['blue', 'red'],
        players: [
            {
                pattern_lines: [[], [], [], [], []],
                wall: Array(5).fill().map(() => Array(5).fill(null)),
                floor_line: [],
                score: 0
            },
            {
                pattern_lines: [[], [], [], [], []],
                wall: Array(5).fill().map(() => Array(5).fill(null)),
                floor_line: [],
                score: 0
            }
        ],
        turn: 0,
        first_player_taken: false
    };

    const testPositions = {
        opening: {
            label: 'Opening Position',
            fen: 'eyJjZW50ZXIiOlsiYmx1ZSIsInJlZCJdLCJmYWN0b3JpZXMiOltbWyJibHVlIiwicmVkIiwieWVsbG93Il0sWyJibGFjayIsIndoaXRlIiwicmVkIl0sWyJibHVlIiwieWVsbG93IiwiYmxhY2siXSxbIndoaXRlIiwicmVkIiwiYmx1ZSJdLFsieWVsbG93IiwiYmxhY2siLCJ3aGl0ZSJdXSwicGxheWVycyI6W3sicGF0dGVybl9saW5lcyI6W1tdLFtdLFtdLFtdLFtdXSwid2FsbCI6W1tudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdXSwic2NvcmUiOjB9LHsicGF0dGVybl9saW5lcyI6W1tdLFtdLFtdLFtdLFtdXSwid2FsbCI6W1tudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdXSwic2NvcmUiOjB9XSwidHVybiI6MCwiZmlyc3RfcGxheWVyX3Rha2VuIjpmYWxzZX0=',
            description: 'Early game position with multiple options'
        },
        midgame: {
            label: 'Midgame Position', 
            fen: 'eyJjZW50ZXIiOlsiYmx1ZSIsInJlZCIsInllbGxvdyJdLCJmYWN0b3JpZXMiOltbWyJibHVlIiwicmVkIiwieWVsbG93Il0sWyJibGFjayIsIndoaXRlIiwicmVkIl0sWyJibHVlIiwieWVsbG93IiwiYmxhY2siXSxbIndoaXRlIiwicmVkIiwiYmx1ZSJdLFsieWVsbG93IiwiYmxhY2siLCJ3aGl0ZSJdXSwicGxheWVycyI6W3sicGF0dGVybl9saW5lcyI6W1siYmx1ZSJdLFtdLFtdLFtdLFtdXSwid2FsbCI6W1tudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdXSwic2NvcmUiOjV9LHsicGF0dGVybl9saW5lcyI6W1tdLFtdLFtdLFtdLFtdXSwid2FsbCI6W1tudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdXSwic2NvcmUiOjB9XSwidHVybiI6MSwiZmlyc3RfcGxheWVyX3Rha2VuIjp0cnVlfQ==',
            description: 'Complex midgame scenario'
        },
        endgame: {
            label: 'Endgame Position',
            fen: 'eyJjZW50ZXIiOltdLCJmYWN0b3JpZXMiOltbXSxbXSxbXSxbXSxbXV0sInBsYXllcnMiOlt7InBhdHRlcm5fbGluZXMiOltbImJsdWUiLCJyZWQiLCJ5ZWxsb3ciXSxbImJsYWNrIiwid2hpdGUiLCJyZWQiXSxbImJsdWUiLCJ5ZWxsb3ciLCJiYWNrIl0sWyJ3aGl0ZSIsInJlZCIsImJsdWUiXSxbInllbGxvdyIsImJsYWNrIiwid2hpdGUiXV0sIndhbGwiOltbImJsdWUiLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLCJyZWQiLG51bGwsbnVsbCxudWxsXSwibnVsbCIsbnVsbCwieWVsbG93IixudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCwiYmxhY2siLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLCJ3aGl0ZSJdXSwic2NvcmUiOjQwfSx7InBhdHRlcm5fbGluZXMiOltbXSxbXSxbXSxbXSxbXV0sIndhbGwiOltbbnVsbCxudWxsLG51bGwsbnVsbCxudWxsXSwibnVsbCIsbnVsbCxudWxsLG51bGwsbnVsbF0sIm51bGwiLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdLFtudWxsLG51bGwsbnVsbCxudWxsLG51bGxdXSwic2NvcmUiOjB9XSwidHVybiI6MCwiZmlyc3RfcGxheWVyX3Rha2VuIjp0cnVlfQ==',
            description: 'Critical endgame decisions'
        }
    };

    const renderTestControls = () => (
        <div style={{
            position: 'absolute',
            top: '20px',
            left: '20px',
            backgroundColor: 'white',
            border: '1px solid #ccc',
            borderRadius: '8px',
            padding: '16px',
            zIndex: 1001,
            width: '300px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
        }}>
            <h3>Move Quality Display Test</h3>
            
            <div style={{ marginBottom: '16px' }}>
                <label>Test Mode: </label>
                <select 
                    value={testMode} 
                    onChange={(e) => setTestMode(e.target.value)}
                    style={{ marginLeft: '8px' }}
                >
                    <option value="mock">Mock Data</option>
                    <option value="api">Real API</option>
                </select>
            </div>

            <div style={{ marginBottom: '16px' }}>
                <label>Test Position: </label>
                <select 
                    value={testPosition} 
                    onChange={(e) => setTestPosition(e.target.value)}
                    style={{ marginLeft: '8px' }}
                >
                    {Object.entries(testPositions).map(([key, pos]) => (
                        <option key={key} value={key}>{pos.label}</option>
                    ))}
                </select>
            </div>

            <div style={{ fontSize: '12px', color: '#666' }}>
                <strong>Current:</strong> {testPositions[testPosition].description}
            </div>
        </div>
    );

    const renderMoveQualityDisplay = () => {
        if (!window.MoveQualityDisplay) {
            return (
                <div style={{
                    position: 'fixed',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    backgroundColor: 'white',
                    border: '1px solid #ccc',
                    borderRadius: '8px',
                    padding: '20px',
                    zIndex: 1000
                }}>
                    <h3>MoveQualityDisplay Component Not Loaded</h3>
                    <p>Check the browser console for errors.</p>
                    <p>Make sure the component file is properly loaded in index.html</p>
                </div>
            );
        }

        return React.createElement('div', {
            style: {
                position: 'absolute',
                top: '20px',
                right: '20px',
                width: '400px',
                maxHeight: '600px',
                overflow: 'auto'
            }
        },
            React.createElement(window.MoveQualityDisplay, {
                gameState: mockGameState,
                currentPlayer: 0,
                onMoveRecommendation: (data) => {
                    console.log('Move recommendation received:', data);
                }
            })
        );
    };

    return React.createElement('div', {
        style: {
            minHeight: '100vh',
            backgroundColor: '#f5f5f5',
            padding: '20px',
            position: 'relative'
        }
    },
        renderTestControls(),
        renderMoveQualityDisplay()
    );
};

// Export to window for global access
window.TestMoveQualityPage = TestMoveQualityPage; 