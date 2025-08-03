// Factory Component
// Factory component for displaying tiles in the Azul game

function Factory({ tiles, onTileClick, heatmap = null, factoryIndex, selectedTile = null, onTileSelection = null, editMode = false, onElementSelect = null, selectedElements = [], heatmapEnabled = false, heatmapData = null }) {
    const factoryRef = React.useRef(null);
    
    React.useEffect(() => {
        const factory = factoryRef.current;
        if (!factory) return;
        
        const handleDragOver = (e) => {
            e.preventDefault();
            e.currentTarget.classList.add('drag-over');
        };
        
        const handleDragLeave = (e) => {
            e.currentTarget.classList.remove('drag-over');
        };
        
        const handleDrop = (e) => {
            e.preventDefault();
            e.currentTarget.classList.remove('drag-over');
        };
        
        factory.addEventListener('dragover', handleDragOver);
        factory.addEventListener('dragleave', handleDragLeave);
        factory.addEventListener('drop', handleDrop);
        
        return () => {
            factory.removeEventListener('dragover', handleDragOver);
            factory.removeEventListener('dragleave', handleDragLeave);
            factory.removeEventListener('drop', handleDrop);
        };
    }, []);
    
    const handleFactoryClick = (e) => {
        if (editMode && onElementSelect) {
            const isCtrlClick = e.ctrlKey;
            onElementSelect({
                type: 'factory',
                data: { factoryIndex, tiles }
            }, isCtrlClick);
        }
    };
    
    const handleFactoryRightClick = (e) => {
        e.preventDefault();
        if (editMode && window.showContextMenu) {
            window.showContextMenu(e, 'factory', { factoryIndex, tiles });
        }
    };
    
    const isSelected = editMode && selectedElements.some(el => el.type === 'factory' && el.data.factoryIndex === factoryIndex);
    const isEditSelected = editMode && isSelected;
    
    // Get heatmap overlay style for this factory
    const getHeatmapOverlay = (tileType) => {
        if (!heatmapEnabled || !heatmapData) return {};
        
        const tileTypeMapping = { 'B': 0, 'Y': 1, 'R': 2, 'K': 3, 'W': 4 };
        const key = `${factoryIndex}_${tileTypeMapping[tileType] || 0}`;
        const heatmapInfo = heatmapData[key];
        
        if (heatmapInfo) {
            return {
                position: 'relative',
                '::after': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: heatmapInfo.color,
                    borderRadius: '4px',
                    pointerEvents: 'none'
                }
            };
        }
        return {};
    };
    
    return React.createElement('div', {
        ref: factoryRef,
        className: `factory ${isEditSelected ? 'selected' : ''} ${heatmapEnabled ? 'heatmap-enabled' : ''}`,
        onClick: handleFactoryClick,
        onContextMenu: handleFactoryRightClick,
        style: { position: 'relative' }
    },
        // Factory label
        React.createElement('div', {
            className: 'text-xs text-gray-600 mb-1 text-center font-medium'
        }, `Factory ${factoryIndex + 1}`),
        React.createElement('div', {
            className: 'flex flex-wrap gap-1'
        },
            tiles.map((tile, index) => {
                const heatmapKey = `${factoryIndex}_${tile === 'B' ? 0 : tile === 'Y' ? 1 : tile === 'R' ? 2 : tile === 'K' ? 3 : 4}`;
                const heatmapInfo = heatmapEnabled && heatmapData ? heatmapData[heatmapKey] : null;
                
                return React.createElement('div', {
                    key: index,
                    style: { position: 'relative' }
                },
                    React.createElement(Tile, {
                        color: tile,
                        onClick: () => onTileClick ? onTileClick(factoryIndex, index, tile) : null,
                        draggable: true,
                        onDragStart: (e) => {
                            e.dataTransfer.setData('application/json', JSON.stringify({
                                sourceType: 'factory',
                                sourceId: factoryIndex,
                                tileIndex: index,
                                tile: tile
                            }));
                        },
                        isSelected: selectedTile && selectedTile.sourceId === factoryIndex && selectedTile.tileIndex === index
                    }),
                    // Heatmap overlay
                    heatmapInfo && React.createElement('div', {
                        className: 'heatmap-overlay',
                        style: {
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            backgroundColor: heatmapInfo.color,
                            borderRadius: '4px',
                            pointerEvents: 'none',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '10px',
                            color: 'white',
                            fontWeight: 'bold',
                            textShadow: '1px 1px 1px rgba(0,0,0,0.8)'
                        }
                    }, heatmapInfo.delta > 0 ? `+${heatmapInfo.delta.toFixed(1)}` : heatmapInfo.delta.toFixed(1))
                );
            })
        )
    );
}

window.Factory = Factory; 