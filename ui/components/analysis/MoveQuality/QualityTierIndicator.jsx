/**
 * QualityTierIndicator Component
 * 
 * Displays the quality tier (Brilliant, Excellent, Good, Dubious, Poor)
 * with visual styling and educational information.
 * 
 * Props:
 * - quality: The move quality object with tier and score
 * - config: The quality tier configuration object
 * 
 * Version: 1.0.0 - Extracted from MoveQualityDisplay
 */

console.log('Loading QualityTierIndicator component...');

const QualityTierIndicator = ({ quality, config }) => {
    if (!quality || !config) {
        return (
            <div style={{ 
                padding: '12px', 
                backgroundColor: '#f8f9fa', 
                borderRadius: '8px',
                textAlign: 'center',
                color: '#6c757d'
            }}>
                No quality data available
            </div>
        );
    }

    return (
        <div 
            className="quality-tier-indicator"
            style={{
                backgroundColor: config.bgColor,
                border: `2px solid ${config.borderColor}`,
                borderRadius: '8px',
                padding: '12px 16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '16px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
        >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '20px' }}>{config.icon}</span>
                <div>
                    <div style={{ 
                        fontWeight: 'bold', 
                        color: config.color,
                        fontSize: '16px',
                        lineHeight: '1.2'
                    }}>
                        {config.label}
                    </div>
                    <div style={{ 
                        fontSize: '12px', 
                        color: '#666',
                        marginTop: '2px'
                    }}>
                        {quality.quality_tier} Tier
                    </div>
                </div>
            </div>
            <div style={{ textAlign: 'right' }}>
                <div style={{ 
                    fontSize: '18px', 
                    fontWeight: 'bold',
                    color: config.color
                }}>
                    {quality.quality_score ? quality.quality_score.toFixed(1) : 'N/A'}
                </div>
                <div style={{ 
                    fontSize: '12px', 
                    color: '#666'
                }}>
                    / 100
                </div>
            </div>
        </div>
    );
};

// Export to window for global access
window.QualityTierIndicator = QualityTierIndicator;

console.log('QualityTierIndicator exported to window:', !!window.QualityTierIndicator);

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QualityTierIndicator;
}
