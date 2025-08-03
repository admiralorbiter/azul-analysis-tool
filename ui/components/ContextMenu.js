// ContextMenu Component
// Extracted from main.js

function ContextMenu({ visible, x, y, options, onAction, onClose }) {
    if (!visible) return null;
    
    return React.createElement('div', {
        className: 'context-menu',
        style: { 
            left: x, 
            top: y,
            position: 'fixed'
        },
        onClick: (e) => e.stopPropagation()
    },
        options.map((option, index) => 
            React.createElement('div', {
                key: index,
                className: 'context-menu-item',
                onClick: () => onAction(option)
            }, option)
        )
    );
}

window.ContextMenu = ContextMenu; 