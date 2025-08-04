# 🔧 Basic Usage Guide

> **Detailed instructions for using the core features of the Azul analysis tools**

## 📋 **Overview**

This guide provides step-by-step instructions for using the main features of the Azul analysis tools. Whether you're analyzing positions, studying patterns, or practicing moves, this guide will help you navigate the interface effectively.

## 🎯 **Core Interface Navigation**

### **Main Layout**

#### **Top Control Bar**
- **Game Controls**: Start, pause, reset, and step through the game
- **Analysis Tools**: Access pattern detection, move quality assessment, and other analysis features
- **Position Library**: Browse and load saved positions
- **Settings**: Configure analysis preferences and display options

#### **Center Game Board**
- **Factory Display**: Shows available tiles in factories
- **Center Pool**: Displays tiles in the center area with first player marker
- **Player Board**: Your pattern lines, wall, and floor line
- **Score Display**: Current scores for all players

#### **Right Analysis Panel**
- **Pattern Results**: Detected tactical patterns and opportunities
- **Move Suggestions**: Recommended moves with explanations
- **Quality Assessment**: Move quality ratings and breakdowns
- **Alternative Moves**: Other good options to consider

### **Basic Controls**

#### **Mouse Interactions**
- **Click on tiles**: Select tiles from factories or center
- **Click on pattern lines**: Place tiles in pattern lines
- **Click on wall**: Place tiles on wall (when pattern lines are full)
- **Click on floor line**: Place tiles in floor line
- **Drag and drop**: Alternative method for tile placement

#### **Keyboard Shortcuts**
- **Spacebar**: Toggle game pause/play
- **R**: Reset game to initial position
- **A**: Run pattern analysis
- **Q**: Run move quality assessment
- **L**: Open position library
- **E**: Enter edit mode

## 🔍 **Pattern Detection Usage**

### **Running Pattern Analysis**

#### **Step 1: Prepare Position**
1. **Load a position** from the position library or set up a custom position
2. **Verify the position** is valid (no rule violations)
3. **Ensure it's your turn** to analyze

#### **Step 2: Run Analysis**
1. **Click "Analyze Patterns"** in the analysis tools menu
2. **Wait for processing** - analysis may take a few seconds
3. **Review results** in the analysis panel

#### **Step 3: Interpret Results**
1. **Check pattern types** detected (blocking, scoring, floor line, etc.)
2. **Review urgency levels** (CRITICAL, HIGH, MEDIUM, LOW)
3. **Read explanations** for each detected pattern
4. **Consider move suggestions** provided by the analysis

### **Understanding Pattern Results**

#### **Tile Blocking Patterns**
- **Opponent analysis**: Shows which opponents have tiles in pattern lines
- **Blocking opportunities**: Identifies when you can prevent opponent completion
- **Urgency scoring**: Prioritizes blocking opportunities by importance
- **Move suggestions**: Specific recommendations for blocking actions

**How to use**:
1. **Look for HIGH/CRITICAL urgency** blocking opportunities
2. **Check if blocking tiles** are available in factories/center
3. **Consider the cost** of blocking vs. other opportunities
4. **Execute blocking moves** when they provide good value

#### **Scoring Optimization Patterns**
- **Wall completion opportunities**: Row, column, and color set completions
- **Pattern line optimization**: High-value completion opportunities
- **Floor line risk assessment**: Penalty detection and recovery
- **Endgame multiplier setup**: Multiple bonus combinations

**How to use**:
1. **Prioritize CRITICAL opportunities** for immediate scoring
2. **Balance immediate vs. future scoring** based on game state
3. **Consider floor line risk** when taking scoring tiles
4. **Plan for endgame bonuses** when possible

#### **Floor Line Management**
- **Risk assessment**: Detects potential floor line penalties
- **Timing optimization**: Identifies optimal timing for tile collection
- **Recovery strategies**: Suggests ways to minimize penalty impact
- **Trade-off analysis**: Balancing scoring vs. penalty avoidance

