#!/usr/bin/env python3
"""
Test the updated game theory API with real StateConverter integration.
"""

import requests
import json

def test_game_theory_api():
    """Test all game theory API endpoints with real state conversion."""
    
    print("=== Testing Real Game Theory API ===")
    
    # Sample game state for testing
    game_state = {
        "factories": [
            ["B", "B", "Y", "R"],  # Factory 0
            ["K", "W", "B", "Y"],  # Factory 1
            ["R", "R", "K", "W"],  # Factory 2
            ["Y", "K", "R", "B"],  # Factory 3
            ["W", "W", "Y", "K"]   # Factory 4
        ],
        "center": ["B", "Y", "R"],
        "players": [
            {
                "pattern_lines": [
                    ["B", "B"],  # Line 0: 2 blue tiles
                    [],          # Line 1: empty
                    ["Y"],       # Line 2: 1 yellow tile
                    [],          # Line 3: empty
                    []           # Line 4: empty
                ],
                "wall": [
                    [False, False, False, False, False],
                    [False, False, False, False, False],
                    [False, False, False, False, False],
                    [False, False, False, False, False],
                    [False, False, False, False, False]
                ],
                "floor": ["FP", "B", "Y"],  # First player marker + 2 tiles
                "score": 15
            },
            {
                "pattern_lines": [
                    [],          # Line 0: empty
                    ["R", "R"],  # Line 1: 2 red tiles
                    [],          # Line 2: empty
                    ["K"],       # Line 3: 1 black tile
                    []           # Line 4: empty
                ],
                "wall": [
                    [False, False, False, False, False],
                    [False, False, False, False, False],
                    [False, False, False, False, False],
                    [False, False, False, False, False],
                    [False, False, False, False, False]
                ],
                "floor": ["R"],
                "score": 12
            }
        ],
        "first_player_taken": False,
        "next_first_agent": 0
    }
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test 1: Nash Equilibrium Detection
    print("\n1. Testing Nash Equilibrium Detection...")
    try:
        response = requests.post(
            f"{base_url}/game-theory/detect-nash-equilibrium",
            json={"game_state": game_state},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Nash equilibrium detection successful")
            print(f"   📊 Equilibrium type: {result.get('equilibrium_type', 'N/A')}")
            print(f"   📊 Confidence: {result.get('confidence', 'N/A')}")
        else:
            print(f"   ❌ Nash equilibrium detection failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Nash equilibrium test error: {e}")
    
    # Test 2: Opponent Modeling
    print("\n2. Testing Opponent Modeling...")
    try:
        response = requests.post(
            f"{base_url}/game-theory/model-opponent",
            json={"game_state": game_state, "opponent_id": 1},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Opponent modeling successful")
            opponent_model = result.get('opponent_model', {})
            print(f"   📊 Risk tolerance: {opponent_model.get('risk_tolerance', 'N/A')}")
            print(f"   📊 Aggression level: {opponent_model.get('aggression_level', 'N/A')}")
        else:
            print(f"   ❌ Opponent modeling failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Opponent modeling test error: {e}")
    
    # Test 3: Strategic Analysis
    print("\n3. Testing Strategic Analysis...")
    try:
        response = requests.post(
            f"{base_url}/game-theory/analyze-strategy",
            json={"game_state": game_state, "player_id": 0},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Strategic analysis successful")
            analysis = result.get('strategic_analysis', {})
            print(f"   📊 Strategic value: {analysis.get('strategic_value', 'N/A')}")
            print(f"   📊 Game phase: {analysis.get('game_phase', 'N/A')}")
        else:
            print(f"   ❌ Strategic analysis failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Strategic analysis test error: {e}")
    
    # Test 4: Move Prediction
    print("\n4. Testing Move Prediction...")
    try:
        response = requests.post(
            f"{base_url}/game-theory/predict-opponent-moves",
            json={"game_state": game_state, "opponent_id": 1, "depth": 3},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Move prediction successful")
            print(f"   📊 Prediction depth: {result.get('prediction_depth', 'N/A')}")
            print(f"   📊 Confidence: {result.get('confidence', 'N/A')}")
        else:
            print(f"   ❌ Move prediction failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Move prediction test error: {e}")
    
    # Test 5: Strategic Value Calculation
    print("\n5. Testing Strategic Value Calculation...")
    try:
        response = requests.post(
            f"{base_url}/game-theory/calculate-strategic-value",
            json={"game_state": game_state, "player_id": 0},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Strategic value calculation successful")
            print(f"   📊 Strategic value: {result.get('strategic_value', 'N/A')}")
            print(f"   📊 Confidence: {result.get('confidence', 'N/A')}")
        else:
            print(f"   ❌ Strategic value calculation failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Strategic value test error: {e}")
    
    print("\n=== Game Theory API Testing Complete ===")

if __name__ == "__main__":
    print("Starting real game theory API tests...")
    test_game_theory_api() 