/**
 * Test Component for MoveQualityDisplay - Slice 3 Phase 1
 * 
 * This component tests the MoveQualityDisplay with mock data to verify
 * all features are working correctly.
 */

import React, { useState } from 'react';
import MoveQualityDisplay from './MoveQualityDisplay';

const TestMoveQualityDisplay = () => {
    const [testCase, setTestCase] = useState('brilliant');
    
    // Mock game state
    const mockGameState = {
        fen_string: 'test_position_1',
        current_player: 0
    };
    
    // Mock analysis data for different test cases
    const mockAnalysisData = {
        brilliant: {
            success: true,
            best_move: {
                quality_tier: '!!',
                quality_score: 95.5,
                blocking_score: 90.0,
                strategic_score: 95.0,
                floor_line_score: 85.0,
                scoring_score: 95.0,
                primary_reason: 'This is a brilliant move that achieves multiple high-value objectives simultaneously. It blocks opponents effectively while creating excellent scoring opportunities and maintaining strong strategic positioning.',
                confidence_score: 0.92
            },
            alternatives: []
        },
        excellent: {
            success: true,
            best_move: {
                quality_tier: '!',
                quality_score: 82.3,
                blocking_score: 85.0,
                strategic_score: 80.0,
                floor_line_score: 75.0,
                scoring_score: 85.0,
                primary_reason: 'This is an excellent move that achieves primary strategic objectives with clear benefits. It provides good blocking value and creates solid scoring opportunities.',
                confidence_score: 0.85
            },
            alternatives: []
        },
        good: {
            success: true,
            best_move: {
                quality_tier: '=',
                quality_score: 65.8,
                blocking_score: 70.0,
                strategic_score: 65.0,
                floor_line_score: 60.0,
                scoring_score: 70.0,
                primary_reason: 'This is a solid move that doesn\'t harm your position and achieves basic objectives. It provides reasonable tactical value without significant risks.',
                confidence_score: 0.75
            },
            alternatives: []
        },
        dubious: {
            success: true,
            best_move: {
                quality_tier: '?!',
                quality_score: 35.2,
                blocking_score: 40.0,
                strategic_score: 35.0,
                floor_line_score: 30.0,
                scoring_score: 40.0,
                primary_reason: 'This move has some benefit but carries significant downsides or risks. It may create tactical opportunities but at the cost of strategic positioning.',
                confidence_score: 0.65
            },
            alternatives: []
        },
        poor: {
            success: true,
            best_move: {
                quality_tier: '?',
                quality_score: 15.7,
                blocking_score: 20.0,
                strategic_score: 15.0,
                floor_line_score: 10.0,
                scoring_score: 20.0,
                primary_reason: 'This move has clear negative impact and should generally be avoided. It provides minimal benefits while creating significant positional weaknesses.',
                confidence_score: 0.45
            },
            alternatives: []
        },
        error: {
            success: false,
            error: 'Mock error for testing error handling'
        },
        loading: null // Will trigger loading state
    };
    
    // Mock the fetch function to return our test data
    const originalFetch = window.fetch;
    
    React.useEffect(() => {
        window.fetch = async (url, options) => {
            if (url === '/api/v1/analyze-move-quality') {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                if (testCase === 'loading') {
                    // Simulate loading state
                    return new Promise(() => {}); // Never resolves
                }
                
                return {
                    ok: mockAnalysisData[testCase]?.success !== false,
                    json: async () => mockAnalysisData[testCase] || mockAnalysisData.brilliant
                };
            }
            return originalFetch(url, options);
        };
        
        return () => {
            window.fetch = originalFetch;
        };
    }, [testCase]);
    
    const testCases = [
        { key: 'brilliant', label: 'Brilliant Move (95.5)' },
        { key: 'excellent', label: 'Excellent Move (82.3)' },
        { key: 'good', label: 'Good Move (65.8)' },
        { key: 'dubious', label: 'Dubious Move (35.2)' },
        { key: 'poor', label: 'Poor Move (15.7)' },
        { key: 'error', label: 'Error State' },
        { key: 'loading', label: 'Loading State' }
    ];
    
    return (
        <div style={{ 
            maxWidth: '600px', 
            margin: '20px auto', 
            padding: '20px',
            fontFamily: 'Arial, sans-serif'
        }}>
            <h1 style={{ 
                textAlign: 'center', 
                color: '#333',
                marginBottom: '20px'
            }}>
                Move Quality Display Test - Slice 3 Phase 1
            </h1>
            
            <div style={{ 
                marginBottom: '20px',
                padding: '16px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                border: '1px solid #e0e0e0'
            }}>
                <h3 style={{ margin: '0 0 12px 0', color: '#333' }}>
                    Test Cases
                </h3>
                <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                    gap: '8px'
                }}>
                    {testCases.map(({ key, label }) => (
                        <button
                            key={key}
                            onClick={() => setTestCase(key)}
                            style={{
                                padding: '8px 12px',
                                fontSize: '12px',
                                backgroundColor: testCase === key ? '#2196F3' : '#fff',
                                color: testCase === key ? '#fff' : '#333',
                                border: '1px solid #ddd',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease'
                            }}
                        >
                            {label}
                        </button>
                    ))}
                </div>
            </div>
            
            <div style={{ 
                marginBottom: '20px',
                padding: '12px',
                backgroundColor: '#e3f2fd',
                borderRadius: '6px',
                fontSize: '14px',
                color: '#0d47a1'
            }}>
                <strong>Current Test Case:</strong> {testCases.find(tc => tc.key === testCase)?.label}
            </div>
            
            <MoveQualityDisplay 
                gameState={mockGameState}
                currentPlayer={0}
                onMoveRecommendation={(data) => {
                    console.log('Move recommendation received:', data);
                }}
            />
            
            <div style={{ 
                marginTop: '20px',
                padding: '16px',
                backgroundColor: '#f5f5f5',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#666'
            }}>
                <h4 style={{ margin: '0 0 8px 0', color: '#333' }}>
                    Test Instructions
                </h4>
                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    <li>Click different test cases to see various quality tiers</li>
                    <li>Test the "Show Detailed Analysis" button</li>
                    <li>Verify responsive design on different screen sizes</li>
                    <li>Check that animations and hover effects work</li>
                    <li>Test error handling and loading states</li>
                </ul>
            </div>
        </div>
    );
};

export default TestMoveQualityDisplay; 