# Pattern Detection Guide

> **Learn how to identify tactical opportunities and blocking moves in Azul**

## 🎯 **Overview**

Pattern detection helps you identify **tile blocking opportunities** - situations where you can prevent opponents from completing pattern lines by taking specific tiles. This is a crucial tactical skill in competitive Azul play.

## 🔍 **What Pattern Detection Finds**

### **Tile Blocking Opportunities**
- **Opponent pattern lines** that are close to completion
- **Available blocking tiles** in factories and center
- **Urgency levels** (HIGH/MEDIUM/LOW) for blocking importance
- **Specific move suggestions** with explanations

### **How It Works**
1. **Analyzes opponent boards** - Checks which tiles opponents have in pattern lines
2. **Identifies blocking tiles** - Finds tiles that would complete opponent lines
3. **Calculates urgency** - Determines how critical the blocking opportunity is
4. **Suggests moves** - Provides specific recommendations for blocking

## 🎮 **Using Pattern Detection**

### **In the Web UI**
1. **Load a position** or set up a game state
2. **Click "Pattern Analysis"** in the analysis panel
3. **Review blocking opportunities** with urgency indicators
4. **Follow move suggestions** to execute blocking moves

### **Via API**
```python
import requests

# Detect blocking opportunities
response = requests.post('http://localhost:5000/api/v1/detect-patterns', json={
    "fen_string": "high_urgency_red_blocking",
    "current_player": 0,
    "include_blocking_opportunities": True,
    "urgency_threshold": 0.6
})

patterns = response.json()
for opportunity in patterns['blocking_opportunities']:
    print(f"Block {opportunity['color']} - Urgency: {opportunity['urgency']}")
```

## 📊 **Understanding Urgency Levels**

### **HIGH Urgency** 🔴
- **Opponent is 1-2 tiles away** from completing a pattern line
- **Few blocking tiles available** (1-2 tiles in factories/center)
- **High scoring potential** for the opponent
- **Immediate action required** - take blocking tiles now

### **MEDIUM Urgency** 🟡
- **Opponent is 2-3 tiles away** from completion
- **Moderate blocking tiles available** (3-4 tiles)
- **Medium scoring potential** for opponent
- **Consider blocking** if it doesn't hurt your position

### **LOW Urgency** 🟢
- **Opponent is 3+ tiles away** from completion
- **Many blocking tiles available** (5+ tiles)
- **Low scoring potential** for opponent
- **Focus on your own position** instead

## 🎯 **Strategic Tips**

### **When to Block**
- **HIGH urgency** - Almost always block if possible
- **MEDIUM urgency** - Block if it doesn't hurt your scoring
- **LOW urgency** - Usually ignore, focus on your position

### **Blocking Considerations**
- **Don't block at the cost of your own scoring** - Balance is key
- **Consider tile colors** - Block colors that help your wall
- **Watch for multiple threats** - Some moves block multiple opponents
- **Plan ahead** - Blocking now may prevent bigger problems later

### **Advanced Strategies**
- **Fake blocking** - Take tiles that look like blocking but help you
- **Timing blocks** - Wait for the right moment to maximize impact
- **Multi-blocking** - Find moves that block multiple opponents
- **Scoring while blocking** - Combine blocking with your own scoring

## 🔧 **Configuration Options**

### **Urgency Threshold**
- **Higher threshold (0.8+)** - Only show critical blocking opportunities
- **Medium threshold (0.6)** - Show moderate and high urgency
- **Lower threshold (0.4)** - Show all blocking opportunities

### **Analysis Depth**
- **Quick analysis** - Fast but may miss some opportunities
- **Deep analysis** - More thorough but slower
- **Real-time analysis** - Automatic updates as you play

## 📚 **Examples**

### **Example 1: High Urgency Blocking**
```
Opponent has 3 red tiles in pattern line 4
Only 2 red tiles available in factories
Urgency: HIGH - Block immediately!
```

### **Example 2: Medium Urgency Blocking**
```
Opponent has 2 blue tiles in pattern line 3
4 blue tiles available in factories
Urgency: MEDIUM - Consider blocking if it helps you
```

### **Example 3: Low Urgency Blocking**
```
Opponent has 1 yellow tile in pattern line 2
6 yellow tiles available in factories
Urgency: LOW - Focus on your own position
```

## 🚀 **Getting Started**

1. **Start with simple positions** - Practice with clear blocking scenarios
2. **Use the urgency indicators** - Let the system guide your decisions
3. **Follow move suggestions** - Learn from the recommended moves
4. **Practice regularly** - Pattern detection improves with experience

## 📖 **Related Guides**

- **[Scoring Optimization](scoring-optimization.md)** - Find high-value scoring moves
- **[Floor Line Patterns](floor-line-patterns.md)** - Manage penalties strategically
- **[Position Editor](../competitive/position-editor.md)** - Set up positions for analysis

---

**Pattern detection is a powerful tool for competitive Azul play. Use it to identify tactical opportunities and improve your blocking skills!** 🎯 