// Position Preview Component
// Displays a visual preview of a position without loading it into the main game

const PositionPreview = React.memo(function PositionPreview({
    position,
    onClose,
    onLoadPosition
}) {
    const [previewState, setPreviewState] = React.useState(null);
    const [isLoading, setIsLoading] = React.useState(true);

    // Generate preview state when component mounts
    React.useEffect(() => {
        try {
            const generatedState = position.generate();
            setPreviewState(generatedState);
            setIsLoading(false);
        } catch (error) {
            console.error('Failed to generate preview:', error);
            setIsLoading(false);
        }
    }, [position]);

    if (isLoading) {
        return React.createElement('div', {
            className: 'position-preview-overlay'
        },
            React.createElement('div', {
                className: 'position-preview-modal'
            },
                React.createElement('div', {
                    className: 'preview-loading'
                },
                    React.createElement('div', {
                        className: 'loading-spinner'
                    }),
                    React.createElement('p', null, 'Generating preview...')
                )
            )
        );
    }

    if (!previewState) {
        return React.createElement('div', {
            className: 'position-preview-overlay'
        },
            React.createElement('div', {
                className: 'position-preview-modal'
            },
                React.createElement('div', {
                    className: 'preview-error'
                },
                    React.createElement('h3', null, 'Preview Error'),
                    React.createElement('p', null, 'Failed to generate preview for this position.'),
                    React.createElement('button', {
                        className: 'btn-primary',
                        onClick: onClose
                    }, 'Close')
                )
            )
        );
    }

    // Helper function to render a single tile
    const renderTile = (color, key) => {
        return React.createElement('div', {
            key: key,
            className: `tile-preview tile-${color.toLowerCase()}`
        });
    };

    // Helper function to render pattern line
    const renderPatternLine = (tiles, lineIndex) => {
        const maxCapacity = lineIndex + 1;
        const filledSlots = tiles.length;
        const emptySlots = maxCapacity - filledSlots;
        
        return React.createElement('div', {
            key: lineIndex,
            className: 'pattern-line-preview'
        },
            // Filled tiles
            ...tiles.map((tile, index) => renderTile(tile, `filled-${lineIndex}-${index}`)),
            // Empty slots
            ...Array(emptySlots).fill(null).map((_, index) => 
                React.createElement('div', {
                    key: `empty-${lineIndex}-${index}`,
                    className: 'tile-slot-empty'
                })
            )
        );
    };

    // Helper function to render wall row
    const renderWallRow = (row, rowIndex) => {
        const wallColors = ['B', 'Y', 'R', 'K', 'W'];
        // Standard Azul wall pattern - each row has a different starting color
        const colorPattern = [rowIndex, (rowIndex + 1) % 5, (rowIndex + 2) % 5, (rowIndex + 3) % 5, (rowIndex + 4) % 5];
        
        return React.createElement('div', {
            key: rowIndex,
            className: 'wall-row-preview'
        },
            colorPattern.map((colorIndex, colIndex) => {
                const expectedColor = wallColors[colorIndex];
                const hasTile = row[colIndex] === expectedColor;
                
                return React.createElement('div', {
                    key: colIndex,
                    className: `wall-cell-preview ${hasTile ? 'has-tile' : 'empty'}`
                },
                    hasTile ? renderTile(expectedColor, `wall-${rowIndex}-${colIndex}`) : null
                );
            })
        );
    };

    return React.createElement('div', {
        className: 'position-preview-overlay'
    },
        React.createElement('div', {
            className: 'position-preview-modal'
        },
            // Header
            React.createElement('div', {
                className: 'preview-header'
            },
                React.createElement('h2', null, `Preview: ${position.name}`),
                React.createElement('button', {
                    className: 'btn-close',
                    onClick: onClose
                }, '×')
            ),
            
            // Position info
            React.createElement('div', {
                className: 'preview-info'
            },
                React.createElement('p', {
                    className: 'preview-description'
                }, position.description),
                React.createElement('div', {
                    className: 'preview-tags'
                },
                    ...position.tags.map(tag =>
                        React.createElement('span', {
                            key: tag,
                            className: 'preview-tag'
                        }, tag)
                    )
                )
            ),
            
            // Game state preview
            React.createElement('div', {
                className: 'preview-content'
            },
                // Factories section
                React.createElement('div', {
                    className: 'preview-section'
                },
                    React.createElement('h3', null, '🏢 Factories'),
                    React.createElement('div', {
                        className: 'factories-preview'
                    },
                        (previewState.factories || []).map((factory, index) =>
                            React.createElement('div', {
                                key: index,
                                className: 'factory-preview'
                            },
                                React.createElement('div', {
                                    className: 'factory-label'
                                }, `Factory ${index + 1}`),
                                React.createElement('div', {
                                    className: 'factory-tiles'
                                },
                                    factory.map((tile, tileIndex) => 
                                        renderTile(tile, `factory-${index}-${tileIndex}`)
                                    )
                                )
                            )
                        )
                    )
                ),
                
                // Center section
                React.createElement('div', {
                    className: 'preview-section'
                },
                    React.createElement('h3', null, '🎯 Center Pool'),
                    React.createElement('div', {
                        className: 'center-preview'
                    },
                        (previewState.center || []).map((tile, index) => 
                            renderTile(tile, `center-${index}`)
                        )
                    )
                ),
                
                // Players section
                React.createElement('div', {
                    className: 'preview-section'
                },
                    React.createElement('h3', null, '👥 Players'),
                    React.createElement('div', {
                        className: 'players-preview'
                    },
                        (previewState.players || []).map((player, playerIndex) =>
                            React.createElement('div', {
                                key: playerIndex,
                                className: 'player-preview'
                            },
                                React.createElement('h4', null, `Player ${playerIndex + 1}`),
                                
                                // Pattern lines
                                React.createElement('div', {
                                    className: 'pattern-lines-preview'
                                },
                                    React.createElement('h5', null, 'Pattern Lines:'),
                                    ...(player.pattern_lines || []).map((line, lineIndex) =>
                                        renderPatternLine(line, lineIndex)
                                    )
                                ),
                                
                                // Wall
                                React.createElement('div', {
                                    className: 'wall-preview'
                                },
                                    React.createElement('h5', null, 'Wall:'),
                                    ...(player.wall || []).map((row, rowIndex) =>
                                        renderWallRow(row, rowIndex)
                                    )
                                ),
                                
                                // Floor line
                                React.createElement('div', {
                                    className: 'floor-preview'
                                },
                                    React.createElement('h5', null, 'Floor Line:'),
                                    React.createElement('div', {
                                        className: 'floor-tiles'
                                    },
                                        (player.floor_line || []).map((tile, index) => 
                                            renderTile(tile, `floor-${playerIndex}-${index}`)
                                        )
                                    )
                                ),
                                
                                // Score
                                React.createElement('div', {
                                    className: 'score-preview'
                                },
                                    React.createElement('h5', null, `Score: ${player.score || 0}`)
                                )
                            )
                        )
                    )
                )
            ),
            
            // Action buttons
            React.createElement('div', {
                className: 'preview-actions'
            },
                React.createElement('button', {
                    className: 'btn-secondary',
                    onClick: onClose
                }, 'Close'),
                React.createElement('button', {
                    className: 'btn-primary',
                    onClick: () => {
                        onLoadPosition(position);
                        onClose();
                    }
                }, 'Load Position')
            )
        )
    );
});

window.PositionPreview = PositionPreview; 