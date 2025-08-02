# 🎯 Board State Setup Tools - Planning Document

## 📋 **Current State Analysis**

### **Existing Foundation** ✅
- **Advanced Sandbox**: Variation management, position export/import, move annotations
- **Game Management**: Player switching, mode selection, basic game setup
- **Board Rendering**: SVG-based interactive board with drag-and-drop
- **API Infrastructure**: Session management, rate limiting, analysis endpoints

### **Current Limitations** 🚧
- Limited to "Reset Game" and "New 2P Game" for initialization
- No granular control over individual board elements
- Can't easily create specific test scenarios
- No quick way to set up educational positions or edge cases

## 🎯 **Board State Setup Goals**

### **Primary Objectives**
1. **Intuitive Editing**: Click-to-edit any board element
2. **Quick Scenarios**: Preset configurations for common test cases
3. **Granular Control**: Full control over every game state component
4. **Educational Value**: Easy creation of teaching positions
5. **Testing Support**: Rapid setup of edge cases and specific scenarios

### **User Stories**
- As a **player**, I want to set up specific positions to practice difficult decisions
- As a **developer**, I want to quickly create edge cases for testing algorithms
- As a **teacher**, I want to create educational scenarios showing key concepts
- As an **analyst**, I want to compare outcomes from specific starting positions

## 🗂️ **Feature Breakdown & Implementation Sequence**

---

## **Phase 1: Core Editing Infrastructure** (3-4 days)

### **F1.1: Board Element Selection System**
*Foundation for all editing - visual feedback and selection*

#### **Implementation Details**
```javascript
class BoardEditor {
    constructor() {
        this.editMode = false;
        this.selectedElement = null;
        this.editHistory = [];
    }
    
    enableEditMode() {
        this.editMode = true;
        document.body.classList.add('edit-mode');
        this.addEditingVisualCues();
    }
    
    selectElement(elementType, elementId) {
        // Highlight selected element
        // Show context menu for editing options
        // Update UI to show edit controls
    }
}
```

#### **Visual Design**
- **Edit Mode Toggle**: Switch between play/edit modes
- **Element Highlighting**: Hover effects showing editable elements
- **Selection Indicators**: Clear visual feedback for selected elements
- **Context Menus**: Right-click options for quick edits

#### **Success Criteria**
- [ ] Users can clearly identify editable elements
- [ ] Smooth transition between play and edit modes
- [ ] Visual feedback is immediate and clear
- [ ] No conflicts with existing drag-and-drop

---

### **F1.2: Factory Editor**
*Direct manipulation of factory contents*

#### **Core Features**
```javascript
class FactoryEditor {
    editFactory(factoryId) {
        const factory = document.getElementById(`factory-${factoryId}`);
        this.showFactoryEditPanel(factory);
    }
    
    showFactoryEditPanel(factory) {
        // Modal with tile selection grid
        // Current tiles displayed with remove buttons
        // Add tile buttons for each color
        // Validate factory capacity (4 tiles max)
    }
}
```

#### **UI Components**
- **Factory Click**: Click any factory to edit contents
- **Tile Grid**: Visual tile selector (Blue, Yellow, Red, Black, White)
- **Current Contents**: Show existing tiles with remove buttons
- **Capacity Indicator**: Visual feedback for 4-tile limit
- **Quick Actions**: "Empty Factory", "Fill Random", "Fill Color"

#### **API Integration**
```python
@api_bp.route('/edit_factory', methods=['POST'])
def edit_factory():
    # Validate tile counts
    # Update factory state
    # Return updated game state
```

---

### **F1.3: Player Board Editor**
*Comprehensive player board manipulation*

#### **Pattern Lines Editor**
```javascript
class PatternLineEditor {
    editPatternLine(playerId, lineIndex) {
        // Show tile count selector (1-5 based on line)
        // Color selector for line contents
        // Option to mark line as "ready to tile"
    }
}
```

#### **Wall Editor**
```javascript
class WallEditor {
    editWall(playerId, row, col) {
        // Toggle tile presence
        // Visual feedback for valid wall positions
        // Auto-update score calculation
    }
}
```

#### **Floor Line Editor**
```javascript
class FloorLineEditor {
    editFloorLine(playerId) {
        // Tile selector for penalty tiles
        // Quantity selector for each tile type
        // Visual penalty point calculator
    }
}
```

---

## **Phase 2: Advanced Editing Tools** (3-4 days)

### **F2.1: Quick Preset System**
*One-click scenarios for common situations*

