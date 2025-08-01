// Move Option Component
import React from 'react';

function MoveOption({ move, score, visits, onClick, isSelected }) {
    return (
        <div 
            className={`move-option ${isSelected ? 'selected' : ''}`}
            onClick={onClick}
        >
            <div className="flex justify-between items-center">
                <span className="font-medium">{move}</span>
                <span className="text-sm">{score?.toFixed(2) || 'N/A'}</span>
            </div>
            {visits && <div className="text-xs text-gray-500">Visits: {visits}</div>}
        </div>
    );
}

export default MoveOption; 