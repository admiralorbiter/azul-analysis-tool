/**
 * Mathematical Optimization Component
 * 
 * This component provides a user interface for mathematical optimization
 * of Azul moves using linear programming techniques.
 */

import React, { useState, useEffect } from 'react';
import { callAPI } from '../utils/api.js';

class MathematicalOptimization extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: false,
            error: null,
            optimizationResults: null,
            selectedObjective: 'maximize_scoring',
            objectives: [
                { value: 'maximize_scoring', label: 'Maximize Scoring' },
                { value: 'minimize_penalty', label: 'Minimize Penalty' },
                { value: 'balance_scoring_penalty', label: 'Balance Scoring & Penalty' },
                { value: 'maximize_wall_completion', label: 'Maximize Wall Completion' },
                { value: 'optimize_resource_allocation', label: 'Optimize Resource Allocation' }
            ],
            optimizationTypes: [
                { value: 'optimize-moves', label: 'General Move Optimization' },
                { value: 'optimize-scoring', label: 'Scoring Optimization' },
                { value: 'optimize-resource-allocation', label: 'Resource Allocation' },
                { value: 'optimize-wall-completion', label: 'Wall Completion' }
            ],
            selectedOptimizationType: 'optimize-moves'
        };
    }

    async optimizeMoves() {
        const { fenString, currentPlayer } = this.props;
        const { selectedObjective, selectedOptimizationType } = this.state;

        if (!fenString) {
            this.setState({ error: 'No game state provided for optimization' });
            return;
        }

        this.setState({ loading: true, error: null, optimizationResults: null });

        try {
            const endpoint = `/api/v1/${selectedOptimizationType}`;
            const requestData = {
                fen_string: fenString,
                current_player: currentPlayer || 0,
                objective: selectedObjective
            };

            const response = await callAPI(endpoint, 'POST', requestData);

            if (response.success) {
                this.setState({
                    optimizationResults: response,
                    loading: false
                });
            } else {
                this.setState({
                    error: response.error || 'Optimization failed',
                    loading: false
                });
            }
        } catch (error) {
            console.error('Optimization error:', error);
            this.setState({
                error: `Optimization failed: ${error.message}`,
                loading: false
            });
        }
    }

    renderOptimizationResults() {
        const { optimizationResults } = this.state;

        if (!optimizationResults) return null;

        return (
            <div className="optimization-results">
                <h3>Optimization Results</h3>
                
                <div className="optimization-summary">
                    <div className="summary-item">
                        <strong>Objective Value:</strong> {optimizationResults.objective_value}
                    </div>
                    <div className="summary-item">
                        <strong>Solver Status:</strong> {optimizationResults.solver_status}
                    </div>
                    <div className="summary-item">
                        <strong>Confidence Score:</strong> {(optimizationResults.confidence_score * 100).toFixed(1)}%
                    </div>
                    <div className="summary-item">
                        <strong>Optimization Time:</strong> {optimizationResults.optimization_time.toFixed(3)}s
                    </div>
                </div>

                {optimizationResults.optimal_moves && optimizationResults.optimal_moves.length > 0 && (
                    <div className="optimal-moves">
                        <h4>Optimal Moves ({optimizationResults.optimal_moves.length})</h4>
                        <div className="moves-list">
                            {optimizationResults.optimal_moves.map((move, index) => (
                                <div key={index} className="move-item">
                                    <strong>{move.move_type.replace(/_/g, ' ').toUpperCase()}</strong>
                                    {move.factory_idx !== undefined && (
                                        <span> - Factory {move.factory_idx}</span>
                                    )}
                                    {move.pattern_line !== undefined && (
                                        <span> - Line {move.pattern_line}</span>
                                    )}
                                    {move.tile_type !== undefined && (
                                        <span> - Tile {move.tile_type}</span>
                                    )}
                                    {move.row !== undefined && move.col !== undefined && (
                                        <span> - Position ({move.row}, {move.col})</span>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {optimizationResults.recommendations && optimizationResults.recommendations.length > 0 && (
                    <div className="recommendations">
                        <h4>Strategic Recommendations</h4>
                        <ul>
                            {optimizationResults.recommendations.map((rec, index) => (
                                <li key={index}>{rec}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {optimizationResults.scoring_opportunities && (
                    <div className="scoring-opportunities">
                        <h4>Scoring Opportunities</h4>
                        <div className="opportunities-grid">
                            {optimizationResults.scoring_opportunities.row_completions && (
                                <div className="opportunity-section">
                                    <h5>Row Completions</h5>
                                    {optimizationResults.scoring_opportunities.row_completions.map((row, index) => (
                                        <div key={index} className="opportunity-item">
                                            Row {row.row}: {row.filled_positions}/5 filled
                                        </div>
                                    ))}
                                </div>
                            )}
                            {optimizationResults.scoring_opportunities.column_completions && (
                                <div className="opportunity-section">
                                    <h5>Column Completions</h5>
                                    {optimizationResults.scoring_opportunities.column_completions.map((col, index) => (
                                        <div key={index} className="opportunity-item">
                                            Column {col.column}: {col.filled_positions}/5 filled
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {optimizationResults.resource_analysis && (
                    <div className="resource-analysis">
                        <h4>Resource Analysis</h4>
                        <div className="resource-summary">
                            <div className="available-tiles">
                                <h5>Available Tiles</h5>
                                {Object.entries(optimizationResults.resource_analysis.available_tiles).map(([tileType, count]) => (
                                    <div key={tileType} className="tile-count">
                                        Tile {tileType}: {count}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {optimizationResults.wall_analysis && (
                    <div className="wall-analysis">
                        <h4>Wall Completion Analysis</h4>
                        {optimizationResults.wall_analysis.near_completions && (
                            <div className="near-completions">
                                <h5>Near Completions</h5>
                                {optimizationResults.wall_analysis.near_completions.map((completion, index) => (
                                    <div key={index} className="completion-item">
                                        {completion.type.toUpperCase()} {completion.index}: {completion.filled_positions}/5
                                        (Value: {completion.completion_value})
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        );
    }

    render() {
        const { loading, error, selectedObjective, selectedOptimizationType, objectives, optimizationTypes } = this.state;

        return (
            <div className="mathematical-optimization">
                <h2>Mathematical Optimization</h2>
                <p>Use linear programming to optimize your moves for maximum scoring potential.</p>

                <div className="optimization-controls">
                    <div className="control-group">
                        <label htmlFor="optimization-type">Optimization Type:</label>
                        <select
                            id="optimization-type"
                            value={selectedOptimizationType}
                            onChange={(e) => this.setState({ selectedOptimizationType: e.target.value })}
                        >
                            {optimizationTypes.map(type => (
                                <option key={type.value} value={type.value}>
                                    {type.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="control-group">
                        <label htmlFor="objective">Objective:</label>
                        <select
                            id="objective"
                            value={selectedObjective}
                            onChange={(e) => this.setState({ selectedObjective: e.target.value })}
                        >
                            {objectives.map(obj => (
                                <option key={obj.value} value={obj.value}>
                                    {obj.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <button
                        className="optimize-button"
                        onClick={() => this.optimizeMoves()}
                        disabled={loading}
                    >
                        {loading ? 'Optimizing...' : 'Run Optimization'}
                    </button>
                </div>

                {error && (
                    <div className="error-message">
                        <strong>Error:</strong> {error}
                    </div>
                )}

                {this.renderOptimizationResults()}
            </div>
        );
    }
}

export default MathematicalOptimization; 