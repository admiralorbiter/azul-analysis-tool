# Scoring Optimization Guide

> **Learn how to maximize your points through strategic tile placement and wall completion**

## 🎯 **Overview**

Scoring optimization helps you identify opportunities to maximize points through strategic tile placement, wall completion bonuses, and endgame scoring multipliers. This is essential for competitive Azul play.

## 🔍 **What Scoring Optimization Finds**

### **Wall Completion Opportunities**
- **Row completion** - 4 tiles in a row, 1 tile needed (+2 points)
- **Column completion** - 4 tiles in a column, 1 tile needed (+7 points)
- **Color set completion** - 4 tiles of same color, 1 tile needed (+10 points)

### **Pattern Line Optimization**
- **High-value pattern lines** - Lines close to completion (3/4, 4/5 tiles)
- **Overflow prevention** - Avoid taking tiles that would overflow to floor
- **Scoring potential** - 1, 3, 6, 10, 15 points for 1-5 tiles respectively

### **Floor Line Management**
- **Risk assessment** - Current floor tiles and potential penalties
- **Recovery opportunities** - Clear floor line with wall completion
- **Penalty avoidance** - Minimize negative points (-1, -1, -2, -2, -2, -3, -3)

### **Endgame Multipliers**
- **Multiplier setup** - Position tiles for multiple bonuses simultaneously
- **Tile counting** - Ensure sufficient tiles for planned bonuses
- **Timing optimization** - Set up bonuses for maximum impact

## 🎮 **Using Scoring Optimization**

### **In the Web UI**
1. **Load a position** or set up a game state
2. **Click "Scoring Optimization"** in the analysis panel
3. **Review opportunities** with urgency indicators
4. **Follow move suggestions** to maximize scoring

### **Via API**
```python
import requests

# Detect scoring optimization opportunities
response = requests.post('http://localhost:8000/api/v1/detect-scoring-optimization', json={
    "fen_string": "wall_completion_opportunity",
    "current_player": 0,
    "include_wall_completion": True,
    "include_pattern_line_optimization": True,
    "urgency_threshold": 0.6
})

optimization = response.json()
for opportunity in optimization['wall_completion_opportunities']:
    print(f"Complete {opportunity['type']} - Bonus: {opportunity['bonus_points']}")
```

## 📊 **Understanding Bonus Values**

### **Wall Completion Bonuses**
- **Row completion**: +2 points (moderate priority)
- **Column completion**: +7 points (high priority)
- **Color set completion**: +10 points (highest priority)

### **Pattern Line Scoring**
- **1 tile**: 1 point
- **2 tiles**: 3 points
- **3 tiles**: 6 points
- **4 tiles**: 10 points
- **5 tiles**: 15 points

### **Floor Line Penalties**
- **1st tile**: -1 point
- **2nd tile**: -1 point
- **3rd tile**: -2 points
- **4th tile**: -2 points
- **5th tile**: -2 points
- **6th tile**: -3 points
- **7th tile**: -3 points

## 🎯 **Strategic Tips**

### **Priority Order**
1. **Color set completion** (+10 points) - Highest value
2. **Column completion** (+7 points) - High value
3. **Row completion** (+2 points) - Moderate value
4. **Pattern line completion** (1-15 points) - Variable value
5. **Floor line avoidance** - Prevent penalties

### **Timing Considerations**
- **Early game**: Focus on pattern line building
- **Mid game**: Balance wall completion with pattern lines
- **Late game**: Prioritize wall completion bonuses
- **Endgame**: Set up multiplier combinations

### **Trade-off Analysis**
- **Wall vs. pattern line**: Wall completion usually worth more
- **Immediate vs. delayed**: Consider timing of bonuses
- **Risk vs. reward**: Balance scoring with floor line risk
- **Opponent disruption**: Consider blocking opportunities

## 🔧 **Configuration Options**

### **Detection Sensitivity**
- **High sensitivity** - Show all opportunities including minor ones
- **Medium sensitivity** - Show moderate and high-value opportunities
- **Low sensitivity** - Only show high-value opportunities

### **Analysis Depth**
- **Quick analysis** - Fast but may miss some opportunities
- **Deep analysis** - More thorough but slower
- **Real-time analysis** - Automatic updates as you play

## 📚 **Examples**

### **Example 1: Color Set Completion**
```
You have 3 red tiles on your wall
1 red tile available in factories
Opportunity: Complete red color set for +10 points
Priority: HIGH - Highest bonus in the game
```

### **Example 2: Column Completion**
```
You have 4 tiles in column 3
1 tile needed to complete the column
Opportunity: Complete column for +7 points
Priority: HIGH - Significant bonus
```

### **Example 3: Pattern Line Optimization**
```
Pattern line 4 has 3 tiles (6 points)
1 more tile would complete it (10 points)
Opportunity: Complete pattern line for +4 points
Priority: MEDIUM - Good value but not highest
```

### **Example 4: Floor Line Risk**
```
You have 2 tiles on floor line (-2 points)
Taking more tiles would add to penalty
Strategy: Avoid floor line, prioritize wall placement
Priority: HIGH - Prevent penalties
```

## 🚀 **Getting Started**

1. **Start with wall completion** - Look for row, column, and color set opportunities
2. **Optimize pattern lines** - Complete high-value lines when possible
3. **Manage floor line** - Avoid penalties and clear when possible
4. **Plan for endgame** - Set up multiplier combinations

## 📖 **Related Guides**

- **[Pattern Detection](pattern-detection.md)** - Identify blocking opportunities
- **[Floor Line Patterns](floor-line-patterns.md)** - Manage penalties strategically
- **[Position Editor](../competitive/position-editor.md)** - Set up positions for analysis

---

**Scoring optimization is crucial for competitive Azul play. Use it to maximize your points and improve your game!** 🎯 