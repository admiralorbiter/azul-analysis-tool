// Status Message Component
import React from 'react';

function StatusMessage({ type, message }) {
    const typeClasses = {
        success: 'status-success',
        error: 'status-error',
        warning: 'status-warning'
    };
    
    return (
        <div className={`text-center p-3 rounded-lg ${typeClasses[type] || 'text-gray-600'}`}>
            {message}
        </div>
    );
}

export default StatusMessage; 