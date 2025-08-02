// AnalysisResults Component
// Displays engine analysis results in a dedicated panel

const AnalysisResults = ({ variations, loading, engineThinking }) => {
    if (!variations || variations.length === 0) {
        return React.createElement('div', {
            className: 'analysis-results-panel bg-gray-50 border border-gray-200 rounded-lg p-3'
        },
            React.createElement('h3', {
                className: 'text-base font-semibold text-gray-700 mb-1'
            }, '🔍 Engine Analysis'),
            React.createElement('div', {
                className: 'text-xs text-gray-500'
            }, 'No analysis results available. Click "Engine Analysis" to analyze the current position.')
        );
    }

    return React.createElement('div', {
        className: 'analysis-results-panel bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-3'
    },
        React.createElement('h3', {
            className: 'text-base font-semibold text-blue-800 mb-2 flex items-center'
        },
            React.createElement('span', null, '🔍 Engine Analysis'),
            engineThinking && React.createElement('span', {
                className: 'ml-2 text-xs text-blue-600 animate-pulse'
            }, '🤖 Thinking...')
        ),
        React.createElement('div', {
            className: 'space-y-1'
        },
            variations.map((variation, index) => 
                React.createElement('div', {
                    key: index,
                    className: 'bg-white rounded p-2 border border-blue-100 shadow-sm'
                },
                    React.createElement('div', {
                        className: 'flex justify-between items-center'
                    },
                        React.createElement('span', {
                            className: 'font-medium text-gray-800 text-sm'
                        }, `Move ${index + 1}: ${variation.move}`),
                        React.createElement('span', {
                            className: `font-bold text-base ${
                                variation.score > 0 ? 'text-green-600' : 
                                variation.score < 0 ? 'text-red-600' : 'text-gray-600'
                            }`
                        }, variation.score.toFixed(2))
                    ),
                    variation.visits && React.createElement('div', {
                        className: 'text-xs text-gray-500 mt-1'
                    }, `Visits: ${variation.visits.toLocaleString()}`)
                )
            )
        )
    );
};

// Make component globally available
window.AnalysisResults = AnalysisResults; 