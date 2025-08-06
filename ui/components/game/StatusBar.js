// StatusBar.js - Status bar component
const { useState } = React;

// Import components from window
const StatusMessage = window.StatusMessage;

window.StatusBar = function StatusBar({
    sessionStatus,
    statusMessage,
    currentPlayer,
    engineThinking,
    positionJustLoaded,
    userActive,
    autoRefreshEnabled,
    moveHistory,
    manualRefresh,
    loading,
    gameState
}) {
    // Determine which player has the first player marker
    const getFirstPlayerInfo = () => {
        if (!gameState || !gameState.first_player_taken) {
            return null;
        }
        
        // Use the next_first_agent information from the game state
        const playerWithMarker = gameState.next_first_agent;
        if (playerWithMarker !== undefined && playerWithMarker !== -1) {
            return {
                playerId: playerWithMarker,
                hasMarker: true
            };
        }
        
        return null;
    };

    const firstPlayerInfo = getFirstPlayerInfo();

    return React.createElement('div', {
        className: 'mb-3'
    },
        React.createElement(StatusMessage, {
            type: sessionStatus === 'connected' ? 'success' : 'error',
            message: statusMessage
        }),
        React.createElement('div', {
            className: 'flex justify-between items-center p-2 bg-blue-50 rounded text-sm'
        },
            React.createElement('div', {
                className: 'flex items-center space-x-2'
            },
                React.createElement('span', {
                    className: 'font-medium'
                }, `Player: ${currentPlayer + 1}`),
                React.createElement('span', {
                    className: 'text-gray-500'
                }, '👤'),
                React.createElement('span', {
                    className: 'text-green-600 font-medium'
                }, 'Active'),
                firstPlayerInfo && React.createElement('div', {
                    className: 'flex items-center space-x-1 bg-yellow-100 border border-yellow-300 rounded px-2 py-1'
                },
                    React.createElement('span', {
                        className: 'text-yellow-600'
                    }, '⭐'),
                    React.createElement('span', {
                        className: 'text-xs font-medium text-yellow-800'
                    }, `P${firstPlayerInfo.playerId + 1} has marker`)
                ),
                engineThinking && React.createElement('span', {
                    className: 'text-blue-600'
                }, '🤖 Thinking...'),
                positionJustLoaded && React.createElement('span', {
                    className: 'text-green-600 font-medium'
                }, '📚 Position Loaded'),
                userActive && React.createElement('span', {
                    className: 'text-orange-600'
                }, '👤 Active'),
                !autoRefreshEnabled && React.createElement('span', {
                    className: 'text-red-600'
                }, '⏸️ Auto-Refresh Off')
            ),
            React.createElement('div', {
                className: 'flex items-center space-x-2'
            },
                React.createElement('span', {
                    className: 'text-gray-600'
                }, `Moves: ${moveHistory.length}`),
                React.createElement('button', {
                    className: 'btn-secondary btn-xs',
                    onClick: manualRefresh,
                    disabled: loading
                }, '🔄 Refresh'),
                gameState && gameState.fen_string && React.createElement('span', {
                    className: 'text-xs text-blue-600 font-mono',
                    title: 'Current FEN string',
                    style: { maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis' }
                }, `FEN: ${gameState.fen_string.substring(0, 20)}...`)
            )
        )
    );
} 