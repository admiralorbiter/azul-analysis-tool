// positionUtils.js - Utility functions for position export/import
const { getGameState = () => Promise.resolve() } = window.gameAPI || {};

window.positionUtils = {
    exportPosition: function exportPosition(gameState, moveHistory, currentPlayer) {
        if (!gameState) return;
        
        const exportData = {
            fen: gameState.fen_string || 'initial',
            moveHistory: moveHistory,
            currentPlayer: currentPlayer,
            timestamp: Date.now(),
            description: `Azul position - ${moveHistory.length} moves`,
            metadata: {
                scores: gameState.players?.map(p => p.score) || [],
                gameMode: 'sandbox'
            }
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `azul_position_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        return 'Position exported successfully';
    },

    importPosition: function importPosition(file, setGameState, setMoveHistory, setCurrentPlayer, setStatusMessage) {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const data = JSON.parse(e.target.result);
                
                getGameState(data.fen).then(async newGameState => {
                    await setGameState(newGameState);
                    
                    if (data.moveHistory) {
                        setMoveHistory(data.moveHistory);
                    }
                    
                    if (data.currentPlayer !== undefined) {
                        setCurrentPlayer(data.currentPlayer);
                    }
                    
                    setStatusMessage(`Position imported: ${data.description || 'Unknown position'}`);
                }).catch(error => {
                    setStatusMessage(`Failed to load imported position: ${error.message}`);
                });
            } catch (error) {
                setStatusMessage(`Invalid position file: ${error.message}`);
            }
        };
        reader.readAsText(file);
    },

    handleFileImport: function handleFileImport(e, importPosition) {
        const file = e.target.files[0];
        if (file) {
            importPosition(file);
        }
        e.target.value = '';
    }
}; 