**How to use**:
1. **Check risk levels** before taking tiles
2. **Consider timing** - when is the best time to take these tiles?
3. **Plan recovery** if penalties are unavoidable
4. **Balance risk vs. reward** with other opportunities

## 🎯 **Move Quality Assessment Usage**

### **Running Move Quality Analysis**

#### **Step 1: Set Up Position**
1. **Load or create a position** with multiple move options
2. **Ensure position is valid** and follows Azul rules
3. **Identify the player** to analyze (usually yourself)

#### **Step 2: Run Quality Assessment**
1. **Click "Analyze Move Quality"** in the analysis tools
2. **Wait for evaluation** - may take longer for complex positions
3. **Review quality tiers** (!!, !, =, ?!, ?) for all moves

#### **Step 3: Study Results**
1. **Check top recommendations** and their quality scores
2. **Read explanations** for why moves are rated as they are
3. **Compare alternatives** to understand trade-offs
4. **Consider situational factors** (score, timing, etc.)

### **Understanding Quality Tiers**

#### **!! (Brilliant Move) - 90-100 points**
- **Characteristics**: Multiple high-value objectives, minimal risk
- **When to play**: Critical positions, game-winning opportunities
- **Examples**: Completing wall while blocking opponent and setting up multiplier

#### **! (Excellent Move) - 75-89 points**
- **Characteristics**: Primary strategic objective achieved, good risk/reward
- **When to play**: Strong positions, clear strategic advantages
- **Examples**: Efficient wall completion with bonus, strong blocking moves

#### **= (Good/Solid Move) - 50-74 points**
- **Characteristics**: Reasonable, safe, doesn't harm position
- **When to play**: Neutral positions, maintenance moves
- **Examples**: Standard pattern line filling, safe tile collection

#### **?! (Dubious Move) - 25-49 points**
- **Characteristics**: Some benefit but significant downsides
- **When to avoid**: When better alternatives exist
- **Examples**: Unnecessary floor line penalties, missed blocking opportunities

#### **? (Poor Move) - 0-24 points**
- **Characteristics**: Clear mistakes with negative impact
- **When to avoid**: Almost always - look for alternatives
- **Examples**: Helping opponent complete patterns, severe penalties

## 📚 **Position Library Usage**

### **Browsing Positions**

#### **Accessing the Library**
1. **Click "Position Library"** in the top control bar
2. **Browse categories** (opening, midgame, endgame, educational)
3. **Use search/filter** to find specific positions
4. **Preview position details** before loading

#### **Loading Positions**
1. **Select a position** from the library
2. **Click "Load Position"** to apply to the game board
3. **Verify the position** matches the description
4. **Begin analysis** with the loaded position

#### **Organizing Your Study**
- **By difficulty**: Start with beginner positions, progress to advanced
- **By theme**: Focus on specific tactical concepts
- **By game phase**: Study opening, midgame, and endgame separately
- **By personal focus**: Target your weak areas

### **Using Educational Positions**

#### **Pattern Recognition Practice**
1. **Load educational positions** designed for specific patterns
2. **Run pattern detection** to see what should be found
3. **Study the explanations** for each detected pattern
4. **Practice identifying** similar patterns in other positions

#### **Move Quality Practice**
1. **Load positions** with clear quality differences
2. **Run move quality analysis** to see the ratings
3. **Study the reasoning** behind each quality rating
4. **Practice recognizing** quality factors in new positions

## 🎮 **Game Play and Analysis**

### **Playing Through Positions**

#### **Step-by-Step Analysis**
1. **Load a position** from the library
2. **Run comprehensive analysis** (patterns + quality)
3. **Study all opportunities** and their priorities
4. **Choose the best move** based on analysis
5. **Execute the move** and see how position changes
6. **Repeat analysis** for the new position

#### **Learning from Analysis**
- **Pattern connections**: See how moves relate to detected patterns
- **Strategic principles**: Understand underlying concepts
- **Common mistakes**: Learn what to avoid
- **Progressive complexity**: Build understanding systematically

