#!/usr/bin/env python3
"""
Generate Diverse Positions - Simplified Version

This script generates diverse Azul positions for move quality analysis.
Simplified to work reliably with the actual AzulState structure.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import random
import json
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

from core.azul_model import AzulState, AzulGameRule

class GamePhase(Enum):
    """Game phases for position generation."""
    OPENING = "opening"
    MIDDLEGAME = "middlegame"
    ENDGAME = "endgame"

class StrategicScenario(Enum):
    """Strategic scenarios for position generation."""
    BLOCKING = "blocking"
    SCORING = "scoring"
    FLOOR_LINE = "floor_line"
    WALL_COMPLETION = "wall_completion"
    RISK_MANAGEMENT = "risk_management"
    FACTORY_CONTROL = "factory_control"

@dataclass
class PositionSpecification:
    """Specification for generating a specific type of position."""
    name: str
    description: str
    game_phase: GamePhase
    strategic_scenario: StrategicScenario
    target_count: int
    complexity_score: float  # 0.0 to 1.0
    risk_level: float  # 0.0 to 1.0
    tags: List[str]

class SimplePositionGenerator:
    """Generates diverse positions for comprehensive move quality analysis."""
    
    def __init__(self):
        self.game_rule = AzulGameRule(2)  # 2-player game
        
        # Define position specifications
        self.position_specs = self._define_position_specifications()
    
    def _define_position_specifications(self) -> List[PositionSpecification]:
        """Define comprehensive position specifications."""
        specs = []
        
        # Opening positions
        specs.extend([
            PositionSpecification(
                name="Early Factory Selection",
                description="Positions where players are choosing from factories with diverse tile distributions",
                game_phase=GamePhase.OPENING,
                strategic_scenario=StrategicScenario.FACTORY_CONTROL,
                target_count=10,
                complexity_score=0.2,
                risk_level=0.1,
                tags=["opening", "factory_selection"]
            ),
            PositionSpecification(
                name="Early Pattern Line Building",
                description="Positions with early pattern line development opportunities",
                game_phase=GamePhase.OPENING,
                strategic_scenario=StrategicScenario.SCORING,
                target_count=10,
                complexity_score=0.4,
                risk_level=0.2,
                tags=["opening", "pattern_building"]
            ),
            PositionSpecification(
                name="Early Blocking Opportunities",
                description="Positions with clear blocking opportunities in opening phase",
                game_phase=GamePhase.OPENING,
                strategic_scenario=StrategicScenario.BLOCKING,
                target_count=8,
                complexity_score=0.6,
                risk_level=0.3,
                tags=["opening", "blocking"]
            )
        ])
        
        # Middlegame positions
        specs.extend([
            PositionSpecification(
                name="Mid Game Blocking",
                description="Positions with multiple blocking opportunities and strategic choices",
                game_phase=GamePhase.MIDDLEGAME,
                strategic_scenario=StrategicScenario.BLOCKING,
                target_count=12,
                complexity_score=0.7,
                risk_level=0.4,
                tags=["middlegame", "blocking"]
            ),
            PositionSpecification(
                name="Mid Game Scoring Optimization",
                description="Positions with scoring opportunities and wall completion setups",
                game_phase=GamePhase.MIDDLEGAME,
                strategic_scenario=StrategicScenario.SCORING,
                target_count=10,
                complexity_score=0.8,
                risk_level=0.5,
                tags=["middlegame", "scoring"]
            ),
            PositionSpecification(
                name="Floor Line Management",
                description="Positions requiring careful floor line management",
                game_phase=GamePhase.MIDDLEGAME,
                strategic_scenario=StrategicScenario.FLOOR_LINE,
                target_count=8,
                complexity_score=0.9,
                risk_level=0.8,
                tags=["middlegame", "floor_line"]
            )
        ])
        
        # Endgame positions
        specs.extend([
            PositionSpecification(
                name="Wall Completion Scenarios",
                description="Positions near wall completion with multiple scoring opportunities",
                game_phase=GamePhase.ENDGAME,
                strategic_scenario=StrategicScenario.WALL_COMPLETION,
                target_count=8,
                complexity_score=0.85,
                risk_level=0.6,
                tags=["endgame", "wall_completion"]
            ),
            PositionSpecification(
                name="Final Scoring Optimization",
                description="Endgame positions with final scoring opportunities",
                game_phase=GamePhase.ENDGAME,
                strategic_scenario=StrategicScenario.SCORING,
                target_count=6,
                complexity_score=0.9,
                risk_level=0.7,
                tags=["endgame", "final_scoring"]
            )
        ])
        
        return specs
    
    def generate_positions_for_spec(self, spec: PositionSpecification) -> List[AzulState]:
        """Generate positions for a specific specification."""
        positions = []
        
        print(f"Generating {spec.target_count} positions for: {spec.name}")
        print(f"  Phase: {spec.game_phase.value}, Scenario: {spec.strategic_scenario.value}")
        print(f"  Complexity: {spec.complexity_score:.2f}, Risk: {spec.risk_level:.2f}")
        
        for i in range(spec.target_count):
            try:
                position = self._generate_position_for_spec(spec)
                if position and self._validate_position(position):
                    positions.append(position)
                    print(f"    Generated position {i+1}/{spec.target_count}")
                else:
                    print(f"    Skipped invalid position {i+1}/{spec.target_count}")
            except Exception as e:
                print(f"    Error generating position {i+1}: {e}")
        
        return positions
    
    def _generate_position_for_spec(self, spec: PositionSpecification) -> AzulState:
        """Generate a single position for a specific specification."""
        
        # Create base state
        state = AzulState(2)  # 2-player game
        
        # Apply phase-specific modifications
        if spec.game_phase == GamePhase.OPENING:
            state = self._modify_for_opening(state, spec)
        elif spec.game_phase == GamePhase.MIDDLEGAME:
            state = self._modify_for_middlegame(state, spec)
        elif spec.game_phase == GamePhase.ENDGAME:
            state = self._modify_for_endgame(state, spec)
        
        # Apply strategic scenario modifications
        if spec.strategic_scenario == StrategicScenario.BLOCKING:
            state = self._add_blocking_scenario(state, spec)
        elif spec.strategic_scenario == StrategicScenario.SCORING:
            state = self._add_scoring_scenario(state, spec)
        elif spec.strategic_scenario == StrategicScenario.FLOOR_LINE:
            state = self._add_floor_line_scenario(state, spec)
        elif spec.strategic_scenario == StrategicScenario.WALL_COMPLETION:
            state = self._add_wall_completion_scenario(state, spec)
        elif spec.strategic_scenario == StrategicScenario.FACTORY_CONTROL:
            state = self._add_factory_control_scenario(state, spec)
        
        return state
    
    def _modify_for_opening(self, state: AzulState, spec: PositionSpecification) -> AzulState:
        """Modify state for opening phase."""
        # Add tiles to factories based on complexity
        factory_count = min(5, len(state.factories))
        tiles_per_factory = int(2 + spec.complexity_score * 3)  # 2-5 tiles per factory
        
        for factory_id in range(factory_count):
            if factory_id < len(state.factories):
                # Add diverse tile distribution
                for _ in range(tiles_per_factory):
                    tile_type = random.randint(0, 4)
                    state.factories[factory_id].AddTiles(1, tile_type)
        
        return state
    
    def _modify_for_middlegame(self, state: AzulState, spec: PositionSpecification) -> AzulState:
        """Modify state for middlegame phase."""
        # Add some pattern line progress
        self._add_pattern_line_progress(state, spec.complexity_score)
        
        # Add some wall progress
        if spec.complexity_score > 0.5:
            self._add_wall_progress(state, spec.complexity_score)
        
        # Add floor line tiles based on risk level
        if spec.risk_level > 0.3:
            self._add_floor_line_tiles(state, spec.risk_level)
        
        return state
    
    def _modify_for_endgame(self, state: AzulState, spec: PositionSpecification) -> AzulState:
        """Modify state for endgame phase."""
        # Add near-complete pattern lines
        self._add_near_complete_pattern_lines(state)
        
        # Add significant wall progress
        self._add_significant_wall_progress(state, spec.complexity_score)
        
        # Add floor line tiles
        self._add_floor_line_tiles(state, spec.risk_level)
        
        return state
    
    def _add_blocking_scenario(self, state: AzulState, spec: PositionSpecification) -> AzulState:
        """Add blocking scenario to the position."""
        # Add tiles to factories that can be used for blocking
        for factory_id in range(min(3, len(state.factories))):
            if factory_id < len(state.factories):
                # Add tiles that can block opponent progress
                for _ in range(random.randint(1, 3)):
                    tile_type = random.randint(0, 4)
                    state.factories[factory_id].AddTiles(1, tile_type)
        
        return state
    
    def _add_scoring_scenario(self, state: AzulState, spec: PositionSpecification) -> AzulState:
        """Add scoring scenario to the position."""
        # Add tiles that create scoring opportunities
        for factory_id in range(min(4, len(state.factories))):
            if factory_id < len(state.factories):
                # Add tiles that can complete pattern lines or wall sections
                for _ in range(random.randint(2, 4)):
                    tile_type = random.randint(0, 4)
                    state.factories[factory_id].AddTiles(1, tile_type)
        
        return state
    
    def _add_floor_line_scenario(self, state: AzulState, spec: PositionSpecification) -> AzulState:
        """Add floor line management scenario to the position."""
        # Add tiles to floor lines based on risk level
        for player_id in range(len(state.agents)):
            agent = state.agents[player_id]
            floor_tiles = int(spec.risk_level * 5)  # 0-5 tiles
            for _ in range(floor_tiles):
                tile_type = random.randint(0, 4)
                agent.AddToFloor([tile_type])
        
        # Add tiles to factories that might create floor line dilemmas
        for factory_id in range(min(3, len(state.factories))):
            if factory_id < len(state.factories):
                for _ in range(random.randint(1, 3)):
                    tile_type = random.randint(0, 4)
                    state.factories[factory_id].AddTiles(1, tile_type)
        
        return state
    
    def _add_wall_completion_scenario(self, state: AzulState, spec: PositionSpecification) -> AzulState:
        """Add wall completion scenario to the position."""
        # Add tiles to factories for wall completion
        for factory_id in range(min(3, len(state.factories))):
            if factory_id < len(state.factories):
                for _ in range(random.randint(2, 4)):
                    tile_type = random.randint(0, 4)
                    state.factories[factory_id].AddTiles(1, tile_type)
        
        return state
    
    def _add_factory_control_scenario(self, state: AzulState, spec: PositionSpecification) -> AzulState:
        """Add factory control scenario to the position."""
        # Add diverse tile distribution to factories
        for factory_id in range(min(4, len(state.factories))):
            if factory_id < len(state.factories):
                # Add different tile types to each factory
                tile_types = list(range(5))  # 0-4
                num_types = random.randint(2, 4)
                selected_types = random.sample(tile_types, num_types)
                for tile_type in selected_types:
                    count = random.randint(1, 2)
                    state.factories[factory_id].AddTiles(count, tile_type)
        
        return state
    
    def _add_pattern_line_progress(self, state: AzulState, complexity: float):
        """Add pattern line progress based on complexity."""
        for player_id in range(len(state.agents)):
            agent = state.agents[player_id]
            lines_to_fill = int(2 + complexity * 3)  # 2-5 lines
            for _ in range(lines_to_fill):
                line_id = random.randint(0, 4)
                tile_type = random.randint(0, 4)
                tiles_to_add = min(random.randint(1, 3), line_id + 1)
                for _ in range(tiles_to_add):
                    agent.AddToPatternLine(line_id, 1, tile_type)
    
    def _add_wall_progress(self, state: AzulState, complexity: float):
        """Add wall progress based on complexity."""
        for player_id in range(len(state.agents)):
            agent = state.agents[player_id]
            wall_positions = int(complexity * 10)  # 0-10 wall positions
            for _ in range(wall_positions):
                row = random.randint(0, 4)
                col = random.randint(0, 4)
                if agent.grid_state[row][col] == 0:  # Empty position
                    agent.grid_state[row][col] = 1
    
    def _add_floor_line_tiles(self, state: AzulState, risk_level: float):
        """Add floor line tiles based on risk level."""
        for player_id in range(len(state.agents)):
            agent = state.agents[player_id]
            floor_tiles = int(risk_level * 4)  # 0-4 tiles
            for _ in range(floor_tiles):
                tile_type = random.randint(0, 4)
                agent.AddToFloor([tile_type])
    
    def _add_near_complete_pattern_lines(self, state: AzulState):
        """Add near-complete pattern lines for endgame."""
        for player_id in range(len(state.agents)):
            agent = state.agents[player_id]
            for line_id in range(3):  # First 3 pattern lines
                if random.random() < 0.7:  # 70% chance
                    # Add tiles to make pattern lines nearly complete
                    tiles_needed = line_id + 1
                    tiles_to_add = max(1, tiles_needed - random.randint(0, 1))
                    tile_type = random.randint(0, 4)
                    for _ in range(tiles_to_add):
                        agent.AddToPatternLine(line_id, 1, tile_type)
    
    def _add_significant_wall_progress(self, state: AzulState, complexity: float):
        """Add significant wall progress for endgame."""
        for player_id in range(len(state.agents)):
            agent = state.agents[player_id]
            wall_positions = int(5 + complexity * 15)  # 5-20 wall positions
            for _ in range(wall_positions):
                row = random.randint(0, 4)
                col = random.randint(0, 4)
                if agent.grid_state[row][col] == 0:  # Empty position
                    agent.grid_state[row][col] = 1
    
    def _validate_position(self, state: AzulState) -> bool:
        """Validate that a position is suitable for analysis."""
        try:
            # Check if position has legal moves
            from analysis_engine.mathematical_optimization.azul_move_generator import FastMoveGenerator
            generator = FastMoveGenerator()
            moves = generator.generate_moves_fast(state, 0)
            
            if not moves:
                return False
            
            # Check if position is not too simple
            if len(moves) < 2:
                return False
            
            # Check if position is not too complex (for analysis purposes)
            if len(moves) > 200:
                return False
            
            # Check if there are tiles in factories
            total_tiles = sum(factory.total for factory in state.factories)
            if total_tiles == 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def generate_all_positions(self) -> List[AzulState]:
        """Generate positions for all specifications."""
        all_positions = []
        
        print("Generating diverse positions for move quality analysis...")
        print("=" * 60)
        
        for spec in self.position_specs:
            positions = self.generate_positions_for_spec(spec)
            all_positions.extend(positions)
            print(f"Generated {len(positions)} positions for {spec.name}")
            print()
        
        print(f"Total positions generated: {len(all_positions)}")
        return all_positions

def main():
    """Main function to generate diverse positions."""
    generator = SimplePositionGenerator()
    
    # Generate all positions
    positions = generator.generate_all_positions()
    
    # Save positions to file
    output_file = "../data/diverse_positions_simple.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    position_data = []
    for i, position in enumerate(positions):
        try:
            # Convert position to serializable format
            from api.utils.state_parser import state_to_fen
            fen_string = state_to_fen(position)
            
            position_data.append({
                "id": i,
                "fen_string": fen_string,
                "description": f"Generated position {i+1}",
                "created_at": time.time()
            })
        except Exception as e:
            print(f"Error serializing position {i}: {e}")
    
    with open(output_file, 'w') as f:
        json.dump(position_data, f, indent=2)
    
    print(f"✅ Generated {len(positions)} diverse positions")
    print(f"📁 Saved to: {output_file}")
    print(f"🔧 Next step: Run move quality analysis on these positions")

if __name__ == "__main__":
    main()
