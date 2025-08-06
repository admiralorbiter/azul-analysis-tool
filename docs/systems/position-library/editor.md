# 🎯 Position Editor - User Guide

> **Complete guide to creating and editing custom positions for analysis**

## 📋 **Overview**

The Advanced Board State Editor allows you to create and modify any Azul position for analysis, training, or sharing. This powerful tool provides complete control over the game state with real-time validation and visual feedback.

## 🎯 **Getting Started**

### **Entering Edit Mode**
1. **Access the editor**: Click "Edit Mode" from the main interface
2. **Enable editing**: The board becomes interactive for modifications
3. **Visual indicators**: Green highlights show editable areas
4. **Validation feedback**: Real-time feedback on rule compliance

### **Understanding the Interface**
- **Factory tiles**: Click to add/remove tiles from factories
- **Center pool**: Modify tiles in the center area
- **Pattern lines**: Click to add/remove tiles from pattern lines
- **Wall**: Click to place/remove tiles on the wall
- **Floor line**: Click to add/remove penalty tiles
- **Score**: Directly edit player scores

## 🔧 **Editing Features**

### **Factory Management**
**How to edit factories**:
1. **Click on factory tiles** to add or remove tiles
2. **Color selection**: Choose from available tile colors
3. **Count validation**: System ensures proper tile counts
4. **Visual feedback**: Green for valid, amber for warnings

**Validation rules**:
- **Maximum 4 tiles per factory**
- **Color consistency**: All tiles in factory must be same color
- **Total tile conservation**: Track all 100 tiles across game

### **Center Pool Editing**
**How to edit center pool**:
1. **Click on center area** to add/remove tiles
2. **Color selection**: Choose tile colors for center
3. **First player marker**: Toggle first player indicator
4. **Conservation check**: Ensure total tiles remain 100

**Validation rules**:
- **First player marker**: Only one first player marker allowed
- **Tile conservation**: Total tiles across all areas must equal 100
- **Color availability**: Only use tiles that exist in the game

### **Pattern Line Editing**
**How to edit pattern lines**:
1. **Click on pattern line slots** to add/remove tiles
2. **Color constraints**: Only one color per pattern line
3. **Capacity limits**: Respect pattern line capacities (1,2,3,4,5)
4. **Visual feedback**: Green for valid, red for violations

**Validation rules**:
- **Single color**: Only one color allowed per pattern line
- **Capacity limits**: Pattern lines have fixed capacities
- **Wall compatibility**: Tiles must be compatible with wall patterns

### **Wall Editing**
**How to edit wall**:
1. **Click on wall positions** to place/remove tiles
2. **Pattern enforcement**: Wall follows fixed color patterns
3. **Row/column rules**: No duplicate colors in rows/columns
4. **Visual feedback**: Green for valid placements

**Validation rules**:
- **Fixed patterns**: Wall follows predetermined color patterns
- **No duplicates**: No same color in rows or columns
- **Pattern line connection**: Wall tiles must match pattern line colors

### **Floor Line Editing**
**How to edit floor line**:
1. **Click on floor line slots** to add/remove penalty tiles
2. **Capacity limit**: Maximum 7 tiles in floor line
3. **Penalty calculation**: Automatic penalty point calculation
4. **Visual feedback**: Red for penalties, green for empty

**Validation rules**:
- **Maximum 7 tiles**: Floor line cannot exceed 7 tiles
- **Penalty calculation**: -1, -2, -4, -7, -12, -20 points
- **Overflow handling**: Tiles overflow to floor when pattern lines are full

### **Score Editing**
**How to edit scores**:
1. **Click on score display** to modify points
2. **Direct input**: Type new score values
3. **Validation**: Ensure scores are reasonable for game state
4. **Consistency check**: Verify scores match board state

## ✅ **Validation System**

### **Real-Time Validation**
- **Immediate feedback**: Changes trigger instant validation
- **Visual indicators**: Color-coded feedback system
- **Error prevention**: Block invalid moves automatically
- **Suggestion system**: Provide corrections for violations

### **Validation Rules**

#### **Tile Conservation**
- **Total tiles**: Must equal exactly 100 across all areas
- **Color distribution**: Track tiles by color across game
- **Missing tiles**: Identify tiles that are unaccounted for
- **Excess tiles**: Detect when too many tiles are placed

#### **Pattern Line Rules**
- **Single color**: Only one color per pattern line
- **Capacity limits**: Respect 1,2,3,4,5 tile capacities
- **Wall compatibility**: Tiles must match wall patterns
- **Overflow handling**: Full pattern lines overflow to floor

#### **Wall Rules**
- **Fixed patterns**: Follow predetermined color patterns
- **No duplicates**: No same color in rows or columns
- **Pattern line connection**: Wall tiles match pattern line colors
- **Completion bonuses**: Track row/column/color completions

#### **Floor Line Rules**
- **Maximum capacity**: 7 tiles maximum
- **Penalty calculation**: Automatic penalty point calculation
- **Overflow source**: Tiles come from full pattern lines
- **First player marker**: Counts as floor line tile