### **Practice Techniques**

#### **Time Pressure Practice**
1. **Set time limits** for move selection (30 seconds, 1 minute, etc.)
2. **Run analysis quickly** and make decisions under pressure
3. **Compare your choices** with analysis results
4. **Practice decision speed** while maintaining quality

#### **Multiple Attempts**
1. **Try different approaches** to the same position
2. **Compare results** of different strategies
3. **Learn from variations** and their outcomes
4. **Develop flexibility** in decision-making

## 🔧 **Advanced Features**

### **Position Editor Usage**

#### **Creating Custom Positions**
1. **Click "Edit Mode"** to enter position editor
2. **Modify board state** by clicking on tiles and areas
3. **Check validation** for rule compliance
4. **Save position** with metadata for later use

#### **Editing Existing Positions**
1. **Load a position** from the library
2. **Enter edit mode** to modify the position
3. **Make changes** to test different scenarios
4. **Save variations** for comparative study

### **Analysis Configuration**

#### **Customizing Analysis**
1. **Access settings** in the top control bar
2. **Adjust analysis depth** (basic, standard, advanced)
3. **Configure display options** (show/hide different elements)
4. **Set personal preferences** for analysis focus

#### **Performance Optimization**
- **Use appropriate analysis depth** for your needs
- **Close unnecessary browser tabs** to improve performance
- **Restart the server** if analysis becomes slow
- **Check system resources** during complex analysis

## 📊 **Tracking Progress**

### **Learning Metrics**

#### **Pattern Recognition**
- **Speed**: How quickly you identify patterns
- **Accuracy**: How often you recognize patterns correctly
- **Comprehensiveness**: How many patterns you identify
- **Understanding**: How well you explain pattern reasoning

#### **Move Quality Assessment**
- **Consistency**: How often you make = or better moves
- **Brilliant moves**: How often you find !! opportunities
- **Error avoidance**: How rarely you make ? or ?! moves
- **Decision speed**: How quickly you make good decisions

### **Study Planning**

#### **Daily Practice Routine**
1. **15-30 minutes** of pattern recognition practice
2. **10-15 minutes** of move quality assessment
3. **5-10 minutes** of position analysis
4. **5 minutes** of progress review and planning

#### **Weekly Review**
1. **Track improvement** in key metrics
2. **Identify weak areas** for focused practice
3. **Plan next week's** study priorities
4. **Adjust difficulty** based on progress

## 🔧 **Troubleshooting**

### **Common Issues and Solutions**

#### **Analysis Not Working**
- **Problem**: Analysis returns no results or errors
- **Solution**: Check position validity, restart server if needed
- **Prevention**: Use validated positions, keep server updated

#### **Slow Performance**
- **Problem**: Analysis takes too long or interface is sluggish
- **Solution**: Close other applications, restart browser
- **Prevention**: Regular system maintenance, appropriate analysis depth

#### **Interface Confusion**
- **Problem**: Don't understand how to use specific features
- **Solution**: Read relevant guides, start with basic features
- **Prevention**: Systematic learning approach, regular practice

### **Getting Help**

#### **Documentation Resources**
- **Pattern Detection Guide**: Detailed pattern recognition instructions
- **Move Quality Assessment**: Comprehensive move evaluation guide
- **Position Library Guide**: How to use study positions effectively
- **Position Editor Guide**: Creating and editing custom positions

#### **Community Support**
- **User forums**: Ask questions and share experiences
- **Study groups**: Learn with other players
- **Feedback system**: Report issues and suggest improvements
- **Tutorial videos**: Visual learning resources

---

**Next Steps**:
- Practice with the [Pattern Detection Guide](../analysis/pattern-detection.md) for detailed pattern recognition
- Study the [Move Quality Assessment Guide](../analysis/move-quality.md) for comprehensive move evaluation
- Explore the [Position Library Guide](../competitive/position-library.md) for effective position study
- Review the [Position Editor Guide](../competitive/position-editor.md) for creating custom positions 