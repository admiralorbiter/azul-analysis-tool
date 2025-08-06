"""
Tests for Move Parser

This module tests the Azul move parser functionality.
"""

import pytest
from analysis_engine.move_quality.move_parser import (
    AzulMoveParser, 
    ParsedMove, 
    MoveType
)
from core import azul_utils as utils


class TestAzulMoveParser:
    """Test the Azul move parser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = AzulMoveParser()
    
    def test_parse_factory_to_pattern_line(self):
        """Test parsing factory to pattern line moves."""
        move_key = "factory_0_tile_blue_pattern_line_1"
        parsed = self.parser.parse_move(move_key)
        
        assert parsed.move_type == MoveType.FACTORY_TO_PATTERN_LINE
        assert parsed.factory_id == 0
        assert parsed.tile_color == utils.Tile.BLUE
        assert parsed.target_type == "pattern_line"
        assert parsed.pattern_line_id == 1
        assert parsed.is_valid == True
        assert len(parsed.validation_errors) == 0
    
    def test_parse_factory_to_floor(self):
        """Test parsing factory to floor moves."""
        move_key = "factory_2_tile_red_floor"
        parsed = self.parser.parse_move(move_key)
        
        assert parsed.move_type == MoveType.FACTORY_TO_FLOOR
        assert parsed.factory_id == 2
        assert parsed.tile_color == utils.Tile.RED
        assert parsed.target_type == "floor"
        assert parsed.is_valid == True
        assert len(parsed.validation_errors) == 0
    
    def test_parse_factory_to_wall(self):
        """Test parsing factory to wall moves."""
        move_key = "factory_1_tile_yellow_wall_2_3"
        parsed = self.parser.parse_move(move_key)
        
        assert parsed.move_type == MoveType.FACTORY_TO_WALL
        assert parsed.factory_id == 1
        assert parsed.tile_color == utils.Tile.YELLOW
        assert parsed.target_type == "wall"
        assert parsed.target_position == (2, 3)
        assert parsed.is_valid == True
        assert len(parsed.validation_errors) == 0
    
    def test_parse_pass_move(self):
        """Test parsing pass moves."""
        move_key = "pass"
        parsed = self.parser.parse_move(move_key)
        
        assert parsed.move_type == MoveType.PASS
        assert parsed.target_type == "pass"
        assert parsed.is_valid == True
        assert len(parsed.validation_errors) == 0
    
    def test_invalid_factory_id(self):
        """Test parsing with invalid factory ID."""
        move_key = "factory_10_tile_blue_pattern_line_1"
        parsed = self.parser.parse_move(move_key)
        
        assert parsed.is_valid == False
        assert "Invalid factory ID: 10" in parsed.validation_errors
    
    def test_invalid_tile_color(self):
        """Test parsing with invalid tile color."""
        move_key = "factory_0_tile_purple_pattern_line_1"
        parsed = self.parser.parse_move(move_key)
        
        assert parsed.is_valid == False
        assert "Invalid tile color: purple" in parsed.validation_errors
    
    def test_invalid_pattern_line_id(self):
        """Test parsing with invalid pattern line ID."""
        move_key = "factory_0_tile_blue_pattern_line_6"
        parsed = self.parser.parse_move(move_key)
        
        assert parsed.is_valid == False
        assert "Invalid pattern line ID: 6" in parsed.validation_errors
    
    def test_invalid_wall_position(self):
        """Test parsing with invalid wall position."""
        move_key = "factory_0_tile_blue_wall_5_3"
        parsed = self.parser.parse_move(move_key)
        
        assert parsed.is_valid == False
        assert "Invalid wall position: (5, 3)" in parsed.validation_errors
    
    def test_unknown_move_format(self):
        """Test parsing unknown move format."""
        move_key = "unknown_move_format"
        parsed = self.parser.parse_move(move_key)
        
        assert parsed.is_valid == False
        assert "Unknown move format: unknown_move_format" in parsed.validation_errors
    
    def test_generate_move_key(self):
        """Test generating move keys from parsed moves."""
        # Test factory to pattern line
        parsed = ParsedMove(
            move_type=MoveType.FACTORY_TO_PATTERN_LINE,
            factory_id=0,
            tile_color=utils.Tile.BLUE,
            target_type="pattern_line",
            target_position=None,
            pattern_line_id=1,
            original_string="factory_0_tile_blue_pattern_line_1",
            is_valid=True,
            validation_errors=[]
        )
        
        key = self.parser.generate_move_key(parsed)
        assert key == "factory_0_tile_blue_pattern_line_1"
        
        # Test pass move
        parsed_pass = ParsedMove(
            move_type=MoveType.PASS,
            factory_id=None,
            tile_color=None,
            target_type="pass",
            target_position=None,
            pattern_line_id=None,
            original_string="pass",
            is_valid=True,
            validation_errors=[]
        )
        
        key = self.parser.generate_move_key(parsed_pass)
        assert key == "pass"
    
    def test_get_move_description(self):
        """Test getting human-readable move descriptions."""
        # Test factory to pattern line
        parsed = ParsedMove(
            move_type=MoveType.FACTORY_TO_PATTERN_LINE,
            factory_id=0,
            tile_color=utils.Tile.BLUE,
            target_type="pattern_line",
            target_position=None,
            pattern_line_id=1,
            original_string="factory_0_tile_blue_pattern_line_1",
            is_valid=True,
            validation_errors=[]
        )
        
        description = self.parser.get_move_description(parsed)
        assert "Take blue tile from factory 0 to pattern line 1" in description
        
        # Test invalid move
        parsed_invalid = ParsedMove(
            move_type=MoveType.PASS,
            factory_id=None,
            tile_color=None,
            target_type="unknown",
            target_position=None,
            pattern_line_id=None,
            original_string="invalid",
            is_valid=False,
            validation_errors=["Invalid format"]
        )
        
        description = self.parser.get_move_description(parsed_invalid)
        assert "Invalid move" in description
        assert "Invalid format" in description


class TestMoveType:
    """Test the MoveType enum."""
    
    def test_move_type_values(self):
        """Test that move type values are correct."""
        assert MoveType.FACTORY_TO_PATTERN_LINE.value == "factory_to_pattern_line"
        assert MoveType.FACTORY_TO_FLOOR.value == "factory_to_floor"
        assert MoveType.FACTORY_TO_WALL.value == "factory_to_wall"
        assert MoveType.PASS.value == "pass"


class TestParsedMove:
    """Test the ParsedMove dataclass."""
    
    def test_parsed_move_creation(self):
        """Test creating a ParsedMove instance."""
        parsed = ParsedMove(
            move_type=MoveType.FACTORY_TO_PATTERN_LINE,
            factory_id=0,
            tile_color=utils.Tile.BLUE,
            target_type="pattern_line",
            target_position=None,
            pattern_line_id=1,
            original_string="factory_0_tile_blue_pattern_line_1",
            is_valid=True,
            validation_errors=[]
        )
        
        assert parsed.move_type == MoveType.FACTORY_TO_PATTERN_LINE
        assert parsed.factory_id == 0
        assert parsed.tile_color == utils.Tile.BLUE
        assert parsed.target_type == "pattern_line"
        assert parsed.pattern_line_id == 1
        assert parsed.is_valid == True
        assert len(parsed.validation_errors) == 0


if __name__ == "__main__":
    pytest.main([__file__]) 