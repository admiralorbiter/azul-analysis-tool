#!/usr/bin/env python3
"""
Position Manager Tool
Helps add and manage positions in the shared database
"""

import json
import os
import sys
from pathlib import Path

def load_positions():
    """Load the current positions database"""
    positions_file = Path(__file__).parent.parent / "data" / "positions.json"
    if positions_file.exists():
        with open(positions_file, 'r') as f:
            return json.load(f)
    return {}

def save_positions(positions):
    """Save positions to the database"""
    positions_file = Path(__file__).parent.parent / "data" / "positions.json"
    positions_file.parent.mkdir(exist_ok=True)
    with open(positions_file, 'w') as f:
        json.dump(positions, f, indent=2)

def add_position(name, description, category, difficulty, tags, setup):
    """Add a new position to the database"""
    positions = load_positions()
    
    positions[name] = {
        "description": description,
        "category": category,
        "difficulty": difficulty,
        "tags": tags,
        "setup": setup
    }
    
    save_positions(positions)
    print(f"✅ Added position '{name}' to database")

def list_positions():
    """List all positions in the database"""
    positions = load_positions()
    
    if not positions:
        print("No positions found in database")
        return
    
    print(f"📚 Found {len(positions)} positions:")
    for name, data in positions.items():
        print(f"  • {name}: {data.get('description', 'No description')}")
        print(f"    Category: {data.get('category', 'Unknown')}")
        print(f"    Difficulty: {data.get('difficulty', 'Unknown')}")
        print(f"    Tags: {', '.join(data.get('tags', []))}")
        print()

def create_setup_from_template():
    """Create a setup template for a new position"""
    print("🎯 Position Setup Template:")
    print("=" * 50)
    
    setup = {
        "player_0_lines": {
            # "line_index": {"color": 0, "count": 1}
            # Example: "0": {"color": 0, "count": 1}  # 1 blue tile in line 0
        },
        "player_1_lines": {
            # "line_index": {"color": 0, "count": 1}
        },
        "player_0_wall": {
            # "row,col": 1
            # Example: "0,0": 1  # Blue tile at row 0, col 0
        },
        "player_1_wall": {
            # "row,col": 1
        },
        "factories": {
            # "factory_index": {"color": count}
            # Example: "0": {"0": 2}  # 2 blue tiles in factory 0
        },
        "center_pool": {
            # "color": count
            # Example: "0": 1  # 1 blue tile in center
        }
    }
    
    print(json.dumps(setup, indent=2))
    print("\nColor mapping: 0=Blue, 1=Yellow, 2=Red, 3=Black, 4=White")
    return setup

def interactive_add_position():
    """Interactively add a new position"""
    print("🎯 Add New Position")
    print("=" * 50)
    
    name = input("Position name (e.g., 'my_test_position'): ").strip()
    if not name:
        print("❌ Position name is required")
        return
    
    description = input("Description: ").strip()
    category = input("Category (e.g., blocking, scoring-optimization): ").strip()
    difficulty = input("Difficulty (beginner/intermediate/advanced): ").strip()
    tags_input = input("Tags (comma-separated): ").strip()
    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
    
    print("\n🎯 Setup Configuration:")
    print("You can either:")
    print("1. Use the template and edit manually")
    print("2. Enter setup interactively")
    
    choice = input("Choice (1 or 2): ").strip()
    
    if choice == "1":
        setup = create_setup_from_template()
        print("\n📝 Edit the setup above and paste it here:")
        setup_input = input("Setup JSON: ").strip()
        try:
            setup = json.loads(setup_input)
        except json.JSONDecodeError:
            print("❌ Invalid JSON format")
            return
    else:
        setup = {}
        print("\n🎯 Interactive Setup:")
        
        # Player lines
        for player in [0, 1]:
            lines = {}
            while True:
                line_input = input(f"Player {player} pattern lines (line,color,count or 'done'): ").strip()
                if line_input.lower() == 'done':
                    break
                try:
                    line, color, count = map(int, line_input.split(','))
                    lines[str(line)] = {"color": color, "count": count}
                except ValueError:
                    print("❌ Format: line,color,count (e.g., 0,0,1)")
            if lines:
                setup[f"player_{player}_lines"] = lines
        
        # Wall tiles
        for player in [0, 1]:
            wall = {}
            while True:
                wall_input = input(f"Player {player} wall tiles (row,col or 'done'): ").strip()
                if wall_input.lower() == 'done':
                    break
                try:
                    row, col = map(int, wall_input.split(','))
                    wall[f"{row},{col}"] = 1
                except ValueError:
                    print("❌ Format: row,col (e.g., 0,0)")
            if wall:
                setup[f"player_{player}_wall"] = wall
        
        # Factories
        factories = {}
        while True:
            factory_input = input("Factory tiles (factory,color,count or 'done'): ").strip()
            if factory_input.lower() == 'done':
                break
            try:
                factory, color, count = map(int, factory_input.split(','))
                if str(factory) not in factories:
                    factories[str(factory)] = {}
                factories[str(factory)][str(color)] = count
            except ValueError:
                print("❌ Format: factory,color,count (e.g., 0,0,2)")
        if factories:
            setup["factories"] = factories
        
        # Center pool
        center = {}
        while True:
            center_input = input("Center pool tiles (color,count or 'done'): ").strip()
            if center_input.lower() == 'done':
                break
            try:
                color, count = map(int, center_input.split(','))
                center[str(color)] = count
            except ValueError:
                print("❌ Format: color,count (e.g., 0,1)")
        if center:
            setup["center_pool"] = center
    
    add_position(name, description, category, difficulty, tags, setup)
    print(f"\n✅ Position '{name}' added successfully!")
    print("🔄 Restart the server to load the new position")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python position_manager.py [command]")
        print("Commands:")
        print("  list     - List all positions")
        print("  add      - Add a new position interactively")
        print("  template - Show setup template")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_positions()
    elif command == "add":
        interactive_add_position()
    elif command == "template":
        create_setup_from_template()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main() 