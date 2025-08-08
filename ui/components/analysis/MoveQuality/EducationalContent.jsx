/**
 * EducationalContent Component
 * 
 * Displays educational content including strategic explanations,
 * learning tips, and best practices for the move quality analysis.
 * 
 * Props:
 * - quality: The move quality object
 * - config: The quality tier configuration with educational content
 * 
 * Version: 1.0.0 - Extracted from MoveQualityDisplay
 */

const { useState } = React;

const EducationalContent = ({ quality, config }) => {
    const [showEducational, setShowEducational] = useState(false);

    if (!quality || !config || !config.educational) {
        return null;
    }

    const { educational } = config;

    return (
        <div className="educational-content" style={{ marginBottom: '16px' }}>
            <button
                onClick={() => setShowEducational(!showEducational)}
                style={{
                    width: '100%',
                    padding: '8px 12px',
                    backgroundColor: '#f8f9fa',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    fontSize: '11px',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    color: '#495057',
                    fontWeight: '500'
                }}
            >
                <span>Learn About This Move</span>
                <span>{showEducational ? '▼' : '▶'}</span>
            </button>
            
            {showEducational && (
                <div style={{
                    marginTop: '8px',
                    padding: '12px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    fontSize: '11px',
                    lineHeight: '1.4',
                    color: '#495057'
                }}>
                    {/* Title */}
                    <div style={{
                        fontSize: '12px',
                        fontWeight: '600',
                        color: '#333',
                        marginBottom: '8px'
                    }}>
                        {educational.title}
                    </div>

                    {/* Explanation */}
                    <div style={{ marginBottom: '8px' }}>
                        <strong>Explanation:</strong> {educational.explanation}
                    </div>

                    {/* Strategic Reasoning */}
                    <div style={{ marginBottom: '8px' }}>
                        <strong>Strategic Reasoning:</strong> {educational.strategicReasoning}
                    </div>

                    {/* Learning Tips */}
                    <div style={{ marginBottom: '8px' }}>
                        <strong>Learning Tips:</strong>
                        <ul style={{ 
                            margin: '4px 0 0 0', 
                            paddingLeft: '16px',
                            marginBottom: '0'
                        }}>
                            {educational.learningTips.map((tip, index) => (
                                <li key={index} style={{ marginBottom: '2px' }}>
                                    {tip}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Best Practices */}
                    <div style={{
                        padding: '6px 8px',
                        backgroundColor: '#e3f2fd',
                        borderRadius: '3px',
                        borderLeft: '3px solid #2196F3',
                        fontSize: '10px',
                        color: '#1976d2'
                    }}>
                        <strong>Best Practice:</strong> {educational.bestPractices}
                    </div>
                </div>
            )}
        </div>
    );
};

// Export to window for global access
window.EducationalContent = EducationalContent;

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EducationalContent;
}
