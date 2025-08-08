/**
 * QualityScoreBreakdown Component
 * 
 * Displays the breakdown of move quality scores with progress bars
 * for different aspects like tactical value, strategic value, etc.
 * 
 * Props:
 * - quality: The move quality object with score breakdown
 * 
 * Version: 1.0.0 - Extracted from MoveQualityDisplay
 */

const ScoreBar = ({ label, score, color, icon }) => {
    const normalizedScore = Math.max(0, Math.min(100, score || 0));
    
    return (
        <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            fontSize: '11px'
        }}>
            <span style={{ fontSize: '12px' }}>{icon}</span>
            <span style={{ 
                minWidth: '80px', 
                color: '#333',
                fontWeight: '500'
            }}>
                {label}
            </span>
            <div style={{ 
                flex: 1, 
                height: '8px', 
                backgroundColor: '#e0e0e0',
                borderRadius: '4px',
                overflow: 'hidden'
            }}>
                <div style={{
                    height: '100%',
                    width: `${normalizedScore}%`,
                    backgroundColor: color,
                    transition: 'width 0.3s ease'
                }} />
            </div>
            <span style={{ 
                minWidth: '25px', 
                textAlign: 'right',
                color: '#666',
                fontSize: '10px'
            }}>
                {normalizedScore.toFixed(0)}
            </span>
        </div>
    );
};

const QualityScoreBreakdown = ({ quality }) => {
    if (!quality) {
        return (
            <div style={{ 
                padding: '12px', 
                backgroundColor: '#f8f9fa', 
                borderRadius: '8px',
                textAlign: 'center',
                color: '#6c757d'
            }}>
                No score breakdown available
            </div>
        );
    }

    const scoreComponents = [
        { 
            label: 'Scoring', 
            score: quality.scoring_score || 0, 
            color: '#2196F3',
            icon: '🎯'
        },
        { 
            label: 'Blocking', 
            score: quality.blocking_score || 0, 
            color: '#4CAF50',
            icon: '🛡️'
        },
        { 
            label: 'Patterns', 
            score: quality.pattern_score || 0, 
            color: '#9C27B0',
            icon: '🔍'
        },
        { 
            label: 'Floor Line', 
            score: quality.floor_line_score || 0, 
            color: '#FF9800',
            icon: '⚠️'
        }
    ];

    return (
        <div className="score-breakdown" style={{ marginBottom: '16px' }}>
            <h4 style={{ 
                margin: '0 0 12px 0', 
                fontSize: '14px', 
                color: '#333',
                fontWeight: '600'
            }}>
                Score Breakdown
            </h4>
            <div style={{ display: 'grid', gap: '12px' }}>
                {scoreComponents.map((component, index) => (
                    <ScoreBar 
                        key={index}
                        label={component.label}
                        score={component.score}
                        color={component.color}
                        icon={component.icon}
                    />
                ))}
            </div>
        </div>
    );
};

// Export to window for global access
window.QualityScoreBreakdown = QualityScoreBreakdown;
window.ScoreBar = ScoreBar;

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { QualityScoreBreakdown, ScoreBar };
}
