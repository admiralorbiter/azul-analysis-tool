# 🔧 FEN Implementation Plan

> **Step-by-step implementation plan for robust FEN system**

## 🎯 **Implementation Phases**

### **Phase 1: Core FEN Methods** *(Priority 1)*

#### **Step 1.1: Add FEN Methods to AzulState**

**File**: `core/azul_model.py`

```python
class AzulState(GameState):
    # ... existing code ...
    
    def to_fen(self) -> str:
        """Convert AzulState to standard FEN string."""
        try:
            # 1. Factories
            factories = self._encode_factories()
            
            # 2. Center Pool
            center = self._encode_center()
            
            # 3. Player Walls
            player1_wall = self._encode_wall(self.agents[0])
            player2_wall = self._encode_wall(self.agents[1])
            
            # 4. Pattern Lines
            player1_pattern = self._encode_pattern_lines(self.agents[0])
            player2_pattern = self._encode_pattern_lines(self.agents[1])
            
            # 5. Floor Lines
            player1_floor = self._encode_floor(self.agents[0])
            player2_floor = self._encode_floor(self.agents[1])
            
            # 6. Scores
            scores = f"{self.agents[0].score},{self.agents[1].score}"
            
            # 7. Round (estimate from game state)
            round_num = self._estimate_round()
            
            # 8. Current Player
            current_player = getattr(self, 'current_player', 0)
            
            # Combine all components
            fen_parts = [
                factories,
                center,
                f"{player1_wall}/{player1_pattern}/{player1_floor}",
                f"{player2_wall}/{player2_pattern}/{player2_floor}",
                scores,
                str(round_num),
                str(current_player)
            ]
            
            return "/".join(fen_parts)
            
        except Exception as e:
            # Fallback to hash-based FEN
            return self._fallback_fen()
    
    @classmethod
    def from_fen(cls, fen_string: str) -> 'AzulState':
        """Create AzulState from standard FEN string."""
        try:
            # Parse FEN components
            components = cls._parse_fen_components(fen_string)
            
            # Create new state
            state = cls(2)  # 2-player game
            
            # Apply components to state
            cls._apply_factories(state, components['factories'])
            cls._apply_center(state, components['center'])
            cls._apply_player(state, 0, components['player1'])
            cls._apply_player(state, 1, components['player2'])
            cls._apply_scores(state, components['scores'])
            cls._apply_round(state, components['round'])
            cls._apply_current_player(state, components['current_player'])
            
            return state
            
        except Exception as e:
            # Fallback to existing parsing
            return cls._fallback_from_fen(fen_string)
    
    # Helper methods for encoding
    def _encode_factories(self) -> str:
        """Encode factories to FEN format."""
        factory_strings = []
        for factory in self.factories:
            tiles = []
            for color, count in factory.tiles.items():
                color_letter = self._color_to_letter(color)
                tiles.extend([color_letter] * count)
            # Pad to 4 tiles
            while len(tiles) < 4:
                tiles.append('-')
            factory_strings.append(''.join(tiles[:4]))
        return "|".join(factory_strings)
    
    def _encode_center(self) -> str:
        """Encode center pool to FEN format."""
        tiles = []
        for color, count in self.centre_pool.tiles.items():
            color_letter = self._color_to_letter(color)
            tiles.extend([color_letter] * count)
        return ''.join(tiles) if tiles else '-'
    
    def _encode_wall(self, agent) -> str:
        """Encode player wall to FEN format."""
        rows = []
        for row in range(5):
            row_tiles = []
            for col in range(5):
                if agent.grid_state[row][col] == 1:
                    # Determine color based on position
                    color = self._get_wall_color(row, col)
                    row_tiles.append(self._color_to_letter(color))
                else:
                    row_tiles.append('-')
            rows.append(''.join(row_tiles))
        return "|".join(rows)
    
    def _encode_pattern_lines(self, agent) -> str:
        """Encode pattern lines to FEN format."""
        lines = []
        for line_num in range(5):
            line_length = line_num + 1
            line_tiles = []
            for pos in range(line_length):
                if pos < agent.lines_number[line_num]:
                    color = agent.lines_tile[line_num]
                    line_tiles.append(self._color_to_letter(color))
                else:
                    line_tiles.append('-')
            lines.append(''.join(line_tiles))
        return "|".join(lines)
    
    def _encode_floor(self, agent) -> str:
        """Encode floor line to FEN format."""
        tiles = []
        for tile in agent.floor_tiles:
            tiles.append(self._color_to_letter(tile))
        return ''.join(tiles) if tiles else '-'
    
    def _color_to_letter(self, color: int) -> str:
        """Convert color number to letter."""
        color_map = {0: 'B', 1: 'Y', 2: 'R', 3: 'K', 4: 'W'}
        return color_map.get(color, '-')
    
    def _get_wall_color(self, row: int, col: int) -> int:
        """Get the color that should be at wall position."""
        # This is the Azul wall color scheme
        color_scheme = [
            [0, 1, 2, 3, 4],  # Row 0: B,Y,R,K,W
            [4, 0, 1, 2, 3],  # Row 1: W,B,Y,R,K
            [3, 4, 0, 1, 2],  # Row 2: K,W,B,Y,R
            [2, 3, 4, 0, 1],  # Row 3: R,K,W,B,Y
            [1, 2, 3, 4, 0]   # Row 4: Y,R,K,W,B
        ]
        return color_scheme[row][col]
```

