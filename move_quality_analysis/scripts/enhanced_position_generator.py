#!/usr/bin/env python3
"""
Enhanced Position Generator - Scale to 1,000 Positions

This script generates 1,000 diverse positions with automated validation,
complexity scoring, and metadata tracking for the advanced dataset.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import time
import random
import sqlite3
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

from core.azul_model import AzulState, AzulGameRule
from analysis_engine.mathematical_optimization.azul_move_generator import FastMoveGenerator

class PositionComplexity(Enum):
    """Position complexity levels."""
    SIMPLE = "simple"      # 0.0-0.3
    MEDIUM = "medium"      # 0.3-0.6
    COMPLEX = "complex"    # 0.6-0.8
    EXPERT = "expert"      # 0.8-1.0

class GamePhase(Enum):
    """Game phases for position generation."""
    OPENING = "opening"      # Rounds 1-2
    MIDDLEGAME = "middlegame" # Rounds 3-4
    ENDGAME = "endgame"      # Round 5

class StrategicScenario(Enum):
    """Strategic scenarios for position generation."""
    BLOCKING = "blocking"
    SCORING = "scoring"
    FLOOR_LINE = "floor_line"
    WALL_COMPLETION = "wall_completion"
    FACTORY_CONTROL = "factory_control"
    RISK_MANAGEMENT = "risk_management"
    PATTERN_BUILDING = "pattern_building"
    BONUS_OPTIMIZATION = "bonus_optimization"

@dataclass
class PositionMetadata:
    """Metadata for generated positions."""
    position_id: str
    fen_string: str
    game_phase: GamePhase
    strategic_scenario: StrategicScenario
    complexity_score: float
    risk_level: float
    move_count: int
    validation_status: str
    generation_time: float
    tags: List[str]
    description: str

class EnhancedPositionGenerator:
    """Enhanced position generator for 1,000 diverse positions."""
    
    def __init__(self, target_count: int = 1000):
        self.target_count = target_count
        self.game_rule = AzulGameRule(2)
        self.move_generator = FastMoveGenerator()
        
        # Position specifications for comprehensive coverage
        self.position_specs = self._define_comprehensive_specifications()
        
        # Database for position metadata
        self.db_path = "../data/position_metadata.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize position metadata database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_metadata (
                position_id TEXT PRIMARY KEY,
                fen_string TEXT NOT NULL,
                game_phase TEXT NOT NULL,
                strategic_scenario TEXT NOT NULL,
                complexity_score REAL NOT NULL,
                risk_level REAL NOT NULL,
                move_count INTEGER NOT NULL,
                validation_status TEXT NOT NULL,
                generation_time REAL NOT NULL,
                tags TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _define_comprehensive_specifications(self) -> List[Dict[str, Any]]:
        """Define comprehensive position specifications for 1,000 positions."""
        specs = []
        
        # Opening positions (300 total)
        opening_specs = [
            {"phase": GamePhase.OPENING, "scenario": StrategicScenario.FACTORY_CONTROL, "count": 50, "complexity": 0.2, "risk": 0.1},
            {"phase": GamePhase.OPENING, "scenario": StrategicScenario.PATTERN_BUILDING, "count": 50, "complexity": 0.4, "risk": 0.2},
            {"phase": GamePhase.OPENING, "scenario": StrategicScenario.BLOCKING, "count": 40, "complexity": 0.6, "risk": 0.3},
            {"phase": GamePhase.OPENING, "scenario": StrategicScenario.SCORING, "count": 40, "complexity": 0.5, "risk": 0.2},
            {"phase": GamePhase.OPENING, "scenario": StrategicScenario.FLOOR_LINE, "count": 30, "complexity": 0.3, "risk": 0.4},
            {"phase": GamePhase.OPENING, "scenario": StrategicScenario.RISK_MANAGEMENT, "count": 30, "complexity": 0.7, "risk": 0.6},
            {"phase": GamePhase.OPENING, "scenario": StrategicScenario.BONUS_OPTIMIZATION, "count": 20, "complexity": 0.6, "risk": 0.3},
            {"phase": GamePhase.OPENING, "scenario": StrategicScenario.WALL_COMPLETION, "count": 20, "complexity": 0.8, "risk": 0.5},
        ]
        
        # Middlegame positions (400 total)
        middlegame_specs = [
            {"phase": GamePhase.MIDDLEGAME, "scenario": StrategicScenario.BLOCKING, "count": 80, "complexity": 0.7, "risk": 0.5},
            {"phase": GamePhase.MIDDLEGAME, "scenario": StrategicScenario.SCORING, "count": 80, "complexity": 0.6, "risk": 0.4},
            {"phase": GamePhase.MIDDLEGAME, "scenario": StrategicScenario.FLOOR_LINE, "count": 60, "complexity": 0.5, "risk": 0.6},
            {"phase": GamePhase.MIDDLEGAME, "scenario": StrategicScenario.WALL_COMPLETION, "count": 50, "complexity": 0.8, "risk": 0.4},
            {"phase": GamePhase.MIDDLEGAME, "scenario": StrategicScenario.FACTORY_CONTROL, "count": 40, "complexity": 0.4, "risk": 0.3},
            {"phase": GamePhase.MIDDLEGAME, "scenario": StrategicScenario.RISK_MANAGEMENT, "count": 40, "complexity": 0.9, "risk": 0.7},
            {"phase": GamePhase.MIDDLEGAME, "scenario": StrategicScenario.PATTERN_BUILDING, "count": 30, "complexity": 0.6, "risk": 0.4},
            {"phase": GamePhase.MIDDLEGAME, "scenario": StrategicScenario.BONUS_OPTIMIZATION, "count": 20, "complexity": 0.7, "risk": 0.5},
        ]
        
        # Endgame positions (300 total)
        endgame_specs = [
            {"phase": GamePhase.ENDGAME, "scenario": StrategicScenario.WALL_COMPLETION, "count": 80, "complexity": 0.9, "risk": 0.3},
            {"phase": GamePhase.ENDGAME, "scenario": StrategicScenario.SCORING, "count": 60, "complexity": 0.8, "risk": 0.4},
            {"phase": GamePhase.ENDGAME, "scenario": StrategicScenario.FLOOR_LINE, "count": 50, "complexity": 0.7, "risk": 0.8},
            {"phase": GamePhase.ENDGAME, "scenario": StrategicScenario.BONUS_OPTIMIZATION, "count": 40, "complexity": 0.8, "risk": 0.5},
            {"phase": GamePhase.ENDGAME, "scenario": StrategicScenario.RISK_MANAGEMENT, "count": 40, "complexity": 0.9, "risk": 0.9},
            {"phase": GamePhase.ENDGAME, "scenario": StrategicScenario.BLOCKING, "count": 30, "complexity": 0.7, "risk": 0.6},
        ]
        
        specs.extend(opening_specs + middlegame_specs + endgame_specs)
        return specs
    
    def generate_position_for_spec(self, spec: Dict[str, Any]) -> Optional[AzulState]:
        """Generate a single position for a given specification."""
        try:
            # Start with a fresh game state (2-player game)
            state = AzulState(2)
            
            # Modify state based on game phase
            if spec["phase"] == GamePhase.OPENING:
                state = self._modify_for_opening(state, spec)
            elif spec["phase"] == GamePhase.MIDDLEGAME:
                state = self._modify_for_middlegame(state, spec)
            elif spec["phase"] == GamePhase.ENDGAME:
                state = self._modify_for_endgame(state, spec)
            
            # Apply strategic scenario modifications
            state = self._apply_strategic_scenario(state, spec["scenario"], spec["complexity"], spec["risk"])
            
            # Validate the position
            if self._validate_position(state):
                return state
            else:
                return None
                
        except Exception as e:
            print(f"Error generating position for spec {spec}: {e}")
            return None
    
    def _modify_for_opening(self, state: AzulState, spec: Dict[str, Any]) -> AzulState:
        """Modify state for opening phase."""
        # Add some initial factory tiles
        for _ in range(random.randint(2, 4)):
            factory_idx = random.randint(0, len(state.factories) - 1)
            color = random.randint(0, 4)
            count = random.randint(1, 4)
            state.factories[factory_idx].AddTiles(count, color)
        
        # Add some pattern line progress
        for player in range(2):
            for line in range(5):
                if random.random() < 0.3:
                    tile_count = random.randint(1, line + 1)
                    tile_type = random.randint(0, 4)
                    state.agents[player].lines_number[line] = tile_count
                    state.agents[player].lines_tile[line] = tile_type
        
        return state
    
    def _modify_for_middlegame(self, state: AzulState, spec: Dict[str, Any]) -> AzulState:
        """Modify state for middlegame phase."""
        # Add more factory tiles
        for _ in range(random.randint(4, 6)):
            factory_idx = random.randint(0, len(state.factories) - 1)
            color = random.randint(0, 4)
            count = random.randint(1, 4)
            state.factories[factory_idx].AddTiles(count, color)
        
        # Add significant pattern line progress
        for player in range(2):
            for line in range(5):
                if random.random() < 0.6:
                    tile_count = random.randint(1, line + 1)
                    tile_type = random.randint(0, 4)
                    state.agents[player].lines_number[line] = tile_count
                    state.agents[player].lines_tile[line] = tile_type
        
        # Add some wall progress
        for player in range(2):
            for row in range(5):
                for col in range(5):
                    if random.random() < 0.3:
                        state.agents[player].grid_state[row][col] = 1
        
        return state
    
    def _modify_for_endgame(self, state: AzulState, spec: Dict[str, Any]) -> AzulState:
        """Modify state for endgame phase."""
        # Add factory tiles
        for _ in range(random.randint(3, 5)):
            factory_idx = random.randint(0, len(state.factories) - 1)
            color = random.randint(0, 4)
            count = random.randint(1, 4)
            state.factories[factory_idx].AddTiles(count, color)
        
        # Add near-complete pattern lines
        for player in range(2):
            for line in range(5):
                if random.random() < 0.7:
                    tile_count = random.randint(line, line + 1)
                    tile_type = random.randint(0, 4)
                    state.agents[player].lines_number[line] = tile_count
                    state.agents[player].lines_tile[line] = tile_type
        
        # Add significant wall progress
        for player in range(2):
            for row in range(5):
                for col in range(5):
                    if random.random() < 0.5:
                        state.agents[player].grid_state[row][col] = 1
        
        return state
    
    def _apply_strategic_scenario(self, state: AzulState, scenario: StrategicScenario, 
                                complexity: float, risk: float) -> AzulState:
        """Apply specific strategic scenario modifications."""
        
        if scenario == StrategicScenario.BLOCKING:
            # Create blocking opportunities
            for player in range(2):
                for line in range(5):
                    if random.random() < complexity:
                        state.agents[player].lines_number[line] = line  # Near completion
                        state.agents[player].lines_tile[line] = random.randint(0, 4)
                        
        elif scenario == StrategicScenario.SCORING:
            # Create scoring opportunities
            for player in range(2):
                for row in range(5):
                    for col in range(5):
                        if random.random() < complexity * 0.5:
                            state.agents[player].grid_state[row][col] = 1
                            
        elif scenario == StrategicScenario.FLOOR_LINE:
            # Add floor line tiles
            for player in range(2):
                floor_count = int(risk * 7)
                for _ in range(floor_count):
                    tile_type = random.randint(0, 4)
                    state.agents[player].floor_tiles.append(tile_type)
                    # Update floor array
                    for i in range(len(state.agents[player].floor)):
                        if state.agents[player].floor[i] == 0:
                            state.agents[player].floor[i] = 1
                            break
                    
        elif scenario == StrategicScenario.WALL_COMPLETION:
            # Add near-complete rows/columns
            for player in range(2):
                for row in range(5):
                    if random.random() < complexity:
                        for col in range(5):
                            if random.random() < 0.8:
                                state.agents[player].grid_state[row][col] = 1
                                
        elif scenario == StrategicScenario.FACTORY_CONTROL:
            # Add diverse factory configurations
            for factory_idx in range(len(state.factories)):
                for color in range(5):
                    if random.random() < complexity:
                        count = random.randint(1, 4)
                        state.factories[factory_idx].AddTiles(count, color)
                        
        elif scenario == StrategicScenario.RISK_MANAGEMENT:
            # Create high-risk scenarios
            for player in range(2):
                # Add floor line tiles
                floor_count = int(risk * 10)
                for _ in range(floor_count):
                    tile_type = random.randint(0, 4)
                    state.agents[player].floor_tiles.append(tile_type)
                    # Update floor array
                    for i in range(len(state.agents[player].floor)):
                        if state.agents[player].floor[i] == 0:
                            state.agents[player].floor[i] = 1
                            break
                    
                # Add near-full pattern lines
                for line in range(5):
                    if random.random() < complexity:
                        state.agents[player].lines_number[line] = line + 1
                        state.agents[player].lines_tile[line] = random.randint(0, 4)
                        
        elif scenario == StrategicScenario.PATTERN_BUILDING:
            # Add pattern line progress
            for player in range(2):
                for line in range(5):
                    if random.random() < complexity:
                        tile_count = random.randint(1, line + 1)
                        tile_type = random.randint(0, 4)
                        state.agents[player].lines_number[line] = tile_count
                        state.agents[player].lines_tile[line] = tile_type
                        
        elif scenario == StrategicScenario.BONUS_OPTIMIZATION:
            # Create bonus opportunities
            for player in range(2):
                # Add row completions
                for row in range(5):
                    if random.random() < complexity * 0.7:
                        for col in range(5):
                            state.agents[player].grid_state[row][col] = 1
                            
                # Add column completions
                for col in range(5):
                    if random.random() < complexity * 0.7:
                        for row in range(5):
                            state.agents[player].grid_state[row][col] = 1
        
        return state
    
    def _validate_position(self, state: AzulState) -> bool:
        """Validate that a position is legal and interesting."""
        try:
            # Check if position has legal moves
            moves = self.move_generator.generate_moves_fast(state, 0)
            if len(moves) == 0:
                return False
            
            # Check if position has some complexity (not too simple)
            total_factory_tiles = sum(factory.total for factory in state.factories)
            if total_factory_tiles < 4:
                return False
            
            # Check if position has some progress (not starting position)
            total_pattern_progress = sum(sum(agent.lines_number) for agent in state.agents)
            total_wall_progress = sum(sum(sum(agent.grid_state)) for agent in state.agents)
            if total_pattern_progress == 0 and total_wall_progress == 0:
                return False
            
            return True
            
        except Exception as e:
            print(f"Validation error: {e}")
            return False
    
    def _calculate_complexity_score(self, state: AzulState) -> float:
        """Calculate complexity score for a position."""
        complexity = 0.0
        
        # Factory complexity
        total_factory_tiles = sum(factory.total for factory in state.factories)
        complexity += min(total_factory_tiles / 20.0, 0.3)
        
        # Pattern line complexity
        total_pattern_progress = sum(sum(agent.lines_number) for agent in state.agents)
        complexity += min(total_pattern_progress / 30.0, 0.3)
        
        # Wall complexity
        total_wall_progress = sum(sum(sum(agent.grid_state)) for agent in state.agents)
        complexity += min(total_wall_progress / 25.0, 0.2)
        
        # Floor line complexity (risk)
        total_floor_tiles = sum(len(agent.floor_tiles) for agent in state.agents)
        complexity += min(total_floor_tiles / 10.0, 0.2)
        
        return min(complexity, 1.0)
    
    def _calculate_risk_level(self, state: AzulState) -> float:
        """Calculate risk level for a position."""
        risk = 0.0
        
        # Floor line risk
        for player in range(2):
            if len(state.agents[player].floor_tiles) > 0:
                risk += len(state.agents[player].floor_tiles) / 7.0
        
        # Pattern line overflow risk
        for player in range(2):
            for line in range(5):
                if state.agents[player].lines_number[line] >= line + 1:
                    risk += 0.2
        
        return min(risk / 2.0, 1.0)
    
    def generate_all_positions(self) -> List[PositionMetadata]:
        """Generate all 1,000 positions with metadata."""
        print(f"Generating {self.target_count} diverse positions...")
        
        positions = []
        generated_count = 0
        attempts = 0
        max_attempts = self.target_count * 10  # Allow for some failed attempts
        
        start_time = time.time()
        
        # Generate positions for each specification
        for spec in self.position_specs:
            spec_count = 0
            target_spec_count = spec["count"]
            
            while spec_count < target_spec_count and attempts < max_attempts:
                attempts += 1
                
                # Generate position
                state = self.generate_position_for_spec(spec)
                
                if state is not None:
                    # Calculate metadata
                    complexity = self._calculate_complexity_score(state)
                    risk = self._calculate_risk_level(state)
                    move_count = len(self.move_generator.generate_moves_fast(state, 0))
                    
                    # Create metadata
                    position_id = f"pos_{generated_count:04d}"
                    fen_string = self._state_to_fen(state)
                    
                    metadata = PositionMetadata(
                        position_id=position_id,
                        fen_string=fen_string,
                        game_phase=spec["phase"],
                        strategic_scenario=spec["scenario"],
                        complexity_score=complexity,
                        risk_level=risk,
                        move_count=move_count,
                        validation_status="valid",
                        generation_time=time.time() - start_time,
                        tags=[spec["phase"].value, spec["scenario"].value],
                        description=f"{spec['phase'].value} {spec['scenario'].value} position"
                    )
                    
                    positions.append(metadata)
                    generated_count += 1
                    spec_count += 1
                    
                    # Save to database
                    self._save_position_metadata(metadata)
                    
                    if generated_count % 100 == 0:
                        print(f"Generated {generated_count} positions...")
                    
                    if generated_count >= self.target_count:
                        break
        
        print(f"Generated {len(positions)} positions in {time.time() - start_time:.2f} seconds")
        return positions
    
    def _state_to_fen(self, state: AzulState) -> str:
        """Convert state to FEN string."""
        # This is a simplified FEN conversion
        # In practice, you'd use the proper FEN parser
        return f"azul_state_{id(state)}"
    
    def _save_position_metadata(self, metadata: PositionMetadata):
        """Save position metadata to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO position_metadata 
            (position_id, fen_string, game_phase, strategic_scenario, complexity_score, 
             risk_level, move_count, validation_status, generation_time, tags, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metadata.position_id,
            metadata.fen_string,
            metadata.game_phase.value,
            metadata.strategic_scenario.value,
            metadata.complexity_score,
            metadata.risk_level,
            metadata.move_count,
            metadata.validation_status,
            metadata.generation_time,
            json.dumps(metadata.tags),
            metadata.description
        ))
        
        conn.commit()
        conn.close()
    
    def _json_default_serializer(self, obj):
        """Custom JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, Enum):
            return obj.value
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    def export_positions_to_json(self, positions: List[PositionMetadata], filename: str):
        """Export positions to JSON file."""
        data = {
            "metadata": {
                "total_positions": len(positions),
                "generation_time": time.time(),
                "version": "1.0"
            },
            "positions": [asdict(pos) for pos in positions]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=self._json_default_serializer)
        
        print(f"Exported {len(positions)} positions to {filename}")

def main():
    """Main function to generate 1,000 diverse positions."""
    generator = EnhancedPositionGenerator(target_count=1000)
    
    # Generate all positions
    positions = generator.generate_all_positions()
    
    # Export to JSON
    generator.export_positions_to_json(positions, "../data/diverse_positions_enhanced.json")
    
    # Print summary
    print("\n=== Position Generation Summary ===")
    print(f"Total positions generated: {len(positions)}")
    
    # Count by phase
    phase_counts = {}
    scenario_counts = {}
    complexity_distribution = {"simple": 0, "medium": 0, "complex": 0, "expert": 0}
    
    for pos in positions:
        phase_counts[pos.game_phase.value] = phase_counts.get(pos.game_phase.value, 0) + 1
        scenario_counts[pos.strategic_scenario.value] = scenario_counts.get(pos.strategic_scenario.value, 0) + 1
        
        if pos.complexity_score < 0.3:
            complexity_distribution["simple"] += 1
        elif pos.complexity_score < 0.6:
            complexity_distribution["medium"] += 1
        elif pos.complexity_score < 0.8:
            complexity_distribution["complex"] += 1
        else:
            complexity_distribution["expert"] += 1
    
    print(f"\nBy Game Phase:")
    for phase, count in phase_counts.items():
        print(f"  {phase}: {count}")
    
    print(f"\nBy Strategic Scenario:")
    for scenario, count in scenario_counts.items():
        print(f"  {scenario}: {count}")
    
    print(f"\nBy Complexity:")
    for complexity, count in complexity_distribution.items():
        print(f"  {complexity}: {count}")

if __name__ == "__main__":
    main()