#### **Preset Categories**
```javascript
const BOARD_PRESETS = {
    educational: [
        {
            name: "First Player Advantage",
            description: "Demonstrate starting player benefits",
            setup: () => { /* configuration */ }
        },
        {
            name: "Endgame Decision",
            description: "Final round optimization",
            setup: () => { /* configuration */ }
        }
    ],
    testing: [
        {
            name: "Empty Bag Edge Case",
            description: "Test bag empty scenario",
            setup: () => { /* configuration */ }
        },
        {
            name: "Maximum Floor Penalty",
            description: "Full floor line testing",
            setup: () => { /* configuration */ }
        }
    ],
    competitive: [
        {
            name: "Tournament Opener",
            description: "Common opening position",
            setup: () => { /* configuration */ }
        }
    ]
};
```

#### **Preset UI**
- **Preset Browser**: Categorized list with thumbnails
- **Quick Apply**: One-click application
- **Preset Editor**: Modify and save custom presets
- **Sharing**: Export/import preset collections

---

### **F2.2: State Validation & Suggestions**
*Intelligent validation and realistic state creation*

#### **Validation Engine**
```javascript
class StateValidator {
    validateState(gameState) {
        const issues = [];
        
        // Check tile conservation
        if (!this.validateTileCount(gameState)) {
            issues.push("Tile count doesn't match expected totals");
        }
        
        // Check wall validity
        if (!this.validateWallPlacements(gameState)) {
            issues.push("Invalid wall tile placements detected");
        }
        
        // Check pattern line logic
        if (!this.validatePatternLines(gameState)) {
            issues.push("Pattern lines contain illegal configurations");
        }
        
        return {
            isValid: issues.length === 0,
            issues: issues,
            suggestions: this.generateSuggestions(issues)
        };
    }
}
```

#### **Smart Suggestions**
- **Auto-Complete**: Fill reasonable defaults for partial setups
- **Tile Distribution**: Suggest realistic tile distributions
- **Game Phase Detection**: Identify likely game phase and adjust accordingly
- **Balance Warnings**: Alert when setups heavily favor one player

---

### **F2.3: Template System**
*Save, load, and share custom scenarios*

#### **Template Management**
```javascript
class TemplateManager {
    saveTemplate(name, description, tags) {
        const template = {
            id: generateId(),
            name: name,
            description: description,
            tags: tags,
            gameState: this.captureCurrentState(),
            thumbnail: this.generateThumbnail(),
            created: Date.now()
        };
        
        return this.storage.save(template);
    }
    
    loadTemplate(templateId) {
        const template = this.storage.load(templateId);
        this.applyGameState(template.gameState);
        return template;
    }
}
```

#### **Template Features**
- **Template Library**: Personal collection of saved scenarios
- **Search & Filter**: Find templates by tags, description, or name
- **Template Sharing**: Export/import individual templates
- **Version Control**: Track template modifications
- **Usage Analytics**: Most-used templates for quick access

---

## **Phase 3: Advanced Features** (2-3 days)

### **F3.1: Batch Operations**
*Efficient multi-element editing*

#### **Multi-Select System**
```javascript
class BatchEditor {
    startMultiSelect() {
        this.multiSelectMode = true;
        this.selectedElements = new Set();
    }
    
    applyBatchOperation(operation, parameters) {
        for (const element of this.selectedElements) {
            this.applyOperation(element, operation, parameters);
        }
        this.commitBatchChanges();
    }
}
```

#### **Batch Operations**
- **Multi-Select**: Shift+click to select multiple elements
- **Bulk Clear**: Clear multiple factories/pattern lines at once
- **Color Replace**: Change all tiles of one color to another
- **Pattern Copy**: Copy one player's setup to another

---

### **F3.2: Visual State Designer**
*Advanced visual tools for state creation*

#### **Grid Overlay System**
```javascript
class GridOverlay {
    showPlacementGrid() {
        // Overlay showing valid tile placements
        // Color-coded for different tile types
        // Constraint visualization (pattern line rules)
    }
    
    showScoringPreview() {
        // Live scoring calculation overlay
        // Highlight scoring opportunities
        // Show point differentials
    }
}
```

#### **Visual Tools**
- **Placement Grid**: Show all valid tile positions
- **Scoring Overlay**: Live score calculation preview
- **Constraint Visualization**: Show pattern line rules visually
- **Symmetry Tools**: Mirror player setups, rotation tools

---

### **F3.3: Integration with Analysis**
*Connect setup tools with existing analysis features*

#### **Setup-to-Analysis Pipeline**
```javascript
class SetupAnalysisIntegration {
    analyzeCurrentSetup() {
        const gameState = this.captureCurrentState();
        return this.runAnalysis(gameState);
    }
    
    generateOptimalNext() {
        // Create setup for optimal continuation
        // Show decision tree from current position
        // Highlight critical next moves
    }
}
```

#### **Analysis Features**
- **Instant Analysis**: Run analysis on any created position
- **Position Comparison**: Compare multiple setup variations
- **Decision Trees**: Show likely continuations from setup
- **Educational Mode**: Explain why certain setups are interesting

