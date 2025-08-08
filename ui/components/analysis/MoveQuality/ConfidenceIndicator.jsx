/**
 * ConfidenceIndicator Component
 * 
 * Displays the confidence level of the move quality analysis
 * with a visual progress bar and percentage.
 * 
 * Props:
 * - quality: The move quality object with confidence score
 * 
 * Version: 1.0.0 - Extracted from MoveQualityDisplay
 */

const ConfidenceIndicator = ({ quality }) => {
    if (!quality) {
        return null;
    }

    const confidenceScore = quality.confidence_score || 0;
    const confidencePercentage = Math.round(confidenceScore * 100);
    
    // Determine confidence color based on level
    const getConfidenceColor = (score) => {
        if (score > 0.7) return '#4CAF50'; // High confidence - green
        if (score > 0.4) return '#FF9800'; // Medium confidence - orange
        return '#F44336'; // Low confidence - red
    };

    const getConfidenceLabel = (score) => {
        if (score > 0.7) return 'High';
        if (score > 0.4) return 'Medium';
        return 'Low';
    };

    return (
        <div className="confidence-indicator" style={{ marginBottom: '16px' }}>
            <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '8px'
            }}>
                <span style={{ 
                    fontSize: '12px', 
                    color: '#333',
                    fontWeight: '500'
                }}>
                    Confidence
                </span>
                <span style={{ 
                    fontSize: '10px', 
                    color: getConfidenceColor(confidenceScore),
                    fontWeight: '600'
                }}>
                    {getConfidenceLabel(confidenceScore)}
                </span>
            </div>
            
            <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '8px'
            }}>
                <div style={{ 
                    flex: 1, 
                    height: '6px', 
                    backgroundColor: '#e0e0e0',
                    borderRadius: '3px',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        height: '100%',
                        width: `${confidencePercentage}%`,
                        backgroundColor: getConfidenceColor(confidenceScore),
                        transition: 'width 0.3s ease'
                    }} />
                </div>
                <span style={{ 
                    fontSize: '10px', 
                    color: '#666',
                    minWidth: '30px',
                    textAlign: 'right'
                }}>
                    {confidencePercentage}%
                </span>
            </div>
        </div>
    );
};

// Export to window for global access
window.ConfidenceIndicator = ConfidenceIndicator;

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConfidenceIndicator;
}
