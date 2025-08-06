/**
 * FEN Manager Component - UI Support for Standard FEN Format
 * 
 * Features:
 * - Display current FEN string
 * - Input new FEN strings
 * - Copy FEN to clipboard
 * - FEN validation and formatting
 * - Tabbed interface for different FEN operations
 * 
 * Version: 1.0.0 - Initial implementation for UI support
 */

const { useState, useEffect } = React;

const FENManager = ({ 
    gameState, 
    onFENLoad = null,
    className = ''
}) => {
    const [activeTab, setActiveTab] = useState('display'); // 'display' or 'input'
    const [showDetails, setShowDetails] = useState(false);

    // Tab configuration
    const tabs = [
        { id: 'display', label: '📋 Display FEN', icon: '📋' },
        { id: 'input', label: '📥 Load FEN', icon: '📥' }
    ];

    return React.createElement('div', {
        className: `fen-manager ${className}`,
        style: {
            backgroundColor: '#ffffff',
            border: '1px solid #dee2e6',
            borderRadius: '8px',
            overflow: 'hidden'
        }
    },
        // Tab navigation
        React.createElement('div', {
            style: {
                display: 'flex',
                borderBottom: '1px solid #dee2e6',
                backgroundColor: '#f8f9fa'
            }
        },
            tabs.map(tab => 
                React.createElement('button', {
                    key: tab.id,
                    onClick: () => setActiveTab(tab.id),
                    style: {
                        flex: 1,
                        padding: '12px 16px',
                        fontSize: '13px',
                        fontWeight: '500',
                        backgroundColor: activeTab === tab.id ? '#007bff' : 'transparent',
                        color: activeTab === tab.id ? 'white' : '#495057',
                        border: 'none',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                    }
                }, `${tab.icon} ${tab.label}`)
            )
        ),

        // Tab content
        React.createElement('div', {
            style: { padding: '16px' }
        },
            // Display tab
            activeTab === 'display' && React.createElement('div', null,
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
                    }, '🎯 Current FEN String'),
                    React.createElement('button', {
                        onClick: () => setShowDetails(!showDetails),
                        style: {
                            padding: '4px 8px',
                            fontSize: '12px',
                            backgroundColor: '#6c757d',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }
                    }, showDetails ? 'Hide Details' : 'Show Details')
                ),
                React.createElement(window.FENDisplay, {
                    gameState: gameState,
                    showDetails: showDetails
                })
            ),

            // Input tab
            activeTab === 'input' && React.createElement('div', null,
                React.createElement(window.FENInput, {
                    onFENLoad: onFENLoad
                })
            )
        )
    );
};

// Export for use in other components
window.FENManager = FENManager; 