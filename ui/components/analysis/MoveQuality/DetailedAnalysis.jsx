/**
 * DetailedAnalysis Component
 * 
 * Displays collapsible detailed analysis of the move quality
 * with primary reasoning and additional insights.
 * 
 * Props:
 * - quality: The move quality object with analysis details
 * - showDetails: Boolean to control visibility
 * - setShowDetails: Function to toggle visibility
 * 
 * Version: 1.0.0 - Extracted from MoveQualityDisplay
 */

const DetailedAnalysis = ({ quality, showDetails, setShowDetails }) => {
    if (!quality) {
        return null;
    }

    return (
        <div className="detailed-analysis" style={{ marginBottom: '12px' }}>
            <button
                onClick={() => setShowDetails(!showDetails)}
                style={{
                    width: '100%',
                    padding: '6px 8px',
                    backgroundColor: 'transparent',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '11px',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    color: '#666'
                }}
            >
                <span>Detailed Analysis</span>
                <span>{showDetails ? '▼' : '▶'}</span>
            </button>
            
            {showDetails && (
                <div style={{
                    marginTop: '8px',
                    padding: '8px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    fontSize: '11px',
                    lineHeight: '1.4',
                    color: '#555'
                }}>
                    {quality.primary_reason || 'No detailed analysis available.'}
                    
                    {/* Additional analysis details if available */}
                    {quality.secondary_reason && (
                        <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #e9ecef' }}>
                            <strong>Additional Insights:</strong> {quality.secondary_reason}
                        </div>
                    )}
                    
                    {quality.risk_assessment && (
                        <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #e9ecef' }}>
                            <strong>Risk Assessment:</strong> {quality.risk_assessment}
                        </div>
                    )}
                    
                    {quality.opportunity_value && (
                        <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #e9ecef' }}>
                            <strong>Opportunity Value:</strong> {quality.opportunity_value}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

// Export to window for global access
window.DetailedAnalysis = DetailedAnalysis;

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DetailedAnalysis;
}
