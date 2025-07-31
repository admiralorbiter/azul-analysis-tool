#!/usr/bin/env python3
"""
Test script for move execution functionality.
"""

import requests
import json

def test_move_execution():
    """Test the move execution endpoint."""
    base_url = "http://127.0.0.1:8000"
    
    # Test data - a simple move from factory 0, blue tile, to pattern line 0
    test_move = {
        "fen_string": "initial",
        "move": {
            "source_id": 0,
            "tile_type": 0,  # Blue tile
            "pattern_line_dest": 0,
            "num_to_pattern_line": 1,
            "num_to_floor_line": 0
        },
        "agent_id": 0
    }
    
    try:
        # Make the request
        response = requests.post(
            f"{base_url}/api/v1/execute_move",
            json=test_move,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Move execution successful!")
            print(f"New FEN: {data.get('new_fen')}")
            print(f"Game Over: {data.get('game_over')}")
            print(f"Scores: {data.get('scores')}")
        else:
            print("❌ Move execution failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the API server is running on port 8000.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_move_execution() 