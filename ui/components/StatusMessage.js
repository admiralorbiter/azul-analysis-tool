// StatusMessage Component
// Extracted from main.js

function StatusMessage({ type, message }) {
    const typeClasses = {
        success: 'status-success',
        error: 'status-error',
        warning: 'status-warning'
    };
    
    return React.createElement('div', {
        className: `text-center p-3 rounded-lg ${typeClasses[type] || 'text-gray-600'}`
    }, message);
}

// Export to window object for global access
window.StatusMessage = StatusMessage; 