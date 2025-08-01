# 🧠 Neural Training Interface Planning Document

## 📋 **Overview**

**Goal**: Create a comprehensive web-based neural training interface that provides full access to CLI neural training capabilities with real-time monitoring, progress tracking, and model management.

**Status**: 📋 **PLANNING** - Ready for implementation
**Timeline**: 3 weeks (5 parts)
**Priority**: High - Essential for advanced users

---

## 🎯 **CLI Capabilities to Implement**

### **Current CLI Commands**:
```bash
# Training
python main.py train --config small --device cpu --epochs 5 --samples 500

# Evaluation
python main.py evaluate --model models/azul_net_small.pth --positions 50 --games 20 --device cpu
```

### **Target Web UI Features**:
- ✅ Training configuration with visual controls
- ✅ Real-time training progress monitoring
- ✅ Model evaluation with results visualization
- ✅ Training history and model management
- ✅ Advanced features (hyperparameter tuning, etc.)

---

## 🚀 **Implementation Plan**

### **Part 2.1.1: Training Configuration Panel** 📋
**Priority**: High - Foundation for all training features
**Timeline**: 2-3 days

#### **Features**:
- **Model Configuration**: Dropdown for small/medium/large model sizes
- **Device Selection**: CPU/CUDA radio buttons with availability detection
- **Training Parameters**: Epochs (1-100), samples (100-10000), batch size (8-64)
- **Learning Settings**: Learning rate (0.0001-0.01), optimizer selection
- **Save Configuration**: Save/load training configurations
- **Validation**: Real-time parameter validation and range checking

