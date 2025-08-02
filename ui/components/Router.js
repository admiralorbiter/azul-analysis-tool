// Router Component
// Simple router for handling page navigation

function Router({ currentPage, onPageChange, children }) {
    return React.createElement('div', { className: 'router' }, children);
}

// Export for global access
window.Router = Router; 