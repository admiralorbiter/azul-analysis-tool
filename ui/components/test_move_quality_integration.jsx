/**
 * Integration Test for MoveQualityDisplay - Slice 3 Phase 1
 * 
 * This component tests the MoveQualityDisplay with real API calls
 * to verify integration with the backend move quality assessment system.
 */

import React, { useState } from 'react';
import MoveQualityDisplay from './MoveQualityDisplay';

const TestMoveQualityIntegration = () => {
    const [testPosition, setTestPosition] = useState('initial');
    const [testResults, setTestResults] = useState([]);
    
    // Test positions with known characteristics
    const testPositions = [
        { 
            key: 'initial', 
            label: 'Initial Position',
            fen: 'initial',
            description: 'Starting position - should show balanced moves'
        },
        { 
            key: 'midgame', 
            label: 'Midgame Position',
            fen: 'midgame_test_1',
            description: 'Midgame position with tactical opportunities'
        },
        { 
            key: 'endgame', 
            label: 'Endgame Position',
            fen: 'endgame_test_1',
            description: 'Endgame position with strategic considerations'
        },
        { 
            key: 'complex', 
            label: 'Complex Position',
            fen: 'complex_test_1',
            description: 'Complex position with multiple viable options'
        }
    ];
    
    const runTest = async (position) => {
        const startTime = Date.now();
        const result = {
            position: position.label,
            timestamp: new Date().toISOString(),
            success: false,
            error: null,
            responseTime: 0,
            data: null
        };
        
        try {
            // Create mock game state for the test
            const mockGameState = {
                fen_string: position.fen,
                current_player: 0
            };
            
            // Test the API call directly
            const response = await fetch('/api/v1/analyze-move-quality', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fen_string: position.fen,
                    current_player: 0,
                    include_alternatives: true,
                    max_alternatives: 4
                })
            });
            
            result.responseTime = Date.now() - startTime;
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                result.success = true;
                result.data = data;
            } else {
                throw new Error(data.error || 'API returned success: false');
            }
            
        } catch (error) {
            result.error = error.message;
            console.error(`Test failed for ${position.label}:`, error);
        }
        
        setTestResults(prev => [result, ...prev.slice(0, 9)]); // Keep last 10 results
    };
    
    const runAllTests = async () => {
        setTestResults([]);
        for (const position of testPositions) {
            await runTest(position);
            // Small delay between tests
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    };
    
    const getTestStatus = (result) => {
        if (result.success) {
            return { 
                color: '#4CAF50', 
                text: '✅ Success',
                details: `Response time: ${result.responseTime}ms`
            };
        } else {
            return { 
                color: '#F44336', 
                text: '❌ Failed',
                details: result.error
            };
        }
    };
    
    return (
        <div style={{ 
            maxWidth: '800px', 
            margin: '20px auto', 
            padding: '20px',
            fontFamily: 'Arial, sans-serif'
        }}>
            <h1 style={{ 
                textAlign: 'center', 
                color: '#333',
                marginBottom: '20px'
            }}>
                Move Quality Display Integration Test - Slice 3 Phase 1
            </h1>
            
            <div style={{ 
                marginBottom: '20px',
                padding: '16px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                border: '1px solid #e0e0e0'
            }}>
                <h3 style={{ margin: '0 0 12px 0', color: '#333' }}>
                    Test Positions
                </h3>
                <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '12px'
                }}>
                    {testPositions.map((position) => (
                        <div key={position.key} style={{
                            padding: '12px',
                            backgroundColor: '#fff',
                            borderRadius: '6px',
                            border: '1px solid #e0e0e0'
                        }}>
                            <h4 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>
                                {position.label}
                            </h4>
                            <p style={{ 
                                margin: '0 0 8px 0', 
                                fontSize: '12px', 
                                color: '#666' 
                            }}>
                                {position.description}
                            </p>
                            <button
                                onClick={() => runTest(position)}
                                style={{
                                    padding: '6px 12px',
                                    fontSize: '11px',
                                    backgroundColor: '#2196F3',
                                    color: '#fff',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer'
                                }}
                            >
                                Test
                            </button>
                        </div>
                    ))}
                </div>
                
                <div style={{ marginTop: '16px', textAlign: 'center' }}>
                    <button
                        onClick={runAllTests}
                        style={{
                            padding: '10px 20px',
                            fontSize: '14px',
                            backgroundColor: '#4CAF50',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontWeight: 'bold'
                        }}
                    >
                        Run All Tests
                    </button>
                </div>
            </div>
            
            {/* Live Component Test */}
            <div style={{ 
                marginBottom: '20px',
                padding: '16px',
                backgroundColor: '#e3f2fd',
                borderRadius: '8px',
                border: '1px solid #2196F3'
            }}>
                <h3 style={{ margin: '0 0 12px 0', color: '#0d47a1' }}>
                    Live Component Test
                </h3>
                <div style={{ marginBottom: '12px' }}>
                    <label style={{ fontSize: '12px', color: '#666' }}>
                        Select Test Position:
                    </label>
                    <select
                        value={testPosition}
                        onChange={(e) => setTestPosition(e.target.value)}
                        style={{
                            marginLeft: '8px',
                            padding: '4px 8px',
                            fontSize: '12px',
                            borderRadius: '4px',
                            border: '1px solid #ddd'
                        }}
                    >
                        {testPositions.map(pos => (
                            <option key={pos.key} value={pos.key}>
                                {pos.label}
                            </option>
                        ))}
                    </select>
                </div>
                
                <MoveQualityDisplay 
                    gameState={{ fen_string: testPositions.find(p => p.key === testPosition)?.fen || 'initial' }}
                    currentPlayer={0}
                    onMoveRecommendation={(data) => {
                        console.log('Live component received:', data);
                    }}
                />
            </div>
            
            {/* Test Results */}
            <div style={{ 
                marginTop: '20px',
                padding: '16px',
                backgroundColor: '#f5f5f5',
                borderRadius: '8px'
            }}>
                <h3 style={{ margin: '0 0 12px 0', color: '#333' }}>
                    Test Results ({testResults.length} tests)
                </h3>
                
                {testResults.length === 0 ? (
                    <p style={{ color: '#666', fontSize: '12px' }}>
                        No tests run yet. Click "Run All Tests" or individual test buttons above.
                    </p>
                ) : (
                    <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                        {testResults.map((result, index) => {
                            const status = getTestStatus(result);
                            return (
                                <div key={index} style={{
                                    padding: '8px 12px',
                                    backgroundColor: '#fff',
                                    borderRadius: '4px',
                                    marginBottom: '8px',
                                    border: '1px solid #e0e0e0',
                                    fontSize: '12px'
                                }}>
                                    <div style={{ 
                                        display: 'flex', 
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        marginBottom: '4px'
                                    }}>
                                        <strong style={{ color: '#333' }}>
                                            {result.position}
                                        </strong>
                                        <span style={{ color: status.color, fontWeight: 'bold' }}>
                                            {status.text}
                                        </span>
                                    </div>
                                    <div style={{ color: '#666', fontSize: '11px' }}>
                                        {status.details}
                                    </div>
                                    {result.data && (
                                        <div style={{ 
                                            marginTop: '4px',
                                            fontSize: '11px',
                                            color: '#888'
                                        }}>
                                            Best move: {result.data.best_move?.quality_tier} 
                                            ({result.data.best_move?.quality_score?.toFixed(1)})
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
            
            {/* Test Summary */}
            {testResults.length > 0 && (
                <div style={{ 
                    marginTop: '16px',
                    padding: '12px',
                    backgroundColor: '#fff3cd',
                    borderRadius: '6px',
                    border: '1px solid #ffeaa7',
                    fontSize: '12px'
                }}>
                    <h4 style={{ margin: '0 0 8px 0', color: '#856404' }}>
                        Test Summary
                    </h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '8px' }}>
                        <div>
                            <strong>Total Tests:</strong> {testResults.length}
                        </div>
                        <div>
                            <strong>Successful:</strong> {testResults.filter(r => r.success).length}
                        </div>
                        <div>
                            <strong>Failed:</strong> {testResults.filter(r => !r.success).length}
                        </div>
                        <div>
                            <strong>Avg Response Time:</strong> {
                                testResults.length > 0 
                                    ? Math.round(testResults.reduce((sum, r) => sum + r.responseTime, 0) / testResults.length)
                                    : 0
                            }ms
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TestMoveQualityIntegration; 