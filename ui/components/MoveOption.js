// MoveOption Component
// Extracted from main.js

function MoveOption({ move, score, visits, onClick, isSelected }) {
    return React.createElement('div', {
        className: `move-option ${isSelected ? 'selected' : ''}`,
        onClick: onClick
    },
        React.createElement('div', {
            className: 'flex justify-between items-center'
        },
            React.createElement('span', {
                className: 'font-medium'
            }, move),
            React.createElement('span', {
                className: 'text-sm'
            }, score?.toFixed(2) || 'N/A')
        ),
        visits && React.createElement('div', {
            className: 'text-xs text-gray-500'
        }, `Visits: ${visits}`)
    );
}

// Export to window object for global access
window.MoveOption = MoveOption; 