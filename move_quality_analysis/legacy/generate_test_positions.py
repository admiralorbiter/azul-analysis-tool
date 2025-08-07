#!/usr/bin/env python3
"""
Generate Test Positions for Move Quality Database

This script systematically generates diverse Azul positions to build a comprehensive
move quality database. It creates positions covering different game phases, 
strategic scenarios, and tactical situations.
"""

import random
import time
from typing import List, Dict, Any
from dataclasses import dataclass

from core.azul_model import AzulState, AzulGameRule
from analysis_engine.mathematical_optimization.azul_move_generator import FastMoveGenerator

@dataclass
class PositionScenario:
    """Represents a specific position scenario to generate."""
    name: str
    description: str
    game_phase: str  # 'opening', 'middlegame', 'endgame'
    strategic_focus: str  # 'blocking', 'scoring', 'floor_line', 'wall_completion'
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    target_count: int

class TestPositionGenerator:
    """Generates diverse test positions for move quality analysis."""
    
    def __init__(self):
        self.move_generator = FastMoveGenerator()
        self.game_rule = AzulGameRule()
        
        # Define position scenarios
        self.scenarios = [
            # Opening positions
            PositionScenario(
                name="Early Game - Factory Selection",
                description="Positions where players are choosing from factories",
                game_phase="opening",
                strategic_focus="blocking",
                difficulty="beginner",
                target_count=20
            ),
            PositionScenario(
                name="Early Game - Pattern Line Building",
                description="Positions where players are building pattern lines",
                game_phase="opening",
                strategic_focus="scoring",
                difficulty="beginner",
                target_count=20
            ),
            
            # Middlegame positions
            PositionScenario(
                name="Mid Game - Blocking Opportunities",
                description="Positions with clear blocking opportunities",
                game_phase="middlegame",
                strategic_focus="blocking",
                difficulty="intermediate",
                target_count=30
            ),
            PositionScenario(
                name="Mid Game - Scoring Optimization",
                description="Positions with scoring opportunities",
                game_phase="middlegame",
                strategic_focus="scoring",
                difficulty="intermediate",
                target_count=30
            ),
            PositionScenario(
                name="Mid Game - Floor Line Management",
                description="Positions requiring floor line management",
                game_phase="middlegame",
                strategic_focus="floor_line",
                difficulty="intermediate",
                target_count=25
            ),
            
            # Endgame positions
            PositionScenario(
                name="End Game - Wall Completion",
                description="Positions near wall completion",
                game_phase="endgame",
                strategic_focus="wall_completion",
                difficulty="advanced",
                target_count=20
            ),
            PositionScenario(
                name="End Game - Final Scoring",
                description="Positions in final scoring phase",
                game_phase="endgame",
                strategic_focus="scoring",
                difficulty="advanced",
                target_count=20
            ),
            
            # Special scenarios
            PositionScenario(
                name="High Risk - Floor Line Penalty",
                description="Positions with high floor line penalties",
                game_phase="middlegame",
                strategic_focus="floor_line",
                difficulty="advanced",
                target_count=15
            ),
            PositionScenario(
                name="Pattern Line Overflow Risk",
                description="Positions with pattern line overflow risk",
                game_phase="middlegame",
                strategic_focus="scoring",
                difficulty="advanced",
                target_count=15
            ),
        ]
    
    def generate_positions_for_scenario(self, scenario: PositionScenario) -> List[AzulState]:
        """Generate positions for a specific scenario."""
        positions = []
        
        print(f"Generating {scenario.target_count} positions for: {scenario.name}")
        
        for i in range(scenario.target_count):
            try:
                position = self._generate_position_for_scenario(scenario)
                if position and self._validate_position(position):
                    positions.append(position)
                    print(f"  Generated position {i+1}/{scenario.target_count}")
                else:
                    print(f"  Skipped invalid position {i+1}/{scenario.target_count}")
            except Exception as e:
                print(f"  Error generating position {i+1}: {e}")
        
        return positions
    
    def _generate_position_for_scenario(self, scenario: PositionScenario) -> AzulState:
        """Generate a single position for a specific scenario."""
        
        # Start with initial state
        state = AzulState()
        
        # Apply scenario-specific modifications
        if scenario.game_phase == "opening":
            state = self._modify_for_opening(state, scenario)
        elif scenario.game_phase == "middlegame":
            state = self._modify_for_middlegame(state, scenario)
        elif scenario.game_phase == "endgame":
            state = self._modify_for_endgame(state, scenario)
        
        return state
    
    def _modify_for_opening(self, state: AzulState, scenario: PositionScenario) -> AzulState:
        """Modify state for opening phase scenarios."""
        
        # Add some tiles to factories and center pool
        if scenario.strategic_focus == "blocking":
            # Create blocking opportunities
            self._add_tiles_to_factories(state, blocking_focus=True)
        elif scenario.strategic_focus == "scoring":
            # Create scoring opportunities
            self._add_tiles_to_factories(state, scoring_focus=True)
        
        # Add some pattern line progress
        self._add_pattern_line_progress(state, early_game=True)
        
        return state
    
    def _modify_for_middlegame(self, state: AzulState, scenario: PositionScenario) -> AzulState:
        """Modify state for middlegame phase scenarios."""
        
        # Add significant pattern line progress
        self._add_pattern_line_progress(state, early_game=False)
        
        if scenario.strategic_focus == "blocking":
            # Create blocking scenarios
            self._create_blocking_scenarios(state)
        elif scenario.strategic_focus == "scoring":
            # Create scoring scenarios
            self._create_scoring_scenarios(state)
        elif scenario.strategic_focus == "floor_line":
            # Create floor line scenarios
            self._create_floor_line_scenarios(state)
        
        return state
    
    def _modify_for_endgame(self, state: AzulState, scenario: PositionScenario) -> AzulState:
        """Modify state for endgame phase scenarios."""
        
        # Add near-complete pattern lines
        self._add_pattern_line_progress(state, endgame=True)
        
        if scenario.strategic_focus == "wall_completion":
            # Create wall completion scenarios
            self._create_wall_completion_scenarios(state)
        elif scenario.strategic_focus == "scoring":
            # Create final scoring scenarios
            self._create_final_scoring_scenarios(state)
        
        return state
    
    def _add_tiles_to_factories(self, state: AzulState, blocking_focus: bool = False, scoring_focus: bool = False):
        """Add tiles to factories based on strategic focus."""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated tile placement
        
        # Add some tiles to factories (simplified)
        for factory_id in range(min(5, len(state.factories))):
            if factory_id < len(state.factories):
                # Add some tiles to this factory
                tile_count = random.randint(1, 4)
                for _ in range(tile_count):
                    tile_type = random.randint(0, 4)  # 0-4 for tile types
                    state.factories[factory_id].append(tile_type)
    
    def _add_pattern_line_progress(self, state: AzulState, early_game: bool = False, endgame: bool = False):
        """Add pattern line progress to players."""
        for player_id in range(len(state.agents)):
            agent = state.agents[player_id]
            
            if early_game:
                # Add 1-2 tiles to pattern lines
                pattern_lines_to_fill = random.randint(1, 3)
                for _ in range(pattern_lines_to_fill):
                    line_id = random.randint(0, 4)
                    tile_type = random.randint(0, 4)
                    tiles_to_add = min(random.randint(1, 3), line_id + 1)
                    # Simplified: just add tiles (would need proper validation)
                    pass
            elif endgame:
                # Add near-complete pattern lines
                pattern_lines_to_fill = random.randint(2, 4)
                for _ in range(pattern_lines_to_fill):
                    line_id = random.randint(0, 4)
                    tile_type = random.randint(0, 4)
                    tiles_to_add = line_id + 1  # Fill the line
                    # Simplified: just add tiles (would need proper validation)
                    pass
    
    def _create_blocking_scenarios(self, state: AzulState):
        """Create scenarios with blocking opportunities."""
        # Add tiles that opponents want to factories
        # This is simplified - would need more sophisticated logic
        pass
    
    def _create_scoring_scenarios(self, state: AzulState):
        """Create scenarios with scoring opportunities."""
        # Add tiles that create scoring opportunities
        # This is simplified - would need more sophisticated logic
        pass
    
    def _create_floor_line_scenarios(self, state: AzulState):
        """Create scenarios with floor line management."""
        # Add tiles to floor lines
        for player_id in range(len(state.agents)):
            agent = state.agents[player_id]
            floor_tiles = random.randint(1, 4)
            for _ in range(floor_tiles):
                tile_type = random.randint(0, 4)
                # Simplified: just add to floor line (would need proper validation)
                pass
    
    def _create_wall_completion_scenarios(self, state: AzulState):
        """Create scenarios near wall completion."""
        # Add near-complete walls
        # This is simplified - would need more sophisticated logic
        pass
    
    def _create_final_scoring_scenarios(self, state: AzulState):
        """Create scenarios in final scoring phase."""
        # Add completed pattern lines and wall progress
        # This is simplified - would need more sophisticated logic
        pass
    
    def _validate_position(self, state: AzulState) -> bool:
        """Validate that a position is legal and interesting."""
        try:
            # Check if position has legal moves
            moves = self.move_generator.generate_moves_fast(state, 0)
            if not moves:
                return False
            
            # Check if position is not too simple
            if len(moves) < 2:
                return False
            
            # Check if position is not too complex (for analysis purposes)
            if len(moves) > 50:
                return False
            
            return True
        except Exception:
            return False
    
    def generate_all_positions(self) -> List[AzulState]:
        """Generate positions for all scenarios."""
        all_positions = []
        
        print("Generating test positions for move quality database...")
        
        for scenario in self.scenarios:
            positions = self.generate_positions_for_scenario(scenario)
            all_positions.extend(positions)
            print(f"Generated {len(positions)} positions for {scenario.name}")
        
        print(f"Total positions generated: {len(all_positions)}")
        return all_positions

def main():
    """Main function to generate test positions."""
    generator = TestPositionGenerator()
    
    # Generate all positions
    positions = generator.generate_all_positions()
    
    # Save positions to file (optional)
    print(f"Generated {len(positions)} test positions")
    
    # You can save these positions or use them directly with the move quality builder
    return positions

if __name__ == "__main__":
    main()
