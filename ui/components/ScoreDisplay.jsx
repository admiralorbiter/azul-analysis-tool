// Enhanced Score Display Component
// Shows detailed score breakdown including wall completions and floor penalties
// Now with collapsible functionality

function ScoreDisplay({ player, playerIndex, isActive = false }) {
    const headerClass = isActive ? 'text-blue-700 font-bold' : 'text-gray-700';
    
    // Calculate score breakdown using the score calculator utility
    const calculateScoreBreakdown = (player) => {
        if (!window.ScoreCalculator) {
            // Fallback if calculator is not available
            if (!player) return { total: 0, wallScore: 0, floorPenalty: 0, endgameBonus: 0 };
            
            const total = player.score || 0;
            const floorTiles = (player.floor_line || player.floor || []).length;
            const floorPenalty = calculateFloorPenalty(floorTiles);
            const wallScore = total - floorPenalty;
            
            return {
                total,
                wallScore,
                floorPenalty,
                endgameBonus: 0
            };
        }
        
        return window.ScoreCalculator.calculateScoreBreakdown(player);
    };
    
    const calculateFloorPenalty = (floorTileCount) => {
        const floorScores = [-1, -1, -2, -2, -2, -3, -3];
        let penalty = 0;
        for (let i = 0; i < Math.min(floorTileCount, floorScores.length); i++) {
            penalty += floorScores[i];
        }
        return penalty;
    };
    
    const breakdown = calculateScoreBreakdown(player);
    
    // State for collapsible functionality
    const [isExpanded, setIsExpanded] = React.useState(false);
    
    const toggleExpanded = () => {
        setIsExpanded(!isExpanded);
    };
    
    // Check if there are interesting details to show
    const hasDetails = breakdown.floorPenalty !== 0 || 
                      breakdown.endgameBonus > 0 || 
                      (breakdown.breakdown && (breakdown.breakdown.completedRows > 0 || breakdown.breakdown.completedCols > 0 || breakdown.breakdown.completedSets > 0));
    
    return React.createElement('div', {
        className: 'score-display bg-white rounded-lg p-3 border border-gray-200 shadow-sm'
    },
        // Main score display (always visible)
        React.createElement('div', {
            className: `flex justify-between items-center mb-2 ${headerClass}`
        },
            React.createElement('span', {
                className: 'text-lg font-semibold'
            }, `Player ${playerIndex + 1}`),
            React.createElement('div', {
                className: 'flex items-center space-x-2'
            },
                React.createElement('span', {
                    className: 'text-2xl font-bold'
                }, `Score: ${breakdown.total}`),
                hasDetails && React.createElement('button', {
                    className: `ml-2 transition-colors p-1 rounded hover:bg-gray-100 ${isExpanded ? 'text-gray-700' : 'text-blue-500 hover:text-blue-700'}`,
                    onClick: toggleExpanded,
                    title: isExpanded ? 'Hide details' : 'Show details'
                },
                    React.createElement('span', {
                        className: 'text-sm font-bold'
                    }, isExpanded ? '−' : '+')
                )
            )
        ),
        
        // Collapsible score breakdown
        isExpanded && React.createElement('div', {
            className: 'text-xs space-y-1 text-gray-600 border-t border-gray-200 pt-2'
        },
            // Wall score
            React.createElement('div', {
                className: 'flex justify-between items-center'
            },
                React.createElement('span', {
                    className: 'flex items-center'
                },
                    React.createElement('span', {
                        className: 'w-3 h-3 bg-blue-500 rounded mr-1'
                    }),
                    'Wall Score:'
                ),
                React.createElement('span', {
                    className: breakdown.wallScore >= 0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'
                }, `${breakdown.wallScore >= 0 ? '+' : ''}${breakdown.wallScore}`)
            ),
            
            // Floor penalty
            React.createElement('div', {
                className: 'flex justify-between items-center'
            },
                React.createElement('span', {
                    className: 'flex items-center'
                },
                    React.createElement('span', {
                        className: 'w-3 h-3 bg-red-500 rounded mr-1'
                    }),
                    'Floor Penalty:'
                ),
                React.createElement('span', {
                    className: 'text-red-600 font-medium'
                }, `${breakdown.floorPenalty}`)
            ),
            
            // Endgame bonus (if any)
            breakdown.endgameBonus > 0 && React.createElement('div', {
                className: 'flex justify-between items-center'
            },
                React.createElement('span', {
                    className: 'flex items-center'
                },
                    React.createElement('span', {
                        className: 'w-3 h-3 bg-yellow-500 rounded mr-1'
                    }),
                    'Endgame Bonus:'
                ),
                React.createElement('span', {
                    className: 'text-yellow-600 font-medium'
                }, `+${breakdown.endgameBonus}`)
            ),
            
            // Wall completions (if available)
            breakdown.breakdown && (breakdown.breakdown.completedRows > 0 || breakdown.breakdown.completedCols > 0 || breakdown.breakdown.completedSets > 0) && React.createElement('div', {
                className: 'mt-2 pt-2 border-t border-gray-200'
            },
                React.createElement('div', {
                    className: 'text-xs text-gray-500 mb-1'
                }, 'Wall Completions:'),
                breakdown.breakdown.completedRows > 0 && React.createElement('div', {
                    className: 'flex justify-between items-center text-xs'
                },
                    React.createElement('span', {}, 'Completed Rows:'),
                    React.createElement('span', {
                        className: 'text-blue-600 font-medium'
                    }, `${breakdown.breakdown.completedRows} (+${breakdown.breakdown.completedRows * 2})`)
                ),
                breakdown.breakdown.completedCols > 0 && React.createElement('div', {
                    className: 'flex justify-between items-center text-xs'
                },
                    React.createElement('span', {}, 'Completed Columns:'),
                    React.createElement('span', {
                        className: 'text-blue-600 font-medium'
                    }, `${breakdown.breakdown.completedCols} (+${breakdown.breakdown.completedCols * 7})`)
                ),
                breakdown.breakdown.completedSets > 0 && React.createElement('div', {
                    className: 'flex justify-between items-center text-xs'
                },
                    React.createElement('span', {}, 'Completed Sets:'),
                    React.createElement('span', {
                        className: 'text-blue-600 font-medium'
                    }, `${breakdown.breakdown.completedSets} (+${breakdown.breakdown.completedSets * 10})`)
                )
            ),
            
            // Floor tile count
            React.createElement('div', {
                className: 'flex justify-between items-center text-gray-500 mt-2 pt-2 border-t border-gray-200'
            },
                React.createElement('span', {}, 'Floor Tiles:'),
                React.createElement('span', {}, `${(player.floor_line || player.floor || []).length}/7`)
            )
        )
    );
}

// Attach to window for backward compatibility
window.ScoreDisplay = ScoreDisplay; 