#### **UI Components**:
```javascript
// TrainingConfigPanel Component
function TrainingConfigPanel({ 
    config, setConfig, startTraining, 
    loading, setLoading, setStatusMessage 
}) {
    // Model size selection
    const [modelSize, setModelSize] = React.useState('small');
    
    // Device selection with detection
    const [device, setDevice] = React.useState('cpu');
    const [availableDevices, setAvailableDevices] = React.useState(['cpu']);
    
    // Training parameters
    const [epochs, setEpochs] = React.useState(5);
    const [samples, setSamples] = React.useState(500);
    const [batchSize, setBatchSize] = React.useState(16);
    const [learningRate, setLearningRate] = React.useState(0.001);
    
    // Start training function
    const handleStartTraining = React.useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/v1/neural/train', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    modelSize, device, epochs, samples, 
                    batchSize, learningRate
                })
            });
            const data = await response.json();
            setStatusMessage('Training started successfully');
        } catch (error) {
            setStatusMessage(`Training failed: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [modelSize, device, epochs, samples, batchSize, learningRate]);
}
```

#### **API Integration**:
- `POST /api/v1/neural/train` - Start training with configuration
- `GET /api/v1/neural/config` - Get available configurations
- `POST /api/v1/neural/config` - Save training configuration

---

### **Part 2.1.2: Real-time Training Monitor** 📊
**Priority**: High - Essential for user experience
**Timeline**: 3-4 days

#### **Features**:
- **Live Progress**: Real-time epoch progress with percentage
- **Loss Visualization**: Live loss curve chart with epoch history
- **Training Metrics**: Current loss, learning rate, batch progress
- **Resource Monitoring**: GPU/CPU usage, memory consumption
- **Training Status**: Running/stopped/paused states with controls
- **Log Display**: Real-time training log with filtering

#### **UI Components**:
```javascript
// TrainingMonitor Component
function TrainingMonitor({ sessionId, loading, setLoading }) {
    const [trainingStatus, setTrainingStatus] = React.useState(null);
    const [progress, setProgress] = React.useState(null);
    const [lossHistory, setLossHistory] = React.useState([]);
    const [logs, setLogs] = React.useState([]);
    
    // Polling for real-time updates
    React.useEffect(() => {
        if (!sessionId) return;
        
        const interval = setInterval(async () => {
            try {
                const [statusRes, progressRes, logsRes] = await Promise.all([
                    fetch(`/api/v1/neural/status?session_id=${sessionId}`),
                    fetch(`/api/v1/neural/progress?session_id=${sessionId}`),
                    fetch(`/api/v1/neural/logs?session_id=${sessionId}`)
                ]);
                
                const status = await statusRes.json();
                const progressData = await progressRes.json();
                const logsData = await logsRes.json();
                
                setTrainingStatus(status);
                setProgress(progressData);
                setLossHistory(progressData.loss_history || []);
                setLogs(logsData.logs || []);
            } catch (error) {
                console.error('Failed to fetch training updates:', error);
            }
        }, 1000); // Poll every second
        
        return () => clearInterval(interval);
    }, [sessionId]);
    
    return (
        <div className="training-monitor">
            <TrainingStatus status={trainingStatus} />
            <ProgressBar progress={progress} />
            <LossChart lossHistory={lossHistory} />
            <ResourceMonitor status={trainingStatus} />
            <TrainingLog logs={logs} />
        </div>
    );
}
```

#### **API Integration**:
- `GET /api/v1/neural/status` - Get current training status
- `GET /api/v1/neural/progress` - Get training progress data
- `GET /api/v1/neural/logs` - Get training logs
- `POST /api/v1/neural/stop` - Stop training
- `POST /api/v1/neural/pause` - Pause/resume training

---

### **Part 2.1.3: Model Evaluation Interface** 🎯
**Priority**: Medium - Important for model validation
**Timeline**: 2-3 days

#### **Features**:
- **Model Selection**: Dropdown for available trained models
- **Evaluation Settings**: Number of positions/games, search time, rollouts
- **Evaluation Types**: Position accuracy, move agreement, self-play win rate
- **Results Display**: Comprehensive evaluation results with charts
- **Comparison Tools**: Compare multiple models side-by-side
- **Export Results**: Export evaluation data and charts

#### **UI Components**:
```javascript
// ModelEvaluator Component
function ModelEvaluator({ loading, setLoading, setStatusMessage }) {
    const [selectedModel, setSelectedModel] = React.useState('');
    const [availableModels, setAvailableModels] = React.useState([]);
    const [evaluationConfig, setEvaluationConfig] = React.useState({
        positions: 50,
        games: 20,
        searchTime: 0.5,
        rollouts: 50,
        device: 'cpu'
    });
    const [evaluationResults, setEvaluationResults] = React.useState(null);
    
    // Load available models
    React.useEffect(() => {
        fetch('/api/v1/neural/models')
            .then(res => res.json())
            .then(models => setAvailableModels(models))
            .catch(err => setStatusMessage(`Failed to load models: ${err.message}`));
    }, []);
    
    // Start evaluation
    const handleEvaluate = React.useCallback(async () => {
        if (!selectedModel) return;
        
        setLoading(true);
        try {
            const response = await fetch('/api/v1/neural/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: selectedModel,
                    ...evaluationConfig
                })
            });
            const results = await response.json();
            setEvaluationResults(results);
            setStatusMessage('Evaluation completed successfully');
        } catch (error) {
            setStatusMessage(`Evaluation failed: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [selectedModel, evaluationConfig]);
}
```

#### **API Integration**:
- `POST /api/v1/neural/evaluate` - Start model evaluation
- `GET /api/v1/neural/models` - List available models
- `GET /api/v1/neural/evaluation/{id}` - Get evaluation results
- `GET /api/v1/neural/evaluation/{id}/export` - Export results

---

### **Part 2.1.4: Training History & Management** 📚
**Priority**: Medium - Important for long-term use
**Timeline**: 2-3 days

#### **Features**:
- **Training History**: List of all training runs with metadata
- **Model Library**: Browse and manage trained models
- **Training Analytics**: Performance trends and model evolution
- **Model Metadata**: Training parameters, performance metrics, timestamps
- **Model Actions**: Delete, rename, duplicate models
- **Training Templates**: Save and reuse training configurations

#### **UI Components**:
```javascript
// TrainingHistory Component
function TrainingHistory({ loading, setLoading, setStatusMessage }) {
    const [trainingHistory, setTrainingHistory] = React.useState([]);
    const [modelLibrary, setModelLibrary] = React.useState([]);
    
    // Load training history and model library
    React.useEffect(() => {
        Promise.all([
            fetch('/api/v1/neural/history'),
            fetch('/api/v1/neural/models')
        ])
        .then(([historyRes, modelsRes]) => Promise.all([
            historyRes.json(),
            modelsRes.json()
        ]))
        .then(([history, models]) => {
            setTrainingHistory(history);
            setModelLibrary(models);
        })
        .catch(err => setStatusMessage(`Failed to load data: ${err.message}`));
    }, []);
    
    return (
        <div className="training-history">
            <TrainingHistoryList history={trainingHistory} />
            <ModelLibrary models={modelLibrary} />
            <TrainingAnalytics history={trainingHistory} />
        </div>
    );
}
```

#### **API Integration**:
- `GET /api/v1/neural/history` - Get training history
- `GET /api/v1/neural/models` - Get model library
- `DELETE /api/v1/neural/models/{id}` - Delete model
- `PUT /api/v1/neural/models/{id}` - Update model metadata

---

### **Part 2.1.5: Advanced Training Features** ⚙️
**Priority**: Low - Advanced features for power users
**Timeline**: 3-4 days

#### **Features**:
- **Hyperparameter Tuning**: Grid search and optimization
- **Data Generation**: Custom training data generation
- **Transfer Learning**: Load and fine-tune existing models
- **Training Scheduling**: Scheduled training runs
- **Distributed Training**: Multi-GPU training support
- **Custom Architectures**: Custom model architecture builder

#### **UI Components**:
```javascript
// AdvancedFeatures Component
function AdvancedFeatures({ loading, setLoading, setStatusMessage }) {
    const [hyperparameterConfig, setHyperparameterConfig] = React.useState({});
    const [dataGenerationConfig, setDataGenerationConfig] = React.useState({});
    const [transferLearningConfig, setTransferLearningConfig] = React.useState({});
    
    return (
        <div className="advanced-features">
            <HyperparameterTuner 
                config={hyperparameterConfig}
                setConfig={setHyperparameterConfig}
            />
            <DataGenerator 
                config={dataGenerationConfig}
                setConfig={setDataGenerationConfig}
            />
            <TransferLearning 
                config={transferLearningConfig}
                setConfig={setTransferLearningConfig}
            />
        </div>
    );
}
```

#### **API Integration**:
- `POST /api/v1/neural/hyperparameter-tune` - Start hyperparameter tuning
- `POST /api/v1/neural/generate-data` - Generate training data
- `POST /api/v1/neural/transfer-learn` - Start transfer learning
- `POST /api/v1/neural/schedule` - Schedule training runs

---

## 🗄️ **Database Schema Extensions**

### **Training Sessions Table**:
```sql
CREATE TABLE training_sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,
    config JSON,
    status TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    progress JSON,
    logs TEXT
);
```

### **Model Metadata Table**:
```sql
CREATE TABLE model_metadata (
    id INTEGER PRIMARY KEY,
    model_path TEXT,
    config JSON,
    performance JSON,
    created_at TIMESTAMP,
    training_session_id INTEGER
);
```

### **Evaluation Results Table**:
```sql
CREATE TABLE evaluation_results (
    id INTEGER PRIMARY KEY,
    model_id INTEGER,
    config JSON,
    results JSON,
    created_at TIMESTAMP
);
```

---

## 🧪 **Test Strategy**

### **Unit Tests**:
- `tests/test_neural_training_config.py` - Training configuration panel
- `tests/test_neural_training_monitor.py` - Real-time monitoring
- `tests/test_neural_evaluation.py` - Model evaluation interface
- `tests/test_neural_history.py` - Training history and management
- `tests/test_neural_advanced.py` - Advanced features

### **Integration Tests**:
- API endpoint testing for all neural training endpoints
- Real-time communication testing
- Database integration testing
- Error handling and edge cases

### **Performance Tests**:
- UI responsiveness during training
- Real-time update performance
- Memory usage during long training sessions

---

## 🎯 **Success Metrics**

### **Usability Goals**:
- [ ] **Training Setup**: Users can configure training in <2 minutes
- [ ] **Progress Monitoring**: Real-time updates with <1 second latency
- [ ] **Model Management**: Complete model lifecycle management
- [ ] **Evaluation**: Comprehensive model evaluation with visual results

### **Technical Goals**:
- [ ] **API Integration**: All CLI training features available via web UI
- [ ] **Real-time Updates**: WebSocket or polling for live progress
- [ ] **Error Handling**: Robust error handling and user feedback
- [ ] **Performance**: UI remains responsive during training

### **User Experience Goals**:
- [ ] **Intuitive Interface**: Clear visual hierarchy and workflow
- [ ] **Progress Feedback**: Clear indication of training progress
- [ ] **Result Visualization**: Charts and graphs for training metrics
- [ ] **Mobile Support**: Responsive design for tablet/mobile use

---

## 🚀 **Next Steps**

1. **Immediate**: Start Part 2.1.1 (Training Configuration Panel)
2. **Week 1**: Complete Parts 2.1.1 & 2.1.2
3. **Week 2**: Complete Parts 2.1.3 & 2.1.4
4. **Week 3**: Complete Part 2.1.5 and final testing

**Current Progress**: 0% of neural training interface complete (0/5 parts)
**Target**: 100% of neural training interface complete by end of Week 3

---

**Last Updated**: Latest
**Next Review**: After Part 2.1.1 completion
**Status**: 📋 Planning Complete → Ready for Implementation 