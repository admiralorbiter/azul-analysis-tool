# Position Library Development Guide

## Overview

The Position Library is a modular system for managing pre-defined Azul game states. This guide explains how to create, organize, and maintain positions for the Azul Solver & Analysis Toolkit.

## Architecture

### Core Components

1. **Position Categories** - High-level organization (opening, midgame, endgame, educational)
2. **Subcategories** - Specific themes within categories (scoring, blocking, etc.)
3. **Position Templates** - Individual game states with metadata
4. **Position Generators** - Functions that create game state objects

### File Structure

```
ui/components/PositionLibrary.js          # Main component
ui/components/positions/                  # Position modules
├── opening-positions.js                  # Opening scenarios
├── midgame-positions.js                  # Mid-game scenarios  
├── endgame-positions.js                  # End-game scenarios
├── educational-positions.js              # Learning scenarios
└── custom-positions.js                   # User-created positions
ui/styles/position-library.css           # Styling
docs/POSITION_LIBRARY_DEVELOPMENT_GUIDE.md  # This guide
```

## Creating New Positions

### Step 1: Choose Your Category

**Opening Positions** (`opening-positions.js`)
- Game start scenarios
- Early tactical decisions
- Balanced vs. aggressive openings

**Mid-Game Positions** (`midgame-positions.js`)
- Tactical scenarios
- Scoring opportunities
- Blocking situations

**End-Game Positions** (`endgame-positions.js`)
- Final round optimization
- Precise counting scenarios
- Tie-breaker situations

**Educational Positions** (`educational-positions.js`)
- Learning scenarios
- Skill development
- Concept demonstration

### Step 2: Create Position Template

```javascript
// Example: Create a new opening position
const balancedStart = {
    name: "Balanced Start",
    description: "Standard opening with mixed factory colors",
    difficulty: "beginner",
    tags: ["opening", "balanced", "2-player"],
    generate: () => ({
        factories: [
            ['B', 'B', 'Y', 'R'],
            ['B', 'Y', 'R', 'K'],
            ['Y', 'R', 'K', 'W'],
            ['R', 'K', 'W', 'B'],
            ['K', 'W', 'B', 'Y']
        ],
        center: [],
        players: Array(2).fill().map(() => ({
            pattern_lines: [[], [], [], [], []],
            wall: Array(5).fill().map(() => Array(5).fill(null)),
            floor_line: [],
            score: 0
        }))
    })
};
```

### Step 3: Add to Module

```javascript
// In opening-positions.js
export const openingPositions = {
    "2-player": {
        name: "2-Player Openings",
        description: "Duel scenarios with focused strategies",
        positions: [
            balancedStart,
            aggressiveStart,
            // ... more positions
        ]
    }
};
```

### Step 4: Register in Main Library

```javascript
// In PositionLibrary.js
import { openingPositions } from './positions/opening-positions.js';
import { midgamePositions } from './positions/midgame-positions.js';
// ... other imports

const positionCategories = {
    opening: {
        name: "Opening Positions",
        description: "Game start scenarios and early tactical decisions",
        icon: "🎯",
        subcategories: openingPositions
    },
    // ... other categories
};
```

## Position Template Structure

### Required Fields

```javascript
{
    name: "Position Name",              // Display name
    description: "Brief description",   // What this position demonstrates
    difficulty: "beginner|intermediate|advanced|expert",
    tags: ["tag1", "tag2"],           // For filtering and search
    generate: () => gameStateObject    // Function that returns game state
}
```

### Game State Format

```javascript
{
    factories: [
        ['B', 'Y', 'R'],  // Factory 1 tiles
        ['K', 'W', 'B'],  // Factory 2 tiles
        // ... 5 factories total
    ],
    center: ['B', 'Y'],   // Center pool tiles
    players: [
        {
            pattern_lines: [['B'], [], ['R', 'R'], [], []],  // 5 pattern lines
            wall: [  // 5x5 wall grid
                ['B', null, null, null, null],
                [null, 'Y', null, null, null],
                // ... 5 rows
            ],
            floor_line: ['B', 'Y'],  // Floor line tiles
            score: 12                 // Current score
        }
        // ... 2 players for 2-player games
    ]
}
```

## Tagging System

### Standard Tags

**Categories:**
- `opening`, `midgame`, `endgame`, `educational`

**Difficulties:**
- `beginner`, `intermediate`, `advanced`, `expert`

**Player Count:**
- `2-player` (only supported currently)

**Themes:**
- `balanced`, `aggressive`, `color-focus`, `high-interaction`
- `scoring`, `blocking`, `optimization`, `counting`
- `multiplier`, `color-race`, `floor-line`, `final-round`
- `tie-breaker`, `conservation`, `pattern-lines`, `wall-strategy`

### Custom Tags

Add descriptive tags that help users find positions:
- `defensive-play`, `aggressive-play`
- `color-completion`, `row-completion`
- `negative-points`, `bonus-scoring`
- `tile-efficiency`, `timing-critical`

## Best Practices

### 1. Position Design

