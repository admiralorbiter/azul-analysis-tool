/**
 * FEN Display Component - UI Support for Standard FEN Format
 * 
 * Features:
 * - Display current FEN string
 * - Copy FEN to clipboard
 * - FEN validation and formatting
 * - Collapsible detailed view
 * - FEN sharing functionality
 * 
 * Version: 1.0.0 - Initial implementation for UI support
 */

const { useState, useEffect } = React;

const FENDisplay = ({ 
    gameState, 
    className = '',
    showDetails = false,
    onFENChange = null
}) => {
    const [fenString, setFenString] = useState('');
    const [isCopied, setIsCopied] = useState(false);
    const [showFullFEN, setShowFullFEN] = useState(false);
    const [fenValidation, setFenValidation] = useState({ valid: true, error: null });
    const [isLoading, setIsLoading] = useState(false);

    // Update FEN string when game state changes
    useEffect(() => {
        if (gameState && gameState.fen_string) {
            setFenString(gameState.fen_string);
            validateFEN(gameState.fen_string);
        } else {
            setFenString('No FEN available');
            setFenValidation({ valid: false, error: 'No game state available' });
        }
    }, [gameState]);

    // Validate FEN string
    const validateFEN = async (fen) => {
        if (!fen || fen === 'No FEN available') {
            setFenValidation({ valid: false, error: 'Invalid FEN' });
            return;
        }

        try {
            const response = await fetch('/api/v1/validate-fen', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fen_string: fen })
            });
            
            const result = await response.json();
            setFenValidation({ 
                valid: result.valid || false, 
                error: result.error || null 
            });
        } catch (error) {
            setFenValidation({ valid: false, error: 'Validation failed' });
        }
    };

    // Copy FEN to clipboard
    const copyFENToClipboard = async () => {
        try {
            await navigator.clipboard.writeText(fenString);
            setIsCopied(true);
            setTimeout(() => setIsCopied(false), 2000);
        } catch (error) {
            console.error('Failed to copy FEN:', error);
        }
    };

    // Parse FEN for detailed display
    const parseFENForDisplay = (fen) => {
        if (!fen || fen === 'No FEN available') return null;
        
        try {
            const parts = fen.split('/');
            if (parts.length < 7) return null;
            
            return {
                factories: parts[0].split('|'),
                center: parts[1],
                player1: {
                    wall: parts[2].split('|'),
                    pattern: parts[3].split('|'),
                    floor: parts[4]
                },
                player2: {
                    wall: parts[5].split('|'),
                    pattern: parts[6].split('|'),
                    floor: parts[7]
                },
                scores: parts[8] || '0,0',
                round: parts[9] || '1',
                currentPlayer: parts[10] || '0'
            };
        } catch (error) {
            return null;
        }
    };

    const fenData = parseFENForDisplay(fenString);

    return React.createElement('div', {
        className: `fen-display ${className}`,
        style: {
            backgroundColor: '#f8f9fa',
            border: '1px solid #dee2e6',
            borderRadius: '8px',
            padding: '12px',
            margin: '8px 0'
        }
    },
        // Header with title and copy button
        React.createElement('div', {
            style: {
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '8px'
            }
        },
            React.createElement('h4', {
                style: {
                    margin: '0',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#495057'
                }
            }, '🎯 FEN String'),
            React.createElement('button', {
                onClick: copyFENToClipboard,
                disabled: !fenValidation.valid,
                style: {
                    padding: '4px 8px',
                    fontSize: '12px',
                    backgroundColor: isCopied ? '#28a745' : '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: fenValidation.valid ? 'pointer' : 'not-allowed',
                    opacity: fenValidation.valid ? 1 : 0.6
                }
            }, isCopied ? '✅ Copied!' : '📋 Copy')
        ),

        // FEN string display
        React.createElement('div', {
            style: {
                backgroundColor: '#ffffff',
                border: '1px solid #ced4da',
                borderRadius: '4px',
                padding: '8px',
                fontFamily: 'monospace',
                fontSize: '12px',
                wordBreak: 'break-all',
                maxHeight: showFullFEN ? 'none' : '60px',
                overflow: 'hidden',
                position: 'relative'
            }
        },
            React.createElement('span', {
                style: {
                    color: fenValidation.valid ? '#28a745' : '#dc3545'
                }
            }, fenString),
            !showFullFEN && fenString.length > 100 && React.createElement('button', {
                onClick: () => setShowFullFEN(true),
                style: {
                    position: 'absolute',
                    bottom: '4px',
                    right: '4px',
                    fontSize: '10px',
                    padding: '2px 4px',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer'
                }
            }, 'Show More')
        ),

        // Validation status
        React.createElement('div', {
            style: {
                marginTop: '8px',
                fontSize: '11px',
                color: fenValidation.valid ? '#28a745' : '#dc3545'
            }
        },
            React.createElement('span', null, 
                fenValidation.valid ? '✅ Valid FEN' : `❌ ${fenValidation.error || 'Invalid FEN'}`
            )
        ),

        // Detailed FEN breakdown (collapsible)
        showDetails && fenData && React.createElement('div', {
            style: {
                marginTop: '12px',
                borderTop: '1px solid #dee2e6',
                paddingTop: '8px'
            }
        },
            React.createElement('details', {
                style: { fontSize: '12px' }
            },
                React.createElement('summary', {
                    style: {
                        cursor: 'pointer',
                        fontWeight: '600',
                        color: '#495057'
                    }
                }, '📊 FEN Breakdown'),
                React.createElement('div', {
                    style: {
                        marginTop: '8px',
                        fontSize: '11px',
                        color: '#6c757d'
                    }
                },
                    // Factories
                    React.createElement('div', { style: { marginBottom: '4px' } },
                        React.createElement('strong', null, 'Factories: '),
                        fenData.factories.join(' | ')
                    ),
                    // Center
                    React.createElement('div', { style: { marginBottom: '4px' } },
                        React.createElement('strong', null, 'Center: '),
                        fenData.center || '-'
                    ),
                    // Player 1
                    React.createElement('div', { style: { marginBottom: '4px' } },
                        React.createElement('strong', null, 'Player 1: '),
                        `Wall: ${fenData.player1.wall.join('|')} | Pattern: ${fenData.player1.pattern.join('|')} | Floor: ${fenData.player1.floor}`
                    ),
                    // Player 2
                    React.createElement('div', { style: { marginBottom: '4px' } },
                        React.createElement('strong', null, 'Player 2: '),
                        `Wall: ${fenData.player2.wall.join('|')} | Pattern: ${fenData.player2.pattern.join('|')} | Floor: ${fenData.player2.floor}`
                    ),
                    // Game info
                    React.createElement('div', { style: { marginBottom: '4px' } },
                        React.createElement('strong', null, 'Scores: '),
                        fenData.scores
                    ),
                    React.createElement('div', { style: { marginBottom: '4px' } },
                        React.createElement('strong', null, 'Round: '),
                        fenData.round
                    ),
                    React.createElement('div', { style: { marginBottom: '4px' } },
                        React.createElement('strong', null, 'Current Player: '),
                        parseInt(fenData.currentPlayer) + 1
                    )
                )
            )
        )
    );
};

// Export for use in other components
window.FENDisplay = FENDisplay; 