### **Error Handling**
- **Amber warnings**: Non-critical issues that should be reviewed
- **Red errors**: Critical violations that prevent saving
- **Tooltip explanations**: Detailed descriptions of issues
- **Suggested fixes**: Automatic correction recommendations

## 📁 **Position Management**

### **Saving Positions**
1. **Click "Save Position"** to store current state
2. **Add metadata**: Name, description, tags, difficulty
3. **Choose category**: Opening, midgame, endgame, tactical
4. **Export format**: Save in standard position format

### **Loading Positions**
1. **Access position library** from main menu
2. **Browse categories** or search by tags
3. **Select position** to load into editor
4. **Verify state** matches expected position

### **Position Templates**
- **Opening positions**: Standard opening scenarios
- **Midgame positions**: Common midgame situations
- **Endgame positions**: Critical endgame scenarios
- **Tactical positions**: Specific tactical themes
- **Educational positions**: Learning-focused scenarios

### **Custom Position Creation**
1. **Start with empty board** or template
2. **Edit to desired state** using editor tools
3. **Validate position** for rule compliance
4. **Add metadata** for organization
5. **Save and share** with other players

## 🎯 **Advanced Features**

### **Position Validation**
- **Complete rule checking**: All Azul rules enforced
- **Consistency verification**: Ensure logical game state
- **Playability testing**: Verify position is reachable
- **Analysis preparation**: Optimize for analysis tools

### **Position Sharing**
- **Export format**: Standard position exchange format
- **Metadata inclusion**: Tags, descriptions, difficulty ratings
- **Bulk operations**: Import/export multiple positions
- **Version control**: Track position modifications

### **Template System**
- **Pre-built scenarios**: Common position types
- **Custom templates**: Create reusable position types
- **Category organization**: Organize by difficulty and theme
- **Quick access**: Rapid position creation

## 🔍 **Best Practices**

### **Creating Analysis Positions**
1. **Start with clear objective**: What are you analyzing?
2. **Use realistic scenarios**: Positions that could occur in play
3. **Include key elements**: Critical tiles, scores, timing
4. **Test playability**: Ensure position is reachable
5. **Add context**: Notes about the scenario

### **Educational Position Design**
1. **Focus on specific concepts**: One learning objective per position
2. **Clear difficulty progression**: Build from simple to complex
3. **Include common mistakes**: Positions that highlight errors
4. **Provide solutions**: Include expected analysis results
5. **Add explanations**: Context for learning

### **Competitive Position Creation**
1. **Study real games**: Base positions on actual play
2. **Include critical decisions**: Positions with multiple good options
3. **Test different approaches**: Positions that reward analysis
4. **Consider timing**: Include time pressure scenarios
5. **Validate with experts**: Get feedback from strong players

## 🚀 **Integration with Analysis Tools**

### **Pattern Detection Integration**
- **Automatic analysis**: Run pattern detection on edited positions
- **Real-time feedback**: See pattern detection results immediately
- **Validation connection**: Pattern detection validates position logic
- **Learning integration**: Use positions for pattern learning

### **Move Quality Assessment**
- **Quality analysis**: Evaluate moves in edited positions
- **Alternative comparison**: Compare different move options
- **Educational value**: Learn from position analysis
- **Training integration**: Use for move quality training

### **Game Analysis Connection**
- **Position sequences**: Create positions for game analysis
- **Critical moments**: Identify key decision points
- **Alternative scenarios**: Explore different game paths
- **Learning progression**: Build complete game scenarios

## 📊 **Troubleshooting**

### **Common Issues**

#### **Tile Conservation Errors**
- **Problem**: Total tiles doesn't equal 100
- **Solution**: Check all areas for missing or excess tiles
- **Prevention**: Use tile counter display

#### **Pattern Line Violations**
- **Problem**: Multiple colors in pattern line
- **Solution**: Ensure single color per pattern line
- **Prevention**: Use color validation

#### **Wall Pattern Errors**
- **Problem**: Wall doesn't follow fixed patterns
- **Solution**: Check wall pattern reference
- **Prevention**: Use wall pattern guide

#### **Floor Line Overflow**
- **Problem**: Too many tiles in floor line
- **Solution**: Reduce floor line tiles to maximum 7
- **Prevention**: Monitor floor line capacity

### **Validation Tips**
- **Check tile counts**: Ensure total equals 100
- **Verify color distribution**: Track tiles by color
- **Test playability**: Ensure position is reachable
- **Review rule compliance**: Check all Azul rules
- **Validate scores**: Ensure scores match board state

---

**Next Steps**:
- Explore [Position Library](position-library.md) for existing positions
- Study [Advanced Analysis](advanced-analysis.md) for analysis techniques
- Practice with [Pattern Detection](../analysis/pattern-detection.md) for position analysis
- Review [Move Quality Assessment](../analysis/move-quality.md) for move evaluation 