**Clear Learning Objectives**
- Each position should teach something specific
- Description should explain what to look for
- Difficulty should match the complexity

**Realistic Scenarios**
- Positions should represent actual game situations
- Avoid artificial or impossible setups
- Consider tile distribution rules

**Progressive Difficulty**
- Start with simple concepts
- Build complexity gradually
- Provide clear progression paths

### 2. Code Organization

**Modular Structure**
- Keep positions in separate files by category
- Use consistent naming conventions
- Group related positions together

**Reusable Components**
- Create helper functions for common patterns
- Use constants for repeated values
- Maintain consistent formatting

**Documentation**
- Comment complex position logic
- Explain strategic elements
- Document any special rules or assumptions

### 3. Testing Positions

**Validation**
- Ensure positions are valid game states
- Check tile counts and distributions
- Verify wall patterns are legal

**Functionality**
- Test that positions load correctly
- Verify tiles display properly
- Check that interactions work

**User Experience**
- Test search and filtering
- Verify tags work correctly
- Ensure descriptions are helpful

## Example: Creating a Mid-Game Position

```javascript
// In midgame-positions.js

const multiplierSetup = {
    name: "Multiplier Setup",
    description: "Positioning for row/column bonuses - focus on completing rows and columns for scoring multipliers",
    difficulty: "intermediate",
    tags: ["midgame", "scoring", "multiplier", "row-completion"],
    generate: () => ({
        factories: [
            ['B', 'Y'],
            ['Y', 'R'],
            ['R', 'K'],
            ['K', 'W'],
            ['W', 'B']
        ],
        center: ['B', 'Y'],
        players: Array(2).fill().map((_, playerIdx) => ({
            pattern_lines: [
                ['B', 'B'],      // Row 1: 2/1 capacity
                ['Y', 'Y', 'Y'], // Row 2: 3/2 capacity  
                [],               // Row 3: 0/3 capacity
                [],               // Row 4: 0/4 capacity
                []                // Row 5: 0/5 capacity
            ],
            wall: Array(5).fill().map((_, row) => 
                Array(5).fill().map((_, col) => 
                    row < 2 && col < 2 ? 'B' : null
                )
            ),
            floor_line: [],
            score: 12 + playerIdx * 3
        }))
    })
};
```

## Adding to the Library

### Quick Start

1. **Choose a category file** (e.g., `opening-positions.js`)
2. **Create your position template** following the structure above
3. **Add it to the appropriate subcategory**
4. **Test the position** by loading it in the UI
5. **Update this guide** if you add new patterns

### Advanced Features

**Dynamic Position Generation**
```javascript
// Generate positions based on parameters
const createColorFocusPosition = (color, intensity) => ({
    name: `${color} Focus (${intensity})`,
    description: `Concentrated ${color} tiles for aggressive play`,
    difficulty: intensity === 'high' ? 'advanced' : 'intermediate',
    tags: ['opening', 'color-focus', 'aggressive', '2-player'],
    generate: () => ({
        factories: Array(5).fill().map(() => Array(4).fill(color)),
        center: [],
        players: Array(2).fill().map(() => ({
            pattern_lines: [[], [], [], [], []],
            wall: Array(5).fill().map(() => Array(5).fill(null)),
            floor_line: [],
            score: 0
        }))
    })
});
```

**Position Collections**
```javascript
// Group related positions
const colorFocusPositions = {
    name: "Color Focus Variations",
    description: "Different color concentration strategies",
    positions: [
        createColorFocusPosition('B', 'medium'),
        createColorFocusPosition('B', 'high'),
        createColorFocusPosition('Y', 'medium'),
        // ... more variations
    ]
};
```

## Maintenance

### Regular Tasks

1. **Review and update tags** for better searchability
2. **Test positions** after code changes
3. **Add new categories** as needed
4. **Document new patterns** in this guide

### Quality Assurance

- **Validate positions** before adding to library
- **Test loading** in different scenarios
- **Check descriptions** for clarity and accuracy
- **Verify difficulty ratings** are appropriate

## Troubleshooting

### Common Issues

**Position doesn't load**
- Check game state format
- Verify factory arrays are correct
- Ensure player objects have all required fields

**Tiles don't display**
- Check tile color codes (B, Y, R, K, W)
- Verify array structure matches expectations
- Test with simpler position first

**Search/filtering issues**
- Check tag spelling and consistency
- Verify tags are in availableTags array
- Test search terms match position content

### Debugging Tips

1. **Console log** the generated game state
2. **Compare** with working positions
3. **Test incrementally** - start simple, add complexity
4. **Check browser console** for errors

## Future Enhancements

### Planned Features

- **Position ratings** and user feedback
- **Position collections** and themes
- **Dynamic difficulty adjustment**
- **Position sharing** and import/export
- **Analytics** on position usage

### Extension Points

- **Custom position creators**
- **Position validation tools**
- **Automated testing** for positions
- **Position recommendation** system

---

This guide should be updated as the position library evolves. For questions or contributions, refer to the main project documentation. 