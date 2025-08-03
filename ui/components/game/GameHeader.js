// GameHeader.js - Header component with game controls
const { useState } = React;

// Import components from window
const StatusMessage = window.StatusMessage;

window.GameHeader = function GameHeader({
    editMode,
    gameState,
    handleEditModeToggle,
    showPositionLibrary,
    setShowPositionLibrary,
    exportPosition,
    handleFileImport,
    saveGameState,
    setStatusMessage
}) {
    return React.createElement('header', {
        className: 'bg-white shadow-sm border-b'
    },
        React.createElement('div', {
            className: 'max-w-8xl mx-auto px-6 py-4'
        },
            React.createElement('div', {
                className: 'flex justify-between items-center'
            },
                React.createElement('h1', {
                    className: 'text-2xl font-bold text-gray-900'
                }, 'Azul Solver & Analysis Toolkit'),
                React.createElement('div', {
                    className: 'flex space-x-4 xl:space-x-6'
                },
                    React.createElement('button', {
                        className: `btn-edit ${editMode ? 'active' : ''}`,
                        onClick: handleEditModeToggle
                    }, editMode ? '✏️ Exit Edit' : '✏️ Edit Mode'),
                    React.createElement('button', {
                        className: 'btn-info',
                        onClick: () => setShowPositionLibrary(true)
                    }, '📚 Position Library'),
                    React.createElement('button', {
                        className: 'btn-success',
                        onClick: () => {
                            if (gameState) {
                                saveGameState(gameState, 'saved').then(() => {
                                    setStatusMessage('✅ Board position saved successfully');
                                }).catch(error => {
                                    setStatusMessage(`❌ Failed to save: ${error.message}`);
                                });
                            } else {
                                setStatusMessage('❌ No game state to save');
                            }
                        },
                        disabled: !gameState
                    }, '💾 Save Position'),
                    React.createElement('div', {
                        className: 'btn-group'
                    },
                        React.createElement('button', {
                            className: 'btn-info btn-sm',
                            onClick: exportPosition,
                            disabled: !gameState
                        }, '💾 Export'),
                        React.createElement('label', {
                            className: 'btn-info btn-sm cursor-pointer',
                            htmlFor: 'position-import'
                        }, '📁 Import'),
                        React.createElement('input', {
                            id: 'position-import',
                            type: 'file',
                            accept: '.json',
                            onChange: handleFileImport,
                            style: { display: 'none' }
                        })
                    )
                )
            )
        )
    );
} 