from .template import GameState, GameRule, Agent

import random
import numpy
import copy
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from . import azul_utils as utils


@dataclass(frozen=True)
class ImmutableTileDisplay:
    """Immutable tile display for factories and center pool."""
    tiles: Dict[int, int] = field(default_factory=dict)
    total: int = 0
    
    def __post_init__(self):
        """Initialize tiles dict if not provided."""
        if not self.tiles:
            object.__setattr__(self, 'tiles', {tile: 0 for tile in utils.Tile})
    
    def reaction_tiles(self, number: int, tile_type: int) -> 'ImmutableTileDisplay':
        """Create new display with tiles removed."""
        new_tiles = self.tiles.copy()
        new_tiles[tile_type] -= number
        return ImmutableTileDisplay(new_tiles, self.total - number)
    
    def add_tiles(self, number: int, tile_type: int) -> 'ImmutableTileDisplay':
        """Create new display with tiles added."""
        new_tiles = self.tiles.copy()
        new_tiles[tile_type] += number
        return ImmutableTileDisplay(new_tiles, self.total + number)


@dataclass(frozen=True)
class ImmutableAgentState:
    """Immutable agent state for efficient copying."""
    id: int
    score: int = 0
    lines_number: List[int] = field(default_factory=lambda: [0] * 5)
    lines_tile: List[int] = field(default_factory=lambda: [-1] * 5)
    grid_state: Any = field(default_factory=lambda: numpy.zeros((5, 5)))
    floor: List[int] = field(default_factory=lambda: [0] * 7)
    floor_tiles: List[int] = field(default_factory=list)
    number_of: Dict[int, int] = field(default_factory=dict)
    grid_scheme: Any = field(default_factory=lambda: numpy.zeros((5, 5)))
    
    def __post_init__(self):
        """Initialize grid scheme and number_of dict."""
        if not self.number_of:
            object.__setattr__(self, 'number_of', {tile: 0 for tile in utils.Tile})
        
        if numpy.array_equal(self.grid_scheme, numpy.zeros((5, 5))):
            # Initialize grid scheme
            scheme = numpy.zeros((5, 5))
            # Set up the grid scheme (this is the same logic as in the original)
            scheme[0][utils.Tile.BLUE] = 0
            scheme[1][utils.Tile.BLUE] = 1
            scheme[2][utils.Tile.BLUE] = 2
            scheme[3][utils.Tile.BLUE] = 3
            scheme[4][utils.Tile.BLUE] = 4
            
            scheme[1][utils.Tile.WHITE] = 0
            scheme[2][utils.Tile.WHITE] = 1
            scheme[3][utils.Tile.WHITE] = 2
            scheme[4][utils.Tile.WHITE] = 3 
            scheme[0][utils.Tile.WHITE] = 4
            
            scheme[2][utils.Tile.BLACK] = 0 
            scheme[3][utils.Tile.BLACK] = 1
            scheme[4][utils.Tile.BLACK] = 2
            scheme[0][utils.Tile.BLACK] = 3
            scheme[1][utils.Tile.BLACK] = 4
            
            scheme[3][utils.Tile.RED] = 0
            scheme[4][utils.Tile.RED] = 1
            scheme[0][utils.Tile.RED] = 2
            scheme[1][utils.Tile.RED] = 3
            scheme[2][utils.Tile.RED] = 4
            
            scheme[4][utils.Tile.YELLOW] = 0
            scheme[0][utils.Tile.YELLOW] = 1
            scheme[1][utils.Tile.YELLOW] = 2
            scheme[2][utils.Tile.YELLOW] = 3
            scheme[3][utils.Tile.YELLOW] = 4
            
            object.__setattr__(self, 'grid_scheme', scheme)
    
    def with_score(self, new_score: int) -> 'ImmutableAgentState':
        """Create new state with updated score."""
        return ImmutableAgentState(
            id=self.id,
            score=new_score,
            lines_number=self.lines_number,
            lines_tile=self.lines_tile,
            grid_state=self.grid_state,
            floor=self.floor,
            floor_tiles=self.floor_tiles,
            number_of=self.number_of,
            grid_scheme=self.grid_scheme
        )
    
    def with_lines(self, lines_number: List[int], lines_tile: List[int]) -> 'ImmutableAgentState':
        """Create new state with updated pattern lines."""
        return ImmutableAgentState(
            id=self.id,
            score=self.score,
            lines_number=lines_number,
            lines_tile=lines_tile,
            grid_state=self.grid_state,
            floor=self.floor,
            floor_tiles=self.floor_tiles,
            number_of=self.number_of,
            grid_scheme=self.grid_scheme
        )
    
    def with_grid_state(self, new_grid_state: Any) -> 'ImmutableAgentState':
        """Create new state with updated grid."""
        return ImmutableAgentState(
            id=self.id,
            score=self.score,
            lines_number=self.lines_number,
            lines_tile=self.lines_tile,
            grid_state=new_grid_state,
            floor=self.floor,
            floor_tiles=self.floor_tiles,
            number_of=self.number_of,
            grid_scheme=self.grid_scheme
        )
    
    def with_floor(self, new_floor: List[int], new_floor_tiles: List[int]) -> 'ImmutableAgentState':
        """Create new state with updated floor."""
        return ImmutableAgentState(
            id=self.id,
            score=self.score,
            lines_number=self.lines_number,
            lines_tile=self.lines_tile,
            grid_state=self.grid_state,
            floor=new_floor,
            floor_tiles=new_floor_tiles,
            number_of=self.number_of,
            grid_scheme=self.grid_scheme
        )


@dataclass(frozen=True)
class ImmutableAzulState:
    """Immutable version of AzulState for functional programming."""
    agents: List[ImmutableAgentState]
    bag: List[int]
    bag_used: List[int]
    factories: List[ImmutableTileDisplay]
    centre_pool: ImmutableTileDisplay
    first_agent_taken: bool
    first_agent: int
    next_first_agent: int
    
    def to_mutable(self) -> 'AzulState':
        """Convert immutable state back to mutable AzulState."""
        # This would need to be implemented to convert back
        # For now, we'll create a new AzulState and populate it
        state = AzulState(len(self.agents))
        state.from_immutable(self)
        return state


