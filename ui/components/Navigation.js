// Navigation Component
// Navigation bar for switching between main interface and neural training

function Navigation({ currentPage, onPageChange }) {
    return React.createElement('nav', { className: 'navigation bg-white shadow-md p-4 mb-4' },
        React.createElement('div', { className: 'flex justify-between items-center' },
            React.createElement('h1', { className: 'text-xl font-bold text-gray-800' }, 'Azul Solver & Analysis Toolkit'),
            React.createElement('div', { className: 'flex space-x-4' },
                React.createElement('button', {
                    className: `px-4 py-2 rounded ${currentPage === 'main' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`,
                    onClick: () => onPageChange('main')
                }, 'Main Interface'),
                React.createElement('button', {
                    className: `px-4 py-2 rounded ${currentPage === 'neural' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700'}`,
                    onClick: () => onPageChange('neural')
                }, '🧠 Neural Training')
            )
        )
    );
}

// Export for global access
window.Navigation = Navigation; 