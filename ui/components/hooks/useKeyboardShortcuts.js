// useKeyboardShortcuts.js - Custom hook for keyboard event handling
const { useEffect } = React;

window.useKeyboardShortcuts = function useKeyboardShortcuts({
    editMode,
    clearSelection,
    handleEditModeToggle,
    handleUndo,
    handleRedo,
    applyTileColor,
    removeSelectedTiles,
    copySelection,
    pasteSelection
}) {
    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyPress = (e) => {
            if (e.key === 'Escape') {
                if (editMode) {
                    // In edit mode, clear selection
                    clearSelection();
                } else {
                    // In normal mode, clear selection
                    clearSelection();
                }
            } else if (e.key === 'e' && e.ctrlKey) {
                e.preventDefault();
                handleEditModeToggle();
            } else if (e.key === 'z' && e.ctrlKey && !editMode) {
                e.preventDefault();
                handleUndo();
            } else if (e.key === 'y' && e.ctrlKey && !editMode) {
                e.preventDefault();
                handleRedo();
            } else if (editMode) {
                if (['1', '2', '3', '4', '5'].includes(e.key)) {
                    e.preventDefault();
                    applyTileColor(e.key);
                } else if (e.key === 'Delete' || e.key === 'Backspace') {
                    e.preventDefault();
                    removeSelectedTiles();
                } else if (e.key === 'c' && e.ctrlKey) {
                    e.preventDefault();
                    copySelection();
                } else if (e.key === 'v' && e.ctrlKey) {
                    e.preventDefault();
                    pasteSelection();
                } else if (e.key === 'a' && e.ctrlKey) {
                    e.preventDefault();
                    // Select All not implemented yet
                    console.log('Select All not implemented yet');
                }
            }
        };
        
        document.addEventListener('keydown', handleKeyPress);
        return () => document.removeEventListener('keydown', handleKeyPress);
    }, [editMode, clearSelection, handleEditModeToggle, handleUndo, handleRedo, applyTileColor, removeSelectedTiles, copySelection, pasteSelection]);

    // Update body class for edit mode
    useEffect(() => {
        document.body.classList.toggle('edit-mode', editMode);
    }, [editMode]);
} 