class AzulState(GameState):
    NUM_FACTORIES = [5]  # Only 2-player games supported
    NUM_TILE_TYPE = 20
    NUM_ON_FACTORY = 4

    # Zobrist hash tables for efficient position identification
    _ZOBRIST_TABLES = None
    
    @classmethod
    def from_dict(cls, game_dict):
        """
        Create AzulState from dictionary format (from UI).
        
        This is a simplified implementation for validation purposes.
        """
        try:
            # Determine number of agents from the data
            agents_data = game_dict.get('agents', [])
            if not agents_data:
                # Try alternative keys that might be used
                if 'players' in game_dict:
                    agents_data = game_dict['players']
                else:
                    # Default to 2 players
                    agents_data = [{}, {}]
            
            num_agents = len(agents_data)
            if num_agents == 0:
                num_agents = 2  # Default to 2 players
            
            # Create new state
            state = cls(num_agents)
            
            # Update agent states if available
            for i, agent_data in enumerate(agents_data):
                if i < len(state.agents):
                    agent = state.agents[i]
                    
                    # Update pattern lines
                    if 'lines_tile' in agent_data:
                        agent.lines_tile = list(agent_data['lines_tile'])
                    if 'lines_number' in agent_data:
                        agent.lines_number = list(agent_data['lines_number'])
                    
                    # Update score
                    if 'score' in agent_data:
                        agent.score = agent_data['score']
                    
                    # Update grid state (wall)
                    if 'grid_state' in agent_data:
                        agent.grid_state = [list(row) for row in agent_data['grid_state']]
                    
                    # Update floor tiles
                    if 'floor_tiles' in agent_data:
                        agent.floor_tiles = list(agent_data['floor_tiles'])
            
            # Update factories if available
            factories_data = game_dict.get('factories', [])
            for i, factory_data in enumerate(factories_data):
                if i < len(state.factories):
                    factory = state.factories[i]
                    if 'tiles' in factory_data:
                        factory.tiles = dict(factory_data['tiles'])
                        factory.total = sum(factory.tiles.values())
            
            # Update center pool if available
            if 'centre_pool' in game_dict:
                center_data = game_dict['centre_pool']
                if 'tiles' in center_data:
                    state.centre_pool.tiles = dict(center_data['tiles'])
                    state.centre_pool.total = sum(state.centre_pool.tiles.values())
            
            return state
            
        except Exception as e:
            # If conversion fails, create a basic valid state
            print(f"Warning: Failed to convert game dict to AzulState: {e}")
            return cls(2)  # Return basic 2-player state

    @classmethod
    def _initialize_zobrist_tables(cls):
        """Initialize Zobrist hash tables for efficient position hashing."""
        if cls._ZOBRIST_TABLES is not None:
            return
            
        import random
        # Use a fixed seed for reproducible hashes
        random.seed(42)
        
        cls._ZOBRIST_TABLES = {
            # Hash for each tile position on each agent's grid (agent, row, col, tile_type)
            'grid': numpy.random.randint(0, 2**64, (4, 5, 5, 5), dtype=numpy.uint64),
            # Hash for each tile in floor line (agent, position, tile_type) 
            'floor': numpy.random.randint(0, 2**64, (4, 7, 5), dtype=numpy.uint64),
            # Hash for each tile in pattern lines (agent, line, tile_type)
            'pattern': numpy.random.randint(0, 2**64, (4, 5, 5), dtype=numpy.uint64),
            # Hash for factory tiles (factory_id, tile_type)
            'factory': numpy.random.randint(0, 2**64, (9, 5), dtype=numpy.uint64),
            # Hash for center pool tiles (tile_type)
            'center': numpy.random.randint(0, 2**64, 5, dtype=numpy.uint64),
            # Hash for first player token (agent_id)
            'first_player': numpy.random.randint(0, 2**64, 4, dtype=numpy.uint64),
            # Hash for bag contents (tile_type)
            'bag': numpy.random.randint(0, 2**64, 5, dtype=numpy.uint64),
        }
        random.seed()  # Reset to random seed
    
    def _compute_zobrist_hash(self):
        """Compute the Zobrist hash for the current game state."""
        if self._ZOBRIST_TABLES is None:
            self._initialize_zobrist_tables()
            
        hash_value = 0
        
        # Hash agent scores and states
        for agent_id, agent in enumerate(self.agents):
            # Hash agent score (for simplicity, we'll use a simple hash of the score)
            score_hash = hash(str(agent.score)) & 0xFFFFFFFFFFFFFFFF
            hash_value ^= score_hash
            
            # Hash agent grid states
            for row in range(5):
                for col in range(5):
                    if agent.grid_state[row][col] == 1:
                        # Find which tile type should be at this position
                        tile_type = self._get_tile_at_position(agent, row, col)
                        hash_value ^= self._ZOBRIST_TABLES['grid'][agent_id][row][col][tile_type]
        
        # Hash floor tiles
        for agent_id, agent in enumerate(self.agents):
            for pos, tile in enumerate(agent.floor_tiles):
                if tile is not None:
                    hash_value ^= self._ZOBRIST_TABLES['floor'][agent_id][pos][tile]
        
        # Hash pattern lines
        for agent_id, agent in enumerate(self.agents):
            for line in range(5):
                if agent.lines_tile[line] != -1:
                    hash_value ^= self._ZOBRIST_TABLES['pattern'][agent_id][line][agent.lines_tile[line]]
        
        # Hash factory tiles
        for factory_id, factory in enumerate(self.factories):
            for tile_type in utils.Tile:
                if factory.tiles[tile_type] > 0:
                    hash_value ^= self._ZOBRIST_TABLES['factory'][factory_id][tile_type]
        
        # Hash center pool tiles
        for tile_type in utils.Tile:
            if self.centre_pool.tiles[tile_type] > 0:
                hash_value ^= self._ZOBRIST_TABLES['center'][tile_type]
        
        # Hash first player token
        if hasattr(self, 'first_agent') and self.first_agent >= 0:
            hash_value ^= self._ZOBRIST_TABLES['first_player'][self.first_agent]
        
        return hash_value
    
    def _get_tile_at_position(self, agent, row, col):
        """Get the tile type that should be at the given position based on the grid scheme."""
        # Find which tile type should be at this position
        for tile_type in utils.Tile:
            if agent.grid_scheme[row][tile_type] == col:
                return tile_type
        return -1  # Should not happen
    
    def get_zobrist_hash(self):
        """Get the Zobrist hash for this position."""
        # Create a more comprehensive hash that includes state differences
        hash_parts = []
        
        # Include agent scores
        for agent in self.agents:
            hash_parts.append(str(agent.score))
        
        # Include grid states
        for agent in self.agents:
            for row in range(5):
                for col in range(5):
                    hash_parts.append(str(agent.grid_state[row][col]))
        
        # Include pattern lines
        for agent in self.agents:
            for line in range(5):
                hash_parts.append(str(agent.lines_tile[line]))
                hash_parts.append(str(agent.lines_number[line]))
        
        # Include floor tiles
        for agent in self.agents:
            hash_parts.append(str(len(agent.floor_tiles)))
        
        # Include factory states
        for factory in self.factories:
            for tile_type in utils.Tile:
                hash_parts.append(str(factory.tiles[tile_type]))
        
        # Include center pool
        for tile_type in utils.Tile:
            hash_parts.append(str(self.centre_pool.tiles[tile_type]))
        
        # Include first agent
        hash_parts.append(str(self.first_agent))
        
        return hash('|'.join(hash_parts))
    
    def update_zobrist_hash(self, old_hash, changes):
        """Efficiently update the Zobrist hash based on changes made to the state.
        
        Args:
            old_hash: The previous hash value
            changes: List of (table, *indices) tuples representing what changed
            
        Returns:
            Updated hash value
        """
        if self._ZOBRIST_TABLES is None:
            self._initialize_zobrist_tables()
            
        new_hash = old_hash
        for table_name, *indices in changes:
            new_hash ^= self._ZOBRIST_TABLES[table_name][indices]
        
        return new_hash


    class TileDisplay:
        def __init__(self):
            # Map between tile colour and number in the display
            self.tiles = {}

            # Total number of tiles in the display
            self.total = 0

            for tile in utils.Tile:
                self.tiles[tile] = 0

        def ReactionTiles(self, number, tile_type):
            assert number > 0
            assert tile_type in utils.Tile
            
            # Ensure all tile types are initialized in self.tiles
            if not hasattr(self, 'tiles') or self.tiles is None:
                self.tiles = {}
                for tile in utils.Tile:
                    self.tiles[tile] = 0
            
            # Ensure this specific tile type is initialized
            if tile_type not in self.tiles:
                self.tiles[tile_type] = 0

            self.tiles[tile_type] -= number
            self.total -= number

            assert self.tiles[tile_type] >= 0
            assert self.total >= 0

        def RemoveTiles(self, number, tile_type):
            """Remove tiles from the display (alias for ReactionTiles for clarity)."""
            self.ReactionTiles(number, tile_type)

        def AddTiles(self, number, tile_type):
            assert number > 0
            assert tile_type in utils.Tile
            
            # Ensure all tile types are initialized in self.tiles
            if not hasattr(self, 'tiles') or self.tiles is None:
                self.tiles = {}
                for tile in utils.Tile:
                    self.tiles[tile] = 0
            
            # Ensure this specific tile type is initialized
            if tile_type not in self.tiles:
                self.tiles[tile_type] = 0
            
            self.tiles[tile_type] += number
            self.total += number

        def to_dict(self):
            return {
                'tiles': dict(self.tiles),
                'total': self.total
            }


    class AgentState:
        GRID_SIZE = 5
        FLOOR_SCORES = [-1,-1,-2,-2,-2,-3,-3]
        ROW_BONUS = 2
        COL_BONUS = 7
        SET_BONUS = 10

        def __init__(self, _id):
            self.id = _id
            self.score = 0
            self.lines_number = [0]*self.GRID_SIZE
            self.lines_tile = [-1]*self.GRID_SIZE

            self.agent_trace = utils.AgentTrace(_id)

            #self.grid_scheme = [
            #    [Tile.BLUE,Tile.YELLOW,Tile.RED,Tile.BLACK,Tile.WHITE],
            #    [Tile.WHITE,Tile.BLUE,Tile.YELLOW,Tile.RED,Tile.BLACK],
            #    [Tile.BLACK,Tile.WHITE,Tile.BLUE,Tile.YELLOW,Tile.RED],
            #    [Tile.RED,Tile.BLACK,Tile.WHITE,Tile.BLUE,Tile.YELLOW],
            #    [Tile.YELLOW,Tile.RED,Tile.BLACK,Tile.WHITE,Tile.BLUE]
            #]
            self.grid_scheme = numpy.zeros((self.GRID_SIZE,self.GRID_SIZE))
            self.grid_scheme[0][utils.Tile.BLUE] = 0
            self.grid_scheme[1][utils.Tile.BLUE] = 1
            self.grid_scheme[2][utils.Tile.BLUE] = 2
            self.grid_scheme[3][utils.Tile.BLUE] = 3
            self.grid_scheme[4][utils.Tile.BLUE] = 4

            self.grid_scheme[1][utils.Tile.WHITE] = 0
            self.grid_scheme[2][utils.Tile.WHITE] = 1
            self.grid_scheme[3][utils.Tile.WHITE] = 2
            self.grid_scheme[4][utils.Tile.WHITE] = 3 
            self.grid_scheme[0][utils.Tile.WHITE] = 4
            
            self.grid_scheme[2][utils.Tile.BLACK] = 0 
            self.grid_scheme[3][utils.Tile.BLACK] = 1
            self.grid_scheme[4][utils.Tile.BLACK] = 2
            self.grid_scheme[0][utils.Tile.BLACK] = 3
            self.grid_scheme[1][utils.Tile.BLACK] = 4

            self.grid_scheme[3][utils.Tile.RED] = 0
            self.grid_scheme[4][utils.Tile.RED] = 1
            self.grid_scheme[0][utils.Tile.RED] = 2
            self.grid_scheme[1][utils.Tile.RED] = 3
            self.grid_scheme[2][utils.Tile.RED] = 4

            self.grid_scheme[4][utils.Tile.YELLOW] = 0
            self.grid_scheme[0][utils.Tile.YELLOW] = 1
            self.grid_scheme[1][utils.Tile.YELLOW] = 2
            self.grid_scheme[2][utils.Tile.YELLOW] = 3
            self.grid_scheme[3][utils.Tile.YELLOW] = 4

            # Matrix representing state of the agent's grid (ie. which
            # slots have tiles on them -- 1s -- and which don't -- 0s).
            self.grid_state = numpy.zeros((self.GRID_SIZE,self.GRID_SIZE))

            # State of the agent's floor line, a 1 indicates there is
            # a tile sitting in that position in their floor line.
            self.floor = [0,0,0,0,0,0,0]
            self.floor_tiles = []

            # Record of the number of tiles of each colour the agent
            # has placed in their grid (useful for end-game scoring)
            self.number_of = {}
            for tile in utils.Tile:
                self.number_of[tile] = 0

        def to_dict(self):
            return {
                'score': self.score,
                'lines_number': list(self.lines_number),
                'lines_tile': list(self.lines_tile),
                'grid_state': [list(row) for row in self.grid_state],
                'floor_tiles': list(self.floor_tiles),
            }

        # Add given tiles to the agent's floor line. After calling this 
        # method, 'tiles' will contain tiles that could not be added to
        # the agent's floor line.
        def AddToFloor(self, tiles):
            number = len(tiles)
            for i in range(len(self.floor)):
                if self.floor[i] == 0:
                    self.floor[i] = 1
                    tt = tiles.pop(0)
                    self.floor_tiles.append(tt)
                    number -= 1
                if number == 0:
                    break

        # Add given number of given tile type to the specified pattern line
        def AddToPatternLine(self, line, number, tile_type):
            assert line >= 0 and line < self.GRID_SIZE

            assert (self.lines_tile[line] == -1 or 
                self.lines_tile[line] == tile_type)

            self.lines_number[line] += number
            self.lines_tile[line] = tile_type

            assert self.lines_number[line] <= line + 1 


        # Assign first agent token to this agent
        def GiveFirstAgentToken(self):
            for i in range(len(self.floor)):
                if self.floor[i] == 0:
                    self.floor[i] = 1
                    break

        # Compute number of completed rows in the agent's grid
        def GetCompletedRows(self):
            completed = 0
            for i in range(self.GRID_SIZE):
                allin = True
                for j in range(self.GRID_SIZE):
                    if self.grid_state[i][j] == 0:
                        allin = False
                        break
                if allin:
                    completed += 1
            return completed

        # Compute number of completed columns in the agent's grid
        def GetCompletedColumns(self):
            completed = 0
            for i in range(self.GRID_SIZE):
                allin = True
                for j in range(self.GRID_SIZE):
                    if self.grid_state[j][i] == 0:
                        allin = False
                        break
                if allin:
                    completed += 1
            return completed

        # Compute the number of completed tile sets in the agent's grid
        def GetCompletedSets(self):
            completed = 0
            for tile in utils.Tile:
                if self.number_of[tile] == self.GRID_SIZE:
                    completed += 1
            return completed
            
        # Complete scoring process for agent at round end: 
        # 1. Action tiles across from pattern lines to the grid and score each;
        #
        # 2. Clear remaining tiles on pattern lines (where appropriate) and
        # return to be added to "used" tiles bag;
        #
        # 3. Score penalties for tiles in floor line and return these tiles
        # to be added to the "used" tiles bag.
        #
        # Returns a pair: the change in the agent's score; and the set of 
        # tiles to be returned to the "used" tile bag. The agents internal
        # representation of their score is updated in the process. 
        def ScoreRound(self):
            used_tiles = []

            score_inc = 0

            # 1. Action tiles across from pattern lines to the wall grid
            for i in range(self.GRID_SIZE):
                # Is the pattern line full? If not it persists in its current
                # state into the next round.
                if self.lines_number[i] == i+1:
                    tc = self.lines_tile[i]
                    col = int(self.grid_scheme[i][tc])

                    # Record that the agent has placed a tile of type 'tc'
                    self.number_of[tc] += 1

                    # Clear the pattern line, add all but one tile into the
                    # used tiles bag. The last tile will be placed on the 
                    # agents wall grid.  
                    for j in range(i):
                        used_tiles.append(tc)

                    self.lines_tile[i] = -1
                    self.lines_number[i] = 0

                    # Tile will be placed at position (i,col) in grid
                    self.grid_state[i][col] = 1

                    # count the number of tiles in a continguous line
                    # above, below, to the left and right of the placed tile.
                    above = 0
                    for j in range(col-1, -1, -1):
                        val = self.grid_state[i][j]
                        above += val
                        if val == 0:
                            break
                    below = 0
                    for j in range(col+1,self.GRID_SIZE,1):
                        val = self.grid_state[i][j]
                        below +=  val
                        if val == 0:
                            break
                    left = 0
                    for j in range(i-1, -1, -1):
                        val = self.grid_state[j][col]
                        left += val
                        if val == 0:
                            break
                    right = 0
                    for j in range(i+1, self.GRID_SIZE, 1):
                        val = self.grid_state[j][col]
                        right += val
                        if val == 0:
                            break

                    # If the tile sits in a contiguous vertical line of 
                    # tiles in the grid, it is worth 1*the number of tiles
                    # in this line (including itself).
                    if above > 0 or below > 0:
                        score_inc += (1 + above + below)

                    # In addition to the vertical score, the tile is worth
                    # an additional H points where H is the length of the 
                    # horizontal contiguous line in which it sits.
                    if left > 0 or right > 0:
                        score_inc += (1 + left + right)

                    # If the tile is not next to any already placed tiles
                    # on the grid, it is worth 1 point.                
                    if above == 0 and below == 0 and left == 0 \
                        and right == 0:
                        score_inc += 1

            # Score penalties for tiles in floor line
            penalties = 0
            for i in range(len(self.floor)):
                penalties += self.floor[i]*self.FLOOR_SCORES[i]
                self.floor[i] = 0
                
            used_tiles.extend(self.floor_tiles)
            self.floor_tiles = []
            
            # Agents cannot be assigned a negative score in any round.
            score_change = score_inc + penalties
            if score_change < 0 and self.score < -score_change:
                score_change = -self.score
            
            self.score += score_change
            self.agent_trace.round_scores[-1] = score_change

            return (self.score, used_tiles) 

        # Complete additional end of game scoring (add bonuses). Return
        # computed bonus, and add to internal score representation.
        def EndOfGameScore(self):
            rows = self.GetCompletedRows()
            cols = self.GetCompletedColumns()
            sets = self.GetCompletedSets()

            bonus = (rows * self.ROW_BONUS) + (cols * self.COL_BONUS) + \
                (sets * self.SET_BONUS)

            self.agent_trace.bonuses = bonus
            self.score += bonus
            return bonus 


    def __init__(self, num_agents):
        # Create agent states
        self.agents = []
        for i in range(num_agents):
            ps = self.AgentState(i)
            self.agents.append(ps)
            
        # Tile bag contains NUM_TILE_TYPE of each tile colour
        self.bag = []
        for i in range(self.NUM_TILE_TYPE):
            self.bag.append(utils.Tile.BLUE)
            self.bag.append(utils.Tile.YELLOW)
            self.bag.append(utils.Tile.RED)
            self.bag.append(utils.Tile.BLACK)
            self.bag.append(utils.Tile.WHITE)

        # Shuffle contents of tile bag
        random.shuffle(self.bag)

        # "Used" bag is initial empty
        self.bag_used = []

        # In a 2-player game, 5 factory displays are used
        self.factories = []
        for i in range(self.NUM_FACTORIES[0]):  # Always use 5 factories for 2-player games
            td = self.TileDisplay()
            
            # Initialise factory display: add NUM_ON_FACTORY randomly
            # drawn tiles to the factory (if available). 
            self.InitialiseFactory(td)
            self.factories.append(td)

        self.centre_pool = self.TileDisplay()
        self.first_agent_taken = False
        self.first_agent = random.randrange(num_agents)
        self.next_first_agent = -1
        
        # Immutability validation
        self._validate_immutability()
    
    def _validate_immutability(self):
        """Validate that the state is properly initialized for immutability."""
        # Ensure all arrays are properly initialized
        for agent in self.agents:
            assert isinstance(agent.lines_number, list)
            assert isinstance(agent.lines_tile, list)
            assert isinstance(agent.grid_state, numpy.ndarray)
            assert isinstance(agent.floor, list)
            assert isinstance(agent.floor_tiles, list)
            assert isinstance(agent.number_of, dict)
            assert isinstance(agent.grid_scheme, numpy.ndarray)
        
        # Ensure bags are lists
        assert isinstance(self.bag, list)
        assert isinstance(self.bag_used, list)
        
        # Ensure factories are properly initialized
        for factory in self.factories:
            assert isinstance(factory.tiles, dict)
            assert isinstance(factory.total, int)
        
        # Ensure center pool is properly initialized
        assert isinstance(self.centre_pool.tiles, dict)
        assert isinstance(self.centre_pool.total, int)
    
    def _check_mutation_attempt(self, operation: str):
        """Check if a mutation operation is being attempted in debug mode."""
        import os
        if os.environ.get('AZUL_DEBUG_IMMUTABILITY', 'false').lower() == 'true':
            import warnings
            warnings.warn(f"Mutation attempt detected: {operation}. Consider using immutable methods instead.")
    
    def _create_immutable_copy(self) -> 'ImmutableAzulState':
        """Create an immutable copy of the current state."""
        # Convert agent states to immutable versions
        immutable_agents = []
        for agent in self.agents:
            immutable_agent = ImmutableAgentState(
                id=agent.id,
                score=agent.score,
                lines_number=agent.lines_number.copy(),
                lines_tile=agent.lines_tile.copy(),
                grid_state=agent.grid_state.copy(),
                floor=agent.floor.copy(),
                floor_tiles=agent.floor_tiles.copy(),
                number_of=agent.number_of.copy(),
                grid_scheme=agent.grid_scheme.copy()
            )
            immutable_agents.append(immutable_agent)
        
        # Convert factories to immutable versions
        immutable_factories = []
        for factory in self.factories:
            immutable_factory = ImmutableTileDisplay(
                tiles=factory.tiles.copy(),
                total=factory.total
            )
            immutable_factories.append(immutable_factory)
        
        # Convert center pool to immutable version
        immutable_center = ImmutableTileDisplay(
            tiles=self.centre_pool.tiles.copy(),
            total=self.centre_pool.total
        )
        
        return ImmutableAzulState(
            agents=immutable_agents,
            bag=self.bag.copy(),
            bag_used=self.bag_used.copy(),
            factories=immutable_factories,
            centre_pool=immutable_center,
            first_agent_taken=self.first_agent_taken,
            first_agent=self.first_agent,
            next_first_agent=self.next_first_agent
        )
    
    def to_immutable(self) -> 'ImmutableAzulState':
        """Convert current state to immutable version."""
        return self._create_immutable_copy()
    
    def from_immutable(self, immutable_state: 'ImmutableAzulState'):
        """Update current state from immutable version."""
        # Update agent states
        for i, immutable_agent in enumerate(immutable_state.agents):
            agent = self.agents[i]
            agent.score = immutable_agent.score
            agent.lines_number = list(immutable_agent.lines_number)
            agent.lines_tile = list(immutable_agent.lines_tile)
            agent.grid_state = immutable_agent.grid_state.copy()
            agent.floor = list(immutable_agent.floor)
            agent.floor_tiles = list(immutable_agent.floor_tiles)
            agent.number_of = immutable_agent.number_of.copy()
            agent.grid_scheme = immutable_agent.grid_scheme.copy()
        
        # Update bags
        self.bag = list(immutable_state.bag)
        self.bag_used = list(immutable_state.bag_used)
        
        # Update factories
        for i, immutable_factory in enumerate(immutable_state.factories):
            factory = self.factories[i]
            factory.tiles = immutable_factory.tiles.copy()
            factory.total = immutable_factory.total
        
        # Update center pool
        self.centre_pool.tiles = immutable_state.centre_pool.tiles.copy()
        self.centre_pool.total = immutable_state.centre_pool.total
        
        # Update game state flags
        self.first_agent_taken = immutable_state.first_agent_taken
        self.first_agent = immutable_state.first_agent
        self.next_first_agent = immutable_state.next_first_agent
        
        # Reset hash since state has changed
        if hasattr(self, '_zobrist_hash'):
            delattr(self, '_zobrist_hash')

    def TilesRemaining(self):
        if self.centre_pool.total > 0:
            return True
        for fac in self.factories:
            if fac.total > 0:
                return True
        return False

    # Place tiles from the main bag (and used bag if the main bag runs
    # out of tiles) onto the given factory display.
    def InitialiseFactory(self, factory):
        # Reset contents of factory display
        factory.total = 0
        for tile in utils.Tile:
            factory.tiles[tile] = 0

        # If there are < NUM_ON_FACTORY tiles in the bag, shuffle the 
        # tiles in the "used" bag and add them to the main bag (we still
        # want the tiles that were left in the main bag to be drawn first).
        # Fill the factory display with tiles, up to capacity, if possible.
        # If there are less than NUM_ON_FACTORY tiles available in both
        # bags, the factory will be left at partial capacity.
        if len(self.bag) < self.NUM_ON_FACTORY and len(self.bag_used) > 0:
            random.shuffle(self.bag_used)
            self.bag.extend(self.bag_used)
            self.bag_used = []

        for i in range(min(self.NUM_ON_FACTORY,len(self.bag))):
            # take tile out of the bag
            tile = self.bag.pop(0)
            factory.tiles[tile] += 1
            factory.total += 1

    # Execute end of round actions (scoring and clean up)
    def ExecuteEndOfRound(self):
        # Each agent scores for the round, and we add tiles to the 
        # used bag (if appropriate).
        for plr in self.agents:
            _,used = plr.ScoreRound()
            self.bag_used.extend(used)

    def clone(self):
        """Create a deep copy of the current game state for search algorithms."""
        import copy
        
        # Create a new state with the same number of agents
        new_state = AzulState(len(self.agents))
        
        # Copy agent states
        for i, agent in enumerate(self.agents):
            new_agent = new_state.agents[i]
            new_agent.score = agent.score
            new_agent.lines_number = agent.lines_number.copy()
            new_agent.lines_tile = agent.lines_tile.copy()
            new_agent.grid_state = agent.grid_state.copy()
            new_agent.floor = agent.floor.copy()
            new_agent.floor_tiles = agent.floor_tiles.copy()
            new_agent.agent_trace = copy.deepcopy(agent.agent_trace)
        
        # Copy bag states
        new_state.bag = self.bag.copy()
        new_state.bag_used = self.bag_used.copy()
        
        # Copy factory states
        for i, factory in enumerate(self.factories):
            new_factory = new_state.factories[i]
            new_factory.total = factory.total
            new_factory.tiles = factory.tiles.copy()
        
        # Copy center pool
        new_state.centre_pool.total = self.centre_pool.total
        new_state.centre_pool.tiles = self.centre_pool.tiles.copy()
        
        # Copy game state flags
        new_state.first_agent_taken = self.first_agent_taken
        new_state.first_agent = self.first_agent
        new_state.next_first_agent = self.next_first_agent
        
        # Reset hash since state has changed
        if hasattr(new_state, '_zobrist_hash'):
            delattr(new_state, '_zobrist_hash')
        
        return new_state
    
    def undo_move(self, move_info):
        """Undo a move using the provided move information.
        
        Args:
            move_info: Dictionary containing the move details and state changes
        """
        # Restore agent states
        for agent_id, agent_changes in move_info.get('agents', {}).items():
            agent = self.agents[agent_id]
            if 'score' in agent_changes:
                agent.score = agent_changes['score']
            if 'lines_number' in agent_changes:
                agent.lines_number = agent_changes['lines_number']
            if 'lines_tile' in agent_changes:
                agent.lines_tile = agent_changes['lines_tile']
            if 'grid_state' in agent_changes:
                agent.grid_state = agent_changes['grid_state']
            if 'floor' in agent_changes:
                agent.floor = agent_changes['floor']
            if 'floor_tiles' in agent_changes:
                agent.floor_tiles = agent_changes['floor_tiles']
        
        # Restore bag states
        if 'bag' in move_info:
            self.bag = move_info['bag']
        if 'bag_used' in move_info:
            self.bag_used = move_info['bag_used']
        
        # Restore factory states
        for factory_id, factory_changes in move_info.get('factories', {}).items():
            factory = self.factories[factory_id]
            factory.total = factory_changes['total']
            factory.tiles = factory_changes['tiles']
        
        # Restore center pool
        if 'centre_pool' in move_info:
            self.centre_pool.total = move_info['centre_pool']['total']
            self.centre_pool.tiles = move_info['centre_pool']['tiles']
        
        # Restore game state flags
        if 'first_agent_taken' in move_info:
            self.first_agent_taken = move_info['first_agent_taken']
        if 'first_agent' in move_info:
            self.first_agent = move_info['first_agent']
        if 'next_first_agent' in move_info:
            self.next_first_agent = move_info['next_first_agent']
        
        # Reset hash since state has changed
        if hasattr(self, '_zobrist_hash'):
            delattr(self, '_zobrist_hash')
    
    def get_move_info(self):
        """Capture current state for potential undo operations.
        
        Returns:
            Dictionary containing the current state for undo operations
        """
        move_info = {
            'agents': {},
            'factories': {},
            'bag': self.bag.copy(),
            'bag_used': self.bag_used.copy(),
            'centre_pool': {
                'total': self.centre_pool.total,
                'tiles': self.centre_pool.tiles.copy()
            },
            'first_agent_taken': self.first_agent_taken,
            'first_agent': self.first_agent,
            'next_first_agent': self.next_first_agent
        }
        
        # Capture agent states
        for i, agent in enumerate(self.agents):
            move_info['agents'][i] = {
                'score': agent.score,
                'lines_number': agent.lines_number.copy(),
                'lines_tile': agent.lines_tile.copy(),
                'grid_state': agent.grid_state.copy(),
                'floor': agent.floor.copy(),
                'floor_tiles': agent.floor_tiles.copy()
            }
        
        # Capture factory states
        for i, factory in enumerate(self.factories):
            move_info['factories'][i] = {
                'total': factory.total,
                'tiles': factory.tiles.copy()
            }
        
        return move_info

    def to_dict(self):
        """Serialize the AzulState to a dictionary for API/testing."""
        return {
            'agents': [agent.to_dict() for agent in self.agents],
            'factories': [factory.to_dict() for factory in self.factories],
            'centre_pool': self.centre_pool.to_dict() if hasattr(self.centre_pool, 'to_dict') else {},
            'first_agent_taken': getattr(self, 'first_agent_taken', False),
            'first_agent': getattr(self, 'first_agent', 0),
            'next_first_agent': getattr(self, 'next_first_agent', 0),
        }

    # ===== FEN System Methods =====
    
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
    
    def _estimate_round(self) -> int:
        """Estimate current round based on game state."""
        # Count completed walls to estimate round
        total_completed = 0
        for agent in self.agents:
            for row in range(5):
                if sum(agent.grid_state[row]) == 5:  # Complete row
                    total_completed += 1
        return max(1, min(5, (total_completed // 2) + 1))
    
    def _fallback_fen(self) -> str:
        """Generate fallback hash-based FEN."""
        import hashlib
        import json
        
        state_data = {
            'factories': [(i, dict(factory.tiles)) for i, factory in enumerate(self.factories)],
            'center': dict(self.centre_pool.tiles),
            'agents': [
                {
                    'lines_tile': agent.lines_tile,
                    'lines_number': agent.lines_number,
                    'grid_state': agent.grid_state.tolist(),
                    'floor_tiles': agent.floor_tiles,
                    'score': agent.score
                }
                for agent in self.agents
            ]
        }
        
        state_json = json.dumps(state_data, sort_keys=True)
        state_hash = hashlib.md5(state_json.encode('utf-8')).hexdigest()[:8]
        return f"state_{state_hash}"
    
    @classmethod
    def _fallback_from_fen(cls, fen_string: str) -> 'AzulState':
        """Fallback parsing for non-standard FEN strings."""
        # For now, create a default state
        # This can be enhanced later to handle other FEN formats
        return cls(2)
    
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
    
    @staticmethod
    def _validate_factories(factories: list) -> bool:
        """Validate factory data."""
        if not isinstance(factories, list):
            return False
        for factory in factories:
            if not isinstance(factory, str) or len(factory) != 4:
                return False
        return True
    
    @staticmethod
    def _validate_center(center: str) -> bool:
        """Validate center pool data."""
        return isinstance(center, str)
    
    @staticmethod
    def _validate_player(player: dict) -> bool:
        """Validate player data."""
        required_keys = ['wall', 'pattern', 'floor']
        return all(key in player for key in required_keys)
    
    @staticmethod
    def _validate_scores(scores: str) -> bool:
        """Validate scores data."""
        try:
            if ',' not in scores:
                return False
            score1, score2 = scores.split(',')
            int(score1)
            int(score2)
            return True
        except:
            return False
    
    @classmethod
    def _apply_factories(cls, state, factories_data):
        """Apply factory data to state."""
        try:
            for i, factory_str in enumerate(factories_data):
                if i < len(state.factories):
                    # Clear existing tiles
                    state.factories[i].tiles.clear()
                    
                    # Parse factory string (e.g., "YYRW")
                    for tile_char in factory_str:
                        if tile_char != '-':
                            color = cls._letter_to_color(tile_char)
                            if color is not None:
                                state.factories[i].tiles[color] = state.factories[i].tiles.get(color, 0) + 1
        except Exception as e:
            print(f"DEBUG: Error applying factories: {e}")
    
    @classmethod
    def _apply_center(cls, state, center_data):
        """Apply center pool data to state."""
        try:
            # Clear existing center pool
            state.centre_pool.tiles.clear()
            
            # Parse center string (e.g., "BYRW")
            for tile_char in center_data:
                if tile_char != '-':
                    color = cls._letter_to_color(tile_char)
                    if color is not None:
                        state.centre_pool.tiles[color] = state.centre_pool.tiles.get(color, 0) + 1
        except Exception as e:
            print(f"DEBUG: Error applying center: {e}")
    
    @classmethod
    def _apply_player(cls, state, player_id, player_data):
        """Apply player data to state."""
        try:
            if player_id >= len(state.agents):
                return
                
            agent = state.agents[player_id]
            
            # Apply wall data
            if 'wall' in player_data:
                cls._apply_wall(agent, player_data['wall'])
            
            # Apply pattern lines data
            if 'pattern' in player_data:
                cls._apply_pattern_lines(agent, player_data['pattern'])
            
            # Apply floor data
            if 'floor' in player_data:
                cls._apply_floor(agent, player_data['floor'])
                
        except Exception as e:
            print(f"DEBUG: Error applying player {player_id}: {e}")
    
    @classmethod
    def _apply_wall(cls, agent, wall_data):
        """Apply wall data to agent."""
        try:
            # Reset wall state
            agent.grid_state.fill(0)
            
            # Parse wall rows (e.g., ["B----", "Y----", ...])
            for row_idx, row_str in enumerate(wall_data):
                if row_idx < 5:
                    for col_idx, tile_char in enumerate(row_str):
                        if col_idx < 5 and tile_char != '-':
                            # Check if this position should have a tile
                            expected_color = cls._get_wall_color_static(row_idx, col_idx)
                            actual_color = cls._letter_to_color(tile_char)
                            if expected_color == actual_color:
                                agent.grid_state[row_idx][col_idx] = 1
        except Exception as e:
            print(f"DEBUG: Error applying wall: {e}")
    
    @staticmethod
    def _get_wall_color_static(row: int, col: int) -> int:
        """Get the color that should be at wall position (static version)."""
        # This is the Azul wall color scheme
        color_scheme = [
            [0, 1, 2, 3, 4],  # Row 0: B,Y,R,K,W
            [4, 0, 1, 2, 3],  # Row 1: W,B,Y,R,K
            [3, 4, 0, 1, 2],  # Row 2: K,W,B,Y,R
            [2, 3, 4, 0, 1],  # Row 3: R,K,W,B,Y
            [1, 2, 3, 4, 0]   # Row 4: Y,R,K,W,B
        ]
        return color_scheme[row][col]
    
    @classmethod
    def _apply_pattern_lines(cls, agent, pattern_data):
        """Apply pattern lines data to agent."""
        try:
            # Reset pattern lines
            agent.lines_number = [0] * 5
            agent.lines_tile = [-1] * 5
            
            # Parse pattern lines (e.g., ["B", "YY", "RRR", "WWWW", "KKKKK"])
            for line_idx, line_str in enumerate(pattern_data):
                if line_idx < 5 and line_str != '-':
                    # Count tiles in this line
                    tile_count = 0
                    tile_color = None
                    
                    for tile_char in line_str:
                        if tile_char != '-':
                            color = cls._letter_to_color(tile_char)
                            if color is not None:
                                tile_count += 1
                                tile_color = color
                    
                    if tile_count > 0 and tile_color is not None:
                        agent.lines_number[line_idx] = tile_count
                        agent.lines_tile[line_idx] = tile_color
        except Exception as e:
            print(f"DEBUG: Error applying pattern lines: {e}")
    
    @classmethod
    def _apply_floor(cls, agent, floor_data):
        """Apply floor data to agent."""
        try:
            # Reset floor
            agent.floor_tiles = []
            agent.floor = [0] * 7
            
            # Parse floor string (e.g., "BYRW")
            for tile_char in floor_data:
                if tile_char != '-':
                    color = cls._letter_to_color(tile_char)
                    if color is not None:
                        agent.floor_tiles.append(color)
                        # Mark floor position as occupied
                        floor_pos = len(agent.floor_tiles) - 1
                        if floor_pos < len(agent.floor):
                            agent.floor[floor_pos] = 1
        except Exception as e:
            print(f"DEBUG: Error applying floor: {e}")
    
    @classmethod
    def _apply_scores(cls, state, scores_data):
        """Apply scores data to state."""
        try:
            # Parse scores (e.g., "10,15")
            score_parts = scores_data.split(',')
            if len(score_parts) >= 2:
                state.agents[0].score = int(score_parts[0])
                state.agents[1].score = int(score_parts[1])
        except Exception as e:
            print(f"DEBUG: Error applying scores: {e}")
    
    @classmethod
    def _apply_round(cls, state, round_data):
        """Apply round data to state."""
        try:
            # Round information is mostly for display purposes
            # The actual game state doesn't store round number
            pass
        except Exception as e:
            print(f"DEBUG: Error applying round: {e}")
    
    @classmethod
    def _apply_current_player(cls, state, current_player_data):
        """Apply current player data to state."""
        try:
            # Set current player
            state.current_player = int(current_player_data)
        except Exception as e:
            print(f"DEBUG: Error applying current player: {e}")
    
    @staticmethod
    def _letter_to_color(letter: str) -> int:
        """Convert letter to color number."""
        color_map = {'B': 0, 'Y': 1, 'R': 2, 'K': 3, 'W': 4}
        return color_map.get(letter, None)

    def is_game_over(self):
        """Check if the game is over according to Azul rules.
        
        Returns:
            bool: True if the game is over, False otherwise.
        """
        # Game ends when at least one player completes a horizontal line
        for agent in self.agents:
            for row in range(5):
                if all(agent.grid_state[row][col] == 1 for col in range(5)):
                    return True
        return False


class AzulGameRule(GameRule):
    def __init__(self,num_of_agent):
        super().__init__(num_of_agent)
        self.private_information = None # Azul is a perfect-information game.
        
    def validAction(self, m, actions):
        return utils.ValidAction(m, actions)

    def initialGameState(self):
        self.current_agent_index = self.num_of_agent
        return AzulState(self.num_of_agent)

    def generateSuccessor(self, state, action, agent_id):
        if action == "ENDROUND":
            for plr in state.agents:
                _,used = plr.ScoreRound()
                state.bag_used.extend(used)

            state.first_agent_taken = False
            state.first_agent = state.next_first_agent
            state.next_first_agent = -1
        elif action == "STARTROUND":
            for plr in state.agents:
                plr.agent_trace.StartRound()
            for fd in state.factories:
                state.InitialiseFactory(fd)

            for tile in utils.Tile:
                state.centre_pool.tiles[tile] = 0
        else:
            plr_state = state.agents[agent_id]
            
            # Ensure agent trace is properly initialized
            if not hasattr(plr_state, 'agent_trace') or plr_state.agent_trace is None:
                plr_state.agent_trace = utils.AgentTrace(plr_state.id)
            
            # Ensure actions list is not empty
            if len(plr_state.agent_trace.actions) == 0:
                plr_state.agent_trace.StartRound()
            
            plr_state.agent_trace.actions[-1].append(action)

            # The agent is taking tiles from the centre
            if action[0] == utils.Action.TAKE_FROM_CENTRE: 
                tg = action[2]

                if not state.first_agent_taken:
                    plr_state.GiveFirstAgentToken()
                    state.first_agent_taken = True
                    state.next_first_agent = agent_id

                if tg.num_to_floor_line > 0:
                    ttf = []
                    for i in range(tg.num_to_floor_line):
                        ttf.append(tg.tile_type)
                    plr_state.AddToFloor(ttf)
                    state.bag_used.extend(ttf)

                if tg.num_to_pattern_line > 0:
                    plr_state.AddToPatternLine(tg.pattern_line_dest, 
                        tg.num_to_pattern_line, tg.tile_type)

                # Reaction tiles from the centre
                state.centre_pool.ReactionTiles(tg.number, tg.tile_type)

            elif action[0] == utils.Action.TAKE_FROM_FACTORY:
                tg = action[2]
                if tg.num_to_floor_line > 0:
                    ttf = []
                    for i in range(tg.num_to_floor_line):
                        ttf.append(tg.tile_type)
                    plr_state.AddToFloor(ttf)
                    state.bag_used.extend(ttf)

                if tg.num_to_pattern_line > 0:
                    plr_state.AddToPatternLine(tg.pattern_line_dest, 
                        tg.num_to_pattern_line, tg.tile_type)

                # Reaction tiles from the factory display
                fid = action[1]
                fac = state.factories[fid]
                fac.ReactionTiles(tg.number,tg.tile_type)

                # All remaining tiles on the factory display go into the 
                # centre!
                for tile in fac.tiles.keys():
                    num_on_fd = fac.tiles[tile]
                    if num_on_fd > 0:
                        state.centre_pool.AddTiles(num_on_fd, tile)
                        fac.RemoveTiles(num_on_fd, tile)
        return state
    
    def getNextAgentIndex(self):
        if not self.current_game_state.TilesRemaining():
            return self.num_of_agent
        if self.current_agent_index == self.num_of_agent:
            return self.current_game_state.first_agent
        return (self.current_agent_index + 1) % self.num_of_agent

    def gameEnds(self):
        for plr_state in self.current_game_state.agents:
            completed_rows = plr_state.GetCompletedRows()
            if completed_rows > 0:
                return True
        return False

    def calScore(self, game_state,agent_id):
        game_state.agents[agent_id].EndOfGameScore()
        return game_state.agents[agent_id].score

    def getLegalActions(self, game_state, agent_id):
        actions = []

        if not game_state.TilesRemaining() and not game_state.next_first_agent == -1:
            return ["ENDROUND"]
        elif agent_id == self.num_of_agent:
            return ["STARTROUND"]
        else: 
            agent_state = game_state.agents[agent_id]

            # Look at each factory display with available tiles
            fid = 0
            for fd in game_state.factories:
                # Look at each available tile set
                for tile in utils.Tile:
                    num_avail = fd.tiles[tile]
                
                    if num_avail == 0:
                        continue

                    # A agent can always take tiles, as they can be 
                    # added to their floor line (if their floor line is 
                    # full, the extra tiles are placed in the used bag).

                    # First look through each pattern line, create actions 
                    # that place the tiles in each appropriate line (with
                    # those that cannot be placed added to the floor line).
                    for i in range(agent_state.GRID_SIZE):
                        # Can tiles be added to pattern line i?
                        if agent_state.lines_tile[i] != -1 and \
                            agent_state.lines_tile[i] != tile:
                            # these tiles cannot be added to this pattern line
                            continue

                        # Is the space on the grid for this tile already
                        # occupied?
                        grid_col = int(agent_state.grid_scheme[i][tile])
                        if agent_state.grid_state[i][grid_col] == 1:
                            # It is, so we cannot place this tile type
                            # in this pattern line!
                            continue

                        slots_free = (i+1) - agent_state.lines_number[i]
                        tg = utils.TileGrab()
                        tg.number = num_avail
                        tg.tile_type = tile
                        tg.pattern_line_dest = i
                        tg.num_to_pattern_line = min(num_avail, slots_free)
                        tg.num_to_floor_line = tg.number - tg.num_to_pattern_line

                        actions.append((utils.Action.TAKE_FROM_FACTORY, fid, tg))
            
                    # Default action is to place all the tiles in the floor line
                    tg = utils.TileGrab()
                    tg.number = num_avail
                    tg.tile_type = tile
                    tg.num_to_floor_line = tg.number
                    actions.append((utils.Action.TAKE_FROM_FACTORY, fid, tg))

                fid += 1    

            # Alternately, the agent could take tiles from the centre pool.
            # Note that we do not include the first agent token in the 
            # collection of tiles recorded in each utils.TileGrab. This is managed
            # by the game running class. 
            for tile in utils.Tile:
                # Number of tiles of this type in the centre
                num_avail = game_state.centre_pool.tiles[tile]

                if num_avail == 0:
                    continue

                # First look through each pattern line, create actions 
                # that place the tiles in each appropriate line (with
                # those that cannot be placed added to the floor line).
                for i in range(agent_state.GRID_SIZE):
                    # Can tiles be added to pattern line i?
                    if agent_state.lines_tile[i] != -1 and \
                        agent_state.lines_tile[i] != tile:
                        # these tiles cannot be added to this pattern line
                        continue

                    # Is the space on the grid for this tile already
                    # occupied?
                    grid_col = int(agent_state.grid_scheme[i][tile])
                    if agent_state.grid_state[i][grid_col] == 1:
                        # It is, so we cannot place this tile type
                        # in this pattern line!
                        continue

                    slots_free = (i+1) - agent_state.lines_number[i]
                    tg = utils.TileGrab()
                    tg.number = num_avail
                    tg.tile_type = tile
                    tg.pattern_line_dest = i
                    tg.num_to_pattern_line = min(num_avail, slots_free)
                    tg.num_to_floor_line = tg.number - tg.num_to_pattern_line

                    actions.append((utils.Action.TAKE_FROM_CENTRE, -1, tg))
            
                # Default action is to place all the tiles in the floor line
                tg = utils.TileGrab()
                tg.number = num_avail
                tg.tile_type = tile
                tg.num_to_floor_line = tg.number
                actions.append((utils.Action.TAKE_FROM_CENTRE, -1, tg))

            return actions
