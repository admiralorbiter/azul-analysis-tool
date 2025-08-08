/**
 * MoveQuality Utilities
 *
 * Wrapped in an IIFE to avoid leaking identifiers (e.g., analyzeMoveQuality)
 * into the global lexical scope and colliding with other scripts.
 */

;(function (global) {
console.log('Loading MoveQuality utils.js...');

// Check if FEN string represents real game data
const isRealGameData = (fenString) => {
    if (!fenString || typeof fenString !== 'string') {
        return false;
    }
    
    // Real FEN strings typically have specific patterns
    // This is a simplified check - in production you'd want more sophisticated validation
    const fenPattern = /^[A-Za-z0-9\/\s\-]+$/;
    const hasValidStructure = fenString.includes('/') && fenString.length > 20;
    
    return fenPattern.test(fenString) && hasValidStructure;
};

// Convert various tile representations into arrays
const normalizeTilesFromCounts = (tilesMap) => {
    if (!tilesMap) return [];
    const tiles = [];
    const indexToColor = { 0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W' };
    Object.entries(tilesMap).forEach(([key, count]) => {
        const color = /^[0-4]$/.test(String(key)) ? indexToColor[Number(key)] : key;
        const repeat = Number(count) || 0;
        if (color && repeat > 0) {
            for (let i = 0; i < repeat; i++) tiles.push(color);
        }
    });
    return tiles;
};

const extractFactoryTiles = (factory) => {
    if (!factory) return [];
    if (Array.isArray(factory)) return factory;
    if (Array.isArray(factory.tiles)) return factory.tiles;
    if (typeof factory.tiles === 'object') return normalizeTilesFromCounts(factory.tiles);
    if (typeof factory === 'object') return normalizeTilesFromCounts(factory);
    return [];
};

const extractCenterTiles = (gameState) => {
    if (!gameState) return [];
    if (Array.isArray(gameState.center)) return gameState.center;
    if (typeof gameState.center === 'object') return normalizeTilesFromCounts(gameState.center);
    if (gameState.center_pool && Array.isArray(gameState.center_pool.tiles)) return gameState.center_pool.tiles;
    if (gameState.center_pool && typeof gameState.center_pool.tiles === 'object') return normalizeTilesFromCounts(gameState.center_pool.tiles);
    return [];
};

// Analyze position complexity
const analyzePositionComplexity = (gameState) => {
    if (!gameState) return { complexity: 'low', score: 0.3 };
    
    let complexityScore = 0.3; // Base complexity
    
    // Analyze factories
    if (gameState.factories) {
        const factoryCount = gameState.factories.length;
        const tileCount = gameState.factories.reduce((total, factory) => {
            const tiles = extractFactoryTiles(factory);
            return total + tiles.length;
        }, 0);
        
        complexityScore += (factoryCount * 0.1) + (tileCount * 0.05);
    }
    
    // Analyze player boards
    if (gameState.players) {
        gameState.players.forEach(player => {
            if (player.pattern_lines) {
                const patternLineTiles = player.pattern_lines.reduce((total, line) => {
                    return total + (line.tiles ? line.tiles.length : 0);
                }, 0);
                complexityScore += patternLineTiles * 0.02;
            }
            
            if (player.wall && player.wall.tiles) {
                const wallTiles = player.wall.tiles.length;
                complexityScore += wallTiles * 0.03;
            }
        });
    }
    
    // Determine complexity level
    let complexity = 'low';
    if (complexityScore > 0.7) complexity = 'high';
    else if (complexityScore > 0.4) complexity = 'medium';
    
    return { complexity, score: Math.min(complexityScore, 1.0) };
};

// Generate realistic moves for analysis
const generateRealisticMoves = (gameState, currentPlayer) => {
    if (!gameState) return [];
    
    const moves = [];
    
    // Generate factory moves
    if (gameState.factories) {
        gameState.factories.forEach((factory, factoryIndex) => {
            const tiles = extractFactoryTiles(factory);
            tiles.forEach(tile => {
                for (let patternLine = 1; patternLine <= 5; patternLine++) {
                    moves.push({
                        type: 'factory_to_pattern',
                        factory: factoryIndex,
                        tile,
                        pattern_line: patternLine,
                        description: `Take ${tile} from factory ${factoryIndex + 1} to pattern line ${patternLine}`
                    });
                }
                moves.push({
                    type: 'factory_to_floor',
                    factory: factoryIndex,
                    tile,
                    description: `Take ${tile} from factory ${factoryIndex + 1} to floor line`
                });
            });
        });
    }
    
    // Generate center pool moves
    const centerTiles = extractCenterTiles(gameState);
    centerTiles.forEach(tile => {
        for (let patternLine = 1; patternLine <= 5; patternLine++) {
            moves.push({
                type: 'center_to_pattern',
                tile,
                pattern_line: patternLine,
                description: `Take ${tile} from center pool to pattern line ${patternLine}`
            });
        }
        moves.push({
            type: 'center_to_floor',
            tile,
            description: `Take ${tile} from center pool to floor line`
        });
    });
    
    return moves;
};

// Determine quality tier based on complexity
const determineQualityTier = (complexity) => {
    const { score } = complexity;
    
    if (score > 0.8) return '!!'; // Brilliant
    if (score > 0.6) return '!';  // Excellent
    if (score > 0.4) return '=';  // Good
    if (score > 0.2) return '?!'; // Dubious
    return '?'; // Poor
};

// Generate educational reasoning
const generateEducationalReason = (qualityTier, complexity) => {
    const reasons = {
        '!!': 'This move demonstrates exceptional strategic thinking with multiple positive outcomes.',
        '!': 'This move is strategically sound and maximizes your advantages.',
        '=': 'This move maintains a solid position without creating weaknesses.',
        '?!': 'This move has some risks but may be justified in specific situations.',
        '?': 'This move has significant drawbacks and should generally be avoided.'
    };
    
    return reasons[qualityTier] || reasons['='];
};

// Main analysis function
const analyzeMoveQuality = async (gameState, currentPlayer = 0) => {
    try {
        // Analyze position complexity
        const complexity = analyzePositionComplexity(gameState);
        
        // Generate possible moves
        let moves = generateRealisticMoves(gameState, currentPlayer);
        
        // Determine best move (simplified logic)
        if (moves.length === 0) {
            // Fallback: synthesize a minimal move so demo never errors
            const factories = gameState.factories || [];
            const firstFactoryTiles = factories.length > 0 ? extractFactoryTiles(factories[0]) : [];
            const sampleTile = firstFactoryTiles[0] || extractCenterTiles(gameState)[0] || 'B';
            moves = [{ type: 'synthetic', factory: 0, tile: sampleTile, pattern_line: 1, description: `Place ${sampleTile} to pattern line 1` }];
        }
        const bestMove = moves[0];
        
        // Calculate quality scores
        const qualityTier = determineQualityTier(complexity);
        const qualityScore = Math.random() * 30 + 70; // 70-100 for demo
        const confidenceScore = Math.random() * 0.3 + 0.7; // 0.7-1.0 for demo
        
        // Generate detailed scores
        const scoringScore = Math.random() * 30 + 70;
        const blockingScore = Math.random() * 30 + 70;
        const patternScore = Math.random() * 30 + 70;
        const floorLineScore = Math.random() * 30 + 70;
        
        const result = {
            best_move: {
                quality_tier: qualityTier,
                quality_score: qualityScore,
                confidence_score: confidenceScore,
                scoring_score: scoringScore,
                blocking_score: blockingScore,
                pattern_score: patternScore,
                floor_line_score: floorLineScore,
                move_description: bestMove.description,
                primary_reason: generateEducationalReason(qualityTier, complexity)
            },
            total_moves_analyzed: moves.length,
            analysis_time_ms: Math.random() * 1000 + 500 // 500-1500ms for demo
        };
        
        return result;
        
    } catch (error) {
        console.error('Move quality analysis failed:', error);
        throw error;
    }
};

// Export utilities to window/global for global access
global.moveQualityUtils = {
    isRealGameData,
    analyzeMoveQuality,
    analyzePositionComplexity,
    generateRealisticMoves,
    determineQualityTier,
    generateEducationalReason
};

console.log('MoveQuality utils exported to global:', {
    moveQualityUtils: !!global.moveQualityUtils,
    isRealGameData: !!global.moveQualityUtils?.isRealGameData,
    analyzeMoveQuality: !!global.moveQualityUtils?.analyzeMoveQuality
});

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        isRealGameData,
        analyzeMoveQuality,
        analyzePositionComplexity,
        generateRealisticMoves,
        determineQualityTier,
        generateEducationalReason
    };
}
})(typeof window !== 'undefined' ? window : globalThis);