---

## 🏗️ **Technical Implementation Plan**

### **Architecture Integration**
```
Current Structure:
├── ui/index.html (Main UI - extend with editing modes)
├── api/routes.py (Add setup endpoints)
└── core/ (Extend with validation logic)

New Components:
├── ui/
│   ├── board-editor.js (F1.1 - Core editing)
│   ├── factory-editor.js (F1.2 - Factory editing)
│   ├── player-editor.js (F1.3 - Player board editing)
│   ├── preset-manager.js (F2.1 - Presets)
│   ├── state-validator.js (F2.2 - Validation)
│   └── template-manager.js (F2.3 - Templates)
├── api/
│   ├── setup_routes.py (New setup endpoints)
│   └── validation.py (State validation logic)
└── core/
    ├── state_builder.py (Programmatic state creation)
    └── preset_definitions.py (Built-in presets)
```

### **UI Integration Points**
1. **Edit Mode Toggle**: Add to Game Management panel
2. **Setup Tools Panel**: New collapsible section in right sidebar
3. **Context Menus**: Right-click editing throughout board
4. **Modal Dialogs**: For complex editing operations
5. **Validation Feedback**: Real-time validation messages

### **API Endpoints**
```python
# Setup Management
POST /api/v1/setup/apply_preset     # Apply preset configuration
POST /api/v1/setup/edit_factory     # Modify factory contents
POST /api/v1/setup/edit_player      # Modify player board
POST /api/v1/setup/validate_state   # Validate current state
POST /api/v1/setup/save_template    # Save custom template
GET  /api/v1/setup/load_template    # Load saved template
GET  /api/v1/setup/list_presets     # Get available presets
```

---

## 📋 **Implementation Checklist**

### **Phase 1: Core Editing (Week 1)**
- [ ] **F1.1**: Board element selection system
  - [ ] Edit mode toggle in UI
  - [ ] Element highlighting on hover
  - [ ] Selection state management
  - [ ] Context menu system
- [ ] **F1.2**: Factory editor
  - [ ] Click-to-edit factories
  - [ ] Tile selection modal
  - [ ] Capacity validation
  - [ ] API integration
- [ ] **F1.3**: Player board editor
  - [ ] Pattern line editing
  - [ ] Wall tile management
  - [ ] Floor line editor
  - [ ] Score recalculation

### **Phase 2: Advanced Tools (Week 2)**
- [ ] **F2.1**: Quick preset system
  - [ ] Preset definitions
  - [ ] Preset browser UI
  - [ ] One-click application
  - [ ] Custom preset creation
- [ ] **F2.2**: State validation
  - [ ] Tile count validation
  - [ ] Wall placement rules
  - [ ] Pattern line logic
  - [ ] Smart suggestions
- [ ] **F2.3**: Template system
  - [ ] Template save/load
  - [ ] Template library UI
  - [ ] Search and filtering
  - [ ] Import/export functionality

### **Phase 3: Advanced Features (Week 3)**
- [ ] **F3.1**: Batch operations
  - [ ] Multi-select system
  - [ ] Bulk editing tools
  - [ ] Batch validation
- [ ] **F3.2**: Visual designer
  - [ ] Grid overlay system
  - [ ] Scoring preview
  - [ ] Constraint visualization
- [ ] **F3.3**: Analysis integration
  - [ ] Setup-to-analysis pipeline
  - [ ] Position comparison
  - [ ] Educational features

---

## 🎯 **Success Metrics**

### **Usability Goals**
- [ ] **Setup Speed**: Create custom position in <60s
- [ ] **Learning Curve**: New users productive within 5 minutes
- [ ] **Error Prevention**: Validation catches 95%+ of invalid states
- [ ] **Flexibility**: Support for any legal Azul position

### **Technical Goals**
- [ ] **Performance**: Setup operations complete in <200ms
- [ ] **Reliability**: Validation accuracy >99%
- [ ] **Integration**: Seamless with existing analysis features
- [ ] **Extensibility**: Easy to add new preset categories

### **Educational Goals**
- [ ] **Clarity**: Visual feedback makes rules obvious
- [ ] **Exploration**: Encourages experimentation with positions
- [ ] **Understanding**: Helps users learn game mechanics
- [ ] **Practice**: Enables targeted skill development

---

## 🚀 **Next Steps**

1. **Immediate**: Start with F1.1 (Board Element Selection System)
2. **Week 1**: Complete core editing infrastructure (F1.1-F1.3)
3. **Week 2**: Implement advanced tools (F2.1-F2.3)
4. **Week 3**: Add advanced features and polish (F3.1-F3.3)
5. **Testing**: Comprehensive user testing and refinement

This plan builds naturally on your existing Advanced Sandbox features and provides the foundation for intuitive board state creation while maintaining consistency with your current UI design and architecture.