#### **Step 1.2: Add Validation Methods**

**File**: `core/azul_model.py` (continued)

```python
    @staticmethod
    def validate_fen(fen_string: str) -> bool:
        """Validate FEN string format and content."""
        try:
            # Basic format check
            if not fen_string or '/' not in fen_string:
                return False
            
            # Parse components
            components = AzulState._parse_fen_components(fen_string)
            
            # Validate each component
            if not AzulState._validate_factories(components.get('factories', [])):
                return False
            
            if not AzulState._validate_center(components.get('center', '')):
                return False
            
            if not AzulState._validate_player(components.get('player1', {})):
                return False
            
            if not AzulState._validate_player(components.get('player2', {})):
                return False
            
            if not AzulState._validate_scores(components.get('scores', '')):
                return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def _parse_fen_components(fen_string: str) -> dict:
        """Parse FEN string into components."""
        parts = fen_string.split('/')
        
        if len(parts) < 7:
            raise ValueError(f"Invalid FEN format: expected 7+ parts, got {len(parts)}")
        
        return {
            'factories': parts[0].split('|'),
            'center': parts[1],
            'player1': {
                'wall': parts[2].split('|'),
                'pattern': parts[3].split('|'),
                'floor': parts[4]
            },
            'player2': {
                'wall': parts[5].split('|'),
                'pattern': parts[6].split('|'),
                'floor': parts[7]
            },
            'scores': parts[8],
            'round': int(parts[9]) if len(parts) > 9 else 1,
            'current_player': int(parts[10]) if len(parts) > 10 else 0
        }
```

### **Phase 2: Integration with Existing System** *(Priority 2)*

#### **Step 2.1: Update API Endpoints**

**File**: `api/utils/state_parser.py`

```python
def state_to_fen(state) -> str:
    """Convert game state to FEN string with fallback."""
    try:
        # Try standard FEN first
        if hasattr(state, 'to_fen'):
            return state.to_fen()
    except Exception as e:
        print(f"DEBUG: Standard FEN failed, using fallback: {e}")
    
    # Fallback to hash-based FEN
    return _fallback_state_to_fen(state)

def parse_fen_string(fen_string: str):
    """Parse FEN string with enhanced support."""
    try:
        # Try standard FEN parsing first
        if AzulState.validate_fen(fen_string):
            return AzulState.from_fen(fen_string)
    except Exception as e:
        print(f"DEBUG: Standard FEN parsing failed: {e}")
    
    # Fallback to existing parsing
    return _fallback_parse_fen_string(fen_string)
```

### **Phase 3: Position Library Integration** *(Priority 3)*

#### **Step 3.1: Update Position Generation**

**File**: `ui/components/positions/opening-positions.js`

```javascript
// Add FEN generation to position objects
const balancedStart = {
    name: "Balanced Start",
    description: "Standard opening with equal distribution of all colors",
    difficulty: "beginner",
    tags: ["opening", "balanced", "standard", "beginner-friendly", "2-player"],
    generate: () => {
        const gameState = {
            factories: createBalancedFactories(),
            center: ['B', 'Y', 'R', 'K', 'W'],
            players: Array(2).fill().map(() => createEmptyPlayer())
        };
        
        // Generate standard FEN
        const fen = generateStandardFEN(gameState);
        
        return {
            ...gameState,
            fen_string: fen
        };
    }
};

function generateStandardFEN(gameState) {
    // Convert game state to standard FEN format
    const factories = gameState.factories.map(f => f.join('')).join('|');
    const center = gameState.center.join('');
    const players = gameState.players.map(player => {
        const wall = player.wall.map(row => row.map(tile => tile || '-').join('')).join('|');
        const pattern = player.pattern_lines.map(line => line.join('')).join('|');
        const floor = player.floor_line.join('');
        return `${wall}/${pattern}/${floor}`;
    });
    
    return `${factories}/${center}/${players[0]}/${players[1]}/0,0/1/0`;
}
```

## 📋 **Implementation Timeline**

### **Week 1: Core Implementation**
- [ ] **Day 1-2**: Implement `to_fen()` method
- [ ] **Day 3-4**: Implement `from_fen()` method
- [ ] **Day 5**: Add validation methods

### **Week 2: Integration**
- [ ] **Day 1-2**: Update API endpoints
- [ ] **Day 3-4**: Add backward compatibility
- [ ] **Day 5**: Update position library

### **Week 3: Testing**
- [ ] **Day 1-2**: Unit tests
- [ ] **Day 3-4**: Integration tests
- [ ] **Day 5**: Performance testing

## 🎯 **Success Criteria**

### **Functionality**
- [ ] Standard FEN format implemented
- [ ] Backward compatibility maintained
- [ ] Validation working correctly
- [ ] Performance acceptable

### **Quality**
- [ ] All tests passing
- [ ] No regression in existing functionality
- [ ] Error handling robust
- [ ] Documentation complete

---

**Status**: 📋 **Implementation Plan Complete** - Ready for coding
**Next Step**: Start implementing core FEN methods in AzulState 