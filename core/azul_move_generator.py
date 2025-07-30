"""
Azul Move Generator - A3 Implementation (Optimized)

This module provides efficient move generation for Azul with:
- Bit mask representations for fast move filtering
- Compound move enumeration (DraftOption × PlacementTarget)
- Performance target: ≤ 50µs per move generation
- Integration with existing state model and validator
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from . import azul_utils as utils
from .azul_model import AzulState, AzulGameRule
from .azul_validator import AzulRuleValidator


class FastMove:
    """Lightweight move representation for fast generation."""
    
    def __init__(self, action_type: int, source_id: int, tile_type: int, 
                 pattern_line_dest: int, num_to_pattern_line: int, num_to_floor_line: int):
        self.action_type = action_type
        self.source_id = source_id
        self.tile_type = tile_type
        self.pattern_line_dest = pattern_line_dest
        self.num_to_pattern_line = num_to_pattern_line
        self.num_to_floor_line = num_to_floor_line
        # Compute bit mask immediately for compatibility
        self.bit_mask = self._compute_bit_mask()
    
    def _compute_bit_mask(self) -> int:
        """Compute bit mask for this move."""
        return (
            (self.action_type & 0x3) << 18 |
            ((self.source_id + 1) & 0xF) << 14 |
            (self.tile_type & 0x7) << 11 |
            ((self.pattern_line_dest + 1) & 0x7) << 8 |
            (self.num_to_pattern_line & 0xF) << 4 |
            (self.num_to_floor_line & 0xF)
        )
    
    def compute_bit_mask(self) -> int:
        """Compute bit mask on demand."""
        return self.bit_mask
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format compatible with existing code."""
        return {
            'action_type': self.action_type,
            'source_id': self.source_id,
            'tile_grab': {
                'tile_type': self.tile_type,
                'number': self.num_to_pattern_line + self.num_to_floor_line,
                'pattern_line_dest': self.pattern_line_dest,
                'num_to_pattern_line': self.num_to_pattern_line,
                'num_to_floor_line': self.num_to_floor_line
            }
        }
    
    def to_tuple(self) -> Tuple:
        """Convert to tuple format compatible with existing getLegalActions."""
        tile_grab = utils.TileGrab()
        tile_grab.tile_type = self.tile_type
        tile_grab.number = self.num_to_pattern_line + self.num_to_floor_line
        tile_grab.pattern_line_dest = self.pattern_line_dest
        tile_grab.num_to_pattern_line = self.num_to_pattern_line
        tile_grab.num_to_floor_line = self.num_to_floor_line
        
        return (self.action_type, self.source_id, tile_grab)
    
    def __eq__(self, other):
        if not isinstance(other, (Move, FastMove)):
            return False
        return (self.action_type == other.action_type and
                self.source_id == other.source_id and
                self.tile_type == other.tile_type and
                self.pattern_line_dest == other.pattern_line_dest and
                self.num_to_pattern_line == other.num_to_pattern_line and
                self.num_to_floor_line == other.num_to_floor_line)
    
    def __hash__(self):
        return self.bit_mask


