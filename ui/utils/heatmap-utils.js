// Heatmap utility functions for Azul Solver & Analysis Toolkit
// Extracted from main.js for modularity

// Generate heatmap data from analysis
function generateHeatmapData(analysisData) {
    if (!analysisData || !analysisData.variations) return null;
    
    const heatmap = {};
    const bestScore = analysisData.variations[0]?.score || 0;
    
    analysisData.variations.forEach(variation => {
        const scoreDelta = variation.score - bestScore;
        const normalizedScore = Math.max(-1, Math.min(1, scoreDelta / 10)); // Normalize to -1 to 1
        
        // Extract move information for heatmap positioning
        if (variation.move_data) {
            const key = `${variation.move_data.source_id}_${variation.move_data.tile_type}`;
            heatmap[key] = {
                score: variation.score,
                delta: scoreDelta,
                normalized: normalizedScore,
                color: getHeatmapColor(normalizedScore)
            };
        }
    });
    
    return heatmap;
}

// Get heatmap color based on score delta
function getHeatmapColor(normalizedScore) {
    // Red for bad moves (negative), green for good moves (positive)
    const intensity = Math.abs(normalizedScore);
    if (normalizedScore < 0) {
        return `rgba(239, 68, 68, ${intensity})`; // Red with alpha
    } else {
        return `rgba(34, 197, 94, ${intensity})`; // Green with alpha
    }
}

// Export heatmap utilities to global scope
window.heatmapUtils = {
    generateHeatmapData,
    getHeatmapColor
}; 