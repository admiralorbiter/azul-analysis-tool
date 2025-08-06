/**
 * FEN Input Component - UI Support for Standard FEN Format
 * 
 * Features:
 * - Input FEN string manually
 * - Validate FEN format
 * - Load FEN into game state
 * - Error handling and feedback
 * - FEN format examples
 * 
 * Version: 1.0.0 - Initial implementation for UI support
 */

const { useState, useEffect } = React;

const FENInput = ({ 
    onFENLoad = null,
    className = '',
    placeholder = 'Enter FEN string...'
}) => {
    const [fenInput, setFenInput] = useState('');
    const [isValidating, setIsValidating] = useState(false);
    const [validationResult, setValidationResult] = useState({ valid: true, error: null });
    const [isLoading, setIsLoading] = useState(false);
    const [showExamples, setShowExamples] = useState(false);

    // Example FEN strings for reference
    const fenExamples = [
        {
            name: 'Empty Game',
            fen: '-----|-----|-----|-----|-----/-/-----|-----|-----|-----|-----/-|--|---|----|-----/-/-----|-----|-----|-----|-----/-|--|---|----|-----/-/0,0/1/0',
            description: 'Starting position with empty board'
        },
        {
            name: 'Sample Position',
            fen: 'BYRK|WBYR|KWBY|RKWB|YRKW/BYRKW/-----|-----|-----|-----|-----/-|--|---|----|-----/-/-----|-----|-----|-----|-----/-|--|---|----|-----/-/0,0/1/0',
            description: 'Position with some tiles in factories and center'
        },
        {
            name: 'Midgame Position',
            fen: 'BBYY|RRKK|WWBB|YYRR|KKWW/BYR/B----|-----|-----|-----|-----/-|--|---|----|-----/-/-----|-----|-----|-----|-----/-|--|---|----|-----/-/15,20/3/0',
            description: 'Midgame position with scores and some wall tiles'
        }
    ];

    // Validate FEN input
    const validateFENInput = async (fen) => {
        if (!fen.trim()) {
            setValidationResult({ valid: false, error: 'FEN string cannot be empty' });
            return false;
        }

        setIsValidating(true);
        try {
            const response = await fetch('/api/v1/validate-fen', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fen_string: fen })
            });
            
            const result = await response.json();
            setValidationResult({ 
                valid: result.valid || false, 
                error: result.error || null 
            });
            return result.valid || false;
        } catch (error) {
            setValidationResult({ valid: false, error: 'Validation failed' });
            return false;
        } finally {
            setIsValidating(false);
        }
    };

    // Load FEN into game
    const loadFEN = async () => {
        if (!fenInput.trim()) {
            setValidationResult({ valid: false, error: 'Please enter a FEN string' });
            return;
        }

        const isValid = await validateFENInput(fenInput);
        if (!isValid) return;

        setIsLoading(true);
        try {
            const response = await fetch('/api/v1/game_state', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fen_string: fenInput })
            });
            
            const result = await response.json();
            if (result.success && result.game_state) {
                if (onFENLoad) {
                    onFENLoad(result.game_state);
                }
                setValidationResult({ valid: true, error: null });
            } else {
                setValidationResult({ valid: false, error: 'Failed to load FEN' });
            }
        } catch (error) {
            setValidationResult({ valid: false, error: 'Failed to load FEN' });
        } finally {
            setIsLoading(false);
        }
    };

    // Handle input change
    const handleInputChange = (e) => {
        setFenInput(e.target.value);
        if (e.target.value.trim()) {
            // Clear validation error when user starts typing
            setValidationResult({ valid: true, error: null });
        }
    };

    // Handle example selection
    const handleExampleSelect = (example) => {
        setFenInput(example.fen);
        setValidationResult({ valid: true, error: null });
    };

    return React.createElement('div', {
        className: `fen-input ${className}`,
        style: {
            backgroundColor: '#f8f9fa',
            border: '1px solid #dee2e6',
            borderRadius: '8px',
            padding: '16px',
            margin: '8px 0'
        }
    },
        // Header
        React.createElement('div', {
            style: {
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '12px'
            }
        },
            React.createElement('h4', {
                style: {
                    margin: '0',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#495057'
                }
            }, '📥 Load FEN String'),
            React.createElement('button', {
                onClick: () => setShowExamples(!showExamples),
                style: {
                    padding: '4px 8px',
                    fontSize: '12px',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                }
            }, showExamples ? 'Hide Examples' : 'Show Examples')
        ),

        // Input field
        React.createElement('div', {
            style: { marginBottom: '12px' }
        },
            React.createElement('textarea', {
                value: fenInput,
                onChange: handleInputChange,
                placeholder: placeholder,
                style: {
                    width: '100%',
                    minHeight: '80px',
                    padding: '8px',
                    fontSize: '12px',
                    fontFamily: 'monospace',
                    border: `1px solid ${validationResult.valid ? '#ced4da' : '#dc3545'}`,
                    borderRadius: '4px',
                    resize: 'vertical'
                }
            })
        ),

        // Validation status
        React.createElement('div', {
            style: {
                marginBottom: '12px',
                fontSize: '12px',
                color: validationResult.valid ? '#28a745' : '#dc3545'
            }
        },
            React.createElement('span', null, 
                isValidating ? '🔄 Validating...' : 
                validationResult.valid ? '✅ Valid FEN' : 
                `❌ ${validationResult.error || 'Invalid FEN'}`
            )
        ),

        // Action buttons
        React.createElement('div', {
            style: {
                display: 'flex',
                gap: '8px',
                marginBottom: '12px'
            }
        },
            React.createElement('button', {
                onClick: loadFEN,
                disabled: isLoading || !fenInput.trim(),
                style: {
                    padding: '8px 16px',
                    fontSize: '12px',
                    backgroundColor: isLoading ? '#6c757d' : '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: isLoading || !fenInput.trim() ? 'not-allowed' : 'pointer',
                    opacity: isLoading || !fenInput.trim() ? 0.6 : 1
                }
            }, isLoading ? '🔄 Loading...' : '🚀 Load FEN'),
            React.createElement('button', {
                onClick: () => setFenInput(''),
                style: {
                    padding: '8px 16px',
                    fontSize: '12px',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                }
            }, '🗑️ Clear')
        ),

        // FEN Examples (collapsible)
        showExamples && React.createElement('div', {
            style: {
                borderTop: '1px solid #dee2e6',
                paddingTop: '12px'
            }
        },
            React.createElement('h5', {
                style: {
                    margin: '0 0 8px 0',
                    fontSize: '13px',
                    fontWeight: '600',
                    color: '#495057'
                }
            }, '📋 FEN Examples'),
            React.createElement('div', {
                style: {
                    fontSize: '11px',
                    color: '#6c757d'
                }
            },
                React.createElement('p', {
                    style: { marginBottom: '8px' }
                }, 'Click an example to load it into the input field:'),
                React.createElement('div', {
                    style: { display: 'flex', flexDirection: 'column', gap: '8px' }
                },
                    fenExamples.map((example, index) => 
                        React.createElement('div', {
                            key: index,
                            onClick: () => handleExampleSelect(example),
                            style: {
                                padding: '8px',
                                border: '1px solid #dee2e6',
                                borderRadius: '4px',
                                backgroundColor: '#ffffff',
                                cursor: 'pointer',
                                transition: 'background-color 0.2s'
                            },
                            onMouseEnter: (e) => e.target.style.backgroundColor = '#f8f9fa',
                            onMouseLeave: (e) => e.target.style.backgroundColor = '#ffffff'
                        },
                            React.createElement('div', {
                                style: {
                                    fontWeight: '600',
                                    color: '#495057',
                                    marginBottom: '4px'
                                }
                            }, example.name),
                            React.createElement('div', {
                                style: {
                                    fontSize: '10px',
                                    color: '#6c757d',
                                    marginBottom: '4px'
                                }
                            }, example.description),
                            React.createElement('div', {
                                style: {
                                    fontSize: '10px',
                                    fontFamily: 'monospace',
                                    color: '#007bff',
                                    wordBreak: 'break-all'
                                }
                            }, example.fen.substring(0, 50) + '...')
                        )
                    )
                )
            )
        )
    );
};

// Export for use in other components
window.FENInput = FENInput; 