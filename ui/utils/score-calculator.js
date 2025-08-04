// Score calculation utilities for Azul
// Provides detailed breakdown of scoring including wall completions and floor penalties

// Floor penalty scores (same as in the backend)
const FLOOR_SCORES = [-1, -1, -2, -2, -2, -3, -3];

// Endgame bonus scores
const ROW_BONUS = 2;
const COL_BONUS = 7;
const SET_BONUS = 10;

/**
 * Calculate floor penalty for a given number of floor tiles
 * @param {number} floorTileCount - Number of tiles in floor
 * @returns {number} Total penalty points
 */
function calculateFloorPenalty(floorTileCount) {
    let penalty = 0;
    for (let i = 0; i < Math.min(floorTileCount, FLOOR_SCORES.length); i++) {
        penalty += FLOOR_SCORES[i];
    }
    return penalty;
}

/**
 * Calculate wall score by analyzing the wall grid
 * @param {Array} wall - 5x5 wall grid where each cell is false (empty) or tile color string
 * @returns {number} Wall score points
 */
function calculateWallScore(wall) {
    if (!wall || !Array.isArray(wall) || wall.length !== 5) {
        return 0;
    }
    
    let score = 0;
    
    // Check each cell in the wall
    for (let row = 0; row < 5; row++) {
        for (let col = 0; col < 5; col++) {
            if (wall[row][col] && wall[row][col] !== false) {
                // This cell has a tile, calculate its score
                score += calculateTileScore(wall, row, col);
            }
        }
    }
    
    return score;
}

/**
 * Calculate score for a single tile at the given position
 * @param {Array} wall - 5x5 wall grid
 * @param {number} row - Row index
 * @param {number} col - Column index
 * @returns {number} Score for this tile
 */
function calculateTileScore(wall, row, col) {
    let score = 0;
    
    // Count connected tiles in each direction
    const above = countConnectedTiles(wall, row, col, -1, 0);  // Up
    const below = countConnectedTiles(wall, row, col, 1, 0);   // Down
    const left = countConnectedTiles(wall, row, col, 0, -1);   // Left
    const right = countConnectedTiles(wall, row, col, 0, 1);   // Right
    
    // Vertical line score
    if (above > 0 || below > 0) {
        score += (1 + above + below);
    }
    
    // Horizontal line score
    if (left > 0 || right > 0) {
        score += (1 + left + right);
    }
    
    // Isolated tile score (if not connected to any other tiles)
    if (above === 0 && below === 0 && left === 0 && right === 0) {
        score += 1;
    }
    
    return score;
}

/**
 * Count connected tiles in a specific direction
 * @param {Array} wall - 5x5 wall grid
 * @param {number} startRow - Starting row
 * @param {number} startCol - Starting column
 * @param {number} deltaRow - Row direction (-1, 0, 1)
 * @param {number} deltaCol - Column direction (-1, 0, 1)
 * @returns {number} Number of connected tiles
 */
function countConnectedTiles(wall, startRow, startCol, deltaRow, deltaCol) {
    let count = 0;
    let row = startRow + deltaRow;
    let col = startCol + deltaCol;
    
    while (row >= 0 && row < 5 && col >= 0 && col < 5) {
        if (wall[row][col] && wall[row][col] !== false) {
            count++;
        } else {
            break;
        }
        row += deltaRow;
        col += deltaCol;
    }
    
    return count;
}

/**
 * Calculate endgame bonuses for completed rows, columns, and sets
 * @param {Array} wall - 5x5 wall grid
 * @returns {Object} Bonus breakdown
 */
function calculateEndgameBonuses(wall) {
    if (!wall || !Array.isArray(wall) || wall.length !== 5) {
        return { rowBonus: 0, colBonus: 0, setBonus: 0, total: 0 };
    }
    
    // Count completed rows
    let completedRows = 0;
    for (let row = 0; row < 5; row++) {
        let rowComplete = true;
        for (let col = 0; col < 5; col++) {
            if (!wall[row][col] || wall[row][col] === false) {
                rowComplete = false;
                break;
            }
        }
        if (rowComplete) completedRows++;
    }
    
    // Count completed columns
    let completedCols = 0;
    for (let col = 0; col < 5; col++) {
        let colComplete = true;
        for (let row = 0; row < 5; row++) {
            if (!wall[row][col] || wall[row][col] === false) {
                colComplete = false;
                break;
            }
        }
        if (colComplete) completedCols++;
    }
    
    // Count completed sets (all 5 tiles of same color)
    let completedSets = 0;
    const tileColors = ['B', 'Y', 'R', 'K', 'W']; // Blue, Yellow, Red, Black, White
    
    for (let color of tileColors) {
        let colorCount = 0;
        for (let row = 0; row < 5; row++) {
            for (let col = 0; col < 5; col++) {
                if (wall[row][col] === color) {
                    colorCount++;
                }
            }
        }
        if (colorCount === 5) completedSets++;
    }
    
    const rowBonus = completedRows * ROW_BONUS;
    const colBonus = completedCols * COL_BONUS;
    const setBonus = completedSets * SET_BONUS;
    const total = rowBonus + colBonus + setBonus;
    
    return {
        rowBonus,
        colBonus,
        setBonus,
        total,
        completedRows,
        completedCols,
        completedSets
    };
}

/**
 * Calculate complete score breakdown for a player
 * @param {Object} player - Player data object
 * @returns {Object} Complete score breakdown
 */
function calculateScoreBreakdown(player) {
    if (!player) {
        return {
            total: 0,
            wallScore: 0,
            floorPenalty: 0,
            endgameBonus: 0,
            breakdown: {
                wallScore: 0,
                floorPenalty: 0,
                endgameBonus: 0,
                completedRows: 0,
                completedCols: 0,
                completedSets: 0
            }
        };
    }
    
    const total = player.score || 0;
    const floorTiles = (player.floor_line || player.floor || []).length;
    const floorPenalty = calculateFloorPenalty(floorTiles);
    const wallScore = calculateWallScore(player.wall || []);
    const endgameBonuses = calculateEndgameBonuses(player.wall || []);
    
    return {
        total,
        wallScore,
        floorPenalty,
        endgameBonus: endgameBonuses.total,
        breakdown: {
            wallScore,
            floorPenalty,
            endgameBonus: endgameBonuses.total,
            completedRows: endgameBonuses.completedRows,
            completedCols: endgameBonuses.completedCols,
            completedSets: endgameBonuses.completedSets
        }
    };
}

// Export functions for use in components
window.ScoreCalculator = {
    calculateFloorPenalty,
    calculateWallScore,
    calculateEndgameBonuses,
    calculateScoreBreakdown
}; 