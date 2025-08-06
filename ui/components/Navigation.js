// Navigation Component
// Navigation bar for switching between main interface, neural training, and game theory

function Navigation({ currentPage, onPageChange }) {
    return React.createElement('nav', { className: 'navigation bg-white shadow-md p-4 mb-4' },
        React.createElement('div', { className: 'flex justify-between items-center' },
            React.createElement('h1', { className: 'text-xl font-bold text-gray-800' }, 'Azul Solver & Analysis Toolkit'),
            React.createElement('div', { className: 'flex space-x-2 flex-wrap' },
                React.createElement('button', {
                    className: `px-3 py-2 rounded text-sm ${currentPage === 'main' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`,
                    onClick: () => onPageChange('main')
                }, 'Main Interface'),
                React.createElement('button', {
                    className: `px-3 py-2 rounded text-sm ${currentPage === 'performance-analytics' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'}`,
                    onClick: () => onPageChange('performance-analytics')
                }, '📈 Analytics'),
                React.createElement('button', {
                    className: `px-3 py-2 rounded text-sm ${currentPage === 'advanced-analysis' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700'}`,
                    onClick: () => onPageChange('advanced-analysis')
                }, '🔍 Advanced'),
                React.createElement('button', {
                    className: `px-3 py-2 rounded text-sm ${currentPage === 'tactical-training' ? 'bg-orange-600 text-white' : 'bg-gray-200 text-gray-700'}`,
                    onClick: () => onPageChange('tactical-training')
                }, '🎯 Training'),
                React.createElement('button', {
                    className: `px-3 py-2 rounded text-sm ${currentPage === 'game-theory' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700'}`,
                    onClick: () => onPageChange('game-theory')
                }, '🎯 Game Theory'),
                React.createElement('button', {
                    className: `px-3 py-2 rounded text-sm ${currentPage === 'neural' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700'}`,
                    onClick: () => onPageChange('neural')
                }, '🧠 Neural'),
                React.createElement('button', {
                    className: `px-3 py-2 rounded text-sm ${currentPage === 'dynamic-optimization' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'}`,
                    onClick: () => onPageChange('dynamic-optimization')
                }, '⚡ Dynamic'),
                React.createElement('button', {
                    className: `px-3 py-2 rounded text-sm ${currentPage === 'test-move-quality' ? 'bg-orange-600 text-white' : 'bg-gray-200 text-gray-700'}`,
                    onClick: () => onPageChange('test-move-quality')
                }, '🧪 Test')
            )
        )
    );
}

window.Navigation = Navigation; 