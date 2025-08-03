/**
 * Floor Line Pattern Analysis Component
 * 
 * Provides comprehensive analysis of floor line management patterns including:
 * - Risk mitigation opportunities
 * - Timing optimization patterns
 * - Trade-off analysis
 * - Endgame management
 * - Blocking opportunities
 * - Efficiency patterns
 */

import React, { useState, useEffect } from 'react';
import { callApi } from '../utils/api.js';

const FloorLinePatternAnalysis = ({ fenString, currentPlayer = 0, onAnalysisComplete }) => {
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [showDetails, setShowDetails] = useState({});

    // Analysis categories
    const categories = {
        all: 'All Patterns',
        risk_mitigation: 'Risk Mitigation',
        timing_optimization: 'Timing Optimization',
        trade_offs: 'Trade-offs',
        endgame_management: 'Endgame Management',
        blocking: 'Blocking Opportunities',
        efficiency: 'Efficiency Patterns'
    };

    // Urgency level colors
    const urgencyColors = {
        'CRITICAL': '#dc3545',
        'HIGH': '#fd7e14',
        'MEDIUM': '#ffc107',
        'LOW': '#28a745'
    };

    // Risk assessment colors
    const riskColors = {
        'critical': '#dc3545',
        'high': '#fd7e14',
        'medium': '#ffc107',
        'low': '#28a745'
    };

    useEffect(() => {
        if (fenString) {
            analyzeFloorLinePatterns();
        }
    }, [fenString, currentPlayer]);

    const analyzeFloorLinePatterns = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await callApi('/detect-floor-line-patterns', {
                method: 'POST',
                body: JSON.stringify({
                    fen_string: fenString,
                    current_player: currentPlayer,
                    include_risk_mitigation: true,
                    include_timing_optimization: true,
                    include_trade_offs: true,
                    include_endgame_management: true,
                    include_blocking_opportunities: true,
                    include_efficiency_opportunities: true,
                    include_move_suggestions: true,
                    urgency_threshold: 0.7
                })
            });

            if (response.ok) {
                const data = await response.json();
                setAnalysis(data);
                if (onAnalysisComplete) {
                    onAnalysisComplete(data);
                }
            } else {
                const errorData = await response.json();
                setError(errorData.error || 'Failed to analyze floor line patterns');
            }
        } catch (err) {
            setError('Network error: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const getOpportunitiesByCategory = () => {
        if (!analysis) return [];

        const categoryMap = {
            risk_mitigation: analysis.risk_mitigation_opportunities || [],
            timing_optimization: analysis.timing_optimization_opportunities || [],
            trade_offs: analysis.trade_off_opportunities || [],
            endgame_management: analysis.endgame_management_opportunities || [],
            blocking: analysis.blocking_opportunities || [],
            efficiency: analysis.efficiency_opportunities || []
        };

        if (selectedCategory === 'all') {
            return Object.values(categoryMap).flat();
        }

        return categoryMap[selectedCategory] || [];
    };

    const toggleDetails = (index) => {
        setShowDetails(prev => ({
            ...prev,
            [index]: !prev[index]
        }));
    };

    const formatOpportunity = (opp, index) => {
        const urgencyColor = urgencyColors[opp.urgency_level] || '#6c757d';
        const riskColor = riskColors[opp.risk_assessment] || '#6c757d';

        return (
            <div key={index} className="opportunity-card">
                <div className="opportunity-header" onClick={() => toggleDetails(index)}>
                    <div className="opportunity-type">
                        <span className="type-badge">{opp.opportunity_type.replace('_', ' ').toUpperCase()}</span>
                    </div>
                    <div className="opportunity-metrics">
                        <span className="urgency-badge" style={{ backgroundColor: urgencyColor }}>
                            {opp.urgency_level}
                        </span>
                        <span className="risk-badge" style={{ backgroundColor: riskColor }}>
                            {opp.risk_assessment}
                        </span>
                        {opp.current_floor_tiles > 0 && (
                            <span className="floor-tiles-badge">
                                {opp.current_floor_tiles} floor tiles
                            </span>
                        )}
                    </div>
                    <div className="opportunity-arrow">
                        {showDetails[index] ? '▼' : '▶'}
                    </div>
                </div>

                <div className="opportunity-description">
                    {opp.description}
                </div>

                {showDetails[index] && (
                    <div className="opportunity-details">
                        {opp.target_position && (
                            <div className="detail-item">
                                <strong>Target Position:</strong> Row {opp.target_position[0]}, Col {opp.target_position[1]}
                            </div>
                        )}
                        {opp.target_color_name && (
                            <div className="detail-item">
                                <strong>Target Color:</strong> {opp.target_color_name}
                            </div>
                        )}
                        <div className="detail-item">
                            <strong>Current Floor Tiles:</strong> {opp.current_floor_tiles}
                        </div>
                        <div className="detail-item">
                            <strong>Potential Penalty:</strong> {opp.potential_penalty} points
                        </div>
                        <div className="detail-item">
                            <strong>Penalty Reduction:</strong> {opp.penalty_reduction} points
                        </div>
                        <div className="detail-item">
                            <strong>Urgency Score:</strong> {opp.urgency_score.toFixed(1)}/10
                        </div>
                        <div className="detail-item">
                            <strong>Strategic Value:</strong> {opp.strategic_value.toFixed(1)}
                        </div>
                        {opp.move_suggestions && opp.move_suggestions.length > 0 && (
                            <div className="move-suggestions">
                                <strong>Move Suggestions:</strong>
                                <ul>
                                    {opp.move_suggestions.map((move, moveIndex) => (
                                        <li key={moveIndex} className={`move-suggestion priority-${move.priority}`}>
                                            <span className="move-type">{move.type.replace('_', ' ')}</span>
                                            {move.color && (
                                                <span className="move-color">{move.color}</span>
                                            )}
                                            <span className="move-description">{move.description}</span>
                                            <span className="move-priority">{move.priority}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>
        );
    };

    if (loading) {
        return (
            <div className="floor-line-analysis">
                <div className="analysis-header">
                    <h3>Floor Line Pattern Analysis</h3>
                    <div className="loading-spinner">Analyzing floor line patterns...</div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="floor-line-analysis">
                <div className="analysis-header">
                    <h3>Floor Line Pattern Analysis</h3>
                    <div className="error-message">
                        Error: {error}
                        <button onClick={analyzeFloorLinePatterns} className="retry-button">
                            Retry Analysis
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (!analysis) {
        return (
            <div className="floor-line-analysis">
                <div className="analysis-header">
                    <h3>Floor Line Pattern Analysis</h3>
                    <div className="no-analysis">No analysis available</div>
                </div>
            </div>
        );
    }

    const opportunities = getOpportunitiesByCategory();

    return (
        <div className="floor-line-analysis">
            <div className="analysis-header">
                <h3>Floor Line Pattern Analysis</h3>
                <div className="analysis-summary">
                    <span className="summary-item">
                        <strong>Total Opportunities:</strong> {analysis.total_opportunities}
                    </span>
                    <span className="summary-item">
                        <strong>Total Penalty Risk:</strong> {analysis.total_penalty_risk} points
                    </span>
                    <span className="summary-item">
                        <strong>Confidence:</strong> {(analysis.confidence_score * 100).toFixed(1)}%
                    </span>
                </div>
            </div>

            <div className="category-filter">
                <label htmlFor="category-select">Filter by Category:</label>
                <select
                    id="category-select"
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                >
                    {Object.entries(categories).map(([key, label]) => (
                        <option key={key} value={key}>{label}</option>
                    ))}
                </select>
            </div>

            {opportunities.length === 0 ? (
                <div className="no-opportunities">
                    No {selectedCategory === 'all' ? '' : categories[selectedCategory].toLowerCase()} opportunities detected.
                </div>
            ) : (
                <div className="opportunities-list">
                    {opportunities.map((opp, index) => formatOpportunity(opp, index))}
                </div>
            )}

            {analysis.move_suggestions && analysis.move_suggestions.length > 0 && (
                <div className="move-suggestions-summary">
                    <h4>All Move Suggestions</h4>
                    <div className="suggestions-grid">
                        {analysis.move_suggestions.map((suggestion, index) => (
                            <div key={index} className="suggestion-item">
                                <span className="suggestion-type">{suggestion.type}</span>
                                <span className="suggestion-description">{suggestion.description}</span>
                                <span className={`suggestion-priority priority-${suggestion.priority}`}>
                                    {suggestion.priority}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default FloorLinePatternAnalysis; 