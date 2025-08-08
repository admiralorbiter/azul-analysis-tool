# 🚀 Quick Start Guide

> **Get up and running with the Azul Solver & Analysis Toolkit in minutes**

## 📋 **Prerequisites**

- **Python 3.11+** installed
- **Git** for cloning the repository
- **Web browser** for the interactive UI

## 🛠️ **Installation**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/azul-analysis-tool.git
cd azul-analysis-tool
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Start the Server**
```bash
python start_server.py
```

The server will start on `http://localhost:8000`

## 🎮 **Basic Usage**

### **Interactive Play**
1. Open your browser to `http://localhost:8000`
2. You'll see the Azul game board
3. **Drag tiles** from factories to your pattern lines
4. **Click "Execute Move"** to make your move
5. **Use analysis tools** to get hints and insights

### **API Usage**
```python
import requests

# Get current game state
response = requests.get('http://localhost:8000/api/v1/game_state', params={'fen_string': 'initial'})
game_state = response.json()

# Execute a move
move_data = {
    "factory_index": 0,
    "color": "red",
    "pattern_line": 2
}
response = requests.post('http://localhost:8000/api/v1/execute_move', json=move_data)
```

## 🔍 **Analysis Features**

### **Pattern Detection**
- **Tile blocking opportunities** - Identify when to block opponents
- **Urgency scoring** - Know which moves are most critical
- **Move suggestions** - Get specific recommendations

### **Scoring Optimization**
- **Wall completion opportunities** - Find high-value scoring moves
- **Pattern line optimization** - Maximize your scoring potential
- **Floor line management** - Minimize penalties

### **Strategic Analysis**
- **Position evaluation** - Understand position strength
- **Move quality assessment** - Compare different move options
- **Endgame analysis** - Optimize final rounds

## 📚 **Next Steps**

- **Read the guides**: Check out the analysis guides for detailed explanations
- **Try the API**: Explore the REST API for programmatic access
- **Study positions**: Use the position library to practice specific scenarios
- **Train neural models**: Experiment with the neural training interface

## 🆘 **Troubleshooting**

### **Common Issues**

**Server won't start:**
- Check Python version: `python --version`
- Verify dependencies: `pip list | grep azul`
- Check port availability: `netstat -an | findstr :8000`

**API errors:**
- Ensure server is running
- Check request format matches API documentation
- Verify authentication if required

**UI issues:**
- Clear browser cache
- Try different browser
- Check browser console for errors

## 📖 **Documentation**

- **API Reference**: Complete endpoint documentation
- **Analysis Guides**: Detailed feature explanations
- **Competitive Features**: Advanced analysis tools
- **Neural Training**: AI model development

---

**Ready to start analyzing Azul positions?** 🎯

The toolkit provides everything you need to study, analyze, and improve your Azul gameplay! 