@dataclass(frozen=True)
class Move:
    """Immutable move representation with bit mask support."""
    action_type: int  # Action.TAKE_FROM_FACTORY or Action.TAKE_FROM_CENTRE
    source_id: int    # Factory ID (-1 for centre pool)
    tile_type: int    # Tile type (BLUE, YELLOW, etc.)
    pattern_line_dest: int  # Pattern line destination (-1 for floor only)
    num_to_pattern_line: int
    num_to_floor_line: int
    bit_mask: int = 0  # Bit representation for fast filtering
    
    def __post_init__(self):
        """Compute bit mask for efficient move comparison."""
        if self.bit_mask == 0:  # Only compute if not already set
            # Create a compact bit representation
            # Format: [action_type(2)][source_id(4)][tile_type(3)][pattern_line(3)][num_pattern(4)][num_floor(4)]
            mask = (
                (self.action_type & 0x3) << 18 |
                ((self.source_id + 1) & 0xF) << 14 |
                (self.tile_type & 0x7) << 11 |
                ((self.pattern_line_dest + 1) & 0x7) << 8 |
                (self.num_to_pattern_line & 0xF) << 4 |
                (self.num_to_floor_line & 0xF)
            )
            object.__setattr__(self, 'bit_mask', mask)
    
    def compute_bit_mask(self) -> int:
        """Compute bit mask on demand."""
        if self.bit_mask == 0:
            mask = (
                (self.action_type & 0x3) << 18 |
                ((self.source_id + 1) & 0xF) << 14 |
                (self.tile_type & 0x7) << 11 |
                ((self.pattern_line_dest + 1) & 0x7) << 8 |
                (self.num_to_pattern_line & 0xF) << 4 |
                (self.num_to_floor_line & 0xF)
            )
            object.__setattr__(self, 'bit_mask', mask)
        return self.bit_mask
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format compatible with existing code."""
        return {
            'action_type': self.action_type,
            'source_id': self.source_id,
            'tile_grab': {
                'tile_type': self.tile_type,
                'number': self.num_to_pattern_line + self.num_to_floor_line,
                'pattern_line_dest': self.pattern_line_dest,
                'num_to_pattern_line': self.num_to_pattern_line,
                'num_to_floor_line': self.num_to_floor_line
            }
        }
    
    def to_tuple(self) -> Tuple:
        """Convert to tuple format compatible with existing getLegalActions."""
        tile_grab = utils.TileGrab()
        tile_grab.tile_type = self.tile_type
        tile_grab.number = self.num_to_pattern_line + self.num_to_floor_line
        tile_grab.pattern_line_dest = self.pattern_line_dest
        tile_grab.num_to_pattern_line = self.num_to_pattern_line
        tile_grab.num_to_floor_line = self.num_to_floor_line
        
        return (self.action_type, self.source_id, tile_grab)
    
    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return (self.action_type == other.action_type and
                self.source_id == other.source_id and
                self.tile_type == other.tile_type and
                self.pattern_line_dest == other.pattern_line_dest and
                self.num_to_pattern_line == other.num_to_pattern_line and
                self.num_to_floor_line == other.num_to_floor_line)
    
    def __hash__(self):
        return self.compute_bit_mask()


class FastMoveGenerator:
    """
    Highly optimized move generator for Azul.
    
    Key optimizations:
    - Pre-computed pattern line validation cache
    - Reduced function calls and object creation
    - Bit operations for fast validation
    - Inline critical path operations
    """
    
    def __init__(self):
        self.validator = AzulRuleValidator()
        self._init_validation_cache()
    
    def _init_validation_cache(self):
        """Initialize validation cache for fast pattern line checking."""
        # Pre-compute grid positions for each tile type and pattern line
        self._grid_positions = {}
        for tile_type in range(5):  # Use integers instead of enum
            self._grid_positions[tile_type] = []
            for pattern_line in range(5):
                # Calculate grid position for this tile type in this pattern line
                # This is the same logic as in the original grid_scheme
                if pattern_line == 0:
                    if tile_type == utils.Tile.BLUE:
                        grid_col = 0
                    elif tile_type == utils.Tile.WHITE:
                        grid_col = 4
                    elif tile_type == utils.Tile.BLACK:
                        grid_col = 3
                    elif tile_type == utils.Tile.RED:
                        grid_col = 2
                    elif tile_type == utils.Tile.YELLOW:
                        grid_col = 1
                elif pattern_line == 1:
                    if tile_type == utils.Tile.BLUE:
                        grid_col = 1
                    elif tile_type == utils.Tile.WHITE:
                        grid_col = 0
                    elif tile_type == utils.Tile.BLACK:
                        grid_col = 4
                    elif tile_type == utils.Tile.RED:
                        grid_col = 3
                    elif tile_type == utils.Tile.YELLOW:
                        grid_col = 2
                elif pattern_line == 2:
                    if tile_type == utils.Tile.BLUE:
                        grid_col = 2
                    elif tile_type == utils.Tile.WHITE:
                        grid_col = 1
                    elif tile_type == utils.Tile.BLACK:
                        grid_col = 0
                    elif tile_type == utils.Tile.RED:
                        grid_col = 4
                    elif tile_type == utils.Tile.YELLOW:
                        grid_col = 3
                elif pattern_line == 3:
                    if tile_type == utils.Tile.BLUE:
                        grid_col = 3
                    elif tile_type == utils.Tile.WHITE:
                        grid_col = 2
                    elif tile_type == utils.Tile.BLACK:
                        grid_col = 1
                    elif tile_type == utils.Tile.RED:
                        grid_col = 0
                    elif tile_type == utils.Tile.YELLOW:
                        grid_col = 4
                elif pattern_line == 4:
                    if tile_type == utils.Tile.BLUE:
                        grid_col = 4
                    elif tile_type == utils.Tile.WHITE:
                        grid_col = 3
                    elif tile_type == utils.Tile.BLACK:
                        grid_col = 2
                    elif tile_type == utils.Tile.RED:
                        grid_col = 1
                    elif tile_type == utils.Tile.YELLOW:
                        grid_col = 0
                
                self._grid_positions[tile_type].append(grid_col)
        
        # Pre-compute pattern line validation masks for compatibility
        self._pattern_line_masks = {}
        for tile_type in range(5):
            for pattern_line in range(5):
                # Create bit mask for quick validation
                mask = 0
                if pattern_line < 5:  # Valid pattern line
                    mask |= (1 << pattern_line)
                self._pattern_line_masks[(tile_type, pattern_line)] = mask
    
    def _get_valid_pattern_lines_for_tile_fast(self, agent_state, tile_type: int) -> List[int]:
        """Get valid pattern lines for a specific tile type (optimized)."""
        valid_lines = []
        
        for pattern_line in range(agent_state.GRID_SIZE):
            # Quick validation using pre-computed grid positions
            if (agent_state.lines_tile[pattern_line] == -1 or 
                agent_state.lines_tile[pattern_line] == tile_type):
                
                grid_col = self._grid_positions[tile_type][pattern_line]
                if agent_state.grid_state[pattern_line][grid_col] == 0:
                    valid_lines.append(pattern_line)
        
        return valid_lines
    
    def _can_place_in_pattern_line(self, agent_state, pattern_line: int, tile_type: int) -> bool:
        """Check if tiles can be placed in a specific pattern line."""
        # Check if pattern line already has different tile type
        if (agent_state.lines_tile[pattern_line] != -1 and 
            agent_state.lines_tile[pattern_line] != tile_type):
            return False
        
        # Check if grid position is already occupied
        grid_col = self._grid_positions[tile_type][pattern_line]
        if agent_state.grid_state[pattern_line][grid_col] == 1:
            return False
        
        return True
    
    def generate_moves_fast(self, state: AzulState, agent_id: int) -> List[FastMove]:
        """
        Ultra-fast move generation with minimal object creation.
        
        This method targets ≤ 50µs performance by:
        - Inlining all validation logic
        - Minimal object creation
        - Direct array access
        """
        moves = []
        agent_state = state.agents[agent_id]
        
        # Pre-compute valid pattern lines for each tile type once
        valid_pattern_lines = self._get_valid_pattern_lines_fast(agent_state)
        
        # Generate factory moves
        for factory_id, factory in enumerate(state.factories):
            factory_moves = self._generate_factory_moves_fast(
                agent_state, factory.tiles, factory_id, valid_pattern_lines
            )
            moves.extend(factory_moves)
        
        # Generate centre moves
        centre_moves = self._generate_centre_moves_fast(
            agent_state, state.centre_pool.tiles, valid_pattern_lines
        )
        moves.extend(centre_moves)
        
        return moves
    
    def _get_valid_pattern_lines_fast(self, agent_state) -> Dict[int, List[int]]:
        """Get valid pattern lines for each tile type (optimized)."""
        valid_lines = {}
        
        for tile_type in range(5):  # Use integers instead of enum
            valid_lines[tile_type] = []
            for pattern_line in range(5):
                # Quick validation using pre-computed grid positions
                if (agent_state.lines_tile[pattern_line] == -1 or 
                    agent_state.lines_tile[pattern_line] == tile_type):
                    
                    grid_col = self._grid_positions[tile_type][pattern_line]
                    if agent_state.grid_state[pattern_line][grid_col] == 0:
                        valid_lines[tile_type].append(pattern_line)
        
        return valid_lines
    
    def _generate_factory_moves_fast(self, agent_state, factory_tiles: Dict, 
                                   factory_id: int, valid_pattern_lines: Dict[int, List[int]]) -> List[FastMove]:
        """Ultra-fast factory move generation."""
        moves = []
        
        for tile_type, num_available in factory_tiles.items():
            if num_available == 0:
                continue
            
            # Generate pattern line moves
            if tile_type in valid_pattern_lines:
                for pattern_line in valid_pattern_lines[tile_type]:
                    slots_free = (pattern_line + 1) - agent_state.lines_number[pattern_line]
                    if slots_free <= 0:
                        continue
                    
                    num_to_pattern = min(num_available, slots_free)
                    num_to_floor = num_available - num_to_pattern
                    
                    # Create move using FastMove for better performance
                    move = FastMove(
                        action_type=utils.Action.TAKE_FROM_FACTORY,
                        source_id=factory_id,
                        tile_type=tile_type,
                        pattern_line_dest=pattern_line,
                        num_to_pattern_line=num_to_pattern,
                        num_to_floor_line=num_to_floor
                    )
                    moves.append(move)
            
            # Generate floor-only move
            move = FastMove(
                action_type=utils.Action.TAKE_FROM_FACTORY,
                source_id=factory_id,
                tile_type=tile_type,
                pattern_line_dest=-1,
                num_to_pattern_line=0,
                num_to_floor_line=num_available
            )
            moves.append(move)
        
        return moves
    
    def _generate_centre_moves_fast(self, agent_state, centre_tiles: Dict, 
                                  valid_pattern_lines: Dict[int, List[int]]) -> List[FastMove]:
        """Ultra-fast centre move generation."""
        moves = []
        
        for tile_type, num_available in centre_tiles.items():
            if num_available == 0:
                continue
            
            # Generate pattern line moves
            if tile_type in valid_pattern_lines:
                for pattern_line in valid_pattern_lines[tile_type]:
                    slots_free = (pattern_line + 1) - agent_state.lines_number[pattern_line]
                    if slots_free <= 0:
                        continue
                    
                    num_to_pattern = min(num_available, slots_free)
                    num_to_floor = num_available - num_to_pattern
                    
                    # Create move using FastMove for better performance
                    move = FastMove(
                        action_type=utils.Action.TAKE_FROM_CENTRE,
                        source_id=-1,
                        tile_type=tile_type,
                        pattern_line_dest=pattern_line,
                        num_to_pattern_line=num_to_pattern,
                        num_to_floor_line=num_to_floor
                    )
                    moves.append(move)
            
            # Generate floor-only move
            move = FastMove(
                action_type=utils.Action.TAKE_FROM_CENTRE,
                source_id=-1,
                tile_type=tile_type,
                pattern_line_dest=-1,
                num_to_pattern_line=0,
                num_to_floor_line=num_available
            )
            moves.append(move)
        
        return moves
    
    def get_move_count(self, state: AzulState, agent_id: int) -> int:
        """Get the number of legal moves without generating them all."""
        count = 0
        agent_state = state.agents[agent_id]
        valid_pattern_lines = self._get_valid_pattern_lines_fast(agent_state)
        
        # Count factory moves
        for factory in state.factories:
            for tile_type in range(5):
                if factory.tiles[tile_type] > 0:
                    count += len(valid_pattern_lines.get(tile_type, [])) + 1  # +1 for floor
        
        # Count centre moves
        for tile_type in range(5):
            if state.centre_pool.tiles[tile_type] > 0:
                count += len(valid_pattern_lines.get(tile_type, [])) + 1  # +1 for floor
        
        return count
    
    def validate_move(self, move: FastMove, state: AzulState, agent_id: int) -> bool:
        """Validate a specific move using the rule validator."""
        move_dict = move.to_dict()
        return self.validator.validate_move(state, move_dict, agent_id)


class AzulMoveGenerator:
    """
    High-performance move generator for Azul.
    
    Features:
    - Bit mask representations for fast filtering
    - Compound move enumeration (DraftOption × PlacementTarget)
    - Cached pattern line validation
    - Performance target: ≤ 50µs per move generation
    """
    
    def __init__(self):
        self.validator = AzulRuleValidator()
        self._pattern_line_cache = {}  # Cache for pattern line validation
        
    def generate_moves(self, state: AzulState, agent_id: int) -> List[Move]:
        """
        Generate all legal moves for the given agent.
        
        Args:
            state: Current game state
            agent_id: Agent to generate moves for
            
        Returns:
            List of legal moves with bit mask representations
        """
        moves = []
        agent_state = state.agents[agent_id]
        
        # Generate factory moves
        for factory_id, factory in enumerate(state.factories):
            moves.extend(self._generate_factory_moves(state, agent_id, factory_id, factory))
        
        # Generate centre pool moves
        moves.extend(self._generate_centre_moves(state, agent_id))
        
        return moves
    
    def _generate_factory_moves(self, state: AzulState, agent_id: int, 
                               factory_id: int, factory) -> List[Move]:
        """Generate moves for a specific factory."""
        moves = []
        agent_state = state.agents[agent_id]
        
        for tile_type in utils.Tile:
            num_available = factory.tiles[tile_type]
            if num_available == 0:
                continue
            
            # Generate pattern line moves
            pattern_moves = self._generate_pattern_line_moves(
                agent_state, tile_type, num_available, factory_id, utils.Action.TAKE_FROM_FACTORY
            )
            moves.extend(pattern_moves)
            
            # Generate floor-only move
            floor_move = Move(
                action_type=utils.Action.TAKE_FROM_FACTORY,
                source_id=factory_id,
                tile_type=tile_type,
                pattern_line_dest=-1,
                num_to_pattern_line=0,
                num_to_floor_line=num_available
            )
            moves.append(floor_move)
        
        return moves
    
    def _generate_centre_moves(self, state: AzulState, agent_id: int) -> List[Move]:
        """Generate moves from the centre pool."""
        moves = []
        agent_state = state.agents[agent_id]
        
        for tile_type in utils.Tile:
            num_available = state.centre_pool.tiles[tile_type]
            if num_available == 0:
                continue
            
            # Generate pattern line moves
            pattern_moves = self._generate_pattern_line_moves(
                agent_state, tile_type, num_available, -1, utils.Action.TAKE_FROM_CENTRE
            )
            moves.extend(pattern_moves)
            
            # Generate floor-only move
            floor_move = Move(
                action_type=utils.Action.TAKE_FROM_CENTRE,
                source_id=-1,
                tile_type=tile_type,
                pattern_line_dest=-1,
                num_to_pattern_line=0,
                num_to_floor_line=num_available
            )
            moves.append(floor_move)
        
        return moves
    
    def _generate_pattern_line_moves(self, agent_state, tile_type: int, 
                                   num_available: int, source_id: int, 
                                   action_type: int) -> List[Move]:
        """Generate moves for pattern line placement."""
        moves = []
        
        for pattern_line in range(agent_state.GRID_SIZE):
            # Check if tiles can be placed in this pattern line
            if not self._can_place_in_pattern_line(agent_state, pattern_line, tile_type):
                continue
            
            # Calculate available slots
            slots_free = (pattern_line + 1) - agent_state.lines_number[pattern_line]
            if slots_free <= 0:
                continue
            
            # Create move with tiles split between pattern line and floor
            num_to_pattern = min(num_available, slots_free)
            num_to_floor = num_available - num_to_pattern
            
            move = Move(
                action_type=action_type,
                source_id=source_id,
                tile_type=tile_type,
                pattern_line_dest=pattern_line,
                num_to_pattern_line=num_to_pattern,
                num_to_floor_line=num_to_floor
            )
            moves.append(move)
        
        return moves
    
    def _can_place_in_pattern_line(self, agent_state, pattern_line: int, tile_type: int) -> bool:
        """Check if tiles can be placed in a specific pattern line."""
        # Check if pattern line already has different tile type
        if (agent_state.lines_tile[pattern_line] != -1 and 
            agent_state.lines_tile[pattern_line] != tile_type):
            return False
        
        # Check if grid position is already occupied
        grid_col = int(agent_state.grid_scheme[pattern_line][tile_type])
        if agent_state.grid_state[pattern_line][grid_col] == 1:
            return False
        
        return True
    
    def filter_moves_by_score(self, moves: List[Move], state: AzulState, 
                             agent_id: int, min_score_delta: float = 0.0) -> List[Move]:
        """
        Filter moves based on immediate score impact.
        
        Args:
            moves: List of moves to filter
            state: Current game state
            agent_id: Agent ID
            min_score_delta: Minimum score improvement to keep move
            
        Returns:
            Filtered list of moves
        """
        if min_score_delta <= 0.0:
            return moves
        
        filtered_moves = []
        for move in moves:
            # Quick heuristic: prefer moves that don't add to floor
            if move.num_to_floor_line == 0:
                filtered_moves.append(move)
            elif move.num_to_pattern_line > 0:
                # Only keep floor moves if they have some pattern line placement
                filtered_moves.append(move)
        
        return filtered_moves
    
    def get_move_count(self, state: AzulState, agent_id: int) -> int:
        """Get the number of legal moves without generating them all."""
        count = 0
        agent_state = state.agents[agent_id]
        
        # Count factory moves
        for factory in state.factories:
            for tile_type in utils.Tile:
                if factory.tiles[tile_type] > 0:
                    count += self._count_pattern_line_options(agent_state, tile_type) + 1  # +1 for floor
        
        # Count centre moves
        for tile_type in utils.Tile:
            if state.centre_pool.tiles[tile_type] > 0:
                count += self._count_pattern_line_options(agent_state, tile_type) + 1  # +1 for floor
        
        return count
    
    def _count_pattern_line_options(self, agent_state, tile_type: int) -> int:
        """Count how many pattern lines can accept this tile type."""
        count = 0
        for pattern_line in range(agent_state.GRID_SIZE):
            if self._can_place_in_pattern_line(agent_state, pattern_line, tile_type):
                count += 1
        return count
    
    def validate_move(self, move: Move, state: AzulState, agent_id: int) -> bool:
        """Validate a specific move using the rule validator."""
        move_dict = move.to_dict()
        return self.validator.validate_move(state, move_dict, agent_id) 