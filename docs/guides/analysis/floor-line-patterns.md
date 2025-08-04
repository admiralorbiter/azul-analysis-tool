# Floor Line Patterns Guide

> **Learn how to manage floor line penalties strategically and optimize your tile placement**

## 🎯 **Overview**

Floor line management is crucial in Azul - tiles that don't fit on your wall or pattern lines go to the floor line, causing penalties. This guide helps you identify strategic opportunities to minimize penalties and use the floor line effectively.

## 🔍 **What Floor Line Patterns Finds**

### **Risk Mitigation Opportunities**
- **Critical risk** - 6+ tiles on floor line (-3 points)
- **High risk** - 4-5 tiles on floor line (-2 points)
- **Medium risk** - 2-3 tiles on floor line (-1 to -2 points)
- **Low risk** - 1 tile on floor line (-1 point)

### **Timing Optimization**
- **Early game** - Strategic floor line usage for future opportunities
- **Mid game** - Balanced floor line management during scoring phases
- **Endgame** - Aggressive floor line clearing for final scoring

### **Trade-off Analysis**
- **Wall vs floor** - Evaluating wall completion value against floor penalties
- **Multiplier setup** - Accepting floor penalties for multiple bonus combinations
- **Blocking value** - Using floor line strategically to block opponents

### **Endgame Management**
- **Penalty minimization** - Reducing floor line penalties in final rounds
- **Efficiency optimization** - Clearing floor line for maximum point efficiency
- **Strategic placement** - Using floor line for optimal tile placement

## 🎮 **Using Floor Line Pattern Analysis**

### **In the Web UI**
1. **Load a position** or set up a game state
2. **Click "Floor Line Analysis"** in the analysis panel
3. **Review risk levels** and mitigation opportunities
4. **Follow move suggestions** to optimize floor line usage

### **Via API**
```python
import requests

# Detect floor line patterns
response = requests.post('http://localhost:5000/api/v1/detect-floor-line-patterns', json={
    "fen_string": "floor_line_risk_scenario",
    "current_player": 0,
    "include_risk_mitigation": True,
    "include_timing_optimization": True,
    "urgency_threshold": 0.6
})

patterns = response.json()
for opportunity in patterns['risk_mitigation_opportunities']:
    print(f"Risk: {opportunity['risk_assessment']} - Penalty: {opportunity['potential_penalty']}")
```

## 📊 **Understanding Risk Levels**

### **CRITICAL Risk** 🔴
- **6+ tiles on floor line** (-3 points)
- **Immediate action required** - clear floor line now
- **High priority** - significant point loss
- **Recovery needed** - find wall placement opportunities

### **HIGH Risk** 🟠
- **4-5 tiles on floor line** (-2 points)
- **Action recommended** - clear floor line soon
- **Medium priority** - moderate point loss
- **Opportunity assessment** - evaluate wall vs floor trade-offs

### **MEDIUM Risk** 🟡
- **2-3 tiles on floor line** (-1 to -2 points)
- **Consider clearing** - if good wall opportunities exist
- **Lower priority** - minor point loss
- **Strategic timing** - clear when beneficial

### **LOW Risk** 🟢
- **1 tile on floor line** (-1 point)
- **Usually acceptable** - minor penalty
- **Low priority** - focus on scoring opportunities
- **Monitor situation** - prevent escalation

## 🎯 **Strategic Tips**

### **When to Use Floor Line**
- **Acceptable penalties** - When wall completion bonuses exceed floor penalties
- **Multiplier setup** - Accepting penalties for multiple bonus combinations
- **Blocking moves** - Using floor line strategically to block opponents
- **Emergency situations** - When no better options are available

### **Floor Line Management**
- **Clear early** - Don't let penalties accumulate
- **Plan wall placements** - Use floor line to enable future wall completions
- **Consider timing** - Clear floor line when it maximizes point efficiency
- **Balance trade-offs** - Weigh floor penalties against scoring opportunities

### **Advanced Strategies**
- **Strategic overflow** - Intentionally use floor line for better positioning
- **Timing optimization** - Clear floor line at optimal moments
- **Multi-blocking** - Use floor line to block multiple opponents
- **Endgame efficiency** - Maximize point efficiency in final rounds

## 🔧 **Configuration Options**

### **Risk Threshold**
- **Higher threshold (0.8+)** - Only show critical and high risk scenarios
- **Medium threshold (0.6)** - Show moderate and high risk scenarios
- **Lower threshold (0.4)** - Show all floor line opportunities

### **Analysis Depth**
- **Quick analysis** - Fast but may miss some opportunities
- **Deep analysis** - More thorough but slower
- **Real-time analysis** - Automatic updates as you play

## 📚 **Examples**

### **Example 1: Critical Risk Mitigation**
```
You have 6 tiles on floor line (-3 points)
Wall placement opportunity available
Action: Clear floor line immediately
Priority: CRITICAL - Significant point loss
```

### **Example 2: Strategic Trade-off**
```
You have 2 tiles on floor line (-2 points)
Wall completion opportunity worth +7 points
Trade-off: Accept floor penalty for wall bonus
Result: Net +5 points gain
```

### **Example 3: Timing Optimization**
```
You have 3 tiles on floor line (-2 points)
Endgame approaching, multiple bonuses possible
Strategy: Clear floor line now for endgame efficiency
Priority: HIGH - Optimize for final scoring
```

### **Example 4: Multiplier Setup**
```
You have 1 tile on floor line (-1 point)
Multiple wall completion opportunities available
Strategy: Accept floor penalty to set up multipliers
Result: Higher endgame scoring potential
```

## 🚀 **Getting Started**

1. **Monitor floor line** - Keep track of current penalties
2. **Assess risk levels** - Use the urgency indicators to guide decisions
3. **Plan wall placements** - Look for opportunities to clear floor line
4. **Consider trade-offs** - Balance floor penalties against scoring opportunities

## 📖 **Related Guides**

- **[Pattern Detection](pattern-detection.md)** - Identify blocking opportunities
- **[Scoring Optimization](scoring-optimization.md)** - Find high-value scoring moves
- **[Position Editor](../competitive/position-editor.md)** - Set up positions for analysis

---

**Floor line management is a key skill in competitive Azul. Use pattern analysis to minimize penalties and optimize your tile placement!** 🎯 