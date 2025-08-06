# 📋 Standard FEN Format Design

> **Design for traditional FEN notation adapted for Azul**

## 🎯 **FEN Format Structure**

### **Traditional FEN Components**
Standard FEN (Forsyth-Edwards Notation) has 6 parts:
1. **Piece placement** - Board state
2. **Active color** - Whose turn
3. **Castling availability** - Not applicable to Azul
4. **En passant** - Not applicable to Azul
5. **Halfmove clock** - Not applicable to Azul
6. **Fullmove number** - Round number

### **Azul-Specific FEN Format**

```
[Factories]/[Center]/[Player1]/[Player2]/[Round]/[CurrentPlayer]
```

#### **Component Breakdown**

**1. Factories (F)**
```
Format: F1|F2|F3|F4|F5
Example: BYRY|RKWW|WBBY|YRKK|KWBB
```
- Each factory: 4 tiles represented by color letters
- Colors: B(Blue), Y(Yellow), R(Red), K(Black), W(White)
- Empty: `----` (4 dashes)

**2. Center Pool (C)**
```
Format: C1C2C3...
Example: BYR
```
- List of available tiles in center
- Empty: `-` (single dash)

**3. Player Walls (W)**
```
Format: W1/W2/W3/W4/W5
Example: B----|Y----|R----|K----|W----
```
- Each row: 5 positions (B,Y,R,K,W or -)
- `-` = empty position
- `B` = Blue tile, etc.

**4. Pattern Lines (P)**
```
Format: P1/P2/P3/P4/P5
Example: BB--|YYY-|----|----|----
```
- Each line: 1-5 positions (B,Y,R,K,W or -)
- `-` = empty position
- Number of positions = line number (line 1 = 1 pos, line 2 = 2 pos, etc.)

**5. Floor Line (L)**
```
Format: L1L2L3...
Example: BRW
```
- List of tiles on floor
- Empty: `-` (single dash)

**6. Scores (S)**
```
Format: S1,S2
Example: 12,8
```
- Player scores separated by comma

**7. Round (R)**
```
Format: R
Example: 3
```
- Current round number (1-6)

**8. Current Player (P)**
```
Format: P
Example: 0
```
- Current player (0 or 1)

## 📝 **Complete FEN Example**

### **Initial Position**
```
BYRY|RKWW|WBBY|YRKK|KWBB/BYR/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-----|-----|-----|-----|-----/-/-/0,0/1/0
```

### **Mid-Game Position**
```
BYRY|RKWW|WBBY|YRKK|KWBB/BY/B----|Y----|R----|K----|W----/BB--|YYY-|----|----|----/BRW/12,8/3/1
```

## 🔧 **Implementation Plan**

### **Phase 1: Core FEN Methods**
```python
class AzulState:
    def to_fen(self) -> str:
        """Convert AzulState to FEN string."""
        pass
    
    @classmethod
    def from_fen(cls, fen_string: str) -> 'AzulState':
        """Create AzulState from FEN string."""
        pass
```

### **Phase 2: Validation**
```python
def validate_fen(fen_string: str) -> bool:
    """Validate FEN string format and content."""
    pass

def parse_fen_components(fen_string: str) -> dict:
    """Parse FEN string into components."""
    pass
```

### **Phase 3: Conversion Utilities**
```python
def fen_to_game_state(fen_string: str) -> dict:
    """Convert FEN to game state dict."""
    pass

def game_state_to_fen(game_state: dict) -> str:
    """Convert game state dict to FEN."""
    pass
```

## 🚀 **Benefits of Standard FEN**

### **1. Interoperability**
- Share positions with other Azul systems
- Standard format for position databases
- Easy import/export functionality

### **2. Human Readability**
- Positions can be read and written by humans
- Easy to share positions via text
- Debugging and analysis simplified

### **3. Validation**
- Clear format rules for validation
- Easy to detect malformed positions
- Consistent error handling

### **4. Performance**
- Direct parsing without hash lookups
- No conversion layers needed
- Efficient serialization/deserialization

## 📋 **Implementation Steps**

### **Step 1: Design Validation**
- [ ] Review FEN format design
- [ ] Test with sample positions
- [ ] Validate edge cases

### **Step 2: Core Implementation**
- [ ] Implement `to_fen()` method
- [ ] Implement `from_fen()` method
- [ ] Add basic validation

### **Step 3: Integration**
- [ ] Update API endpoints
- [ ] Modify position library
- [ ] Add backward compatibility

### **Step 4: Testing**
- [ ] Unit tests for FEN methods
- [ ] Integration tests
- [ ] Performance testing

---

**Status**: 📋 **Design Complete** - Ready for implementation
**Next Step**: Implement core FEN methods in AzulState 