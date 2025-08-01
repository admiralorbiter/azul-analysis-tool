// Context Menu Component
import React from 'react';

function ContextMenu({ visible, x, y, options, onAction, onClose }) {
    if (!visible) return null;

    return (
        <div 
            className="context-menu"
            style={{ 
                left: x, 
                top: y,
                position: 'fixed'
            }}
            onClick={(e) => e.stopPropagation()}
        >
            {options.map((option, index) => (
                <div
                    key={index}
                    className="context-menu-item"
                    onClick={() => onAction(option)}
                >
                    {option}
                </div>
            ))}
        </div>
    );
}

export default ContextMenu; 