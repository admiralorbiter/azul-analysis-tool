#!/usr/bin/env python3
"""
Test script for Game Theory API endpoints

This script tests the game theory API endpoints including Nash equilibrium detection,
opponent modeling, and strategic analysis.
"""

import requests
import json
import time
from typing import Dict, Any


def test_game_theory_api():
    """Test all game theory API endpoints"""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Sample game state for testing
    sample_game_state = {
        "factories": [
            ["blue", "red", "yellow", "black"],
            ["white", "blue", "red", "yellow"],
            ["black", "white", "blue", "red"],
            ["yellow", "black", "white", "blue"],
            ["red", "yellow", "black", "white"]
        ],
        "center_pool": ["blue", "red", "yellow"],
        "players": [
            {
                "id": 0,
                "score": 15,
                "pattern_lines": [[], ["blue"], [], [], []],
                "wall": [[False] * 5 for _ in range(5)],
                "floor_line": []
            },
            {
                "id": 1,
                "score": 12,
                "pattern_lines": [[], [], ["red"], [], []],
                "wall": [[False] * 5 for _ in range(5)],
                "floor_line": ["blue"]
            }
        ],
        "current_player": 0,
        "num_players": 2
    }
    
    print("🧪 Testing Game Theory API Endpoints")
    print("=" * 50)
    
    # Test 1: Nash Equilibrium Detection
    print("\n1️⃣ Testing Nash Equilibrium Detection...")
    try:
        response = requests.post(
            f"{base_url}/game-theory/detect-nash-equilibrium",
            json={
                "game_state": sample_game_state,
                "player_id": 0
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Nash Equilibrium Detection - SUCCESS")
            print(f"   Equilibrium Type: {result.get('equilibrium_type', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Strategic Insights: {len(result.get('strategic_insights', []))} insights")
        else:
            print(f"❌ Nash Equilibrium Detection - FAILED (Status: {response.status_code})")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Nash Equilibrium Detection - ERROR: {str(e)}")
    
    # Test 2: Opponent Modeling
    print("\n2️⃣ Testing Opponent Modeling...")
    try:
        response = requests.post(
            f"{base_url}/game-theory/model-opponent",
            json={
                "game_state": sample_game_state,
                "opponent_id": 1
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            opponent_model = result.get('opponent_model', {})
            print("✅ Opponent Modeling - SUCCESS")
            print(f"   Player ID: {opponent_model.get('player_id', 'N/A')}")
            print(f"   Risk Tolerance: {opponent_model.get('risk_tolerance', 'N/A')}")
            print(f"   Aggression Level: {opponent_model.get('aggression_level', 'N/A')}")
            print(f"   Predictability: {opponent_model.get('predictability_score', 'N/A')}")
        else:
            print(f"❌ Opponent Modeling - FAILED (Status: {response.status_code})")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Opponent Modeling - ERROR: {str(e)}")
    
    # Test 3: Strategic Analysis
    print("\n3️⃣ Testing Strategic Analysis...")
    try:
        response = requests.post(
            f"{base_url}/game-theory/analyze-strategy",
            json={
                "game_state": sample_game_state,
                "player_id": 0
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            strategic_analysis = result.get('strategic_analysis', {})
            print("✅ Strategic Analysis - SUCCESS")
            print(f"   Strategic Value: {strategic_analysis.get('strategic_value', 'N/A')}")
            print(f"   Game Phase: {strategic_analysis.get('game_phase', 'N/A')}")
            print(f"   Confidence: {strategic_analysis.get('confidence', 'N/A')}")
            print(f"   Recommended Actions: {len(strategic_analysis.get('recommended_actions', []))} actions")
        else:
            print(f"❌ Strategic Analysis - FAILED (Status: {response.status_code})")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Strategic Analysis - ERROR: {str(e)}")
    
    # Test 4: Opponent Move Prediction
    print("\n4️⃣ Testing Opponent Move Prediction...")
    try:
        response = requests.post(
            f"{base_url}/game-theory/predict-opponent-moves",
            json={
                "game_state": sample_game_state,
                "opponent_id": 1,
                "depth": 3
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Opponent Move Prediction - SUCCESS")
            print(f"   Predicted Moves: {len(result.get('predicted_moves', []))} moves")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
        else:
            print(f"❌ Opponent Move Prediction - FAILED (Status: {response.status_code})")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Opponent Move Prediction - ERROR: {str(e)}")
    
    # Test 5: Strategic Value Calculation
    print("\n5️⃣ Testing Strategic Value Calculation...")
    try:
        response = requests.post(
            f"{base_url}/game-theory/calculate-strategic-value",
            json={
                "game_state": sample_game_state,
                "player_id": 0
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Strategic Value Calculation - SUCCESS")
            print(f"   Strategic Value: {result.get('strategic_value', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            components = result.get('components', {})
            print(f"   Components: {len(components)} components")
        else:
            print(f"❌ Strategic Value Calculation - FAILED (Status: {response.status_code})")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Strategic Value Calculation - ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Game Theory API Testing Complete!")
    print("=" * 50)


if __name__ == "__main__":
    test_game_theory_api() 