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
    loading
}) {
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
                }, '🔄 Refresh')
            )
        )
    );
} 