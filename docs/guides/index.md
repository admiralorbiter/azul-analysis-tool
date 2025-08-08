# 📚 Guides Index

> **Complete guide to using the Azul Solver & Analysis Toolkit**

## 🎯 **Getting Started**

### **[Quick Start](../QUICK_START.md)**
Essential setup and basic usage for all users.

### **[Quick Start for New Users](getting-started/quick-start-guide.md)**
Pointer: redirects to canonical Quick Start and API Quick Start.

### **[Installation](getting-started/installation.md)**
Detailed installation instructions and system requirements.

### **[First Steps](getting-started/first-steps.md)**
Your first analysis session and basic features.

### **[Basic Usage](getting-started/basic-usage.md)**
Core functionality and common use cases.

## 🔍 **Analysis Guides**

### **[Pattern Detection](analysis/pattern-detection.md)**
Pointer: canonical in `systems/move-quality/patterns.md`.

### **[Scoring Optimization](analysis/scoring-optimization.md)**
Pointer: canonical overview and technical implementation.

### **[Floor Line Patterns](analysis/floor-line-patterns.md)**
Pointer: canonical in `systems/move-quality/patterns.md`.

### **[Move Quality Assessment](analysis/move-quality.md)**
Pointer: canonical in `systems/move-quality/assessment.md`.

### **[Strategic Analysis](analysis/strategic-analysis.md)**
Pointer: canonical in `systems/competitive/analysis.md`.

## 🏆 **Competitive Features**

### **[Position Editor](competitive/position-editor.md)**
Pointer: canonical in `systems/position-library/editor.md`.

### **[Position Library](competitive/position-library.md)**
Pointer: canonical in `systems/position-library/README.md`.

### **[Advanced Analysis](competitive/advanced-analysis.md)**
Pointer: canonical in `systems/competitive/analysis.md`.

## 🧠 **Neural Features**

### **[Training](neural/training.md)**
Train neural models for improved analysis.

### **[Evaluation](neural/evaluation.md)**
Evaluate model performance and compare with heuristics.

### **[Integration](neural/integration.md)**
Integrate neural models with search algorithms.

## 📖 **Technical Documentation**

### **API Reference (technical/api/)**
Complete REST API documentation by category.

### **[Architecture](../technical/architecture.md)**
System architecture and component overview.

### **[Development Setup](../technical/development/setup.md)**
Setting up the development environment.

## 🎯 **Guide Selection by Use Case**

### **For New Users**
1. **[Quick Start for New Users](getting-started/quick-start-guide.md)** - 5-minute setup
2. **[Quick Start](../QUICK_START.md)** - Essential setup and usage
3. **[First Steps](getting-started/first-steps.md)** - Learn basic features
4. **[Pattern Detection](analysis/pattern-detection.md)** - Start with analysis

### **For Competitive Players**
1. **[Position Editor](competitive/position-editor.md)** - Set up positions
2. **[Pattern Detection](analysis/pattern-detection.md)** - Learn blocking
3. **[Scoring Optimization](analysis/scoring-optimization.md)** - Optimize scoring
4. **[Floor Line Patterns](analysis/floor-line-patterns.md)** - Manage penalties
5. **[Move Quality Assessment](analysis/move-quality.md)** - Evaluate moves

### **For Developers**
1. **API Reference (technical/api/)** - Understand the API
2. **[Architecture](../technical/architecture.md)** - Learn the system
3. **[Development Setup](../technical/development/setup.md)** - Set up development

### **For Researchers**
1. **[Neural Training](neural/training.md)** - Train AI models
2. **[Advanced Analysis](competitive/advanced-analysis.md)** - Use advanced tools
3. **[Strategic Analysis](analysis/strategic-analysis.md)** - Study strategy

## 📊 **Feature Overview**

| Feature | Status | Guide |
|---------|--------|-------|
| Pattern Detection | ✅ Complete | [Pattern Detection](analysis/pattern-detection.md) |
| Scoring Optimization | ✅ Complete | [Scoring Optimization](analysis/scoring-optimization.md) |
| Floor Line Patterns | ✅ Complete | [Floor Line Patterns](analysis/floor-line-patterns.md) |
| Move Quality Assessment | ✅ Complete | [Move Quality Assessment](analysis/move-quality.md) |
| Installation | ✅ Complete | [Installation](getting-started/installation.md) |
| Position Editor | ✅ Complete | [Position Editor](competitive/position-editor.md) |
| Position Library | ✅ Complete | [Position Library](competitive/position-library.md) |
| Neural Training | 🚧 80% Complete | [Neural Training](neural/training.md) |
| Strategic Analysis | 🚧 In Progress | [Strategic Analysis](analysis/strategic-analysis.md) |

## 🚀 **Quick Reference**

### **Common Tasks**
- **Set up a position**: [Position Editor](competitive/position-editor.md)
- **Find blocking moves**: [Pattern Detection](analysis/pattern-detection.md)
- **Optimize scoring**: [Scoring Optimization](analysis/scoring-optimization.md)
- **Manage penalties**: [Floor Line Patterns](analysis/floor-line-patterns.md)
- **Evaluate moves**: [Move Quality Assessment](analysis/move-quality.md)
- **Train AI models**: [Neural Training](neural/training.md)

### **API Usage**
- **Pattern detection**: `POST /api/v1/detect-patterns`
- **Scoring optimization**: `POST /api/v1/detect-scoring-optimization`
- **Floor line patterns**: `POST /api/v1/detect-floor-line-patterns`
- **Move quality assessment**: `POST /api/v1/analyze-move-quality`
- **Position validation**: `POST /api/v1/validate-position`

### **Performance Targets**
- **Analysis response**: < 200ms
- **Pattern detection**: < 100ms
- **Position validation**: < 50ms
- **Real-time updates**: Automatic

---

**Start with the [Quick Start](../QUICK_START.md) (canonical). For API integration, see [API Quick Start](../api/QUICK_START.md).** 🎯